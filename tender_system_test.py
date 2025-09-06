#!/usr/bin/env python3
"""
Cataloro Marketplace Tender/Bidding System Test Suite
Tests all tender/bidding API endpoints for functionality and integration
"""

import requests
import sys
import json
from datetime import datetime
import time

class TenderSystemTester:
    def __init__(self, base_url="https://cataloro-marketplace-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_user = None
        self.regular_user = None
        self.test_listing_id = None
        self.test_tender_ids = []
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

    def setup_test_users(self):
        """Setup test users for tender testing"""
        print("\n🔧 Setting up test users...")
        
        # Login admin user
        success_admin, admin_response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success_admin and 'user' in admin_response:
            self.admin_user = admin_response['user']
            print(f"   Admin User ID: {self.admin_user['id']}")
        
        # Login regular user
        success_user, user_response = self.run_test(
            "Regular User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        
        if success_user and 'user' in user_response:
            self.regular_user = user_response['user']
            print(f"   Regular User ID: {self.regular_user['id']}")
        
        return success_admin and success_user

    def create_test_listing(self):
        """Create a test listing for tender testing"""
        print("\n📝 Creating test listing for tender system...")
        
        if not self.admin_user:
            print("❌ Cannot create listing - no admin user")
            return False
        
        test_listing = {
            "title": "Tender Test Listing - Premium Gaming Laptop",
            "description": "High-performance gaming laptop for tender system testing. RTX 4080, 32GB RAM, 1TB SSD. Perfect for competitive gaming and content creation.",
            "price": 2500.00,  # Starting price
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400"],
            "tags": ["gaming", "laptop", "RTX", "high-performance"],
            "features": ["RTX 4080 GPU", "32GB DDR5 RAM", "1TB NVMe SSD", "144Hz Display"]
        }
        
        success, response = self.run_test(
            "Create Test Listing for Tenders",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if success and 'listing_id' in response:
            self.test_listing_id = response['listing_id']
            print(f"   ✅ Created test listing with ID: {self.test_listing_id}")
            return True
        
        return False

    def test_submit_tender_validation(self):
        """Test tender submission with various validation scenarios"""
        print("\n1️⃣ Testing Tender Submission Validation...")
        
        if not self.regular_user or not self.test_listing_id:
            print("❌ Cannot test tender submission - missing prerequisites")
            return False
        
        # Test 1: Valid tender submission
        tender_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.regular_user['id'],
            "offer_amount": 2600.00  # Above starting price
        }
        
        success, response = self.run_test(
            "Submit Valid Tender",
            "POST",
            "api/tenders/submit",
            200,
            data=tender_data
        )
        
        if success and 'tender_id' in response:
            self.test_tender_ids.append(response['tender_id'])
            print(f"   ✅ Created tender with ID: {response['tender_id']}")
            print(f"   💰 Minimum next bid: €{response.get('minimum_next_bid', 'N/A')}")
        
        # Test 2: Tender below minimum bid (should fail)
        low_tender_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.regular_user['id'],
            "offer_amount": 2550.00  # Below current highest bid
        }
        
        success_low, _ = self.run_test(
            "Submit Tender Below Minimum (Should Fail)",
            "POST",
            "api/tenders/submit",
            400,  # Expecting 400 Bad Request
            data=low_tender_data
        )
        
        # Test 3: Self-bidding (should fail)
        self_bid_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.admin_user['id'],  # Admin is the seller
            "offer_amount": 2700.00
        }
        
        success_self, _ = self.run_test(
            "Submit Self-Bid (Should Fail)",
            "POST",
            "api/tenders/submit",
            400,  # Expecting 400 Bad Request
            data=self_bid_data
        )
        
        # Test 4: Missing required fields
        invalid_tender_data = {
            "listing_id": self.test_listing_id,
            # Missing buyer_id and offer_amount
        }
        
        success_invalid, _ = self.run_test(
            "Submit Invalid Tender (Missing Fields)",
            "POST",
            "api/tenders/submit",
            400,  # Expecting 400 Bad Request
            data=invalid_tender_data
        )
        
        # Test 5: Non-existent listing
        nonexistent_tender_data = {
            "listing_id": "non-existent-listing-id",
            "buyer_id": self.regular_user['id'],
            "offer_amount": 2600.00
        }
        
        success_nonexistent, _ = self.run_test(
            "Submit Tender for Non-existent Listing",
            "POST",
            "api/tenders/submit",
            404,  # Expecting 404 Not Found
            data=nonexistent_tender_data
        )
        
        validation_tests = [success, success_low, success_self, success_invalid, success_nonexistent]
        passed_validation = sum(validation_tests)
        
        print(f"\n📊 Tender Validation Tests: {passed_validation}/{len(validation_tests)} passed")
        return passed_validation == len(validation_tests)

    def test_multiple_tender_submissions(self):
        """Test multiple tender submissions to verify bidding logic"""
        print("\n2️⃣ Testing Multiple Tender Submissions...")
        
        if not self.regular_user or not self.test_listing_id:
            print("❌ Cannot test multiple tenders - missing prerequisites")
            return False
        
        # Create a second user for bidding competition
        second_user_data = {
            "username": "tender_bidder_2",
            "email": "bidder2@cataloro.com",
            "full_name": "Tender Bidder 2",
            "password": "demo123"
        }
        
        success_register, register_response = self.run_test(
            "Register Second Bidder",
            "POST",
            "api/auth/register",
            200,
            data=second_user_data
        )
        
        if not success_register:
            print("   ⚠️ Could not create second user, using existing user for testing")
            # Try to login with existing credentials
            success_login, login_response = self.run_test(
                "Login Second Bidder",
                "POST",
                "api/auth/login",
                200,
                data={"email": "bidder2@cataloro.com", "password": "demo123"}
            )
            if success_login:
                second_user_id = login_response['user']['id']
            else:
                print("❌ Cannot proceed with multiple tender testing")
                return False
        else:
            second_user_id = register_response['user_id']
        
        # Submit higher bid from second user
        higher_tender_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": second_user_id,
            "offer_amount": 2750.00  # Higher than previous bid
        }
        
        success_higher, higher_response = self.run_test(
            "Submit Higher Tender from Second User",
            "POST",
            "api/tenders/submit",
            200,
            data=higher_tender_data
        )
        
        if success_higher and 'tender_id' in higher_response:
            self.test_tender_ids.append(higher_response['tender_id'])
            print(f"   ✅ Second tender ID: {higher_response['tender_id']}")
        
        # Submit even higher bid from first user
        highest_tender_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.regular_user['id'],
            "offer_amount": 2900.00  # Highest bid
        }
        
        success_highest, highest_response = self.run_test(
            "Submit Highest Tender from First User",
            "POST",
            "api/tenders/submit",
            200,
            data=highest_tender_data
        )
        
        if success_highest and 'tender_id' in highest_response:
            self.test_tender_ids.append(highest_response['tender_id'])
            print(f"   ✅ Highest tender ID: {highest_response['tender_id']}")
        
        multiple_tests = [success_higher, success_highest]
        passed_multiple = sum(multiple_tests)
        
        print(f"\n📊 Multiple Tender Tests: {passed_multiple}/{len(multiple_tests)} passed")
        return passed_multiple == len(multiple_tests)

    def test_get_listing_tenders(self):
        """Test GET /api/tenders/listing/{listing_id} endpoint"""
        print("\n3️⃣ Testing Get Listing Tenders...")
        
        if not self.test_listing_id:
            print("❌ Cannot test listing tenders - no test listing")
            return False
        
        success, response = self.run_test(
            "Get All Tenders for Listing",
            "GET",
            f"api/tenders/listing/{self.test_listing_id}",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(response)} active tenders for listing")
            
            # Verify tender data structure
            if response:
                tender = response[0]  # Highest bid should be first
                required_fields = ['id', 'offer_amount', 'status', 'created_at', 'buyer']
                has_required_fields = all(field in tender for field in required_fields)
                
                self.log_test("Tender Data Structure Complete", has_required_fields,
                             f"Required fields present: {has_required_fields}")
                
                if has_required_fields:
                    print(f"   💰 Highest offer: €{tender['offer_amount']}")
                    print(f"   👤 Buyer: {tender['buyer'].get('username', 'Unknown')}")
                    print(f"   📅 Created: {tender['created_at']}")
                
                # Verify tenders are sorted by amount (highest first)
                if len(response) > 1:
                    amounts = [t['offer_amount'] for t in response]
                    is_sorted = amounts == sorted(amounts, reverse=True)
                    self.log_test("Tenders Sorted by Amount", is_sorted,
                                 f"Amounts sorted correctly: {is_sorted}")
        
        return success

    def test_get_buyer_tenders(self):
        """Test GET /api/tenders/buyer/{buyer_id} endpoint"""
        print("\n4️⃣ Testing Get Buyer Tenders...")
        
        if not self.regular_user:
            print("❌ Cannot test buyer tenders - no regular user")
            return False
        
        success, response = self.run_test(
            "Get Buyer's Submitted Tenders",
            "GET",
            f"api/tenders/buyer/{self.regular_user['id']}",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(response)} tenders submitted by buyer")
            
            # Verify tender data structure with listing information
            if response:
                tender = response[0]
                required_fields = ['id', 'offer_amount', 'status', 'created_at', 'listing']
                has_required_fields = all(field in tender for field in required_fields)
                
                self.log_test("Buyer Tender Data Structure", has_required_fields,
                             f"Required fields present: {has_required_fields}")
                
                if has_required_fields and 'listing' in tender:
                    listing = tender['listing']
                    listing_fields = ['id', 'title', 'price', 'images']
                    has_listing_fields = all(field in listing for field in listing_fields)
                    
                    self.log_test("Listing Data Enrichment", has_listing_fields,
                                 f"Listing fields present: {has_listing_fields}")
                    
                    if has_listing_fields:
                        print(f"   📦 Listing: {listing['title']}")
                        print(f"   💰 Offer: €{tender['offer_amount']} (vs listing price €{listing['price']})")
                        print(f"   📊 Status: {tender['status']}")
        
        return success

    def test_tender_acceptance_workflow(self):
        """Test tender acceptance workflow and notifications"""
        print("\n5️⃣ Testing Tender Acceptance Workflow...")
        
        if not self.admin_user or not self.test_tender_ids:
            print("❌ Cannot test acceptance - missing admin user or tender IDs")
            return False
        
        # Get the highest tender to accept
        success_get, tenders_response = self.run_test(
            "Get Tenders for Acceptance",
            "GET",
            f"api/tenders/listing/{self.test_listing_id}",
            200
        )
        
        if not success_get or not tenders_response:
            print("❌ Cannot get tenders for acceptance")
            return False
        
        # Accept the highest tender
        highest_tender = tenders_response[0]  # Should be sorted by amount
        tender_id = highest_tender['id']
        
        acceptance_data = {
            "seller_id": self.admin_user['id']
        }
        
        success_accept, accept_response = self.run_test(
            "Accept Highest Tender",
            "PUT",
            f"api/tenders/{tender_id}/accept",
            200,
            data=acceptance_data
        )
        
        if success_accept:
            print(f"   ✅ Accepted tender {tender_id}")
            
            # Verify listing status changed to sold
            success_listing, listing_response = self.run_test(
                "Verify Listing Marked as Sold",
                "GET",
                f"api/listings/{self.test_listing_id}",
                200
            )
            
            if success_listing:
                listing_status = listing_response.get('status')
                is_sold = listing_status == 'sold'
                self.log_test("Listing Status Updated to Sold", is_sold,
                             f"Status: {listing_status} (expected: sold)")
                
                if is_sold:
                    sold_price = listing_response.get('sold_price')
                    print(f"   💰 Sold price: €{sold_price}")
            
            # Verify other tenders were rejected
            success_check, check_response = self.run_test(
                "Check Other Tenders Rejected",
                "GET",
                f"api/tenders/listing/{self.test_listing_id}",
                200
            )
            
            if success_check:
                active_tenders = [t for t in check_response if t['status'] == 'active']
                rejected_tenders = [t for t in check_response if t['status'] == 'rejected']
                accepted_tenders = [t for t in check_response if t['status'] == 'accepted']
                
                self.log_test("Other Tenders Auto-Rejected", len(active_tenders) == 0,
                             f"Active: {len(active_tenders)}, Rejected: {len(rejected_tenders)}, Accepted: {len(accepted_tenders)}")
        
        return success_accept

    def test_tender_rejection_workflow(self):
        """Test tender rejection workflow"""
        print("\n6️⃣ Testing Tender Rejection Workflow...")
        
        # Create a new listing for rejection testing
        reject_test_listing = {
            "title": "Rejection Test Listing - Wireless Headphones",
            "description": "Premium wireless headphones for rejection testing.",
            "price": 300.00,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"]
        }
        
        success_listing, listing_response = self.run_test(
            "Create Listing for Rejection Test",
            "POST",
            "api/listings",
            200,
            data=reject_test_listing
        )
        
        if not success_listing:
            print("❌ Cannot create listing for rejection test")
            return False
        
        reject_listing_id = listing_response['listing_id']
        
        # Submit tender for rejection
        reject_tender_data = {
            "listing_id": reject_listing_id,
            "buyer_id": self.regular_user['id'],
            "offer_amount": 350.00
        }
        
        success_tender, tender_response = self.run_test(
            "Submit Tender for Rejection Test",
            "POST",
            "api/tenders/submit",
            200,
            data=reject_tender_data
        )
        
        if not success_tender:
            print("❌ Cannot create tender for rejection test")
            return False
        
        reject_tender_id = tender_response['tender_id']
        
        # Reject the tender
        rejection_data = {
            "seller_id": self.admin_user['id']
        }
        
        success_reject, reject_response = self.run_test(
            "Reject Tender",
            "PUT",
            f"api/tenders/{reject_tender_id}/reject",
            200,
            data=rejection_data
        )
        
        if success_reject:
            print(f"   ✅ Rejected tender {reject_tender_id}")
            
            # Verify listing is still active
            success_check, check_response = self.run_test(
                "Verify Listing Still Active After Rejection",
                "GET",
                f"api/listings/{reject_listing_id}",
                200
            )
            
            if success_check:
                listing_status = check_response.get('status')
                is_active = listing_status == 'active'
                self.log_test("Listing Remains Active After Rejection", is_active,
                             f"Status: {listing_status} (expected: active)")
        
        # Cleanup
        self.run_test(
            "Cleanup Rejection Test Listing",
            "DELETE",
            f"api/listings/{reject_listing_id}",
            200
        )
        
        return success_reject

    def test_seller_tender_overview(self):
        """Test GET /api/tenders/seller/{seller_id}/overview endpoint"""
        print("\n7️⃣ Testing Seller Tender Overview...")
        
        if not self.admin_user:
            print("❌ Cannot test seller overview - no admin user")
            return False
        
        success, response = self.run_test(
            "Get Seller Tender Overview",
            "GET",
            f"api/tenders/seller/{self.admin_user['id']}/overview",
            200
        )
        
        if success:
            print(f"   ✅ Found overview for {len(response)} listings")
            
            # Verify overview data structure
            if response:
                overview_item = response[0]
                required_fields = ['listing_id', 'listing_title', 'listing_price', 'tender_count', 'highest_offer', 'tenders']
                has_required_fields = all(field in overview_item for field in required_fields)
                
                self.log_test("Overview Data Structure", has_required_fields,
                             f"Required fields present: {has_required_fields}")
                
                if has_required_fields:
                    print(f"   📦 Listing: {overview_item['listing_title']}")
                    print(f"   💰 Starting price: €{overview_item['listing_price']}")
                    print(f"   📊 Tender count: {overview_item['tender_count']}")
                    print(f"   🏆 Highest offer: €{overview_item.get('highest_offer', 0)}")
                    
                    # Verify tender details in overview
                    if overview_item.get('tenders'):
                        tender_details = overview_item['tenders'][0]
                        tender_fields = ['id', 'offer_amount', 'buyer_username', 'created_at']
                        has_tender_fields = all(field in tender_details for field in tender_fields)
                        
                        self.log_test("Tender Details in Overview", has_tender_fields,
                                     f"Tender fields present: {has_tender_fields}")
        
        return success

    def test_notification_integration(self):
        """Test that tender actions create proper notifications"""
        print("\n8️⃣ Testing Notification Integration...")
        
        if not self.admin_user or not self.regular_user:
            print("❌ Cannot test notifications - missing users")
            return False
        
        # Check seller notifications (should have tender offer notifications)
        success_seller, seller_notifications = self.run_test(
            "Check Seller Notifications",
            "GET",
            f"api/user/notifications/{self.admin_user['id']}",
            200
        )
        
        seller_tender_notifications = 0
        if success_seller:
            tender_notifications = [n for n in seller_notifications if n.get('type') == 'tender_offer']
            seller_tender_notifications = len(tender_notifications)
            
            self.log_test("Seller Tender Offer Notifications", seller_tender_notifications > 0,
                         f"Found {seller_tender_notifications} tender offer notifications")
            
            if tender_notifications:
                notification = tender_notifications[0]
                print(f"   📧 Notification: {notification.get('title', 'No title')}")
                print(f"   💬 Message: {notification.get('message', 'No message')[:100]}...")
        
        # Check buyer notifications (should have acceptance/rejection notifications)
        success_buyer, buyer_notifications = self.run_test(
            "Check Buyer Notifications",
            "GET",
            f"api/user/notifications/{self.regular_user['id']}",
            200
        )
        
        buyer_tender_notifications = 0
        if success_buyer:
            tender_notifications = [n for n in buyer_notifications 
                                  if n.get('type') in ['tender_accepted', 'tender_rejected']]
            buyer_tender_notifications = len(tender_notifications)
            
            self.log_test("Buyer Tender Result Notifications", buyer_tender_notifications > 0,
                         f"Found {buyer_tender_notifications} tender result notifications")
            
            if tender_notifications:
                notification = tender_notifications[0]
                print(f"   📧 Notification: {notification.get('title', 'No title')}")
                print(f"   💬 Message: {notification.get('message', 'No message')[:100]}...")
        
        return success_seller and success_buyer

    def test_message_integration(self):
        """Test that tender acceptance creates messages between users"""
        print("\n9️⃣ Testing Message Integration...")
        
        if not self.admin_user or not self.regular_user:
            print("❌ Cannot test messages - missing users")
            return False
        
        # Check if acceptance created a message from seller to buyer
        success_messages, messages_response = self.run_test(
            "Check Messages Between Users",
            "GET",
            f"api/user/{self.regular_user['id']}/messages",
            200
        )
        
        if success_messages:
            # Look for messages related to tender acceptance
            tender_messages = [m for m in messages_response 
                             if 'tender' in m.get('subject', '').lower() or 
                                'accepted' in m.get('content', '').lower()]
            
            self.log_test("Tender Acceptance Messages Created", len(tender_messages) > 0,
                         f"Found {len(tender_messages)} tender-related messages")
            
            if tender_messages:
                message = tender_messages[0]
                print(f"   📧 Subject: {message.get('subject', 'No subject')}")
                print(f"   💬 Content: {message.get('content', 'No content')[:100]}...")
                print(f"   👤 From: {message.get('sender_name', 'Unknown')}")
        
        return success_messages

    def test_error_handling(self):
        """Test error handling for various edge cases"""
        print("\n🔟 Testing Error Handling...")
        
        error_tests = []
        
        # Test 1: Invalid tender ID for acceptance
        success_invalid_accept, _ = self.run_test(
            "Accept Invalid Tender ID",
            "PUT",
            "api/tenders/invalid-tender-id/accept",
            404,
            data={"seller_id": self.admin_user['id'] if self.admin_user else "test"}
        )
        error_tests.append(success_invalid_accept)
        
        # Test 2: Invalid tender ID for rejection
        success_invalid_reject, _ = self.run_test(
            "Reject Invalid Tender ID",
            "PUT",
            "api/tenders/invalid-tender-id/reject",
            404,
            data={"seller_id": self.admin_user['id'] if self.admin_user else "test"}
        )
        error_tests.append(success_invalid_reject)
        
        # Test 3: Invalid listing ID for tenders
        success_invalid_listing, _ = self.run_test(
            "Get Tenders for Invalid Listing",
            "GET",
            "api/tenders/listing/invalid-listing-id",
            200  # Should return empty array, not error
        )
        error_tests.append(success_invalid_listing)
        
        # Test 4: Invalid buyer ID
        success_invalid_buyer, _ = self.run_test(
            "Get Tenders for Invalid Buyer",
            "GET",
            "api/tenders/buyer/invalid-buyer-id",
            200  # Should return empty array, not error
        )
        error_tests.append(success_invalid_buyer)
        
        # Test 5: Invalid seller ID for overview
        success_invalid_seller, _ = self.run_test(
            "Get Overview for Invalid Seller",
            "GET",
            "api/tenders/seller/invalid-seller-id/overview",
            200  # Should return empty array, not error
        )
        error_tests.append(success_invalid_seller)
        
        passed_error_tests = sum(error_tests)
        print(f"\n📊 Error Handling Tests: {passed_error_tests}/{len(error_tests)} passed")
        
        return passed_error_tests == len(error_tests)

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test listing if it exists
        if self.test_listing_id:
            self.run_test(
                "Cleanup Test Listing",
                "DELETE",
                f"api/listings/{self.test_listing_id}",
                200
            )
        
        print("   ✅ Cleanup completed")

    def run_comprehensive_tender_tests(self):
        """Run all tender system tests"""
        print("🎯 TENDER/BIDDING SYSTEM COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False
        
        if not self.create_test_listing():
            print("❌ Failed to create test listing - stopping tests")
            return False
        
        # Run all test suites
        test_results = []
        
        test_results.append(self.test_submit_tender_validation())
        test_results.append(self.test_multiple_tender_submissions())
        test_results.append(self.test_get_listing_tenders())
        test_results.append(self.test_get_buyer_tenders())
        test_results.append(self.test_tender_acceptance_workflow())
        test_results.append(self.test_tender_rejection_workflow())
        test_results.append(self.test_seller_tender_overview())
        test_results.append(self.test_notification_integration())
        test_results.append(self.test_message_integration())
        test_results.append(self.test_error_handling())
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        passed_suites = sum(test_results)
        total_suites = len(test_results)
        
        print(f"\n" + "=" * 60)
        print(f"🎯 TENDER SYSTEM TEST SUMMARY")
        print(f"=" * 60)
        print(f"📊 Test Suites: {passed_suites}/{total_suites} passed")
        print(f"📊 Individual Tests: {self.tests_passed}/{self.tests_run} passed")
        print(f"📊 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if passed_suites == total_suites:
            print("🎉 ALL TENDER SYSTEM TESTS PASSED!")
        else:
            print(f"⚠️  {total_suites - passed_suites} test suites failed")
        
        return passed_suites == total_suites

if __name__ == "__main__":
    tester = TenderSystemTester()
    success = tester.run_comprehensive_tender_tests()
    sys.exit(0 if success else 1)