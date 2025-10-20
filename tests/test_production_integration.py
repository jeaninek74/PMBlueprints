#!/usr/bin/env python3
"""
Production Integration Tests
Tests all critical user flows and subscription tier permissions
Run this on every deployment to catch regressions
"""
import requests
import sys
import json
from typing import Dict, List, Tuple

# Production URL
BASE_URL = "https://www.pmblueprints.net"

# Test users for each tier
TEST_USERS = {
    'free': {
        'email': 'free@pmblueprints.com',
        'password': 'TestFree123!',
        'expected_tier': 'free',
        'can_access_integrations': False
    },
    'individual': {
        'email': 'individual@pmblueprints.com',
        'password': 'TestIndividual123!',
        'expected_tier': 'individual',
        'can_access_integrations': False
    },
    'professional': {
        'email': 'professional@pmblueprints.com',
        'password': 'TestPro123!',
        'expected_tier': 'professional',
        'can_access_integrations': False
    },
    'enterprise': {
        'email': 'enterprise@pmblueprints.com',
        'password': 'TestEnterprise123!',
        'expected_tier': 'enterprise',
        'can_access_integrations': True
    }
}

class ProductionTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        
    def test(self, name: str, condition: bool, details: str = ""):
        """Record a test result"""
        status = "✓ PASS" if condition else "✗ FAIL"
        self.results.append({
            'name': name,
            'passed': condition,
            'details': details
        })
        print(f"{status}: {name}")
        if details and not condition:
            print(f"  Details: {details}")
        return condition
    
    def login(self, email: str, password: str) -> bool:
        """Login and return success status"""
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                data={'email': email, 'password': password},
                allow_redirects=False
            )
            return response.status_code in [200, 302]
        except Exception as e:
            return False
    
    def check_integration_access(self, template_id: int = 1) -> Tuple[bool, int]:
        """Check if integration route is accessible"""
        try:
            response = self.session.get(
                f"{BASE_URL}/integrations/monday/send/{template_id}",
                allow_redirects=False
            )
            # 200 = access granted, 302 = redirect (blocked)
            return (response.status_code == 200, response.status_code)
        except Exception as e:
            return (False, 0)
    
    def test_user_tier(self, tier_name: str, user_config: Dict):
        """Test a specific subscription tier"""
        print(f"\n{'='*80}")
        print(f"Testing {tier_name.upper()} tier")
        print(f"{'='*80}")
        
        # Test 1: Login
        login_success = self.login(user_config['email'], user_config['password'])
        self.test(
            f"{tier_name}: Login",
            login_success,
            f"Failed to login as {user_config['email']}"
        )
        
        if not login_success:
            print(f"Skipping remaining tests for {tier_name} due to login failure")
            return
        
        # Test 2: Dashboard access
        try:
            response = self.session.get(f"{BASE_URL}/dashboard")
            dashboard_ok = response.status_code == 200
            self.test(
                f"{tier_name}: Dashboard access",
                dashboard_ok,
                f"Status code: {response.status_code}"
            )
        except Exception as e:
            self.test(f"{tier_name}: Dashboard access", False, str(e))
        
        # Test 3: Template browsing
        try:
            response = self.session.get(f"{BASE_URL}/templates/browse")
            browse_ok = response.status_code == 200
            self.test(
                f"{tier_name}: Template browsing",
                browse_ok,
                f"Status code: {response.status_code}"
            )
        except Exception as e:
            self.test(f"{tier_name}: Template browsing", False, str(e))
        
        # Test 4: Template preview
        try:
            response = self.session.get(f"{BASE_URL}/templates/preview/1")
            preview_ok = response.status_code == 200
            self.test(
                f"{tier_name}: Template preview",
                preview_ok,
                f"Status code: {response.status_code}"
            )
        except Exception as e:
            self.test(f"{tier_name}: Template preview", False, str(e))
        
        # Test 5: Integration access (critical test)
        can_access, status_code = self.check_integration_access()
        expected_access = user_config['can_access_integrations']
        
        if expected_access:
            # Enterprise should have access (200)
            self.test(
                f"{tier_name}: Integration access (SHOULD ALLOW)",
                can_access and status_code == 200,
                f"Expected 200, got {status_code}"
            )
        else:
            # Other tiers should be blocked (302 redirect)
            self.test(
                f"{tier_name}: Integration access (SHOULD BLOCK)",
                not can_access and status_code == 302,
                f"Expected 302 redirect, got {status_code}"
            )
        
        # Logout
        self.session.get(f"{BASE_URL}/auth/logout")
    
    def run_all_tests(self):
        """Run all production tests"""
        print("\n" + "="*80)
        print("PRODUCTION INTEGRATION TESTS")
        print("="*80)
        print(f"Testing against: {BASE_URL}")
        print()
        
        # Test each subscription tier
        for tier_name, user_config in TEST_USERS.items():
            self.test_user_tier(tier_name, user_config)
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print("\nFailed tests:")
            for result in self.results:
                if not result['passed']:
                    print(f"  ✗ {result['name']}")
                    if result['details']:
                        print(f"    {result['details']}")
        
        print("="*80)
        
        # Exit with error code if any tests failed
        return 0 if failed == 0 else 1

def main():
    tester = ProductionTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()

