#!/usr/bin/env python3
"""
Enhanced Bulk Notification Functionality Test Suite
Tests the new general notification update endpoint and bulk operations
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class NotificationBulkTester:
    def __init__(self, base_url="https://admanager-cataloro.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        # Disable SSL verification for testing environment
        self.session.verify = False
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.test_notifications = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_users(self):
        """Setup admin and regular users for testing"""
        print("\n🔧 Setting up test users...")
        
        # Login admin user
        success_admin, admin_response = self.run_test(
            "Admin Login Setup",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success_admin and 'token' in admin_response:
            self.admin_token = admin_response['token']
            self.admin_user = admin_response['user']
            print(f"   ✅ Admin User: {self.admin_user.get('username', 'N/A')}")
        
        # Login regular user
        success_user, user_response = self.run_test(
            "Regular User Login Setup",
            "POST",
            "api/auth/login",
            200,
            data={"email": "demo@cataloro.com", "password": "demo123"}
        )
        
        if success_user and 'token' in user_response:
            self.user_token = user_response['token']
            self.regular_user = user_response['user']
            print(f"   ✅ Regular User: {self.regular_user.get('username', 'N/A')}")
        
        return success_admin and success_user

    def create_test_notifications(self):
        """Create test notifications for bulk operations testing"""
        print("\n📝 Creating test notifications...")
        
        if not self.regular_user:
            print("❌ Cannot create test notifications - no regular user")
            return False
        
        user_id = self.regular_user['id']
        
        # Create multiple test notifications with different types
        test_notifications_data = [
            {
                "title": "Bulk Test Notification 1",
                "message": "This is a test notification for bulk operations - Message type",
                "type": "message"
            },
            {
                "title": "Bulk Test Notification 2", 
                "message": "This is a test notification for bulk operations - Info type",
                "type": "info"
            },
            {
                "title": "Bulk Test Notification 3",
                "message": "This is a test notification for bulk operations - System type",
                "type": "system"
            },
            {
                "title": "Bulk Test Notification 4",
                "message": "This is a test notification for bulk operations - Alert type",
                "type": "alert"
            }
        ]
        
        created_count = 0
        for i, notification_data in enumerate(test_notifications_data):
            success, response = self.run_test(
                f"Create Test Notification {i+1}",
                "POST",
                f"api/user/{user_id}/notifications",
                200,
                data=notification_data
            )
            
            if success and 'id' in response:
                self.test_notifications.append(response['id'])
                created_count += 1
                print(f"   ✅ Created notification {i+1} with ID: {response['id']}")
        
        self.log_test("Test Notifications Creation", created_count == 4, 
                     f"Created {created_count}/4 test notifications")
        
        return created_count == 4

    def test_general_notification_update_endpoint(self):
        """Test the new general notification update endpoint with various payloads"""
        print("\n🔄 Testing General Notification Update Endpoint...")
        
        if not self.regular_user or not self.test_notifications:
            print("❌ Cannot test update endpoint - missing user or notifications")
            return False
        
        user_id = self.regular_user['id']
        test_results = []
        
        # Test 1: Mark as read
        print("\n1️⃣ Testing mark as read...")
        notification_id = self.test_notifications[0]
        success, response = self.run_test(
            "Update Notification - Mark as Read",
            "PUT",
            f"api/user/{user_id}/notifications/{notification_id}",
            200,
            data={"read": True}
        )
        test_results.append(success)
        
        if success:
            updated_fields = response.get('updated_fields', [])
            read_updated = 'is_read' in updated_fields
            self.log_test("Read Field Updated", read_updated, 
                         f"is_read field updated: {read_updated}")
        
        # Test 2: Mark as unread
        print("\n2️⃣ Testing mark as unread...")
        success, response = self.run_test(
            "Update Notification - Mark as Unread",
            "PUT",
            f"api/user/{user_id}/notifications/{notification_id}",
            200,
            data={"read": False}
        )
        test_results.append(success)
        
        # Test 3: Archive notification
        print("\n3️⃣ Testing archive notification...")
        notification_id = self.test_notifications[1]
        success, response = self.run_test(
            "Update Notification - Archive",
            "PUT",
            f"api/user/{user_id}/notifications/{notification_id}",
            200,
            data={"archived": True}
        )
        test_results.append(success)
        
        if success:
            updated_fields = response.get('updated_fields', [])
            archived_updated = 'archived' in updated_fields
            self.log_test("Archived Field Updated", archived_updated,
                         f"archived field updated: {archived_updated}")
        
        # Test 4: Unarchive notification
        print("\n4️⃣ Testing unarchive notification...")
        success, response = self.run_test(
            "Update Notification - Unarchive",
            "PUT",
            f"api/user/{user_id}/notifications/{notification_id}",
            200,
            data={"archived": False}
        )
        test_results.append(success)
        
        # Test 5: Combined updates (read + archived)
        print("\n5️⃣ Testing combined updates...")
        notification_id = self.test_notifications[2]
        success, response = self.run_test(
            "Update Notification - Combined (Read + Archived)",
            "PUT",
            f"api/user/{user_id}/notifications/{notification_id}",
            200,
            data={"read": True, "archived": True}
        )
        test_results.append(success)
        
        if success:
            updated_fields = response.get('updated_fields', [])
            both_updated = 'is_read' in updated_fields and 'archived' in updated_fields
            self.log_test("Combined Fields Updated", both_updated,
                         f"Both fields updated: {both_updated}")
        
        # Test 6: Invalid notification ID
        print("\n6️⃣ Testing invalid notification ID...")
        invalid_id = str(uuid.uuid4())
        success, response = self.run_test(
            "Update Notification - Invalid ID (Should Fail)",
            "PUT",
            f"api/user/{user_id}/notifications/{invalid_id}",
            404,
            data={"read": True}
        )
        test_results.append(success)
        
        # Test 7: Empty update data
        print("\n7️⃣ Testing empty update data...")
        notification_id = self.test_notifications[3]
        success, response = self.run_test(
            "Update Notification - Empty Data (Should Fail)",
            "PUT",
            f"api/user/{user_id}/notifications/{notification_id}",
            400,
            data={}
        )
        test_results.append(success)
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"\n📊 General Update Endpoint Summary: {passed_tests}/{total_tests} tests passed")
        return passed_tests == total_tests

    def test_existing_read_only_endpoint(self):
        """Test the existing read-only notification endpoint"""
        print("\n📖 Testing Existing Read-Only Endpoint...")
        
        if not self.regular_user or not self.test_notifications:
            print("❌ Cannot test read-only endpoint - missing user or notifications")
            return False
        
        user_id = self.regular_user['id']
        
        # Use the last test notification for read-only testing
        notification_id = self.test_notifications[-1]
        
        success, response = self.run_test(
            "Read-Only Endpoint - Mark as Read",
            "PUT",
            f"api/user/{user_id}/notifications/{notification_id}/read",
            200
        )
        
        if success:
            message = response.get('message', '')
            correct_message = 'marked as read' in message.lower()
            self.log_test("Read-Only Endpoint Message", correct_message,
                         f"Correct response message: {correct_message}")
        
        return success

    def test_notification_retrieval_with_archived_field(self):
        """Test notification retrieval includes archived field"""
        print("\n📋 Testing Notification Retrieval with Archived Field...")
        
        if not self.regular_user:
            print("❌ Cannot test retrieval - no regular user")
            return False
        
        user_id = self.regular_user['id']
        
        success, response = self.run_test(
            "Get User Notifications",
            "GET",
            f"api/user/{user_id}/notifications",
            200
        )
        
        if success and response:
            # Check if notifications have archived field
            archived_field_present = False
            archived_notifications_found = False
            
            for notification in response:
                if 'archived' in notification:
                    archived_field_present = True
                    if notification.get('archived'):
                        archived_notifications_found = True
                        break
            
            self.log_test("Archived Field Present", archived_field_present,
                         f"Archived field found in notifications: {archived_field_present}")
            
            # Check for other expected fields
            if response:
                first_notification = response[0]
                expected_fields = ['id', 'user_id', 'title', 'message', 'type', 'is_read', 'created_at']
                fields_present = all(field in first_notification for field in expected_fields)
                self.log_test("Required Fields Present", fields_present,
                             f"All required fields present: {fields_present}")
            
            print(f"   📊 Retrieved {len(response)} notifications")
            print(f"   📁 Archived field present: {archived_field_present}")
            
            return archived_field_present
        
        return False

    def test_bulk_notification_scenarios(self):
        """Test bulk notification scenarios that would be used by frontend"""
        print("\n📦 Testing Bulk Notification Scenarios...")
        
        if not self.regular_user or len(self.test_notifications) < 3:
            print("❌ Cannot test bulk scenarios - insufficient test data")
            return False
        
        user_id = self.regular_user['id']
        bulk_results = []
        
        # Scenario 1: Bulk mark as read (simulate selecting multiple notifications)
        print("\n1️⃣ Testing bulk mark as read scenario...")
        read_count = 0
        for i, notification_id in enumerate(self.test_notifications[:3]):
            success, response = self.run_test(
                f"Bulk Read {i+1}/3",
                "PUT",
                f"api/user/{user_id}/notifications/{notification_id}",
                200,
                data={"read": True}
            )
            if success:
                read_count += 1
        
        bulk_read_success = read_count == 3
        bulk_results.append(bulk_read_success)
        self.log_test("Bulk Mark as Read", bulk_read_success,
                     f"Successfully marked {read_count}/3 notifications as read")
        
        # Scenario 2: Bulk archive (simulate archive selected)
        print("\n2️⃣ Testing bulk archive scenario...")
        archive_count = 0
        for i, notification_id in enumerate(self.test_notifications[:2]):
            success, response = self.run_test(
                f"Bulk Archive {i+1}/2",
                "PUT",
                f"api/user/{user_id}/notifications/{notification_id}",
                200,
                data={"archived": True}
            )
            if success:
                archive_count += 1
        
        bulk_archive_success = archive_count == 2
        bulk_results.append(bulk_archive_success)
        self.log_test("Bulk Archive", bulk_archive_success,
                     f"Successfully archived {archive_count}/2 notifications")
        
        # Scenario 3: Bulk unarchive
        print("\n3️⃣ Testing bulk unarchive scenario...")
        unarchive_count = 0
        for i, notification_id in enumerate(self.test_notifications[:2]):
            success, response = self.run_test(
                f"Bulk Unarchive {i+1}/2",
                "PUT",
                f"api/user/{user_id}/notifications/{notification_id}",
                200,
                data={"archived": False}
            )
            if success:
                unarchive_count += 1
        
        bulk_unarchive_success = unarchive_count == 2
        bulk_results.append(bulk_unarchive_success)
        self.log_test("Bulk Unarchive", bulk_unarchive_success,
                     f"Successfully unarchived {unarchive_count}/2 notifications")
        
        # Scenario 4: Mixed bulk operations
        print("\n4️⃣ Testing mixed bulk operations...")
        mixed_success_count = 0
        
        # Mark first as read and archived
        success1, _ = self.run_test(
            "Mixed Operation 1 - Read + Archive",
            "PUT",
            f"api/user/{user_id}/notifications/{self.test_notifications[0]}",
            200,
            data={"read": True, "archived": True}
        )
        if success1:
            mixed_success_count += 1
        
        # Mark second as unread and unarchived
        success2, _ = self.run_test(
            "Mixed Operation 2 - Unread + Unarchive",
            "PUT",
            f"api/user/{user_id}/notifications/{self.test_notifications[1]}",
            200,
            data={"read": False, "archived": False}
        )
        if success2:
            mixed_success_count += 1
        
        mixed_operations_success = mixed_success_count == 2
        bulk_results.append(mixed_operations_success)
        self.log_test("Mixed Bulk Operations", mixed_operations_success,
                     f"Successfully completed {mixed_success_count}/2 mixed operations")
        
        # Summary
        passed_scenarios = sum(bulk_results)
        total_scenarios = len(bulk_results)
        
        print(f"\n📊 Bulk Scenarios Summary: {passed_scenarios}/{total_scenarios} scenarios passed")
        return passed_scenarios == total_scenarios

    def test_notification_state_persistence(self):
        """Test that notification state changes persist across API calls"""
        print("\n💾 Testing Notification State Persistence...")
        
        if not self.regular_user or not self.test_notifications:
            print("❌ Cannot test persistence - missing test data")
            return False
        
        user_id = self.regular_user['id']
        notification_id = self.test_notifications[0]
        
        # Step 1: Set specific state
        print("\n1️⃣ Setting notification state...")
        success_set, _ = self.run_test(
            "Set Notification State",
            "PUT",
            f"api/user/{user_id}/notifications/{notification_id}",
            200,
            data={"read": True, "archived": True}
        )
        
        if not success_set:
            return False
        
        # Step 2: Retrieve notifications and verify state
        print("\n2️⃣ Verifying state persistence...")
        success_get, notifications = self.run_test(
            "Get Notifications for Persistence Check",
            "GET",
            f"api/user/{user_id}/notifications",
            200
        )
        
        if success_get and notifications:
            # Find our test notification
            test_notification = None
            for notification in notifications:
                if notification.get('id') == notification_id:
                    test_notification = notification
                    break
            
            if test_notification:
                is_read = test_notification.get('is_read', False)
                is_archived = test_notification.get('archived', False)
                
                state_persisted = is_read and is_archived
                self.log_test("State Persistence", state_persisted,
                             f"Read: {is_read}, Archived: {is_archived}")
                
                # Check for timestamp fields
                has_read_at = 'read_at' in test_notification
                has_archived_at = 'archived_at' in test_notification
                
                self.log_test("Timestamp Fields Present", has_read_at and has_archived_at,
                             f"read_at: {has_read_at}, archived_at: {has_archived_at}")
                
                return state_persisted
            else:
                self.log_test("Test Notification Found", False, "Test notification not found in response")
                return False
        
        return False

    def cleanup_test_notifications(self):
        """Clean up test notifications"""
        print("\n🧹 Cleaning up test notifications...")
        
        if not self.regular_user or not self.test_notifications:
            print("   ℹ️  No test notifications to clean up")
            return True
        
        user_id = self.regular_user['id']
        cleanup_count = 0
        
        for notification_id in self.test_notifications:
            try:
                # Use the delete endpoint to clean up
                success, _ = self.run_test(
                    f"Cleanup Notification {notification_id[:8]}...",
                    "DELETE",
                    f"api/user/{user_id}/notifications/{notification_id}",
                    200
                )
                if success:
                    cleanup_count += 1
            except:
                # Continue cleanup even if some fail
                pass
        
        self.log_test("Test Notifications Cleanup", cleanup_count > 0,
                     f"Cleaned up {cleanup_count}/{len(self.test_notifications)} notifications")
        
        return True

    def run_comprehensive_test(self):
        """Run comprehensive test of enhanced bulk notification functionality"""
        print("🚀 Starting Enhanced Bulk Notification Functionality Test Suite")
        print("=" * 80)
        
        # Setup
        if not self.setup_users():
            print("❌ Failed to setup users - stopping tests")
            return False
        
        # Create test data
        if not self.create_test_notifications():
            print("❌ Failed to create test notifications - stopping tests")
            return False
        
        # Run tests
        test_results = []
        
        # Test 1: General notification update endpoint
        test_results.append(self.test_general_notification_update_endpoint())
        
        # Test 2: Existing read-only endpoint
        test_results.append(self.test_existing_read_only_endpoint())
        
        # Test 3: Notification retrieval with archived field
        test_results.append(self.test_notification_retrieval_with_archived_field())
        
        # Test 4: Bulk notification scenarios
        test_results.append(self.test_bulk_notification_scenarios())
        
        # Test 5: State persistence
        test_results.append(self.test_notification_state_persistence())
        
        # Cleanup
        self.cleanup_test_notifications()
        
        # Final summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print("\n" + "=" * 80)
        print("📊 ENHANCED BULK NOTIFICATION FUNCTIONALITY TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"Major Test Categories: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL ENHANCED BULK NOTIFICATION TESTS PASSED!")
            print("✅ New general notification update endpoint working correctly")
            print("✅ Existing read-only endpoint still functional")
            print("✅ Notification retrieval includes archived field")
            print("✅ Bulk operations scenarios working")
            print("✅ State persistence verified")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} major test categories failed")
            print("❌ Enhanced bulk notification functionality has issues")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = NotificationBulkTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)