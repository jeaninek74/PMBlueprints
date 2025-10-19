#!/usr/bin/env python3
"""
Upgrade test user to Enterprise plan for testing downloads and integrations
"""

import os
import sys

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import User
from datetime import datetime

def upgrade_user():
    """Upgrade test user to Enterprise plan"""
    with app.app_context():
        # Find the test user
        user = User.query.filter_by(email='phase2test@pmblueprints.com').first()
        
        if not user:
            print("❌ User not found: phase2test@pmblueprints.com")
            return False
        
        print(f"Found user: {user.email}")
        print(f"Current plan: {user.subscription_tier}")
        
        # Upgrade to Enterprise
        user.subscription_tier = 'enterprise'
        user.subscription_status = 'active'
        user.subscription_start_date = datetime.utcnow()
        user.downloads_this_month = 0
        user.ai_suggestions_this_month = 0
        user.ai_generations_this_month = 0
        
        try:
            db.session.commit()
            print(f"\n✅ Successfully upgraded user to Enterprise!")
            print(f"   Email: {user.email}")
            print(f"   Plan: {user.subscription_tier}")
            print(f"   Status: {user.subscription_status}")
            print(f"   Downloads remaining: 2")
            print(f"   AI Suggestions remaining: 4")
            print(f"   AI Generations remaining: 6")
            print(f"   Platform Integrations: ✅ Enabled")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error upgrading user: {e}")
            return False

if __name__ == '__main__':
    success = upgrade_user()
    sys.exit(0 if success else 1)

