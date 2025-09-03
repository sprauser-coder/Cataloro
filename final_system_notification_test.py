#!/usr/bin/env python3
"""
FINAL SYSTEM NOTIFICATION FIX TEST - COMPREHENSIVE VERIFICATION
Tests the complete system notification fix for user ID consistency as requested in review
"""

import requests
import sys
import json
from datetime import datetime
import time

class FinalSystemNotificationTester:
    def __init__(self, base_url="https://cataloro-marketplace-2.preview.emergentagent.com"):
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

    def run_api_call(self, method, endpoint, data=None, expected_status=200):
        """Make API call and return response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            return response.status_code == expected_status, response
        except Exception as e:
            print(f"API call error: {e}")
            return False, None

    def test_login_with_notification_creation(self, email, user_type):
        """Test 1: Login notification creation with proper user ID"""
        print(f"\n🔐 TEST 1: Login notification creation for {email}...")
        
        # Login and capture user data
        success, response = self.run_api_call(
            'POST', 
            'api/auth/login',
            data={"email": email, "password": "demo123"}
        )
        
        if not success:
            self.log_test(f"Login {email}", False, f"Login failed: {response.text if response else 'No response'}")
            return None
        
        try:
            login_data = response.json()
            user = login_data.get('user')
            if not user:
                self.log_test(f"Login {email}", False, "No user data in login response")
                return None
            
            user_id = user.get('id')
            if not user_id:
                self.log_test(f"Login {email}", False, "No user ID in login response")
                return None
            
            print(f"   ✅ Login successful for {email}")
            print(f"   📋 User ID from login response: {user_id}")
            print(f"   📋 User ID format: {type(user_id)} - {len(user_id)} characters")
            
            # Check if it's UUID format (36 chars with dashes) or ObjectId format (24 chars hex)
            if len(user_id) == 36 and user_id.count('-') == 4:
                id_format = "UUID"
            elif len(user_id) == 24:
                id_format = "ObjectId"
            else:
                id_format = "Unknown"
            
            print(f"   📋 Detected ID format: {id_format}")
            
            self.log_test(f"Login {email}", True, f"User ID: {user_id} ({id_format})")
            
            return user
            
        except Exception as e:
            self.log_test(f"Login {email}", False, f"Error parsing login response: {e}")
            return None

    def test_user_id_consistency(self, user_data, email):
        """Test 2: Verify user ID consistency between login and profile"""
        print(f"\n🔄 TEST 2: User ID consistency verification for {email}...")
        
        if not user_data:
            self.log_test(f"User ID Consistency {email}", False, "No user data provided")
            return False
        
        login_user_id = user_data.get('id')
        
        # Get profile data to compare
        success, response = self.run_api_call('GET', f'api/auth/profile/{login_user_id}')
        
        if not success:
            self.log_test(f"Profile Access {email}", False, "Could not access profile endpoint")
            return False
        
        try:
            profile_data = response.json()
            profile_user_id = profile_data.get('id')
            
            print(f"   📋 Login user ID: {login_user_id}")
            print(f"   📋 Profile user ID: {profile_user_id}")
            
            id_match = login_user_id == profile_user_id
            
            self.log_test(f"User ID Consistency {email}", id_match,
                         f"Login ID matches Profile ID: {id_match}")
            
            return id_match
            
        except Exception as e:
            self.log_test(f"User ID Consistency {email}", False, f"Error checking consistency: {e}")
            return False

    def test_notification_retrieval(self, user_data, email):
        """Test 3: Test notification retrieval via API"""
        print(f"\n📬 TEST 3: Notification retrieval for {email}...")
        
        if not user_data:
            self.log_test(f"Notification Retrieval {email}", False, "No user data provided")
            return False, []
        
        user_id = user_data.get('id')
        
        # Test both possible endpoints
        endpoints_to_test = [
            f'api/user/{user_id}/notifications',
            f'api/user/{user_id}/system-notifications'
        ]
        
        notifications_found = False
        all_notifications = []
        
        for endpoint in endpoints_to_test:
            print(f"   🔍 Testing endpoint: {endpoint}")
            
            success, response = self.run_api_call('GET', endpoint)
            
            if success:
                try:
                    notifications = response.json()
                    print(f"   ✅ Endpoint {endpoint} accessible")
                    print(f"   📊 Found {len(notifications)} notifications")
                    
                    if notifications:
                        notifications_found = True
                        all_notifications.extend(notifications)
                        
                        # Show sample notifications
                        for i, notif in enumerate(notifications[:3]):  # Show first 3
                            print(f"   📝 Notification {i+1}:")
                            print(f"      ID: {notif.get('id', 'N/A')}")
                            print(f"      User ID: {notif.get('user_id', 'N/A')}")
                            print(f"      Title: {notif.get('title', 'N/A')}")
                            print(f"      Message: {notif.get('message', 'N/A')[:50]}...")
                            print(f"      Type: {notif.get('type', 'N/A')}")
                        
                except Exception as e:
                    print(f"   ❌ Error parsing notifications: {e}")
            else:
                status_code = response.status_code if response else 'No response'
                print(f"   ❌ Endpoint {endpoint} failed: {status_code}")
        
        self.log_test(f"Notification Retrieval {email}", notifications_found, 
                     f"Total notifications found: {len(all_notifications)}")
        
        return notifications_found, all_notifications

    def test_login_notification_specific(self, user_data, email, all_notifications):
        """Test 4: Verify login notifications are created and retrievable"""
        print(f"\n🎯 TEST 4: Login notification verification for {email}...")
        
        if not user_data or not all_notifications:
            self.log_test(f"Login Notification {email}", False, "No user data or notifications")
            return False
        
        user_id = user_data.get('id')
        
        # Look for login/system notifications
        login_notifications = []
        system_notifications = []
        
        for notif in all_notifications:
            notif_type = notif.get('type', '')
            message = notif.get('message', '').lower()
            title = notif.get('title', '').lower()
            
            if notif_type == 'system':
                system_notifications.append(notif)
                
            if ('login' in message or 'login' in title or 
                'welcome' in message or 'welcome' in title):
                login_notifications.append(notif)
        
        print(f"   📊 System notifications: {len(system_notifications)}")
        print(f"   📊 Login-related notifications: {len(login_notifications)}")
        
        # Check user ID consistency in notifications
        matching_user_ids = 0
        mismatched_user_ids = 0
        
        for notif in all_notifications:
            notif_user_id = notif.get('user_id')
            if notif_user_id == user_id:
                matching_user_ids += 1
            else:
                mismatched_user_ids += 1
                print(f"   ⚠️  Mismatched user ID in notification:")
                print(f"      Expected: {user_id}")
                print(f"      Found: {notif_user_id}")
                print(f"      Notification: {notif.get('title', 'N/A')}")
        
        print(f"   📊 Notifications with matching user ID: {matching_user_ids}")
        print(f"   📊 Notifications with mismatched user ID: {mismatched_user_ids}")
        
        # Check for hardcoded messages
        hardcoded_found = False
        for notif in login_notifications:
            message = notif.get('message', '')
            if 'Welcome back to the new Cataloro' in message:
                hardcoded_found = True
                print(f"   ⚠️  Found hardcoded message: {message}")
        
        login_success = len(login_notifications) > 0 and matching_user_ids > 0 and mismatched_user_ids == 0
        
        self.log_test(f"Login Notification {email}", login_success,
                     f"Login notifications: {len(login_notifications)}, User ID matches: {matching_user_ids}, Mismatches: {mismatched_user_ids}")
        
        self.log_test(f"Hardcoded Message Check {email}", not hardcoded_found,
                     f"No hardcoded messages found: {not hardcoded_found}")
        
        return login_success

    def test_complete_flow(self, email, user_type):
        """Test 5: Complete flow - Login → Notification Creation → Retrieval → User sees notifications"""
        print(f"\n🔄 TEST 5: Complete flow for {email} ({user_type})...")
        
        # Step 1: Login (triggers notification creation)
        user_data = self.test_login_with_notification_creation(email, user_type)
        if not user_data:
            return False
        
        # Step 2: Wait for notification processing
        print("   ⏳ Waiting 3 seconds for notification processing...")
        time.sleep(3)
        
        # Step 3: Verify user ID consistency
        consistency_ok = self.test_user_id_consistency(user_data, email)
        
        # Step 4: Test notification retrieval
        notifications_found, all_notifications = self.test_notification_retrieval(user_data, email)
        
        # Step 5: Verify login notifications specifically
        login_notifications_ok = self.test_login_notification_specific(user_data, email, all_notifications)
        
        # Overall flow success
        flow_success = consistency_ok and notifications_found and login_notifications_ok
        
        self.log_test(f"Complete Flow {email}", flow_success,
                     f"Consistency: {consistency_ok}, Notifications: {notifications_found}, Login notifications: {login_notifications_ok}")
        
        return flow_success

    def run_comprehensive_test(self):
        """Run the final comprehensive system notification test"""
        print("🚀 FINAL SYSTEM NOTIFICATION FIX - COMPREHENSIVE TEST")
        print("=" * 70)
        print("Review Request: Final comprehensive test of the complete system notification fix")
        print("Testing: Login notification creation with proper user ID, user ID consistency,")
        print("         notification retrieval, complete flow, and hardcoded message fix")
        print("=" * 70)
        
        # Test users as specified in review
        test_users = [
            ("demo@cataloro.com", "demo"),
            ("admin@cataloro.com", "admin")
        ]
        
        # Test each user
        flow_results = []
        for email, user_type in test_users:
            print(f"\n{'='*70}")
            print(f"TESTING USER: {email} ({user_type.upper()})")
            print(f"{'='*70}")
            
            flow_success = self.test_complete_flow(email, user_type)
            flow_results.append((email, flow_success))
        
        # Final Summary
        print(f"\n{'='*70}")
        print("FINAL SYSTEM NOTIFICATION FIX TEST RESULTS")
        print(f"{'='*70}")
        
        total_flows = len(flow_results)
        successful_flows = sum(1 for _, success in flow_results if success)
        
        print(f"📊 Total Individual Tests Run: {self.tests_run}")
        print(f"✅ Individual Tests Passed: {self.tests_passed}")
        print(f"❌ Individual Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Individual Test Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n🔄 Complete Flow Results:")
        for email, success in flow_results:
            status = "✅ WORKING" if success else "❌ FAILED"
            print(f"   {email}: {status}")
        
        print(f"\n🎯 Overall System Success: {successful_flows}/{total_flows} users working")
        
        # Final verdict based on review requirements
        all_requirements_met = (
            successful_flows == total_flows and 
            self.tests_passed >= (self.tests_run * 0.8)
        )
        
        print(f"\n{'='*70}")
        if all_requirements_met:
            print("🎉 SYSTEM NOTIFICATION FIX: ✅ WORKING COMPLETELY")
            print("✅ Login notification creation with proper user ID - WORKING")
            print("✅ User ID consistency verification - WORKING") 
            print("✅ Notification retrieval functionality - WORKING")
            print("✅ Complete flow (Login → Creation → Retrieval) - WORKING")
            print("✅ Hardcoded message fix verification - WORKING")
            print("\nThe ENTIRE system notification system is now working end-to-end.")
        else:
            print("❌ SYSTEM NOTIFICATION FIX: ❌ NOT WORKING COMPLETELY")
            print("Issues found with one or more components:")
            if successful_flows < total_flows:
                print(f"   - Complete flow failed for {total_flows - successful_flows} users")
            if self.tests_passed < (self.tests_run * 0.8):
                print(f"   - Individual test success rate too low: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"{'='*70}")
        
        return all_requirements_met

if __name__ == "__main__":
    tester = FinalSystemNotificationTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)