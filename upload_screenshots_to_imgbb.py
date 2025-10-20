"""
Upload all template screenshots to ImgBB and update database with CDN URLs
"""

import os
import requests
import time
from database import db
from models import Template
from app import app
import base64

# ImgBB API configuration
IMGBB_API_KEY = "2706400918b0e469ebadb69b4bc78a0d"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Screenshot directory
SCREENSHOTS_DIR = "static/final_screenshots"

def upload_to_imgbb(image_path, image_name):
    """Upload a single image to ImgBB and return the CDN URL"""
    try:
        # Read image file
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Prepare payload
        payload = {
            'key': IMGBB_API_KEY,
            'image': image_data,
            'name': image_name
        }
        
        # Upload to ImgBB
        response = requests.post(IMGBB_UPLOAD_URL, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result['data']['url']
            else:
                print(f"  ❌ ImgBB API error: {result.get('error', {}).get('message', 'Unknown error')}")
                return None
        else:
            print(f"  ❌ HTTP error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")
        return None

def get_screenshot_filename(template):
    """Generate screenshot filename from template"""
    # Match the naming convention used in final_screenshots
    safe_name_part = template.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    safe_name = f"{template.industry.replace(' ', '_')}_{safe_name_part}"
    safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    return f"{safe_name}.png"

def main():
    """Main upload process"""
    with app.app_context():
        # Get all templates
        templates = Template.query.all()
        total = len(templates)
        
        print(f"\n🚀 Starting ImgBB upload for {total} templates")
        print(f"📁 Screenshot directory: {SCREENSHOTS_DIR}\n")
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for idx, template in enumerate(templates, 1):
            # Generate screenshot filename
            screenshot_filename = get_screenshot_filename(template)
            screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
            
            print(f"[{idx}/{total}] {template.name}")
            
            # Check if screenshot exists
            if not os.path.exists(screenshot_path):
                print(f"  ⚠️  Screenshot not found: {screenshot_filename}")
                error_count += 1
                continue
            
            # Skip if already uploaded
            if template.imgbb_url:
                print(f"  ⏭️  Already uploaded: {template.imgbb_url}")
                skip_count += 1
                continue
            
            # Upload to ImgBB
            print(f"  📤 Uploading {screenshot_filename}...")
            imgbb_url = upload_to_imgbb(screenshot_path, screenshot_filename)
            
            if imgbb_url:
                # Update database
                template.imgbb_url = imgbb_url
                db.session.commit()
                print(f"  ✅ Success: {imgbb_url}")
                success_count += 1
            else:
                print(f"  ❌ Upload failed")
                error_count += 1
            
            # Rate limiting - ImgBB free tier allows ~5000 uploads/hour
            # Sleep 1 second to be safe (3600 uploads/hour max)
            if idx < total:
                time.sleep(1)
        
        print(f"\n" + "="*60)
        print(f"📊 Upload Summary:")
        print(f"  ✅ Successful uploads: {success_count}")
        print(f"  ⏭️  Skipped (already uploaded): {skip_count}")
        print(f"  ❌ Errors: {error_count}")
        print(f"  📈 Total processed: {total}")
        print(f"="*60 + "\n")

if __name__ == '__main__':
    main()

