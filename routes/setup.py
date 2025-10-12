"""
Setup and database initialization routes
"""
from flask import Blueprint, jsonify, request
from app import db, Template, User, Download, Favorite, TemplateRating
from sqlalchemy import inspect
import os

setup_bp = Blueprint('setup', __name__, url_prefix='/setup')

@setup_bp.route('/init-database', methods=['GET', 'POST'])
def init_database():
    """Initialize database tables - requires secret key"""
    # Check for secret key
    secret = request.args.get('secret') or request.form.get('secret')
    expected_secret = os.getenv('SETUP_SECRET_KEY', 'pmb_setup_2024')
    
    if secret != expected_secret:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing secret key'
        }), 403
    
    try:
        # Create all tables
        db.create_all()
        
        # Get list of created tables
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Get counts
        user_count = User.query.count()
        template_count = Template.query.count()
        
        return jsonify({
            'success': True,
            'message': 'Database initialized successfully',
            'tables': tables,
            'counts': {
                'users': user_count,
                'templates': template_count
            }
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@setup_bp.route('/check-database', methods=['GET'])
def check_database():
    """Check database status"""
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        counts = {}
        if 'user' in tables:
            counts['users'] = User.query.count()
        if 'template' in tables:
            counts['templates'] = Template.query.count()
        if 'download' in tables:
            counts['downloads'] = Download.query.count()
        if 'favorite' in tables:
            counts['favorites'] = Favorite.query.count()
        if 'template_rating' in tables:
            counts['ratings'] = TemplateRating.query.count()
        
        return jsonify({
            'success': True,
            'tables': tables,
            'counts': counts
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500



@setup_bp.route('/populate-templates', methods=['GET', 'POST'])
def populate_templates():
    """Populate database with templates from JSON file - requires secret key"""
    # Check for secret key
    secret = request.args.get('secret') or request.form.get('secret')
    expected_secret = os.getenv('SETUP_SECRET_KEY', 'pmb_setup_2024')
    
    if secret != expected_secret:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing secret key'
        }), 403
    
    try:
        import json
        from pathlib import Path
        from sqlalchemy.exc import IntegrityError
        
        # Load templates from JSON
        json_path = Path(__file__).parent.parent / 'templates_catalog.json'
        
        if not json_path.exists():
            return jsonify({
                'success': False,
                'error': f'Template catalog not found at {json_path}'
            }), 404
        
        with open(json_path, 'r') as f:
            templates_data = json.load(f)
        
        # Check if we should clear existing data
        clear_existing = request.args.get('clear', 'false').lower() == 'true'
        existing_count = Template.query.count()
        
        if existing_count > 0 and clear_existing:
            Template.query.delete()
            db.session.commit()
        elif existing_count > 0 and not clear_existing:
            return jsonify({
                'success': False,
                'error': f'Database already contains {existing_count} templates. Use ?clear=true to reimport'
            }), 400
        
        # Import templates
        imported = 0
        skipped = 0
        errors = []
        
        for template_data in templates_data:
            try:
                # Create template object
                template = Template(
                    id=template_data.get("id"),
                    name=template_data.get("name"),
                    filename=template_data.get("filename"),
                    industry=template_data.get("industry"),
                    category=template_data.get("category"),
                    file_type=template_data.get("file_type", "xlsx"),
                    description=template_data.get("description", ""),
                    downloads=template_data.get("downloads", 0),
                    rating=template_data.get("rating", 4.5),
                    tags=",".join(template_data.get("tags", [])),
                    file_size=template_data.get("file_size"),
                    has_formulas=template_data.get("has_formulas", False),
                    has_fields=template_data.get("has_fields", False),
                    is_premium=template_data.get("is_premium", False),
                )
                db.session.add(template)
                imported += 1
                
                # Commit in batches of 100
                if imported % 100 == 0:
                    db.session.commit()
                    
            except IntegrityError as e:
                db.session.rollback()
                skipped += 1
                errors.append(f"Template {template_data.get('id')}: Duplicate")
            except Exception as e:
                db.session.rollback()
                skipped += 1
                errors.append(f"Template {template_data.get('id')}: {str(e)}")
        
        # Final commit
        db.session.commit()
        
        # Get statistics
        total_count = Template.query.count()
        industries_count = db.session.query(Template.industry).distinct().count()
        categories_count = db.session.query(Template.category).distinct().count()
        
        return jsonify({
            'success': True,
            'message': 'Templates imported successfully',
            'imported': imported,
            'skipped': skipped,
            'total_in_database': total_count,
            'statistics': {
                'industries': industries_count,
                'categories': categories_count,
                'templates': total_count
            },
            'errors': errors[:10] if errors else []  # Return first 10 errors only
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

