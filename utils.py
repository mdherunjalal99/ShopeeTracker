"""
Utility Module

This module provides utility functions for the Shopee price tracker.
"""

import logging
import re
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


def extract_shopee_ids(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract shop_id and item_id from a Shopee product URL.
    
    Args:
        url: The Shopee product URL
        
    Returns:
        Tuple of (shop_id, item_id)
    """
    if not url or not isinstance(url, str):
        return None, None
    
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Check if it's a Shopee URL
        if "shopee.vn" not in parsed_url.netloc:
            logger.warning(f"Not a Shopee URL: {url}")
            return None, None
        
        # Extract from URL path
        path_parts = parsed_url.path.strip('/').split('-')
        
        # Last part might contain the IDs in format i.X.Y
        if len(path_parts) >= 1:
            id_part = path_parts[-1]
            id_match = re.search(r'i\.(\d+)\.(\d+)', id_part)
            
            if id_match:
                shop_id = id_match.group(1)
                item_id = id_match.group(2)
                return shop_id, item_id
        
        # Try query parameters
        query_params = parse_qs(parsed_url.query)
        if 'shopid' in query_params and 'itemid' in query_params:
            shop_id = query_params['shopid'][0]
            item_id = query_params['itemid'][0]
            return shop_id, item_id
        
        logger.warning(f"Could not extract shop_id and item_id from URL: {url}")
        return None, None
    
    except Exception as e:
        logger.error(f"Error extracting IDs from URL {url}: {e}")
        return None, None


def format_price(price: float) -> str:
    """
    Format price with thousands separators.
    
    Args:
        price: The price value
        
    Returns:
        Formatted price string
    """
    return f"{price:,.0f}"


def calculate_discount_percent(current_price: float, avg_price: float) -> float:
    """
    Calculate discount percentage compared to average price.
    
    Formula: (1 - (current_price / avg_price)) * 100
    
    Args:
        current_price: The current price
        avg_price: The average price
        
    Returns:
        Discount percentage
    """
    if avg_price <= 0 or current_price <= 0:
        return 0
    
    return (1 - (current_price / avg_price)) * 100
