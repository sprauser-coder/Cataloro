#!/usr/bin/env python3
"""
Cataloro Marketplace - Demo Data Creation Fix Test
Tests the fix for automatic demo data creation when database is empty
"""

import requests
import sys
import json
import time
from datetime import datetime

class DemoDataFixTester:
    def __init__(self, base_url="https://browse-ads.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.deleted_listing_ids = []

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

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("🔐 Setting up authentication...")
        
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
            print(f"   Admin User: {self.admin_user}")

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
            print(f"   Regular User: {self.regular_user}")

        return self.admin_user is not None and self.regular_user is not None

    def get_all_listings(self):
        """Get all current listings from /api/listings endpoint"""
        print("\n📋 Getting all current listings...")
        
        success, response = self.run_test(
            "Get All Listings",
            "GET",
            "api/listings",
            200
        )
        
        if success and 'listings' in response:
            listings = response['listings']
            print(f"   Found {len(listings)} listings in /api/listings")
            return listings
        elif success and isinstance(response, list):
            print(f"   Found {len(response)} listings in /api/listings (array format)")
            return response
        else:
            print("   No listings found or error occurred")
            return []

    def get_browse_listings(self):
        """Get all current listings from /api/marketplace/browse endpoint"""
        print("\n🌐 Getting all browse listings...")
        
        success, response = self.run_test(
            "Get Browse Listings",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} listings in /api/marketplace/browse")
            return response
        else:
            print("   No listings found or error occurred")
            return []

    def delete_all_listings(self):
        """Delete all existing listings one by one"""
        print("\n🗑️ Deleting all existing listings...")
        
        # Get all listings first
        all_listings = self.get_all_listings()
        browse_listings = self.get_browse_listings()
        
        # Combine and deduplicate listings by ID
        all_listing_ids = set()
        
        # Add IDs from /api/listings
        for listing in all_listings:
            if 'id' in listing:
                all_listing_ids.add(listing['id'])
        
        # Add IDs from /api/marketplace/browse
        for listing in browse_listings:
            if 'id' in listing:
                all_listing_ids.add(listing['id'])
        
        print(f"   Total unique listings to delete: {len(all_listing_ids)}")
        
        if not all_listing_ids:
            print("   No listings to delete")
            return True
        
        # Delete each listing
        successful_deletions = 0
        failed_deletions = 0
        
        for listing_id in all_listing_ids:
            print(f"\n   Deleting listing: {listing_id}")
            success, response = self.run_test(
                f"Delete Listing {listing_id[:8]}...",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            
            if success:
                successful_deletions += 1
                self.deleted_listing_ids.append(listing_id)
                deleted_count = response.get('deleted_count', 0)
                print(f"     ✅ Deleted successfully (deleted_count: {deleted_count})")
            else:
                failed_deletions += 1
                print(f"     ❌ Failed to delete")
        
        print(f"\n📊 Deletion Summary:")
        print(f"   Successful deletions: {successful_deletions}")
        print(f"   Failed deletions: {failed_deletions}")
        
        self.log_test("Delete All Listings", failed_deletions == 0, 
                     f"Deleted {successful_deletions}/{len(all_listing_ids)} listings")
        
        return failed_deletions == 0

    def verify_empty_database(self):
        """Verify that both endpoints return empty arrays after deletion"""
        print("\n🔍 Verifying empty database state...")
        
        # Test /api/marketplace/browse
        success_browse, browse_response = self.run_test(
            "Browse Listings (Should be Empty)",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        browse_empty = False
        if success_browse:
            if isinstance(browse_response, list):
                browse_empty = len(browse_response) == 0
                print(f"   /api/marketplace/browse returned {len(browse_response)} listings")
            else:
                print(f"   /api/marketplace/browse returned unexpected format: {type(browse_response)}")
        
        # Test /api/listings
        success_listings, listings_response = self.run_test(
            "Admin Listings (Should be Empty)",
            "GET",
            "api/listings",
            200
        )
        
        listings_empty = False
        if success_listings:
            if 'listings' in listings_response:
                listings_count = len(listings_response['listings'])
                listings_empty = listings_count == 0
                print(f"   /api/listings returned {listings_count} listings")
            elif isinstance(listings_response, list):
                listings_count = len(listings_response)
                listings_empty = listings_count == 0
                print(f"   /api/listings returned {listings_count} listings (array format)")
            else:
                print(f"   /api/listings returned unexpected format: {type(listings_response)}")
        
        self.log_test("Browse Endpoint Empty", browse_empty, 
                     f"/api/marketplace/browse returns empty array: {browse_empty}")
        self.log_test("Listings Endpoint Empty", listings_empty, 
                     f"/api/listings returns empty results: {listings_empty}")
        
        return browse_empty and listings_empty

    def test_multiple_api_calls(self):
        """Test multiple API calls to ensure no demo data is created"""
        print("\n🔄 Testing multiple API calls to ensure no demo data creation...")
        
        # Call browse endpoint multiple times
        for i in range(5):
            print(f"\n   Call {i+1}/5 to /api/marketplace/browse...")
            success, response = self.run_test(
                f"Browse Call {i+1}",
                "GET",
                "api/marketplace/browse",
                200
            )
            
            if success and isinstance(response, list):
                if len(response) > 0:
                    print(f"     ❌ Found {len(response)} listings - demo data may have been created!")
                    self.log_test(f"No Demo Data Call {i+1}", False, 
                                 f"Found {len(response)} listings on call {i+1}")
                    return False
                else:
                    print(f"     ✅ Still empty ({len(response)} listings)")
            else:
                print(f"     ❌ API call failed or unexpected response")
                return False
            
            # Small delay between calls
            time.sleep(0.5)
        
        # Call admin listings endpoint multiple times
        for i in range(3):
            print(f"\n   Call {i+1}/3 to /api/listings...")
            success, response = self.run_test(
                f"Admin Listings Call {i+1}",
                "GET",
                "api/listings",
                200
            )
            
            if success:
                listings_count = 0
                if 'listings' in response:
                    listings_count = len(response['listings'])
                elif isinstance(response, list):
                    listings_count = len(response)
                
                if listings_count > 0:
                    print(f"     ❌ Found {listings_count} listings - demo data may have been created!")
                    self.log_test(f"No Demo Data Admin Call {i+1}", False, 
                                 f"Found {listings_count} listings on admin call {i+1}")
                    return False
                else:
                    print(f"     ✅ Still empty ({listings_count} listings)")
            else:
                print(f"     ❌ API call failed")
                return False
            
            # Small delay between calls
            time.sleep(0.5)
        
        self.log_test("Multiple API Calls No Demo Data", True, 
                     "No demo data created after 8 API calls")
        return True

    def test_persistence_verification(self):
        """Test that empty state persists across different operations"""
        print("\n🔒 Testing persistence verification...")
        
        # Test refresh operations by calling different endpoints
        endpoints_to_test = [
            ("api/marketplace/browse", "Browse Listings"),
            ("api/listings", "Admin Listings"),
        ]
        
        if self.regular_user:
            endpoints_to_test.append((f"api/user/my-listings/{self.regular_user['id']}", "My Listings"))
        
        all_empty = True
        
        for endpoint, name in endpoints_to_test:
            print(f"\n   Testing {name} endpoint...")
            success, response = self.run_test(
                f"Persistence Check - {name}",
                "GET",
                endpoint,
                200
            )
            
            if success:
                count = 0
                if isinstance(response, list):
                    count = len(response)
                elif 'listings' in response:
                    count = len(response['listings'])
                
                if count > 0:
                    print(f"     ❌ Found {count} listings in {name}")
                    all_empty = False
                else:
                    print(f"     ✅ {name} is empty ({count} listings)")
            else:
                print(f"     ❌ Failed to check {name}")
                all_empty = False
        
        self.log_test("Persistence Verification", all_empty, 
                     f"All endpoints remain empty: {all_empty}")
        return all_empty

    def run_demo_data_fix_test(self):
        """Run the complete demo data creation fix test"""
        print("🚀 Starting Demo Data Creation Fix Test")
        print("=" * 60)
        print("Testing that automatic demo listings are NOT created when database is empty")
        print("=" * 60)

        # Step 1: Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return False

        # Step 2: Delete all existing listings
        print(f"\n{'='*60}")
        print("STEP 1: DELETE ALL EXISTING LISTINGS")
        print(f"{'='*60}")
        
        if not self.delete_all_listings():
            print("❌ Failed to delete all listings - stopping tests")
            return False

        # Step 3: Verify empty database behavior
        print(f"\n{'='*60}")
        print("STEP 2: TEST EMPTY DATABASE BEHAVIOR")
        print(f"{'='*60}")
        
        if not self.verify_empty_database():
            print("❌ Database is not empty after deletions - test failed")
            return False

        # Step 4: Test multiple API calls
        print(f"\n{'='*60}")
        print("STEP 3: TEST MULTIPLE API CALLS (NO AUTO-CREATION)")
        print(f"{'='*60}")
        
        if not self.test_multiple_api_calls():
            print("❌ Demo data was created during multiple API calls - test failed")
            return False

        # Step 5: Test persistence verification
        print(f"\n{'='*60}")
        print("STEP 4: PERSISTENCE VERIFICATION")
        print(f"{'='*60}")
        
        if not self.test_persistence_verification():
            print("❌ Empty state did not persist - test failed")
            return False

        # Final verification
        print(f"\n{'='*60}")
        print("FINAL VERIFICATION")
        print(f"{'='*60}")
        
        final_browse_success, final_browse_response = self.run_test(
            "Final Browse Check",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        final_admin_success, final_admin_response = self.run_test(
            "Final Admin Check",
            "GET",
            "api/listings",
            200
        )
        
        final_success = True
        if final_browse_success and isinstance(final_browse_response, list):
            if len(final_browse_response) > 0:
                print(f"❌ FINAL CHECK FAILED: Found {len(final_browse_response)} listings in browse")
                final_success = False
            else:
                print(f"✅ FINAL CHECK PASSED: Browse endpoint is empty")
        
        if final_admin_success:
            admin_count = 0
            if 'listings' in final_admin_response:
                admin_count = len(final_admin_response['listings'])
            elif isinstance(final_admin_response, list):
                admin_count = len(final_admin_response)
            
            if admin_count > 0:
                print(f"❌ FINAL CHECK FAILED: Found {admin_count} listings in admin")
                final_success = False
            else:
                print(f"✅ FINAL CHECK PASSED: Admin endpoint is empty")

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"🗑️ Deleted Listings: {len(self.deleted_listing_ids)}")
        
        if final_success and self.tests_passed == self.tests_run:
            print("🎉 DEMO DATA FIX VERIFIED SUCCESSFULLY!")
            print("✅ No automatic demo listings are created when database is empty")
            print("✅ Empty database returns empty arrays consistently")
            print("✅ Multiple API calls do not trigger demo data creation")
            print("✅ Empty state persists across different operations")
            return True
        else:
            print(f"⚠️ DEMO DATA FIX TEST FAILED!")
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            if not final_success:
                print("❌ Final verification failed - listings found when database should be empty")
            return False

def main():
    """Main test execution"""
    tester = DemoDataFixTester()
    success = tester.run_demo_data_fix_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())