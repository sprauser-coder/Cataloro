#!/usr/bin/env python3
"""
Comprehensive Enhanced Functionality Test Suite for Cataloro Marketplace
Tests all enhanced features with correct API usage patterns
"""

import requests
import sys
import json
import time
from datetime import datetime

class ComprehensiveEnhancedTester:
    def __init__(self, base_url="https://cataloro-admin-3.preview.emergentagent.com"):
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

    def setup_test_environment(self):
        """Setup test environment with users and test data"""
        print("\n🔧 Setting up test environment...")
        
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
            
        # Get test listing
        success, listings_data, status = self.make_request('GET', 'api/marketplace/browse')
        
        if success and listings_data and len(listings_data) > 0:
            self.test_listing_id = listings_data[0]['id']
            print(f"   ✅ Using test listing: {listings_data[0]['title']} (ID: {self.test_listing_id})")
        else:
            print(f"   ❌ No listings found for testing: Status {status}")
            return False
            
        return True

    def test_favorites_api_comprehensive(self):
        """Comprehensive test of favorites API"""
        print("\n💖 Testing Favorites API (Comprehensive)...")
        
        user_id = self.regular_user['id']
        
        # Get initial favorites count
        success, initial_favorites, status = self.make_request('GET', f'api/user/{user_id}/favorites')
        if not success:
            self.log_test("Favorites API - Initial State", False, f"Status: {status}")
            return False
            
        initial_count = len(initial_favorites)
        self.log_test("Favorites API - Initial State", True, f"Found {initial_count} existing favorites")
        
        # Test adding new favorite
        success, add_response, status = self.make_request(
            'POST', f'api/user/{user_id}/favorites/{self.test_listing_id}'
        )
        
        if success:
            self.log_test("Favorites API - Add Item", True, f"Response: {add_response.get('message', 'Success')}")
        else:
            self.log_test("Favorites API - Add Item", False, f"Status: {status}")
            return False
            
        # Verify addition
        success, updated_favorites, status = self.make_request('GET', f'api/user/{user_id}/favorites')
        if success:
            new_count = len(updated_favorites)
            if new_count > initial_count or any(fav.get('id') == self.test_listing_id for fav in updated_favorites):
                self.log_test("Favorites API - Verify Addition", True, f"Favorites count: {new_count}")
                
                # Check enhanced data structure
                if updated_favorites:
                    sample_favorite = updated_favorites[0]
                    required_fields = ['title', 'description', 'price', 'category', 'seller_id']
                    has_enhanced_data = all(field in sample_favorite for field in required_fields)
                    
                    if has_enhanced_data:
                        self.log_test("Favorites API - Enhanced Data", True, "Full listing details included")
                    else:
                        self.log_test("Favorites API - Enhanced Data", False, "Missing enhanced listing details")
            else:
                self.log_test("Favorites API - Verify Addition", False, "Item not found in favorites")
        else:
            self.log_test("Favorites API - Verify Addition", False, f"Status: {status}")
            
        # Test duplicate handling
        success, duplicate_response, status = self.make_request(
            'POST', f'api/user/{user_id}/favorites/{self.test_listing_id}'
        )
        
        if success:
            self.log_test("Favorites API - Duplicate Handling", True, 
                         f"Duplicate handled: {duplicate_response.get('message', 'Success')}")
        else:
            self.log_test("Favorites API - Duplicate Handling", False, f"Status: {status}")
            
        # Test removal using correct listing ID
        success, remove_response, status = self.make_request(
            'DELETE', f'api/user/{user_id}/favorites/{self.test_listing_id}'
        )
        
        if success:
            self.log_test("Favorites API - Remove Item", True, f"Response: {remove_response.get('message', 'Success')}")
            
            # Verify removal
            success, final_favorites, status = self.make_request('GET', f'api/user/{user_id}/favorites')
            if success:
                final_count = len(final_favorites)
                item_still_exists = any(fav.get('id') == self.test_listing_id for fav in final_favorites)
                
                if not item_still_exists:
                    self.log_test("Favorites API - Verify Removal", True, f"Item removed, count: {final_count}")
                else:
                    self.log_test("Favorites API - Verify Removal", False, "Item still exists in favorites")
            else:
                self.log_test("Favorites API - Verify Removal", False, f"Status: {status}")
        else:
            self.log_test("Favorites API - Remove Item", False, f"Status: {status}")
            
        return True

    def test_cart_api_comprehensive(self):
        """Comprehensive test of cart API"""
        print("\n🛒 Testing Cart API (Comprehensive)...")
        
        user_id = self.regular_user['id']
        
        # Get initial cart
        success, initial_cart, status = self.make_request('GET', f'api/user/{user_id}/cart')
        if not success:
            self.log_test("Cart API - Initial State", False, f"Status: {status}")
            return False
            
        initial_count = len(initial_cart)
        self.log_test("Cart API - Initial State", True, f"Found {initial_count} existing cart items")
        
        # Test adding item to cart
        cart_item_data = {
            "item_id": self.test_listing_id,
            "quantity": 2,
            "price": 99.99
        }
        
        success, add_response, status = self.make_request(
            'POST', f'api/user/{user_id}/cart', cart_item_data
        )
        
        if success:
            self.log_test("Cart API - Add Item", True, f"Response: {add_response.get('message', 'Success')}")
        else:
            self.log_test("Cart API - Add Item", False, f"Status: {status}")
            return False
            
        # Verify addition and check data
        success, updated_cart, status = self.make_request('GET', f'api/user/{user_id}/cart')
        if success:
            new_count = len(updated_cart)
            added_item = next((item for item in updated_cart if item.get('item_id') == self.test_listing_id), None)
            
            if added_item:
                expected_quantity = cart_item_data['quantity']
                actual_quantity = added_item.get('quantity')
                
                if actual_quantity == expected_quantity:
                    self.log_test("Cart API - Verify Addition", True, 
                                 f"Item added with correct quantity: {actual_quantity}")
                else:
                    self.log_test("Cart API - Verify Addition", False, 
                                 f"Quantity mismatch: Expected {expected_quantity}, Got {actual_quantity}")
            else:
                self.log_test("Cart API - Verify Addition", False, "Added item not found in cart")
        else:
            self.log_test("Cart API - Verify Addition", False, f"Status: {status}")
            
        # Test quantity update
        update_data = {"quantity": 5}
        success, update_response, status = self.make_request(
            'PUT', f'api/user/{user_id}/cart/{self.test_listing_id}', update_data
        )
        
        if success:
            self.log_test("Cart API - Update Quantity", True, f"Response: {update_response.get('message', 'Success')}")
            
            # Verify update
            success, updated_cart_check, status = self.make_request('GET', f'api/user/{user_id}/cart')
            if success:
                updated_item = next((item for item in updated_cart_check if item.get('item_id') == self.test_listing_id), None)
                
                if updated_item and updated_item.get('quantity') == 5:
                    self.log_test("Cart API - Verify Update", True, "Quantity updated correctly to 5")
                else:
                    actual_qty = updated_item.get('quantity') if updated_item else 'Item not found'
                    self.log_test("Cart API - Verify Update", False, f"Update failed: {actual_qty}")
            else:
                self.log_test("Cart API - Verify Update", False, f"Status: {status}")
        else:
            self.log_test("Cart API - Update Quantity", False, f"Status: {status}")
            
        # Test duplicate item handling (should update quantity)
        duplicate_item_data = {
            "item_id": self.test_listing_id,
            "quantity": 3,
            "price": 99.99
        }
        
        success, duplicate_response, status = self.make_request(
            'POST', f'api/user/{user_id}/cart', duplicate_item_data
        )
        
        if success:
            self.log_test("Cart API - Duplicate Handling", True, 
                         f"Duplicate handled: {duplicate_response.get('message', 'Success')}")
        else:
            self.log_test("Cart API - Duplicate Handling", False, f"Status: {status}")
            
        # Test removal
        success, remove_response, status = self.make_request(
            'DELETE', f'api/user/{user_id}/cart/{self.test_listing_id}'
        )
        
        if success:
            self.log_test("Cart API - Remove Item", True, f"Response: {remove_response.get('message', 'Success')}")
            
            # Verify removal
            success, final_cart, status = self.make_request('GET', f'api/user/{user_id}/cart')
            if success:
                removed_item = next((item for item in final_cart if item.get('item_id') == self.test_listing_id), None)
                
                if not removed_item:
                    self.log_test("Cart API - Verify Removal", True, "Item successfully removed from cart")
                else:
                    self.log_test("Cart API - Verify Removal", False, "Item still exists in cart")
            else:
                self.log_test("Cart API - Verify Removal", False, f"Status: {status}")
        else:
            self.log_test("Cart API - Remove Item", False, f"Status: {status}")
            
        return True

    def test_messaging_api_comprehensive(self):
        """Comprehensive test of messaging API"""
        print("\n💬 Testing Messaging API (Comprehensive)...")
        
        user_id = self.regular_user['id']
        admin_id = self.admin_user['id']
        
        # Get initial messages
        success, initial_messages, status = self.make_request('GET', f'api/user/{user_id}/messages')
        if not success:
            self.log_test("Messaging API - Initial State", False, f"Status: {status}")
            return False
            
        initial_count = len(initial_messages)
        self.log_test("Messaging API - Initial State", True, f"Found {initial_count} existing messages")
        
        # Send message from user to admin
        message_data = {
            "recipient_id": admin_id,
            "subject": "Enhanced Messaging Test",
            "content": "This is a comprehensive test of the enhanced messaging system with full functionality verification."
        }
        
        success, send_response, status = self.make_request(
            'POST', f'api/user/{user_id}/messages', message_data
        )
        
        message_id = None
        if success and 'id' in send_response:
            message_id = send_response['id']
            self.log_test("Messaging API - Send Message", True, f"Message sent with ID: {message_id}")
        else:
            self.log_test("Messaging API - Send Message", False, f"Status: {status}")
            return False
            
        # Verify message in sender's messages
        success, sender_messages, status = self.make_request('GET', f'api/user/{user_id}/messages')
        if success:
            sent_message = next((msg for msg in sender_messages if msg.get('id') == message_id), None)
            if sent_message:
                self.log_test("Messaging API - Sender Verification", True, "Message found in sender's messages")
                
                # Check message structure
                required_fields = ['sender_id', 'recipient_id', 'subject', 'content', 'is_read', 'created_at']
                has_complete_structure = all(field in sent_message for field in required_fields)
                
                if has_complete_structure:
                    self.log_test("Messaging API - Message Structure", True, "Complete message structure verified")
                else:
                    missing_fields = [field for field in required_fields if field not in sent_message]
                    self.log_test("Messaging API - Message Structure", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Messaging API - Sender Verification", False, "Message not found in sender's messages")
        else:
            self.log_test("Messaging API - Sender Verification", False, f"Status: {status}")
            
        # Verify message in recipient's messages
        success, recipient_messages, status = self.make_request('GET', f'api/user/{admin_id}/messages')
        if success:
            received_message = next((msg for msg in recipient_messages if msg.get('id') == message_id), None)
            if received_message:
                self.log_test("Messaging API - Recipient Verification", True, "Message found in recipient's messages")
                
                # Test mark as read functionality
                if not received_message.get('is_read', True):
                    success, read_response, status = self.make_request(
                        'PUT', f'api/user/{admin_id}/messages/{message_id}/read'
                    )
                    
                    if success:
                        self.log_test("Messaging API - Mark as Read", True, 
                                     f"Response: {read_response.get('message', 'Success')}")
                        
                        # Verify read status update
                        success, verify_read, status = self.make_request('GET', f'api/user/{admin_id}/messages')
                        if success:
                            updated_message = next((msg for msg in verify_read if msg.get('id') == message_id), None)
                            if updated_message and updated_message.get('is_read'):
                                self.log_test("Messaging API - Read Status Verification", True, "Message marked as read")
                            else:
                                self.log_test("Messaging API - Read Status Verification", False, "Read status not updated")
                    else:
                        self.log_test("Messaging API - Mark as Read", False, f"Status: {status}")
                else:
                    self.log_test("Messaging API - Mark as Read", True, "Message already marked as read")
            else:
                self.log_test("Messaging API - Recipient Verification", False, "Message not found in recipient's messages")
        else:
            self.log_test("Messaging API - Recipient Verification", False, f"Status: {status}")
            
        return True

    def test_notifications_api_comprehensive(self):
        """Comprehensive test of notifications API"""
        print("\n🔔 Testing Notifications API (Comprehensive)...")
        
        user_id = self.regular_user['id']
        
        # Get initial notifications
        success, initial_notifications, status = self.make_request('GET', f'api/user/{user_id}/notifications')
        if not success:
            self.log_test("Notifications API - Initial State", False, f"Status: {status}")
            return False
            
        initial_count = len(initial_notifications)
        self.log_test("Notifications API - Initial State", True, f"Found {initial_count} existing notifications")
        
        # Create new notification
        notification_data = {
            "title": "Enhanced Notification System Test",
            "message": "This is a comprehensive test of the enhanced header notification system with full integration testing.",
            "type": "info"
        }
        
        success, create_response, status = self.make_request(
            'POST', f'api/user/{user_id}/notifications', notification_data
        )
        
        notification_id = None
        if success and 'id' in create_response:
            notification_id = create_response['id']
            self.log_test("Notifications API - Create Notification", True, f"Notification created with ID: {notification_id}")
        else:
            self.log_test("Notifications API - Create Notification", False, f"Status: {status}")
            return False
            
        # Verify notification creation
        success, updated_notifications, status = self.make_request('GET', f'api/user/{user_id}/notifications')
        if success:
            new_notification = next((notif for notif in updated_notifications if notif.get('id') == notification_id), None)
            if new_notification:
                self.log_test("Notifications API - Verify Creation", True, "New notification found in list")
                
                # Check notification structure
                required_fields = ['user_id', 'title', 'message', 'type', 'is_read', 'created_at']
                has_complete_structure = all(field in new_notification for field in required_fields)
                
                if has_complete_structure:
                    self.log_test("Notifications API - Structure Verification", True, "Complete notification structure verified")
                else:
                    missing_fields = [field for field in required_fields if field not in new_notification]
                    self.log_test("Notifications API - Structure Verification", False, f"Missing fields: {missing_fields}")
                    
                # Test mark as read functionality
                if not new_notification.get('is_read', True):
                    success, read_response, status = self.make_request(
                        'PUT', f'api/user/{user_id}/notifications/{notification_id}/read'
                    )
                    
                    if success:
                        self.log_test("Notifications API - Mark as Read", True, 
                                     f"Response: {read_response.get('message', 'Success')}")
                        
                        # Verify read status
                        success, verify_read, status = self.make_request('GET', f'api/user/{user_id}/notifications')
                        if success:
                            updated_notification = next((notif for notif in verify_read if notif.get('id') == notification_id), None)
                            if updated_notification and updated_notification.get('is_read'):
                                self.log_test("Notifications API - Read Status Verification", True, "Notification marked as read")
                            else:
                                self.log_test("Notifications API - Read Status Verification", False, "Read status not updated")
                    else:
                        self.log_test("Notifications API - Mark as Read", False, f"Status: {status}")
                else:
                    self.log_test("Notifications API - Mark as Read", True, "Notification already marked as read")
            else:
                self.log_test("Notifications API - Verify Creation", False, "New notification not found in list")
        else:
            self.log_test("Notifications API - Verify Creation", False, f"Status: {status}")
            
        return True

    def test_integration_and_performance(self):
        """Test integration between all systems and performance"""
        print("\n🔗 Testing Integration and Performance...")
        
        user_id = self.regular_user['id']
        
        # Test cross-system integration
        print("   Testing cross-system integration...")
        
        # Add item to favorites and cart simultaneously
        success_fav, _, _ = self.make_request('POST', f'api/user/{user_id}/favorites/{self.test_listing_id}')
        cart_data = {"item_id": self.test_listing_id, "quantity": 1, "price": 50.00}
        success_cart, _, _ = self.make_request('POST', f'api/user/{user_id}/cart', cart_data)
        
        # Create notification about the action
        notification_data = {
            "title": "Item Added to Favorites and Cart",
            "message": f"Item {self.test_listing_id} has been added to both favorites and cart",
            "type": "success"
        }
        success_notif, _, _ = self.make_request('POST', f'api/user/{user_id}/notifications', notification_data)
        
        if success_fav and success_cart and success_notif:
            self.log_test("Integration - Cross-System Operations", True, "All systems updated successfully")
        else:
            self.log_test("Integration - Cross-System Operations", False, "Some systems failed to update")
            
        # Test performance of key endpoints
        endpoints_to_test = [
            ('GET', f'api/user/{user_id}/favorites'),
            ('GET', f'api/user/{user_id}/cart'),
            ('GET', f'api/user/{user_id}/messages'),
            ('GET', f'api/user/{user_id}/notifications'),
            ('GET', 'api/marketplace/browse')
        ]
        
        response_times = []
        all_fast = True
        
        for method, endpoint in endpoints_to_test:
            start_time = time.time()
            success, _, status = self.make_request(method, endpoint)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times.append(response_time)
            
            if response_time > 1000:  # More than 1 second
                all_fast = False
                
        avg_response_time = sum(response_times) / len(response_times)
        
        if all_fast and avg_response_time < 500:
            self.log_test("Performance - Response Times", True, f"Average: {avg_response_time:.0f}ms")
        else:
            self.log_test("Performance - Response Times", False, f"Average: {avg_response_time:.0f}ms (too slow)")
            
        # Cleanup test data
        self.make_request('DELETE', f'api/user/{user_id}/favorites/{self.test_listing_id}')
        self.make_request('DELETE', f'api/user/{user_id}/cart/{self.test_listing_id}')
        
        return True

    def run_comprehensive_tests(self):
        """Run all comprehensive enhanced functionality tests"""
        print("🚀 Starting Comprehensive Enhanced Functionality Tests")
        print("=" * 70)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment - stopping tests")
            return False
        
        # Run comprehensive tests
        print("\n🔥 Running Comprehensive Enhanced Feature Tests...")
        
        self.test_favorites_api_comprehensive()
        self.test_cart_api_comprehensive()
        self.test_messaging_api_comprehensive()
        self.test_notifications_api_comprehensive()
        self.test_integration_and_performance()
        
        # Print results
        print("\n" + "=" * 70)
        print(f"📊 Comprehensive Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        if success_rate >= 95:
            print(f"🎉 Excellent! {success_rate:.1f}% success rate - Enhanced functionality is working perfectly!")
            return True
        elif success_rate >= 85:
            print(f"✅ Good! {success_rate:.1f}% success rate - Enhanced functionality is mostly working")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {success_rate:.1f}% success rate - {failed_tests} tests failed")
            return False

def main():
    """Main test execution"""
    tester = ComprehensiveEnhancedTester()
    success = tester.run_comprehensive_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())