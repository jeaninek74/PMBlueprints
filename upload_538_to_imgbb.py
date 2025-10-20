"""
Upload FIRST 538 NEW screenshots to ImgBB
"""

import requests
import base64
import json
import time
import os
from pathlib import Path

API_KEY = "2706400918b0e469ebadb69b4bc78a0d"
SCREENSHOTS_DIR = "/home/ubuntu/pmb_repo/static/screenshots_FULL"
OUTPUT_FILE = "/home/ubuntu/pmb_repo/imgbb_urls_538.json"
LOG_FILE = "/home/ubuntu/pmb_repo/upload_538_log.txt"

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

# Get all screenshots and sort
screenshots = sorted(Path(SCREENSHOTS_DIR).glob("*.png"))
print(f"Found {len(screenshots)} total screenshots")
print(f"Uploading FIRST 538 screenshots\n")

# Take only first 538
screenshots_to_upload = screenshots[:538]

url_mapping = {}
success = 0
failed = 0

with open(LOG_FILE, 'w') as log:
    for idx, screenshot in enumerate(screenshots_to_upload, 1):
        filename = screenshot.name
        
        print(f"[{idx}/538] Uploading: {filename}")
        log.write(f"[{idx}/538] Uploading: {filename}\n")
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
            
            # Stop if we hit rate limit (multiple consecutive failures)
            if failed > 5 and success < 10:
                print(f"\n⚠️  Hit rate limit early, stopping...")
                log.write(f"\n⚠️  Hit rate limit early, stopping...\n")
                break
        
        log.flush()
        
        # Rate limiting - wait between uploads
        if idx < len(screenshots_to_upload):
            time.sleep(0.5)
        
        # Progress update every 50
        if idx % 50 == 0:
            print(f"\n--- Progress: {idx}/538 ({success} success, {failed} failed) ---\n")
            log.write(f"\n--- Progress: {idx}/538 ({success} success, {failed} failed) ---\n")
            log.flush()

print(f"\n✅ UPLOAD COMPLETE!")
print(f"Success: {success}")
print(f"Failed: {failed}")
print(f"Total URLs saved: {len(url_mapping)}")
print(f"Saved to: {OUTPUT_FILE}")

with open(LOG_FILE, 'a') as log:
    log.write(f"\n✅ UPLOAD COMPLETE!\n")
    log.write(f"Success: {success}\n")
    log.write(f"Failed: {failed}\n")
    log.write(f"Total URLs: {len(url_mapping)}\n")

