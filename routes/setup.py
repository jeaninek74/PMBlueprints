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

