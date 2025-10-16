#!/usr/bin/env python3.11
"""
Initialize Railway Database and Import Production Templates
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import execute_values

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

print(f"Connecting to database...")
print(f"Database URL: {DATABASE_URL[:30]}...")

# Connect to database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create tables
print("\n1. Creating database tables...")

# Drop existing tables if they exist (for clean setup)
cur.execute("DROP TABLE IF EXISTS download CASCADE")
cur.execute("DROP TABLE IF EXISTS favorite CASCADE")
cur.execute("DROP TABLE IF EXISTS template CASCADE")
cur.execute("DROP TABLE IF EXISTS user CASCADE")

# Create User table
cur.execute("""
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    company VARCHAR(100),
    subscription_plan VARCHAR(20) DEFAULT 'free',
    subscription_status VARCHAR(20) DEFAULT 'active',
    stripe_customer_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    downloads_used INTEGER DEFAULT 0,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    platform_tokens TEXT,
    openai_api_key VARCHAR(255),
    openai_usage_count INTEGER DEFAULT 0
)
""")
print("✓ Created user table")

# Create Template table
cur.execute("""
CREATE TABLE template (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    industry VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(255),
    preview_image VARCHAR(255),
    downloads INTEGER DEFAULT 0,
    rating FLOAT DEFAULT 4.5,
    tags TEXT,
    file_size INTEGER,
    has_formulas BOOLEAN DEFAULT FALSE,
    has_fields BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_premium BOOLEAN DEFAULT FALSE
)
""")
print("✓ Created template table")

# Create Download table
cur.execute("""
CREATE TABLE download (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    template_id INTEGER NOT NULL REFERENCES template(id),
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
print("✓ Created download table")

# Create Favorite table
cur.execute("""
CREATE TABLE favorite (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    template_id INTEGER NOT NULL REFERENCES template(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
print("✓ Created favorite table")

# Commit table creation
conn.commit()
print("\n✓ All tables created successfully")

# Load templates from catalog
print("\n2. Loading templates from catalog...")
catalog_path = '/home/ubuntu/pmb_repo/templates_catalog.json'
with open(catalog_path, 'r') as f:
    templates = json.load(f)

print(f"Found {len(templates)} templates in catalog")

# Prepare template data for bulk insert
template_data = []
for template in templates:
    template_data.append((
        template.get('name', ''),
        template.get('description', ''),
        template.get('industry', ''),
        template.get('category', ''),
        template.get('file_type', ''),
        template.get('filename', ''),
        f"/templates/{template.get('filename', '')}" if template.get('filename') else None,
        None,  # preview_image
        0,  # downloads
        4.5,  # rating
        ','.join(template.get('tags', [])) if template.get('tags') else '',
        template.get('file_size', 0),
        template.get('has_formulas', False),
        template.get('has_fields', False),
        False  # is_premium
    ))

# Bulk insert templates
print("\n3. Inserting templates into database...")
insert_query = """
INSERT INTO template (
    name, description, industry, category, file_type, filename, file_path,
    preview_image, downloads, rating, tags, file_size, has_formulas, has_fields, is_premium
) VALUES %s
"""

execute_values(cur, insert_query, template_data)
conn.commit()

print(f"✓ Inserted {len(template_data)} templates")

# Verify insertion
cur.execute("SELECT COUNT(*) FROM template")
count = cur.fetchone()[0]
print(f"\n✓ Database now contains {count} templates")

# Show sample templates
cur.execute("SELECT id, name, industry, category, file_type FROM template LIMIT 5")
print("\nSample templates:")
for row in cur.fetchall():
    print(f"  - {row[0]}: {row[1]} ({row[2]}, {row[3]}, {row[4]})")

# Close connection
cur.close()
conn.close()

print("\n" + "="*60)
print("✓ DATABASE INITIALIZATION COMPLETE")
print("="*60)
print(f"\nTotal templates imported: {count}")
print("Database is ready for production use")
print("\nNext steps:")
print("1. Test template downloads")
print("2. Configure domain DNS")
print("3. Verify end-to-end functionality")

