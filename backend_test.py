#!/usr/bin/env python3
"""
Backend API Connectivity Test for 217.154.0.82 Server
Testing critical endpoints to diagnose frontend authentication issues and white screen problem.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Updated for 217.154.0.82 server
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class AdminAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_admin_login(self):
        """Test 1: Admin Login Test - POST /api/auth/login with admin credentials"""
        print("🔐 Testing Admin Login...")
        
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "access_token" in data and "user" in data:
                    self.admin_token = data["access_token"]
                    self.admin_user = data["user"]
                    
                    # Verify token type
                    if data.get("token_type") == "bearer":
                        self.log_test(
                            "Admin Login", 
                            True, 
                            f"Successfully logged in as {self.admin_user.get('email')}. Token received."
                        )
                        return True
                    else:
                        self.log_test("Admin Login", False, "Invalid token type returned")
                        return False
                else:
                    self.log_test("Admin Login", False, "Missing access_token or user in response")
                    return False
            else:
                self.log_test(
                    "Admin Login", 
                    False, 
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_admin_role_verification(self):
        """Test 2: Admin Role Verification - Verify returned user object contains role='admin'"""
        print("👤 Testing Admin Role Verification...")
        
        if not self.admin_user:
            self.log_test("Admin Role Verification", False, "No admin user data available")
            return False
        
        try:
            user_role = self.admin_user.get("role")
            user_email = self.admin_user.get("email")
            user_id = self.admin_user.get("id")
            user_username = self.admin_user.get("username")
            
            if user_role == "admin":
                self.log_test(
                    "Admin Role Verification", 
                    True, 
                    f"User role correctly set to 'admin'. User details: email={user_email}, username={user_username}, id={user_id}"
                )
                return True
            else:
                self.log_test(
                    "Admin Role Verification", 
                    False, 
                    f"Expected role 'admin' but got '{user_role}'"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Role Verification", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_token_validation(self):
        """Test 3: Token Validation - Test if JWT token is valid for protected routes"""
        print("🔑 Testing Token Validation...")
        
        if not self.admin_token:
            self.log_test("Token Validation", False, "No admin token available")
            return False
        
        try:
            # Test token with a simple protected endpoint
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/listings/my-listings", headers=headers)
            
            if response.status_code == 200:
                self.log_test(
                    "Token Validation", 
                    True, 
                    "JWT token is valid and accepted by protected endpoints"
                )
                return True
            elif response.status_code == 401:
                self.log_test("Token Validation", False, "Token rejected - 401 Unauthorized")
                return False
            elif response.status_code == 403:
                self.log_test("Token Validation", False, "Token rejected - 403 Forbidden")
                return False
            else:
                self.log_test(
                    "Token Validation", 
                    False, 
                    f"Unexpected response status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Token Validation", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_admin_profile(self):
        """Test 4: Admin Profile - Test GET /api/profile with admin token"""
        print("📋 Testing Admin Profile Access...")
        
        if not self.admin_token:
            self.log_test("Admin Profile Access", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Verify role persistence in profile
                profile_role = profile_data.get("role")
                profile_email = profile_data.get("email")
                user_id = profile_data.get("user_id", "Not set")
                
                if profile_role == "admin":
                    self.log_test(
                        "Admin Profile Access", 
                        True, 
                        f"Profile endpoint working. Role persisted as 'admin'. Email: {profile_email}, User ID: {user_id}"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Profile Access", 
                        False, 
                        f"Role not persisted correctly. Expected 'admin', got '{profile_role}'"
                    )
                    return False
            else:
                self.log_test(
                    "Admin Profile Access", 
                    False, 
                    f"Profile endpoint failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Profile Access", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_admin_stats_access(self):
        """Test 5: Admin Stats Access - Test GET /api/admin/stats with admin token"""
        print("📊 Testing Admin Stats Access...")
        
        if not self.admin_token:
            self.log_test("Admin Stats Access", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                stats_data = response.json()
                
                # Verify expected stats fields
                expected_fields = [
                    "total_users", "active_users", "blocked_users",
                    "total_listings", "active_listings", 
                    "total_orders", "total_revenue"
                ]
                
                missing_fields = [field for field in expected_fields if field not in stats_data]
                
                if not missing_fields:
                    self.log_test(
                        "Admin Stats Access", 
                        True, 
                        f"Admin stats endpoint working. Stats: {json.dumps(stats_data, indent=2)}"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Stats Access", 
                        False, 
                        f"Missing expected fields in stats response: {missing_fields}"
                    )
                    return False
            elif response.status_code == 403:
                self.log_test(
                    "Admin Stats Access", 
                    False, 
                    "Access denied to admin stats - role verification may be failing"
                )
                return False
            else:
                self.log_test(
                    "Admin Stats Access", 
                    False, 
                    f"Admin stats endpoint failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Stats Access", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_additional_admin_endpoints(self):
        """Test additional admin endpoints to ensure comprehensive access"""
        print("🔧 Testing Additional Admin Endpoints...")
        
        if not self.admin_token:
            self.log_test("Additional Admin Endpoints", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        admin_endpoints = [
            ("/admin/users", "Users Management"),
            ("/admin/listings", "Listings Management"),
            ("/admin/orders", "Orders Management"),
            ("/admin/cms/settings", "CMS Settings")
        ]
        
        successful_endpoints = []
        failed_endpoints = []
        
        for endpoint, description in admin_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                if response.status_code == 200:
                    successful_endpoints.append(f"{description} ({endpoint})")
                else:
                    failed_endpoints.append(f"{description} ({endpoint}) - Status: {response.status_code}")
            except Exception as e:
                failed_endpoints.append(f"{description} ({endpoint}) - Error: {str(e)}")
        
        if len(successful_endpoints) >= 3:  # At least 3 out of 4 should work
            self.log_test(
                "Additional Admin Endpoints", 
                True, 
                f"Working endpoints: {', '.join(successful_endpoints)}"
            )
            if failed_endpoints:
                print(f"   Note: Some endpoints had issues: {', '.join(failed_endpoints)}")
            return True
        else:
            self.log_test(
                "Additional Admin Endpoints", 
                False, 
                f"Too many endpoints failed. Working: {len(successful_endpoints)}, Failed: {len(failed_endpoints)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all admin authentication tests"""
        print("=" * 80)
        print("🚀 ADMIN AUTHENTICATION & ROLE VERIFICATION TEST SUITE")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        tests = [
            self.test_admin_login,
            self.test_admin_role_verification,
            self.test_token_validation,
            self.test_admin_profile,
            self.test_admin_stats_access,
            self.test_additional_admin_endpoints
        ]
        
        for test in tests:
            test()
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        print()
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            print()
        
        if len(passed_tests) == len(self.test_results):
            print("🎉 ALL TESTS PASSED! Admin authentication is working correctly.")
            print("✅ Admin panel should be accessible without white screen issues.")
        elif len(passed_tests) >= 4:  # At least core functionality working
            print("⚠️  MOSTLY WORKING: Core admin authentication is functional.")
            print("✅ Admin panel should be accessible, but some features may have issues.")
        else:
            print("🚨 CRITICAL ISSUES FOUND: Admin authentication has significant problems.")
            print("❌ Admin panel white screen issue likely caused by authentication failures.")
        
        print("=" * 80)
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = AdminAuthTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
"""
Profile Endpoints Testing for Cataloro v1.0.4
Testing Phase 1 fixes for profile functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://shopfix-deploy-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ProfileEndpointTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Token obtained for {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_get_profile(self):
        """Test GET /api/profile endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Check required fields
                required_fields = ["id", "user_id", "username", "full_name", "email", "role", "created_at"]
                missing_fields = [field for field in required_fields if field not in profile_data]
                
                if missing_fields:
                    self.log_test("GET /profile - Required Fields", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Check user_id format (should be like U00001 or USER002)
                user_id = profile_data.get("user_id", "")
                if not user_id:
                    self.log_test("GET /profile - User ID", False, "user_id field is empty")
                    return False
                
                # Verify profile data structure
                profile_info = {
                    "user_id": user_id,
                    "username": profile_data.get("username"),
                    "full_name": profile_data.get("full_name"),
                    "email": profile_data.get("email"),
                    "role": profile_data.get("role"),
                    "phone": profile_data.get("phone"),
                    "bio": profile_data.get("bio"),
                    "location": profile_data.get("location"),
                    "is_business": profile_data.get("is_business"),
                    "company_name": profile_data.get("company_name"),
                    "country": profile_data.get("country"),
                    "vat_number": profile_data.get("vat_number")
                }
                
                self.log_test("GET /profile - Data Retrieval", True, f"Profile retrieved successfully with user_id: {user_id}")
                return profile_data
            else:
                self.log_test("GET /profile - Data Retrieval", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("GET /profile - Data Retrieval", False, f"Exception: {str(e)}")
            return None
    
    def test_update_profile(self):
        """Test PUT /api/profile endpoint"""
        try:
            # Test updating regular profile fields
            update_data = {
                "phone": "+1-555-0123",
                "bio": "Updated bio for profile testing",
                "location": "Test City, Test State"
            }
            
            response = self.session.put(f"{BASE_URL}/profile", json=update_data)
            
            if response.status_code == 200:
                updated_profile = response.json()
                
                # Verify updates were applied
                success = True
                details = []
                
                if updated_profile.get("phone") != update_data["phone"]:
                    success = False
                    details.append(f"Phone not updated: expected {update_data['phone']}, got {updated_profile.get('phone')}")
                
                if updated_profile.get("bio") != update_data["bio"]:
                    success = False
                    details.append(f"Bio not updated: expected {update_data['bio']}, got {updated_profile.get('bio')}")
                
                if updated_profile.get("location") != update_data["location"]:
                    success = False
                    details.append(f"Location not updated: expected {update_data['location']}, got {updated_profile.get('location')}")
                
                # Check that user_id is preserved
                if not updated_profile.get("user_id"):
                    success = False
                    details.append("user_id field missing after update")
                
                if success:
                    self.log_test("PUT /profile - Regular Fields", True, "Regular profile fields updated successfully")
                else:
                    self.log_test("PUT /profile - Regular Fields", False, "; ".join(details))
                
                # Test updating business fields
                business_update = {
                    "is_business": True,
                    "company_name": "Test Company LLC",
                    "country": "USA",
                    "vat_number": "VAT123456789"
                }
                
                response = self.session.put(f"{BASE_URL}/profile", json=business_update)
                
                if response.status_code == 200:
                    business_profile = response.json()
                    
                    business_success = True
                    business_details = []
                    
                    if business_profile.get("is_business") != business_update["is_business"]:
                        business_success = False
                        business_details.append(f"is_business not updated: expected {business_update['is_business']}, got {business_profile.get('is_business')}")
                    
                    if business_profile.get("company_name") != business_update["company_name"]:
                        business_success = False
                        business_details.append(f"company_name not updated: expected {business_update['company_name']}, got {business_profile.get('company_name')}")
                    
                    if business_profile.get("country") != business_update["country"]:
                        business_success = False
                        business_details.append(f"country not updated: expected {business_update['country']}, got {business_profile.get('country')}")
                    
                    if business_profile.get("vat_number") != business_update["vat_number"]:
                        business_success = False
                        business_details.append(f"vat_number not updated: expected {business_update['vat_number']}, got {business_profile.get('vat_number')}")
                    
                    if business_success:
                        self.log_test("PUT /profile - Business Fields", True, "Business profile fields updated successfully")
                    else:
                        self.log_test("PUT /profile - Business Fields", False, "; ".join(business_details))
                    
                    return business_success
                else:
                    self.log_test("PUT /profile - Business Fields", False, f"Status: {response.status_code}, Response: {response.text}")
                    return False
                
                return success
            else:
                self.log_test("PUT /profile - Regular Fields", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT /profile - Update", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_stats(self):
        """Test GET /api/profile/stats endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/profile/stats")
            
            if response.status_code == 200:
                stats_data = response.json()
                
                # Check required stats fields
                required_stats = ["total_orders", "total_listings", "total_spent", "total_earned", "avg_rating", "total_reviews"]
                missing_stats = [field for field in required_stats if field not in stats_data]
                
                if missing_stats:
                    self.log_test("GET /profile/stats", False, f"Missing stats fields: {missing_stats}")
                    return False
                
                # Verify data types
                numeric_fields = ["total_orders", "total_listings", "total_spent", "total_earned", "avg_rating", "total_reviews"]
                type_errors = []
                
                for field in numeric_fields:
                    value = stats_data.get(field)
                    if not isinstance(value, (int, float)):
                        type_errors.append(f"{field}: expected number, got {type(value)}")
                
                if type_errors:
                    self.log_test("GET /profile/stats - Data Types", False, "; ".join(type_errors))
                    return False
                
                stats_summary = {
                    "total_orders": stats_data["total_orders"],
                    "total_listings": stats_data["total_listings"],
                    "total_spent": stats_data["total_spent"],
                    "total_earned": stats_data["total_earned"],
                    "avg_rating": stats_data["avg_rating"],
                    "total_reviews": stats_data["total_reviews"]
                }
                
                self.log_test("GET /profile/stats", True, f"Stats retrieved: {stats_summary}")
                return True
            else:
                self.log_test("GET /profile/stats", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /profile/stats", False, f"Exception: {str(e)}")
            return False
    
    def test_my_listings(self):
        """Test GET /api/listings/my-listings endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/listings/my-listings")
            
            if response.status_code == 200:
                listings_data = response.json()
                
                # Should return a list (even if empty)
                if not isinstance(listings_data, list):
                    self.log_test("GET /listings/my-listings", False, f"Expected list, got {type(listings_data)}")
                    return False
                
                # If there are listings, check their structure
                if listings_data:
                    first_listing = listings_data[0]
                    required_listing_fields = ["id", "title", "seller_id", "seller_name", "seller_username", "status", "created_at"]
                    missing_listing_fields = [field for field in required_listing_fields if field not in first_listing]
                    
                    if missing_listing_fields:
                        self.log_test("GET /listings/my-listings - Structure", False, f"Missing listing fields: {missing_listing_fields}")
                        return False
                    
                    # Verify seller information is populated
                    if not first_listing.get("seller_name") or not first_listing.get("seller_username"):
                        self.log_test("GET /listings/my-listings - Seller Info", False, "Seller name or username missing")
                        return False
                
                self.log_test("GET /listings/my-listings", True, f"Retrieved {len(listings_data)} user listings")
                return True
            else:
                self.log_test("GET /listings/my-listings", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /listings/my-listings", False, f"Exception: {str(e)}")
            return False
    
    def test_user_orders(self):
        """Test GET /api/orders endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/orders")
            
            if response.status_code == 200:
                orders_data = response.json()
                
                # Should return a list (even if empty)
                if not isinstance(orders_data, list):
                    self.log_test("GET /orders", False, f"Expected list, got {type(orders_data)}")
                    return False
                
                # If there are orders, check their structure
                if orders_data:
                    first_order = orders_data[0]
                    
                    # Check for order structure with nested objects
                    if "order" not in first_order:
                        self.log_test("GET /orders - Structure", False, "Missing 'order' object in response")
                        return False
                    
                    order_obj = first_order["order"]
                    required_order_fields = ["id", "buyer_id", "seller_id", "listing_id", "total_amount", "status", "created_at"]
                    missing_order_fields = [field for field in required_order_fields if field not in order_obj]
                    
                    if missing_order_fields:
                        self.log_test("GET /orders - Order Fields", False, f"Missing order fields: {missing_order_fields}")
                        return False
                    
                    # Check for related objects
                    if "listing" not in first_order or "buyer" not in first_order or "seller" not in first_order:
                        self.log_test("GET /orders - Related Objects", False, "Missing listing, buyer, or seller objects")
                        return False
                
                self.log_test("GET /orders", True, f"Retrieved {len(orders_data)} user orders with complete relationship data")
                return True
            else:
                self.log_test("GET /orders", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /orders", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_data_persistence(self):
        """Test that profile updates persist correctly"""
        try:
            # Get current profile
            initial_response = self.session.get(f"{BASE_URL}/profile")
            if initial_response.status_code != 200:
                self.log_test("Profile Persistence - Initial Get", False, f"Status: {initial_response.status_code}")
                return False
            
            initial_profile = initial_response.json()
            initial_user_id = initial_profile.get("user_id")
            
            # Update profile with test data
            test_update = {
                "phone": "+1-555-9999",
                "bio": "Persistence test bio",
                "location": "Persistence Test City"
            }
            
            update_response = self.session.put(f"{BASE_URL}/profile", json=test_update)
            if update_response.status_code != 200:
                self.log_test("Profile Persistence - Update", False, f"Status: {update_response.status_code}")
                return False
            
            # Get profile again to verify persistence
            verify_response = self.session.get(f"{BASE_URL}/profile")
            if verify_response.status_code != 200:
                self.log_test("Profile Persistence - Verify Get", False, f"Status: {verify_response.status_code}")
                return False
            
            verified_profile = verify_response.json()
            
            # Check that updates persisted
            persistence_success = True
            persistence_details = []
            
            if verified_profile.get("phone") != test_update["phone"]:
                persistence_success = False
                persistence_details.append(f"Phone not persisted: expected {test_update['phone']}, got {verified_profile.get('phone')}")
            
            if verified_profile.get("bio") != test_update["bio"]:
                persistence_success = False
                persistence_details.append(f"Bio not persisted: expected {test_update['bio']}, got {verified_profile.get('bio')}")
            
            if verified_profile.get("location") != test_update["location"]:
                persistence_success = False
                persistence_details.append(f"Location not persisted: expected {test_update['location']}, got {verified_profile.get('location')}")
            
            # Check that user_id is preserved
            if verified_profile.get("user_id") != initial_user_id:
                persistence_success = False
                persistence_details.append(f"user_id changed: expected {initial_user_id}, got {verified_profile.get('user_id')}")
            
            if persistence_success:
                self.log_test("Profile Data Persistence", True, "All profile changes persist correctly across requests")
            else:
                self.log_test("Profile Data Persistence", False, "; ".join(persistence_details))
            
            return persistence_success
            
        except Exception as e:
            self.log_test("Profile Data Persistence", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all profile endpoint tests"""
        print("=" * 80)
        print("CATALORO v1.0.4 PROFILE ENDPOINTS TESTING")
        print("Testing Phase 1 fixes for profile functionality")
        print("=" * 80)
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run profile endpoint tests
        tests_passed = 0
        total_tests = 6
        
        # Test 1: Profile Data Retrieval
        if self.test_get_profile():
            tests_passed += 1
        
        # Test 2: Profile Updates
        if self.test_update_profile():
            tests_passed += 1
        
        # Test 3: Profile Stats
        if self.test_profile_stats():
            tests_passed += 1
        
        # Test 4: My Listings
        if self.test_my_listings():
            tests_passed += 1
        
        # Test 5: User Orders
        if self.test_user_orders():
            tests_passed += 1
        
        # Test 6: Data Persistence
        if self.test_profile_data_persistence():
            tests_passed += 1
        
        # Summary
        print("=" * 80)
        print("PROFILE ENDPOINTS TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (tests_passed / total_tests) * 100
        print(f"Tests Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"] and not result["success"]:
                print(f"   {result['details']}")
        
        print()
        if tests_passed == total_tests:
            print("🎉 ALL PROFILE ENDPOINT TESTS PASSED!")
            print("✅ Profile functionality is working correctly")
        else:
            print(f"⚠️  {total_tests - tests_passed} test(s) failed")
            print("❌ Profile functionality has issues that need attention")
        
        print("=" * 80)
        return tests_passed == total_tests

if __name__ == "__main__":
    tester = ProfileEndpointTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)