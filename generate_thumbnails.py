"""
Generate Thumbnails Script
Generates real thumbnails from actual template files
Run this script to create thumbnails for all templates in the database
"""

import os
import sys
from app import app, db
from models import Template
from utils.thumbnail_generator import ThumbnailGenerator

def generate_all_thumbnails():
    """Generate thumbnails for all templates"""
    with app.app_context():
        print("Starting thumbnail generation...")
        
        # Get all templates
        templates = Template.query.all()
        print(f"Found {len(templates)} templates")
        
        # Initialize generator
        generator = ThumbnailGenerator(thumbnail_dir='static/thumbnails')
        
        # Generate thumbnails
        success_count, fail_count = generator.generate_all_thumbnails(templates)
        
        # Commit changes
        db.session.commit()
        
        print(f"\nThumbnail generation complete!")
        print(f"Success: {success_count}")
        print(f"Failed: {fail_count}")
        print(f"Total: {len(templates)}")

if __name__ == '__main__':
    generate_all_thumbnails()

