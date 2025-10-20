# Production Safeguards Documentation

This document describes the production safeguards implemented to prevent platform breakage and ensure system reliability.

---

## Overview

Three key safeguards have been implemented:

1. **Automated Integration Tests** - Validates all critical features
2. **Robust Database Seeding Script** - Ensures test users are always correct
3. **Health Check Endpoint** - Monitors system health in real-time

---

## 1. Automated Integration Tests

**File:** `tests/test_production_integration.py`

### Purpose
Automatically test all critical platform features to catch bugs before they reach production.

### What It Tests
- ✅ Authentication (login/logout)
- ✅ Dashboard access
- ✅ Template browsing
- ✅ Platform integrations (Monday.com, Smartsheet, Google, Microsoft 365)
- ✅ Subscription tier access control

### Usage

**Run locally:**
```bash
cd /home/ubuntu/pmb_repo
python3 tests/test_production_integration.py
```

**Run in CI/CD:**
```bash
# Add to your deployment pipeline
python3 tests/test_production_integration.py
if [ $? -ne 0 ]; then
    echo "Integration tests failed! Aborting deployment."
    exit 1
fi
```

### Exit Codes
- `0` - All tests passed
- `1` - One or more tests failed

### Example Output
```
========================================
RUNNING PRODUCTION INTEGRATION TESTS
========================================

Testing Free Tier User...
✅ Login successful
✅ Dashboard accessible
✅ Templates accessible
✅ Integrations correctly blocked

Testing Individual Tier User...
✅ Login successful
✅ Dashboard accessible
✅ Templates accessible
✅ Integrations correctly blocked

Testing Professional Tier User...
✅ Login successful
✅ Dashboard accessible
✅ Templates accessible
✅ Integrations correctly blocked

Testing Enterprise Tier User...
✅ Login successful
✅ Dashboard accessible
✅ Templates accessible
✅ Integrations accessible

========================================
ALL TESTS PASSED: 4/4 tiers tested
========================================
```

---

## 2. Robust Database Seeding Script

**File:** `seed_test_users_robust.py`

### Purpose
Ensure all test users exist with correct subscription tiers in all environments (local, staging, production).

### Features
- ✅ **Idempotent** - Safe to run multiple times
- ✅ **Error Handling** - Never crashes, always provides detailed logs
- ✅ **Validation** - Verifies users after creation
- ✅ **Rollback** - Can delete test users if needed

### Test Users Created
```python
free@pmblueprints.com          / TestFree123!          (tier: free)
individual@pmblueprints.com    / TestIndividual123!    (tier: individual)
professional@pmblueprints.com  / TestPro123!           (tier: professional)
enterprise@pmblueprints.com    / TestEnterprise123!    (tier: enterprise)
```

### Usage

**Normal mode (create/update users):**
```bash
cd /home/ubuntu/pmb_repo
python3 seed_test_users_robust.py
```

**Verify-only mode (check without modifying):**
```bash
python3 seed_test_users_robust.py --verify-only
```

**Rollback mode (delete all test users):**
```bash
python3 seed_test_users_robust.py --rollback
```

### Example Output
```
2025-10-20 05:18:47 - INFO - ✅ Database connection verified
2025-10-20 05:18:47 - INFO - ============================================================
2025-10-20 05:18:47 - INFO - STARTING DATABASE SEEDING
2025-10-20 05:18:47 - INFO - ============================================================
2025-10-20 05:18:47 - INFO - ➕ Creating new user: free@pmblueprints.com
2025-10-20 05:18:47 - INFO - ✅ Created user: free@pmblueprints.com (tier: free)
2025-10-20 05:18:47 - INFO - ➕ Creating new user: individual@pmblueprints.com
2025-10-20 05:18:47 - INFO - ✅ Created user: individual@pmblueprints.com (tier: individual)
2025-10-20 05:18:47 - INFO - ➕ Creating new user: professional@pmblueprints.com
2025-10-20 05:18:47 - INFO - ✅ Created user: professional@pmblueprints.com (tier: professional)
2025-10-20 05:18:47 - INFO - ➕ Creating new user: enterprise@pmblueprints.com
2025-10-20 05:18:47 - INFO - ✅ Created user: enterprise@pmblueprints.com (tier: enterprise)
2025-10-20 05:18:47 - INFO - ============================================================
2025-10-20 05:18:47 - INFO - SEEDING COMPLETE: 4 success, 0 failures
2025-10-20 05:18:47 - INFO - ============================================================
```

### When to Run
- ✅ After deploying to a new environment
- ✅ After database migrations
- ✅ When test users are accidentally deleted
- ✅ When subscription tiers get corrupted
- ✅ As part of deployment pipeline

---

## 3. Health Check Endpoint

**Endpoint:** `https://www.pmblueprints.net/api/health-check`

### Purpose
Monitor system health and catch configuration issues before they affect users.

### What It Checks
- ✅ Database connectivity
- ✅ Template count (should be 955)
- ✅ Test user existence and tiers
- ✅ Subscription tier permissions
- ✅ Critical route registration

### Usage

**Manual check:**
```bash
curl https://www.pmblueprints.net/api/health-check
```

**Automated monitoring:**
```bash
# Add to cron or monitoring service
*/5 * * * * curl -f https://www.pmblueprints.net/api/health-check || alert_team
```

