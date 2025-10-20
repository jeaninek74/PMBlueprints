"""
Subscription Tier Security
Enforces access control based on user's subscription tier
"""

from functools import wraps
from flask import flash, redirect, url_for, jsonify, request
from flask_login import current_user
from datetime import datetime, timedelta

# Subscription tier limits
TIER_LIMITS = {
    'free': {
        'downloads_per_month': 0,
        'ai_generations_per_month': 1,
        'ai_suggestions_per_month': 1,
        'ai_suggestions_access': True,
        'platform_integrations': False,
        'custom_templates': False,
        'advanced_analytics': False,
        'priority_support': False,
        'can_download_ai_generated': False,  # View only, no download
        'template_access': 'all'
    },
    'individual': {
        'downloads_per_month': 1,  # 1 download per $50 purchase
        'ai_generations_per_month': 0,
        'ai_suggestions_per_month': 0,
        'ai_suggestions_access': False,
        'platform_integrations': False,
        'custom_templates': False,
        'advanced_analytics': False,
        'priority_support': False,
        'can_download_ai_generated': False,
        'is_one_time_purchase': True,
        'template_access': 'all'
    },
    'professional': {
        'downloads_per_month': 2,
        'ai_generations_per_month': 6,
        'ai_suggestions_per_month': 4,
        'ai_suggestions_access': True,
        'platform_integrations': False,
        'custom_templates': False,
        'advanced_analytics': False,
        'priority_support': False,
        'can_download_ai_generated': True,
        'template_access': 'all'
    },
    'enterprise': {
        'downloads_per_month': 2,
        'ai_generations_per_month': 6,
        'ai_suggestions_per_month': 4,
        'ai_suggestions_access': True,
        'platform_integrations': True,
        'custom_templates': False,
        'advanced_analytics': False,
        'priority_support': True,
        'can_download_ai_generated': True,
        'template_access': 'all'
    }
}


def get_user_tier_limits(user):
    """Get limits for user's subscription tier"""
    if user is None:
        return TIER_LIMITS['free']
    tier = user.subscription_tier or 'free'
    return TIER_LIMITS.get(tier, TIER_LIMITS['free'])


def check_download_limit(user):
    """Check if user has exceeded download limit for current month"""
    from database import db
    from models import DownloadHistory
    
    limits = get_user_tier_limits(user)
    max_downloads = limits['downloads_per_month']
    
    # Unlimited for enterprise
    if max_downloads == float('inf'):
        return True, 0
    
    # Count downloads this month
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    downloads_this_month = DownloadHistory.query.filter(
        DownloadHistory.user_id == user.id,
        DownloadHistory.download_date >= first_day_of_month
    ).count()
    
    remaining = max_downloads - downloads_this_month
    
    return downloads_this_month < max_downloads, remaining


def check_ai_generation_limit(user):
    """Check if user has exceeded AI generation limit for current month"""
    from database import db
    from models import AIGeneratorHistory, AISuggestionHistory
    
    limits = get_user_tier_limits(user)
    max_generations = limits['ai_generations_per_month']
    
    # If no user (not logged in), use free tier limits
    if user is None:
        return {'allowed': max_generations > 0, 'remaining': max_generations, 'limit': max_generations, 'error': 'Please log in to use AI Generator' if max_generations == 0 else None}
    
    # Count AI generations this month
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    generator_count = AIGeneratorHistory.query.filter(
        AIGeneratorHistory.user_id == user.id,
        AIGeneratorHistory.created_at >= first_day_of_month
    ).count()
    
    suggestion_count = AISuggestionHistory.query.filter(
        AISuggestionHistory.user_id == user.id,
        AISuggestionHistory.created_at >= first_day_of_month
    ).count()
    
    total_generations = generator_count + suggestion_count
    remaining = max_generations - total_generations
    allowed = total_generations < max_generations
    
    return {'allowed': allowed, 'remaining': remaining, 'limit': max_generations, 'error': 'Monthly limit reached' if not allowed else None}


def check_usage_limit(user, usage_type):
    """
    Universal usage limit checker
    
    Args:
        user: User object
        usage_type: 'downloads', 'ai_generations', or 'ai_suggestions'
    
    Returns:
        tuple: (can_use: bool, remaining: int, limit: int)
    """
    from database import db
    from models import DownloadHistory, AIGeneratorHistory, AISuggestionHistory
    
    limits = get_user_tier_limits(user)
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if usage_type == 'downloads':
        limit = limits['downloads_per_month']
        used = DownloadHistory.query.filter(
            DownloadHistory.user_id == user.id,
            DownloadHistory.download_date >= first_day_of_month
        ).count()
        
    elif usage_type == 'ai_generations':
        limit = limits['ai_generations_per_month']
        used = AIGeneratorHistory.query.filter(
            AIGeneratorHistory.user_id == user.id,
            AIGeneratorHistory.created_at >= first_day_of_month
        ).count()
        
    elif usage_type == 'ai_suggestions':
        limit = limits.get('ai_suggestions_per_month', 0)
        used = AISuggestionHistory.query.filter(
            AISuggestionHistory.user_id == user.id,
            AISuggestionHistory.created_at >= first_day_of_month
        ).count()
    else:
        return False, 0, 0
    
    remaining = limit - used
    can_use = used < limit
    
    return can_use, remaining, limit


