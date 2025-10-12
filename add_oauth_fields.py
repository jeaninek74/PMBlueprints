"""
Add OAuth fields to User model
Run this script to add oauth_provider, oauth_id, and email_verified fields
"""
import os
from sqlalchemy import create_engine, text

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    exit(1)

engine = create_engine(DATABASE_URL)

# SQL statements to add OAuth fields
sql_statements = [
    """
    ALTER TABLE "user" 
    ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50);
    """,
    """
    ALTER TABLE "user" 
    ADD COLUMN IF NOT EXISTS oauth_id VARCHAR(255);
    """,
    """
    ALTER TABLE "user" 
    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_user_oauth 
    ON "user" (oauth_provider, oauth_id);
    """
]

print("Adding OAuth fields to User table...")

try:
    with engine.connect() as conn:
        for sql in sql_statements:
            conn.execute(text(sql))
            conn.commit()
    
    print("✅ OAuth fields added successfully!")
    print("   - oauth_provider (VARCHAR(50))")
    print("   - oauth_id (VARCHAR(255))")
    print("   - email_verified (BOOLEAN)")
    print("   - Index on (oauth_provider, oauth_id)")
    
except Exception as e:
    print(f"❌ Error adding OAuth fields: {str(e)}")
    exit(1)

