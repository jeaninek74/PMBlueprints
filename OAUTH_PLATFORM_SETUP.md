# Platform OAuth Integration Setup Guide

This guide explains how to set up OAuth integrations for Monday.com, Smartsheet, Google Sheets, and Microsoft 365.

## Overview

The OAuth implementation allows users to:
1. Click a "Connect" button
2. Authorize PMBlueprints to access their platform account
3. Automatically upload templates to their connected platforms

## Prerequisites

You need to register PMBlueprints as an OAuth application with each platform to get Client IDs and Secrets.

---

## Monday.com OAuth Setup

### 1. Create Monday.com App

1. Go to https://monday.com/developers/apps
2. Click "Create App"
3. Fill in app details:
   - **App Name**: PMBlueprints
   - **Description**: Project management template platform
   - **Website**: https://www.pmblueprints.net

### 2. Configure OAuth

1. Go to "OAuth & Permissions"
2. Add redirect URI: `https://www.pmblueprints.net/integrations/oauth/monday/callback`
3. Select scopes:
   - `boards:read`
   - `boards:write`
4. Save settings

### 3. Get Credentials

1. Copy the **Client ID**
2. Copy the **Client Secret**
3. Add to environment variables:
   ```bash
   MONDAY_CLIENT_ID=your_client_id
   MONDAY_CLIENT_SECRET=your_client_secret
   ```

---

## Smartsheet OAuth Setup

### 1. Register Application

1. Go to https://developers.smartsheet.com/register
2. Register as a developer
3. Create new app:
   - **App Name**: PMBlueprints
   - **Description**: PM template integration
   - **App URL**: https://www.pmblueprints.net

### 2. Configure OAuth

1. Set redirect URI: `https://www.pmblueprints.net/integrations/oauth/smartsheet/callback`
2. Select scopes:
   - `READ_SHEETS`
   - `WRITE_SHEETS`
   - `CREATE_SHEETS`

### 3. Get Credentials

1. Copy **App Client ID**
2. Copy **App Secret**
3. Add to environment variables:
   ```bash
   SMARTSHEET_CLIENT_ID=your_client_id
   SMARTSHEET_CLIENT_SECRET=your_client_secret
   ```

---

## Google Sheets OAuth Setup

### 1. Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Create new project: "PMBlueprints"
3. Enable APIs:
   - Google Sheets API
   - Google Drive API

### 2. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **Web application**
4. Add authorized redirect URI:
   - `https://www.pmblueprints.net/integrations/oauth/google/callback`

### 3. Configure OAuth Consent Screen

1. User type: **External**
2. App information:
   - **App name**: PMBlueprints
   - **User support email**: support@pmblueprints.net
   - **Developer contact**: support@pmblueprints.net
3. Scopes:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive.file`

### 4. Get Credentials

1. Copy **Client ID**
2. Copy **Client Secret**
3. Add to environment variables:
   ```bash
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   ```

**Note**: You can reuse the same Google OAuth credentials used for user authentication.

---

## Microsoft 365 OAuth Setup

### 1. Register Application in Azure

1. Go to https://portal.azure.com
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Fill in details:
   - **Name**: PMBlueprints
   - **Supported account types**: Multitenant
   - **Redirect URI**: Web - `https://www.pmblueprints.net/integrations/oauth/microsoft/callback`

### 2. Configure API Permissions

1. Go to "API permissions"
2. Add permissions:
   - **Microsoft Graph**:
     - `Files.ReadWrite.All`
     - `offline_access`
3. Grant admin consent

### 3. Create Client Secret

1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Description: "PMBlueprints Integration"
4. Expiry: 24 months
5. Copy the secret value immediately (it won't be shown again)

### 4. Get Credentials

1. Copy **Application (client) ID**
2. Copy **Client secret** (from step 3)
3. Add to environment variables:
   ```bash
   MICROSOFT_CLIENT_ID=your_client_id
   MICROSOFT_CLIENT_SECRET=your_client_secret
   ```

---

## Database Migration

After setting up OAuth credentials, run the database migration:

```bash
python3 add_oauth_integration_fields.py
```

This adds the following fields to `integration_settings` table:
- OAuth access tokens
- OAuth refresh tokens
- Connection status
- Connection timestamps

---

## Environment Variables Summary

Add all these to your Railway/deployment environment:

```bash
# Monday.com
MONDAY_CLIENT_ID=xxx
MONDAY_CLIENT_SECRET=xxx

# Smartsheet
SMARTSHEET_CLIENT_ID=xxx
SMARTSHEET_CLIENT_SECRET=xxx

# Google (can reuse existing if already set for auth)
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx

# Microsoft 365
MICROSOFT_CLIENT_ID=xxx
MICROSOFT_CLIENT_SECRET=xxx
```

---

## Testing OAuth Flow

### For Each Platform:

1. **Connect**: User clicks "Connect [Platform]" button
2. **Authorize**: User is redirected to platform login
3. **Callback**: Platform redirects back with authorization code
4. **Token Exchange**: PMBlueprints exchanges code for access token
5. **Store**: Token is saved in database
6. **Upload**: User can now upload templates to platform

### Test Checklist:

- [ ] Monday.com connect/disconnect works
- [ ] Smartsheet connect/disconnect works
- [ ] Google Sheets connect/disconnect works
- [ ] Microsoft 365 connect/disconnect works
- [ ] Connection status displays correctly
- [ ] Upload buttons appear after connection
- [ ] Tokens are stored securely in database

---

## Security Notes

1. **Token Storage**: All OAuth tokens are encrypted in the database
2. **Refresh Tokens**: Implement token refresh logic for expired tokens
3. **Scope Limitation**: Only request minimum required permissions
4. **HTTPS Required**: OAuth flows must use HTTPS in production
5. **State Parameter**: Add CSRF protection with state parameter (recommended)

---

## Troubleshooting

### "Redirect URI mismatch" error
- Verify the redirect URI in platform settings exactly matches the callback URL
- Check for trailing slashes
- Ensure using HTTPS in production

### "Invalid client" error
- Verify Client ID and Secret are correct
- Check environment variables are set properly
- Ensure credentials haven't expired

### Connection fails silently
- Check application logs for errors
- Verify database migration ran successfully
- Test with platform's OAuth playground first

---

## Next Steps

After OAuth is working:

1. Implement template upload functionality for each platform
2. Add token refresh logic for expired tokens
3. Create upload UI in template detail pages
4. Add usage analytics for integrations
5. Implement error handling and user notifications

---

**Status**: Ready for implementation
**Last Updated**: October 16, 2025

