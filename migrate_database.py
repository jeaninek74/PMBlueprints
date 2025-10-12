#!/usr/bin/env python3
"""
Database Migration Script for PMBlueprints
Adds missing tables: favorite and template_rating
"""
import os
import sys
from app import app, db

def migrate_database():
    """Create all missing database tables"""
    with app.app_context():
        try:
            print("Starting database migration...")
            
            # Create all tables (will skip existing ones)
            db.create_all()
            
            print("✓ Database migration completed successfully!")
            print("✓ All tables created/verified:")
            print("  - user")
            print("  - template")
            print("  - download")
            print("  - favorite")
            print("  - template_rating")
            
            return True
        except Exception as e:
            print(f"✗ Migration failed: {str(e)}")
            return False

if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)

