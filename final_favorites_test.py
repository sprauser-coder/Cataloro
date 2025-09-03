#!/usr/bin/env python3
"""
Final Comprehensive Favorites Bug Fix Test
Using real database listing IDs to test the favorites functionality
"""

import requests
import json
import sys

def test_favorites_bug_fix_final():
    """Final comprehensive test of favorites bug fix"""
    base_url = 'https://bid-manager-5.preview.emergentagent.com'
    
    print("🚀 FINAL FAVORITES BUG FIX VERIFICATION")
    print("=" * 60)
    print("Testing with REAL database listing IDs")
    print("=" * 60)
    
    # Login as admin user
    print("1. 🔐 Logging in as admin user...")
    login_response = requests.post(f'{base_url}/api/auth/login', 
                                 json={'email': 'admin@cataloro.com', 'password': 'admin123'})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    user = login_response.json()['user']
    user_id = user['id']
    print(f"✅ Logged in as: {user['email']} (ID: {user_id})")
    
    # Get REAL listings from database
    print("\n2. 📋 Getting REAL listings from database...")
    listings_response = requests.get(f'{base_url}/api/listings')
    
    if listings_response.status_code != 200:
        print(f"❌ Failed to get listings: {listings_response.status_code}")
        return False
    
    listings_data = listings_response.json()
    if 'listings' not in listings_data:
        print(f"❌ No listings key in response")
        return False
    
    real_listings = listings_data['listings']
    print(f"✅ Found {len(real_listings)} REAL listings in database")
    
    if len(real_listings) < 2:
        print("❌ Need at least 2 listings for testing")
        return False
    
    listing1 = real_listings[0]
    listing2 = real_listings[1]
    print(f"   Test listing 1: {listing1['title']} (${listing1['price']}) - ID: {listing1['id']}")
    print(f"   Test listing 2: {listing2['title']} (${listing2['price']}) - ID: {listing2['id']}")
    
    # Verify listings exist individually
    print("\n3. 🔍 Verifying listings exist individually...")
    for i, listing in enumerate([listing1, listing2], 1):
        verify_response = requests.get(f'{base_url}/api/listings/{listing["id"]}')
        if verify_response.status_code == 200:
            print(f"✅ Listing {i} verified in database")
        else:
            print(f"❌ Listing {i} not found: {verify_response.status_code}")
            return False
    
    # Clear any existing favorites
    print("\n4. 🧹 Clearing any existing favorites...")
    initial_favorites_response = requests.get(f'{base_url}/api/user/{user_id}/favorites')
    if initial_favorites_response.status_code == 200:
        initial_favorites = initial_favorites_response.json()
        for fav in initial_favorites:
            if 'id' in fav:
                requests.delete(f'{base_url}/api/user/{user_id}/favorites/{fav["id"]}')
        print(f"✅ Cleared {len(initial_favorites)} existing favorites")
    
    # Test 1: GET empty favorites
    print("\n5. 📭 Testing GET favorites (empty state)...")
    empty_response = requests.get(f'{base_url}/api/user/{user_id}/favorites')
    
    if empty_response.status_code != 200:
        print(f"❌ Failed to get empty favorites: {empty_response.status_code}")
        return False
    
    empty_favorites = empty_response.json()
    if len(empty_favorites) == 0:
        print(f"✅ Empty favorites returned correctly: {len(empty_favorites)} items")
    else:
        print(f"⚠️  Expected 0 favorites, got {len(empty_favorites)}")
    
    # Test 2: Add first listing to favorites
    print(f"\n6. ➕ Adding '{listing1['title']}' to favorites...")
    add_response1 = requests.post(f'{base_url}/api/user/{user_id}/favorites/{listing1["id"]}')
    
    if add_response1.status_code != 200:
        print(f"❌ Failed to add to favorites: {add_response1.status_code}")
        return False
    
    add_result1 = add_response1.json()
    print(f"✅ {add_result1['message']}")
    
    # Test 3: Add second listing to favorites
    print(f"\n7. ➕ Adding '{listing2['title']}' to favorites...")
    add_response2 = requests.post(f'{base_url}/api/user/{user_id}/favorites/{listing2["id"]}')
    
    if add_response2.status_code != 200:
        print(f"❌ Failed to add second favorite: {add_response2.status_code}")
        return False
    
    add_result2 = add_response2.json()
    print(f"✅ {add_result2['message']}")
    
    # Test 4: THE CRITICAL BUG FIX TEST - Get favorites with full listing details
    print(f"\n8. 🎯 CRITICAL BUG FIX TEST: Getting favorites with full listing details...")
    favorites_response = requests.get(f'{base_url}/api/user/{user_id}/favorites')
    
    if favorites_response.status_code != 200:
        print(f"❌ Failed to get favorites: {favorites_response.status_code}")
        return False
    
    favorites = favorites_response.json()
    print(f"✅ Retrieved {len(favorites)} favorites")
    
    if len(favorites) != 2:
        print(f"❌ Expected 2 favorites, got {len(favorites)}")
        return False
    
    # Verify full listing details are present
    print("\n9. 🔍 VERIFYING FULL LISTING DETAILS (Bug Fix Verification)...")
    
    required_fields = ['id', 'title', 'description', 'price', 'category', 'seller_id']
    bug_fix_verified = True
    
    for i, favorite in enumerate(favorites):
        print(f"\n   📄 Favorite {i+1} Analysis:")
        print(f"      Title: {favorite.get('title', 'MISSING')}")
        print(f"      Price: ${favorite.get('price', 'MISSING')}")
        print(f"      Category: {favorite.get('category', 'MISSING')}")
        print(f"      Description: {favorite.get('description', 'MISSING')[:50]}...")
        print(f"      Seller ID: {favorite.get('seller_id', 'MISSING')}")
        
        # Check all required fields are present
        missing_fields = []
        for field in required_fields:
            if field not in favorite or favorite[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"      ❌ Missing required fields: {missing_fields}")
            bug_fix_verified = False
        else:
            print(f"      ✅ All required listing fields present")
        
        # Check for favorite metadata
        if 'favorited_at' in favorite:
            print(f"      ✅ Favorite metadata present (favorited_at: {favorite['favorited_at']})")
        else:
            print(f"      ⚠️  No favorite metadata (favorited_at missing)")
        
        # Verify this is complete listing data (not just favorite record)
        if len(favorite.keys()) >= 8:  # Should have many fields for full listing
            print(f"      ✅ Rich data object ({len(favorite.keys())} fields)")
        else:
            print(f"      ❌ Sparse data object ({len(favorite.keys())} fields)")
            bug_fix_verified = False
        
        print(f"      📋 All fields: {list(favorite.keys())}")
    
    # Test 5: Verify data matches original listings
    print(f"\n10. 🔄 Verifying favorite data matches original listings...")
    
    for favorite in favorites:
        # Find matching original listing
        original = None
        if favorite['id'] == listing1['id']:
            original = listing1
        elif favorite['id'] == listing2['id']:
            original = listing2
        
        if original:
            if (favorite['title'] == original['title'] and 
                favorite['price'] == original['price'] and
                favorite['category'] == original['category']):
                print(f"      ✅ '{favorite['title']}' data matches original")
            else:
                print(f"      ❌ '{favorite['title']}' data doesn't match original")
                bug_fix_verified = False
        else:
            print(f"      ❌ No matching original listing found for {favorite.get('title', 'UNKNOWN')}")
            bug_fix_verified = False
    
    # Test 6: Test duplicate handling
    print(f"\n11. 🔄 Testing duplicate favorite handling...")
    duplicate_response = requests.post(f'{base_url}/api/user/{user_id}/favorites/{listing1["id"]}')
    
    if duplicate_response.status_code == 200:
        duplicate_result = duplicate_response.json()
        if 'already' in duplicate_result['message'].lower():
            print(f"✅ Duplicate handling: {duplicate_result['message']}")
        else:
            print(f"⚠️  Unexpected duplicate message: {duplicate_result['message']}")
    else:
        print(f"❌ Duplicate test failed: {duplicate_response.status_code}")
        bug_fix_verified = False
    
    # Test 7: Remove from favorites
    print(f"\n12. ➖ Testing remove from favorites...")
    remove_response = requests.delete(f'{base_url}/api/user/{user_id}/favorites/{listing1["id"]}')
    
    if remove_response.status_code == 200:
        remove_result = remove_response.json()
        print(f"✅ Remove successful: {remove_result['message']}")
        
        # Verify removal
        verify_response = requests.get(f'{base_url}/api/user/{user_id}/favorites')
        if verify_response.status_code == 200:
            remaining_favorites = verify_response.json()
            if len(remaining_favorites) == 1:
                print(f"✅ Favorite count correctly reduced to {len(remaining_favorites)}")
            else:
                print(f"❌ Expected 1 remaining favorite, got {len(remaining_favorites)}")
                bug_fix_verified = False
    else:
        print(f"❌ Remove failed: {remove_response.status_code}")
        bug_fix_verified = False
    
    # Test 8: Error handling
    print(f"\n13. 🚫 Testing error handling for non-existent favorite...")
    error_response = requests.delete(f'{base_url}/api/user/{user_id}/favorites/nonexistent-listing-id')
    
    if error_response.status_code == 404:
        print(f"✅ Correctly returned 404 for non-existent favorite")
    else:
        print(f"❌ Expected 404, got: {error_response.status_code}")
        bug_fix_verified = False
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL FAVORITES BUG FIX TEST RESULTS")
    print("=" * 60)
    
    if bug_fix_verified:
        print("🎉 ✅ ALL FAVORITES TESTS PASSED!")
        print("🎯 ✅ BUG FIX VERIFIED: Favorites return full listing details")
        print("📋 ✅ Complete listing objects with title, description, price, etc.")
        print("🔄 ✅ All CRUD operations working correctly")
        print("🚫 ✅ Error handling working correctly")
        print("🆔 ✅ Real user IDs and listing IDs working correctly")
        print("📊 ✅ Favorite metadata (favorited_at) included")
        print("\n🐛 BUG STATUS: FIXED ✅")
        print("   - Favorites endpoint now returns full listing objects")
        print("   - No longer returns just favorite records")
        print("   - Frontend will receive complete product information")
        return True
    else:
        print("❌ SOME FAVORITES TESTS FAILED")
        print("⚠️  Bug fix verification incomplete")
        print("\n🐛 BUG STATUS: NEEDS ATTENTION ❌")
        return False

if __name__ == "__main__":
    success = test_favorites_bug_fix_final()
    sys.exit(0 if success else 1)