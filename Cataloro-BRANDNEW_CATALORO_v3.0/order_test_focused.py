#!/usr/bin/env python3
"""
Focused Order Management System Test
Tests only the order management endpoints
"""

import requests
import sys
import json
from datetime import datetime

class OrderManagementTester:
    def __init__(self, base_url="https://browse-ads.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
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

    def setup_users(self):
        """Setup admin and regular users"""
        print("🔧 Setting up test users...")
        
        # Admin login
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_user = response['user']
            print(f"   Admin User: {self.admin_user['id']}")

        # User login
        success, response = self.run_test(
            "User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.user_token = response['token']
            self.regular_user = response['user']
            print(f"   Regular User: {self.regular_user['id']}")

        return self.admin_user and self.regular_user

    def test_order_management_comprehensive(self):
        """Comprehensive order management test"""
        print("\n🛒 COMPREHENSIVE ORDER MANAGEMENT TESTING")
        print("=" * 60)
        
        if not self.setup_users():
            print("❌ Failed to setup users")
            return False

        # Test 1: Create test listing
        print("\n1️⃣ Creating test listing...")
        test_listing = {
            "title": "Order Test - Premium Headphones",
            "description": "High-quality wireless headphones for order testing.",
            "price": 299.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],  # Admin is seller
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"]
        }
        
        success_create, create_response = self.run_test(
            "Create Test Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_create:
            print("❌ Cannot proceed without test listing")
            return False
        
        test_listing_id = create_response['listing_id']
        print(f"   ✅ Created listing: {test_listing_id}")

        # Test 2: Create buy request
        print("\n2️⃣ Testing buy request creation...")
        order_data = {
            "listing_id": test_listing_id,
            "buyer_id": self.regular_user['id']
        }
        
        success_order, order_response = self.run_test(
            "Create Buy Request",
            "POST",
            "api/orders/create",
            200,
            data=order_data
        )
        
        if not success_order:
            print("❌ Cannot proceed without order")
            return False
        
        test_order_id = order_response['order_id']
        print(f"   ✅ Created order: {test_order_id}")
        print(f"   ⏰ Expires: {order_response.get('expires_at')}")

        # Test 3: Test duplicate request (should fail)
        print("\n3️⃣ Testing duplicate request rejection...")
        success_dup, dup_response = self.run_test(
            "Duplicate Request (Should Fail)",
            "POST",
            "api/orders/create",
            409,
            data=order_data
        )

        # Test 4: Test own listing purchase (should fail)
        print("\n4️⃣ Testing own listing purchase rejection...")
        own_order_data = {
            "listing_id": test_listing_id,
            "buyer_id": self.admin_user['id']  # Admin trying to buy own listing
        }
        
        success_own, own_response = self.run_test(
            "Own Listing Purchase (Should Fail)",
            "POST",
            "api/orders/create",
            400,
            data=own_order_data
        )

        # Test 5: Get seller orders
        print("\n5️⃣ Testing seller orders retrieval...")
        success_seller, seller_response = self.run_test(
            "Get Seller Orders",
            "GET",
            f"api/orders/seller/{self.admin_user['id']}",
            200
        )
        
        if success_seller:
            print(f"   📋 Found {len(seller_response)} seller orders")
            if seller_response:
                order = seller_response[0]
                print(f"   📦 Order: {order.get('listing', {}).get('title', 'N/A')}")
                print(f"   👤 Buyer: {order.get('buyer', {}).get('username', 'N/A')}")

        # Test 6: Get buyer orders
        print("\n6️⃣ Testing buyer orders retrieval...")
        success_buyer, buyer_response = self.run_test(
            "Get Buyer Orders",
            "GET",
            f"api/orders/buyer/{self.regular_user['id']}",
            200
        )
        
        if success_buyer:
            print(f"   📋 Found {len(buyer_response)} buyer orders")
            if buyer_response:
                order = buyer_response[0]
                print(f"   📦 Order: {order.get('listing', {}).get('title', 'N/A')}")
                print(f"   👤 Seller: {order.get('seller', {}).get('username', 'N/A')}")
                print(f"   📧 Contact hidden: {not order.get('seller', {}).get('email', '')}")

        # Test 7: Approve order
        print("\n7️⃣ Testing order approval...")
        approval_data = {
            "seller_id": self.admin_user['id']
        }
        
        success_approve, approve_response = self.run_test(
            "Approve Order",
            "PUT",
            f"api/orders/{test_order_id}/approve",
            200,
            data=approval_data
        )
        
        if success_approve:
            print("   ✅ Order approved successfully")
            
            # Check listing status
            success_listing, listing_response = self.run_test(
                "Check Listing Status",
                "GET",
                f"api/listings/{test_listing_id}",
                200
            )
            
            if success_listing:
                status = listing_response.get('status')
                print(f"   📋 Listing status: {status}")
                if status == 'sold':
                    self.log_test("Listing Marked as Sold", True, "Status correctly updated")
                else:
                    self.log_test("Listing Marked as Sold", False, f"Status is {status}, expected 'sold'")

        # Test 8: Check notifications
        print("\n8️⃣ Testing notifications...")
        
        # Seller notifications
        success_seller_notif, seller_notif_response = self.run_test(
            "Check Seller Notifications",
            "GET",
            f"api/user/notifications/{self.admin_user['id']}",
            200
        )
        
        if success_seller_notif:
            buy_requests = [n for n in seller_notif_response if n.get('type') == 'buy_request']
            print(f"   📧 Seller notifications: {len(buy_requests)} buy requests")

        # Buyer notifications
        success_buyer_notif, buyer_notif_response = self.run_test(
            "Check Buyer Notifications",
            "GET",
            f"api/user/notifications/{self.regular_user['id']}",
            200
        )
        
        if success_buyer_notif:
            approvals = [n for n in buyer_notif_response if n.get('type') == 'buy_approved']
            print(f"   📧 Buyer notifications: {len(approvals)} approvals")

        # Test 9: Test cleanup
        print("\n9️⃣ Testing expired order cleanup...")
        success_cleanup, cleanup_response = self.run_test(
            "Cleanup Expired Orders",
            "POST",
            "api/orders/cleanup-expired",
            200
        )
        
        if success_cleanup:
            print(f"   🧹 Cleanup result: {cleanup_response.get('message', 'Success')}")

        # Cleanup
        print("\n🧹 Cleaning up test data...")
        self.run_test(
            "Delete Test Listing",
            "DELETE",
            f"api/listings/{test_listing_id}",
            200
        )

        # Summary
        print(f"\n📊 Order Management Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = OrderManagementTester()
    success = tester.test_order_management_comprehensive()
    
    if success:
        print("\n🎉 ALL ORDER MANAGEMENT TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️ {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())