"""
OAuth Routes for Google Sign-In and Platform Integrations
"""
from flask import Blueprint, redirect, url_for, session, request, flash, jsonify
from flask_login import login_user, current_user, login_required
from models import User, db
import secrets
import json

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
    
    # ==================== Platform Integration OAuth Routes ====================
    
    @oauth_bp.route('/connect/<platform>')
    @login_required
    def connect_platform(platform):
        """Initiate OAuth connection to a platform integration"""
        valid_platforms = ['google_workspace', 'microsoft_365', 'monday', 'smartsheet', 'workday']
        
        if platform not in valid_platforms:
            flash(f'Invalid platform: {platform}', 'error')
            return redirect(url_for('dashboard'))
        
        # Store the platform in session for callback
        session['connecting_platform'] = platform
        
        redirect_uri = url_for('oauth.platform_callback', platform=platform, _external=True)
        
        if platform == 'google_workspace':
            return oauth.google_workspace.authorize_redirect(redirect_uri)
        elif platform == 'microsoft_365':
            return oauth.microsoft_365.authorize_redirect(redirect_uri)
        elif platform == 'monday':
            return oauth.monday.authorize_redirect(redirect_uri)
        elif platform == 'smartsheet':
            return oauth.smartsheet.authorize_redirect(redirect_uri)
        elif platform == 'workday':
            return oauth.workday.authorize_redirect(redirect_uri)
    
    @oauth_bp.route('/callback/<platform>')
    @login_required
    def platform_callback(platform):
        """Handle OAuth callback from platform integrations"""
        try:
            # Get the OAuth token based on platform
            if platform == 'google_workspace':
                token = oauth.google_workspace.authorize_access_token()
            elif platform == 'microsoft_365':
                token = oauth.microsoft_365.authorize_access_token()
            elif platform == 'monday':
                token = oauth.monday.authorize_access_token()
            elif platform == 'smartsheet':
                token = oauth.smartsheet.authorize_access_token()
            elif platform == 'workday':
                token = oauth.workday.authorize_access_token()
            else:
                flash(f'Invalid platform: {platform}', 'error')
                return redirect(url_for('dashboard'))
            
            # Store the access token in user's session or database
            # For security, we'll store it encrypted in the database
            if not hasattr(current_user, 'platform_tokens'):
                current_user.platform_tokens = {}
            
            # Store token (in production, encrypt this!)
            platform_tokens = json.loads(current_user.platform_tokens or '{}')
            platform_tokens[platform] = {
                'access_token': token.get('access_token'),
                'refresh_token': token.get('refresh_token'),
                'expires_at': token.get('expires_at')
            }
            current_user.platform_tokens = json.dumps(platform_tokens)
            db.session.commit()
            
            flash(f'Successfully connected to {platform.title()}!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Failed to connect to {platform}: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
    
    @oauth_bp.route('/disconnect/<platform>', methods=['POST'])
    @login_required
    def disconnect_platform(platform):
        """Disconnect a platform integration"""
        try:
            if hasattr(current_user, 'platform_tokens') and current_user.platform_tokens:
                platform_tokens = json.loads(current_user.platform_tokens)
                if platform in platform_tokens:
                    del platform_tokens[platform]
                    current_user.platform_tokens = json.dumps(platform_tokens)
                    db.session.commit()
                    flash(f'Disconnected from {platform.title()}', 'success')
                else:
                    flash(f'Not connected to {platform}', 'info')
            else:
                flash(f'Not connected to {platform}', 'info')
        except Exception as e:
            flash(f'Error disconnecting: {str(e)}', 'error')
        
        return redirect(url_for('dashboard'))
    
    # Register blueprint
    app.register_blueprint(oauth_bp)
    
    return oauth_bp

