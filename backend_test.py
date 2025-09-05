#!/usr/bin/env python3
"""
SYSTEM NOTIFICATIONS CLEANUP EXECUTION AND VERIFICATION
Backend API Testing for Cataloro Marketplace

This test focuses on:
1. Execute cleanup endpoint - call /api/admin/cleanup-system-notifications POST
2. Verify cleanup results - check how many notifications were removed
3. Test clean separation after cleanup - ensure regular notifications are clean
4. Verify system notifications still work for toast display
5. Test multiple users to ensure cleanup worked across all users
6. Complete separation verification between system and regular notifications
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

class SystemNotificationsTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_user_id = None
        self.admin_user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def setup_test_user(self):
        """Create or login test user"""
        try:
            # Try to login first
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                user_data = response.json()
                self.test_user_id = user_data["user"]["id"]
                self.log_result("User Setup", True, f"Test user logged in successfully: {self.test_user_id}")
                return True
            else:
                # Create new user
                register_data = {
                    "username": f"system_test_user_{int(time.time())}",
                    "email": TEST_USER_EMAIL,
                    "full_name": "System Test User",
                    "password": TEST_USER_PASSWORD
                }
                
                response = self.session.post(f"{BASE_URL}/auth/register", json=register_data)
                if response.status_code == 200:
                    # Login after registration
                    login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
                    if login_response.status_code == 200:
                        user_data = login_response.json()
                        self.test_user_id = user_data["user"]["id"]
                        self.log_result("User Setup", True, f"Test user created and logged in: {self.test_user_id}")
                        return True
                
                self.log_result("User Setup", False, "Failed to create or login test user", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("User Setup", False, f"Exception during user setup: {str(e)}")
            return False
    
    def setup_admin_user(self):
        """Login admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                user_data = response.json()
                self.admin_user_id = user_data["user"]["id"]
                self.log_result("Admin Setup", True, f"Admin user logged in successfully: {self.admin_user_id}")
                return True
            else:
                self.log_result("Admin Setup", False, "Failed to login admin user", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Setup", False, f"Exception during admin setup: {str(e)}")
            return False
    
    def test_cleanup_endpoint_execution(self):
        """Test 1: Execute cleanup endpoint - call /api/admin/cleanup-system-notifications POST"""
        try:
            # First, check current state of notifications before cleanup
            response = self.session.get(f"{BASE_URL}/user/{self.test_user_id}/notifications")
            
            if response.status_code == 200:
                notifications_before = response.json()
                system_notifications_before = []
                
                for notification in notifications_before:
                    # Check for system notification indicators
                    if ("system_notification_id" in notification or 
                        "Welcome back!" in notification.get("message", "") or
                        "Endpoint Test" in notification.get("title", "") or
                        notification.get("type") == "system"):
                        system_notifications_before.append(notification)
                
                self.log_result("Pre-Cleanup Check", True, 
                              f"Found {len(system_notifications_before)} system notifications before cleanup",
                              {"total_notifications": len(notifications_before), 
                               "system_notifications": len(system_notifications_before)})
                
                # Execute the cleanup endpoint
                cleanup_response = self.session.post(f"{BASE_URL}/admin/cleanup-system-notifications")
                
                if cleanup_response.status_code == 200:
                    cleanup_result = cleanup_response.json()
                    removed_count = cleanup_result.get("removed_count", 0)
                    
                    self.log_result("Cleanup Endpoint Execution", True, 
                                  f"Cleanup endpoint executed successfully - removed {removed_count} notifications",
                                  {"cleanup_result": cleanup_result})
                    
                    # Verify cleanup results
                    post_cleanup_response = self.session.get(f"{BASE_URL}/user/{self.test_user_id}/notifications")
                    
                    if post_cleanup_response.status_code == 200:
                        notifications_after = post_cleanup_response.json()
                        system_notifications_after = []
                        
                        for notification in notifications_after:
                            if ("system_notification_id" in notification or 
                                "Welcome back!" in notification.get("message", "") or
                                "Endpoint Test" in notification.get("title", "") or
                                notification.get("type") == "system"):
                                system_notifications_after.append(notification)
                        
                        if len(system_notifications_after) == 0:
                            self.log_result("Cleanup Verification", True, 
                                          f"Cleanup successful - no system notifications remain in regular notifications",
                                          {"notifications_before": len(notifications_before),
                                           "notifications_after": len(notifications_after),
                                           "system_notifications_removed": len(system_notifications_before)})
                            return True
                        else:
                            self.log_result("Cleanup Verification", False, 
                                          f"Cleanup incomplete - {len(system_notifications_after)} system notifications still remain",
                                          {"remaining_system_notifications": system_notifications_after})
                            return False
                    else:
                        self.log_result("Cleanup Verification", False, 
                                      "Failed to retrieve notifications after cleanup")
                        return False
                else:
                    self.log_result("Cleanup Endpoint Execution", False, 
                                  f"Cleanup endpoint failed with status {cleanup_response.status_code}",
                                  {"response": cleanup_response.text})
                    return False
            else:
                self.log_result("Pre-Cleanup Check", False, 
                              "Failed to retrieve user notifications before cleanup", 
                              {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Cleanup Endpoint Execution", False, f"Exception during cleanup execution: {str(e)}")
            return False
    
    def test_system_notifications_endpoint(self):
        """Test 2: System notifications endpoint - verify /api/user/{user_id}/system-notifications"""
        try:
            response = self.session.get(f"{BASE_URL}/user/{self.test_user_id}/system-notifications")
            
            if response.status_code == 200:
                system_notifications = response.json()
                
                # Verify response structure
                if "notifications" in system_notifications:
                    notifications_list = system_notifications["notifications"]
                    self.log_result("System Notifications Endpoint", True, 
                                  f"System notifications endpoint working - found {len(notifications_list)} notifications",
                                  {"notifications_count": len(notifications_list)})
                    
                    # Verify notification structure
                    if notifications_list:
                        sample_notification = notifications_list[0]
                        required_fields = ["id", "title", "message", "type"]
                        missing_fields = [field for field in required_fields if field not in sample_notification]
                        
                        if not missing_fields:
                            self.log_result("System Notifications Structure", True, 
                                          "System notification structure is correct")
                        else:
                            self.log_result("System Notifications Structure", False, 
                                          f"Missing required fields: {missing_fields}",
                                          {"sample_notification": sample_notification})
                    
                    return True
                else:
                    self.log_result("System Notifications Endpoint", False, 
                                  "Invalid response structure - missing 'notifications' field",
                                  {"response": system_notifications})
                    return False
            else:
                self.log_result("System Notifications Endpoint", False, 
                              f"System notifications endpoint failed with status {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("System Notifications Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_regular_notifications_endpoint(self):
        """Test 3: Regular notifications endpoint - verify /api/user/{user_id}/notifications returns ONLY regular notifications"""
        try:
            response = self.session.get(f"{BASE_URL}/user/{self.test_user_id}/notifications")
            
            if response.status_code == 200:
                notifications = response.json()
                
                # Check that no notifications have system_notification_id field
                system_notifications_found = []
                for notification in notifications:
                    if "system_notification_id" in notification:
                        system_notifications_found.append(notification)
                
                if not system_notifications_found:
                    self.log_result("Regular Notifications Separation", True, 
                                  f"Regular notifications endpoint properly separated - {len(notifications)} regular notifications, 0 system notifications")
                    return True
                else:
                    self.log_result("Regular Notifications Separation", False, 
                                  f"Found {len(system_notifications_found)} system notifications in regular notifications endpoint",
                                  {"system_notifications": system_notifications_found})
                    return False
            else:
                self.log_result("Regular Notifications Endpoint", False, 
                              f"Regular notifications endpoint failed with status {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Regular Notifications Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_multiple_users_cleanup_verification(self):
        """Test 4: Test multiple users to ensure cleanup worked across all users"""
        try:
            # Create a second test user
            test_user_2_email = "system_test_user_2@example.com"
            register_data = {
                "username": f"system_test_user_2_{int(time.time())}",
                "email": test_user_2_email,
                "full_name": "System Test User 2",
                "password": TEST_USER_PASSWORD
            }
            
            register_response = self.session.post(f"{BASE_URL}/auth/register", json=register_data)
            
            if register_response.status_code == 200:
                # Login the second user
                login_data = {
                    "email": test_user_2_email,
                    "password": TEST_USER_PASSWORD
                }
                
                login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
                
                if login_response.status_code == 200:
                    user_2_data = login_response.json()
                    user_2_id = user_2_data["user"]["id"]
                    
                    # Check notifications for user 2
                    user_2_notifications_response = self.session.get(f"{BASE_URL}/user/{user_2_id}/notifications")
                    
                    if user_2_notifications_response.status_code == 200:
                        user_2_notifications = user_2_notifications_response.json()
                        system_notifications_user_2 = []
                        
                        for notification in user_2_notifications:
                            if ("system_notification_id" in notification or 
                                "Welcome back!" in notification.get("message", "") or
                                "Endpoint Test" in notification.get("title", "") or
                                notification.get("type") == "system"):
                                system_notifications_user_2.append(notification)
                        
                        # Also check admin user notifications
                        admin_notifications_response = self.session.get(f"{BASE_URL}/user/{self.admin_user_id}/notifications")
                        
                        if admin_notifications_response.status_code == 200:
                            admin_notifications = admin_notifications_response.json()
                            system_notifications_admin = []
                            
                            for notification in admin_notifications:
                                if ("system_notification_id" in notification or 
                                    "Welcome back!" in notification.get("message", "") or
                                    "Endpoint Test" in notification.get("title", "") or
                                    notification.get("type") == "system"):
                                    system_notifications_admin.append(notification)
                            
                            if len(system_notifications_user_2) == 0 and len(system_notifications_admin) == 0:
                                self.log_result("Multiple Users Cleanup Verification", True, 
                                              f"Cleanup successful across all users - no system notifications found",
                                              {"user_1_id": self.test_user_id,
                                               "user_2_id": user_2_id,
                                               "admin_id": self.admin_user_id,
                                               "user_2_notifications": len(user_2_notifications),
                                               "admin_notifications": len(admin_notifications)})
                                return True
                            else:
                                self.log_result("Multiple Users Cleanup Verification", False, 
                                              f"System notifications still found in some users",
                                              {"user_2_system_notifications": len(system_notifications_user_2),
                                               "admin_system_notifications": len(system_notifications_admin)})
                                return False
                        else:
                            self.log_result("Multiple Users Cleanup Verification", False, 
                                          "Failed to retrieve admin notifications")
                            return False
                    else:
                        self.log_result("Multiple Users Cleanup Verification", False, 
                                      "Failed to retrieve user 2 notifications")
                        return False
                else:
                    self.log_result("Multiple Users Cleanup Verification", False, 
                                  "Failed to login second test user")
                    return False
            else:
                self.log_result("Multiple Users Cleanup Verification", False, 
                              "Failed to create second test user")
                return False
                
        except Exception as e:
            self.log_result("Multiple Users Cleanup Verification", False, f"Exception: {str(e)}")
            return False

    def test_system_notification_toast_functionality(self):
        """Test 5: Verify system notifications still work for toast display"""
        try:
            # First, create a system notification via admin endpoint
            system_notification_data = {
                "title": "Test System Notification",
                "message": "This is a test system notification for separation testing",
                "type": "info",
                "event_trigger": "login",
                "target_users": "all",
                "is_active": True,
                "show_duration": 5000,
                "auto_dismiss": True
            }
            
            response = self.session.post(f"{BASE_URL}/admin/system-notifications", json=system_notification_data)
            
            if response.status_code == 200:
                created_notification = response.json()
                notification_id = created_notification.get("notification_id")
                
                self.log_result("System Notification Creation", True, 
                              f"System notification created successfully: {notification_id}")
                
                # Now trigger a login event to test the notification system
                login_data = {
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                }
                
                login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
                
                if login_response.status_code == 200:
                    # Wait a moment for notification processing
                    time.sleep(2)
                    
                    # Check system notifications endpoint - should show the notification
                    system_notif_response = self.session.get(f"{BASE_URL}/user/{self.test_user_id}/system-notifications")
                    
                    # Check regular notifications endpoint - should NOT show the notification
                    regular_notif_response = self.session.get(f"{BASE_URL}/user/{self.test_user_id}/notifications")
                    
                    if system_notif_response.status_code == 200 and regular_notif_response.status_code == 200:
                        system_notifications = system_notif_response.json().get("notifications", [])
                        regular_notifications = regular_notif_response.json()
                        
                        # Check if our test notification appears in system notifications
                        test_notification_in_system = any(
                            notif.get("title") == "Test System Notification" 
                            for notif in system_notifications
                        )
                        
                        # Check if our test notification appears in regular notifications (it shouldn't)
                        test_notification_in_regular = any(
                            notif.get("title") == "Test System Notification" 
                            for notif in regular_notifications
                        )
                        
                        if test_notification_in_system and not test_notification_in_regular:
                            self.log_result("System Notification Triggering", True, 
                                          "System notification correctly appears in system endpoint but not in regular endpoint")
                            return True
                        else:
                            self.log_result("System Notification Triggering", False, 
                                          f"Notification separation failed - in_system: {test_notification_in_system}, in_regular: {test_notification_in_regular}")
                            return False
                    else:
                        self.log_result("System Notification Triggering", False, 
                                      "Failed to retrieve notifications after login trigger")
                        return False
                else:
                    self.log_result("System Notification Triggering", False, 
                                  "Failed to trigger login event")
                    return False
            else:
                self.log_result("System Notification Creation", False, 
                              f"Failed to create system notification: {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("System Notification Creation/Triggering", False, f"Exception: {str(e)}")
            return False
    
    def test_database_collections_verification(self):
        """Test 5: Verify database collections structure and separation"""
        try:
            # Test system notifications collection via admin endpoint
            admin_system_notif_response = self.session.get(f"{BASE_URL}/admin/system-notifications")
            
            if admin_system_notif_response.status_code == 200:
                admin_notifications = admin_system_notif_response.json()
                
                self.log_result("System Notifications Collection", True, 
                              f"System notifications collection accessible - found {len(admin_notifications.get('notifications', []))} notifications")
                
                # Verify that system notifications have proper structure
                if admin_notifications.get("notifications"):
                    sample_system_notif = admin_notifications["notifications"][0]
                    system_fields = ["id", "title", "message", "type", "event_trigger", "target_users", "is_active"]
                    missing_system_fields = [field for field in system_fields if field not in sample_system_notif]
                    
                    if not missing_system_fields:
                        self.log_result("System Notifications Schema", True, 
                                      "System notifications have correct schema")
                    else:
                        self.log_result("System Notifications Schema", False, 
                                      f"Missing system notification fields: {missing_system_fields}")
                
                # Test regular notifications collection
                regular_notif_response = self.session.get(f"{BASE_URL}/user/{self.test_user_id}/notifications")
                
                if regular_notif_response.status_code == 200:
                    regular_notifications = regular_notif_response.json()
                    
                    self.log_result("Regular Notifications Collection", True, 
                                  f"Regular notifications collection accessible - found {len(regular_notifications)} notifications")
                    
                    # Verify separation - no system_notification_id in regular notifications
                    system_notif_ids_in_regular = [
                        notif.get("system_notification_id") 
                        for notif in regular_notifications 
                        if "system_notification_id" in notif
                    ]
                    
                    if not system_notif_ids_in_regular:
                        self.log_result("Collections Separation", True, 
                                      "Database collections properly separated - no system notification IDs in regular notifications")
                        return True
                    else:
                        self.log_result("Collections Separation", False, 
                                      f"Found {len(system_notif_ids_in_regular)} system notification references in regular notifications",
                                      {"system_notification_ids": system_notif_ids_in_regular})
                        return False
                else:
                    self.log_result("Regular Notifications Collection", False, 
                                  f"Failed to access regular notifications: {regular_notif_response.status_code}")
                    return False
            else:
                self.log_result("System Notifications Collection", False, 
                              f"Failed to access system notifications collection: {admin_system_notif_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Database Collections Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_notification_view_tracking(self):
        """Test 6: Verify notification view tracking works correctly"""
        try:
            # Get system notifications
            response = self.session.get(f"{BASE_URL}/user/{self.test_user_id}/system-notifications")
            
            if response.status_code == 200:
                system_notifications = response.json().get("notifications", [])
                
                if system_notifications:
                    # Mark first notification as viewed
                    notification_id = system_notifications[0]["id"]
                    
                    view_response = self.session.post(f"{BASE_URL}/user/{self.test_user_id}/system-notifications/{notification_id}/view")
                    
                    if view_response.status_code == 200:
                        # Wait a moment for processing
                        time.sleep(1)
                        
                        # Get notifications again - the viewed notification should be filtered out
                        updated_response = self.session.get(f"{BASE_URL}/user/{self.test_user_id}/system-notifications")
                        
                        if updated_response.status_code == 200:
                            updated_notifications = updated_response.json().get("notifications", [])
                            
                            # Check if the viewed notification is no longer in the list
                            viewed_notification_still_present = any(
                                notif["id"] == notification_id for notif in updated_notifications
                            )
                            
                            if not viewed_notification_still_present:
                                self.log_result("Notification View Tracking", True, 
                                              "Viewed notifications correctly filtered out from system notifications")
                                return True
                            else:
                                self.log_result("Notification View Tracking", False, 
                                              "Viewed notification still appears in system notifications list")
                                return False
                        else:
                            self.log_result("Notification View Tracking", False, 
                                          "Failed to retrieve updated notifications")
                            return False
                    else:
                        self.log_result("Notification View Tracking", False, 
                                      f"Failed to mark notification as viewed: {view_response.status_code}")
                        return False
                else:
                    self.log_result("Notification View Tracking", True, 
                                  "No system notifications available for view tracking test")
                    return True
            else:
                self.log_result("Notification View Tracking", False, 
                              f"Failed to retrieve system notifications: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Notification View Tracking", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all system notifications cleanup execution tests"""
        print("🧹 SYSTEM NOTIFICATIONS CLEANUP EXECUTION AND VERIFICATION")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_user():
            print("❌ Failed to setup test user - aborting tests")
            return False
        
        if not self.setup_admin_user():
            print("❌ Failed to setup admin user - aborting tests")
            return False
        
        # Run tests
        tests = [
            self.test_cleanup_endpoint_execution,
            self.test_system_notifications_endpoint,
            self.test_regular_notifications_endpoint,
            self.test_multiple_users_cleanup_verification,
            self.test_system_notification_toast_functionality,
            self.test_database_collections_verification
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("✅ ALL TESTS PASSED - System notifications separation is working correctly")
        else:
            print("❌ SOME TESTS FAILED - System notifications separation needs attention")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']} - {result['message']}")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = SystemNotificationsTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 SYSTEM NOTIFICATIONS SEPARATION TESTING COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n⚠️  SYSTEM NOTIFICATIONS SEPARATION TESTING COMPLETED WITH ISSUES")
        sys.exit(1)

if __name__ == "__main__":
    main()