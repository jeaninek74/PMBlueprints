"""
Delete the missing Product_Business_Case.docx template entry
"""
from flask import Blueprint, jsonify
from database import db
from models import Template
import logging

logger = logging.getLogger(__name__)

delete_missing_bp = Blueprint('delete_missing', __name__)

@delete_missing_bp.route('/admin/delete-missing-business-case', methods=['GET'])
def delete_missing_business_case():
    """Delete the Product_Business_Case.docx entry (ID: 699) that has no file"""
    try:
        # Find the template
        template = Template.query.filter_by(
            id=699,
            industry='Product',
            file_path='Product_Business_Case.docx'
        ).first()
        
        if not template:
            return jsonify({
                'success': True,
                'message': 'Template not found (may have been already deleted)',
                'deleted': False
            })
        
        # Delete it
        template_info = {
            'id': template.id,
            'name': template.name,
            'industry': template.industry,
            'file_path': template.file_path
        }
        
        db.session.delete(template)
        db.session.commit()
        
        logger.info(f"Deleted missing template: {template_info}")
        
        return jsonify({
            'success': True,
            'message': 'Successfully deleted missing Business Case template entry',
            'deleted': True,
            'template_info': template_info
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting template: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

