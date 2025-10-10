"""
Search API Routes
Handles search suggestions and advanced search functionality
"""

from flask import Blueprint, jsonify, request
import logging

logger = logging.getLogger(__name__)

search_api_bp = Blueprint('search_api', __name__)

@search_api_bp.route('/suggestions')
def search_suggestions():
    """Get search suggestions"""
    try:
        # Import here to avoid circular imports
        from app import db, Template
        
        query = request.args.get('q', '').strip()
        if not query or len(query) < 2:
            return jsonify({'success': True, 'suggestions': []})

        # Search in template names and descriptions
        search_term = f"%{query}%"
        templates = Template.query.filter(
            Template.name.ilike(search_term) | 
            Template.description.ilike(search_term)
        ).limit(10).all()

        suggestions = []
        for template in templates:
            suggestions.append({
                'id': template.id,
                'name': template.name,
                'industry': template.industry,
                'category': template.category
            })

        return jsonify({
            'success': True,
            'suggestions': suggestions
        })

    except Exception as e:
        logger.error(f"Search suggestions error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
