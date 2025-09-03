#!/usr/bin/env python3
"""
Debug script to investigate enhanced API issues
"""

import requests
import json

def debug_favorites_api():
    """Debug favorites API issues"""
    base_url = "https://market-upgrade-2.preview.emergentagent.com"
    
    # Login user
    login_response = requests.post(f"{base_url}/api/auth/login", 
                                 json={"email": "user@cataloro.com", "password": "demo123"})
    user_data = login_response.json()
    user_id = user_data['user']['id']
    
    print(f"🔍 Debugging Favorites API for user: {user_id}")
    
    # Get current favorites
    favorites_response = requests.get(f"{base_url}/api/user/{user_id}/favorites")
    favorites = favorites_response.json()
    
    print(f"\n📋 Current favorites ({len(favorites)} items):")
    for i, fav in enumerate(favorites):
        print(f"   {i+1}. ID: {fav.get('id', 'N/A')}, Title: {fav.get('title', 'N/A')}")
    
    # Get a test listing
    browse_response = requests.get(f"{base_url}/api/marketplace/browse")
    listings = browse_response.json()
    test_listing_id = listings[0]['id']
    
    print(f"\n🎯 Test listing ID: {test_listing_id}")
    
    # Try to remove a specific favorite if it exists
    if favorites:
        existing_fav_id = favorites[0]['id']
        print(f"\n🗑️ Attempting to remove favorite with ID: {existing_fav_id}")
        
        remove_response = requests.delete(f"{base_url}/api/user/{user_id}/favorites/{existing_fav_id}")
        print(f"   Remove response: {remove_response.status_code} - {remove_response.text}")
        
        # Check favorites again
        check_response = requests.get(f"{base_url}/api/user/{user_id}/favorites")
        updated_favorites = check_response.json()
        print(f"   Favorites after removal: {len(updated_favorites)} items")

def debug_cart_api():
    """Debug cart API issues"""
    base_url = "https://market-upgrade-2.preview.emergentagent.com"
    
    # Login user
    login_response = requests.post(f"{base_url}/api/auth/login", 
                                 json={"email": "user@cataloro.com", "password": "demo123"})
    user_data = login_response.json()
    user_id = user_data['user']['id']
    
    print(f"\n🔍 Debugging Cart API for user: {user_id}")
    
    # Get current cart
    cart_response = requests.get(f"{base_url}/api/user/{user_id}/cart")
    cart_items = cart_response.json()
    
    print(f"\n🛒 Current cart ({len(cart_items)} items):")
    for i, item in enumerate(cart_items):
        print(f"   {i+1}. Item ID: {item.get('item_id', 'N/A')}, Quantity: {item.get('quantity', 'N/A')}, Price: {item.get('price', 'N/A')}")
    
    # Get a test listing
    browse_response = requests.get(f"{base_url}/api/marketplace/browse")
    listings = browse_response.json()
    test_listing_id = listings[0]['id']
    
    print(f"\n🎯 Test listing ID: {test_listing_id}")
    
    # Add item to cart with specific data
    cart_data = {
        "item_id": test_listing_id,
        "quantity": 3,
        "price": 123.45
    }
    
    print(f"\n➕ Adding item to cart: {cart_data}")
    add_response = requests.post(f"{base_url}/api/user/{user_id}/cart", json=cart_data)
    print(f"   Add response: {add_response.status_code} - {add_response.text}")
    
    # Check cart after adding
    updated_cart_response = requests.get(f"{base_url}/api/user/{user_id}/cart")
    updated_cart = updated_cart_response.json()
    
    print(f"\n🛒 Cart after adding ({len(updated_cart)} items):")
    for i, item in enumerate(updated_cart):
        print(f"   {i+1}. Item ID: {item.get('item_id', 'N/A')}, Quantity: {item.get('quantity', 'N/A')}, Price: {item.get('price', 'N/A')}")
        
        # Try to update this item
        if item.get('item_id') == test_listing_id:
            print(f"\n🔄 Updating quantity for item {test_listing_id} to 7")
            update_response = requests.put(f"{base_url}/api/user/{user_id}/cart/{test_listing_id}", 
                                         json={"quantity": 7})
            print(f"   Update response: {update_response.status_code} - {update_response.text}")
            
            # Check cart after update
            final_cart_response = requests.get(f"{base_url}/api/user/{user_id}/cart")
            final_cart = final_cart_response.json()
            
            print(f"\n🛒 Cart after update ({len(final_cart)} items):")
            for j, final_item in enumerate(final_cart):
                print(f"   {j+1}. Item ID: {final_item.get('item_id', 'N/A')}, Quantity: {final_item.get('quantity', 'N/A')}")

if __name__ == "__main__":
    debug_favorites_api()
    debug_cart_api()