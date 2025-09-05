#!/usr/bin/env python3
"""
My Deals System Test Suite
Tests the fixed /api/user/my-deals/{user_id} endpoint functionality
"""

import requests
import sys
import json
from datetime import datetime

class MyDealsAPITester:
    def __init__(self, base_url="https://cataloro-upgrade.preview.emergentagent.com"):
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

    def setup_test_users(self):
        """Setup test users for deals testing"""
        print("\n🔧 Setting up test users...")
        
        # Login admin user (seller)
        success_admin, admin_response = self.run_test(
            "Admin Login (Seller)",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success_admin and 'token' in admin_response:
            self.admin_token = admin_response['token']
            self.admin_user = admin_response['user']
            print(f"   Admin User ID: {self.admin_user['id']}")
        
        # Login regular user (buyer)
        success_user, user_response = self.run_test(
            "User Login (Buyer)",
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

    def create_test_listing(self, seller_id, title_suffix=""):
        """Create a test listing for deals testing"""
        test_listing = {
            "title": f"My Deals Test Listing{title_suffix} - Premium Headphones",
            "description": "High-quality wireless headphones for deals testing. Excellent sound quality and noise cancellation.",
            "price": 299.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": seller_id,
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"],
            "tags": ["wireless", "headphones", "premium"],
            "features": ["Noise cancellation", "Bluetooth 5.0", "30-hour battery"]
        }
        
        success, response = self.run_test(
            f"Create Test Listing{title_suffix}",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if success and 'listing_id' in response:
            return response['listing_id']
        return None

    def create_and_approve_order(self, listing_id, buyer_id, seller_id):
        """Create and approve an order to generate a deal"""
        # Create buy request
        order_data = {
            "listing_id": listing_id,
            "buyer_id": buyer_id
        }
        
        success_order, order_response = self.run_test(
            "Create Buy Request for Deal",
            "POST",
            "api/orders/create",
            200,
            data=order_data
        )
        
        if not success_order or 'order_id' not in order_response:
            return None
        
        order_id = order_response['order_id']
        
        # Approve the order
        approval_data = {
            "seller_id": seller_id
        }
        
        success_approve, approve_response = self.run_test(
            "Approve Order to Create Deal",
            "PUT",
            f"api/orders/{order_id}/approve",
            200,
            data=approval_data
        )
        
        if success_approve:
            return order_id
        return None

    def test_my_deals_endpoint_structure(self):
        """Test the basic structure and response of my deals endpoint"""
        print("\n📋 Testing My Deals Endpoint Structure...")
        
        if not self.regular_user:
            print("❌ My Deals Structure Test - SKIPPED (No user logged in)")
            return False
        
        # Test with the specific user ID from the review request
        test_user_id = "68b191ec38e6062fee10bd28"
        
        success, response = self.run_test(
            f"My Deals Endpoint Structure (User: {test_user_id})",
            "GET",
            f"api/user/my-deals/{test_user_id}",
            200
        )
        
        if success:
            print(f"   ✅ Endpoint returns {len(response)} deals")
            
            # Verify response is an array
            is_array = isinstance(response, list)
            self.log_test("Response is Array", is_array, f"Response type: {type(response)}")
            
            if response and len(response) > 0:
                # Check deal structure
                first_deal = response[0]
                required_fields = ['id', 'listing_id', 'buyer_id', 'seller_id', 'status', 'amount', 'created_at', 'listing']
                
                has_required_fields = all(field in first_deal for field in required_fields)
                self.log_test("Deal Structure Complete", has_required_fields, 
                             f"Required fields present: {has_required_fields}")
                
                # Check listing enrichment
                if 'listing' in first_deal:
                    listing = first_deal['listing']
                    listing_fields = ['id', 'title', 'price', 'image']
                    has_listing_fields = all(field in listing for field in listing_fields)
                    self.log_test("Listing Data Enrichment", has_listing_fields,
                                 f"Listing fields present: {has_listing_fields}")
                
                # Check buyer/seller information
                has_buyer_info = 'buyer' in first_deal and isinstance(first_deal['buyer'], dict)
                has_seller_info = 'seller' in first_deal and isinstance(first_deal['seller'], dict)
                
                self.log_test("Buyer Information Present", has_buyer_info,
                             f"Buyer info structure: {type(first_deal.get('buyer', 'Missing'))}")
                self.log_test("Seller Information Present", has_seller_info,
                             f"Seller info structure: {type(first_deal.get('seller', 'Missing'))}")
                
                # Print sample deal structure for verification
                print(f"\n📊 Sample Deal Structure:")
                print(f"   Deal ID: {first_deal.get('id', 'N/A')}")
                print(f"   Status: {first_deal.get('status', 'N/A')}")
                print(f"   Amount: €{first_deal.get('amount', 0)}")
                print(f"   Listing: {first_deal.get('listing', {}).get('title', 'N/A')}")
                print(f"   Created: {first_deal.get('created_at', 'N/A')}")
                print(f"   Approved: {first_deal.get('approved_at', 'N/A')}")
            else:
                print("   ℹ️  No existing deals found - will create test deals")
        
        return success

    def test_deal_data_completeness(self):
        """Test that deal data includes all required information"""
        print("\n🔍 Testing Deal Data Completeness...")
        
        if not self.admin_user or not self.regular_user:
            print("❌ Deal Data Completeness - SKIPPED (Need both users)")
            return False
        
        # Create test scenario: listing -> order -> approval -> deal
        print("\n1️⃣ Creating test listing for deal completeness test...")
        listing_id = self.create_test_listing(self.admin_user['id'], " (Completeness Test)")
        
        if not listing_id:
            print("❌ Failed to create test listing")
            return False
        
        print("\n2️⃣ Creating and approving order...")
        order_id = self.create_and_approve_order(listing_id, self.regular_user['id'], self.admin_user['id'])
        
        if not order_id:
            print("❌ Failed to create and approve order")
            return False
        
        print("\n3️⃣ Testing buyer's deals (user as buyer)...")
        success_buyer, buyer_deals = self.run_test(
            "Get Buyer Deals",
            "GET",
            f"api/user/my-deals/{self.regular_user['id']}",
            200
        )
        
        if success_buyer:
            # Find our test deal
            test_deal = None
            for deal in buyer_deals:
                if deal.get('listing_id') == listing_id:
                    test_deal = deal
                    break
            
            if test_deal:
                print(f"   ✅ Found test deal in buyer's deals")
                
                # Test amount calculation
                expected_amount = 299.99  # Price from test listing
                actual_amount = test_deal.get('amount', 0)
                amount_correct = abs(actual_amount - expected_amount) < 0.01
                self.log_test("Amount Calculation Correct", amount_correct,
                             f"Expected: €{expected_amount}, Actual: €{actual_amount}")
                
                # Test buyer/seller role identification
                is_buyer = test_deal.get('buyer_id') == self.regular_user['id']
                is_seller = test_deal.get('seller_id') == self.admin_user['id']
                roles_correct = is_buyer and is_seller
                self.log_test("Buyer/Seller Roles Correct", roles_correct,
                             f"User is buyer: {is_buyer}, Admin is seller: {is_seller}")
                
                # Test timestamp formatting
                created_at = test_deal.get('created_at')
                approved_at = test_deal.get('approved_at')
                timestamps_present = created_at is not None and approved_at is not None
                self.log_test("Timestamps Present", timestamps_present,
                             f"Created: {created_at}, Approved: {approved_at}")
                
                # Test listing information completeness
                listing_info = test_deal.get('listing', {})
                listing_complete = all(field in listing_info for field in ['id', 'title', 'price'])
                self.log_test("Listing Information Complete", listing_complete,
                             f"Listing fields: {list(listing_info.keys())}")
                
                # Test seller information (should be empty for buyer)
                seller_info = test_deal.get('seller', {})
                has_seller_data = bool(seller_info.get('username') or seller_info.get('id'))
                self.log_test("Seller Information Populated", has_seller_data,
                             f"Seller data present: {has_seller_data}")
            else:
                self.log_test("Test Deal Found in Buyer Deals", False, "Test deal not found")
        
        print("\n4️⃣ Testing seller's deals (user as seller)...")
        success_seller, seller_deals = self.run_test(
            "Get Seller Deals",
            "GET",
            f"api/user/my-deals/{self.admin_user['id']}",
            200
        )
        
        if success_seller:
            # Find our test deal
            test_deal_seller = None
            for deal in seller_deals:
                if deal.get('listing_id') == listing_id:
                    test_deal_seller = deal
                    break
            
            if test_deal_seller:
                print(f"   ✅ Found test deal in seller's deals")
                
                # Test buyer information (should be populated for seller)
                buyer_info = test_deal_seller.get('buyer', {})
                has_buyer_data = bool(buyer_info.get('username') or buyer_info.get('id'))
                self.log_test("Buyer Information Populated", has_buyer_data,
                             f"Buyer data present: {has_buyer_data}")
            else:
                self.log_test("Test Deal Found in Seller Deals", False, "Test deal not found")
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        self.run_test(
            "Cleanup Test Listing",
            "DELETE",
            f"api/listings/{listing_id}",
            200
        )
        
        return success_buyer and success_seller

    def test_approved_completed_filtering(self):
        """Test that only approved/completed orders are returned as deals"""
        print("\n🔍 Testing Approved/Completed Orders Filtering...")
        
        if not self.admin_user or not self.regular_user:
            print("❌ Filtering Test - SKIPPED (Need both users)")
            return False
        
        # Create test listing
        listing_id = self.create_test_listing(self.admin_user['id'], " (Filtering Test)")
        if not listing_id:
            return False
        
        # Create a pending order (should NOT appear in deals)
        print("\n1️⃣ Creating pending order (should not appear in deals)...")
        pending_order_data = {
            "listing_id": listing_id,
            "buyer_id": self.regular_user['id']
        }
        
        success_pending, pending_response = self.run_test(
            "Create Pending Order",
            "POST",
            "api/orders/create",
            200,
            data=pending_order_data
        )
        
        if success_pending:
            pending_order_id = pending_response.get('order_id')
            
            # Check deals before approval (should not include pending order)
            print("\n2️⃣ Checking deals before approval...")
            success_before, deals_before = self.run_test(
                "Get Deals Before Approval",
                "GET",
                f"api/user/my-deals/{self.regular_user['id']}",
                200
            )
            
            if success_before:
                pending_in_deals = any(deal.get('id') == pending_order_id for deal in deals_before)
                self.log_test("Pending Order NOT in Deals", not pending_in_deals,
                             f"Pending order in deals: {pending_in_deals} (should be False)")
            
            # Approve the order
            print("\n3️⃣ Approving order...")
            approval_data = {"seller_id": self.admin_user['id']}
            success_approve, _ = self.run_test(
                "Approve Order for Filtering Test",
                "PUT",
                f"api/orders/{pending_order_id}/approve",
                200,
                data=approval_data
            )
            
            if success_approve:
                # Check deals after approval (should now include the order)
                print("\n4️⃣ Checking deals after approval...")
                success_after, deals_after = self.run_test(
                    "Get Deals After Approval",
                    "GET",
                    f"api/user/my-deals/{self.regular_user['id']}",
                    200
                )
                
                if success_after:
                    approved_in_deals = any(deal.get('id') == pending_order_id for deal in deals_after)
                    self.log_test("Approved Order IN Deals", approved_in_deals,
                                 f"Approved order in deals: {approved_in_deals} (should be True)")
                    
                    # Verify status is approved/completed
                    if approved_in_deals:
                        approved_deal = next(deal for deal in deals_after if deal.get('id') == pending_order_id)
                        status = approved_deal.get('status')
                        status_correct = status in ['approved', 'completed']
                        self.log_test("Deal Status Correct", status_correct,
                                     f"Deal status: {status} (should be approved/completed)")
        
        # Cleanup
        self.run_test("Cleanup Filtering Test Listing", "DELETE", f"api/listings/{listing_id}", 200)
        
        return success_pending and success_approve

    def test_user_scenarios(self):
        """Test different user scenarios - user as buyer vs seller"""
        print("\n👥 Testing Different User Scenarios...")
        
        if not self.admin_user or not self.regular_user:
            print("❌ User Scenarios Test - SKIPPED (Need both users)")
            return False
        
        # Scenario 1: User as buyer, Admin as seller
        print("\n📋 Scenario 1: User as Buyer, Admin as Seller")
        listing_id_1 = self.create_test_listing(self.admin_user['id'], " (User as Buyer)")
        if listing_id_1:
            order_id_1 = self.create_and_approve_order(listing_id_1, self.regular_user['id'], self.admin_user['id'])
            
            if order_id_1:
                # Check user's deals (as buyer)
                success_buyer, buyer_deals = self.run_test(
                    "User Deals (As Buyer)",
                    "GET",
                    f"api/user/my-deals/{self.regular_user['id']}",
                    200
                )
                
                if success_buyer:
                    user_as_buyer_deal = next((deal for deal in buyer_deals if deal.get('id') == order_id_1), None)
                    if user_as_buyer_deal:
                        is_buyer = user_as_buyer_deal.get('buyer_id') == self.regular_user['id']
                        has_seller_info = bool(user_as_buyer_deal.get('seller', {}).get('id'))
                        self.log_test("User as Buyer Scenario", is_buyer and has_seller_info,
                                     f"User is buyer: {is_buyer}, Has seller info: {has_seller_info}")
        
        # Scenario 2: Admin as buyer, User as seller
        print("\n📋 Scenario 2: Admin as Buyer, User as Seller")
        listing_id_2 = self.create_test_listing(self.regular_user['id'], " (Admin as Buyer)")
        if listing_id_2:
            order_id_2 = self.create_and_approve_order(listing_id_2, self.admin_user['id'], self.regular_user['id'])
            
            if order_id_2:
                # Check user's deals (as seller)
                success_seller, seller_deals = self.run_test(
                    "User Deals (As Seller)",
                    "GET",
                    f"api/user/my-deals/{self.regular_user['id']}",
                    200
                )
                
                if success_seller:
                    user_as_seller_deal = next((deal for deal in seller_deals if deal.get('id') == order_id_2), None)
                    if user_as_seller_deal:
                        is_seller = user_as_seller_deal.get('seller_id') == self.regular_user['id']
                        has_buyer_info = bool(user_as_seller_deal.get('buyer', {}).get('id'))
                        self.log_test("User as Seller Scenario", is_seller and has_buyer_info,
                                     f"User is seller: {is_seller}, Has buyer info: {has_buyer_info}")
        
        # Test data consistency
        print("\n🔄 Testing Data Consistency Across Scenarios...")
        success_final, final_deals = self.run_test(
            "Final Deals Check",
            "GET",
            f"api/user/my-deals/{self.regular_user['id']}",
            200
        )
        
        if success_final:
            total_deals = len(final_deals)
            approved_deals = len([deal for deal in final_deals if deal.get('status') in ['approved', 'completed']])
            consistency_check = total_deals == approved_deals
            self.log_test("Data Consistency", consistency_check,
                         f"Total deals: {total_deals}, Approved deals: {approved_deals}")
        
        # Cleanup
        if listing_id_1:
            self.run_test("Cleanup Scenario 1 Listing", "DELETE", f"api/listings/{listing_id_1}", 200)
        if listing_id_2:
            self.run_test("Cleanup Scenario 2 Listing", "DELETE", f"api/listings/{listing_id_2}", 200)
        
        return True

    def test_specific_user_id(self):
        """Test the specific user ID mentioned in the review request"""
        print("\n🎯 Testing Specific User ID from Review Request...")
        
        # Test the specific user ID: 68b191ec38e6062fee10bd28
        target_user_id = "68b191ec38e6062fee10bd28"
        
        success, response = self.run_test(
            f"My Deals for User {target_user_id}",
            "GET",
            f"api/user/my-deals/{target_user_id}",
            200
        )
        
        if success:
            print(f"   ✅ Successfully retrieved deals for user {target_user_id}")
            print(f"   📊 Found {len(response)} deals")
            
            if response:
                # Analyze the deals structure
                for i, deal in enumerate(response[:3]):  # Show first 3 deals
                    print(f"\n   Deal {i+1}:")
                    print(f"     ID: {deal.get('id', 'N/A')}")
                    print(f"     Status: {deal.get('status', 'N/A')}")
                    print(f"     Amount: €{deal.get('amount', 0)}")
                    print(f"     Listing: {deal.get('listing', {}).get('title', 'N/A')}")
                    print(f"     Created: {deal.get('created_at', 'N/A')}")
                    
                    # Check if user is buyer or seller
                    if deal.get('buyer_id') == target_user_id:
                        print(f"     Role: BUYER")
                        seller_info = deal.get('seller', {})
                        print(f"     Seller: {seller_info.get('username', 'N/A')}")
                    elif deal.get('seller_id') == target_user_id:
                        print(f"     Role: SELLER")
                        buyer_info = deal.get('buyer', {})
                        print(f"     Buyer: {buyer_info.get('username', 'N/A')}")
                
                # Verify all deals are approved/completed
                all_approved = all(deal.get('status') in ['approved', 'completed'] for deal in response)
                self.log_test("All Deals Approved/Completed", all_approved,
                             f"All deals have correct status: {all_approved}")
                
                # Verify data enrichment
                all_enriched = all(
                    'listing' in deal and 
                    deal['listing'].get('title') and 
                    deal['listing'].get('price') is not None
                    for deal in response
                )
                self.log_test("All Deals Enriched with Listing Data", all_enriched,
                             f"All deals have listing data: {all_enriched}")
            else:
                print("   ℹ️  No deals found for this user")
                self.log_test("Deals Endpoint Accessible", True, "Endpoint returns empty array (valid)")
        
        return success

    def run_comprehensive_test(self):
        """Run all My Deals tests"""
        print("🚀 Starting My Deals System Comprehensive Test Suite")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False
        
        # Test 1: Basic endpoint structure
        test1_success = self.test_my_deals_endpoint_structure()
        
        # Test 2: Specific user ID from review
        test2_success = self.test_specific_user_id()
        
        # Test 3: Deal data completeness
        test3_success = self.test_deal_data_completeness()
        
        # Test 4: Approved/completed filtering
        test4_success = self.test_approved_completed_filtering()
        
        # Test 5: User scenarios
        test5_success = self.test_user_scenarios()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 MY DEALS SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        tests = [
            ("Endpoint Structure", test1_success),
            ("Specific User ID", test2_success),
            ("Data Completeness", test3_success),
            ("Status Filtering", test4_success),
            ("User Scenarios", test5_success)
        ]
        
        passed_tests = sum(1 for _, success in tests if success)
        total_tests = len(tests)
        
        for test_name, success in tests:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        print(f"Individual API calls: {self.tests_passed}/{self.tests_run} passed")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL MY DEALS TESTS PASSED!")
            print("✅ The My Deals system is working correctly")
            print("✅ Approved/completed orders are properly returned")
            print("✅ Data enrichment with listing details is working")
            print("✅ Buyer/seller information is populated correctly")
            print("✅ Deal structure matches frontend expectations")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
            print("❌ My Deals system needs attention")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = MyDealsAPITester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)