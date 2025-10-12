"""
Populate production database with templates from templates_catalog.json
This script will be run as a Vercel serverless function
"""
import json
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app import app, db, Template
from sqlalchemy.exc import IntegrityError

def populate_database():
    """Populate database with templates from JSON file"""
    with app.app_context():
        try:
            # Load templates from JSON
            json_path = current_dir / 'templates_catalog.json'
            with open(json_path, 'r') as f:
                templates_data = json.load(f)
            
            print(f"Found {len(templates_data)} templates to import")
            
            # Check if database already has templates
            existing_count = Template.query.count()
            if existing_count > 0:
                print(f"Database already contains {existing_count} templates")
                response = input("Do you want to clear and reimport? (yes/no): ")
                if response.lower() == 'yes':
                    Template.query.delete()
                    db.session.commit()
                    print("Cleared existing templates")
                else:
                    print("Skipping import")
                    return
            
            # Import templates
            imported = 0
            skipped = 0
            
            for template_data in templates_data:
                try:
                    # Create template object
                    template = Template(
                        id=template_data.get("id"),
                        name=template_data.get("name"),
                        filename=template_data.get("filename"),
                        industry=template_data.get("industry"),
                        category=template_data.get("category"),
                        file_type=template_data.get("file_type", "xlsx"),
                        description=template_data.get("description", ""),
                        downloads=template_data.get("downloads", 0),
                        rating=template_data.get("rating", 4.5),
                        tags=",".join(template_data.get("tags", [])),
                        file_size=template_data.get("file_size"),
                        has_formulas=template_data.get("has_formulas", False),
                        has_fields=template_data.get("has_fields", False),
                        is_premium=template_data.get("is_premium", False),
                    )
                    db.session.add(template)
                    imported += 1
                    
                    # Commit in batches of 100
                    if imported % 100 == 0:
                        db.session.commit()
                        print(f"Imported {imported} templates...")
                        
                except IntegrityError as e:
                    db.session.rollback()
                    skipped += 1
                    print(f"Skipped template {template_data.get('id')}: {e}")
                except Exception as e:
                    db.session.rollback()
                    skipped += 1
                    print(f"Error importing template {template_data.get('id')}: {e}")
            
            # Final commit
            db.session.commit()
            
            print(f"\n✅ Import complete!")
            print(f"   Imported: {imported} templates")
            print(f"   Skipped: {skipped} templates")
            print(f"   Total in database: {Template.query.count()} templates")
            
            # Show some statistics
            industries = db.session.query(Template.industry).distinct().count()
            categories = db.session.query(Template.category).distinct().count()
            
            print(f"\n📊 Database Statistics:")
            print(f"   Industries: {industries}")
            print(f"   Categories: {categories}")
            print(f"   Templates: {Template.query.count()}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    populate_database()

