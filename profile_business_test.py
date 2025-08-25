#!/usr/bin/env python3
"""
Profile Endpoints with Business Fields Testing
==============================================

Testing the updated profile endpoints with the new business fields:

1. GET /api/profile - Verify it returns all fields including the new business fields:
   - user_id (should display the user number)
   - is_business, company_name, country, vat_number (business fields)

2. PUT /api/profile - Test updating both regular profile fields and business fields:
   - Update regular fields: phone, bio, location
   - Update business fields: is_business=true, company_name="Test Company", country="USA", vat_number="VAT123"
   - Verify all fields persist correctly

3. Data persistence - After update, call GET /api/profile again to confirm all changes were saved

Use admin credentials: admin@marketplace.com/admin123

This relates to fixing the "My profile changes not saved and missing user number display" bug.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://marketplace-ready.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ProfileEndpointsTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_result("Admin Authentication", True, f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Failed to authenticate: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_get_profile_endpoint(self):
        """Test GET /api/profile endpoint - verify all fields including business fields"""
        try:
            response = self.session.get(f"{BASE_URL}/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Check required fields
                required_fields = ["id", "user_id", "username", "full_name", "email", "role", "created_at"]
                missing_fields = [field for field in required_fields if field not in profile_data]
                
                if missing_fields:
                    self.log_result("GET Profile - Required Fields", False, 
                                  f"Missing required fields: {missing_fields}", profile_data)
                    return False
                
                # Check business fields are present (even if None/null)
                business_fields = ["is_business", "company_name", "country", "vat_number"]
                missing_business_fields = [field for field in business_fields if field not in profile_data]
                
                if missing_business_fields:
                    self.log_result("GET Profile - Business Fields", False, 
                                  f"Missing business fields: {missing_business_fields}", profile_data)
                    return False
                
                # Check user_id field specifically (should display user number)
                user_id = profile_data.get("user_id", "")
                if not user_id or user_id == "":
                    self.log_result("GET Profile - User ID", False, 
                                  "user_id field is empty or missing", profile_data)
                    return False
                
                self.log_result("GET Profile Endpoint", True, 
                              f"All fields present including business fields. User ID: {user_id}")
                
                # Store current profile for comparison
                self.original_profile = profile_data
                return True
                
            else:
                self.log_result("GET Profile Endpoint", False, 
                              f"Failed to get profile: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("GET Profile Endpoint", False, f"Error getting profile: {str(e)}")
            return False
    
    def test_put_profile_regular_fields(self):
        """Test PUT /api/profile endpoint - update regular profile fields"""
        try:
            # Test data for regular fields
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
                failed_updates = []
                
                for field, expected_value in update_data.items():
                    actual_value = updated_profile.get(field)
                    if actual_value != expected_value:
                        success = False
                        failed_updates.append(f"{field}: expected '{expected_value}', got '{actual_value}'")
                
                if success:
                    self.log_result("PUT Profile - Regular Fields", True, 
                                  "Successfully updated phone, bio, and location")
                    self.updated_profile_regular = updated_profile
                    return True
                else:
                    self.log_result("PUT Profile - Regular Fields", False, 
                                  f"Field updates failed: {failed_updates}", updated_profile)
                    return False
                    
            else:
                self.log_result("PUT Profile - Regular Fields", False, 
                              f"Failed to update profile: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("PUT Profile - Regular Fields", False, f"Error updating profile: {str(e)}")
            return False
    
    def test_put_profile_business_fields(self):
        """Test PUT /api/profile endpoint - update business fields"""
        try:
            # Test data for business fields
            business_update_data = {
                "is_business": True,
                "company_name": "Test Company LLC",
                "country": "USA",
                "vat_number": "VAT123456789"
            }
            
            response = self.session.put(f"{BASE_URL}/profile", json=business_update_data)
            
            if response.status_code == 200:
                updated_profile = response.json()
                
                # Verify business updates were applied
                success = True
                failed_updates = []
                
                for field, expected_value in business_update_data.items():
                    actual_value = updated_profile.get(field)
                    if actual_value != expected_value:
                        success = False
                        failed_updates.append(f"{field}: expected '{expected_value}', got '{actual_value}'")
                
                if success:
                    self.log_result("PUT Profile - Business Fields", True, 
                                  "Successfully updated all business fields")
                    self.updated_profile_business = updated_profile
                    return True
                else:
                    self.log_result("PUT Profile - Business Fields", False, 
                                  f"Business field updates failed: {failed_updates}", updated_profile)
                    return False
                    
            else:
                self.log_result("PUT Profile - Business Fields", False, 
                              f"Failed to update business fields: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("PUT Profile - Business Fields", False, f"Error updating business fields: {str(e)}")
            return False
    
    def test_data_persistence(self):
        """Test data persistence - GET profile again to confirm all changes were saved"""
        try:
            response = self.session.get(f"{BASE_URL}/profile")
            
            if response.status_code == 200:
                final_profile = response.json()
                
                # Expected values after all updates
                expected_values = {
                    "phone": "+1-555-0123",
                    "bio": "Updated bio for profile testing", 
                    "location": "Test City, Test State",
                    "is_business": True,
                    "company_name": "Test Company LLC",
                    "country": "USA",
                    "vat_number": "VAT123456789"
                }
                
                # Verify all changes persisted
                success = True
                persistence_failures = []
                
                for field, expected_value in expected_values.items():
                    actual_value = final_profile.get(field)
                    if actual_value != expected_value:
                        success = False
                        persistence_failures.append(f"{field}: expected '{expected_value}', got '{actual_value}'")
                
                # Also verify user_id is still present and unchanged
                original_user_id = self.original_profile.get("user_id", "")
                final_user_id = final_profile.get("user_id", "")
                
                if original_user_id != final_user_id:
                    success = False
                    persistence_failures.append(f"user_id changed: was '{original_user_id}', now '{final_user_id}'")
                
                if success:
                    self.log_result("Data Persistence Verification", True, 
                                  f"All profile changes persisted correctly. User ID: {final_user_id}")
                    return True
                else:
                    self.log_result("Data Persistence Verification", False, 
                                  f"Persistence failures: {persistence_failures}", final_profile)
                    return False
                    
            else:
                self.log_result("Data Persistence Verification", False, 
                              f"Failed to get profile for persistence check: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Data Persistence Verification", False, f"Error checking persistence: {str(e)}")
            return False
    
    def test_user_id_display(self):
        """Test that user_id field displays the user number correctly"""
        try:
            response = self.session.get(f"{BASE_URL}/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                user_id = profile_data.get("user_id", "")
                
                # Check if user_id follows expected format (U00001, USER001, etc.)
                if user_id and len(user_id) > 0:
                    # Check if it contains some kind of user identifier
                    if any(char.isdigit() for char in user_id):
                        self.log_result("User ID Display", True, 
                                      f"User ID is properly displayed: {user_id}")
                        return True
                    else:
                        self.log_result("User ID Display", False, 
                                      f"User ID doesn't contain expected number format: {user_id}")
                        return False
                else:
                    self.log_result("User ID Display", False, 
                                  "User ID is empty or missing")
                    return False
                    
            else:
                self.log_result("User ID Display", False, 
                              f"Failed to get profile: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("User ID Display", False, f"Error checking user ID: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all profile endpoint tests"""
        print("=" * 80)
        print("PROFILE ENDPOINTS WITH BUSINESS FIELDS - COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Testing against: {BASE_URL}")
        print(f"Admin credentials: {ADMIN_EMAIL}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return False
        
        print()
        
        # Step 2: Test GET /api/profile endpoint
        print("🔍 Testing GET /api/profile endpoint...")
        get_success = self.test_get_profile_endpoint()
        
        if not get_success:
            print("❌ GET profile test failed, cannot proceed with updates")
            return False
        
        print()
        
        # Step 3: Test user ID display
        print("🔍 Testing user ID display...")
        self.test_user_id_display()
        print()
        
        # Step 4: Test PUT /api/profile with regular fields
        print("🔍 Testing PUT /api/profile with regular fields...")
        regular_success = self.test_put_profile_regular_fields()
        print()
        
        # Step 5: Test PUT /api/profile with business fields
        print("🔍 Testing PUT /api/profile with business fields...")
        business_success = self.test_put_profile_business_fields()
        print()
        
        # Step 6: Test data persistence
        print("🔍 Testing data persistence...")
        persistence_success = self.test_data_persistence()
        print()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        print()
        
        # Overall assessment
        critical_tests = ["Admin Authentication", "GET Profile Endpoint", "Data Persistence Verification"]
        critical_failures = [r for r in self.test_results if not r["success"] and r["test"] in critical_tests]
        
        if critical_failures:
            print("🔴 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['message']}")
            print()
            print("❌ PROFILE ENDPOINTS HAVE CRITICAL ISSUES")
            return False
        elif failed_tests == 0:
            print("✅ ALL TESTS PASSED - PROFILE ENDPOINTS WORKING PERFECTLY")
            return True
        else:
            print("⚠️  MINOR ISSUES FOUND BUT CORE FUNCTIONALITY WORKING")
            return True

def main():
    """Main test execution"""
    tester = ProfileEndpointsTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()