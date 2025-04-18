"""
Authentication Module

This module handles user authentication in the Shopee Price Tracker application.
"""

import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

from models import db, User

# Create Blueprint
auth = Blueprint('auth', __name__)

# Initialize login manager to be used in app.py
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    """Load user from database."""
    return User.query.get(int(user_id))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validate inputs
        if not username or not email or not password:
            flash('Vui lòng điền đầy đủ thông tin', 'error')
            return render_template('auth/register.html')
        
        if password != password_confirm:
            flash('Mật khẩu nhập lại không khớp', 'error')
            return render_template('auth/register.html')
        
        # Validate email format
        try:
            valid_email = validate_email(email)
            email = valid_email.email
        except EmailNotValidError as e:
            flash(f'Email không hợp lệ: {str(e)}', 'error')
            return render_template('auth/register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Tên người dùng đã tồn tại', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=password_hash)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Đã xảy ra lỗi khi đăng ký: {str(e)}', 'error')
    
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        if not username or not password:
            flash('Vui lòng nhập tên người dùng và mật khẩu', 'error')
            return render_template('auth/login.html')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Tên người dùng hoặc mật khẩu không đúng', 'error')
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('Bạn đã đăng xuất thành công', 'success')
    return redirect(url_for('index'))

@auth.route('/profile')
@login_required
def profile():
    """Show user profile."""
    return render_template('auth/profile.html', user=current_user)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('Vui lòng điền đầy đủ thông tin', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('Mật khẩu mới nhập lại không khớp', 'error')
            return render_template('auth/change_password.html')
        
        # Check current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Mật khẩu hiện tại không đúng', 'error')
            return render_template('auth/change_password.html')
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            flash('Đổi mật khẩu thành công', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Đã xảy ra lỗi khi đổi mật khẩu: {str(e)}', 'error')
    
    return render_template('auth/change_password.html')