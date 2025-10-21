"""
Database Migration: Add cloudflare_url column to templates table
Run this script to add the new cloudflare_url field to existing database
"""

import sqlite3
import os

# Database path
DB_PATH = 'pmblueprints.db'

def add_cloudflare_url_column():
    """Add cloudflare_url column to templates table"""
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(templates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'cloudflare_url' in columns:
            print("✓ Column 'cloudflare_url' already exists in templates table")
            conn.close()
            return True
        
        # Add the new column
        print("Adding 'cloudflare_url' column to templates table...")
        cursor.execute("""
            ALTER TABLE templates 
            ADD COLUMN cloudflare_url VARCHAR(500)
        """)
        
        conn.commit()
        print("✓ Successfully added 'cloudflare_url' column to templates table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(templates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'cloudflare_url' in columns:
            print("✓ Migration verified successfully")
            
            # Show current schema
            print("\nCurrent templates table schema:")
            cursor.execute("PRAGMA table_info(templates)")
            for column in cursor.fetchall():
                print(f"  - {column[1]} ({column[2]})")
        else:
            print("✗ Migration verification failed")
            return False
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Database Migration: Add cloudflare_url column")
    print("="*60)
    print()
    
    success = add_cloudflare_url_column()
    
    print()
    if success:
        print("="*60)
        print("Migration completed successfully!")
        print("="*60)
    else:
        print("="*60)
        print("Migration failed!")
        print("="*60)

