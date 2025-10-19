"""
Database Migration: Add reset_token fields to users table
Run this once to add password reset functionality
"""

import os
import psycopg2
from urllib.parse import urlparse

def migrate_database():
    """Add reset_token and reset_token_expires columns to users table"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    # Parse database URL
    result = urlparse(database_url)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name IN ('reset_token', 'reset_token_expires')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if 'reset_token' in existing_columns and 'reset_token_expires' in existing_columns:
            print("✅ Columns already exist. No migration needed.")
            cursor.close()
            conn.close()
            return True
        
        # Add reset_token column if it doesn't exist
        if 'reset_token' not in existing_columns:
            print("Adding reset_token column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN reset_token VARCHAR(100)
            """)
            print("✅ reset_token column added")
        
        # Add reset_token_expires column if it doesn't exist
        if 'reset_token_expires' not in existing_columns:
            print("Adding reset_token_expires column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN reset_token_expires TIMESTAMP
            """)
            print("✅ reset_token_expires column added")
        
        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("Starting database migration...")
    print("Adding password reset fields to users table...")
    success = migrate_database()
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")

