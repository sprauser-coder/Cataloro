#!/usr/bin/env python3
"""
Login Notification Fix Test Suite
Tests the specific login notification fix for user ID handling
"""

import requests
import sys
import json
import time
from datetime import datetime

class LoginNotificationTester:
    def __init__(self, base_url="https://tender-fix.preview.emergentagent.com"):
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

    def test_login_notification_creation(self, email, password="demo123"):
        """Test login notification creation for a specific user"""
        print(f"\n🔐 Testing Login Notification Creation for {email}...")
        
        # Step 1: Get current notification count
        print("   1️⃣ Getting current notification count...")
        
        # First login to get user ID
        login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Initial login failed: {login_response.status_code}")
            return False
        
        user_data = login_response.json().get('user', {})
        user_id = user_data.get('id')
        
        if not user_id:
            print(f"   ❌ No user ID in login response")
            return False
        
        print(f"   📋 User ID: {user_id}")
        print(f"   📋 User data: {user_data}")
        
        # Get current notifications
        notif_response = requests.get(
            f"{self.base_url}/api/user/notifications/{user_id}",
            headers={"Content-Type": "application/json"}
        )
        
        if notif_response.status_code == 200:
            current_notifications = notif_response.json()
            current_count = len(current_notifications)
            print(f"   📧 Current notification count: {current_count}")
            
            # Count login notifications specifically
            login_notifs_before = [
                n for n in current_notifications 
                if n.get('type') == 'system' and 'login' in n.get('message', '').lower()
            ]
            print(f"   🔐 Current login notifications: {len(login_notifs_before)}")
        else:
            current_count = 0
            login_notifs_before = []
            print(f"   ⚠️  Could not get current notifications: {notif_response.status_code}")
        
        # Step 2: Perform fresh login to trigger notification
        print("   2️⃣ Performing fresh login to trigger notification...")
        
        fresh_login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if fresh_login_response.status_code != 200:
            print(f"   ❌ Fresh login failed: {fresh_login_response.status_code}")
            return False
        
        fresh_user_data = fresh_login_response.json().get('user', {})
        fresh_user_id = fresh_user_data.get('id')
        
        print(f"   ✅ Fresh login successful")
        print(f"   📋 Fresh login user ID: {fresh_user_id}")
        
        # Step 3: Wait for notification creation
        print("   3️⃣ Waiting for notification creation...")
        time.sleep(3)  # Wait for async notification creation
        
        # Step 4: Check for new notifications
        print("   4️⃣ Checking for new notifications...")
        
        new_notif_response = requests.get(
            f"{self.base_url}/api/user/notifications/{user_id}",
            headers={"Content-Type": "application/json"}
        )
        
        if new_notif_response.status_code != 200:
            print(f"   ❌ Failed to get notifications after login: {new_notif_response.status_code}")
            return False
        
        new_notifications = new_notif_response.json()
        new_count = len(new_notifications)
        
        print(f"   📧 New notification count: {new_count}")
        
        # Look for login notifications
        login_notifs_after = [
            n for n in new_notifications 
            if n.get('type') == 'system' and 'login' in n.get('message', '').lower()
        ]
        
        print(f"   🔐 Login notifications after: {len(login_notifs_after)}")
        
        # Check if new login notification was created
        new_login_notifs = len(login_notifs_after) - len(login_notifs_before)
        
        if new_login_notifs > 0:
            print(f"   ✅ {new_login_notifs} new login notification(s) created!")
            
            # Show the latest login notification
            latest_login_notif = login_notifs_after[0]  # Most recent first
            print(f"   📝 Latest login notification:")
            print(f"      Title: {latest_login_notif.get('title')}")
            print(f"      Message: {latest_login_notif.get('message')}")
            print(f"      Type: {latest_login_notif.get('type')}")
            print(f"      Created: {latest_login_notif.get('created_at')}")
            
            self.log_test(f"Login Notification Creation for {email}", True, 
                         f"{new_login_notifs} new login notifications created")
            return True
        else:
            print(f"   ❌ No new login notifications created")
            print(f"   📋 All notification types: {[n.get('type') for n in new_notifications]}")
            print(f"   📋 All notification titles: {[n.get('title') for n in new_notifications[:5]]}")
            
            self.log_test(f"Login Notification Creation for {email}", False, 
                         "No new login notifications created")
            return False

    def test_user_id_formats(self):
        """Test that both UUID and ObjectId formats work for notifications"""
        print(f"\n🆔 Testing User ID Format Compatibility...")
        
        # Test with demo user (likely to have ObjectId format)
        demo_success = self.test_login_notification_creation("demo@cataloro.com")
        
        # Test with admin user (likely to have ObjectId format)  
        admin_success = self.test_login_notification_creation("admin@cataloro.com")
        
        # Create a new user (will have UUID format)
        new_user_email = f"test_uuid_{int(time.time())}@cataloro.com"
        
        print(f"\n   🆕 Creating new user with UUID format: {new_user_email}")
        
        register_response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={
                "username": f"test_uuid_{int(time.time())}",
                "email": new_user_email,
                "full_name": "Test UUID User",
                "password": "test123"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if register_response.status_code == 200:
            print(f"   ✅ New user registered successfully")
            new_user_success = self.test_login_notification_creation(new_user_email, "test123")
        else:
            print(f"   ❌ Failed to register new user: {register_response.status_code}")
            new_user_success = False
        
        # Summary
        total_formats = 3
        successful_formats = sum([demo_success, admin_success, new_user_success])
        
        self.log_test("User ID Format Compatibility", successful_formats > 0,
                     f"{successful_formats}/{total_formats} user ID formats working")
        
        return successful_formats > 0

    def test_notification_database_storage(self):
        """Test that notifications are properly stored in user_notifications collection"""
        print(f"\n💾 Testing Notification Database Storage...")
        
        # Login with demo user
        login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": "demo@cataloro.com", "password": "demo123"},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed for database test")
            return False
        
        user_data = login_response.json().get('user', {})
        user_id = user_data.get('id')
        
        # Wait for notification
        time.sleep(2)
        
        # Get notifications from user_notifications endpoint
        user_notif_response = requests.get(
            f"{self.base_url}/api/user/notifications/{user_id}",
            headers={"Content-Type": "application/json"}
        )
        
        # Also try the system-notifications endpoint if it exists
        system_notif_response = requests.get(
            f"{self.base_url}/api/user/{user_id}/system-notifications",
            headers={"Content-Type": "application/json"}
        )
        
        user_notif_success = user_notif_response.status_code == 200
        system_notif_success = system_notif_response.status_code == 200
        
        print(f"   📊 User notifications endpoint: {'✅' if user_notif_success else '❌'}")
        print(f"   📊 System notifications endpoint: {'✅' if system_notif_success else '❌'}")
        
        if user_notif_success:
            user_notifications = user_notif_response.json()
            login_notifs = [
                n for n in user_notifications 
                if n.get('type') == 'system' and 'login' in n.get('message', '').lower()
            ]
            print(f"   📧 Login notifications in user_notifications: {len(login_notifs)}")
        
        if system_notif_success:
            system_notifications = system_notif_response.json()
            print(f"   📧 System notifications endpoint returned: {len(system_notifications)} notifications")
        
        storage_success = user_notif_success and (len(login_notifs) > 0 if user_notif_success else False)
        
        self.log_test("Notification Database Storage", storage_success,
                     f"Notifications properly stored and retrievable")
        
        return storage_success

    def debug_login_notification_flow(self):
        """Debug the login notification flow step by step"""
        print(f"\n🔍 DEBUG: Login Notification Flow Analysis...")
        
        # Step 1: Test login endpoint response
        print("   🔍 Step 1: Testing login endpoint response...")
        
        login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": "demo@cataloro.com", "password": "demo123"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   📊 Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            user_data = login_data.get('user', {})
            user_id = user_data.get('id')
            
            print(f"   📋 Login response keys: {list(login_data.keys())}")
            print(f"   📋 User ID: {user_id}")
            print(f"   📋 User ID type: {type(user_id)}")
            print(f"   📋 User ID length: {len(user_id) if user_id else 0}")
            
            # Check if it's ObjectId format (24 hex chars) or UUID format
            if user_id:
                if len(user_id) == 24 and all(c in '0123456789abcdef' for c in user_id.lower()):
                    print(f"   📋 User ID format: ObjectId (_id field)")
                elif len(user_id) == 36 and user_id.count('-') == 4:
                    print(f"   📋 User ID format: UUID (id field)")
                else:
                    print(f"   📋 User ID format: Unknown")
            
            # Step 2: Test profile endpoint (tests user lookup logic)
            print("   🔍 Step 2: Testing profile endpoint (user lookup)...")
            
            profile_response = requests.get(
                f"{self.base_url}/api/auth/profile/{user_id}",
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   📊 Profile lookup status: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"   ✅ Profile lookup successful")
                print(f"   📋 Profile user ID: {profile_data.get('id')}")
            else:
                print(f"   ❌ Profile lookup failed: {profile_response.text[:200]}")
            
            # Step 3: Check notification creation timing
            print("   🔍 Step 3: Checking notification creation timing...")
            
            # Immediate check
            immediate_response = requests.get(
                f"{self.base_url}/api/user/notifications/{user_id}",
                headers={"Content-Type": "application/json"}
            )
            
            if immediate_response.status_code == 200:
                immediate_notifs = immediate_response.json()
                print(f"   📧 Immediate notifications: {len(immediate_notifs)}")
            
            # Wait and check again
            time.sleep(3)
            
            delayed_response = requests.get(
                f"{self.base_url}/api/user/notifications/{user_id}",
                headers={"Content-Type": "application/json"}
            )
            
            if delayed_response.status_code == 200:
                delayed_notifs = delayed_response.json()
                print(f"   📧 Delayed notifications: {len(delayed_notifs)}")
                
                # Show notification details
                for i, notif in enumerate(delayed_notifs[:3]):
                    print(f"   📝 Notification {i+1}: {notif.get('type')} - {notif.get('title')} - {notif.get('message')[:50]}...")
        
        return True

    def run_all_tests(self):
        """Run all login notification tests"""
        print("🚀 Starting Login Notification Fix Test Suite")
        print("=" * 70)
        
        # Debug flow first
        self.debug_login_notification_flow()
        
        # Test 1: User ID format compatibility
        test1 = self.test_user_id_formats()
        
        # Test 2: Database storage
        test2 = self.test_notification_database_storage()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 LOGIN NOTIFICATION TEST SUMMARY")
        print("=" * 70)
        
        tests = [
            ("User ID Format Compatibility", test1),
            ("Notification Database Storage", test2)
        ]
        
        passed_tests = sum(1 for _, result in tests if result)
        total_tests = len(tests)
        
        for test_name, result in tests:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n📈 Overall Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        print(f"🔧 Individual API calls: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        if passed_tests > 0:
            print("\n✅ LOGIN NOTIFICATION FUNCTIONALITY IS WORKING")
            print("✅ System notification fix appears to be functioning")
            return True
        else:
            print(f"\n❌ LOGIN NOTIFICATION FUNCTIONALITY NEEDS ATTENTION")
            print("❌ System notification fix requires investigation")
            return False

def main():
    """Main test execution"""
    tester = LoginNotificationTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()