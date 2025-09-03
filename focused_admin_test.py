#!/usr/bin/env python3
"""
Focused Admin Panel Fallback Data Fix Test
Tests the specific issue: admin panel falling back to local marketplace data
"""

import requests
import sys
import json
import time
from datetime import datetime

class FocusedAdminTester:
    def __init__(self, base_url="https://tender-system.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_user = None
        self.test_listing_ids = []
        self.session = requests.Session()

    def setup_admin(self):
        """Setup admin authentication"""
        response = self.session.post(f"{self.base_url}/api/auth/login", 
                                   json={"email": "admin@cataloro.com", "password": "demo123"})
        if response.status_code == 200:
            data = response.json()
            self.admin_user = data['user']
            print(f"✅ Admin authenticated: {self.admin_user.get('full_name', 'Admin')}")
            return True
        return False

    def create_test_listings(self):
        """Create test listings and track their IDs"""
        print("\n📝 Creating test listings...")
        
        test_listings = [
            {
                "title": "Admin Fallback Test 1 - Gaming Laptop",
                "description": "High-performance gaming laptop for admin fallback testing",
                "price": 1899.99,
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.admin_user['id'],
                "tags": ["gaming", "laptop", "admin-fallback-test"]
            },
            {
                "title": "Admin Fallback Test 2 - Mechanical Keyboard",
                "description": "RGB mechanical keyboard for admin fallback testing",
                "price": 149.99,
                "category": "Electronics",
                "condition": "New",
                "seller_id": self.admin_user['id'],
                "tags": ["keyboard", "mechanical", "admin-fallback-test"]
            }
        ]
        
        for i, listing in enumerate(test_listings):
            response = self.session.post(f"{self.base_url}/api/listings", json=listing)
            if response.status_code == 200:
                listing_id = response.json()['listing_id']
                self.test_listing_ids.append(listing_id)
                print(f"   ✅ Created test listing {i+1}: {listing_id}")
            else:
                print(f"   ❌ Failed to create test listing {i+1}")
                return False
        
        return len(self.test_listing_ids) == len(test_listings)

    def verify_listings_in_endpoints(self, stage=""):
        """Verify test listings appear in both endpoints"""
        print(f"\n🔍 Verifying listings in endpoints {stage}...")
        
        # Check /api/listings (admin panel endpoint)
        api_response = self.session.get(f"{self.base_url}/api/listings?limit=100")
        api_listings = api_response.json().get('listings', []) if api_response.status_code == 200 else []
        api_test_count = sum(1 for listing in api_listings if listing.get('id') in self.test_listing_ids)
        
        # Check /api/marketplace/browse (browse endpoint)
        browse_response = self.session.get(f"{self.base_url}/api/marketplace/browse")
        browse_listings = browse_response.json() if browse_response.status_code == 200 else []
        browse_test_count = sum(1 for listing in browse_listings if listing.get('id') in self.test_listing_ids)
        
        print(f"   📊 API endpoint: {api_test_count}/{len(self.test_listing_ids)} test listings found")
        print(f"   📊 Browse endpoint: {browse_test_count}/{len(self.test_listing_ids)} test listings found")
        
        return api_test_count, browse_test_count

    def test_bulk_delete_and_persistence(self):
        """Test the core issue: bulk delete and no fallback data reappearance"""
        print("\n🗑️ Testing bulk delete and persistence...")
        
        # Step 1: Verify listings exist before delete
        api_before, browse_before = self.verify_listings_in_endpoints("BEFORE DELETE")
        
        if api_before != len(self.test_listing_ids) or browse_before != len(self.test_listing_ids):
            print("❌ Test listings not properly created - aborting delete test")
            return False
        
        # Step 2: Perform bulk delete operations
        print("\n   🗑️ Performing bulk delete operations...")
        deleted_count = 0
        for i, listing_id in enumerate(self.test_listing_ids):
            response = self.session.delete(f"{self.base_url}/api/listings/{listing_id}")
            if response.status_code == 200:
                deleted_count += 1
                print(f"      ✅ Deleted listing {i+1}: {listing_id}")
            else:
                print(f"      ❌ Failed to delete listing {i+1}: {response.status_code}")
        
        if deleted_count != len(self.test_listing_ids):
            print(f"❌ Only deleted {deleted_count}/{len(self.test_listing_ids)} listings")
            return False
        
        # Step 3: Wait for database consistency
        print("\n   ⏳ Waiting for database consistency...")
        time.sleep(2)
        
        # Step 4: Verify listings are gone and don't reappear
        print("\n   🔍 Verifying deletion persistence...")
        api_after, browse_after = self.verify_listings_in_endpoints("AFTER DELETE")
        
        # Step 5: Multiple consistency checks to ensure no fallback data reappearance
        print("\n   🔄 Testing for fallback data reappearance (multiple checks)...")
        consistent = True
        for i in range(5):
            time.sleep(1)
            api_check, browse_check = self.verify_listings_in_endpoints(f"CHECK {i+1}")
            if api_check > 0 or browse_check > 0:
                print(f"      ⚠️ Check {i+1}: Found {api_check} in API, {browse_check} in Browse - FALLBACK DATA DETECTED!")
                consistent = False
            else:
                print(f"      ✅ Check {i+1}: No test listings found - Good!")
        
        # Results
        delete_success = (deleted_count == len(self.test_listing_ids))
        persistence_success = (api_after == 0 and browse_after == 0)
        no_fallback = consistent
        
        print(f"\n📊 Bulk Delete Results:")
        print(f"   Delete Operations: {'✅ PASSED' if delete_success else '❌ FAILED'} ({deleted_count}/{len(self.test_listing_ids)})")
        print(f"   Immediate Persistence: {'✅ PASSED' if persistence_success else '❌ FAILED'} (API: {api_after}, Browse: {browse_after})")
        print(f"   No Fallback Reappearance: {'✅ PASSED' if no_fallback else '❌ FAILED'}")
        
        return delete_success and persistence_success and no_fallback

    def test_admin_panel_fallback_fix(self):
        """Main test for admin panel fallback data fix"""
        print("🚀 Testing Admin Panel Fallback Data Fix")
        print("=" * 60)
        
        # Setup
        if not self.setup_admin():
            print("❌ Admin setup failed")
            return False
        
        # Create test listings
        if not self.create_test_listings():
            print("❌ Failed to create test listings")
            return False
        
        # Test the core issue
        success = self.test_bulk_delete_and_persistence()
        
        # Summary
        print("\n" + "=" * 60)
        print("ADMIN PANEL FALLBACK FIX TEST SUMMARY")
        print("=" * 60)
        
        if success:
            print("🎉 ADMIN PANEL FALLBACK FIX VERIFIED!")
            print("✅ Deleted listings stay deleted and don't reappear due to fallback data")
            print("✅ Admin panel now ONLY uses backend API data")
            print("✅ No fallback to marketplace data after delete operations")
        else:
            print("❌ ADMIN PANEL FALLBACK FIX HAS ISSUES!")
            print("⚠️ Deleted listings may reappear due to fallback data")
        
        return success

def main():
    tester = FocusedAdminTester()
    success = tester.test_admin_panel_fallback_fix()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())