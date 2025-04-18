"""
Database Models Module

This module defines the database models for the Shopee Price Tracker application.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

# Initialize SQLAlchemy instance to be used by the Flask app
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product_lists = relationship('ProductList', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class ProductList(db.Model):
    """Model for storing product lists (Excel files)."""
    __tablename__ = 'product_lists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    filename = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Configuration
    link_column = Column(String(10), nullable=False, default='A')
    var1_column = Column(String(10), nullable=True)
    var2_column = Column(String(10), nullable=True)
    discount_column = Column(String(10), nullable=True, default='D')
    
    # Relationships
    user = relationship('User', back_populates='product_lists')
    products = relationship('Product', back_populates='product_list', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ProductList {self.name}>'

class Product(db.Model):
    """Model for storing individual products."""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    product_list_id = Column(Integer, ForeignKey('product_lists.id'), nullable=False)
    url = Column(String(512), nullable=False)
    shop_id = Column(String(50), nullable=True)
    item_id = Column(String(50), nullable=True)
    row_index = Column(Integer, nullable=False)  # Row in Excel file
    var1 = Column(String(128), nullable=True)
    var2 = Column(String(128), nullable=True)
    
    # Relationships
    product_list = relationship('ProductList', back_populates='products')
    price_history = relationship('PriceHistory', back_populates='product', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.url}>'

class PriceHistory(db.Model):
    """Model for storing price history for products."""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    price = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    discount_percent = Column(Float, nullable=True)  # Calculated discount percentage
    
    # Relationships
    product = relationship('Product', back_populates='price_history')
    
    def __repr__(self):
        return f'<PriceHistory {self.product_id} {self.date} {self.price}>'

class JobStatus(db.Model):
    """Model for storing job status information."""
    __tablename__ = 'job_status'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_list_id = Column(Integer, ForeignKey('product_lists.id'), nullable=False)
    status = Column(String(50), nullable=False, default='pending')  # pending, running, completed, error
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_products = Column(Integer, nullable=True, default=0)
    processed_products = Column(Integer, nullable=True, default=0)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f'<JobStatus {self.id} {self.status}>'