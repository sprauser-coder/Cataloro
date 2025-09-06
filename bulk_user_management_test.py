#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Bulk User Management Focus
Testing the newly implemented bulk user management functionality
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

class BulkUserManagementTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.created_user_ids = []
        
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
                    f"Status: {data.get('status')}, App: {data.get('app')}, Version: {data.get('version')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def create_test_users(self, count=5):
        """Create test users for bulk operations"""
        created_users = []
        
        for i in range(count):
            try:
                test_id = str(uuid.uuid4())[:8]
                user_data = {
                    "username": f"bulktest_{test_id}",
                    "email": f"bulktest_{test_id}@example.com",
                    "full_name": f"Bulk Test User {i+1}",
                    "password": "TestPassword123!",
                    "role": "user"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/admin/users", 
                    json=user_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    user = data.get('user', {})
                    user_id = user.get('id')
                    if user_id:
                        created_users.append(user_id)
                        self.created_user_ids.append(user_id)
                        
            except Exception as e:
                print(f"Error creating test user {i+1}: {e}")
                
        self.log_test(
            "Create Test Users for Bulk Operations", 
            len(created_users) > 0, 
            f"Created {len(created_users)} test users for bulk testing"
        )
        return created_users

    def test_bulk_delete_operation(self, user_ids):
        """Test bulk delete operation"""
        if len(user_ids) < 2:
            self.log_test("Bulk Delete Operation", False, error_msg="Need at least 2 users for bulk delete test")
            return False
            
        try:
            # Use first 2 users for delete test
            delete_user_ids = user_ids[:2]
            
            bulk_data = {
                "action": "delete",
                "user_ids": delete_user_ids
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/bulk-action",
                json=bulk_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {})
                success_count = results.get('success_count', 0)
                failed_count = results.get('failed_count', 0)
                errors = results.get('errors', [])
                
                # Verify users are actually deleted
                deleted_count = 0
                for user_id in delete_user_ids:
                    try:
                        check_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=5)
                        if check_response.status_code == 200:
                            all_users = check_response.json()
                            user_exists = any(user.get('id') == user_id for user in all_users)
                            if not user_exists:
                                deleted_count += 1
                    except:
                        pass
                
                self.log_test(
                    "Bulk Delete Operation", 
                    success_count == len(delete_user_ids) and deleted_count == len(delete_user_ids),
                    f"Deleted {success_count}/{len(delete_user_ids)} users successfully. Verified {deleted_count} users removed from database. Errors: {len(errors)}"
                )
                
                # Remove deleted users from our tracking list
                for user_id in delete_user_ids:
                    if user_id in self.created_user_ids:
                        self.created_user_ids.remove(user_id)
                        
                return success_count == len(delete_user_ids)
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Bulk Delete Operation", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Bulk Delete Operation", False, error_msg=str(e))
            return False

    def test_bulk_activate_operation(self, user_ids):
        """Test bulk activate operation"""
        if len(user_ids) < 2:
            self.log_test("Bulk Activate Operation", False, error_msg="Need at least 2 users for bulk activate test")
            return False
            
        try:
            # Use next 2 users for activate test
            activate_user_ids = user_ids[:2]
            
            # First deactivate them to test activation
            for user_id in activate_user_ids:
                requests.put(
                    f"{BACKEND_URL}/admin/users/{user_id}",
                    json={"is_active": False},
                    timeout=5
                )
            
            bulk_data = {
                "action": "activate",
                "user_ids": activate_user_ids
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/bulk-action",
                json=bulk_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {})
                success_count = results.get('success_count', 0)
                failed_count = results.get('failed_count', 0)
                errors = results.get('errors', [])
                
                # Verify users are actually activated
                activated_count = 0
                try:
                    check_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=5)
                    if check_response.status_code == 200:
                        all_users = check_response.json()
                        for user_id in activate_user_ids:
                            user = next((u for u in all_users if u.get('id') == user_id), None)
                            if user and user.get('is_active', False):
                                activated_count += 1
                except:
                    pass
                
                self.log_test(
                    "Bulk Activate Operation", 
                    success_count == len(activate_user_ids),
                    f"Activated {success_count}/{len(activate_user_ids)} users successfully. Verified {activated_count} users are active. Errors: {len(errors)}"
                )
                return success_count == len(activate_user_ids)
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Bulk Activate Operation", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Bulk Activate Operation", False, error_msg=str(e))
            return False

    def test_bulk_suspend_operation(self, user_ids):
        """Test bulk suspend operation"""
        if len(user_ids) < 2:
            self.log_test("Bulk Suspend Operation", False, error_msg="Need at least 2 users for bulk suspend test")
            return False
            
        try:
            # Use next 2 users for suspend test
            suspend_user_ids = user_ids[:2]
            
            bulk_data = {
                "action": "suspend",
                "user_ids": suspend_user_ids
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/bulk-action",
                json=bulk_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {})
                success_count = results.get('success_count', 0)
                failed_count = results.get('failed_count', 0)
                errors = results.get('errors', [])
                
                # Verify users are actually suspended
                suspended_count = 0
                try:
                    check_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=5)
                    if check_response.status_code == 200:
                        all_users = check_response.json()
                        for user_id in suspend_user_ids:
                            user = next((u for u in all_users if u.get('id') == user_id), None)
                            if user and not user.get('is_active', True):
                                suspended_count += 1
                except:
                    pass
                
                self.log_test(
                    "Bulk Suspend Operation", 
                    success_count == len(suspend_user_ids),
                    f"Suspended {success_count}/{len(suspend_user_ids)} users successfully. Verified {suspended_count} users are inactive. Errors: {len(errors)}"
                )
                return success_count == len(suspend_user_ids)
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Bulk Suspend Operation", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Bulk Suspend Operation", False, error_msg=str(e))
            return False

    def test_bulk_approve_operation(self, user_ids):
        """Test bulk approve operation"""
        if len(user_ids) < 2:
            self.log_test("Bulk Approve Operation", False, error_msg="Need at least 2 users for bulk approve test")
            return False
            
        try:
            # Use next 2 users for approve test
            approve_user_ids = user_ids[:2]
            
            # First set them to pending status
            for user_id in approve_user_ids:
                requests.put(
                    f"{BACKEND_URL}/admin/users/{user_id}",
                    json={"registration_status": "Pending"},
                    timeout=5
                )
            
            bulk_data = {
                "action": "approve",
                "user_ids": approve_user_ids
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/bulk-action",
                json=bulk_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {})
                success_count = results.get('success_count', 0)
                failed_count = results.get('failed_count', 0)
                errors = results.get('errors', [])
                
                # Verify users are actually approved
                approved_count = 0
                try:
                    check_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=5)
                    if check_response.status_code == 200:
                        all_users = check_response.json()
                        for user_id in approve_user_ids:
                            user = next((u for u in all_users if u.get('id') == user_id), None)
                            if user and user.get('registration_status') == 'Approved':
                                approved_count += 1
                except:
                    pass
                
                # Check for approval notifications
                notification_count = 0
                for user_id in approve_user_ids:
                    try:
                        notif_response = requests.get(f"{BACKEND_URL}/user/{user_id}/notifications", timeout=5)
                        if notif_response.status_code == 200:
                            notifications = notif_response.json()
                            approval_notifs = [n for n in notifications if n.get('type') == 'registration_approved']
                            if approval_notifs:
                                notification_count += 1
                    except:
                        pass
                
                self.log_test(
                    "Bulk Approve Operation", 
                    success_count == len(approve_user_ids),
                    f"Approved {success_count}/{len(approve_user_ids)} users successfully. Verified {approved_count} users approved, {notification_count} notifications sent. Errors: {len(errors)}"
                )
                return success_count == len(approve_user_ids)
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Bulk Approve Operation", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Bulk Approve Operation", False, error_msg=str(e))
            return False

    def test_bulk_reject_operation(self, user_ids):
        """Test bulk reject operation"""
        if len(user_ids) < 2:
            self.log_test("Bulk Reject Operation", False, error_msg="Need at least 2 users for bulk reject test")
            return False
            
        try:
            # Use remaining users for reject test
            reject_user_ids = user_ids[:2]
            
            # First set them to pending status
            for user_id in reject_user_ids:
                requests.put(
                    f"{BACKEND_URL}/admin/users/{user_id}",
                    json={"registration_status": "Pending"},
                    timeout=5
                )
            
            bulk_data = {
                "action": "reject",
                "user_ids": reject_user_ids
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/bulk-action",
                json=bulk_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {})
                success_count = results.get('success_count', 0)
                failed_count = results.get('failed_count', 0)
                errors = results.get('errors', [])
                
                # Verify users are actually rejected
                rejected_count = 0
                try:
                    check_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=5)
                    if check_response.status_code == 200:
                        all_users = check_response.json()
                        for user_id in reject_user_ids:
                            user = next((u for u in all_users if u.get('id') == user_id), None)
                            if user and user.get('registration_status') == 'Rejected':
                                rejected_count += 1
                except:
                    pass
                
                # Check for rejection notifications
                notification_count = 0
                for user_id in reject_user_ids:
                    try:
                        notif_response = requests.get(f"{BACKEND_URL}/user/{user_id}/notifications", timeout=5)
                        if notif_response.status_code == 200:
                            notifications = notif_response.json()
                            rejection_notifs = [n for n in notifications if n.get('type') == 'registration_rejected']
                            if rejection_notifs:
                                notification_count += 1
                    except:
                        pass
                
                self.log_test(
                    "Bulk Reject Operation", 
                    success_count == len(reject_user_ids),
                    f"Rejected {success_count}/{len(reject_user_ids)} users successfully. Verified {rejected_count} users rejected, {notification_count} notifications sent. Errors: {len(errors)}"
                )
                return success_count == len(reject_user_ids)
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Bulk Reject Operation", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Bulk Reject Operation", False, error_msg=str(e))
            return False

    def test_bulk_error_handling(self):
        """Test bulk operation error handling"""
        try:
            # Test invalid action
            invalid_action_data = {
                "action": "invalid_action",
                "user_ids": ["test_id_1", "test_id_2"]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/bulk-action",
                json=invalid_action_data,
                timeout=10
            )
            
            invalid_action_handled = response.status_code == 200
            if invalid_action_handled:
                data = response.json()
                results = data.get('results', {})
                errors = results.get('errors', [])
                invalid_action_handled = len(errors) > 0
            
            # Test missing parameters
            missing_params_data = {
                "action": "delete"
                # Missing user_ids
            }
            
            response2 = requests.post(
                f"{BACKEND_URL}/admin/users/bulk-action",
                json=missing_params_data,
                timeout=10
            )
            
            missing_params_handled = response2.status_code == 400
            
            # Test non-existent users
            nonexistent_data = {
                "action": "delete",
                "user_ids": ["nonexistent_id_1", "nonexistent_id_2"]
            }
            
            response3 = requests.post(
                f"{BACKEND_URL}/admin/users/bulk-action",
                json=nonexistent_data,
                timeout=10
            )
            
            nonexistent_handled = response3.status_code == 200
            if nonexistent_handled:
                data3 = response3.json()
                results3 = data3.get('results', {})
                failed_count = results3.get('failed_count', 0)
                nonexistent_handled = failed_count > 0
            
            self.log_test(
                "Bulk Error Handling", 
                invalid_action_handled and missing_params_handled and nonexistent_handled,
                f"Invalid action handled: {invalid_action_handled}, Missing params handled: {missing_params_handled}, Non-existent users handled: {nonexistent_handled}"
            )
            return invalid_action_handled and missing_params_handled and nonexistent_handled
            
        except Exception as e:
            self.log_test("Bulk Error Handling", False, error_msg=str(e))
            return False

    def test_bulk_performance(self):
        """Test bulk operation performance with multiple users"""
        try:
            # Create 10 test users for performance test
            perf_user_ids = []
            for i in range(10):
                test_id = str(uuid.uuid4())[:8]
                user_data = {
                    "username": f"perftest_{test_id}",
                    "email": f"perftest_{test_id}@example.com",
                    "full_name": f"Performance Test User {i+1}",
                    "password": "TestPassword123!",
                    "role": "user"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/admin/users", 
                    json=user_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    user = data.get('user', {})
                    user_id = user.get('id')
                    if user_id:
                        perf_user_ids.append(user_id)
                        self.created_user_ids.append(user_id)
            
            if len(perf_user_ids) < 5:
                self.log_test("Bulk Performance Test", False, error_msg="Could not create enough users for performance test")
                return False
            
            # Test bulk activate performance
            start_time = time.time()
            
            bulk_data = {
                "action": "activate",
                "user_ids": perf_user_ids
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/bulk-action",
                json=bulk_data,
                timeout=30  # Longer timeout for performance test
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {})
                success_count = results.get('success_count', 0)
                
                # Performance is acceptable if it processes users in reasonable time
                performance_acceptable = duration < 10.0 and success_count == len(perf_user_ids)
                
                self.log_test(
                    "Bulk Performance Test", 
                    performance_acceptable,
                    f"Processed {success_count}/{len(perf_user_ids)} users in {duration:.2f} seconds ({len(perf_user_ids)/duration:.1f} users/sec)"
                )
                return performance_acceptable
            else:
                self.log_test("Bulk Performance Test", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Bulk Performance Test", False, error_msg=str(e))
            return False

    def cleanup_test_users(self):
        """Clean up all test users created during testing"""
        if not self.created_user_ids:
            return
            
        try:
            # Use bulk delete to clean up
            cleanup_data = {
                "action": "delete",
                "user_ids": self.created_user_ids
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/bulk-action",
                json=cleanup_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {})
                success_count = results.get('success_count', 0)
                
                self.log_test(
                    "Test Cleanup", 
                    True, 
                    f"Successfully cleaned up {success_count}/{len(self.created_user_ids)} test users using bulk delete"
                )
            else:
                # Fallback to individual deletion
                cleaned_count = 0
                for user_id in self.created_user_ids:
                    try:
                        response = requests.delete(f"{BACKEND_URL}/admin/users/{user_id}", timeout=5)
                        if response.status_code == 200:
                            cleaned_count += 1
                    except:
                        pass
                
                self.log_test(
                    "Test Cleanup (Fallback)", 
                    True, 
                    f"Cleaned up {cleaned_count}/{len(self.created_user_ids)} test users individually"
                )
                
        except Exception as e:
            self.log_test("Test Cleanup", False, error_msg=str(e))

    def run_comprehensive_bulk_tests(self):
        """Run all bulk user management tests"""
        print("=" * 80)
        print("CATALORO BULK USER MANAGEMENT TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting bulk user management testing.")
            return
        
        # 2. Create Test Users
        print("👥 CREATING TEST USERS FOR BULK OPERATIONS")
        print("-" * 40)
        test_users = self.create_test_users(10)  # Create 10 test users
        
        if len(test_users) < 5:
            print("❌ Could not create enough test users. Aborting bulk testing.")
            return
        
        # 3. Test Bulk Delete
        print("🗑️ TESTING BULK DELETE OPERATION")
        print("-" * 40)
        remaining_users = test_users[2:]  # Keep some users for other tests
        self.test_bulk_delete_operation(test_users[:2])
        
        # 4. Test Bulk Activate
        print("✅ TESTING BULK ACTIVATE OPERATION")
        print("-" * 40)
        if len(remaining_users) >= 2:
            self.test_bulk_activate_operation(remaining_users[:2])
            remaining_users = remaining_users[2:]
        
        # 5. Test Bulk Suspend
        print("⏸️ TESTING BULK SUSPEND OPERATION")
        print("-" * 40)
        if len(remaining_users) >= 2:
            self.test_bulk_suspend_operation(remaining_users[:2])
            remaining_users = remaining_users[2:]
        
        # 6. Test Bulk Approve
        print("👍 TESTING BULK APPROVE OPERATION")
        print("-" * 40)
        if len(remaining_users) >= 2:
            self.test_bulk_approve_operation(remaining_users[:2])
            remaining_users = remaining_users[2:]
        
        # 7. Test Bulk Reject
        print("👎 TESTING BULK REJECT OPERATION")
        print("-" * 40)
        if len(remaining_users) >= 2:
            self.test_bulk_reject_operation(remaining_users[:2])
        
        # 8. Test Error Handling
        print("⚠️ TESTING BULK ERROR HANDLING")
        print("-" * 40)
        self.test_bulk_error_handling()
        
        # 9. Test Performance
        print("🚀 TESTING BULK PERFORMANCE")
        print("-" * 40)
        self.test_bulk_performance()
        
        # 10. Cleanup
        print("🧹 CLEANUP")
        print("-" * 40)
        self.cleanup_test_users()
        
        # Print Summary
        print("=" * 80)
        print("BULK USER MANAGEMENT TEST SUMMARY")
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
        
        print("\n🎯 BULK USER MANAGEMENT TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BulkUserManagementTester()
    
    print("🎯 RUNNING BULK USER MANAGEMENT TESTING")
    print("Testing the newly implemented bulk user management functionality...")
    print()
    
    passed, failed, results = tester.run_comprehensive_bulk_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)