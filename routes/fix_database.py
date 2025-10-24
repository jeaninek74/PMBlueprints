"""
Database Fix Route - Clean up NULL values in production database
"""
from flask import Blueprint, jsonify
from database import db
from models import Template
import logging

logger = logging.getLogger(__name__)

fix_database_bp = Blueprint('fix_database', __name__)

@fix_database_bp.route('/admin/fix-database', methods=['GET'])
def fix_database():
    """
    Admin endpoint to fix NULL values in database
    Sets all NULL file_format values to 'xlsx'
    """
    try:
        # Count and fix NULL file_format
        null_formats = Template.query.filter(Template.file_format == None).count()
        
        if null_formats > 0:
            Template.query.filter(Template.file_format == None).update(
                {'file_format': 'xlsx'},
                synchronize_session=False
            )
            db.session.commit()
            logger.info(f"Fixed {null_formats} templates with NULL file_format")
        
        # Count and fix empty file_format
        empty_formats = Template.query.filter(Template.file_format == '').count()
        
        if empty_formats > 0:
            Template.query.filter(Template.file_format == '').update(
                {'file_format': 'xlsx'},
                synchronize_session=False
            )
            db.session.commit()
            logger.info(f"Fixed {empty_formats} templates with empty file_format")
        
        # Verify all templates now have file_format
        total_templates = Template.query.count()
        templates_with_format = Template.query.filter(Template.file_format != None, Template.file_format != '').count()
        
        return jsonify({
            'success': True,
            'fixed_null': null_formats,
            'fixed_empty': empty_formats,
            'total_templates': total_templates,
            'templates_with_format': templates_with_format,
            'message': f'Database cleaned: {null_formats + empty_formats} templates fixed'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database fix failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

