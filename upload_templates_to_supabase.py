#!/usr/bin/env python3
"""
Upload Template Files to Supabase Storage
==========================================

This script uploads all template files from static/templates/ to Supabase Storage.

Prerequisites:
1. Supabase project created
2. Storage bucket 'templates' created (public)
3. Environment variables set:
   - SUPABASE_URL
   - SUPABASE_KEY

Usage:
    python3 upload_templates_to_supabase.py

This will upload all 955 templates to Supabase Storage.
"""

import os
import sys
from pathlib import Path

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Error: supabase package not installed")
    print("Run: pip3 install supabase")
    sys.exit(1)

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
BUCKET_NAME = 'templates'
TEMPLATE_DIR = 'static/templates'

# File type mappings
MIME_TYPES = {
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.pdf': 'application/pdf',
    '.xls': 'application/vnd.ms-excel',
    '.doc': 'application/msword',
    '.ppt': 'application/vnd.ms-powerpoint'
}

def main():
    print("=" * 60)
    print("PMBlueprints Template Upload to Supabase Storage")
    print("=" * 60)
    print()
    
    # Validate environment variables
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Missing environment variables")
        print("Required:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_KEY (or SUPABASE_SERVICE_KEY)")
        print()
        print("Set them in your environment:")
        print("  export SUPABASE_URL='your-project-url'")
        print("  export SUPABASE_KEY='your-anon-key'")
        sys.exit(1)
    
    print(f"✅ Supabase URL: {SUPABASE_URL}")
    print(f"✅ Bucket: {BUCKET_NAME}")
    print()
    
    # Initialize Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)
    
    # Check if template directory exists
    template_path = Path(TEMPLATE_DIR)
    if not template_path.exists():
        print(f"❌ Error: Template directory not found: {TEMPLATE_DIR}")
        sys.exit(1)
    
    # Get list of template files
    template_files = list(template_path.glob('*'))
    template_files = [f for f in template_files if f.is_file()]
    
    print(f"📁 Found {len(template_files)} template files")
    print()
    
    # Confirm upload
    response = input(f"Upload {len(template_files)} files to Supabase Storage? (y/n): ")
    if response.lower() != 'y':
        print("❌ Upload cancelled")
        sys.exit(0)
    
    print()
    print("Starting upload...")
    print("-" * 60)
    
    # Upload files
    uploaded = 0
    failed = 0
    skipped = 0
    
    for i, filepath in enumerate(template_files, 1):
        filename = filepath.name
        file_ext = filepath.suffix.lower()
        mime_type = MIME_TYPES.get(file_ext, 'application/octet-stream')
        
        try:
            # Read file
            with open(filepath, 'rb') as f:
                file_data = f.read()
            
            # Upload to Supabase
            result = supabase.storage.from_(BUCKET_NAME).upload(
                path=filename,
                file=file_data,
                file_options={"content-type": mime_type}
            )
            
            uploaded += 1
            print(f"[{i}/{len(template_files)}] ✅ {filename}")
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if file already exists
            if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                skipped += 1
                print(f"[{i}/{len(template_files)}] ⏭️  {filename} (already exists)")
            else:
                failed += 1
                print(f"[{i}/{len(template_files)}] ❌ {filename}")
                print(f"    Error: {error_msg}")
    
    # Summary
    print()
    print("=" * 60)
    print("Upload Summary")
    print("=" * 60)
    print(f"✅ Uploaded: {uploaded}")
    print(f"⏭️  Skipped: {skipped} (already exist)")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(template_files)}")
    print()
    
    if failed == 0:
        print("🎉 All templates uploaded successfully!")
        print()
        print("Next steps:")
        print("1. Update routes/templates.py to use Supabase storage")
        print("2. Deploy the changes")
        print("3. Test template downloads")
    else:
        print(f"⚠️  {failed} files failed to upload. Please check errors above.")
    
    print()

if __name__ == '__main__':
    main()

