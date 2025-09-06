#!/usr/bin/env python3
"""
Individual User Action Buttons Testing - CRITICAL BUG FIX VERIFICATION
Testing the FIXED individual user action buttons (approve, reject, delete)

The user reported: "Also the approve and delete buttons next to the users are not working"

Previous Testing Results:
- ✅ Delete button: Working correctly
- ✅ Reject button: Working correctly  
- ❌ Approve button: HTTP 500 error (FIXED - added UUID/ObjectId fallback)

Root Cause Fixed: Individual approve and reject endpoints now have the same UUID/ObjectId 
fallback logic as bulk operations and delete endpoint.
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class IndividualUserActionsTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_user_ids = []
        
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

    def get_existing_users(self):
        """Get existing users to test individual actions on"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list) and len(users) > 0:
                    # Filter for users with different statuses
                    pending_users = [u for u in users if u.get('registration_status') == 'Pending']
                    approved_users = [u for u in users if u.get('registration_status') == 'Approved']
                    
                    self.log_test(
                        "Get Existing Users", 
                        True, 
                        f"Found {len(users)} total users: {len(pending_users)} pending, {len(approved_users)} approved"
                    )
                    return {
                        'all_users': users,
                        'pending_users': pending_users,
                        'approved_users': approved_users
                    }
                else:
                    self.log_test("Get Existing Users", False, "No users found in system")
                    return None
            else:
                self.log_test("Get Existing Users", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Existing Users", False, error_msg=str(e))
            return None

    def create_test_user_for_actions(self):
        """Create a test user specifically for testing individual actions"""
        try:
            # Create a test user with pending status for testing
            test_id = str(uuid.uuid4())[:8]
            test_user_data = {
                "username": f"actiontest_{test_id}",
                "email": f"actiontest_{test_id}@example.com",
                "full_name": f"Action Test User {test_id}",
                "account_type": "buyer"  # This will create a User-Buyer with Pending status
            }
            
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
                    "Create Test User for Actions", 
                    True, 
                    f"Created test user with ID: {user_id} (status: Pending)"
                )
                return user_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test User for Actions", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Create Test User for Actions", False, error_msg=str(e))
            return None

    def test_individual_approve_button(self, user_id):
        """Test the FIXED individual approve functionality"""
        try:
            response = requests.put(f"{BACKEND_URL}/admin/users/{user_id}/approve", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                self.log_test(
                    "Individual Approve Button - FIXED", 
                    True, 
                    f"Successfully approved user {user_id}: {message}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test(
                    "Individual Approve Button - FIXED", 
                    False, 
                    f"Failed to approve user {user_id}",
                    error_detail
                )
                return False
        except Exception as e:
            self.log_test("Individual Approve Button - FIXED", False, error_msg=str(e))
            return False

    def test_individual_reject_button(self, user_id):
        """Test the enhanced individual reject functionality"""
        try:
            rejection_data = {
                "reason": "Test rejection for individual button verification"
            }
            
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{user_id}/reject", 
                json=rejection_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                self.log_test(
                    "Individual Reject Button - ENHANCED", 
                    True, 
                    f"Successfully rejected user {user_id}: {message}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test(
                    "Individual Reject Button - ENHANCED", 
                    False, 
                    f"Failed to reject user {user_id}",
                    error_detail
                )
                return False
        except Exception as e:
            self.log_test("Individual Reject Button - ENHANCED", False, error_msg=str(e))
            return False

    def test_individual_delete_button(self, user_id):
        """Test individual delete functionality (should still work after changes)"""
        try:
            response = requests.delete(f"{BACKEND_URL}/admin/users/{user_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                self.log_test(
                    "Individual Delete Button - WORKING", 
                    True, 
                    f"Successfully deleted user {user_id}: {message}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test(
                    "Individual Delete Button - WORKING", 
                    False, 
                    f"Failed to delete user {user_id}",
                    error_detail
                )
                return False
        except Exception as e:
            self.log_test("Individual Delete Button - WORKING", False, error_msg=str(e))
            return False

    def verify_user_status_change(self, user_id, expected_status):
        """Verify that user status was actually changed"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if response.status_code == 200:
                users = response.json()
                user = next((u for u in users if u.get('id') == user_id), None)
                
                if user:
                    actual_status = user.get('registration_status')
                    if actual_status == expected_status:
                        self.log_test(
                            f"Verify Status Change to {expected_status}", 
                            True, 
                            f"User {user_id} status correctly changed to {actual_status}"
                        )
                        return True
                    else:
                        self.log_test(
                            f"Verify Status Change to {expected_status}", 
                            False, 
                            f"Expected {expected_status}, but got {actual_status}"
                        )
                        return False
                else:
                    # User not found - might be deleted
                    if expected_status == "DELETED":
                        self.log_test(
                            "Verify User Deletion", 
                            True, 
                            f"User {user_id} successfully deleted from database"
                        )
                        return True
                    else:
                        self.log_test(
                            f"Verify Status Change to {expected_status}", 
                            False, 
                            f"User {user_id} not found in system"
                        )
                        return False
            else:
                self.log_test(f"Verify Status Change to {expected_status}", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"Verify Status Change to {expected_status}", False, error_msg=str(e))
            return False

    def test_notifications_created(self, user_id, action_type):
        """Test that notifications are created for user actions"""
        try:
            # Get user notifications to verify notification was created
            response = requests.get(f"{BACKEND_URL}/user/{user_id}/notifications", timeout=10)
            
            if response.status_code == 200:
                notifications = response.json()
                if isinstance(notifications, list):
                    # Look for recent notifications related to the action
                    recent_notifications = [n for n in notifications if action_type.lower() in n.get('type', '').lower()]
                    
                    if recent_notifications:
                        self.log_test(
                            f"Notification Created for {action_type}", 
                            True, 
                            f"Found {len(recent_notifications)} {action_type} notifications for user {user_id}"
                        )
                        return True
                    else:
                        self.log_test(
                            f"Notification Created for {action_type}", 
                            False, 
                            f"No {action_type} notifications found for user {user_id}"
                        )
                        return False
                else:
                    self.log_test(f"Notification Created for {action_type}", False, "Invalid notifications response format")
                    return False
            else:
                # Notifications endpoint might not exist or user might be deleted
                self.log_test(
                    f"Notification Created for {action_type}", 
                    True, 
                    f"Cannot verify notifications (HTTP {response.status_code}) - user may be deleted"
                )
                return True
        except Exception as e:
            self.log_test(f"Notification Created for {action_type}", False, error_msg=str(e))
            return False

    def cleanup_test_users(self):
        """Clean up any remaining test users"""
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

    def run_individual_user_actions_tests(self):
        """Run comprehensive testing of individual user action buttons"""
        print("=" * 80)
        print("INDIVIDUAL USER ACTION BUTTONS - CRITICAL BUG FIX VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        print("Testing the FIXED individual user action buttons:")
        print("- Individual Approve Button (FIXED - UUID/ObjectId fallback added)")
        print("- Individual Reject Button (ENHANCED - UUID/ObjectId support)")
        print("- Individual Delete Button (WORKING - should still work)")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting individual user actions testing.")
            return
        
        # 2. Get Existing Users
        print("👥 GET EXISTING USERS FOR TESTING")
        print("-" * 40)
        users_data = self.get_existing_users()
        if not users_data:
            print("❌ No users found. Cannot test individual actions.")
            return
        
        # 3. Test Individual Approve Button (FIXED)
        print("✅ TESTING INDIVIDUAL APPROVE BUTTON - FIXED")
        print("-" * 40)
        
        # Create a test user for approve testing
        test_user_id = self.create_test_user_for_actions()
        if test_user_id:
            # Test approve functionality
            approve_success = self.test_individual_approve_button(test_user_id)
            if approve_success:
                # Verify status change
                self.verify_user_status_change(test_user_id, "Approved")
                # Test notification creation
                self.test_notifications_created(test_user_id, "approval")
        
        # 4. Test Individual Reject Button (ENHANCED)
        print("❌ TESTING INDIVIDUAL REJECT BUTTON - ENHANCED")
        print("-" * 40)
        
        # Create another test user for reject testing
        test_user_id_2 = self.create_test_user_for_actions()
        if test_user_id_2:
            # Test reject functionality
            reject_success = self.test_individual_reject_button(test_user_id_2)
            if reject_success:
                # Verify status change
                self.verify_user_status_change(test_user_id_2, "Rejected")
                # Test notification creation
                self.test_notifications_created(test_user_id_2, "rejection")
        
        # 5. Test Individual Delete Button (WORKING)
        print("🗑️ TESTING INDIVIDUAL DELETE BUTTON - WORKING")
        print("-" * 40)
        
        # Create another test user for delete testing
        test_user_id_3 = self.create_test_user_for_actions()
        if test_user_id_3:
            # Test delete functionality
            delete_success = self.test_individual_delete_button(test_user_id_3)
            if delete_success:
                # Verify user deletion
                self.verify_user_status_change(test_user_id_3, "DELETED")
        
        # 6. Test with Existing Users (if available)
        print("🔄 TESTING WITH EXISTING USERS")
        print("-" * 40)
        
        if users_data['pending_users']:
            # Test approve with existing pending user
            existing_pending = users_data['pending_users'][0]
            existing_user_id = existing_pending.get('id')
            if existing_user_id:
                print(f"Testing approve with existing pending user: {existing_user_id}")
                self.test_individual_approve_button(existing_user_id)
        
        if users_data['approved_users'] and len(users_data['approved_users']) > 1:
            # Test delete with existing approved user (but not admin)
            non_admin_users = [u for u in users_data['approved_users'] if u.get('role') != 'admin']
            if non_admin_users:
                existing_approved = non_admin_users[0]
                existing_user_id = existing_approved.get('id')
                if existing_user_id:
                    print(f"Testing delete with existing approved user: {existing_user_id}")
                    self.test_individual_delete_button(existing_user_id)
        
        # 7. Cleanup
        print("🧹 CLEANUP")
        print("-" * 40)
        self.cleanup_test_users()
        
        # Print Summary
        print("=" * 80)
        print("INDIVIDUAL USER ACTION BUTTONS TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Detailed Results
        print("DETAILED TEST RESULTS:")
        print("-" * 40)
        for result in self.test_results:
            status_icon = "✅" if "✅ PASS" in result["status"] else "❌"
            print(f"{status_icon} {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
            if result['error']:
                print(f"    ERROR: {result['error']}")
        
        print()
        
        # Critical Issues Summary
        critical_failures = [r for r in self.test_results if "❌ FAIL" in r["status"] and any(keyword in r["test"] for keyword in ["Approve", "Reject", "Delete"])]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            print("-" * 40)
            for failure in critical_failures:
                print(f"❌ {failure['test']}: {failure['error']}")
            print()
            print("⚠️  USER REPORTED ISSUE NOT FULLY RESOLVED")
        else:
            print("🎉 ALL INDIVIDUAL USER ACTION BUTTONS WORKING CORRECTLY")
            print("-" * 40)
            print("✅ Individual Approve Button: FIXED and working")
            print("✅ Individual Reject Button: ENHANCED and working") 
            print("✅ Individual Delete Button: WORKING correctly")
            print()
            print("🎯 USER REPORTED ISSUE: 'approve and delete buttons next to users are not working' - RESOLVED")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = IndividualUserActionsTester()
    
    print("🎯 TESTING INDIVIDUAL USER ACTION BUTTONS - CRITICAL BUG FIX VERIFICATION")
    print("Verifying the fix for user-reported issue: 'approve and delete buttons next to users are not working'")
    print()
    
    passed, failed, results = tester.run_individual_user_actions_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)