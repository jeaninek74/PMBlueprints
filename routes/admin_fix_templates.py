"""
Admin endpoint to fix missing template database records
"""

from flask import Blueprint, jsonify, request
import json
import os

admin_fix_bp = Blueprint('admin_fix', __name__, url_prefix='/api/admin')

@admin_fix_bp.route('/fix-missing-templates', methods=['POST'])
def fix_missing_templates():
    """
    Fix templates that exist in catalog but missing from database
    
    This endpoint:
    1. Loads templates_catalog.json
    2. Checks each template exists in database
    3. Creates missing database records
    4. Returns list of fixed templates
    """
    try:
        from app import db, Template
        
        # Load catalog
        catalog_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'templates_catalog.json'
        )
        
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
        
        fixed = []
        already_exist = []
        errors = []
        
        for template_data in catalog:
            template_id = template_data.get('id')
            filename = template_data['filename']
            
            # Skip if no ID
            if not template_id:
                continue
            
            # Check if exists
            existing = Template.query.filter_by(id=template_id).first()
            
            if existing:
                already_exist.append({
                    'id': template_id,
                    'name': template_data['name']
                })
            else:
                # Create new record
                try:
                    new_template = Template(
                        id=template_id,
                        name=template_data['name'],
                        filename=filename,
                        category=template_data['category'],
                        industry=template_data['industry'],
                        description=template_data.get('description', ''),
                        file_type=template_data.get('file_type', 'xlsx'),
                        is_premium=False,
                        downloads=0
                    )
                    
                    db.session.add(new_template)
                    db.session.commit()
                    
                    fixed.append({
                        'id': template_id,
                        'name': template_data['name'],
                        'filename': filename
                    })
                
                except Exception as e:
                    errors.append({
                        'id': template_id,
                        'name': template_data['name'],
                        'error': str(e)
                    })
        
        return jsonify({
            'success': True,
            'fixed_count': len(fixed),
            'already_exist_count': len(already_exist),
            'error_count': len(errors),
            'fixed': fixed[:10],  # Show first 10
            'errors': errors
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_fix_bp.route('/verify-all-templates', methods=['GET'])
def verify_all_templates():
    """
    Verify all templates in catalog have database records and files exist
    
    Returns:
    - missing_in_db: Templates in catalog but not in database
    - missing_files: Templates in database but files don't exist
    - all_good: Templates that are complete
    """
    try:
        from app import db, Template
        
        # Load catalog
        catalog_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'templates_catalog.json'
        )
        
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
        
        missing_in_db = []
        missing_files = []
        all_good = []
        
        for template_data in catalog:
            template_id = template_data.get('id')
            filename = template_data['filename']
            
            if not template_id:
                continue
            
            # Check database
            db_template = Template.query.filter_by(id=template_id).first()
            
            if not db_template:
                missing_in_db.append({
                    'id': template_id,
                    'name': template_data['name'],
                    'filename': filename
                })
                continue
            
            # Check file exists
            file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'static',
                'templates',
                filename
            )
            
            if not os.path.exists(file_path):
                missing_files.append({
                    'id': template_id,
                    'name': template_data['name'],
                    'filename': filename
                })
            else:
                all_good.append({
                    'id': template_id,
                    'name': template_data['name']
                })
        
        return jsonify({
            'success': True,
            'total_in_catalog': len(catalog),
            'missing_in_db': len(missing_in_db),
            'missing_files': len(missing_files),
            'all_good': len(all_good),
            'missing_in_db_list': missing_in_db,
            'missing_files_list': missing_files
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

