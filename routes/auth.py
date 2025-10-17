"""
Authentication Routes
Handles user registration, login, logout, and Google OAuth
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os
import requests
from datetime import datetime
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('account.dashboard'))
    
    if request.method == 'POST':
        from models import User
        from database import db
        
        logger.info("Registration POST request received")
        
        # Handle both form data and JSON submissions
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            company = data.get('company', '').strip()
        else:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            company = request.form.get('company', '').strip()
        
        logger.info(f"Registration attempt for email: {email}")
        
        # Validation
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('auth/register.html')
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        try:
            # Create new user
            logger.info(f"Creating new user: {email}")
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                company=company,
                subscription_tier='free',
                subscription_status='active',
                created_at=datetime.utcnow(),
                email_verified=False
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            logger.info(f"User created successfully: {email}")
            
            # Log user in
            login_user(user)
            logger.info(f"User logged in after registration: {email}")
            
            flash('Account created successfully!', 'success')
            return redirect(url_for('account.dashboard'))
            
        except Exception as e:
            logger.error(f"Registration error for {email}: {str(e)}")
            db.session.rollback()
            flash('An error occurred during registration', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('account.dashboard'))
    
    if request.method == 'POST':
        from models import User
        from flask import session as flask_session
        import redis
        
        # Delete ALL stale sessions from Redis before login
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            try:
                r = redis.from_url(redis_url)
                session_keys = r.keys('pmb:*')
                if session_keys:
                    r.delete(*session_keys)
                    logger.info(f"Deleted {len(session_keys)} stale Redis session(s)")
            except Exception as e:
                logger.error(f"Redis cleanup error: {e}")
        
        # Clear Flask session
        flask_session.clear()
        flask_session.modified = True
        
        # Handle both form data and JSON submissions
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            remember = data.get('remember', False)
        else:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            remember = request.form.get('remember', False)
        
        logger.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            logger.warning(f"Missing credentials: email={bool(email)}, password={bool(password)}")
            flash('Email and password are required', 'error')
            return render_template('auth/login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.warning(f"User not found: {email}")
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
        
        if not user.check_password(password):
            logger.warning(f"Invalid password for user: {email}")
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
        
        # Log user in
        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        
        from database import db
        db.session.commit()
        
        flash('Welcome back!', 'success')
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('account.dashboard'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/google')
def google_login():
    """Initiate Google OAuth login"""
    
    # Get Google OAuth URLs
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    # Construct redirect URI
    redirect_uri = url_for('auth.google_callback', _external=True)
    
    # Build authorization URL
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': 'openid email profile',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'select_account'
    }
    
    authorization_url = f"{authorization_endpoint}?{urlencode(params)}"
    
    return redirect(authorization_url)

@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    from models import User
    from database import db
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        flash('Google login failed', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Get Google OAuth URLs
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Exchange code for token
        token_data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': url_for('auth.google_callback', _external=True),
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_endpoint, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Get user info
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        userinfo_response = requests.get(userinfo_endpoint, headers=headers)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
        
        # Extract user data
        google_id = userinfo['sub']
        email = userinfo['email']
        email_verified = userinfo.get('email_verified', False)
        first_name = userinfo.get('given_name', '')
        last_name = userinfo.get('family_name', '')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                oauth_provider='google',
                oauth_id=google_id,
                email_verified=email_verified,
                subscription_tier='free',
                subscription_status='active',
                created_at=datetime.utcnow()
            )
            db.session.add(user)
        else:
            # Update existing user
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_id = google_id
            user.email_verified = email_verified
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log user in
        login_user(user)
        
        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('account.dashboard'))
        
    except requests.RequestException as e:
        logger.error(f"Google OAuth error: {str(e)}")
        flash('Google login failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    except Exception as e:
        logger.error(f"Google callback error: {str(e)}")
        db.session.rollback()
        flash('An error occurred during Google login', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Email is required', 'error')
            return render_template('auth/forgot_password.html')
        
        from models import User
        user = User.query.filter_by(email=email).first()
        
        # Always show success message for security
        flash('If an account exists with that email, a password reset link has been sent.', 'success')
        
        if user:
            # TODO: Send password reset email
            logger.info(f"Password reset requested for {email}")
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    # TODO: Implement token verification and password reset
    flash('Password reset functionality coming soon', 'info')
    return redirect(url_for('auth.login'))

