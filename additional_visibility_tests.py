#!/usr/bin/env python3
"""
Additional Tender Visibility Tests
Specific tests for the review request scenarios
"""

import requests
import json

class AdditionalVisibilityTests:
    def __init__(self, base_url="https://market-evolution-1.preview.emergentagent.com"):
        self.base_url = base_url
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
            return response
        except Exception as e:
            print(f"Request failed: {str(e)}")
            return None

    def test_existing_user_data(self):
        """Test with existing users to verify ObjectId fallback works"""
        print("\n🔍 Testing with Existing User Data (ObjectId Format)")
        
        # Try to get existing users first
        response = self.make_request('GET', 'api/admin/users')
        if response and response.status_code == 200:
            users = response.json()
            print(f"   Found {len(users)} existing users")
            
            # Find a user with ObjectId format (24-character hex)
            objectid_user = None
            for user in users:
                user_id = user.get('id', '')
                if len(user_id) == 24 and all(c in '0123456789abcdef' for c in user_id.lower()):
                    objectid_user = user
                    break
            
            if objectid_user:
                user_id = objectid_user['id']
                print(f"   Testing with ObjectId user: {user_id}")
                
                # Test profile endpoint
                profile_response = self.make_request('GET', f'api/auth/profile/{user_id}')
                if profile_response and profile_response.status_code == 200:
                    print(f"   ✅ Profile endpoint works with ObjectId: {user_id}")
                    profile_data = profile_response.json()
                    print(f"   📋 User: {profile_data.get('username', 'Unknown')} ({profile_data.get('full_name', 'No name')})")
                    
                    # Test if this user has any listings to test seller overview
                    listings_response = self.make_request('GET', f'api/user/my-listings/{user_id}')
                    if listings_response and listings_response.status_code == 200:
                        listings = listings_response.json()
                        if listings:
                            print(f"   Found {len(listings)} listings for this user")
                            
                            # Test seller overview endpoint
                            overview_response = self.make_request('GET', f'api/tenders/seller/{user_id}/overview')
                            if overview_response and overview_response.status_code == 200:
                                overview_data = overview_response.json()
                                print(f"   ✅ Seller overview works with ObjectId: {len(overview_data)} listings")
                                
                                # Check if seller info is populated
                                if overview_data:
                                    seller_info = overview_data[0].get('seller', {})
                                    if seller_info and seller_info != {}:
                                        print(f"   ✅ Seller information populated: {seller_info.get('username', 'Unknown')}")
                                    else:
                                        print(f"   ❌ Seller information empty: {seller_info}")
                            else:
                                print(f"   ❌ Seller overview failed: {overview_response.status_code if overview_response else 'No response'}")
                        else:
                            print(f"   No listings found for user {user_id}")
                    else:
                        print(f"   ❌ My listings failed: {listings_response.status_code if listings_response else 'No response'}")
                else:
                    print(f"   ❌ Profile endpoint failed with ObjectId: {profile_response.status_code if profile_response else 'No response'}")
            else:
                print("   No ObjectId format users found")
        else:
            print(f"   ❌ Failed to get users: {response.status_code if response else 'No response'}")

    def test_frontend_display_scenarios(self):
        """Test specific frontend display scenarios"""
        print("\n🔍 Testing Frontend Display Scenarios")
        
        # Get some existing data to test display scenarios
        response = self.make_request('GET', 'api/marketplace/browse')
        if response and response.status_code == 200:
            listings = response.json()
            print(f"   Found {len(listings)} listings in browse")
            
            # Test each listing for seller information
            for i, listing in enumerate(listings[:3]):  # Test first 3 listings
                seller_info = listing.get('seller', {})
                listing_title = listing.get('title', 'Unknown')
                
                print(f"\n   Listing {i+1}: {listing_title}")
                
                # Check if seller name can be displayed
                seller_name = seller_info.get('name') or seller_info.get('username') or 'Unknown'
                print(f"   📋 Seller display name: '{seller_name}'")
                
                # Check business information
                if seller_info.get('is_business'):
                    business_name = seller_info.get('business_name', '')
                    print(f"   🏢 Business: {business_name}")
                else:
                    print(f"   👤 Individual seller")
                
                # Test seller overview for this seller
                seller_id = listing.get('seller_id')
                if seller_id:
                    overview_response = self.make_request('GET', f'api/tenders/seller/{seller_id}/overview')
                    if overview_response and overview_response.status_code == 200:
                        overview_data = overview_response.json()
                        
                        # Check for tenders with buyer information
                        total_tenders = 0
                        for listing_overview in overview_data:
                            tenders = listing_overview.get('tenders', [])
                            total_tenders += len(tenders)
                            
                            for tender in tenders:
                                buyer_info = tender.get('buyer', {})
                                buyer_name = buyer_info.get('full_name') or buyer_info.get('username') or 'Unknown'
                                offer_amount = tender.get('offer_amount', 0)
                                print(f"   💰 Tender: €{offer_amount} by {buyer_name}")
                        
                        if total_tenders == 0:
                            print(f"   📝 No tenders for this seller's listings")
                    else:
                        print(f"   ❌ Seller overview failed for {seller_id}")
        else:
            print(f"   ❌ Browse failed: {response.status_code if response else 'No response'}")

    def test_empty_vs_populated_scenarios(self):
        """Test scenarios where seller/buyer info might be empty vs populated"""
        print("\n🔍 Testing Empty vs Populated Scenarios")
        
        # Create a test user with minimal information
        minimal_user_data = {
            "username": "minimal_test_user",
            "email": "minimal@test.com",
            "full_name": "Minimal User"
        }
        
        response = self.make_request('POST', 'api/auth/register', minimal_user_data)
        if response and response.status_code == 200:
            result = response.json()
            minimal_user_id = result.get('user_id')
            print(f"   ✅ Created minimal user: {minimal_user_id}")
            
            # Test seller overview with minimal user
            overview_response = self.make_request('GET', f'api/tenders/seller/{minimal_user_id}/overview')
            if overview_response and overview_response.status_code == 200:
                overview_data = overview_response.json()
                print(f"   ✅ Seller overview works with minimal user data")
                
                # The overview should be empty (no listings) but seller info should still be populated
                if len(overview_data) == 0:
                    print(f"   📝 No listings for minimal user (expected)")
                else:
                    # If there are listings, check seller info
                    seller_info = overview_data[0].get('seller', {})
                    if seller_info and seller_info != {}:
                        print(f"   ✅ Seller info populated even for minimal user")
                    else:
                        print(f"   ❌ Seller info empty for minimal user")
            else:
                print(f"   ❌ Seller overview failed for minimal user")
        else:
            print(f"   ❌ Failed to create minimal user")

    def run_additional_tests(self):
        """Run all additional tests"""
        print("🎯 ADDITIONAL TENDER VISIBILITY TESTS")
        print("=" * 50)
        
        self.test_existing_user_data()
        self.test_frontend_display_scenarios()
        self.test_empty_vs_populated_scenarios()
        
        print("\n" + "=" * 50)
        print("🎯 ADDITIONAL TESTS COMPLETED")

if __name__ == "__main__":
    tester = AdditionalVisibilityTests()
    tester.run_additional_tests()