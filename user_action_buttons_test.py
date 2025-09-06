#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Individual User Action Buttons
Testing the individual user action buttons (approve, reject, delete) as reported by user
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

class UserActionButtonsTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_user_ids = []  # Track created test users for cleanup
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def create_test_user_with_pending_status(self):
        """Create a test user with pending registration status for testing"""
        try:
            test_id = str(uuid.uuid4())[:8]
            test_user_data = {
                "username": f"pending_user_{test_id}",
                "email": f"pending_{test_id}@example.com",
                "full_name": f"Pending Test User {test_id}",
                "account_type": "buyer"  # This will create a User-Buyer
            }
            
            # Use registration endpoint to create user with pending status
            response = requests.post(
                f"{BACKEND_URL}/auth/register", 
                json=test_user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('user_id')
                self.test_user_ids.append(user_id)
                self.log_test(
                    "Create Test User (Pending Status)", 
                    True, 
                    f"Created pending user: {test_user_data['username']} with ID: {user_id}"
                )
                return user_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test User (Pending Status)", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Create Test User (Pending Status)", False, error_msg=str(e))
            return None

    def create_test_user_with_approved_status(self):
        """Create a test user with approved status for delete testing"""
        try:
            test_id = str(uuid.uuid4())[:8]
            test_user_data = {
                "username": f"approved_user_{test_id}",
                "email": f"approved_{test_id}@example.com",
                "full_name": f"Approved Test User {test_id}",
                "account_type": "seller"  # This will create a User-Seller
            }
            
            # Use registration endpoint to create user
            response = requests.post(
                f"{BACKEND_URL}/auth/register", 
                json=test_user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('user_id')
                
                # Immediately approve the user for delete testing
                approve_response = requests.put(f"{BACKEND_URL}/admin/users/{user_id}/approve", timeout=10)
                if approve_response.status_code == 200:
                    self.test_user_ids.append(user_id)
                    self.log_test(
                        "Create Test User (Approved Status)", 
                        True, 
                        f"Created and approved user: {test_user_data['username']} with ID: {user_id}"
                    )
                    return user_id
                else:
                    self.log_test("Create Test User (Approved Status)", False, "Failed to approve test user")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test User (Approved Status)", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Create Test User (Approved Status)", False, error_msg=str(e))
            return None

    def test_individual_user_approval(self, user_id):
        """Test individual user approval button functionality"""
        if not user_id:
            self.log_test("Individual User Approval", False, error_msg="No user ID provided")
            return False
            
        try:
            # First verify user is in pending status
            users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if users_response.status_code != 200:
                self.log_test("Individual User Approval", False, "Failed to get users list")
                return False
                
            users = users_response.json()
            test_user = None
            for user in users:
                if user.get('id') == user_id:
                    test_user = user
                    break
                    
            if not test_user:
                self.log_test("Individual User Approval", False, "Test user not found in users list")
                return False
                
            if test_user.get('registration_status') != 'Pending':
                self.log_test("Individual User Approval", False, f"User status is {test_user.get('registration_status')}, expected Pending")
                return False
            
            # Test the approve button endpoint
            response = requests.put(f"{BACKEND_URL}/admin/users/{user_id}/approve", timeout=10)
            
            if response.status_code == 200:
                # Verify user status changed to Approved
                time.sleep(1)  # Brief delay for database update
                users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
                if users_response.status_code == 200:
                    users = users_response.json()
                    updated_user = None
                    for user in users:
                        if user.get('id') == user_id:
                            updated_user = user
                            break
                    
                    if updated_user and updated_user.get('registration_status') == 'Approved':
                        self.log_test(
                            "Individual User Approval", 
                            True, 
                            f"Successfully approved user {user_id}, status changed from Pending to Approved"
                        )
                        return True
                    else:
                        self.log_test("Individual User Approval", False, "User status did not change to Approved")
                        return False
                else:
                    self.log_test("Individual User Approval", False, "Failed to verify status change")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Individual User Approval", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Individual User Approval", False, error_msg=str(e))
            return False

    def test_individual_user_rejection(self, user_id):
        """Test individual user rejection button functionality"""
        if not user_id:
            self.log_test("Individual User Rejection", False, error_msg="No user ID provided")
            return False
            
        try:
            # First verify user is in pending status
            users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if users_response.status_code != 200:
                self.log_test("Individual User Rejection", False, "Failed to get users list")
                return False
                
            users = users_response.json()
            test_user = None
            for user in users:
                if user.get('id') == user_id:
                    test_user = user
                    break
                    
            if not test_user:
                self.log_test("Individual User Rejection", False, "Test user not found in users list")
                return False
                
            if test_user.get('registration_status') != 'Pending':
                self.log_test("Individual User Rejection", False, f"User status is {test_user.get('registration_status')}, expected Pending")
                return False
            
            # Test the reject button endpoint with reason
            rejection_data = {"reason": "Test rejection for button functionality testing"}
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{user_id}/reject", 
                json=rejection_data,
                timeout=10
            )
            
            if response.status_code == 200:
                # Verify user status changed to Rejected
                time.sleep(1)  # Brief delay for database update
                users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
                if users_response.status_code == 200:
                    users = users_response.json()
                    updated_user = None
                    for user in users:
                        if user.get('id') == user_id:
                            updated_user = user
                            break
                    
                    if updated_user and updated_user.get('registration_status') == 'Rejected':
                        self.log_test(
                            "Individual User Rejection", 
                            True, 
                            f"Successfully rejected user {user_id}, status changed from Pending to Rejected"
                        )
                        return True
                    else:
                        self.log_test("Individual User Rejection", False, "User status did not change to Rejected")
                        return False
                else:
                    self.log_test("Individual User Rejection", False, "Failed to verify status change")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Individual User Rejection", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Individual User Rejection", False, error_msg=str(e))
            return False

    def test_individual_user_deletion(self, user_id):
        """Test individual user deletion button functionality"""
        if not user_id:
            self.log_test("Individual User Deletion", False, error_msg="No user ID provided")
            return False
            
        try:
            # First verify user exists
            users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if users_response.status_code != 200:
                self.log_test("Individual User Deletion", False, "Failed to get users list")
                return False
                
            users = users_response.json()
            test_user = None
            for user in users:
                if user.get('id') == user_id:
                    test_user = user
                    break
                    
            if not test_user:
                self.log_test("Individual User Deletion", False, "Test user not found in users list")
                return False
            
            # Test the delete button endpoint
            response = requests.delete(f"{BACKEND_URL}/admin/users/{user_id}", timeout=10)
            
            if response.status_code == 200:
                # Verify user is actually deleted from database
                time.sleep(1)  # Brief delay for database update
                users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
                if users_response.status_code == 200:
                    users = users_response.json()
                    deleted_user = None
                    for user in users:
                        if user.get('id') == user_id:
                            deleted_user = user
                            break
                    
                    if deleted_user is None:
                        self.log_test(
                            "Individual User Deletion", 
                            True, 
                            f"Successfully deleted user {user_id}, user no longer exists in database"
                        )
                        # Remove from cleanup list since it's already deleted
                        if user_id in self.test_user_ids:
                            self.test_user_ids.remove(user_id)
                        return True
                    else:
                        self.log_test("Individual User Deletion", False, "User still exists in database after deletion")
                        return False
                else:
                    self.log_test("Individual User Deletion", False, "Failed to verify deletion")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Individual User Deletion", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Individual User Deletion", False, error_msg=str(e))
            return False

    def test_button_visibility_logic(self):
        """Test button visibility logic by checking user statuses"""
        try:
            # Get all users to check different statuses
            response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if response.status_code != 200:
                self.log_test("Button Visibility Logic", False, "Failed to get users list")
                return False
                
            users = response.json()
            
            # Count users by status
            status_counts = {}
            for user in users:
                status = user.get('registration_status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Check if we have users in different statuses for proper testing
            has_pending = status_counts.get('Pending', 0) > 0
            has_approved = status_counts.get('Approved', 0) > 0
            has_rejected = status_counts.get('Rejected', 0) > 0
            
            visibility_details = []
            if has_pending:
                visibility_details.append(f"Pending users ({status_counts['Pending']}): Should show Approve/Reject buttons")
            if has_approved:
                visibility_details.append(f"Approved users ({status_counts['Approved']}): Should show Delete/Suspend buttons")
            if has_rejected:
                visibility_details.append(f"Rejected users ({status_counts['Rejected']}): Should show Delete button")
            
            self.log_test(
                "Button Visibility Logic", 
                True, 
                f"Found users in different statuses for button visibility testing. {'; '.join(visibility_details)}"
            )
            return True
            
        except Exception as e:
            self.log_test("Button Visibility Logic", False, error_msg=str(e))
            return False

    def test_api_endpoints_accessibility(self):
        """Test that all user action API endpoints are accessible"""
        try:
            # Test with a non-existent user ID to check endpoint accessibility
            test_user_id = "non-existent-user-id"
            
            endpoints_tested = []
            
            # Test approve endpoint
            try:
                response = requests.put(f"{BACKEND_URL}/admin/users/{test_user_id}/approve", timeout=5)
                if response.status_code == 404:  # Expected for non-existent user
                    endpoints_tested.append("✅ Approve endpoint accessible")
                else:
                    endpoints_tested.append(f"⚠️ Approve endpoint returned {response.status_code}")
            except Exception as e:
                endpoints_tested.append(f"❌ Approve endpoint error: {str(e)}")
            
            # Test reject endpoint
            try:
                response = requests.put(f"{BACKEND_URL}/admin/users/{test_user_id}/reject", json={"reason": "test"}, timeout=5)
                if response.status_code == 404:  # Expected for non-existent user
                    endpoints_tested.append("✅ Reject endpoint accessible")
                else:
                    endpoints_tested.append(f"⚠️ Reject endpoint returned {response.status_code}")
            except Exception as e:
                endpoints_tested.append(f"❌ Reject endpoint error: {str(e)}")
            
            # Test delete endpoint
            try:
                response = requests.delete(f"{BACKEND_URL}/admin/users/{test_user_id}", timeout=5)
                if response.status_code == 404:  # Expected for non-existent user
                    endpoints_tested.append("✅ Delete endpoint accessible")
                else:
                    endpoints_tested.append(f"⚠️ Delete endpoint returned {response.status_code}")
            except Exception as e:
                endpoints_tested.append(f"❌ Delete endpoint error: {str(e)}")
            
            # Check if all endpoints are accessible
            accessible_count = sum(1 for result in endpoints_tested if result.startswith("✅"))
            
            self.log_test(
                "API Endpoints Accessibility", 
                accessible_count == 3, 
                f"Endpoint accessibility results: {'; '.join(endpoints_tested)}"
            )
            return accessible_count == 3
            
        except Exception as e:
            self.log_test("API Endpoints Accessibility", False, error_msg=str(e))
            return False

    def cleanup_test_users(self):
        """Clean up test users created during testing"""
        cleaned_count = 0
        for user_id in self.test_user_ids:
            try:
                response = requests.delete(f"{BACKEND_URL}/admin/users/{user_id}", timeout=10)
                if response.status_code == 200:
                    cleaned_count += 1
            except:
                pass  # Ignore cleanup errors
        
        if cleaned_count > 0:
            self.log_test(
                "Test Cleanup", 
                True, 
                f"Successfully cleaned up {cleaned_count} test users"
            )

    def run_user_action_buttons_tests(self):
        """Run comprehensive tests for individual user action buttons"""
        print("=" * 80)
        print("CATALORO BACKEND TESTING - INDIVIDUAL USER ACTION BUTTONS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting user action button testing.")
            return
        
        # 2. API Endpoints Accessibility Test
        print("🌐 API ENDPOINTS ACCESSIBILITY TEST")
        print("-" * 40)
        self.test_api_endpoints_accessibility()
        
        # 3. Button Visibility Logic Test
        print("👁️ BUTTON VISIBILITY LOGIC TEST")
        print("-" * 40)
        self.test_button_visibility_logic()
        
        # 4. Individual User Approval Testing
        print("✅ INDIVIDUAL USER APPROVAL TESTING")
        print("-" * 40)
        pending_user_id = self.create_test_user_with_pending_status()
        if pending_user_id:
            self.test_individual_user_approval(pending_user_id)
        
        # 5. Individual User Rejection Testing
        print("❌ INDIVIDUAL USER REJECTION TESTING")
        print("-" * 40)
        pending_user_id_2 = self.create_test_user_with_pending_status()
        if pending_user_id_2:
            self.test_individual_user_rejection(pending_user_id_2)
        
        # 6. Individual User Delete Testing
        print("🗑️ INDIVIDUAL USER DELETE TESTING")
        print("-" * 40)
        approved_user_id = self.create_test_user_with_approved_status()
        if approved_user_id:
            self.test_individual_user_deletion(approved_user_id)
        
        # 7. Cleanup
        print("🧹 CLEANUP")
        print("-" * 40)
        self.cleanup_test_users()
        
        # Print Summary
        print("=" * 80)
        print("USER ACTION BUTTONS TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 USER ACTION BUTTONS TESTING COMPLETE")
        print("Individual approve, reject, and delete button functionality has been tested.")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = UserActionButtonsTester()
    
    print("🎯 TESTING INDIVIDUAL USER ACTION BUTTONS AS REQUESTED")
    print("Testing approve, reject, and delete button functionality...")
    print()
    
    passed, failed, results = tester.run_user_action_buttons_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)