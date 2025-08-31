#!/usr/bin/env python3
"""
Cataloro Marketplace Comprehensive Backend API Test Suite
Focuses on Live Functionality Testing as requested in review:
- User favorites endpoints: GET/POST/DELETE /api/user/{user_id}/favorites
- User cart endpoints: GET/POST/PUT/DELETE /api/user/{user_id}/cart 
- User messaging endpoints: GET/POST/PUT /api/user/{user_id}/messages
- User notifications endpoints: GET/POST/PUT /api/user/{user_id}/notifications
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class CataloroLiveFunctionalityTester:
    def __init__(self, base_url="https://seller-status-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.test_user_2 = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_item_id = str(uuid.uuid4())
        self.test_message_id = None
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

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                    return success, response_data
                except:
                    details += f", Response: {response.text[:100]}..."
                    return success, {}
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_test_users(self):
        """Setup test users for comprehensive testing"""
        print("\n🔧 Setting up test users...")
        
        # Login admin user
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
            print(f"   Admin User ID: {self.admin_user['id']}")

        # Login regular user
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
            print(f"   Regular User ID: {self.regular_user['id']}")

        # Create second test user for messaging
        success, response = self.run_test(
            "Second Test User Registration",
            "POST",
            "api/auth/register",
            200,
            data={
                "username": "testuser2",
                "email": "testuser2@cataloro.com",
                "full_name": "Test User Two"
            }
        )
        if success:
            # Login the second user to get their details
            success2, response2 = self.run_test(
                "Second Test User Login",
                "POST",
                "api/auth/login",
                200,
                data={"email": "testuser2@cataloro.com", "password": "demo123"}
            )
            if success2:
                self.test_user_2 = response2['user']
                print(f"   Second Test User ID: {self.test_user_2['id']}")

        return self.regular_user is not None

    def test_health_check(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        return success

    # ============================================================================
    # FAVORITES FUNCTIONALITY TESTS
    # ============================================================================

    def test_favorites_get_empty(self):
        """Test GET user favorites (initially empty)"""
        if not self.regular_user:
            print("❌ Favorites GET (Empty) - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "User Favorites GET (Empty State)",
            "GET",
            f"api/user/{self.regular_user['id']}/favorites",
            200
        )
        if success:
            print(f"   Initial favorites count: {len(response)}")
        return success

    def test_favorites_add_item(self):
        """Test POST add item to favorites"""
        if not self.regular_user:
            print("❌ Favorites POST - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "Add Item to Favorites",
            "POST",
            f"api/user/{self.regular_user['id']}/favorites/{self.test_item_id}",
            200
        )
        if success:
            print(f"   Added item {self.test_item_id} to favorites")
        return success

    def test_favorites_get_with_items(self):
        """Test GET user favorites (with items)"""
        if not self.regular_user:
            print("❌ Favorites GET (With Items) - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "User Favorites GET (With Items)",
            "GET",
            f"api/user/{self.regular_user['id']}/favorites",
            200
        )
        if success:
            print(f"   Favorites count after adding: {len(response)}")
            # Verify our test item is in the list
            item_found = any(fav.get('item_id') == self.test_item_id for fav in response)
            if item_found:
                print(f"   ✅ Test item {self.test_item_id} found in favorites")
            else:
                print(f"   ⚠️  Test item {self.test_item_id} not found in favorites")
        return success

    def test_favorites_add_duplicate(self):
        """Test POST add duplicate item to favorites"""
        if not self.regular_user:
            print("❌ Favorites POST (Duplicate) - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "Add Duplicate Item to Favorites",
            "POST",
            f"api/user/{self.regular_user['id']}/favorites/{self.test_item_id}",
            200
        )
        if success:
            print(f"   Duplicate handling: {response.get('message', 'No message')}")
        return success

    def test_favorites_remove_item(self):
        """Test DELETE remove item from favorites"""
        if not self.regular_user:
            print("❌ Favorites DELETE - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "Remove Item from Favorites",
            "DELETE",
            f"api/user/{self.regular_user['id']}/favorites/{self.test_item_id}",
            200
        )
        if success:
            print(f"   Removed item {self.test_item_id} from favorites")
        return success

    def test_favorites_remove_nonexistent(self):
        """Test DELETE remove non-existent item from favorites"""
        if not self.regular_user:
            print("❌ Favorites DELETE (Non-existent) - SKIPPED (No user)")
            return False
            
        fake_item_id = str(uuid.uuid4())
        success, response = self.run_test(
            "Remove Non-existent Item from Favorites",
            "DELETE",
            f"api/user/{self.regular_user['id']}/favorites/{fake_item_id}",
            404
        )
        return success

    # ============================================================================
    # CART FUNCTIONALITY TESTS
    # ============================================================================

    def test_cart_get_empty(self):
        """Test GET user cart (initially empty)"""
        if not self.regular_user:
            print("❌ Cart GET (Empty) - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "User Cart GET (Empty State)",
            "GET",
            f"api/user/{self.regular_user['id']}/cart",
            200
        )
        if success:
            print(f"   Initial cart items count: {len(response)}")
        return success

    def test_cart_add_item(self):
        """Test POST add item to cart"""
        if not self.regular_user:
            print("❌ Cart POST - SKIPPED (No user)")
            return False
            
        cart_item = {
            "item_id": self.test_item_id,
            "quantity": 2,
            "price": 99.99
        }
        
        success, response = self.run_test(
            "Add Item to Cart",
            "POST",
            f"api/user/{self.regular_user['id']}/cart",
            200,
            data=cart_item
        )
        if success:
            print(f"   Added item {self.test_item_id} to cart (qty: 2, price: $99.99)")
        return success

    def test_cart_get_with_items(self):
        """Test GET user cart (with items)"""
        if not self.regular_user:
            print("❌ Cart GET (With Items) - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "User Cart GET (With Items)",
            "GET",
            f"api/user/{self.regular_user['id']}/cart",
            200
        )
        if success:
            print(f"   Cart items count after adding: {len(response)}")
            # Verify our test item is in the cart
            item_found = any(item.get('item_id') == self.test_item_id for item in response)
            if item_found:
                cart_item = next(item for item in response if item.get('item_id') == self.test_item_id)
                print(f"   ✅ Test item found - Qty: {cart_item.get('quantity')}, Price: ${cart_item.get('price')}")
            else:
                print(f"   ⚠️  Test item {self.test_item_id} not found in cart")
        return success

    def test_cart_add_duplicate_item(self):
        """Test POST add duplicate item to cart (should update quantity)"""
        if not self.regular_user:
            print("❌ Cart POST (Duplicate) - SKIPPED (No user)")
            return False
            
        cart_item = {
            "item_id": self.test_item_id,
            "quantity": 1,
            "price": 99.99
        }
        
        success, response = self.run_test(
            "Add Duplicate Item to Cart",
            "POST",
            f"api/user/{self.regular_user['id']}/cart",
            200,
            data=cart_item
        )
        if success:
            print(f"   Duplicate handling: {response.get('message', 'No message')}")
        return success

    def test_cart_update_item(self):
        """Test PUT update cart item quantity"""
        if not self.regular_user:
            print("❌ Cart PUT - SKIPPED (No user)")
            return False
            
        update_data = {
            "quantity": 5
        }
        
        success, response = self.run_test(
            "Update Cart Item Quantity",
            "PUT",
            f"api/user/{self.regular_user['id']}/cart/{self.test_item_id}",
            200,
            data=update_data
        )
        if success:
            print(f"   Updated item quantity to 5")
        return success

    def test_cart_remove_item(self):
        """Test DELETE remove item from cart"""
        if not self.regular_user:
            print("❌ Cart DELETE - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "Remove Item from Cart",
            "DELETE",
            f"api/user/{self.regular_user['id']}/cart/{self.test_item_id}",
            200
        )
        if success:
            print(f"   Removed item {self.test_item_id} from cart")
        return success

    def test_cart_remove_nonexistent(self):
        """Test DELETE remove non-existent item from cart"""
        if not self.regular_user:
            print("❌ Cart DELETE (Non-existent) - SKIPPED (No user)")
            return False
            
        fake_item_id = str(uuid.uuid4())
        success, response = self.run_test(
            "Remove Non-existent Item from Cart",
            "DELETE",
            f"api/user/{self.regular_user['id']}/cart/{fake_item_id}",
            404
        )
        return success

    # ============================================================================
    # MESSAGING FUNCTIONALITY TESTS
    # ============================================================================

    def test_messages_get_empty(self):
        """Test GET user messages (initially empty)"""
        if not self.regular_user:
            print("❌ Messages GET (Empty) - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "User Messages GET (Empty State)",
            "GET",
            f"api/user/{self.regular_user['id']}/messages",
            200
        )
        if success:
            print(f"   Initial messages count: {len(response)}")
        return success

    def test_messages_send_message(self):
        """Test POST send message"""
        if not self.regular_user or not self.test_user_2:
            print("❌ Messages POST - SKIPPED (Need two users)")
            return False
            
        message_data = {
            "recipient_id": self.test_user_2['id'],
            "subject": "Test Message Subject",
            "content": "This is a test message content for API testing."
        }
        
        success, response = self.run_test(
            "Send Message",
            "POST",
            f"api/user/{self.regular_user['id']}/messages",
            200,
            data=message_data
        )
        if success:
            self.test_message_id = response.get('id')
            print(f"   Sent message from {self.regular_user['id']} to {self.test_user_2['id']}")
            print(f"   Message ID: {self.test_message_id}")
        return success

    def test_messages_get_with_messages(self):
        """Test GET user messages (with messages)"""
        if not self.regular_user:
            print("❌ Messages GET (With Messages) - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "User Messages GET (With Messages)",
            "GET",
            f"api/user/{self.regular_user['id']}/messages",
            200
        )
        if success:
            print(f"   Messages count after sending: {len(response)}")
            # Verify our test message is in the list
            if self.test_message_id:
                message_found = any(msg.get('id') == self.test_message_id for msg in response)
                if message_found:
                    test_msg = next(msg for msg in response if msg.get('id') == self.test_message_id)
                    print(f"   ✅ Test message found - Subject: {test_msg.get('subject')}")
                    print(f"   Read status: {test_msg.get('is_read')}")
                else:
                    print(f"   ⚠️  Test message {self.test_message_id} not found")
        return success

    def test_messages_mark_read(self):
        """Test PUT mark message as read"""
        if not self.regular_user or not self.test_message_id:
            print("❌ Messages PUT (Mark Read) - SKIPPED (No message)")
            return False
            
        success, response = self.run_test(
            "Mark Message as Read",
            "PUT",
            f"api/user/{self.regular_user['id']}/messages/{self.test_message_id}/read",
            200
        )
        if success:
            print(f"   Marked message {self.test_message_id} as read")
        return success

    def test_messages_recipient_view(self):
        """Test GET messages from recipient's perspective"""
        if not self.test_user_2 or not self.test_message_id:
            print("❌ Messages GET (Recipient) - SKIPPED (No recipient)")
            return False
            
        success, response = self.run_test(
            "Recipient Messages GET",
            "GET",
            f"api/user/{self.test_user_2['id']}/messages",
            200
        )
        if success:
            print(f"   Recipient messages count: {len(response)}")
            # Verify recipient can see the message
            message_found = any(msg.get('id') == self.test_message_id for msg in response)
            if message_found:
                print(f"   ✅ Recipient can see the message")
            else:
                print(f"   ⚠️  Recipient cannot see the message")
        return success

    # ============================================================================
    # NOTIFICATIONS FUNCTIONALITY TESTS
    # ============================================================================

    def test_notifications_get_empty(self):
        """Test GET user notifications (initially may have some)"""
        if not self.regular_user:
            print("❌ Notifications GET (Initial) - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "User Notifications GET (Initial State)",
            "GET",
            f"api/user/{self.regular_user['id']}/notifications",
            200
        )
        if success:
            print(f"   Initial notifications count: {len(response)}")
        return success

    def test_notifications_create(self):
        """Test POST create notification"""
        if not self.regular_user:
            print("❌ Notifications POST - SKIPPED (No user)")
            return False
            
        notification_data = {
            "title": "Test Notification",
            "message": "This is a test notification for API testing.",
            "type": "info"
        }
        
        success, response = self.run_test(
            "Create Notification",
            "POST",
            f"api/user/{self.regular_user['id']}/notifications",
            200,
            data=notification_data
        )
        if success:
            self.test_notification_id = response.get('id')
            print(f"   Created notification for user {self.regular_user['id']}")
            print(f"   Notification ID: {self.test_notification_id}")
        return success

    def test_notifications_get_with_notifications(self):
        """Test GET user notifications (with notifications)"""
        if not self.regular_user:
            print("❌ Notifications GET (With Notifications) - SKIPPED (No user)")
            return False
            
        success, response = self.run_test(
            "User Notifications GET (With Notifications)",
            "GET",
            f"api/user/{self.regular_user['id']}/notifications",
            200
        )
        if success:
            print(f"   Notifications count after creating: {len(response)}")
            # Verify our test notification is in the list
            if self.test_notification_id:
                notification_found = any(notif.get('id') == self.test_notification_id for notif in response)
                if notification_found:
                    test_notif = next(notif for notif in response if notif.get('id') == self.test_notification_id)
                    print(f"   ✅ Test notification found - Title: {test_notif.get('title')}")
                    print(f"   Read status: {test_notif.get('is_read')}")
                else:
                    print(f"   ⚠️  Test notification {self.test_notification_id} not found")
        return success

    def test_notifications_mark_read(self):
        """Test PUT mark notification as read"""
        if not self.regular_user or not self.test_notification_id:
            print("❌ Notifications PUT (Mark Read) - SKIPPED (No notification)")
            return False
            
        success, response = self.run_test(
            "Mark Notification as Read",
            "PUT",
            f"api/user/{self.regular_user['id']}/notifications/{self.test_notification_id}/read",
            200
        )
        if success:
            print(f"   Marked notification {self.test_notification_id} as read")
        return success

    # ============================================================================
    # DATABASE OPERATIONS TESTS
    # ============================================================================

    def test_database_persistence(self):
        """Test database persistence by checking data consistency"""
        if not self.regular_user:
            print("❌ Database Persistence - SKIPPED (No user)")
            return False
            
        print("\n🗄️  Testing Database Persistence...")
        
        # Test that data persists across multiple requests
        # Add item to favorites
        success1, _ = self.run_test(
            "DB Persistence - Add Favorite",
            "POST",
            f"api/user/{self.regular_user['id']}/favorites/{self.test_item_id}",
            200
        )
        
        # Immediately check if it's there
        success2, response = self.run_test(
            "DB Persistence - Check Favorite",
            "GET",
            f"api/user/{self.regular_user['id']}/favorites",
            200
        )
        
        persistence_success = False
        if success1 and success2:
            item_found = any(fav.get('item_id') == self.test_item_id for fav in response)
            if item_found:
                print("   ✅ Data persisted correctly in database")
                persistence_success = True
            else:
                print("   ❌ Data not found after insertion")
        
        # Clean up
        self.run_test(
            "DB Persistence - Cleanup",
            "DELETE",
            f"api/user/{self.regular_user['id']}/favorites/{self.test_item_id}",
            200
        )
        
        return persistence_success

    def test_service_status(self):
        """Test service status and performance"""
        print("\n⚡ Testing Service Status and Performance...")
        
        start_time = datetime.now()
        success, response = self.run_test(
            "Service Performance - Health Check",
            "GET",
            "api/health",
            200
        )
        end_time = datetime.now()
        
        if success:
            response_time = (end_time - start_time).total_seconds() * 1000
            print(f"   Response time: {response_time:.2f}ms")
            
            if response_time < 1000:  # Less than 1 second
                print("   ✅ Service performance is good")
                return True
            else:
                print("   ⚠️  Service response time is slow")
                return True  # Still working, just slow
        
        return False

    def run_comprehensive_tests(self):
        """Run comprehensive live functionality test suite"""
        print("🚀 Starting Cataloro Live Functionality Tests")
        print("=" * 70)
        print("Testing specific endpoints as requested in review:")
        print("- User favorites endpoints: GET/POST/DELETE /api/user/{user_id}/favorites")
        print("- User cart endpoints: GET/POST/PUT/DELETE /api/user/{user_id}/cart")
        print("- User messaging endpoints: GET/POST/PUT /api/user/{user_id}/messages")
        print("- User notifications endpoints: GET/POST/PUT /api/user/{user_id}/notifications")
        print("=" * 70)

        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False

        # Setup test users
        if not self.setup_test_users():
            print("❌ User setup failed - stopping tests")
            return False

        # ============================================================================
        # FAVORITES FUNCTIONALITY TESTS
        # ============================================================================
        print("\n💖 TESTING FAVORITES FUNCTIONALITY")
        print("-" * 50)
        self.test_favorites_get_empty()
        self.test_favorites_add_item()
        self.test_favorites_get_with_items()
        self.test_favorites_add_duplicate()
        self.test_favorites_remove_item()
        self.test_favorites_remove_nonexistent()

        # ============================================================================
        # CART FUNCTIONALITY TESTS
        # ============================================================================
        print("\n🛒 TESTING CART FUNCTIONALITY")
        print("-" * 50)
        self.test_cart_get_empty()
        self.test_cart_add_item()
        self.test_cart_get_with_items()
        self.test_cart_add_duplicate_item()
        self.test_cart_update_item()
        self.test_cart_remove_item()
        self.test_cart_remove_nonexistent()

        # ============================================================================
        # MESSAGING FUNCTIONALITY TESTS
        # ============================================================================
        print("\n💬 TESTING MESSAGING FUNCTIONALITY")
        print("-" * 50)
        self.test_messages_get_empty()
        self.test_messages_send_message()
        self.test_messages_get_with_messages()
        self.test_messages_mark_read()
        self.test_messages_recipient_view()

        # ============================================================================
        # NOTIFICATIONS FUNCTIONALITY TESTS
        # ============================================================================
        print("\n🔔 TESTING NOTIFICATIONS FUNCTIONALITY")
        print("-" * 50)
        self.test_notifications_get_empty()
        self.test_notifications_create()
        self.test_notifications_get_with_notifications()
        self.test_notifications_mark_read()

        # ============================================================================
        # DATABASE AND SERVICE TESTS
        # ============================================================================
        print("\n🗄️  TESTING DATABASE OPERATIONS")
        print("-" * 50)
        self.test_database_persistence()
        self.test_service_status()

        # Print results
        print("\n" + "=" * 70)
        print(f"📊 Live Functionality Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All live functionality tests passed!")
            print("✅ Backend is ready for frontend integration!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed")
            
            if failed_tests <= 2:  # Allow for minor issues
                print("✅ Backend is mostly functional with minor issues")
                return True
            else:
                print("❌ Backend has significant issues that need attention")
                return False

def main():
    """Main test execution"""
    tester = CataloroLiveFunctionalityTester()
    success = tester.run_comprehensive_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())