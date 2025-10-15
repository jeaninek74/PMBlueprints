"""
Admin route to update template thumbnails
Safe standalone route that can be enabled/disabled easily
"""
from flask import Blueprint, jsonify
import os
import logging

logger = logging.getLogger(__name__)

admin_thumbnails_bp = Blueprint('admin_thumbnails', __name__)

@admin_thumbnails_bp.route('/admin/update-thumbnails-now', methods=['GET'])
def update_thumbnails_now():
    """Update all templates with thumbnail URLs - safe version"""
    try:
        # Import models here to avoid circular imports
        from app import db, Template
        
        logger.info("Starting thumbnail update process")
        
        # Get all templates
        templates = Template.query.all()
        total = len(templates)
        
        updated = 0
        skipped = 0
        errors = []
        
        for template in templates:
            try:
                # Generate thumbnail filename from template filename
                if template.filename:
                    base_name = os.path.splitext(template.filename)[0]
                    thumb_filename = f"{base_name}.png"
                    thumb_url = f"/static/thumbnails/{thumb_filename}"
                    
                    # Update the template (use preview_image field)
                    template.preview_image = thumb_url
                    updated += 1
                    
                    if updated % 100 == 0:
                        logger.info(f"Updated {updated} templates so far...")
                else:
                    skipped += 1
                    
            except Exception as e:
                errors.append(f"Template {template.id}: {str(e)}")
                logger.error(f"Error updating template {template.id}: {e}")
        
        # Commit all changes at once
        db.session.commit()
        logger.info(f"Thumbnail update complete. Updated: {updated}, Skipped: {skipped}")
        
        return jsonify({
            'success': True,
            'message': 'Thumbnails updated successfully',
            'total_templates': total,
            'updated': updated,
            'skipped': skipped,
            'errors': errors[:10]  # Show first 10 errors if any
        })
        
    except Exception as e:
        logger.error(f"Critical error in thumbnail update: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

