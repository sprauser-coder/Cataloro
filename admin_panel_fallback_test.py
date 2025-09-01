#!/usr/bin/env python3
"""
Admin Panel Fallback Data Fix Test Suite
Tests the specific fix for admin panel falling back to local marketplace data
"""

import requests
import sys
import json
import time
from datetime import datetime

class AdminPanelFallbackTester:
    def __init__(self, base_url="https://cataloro-marketplace.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.admin_user = None
        self.test_listing_ids = []
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

    def setup_admin_login(self):
        """Setup admin authentication"""
        print("\n🔐 Setting up admin authentication...")
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
            print(f"   ✅ Admin authenticated: {self.admin_user.get('full_name', 'Admin')}")
        return success

    def create_test_listings(self):
        """Create 2-3 test listings via API"""
        print("\n📝 Creating test listings for admin panel testing...")
        
        test_listings = [
            {
                "title": "Admin Panel Test Listing 1 - MacBook Pro M2",
                "description": "Test listing for admin panel fallback fix verification. MacBook Pro with M2 chip, 16GB RAM, 512GB SSD.",
                "price": 2299.99,
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.admin_user['id'],
                "images": ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"],
                "tags": ["laptop", "apple", "macbook", "admin-test"]
            },
            {
                "title": "Admin Panel Test Listing 2 - iPhone 15 Pro",
                "description": "Test listing for admin panel fallback fix verification. iPhone 15 Pro with 256GB storage, Titanium finish.",
                "price": 1199.99,
                "category": "Electronics",
                "condition": "New",
                "seller_id": self.admin_user['id'],
                "images": ["https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400"],
                "tags": ["phone", "apple", "iphone", "admin-test"]
            },
            {
                "title": "Admin Panel Test Listing 3 - Gaming Setup",
                "description": "Test listing for admin panel fallback fix verification. Complete gaming setup with RGB keyboard, mouse, and headset.",
                "price": 599.99,
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": self.admin_user['id'],
                "images": ["https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400"],
                "tags": ["gaming", "setup", "peripherals", "admin-test"]
            }
        ]
        
        created_count = 0
        for i, listing_data in enumerate(test_listings):
            success, response = self.run_test(
                f"Create Test Listing {i+1}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            if success and 'listing_id' in response:
                self.test_listing_ids.append(response['listing_id'])
                created_count += 1
                print(f"   ✅ Created listing {i+1}: {response['listing_id']}")
        
        self.log_test("Test Listings Creation", created_count == 3, f"Created {created_count}/3 test listings")
        return created_count == 3

    def verify_admin_panel_loading(self):
        """Check that /api/listings returns all listings properly"""
        print("\n🔍 Verifying admin panel loading with /api/listings endpoint...")
        
        success, response = self.run_test(
            "Admin Panel Listings Endpoint",
            "GET",
            "api/listings",
            200
        )
        
        if success:
            listings_data = response.get('listings', [])
            total_count = response.get('total', 0)
            
            # Check if our test listings are present
            test_listings_found = 0
            for listing_id in self.test_listing_ids:
                found = any(listing.get('id') == listing_id for listing in listings_data)
                if found:
                    test_listings_found += 1
            
            print(f"   📊 Total listings in /api/listings: {total_count}")
            print(f"   📊 Listings in response array: {len(listings_data)}")
            print(f"   📊 Test listings found: {test_listings_found}/{len(self.test_listing_ids)}")
            
            self.log_test("Test Listings in Admin Panel", test_listings_found == len(self.test_listing_ids),
                         f"Found {test_listings_found}/{len(self.test_listing_ids)} test listings")
            
            return success and test_listings_found == len(self.test_listing_ids)
        
        return False

    def get_listings_count(self, endpoint_name, endpoint):
        """Get count of listings from specific endpoint"""
        success, response = self.run_test(
            f"Get {endpoint_name} Count",
            "GET",
            endpoint,
            200
        )
        
        if success:
            if isinstance(response, list):
                # Array format (like /api/marketplace/browse)
                count = len(response)
                test_listings = sum(1 for listing in response 
                                  if listing.get('id') in self.test_listing_ids)
            else:
                # Object format (like /api/listings)
                listings = response.get('listings', [])
                count = len(listings)
                test_listings = sum(1 for listing in listings 
                                  if listing.get('id') in self.test_listing_ids)
            
            print(f"   📊 {endpoint_name} total count: {count}")
            print(f"   📊 {endpoint_name} test listings: {test_listings}")
            return count, test_listings
        
        return 0, 0

    def test_bulk_delete_persistence(self):
        """Test bulk delete persistence - ensure deleted listings don't reappear"""
        print("\n🗑️ Testing bulk delete persistence...")
        
        if not self.test_listing_ids:
            print("❌ No test listings available for bulk delete test")
            return False
        
        # Step 1: Get initial counts
        print("\n1️⃣ Getting initial listing counts...")
        initial_api_count, initial_api_test = self.get_listings_count("API Listings", "api/listings")
        initial_browse_count, initial_browse_test = self.get_listings_count("Browse Listings", "api/marketplace/browse")
        
        print(f"   📊 Initial state - API: {initial_api_count} total, {initial_api_test} test")
        print(f"   📊 Initial state - Browse: {initial_browse_count} total, {initial_browse_test} test")
        
        # Step 2: Perform bulk delete operations
        print("\n2️⃣ Performing bulk delete operations...")
        deleted_count = 0
        for i, listing_id in enumerate(self.test_listing_ids):
            success, response = self.run_test(
                f"Bulk Delete Listing {i+1}",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                deleted_count += 1
                print(f"   ✅ Deleted listing {i+1}: {listing_id}")
                # Verify delete response
                if response.get('deleted_count') == 1:
                    print(f"      ✅ Backend confirmed deletion (deleted_count: 1)")
                else:
                    print(f"      ⚠️ Backend response: {response}")
        
        self.log_test("Bulk Delete Operations", deleted_count == len(self.test_listing_ids),
                     f"Deleted {deleted_count}/{len(self.test_listing_ids)} listings")
        
        # Step 3: Wait a moment for database consistency
        print("\n⏳ Waiting for database consistency...")
        time.sleep(2)
        
        # Step 4: Verify they're removed from backend database
        print("\n3️⃣ Verifying removal from backend database...")
        post_delete_api_count, post_delete_api_test = self.get_listings_count("API Listings After Delete", "api/listings")
        post_delete_browse_count, post_delete_browse_test = self.get_listings_count("Browse Listings After Delete", "api/marketplace/browse")
        
        print(f"   📊 After delete - API: {post_delete_api_count} total, {post_delete_api_test} test")
        print(f"   📊 After delete - Browse: {post_delete_browse_count} total, {post_delete_browse_test} test")
        
        # Step 5: Check that fetchListings() after delete shows reduced count
        api_count_reduced = post_delete_api_count < initial_api_count
        browse_count_reduced = post_delete_browse_count < initial_browse_count
        test_listings_gone_api = post_delete_api_test == 0
        test_listings_gone_browse = post_delete_browse_test == 0
        
        self.log_test("API Count Decreased", api_count_reduced,
                     f"API count: {initial_api_count} → {post_delete_api_count}")
        self.log_test("Browse Count Decreased", browse_count_reduced,
                     f"Browse count: {initial_browse_count} → {post_delete_browse_count}")
        self.log_test("Test Listings Removed from API", test_listings_gone_api,
                     f"Test listings in API: {initial_api_test} → {post_delete_api_test}")
        self.log_test("Test Listings Removed from Browse", test_listings_gone_browse,
                     f"Test listings in Browse: {initial_browse_test} → {post_delete_browse_test}")
        
        # Step 6: Confirm no listings reappear due to fallback data
        print("\n4️⃣ Testing for fallback data reappearance...")
        
        # Make multiple requests to check for consistency
        consistent_results = True
        for i in range(3):
            print(f"   🔄 Consistency check {i+1}/3...")
            check_api_count, check_api_test = self.get_listings_count(f"API Check {i+1}", "api/listings")
            check_browse_count, check_browse_test = self.get_listings_count(f"Browse Check {i+1}", "api/marketplace/browse")
            
            if (check_api_test > 0 or check_browse_test > 0 or 
                check_api_count != post_delete_api_count or 
                check_browse_count != post_delete_browse_count):
                consistent_results = False
                print(f"      ⚠️ Inconsistency detected - API: {check_api_count}/{check_api_test}, Browse: {check_browse_count}/{check_browse_test}")
            else:
                print(f"      ✅ Consistent - API: {check_api_count}/{check_api_test}, Browse: {check_browse_count}/{check_browse_test}")
            
            time.sleep(1)  # Brief pause between checks
        
        self.log_test("No Fallback Data Reappearance", consistent_results,
                     f"Deleted listings stayed deleted across multiple checks")
        
        return (deleted_count == len(self.test_listing_ids) and 
                test_listings_gone_api and test_listings_gone_browse and 
                consistent_results)

    def test_admin_panel_consistency(self):
        """Test admin panel consistency - count before/after operations"""
        print("\n📊 Testing admin panel consistency...")
        
        # Create a new test listing for consistency testing
        consistency_listing = {
            "title": "Admin Panel Consistency Test - Wireless Earbuds",
            "description": "Test listing for admin panel consistency verification. Premium wireless earbuds with noise cancellation.",
            "price": 199.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400"],
            "tags": ["earbuds", "wireless", "audio", "consistency-test"]
        }
        
        # Step 1: Get baseline counts
        print("\n1️⃣ Getting baseline counts...")
        baseline_api_count, _ = self.get_listings_count("Baseline API", "api/listings")
        baseline_browse_count, _ = self.get_listings_count("Baseline Browse", "api/marketplace/browse")
        
        # Step 2: Create new listing
        print("\n2️⃣ Creating consistency test listing...")
        success, response = self.run_test(
            "Create Consistency Test Listing",
            "POST",
            "api/listings",
            200,
            data=consistency_listing
        )
        
        if not success:
            return False
        
        consistency_listing_id = response.get('listing_id')
        print(f"   ✅ Created consistency test listing: {consistency_listing_id}")
        
        # Step 3: Verify count increase
        print("\n3️⃣ Verifying count increase after creation...")
        after_create_api_count, _ = self.get_listings_count("After Create API", "api/listings")
        after_create_browse_count, _ = self.get_listings_count("After Create Browse", "api/marketplace/browse")
        
        api_increased = after_create_api_count == baseline_api_count + 1
        browse_increased = after_create_browse_count == baseline_browse_count + 1
        
        self.log_test("Count Increased After Create (API)", api_increased,
                     f"API count: {baseline_api_count} → {after_create_api_count}")
        self.log_test("Count Increased After Create (Browse)", browse_increased,
                     f"Browse count: {baseline_browse_count} → {after_create_browse_count}")
        
        # Step 4: Delete the listing
        print("\n4️⃣ Deleting consistency test listing...")
        success, response = self.run_test(
            "Delete Consistency Test Listing",
            "DELETE",
            f"api/listings/{consistency_listing_id}",
            200
        )
        
        if not success:
            return False
        
        # Step 5: Verify count decrease and stays decreased
        print("\n5️⃣ Verifying count decrease after deletion...")
        time.sleep(1)  # Brief pause for consistency
        
        after_delete_api_count, _ = self.get_listings_count("After Delete API", "api/listings")
        after_delete_browse_count, _ = self.get_listings_count("After Delete Browse", "api/marketplace/browse")
        
        api_decreased = after_delete_api_count == baseline_api_count
        browse_decreased = after_delete_browse_count == baseline_browse_count
        
        self.log_test("Count Decreased After Delete (API)", api_decreased,
                     f"API count: {after_create_api_count} → {after_delete_api_count}")
        self.log_test("Count Decreased After Delete (Browse)", browse_decreased,
                     f"Browse count: {after_create_browse_count} → {after_delete_browse_count}")
        
        # Step 6: Multiple consistency checks
        print("\n6️⃣ Multiple consistency checks...")
        consistency_maintained = True
        for i in range(3):
            time.sleep(1)
            check_api_count, _ = self.get_listings_count(f"Consistency Check {i+1} API", "api/listings")
            check_browse_count, _ = self.get_listings_count(f"Consistency Check {i+1} Browse", "api/marketplace/browse")
            
            if check_api_count != baseline_api_count or check_browse_count != baseline_browse_count:
                consistency_maintained = False
                print(f"   ⚠️ Consistency check {i+1} failed - API: {check_api_count}, Browse: {check_browse_count}")
            else:
                print(f"   ✅ Consistency check {i+1} passed - API: {check_api_count}, Browse: {check_browse_count}")
        
        self.log_test("Consistency Maintained", consistency_maintained,
                     f"Counts remained stable across multiple checks")
        
        return (api_increased and browse_increased and 
                api_decreased and browse_decreased and 
                consistency_maintained)

    def test_backend_vs_frontend_consistency(self):
        """Test backend vs frontend consistency - ensure counts match"""
        print("\n🔄 Testing backend vs frontend consistency...")
        
        # Get counts from both endpoints multiple times
        consistency_checks = []
        
        for i in range(5):
            print(f"\n   🔍 Consistency check {i+1}/5...")
            
            api_count, _ = self.get_listings_count(f"API Check {i+1}", "api/listings")
            browse_count, _ = self.get_listings_count(f"Browse Check {i+1}", "api/marketplace/browse")
            
            # Note: These might not be exactly equal due to different filtering
            # but they should be consistent within themselves
            consistency_checks.append((api_count, browse_count))
            
            print(f"      API: {api_count}, Browse: {browse_count}")
            time.sleep(0.5)
        
        # Check for consistency within each endpoint
        api_counts = [check[0] for check in consistency_checks]
        browse_counts = [check[1] for check in consistency_checks]
        
        api_consistent = len(set(api_counts)) == 1  # All counts are the same
        browse_consistent = len(set(browse_counts)) == 1  # All counts are the same
        
        self.log_test("API Endpoint Consistency", api_consistent,
                     f"API counts: {api_counts}")
        self.log_test("Browse Endpoint Consistency", browse_consistent,
                     f"Browse counts: {browse_counts}")
        
        # Additional check: Verify specific listings exist in both endpoints
        print("\n   🔍 Cross-endpoint listing verification...")
        
        # Get current listings from both endpoints
        success_api, api_response = self.run_test(
            "Get API Listings for Cross-Check",
            "GET",
            "api/listings",
            200
        )
        
        success_browse, browse_response = self.run_test(
            "Get Browse Listings for Cross-Check",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        cross_consistency = True
        if success_api and success_browse:
            api_listings = api_response.get('listings', [])
            browse_listings = browse_response if isinstance(browse_response, list) else []
            
            # Check if active listings from API appear in browse
            api_active_ids = {listing['id'] for listing in api_listings 
                            if listing.get('status') == 'active'}
            browse_ids = {listing['id'] for listing in browse_listings}
            
            missing_in_browse = api_active_ids - browse_ids
            extra_in_browse = browse_ids - api_active_ids
            
            if missing_in_browse:
                print(f"   ⚠️ Active listings missing in browse: {len(missing_in_browse)}")
                cross_consistency = False
            
            if extra_in_browse:
                print(f"   ⚠️ Extra listings in browse: {len(extra_in_browse)}")
                # This might be OK if browse includes inactive listings
            
            if not missing_in_browse and not extra_in_browse:
                print(f"   ✅ Perfect cross-endpoint consistency")
            elif not missing_in_browse:
                print(f"   ✅ All active listings appear in browse (some extra is OK)")
        
        self.log_test("Cross-Endpoint Consistency", cross_consistency,
                     f"Active listings properly synchronized between endpoints")
        
        return api_consistent and browse_consistent and cross_consistency

    def run_admin_panel_fallback_tests(self):
        """Run the complete admin panel fallback data fix test suite"""
        print("🚀 Starting Admin Panel Fallback Data Fix Tests")
        print("=" * 70)
        
        # Setup
        if not self.setup_admin_login():
            print("❌ Admin authentication failed - stopping tests")
            return False
        
        # Test 1: Create Test Listings
        print("\n" + "="*50)
        print("TEST 1: CREATE TEST LISTINGS")
        print("="*50)
        create_success = self.create_test_listings()
        
        # Test 2: Verify Admin Panel Loading
        print("\n" + "="*50)
        print("TEST 2: VERIFY ADMIN PANEL LOADING")
        print("="*50)
        loading_success = self.verify_admin_panel_loading()
        
        # Test 3: Test Bulk Delete Persistence
        print("\n" + "="*50)
        print("TEST 3: TEST BULK DELETE PERSISTENCE")
        print("="*50)
        delete_success = self.test_bulk_delete_persistence()
        
        # Test 4: Test Admin Panel Consistency
        print("\n" + "="*50)
        print("TEST 4: TEST ADMIN PANEL CONSISTENCY")
        print("="*50)
        consistency_success = self.test_admin_panel_consistency()
        
        # Test 5: Test Backend vs Frontend Consistency
        print("\n" + "="*50)
        print("TEST 5: BACKEND VS FRONTEND CONSISTENCY")
        print("="*50)
        cross_consistency_success = self.test_backend_vs_frontend_consistency()
        
        # Summary
        print("\n" + "="*70)
        print("ADMIN PANEL FALLBACK FIX TEST RESULTS")
        print("="*70)
        
        test_results = [
            ("Create Test Listings", create_success),
            ("Admin Panel Loading", loading_success),
            ("Bulk Delete Persistence", delete_success),
            ("Admin Panel Consistency", consistency_success),
            ("Backend vs Frontend Consistency", cross_consistency_success)
        ]
        
        passed_tests = sum(1 for _, success in test_results if success)
        total_tests = len(test_results)
        
        for test_name, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} major tests passed")
        print(f"📊 Individual Assertions: {self.tests_passed}/{self.tests_run} assertions passed")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL ADMIN PANEL FALLBACK FIX TESTS PASSED!")
            print("✅ The fix ensures deleted listings stay deleted and don't reappear due to fallback data")
            return True
        else:
            print(f"\n⚠️ {total_tests - passed_tests} major tests failed")
            print("❌ Admin panel fallback data fix may have issues")
            return False

def main():
    """Main test execution"""
    tester = AdminPanelFallbackTester()
    success = tester.run_admin_panel_fallback_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())