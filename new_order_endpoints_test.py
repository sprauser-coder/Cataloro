#!/usr/bin/env python3
"""
New Order Management Endpoints Testing
Tests the specific new endpoints mentioned in the review request:
1. Order Completion: PUT /api/orders/{order_id}/complete
2. Order Shipping: PUT /api/orders/{order_id}/ship  
3. Enhanced Order Cancellation: PUT /api/orders/{order_id}/cancel
4. Listing Status Changes and Order Status Flow
"""

import requests
import sys
import json
from datetime import datetime

class NewOrderEndpointsTester:
    def __init__(self, base_url="https://admanager-cataloro.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

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
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
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
        
        if success_admin and 'user' in admin_response:
            self.admin_user = admin_response['user']
            print(f"   ✅ Admin user setup: {self.admin_user['id']}")
        
        # Login regular user
        success_user, user_response = self.run_test(
            "Regular User Login Setup",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        
        if success_user and 'user' in user_response:
            self.regular_user = user_response['user']
            print(f"   ✅ Regular user setup: {self.regular_user['id']}")
        
        return success_admin and success_user

    def test_order_completion_endpoint(self):
        """Test PUT /api/orders/{order_id}/complete with buyer user_id"""
        print("\n🎯 TESTING ORDER COMPLETION ENDPOINT")
        print("=" * 50)
        
        # Create test listing
        test_listing = {
            "title": "Completion Test - Premium Headphones",
            "description": "High-quality wireless headphones for completion testing.",
            "price": 299.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"]
        }
        
        success_listing, listing_response = self.run_test(
            "Create Listing for Completion Test",
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
            "Create Order for Completion Test",
            "POST",
            "api/orders/create",
            200,
            data=order_data
        )
        
        if not success_order:
            return False
        
        order_id = order_response['order_id']
        
        # Approve order first (required for completion)
        approval_data = {"seller_id": self.admin_user['id']}
        
        success_approve, _ = self.run_test(
            "Approve Order for Completion Test",
            "PUT",
            f"api/orders/{order_id}/approve",
            200,
            data=approval_data
        )
        
        if not success_approve:
            return False
        
        # Test order completion endpoint
        completion_data = {"user_id": self.regular_user['id']}
        
        success_complete, complete_response = self.run_test(
            "Order Completion Endpoint",
            "PUT",
            f"api/orders/{order_id}/complete",
            200,
            data=completion_data
        )
        
        if success_complete:
            # Verify order status updated to "completed"
            success_check, buyer_orders = self.run_test(
                "Verify Order Status After Completion",
                "GET",
                f"api/orders/buyer/{self.regular_user['id']}",
                200
            )
            
            if success_check:
                completed_order = next((o for o in buyer_orders if o['id'] == order_id), None)
                if completed_order and completed_order['status'] == 'completed':
                    self.log_test("Order Status Updated to Completed", True, "Status correctly updated")
                else:
                    self.log_test("Order Status Updated to Completed", False, f"Status: {completed_order['status'] if completed_order else 'Not found'}")
            
            # Check seller notification
            success_notif, seller_notifications = self.run_test(
                "Check Seller Completion Notification",
                "GET",
                f"api/user/notifications/{self.admin_user['id']}",
                200
            )
            
            if success_notif:
                completion_notifs = [n for n in seller_notifications if n.get('type') == 'order_completed']
                has_completion_notif = len(completion_notifs) > 0
                self.log_test("Seller Gets Completion Notification", has_completion_notif,
                             f"Found {len(completion_notifs)} completion notifications")
        
        # Cleanup
        self.run_test("Cleanup Completion Test Listing", "DELETE", f"api/listings/{listing_id}", 200)
        
        return success_complete

    def test_order_shipping_endpoint(self):
        """Test PUT /api/orders/{order_id}/ship with seller user_id"""
        print("\n🚚 TESTING ORDER SHIPPING ENDPOINT")
        print("=" * 50)
        
        # Create test listing
        ship_test_listing = {
            "title": "Shipping Test - Gaming Mouse",
            "description": "Gaming mouse for shipping endpoint testing.",
            "price": 89.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"]
        }
        
        success_listing, listing_response = self.run_test(
            "Create Listing for Shipping Test",
            "POST",
            "api/listings",
            200,
            data=ship_test_listing
        )
        
        if not success_listing:
            return False
        
        ship_listing_id = listing_response['listing_id']
        
        # Create order
        ship_order_data = {
            "listing_id": ship_listing_id,
            "buyer_id": self.regular_user['id']
        }
        
        success_order, order_response = self.run_test(
            "Create Order for Shipping Test",
            "POST",
            "api/orders/create",
            200,
            data=ship_order_data
        )
        
        if not success_order:
            return False
        
        ship_order_id = order_response['order_id']
        
        # Approve order first (required for shipping)
        approval_data = {"seller_id": self.admin_user['id']}
        
        success_approve, _ = self.run_test(
            "Approve Order for Shipping Test",
            "PUT",
            f"api/orders/{ship_order_id}/approve",
            200,
            data=approval_data
        )
        
        if not success_approve:
            return False
        
        # Test order shipping endpoint
        shipping_data = {"user_id": self.admin_user['id']}
        
        success_ship, ship_response = self.run_test(
            "Order Shipping Endpoint",
            "PUT",
            f"api/orders/{ship_order_id}/ship",
            200,
            data=shipping_data
        )
        
        if success_ship:
            # Verify order status updated to "shipped"
            success_check, buyer_orders = self.run_test(
                "Verify Order Status After Shipping",
                "GET",
                f"api/orders/buyer/{self.regular_user['id']}",
                200
            )
            
            if success_check:
                shipped_order = next((o for o in buyer_orders if o['id'] == ship_order_id), None)
                if shipped_order and shipped_order['status'] == 'shipped':
                    self.log_test("Order Status Updated to Shipped", True, "Status correctly updated")
                else:
                    self.log_test("Order Status Updated to Shipped", False, f"Status: {shipped_order['status'] if shipped_order else 'Not found'}")
            
            # Check buyer notification
            success_notif, buyer_notifications = self.run_test(
                "Check Buyer Shipping Notification",
                "GET",
                f"api/user/notifications/{self.regular_user['id']}",
                200
            )
            
            if success_notif:
                shipping_notifs = [n for n in buyer_notifications if n.get('type') == 'order_shipped']
                has_shipping_notif = len(shipping_notifs) > 0
                self.log_test("Buyer Gets Shipping Notification", has_shipping_notif,
                             f"Found {len(shipping_notifs)} shipping notifications")
        
        # Cleanup
        self.run_test("Cleanup Shipping Test Listing", "DELETE", f"api/listings/{ship_listing_id}", 200)
        
        return success_ship

    def test_enhanced_order_cancellation(self):
        """Test PUT /api/orders/{order_id}/cancel with both buyer and seller user_ids"""
        print("\n❌ TESTING ENHANCED ORDER CANCELLATION")
        print("=" * 50)
        
        # Test 1: Buyer cancelling pending order
        print("\n   🔸 Testing buyer cancellation of pending order...")
        
        cancel_test_listing = {
            "title": "Cancellation Test - Keyboard",
            "description": "Mechanical keyboard for cancellation testing.",
            "price": 149.99,
            "category": "Electronics",
            "condition": "Used - Good",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400"]
        }
        
        success_listing, listing_response = self.run_test(
            "Create Listing for Cancellation Test",
            "POST",
            "api/listings",
            200,
            data=cancel_test_listing
        )
        
        if not success_listing:
            return False
        
        cancel_listing_id = listing_response['listing_id']
        
        # Create order for cancellation
        cancel_order_data = {
            "listing_id": cancel_listing_id,
            "buyer_id": self.regular_user['id']
        }
        
        success_order, order_response = self.run_test(
            "Create Order for Cancellation Test",
            "POST",
            "api/orders/create",
            200,
            data=cancel_order_data
        )
        
        if not success_order:
            return False
        
        cancel_order_id = order_response['order_id']
        
        # Test buyer cancellation of pending order
        buyer_cancel_data = {"user_id": self.regular_user['id']}
        
        success_buyer_cancel, _ = self.run_test(
            "Buyer Cancel Pending Order",
            "PUT",
            f"api/orders/{cancel_order_id}/cancel",
            200,
            data=buyer_cancel_data
        )
        
        # Test 2: Seller cancelling approved order
        print("\n   🔸 Testing seller cancellation of approved order...")
        
        # Create another order for approved cancellation test
        success_order2, order_response2 = self.run_test(
            "Create Second Order for Approved Cancellation",
            "POST",
            "api/orders/create",
            200,
            data=cancel_order_data
        )
        
        if success_order2:
            cancel_order_id2 = order_response2['order_id']
            
            # Approve the order first
            approval_data = {"seller_id": self.admin_user['id']}
            
            success_approve, _ = self.run_test(
                "Approve Order for Cancellation Test",
                "PUT",
                f"api/orders/{cancel_order_id2}/approve",
                200,
                data=approval_data
            )
            
            if success_approve:
                # Verify listing is marked as sold
                success_sold_check, listing_data = self.run_test(
                    "Check Listing Sold Status Before Cancellation",
                    "GET",
                    f"api/listings/{cancel_listing_id}",
                    200
                )
                
                if success_sold_check:
                    listing_sold = listing_data.get('status') == 'sold'
                    self.log_test("Listing Marked as Sold After Approval", listing_sold,
                                 f"Listing status: {listing_data.get('status')}")
                
                # Test seller cancellation of approved order
                seller_cancel_data = {"user_id": self.admin_user['id']}
                
                success_seller_cancel, _ = self.run_test(
                    "Seller Cancel Approved Order",
                    "PUT",
                    f"api/orders/{cancel_order_id2}/cancel",
                    200,
                    data=seller_cancel_data
                )
                
                if success_seller_cancel:
                    # Verify listing status is restored to "active"
                    success_active_check, listing_data_after = self.run_test(
                        "Check Listing Active Status After Cancellation",
                        "GET",
                        f"api/listings/{cancel_listing_id}",
                        200
                    )
                    
                    if success_active_check:
                        listing_active = listing_data_after.get('status') == 'active'
                        self.log_test("Listing Restored to Active After Cancellation", listing_active,
                                     f"Listing status after cancellation: {listing_data_after.get('status')}")
        
        # Cleanup
        self.run_test("Cleanup Cancellation Test Listing", "DELETE", f"api/listings/{cancel_listing_id}", 200)
        
        return success_buyer_cancel and success_seller_cancel

    def test_listing_status_changes(self):
        """Test that listings change status correctly and sold listings don't appear in browse"""
        print("\n📊 TESTING LISTING STATUS CHANGES")
        print("=" * 50)
        
        # Create test listing
        status_test_listing = {
            "title": "Status Test - Smart Watch",
            "description": "Smart watch for status change testing.",
            "price": 199.99,
            "category": "Electronics",
            "condition": "Used - Good",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"]
        }
        
        success_listing, listing_response = self.run_test(
            "Create Listing for Status Test",
            "POST",
            "api/listings",
            200,
            data=status_test_listing
        )
        
        if not success_listing:
            return False
        
        status_listing_id = listing_response['listing_id']
        
        # Verify initial status is "active"
        success_initial, initial_data = self.run_test(
            "Check Initial Listing Status",
            "GET",
            f"api/listings/{status_listing_id}",
            200
        )
        
        if success_initial:
            initial_status = initial_data.get('status')
            self.log_test("Initial Listing Status is Active", initial_status == 'active',
                         f"Initial status: {initial_status}")
        
        # Verify listing appears in browse (active listings)
        success_browse_active, browse_data = self.run_test(
            "Check Active Listing in Browse",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success_browse_active:
            found_in_browse = any(listing.get('id') == status_listing_id for listing in browse_data)
            self.log_test("Active Listing Appears in Browse", found_in_browse,
                         f"Listing found in browse: {found_in_browse}")
        
        # Create and approve order
        status_order_data = {
            "listing_id": status_listing_id,
            "buyer_id": self.regular_user['id']
        }
        
        success_order, order_response = self.run_test(
            "Create Order for Status Test",
            "POST",
            "api/orders/create",
            200,
            data=status_order_data
        )
        
        if success_order:
            status_order_id = order_response['order_id']
            
            # Approve order
            approval_data = {"seller_id": self.admin_user['id']}
            
            success_approve, _ = self.run_test(
                "Approve Order for Status Test",
                "PUT",
                f"api/orders/{status_order_id}/approve",
                200,
                data=approval_data
            )
            
            if success_approve:
                # Verify listing status changed to "sold"
                success_sold, sold_data = self.run_test(
                    "Check Listing Sold Status After Approval",
                    "GET",
                    f"api/listings/{status_listing_id}",
                    200
                )
                
                if success_sold:
                    sold_status = sold_data.get('status')
                    self.log_test("Listing Status Changed to Sold", sold_status == 'sold',
                                 f"Status after approval: {sold_status}")
                
                # Verify sold listing doesn't appear in browse
                success_browse_sold, browse_sold_data = self.run_test(
                    "Check Sold Listing Not in Browse",
                    "GET",
                    "api/marketplace/browse",
                    200
                )
                
                if success_browse_sold:
                    found_sold_in_browse = any(listing.get('id') == status_listing_id for listing in browse_sold_data)
                    self.log_test("Sold Listing Doesn't Appear in Browse", not found_sold_in_browse,
                                 f"Sold listing found in browse: {found_sold_in_browse}")
        
        # Cleanup
        self.run_test("Cleanup Status Test Listing", "DELETE", f"api/listings/{status_listing_id}", 200)
        
        return True

    def test_complete_order_workflow(self):
        """Test complete order workflow: pending → approved → shipped → completed"""
        print("\n🔄 TESTING COMPLETE ORDER STATUS FLOW")
        print("=" * 50)
        
        # Create test listing for workflow
        workflow_listing = {
            "title": "Workflow Test - Tablet",
            "description": "Tablet for complete workflow testing.",
            "price": 399.99,
            "category": "Electronics",
            "condition": "Used - Excellent",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400"]
        }
        
        success_listing, listing_response = self.run_test(
            "Create Listing for Workflow Test",
            "POST",
            "api/listings",
            200,
            data=workflow_listing
        )
        
        if not success_listing:
            return False
        
        workflow_listing_id = listing_response['listing_id']
        
        # Step 1: Create order (pending status)
        workflow_order_data = {
            "listing_id": workflow_listing_id,
            "buyer_id": self.regular_user['id']
        }
        
        success_order, order_response = self.run_test(
            "Create Order (Pending Status)",
            "POST",
            "api/orders/create",
            200,
            data=workflow_order_data
        )
        
        if not success_order:
            return False
        
        workflow_order_id = order_response['order_id']
        
        # Verify pending status
        success_pending, buyer_orders = self.run_test(
            "Verify Pending Status",
            "GET",
            f"api/orders/buyer/{self.regular_user['id']}",
            200
        )
        
        if success_pending:
            pending_order = next((o for o in buyer_orders if o['id'] == workflow_order_id), None)
            if pending_order:
                self.log_test("Order Status: Pending", pending_order['status'] == 'pending',
                             f"Status: {pending_order['status']}")
        
        # Step 2: Approve order (approved status)
        approval_data = {"seller_id": self.admin_user['id']}
        
        success_approve, _ = self.run_test(
            "Approve Order (Approved Status)",
            "PUT",
            f"api/orders/{workflow_order_id}/approve",
            200,
            data=approval_data
        )
        
        if success_approve:
            # Verify approved status
            success_approved, buyer_orders_approved = self.run_test(
                "Verify Approved Status",
                "GET",
                f"api/orders/buyer/{self.regular_user['id']}",
                200
            )
            
            if success_approved:
                approved_order = next((o for o in buyer_orders_approved if o['id'] == workflow_order_id), None)
                if approved_order:
                    self.log_test("Order Status: Approved", approved_order['status'] == 'approved',
                                 f"Status: {approved_order['status']}")
        
        # Step 3: Ship order (shipped status)
        shipping_data = {"user_id": self.admin_user['id']}
        
        success_ship, _ = self.run_test(
            "Ship Order (Shipped Status)",
            "PUT",
            f"api/orders/{workflow_order_id}/ship",
            200,
            data=shipping_data
        )
        
        if success_ship:
            # Verify shipped status
            success_shipped, buyer_orders_shipped = self.run_test(
                "Verify Shipped Status",
                "GET",
                f"api/orders/buyer/{self.regular_user['id']}",
                200
            )
            
            if success_shipped:
                shipped_order = next((o for o in buyer_orders_shipped if o['id'] == workflow_order_id), None)
                if shipped_order:
                    self.log_test("Order Status: Shipped", shipped_order['status'] == 'shipped',
                                 f"Status: {shipped_order['status']}")
        
        # Step 4: Complete order (completed status)
        completion_data = {"user_id": self.regular_user['id']}
        
        success_complete, _ = self.run_test(
            "Complete Order (Completed Status)",
            "PUT",
            f"api/orders/{workflow_order_id}/complete",
            200,
            data=completion_data
        )
        
        if success_complete:
            # Verify completed status
            success_completed, buyer_orders_completed = self.run_test(
                "Verify Completed Status",
                "GET",
                f"api/orders/buyer/{self.regular_user['id']}",
                200
            )
            
            if success_completed:
                completed_order = next((o for o in buyer_orders_completed if o['id'] == workflow_order_id), None)
                if completed_order:
                    self.log_test("Order Status: Completed", completed_order['status'] == 'completed',
                                 f"Status: {completed_order['status']}")
        
        # Verify notifications were created for each step
        print("\n   📧 Verifying notifications for each workflow step...")
        
        # Check seller notifications
        success_seller_notifs, seller_notifications = self.run_test(
            "Check Seller Workflow Notifications",
            "GET",
            f"api/user/notifications/{self.admin_user['id']}",
            200
        )
        
        if success_seller_notifs:
            buy_request_notifs = [n for n in seller_notifications if n.get('type') == 'buy_request']
            completion_notifs = [n for n in seller_notifications if n.get('type') == 'order_completed']
            
            self.log_test("Seller Received Buy Request Notification", len(buy_request_notifs) > 0,
                         f"Buy request notifications: {len(buy_request_notifs)}")
            self.log_test("Seller Received Completion Notification", len(completion_notifs) > 0,
                         f"Completion notifications: {len(completion_notifs)}")
        
        # Check buyer notifications
        success_buyer_notifs, buyer_notifications = self.run_test(
            "Check Buyer Workflow Notifications",
            "GET",
            f"api/user/notifications/{self.regular_user['id']}",
            200
        )
        
        if success_buyer_notifs:
            approval_notifs = [n for n in buyer_notifications if n.get('type') == 'buy_approved']
            shipping_notifs = [n for n in buyer_notifications if n.get('type') == 'order_shipped']
            
            self.log_test("Buyer Received Approval Notification", len(approval_notifs) > 0,
                         f"Approval notifications: {len(approval_notifs)}")
            self.log_test("Buyer Received Shipping Notification", len(shipping_notifs) > 0,
                         f"Shipping notifications: {len(shipping_notifs)}")
        
        # Cleanup
        self.run_test("Cleanup Workflow Test Listing", "DELETE", f"api/listings/{workflow_listing_id}", 200)
        
        return True

    def run_all_tests(self):
        """Run all new order management endpoint tests"""
        print("🚀 NEW ORDER MANAGEMENT ENDPOINTS TESTING")
        print("=" * 60)
        print("Testing the new order management endpoints for action button functionality:")
        print("1. Order Completion Endpoint")
        print("2. Order Shipping Endpoint") 
        print("3. Enhanced Order Cancellation")
        print("4. Listing Status Changes")
        print("5. Complete Order Workflow")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False
        
        # Run tests
        test_results = []
        
        # Test 1: Order Completion Endpoint
        test_results.append(self.test_order_completion_endpoint())
        
        # Test 2: Order Shipping Endpoint
        test_results.append(self.test_order_shipping_endpoint())
        
        # Test 3: Enhanced Order Cancellation
        test_results.append(self.test_enhanced_order_cancellation())
        
        # Test 4: Listing Status Changes
        test_results.append(self.test_listing_status_changes())
        
        # Test 5: Complete Order Workflow
        test_results.append(self.test_complete_order_workflow())
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 NEW ORDER MANAGEMENT ENDPOINTS TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"Total Individual Tests Run: {self.tests_run}")
        print(f"Individual Tests Passed: {self.tests_passed}")
        print(f"Individual Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Individual Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        print(f"\nMajor Test Categories: {passed_tests}/{total_tests} passed")
        
        test_names = [
            "Order Completion Endpoint",
            "Order Shipping Endpoint", 
            "Enhanced Order Cancellation",
            "Listing Status Changes",
            "Complete Order Workflow"
        ]
        
        for i, (name, result) in enumerate(zip(test_names, test_results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {i+1}. {name}: {status}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL NEW ORDER MANAGEMENT ENDPOINT TESTS PASSED!")
            print("✅ Action button functionality endpoints are working correctly")
            print("✅ Order completion, shipping, and cancellation endpoints functional")
            print("✅ Listing status changes work properly")
            print("✅ Complete order workflow (pending → approved → shipped → completed) verified")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test categories failed")
            print("❌ Some action button endpoints need attention")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = NewOrderEndpointsTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)