#!/usr/bin/env python3
"""
Force delete Business Case templates from production database
This script calls the production API endpoint to remove Business Case templates
"""

import requests
import sys

PRODUCTION_URL = "https://www.pmblueprints.net"
ENDPOINT = "/api/admin/delete-business-cases-force"

def force_delete_business_cases():
    """Call the production API to force delete Business Case templates"""
    print("=" * 80)
    print("FORCE DELETE BUSINESS CASE TEMPLATES FROM PRODUCTION")
    print("=" * 80)
    
    url = f"{PRODUCTION_URL}{ENDPOINT}"
    
    print(f"\n📡 Calling production API: {url}")
    print("⚠️  This will:")
    print("   1. Delete all download_history records for Business Case templates")
    print("   2. Delete all 30 Business Case template records")
    print("   3. Reduce template count from 955 to 925")
    
    try:
        response = requests.post(url, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("\n✅ SUCCESS!")
                print(f"   Templates deleted: {data.get('templates_deleted', 0)}")
                print(f"   Download history deleted: {data.get('download_history_deleted', 0)}")
                print(f"   Template IDs: {data.get('template_ids', [])}")
                print(f"\n🎉 Production database now has 925 templates (Business Case removed)")
                return 0
            else:
                print(f"\n❌ API returned success=False")
                print(f"   Error: {data.get('error', 'Unknown error')}")
                return 1
        else:
            print(f"\n❌ API returned error status: {response.status_code}")
            print(f"   Response: {response.text}")
            return 1
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out after 30 seconds")
        return 1
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(force_delete_business_cases())
