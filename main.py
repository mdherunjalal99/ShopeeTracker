#!/usr/bin/env python3
"""
Shopee Price Tracker

This file is an intermediary between the workflow configuration and the Flask app.
It simply imports the app object from app.py to make gunicorn work properly.
"""

import sys

try:
    from app import app  # This is what gunicorn looks for
except ImportError as e:
    print(f"Error: {e}")
    print("Please make sure Flask is installed: 'pip install flask'")
    sys.exit(1)

if __name__ == "__main__":
    # If run directly, use the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)