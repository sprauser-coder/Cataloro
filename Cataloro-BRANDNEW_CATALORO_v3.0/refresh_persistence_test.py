#!/usr/bin/env python3
"""
Refresh Persistence Test - Verify listings don't reappear after delete
Tests the specific issue: "All listings come back after refresh"
"""

import requests
import sys
import json
import time
from datetime import datetime

class RefreshPersistenceTest:
    def __init__(self, base_url="https://bid-manager-5.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.admin_user = None
        self.session = requests.Session()

    def log_test(self, name, success, details=""):
        """Log test results"""
        if success:
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}

        print(f"\n🔍 {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(name, success, f"Status: {response.status_code}")
                    return success, response_data
                except:
                    self.log_test(name, success, f"Status: {response.status_code}")
                    return success, {}
            else:
                self.log_test(name, False, f"Status: {response.status_code}, Expected: {expected_status}")
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_admin_session(self):
        """Setup admin session"""
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
            return True
        return False

    def test_refresh_persistence_issue(self):
        """Test the specific issue: listings reappearing after refresh"""
        print("\n🔄 TESTING REFRESH PERSISTENCE ISSUE")
        print("=" * 60)
        
        # Step 1: Create a test listing
        test_listing = {
            "title": "Refresh Test Listing - Gaming Headset",
            "description": "Test listing to verify refresh persistence issue",
            "price": 199.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"]
        }
        
        success_create, create_response = self.run_test(
            "Create Test Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_create:
            return False
        
        listing_id = create_response['listing_id']
        print(f"   📝 Created test listing: {listing_id}")
        
        # Step 2: Verify listing appears in admin endpoint
        success_admin_before, admin_before = self.run_test(
            "Check Admin Listings (Before Delete)",
            "GET",
            "api/listings",
            200
        )
        
        admin_count_before = len(admin_before.get('listings', [])) if success_admin_before else 0
        listing_in_admin_before = False
        if success_admin_before:
            listing_in_admin_before = any(
                listing.get('id') == listing_id 
                for listing in admin_before.get('listings', [])
            )
        
        print(f"   📊 Admin listings before delete: {admin_count_before} (test listing present: {listing_in_admin_before})")
        
        # Step 3: Verify listing appears in browse endpoint
        success_browse_before, browse_before = self.run_test(
            "Check Browse Listings (Before Delete)",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        browse_count_before = len(browse_before) if success_browse_before else 0
        listing_in_browse_before = False
        if success_browse_before:
            listing_in_browse_before = any(
                listing.get('id') == listing_id 
                for listing in browse_before
            )
        
        print(f"   📊 Browse listings before delete: {browse_count_before} (test listing present: {listing_in_browse_before})")
        
        # Step 4: DELETE the listing
        success_delete, delete_response = self.run_test(
            "DELETE Test Listing",
            "DELETE",
            f"api/listings/{listing_id}",
            200
        )
        
        if not success_delete:
            print("❌ DELETE failed - cannot test refresh persistence")
            return False
        
        deleted_count = delete_response.get('deleted_count', 0)
        print(f"   🗑️ DELETE successful - deleted_count: {deleted_count}")
        
        # Step 5: Immediate check after delete (simulating UI state)
        print(f"\n⚡ IMMEDIATE CHECK AFTER DELETE (simulating UI state)")
        
        success_admin_immediate, admin_immediate = self.run_test(
            "Check Admin Listings (Immediate After Delete)",
            "GET",
            "api/listings",
            200
        )
        
        admin_count_immediate = len(admin_immediate.get('listings', [])) if success_admin_immediate else 0
        listing_in_admin_immediate = False
        if success_admin_immediate:
            listing_in_admin_immediate = any(
                listing.get('id') == listing_id 
                for listing in admin_immediate.get('listings', [])
            )
        
        print(f"   📊 Admin listings immediately after delete: {admin_count_immediate} (test listing present: {listing_in_admin_immediate})")
        
        success_browse_immediate, browse_immediate = self.run_test(
            "Check Browse Listings (Immediate After Delete)",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        browse_count_immediate = len(browse_immediate) if success_browse_immediate else 0
        listing_in_browse_immediate = False
        if success_browse_immediate:
            listing_in_browse_immediate = any(
                listing.get('id') == listing_id 
                for listing in browse_immediate
            )
        
        print(f"   📊 Browse listings immediately after delete: {browse_count_immediate} (test listing present: {listing_in_browse_immediate})")
        
        # Step 6: Wait and check again (simulating refresh)
        print(f"\n🔄 REFRESH SIMULATION (waiting 2 seconds then checking again)")
        time.sleep(2)
        
        success_admin_refresh, admin_refresh = self.run_test(
            "Check Admin Listings (After Refresh)",
            "GET",
            "api/listings",
            200
        )
        
        admin_count_refresh = len(admin_refresh.get('listings', [])) if success_admin_refresh else 0
        listing_in_admin_refresh = False
        if success_admin_refresh:
            listing_in_admin_refresh = any(
                listing.get('id') == listing_id 
                for listing in admin_refresh.get('listings', [])
            )
        
        print(f"   📊 Admin listings after refresh: {admin_count_refresh} (test listing present: {listing_in_admin_refresh})")
        
        success_browse_refresh, browse_refresh = self.run_test(
            "Check Browse Listings (After Refresh)",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        browse_count_refresh = len(browse_refresh) if success_browse_refresh else 0
        listing_in_browse_refresh = False
        if success_browse_refresh:
            listing_in_browse_refresh = any(
                listing.get('id') == listing_id 
                for listing in browse_refresh
            )
        
        print(f"   📊 Browse listings after refresh: {browse_count_refresh} (test listing present: {listing_in_browse_refresh})")
        
        # Step 7: Analysis
        print(f"\n📊 REFRESH PERSISTENCE ANALYSIS")
        print("=" * 60)
        
        print(f"📈 Count Changes:")
        print(f"   Admin: {admin_count_before} → {admin_count_immediate} → {admin_count_refresh}")
        print(f"   Browse: {browse_count_before} → {browse_count_immediate} → {browse_count_refresh}")
        
        print(f"\n🎯 Test Listing Presence:")
        print(f"   Before Delete - Admin: {listing_in_admin_before}, Browse: {listing_in_browse_before}")
        print(f"   After Delete  - Admin: {listing_in_admin_immediate}, Browse: {listing_in_browse_immediate}")
        print(f"   After Refresh - Admin: {listing_in_admin_refresh}, Browse: {listing_in_browse_refresh}")
        
        # Check for the reported issue
        reappeared_in_admin = not listing_in_admin_immediate and listing_in_admin_refresh
        reappeared_in_browse = not listing_in_browse_immediate and listing_in_browse_refresh
        
        print(f"\n🚨 ISSUE DETECTION:")
        print(f"   Listing reappeared in admin after refresh: {reappeared_in_admin}")
        print(f"   Listing reappeared in browse after refresh: {reappeared_in_browse}")
        
        if reappeared_in_admin or reappeared_in_browse:
            print(f"   ❌ ISSUE CONFIRMED: Listings are reappearing after refresh!")
            print(f"   ❌ This matches the user's report: 'All listings come back after refresh'")
        else:
            print(f"   ✅ NO ISSUE: Deleted listings stay deleted after refresh")
        
        # Check for count inconsistencies
        admin_count_decreased = admin_count_refresh < admin_count_before
        browse_count_decreased = browse_count_refresh < browse_count_before
        
        print(f"\n📉 COUNT VERIFICATION:")
        print(f"   Admin count decreased after delete: {admin_count_decreased}")
        print(f"   Browse count decreased after delete: {browse_count_decreased}")
        
        # Overall assessment
        persistence_working = (
            not listing_in_admin_refresh and 
            not listing_in_browse_refresh and
            admin_count_decreased and
            browse_count_decreased
        )
        
        print(f"\n🏁 OVERALL ASSESSMENT:")
        if persistence_working:
            print(f"   ✅ REFRESH PERSISTENCE WORKING: Deleted listings don't reappear")
        else:
            print(f"   ❌ REFRESH PERSISTENCE ISSUE CONFIRMED: Deleted listings are reappearing")
            if listing_in_admin_refresh:
                print(f"      - Test listing still present in admin endpoint after refresh")
            if listing_in_browse_refresh:
                print(f"      - Test listing still present in browse endpoint after refresh")
            if not admin_count_decreased:
                print(f"      - Admin listing count didn't decrease")
            if not browse_count_decreased:
                print(f"      - Browse listing count didn't decrease")
        
        return persistence_working

    def run_test_suite(self):
        """Run the complete refresh persistence test suite"""
        print("🚀 Starting Refresh Persistence Test Suite")
        print("Testing: 'All listings come back after refresh' issue")
        print("=" * 80)
        
        if not self.setup_admin_session():
            print("❌ Failed to setup admin session")
            return False
        
        persistence_working = self.test_refresh_persistence_issue()
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        
        if persistence_working:
            print("🎉 SUCCESS: No refresh persistence issues detected")
            print("✅ Deleted listings stay deleted after refresh")
            print("✅ Backend DELETE operations are working correctly")
        else:
            print("⚠️ ISSUE DETECTED: Refresh persistence problems found")
            print("❌ Deleted listings are reappearing after refresh")
            print("❌ This confirms the user's reported issue")
        
        return persistence_working

def main():
    """Main test execution"""
    tester = RefreshPersistenceTest()
    success = tester.run_test_suite()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())