#!/usr/bin/env python3
"""
Final Business Badge Test
Test that business badges now work correctly after the fix
"""

import requests
import json
import time

def test_business_badge_fix():
    """Test complete business badge functionality after fix"""
    base_url = "https://catalog-admin-2.preview.emergentagent.com"
    
    print("🎯 FINAL BUSINESS BADGE TEST")
    print("=" * 50)
    
    # Step 1: Create business user
    timestamp = int(time.time())
    business_data = {
        "username": f"final_business_{timestamp}",
        "email": f"finalbusiness_{timestamp}@cataloro.com", 
        "full_name": "Final Business Test",
        "is_business": True,
        "business_name": "Final Business Solutions",
        "company_name": "Final Business Solutions"
    }
    
    print("1️⃣ Creating business user...")
    register_response = requests.post(f"{base_url}/api/auth/register", json=business_data)
    
    if register_response.status_code != 200:
        print(f"   ❌ Registration failed: {register_response.status_code}")
        return False
    
    print(f"   ✅ Business user registered")
    
    # Step 2: Login as business user
    print("2️⃣ Logging in as business user...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": business_data["email"],
        "password": "demo123"
    })
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.status_code}")
        return False
    
    user_data = login_response.json().get('user', {})
    user_id = user_data.get('id')
    print(f"   ✅ Login successful, user_id: {user_id}")
    print(f"   Business fields: is_business={user_data.get('is_business')}, business_name={user_data.get('business_name')}")
    
    # Step 3: Create business listing
    print("3️⃣ Creating business listing...")
    listing_data = {
        "title": "Final Business Test - Professional Service",
        "description": "Professional business service to test business badge functionality",
        "price": 750.00,
        "category": "Services",
        "condition": "New",
        "seller_id": user_id,
        "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"]
    }
    
    listing_response = requests.post(f"{base_url}/api/listings", json=listing_data)
    
    if listing_response.status_code != 200:
        print(f"   ❌ Listing creation failed: {listing_response.status_code}")
        return False
    
    listing_id = listing_response.json().get('listing_id')
    print(f"   ✅ Business listing created: {listing_id}")
    
    # Step 4: Check browse endpoint for business badge
    print("4️⃣ Checking browse endpoint for business badge...")
    browse_response = requests.get(f"{base_url}/api/marketplace/browse")
    
    if browse_response.status_code != 200:
        print(f"   ❌ Browse failed: {browse_response.status_code}")
        return False
    
    listings = browse_response.json()
    business_listing = None
    
    for listing in listings:
        if listing.get('id') == listing_id:
            business_listing = listing
            break
    
    if not business_listing:
        print(f"   ❌ Business listing not found in browse results")
        return False
    
    seller = business_listing.get('seller', {})
    print(f"   📋 Business listing found in browse")
    print(f"   Seller object: {json.dumps(seller, indent=4)}")
    
    # Check business badge data
    is_business = seller.get('is_business')
    business_name = seller.get('business_name')
    
    print(f"\n🏷️ BUSINESS BADGE ANALYSIS:")
    print(f"   is_business: {is_business}")
    print(f"   business_name: {business_name}")
    
    if is_business is True and business_name:
        print(f"   ✅ BUSINESS BADGE WILL SHOW CORRECTLY!")
        print(f"   Badge text should be: 'Business: {business_name}'")
        return True
    else:
        print(f"   ❌ Business badge will NOT show correctly")
        print(f"   Expected: is_business=True, business_name='Final Business Solutions'")
        print(f"   Actual: is_business={is_business}, business_name='{business_name}'")
        return False

if __name__ == "__main__":
    success = test_business_badge_fix()
    if success:
        print("\n🎉 BUSINESS BADGE FIX SUCCESSFUL!")
        print("Business badges should now display correctly for business accounts.")
    else:
        print("\n❌ BUSINESS BADGE FIX FAILED!")
        print("Additional debugging required.")