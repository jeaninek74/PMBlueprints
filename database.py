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
        catalog_path = os.path.join(current_dir, "templates_catalog.json")
        
        # Fallback to embedded data if file not found
        if not os.path.exists(catalog_path):
            logger.warning("Templates catalog file not found, using embedded data")
            templates_data = get_embedded_templates()
        else:
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

def get_embedded_templates():
    """Embedded template data as fallback"""
    return [
        {
            "id": 1,
            "name": "Project Charter Template",
            "description": "Comprehensive project charter following PMI standards",
            "industry": "Technology",
            "category": "Project Planning",
            "file_type": "xlsx",
            "filename": "project_charter.xlsx",
            "downloads": 1250,
            "rating": 4.8,
            "tags": ["charter", "initiation", "pmi"],
            "file_size": "45KB",
            "has_formulas": True,
            "has_fields": True,
            "is_premium": False
        },
        {
            "id": 2,
            "name": "Risk Register Template",
            "description": "Complete risk management tracking with formulas",
            "industry": "General",
            "category": "Risk Management",
            "file_type": "xlsx",
            "filename": "risk_register.xlsx",
            "downloads": 980,
            "rating": 4.7,
            "tags": ["risk", "management", "tracking"],
            "file_size": "38KB",
            "has_formulas": True,
            "has_fields": True,
            "is_premium": False
        },
        {
            "id": 3,
            "name": "WBS Template",
            "description": "Work Breakdown Structure with automated calculations",
            "industry": "Technology",
            "category": "Project Planning",
            "file_type": "xlsx",
            "filename": "wbs_template.xlsx",
            "downloads": 875,
            "rating": 4.6,
            "tags": ["wbs", "planning", "structure"],
            "file_size": "52KB",
            "has_formulas": True,
            "has_fields": True,
            "is_premium": False
        }
    ]
