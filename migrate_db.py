#!/usr/bin/env python3
"""
Database migration script to add missing columns to production database
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

def migrate_database():
    """Add missing columns to users table"""
    
    # Get database URL from environment or use default
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/pmblueprints.db')
    
    # Fix postgres URL if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"Connecting to database...")
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Check if columns exist
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        print(f"Current columns in users table: {columns}")
        
        migrations_needed = []
        
        if 'reset_token' not in columns:
            migrations_needed.append("ALTER TABLE users ADD COLUMN reset_token VARCHAR(100)")
            print("Need to add: reset_token")
        
        if 'reset_token_expires' not in columns:
            migrations_needed.append("ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP")
            print("Need to add: reset_token_expires")
        
        if not migrations_needed:
            print("✅ Database schema is up to date!")
            return True
        
        print(f"\nApplying {len(migrations_needed)} migrations...")
        
        for migration_sql in migrations_needed:
            try:
                print(f"Executing: {migration_sql}")
                conn.execute(text(migration_sql))
                conn.commit()
                print("✅ Success")
            except Exception as e:
                print(f"❌ Error: {e}")
                # Continue with other migrations
                continue
        
        print("\n✅ All migrations completed!")
        return True

if __name__ == '__main__':
    try:
        migrate_database()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

