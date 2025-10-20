#!/usr/bin/env python3
"""
Update database with ImgBB URLs for templates.
Maps screenshot filenames to template records and updates image_url field.
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, '/home/ubuntu/pmb_repo')

from app import app, db
from models import Template

def load_imgbb_urls():
    """Load ImgBB URL mappings from JSON file."""
    with open('/home/ubuntu/pmb_repo/imgbb_urls.json', 'r') as f:
        return json.load(f)

def get_template_base_name(file_path):
    """Extract base name from template file path for matching."""
    if not file_path:
        return None
    filename = os.path.basename(file_path)
    # Remove extension (.xlsx or .docx)
    base_name = os.path.splitext(filename)[0]
    return base_name

def update_database():
    """Update all template records with ImgBB URLs."""
    
    with app.app_context():
        print("=" * 80)
        print("UPDATING DATABASE WITH IMGBB URLS")
        print("=" * 80)
        print()
        
        # Load ImgBB URLs
        imgbb_urls = load_imgbb_urls()
        print(f"Loaded {len(imgbb_urls)} ImgBB URLs")
        print()
        
        # Get all templates
        templates = Template.query.all()
        print(f"Found {len(templates)} templates in database")
        print()
        
        updated = 0
        not_found = 0
        
        for template in templates:
            base_name = get_template_base_name(template.file_path)
            
            if not base_name:
                continue
            
            # Try to find matching screenshot
            screenshot_name = f"{base_name}.png"
            
            if screenshot_name in imgbb_urls:
                # Update with ImgBB URL
                imgbb_url = imgbb_urls[screenshot_name]['url']
                template.image_url = imgbb_url
                updated += 1
                
                if updated <= 10:
                    print(f"✓ Updated: {template.name}")
                    print(f"  File: {base_name}")
                    print(f"  Image: {imgbb_url}")
                    print()
            else:
                not_found += 1
                if not_found <= 5:
                    print(f"✗ No ImgBB URL for: {base_name}")
        
        # Commit changes
        db.session.commit()
        
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total templates: {len(templates)}")
        print(f"Updated with ImgBB URLs: {updated}")
        print(f"Not found in ImgBB: {not_found}")
        print()
        print("✓ Database updated successfully!")
        print()
        
        return updated, not_found

if __name__ == "__main__":
    update_database()

