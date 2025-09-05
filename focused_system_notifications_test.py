#!/usr/bin/env python3
"""
Focused System Notifications Manager Testing Suite
Tests all CRUD operations and event triggering functionality as requested in review
"""

import requests
import json
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://cataloro-marketplace-3.preview.emergentagent.com')
BASE_URL = f"{BACKEND_URL}/api"

class FocusedSystemNotificationsTest:
    def __init__(self):
        self.test_notification_id = None
        self.test_user_id = None
        self.results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_1_get_system_notifications(self):
        """Test 1: GET /api/admin/system-notifications endpoint - should return list of notifications"""
        try:
            response = requests.get(f"{BASE_URL}/admin/system-notifications")
            
            if response.status_code == 200:
                data = response.json()
                if "notifications" in data and isinstance(data["notifications"], list):
                    notifications = data["notifications"]
                    self.log_result(
                        "1. GET System Notifications List",
                        True,
                        f"Successfully retrieved {len(notifications)} notifications",
                        f"Response structure valid with 'notifications' array"
                    )
                    
                    # Check if notifications have event_trigger field
                    if notifications:
                        sample_notif = notifications[0]
                        has_event_trigger = "event_trigger" in sample_notif
                        self.log_result(
                            "1a. Event Trigger Field Present",
                            has_event_trigger,
                            f"Event trigger field present: {has_event_trigger}",
                            f"Sample notification fields: {list(sample_notif.keys())}"
                        )
                    
                    return True
                else:
                    self.log_result(
                        "1. GET System Notifications List",
                        False,
                        "Invalid response structure",
                        f"Expected 'notifications' key, got: {list(data.keys())}"
                    )
                    return False
            else:
                self.log_result(
                    "1. GET System Notifications List",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(
                "1. GET System Notifications List",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_2_create_system_notification(self):
        """Test 2: POST /api/admin/system-notifications endpoint - create a test notification with event_trigger field"""
        try:
            test_notification = {
                "title": "Test System Notification - Event Trigger Test",
                "message": "This notification tests the event_trigger functionality for login events",
                "type": "success",
                "event_trigger": "login",  # Key field being tested
                "target_users": "all",
                "show_duration": 5000,
                "delay_before_show": 0,
                "is_active": True,
                "auto_dismiss": True,
                "created_by": "test_admin"
            }
            
            response = requests.post(
                f"{BASE_URL}/admin/system-notifications",
                json=test_notification
            )
            
            if response.status_code == 200:
                data = response.json()
                if "notification_id" in data:
                    self.test_notification_id = data["notification_id"]
                    self.log_result(
                        "2. POST Create System Notification",
                        True,
                        f"Successfully created notification with ID: {self.test_notification_id}",
                        f"Event trigger set to: {test_notification['event_trigger']}"
                    )
                    return True
                else:
                    self.log_result(
                        "2. POST Create System Notification",
                        False,
                        "No notification_id in response",
                        data
                    )
                    return False
            else:
                self.log_result(
                    "2. POST Create System Notification",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(
                "2. POST Create System Notification",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_3_update_system_notification(self):
        """Test 3: PUT /api/admin/system-notifications/{id} endpoint - update the notification including event_trigger"""
        if not self.test_notification_id:
            self.log_result(
                "3. PUT Update System Notification",
                False,
                "No test notification ID available from previous test"
            )
            return False
            
        try:
            update_data = {
                "title": "Updated Test System Notification - Event Trigger Changed",
                "message": "This notification has been updated with a new event trigger type",
                "type": "info",
                "event_trigger": "profile_update",  # Changed from "login" to "profile_update"
                "target_users": "all",
                "show_duration": 7000,
                "is_active": True
            }
            
            response = requests.put(
                f"{BASE_URL}/admin/system-notifications/{self.test_notification_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                self.log_result(
                    "3. PUT Update System Notification",
                    True,
                    f"Successfully updated notification {self.test_notification_id}",
                    f"Event trigger changed from 'login' to '{update_data['event_trigger']}'"
                )
                return True
            else:
                self.log_result(
                    "3. PUT Update System Notification",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(
                "3. PUT Update System Notification",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_4_verify_event_trigger_persistence(self):
        """Test 4: Verify that event_trigger field is properly saved and retrieved"""
        try:
            response = requests.get(f"{BASE_URL}/admin/system-notifications")
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                
                # Find our test notification
                test_notification = None
                for notif in notifications:
                    if notif.get("id") == self.test_notification_id:
                        test_notification = notif
                        break
                
                if test_notification:
                    event_trigger = test_notification.get("event_trigger")
                    expected_trigger = "profile_update"  # Should be updated value from test 3
                    
                    if event_trigger == expected_trigger:
                        self.log_result(
                            "4. Verify Event Trigger Persistence",
                            True,
                            f"Event trigger correctly persisted: {event_trigger}",
                            f"All notification fields: {list(test_notification.keys())}"
                        )
                        return True
                    else:
                        self.log_result(
                            "4. Verify Event Trigger Persistence",
                            False,
                            f"Event trigger mismatch. Expected: {expected_trigger}, Got: {event_trigger}",
                            test_notification
                        )
                        return False
                else:
                    self.log_result(
                        "4. Verify Event Trigger Persistence",
                        False,
                        f"Test notification {self.test_notification_id} not found in list"
                    )
                    return False
            else:
                self.log_result(
                    "4. Verify Event Trigger Persistence",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(
                "4. Verify Event Trigger Persistence",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_5_create_different_event_triggers(self):
        """Test 5: Test creating notifications with different event trigger types"""
        event_triggers = ["login", "profile_update", "listing_published", "purchase_complete", "manual"]
        created_notifications = []
        
        try:
            for i, trigger in enumerate(event_triggers):
                notification_data = {
                    "title": f"Test Notification - {trigger.title()} Event",
                    "message": f"This notification is triggered by {trigger} events",
                    "type": "info",
                    "event_trigger": trigger,
                    "target_users": "all",
                    "is_active": True
                }
                
                response = requests.post(
                    f"{BASE_URL}/admin/system-notifications",
                    json=notification_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    notification_id = data.get("notification_id")
                    if notification_id:
                        created_notifications.append(notification_id)
                        self.log_result(
                            f"5.{i+1} Create {trigger} Event Notification",
                            True,
                            f"Created notification for {trigger} events",
                            f"Notification ID: {notification_id}"
                        )
                    else:
                        self.log_result(
                            f"5.{i+1} Create {trigger} Event Notification",
                            False,
                            "No notification_id in response"
                        )
                        return False
                else:
                    self.log_result(
                        f"5.{i+1} Create {trigger} Event Notification",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                    return False
            
            # Clean up created notifications
            for notif_id in created_notifications:
                requests.delete(f"{BASE_URL}/admin/system-notifications/{notif_id}")
            
            self.log_result(
                "5. Different Event Triggers Test",
                True,
                f"Successfully created and cleaned up {len(created_notifications)} notifications",
                f"Event triggers tested: {event_triggers}"
            )
            return True
            
        except Exception as e:
            # Clean up any created notifications
            for notif_id in created_notifications:
                try:
                    requests.delete(f"{BASE_URL}/admin/system-notifications/{notif_id}")
                except:
                    pass
            
            self.log_result(
                "5. Different Event Triggers Test",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_6_trigger_login_event(self):
        """Test 6: Test triggering notifications on login event"""
        try:
            # First create a notification for login event
            login_notification = {
                "title": "Welcome Back - Login Test",
                "message": "This notification should appear when you log in",
                "type": "success",
                "event_trigger": "login",
                "target_users": "all",
                "is_active": True
            }
            
            create_response = requests.post(
                f"{BASE_URL}/admin/system-notifications",
                json=login_notification
            )
            
            if create_response.status_code != 200:
                self.log_result(
                    "6. Test Login Event Trigger",
                    False,
                    "Failed to create login notification",
                    create_response.text
                )
                return False
            
            login_notif_id = create_response.json().get("notification_id")
            
            # Trigger login event by logging in
            login_data = {
                "email": "user@cataloro.com",
                "password": "password"
            }
            
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                json=login_data
            )
            
            if login_response.status_code == 200:
                user_data = login_response.json().get("user", {})
                user_id = user_data.get("id")
                
                if user_id:
                    # Check if user notifications were created (wait a moment for processing)
                    time.sleep(2)
                    
                    user_notifs_response = requests.get(f"{BASE_URL}/user/{user_id}/system-notifications")
                    
                    if user_notifs_response.status_code == 200:
                        user_notifications = user_notifs_response.json().get("notifications", [])
                        
                        # Look for our login notification
                        login_notif_found = False
                        for notif in user_notifications:
                            if notif.get("id") == login_notif_id:
                                login_notif_found = True
                                break
                        
                        self.log_result(
                            "6. Test Login Event Trigger",
                            login_notif_found,
                            f"Login event trigger {'worked' if login_notif_found else 'failed'}",
                            f"User notifications count: {len(user_notifications)}, Login notification found: {login_notif_found}"
                        )
                        
                        # Clean up
                        requests.delete(f"{BASE_URL}/admin/system-notifications/{login_notif_id}")
                        return login_notif_found
                    else:
                        self.log_result(
                            "6. Test Login Event Trigger",
                            False,
                            "Could not retrieve user notifications after login"
                        )
                        return False
                else:
                    self.log_result(
                        "6. Test Login Event Trigger",
                        False,
                        "No user ID in login response"
                    )
                    return False
            else:
                self.log_result(
                    "6. Test Login Event Trigger",
                    False,
                    f"Login failed: HTTP {login_response.status_code}",
                    login_response.text
                )
                return False
                
        except Exception as e:
            self.log_result(
                "6. Test Login Event Trigger",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def test_7_delete_system_notification(self):
        """Test 7: DELETE /api/admin/system-notifications/{id} endpoint - delete the test notification"""
        if not self.test_notification_id:
            self.log_result(
                "7. DELETE System Notification",
                False,
                "No test notification ID available"
            )
            return False
            
        try:
            response = requests.delete(f"{BASE_URL}/admin/system-notifications/{self.test_notification_id}")
            
            if response.status_code == 200:
                self.log_result(
                    "7. DELETE System Notification",
                    True,
                    f"Successfully deleted notification {self.test_notification_id}"
                )
                
                # Verify deletion by checking if notification still exists
                verify_response = requests.get(f"{BASE_URL}/admin/system-notifications")
                if verify_response.status_code == 200:
                    notifications = verify_response.json().get("notifications", [])
                    deleted_notif = None
                    for notif in notifications:
                        if notif.get("id") == self.test_notification_id:
                            deleted_notif = notif
                            break
                    
                    if deleted_notif is None:
                        self.log_result(
                            "7a. Verify Notification Deletion",
                            True,
                            "Notification successfully removed from database"
                        )
                    else:
                        self.log_result(
                            "7a. Verify Notification Deletion",
                            False,
                            "Notification still exists in database after deletion"
                        )
                
                return True
            else:
                self.log_result(
                    "7. DELETE System Notification",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(
                "7. DELETE System Notification",
                False,
                f"Request failed: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all system notification tests as specified in the review request"""
        print("=" * 80)
        print("FOCUSED SYSTEM NOTIFICATIONS MANAGER TESTING SUITE")
        print("Testing as requested in review:")
        print("1. GET /api/admin/system-notifications - return list of notifications")
        print("2. POST /api/admin/system-notifications - create notification with event_trigger")
        print("3. PUT /api/admin/system-notifications/{id} - update including event_trigger")
        print("4. DELETE /api/admin/system-notifications/{id} - delete notification")
        print("5. Verify event_trigger field persistence")
        print("6. Test triggering on different events (login, profile_update, etc.)")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Test sequence as requested in review
        tests = [
            self.test_1_get_system_notifications,
            self.test_2_create_system_notification,
            self.test_3_update_system_notification,
            self.test_4_verify_event_trigger_persistence,
            self.test_5_create_different_event_triggers,
            self.test_6_trigger_login_event,
            self.test_7_delete_system_notification
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL: {test.__name__} - Unexpected error: {str(e)}")
                failed += 1
            print("-" * 40)
        
        # Summary
        print("=" * 80)
        print("SYSTEM NOTIFICATIONS MANAGER TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("🎉 ALL SYSTEM NOTIFICATIONS TESTS PASSED!")
            print("✅ System Notifications Manager functionality is working correctly")
            print("✅ Event trigger functionality is operational")
            print("✅ CRUD operations are all functional")
        else:
            print(f"⚠️  {failed} TEST(S) FAILED")
            print("❌ Some System Notifications Manager functionality needs attention")
        
        print("=" * 80)
        
        return passed, failed, self.results

if __name__ == "__main__":
    tester = FocusedSystemNotificationsTest()
    passed, failed, results = tester.run_all_tests()
    
    # Save detailed results
    with open("/app/focused_system_notifications_test_results.json", "w") as f:
        json.dump({
            "summary": {
                "total_tests": passed + failed,
                "passed": passed,
                "failed": failed,
                "success_rate": (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0,
                "test_date": datetime.now().isoformat(),
                "focus": "System Notifications Manager CRUD and Event Triggering"
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: /app/focused_system_notifications_test_results.json")