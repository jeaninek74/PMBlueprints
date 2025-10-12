"""
Vercel serverless function to initialize the database
Call this endpoint once to create all tables: /api/init_db
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from flask import jsonify
from app import app, db, User, Template, Download, Favorite, TemplateRating

def handler(request, response):
    """Initialize database tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Check what tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Count templates
            template_count = Template.query.count()
            
            result = {
                'success': True,
                'message': 'Database initialized successfully',
                'tables_created': tables,
                'template_count': template_count
            }
            
            response.status_code = 200
            response.headers['Content-Type'] = 'application/json'
            return jsonify(result)
            
        except Exception as e:
            import traceback
            result = {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            response.status_code = 500
            response.headers['Content-Type'] = 'application/json'
            return jsonify(result)

