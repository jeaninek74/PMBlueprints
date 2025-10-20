#!/usr/bin/env python3
"""
Fix the enterprise user's subscription tier in production database
Since we can't directly access the production database, we'll use the app's API
"""
import requests

# Production URL
BASE_URL = "https://www.pmblueprints.net"

# Login as admin or use direct database update via Railway CLI
# For now, let's create a migration script that can be run on Railway

migration_sql = """
-- Fix enterprise user subscription tier
UPDATE users 
SET subscription_tier = 'enterprise' 
WHERE email = 'enterprise@pmblueprints.com';

-- Verify the update
SELECT id, email, first_name, subscription_tier, subscription_status 
FROM users 
WHERE email = 'enterprise@pmblueprints.com';
"""

print("SQL Migration Script to run on Railway:")
print("=" * 60)
print(migration_sql)
print("=" * 60)
print("\nTo execute this on Railway:")
print("1. Go to Railway dashboard")
print("2. Click on the Postgres service")
print("3. Go to 'Data' tab")
print("4. Run the UPDATE query")
print("\nOR use Railway CLI:")
print("railway run psql -c \"UPDATE users SET subscription_tier = 'enterprise' WHERE email = 'enterprise@pmblueprints.com';\"")

