# PMBlueprints Seeding Scripts

This directory contains comprehensive seeding and validation scripts to ensure the platform never crashes due to missing data.

## Available Scripts

### 1. seed_test_users_robust.py
**Purpose:** Create test users for all subscription tiers

**Creates:**
- free@pmblueprints.com (Free tier)
- individual@pmblueprints.com (Individual tier)
- professional@pmblueprints.com (Professional tier)
- enterprise@pmblueprints.com (Enterprise tier)

**Usage:**
```bash
python3.11 seed_test_users_robust.py
```

**When to Run:**
- After database initialization
- When test users are missing
- Before running integration tests

---

### 2. seed_templates_robust.py
**Purpose:** Seed all 925 production templates with validation

**Features:**
- Validates template files exist
- Checks metadata completeness
- Verifies categories and industries
- Reports missing or invalid templates

**Usage:**
```bash
python3.11 seed_templates_robust.py
```

**When to Run:**
- After database initialization
- When adding new templates
- To verify template integrity

---

### 3. seed_ai_components_robust.py
**Purpose:** Configure AI Suggestor and AI Generator

**Configures:**
- AI Suggestor: Unlimited template types (text input)
- AI Generator: 30 methodologies
- Document formats: WORD, EXCEL, POWERPOINT

**Usage:**
```bash
python3.11 seed_ai_components_robust.py
```

**When to Run:**
- After database initialization
- When AI components need reconfiguration
- To update methodologies or formats

---

### 4. seed_page_data_robust.py
**Purpose:** Validate all critical page data

**Validates:**
- Home page data (templates, industries, categories)
- Dashboard data (users, stats)
- Navigation data (menu items)
- Search data (searchable fields)
- Pricing data (subscription tiers)

**Usage:**
```bash
python3.11 seed_page_data_robust.py
```

**When to Run:**
- Before deployment
- To verify data integrity
- When pages are crashing

---

### 5. validate_critical_pages.py
**Purpose:** Test all critical pages for errors

**Tests:**
- Home page
- Login page
- Signup page
- Dashboard page
- AI Suggestor page
- AI Generator page
- Template count

**Usage:**
```bash
python3.11 validate_critical_pages.py
```

**When to Run:**
- Before deployment
- After major changes
- To verify platform stability

---

## Complete Seeding Workflow

### Initial Setup (New Database)

```bash
# Step 1: Create test users
python3.11 seed_test_users_robust.py

# Step 2: Seed templates
python3.11 seed_templates_robust.py

# Step 3: Configure AI components
python3.11 seed_ai_components_robust.py

# Step 4: Validate page data
python3.11 seed_page_data_robust.py

# Step 5: Validate critical pages
python3.11 validate_critical_pages.py
```

### Pre-Deployment Validation

```bash
# Validate page data
python3.11 seed_page_data_robust.py

# Validate critical pages
python3.11 validate_critical_pages.py
```

### Troubleshooting

If any script fails:

1. Check the error message
2. Run the recommended action from the script output
3. Re-run the failed script
4. Run validation scripts to verify

---

## Production Scripts

### force_delete_business_cases_production.py
**Purpose:** Force delete Business Case templates from production

**Usage:**
```bash
python3.11 force_delete_business_cases_production.py
```

**When to Run:**
- Only when Business Case templates need to be removed
- **WARNING:** This deletes data from production database

---

## Script Status

| Script | Status | Last Run | Result |
|--------|--------|----------|--------|
| seed_test_users_robust.py | ✅ Ready | Oct 20, 2025 | 4/4 users created |
| seed_templates_robust.py | ✅ Ready | Oct 20, 2025 | 925 templates seeded |
| seed_ai_components_robust.py | ✅ Ready | Oct 20, 2025 | AI configured |
| seed_page_data_robust.py | ✅ Ready | Oct 20, 2025 | All checks passing |
| validate_critical_pages.py | ✅ Ready | Oct 20, 2025 | All pages passing |

---

## Notes

- All scripts use robust error handling
- Scripts provide detailed output for debugging
- Scripts are idempotent (safe to run multiple times)
- Scripts validate data before and after seeding
- Scripts report issues and recommend actions

---

**Last Updated:** October 20, 2025  
**Platform Version:** Latest (commit 111df2d)
