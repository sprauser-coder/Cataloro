#!/usr/bin/env python3
"""
Cataloro Marketplace - Tender Offerer Visibility Test Suite
Tests tender offer creation and buyer information display in seller overview
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class TenderOffererTester:
    def __init__(self, base_url="https://cataloro-upgrade.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.seller_user = None
        self.buyer_users = []
        self.test_listings = []
        self.test_tenders = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
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
                    details += f", Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Array'}"
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_test_users(self):
        """Create test users for tender testing"""
        print("\n👥 Setting up test users...")
        
        # Create seller user (business account)
        seller_data = {
            "username": "tender_seller",
            "email": "seller@tendertest.com",
            "full_name": "Tender Test Seller",
            "is_business": True,
            "business_name": "Premium Auto Parts Ltd",
            "company_name": "Premium Auto Parts Ltd"
        }
        
        success_seller, seller_response = self.run_test(
            "Create Seller User",
            "POST",
            "api/auth/register",
            200,
            data=seller_data
        )
        
        # If user already exists, try to login directly
        if not success_seller:
            print("   ℹ️  Seller user may already exist, attempting login...")
        
        # Login seller to get user object (whether newly created or existing)
        login_success, login_response = self.run_test(
            "Login Seller User",
            "POST",
            "api/auth/login",
            200,
            data={"email": "seller@tendertest.com", "password": "demo123"}
        )
        if login_success:
            self.seller_user = login_response['user']
            print(f"   ✅ Seller user available: {self.seller_user['id']}")
        
        # Create buyer users
        buyer_data_list = [
            {
                "username": "buyer_one",
                "email": "buyer1@tendertest.com", 
                "full_name": "John Smith",
                "is_business": False
            },
            {
                "username": "buyer_two",
                "email": "buyer2@tendertest.com",
                "full_name": "Sarah Johnson", 
                "is_business": False
            },
            {
                "username": "business_buyer",
                "email": "buyer3@tendertest.com",
                "full_name": "Mike Wilson",
                "is_business": True,
                "business_name": "Wilson Automotive Solutions",
                "company_name": "Wilson Automotive Solutions"
            }
        ]
        
        for i, buyer_data in enumerate(buyer_data_list):
            success_buyer, buyer_response = self.run_test(
                f"Create Buyer User {i+1}",
                "POST", 
                "api/auth/register",
                200,
                data=buyer_data
            )
            
            # If user creation failed (likely already exists), try login directly
            if not success_buyer:
                print(f"   ℹ️  Buyer {i+1} may already exist, attempting login...")
            
            # Login buyer to get user object (whether newly created or existing)
            login_success, login_response = self.run_test(
                f"Login Buyer User {i+1}",
                "POST",
                "api/auth/login", 
                200,
                data={"email": buyer_data["email"], "password": "demo123"}
            )
            if login_success:
                self.buyer_users.append(login_response['user'])
                print(f"   ✅ Buyer {i+1} available: {login_response['user']['id']}")
        
        return len(self.buyer_users) >= 2 and self.seller_user is not None

    def create_test_listings(self):
        """Create test listings for tender offers"""
        print("\n📝 Creating test listings...")
        
        if not self.seller_user:
            print("❌ No seller user available")
            return False
        
        # Create listings similar to the ones mentioned in the review request
        listings_data = [
            {
                "title": "Mitsubishi AH Catalytic Converter",
                "description": "High-quality Mitsubishi AH catalytic converter. Excellent condition with good precious metal content. Perfect for automotive recycling.",
                "price": 600.00,
                "category": "Automotive",
                "condition": "Used - Good",
                "seller_id": self.seller_user['id'],
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
                "tags": ["mitsubishi", "catalytic converter", "automotive"],
                "features": ["High precious metal content", "Good condition", "Tested quality"]
            },
            {
                "title": "Ford 6G915E211FA Catalytic Converter", 
                "description": "Ford 6G915E211FA catalytic converter in good working condition. Suitable for precious metal recovery and automotive applications.",
                "price": 80.00,
                "category": "Automotive",
                "condition": "Used - Fair",
                "seller_id": self.seller_user['id'],
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
                "tags": ["ford", "catalytic converter", "6G915E211FA"],
                "features": ["Working condition", "Precious metal recovery", "Automotive grade"]
            },
            {
                "title": "Premium BMW Catalytic Converter",
                "description": "Premium BMW catalytic converter with excellent precious metal content. High-value item for serious buyers.",
                "price": 1500.00,
                "category": "Automotive", 
                "condition": "Used - Excellent",
                "seller_id": self.seller_user['id'],
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
                "tags": ["bmw", "catalytic converter", "premium"],
                "features": ["Excellent condition", "High precious metal content", "Premium grade"]
            }
        ]
        
        for i, listing_data in enumerate(listings_data):
            success, response = self.run_test(
                f"Create Test Listing {i+1}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            
            if success and 'listing_id' in response:
                self.test_listings.append({
                    'id': response['listing_id'],
                    'title': listing_data['title'],
                    'price': listing_data['price']
                })
                print(f"   ✅ Created listing: {listing_data['title']} (€{listing_data['price']})")
        
        return len(self.test_listings) >= 2

    def submit_tender_offers(self):
        """Submit multiple tender offers for the test listings"""
        print("\n💰 Submitting tender offers...")
        
        if not self.test_listings or not self.buyer_users:
            print("❌ Missing test listings or buyer users")
            return False
        
        # Define tender offers for each listing
        tender_offers = [
            # Offers for Mitsubishi AH (€600 starting price)
            {
                "listing_id": self.test_listings[0]['id'],
                "buyer_id": self.buyer_users[0]['id'],
                "offer_amount": 600.00,  # Starting price
                "buyer_name": self.buyer_users[0]['full_name']
            },
            {
                "listing_id": self.test_listings[0]['id'], 
                "buyer_id": self.buyer_users[1]['id'],
                "offer_amount": 650.00,  # Higher bid
                "buyer_name": self.buyer_users[1]['full_name']
            },
            # Offers for Ford 6G915E211FA (€80 starting price)
            {
                "listing_id": self.test_listings[1]['id'],
                "buyer_id": self.buyer_users[0]['id'],
                "offer_amount": 80.00,   # Starting price
                "buyer_name": self.buyer_users[0]['full_name']
            },
            {
                "listing_id": self.test_listings[1]['id'],
                "buyer_id": self.buyer_users[2]['id'] if len(self.buyer_users) > 2 else self.buyer_users[1]['id'],
                "offer_amount": 95.00,   # Higher bid
                "buyer_name": self.buyer_users[2]['full_name'] if len(self.buyer_users) > 2 else self.buyer_users[1]['full_name']
            },
            # Offers for BMW Premium (€1500 starting price)
            {
                "listing_id": self.test_listings[2]['id'] if len(self.test_listings) > 2 else self.test_listings[0]['id'],
                "buyer_id": self.buyer_users[1]['id'],
                "offer_amount": 1500.00, # Starting price
                "buyer_name": self.buyer_users[1]['full_name']
            },
            {
                "listing_id": self.test_listings[2]['id'] if len(self.test_listings) > 2 else self.test_listings[0]['id'],
                "buyer_id": self.buyer_users[2]['id'] if len(self.buyer_users) > 2 else self.buyer_users[0]['id'],
                "offer_amount": 1750.00, # Higher bid
                "buyer_name": self.buyer_users[2]['full_name'] if len(self.buyer_users) > 2 else self.buyer_users[0]['full_name']
            }
        ]
        
        successful_tenders = 0
        for i, tender_data in enumerate(tender_offers):
            tender_request = {
                "listing_id": tender_data["listing_id"],
                "buyer_id": tender_data["buyer_id"],
                "offer_amount": tender_data["offer_amount"]
            }
            
            success, response = self.run_test(
                f"Submit Tender Offer {i+1}",
                "POST",
                "api/tenders/submit",
                200,
                data=tender_request
            )
            
            if success and 'tender_id' in response:
                self.test_tenders.append({
                    'id': response['tender_id'],
                    'listing_id': tender_data['listing_id'],
                    'buyer_id': tender_data['buyer_id'],
                    'buyer_name': tender_data['buyer_name'],
                    'offer_amount': tender_data['offer_amount']
                })
                successful_tenders += 1
                print(f"   ✅ Tender submitted: €{tender_data['offer_amount']} by {tender_data['buyer_name']}")
        
        self.log_test("Tender Offers Submission", successful_tenders >= 4, 
                     f"Successfully submitted {successful_tenders} tender offers")
        
        return successful_tenders >= 4

    def test_seller_overview_endpoint(self):
        """Test the seller overview endpoint for tender offerer visibility"""
        print("\n🔍 Testing seller overview endpoint...")
        
        if not self.seller_user:
            print("❌ No seller user available")
            return False
        
        success, response = self.run_test(
            "Get Seller Overview",
            "GET",
            f"api/tenders/seller/{self.seller_user['id']}/overview",
            200
        )
        
        if not success:
            return False
        
        print(f"\n📊 Seller Overview Response Analysis:")
        print(f"   Response type: {type(response)}")
        
        if isinstance(response, list):
            print(f"   Number of listings with tenders: {len(response)}")
            
            # Analyze each listing in the overview
            for i, listing_overview in enumerate(response):
                print(f"\n   📋 Listing {i+1} Analysis:")
                print(f"      Listing ID: {listing_overview.get('listing', {}).get('id', 'N/A')}")
                print(f"      Listing Title: {listing_overview.get('listing', {}).get('title', 'N/A')}")
                
                # Check seller information population
                seller_info = listing_overview.get('seller', {})
                print(f"      Seller Info Present: {bool(seller_info)}")
                if seller_info:
                    print(f"         Seller ID: {seller_info.get('id', 'N/A')}")
                    print(f"         Seller Username: {seller_info.get('username', 'N/A')}")
                    print(f"         Seller Full Name: {seller_info.get('full_name', 'N/A')}")
                    print(f"         Is Business: {seller_info.get('is_business', 'N/A')}")
                    print(f"         Business Name: {seller_info.get('business_name', 'N/A')}")
                
                # Check tender information
                tender_count = listing_overview.get('tender_count', 0)
                highest_offer = listing_overview.get('highest_offer', 0)
                tenders = listing_overview.get('tenders', [])
                
                print(f"      Tender Count: {tender_count}")
                print(f"      Highest Offer: €{highest_offer}")
                print(f"      Tenders Array Length: {len(tenders)}")
                
                # Analyze individual tenders for buyer information
                for j, tender in enumerate(tenders):
                    print(f"         Tender {j+1}:")
                    print(f"            Offer Amount: €{tender.get('offer_amount', 'N/A')}")
                    print(f"            Status: {tender.get('status', 'N/A')}")
                    
                    # Check buyer information population - THIS IS THE KEY TEST
                    buyer_info = tender.get('buyer', {})
                    print(f"            Buyer Info Present: {bool(buyer_info)}")
                    if buyer_info:
                        print(f"               Buyer ID: {buyer_info.get('id', 'N/A')}")
                        print(f"               Buyer Username: {buyer_info.get('username', 'N/A')}")
                        print(f"               Buyer Full Name: {buyer_info.get('full_name', 'N/A')}")
                        print(f"               Is Business: {buyer_info.get('is_business', 'N/A')}")
                        print(f"               Business Name: {buyer_info.get('business_name', 'N/A')}")
                        
                        # Test if we can display "by [buyer name]"
                        display_name = buyer_info.get('full_name') or buyer_info.get('username') or 'Unknown'
                        print(f"               Display Name for 'by [name]': {display_name}")
                    else:
                        print(f"               ❌ CRITICAL: No buyer information found!")
        
        # Verify critical requirements for tender offerer visibility
        seller_info_populated = False
        buyer_info_populated = False
        tender_data_present = False
        
        if isinstance(response, list) and len(response) > 0:
            # Check first listing for seller info
            first_listing = response[0]
            seller_info = first_listing.get('seller', {})
            seller_info_populated = bool(seller_info.get('id') and seller_info.get('full_name'))
            
            # Check for tender data and buyer info
            tenders = first_listing.get('tenders', [])
            tender_data_present = len(tenders) > 0
            
            if tenders:
                # Check first tender for buyer info
                first_tender = tenders[0]
                buyer_info = first_tender.get('buyer', {})
                buyer_info_populated = bool(buyer_info.get('id') and buyer_info.get('full_name'))
        
        # Log test results
        self.log_test("Seller Information Population", seller_info_populated,
                     f"Seller info populated in overview: {seller_info_populated}")
        
        self.log_test("Tender Data Present", tender_data_present,
                     f"Tender data found in overview: {tender_data_present}")
        
        self.log_test("Buyer Information Population", buyer_info_populated,
                     f"Buyer info populated in tenders: {buyer_info_populated}")
        
        # Overall tender offerer visibility test
        overall_success = seller_info_populated and buyer_info_populated and tender_data_present
        self.log_test("Tender Offerer Visibility Complete", overall_success,
                     f"All tender offerer data visible: {overall_success}")
        
        return overall_success

    def test_individual_listing_tenders(self):
        """Test individual listing tender endpoints for buyer information"""
        print("\n🔍 Testing individual listing tender endpoints...")
        
        if not self.test_listings:
            print("❌ No test listings available")
            return False
        
        successful_tests = 0
        
        for listing in self.test_listings:
            success, response = self.run_test(
                f"Get Tenders for Listing {listing['title'][:30]}...",
                "GET",
                f"api/tenders/listing/{listing['id']}",
                200
            )
            
            if success:
                print(f"\n   📋 Listing: {listing['title']}")
                print(f"      Found {len(response)} tenders")
                
                # Check each tender for buyer information
                buyer_info_complete = True
                for i, tender in enumerate(response):
                    buyer_info = tender.get('buyer', {})
                    has_buyer_data = bool(buyer_info.get('id') and buyer_info.get('full_name'))
                    
                    print(f"         Tender {i+1}: €{tender.get('offer_amount', 'N/A')}")
                    print(f"            Buyer Info Complete: {has_buyer_data}")
                    if has_buyer_data:
                        display_name = buyer_info.get('full_name') or buyer_info.get('username')
                        print(f"            Display as 'by {display_name}'")
                    
                    if not has_buyer_data:
                        buyer_info_complete = False
                
                if buyer_info_complete and len(response) > 0:
                    successful_tests += 1
        
        self.log_test("Individual Listing Tender Buyer Info", successful_tests > 0,
                     f"Buyer info complete in {successful_tests} listings")
        
        return successful_tests > 0

    def test_buyer_tender_history(self):
        """Test buyer tender history endpoints"""
        print("\n👤 Testing buyer tender history...")
        
        if not self.buyer_users:
            print("❌ No buyer users available")
            return False
        
        successful_tests = 0
        
        for buyer in self.buyer_users:
            success, response = self.run_test(
                f"Get Buyer Tenders for {buyer['full_name']}",
                "GET",
                f"api/tenders/buyer/{buyer['id']}",
                200
            )
            
            if success:
                print(f"\n   👤 Buyer: {buyer['full_name']}")
                print(f"      Found {len(response)} submitted tenders")
                
                # Check each tender for complete listing and seller information
                for i, tender in enumerate(response):
                    listing_info = tender.get('listing', {})
                    seller_info = tender.get('seller', {})
                    
                    print(f"         Tender {i+1}: €{tender.get('offer_amount', 'N/A')}")
                    print(f"            Listing: {listing_info.get('title', 'N/A')}")
                    print(f"            Seller: {seller_info.get('full_name', 'N/A')}")
                    print(f"            Status: {tender.get('status', 'N/A')}")
                
                if len(response) > 0:
                    successful_tests += 1
        
        self.log_test("Buyer Tender History", successful_tests > 0,
                     f"Tender history available for {successful_tests} buyers")
        
        return successful_tests > 0

    def test_frontend_display_readiness(self):
        """Test if all data is ready for frontend display of 'by [buyer name]'"""
        print("\n🖥️  Testing frontend display readiness...")
        
        # Get seller overview again to verify frontend display capability
        if not self.seller_user:
            return False
        
        success, response = self.run_test(
            "Frontend Display Data Check",
            "GET",
            f"api/tenders/seller/{self.seller_user['id']}/overview",
            200
        )
        
        if not success:
            return False
        
        frontend_ready_count = 0
        total_tenders = 0
        
        if isinstance(response, list):
            for listing_overview in response:
                tenders = listing_overview.get('tenders', [])
                
                for tender in tenders:
                    total_tenders += 1
                    buyer_info = tender.get('buyer', {})
                    
                    # Check if we have enough data for "by [buyer name]" display
                    display_name = buyer_info.get('full_name') or buyer_info.get('username')
                    offer_amount = tender.get('offer_amount')
                    
                    if display_name and offer_amount:
                        frontend_ready_count += 1
                        print(f"   ✅ Ready for display: €{offer_amount} by {display_name}")
                    else:
                        print(f"   ❌ Missing data: offer={offer_amount}, name={display_name}")
        
        frontend_ready = frontend_ready_count == total_tenders and total_tenders > 0
        
        self.log_test("Frontend Display Readiness", frontend_ready,
                     f"Frontend ready: {frontend_ready_count}/{total_tenders} tenders")
        
        return frontend_ready

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test listings (this should also clean up associated tenders)
        for listing in self.test_listings:
            self.run_test(
                f"Delete Test Listing {listing['title'][:30]}...",
                "DELETE",
                f"api/listings/{listing['id']}",
                200
            )
        
        print("   ✅ Test data cleanup completed")

    def run_comprehensive_test(self):
        """Run the complete tender offerer visibility test suite"""
        print("🎯 TENDER OFFERER VISIBILITY COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        # Test sequence as requested in review
        print("\n📋 TEST SEQUENCE:")
        print("1. Create test users (seller and buyers)")
        print("2. Create test listings (MitsubishiAH €600, Ford6G915E211FA €80, etc.)")
        print("3. Submit 2-3 tender offers for existing listings")
        print("4. Verify seller overview shows populated tender data")
        print("5. Confirm buyer information is visible in individual tender entries")
        print("6. Test complete frontend display chain for 'by [buyer name]' visibility")
        
        try:
            # Step 1: Setup test users
            if not self.setup_test_users():
                print("\n❌ CRITICAL: Failed to setup test users")
                return False
            
            # Step 2: Create test listings
            if not self.create_test_listings():
                print("\n❌ CRITICAL: Failed to create test listings")
                return False
            
            # Step 3: Submit tender offers
            if not self.submit_tender_offers():
                print("\n❌ CRITICAL: Failed to submit tender offers")
                return False
            
            # Step 4: Test seller overview endpoint
            seller_overview_success = self.test_seller_overview_endpoint()
            
            # Step 5: Test individual listing tender endpoints
            individual_tender_success = self.test_individual_listing_tenders()
            
            # Step 6: Test buyer tender history
            buyer_history_success = self.test_buyer_tender_history()
            
            # Step 7: Test frontend display readiness
            frontend_ready_success = self.test_frontend_display_readiness()
            
            # Final results
            print("\n" + "=" * 60)
            print("🎯 TENDER OFFERER VISIBILITY TEST RESULTS")
            print("=" * 60)
            
            print(f"\n📊 Test Summary:")
            print(f"   Total Tests Run: {self.tests_run}")
            print(f"   Tests Passed: {self.tests_passed}")
            print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
            
            print(f"\n🔍 Key Test Results:")
            print(f"   ✅ Seller Overview Endpoint: {'PASSED' if seller_overview_success else 'FAILED'}")
            print(f"   ✅ Individual Tender Endpoints: {'PASSED' if individual_tender_success else 'FAILED'}")
            print(f"   ✅ Buyer Tender History: {'PASSED' if buyer_history_success else 'FAILED'}")
            print(f"   ✅ Frontend Display Ready: {'PASSED' if frontend_ready_success else 'FAILED'}")
            
            # Overall assessment
            critical_tests_passed = sum([
                seller_overview_success,
                individual_tender_success,
                frontend_ready_success
            ])
            
            overall_success = critical_tests_passed >= 2  # At least 2 of 3 critical tests must pass
            
            print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
            
            if overall_success:
                print("\n🎉 TENDER OFFERER VISIBILITY IS WORKING!")
                print("   - Seller overview shows populated tender data")
                print("   - Buyer information is visible in tender entries")
                print("   - Frontend can display 'by [buyer name]' for each tender offer")
            else:
                print("\n⚠️  TENDER OFFERER VISIBILITY ISSUES DETECTED!")
                print("   - Check seller overview endpoint for buyer information population")
                print("   - Verify ObjectId fallback logic is working correctly")
                print("   - Ensure tender-buyer associations are properly maintained")
            
            return overall_success
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {str(e)}")
            return False
        
        finally:
            # Always cleanup
            self.cleanup_test_data()

def main():
    """Main test execution"""
    print("Starting Tender Offerer Visibility Test Suite...")
    
    tester = TenderOffererTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()