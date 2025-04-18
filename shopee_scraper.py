"""
Shopee Scraper Module

This module handles the scraping of product prices from Shopee.
It includes both regular HTTP request-based scraping and Selenium fallback.
"""

import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Constants
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}
SHOPEE_API_BASE = "https://shopee.vn/api/v4/item/get"


class ShopeeScraper:
    """Class for scraping Shopee product prices."""
    
    def __init__(self):
        """Initialize the scraper with session and required fields."""
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def extract_product_info(self, url: str) -> Tuple[str, str]:
        """
        Extract shop_id and item_id from Shopee product URL.
        
        Args:
            url: The Shopee product URL
            
        Returns:
            Tuple containing shop_id and item_id
        """
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Check if it's a Shopee URL
        if "shopee.vn" not in parsed_url.netloc:
            raise ValueError("Not a valid Shopee URL")
        
        # Extract shop_id and item_id from URL path
        path_parts = parsed_url.path.strip('/').split('-')
        
        # The last part contains the IDs in format i.X.Y where X is shop_id and Y is item_id
        if len(path_parts) < 1:
            raise ValueError("Invalid Shopee URL format")
        
        id_part = path_parts[-1]
        id_match = re.search(r'i\.(\d+)\.(\d+)', id_part)
        
        if id_match:
            shop_id = id_match.group(1)
            item_id = id_match.group(2)
            return shop_id, item_id
        
        # If we couldn't extract from the path, try query parameters
        query_params = parse_qs(parsed_url.query)
        if 'shopid' in query_params and 'itemid' in query_params:
            shop_id = query_params['shopid'][0]
            item_id = query_params['itemid'][0]
            return shop_id, item_id
        
        raise ValueError("Could not extract shop_id and item_id from URL")
    
    def get_product_data(self, shop_id: str, item_id: str) -> Dict:
        """
        Get product data from Shopee API.
        
        Args:
            shop_id: The shop ID
            item_id: The item ID
            
        Returns:
            Dict containing product data
        """
        url = f"{SHOPEE_API_BASE}?itemid={item_id}&shopid={shop_id}"
        
        # Add additional parameters required by the API
        params = {
            "shop_id": shop_id,
            "item_id": item_id,
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("error") is not None:
            raise ValueError(f"API returned error: {data['error']}")
        
        return data.get("data", {})
    
    def find_variation_option_index(self, data: Dict, variation_name: str, option_value: str) -> int:
        """
        Find the index of a variation option.
        
        Args:
            data: The product data
            variation_name: The name of the variation
            option_value: The option value to find
            
        Returns:
            Index of the option, or -1 if not found
        """
        if not variation_name or not option_value:
            return -1
        
        # Convert to lowercase for case-insensitive comparison
        variation_name = variation_name.lower().strip()
        option_value = option_value.lower().strip()
        
        tier_variations = data.get("tier_variations", [])
        
        for i, variation in enumerate(tier_variations):
            var_name = variation.get("name", "").lower().strip()
            
            # Check if this is the variation we're looking for
            if var_name == variation_name or var_name in variation_name or variation_name in var_name:
                options = variation.get("options", [])
                
                for j, option in enumerate(options):
                    opt_val = option.lower().strip()
                    if opt_val == option_value or opt_val in option_value or option_value in opt_val:
                        return j
        
        return -1
    
    def get_model_index(self, data: Dict, var1_value: Optional[str], var2_value: Optional[str]) -> int:
        """
        Find the model index for the specified variations.
        
        Args:
            data: The product data
            var1_value: The first variation value
            var2_value: The second variation value
            
        Returns:
            Index of the model, or 0 if not found
        """
        if not var1_value and not var2_value:
            return 0  # No variations specified, use default model
        
        tier_variations = data.get("tier_variations", [])
        if not tier_variations:
            return 0
        
        # Get the variation indexes
        var1_idx = -1
        var2_idx = -1
        
        if var1_value and len(tier_variations) > 0:
            var1_name = tier_variations[0].get("name", "")
            var1_idx = self.find_variation_option_index(data, var1_name, var1_value)
        
        if var2_value and len(tier_variations) > 1:
            var2_name = tier_variations[1].get("name", "")
            var2_idx = self.find_variation_option_index(data, var2_name, var2_value)
        
        # Find the matching model
        models = data.get("models", [])
        for i, model in enumerate(models):
            # For single variation
            if var1_idx >= 0 and var2_idx < 0:
                if model.get("extinfo", {}).get("tier_index", [0])[0] == var1_idx:
                    return i
            # For double variation
            elif var1_idx >= 0 and var2_idx >= 0:
                tier_index = model.get("extinfo", {}).get("tier_index", [0, 0])
                if len(tier_index) >= 2 and tier_index[0] == var1_idx and tier_index[1] == var2_idx:
                    return i
        
        # If no matching model found, return the first one
        return 0
    
    def get_price(self, url: str, var1: Optional[str] = None, var2: Optional[str] = None) -> float:
        """
        Get the price of a product from Shopee.
        
        Args:
            url: The Shopee product URL
            var1: First variation option (optional)
            var2: Second variation option (optional)
            
        Returns:
            Price of the product as a float
        """
        try:
            # Extract shop_id and item_id from URL
            shop_id, item_id = self.extract_product_info(url)
            
            # Get product data
            data = self.get_product_data(shop_id, item_id)
            
            # Find the model with matching variations
            model_idx = self.get_model_index(data, var1, var2)
            
            # Get the price from the model
            models = data.get("models", [])
            if not models:
                raise ValueError("No models found in product data")
            
            model = models[model_idx]
            
            # Price is stored in cents, convert to actual price
            price = model.get("price", 0) / 100000
            
            return price
        except Exception as e:
            logger.error(f"Error scraping price from {url}: {e}")
            raise


class ShopeeScraperPool:
    """Thread pool for scraping multiple products concurrently."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the scraper pool.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def get_price(self, url: str, var1: Optional[str] = None, var2: Optional[str] = None) -> float:
        """
        Get the price of a product from Shopee using the thread pool.
        
        Args:
            url: The Shopee product URL
            var1: First variation option (optional)
            var2: Second variation option (optional)
            
        Returns:
            Price of the product as a float
        """
        scraper = ShopeeScraper()
        future = self.executor.submit(scraper.get_price, url, var1, var2)
        return future.result()
    
    def shutdown(self):
        """Shutdown the thread pool."""
        self.executor.shutdown(wait=True)
