"""
Restore database from templates_catalog_final.json
This will replace all corrupted AI ML templates with correct industry-specific templates
Updates existing templates instead of deleting to avoid foreign key constraint issues
"""
import json
import os
from app import app, db
from models import Template

def restore_database():
    """Restore database from correct catalog"""
    
    with app.app_context():
        print("🔄 Starting database restoration...")
        
        # Load correct catalog
        catalog_path = 'templates_catalog_final.json'
        print(f"📁 Loading catalog from {catalog_path}...")
        
        with open(catalog_path, 'r') as f:
            all_templates = json.load(f)
        
        print(f"✅ Loaded {len(all_templates)} templates from catalog")
        
        # Filter out Business Case templates (30 templates to remove)
        templates = [t for t in all_templates if t['category'] != 'Business Case']
        print(f"✅ Filtered to {len(templates)} templates (excluded {len(all_templates) - len(templates)} Business Case templates)")
        
        # Get all existing templates
        existing_templates = {t.id: t for t in Template.query.all()}
        print(f"📊 Found {len(existing_templates)} existing templates in database")
        
        # Update existing templates and add new ones
        print("🔄 Updating templates...")
        updated_count = 0
        added_count = 0
        errors = []
        
        # Create a mapping of filename to catalog entry
        catalog_by_filename = {entry['filename']: entry for entry in templates}
        
        # Update existing templates
        for template_id, template in existing_templates.items():
            try:
                # Find matching catalog entry by filename
                catalog_entry = catalog_by_filename.get(template.file_path)
                
                if catalog_entry:
                    # Update template with correct data
                    template.name = catalog_entry['name']
                    template.description = catalog_entry['description']
                    template.category = catalog_entry['category']
                    template.industry = catalog_entry['industry']
                    template.file_format = catalog_entry.get('file_format', catalog_entry.get('file_type', 'xlsx')).upper()
                    updated_count += 1
                    
                    # Remove from catalog so we don't add it again
                    del catalog_by_filename[template.file_path]
                    
                if updated_count % 100 == 0 and updated_count > 0:
                    print(f"  Progress: {updated_count} templates updated...")
                    
            except Exception as e:
                errors.append(f"Error updating template {template_id}: {e}")
        
        # Add remaining templates from catalog that don't exist in database
        print(f"📥 Adding {len(catalog_by_filename)} new templates...")
        for filename, entry in catalog_by_filename.items():
            try:
                template = Template(
                    name=entry['name'],
                    description=entry['description'],
                    category=entry['category'],
                    industry=entry['industry'],
                    file_path=entry['filename'],
                    file_format=entry.get('file_format', entry.get('file_type', 'xlsx')).upper()
                )
                db.session.add(template)
                added_count += 1
                
                if added_count % 100 == 0:
                    print(f"  Progress: {added_count} templates added...")
                    
            except Exception as e:
                errors.append(f"Error adding {entry.get('name', 'unknown')}: {e}")
        
        # Commit all changes
        print("💾 Committing changes to database...")
        db.session.commit()
        
        print(f"\n✅ Database restoration complete!")
        print(f"📊 Updated {updated_count} existing templates")
        print(f"📊 Added {added_count} new templates")
        
        if errors:
            print(f"\n⚠️  {len(errors)} errors occurred:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
        
        # Verify restoration
        print("\n🔍 Verifying restoration...")
        total = Template.query.count()
        industries = db.session.query(Template.industry).distinct().count()
        
        print(f"✅ Total templates in database: {total}")
        print(f"✅ Total industries: {industries}")
        
        # Show sample by industry
        print("\n📋 Sample templates by industry:")
        sample_industries = ['Healthcare', 'Construction', 'Finance', 'IT', 'Product']
        for industry in sample_industries:
            count = Template.query.filter_by(industry=industry).count()
            sample = Template.query.filter_by(industry=industry).first()
            if sample:
                print(f"  {industry}: {count} templates")
                print(f"    Example: {sample.name[:50]}...")
                print(f"    Description: {sample.description[:60]}...")
                
        # Verify no AI ML descriptions
        ai_ml_count = Template.query.filter(Template.description.like('%AI ML%')).count()
        if ai_ml_count > 0:
            print(f"\n⚠️  WARNING: Found {ai_ml_count} templates with 'AI ML' in description!")
        else:
            print(f"\n✅ SUCCESS: No AI ML descriptions found - all templates have correct industry content!")

if __name__ == '__main__':
    restore_database()

