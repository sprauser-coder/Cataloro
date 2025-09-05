#!/usr/bin/env python3
"""
New Backend Features Test Suite
Tests the newly added backend functionality as requested in review:
1. Price Range Settings endpoint
2. User Active Bids endpoint  
3. Enhanced Browse Listings with bid_info
4. Favorites Cleanup functionality
"""

import requests
import sys
import json
from datetime import datetime
import time

class NewBackendFeaturesTest:
    def __init__(self, base_url="https://market-refactor.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_data = {}  # Store test data for cleanup

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
                    details += f", Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Array'}"
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
        
        if success_admin and 'token' in admin_response:
            self.admin_token = admin_response['token']
            self.admin_user = admin_response['user']
            print(f"   ✅ Admin User: {self.admin_user.get('username', 'N/A')}")
        
        # Login regular user
        success_user, user_response = self.run_test(
            "Regular User Login Setup",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        
        if success_user and 'token' in user_response:
            self.user_token = user_response['token']
            self.regular_user = user_response['user']
            print(f"   ✅ Regular User: {self.regular_user.get('username', 'N/A')}")
        
        return success_admin and success_user

    def test_price_range_settings(self):
        """Test 1: Price Range Settings endpoint /api/marketplace/price-range-settings"""
        print("\n💰 Testing Price Range Settings Endpoint...")
        
        success, response = self.run_test(
            "Price Range Settings GET",
            "GET",
            "api/marketplace/price-range-settings",
            200
        )
        
        if success:
            # Verify response structure
            required_fields = ['price_range_min_percent', 'price_range_max_percent']
            has_required_fields = all(field in response for field in required_fields)
            
            self.log_test("Price Range Settings Structure", has_required_fields,
                         f"Required fields present: {has_required_fields}")
            
            if has_required_fields:
                min_percent = response.get('price_range_min_percent')
                max_percent = response.get('price_range_max_percent')
                
                # Verify default values (should be 10% each)
                default_values_correct = (min_percent == 10.0 and max_percent == 10.0)
                self.log_test("Price Range Default Values", default_values_correct,
                             f"Min: {min_percent}%, Max: {max_percent}% (expected: 10%, 10%)")
                
                print(f"   📊 Price Range Configuration:")
                print(f"      Min Range: -{min_percent}%")
                print(f"      Max Range: +{max_percent}%")
        
        return success

    def test_user_active_bids(self):
        """Test 2: User Active Bids endpoint /api/user/{user_id}/active-bids"""
        print("\n🎯 Testing User Active Bids Endpoint...")
        
        if not self.regular_user:
            print("❌ User Active Bids - SKIPPED (No regular user)")
            return False
        
        # First, test the endpoint with current user (may have no bids initially)
        success, response = self.run_test(
            "User Active Bids GET",
            "GET",
            f"api/user/{self.regular_user['id']}/active-bids",
            200
        )
        
        if success:
            # Verify response structure
            has_active_bids_key = 'active_bids' in response
            self.log_test("Active Bids Response Structure", has_active_bids_key,
                         f"'active_bids' key present: {has_active_bids_key}")
            
            if has_active_bids_key:
                active_bids = response.get('active_bids', {})
                print(f"   📊 Active Bids Found: {len(active_bids)} listings")
                
                # If there are active bids, verify their structure
                if active_bids:
                    first_listing_id = list(active_bids.keys())[0]
                    first_bid = active_bids[first_listing_id]
                    
                    required_bid_fields = ['tender_id', 'amount', 'submitted_at', 'status']
                    has_bid_structure = all(field in first_bid for field in required_bid_fields)
                    
                    self.log_test("Active Bid Data Structure", has_bid_structure,
                                 f"Bid fields present: {has_bid_structure}")
                    
                    if has_bid_structure:
                        print(f"   💰 Sample Bid: €{first_bid['amount']} on listing {first_listing_id[:8]}...")
                        print(f"   📅 Submitted: {first_bid['submitted_at']}")
                        print(f"   🔄 Status: {first_bid['status']}")
                else:
                    print("   ℹ️  No active bids found for user (expected for new user)")
                    self.log_test("Active Bids Empty Response", True, "Empty active_bids object returned correctly")
        
        return success

    def test_enhanced_browse_listings(self):
        """Test 3: Enhanced Browse Listings with bid_info"""
        print("\n🛍️ Testing Enhanced Browse Listings with bid_info...")
        
        success, response = self.run_test(
            "Enhanced Browse Listings",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success and response:
            print(f"   📊 Found {len(response)} listings")
            
            # Check if listings have bid_info
            listings_with_bid_info = 0
            sample_bid_info = None
            
            for listing in response:
                if 'bid_info' in listing:
                    listings_with_bid_info += 1
                    if not sample_bid_info:
                        sample_bid_info = listing['bid_info']
            
            has_bid_info = listings_with_bid_info > 0
            self.log_test("Browse Listings bid_info Present", has_bid_info,
                         f"{listings_with_bid_info}/{len(response)} listings have bid_info")
            
            if sample_bid_info:
                # Verify bid_info structure
                required_bid_fields = ['has_bids', 'total_bids', 'highest_bid', 'highest_bidder_id']
                has_correct_structure = all(field in sample_bid_info for field in required_bid_fields)
                
                self.log_test("bid_info Structure Correct", has_correct_structure,
                             f"Required bid_info fields present: {has_correct_structure}")
                
                if has_correct_structure:
                    print(f"   📋 Sample bid_info structure:")
                    print(f"      Has Bids: {sample_bid_info['has_bids']}")
                    print(f"      Total Bids: {sample_bid_info['total_bids']}")
                    print(f"      Highest Bid: €{sample_bid_info['highest_bid']}")
                    print(f"      Highest Bidder ID: {sample_bid_info['highest_bidder_id'][:8] if sample_bid_info['highest_bidder_id'] else 'None'}...")
            
            # Test with filters to ensure bid_info is preserved
            success_filtered, filtered_response = self.run_test(
                "Browse with Filters (bid_info preserved)",
                "GET",
                "api/marketplace/browse?type=all&price_from=0&price_to=1000",
                200
            )
            
            if success_filtered and filtered_response:
                filtered_with_bid_info = sum(1 for listing in filtered_response if 'bid_info' in listing)
                self.log_test("bid_info Preserved with Filters", filtered_with_bid_info > 0,
                             f"{filtered_with_bid_info}/{len(filtered_response)} filtered listings have bid_info")
        
        return success

    def test_favorites_cleanup_functionality(self):
        """Test 4: Favorites Cleanup when listings are deleted/updated/sold"""
        print("\n❤️ Testing Favorites Cleanup Functionality...")
        
        if not self.regular_user or not self.admin_user:
            print("❌ Favorites Cleanup - SKIPPED (Need both users)")
            return False
        
        # Step 1: Create a test listing
        print("\n1️⃣ Creating test listing for favorites cleanup...")
        test_listing = {
            "title": "Favorites Cleanup Test - Vintage Watch",
            "description": "Luxury vintage watch for testing favorites cleanup functionality.",
            "price": 850.00,
            "category": "Accessories",
            "condition": "Used - Excellent",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400"],
            "tags": ["vintage", "watch", "luxury"],
            "features": ["Automatic movement", "Leather strap", "Water resistant"]
        }
        
        success_create, create_response = self.run_test(
            "Create Test Listing for Favorites",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_create or 'listing_id' not in create_response:
            print("❌ Failed to create test listing - stopping favorites cleanup tests")
            return False
        
        listing_id = create_response['listing_id']
        self.test_data['cleanup_listing_id'] = listing_id
        print(f"   ✅ Created test listing: {listing_id}")
        
        # Step 2: Add listing to user's favorites
        print("\n2️⃣ Adding listing to user's favorites...")
        success_add_fav, add_fav_response = self.run_test(
            "Add to Favorites",
            "POST",
            f"api/user/{self.regular_user['id']}/favorites/{listing_id}",
            200
        )
        
        if success_add_fav:
            print(f"   ✅ Added listing to favorites")
            
            # Verify it's in favorites
            success_check_fav, check_fav_response = self.run_test(
                "Verify in Favorites",
                "GET",
                f"api/user/{self.regular_user['id']}/favorites",
                200
            )
            
            if success_check_fav:
                favorite_ids = [fav.get('id') for fav in check_fav_response]
                is_in_favorites = listing_id in favorite_ids
                self.log_test("Listing Added to Favorites", is_in_favorites,
                             f"Listing found in favorites: {is_in_favorites}")
        
        # Step 3: Test cleanup on listing status change to "sold"
        print("\n3️⃣ Testing favorites cleanup on status change to 'sold'...")
        update_data = {"status": "sold"}
        
        success_update_sold, update_sold_response = self.run_test(
            "Update Listing Status to Sold",
            "PUT",
            f"api/listings/{listing_id}",
            200,
            data=update_data
        )
        
        if success_update_sold:
            # Check if favorites were cleaned up
            time.sleep(1)  # Brief pause for cleanup to process
            
            success_check_cleanup, check_cleanup_response = self.run_test(
                "Check Favorites After Sold Status",
                "GET",
                f"api/user/{self.regular_user['id']}/favorites",
                200
            )
            
            if success_check_cleanup:
                favorite_ids_after = [fav.get('id') for fav in check_cleanup_response]
                is_cleaned_up = listing_id not in favorite_ids_after
                self.log_test("Favorites Cleanup on Sold Status", is_cleaned_up,
                             f"Listing removed from favorites: {is_cleaned_up}")
        
        # Step 4: Test cleanup on listing deletion
        print("\n4️⃣ Testing favorites cleanup on listing deletion...")
        
        # First, create another test listing and add to favorites
        test_listing_2 = {
            "title": "Favorites Cleanup Test 2 - Camera Lens",
            "description": "Professional camera lens for deletion cleanup testing.",
            "price": 450.00,
            "category": "Photography",
            "condition": "Used - Good",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"]
        }
        
        success_create_2, create_response_2 = self.run_test(
            "Create Second Test Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing_2
        )
        
        if success_create_2:
            listing_id_2 = create_response_2['listing_id']
            self.test_data['cleanup_listing_id_2'] = listing_id_2
            
            # Add to favorites
            success_add_fav_2, _ = self.run_test(
                "Add Second Listing to Favorites",
                "POST",
                f"api/user/{self.regular_user['id']}/favorites/{listing_id_2}",
                200
            )
            
            if success_add_fav_2:
                # Delete the listing
                success_delete, delete_response = self.run_test(
                    "Delete Listing (Test Cleanup)",
                    "DELETE",
                    f"api/listings/{listing_id_2}",
                    200
                )
                
                if success_delete:
                    # Check if favorites were cleaned up
                    time.sleep(1)  # Brief pause for cleanup to process
                    
                    success_check_delete_cleanup, check_delete_cleanup_response = self.run_test(
                        "Check Favorites After Deletion",
                        "GET",
                        f"api/user/{self.regular_user['id']}/favorites",
                        200
                    )
                    
                    if success_check_delete_cleanup:
                        favorite_ids_after_delete = [fav.get('id') for fav in check_delete_cleanup_response]
                        is_cleaned_up_delete = listing_id_2 not in favorite_ids_after_delete
                        self.log_test("Favorites Cleanup on Deletion", is_cleaned_up_delete,
                                     f"Deleted listing removed from favorites: {is_cleaned_up_delete}")
        
        # Step 5: Test cleanup when tender is accepted (if tender system is available)
        print("\n5️⃣ Testing favorites cleanup when tender is accepted...")
        
        # Create a third test listing for tender acceptance test
        test_listing_3 = {
            "title": "Favorites Cleanup Test 3 - Gaming Headset",
            "description": "Gaming headset for tender acceptance cleanup testing.",
            "price": 120.00,
            "category": "Electronics",
            "condition": "Used - Good",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"]
        }
        
        success_create_3, create_response_3 = self.run_test(
            "Create Third Test Listing for Tender",
            "POST",
            "api/listings",
            200,
            data=test_listing_3
        )
        
        if success_create_3:
            listing_id_3 = create_response_3['listing_id']
            self.test_data['cleanup_listing_id_3'] = listing_id_3
            
            # Add to favorites
            success_add_fav_3, _ = self.run_test(
                "Add Third Listing to Favorites",
                "POST",
                f"api/user/{self.regular_user['id']}/favorites/{listing_id_3}",
                200
            )
            
            if success_add_fav_3:
                # Submit a tender
                tender_data = {
                    "listing_id": listing_id_3,
                    "buyer_id": self.regular_user['id'],
                    "offer_amount": 125.00
                }
                
                success_tender, tender_response = self.run_test(
                    "Submit Tender for Cleanup Test",
                    "POST",
                    "api/tenders/submit",
                    200,
                    data=tender_data
                )
                
                if success_tender and 'tender_id' in tender_response:
                    tender_id = tender_response['tender_id']
                    
                    # Accept the tender (as seller)
                    accept_data = {"seller_id": self.admin_user['id']}
                    
                    success_accept, accept_response = self.run_test(
                        "Accept Tender (Test Cleanup)",
                        "PUT",
                        f"api/tenders/{tender_id}/accept",
                        200,
                        data=accept_data
                    )
                    
                    if success_accept:
                        # Check if favorites were cleaned up
                        time.sleep(1)  # Brief pause for cleanup to process
                        
                        success_check_tender_cleanup, check_tender_cleanup_response = self.run_test(
                            "Check Favorites After Tender Acceptance",
                            "GET",
                            f"api/user/{self.regular_user['id']}/favorites",
                            200
                        )
                        
                        if success_check_tender_cleanup:
                            favorite_ids_after_tender = [fav.get('id') for fav in check_tender_cleanup_response]
                            is_cleaned_up_tender = listing_id_3 not in favorite_ids_after_tender
                            self.log_test("Favorites Cleanup on Tender Acceptance", is_cleaned_up_tender,
                                         f"Sold listing removed from favorites: {is_cleaned_up_tender}")
        
        return True

    def cleanup_test_data(self):
        """Clean up any test data created during testing"""
        print("\n🧹 Cleaning up test data...")
        
        # Clean up any remaining test listings
        for key, listing_id in self.test_data.items():
            if 'listing_id' in key and listing_id:
                try:
                    self.run_test(
                        f"Cleanup {key}",
                        "DELETE",
                        f"api/listings/{listing_id}",
                        200
                    )
                except:
                    pass  # Ignore cleanup errors

    def run_all_tests(self):
        """Run all new backend feature tests"""
        print("🚀 Starting New Backend Features Test Suite...")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False
        
        # Run tests
        test_results = []
        
        print("\n" + "=" * 60)
        test_results.append(self.test_price_range_settings())
        
        print("\n" + "=" * 60)
        test_results.append(self.test_user_active_bids())
        
        print("\n" + "=" * 60)
        test_results.append(self.test_enhanced_browse_listings())
        
        print("\n" + "=" * 60)
        test_results.append(self.test_favorites_cleanup_functionality())
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 NEW BACKEND FEATURES TEST SUMMARY")
        print("=" * 60)
        
        test_names = [
            "Price Range Settings",
            "User Active Bids", 
            "Enhanced Browse Listings",
            "Favorites Cleanup"
        ]
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        for i, (name, result) in enumerate(zip(test_names, test_results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{i+1}. {name}: {status}")
        
        print(f"\nOverall Results: {passed_tests}/{total_tests} major tests passed")
        print(f"Individual Tests: {self.tests_passed}/{self.tests_run} individual tests passed")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL NEW BACKEND FEATURES TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️ {total_tests - passed_tests} major test(s) failed")
            return False

if __name__ == "__main__":
    tester = NewBackendFeaturesTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)