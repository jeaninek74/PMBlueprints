#!/usr/bin/env python3
"""
Remove templates added by seed script, keep only catalog templates
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Template

def clean_to_catalog_only():
    """Keep only templates that are in the catalog"""
    
    catalog_path = os.path.join(os.path.dirname(__file__), 'templates_catalog.json')
    
    if not os.path.exists(catalog_path):
        print(f"❌ Catalog not found: {catalog_path}")
        return False
    
    # Load catalog
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    # Get catalog filenames
    catalog_files = {entry.get('filename') for entry in catalog if entry.get('filename')}
    
    print(f"📁 Catalog has {len(catalog_files)} templates")
    print(f"Catalog files: {sorted(catalog_files)}")
    
    with app.app_context():
        try:
            # Get all templates
            all_templates = Template.query.all()
            print(f"\n📊 Database has {len(all_templates)} templates")
            
            # Find templates to remove (not in catalog)
            to_remove = []
            for template in all_templates:
                # Extract filename from file_path
                if template.file_path:
                    filename = os.path.basename(template.file_path)
                    if filename not in catalog_files:
                        to_remove.append(template)
            
            print(f"\n🗑️  Found {len(to_remove)} templates to remove (not in catalog)")
            
            # Group by industry for reporting
            by_industry = {}
            for template in to_remove:
                industry = template.industry or 'Unknown'
                if industry not in by_industry:
                    by_industry[industry] = []
                by_industry[industry].append(template.name)
            
            print("\nTemplates to remove by industry:")
            for industry, names in sorted(by_industry.items()):
                print(f"  {industry}: {len(names)} templates")
                for name in sorted(names)[:5]:  # Show first 5
                    print(f"    - {name}")
                if len(names) > 5:
                    print(f"    ... and {len(names) - 5} more")
            
            # Remove templates
            for template in to_remove:
                db.session.delete(template)
            
            db.session.commit()
            print(f"\n✅ Removed {len(to_remove)} templates")
            
            # Verify final state
            remaining = Template.query.count()
            product_count = Template.query.filter_by(industry='Product').count()
            finance_count = Template.query.filter_by(industry='Finance').count()
            it_count = Template.query.filter_by(industry='IT').count()
            
            print(f"\n{'='*80}")
            print(f"FINAL DATABASE STATE")
            print(f"{'='*80}")
            print(f"Total templates: {remaining}")
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
    success = clean_to_catalog_only()
    sys.exit(0 if success else 1)

