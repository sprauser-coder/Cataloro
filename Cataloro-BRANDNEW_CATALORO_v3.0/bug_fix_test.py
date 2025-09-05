#!/usr/bin/env python3
"""
Bug Fix Testing Suite for Cataloro Marketplace
Tests specific bug fixes for notification system and order management
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class BugFixTester:
    def __init__(self, base_url="https://market-refactor.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_notifications = []
        self.test_orders = []

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
        
        # Login admin
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
            print(f"   Regular User ID: {self.regular_user['id']}")
        
        return success_admin and success_user

    def test_notification_fetching(self):
        """Test notification fetching endpoints /api/notifications/{user_id}"""
        print("\n📢 Testing Notification Fetching...")
        
        if not self.regular_user:
            print("❌ Notification Fetching - SKIPPED (No user logged in)")
            return False
        
        # Test fetching notifications for regular user
        success, response = self.run_test(
            "Fetch User Notifications",
            "GET",
            f"api/user/notifications/{self.regular_user['id']}",
            200
        )
        
        if success:
            print(f"   Found {len(response)} notifications")
            self.test_notifications = response
            
            # Verify notification structure
            if response:
                notification = response[0]
                required_fields = ['id', 'user_id', 'title', 'message', 'type', 'is_read', 'created_at']
                has_required_fields = all(field in notification for field in required_fields)
                self.log_test("Notification Structure", has_required_fields,
                             f"Required fields present: {has_required_fields}")
                
                if has_required_fields:
                    print(f"   Sample notification: {notification['title']} - {notification['type']}")
        
        return success

    def test_notification_read_status(self):
        """Test notification read status endpoints /api/notifications/{notification_id}/read with PUT method"""
        print("\n📖 Testing Notification Read Status...")
        
        if not self.test_notifications or not self.regular_user:
            print("❌ Notification Read Status - SKIPPED (No notifications or user)")
            return False
        
        # Find an unread notification
        unread_notification = None
        for notification in self.test_notifications:
            if not notification.get('is_read', True):
                unread_notification = notification
                break
        
        if not unread_notification:
            # Create a test notification first
            print("   Creating test notification for read status testing...")
            success_create, create_response = self.run_test(
                "Create Test Notification",
                "POST",
                f"api/user/{self.regular_user['id']}/notifications",
                200,
                data={
                    "title": "Test Notification for Read Status",
                    "message": "This is a test notification to verify read status functionality",
                    "type": "test"
                }
            )
            
            if success_create and 'id' in create_response:
                unread_notification = {
                    'id': create_response['id'],
                    'user_id': self.regular_user['id'],
                    'is_read': False
                }
                print(f"   Created test notification with ID: {unread_notification['id']}")
        
        if unread_notification:
            # Test marking notification as read
            success, response = self.run_test(
                "Mark Notification as Read",
                "PUT",
                f"api/user/{self.regular_user['id']}/notifications/{unread_notification['id']}/read",
                200
            )
            
            if success:
                # Verify the notification is now marked as read
                success_verify, verify_response = self.run_test(
                    "Verify Notification Read Status",
                    "GET",
                    f"api/user/notifications/{self.regular_user['id']}",
                    200
                )
                
                if success_verify:
                    updated_notification = None
                    for notification in verify_response:
                        if notification['id'] == unread_notification['id']:
                            updated_notification = notification
                            break
                    
                    if updated_notification:
                        is_read = updated_notification.get('is_read', False)
                        self.log_test("Notification Read Status Update", is_read,
                                     f"Notification marked as read: {is_read}")
                        return is_read
            
            return success
        else:
            print("❌ No unread notifications found for testing")
            return False

    def test_notification_deletion(self):
        """Test notification deletion endpoints /api/notifications/{notification_id} with DELETE method"""
        print("\n🗑️ Testing Notification Deletion...")
        
        if not self.regular_user:
            print("❌ Notification Deletion - SKIPPED (No user logged in)")
            return False
        
        # Create a test notification for deletion
        print("   Creating test notification for deletion testing...")
        success_create, create_response = self.run_test(
            "Create Test Notification for Deletion",
            "POST",
            f"api/user/{self.regular_user['id']}/notifications",
            200,
            data={
                "title": "Test Notification for Deletion",
                "message": "This notification will be deleted to test deletion functionality",
                "type": "test_delete"
            }
        )
        
        if not success_create or 'id' not in create_response:
            print("❌ Failed to create test notification for deletion")
            return False
        
        test_notification_id = create_response['id']
        print(f"   Created test notification with ID: {test_notification_id}")
        
        # Get initial notification count
        success_initial, initial_response = self.run_test(
            "Get Initial Notification Count",
            "GET",
            f"api/user/notifications/{self.regular_user['id']}",
            200
        )
        
        initial_count = len(initial_response) if success_initial else 0
        print(f"   Initial notification count: {initial_count}")
        
        # Test deletion - Note: The endpoint might be different based on backend implementation
        # Let's try the user-specific deletion endpoint first
        success_delete, delete_response = self.run_test(
            "Delete Notification (User Endpoint)",
            "DELETE",
            f"api/user/{self.regular_user['id']}/notifications/{test_notification_id}",
            200
        )
        
        if not success_delete:
            # Try alternative endpoint structure
            success_delete, delete_response = self.run_test(
                "Delete Notification (Alternative Endpoint)",
                "DELETE",
                f"api/notifications/{test_notification_id}",
                200
            )
        
        if success_delete:
            print(f"   ✅ Notification deleted successfully")
            
            # Verify deletion - check that notification doesn't reappear
            success_verify, verify_response = self.run_test(
                "Verify Notification Deletion",
                "GET",
                f"api/user/notifications/{self.regular_user['id']}",
                200
            )
            
            if success_verify:
                final_count = len(verify_response)
                deleted_notification_found = any(n['id'] == test_notification_id for n in verify_response)
                
                deletion_verified = not deleted_notification_found and final_count == (initial_count - 1)
                self.log_test("Notification Deletion Verification", deletion_verified,
                             f"Deleted notification absent: {not deleted_notification_found}, Count: {final_count} (expected: {initial_count - 1})")
                
                return deletion_verified
        
        return success_delete

    def test_deleted_notifications_persistence(self):
        """Verify that deleted notifications don't reappear in subsequent fetches"""
        print("\n🔄 Testing Deleted Notifications Persistence...")
        
        if not self.regular_user:
            print("❌ Notification Persistence - SKIPPED (No user logged in)")
            return False
        
        # Create multiple test notifications
        created_notifications = []
        for i in range(3):
            success_create, create_response = self.run_test(
                f"Create Test Notification {i+1} for Persistence Test",
                "POST",
                f"api/user/{self.regular_user['id']}/notifications",
                200,
                data={
                    "title": f"Persistence Test Notification {i+1}",
                    "message": f"Test notification {i+1} for persistence testing",
                    "type": "persistence_test"
                }
            )
            
            if success_create and 'id' in create_response:
                created_notifications.append(create_response['id'])
        
        print(f"   Created {len(created_notifications)} test notifications")
        
        # Delete the first two notifications
        deleted_notifications = []
        for i, notification_id in enumerate(created_notifications[:2]):
            success_delete, _ = self.run_test(
                f"Delete Persistence Test Notification {i+1}",
                "DELETE",
                f"api/user/{self.regular_user['id']}/notifications/{notification_id}",
                200
            )
            
            if success_delete:
                deleted_notifications.append(notification_id)
        
        print(f"   Deleted {len(deleted_notifications)} notifications")
        
        # Make multiple subsequent fetches to verify persistence
        persistence_verified = True
        for fetch_attempt in range(3):
            success_fetch, fetch_response = self.run_test(
                f"Persistence Check Fetch {fetch_attempt + 1}",
                "GET",
                f"api/user/notifications/{self.regular_user['id']}",
                200
            )
            
            if success_fetch:
                # Check if any deleted notifications reappeared
                reappeared_notifications = []
                for notification in fetch_response:
                    if notification['id'] in deleted_notifications:
                        reappeared_notifications.append(notification['id'])
                
                if reappeared_notifications:
                    persistence_verified = False
                    print(f"   ❌ Fetch {fetch_attempt + 1}: Deleted notifications reappeared: {reappeared_notifications}")
                else:
                    print(f"   ✅ Fetch {fetch_attempt + 1}: No deleted notifications found")
        
        # Cleanup remaining test notification
        if len(created_notifications) > 2:
            self.run_test(
                "Cleanup Remaining Test Notification",
                "DELETE",
                f"api/user/{self.regular_user['id']}/notifications/{created_notifications[2]}",
                200
            )
        
        self.log_test("Deleted Notifications Persistence", persistence_verified,
                     f"Deleted notifications stayed deleted across multiple fetches: {persistence_verified}")
        
        return persistence_verified

    def test_order_status_retrieval(self):
        """Test approved/denied order endpoints /api/orders/buyer/{user_id}"""
        print("\n📦 Testing Order Status Retrieval...")
        
        if not self.regular_user or not self.admin_user:
            print("❌ Order Status Retrieval - SKIPPED (Need both users)")
            return False
        
        # Create test listing for order testing
        test_listing = {
            "title": "Order Status Test - Bluetooth Speaker",
            "description": "Premium Bluetooth speaker for order status testing",
            "price": 199.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400"]
        }
        
        success_listing, listing_response = self.run_test(
            "Create Test Listing for Order Status",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_listing or 'listing_id' not in listing_response:
            print("❌ Failed to create test listing for order status testing")
            return False
        
        listing_id = listing_response['listing_id']
        print(f"   Created test listing: {listing_id}")
        
        # Create buy request
        order_data = {
            "listing_id": listing_id,
            "buyer_id": self.regular_user['id']
        }
        
        success_order, order_response = self.run_test(
            "Create Buy Request for Status Test",
            "POST",
            "api/orders/create",
            200,
            data=order_data
        )
        
        if not success_order or 'order_id' not in order_response:
            print("❌ Failed to create buy request for order status testing")
            return False
        
        order_id = order_response['order_id']
        print(f"   Created buy request: {order_id}")
        
        # Test getting buyer orders (should show pending status)
        success_buyer_pending, buyer_pending_response = self.run_test(
            "Get Buyer Orders (Pending Status)",
            "GET",
            f"api/orders/buyer/{self.regular_user['id']}",
            200
        )
        
        pending_order_found = False
        if success_buyer_pending:
            for order in buyer_pending_response:
                if order['id'] == order_id and order['status'] == 'pending':
                    pending_order_found = True
                    print(f"   ✅ Found pending order: {order['listing']['title']}")
                    break
        
        self.log_test("Buyer Orders Pending Status", pending_order_found,
                     f"Pending order found in buyer orders: {pending_order_found}")
        
        # Approve the order
        approval_data = {"seller_id": self.admin_user['id']}
        success_approve, _ = self.run_test(
            "Approve Order for Status Test",
            "PUT",
            f"api/orders/{order_id}/approve",
            200,
            data=approval_data
        )
        
        approved_order_found = False
        if success_approve:
            # Test getting buyer orders (should show approved status)
            success_buyer_approved, buyer_approved_response = self.run_test(
                "Get Buyer Orders (Approved Status)",
                "GET",
                f"api/orders/buyer/{self.regular_user['id']}",
                200
            )
            
            if success_buyer_approved:
                for order in buyer_approved_response:
                    if order['id'] == order_id and order['status'] == 'approved':
                        approved_order_found = True
                        print(f"   ✅ Found approved order: {order['listing']['title']}")
                        break
        
        self.log_test("Buyer Orders Approved Status", approved_order_found,
                     f"Approved order found in buyer orders: {approved_order_found}")
        
        # Test rejection with another order
        # Create another test listing and order for rejection test
        reject_test_listing = {
            "title": "Order Rejection Test - Gaming Mouse",
            "description": "Gaming mouse for order rejection testing",
            "price": 79.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"]
        }
        
        success_reject_listing, reject_listing_response = self.run_test(
            "Create Test Listing for Rejection",
            "POST",
            "api/listings",
            200,
            data=reject_test_listing
        )
        
        rejected_order_found = False
        if success_reject_listing:
            reject_listing_id = reject_listing_response['listing_id']
            
            # Create order for rejection
            reject_order_data = {
                "listing_id": reject_listing_id,
                "buyer_id": self.regular_user['id']
            }
            
            success_reject_order, reject_order_response = self.run_test(
                "Create Order for Rejection Test",
                "POST",
                "api/orders/create",
                200,
                data=reject_order_data
            )
            
            if success_reject_order:
                reject_order_id = reject_order_response['order_id']
                
                # Reject the order
                rejection_data = {"seller_id": self.admin_user['id']}
                success_reject, _ = self.run_test(
                    "Reject Order for Status Test",
                    "PUT",
                    f"api/orders/{reject_order_id}/reject",
                    200,
                    data=rejection_data
                )
                
                if success_reject:
                    # Test getting buyer orders (should show rejected status)
                    success_buyer_rejected, buyer_rejected_response = self.run_test(
                        "Get Buyer Orders (Rejected Status)",
                        "GET",
                        f"api/orders/buyer/{self.regular_user['id']}",
                        200
                    )
                    
                    if success_buyer_rejected:
                        for order in buyer_rejected_response:
                            if order['id'] == reject_order_id and order['status'] == 'rejected':
                                rejected_order_found = True
                                print(f"   ✅ Found rejected order: {order['listing']['title']}")
                                break
            
            # Cleanup reject test listing
            self.run_test(
                "Cleanup Reject Test Listing",
                "DELETE",
                f"api/listings/{reject_listing_id}",
                200
            )
        
        self.log_test("Buyer Orders Rejected Status", rejected_order_found,
                     f"Rejected order found in buyer orders: {rejected_order_found}")
        
        # Cleanup main test listing
        self.run_test(
            "Cleanup Order Status Test Listing",
            "DELETE",
            f"api/listings/{listing_id}",
            200
        )
        
        return pending_order_found and approved_order_found and rejected_order_found

    def test_seller_information_in_orders(self):
        """Check if seller information is included in order responses"""
        print("\n👤 Testing Seller Information in Order Responses...")
        
        if not self.regular_user or not self.admin_user:
            print("❌ Seller Information Test - SKIPPED (Need both users)")
            return False
        
        # Create test listing
        test_listing = {
            "title": "Seller Info Test - Wireless Keyboard",
            "description": "Mechanical keyboard for seller info testing",
            "price": 149.99,
            "category": "Electronics",
            "condition": "Used - Good",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400"]
        }
        
        success_listing, listing_response = self.run_test(
            "Create Test Listing for Seller Info",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_listing:
            return False
        
        listing_id = listing_response['listing_id']
        
        # Create order
        order_data = {
            "listing_id": listing_id,
            "buyer_id": self.regular_user['id']
        }
        
        success_order, order_response = self.run_test(
            "Create Order for Seller Info Test",
            "POST",
            "api/orders/create",
            200,
            data=order_data
        )
        
        if not success_order:
            return False
        
        order_id = order_response['order_id']
        
        # Test buyer orders endpoint for seller information
        success_buyer, buyer_response = self.run_test(
            "Get Buyer Orders for Seller Info",
            "GET",
            f"api/orders/buyer/{self.regular_user['id']}",
            200
        )
        
        seller_info_complete = False
        if success_buyer and buyer_response:
            for order in buyer_response:
                if order['id'] == order_id:
                    seller_info = order.get('seller', {})
                    required_seller_fields = ['id', 'username', 'full_name']
                    has_seller_info = all(field in seller_info for field in required_seller_fields)
                    
                    if has_seller_info:
                        seller_info_complete = True
                        print(f"   ✅ Seller info complete: {seller_info['username']} ({seller_info['full_name']})")
                        
                        # Check contact privacy (should be hidden before approval)
                        contact_hidden = not seller_info.get('email', '')
                        self.log_test("Seller Contact Privacy Before Approval", contact_hidden,
                                     f"Seller contact hidden before approval: {contact_hidden}")
                    else:
                        print(f"   ❌ Missing seller fields: {[f for f in required_seller_fields if f not in seller_info]}")
                    break
        
        self.log_test("Seller Information in Orders", seller_info_complete,
                     f"Complete seller information in order response: {seller_info_complete}")
        
        # Approve order and check if contact details are revealed
        approval_data = {"seller_id": self.admin_user['id']}
        success_approve, _ = self.run_test(
            "Approve Order for Contact Reveal Test",
            "PUT",
            f"api/orders/{order_id}/approve",
            200,
            data=approval_data
        )
        
        contact_revealed = False
        if success_approve:
            success_buyer_after, buyer_after_response = self.run_test(
                "Get Buyer Orders After Approval",
                "GET",
                f"api/orders/buyer/{self.regular_user['id']}",
                200
            )
            
            if success_buyer_after:
                for order in buyer_after_response:
                    if order['id'] == order_id and order['status'] == 'approved':
                        seller_info = order.get('seller', {})
                        contact_revealed = bool(seller_info.get('email', ''))
                        if contact_revealed:
                            print(f"   ✅ Seller contact revealed after approval: {seller_info['email']}")
                        break
        
        self.log_test("Seller Contact Revealed After Approval", contact_revealed,
                     f"Seller contact details revealed after approval: {contact_revealed}")
        
        # Cleanup
        self.run_test(
            "Cleanup Seller Info Test Listing",
            "DELETE",
            f"api/listings/{listing_id}",
            200
        )
        
        return seller_info_complete and contact_revealed

    def test_general_system_health(self):
        """Test that all existing functionality still works after changes"""
        print("\n🏥 Testing General System Health...")
        
        # Test core endpoints
        health_tests = []
        
        # Health check
        success_health, _ = self.run_test(
            "System Health Check",
            "GET",
            "api/health",
            200
        )
        health_tests.append(success_health)
        
        # Authentication
        success_auth, _ = self.run_test(
            "Authentication System Check",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        health_tests.append(success_auth)
        
        # Marketplace browse
        success_browse, browse_response = self.run_test(
            "Marketplace Browse Check",
            "GET",
            "api/marketplace/browse",
            200
        )
        health_tests.append(success_browse)
        
        if success_browse:
            print(f"   Marketplace has {len(browse_response)} active listings")
        
        # Admin dashboard
        success_admin, admin_response = self.run_test(
            "Admin Dashboard Check",
            "GET",
            "api/admin/dashboard",
            200
        )
        health_tests.append(success_admin)
        
        if success_admin and 'kpis' in admin_response:
            kpis = admin_response['kpis']
            print(f"   System KPIs: {kpis.get('total_users', 0)} users, {kpis.get('total_listings', 0)} listings")
        
        # User profile access
        if self.regular_user:
            success_profile, _ = self.run_test(
                "User Profile Access Check",
                "GET",
                f"api/auth/profile/{self.regular_user['id']}",
                200
            )
            health_tests.append(success_profile)
        
        # My listings
        if self.regular_user:
            success_my_listings, _ = self.run_test(
                "My Listings Check",
                "GET",
                f"api/user/my-listings/{self.regular_user['id']}",
                200
            )
            health_tests.append(success_my_listings)
        
        # My deals
        if self.regular_user:
            success_my_deals, _ = self.run_test(
                "My Deals Check",
                "GET",
                f"api/user/my-deals/{self.regular_user['id']}",
                200
            )
            health_tests.append(success_my_deals)
        
        passed_health_tests = sum(health_tests)
        total_health_tests = len(health_tests)
        
        system_healthy = passed_health_tests == total_health_tests
        self.log_test("General System Health", system_healthy,
                     f"System health: {passed_health_tests}/{total_health_tests} core endpoints working")
        
        return system_healthy

    def run_all_bug_fix_tests(self):
        """Run all bug fix tests"""
        print("🐛 CATALORO BUG FIX TESTING SUITE")
        print("=" * 50)
        print("Testing specific bug fixes for notification system and order management")
        print()
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False
        
        # Test results
        test_results = []
        
        # 1. Notification System Testing
        print("\n" + "="*50)
        print("1️⃣ NOTIFICATION SYSTEM TESTING")
        print("="*50)
        
        test_results.append(self.test_notification_fetching())
        test_results.append(self.test_notification_read_status())
        test_results.append(self.test_notification_deletion())
        test_results.append(self.test_deleted_notifications_persistence())
        
        # 2. Shopping Cart & Orders Testing
        print("\n" + "="*50)
        print("2️⃣ SHOPPING CART & ORDERS TESTING")
        print("="*50)
        
        test_results.append(self.test_order_status_retrieval())
        test_results.append(self.test_seller_information_in_orders())
        
        # 3. General System Health
        print("\n" + "="*50)
        print("3️⃣ GENERAL SYSTEM HEALTH")
        print("="*50)
        
        test_results.append(self.test_general_system_health())
        
        # Summary
        print("\n" + "="*50)
        print("🎯 BUG FIX TEST SUMMARY")
        print("="*50)
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print()
        print(f"Major Test Categories: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL BUG FIX TESTS PASSED!")
            print("✅ Notification system fixes working correctly")
            print("✅ Order management fixes working correctly")
            print("✅ System health maintained after changes")
        else:
            print(f"⚠️  {total_tests - passed_tests} test categories failed")
            print("❌ Some bug fixes may need attention")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = BugFixTester()
    success = tester.run_all_bug_fix_tests()
    sys.exit(0 if success else 1)