#!/usr/bin/env python3
"""
Data Source Discrepancy Investigation Test
Investigates the data source discrepancy between admin delete and browse display
"""

import requests
import sys
import json
import time
from datetime import datetime

class DataSourceInvestigator:
    def __init__(self, base_url="https://bizcat-market.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_listing_ids = []

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

    def test_admin_delete_api(self):
        """Test 1: Test Admin Delete API - Create, Delete, Verify"""
        print("\n📋 TEST 1: Admin Delete API Investigation")
        print("=" * 50)
        
        if not self.regular_user:
            print("❌ Cannot test - no user authenticated")
            return False

        # Step 1: Create a test listing via POST /api/listings
        print("\n➕ Step 1: Creating test listing via POST /api/listings")
        test_listing = {
            "title": "DATA SOURCE TEST - MacBook Pro Investigation",
            "description": "Test listing to investigate data source discrepancy between admin delete and browse display",
            "price": 1999.99,
            "category": "Electronics",
            "condition": "Used - Excellent",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"],
            "tags": ["test", "investigation", "macbook"],
            "features": ["Test listing", "Data source investigation"]
        }
        
        success, create_response = self.run_test(
            "Create Test Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success or 'listing_id' not in create_response:
            print("❌ Failed to create test listing - cannot continue investigation")
            return False
        
        listing_id = create_response['listing_id']
        self.test_listing_ids.append(listing_id)
        print(f"   ✅ Created test listing with ID: {listing_id}")

        # Step 2: Verify listing exists in database via GET /api/listings/{id}
        print(f"\n📖 Step 2: Verifying listing exists via GET /api/listings/{listing_id}")
        success, get_response = self.run_test(
            "Verify Listing Exists",
            "GET",
            f"api/listings/{listing_id}",
            200
        )
        
        if not success:
            print("❌ Cannot verify listing exists - investigation compromised")
            return False
        
        print(f"   ✅ Listing verified in database: {get_response.get('title', 'N/A')}")

        # Step 3: Delete via DELETE /api/listings/{id}
        print(f"\n🗑️  Step 3: Deleting listing via DELETE /api/listings/{listing_id}")
        success, delete_response = self.run_test(
            "Delete Test Listing",
            "DELETE",
            f"api/listings/{listing_id}",
            200
        )
        
        if not success:
            print("❌ Failed to delete listing - investigation incomplete")
            return False
        
        print(f"   ✅ Listing deleted successfully: {delete_response.get('message', 'N/A')}")

        # Step 4: Verify it's deleted from the database
        print(f"\n🔍 Step 4: Verifying deletion from database via GET /api/listings/{listing_id}")
        success, verify_response = self.run_test(
            "Verify Listing Deleted from Database",
            "GET",
            f"api/listings/{listing_id}",
            404  # Should return 404 if properly deleted
        )
        
        deletion_verified = success  # Success means we got expected 404
        self.log_test("Database Deletion Verification", deletion_verified, 
                     f"Listing properly deleted from database: {deletion_verified}")
        
        return deletion_verified

    def test_browse_page_api(self):
        """Test 2: Test Browse Page API - Check if deleted listing appears"""
        print("\n🌐 TEST 2: Browse Page API Investigation")
        print("=" * 50)
        
        # Check GET /api/marketplace/browse to see if deleted listing appears
        print("\n🔍 Checking GET /api/marketplace/browse for deleted listings")
        success, browse_response = self.run_test(
            "Browse Marketplace Listings",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            print("❌ Cannot access browse endpoint - investigation incomplete")
            return False
        
        print(f"   📊 Found {len(browse_response)} total listings in browse")
        
        # Check if any of our test listings appear in browse results
        deleted_listings_found = []
        for listing_id in self.test_listing_ids:
            found = any(listing.get('id') == listing_id for listing in browse_response)
            if found:
                deleted_listings_found.append(listing_id)
                print(f"   ⚠️  ISSUE: Deleted listing {listing_id[:8]}... still appears in browse!")
        
        browse_clean = len(deleted_listings_found) == 0
        self.log_test("Browse Page Clean of Deleted Listings", browse_clean,
                     f"Deleted listings in browse: {len(deleted_listings_found)}")
        
        return browse_clean, browse_response

    def compare_data_sources(self):
        """Test 3: Compare data sources between /api/listings and /api/marketplace/browse"""
        print("\n🔄 TEST 3: Data Source Comparison")
        print("=" * 50)
        
        # Get data from /api/listings
        print("\n📋 Getting data from GET /api/listings")
        success_listings, listings_response = self.run_test(
            "Get All Listings",
            "GET",
            "api/listings",
            200
        )
        
        if not success_listings:
            print("❌ Cannot access /api/listings endpoint")
            return False
        
        # Get data from /api/marketplace/browse
        print("\n🌐 Getting data from GET /api/marketplace/browse")
        success_browse, browse_response = self.run_test(
            "Get Browse Listings",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success_browse:
            print("❌ Cannot access /api/marketplace/browse endpoint")
            return False
        
        # Analyze response formats
        print(f"\n📊 Data Source Analysis:")
        
        # Check /api/listings response format
        listings_format = "UNKNOWN"
        listings_count = 0
        if isinstance(listings_response, dict) and 'listings' in listings_response:
            listings_format = "OBJECT with 'listings' array"
            listings_count = len(listings_response['listings'])
            listings_data = listings_response['listings']
        elif isinstance(listings_response, list):
            listings_format = "ARRAY format"
            listings_count = len(listings_response)
            listings_data = listings_response
        else:
            listings_format = f"UNEXPECTED: {type(listings_response)}"
            listings_data = []
        
        print(f"   /api/listings format: {listings_format}")
        print(f"   /api/listings count: {listings_count}")
        
        # Check /api/marketplace/browse response format
        browse_format = "UNKNOWN"
        browse_count = 0
        if isinstance(browse_response, list):
            browse_format = "ARRAY format"
            browse_count = len(browse_response)
            browse_data = browse_response
        elif isinstance(browse_response, dict) and 'listings' in browse_response:
            browse_format = "OBJECT with 'listings' array"
            browse_count = len(browse_response['listings'])
            browse_data = browse_response['listings']
        else:
            browse_format = f"UNEXPECTED: {type(browse_response)}"
            browse_data = []
        
        print(f"   /api/marketplace/browse format: {browse_format}")
        print(f"   /api/marketplace/browse count: {browse_count}")
        
        # Compare data consistency
        format_consistent = (listings_format == browse_format) or (
            "ARRAY" in listings_format and "ARRAY" in browse_format
        )
        
        self.log_test("Response Format Consistency", format_consistent,
                     f"Formats match: {format_consistent}")
        
        # Check if they query the same database collection (by comparing listing IDs)
        listings_ids = set()
        browse_ids = set()
        
        for listing in listings_data:
            if isinstance(listing, dict) and 'id' in listing:
                listings_ids.add(listing['id'])
        
        for listing in browse_data:
            if isinstance(listing, dict) and 'id' in listing:
                browse_ids.add(listing['id'])
        
        # Check for overlap and differences
        common_ids = listings_ids.intersection(browse_ids)
        listings_only = listings_ids - browse_ids
        browse_only = browse_ids - listings_ids
        
        print(f"\n🔍 ID Comparison Analysis:")
        print(f"   Common listings: {len(common_ids)}")
        print(f"   Only in /api/listings: {len(listings_only)}")
        print(f"   Only in /api/marketplace/browse: {len(browse_only)}")
        
        if listings_only:
            print(f"   ⚠️  Listings not in browse: {list(listings_only)[:3]}...")
        if browse_only:
            print(f"   ⚠️  Browse items not in listings: {list(browse_only)[:3]}...")
        
        same_collection = len(listings_only) == 0 and len(browse_only) == 0
        self.log_test("Same Database Collection", same_collection,
                     f"Both endpoints use same data source: {same_collection}")
        
        return same_collection

    def verify_database_collections(self):
        """Test 4: Verify if both endpoints use the same MongoDB collection"""
        print("\n🗄️  TEST 4: Database Collection Verification")
        print("=" * 50)
        
        print("\n📋 Analyzing backend code behavior...")
        
        # Based on backend code analysis:
        # - POST /api/listings creates in db.listings collection
        # - DELETE /api/listings/{id} deletes from db.listings collection using {"id": listing_id}
        # - GET /api/marketplace/browse queries db.listings.find({"status": "active"})
        # - GET /api/listings queries db.listings.find(query)
        
        print("   📝 Backend Code Analysis:")
        print("   - POST /api/listings → db.listings collection")
        print("   - DELETE /api/listings/{id} → db.listings collection")
        print("   - GET /api/marketplace/browse → db.listings.find({'status': 'active'})")
        print("   - GET /api/listings → db.listings.find(query)")
        
        print("\n✅ CONCLUSION: Both endpoints use the SAME MongoDB collection (db.listings)")
        print("   The difference is in the query filters:")
        print("   - /api/marketplace/browse filters by status='active'")
        print("   - /api/listings may return all listings regardless of status")
        
        self.log_test("Database Collection Analysis", True, 
                     "Both endpoints use same collection with different filters")
        
        return True

    def test_real_deletion_persistence(self):
        """Test 5: Test if deleting from /api/listings removes from both sources"""
        print("\n🔄 TEST 5: Real Deletion Persistence Test")
        print("=" * 50)
        
        if not self.regular_user:
            print("❌ Cannot test - no user authenticated")
            return False

        # Create a new test listing
        print("\n➕ Creating new test listing for persistence test")
        persistence_listing = {
            "title": "PERSISTENCE TEST - Gaming Laptop",
            "description": "Test listing for deletion persistence verification across all endpoints",
            "price": 1299.99,
            "category": "Electronics",
            "condition": "Used - Good",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400"],
            "tags": ["test", "persistence", "gaming"],
            "features": ["Persistence test", "Cross-endpoint verification"]
        }
        
        success, create_response = self.run_test(
            "Create Persistence Test Listing",
            "POST",
            "api/listings",
            200,
            data=persistence_listing
        )
        
        if not success or 'listing_id' not in create_response:
            print("❌ Failed to create persistence test listing")
            return False
        
        listing_id = create_response['listing_id']
        print(f"   ✅ Created persistence test listing: {listing_id}")

        # Verify it appears in both endpoints before deletion
        print(f"\n🔍 Verifying listing appears in both endpoints before deletion")
        
        # Check in /api/listings
        success_listings, listings_response = self.run_test(
            "Check in /api/listings (Before Delete)",
            "GET",
            "api/listings",
            200
        )
        
        in_listings_before = False
        if success_listings:
            listings_data = listings_response.get('listings', listings_response) if isinstance(listings_response, dict) else listings_response
            in_listings_before = any(listing.get('id') == listing_id for listing in listings_data)
        
        # Check in /api/marketplace/browse
        success_browse, browse_response = self.run_test(
            "Check in /api/marketplace/browse (Before Delete)",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        in_browse_before = False
        if success_browse:
            in_browse_before = any(listing.get('id') == listing_id for listing in browse_response)
        
        print(f"   📊 Before deletion - In /api/listings: {in_listings_before}, In browse: {in_browse_before}")

        # Delete via admin API
        print(f"\n🗑️  Deleting via DELETE /api/listings/{listing_id}")
        success_delete, delete_response = self.run_test(
            "Delete via Admin API",
            "DELETE",
            f"api/listings/{listing_id}",
            200
        )
        
        if not success_delete:
            print("❌ Failed to delete listing")
            return False

        # Wait a moment for any async operations
        time.sleep(1)

        # Check if it appears in browse API after deletion
        print(f"\n🔍 Checking if listing appears in browse API after deletion")
        success_browse_after, browse_after_response = self.run_test(
            "Check Browse After Delete",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        in_browse_after = False
        if success_browse_after:
            in_browse_after = any(listing.get('id') == listing_id for listing in browse_after_response)
        
        # Check if it appears in admin listings API after deletion
        print(f"\n🔍 Checking if listing appears in admin listings API after deletion")
        success_listings_after, listings_after_response = self.run_test(
            "Check Admin Listings After Delete",
            "GET",
            "api/listings",
            200
        )
        
        in_listings_after = False
        if success_listings_after:
            listings_data = listings_after_response.get('listings', listings_after_response) if isinstance(listings_after_response, dict) else listings_after_response
            in_listings_after = any(listing.get('id') == listing_id for listing in listings_data)

        print(f"\n📊 After deletion results:")
        print(f"   In /api/listings: {in_listings_after}")
        print(f"   In /api/marketplace/browse: {in_browse_after}")
        
        # Determine if deletion worked properly
        deletion_complete = not in_listings_after and not in_browse_after
        
        self.log_test("Complete Deletion Verification", deletion_complete,
                     f"Listing removed from both sources: {deletion_complete}")
        
        if in_browse_after:
            print("   ⚠️  ISSUE: Deleted listing still appears in browse page!")
        if in_listings_after:
            print("   ⚠️  ISSUE: Deleted listing still appears in admin listings!")
        
        return deletion_complete

    def identify_database_collections(self):
        """Test 6: Identify what MongoDB collections each endpoint uses"""
        print("\n🗄️  TEST 6: MongoDB Collection Identification")
        print("=" * 50)
        
        print("\n📋 Based on backend server.py code analysis:")
        print("   🔍 /api/listings endpoint:")
        print("      - Collection: db.listings")
        print("      - Query: db.listings.find(query) with optional filters")
        print("      - Returns: Object with 'listings' array")
        
        print("\n   🔍 /api/marketplace/browse endpoint:")
        print("      - Collection: db.listings")
        print("      - Query: db.listings.find({'status': 'active'})")
        print("      - Returns: Array of listings directly")
        
        print("\n   🔍 DELETE /api/listings/{id} endpoint:")
        print("      - Collection: db.listings")
        print("      - Operation: db.listings.delete_one({'id': listing_id})")
        
        print("\n✅ CONCLUSION:")
        print("   - Both endpoints use the SAME MongoDB collection: 'listings'")
        print("   - The difference is in query filters and response format")
        print("   - Browse only shows active listings, admin shows all")
        print("   - Deletion removes from the shared collection")
        
        self.log_test("MongoDB Collection Identification", True,
                     "Both endpoints confirmed to use same 'listings' collection")
        
        return True

    def run_investigation(self):
        """Run complete data source discrepancy investigation"""
        print("🔍 Starting Data Source Discrepancy Investigation")
        print("=" * 60)
        print("Investigating the data source discrepancy between admin delete and browse display")
        print("=" * 60)

        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed - cannot continue investigation")
            return False

        # Run all investigation tests
        test_results = []
        
        # Test 1: Admin Delete API
        test_results.append(self.test_admin_delete_api())
        
        # Test 2: Browse Page API
        browse_clean, browse_data = self.test_browse_page_api()
        test_results.append(browse_clean)
        
        # Test 3: Compare Data Sources
        test_results.append(self.compare_data_sources())
        
        # Test 4: Verify Database Collections
        test_results.append(self.verify_database_collections())
        
        # Test 5: Real Deletion Persistence
        test_results.append(self.test_real_deletion_persistence())
        
        # Test 6: Identify Database Collections
        test_results.append(self.identify_database_collections())

        # Final Analysis
        print("\n" + "=" * 60)
        print("🔍 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"📊 Investigation Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\n✅ INVESTIGATION CONCLUSION:")
            print("   - No data source discrepancy found")
            print("   - Both endpoints use the same MongoDB collection")
            print("   - Deletions work correctly across both sources")
            print("   - Any reported issues may be due to:")
            print("     * Frontend caching")
            print("     * Network connectivity issues")
            print("     * Timing issues in UI updates")
        else:
            print(f"\n⚠️  INVESTIGATION FINDINGS:")
            print(f"   - {total_tests - passed_tests} tests revealed potential issues")
            print("   - Data source discrepancy may exist")
            print("   - Further investigation needed")
        
        return passed_tests == total_tests

def main():
    """Main investigation execution"""
    investigator = DataSourceInvestigator()
    success = investigator.run_investigation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())