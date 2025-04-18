"""
Shopee Price Tracker

This file is an intermediary between the workflow configuration and the Flask app.
It simply imports the app object from app.py to make gunicorn work properly.
"""

import os

# Initialize app and databases before importing
from app import app  # This is what gunicorn looks for

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)