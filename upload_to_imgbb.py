#!/usr/bin/env python3
"""
Upload all 955 template screenshots to ImgBB CDN and collect hosted URLs.
"""

import requests
import os
import json
import time
from pathlib import Path
import base64

# ImgBB API configuration
IMGBB_API_KEY = "2706400918b0e469ebadb69b4bc78a0d"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Directories
SCREENSHOTS_DIR = "/home/ubuntu/pmb_repo/static/final_screenshots"
OUTPUT_FILE = "/home/ubuntu/pmb_repo/imgbb_urls.json"

def upload_image_to_imgbb(image_path, api_key):
    """
    Upload a single image to ImgBB and return the hosted URL.
    
    Args:
        image_path: Path to the image file
        api_key: ImgBB API key
        
    Returns:
        dict with image info or None if failed
    """
    try:
        # Read image and encode to base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Prepare payload
        payload = {
            'key': api_key,
            'image': image_data,
            'name': os.path.basename(image_path)
        }
        
        # Upload to ImgBB
        response = requests.post(IMGBB_UPLOAD_URL, data=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {
                    'filename': os.path.basename(image_path),
                    'url': result['data']['url'],
                    'display_url': result['data']['display_url'],
                    'delete_url': result['data']['delete_url'],
                    'size': result['data']['size']
                }
        
        print(f"  Error: {response.status_code} - {response.text[:100]}")
        return None
        
    except Exception as e:
        print(f"  Exception: {e}")
        return None


def main():
    """Upload all screenshots to ImgBB."""
    print("=" * 80)
    print("UPLOADING SCREENSHOTS TO IMGBB CDN")
    print("=" * 80)
    print(f"Screenshots directory: {SCREENSHOTS_DIR}")
    print(f"Output file: {OUTPUT_FILE}")
    print()
    
    # Get all screenshot files
    screenshot_files = sorted(Path(SCREENSHOTS_DIR).glob("*.png"))
    total_files = len(screenshot_files)
    
    print(f"Found {total_files} screenshot files")
    print()
    
    # Track results
    uploaded_urls = {}
    success_count = 0
    failed_count = 0
    
    # Upload each file
    for idx, screenshot_path in enumerate(screenshot_files, 1):
        filename = screenshot_path.name
        
        print(f"[{idx}/{total_files}] Uploading: {filename}")
        
        result = upload_image_to_imgbb(str(screenshot_path), IMGBB_API_KEY)
        
        if result:
            uploaded_urls[filename] = result
            success_count += 1
            print(f"  ✓ Success: {result['display_url']}")
        else:
            failed_count += 1
            print(f"  ✗ Failed")
        
        # Progress update every 50 files
        if idx % 50 == 0:
            print()
            print(f"Progress: {idx}/{total_files} ({success_count} success, {failed_count} failed)")
            print()
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Save results to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(uploaded_urls, f, indent=2)
    
    print()
    print("=" * 80)
    print("UPLOAD COMPLETE")
    print("=" * 80)
    print(f"Total files: {total_files}")
    print(f"Successful uploads: {success_count}")
    print(f"Failed uploads: {failed_count}")
    print(f"URLs saved to: {OUTPUT_FILE}")
    print()
    
    # Show first 5 URLs
    if uploaded_urls:
        print("First 5 uploaded images:")
        for idx, (filename, info) in enumerate(list(uploaded_urls.items())[:5], 1):
            print(f"  {idx}. {filename}")
            print(f"     URL: {info['display_url']}")
        print()


if __name__ == "__main__":
    main()

