#!/bin/bash

# PMBlueprints Railway Environment Setup Script
# This script helps you set up all required environment variables

echo "========================================="
echo "PMBlueprints Railway Setup"
echo "========================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

echo "✅ Railway CLI installed"
echo ""

# Login to Railway
echo "🔐 Please log in to Railway..."
railway login

echo ""
echo "📝 Setting environment variables..."
echo ""

# Set Google OAuth
echo "Setting Google OAuth credentials..."
railway variables set GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID"
railway variables set GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET"
echo "✅ Google OAuth configured"

# Set Smartsheet
echo "Setting Smartsheet token..."
railway variables set SMARTSHEET_ACCESS_TOKEN="YOUR_SMARTSHEET_TOKEN"
echo "✅ Smartsheet configured"

# Set Supabase
echo "Setting Supabase credentials..."
railway variables set SUPABASE_URL="YOUR_SUPABASE_URL"
railway variables set SUPABASE_KEY="YOUR_SUPABASE_KEY"
echo "✅ Supabase configured"

# Generate and set SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set SECRET_KEY="$SECRET_KEY"
echo "✅ SECRET_KEY generated and set"

# Set Flask environment
railway variables set FLASK_ENV="production"
echo "✅ Flask environment configured"

echo ""
echo "========================================="
echo "⚠️  MANUAL SETUP REQUIRED"
echo "========================================="
echo ""
echo "You still need to add these manually:"
echo ""
echo "1. STRIPE_SECRET_KEY - Get from Stripe Dashboard"
echo "2. STRIPE_PUBLISHABLE_KEY - Get from Stripe Dashboard"
echo "3. STRIPE_WEBHOOK_SECRET - Get from Stripe Dashboard"
echo "4. OPENAI_API_KEY - Your OpenAI API key"
echo ""
echo "Add them with:"
echo "  railway variables set STRIPE_SECRET_KEY=sk_..."
echo "  railway variables set OPENAI_API_KEY=sk-..."
echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Add remaining variables (Stripe, OpenAI)"
echo "2. Run: railway up"
echo "3. Run database migration"
echo ""

