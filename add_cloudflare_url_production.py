"""
Production Database Migration: Add cloudflare_url column to templates table
This script connects to the Supabase production database
"""

import os
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://mmrazymwgqfxkhczqpus.supabase.co"
SUPABASE_KEY = "sbp_e5f182e48846964e6cea5bdb3f59a6513efd7386"

def add_cloudflare_url_column_production():
    """Add cloudflare_url column to templates table in production"""
    
    try:
        # Connect to Supabase
        print("Connecting to Supabase...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Execute SQL to add column
        print("Adding 'cloudflare_url' column to templates table...")
        
        # Note: Supabase uses PostgreSQL, so we use ALTER TABLE syntax
        sql = """
        ALTER TABLE templates 
        ADD COLUMN IF NOT EXISTS cloudflare_url VARCHAR(500);
        """
        
        # Execute via Supabase RPC or direct SQL
        # Since Supabase doesn't directly support ALTER TABLE via Python client,
        # you'll need to run this SQL in the Supabase SQL Editor:
        
        print("\n" + "="*60)
        print("MANUAL STEP REQUIRED:")
        print("="*60)
        print("\nPlease run the following SQL in your Supabase SQL Editor:")
        print("\n" + "-"*60)
        print(sql)
        print("-"*60)
        print("\nSteps:")
        print("1. Go to https://mmrazymwgqfxkhczqpus.supabase.co")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the SQL above")
        print("4. Click 'Run'")
        print("\n" + "="*60)
        
        # Verify by checking if we can query templates
        print("\nVerifying connection to templates table...")
        result = supabase.table('templates').select("*").limit(1).execute()
        
        if result.data:
            print(f"✓ Successfully connected to templates table")
            print(f"✓ Found {len(result.data)} template(s) in database")
            
            # Check if cloudflare_url exists in the first record
            if result.data and 'cloudflare_url' in result.data[0]:
                print("✓ Column 'cloudflare_url' already exists!")
            else:
                print("⚠ Column 'cloudflare_url' not yet added - please run the SQL above")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Production Database Migration")
    print("="*60)
    print()
    
    add_cloudflare_url_column_production()

