#!/usr/bin/env python3
"""
Comprehensive Favorites Functionality Test
Testing the bug fix with clean admin user data
"""

import requests
import json
import sys

def test_favorites_bug_fix():
    """Test the favorites bug fix comprehensively"""
    base_url = 'https://cataloro-marketplace.preview.emergentagent.com'
    
    print("🚀 Testing Favorites Bug Fix - Full Listing Details")
    print("=" * 60)
    
    # Login as admin user
    print("1. Logging in as admin user...")
    login_response = requests.post(f'{base_url}/api/auth/login', 
                                 json={'email': 'admin@cataloro.com', 'password': 'admin123'})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    user = login_response.json()['user']
    user_id = user['id']
    print(f"✅ Logged in as: {user['email']} (ID: {user_id})")
    
    # Get available listings
    print("\n2. Getting available listings...")
    listings_response = requests.get(f'{base_url}/api/marketplace/browse')
    
    if listings_response.status_code != 200:
        print(f"❌ Failed to get listings: {listings_response.status_code}")
        return False
    
    listings = listings_response.json()
    print(f"✅ Found {len(listings)} listings")
    
    if len(listings) < 2:
        print("❌ Need at least 2 listings for testing")
        return False
    
    listing1 = listings[0]
    listing2 = listings[1]
    print(f"   Test listing 1: {listing1['title']} (${listing1['price']})")
    print(f"   Test listing 2: {listing2['title']} (${listing2['price']})")
    
    # Test 1: Get empty favorites
    print("\n3. Testing GET favorites (empty state)...")
    favorites_response = requests.get(f'{base_url}/api/user/{user_id}/favorites')
    
    if favorites_response.status_code != 200:
        print(f"❌ Failed to get favorites: {favorites_response.status_code}")
        return False
    
    initial_favorites = favorites_response.json()
    print(f"✅ Initial favorites count: {len(initial_favorites)}")
    
    # Clear any existing favorites for clean test
    for fav in initial_favorites:
        if 'id' in fav:
            requests.delete(f'{base_url}/api/user/{user_id}/favorites/{fav["id"]}')
    
    # Test 2: Add first listing to favorites
    print(f"\n4. Adding '{listing1['title']}' to favorites...")
    add_response1 = requests.post(f'{base_url}/api/user/{user_id}/favorites/{listing1["id"]}')
    
    if add_response1.status_code != 200:
        print(f"❌ Failed to add to favorites: {add_response1.status_code}")
        return False
    
    add_result1 = add_response1.json()
    print(f"✅ {add_result1['message']}")
    
    # Test 3: Add second listing to favorites
    print(f"\n5. Adding '{listing2['title']}' to favorites...")
    add_response2 = requests.post(f'{base_url}/api/user/{user_id}/favorites/{listing2["id"]}')
    
    if add_response2.status_code != 200:
        print(f"❌ Failed to add second favorite: {add_response2.status_code}")
        return False
    
    add_result2 = add_response2.json()
    print(f"✅ {add_result2['message']}")
    
    # Test 4: THE CRITICAL TEST - Get favorites with full listing details
    print(f"\n6. 🔍 CRITICAL TEST: Getting favorites with full listing details...")
    favorites_response = requests.get(f'{base_url}/api/user/{user_id}/favorites')
    
    if favorites_response.status_code != 200:
        print(f"❌ Failed to get favorites: {favorites_response.status_code}")
        return False
    
    favorites = favorites_response.json()
    print(f"✅ Retrieved {len(favorites)} favorites")
    
    if len(favorites) == 0:
        print("❌ No favorites returned after adding items")
        return False
    
    # Verify full listing details are present
    print("\n7. 🔍 Verifying full listing details in favorites...")
    
    required_fields = ['id', 'title', 'description', 'price', 'category', 'seller_id']
    success = True
    
    for i, favorite in enumerate(favorites):
        print(f"\n   Favorite {i+1}: {favorite.get('title', 'NO TITLE')}")
        print(f"   Price: ${favorite.get('price', 'NO PRICE')}")
        print(f"   Category: {favorite.get('category', 'NO CATEGORY')}")
        print(f"   Description: {favorite.get('description', 'NO DESCRIPTION')[:50]}...")
        
        # Check required fields
        missing_fields = []
        for field in required_fields:
            if field not in favorite:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   ❌ Missing fields: {missing_fields}")
            success = False
        else:
            print(f"   ✅ All required fields present")
        
        # Check for favorite metadata
        if 'favorited_at' in favorite:
            print(f"   ✅ Favorite metadata present (favorited_at: {favorite['favorited_at']})")
        
        # Verify this matches original listing data
        original_listing = listing1 if favorite['id'] == listing1['id'] else listing2
        if (favorite['title'] == original_listing['title'] and 
            favorite['price'] == original_listing['price']):
            print(f"   ✅ Data matches original listing")
        else:
            print(f"   ❌ Data doesn't match original listing")
            success = False
    
    # Test 5: Test duplicate handling
    print(f"\n8. Testing duplicate favorite handling...")
    duplicate_response = requests.post(f'{base_url}/api/user/{user_id}/favorites/{listing1["id"]}')
    
    if duplicate_response.status_code == 200:
        duplicate_result = duplicate_response.json()
        if 'already' in duplicate_result['message'].lower():
            print(f"✅ Duplicate handling: {duplicate_result['message']}")
        else:
            print(f"⚠️  Unexpected duplicate message: {duplicate_result['message']}")
    else:
        print(f"❌ Duplicate test failed: {duplicate_response.status_code}")
        success = False
    
    # Test 6: Remove from favorites
    print(f"\n9. Testing remove from favorites...")
    remove_response = requests.delete(f'{base_url}/api/user/{user_id}/favorites/{listing1["id"]}')
    
    if remove_response.status_code == 200:
        remove_result = remove_response.json()
        print(f"✅ Remove successful: {remove_result['message']}")
        
        # Verify it's removed
        verify_response = requests.get(f'{base_url}/api/user/{user_id}/favorites')
        if verify_response.status_code == 200:
            remaining_favorites = verify_response.json()
            if len(remaining_favorites) == len(favorites) - 1:
                print(f"✅ Favorite count reduced to {len(remaining_favorites)}")
            else:
                print(f"❌ Favorite count not reduced correctly")
                success = False
    else:
        print(f"❌ Remove failed: {remove_response.status_code}")
        success = False
    
    # Test 7: Error handling for non-existent favorite
    print(f"\n10. Testing error handling for non-existent favorite...")
    error_response = requests.delete(f'{base_url}/api/user/{user_id}/favorites/nonexistent-id')
    
    if error_response.status_code == 404:
        print(f"✅ Correctly returned 404 for non-existent favorite")
    else:
        print(f"❌ Expected 404, got: {error_response.status_code}")
        success = False
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL FAVORITES TESTS PASSED!")
        print("✅ Bug fix verified: Favorites now return full listing details")
        print("✅ All CRUD operations working correctly")
        print("✅ Error handling working correctly")
        print("✅ Real user IDs and listing IDs working correctly")
        return True
    else:
        print("❌ Some favorites tests failed")
        print("⚠️  Bug fix may not be complete")
        return False

if __name__ == "__main__":
    success = test_favorites_bug_fix()
    sys.exit(0 if success else 1)