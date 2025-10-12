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
from app import app, db

# Initialize database immediately for serverless compatibility
def initialize_database():
    """Ensure all database tables exist"""
    with app.app_context():
        try:
            # Create all tables if they don't exist
            db.create_all()
            
            # Auto-populate templates if database is empty
            from app import Template
            import json
            import logging
            
            logger = logging.getLogger(__name__)
            
            if Template.query.count() == 0:
                logger.info("Populating database with templates...")
                try:
                    catalog_path = os.path.join(parent_dir, "templates_catalog.json")
                    with open(catalog_path, "r") as f:
                        templates = json.load(f)
                    
                    for template_data in templates:
                        template = Template(
                            id=template_data.get("id"),
                            name=template_data.get("name"),
                            description=template_data.get("description"),
                            industry=template_data.get("industry"),
                            category=template_data.get("category"),
                            file_type=template_data.get("file_type"),
                            filename=template_data.get("filename"),
                            downloads=template_data.get("downloads", 0),
                            rating=template_data.get("rating", 4.5),
                            tags=",".join(template_data.get("tags", [])),
                            file_size=template_data.get("file_size"),
                            has_formulas=template_data.get("has_formulas", False),
                            has_fields=template_data.get("has_fields", False),
                            is_premium=template_data.get("is_premium", False),
                        )
                        db.session.add(template)
                    
                    db.session.commit()
                    logger.info(f"Database populated with {Template.query.count()} templates")
                except Exception as e:
                    logger.error(f"Error populating database: {e}")
            else:
                logger.info(f"Database already contains {Template.query.count()} templates")
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Database initialization error: {e}")

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

