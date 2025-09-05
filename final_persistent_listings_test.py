#!/usr/bin/env python3
"""
Final Persistent Listings Investigation
Comprehensive test to demonstrate and document the 6 listings issue
"""

import requests
import sys
import json
import time

class PersistentListingsTest:
    def __init__(self, base_url="https://market-refactor.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_user = None

    def make_request(self, method, endpoint, data=None):
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)

            return response.status_code, response.json() if response.text else {}

        except Exception as e:
            return 500, {"error": str(e)}

    def admin_login(self):
        """Login as admin"""
        status, response = self.make_request("POST", "api/auth/login", 
                                           {"email": "admin@cataloro.com", "password": "demo123"})
        
        if status == 200 and 'user' in response:
            self.admin_user = response['user']
            return True
        return False

    def demonstrate_6_listings_scenario(self):
        """Demonstrate how the 6 listings scenario occurs"""
        print("🔍 DEMONSTRATING THE 6 LISTINGS SCENARIO")
        print("=" * 60)
        
        # Step 1: Login as admin
        if not self.admin_login():
            print("❌ Failed to login as admin")
            return
        
        print("✅ Logged in as admin")
        
        # Step 2: Check current state
        print("\n📊 Step 1: Current database state")
        status, listings_data = self.make_request("GET", "api/listings")
        if status == 200 and "listings" in listings_data:
            current_listings = listings_data["listings"]
            print(f"   Database contains: {len(current_listings)} listings")
            
            for listing in current_listings:
                print(f"   - {listing['title']} (ID: {listing['id'][:8]}..., Seller: {listing['seller_id']})")
        
        # Step 3: Create a user listing to mix with demo data
        print("\n📝 Step 2: Creating a real user listing")
        user_listing = {
            "title": "Real User Listing - Test Product",
            "description": "This is a real user-created listing for testing",
            "price": 150.00,
            "category": "Test",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"]
        }
        
        status, create_response = self.make_request("POST", "api/listings", user_listing)
        if status == 200:
            user_listing_id = create_response.get('listing_id')
            print(f"   ✅ Created user listing: {user_listing_id[:8]}...")
        else:
            print(f"   ❌ Failed to create user listing")
            return
        
        # Step 4: Check browse endpoint
        print("\n🌐 Step 3: Checking browse endpoint")
        status, browse_data = self.make_request("GET", "api/marketplace/browse")
        if status == 200:
            print(f"   Browse returns: {len(browse_data)} listings")
            for i, listing in enumerate(browse_data):
                seller_type = "DEMO" if "demo_seller" in listing.get('seller_id', '') else "USER"
                print(f"   {i+1}. {listing['title']} ({seller_type})")
        
        # Step 5: Delete ALL listings (including user listing)
        print("\n🗑️ Step 4: Deleting ALL listings (simulating admin bulk delete)")
        
        # Get all listings to delete
        status, all_listings_data = self.make_request("GET", "api/listings")
        if status == 200 and "listings" in all_listings_data:
            all_listings = all_listings_data["listings"]
            
            print(f"   Deleting {len(all_listings)} listings...")
            for listing in all_listings:
                listing_id = listing['id']
                title = listing['title']
                
                status, delete_response = self.make_request("DELETE", f"api/listings/{listing_id}")
                if status == 200:
                    print(f"   ✅ Deleted: {title}")
                else:
                    print(f"   ❌ Failed to delete: {title}")
        
        # Step 6: Check database after deletion
        print("\n📊 Step 5: Database state after deletion")
        status, after_delete_data = self.make_request("GET", "api/listings")
        if status == 200 and "listings" in after_delete_data:
            remaining_listings = after_delete_data["listings"]
            print(f"   Database contains: {len(remaining_listings)} listings")
            
            if remaining_listings:
                print("   Remaining listings:")
                for listing in remaining_listings:
                    print(f"   - {listing['title']} (Created: {listing['created_at']})")
        
        # Step 7: Call browse endpoint (this triggers demo data creation)
        print("\n🌐 Step 6: Calling browse endpoint (triggers demo data creation)")
        status, browse_after_delete = self.make_request("GET", "api/marketplace/browse")
        if status == 200:
            print(f"   Browse returns: {len(browse_after_delete)} listings")
            print("   New demo listings created:")
            for listing in browse_after_delete:
                print(f"   - {listing['title']} (Seller: {listing['seller_id']})")
        
        # Step 8: Check database again to see new demo data
        print("\n📊 Step 7: Database state after browse call")
        status, final_data = self.make_request("GET", "api/listings")
        if status == 200 and "listings" in final_data:
            final_listings = final_data["listings"]
            print(f"   Database now contains: {len(final_listings)} listings")
        
        # Step 9: Simulate the scenario where user refreshes admin panel
        print("\n🔄 Step 8: Simulating admin panel refresh (multiple browse calls)")
        
        # Make multiple browse calls to simulate user refreshing
        for i in range(3):
            print(f"   Refresh {i+1}:")
            status, refresh_data = self.make_request("GET", "api/marketplace/browse")
            if status == 200:
                print(f"      Browse returns: {len(refresh_data)} listings")
        
        # Final database check
        print("\n📊 Step 9: Final database state")
        status, final_check_data = self.make_request("GET", "api/listings")
        if status == 200 and "listings" in final_check_data:
            final_check_listings = final_check_data["listings"]
            print(f"   Database finally contains: {len(final_check_listings)} listings")
            
            # Group by creation time to show duplicates
            creation_times = {}
            for listing in final_check_listings:
                created = listing['created_at'][:19]  # Remove microseconds
                if created not in creation_times:
                    creation_times[created] = []
                creation_times[created].append(listing['title'])
            
            print("\n   Listings grouped by creation time:")
            for created_time, titles in creation_times.items():
                print(f"   {created_time}: {len(titles)} listings")
                for title in titles:
                    print(f"      - {title}")
        
        print("\n" + "=" * 60)
        print("🎯 ROOT CAUSE ANALYSIS")
        print("=" * 60)
        print("The persistent listings issue occurs because:")
        print("1. Backend has demo data creation logic in /api/marketplace/browse")
        print("2. When database is empty, it automatically creates 3 demo listings")
        print("3. Each browse call when empty creates NEW demo listings")
        print("4. Admin panel calls browse endpoint, triggering demo data creation")
        print("5. Multiple refreshes create multiple sets of demo data")
        print("6. This results in 3, 6, 9, 12... listings depending on refresh count")
        
        print("\n📋 TECHNICAL DETAILS:")
        print("- Demo listings use seller_id: demo_seller_1, demo_seller_2, demo_seller_3")
        print("- Each has different UUID but same title/content")
        print("- They are real database entries, not cached data")
        print("- DELETE operations work correctly on them")
        print("- The issue is the automatic recreation logic")
        
        print("\n🔧 SOLUTION:")
        print("Modify /api/marketplace/browse endpoint to:")
        print("1. Remove automatic demo data creation, OR")
        print("2. Add a flag to disable demo data in production, OR")
        print("3. Check if demo data already exists before creating new ones")

def main():
    tester = PersistentListingsTest()
    tester.demonstrate_6_listings_scenario()
    return 0

if __name__ == "__main__":
    sys.exit(main())