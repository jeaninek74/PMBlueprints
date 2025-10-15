"""
Admin route to update all templates with thumbnail URLs
Run once after deploying thumbnails
"""
from flask import Blueprint, jsonify
from database import get_db_connection
import os

update_thumbnails_bp = Blueprint('update_thumbnails', __name__)

@update_thumbnails_bp.route('/admin/update-thumbnails', methods=['GET'])
def update_all_thumbnails():
    """Update all templates with thumbnail URLs"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get all templates
        cur.execute("SELECT id, filename FROM templates ORDER BY id")
        templates = cur.fetchall()
        
        updated = 0
        not_found = 0
        results = []
        
        for template_id, filename in templates:
            # Generate thumbnail filename
            base_name = os.path.splitext(filename)[0]
            thumb_filename = f"{base_name}.png"
            thumb_url = f"/static/thumbnails/{thumb_filename}"
            
            # Check if thumbnail file exists
            thumb_path = os.path.join('static', 'thumbnails', thumb_filename)
            
            if os.path.exists(thumb_path):
                # Update database
                cur.execute(
                    "UPDATE templates SET thumbnail = %s WHERE id = %s",
                    (thumb_url, template_id)
                )
                updated += 1
            else:
                not_found += 1
                results.append(f"Missing: {thumb_filename}")
        
        # Commit changes
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'updated': updated,
            'not_found': not_found,
            'total': len(templates),
            'missing_files': results[:10]  # Show first 10 missing
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

