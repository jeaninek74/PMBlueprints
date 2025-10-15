"""
Admin route to update all templates with thumbnail URLs
Run once after deploying thumbnails
"""
from flask import Blueprint, jsonify
from app import db
import os

update_thumbnails_bp = Blueprint('update_thumbnails', __name__)

@update_thumbnails_bp.route('/admin/update-thumbnails', methods=['GET'])
def update_all_thumbnails():
    """Update all templates with thumbnail URLs"""
    try:
        # Import Template model
        from models import Template
        
        # Get all templates
        templates = Template.query.all()
        
        updated = 0
        not_found = 0
        results = []
        
        for template in templates:
            # Generate thumbnail filename
            base_name = os.path.splitext(template.filename)[0]
            thumb_filename = f"{base_name}.png"
            thumb_url = f"/static/thumbnails/{thumb_filename}"
            
            # Check if thumbnail file exists
            thumb_path = os.path.join('static', 'thumbnails', thumb_filename)
            
            if os.path.exists(thumb_path):
                # Update template
                template.thumbnail = thumb_url
                updated += 1
            else:
                not_found += 1
                if len(results) < 10:
                    results.append(f"Missing: {thumb_filename}")
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated': updated,
            'not_found': not_found,
            'total': len(templates),
            'missing_files': results
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

