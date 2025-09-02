#!/usr/bin/env python3
"""
Enhanced Functionality Test Suite for Cataloro Marketplace
Tests the enhanced favorites, messaging, notifications, and cart APIs
Focus on integration and real-time functionality
"""

import requests
import sys
import json
import time
from datetime import datetime

class EnhancedFunctionalityTester:
    def __init__(self, base_url="https://catalog-admin-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_user = None
        self.regular_user = None
        self.test_listing_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request and return success status and response"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                response = self.session.post(url, json=data)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json() if response.text else {}
            except:
                response_data = {}
                
            return success, response_data, response.status_code
            
        except Exception as e:
            print(f"   Request error: {str(e)}")
            return False, {}, 0

    def setup_test_users(self):
        """Setup test users for enhanced functionality testing"""
        print("\n🔧 Setting up test users...")
        
        # Login admin user
        success, admin_data, status = self.make_request(
            'POST', 
            'api/auth/login',
            {"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success and 'user' in admin_data:
            self.admin_user = admin_data['user']
            print(f"   ✅ Admin user logged in: {self.admin_user['email']}")
        else:
            print(f"   ❌ Admin login failed: Status {status}")
            return False
            
        # Login regular user
        success, user_data, status = self.make_request(
            'POST',
            'api/auth/login', 
            {"email": "user@cataloro.com", "password": "demo123"}
        )
        
        if success and 'user' in user_data:
            self.regular_user = user_data['user']
            print(f"   ✅ Regular user logged in: {self.regular_user['email']}")
        else:
            print(f"   ❌ Regular user login failed: Status {status}")
            return False
            
        return True

    def get_test_listing_id(self):
        """Get a test listing ID for favorites and cart testing"""
        print("\n🔍 Getting test listing for enhanced functionality tests...")
        
        success, listings_data, status = self.make_request('GET', 'api/marketplace/browse')
        
        if success and listings_data and len(listings_data) > 0:
            self.test_listing_id = listings_data[0]['id']
            print(f"   ✅ Using test listing: {listings_data[0]['title']} (ID: {self.test_listing_id})")
            return True
        else:
            print(f"   ❌ No listings found for testing: Status {status}")
            return False

    def test_enhanced_favorites_api(self):
        """Test enhanced favorites API functionality"""
        print("\n💖 Testing Enhanced Favorites API...")
        
        if not self.regular_user or not self.test_listing_id:
            self.log_test("Enhanced Favorites API", False, "Missing test user or listing")
            return False
            
        user_id = self.regular_user['id']
        
        # Test 1: Get empty favorites initially
        success, favorites_data, status = self.make_request(
            'GET', 
            f'api/user/{user_id}/favorites'
        )
        
        if success:
            self.log_test("Get Favorites (Empty State)", True, f"Found {len(favorites_data)} favorites")
        else:
            self.log_test("Get Favorites (Empty State)", False, f"Status: {status}")
            return False
            
        # Test 2: Add item to favorites
        success, add_response, status = self.make_request(
            'POST',
            f'api/user/{user_id}/favorites/{self.test_listing_id}'
        )
        
        if success:
            self.log_test("Add to Favorites", True, f"Response: {add_response.get('message', 'Success')}")
        else:
            self.log_test("Add to Favorites", False, f"Status: {status}")
            return False
            
        # Test 3: Get favorites with items (enhanced data)
        success, favorites_with_items, status = self.make_request(
            'GET',
            f'api/user/{user_id}/favorites'
        )
        
        if success and len(favorites_with_items) > 0:
            favorite_item = favorites_with_items[0]
            # Check if enhanced data is present
            required_fields = ['title', 'description', 'price', 'category', 'seller_id']
            has_enhanced_data = all(field in favorite_item for field in required_fields)
            
            if has_enhanced_data:
                self.log_test("Get Favorites (Enhanced Data)", True, 
                             f"Found {len(favorites_with_items)} favorites with full listing details")
                print(f"      Enhanced data includes: {', '.join(required_fields)}")
            else:
                self.log_test("Get Favorites (Enhanced Data)", False, 
                             "Favorites missing enhanced listing details")
        else:
            self.log_test("Get Favorites (Enhanced Data)", False, f"No favorites returned: Status {status}")
            
        # Test 4: Test duplicate handling
        success, duplicate_response, status = self.make_request(
            'POST',
            f'api/user/{user_id}/favorites/{self.test_listing_id}'
        )
        
        if success:
            self.log_test("Favorites Duplicate Handling", True, 
                         f"Duplicate handled: {duplicate_response.get('message', 'Success')}")
        else:
            self.log_test("Favorites Duplicate Handling", False, f"Status: {status}")
            
        # Test 5: Remove from favorites
        success, remove_response, status = self.make_request(
            'DELETE',
            f'api/user/{user_id}/favorites/{self.test_listing_id}'
        )
        
        if success:
            self.log_test("Remove from Favorites", True, f"Response: {remove_response.get('message', 'Success')}")
        else:
            self.log_test("Remove from Favorites", False, f"Status: {status}")
            
        # Test 6: Verify removal
        success, empty_favorites, status = self.make_request(
            'GET',
            f'api/user/{user_id}/favorites'
        )
        
        if success and len(empty_favorites) == 0:
            self.log_test("Favorites Removal Verification", True, "Favorites list empty after removal")
        else:
            self.log_test("Favorites Removal Verification", False, 
                         f"Favorites not properly removed: {len(empty_favorites)} items remain")
            
        return True

    def test_enhanced_messaging_api(self):
        """Test enhanced messaging API functionality"""
        print("\n💬 Testing Enhanced Messaging API...")
        
        if not self.regular_user or not self.admin_user:
            self.log_test("Enhanced Messaging API", False, "Missing test users")
            return False
            
        user_id = self.regular_user['id']
        admin_id = self.admin_user['id']
        
        # Test 1: Get empty messages initially
        success, messages_data, status = self.make_request(
            'GET',
            f'api/user/{user_id}/messages'
        )
        
        if success:
            self.log_test("Get Messages (Initial)", True, f"Found {len(messages_data)} messages")
        else:
            self.log_test("Get Messages (Initial)", False, f"Status: {status}")
            return False
            
        # Test 2: Send message from user to admin
        message_data = {
            "recipient_id": admin_id,
            "subject": "Test Enhanced Messaging",
            "content": "This is a test message for the enhanced messaging system functionality."
        }
        
        success, send_response, status = self.make_request(
            'POST',
            f'api/user/{user_id}/messages',
            message_data
        )
        
        message_id = None
        if success and 'id' in send_response:
            message_id = send_response['id']
            self.log_test("Send Message", True, f"Message sent with ID: {message_id}")
        else:
            self.log_test("Send Message", False, f"Status: {status}")
            return False
            
        # Test 3: Get messages for sender (should include sent message)
        success, sender_messages, status = self.make_request(
            'GET',
            f'api/user/{user_id}/messages'
        )
        
        if success and len(sender_messages) > 0:
            sent_message = next((msg for msg in sender_messages if msg.get('id') == message_id), None)
            if sent_message:
                self.log_test("Get Messages (Sender)", True, "Sent message found in sender's messages")
            else:
                self.log_test("Get Messages (Sender)", False, "Sent message not found in sender's messages")
        else:
            self.log_test("Get Messages (Sender)", False, f"No messages found: Status {status}")
            
        # Test 4: Get messages for recipient (admin)
        success, recipient_messages, status = self.make_request(
            'GET',
            f'api/user/{admin_id}/messages'
        )
        
        if success and len(recipient_messages) > 0:
            received_message = next((msg for msg in recipient_messages if msg.get('id') == message_id), None)
            if received_message:
                self.log_test("Get Messages (Recipient)", True, "Message found in recipient's messages")
                
                # Test 5: Mark message as read
                if not received_message.get('is_read', True):
                    success, read_response, status = self.make_request(
                        'PUT',
                        f'api/user/{admin_id}/messages/{message_id}/read'
                    )
                    
                    if success:
                        self.log_test("Mark Message as Read", True, f"Response: {read_response.get('message', 'Success')}")
                    else:
                        self.log_test("Mark Message as Read", False, f"Status: {status}")
                else:
                    self.log_test("Mark Message as Read", True, "Message already marked as read")
            else:
                self.log_test("Get Messages (Recipient)", False, "Message not found in recipient's messages")
        else:
            self.log_test("Get Messages (Recipient)", False, f"No messages found: Status {status}")
            
        return True

    def test_enhanced_notifications_api(self):
        """Test enhanced notifications API functionality"""
        print("\n🔔 Testing Enhanced Notifications API...")
        
        if not self.regular_user:
            self.log_test("Enhanced Notifications API", False, "Missing test user")
            return False
            
        user_id = self.regular_user['id']
        
        # Test 1: Get initial notifications
        success, notifications_data, status = self.make_request(
            'GET',
            f'api/user/{user_id}/notifications'
        )
        
        if success:
            initial_count = len(notifications_data)
            self.log_test("Get Notifications (Initial)", True, f"Found {initial_count} notifications")
        else:
            self.log_test("Get Notifications (Initial)", False, f"Status: {status}")
            return False
            
        # Test 2: Create new notification
        notification_data = {
            "title": "Enhanced Notification Test",
            "message": "This is a test notification for the enhanced header notification system.",
            "type": "info"
        }
        
        success, create_response, status = self.make_request(
            'POST',
            f'api/user/{user_id}/notifications',
            notification_data
        )
        
        notification_id = None
        if success and 'id' in create_response:
            notification_id = create_response['id']
            self.log_test("Create Notification", True, f"Notification created with ID: {notification_id}")
        else:
            self.log_test("Create Notification", False, f"Status: {status}")
            return False
            
        # Test 3: Get notifications (should include new one)
        success, updated_notifications, status = self.make_request(
            'GET',
            f'api/user/{user_id}/notifications'
        )
        
        if success and len(updated_notifications) > initial_count:
            new_notification = next((notif for notif in updated_notifications if notif.get('id') == notification_id), None)
            if new_notification:
                self.log_test("Get Notifications (Updated)", True, "New notification found in list")
                
                # Test 4: Mark notification as read
                if not new_notification.get('is_read', True):
                    success, read_response, status = self.make_request(
                        'PUT',
                        f'api/user/{user_id}/notifications/{notification_id}/read'
                    )
                    
                    if success:
                        self.log_test("Mark Notification as Read", True, f"Response: {read_response.get('message', 'Success')}")
                    else:
                        self.log_test("Mark Notification as Read", False, f"Status: {status}")
                else:
                    self.log_test("Mark Notification as Read", True, "Notification already marked as read")
            else:
                self.log_test("Get Notifications (Updated)", False, "New notification not found in list")
        else:
            self.log_test("Get Notifications (Updated)", False, f"Notification count not increased: Status {status}")
            
        return True

    def test_enhanced_cart_api(self):
        """Test enhanced cart API functionality"""
        print("\n🛒 Testing Enhanced Cart API...")
        
        if not self.regular_user or not self.test_listing_id:
            self.log_test("Enhanced Cart API", False, "Missing test user or listing")
            return False
            
        user_id = self.regular_user['id']
        
        # Test 1: Get empty cart initially
        success, cart_data, status = self.make_request(
            'GET',
            f'api/user/{user_id}/cart'
        )
        
        if success:
            self.log_test("Get Cart (Empty State)", True, f"Found {len(cart_data)} cart items")
        else:
            self.log_test("Get Cart (Empty State)", False, f"Status: {status}")
            return False
            
        # Test 2: Add item to cart
        cart_item_data = {
            "item_id": self.test_listing_id,
            "quantity": 2,
            "price": 99.99
        }
        
        success, add_response, status = self.make_request(
            'POST',
            f'api/user/{user_id}/cart',
            cart_item_data
        )
        
        if success:
            self.log_test("Add to Cart", True, f"Response: {add_response.get('message', 'Success')}")
        else:
            self.log_test("Add to Cart", False, f"Status: {status}")
            return False
            
        # Test 3: Get cart with items
        success, cart_with_items, status = self.make_request(
            'GET',
            f'api/user/{user_id}/cart'
        )
        
        if success and len(cart_with_items) > 0:
            cart_item = cart_with_items[0]
            if cart_item.get('quantity') == 2 and cart_item.get('item_id') == self.test_listing_id:
                self.log_test("Get Cart (With Items)", True, f"Cart item found with correct quantity: {cart_item.get('quantity')}")
            else:
                self.log_test("Get Cart (With Items)", False, "Cart item data incorrect")
        else:
            self.log_test("Get Cart (With Items)", False, f"No cart items returned: Status {status}")
            
        # Test 4: Update cart item quantity
        update_data = {"quantity": 5}
        
        success, update_response, status = self.make_request(
            'PUT',
            f'api/user/{user_id}/cart/{self.test_listing_id}',
            update_data
        )
        
        if success:
            self.log_test("Update Cart Item", True, f"Response: {update_response.get('message', 'Success')}")
        else:
            self.log_test("Update Cart Item", False, f"Status: {status}")
            
        # Test 5: Verify quantity update
        success, updated_cart, status = self.make_request(
            'GET',
            f'api/user/{user_id}/cart'
        )
        
        if success and len(updated_cart) > 0:
            updated_item = updated_cart[0]
            if updated_item.get('quantity') == 5:
                self.log_test("Cart Quantity Update Verification", True, "Quantity updated correctly to 5")
            else:
                self.log_test("Cart Quantity Update Verification", False, 
                             f"Quantity not updated: Expected 5, Got {updated_item.get('quantity')}")
        else:
            self.log_test("Cart Quantity Update Verification", False, f"Cart verification failed: Status {status}")
            
        # Test 6: Test duplicate item handling (should update quantity)
        duplicate_item_data = {
            "item_id": self.test_listing_id,
            "quantity": 3,
            "price": 99.99
        }
        
        success, duplicate_response, status = self.make_request(
            'POST',
            f'api/user/{user_id}/cart',
            duplicate_item_data
        )
        
        if success:
            self.log_test("Cart Duplicate Handling", True, f"Duplicate handled: {duplicate_response.get('message', 'Success')}")
        else:
            self.log_test("Cart Duplicate Handling", False, f"Status: {status}")
            
        # Test 7: Remove item from cart
        success, remove_response, status = self.make_request(
            'DELETE',
            f'api/user/{user_id}/cart/{self.test_listing_id}'
        )
        
        if success:
            self.log_test("Remove from Cart", True, f"Response: {remove_response.get('message', 'Success')}")
        else:
            self.log_test("Remove from Cart", False, f"Status: {status}")
            
        # Test 8: Verify removal
        success, empty_cart, status = self.make_request(
            'GET',
            f'api/user/{user_id}/cart'
        )
        
        if success and len(empty_cart) == 0:
            self.log_test("Cart Removal Verification", True, "Cart empty after removal")
        else:
            self.log_test("Cart Removal Verification", False, 
                         f"Cart not properly emptied: {len(empty_cart)} items remain")
            
        return True

    def test_integration_functionality(self):
        """Test integration between all enhanced features"""
        print("\n🔗 Testing Integration Functionality...")
        
        if not self.regular_user or not self.test_listing_id:
            self.log_test("Integration Testing", False, "Missing test user or listing")
            return False
            
        user_id = self.regular_user['id']
        
        # Test 1: Add item to both favorites and cart
        print("   Testing cross-feature integration...")
        
        # Add to favorites
        success_fav, _, _ = self.make_request(
            'POST',
            f'api/user/{user_id}/favorites/{self.test_listing_id}'
        )
        
        # Add to cart
        cart_data = {"item_id": self.test_listing_id, "quantity": 1, "price": 50.00}
        success_cart, _, _ = self.make_request(
            'POST',
            f'api/user/{user_id}/cart',
            cart_data
        )
        
        if success_fav and success_cart:
            self.log_test("Cross-Feature Integration", True, "Item added to both favorites and cart")
        else:
            self.log_test("Cross-Feature Integration", False, "Failed to add item to both features")
            
        # Test 2: Create notification about the action
        notification_data = {
            "title": "Item Added",
            "message": f"Item {self.test_listing_id} added to favorites and cart",
            "type": "success"
        }
        
        success_notif, _, _ = self.make_request(
            'POST',
            f'api/user/{user_id}/notifications',
            notification_data
        )
        
        if success_notif:
            self.log_test("Integration Notification", True, "Notification created for cross-feature action")
        else:
            self.log_test("Integration Notification", False, "Failed to create integration notification")
            
        # Test 3: Verify all features have the data
        success_fav_check, favorites, _ = self.make_request('GET', f'api/user/{user_id}/favorites')
        success_cart_check, cart, _ = self.make_request('GET', f'api/user/{user_id}/cart')
        success_notif_check, notifications, _ = self.make_request('GET', f'api/user/{user_id}/notifications')
        
        integration_success = (
            success_fav_check and len(favorites) > 0 and
            success_cart_check and len(cart) > 0 and
            success_notif_check and len(notifications) > 0
        )
        
        if integration_success:
            self.log_test("Integration Data Verification", True, 
                         f"All features have data: {len(favorites)} favorites, {len(cart)} cart items, {len(notifications)} notifications")
        else:
            self.log_test("Integration Data Verification", False, "Not all features have expected data")
            
        # Cleanup for next tests
        self.make_request('DELETE', f'api/user/{user_id}/favorites/{self.test_listing_id}')
        self.make_request('DELETE', f'api/user/{user_id}/cart/{self.test_listing_id}')
        
        return integration_success

    def test_performance_and_stability(self):
        """Test performance and stability of enhanced endpoints"""
        print("\n⚡ Testing Performance and Stability...")
        
        if not self.regular_user:
            self.log_test("Performance Testing", False, "Missing test user")
            return False
            
        user_id = self.regular_user['id']
        
        # Test response times for key endpoints
        endpoints_to_test = [
            ('GET', f'api/user/{user_id}/favorites'),
            ('GET', f'api/user/{user_id}/cart'),
            ('GET', f'api/user/{user_id}/messages'),
            ('GET', f'api/user/{user_id}/notifications'),
            ('GET', 'api/marketplace/browse')
        ]
        
        response_times = []
        
        for method, endpoint in endpoints_to_test:
            start_time = time.time()
            success, _, status = self.make_request(method, endpoint)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times.append(response_time)
            
            if success and response_time < 1000:  # Less than 1 second
                print(f"   ✅ {endpoint}: {response_time:.0f}ms")
            else:
                print(f"   ⚠️  {endpoint}: {response_time:.0f}ms (Status: {status})")
        
        avg_response_time = sum(response_times) / len(response_times)
        
        if avg_response_time < 500:  # Average less than 500ms
            self.log_test("Performance Test", True, f"Average response time: {avg_response_time:.0f}ms")
        else:
            self.log_test("Performance Test", False, f"Average response time too high: {avg_response_time:.0f}ms")
            
        return avg_response_time < 1000  # Accept up to 1 second average

    def run_enhanced_functionality_tests(self):
        """Run all enhanced functionality tests"""
        print("🚀 Starting Enhanced Functionality Tests for Cataloro Marketplace")
        print("=" * 70)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False
            
        if not self.get_test_listing_id():
            print("❌ Failed to get test listing - stopping tests")
            return False
        
        # Run enhanced functionality tests
        print("\n🔥 Testing Enhanced Features...")
        
        self.test_enhanced_favorites_api()
        self.test_enhanced_messaging_api() 
        self.test_enhanced_notifications_api()
        self.test_enhanced_cart_api()
        self.test_integration_functionality()
        self.test_performance_and_stability()
        
        # Print results
        print("\n" + "=" * 70)
        print(f"📊 Enhanced Functionality Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All enhanced functionality tests passed!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} enhanced functionality tests failed")
            return False

def main():
    """Main test execution"""
    tester = EnhancedFunctionalityTester()
    success = tester.run_enhanced_functionality_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())