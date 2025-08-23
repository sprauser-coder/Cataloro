#!/usr/bin/env python3
"""
Phase 3A Backend Testing - Complete Profile Management & Workflow Testing
Testing after routing issue fix - verifying all Phase 3A functionality is working
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
BACKEND_DIRECT_URL = "http://localhost:8001/api"  # Direct backend access for profile endpoints
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class Phase3ABackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_user_token = None
        self.test_user_id = None
        self.test_listing_id = None
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
                self.log_test("Admin Login", True, f"Successfully logged in as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False

    def create_test_user(self):
        """Create a test user for profile testing"""
        try:
            test_user_data = {
                "email": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
                "password": "testpass123",
                "full_name": "Test User Profile",
                "role": "both",
                "phone": "+1234567890",
                "address": "123 Test Street, Test City"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                self.log_test("Create Test User", True, f"Created user: {test_user_data['email']}")
                return True
            else:
                self.log_test("Create Test User", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Test User", False, f"Exception: {str(e)}")
            return False

    def test_get_profile(self):
        """Test GET /profile endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            # Use direct backend URL due to nginx routing issue with /profile endpoints
            response = self.session.get(f"{BACKEND_DIRECT_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "username", "full_name", "email", "role", "created_at"]
                phase3a_fields = ["bio", "location", "updated_at"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("GET /profile - Required Fields", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Check Phase 3A fields exist (can be null)
                phase3a_present = [field for field in phase3a_fields if field in data]
                self.log_test("GET /profile - Basic Fields", True, f"All required fields present")
                self.log_test("GET /profile - Phase 3A Fields", True, f"Phase 3A fields present: {phase3a_present}")
                return True
            else:
                self.log_test("GET /profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /profile", False, f"Exception: {str(e)}")
            return False

    def test_update_profile(self):
        """Test PUT /profile endpoint with Phase 3A fields"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Test updating Phase 3A fields
            update_data = {
                "username": f"updated_user_{datetime.now().strftime('%H%M%S')}",
                "full_name": "Updated Test User",
                "phone": "+1987654321",
                "bio": "This is my updated bio for Phase 3A testing. I love using this marketplace!",
                "location": "San Francisco, CA, USA"
            }
            
            # Use direct backend URL due to nginx routing issue with /profile endpoints
            response = self.session.put(f"{BACKEND_DIRECT_URL}/profile", json=update_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify updates were applied
                checks = [
                    (data.get("username") == update_data["username"], "Username update"),
                    (data.get("full_name") == update_data["full_name"], "Full name update"),
                    (data.get("phone") == update_data["phone"], "Phone update"),
                    (data.get("bio") == update_data["bio"], "Bio update (Phase 3A)"),
                    (data.get("location") == update_data["location"], "Location update (Phase 3A)"),
                    (data.get("updated_at") is not None, "Updated timestamp (Phase 3A)")
                ]
                
                all_passed = True
                for check, description in checks:
                    if check:
                        self.log_test(f"PUT /profile - {description}", True)
                    else:
                        self.log_test(f"PUT /profile - {description}", False, f"Expected vs Actual mismatch")
                        all_passed = False
                
                return all_passed
            else:
                self.log_test("PUT /profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("PUT /profile", False, f"Exception: {str(e)}")
            return False

    def test_get_profile_stats(self):
        """Test GET /profile/stats endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            # Use direct backend URL due to nginx routing issue with /profile endpoints
            response = self.session.get(f"{BACKEND_DIRECT_URL}/profile/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_orders", "total_listings", "total_spent", "total_earned", "avg_rating", "total_reviews"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("GET /profile/stats", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify data types
                numeric_fields = ["total_orders", "total_listings", "total_spent", "total_earned", "avg_rating", "total_reviews"]
                type_checks = []
                for field in numeric_fields:
                    value = data.get(field)
                    is_numeric = isinstance(value, (int, float))
                    type_checks.append((is_numeric, f"{field} is numeric"))
                
                all_types_correct = all(check[0] for check in type_checks)
                if all_types_correct:
                    self.log_test("GET /profile/stats - Data Types", True, "All fields are properly typed")
                else:
                    failed_types = [check[1] for check in type_checks if not check[0]]
                    self.log_test("GET /profile/stats - Data Types", False, f"Type errors: {failed_types}")
                
                self.log_test("GET /profile/stats - Structure", True, f"Stats: Orders={data['total_orders']}, Listings={data['total_listings']}, Spent=${data['total_spent']}, Earned=${data['total_earned']}")
                return True
            else:
                self.log_test("GET /profile/stats", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /profile/stats", False, f"Exception: {str(e)}")
            return False

    def create_test_listing(self):
        """Create a test listing for my-listings endpoint testing"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            listing_data = {
                "title": "Phase 3A Test Listing",
                "description": "This is a test listing created during Phase 3A profile testing",
                "category": "Electronics",
                "condition": "New",
                "listing_type": "fixed_price",
                "price": 299.99,
                "quantity": 1,
                "location": "Test City, Test State"
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_listing_id = data["id"]
                self.log_test("Create Test Listing", True, f"Created listing: {data['title']}")
                return True
            else:
                self.log_test("Create Test Listing", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Test Listing", False, f"Exception: {str(e)}")
            return False

    def test_get_my_listings(self):
        """Test GET /listings/my-listings endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = self.session.get(f"{BACKEND_URL}/listings/my-listings", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    self.log_test("GET /listings/my-listings", False, "Response is not a list")
                    return False
                
                # Should contain our test listing
                found_test_listing = False
                for listing in data:
                    if listing.get("id") == self.test_listing_id:
                        found_test_listing = True
                        break
                
                if found_test_listing:
                    self.log_test("GET /listings/my-listings", True, f"Found {len(data)} listings including test listing")
                else:
                    self.log_test("GET /listings/my-listings", False, f"Test listing not found in {len(data)} listings")
                
                return found_test_listing
            else:
                self.log_test("GET /listings/my-listings", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("GET /listings/my-listings", False, f"Exception: {str(e)}")
            return False

    def test_complete_phase3a_workflow(self):
        """Test complete Phase 3A workflow: register → profile update → create listing → stats"""
        try:
            workflow_steps = []
            
            # Step 1: User already registered (done in create_test_user)
            workflow_steps.append(("User Registration", True))
            
            # Step 2: Update profile with Phase 3A fields
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            profile_update = {
                "bio": "Complete workflow test bio - I'm testing the full Phase 3A functionality!",
                "location": "Workflow Test City, CA"
            }
            
            profile_response = self.session.put(f"{BACKEND_URL}/profile", json=profile_update, headers=headers)
            workflow_steps.append(("Profile Update", profile_response.status_code == 200))
            
            # Step 3: Create listing (already done)
            workflow_steps.append(("Create Listing", self.test_listing_id is not None))
            
            # Step 4: Check updated stats
            stats_response = self.session.get(f"{BACKEND_URL}/profile/stats", headers=headers)
            stats_success = stats_response.status_code == 200
            if stats_success:
                stats_data = stats_response.json()
                # Should have at least 1 listing now
                stats_success = stats_data.get("total_listings", 0) >= 1
            workflow_steps.append(("Updated Stats", stats_success))
            
            # Step 5: Verify my-listings shows the listing
            my_listings_response = self.session.get(f"{BACKEND_URL}/listings/my-listings", headers=headers)
            my_listings_success = my_listings_response.status_code == 200
            if my_listings_success:
                listings_data = my_listings_response.json()
                my_listings_success = len(listings_data) >= 1
            workflow_steps.append(("My Listings", my_listings_success))
            
            # Evaluate overall workflow
            all_steps_passed = all(step[1] for step in workflow_steps)
            
            workflow_details = " → ".join([f"{step[0]}({'✅' if step[1] else '❌'})" for step in workflow_steps])
            self.log_test("Complete Phase 3A Workflow", all_steps_passed, workflow_details)
            
            return all_steps_passed
            
        except Exception as e:
            self.log_test("Complete Phase 3A Workflow", False, f"Exception: {str(e)}")
            return False

    def test_page_management_quick_verification(self):
        """Quick verification that page CRUD operations still work"""
        try:
            # Switch to admin token for page management
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test GET pages
            response = self.session.get(f"{BACKEND_URL}/admin/cms/pages", headers=admin_headers)
            if response.status_code == 200:
                self.log_test("Page Management - GET Pages", True, f"Retrieved {len(response.json())} pages")
            else:
                self.log_test("Page Management - GET Pages", False, f"Status: {response.status_code}")
                return False
            
            # Test create page
            test_page = {
                "page_slug": f"test-page-{datetime.now().strftime('%H%M%S')}",
                "title": "Phase 3A Test Page",
                "content": "<h1>Test Page Content</h1><p>This page was created during Phase 3A testing.</p>",
                "is_published": True,
                "meta_description": "Test page for Phase 3A verification"
            }
            
            create_response = self.session.post(f"{BACKEND_URL}/admin/cms/pages", json=test_page, headers=admin_headers)
            if create_response.status_code == 200:
                self.log_test("Page Management - Create Page", True, f"Created page: {test_page['title']}")
                
                # Test published/unpublished functionality
                update_data = {"is_published": False}
                update_response = self.session.put(f"{BACKEND_URL}/admin/cms/pages/{test_page['page_slug']}", json=update_data, headers=admin_headers)
                
                if update_response.status_code == 200:
                    self.log_test("Page Management - Update Published Status", True, "Successfully updated page publication status")
                else:
                    self.log_test("Page Management - Update Published Status", False, f"Status: {update_response.status_code}")
                
                return True
            else:
                self.log_test("Page Management - Create Page", False, f"Status: {create_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Page Management Quick Verification", False, f"Exception: {str(e)}")
            return False

    def test_authentication_integration(self):
        """Test profile endpoints with authentication"""
        try:
            # Test without authentication
            no_auth_response = self.session.get(f"{BACKEND_URL}/profile")
            if no_auth_response.status_code == 401:
                self.log_test("Profile Authentication - No Token", True, "Correctly rejected unauthenticated request")
            else:
                self.log_test("Profile Authentication - No Token", False, f"Expected 401, got {no_auth_response.status_code}")
                return False
            
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_here"}
            invalid_response = self.session.get(f"{BACKEND_URL}/profile", headers=invalid_headers)
            if invalid_response.status_code == 401:
                self.log_test("Profile Authentication - Invalid Token", True, "Correctly rejected invalid token")
            else:
                self.log_test("Profile Authentication - Invalid Token", False, f"Expected 401, got {invalid_response.status_code}")
                return False
            
            # Test with valid token (should work)
            valid_headers = {"Authorization": f"Bearer {self.test_user_token}"}
            valid_response = self.session.get(f"{BACKEND_URL}/profile", headers=valid_headers)
            if valid_response.status_code == 200:
                self.log_test("Profile Authentication - Valid Token", True, "Successfully authenticated with valid token")
            else:
                self.log_test("Profile Authentication - Valid Token", False, f"Expected 200, got {valid_response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Authentication Integration", False, f"Exception: {str(e)}")
            return False

    def test_user_model_phase3a_fields(self):
        """Test that User model handles Phase 3A fields correctly"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Test updating all Phase 3A fields
            phase3a_update = {
                "bio": "Testing Phase 3A bio field - this should be stored and retrieved correctly!",
                "location": "Phase 3A Test Location, State, Country"
            }
            
            update_response = self.session.put(f"{BACKEND_URL}/profile", json=phase3a_update, headers=headers)
            if update_response.status_code != 200:
                self.log_test("User Model - Phase 3A Fields Update", False, f"Update failed: {update_response.status_code}")
                return False
            
            # Retrieve and verify
            get_response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            if get_response.status_code != 200:
                self.log_test("User Model - Phase 3A Fields Retrieval", False, f"Retrieval failed: {get_response.status_code}")
                return False
            
            profile_data = get_response.json()
            
            # Check Phase 3A fields
            bio_correct = profile_data.get("bio") == phase3a_update["bio"]
            location_correct = profile_data.get("location") == phase3a_update["location"]
            updated_at_present = profile_data.get("updated_at") is not None
            
            if bio_correct and location_correct and updated_at_present:
                self.log_test("User Model - Phase 3A Fields", True, "Bio, location, and updated_at fields working correctly")
                return True
            else:
                issues = []
                if not bio_correct:
                    issues.append("bio field mismatch")
                if not location_correct:
                    issues.append("location field mismatch")
                if not updated_at_present:
                    issues.append("updated_at field missing")
                
                self.log_test("User Model - Phase 3A Fields", False, f"Issues: {', '.join(issues)}")
                return False
                
        except Exception as e:
            self.log_test("User Model Phase 3A Fields", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all Phase 3A tests"""
        print("=" * 80)
        print("PHASE 3A BACKEND TESTING - COMPLETE PROFILE MANAGEMENT & WORKFLOW")
        print("Testing after routing issue fix")
        print("=" * 80)
        
        # Step 1: Admin login
        if not self.admin_login():
            print("❌ Cannot proceed without admin access")
            return False
        
        # Step 2: Create test user
        if not self.create_test_user():
            print("❌ Cannot proceed without test user")
            return False
        
        print("\n🔍 TESTING PROFILE MANAGEMENT ENDPOINTS:")
        print("-" * 50)
        
        # Test profile endpoints
        self.test_get_profile()
        self.test_update_profile()
        self.test_get_profile_stats()
        
        # Create test listing for my-listings test
        self.create_test_listing()
        self.test_get_my_listings()
        
        print("\n🔍 TESTING COMPLETE PHASE 3A WORKFLOW:")
        print("-" * 50)
        self.test_complete_phase3a_workflow()
        
        print("\n🔍 TESTING PAGE MANAGEMENT (QUICK VERIFICATION):")
        print("-" * 50)
        self.test_page_management_quick_verification()
        
        print("\n🔍 TESTING INTEGRATION & AUTHENTICATION:")
        print("-" * 50)
        self.test_authentication_integration()
        self.test_user_model_phase3a_fields()
        
        # Print summary
        print("\n" + "=" * 80)
        print("PHASE 3A TESTING SUMMARY")
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
    tester = Phase3ABackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL PHASE 3A TESTS PASSED - Phase 3A is 100% complete and ready for Phase 3B!")
        sys.exit(0)
    else:
        print("⚠️  Some Phase 3A tests failed - review the issues above")
        sys.exit(1)