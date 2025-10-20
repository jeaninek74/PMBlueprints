#!/usr/bin/env python3
"""
Diagnose why platform integrations are being blocked for Enterprise users
"""

import sys
sys.path.insert(0, '/home/ubuntu/pmb_repo')

from app import app
from database import db
from models import User
from utils.subscription_security import check_feature_access, get_user_tier_limits, TIER_LIMITS

def diagnose():
    with app.app_context():
        # Test with enterprise user
        user = User.query.filter_by(email='enterprise@pmblueprints.com').first()
        
        if not user:
            print("❌ Enterprise user not found in database!")
            return
        
        print("=" * 80)
        print("ENTERPRISE USER DIAGNOSTICS")
        print("=" * 80)
        print(f"\n1. User Object:")
        print(f"   Email: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   First Name: {user.first_name}")
        print(f"   Last Name: {user.last_name}")
        print(f"   Subscription Tier: '{user.subscription_tier}'")
        print(f"   Subscription Tier (type): {type(user.subscription_tier)}")
        print(f"   Subscription Tier (repr): {repr(user.subscription_tier)}")
        print(f"   Subscription Status: {user.subscription_status}")
        print(f"   Is Authenticated: {user.is_authenticated}")
        
        print(f"\n2. TIER_LIMITS Configuration:")
        print(f"   Enterprise config exists: {'enterprise' in TIER_LIMITS}")
        if 'enterprise' in TIER_LIMITS:
            print(f"   Enterprise platform_integrations: {TIER_LIMITS['enterprise'].get('platform_integrations')}")
        
        print(f"\n3. get_user_tier_limits() Result:")
        limits = get_user_tier_limits(user)
        print(f"   Returned limits: {limits}")
        print(f"   platform_integrations value: {limits.get('platform_integrations')}")
        print(f"   platform_integrations type: {type(limits.get('platform_integrations'))}")
        
        print(f"\n4. check_feature_access() Result:")
        has_access = check_feature_access(user, 'platform_integrations')
        print(f"   Result: {has_access}")
        print(f"   Result type: {type(has_access)}")
        print(f"   Result is True: {has_access is True}")
        print(f"   Result == True: {has_access == True}")
        print(f"   bool(Result): {bool(has_access)}")
        print(f"   not Result: {not has_access}")
        
        print(f"\n5. Decorator Logic Simulation:")
        print(f"   if not check_feature_access(current_user, 'platform_integrations'):")
        if not has_access:
            print(f"      ❌ BLOCKED - Would redirect to pricing")
        else:
            print(f"      ✅ ALLOWED - Would proceed to integration page")
        
        print("\n" + "=" * 80)
        
        # Test all tiers
        print("\nTESTING ALL TIERS:")
        print("=" * 80)
        
        for tier_name in ['free', 'individual', 'professional', 'enterprise']:
            # Create a mock user object
            test_user = User(email=f'test@{tier_name}.com', subscription_tier=tier_name)
            limits = get_user_tier_limits(test_user)
            has_access = check_feature_access(test_user, 'platform_integrations')
            
            status = "✅ ALLOWED" if has_access else "❌ BLOCKED"
            print(f"{tier_name.upper():15} - platform_integrations: {limits.get('platform_integrations'):5} - {status}")

if __name__ == '__main__':
    diagnose()

