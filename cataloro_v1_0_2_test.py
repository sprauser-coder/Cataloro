#!/usr/bin/env python3
"""
Cataloro Marketplace Backend v1.0.2 Testing
Testing the enhanced features as requested in the review:

1. Listing Edit Endpoint: PUT /api/admin/listings/{listing_id}
2. Enhanced Order Management: GET /api/admin/orders with filters
3. User ID Generation: U00001 format testing
4. Listings Pagination: GET /api/listings with limit parameter
5. Profile Management: All profile endpoints verification
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import time

# Configuration - Using the production URL from frontend/.env
BACKEND_URL = "https://cataloro-market.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class CataloroV102Tester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_user_token = None
        self.test_user_id = None
        self.test_listing_id = None
        self.test_order_id = None
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

    def test_user_id_generation(self):
        """Test the new U00001 format user ID generation"""
        try:
            # Create a new user to test ID generation
            test_user_data = {
                "email": f"userid_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "username": f"userid_test_{datetime.now().strftime('%H%M%S')}",
                "password": "testpass123",
                "full_name": "User ID Test User",
                "role": "both",  # Changed to "both" so user can create listings
                "phone": "+1234567890",
                "address": "123 Test Street"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                user_id = data["user"]["user_id"]
                
                # Check if user_id follows U00001 format
                if user_id and user_id.startswith('U') and len(user_id) == 6 and user_id[1:].isdigit():
                    self.log_test("User ID Generation Format", True, f"Generated user_id: {user_id} (follows U00001 format)")
                    
                    # Store for later use
                    self.test_user_token = data["access_token"]
                    self.test_user_id = data["user"]["id"]
                    return True
                else:
                    self.log_test("User ID Generation Format", False, f"Invalid format: {user_id} (expected U00001 format)")
                    return False
            else:
                self.log_test("User ID Generation", False, f"Registration failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User ID Generation", False, f"Exception: {str(e)}")
            return False

    def test_listings_pagination(self):
        """Test GET /api/listings with limit parameter (10, 50, 100)"""
        try:
            # Test different limit values
            limit_tests = [10, 50, 100]
            all_passed = True
            
            for limit in limit_tests:
                response = self.session.get(f"{BACKEND_URL}/listings?limit={limit}")
                
                if response.status_code == 200:
                    data = response.json()
                    actual_count = len(data)
                    
                    # Check if we got the expected number or less (if there aren't enough listings)
                    if actual_count <= limit:
                        self.log_test(f"Listings Pagination - Limit {limit}", True, f"Returned {actual_count} listings (≤ {limit})")
                    else:
                        self.log_test(f"Listings Pagination - Limit {limit}", False, f"Returned {actual_count} listings (> {limit})")
                        all_passed = False
                else:
                    self.log_test(f"Listings Pagination - Limit {limit}", False, f"Status: {response.status_code}")
                    all_passed = False
            
            # Test default behavior (no limit)
            response = self.session.get(f"{BACKEND_URL}/listings")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Listings Pagination - Default", True, f"Default returned {len(data)} listings")
            else:
                self.log_test("Listings Pagination - Default", False, f"Status: {response.status_code}")
                all_passed = False
            
            return all_passed
        except Exception as e:
            self.log_test("Listings Pagination", False, f"Exception: {str(e)}")
            return False

    def create_test_listing(self):
        """Create a test listing for editing tests"""
        try:
            # Switch to test user token for creating listing
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            listing_data = {
                "title": "V1.0.2 Test Listing for Edit",
                "description": "This listing will be used to test the admin edit functionality",
                "category": "Electronics",
                "condition": "New",
                "listing_type": "fixed_price",
                "price": 199.99,
                "quantity": 5,
                "location": "Test City, Test State"
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

    def test_listing_edit_endpoint(self):
        """Test PUT /api/admin/listings/{listing_id} with admin credentials"""
        try:
            if not self.test_listing_id:
                self.log_test("Listing Edit Endpoint", False, "No test listing available")
                return False
            
            # Switch back to admin token
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test editing the listing
            edit_data = {
                "title": "EDITED - V1.0.2 Test Listing",
                "description": "This listing has been edited by admin using the new edit endpoint",
                "price": 299.99,
                "category": "Fashion",
                "condition": "Like New",
                "quantity": 3,
                "location": "Updated Location, New State"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/listings/{self.test_listing_id}", 
                                      json=edit_data, headers=admin_headers)
            
            if response.status_code == 200:
                # Verify the changes by getting the listing
                get_response = self.session.get(f"{BACKEND_URL}/listings/{self.test_listing_id}")
                
                if get_response.status_code == 200:
                    updated_listing = get_response.json()
                    
                    # Check if changes were applied
                    checks = [
                        (updated_listing.get("title") == edit_data["title"], "Title update"),
                        (updated_listing.get("description") == edit_data["description"], "Description update"),
                        (updated_listing.get("price") == edit_data["price"], "Price update"),
                        (updated_listing.get("category") == edit_data["category"], "Category update"),
                        (updated_listing.get("condition") == edit_data["condition"], "Condition update"),
                        (updated_listing.get("quantity") == edit_data["quantity"], "Quantity update"),
                        (updated_listing.get("location") == edit_data["location"], "Location update")
                    ]
                    
                    passed_checks = [check for check, desc in checks if check]
                    failed_checks = [desc for check, desc in checks if not check]
                    
                    if len(failed_checks) == 0:
                        self.log_test("Listing Edit Endpoint", True, f"All {len(checks)} fields updated successfully")
                        return True
                    else:
                        self.log_test("Listing Edit Endpoint", False, f"Failed updates: {', '.join(failed_checks)}")
                        return False
                else:
                    self.log_test("Listing Edit Endpoint", False, f"Could not verify changes: {get_response.status_code}")
                    return False
            else:
                self.log_test("Listing Edit Endpoint", False, f"Edit failed: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Listing Edit Endpoint", False, f"Exception: {str(e)}")
            return False

    def create_test_orders(self):
        """Create test orders for order management testing"""
        try:
            # Create orders with different statuses and times
            orders_created = 0
            
            # Create a pending order
            order_data = {
                "listing_id": self.test_listing_id,
                "quantity": 1,
                "shipping_address": "123 Test Address, Test City, Test State"
            }
            
            # Use test user token to create order
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = self.session.post(f"{BACKEND_URL}/orders", json=order_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_order_id = data["id"]
                orders_created += 1
                self.log_test("Create Test Orders", True, f"Created {orders_created} test order(s)")
                return True
            else:
                self.log_test("Create Test Orders", False, f"Order creation failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create Test Orders", False, f"Exception: {str(e)}")
            return False

    def test_enhanced_order_management(self):
        """Test GET /api/admin/orders with status_filter and time_frame parameters"""
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            all_passed = True
            
            # Test 1: Get all orders (no filters)
            response = self.session.get(f"{BACKEND_URL}/admin/orders", headers=admin_headers)
            if response.status_code == 200:
                all_orders = response.json()
                self.log_test("Enhanced Order Management - All Orders", True, f"Retrieved {len(all_orders)} total orders")
            else:
                self.log_test("Enhanced Order Management - All Orders", False, f"Status: {response.status_code}")
                all_passed = False
            
            # Test 2: Filter by status - pending
            response = self.session.get(f"{BACKEND_URL}/admin/orders?status_filter=pending", headers=admin_headers)
            if response.status_code == 200:
                pending_orders = response.json()
                self.log_test("Enhanced Order Management - Pending Filter", True, f"Retrieved {len(pending_orders)} pending orders")
            else:
                self.log_test("Enhanced Order Management - Pending Filter", False, f"Status: {response.status_code}")
                all_passed = False
            
            # Test 3: Filter by status - completed
            response = self.session.get(f"{BACKEND_URL}/admin/orders?status_filter=completed", headers=admin_headers)
            if response.status_code == 200:
                completed_orders = response.json()
                self.log_test("Enhanced Order Management - Completed Filter", True, f"Retrieved {len(completed_orders)} completed orders")
            else:
                self.log_test("Enhanced Order Management - Completed Filter", False, f"Status: {response.status_code}")
                all_passed = False
            
            # Test 4: Time frame filters
            time_frames = ["today", "yesterday", "last_week", "last_month", "last_year"]
            for time_frame in time_frames:
                response = self.session.get(f"{BACKEND_URL}/admin/orders?time_frame={time_frame}", headers=admin_headers)
                if response.status_code == 200:
                    filtered_orders = response.json()
                    self.log_test(f"Enhanced Order Management - {time_frame.title()} Filter", True, f"Retrieved {len(filtered_orders)} orders")
                else:
                    self.log_test(f"Enhanced Order Management - {time_frame.title()} Filter", False, f"Status: {response.status_code}")
                    all_passed = False
            
            # Test 5: Combined filters
            response = self.session.get(f"{BACKEND_URL}/admin/orders?status_filter=pending&time_frame=last_week", headers=admin_headers)
            if response.status_code == 200:
                combined_orders = response.json()
                self.log_test("Enhanced Order Management - Combined Filters", True, f"Retrieved {len(combined_orders)} orders with combined filters")
            else:
                self.log_test("Enhanced Order Management - Combined Filters", False, f"Status: {response.status_code}")
                all_passed = False
            
            return all_passed
        except Exception as e:
            self.log_test("Enhanced Order Management", False, f"Exception: {str(e)}")
            return False

    def test_profile_management_endpoints(self):
        """Verify all profile endpoints are working correctly"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            all_passed = True
            
            # Test 1: GET /profile
            response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            if response.status_code == 200:
                profile_data = response.json()
                required_fields = ["id", "email", "username", "full_name", "role"]
                missing_fields = [field for field in required_fields if field not in profile_data]
                
                # Check if user_id exists (it should be generated)
                if "user_id" in profile_data and profile_data["user_id"]:
                    self.log_test("Profile Management - User ID Present", True, f"User ID: {profile_data['user_id']}")
                else:
                    self.log_test("Profile Management - User ID Present", False, "user_id field missing or empty")
                    all_passed = False
                
                if not missing_fields:
                    self.log_test("Profile Management - GET Profile", True, f"Retrieved profile with all required fields")
                else:
                    self.log_test("Profile Management - GET Profile", False, f"Missing fields: {missing_fields}")
                    all_passed = False
            else:
                self.log_test("Profile Management - GET Profile", False, f"Status: {response.status_code}")
                all_passed = False
            
            # Test 2: PUT /profile (update profile)
            update_data = {
                "full_name": "Updated V1.0.2 Test User",
                "phone": "+1987654321",
                "bio": "Updated bio for v1.0.2 testing",
                "location": "Updated Location, CA"
            }
            
            response = self.session.put(f"{BACKEND_URL}/profile", json=update_data, headers=headers)
            if response.status_code == 200:
                updated_profile = response.json()
                
                # Verify updates
                checks = [
                    (updated_profile.get("full_name") == update_data["full_name"], "Full name"),
                    (updated_profile.get("phone") == update_data["phone"], "Phone"),
                    (updated_profile.get("bio") == update_data["bio"], "Bio"),
                    (updated_profile.get("location") == update_data["location"], "Location")
                ]
                
                failed_updates = [desc for check, desc in checks if not check]
                if not failed_updates:
                    self.log_test("Profile Management - PUT Profile", True, "All profile fields updated successfully")
                else:
                    self.log_test("Profile Management - PUT Profile", False, f"Failed updates: {', '.join(failed_updates)}")
                    all_passed = False
            else:
                self.log_test("Profile Management - PUT Profile", False, f"Status: {response.status_code}")
                all_passed = False
            
            # Test 3: GET /profile/stats
            response = self.session.get(f"{BACKEND_URL}/profile/stats", headers=headers)
            if response.status_code == 200:
                stats_data = response.json()
                required_stats = ["total_orders", "total_listings", "total_spent", "total_earned", "avg_rating", "total_reviews"]
                missing_stats = [stat for stat in required_stats if stat not in stats_data]
                
                if not missing_stats:
                    self.log_test("Profile Management - GET Stats", True, f"Retrieved all profile statistics")
                else:
                    self.log_test("Profile Management - GET Stats", False, f"Missing stats: {missing_stats}")
                    all_passed = False
            else:
                self.log_test("Profile Management - GET Stats", False, f"Status: {response.status_code}")
                all_passed = False
            
            # Test 4: GET /listings/my-listings
            response = self.session.get(f"{BACKEND_URL}/listings/my-listings", headers=headers)
            if response.status_code == 200:
                my_listings = response.json()
                self.log_test("Profile Management - GET My Listings", True, f"Retrieved {len(my_listings)} user listings")
            else:
                self.log_test("Profile Management - GET My Listings", False, f"Status: {response.status_code}")
                all_passed = False
            
            return all_passed
        except Exception as e:
            self.log_test("Profile Management Endpoints", False, f"Exception: {str(e)}")
            return False

    def test_admin_authentication_security(self):
        """Test that admin endpoints require proper admin credentials"""
        try:
            # Test admin endpoints without admin token (should fail)
            regular_headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Test listing edit with non-admin token
            response = self.session.put(f"{BACKEND_URL}/admin/listings/{self.test_listing_id}", 
                                      json={"title": "Should Fail"}, headers=regular_headers)
            
            if response.status_code == 403:
                self.log_test("Admin Security - Listing Edit", True, "Correctly blocked non-admin user from editing listings")
            else:
                self.log_test("Admin Security - Listing Edit", False, f"Expected 403, got {response.status_code}")
                return False
            
            # Test order management with non-admin token
            response = self.session.get(f"{BACKEND_URL}/admin/orders", headers=regular_headers)
            
            if response.status_code == 403:
                self.log_test("Admin Security - Order Management", True, "Correctly blocked non-admin user from accessing admin orders")
            else:
                self.log_test("Admin Security - Order Management", False, f"Expected 403, got {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.log_test("Admin Authentication Security", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all v1.0.2 tests"""
        print("=" * 80)
        print("CATALORO MARKETPLACE BACKEND v1.0.2 TESTING")
        print("Testing enhanced features as requested in review")
        print("=" * 80)
        
        # Step 1: Admin login
        if not self.admin_login():
            print("❌ Cannot proceed without admin access")
            return False
        
        print("\n🔍 TESTING USER ID GENERATION (U00001 FORMAT):")
        print("-" * 50)
        if not self.test_user_id_generation():
            print("❌ Cannot proceed without test user")
            return False
        
        print("\n🔍 TESTING LISTINGS PAGINATION (10, 50, 100 LIMITS):")
        print("-" * 50)
        self.test_listings_pagination()
        
        print("\n🔍 TESTING LISTING EDIT ENDPOINT:")
        print("-" * 50)
        self.create_test_listing()
        self.test_listing_edit_endpoint()
        
        print("\n🔍 TESTING ENHANCED ORDER MANAGEMENT:")
        print("-" * 50)
        self.create_test_orders()
        self.test_enhanced_order_management()
        
        print("\n🔍 TESTING PROFILE MANAGEMENT ENDPOINTS:")
        print("-" * 50)
        self.test_profile_management_endpoints()
        
        print("\n🔍 TESTING ADMIN AUTHENTICATION SECURITY:")
        print("-" * 50)
        self.test_admin_authentication_security()
        
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
        
        print("\n" + "=" * 80)
        
        return self.results["failed_tests"] == 0

if __name__ == "__main__":
    tester = CataloroV102Tester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL v1.0.2 TESTS PASSED - Enhanced features are working correctly!")
        sys.exit(0)
    else:
        print("⚠️  Some v1.0.2 tests failed - review the issues above")
        sys.exit(1)