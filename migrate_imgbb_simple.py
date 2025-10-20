"""
Simple migration to add imgbb_url column - works with Railway
Run with: railway run python3 migrate_imgbb_simple.py
"""

import os
import sys

def run_migration():
    """Add imgbb_url column using raw SQL"""
    try:
        # Import after environment is loaded
        import psycopg2
        
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        if not DATABASE_URL:
            print("❌ DATABASE_URL not found in environment")
            return False
        
        # Fix postgres:// to postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        print(f"🔌 Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check if column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='templates' AND column_name='imgbb_url'
        """)
        
        if cur.fetchone():
            print("✅ Column 'imgbb_url' already exists")
            cur.close()
            conn.close()
            return True
        
        # Add column
        print("📝 Adding imgbb_url column...")
        cur.execute("ALTER TABLE templates ADD COLUMN imgbb_url VARCHAR(500)")
        conn.commit()
        
        print("✅ Migration successful!")
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)

