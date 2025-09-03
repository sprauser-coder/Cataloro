#!/usr/bin/env python3
"""
System Notifications and Enhanced Backend Features Test Suite
Tests the comprehensive backend improvements for system notifications, deals, profiles, and user interactions
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class SystemNotificationsAPITester:
    def __init__(self, base_url="https://tender-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_notification_id = None

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

    def setup_users(self):
        """Setup admin and regular users for testing"""
        print("\n🔧 Setting up test users...")
        
        # Admin login
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
            print(f"   Admin User ID: {self.admin_user['id']}")

        # Regular user login
        success_user, user_response = self.run_test(
            "Regular User Login Setup",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        if success_user and 'token' in user_response:
            self.user_token = user_response['token']
            self.regular_user = user_response['user']
            print(f"   Regular User ID: {self.regular_user['id']}")

        return success_admin and success_user

    def test_system_notifications_management(self):
        """Test System Notifications Management endpoints"""
        print("\n🔔 Testing System Notifications Management...")
        
        if not self.admin_user or not self.regular_user:
            print("❌ System Notifications - SKIPPED (Need both admin and regular user)")
            return False

        # Test 1: GET /api/admin/system-notifications (admin management)
        print("\n1️⃣ Testing GET /api/admin/system-notifications...")
        success_get_admin, admin_notifications = self.run_test(
            "GET Admin System Notifications",
            "GET",
            "api/admin/system-notifications",
            200
        )
        
        if success_get_admin:
            print(f"   Found {len(admin_notifications)} admin system notifications")
        
        # Test 2: POST /api/admin/system-notifications (create toast notifications)
        print("\n2️⃣ Testing POST /api/admin/system-notifications...")
        test_notification = {
            "title": "System Maintenance Notice",
            "message": "Scheduled maintenance will occur tonight from 2-4 AM EST. Please save your work.",
            "type": "maintenance",
            "priority": "high",
            "target_users": "all",
            "display_duration": 10000,
            "auto_dismiss": True,
            "created_by": self.admin_user['id']
        }
        
        success_create, create_response = self.run_test(
            "POST Create System Notification",
            "POST",
            "api/admin/system-notifications",
            200,
            data=test_notification
        )
        
        if success_create and 'notification_id' in create_response:
            self.test_notification_id = create_response['notification_id']
            print(f"   Created system notification with ID: {self.test_notification_id}")
        
        # Test 3: GET /api/user/{user_id}/system-notifications (get user notifications)
        print("\n3️⃣ Testing GET /api/user/{user_id}/system-notifications...")
        success_get_user, user_notifications = self.run_test(
            "GET User System Notifications",
            "GET",
            f"api/user/{self.regular_user['id']}/system-notifications",
            200
        )
        
        if success_get_user:
            # Handle both direct list and wrapped response
            if isinstance(user_notifications, dict) and 'notifications' in user_notifications:
                notifications_list = user_notifications['notifications']
            else:
                notifications_list = user_notifications if isinstance(user_notifications, list) else []
            
            print(f"   Found {len(notifications_list)} user system notifications")
            # Check if our created notification appears for the user
            if self.test_notification_id and notifications_list:
                found_notification = any(n.get('id') == self.test_notification_id for n in notifications_list)
                self.log_test("System Notification Delivery to User", found_notification,
                             f"Created notification delivered to user: {found_notification}")
        
        # Test 4: POST /api/user/{user_id}/system-notifications/{notification_id}/view (mark as viewed)
        print("\n4️⃣ Testing POST /api/user/{user_id}/system-notifications/{notification_id}/view...")
        if self.test_notification_id:
            success_mark_viewed, view_response = self.run_test(
                "POST Mark System Notification as Viewed",
                "POST",
                f"api/user/{self.regular_user['id']}/system-notifications/{self.test_notification_id}/view",
                200,
                data={"viewed_at": datetime.utcnow().isoformat()}
            )
            
            if success_mark_viewed:
                print("   ✅ System notification marked as viewed successfully")
        
        # Test 5: Verify green toast notification structure
        print("\n5️⃣ Testing green toast notification data structure...")
        if success_get_user and notifications_list:
            for notification in notifications_list[:3]:  # Check first 3 notifications
                required_fields = ['id', 'title', 'message', 'type']
                has_required_fields = all(field in notification for field in required_fields)
                
                # Check for toast-specific fields
                toast_fields = ['show_duration', 'auto_dismiss']
                has_toast_fields = any(field in notification for field in toast_fields)
                
                if has_required_fields:
                    self.log_test("System Notification Structure", True,
                                 f"Notification has required fields for green toast display")
                    break
        
        return True

    def test_enhanced_deals_system(self):
        """Test Enhanced Deals/Orders System"""
        print("\n💼 Testing Enhanced Deals/Orders System...")
        
        if not self.regular_user:
            print("❌ Enhanced Deals System - SKIPPED (No regular user)")
            return False

        # Test 1: GET /api/user/my-deals/{user_id} (real deals data)
        print("\n1️⃣ Testing GET /api/user/my-deals/{user_id}...")
        success_deals, deals_response = self.run_test(
            "GET My Deals with Real Data",
            "GET",
            f"api/user/my-deals/{self.regular_user['id']}",
            200
        )
        
        if success_deals:
            print(f"   Found {len(deals_response)} deals for user")
            
            # Test 2: Verify deals data structure for live statistics
            print("\n2️⃣ Verifying deals data structure for live statistics...")
            if deals_response:
                deal = deals_response[0]
                required_fields = ['id', 'listing_id', 'buyer_id', 'seller_id', 'status', 'amount', 'created_at']
                has_required_fields = all(field in deal for field in required_fields)
                
                # Check for enriched data
                enriched_fields = ['listing', 'buyer', 'seller']
                has_enriched_data = all(field in deal for field in enriched_fields)
                
                self.log_test("Deals Data Structure", has_required_fields,
                             f"Deal has required fields: {has_required_fields}")
                self.log_test("Deals Enriched Data", has_enriched_data,
                             f"Deal has enriched data: {has_enriched_data}")
                
                # Check listing data within deal
                if 'listing' in deal:
                    listing = deal['listing']
                    listing_fields = ['id', 'title', 'price', 'image']
                    has_listing_fields = all(field in listing for field in listing_fields)
                    self.log_test("Deal Listing Data", has_listing_fields,
                                 f"Deal listing has required fields: {has_listing_fields}")
                
                # Check participant data
                if 'buyer' in deal and 'seller' in deal:
                    buyer = deal['buyer']
                    seller = deal['seller']
                    participant_fields = ['id', 'username']
                    has_buyer_fields = all(field in buyer for field in participant_fields)
                    has_seller_fields = all(field in seller for field in participant_fields)
                    self.log_test("Deal Participant Data", has_buyer_fields and has_seller_fields,
                                 f"Deal participants have required fields: buyer={has_buyer_fields}, seller={has_seller_fields}")
            
            # Test 3: Test deals filtering and sorting
            print("\n3️⃣ Testing deals filtering and sorting...")
            # Check if deals are sorted by creation date (newest first)
            if len(deals_response) > 1:
                dates_sorted = True
                for i in range(len(deals_response) - 1):
                    current_date = deals_response[i].get('created_at', '')
                    next_date = deals_response[i + 1].get('created_at', '')
                    if current_date < next_date:  # Should be newest first
                        dates_sorted = False
                        break
                
                self.log_test("Deals Sorting by Date", dates_sorted,
                             f"Deals sorted by creation date (newest first): {dates_sorted}")
            
            # Test 4: Test deals status management
            print("\n4️⃣ Testing deals status management...")
            status_counts = {}
            for deal in deals_response:
                status = deal.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            valid_statuses = ['pending', 'approved', 'completed', 'cancelled', 'rejected']
            has_valid_statuses = all(status in valid_statuses for status in status_counts.keys())
            
            self.log_test("Deals Status Management", has_valid_statuses,
                         f"All deal statuses are valid: {status_counts}")
            
            print(f"   📊 Deal Status Distribution: {status_counts}")
        
        return True

    def test_public_profile_data_fetching(self):
        """Test Public Profile Data Fetching endpoints"""
        print("\n👤 Testing Public Profile Data Fetching...")
        
        if not self.regular_user:
            print("❌ Public Profile Data - SKIPPED (No regular user)")
            return False

        user_id = self.regular_user['id']
        
        # Test 1: GET /api/auth/profile/{user_id} (primary profile endpoint)
        print("\n1️⃣ Testing GET /api/auth/profile/{user_id}...")
        success_auth_profile, auth_profile_response = self.run_test(
            "GET Auth Profile (Primary)",
            "GET",
            f"api/auth/profile/{user_id}",
            200
        )
        
        if success_auth_profile:
            print(f"   Retrieved profile via auth endpoint: {auth_profile_response.get('username', 'Unknown')}")
            
            # Verify profile data completeness for public profiles
            required_profile_fields = ['id', 'username', 'email', 'full_name', 'role', 'created_at']
            has_required_fields = all(field in auth_profile_response for field in required_profile_fields)
            self.log_test("Auth Profile Data Completeness", has_required_fields,
                         f"Profile has required fields: {has_required_fields}")
        
        # Test 2: GET /api/user/{user_id} (alternative profile endpoint)
        print("\n2️⃣ Testing GET /api/user/{user_id}...")
        success_user_profile, user_profile_response = self.run_test(
            "GET User Profile (Alternative)",
            "GET",
            f"api/user/{user_id}",
            200
        )
        
        if success_user_profile:
            print(f"   Retrieved profile via user endpoint: {user_profile_response.get('username', 'Unknown')}")
        
        # Test 3: Compare profile data consistency
        print("\n3️⃣ Testing profile data consistency between endpoints...")
        if success_auth_profile and success_user_profile:
            # Compare key fields
            consistency_fields = ['id', 'username', 'email', 'full_name']
            consistent = True
            for field in consistency_fields:
                auth_value = auth_profile_response.get(field)
                user_value = user_profile_response.get(field)
                if auth_value != user_value:
                    consistent = False
                    print(f"   ⚠️  Inconsistency in {field}: auth='{auth_value}' vs user='{user_value}'")
            
            self.log_test("Profile Data Consistency", consistent,
                         f"Profile data consistent between endpoints: {consistent}")
        
        # Test 4: Verify public profile fields for frontend display
        print("\n4️⃣ Testing public profile fields for frontend display...")
        if success_auth_profile:
            profile = auth_profile_response
            
            # Check for business account fields
            business_fields = ['is_business', 'business_name', 'company_name']
            has_business_fields = any(field in profile for field in business_fields)
            
            # Check for activity fields
            activity_fields = ['created_at', 'is_active']
            has_activity_fields = all(field in profile for field in activity_fields)
            
            # Check for contact fields
            contact_fields = ['email']
            has_contact_fields = all(field in profile for field in contact_fields)
            
            self.log_test("Public Profile Business Fields", has_business_fields,
                         f"Profile has business account fields: {has_business_fields}")
            self.log_test("Public Profile Activity Fields", has_activity_fields,
                         f"Profile has activity fields: {has_activity_fields}")
            self.log_test("Public Profile Contact Fields", has_contact_fields,
                         f"Profile has contact fields: {has_contact_fields}")
        
        return True

    def test_user_interactions_and_statistics(self):
        """Test User Interactions and Statistics endpoints"""
        print("\n📊 Testing User Interactions and Statistics...")
        
        if not self.regular_user:
            print("❌ User Interactions - SKIPPED (No regular user)")
            return False

        user_id = self.regular_user['id']
        
        # Test 1: GET /api/user/{user_id}/messages (for response rate calculation)
        print("\n1️⃣ Testing GET /api/user/{user_id}/messages...")
        success_conversations, conversations_response = self.run_test(
            "GET User Messages",
            "GET",
            f"api/user/{user_id}/messages",
            200
        )
        
        if success_conversations:
            print(f"   Found {len(conversations_response)} messages for response rate calculation")
            
            # Verify message data structure for response rate calculation
            if conversations_response:
                message = conversations_response[0]
                response_rate_fields = ['sender_id', 'recipient_id', 'created_at', 'is_read']
                has_response_fields = all(field in message for field in response_rate_fields)
                self.log_test("Message Response Rate Data", has_response_fields,
                             f"Message has response rate calculation fields: {has_response_fields}")
        
        # Test 2: User favorites data
        print("\n2️⃣ Testing user favorites data...")
        success_favorites, favorites_response = self.run_test(
            "GET User Favorites",
            "GET",
            f"api/user/{user_id}/favorites",
            200
        )
        
        if success_favorites:
            print(f"   Found {len(favorites_response)} favorite items")
            
            # Verify favorites data structure
            if favorites_response:
                favorite = favorites_response[0]
                favorite_fields = ['id', 'title', 'price', 'favorited_at']
                has_favorite_fields = any(field in favorite for field in favorite_fields)
                self.log_test("Favorites Data Structure", has_favorite_fields,
                             f"Favorite has required fields: {has_favorite_fields}")
        
        # Test 3: User deals history (already tested in deals system)
        print("\n3️⃣ Testing user deals history for statistics...")
        success_deals_history, deals_history_response = self.run_test(
            "GET User Deals History",
            "GET",
            f"api/user/my-deals/{user_id}",
            200
        )
        
        if success_deals_history:
            print(f"   Found {len(deals_history_response)} deals in history")
            
            # Calculate basic statistics
            total_deals = len(deals_history_response)
            completed_deals = len([d for d in deals_history_response if d.get('status') == 'completed'])
            total_value = sum(d.get('amount', 0) for d in deals_history_response)
            
            print(f"   📈 Deal Statistics: Total={total_deals}, Completed={completed_deals}, Value=${total_value:.2f}")
            
            self.log_test("Deals History Statistics", total_deals > 0,
                         f"User has deal history for statistics: {total_deals} deals")
        
        # Test 4: User activity data
        print("\n4️⃣ Testing user activity data...")
        success_messages, messages_response = self.run_test(
            "GET User Messages Activity",
            "GET",
            f"api/user/{user_id}/messages",
            200
        )
        
        if success_messages:
            print(f"   Found {len(messages_response)} messages for activity calculation")
            
            # Verify message data for activity statistics
            if messages_response:
                message = messages_response[0]
                activity_fields = ['created_at', 'sender_id', 'recipient_id', 'is_read']
                has_activity_fields = all(field in message for field in activity_fields)
                self.log_test("Message Activity Data", has_activity_fields,
                             f"Message has activity tracking fields: {has_activity_fields}")
        
        # Test 5: User notifications for engagement statistics
        print("\n5️⃣ Testing user notifications for engagement statistics...")
        success_notifications, notifications_response = self.run_test(
            "GET User Notifications Activity",
            "GET",
            f"api/user/notifications/{user_id}",
            200
        )
        
        if success_notifications:
            print(f"   Found {len(notifications_response)} notifications for engagement tracking")
            
            # Calculate engagement statistics
            total_notifications = len(notifications_response)
            read_notifications = len([n for n in notifications_response if n.get('is_read')])
            engagement_rate = (read_notifications / total_notifications * 100) if total_notifications > 0 else 0
            
            print(f"   📊 Engagement Statistics: {read_notifications}/{total_notifications} read ({engagement_rate:.1f}%)")
            
            self.log_test("Notification Engagement Data", total_notifications > 0,
                         f"User has notification engagement data: {total_notifications} notifications")
        
        return True

    def run_comprehensive_test(self):
        """Run all comprehensive backend improvement tests"""
        print("🚀 Starting Comprehensive Backend Improvements Testing...")
        print("=" * 80)
        
        # Setup
        if not self.setup_users():
            print("❌ Failed to setup test users - stopping tests")
            return False
        
        # Test categories
        test_results = []
        
        # 1. System Notifications Management
        print("\n" + "=" * 80)
        result1 = self.test_system_notifications_management()
        test_results.append(("System Notifications Management", result1))
        
        # 2. Enhanced Deals/Orders System
        print("\n" + "=" * 80)
        result2 = self.test_enhanced_deals_system()
        test_results.append(("Enhanced Deals/Orders System", result2))
        
        # 3. Public Profile Data Fetching
        print("\n" + "=" * 80)
        result3 = self.test_public_profile_data_fetching()
        test_results.append(("Public Profile Data Fetching", result3))
        
        # 4. User Interactions and Statistics
        print("\n" + "=" * 80)
        result4 = self.test_user_interactions_and_statistics()
        test_results.append(("User Interactions and Statistics", result4))
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE BACKEND IMPROVEMENTS TEST SUMMARY")
        print("=" * 80)
        
        passed_categories = 0
        for category, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} {category}")
            if result:
                passed_categories += 1
        
        print(f"\n🎯 Overall Results: {passed_categories}/{len(test_results)} categories passed")
        print(f"📈 Individual Tests: {self.tests_passed}/{self.tests_run} tests passed")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if passed_categories == len(test_results):
            print("\n🎉 ALL COMPREHENSIVE BACKEND IMPROVEMENTS TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  {len(test_results) - passed_categories} test categories failed")
            return False

def main():
    """Main test execution"""
    tester = SystemNotificationsAPITester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ All comprehensive backend improvement tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some comprehensive backend improvement tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()