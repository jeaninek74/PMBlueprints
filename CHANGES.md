# Production Fix - Remove Mock Data and Use Actual 960 Templates

## Changes Made:

### 1. Fixed populate_database.py
- Changed hardcoded path `/home/ubuntu/pmblueprints-production-v2/templates_catalog.json` to relative path
- Now uses `os.path.join(os.path.dirname(__file__), "templates_catalog.json")`

### 2. Fixed routes/templates.py
- Changed hardcoded template file path `/home/ubuntu/pmblueprints-production-v2/static/templates/` to relative path
- Now uses `os.path.join(base_dir, 'static', 'templates', template.filename)`

### 3. Fixed database.py
- **REMOVED** mock embedded templates (Project Charter, Risk Register, WBS)
- Added multiple path resolution attempts for serverless compatibility
- Now tries: current_dir, cwd, /var/task (Vercel), and relative paths
- **CRITICAL**: Raises error if templates_catalog.json not found instead of falling back to mock data

## Impact:
- Production site will now serve all 964 actual templates instead of 3 mock templates
- Template downloads will serve actual .xlsx and .docx files from static/templates/
- No more fake download counts or generic descriptions

## Files Changed:
1. populate_database.py
2. routes/templates.py  
3. database.py

## Next Steps:
1. Test locally
2. Commit and push to GitHub
3. Vercel will auto-deploy
4. Validate production site shows 964 templates
