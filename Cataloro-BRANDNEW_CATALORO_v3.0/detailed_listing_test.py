#!/usr/bin/env python3
"""
Detailed Listing Creation Analysis
Investigating specific issues reported by users
"""

import requests
import json

def test_listing_creation_detailed():
    """Test the exact scenario users are reporting"""
    base_url = "https://cataloro-marketplace-3.preview.emergentagent.com"
    
    print("🔍 DETAILED LISTING CREATION ANALYSIS")
    print("=" * 50)
    
    # Setup user
    print("\n1. Setting up test user...")
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        json={"email": "testuser@cataloro.com", "password": "demo123"},
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code == 200:
        user_data = login_response.json()
        user_id = user_data['user']['id']
        print(f"   ✅ User ID: {user_id}")
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")
        return
    
    # Test 1: Exact frontend payload
    print("\n2. Testing with typical frontend payload...")
    frontend_payload = {
        "title": "iPhone 14 Pro Max",
        "description": "Excellent condition iPhone 14 Pro Max, 256GB, Space Black. Includes original box and charger.",
        "price": 899.99,
        "category": "Electronics",
        "condition": "Like New",
        "seller_id": user_id,
        "images": [
            "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400"
        ]
    }
    
    response = requests.post(
        f"{base_url}/api/listings",
        json=frontend_payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        listing_id = response.json().get('listing_id')
        print(f"   ✅ Listing created successfully: {listing_id}")
        
        # Test 3: Verify listing exists
        print("\n3. Verifying listing exists...")
        get_response = requests.get(
            f"{base_url}/api/listings/{listing_id}",
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Get Status: {get_response.status_code}")
        if get_response.status_code == 200:
            listing_data = get_response.json()
            print(f"   ✅ Listing retrieved: {listing_data.get('title')}")
            print(f"   Price: ${listing_data.get('price')}")
            print(f"   Category: {listing_data.get('category')}")
            print(f"   Images: {len(listing_data.get('images', []))} images")
        else:
            print(f"   ❌ Failed to retrieve listing: {get_response.text}")
    else:
        print(f"   ❌ Listing creation failed: {response.text}")
    
    # Test 4: Check marketplace browse
    print("\n4. Checking marketplace browse...")
    browse_response = requests.get(
        f"{base_url}/api/marketplace/browse",
        headers={'Content-Type': 'application/json'}
    )
    
    if browse_response.status_code == 200:
        listings = browse_response.json()
        print(f"   ✅ Browse working: {len(listings)} total listings")
        
        # Check if our listing appears
        our_listing = None
        for listing in listings:
            if listing.get('title') == frontend_payload['title']:
                our_listing = listing
                break
        
        if our_listing:
            print(f"   ✅ Our listing appears in browse results")
        else:
            print(f"   ⚠️  Our listing not found in browse results")
    else:
        print(f"   ❌ Browse failed: {browse_response.status_code}")
    
    # Test 5: Test error scenarios
    print("\n5. Testing error scenarios...")
    
    # Missing seller_id
    error_payload = {
        "title": "Error Test",
        "description": "Testing error handling",
        "price": 100.00,
        "category": "Electronics",
        "condition": "Good"
        # Missing seller_id
    }
    
    error_response = requests.post(
        f"{base_url}/api/listings",
        json=error_payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Missing seller_id - Status: {error_response.status_code}")
    if error_response.status_code == 400:
        print(f"   ✅ Proper error handling for missing seller_id")
    else:
        print(f"   ⚠️  Unexpected response: {error_response.text}")
    
    # Test 6: Check data types and validation
    print("\n6. Testing data validation...")
    
    # Invalid price type (string instead of number)
    invalid_payload = {
        "title": "Invalid Price Test",
        "description": "Testing price validation",
        "price": "invalid_price",
        "category": "Electronics",
        "condition": "Good",
        "seller_id": user_id
    }
    
    invalid_response = requests.post(
        f"{base_url}/api/listings",
        json=invalid_payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Invalid price type - Status: {invalid_response.status_code}")
    if invalid_response.status_code in [400, 422]:
        print(f"   ✅ Proper validation for invalid price")
    else:
        print(f"   ⚠️  Validation issue: {invalid_response.text}")
    
    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE")

if __name__ == "__main__":
    test_listing_creation_detailed()