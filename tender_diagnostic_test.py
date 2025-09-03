#!/usr/bin/env python3
"""
Tender Diagnostic Test
Detailed investigation of the tender offerer visibility issue
"""

import requests
import json

class TenderDiagnosticTester:
    def __init__(self, base_url="https://cataloro-marketplace-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()

    def run_api_call(self, method, endpoint, data=None):
        """Make API call and return response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            return response.status_code, response.json() if response.text else {}
            
        except Exception as e:
            print(f"API call error: {str(e)}")
            return 0, {}

    def investigate_issue(self):
        """Investigate the tender visibility issue"""
        print("🔍 TENDER VISIBILITY DIAGNOSTIC")
        print("=" * 50)
        
        # Step 1: Login as seller
        print("\n1️⃣ Logging in as seller...")
        seller_data = {"email": "seller@tendertest.com", "password": "test123"}
        status, response = self.run_api_call('POST', 'api/auth/login', seller_data)
        
        if status != 200:
            print(f"❌ Seller login failed: {status}")
            return
        
        seller_user = response.get('user')
        seller_id = seller_user['id']
        print(f"✅ Seller logged in: {seller_user['username']} (ID: {seller_id})")
        
        # Step 2: Check seller profile directly
        print(f"\n2️⃣ Checking seller profile directly...")
        status, profile = self.run_api_call('GET', f'api/auth/profile/{seller_id}')
        
        if status == 200:
            print(f"✅ Seller profile found:")
            print(f"   ID: {profile.get('id')}")
            print(f"   Username: {profile.get('username')}")
            print(f"   Full Name: {profile.get('full_name')}")
            print(f"   Is Business: {profile.get('is_business')}")
            print(f"   Business Name: {profile.get('business_name')}")
        else:
            print(f"❌ Seller profile not found: {status}")
        
        # Step 3: Check seller overview endpoint
        print(f"\n3️⃣ Checking seller overview endpoint...")
        status, overview = self.run_api_call('GET', f'api/tenders/seller/{seller_id}/overview')
        
        if status == 200:
            print(f"✅ Seller overview retrieved:")
            print(f"   Response type: {type(overview)}")
            print(f"   Number of listings: {len(overview) if isinstance(overview, list) else 'Not a list'}")
            
            if isinstance(overview, list) and len(overview) > 0:
                first_listing = overview[0]
                print(f"\n   First listing analysis:")
                print(f"   - Listing ID: {first_listing.get('listing', {}).get('id', 'Missing')}")
                print(f"   - Listing Title: {first_listing.get('listing', {}).get('title', 'Missing')}")
                print(f"   - Seller Info: {first_listing.get('seller', 'Missing')}")
                print(f"   - Tender Count: {first_listing.get('tender_count', 'Missing')}")
                print(f"   - Tenders: {len(first_listing.get('tenders', []))}")
                
                # Check if seller info is empty
                seller_info = first_listing.get('seller', {})
                if not seller_info or not seller_info.get('id'):
                    print(f"\n❌ ISSUE CONFIRMED: Seller information is empty or missing ID")
                    print(f"   Expected seller ID: {seller_id}")
                    print(f"   Actual seller info: {seller_info}")
                else:
                    print(f"\n✅ Seller information populated correctly")
        else:
            print(f"❌ Seller overview failed: {status}")
        
        # Step 4: Check if there are any tenders in the database
        print(f"\n4️⃣ Checking for existing tenders...")
        
        # Login as buyer to check tenders
        buyer_data = {"email": "buyer@tendertest.com", "password": "test123"}
        status, response = self.run_api_call('POST', 'api/auth/login', buyer_data)
        
        if status == 200:
            buyer_user = response.get('user')
            buyer_id = buyer_user['id']
            print(f"✅ Buyer logged in: {buyer_user['username']} (ID: {buyer_id})")
            
            # Check buyer's tenders
            status, buyer_tenders = self.run_api_call('GET', f'api/tenders/buyer/{buyer_id}')
            
            if status == 200:
                print(f"✅ Buyer tenders retrieved: {len(buyer_tenders)} tenders found")
                
                for i, tender in enumerate(buyer_tenders):
                    print(f"   Tender {i+1}:")
                    print(f"   - ID: {tender.get('id')}")
                    print(f"   - Listing ID: {tender.get('listing', {}).get('id')}")
                    print(f"   - Offer Amount: €{tender.get('offer_amount')}")
                    print(f"   - Status: {tender.get('status')}")
            else:
                print(f"❌ Could not retrieve buyer tenders: {status}")
        
        # Step 5: Check marketplace browse to see listings
        print(f"\n5️⃣ Checking marketplace browse...")
        status, browse = self.run_api_call('GET', 'api/marketplace/browse')
        
        if status == 200:
            print(f"✅ Browse listings retrieved: {len(browse)} listings found")
            
            # Look for seller's listings
            seller_listings = [listing for listing in browse if listing.get('seller_id') == seller_id]
            print(f"   Seller's listings in browse: {len(seller_listings)}")
            
            for listing in seller_listings:
                print(f"   - Listing: {listing.get('title')} (ID: {listing.get('id')})")
        else:
            print(f"❌ Could not retrieve browse listings: {status}")

if __name__ == "__main__":
    tester = TenderDiagnosticTester()
    tester.investigate_issue()