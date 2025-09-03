#!/usr/bin/env python3
"""
My Listings Functionality Investigation
Investigating the issue where frontend gets 404 errors when calling /api/user/my-listings/{user_id}
"""

import requests
import sys
import json
from datetime import datetime

class MyListingsInvestigator:
    def __init__(self, base_url="https://cataloro-marketplace-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user_id = "68b191ec38e6062fee10bd27"  # admin@cataloro.com as mentioned in review
        self.admin_user = None
        
    def log_result(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        print()

    def make_request(self, method, endpoint, data=None, expected_status=None):
        """Make HTTP request and return response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        print(f"🔍 {method} {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.text:
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return response.status_code, response_data
                except:
                    print(f"   Response (text): {response.text}")
                    return response.status_code, response.text
            else:
                print("   Response: Empty")
                return response.status_code, {}
                
        except Exception as e:
            print(f"   Error: {str(e)}")
            return None, str(e)

    def test_1_check_my_listings_endpoint(self):
        """Test 1: Check if /api/user/my-listings/{user_id} endpoint exists"""
        print("=" * 80)
        print("TEST 1: Check My Listings Endpoint Existence")
        print("=" * 80)
        
        status, response = self.make_request('GET', f'api/user/my-listings/{self.test_user_id}')
        
        if status == 200:
            self.log_result("My Listings Endpoint", True, f"Endpoint exists and returns {len(response) if isinstance(response, list) else 'data'}")
            return True, response
        elif status == 404:
            self.log_result("My Listings Endpoint", False, "Endpoint returns 404 - this is the reported issue")
            return False, response
        else:
            self.log_result("My Listings Endpoint", False, f"Unexpected status {status}")
            return False, response

    def test_2_check_alternative_endpoints(self):
        """Test 2: Check alternative endpoints for fetching user listings"""
        print("=" * 80)
        print("TEST 2: Check Alternative Listing Endpoints")
        print("=" * 80)
        
        alternatives = [
            f'api/listings?seller_id={self.test_user_id}',
            f'api/listings?user_id={self.test_user_id}',
            'api/listings',
            'api/marketplace/browse'
        ]
        
        results = {}
        
        for endpoint in alternatives:
            print(f"\n--- Testing {endpoint} ---")
            status, response = self.make_request('GET', endpoint)
            
            if status == 200:
                if isinstance(response, dict) and 'listings' in response:
                    listings = response['listings']
                    user_listings = [l for l in listings if l.get('seller_id') == self.test_user_id]
                    results[endpoint] = {
                        'status': 'success',
                        'total_listings': len(listings),
                        'user_listings': len(user_listings),
                        'format': 'object_with_listings_array',
                        'user_listings_data': user_listings
                    }
                    self.log_result(f"Alternative endpoint {endpoint}", True, 
                                  f"Found {len(listings)} total listings, {len(user_listings)} for user {self.test_user_id}")
                elif isinstance(response, list):
                    user_listings = [l for l in response if l.get('seller_id') == self.test_user_id]
                    results[endpoint] = {
                        'status': 'success',
                        'total_listings': len(response),
                        'user_listings': len(user_listings),
                        'format': 'array',
                        'user_listings_data': user_listings
                    }
                    self.log_result(f"Alternative endpoint {endpoint}", True, 
                                  f"Found {len(response)} total listings, {len(user_listings)} for user {self.test_user_id}")
                else:
                    results[endpoint] = {
                        'status': 'success',
                        'format': 'unknown',
                        'data': response
                    }
                    self.log_result(f"Alternative endpoint {endpoint}", True, "Returns data but format unclear")
            else:
                results[endpoint] = {
                    'status': 'failed',
                    'status_code': status,
                    'response': response
                }
                self.log_result(f"Alternative endpoint {endpoint}", False, f"Status {status}")
        
        return results

    def test_3_login_and_get_user_data(self):
        """Test 3: Login as admin user and get actual user data"""
        print("=" * 80)
        print("TEST 3: Login and Get User Data")
        print("=" * 80)
        
        # Login as admin
        print("--- Logging in as admin@cataloro.com ---")
        status, response = self.make_request('POST', 'api/auth/login', {
            'email': 'admin@cataloro.com',
            'password': 'demo123'
        })
        
        if status == 200 and 'user' in response:
            self.admin_user = response['user']
            actual_user_id = self.admin_user.get('id')
            self.log_result("Admin Login", True, f"Logged in successfully, user ID: {actual_user_id}")
            
            # Now test my-listings with the actual user ID
            print(f"--- Testing my-listings with actual user ID: {actual_user_id} ---")
            status, listings_response = self.make_request('GET', f'api/user/my-listings/{actual_user_id}')
            
            if status == 200:
                self.log_result("My Listings with Actual User ID", True, 
                              f"Found {len(listings_response) if isinstance(listings_response, list) else 'data'}")
                return True, actual_user_id, listings_response
            else:
                self.log_result("My Listings with Actual User ID", False, f"Status {status}")
                return False, actual_user_id, listings_response
        else:
            self.log_result("Admin Login", False, f"Status {status}")
            return False, None, None

    def test_4_create_test_listing(self):
        """Test 4: Create a test listing for the user and verify it appears"""
        print("=" * 80)
        print("TEST 4: Create Test Listing and Verify")
        print("=" * 80)
        
        if not self.admin_user:
            self.log_result("Create Test Listing", False, "No admin user logged in")
            return False, None
        
        user_id = self.admin_user.get('id')
        
        # Create a test listing
        test_listing = {
            "title": "Test Listing for My Listings Investigation",
            "description": "This is a test listing created to investigate the My Listings functionality",
            "price": 99.99,
            "category": "Test",
            "condition": "new",
            "seller_id": user_id,
            "images": ["https://via.placeholder.com/400x300?text=Test+Listing"]
        }
        
        print("--- Creating test listing ---")
        status, create_response = self.make_request('POST', 'api/listings', test_listing)
        
        if status == 200:
            listing_id = create_response.get('listing_id')
            self.log_result("Create Test Listing", True, f"Created listing with ID: {listing_id}")
            
            # Now check if it appears in my-listings
            print("--- Checking if test listing appears in my-listings ---")
            status, listings_response = self.make_request('GET', f'api/user/my-listings/{user_id}')
            
            if status == 200:
                if isinstance(listings_response, list):
                    test_listings = [l for l in listings_response if l.get('title') == test_listing['title']]
                    if test_listings:
                        self.log_result("Test Listing in My Listings", True, 
                                      f"Test listing found in my-listings response")
                        return True, listing_id
                    else:
                        self.log_result("Test Listing in My Listings", False, 
                                      "Test listing not found in my-listings response")
                        return False, listing_id
                else:
                    self.log_result("Test Listing in My Listings", False, 
                                  "my-listings returned non-list response")
                    return False, listing_id
            else:
                self.log_result("Test Listing in My Listings", False, 
                              f"my-listings endpoint returned status {status}")
                return False, listing_id
        else:
            self.log_result("Create Test Listing", False, f"Status {status}")
            return False, None

    def test_5_database_investigation(self):
        """Test 5: Investigate what listings exist in database for the specific user"""
        print("=" * 80)
        print("TEST 5: Database Investigation")
        print("=" * 80)
        
        # Check all listings and filter by user
        print("--- Getting all listings from database ---")
        status, response = self.make_request('GET', 'api/listings')
        
        if status == 200:
            if isinstance(response, dict) and 'listings' in response:
                all_listings = response['listings']
                
                # Filter by the specific user ID mentioned in review
                user_listings_original = [l for l in all_listings if l.get('seller_id') == self.test_user_id]
                
                # Also check with actual admin user ID if we have it
                admin_listings = []
                if self.admin_user:
                    admin_user_id = self.admin_user.get('id')
                    admin_listings = [l for l in all_listings if l.get('seller_id') == admin_user_id]
                
                print(f"Total listings in database: {len(all_listings)}")
                print(f"Listings for user {self.test_user_id}: {len(user_listings_original)}")
                if self.admin_user:
                    print(f"Listings for admin user {admin_user_id}: {len(admin_listings)}")
                
                # Show seller_ids that exist
                seller_ids = list(set([l.get('seller_id') for l in all_listings if l.get('seller_id')]))
                print(f"Seller IDs found in database: {seller_ids}")
                
                self.log_result("Database Investigation", True, 
                              f"Found {len(all_listings)} total listings with {len(seller_ids)} unique sellers")
                
                return {
                    'total_listings': len(all_listings),
                    'user_listings_original': user_listings_original,
                    'admin_listings': admin_listings,
                    'seller_ids': seller_ids,
                    'all_listings': all_listings
                }
            else:
                self.log_result("Database Investigation", False, "Unexpected response format")
                return None
        else:
            self.log_result("Database Investigation", False, f"Status {status}")
            return None

    def run_investigation(self):
        """Run complete investigation"""
        print("🔍 MY LISTINGS FUNCTIONALITY INVESTIGATION")
        print("🎯 Investigating why frontend gets 404 errors for /api/user/my-listings/{user_id}")
        print("👤 Target user ID: 68b191ec38e6062fee10bd27 (admin@cataloro.com)")
        print("=" * 80)
        
        # Test 1: Check if endpoint exists
        endpoint_exists, endpoint_response = self.test_1_check_my_listings_endpoint()
        
        # Test 2: Check alternative endpoints
        alternative_results = self.test_2_check_alternative_endpoints()
        
        # Test 3: Login and get actual user data
        login_success, actual_user_id, actual_listings = self.test_3_login_and_get_user_data()
        
        # Test 4: Create test listing and verify
        listing_created, test_listing_id = self.test_4_create_test_listing()
        
        # Test 5: Database investigation
        db_results = self.test_5_database_investigation()
        
        # Summary and conclusions
        print("=" * 80)
        print("🔍 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        print("KEY FINDINGS:")
        print("-" * 40)
        
        if not endpoint_exists:
            print("❌ ISSUE CONFIRMED: /api/user/my-listings/{user_id} returns 404")
            print("   This matches the reported frontend issue")
        else:
            print("✅ /api/user/my-listings/{user_id} endpoint is working")
        
        # Check if alternative endpoints work
        working_alternatives = []
        for endpoint, result in alternative_results.items():
            if result.get('status') == 'success':
                working_alternatives.append(endpoint)
                if result.get('user_listings', 0) > 0:
                    print(f"✅ {endpoint} works and has {result['user_listings']} listings for user")
        
        if working_alternatives:
            print(f"✅ Alternative endpoints available: {working_alternatives}")
        else:
            print("❌ No working alternative endpoints found")
        
        # User ID analysis
        if actual_user_id and actual_user_id != self.test_user_id:
            print(f"⚠️  USER ID MISMATCH:")
            print(f"   Expected: {self.test_user_id}")
            print(f"   Actual:   {actual_user_id}")
            print("   This could be the root cause of the 404 errors")
        
        # Database analysis
        if db_results:
            print(f"📊 DATABASE ANALYSIS:")
            print(f"   Total listings: {db_results['total_listings']}")
            print(f"   Unique sellers: {len(db_results['seller_ids'])}")
            print(f"   Seller IDs: {db_results['seller_ids']}")
            
            if self.test_user_id not in db_results['seller_ids']:
                print(f"❌ User ID {self.test_user_id} has NO listings in database")
                print("   This explains why my-listings returns empty array, not 404")
        
        # Recommendations
        print("\n🎯 RECOMMENDATIONS:")
        print("-" * 40)
        
        if not endpoint_exists:
            print("1. ❌ CRITICAL: /api/user/my-listings/{user_id} endpoint is broken")
            print("   - Check backend routing and implementation")
            print("   - Verify endpoint is properly registered")
        else:
            print("1. ✅ /api/user/my-listings/{user_id} endpoint exists and works")
        
        if actual_user_id != self.test_user_id:
            print("2. ⚠️  USER ID ISSUE: Frontend using wrong user ID")
            print(f"   - Frontend should use: {actual_user_id}")
            print(f"   - Not: {self.test_user_id}")
        
        if db_results and self.test_user_id not in db_results['seller_ids']:
            print("3. 📊 DATA ISSUE: User has no listings in database")
            print("   - Create test listings for this user")
            print("   - Or use a user ID that has existing listings")
        
        if working_alternatives:
            print("4. 🔄 ALTERNATIVE SOLUTION: Use working endpoints")
            for endpoint in working_alternatives:
                if 'seller_id' in endpoint:
                    print(f"   - {endpoint} (filter by seller_id)")
        
        return {
            'endpoint_exists': endpoint_exists,
            'alternative_endpoints': alternative_results,
            'actual_user_id': actual_user_id,
            'database_results': db_results,
            'test_listing_created': listing_created
        }

def main():
    """Main investigation execution"""
    investigator = MyListingsInvestigator()
    results = investigator.run_investigation()
    return 0

if __name__ == "__main__":
    sys.exit(main())