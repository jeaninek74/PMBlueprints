"""
Admin Routes
Temporary admin functions for testing
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import User
from database import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/upgrade-user', methods=['POST'])
@login_required
def upgrade_user():
    """Upgrade user to specified plan (for testing only)"""
    try:
        data = request.get_json()
        email = data.get('email')
        plan = data.get('plan', 'enterprise')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': f'User not found: {email}'}), 404
        
        # Upgrade user
        user.subscription_tier = plan
        user.subscription_status = 'active'
        user.subscription_start_date = datetime.utcnow()
        user.downloads_this_month = 0
        user.ai_suggestions_this_month = 0
        user.ai_generations_this_month = 0
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {email} upgraded to {plan}',
            'user': {
                'email': user.email,
                'plan': user.subscription_tier,
                'status': user.subscription_status
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/user-info/<email>', methods=['GET'])
@login_required
def user_info(email):
    """Get user information"""
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': f'User not found: {email}'}), 404
        
        return jsonify({
            'email': user.email,
            'plan': user.subscription_tier,
            'status': user.subscription_status,
            'downloads_this_month': user.downloads_this_month,
            'ai_suggestions_this_month': user.ai_suggestions_this_month,
            'ai_generations_this_month': user.ai_generations_this_month,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

