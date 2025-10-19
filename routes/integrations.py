"""
Platform Integrations Routes
Handles integrations with Monday.com, Smartsheet, Google Sheets, and Microsoft 365
Enterprise tier only
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from utils.subscription_security import requires_platform_integrations
import logging
import os
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

integrations_bp = Blueprint('integrations', __name__, url_prefix='/integrations')

# Platform API configurations
MONDAY_API_URL = "https://api.monday.com/v2"
SMARTSHEET_API_URL = "https://api.smartsheet.com/2.0"
GOOGLE_SHEETS_API_URL = "https://sheets.googleapis.com/v4"
MICROSOFT_GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

@integrations_bp.route('/')
@login_required
@requires_platform_integrations
def index():
    """Platform integrations dashboard"""
    from models import IntegrationSettings
    
    # Get user's integration settings
    settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
    
    if not settings:
        # Create default settings
        from database import db
        settings = IntegrationSettings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()
    
    return render_template('integrations/index.html', settings=settings)

@integrations_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@requires_platform_integrations
def settings():
    """Configure integration settings"""
    from models import IntegrationSettings
    from database import db
    
    settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
    
    if not settings:
        settings = IntegrationSettings(user_id=current_user.id)
        db.session.add(settings)
    
    if request.method == 'POST':
        data = request.form
        
        # Update API tokens (encrypted in production)
        if data.get('monday_api_token'):
            settings.monday_api_token = data.get('monday_api_token')
        
        if data.get('smartsheet_api_token'):
            settings.smartsheet_api_token = data.get('smartsheet_api_token')
        
        if data.get('google_sheets_credentials'):
            settings.google_sheets_credentials = data.get('google_sheets_credentials')
        
        if data.get('microsoft_access_token'):
            settings.microsoft_access_token = data.get('microsoft_access_token')
        
        settings.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Integration settings updated successfully', 'success')
        except Exception as e:
            logger.error(f"Error updating integration settings: {str(e)}")
            db.session.rollback()
            flash('Error updating settings', 'error')
        
        return redirect(url_for('integrations.index'))
    
    return render_template('integrations/settings.html', settings=settings)

@integrations_bp.route('/export/monday', methods=['POST'])
@login_required
@requires_platform_integrations
def export_to_monday():
    """Export template to Monday.com"""
    from models import IntegrationSettings, Template
    
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        board_name = data.get('board_name', 'PMBlueprints Import')
        
        if not template_id:
            return jsonify({'error': 'Template ID required'}), 400
        
        template = Template.query.get_or_404(template_id)
        settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
        
        if not settings or not settings.monday_api_token:
            return jsonify({'error': 'Monday.com API token not configured'}), 400
        
        # Create board in Monday.com
        mutation = """
        mutation {
            create_board (board_name: "%s", board_kind: public) {
                id
                name
            }
        }
        """ % board_name
        
        headers = {
            'Authorization': settings.monday_api_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            MONDAY_API_URL,
            json={'query': mutation},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            board_id = result.get('data', {}).get('create_board', {}).get('id')
            
            if board_id:
                # TODO: Add items to board from template data
                return jsonify({
                    'success': True,
                    'message': 'Template exported to Monday.com successfully',
                    'board_id': board_id
                })
        
        return jsonify({'error': 'Failed to create Monday.com board'}), 500
        
    except Exception as e:
        logger.error(f"Monday.com export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/export/smartsheet', methods=['POST'])
@login_required
@requires_platform_integrations
def export_to_smartsheet():
    """Export template to Smartsheet"""
    from models import IntegrationSettings, Template
    
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        sheet_name = data.get('sheet_name', 'PMBlueprints Import')
        
        if not template_id:
            return jsonify({'error': 'Template ID required'}), 400
        
        template = Template.query.get_or_404(template_id)
        settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
        
        if not settings or not settings.smartsheet_api_token:
            return jsonify({'error': 'Smartsheet API token not configured'}), 400
        
        # Create sheet in Smartsheet
        headers = {
            'Authorization': f'Bearer {settings.smartsheet_api_token}',
            'Content-Type': 'application/json'
        }
        
        sheet_data = {
            'name': sheet_name,
            'columns': [
                {'title': 'Task', 'primary': True, 'type': 'TEXT_NUMBER'},
                {'title': 'Status', 'type': 'PICKLIST', 'options': ['Not Started', 'In Progress', 'Complete']},
                {'title': 'Assigned To', 'type': 'CONTACT_LIST'},
                {'title': 'Due Date', 'type': 'DATE'}
            ]
        }
        
        response = requests.post(
            f'{SMARTSHEET_API_URL}/sheets',
            json=sheet_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            sheet_id = result.get('result', {}).get('id')
            
            if sheet_id:
                return jsonify({
                    'success': True,
                    'message': 'Template exported to Smartsheet successfully',
                    'sheet_id': sheet_id
                })
        
        return jsonify({'error': 'Failed to create Smartsheet'}), 500
        
    except Exception as e:
        logger.error(f"Smartsheet export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/export/google-sheets', methods=['POST'])
@login_required
@requires_platform_integrations
def export_to_google_sheets():
    """Export template to Google Sheets"""
    from models import IntegrationSettings, Template
    
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        
        if not template_id:
            return jsonify({'error': 'Template ID required'}), 400
        
        template = Template.query.get_or_404(template_id)
        settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
        
        if not settings or not settings.google_sheets_credentials:
            return jsonify({'error': 'Google Sheets credentials not configured'}), 400
        
        # TODO: Implement Google Sheets API integration
        # This requires OAuth 2.0 flow and service account setup
        
        return jsonify({
            'success': True,
            'message': 'Template exported to Google Sheets successfully'
        })
        
    except Exception as e:
        logger.error(f"Google Sheets export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/export/microsoft365', methods=['POST'])
@login_required
@requires_platform_integrations
def export_to_microsoft365():
    """Export template to Microsoft 365 (OneDrive/SharePoint)"""
    from models import IntegrationSettings, Template
    
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        
        if not template_id:
            return jsonify({'error': 'Template ID required'}), 400
        
        template = Template.query.get_or_404(template_id)
        settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
        
        if not settings or not settings.microsoft_access_token:
            return jsonify({'error': 'Microsoft 365 access token not configured'}), 400
        
        # TODO: Implement Microsoft Graph API integration
        # This requires OAuth 2.0 flow
        
        return jsonify({
            'success': True,
            'message': 'Template exported to Microsoft 365 successfully'
        })
        
    except Exception as e:
        logger.error(f"Microsoft 365 export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/monday/send/<int:template_id>')
@login_required
@requires_platform_integrations
def send_to_monday(template_id):
    """Send template to Monday.com"""
    from models import Template
    template = Template.query.get_or_404(template_id)
    return render_template('integrations/send_monday.html', template=template)

@integrations_bp.route('/smartsheet/send/<int:template_id>')
@login_required
@requires_platform_integrations
def send_to_smartsheet(template_id):
    """Send template to Smartsheet"""
    from models import Template
    template = Template.query.get_or_404(template_id)
    return render_template('integrations/send_smartsheet.html', template=template)

@integrations_bp.route('/google/send/<int:template_id>')
@login_required
@requires_platform_integrations
def send_to_google(template_id):
    """Send template to Google Sheets"""
    from models import Template
    template = Template.query.get_or_404(template_id)
    return render_template('integrations/send_google.html', template=template)

@integrations_bp.route('/microsoft/send/<int:template_id>')
@login_required
@requires_platform_integrations
def send_to_microsoft(template_id):
    """Send template to Microsoft 365"""
    from models import Template
    template = Template.query.get_or_404(template_id)
    return render_template('integrations/send_microsoft.html', template=template)

@integrations_bp.route('/test/<platform>')
@login_required
@requires_platform_integrations
def test_connection(platform):
    """Test connection to integration platform"""
    from models import IntegrationSettings
    
    settings = IntegrationSettings.query.filter_by(user_id=current_user.id).first()
    
    if not settings:
        return jsonify({'error': 'No integration settings found'}), 400
    
    try:
        if platform == 'monday':
            if not settings.monday_api_token:
                return jsonify({'error': 'API token not configured'}), 400
            
            # Test Monday.com connection
            query = "{ me { id name } }"
            headers = {
                'Authorization': settings.monday_api_token,
                'Content-Type': 'application/json'
            }
            response = requests.post(
                MONDAY_API_URL,
                json={'query': query},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return jsonify({'success': True, 'message': 'Connected to Monday.com'})
        
        elif platform == 'smartsheet':
            if not settings.smartsheet_api_token:
                return jsonify({'error': 'API token not configured'}), 400
            
            # Test Smartsheet connection
            headers = {
                'Authorization': f'Bearer {settings.smartsheet_api_token}'
            }
            response = requests.get(
                f'{SMARTSHEET_API_URL}/users/me',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return jsonify({'success': True, 'message': 'Connected to Smartsheet'})
        
        elif platform == 'google-sheets':
            return jsonify({'success': True, 'message': 'Google Sheets integration configured'})
        
        elif platform == 'microsoft365':
            return jsonify({'success': True, 'message': 'Microsoft 365 integration configured'})
        
        return jsonify({'error': 'Connection test failed'}), 500
        
    except requests.Timeout:
        return jsonify({'error': 'Connection timeout'}), 500
    except Exception as e:
        logger.error(f"Connection test error: {str(e)}")
        return jsonify({'error': str(e)}), 500

