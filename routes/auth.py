"""
Authentication Routes
Handles user registration, login, logout, and profile management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import stripe
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    try:
        # Get form data
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        company = data.get('company', '').strip()
        
        # Validation
        if not all([email, password, first_name, last_name]):
            if request.is_json:
                return jsonify({'success': False, 'error': 'All fields are required'}), 400
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))
        
        # Import here to avoid circular imports
        from app import db, User
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'success': False, 'error': 'Email already registered'}), 400
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # Create Stripe customer
        try:
            stripe_customer = stripe.Customer.create(
                email=email,
                name=f"{first_name} {last_name}",
                metadata={'company': company}
            )
            stripe_customer_id = stripe_customer.id
        except Exception as e:
            logger.error(f"Stripe customer creation failed: {e}")
            stripe_customer_id = None
        
        # Create new user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company=company,
            stripe_customer_id=stripe_customer_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log in the user
        login_user(user)
        
        logger.info(f"New user registered: {email}")
        
        if request.is_json:
            return jsonify({
                'success': True, 
                'message': 'Registration successful',
                'redirect': url_for('dashboard')
            })
        
        flash('Registration successful! Welcome to PMBlueprints.', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Registration failed'}), 500
        flash('Registration failed. Please try again.', 'error')
        return redirect(url_for('auth.register'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    try:
        # Get form data
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        if not email or not password:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Email and password required'}), 400
            flash('Email and password required', 'error')
            return redirect(url_for('auth.login'))
        
        # Import here to avoid circular imports
        from app import db, User
        from datetime import datetime
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log in user
            login_user(user, remember=remember)
            
            logger.info(f"User logged in: {email}")
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'redirect': url_for('dashboard')
                })
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Login failed'}), 500
        flash('Login failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/demo-login')
def demo_login():
    """Demo login for testing"""
    try:
        from flask import current_app
        from app import db, User
        
        # Find or create demo user
        demo_user = User.query.filter_by(email='demo@pmblueprints.com').first()
        
        if not demo_user:
            demo_user = User(
                email='demo@pmblueprints.com',
                first_name='Demo',
                last_name='User',
                company='PMBlueprints Demo',
                subscription_plan='professional'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()
        
        login_user(demo_user)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Demo login successful',
                'redirect': url_for('dashboard')
            })
        
        flash('Demo login successful!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Demo login error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Demo login failed'}), 500
        flash('Demo login failed', 'error')
        return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'GET':
        return render_template('auth/profile.html', user=current_user)
    
    try:
        # Get form data
        data = request.get_json() if request.is_json else request.form
        
        # Update user information
        current_user.first_name = data.get('first_name', current_user.first_name).strip()
        current_user.last_name = data.get('last_name', current_user.last_name).strip()
        current_user.company = data.get('company', current_user.company or '').strip()
        
        # Update password if provided
        new_password = data.get('new_password')
        if new_password:
            current_password = data.get('current_password')
            if not current_user.check_password(current_password):
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Current password incorrect'}), 400
                flash('Current password incorrect', 'error')
                return redirect(url_for('auth.profile'))
            
            current_user.set_password(new_password)
        
        from app import db
        db.session.commit()
        
        logger.info(f"Profile updated for user: {current_user.email}")
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'user': current_user.to_dict()
            })
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Profile update failed'}), 500
        flash('Profile update failed', 'error')
        return redirect(url_for('auth.profile'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset (simplified version)"""
    if request.method == 'GET':
        return render_template('auth/reset_password.html')
    
    # For production, implement proper email-based password reset
    # This is a simplified version for demo purposes
    
    try:
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        
        if not email:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Email required'}), 400
            flash('Email required', 'error')
            return redirect(url_for('auth.reset_password'))
        
        # In production, send reset email here
        logger.info(f"Password reset requested for: {email}")
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Password reset instructions sent to your email'
            })
        
        flash('Password reset instructions sent to your email', 'info')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Password reset failed'}), 500
        flash('Password reset failed', 'error')
        return redirect(url_for('auth.reset_password'))
