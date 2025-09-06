#!/usr/bin/env python3
"""
Cataloro Marketplace - Bid Info Testing
Focused test for browse listings endpoint bid_info functionality
"""

import requests
import sys
import json
from datetime import datetime

class BidInfoTester:
    def __init__(self, base_url="https://cataloro-ads.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_listing_id = None
        self.test_tender_id = None

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
                    details += f", Response length: {len(str(response_data))}"
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
        """Setup test users for bid testing"""
        print("\n🔧 Setting up test users...")
        
        # Login admin user (seller)
        success_admin, admin_response = self.run_test(
            "Admin Login (Seller)",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success_admin and 'user' in admin_response:
            self.admin_user = admin_response['user']
            print(f"   ✅ Admin user logged in: {self.admin_user['id']}")
        
        # Login regular user (buyer)
        success_user, user_response = self.run_test(
            "Regular User Login (Buyer)",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        
        if success_user and 'user' in user_response:
            self.regular_user = user_response['user']
            print(f"   ✅ Regular user logged in: {self.regular_user['id']}")
        
        return success_admin and success_user

    def test_browse_endpoint_basic(self):
        """Test 1: Basic browse endpoint functionality"""
        print("\n📋 TEST 1: Testing Browse Endpoint Basic Functionality")
        
        success, response = self.run_test(
            "Browse Listings Endpoint",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            print(f"   📊 Found {len(response)} listings")
            return True, response
        return False, []

    def test_bid_info_structure(self, listings):
        """Test 2: Check bid_info structure in all listings"""
        print("\n🏗️ TEST 2: Checking bid_info Structure in All Listings")
        
        if not listings:
            self.log_test("Bid Info Structure Check", False, "No listings to check")
            return False
        
        required_fields = ['has_bids', 'total_bids', 'highest_bid', 'highest_bidder_id']
        listings_with_bid_info = 0
        listings_with_complete_structure = 0
        
        for listing in listings:
            listing_id = listing.get('id', 'Unknown')
            print(f"\n   📋 Checking listing: {listing.get('title', 'Unknown')[:50]}...")
            print(f"      ID: {listing_id}")
            
            if 'bid_info' in listing:
                listings_with_bid_info += 1
                bid_info = listing['bid_info']
                print(f"      bid_info found: {bid_info}")
                
                # Check all required fields
                missing_fields = []
                for field in required_fields:
                    if field not in bid_info:
                        missing_fields.append(field)
                
                if not missing_fields:
                    listings_with_complete_structure += 1
                    print(f"      ✅ Complete bid_info structure")
                    
                    # Validate data types
                    type_checks = [
                        isinstance(bid_info['has_bids'], bool),
                        isinstance(bid_info['total_bids'], int),
                        isinstance(bid_info['highest_bid'], (int, float)),
                        isinstance(bid_info['highest_bidder_id'], str)
                    ]
                    
                    if all(type_checks):
                        print(f"      ✅ All field types correct")
                    else:
                        print(f"      ⚠️ Some field types incorrect")
                else:
                    print(f"      ❌ Missing fields: {missing_fields}")
            else:
                print(f"      ❌ No bid_info field found")
        
        structure_success = listings_with_complete_structure == len(listings)
        self.log_test("All Listings Have bid_info", listings_with_bid_info == len(listings), 
                     f"{listings_with_bid_info}/{len(listings)} listings have bid_info")
        self.log_test("All bid_info Complete Structure", structure_success,
                     f"{listings_with_complete_structure}/{len(listings)} listings have complete bid_info structure")
        
        return structure_success

    def create_test_listing(self):
        """Create a test listing for tender testing"""
        print("\n🏗️ Creating Test Listing for Tender Testing")
        
        if not self.admin_user:
            self.log_test("Create Test Listing", False, "No admin user available")
            return False
        
        test_listing = {
            "title": "Bid Info Test Listing - Premium Catalyst Unit",
            "description": "High-quality automotive catalyst for bid info testing. Excellent precious metal content.",
            "price": 500.00,  # Starting price
            "category": "Catalysts",
            "condition": "Used - Excellent",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
            "tags": ["catalyst", "automotive", "testing"],
            "features": ["High PT content", "Tested quality", "Bid testing"]
        }
        
        success, response = self.run_test(
            "Create Test Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if success and 'listing_id' in response:
            self.test_listing_id = response['listing_id']
            print(f"   ✅ Created test listing: {self.test_listing_id}")
            print(f"   💰 Starting price: €{test_listing['price']}")
            return True
        
        return False

    def test_initial_bid_info(self):
        """Test 3: Check initial bid_info for new listing (no bids)"""
        print("\n🆕 TEST 3: Testing Initial bid_info (No Bids)")
        
        if not self.test_listing_id:
            self.log_test("Initial Bid Info Test", False, "No test listing available")
            return False
        
        success, listings = self.run_test(
            "Browse After Creating Test Listing",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False
        
        # Find our test listing
        test_listing = None
        for listing in listings:
            if listing.get('id') == self.test_listing_id:
                test_listing = listing
                break
        
        if not test_listing:
            self.log_test("Find Test Listing in Browse", False, "Test listing not found in browse results")
            return False
        
        print(f"   📋 Found test listing: {test_listing.get('title')}")
        
        # Check initial bid_info
        if 'bid_info' not in test_listing:
            self.log_test("Initial bid_info Present", False, "bid_info field missing")
            return False
        
        bid_info = test_listing['bid_info']
        print(f"   📊 Initial bid_info: {bid_info}")
        
        # Validate initial state
        expected_initial_state = {
            'has_bids': False,
            'total_bids': 0,
            'highest_bid': 500.00,  # Should match starting price
            'highest_bidder_id': ''
        }
        
        initial_state_correct = True
        for field, expected_value in expected_initial_state.items():
            actual_value = bid_info.get(field)
            if actual_value != expected_value:
                print(f"   ❌ {field}: expected {expected_value}, got {actual_value}")
                initial_state_correct = False
            else:
                print(f"   ✅ {field}: {actual_value} (correct)")
        
        self.log_test("Initial bid_info State Correct", initial_state_correct,
                     f"All initial bid_info fields match expected values")
        
        return initial_state_correct

    def submit_test_tender(self, offer_amount):
        """Submit a test tender offer"""
        print(f"\n💰 Submitting Test Tender: €{offer_amount}")
        
        if not self.test_listing_id or not self.regular_user:
            self.log_test("Submit Test Tender", False, "Missing test listing or user")
            return False
        
        tender_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.regular_user['id'],
            "offer_amount": offer_amount
        }
        
        success, response = self.run_test(
            f"Submit Tender €{offer_amount}",
            "POST",
            "api/tenders/submit",
            200,
            data=tender_data
        )
        
        if success and 'tender_id' in response:
            tender_id = response['tender_id']
            print(f"   ✅ Tender submitted: {tender_id}")
            print(f"   💰 Offer amount: €{offer_amount}")
            return True, tender_id
        
        return False, None

    def test_bid_info_with_single_bid(self):
        """Test 4: Check bid_info after submitting one bid"""
        print("\n🎯 TEST 4: Testing bid_info with Single Bid")
        
        # Submit first tender
        tender_success, tender_id = self.submit_test_tender(600.00)
        if not tender_success:
            return False
        
        self.test_tender_id = tender_id
        
        # Check updated bid_info
        success, listings = self.run_test(
            "Browse After First Tender",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False
        
        # Find our test listing
        test_listing = None
        for listing in listings:
            if listing.get('id') == self.test_listing_id:
                test_listing = listing
                break
        
        if not test_listing:
            self.log_test("Find Test Listing After Tender", False, "Test listing not found")
            return False
        
        bid_info = test_listing.get('bid_info', {})
        print(f"   📊 bid_info after first tender: {bid_info}")
        
        # Validate updated state
        expected_state = {
            'has_bids': True,
            'total_bids': 1,
            'highest_bid': 600.00,
            'highest_bidder_id': self.regular_user['id']
        }
        
        state_correct = True
        for field, expected_value in expected_state.items():
            actual_value = bid_info.get(field)
            if actual_value != expected_value:
                print(f"   ❌ {field}: expected {expected_value}, got {actual_value}")
                state_correct = False
            else:
                print(f"   ✅ {field}: {actual_value} (correct)")
        
        self.log_test("bid_info After Single Bid", state_correct,
                     f"bid_info correctly updated after first tender")
        
        return state_correct

    def test_bid_info_with_multiple_bids(self):
        """Test 5: Check bid_info after submitting multiple bids"""
        print("\n🎯🎯 TEST 5: Testing bid_info with Multiple Bids")
        
        # Submit second tender (higher amount)
        tender_success_2, tender_id_2 = self.submit_test_tender(750.00)
        if not tender_success_2:
            return False
        
        # Submit third tender (even higher amount)
        tender_success_3, tender_id_3 = self.submit_test_tender(850.00)
        if not tender_success_3:
            return False
        
        # Check updated bid_info
        success, listings = self.run_test(
            "Browse After Multiple Tenders",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False
        
        # Find our test listing
        test_listing = None
        for listing in listings:
            if listing.get('id') == self.test_listing_id:
                test_listing = listing
                break
        
        if not test_listing:
            self.log_test("Find Test Listing After Multiple Tenders", False, "Test listing not found")
            return False
        
        bid_info = test_listing.get('bid_info', {})
        print(f"   📊 bid_info after multiple tenders: {bid_info}")
        
        # Validate updated state (should show highest bid)
        expected_state = {
            'has_bids': True,
            'total_bids': 3,  # Should have 3 total bids now
            'highest_bid': 850.00,  # Should be the highest amount
            'highest_bidder_id': self.regular_user['id']
        }
        
        state_correct = True
        for field, expected_value in expected_state.items():
            actual_value = bid_info.get(field)
            if actual_value != expected_value:
                print(f"   ❌ {field}: expected {expected_value}, got {actual_value}")
                state_correct = False
            else:
                print(f"   ✅ {field}: {actual_value} (correct)")
        
        self.log_test("bid_info After Multiple Bids", state_correct,
                     f"bid_info correctly shows highest of multiple bids")
        
        return state_correct

    def test_highest_bid_vs_price_difference(self):
        """Test 6: Verify highest_bid is different from original price when bids exist"""
        print("\n💰 TEST 6: Testing highest_bid vs Original Price Difference")
        
        success, listings = self.run_test(
            "Browse for Price Comparison",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False
        
        price_differences_found = 0
        listings_with_bids = 0
        
        for listing in listings:
            bid_info = listing.get('bid_info', {})
            original_price = listing.get('price', 0)
            highest_bid = bid_info.get('highest_bid', 0)
            has_bids = bid_info.get('has_bids', False)
            
            print(f"\n   📋 Listing: {listing.get('title', 'Unknown')[:40]}...")
            print(f"      Original Price: €{original_price}")
            print(f"      Highest Bid: €{highest_bid}")
            print(f"      Has Bids: {has_bids}")
            
            if has_bids:
                listings_with_bids += 1
                if highest_bid != original_price:
                    price_differences_found += 1
                    print(f"      ✅ Price difference detected: €{highest_bid - original_price:+.2f}")
                else:
                    print(f"      ⚠️ Highest bid equals original price")
            else:
                if highest_bid == original_price:
                    print(f"      ✅ No bids: highest_bid equals original price (correct)")
                else:
                    print(f"      ❌ No bids but highest_bid ≠ original price")
        
        # For our test listing specifically
        test_listing = None
        for listing in listings:
            if listing.get('id') == self.test_listing_id:
                test_listing = listing
                break
        
        test_listing_correct = False
        if test_listing:
            test_bid_info = test_listing.get('bid_info', {})
            test_original_price = test_listing.get('price', 0)
            test_highest_bid = test_bid_info.get('highest_bid', 0)
            
            print(f"\n   🎯 TEST LISTING SPECIFIC CHECK:")
            print(f"      Original Price: €{test_original_price}")
            print(f"      Current Highest Bid: €{test_highest_bid}")
            print(f"      Difference: €{test_highest_bid - test_original_price:+.2f}")
            
            test_listing_correct = test_highest_bid > test_original_price
            
        self.log_test("Listings with Bids Found", listings_with_bids > 0,
                     f"Found {listings_with_bids} listings with bids")
        self.log_test("Price Differences Detected", price_differences_found > 0,
                     f"Found {price_differences_found} listings where highest_bid ≠ original price")
        self.log_test("Test Listing Price Difference", test_listing_correct,
                     f"Test listing highest_bid (€{test_highest_bid if test_listing else 0}) > original price (€{test_original_price if test_listing else 0})")
        
        return test_listing_correct and price_differences_found > 0

    def test_bid_info_with_filters(self):
        """Test 7: Verify bid_info persists with browse filters"""
        print("\n🔍 TEST 7: Testing bid_info with Browse Filters")
        
        # Test with price filter
        success_price, price_filtered = self.run_test(
            "Browse with Price Filter",
            "GET",
            "api/marketplace/browse?price_from=400&price_to=1000",
            200
        )
        
        if success_price:
            filtered_listings_with_bid_info = 0
            for listing in price_filtered:
                if 'bid_info' in listing:
                    filtered_listings_with_bid_info += 1
            
            self.log_test("bid_info Present with Price Filter", 
                         filtered_listings_with_bid_info == len(price_filtered),
                         f"{filtered_listings_with_bid_info}/{len(price_filtered)} filtered listings have bid_info")
        
        # Test with type filter
        success_type, type_filtered = self.run_test(
            "Browse with Type Filter",
            "GET",
            "api/marketplace/browse?type=all",
            200
        )
        
        if success_type:
            type_filtered_with_bid_info = 0
            for listing in type_filtered:
                if 'bid_info' in listing:
                    type_filtered_with_bid_info += 1
            
            self.log_test("bid_info Present with Type Filter",
                         type_filtered_with_bid_info == len(type_filtered),
                         f"{type_filtered_with_bid_info}/{len(type_filtered)} type-filtered listings have bid_info")
        
        return success_price and success_type

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        if self.test_listing_id:
            success, response = self.run_test(
                "Delete Test Listing",
                "DELETE",
                f"api/listings/{self.test_listing_id}",
                200
            )
            if success:
                print(f"   ✅ Deleted test listing: {self.test_listing_id}")

    def run_all_tests(self):
        """Run all bid_info tests"""
        print("🎯 CATALORO MARKETPLACE - BID INFO TESTING")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False
        
        # Test 1: Basic browse endpoint
        browse_success, initial_listings = self.test_browse_endpoint_basic()
        if not browse_success:
            print("❌ Basic browse test failed - stopping tests")
            return False
        
        # Test 2: Check bid_info structure in existing listings
        structure_success = self.test_bid_info_structure(initial_listings)
        
        # Test 3: Create test listing and check initial bid_info
        if not self.create_test_listing():
            print("❌ Failed to create test listing - stopping bid tests")
            return False
        
        initial_bid_success = self.test_initial_bid_info()
        
        # Test 4: Submit single bid and check bid_info
        single_bid_success = self.test_bid_info_with_single_bid()
        
        # Test 5: Submit multiple bids and check bid_info
        multiple_bid_success = self.test_bid_info_with_multiple_bids()
        
        # Test 6: Check price differences
        price_diff_success = self.test_highest_bid_vs_price_difference()
        
        # Test 7: Test with filters
        filter_success = self.test_bid_info_with_filters()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 BID INFO TEST SUMMARY")
        print("=" * 60)
        
        test_results = [
            ("Browse Endpoint Basic", browse_success),
            ("bid_info Structure Check", structure_success),
            ("Initial bid_info State", initial_bid_success),
            ("Single Bid bid_info Update", single_bid_success),
            ("Multiple Bids bid_info Update", multiple_bid_success),
            ("Price Difference Verification", price_diff_success),
            ("Filters Preserve bid_info", filter_success)
        ]
        
        for test_name, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} {test_name}")
        
        passed_tests = sum(1 for _, success in test_results if success)
        total_tests = len(test_results)
        
        print(f"\n📈 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL BID INFO TESTS PASSED!")
            return True
        else:
            print(f"⚠️ {total_tests - passed_tests} tests failed")
            return False

if __name__ == "__main__":
    tester = BidInfoTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)