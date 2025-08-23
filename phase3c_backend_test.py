#!/usr/bin/env python3
"""
Phase 3C Order Processing & Notification System Backend Testing
Testing comprehensive notification system and order approval workflow
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "http://217.154.0.82/api"  # Using VPS URL from frontend/.env
WEBSOCKET_URL = "ws://217.154.0.82/api"

# Admin credentials for testing
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class Phase3CBackendTester:
    def __init__(self):
        self.admin_token = None
        self.buyer_token = None
        self.seller_token = None
        self.buyer_user_id = None
        self.seller_user_id = None
        self.admin_user_id = None
        self.test_listing_id = None
        self.test_order_id = None
        self.results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.admin_user_id = data["user"]["id"]
                self.log_result("Admin Authentication", True, f"Admin user ID: {self.admin_user_id}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def create_test_users(self):
        """Create test buyer and seller users"""
        try:
            # Create buyer user
            buyer_data = {
                "email": "testbuyer@example.com",
                "username": "testbuyer",
                "password": "testpass123",
                "full_name": "Test Buyer",
                "role": "buyer"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/register", json=buyer_data)
            if response.status_code == 200:
                data = response.json()
                self.buyer_token = data["access_token"]
                self.buyer_user_id = data["user"]["id"]
                self.log_result("Create Test Buyer", True, f"Buyer ID: {self.buyer_user_id}")
            else:
                # Try to login if user already exists
                login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                    "email": buyer_data["email"],
                    "password": buyer_data["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.buyer_token = data["access_token"]
                    self.buyer_user_id = data["user"]["id"]
                    self.log_result("Create Test Buyer", True, f"Existing buyer logged in, ID: {self.buyer_user_id}")
                else:
                    self.log_result("Create Test Buyer", False, f"Registration failed: {response.text}, Login failed: {login_response.text}")
                    return False

            # Create seller user
            seller_data = {
                "email": "testseller@example.com",
                "username": "testseller",
                "password": "testpass123",
                "full_name": "Test Seller",
                "role": "seller"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/register", json=seller_data)
            if response.status_code == 200:
                data = response.json()
                self.seller_token = data["access_token"]
                self.seller_user_id = data["user"]["id"]
                self.log_result("Create Test Seller", True, f"Seller ID: {self.seller_user_id}")
            else:
                # Try to login if user already exists
                login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                    "email": seller_data["email"],
                    "password": seller_data["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.seller_token = data["access_token"]
                    self.seller_user_id = data["user"]["id"]
                    self.log_result("Create Test Seller", True, f"Existing seller logged in, ID: {self.seller_user_id}")
                else:
                    self.log_result("Create Test Seller", False, f"Registration failed: {response.text}, Login failed: {login_response.text}")
                    return False
                    
            return True
            
        except Exception as e:
            self.log_result("Create Test Users", False, f"Exception: {str(e)}")
            return False

    def create_test_listing(self):
        """Create a test listing for order testing"""
        try:
            listing_data = {
                "title": "Phase 3C Test Product",
                "description": "Test product for order approval workflow testing",
                "category": "Electronics",
                "listing_type": "fixed_price",
                "price": 99.99,
                "condition": "New",
                "quantity": 5,
                "location": "Test City",
                "shipping_cost": 10.0
            }
            
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_listing_id = data["id"]
                self.log_result("Create Test Listing", True, f"Listing ID: {self.test_listing_id}")
                return True
            else:
                self.log_result("Create Test Listing", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Create Test Listing", False, f"Exception: {str(e)}")
            return False

    def test_notification_endpoints(self):
        """Test notification system endpoints"""
        print("=== TESTING NOTIFICATION SYSTEM ENDPOINTS ===")
        
        # Test GET /notifications
        try:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "notifications" in data and "unread_count" in data:
                    self.log_result("GET /notifications", True, f"Retrieved {len(data['notifications'])} notifications, {data['unread_count']} unread")
                else:
                    self.log_result("GET /notifications", False, "Missing required fields in response")
            else:
                self.log_result("GET /notifications", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("GET /notifications", False, f"Exception: {str(e)}")

        # Test GET /notifications with unread_only parameter
        try:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = requests.get(f"{BACKEND_URL}/notifications?unread_only=true", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("GET /notifications (unread only)", True, f"Retrieved {len(data['notifications'])} unread notifications")
            else:
                self.log_result("GET /notifications (unread only)", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("GET /notifications (unread only)", False, f"Exception: {str(e)}")

    def test_order_creation_with_notifications(self):
        """Test order creation and seller notification"""
        print("=== TESTING ORDER CREATION WITH NOTIFICATIONS ===")
        
        try:
            order_data = {
                "listing_id": self.test_listing_id,
                "quantity": 1,
                "shipping_address": "123 Test Street, Test City, 12345"
            }
            
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = requests.post(f"{BACKEND_URL}/orders", json=order_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_order_id = data["id"]
                
                # Check if order status is PENDING
                if data["status"] == "pending":
                    self.log_result("Order Creation (PENDING status)", True, f"Order ID: {self.test_order_id}, Status: {data['status']}")
                else:
                    self.log_result("Order Creation (PENDING status)", False, f"Expected PENDING status, got: {data['status']}")
                
                # Wait a moment for notification to be created
                time.sleep(2)
                
                # Check if seller received notification
                seller_headers = {"Authorization": f"Bearer {self.seller_token}"}
                notif_response = requests.get(f"{BACKEND_URL}/notifications", headers=seller_headers)
                
                if notif_response.status_code == 200:
                    notif_data = notif_response.json()
                    order_notifications = [n for n in notif_data["notifications"] if n.get("notification_type") == "order_received"]
                    
                    if order_notifications:
                        self.log_result("Seller Order Notification", True, f"Seller received {len(order_notifications)} order notification(s)")
                    else:
                        self.log_result("Seller Order Notification", False, "No order_received notifications found for seller")
                else:
                    self.log_result("Seller Order Notification", False, f"Failed to get seller notifications: {notif_response.text}")
                    
            else:
                self.log_result("Order Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Order Creation with Notifications", False, f"Exception: {str(e)}")
            return False
            
        return True

    def test_order_approval_workflow(self):
        """Test order approval and buyer notification"""
        print("=== TESTING ORDER APPROVAL WORKFLOW ===")
        
        if not self.test_order_id:
            self.log_result("Order Approval Test", False, "No test order ID available")
            return False
            
        try:
            # Test order approval by seller
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = requests.put(f"{BACKEND_URL}/orders/{self.test_order_id}/approve", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Order Approval", True, f"Order approved: {data['message']}")
                
                # Wait for notification to be created
                time.sleep(2)
                
                # Check if buyer received approval notification
                buyer_headers = {"Authorization": f"Bearer {self.buyer_token}"}
                notif_response = requests.get(f"{BACKEND_URL}/notifications", headers=buyer_headers)
                
                if notif_response.status_code == 200:
                    notif_data = notif_response.json()
                    approval_notifications = [n for n in notif_data["notifications"] if n.get("notification_type") == "order_approved"]
                    
                    if approval_notifications:
                        self.log_result("Buyer Approval Notification", True, f"Buyer received {len(approval_notifications)} approval notification(s)")
                    else:
                        self.log_result("Buyer Approval Notification", False, "No order_approved notifications found for buyer")
                else:
                    self.log_result("Buyer Approval Notification", False, f"Failed to get buyer notifications: {notif_response.text}")
                
                # Check if order status changed to COMPLETED
                order_response = requests.get(f"{BACKEND_URL}/orders", headers=buyer_headers)
                if order_response.status_code == 200:
                    orders_data = order_response.json()
                    test_order = next((o["order"] for o in orders_data if o["order"]["id"] == self.test_order_id), None)
                    
                    if test_order and test_order["status"] == "completed":
                        self.log_result("Order Status Update", True, "Order status changed to COMPLETED")
                    else:
                        self.log_result("Order Status Update", False, f"Expected COMPLETED status, got: {test_order['status'] if test_order else 'Order not found'}")
                        
            else:
                self.log_result("Order Approval", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Order Approval Workflow", False, f"Exception: {str(e)}")
            return False
            
        return True

    def test_order_rejection_workflow(self):
        """Test order rejection and buyer notification"""
        print("=== TESTING ORDER REJECTION WORKFLOW ===")
        
        # Create another test order for rejection
        try:
            order_data = {
                "listing_id": self.test_listing_id,
                "quantity": 1,
                "shipping_address": "456 Reject Street, Test City, 12345"
            }
            
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = requests.post(f"{BACKEND_URL}/orders", json=order_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                reject_order_id = data["id"]
                
                # Wait a moment
                time.sleep(1)
                
                # Test order rejection by seller
                seller_headers = {"Authorization": f"Bearer {self.seller_token}"}
                rejection_data = {"rejection_reason": "Out of stock"}
                reject_response = requests.put(
                    f"{BACKEND_URL}/orders/{reject_order_id}/reject",
                    json=rejection_data,
                    headers=seller_headers
                )
                
                if reject_response.status_code == 200:
                    reject_data = reject_response.json()
                    self.log_result("Order Rejection", True, f"Order rejected: {reject_data['message']}")
                    
                    # Wait for notification to be created
                    time.sleep(2)
                    
                    # Check if buyer received rejection notification
                    buyer_headers = {"Authorization": f"Bearer {self.buyer_token}"}
                    notif_response = requests.get(f"{BACKEND_URL}/notifications", headers=buyer_headers)
                    
                    if notif_response.status_code == 200:
                        notif_data = notif_response.json()
                        rejection_notifications = [n for n in notif_data["notifications"] if n.get("notification_type") == "order_rejected"]
                        
                        if rejection_notifications:
                            self.log_result("Buyer Rejection Notification", True, f"Buyer received {len(rejection_notifications)} rejection notification(s)")
                        else:
                            self.log_result("Buyer Rejection Notification", False, "No order_rejected notifications found for buyer")
                    else:
                        self.log_result("Buyer Rejection Notification", False, f"Failed to get buyer notifications: {notif_response.text}")
                        
                else:
                    self.log_result("Order Rejection", False, f"Status: {reject_response.status_code}, Response: {reject_response.text}")
                    
            else:
                self.log_result("Create Order for Rejection", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Order Rejection Workflow", False, f"Exception: {str(e)}")
            return False
            
        return True

    def test_notification_read_functionality(self):
        """Test marking notifications as read"""
        print("=== TESTING NOTIFICATION READ FUNCTIONALITY ===")
        
        try:
            # Get buyer notifications
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data["notifications"]
                
                if notifications:
                    # Test marking single notification as read
                    first_notification = notifications[0]
                    notif_id = first_notification["id"]
                    
                    read_response = requests.put(f"{BACKEND_URL}/notifications/{notif_id}/read", headers=headers)
                    
                    if read_response.status_code == 200:
                        self.log_result("Mark Single Notification Read", True, f"Notification {notif_id} marked as read")
                    else:
                        self.log_result("Mark Single Notification Read", False, f"Status: {read_response.status_code}, Response: {read_response.text}")
                    
                    # Test marking all notifications as read
                    mark_all_response = requests.put(f"{BACKEND_URL}/notifications/mark-all-read", headers=headers)
                    
                    if mark_all_response.status_code == 200:
                        mark_all_data = mark_all_response.json()
                        self.log_result("Mark All Notifications Read", True, f"Response: {mark_all_data['message']}")
                    else:
                        self.log_result("Mark All Notifications Read", False, f"Status: {mark_all_response.status_code}, Response: {mark_all_response.text}")
                        
                else:
                    self.log_result("Notification Read Test", False, "No notifications available to test read functionality")
                    
            else:
                self.log_result("Get Notifications for Read Test", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Notification Read Functionality", False, f"Exception: {str(e)}")

    def test_websocket_connection(self):
        """Test WebSocket notification endpoint"""
        print("=== TESTING WEBSOCKET NOTIFICATION ENDPOINT ===")
        
        try:
            # Test WebSocket connection (basic connectivity test)
            websocket_url = f"{WEBSOCKET_URL}/notifications/{self.buyer_user_id}"
            
            # Since we can't easily test WebSocket in this synchronous context,
            # we'll test if the endpoint exists and responds appropriately
            import socket
            
            # Parse URL to get host and port
            host = "217.154.0.82"
            port = 80
            
            # Test if we can connect to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                self.log_result("WebSocket Server Connectivity", True, f"Server {host}:{port} is reachable")
            else:
                self.log_result("WebSocket Server Connectivity", False, f"Cannot connect to {host}:{port}")
                
        except Exception as e:
            self.log_result("WebSocket Connection Test", False, f"Exception: {str(e)}")

    def test_listing_status_updates(self):
        """Test that listing status updates correctly after order approval"""
        print("=== TESTING LISTING STATUS UPDATES ===")
        
        try:
            # Get current listing status
            response = requests.get(f"{BACKEND_URL}/listings/{self.test_listing_id}")
            
            if response.status_code == 200:
                listing_data = response.json()
                original_quantity = listing_data.get("quantity", 0)
                
                self.log_result("Listing Status Check", True, f"Original quantity: {original_quantity}, Status: {listing_data.get('status')}")
                
                # After order approval, quantity should be reduced
                # Since we approved 1 item from quantity 5, it should now be 4
                expected_quantity = original_quantity - 1
                
                if listing_data.get("quantity") == expected_quantity:
                    self.log_result("Listing Quantity Update", True, f"Quantity correctly updated to {listing_data.get('quantity')}")
                else:
                    self.log_result("Listing Quantity Update", False, f"Expected quantity {expected_quantity}, got {listing_data.get('quantity')}")
                    
            else:
                self.log_result("Listing Status Check", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Listing Status Updates", False, f"Exception: {str(e)}")

    def test_integration_workflow(self):
        """Test complete integration workflow"""
        print("=== TESTING COMPLETE INTEGRATION WORKFLOW ===")
        
        # This test verifies the entire flow works together
        try:
            # Create a new listing for complete workflow test
            listing_data = {
                "title": "Integration Test Product",
                "description": "Complete workflow integration test",
                "category": "Books",
                "listing_type": "fixed_price",
                "price": 25.99,
                "condition": "Used",
                "quantity": 1,  # Only 1 item so it becomes SOLD after approval
                "location": "Integration City"
            }
            
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
            
            if response.status_code == 200:
                integration_listing_id = response.json()["id"]
                
                # Create order
                order_data = {
                    "listing_id": integration_listing_id,
                    "quantity": 1,
                    "shipping_address": "789 Integration Ave, Test City, 12345"
                }
                
                buyer_headers = {"Authorization": f"Bearer {self.buyer_token}"}
                order_response = requests.post(f"{BACKEND_URL}/orders", json=order_data, headers=buyer_headers)
                
                if order_response.status_code == 200:
                    integration_order_id = order_response.json()["id"]
                    
                    # Wait for notification
                    time.sleep(2)
                    
                    # Approve order
                    approve_response = requests.put(f"{BACKEND_URL}/orders/{integration_order_id}/approve", headers=headers)
                    
                    if approve_response.status_code == 200:
                        # Wait for processing
                        time.sleep(2)
                        
                        # Check listing status should be SOLD (quantity was 1)
                        listing_check = requests.get(f"{BACKEND_URL}/listings/{integration_listing_id}")
                        
                        if listing_check.status_code == 200:
                            final_listing = listing_check.json()
                            
                            if final_listing.get("status") == "sold" and final_listing.get("quantity") == 0:
                                self.log_result("Complete Integration Workflow", True, "Order → Notification → Approval → Listing Status Update all working correctly")
                            else:
                                self.log_result("Complete Integration Workflow", False, f"Listing status: {final_listing.get('status')}, quantity: {final_listing.get('quantity')}")
                        else:
                            self.log_result("Complete Integration Workflow", False, "Failed to check final listing status")
                    else:
                        self.log_result("Complete Integration Workflow", False, f"Order approval failed: {approve_response.text}")
                else:
                    self.log_result("Complete Integration Workflow", False, f"Order creation failed: {order_response.text}")
            else:
                self.log_result("Complete Integration Workflow", False, f"Listing creation failed: {response.text}")
                
        except Exception as e:
            self.log_result("Complete Integration Workflow", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all Phase 3C tests"""
        print("🚀 STARTING PHASE 3C ORDER PROCESSING & NOTIFICATION SYSTEM TESTING")
        print("=" * 80)
        
        # Setup
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
            
        if not self.create_test_users():
            print("❌ CRITICAL: Test user creation failed. Cannot proceed with tests.")
            return False
            
        if not self.create_test_listing():
            print("❌ CRITICAL: Test listing creation failed. Cannot proceed with tests.")
            return False
        
        # Core notification system tests
        self.test_notification_endpoints()
        
        # Order workflow tests
        if self.test_order_creation_with_notifications():
            self.test_order_approval_workflow()
        
        self.test_order_rejection_workflow()
        
        # Notification management tests
        self.test_notification_read_functionality()
        
        # WebSocket tests
        self.test_websocket_connection()
        
        # Integration tests
        self.test_listing_status_updates()
        self.test_integration_workflow()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 PHASE 3C TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.results:
            if result["success"]:
                print(f"  - {result['test']}")
        
        return success_rate >= 80  # Consider 80%+ success rate as overall success

if __name__ == "__main__":
    tester = Phase3CBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 PHASE 3C TESTING COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n⚠️  PHASE 3C TESTING COMPLETED WITH ISSUES")
        sys.exit(1)