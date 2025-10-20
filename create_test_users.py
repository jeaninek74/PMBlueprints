import requests
import json

# Create test users for each tier via the registration endpoint
base_url = "https://www.pmblueprints.net"

test_users = [
    {
        "email": "free@pmblueprints.com",
        "password": "TestFree123!",
        "first_name": "Free",
        "last_name": "Tier",
        "company": "Test Company",
        "tier": "free"
    },
    {
        "email": "individual@pmblueprints.com",
        "password": "TestIndividual123!",
        "first_name": "Individual",
        "last_name": "Tier",
        "company": "Test Company",
        "tier": "individual"
    },
    {
        "email": "professional@pmblueprints.com",
        "password": "TestPro123!",
        "first_name": "Professional",
        "last_name": "Tier",
        "company": "Test Company",
        "tier": "professional"
    },
    {
        "email": "enterprise@pmblueprints.com",
        "password": "TestEnterprise123!",
        "first_name": "Enterprise",
        "last_name": "Tier",
        "company": "Test Company",
        "tier": "enterprise"
    }
]

print("Creating test users for all subscription tiers...\n")

for user in test_users:
    try:
        response = requests.post(
            f"{base_url}/auth/register",
            json=user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Created: {user['email']} ({user['tier']} tier)")
        else:
            print(f"❌ Failed: {user['email']} - {response.text}")
    except Exception as e:
        print(f"❌ Error creating {user['email']}: {str(e)}")

print("\nTest user creation complete!")
