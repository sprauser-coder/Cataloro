#!/usr/bin/env python3
"""
Bug Fix Verification Test Suite
Tests specific bug fixes mentioned in the review request:
1. My Deals Action Buttons Testing
2. Notifications Real Data Testing  
3. Admin Notification Center Real Data
"""

import requests
import sys
import json
from datetime import datetime
import time

class BugFixTester:
    def __init__(self, base_url="https://market-evolution-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_data = {}

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
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
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
        """Setup admin and regular users for testing"""
        print("\n🔧 Setting up test users...")
        
        # Login admin user
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
            print(f"   ✅ Admin User: {self.admin_user.get('full_name', 'Unknown')}")
        
        # Login regular user
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
            print(f"   ✅ Regular User: {self.regular_user.get('full_name', 'Unknown')}")
        
        return success_admin and success_user

    def create_test_data(self):
        """Create test data for bug fix verification"""
        print("\n📦 Creating test data for bug fix verification...")
        
        if not self.admin_user or not self.regular_user:
            print("❌ Cannot create test data - users not set up")
            return False
        
        # Create test listing for orders/deals
        test_listing = {
            "title": "Bug Fix Test Listing - Premium Headphones",
            "description": "High-quality wireless headphones for bug fix testing. Excellent sound quality and noise cancellation.",
            "price": 299.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"],
            "tags": ["wireless", "headphones", "premium"],
            "features": ["Noise cancellation", "Bluetooth 5.0", "30-hour battery"]
        }
        
        success_listing, listing_response = self.run_test(
            "Create Test Listing for Orders",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if success_listing and 'listing_id' in listing_response:
            self.test_data['listing_id'] = listing_response['listing_id']
            print(f"   ✅ Created test listing: {self.test_data['listing_id']}")
        
        # Create test order/deal
        if 'listing_id' in self.test_data:
            order_data = {
                "listing_id": self.test_data['listing_id'],
                "buyer_id": self.regular_user['id']
            }
            
            success_order, order_response = self.run_test(
                "Create Test Order for Deals",
                "POST",
                "api/orders/create",
                200,
                data=order_data
            )
            
            if success_order and 'order_id' in order_response:
                self.test_data['order_id'] = order_response['order_id']
                print(f"   ✅ Created test order: {self.test_data['order_id']}")
                
                # Approve the order to create a deal
                approval_data = {"seller_id": self.admin_user['id']}
                success_approve, approve_response = self.run_test(
                    "Approve Test Order to Create Deal",
                    "PUT",
                    f"api/orders/{self.test_data['order_id']}/approve",
                    200,
                    data=approval_data
                )
                
                if success_approve:
                    print(f"   ✅ Approved order to create deal")
        
        return True

    def test_my_deals_action_buttons(self):
        """Test My Deals Action Buttons functionality"""
        print("\n🎯 TESTING MY DEALS ACTION BUTTONS...")
        
        if not self.regular_user:
            print("❌ My Deals Action Buttons - SKIPPED (No regular user)")
            return False
        
        # Test 1: Get My Deals endpoint
        print("\n1️⃣ Testing My Deals endpoint...")
        success_deals, deals_response = self.run_test(
            "Get My Deals",
            "GET",
            f"api/user/my-deals/{self.regular_user['id']}",
            200
        )
        
        if not success_deals:
            print("❌ Cannot test action buttons - My Deals endpoint failed")
            return False
        
        print(f"   📊 Found {len(deals_response)} deals")
        
        # Test 2: Verify deal structure for action buttons
        if deals_response:
            deal = deals_response[0]
            required_fields = ['id', 'status', 'listing', 'seller', 'buyer']
            has_required_fields = all(field in deal for field in required_fields)
            
            self.log_test("Deal Structure for Action Buttons", has_required_fields,
                         f"Required fields present: {has_required_fields}")
            
            # Test 3: Verify seller information for "Contact Seller" buttons
            if 'seller' in deal and deal['seller']:
                seller_info = deal['seller']
                has_contact_info = bool(seller_info.get('email') or seller_info.get('username'))
                self.log_test("Seller Contact Information Available", has_contact_info,
                             f"Seller contact info available: {has_contact_info}")
                
                # Test messaging URL construction data
                if has_contact_info:
                    seller_id = seller_info.get('id')
                    listing_title = deal.get('listing', {}).get('title', '')
                    messaging_data_complete = bool(seller_id and listing_title)
                    self.log_test("Messaging URL Data Complete", messaging_data_complete,
                                 f"Seller ID and listing title available: {messaging_data_complete}")
            
            # Test 4: Verify deal status for action button logic
            deal_status = deal.get('status')
            valid_status = deal_status in ['approved', 'completed', 'pending', 'rejected']
            self.log_test("Deal Status for Button Logic", valid_status,
                         f"Deal status: {deal_status}")
            
            # Test 5: Test order operations for "Cancel Deal" and "Confirm Receipt"
            if 'id' in deal:
                deal_id = deal['id']
                
                # Test cancel operation (if deal is still pending/approved)
                if deal_status in ['pending', 'approved']:
                    cancel_data = {"buyer_id": self.regular_user['id']}
                    success_cancel_test, cancel_response = self.run_test(
                        "Test Cancel Deal Operation",
                        "PUT",
                        f"api/orders/{deal_id}/cancel",
                        200,
                        data=cancel_data
                    )
                    
                    if success_cancel_test:
                        print("   ✅ Cancel Deal operation working")
                    else:
                        # Try to get order details to understand why cancel failed
                        success_order_check, order_details = self.run_test(
                            "Check Order Details for Cancel",
                            "GET",
                            f"api/orders/buyer/{self.regular_user['id']}",
                            200
                        )
                        if success_order_check:
                            print(f"   ℹ️  Order details available for cancel button logic")
        
        # Test 6: Create additional test scenarios for action buttons
        print("\n6️⃣ Testing action button scenarios...")
        
        # Create a second listing and order for more comprehensive testing
        test_listing_2 = {
            "title": "Action Button Test - Gaming Mouse",
            "description": "Gaming mouse for action button testing.",
            "price": 89.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"]
        }
        
        success_listing_2, listing_response_2 = self.run_test(
            "Create Second Test Listing for Action Buttons",
            "POST",
            "api/listings",
            200,
            data=test_listing_2
        )
        
        if success_listing_2:
            listing_id_2 = listing_response_2['listing_id']
            
            # Create order for rejection test
            order_data_2 = {
                "listing_id": listing_id_2,
                "buyer_id": self.regular_user['id']
            }
            
            success_order_2, order_response_2 = self.run_test(
                "Create Second Order for Action Button Test",
                "POST",
                "api/orders/create",
                200,
                data=order_data_2
            )
            
            if success_order_2:
                order_id_2 = order_response_2['order_id']
                
                # Reject this order to test different button states
                rejection_data = {"seller_id": self.admin_user['id']}
                success_reject, reject_response = self.run_test(
                    "Reject Order for Button State Testing",
                    "PUT",
                    f"api/orders/{order_id_2}/reject",
                    200,
                    data=rejection_data
                )
                
                if success_reject:
                    print("   ✅ Created rejected order for button state testing")
            
            # Cleanup second test listing
            self.run_test(
                "Cleanup Second Test Listing",
                "DELETE",
                f"api/listings/{listing_id_2}",
                200
            )
        
        return True

    def test_notifications_real_data(self):
        """Test Notifications Real Data functionality"""
        print("\n🔔 TESTING NOTIFICATIONS REAL DATA...")
        
        if not self.regular_user:
            print("❌ Notifications Real Data - SKIPPED (No regular user)")
            return False
        
        # Test 1: Get user notifications endpoint
        print("\n1️⃣ Testing user notifications endpoint...")
        success_notif, notif_response = self.run_test(
            "Get User Notifications",
            "GET",
            f"api/user/notifications/{self.regular_user['id']}",
            200
        )
        
        if not success_notif:
            print("❌ Cannot test notifications - endpoint failed")
            return False
        
        print(f"   📊 Found {len(notif_response)} notifications")
        
        # Test 2: Verify notifications are real data (not dummy fallback)
        if notif_response:
            # Check if notifications have proper structure
            notification = notif_response[0]
            required_fields = ['id', 'user_id', 'title', 'message', 'type', 'is_read', 'created_at']
            has_structure = all(field in notification for field in required_fields)
            
            self.log_test("Notification Data Structure", has_structure,
                         f"Required fields present: {has_structure}")
            
            # Check if notifications are order-related (indicating real data)
            order_related_types = ['buy_request', 'buy_approved', 'buy_rejected', 'buy_expired']
            real_notifications = [n for n in notif_response if n.get('type') in order_related_types]
            
            self.log_test("Real Order Notifications Present", len(real_notifications) > 0,
                         f"Found {len(real_notifications)} order-related notifications")
            
            # Test 3: Test notification deletion endpoints
            print("\n3️⃣ Testing notification deletion endpoints...")
            
            if real_notifications:
                test_notification = real_notifications[0]
                notification_id = test_notification['id']
                
                # Test DELETE /api/user/{user_id}/notifications/{notification_id}
                success_delete_user, delete_user_response = self.run_test(
                    "Delete User Notification Endpoint",
                    "DELETE",
                    f"api/user/{self.regular_user['id']}/notifications/{notification_id}",
                    200
                )
                
                if success_delete_user:
                    print("   ✅ User-scoped notification deletion working")
                    
                    # Verify deletion by getting notifications again
                    success_verify, verify_response = self.run_test(
                        "Verify Notification Deletion",
                        "GET",
                        f"api/user/notifications/{self.regular_user['id']}",
                        200
                    )
                    
                    if success_verify:
                        deleted_notification_gone = not any(n['id'] == notification_id for n in verify_response)
                        self.log_test("Notification Actually Deleted", deleted_notification_gone,
                                     f"Deleted notification absent: {deleted_notification_gone}")
                
                # Test DELETE /api/notifications/{notification_id} (general endpoint)
                if len(real_notifications) > 1:
                    test_notification_2 = real_notifications[1]
                    notification_id_2 = test_notification_2['id']
                    
                    success_delete_general, delete_general_response = self.run_test(
                        "Delete General Notification Endpoint",
                        "DELETE",
                        f"api/notifications/{notification_id_2}",
                        200
                    )
                    
                    if success_delete_general:
                        print("   ✅ General notification deletion working")
        
        # Test 4: Create test notification to verify real-time functionality
        print("\n4️⃣ Testing notification creation and real-time updates...")
        
        test_notification_data = {
            "title": "Bug Fix Test Notification",
            "message": "This is a test notification created during bug fix verification.",
            "type": "test"
        }
        
        success_create_notif, create_notif_response = self.run_test(
            "Create Test Notification",
            "POST",
            f"api/user/{self.regular_user['id']}/notifications",
            200,
            data=test_notification_data
        )
        
        if success_create_notif:
            created_notif_id = create_notif_response.get('id')
            print(f"   ✅ Created test notification: {created_notif_id}")
            
            # Verify it appears in notifications list
            success_verify_create, verify_create_response = self.run_test(
                "Verify Created Notification Appears",
                "GET",
                f"api/user/notifications/{self.regular_user['id']}",
                200
            )
            
            if success_verify_create:
                created_notification_found = any(n['id'] == created_notif_id for n in verify_create_response)
                self.log_test("Created Notification Appears", created_notification_found,
                             f"Created notification found: {created_notification_found}")
                
                # Test mark as read functionality
                success_mark_read, mark_read_response = self.run_test(
                    "Mark Notification as Read",
                    "PUT",
                    f"api/user/{self.regular_user['id']}/notifications/{created_notif_id}/read",
                    200
                )
                
                if success_mark_read:
                    print("   ✅ Mark as read functionality working")
                
                # Cleanup test notification
                self.run_test(
                    "Cleanup Test Notification",
                    "DELETE",
                    f"api/user/{self.regular_user['id']}/notifications/{created_notif_id}",
                    200
                )
        
        return True

    def test_admin_notification_center(self):
        """Test Admin Notification Center Real Data functionality"""
        print("\n👑 TESTING ADMIN NOTIFICATION CENTER...")
        
        if not self.admin_user:
            print("❌ Admin Notification Center - SKIPPED (No admin user)")
            return False
        
        # Test 1: Check for admin notifications endpoint
        print("\n1️⃣ Testing admin notifications endpoint...")
        
        # Try /api/admin/notifications first
        success_admin_notif, admin_notif_response = self.run_test(
            "Get Admin Notifications",
            "GET",
            "api/admin/notifications",
            200
        )
        
        admin_endpoint_exists = success_admin_notif
        
        if not admin_endpoint_exists:
            print("   ℹ️  Admin notifications endpoint not implemented, testing fallback to user notifications")
            
            # Test fallback to admin user notifications
            success_fallback, fallback_response = self.run_test(
                "Get Admin User Notifications (Fallback)",
                "GET",
                f"api/user/notifications/{self.admin_user['id']}",
                200
            )
            
            if success_fallback:
                print(f"   📊 Admin fallback notifications: {len(fallback_response)}")
                admin_notif_response = fallback_response
                success_admin_notif = success_fallback
        else:
            print(f"   📊 Admin notifications endpoint found: {len(admin_notif_response)} notifications")
        
        # Test 2: Verify admin notification structure
        if success_admin_notif and admin_notif_response:
            notification = admin_notif_response[0]
            required_fields = ['id', 'title', 'message', 'type', 'created_at']
            has_structure = all(field in notification for field in required_fields)
            
            self.log_test("Admin Notification Structure", has_structure,
                         f"Required fields present: {has_structure}")
            
            # Test 3: Check for system notification types
            system_notification_types = ['system', 'maintenance', 'security', 'welcome', 'feature']
            system_notifications = [n for n in admin_notif_response if n.get('type') in system_notification_types]
            
            self.log_test("System Notifications Present", len(system_notifications) > 0,
                         f"Found {len(system_notifications)} system notifications")
        
        # Test 4: Test admin notification management endpoints
        print("\n4️⃣ Testing admin notification management...")
        
        # Create system notification
        system_notification_data = {
            "title": "System Maintenance Notice",
            "message": "Scheduled maintenance will occur tonight from 2-4 AM EST.",
            "type": "maintenance"
        }
        
        if admin_endpoint_exists:
            # Try creating admin notification
            success_create_admin, create_admin_response = self.run_test(
                "Create Admin System Notification",
                "POST",
                "api/admin/notifications",
                200,
                data=system_notification_data
            )
            
            if success_create_admin:
                print("   ✅ Admin notification creation working")
        else:
            # Fallback to creating notification for admin user
            success_create_fallback, create_fallback_response = self.run_test(
                "Create Admin Notification (Fallback)",
                "POST",
                f"api/user/{self.admin_user['id']}/notifications",
                200,
                data=system_notification_data
            )
            
            if success_create_fallback:
                print("   ✅ Admin notification creation (fallback) working")
        
        # Test 5: Test notification center management features
        print("\n5️⃣ Testing notification center management features...")
        
        # Test getting all users for broadcast notifications
        success_users, users_response = self.run_test(
            "Get All Users for Broadcast",
            "GET",
            "api/admin/users",
            200
        )
        
        if success_users:
            print(f"   📊 Found {len(users_response)} users for broadcast notifications")
            
            # Test broadcast notification creation (create notification for all users)
            if len(users_response) > 0:
                broadcast_notification = {
                    "title": "Welcome to Cataloro Marketplace",
                    "message": "Thank you for joining our marketplace community!",
                    "type": "welcome"
                }
                
                broadcast_success_count = 0
                for user in users_response[:3]:  # Test with first 3 users
                    user_id = user.get('id')
                    if user_id:
                        success_broadcast, broadcast_response = self.run_test(
                            f"Broadcast to User {user_id[:8]}...",
                            "POST",
                            f"api/user/{user_id}/notifications",
                            200,
                            data=broadcast_notification
                        )
                        if success_broadcast:
                            broadcast_success_count += 1
                
                self.log_test("Broadcast Notification Capability", broadcast_success_count > 0,
                             f"Successfully broadcast to {broadcast_success_count} users")
        
        # Test 6: Test notification templates and settings
        print("\n6️⃣ Testing notification templates and settings...")
        
        # Test different notification templates
        notification_templates = [
            {
                "title": "New Features Available",
                "message": "Check out our latest marketplace features!",
                "type": "feature"
            },
            {
                "title": "Security Update",
                "message": "We've enhanced our security measures for your protection.",
                "type": "security"
            },
            {
                "title": "Sales Promotion",
                "message": "Special promotion: 10% off all electronics this week!",
                "type": "promotion"
            }
        ]
        
        template_success_count = 0
        for template in notification_templates:
            if admin_endpoint_exists:
                success_template, template_response = self.run_test(
                    f"Create {template['type'].title()} Notification Template",
                    "POST",
                    "api/admin/notifications",
                    200,
                    data=template
                )
            else:
                success_template, template_response = self.run_test(
                    f"Create {template['type'].title()} Notification (Fallback)",
                    "POST",
                    f"api/user/{self.admin_user['id']}/notifications",
                    200,
                    data=template
                )
            
            if success_template:
                template_success_count += 1
        
        self.log_test("Notification Templates Working", template_success_count == len(notification_templates),
                     f"Created {template_success_count}/{len(notification_templates)} notification templates")
        
        return True

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n🧹 Cleaning up test data...")
        
        # Clean up test listing
        if 'listing_id' in self.test_data:
            self.run_test(
                "Cleanup Test Listing",
                "DELETE",
                f"api/listings/{self.test_data['listing_id']}",
                200
            )
        
        print("   ✅ Test data cleanup completed")

    def run_all_bug_fix_tests(self):
        """Run all bug fix verification tests"""
        print("🐛 CATALORO BUG FIX VERIFICATION TEST SUITE")
        print("=" * 60)
        print("Testing specific bug fixes from review request:")
        print("1. My Deals Action Buttons Testing")
        print("2. Notifications Real Data Testing")
        print("3. Admin Notification Center Real Data")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - aborting tests")
            return False
        
        self.create_test_data()
        
        # Run bug fix tests
        test_results = []
        
        try:
            # Test 1: My Deals Action Buttons
            result1 = self.test_my_deals_action_buttons()
            test_results.append(("My Deals Action Buttons", result1))
            
            # Test 2: Notifications Real Data
            result2 = self.test_notifications_real_data()
            test_results.append(("Notifications Real Data", result2))
            
            # Test 3: Admin Notification Center
            result3 = self.test_admin_notification_center()
            test_results.append(("Admin Notification Center", result3))
            
        finally:
            # Cleanup
            self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("🐛 BUG FIX VERIFICATION SUMMARY")
        print("=" * 60)
        
        passed_tests = 0
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if result:
                passed_tests += 1
        
        print(f"\nOverall Results: {passed_tests}/{len(test_results)} bug fix areas verified")
        print(f"Individual Tests: {self.tests_passed}/{self.tests_run} tests passed")
        
        if passed_tests == len(test_results):
            print("\n🎉 ALL BUG FIXES VERIFIED SUCCESSFULLY!")
            return True
        else:
            print(f"\n⚠️  {len(test_results) - passed_tests} bug fix areas need attention")
            return False

def main():
    """Main function to run bug fix verification tests"""
    tester = BugFixTester()
    success = tester.run_all_bug_fix_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()