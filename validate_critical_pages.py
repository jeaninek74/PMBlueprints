#!/usr/bin/env python3
"""
Validate critical pages (login, home, dashboard) to ensure they never break
"""
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Template, User
from flask import url_for

def validate_home_page():
    """Validate home page has all required elements"""
    print("\n📄 Validating Home Page...")
    
    try:
        with app.test_client() as client:
            response = client.get('/')
            
            if response.status_code != 200:
                print(f"   ❌ Home page returned status {response.status_code}")
                return False
            
            html = response.data.decode('utf-8')
            
            # Check for required elements
            required_elements = [
                'PMBlueprints',
                'AI Suggestor',
                'AI Generator',
                'Templates',
                'Login',
                'Get Started'
            ]
            
            missing = []
            for element in required_elements:
                if element not in html:
                    missing.append(element)
            
            if missing:
                print(f"   ❌ Missing elements: {', '.join(missing)}")
                return False
            
            print("   ✅ Home page validated")
            print(f"      - Status: 200 OK")
            print(f"      - All required elements present")
            return True
            
    except Exception as e:
        print(f"   ❌ Home page validation failed: {e}")
        return False

def validate_login_page():
    """Validate login page has all required elements"""
    print("\n🔐 Validating Login Page...")
    
    try:
        with app.test_client() as client:
            response = client.get('/auth/login')
            
            if response.status_code != 200:
                print(f"   ❌ Login page returned status {response.status_code}")
                return False
            
            html = response.data.decode('utf-8')
            
            # Check for required elements
            required_elements = [
                'Sign In',
                'Email',
                'Password'
            ]
            
            missing = []
            for element in required_elements:
                if element not in html:
                    missing.append(element)
            
            if missing:
                print(f"   ❌ Missing elements: {', '.join(missing)}")
                return False
            
            print("   ✅ Login page validated")
            print(f"      - Status: 200 OK")
            print(f"      - All required elements present")
            return True
            
    except Exception as e:
        print(f"   ❌ Login page validation failed: {e}")
        return False

def validate_signup_page():
    """Validate signup page has all required elements"""
    print("\n📝 Validating Signup Page...")
    
    try:
        with app.test_client() as client:
            response = client.get('/auth/register')
            
            if response.status_code != 200:
                print(f"   ❌ Signup page returned status {response.status_code}")
                return False
            
            html = response.data.decode('utf-8')
            
            # Check for required elements
            required_elements = [
                'Register',
                'First Name',
                'Last Name',
                'Email',
                'Password'
            ]
            
            missing = []
            for element in required_elements:
                if element not in html:
                    missing.append(element)
            
            if missing:
                print(f"   ❌ Missing elements: {', '.join(missing)}")
                return False
            
            print("   ✅ Signup page validated")
            print(f"      - Status: 200 OK")
            print(f"      - All required elements present")
            return True
            
    except Exception as e:
        print(f"   ❌ Signup page validation failed: {e}")
        return False

def validate_dashboard_page():
    """Validate dashboard page loads correctly for authenticated users"""
    print("\n📊 Validating Dashboard Page...")
    
    try:
        with app.app_context():
            # Get a test user
            test_user = User.query.filter_by(email='enterprise@pmblueprints.com').first()
            
            if not test_user:
                print("   ⚠️  Test user not found, skipping dashboard validation")
                return True  # Don't fail if test user doesn't exist
        
        with app.test_client() as client:
            # Login as test user
            client.post('/auth/login', data={
                'email': 'enterprise@pmblueprints.com',
                'password': 'TestEnterprise123!'
            })
            
            response = client.get('/dashboard')
            
            if response.status_code != 200:
                print(f"   ❌ Dashboard page returned status {response.status_code}")
                return False
            
            html = response.data.decode('utf-8')
            
            # Check for required elements
            required_elements = [
                'Dashboard',
                'Welcome',
                'Templates',
                'Subscription'
            ]
            
            missing = []
            for element in required_elements:
                if element not in html:
                    missing.append(element)
            
            if missing:
                print(f"   ❌ Missing elements: {', '.join(missing)}")
                return False
            
            print("   ✅ Dashboard page validated")
            print(f"      - Status: 200 OK")
            print(f"      - All required elements present")
            return True
            
    except Exception as e:
        print(f"   ❌ Dashboard page validation failed: {e}")
        return False

def validate_ai_suggestor_page():
    """Validate AI Suggestor page has all required elements"""
    print("\n🤖 Validating AI Suggestor Page...")
    
    try:
        with app.test_client() as client:
            response = client.get('/ai_suggestions', follow_redirects=True)
            
            if response.status_code != 200:
                print(f"   ❌ AI Suggestor page returned status {response.status_code}")
                return False
            
            html = response.data.decode('utf-8')
            
            # Check for required elements
            required_elements = [
                'AI Suggestor',
                'Template Type'
            ]
            
            missing = []
            for element in required_elements:
                if element not in html:
                    missing.append(element)
            
            if missing:
                print(f"   ❌ Missing elements: {', '.join(missing)}")
                return False
            
            print("   ✅ AI Suggestor page validated")
            print(f"      - Status: 200 OK")
            print(f"      - All required elements present")
            return True
            
    except Exception as e:
        print(f"   ❌ AI Suggestor page validation failed: {e}")
        return False

def validate_ai_generator_page():
    """Validate AI Generator page has all required elements"""
    print("\n🎨 Validating AI Generator Page...")
    
    try:
        with app.test_client() as client:
            response = client.get('/ai-generator')
            
            if response.status_code != 200:
                print(f"   ❌ AI Generator page returned status {response.status_code}")
                return False
            
            html = response.data.decode('utf-8')
            
            # Check for required elements
            required_elements = [
                'AI Generator',
                'Methodology',
                'Generate'
            ]
            
            missing = []
            for element in required_elements:
                if element not in html:
                    missing.append(element)
            
            if missing:
                print(f"   ❌ Missing elements: {', '.join(missing)}")
                return False
            
            print("   ✅ AI Generator page validated")
            print(f"      - Status: 200 OK")
            print(f"      - All required elements present")
            return True
            
    except Exception as e:
        print(f"   ❌ AI Generator page validation failed: {e}")
        return False

def validate_template_count():
    """Validate template count is correct"""
    print("\n📚 Validating Template Count...")
    
    try:
        with app.app_context():
            template_count = Template.query.count()
            
            if template_count == 0:
                print(f"   ❌ No templates found in database")
                return False
            
            print(f"   ✅ Template count: {template_count}")
            return True
            
    except Exception as e:
        print(f"   ❌ Template count validation failed: {e}")
        return False

def main():
    """Run all validations"""
    print("=" * 80)
    print("CRITICAL PAGES VALIDATION")
    print("=" * 80)
    
    results = {
        'Home Page': validate_home_page(),
        'Login Page': validate_login_page(),
        'Signup Page': validate_signup_page(),
        'Dashboard Page': validate_dashboard_page(),
        'AI Suggestor Page': validate_ai_suggestor_page(),
        'AI Generator Page': validate_ai_generator_page(),
        'Template Count': validate_template_count()
    }
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for page, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{page}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All critical pages validated successfully!")
        return 0
    else:
        print("\n❌ Some critical pages failed validation")
        return 1

if __name__ == '__main__':
    sys.exit(main())

