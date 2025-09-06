#!/usr/bin/env python3
"""
Admin Panel Bulk Delete ID Mismatch Debug Test
Specifically tests the ID mismatch issue reported in admin panel bulk delete operations
"""

import requests
import sys
import json
from datetime import datetime

class AdminBulkDeleteDebugTester:
    def __init__(self, base_url="https://admanager-cataloro.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.admin_user = None
        self.session = requests.Session()
        self.test_listing_ids = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        if success:
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

    def setup_admin_session(self):
        """Setup admin session for testing"""
        print("🔐 Setting up admin session...")
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
            print(f"   ✅ Admin logged in: {self.admin_user.get('full_name', 'Admin')}")
            return True
        return False

    def create_test_listings(self):
        """Create multiple test listings for bulk delete testing"""
        print("\n📝 Creating test listings for bulk delete testing...")
        
        test_listings = [
            {
                "title": "Bulk Delete Test 1 - MacBook Pro M2",
                "description": "Test listing for admin bulk delete ID debugging - MacBook Pro with M2 chip",
                "price": 2299.99,
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.admin_user['id'],
                "images": ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"],
                "tags": ["macbook", "laptop", "apple"]
            },
            {
                "title": "Bulk Delete Test 2 - iPhone 15 Pro",
                "description": "Test listing for admin bulk delete ID debugging - iPhone 15 Pro Max",
                "price": 1199.99,
                "category": "Electronics",
                "condition": "New",
                "seller_id": self.admin_user['id'],
                "images": ["https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400"],
                "tags": ["iphone", "smartphone", "apple"]
            },
            {
                "title": "Bulk Delete Test 3 - Gaming Setup",
                "description": "Test listing for admin bulk delete ID debugging - Complete gaming setup",
                "price": 1899.99,
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": self.admin_user['id'],
                "images": ["https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=400"],
                "tags": ["gaming", "pc", "setup"]
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
                listing_id = response['listing_id']
                self.test_listing_ids.append(listing_id)
                created_count += 1
                print(f"   ✅ Created listing {i+1} with ID: {listing_id}")
                print(f"      Title: {listing_data['title']}")
        
        print(f"\n📊 Created {created_count}/{len(test_listings)} test listings")
        return created_count == len(test_listings)

    def analyze_id_formats(self):
        """Analyze ID formats across different endpoints"""
        print("\n🔍 CRITICAL: Analyzing ID formats across endpoints...")
        
        # 1. Get IDs from /api/listings endpoint (admin listings)
        print("\n1️⃣ Getting IDs from /api/listings endpoint (admin listings)...")
        success_listings, listings_response = self.run_test(
            "Get Admin Listings IDs",
            "GET",
            "api/listings",
            200
        )
        
        admin_listing_ids = []
        if success_listings and 'listings' in listings_response:
            admin_listing_ids = [listing.get('id') or listing.get('_id') for listing in listings_response['listings']]
            print(f"   📋 Found {len(admin_listing_ids)} listings in admin endpoint")
            for i, listing_id in enumerate(admin_listing_ids[:3]):  # Show first 3
                print(f"      ID {i+1}: {listing_id} (type: {type(listing_id).__name__}, length: {len(str(listing_id))})")
        
        # 2. Get IDs from /api/marketplace/browse endpoint (public browse)
        print("\n2️⃣ Getting IDs from /api/marketplace/browse endpoint (public browse)...")
        success_browse, browse_response = self.run_test(
            "Get Browse Listings IDs",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        browse_listing_ids = []
        if success_browse:
            browse_listing_ids = [listing.get('id') or listing.get('_id') for listing in browse_response]
            print(f"   📋 Found {len(browse_listing_ids)} listings in browse endpoint")
            for i, listing_id in enumerate(browse_listing_ids[:3]):  # Show first 3
                print(f"      ID {i+1}: {listing_id} (type: {type(listing_id).__name__}, length: {len(str(listing_id))})")
        
        # 3. Compare ID formats
        print("\n3️⃣ Comparing ID formats between endpoints...")
        
        # Find common listings between both endpoints
        common_ids = set(admin_listing_ids) & set(browse_listing_ids)
        admin_only_ids = set(admin_listing_ids) - set(browse_listing_ids)
        browse_only_ids = set(browse_listing_ids) - set(admin_listing_ids)
        
        print(f"   📊 ID Format Analysis:")
        print(f"      Common IDs (same in both): {len(common_ids)}")
        print(f"      Admin-only IDs: {len(admin_only_ids)}")
        print(f"      Browse-only IDs: {len(browse_only_ids)}")
        
        if admin_only_ids:
            print(f"      ⚠️  Admin-only ID examples: {list(admin_only_ids)[:2]}")
        if browse_only_ids:
            print(f"      ⚠️  Browse-only ID examples: {list(browse_only_ids)[:2]}")
        
        # 4. Check our test listing IDs specifically
        print(f"\n4️⃣ Checking our test listing IDs...")
        for test_id in self.test_listing_ids:
            in_admin = test_id in admin_listing_ids
            in_browse = test_id in browse_listing_ids
            print(f"   Test ID {test_id[:8]}... - Admin: {in_admin}, Browse: {in_browse}")
            
            if not in_admin or not in_browse:
                print(f"      ⚠️  ID MISMATCH DETECTED for test listing!")
        
        return {
            'admin_ids': admin_listing_ids,
            'browse_ids': browse_listing_ids,
            'common_ids': common_ids,
            'id_mismatch_detected': len(admin_only_ids) > 0 or len(browse_only_ids) > 0
        }

    def test_delete_operations_with_actual_ids(self, id_analysis):
        """Test DELETE operations using actual IDs from the admin listings"""
        print("\n🗑️ CRITICAL: Testing DELETE operations with actual admin listing IDs...")
        
        # Use the first few IDs from admin listings for testing
        admin_ids = id_analysis['admin_ids'][:3]  # Test with first 3 IDs
        
        delete_results = []
        
        for i, listing_id in enumerate(admin_ids):
            print(f"\n🎯 Testing DELETE with admin listing ID {i+1}: {listing_id}")
            
            # First, verify the listing exists
            success_get, get_response = self.run_test(
                f"Verify Listing Exists (ID: {listing_id[:8]}...)",
                "GET",
                f"api/listings/{listing_id}",
                200
            )
            
            if not success_get:
                print(f"   ⚠️  Listing {listing_id} not found via GET - skipping DELETE test")
                continue
            
            # Now test DELETE operation
            success_delete, delete_response = self.run_test(
                f"DELETE Listing (ID: {listing_id[:8]}...)",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            
            delete_result = {
                'listing_id': listing_id,
                'delete_success': success_delete,
                'delete_response': delete_response,
                'deleted_count': delete_response.get('deleted_count', 0) if success_delete else 0
            }
            delete_results.append(delete_result)
            
            if success_delete:
                deleted_count = delete_response.get('deleted_count', 0)
                print(f"   ✅ DELETE returned success - deleted_count: {deleted_count}")
                
                # Verify deletion by checking if listing still exists
                success_verify, _ = self.run_test(
                    f"Verify Deletion (ID: {listing_id[:8]}...)",
                    "GET",
                    f"api/listings/{listing_id}",
                    404  # Should return 404 if truly deleted
                )
                
                delete_result['verification_success'] = success_verify
                
                if success_verify:
                    print(f"   ✅ Deletion verified - listing no longer exists")
                else:
                    print(f"   ❌ CRITICAL: Listing still exists after DELETE!")
            else:
                print(f"   ❌ DELETE operation failed")
                delete_result['verification_success'] = False
        
        return delete_results

    def test_database_persistence_verification(self):
        """Verify that DELETE operations actually persist in the database"""
        print("\n💾 CRITICAL: Testing database persistence after DELETE operations...")
        
        # Create a fresh test listing specifically for persistence testing
        persistence_test_listing = {
            "title": "Persistence Test Listing - Wireless Earbuds",
            "description": "Test listing specifically for database persistence verification",
            "price": 149.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"]
        }
        
        # Step 1: Create the listing
        success_create, create_response = self.run_test(
            "Create Persistence Test Listing",
            "POST",
            "api/listings",
            200,
            data=persistence_test_listing
        )
        
        if not success_create:
            print("❌ Failed to create persistence test listing")
            return False
        
        persistence_listing_id = create_response['listing_id']
        print(f"   ✅ Created persistence test listing: {persistence_listing_id}")
        
        # Step 2: Verify it appears in both endpoints
        print(f"\n📋 Verifying listing appears in both endpoints...")
        
        # Check admin listings
        success_admin, admin_response = self.run_test(
            "Check Admin Listings",
            "GET",
            "api/listings",
            200
        )
        
        in_admin = False
        if success_admin and 'listings' in admin_response:
            in_admin = any(listing.get('id') == persistence_listing_id for listing in admin_response['listings'])
        
        # Check browse listings
        success_browse, browse_response = self.run_test(
            "Check Browse Listings",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        in_browse = False
        if success_browse:
            in_browse = any(listing.get('id') == persistence_listing_id for listing in browse_response)
        
        print(f"   📊 Listing presence before DELETE:")
        print(f"      Admin listings: {in_admin}")
        print(f"      Browse listings: {in_browse}")
        
        # Step 3: DELETE the listing
        print(f"\n🗑️ Deleting persistence test listing...")
        success_delete, delete_response = self.run_test(
            "DELETE Persistence Test Listing",
            "DELETE",
            f"api/listings/{persistence_listing_id}",
            200
        )
        
        if not success_delete:
            print("❌ DELETE operation failed")
            return False
        
        deleted_count = delete_response.get('deleted_count', 0)
        print(f"   ✅ DELETE returned success - deleted_count: {deleted_count}")
        
        # Step 4: Verify persistence - check both endpoints again
        print(f"\n🔄 Verifying persistence - checking both endpoints after DELETE...")
        
        # Check admin listings after delete
        success_admin_after, admin_after_response = self.run_test(
            "Check Admin Listings After DELETE",
            "GET",
            "api/listings",
            200
        )
        
        still_in_admin = False
        if success_admin_after and 'listings' in admin_after_response:
            still_in_admin = any(listing.get('id') == persistence_listing_id for listing in admin_after_response['listings'])
        
        # Check browse listings after delete
        success_browse_after, browse_after_response = self.run_test(
            "Check Browse Listings After DELETE",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        still_in_browse = False
        if success_browse_after:
            still_in_browse = any(listing.get('id') == persistence_listing_id for listing in browse_after_response)
        
        print(f"   📊 Listing presence after DELETE:")
        print(f"      Admin listings: {still_in_admin}")
        print(f"      Browse listings: {still_in_browse}")
        
        # Step 5: Analysis
        persistence_success = not still_in_admin and not still_in_browse
        
        if persistence_success:
            print(f"   ✅ PERSISTENCE VERIFIED: Listing successfully removed from both endpoints")
        else:
            print(f"   ❌ PERSISTENCE FAILED: Listing still appears in one or both endpoints")
            if still_in_admin:
                print(f"      ⚠️  Still in admin listings - DELETE may not be working properly")
            if still_in_browse:
                print(f"      ⚠️  Still in browse listings - DELETE may not be working properly")
        
        return persistence_success

    def test_bulk_delete_simulation(self):
        """Simulate the bulk delete operation that admin panel performs"""
        print("\n📦 CRITICAL: Simulating admin panel bulk delete operation...")
        
        if len(self.test_listing_ids) < 2:
            print("❌ Need at least 2 test listings for bulk delete simulation")
            return False
        
        # Select first 2 test listings for bulk delete
        bulk_delete_ids = self.test_listing_ids[:2]
        print(f"   🎯 Bulk deleting {len(bulk_delete_ids)} listings:")
        for i, listing_id in enumerate(bulk_delete_ids):
            print(f"      {i+1}. {listing_id}")
        
        # Simulate what the frontend bulk delete does - individual DELETE calls
        bulk_results = []
        successful_deletes = 0
        
        for i, listing_id in enumerate(bulk_delete_ids):
            print(f"\n🗑️ Bulk Delete Step {i+1}: DELETE {listing_id[:8]}...")
            
            success_delete, delete_response = self.run_test(
                f"Bulk DELETE {i+1}",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            
            result = {
                'listing_id': listing_id,
                'success': success_delete,
                'response': delete_response,
                'deleted_count': delete_response.get('deleted_count', 0) if success_delete else 0
            }
            bulk_results.append(result)
            
            if success_delete:
                successful_deletes += 1
                print(f"   ✅ Bulk delete step {i+1} successful")
            else:
                print(f"   ❌ Bulk delete step {i+1} failed")
        
        print(f"\n📊 Bulk Delete Results: {successful_deletes}/{len(bulk_delete_ids)} successful")
        
        # Verify bulk delete persistence
        print(f"\n🔄 Verifying bulk delete persistence...")
        success_browse_final, browse_final_response = self.run_test(
            "Final Browse Check After Bulk Delete",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success_browse_final:
            remaining_test_listings = 0
            for listing_id in bulk_delete_ids:
                still_exists = any(listing.get('id') == listing_id for listing in browse_final_response)
                if still_exists:
                    remaining_test_listings += 1
                    print(f"   ⚠️  Bulk deleted listing {listing_id[:8]}... still exists!")
            
            bulk_persistence_success = remaining_test_listings == 0
            print(f"   📊 Bulk delete persistence: {remaining_test_listings} listings still exist (should be 0)")
            
            if bulk_persistence_success:
                print(f"   ✅ BULK DELETE PERSISTENCE VERIFIED")
            else:
                print(f"   ❌ BULK DELETE PERSISTENCE FAILED - {remaining_test_listings} listings reappeared")
            
            return bulk_persistence_success
        
        return False

    def run_debug_tests(self):
        """Run the complete debug test suite for admin bulk delete ID mismatch"""
        print("🚀 Starting Admin Panel Bulk Delete ID Mismatch Debug Tests")
        print("=" * 80)
        
        # Setup
        if not self.setup_admin_session():
            print("❌ Failed to setup admin session - stopping tests")
            return False
        
        # Create test data
        if not self.create_test_listings():
            print("❌ Failed to create test listings - stopping tests")
            return False
        
        # Core debug tests
        print("\n" + "=" * 80)
        print("🔍 CORE DEBUG ANALYSIS")
        print("=" * 80)
        
        # 1. ID Format Analysis
        id_analysis = self.analyze_id_formats()
        
        # 2. DELETE Operations with Actual IDs
        delete_results = self.test_delete_operations_with_actual_ids(id_analysis)
        
        # 3. Database Persistence Verification
        persistence_success = self.test_database_persistence_verification()
        
        # 4. Bulk Delete Simulation
        bulk_delete_success = self.test_bulk_delete_simulation()
        
        # Final Analysis
        print("\n" + "=" * 80)
        print("📊 FINAL DEBUG ANALYSIS")
        print("=" * 80)
        
        print(f"\n🔍 ID Mismatch Analysis:")
        print(f"   ID format mismatch detected: {id_analysis['id_mismatch_detected']}")
        print(f"   Common IDs between endpoints: {len(id_analysis['common_ids'])}")
        
        print(f"\n🗑️ DELETE Operation Analysis:")
        successful_deletes = sum(1 for result in delete_results if result['delete_success'])
        verified_deletes = sum(1 for result in delete_results if result.get('verification_success', False))
        print(f"   DELETE operations successful: {successful_deletes}/{len(delete_results)}")
        print(f"   DELETE operations verified: {verified_deletes}/{len(delete_results)}")
        
        print(f"\n💾 Persistence Analysis:")
        print(f"   Database persistence working: {persistence_success}")
        print(f"   Bulk delete persistence working: {bulk_delete_success}")
        
        # Root Cause Analysis
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        
        if id_analysis['id_mismatch_detected']:
            print(f"   ❌ ISSUE FOUND: ID format mismatch between admin and browse endpoints")
            print(f"      - This could cause frontend to use wrong IDs for DELETE operations")
            print(f"      - Frontend may be using IDs from browse that don't match admin listings")
        else:
            print(f"   ✅ ID formats consistent between endpoints")
        
        if successful_deletes == len(delete_results) and verified_deletes == len(delete_results):
            print(f"   ✅ DELETE operations working correctly with proper IDs")
        else:
            print(f"   ❌ ISSUE FOUND: DELETE operations not working properly")
            print(f"      - Some DELETE calls failed or didn't actually remove records")
        
        if persistence_success and bulk_delete_success:
            print(f"   ✅ Database persistence working correctly")
        else:
            print(f"   ❌ ISSUE FOUND: Database persistence problems detected")
            print(f"      - Deleted records may be reappearing after refresh")
        
        # Overall Assessment
        all_tests_passed = (
            not id_analysis['id_mismatch_detected'] and
            successful_deletes == len(delete_results) and
            verified_deletes == len(delete_results) and
            persistence_success and
            bulk_delete_success
        )
        
        print(f"\n🏁 OVERALL ASSESSMENT:")
        if all_tests_passed:
            print(f"   ✅ NO ISSUES DETECTED - Admin bulk delete should be working correctly")
            print(f"   ✅ All DELETE operations successful and persistent")
            print(f"   ✅ No ID format mismatches found")
        else:
            print(f"   ❌ ISSUES DETECTED - Admin bulk delete has problems")
            print(f"   ❌ See analysis above for specific issues")
            print(f"   ❌ Frontend may be using incorrect IDs or DELETE operations not persisting")
        
        return all_tests_passed

def main():
    """Main test execution"""
    tester = AdminBulkDeleteDebugTester()
    success = tester.run_debug_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())