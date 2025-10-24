"""
Admin route to manage Product templates
"""
from flask import Blueprint, jsonify, request
from database import db
from models import Template
import logging

logger = logging.getLogger(__name__)

manage_product_bp = Blueprint('manage_product', __name__)

@manage_product_bp.route('/admin/product-templates/list', methods=['GET'])
def list_product_templates():
    """List all Product templates"""
    try:
        templates = Template.query.filter_by(industry='Product').all()
        
        template_list = []
        for t in templates:
            template_list.append({
                'id': t.id,
                'name': t.name,
                'category': t.category,
                'file_format': t.file_format,
                'file_path': t.file_path
            })
        
        return jsonify({
            'success': True,
            'count': len(template_list),
            'templates': template_list,
            'ids': [t.id for t in templates]
        })
        
    except Exception as e:
        logger.error(f"Error listing Product templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@manage_product_bp.route('/admin/product-templates/delete', methods=['POST'])
def delete_product_templates():
    """Delete all Product templates"""
    try:
        # Get all Product templates
        templates = Template.query.filter_by(industry='Product').all()
        count = len(templates)
        
        if count == 0:
            return jsonify({
                'success': True,
                'message': 'No Product templates found',
                'deleted': 0
            })
        
        # Store IDs before deletion
        deleted_ids = [t.id for t in templates]
        
        # Delete all Product templates
        Template.query.filter_by(industry='Product').delete()
        db.session.commit()
        
        logger.info(f"Deleted {count} Product templates: {deleted_ids}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {count} Product templates',
            'deleted': count,
            'deleted_ids': deleted_ids
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting Product templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

