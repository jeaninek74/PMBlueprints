"""
Force delete Business Case templates by removing download history first
"""
from flask import Blueprint, jsonify
from app import db
from models import Template, DownloadHistory

delete_bc_bp = Blueprint('delete_business_cases_force', __name__)

@delete_bc_bp.route('/api/admin/delete-business-cases-force', methods=['POST'])
def delete_business_cases_force():
    """Force delete all Business Case templates and their download history"""
    try:
        # Find all Business Case templates
        business_case_templates = Template.query.filter(
            Template.category == 'Business Case'
        ).all()
        
        if not business_case_templates:
            return jsonify({
                'success': True,
                'message': 'No Business Case templates found',
                'deleted_count': 0
            })
        
        template_ids = [t.id for t in business_case_templates]
        
        # First, delete all download history records for these templates
        download_history_deleted = DownloadHistory.query.filter(
            DownloadHistory.template_id.in_(template_ids)
        ).delete(synchronize_session=False)
        
        # Then delete the templates
        templates_deleted = Template.query.filter(
            Template.id.in_(template_ids)
        ).delete(synchronize_session=False)
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Deleted {templates_deleted} Business Case templates',
            'templates_deleted': templates_deleted,
            'download_history_deleted': download_history_deleted,
            'template_ids': template_ids
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

