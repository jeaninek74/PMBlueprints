"""
Favorites and Ratings API Routes
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging

favorites_bp = Blueprint('favorites', __name__)
logger = logging.getLogger(__name__)

@favorites_bp.route('/api/favorites', methods=['GET'])
@login_required
def get_favorites():
    """Get user's favorite templates"""
    try:
        from app import Favorite, Template
        
        favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        template_ids = [f.template_id for f in favorites]
        
        return jsonify({
            'success': True,
            'favorites': template_ids,
            'count': len(template_ids)
        })
    except Exception as e:
        logger.error(f"Error getting favorites: {e}")
        return jsonify({'success': False, 'error': 'Failed to get favorites'}), 500

@favorites_bp.route('/api/favorites/<int:template_id>', methods=['POST'])
@login_required
def add_favorite(template_id):
    """Add template to favorites"""
    try:
        from database import db, Favorite, Template
        
        # Check if template exists
        template = Template.query.get(template_id)
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        # Check if already favorited
        existing = Favorite.query.filter_by(
            user_id=current_user.id,
            template_id=template_id
        ).first()
        
        if existing:
            return jsonify({'success': True, 'message': 'Already favorited', 'action': 'none'})
        
        # Add favorite
        favorite = Favorite(user_id=current_user.id, template_id=template_id)
        db.session.add(favorite)
        db.session.commit()
        
        logger.info(f"User {current_user.id} favorited template {template_id}")
        
        return jsonify({
            'success': True,
            'message': 'Template added to favorites',
            'action': 'added'
        })
    except Exception as e:
        logger.error(f"Error adding favorite: {e}")
        return jsonify({'success': False, 'error': 'Failed to add favorite'}), 500

@favorites_bp.route('/api/favorites/<int:template_id>', methods=['DELETE'])
@login_required
def remove_favorite(template_id):
    """Remove template from favorites"""
    try:
        from database import db, Favorite
        
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            template_id=template_id
        ).first()
        
        if not favorite:
            return jsonify({'success': False, 'error': 'Favorite not found'}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        logger.info(f"User {current_user.id} unfavorited template {template_id}")
        
        return jsonify({
            'success': True,
            'message': 'Template removed from favorites',
            'action': 'removed'
        })
    except Exception as e:
        logger.error(f"Error removing favorite: {e}")
        return jsonify({'success': False, 'error': 'Failed to remove favorite'}), 500

@favorites_bp.route('/api/ratings/<int:template_id>', methods=['POST'])
@login_required
def rate_template(template_id):
    """Rate a template (1-5 stars)"""
    try:
        from database import db, TemplateRating, Template
        
        data = request.get_json()
        rating_value = data.get('rating')
        review_text = data.get('review', '')
        
        # Validate rating
        if not rating_value or not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
            return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400
        
        # Check if template exists
        template = Template.query.get(template_id)
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        # Check if user already rated
        existing_rating = TemplateRating.query.filter_by(
            user_id=current_user.id,
            template_id=template_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_value
            existing_rating.review = review_text
            action = 'updated'
        else:
            # Create new rating
            new_rating = TemplateRating(
                user_id=current_user.id,
                template_id=template_id,
                rating=rating_value,
                review=review_text
            )
            db.session.add(new_rating)
            action = 'added'
        
        db.session.commit()
        
        # Calculate new average rating
        all_ratings = TemplateRating.query.filter_by(template_id=template_id).all()
        avg_rating = sum(r.rating for r in all_ratings) / len(all_ratings)
        
        # Update template's rating
        template.rating = round(avg_rating, 1)
        db.session.commit()
        
        logger.info(f"User {current_user.id} rated template {template_id}: {rating_value} stars")
        
        return jsonify({
            'success': True,
            'message': f'Rating {action}',
            'action': action,
            'new_average': template.rating,
            'total_ratings': len(all_ratings)
        })
    except Exception as e:
        logger.error(f"Error rating template: {e}")
        return jsonify({'success': False, 'error': 'Failed to rate template'}), 500

@favorites_bp.route('/api/ratings/<int:template_id>', methods=['GET'])
def get_template_ratings(template_id):
    """Get ratings for a template"""
    try:
        from app import TemplateRating, Template, User
        
        template = Template.query.get(template_id)
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        ratings = TemplateRating.query.filter_by(template_id=template_id).all()
        
        ratings_data = []
        for rating in ratings:
            user = User.query.get(rating.user_id)
            ratings_data.append({
                'rating': rating.rating,
                'review': rating.review,
                'user_name': f"{user.first_name} {user.last_name[0]}." if user else "Anonymous",
                'created_at': rating.created_at.isoformat() if rating.created_at else None
            })
        
        return jsonify({
            'success': True,
            'average_rating': template.rating,
            'total_ratings': len(ratings),
            'ratings': ratings_data
        })
    except Exception as e:
        logger.error(f"Error getting ratings: {e}")
        return jsonify({'success': False, 'error': 'Failed to get ratings'}), 500

