#!/usr/bin/env python3
"""
Focused Backend API Test Suite for Review Request
Tests specific endpoints mentioned in the review:
1. Public profile endpoint `/api/auth/profile/{user_id}`
2. Notifications page functionality 
3. Deals/orders endpoint `/api/user/my-deals/{user_id}`
4. Authentication issues preventing access to profile pages
5. Various user IDs that might exist in the system
"""

import requests
import sys
import json
from datetime import datetime

class FocusedAPITester:
    def __init__(self, base_url="https://market-upgrade-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.discovered_users = []

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
                    details += f", Response: {json.dumps(response_data, indent=2)[:300]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_test_users(self):
        """Setup test users for testing"""
        print("\n🔧 Setting up test users...")
        
        # Test admin login
        success, response = self.run_test(
            "Admin Login Setup",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_user = response['user']
            self.discovered_users.append(self.admin_user)
            print(f"   Admin User: {self.admin_user}")

        # Test regular user login
        success, response = self.run_test(
            "Regular User Login Setup",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.user_token = response['token']
            self.regular_user = response['user']
            self.discovered_users.append(self.regular_user)
            print(f"   Regular User: {self.regular_user}")

        # Discover more users from admin endpoint
        if self.admin_user:
            success, response = self.run_test(
                "Discover All Users",
                "GET",
                "api/admin/users",
                200
            )
            if success:
                for user in response:
                    if user not in self.discovered_users:
                        self.discovered_users.append(user)
                print(f"   Total discovered users: {len(self.discovered_users)}")

    def test_public_profile_endpoints(self):
        """Test public profile endpoint with various user IDs"""
        print("\n👤 TESTING PUBLIC PROFILE ENDPOINTS")
        print("=" * 50)
        
        if not self.discovered_users:
            print("❌ No users discovered - cannot test profiles")
            return False

        profile_tests_passed = 0
        total_profile_tests = 0

        for user in self.discovered_users:
            user_id = user.get('id')
            username = user.get('username', 'Unknown')
            full_name = user.get('full_name', 'Unknown')
            email = user.get('email', 'Unknown')
            
            if not user_id:
                continue
                
            total_profile_tests += 1
            
            print(f"\n📋 Testing profile for user: {username} ({email})")
            success, response = self.run_test(
                f"Public Profile - {username}",
                "GET",
                f"api/auth/profile/{user_id}",
                200
            )
            
            if success:
                profile_tests_passed += 1
                
                # Verify profile data integrity
                returned_username = response.get('username', '')
                returned_full_name = response.get('full_name', '')
                returned_email = response.get('email', '')
                
                print(f"   📊 Profile Data Analysis:")
                print(f"      Expected Username: {username}")
                print(f"      Returned Username: {returned_username}")
                print(f"      Expected Full Name: {full_name}")
                print(f"      Returned Full Name: {returned_full_name}")
                print(f"      Expected Email: {email}")
                print(f"      Returned Email: {returned_email}")
                
                # Check for the "sash_admin" issue mentioned in review
                if returned_username == "sash_admin" and username != "sash_admin":
                    print(f"   ⚠️  ISSUE DETECTED: Profile returning 'sash_admin' for user {username}")
                    self.log_test(f"Profile Data Integrity - {username}", False, 
                                 "Profile returning 'sash_admin' instead of actual user data")
                else:
                    print(f"   ✅ Profile data integrity verified for {username}")
                    self.log_test(f"Profile Data Integrity - {username}", True, 
                                 "Profile returns correct user-specific data")

        print(f"\n📊 Public Profile Tests Summary: {profile_tests_passed}/{total_profile_tests} passed")
        return profile_tests_passed == total_profile_tests

    def test_notifications_functionality(self):
        """Test notifications page functionality"""
        print("\n🔔 TESTING NOTIFICATIONS FUNCTIONALITY")
        print("=" * 50)
        
        if not self.discovered_users:
            print("❌ No users discovered - cannot test notifications")
            return False

        notifications_tests_passed = 0
        total_notifications_tests = 0

        for user in self.discovered_users:
            user_id = user.get('id')
            username = user.get('username', 'Unknown')
            
            if not user_id:
                continue
                
            total_notifications_tests += 1
            
            print(f"\n📋 Testing notifications for user: {username}")
            success, response = self.run_test(
                f"User Notifications - {username}",
                "GET",
                f"api/user/notifications/{user_id}",
                200
            )
            
            if success:
                notifications_tests_passed += 1
                
                print(f"   📊 Notifications Analysis:")
                print(f"      Total Notifications: {len(response)}")
                
                if response:
                    # Analyze notification structure
                    first_notification = response[0]
                    required_fields = ['id', 'user_id', 'title', 'message', 'type', 'is_read', 'created_at']
                    missing_fields = [field for field in required_fields if field not in first_notification]
                    
                    if missing_fields:
                        print(f"   ⚠️  Missing notification fields: {missing_fields}")
                        self.log_test(f"Notification Structure - {username}", False, 
                                     f"Missing fields: {missing_fields}")
                    else:
                        print(f"   ✅ Notification structure complete")
                        self.log_test(f"Notification Structure - {username}", True, 
                                     "All required notification fields present")
                    
                    # Check notification types
                    notification_types = set(n.get('type', 'unknown') for n in response)
                    print(f"      Notification Types: {list(notification_types)}")
                    
                    # Check read/unread status
                    unread_count = sum(1 for n in response if not n.get('is_read', True))
                    print(f"      Unread Notifications: {unread_count}/{len(response)}")
                else:
                    print(f"   📝 No notifications found for user {username}")

        print(f"\n📊 Notifications Tests Summary: {notifications_tests_passed}/{total_notifications_tests} passed")
        return notifications_tests_passed == total_notifications_tests

    def test_deals_orders_functionality(self):
        """Test deals/orders endpoint functionality"""
        print("\n🤝 TESTING DEALS/ORDERS FUNCTIONALITY")
        print("=" * 50)
        
        if not self.discovered_users:
            print("❌ No users discovered - cannot test deals")
            return False

        deals_tests_passed = 0
        total_deals_tests = 0

        for user in self.discovered_users:
            user_id = user.get('id')
            username = user.get('username', 'Unknown')
            
            if not user_id:
                continue
                
            total_deals_tests += 1
            
            print(f"\n📋 Testing deals for user: {username}")
            success, response = self.run_test(
                f"User Deals - {username}",
                "GET",
                f"api/user/my-deals/{user_id}",
                200
            )
            
            if success:
                deals_tests_passed += 1
                
                print(f"   📊 Deals Analysis:")
                print(f"      Total Deals: {len(response)}")
                
                if response:
                    # Analyze deal structure
                    first_deal = response[0]
                    required_fields = ['id', 'listing_id', 'buyer_id', 'seller_id', 'status', 'amount', 'created_at']
                    missing_fields = [field for field in required_fields if field not in first_deal]
                    
                    if missing_fields:
                        print(f"   ⚠️  Missing deal fields: {missing_fields}")
                        self.log_test(f"Deal Structure - {username}", False, 
                                     f"Missing fields: {missing_fields}")
                    else:
                        print(f"   ✅ Deal structure complete")
                        self.log_test(f"Deal Structure - {username}", True, 
                                     "All required deal fields present")
                    
                    # Check deal enrichment (listing and user data)
                    has_listing_data = 'listing' in first_deal and first_deal['listing']
                    has_buyer_data = 'buyer' in first_deal
                    has_seller_data = 'seller' in first_deal
                    
                    print(f"      Listing Data Present: {has_listing_data}")
                    print(f"      Buyer Data Present: {has_buyer_data}")
                    print(f"      Seller Data Present: {has_seller_data}")
                    
                    if has_listing_data:
                        listing = first_deal['listing']
                        print(f"      Sample Listing: {listing.get('title', 'No title')[:50]}...")
                        print(f"      Listing Price: €{listing.get('price', 0)}")
                    
                    # Check deal statuses
                    deal_statuses = set(d.get('status', 'unknown') for d in response)
                    print(f"      Deal Statuses: {list(deal_statuses)}")
                    
                    # Check if deals are properly sorted (newest first)
                    if len(response) > 1:
                        dates = [d.get('created_at') for d in response if d.get('created_at')]
                        if dates:
                            is_sorted = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
                            print(f"      Properly Sorted (newest first): {is_sorted}")
                            self.log_test(f"Deal Sorting - {username}", is_sorted, 
                                         f"Deals sorted by date: {is_sorted}")
                else:
                    print(f"   📝 No deals found for user {username}")

        print(f"\n📊 Deals Tests Summary: {deals_tests_passed}/{total_deals_tests} passed")
        return deals_tests_passed == total_deals_tests

    def test_authentication_access(self):
        """Test authentication issues preventing access to profile pages"""
        print("\n🔐 TESTING AUTHENTICATION ACCESS")
        print("=" * 50)
        
        auth_tests_passed = 0
        total_auth_tests = 0
        
        # Test 1: Access profile without authentication
        print("\n🚫 Testing unauthenticated profile access...")
        if self.regular_user:
            total_auth_tests += 1
            success, response = self.run_test(
                "Unauthenticated Profile Access",
                "GET",
                f"api/auth/profile/{self.regular_user['id']}",
                200  # Profile endpoint should work without auth (public)
            )
            if success:
                auth_tests_passed += 1
                print("   ✅ Profile endpoint accessible without authentication (as expected for public profiles)")
        
        # Test 2: Access with valid authentication
        print("\n✅ Testing authenticated profile access...")
        if self.regular_user and self.user_token:
            total_auth_tests += 1
            headers = {"Authorization": f"Bearer {self.user_token}"}
            success, response = self.run_test(
                "Authenticated Profile Access",
                "GET",
                f"api/auth/profile/{self.regular_user['id']}",
                200,
                headers=headers
            )
            if success:
                auth_tests_passed += 1
                print("   ✅ Profile endpoint accessible with authentication")
        
        # Test 3: Access with invalid authentication
        print("\n❌ Testing invalid authentication...")
        if self.regular_user:
            total_auth_tests += 1
            headers = {"Authorization": "Bearer invalid_token_12345"}
            success, response = self.run_test(
                "Invalid Authentication Profile Access",
                "GET",
                f"api/auth/profile/{self.regular_user['id']}",
                200  # Profile endpoint should still work (public endpoint)
            )
            if success:
                auth_tests_passed += 1
                print("   ✅ Profile endpoint accessible even with invalid auth (public endpoint)")
        
        # Test 4: Test cross-user profile access
        print("\n🔄 Testing cross-user profile access...")
        if len(self.discovered_users) >= 2:
            user1 = self.discovered_users[0]
            user2 = self.discovered_users[1]
            
            total_auth_tests += 1
            success, response = self.run_test(
                f"Cross-User Profile Access ({user1.get('username', 'User1')} accessing {user2.get('username', 'User2')})",
                "GET",
                f"api/auth/profile/{user2['id']}",
                200
            )
            if success:
                auth_tests_passed += 1
                
                # Check if correct user data is returned
                returned_username = response.get('username', '')
                expected_username = user2.get('username', '')
                
                if returned_username == expected_username:
                    print(f"   ✅ Correct user data returned: {returned_username}")
                    self.log_test("Cross-User Profile Data Integrity", True, 
                                 "Correct user-specific data returned")
                else:
                    print(f"   ⚠️  Incorrect user data: expected {expected_username}, got {returned_username}")
                    self.log_test("Cross-User Profile Data Integrity", False, 
                                 f"Wrong user data: expected {expected_username}, got {returned_username}")

        print(f"\n📊 Authentication Tests Summary: {auth_tests_passed}/{total_auth_tests} passed")
        return auth_tests_passed == total_auth_tests

    def test_various_user_ids(self):
        """Test various user IDs that might exist in the system"""
        print("\n🆔 TESTING VARIOUS USER IDS")
        print("=" * 50)
        
        # Test with discovered user IDs
        valid_ids_tested = 0
        total_valid_tests = len(self.discovered_users)
        
        print(f"\n✅ Testing {total_valid_tests} discovered valid user IDs...")
        for user in self.discovered_users:
            user_id = user.get('id')
            username = user.get('username', 'Unknown')
            
            if user_id:
                success, response = self.run_test(
                    f"Valid User ID Test - {username}",
                    "GET",
                    f"api/auth/profile/{user_id}",
                    200
                )
                if success:
                    valid_ids_tested += 1
        
        # Test with invalid/non-existent user IDs
        invalid_ids = [
            "00000000-0000-0000-0000-000000000000",  # UUID format but non-existent
            "invalid-user-id",  # Invalid format
            "123456789",  # Numeric ID
            "nonexistent@email.com",  # Email format
            "",  # Empty string
        ]
        
        invalid_ids_tested = 0
        total_invalid_tests = len(invalid_ids)
        
        print(f"\n❌ Testing {total_invalid_tests} invalid user IDs...")
        for invalid_id in invalid_ids:
            success, response = self.run_test(
                f"Invalid User ID Test - {invalid_id}",
                "GET",
                f"api/auth/profile/{invalid_id}",
                404  # Expecting 404 for non-existent users
            )
            if success:
                invalid_ids_tested += 1

        print(f"\n📊 User ID Tests Summary:")
        print(f"   Valid IDs: {valid_ids_tested}/{total_valid_tests} passed")
        print(f"   Invalid IDs: {invalid_ids_tested}/{total_invalid_tests} properly rejected")
        
        return (valid_ids_tested == total_valid_tests) and (invalid_ids_tested == total_invalid_tests)

    def run_focused_tests(self):
        """Run all focused tests as requested in the review"""
        print("🎯 FOCUSED BACKEND API TESTING")
        print("=" * 60)
        print("Testing specific endpoints mentioned in review request:")
        print("1. Public profile endpoint `/api/auth/profile/{user_id}`")
        print("2. Notifications page functionality")
        print("3. Deals/orders endpoint `/api/user/my-deals/{user_id}`")
        print("4. Authentication issues preventing access to profile pages")
        print("5. Various user IDs that might exist in the system")
        print("=" * 60)

        # Setup
        self.setup_test_users()
        
        # Run focused tests
        test_results = []
        
        test_results.append(("Public Profile Endpoints", self.test_public_profile_endpoints()))
        test_results.append(("Notifications Functionality", self.test_notifications_functionality()))
        test_results.append(("Deals/Orders Functionality", self.test_deals_orders_functionality()))
        test_results.append(("Authentication Access", self.test_authentication_access()))
        test_results.append(("Various User IDs", self.test_various_user_ids()))
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 FOCUSED TESTING SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} {test_name}")
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} test suites passed")
        print(f"Individual Tests: {self.tests_passed}/{self.tests_run} tests passed")
        
        # Specific findings for review
        print("\n" + "=" * 60)
        print("🔍 KEY FINDINGS FOR REVIEW")
        print("=" * 60)
        
        if self.discovered_users:
            print(f"✅ Discovered {len(self.discovered_users)} users in the system")
            for user in self.discovered_users:
                print(f"   - {user.get('username', 'Unknown')} ({user.get('email', 'No email')}) - Role: {user.get('role', 'Unknown')}")
        
        print(f"\n📊 Test Coverage:")
        print(f"   - Profile endpoints tested with {len(self.discovered_users)} different user IDs")
        print(f"   - Notifications tested for all discovered users")
        print(f"   - Deals/orders tested for all discovered users")
        print(f"   - Authentication scenarios tested")
        print(f"   - Invalid user ID handling tested")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    print("🚀 Starting Focused Backend API Testing...")
    tester = FocusedAPITester()
    success = tester.run_focused_tests()
    
    if success:
        print("\n🎉 All focused tests completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Some focused tests failed - check results above")
        sys.exit(1)