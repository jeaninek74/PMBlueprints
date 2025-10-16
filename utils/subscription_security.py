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
        'downloads_per_month': 0,  # Free users cannot download
        'ai_generations_per_month': 0,  # Free users cannot use AI
        'ai_suggestions_access': False,
        'platform_integrations': False,
        'custom_templates': False,
        'advanced_analytics': False,
        'priority_support': False
    },
    'individual': {
        'downloads_per_month': 1,  # One-time: 1 template download OR 1 AI generation
        'ai_generations_per_month': 1,  # Can use AI Generator for 1 template
        'ai_suggestions_access': False,  # No AI Suggestions
        'platform_integrations': False,
        'custom_templates': False,
        'advanced_analytics': False,
        'priority_support': False,
        'is_one_time_purchase': True  # Not a subscription
    },
    'professional': {
        'downloads_per_month': 2,
        'ai_suggestions_per_month': 4,
        'ai_generations_per_month': 6,
        'ai_suggestions_access': True,
        'platform_integrations': False,
        'custom_templates': False,
        'advanced_analytics': False,
        'priority_support': False
    },
    'enterprise': {
        'downloads_per_month': 2,
        'ai_suggestions_per_month': 4,
        'ai_generations_per_month': 6,
        'ai_suggestions_access': True,
        'platform_integrations': True,
        'custom_templates': False,
        'advanced_analytics': False,
        'priority_support': False
    }
}


def get_user_tier_limits(user):
    """Get limits for user's subscription tier"""
    tier = user.subscription_tier or 'free'
    return TIER_LIMITS.get(tier, TIER_LIMITS['free'])


def check_download_limit(user):
    """Check if user has exceeded download limit for current month"""
    from app import db, TemplateDownload
    
    limits = get_user_tier_limits(user)
    max_downloads = limits['downloads_per_month']
    
    # Unlimited for enterprise
    if max_downloads == float('inf'):
        return True, 0
    
    # Count downloads this month
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    downloads_this_month = TemplateDownload.query.filter(
        TemplateDownload.user_id == user.id,
        TemplateDownload.download_date >= first_day_of_month
    ).count()
    
    remaining = max_downloads - downloads_this_month
    
    return downloads_this_month < max_downloads, remaining


def check_ai_generation_limit(user):
    """Check if user has exceeded AI generation limit for current month"""
    from app import db, AIGeneratorHistory, AISuggestionHistory
    
    limits = get_user_tier_limits(user)
    max_generations = limits['ai_generations_per_month']
    
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
    
    return total_generations < max_generations, remaining


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
        
        can_generate, remaining = check_ai_generation_limit(current_user)
        
        if not can_generate:
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
    from app import db, TemplateDownload, AIGeneratorHistory, AISuggestionHistory
    
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Downloads
    downloads_this_month = TemplateDownload.query.filter(
        TemplateDownload.user_id == user.id,
        TemplateDownload.download_date >= first_day_of_month
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

