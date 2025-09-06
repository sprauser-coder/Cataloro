#!/usr/bin/env python3
"""
Business User Registration Fix Test
Test and fix the business user registration issue
"""

import requests
import json

def test_business_user_registration():
    """Test business user registration and profile retrieval"""
    base_url = "https://browse-ads.preview.emergentagent.com"
    
    print("🔧 TESTING BUSINESS USER REGISTRATION FIX")
    print("=" * 50)
    
    # Test 1: Register business user with explicit business fields
    import time
    timestamp = int(time.time())
    business_data = {
        "username": f"fix_test_business_{timestamp}",
        "email": f"fixtest_{timestamp}@business.com", 
        "full_name": "Fix Test Business",
        "is_business": True,
        "business_name": "Fix Test Solutions",
        "company_name": "Fix Test Solutions"
    }
    
    print("1️⃣ Registering business user...")
    response = requests.post(f"{base_url}/api/auth/register", json=business_data)
    
    if response.status_code == 200:
        result = response.json()
        user_id = result.get('user_id')
        print(f"   ✅ Registration successful: {user_id}")
        
        # Test 2: Login and check user data
        print("2️⃣ Testing login...")
        login_response = requests.post(f"{base_url}/api/auth/login", json={
            "email": business_data["email"],
            "password": "demo123"
        })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            user_data = login_data.get('user', {})
            print(f"   Login user data: {json.dumps(user_data, indent=2)}")
            
            # Test 3: Get profile
            print("3️⃣ Testing profile retrieval...")
            profile_response = requests.get(f"{base_url}/api/auth/profile/{user_data.get('id')}")
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"   Profile data: {json.dumps(profile_data, indent=2)}")
                
                # Check if business fields are present
                has_is_business = 'is_business' in profile_data
                is_business_value = profile_data.get('is_business')
                has_business_name = 'business_name' in profile_data or 'company_name' in profile_data
                
                print(f"\n📊 BUSINESS FIELD ANALYSIS:")
                print(f"   has_is_business: {has_is_business}")
                print(f"   is_business_value: {is_business_value}")
                print(f"   has_business_name: {has_business_name}")
                
                if has_is_business and is_business_value is True:
                    print("   ✅ Business registration working correctly")
                    return True
                else:
                    print("   ❌ Business registration NOT working - fields missing or incorrect")
                    return False
            else:
                print(f"   ❌ Profile retrieval failed: {profile_response.status_code}")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
    else:
        print(f"   ❌ Registration failed: {response.status_code} - {response.text}")
    
    return False

if __name__ == "__main__":
    test_business_user_registration()