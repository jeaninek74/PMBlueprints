#!/usr/bin/env python3
"""Resume uploading remaining screenshots to ImgBB"""

import os
import json
import time
import base64
import requests
from pathlib import Path

# ImgBB API configuration
API_KEY = "2706400918b0e469ebadb69b4bc78a0d"
API_URL = "https://api.imgbb.com/1/upload"

# Directories
SCREENSHOTS_DIR = Path("/home/ubuntu/pmb_repo/static/final_screenshots")
URLS_FILE = Path("/home/ubuntu/pmb_repo/imgbb_urls.json")
LOG_FILE = Path("/home/ubuntu/pmb_repo/upload_log_resume.txt")

def load_existing_urls():
    """Load already uploaded URLs"""
    if URLS_FILE.exists():
        with open(URLS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_urls(urls_dict):
    """Save URLs to JSON file"""
    with open(URLS_FILE, 'w') as f:
        json.dump(urls_dict, f, indent=2)

def upload_image(image_path, api_key):
    """Upload a single image to ImgBB"""
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {
            'key': api_key,
            'image': image_data,
            'name': image_path.stem
        }
        
        response = requests.post(API_URL, data=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data['data']['url']
            else:
                return None
        else:
            return None
            
    except Exception as e:
        print(f"Error uploading {image_path.name}: {e}")
        return None

def main():
    """Main upload function"""
    # Load existing URLs
    existing_urls = load_existing_urls()
    uploaded_count = len(existing_urls)
    
    print(f"Already uploaded: {uploaded_count} images")
    print(f"Starting resume upload...")
    
    # Get all screenshot files
    all_files = sorted(SCREENSHOTS_DIR.glob("*.png"))
    total_files = len(all_files)
    
    print(f"Total screenshot files: {total_files}")
    
    # Filter out already uploaded files
    remaining_files = [f for f in all_files if f.name not in existing_urls]
    print(f"Remaining to upload: {len(remaining_files)}")
    
    success_count = 0
    fail_count = 0
    
    with open(LOG_FILE, 'w') as log:
        log.write(f"Resume Upload Started\n")
        log.write(f"Already uploaded: {uploaded_count}\n")
        log.write(f"Remaining: {len(remaining_files)}\n")
        log.write("=" * 80 + "\n\n")
        
        for idx, image_file in enumerate(remaining_files, 1):
            print(f"Uploading {idx}/{len(remaining_files)}: {image_file.name}")
            
            url = upload_image(image_file, API_KEY)
            
            if url:
                existing_urls[image_file.name] = url
                success_count += 1
                log.write(f"✓ Success: {image_file.name}\n")
                log.write(f"  URL: {url}\n\n")
                log.flush()
                
                # Save progress every 10 uploads
                if success_count % 10 == 0:
                    save_urls(existing_urls)
                    print(f"  Progress saved: {uploaded_count + success_count} total")
            else:
                fail_count += 1
                log.write(f"✗ Failed: {image_file.name}\n\n")
                log.flush()
            
            # Progress update
            if idx % 50 == 0:
                total_uploaded = uploaded_count + success_count
                print(f"Progress: {idx}/{len(remaining_files)} ({success_count} success, {fail_count} failed)")
                print(f"Total uploaded so far: {total_uploaded}/{total_files}")
            
            # Rate limiting - wait 0.5 seconds between uploads
            time.sleep(0.5)
        
        # Final save
        save_urls(existing_urls)
        
        total_uploaded = uploaded_count + success_count
        log.write("\n" + "=" * 80 + "\n")
        log.write(f"UPLOAD COMPLETE\n")
        log.write(f"Total uploaded: {total_uploaded}/{total_files}\n")
        log.write(f"This session: {success_count} success, {fail_count} failed\n")
        
    print(f"\n{'='*80}")
    print(f"UPLOAD COMPLETE!")
    print(f"Total uploaded: {total_uploaded}/{total_files}")
    print(f"This session: {success_count} success, {fail_count} failed")
    print(f"URLs saved to: {URLS_FILE}")
    print(f"Log saved to: {LOG_FILE}")

if __name__ == "__main__":
    main()

