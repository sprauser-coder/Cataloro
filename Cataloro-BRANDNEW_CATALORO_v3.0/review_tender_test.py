#!/usr/bin/env python3
"""
Review Request: Tender Offerer Display Bug Test
Tests the specific admin user ID and tender visibility issue
"""

import requests
import sys
import json
from datetime import datetime

class ReviewTenderTester:
    def __init__(self, base_url="https://market-refactor.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_user_id = "68b191ec38e6062fee10bd27"  # From review request
        self.session = requests.Session()

    def make_request(self, method, endpoint, data=None):
        """Make HTTP request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            
            return response.status_code, response.json() if response.text else {}
        except Exception as e:
            print(f"Request error: {str(e)}")
            return 500, {}

    def test_admin_listings(self):
        """1. Check what listings the current admin user has"""
        print(f"🔍 1. Checking listings for admin user ID: {self.admin_user_id}")
        
        status, response = self.make_request('GET', f'api/user/my-listings/{self.admin_user_id}')
        
        print(f"   Status: {status}")
        if status == 200:
            print(f"   Found {len(response)} listings for admin user")
            for i, listing in enumerate(response):
                print(f"     {i+1}. {listing.get('title', 'No title')} - €{listing.get('price', 0)} (ID: {listing.get('id', 'No ID')[:8]}...)")
            return response
        else:
            print(f"   Error: {response}")
            return []

    def test_existing_tenders(self):
        """2. Check what tenders exist in the database and which seller IDs they belong to"""
        print(f"\n🔍 2. Checking existing tenders for admin user")
        
        status, response = self.make_request('GET', f'api/tenders/seller/{self.admin_user_id}/overview')
        
        print(f"   Status: {status}")
        if status == 200:
            print(f"   Seller overview response type: {type(response)}")
            
            if isinstance(response, list):
                total_tenders = 0
                for listing_data in response:
                    tender_count = listing_data.get('tender_count', 0)
                    total_tenders += tender_count
                    listing_title = listing_data.get('listing', {}).get('title', 'Unknown')
                    print(f"     Listing: {listing_title} - {tender_count} tenders")
                
                print(f"   Total tenders found: {total_tenders}")
                return response
            else:
                print(f"   Unexpected response format: {response}")
                return []
        else:
            print(f"   Error: {response}")
            return []

    def create_test_tender_offers(self, admin_listings):
        """3. Create 2-3 tender offers for admin user's listings"""
        print(f"\n💰 3. Creating tender offers for admin user's listings")
        
        if not admin_listings:
            print("   No admin listings available - creating test listing first")
            
            # Create a test listing for the admin user
            test_listing = {
                "title": "Test Listing for Tender - Premium Catalyst",
                "description": "Test listing for tender offerer visibility testing",
                "price": 500.00,
                "category": "Catalysts",
                "condition": "Used - Good",
                "seller_id": self.admin_user_id,
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"]
            }
            
            status, response = self.make_request('POST', 'api/listings', test_listing)
            if status == 200:
                listing_id = response.get('listing_id')
                print(f"   ✅ Created test listing: {listing_id}")
                admin_listings = [{"id": listing_id, "title": test_listing["title"], "price": test_listing["price"]}]
            else:
                print(f"   ❌ Failed to create test listing: {response}")
                return []
        
        # Create a test buyer
        buyer_data = {
            "username": f"test_buyer_{int(datetime.now().timestamp())}",
            "email": f"buyer_{int(datetime.now().timestamp())}@test.com",
            "full_name": "Test Buyer for Tender Visibility",
            "is_business": False
        }
        
        status, buyer_response = self.make_request('POST', 'api/auth/register', buyer_data)
        if status != 200:
            print(f"   ❌ Failed to create test buyer: {buyer_response}")
            return []
        
        buyer_id = buyer_response.get('user_id')
        print(f"   ✅ Created test buyer: {buyer_id}")
        
        # Create tender offers
        created_tenders = []
        for i, listing in enumerate(admin_listings[:2]):  # Use first 2 listings
            listing_id = listing.get('id')
            base_price = listing.get('price', 100)
            offer_amount = base_price + (50 * (i + 1))  # Offer more than base price
            
            tender_data = {
                "listing_id": listing_id,
                "buyer_id": buyer_id,
                "offer_amount": offer_amount
            }
            
            status, response = self.make_request('POST', 'api/tenders/submit', tender_data)
            if status == 200:
                tender_id = response.get('tender_id')
                created_tenders.append(tender_id)
                print(f"   ✅ Created tender {i+1}: €{offer_amount} for listing {listing_id[:8]}...")
            else:
                print(f"   ❌ Failed to create tender {i+1}: {response}")
        
        return created_tenders

    def test_seller_overview_endpoint(self):
        """4. Test the seller overview endpoint for the admin user"""
        print(f"\n📊 4. Testing seller overview endpoint for admin user")
        
        status, response = self.make_request('GET', f'api/tenders/seller/{self.admin_user_id}/overview')
        
        print(f"   Status: {status}")
        if status == 200:
            print(f"   ✅ Seller overview endpoint accessible")
            
            if isinstance(response, list):
                for i, listing_data in enumerate(response):
                    listing_info = listing_data.get('listing', {})
                    seller_info = listing_data.get('seller', {})
                    tenders = listing_data.get('tenders', [])
                    
                    print(f"\n   Listing {i+1}: {listing_info.get('title', 'Unknown')}")
                    print(f"     Seller info populated: {bool(seller_info.get('id'))}")
                    print(f"     Tender count: {len(tenders)}")
                    
                    for j, tender in enumerate(tenders):
                        buyer_info = tender.get('buyer', {})
                        print(f"     Tender {j+1}: €{tender.get('offer_amount', 0)}")
                        print(f"       Buyer ID: {buyer_info.get('id', 'Missing')}")
                        print(f"       Buyer full_name: {buyer_info.get('full_name', 'Missing')}")
                        print(f"       Buyer username: {buyer_info.get('username', 'Missing')}")
                
                return response
            else:
                print(f"   Unexpected response format: {response}")
                return []
        else:
            print(f"   ❌ Seller overview endpoint failed: {response}")
            return []

    def verify_tender_buyer_information(self, seller_overview_data):
        """5. Verify the tender data includes complete buyer information"""
        print(f"\n🔍 5. Verifying tender data includes complete buyer information")
        
        if not seller_overview_data:
            print("   ❌ No seller overview data to verify")
            return False
        
        complete_info_count = 0
        total_tenders = 0
        display_examples = []
        
        for listing_data in seller_overview_data:
            tenders = listing_data.get('tenders', [])
            total_tenders += len(tenders)
            
            for tender in tenders:
                buyer_info = tender.get('buyer', {})
                offer_amount = tender.get('offer_amount', 0)
                
                # Check if buyer information is complete
                has_id = bool(buyer_info.get('id'))
                has_full_name = bool(buyer_info.get('full_name'))
                has_username = bool(buyer_info.get('username'))
                
                if has_id and has_full_name and has_username:
                    complete_info_count += 1
                    
                    # Create display example for frontend
                    buyer_name = buyer_info.get('full_name') or buyer_info.get('username')
                    display_text = f"€{offer_amount:.2f} by {buyer_name}"
                    display_examples.append(display_text)
                    print(f"   ✅ Complete buyer info: {display_text}")
                else:
                    print(f"   ❌ Incomplete buyer info - ID: {has_id}, Name: {has_full_name}, Username: {has_username}")
        
        print(f"\n   Summary: {complete_info_count}/{total_tenders} tenders have complete buyer information")
        
        if display_examples:
            print(f"   Frontend display examples:")
            for example in display_examples:
                print(f"     - {example}")
        
        return complete_info_count == total_tenders and total_tenders > 0

    def run_review_test(self):
        """Run the complete review test as requested"""
        print("🎯 TENDER OFFERER DISPLAY BUG VERIFICATION")
        print("=" * 60)
        print(f"Testing admin user ID: {self.admin_user_id}")
        print(f"Backend URL: {self.base_url}")
        
        # Step 1: Check admin user listings
        admin_listings = self.test_admin_listings()
        
        # Step 2: Check existing tenders
        existing_tenders = self.test_existing_tenders()
        
        # Step 3: Create tender offers if needed
        created_tenders = self.create_test_tender_offers(admin_listings)
        
        # Step 4: Test seller overview endpoint
        seller_overview_data = self.test_seller_overview_endpoint()
        
        # Step 5: Verify buyer information completeness
        buyer_info_complete = self.verify_tender_buyer_information(seller_overview_data)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 REVIEW TEST RESULTS")
        print("=" * 60)
        
        print(f"✅ Admin user listings: {len(admin_listings)} found")
        print(f"✅ Existing tenders checked: {len(existing_tenders) if existing_tenders else 0}")
        print(f"✅ New tender offers created: {len(created_tenders)}")
        print(f"✅ Seller overview endpoint: {'Working' if seller_overview_data else 'Failed'}")
        print(f"✅ Complete buyer information: {'Yes' if buyer_info_complete else 'No'}")
        
        if buyer_info_complete:
            print("\n🎉 SUCCESS: Tender offerer display bug appears to be resolved!")
            print("   Frontend can now display complete 'by [buyer name]' information")
        else:
            print("\n⚠️  ISSUE: Tender offerer display bug still exists")
            print("   Frontend cannot display complete buyer information")
        
        return buyer_info_complete

if __name__ == "__main__":
    tester = ReviewTenderTester()
    success = tester.run_review_test()
    sys.exit(0 if success else 1)