### Response Format
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T05:14:23Z",
  "checks": {
    "database": {
      "status": "ok",
      "templates_count": 955
    },
    "test_users": {
      "free": {
        "exists": true,
        "tier": "free"
      },
      "individual": {
        "exists": true,
        "tier": "individual"
      },
      "professional": {
        "exists": true,
        "tier": "professional"
      },
      "enterprise": {
        "exists": true,
        "tier": "enterprise"
      }
    },
    "tier_permissions": {
      "enterprise_platform_integrations": true
    },
    "routes": {
      "templates": true,
      "integrations": true,
      "ai_generator": true,
      "ai_suggestions": true
    }
  }
}
```

### Status Codes
- `200 OK` - System healthy
- `500 Internal Server Error` - System unhealthy (check response for details)

### Integration with Monitoring Services

**Uptime Robot:**
```
Monitor Type: HTTP(s)
URL: https://www.pmblueprints.net/api/health-check
Interval: 5 minutes
Alert: Email/SMS when down
```

**Pingdom:**
```
Check Type: HTTP Check
URL: https://www.pmblueprints.net/api/health-check
Check Interval: 1 minute
Alert: When status != 200
```

**Custom Script:**
```python
import requests
import time

def check_health():
    try:
        response = requests.get('https://www.pmblueprints.net/api/health-check', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'healthy':
                print("✅ System healthy")
                return True
            else:
                print(f"⚠️  System unhealthy: {data}")
                send_alert(data)
                return False
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            send_alert(f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        send_alert(str(e))
        return False

# Run every 5 minutes
while True:
    check_health()
    time.sleep(300)
```

---

## Deployment Checklist

Use this checklist for every deployment to ensure all safeguards are in place:

### Pre-Deployment
- [ ] Run integration tests locally: `python3 tests/test_production_integration.py`
- [ ] Verify test users locally: `python3 seed_test_users_robust.py --verify-only`
- [ ] Check health endpoint locally: `curl http://localhost:5000/api/health-check`

### Post-Deployment
- [ ] Seed test users in production: `python3 seed_test_users_robust.py`
- [ ] Run integration tests in production
- [ ] Verify health endpoint: `curl https://www.pmblueprints.net/api/health-check`
- [ ] Test login with all 4 tiers
- [ ] Test integration access with Enterprise tier

### Monitoring Setup
- [ ] Configure uptime monitoring for health endpoint
- [ ] Set up alerts for health check failures
- [ ] Schedule daily integration test runs
- [ ] Monitor error logs for unexpected issues

---

## Troubleshooting

### Integration Tests Failing

**Problem:** Tests fail with "Invalid email or password"

**Solution:**
```bash
# Re-seed test users
python3 seed_test_users_robust.py

# Verify users were created
python3 seed_test_users_robust.py --verify-only
```

---

### Health Check Returns Unhealthy

**Problem:** Health endpoint returns 500 or status "unhealthy"

**Solution:**
```bash
# Check the response for details
curl https://www.pmblueprints.net/api/health-check | jq

# Common issues:
# 1. Database connection failed -> Check DATABASE_URL
# 2. Test users missing -> Run seed_test_users_robust.py
# 3. Wrong subscription tiers -> Run seed_test_users_robust.py
# 4. Routes not registered -> Check app.py for blueprint registration
```

---

### Test Users Have Wrong Tiers

**Problem:** Users exist but have incorrect subscription_tier values

**Solution:**
```bash
# Update all test users
python3 seed_test_users_robust.py

# This will update existing users with correct tiers
```

---

### Database Seeding Fails

**Problem:** Script crashes or returns errors

**Solution:**
```bash
# The robust script should never crash, but if it does:

# 1. Check database connection
python3 -c "from app import app, db; app.app_context().push(); print(db.engine.url)"

# 2. Check for database locks
# (PostgreSQL) SELECT * FROM pg_stat_activity WHERE datname = 'your_db_name';

# 3. Try rollback and re-seed
python3 seed_test_users_robust.py --rollback
python3 seed_test_users_robust.py
```

---

## Best Practices

### For Developers
1. **Always run integration tests** before pushing code
2. **Never modify test user credentials** without updating the script
3. **Check health endpoint** after major changes
4. **Run seeding script** after database migrations

### For DevOps
1. **Add integration tests to CI/CD pipeline**
2. **Monitor health endpoint** with external service
3. **Run seeding script** as part of deployment process
4. **Set up alerts** for health check failures

### For QA
1. **Use test users** for all manual testing
2. **Verify all tiers** after major releases
3. **Report any access control issues** immediately
4. **Test integrations** with Enterprise tier account

---

## Emergency Procedures

### Platform Integrations Not Working

**Symptoms:** Enterprise users can't access integrations

**Emergency Fix:**
```bash
# 1. Check enterprise user tier
curl https://www.pmblueprints.net/api/health-check | jq '.checks.test_users.enterprise'

# 2. If tier is wrong, fix it
python3 seed_test_users_robust.py

# 3. Verify fix
curl https://www.pmblueprints.net/api/health-check

# 4. Test integration access
# Login as enterprise@pmblueprints.com and try accessing:
# https://www.pmblueprints.net/integrations/monday/send/1
```

---

### All Test Users Missing

**Symptoms:** Cannot login with any test credentials

**Emergency Fix:**
```bash
# Re-create all test users
python3 seed_test_users_robust.py

# Verify creation
python3 seed_test_users_robust.py --verify-only
```

---

## Maintenance

### Weekly Tasks
- [ ] Review health check logs
- [ ] Verify test users still exist
- [ ] Run integration tests

### Monthly Tasks
- [ ] Review and update test coverage
- [ ] Update test user passwords (if needed)
- [ ] Review monitoring alerts

### Quarterly Tasks
- [ ] Full system audit
- [ ] Update documentation
- [ ] Review and improve safeguards

---

## Contact

For questions or issues with production safeguards:
- **Documentation:** This file
- **Code:** `tests/test_production_integration.py`, `seed_test_users_robust.py`, `routes/health_check.py`
- **Health Endpoint:** https://www.pmblueprints.net/api/health-check

---

**Last Updated:** October 20, 2025  
**Version:** 1.0

