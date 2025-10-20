"""
Add this route temporarily to app.py to debug the current_user object
"""

@app.route('/debug/user')
@login_required
def debug_user():
    from flask import jsonify
    from utils.subscription_security import check_feature_access, get_user_tier_limits
    
    user_data = {
        'email': current_user.email,
        'id': current_user.id,
        'subscription_tier': current_user.subscription_tier,
        'subscription_tier_type': str(type(current_user.subscription_tier)),
        'subscription_status': current_user.subscription_status,
        'is_authenticated': current_user.is_authenticated,
        'platform_integrations_access': check_feature_access(current_user, 'platform_integrations'),
        'tier_limits': get_user_tier_limits(current_user)
    }
    
    return jsonify(user_data)

