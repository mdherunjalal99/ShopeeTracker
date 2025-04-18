"""
Create a sample Excel file for Shopee Price Tracker

This script creates a sample Excel file with a proper format for
the Shopee Price Tracker application.
"""

import pandas as pd
from datetime import datetime, timedelta
import os

# Create DataFrame with column headers
today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
day_before = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

# Sample product data - đây là dữ liệu mẫu, khi sử dụng thực tế, hãy thay thế bằng các URL sản phẩm thực trên Shopee
products = [
    [
        "https://shopee.vn/iPhone-14-Pro-Max-128GB-Ch%C3%ADnh-h%C3%A3ng-VN-A-i.88201679.18932132659",
        "Đen", 
        "128GB",
        "",  # Discount column (will be calculated by the app)
        "",  # Today's price (will be filled by the app)
        27500000,  # Yesterday's price
        27600000,  # Price from 2 days ago
    ],
    [
        "https://shopee.vn/Apple-MacBook-Air-13-M2-2022-8GB-RAM-256GB-SSD-i.88201679.10882029466",
        "Xám",
        "256GB",
        "",
        "",
        21500000,
        21600000,
    ],
    [
        "https://shopee.vn/Tai-nghe-Apple-AirPods-Pro-2-2022-i.88201679.11893691238",
        "",
        "",
        "",
        "",
        5590000,
        5600000,
    ],
    [
        "https://shopee.vn/Apple-iPad-Gen-10-10.9-inch-Wi-Fi-64GB-Ch%C3%ADnh-h%C3%A3ng-VN-A-i.88201679.19848766397",
        "Bạc",
        "64GB",
        "",
        "",
        9200000,
        9300000,
    ],
    [
        "https://shopee.vn/Apple-Watch-Series-9-GPS-41mm-vi%E1%BB%81n-nh%C3%B4m-%C4%91%E1%BB%8Fa-cao-su-ch%C3%ADnh-h%C3%A3ng-VN-A-i.88201679.21366382963",
        "Đen",
        "41mm",
        "",
        "",
        10500000,
        10600000,
    ],
    # Thêm các sản phẩm điện thoại
    [
        "https://shopee.vn/Samsung-Galaxy-S24-Ultra-12GB-256GB-i.88201679.23626487486",
        "Đen",
        "256GB",
        "",
        "",
        28990000,
        29500000,
    ],
    [
        "https://shopee.vn/Google-Pixel-8-Pro-128GB-Ch%C3%ADnh-H%C3%A3ng-i.88201679.23548769421",
        "Xanh",
        "128GB",
        "",
        "",
        21490000,
        21990000,
    ],
    # Thêm các sản phẩm laptop
    [
        "https://shopee.vn/Laptop-Dell-XPS-13-Plus-9320-i7-1260P-16GB-512GB-Windows-11-i.88201679.21845126497",
        "",
        "512GB",
        "",
        "",
        38990000,
        39900000,
    ],
    [
        "https://shopee.vn/Laptop-Gaming-Asus-ROG-Strix-G16-G614JV-N4086W-i7-13650HX-16GB-512GB-RTX-4060-Windows-11-i.88201679.22274851269",
        "",
        "",
        "",
        "",
        39490000,
        39990000,
    ],
]

# Create DataFrame with product data
df_products = pd.DataFrame(products, columns=[
    "Link", 
    "Phân loại 1", 
    "Phân loại 2", 
    "% Giảm giá", 
    today, 
    yesterday, 
    day_before
])

# Create configuration row
config_df = pd.DataFrame([["link_column=A;var1_column=B;var2_column=C;discount_column=D"] + [""] * 6], 
                          columns=df_products.columns)

# Combine configuration row with product data
final_df = pd.concat([config_df, df_products], ignore_index=True)

# Write to Excel
filename = "shopee_sample.xlsx"
final_df.to_excel(filename, index=False)

print(f"Sample Excel file created at: {filename}")
print("This file can be used with the Shopee Price Tracker application.")
print("It includes sample product links from Shopee and configuration in the first row.")