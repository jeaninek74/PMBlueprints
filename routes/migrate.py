"""
Database Migration Route
Provides HTTP endpoint to run database migrations
"""

from flask import Blueprint, jsonify
import logging
from sqlalchemy import text
from database import db

logger = logging.getLogger(__name__)

migrate_bp = Blueprint('migrate', __name__, url_prefix='/migrate')

@migrate_bp.route('/add-reset-token-fields')
def add_reset_token_fields():
    """Add reset_token and reset_token_expires columns to users table"""
    
    try:
        # Check if columns already exist
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name IN ('reset_token', 'reset_token_expires')
        """))
        existing_columns = [row[0] for row in result]
        
        if 'reset_token' in existing_columns and 'reset_token_expires' in existing_columns:
            return jsonify({
                'success': True,
                'message': 'Columns already exist. No migration needed.',
                'columns_added': []
            })
        
        columns_added = []
        
        # Add reset_token column if it doesn't exist
        if 'reset_token' not in existing_columns:
            logger.info("Adding reset_token column...")
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN reset_token VARCHAR(100)
            """))
            columns_added.append('reset_token')
            logger.info("reset_token column added")
        
        # Add reset_token_expires column if it doesn't exist
        if 'reset_token_expires' not in existing_columns:
            logger.info("Adding reset_token_expires column...")
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN reset_token_expires TIMESTAMP
            """))
            columns_added.append('reset_token_expires')
            logger.info("reset_token_expires column added")
        
        # Commit changes
        db.session.commit()
        logger.info("Migration completed successfully!")
        
        return jsonify({
            'success': True,
            'message': 'Migration completed successfully!',
            'columns_added': columns_added
        })
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@migrate_bp.route('/status')
def migration_status():
    """Check migration status"""
    
    try:
        # Check if columns exist
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name IN ('reset_token', 'reset_token_expires')
        """))
        existing_columns = [row[0] for row in result]
        
        return jsonify({
            'success': True,
            'reset_token_exists': 'reset_token' in existing_columns,
            'reset_token_expires_exists': 'reset_token_expires' in existing_columns,
            'migration_needed': len(existing_columns) < 2
        })
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

