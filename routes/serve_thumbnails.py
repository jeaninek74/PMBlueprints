"""
Serve Thumbnail Files Route
Serves static thumbnail images for template previews
"""

from flask import Blueprint, send_from_directory, abort
import os
import logging

logger = logging.getLogger(__name__)

# Create blueprint
serve_thumbnails_bp = Blueprint('serve_thumbnails', __name__)

# Get the absolute path to the thumbnails directory
THUMBNAILS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'thumbnails')

@serve_thumbnails_bp.route('/static/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    """
    Serve thumbnail files from the static/thumbnails directory
    """
    try:
        logger.info(f"Serving thumbnail: {filename}")
        logger.info(f"Thumbnails directory: {THUMBNAILS_DIR}")
        
        # Security: Only allow PNG files
        if not filename.endswith('.png'):
            logger.warning(f"Invalid file type requested: {filename}")
            abort(404)
        
        # Check if file exists
        file_path = os.path.join(THUMBNAILS_DIR, filename)
        if not os.path.exists(file_path):
            logger.warning(f"Thumbnail not found: {file_path}")
            abort(404)
        
        return send_from_directory(THUMBNAILS_DIR, filename, mimetype='image/png')
    
    except Exception as e:
        logger.error(f"Error serving thumbnail {filename}: {e}")
        abort(404)

