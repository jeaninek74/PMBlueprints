#!/usr/bin/env python3
"""
Update database to use correct image paths for all templates.
Maps template filenames to their corresponding screenshot images.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, '/home/ubuntu/pmb_repo')

from app import app, db
from models import Template

def update_template_images():
    """Update all template records with correct image paths."""
    
    with app.app_context():
        print("=" * 80)
        print("UPDATING TEMPLATE IMAGE PATHS")
        print("=" * 80)
        
        # Get all templates
        templates = Template.query.all()
        print(f"Found {len(templates)} templates in database")
        print()
        
        # Directory with screenshots
        screenshots_dir = "/home/ubuntu/pmb_repo/static/final_screenshots"
        
        # Get all screenshot files
        screenshot_files = {}
        for filename in os.listdir(screenshots_dir):
            if filename.endswith('.png'):
                # Remove .png extension to get base name
                base_name = filename[:-4]
                screenshot_files[base_name] = filename
        
        print(f"Found {len(screenshot_files)} screenshot files")
        print()
        
        updated = 0
        not_found = 0
        
        for template in templates:
            # Get template filename without extension
            if template.file_path:
                file_path = template.file_path
                # Extract filename from path
                filename = os.path.basename(file_path)
                # Remove extension (.xlsx or .docx)
                base_name = os.path.splitext(filename)[0]
                
                # Check if we have a screenshot for this template
                if base_name in screenshot_files:
                    # Update image path to use new screenshot
                    new_image_path = f"/static/final_screenshots/{screenshot_files[base_name]}"
                    template.image_url = new_image_path
                    updated += 1
                    
                    if updated <= 10:
                        print(f"✓ Updated: {template.name}")
                        print(f"  Image: {new_image_path}")
                else:
                    not_found += 1
                    if not_found <= 5:
                        print(f"✗ No screenshot found for: {base_name}")
        
        # Commit changes
        db.session.commit()
        
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total templates: {len(templates)}")
        print(f"Updated: {updated}")
        print(f"Not found: {not_found}")
        print()
        print("✓ Database updated successfully!")
        print()

if __name__ == "__main__":
    update_template_images()

