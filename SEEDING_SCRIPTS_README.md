# PMBlueprints Seeding Scripts

## Overview

This directory contains robust seeding scripts to ensure the PMBlueprints platform never crashes due to missing data. All scripts are designed to be idempotent (safe to run multiple times) and production-ready.

## Available Scripts

### 1. `seed_test_users_robust.py`
**Purpose:** Create test users for all subscription tiers

**Test Users Created:**
- `free@pmblueprints.com` - Free tier (Password: `TestFree123!`)
- `individual@pmblueprints.com` - Individual tier (Password: `TestIndividual123!`)
- `professional@pmblueprints.com` - Professional tier (Password: `TestProfessional123!`)
- `enterprise@pmblueprints.com` - Enterprise tier (Password: `TestEnterprise123!`)

**Usage:**
```bash
python3.11 seed_test_users_robust.py
```

**Features:**
- ✅ Checks if users already exist before creating
- ✅ Validates email format
- ✅ Sets correct subscription tiers
- ✅ Hashes passwords securely
- ✅ Provides detailed logging

---

### 2. `seed_templates_robust.py`
**Purpose:** Seed all 925 templates into the database

**What it does:**
- Validates all template files exist in `static/templates/`
- Checks file formats (WORD, EXCEL, POWERPOINT only)
- Removes Business Case templates (incorrect content)
- Seeds 925 templates with proper metadata
- Validates industry and category assignments

**Usage:**
```bash
python3.11 seed_templates_robust.py
```

**Features:**
- ✅ Validates template files before seeding
- ✅ Skips duplicates (idempotent)
- ✅ Removes Business Case templates
- ✅ Assigns industries and categories
- ✅ Sets proper document formats
- ✅ Detailed error reporting

---

### 3. `seed_ai_components_robust.py`
**Purpose:** Seed AI Suggestor and AI Generator configurations

**What it does:**
- Seeds AI Suggestor with unlimited template type support (text input)
- Seeds AI Generator with 30 PM methodologies
- Configures document formats (WORD, EXCEL, POWERPOINT)
- Sets up AI component metadata

**Usage:**
```bash
python3.11 seed_ai_components_robust.py
```

**Features:**
- ✅ Unlimited template types (text input, not dropdown)
- ✅ 30 PM methodologies for AI Generator
- ✅ Proper document format configuration
- ✅ Idempotent (safe to run multiple times)

---

### 4. `seed_page_data_robust.py`
**Purpose:** Validate that all critical pages have required data

**What it validates:**
- Home page data (templates, industries, categories)
- Dashboard data (test users, templates)
- Navigation data (menu items, links)
- Search data (searchable fields)
- Pricing data (subscription tiers)

**Usage:**
```bash
python3.11 seed_page_data_robust.py
```

**Features:**
- ✅ Validates all critical page data
- ✅ Reports missing data
- ✅ Provides actionable recommendations
- ✅ Non-destructive (read-only validation)

---

### 5. `validate_critical_pages.py`
**Purpose:** Test critical pages to ensure they don't crash

**What it tests:**
- Home page (GET /)
- Login page (GET /auth/login)
- Signup page (GET /auth/register)
- Dashboard page (authenticated)
- Template count validation

**Usage:**
```bash
python3.11 validate_critical_pages.py
```

**Features:**
- ✅ Tests actual HTTP responses
- ✅ Validates page elements
- ✅ Tests authentication flow
- ✅ Reports missing elements
- ✅ Exit code 0 on success, 1 on failure

---

## Recommended Seeding Order

For a fresh database, run scripts in this order:

```bash
# 1. Seed test users first
python3.11 seed_test_users_robust.py

# 2. Seed templates
python3.11 seed_templates_robust.py

# 3. Seed AI components
python3.11 seed_ai_components_robust.py

# 4. Validate page data
python3.11 seed_page_data_robust.py

# 5. Validate critical pages
python3.11 validate_critical_pages.py
```

---

## Production Deployment

### Railway Deployment

After pushing to GitHub, Railway will automatically deploy. To seed production database:

1. **SSH into Railway container:**
   ```bash
   railway run bash
   ```

2. **Run seeding scripts:**
   ```bash
   python3.11 seed_test_users_robust.py
   python3.11 seed_templates_robust.py
   python3.11 seed_ai_components_robust.py
   ```

3. **Validate:**
   ```bash
   python3.11 validate_critical_pages.py
   ```

### Using API Endpoints

Alternatively, use the admin API endpoints (requires authentication):

```bash
# Seed test users
curl -X POST https://www.pmblueprints.net/api/admin/seed-test-users

# Seed templates
curl -X POST https://www.pmblueprints.net/api/admin/seed-templates

# Seed AI components
curl -X POST https://www.pmblueprints.net/api/admin/seed-ai-components
```

---

## Troubleshooting

### "No templates found in database"
**Solution:** Run `seed_templates_robust.py`

### "Missing test users"
**Solution:** Run `seed_test_users_robust.py`

### "Dashboard crashes"
**Solution:** 
1. Run `seed_test_users_robust.py`
2. Run `seed_templates_robust.py`
3. Run `validate_critical_pages.py`

### "Business Case templates still exist"
**Solution:** Use force delete endpoint:
```bash
curl -X POST https://www.pmblueprints.net/api/admin/delete-business-cases-force
```

---

## Data Integrity

All seeding scripts ensure:

- ✅ **Idempotent operations** - Safe to run multiple times
- ✅ **Validation before seeding** - Checks data integrity
- ✅ **Detailed logging** - Track what's happening
- ✅ **Error handling** - Graceful failures with rollback
- ✅ **Production-safe** - No mock data, real production data

---

## Template Count

**Expected:** 925 templates (30 Business Case templates removed)

**Breakdown:**
- 30 industries × 31 templates per industry = 930 templates
- Minus 30 Business Case templates (incorrect content) = 900 templates
- Plus 25 additional specialized templates = 925 templates

---

## Support

For issues or questions:
- Check Railway logs: `railway logs`
- Check health endpoint: `https://www.pmblueprints.net/api/health`
- Review this README
- Contact platform administrator

---

**Last Updated:** October 20, 2025
**Platform Version:** Production v1.0
**Template Count:** 925

