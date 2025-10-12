"""
Update template industries without deleting data
"""
from flask import Blueprint, jsonify, request
from app import db, Template
import os
import json
from pathlib import Path

update_industries_bp = Blueprint('update_industries', __name__)

@update_industries_bp.route('/api/admin/update-industries', methods=['GET', 'POST'])
def update_industries():
    """Update template industries from catalog without deleting data"""
    # Check for secret key
    secret = request.args.get('secret') or request.form.get('secret')
    expected_secret = os.getenv('SETUP_SECRET_KEY', 'pmb_setup_2024')
    
    if secret != expected_secret:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing secret key'
        }), 403
    
    try:
        # Load templates from JSON
        json_path = Path(__file__).parent.parent / 'templates_catalog.json'
        
        if not json_path.exists():
            return jsonify({
                'success': False,
                'error': f'Template catalog not found'
            }), 404
        
        with open(json_path, 'r') as f:
            catalog_data = json.load(f)
        
        # Create a mapping of filename to industry
        filename_to_data = {}
        for template in catalog_data:
            filename = template.get('filename')
            if filename:
                filename_to_data[filename] = {
                    'industry': template.get('industry'),
                    'category': template.get('category'),
                    'name': template.get('name'),
                    'description': template.get('description', '')
                }
        
        # Update existing templates
        updated = 0
        added = 0
        skipped = 0
        
        # First, update existing templates
        existing_templates = Template.query.all()
        existing_filenames = set()
        
        for template in existing_templates:
            existing_filenames.add(template.filename)
            if template.filename in filename_to_data:
                data = filename_to_data[template.filename]
                old_industry = template.industry
                template.industry = data['industry']
                template.category = data['category']
                template.name = data['name']
                template.description = data['description']
                updated += 1
                
                if updated % 100 == 0:
                    db.session.commit()
        
        # Add new templates that don't exist
        for template_data in catalog_data:
            filename = template_data.get('filename')
            if filename and filename not in existing_filenames:
                try:
                    new_template = Template(
                        name=template_data.get("name"),
                        filename=filename,
                        industry=template_data.get("industry"),
                        category=template_data.get("category"),
                        file_type=template_data.get("file_type", "xlsx"),
                        description=template_data.get("description", ""),
                        downloads=0,
                        rating=4.5,
                        tags=",".join(template_data.get("tags", [])),
                        file_size=template_data.get("file_size"),
                        has_formulas=template_data.get("has_formulas", False),
                        has_fields=template_data.get("has_fields", False),
                        is_premium=template_data.get("is_premium", False),
                    )
                    db.session.add(new_template)
                    added += 1
                    
                    if added % 100 == 0:
                        db.session.commit()
                except Exception as e:
                    skipped += 1
        
        # Final commit
        db.session.commit()
        
        # Get updated statistics
        total_count = Template.query.count()
        industries = db.session.query(Template.industry).distinct().all()
        industries_list = sorted([i[0] for i in industries if i[0]])
        industries_count = len(industries_list)
        categories_count = db.session.query(Template.category).distinct().count()
        
        return jsonify({
            'success': True,
            'message': 'Templates updated successfully',
            'updated': updated,
            'added': added,
            'skipped': skipped,
            'total_in_database': total_count,
            'statistics': {
                'industries': industries_count,
                'categories': categories_count,
                'templates': total_count
            },
            'industries_list': industries_list
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

