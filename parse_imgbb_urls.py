#!/usr/bin/env python3
"""
Parse the upload log to extract successful ImgBB URLs and create a mapping.
"""

import json
import re

LOG_FILE = "/home/ubuntu/pmb_repo/upload_log_v2.txt"
OUTPUT_FILE = "/home/ubuntu/pmb_repo/imgbb_urls.json"

def parse_upload_log():
    """Parse upload log and extract filename -> URL mappings."""
    
    url_mapping = {}
    
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()
    
    current_filename = None
    
    for line in lines:
        # Match upload line: [123/955] Uploading: filename.png
        upload_match = re.search(r'\[\d+/\d+\] Uploading: (.+\.png)', line)
        if upload_match:
            current_filename = upload_match.group(1)
            continue
        
        # Match success line: ✓ Success: https://i.ibb.co/...
        success_match = re.search(r'✓ Success: (https://i\.ibb\.co/[^\s]+)', line)
        if success_match and current_filename:
            url = success_match.group(1)
            url_mapping[current_filename] = {
                'url': url,
                'display_url': url,
                'filename': current_filename
            }
            current_filename = None
    
    return url_mapping

def main():
    print("=" * 80)
    print("PARSING IMGBB UPLOAD LOG")
    print("=" * 80)
    print(f"Log file: {LOG_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print()
    
    url_mapping = parse_upload_log()
    
    print(f"Found {len(url_mapping)} successful uploads")
    print()
    
    # Save to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(url_mapping, f, indent=2)
    
    print(f"✓ URL mapping saved to: {OUTPUT_FILE}")
    print()
    
    # Show first 10
    print("First 10 mappings:")
    for idx, (filename, info) in enumerate(list(url_mapping.items())[:10], 1):
        print(f"  {idx}. {filename}")
        print(f"     → {info['url']}")
    print()
    
    return url_mapping

if __name__ == "__main__":
    main()

