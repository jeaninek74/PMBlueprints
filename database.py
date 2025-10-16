""" Database initialization module
Re-exports all models for backward compatibility
"""
from flask_sqlalchemy import SQLAlchemy

# Create the database instance
db = SQLAlchemy()

# Import and re-export all models for backward compatibility
try:
    from models import (
        User, Template, Download, TemplateDownload, Favorite,
        TemplateRating, Payment, TemplatePurchase,
        AIGeneratorHistory, AISuggestionHistory
    )
except ImportError:
    # Models will be available after app initialization
    pass

