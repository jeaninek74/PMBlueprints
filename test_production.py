#!/usr/bin/env python3
"""
PMBlueprints Production Testing Script
Tests all platform modules sequentially with error handling and logging
"""
import os
import sys
import requests
import json
from datetime import datetime

# Load production environment
from dotenv import load_dotenv
load_dotenv('.env.production')

BASE_URL = os.getenv('APP_URL', 'https://pmblueprints-production.vercel.app')
TEST_EMAIL = 'test@pmblueprints.com'
TEST_PASSWORD = 'TestUser2025!'

class ProductionTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def log(self, module, test, status, message=""):
        """Log test result"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'module': module,
            'test': test,
            'status': status,
            'message': message
        }
        self.results.append(result)
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} [{module}] {test}: {status} {message}")
        
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
    
    def test_homepage(self):
        """Test homepage loads"""
        try:
            r = self.session.get(BASE_URL, timeout=10)
            if r.status_code == 200 and 'PMBlueprints' in r.text:
                self.log('Frontend', 'Homepage', 'PASS')
                return True
            else:
                self.log('Frontend', 'Homepage', 'FAIL', f'Status: {r.status_code}')
                return False
        except Exception as e:
            self.log('Frontend', 'Homepage', 'FAIL', str(e))
            return False
    
    def test_templates_page(self):
        """Test templates page loads"""
        try:
            r = self.session.get(f'{BASE_URL}/templates', timeout=10)
            if r.status_code == 200:
                self.log('Frontend', 'Templates Page', 'PASS')
                return True
            else:
                self.log('Frontend', 'Templates Page', 'FAIL', f'Status: {r.status_code}')
                return False
        except Exception as e:
            self.log('Frontend', 'Templates Page', 'FAIL', str(e))
            return False
    
    def test_login(self):
        """Test user login"""
        try:
            r = self.session.post(f'{BASE_URL}/auth/login', 
                data={'email': TEST_EMAIL, 'password': TEST_PASSWORD},
                timeout=10,
                allow_redirects=False)
            
            if r.status_code in [200, 302]:
                self.log('Authentication', 'Login', 'PASS')
                return True
            else:
                self.log('Authentication', 'Login', 'FAIL', f'Status: {r.status_code}')
                return False
        except Exception as e:
            self.log('Authentication', 'Login', 'FAIL', str(e))
            return False
    
    def test_dashboard(self):
        """Test dashboard loads"""
        try:
            r = self.session.get(f'{BASE_URL}/dashboard', timeout=10)
            if r.status_code == 200:
                self.log('Dashboard', 'Load Dashboard', 'PASS')
                return True
            else:
                self.log('Dashboard', 'Load Dashboard', 'FAIL', f'Status: {r.status_code}')
                return False
        except Exception as e:
            self.log('Dashboard', 'Load Dashboard', 'FAIL', str(e))
            return False
    
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            import psycopg2
            db_url = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.close()
            conn.close()
            self.log('Database', 'Connection', 'PASS')
            return True
        except Exception as e:
            self.log('Database', 'Connection', 'FAIL', str(e))
            return False
    
    def test_stripe_config(self):
        """Test Stripe configuration"""
        try:
            import stripe
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            # Test API key by listing products
            products = stripe.Product.list(limit=1)
            self.log('Payment', 'Stripe Config', 'PASS')
            return True
        except Exception as e:
            self.log('Payment', 'Stripe Config', 'FAIL', str(e))
            return False
    
    def test_openai_config(self):
        """Test OpenAI configuration"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            # Test with a simple completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            self.log('AI', 'OpenAI Config', 'PASS')
            return True
        except Exception as e:
            self.log('AI', 'OpenAI Config', 'FAIL', str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests sequentially"""
        print("\n" + "="*60)
        print("PMBlueprints Production Testing")
        print("="*60 + "\n")
        
        # Frontend Tests
        print("\n🌐 Frontend Tests")
        print("-" * 40)
        self.test_homepage()
        self.test_templates_page()
        
        # Authentication Tests
        print("\n🔐 Authentication Tests")
        print("-" * 40)
        self.test_login()
        self.test_dashboard()
        
        # Backend Tests
        print("\n⚙️ Backend Tests")
        print("-" * 40)
        self.test_database_connection()
        
        # Integration Tests
        print("\n🔌 Integration Tests")
        print("-" * 40)
        self.test_stripe_config()
        self.test_openai_config()
        
        # Summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total: {self.passed + self.failed}")
        print(f"📈 Success Rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        
        # Save results
        with open('test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to test_results.json")
        
        return self.failed == 0

if __name__ == '__main__':
    tester = ProductionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

