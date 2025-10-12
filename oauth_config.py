"""
OAuth Configuration for Google and Apple Sign-In
"""
import os
from authlib.integrations.flask_client import OAuth

def init_oauth(app):
    """Initialize OAuth with Flask app"""
    oauth = OAuth(app)
    
    # Google OAuth Configuration
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    # Apple OAuth Configuration
    apple = oauth.register(
        name='apple',
        client_id=os.getenv('APPLE_CLIENT_ID'),
        client_secret=os.getenv('APPLE_CLIENT_SECRET'),
        server_metadata_url='https://appleid.apple.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'name email'
        }
    )
    
    return oauth

