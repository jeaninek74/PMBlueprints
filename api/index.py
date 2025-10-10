"""
Vercel serverless entry point for PMBlueprints Flask application
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import our app
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Import the Flask app
from app import app

# Initialize database immediately for serverless compatibility
def initialize_database():
    from database import ensure_database_initialized
    with app.app_context():
        ensure_database_initialized()

# Initialize on import for serverless
try:
    initialize_database()
except Exception as e:
    # Log error but don't fail import
    import logging
    logging.getLogger(__name__).warning(f"Database initialization warning: {e}")

# Vercel expects the app to be available directly
# This is the WSGI application that Vercel will call
application = app

# For local testing
if __name__ == "__main__":
    app.run(debug=True)