def track_usage(user, usage_type, **kwargs):
    """
    Track usage for billing and quota enforcement
    
    Args:
        user: User object
        usage_type: 'download', 'ai_generation', 'ai_suggestion'
        **kwargs: Additional data to store
    """
    from database import db
    from models import DownloadHistory, AIGeneratorHistory, AISuggestionHistory
    
    try:
        if usage_type == 'download':
            record = DownloadHistory(
                user_id=user.id,
                template_id=kwargs.get('template_id'),
                download_date=datetime.utcnow()
            )
            db.session.add(record)
            
        elif usage_type == 'ai_generation':
            record = AIGeneratorHistory(
                user_id=user.id,
                document_type=kwargs.get('document_type'),
                content=kwargs.get('content'),
                created_at=datetime.utcnow()
            )
            db.session.add(record)
            
        elif usage_type == 'ai_suggestion':
            record = AISuggestionHistory(
                user_id=user.id,
                query=kwargs.get('query'),
                suggestions=kwargs.get('suggestions'),
                created_at=datetime.utcnow()
            )
            db.session.add(record)
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error tracking usage: {e}")
        return False


def check_feature_access(user, feature):
    """Check if user has access to a specific feature"""
    limits = get_user_tier_limits(user)
    return limits.get(feature, False)


# Decorators for route protection

def require_tier(min_tier):
    """Decorator to require minimum subscription tier"""
    tier_hierarchy = {'free': 0, 'individual': 1, 'professional': 2, 'enterprise': 3}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this feature', 'warning')
                return redirect(url_for('auth.login'))
            
            user_tier_level = tier_hierarchy.get(current_user.subscription_tier or 'free', 0)
            required_tier_level = tier_hierarchy.get(min_tier, 0)
            
            if user_tier_level < required_tier_level:
                if request.is_json:
                    return jsonify({
                        'error': f'This feature requires {min_tier.title()} plan or higher',
                        'upgrade_url': url_for('pricing')
                    }), 403
                else:
                    flash(f'This feature requires {min_tier.title()} plan or higher. Please upgrade.', 'warning')
                    return redirect(url_for('pricing'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_download_quota(f):
    """Decorator to check download quota before allowing download"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to download templates', 'warning')
            return redirect(url_for('auth.login'))
        
        can_download, remaining = check_download_limit(current_user)
        
        if not can_download:
            if request.is_json:
                return jsonify({
                    'error': 'Download limit exceeded for this month',
                    'upgrade_url': url_for('pricing')
                }), 403
            else:
                flash('You have reached your download limit for this month. Please upgrade your plan.', 'warning')
                return redirect(url_for('pricing'))
        
        return f(*args, **kwargs)
    return decorated_function


def check_ai_quota(f):
    """Decorator to check AI generation quota before allowing generation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Please log in to use AI features'}), 401
        
        limit_result = check_ai_generation_limit(current_user)
        
        if not limit_result['allowed']:
            return jsonify({
                'error': 'AI generation limit exceeded for this month',
                'remaining': 0,
                'upgrade_url': url_for('pricing')
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def require_feature(feature_name):
    """Decorator to require specific feature access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this feature', 'warning')
                return redirect(url_for('auth.login'))
            
            if not check_feature_access(current_user, feature_name):
                if request.is_json:
                    return jsonify({
                        'error': f'This feature is not available in your current plan',
                        'upgrade_url': url_for('pricing')
                    }), 403
                else:
                    flash('This feature is not available in your current plan. Please upgrade.', 'warning')
                    return redirect(url_for('pricing'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_usage_stats(user):
    """Get current usage statistics for user"""
    from database import db
    from models import DownloadHistory, AIGeneratorHistory, AISuggestionHistory
    
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Downloads
    downloads_this_month = DownloadHistory.query.filter(
        DownloadHistory.user_id == user.id,
        DownloadHistory.download_date >= first_day_of_month
    ).count()
    
    # AI Generations
    generator_count = AIGeneratorHistory.query.filter(
        AIGeneratorHistory.user_id == user.id,
        AIGeneratorHistory.created_at >= first_day_of_month
    ).count()
    
    suggestion_count = AISuggestionHistory.query.filter(
        AISuggestionHistory.user_id == user.id,
        AISuggestionHistory.created_at >= first_day_of_month
    ).count()
    
    ai_generations_this_month = generator_count + suggestion_count
    
    # Get limits
    limits = get_user_tier_limits(user)
    
    return {
        'downloads': {
            'used': downloads_this_month,
            'limit': limits['downloads_per_month'],
            'remaining': limits['downloads_per_month'] - downloads_this_month if limits['downloads_per_month'] != float('inf') else 'Unlimited'
        },
        'ai_generations': {
            'used': ai_generations_this_month,
            'limit': limits['ai_generations_per_month'],
            'remaining': limits['ai_generations_per_month'] - ai_generations_this_month
        },
        'features': {
            'platform_integrations': limits['platform_integrations'],
            'custom_templates': limits['custom_templates'],
            'advanced_analytics': limits['advanced_analytics'],
            'priority_support': limits['priority_support']
        }
    }


def requires_platform_integrations(f):
    """
    Decorator to require platform integrations feature access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        if not current_user.is_authenticated:
            logger.warning("User not authenticated")
            return redirect(url_for('login'))
        
        # Debug logging
        logger.info(f"Checking platform integrations for user: {current_user.email}")
        logger.info(f"User subscription tier: {current_user.subscription_tier}")
        
        # Check if user has platform integrations access
        has_access = check_feature_access(current_user, 'platform_integrations')
        logger.info(f"Platform integrations access: {has_access}")
        
        if not has_access:
            logger.warning(f"Access denied for user {current_user.email} with tier {current_user.subscription_tier}")
            flash('Platform integrations require a Professional or Enterprise subscription.', 'warning')
            return redirect(url_for('pricing'))
        
        logger.info(f"Access granted for user {current_user.email}")
        return f(*args, **kwargs)
    return decorated_function

