"""
Add platform integration fields to User model
Run this to update the database schema
"""
import os
from app import app, db

def add_integration_fields():
    """Add platform_tokens and openai_usage_count fields to users table"""
    with app.app_context():
        try:
            # Check if we're using PostgreSQL (Neon)
            db_url = os.getenv('DATABASE_URL', '')
            
            if 'postgres' in db_url:
                # PostgreSQL ALTER TABLE commands
                with db.engine.connect() as conn:
                    # Add platform_tokens column if it doesn't exist
                    conn.execute(db.text("""
                        ALTER TABLE "user" 
                        ADD COLUMN IF NOT EXISTS platform_tokens TEXT;
                    """))
                    
                    # Add openai_usage_count column if it doesn't exist
                    conn.execute(db.text("""
                        ALTER TABLE "user" 
                        ADD COLUMN IF NOT EXISTS openai_usage_count INTEGER DEFAULT 0;
                    """))
                    
                    conn.commit()
                    print("✅ Successfully added integration fields to User table (PostgreSQL)")
            else:
                # SQLite - use db.create_all() which adds missing columns
                db.create_all()
                print("✅ Successfully updated User table schema (SQLite)")
                
        except Exception as e:
            print(f"❌ Error adding integration fields: {e}")
            print("Note: If columns already exist, this error can be ignored")

if __name__ == '__main__':
    add_integration_fields()

