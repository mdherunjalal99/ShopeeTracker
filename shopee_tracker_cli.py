#!/usr/bin/env python3
"""
Shopee Price Tracker

This tool tracks Shopee product prices, records them in an Excel file,
and calculates discount percentages compared to the average price.
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime

from tqdm import tqdm

from config import load_config_from_excel, Config
from excel_handler import ExcelHandler
from shopee_scraper import ShopeeScraperPool
# No need to import app from app.py here anymore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Shopee Price Tracker')
    parser.add_argument(
        '-f', '--file',
        required=True,
        help='Path to the Excel file containing Shopee product links'
    )
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=4,
        help='Number of threads for scraping (default: 4)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    return parser.parse_args()


def main():
    """Main entry point of the application."""
    args = parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        sys.exit(1)
    
    # Load the Excel file
    try:
        excel_handler = ExcelHandler(args.file)
        logger.info(f"Successfully loaded Excel file: {args.file}")
    except Exception as e:
        logger.error(f"Failed to load Excel file: {e}")
        sys.exit(1)
    
    # Load configuration from Excel
    try:
        config = load_config_from_excel(excel_handler)
        logger.info("Successfully loaded configuration from Excel")
        logger.debug(f"Configuration: {config}")
    except Exception as e:
        logger.error(f"Failed to load configuration from Excel: {e}")
        sys.exit(1)
    
    # Get Shopee product links and variations
    try:
        products = excel_handler.get_product_links_and_variations(
            config.link_column,
            config.var1_column,
            config.var2_column
        )
        logger.info(f"Found {len(products)} products to track")
    except Exception as e:
        logger.error(f"Failed to get product links: {e}")
        sys.exit(1)
    
    if not products:
        logger.error("No products found in the Excel file")
        sys.exit(1)

    # Current date for the column header
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Initialize the scraper pool
    scraper_pool = ShopeeScraperPool(args.threads)
    
    # Scrape prices
    logger.info(f"Starting price scraping with {args.threads} threads")
    start_time = time.time()
    
    results = []
    with tqdm(total=len(products), desc="Scraping prices", unit="product") as pbar:
        for i, (index, product) in enumerate(products.items()):
            link = product['link']
            var1 = product['var1']
            var2 = product['var2']
            
            try:
                price = scraper_pool.get_price(link, var1, var2)
                results.append((index, price))
                pbar.update(1)
            except Exception as e:
                logger.error(f"Failed to scrape price for {link}: {e}")
                results.append((index, None))
                pbar.update(1)
    
    elapsed_time = time.time() - start_time
    logger.info(f"Scraping completed in {elapsed_time:.2f} seconds")
    
    # Update Excel with prices and calculate discounts
    try:
        # Write prices
        excel_handler.write_prices(results, today)
        logger.info(f"Successfully wrote prices to column: {today}")
        
        # Calculate discounts
        excel_handler.calculate_discounts(config.discount_column)
        logger.info(f"Successfully calculated discounts in column: {config.discount_column}")
        
        # Save the Excel file
        excel_handler.save()
        logger.info("Successfully saved the Excel file")
    except Exception as e:
        logger.error(f"Failed to update Excel file: {e}")
        sys.exit(1)
    
    logger.info("Price tracking completed successfully")


if __name__ == "__main__":
    main()
