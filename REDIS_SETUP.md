# Redis Setup for Session Management

## Why Redis?

PMBlueprints runs on Vercel serverless functions, which are stateless. Flask's default session storage (cookies/filesystem) doesn't work reliably across different function instances. Redis provides a centralized session store that works perfectly with serverless architectures.

## Setup Instructions

### 1. Create Upstash Redis Instance (Free Tier)

Upstash Redis is recommended for Vercel deployments as it's optimized for serverless and has a generous free tier.

1. Go to https://upstash.com/
2. Sign up for a free account
3. Create a new Redis database
4. Select the region closest to your Vercel deployment
5. Copy the `REDIS_URL` connection string

### 2. Configure Vercel Environment Variable

1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add a new variable:
   - **Name:** `REDIS_URL`
   - **Value:** Your Upstash Redis URL (format: `redis://default:password@host:port`)
   - **Environments:** Production, Preview, Development

### 3. Redeploy

After adding the environment variable, trigger a new deployment:

```bash
vercel --prod
```

Or push a commit to trigger automatic deployment.

## Verification

### Check if Redis is Connected

Visit: https://pmblueprints-production.vercel.app/health/detailed

Look for:
```json
{
  "environment": {
    "redis_configured": true
  }
}
```

### Test Session Persistence

1. Log in with Demo Login
2. Navigate to Templates page
3. Verify you remain logged in (navigation shows "Dashboard" and "Demo")
4. Refresh the page
5. Verify you're still logged in

## Fallback Behavior

If `REDIS_URL` is not configured, the application will fall back to filesystem sessions stored in `/tmp/flask_sessions`. This works for development but is **not recommended for production** as:

- Sessions are lost when serverless functions scale down
- Different function instances don't share the same filesystem
- Users will be logged out frequently

## Configuration Details

### Session Settings

- **Session Type:** Redis (or filesystem fallback)
- **Session Lifetime:** 7 days (permanent sessions)
- **Remember Me Duration:** 30 days
- **Cookie Settings:**
  - Secure: True (HTTPS only)
  - HttpOnly: True (prevents XSS)
  - SameSite: Lax (Vercel compatibility)

### Redis Configuration

- **Key Prefix:** `pmb:` (to namespace sessions)
- **Connection:** Automatic reconnection on failure
- **Timeout:** 5 seconds

## Troubleshooting

### Sessions Still Not Persisting

1. **Check Redis URL format:**
   ```
   redis://default:password@host.upstash.io:port
   ```

2. **Verify environment variable is set in Vercel:**
   ```bash
   vercel env ls
   ```

3. **Check application logs:**
   Look for "Flask-Session initialized with Redis backend" message

4. **Test Redis connection:**
   ```bash
   redis-cli -u $REDIS_URL ping
   ```

### Redis Connection Errors

1. **Firewall/Network Issues:**
   - Upstash Redis should be accessible from Vercel
   - Check if your Redis instance allows connections from all IPs

2. **Authentication Errors:**
   - Verify the password in REDIS_URL is correct
   - Check if Redis instance requires TLS (use `rediss://` instead of `redis://`)

3. **Timeout Errors:**
   - Increase connection timeout in app.py
   - Check Redis instance health in Upstash dashboard

## Alternative: Database-Backed Sessions

If you prefer not to use Redis, you can use database-backed sessions:

```python
# In app.py
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
```

However, this is slower than Redis and not recommended for high-traffic applications.

## Cost Considerations

### Upstash Redis Free Tier

- **Storage:** 256 MB
- **Requests:** 10,000 commands per day
- **Bandwidth:** 200 MB per day

This is more than sufficient for PMBlueprints session storage. A typical session is ~1-2 KB, so you can store 100,000+ sessions.

### Upgrade Options

If you exceed the free tier:

- **Pay-as-you-go:** $0.20 per 100K commands
- **Pro Plan:** $10/month for 1 GB storage and 1M commands/day

## Security Best Practices

1. **Use TLS:** Always use `rediss://` (with SSL) for production
2. **Rotate Credentials:** Change Redis password periodically
3. **Limit Access:** Configure Redis to only accept connections from Vercel IPs
4. **Monitor Usage:** Set up alerts for unusual activity in Upstash dashboard

## References

- [Flask-Session Documentation](https://flask-session.readthedocs.io/)
- [Upstash Redis Documentation](https://docs.upstash.com/redis)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

