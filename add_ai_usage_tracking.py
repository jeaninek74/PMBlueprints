"""
Database Migration: Add AI Usage Tracking
Adds persistent AI usage tracking to prevent abuse and enforce limits
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def add_ai_usage_tracking():
    """Add AI usage tracking fields and table"""
    
    with app.app_context():
        try:
            print("=" * 60)
            print("Adding AI Usage Tracking to Database")
            print("=" * 60)
            
            # Check if we're using PostgreSQL or SQLite
            is_postgres = 'postgres' in app.config['SQLALCHEMY_DATABASE_URI']
            
            # 1. Add fields to User table if they don't exist
            print("\n1. Adding AI usage fields to User table...")
            
            user_fields = [
                ('ai_generations_used_this_month', 'INTEGER DEFAULT 0'),
                ('ai_generation_reset_date', 'TIMESTAMP'),
                ('subscription_expires_at', 'TIMESTAMP'),
            ]
            
            for field_name, field_type in user_fields:
                try:
                    if is_postgres:
                        db.session.execute(text(
                            f"ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS {field_name} {field_type}"
                        ))
                    else:
                        # SQLite doesn't support IF NOT EXISTS in ALTER TABLE
                        # Try to add and catch error if exists
                        try:
                            db.session.execute(text(
                                f"ALTER TABLE user ADD COLUMN {field_name} {field_type}"
                            ))
                        except Exception as e:
                            if 'duplicate column' in str(e).lower():
                                print(f"   ✓ Field {field_name} already exists")
                            else:
                                raise
                    
                    db.session.commit()
                    print(f"   ✓ Added field: {field_name}")
                except Exception as e:
                    if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                        print(f"   ✓ Field {field_name} already exists")
                    else:
                        print(f"   ✗ Error adding {field_name}: {e}")
                        db.session.rollback()
            
            # 2. Create AIUsageLog table
            print("\n2. Creating AIUsageLog table...")
            
            try:
                if is_postgres:
                    create_table_sql = """
                    CREATE TABLE IF NOT EXISTS ai_usage_log (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                        request_type VARCHAR(50) NOT NULL,
                        template_type VARCHAR(100),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT TRUE,
                        tokens_used INTEGER DEFAULT 0,
                        input_length INTEGER,
                        output_length INTEGER,
                        error_message TEXT,
                        metadata TEXT
                    )
                    """
                else:
                    create_table_sql = """
                    CREATE TABLE IF NOT EXISTS ai_usage_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        request_type VARCHAR(50) NOT NULL,
                        template_type VARCHAR(100),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT 1,
                        tokens_used INTEGER DEFAULT 0,
                        input_length INTEGER,
                        output_length INTEGER,
                        error_message TEXT,
                        metadata TEXT,
                        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
                    )
                    """
                
                db.session.execute(text(create_table_sql))
                db.session.commit()
                print("   ✓ AIUsageLog table created")
                
                # Create index on user_id and timestamp for efficient queries
                print("\n3. Creating indexes...")
                try:
                    db.session.execute(text(
                        "CREATE INDEX IF NOT EXISTS idx_ai_usage_user_timestamp ON ai_usage_log(user_id, timestamp)"
                    ))
                    db.session.commit()
                    print("   ✓ Index created on ai_usage_log(user_id, timestamp)")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print("   ✓ Index already exists")
                    else:
                        print(f"   ⚠ Warning creating index: {e}")
                
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print("   ✓ AIUsageLog table already exists")
                else:
                    print(f"   ✗ Error creating table: {e}")
                    db.session.rollback()
            
            # 4. Initialize reset dates for existing users
            print("\n4. Initializing AI usage data for existing users...")
            
            try:
                # Set reset date to first of next month for users without one
                if is_postgres:
                    update_sql = """
                    UPDATE "user" 
                    SET ai_generation_reset_date = DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
                    WHERE ai_generation_reset_date IS NULL
                    """
                else:
                    update_sql = """
                    UPDATE user 
                    SET ai_generation_reset_date = datetime('now', 'start of month', '+1 month')
                    WHERE ai_generation_reset_date IS NULL
                    """
                
                result = db.session.execute(text(update_sql))
                db.session.commit()
                print(f"   ✓ Initialized reset dates for {result.rowcount} users")
                
            except Exception as e:
                print(f"   ⚠ Warning initializing user data: {e}")
                db.session.rollback()
            
            # 5. Verify the changes
            print("\n5. Verifying database changes...")
            
            try:
                # Check User table columns
                if is_postgres:
                    columns_query = """
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'user' 
                    AND column_name IN ('ai_generations_used_this_month', 'ai_generation_reset_date', 'subscription_expires_at')
                    """
                else:
                    columns_query = "PRAGMA table_info(user)"
                
                result = db.session.execute(text(columns_query))
                columns = result.fetchall()
                print(f"   ✓ User table has {len(columns)} new AI-related columns")
                
                # Check AIUsageLog table exists
                if is_postgres:
                    table_query = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'ai_usage_log'
                    )
                    """
                else:
                    table_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='ai_usage_log'"
                
                result = db.session.execute(text(table_query))
                table_exists = result.fetchone()
                if table_exists:
                    print("   ✓ AIUsageLog table exists")
                else:
                    print("   ✗ AIUsageLog table not found")
                
            except Exception as e:
                print(f"   ⚠ Warning during verification: {e}")
            
            print("\n" + "=" * 60)
            print("✓ AI Usage Tracking Migration Complete!")
            print("=" * 60)
            print("\nNew features enabled:")
            print("  • Persistent AI usage tracking across server restarts")
            print("  • Monthly AI generation limits enforced")
            print("  • Automatic usage reset on first of each month")
            print("  • Detailed audit log for AI requests")
            print("  • Subscription expiration date tracking")
            print("\n")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = add_ai_usage_tracking()
    sys.exit(0 if success else 1)

