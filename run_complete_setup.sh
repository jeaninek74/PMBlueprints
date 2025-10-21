#!/bin/bash
# Complete Cloudflare R2 Screenshot Setup
# Runs all steps in sequence

set -e  # Exit on error

echo "======================================================================"
echo "PM BLUEPRINTS - CLOUDFLARE R2 SCREENSHOT AUTOMATION"
echo "======================================================================"
echo ""

# Step 1: Database Migration
echo "Step 1/3: Running database migration..."
echo "----------------------------------------------------------------------"
python3 add_cloudflare_url_production.py
echo ""

# Step 2: Capture Screenshots
echo "Step 2/3: Capturing screenshots from templates..."
echo "----------------------------------------------------------------------"
python3 capture_screenshots.py
echo ""

# Step 3: Upload to R2 and Update Database
echo "Step 3/3: Uploading to Cloudflare R2 and updating database..."
echo "----------------------------------------------------------------------"
python3 upload_to_cloudflare_r2.py
echo ""

echo "======================================================================"
echo "✅ COMPLETE! All screenshots are now served from Cloudflare R2 CDN"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. Visit https://www.pmblueprints.net to verify"
echo "2. Check Cloudflare dashboard: https://dash.cloudflare.com"
echo "3. Review CLOUDFLARE_SCREENSHOT_SETUP.md for details"
echo ""
