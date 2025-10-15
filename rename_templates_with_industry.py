#!/usr/bin/env python3.11
"""
Rename all templates with industry prefix
Format: Industry_Template_Name.ext
Example: AI_ML_Project_Plan.xlsx
"""

import os
import sys
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Template

def sanitize_industry_name(industry):
    """Convert industry name to filename-safe format"""
    # Remove special characters and replace spaces with underscores
    sanitized = re.sub(r'[^\w\s-]', '', industry)
    sanitized = re.sub(r'[\s-]+', '_', sanitized)
    return sanitized

def rename_template_file(old_path, new_path):
    """Rename a template file"""
    if os.path.exists(old_path):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        
        # Rename the file
        os.rename(old_path, new_path)
        return True
    return False

def main():
    """Main function to rename all templates"""
    with app.app_context():
        print("Starting template renaming process...")
        print(f"Total templates in database: {Template.query.count()}")
        
        templates = Template.query.all()
        
        renamed_count = 0
        skipped_count = 0
        error_count = 0
        
        for template in templates:
            try:
                # Get current filename
                current_filename = template.filename
                
                # Check if already has industry prefix
                industry_prefix = sanitize_industry_name(template.industry)
                
                if current_filename.startswith(industry_prefix + '_'):
                    print(f"SKIP: {current_filename} already has industry prefix")
                    skipped_count += 1
                    continue
                
                # Create new filename with industry prefix
                file_extension = Path(current_filename).suffix
                template_name_without_ext = Path(current_filename).stem
                
                new_filename = f"{industry_prefix}_{template_name_without_ext}{file_extension}"
                
                # Get file paths
                old_file_path = os.path.join('public', 'templates', current_filename)
                new_file_path = os.path.join('public', 'templates', new_filename)
                
                # Rename physical file
                if rename_template_file(old_file_path, new_file_path):
                    # Update database record
                    template.filename = new_filename
                    
                    # Update template name to include industry
                    if not template.name.startswith(template.industry):
                        template.name = f"{template.industry} {template.name}"
                    
                    db.session.commit()
                    
                    print(f"✓ Renamed: {current_filename} → {new_filename}")
                    renamed_count += 1
                else:
                    print(f"✗ File not found: {old_file_path}")
                    error_count += 1
                    
            except Exception as e:
                print(f"✗ Error renaming {template.filename}: {e}")
                error_count += 1
                db.session.rollback()
        
        print("\n" + "="*60)
        print("RENAMING SUMMARY")
        print("="*60)
        print(f"Total templates: {len(templates)}")
        print(f"Renamed: {renamed_count}")
        print(f"Skipped (already prefixed): {skipped_count}")
        print(f"Errors: {error_count}")
        print("="*60)
        
        if renamed_count > 0:
            print("\n✓ Template renaming completed successfully!")
        else:
            print("\n⚠ No templates were renamed.")

if __name__ == '__main__':
    main()

