# Cloudflare R2 Screenshot Setup Guide

Complete solution for automated screenshot capture and CDN hosting for PM Blueprints templates.

## Overview

This solution automates the process of:
1. Capturing screenshots from 925+ Excel and Word templates
2. Uploading screenshots to Cloudflare R2 CDN
3. Updating the database with CDN URLs
4. Serving screenshots from Cloudflare CDN on www.pmblueprints.net

## Architecture

```
Templates (Excel/Word)
    ↓
Screenshot Capture Script
    ↓
PNG Screenshots (local)
    ↓
Cloudflare R2 Upload Script
    ↓
Cloudflare R2 CDN
    ↓
Database Update (cloudflare_url field)
    ↓
Preview Pages (using template.thumbnail property)
```

## Prerequisites

### 1. Python Packages
```bash
pip3 install boto3 python-docx openpyxl Pillow psycopg2-binary python-dotenv
```

### 2. Cloudflare R2 Setup ✅ COMPLETED

- **Account ID**: `5e687ea57869abd16d33fa2f3a69af50`
- **Bucket Name**: `pmblueprints-screenshots`
- **Public URL**: `https://pub-88e6ef534d3c4ce76zafcdd6b325604c.r2.dev`
- **Access Key ID**: `3aae1723b00b01b111c084e6cdac0a06`
- **Secret Access Key**: `b9e28a118ef90e6eabe40aded548e4d284d85f6737806227cc8f349b068d1d4a`
- **S3 Endpoint**: `https://5e687ea57869abd16d33fa2f3a69af50.r2.cloudflarestorage.com`

### 3. Database Setup ✅ COMPLETED

The `cloudflare_url` field has been added to the Template model:
```python
cloudflare_url = db.Column(db.String(500))  # CDN URL for screenshot
```

The `thumbnail` property automatically uses Cloudflare URLs:
```python
@property
def thumbnail(self):
    # Priority 1: Use Cloudflare CDN URL if available
    if self.cloudflare_url:
        return self.cloudflare_url
    # Priority 2: Use stored thumbnail path
    elif self.thumbnail_path:
        return f'/static/thumbnails/{self.thumbnail_path}'
    # Priority 3: Generate thumbnail filename
    ...
```

## Files Created

1. **`capture_screenshots.py`** - Automated screenshot capture
2. **`upload_to_cloudflare_r2.py`** - Upload to R2 and update database
3. **`add_cloudflare_url_production.py`** - Database migration for production
4. **`cloudflare_r2_credentials.txt`** - API credentials (KEEP SECURE)

## Step-by-Step Execution

### Step 1: Run Database Migration (Production)

Add the `cloudflare_url` column to your production database:

```bash
python3 add_cloudflare_url_production.py
```

**Expected Output:**
```
✓ Connected to production database
✓ Successfully added 'cloudflare_url' column to templates table
```

### Step 2: Capture Screenshots

Generate screenshots from all Excel and Word templates:

```bash
python3 capture_screenshots.py
```

**Screenshot Specifications:**
- **Excel Files**: 
  - Orientation: Landscape
  - Target: Dashboard tab (2nd tab)
  - Shows: All columns, rows, and tab bar
  - Format: PNG with color
  
- **Word Files**:
  - Orientation: Portrait
  - Target: Title page
  - Format: PNG with color

**Expected Output:**
```
PM BLUEPRINTS - AUTOMATED SCREENSHOT CAPTURE
======================================================================

📁 Found 462 Excel files and 463 Word files
📊 Total templates to process: 925

Processing Excel files...
----------------------------------------------------------------------
[1/462] AI_ML_Business_Case.xlsx
  📊 Capturing sheet: Dashboard
  ✅ Saved screenshot: AI_ML_Business_Case.png

...

SUMMARY
======================================================================
✅ Successfully captured: 925 screenshots
❌ Errors: 0
📁 Output directory: /home/ubuntu/PMBlueprints/static/screenshots_new
```

### Step 3: Upload to Cloudflare R2 and Update Database

Upload all screenshots to Cloudflare R2 CDN and update database:

```bash
python3 upload_to_cloudflare_r2.py
```

**Expected Output:**
```
PM BLUEPRINTS - CLOUDFLARE R2 UPLOAD & DATABASE UPDATE
======================================================================

📁 Found 925 screenshots to upload
☁️  Uploading to Cloudflare R2 bucket: pmblueprints-screenshots
🔗 Public URL base: https://pub-88e6ef534d3c4ce76zafcdd6b325604c.r2.dev

🔌 Testing database connection...
✅ Database connection successful

Uploading screenshots...
----------------------------------------------------------------------
[1/925] AI_ML_Business_Case.png
  ✅ Uploaded: https://pub-88e6ef534d3c4ce76zafcdd6b325604c.r2.dev/AI_ML_Business_Case.png
  ✅ Database updated for: AI_ML_Business_Case

...

SUMMARY
======================================================================
✅ Successfully uploaded: 925 screenshots
✅ Database records updated: 925
❌ Upload errors: 0

🎉 Screenshots are now served from Cloudflare R2 CDN!
🔗 Access them at: https://pub-88e6ef534d3c4ce76zafcdd6b325604c.r2.dev/[filename].png
```

## How It Works

### Screenshot Capture Logic

