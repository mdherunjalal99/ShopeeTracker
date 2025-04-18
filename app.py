"""
Shopee Price Tracker Web Interface

This module provides a web interface for the Shopee price tracker,
allowing users to upload Excel files, track prices, and view results.
"""

import os
import logging
import tempfile
from datetime import datetime
from threading import Thread
from pathlib import Path

try:
    from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
    from werkzeug.utils import secure_filename
except ImportError:
    import sys
    print("Flask and Werkzeug are required. Install them using 'pip install flask werkzeug'")
    sys.exit(1)

from excel_handler import ExcelHandler
from config import load_config_from_excel
from shopee_scraper import ShopeeScraperPool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "shopee_tracker_secret_key")

# Configure upload folder
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / "shopee_tracker_uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Store background job status
jobs = {}


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_excel_file(file_path, threads=4):
    """
    Process the Excel file in the background.
    
    Args:
        file_path: Path to the Excel file
        threads: Number of threads for scraping
    """
    job_id = os.path.basename(file_path)
    jobs[job_id] = {
        'status': 'running',
        'progress': 0,
        'total': 0,
        'results': [],
        'error': None,
        'output_file': file_path
    }
    
    try:
        # Load the Excel file
        excel_handler = ExcelHandler(file_path)
        logger.info(f"Successfully loaded Excel file: {file_path}")
        
        # Load configuration from Excel
        config = load_config_from_excel(excel_handler)
        logger.info("Successfully loaded configuration from Excel")
        logger.debug(f"Configuration: {config}")
        
        # Get Shopee product links and variations
        products = excel_handler.get_product_links_and_variations(
            config.link_column,
            config.var1_column,
            config.var2_column
        )
        logger.info(f"Found {len(products)} products to track")
        
        if not products:
            raise ValueError("No products found in the Excel file")
        
        # Update job status
        jobs[job_id]['total'] = len(products)
        
        # Current date for the column header
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Initialize the scraper pool
        scraper_pool = ShopeeScraperPool(threads)
        
        # Scrape prices
        logger.info(f"Starting price scraping with {threads} threads")
        
        results = []
        for i, (index, product) in enumerate(products.items()):
            link = product['link']
            var1 = product['var1']
            var2 = product['var2']
            
            try:
                price = scraper_pool.get_price(link, var1, var2)
                results.append((index, price))
                
                # Update job progress
                jobs[job_id]['progress'] = i + 1
                jobs[job_id]['results'].append({
                    'link': link,
                    'var1': var1 or 'N/A',
                    'var2': var2 or 'N/A',
                    'price': price
                })
            except Exception as e:
                logger.error(f"Failed to scrape price for {link}: {e}")
                results.append((index, None))
                jobs[job_id]['progress'] = i + 1
        
        # Update Excel with prices and calculate discounts
        # Write prices
        excel_handler.write_prices(results, today)
        logger.info(f"Successfully wrote prices to column: {today}")
        
        # Calculate discounts
        excel_handler.calculate_discounts(config.discount_column)
        logger.info(f"Successfully calculated discounts in column: {config.discount_column}")
        
        # Save the Excel file
        excel_handler.save()
        logger.info("Successfully saved the Excel file")
        
        # Update job status
        jobs[job_id]['status'] = 'completed'
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)


@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('Only Excel files (.xlsx, .xls) are allowed', 'error')
        return redirect(url_for('index'))
    
    threads = int(request.form.get('threads', 4))
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save the file
    file.save(file_path)
    
    # Start processing in background
    thread = Thread(target=process_excel_file, args=(file_path, threads))
    thread.daemon = True
    thread.start()
    
    # Store job ID in session
    session['job_id'] = os.path.basename(file_path)
    
    return redirect(url_for('status'))


@app.route('/status')
def status():
    """Show job status."""
    job_id = session.get('job_id')
    
    if not job_id or job_id not in jobs:
        flash('No active job found', 'error')
        return redirect(url_for('index'))
    
    job = jobs[job_id]
    
    if job['status'] == 'completed':
        flash('Processing completed successfully!', 'success')
    elif job['status'] == 'error':
        flash(f'Error: {job["error"]}', 'error')
    
    return render_template('status.html', job=job)


@app.route('/download/<job_id>')
def download_file(job_id):
    """Download processed Excel file."""
    if job_id not in jobs:
        flash('File not found', 'error')
        return redirect(url_for('index'))
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        flash('Processing not completed yet', 'error')
        return redirect(url_for('status'))
    
    return send_file(job['output_file'], as_attachment=True, download_name=os.path.basename(job['output_file']))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)