#!/bin/bash
# Copy template files to public directory for Vercel static serving

# Create public directory structure
mkdir -p public/templates

# Copy all template files
cp -r static/templates/* public/templates/

echo "Template files copied to public/templates/"
ls -lh public/templates/ | head -20