**Excel Files:**
1. Opens the Excel file using `openpyxl`
2. Navigates to the Dashboard tab (2nd sheet)
3. Extracts data from all columns and rows
4. Generates a landscape PNG with:
   - Title showing sheet name
   - Column headers in blue
   - Data rows with color coding (green for numbers)
   - Tab bar at bottom showing all sheet names
   - Dashboard tab highlighted

**Word Files:**
1. Opens the Word document using `python-docx`
2. Extracts text from the first page (first 15 paragraphs)
3. Generates a portrait PNG with:
   - Title in large font
   - Subtitles in medium font
   - Body text in regular font
   - Document metadata at bottom

### Upload and Database Update Logic

1. **Upload to R2**: Uses boto3 S3 client to upload PNG files
2. **Generate Public URL**: Constructs CDN URL using public development URL
3. **Update Database**: Updates `cloudflare_url` field in templates table
4. **Template Matching**: Matches screenshots to templates by name

### Preview Page Integration

The preview pages automatically use Cloudflare URLs through the `template.thumbnail` property:

```python
# In your Jinja2 templates:
<img src="{{ template.thumbnail }}" alt="{{ template.name }}">
```

The property returns:
1. Cloudflare CDN URL (if available) ← **NEW**
2. Local thumbnail path (if available)
3. Generated thumbnail filename (fallback)

## Verification

### Check Cloudflare R2 Dashboard

1. Go to: https://dash.cloudflare.com/5e687ea57869abd16d33fa2f3a69af50/r2/default/buckets/pmblueprints-screenshots
2. Verify 925 objects are uploaded
3. Check bucket size

### Check Database

```sql
-- Count templates with Cloudflare URLs
SELECT COUNT(*) FROM templates WHERE cloudflare_url IS NOT NULL;

-- Sample Cloudflare URLs
SELECT name, cloudflare_url FROM templates WHERE cloudflare_url IS NOT NULL LIMIT 10;
```

### Check Website

1. Visit: https://www.pmblueprints.net
2. Browse templates
3. Click "Preview" button
4. Verify screenshots load from Cloudflare CDN
5. Check browser DevTools → Network tab to confirm CDN URLs

## Troubleshooting

### Issue: Screenshots not capturing correctly

**Solution**: Check template files exist in `static/templates/`
```bash
ls -la static/templates/*.xlsx | wc -l
ls -la static/templates/*.docx | wc -l
```

### Issue: Upload fails with authentication error

**Solution**: Verify R2 credentials in `upload_to_cloudflare_r2.py`
```bash
# Test R2 connection
python3 -c "import boto3; print('Testing R2...'); boto3.client('s3', endpoint_url='https://5e687ea57869abd16d33fa2f3a69af50.r2.cloudflarestorage.com', aws_access_key_id='3aae1723b00b01b111c084e6cdac0a06', aws_secret_access_key='b9e28a118ef90e6eabe40aded548e4d284d85f6737806227cc8f349b068d1d4a').list_buckets(); print('✅ Success')"
```

### Issue: Database update fails

**Solution**: Check Supabase connection
```bash
# Test database connection
python3 -c "import psycopg2; conn = psycopg2.connect(host='mmrazymwgqfxkhczqpus.supabase.co', database='postgres', user='postgres', password='sbp_e5f182e48846964e6cea5bdb3f59a6513efd7386', port='5432', sslmode='require'); print('✅ Database connected'); conn.close()"
```

### Issue: Preview page not showing CDN images

**Solution**: 
1. Check if `cloudflare_url` field exists in database
2. Verify template.thumbnail property in models.py
3. Clear browser cache
4. Check browser console for errors

## Cost Estimate

**Cloudflare R2 Free Tier:**
- Storage: 10 GB/month (FREE)
- Class A Operations: 1 million/month (FREE)
- Class B Operations: 10 million/month (FREE)
- Egress: Unlimited (FREE)

**Current Usage:**
- 925 screenshots × ~200 KB average = ~185 MB
- Well within free tier limits ✅

## Security Notes

⚠️ **IMPORTANT**: The credentials in this setup are hardcoded for simplicity. For production:

1. Move credentials to environment variables:
```bash
export R2_ACCESS_KEY_ID="..."
export R2_SECRET_ACCESS_KEY="..."
export DB_PASSWORD="..."
```

2. Use `.env` file with `python-dotenv`:
```python
from dotenv import load_dotenv
load_dotenv()

R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
```

3. Add `.env` to `.gitignore`

## Maintenance

### Re-generating Screenshots

If templates are updated:
```bash
# 1. Delete old screenshots
rm -rf static/screenshots_new/*.png

# 2. Re-capture
python3 capture_screenshots.py

# 3. Re-upload (will overwrite in R2)
python3 upload_to_cloudflare_r2.py
```

### Adding New Templates

New templates will automatically get screenshots:
1. Add template files to `static/templates/`
2. Run capture and upload scripts
3. Database will be updated automatically

## Support

For issues or questions:
- Check Cloudflare R2 dashboard: https://dash.cloudflare.com
- Check Supabase dashboard: https://mmrazymwgqfxkhczqpus.supabase.co
- Review script logs for error messages

---

**Status**: ✅ Ready to execute
**Last Updated**: October 20, 2025
**Version**: 1.0

