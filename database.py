"""
Database initialization for serverless deployment
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

def ensure_database_initialized():
    """Ensure database is initialized - safe to call multiple times"""
    try:
        # Import here to avoid circular imports
        from app import db, Template
        
        # Create tables if they don't exist
        db.create_all()
        
        # Check if templates exist
        if Template.query.count() == 0:
            populate_templates()
        
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

def populate_templates():
    """Populate database with templates from catalog"""
    try:
        # Import here to avoid circular imports
        from app import db, Template
        
        # Handle __file__ reference for serverless compatibility
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            current_dir = os.getcwd()
        
        # Try multiple possible paths for templates_catalog.json
        possible_paths = [
            os.path.join(current_dir, "templates_catalog.json"),
            os.path.join(os.getcwd(), "templates_catalog.json"),
            "/var/task/templates_catalog.json",  # Vercel serverless path
            "./templates_catalog.json"
        ]
        
        catalog_path = None
        for path in possible_paths:
            if os.path.exists(path):
                catalog_path = path
                logger.info(f"Found templates catalog at: {path}")
                break
        
        if not catalog_path:
            error_msg = f"Templates catalog not found. Tried paths: {possible_paths}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        with open(catalog_path, "r") as f:
            templates_data = json.load(f)
        
        for template_data in templates_data:
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
        logger.error(f"Error populating templates: {e}")
        # Import here to avoid circular imports
        from app import db
        db.session.rollback()

# Mock embedded templates removed - all templates must come from templates_catalog.json
