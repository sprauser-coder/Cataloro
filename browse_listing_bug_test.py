#!/usr/bin/env python3
"""
Cataloro Marketplace - Browse Listings Bug Fix Test
Tests the specific bug: "new listing is only pushed into the listings tab of the user, but not as listing for all in browse"

This test verifies:
1. Browse listings endpoint returns array format
2. Listing creation works correctly
3. Newly created listings appear in browse results
4. Listings are stored with "active" status
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class BrowseListingBugTester:
    def __init__(self, base_url="https://marketplace-pro-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user = None
        self.created_listing_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def make_request(self, method, endpoint, data=None):
        """Make HTTP request to API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            
            return response
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None

    def test_browse_listings_format(self):
        """Test 1: Browse listings endpoint returns array format"""
        print("\n🔍 Test 1: Browse Listings Endpoint Format")
        
        response = self.make_request('GET', 'api/marketplace/browse')
        
        if not response:
            return self.log_test("Browse Listings Request", False, "Request failed")
        
        if response.status_code != 200:
            return self.log_test("Browse Listings Status", False, f"Status: {response.status_code}")
        
        try:
            data = response.json()
            
            # Check if response is an array (list)
            if not isinstance(data, list):
                return self.log_test("Browse Listings Format", False, f"Expected array, got {type(data)}")
            
            print(f"   Found {len(data)} existing listings")
            
            # Verify each listing has required fields
            for i, listing in enumerate(data):
                if not all(key in listing for key in ['id', 'title', 'price', 'status']):
                    return self.log_test("Browse Listings Structure", False, f"Listing {i} missing required fields")
            
            return self.log_test("Browse Listings Format", True, f"Array format with {len(data)} listings")
            
        except json.JSONDecodeError:
            return self.log_test("Browse Listings JSON", False, "Invalid JSON response")

    def test_create_test_listing(self):
        """Test 2: Create a new test listing"""
        print("\n🔍 Test 2: Create Test Listing")
        
        # First, login as a test user
        login_data = {
            "email": "testuser@cataloro.com",
            "password": "test123"
        }
        
        login_response = self.make_request('POST', 'api/auth/login', login_data)
        
        if not login_response or login_response.status_code != 200:
            return self.log_test("Test User Login", False, "Could not login test user")
        
        try:
            login_result = login_response.json()
            self.test_user = login_result.get('user')
            if not self.test_user:
                return self.log_test("Test User Data", False, "No user data in login response")
            
            print(f"   Logged in as: {self.test_user.get('email', 'Unknown')}")
            
        except json.JSONDecodeError:
            return self.log_test("Login Response", False, "Invalid login response")
        
        # Create test listing
        test_listing = {
            "title": "Test Bug Fix Listing",
            "description": "This is a test listing to verify the browse bug fix. Created by automated test.",
            "price": 99.99,
            "category": "Test Category",
            "condition": "new",
            "seller_id": self.test_user['id'],
            "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"],
            "tags": ["test", "bug-fix", "automated"]
        }
        
        create_response = self.make_request('POST', 'api/listings', test_listing)
        
        if not create_response:
            return self.log_test("Create Listing Request", False, "Request failed")
        
        if create_response.status_code != 200:
            return self.log_test("Create Listing Status", False, f"Status: {create_response.status_code}, Response: {create_response.text}")
        
        try:
            create_result = create_response.json()
            
            if 'listing_id' not in create_result:
                return self.log_test("Create Listing Response", False, "No listing_id in response")
            
            self.created_listing_id = create_result['listing_id']
            
            # Verify status is active
            if create_result.get('status') != 'active':
                return self.log_test("Listing Status", False, f"Expected 'active', got '{create_result.get('status')}'")
            
            return self.log_test("Create Test Listing", True, f"Created listing ID: {self.created_listing_id}")
            
        except json.JSONDecodeError:
            return self.log_test("Create Listing JSON", False, "Invalid JSON response")

    def test_listing_appears_in_browse(self):
        """Test 3: Verify newly created listing appears in browse results"""
        print("\n🔍 Test 3: New Listing in Browse Results")
        
        if not self.created_listing_id:
            return self.log_test("Browse Check Prerequisites", False, "No listing created to check")
        
        # Wait a moment for database consistency
        import time
        time.sleep(1)
        
        response = self.make_request('GET', 'api/marketplace/browse')
        
        if not response or response.status_code != 200:
            return self.log_test("Browse After Create", False, "Could not fetch browse listings")
        
        try:
            listings = response.json()
            
            # Look for our test listing
            found_listing = None
            for listing in listings:
                if listing.get('id') == self.created_listing_id:
                    found_listing = listing
                    break
            
            if not found_listing:
                # Also check by title as fallback
                for listing in listings:
                    if listing.get('title') == "Test Bug Fix Listing":
                        found_listing = listing
                        print(f"   Found by title match (ID: {listing.get('id')})")
                        break
            
            if not found_listing:
                return self.log_test("New Listing in Browse", False, f"Test listing not found in {len(listings)} browse results")
            
            # Verify listing details
            if found_listing.get('title') != "Test Bug Fix Listing":
                return self.log_test("Listing Title", False, f"Expected 'Test Bug Fix Listing', got '{found_listing.get('title')}'")
            
            if found_listing.get('price') != 99.99:
                return self.log_test("Listing Price", False, f"Expected 99.99, got {found_listing.get('price')}")
            
            if found_listing.get('status') != 'active':
                return self.log_test("Listing Active Status", False, f"Expected 'active', got '{found_listing.get('status')}'")
            
            return self.log_test("New Listing in Browse", True, f"Found test listing with correct details")
            
        except json.JSONDecodeError:
            return self.log_test("Browse Results JSON", False, "Invalid JSON response")

    def test_listing_storage_verification(self):
        """Test 4: Verify listing storage and retrieval"""
        print("\n🔍 Test 4: Listing Storage Verification")
        
        if not self.created_listing_id:
            return self.log_test("Storage Check Prerequisites", False, "No listing created to verify")
        
        # Test direct listing retrieval
        response = self.make_request('GET', f'api/listings/{self.created_listing_id}')
        
        if not response:
            return self.log_test("Direct Listing Retrieval", False, "Request failed")
        
        if response.status_code != 200:
            return self.log_test("Direct Listing Status", False, f"Status: {response.status_code}")
        
        try:
            listing = response.json()
            
            # Verify all required fields are present and correct
            required_checks = [
                ('id', self.created_listing_id),
                ('title', 'Test Bug Fix Listing'),
                ('price', 99.99),
                ('status', 'active'),
                ('seller_id', self.test_user['id'] if self.test_user else None)
            ]
            
            for field, expected_value in required_checks:
                if expected_value is None:
                    continue
                    
                actual_value = listing.get(field)
                if actual_value != expected_value:
                    return self.log_test(f"Storage Field {field}", False, f"Expected {expected_value}, got {actual_value}")
            
            # Check if created_at timestamp exists
            if 'created_at' not in listing:
                return self.log_test("Storage Timestamp", False, "No created_at timestamp")
            
            return self.log_test("Listing Storage Verification", True, "All fields stored correctly")
            
        except json.JSONDecodeError:
            return self.log_test("Storage Verification JSON", False, "Invalid JSON response")

    def test_browse_shows_existing_listings(self):
        """Test 5: Verify browse still shows existing listings"""
        print("\n🔍 Test 5: Browse Shows Existing Listings")
        
        response = self.make_request('GET', 'api/marketplace/browse')
        
        if not response or response.status_code != 200:
            return self.log_test("Browse Existing Check", False, "Could not fetch browse listings")
        
        try:
            listings = response.json()
            
            if len(listings) == 0:
                return self.log_test("Browse Has Listings", False, "No listings found in browse")
            
            # Check for variety of listings (should have more than just our test listing)
            unique_titles = set(listing.get('title', '') for listing in listings)
            
            if len(unique_titles) < 2:
                return self.log_test("Browse Listing Variety", False, f"Only {len(unique_titles)} unique listings found")
            
            # Verify all listings have active status
            active_count = sum(1 for listing in listings if listing.get('status') == 'active')
            
            if active_count != len(listings):
                return self.log_test("Browse Active Status", False, f"Only {active_count}/{len(listings)} listings are active")
            
            return self.log_test("Browse Shows Existing Listings", True, f"{len(listings)} active listings with {len(unique_titles)} unique titles")
            
        except json.JSONDecodeError:
            return self.log_test("Browse Existing JSON", False, "Invalid JSON response")

    def cleanup_test_listing(self):
        """Clean up: Delete the test listing"""
        if not self.created_listing_id:
            return
        
        print(f"\n🧹 Cleaning up test listing: {self.created_listing_id}")
        
        response = self.make_request('DELETE', f'api/listings/{self.created_listing_id}')
        
        if response and response.status_code == 200:
            print("   ✅ Test listing cleaned up successfully")
        else:
            print("   ⚠️  Could not clean up test listing (may need manual cleanup)")

    def run_bug_fix_tests(self):
        """Run all bug fix verification tests"""
        print("🚀 Starting Browse Listings Bug Fix Verification")
        print("=" * 70)
        print("Testing: 'new listing is only pushed into the listings tab of the user, but not as listing for all in browse'")
        print("=" * 70)

        try:
            # Run all tests in sequence
            test1 = self.test_browse_listings_format()
            test2 = self.test_create_test_listing()
            test3 = self.test_listing_appears_in_browse()
            test4 = self.test_listing_storage_verification()
            test5 = self.test_browse_shows_existing_listings()

            # Print results
            print("\n" + "=" * 70)
            print(f"📊 Bug Fix Test Results: {self.tests_passed}/{self.tests_run} tests passed")
            
            if self.tests_passed == self.tests_run:
                print("🎉 BUG FIX VERIFIED: All tests passed!")
                print("✅ New listings now appear correctly in browse results")
                success = True
            else:
                print(f"❌ BUG NOT FIXED: {self.tests_run - self.tests_passed} tests failed")
                print("⚠️  New listings may not be appearing in browse results")
                success = False
            
            return success
            
        finally:
            # Always try to clean up
            self.cleanup_test_listing()

def main():
    """Main test execution"""
    tester = BrowseListingBugTester()
    success = tester.run_bug_fix_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())