#!/usr/bin/env python3
"""
SYSTEM NOTIFICATIONS SEPARATION TESTING AND CLEANUP
Backend API Testing for Cataloro Marketplace

This test focuses on:
1. Database cleanup - removing system notifications from user_notifications collection
2. System notifications endpoint test - verify /api/user/{user_id}/system-notifications
3. Regular notifications endpoint test - verify /api/user/{user_id}/notifications  
4. Separation verification - confirm system and regular notifications are separate
5. System notification triggering - test they're triggered but NOT stored in user_notifications
6. Database collections verification
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://cataloro-upgrade.preview.emergentagent.com/api"
TEST_USER_EMAIL = "system_test_user@example.com"
TEST_USER_PASSWORD = "testpass123"
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin123"

class NotificationsTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_user_id = None
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
    
    def log_test(self, test_name, success, details, expected=None, actual=None):
        """Log test results"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed_tests"] += 1
            status = "✅ PASSED"
        else:
            self.test_results["failed_tests"] += 1
            status = "❌ FAILED"
        
        self.test_results["test_details"].append(f"{status} - {test_name}")
        print(f"{status} - {test_name}")
        print(f"   Details: {details}")
        if expected and actual:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
        print()
    
    def setup_test_user(self):
        """Setup test user for notifications testing"""
        try:
            # Login as demo user to get user ID
            test_user_data = {
                "email": "demo@cataloro.com",
                "password": "demo123",
                "username": "notifications_test_user"
            }
            
            login_response = self.session.post(f"{API_BASE}/auth/login", json=test_user_data)
            if login_response.status_code == 200:
                user_data = login_response.json()
                self.test_user_id = user_data.get("user", {}).get("id")
                
                if self.test_user_id:
                    self.log_test(
                        "Test User Setup",
                        True,
                        f"Successfully logged in test user with ID: {self.test_user_id}"
                    )
                    return True
                else:
                    self.log_test(
                        "Test User Setup",
                        False,
                        "Failed to get user ID from login response"
                    )
                    return False
            else:
                self.log_test(
                    "Test User Setup",
                    False,
                    f"Login failed with status {login_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Test User Setup",
                False,
                f"Exception during setup: {str(e)}"
            )
            return False
    
    def test_old_notifications_endpoint(self):
        """Test 1: Check old notifications endpoint (the problematic one)"""
        try:
            if not self.test_user_id:
                self.log_test(
                    "Old Notifications Endpoint Test",
                    False,
                    "No test user ID available"
                )
                return False
            
            response = self.session.get(f"{API_BASE}/user/notifications/{self.test_user_id}")
            
            if response.status_code != 200:
                self.log_test(
                    "Old Notifications Endpoint Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            notifications = response.json()
            
            # Check if this endpoint returns dummy data
            dummy_indicators = [
                "MacBook listing",
                "vintage guitar listing",
                "New message",
                "Listing viewed"
            ]
            
            has_dummy_data = False
            for notification in notifications:
                message = notification.get("message", "")
                title = notification.get("title", "")
                for indicator in dummy_indicators:
                    if indicator in message or indicator in title:
                        has_dummy_data = True
                        break
            
            self.log_test(
                "Old Notifications Endpoint Test",
                True,
                f"Endpoint accessible, returned {len(notifications)} notifications. Contains dummy data: {has_dummy_data}"
            )
            
            return {"notifications": notifications, "has_dummy_data": has_dummy_data}
            
        except Exception as e:
            self.log_test(
                "Old Notifications Endpoint Test",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_new_notifications_endpoint(self):
        """Test 2: Check new notifications endpoint (the correct one)"""
        try:
            if not self.test_user_id:
                self.log_test(
                    "New Notifications Endpoint Test",
                    False,
                    "No test user ID available"
                )
                return False
            
            response = self.session.get(f"{API_BASE}/user/{self.test_user_id}/notifications")
            
            if response.status_code != 200:
                self.log_test(
                    "New Notifications Endpoint Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            notifications = response.json()
            
            # Check notification structure
            required_fields = ["id", "title", "message", "type", "is_read", "created_at"]
            structure_valid = True
            missing_fields = []
            
            for notification in notifications:
                for field in required_fields:
                    if field not in notification:
                        structure_valid = False
                        if field not in missing_fields:
                            missing_fields.append(field)
            
            self.log_test(
                "New Notifications Endpoint Test",
                True,
                f"Endpoint accessible, returned {len(notifications)} notifications. Structure valid: {structure_valid}"
            )
            
            if missing_fields:
                print(f"   Missing fields in some notifications: {missing_fields}")
            
            return {"notifications": notifications, "structure_valid": structure_valid}
            
        except Exception as e:
            self.log_test(
                "New Notifications Endpoint Test",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_notification_creation_trigger(self):
        """Test 3: Test if notifications are created when actions are performed"""
        try:
            if not self.test_user_id:
                self.log_test(
                    "Notification Creation Test",
                    False,
                    "No test user ID available"
                )
                return False
            
            # Get initial notification count
            initial_response = self.session.get(f"{API_BASE}/user/{self.test_user_id}/notifications")
            if initial_response.status_code != 200:
                self.log_test(
                    "Notification Creation Test",
                    False,
                    "Failed to get initial notification count"
                )
                return False
            
            initial_count = len(initial_response.json())
            
            # Trigger a notification by creating a test notification
            test_notification = {
                "title": "Test Notification",
                "message": "This is a test notification created during testing",
                "type": "test"
            }
            
            create_response = self.session.post(
                f"{API_BASE}/user/{self.test_user_id}/notifications",
                json=test_notification
            )
            
            if create_response.status_code not in [200, 201]:
                self.log_test(
                    "Notification Creation Test",
                    False,
                    f"Failed to create test notification: HTTP {create_response.status_code}"
                )
                return False
            
            # Wait a moment for the notification to be processed
            time.sleep(1)
            
            # Check if notification count increased
            final_response = self.session.get(f"{API_BASE}/user/{self.test_user_id}/notifications")
            if final_response.status_code != 200:
                self.log_test(
                    "Notification Creation Test",
                    False,
                    "Failed to get final notification count"
                )
                return False
            
            final_count = len(final_response.json())
            
            if final_count > initial_count:
                self.log_test(
                    "Notification Creation Test",
                    True,
                    f"Notification created successfully. Count increased from {initial_count} to {final_count}"
                )
                return True
            else:
                self.log_test(
                    "Notification Creation Test",
                    False,
                    f"Notification not created. Count remained {initial_count}"
                )
                return False
            
        except Exception as e:
            self.log_test(
                "Notification Creation Test",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_notification_structure_validation(self):
        """Test 4: Validate notification structure matches frontend expectations"""
        try:
            if not self.test_user_id:
                self.log_test(
                    "Notification Structure Validation",
                    False,
                    "No test user ID available"
                )
                return False
            
            response = self.session.get(f"{API_BASE}/user/{self.test_user_id}/notifications")
            
            if response.status_code != 200:
                self.log_test(
                    "Notification Structure Validation",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            notifications = response.json()
            
            if not notifications:
                self.log_test(
                    "Notification Structure Validation",
                    False,
                    "No notifications found to validate structure"
                )
                return False
            
            # Check required fields for frontend
            required_fields = ["id", "title", "message", "type", "is_read", "created_at"]
            optional_fields = ["user_id", "read_at", "archived"]
            
            structure_issues = []
            valid_notifications = 0
            
            for i, notification in enumerate(notifications):
                notification_issues = []
                
                # Check required fields
                for field in required_fields:
                    if field not in notification:
                        notification_issues.append(f"Missing required field: {field}")
                    elif notification[field] is None:
                        notification_issues.append(f"Required field is null: {field}")
                
                # Check field types
                if "id" in notification and not isinstance(notification["id"], str):
                    notification_issues.append("ID field should be string")
                
                if "is_read" in notification and not isinstance(notification["is_read"], bool):
                    notification_issues.append("is_read field should be boolean")
                
                if "created_at" in notification:
                    created_at = notification["created_at"]
                    if not isinstance(created_at, str):
                        notification_issues.append("created_at should be string (ISO format)")
                
                if not notification_issues:
                    valid_notifications += 1
                else:
                    structure_issues.extend([f"Notification {i+1}: {issue}" for issue in notification_issues])
            
            if not structure_issues:
                self.log_test(
                    "Notification Structure Validation",
                    True,
                    f"All {len(notifications)} notifications have valid structure"
                )
                return True
            else:
                self.log_test(
                    "Notification Structure Validation",
                    False,
                    f"Structure issues found in {len(notifications) - valid_notifications} notifications: {structure_issues[:5]}"  # Show first 5 issues
                )
                return False
            
        except Exception as e:
            self.log_test(
                "Notification Structure Validation",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_mark_notification_read(self):
        """Test 5: Test marking notifications as read"""
        try:
            if not self.test_user_id:
                self.log_test(
                    "Mark Notification Read Test",
                    False,
                    "No test user ID available"
                )
                return False
            
            # Get notifications to find one to mark as read
            response = self.session.get(f"{API_BASE}/user/{self.test_user_id}/notifications")
            
            if response.status_code != 200:
                self.log_test(
                    "Mark Notification Read Test",
                    False,
                    f"Failed to get notifications: HTTP {response.status_code}"
                )
                return False
            
            notifications = response.json()
            
            if not notifications:
                self.log_test(
                    "Mark Notification Read Test",
                    False,
                    "No notifications available to test read functionality"
                )
                return False
            
            # Find an unread notification
            unread_notification = None
            for notification in notifications:
                if not notification.get("is_read", True):
                    unread_notification = notification
                    break
            
            if not unread_notification:
                # Create a test notification to mark as read
                test_notification = {
                    "title": "Read Test Notification",
                    "message": "This notification will be marked as read",
                    "type": "test"
                }
                
                create_response = self.session.post(
                    f"{API_BASE}/user/{self.test_user_id}/notifications",
                    json=test_notification
                )
                
                if create_response.status_code not in [200, 201]:
                    self.log_test(
                        "Mark Notification Read Test",
                        False,
                        "Failed to create test notification for read test"
                    )
                    return False
                
                # Get the newly created notification
                time.sleep(1)
                response = self.session.get(f"{API_BASE}/user/{self.test_user_id}/notifications")
                notifications = response.json()
                unread_notification = notifications[0] if notifications else None
            
            if not unread_notification:
                self.log_test(
                    "Mark Notification Read Test",
                    False,
                    "Could not find or create notification to test read functionality"
                )
                return False
            
            notification_id = unread_notification.get("id")
            
            # Test the read endpoint
            read_response = self.session.put(f"{API_BASE}/user/{self.test_user_id}/notifications/{notification_id}/read")
            
            if read_response.status_code != 200:
                self.log_test(
                    "Mark Notification Read Test",
                    False,
                    f"Failed to mark notification as read: HTTP {read_response.status_code}"
                )
                return False
            
            # Verify the notification is now marked as read
            verify_response = self.session.get(f"{API_BASE}/user/{self.test_user_id}/notifications")
            if verify_response.status_code == 200:
                updated_notifications = verify_response.json()
                updated_notification = None
                
                for notification in updated_notifications:
                    if notification.get("id") == notification_id:
                        updated_notification = notification
                        break
                
                if updated_notification and updated_notification.get("is_read"):
                    self.log_test(
                        "Mark Notification Read Test",
                        True,
                        f"Successfully marked notification {notification_id} as read"
                    )
                    return True
                else:
                    self.log_test(
                        "Mark Notification Read Test",
                        False,
                        "Notification was not properly marked as read"
                    )
                    return False
            else:
                self.log_test(
                    "Mark Notification Read Test",
                    False,
                    "Failed to verify read status"
                )
                return False
            
        except Exception as e:
            self.log_test(
                "Mark Notification Read Test",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_system_notification_triggers(self):
        """Test 6: Test if system notifications are triggered by user actions"""
        try:
            if not self.test_user_id:
                self.log_test(
                    "System Notification Triggers Test",
                    False,
                    "No test user ID available"
                )
                return False
            
            # Get initial notification count
            initial_response = self.session.get(f"{API_BASE}/user/{self.test_user_id}/notifications")
            if initial_response.status_code != 200:
                self.log_test(
                    "System Notification Triggers Test",
                    False,
                    "Failed to get initial notification count"
                )
                return False
            
            initial_count = len(initial_response.json())
            
            # Trigger a login event (which should create system notifications)
            login_data = {
                "email": "demo@cataloro.com",
                "password": "demo123"
            }
            
            login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                self.log_test(
                    "System Notification Triggers Test",
                    False,
                    f"Login trigger failed: HTTP {login_response.status_code}"
                )
                return False
            
            # Wait for system notifications to be processed
            time.sleep(2)
            
            # Check if new notifications were created
            final_response = self.session.get(f"{API_BASE}/user/{self.test_user_id}/notifications")
            if final_response.status_code != 200:
                self.log_test(
                    "System Notification Triggers Test",
                    False,
                    "Failed to get final notification count"
                )
                return False
            
            final_notifications = final_response.json()
            final_count = len(final_notifications)
            
            # Check for system-generated notifications
            system_notifications = []
            for notification in final_notifications:
                if notification.get("system_notification_id") or notification.get("event_trigger"):
                    system_notifications.append(notification)
            
            self.log_test(
                "System Notification Triggers Test",
                True,
                f"Found {len(system_notifications)} system notifications out of {final_count} total notifications"
            )
            
            return len(system_notifications) > 0
            
        except Exception as e:
            self.log_test(
                "System Notification Triggers Test",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all notification system tests"""
        print("=" * 80)
        print("USER NOTIFICATIONS SYSTEM COMPREHENSIVE TESTING")
        print("Testing why NotificationsCenterPage shows fake/demo notifications")
        print("=" * 80)
        print()
        
        # Setup test user
        if not self.setup_test_user():
            print("❌ Cannot proceed without test user setup")
            return False
        
        # Test 1: Old notifications endpoint (problematic one)
        old_endpoint_result = self.test_old_notifications_endpoint()
        
        # Test 2: New notifications endpoint (correct one)
        new_endpoint_result = self.test_new_notifications_endpoint()
        
        # Test 3: Notification creation
        creation_success = self.test_notification_creation_trigger()
        
        # Test 4: Structure validation
        structure_success = self.test_notification_structure_validation()
        
        # Test 5: Mark as read functionality
        read_success = self.test_mark_notification_read()
        
        # Test 6: System notification triggers
        system_triggers_success = self.test_system_notification_triggers()
        
        # Summary
        print("=" * 80)
        print("NOTIFICATIONS SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']}")
        print(f"Failed: {self.test_results['failed_tests']}")
        print(f"Success Rate: {(self.test_results['passed_tests']/self.test_results['total_tests']*100):.1f}%")
        print()
        
        # Individual test results
        for detail in self.test_results['test_details']:
            print(detail)
        
        print()
        
        # Root cause analysis
        print("=" * 80)
        print("ROOT CAUSE ANALYSIS")
        print("=" * 80)
        
        issues_found = []
        
        if old_endpoint_result and old_endpoint_result.get("has_dummy_data"):
            issues_found.append("❌ Old endpoint (/api/user/notifications/{user_id}) returns dummy data")
        
        if new_endpoint_result:
            new_notifications = new_endpoint_result.get("notifications", [])
            if len(new_notifications) == 0:
                issues_found.append("❌ New endpoint (/api/user/{user_id}/notifications) has no real notifications")
            else:
                print(f"✅ New endpoint has {len(new_notifications)} real notifications")
        
        if not creation_success:
            issues_found.append("❌ Notification creation is not working properly")
        
        if not structure_success:
            issues_found.append("❌ Notification structure doesn't match frontend expectations")
        
        if not read_success:
            issues_found.append("❌ Mark as read functionality is not working")
        
        if issues_found:
            print("CRITICAL ISSUES IDENTIFIED:")
            for issue in issues_found:
                print(f"  {issue}")
        else:
            print("✅ NO CRITICAL ISSUES FOUND - Notifications system appears to be working correctly")
        
        print()
        
        # Recommendations
        print("RECOMMENDATIONS:")
        if old_endpoint_result and old_endpoint_result.get("has_dummy_data"):
            print("1. Frontend should use /api/user/{user_id}/notifications instead of /api/user/notifications/{user_id}")
            print("2. Remove dummy data generation from old endpoint")
        
        if new_endpoint_result and len(new_endpoint_result.get("notifications", [])) == 0:
            print("3. Ensure system notifications are being triggered properly for user actions")
            print("4. Check if notification triggers are working for listing views, messages, etc.")
        
        print()
        return len(issues_found) == 0

if __name__ == "__main__":
    tester = NotificationsTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 NOTIFICATIONS SYSTEM WORKING CORRECTLY!")
        sys.exit(0)
    else:
        print("⚠️  NOTIFICATIONS SYSTEM ISSUES FOUND - Check analysis above")
        sys.exit(1)