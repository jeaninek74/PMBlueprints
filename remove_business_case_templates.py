#!/usr/bin/env python3
"""
Remove all Business Case templates from database and files
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Template

def main():
    print("=" * 80)
    print("REMOVING ALL BUSINESS CASE TEMPLATES")
    print("=" * 80)
    print()
    
    templates_dir = Path(__file__).parent / 'static' / 'templates'
    
    with app.app_context():
        # Find all Business Case templates
        business_cases = Template.query.filter(Template.name == 'Business Case').all()
        
        print(f"Found {len(business_cases)} Business Case templates to remove")
        print()
        
        for template in business_cases:
            print(f"Removing ID {template.id}: {template.name}")
            print(f"  Industry: {template.industry}")
            print(f"  File: {template.file_path}")
            
            # Delete file
            file_path = templates_dir / template.file_path
            if file_path.exists():
                file_path.unlink()
                print(f"  ✅ File deleted")
            else:
                print(f"  ⚠️  File not found")
            
            # Delete from database
            db.session.delete(template)
            print(f"  ✅ Removed from database")
            print()
        
        # Commit changes
        db.session.commit()
        print("=" * 80)
        print(f"COMPLETE - Removed {len(business_cases)} Business Case templates")
        print("=" * 80)

if __name__ == '__main__':
    main()

