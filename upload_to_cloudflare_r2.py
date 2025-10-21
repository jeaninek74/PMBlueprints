#!/usr/bin/env python3
"""
Cloudflare R2 Upload Script for PM Blueprints Screenshots
Uploads all screenshots to Cloudflare R2 and updates the database with CDN URLs
"""

import os
import sys
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cloudflare R2 Credentials
R2_ACCOUNT_ID = "5e687ea57869abd16d33fa2f3a69af50"
R2_ACCESS_KEY_ID = "3aae1723b00b01b111c084e6cdac0a06"
R2_SECRET_ACCESS_KEY = "b9e28a118ef90e6eabe40aded548e4d284d85f6737806227cc8f349b068d1d4a"
R2_ENDPOINT = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
R2_BUCKET_NAME = "pmblueprints-screenshots"
R2_PUBLIC_URL = "https://pub-88e6ef534d3c4ce76zafcdd6b325604c.r2.dev"

# Database connection (Supabase PostgreSQL)
DB_HOST = "mmrazymwgqfxkhczqpus.supabase.co"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "sbp_e5f182e48846964e6cea5bdb3f59a6513efd7386"
DB_PORT = "5432"

# Screenshot directory
SCREENSHOT_DIR = Path("static/screenshots_new")

def get_r2_client():
    """Create and return Cloudflare R2 S3 client"""
    return boto3.client(
        's3',
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto'
    )

def upload_to_r2(file_path, object_name):
    """
    Upload a file to Cloudflare R2
    Returns the public URL if successful, None otherwise
    """
    s3_client = get_r2_client()
    
    try:
        # Upload file with public-read ACL
        s3_client.upload_file(
            str(file_path),
            R2_BUCKET_NAME,
            object_name,
            ExtraArgs={
                'ContentType': 'image/png',
                'CacheControl': 'public, max-age=31536000'  # Cache for 1 year
            }
        )
        
        # Construct public URL
        public_url = f"{R2_PUBLIC_URL}/{object_name}"
        return public_url
        
    except ClientError as e:
        print(f"  ❌ Error uploading {object_name}: {e}")
        return None

def get_db_connection():
    """Create and return database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def update_template_url(template_name, cloudflare_url):
    """
    Update the template's cloudflare_url in the database
    Returns True if successful, False otherwise
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Update the cloudflare_url field
        query = """
        UPDATE templates 
        SET cloudflare_url = %s 
        WHERE name = %s OR file_path LIKE %s
        """
        
        cursor.execute(query, (cloudflare_url, template_name, f"%{template_name}%"))
        conn.commit()
        
        rows_updated = cursor.rowcount
        cursor.close()
        conn.close()
        
        return rows_updated > 0
        
    except Exception as e:
        print(f"  ❌ Database update error: {e}")
        if conn:
            conn.close()
        return False

def main():
    """Main function to upload all screenshots and update database"""
    
    print("=" * 70)
    print("PM BLUEPRINTS - CLOUDFLARE R2 UPLOAD & DATABASE UPDATE")
    print("=" * 70)
    print()
    
    # Check if screenshot directory exists
    if not SCREENSHOT_DIR.exists():
        print(f"❌ Screenshot directory not found: {SCREENSHOT_DIR}")
        print("   Please run capture_screenshots.py first")
        return 1
    
    # Get all PNG files
    screenshot_files = list(SCREENSHOT_DIR.glob("*.png"))
    
    if not screenshot_files:
        print(f"❌ No screenshot files found in {SCREENSHOT_DIR}")
        return 1
    
    print(f"📁 Found {len(screenshot_files)} screenshots to upload")
    print(f"☁️  Uploading to Cloudflare R2 bucket: {R2_BUCKET_NAME}")
    print(f"🔗 Public URL base: {R2_PUBLIC_URL}")
    print()
    
    # Test database connection
    print("🔌 Testing database connection...")
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database. Please check credentials.")
        return 1
    conn.close()
    print("✅ Database connection successful")
    print()
    
    # Upload files
    success_count = 0
    error_count = 0
    db_update_count = 0
    
    print("Uploading screenshots...")
    print("-" * 70)
    
    for idx, screenshot_file in enumerate(screenshot_files, 1):
        template_name = screenshot_file.stem
        object_name = screenshot_file.name
        
        print(f"[{idx}/{len(screenshot_files)}] {screenshot_file.name}")
        
        # Upload to R2
        public_url = upload_to_r2(screenshot_file, object_name)
        
        if public_url:
            print(f"  ✅ Uploaded: {public_url}")
            success_count += 1
            
            # Update database
            if update_template_url(template_name, public_url):
                print(f"  ✅ Database updated for: {template_name}")
                db_update_count += 1
            else:
                print(f"  ⚠️  Database update failed (template may not exist): {template_name}")
        else:
            error_count += 1
        
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully uploaded: {success_count} screenshots")
    print(f"✅ Database records updated: {db_update_count}")
    print(f"❌ Upload errors: {error_count}")
    print()
    
    if success_count > 0:
        print("🎉 Screenshots are now served from Cloudflare R2 CDN!")
        print(f"🔗 Access them at: {R2_PUBLIC_URL}/[filename].png")
    
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

