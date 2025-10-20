"""
Upload ALL 955 new screenshots to ImgBB and save URLs
"""

import requests
import base64
import json
import time
import os
from pathlib import Path

API_KEY = "2706400918b0e469ebadb69b4bc78a0d"
SCREENSHOTS_DIR = "/home/ubuntu/pmb_repo/static/screenshots_FULL"
OUTPUT_FILE = "/home/ubuntu/pmb_repo/imgbb_urls_ALL.json"
LOG_FILE = "/home/ubuntu/pmb_repo/upload_ALL_log.txt"

def upload_to_imgbb(image_path, api_key):
    """Upload image to ImgBB and return URL."""
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        response = requests.post(
            'https://api.imgbb.com/1/upload',
            data={
                'key': api_key,
                'image': image_data
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['url']
        else:
            return None
            
    except Exception as e:
        return None

# Get all screenshots
screenshots = sorted(Path(SCREENSHOTS_DIR).glob("*.png"))
print(f"Found {len(screenshots)} screenshots to upload\n")

# Load existing URLs if any
url_mapping = {}
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'r') as f:
        url_mapping = json.load(f)
    print(f"Loaded {len(url_mapping)} existing URLs\n")

# Upload
success = 0
failed = 0
skipped = 0

with open(LOG_FILE, 'w') as log:
    for idx, screenshot in enumerate(screenshots, 1):
        filename = screenshot.name
        
        # Skip if already uploaded
        if filename in url_mapping:
            print(f"[{idx}/{len(screenshots)}] SKIP: {filename} (already uploaded)")
            log.write(f"[{idx}/{len(screenshots)}] SKIP: {filename}\n")
            skipped += 1
            continue
        
        print(f"[{idx}/{len(screenshots)}] Uploading: {filename}")
        log.write(f"[{idx}/{len(screenshots)}] Uploading: {filename}\n")
        log.flush()
        
        url = upload_to_imgbb(str(screenshot), API_KEY)
        
        if url:
            url_mapping[filename] = url
            success += 1
            print(f"  ✓ Success: {url}")
            log.write(f"  ✓ Success: {url}\n")
            
            # Save after each successful upload
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(url_mapping, f, indent=2)
        else:
            failed += 1
            print(f"  ✗ Failed")
            log.write(f"  ✗ Failed\n")
        
        log.flush()
        
        # Rate limiting - wait between uploads
        if idx < len(screenshots):
            time.sleep(0.5)
        
        # Progress update every 50
        if idx % 50 == 0:
            print(f"\n--- Progress: {idx}/{len(screenshots)} ({success} success, {failed} failed, {skipped} skipped) ---\n")
            log.write(f"\n--- Progress: {idx}/{len(screenshots)} ({success} success, {failed} failed, {skipped} skipped) ---\n")
            log.flush()

print(f"\n✅ COMPLETE!")
print(f"Success: {success}")
print(f"Failed: {failed}")
print(f"Skipped: {skipped}")
print(f"Total URLs: {len(url_mapping)}")
print(f"Saved to: {OUTPUT_FILE}")

