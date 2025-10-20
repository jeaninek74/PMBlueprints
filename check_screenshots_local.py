import sys
sys.path.insert(0, '/home/ubuntu/pmb_repo')

from app import app
from models import Template
import os

with app.app_context():
    # Get first 5 templates
    templates = Template.query.limit(5).all()
    
    print("Checking screenshot paths for first 5 templates:\n")
    
    for template in templates:
        print(f"Template ID: {template.id}")
        print(f"Name: {template.name}")
        print(f"File path: {template.file_path}")
        
        # Generate screenshot filename
        basename = os.path.basename(template.file_path)
        screenshot_filename = basename.rsplit('.', 1)[0] + '.png'
        print(f"Expected screenshot: {screenshot_filename}")
        
        # Check if file exists
        screenshot_path = f'static/screenshots_FULL/{screenshot_filename}'
        if os.path.exists(screenshot_path):
            size = os.path.getsize(screenshot_path)
            print(f"✓ Screenshot EXISTS ({size} bytes)")
        else:
            print(f"✗ Screenshot NOT FOUND")
            # Try to find by template name
            import glob
            similar = glob.glob(f'static/screenshots_FULL/{template.name.replace(" ", "_")}*')
            if similar:
                print(f"  Found similar: {os.path.basename(similar[0])}")
        
        print("-" * 60)
