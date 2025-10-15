#!/usr/bin/env python3
"""
Update all templates with thumbnail URLs
Run this once to populate preview_image field for all templates
"""
import os
from app import app, db, Template

def update_thumbnails():
    """Update all templates with thumbnail URLs"""
    with app.app_context():
        try:
            # Get all templates
            templates = Template.query.all()
            total = len(templates)
            updated = 0
            
            print(f"Found {total} templates in database")
            print("Updating thumbnail URLs...")
            
            for template in templates:
                # Generate thumbnail filename from template filename
                # Example: template_123.xlsx -> template_123.png
                if template.filename:
                    base_name = os.path.splitext(template.filename)[0]
                    thumbnail_filename = f"{base_name}.png"
                    thumbnail_url = f"/static/thumbnails/{thumbnail_filename}"
                    
                    # Update preview_image field
                    template.preview_image = thumbnail_url
                    updated += 1
                    
                    if updated % 100 == 0:
                        print(f"Progress: {updated}/{total} templates updated...")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✅ Successfully updated {updated} templates with thumbnail URLs!")
            print(f"Thumbnails are now available at /static/thumbnails/")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error updating thumbnails: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("="*60)
    print("Template Thumbnail URL Updater")
    print("="*60)
    success = update_thumbnails()
    print("="*60)
    exit(0 if success else 1)

