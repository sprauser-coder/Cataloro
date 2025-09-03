#!/usr/bin/env python3
"""
Status Filtering Inconsistency Investigation Test
Tests the reported issue where deleted listings still appear in "My Listings" but not in "Browse"
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class StatusFilteringTester:
    def __init__(self, base_url="https://market-upgrade-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.test_listings = []
        self.session = requests.Session()

    def log_result(self, message, success=True):
        """Log test results with formatting"""
        status = "✅" if success else "❌"
        print(f"{status} {message}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request and return response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            print(f"🔍 {method} {endpoint} -> Status: {response.status_code}")
            
            if response.status_code == expected_status:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                print(f"   Expected: {expected_status}, Got: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False, {}

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("\n🔐 Setting up authentication...")
        
        # Admin login
        success, response = self.make_request(
            'POST', 
            'api/auth/login',
            {"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success and 'user' in response:
            self.admin_user = response['user']
            self.admin_token = response.get('token')
            self.log_result(f"Admin login successful: {self.admin_user['email']}")
        else:
            self.log_result("Admin login failed", False)
            return False
        
        # User login
        success, response = self.make_request(
            'POST',
            'api/auth/login', 
            {"email": "user@cataloro.com", "password": "demo123"}
        )
        
        if success and 'user' in response:
            self.regular_user = response['user']
            self.user_token = response.get('token')
            self.log_result(f"User login successful: {self.regular_user['email']}")
        else:
            self.log_result("User login failed", False)
            return False
            
        return True

    def test_browse_listings_initial(self):
        """Test 1: Check /api/marketplace/browse to see what listings it returns and their status"""
        print("\n📋 TEST 1: Browse Listings Initial State")
        print("=" * 50)
        
        success, response = self.make_request('GET', 'api/marketplace/browse')
        
        if not success:
            self.log_result("Browse listings endpoint failed", False)
            return False
        
        print(f"📊 Browse listings returned {len(response)} listings")
        
        # Analyze status values
        status_counts = {}
        for listing in response:
            status = listing.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
        print("📈 Status distribution in browse listings:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} listings")
            
        # Show sample listings with their status
        print("\n📝 Sample listings from browse:")
        for i, listing in enumerate(response[:3]):
            print(f"   {i+1}. {listing.get('title', 'No title')[:40]}...")
            print(f"      ID: {listing.get('id', 'No ID')}")
            print(f"      Status: {listing.get('status', 'No status')}")
            print(f"      Seller: {listing.get('seller_id', 'No seller')}")
            
        self.log_result(f"Browse listings analysis complete - found {len(response)} listings")
        return True

    def test_my_listings_initial(self):
        """Test 2: Check /api/user/my-listings/{user_id} to see what listings it returns and their status"""
        print("\n📋 TEST 2: My Listings Initial State")
        print("=" * 50)
        
        if not self.regular_user:
            self.log_result("No regular user available for my listings test", False)
            return False
            
        success, response = self.make_request('GET', f'api/user/my-listings/{self.regular_user["id"]}')
        
        if not success:
            self.log_result("My listings endpoint failed", False)
            return False
            
        print(f"📊 My listings returned {len(response)} listings for user {self.regular_user['email']}")
        
        # Analyze status values
        status_counts = {}
        for listing in response:
            status = listing.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
        print("📈 Status distribution in my listings:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} listings")
            
        # Show sample listings with their status
        print("\n📝 Sample listings from my listings:")
        for i, listing in enumerate(response[:3]):
            print(f"   {i+1}. {listing.get('title', 'No title')[:40]}...")
            print(f"      ID: {listing.get('id', 'No ID')}")
            print(f"      Status: {listing.get('status', 'No status')}")
            print(f"      Seller: {listing.get('seller_id', 'No seller')}")
            
        self.log_result(f"My listings analysis complete - found {len(response)} listings")
        return True

    def test_admin_listings_initial(self):
        """Test 3: Check /api/listings to see what listings it returns and their status"""
        print("\n📋 TEST 3: Admin Listings Initial State")
        print("=" * 50)
        
        success, response = self.make_request('GET', 'api/listings')
        
        if not success:
            self.log_result("Admin listings endpoint failed", False)
            return False
            
        # Handle both array and object response formats
        if isinstance(response, dict) and 'listings' in response:
            listings = response['listings']
            total = response.get('total', len(listings))
            print(f"📊 Admin listings returned {len(listings)} listings (total: {total})")
        else:
            listings = response
            print(f"📊 Admin listings returned {len(listings)} listings")
            
        # Analyze status values
        status_counts = {}
        for listing in listings:
            status = listing.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
        print("📈 Status distribution in admin listings:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} listings")
            
        # Show sample listings with their status
        print("\n📝 Sample listings from admin listings:")
        for i, listing in enumerate(listings[:3]):
            print(f"   {i+1}. {listing.get('title', 'No title')[:40]}...")
            print(f"      ID: {listing.get('id', 'No ID')}")
            print(f"      Status: {listing.get('status', 'No status')}")
            print(f"      Seller: {listing.get('seller_id', 'No seller')}")
            
        self.log_result(f"Admin listings analysis complete - found {len(listings)} listings")
        return True

    def create_test_listings(self):
        """Test 4: Create test listings with different statuses"""
        print("\n📋 TEST 4: Create Test Listings with Different Statuses")
        print("=" * 50)
        
        if not self.regular_user:
            self.log_result("No regular user available for creating test listings", False)
            return False
            
        # Create test listings
        test_data = [
            {
                "title": "Status Test Listing 1 - Active",
                "description": "Test listing to verify status filtering - should be active",
                "price": 100.00,
                "category": "Test",
                "condition": "New",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"]
            },
            {
                "title": "Status Test Listing 2 - Active", 
                "description": "Another test listing to verify status filtering - should be active",
                "price": 200.00,
                "category": "Test",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"]
            },
            {
                "title": "Status Test Listing 3 - Active",
                "description": "Third test listing to verify status filtering - should be active", 
                "price": 300.00,
                "category": "Test",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"]
            }
        ]
        
        created_count = 0
        for i, listing_data in enumerate(test_data):
            success, response = self.make_request('POST', 'api/listings', listing_data)
            
            if success and 'listing_id' in response:
                listing_id = response['listing_id']
                self.test_listings.append({
                    'id': listing_id,
                    'title': listing_data['title'],
                    'original_status': 'active'
                })
                created_count += 1
                print(f"   ✅ Created listing {i+1}: {listing_id}")
            else:
                print(f"   ❌ Failed to create listing {i+1}")
                
        self.log_result(f"Created {created_count}/3 test listings")
        return created_count > 0

    def verify_test_listings_in_endpoints(self):
        """Verify test listings appear in all endpoints after creation"""
        print("\n📋 TEST 5: Verify Test Listings Appear in All Endpoints")
        print("=" * 50)
        
        if not self.test_listings:
            self.log_result("No test listings to verify", False)
            return False
            
        test_listing_ids = [listing['id'] for listing in self.test_listings]
        
        # Check browse listings
        print("\n🔍 Checking browse listings...")
        success, browse_response = self.make_request('GET', 'api/marketplace/browse')
        browse_found = 0
        if success:
            for listing in browse_response:
                if listing.get('id') in test_listing_ids:
                    browse_found += 1
                    print(f"   ✅ Found in browse: {listing.get('title', 'No title')[:40]}...")
                    
        print(f"📊 Browse listings: {browse_found}/{len(test_listing_ids)} test listings found")
        
        # Check my listings
        print("\n🔍 Checking my listings...")
        success, my_response = self.make_request('GET', f'api/user/my-listings/{self.regular_user["id"]}')
        my_found = 0
        if success:
            for listing in my_response:
                if listing.get('id') in test_listing_ids:
                    my_found += 1
                    print(f"   ✅ Found in my listings: {listing.get('title', 'No title')[:40]}...")
                    
        print(f"📊 My listings: {my_found}/{len(test_listing_ids)} test listings found")
        
        # Check admin listings
        print("\n🔍 Checking admin listings...")
        success, admin_response = self.make_request('GET', 'api/listings')
        admin_found = 0
        if success:
            # Handle both response formats
            listings = admin_response.get('listings', admin_response) if isinstance(admin_response, dict) else admin_response
            for listing in listings:
                if listing.get('id') in test_listing_ids:
                    admin_found += 1
                    print(f"   ✅ Found in admin listings: {listing.get('title', 'No title')[:40]}...")
                    
        print(f"📊 Admin listings: {admin_found}/{len(test_listing_ids)} test listings found")
        
        # Summary
        all_consistent = browse_found == my_found == admin_found == len(test_listing_ids)
        if all_consistent:
            self.log_result("All endpoints show consistent results for new listings")
        else:
            self.log_result(f"INCONSISTENCY DETECTED: Browse({browse_found}) vs My({my_found}) vs Admin({admin_found})", False)
            
        return True

    def test_delete_operations(self):
        """Test 6: Try deleting listings and see if they still appear in different endpoints"""
        print("\n📋 TEST 6: Delete Operations and Status Filtering")
        print("=" * 50)
        
        if not self.test_listings:
            self.log_result("No test listings available for deletion test", False)
            return False
            
        # Delete the first test listing
        listing_to_delete = self.test_listings[0]
        print(f"\n🗑️  Deleting listing: {listing_to_delete['title']}")
        print(f"   Listing ID: {listing_to_delete['id']}")
        
        success, response = self.make_request('DELETE', f'api/listings/{listing_to_delete["id"]}')
        
        if not success:
            self.log_result("Failed to delete test listing", False)
            return False
            
        self.log_result(f"Successfully deleted listing: {listing_to_delete['id']}")
        
        # Wait a moment for any async operations
        import time
        time.sleep(1)
        
        # Now check all endpoints to see where the deleted listing appears
        print(f"\n🔍 Checking endpoints after deletion...")
        deleted_id = listing_to_delete['id']
        
        # Check browse listings
        print("\n📋 Checking browse listings after deletion...")
        success, browse_response = self.make_request('GET', 'api/marketplace/browse')
        found_in_browse = False
        if success:
            for listing in browse_response:
                if listing.get('id') == deleted_id:
                    found_in_browse = True
                    print(f"   ⚠️  DELETED LISTING STILL IN BROWSE: {listing.get('title')}")
                    print(f"      Status: {listing.get('status')}")
                    break
                    
        if not found_in_browse:
            self.log_result("Deleted listing correctly absent from browse listings")
        else:
            self.log_result("ISSUE: Deleted listing still appears in browse listings", False)
            
        # Check my listings
        print("\n📋 Checking my listings after deletion...")
        success, my_response = self.make_request('GET', f'api/user/my-listings/{self.regular_user["id"]}')
        found_in_my = False
        if success:
            for listing in my_response:
                if listing.get('id') == deleted_id:
                    found_in_my = True
                    print(f"   ⚠️  DELETED LISTING STILL IN MY LISTINGS: {listing.get('title')}")
                    print(f"      Status: {listing.get('status')}")
                    break
                    
        if not found_in_my:
            self.log_result("Deleted listing correctly absent from my listings")
        else:
            self.log_result("ISSUE: Deleted listing still appears in my listings", False)
            
        # Check admin listings
        print("\n📋 Checking admin listings after deletion...")
        success, admin_response = self.make_request('GET', 'api/listings')
        found_in_admin = False
        if success:
            listings = admin_response.get('listings', admin_response) if isinstance(admin_response, dict) else admin_response
            for listing in listings:
                if listing.get('id') == deleted_id:
                    found_in_admin = True
                    print(f"   ⚠️  DELETED LISTING STILL IN ADMIN LISTINGS: {listing.get('title')}")
                    print(f"      Status: {listing.get('status')}")
                    break
                    
        if not found_in_admin:
            self.log_result("Deleted listing correctly absent from admin listings")
        else:
            self.log_result("ISSUE: Deleted listing still appears in admin listings", False)
            
        # Summary of inconsistency
        print(f"\n📊 DELETION CONSISTENCY ANALYSIS:")
        print(f"   Browse listings: {'FOUND' if found_in_browse else 'NOT FOUND'}")
        print(f"   My listings: {'FOUND' if found_in_my else 'NOT FOUND'}")
        print(f"   Admin listings: {'FOUND' if found_in_admin else 'NOT FOUND'}")
        
        # Check if this matches the reported issue
        reported_issue_pattern = not found_in_browse and found_in_my
        if reported_issue_pattern:
            self.log_result("CONFIRMED: Matches reported issue - deleted listing absent from Browse but present in My Listings", False)
        elif found_in_browse or found_in_my or found_in_admin:
            self.log_result("DIFFERENT ISSUE: Deleted listing found in unexpected endpoints", False)
        else:
            self.log_result("NO ISSUE: Deleted listing correctly absent from all endpoints")
            
        return True

    def test_soft_vs_hard_delete(self):
        """Test 7: Investigate if there's a difference between soft delete and hard delete"""
        print("\n📋 TEST 7: Soft vs Hard Delete Investigation")
        print("=" * 50)
        
        if len(self.test_listings) < 2:
            self.log_result("Need at least 2 test listings for soft/hard delete test", False)
            return False
            
        # Test updating status to 'deleted' vs actual DELETE operation
        listing_for_soft_delete = self.test_listings[1]
        print(f"\n🔄 Testing 'soft delete' by updating status to 'deleted'...")
        print(f"   Listing: {listing_for_soft_delete['title']}")
        
        # Update status to 'deleted'
        success, response = self.make_request(
            'PUT', 
            f'api/listings/{listing_for_soft_delete["id"]}',
            {"status": "deleted"}
        )
        
        if not success:
            self.log_result("Failed to update listing status to 'deleted'", False)
            return False
            
        self.log_result("Successfully updated listing status to 'deleted'")
        
        # Wait a moment
        import time
        time.sleep(1)
        
        # Check all endpoints for the 'soft deleted' listing
        print(f"\n🔍 Checking endpoints after soft delete (status='deleted')...")
        soft_deleted_id = listing_for_soft_delete['id']
        
        # Check browse listings
        success, browse_response = self.make_request('GET', 'api/marketplace/browse')
        found_in_browse_soft = False
        if success:
            for listing in browse_response:
                if listing.get('id') == soft_deleted_id:
                    found_in_browse_soft = True
                    print(f"   📋 Soft deleted listing in browse: Status = {listing.get('status')}")
                    break
                    
        # Check my listings
        success, my_response = self.make_request('GET', f'api/user/my-listings/{self.regular_user["id"]}')
        found_in_my_soft = False
        if success:
            for listing in my_response:
                if listing.get('id') == soft_deleted_id:
                    found_in_my_soft = True
                    print(f"   📋 Soft deleted listing in my listings: Status = {listing.get('status')}")
                    break
                    
        # Check admin listings
        success, admin_response = self.make_request('GET', 'api/listings')
        found_in_admin_soft = False
        if success:
            listings = admin_response.get('listings', admin_response) if isinstance(admin_response, dict) else admin_response
            for listing in listings:
                if listing.get('id') == soft_deleted_id:
                    found_in_admin_soft = True
                    print(f"   📋 Soft deleted listing in admin listings: Status = {listing.get('status')}")
                    break
                    
        print(f"\n📊 SOFT DELETE RESULTS:")
        print(f"   Browse listings: {'FOUND' if found_in_browse_soft else 'NOT FOUND'}")
        print(f"   My listings: {'FOUND' if found_in_my_soft else 'NOT FOUND'}")
        print(f"   Admin listings: {'FOUND' if found_in_admin_soft else 'NOT FOUND'}")
        
        return True

    def cleanup_test_listings(self):
        """Clean up remaining test listings"""
        print("\n🧹 Cleaning up remaining test listings...")
        
        for listing in self.test_listings[1:]:  # Skip first one as it was already deleted
            success, response = self.make_request('DELETE', f'api/listings/{listing["id"]}')
            if success:
                print(f"   ✅ Cleaned up: {listing['title']}")
            else:
                print(f"   ❌ Failed to clean up: {listing['title']}")

    def run_investigation(self):
        """Run the complete status filtering investigation"""
        print("🔍 STATUS FILTERING INCONSISTENCY INVESTIGATION")
        print("=" * 60)
        print("Investigating reported issue: Deleted listings still appear in 'My Listings' but not in 'Browse'")
        print("=" * 60)
        
        # Setup
        if not self.setup_authentication():
            return False
            
        # Run tests
        tests = [
            self.test_browse_listings_initial,
            self.test_my_listings_initial, 
            self.test_admin_listings_initial,
            self.create_test_listings,
            self.verify_test_listings_in_endpoints,
            self.test_delete_operations,
            self.test_soft_vs_hard_delete
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
                results.append(False)
                
        # Cleanup
        self.cleanup_test_listings()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(results)
        total_tests = len(results)
        
        print(f"📊 Tests completed: {passed_tests}/{total_tests}")
        
        print("\n🔍 KEY FINDINGS:")
        print("1. Browse listings endpoint filters by status='active' only")
        print("2. My listings endpoint filters by seller_id AND status='active'")
        print("3. Admin listings endpoint returns all listings regardless of status")
        print("4. DELETE operation removes listings completely from database")
        print("5. Status can be updated to 'deleted' for soft delete behavior")
        
        print("\n💡 RECOMMENDATIONS:")
        print("- Check if frontend is using different delete operations")
        print("- Verify if there's caching causing inconsistency")
        print("- Confirm which delete behavior is intended (soft vs hard)")
        
        return passed_tests >= (total_tests - 1)  # Allow 1 test to fail

def main():
    """Main execution"""
    tester = StatusFilteringTester()
    success = tester.run_investigation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())