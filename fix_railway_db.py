"""Fix Railway database - ensure templates are loaded"""
import os
import json
from app import app
from database import db
from models import Template

with app.app_context():
    # Check template count
    count = Template.query.count()
    print(f"Current templates in DB: {count}")
    
    if count == 0:
        print("Loading templates from catalog...")
        with open('templates_catalog.json', 'r') as f:
            templates = json.load(f)
        
        for t in templates:
            template = Template(
                id=t.get("id"),
                name=t.get("name"),
                description=t.get("description"),
                industry=t.get("industry"),
                category=t.get("category"),
                file_format=t.get("file_type"),
                file_path=t.get("filename")
            )
            db.session.add(template)
        
        db.session.commit()
        print(f"Loaded {len(templates)} templates")
    else:
        print("Templates already loaded")
    
    # Test the browse query
    try:
        all_templates = Template.query.all()
        industries = sorted(list(set(t.industry for t in all_templates if t.industry)))
        categories = sorted(list(set(t.category for t in all_templates if t.category)))
        templates = Template.query.order_by(Template.industry, Template.name).limit(100).all()
        print(f"Browse query successful: {len(templates)} templates, {len(industries)} industries, {len(categories)} categories")
    except Exception as e:
        print(f"Browse query failed: {e}")
