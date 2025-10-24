#!/usr/bin/env python3
"""
Seed database from templates_catalog.json
Clears existing templates and loads only from catalog
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Template

def seed_from_catalog():
    """Load templates from catalog into database"""
    
    catalog_path = os.path.join(os.path.dirname(__file__), 'templates_catalog.json')
    
    if not os.path.exists(catalog_path):
        print(f"❌ Catalog not found: {catalog_path}")
        return False
    
    # Load catalog
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    print(f"📁 Loaded {len(catalog)} templates from catalog")
    
    with app.app_context():
        try:
            # Clear existing templates
            print("🗑️  Clearing existing templates from database...")
            Template.query.delete()
            db.session.commit()
            print("✓ Database cleared")
            
            # Add templates from catalog
            print("📝 Adding templates from catalog...")
            added = 0
            
            for entry in catalog:
                filename = entry.get('filename', '')
                file_path = f'static/templates/{filename}' if filename else ''
                
                template = Template(
                    name=entry.get('name', 'Unknown'),
                    description=entry.get('description', ''),
                    industry=entry.get('industry', 'General'),
                    category=entry.get('category', 'Other'),
                    file_format=entry.get('file_type', 'xlsx').upper(),
                    file_path=file_path
                )
                db.session.add(template)
                added += 1
            
            db.session.commit()
            print(f"✓ Added {added} templates to database")
            
            # Verify
            total = Template.query.count()
            product_count = Template.query.filter_by(industry='Product').count()
            finance_count = Template.query.filter_by(industry='Finance').count()
            it_count = Template.query.filter_by(industry='IT').count()
            
            print(f"\n{'='*80}")
            print(f"DATABASE SUMMARY")
            print(f"{'='*80}")
            print(f"Total templates: {total}")
            print(f"  Product: {product_count}")
            print(f"  Finance: {finance_count}")
            print(f"  IT: {it_count}")
            print(f"{'='*80}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = seed_from_catalog()
    sys.exit(0 if success else 1)

