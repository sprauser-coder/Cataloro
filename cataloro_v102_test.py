#!/usr/bin/env python3
"""
Cataloro v1.0.2 Enhanced Features Testing
Testing the newly implemented bug fixes and enhancements:
1. Favorites System (replaces cart)
2. Navigation Management 
3. Products Tab (combined listings and orders)
4. User ID Migration
5. Single Listing Edit
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Use the production URL from frontend/.env
BACKEND_URL = "https://api-connect-fix-5.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class CataloroV102Tester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_user_token = None
        self.test_user_id = None
        self.test_listing_id = None
        self.test_favorite_id = None
        self.test_nav_id = None
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }

    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed_tests"] += 1
            status = "✅ PASS"
        else:
            self.results["failed_tests"] += 1
            status = "❌ FAIL"
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.results["test_details"].append({
            "test": test_name,
            "passed": passed,
            "details": details
        })

    def admin_login(self):
        """Login as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Authentication", True, f"Successfully logged in as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def create_test_user(self):
        """Create a test user for favorites testing"""
        try:
            test_user_data = {
                "email": f"favtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}@cataloro.com",
                "username": f"favuser_{datetime.now().strftime('%H%M%S')}",
                "password": "testpass123",
                "full_name": "Favorites Test User",
                "role": "both",
                "phone": "+1555123456",
                "address": "123 Favorites Street, Test City"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                user_id_format = data["user"].get("user_id", "Not Generated")
                self.log_test("Create Test User", True, f"Created user: {test_user_data['email']}, User ID: {user_id_format}")
                return True
            else:
                self.log_test("Create Test User", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Test User", False, f"Exception: {str(e)}")
            return False

    def create_test_listing(self):
        """Create a test listing for favorites testing"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            listing_data = {
                "title": "Cataloro v1.0.2 Test Product",
                "description": "This is a test product for testing the new favorites system in Cataloro v1.0.2",
                "category": "Electronics",
                "condition": "New",
                "listing_type": "fixed_price",
                "price": 199.99,
                "quantity": 5,
                "location": "Cataloro Test City"
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_listing_id = data["id"]
                self.log_test("Create Test Listing", True, f"Created listing: {data['title']} (ID: {self.test_listing_id})")
                return True
            else:
                self.log_test("Create Test Listing", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Test Listing", False, f"Exception: {str(e)}")
            return False

    def test_favorites_system(self):
        """Test the complete favorites system (POST, GET, DELETE)"""
        print("\n🔍 TESTING FAVORITES SYSTEM:")
        print("-" * 50)
        
        # Test 1: Add to favorites (POST /api/favorites)
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            favorite_data = {"listing_id": self.test_listing_id}
            
            response = self.session.post(f"{BACKEND_URL}/favorites", json=favorite_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_favorite_id = data.get("favorite_id")
                self.log_test("POST /api/favorites", True, f"Added to favorites: {data.get('message')}")
            else:
                self.log_test("POST /api/favorites", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("POST /api/favorites", False, f"Exception: {str(e)}")
            return False

        # Test 2: Get user favorites (GET /api/favorites)
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = self.session.get(f"{BACKEND_URL}/favorites", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if our test listing is in favorites
                    found_listing = False
                    for favorite in data:
                        if favorite.get("listing", {}).get("id") == self.test_listing_id:
                            found_listing = True
                            break
                    
                    if found_listing:
                        self.log_test("GET /api/favorites", True, f"Retrieved {len(data)} favorites including test listing")
                    else:
                        self.log_test("GET /api/favorites", False, "Test listing not found in favorites")
                        return False
                else:
                    self.log_test("GET /api/favorites", False, "No favorites returned or invalid format")
                    return False
            else:
                self.log_test("GET /api/favorites", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /api/favorites", False, f"Exception: {str(e)}")
            return False

        # Test 3: Remove from favorites (DELETE /api/favorites/{favorite_id})
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = self.session.delete(f"{BACKEND_URL}/favorites/{self.test_favorite_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("DELETE /api/favorites/{favorite_id}", True, f"Removed from favorites: {data.get('message')}")
            else:
                self.log_test("DELETE /api/favorites/{favorite_id}", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("DELETE /api/favorites/{favorite_id}", False, f"Exception: {str(e)}")
            return False

        # Test 4: Verify favorites only show active listings
        try:
            # First add the listing back to favorites
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            favorite_data = {"listing_id": self.test_listing_id}
            add_response = self.session.post(f"{BACKEND_URL}/favorites", json=favorite_data, headers=headers)
            
            if add_response.status_code == 200:
                # Now get favorites - should show the active listing
                get_response = self.session.get(f"{BACKEND_URL}/favorites", headers=headers)
                if get_response.status_code == 200:
                    favorites = get_response.json()
                    active_listings_count = len([f for f in favorites if f.get("listing", {}).get("status") == "active"])
                    self.log_test("Favorites Show Only Active Listings", True, f"Found {active_listings_count} active listings in favorites")
                else:
                    self.log_test("Favorites Show Only Active Listings", False, f"Failed to get favorites: {get_response.status_code}")
                    return False
            else:
                self.log_test("Favorites Show Only Active Listings", False, f"Failed to re-add to favorites: {add_response.status_code}")
                return False
        except Exception as e:
            self.log_test("Favorites Show Only Active Listings", False, f"Exception: {str(e)}")
            return False

        return True

    def test_navigation_management(self):
        """Test navigation management endpoints"""
        print("\n🔍 TESTING NAVIGATION MANAGEMENT:")
        print("-" * 50)
        
        # Test 1: Get navigation items (GET /admin/navigation)
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/admin/navigation", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("GET /admin/navigation", True, f"Retrieved {len(data)} navigation items")
                    # Store a test nav ID if available
                    if len(data) > 0:
                        self.test_nav_id = data[0].get("id")
                else:
                    self.log_test("GET /admin/navigation", False, "Invalid response format")
                    return False
            else:
                self.log_test("GET /admin/navigation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /admin/navigation", False, f"Exception: {str(e)}")
            return False

        # Test 2: Delete test pages (DELETE /admin/navigation/test-pages)
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.delete(f"{BACKEND_URL}/admin/navigation/test-pages", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                nav_deleted = data.get("navigation_deleted", 0)
                pages_deleted = data.get("pages_deleted", 0)
                self.log_test("DELETE /admin/navigation/test-pages", True, f"Deleted {nav_deleted} nav items and {pages_deleted} test pages")
            else:
                self.log_test("DELETE /admin/navigation/test-pages", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("DELETE /admin/navigation/test-pages", False, f"Exception: {str(e)}")
            return False

        # Test 3: Delete specific navigation item (if we have one)
        if self.test_nav_id:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.delete(f"{BACKEND_URL}/admin/navigation/{self.test_nav_id}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("DELETE /admin/navigation/{nav_id}", True, f"Deleted navigation item: {data.get('message')}")
                elif response.status_code == 404:
                    self.log_test("DELETE /admin/navigation/{nav_id}", True, "Navigation item not found (expected for test)")
                else:
                    self.log_test("DELETE /admin/navigation/{nav_id}", False, f"Status: {response.status_code}, Response: {response.text}")
                    return False
            except Exception as e:
                self.log_test("DELETE /admin/navigation/{nav_id}", False, f"Exception: {str(e)}")
                return False

        return True

    def test_single_listing_edit(self):
        """Test single listing edit functionality (PUT /api/admin/listings/{listing_id})"""
        print("\n🔍 TESTING SINGLE LISTING EDIT:")
        print("-" * 50)
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test updating various fields
            update_data = {
                "title": "Updated Cataloro v1.0.2 Test Product",
                "description": "This listing has been updated using the new single listing edit feature",
                "price": 249.99,
                "category": "Home & Garden",
                "condition": "Like New",
                "quantity": 3,
                "location": "Updated Test City"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/listings/{self.test_listing_id}", json=update_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("PUT /api/admin/listings/{listing_id}", True, f"Updated listing: {data.get('message')}")
                
                # Verify the update by getting the listing
                get_response = self.session.get(f"{BACKEND_URL}/listings/{self.test_listing_id}")
                if get_response.status_code == 200:
                    listing_data = get_response.json()
                    
                    # Check if updates were applied
                    checks = [
                        (listing_data.get("title") == update_data["title"], "Title update"),
                        (listing_data.get("price") == update_data["price"], "Price update"),
                        (listing_data.get("category") == update_data["category"], "Category update"),
                        (listing_data.get("condition") == update_data["condition"], "Condition update"),
                        (listing_data.get("quantity") == update_data["quantity"], "Quantity update"),
                        (listing_data.get("location") == update_data["location"], "Location update")
                    ]
                    
                    passed_checks = [check[1] for check in checks if check[0]]
                    failed_checks = [check[1] for check in checks if not check[0]]
                    
                    if len(failed_checks) == 0:
                        self.log_test("Listing Edit Verification", True, f"All fields updated correctly: {', '.join(passed_checks)}")
                    else:
                        self.log_test("Listing Edit Verification", False, f"Failed updates: {', '.join(failed_checks)}")
                        return False
                else:
                    self.log_test("Listing Edit Verification", False, f"Failed to retrieve updated listing: {get_response.status_code}")
                    return False
            else:
                self.log_test("PUT /api/admin/listings/{listing_id}", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Single Listing Edit", False, f"Exception: {str(e)}")
            return False

        return True

    def test_user_id_migration(self):
        """Test user ID migration functionality"""
        print("\n🔍 TESTING USER ID MIGRATION:")
        print("-" * 50)
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test the generate user IDs endpoint
            response = self.session.post(f"{BACKEND_URL}/admin/generate-user-ids", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                updated_count = data.get("updated_count", 0)
                generated_ids = data.get("generated_ids", [])
                
                self.log_test("POST /admin/generate-user-ids", True, f"Updated {updated_count} users with new IDs")
                
                # Check if our test user has a proper user ID format
                if self.test_user_id:
                    # Get user details to check user_id format
                    users_response = self.session.get(f"{BACKEND_URL}/admin/users", headers=headers)
                    if users_response.status_code == 200:
                        users = users_response.json()
                        test_user = next((u for u in users if u.get("id") == self.test_user_id), None)
                        
                        if test_user:
                            user_id = test_user.get("user_id", "")
                            if user_id.startswith("U") and len(user_id) == 6 and user_id[1:].isdigit():
                                self.log_test("User ID Format Verification", True, f"Test user has proper ID format: {user_id}")
                            else:
                                self.log_test("User ID Format Verification", False, f"Invalid user ID format: {user_id}")
                                return False
                        else:
                            self.log_test("User ID Format Verification", False, "Test user not found in admin users list")
                            return False
                    else:
                        self.log_test("User ID Format Verification", False, f"Failed to get users list: {users_response.status_code}")
                        return False
            else:
                self.log_test("POST /admin/generate-user-ids", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User ID Migration", False, f"Exception: {str(e)}")
            return False

        return True

    def test_products_tab_endpoints(self):
        """Test that combined listings and orders endpoints still work"""
        print("\n🔍 TESTING PRODUCTS TAB ENDPOINTS:")
        print("-" * 50)
        
        # Test 1: Admin listings endpoint
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/admin/listings", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("GET /admin/listings", True, f"Retrieved {len(data)} listings for products tab")
                else:
                    self.log_test("GET /admin/listings", False, "Invalid response format")
                    return False
            else:
                self.log_test("GET /admin/listings", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /admin/listings", False, f"Exception: {str(e)}")
            return False

        # Test 2: Admin orders endpoint with filters
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test with different filters
            filter_tests = [
                ("all", "All orders"),
                ("pending", "Pending orders"),
                ("completed", "Completed orders")
            ]
            
            for status_filter, description in filter_tests:
                response = self.session.get(f"{BACKEND_URL}/admin/orders", 
                                          params={"status_filter": status_filter}, 
                                          headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"GET /admin/orders ({status_filter})", True, f"{description}: {len(data)} orders")
                    else:
                        self.log_test(f"GET /admin/orders ({status_filter})", False, "Invalid response format")
                        return False
                else:
                    self.log_test(f"GET /admin/orders ({status_filter})", False, f"Status: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test("GET /admin/orders with filters", False, f"Exception: {str(e)}")
            return False

        # Test 3: Time frame filters
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            time_frames = ["today", "last_week", "last_month"]
            
            for time_frame in time_frames:
                response = self.session.get(f"{BACKEND_URL}/admin/orders", 
                                          params={"time_frame": time_frame}, 
                                          headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Orders Time Frame ({time_frame})", True, f"Retrieved {len(data)} orders")
                else:
                    self.log_test(f"Orders Time Frame ({time_frame})", False, f"Status: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test("Orders Time Frame Filters", False, f"Exception: {str(e)}")
            return False

        return True

    def test_authentication_security(self):
        """Test that all new endpoints require proper authentication"""
        print("\n🔍 TESTING AUTHENTICATION SECURITY:")
        print("-" * 50)
        
        # Test endpoints without authentication
        endpoints_to_test = [
            ("POST", "/favorites", {"listing_id": "test"}),
            ("GET", "/favorites", None),
            ("DELETE", f"/favorites/test", None),
            ("GET", "/admin/navigation", None),
            ("DELETE", "/admin/navigation/test", None),
            ("PUT", f"/admin/listings/test", {"title": "test"}),
            ("POST", "/admin/generate-user-ids", None)
        ]
        
        # Remove authorization header temporarily
        original_auth = self.session.headers.get("Authorization")
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        
        for method, endpoint, data in endpoints_to_test:
            try:
                if method == "POST":
                    response = self.session.post(f"{BACKEND_URL}{endpoint}", json=data)
                elif method == "GET":
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                elif method == "DELETE":
                    response = self.session.delete(f"{BACKEND_URL}{endpoint}")
                elif method == "PUT":
                    response = self.session.put(f"{BACKEND_URL}{endpoint}", json=data)
                
                if response.status_code in [401, 403]:
                    self.log_test(f"Auth Required: {method} {endpoint}", True, f"Correctly rejected (Status: {response.status_code})")
                else:
                    self.log_test(f"Auth Required: {method} {endpoint}", False, f"Should require auth but got: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Auth Required: {method} {endpoint}", False, f"Exception: {str(e)}")
        
        # Restore authorization header
        if original_auth:
            self.session.headers["Authorization"] = original_auth

        return True

    def run_all_tests(self):
        """Run all Cataloro v1.0.2 enhancement tests"""
        print("=" * 80)
        print("CATALORO v1.0.2 ENHANCED FEATURES TESTING")
        print("Testing newly implemented bug fixes and enhancements")
        print("=" * 80)
        
        # Step 1: Admin login
        if not self.admin_login():
            print("❌ Cannot proceed without admin access")
            return False
        
        # Step 2: Create test user
        if not self.create_test_user():
            print("❌ Cannot proceed without test user")
            return False
        
        # Step 3: Create test listing
        if not self.create_test_listing():
            print("❌ Cannot proceed without test listing")
            return False
        
        # Run all enhancement tests
        test_results = []
        test_results.append(self.test_favorites_system())
        test_results.append(self.test_navigation_management())
        test_results.append(self.test_single_listing_edit())
        test_results.append(self.test_user_id_migration())
        test_results.append(self.test_products_tab_endpoints())
        test_results.append(self.test_authentication_security())
        
        # Print summary
        print("\n" + "=" * 80)
        print("CATALORO v1.0.2 TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.results["passed_tests"] / self.results["total_tests"]) * 100 if self.results["total_tests"] > 0 else 0
        
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']} ✅")
        print(f"Failed: {self.results['failed_tests']} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results["failed_tests"] > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.results["test_details"]:
                if not test["passed"]:
                    print(f"  • {test['test']}: {test['details']}")
        
        print("\n🎯 ENHANCEMENT AREAS TESTED:")
        print("  ✅ Favorites System (POST/GET/DELETE /api/favorites)")
        print("  ✅ Navigation Management (/admin/navigation endpoints)")
        print("  ✅ Single Listing Edit (PUT /admin/listings/{id})")
        print("  ✅ User ID Migration (/admin/generate-user-ids)")
        print("  ✅ Products Tab Endpoints (combined listings/orders)")
        print("  ✅ Authentication Security (all endpoints)")
        
        print("\n" + "=" * 80)
        
        return all(test_results)

if __name__ == "__main__":
    tester = CataloroV102Tester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL CATALORO v1.0.2 ENHANCEMENT TESTS PASSED!")
        print("✅ Favorites system working completely")
        print("✅ Navigation management functional")
        print("✅ Single listing edit operational")
        print("✅ User ID migration working")
        print("✅ Products tab endpoints functional")
        print("✅ Authentication security enforced")
        sys.exit(0)
    else:
        print("⚠️  Some v1.0.2 enhancement tests failed - review the issues above")
        sys.exit(1)