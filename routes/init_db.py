"""
Database Initialization Route for Railway
Accessible via /admin/init-database endpoint
"""

from flask import Blueprint, jsonify, request, render_template
import json
import os
from datetime import datetime

init_db_bp = Blueprint('init_db', __name__)

@init_db_bp.route('/admin/init-database', methods=['POST'])
def initialize_database():
    """Initialize database tables and import templates"""
    
    # Security check - require a secret key
    secret = request.headers.get('X-Init-Secret')
    expected_secret = os.getenv('INIT_SECRET', 'pmb-init-2025')
    
    if secret != expected_secret:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from app import db, Template
        
        # Create all tables
        db.create_all()
        
        # Check if templates already exist
        existing_count = Template.query.count()
        if existing_count > 0:
            return jsonify({
                'status': 'already_initialized',
                'message': f'Database already contains {existing_count} templates',
                'templates_count': existing_count
            })
        
        # Load templates from catalog
        catalog_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates_catalog.json')
        with open(catalog_path, 'r') as f:
            templates = json.load(f)
        
        # Import templates
        imported = 0
        for template_data in templates:
            template = Template(
                name=template_data.get('name', ''),
                description=template_data.get('description', ''),
                industry=template_data.get('industry', ''),
                category=template_data.get('category', ''),
                file_type=template_data.get('file_type', ''),
                filename=template_data.get('filename', ''),
                file_path=f"/templates/{template_data.get('filename', '')}" if template_data.get('filename') else None,
                downloads=0,
                rating=4.5,
                tags=','.join(template_data.get('tags', [])) if template_data.get('tags') else '',
                file_size=template_data.get('file_size', 0),
                has_formulas=template_data.get('has_formulas', False),
                has_fields=template_data.get('has_fields', False),
                is_premium=False,
                created_at=datetime.utcnow()
            )
            db.session.add(template)
            imported += 1
            
            # Commit in batches of 100
            if imported % 100 == 0:
                db.session.commit()
        
        # Final commit
        db.session.commit()
        
        # Verify
        final_count = Template.query.count()
        
        return jsonify({
            'status': 'success',
            'message': 'Database initialized successfully',
            'templates_imported': imported,
            'templates_count': final_count,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@init_db_bp.route('/admin/db-status', methods=['GET'])
def database_status():
    """Check database status"""
    try:
        from app import db, Template, User, Download
        
        template_count = Template.query.count()
        user_count = User.query.count()
        download_count = Download.query.count()
        
        # Get sample templates
        sample_templates = Template.query.limit(5).all()
        
        return jsonify({
            'status': 'connected',
            'templates_count': template_count,
            'users_count': user_count,
            'downloads_count': download_count,
            'sample_templates': [
                {
                    'id': t.id,
                    'name': t.name,
                    'industry': t.industry,
                    'category': t.category,
                    'file_type': t.file_type
                }
                for t in sample_templates
            ],
            'database_url': os.getenv('DATABASE_URL', '').split('@')[1] if '@' in os.getenv('DATABASE_URL', '') else 'not set'
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500



@init_db_bp.route('/admin/fix-industry-names', methods=['POST'])
def fix_industry_names():
    """Fix incomplete industry names in database"""
    
    # Security check
    secret = request.headers.get('X-Init-Secret')
    expected_secret = os.getenv('INIT_SECRET', 'pmb-init-2025')
    
    if secret != expected_secret:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Industry name corrections
    INDUSTRY_CORRECTIONS = {
        "Business": "Business Process Improvement",
        "Cloud": "Cloud Migration",
        "Customer": "Customer Experience",
        "Data": "Data Analytics",
        "Digital": "Digital Transformation",
        "Hardware": "Hardware Implementation",
        "Media": "Media & Entertainment",
        "Merger": "Merger & Acquisition",
        "Network": "Network Infrastructure",
        "Operational": "Operational Excellence",
        "Operations": "Operations Management",
        "Product": "Product Development",
        "Research": "Research & Development"
    }
    
    try:
        from app import db
        
        results = {
            'industries_updated': 0,
            'changes': []
        }
        
        # Fix industry names using raw SQL
        for old_name, new_name in INDUSTRY_CORRECTIONS.items():
            result = db.session.execute(
                db.text("UPDATE template SET industry = :new WHERE industry = :old"),
                {"new": new_name, "old": old_name}
            )
            count = result.rowcount
            if count > 0:
                results['industries_updated'] += count
                results['changes'].append({
                    'from': old_name,
                    'to': new_name,
                    'count': count
                })
        
        db.session.commit()
        
        # Get updated industry list
        result = db.session.execute(db.text("SELECT DISTINCT industry FROM template ORDER BY industry"))
        industries = [row[0] for row in result]
        
        return jsonify({
            'status': 'success',
            'message': f'Updated {results["industries_updated"]} templates',
            'results': results,
            'current_industries': industries
        })
        
    except Exception as e:
        import traceback
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500




@init_db_bp.route('/admin/fix-names-page', methods=['GET'])
def fix_names_page():
    """Admin page to fix template and industry names"""
    return render_template('admin/fix_names.html')

