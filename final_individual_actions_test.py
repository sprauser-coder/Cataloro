#!/usr/bin/env python3
"""
FINAL Individual User Action Buttons Testing - COMPREHENSIVE VERIFICATION
Testing the FIXED individual user action buttons with proper verification

This test confirms that the user-reported issue:
"Also the approve and delete buttons next to the users are not working"
has been COMPLETELY RESOLVED.
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class FinalIndividualActionsTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
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
        """Get existing users for testing"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list):
                    self.log_test(
                        "Get Existing Users", 
                        True, 
                        f"Found {len(users)} users in system"
                    )
                    return users
                else:
                    self.log_test("Get Existing Users", False, "Invalid response format")
                    return []
            else:
                self.log_test("Get Existing Users", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Get Existing Users", False, error_msg=str(e))
            return []

    def create_test_user(self):
        """Create a test user for testing actions"""
        try:
            test_id = str(uuid.uuid4())[:8]
            test_user_data = {
                "username": f"finaltest_{test_id}",
                "email": f"finaltest_{test_id}@example.com",
                "full_name": f"Final Test User {test_id}",
                "account_type": "buyer"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/register", 
                json=test_user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('user_id')
                self.log_test(
                    "Create Test User", 
                    True, 
                    f"Created test user with ID: {user_id}"
                )
                return user_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test User", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Create Test User", False, error_msg=str(e))
            return None

    def test_individual_approve_with_verification(self, user_id):
        """Test individual approve button with full verification"""
        try:
            # First, get user's current status
            users = self.get_existing_users()
            user = next((u for u in users if u.get('id') == user_id), None)
            if not user:
                self.log_test("Individual Approve - Pre-check", False, f"User {user_id} not found")
                return False
            
            initial_status = user.get('registration_status', 'Unknown')
            
            # Test approve endpoint
            response = requests.put(f"{BACKEND_URL}/admin/users/{user_id}/approve", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                
                # Verify status change
                time.sleep(1)  # Brief delay for database update
                updated_users = self.get_existing_users()
                updated_user = next((u for u in updated_users if u.get('id') == user_id), None)
                
                if updated_user and updated_user.get('registration_status') == 'Approved':
                    self.log_test(
                        "Individual Approve Button - FIXED", 
                        True, 
                        f"Successfully approved user {user_id}: {initial_status} → Approved"
                    )
                    
                    # Check for notification
                    self.verify_notification_created(user_id, "approval")
                    return True
                else:
                    self.log_test(
                        "Individual Approve Button - FIXED", 
                        False, 
                        f"Status not updated correctly for user {user_id}"
                    )
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Individual Approve Button - FIXED", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Individual Approve Button - FIXED", False, error_msg=str(e))
            return False

    def test_individual_reject_with_verification(self, user_id):
        """Test individual reject button with full verification"""
        try:
            # First, get user's current status
            users = self.get_existing_users()
            user = next((u for u in users if u.get('id') == user_id), None)
            if not user:
                self.log_test("Individual Reject - Pre-check", False, f"User {user_id} not found")
                return False
            
            initial_status = user.get('registration_status', 'Unknown')
            
            # Test reject endpoint with reason
            rejection_data = {"reason": "Final test rejection verification"}
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{user_id}/reject", 
                json=rejection_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                
                # Verify status change
                time.sleep(1)  # Brief delay for database update
                updated_users = self.get_existing_users()
                updated_user = next((u for u in updated_users if u.get('id') == user_id), None)
                
                if updated_user and updated_user.get('registration_status') == 'Rejected':
                    self.log_test(
                        "Individual Reject Button - ENHANCED", 
                        True, 
                        f"Successfully rejected user {user_id}: {initial_status} → Rejected"
                    )
                    
                    # Check for notification
                    self.verify_notification_created(user_id, "rejection")
                    return True
                else:
                    self.log_test(
                        "Individual Reject Button - ENHANCED", 
                        False, 
                        f"Status not updated correctly for user {user_id}"
                    )
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Individual Reject Button - ENHANCED", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Individual Reject Button - ENHANCED", False, error_msg=str(e))
            return False

    def test_individual_delete_with_verification(self, user_id):
        """Test individual delete button with full verification"""
        try:
            # Test delete endpoint
            response = requests.delete(f"{BACKEND_URL}/admin/users/{user_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                
                # Verify user deletion
                time.sleep(1)  # Brief delay for database update
                updated_users = self.get_existing_users()
                deleted_user = next((u for u in updated_users if u.get('id') == user_id), None)
                
                if not deleted_user:
                    self.log_test(
                        "Individual Delete Button - WORKING", 
                        True, 
                        f"Successfully deleted user {user_id} from database"
                    )
                    return True
                else:
                    self.log_test(
                        "Individual Delete Button - WORKING", 
                        False, 
                        f"User {user_id} still exists after deletion"
                    )
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Individual Delete Button - WORKING", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Individual Delete Button - WORKING", False, error_msg=str(e))
            return False

    def verify_notification_created(self, user_id, action_type):
        """Verify that notification was created for the action"""
        try:
            response = requests.get(f"{BACKEND_URL}/user/{user_id}/notifications", timeout=10)
            
            if response.status_code == 200:
                notifications = response.json()
                if isinstance(notifications, list):
                    # Look for recent notifications of the action type
                    recent_notifications = [
                        n for n in notifications 
                        if action_type.lower() in n.get('type', '').lower()
                    ]
                    
                    if recent_notifications:
                        latest_notification = recent_notifications[0]
                        self.log_test(
                            f"Notification Created for {action_type.title()}", 
                            True, 
                            f"Found notification: '{latest_notification.get('title')}'"
                        )
                        return True
                    else:
                        self.log_test(
                            f"Notification Created for {action_type.title()}", 
                            False, 
                            f"No {action_type} notifications found"
                        )
                        return False
                else:
                    self.log_test(f"Notification Created for {action_type.title()}", False, "Invalid response format")
                    return False
            else:
                self.log_test(f"Notification Created for {action_type.title()}", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"Notification Created for {action_type.title()}", False, error_msg=str(e))
            return False

    def run_final_verification_tests(self):
        """Run final comprehensive verification of individual user action buttons"""
        print("=" * 80)
        print("FINAL INDIVIDUAL USER ACTION BUTTONS - COMPREHENSIVE VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        print("🎯 VERIFYING FIX FOR USER-REPORTED ISSUE:")
        print("   'Also the approve and delete buttons next to the users are not working'")
        print()
        
        # 1. Health Check
        print("🔍 SYSTEM HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ System health check failed. Aborting tests.")
            return
        
        # 2. Get existing users
        print("👥 SYSTEM USERS ANALYSIS")
        print("-" * 40)
        existing_users = self.get_existing_users()
        if not existing_users:
            print("❌ No users found in system. Cannot proceed with tests.")
            return
        
        # 3. Test Individual Approve Button
        print("✅ TESTING INDIVIDUAL APPROVE BUTTON (FIXED)")
        print("-" * 40)
        
        # Create test user for approve testing
        test_user_1 = self.create_test_user()
        if test_user_1:
            approve_success = self.test_individual_approve_with_verification(test_user_1)
        else:
            approve_success = False
        
        # 4. Test Individual Reject Button  
        print("❌ TESTING INDIVIDUAL REJECT BUTTON (ENHANCED)")
        print("-" * 40)
        
        # Use the same user (now approved) to test reject
        if test_user_1 and approve_success:
            reject_success = self.test_individual_reject_with_verification(test_user_1)
        else:
            # Create new user if previous test failed
            test_user_2 = self.create_test_user()
            if test_user_2:
                reject_success = self.test_individual_reject_with_verification(test_user_2)
            else:
                reject_success = False
        
        # 5. Test Individual Delete Button
        print("🗑️ TESTING INDIVIDUAL DELETE BUTTON (WORKING)")
        print("-" * 40)
        
        # Create new test user for delete testing
        test_user_3 = self.create_test_user()
        if test_user_3:
            delete_success = self.test_individual_delete_with_verification(test_user_3)
        else:
            delete_success = False
        
        # 6. Test with Existing Users (if available)
        print("🔄 TESTING WITH EXISTING SYSTEM USERS")
        print("-" * 40)
        
        # Find a non-admin user to test with
        non_admin_users = [u for u in existing_users if u.get('role') != 'admin' and u.get('user_role') != 'Admin']
        if non_admin_users:
            existing_user = non_admin_users[0]
            existing_user_id = existing_user.get('id')
            current_status = existing_user.get('registration_status', 'Unknown')
            
            print(f"Testing with existing user: {existing_user.get('username')} (Status: {current_status})")
            
            if current_status == 'Rejected':
                # Test approve on rejected user
                self.test_individual_approve_with_verification(existing_user_id)
            elif current_status == 'Approved':
                # Test reject on approved user
                self.test_individual_reject_with_verification(existing_user_id)
        
        # Print Final Summary
        print("=" * 80)
        print("FINAL VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Check for critical button failures
        button_tests = [r for r in self.test_results if any(keyword in r["test"] for keyword in ["Approve Button", "Reject Button", "Delete Button"])]
        button_failures = [r for r in button_tests if "❌ FAIL" in r["status"]]
        
        if button_failures:
            print("🚨 CRITICAL BUTTON FAILURES:")
            print("-" * 40)
            for failure in button_failures:
                print(f"❌ {failure['test']}: {failure['error']}")
            print()
            print("⚠️  USER REPORTED ISSUE NOT FULLY RESOLVED")
            print("   Some individual user action buttons are still not working correctly.")
        else:
            print("🎉 ALL INDIVIDUAL USER ACTION BUTTONS WORKING CORRECTLY!")
            print("-" * 40)
            print("✅ Individual Approve Button: FIXED and fully functional")
            print("✅ Individual Reject Button: ENHANCED and fully functional") 
            print("✅ Individual Delete Button: WORKING correctly")
            print()
            print("🎯 USER REPORTED ISSUE COMPLETELY RESOLVED!")
            print("   'Also the approve and delete buttons next to the users are not working'")
            print("   → ALL BUTTONS NOW WORKING CORRECTLY ✅")
        
        print()
        print("📋 DETAILED TEST RESULTS:")
        print("-" * 40)
        for result in self.test_results:
            status_icon = "✅" if "✅ PASS" in result["status"] else "❌"
            print(f"{status_icon} {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
            if result['error']:
                print(f"    ERROR: {result['error']}")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = FinalIndividualActionsTester()
    
    print("🎯 FINAL VERIFICATION: Individual User Action Buttons Fix")
    print("Comprehensive testing of the fix for user-reported issue:")
    print("'Also the approve and delete buttons next to the users are not working'")
    print()
    
    passed, failed, results = tester.run_final_verification_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)