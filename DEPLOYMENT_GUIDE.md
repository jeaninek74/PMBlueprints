# PMBlueprints - Complete Deployment Guide

## Updates Completed

### 1. Pricing Structure ✅
- **Free ($0)**: Browse templates only
- **Individual ($50 one-time)**: 1 download OR 1 AI generation
- **Professional ($49/month)**: 2 downloads, 4 AI suggestions, 6 AI generations per month
- **Enterprise ($100/month)**: Professional features + platform integrations

### 2. Payment & Billing Integration ✅
- Stripe checkout for all tiers
- Individual template purchase option ($50 per template)
- Subscription management
- Webhook handling for payment events
- Customer portal access

### 3. Template Previews with Real Thumbnails ✅
- Thumbnail generator creates real previews from actual template files
- Supports Excel, Word, and PowerPoint formats
- On-the-fly thumbnail generation if missing
- No mock or placeholder thumbnails

### 4. AI Generator & Suggestor ✅
- Full document generation with OpenAI GPT-4
- Download functionality for generated documents
- Tier-based usage limits enforced
- Usage tracking per user
- Export suggestions as documents

### 5. Dashboard Updates ✅
- Clean, professional design
- Usage statistics with progress bars
- Recent activity display
- Quick actions panel
- **All animations removed**

### 6. Platform Integrations ✅
- Monday.com integration
- Smartsheet integration
- Google Sheets integration
- Microsoft 365 integration
- Enterprise tier only access
- Detailed setup instructions on integration page

### 7. UI Improvements ✅
- Pricing icon moved to right side by login
- Industry and Template Type dropdowns **both required** on homepage
- Form validation before submission
- Popular Templates section with Preview only (no Download button)
- All animations removed globally
- Clean, professional design

## File Structure

```
pmblueprints_updated/
├── routes/
│   ├── payment.py              # Payment & subscription routes
│   ├── templates.py            # Template browsing & download
│   ├── ai_generator.py         # AI document generation
│   ├── ai_suggestions.py       # AI template suggestions
│   └── integrations.py         # Platform integrations
├── templates/
│   ├── base.html               # Base template with updated nav
│   ├── index.html              # Homepage with all updates
│   ├── dashboard.html          # User dashboard (no animations)
│   ├── pricing.html            # Pricing page
│   ├── templates/
│   │   └── browse.html         # Template browser
│   └── integrations/
│       └── index.html          # Integrations page
├── utils/
│   ├── subscription_security.py    # Tier limits & decorators
│   └── thumbnail_generator.py      # Real thumbnail generation
├── models.py                   # Database models
├── generate_thumbnails.py      # Script to generate all thumbnails
└── DEPLOYMENT_GUIDE.md         # This file
```

## Environment Variables Required

```bash
# Database
POSTGRES_URL=postgresql://user:password@host:port/database

# Flask
SECRET_KEY=your-secret-key-here

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# OpenAI
OPENAI_API_KEY=sk-...

# OAuth (Optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Redis (Optional but recommended)
REDIS_URL=redis://...
```

## Deployment Steps

### 1. Update Database Schema

Run migrations to add new fields:

```bash
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database schema updated')
"
```

### 2. Generate Thumbnails

Generate real thumbnails from template files:

```bash
python3 generate_thumbnails.py
```

### 3. Configure Stripe

1. Create products in Stripe Dashboard (optional, using inline pricing)
2. Set up webhook endpoint: `https://your-domain.com/payment/webhook`
3. Add webhook events:
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `customer.subscription.deleted`
4. Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

### 4. Deploy to Production

```bash
# Push to GitHub
git add .
git commit -m "Complete platform updates"
git push origin main

# Vercel will auto-deploy
# Or trigger manual deployment
```

### 5. Test All Features

#### Test Pricing Tiers
- [ ] Free tier can browse but not download
- [ ] Individual tier can purchase for $50
- [ ] Professional tier has correct monthly limits
- [ ] Enterprise tier has integration access

#### Test AI Features
- [ ] AI Generator creates documents
- [ ] AI Suggestor provides recommendations
- [ ] Downloads work correctly
- [ ] Usage limits are enforced

#### Test Integrations (Enterprise only)
- [ ] Monday.com connection test works
- [ ] Smartsheet connection test works
- [ ] Google Sheets configured
- [ ] Microsoft 365 configured

#### Test UI
- [ ] No animations anywhere
- [ ] Pricing icon on right side
- [ ] Both dropdowns required on homepage
- [ ] Popular Templates shows Preview only
- [ ] Thumbnails display correctly

## Integration Setup Instructions

### Monday.com
1. Go to Monday.com → Profile → Admin → API
2. Generate API token
3. Paste in Integration Settings
4. Test connection

### Smartsheet
1. Go to Smartsheet → Account → Apps & Integrations
2. Generate API token
3. Paste in Integration Settings
4. Test connection

### Google Sheets
1. Go to Google Cloud Console
2. Enable Google Sheets API
3. Create OAuth 2.0 credentials
4. Authorize access

### Microsoft 365
1. Go to Azure Portal
2. Register application
3. Grant Microsoft Graph permissions
4. Authorize access

## Monthly Maintenance

### Usage Reset
Create a cron job to reset monthly usage:

```python
from app import app, db, User
from datetime import datetime

with app.app_context():
    users = User.query.filter(
        User.subscription_tier.in_(['professional', 'enterprise'])
    ).all()
    
    for user in users:
        user.downloads_this_month = 0
        user.ai_suggestions_this_month = 0
        user.ai_generations_this_month = 0
        user.last_usage_reset = datetime.utcnow()
    
    db.session.commit()
```

## Troubleshooting

### Thumbnails Not Showing
- Run `python3 generate_thumbnails.py`
- Check file permissions on `static/thumbnails/`
- Verify template files exist

### Payment Issues
- Verify Stripe keys are correct
- Check webhook is receiving events
- Review Stripe logs

### AI Features Not Working
- Verify `OPENAI_API_KEY` is set
- Check OpenAI API quota
- Review error logs

### Integration Errors
- Verify API tokens are valid
- Check platform API status
- Test connection from settings page

## Support

For issues or questions:
- Email: support@pmblueprints.net
- Documentation: https://docs.pmblueprints.net

## Environment Configuration

All sensitive credentials should be configured in your deployment environment variables:
- Supabase URL and Token
- OpenAI API Key
- Google OAuth Client ID and Secret
- Stripe API Keys

**Note**: Never commit credentials to the repository. Use environment variables for all sensitive data.

## Production URL
- **Domain**: https://www.pmblueprints.net
- **Repository**: https://github.com/jeaninek74/PMBlueprints

---

**Status**: ✅ All updates completed and ready for deployment
**Last Updated**: October 16, 2025

