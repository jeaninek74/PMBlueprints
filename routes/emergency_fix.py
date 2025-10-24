"""
Emergency admin endpoint to fix user subscription tiers
This should be removed after the fix is applied
"""
from flask import Blueprint, jsonify, request
from models import db, User
import logging

emergency_bp = Blueprint('emergency', __name__)
logger = logging.getLogger(__name__)

# Secret key to prevent unauthorized access
EMERGENCY_KEY = "pmb_emergency_fix_2025"

@emergency_bp.route('/emergency/fix-user-tier', methods=['POST'])
def fix_user_tier():
    """
    Emergency endpoint to fix user subscription tier
    POST /emergency/fix-user-tier
    Body: {"key": "secret", "email": "user@example.com", "tier": "enterprise"}
    """
    try:
        data = request.get_json()
        
        # Verify emergency key
        if data.get('key') != EMERGENCY_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        
        email = data.get('email')
        tier = data.get('tier')
        
        if not email or not tier:
            return jsonify({"error": "Missing email or tier"}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({"error": f"User not found: {email}"}), 404
        
        # Log before
        logger.info(f"[EMERGENCY FIX] User {email} - Current tier: {user.subscription_tier}")
        
        # Update tier
        old_tier = user.subscription_tier
        user.subscription_tier = tier
        user.subscription_status = 'active'
        db.session.commit()
        
        # Log after
        logger.info(f"[EMERGENCY FIX] User {email} - Updated tier: {user.subscription_tier}")
        
        return jsonify({
            "success": True,
            "email": email,
            "old_tier": old_tier,
            "new_tier": user.subscription_tier,
            "message": f"User {email} tier updated from '{old_tier}' to '{tier}'"
        }), 200
        
    except Exception as e:
        logger.error(f"[EMERGENCY FIX] Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@emergency_bp.route('/emergency/fix-null-formats', methods=['GET'])
def fix_null_formats():
    """
    Emergency endpoint to fix NULL file_format values causing 500 errors
    GET /emergency/fix-null-formats
    Error: jinja2.exceptions.UndefinedError: 'None' has no attribute 'upper'
    Location: /app/templates/templates/browse.html line 90
    """
    try:
        from models import Template
        
        # Count templates with NULL file_format
        null_count = Template.query.filter(Template.file_format == None).count()
        
        if null_count == 0:
            return jsonify({
                'success': True,
                'message': 'No templates with NULL file_format found',
                'updated': 0
            })
        
        # Get examples before fixing
        examples = Template.query.filter(Template.file_format == None).limit(5).all()
        example_ids = [t.id for t in examples]
        
        # Update all NULL file_format to 'xlsx'
        updated = Template.query.filter(Template.file_format == None).update(
            {'file_format': 'xlsx'},
            synchronize_session=False
        )
        
        db.session.commit()
        
        logger.info(f"Emergency fix: Updated {updated} templates with NULL file_format")
        
        return jsonify({
            'success': True,
            'message': f'Successfully fixed {updated} templates',
            'updated': updated,
            'example_ids': example_ids,
            'fix_applied': 'Set file_format to xlsx for all NULL values'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Emergency fix failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@emergency_bp.route('/emergency/list-users', methods=['POST'])
def list_users():
    """
    Emergency endpoint to list all users
    POST /emergency/list-users
    Body: {"key": "secret"}
    """
    try:
        data = request.get_json()
        
        # Verify emergency key
        if data.get('key') != EMERGENCY_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        
        users = User.query.all()
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "subscription_tier": user.subscription_tier,
                "subscription_status": user.subscription_status
            })
        
        return jsonify({
            "success": True,
            "count": len(user_list),
            "users": user_list
        }), 200
        
    except Exception as e:
        logger.error(f"[EMERGENCY FIX] Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

