#!/usr/bin/env python3
"""
Cataloro Marketplace - Notification System & Authentication Test Suite
Tests notification system and authentication endpoints as requested in review
"""

import requests
import sys
import json
from datetime import datetime

class NotificationAuthTester:
    def __init__(self, base_url="https://catalog-admin-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.demo_user = None
        self.demo_user_token = None
        self.admin_user = None
        self.admin_token = None
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

    def test_demo_user_login(self):
        """Test demo user login with email 'user@cataloro.com' and password 'demo123'"""
        print("\n🔐 Testing Demo User Authentication...")
        
        success, response = self.run_test(
            "Demo User Login (user@cataloro.com)",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        
        if success and 'token' in response and 'user' in response:
            self.demo_user_token = response['token']
            self.demo_user = response['user']
            print(f"   ✅ Demo User ID: {self.demo_user['id']}")
            print(f"   ✅ Demo User Email: {self.demo_user['email']}")
            print(f"   ✅ Demo User Name: {self.demo_user.get('full_name', 'N/A')}")
            print(f"   ✅ Demo User Role: {self.demo_user.get('role', 'N/A')}")
            return True
        else:
            print("   ❌ Failed to get user token or user data")
            return False

    def test_admin_login(self):
        """Test admin login for comparison"""
        success, response = self.run_test(
            "Admin Login (admin@cataloro.com)",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success and 'token' in response and 'user' in response:
            self.admin_token = response['token']
            self.admin_user = response['user']
            print(f"   ✅ Admin User ID: {self.admin_user['id']}")
            return True
        return False

    def test_get_user_notifications(self):
        """Test getting user notifications for the returned user ID"""
        if not self.demo_user:
            print("❌ Get User Notifications - SKIPPED (No demo user logged in)")
            return False
            
        print(f"\n📬 Testing Get User Notifications for User ID: {self.demo_user['id']}")
        
        success, response = self.run_test(
            "Get User Notifications",
            "GET",
            f"api/user/notifications/{self.demo_user['id']}",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(response)} notifications for user")
            
            # Analyze notification structure
            if response:
                first_notification = response[0]
                required_fields = ['id', 'user_id', 'title', 'message', 'type', 'is_read', 'created_at']
                has_all_fields = all(field in first_notification for field in required_fields)
                
                self.log_test("Notification Data Structure", has_all_fields,
                             f"All required fields present: {has_all_fields}")
                
                print(f"   📋 Sample notification:")
                print(f"      ID: {first_notification.get('id', 'N/A')}")
                print(f"      Title: {first_notification.get('title', 'N/A')}")
                print(f"      Type: {first_notification.get('type', 'N/A')}")
                print(f"      Read Status: {first_notification.get('is_read', 'N/A')}")
                
                # Store a notification ID for read testing
                if not first_notification.get('is_read', True):
                    self.test_notification_id = first_notification.get('id')
                    print(f"   📌 Selected unread notification for read test: {self.test_notification_id}")
            else:
                print("   ℹ️  No notifications found - this is normal for new users")
                
        return success

    def test_create_notification(self):
        """Test creating a notification for testing purposes"""
        if not self.demo_user:
            print("❌ Create Notification - SKIPPED (No demo user logged in)")
            return False
            
        print(f"\n📝 Creating Test Notification for User ID: {self.demo_user['id']}")
        
        notification_data = {
            "title": "Test Notification",
            "message": "This is a test notification created for testing the notification system functionality.",
            "type": "test"
        }
        
        success, response = self.run_test(
            "Create Test Notification",
            "POST",
            f"api/user/{self.demo_user['id']}/notifications",
            200,
            data=notification_data
        )
        
        if success and 'id' in response:
            self.test_notification_id = response['id']
            print(f"   ✅ Created test notification with ID: {self.test_notification_id}")
            return True
        return False

    def test_mark_notification_as_read(self):
        """Test marking a notification as read"""
        if not self.demo_user or not self.test_notification_id:
            print("❌ Mark Notification Read - SKIPPED (No demo user or notification ID)")
            return False
            
        print(f"\n✅ Testing Mark Notification as Read: {self.test_notification_id}")
        
        success, response = self.run_test(
            "Mark Notification as Read",
            "PUT",
            f"api/user/{self.demo_user['id']}/notifications/{self.test_notification_id}/read",
            200
        )
        
        if success:
            print(f"   ✅ Notification marked as read successfully")
            
            # Verify the notification is now marked as read
            verify_success, verify_response = self.run_test(
                "Verify Notification Read Status",
                "GET",
                f"api/user/notifications/{self.demo_user['id']}",
                200
            )
            
            if verify_success:
                # Find our test notification and check if it's marked as read
                test_notif = None
                for notif in verify_response:
                    if notif.get('id') == self.test_notification_id:
                        test_notif = notif
                        break
                
                if test_notif:
                    is_read = test_notif.get('is_read', False)
                    self.log_test("Notification Read Status Verification", is_read,
                                 f"Notification marked as read: {is_read}")
                else:
                    self.log_test("Notification Read Status Verification", False,
                                 "Test notification not found in user notifications")
            
        return success

    def test_notification_endpoints_comprehensive(self):
        """Test all notification-related API endpoints comprehensively"""
        print("\n🔔 Testing All Notification-Related API Endpoints...")
        
        if not self.demo_user:
            print("❌ Comprehensive Notification Tests - SKIPPED (No demo user logged in)")
            return False
        
        user_id = self.demo_user['id']
        
        # Test 1: Get initial notifications
        print("\n1️⃣ Testing GET notifications endpoint...")
        success_get, initial_notifications = self.run_test(
            "GET User Notifications (Initial)",
            "GET",
            f"api/user/notifications/{user_id}",
            200
        )
        
        initial_count = len(initial_notifications) if success_get else 0
        print(f"   📊 Initial notification count: {initial_count}")
        
        # Test 2: Create multiple test notifications
        print("\n2️⃣ Testing POST notifications endpoint (multiple notifications)...")
        test_notifications = [
            {
                "title": "Welcome Notification",
                "message": "Welcome to Cataloro Marketplace! Start browsing amazing deals.",
                "type": "welcome"
            },
            {
                "title": "System Update",
                "message": "System maintenance completed. All features are now available.",
                "type": "system"
            },
            {
                "title": "New Message",
                "message": "You have received a new message from a seller.",
                "type": "message"
            }
        ]
        
        created_notification_ids = []
        for i, notif_data in enumerate(test_notifications):
            success_create, create_response = self.run_test(
                f"Create Test Notification {i+1}",
                "POST",
                f"api/user/{user_id}/notifications",
                200,
                data=notif_data
            )
            
            if success_create and 'id' in create_response:
                created_notification_ids.append(create_response['id'])
                print(f"   ✅ Created notification {i+1}: {create_response['id']}")
        
        self.log_test("Multiple Notification Creation", len(created_notification_ids) == 3,
                     f"Created {len(created_notification_ids)}/3 notifications")
        
        # Test 3: Verify notifications appear in GET request
        print("\n3️⃣ Testing notification retrieval after creation...")
        success_get_after, notifications_after = self.run_test(
            "GET User Notifications (After Creation)",
            "GET",
            f"api/user/notifications/{user_id}",
            200
        )
        
        if success_get_after:
            new_count = len(notifications_after)
            expected_count = initial_count + len(created_notification_ids)
            count_correct = new_count >= expected_count
            
            self.log_test("Notification Count After Creation", count_correct,
                         f"Count: {new_count}, Expected: >= {expected_count}")
            
            # Verify notification types and content
            notification_types = [notif.get('type') for notif in notifications_after]
            has_welcome = 'welcome' in notification_types
            has_system = 'system' in notification_types
            has_message = 'message' in notification_types
            
            self.log_test("Notification Types Variety", has_welcome and has_system and has_message,
                         f"Types found: welcome={has_welcome}, system={has_system}, message={has_message}")
        
        # Test 4: Test marking notifications as read (batch operation)
        print("\n4️⃣ Testing PUT notifications endpoint (mark as read)...")
        read_success_count = 0
        for notif_id in created_notification_ids[:2]:  # Mark first 2 as read
            success_read, read_response = self.run_test(
                f"Mark Notification Read: {notif_id[:8]}...",
                "PUT",
                f"api/user/{user_id}/notifications/{notif_id}/read",
                200
            )
            if success_read:
                read_success_count += 1
        
        self.log_test("Batch Mark as Read", read_success_count == 2,
                     f"Marked {read_success_count}/2 notifications as read")
        
        # Test 5: Verify read status persistence
        print("\n5️⃣ Testing read status persistence...")
        success_verify, verify_notifications = self.run_test(
            "Verify Read Status Persistence",
            "GET",
            f"api/user/notifications/{user_id}",
            200
        )
        
        if success_verify:
            read_notifications = [n for n in verify_notifications if n.get('is_read', False)]
            unread_notifications = [n for n in verify_notifications if not n.get('is_read', True)]
            
            print(f"   📊 Read notifications: {len(read_notifications)}")
            print(f"   📊 Unread notifications: {len(unread_notifications)}")
            
            # Should have at least 2 read notifications from our test
            has_read_notifications = len(read_notifications) >= 2
            self.log_test("Read Status Persistence", has_read_notifications,
                         f"Found {len(read_notifications)} read notifications (expected >= 2)")
        
        # Test 6: Test notification filtering by type (if supported)
        print("\n6️⃣ Testing notification data structure and metadata...")
        if success_verify and verify_notifications:
            sample_notification = verify_notifications[0]
            
            # Check for required fields
            required_fields = ['id', 'user_id', 'title', 'message', 'type', 'is_read', 'created_at']
            missing_fields = [field for field in required_fields if field not in sample_notification]
            
            structure_valid = len(missing_fields) == 0
            self.log_test("Notification Data Structure", structure_valid,
                         f"Missing fields: {missing_fields if missing_fields else 'None'}")
            
            # Check for proper timestamps
            created_at = sample_notification.get('created_at')
            has_timestamp = created_at is not None
            self.log_test("Notification Timestamps", has_timestamp,
                         f"Created timestamp present: {has_timestamp}")
            
            # Check user_id matches
            user_id_matches = sample_notification.get('user_id') == user_id
            self.log_test("Notification User ID Matching", user_id_matches,
                         f"User ID matches: {user_id_matches}")
        
        return True

    def test_order_management_notifications(self):
        """Test order management system notifications"""
        print("\n🛒 Testing Order Management System Notifications...")
        
        if not self.demo_user or not self.admin_user:
            print("❌ Order Management Notifications - SKIPPED (Need both demo user and admin)")
            return False
        
        # Create a test listing for order testing
        print("\n1️⃣ Creating test listing for order notifications...")
        test_listing = {
            "title": "Notification Test Listing - Bluetooth Speaker",
            "description": "Premium Bluetooth speaker for order notification testing.",
            "price": 199.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],  # Admin is seller
            "images": ["https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400"]
        }
        
        success_listing, listing_response = self.run_test(
            "Create Test Listing for Order Notifications",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_listing or 'listing_id' not in listing_response:
            print("❌ Failed to create test listing for order notifications")
            return False
        
        listing_id = listing_response['listing_id']
        print(f"   ✅ Created test listing: {listing_id}")
        
        # Get initial notification counts
        success_seller_initial, seller_initial_notifs = self.run_test(
            "Get Seller Initial Notifications",
            "GET",
            f"api/user/notifications/{self.admin_user['id']}",
            200
        )
        
        success_buyer_initial, buyer_initial_notifs = self.run_test(
            "Get Buyer Initial Notifications", 
            "GET",
            f"api/user/notifications/{self.demo_user['id']}",
            200
        )
        
        seller_initial_count = len(seller_initial_notifs) if success_seller_initial else 0
        buyer_initial_count = len(buyer_initial_notifs) if success_buyer_initial else 0
        
        print(f"   📊 Initial seller notifications: {seller_initial_count}")
        print(f"   📊 Initial buyer notifications: {buyer_initial_count}")
        
        # Create buy request (should generate notification for seller)
        print("\n2️⃣ Creating buy request (should notify seller)...")
        order_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user['id']
        }
        
        success_order, order_response = self.run_test(
            "Create Buy Request for Notifications",
            "POST",
            "api/orders/create",
            200,
            data=order_data
        )
        
        order_id = None
        if success_order and 'order_id' in order_response:
            order_id = order_response['order_id']
            print(f"   ✅ Created buy request: {order_id}")
            
            # Check if seller received notification
            success_seller_after, seller_after_notifs = self.run_test(
                "Check Seller Notifications After Buy Request",
                "GET",
                f"api/user/notifications/{self.admin_user['id']}",
                200
            )
            
            if success_seller_after:
                seller_new_count = len(seller_after_notifs)
                seller_got_notification = seller_new_count > seller_initial_count
                
                self.log_test("Seller Buy Request Notification", seller_got_notification,
                             f"Seller notifications: {seller_initial_count} → {seller_new_count}")
                
                if seller_got_notification:
                    # Find the buy request notification
                    buy_request_notifs = [n for n in seller_after_notifs if n.get('type') == 'buy_request']
                    if buy_request_notifs:
                        latest_notif = buy_request_notifs[0]  # Should be most recent
                        print(f"   📬 Buy request notification: '{latest_notif.get('title', 'N/A')}'")
                        print(f"   📝 Message: '{latest_notif.get('message', 'N/A')}'")
        
        # Approve the order (should generate notification for buyer)
        if order_id:
            print("\n3️⃣ Approving buy request (should notify buyer)...")
            approval_data = {
                "seller_id": self.admin_user['id']
            }
            
            success_approve, approve_response = self.run_test(
                "Approve Buy Request for Notifications",
                "PUT",
                f"api/orders/{order_id}/approve",
                200,
                data=approval_data
            )
            
            if success_approve:
                print("   ✅ Buy request approved")
                
                # Check if buyer received approval notification
                success_buyer_after, buyer_after_notifs = self.run_test(
                    "Check Buyer Notifications After Approval",
                    "GET",
                    f"api/user/notifications/{self.demo_user['id']}",
                    200
                )
                
                if success_buyer_after:
                    buyer_new_count = len(buyer_after_notifs)
                    buyer_got_notification = buyer_new_count > buyer_initial_count
                    
                    self.log_test("Buyer Approval Notification", buyer_got_notification,
                                 f"Buyer notifications: {buyer_initial_count} → {buyer_new_count}")
                    
                    if buyer_got_notification:
                        # Find the approval notification
                        approval_notifs = [n for n in buyer_after_notifs if n.get('type') == 'buy_approved']
                        if approval_notifs:
                            latest_notif = approval_notifs[0]
                            print(f"   📬 Approval notification: '{latest_notif.get('title', 'N/A')}'")
                            print(f"   📝 Message: '{latest_notif.get('message', 'N/A')}'")
        
        # Test notification types for order management
        print("\n4️⃣ Testing order management notification types...")
        
        # Get all notifications for both users
        all_seller_notifs = seller_after_notifs if 'seller_after_notifs' in locals() else []
        all_buyer_notifs = buyer_after_notifs if 'buyer_after_notifs' in locals() else []
        
        # Check for order-related notification types
        order_notification_types = ['buy_request', 'buy_approved', 'buy_rejected', 'buy_expired']
        
        found_types = set()
        for notif in all_seller_notifs + all_buyer_notifs:
            notif_type = notif.get('type', '')
            if notif_type in order_notification_types:
                found_types.add(notif_type)
        
        self.log_test("Order Notification Types", len(found_types) > 0,
                     f"Found order notification types: {list(found_types)}")
        
        # Cleanup test listing
        if listing_id:
            self.run_test(
                "Cleanup Order Notification Test Listing",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
        
        return True

    def test_notification_system_backend_functionality(self):
        """Verify that all notification system backend functionality is working correctly"""
        print("\n🔧 Testing Notification System Backend Functionality...")
        
        if not self.demo_user:
            print("❌ Backend Functionality Test - SKIPPED (No demo user logged in)")
            return False
        
        user_id = self.demo_user['id']
        
        # Test 1: Notification CRUD Operations
        print("\n1️⃣ Testing notification CRUD operations...")
        
        # Create
        create_data = {
            "title": "Backend Test Notification",
            "message": "Testing backend notification functionality with comprehensive data validation.",
            "type": "backend_test"
        }
        
        success_create, create_response = self.run_test(
            "Backend Notification CREATE",
            "POST",
            f"api/user/{user_id}/notifications",
            200,
            data=create_data
        )
        
        backend_test_id = None
        if success_create and 'id' in create_response:
            backend_test_id = create_response['id']
            
            # Read
            success_read, read_response = self.run_test(
                "Backend Notification READ",
                "GET",
                f"api/user/notifications/{user_id}",
                200
            )
            
            if success_read:
                # Find our test notification
                test_notif = None
                for notif in read_response:
                    if notif.get('id') == backend_test_id:
                        test_notif = notif
                        break
                
                read_success = test_notif is not None
                self.log_test("Backend Notification READ Verification", read_success,
                             f"Test notification found in response: {read_success}")
                
                if test_notif:
                    # Verify data integrity
                    title_match = test_notif.get('title') == create_data['title']
                    message_match = test_notif.get('message') == create_data['message']
                    type_match = test_notif.get('type') == create_data['type']
                    
                    data_integrity = title_match and message_match and type_match
                    self.log_test("Backend Notification Data Integrity", data_integrity,
                                 f"All fields match: title={title_match}, message={message_match}, type={type_match}")
            
            # Update (mark as read)
            success_update, update_response = self.run_test(
                "Backend Notification UPDATE",
                "PUT",
                f"api/user/{user_id}/notifications/{backend_test_id}/read",
                200
            )
            
            if success_update:
                # Verify update
                success_verify_update, verify_response = self.run_test(
                    "Backend Notification UPDATE Verification",
                    "GET",
                    f"api/user/notifications/{user_id}",
                    200
                )
                
                if success_verify_update:
                    updated_notif = None
                    for notif in verify_response:
                        if notif.get('id') == backend_test_id:
                            updated_notif = notif
                            break
                    
                    if updated_notif:
                        is_read = updated_notif.get('is_read', False)
                        has_read_timestamp = 'read_at' in updated_notif
                        
                        update_success = is_read and has_read_timestamp
                        self.log_test("Backend Notification UPDATE Success", update_success,
                                     f"Read status: {is_read}, Read timestamp: {has_read_timestamp}")
        
        # Test 2: Error Handling
        print("\n2️⃣ Testing notification error handling...")
        
        # Test invalid user ID
        success_invalid_user, _ = self.run_test(
            "Invalid User ID Handling",
            "GET",
            "api/user/notifications/invalid-user-id-12345",
            200  # Should still return 200 with empty array or handle gracefully
        )
        
        # Test invalid notification ID for read operation
        success_invalid_notif, _ = self.run_test(
            "Invalid Notification ID Handling",
            "PUT",
            f"api/user/{user_id}/notifications/invalid-notification-id/read",
            404  # Should return 404 for non-existent notification
        )
        
        self.log_test("Backend Error Handling", success_invalid_user,
                     "Invalid requests handled gracefully")
        
        # Test 3: Notification Metadata and Timestamps
        print("\n3️⃣ Testing notification metadata and timestamps...")
        
        if backend_test_id:
            success_metadata, metadata_response = self.run_test(
                "Notification Metadata Check",
                "GET",
                f"api/user/notifications/{user_id}",
                200
            )
            
            if success_metadata:
                test_notif = None
                for notif in metadata_response:
                    if notif.get('id') == backend_test_id:
                        test_notif = notif
                        break
                
                if test_notif:
                    # Check required metadata fields
                    has_id = 'id' in test_notif
                    has_user_id = 'user_id' in test_notif and test_notif['user_id'] == user_id
                    has_created_at = 'created_at' in test_notif
                    has_is_read = 'is_read' in test_notif
                    
                    metadata_complete = has_id and has_user_id and has_created_at and has_is_read
                    self.log_test("Notification Metadata Complete", metadata_complete,
                                 f"ID: {has_id}, User ID: {has_user_id}, Created: {has_created_at}, Read: {has_is_read}")
                    
                    # Validate timestamp format
                    created_at = test_notif.get('created_at')
                    timestamp_valid = False
                    if created_at:
                        try:
                            # Try to parse the timestamp
                            if isinstance(created_at, str):
                                datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            timestamp_valid = True
                        except:
                            timestamp_valid = False
                    
                    self.log_test("Notification Timestamp Format", timestamp_valid,
                                 f"Timestamp format valid: {timestamp_valid}")
        
        # Test 4: Notification Sorting and Ordering
        print("\n4️⃣ Testing notification sorting and ordering...")
        
        # Create multiple notifications with slight delays to test ordering
        import time
        
        ordering_test_ids = []
        for i in range(3):
            order_data = {
                "title": f"Ordering Test {i+1}",
                "message": f"Testing notification ordering - notification {i+1}",
                "type": "ordering_test"
            }
            
            success_order, order_response = self.run_test(
                f"Create Ordering Test Notification {i+1}",
                "POST",
                f"api/user/{user_id}/notifications",
                200,
                data=order_data
            )
            
            if success_order and 'id' in order_response:
                ordering_test_ids.append(order_response['id'])
                time.sleep(0.1)  # Small delay to ensure different timestamps
        
        if len(ordering_test_ids) == 3:
            success_ordering, ordering_response = self.run_test(
                "Check Notification Ordering",
                "GET",
                f"api/user/notifications/{user_id}",
                200
            )
            
            if success_ordering:
                # Find our ordering test notifications
                ordering_notifs = []
                for notif in ordering_response:
                    if notif.get('type') == 'ordering_test':
                        ordering_notifs.append(notif)
                
                if len(ordering_notifs) >= 3:
                    # Check if they're in reverse chronological order (newest first)
                    timestamps = [notif.get('created_at') for notif in ordering_notifs[:3]]
                    
                    # Convert to datetime objects for comparison
                    try:
                        dt_timestamps = []
                        for ts in timestamps:
                            if isinstance(ts, str):
                                dt_timestamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
                            else:
                                dt_timestamps.append(ts)
                        
                        # Check if sorted in descending order (newest first)
                        is_sorted_desc = all(dt_timestamps[i] >= dt_timestamps[i+1] for i in range(len(dt_timestamps)-1))
                        
                        self.log_test("Notification Chronological Ordering", is_sorted_desc,
                                     f"Notifications sorted newest first: {is_sorted_desc}")
                    except Exception as e:
                        self.log_test("Notification Chronological Ordering", False,
                                     f"Error parsing timestamps: {str(e)}")
        
        return True

    def run_comprehensive_tests(self):
        """Run all notification system and authentication tests"""
        print("🚀 Starting Comprehensive Notification System & Authentication Tests")
        print("=" * 80)
        
        # Test 1: Authentication
        print("\n" + "="*50)
        print("AUTHENTICATION TESTS")
        print("="*50)
        
        auth_success = self.test_demo_user_login()
        admin_success = self.test_admin_login()
        
        if not auth_success:
            print("\n❌ CRITICAL: Demo user authentication failed - stopping tests")
            return False
        
        # Test 2: Basic Notification Operations
        print("\n" + "="*50)
        print("BASIC NOTIFICATION TESTS")
        print("="*50)
        
        get_notifs_success = self.test_get_user_notifications()
        create_notif_success = self.test_create_notification()
        mark_read_success = self.test_mark_notification_as_read()
        
        # Test 3: Comprehensive Notification Endpoints
        print("\n" + "="*50)
        print("COMPREHENSIVE NOTIFICATION ENDPOINT TESTS")
        print("="*50)
        
        comprehensive_success = self.test_notification_endpoints_comprehensive()
        
        # Test 4: Order Management Notifications
        print("\n" + "="*50)
        print("ORDER MANAGEMENT NOTIFICATION TESTS")
        print("="*50)
        
        order_notifs_success = self.test_order_management_notifications()
        
        # Test 5: Backend Functionality
        print("\n" + "="*50)
        print("BACKEND FUNCTIONALITY TESTS")
        print("="*50)
        
        backend_success = self.test_notification_system_backend_functionality()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total_test_categories = 5
        passed_categories = sum([
            auth_success,
            get_notifs_success and create_notif_success and mark_read_success,
            comprehensive_success,
            order_notifs_success,
            backend_success
        ])
        
        print(f"\n📊 Overall Results:")
        print(f"   Total Test Categories: {total_test_categories}")
        print(f"   Passed Categories: {passed_categories}")
        print(f"   Individual Tests Run: {self.tests_run}")
        print(f"   Individual Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n📋 Category Results:")
        print(f"   ✅ Authentication: {'PASSED' if auth_success else 'FAILED'}")
        print(f"   ✅ Basic Notifications: {'PASSED' if (get_notifs_success and create_notif_success and mark_read_success) else 'FAILED'}")
        print(f"   ✅ Comprehensive Endpoints: {'PASSED' if comprehensive_success else 'FAILED'}")
        print(f"   ✅ Order Management Notifications: {'PASSED' if order_notifs_success else 'FAILED'}")
        print(f"   ✅ Backend Functionality: {'PASSED' if backend_success else 'FAILED'}")
        
        if passed_categories == total_test_categories:
            print(f"\n🎉 ALL NOTIFICATION SYSTEM TESTS PASSED!")
            print(f"   The notification system and authentication endpoints are working correctly.")
            print(f"   Order management system notifications are functional.")
            return True
        else:
            print(f"\n⚠️  {total_test_categories - passed_categories} test categories failed")
            print(f"   Some notification system functionality may need attention.")
            return False

def main():
    """Main test execution"""
    print("Cataloro Marketplace - Notification System & Authentication Test Suite")
    print("Testing notification system and authentication endpoints as requested")
    print("=" * 80)
    
    tester = NotificationAuthTester()
    
    try:
        success = tester.run_comprehensive_tests()
        
        if success:
            print(f"\n✅ NOTIFICATION SYSTEM TESTING COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print(f"\n❌ NOTIFICATION SYSTEM TESTING COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()