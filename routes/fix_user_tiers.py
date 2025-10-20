"""
One-time migration to fix user subscription tiers
"""
from flask import Blueprint, jsonify
from models import db, User
from werkzeug.security import generate_password_hash

fix_tiers_bp = Blueprint('fix_tiers', __name__)

@fix_tiers_bp.route('/admin/fix-all-user-tiers', methods=['POST'])
def fix_all_user_tiers():
    """Fix all test user subscription tiers"""
    try:
        # Update individual user
        individual = User.query.filter_by(email='individual@pmblueprints.com').first()
        if individual:
            individual.subscription_tier = 'individual'
        
        # Update professional user
        professional = User.query.filter_by(email='professional@pmblueprints.com').first()
        if professional:
            professional.subscription_tier = 'professional'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User tiers fixed',
            'individual': individual.subscription_tier if individual else 'not found',
            'professional': professional.subscription_tier if professional else 'not found'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

