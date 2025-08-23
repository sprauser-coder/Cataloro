#!/usr/bin/env python3
"""
Phase 3A Profile Management Testing
Tests the complete profile management functionality including:
1. Profile endpoints (GET/PUT /profile, GET /profile/stats, GET /listings/my-listings)
2. Updated User Model with new fields (bio, location, updated_at)
3. Integration testing with authentication
4. Complete Phase 3A workflow testing
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class Phase3AProfileTester:
    def __init__(self):
        self.admin_token = None
        self.test_user_token = None
        self.test_user_id = None
        self.test_listing_id = None
        self.results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append(f"{status}: {test_name}")
        if details:
            self.results.append(f"    Details: {details}")
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.log_result("Admin Authentication", True, f"Token obtained for {ADMIN_EMAIL}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_test_user(self):
        """Create a test user for profile testing"""
        try:
            test_user_data = {
                "email": "profiletest@example.com",
                "username": "profiletester",
                "password": "testpass123",
                "full_name": "Profile Test User",
                "role": "both",
                "phone": "555-0123",
                "address": "123 Test Street"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                self.log_result("Test User Creation", True, f"User created with ID: {self.test_user_id}")
                return True
            else:
                self.log_result("Test User Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test User Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_get_profile(self):
        """Test GET /profile endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = requests.get(f"{BACKEND_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Verify required fields are present
                required_fields = ["id", "username", "full_name", "email", "role", "created_at"]
                missing_fields = [field for field in required_fields if field not in profile_data]
                
                if missing_fields:
                    self.log_result("GET /profile - Required Fields", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify new Phase 3A fields are present (can be null)
                phase3a_fields = ["bio", "location", "updated_at"]
                for field in phase3a_fields:
                    if field not in profile_data:
                        self.log_result("GET /profile - Phase 3A Fields", False, f"Missing Phase 3A field: {field}")
                        return False
                
                self.log_result("GET /profile", True, f"Profile retrieved with all required fields")
                return True
            else:
                self.log_result("GET /profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("GET /profile", False, f"Exception: {str(e)}")
            return False
    
    def test_update_profile(self):
        """Test PUT /profile endpoint with new Phase 3A fields"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Test updating all profile fields including new Phase 3A fields
            update_data = {
                "username": "updatedprofiletester",
                "full_name": "Updated Profile Test User",
                "phone": "555-9999",
                "bio": "This is my updated bio for Phase 3A testing",
                "location": "Updated Test City, TC 12345"
            }
            
            response = requests.put(f"{BACKEND_URL}/profile", headers=headers, json=update_data)
            
            if response.status_code == 200:
                updated_profile = response.json()
                
                # Verify all updates were applied
                for field, expected_value in update_data.items():
                    if updated_profile.get(field) != expected_value:
                        self.log_result("PUT /profile - Field Updates", False, 
                                      f"Field {field}: expected '{expected_value}', got '{updated_profile.get(field)}'")
                        return False
                
                # Verify updated_at field was set
                if not updated_profile.get("updated_at"):
                    self.log_result("PUT /profile - Updated At", False, "updated_at field not set")
                    return False
                
                self.log_result("PUT /profile", True, "All profile fields updated successfully including Phase 3A fields")
                return True
            else:
                self.log_result("PUT /profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("PUT /profile", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_username_uniqueness(self):
        """Test username uniqueness validation in profile update"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Try to update username to admin's username (should fail)
            update_data = {"username": "admin"}
            
            response = requests.put(f"{BACKEND_URL}/profile", headers=headers, json=update_data)
            
            if response.status_code == 400:
                error_data = response.json()
                if "already taken" in error_data.get("detail", "").lower():
                    self.log_result("PUT /profile - Username Uniqueness", True, "Correctly rejected duplicate username")
                    return True
                else:
                    self.log_result("PUT /profile - Username Uniqueness", False, f"Wrong error message: {error_data}")
                    return False
            else:
                self.log_result("PUT /profile - Username Uniqueness", False, f"Should have failed with 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("PUT /profile - Username Uniqueness", False, f"Exception: {str(e)}")
            return False
    
    def create_test_listing(self):
        """Create a test listing for my-listings testing"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            listing_data = {
                "title": "Phase 3A Test Listing",
                "description": "Test listing for Phase 3A profile testing",
                "category": "Electronics",
                "listing_type": "fixed_price",
                "price": 299.99,
                "condition": "New",
                "quantity": 1,
                "location": "Test City"
            }
            
            response = requests.post(f"{BACKEND_URL}/listings", headers=headers, json=listing_data)
            
            if response.status_code == 200:
                listing = response.json()
                self.test_listing_id = listing["id"]
                self.log_result("Test Listing Creation", True, f"Listing created with ID: {self.test_listing_id}")
                return True
            else:
                self.log_result("Test Listing Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test Listing Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_get_my_listings(self):
        """Test GET /listings/my-listings endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = requests.get(f"{BACKEND_URL}/listings/my-listings", headers=headers)
            
            if response.status_code == 200:
                listings = response.json()
                
                if not isinstance(listings, list):
                    self.log_result("GET /listings/my-listings", False, "Response is not a list")
                    return False
                
                # Should have at least our test listing
                if len(listings) == 0:
                    self.log_result("GET /listings/my-listings", False, "No listings returned")
                    return False
                
                # Find our test listing
                test_listing = None
                for listing in listings:
                    if listing.get("id") == self.test_listing_id:
                        test_listing = listing
                        break
                
                if not test_listing:
                    self.log_result("GET /listings/my-listings", False, "Test listing not found in results")
                    return False
                
                # Verify seller information is included
                if not test_listing.get("seller_name") or not test_listing.get("seller_username"):
                    self.log_result("GET /listings/my-listings", False, "Seller information missing from listing")
                    return False
                
                self.log_result("GET /listings/my-listings", True, f"Retrieved {len(listings)} listings with seller info")
                return True
            else:
                self.log_result("GET /listings/my-listings", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("GET /listings/my-listings", False, f"Exception: {str(e)}")
            return False
    
    def test_get_profile_stats(self):
        """Test GET /profile/stats endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = requests.get(f"{BACKEND_URL}/profile/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                
                # Verify required stats fields
                required_stats = ["total_orders", "total_listings", "total_spent", "total_earned", "avg_rating", "total_reviews"]
                missing_stats = [field for field in required_stats if field not in stats]
                
                if missing_stats:
                    self.log_result("GET /profile/stats", False, f"Missing stats fields: {missing_stats}")
                    return False
                
                # Verify data types
                numeric_fields = ["total_orders", "total_listings", "total_spent", "total_earned", "avg_rating", "total_reviews"]
                for field in numeric_fields:
                    if not isinstance(stats[field], (int, float)):
                        self.log_result("GET /profile/stats", False, f"Field {field} is not numeric: {type(stats[field])}")
                        return False
                
                # Should have at least 1 listing from our test
                if stats["total_listings"] < 1:
                    self.log_result("GET /profile/stats", False, f"Expected at least 1 listing, got {stats['total_listings']}")
                    return False
                
                self.log_result("GET /profile/stats", True, f"Stats: {stats['total_listings']} listings, {stats['total_orders']} orders")
                return True
            else:
                self.log_result("GET /profile/stats", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("GET /profile/stats", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_authentication(self):
        """Test that profile endpoints require authentication"""
        try:
            # Test without token
            endpoints = [
                "/profile",
                "/profile/stats", 
                "/listings/my-listings"
            ]
            
            all_passed = True
            for endpoint in endpoints:
                response = requests.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code != 403:
                    self.log_result(f"Auth Required - {endpoint}", False, f"Expected 403, got {response.status_code}")
                    all_passed = False
                else:
                    self.log_result(f"Auth Required - {endpoint}", True, "Correctly requires authentication")
            
            return all_passed
                
        except Exception as e:
            self.log_result("Profile Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_phase3a_workflow(self):
        """Test complete Phase 3A workflow: Register → Update Profile → Create Listing → Check Stats"""
        try:
            # Create a new user for workflow testing
            workflow_user_data = {
                "email": "workflow@example.com",
                "username": "workflowuser",
                "password": "workflow123",
                "full_name": "Workflow Test User",
                "role": "both"
            }
            
            # Step 1: Register
            response = requests.post(f"{BACKEND_URL}/auth/register", json=workflow_user_data)
            if response.status_code != 200:
                self.log_result("Phase 3A Workflow - Register", False, f"Registration failed: {response.status_code}")
                return False
            
            workflow_token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {workflow_token}"}
            
            # Step 2: Update Profile with Phase 3A fields
            profile_update = {
                "bio": "I'm a workflow test user for Phase 3A",
                "location": "Workflow City, WF 54321",
                "phone": "555-WORK"
            }
            
            response = requests.put(f"{BACKEND_URL}/profile", headers=headers, json=profile_update)
            if response.status_code != 200:
                self.log_result("Phase 3A Workflow - Update Profile", False, f"Profile update failed: {response.status_code}")
                return False
            
            # Step 3: Create Listing
            listing_data = {
                "title": "Workflow Test Product",
                "description": "Product created during workflow testing",
                "category": "Books",
                "listing_type": "fixed_price",
                "price": 19.99,
                "condition": "Used",
                "quantity": 1,
                "location": "Workflow City"
            }
            
            response = requests.post(f"{BACKEND_URL}/listings", headers=headers, json=listing_data)
            if response.status_code != 200:
                self.log_result("Phase 3A Workflow - Create Listing", False, f"Listing creation failed: {response.status_code}")
                return False
            
            # Step 4: Check Stats
            response = requests.get(f"{BACKEND_URL}/profile/stats", headers=headers)
            if response.status_code != 200:
                self.log_result("Phase 3A Workflow - Check Stats", False, f"Stats retrieval failed: {response.status_code}")
                return False
            
            stats = response.json()
            if stats["total_listings"] < 1:
                self.log_result("Phase 3A Workflow - Verify Stats", False, f"Expected at least 1 listing in stats")
                return False
            
            # Step 5: Verify My Listings
            response = requests.get(f"{BACKEND_URL}/listings/my-listings", headers=headers)
            if response.status_code != 200:
                self.log_result("Phase 3A Workflow - My Listings", False, f"My listings retrieval failed: {response.status_code}")
                return False
            
            my_listings = response.json()
            if len(my_listings) < 1:
                self.log_result("Phase 3A Workflow - Verify My Listings", False, "No listings found in my-listings")
                return False
            
            self.log_result("Phase 3A Complete Workflow", True, "Register → Update Profile → Create Listing → Check Stats → Verify My Listings")
            return True
                
        except Exception as e:
            self.log_result("Phase 3A Complete Workflow", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            if self.admin_token:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                
                # Delete test users (this will also clean up their listings)
                test_emails = ["profiletest@example.com", "workflow@example.com"]
                
                for email in test_emails:
                    # Find user by email and delete
                    users_response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
                    if users_response.status_code == 200:
                        users = users_response.json()
                        for user in users:
                            if user.get("email") == email:
                                delete_response = requests.delete(f"{BACKEND_URL}/admin/users/{user['id']}", headers=headers)
                                if delete_response.status_code == 200:
                                    self.log_result(f"Cleanup - Delete {email}", True, "User and data deleted")
                                break
                
        except Exception as e:
            self.log_result("Cleanup", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Phase 3A profile tests"""
        print("🚀 PHASE 3A PROFILE MANAGEMENT TESTING STARTED")
        print("=" * 60)
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        if not self.create_test_user():
            print("❌ Cannot proceed without test user")
            return False
        
        # Core Profile Tests
        tests = [
            self.test_profile_authentication,
            self.test_get_profile,
            self.test_update_profile,
            self.test_profile_username_uniqueness,
            self.create_test_listing,
            self.test_get_my_listings,
            self.test_get_profile_stats,
            self.test_complete_phase3a_workflow
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PHASE 3A PROFILE TESTING SUMMARY")
        print("=" * 60)
        
        for result in self.results:
            print(result)
        
        success_rate = (passed / total) * 100
        print(f"\n🎯 SUCCESS RATE: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("✅ ALL PHASE 3A PROFILE TESTS PASSED - FUNCTIONALITY IS WORKING CORRECTLY")
        elif success_rate >= 80:
            print("⚠️  MOST PHASE 3A PROFILE TESTS PASSED - MINOR ISSUES DETECTED")
        else:
            print("❌ SIGNIFICANT PHASE 3A PROFILE ISSUES DETECTED - REQUIRES ATTENTION")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = Phase3AProfileTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)