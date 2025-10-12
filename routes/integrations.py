"""
PMBlueprints Integration Routes
API endpoints for platform integrations (Monday.com, Smartsheet, Workday)
"""

from flask import Blueprint, request, jsonify
from platform_integrations import integrations

integrations_bp = Blueprint('integrations', __name__)

# ==================== Monday.com Routes ====================

@integrations_bp.route('/monday/export', methods=['POST'])
def monday_export():
    """Export template to Monday.com"""
    try:
        data = request.get_json()
        
        template_data = data.get('template_data', {})
        board_id = data.get('board_id')
        
        result = integrations.monday_export_template(template_data, board_id)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/monday/preserve-formulas', methods=['POST'])
def monday_preserve_formulas():
    """Preserve Excel formulas for Monday.com export"""
    try:
        data = request.get_json()
        
        template_path = data.get('template_path')
        
        if not template_path:
            return jsonify({
                'success': False,
                'error': 'template_path required'
            }), 400
        
        result = integrations.monday_preserve_formulas(template_path)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== Smartsheet Routes ====================

@integrations_bp.route('/smartsheet/sync', methods=['POST'])
def smartsheet_sync():
    """Synchronize template with Smartsheet"""
    try:
        data = request.get_json()
        
        template_data = data.get('template_data', {})
        sheet_id = data.get('sheet_id')
        
        result = integrations.smartsheet_sync_project(template_data, sheet_id)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== Workday Routes ====================

@integrations_bp.route('/workday/hcm', methods=['POST'])
def workday_hcm():
    """Integrate with Workday HCM"""
    try:
        data = request.get_json()
        
        project_data = data.get('project_data', {})
        integration_type = data.get('integration_type', 'resource_planning')
        
        result = integrations.workday_hcm_integration(project_data, integration_type)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== Google Sheets Routes ====================

@integrations_bp.route('/google-sheets/export', methods=['POST'])
def google_sheets_export():
    """Export template to Google Sheets"""
    try:
        data = request.get_json()
        
        template_data = data.get('template_data', {})
        spreadsheet_id = data.get('spreadsheet_id')
        
        result = integrations.google_sheets_export_template(template_data, spreadsheet_id)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/google-sheets/preserve-formulas', methods=['POST'])
def google_sheets_preserve_formulas():
    """Preserve Excel formulas for Google Sheets export"""
    try:
        data = request.get_json()
        
        template_path = data.get('template_path')
        
        if not template_path:
            return jsonify({
                'success': False,
                'error': 'template_path required'
            }), 400
        
        result = integrations.google_sheets_preserve_formulas(template_path)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== General Integration Routes ====================

@integrations_bp.route('/status', methods=['GET'])
def integration_status():
    """Get status of all platform integrations"""
    try:
        status = integrations.get_integration_status()
        
        return jsonify({
            'success': True,
            'integrations': status
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/test/<platform>', methods=['GET'])
def test_integration(platform):
    """Test connection to a specific platform"""
    try:
        result = integrations.test_integration(platform)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/health', methods=['GET'])
def integrations_health():
    """Health check for integrations service"""
    return jsonify({
        'success': True,
        'service': 'integrations',
        'status': 'healthy',
        'integrations_available': ['monday', 'smartsheet', 'workday', 'google_sheets']
    }), 200

