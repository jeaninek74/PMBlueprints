#!/usr/bin/env python3
"""
Fix Broken Template Downloads
==============================

This script fixes templates 960 and 962 which are returning 500 errors.

The issue is likely:
1. Missing database records for these template IDs
2. Monitoring system error
3. Database ID mismatch

Solution:
- Verify database records exist
- Update records if needed
- Test downloads
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_templates():
    """Fix broken template downloads"""
    
    try:
        from app import app, db, Template
        import json
        
        with app.app_context():
            print("=" * 80)
            print("Fixing Broken Template Downloads")
            print("=" * 80)
            print()
            
            # Load catalog
            with open('templates_catalog.json', 'r') as f:
                catalog = json.load(f)
            
            # Find the problematic templates in catalog
            problem_files = [
                'Cybersecurity_Model_Feasibility_Evaluation_2025_PMI.docx',
                'Cybersecurity_Procurement_Management_Plan_2025_PMI.xlsx'
            ]
            
            for template_data in catalog:
                if template_data['filename'] in problem_files:
                    template_id = template_data.get('id')
                    filename = template_data['filename']
                    
                    print(f"Checking: {filename}")
                    print(f"Expected ID: {template_id}")
                    
                    # Check if template exists in database
                    template = Template.query.filter_by(id=template_id).first()
                    
                    if template:
                        print(f"✅ Template exists in database")
                        print(f"   Name: {template.name}")
                        print(f"   Filename: {template.filename}")
                        print(f"   Category: {template.category}")
                        
                        # Verify filename matches
                        if template.filename != filename:
                            print(f"⚠️  Filename mismatch!")
                            print(f"   DB: {template.filename}")
                            print(f"   Catalog: {filename}")
                            print(f"   Updating...")
                            template.filename = filename
                            db.session.commit()
                            print(f"✅ Fixed")
                        
                        # Verify file exists
                        file_path = os.path.join('static', 'templates', filename)
                        if os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)
                            print(f"✅ File exists: {file_size:,} bytes")
                        else:
                            print(f"❌ File missing: {file_path}")
                    
                    else:
                        print(f"❌ Template NOT in database")
                        print(f"   Creating database record...")
                        
                        # Create template record
                        new_template = Template(
                            id=template_id,
                            name=template_data['name'],
                            filename=filename,
                            category=template_data['category'],
                            industry=template_data['industry'],
                            description=template_data.get('description', ''),
                            file_type=template_data.get('file_type', 'xlsx'),
                            is_premium=False,
                            downloads=0
                        )
                        
                        db.session.add(new_template)
                        db.session.commit()
                        print(f"✅ Template created in database")
                    
                    print()
            
            print("=" * 80)
            print("✅ Fix Complete")
            print("=" * 80)
            print()
            print("Test the downloads:")
            print("  https://www.pmblueprints.net/templates/960/download")
            print("  https://www.pmblueprints.net/templates/962/download")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_templates()

