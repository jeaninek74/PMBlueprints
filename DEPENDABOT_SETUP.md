# Dependabot Setup Guide for PMBlueprints

## ✅ What's Been Configured

This repository now has **automated dependency monitoring** with safe update workflows.

### Files Added:
1. `.github/dependabot.yml` - Dependabot configuration
2. `.github/workflows/test-pr.yml` - Automated testing for PRs
3. `railway.json` - Updated with health checks

## 🔄 How It Works

### Step 1: Dependabot Monitors Dependencies
- Checks every **Monday at 9 AM EST**
- Monitors: OpenAI, Flask, Stripe, PostgreSQL, and all other Python packages
- Groups minor updates together to reduce PR noise

### Step 2: Dependabot Creates Pull Request
When an update is available:
- Creates a PR with detailed changelog
- Automatically runs tests via GitHub Actions
- Labels PR as "dependencies" and "python"

### Step 3: Automated Tests Run
GitHub Actions automatically:
- ✅ Checks Python syntax
- ✅ Verifies all imports work
- ✅ Tests OpenAI library compatibility
- ✅ Scans for security vulnerabilities
- ✅ Validates requirements.txt format

### Step 4: Railway Creates Preview Deployment
Railway automatically:
- Deploys the PR to a preview URL
- Runs health checks
- Keeps production untouched

### Step 5: You Review & Test
1. Check your email/GitHub notifications
2. Review the PR changes
3. Test on the preview URL
4. If good → Merge PR
5. If issues → Close PR (no changes to production)

### Step 6: Auto-Deploy to Production
When you merge:
- Railway deploys to production
- Zero-downtime deployment
- Users experience no interruption

## 📧 Notifications You'll Receive

### Email Example:
```
Subject: [PMBlueprints] Bump openai from 1.12.0 to 1.13.0 (#47)

Dependabot opened a pull request:
- Updates openai from 1.12.0 to 1.13.0
- ✅ All automated tests passed
- 🔗 Preview: https://pr-47-pmblueprints.up.railway.app

Release Notes:
- Added GPT-4 Turbo support
- Fixed streaming responses
- Improved error handling

[View Pull Request] [Merge] [Close]
```

## 🎯 What Gets Updated Automatically

### High Priority (Separate PRs):
- **OpenAI** - AI functionality
- **Flask** - Web framework
- **Stripe** - Payment processing
- **psycopg2-binary** - Database driver
- **gunicorn** - Production server

### Grouped Updates (Combined PRs):
- Minor version updates (e.g., 1.2.0 → 1.3.0)
- Patch updates (e.g., 1.2.0 → 1.2.1)
- Security patches (always separate)

## ⚙️ Configuration Options

### Change Update Frequency
Edit `.github/dependabot.yml`:
```yaml
schedule:
  interval: "daily"    # or "weekly" or "monthly"
```

### Limit Open PRs
```yaml
open-pull-requests-limit: 3  # Max PRs at once
```

### Add Auto-Merge for Patches
For patch updates only (e.g., 1.2.0 → 1.2.1):
```yaml
# Add to dependabot.yml
auto-merge:
  - match:
      dependency-type: "all"
      update-type: "semver:patch"
```

## 🚀 Railway Preview Deployments

### Enable PR Deployments in Railway:
1. Go to Railway dashboard
2. Select PMBlueprints project
3. Settings → Deployments
4. Enable "PR Deployments"
5. Railway will create preview URLs like:
   - `pr-47-pmblueprints.up.railway.app`
   - `pr-48-pmblueprints.up.railway.app`

### Preview Environment Variables:
Railway automatically copies your production environment variables to preview deployments, so OpenAI API keys, Stripe keys, etc. work in previews.

## 🔒 Security Updates

Dependabot prioritizes security:
- **Critical vulnerabilities**: Immediate PR
- **High severity**: Within 24 hours
- **Medium/Low**: Next weekly check

## 📊 Monitoring

### View Dependabot Activity:
1. Go to: `github.com/jeaninek74/PMBlueprints`
2. Click "Insights" → "Dependency graph" → "Dependabot"
3. See all updates, alerts, and history

### View Test Results:
1. Go to any PR created by Dependabot
2. Scroll to "Checks" section
3. See automated test results

## 🛠️ Troubleshooting

### If Tests Fail:
- Dependabot PR will show ❌ status
- Review test logs in GitHub Actions
- Fix issues before merging
- Or close PR if update is problematic

### If Preview Deployment Fails:
- Check Railway logs
- Verify environment variables
- Test locally first
- Contact Railway support if needed

### If You Want to Skip an Update:
- Just close the PR
- Dependabot won't recreate it
- You can manually update later

## 📝 Best Practices

1. **Review PRs Weekly**: Check every Monday for new updates
2. **Test Previews**: Always test preview URL before merging
3. **Read Release Notes**: Understand what changed
4. **Monitor Production**: Watch Railway logs after merging
5. **Keep Rollback Ready**: Railway can rollback in seconds if needed

## 🎓 Learning Resources

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Railway Preview Deployments](https://docs.railway.app/deploy/deployments#preview-deployments)
- [OpenAI Python Library Changelog](https://github.com/openai/openai-python/releases)

## ✅ Next Steps

1. **Push these changes to GitHub**
2. **Enable Dependabot** (automatically enabled when you push)
3. **Enable PR deployments in Railway**
4. **Wait for first PR** (next Monday or when update available)
5. **Test the workflow** with the first update

## 🆘 Need Help?

If you have questions about:
- Dependabot: Check GitHub Dependabot docs
- Railway previews: Check Railway dashboard
- OpenAI updates: Review OpenAI changelog
- Platform issues: Check Railway logs

---

**Status**: ✅ Ready to deploy
**Last Updated**: October 18, 2025

