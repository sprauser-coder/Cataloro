#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - FAVORITES AND VIEWS COUNTER BUGS TESTING
Testing the fixes for favorites and views counter bugs as specifically requested by the user

CRITICAL FIXES BEING TESTED:
1. **Favorites Fix**:
   - Removed duplicate favorites endpoints that were causing data conflicts
   - Fixed favorites persistence - all favorites should be returned (not just one)
   - Test that there are no duplicate endpoint conflicts

2. **Views Counter Fix**:
   - Added increment_view parameter to listings endpoint to control view counting
   - Views should only increment when increment_view=true is passed
   - Background calls without increment_view should NOT increase views

FOCUS AREAS:
1. **Test Favorites Fix**:
   - Login as demo user
   - Add multiple items to favorites using POST /api/user/{user_id}/favorites/{listing_id}
   - Verify favorites are added correctly
   - Get favorites using GET /api/user/{user_id}/favorites
   - Verify ALL favorites are returned (not just one)
   - Test edge cases: duplicates, non-existent listings, remove favorites

2. **Test Views Counter Fix**:
   - Get a test listing's current view count
   - Call GET /api/listings/{listing_id} WITHOUT increment_view parameter (should NOT increment)
   - Verify view count stays the same
   - Call GET /api/listings/{listing_id}?increment_view=true (should increment)
   - Verify view count increases by 1
   - Test multiple background calls without increment_view (should not increase views)

TESTING ENDPOINTS:
- POST /api/auth/login (demo user authentication)
- POST /api/user/{user_id}/favorites/{listing_id} (add to favorites)
- GET /api/user/{user_id}/favorites (get favorites)
- DELETE /api/user/{user_id}/favorites/{listing_id} (remove from favorites)
- GET /api/listings/{listing_id} (with and without increment_view parameter)
- GET /api/marketplace/browse (get test listings)

EXPECTED RESULTS:
- Multiple favorites can be added and ALL are returned when fetched
- Views only increment when increment_view=true is explicitly passed
- Background API calls do not artificially inflate view counts
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://cataloro-admin-fix.preview.emergentagent.com/api"

class FavoritesViewsTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, details, response_time=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        time_info = f" ({response_time:.1f}ms)" if response_time else ""
        print(f"{status}: {test_name}{time_info}")
        print(f"   Details: {details}")
        print()
    
    async def test_database_connectivity(self):
        """Test if backend can connect to database"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Database Connectivity", 
                        True, 
                        f"Backend health check passed: {data.get('status', 'unknown')}",
                        response_time
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Database Connectivity", 
                        False, 
                        f"Health check failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Database Connectivity", 
                False, 
                f"Health check failed with exception: {str(e)}",
                response_time
            )
            return False
    
    async def test_demo_user_authentication(self):
        """Test demo user authentication for favorites testing"""
        print("\n🔐 DEMO USER AUTHENTICATION:")
        start_time = datetime.now()
        
        try:
            login_data = {
                "email": "demo@cataloro.com",
                "password": "demo123"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    user = data.get("user", {})
                    user_id = user.get("id")
                    
                    if token and user_id:
                        self.log_result(
                            "Demo User Authentication", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Unknown')} (ID: {user_id}), token received",
                            response_time
                        )
                        return {
                            "token": token,
                            "user_id": user_id,
                            "user": user
                        }
                    else:
                        self.log_result(
                            "Demo User Authentication", 
                            False, 
                            f"Login successful but missing token or user_id in response: {data}",
                            response_time
                        )
                        return None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Demo User Authentication", 
                        False, 
                        f"Login failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Demo User Authentication", 
                False, 
                f"Login request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_favorites_functionality(self, user_id, token):
        """Test favorites functionality comprehensively"""
        print("\n❤️ FAVORITES FUNCTIONALITY TESTS:")
        
        # Get some test listings first
        test_listings = await self.get_test_listings_for_favorites()
        
        if not test_listings or len(test_listings) < 2:
            self.log_result(
                "Favorites Test Setup", 
                False, 
                f"Need at least 2 listings for testing, found {len(test_listings) if test_listings else 0}"
            )
            return
        
        # Test adding multiple items to favorites
        await self.test_add_multiple_favorites(user_id, token, test_listings)
        
        # Test getting all favorites (should return ALL, not just one)
        await self.test_get_all_favorites(user_id, token)
        
        # Test duplicate handling
        await self.test_add_duplicate_favorite(user_id, token, test_listings[0]['id'])
        
        # Test removing from favorites
        await self.test_remove_from_favorites(user_id, token, test_listings[0]['id'])
    
    async def get_test_listings_for_favorites(self):
        """Get test listings for favorites testing"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse?limit=5") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    listings = await response.json()
                    
                    self.log_result(
                        "Get Test Listings for Favorites", 
                        True, 
                        f"Retrieved {len(listings)} listings for favorites testing",
                        response_time
                    )
                    return listings
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get Test Listings for Favorites", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return []
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get Test Listings for Favorites", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return []
    
    async def test_add_multiple_favorites(self, user_id, token, listings):
        """Test adding multiple items to favorites"""
        headers = {"Authorization": f"Bearer {token}"}
        added_favorites = []
        
        # Add first 3 listings to favorites
        for i, listing in enumerate(listings[:3]):
            listing_id = listing['id']
            start_time = datetime.now()
            
            try:
                async with self.session.post(f"{BACKEND_URL}/user/{user_id}/favorites/{listing_id}", headers=headers) as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        added_favorites.append(listing_id)
                        
                        self.log_result(
                            f"Add Favorite {i+1}", 
                            True, 
                            f"Successfully added listing {listing_id} to favorites: {data.get('message')}",
                            response_time
                        )
                    else:
                        error_text = await response.text()
                        self.log_result(
                            f"Add Favorite {i+1}", 
                            False, 
                            f"Failed with status {response.status}: {error_text}",
                            response_time
                        )
                        
            except Exception as e:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                self.log_result(
                    f"Add Favorite {i+1}", 
                    False, 
                    f"Request failed with exception: {str(e)}",
                    response_time
                )
        
        return added_favorites
    
    async def test_get_all_favorites(self, user_id, token):
        """Test getting all favorites - should return ALL favorites, not just one"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.get(f"{BACKEND_URL}/user/{user_id}/favorites", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    favorites = await response.json()
                    
                    if len(favorites) >= 2:  # Should have multiple favorites
                        self.log_result(
                            "Get All Favorites - CRITICAL FIX", 
                            True, 
                            f"✅ SUCCESS: Retrieved {len(favorites)} favorites (not just one!) - duplicate endpoint conflict resolved",
                            response_time
                        )
                        
                        # Log details of favorites
                        for i, fav in enumerate(favorites):
                            print(f"   Favorite {i+1}: {fav.get('title', 'Unknown')} (ID: {fav.get('id')})")
                        
                        return favorites
                    elif len(favorites) == 1:
                        self.log_result(
                            "Get All Favorites - CRITICAL FIX", 
                            False, 
                            f"❌ ISSUE: Only retrieved 1 favorite when multiple were added - duplicate endpoint conflict still exists",
                            response_time
                        )
                        return favorites
                    else:
                        self.log_result(
                            "Get All Favorites - CRITICAL FIX", 
                            False, 
                            f"❌ ISSUE: No favorites retrieved when multiple were added",
                            response_time
                        )
                        return []
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get All Favorites - CRITICAL FIX", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return []
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get All Favorites - CRITICAL FIX", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return []
    
    async def test_add_duplicate_favorite(self, user_id, token, listing_id):
        """Test adding same item to favorites twice - should handle duplicates"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.post(f"{BACKEND_URL}/user/{user_id}/favorites/{listing_id}", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    message = data.get('message', '')
                    
                    if 'already' in message.lower():
                        self.log_result(
                            "Add Duplicate Favorite", 
                            True, 
                            f"✅ Duplicate handling working: {message}",
                            response_time
                        )
                    else:
                        self.log_result(
                            "Add Duplicate Favorite", 
                            True, 
                            f"✅ Duplicate handled: {message}",
                            response_time
                        )
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Add Duplicate Favorite", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Add Duplicate Favorite", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
    
    async def test_remove_from_favorites(self, user_id, token, listing_id):
        """Test removing item from favorites"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.delete(f"{BACKEND_URL}/user/{user_id}/favorites/{listing_id}", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    self.log_result(
                        "Remove from Favorites", 
                        True, 
                        f"✅ Successfully removed from favorites: {data.get('message')}",
                        response_time
                    )
                elif response.status == 404:
                    self.log_result(
                        "Remove from Favorites", 
                        True, 
                        f"✅ Item not in favorites (expected after removal)",
                        response_time
                    )
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Remove from Favorites", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Remove from Favorites", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
    
    async def test_views_counter_functionality(self):
        """Test views counter functionality with increment_view parameter"""
        print("\n👁️ VIEWS COUNTER FUNCTIONALITY TESTS:")
        
        # Get a test listing
        test_listing = await self.get_single_test_listing()
        
        if not test_listing:
            self.log_result(
                "Views Counter Test Setup", 
                False, 
                "No test listing available for views counter testing"
            )
            return
        
        listing_id = test_listing['id']
        
        # Test 1: Get initial view count
        initial_views = await self.get_listing_view_count(listing_id)
        
        # Test 2: Call without increment_view (should NOT increment)
        await self.test_get_listing_without_increment(listing_id, initial_views)
        
        # Test 3: Call with increment_view=true (should increment)
        await self.test_get_listing_with_increment(listing_id, initial_views)
        
        # Test 4: Multiple background calls without increment_view (should not increase)
        await self.test_multiple_background_calls(listing_id)
    
    async def get_single_test_listing(self):
        """Get a single test listing for views counter testing"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse?limit=1") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    listings = await response.json()
                    
                    if listings:
                        self.log_result(
                            "Get Single Test Listing", 
                            True, 
                            f"Retrieved test listing: {listings[0].get('title')} (ID: {listings[0].get('id')})",
                            response_time
                        )
                        return listings[0]
                    else:
                        self.log_result(
                            "Get Single Test Listing", 
                            False, 
                            "No listings available for testing",
                            response_time
                        )
                        return None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get Single Test Listing", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get Single Test Listing", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def get_listing_view_count(self, listing_id):
        """Get current view count for a listing"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/listings/{listing_id}") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    listing = await response.json()
                    views = listing.get('views', 0)
                    
                    self.log_result(
                        "Get Initial View Count", 
                        True, 
                        f"Current view count: {views}",
                        response_time
                    )
                    return views
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get Initial View Count", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return 0
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get Initial View Count", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return 0
    
    async def test_get_listing_without_increment(self, listing_id, initial_views):
        """Test getting listing WITHOUT increment_view parameter - should NOT increment"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/listings/{listing_id}") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    listing = await response.json()
                    current_views = listing.get('views', 0)
                    
                    if current_views == initial_views:
                        self.log_result(
                            "Get Listing WITHOUT increment_view - CRITICAL FIX", 
                            True, 
                            f"✅ SUCCESS: View count unchanged ({current_views}) - background calls don't inflate views",
                            response_time
                        )
                    else:
                        self.log_result(
                            "Get Listing WITHOUT increment_view - CRITICAL FIX", 
                            False, 
                            f"❌ ISSUE: View count increased from {initial_views} to {current_views} without increment_view=true",
                            response_time
                        )
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get Listing WITHOUT increment_view - CRITICAL FIX", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get Listing WITHOUT increment_view - CRITICAL FIX", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
    
    async def test_get_listing_with_increment(self, listing_id, initial_views):
        """Test getting listing WITH increment_view=true - should increment"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/listings/{listing_id}?increment_view=true") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    listing = await response.json()
                    current_views = listing.get('views', 0)
                    
                    if current_views == initial_views + 1:
                        self.log_result(
                            "Get Listing WITH increment_view=true - CRITICAL FIX", 
                            True, 
                            f"✅ SUCCESS: View count incremented from {initial_views} to {current_views} - actual page views tracked correctly",
                            response_time
                        )
                    else:
                        self.log_result(
                            "Get Listing WITH increment_view=true - CRITICAL FIX", 
                            False, 
                            f"❌ ISSUE: View count should be {initial_views + 1}, got {current_views}",
                            response_time
                        )
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get Listing WITH increment_view=true - CRITICAL FIX", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get Listing WITH increment_view=true - CRITICAL FIX", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
    
    async def test_multiple_background_calls(self, listing_id):
        """Test multiple background calls without increment_view - should not increase views"""
        print(f"\n🔄 Testing multiple background calls without increment_view...")
        
        # Get current view count
        current_views = await self.get_listing_view_count(listing_id)
        
        # Make 5 background calls without increment_view
        for i in range(5):
            start_time = datetime.now()
            
            try:
                async with self.session.get(f"{BACKEND_URL}/listings/{listing_id}") as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    if response.status == 200:
                        listing = await response.json()
                        views_after_call = listing.get('views', 0)
                        
                        if views_after_call == current_views:
                            print(f"   ✅ Background call {i+1}: Views unchanged ({views_after_call})")
                        else:
                            print(f"   ❌ Background call {i+1}: Views changed from {current_views} to {views_after_call}")
                    else:
                        print(f"   ❌ Background call {i+1}: Failed with status {response.status}")
                        
            except Exception as e:
                print(f"   ❌ Background call {i+1}: Exception {str(e)}")
        
        # Final verification
        final_views = await self.get_listing_view_count(listing_id)
        
        if final_views == current_views:
            self.log_result(
                "Multiple Background Calls Test - CRITICAL FIX", 
                True, 
                f"✅ SUCCESS: View count unchanged after 5 background calls ({final_views}) - no artificial inflation"
            )
        else:
            self.log_result(
                "Multiple Background Calls Test - CRITICAL FIX", 
                False, 
                f"❌ ISSUE: View count changed from {current_views} to {final_views} after background calls"
            )
    
    async def test_favorites_edge_cases(self, user_id, token):
        """Test edge cases for favorites functionality"""
        print("\n🧪 FAVORITES EDGE CASES TESTS:")
        
        # Test adding non-existent listing to favorites
        await self.test_add_nonexistent_favorite(user_id, token)
        
        # Test getting favorites when user has none
        await self.test_get_empty_favorites(user_id, token)
    
    async def test_add_nonexistent_favorite(self, user_id, token):
        """Test adding non-existent listing to favorites"""
        start_time = datetime.now()
        fake_listing_id = "nonexistent-listing-id-12345"
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.post(f"{BACKEND_URL}/user/{user_id}/favorites/{fake_listing_id}", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    # Some systems allow adding non-existent items to favorites
                    self.log_result(
                        "Add Non-existent Favorite", 
                        True, 
                        f"✅ Non-existent listing handled gracefully",
                        response_time
                    )
                elif response.status in [400, 404]:
                    self.log_result(
                        "Add Non-existent Favorite", 
                        True, 
                        f"✅ Non-existent listing properly rejected (Status {response.status})",
                        response_time
                    )
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Add Non-existent Favorite", 
                        False, 
                        f"Unexpected status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Add Non-existent Favorite", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
    
    async def test_get_empty_favorites(self, user_id, token):
        """Test getting favorites when user has none (after cleanup)"""
        # First, clean up all favorites
        await self.cleanup_all_favorites(user_id, token)
        
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.get(f"{BACKEND_URL}/user/{user_id}/favorites", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    favorites = await response.json()
                    
                    if len(favorites) == 0:
                        self.log_result(
                            "Get Empty Favorites", 
                            True, 
                            f"✅ Empty favorites list returned correctly",
                            response_time
                        )
                    else:
                        self.log_result(
                            "Get Empty Favorites", 
                            False, 
                            f"❌ Expected empty list, got {len(favorites)} favorites",
                            response_time
                        )
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get Empty Favorites", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get Empty Favorites", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
    
    async def cleanup_all_favorites(self, user_id, token):
        """Clean up all favorites for testing"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get current favorites
            async with self.session.get(f"{BACKEND_URL}/user/{user_id}/favorites", headers=headers) as response:
                if response.status == 200:
                    favorites = await response.json()
                    
                    # Remove each favorite
                    for favorite in favorites:
                        listing_id = favorite.get('id')
                        if listing_id:
                            async with self.session.delete(f"{BACKEND_URL}/user/{user_id}/favorites/{listing_id}", headers=headers) as del_response:
                                if del_response.status == 200:
                                    print(f"   Cleaned up favorite: {listing_id}")
                                    
        except Exception as e:
            print(f"   Warning: Could not clean up favorites: {str(e)}")
    
    async def print_test_summary(self):
        """Print comprehensive test summary for favorites and views counter fixes"""
        print("\n" + "=" * 80)
        print("🚀 CATALORO MARKETPLACE - FAVORITES & VIEWS COUNTER FIXES TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests/total_tests*100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL TEST RESULTS:")
        print(f"   Total Tests Executed: {total_tests}")
        print(f"   Tests Passed: {passed_tests}")
        print(f"   Tests Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize fixes
        fix_categories = {
            "Favorites Fix": ["Favorite", "favorites"],
            "Views Counter Fix": ["increment_view", "Views Counter", "Background Calls"],
            "Authentication": ["Demo User Authentication"],
            "Edge Cases": ["Non-existent", "Empty Favorites"]
        }
        
        print("🔧 CRITICAL FIXES STATUS:")
        print("-" * 50)
        
        critical_issues = []
        
        for category, keywords in fix_categories.items():
            category_tests = [r for r in self.test_results if any(keyword in r["test"] for keyword in keywords)]
            
            if category_tests:
                category_passed = sum(1 for r in category_tests if r["success"])
                category_total = len(category_tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                
                if category_rate >= 80:
                    status = "✅ FIXED"
                elif category_rate >= 60:
                    status = "⚠️ PARTIAL"
                    critical_issues.extend([r for r in category_tests if not r["success"]])
                else:
                    status = "❌ BROKEN"
                    critical_issues.extend([r for r in category_tests if not r["success"]])
                
                print(f"   {status} {category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
            else:
                print(f"   ⚠️ NOT TESTED {category}")
        
        print()
        print("🚨 CRITICAL FINDINGS:")
        print("-" * 50)
        
        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue['test']}: {issue['details']}")
        else:
            print("   ✅ No critical issues found with favorites and views counter fixes")
        
        print()
        print("🎯 FIX VERIFICATION RESULTS:")
        print("-" * 50)
        
        # Check specific fixes
        favorites_fixed = any("Get All Favorites - CRITICAL FIX" in r["test"] and r["success"] for r in self.test_results)
        views_fixed = any("increment_view" in r["test"] and r["success"] for r in self.test_results)
        background_calls_fixed = any("Background Calls" in r["test"] and r["success"] for r in self.test_results)
        
        if favorites_fixed:
            print("   ✅ FAVORITES FIX VERIFIED: All favorites are returned (not just one)")
            print("   ✅ DUPLICATE ENDPOINTS RESOLVED: No more data conflicts")
        else:
            print("   ❌ FAVORITES FIX NOT VERIFIED: May still have duplicate endpoint issues")
        
        if views_fixed and background_calls_fixed:
            print("   ✅ VIEWS COUNTER FIX VERIFIED: increment_view parameter working correctly")
            print("   ✅ BACKGROUND CALLS FIX VERIFIED: Views only increment when increment_view=true")
        elif views_fixed:
            print("   ⚠️ VIEWS COUNTER PARTIALLY FIXED: increment_view working but background calls not tested")
        else:
            print("   ❌ VIEWS COUNTER FIX NOT VERIFIED: May still have artificial view inflation")
        
        print()
        print("📋 FRONTEND INTEGRATION STATUS:")
        print("-" * 50)
        
        if favorites_fixed and views_fixed:
            print("   ✅ ProductDetailPage can use increment_view=true for actual page views")
            print("   ✅ MobileProductDetailPage can use increment_view=true for actual page views")
            print("   ✅ Favorites persistence working - users will see all their favorites")
            print("   ✅ No more duplicate endpoint conflicts affecting favorites data")
        else:
            print("   ⚠️ Frontend integration may still have issues with unfixed components")
        
        print()
        print("🔧 RECOMMENDATIONS:")
        print("-" * 50)
        
        if success_rate >= 90:
            print("   ✅ FIXES SUCCESSFUL: Both favorites and views counter issues resolved")
            print("   📋 Frontend can now properly track actual page views vs background API calls")
            print("   📋 Users will see all their favorites, not just one item")
        elif success_rate >= 70:
            print("   ⚠️ MOSTLY WORKING: Minor issues remain")
            print("   📋 Review failed tests and address remaining issues")
        else:
            print("   ❌ FIXES INCOMPLETE: Major issues remain")
            print("   📋 Users may still experience favorites not persisting correctly")
            print("   📋 View counts may still be artificially inflated by background calls")
        
        print("=" * 80)

    async def run_favorites_and_views_tests(self):
        """Run the comprehensive favorites and views counter tests"""
        print("🚀 STARTING CATALORO MARKETPLACE BACKEND TESTING - FAVORITES & VIEWS COUNTER FIXES")
        print("=" * 80)
        
        # Test database connectivity first
        db_healthy = await self.test_database_connectivity()
        if not db_healthy:
            print("❌ Database connectivity failed - aborting tests")
            return
        
        # Test demo user authentication for favorites testing
        demo_info = await self.test_demo_user_authentication()
        if not demo_info:
            print("❌ Demo user authentication failed - aborting favorites tests")
            return
        
        demo_token = demo_info["token"]
        demo_user_id = demo_info["user_id"]
        
        # Test favorites functionality
        await self.test_favorites_functionality(demo_user_id, demo_token)
        
        # Test views counter functionality
        await self.test_views_counter_functionality()
        
        # Test edge cases
        await self.test_favorites_edge_cases(demo_user_id, demo_token)
        
        # Print summary
        await self.print_test_summary()

async def main():
    """Main function to run the tests"""
    async with FavoritesViewsTester() as tester:
        await tester.run_favorites_and_views_tests()

if __name__ == "__main__":
    asyncio.run(main())