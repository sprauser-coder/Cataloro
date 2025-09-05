#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM NOTIFICATIONS DATABASE CLEANUP TEST
Backend API Testing for Cataloro Marketplace

This test focuses on the specific review request:
1. Identify system notifications in user_notifications database with system_notification_id field
2. Remove system notifications from user_notifications collection 
3. Verify clean separation between system and regular notifications
4. Test system notification creation and toast display logic
5. Verify frontend will no longer see system notifications in regular notifications endpoint
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://cataloro-upgrade.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin123"

class SystemNotificationsCleanupTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_user_id = None
        self.test_results = []
        self.cleanup_results = []
        
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
    
    def get_all_users(self):
        """Get all users to check their notifications"""
        try:
            response = self.session.get(f"{BASE_URL}/admin/users")
            
            if response.status_code == 200:
                users = response.json()
                self.log_result("Get All Users", True, f"Retrieved {len(users)} users from database")
                return users
            else:
                self.log_result("Get All Users", False, f"Failed to get users: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_result("Get All Users", False, f"Exception: {str(e)}")
            return []
    
    def check_user_notifications_for_system_notifications(self, user_id, username="Unknown"):
        """Check a specific user's notifications for system notifications"""
        try:
            response = self.session.get(f"{BASE_URL}/user/{user_id}/notifications")
            
            if response.status_code == 200:
                notifications = response.json()
                system_notifications_found = []
                
                for notification in notifications:
                    # Check for system_notification_id field (indicates system notification incorrectly stored)
                    if "system_notification_id" in notification:
                        system_notifications_found.append({
                            "notification_id": notification.get("id"),
                            "system_notification_id": notification.get("system_notification_id"),
                            "title": notification.get("title"),
                            "message": notification.get("message"),
                            "type": notification.get("type"),
                            "created_at": notification.get("created_at")
                        })
                    
                    # Also check for system-related content in messages
                    message = notification.get("message", "").lower()
                    title = notification.get("title", "").lower()
                    if any(keyword in message or keyword in title for keyword in 
                           ["welcome back", "endpoint test", "system notification", "login notification"]):
                        if notification not in system_notifications_found:
                            system_notifications_found.append({
                                "notification_id": notification.get("id"),
                                "system_notification_id": notification.get("system_notification_id", "N/A"),
                                "title": notification.get("title"),
                                "message": notification.get("message"),
                                "type": notification.get("type"),
                                "created_at": notification.get("created_at"),
                                "reason": "System-related content detected"
                            })
                
                return {
                    "user_id": user_id,
                    "username": username,
                    "total_notifications": len(notifications),
                    "system_notifications_found": system_notifications_found,
                    "needs_cleanup": len(system_notifications_found) > 0
                }
            else:
                return {
                    "user_id": user_id,
                    "username": username,
                    "error": f"Failed to get notifications: {response.status_code}",
                    "needs_cleanup": False
                }
                
        except Exception as e:
            return {
                "user_id": user_id,
                "username": username,
                "error": f"Exception: {str(e)}",
                "needs_cleanup": False
            }
    
    def test_comprehensive_database_scan(self):
        """Test 1: Comprehensive scan of all users for system notifications in user_notifications"""
        try:
            users = self.get_all_users()
            if not users:
                self.log_result("Database Scan", False, "No users found or failed to retrieve users")
                return False
            
            total_system_notifications_found = 0
            users_needing_cleanup = []
            
            print(f"\n🔍 Scanning {len(users)} users for system notifications in regular notifications...")
            
            for user in users:
                user_id = user.get("id")
                username = user.get("username", "Unknown")
                
                if user_id:
                    result = self.check_user_notifications_for_system_notifications(user_id, username)
                    
                    if result["needs_cleanup"]:
                        users_needing_cleanup.append(result)
                        total_system_notifications_found += len(result["system_notifications_found"])
                        
                        print(f"   ⚠️  User {username} ({user_id}): {len(result['system_notifications_found'])} system notifications found")
                        for sys_notif in result["system_notifications_found"]:
                            print(f"      - {sys_notif['title']}: {sys_notif['message'][:50]}...")
                    else:
                        print(f"   ✅ User {username} ({user_id}): Clean (no system notifications)")
            
            if total_system_notifications_found > 0:
                self.log_result("Database Scan", False, 
                              f"Found {total_system_notifications_found} system notifications across {len(users_needing_cleanup)} users",
                              {"users_needing_cleanup": users_needing_cleanup})
                self.cleanup_results = users_needing_cleanup
                return False
            else:
                self.log_result("Database Scan", True, 
                              f"Database is clean - no system notifications found in user_notifications across {len(users)} users")
                return True
                
        except Exception as e:
            self.log_result("Database Scan", False, f"Exception during database scan: {str(e)}")
            return False
    
    def test_system_notifications_collection_structure(self):
        """Test 2: Verify system_notifications collection structure"""
        try:
            response = self.session.get(f"{BASE_URL}/admin/system-notifications")
            
            if response.status_code == 200:
                system_notifications = response.json()
                notifications_list = system_notifications.get("notifications", [])
                
                self.log_result("System Notifications Collection", True, 
                              f"System notifications collection accessible - found {len(notifications_list)} notifications")
                
                if notifications_list:
                    # Analyze structure
                    sample_notification = notifications_list[0]
                    required_fields = ["id", "title", "message", "type", "event_trigger", "target_users", "is_active"]
                    present_fields = [field for field in required_fields if field in sample_notification]
                    missing_fields = [field for field in required_fields if field not in sample_notification]
                    
                    self.log_result("System Notifications Schema", len(missing_fields) == 0, 
                                  f"Schema check - {len(present_fields)}/{len(required_fields)} required fields present",
                                  {"missing_fields": missing_fields, "sample": sample_notification})
                    
                    return len(missing_fields) == 0
                else:
                    self.log_result("System Notifications Schema", True, "No system notifications to analyze")
                    return True
            else:
                self.log_result("System Notifications Collection", False, 
                              f"Failed to access system notifications: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("System Notifications Collection", False, f"Exception: {str(e)}")
            return False
    
    def test_system_notification_creation_flow(self):
        """Test 3: Create system notification and verify it goes to correct collection"""
        try:
            # Create a test system notification
            test_notification = {
                "title": "Cleanup Test Notification",
                "message": "This is a test notification for cleanup verification",
                "type": "info",
                "event_trigger": "manual",
                "target_users": "all",
                "is_active": True,
                "show_duration": 5000,
                "auto_dismiss": True
            }
            
            response = self.session.post(f"{BASE_URL}/admin/system-notifications", json=test_notification)
            
            if response.status_code == 200:
                created_notification = response.json()
                notification_id = created_notification.get("notification_id")
                
                self.log_result("System Notification Creation", True, 
                              f"Test system notification created: {notification_id}")
                
                # Verify it appears in system notifications collection
                system_response = self.session.get(f"{BASE_URL}/admin/system-notifications")
                if system_response.status_code == 200:
                    system_notifications = system_response.json().get("notifications", [])
                    found_in_system = any(notif.get("title") == "Cleanup Test Notification" for notif in system_notifications)
                    
                    if found_in_system:
                        self.log_result("System Notification Storage", True, 
                                      "Test notification correctly stored in system_notifications collection")
                        
                        # Now check that it doesn't appear in any user's regular notifications
                        users = self.get_all_users()
                        found_in_user_notifications = False
                        
                        for user in users[:5]:  # Check first 5 users
                            user_id = user.get("id")
                            if user_id:
                                user_notif_response = self.session.get(f"{BASE_URL}/user/{user_id}/notifications")
                                if user_notif_response.status_code == 200:
                                    user_notifications = user_notif_response.json()
                                    if any(notif.get("title") == "Cleanup Test Notification" for notif in user_notifications):
                                        found_in_user_notifications = True
                                        break
                        
                        if not found_in_user_notifications:
                            self.log_result("System Notification Separation", True, 
                                          "Test notification correctly NOT stored in user_notifications")
                            return True
                        else:
                            self.log_result("System Notification Separation", False, 
                                          "Test notification incorrectly found in user_notifications")
                            return False
                    else:
                        self.log_result("System Notification Storage", False, 
                                      "Test notification not found in system_notifications collection")
                        return False
                else:
                    self.log_result("System Notification Storage", False, 
                                  "Failed to retrieve system notifications for verification")
                    return False
            else:
                self.log_result("System Notification Creation", False, 
                              f"Failed to create test notification: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("System Notification Creation Flow", False, f"Exception: {str(e)}")
            return False
    
    def test_system_notifications_endpoint_for_toast_display(self):
        """Test 4: Verify system notifications endpoint returns notifications for toast display"""
        try:
            # Test with admin user
            response = self.session.get(f"{BASE_URL}/user/{self.admin_user_id}/system-notifications")
            
            if response.status_code == 200:
                system_notifications = response.json()
                notifications_list = system_notifications.get("notifications", [])
                
                self.log_result("System Notifications Toast Endpoint", True, 
                              f"System notifications endpoint working - found {len(notifications_list)} notifications for toast display")
                
                # Verify structure for toast display
                if notifications_list:
                    sample_notification = notifications_list[0]
                    toast_fields = ["id", "title", "message", "type", "show_duration", "auto_dismiss"]
                    present_toast_fields = [field for field in toast_fields if field in sample_notification]
                    
                    self.log_result("Toast Display Structure", len(present_toast_fields) >= 4, 
                                  f"Toast display fields check - {len(present_toast_fields)}/{len(toast_fields)} fields present")
                
                return True
            else:
                self.log_result("System Notifications Toast Endpoint", False, 
                              f"System notifications endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("System Notifications Toast Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def generate_cleanup_report(self):
        """Generate detailed cleanup report"""
        if not self.cleanup_results:
            print("\n✅ NO CLEANUP NEEDED - Database is already clean")
            return
        
        print("\n" + "=" * 80)
        print("🧹 CLEANUP REPORT - SYSTEM NOTIFICATIONS IN USER_NOTIFICATIONS")
        print("=" * 80)
        
        total_notifications_to_clean = 0
        
        for user_result in self.cleanup_results:
            username = user_result["username"]
            user_id = user_result["user_id"]
            system_notifications = user_result["system_notifications_found"]
            
            print(f"\n👤 User: {username} ({user_id})")
            print(f"   System notifications to remove: {len(system_notifications)}")
            
            for i, sys_notif in enumerate(system_notifications, 1):
                print(f"   {i}. ID: {sys_notif['notification_id']}")
                print(f"      Title: {sys_notif['title']}")
                print(f"      Message: {sys_notif['message'][:100]}...")
                if sys_notif.get('system_notification_id') != 'N/A':
                    print(f"      System Notification ID: {sys_notif['system_notification_id']}")
                print(f"      Created: {sys_notif['created_at']}")
                if sys_notif.get('reason'):
                    print(f"      Reason: {sys_notif['reason']}")
                print()
            
            total_notifications_to_clean += len(system_notifications)
        
        print(f"📊 TOTAL CLEANUP REQUIRED:")
        print(f"   - Users affected: {len(self.cleanup_results)}")
        print(f"   - System notifications to remove: {total_notifications_to_clean}")
        print(f"   - Collections to clean: user_notifications")
        
        print(f"\n🔧 RECOMMENDED CLEANUP ACTIONS:")
        print(f"   1. Remove all notifications with 'system_notification_id' field from user_notifications collection")
        print(f"   2. Remove notifications with system-related content from user_notifications collection")
        print(f"   3. Verify system notifications only exist in system_notifications collection")
        print(f"   4. Test that frontend no longer shows system notifications in notifications center")
    
    def run_all_tests(self):
        """Run all system notifications cleanup tests"""
        print("🧹 SYSTEM NOTIFICATIONS DATABASE CLEANUP VERIFICATION")
        print("=" * 80)
        
        # Setup
        if not self.setup_admin_user():
            print("❌ Failed to setup admin user - aborting tests")
            return False
        
        # Run tests
        tests = [
            self.test_comprehensive_database_scan,
            self.test_system_notifications_collection_structure,
            self.test_system_notification_creation_flow,
            self.test_system_notifications_endpoint_for_toast_display
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
        
        # Generate cleanup report
        self.generate_cleanup_report()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("✅ ALL TESTS PASSED - System notifications separation is working correctly")
        else:
            print("❌ SOME TESTS FAILED - System notifications cleanup required")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']} - {result['message']}")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = SystemNotificationsCleanupTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 SYSTEM NOTIFICATIONS CLEANUP VERIFICATION COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n⚠️  SYSTEM NOTIFICATIONS CLEANUP VERIFICATION COMPLETED - ACTION REQUIRED")
        sys.exit(1)

if __name__ == "__main__":
    main()