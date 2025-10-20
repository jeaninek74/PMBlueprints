#!/usr/bin/env python3
"""
Create test users directly in the database
"""

import os
import sys

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_users():
    """Create all test users for different subscription tiers"""
    
    test_users = [
        {
            'email': 'free@pmblueprints.com',
            'password': 'TestFree123!',
            'first_name': 'Test',
            'last_name': 'Free',
            'company': 'Test Company Free',
            'subscription_tier': 'free',
            'subscription_status': 'active'
        },
        {
            'email': 'individual@pmblueprints.com',
            'password': 'TestIndividual123!',
            'first_name': 'Test',
            'last_name': 'Individual',
            'company': 'Test Company Individual',
            'subscription_tier': 'individual',
            'subscription_status': 'active'
        },
        {
            'email': 'professional@pmblueprints.com',
            'password': 'TestPro123!',
            'first_name': 'Test',
            'last_name': 'Professional',
            'company': 'Test Company Professional',
            'subscription_tier': 'professional',
            'subscription_status': 'active'
        },
        {
            'email': 'enterprise@pmblueprints.com',
            'password': 'TestEnterprise123!',
            'first_name': 'Test',
            'last_name': 'Enterprise',
            'company': 'Test Company Enterprise',
            'subscription_tier': 'enterprise',
            'subscription_status': 'active'
        }
    ]
    
    with app.app_context():
        created_count = 0
        updated_count = 0
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            
            if existing_user:
                # Update existing user
                existing_user.subscription_tier = user_data['subscription_tier']
                existing_user.subscription_status = user_data['subscription_status']
                existing_user.subscription_start_date = datetime.utcnow()
                existing_user.downloads_this_month = 0
                existing_user.ai_suggestions_this_month = 0
                existing_user.ai_generations_this_month = 0
                
                print(f"✓ Updated: {user_data['email']} → {user_data['subscription_tier']}")
                updated_count += 1
            else:
                # Create new user
                new_user = User(
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    company=user_data['company'],
                    subscription_tier=user_data['subscription_tier'],
                    subscription_status=user_data['subscription_status'],
                    subscription_start_date=datetime.utcnow(),
                    downloads_this_month=0,
                    ai_suggestions_this_month=0,
                    ai_generations_this_month=0,
                    created_at=datetime.utcnow()
                )
                db.session.add(new_user)
                
                print(f"✓ Created: {user_data['email']} → {user_data['subscription_tier']}")
                created_count += 1
        
        try:
            db.session.commit()
            print(f"\n✅ SUCCESS!")
            print(f"   Created: {created_count} users")
            print(f"   Updated: {updated_count} users")
            print(f"\n📋 Test Credentials:")
            print(f"   Free:         free@pmblueprints.com / TestFree123!")
            print(f"   Individual:   individual@pmblueprints.com / TestIndividual123!")
            print(f"   Professional: professional@pmblueprints.com / TestPro123!")
            print(f"   Enterprise:   enterprise@pmblueprints.com / TestEnterprise123!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating users: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = create_test_users()
    sys.exit(0 if success else 1)

