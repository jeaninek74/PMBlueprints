"""
OAuth Routes for Google and Apple Sign-In
"""
from flask import Blueprint, redirect, url_for, session, request, flash
from flask_login import login_user, current_user
from models import User, db
import secrets

oauth_bp = Blueprint('oauth', __name__, url_prefix='/auth')

def init_oauth_routes(app, oauth):
    """Initialize OAuth routes with app and oauth instance"""
    
    @oauth_bp.route('/login/google')
    def google_login():
        """Initiate Google OAuth login"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        redirect_uri = url_for('oauth.google_callback', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    
    @oauth_bp.route('/callback/google')
    def google_callback():
        """Handle Google OAuth callback"""
        try:
            token = oauth.google.authorize_access_token()
            user_info = token.get('userinfo')
            
            if not user_info:
                flash('Failed to get user information from Google', 'error')
                return redirect(url_for('auth.login'))
            
            # Get or create user
            email = user_info.get('email')
            name = user_info.get('name', email.split('@')[0])
            
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Create new user
                user = User(
                    email=email,
                    username=email.split('@')[0],
                    full_name=name,
                    oauth_provider='google',
                    oauth_id=user_info.get('sub'),
                    email_verified=True
                )
                # Set a random password (won't be used for OAuth login)
                user.set_password(secrets.token_urlsafe(32))
                db.session.add(user)
                db.session.commit()
            else:
                # Update OAuth info if not set
                if not user.oauth_provider:
                    user.oauth_provider = 'google'
                    user.oauth_id = user_info.get('sub')
                    user.email_verified = True
                    db.session.commit()
            
            # Log in the user
            login_user(user, remember=True)
            flash(f'Welcome, {name}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = session.get('next', url_for('dashboard'))
            return redirect(next_page)
            
        except Exception as e:
            flash(f'Authentication failed: {str(e)}', 'error')
            return redirect(url_for('auth.login'))
    
    @oauth_bp.route('/login/apple')
    def apple_login():
        """Initiate Apple OAuth login"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        redirect_uri = url_for('oauth.apple_callback', _external=True)
        return oauth.apple.authorize_redirect(redirect_uri)
    
    @oauth_bp.route('/callback/apple')
    def apple_callback():
        """Handle Apple OAuth callback"""
        try:
            token = oauth.apple.authorize_access_token()
            user_info = token.get('userinfo')
            
            if not user_info:
                flash('Failed to get user information from Apple', 'error')
                return redirect(url_for('auth.login'))
            
            # Get or create user
            email = user_info.get('email')
            name = user_info.get('name', email.split('@')[0]) if email else 'Apple User'
            
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Create new user
                user = User(
                    email=email,
                    username=email.split('@')[0] if email else f'apple_user_{secrets.token_hex(4)}',
                    full_name=name,
                    oauth_provider='apple',
                    oauth_id=user_info.get('sub'),
                    email_verified=True
                )
                # Set a random password (won't be used for OAuth login)
                user.set_password(secrets.token_urlsafe(32))
                db.session.add(user)
                db.session.commit()
            else:
                # Update OAuth info if not set
                if not user.oauth_provider:
                    user.oauth_provider = 'apple'
                    user.oauth_id = user_info.get('sub')
                    user.email_verified = True
                    db.session.commit()
            
            # Log in the user
            login_user(user, remember=True)
            flash(f'Welcome, {name}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = session.get('next', url_for('dashboard'))
            return redirect(next_page)
            
        except Exception as e:
            flash(f'Authentication failed: {str(e)}', 'error')
            return redirect(url_for('auth.login'))
    
    # Register blueprint
    app.register_blueprint(oauth_bp)
    
    return oauth_bp

