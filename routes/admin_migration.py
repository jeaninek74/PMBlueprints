"""
Admin migration endpoint - ONE TIME USE ONLY
This endpoint runs database migrations and should be deleted after use
"""
from flask import Blueprint, jsonify
from database import db
import logging

logger = logging.getLogger(__name__)

admin_migration_bp = Blueprint('admin_migration', __name__, url_prefix='/admin')

@admin_migration_bp.route('/run-migration-2025-10-19', methods=['GET'])
def run_migration():
    """Run database migration to add missing columns"""
    try:
        # Check if columns already exist
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        migrations_needed = []
        migrations_completed = []
        
        # Check and add reset_token column
        if 'reset_token' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN reset_token VARCHAR(100)'))
            migrations_needed.append('reset_token')
            migrations_completed.append('Added reset_token column')
            logger.info("Added reset_token column to users table")
        else:
            logger.info("reset_token column already exists")
        
        # Check and add reset_token_expires column
        if 'reset_token_expires' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP'))
            migrations_needed.append('reset_token_expires')
            migrations_completed.append('Added reset_token_expires column')
            logger.info("Added reset_token_expires column to users table")
        else:
            logger.info("reset_token_expires column already exists")
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Database migration completed successfully',
            'migrations_completed': migrations_completed,
            'migrations_needed': migrations_needed,
            'note': 'Please delete this endpoint after use for security'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Migration failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Database migration failed'
        }), 500

