"""
Add OAuth integration fields to IntegrationSettings table
Run this migration to add OAuth token storage fields
"""

import os
import sys
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')

if not DATABASE_URL:
    print("Error: DATABASE_URL or POSTGRES_URL environment variable not set")
    sys.exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

# SQL to add OAuth fields
sql_commands = [
    # Monday.com OAuth fields
    """
    ALTER TABLE integration_settings 
    ADD COLUMN IF NOT EXISTS monday_access_token TEXT,
    ADD COLUMN IF NOT EXISTS monday_refresh_token TEXT,
    ADD COLUMN IF NOT EXISTS monday_connected BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS monday_connected_at TIMESTAMP;
    """,
    
    # Smartsheet OAuth fields
    """
    ALTER TABLE integration_settings 
    ADD COLUMN IF NOT EXISTS smartsheet_access_token TEXT,
    ADD COLUMN IF NOT EXISTS smartsheet_refresh_token TEXT,
    ADD COLUMN IF NOT EXISTS smartsheet_connected BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS smartsheet_connected_at TIMESTAMP;
    """,
    
    # Google Sheets OAuth fields
    """
    ALTER TABLE integration_settings 
    ADD COLUMN IF NOT EXISTS google_access_token TEXT,
    ADD COLUMN IF NOT EXISTS google_refresh_token TEXT,
    ADD COLUMN IF NOT EXISTS google_connected BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS google_connected_at TIMESTAMP;
    """,
    
    # Microsoft 365 OAuth fields
    """
    ALTER TABLE integration_settings 
    ADD COLUMN IF NOT EXISTS microsoft_access_token TEXT,
    ADD COLUMN IF NOT EXISTS microsoft_refresh_token TEXT,
    ADD COLUMN IF NOT EXISTS microsoft_connected BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS microsoft_connected_at TIMESTAMP;
    """
]

print("Adding OAuth integration fields to database...")

try:
    with engine.connect() as conn:
        for sql in sql_commands:
            print(f"Executing: {sql[:50]}...")
            conn.execute(text(sql))
            conn.commit()
    
    print("✓ OAuth integration fields added successfully!")
    print("\nNew fields added:")
    print("  - monday_access_token, monday_refresh_token, monday_connected, monday_connected_at")
    print("  - smartsheet_access_token, smartsheet_refresh_token, smartsheet_connected, smartsheet_connected_at")
    print("  - google_access_token, google_refresh_token, google_connected, google_connected_at")
    print("  - microsoft_access_token, microsoft_refresh_token, microsoft_connected, microsoft_connected_at")
    
except Exception as e:
    print(f"✗ Error adding OAuth fields: {str(e)}")
    sys.exit(1)

