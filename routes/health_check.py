"""
Health Check Endpoint
Validates critical system functionality and subscription permissions
"""
from flask import Blueprint, jsonify
from models import db, User, Template
from utils.subscription_security import get_user_tier_limits, check_feature_access
import logging

health_check_bp = Blueprint('health_check', __name__)
logger = logging.getLogger(__name__)

@health_check_bp.route('/api/health-check', methods=['GET'])
def health_check():
    """
    Comprehensive health check endpoint
    Returns status of critical system components
    """
    results = {
        'status': 'healthy',
        'checks': {}
    }
    
    try:
        # Check 1: Database connectivity
        try:
            template_count = Template.query.count()
            results['checks']['database'] = {
                'status': 'ok',
                'template_count': template_count
            }
        except Exception as e:
            results['checks']['database'] = {
                'status': 'error',
                'error': str(e)
            }
            results['status'] = 'unhealthy'
        
        # Check 2: Test users exist with correct tiers
        test_users = {
            'free@pmblueprints.com': 'free',
            'individual@pmblueprints.com': 'individual',
            'professional@pmblueprints.com': 'professional',
            'enterprise@pmblueprints.com': 'enterprise'
        }
        
        user_check = {'status': 'ok', 'users': {}}
        for email, expected_tier in test_users.items():
            user = User.query.filter_by(email=email).first()
            if user:
                tier_correct = user.subscription_tier == expected_tier
                user_check['users'][email] = {
                    'exists': True,
                    'tier': user.subscription_tier,
                    'expected_tier': expected_tier,
                    'tier_correct': tier_correct
                }
                if not tier_correct:
                    user_check['status'] = 'warning'
            else:
                user_check['users'][email] = {
                    'exists': False,
                    'expected_tier': expected_tier
                }
                user_check['status'] = 'error'
                results['status'] = 'unhealthy'
        
        results['checks']['test_users'] = user_check
        
        # Check 3: Subscription tier permissions
        from utils.subscription_security import TIER_LIMITS
        tier_permissions = {}
        for tier in ['free', 'individual', 'professional', 'enterprise']:
            limits = TIER_LIMITS.get(tier, {})
            tier_permissions[tier] = {
                'platform_integrations': limits.get('platform_integrations', False),
                'ai_generator': limits.get('ai_generator', False),
                'ai_suggestor': limits.get('ai_suggestor', False)
            }
        
        results['checks']['tier_permissions'] = {
            'status': 'ok',
            'tiers': tier_permissions
        }
        
        # Verify enterprise has platform integrations
        if not tier_permissions['enterprise']['platform_integrations']:
            results['checks']['tier_permissions']['status'] = 'error'
            results['checks']['tier_permissions']['error'] = 'Enterprise tier does not have platform_integrations access'
            results['status'] = 'unhealthy'
        
        # Check 4: Critical routes accessibility (basic check)
        results['checks']['routes'] = {
            'status': 'ok',
            'note': 'Route registration successful (app is running)'
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        results['status'] = 'error'
        results['error'] = str(e)
    
    # Return appropriate HTTP status code
    status_code = 200 if results['status'] == 'healthy' else 503
    
    return jsonify(results), status_code

@health_check_bp.route('/api/health', methods=['GET'])
def simple_health():
    """Simple health check - just returns OK if app is running"""
    return jsonify({'status': 'ok'}), 200

