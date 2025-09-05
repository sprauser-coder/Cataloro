#!/usr/bin/env python3
"""
Browse Listings Data Structure Debug Test
Comprehensive testing to debug business badge and seller data issues
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class BrowseListingsDebugTester:
    def __init__(self, base_url="https://market-refactor.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_user = None
        self.regular_user = None
        self.business_user = None
        self.test_listings = []
        
    def log_result(self, test_name, success, details=""):
        """Log test results with detailed information"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        return success

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request and return response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
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

    def setup_test_users(self):
        """Create test users with different account types"""
        print("\n🔧 Setting up test users...")
        
        # Create admin user
        success, admin_data = self.make_request(
            'POST', 'api/auth/login',
            {"email": "admin@cataloro.com", "password": "demo123"}
        )
        if success:
            self.admin_user = admin_data.get('user')
            print(f"   ✅ Admin user: {self.admin_user.get('email')} (Role: {self.admin_user.get('role')})")
        
        # Create regular user
        success, user_data = self.make_request(
            'POST', 'api/auth/login',
            {"email": "user@cataloro.com", "password": "demo123"}
        )
        if success:
            self.regular_user = user_data.get('user')
            print(f"   ✅ Regular user: {self.regular_user.get('email')} (Role: {self.regular_user.get('role')})")
        
        # Create business user (simulate business account)
        success, business_data = self.make_request(
            'POST', 'api/auth/login',
            {"email": "business@cataloro.com", "password": "demo123", "username": "business_account"}
        )
        if success:
            self.business_user = business_data.get('user')
            print(f"   ✅ Business user: {self.business_user.get('email')} (Role: {self.business_user.get('role')})")
            
            # Try to update business user to have business account flag
            if self.admin_user:
                business_update = {
                    "is_business": True,
                    "business_name": "Cataloro Business Solutions",
                    "username": "cataloro_business"
                }
                self.make_request(
                    'PUT', f'api/admin/users/{self.business_user.get("id")}',
                    business_update
                )
                print(f"   📝 Updated business user with business account flags")

    def test_browse_api_response_structure(self):
        """Test 1: Check what /api/marketplace/browse actually returns"""
        print("\n📊 TEST 1: Browse API Response Structure Analysis")
        
        success, browse_data = self.make_request('GET', 'api/marketplace/browse')
        
        if not success:
            return self.log_result("Browse API Response", False, "API call failed")
        
        # Analyze response structure
        print(f"\n📋 Browse API Response Analysis:")
        print(f"   Response Type: {type(browse_data)}")
        print(f"   Total Listings: {len(browse_data) if isinstance(browse_data, list) else 'Not a list'}")
        
        if isinstance(browse_data, list) and len(browse_data) > 0:
            # Analyze first listing structure
            first_listing = browse_data[0]
            print(f"\n🔍 First Listing Structure:")
            for key, value in first_listing.items():
                print(f"   {key}: {type(value).__name__} = {str(value)[:100]}")
            
            # Check for seller information
            seller_fields = ['seller_id', 'seller', 'seller_info', 'user_id']
            seller_data_found = {}
            
            for field in seller_fields:
                if field in first_listing:
                    seller_data_found[field] = first_listing[field]
                    print(f"   🔍 Found seller field '{field}': {first_listing[field]}")
            
            # Check if seller_id exists and get seller details
            if 'seller_id' in first_listing:
                seller_id = first_listing['seller_id']
                print(f"\n👤 Checking seller details for ID: {seller_id}")
                
                # Try to get seller profile
                seller_success, seller_profile = self.make_request(
                    'GET', f'api/auth/profile/{seller_id}'
                )
                
                if seller_success:
                    print(f"   ✅ Seller Profile Found:")
                    for key, value in seller_profile.items():
                        print(f"      {key}: {value}")
                    
                    # Check for business account indicators
                    business_indicators = ['is_business', 'business_name', 'account_type', 'username']
                    for indicator in business_indicators:
                        if indicator in seller_profile:
                            print(f"   🏢 Business Indicator '{indicator}': {seller_profile[indicator]}")
                else:
                    print(f"   ❌ Could not fetch seller profile for ID: {seller_id}")
            
            return self.log_result("Browse API Response Structure", True, 
                                 f"Found {len(browse_data)} listings with detailed structure analysis")
        else:
            return self.log_result("Browse API Response Structure", False, 
                                 "No listings found or invalid response format")

    def test_seller_data_structure(self):
        """Test 2: Verify seller data structure in listings"""
        print("\n👥 TEST 2: Seller Data Structure Verification")
        
        success, browse_data = self.make_request('GET', 'api/marketplace/browse')
        
        if not success or not isinstance(browse_data, list):
            return self.log_result("Seller Data Structure", False, "Could not get browse data")
        
        seller_analysis = {
            'total_listings': len(browse_data),
            'listings_with_seller_id': 0,
            'unique_sellers': set(),
            'seller_profiles': {},
            'business_accounts': 0,
            'username_vs_email': {'usernames': 0, 'emails': 0}
        }
        
        print(f"\n📊 Analyzing {len(browse_data)} listings for seller data...")
        
        for i, listing in enumerate(browse_data):
            if 'seller_id' in listing:
                seller_analysis['listings_with_seller_id'] += 1
                seller_id = listing['seller_id']
                seller_analysis['unique_sellers'].add(seller_id)
                
                # Get seller profile if not already fetched
                if seller_id not in seller_analysis['seller_profiles']:
                    seller_success, seller_profile = self.make_request(
                        'GET', f'api/auth/profile/{seller_id}'
                    )
                    
                    if seller_success:
                        seller_analysis['seller_profiles'][seller_id] = seller_profile
                        
                        # Check for business account
                        if seller_profile.get('is_business') or seller_profile.get('account_type') == 'business':
                            seller_analysis['business_accounts'] += 1
                        
                        # Check username vs email display
                        username = seller_profile.get('username', '')
                        email = seller_profile.get('email', '')
                        
                        if username and '@' not in username:
                            seller_analysis['username_vs_email']['usernames'] += 1
                        elif email and '@' in email:
                            seller_analysis['username_vs_email']['emails'] += 1
                        
                        print(f"   Listing {i+1}: Seller {seller_id[:8]}... - "
                              f"Username: '{username}' | Email: '{email}' | "
                              f"Business: {seller_profile.get('is_business', False)}")
        
        # Print analysis results
        print(f"\n📋 Seller Data Analysis Results:")
        print(f"   Total Listings: {seller_analysis['total_listings']}")
        print(f"   Listings with seller_id: {seller_analysis['listings_with_seller_id']}")
        print(f"   Unique Sellers: {len(seller_analysis['unique_sellers'])}")
        print(f"   Business Accounts: {seller_analysis['business_accounts']}")
        print(f"   Usernames Found: {seller_analysis['username_vs_email']['usernames']}")
        print(f"   Emails Found: {seller_analysis['username_vs_email']['emails']}")
        
        # Check for issues
        issues_found = []
        
        if seller_analysis['business_accounts'] == 0:
            issues_found.append("No business accounts found - all showing as 'Private'")
        
        if seller_analysis['username_vs_email']['emails'] > seller_analysis['username_vs_email']['usernames']:
            issues_found.append("More emails than usernames - sellers showing emails instead of usernames")
        
        if issues_found:
            print(f"\n⚠️  Issues Identified:")
            for issue in issues_found:
                print(f"   - {issue}")
        
        return self.log_result("Seller Data Structure", len(issues_found) == 0, 
                             f"Analysis complete - {len(issues_found)} issues found")

    def test_create_business_listing(self):
        """Test 3: Create listings with proper seller information"""
        print("\n📝 TEST 3: Create Listings with Business Account Information")
        
        if not self.business_user:
            return self.log_result("Create Business Listing", False, "No business user available")
        
        # Create a business listing
        business_listing = {
            "title": "Professional Business Laptop - Dell XPS 15",
            "description": "High-performance business laptop from Cataloro Business Solutions. Perfect for professional use with warranty included.",
            "price": 1899.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.business_user['id'],
            "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400"],
            "tags": ["business", "laptop", "professional"],
            "features": ["Business warranty", "Professional support", "Enterprise grade"]
        }
        
        success, create_response = self.make_request(
            'POST', 'api/listings', business_listing
        )
        
        if success:
            listing_id = create_response.get('listing_id')
            self.test_listings.append(listing_id)
            print(f"   ✅ Created business listing: {listing_id}")
            
            # Verify listing appears in browse with correct seller info
            success, browse_data = self.make_request('GET', 'api/marketplace/browse')
            
            if success:
                # Find our listing
                our_listing = None
                for listing in browse_data:
                    if listing.get('id') == listing_id:
                        our_listing = listing
                        break
                
                if our_listing:
                    print(f"   ✅ Listing found in browse results")
                    print(f"   Seller ID: {our_listing.get('seller_id')}")
                    
                    # Get seller profile to verify business status
                    seller_success, seller_profile = self.make_request(
                        'GET', f'api/auth/profile/{our_listing.get("seller_id")}'
                    )
                    
                    if seller_success:
                        is_business = seller_profile.get('is_business', False)
                        username = seller_profile.get('username', '')
                        business_name = seller_profile.get('business_name', '')
                        
                        print(f"   Business Status: {is_business}")
                        print(f"   Username: {username}")
                        print(f"   Business Name: {business_name}")
                        
                        return self.log_result("Create Business Listing", True,
                                             f"Business listing created with proper seller info")
                    else:
                        return self.log_result("Create Business Listing", False,
                                             "Could not verify seller profile")
                else:
                    return self.log_result("Create Business Listing", False,
                                         "Listing not found in browse results")
            else:
                return self.log_result("Create Business Listing", False,
                                     "Could not fetch browse results")
        else:
            return self.log_result("Create Business Listing", False,
                                 "Failed to create listing")

    def test_regular_user_listing(self):
        """Test 4: Create regular user listing for comparison"""
        print("\n👤 TEST 4: Create Regular User Listing for Comparison")
        
        if not self.regular_user:
            return self.log_result("Create Regular Listing", False, "No regular user available")
        
        # Create a regular user listing
        regular_listing = {
            "title": "Personal Gaming Setup - RTX 4080",
            "description": "Personal gaming computer with RTX 4080. Selling due to upgrade. Great condition.",
            "price": 2299.99,
            "category": "Electronics",
            "condition": "Used - Excellent",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=400"],
            "tags": ["gaming", "personal", "rtx"],
            "features": ["High performance", "Personal use", "Well maintained"]
        }
        
        success, create_response = self.make_request(
            'POST', 'api/listings', regular_listing
        )
        
        if success:
            listing_id = create_response.get('listing_id')
            self.test_listings.append(listing_id)
            print(f"   ✅ Created regular listing: {listing_id}")
            
            # Get seller profile
            seller_success, seller_profile = self.make_request(
                'GET', f'api/auth/profile/{self.regular_user["id"]}'
            )
            
            if seller_success:
                is_business = seller_profile.get('is_business', False)
                username = seller_profile.get('username', '')
                email = seller_profile.get('email', '')
                
                print(f"   Business Status: {is_business}")
                print(f"   Username: {username}")
                print(f"   Email: {email}")
                
                return self.log_result("Create Regular Listing", True,
                                     f"Regular listing created - Business: {is_business}")
            else:
                return self.log_result("Create Regular Listing", False,
                                     "Could not verify seller profile")
        else:
            return self.log_result("Create Regular Listing", False,
                                 "Failed to create listing")

    def test_new_listings_visibility(self):
        """Test 5: Check if new listings appear in browse page"""
        print("\n👁️  TEST 5: New Listings Visibility in Browse Page")
        
        if not self.test_listings:
            return self.log_result("New Listings Visibility", False, "No test listings created")
        
        success, browse_data = self.make_request('GET', 'api/marketplace/browse')
        
        if not success:
            return self.log_result("New Listings Visibility", False, "Could not fetch browse data")
        
        found_listings = 0
        total_test_listings = len(self.test_listings)
        
        print(f"   Checking for {total_test_listings} test listings in browse results...")
        
        for test_listing_id in self.test_listings:
            found = False
            for listing in browse_data:
                if listing.get('id') == test_listing_id:
                    found = True
                    found_listings += 1
                    print(f"   ✅ Found test listing: {test_listing_id[:8]}... - {listing.get('title', 'No title')}")
                    break
            
            if not found:
                print(f"   ❌ Missing test listing: {test_listing_id[:8]}...")
        
        visibility_success = found_listings == total_test_listings
        
        return self.log_result("New Listings Visibility", visibility_success,
                             f"Found {found_listings}/{total_test_listings} test listings in browse")

    def test_data_flow_analysis(self):
        """Test 6: Comprehensive data flow analysis"""
        print("\n🔄 TEST 6: Data Flow Analysis - Fetching vs Transformation vs Display")
        
        # Step 1: Raw API data
        print("\n1️⃣ Raw API Data Analysis:")
        success, browse_data = self.make_request('GET', 'api/marketplace/browse')
        
        if not success:
            return self.log_result("Data Flow Analysis", False, "Could not fetch browse data")
        
        print(f"   Browse endpoint returns: {type(browse_data)} with {len(browse_data)} items")
        
        # Step 2: Seller data enrichment analysis
        print("\n2️⃣ Seller Data Enrichment Analysis:")
        enriched_listings = []
        
        for listing in browse_data[:3]:  # Analyze first 3 listings
            seller_id = listing.get('seller_id')
            if seller_id:
                seller_success, seller_profile = self.make_request(
                    'GET', f'api/auth/profile/{seller_id}'
                )
                
                if seller_success:
                    # Simulate frontend data transformation
                    enriched_listing = {
                        'id': listing.get('id'),
                        'title': listing.get('title'),
                        'price': listing.get('price'),
                        'seller_id': seller_id,
                        'seller_username': seller_profile.get('username', ''),
                        'seller_email': seller_profile.get('email', ''),
                        'seller_full_name': seller_profile.get('full_name', ''),
                        'is_business': seller_profile.get('is_business', False),
                        'business_name': seller_profile.get('business_name', ''),
                        'display_name': seller_profile.get('username') or seller_profile.get('full_name') or seller_profile.get('email'),
                        'badge_type': 'Business' if seller_profile.get('is_business') else 'Private'
                    }
                    
                    enriched_listings.append(enriched_listing)
                    
                    print(f"   Listing: {listing.get('title', 'No title')[:30]}...")
                    print(f"      Raw seller_id: {seller_id}")
                    print(f"      Username: '{seller_profile.get('username', 'None')}'")
                    print(f"      Email: '{seller_profile.get('email', 'None')}'")
                    print(f"      Is Business: {seller_profile.get('is_business', False)}")
                    print(f"      Display Name: '{enriched_listing['display_name']}'")
                    print(f"      Badge Type: {enriched_listing['badge_type']}")
        
        # Step 3: Issue identification
        print("\n3️⃣ Issue Identification:")
        issues = []
        
        # Check for business badge issue
        business_count = sum(1 for listing in enriched_listings if listing['is_business'])
        if business_count == 0:
            issues.append("All listings show 'Private' badge - no business accounts detected")
        
        # Check for username vs email issue
        email_display_count = sum(1 for listing in enriched_listings if '@' in listing['display_name'])
        username_display_count = sum(1 for listing in enriched_listings if listing['seller_username'] and '@' not in listing['display_name'])
        
        if email_display_count > username_display_count:
            issues.append("Sellers showing emails instead of usernames")
        
        # Check for missing seller data
        missing_seller_data = sum(1 for listing in enriched_listings if not listing['display_name'])
        if missing_seller_data > 0:
            issues.append(f"{missing_seller_data} listings have missing seller display names")
        
        print(f"   Business Accounts Found: {business_count}")
        print(f"   Email Display Count: {email_display_count}")
        print(f"   Username Display Count: {username_display_count}")
        print(f"   Missing Seller Data: {missing_seller_data}")
        
        if issues:
            print(f"\n⚠️  Issues Identified:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ No data flow issues detected")
        
        return self.log_result("Data Flow Analysis", len(issues) == 0,
                             f"Analysis complete - {len(issues)} issues identified")

    def cleanup_test_listings(self):
        """Clean up test listings"""
        print("\n🧹 Cleaning up test listings...")
        
        for listing_id in self.test_listings:
            success, _ = self.make_request('DELETE', f'api/listings/{listing_id}')
            if success:
                print(f"   ✅ Deleted test listing: {listing_id[:8]}...")
            else:
                print(f"   ❌ Failed to delete: {listing_id[:8]}...")

    def run_debug_tests(self):
        """Run all debug tests"""
        print("🔍 BROWSE LISTINGS DATA STRUCTURE DEBUG TESTS")
        print("=" * 60)
        print("Debugging business badge and seller data issues...")
        
        # Setup
        self.setup_test_users()
        
        # Run tests
        test_results = []
        
        test_results.append(self.test_browse_api_response_structure())
        test_results.append(self.test_seller_data_structure())
        test_results.append(self.test_create_business_listing())
        test_results.append(self.test_regular_user_listing())
        test_results.append(self.test_new_listings_visibility())
        test_results.append(self.test_data_flow_analysis())
        
        # Cleanup
        self.cleanup_test_listings()
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print("\n" + "=" * 60)
        print(f"🔍 DEBUG TEST RESULTS: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✅ All debug tests passed - no issues detected")
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed - issues identified")
        
        return passed_tests == total_tests

def main():
    """Main execution"""
    tester = BrowseListingsDebugTester()
    success = tester.run_debug_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())