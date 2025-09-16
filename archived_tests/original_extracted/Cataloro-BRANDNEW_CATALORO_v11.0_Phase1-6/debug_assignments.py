#!/usr/bin/env python3
"""
Debug script to check assignment records
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://cataloro-uxfixes.preview.emergentagent.com/api"

def get_demo_user():
    """Get demo user for testing"""
    try:
        demo_credentials = {
            "email": "demo@cataloro.com",
            "password": "demo123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login", 
            json=demo_credentials,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            return user
        else:
            return None
    except Exception as e:
        return None

def debug_specific_listing():
    """Debug a specific listing that should have catalyst data"""
    print("=" * 60)
    print("DEBUGGING SPECIFIC LISTING WITH CATALYST DATA")
    print("=" * 60)
    
    # Check the Ford listing that should have catalyst data
    listing_id = "28dedd1b-6b17-4a5c-953a-b86fbf10029b"  # Ford F150 from debug output
    
    response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
    
    if response.status_code == 200:
        listings = response.json()
        
        ford_listing = None
        for listing in listings:
            if listing.get('id') == listing_id:
                ford_listing = listing
                break
        
        if ford_listing:
            print(f"Found Ford listing: {ford_listing.get('title')}")
            print(f"ID: {ford_listing.get('id')}")
            print(f"Ceramic Weight: {ford_listing.get('ceramic_weight')}")
            print(f"PT PPM: {ford_listing.get('pt_ppm')}")
            print(f"PD PPM: {ford_listing.get('pd_ppm')}")
            print(f"RH PPM: {ford_listing.get('rh_ppm')}")
            print(f"All keys: {list(ford_listing.keys())}")
        else:
            print(f"Ford listing not found with ID: {listing_id}")
    else:
        print(f"Failed to get listings: HTTP {response.status_code}")

def test_assignment_with_catalyst_listing():
    """Test assigning a bought item that should have catalyst data"""
    print("\n" + "=" * 60)
    print("TESTING ASSIGNMENT WITH CATALYST LISTING")
    print("=" * 60)
    
    user = get_demo_user()
    if not user:
        print("❌ Could not get demo user")
        return
    
    user_id = user.get('id')
    
    # Get bought items to find one with catalyst data
    response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
    
    if response.status_code == 200:
        bought_items = response.json()
        
        # Find the item with catalyst data
        catalyst_item = None
        for item in bought_items:
            if item.get('weight', 0) > 0:  # This should be the Ford item
                catalyst_item = item
                break
        
        if catalyst_item:
            print(f"Found bought item with catalyst data: {catalyst_item.get('title')}")
            print(f"Item ID: {catalyst_item.get('id')}")
            print(f"Weight: {catalyst_item.get('weight')}")
            print(f"PT PPM: {catalyst_item.get('pt_ppm')}")
            
            # Get baskets to find one to assign to
            baskets_response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if baskets_response.status_code == 200:
                baskets = baskets_response.json()
                
                # Find an empty basket
                empty_basket = None
                for basket in baskets:
                    if len(basket.get('items', [])) == 0:
                        empty_basket = basket
                        break
                
                if empty_basket:
                    print(f"Found empty basket: {empty_basket.get('name')}")
                    print(f"Basket ID: {empty_basket.get('id')}")
                    
                    # Try to assign the item
                    assignment_data = {
                        "basket_id": empty_basket.get('id')
                    }
                    
                    assign_response = requests.put(
                        f"{BACKEND_URL}/user/bought-items/{catalyst_item.get('id')}/assign",
                        json=assignment_data,
                        timeout=10
                    )
                    
                    if assign_response.status_code == 200:
                        print("✅ Assignment successful")
                        
                        # Check the basket again to see if catalyst data is preserved
                        updated_baskets_response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
                        
                        if updated_baskets_response.status_code == 200:
                            updated_baskets = updated_baskets_response.json()
                            
                            for basket in updated_baskets:
                                if basket.get('id') == empty_basket.get('id'):
                                    items = basket.get('items', [])
                                    if items:
                                        assigned_item = items[0]
                                        print(f"\nAssigned item in basket:")
                                        print(f"  Title: {assigned_item.get('title')}")
                                        print(f"  Weight: {assigned_item.get('weight')}")
                                        print(f"  PT PPM: {assigned_item.get('pt_ppm')}")
                                        print(f"  PD PPM: {assigned_item.get('pd_ppm')}")
                                        print(f"  RH PPM: {assigned_item.get('rh_ppm')}")
                                        print(f"  Renumeration PT: {assigned_item.get('renumeration_pt')}")
                                    break
                    else:
                        print(f"❌ Assignment failed: HTTP {assign_response.status_code}")
                        if assign_response.content:
                            print(f"Error: {assign_response.json()}")
                else:
                    print("❌ No empty basket found")
            else:
                print(f"❌ Failed to get baskets: HTTP {baskets_response.status_code}")
        else:
            print("❌ No bought item with catalyst data found")
    else:
        print(f"❌ Failed to get bought items: HTTP {response.status_code}")

if __name__ == "__main__":
    debug_specific_listing()
    test_assignment_with_catalyst_listing()