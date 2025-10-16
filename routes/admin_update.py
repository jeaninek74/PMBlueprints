"""
Admin API for Template Updates
===============================

Temporary endpoint to update template names and descriptions
"""

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin_update', __name__, url_prefix='/api/admin')

@admin_bp.route('/update-templates', methods=['POST'])
def update_templates():
    """Update all template names and descriptions from catalog"""
    try:
        from database import db, Template
        
        data = request.get_json()
        
        if not data or 'templates' not in data:
            return jsonify({'success': False, 'error': 'No template data provided'}), 400
        
        templates = data['templates']
        rename_category = data.get('rename_category', {})
        
        updated_count = 0
        renamed_count = 0
        
        # Update each template
        for template_data in templates:
            filename = template_data['filename']
            name = template_data['name']
            description = template_data['description']
            category = template_data['category']
            
            template = Template.query.filter_by(filename=filename).first()
            
            if template:
                template.name = name
                template.description = description
                template.category = category
                updated_count += 1
        
        # Rename category if specified
        if rename_category:
            from_cat = rename_category.get('from')
            to_cat = rename_category.get('to')
            
            if from_cat and to_cat:
                templates_to_rename = Template.query.filter_by(category=from_cat).all()
                for template in templates_to_rename:
                    template.category = to_cat
                    renamed_count += 1
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"Updated {updated_count} templates, renamed {renamed_count} categories")
        
        return jsonify({
            'success': True,
            'updated': updated_count,
            'renamed': renamed_count,
            'message': f'Successfully updated {updated_count} templates'
        })
    
    except Exception as e:
        logger.error(f"Template update error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

