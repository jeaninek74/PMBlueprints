# OAuth Setup Guide for PMBlueprints

This guide explains how to set up Google and Apple OAuth authentication for PMBlueprints.

## Environment Variables Required

Add these environment variables to your Vercel project settings:

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Set Application Type to "Web application"
6. Add Authorized redirect URIs:
   - `https://pmblueprints-production.vercel.app/auth/callback/google`
   - `http://localhost:5000/auth/callback/google` (for local testing)

**Environment Variables:**
```
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

### Apple OAuth

1. Go to [Apple Developer Portal](https://developer.apple.com/)
2. Sign in with your Apple Developer account
3. Go to "Certificates, Identifiers & Profiles"
4. Create a new "Services ID"
5. Enable "Sign in with Apple"
6. Add Return URLs:
   - `https://pmblueprints-production.vercel.app/auth/callback/apple`

**Environment Variables:**
```
APPLE_CLIENT_ID=your_apple_service_id_here
APPLE_CLIENT_SECRET=your_apple_client_secret_here
```

Note: Apple OAuth requires additional setup for generating the client secret using a private key. See [Apple's documentation](https://developer.apple.com/documentation/sign_in_with_apple/generate_and_validate_tokens) for details.

## Database Migration

Run the database migration script to add OAuth fields to the User table:

```bash
python add_oauth_fields.py
```

This adds:
- `oauth_provider` (VARCHAR(50)) - 'google' or 'apple'
- `oauth_id` (VARCHAR(255)) - OAuth provider's user ID
- `email_verified` (BOOLEAN) - Email verification status

## Testing Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables in `.env` file:
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
APPLE_CLIENT_ID=your_apple_id
APPLE_CLIENT_SECRET=your_apple_secret
```

3. Run the app:
```bash
python app.py
```

4. Visit `http://localhost:5000/auth/login` and test OAuth buttons

## Deployment to Vercel

1. Add environment variables in Vercel dashboard:
   - Project Settings → Environment Variables
   - Add all OAuth credentials

2. Deploy:
```bash
git push origin main
```

Vercel will automatically deploy with OAuth enabled.

## How It Works

1. User clicks "Continue with Google" or "Continue with Apple"
2. User is redirected to Google/Apple login page
3. After successful authentication, user is redirected back to PMBlueprints
4. System checks if user exists by email:
   - If exists: Log in the user
   - If new: Create new user account with OAuth details
5. User is redirected to dashboard

## Security Notes

- OAuth users don't have passwords stored in the database
- A random secure password is generated but never used
- Email is automatically verified for OAuth users
- OAuth provider ID is stored for future logins
- Users can link multiple OAuth providers to same email

## Troubleshooting

### "Failed to get user information"
- Check that OAuth credentials are correct
- Verify redirect URIs match exactly
- Ensure OAuth scopes include 'email' and 'profile'

### "Authentication failed"
- Check Vercel logs for detailed error messages
- Verify environment variables are set correctly
- Ensure database migration was run successfully

### "OAuth provider not available"
- Verify Authlib is installed: `pip install Authlib`
- Check that oauth_config.py and routes/oauth.py exist
- Ensure blueprints are registered in app.py

## Support

For issues or questions, visit [PMBlueprints Support](https://help.manus.im)

