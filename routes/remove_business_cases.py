"""
API endpoint to remove Business Case templates from production database
"""

from flask import Blueprint, jsonify
from app import db
from models import Template
from pathlib import Path

remove_bc_bp = Blueprint('remove_bc', __name__)

@remove_bc_bp.route('/api/admin/remove-business-cases', methods=['POST'])
def remove_business_cases():
    """Remove all Business Case templates from database"""
    try:
        # Find all Business Case templates
        business_cases = Template.query.filter(Template.name == 'Business Case').all()
        
        removed = []
        for template in business_cases:
            removed.append({
                'id': template.id,
                'industry': template.industry,
                'file_path': template.file_path
            })
            db.session.delete(template)
        
        db.session.commit()
        
        # Get new counts
        total = Template.query.count()
        categories = db.session.query(Template.category).distinct().count()
        
        return jsonify({
            'success': True,
            'removed_count': len(removed),
            'removed_templates': removed,
            'new_total': total,
            'new_categories_count': categories
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

