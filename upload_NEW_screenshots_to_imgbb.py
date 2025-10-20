#!/usr/bin/env python3
"""
Upload NEW screenshots (with colors) to ImgBB CDN
Handles rate limiting with delays between uploads
"""
import os
import sys
import time
import requests
import json
from pathlib import Path

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 1)

# ImgBB API key
IMGBB_API_KEY = "2706400918b0e469ebadb69b4bc78a0d"  # Correct ImgBB API key
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Paths
SCREENSHOTS_DIR = "/home/ubuntu/pmb_repo/static/screenshots_FULL"
OUTPUT_JSON = "/home/ubuntu/pmb_repo/imgbb_urls_NEW.json"
LOG_FILE = "/home/ubuntu/pmb_repo/upload_NEW_log.txt"

# Rate limiting
DELAY_BETWEEN_UPLOADS = 1  # seconds (reduced for faster upload)
MAX_RETRIES = 2

def upload_to_imgbb(image_path, api_key):
    """Upload a single image to ImgBB"""
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'key': api_key}
            response = requests.post(IMGBB_UPLOAD_URL, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return {
                        'success': True,
                        'url': result['data']['url'],
                        'display_url': result['data']['display_url'],
                        'delete_url': result['data']['delete_url'],
                        'size': result['data']['size']
                    }
            
            return {'success': False, 'error': response.text}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    # Get all screenshot files
    screenshots = sorted([f for f in os.listdir(SCREENSHOTS_DIR) if f.endswith('.png')])
    total = len(screenshots)
    
    print(f"Found {total} screenshots to upload")
    print(f"Output will be saved to: {OUTPUT_JSON}")
    print(f"Log will be saved to: {LOG_FILE}")
    print("=" * 80)
    
    # Load existing URLs if any
    imgbb_urls = {}
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, 'r') as f:
            imgbb_urls = json.load(f)
        print(f"Loaded {len(imgbb_urls)} existing URLs")
    
    # Open log file
    with open(LOG_FILE, 'w') as log:
        log.write(f"ImgBB Upload Log - NEW Screenshots\\n")
        log.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n")
        log.write(f"Total files: {total}\\n")
        log.write("=" * 80 + "\\n")
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for idx, filename in enumerate(screenshots, 1):
            # Skip if already uploaded
            if filename in imgbb_urls:
                print(f"[{idx}/{total}] Skipping (already uploaded): {filename}")
                log.write(f"[{idx}/{total}] Skipping: {filename}\\n")
                skipped_count += 1
                continue
            
            print(f"[{idx}/{total}] Uploading: {filename}")
            log.write(f"[{idx}/{total}] Uploading: {filename}\\n")
            
            image_path = os.path.join(SCREENSHOTS_DIR, filename)
            
            # Try uploading with retries
            retry_count = 0
            while retry_count < MAX_RETRIES:
                result = upload_to_imgbb(image_path, IMGBB_API_KEY)
                
                if result['success']:
                    imgbb_urls[filename] = {
                        'filename': filename,
                        'url': result['url'],
                        'display_url': result['display_url'],
                        'delete_url': result['delete_url'],
                        'size': result['size']
                    }
                    print(f"  ✓ Success: {result['display_url']}")
                    log.write(f"  ✓ Success: {result['display_url']}\\n")
                    success_count += 1
                    
                    # Save progress after each successful upload
                    with open(OUTPUT_JSON, 'w') as f:
                        json.dump(imgbb_urls, f, indent=2)
                    
                    break
                else:
                    retry_count += 1
                    error_msg = result.get('error', 'Unknown error')
                    print(f"  ✗ Failed (attempt {retry_count}/{MAX_RETRIES}): {error_msg}")
                    log.write(f"  ✗ Failed (attempt {retry_count}/{MAX_RETRIES}): {error_msg}\\n")
                    
                    if retry_count < MAX_RETRIES:
                        time.sleep(DELAY_BETWEEN_UPLOADS * 2)  # Longer delay on retry
            
            if retry_count >= MAX_RETRIES:
                failed_count += 1
            
            # Progress update every 10 files
            if idx % 10 == 0:
                print(f"--- Progress: {idx}/{total} ({success_count} success, {failed_count} failed, {skipped_count} skipped) ---")
                log.write(f"--- Progress: {idx}/{total} ({success_count} success, {failed_count} failed, {skipped_count} skipped) ---\\n")
            
            # Rate limiting delay
            time.sleep(DELAY_BETWEEN_UPLOADS)
        
        # Final summary
        print("=" * 80)
        print(f"Upload complete!")
        print(f"  Success: {success_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Total: {total}")
        print(f"\\nURLs saved to: {OUTPUT_JSON}")
        
        log.write("=" * 80 + "\\n")
        log.write(f"Upload complete!\\n")
        log.write(f"  Success: {success_count}\\n")
        log.write(f"  Failed: {failed_count}\\n")
        log.write(f"  Skipped: {skipped_count}\\n")
        log.write(f"  Total: {total}\\n")
        log.write(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n")

if __name__ == '__main__':
    main()

