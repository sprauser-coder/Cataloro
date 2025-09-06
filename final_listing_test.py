#!/usr/bin/env python3
"""
Final Listing Creation Test - After Fix
"""

import requests
import json

def test_fixed_listing_creation():
    """Test listing creation after configuration fix"""
    base_url = "https://admanager-cataloro.preview.emergentagent.com"
    
    print("🔍 FINAL LISTING CREATION TEST")
    print("=" * 40)
    
    # Setup user
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        json={"email": "finaltest@cataloro.com", "password": "demo123"},
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code == 200:
        user_data = login_response.json()
        user_id = user_data['user']['id']
        print(f"✅ User setup: {user_id}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    # Test listing creation
    listing_data = {
        "title": "Final Test - Gaming Laptop",
        "description": "High-performance gaming laptop with RTX 4070, perfect for gaming and development",
        "price": 1599.99,
        "category": "Electronics",
        "condition": "Excellent",
        "seller_id": user_id,
        "images": [
            "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400"
        ]
    }
    
    response = requests.post(
        f"{base_url}/api/listings",
        json=listing_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\nListing Creation:")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        listing_id = result.get('listing_id')
        print(f"✅ SUCCESS: Listing created with ID {listing_id}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        # Verify it appears in browse
        browse_response = requests.get(f"{base_url}/api/marketplace/browse")
        if browse_response.status_code == 200:
            listings = browse_response.json()
            found = any(l.get('id') == listing_id for l in listings)
            print(f"✅ Listing appears in browse: {found}")
        
        return True
    else:
        print(f"❌ FAILED: {response.text}")
        return False

if __name__ == "__main__":
    test_fixed_listing_creation()