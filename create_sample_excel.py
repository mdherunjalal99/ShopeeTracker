"""
Create a sample Excel file for Shopee Price Tracker

This script creates a sample Excel file with a proper format for
the Shopee Price Tracker application.
"""

import pandas as pd
from datetime import datetime, timedelta

# Create DataFrame with column headers
today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
day_before = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

# Create an empty DataFrame
df = pd.DataFrame(columns=[
    "Link", 
    "Phân loại 1", 
    "Phân loại 2", 
    "% Giảm giá", 
    today, 
    yesterday, 
    day_before
])

# Add the configuration row at the top
config_row = pd.DataFrame([["link_column=A;var1_column=B;var2_column=C;discount_column=D"] + [""] * 6], 
                          columns=df.columns)

# Sample product data
products = [
    [
        "https://shopee.vn/iPhone-14-Pro-Max-128GB-Ch%C3%ADnh-h%C3%A3ng-VN-A-i.88201679.18932132659",
        "Đen", 
        "128GB",
        "",  # Discount column (will be calculated by the app)
        "",  # Today's price (will be filled by the app)
        "27500000",  # Yesterday's price
        "27600000",  # Price from 2 days ago
    ],
    [
        "https://shopee.vn/Apple-MacBook-Air-13-M2-2022-8GB-RAM-256GB-SSD-i.88201679.10882029466",
        "Xám",
        "256GB",
        "",
        "",
        "21500000",
        "21600000",
    ],
    [
        "https://shopee.vn/Tai-nghe-Apple-AirPods-Pro-2-2022-i.88201679.11893691238",
        "",
        "",
        "",
        "",
        "5590000",
        "5600000",
    ],
    [
        "https://shopee.vn/Apple-iPad-Gen-10-10.9-inch-Wi-Fi-64GB-Ch%C3%ADnh-h%C3%A3ng-VN-A-i.88201679.19848766397",
        "Bạc",
        "64GB",
        "",
        "",
        "9200000",
        "9300000",
    ],
    [
        "https://shopee.vn/Apple-Watch-Series-9-GPS-41mm-vi%E1%BB%81n-nh%C3%B4m-%C4%91%E1%BB%8Fa-cao-su-ch%C3%ADnh-h%C3%A3ng-VN-A-i.88201679.21366382963",
        "Đen",
        "41mm",
        "",
        "",
        "10500000",
        "10600000",
    ],
]

# Add product data
for row_idx, product in enumerate(products, start=3):
    for col_idx, value in enumerate(product, start=1):
        ws.cell(row=row_idx, column=col_idx, value=value)

# Write to Excel
filename = "shopee_sample.xlsx"
wb.save(filename)

print(f"Sample Excel file created at: {filename}")
print("This file can be used with the Shopee Price Tracker application.")
print("It includes sample product links from Shopee and configuration in the first row.")