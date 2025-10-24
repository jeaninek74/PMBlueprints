#!/usr/bin/env python3
"""
Migration: Delete Product, IT, and Finance templates with wrong content.
Keep only templates whose filenames exist in public/templates folder.
"""

from models import Template, db
import os

def run_migration():
    """Delete templates that don't have corresponding files in public/templates"""
    
    # Get list of actual template files in public/templates
    template_dir = 'public/templates'
    if not os.path.exists(template_dir):
        print(f"❌ Template directory {template_dir} not found")
        return False
    
    existing_files = set(os.listdir(template_dir))
    
    # Get all Product, IT, and Finance templates from database
    templates_to_check = Template.query.filter(
        Template.industry.in_(['Product', 'IT', 'Finance'])
    ).all()
    
    templates_to_delete = []
    for template in templates_to_check:
        if template.file_path not in existing_files:
            templates_to_delete.append(template)
    
    if not templates_to_delete:
        print("✅ No templates to delete - all templates have corresponding files")
        return True
    
    print(f"🗑️  Deleting {len(templates_to_delete)} templates with missing files:")
    
    product_delete = [t for t in templates_to_delete if t.industry == 'Product']
    it_delete = [t for t in templates_to_delete if t.industry == 'IT']
    finance_delete = [t for t in templates_to_delete if t.industry == 'Finance']
    
    print(f"  Product: {len(product_delete)}")
    print(f"  IT: {len(it_delete)}")
    print(f"  Finance: {len(finance_delete)}")
    
    # Delete templates
    for template in templates_to_delete:
        db.session.delete(template)
    
    db.session.commit()
    
    print(f"✅ Successfully deleted {len(templates_to_delete)} templates")
    print(f"Remaining templates:")
    print(f"  Product: {Template.query.filter_by(industry='Product').count()}")
    print(f"  IT: {Template.query.filter_by(industry='IT').count()}")
    print(f"  Finance: {Template.query.filter_by(industry='Finance').count()}")
    print(f"  Total: {Template.query.count()}")
    
    return True

