"""
Fix Database Names Route
Applies SQL fixes to correct template and industry names
"""

from flask import Blueprint, jsonify, request
import os

fix_database_names_bp = Blueprint('fix_database_names', __name__)

@fix_database_names_bp.route('/admin/fix-all-names', methods=['POST'])
def fix_all_names():
    """Fix all incorrect template and industry names in the database"""
    
    # Security check
    secret = request.headers.get('X-Init-Secret')
    expected_secret = os.getenv('INIT_SECRET', 'pmb-init-2025')
    
    if secret != expected_secret:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from app import db, Template
        
        # Industry name fixes
        industry_fixes = {
            "Hardware Development": "Hardware Implementation",
            "Operational Excellence": "Operational Improvement",
            "Operations Management": "Operational Improvement",
            "R&D": "Research & Development",
            "ERP": "ERP Implementation",
            "Media": "Media & Entertainment",
            "Merger and Acquisition": "Merger & Acquisition"
        }
        
        # Template name fixes
        template_fixes = {
            "WBS": "Project Plan",
            "Planning": "Project Plan",
            "Project Planning": "Project Plan"
        }
        
        industries_updated = 0
        templates_updated = 0
        
        # Fix industry names
        for old_name, new_name in industry_fixes.items():
            count = Template.query.filter_by(industry=old_name).update({'industry': new_name})
            industries_updated += count
        
        # Fix template names
        for old_name, new_name in template_fixes.items():
            count = Template.query.filter_by(name=old_name).update({'name': new_name})
            templates_updated += count
        
        # Commit changes
        db.session.commit()
        
        # Get updated stats
        total_templates = Template.query.count()
        unique_industries = db.session.query(Template.industry).distinct().count()
        unique_templates = db.session.query(Template.name).distinct().count()
        
        return jsonify({
            'status': 'success',
            'industries_updated': industries_updated,
            'templates_updated': templates_updated,
            'total_templates': total_templates,
            'unique_industries': unique_industries,
            'unique_template_types': unique_templates,
            'industry_fixes_applied': list(industry_fixes.keys()),
            'template_fixes_applied': list(template_fixes.keys())
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

