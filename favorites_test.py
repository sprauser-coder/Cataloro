#!/usr/bin/env python3
"""
Cataloro Marketplace Favorites Functionality Test Suite
Focused testing for the favorites bug fix - ensuring full listing details are returned
"""

import requests
import sys
import json
from datetime import datetime

class FavoritesAPITester:
    def __init__(self, base_url="https://cataloro-admin-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user = None
        self.test_listings = []
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def setup_test_data(self):
        """Setup test user and get available listings"""
        print("🔧 Setting up test data...")
        
        # Login as test user
        login_url = f"{self.base_url}/api/auth/login"
        login_data = {"email": "testuser@cataloro.com", "password": "test123"}
        
        try:
            response = self.session.post(login_url, json=login_data)
            if response.status_code == 200:
                self.test_user = response.json()['user']
                print(f"   Test user logged in: {self.test_user['email']} (ID: {self.test_user['id']})")
            else:
                print(f"   Failed to login test user: {response.status_code}")
                return False
        except Exception as e:
            print(f"   Error logging in: {str(e)}")
            return False

        # Get available listings to use for favorites testing
        browse_url = f"{self.base_url}/api/marketplace/browse"
        try:
            response = self.session.get(browse_url)
            if response.status_code == 200:
                self.test_listings = response.json()
                print(f"   Found {len(self.test_listings)} listings for testing")
                if len(self.test_listings) >= 2:
                    print(f"   Test listing 1: {self.test_listings[0]['title']} (ID: {self.test_listings[0]['id']})")
                    print(f"   Test listing 2: {self.test_listings[1]['title']} (ID: {self.test_listings[1]['id']})")
                    return True
                else:
                    print("   Not enough listings available for comprehensive testing")
                    return False
            else:
                print(f"   Failed to get listings: {response.status_code}")
                return False
        except Exception as e:
            print(f"   Error getting listings: {str(e)}")
            return False

    def test_get_empty_favorites(self):
        """Test GET favorites when user has no favorites (should return empty array)"""
        if not self.test_user:
            self.log_test("GET Empty Favorites", False, "No test user available")
            return False

        url = f"{self.base_url}/api/user/{self.test_user['id']}/favorites"
        
        try:
            response = self.session.get(url)
            success = response.status_code == 200
            
            if success:
                favorites = response.json()
                if isinstance(favorites, list):
                    details = f"Status: {response.status_code}, Count: {len(favorites)}"
                    self.log_test("GET Empty Favorites", True, details)
                    return True
                else:
                    self.log_test("GET Empty Favorites", False, f"Expected array, got: {type(favorites)}")
                    return False
            else:
                self.log_test("GET Empty Favorites", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("GET Empty Favorites", False, f"Error: {str(e)}")
            return False

    def test_add_to_favorites(self):
        """Test POST to add items to favorites"""
        if not self.test_user or len(self.test_listings) < 2:
            self.log_test("Add to Favorites", False, "No test data available")
            return False

        # Add first listing to favorites
        listing_id = self.test_listings[0]['id']
        url = f"{self.base_url}/api/user/{self.test_user['id']}/favorites/{listing_id}"
        
        try:
            response = self.session.post(url)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                details = f"Status: {response.status_code}, Message: {result.get('message', 'N/A')}"
                self.log_test("Add to Favorites (Item 1)", True, details)
                
                # Add second listing to favorites
                listing_id_2 = self.test_listings[1]['id']
                url_2 = f"{self.base_url}/api/user/{self.test_user['id']}/favorites/{listing_id_2}"
                
                response_2 = self.session.post(url_2)
                success_2 = response_2.status_code == 200
                
                if success_2:
                    result_2 = response_2.json()
                    details_2 = f"Status: {response_2.status_code}, Message: {result_2.get('message', 'N/A')}"
                    self.log_test("Add to Favorites (Item 2)", True, details_2)
                    return True
                else:
                    self.log_test("Add to Favorites (Item 2)", False, f"Status: {response_2.status_code}")
                    return False
            else:
                self.log_test("Add to Favorites (Item 1)", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Add to Favorites", False, f"Error: {str(e)}")
            return False

    def test_get_favorites_with_full_details(self):
        """Test GET favorites returns full listing details (THE CRITICAL BUG FIX TEST)"""
        if not self.test_user:
            self.log_test("GET Favorites Full Details", False, "No test user available")
            return False

        url = f"{self.base_url}/api/user/{self.test_user['id']}/favorites"
        
        try:
            response = self.session.get(url)
            success = response.status_code == 200
            
            if success:
                favorites = response.json()
                
                if not isinstance(favorites, list):
                    self.log_test("GET Favorites Full Details", False, f"Expected array, got: {type(favorites)}")
                    return False
                
                if len(favorites) == 0:
                    self.log_test("GET Favorites Full Details", False, "No favorites found - add items first")
                    return False
                
                # Check if favorites contain full listing details
                first_favorite = favorites[0]
                required_fields = ['id', 'title', 'description', 'price', 'category', 'seller_id']
                missing_fields = []
                
                for field in required_fields:
                    if field not in first_favorite:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_test("GET Favorites Full Details", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify this is full listing data, not just favorite records
                if 'favorited_at' in first_favorite:
                    print("   ✅ Favorite metadata included (favorited_at)")
                
                details = f"Status: {response.status_code}, Count: {len(favorites)}, Fields: {list(first_favorite.keys())}"
                print(f"   Sample favorite: {first_favorite['title']} - ${first_favorite['price']}")
                print(f"   Full listing details confirmed: title, description, price, category, seller_id all present")
                
                self.log_test("GET Favorites Full Details", True, details)
                return True
            else:
                self.log_test("GET Favorites Full Details", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("GET Favorites Full Details", False, f"Error: {str(e)}")
            return False

    def test_duplicate_favorite_handling(self):
        """Test adding duplicate favorites (should handle gracefully)"""
        if not self.test_user or len(self.test_listings) < 1:
            self.log_test("Duplicate Favorite Handling", False, "No test data available")
            return False

        # Try to add the same item again
        listing_id = self.test_listings[0]['id']
        url = f"{self.base_url}/api/user/{self.test_user['id']}/favorites/{listing_id}"
        
        try:
            response = self.session.post(url)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                message = result.get('message', '')
                
                # Should indicate it's already in favorites
                if 'already' in message.lower():
                    details = f"Status: {response.status_code}, Message: {message}"
                    self.log_test("Duplicate Favorite Handling", True, details)
                    return True
                else:
                    self.log_test("Duplicate Favorite Handling", False, f"Unexpected message: {message}")
                    return False
            else:
                self.log_test("Duplicate Favorite Handling", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Duplicate Favorite Handling", False, f"Error: {str(e)}")
            return False

    def test_remove_from_favorites(self):
        """Test DELETE to remove items from favorites"""
        if not self.test_user or len(self.test_listings) < 1:
            self.log_test("Remove from Favorites", False, "No test data available")
            return False

        # Remove first listing from favorites
        listing_id = self.test_listings[0]['id']
        url = f"{self.base_url}/api/user/{self.test_user['id']}/favorites/{listing_id}"
        
        try:
            response = self.session.delete(url)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                details = f"Status: {response.status_code}, Message: {result.get('message', 'N/A')}"
                self.log_test("Remove from Favorites", True, details)
                return True
            else:
                self.log_test("Remove from Favorites", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Remove from Favorites", False, f"Error: {str(e)}")
            return False

    def test_remove_nonexistent_favorite(self):
        """Test removing a favorite that doesn't exist (should return 404)"""
        if not self.test_user:
            self.log_test("Remove Nonexistent Favorite", False, "No test user available")
            return False

        # Try to remove a non-existent favorite
        fake_listing_id = "nonexistent-listing-id"
        url = f"{self.base_url}/api/user/{self.test_user['id']}/favorites/{fake_listing_id}"
        
        try:
            response = self.session.delete(url)
            success = response.status_code == 404  # Should return 404 for not found
            
            if success:
                details = f"Status: {response.status_code} (correctly returned 404)"
                self.log_test("Remove Nonexistent Favorite", True, details)
                return True
            else:
                self.log_test("Remove Nonexistent Favorite", False, f"Expected 404, got: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Remove Nonexistent Favorite", False, f"Error: {str(e)}")
            return False

    def test_favorites_with_real_user_and_listing_ids(self):
        """Test favorites endpoints work with real database IDs"""
        if not self.test_user or len(self.test_listings) < 1:
            self.log_test("Real ID Compatibility", False, "No test data available")
            return False

        # Verify we're using real UUIDs/IDs from the database
        user_id = self.test_user['id']
        listing_id = self.test_listings[0]['id']
        
        print(f"   Testing with real User ID: {user_id}")
        print(f"   Testing with real Listing ID: {listing_id}")
        
        # Test the full cycle with real IDs
        url = f"{self.base_url}/api/user/{user_id}/favorites/{listing_id}"
        
        try:
            # Add to favorites
            add_response = self.session.post(url)
            if add_response.status_code != 200:
                self.log_test("Real ID Compatibility", False, f"Add failed: {add_response.status_code}")
                return False
            
            # Get favorites
            get_url = f"{self.base_url}/api/user/{user_id}/favorites"
            get_response = self.session.get(get_url)
            if get_response.status_code != 200:
                self.log_test("Real ID Compatibility", False, f"Get failed: {get_response.status_code}")
                return False
            
            favorites = get_response.json()
            found_listing = any(fav['id'] == listing_id for fav in favorites)
            
            if found_listing:
                details = f"Successfully used real User ID and Listing ID from database"
                self.log_test("Real ID Compatibility", True, details)
                return True
            else:
                self.log_test("Real ID Compatibility", False, "Added favorite not found in results")
                return False
                
        except Exception as e:
            self.log_test("Real ID Compatibility", False, f"Error: {str(e)}")
            return False

    def run_favorites_tests(self):
        """Run complete favorites functionality test suite"""
        print("🚀 Starting Favorites Functionality Tests")
        print("=" * 60)
        print("Testing the bug fix: Favorites should return full listing details")
        print("=" * 60)

        # Setup test data
        if not self.setup_test_data():
            print("❌ Failed to setup test data - stopping tests")
            return False

        # Run tests in sequence
        print("\n📋 Running Favorites Test Sequence...")
        
        # 1. Test empty state
        self.test_get_empty_favorites()
        
        # 2. Add items to favorites
        self.test_add_to_favorites()
        
        # 3. THE CRITICAL TEST - Get favorites with full details
        self.test_get_favorites_with_full_details()
        
        # 4. Test duplicate handling
        self.test_duplicate_favorite_handling()
        
        # 5. Test removal
        self.test_remove_from_favorites()
        
        # 6. Test error handling
        self.test_remove_nonexistent_favorite()
        
        # 7. Test with real IDs
        self.test_favorites_with_real_user_and_listing_ids()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Favorites Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All favorites tests passed! Bug fix verified.")
            print("✅ Favorites now return full listing details instead of just favorite records")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} favorites tests failed")
            print("❌ Bug fix may not be working correctly")
            return False

def main():
    """Main test execution"""
    tester = FavoritesAPITester()
    success = tester.run_favorites_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())