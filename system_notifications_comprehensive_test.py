#!/usr/bin/env python3
"""
System Notifications Manager Comprehensive Backend Testing
Tests the complete system notification flow as requested in the review:

1. GET System Notifications for User: /api/user/{user_id}/system-notifications
2. Mark Notification as Viewed: /api/user/{user_id}/system-notifications/{notification_id}/view
3. System Notification Creation: /api/admin/system-notifications POST
4. Event Trigger Logic: Different event triggers (manual, login, profile_update, etc.)
5. Target User Filtering: "all" users vs "specific_ids"
6. JSON Serialization: UUIDs not ObjectIds
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import os
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cataloro-marketplace-4.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class SystemNotificationsComprehensiveTest:
    def __init__(self):
        self.test_results = []
        self.created_notifications = []
        self.test_user_id = None
        self.admin_user_id = None
        self.passed_tests = 0
        self.total_tests = 0
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details and not success:
            print(f"   Details: {details}")
        print()
    
    def setup_test_environment(self):
        """Setup test users and environment"""
        try:
            # Login as admin
            admin_login = {
                "email": "admin@cataloro.com",
                "password": "admin123"
            }
            response = requests.post(f"{API_BASE}/auth/login", json=admin_login)
            if response.status_code == 200:
                user_data = response.json().get("user", {})
                self.admin_user_id = user_data.get("id")
                self.log_result("Setup Admin User", True, f"Admin user ID: {self.admin_user_id}")
            else:
                self.log_result("Setup Admin User", False, f"Failed to login admin: {response.status_code}")
                return False
            
            # Login as regular user
            user_login = {
                "email": "user@cataloro.com",
                "password": "user123"
            }
            response = requests.post(f"{API_BASE}/auth/login", json=user_login)
            if response.status_code == 200:
                user_data = response.json().get("user", {})
                self.test_user_id = user_data.get("id")
                self.log_result("Setup Test User", True, f"Test user ID: {self.test_user_id}")
            else:
                self.log_result("Setup Test User", False, f"Failed to login user: {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            self.log_result("Setup Test Environment", False, f"Exception: {str(e)}")
            return False
    
    def test_system_notification_creation(self):
        """Test 3: System Notification Creation - /api/admin/system-notifications POST"""
        try:
            # Create notification for all users with manual trigger
            notification_data = {
                "title": "System Maintenance Alert",
                "message": "Scheduled maintenance will occur tonight from 2-4 AM EST. Please save your work.",
                "type": "warning",
                "event_trigger": "manual",
                "target_users": "all",
                "show_duration": 5000,
                "is_active": True,
                "created_by": self.admin_user_id
            }
            
            response = requests.post(f"{API_BASE}/admin/system-notifications", json=notification_data)
            if response.status_code == 200:
                notification_id = response.json().get("notification_id")
                self.created_notifications.append(notification_id)
                self.log_result("System Notification Creation", True, 
                              f"Successfully created notification: {notification_id}")
                return notification_id
            else:
                self.log_result("System Notification Creation", False, 
                              f"Failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result("System Notification Creation", False, f"Exception: {str(e)}")
            return None
    
    def test_get_system_notifications_for_user(self):
        """Test 1: GET System Notifications for User - /api/user/{user_id}/system-notifications"""
        try:
            response = requests.get(f"{API_BASE}/user/{self.test_user_id}/system-notifications")
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                
                # Verify response structure
                if "notifications" in data and isinstance(notifications, list):
                    self.log_result("GET System Notifications for User", True, 
                                  f"Successfully retrieved {len(notifications)} notifications for user")
                    
                    # Verify notification structure if notifications exist
                    if notifications:
                        first_notification = notifications[0]
                        required_fields = ["id", "title", "message", "type", "event_trigger", "target_users"]
                        missing_fields = [field for field in required_fields if field not in first_notification]
                        
                        if not missing_fields:
                            self.log_result("Notification Structure Validation", True, 
                                          "All required fields present in notification")
                        else:
                            self.log_result("Notification Structure Validation", False, 
                                          f"Missing required fields: {missing_fields}")
                    
                    return notifications
                else:
                    self.log_result("GET System Notifications for User", False, 
                                  "Invalid response structure - missing 'notifications' array")
                    return []
            else:
                self.log_result("GET System Notifications for User", False, 
                              f"Failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.log_result("GET System Notifications for User", False, f"Exception: {str(e)}")
            return []
    
    def test_mark_notification_as_viewed(self, notification_id):
        """Test 2: Mark Notification as Viewed - /api/user/{user_id}/system-notifications/{notification_id}/view"""
        try:
            response = requests.post(f"{API_BASE}/user/{self.test_user_id}/system-notifications/{notification_id}/view")
            
            if response.status_code == 200:
                self.log_result("Mark Notification as Viewed", True, 
                              f"Successfully marked notification {notification_id} as viewed")
                
                # Verify notification is no longer returned for user
                response = requests.get(f"{API_BASE}/user/{self.test_user_id}/system-notifications")
                if response.status_code == 200:
                    new_notifications = response.json().get("notifications", [])
                    viewed_notification_still_present = any(n["id"] == notification_id for n in new_notifications)
                    
                    if not viewed_notification_still_present:
                        self.log_result("Notification Filtering After View", True, 
                                      "Viewed notification correctly filtered out from user notifications")
                    else:
                        self.log_result("Notification Filtering After View", False, 
                                      "Viewed notification still appears in user notifications")
                        
                return True
            else:
                self.log_result("Mark Notification as Viewed", False, 
                              f"Failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Mark Notification as Viewed", False, f"Exception: {str(e)}")
            return False
    
    def test_event_trigger_logic(self):
        """Test 4: Event Trigger Logic - Different event triggers"""
        try:
            # Test different event triggers
            event_triggers = ["login", "profile_update", "listing_published", "purchase_complete"]
            created_trigger_notifications = []
            
            for event_trigger in event_triggers:
                notification_data = {
                    "title": f"{event_trigger.title()} Event Notification",
                    "message": f"This notification is triggered by {event_trigger} events",
                    "type": "info",
                    "event_trigger": event_trigger,
                    "target_users": "all",
                    "show_duration": 3000,
                    "is_active": True,
                    "created_by": self.admin_user_id
                }
                
                response = requests.post(f"{API_BASE}/admin/system-notifications", json=notification_data)
                if response.status_code == 200:
                    notification_id = response.json().get("notification_id")
                    created_trigger_notifications.append(notification_id)
                    self.created_notifications.append(notification_id)
                else:
                    self.log_result(f"Create {event_trigger} Event Notification", False, 
                                  f"Failed to create: {response.status_code}")
                    return False
            
            self.log_result("Event Trigger Logic", True, 
                          f"Successfully created notifications for {len(event_triggers)} different event triggers")
            
            # Verify event triggers are stored correctly
            response = requests.get(f"{API_BASE}/admin/system-notifications")
            if response.status_code == 200:
                all_notifications = response.json().get("notifications", [])
                trigger_counts = {}
                
                for notification in all_notifications:
                    trigger = notification.get("event_trigger")
                    if trigger in event_triggers:
                        trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
                
                if len(trigger_counts) >= len(event_triggers):
                    self.log_result("Event Trigger Storage Verification", True, 
                                  f"Event triggers properly stored: {list(trigger_counts.keys())}")
                else:
                    self.log_result("Event Trigger Storage Verification", False, 
                                  f"Not all event triggers found: {list(trigger_counts.keys())}")
            
            return True
            
        except Exception as e:
            self.log_result("Event Trigger Logic", False, f"Exception: {str(e)}")
            return False
    
    def test_target_user_filtering(self):
        """Test 5: Target User Filtering - 'all' users vs 'specific_ids'"""
        try:
            # Create notification for all users
            all_users_notification = {
                "title": "All Users Notification",
                "message": "This notification is for all users",
                "type": "info",
                "event_trigger": "manual",
                "target_users": "all",
                "show_duration": 3000,
                "is_active": True,
                "created_by": self.admin_user_id
            }
            
            response = requests.post(f"{API_BASE}/admin/system-notifications", json=all_users_notification)
            if response.status_code != 200:
                self.log_result("Create All Users Notification", False, 
                              f"Failed to create: {response.status_code}")
                return False
            
            all_users_notification_id = response.json().get("notification_id")
            self.created_notifications.append(all_users_notification_id)
            
            # Create notification for specific users only
            specific_users_notification = {
                "title": "Specific Users Notification",
                "message": "This notification is only for specific users",
                "type": "warning",
                "event_trigger": "manual",
                "target_users": "specific_ids",
                "user_ids": [self.admin_user_id],  # Only for admin user
                "show_duration": 3000,
                "is_active": True,
                "created_by": self.admin_user_id
            }
            
            response = requests.post(f"{API_BASE}/admin/system-notifications", json=specific_users_notification)
            if response.status_code != 200:
                self.log_result("Create Specific Users Notification", False, 
                              f"Failed to create: {response.status_code}")
                return False
            
            specific_users_notification_id = response.json().get("notification_id")
            self.created_notifications.append(specific_users_notification_id)
            
            # Test user should see all users notification but NOT specific users notification
            response = requests.get(f"{API_BASE}/user/{self.test_user_id}/system-notifications")
            if response.status_code == 200:
                test_user_notifications = response.json().get("notifications", [])
                
                all_users_visible = any(n["id"] == all_users_notification_id for n in test_user_notifications)
                specific_users_visible = any(n["id"] == specific_users_notification_id for n in test_user_notifications)
                
                if all_users_visible and not specific_users_visible:
                    self.log_result("Target User Filtering - Test User", True, 
                                  "Test user correctly sees 'all' notification but not 'specific_ids' notification")
                else:
                    self.log_result("Target User Filtering - Test User", False, 
                                  f"Incorrect filtering: all_users_visible={all_users_visible}, specific_users_visible={specific_users_visible}")
                    return False
            
            # Admin user should see both notifications
            response = requests.get(f"{API_BASE}/user/{self.admin_user_id}/system-notifications")
            if response.status_code == 200:
                admin_notifications = response.json().get("notifications", [])
                
                all_users_visible = any(n["id"] == all_users_notification_id for n in admin_notifications)
                specific_users_visible = any(n["id"] == specific_users_notification_id for n in admin_notifications)
                
                if all_users_visible and specific_users_visible:
                    self.log_result("Target User Filtering - Admin User", True, 
                                  "Admin user correctly sees both 'all' and 'specific_ids' notifications")
                else:
                    self.log_result("Target User Filtering - Admin User", False, 
                                  f"Incorrect filtering: all_users_visible={all_users_visible}, specific_users_visible={specific_users_visible}")
                    return False
            
            self.log_result("Target User Filtering", True, 
                          "Target user filtering working correctly for both 'all' and 'specific_ids'")
            return True
            
        except Exception as e:
            self.log_result("Target User Filtering", False, f"Exception: {str(e)}")
            return False
    
    def test_json_serialization(self):
        """Test 6: JSON Serialization - UUIDs not ObjectIds"""
        try:
            response = requests.get(f"{API_BASE}/admin/system-notifications")
            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                
                if notifications:
                    # Check that IDs are UUIDs (strings) not ObjectIds
                    first_notification = notifications[0]
                    notification_id = first_notification.get("id")
                    
                    # UUID format validation
                    if isinstance(notification_id, str) and len(notification_id) == 36 and notification_id.count("-") == 4:
                        self.log_result("JSON Serialization - UUID Format", True, 
                                      f"Notification ID is proper UUID format: {notification_id}")
                    else:
                        self.log_result("JSON Serialization - UUID Format", False, 
                                      f"ID is not in UUID format: {notification_id}")
                        return False
                    
                    # Check that response is valid JSON
                    try:
                        json.dumps(data)
                        self.log_result("JSON Serialization - Valid JSON", True, 
                                      "Response is valid JSON and serializable")
                    except Exception as json_error:
                        self.log_result("JSON Serialization - Valid JSON", False, 
                                      f"JSON serialization error: {json_error}")
                        return False
                    
                    # Check for ObjectId patterns (should not exist)
                    response_text = response.text
                    if "ObjectId" in response_text or "$oid" in response_text:
                        self.log_result("JSON Serialization - No ObjectIds", False, 
                                      "Response contains ObjectId patterns")
                        return False
                    else:
                        self.log_result("JSON Serialization - No ObjectIds", True, 
                                      "Response does not contain ObjectId patterns")
                    
                    return True
                else:
                    self.log_result("JSON Serialization", False, "No notifications to test serialization")
                    return False
            else:
                self.log_result("JSON Serialization", False, f"Failed to get notifications: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("JSON Serialization", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up created test notifications"""
        try:
            cleanup_count = 0
            for notification_id in self.created_notifications:
                try:
                    response = requests.delete(f"{API_BASE}/admin/system-notifications/{notification_id}")
                    if response.status_code == 200:
                        cleanup_count += 1
                except:
                    pass  # Continue cleanup even if some fail
            
            self.log_result("Cleanup Test Data", True, f"Cleaned up {cleanup_count}/{len(self.created_notifications)} notifications")
            
        except Exception as e:
            self.log_result("Cleanup Test Data", False, f"Exception: {str(e)}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive system notification tests"""
        print("=" * 100)
        print("SYSTEM NOTIFICATIONS MANAGER COMPREHENSIVE BACKEND TESTING")
        print("=" * 100)
        print("Testing the complete system notification flow as requested in review:")
        print("1. GET System Notifications for User: /api/user/{user_id}/system-notifications")
        print("2. Mark Notification as Viewed: /api/user/{user_id}/system-notifications/{notification_id}/view")
        print("3. System Notification Creation: /api/admin/system-notifications POST")
        print("4. Event Trigger Logic: Different event triggers (manual, login, profile_update, etc.)")
        print("5. Target User Filtering: 'all' users vs 'specific_ids'")
        print("6. JSON Serialization: UUIDs not ObjectIds")
        print("=" * 100)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print()
        
        # Setup
        if not self.setup_test_environment():
            print("❌ CRITICAL: Failed to setup test environment. Aborting tests.")
            return False
        
        # Test 3: Create system notification first (needed for other tests)
        notification_id = self.test_system_notification_creation()
        if not notification_id:
            print("❌ CRITICAL: Failed to create test notification. Some tests may fail.")
        
        # Test 1: Get system notifications for user
        notifications = self.test_get_system_notifications_for_user()
        
        # Test 2: Mark notification as viewed (if we have notifications)
        if notifications and notification_id:
            # Use the notification we just created
            self.test_mark_notification_as_viewed(notification_id)
        elif notifications:
            # Use any available notification
            self.test_mark_notification_as_viewed(notifications[0]["id"])
        
        # Test 4: Event trigger logic
        self.test_event_trigger_logic()
        
        # Test 5: Target user filtering
        self.test_target_user_filtering()
        
        # Test 6: JSON serialization
        self.test_json_serialization()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("=" * 100)
        print("SYSTEM NOTIFICATIONS COMPREHENSIVE TESTING SUMMARY")
        print("=" * 100)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        print(f"Tests Passed: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
        
        print()
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL SYSTEM NOTIFICATION COMPREHENSIVE TESTS PASSED!")
            print("✅ System notification flow from creation to user display is working correctly")
            print("✅ Event triggers are properly handled")
            print("✅ Target user filtering is functional")
            print("✅ JSON serialization uses UUIDs correctly")
            return True
        else:
            print(f"⚠️  {self.total_tests - self.passed_tests} TESTS FAILED")
            print("❌ Some system notification functionality needs attention")
            return False

def main():
    """Main test execution"""
    tester = SystemNotificationsComprehensiveTest()
    success = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()