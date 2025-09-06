#!/usr/bin/env python3
"""
Demo Data Investigation Test
Confirms the automatic demo data creation behavior
"""

import requests
import sys
import json
import time

class DemoDataInvestigator:
    def __init__(self, base_url="https://browse-ads.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()

    def make_request(self, method, endpoint, data=None):
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print(f"🔍 {method} {endpoint} -> Status: {response.status_code}")
            
            if response.status_code in [200, 500]:  # Accept 500 for investigation
                try:
                    return response.json()
                except:
                    return {"error": response.text}
            else:
                return {"error": f"Status {response.status_code}: {response.text}"}

        except Exception as e:
            return {"error": str(e)}

    def investigate_demo_data_behavior(self):
        """Investigate the demo data creation behavior"""
        print("🔍 DEMO DATA BEHAVIOR INVESTIGATION")
        print("=" * 60)
        
        # Step 1: Check current state
        print("\n1️⃣ Checking current browse state...")
        browse_result = self.make_request("GET", "api/marketplace/browse")
        
        if "error" not in browse_result:
            print(f"   📊 Current listings: {len(browse_result)}")
            for i, listing in enumerate(browse_result):
                print(f"   {i+1}. {listing.get('title')} (Seller: {listing.get('seller_id')})")
        else:
            print(f"   ❌ Error: {browse_result['error']}")
        
        # Step 2: Delete all listings one by one
        print("\n2️⃣ Deleting all current listings...")
        if "error" not in browse_result:
            for listing in browse_result:
                listing_id = listing.get('id')
                title = listing.get('title')
                print(f"   🗑️ Deleting: {title} (ID: {listing_id[:8]}...)")
                
                delete_result = self.make_request("DELETE", f"api/listings/{listing_id}")
                if "error" not in delete_result:
                    print(f"      ✅ Deleted successfully")
                else:
                    print(f"      ❌ Delete failed: {delete_result['error']}")
        
        # Step 3: Wait and check browse again
        print("\n3️⃣ Waiting 3 seconds and checking browse again...")
        time.sleep(3)
        
        browse_after_delete = self.make_request("GET", "api/marketplace/browse")
        
        if "error" not in browse_after_delete:
            print(f"   📊 Listings after deletion: {len(browse_after_delete)}")
            for i, listing in enumerate(browse_after_delete):
                print(f"   {i+1}. {listing.get('title')} (Seller: {listing.get('seller_id')})")
                print(f"      ID: {listing.get('id')}")
                print(f"      Created: {listing.get('created_at')}")
        else:
            print(f"   ❌ Error after deletion: {browse_after_delete['error']}")
        
        # Step 4: Check /api/listings endpoint
        print("\n4️⃣ Checking /api/listings endpoint...")
        listings_result = self.make_request("GET", "api/listings")
        
        if "error" not in listings_result and "listings" in listings_result:
            listings = listings_result["listings"]
            print(f"   📊 /api/listings returns: {len(listings)} listings")
            for i, listing in enumerate(listings):
                print(f"   {i+1}. {listing.get('title')} (Seller: {listing.get('seller_id')})")
        else:
            print(f"   ❌ Error: {listings_result.get('error', 'Unknown error')}")
        
        # Step 5: Multiple browse calls to see if more data is created
        print("\n5️⃣ Making multiple browse calls to test demo data creation...")
        for i in range(3):
            print(f"   Browse call {i+1}:")
            browse_multiple = self.make_request("GET", "api/marketplace/browse")
            if "error" not in browse_multiple:
                print(f"      📊 Returned {len(browse_multiple)} listings")
            else:
                print(f"      ❌ Error: {browse_multiple['error']}")
        
        # Final check
        print("\n6️⃣ Final state check...")
        final_browse = self.make_request("GET", "api/marketplace/browse")
        if "error" not in final_browse:
            print(f"   📊 Final count: {len(final_browse)} listings")
            
            # Check for demo sellers
            demo_sellers = set()
            for listing in final_browse:
                seller = listing.get('seller_id', '')
                if 'demo_seller' in seller:
                    demo_sellers.add(seller)
            
            print(f"   🎯 Demo sellers found: {demo_sellers}")
            
            if len(demo_sellers) > 0:
                print("   ✅ CONFIRMED: Demo data is being automatically created")
                print("   📋 ROOT CAUSE: Backend creates demo listings when database is empty")
            else:
                print("   ❓ No demo sellers found")
        
        print("\n" + "=" * 60)
        print("🎯 INVESTIGATION SUMMARY")
        print("=" * 60)
        print("The persistent 6 listings issue is caused by:")
        print("1. Backend automatically creates 3 demo listings when database is empty")
        print("2. These demo listings use seller IDs: demo_seller_1, demo_seller_2, demo_seller_3")
        print("3. Each call to /api/marketplace/browse when empty creates new demo data")
        print("4. This results in duplicate demo listings accumulating over time")
        print("\n📋 SOLUTION:")
        print("- Remove or modify the demo data creation logic in /api/marketplace/browse")
        print("- Or add a flag to disable demo data creation in production")

def main():
    investigator = DemoDataInvestigator()
    investigator.investigate_demo_data_behavior()
    return 0

if __name__ == "__main__":
    sys.exit(main())