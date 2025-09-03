#!/usr/bin/env python3
"""
Debug Seller Lookup Issue
Test the exact database query that's failing in the seller overview endpoint
"""

import requests
import json

def test_seller_lookup():
    base_url = "https://cataloro-marketplace-1.preview.emergentagent.com"
    
    # Login as seller
    seller_data = {"email": "seller@tendertest.com", "password": "test123"}
    response = requests.post(f"{base_url}/api/auth/login", json=seller_data)
    
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    seller_user = response.json().get('user')
    seller_id = seller_user['id']
    
    print(f"🔍 DEBUGGING SELLER LOOKUP")
    print(f"Seller ID from login: {seller_id}")
    print(f"Seller ID type: {type(seller_id)}")
    print(f"Seller ID length: {len(seller_id)}")
    
    # Test profile endpoint (this works)
    profile_response = requests.get(f"{base_url}/api/auth/profile/{seller_id}")
    print(f"\n📋 Profile endpoint test:")
    print(f"Status: {profile_response.status_code}")
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        print(f"Profile ID: {profile_data.get('id')}")
        print(f"Profile ID type: {type(profile_data.get('id'))}")
        print(f"Profile username: {profile_data.get('username')}")
    
    # Test seller overview endpoint (this fails to populate seller info)
    overview_response = requests.get(f"{base_url}/api/tenders/seller/{seller_id}/overview")
    print(f"\n📊 Seller overview endpoint test:")
    print(f"Status: {overview_response.status_code}")
    if overview_response.status_code == 200:
        overview_data = overview_response.json()
        if overview_data and len(overview_data) > 0:
            first_listing = overview_data[0]
            seller_info = first_listing.get('seller', {})
            print(f"Seller info in overview: {seller_info}")
            print(f"Seller info empty: {not bool(seller_info and seller_info.get('id'))}")
        else:
            print("No listings in overview")
    
    print(f"\n🔍 ANALYSIS:")
    print(f"The issue appears to be that the seller lookup query in the overview endpoint:")
    print(f'await db.users.find_one({{"id": "{seller_id}"}})')
    print(f"is not finding the user, even though the profile endpoint works with the same ID.")
    print(f"This suggests the database query logic in the seller overview endpoint needs investigation.")

if __name__ == "__main__":
    test_seller_lookup()