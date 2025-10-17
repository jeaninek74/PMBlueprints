"""
Update template thumbnail paths in database to match actual thumbnail files
"""
import os
from flask import Flask
from database import db
from models import Template

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def update_thumbnails():
    with app.app_context():
        # Get all thumbnail files
        thumbnails_dir = 'static/thumbnails'
        if not os.path.exists(thumbnails_dir):
            print(f"Thumbnails directory not found: {thumbnails_dir}")
            return
        
        thumbnail_files = [f for f in os.listdir(thumbnails_dir) if f.endswith('.png')]
        print(f"Found {len(thumbnail_files)} thumbnail files")
        
        # Get all templates
        templates = Template.query.all()
        print(f"Found {len(templates)} templates in database")
        
        updated = 0
        for template in templates:
            # Generate expected thumbnail filename from template name
            safe_name = template.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
            expected_filename = f"{safe_name}.png"
            
            # Check if thumbnail file exists
            if expected_filename in thumbnail_files:
                template.thumbnail_path = expected_filename
                updated += 1
                print(f"✓ Matched: {template.name} -> {expected_filename}")
            else:
                # Try to find a close match
                template_name_lower = template.name.lower().replace(' ', '_')
                for thumb_file in thumbnail_files:
                    if thumb_file.lower().replace('.png', '') in template_name_lower or \
                       template_name_lower in thumb_file.lower().replace('.png', ''):
                        template.thumbnail_path = thumb_file
                        updated += 1
                        print(f"~ Fuzzy matched: {template.name} -> {thumb_file}")
                        break
                else:
                    print(f"✗ No match: {template.name}")
        
        db.session.commit()
        print(f"\nUpdated {updated} templates with thumbnail paths")

if __name__ == '__main__':
    update_thumbnails()
