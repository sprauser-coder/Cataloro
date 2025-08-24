#!/usr/bin/env python3
"""
Simple Page Creation Test - Focus on the specific bug fix
"""

import requests
import json

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def test_page_creation():
    # Login as admin
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Admin login successful")
    
    # Test 1: Corrected field names (should work)
    corrected_data = {
        "title": "Test Page",
        "page_slug": "test-page",
        "content": "<p>This is test content</p>",
        "is_published": True,
        "meta_description": "Test page description"
    }
    
    print(f"\n🔍 Testing corrected field names: {list(corrected_data.keys())}")
    
    response = requests.post(f"{BACKEND_URL}/admin/cms/pages", json=corrected_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Page creation with corrected field names: SUCCESS")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print("❌ Page creation with corrected field names: FAILED")
        print(f"Response: {response.text}")
        return False
    
    # Test 2: Verify page was created by retrieving it
    get_response = requests.get(f"{BACKEND_URL}/admin/cms/pages", headers=headers)
    if get_response.status_code == 200:
        pages = get_response.json()
        test_page = None
        for page in pages:
            if page.get("page_slug") == "test-page":
                test_page = page
                break
        
        if test_page:
            print("✅ Page retrieval: SUCCESS")
            print(f"Created page: {test_page['title']} (slug: {test_page['page_slug']})")
        else:
            print("❌ Page retrieval: Page not found")
            return False
    else:
        print(f"❌ Page retrieval failed: {get_response.status_code}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_page_creation()
    if success:
        print("\n🎉 Page creation bug fix VERIFIED - corrected field names work correctly!")
    else:
        print("\n⚠️ Page creation bug fix test FAILED")