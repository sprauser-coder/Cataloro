#!/usr/bin/env python3
"""
Focused Tender Offerer Visibility Test
Tests the specific tender visibility issue as requested in review
"""

import requests
import sys
import json
from datetime import datetime

class TenderVisibilityTester:
    def __init__(self, base_url="https://market-refactor.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.seller_user = None
        self.buyer_user = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def make_request(self, method, endpoint, data=None):
        """Make HTTP request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            return response
        except Exception as e:
            print(f"Request failed: {str(e)}")
            return None

    def setup_users(self):
        """Setup test users"""
        print("\n👥 Setting up test users...")
        
        # Login admin user
        admin_response = self.make_request('POST', 'api/auth/login', {
            "email": "admin@cataloro.com",
            "password": "demo123"
        })
        
        if admin_response and admin_response.status_code == 200:
            self.seller_user = admin_response.json()['user']
            print(f"   ✅ Admin user logged in: {self.seller_user['id']}")
        
        # Login regular user
        user_response = self.make_request('POST', 'api/auth/login', {
            "email": "user@cataloro.com", 
            "password": "demo123"
        })
        
        if user_response and user_response.status_code == 200:
            self.buyer_user = user_response.json()['user']
            print(f"   ✅ Regular user logged in: {self.buyer_user['id']}")
        
        return self.seller_user is not None and self.buyer_user is not None

    def create_test_listings(self):
        """Create test listings as specified in review"""
        print("\n📝 Creating test listings...")
        
        listings = [
            {
                "title": "MitsubishiAH Premium Catalyst",
                "description": "High-quality Mitsubishi catalyst with excellent precious metal content.",
                "price": 600.0,
                "category": "Automotive",
                "condition": "Used - Good",
                "seller_id": self.seller_user['id'],
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"]
            },
            {
                "title": "Ford 6G915E211FA Catalyst Unit",
                "description": "Original Ford catalyst unit 6G915E211FA. Tested and verified.",
                "price": 80.0,
                "category": "Automotive",
                "condition": "Used - Fair", 
                "seller_id": self.seller_user['id'],
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"]
            }
        ]
        
        created_listings = []
        
        for i, listing_data in enumerate(listings):
            response = self.make_request('POST', 'api/listings', listing_data)
            
            if response and response.status_code == 200:
                listing_id = response.json().get('listing_id')
                created_listings.append({
                    'id': listing_id,
                    'title': listing_data['title'],
                    'price': listing_data['price']
                })
                print(f"   ✅ Created listing {i+1}: {listing_id}")
            else:
                print(f"   ❌ Failed to create listing {i+1}")
        
        return created_listings

    def create_tender_offers(self, listings):
        """Create tender offers for the listings"""
        print("\n💰 Creating tender offers...")
        
        tenders = []
        
        # Create offers for MitsubishiAH (€600)
        if len(listings) > 0:
            tender_data = {
                "listing_id": listings[0]['id'],
                "buyer_id": self.buyer_user['id'],
                "offer_amount": 650.0
            }
            
            response = self.make_request('POST', 'api/tenders/submit', tender_data)
            if response and response.status_code == 200:
                tender_id = response.json().get('tender_id')
                tenders.append(tender_id)
                print(f"   ✅ Created tender for MitsubishiAH: €650 - {tender_id}")
        
        # Create offers for Ford (€80)
        if len(listings) > 1:
            tender_data = {
                "listing_id": listings[1]['id'],
                "buyer_id": self.buyer_user['id'],
                "offer_amount": 95.0
            }
            
            response = self.make_request('POST', 'api/tenders/submit', tender_data)
            if response and response.status_code == 200:
                tender_id = response.json().get('tender_id')
                tenders.append(tender_id)
                print(f"   ✅ Created tender for Ford: €95 - {tender_id}")
        
        return tenders

    def test_seller_overview(self):
        """Test the seller overview endpoint for buyer information visibility"""
        print("\n🔍 Testing seller overview endpoint...")
        
        response = self.make_request('GET', f'api/tenders/seller/{self.seller_user["id"]}/overview')
        
        if not response or response.status_code != 200:
            self.log_test("Seller Overview Endpoint", False, f"Status: {response.status_code if response else 'No response'}")
            return False
        
        data = response.json()
        print(f"   📊 Found {len(data)} listings with tender data")
        
        # Analyze the response
        total_tenders = 0
        complete_buyer_info = 0
        seller_info_complete = False
        display_examples = []
        
        for i, listing_overview in enumerate(data):
            listing = listing_overview.get('listing', {})
            seller = listing_overview.get('seller', {})
            tenders = listing_overview.get('tenders', [])
            
            print(f"\n   📋 Listing {i+1}: {listing.get('title', 'Unknown')}")
            print(f"      Price: €{listing.get('price', 0)}")
            print(f"      Tender Count: {len(tenders)}")
            
            # Check seller information
            if seller.get('full_name') and seller.get('username'):
                seller_info_complete = True
                print(f"      ✅ Seller: {seller.get('full_name')} ({seller.get('username')})")
            else:
                print(f"      ❌ Seller info incomplete: {seller}")
            
            # Check buyer information in tenders
            for j, tender in enumerate(tenders):
                buyer = tender.get('buyer', {})
                amount = tender.get('offer_amount', 0)
                total_tenders += 1
                
                buyer_name = buyer.get('full_name') or buyer.get('username')
                if buyer_name:
                    complete_buyer_info += 1
                    display_examples.append(f"€{amount} by {buyer_name}")
                    print(f"         ✅ Tender {j+1}: €{amount} by {buyer_name}")
                else:
                    print(f"         ❌ Tender {j+1}: €{amount} - Missing buyer name")
                    print(f"            Buyer data: {buyer}")
        
        # Test results
        endpoint_accessible = True
        all_buyer_info_complete = complete_buyer_info == total_tenders and total_tenders > 0
        frontend_ready = len(display_examples) > 0
        
        self.log_test("Seller Overview Endpoint Accessible", endpoint_accessible, f"Found {len(data)} listings")
        self.log_test("Seller Information Populated", seller_info_complete, f"Seller info complete: {seller_info_complete}")
        self.log_test("Complete Buyer Information", all_buyer_info_complete, f"{complete_buyer_info}/{total_tenders} tenders have complete buyer info")
        self.log_test("Frontend Display Ready", frontend_ready, f"Can display: {', '.join(display_examples)}")
        
        return endpoint_accessible and seller_info_complete and all_buyer_info_complete and frontend_ready

    def cleanup_listings(self, listings):
        """Clean up test listings"""
        print("\n🧹 Cleaning up test data...")
        
        for listing in listings:
            response = self.make_request('DELETE', f'api/listings/{listing["id"]}')
            if response and response.status_code == 200:
                print(f"   ✅ Deleted listing: {listing['id']}")

    def run_test(self):
        """Run the complete tender visibility test"""
        print("🎯 TENDER OFFERER VISIBILITY TEST")
        print("=" * 50)
        
        # Step 1: Setup users
        if not self.setup_users():
            print("❌ Failed to setup users")
            return False
        
        # Step 2: Create test listings
        listings = self.create_test_listings()
        if len(listings) < 2:
            print("❌ Failed to create required test listings")
            return False
        
        # Step 3: Create tender offers
        tenders = self.create_tender_offers(listings)
        if len(tenders) < 2:
            print("❌ Failed to create required tender offers")
            self.cleanup_listings(listings)
            return False
        
        # Step 4: Test seller overview
        success = self.test_seller_overview()
        
        # Step 5: Cleanup
        self.cleanup_listings(listings)
        
        # Summary
        print(f"\n{'='*50}")
        print(f"🎯 TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if success:
            print("🎉 TENDER OFFERER VISIBILITY TEST PASSED!")
        else:
            print("⚠️  TENDER OFFERER VISIBILITY TEST FAILED")
        
        return success

def main():
    tester = TenderVisibilityTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()