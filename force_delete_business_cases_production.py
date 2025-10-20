#!/usr/bin/env python3
"""
Force delete Business Case templates from PRODUCTION database
This script connects to production and removes the 30 Business Case templates
"""
import sys
import os
import requests

# Production URL
PRODUCTION_URL = "https://www.pmblueprints.net"

def force_delete_business_cases():
    """Call the production API to force delete Business Case templates"""
    print("=" * 80)
    print("FORCE DELETE BUSINESS CASE TEMPLATES FROM PRODUCTION")
    print("=" * 80)
    
    endpoint = f"{PRODUCTION_URL}/api/admin/delete-business-cases-force"
    
    print(f"\n📡 Calling production endpoint: {endpoint}")
    print("⚠️  This will delete Business Case templates and their download history")
    
    try:
        response = requests.post(endpoint, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("\n✅ SUCCESS!")
                print(f"   Templates deleted: {data.get('templates_deleted', 0)}")
                print(f"   Download history deleted: {data.get('download_history_deleted', 0)}")
                
                if data.get('template_ids'):
                    print(f"   Template IDs removed: {data['template_ids'][:5]}..." if len(data['template_ids']) > 5 else f"   Template IDs removed: {data['template_ids']}")
                
                return True
            else:
                print(f"\n❌ API returned success=False")
                print(f"   Error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out after 30 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def verify_production_template_count():
    """Verify the production database has 925 templates"""
    print("\n" + "=" * 80)
    print("VERIFYING PRODUCTION TEMPLATE COUNT")
    print("=" * 80)
    
    health_endpoint = f"{PRODUCTION_URL}/api/health-check"
    
    try:
        response = requests.get(health_endpoint, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            template_count = data.get('checks', {}).get('database', {}).get('template_count', 0)
            
            print(f"\n📊 Production Template Count: {template_count}")
            
            if template_count == 925:
                print("✅ Correct! Production has 925 templates (Business Case removed)")
                return True
            elif template_count == 955:
                print("❌ Production still has 955 templates (Business Case NOT removed)")
                return False
            else:
                print(f"⚠️  Unexpected count: {template_count}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking template count: {e}")
        return False

def main():
    """Main execution"""
    print("\n🚀 Starting Business Case template deletion from production...")
    
    # Step 1: Force delete
    delete_success = force_delete_business_cases()
    
    if not delete_success:
        print("\n❌ Failed to delete Business Case templates")
        return 1
    
    # Step 2: Verify count
    print("\n⏳ Waiting 3 seconds for database to update...")
    import time
    time.sleep(3)
    
    verify_success = verify_production_template_count()
    
    if verify_success:
        print("\n" + "=" * 80)
        print("🎉 SUCCESS! Production database cleaned:")
        print("   - Business Case templates: DELETED")
        print("   - Template count: 925")
        print("   - Platform: READY")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print("⚠️  Deletion completed but verification failed")
        print("   Please check production manually")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())

