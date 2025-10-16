"""
Platform OAuth Integration Routes
Handles OAuth flows for Monday.com, Smartsheet, Google Sheets, and Microsoft 365
"""

from flask import Blueprint, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
import logging
import os
import requests
from datetime import datetime
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

platform_oauth_bp = Blueprint('platform_oauth', __name__, url_prefix='/integrations/oauth')

# OAuth Configuration
MONDAY_CLIENT_ID = os.getenv('MONDAY_CLIENT_ID')
MONDAY_CLIENT_SECRET = os.getenv('MONDAY_CLIENT_SECRET')
MONDAY_AUTH_URL = "https://auth.monday.com/oauth2/authorize"
MONDAY_TOKEN_URL = "https://auth.monday.com/oauth2/token"

SMARTSHEET_CLIENT_ID = os.getenv('SMARTSHEET_CLIENT_ID')
SMARTSHEET_CLIENT_SECRET = os.getenv('SMARTSHEET_CLIENT_SECRET')
SMARTSHEET_AUTH_URL = "https://app.smartsheet.com/b/authorize"
SMARTSHEET_TOKEN_URL = "https://api.smartsheet.com/2.0/token"

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
MICROSOFT_CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')
MICROSOFT_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

# ============================================================================
# MONDAY.COM OAUTH
# ============================================================================

@platform_oauth_bp.route('/monday/connect')
@login_required
def monday_connect():
    """Initiate Monday.com OAuth flow"""
    
    redirect_uri = url_for('platform_oauth.monday_callback', _external=True)
    
    params = {
        'client_id': MONDAY_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'boards:read boards:write'
    }
    
    auth_url = f"{MONDAY_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

