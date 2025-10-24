"""
Migration: Replace Product and IT templates with catalog versions
Removes seed-generated duplicates and loads only catalog templates
"""
import os
import json
from datetime import datetime

def run_migration(app, db, Template):
    """Replace Product and IT templates with catalog versions"""
    
    migration_name = "replace_product_it_with_catalog"
    
    # Check if migration already ran
    from models import Migration
    existing = Migration.query.filter_by(name=migration_name).first()
    if existing:
        app.logger.info(f"✅ Migration '{migration_name}' already applied")
        return
    
    app.logger.info(f"🔄 Running migration: {migration_name}")
    
    try:
        # Load catalog
        catalog_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates_catalog.json')
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
        
        # Get Product and IT templates from catalog
        product_catalog = [t for t in catalog if t.get('industry') == 'Product']
        it_catalog = [t for t in catalog if t.get('industry') == 'IT']
        
        app.logger.info(f"📁 Catalog has {len(product_catalog)} Product and {len(it_catalog)} IT templates")
        
        # Delete all existing Product templates
        product_deleted = Template.query.filter_by(industry='Product').delete()
        app.logger.info(f"🗑️  Deleted {product_deleted} Product templates")
        
        # Delete all existing IT templates
        it_deleted = Template.query.filter_by(industry='IT').delete()
        app.logger.info(f"🗑️  Deleted {it_deleted} IT templates")
        
        db.session.commit()
        
        # Add Product templates from catalog
        product_added = 0
        for entry in product_catalog:
            template = Template(
                name=entry['name'],
                description=entry['description'],
                category=entry['category'],
                industry=entry['industry'],
                file_path=entry['filename'],
                file_format=entry.get('file_format', 'xlsx').upper(),
                is_free=entry.get('is_free', False)
            )
            db.session.add(template)
            product_added += 1
        
        # Add IT templates from catalog
        it_added = 0
        for entry in it_catalog:
            template = Template(
                name=entry['name'],
                description=entry['description'],
                category=entry['category'],
                industry=entry['industry'],
                file_path=entry['filename'],
                file_format=entry.get('file_format', 'xlsx').upper(),
                is_free=entry.get('is_free', False)
            )
            db.session.add(template)
            it_added += 1
        
        db.session.commit()
        
        app.logger.info(f"✅ Added {product_added} Product templates from catalog")
        app.logger.info(f"✅ Added {it_added} IT templates from catalog")
        
        # Record migration
        migration_record = Migration(
            name=migration_name,
            applied_at=datetime.utcnow()
        )
        db.session.add(migration_record)
        db.session.commit()
        
        app.logger.info(f"✅ Migration '{migration_name}' completed successfully")
        
        # Log final counts
        final_product = Template.query.filter_by(industry='Product').count()
        final_it = Template.query.filter_by(industry='IT').count()
        final_total = Template.query.count()
        
        app.logger.info(f"📊 Final counts: Product={final_product}, IT={final_it}, Total={final_total}")
        
    except Exception as e:
        app.logger.error(f"❌ Migration '{migration_name}' failed: {e}")
        db.session.rollback()
        raise

