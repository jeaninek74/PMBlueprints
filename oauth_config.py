"""
OAuth Configuration for Google Sign-In and Platform Integrations
"""
import os
from authlib.integrations.flask_client import OAuth

def init_oauth(app):
    """Initialize OAuth with Flask app"""
    oauth = OAuth(app)
    
    # Google OAuth Configuration (for login)
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    # Google Workspace OAuth Configuration (for platform integration)
    # Includes: Sheets, Drive, Docs, Calendar
    google_workspace = oauth.register(
        name='google_workspace',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),  # Same as login, but different scopes
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/calendar'
        }
    )
    
    # Microsoft 365 OAuth Configuration (for platform integration)
    # Includes: Project, Planner, Teams, SharePoint, OneDrive
    microsoft_365 = oauth.register(
        name='microsoft_365',
        client_id=os.getenv('MICROSOFT_CLIENT_ID'),
        client_secret=os.getenv('MICROSOFT_CLIENT_SECRET'),
        access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
        authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        api_base_url='https://graph.microsoft.com/v1.0',
        client_kwargs={
            'scope': 'User.Read Files.ReadWrite.All Sites.ReadWrite.All Tasks.ReadWrite Group.ReadWrite.All'
        }
    )
    
    # Monday.com OAuth Configuration (for platform integration)
    monday = oauth.register(
        name='monday',
        client_id=os.getenv('MONDAY_CLIENT_ID'),
        client_secret=os.getenv('MONDAY_CLIENT_SECRET'),
        access_token_url='https://auth.monday.com/oauth2/token',
        authorize_url='https://auth.monday.com/oauth2/authorize',
        api_base_url='https://api.monday.com/v2',
        client_kwargs={
            'scope': 'boards:read boards:write workspaces:read'
        }
    )
    
    # Smartsheet OAuth Configuration (for platform integration)
    smartsheet = oauth.register(
        name='smartsheet',
        client_id=os.getenv('SMARTSHEET_CLIENT_ID'),
        client_secret=os.getenv('SMARTSHEET_CLIENT_SECRET'),
        access_token_url='https://api.smartsheet.com/2.0/token',
        authorize_url='https://app.smartsheet.com/b/authorize',
        api_base_url='https://api.smartsheet.com/2.0',
        client_kwargs={
            'scope': 'READ_SHEETS WRITE_SHEETS CREATE_SHEETS'
        }
    )
    
    # Workday OAuth Configuration (for platform integration)
    workday = oauth.register(
        name='workday',
        client_id=os.getenv('WORKDAY_CLIENT_ID'),
        client_secret=os.getenv('WORKDAY_CLIENT_SECRET'),
        access_token_url=f'https://wd2-impl.workday.com/{os.getenv("WORKDAY_TENANT")}/oauth2/token',
        authorize_url=f'https://wd2-impl.workday.com/{os.getenv("WORKDAY_TENANT")}/oauth2/authorize',
        api_base_url=f'https://wd2-impl.workday.com/ccx/service/{os.getenv("WORKDAY_TENANT")}',
        client_kwargs={
            'scope': 'openid'
        }
    )
    
    return oauth

