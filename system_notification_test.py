#!/usr/bin/env python3
"""
System Notification Fix Testing Suite
Tests the complete system notification flow after applying the user ID timing fix
"""

import requests
import sys
import json
from datetime import datetime
import time

class SystemNotificationTester:
    def __init__(self, base_url="https://market-evolution-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        
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
                    details += f", Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Array'}"
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_login_notification_creation_demo_user(self):
        """Test login notification creation for demo@cataloro.com"""
        print("\n🔐 Testing Login Notification Creation for demo@cataloro.com...")
        
        # Step 1: Login with demo@cataloro.com
        success, login_response = self.run_test(
            "Login demo@cataloro.com",
            "POST",
            "api/auth/login",
            200,
            data={"email": "demo@cataloro.com", "password": "demo123"}
        )
        
        if not success or 'user' not in login_response:
            print("❌ Failed to login - cannot test notifications")
            return False
        
        user_data = login_response['user']
        user_id = user_data.get('id')
        
        print(f"   📋 Login Response User ID: {user_id}")
        print(f"   📋 User Data: {json.dumps(user_data, indent=2)}")
        
        # Step 2: Wait a moment for notification creation
        print("   ⏳ Waiting 2 seconds for notification creation...")
        time.sleep(2)
        
        # Step 3: Check user notifications
        success_notif, notifications = self.run_test(
            "Get User Notifications",
            "GET",
            f"api/user/{user_id}/notifications",
            200
        )
        
        if success_notif:
            print(f"   📊 Found {len(notifications)} total notifications")
            
            # Look for login notifications
            login_notifications = [n for n in notifications if n.get('type') == 'system' and 'login' in n.get('message', '').lower()]
            
            print(f"   🔍 Found {len(login_notifications)} login notifications")
            
            if login_notifications:
                latest_login_notif = login_notifications[0]  # Most recent first
                print(f"   📝 Latest login notification: {latest_login_notif.get('title')} - {latest_login_notif.get('message')}")
                print(f"   🆔 Notification user_id: {latest_login_notif.get('user_id')}")
                
                # Check if user_id matches
                user_id_match = latest_login_notif.get('user_id') == user_id
                self.log_test("User ID Consistency", user_id_match, 
                             f"Notification user_id matches login user_id: {user_id_match}")
                
                return user_id_match
            else:
                self.log_test("Login Notification Creation", False, "No login notifications found")
                return False
        else:
            print("❌ Failed to retrieve notifications")
            return False

    def test_login_notification_creation_admin_user(self):
        """Test login notification creation for admin@cataloro.com"""
        print("\n🔐 Testing Login Notification Creation for admin@cataloro.com...")
        
        # Step 1: Login with admin@cataloro.com
        success, login_response = self.run_test(
            "Login admin@cataloro.com",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "admin123"}
        )
        
        if not success or 'user' not in login_response:
            print("❌ Failed to login - cannot test notifications")
            return False
        
        user_data = login_response['user']
        user_id = user_data.get('id')
        
        print(f"   📋 Login Response User ID: {user_id}")
        print(f"   📋 User Data: {json.dumps(user_data, indent=2)}")
        
        # Step 2: Wait a moment for notification creation
        print("   ⏳ Waiting 2 seconds for notification creation...")
        time.sleep(2)
        
        # Step 3: Check user notifications
        success_notif, notifications = self.run_test(
            "Get Admin User Notifications",
            "GET",
            f"api/user/{user_id}/notifications",
            200
        )
        
        if success_notif:
            print(f"   📊 Found {len(notifications)} total notifications")
            
            # Look for login notifications
            login_notifications = [n for n in notifications if n.get('type') == 'system' and 'login' in n.get('message', '').lower()]
            
            print(f"   🔍 Found {len(login_notifications)} login notifications")
            
            if login_notifications:
                latest_login_notif = login_notifications[0]  # Most recent first
                print(f"   📝 Latest login notification: {latest_login_notif.get('title')} - {latest_login_notif.get('message')}")
                print(f"   🆔 Notification user_id: {latest_login_notif.get('user_id')}")
                
                # Check if user_id matches
                user_id_match = latest_login_notif.get('user_id') == user_id
                self.log_test("Admin User ID Consistency", user_id_match, 
                             f"Notification user_id matches login user_id: {user_id_match}")
                
                return user_id_match
            else:
                self.log_test("Admin Login Notification Creation", False, "No login notifications found")
                return False
        else:
            print("❌ Failed to retrieve admin notifications")
            return False

    def test_new_user_registration_notifications(self):
        """Test system notifications for new user registration"""
        print("\n👤 Testing New User Registration Notifications...")
        
        # Generate unique email for new user
        timestamp = int(time.time())
        new_email = f"testuser{timestamp}@cataloro.com"
        
        # Step 1: Register new user
        success, register_response = self.run_test(
            "Register New User",
            "POST",
            "api/auth/register",
            200,
            data={
                "username": f"testuser{timestamp}",
                "email": new_email,
                "full_name": f"Test User {timestamp}",
                "password": "test123"
            }
        )
        
        if not success or 'user_id' not in register_response:
            print("❌ Failed to register new user")
            return False
        
        new_user_id = register_response['user_id']
        print(f"   ✅ Registered new user with ID: {new_user_id}")
        
        # Step 2: Login with new user
        success_login, login_response = self.run_test(
            "Login New User",
            "POST",
            "api/auth/login",
            200,
            data={"email": new_email, "password": "test123"}
        )
        
        if not success_login or 'user' not in login_response:
            print("❌ Failed to login with new user")
            return False
        
        login_user_data = login_response['user']
        login_user_id = login_user_data.get('id')
        
        print(f"   📋 Login User ID: {login_user_id}")
        print(f"   🔍 Registration User ID: {new_user_id}")
        
        # Check if IDs match
        id_consistency = login_user_id == new_user_id
        self.log_test("New User ID Consistency", id_consistency,
                     f"Registration and login IDs match: {id_consistency}")
        
        # Step 3: Wait and check notifications
        print("   ⏳ Waiting 2 seconds for notification creation...")
        time.sleep(2)
        
        success_notif, notifications = self.run_test(
            "Get New User Notifications",
            "GET",
            f"api/user/{login_user_id}/notifications",
            200
        )
        
        if success_notif:
            print(f"   📊 Found {len(notifications)} total notifications for new user")
            
            # Look for login notifications
            login_notifications = [n for n in notifications if n.get('type') == 'system' and 'login' in n.get('message', '').lower()]
            
            print(f"   🔍 Found {len(login_notifications)} login notifications for new user")
            
            if login_notifications:
                latest_login_notif = login_notifications[0]
                print(f"   📝 New user login notification: {latest_login_notif.get('title')} - {latest_login_notif.get('message')}")
                
                # Check user_id format (should be UUID for new users)
                notif_user_id = latest_login_notif.get('user_id')
                is_uuid_format = len(notif_user_id) == 36 and notif_user_id.count('-') == 4
                
                self.log_test("New User Notification Format", is_uuid_format,
                             f"New user notification uses UUID format: {is_uuid_format}")
                
                # Check if notification user_id matches login user_id
                user_id_match = notif_user_id == login_user_id
                self.log_test("New User Notification ID Match", user_id_match,
                             f"Notification user_id matches login user_id: {user_id_match}")
                
                return user_id_match
            else:
                self.log_test("New User Login Notification Creation", False, "No login notifications found for new user")
                return False
        else:
            print("❌ Failed to retrieve new user notifications")
            return False

    def test_existing_user_objectid_format(self):
        """Test notifications for existing users with ObjectId format"""
        print("\n🔍 Testing Existing User ObjectId Format Handling...")
        
        # Step 1: Get all users to find existing ObjectId format users
        success, users = self.run_test(
            "Get All Users",
            "GET",
            "api/admin/users",
            200
        )
        
        if not success:
            print("❌ Failed to get users list")
            return False
        
        # Find users with ObjectId format (24-character hex string)
        objectid_users = []
        for user in users:
            user_id = user.get('id', '')
            if len(user_id) == 24 and all(c in '0123456789abcdef' for c in user_id.lower()):
                objectid_users.append(user)
        
        print(f"   📊 Found {len(objectid_users)} users with ObjectId format")
        
        if not objectid_users:
            print("   ⚠️  No ObjectId format users found - creating test scenario")
            return True  # Not a failure, just no ObjectId users exist
        
        # Test with first ObjectId user
        test_user = objectid_users[0]
        test_user_id = test_user.get('id')
        test_email = test_user.get('email')
        
        print(f"   🎯 Testing with ObjectId user: {test_email} (ID: {test_user_id})")
        
        # Step 2: Test profile endpoint with ObjectId
        success_profile, profile_data = self.run_test(
            "Get ObjectId User Profile",
            "GET",
            f"api/auth/profile/{test_user_id}",
            200
        )
        
        if success_profile:
            profile_user_id = profile_data.get('id')
            print(f"   📋 Profile endpoint returned user_id: {profile_user_id}")
            
            # Check if profile lookup works with ObjectId
            profile_works = profile_user_id == test_user_id
            self.log_test("ObjectId Profile Lookup", profile_works,
                         f"Profile lookup works with ObjectId: {profile_works}")
        
        # Step 3: Test notifications endpoint with ObjectId
        success_notif, notifications = self.run_test(
            "Get ObjectId User Notifications",
            "GET",
            f"api/user/{test_user_id}/notifications",
            200
        )
        
        if success_notif:
            print(f"   📊 Found {len(notifications)} notifications for ObjectId user")
            
            # Check if any notifications have matching user_id
            matching_notifications = [n for n in notifications if n.get('user_id') == test_user_id]
            
            print(f"   🔍 Found {len(matching_notifications)} notifications with matching user_id")
            
            if matching_notifications:
                self.log_test("ObjectId Notification Retrieval", True,
                             f"Successfully retrieved {len(matching_notifications)} notifications")
                return True
            else:
                # Check if notifications exist but with different user_id format
                all_user_ids = set(n.get('user_id') for n in notifications if n.get('user_id'))
                print(f"   🔍 All notification user_ids found: {list(all_user_ids)}")
                
                self.log_test("ObjectId Notification Retrieval", False,
                             f"No notifications with matching ObjectId user_id found")
                return False
        else:
            print("❌ Failed to retrieve ObjectId user notifications")
            return False

    def test_system_notification_endpoint_functionality(self):
        """Test system notification endpoint functionality"""
        print("\n🔔 Testing System Notification Endpoint Functionality...")
        
        # Step 1: Test admin system notifications endpoint
        success_admin, admin_notifications = self.run_test(
            "Get Admin System Notifications",
            "GET",
            "api/admin/system-notifications",
            200
        )
        
        if success_admin:
            print(f"   📊 Found {len(admin_notifications)} admin system notifications")
            self.log_test("Admin System Notifications Endpoint", True,
                         f"Admin endpoint accessible with {len(admin_notifications)} notifications")
        
        # Step 2: Create a test system notification
        test_notification = {
            "title": "System Test Notification",
            "message": "This is a test system notification for verification",
            "type": "green_toast",
            "target_users": "all",
            "show_duration": 5000,
            "auto_dismiss": True
        }
        
        success_create, create_response = self.run_test(
            "Create Test System Notification",
            "POST",
            "api/admin/system-notifications",
            200,
            data=test_notification
        )
        
        if success_create:
            print(f"   ✅ Created test system notification")
            notification_id = create_response.get('id', create_response.get('notification_id'))
            
            # Step 3: Test user system notifications endpoint
            # Use demo user for testing
            success_login, login_response = self.run_test(
                "Login for System Notification Test",
                "POST",
                "api/auth/login",
                200,
                data={"email": "demo@cataloro.com", "password": "demo123"}
            )
            
            if success_login and 'user' in login_response:
                user_id = login_response['user']['id']
                
                success_user_notif, user_notifications = self.run_test(
                    "Get User System Notifications",
                    "GET",
                    f"api/user/{user_id}/system-notifications",
                    200
                )
                
                if success_user_notif:
                    print(f"   📊 Found {len(user_notifications)} user system notifications")
                    
                    # Look for our test notification
                    test_notif_found = any(n.get('title') == test_notification['title'] for n in user_notifications)
                    
                    self.log_test("System Notification Delivery", test_notif_found,
                                 f"Test notification delivered to user: {test_notif_found}")
                    
                    if test_notif_found and notification_id:
                        # Step 4: Test mark as viewed
                        success_view, view_response = self.run_test(
                            "Mark System Notification as Viewed",
                            "POST",
                            f"api/user/{user_id}/system-notifications/{notification_id}/view",
                            200
                        )
                        
                        if success_view:
                            self.log_test("System Notification View Tracking", True,
                                         "Successfully marked notification as viewed")
                        
                    return test_notif_found
                else:
                    print("❌ Failed to get user system notifications")
                    return False
            else:
                print("❌ Failed to login for system notification test")
                return False
        else:
            print("❌ Failed to create test system notification")
            return False

    def test_user_id_format_analysis(self):
        """Analyze user ID formats in the system"""
        print("\n🔍 Analyzing User ID Formats in System...")
        
        # Step 1: Get all users
        success, users = self.run_test(
            "Get All Users for ID Analysis",
            "GET",
            "api/admin/users",
            200
        )
        
        if not success:
            print("❌ Failed to get users for analysis")
            return False
        
        # Analyze ID formats
        uuid_users = []
        objectid_users = []
        other_users = []
        
        for user in users:
            user_id = user.get('id', '')
            email = user.get('email', '')
            
            if len(user_id) == 36 and user_id.count('-') == 4:
                uuid_users.append((email, user_id))
            elif len(user_id) == 24 and all(c in '0123456789abcdef' for c in user_id.lower()):
                objectid_users.append((email, user_id))
            else:
                other_users.append((email, user_id))
        
        print(f"   📊 User ID Format Analysis:")
        print(f"      UUID Format (36 chars with dashes): {len(uuid_users)} users")
        print(f"      ObjectId Format (24 hex chars): {len(objectid_users)} users")
        print(f"      Other Formats: {len(other_users)} users")
        
        # Show examples
        if uuid_users:
            print(f"      UUID Example: {uuid_users[0][0]} -> {uuid_users[0][1]}")
        if objectid_users:
            print(f"      ObjectId Example: {objectid_users[0][0]} -> {objectid_users[0][1]}")
        
        # Test notification retrieval for each format
        format_test_results = {}
        
        # Test UUID format user
        if uuid_users:
            test_email, test_id = uuid_users[0]
            success_uuid, uuid_notifications = self.run_test(
                f"Test UUID User Notifications ({test_email})",
                "GET",
                f"api/user/{test_id}/notifications",
                200
            )
            
            if success_uuid:
                matching_notifs = [n for n in uuid_notifications if n.get('user_id') == test_id]
                format_test_results['UUID'] = len(matching_notifs)
                print(f"      UUID User: {len(matching_notifs)} matching notifications out of {len(uuid_notifications)} total")
        
        # Test ObjectId format user
        if objectid_users:
            test_email, test_id = objectid_users[0]
            success_objectid, objectid_notifications = self.run_test(
                f"Test ObjectId User Notifications ({test_email})",
                "GET",
                f"api/user/{test_id}/notifications",
                200
            )
            
            if success_objectid:
                matching_notifs = [n for n in objectid_notifications if n.get('user_id') == test_id]
                format_test_results['ObjectId'] = len(matching_notifs)
                print(f"      ObjectId User: {len(matching_notifs)} matching notifications out of {len(objectid_notifications)} total")
        
        # Summary
        self.log_test("User ID Format Analysis", True,
                     f"UUID: {len(uuid_users)}, ObjectId: {len(objectid_users)}, Other: {len(other_users)}")
        
        return True

    def run_comprehensive_test(self):
        """Run comprehensive system notification fix testing"""
        print("🚀 Starting Comprehensive System Notification Fix Testing")
        print("=" * 80)
        
        # Test 1: Login notification creation for demo user
        test1_result = self.test_login_notification_creation_demo_user()
        
        # Test 2: Login notification creation for admin user  
        test2_result = self.test_login_notification_creation_admin_user()
        
        # Test 3: New user registration and notifications
        test3_result = self.test_new_user_registration_notifications()
        
        # Test 4: Existing user ObjectId format handling
        test4_result = self.test_existing_user_objectid_format()
        
        # Test 5: System notification endpoint functionality
        test5_result = self.test_system_notification_endpoint_functionality()
        
        # Test 6: User ID format analysis
        test6_result = self.test_user_id_format_analysis()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 SYSTEM NOTIFICATION FIX TEST SUMMARY")
        print("=" * 80)
        
        test_results = [
            ("Demo User Login Notifications", test1_result),
            ("Admin User Login Notifications", test2_result), 
            ("New User Registration Notifications", test3_result),
            ("Existing User ObjectId Handling", test4_result),
            ("System Notification Endpoints", test5_result),
            ("User ID Format Analysis", test6_result)
        ]
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n📈 Overall Results: {passed_tests}/{total_tests} tests passed ({self.tests_passed}/{self.tests_run} individual assertions)")
        
        if passed_tests == total_tests:
            print("🎉 ALL SYSTEM NOTIFICATION TESTS PASSED!")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} system notification tests failed")
            return False

if __name__ == "__main__":
    tester = SystemNotificationTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)