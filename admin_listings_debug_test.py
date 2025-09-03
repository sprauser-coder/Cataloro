#!/usr/bin/env python3
"""
Admin Panel Listings Debug Test
Investigates the persistent 6 listings issue after deletion
"""

import requests
import sys
import json
from datetime import datetime

class AdminListingsDebugger:
    def __init__(self, base_url="https://cataloro-marketplace-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.admin_user = None
        self.session = requests.Session()
        self.persistent_listings = []

    def log_result(self, name, success, details=""):
        """Log test results"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {name}")
        if details:
            print(f"   {details}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make API request and return response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print(f"\n🔍 {method} {endpoint}")
            print(f"   Status: {response.status_code} (Expected: {expected_status})")
            
            if response.status_code == expected_status:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                print(f"   Error: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"   Exception: {str(e)}")
            return False, {}

    def admin_login(self):
        """Login as admin"""
        print("\n🔐 Admin Login...")
        success, response = self.make_request(
            "POST", 
            "api/auth/login",
            {"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_user = response['user']
            self.log_result("Admin Login", True, f"Logged in as: {self.admin_user.get('full_name', 'Admin')}")
            return True
        else:
            self.log_result("Admin Login", False, "Failed to authenticate")
            return False

    def analyze_database_listings(self):
        """Analyze what listings exist in the database"""
        print("\n📊 DATABASE ANALYSIS")
        print("=" * 50)
        
        # Get all listings from /api/listings endpoint
        success, listings_response = self.make_request("GET", "api/listings")
        
        if success and 'listings' in listings_response:
            all_listings = listings_response['listings']
            print(f"📋 Total listings in database: {len(all_listings)}")
            
            # Analyze by status
            status_counts = {}
            for listing in all_listings:
                status = listing.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("📊 Listings by status:")
            for status, count in status_counts.items():
                print(f"   {status}: {count}")
            
            # Show first 10 listings with details
            print("\n📝 First 10 listings details:")
            for i, listing in enumerate(all_listings[:10]):
                print(f"   {i+1}. ID: {listing.get('id', 'N/A')[:8]}...")
                print(f"      Title: {listing.get('title', 'N/A')}")
                print(f"      Status: {listing.get('status', 'N/A')}")
                print(f"      Seller: {listing.get('seller_id', 'N/A')}")
                print(f"      Created: {listing.get('created_at', 'N/A')}")
                print()
            
            return all_listings
        else:
            self.log_result("Database Analysis", False, "Could not retrieve listings")
            return []

    def analyze_browse_endpoint(self):
        """Analyze what /api/marketplace/browse returns"""
        print("\n🌐 BROWSE ENDPOINT ANALYSIS")
        print("=" * 50)
        
        success, browse_listings = self.make_request("GET", "api/marketplace/browse")
        
        if success:
            print(f"📋 Browse endpoint returns: {len(browse_listings)} listings")
            
            # Show details of all browse listings
            print("\n📝 Browse listings details:")
            for i, listing in enumerate(browse_listings):
                print(f"   {i+1}. ID: {listing.get('id', 'N/A')[:8]}...")
                print(f"      Title: {listing.get('title', 'N/A')}")
                print(f"      Status: {listing.get('status', 'N/A')}")
                print(f"      Price: €{listing.get('price', 'N/A')}")
                print(f"      Category: {listing.get('category', 'N/A')}")
                print(f"      Seller: {listing.get('seller_id', 'N/A')}")
                print()
            
            return browse_listings
        else:
            self.log_result("Browse Analysis", False, "Could not retrieve browse listings")
            return []

    def compare_endpoints(self, all_listings, browse_listings):
        """Compare /api/listings vs /api/marketplace/browse"""
        print("\n🔍 ENDPOINT COMPARISON")
        print("=" * 50)
        
        # Extract IDs from both endpoints
        all_ids = set(listing.get('id') for listing in all_listings)
        browse_ids = set(listing.get('id') for listing in browse_listings)
        
        print(f"📊 /api/listings IDs: {len(all_ids)}")
        print(f"📊 /api/marketplace/browse IDs: {len(browse_ids)}")
        
        # Find differences
        only_in_all = all_ids - browse_ids
        only_in_browse = browse_ids - all_ids
        common_ids = all_ids & browse_ids
        
        print(f"📊 Common listings: {len(common_ids)}")
        print(f"📊 Only in /api/listings: {len(only_in_all)}")
        print(f"📊 Only in /api/marketplace/browse: {len(only_in_browse)}")
        
        if only_in_all:
            print("\n🔍 Listings only in /api/listings:")
            for listing in all_listings:
                if listing.get('id') in only_in_all:
                    print(f"   - {listing.get('title', 'N/A')} (Status: {listing.get('status', 'N/A')})")
        
        if only_in_browse:
            print("\n🔍 Listings only in /api/marketplace/browse:")
            for listing in browse_listings:
                if listing.get('id') in only_in_browse:
                    print(f"   - {listing.get('title', 'N/A')} (Status: {listing.get('status', 'N/A')})")

    def test_delete_operations(self, browse_listings):
        """Test DELETE operations on the persistent listings"""
        print("\n🗑️ DELETE OPERATIONS TEST")
        print("=" * 50)
        
        if len(browse_listings) == 0:
            print("❌ No listings to delete")
            return
        
        print(f"🎯 Testing DELETE on {len(browse_listings)} listings...")
        
        delete_results = []
        for i, listing in enumerate(browse_listings):
            listing_id = listing.get('id')
            title = listing.get('title', 'Unknown')
            
            print(f"\n🗑️ Deleting listing {i+1}/{len(browse_listings)}: {title}")
            print(f"   ID: {listing_id}")
            
            success, response = self.make_request("DELETE", f"api/listings/{listing_id}")
            
            delete_results.append({
                'id': listing_id,
                'title': title,
                'success': success,
                'response': response
            })
            
            if success:
                deleted_count = response.get('deleted_count', 0)
                print(f"   ✅ Delete successful, deleted_count: {deleted_count}")
            else:
                print(f"   ❌ Delete failed: {response}")
        
        return delete_results

    def verify_deletion_persistence(self):
        """Verify if deletions actually persist"""
        print("\n🔄 DELETION PERSISTENCE VERIFICATION")
        print("=" * 50)
        
        # Wait a moment for database operations to complete
        import time
        time.sleep(2)
        
        # Check browse endpoint again
        success, browse_after = self.make_request("GET", "api/marketplace/browse")
        
        if success:
            print(f"📊 Listings remaining after deletion: {len(browse_after)}")
            
            if len(browse_after) > 0:
                print("\n⚠️ PERSISTENT LISTINGS FOUND:")
                for i, listing in enumerate(browse_after):
                    print(f"   {i+1}. ID: {listing.get('id', 'N/A')[:8]}...")
                    print(f"      Title: {listing.get('title', 'N/A')}")
                    print(f"      Status: {listing.get('status', 'N/A')}")
                    print(f"      Category: {listing.get('category', 'N/A')}")
                    print(f"      Seller: {listing.get('seller_id', 'N/A')}")
                    print(f"      Created: {listing.get('created_at', 'N/A')}")
                    
                    # Check if this is a special listing
                    if listing.get('seller_id') in ['demo_seller_1', 'demo_seller_2', 'demo_seller_3']:
                        print(f"      🎯 DEMO/SEED DATA DETECTED!")
                    
                    print()
                
                self.persistent_listings = browse_after
                return False  # Listings still exist
            else:
                print("✅ All listings successfully deleted")
                return True
        else:
            print("❌ Could not verify deletion")
            return False

    def analyze_persistent_listings(self):
        """Analyze the structure of persistent listings"""
        if not self.persistent_listings:
            print("\n✅ No persistent listings to analyze")
            return
        
        print("\n🔬 PERSISTENT LISTINGS ANALYSIS")
        print("=" * 50)
        
        print(f"📊 Found {len(self.persistent_listings)} persistent listings")
        
        # Analyze common characteristics
        sellers = set()
        categories = set()
        statuses = set()
        has_demo_data = False
        
        for listing in self.persistent_listings:
            sellers.add(listing.get('seller_id', 'unknown'))
            categories.add(listing.get('category', 'unknown'))
            statuses.add(listing.get('status', 'unknown'))
            
            # Check for demo/seed data indicators
            seller_id = listing.get('seller_id', '')
            if 'demo_seller' in seller_id or seller_id in ['demo_seller_1', 'demo_seller_2', 'demo_seller_3']:
                has_demo_data = True
        
        print(f"📊 Unique sellers: {sellers}")
        print(f"📊 Unique categories: {categories}")
        print(f"📊 Unique statuses: {statuses}")
        print(f"📊 Contains demo/seed data: {has_demo_data}")
        
        # Check for special metadata
        print("\n🔍 Detailed analysis of each persistent listing:")
        for i, listing in enumerate(self.persistent_listings):
            print(f"\n   Listing {i+1}:")
            print(f"   ID: {listing.get('id')}")
            print(f"   Title: {listing.get('title')}")
            print(f"   Seller ID: {listing.get('seller_id')}")
            print(f"   Status: {listing.get('status')}")
            print(f"   Created: {listing.get('created_at')}")
            
            # Check for special fields
            special_fields = []
            for key, value in listing.items():
                if key not in ['id', 'title', 'description', 'price', 'category', 'condition', 'seller_id', 'images', 'status', 'created_at', 'updated_at']:
                    special_fields.append(f"{key}: {value}")
            
            if special_fields:
                print(f"   Special fields: {special_fields}")

    def test_admin_panel_data_source(self):
        """Test where admin panel gets its listing data"""
        print("\n🎛️ ADMIN PANEL DATA SOURCE TEST")
        print("=" * 50)
        
        # Test admin dashboard
        success, dashboard = self.make_request("GET", "api/admin/dashboard")
        
        if success and 'kpis' in dashboard:
            kpis = dashboard['kpis']
            print(f"📊 Admin Dashboard KPIs:")
            print(f"   Total Listings: {kpis.get('total_listings', 'N/A')}")
            print(f"   Active Listings: {kpis.get('active_listings', 'N/A')}")
            print(f"   Total Users: {kpis.get('total_users', 'N/A')}")
        
        # Test admin users endpoint
        success, users = self.make_request("GET", "api/admin/users")
        
        if success:
            print(f"📊 Admin Users: {len(users)} users found")
            
            # Check for demo sellers
            demo_sellers = []
            for user in users:
                user_id = user.get('id', '')
                if 'demo' in user_id.lower() or user.get('username', '').startswith('demo'):
                    demo_sellers.append(user)
            
            print(f"📊 Demo/System Users: {len(demo_sellers)}")
            for demo_user in demo_sellers:
                print(f"   - {demo_user.get('username', 'N/A')} (ID: {demo_user.get('id', 'N/A')[:8]}...)")

    def run_comprehensive_debug(self):
        """Run comprehensive debug analysis"""
        print("🔍 ADMIN PANEL LISTINGS DEBUG")
        print("=" * 60)
        print("Investigating persistent 6 listings issue...")
        
        # Step 1: Admin login
        if not self.admin_login():
            return False
        
        # Step 2: Analyze database state
        all_listings = self.analyze_database_listings()
        
        # Step 3: Analyze browse endpoint
        browse_listings = self.analyze_browse_endpoint()
        
        # Step 4: Compare endpoints
        if all_listings and browse_listings:
            self.compare_endpoints(all_listings, browse_listings)
        
        # Step 5: Test admin panel data sources
        self.test_admin_panel_data_source()
        
        # Step 6: Test delete operations on current listings
        if browse_listings:
            delete_results = self.test_delete_operations(browse_listings)
            
            # Step 7: Verify deletion persistence
            deletion_successful = self.verify_deletion_persistence()
            
            # Step 8: Analyze any persistent listings
            self.analyze_persistent_listings()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 DEBUG SUMMARY")
        print("=" * 60)
        
        if self.persistent_listings:
            print(f"❌ ISSUE CONFIRMED: {len(self.persistent_listings)} listings persist after deletion")
            print("\n🔍 ROOT CAUSE ANALYSIS:")
            
            # Check for demo data
            demo_data_found = any(
                listing.get('seller_id', '').startswith('demo_seller') 
                for listing in self.persistent_listings
            )
            
            if demo_data_found:
                print("   🎯 LIKELY CAUSE: Demo/Seed data that regenerates automatically")
                print("   📋 RECOMMENDATION: Check backend code for automatic demo data creation")
            else:
                print("   🎯 LIKELY CAUSE: Database constraint or special status preventing deletion")
                print("   📋 RECOMMENDATION: Check for special flags or constraints on these listings")
            
            print(f"\n📊 Persistent listings details:")
            for listing in self.persistent_listings:
                print(f"   - {listing.get('title', 'N/A')} (Seller: {listing.get('seller_id', 'N/A')})")
        else:
            print("✅ NO PERSISTENT LISTINGS: All listings deleted successfully")
        
        return True

def main():
    """Main debug execution"""
    debugger = AdminListingsDebugger()
    success = debugger.run_comprehensive_debug()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())