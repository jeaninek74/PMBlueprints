#!/usr/bin/env python3
"""
Delete Product, IT, and Finance templates that don't match the correct uploaded files.
Keep only templates whose filenames exist in the correct_template_files.txt list.
"""

from app import app, db
from models import Template
import os

# Read list of correct template filenames
with open('/home/ubuntu/correct_template_files.txt', 'r') as f:
    correct_filenames = set(line.strip() for line in f)

print(f"Correct template files to keep: {len(correct_filenames)}")
print(f"  Product: {len([f for f in correct_filenames if f.startswith('Product_')])}")
print(f"  IT: {len([f for f in correct_filenames if f.startswith('IT_')])}")
print(f"  Finance: {len([f for f in correct_filenames if f.startswith('Finance_')])}")

with app.app_context():
    # Get all Product, IT, and Finance templates
    templates_to_check = Template.query.filter(
        Template.industry.in_(['Product', 'IT', 'Finance'])
    ).all()
    
    print(f"\nTotal templates to check: {len(templates_to_check)}")
    
    templates_to_delete = []
    templates_to_keep = []
    
    for template in templates_to_check:
        if template.file_path in correct_filenames:
            templates_to_keep.append(template)
        else:
            templates_to_delete.append(template)
    
    print(f"\nTemplates to KEEP: {len(templates_to_keep)}")
    print(f"Templates to DELETE: {len(templates_to_delete)}")
    
    # Show what will be deleted by industry
    product_delete = [t for t in templates_to_delete if t.industry == 'Product']
    it_delete = [t for t in templates_to_delete if t.industry == 'IT']
    finance_delete = [t for t in templates_to_delete if t.industry == 'Finance']
    
    print(f"\nBreakdown of deletions:")
    print(f"  Product: {len(product_delete)}")
    print(f"  IT: {len(it_delete)}")
    print(f"  Finance: {len(finance_delete)}")
    
    # Delete template files and database records
    deleted_count = 0
    for template in templates_to_delete:
        # Delete file if it exists
        file_path = os.path.join('public/templates', template.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  Deleted file: {template.file_path}")
        
        # Delete database record
        db.session.delete(template)
        deleted_count += 1
    
    db.session.commit()
    
    print(f"\n✅ DELETION COMPLETE!")
    print(f"Total templates deleted: {deleted_count}")
    print(f"Remaining templates: {Template.query.count()}")
    print(f"  Product: {Template.query.filter_by(industry='Product').count()}")
    print(f"  IT: {Template.query.filter_by(industry='IT').count()}")
    print(f"  Finance: {Template.query.filter_by(industry='Finance').count()}")