@platform_oauth_bp.route('/monday/callback')
@login_required
def monday_callback():
    """Handle Monday.com OAuth callback"""
    from models import IntegrationSettings
    from database import db
    
    code = request.args.get('code')
    if not code:
        flash('Monday.com connection failed', 'error')
        return redirect(url_for('integrations.index'))
    
    try:
        # Exchange code for token
        redirect_uri = url_for('platform_oauth.monday_callback', _external=True)
        
        token_data = {
            'code': code,
            'client_id': MONDAY_CLIENT_ID,
            'client_secret': MONDAY_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(MONDAY_TOKEN_URL, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        # Save token to database
        settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
        if not settings:
            settings = IntegrationSettings(user_id=current_user.id)
            db.session.add(settings)
        
        settings.monday_access_token = tokens.get('access_token')
        settings.monday_refresh_token = tokens.get('refresh_token')
        settings.monday_connected = True
        settings.monday_connected_at = datetime.utcnow()
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Successfully connected to Monday.com!', 'success')
        return redirect(url_for('integrations.index'))
        
    except Exception as e:
        logger.error(f"Monday.com OAuth error: {str(e)}")
        flash('Failed to connect to Monday.com', 'error')
        return redirect(url_for('integrations.index'))

@platform_oauth_bp.route('/monday/disconnect')
@login_required
def monday_disconnect():
    """Disconnect Monday.com"""
    from models import IntegrationSettings
    from database import db
    
    settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
    if settings:
        settings.monday_access_token = None
        settings.monday_refresh_token = None
        settings.monday_connected = False
        settings.monday_connected_at = None
        db.session.commit()
    
    flash('Disconnected from Monday.com', 'success')
    return redirect(url_for('integrations.index'))

# ============================================================================
# SMARTSHEET OAUTH
# ============================================================================

@platform_oauth_bp.route('/smartsheet/connect')
@login_required
def smartsheet_connect():
    """Initiate Smartsheet OAuth flow"""
    
    redirect_uri = url_for('platform_oauth.smartsheet_callback', _external=True)
    
    params = {
        'client_id': SMARTSHEET_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'READ_SHEETS WRITE_SHEETS CREATE_SHEETS'
    }
    
    auth_url = f"{SMARTSHEET_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

@platform_oauth_bp.route('/smartsheet/callback')
@login_required
def smartsheet_callback():
    """Handle Smartsheet OAuth callback"""
    from models import IntegrationSettings
    from database import db
    
    code = request.args.get('code')
    if not code:
        flash('Smartsheet connection failed', 'error')
        return redirect(url_for('integrations.index'))
    
    try:
        # Exchange code for token
        redirect_uri = url_for('platform_oauth.smartsheet_callback', _external=True)
        
        token_data = {
            'code': code,
            'client_id': SMARTSHEET_CLIENT_ID,
            'client_secret': SMARTSHEET_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(SMARTSHEET_TOKEN_URL, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        # Save token to database
        settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
        if not settings:
            settings = IntegrationSettings(user_id=current_user.id)
            db.session.add(settings)
        
        settings.smartsheet_access_token = tokens.get('access_token')
        settings.smartsheet_refresh_token = tokens.get('refresh_token')
        settings.smartsheet_connected = True
        settings.smartsheet_connected_at = datetime.utcnow()
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Successfully connected to Smartsheet!', 'success')
        return redirect(url_for('integrations.index'))
        
    except Exception as e:
        logger.error(f"Smartsheet OAuth error: {str(e)}")
        flash('Failed to connect to Smartsheet', 'error')
        return redirect(url_for('integrations.index'))

@platform_oauth_bp.route('/smartsheet/disconnect')
@login_required
def smartsheet_disconnect():
    """Disconnect Smartsheet"""
    from models import IntegrationSettings
    from database import db
    
    settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
    if settings:
        settings.smartsheet_access_token = None
        settings.smartsheet_refresh_token = None
        settings.smartsheet_connected = False
        settings.smartsheet_connected_at = None
        db.session.commit()
    
    flash('Disconnected from Smartsheet', 'success')
    return redirect(url_for('integrations.index'))

# ============================================================================
# GOOGLE SHEETS OAUTH
# ============================================================================

@platform_oauth_bp.route('/google/connect')
@login_required
def google_connect():
    """Initiate Google Sheets OAuth flow"""
    
    redirect_uri = url_for('platform_oauth.google_callback', _external=True)
    
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

@platform_oauth_bp.route('/google/callback')
@login_required
def google_callback():
    """Handle Google Sheets OAuth callback"""
    from models import IntegrationSettings
    from database import db
    
    code = request.args.get('code')
    if not code:
        flash('Google Sheets connection failed', 'error')
        return redirect(url_for('integrations.index'))
    
    try:
        # Exchange code for token
        redirect_uri = url_for('platform_oauth.google_callback', _external=True)
        
        token_data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        # Save token to database
        settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
        if not settings:
            settings = IntegrationSettings(user_id=current_user.id)
            db.session.add(settings)
        
        settings.google_access_token = tokens.get('access_token')
        settings.google_refresh_token = tokens.get('refresh_token')
        settings.google_connected = True
        settings.google_connected_at = datetime.utcnow()
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Successfully connected to Google Sheets!', 'success')
        return redirect(url_for('integrations.index'))
        
    except Exception as e:
        logger.error(f"Google Sheets OAuth error: {str(e)}")
        flash('Failed to connect to Google Sheets', 'error')
        return redirect(url_for('integrations.index'))

@platform_oauth_bp.route('/google/disconnect')
@login_required
def google_disconnect():
    """Disconnect Google Sheets"""
    from models import IntegrationSettings
    from database import db
    
    settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
    if settings:
        settings.google_access_token = None
        settings.google_refresh_token = None
        settings.google_connected = False
        settings.google_connected_at = None
        db.session.commit()
    
    flash('Disconnected from Google Sheets', 'success')
    return redirect(url_for('integrations.index'))

# ============================================================================
# MICROSOFT 365 OAUTH
# ============================================================================

@platform_oauth_bp.route('/microsoft/connect')
@login_required
def microsoft_connect():
    """Initiate Microsoft 365 OAuth flow"""
    
    redirect_uri = url_for('platform_oauth.microsoft_callback', _external=True)
    
    params = {
        'client_id': MICROSOFT_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'Files.ReadWrite.All offline_access',
        'response_mode': 'query'
    }
    
    auth_url = f"{MICROSOFT_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

@platform_oauth_bp.route('/microsoft/callback')
@login_required
def microsoft_callback():
    """Handle Microsoft 365 OAuth callback"""
    from models import IntegrationSettings
    from database import db
    
    code = request.args.get('code')
    if not code:
        flash('Microsoft 365 connection failed', 'error')
        return redirect(url_for('integrations.index'))
    
    try:
        # Exchange code for token
        redirect_uri = url_for('platform_oauth.microsoft_callback', _external=True)
        
        token_data = {
            'code': code,
            'client_id': MICROSOFT_CLIENT_ID,
            'client_secret': MICROSOFT_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(MICROSOFT_TOKEN_URL, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        # Save token to database
        settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
        if not settings:
            settings = IntegrationSettings(user_id=current_user.id)
            db.session.add(settings)
        
        settings.microsoft_access_token = tokens.get('access_token')
        settings.microsoft_refresh_token = tokens.get('refresh_token')
        settings.microsoft_connected = True
        settings.microsoft_connected_at = datetime.utcnow()
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Successfully connected to Microsoft 365!', 'success')
        return redirect(url_for('integrations.index'))
        
    except Exception as e:
        logger.error(f"Microsoft 365 OAuth error: {str(e)}")
        flash('Failed to connect to Microsoft 365', 'error')
        return redirect(url_for('integrations.index'))

@platform_oauth_bp.route('/microsoft/disconnect')
@login_required
def microsoft_disconnect():
    """Disconnect Microsoft 365"""
    from models import IntegrationSettings
    from database import db
    
    settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
    if settings:
        settings.microsoft_access_token = None
        settings.microsoft_refresh_token = None
        settings.microsoft_connected = False
        settings.microsoft_connected_at = None
        db.session.commit()
    
    flash('Disconnected from Microsoft 365', 'success')
    return redirect(url_for('integrations.index'))

