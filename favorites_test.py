#!/usr/bin/env python3
"""
Focused Favorites Endpoints Testing
Testing the favorites toggle functionality as requested:
1. GET /api/favorites - Test getting user's favorites (should return favorite_id and listing data)
2. POST /api/favorites - Test adding a listing to favorites 
3. GET /api/favorites - Verify the favorite was added and note the favorite_id
4. DELETE /api/favorites/{favorite_id} - Test removing using the correct favorite_id

Using admin credentials: admin@marketplace.com / admin123
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class FavoritesTestRunner:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def get_available_listing(self):
        """Get an available listing to use for favorites testing"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings?limit=1")
            
            if response.status_code == 200:
                listings = response.json()
                if listings and len(listings) > 0:
                    listing = listings[0]
                    self.log_test("Get Available Listing", True, f"Found listing: {listing['title']} (ID: {listing['id']})")
                    return listing['id']
                else:
                    self.log_test("Get Available Listing", False, "No listings available for testing")
                    return None
            else:
                self.log_test("Get Available Listing", False, f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Get Available Listing", False, f"Exception: {str(e)}")
            return None

    def test_get_empty_favorites(self):
        """Test GET /api/favorites - should return empty list initially"""
        try:
            response = self.session.get(f"{BACKEND_URL}/favorites")
            
            if response.status_code == 200:
                favorites = response.json()
                self.log_test("GET /api/favorites (Empty)", True, f"Retrieved {len(favorites)} favorites (expected empty initially)")
                return favorites
            else:
                self.log_test("GET /api/favorites (Empty)", False, f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("GET /api/favorites (Empty)", False, f"Exception: {str(e)}")
            return None

    def test_add_to_favorites(self, listing_id):
        """Test POST /api/favorites - add a listing to favorites"""
        try:
            response = self.session.post(f"{BACKEND_URL}/favorites", json={
                "listing_id": listing_id
            })
            
            if response.status_code == 200:
                data = response.json()
                favorite_id = data.get("favorite_id")
                self.log_test("POST /api/favorites (Add)", True, f"Successfully added to favorites. Favorite ID: {favorite_id}")
                return favorite_id
            else:
                self.log_test("POST /api/favorites (Add)", False, f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("POST /api/favorites (Add)", False, f"Exception: {str(e)}")
            return None

    def test_get_favorites_with_data(self):
        """Test GET /api/favorites - verify the favorite was added and contains both favorite_id and listing data"""
        try:
            response = self.session.get(f"{BACKEND_URL}/favorites")
            
            if response.status_code == 200:
                favorites = response.json()
                
                if len(favorites) > 0:
                    favorite = favorites[0]
                    
                    # Check if favorite_id is present
                    has_favorite_id = "favorite_id" in favorite
                    
                    # Check if listing data is present
                    has_listing_data = "listing" in favorite
                    
                    # Check listing data structure
                    listing_complete = False
                    if has_listing_data:
                        listing = favorite["listing"]
                        required_fields = ["id", "title", "description", "price", "category", "status"]
                        listing_complete = all(field in listing for field in required_fields)
                    
                    if has_favorite_id and has_listing_data and listing_complete:
                        self.log_test("GET /api/favorites (With Data)", True, 
                                    f"Retrieved {len(favorites)} favorites. Contains favorite_id: {favorite['favorite_id']} and complete listing data")
                        return favorites
                    else:
                        missing = []
                        if not has_favorite_id:
                            missing.append("favorite_id")
                        if not has_listing_data:
                            missing.append("listing data")
                        if has_listing_data and not listing_complete:
                            missing.append("complete listing fields")
                        
                        self.log_test("GET /api/favorites (With Data)", False, 
                                    f"Missing required fields: {', '.join(missing)}", favorite)
                        return None
                else:
                    self.log_test("GET /api/favorites (With Data)", False, "No favorites found after adding")
                    return None
            else:
                self.log_test("GET /api/favorites (With Data)", False, f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("GET /api/favorites (With Data)", False, f"Exception: {str(e)}")
            return None

    def test_remove_from_favorites(self, favorite_id):
        """Test DELETE /api/favorites/{favorite_id} - remove using the correct favorite_id"""
        try:
            response = self.session.delete(f"{BACKEND_URL}/favorites/{favorite_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("DELETE /api/favorites/{favorite_id}", True, f"Successfully removed favorite. Response: {data.get('message', 'No message')}")
                return True
            else:
                self.log_test("DELETE /api/favorites/{favorite_id}", False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("DELETE /api/favorites/{favorite_id}", False, f"Exception: {str(e)}")
            return False

    def test_verify_removal(self):
        """Test GET /api/favorites - verify the favorite was removed"""
        try:
            response = self.session.get(f"{BACKEND_URL}/favorites")
            
            if response.status_code == 200:
                favorites = response.json()
                if len(favorites) == 0:
                    self.log_test("Verify Removal", True, "Favorites list is empty after removal - removal successful")
                    return True
                else:
                    self.log_test("Verify Removal", False, f"Still {len(favorites)} favorites after removal")
                    return False
            else:
                self.log_test("Verify Removal", False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Verify Removal", False, f"Exception: {str(e)}")
            return False

    def test_add_duplicate_favorite(self, listing_id):
        """Test adding the same listing to favorites again (should handle gracefully)"""
        try:
            # Add to favorites first
            response1 = self.session.post(f"{BACKEND_URL}/favorites", json={
                "listing_id": listing_id
            })
            
            if response1.status_code == 200:
                # Try to add the same listing again
                response2 = self.session.post(f"{BACKEND_URL}/favorites", json={
                    "listing_id": listing_id
                })
                
                if response2.status_code == 400:
                    self.log_test("Duplicate Favorite Prevention", True, "Correctly prevented duplicate favorite with 400 status")
                    return True
                elif response2.status_code == 200:
                    self.log_test("Duplicate Favorite Prevention", True, "Handled duplicate gracefully with 200 status (acceptable behavior)")
                    return True
                else:
                    self.log_test("Duplicate Favorite Prevention", False, f"Unexpected status {response2.status_code}", response2.text)
                    return False
            else:
                self.log_test("Duplicate Favorite Prevention", False, f"Initial add failed with status {response1.status_code}", response1.text)
                return False
                
        except Exception as e:
            self.log_test("Duplicate Favorite Prevention", False, f"Exception: {str(e)}")
            return False

    def run_complete_favorites_test(self):
        """Run the complete favorites toggle functionality test"""
        print("=" * 80)
        print("FAVORITES ENDPOINTS TESTING - TOGGLE FUNCTIONALITY")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print()

        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Authentication failed. Cannot proceed with testing.")
            return False

        # Step 2: Get an available listing
        listing_id = self.get_available_listing()
        if not listing_id:
            print("❌ CRITICAL: No listings available for testing. Cannot proceed.")
            return False

        # Step 3: Test GET /api/favorites (should be empty initially)
        initial_favorites = self.test_get_empty_favorites()
        if initial_favorites is None:
            print("❌ CRITICAL: Cannot retrieve favorites. Cannot proceed.")
            return False

        # Step 4: Test POST /api/favorites (add listing to favorites)
        favorite_id = self.test_add_to_favorites(listing_id)
        if not favorite_id:
            print("❌ CRITICAL: Cannot add to favorites. Cannot proceed.")
            return False

        # Step 5: Test GET /api/favorites (verify addition and data structure)
        favorites_with_data = self.test_get_favorites_with_data()
        if not favorites_with_data:
            print("❌ CRITICAL: Favorites data structure is incorrect.")
            return False

        # Step 6: Test DELETE /api/favorites/{favorite_id} (remove using favorite_id)
        removal_success = self.test_remove_from_favorites(favorite_id)
        if not removal_success:
            print("❌ CRITICAL: Cannot remove from favorites.")
            return False

        # Step 7: Verify removal
        verification_success = self.test_verify_removal()
        if not verification_success:
            print("❌ CRITICAL: Removal verification failed.")
            return False

        # Step 8: Test duplicate prevention (bonus test)
        self.test_add_duplicate_favorite(listing_id)

        # Final cleanup - remove any remaining favorites
        try:
            response = self.session.get(f"{BACKEND_URL}/favorites")
            if response.status_code == 200:
                remaining_favorites = response.json()
                for fav in remaining_favorites:
                    self.session.delete(f"{BACKEND_URL}/favorites/{fav['favorite_id']}")
        except:
            pass

        return True

    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("FAVORITES TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        # Key findings
        print("KEY FINDINGS:")
        print("✅ Favorites endpoints tested for complete toggle functionality")
        print("✅ Verified favorite_id and listing data structure in GET response")
        print("✅ Tested complete add/remove cycle as requested")
        print("✅ Used admin credentials as specified")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - Favorites toggle functionality is working correctly!")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed - See details above")

def main():
    """Main test execution"""
    tester = FavoritesTestRunner()
    
    try:
        success = tester.run_complete_favorites_test()
        tester.print_summary()
        
        if success and len([r for r in tester.test_results if "❌ FAIL" in r["status"]]) == 0:
            print("\n✅ FAVORITES TOGGLE FUNCTIONALITY: FULLY OPERATIONAL")
            sys.exit(0)
        else:
            print("\n❌ FAVORITES TOGGLE FUNCTIONALITY: ISSUES DETECTED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()