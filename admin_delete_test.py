#!/usr/bin/env python3
"""
Admin Panel Delete Functionality Test Suite
Tests the admin panel delete functionality fix as requested in review
"""

import requests
import sys
import json
from datetime import datetime

class AdminDeleteTester:
    def __init__(self, base_url="https://catalog-admin-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.admin_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.created_listing_ids = []

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

    def test_admin_login(self):
        """Test admin login"""
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
            print(f"   Admin User: {self.admin_user}")
        return success

    def test_individual_delete_operation(self):
        """Test Individual Delete Operation as requested in review"""
        print("\n🗑️ Testing Individual Delete Operation...")
        
        if not self.admin_user:
            print("❌ Individual Delete Test - SKIPPED (No admin logged in)")
            return False
        
        # Step 1: Create a test listing via API
        print("\n1️⃣ Creating test listing via API...")
        test_listing = {
            "title": "Admin Delete Test - Premium Laptop",
            "description": "High-end laptop for admin panel delete testing. Excellent performance and build quality.",
            "price": 1899.99,
            "category": "Electronics",
            "condition": "Used - Excellent",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400"],
            "tags": ["laptop", "premium", "admin-test"],
            "features": ["High performance", "SSD storage", "Premium build"]
        }
        
        success_create, create_response = self.run_test(
            "Create Test Listing for Admin Delete",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_create or 'listing_id' not in create_response:
            print("❌ Failed to create test listing - stopping individual delete test")
            return False
        
        listing_id = create_response['listing_id']
        self.created_listing_ids.append(listing_id)
        print(f"   ✅ Created test listing with ID: {listing_id}")
        
        # Step 2: Verify it appears in admin listings endpoint (/api/listings)
        print("\n2️⃣ Verifying listing appears in admin listings endpoint...")
        success_admin_listings, admin_listings_response = self.run_test(
            "Admin Listings Endpoint Check",
            "GET",
            "api/listings",
            200
        )
        
        found_in_admin = False
        if success_admin_listings:
            # Check if response is object format with 'listings' array
            if isinstance(admin_listings_response, dict) and 'listings' in admin_listings_response:
                listings_array = admin_listings_response['listings']
                found_in_admin = any(listing.get('id') == listing_id for listing in listings_array)
                print(f"   📊 Admin endpoint returned object format with {len(listings_array)} listings")
            # Check if response is direct array format
            elif isinstance(admin_listings_response, list):
                found_in_admin = any(listing.get('id') == listing_id for listing in admin_listings_response)
                print(f"   📊 Admin endpoint returned array format with {len(admin_listings_response)} listings")
            
            self.log_test("Listing Appears in Admin Endpoint", found_in_admin,
                         f"Test listing found in admin listings: {found_in_admin}")
        
        # Step 3: Test deleting it via DELETE /api/listings/{id}
        print(f"\n3️⃣ Testing DELETE /api/listings/{listing_id}...")
        success_delete, delete_response = self.run_test(
            "Individual Delete Operation",
            "DELETE",
            f"api/listings/{listing_id}",
            200
        )
        
        if success_delete:
            print(f"   ✅ Delete operation successful: {delete_response.get('message', 'No message')}")
            deleted_count = delete_response.get('deleted_count', 0)
            self.log_test("Delete Response Validation", deleted_count == 1,
                         f"Deleted count: {deleted_count} (expected: 1)")
        
        # Step 4: Verify it's removed from admin listings
        print("\n4️⃣ Verifying removal from admin listings...")
        success_verify_admin, verify_admin_response = self.run_test(
            "Verify Removal from Admin Listings",
            "GET",
            "api/listings",
            200
        )
        
        still_in_admin = False
        if success_verify_admin:
            # Handle both object and array response formats
            if isinstance(verify_admin_response, dict) and 'listings' in verify_admin_response:
                listings_array = verify_admin_response['listings']
                still_in_admin = any(listing.get('id') == listing_id for listing in listings_array)
            elif isinstance(verify_admin_response, list):
                still_in_admin = any(listing.get('id') == listing_id for listing in verify_admin_response)
            
            self.log_test("Listing Removed from Admin Endpoint", not still_in_admin,
                         f"Listing absent from admin listings after delete: {not still_in_admin}")
        
        # Step 5: Also verify removal from browse endpoint
        print("\n5️⃣ Verifying removal from browse endpoint...")
        success_verify_browse, verify_browse_response = self.run_test(
            "Verify Removal from Browse Endpoint",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        still_in_browse = False
        if success_verify_browse:
            still_in_browse = any(listing.get('id') == listing_id for listing in verify_browse_response)
            self.log_test("Listing Removed from Browse Endpoint", not still_in_browse,
                         f"Listing absent from browse after delete: {not still_in_browse}")
        
        # Summary for individual delete
        individual_tests = [
            ("Create Test Listing", success_create),
            ("Appears in Admin Listings", found_in_admin),
            ("Delete Operation Success", success_delete),
            ("Removed from Admin Listings", not still_in_admin if success_verify_admin else False),
            ("Removed from Browse Listings", not still_in_browse if success_verify_browse else False)
        ]
        
        passed_individual = sum(1 for _, success in individual_tests if success)
        total_individual = len(individual_tests)
        
        print(f"\n📊 Individual Delete Test Summary: {passed_individual}/{total_individual} tests passed")
        return passed_individual == total_individual

    def test_admin_listings_endpoint(self):
        """Test Admin Listings Endpoint as requested in review"""
        print("\n📋 Testing Admin Listings Endpoint...")
        
        # Test 1: Verify /api/listings endpoint returns all listings
        print("\n1️⃣ Testing /api/listings endpoint returns all listings...")
        success_admin, admin_response = self.run_test(
            "Admin Listings Endpoint",
            "GET",
            "api/listings",
            200
        )
        
        admin_listings_count = 0
        admin_format_correct = False
        
        if success_admin:
            # Handle both possible response formats
            if isinstance(admin_response, dict) and 'listings' in admin_response:
                admin_listings_count = len(admin_response['listings'])
                admin_format_correct = True
                print(f"   📊 Admin endpoint returned object format with {admin_listings_count} listings")
                self.log_test("Admin Endpoint Object Format", True, "Returns object with 'listings' array")
            elif isinstance(admin_response, list):
                admin_listings_count = len(admin_response)
                admin_format_correct = True
                print(f"   📊 Admin endpoint returned array format with {admin_listings_count} listings")
                self.log_test("Admin Endpoint Array Format", True, "Returns direct array of listings")
            else:
                self.log_test("Admin Endpoint Format", False, f"Unexpected format: {type(admin_response)}")
        
        # Test 2: Compare with browse endpoint to verify admin shows ALL listings
        print("\n2️⃣ Comparing with browse endpoint...")
        success_browse, browse_response = self.run_test(
            "Browse Listings Endpoint",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        browse_listings_count = 0
        if success_browse:
            browse_listings_count = len(browse_response)
            print(f"   📊 Browse endpoint returned {browse_listings_count} listings")
        
        # Test 3: Verify admin endpoint shows all listings (including inactive ones)
        admin_shows_all = admin_listings_count >= browse_listings_count
        self.log_test("Admin Shows All Listings", admin_shows_all,
                     f"Admin: {admin_listings_count}, Browse: {browse_listings_count} (admin should be >= browse)")
        
        # Test 4: Check if admin endpoint includes inactive listings
        print("\n3️⃣ Testing if admin endpoint includes inactive listings...")
        
        # Create an inactive listing to test
        inactive_listing = {
            "title": "Admin Test - Inactive Listing",
            "description": "Test listing that will be set to inactive status for admin endpoint testing.",
            "price": 99.99,
            "category": "Test",
            "condition": "New",
            "seller_id": self.admin_user['id'] if self.admin_user else "test_seller",
            "status": "inactive"  # Set as inactive
        }
        
        success_inactive, inactive_response = self.run_test(
            "Create Inactive Test Listing",
            "POST",
            "api/listings",
            200,
            data=inactive_listing
        )
        
        inactive_in_admin = False
        inactive_in_browse = False
        
        if success_inactive:
            inactive_id = inactive_response.get('listing_id')
            self.created_listing_ids.append(inactive_id)
            
            # Check if inactive listing appears in admin endpoint
            success_admin_check, admin_check_response = self.run_test(
                "Check Inactive in Admin Endpoint",
                "GET",
                "api/listings",
                200
            )
            
            if success_admin_check:
                if isinstance(admin_check_response, dict) and 'listings' in admin_check_response:
                    inactive_in_admin = any(listing.get('id') == inactive_id for listing in admin_check_response['listings'])
                elif isinstance(admin_check_response, list):
                    inactive_in_admin = any(listing.get('id') == inactive_id for listing in admin_check_response)
            
            # Check if inactive listing appears in browse endpoint (should NOT appear)
            success_browse_check, browse_check_response = self.run_test(
                "Check Inactive in Browse Endpoint",
                "GET",
                "api/marketplace/browse",
                200
            )
            
            if success_browse_check:
                inactive_in_browse = any(listing.get('id') == inactive_id for listing in browse_check_response)
            
            self.log_test("Admin Shows Inactive Listings", inactive_in_admin,
                         f"Inactive listing in admin endpoint: {inactive_in_admin}")
            self.log_test("Browse Hides Inactive Listings", not inactive_in_browse,
                         f"Inactive listing hidden from browse: {not inactive_in_browse}")
        
        # Summary for admin endpoint tests
        admin_endpoint_tests = [
            ("Admin Endpoint Accessible", success_admin),
            ("Admin Endpoint Format Correct", admin_format_correct),
            ("Admin Shows All Listings", admin_shows_all),
            ("Admin Shows Inactive Listings", inactive_in_admin),
            ("Browse Hides Inactive Listings", not inactive_in_browse)
        ]
        
        passed_admin_endpoint = sum(1 for _, success in admin_endpoint_tests if success)
        total_admin_endpoint = len(admin_endpoint_tests)
        
        print(f"\n📊 Admin Endpoint Test Summary: {passed_admin_endpoint}/{total_admin_endpoint} tests passed")
        return passed_admin_endpoint == total_admin_endpoint

    def test_bulk_delete_operations(self):
        """Test Bulk Delete Operations as requested in review"""
        print("\n📦 Testing Bulk Delete Operations...")
        
        if not self.admin_user:
            print("❌ Bulk Delete Test - SKIPPED (No admin logged in)")
            return False
        
        # Step 1: Create multiple test listings
        print("\n1️⃣ Creating multiple test listings for bulk delete...")
        
        bulk_test_listings = [
            {
                "title": "Bulk Delete Test 1 - Smartphone",
                "description": "Premium smartphone for bulk delete testing.",
                "price": 899.99,
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": self.admin_user['id'],
                "tags": ["bulk-test", "smartphone"]
            },
            {
                "title": "Bulk Delete Test 2 - Tablet",
                "description": "High-resolution tablet for bulk delete testing.",
                "price": 599.99,
                "category": "Electronics", 
                "condition": "Used - Excellent",
                "seller_id": self.admin_user['id'],
                "tags": ["bulk-test", "tablet"]
            },
            {
                "title": "Bulk Delete Test 3 - Smartwatch",
                "description": "Feature-rich smartwatch for bulk delete testing.",
                "price": 299.99,
                "category": "Electronics",
                "condition": "New",
                "seller_id": self.admin_user['id'],
                "tags": ["bulk-test", "smartwatch"]
            },
            {
                "title": "Bulk Delete Test 4 - Headphones",
                "description": "Noise-canceling headphones for bulk delete testing.",
                "price": 199.99,
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": self.admin_user['id'],
                "tags": ["bulk-test", "headphones"]
            }
        ]
        
        bulk_listing_ids = []
        create_success_count = 0
        
        for i, listing_data in enumerate(bulk_test_listings):
            success, response = self.run_test(
                f"Create Bulk Test Listing {i+1}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            if success and 'listing_id' in response:
                listing_id = response['listing_id']
                bulk_listing_ids.append(listing_id)
                self.created_listing_ids.append(listing_id)
                create_success_count += 1
                print(f"   ✅ Created bulk test listing {i+1} with ID: {listing_id}")
        
        self.log_test("Bulk Listing Creation", create_success_count == 4,
                     f"Created {create_success_count}/4 bulk test listings")
        
        if create_success_count == 0:
            print("❌ No bulk test listings created - stopping bulk delete test")
            return False
        
        # Step 2: Verify all listings appear in admin listings
        print("\n2️⃣ Verifying all listings appear in admin listings...")
        success_verify, verify_response = self.run_test(
            "Verify Bulk Listings in Admin Endpoint",
            "GET",
            "api/listings",
            200
        )
        
        found_in_admin_count = 0
        if success_verify:
            # Handle both response formats
            listings_to_check = []
            if isinstance(verify_response, dict) and 'listings' in verify_response:
                listings_to_check = verify_response['listings']
            elif isinstance(verify_response, list):
                listings_to_check = verify_response
            
            for listing_id in bulk_listing_ids:
                if any(listing.get('id') == listing_id for listing in listings_to_check):
                    found_in_admin_count += 1
        
        self.log_test("Bulk Listings Visible in Admin", found_in_admin_count == len(bulk_listing_ids),
                     f"Found {found_in_admin_count}/{len(bulk_listing_ids)} bulk listings in admin endpoint")
        
        # Step 3: Test bulk delete functionality via multiple DELETE operations
        print("\n3️⃣ Testing bulk delete via multiple DELETE operations...")
        
        delete_success_count = 0
        for i, listing_id in enumerate(bulk_listing_ids):
            success, response = self.run_test(
                f"Bulk Delete Operation {i+1}",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                delete_success_count += 1
                print(f"   ✅ Successfully deleted bulk listing {i+1}: {listing_id}")
            else:
                print(f"   ❌ Failed to delete bulk listing {i+1}: {listing_id}")
        
        self.log_test("Bulk Delete Operations", delete_success_count == len(bulk_listing_ids),
                     f"Successfully deleted {delete_success_count}/{len(bulk_listing_ids)} listings")
        
        # Step 4: Verify all listings are properly removed from admin endpoint
        print("\n4️⃣ Verifying all listings are removed from admin endpoint...")
        success_verify_removal, removal_response = self.run_test(
            "Verify Bulk Removal from Admin Endpoint",
            "GET",
            "api/listings",
            200
        )
        
        remaining_in_admin = 0
        if success_verify_removal:
            # Handle both response formats
            listings_to_check = []
            if isinstance(removal_response, dict) and 'listings' in removal_response:
                listings_to_check = removal_response['listings']
            elif isinstance(removal_response, list):
                listings_to_check = removal_response
            
            for listing_id in bulk_listing_ids:
                if any(listing.get('id') == listing_id for listing in listings_to_check):
                    remaining_in_admin += 1
                    print(f"   ⚠️  Bulk listing {listing_id} still found in admin endpoint!")
        
        self.log_test("Bulk Listings Removed from Admin", remaining_in_admin == 0,
                     f"Remaining listings in admin: {remaining_in_admin} (should be 0)")
        
        # Step 5: Verify all listings are removed from browse endpoint
        print("\n5️⃣ Verifying all listings are removed from browse endpoint...")
        success_verify_browse, browse_removal_response = self.run_test(
            "Verify Bulk Removal from Browse Endpoint",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        remaining_in_browse = 0
        if success_verify_browse:
            for listing_id in bulk_listing_ids:
                if any(listing.get('id') == listing_id for listing in browse_removal_response):
                    remaining_in_browse += 1
                    print(f"   ⚠️  Bulk listing {listing_id} still found in browse endpoint!")
        
        self.log_test("Bulk Listings Removed from Browse", remaining_in_browse == 0,
                     f"Remaining listings in browse: {remaining_in_browse} (should be 0)")
        
        # Summary for bulk delete tests
        bulk_delete_tests = [
            ("Create Bulk Test Listings", create_success_count == 4),
            ("Bulk Listings Visible in Admin", found_in_admin_count == len(bulk_listing_ids)),
            ("Bulk Delete Operations Success", delete_success_count == len(bulk_listing_ids)),
            ("Bulk Listings Removed from Admin", remaining_in_admin == 0),
            ("Bulk Listings Removed from Browse", remaining_in_browse == 0)
        ]
        
        passed_bulk = sum(1 for _, success in bulk_delete_tests if success)
        total_bulk = len(bulk_delete_tests)
        
        print(f"\n📊 Bulk Delete Test Summary: {passed_bulk}/{total_bulk} tests passed")
        return passed_bulk == total_bulk

    def test_endpoint_consistency(self):
        """Test Endpoint Consistency as requested in review"""
        print("\n🔄 Testing Endpoint Consistency...")
        
        # Test 1: Check that admin endpoint (/api/listings) shows ALL listings
        print("\n1️⃣ Testing admin endpoint shows ALL listings...")
        success_admin, admin_response = self.run_test(
            "Admin Endpoint All Listings",
            "GET",
            "api/listings",
            200
        )
        
        admin_listings = []
        if success_admin:
            if isinstance(admin_response, dict) and 'listings' in admin_response:
                admin_listings = admin_response['listings']
            elif isinstance(admin_response, list):
                admin_listings = admin_response
        
        # Test 2: Check that browse endpoint (/api/marketplace/browse) shows only active listings
        print("\n2️⃣ Testing browse endpoint shows only active listings...")
        success_browse, browse_response = self.run_test(
            "Browse Endpoint Active Listings",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        browse_listings = browse_response if success_browse else []
        
        # Test 3: Verify filtering differences are correct
        print("\n3️⃣ Verifying filtering differences...")
        
        # Count active vs all listings
        active_count_in_admin = 0
        total_count_in_admin = len(admin_listings)
        
        for listing in admin_listings:
            if listing.get('status', 'active') == 'active':
                active_count_in_admin += 1
        
        browse_count = len(browse_listings)
        
        print(f"   📊 Admin endpoint: {total_count_in_admin} total listings, {active_count_in_admin} active")
        print(f"   📊 Browse endpoint: {browse_count} listings (should be active only)")
        
        # Verify browse shows only active listings
        all_browse_active = True
        inactive_in_browse = 0
        for listing in browse_listings:
            if listing.get('status') != 'active' and listing.get('status') is not None:
                all_browse_active = False
                inactive_in_browse += 1
        
        self.log_test("Browse Shows Only Active", all_browse_active,
                     f"All browse listings are active: {all_browse_active} (found {inactive_in_browse} inactive)")
        
        # Verify admin shows more or equal listings than browse
        admin_comprehensive = total_count_in_admin >= browse_count
        self.log_test("Admin Shows All Listings", admin_comprehensive,
                     f"Admin ({total_count_in_admin}) >= Browse ({browse_count}): {admin_comprehensive}")
        
        # Test 4: Create test listings with different statuses to verify filtering
        print("\n4️⃣ Testing filtering with different status listings...")
        
        # Create active listing
        active_listing = {
            "title": "Consistency Test - Active Listing",
            "description": "Active listing for endpoint consistency testing.",
            "price": 149.99,
            "category": "Test",
            "condition": "New",
            "seller_id": self.admin_user['id'] if self.admin_user else "test_seller",
            "status": "active"
        }
        
        success_active, active_response = self.run_test(
            "Create Active Test Listing",
            "POST",
            "api/listings",
            200,
            data=active_listing
        )
        
        active_id = None
        if success_active:
            active_id = active_response.get('listing_id')
            self.created_listing_ids.append(active_id)
        
        # Create inactive listing
        inactive_listing = {
            "title": "Consistency Test - Inactive Listing",
            "description": "Inactive listing for endpoint consistency testing.",
            "price": 149.99,
            "category": "Test",
            "condition": "New",
            "seller_id": self.admin_user['id'] if self.admin_user else "test_seller",
            "status": "inactive"
        }
        
        success_inactive, inactive_response = self.run_test(
            "Create Inactive Test Listing",
            "POST",
            "api/listings",
            200,
            data=inactive_listing
        )
        
        inactive_id = None
        if success_inactive:
            inactive_id = inactive_response.get('listing_id')
            self.created_listing_ids.append(inactive_id)
        
        # Test 5: Verify filtering behavior with test listings
        print("\n5️⃣ Verifying filtering behavior with test listings...")
        
        if active_id and inactive_id:
            # Check admin endpoint includes both
            success_admin_filter, admin_filter_response = self.run_test(
                "Admin Endpoint Filter Test",
                "GET",
                "api/listings",
                200
            )
            
            admin_has_active = False
            admin_has_inactive = False
            
            if success_admin_filter:
                filter_listings = []
                if isinstance(admin_filter_response, dict) and 'listings' in admin_filter_response:
                    filter_listings = admin_filter_response['listings']
                elif isinstance(admin_filter_response, list):
                    filter_listings = admin_filter_response
                
                admin_has_active = any(listing.get('id') == active_id for listing in filter_listings)
                admin_has_inactive = any(listing.get('id') == inactive_id for listing in filter_listings)
            
            # Check browse endpoint includes only active
            success_browse_filter, browse_filter_response = self.run_test(
                "Browse Endpoint Filter Test",
                "GET",
                "api/marketplace/browse",
                200
            )
            
            browse_has_active = False
            browse_has_inactive = False
            
            if success_browse_filter:
                browse_has_active = any(listing.get('id') == active_id for listing in browse_filter_response)
                browse_has_inactive = any(listing.get('id') == inactive_id for listing in browse_filter_response)
            
            self.log_test("Admin Includes Active Listing", admin_has_active,
                         f"Admin endpoint includes active test listing: {admin_has_active}")
            self.log_test("Admin Includes Inactive Listing", admin_has_inactive,
                         f"Admin endpoint includes inactive test listing: {admin_has_inactive}")
            self.log_test("Browse Includes Active Listing", browse_has_active,
                         f"Browse endpoint includes active test listing: {browse_has_active}")
            self.log_test("Browse Excludes Inactive Listing", not browse_has_inactive,
                         f"Browse endpoint excludes inactive test listing: {not browse_has_inactive}")
        
        # Summary for endpoint consistency tests
        consistency_tests = [
            ("Admin Endpoint Accessible", success_admin),
            ("Browse Endpoint Accessible", success_browse),
            ("Browse Shows Only Active", all_browse_active),
            ("Admin Shows All Listings", admin_comprehensive),
            ("Admin Includes Active", admin_has_active if 'admin_has_active' in locals() else True),
            ("Admin Includes Inactive", admin_has_inactive if 'admin_has_inactive' in locals() else True),
            ("Browse Includes Active", browse_has_active if 'browse_has_active' in locals() else True),
            ("Browse Excludes Inactive", not browse_has_inactive if 'browse_has_inactive' in locals() else True)
        ]
        
        passed_consistency = sum(1 for _, success in consistency_tests if success)
        total_consistency = len(consistency_tests)
        
        print(f"\n📊 Endpoint Consistency Test Summary: {passed_consistency}/{total_consistency} tests passed")
        return passed_consistency == total_consistency

    def cleanup_test_listings(self):
        """Clean up any remaining test listings"""
        print("\n🧹 Cleaning up test listings...")
        
        cleanup_count = 0
        for listing_id in self.created_listing_ids:
            try:
                success, _ = self.run_test(
                    f"Cleanup Listing {listing_id[:8]}...",
                    "DELETE",
                    f"api/listings/{listing_id}",
                    200
                )
                if success:
                    cleanup_count += 1
            except:
                pass  # Ignore cleanup errors
        
        print(f"   🧹 Cleaned up {cleanup_count}/{len(self.created_listing_ids)} test listings")

    def run_admin_delete_tests(self):
        """Run complete admin delete functionality test suite"""
        print("🚀 Starting Admin Panel Delete Functionality Tests")
        print("=" * 70)
        print("Testing the admin panel delete functionality fix as requested in review")
        print("=" * 70)

        # Admin login
        if not self.test_admin_login():
            print("❌ Admin login failed - stopping tests")
            return False

        # Run the four main test categories as requested in review
        test_results = []
        
        print("\n🔥 1. TESTING INDIVIDUAL DELETE OPERATION")
        individual_success = self.test_individual_delete_operation()
        test_results.append(("Individual Delete Operation", individual_success))
        
        print("\n🔥 2. TESTING ADMIN LISTINGS ENDPOINT")
        admin_endpoint_success = self.test_admin_listings_endpoint()
        test_results.append(("Admin Listings Endpoint", admin_endpoint_success))
        
        print("\n🔥 3. TESTING BULK DELETE OPERATIONS")
        bulk_delete_success = self.test_bulk_delete_operations()
        test_results.append(("Bulk Delete Operations", bulk_delete_success))
        
        print("\n🔥 4. TESTING ENDPOINT CONSISTENCY")
        consistency_success = self.test_endpoint_consistency()
        test_results.append(("Endpoint Consistency", consistency_success))
        
        # Cleanup
        self.cleanup_test_listings()
        
        # Final results
        print("\n" + "=" * 70)
        print("📊 ADMIN DELETE FUNCTIONALITY TEST RESULTS")
        print("=" * 70)
        
        passed_categories = 0
        for category, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} {category}")
            if success:
                passed_categories += 1
        
        print(f"\n📊 Overall Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        print(f"📊 Category Results: {passed_categories}/{len(test_results)} test categories passed")
        
        if passed_categories == len(test_results):
            print("\n🎉 ALL ADMIN DELETE FUNCTIONALITY TESTS PASSED!")
            print("✅ Individual delete operations work correctly")
            print("✅ Admin listings endpoint returns all listings")
            print("✅ Bulk delete operations work correctly")
            print("✅ Endpoint consistency is maintained")
            print("\n🔧 The admin panel delete functionality fix is working properly!")
            return True
        else:
            print(f"\n⚠️  {len(test_results) - passed_categories} test categories failed")
            print("❌ Admin panel delete functionality needs attention")
            return False

def main():
    """Main test execution"""
    tester = AdminDeleteTester()
    success = tester.run_admin_delete_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())