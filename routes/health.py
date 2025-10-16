"""
Health Check Routes
Provides system health and diagnostics endpoints
"""

from flask import Blueprint, jsonify
import logging
import os

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'PMBlueprints',
        'version': '1.0.0'
    })

@health_bp.route('/health/database')
def database_health():
    """Database connection health check"""
    try:
        from database import db, Template
        
        # Test database connection
        template_count = Template.query.count()
        
        # Get sample template
        sample_template = Template.query.first()
        
        # Get database info
        db_url = os.environ.get('DATABASE_URL', 'Not set')
        # Mask password in URL for security
        if '@' in db_url:
            parts = db_url.split('@')
            user_pass = parts[0].split('//')[-1]
            if ':' in user_pass:
                user = user_pass.split(':')[0]
                db_url_masked = db_url.replace(user_pass, f"{user}:****")
            else:
                db_url_masked = db_url
        else:
            db_url_masked = db_url
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'template_count': template_count,
            'sample_template': {
                'id': sample_template.id if sample_template else None,
                'name': sample_template.name if sample_template else None,
                'industry': sample_template.industry if sample_template else None,
                'category': sample_template.category if sample_template else None
            } if sample_template else None,
            'database_url': db_url_masked
        })
    
    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'error_type': type(e).__name__,
            'database_url': os.environ.get('DATABASE_URL', 'Not set')[:50] + '...' if os.environ.get('DATABASE_URL') else 'Not set'
        }), 500

@health_bp.route('/health/detailed')
def detailed_health():
    """Detailed system health check"""
    try:
        from database import db, Template, User
        
        # Database checks
        template_count = Template.query.count()
        user_count = User.query.count()
        
        # Get database statistics
        industries = db.session.query(Template.industry).distinct().count()
        categories = db.session.query(Template.category).distinct().count()
        
        return jsonify({
            'status': 'healthy',
            'database': {
                'status': 'connected',
                'templates': template_count,
                'users': user_count,
                'industries': industries,
                'categories': categories
            },
            'environment': {
                'database_configured': bool(os.environ.get('DATABASE_URL')),
                'supabase_configured': bool(os.environ.get('SUPABASE_URL')),
                'openai_configured': bool(os.environ.get('OPENAI_API_KEY')),
                'stripe_configured': bool(os.environ.get('STRIPE_SECRET_KEY'))
            }
        })
    
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}", exc_info=True)
        
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

