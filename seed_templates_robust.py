#!/usr/bin/env python3
"""
Robust Template Database Seeding Script
Ensures production database always has correct template data
Never crashes - comprehensive error handling
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Template

def load_template_metadata():
    """Load template metadata from templates directory"""
    templates_dir = Path(__file__).parent / 'static' / 'templates'
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return []
    
    template_files = list(templates_dir.glob('*.xlsx')) + list(templates_dir.glob('*.docx'))
    
    print(f"📁 Found {len(template_files)} template files")
    return template_files

def parse_filename(filename):
    """Parse template filename to extract metadata"""
    try:
        # Remove extension
        name_parts = filename.stem.split('_')
        
        # First part is usually industry (e.g., AI_ML, Healthcare, Construction)
        if len(name_parts) >= 2:
            # Handle multi-word industries like "AI_ML"
            if name_parts[0] == 'AI' and name_parts[1] == 'ML':
                industry = 'AI ML'
                template_name_parts = name_parts[2:]
            elif name_parts[0] == 'Business' and name_parts[1] == 'Process':
                industry = 'Business Process Improvement'
                template_name_parts = name_parts[2:]
            elif name_parts[0] == 'Cloud':
                industry = 'Cloud Migration'
                template_name_parts = name_parts[2:]
            elif name_parts[0] == 'Customer':
                industry = 'Customer Experience'
                template_name_parts = name_parts[2:]
            elif name_parts[0] == 'Data':
                industry = 'Data Analytics'
                template_name_parts = name_parts[2:]
            elif name_parts[0] == 'Digital':
                industry = 'Digital Transformation'
                template_name_parts = name_parts[2:]
            elif name_parts[0] == 'ERP':
                industry = 'ERP Implementation'
                template_name_parts = name_parts[1:]
            elif name_parts[0] == 'Hardware':
                industry = 'Hardware Implementation'
                template_name_parts = name_parts[1:]
            elif name_parts[0] == 'Media':
                industry = 'Media & Entertainment'
                template_name_parts = name_parts[1:]
            elif name_parts[0] == 'Merger':
                industry = 'Merger & Acquisition'
                template_name_parts = name_parts[3:]
            elif name_parts[0] == 'Non':
                industry = 'Non-Profit'
                template_name_parts = name_parts[1:]
            elif name_parts[0] == 'Operational':
                industry = 'Operational Improvement'
                template_name_parts = name_parts[1:]
            elif name_parts[0] == 'R&D':
                industry = 'Research & Development'
                template_name_parts = name_parts[1:]
            elif name_parts[0] == 'Supply':
                industry = 'Supply Chain Optimization'
                template_name_parts = name_parts[3:]
            else:
                industry = name_parts[0].replace('_', ' ')
                template_name_parts = name_parts[1:]
            
            # Join remaining parts as template name
            template_name = ' '.join(template_name_parts).replace('_', ' ')
            
            # Remove common suffixes
            template_name = template_name.replace(' 2025 PMI', '')
            template_name = template_name.replace(' with Instructions', '')
            template_name = template_name.replace(' REBUILT', '')
            
            # Extract category (usually the last meaningful part)
            category = template_name.strip()
            
            # Determine format
            format_type = 'EXCEL' if filename.suffix == '.xlsx' else 'WORD'
            
            return {
                'industry': industry,
                'name': category,
                'category': category,
                'format': format_type,
                'file_path': filename.name
            }
    except Exception as e:
        print(f"⚠️  Error parsing {filename.name}: {e}")
        return None

def seed_templates(mode='sync'):
    """
    Seed templates into database
    
    Modes:
    - 'sync': Add missing templates, update existing ones
    - 'verify': Only check without making changes
    - 'reset': Delete all and re-import (dangerous!)
    """
    
    print("=" * 80)
    print("TEMPLATE DATABASE SEEDING")
    print("=" * 80)
    print(f"Mode: {mode}")
    print()
    
    try:
        with app.app_context():
            # Load template files
            template_files = load_template_metadata()
            
            if not template_files:
                print("❌ No template files found!")
                return False
            
            # Get current database state
            existing_templates = {t.file_path: t for t in Template.query.all()}
            existing_count = len(existing_templates)
            
            print(f"📊 Current State:")
            print(f"   Files on disk: {len(template_files)}")
            print(f"   Templates in DB: {existing_count}")
            print()
            
            if mode == 'reset':
                print("⚠️  RESET MODE - Deleting all templates...")
                Template.query.delete()
                db.session.commit()
                existing_templates = {}
                print("✅ All templates deleted")
                print()
            
            # Process each file
            added = 0
            updated = 0
            skipped = 0
            errors = 0
            
            for template_file in template_files:
                try:
                    metadata = parse_filename(template_file)
                    
                    if not metadata:
                        errors += 1
                        continue
                    
                    file_path = metadata['file_path']
                    
                    if mode == 'verify':
                        if file_path in existing_templates:
                            print(f"✅ {file_path}")
                        else:
                            print(f"❌ MISSING: {file_path}")
                        continue
                    
                    # Check if template exists
                    if file_path in existing_templates:
                        # Update existing template
                        template = existing_templates[file_path]
                        template.industry = metadata['industry']
                        template.name = metadata['name']
                        template.category = metadata['category']
                        template.format = metadata['format']
                        updated += 1
                    else:
                        # Add new template
                        template = Template(
                            industry=metadata['industry'],
                            name=metadata['name'],
                            category=metadata['category'],
                            format=metadata['format'],
                            file_path=file_path,
                            description=f"{metadata['name']} for {metadata['industry']} projects",
                            price=50.00
                        )
                        db.session.add(template)
                        added += 1
                    
                except Exception as e:
                    print(f"❌ Error processing {template_file.name}: {e}")
                    errors += 1
                    continue
            
            if mode != 'verify':
                # Commit changes
                db.session.commit()
            
            # Print summary
            print()
            print("=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"✅ Added: {added}")
            print(f"🔄 Updated: {updated}")
            print(f"⏭️  Skipped: {skipped}")
            print(f"❌ Errors: {errors}")
            print()
            
            # Verify final state
            final_count = Template.query.count()
            industries = db.session.query(Template.industry).distinct().count()
            categories = db.session.query(Template.category).distinct().count()
            
            print(f"📊 Final State:")
            print(f"   Total templates: {final_count}")
            print(f"   Industries: {industries}")
            print(f"   Categories: {categories}")
            print("=" * 80)
            
            return True
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed template database')
    parser.add_argument('--mode', choices=['sync', 'verify', 'reset'], 
                       default='sync', help='Seeding mode')
    
    args = parser.parse_args()
    
    success = seed_templates(mode=args.mode)
    sys.exit(0 if success else 1)

