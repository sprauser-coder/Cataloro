#!/usr/bin/env python3
"""
Seller Information Enrichment Test Suite
Tests the enhanced /api/marketplace/browse endpoint for seller information enrichment
"""

import requests
import sys
import json
from datetime import datetime

class SellerEnrichmentTester:
    def __init__(self, base_url="https://trade-platform-30.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.business_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_listing_ids = []

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
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
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
        """Setup test users including business account"""
        print("\n🔧 Setting up test users...")
        
        # Login admin user
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_user = response['user']
            print(f"   Admin User: {self.admin_user}")

        # Login regular user
        success, response = self.run_test(
            "Regular User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.user_token = response['token']
            self.regular_user = response['user']
            print(f"   Regular User: {self.regular_user}")

        # Create/Login business user
        success, response = self.run_test(
            "Business User Login/Create",
            "POST",
            "api/auth/login",
            200,
            data={"email": "business@cataloro.com", "password": "demo123", "username": "cataloro_business"}
        )
        if success and 'token' in response:
            self.business_user = response['user']
            print(f"   Business User: {self.business_user}")
            
            # Update business user profile to have business account information
            if self.business_user:
                business_update = {
                    "is_business": True,
                    "company_name": "Cataloro Business Solutions",
                    "username": "cataloro_business"
                }
                
                # Update user profile to be a business account
                update_success, update_response = self.run_test(
                    "Update Business User Profile",
                    "PUT",
                    f"api/admin/users/{self.business_user['id']}",
                    200,
                    data=business_update
                )
                
                if update_success:
                    print("   ✅ Business user profile updated with business account information")
                    # Refresh business user data
                    profile_success, profile_response = self.run_test(
                        "Get Business User Profile",
                        "GET",
                        f"api/auth/profile/{self.business_user['id']}",
                        200
                    )
                    if profile_success:
                        self.business_user = profile_response
                        print(f"   Updated Business User: {self.business_user}")

        return self.admin_user is not None and self.regular_user is not None and self.business_user is not None

    def create_test_listings(self):
        """Create test listings from different user types"""
        print("\n📝 Creating test listings from different user types...")
        
        # Create listing from regular user
        if self.regular_user:
            regular_listing = {
                "title": "Regular User Listing - MacBook Pro",
                "description": "MacBook Pro 16-inch from regular user account",
                "price": 2500.00,
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"]
            }
            
            success, response = self.run_test(
                "Create Regular User Listing",
                "POST",
                "api/listings",
                200,
                data=regular_listing
            )
            
            if success and 'listing_id' in response:
                self.test_listing_ids.append(response['listing_id'])
                print(f"   ✅ Created regular user listing: {response['listing_id']}")

        # Create listing from business user
        if self.business_user:
            business_listing = {
                "title": "Business Account Listing - Professional Camera",
                "description": "Professional camera equipment from business account",
                "price": 3500.00,
                "category": "Photography",
                "condition": "New",
                "seller_id": self.business_user['id'],
                "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"]
            }
            
            success, response = self.run_test(
                "Create Business User Listing",
                "POST",
                "api/listings",
                200,
                data=business_listing
            )
            
            if success and 'listing_id' in response:
                self.test_listing_ids.append(response['listing_id'])
                print(f"   ✅ Created business user listing: {response['listing_id']}")

        # Create listing from admin user
        if self.admin_user:
            admin_listing = {
                "title": "Admin User Listing - Vintage Guitar",
                "description": "Vintage guitar from admin account",
                "price": 1200.00,
                "category": "Music",
                "condition": "Used - Good",
                "seller_id": self.admin_user['id'],
                "images": ["https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400"]
            }
            
            success, response = self.run_test(
                "Create Admin User Listing",
                "POST",
                "api/listings",
                200,
                data=admin_listing
            )
            
            if success and 'listing_id' in response:
                self.test_listing_ids.append(response['listing_id'])
                print(f"   ✅ Created admin user listing: {response['listing_id']}")

        return len(self.test_listing_ids) > 0

    def test_seller_information_enrichment(self):
        """Test seller information enrichment in browse endpoint"""
        print("\n🔍 Testing Seller Information Enrichment...")
        
        success, response = self.run_test(
            "Browse Listings with Seller Enrichment",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False

        enrichment_tests = []
        
        # Test each listing for proper seller enrichment
        for listing in response:
            listing_id = listing.get('id', 'Unknown')
            seller = listing.get('seller', {})
            
            print(f"\n   📋 Analyzing listing: {listing.get('title', 'Unknown')[:50]}...")
            print(f"      Listing ID: {listing_id}")
            print(f"      Seller Object: {json.dumps(seller, indent=6)}")
            
            # Test 1: Seller object exists
            has_seller_object = 'seller' in listing and isinstance(seller, dict)
            enrichment_tests.append(("Seller Object Present", has_seller_object))
            
            if has_seller_object:
                # Test 2: Required seller fields present
                required_fields = ['name', 'username', 'is_business', 'business_name', 'verified', 'location']
                missing_fields = [field for field in required_fields if field not in seller]
                
                has_required_fields = len(missing_fields) == 0
                enrichment_tests.append(("Required Seller Fields", has_required_fields))
                
                if missing_fields:
                    print(f"      ⚠️  Missing fields: {missing_fields}")
                
                # Test 3: Username vs Email priority
                seller_name = seller.get('name', '')
                seller_username = seller.get('username', '')
                seller_email = seller.get('email', '')
                
                # Check if name prioritizes username over email
                name_is_username = seller_name == seller_username and seller_name != seller_email
                if not name_is_username and seller_email and '@' in seller_name:
                    print(f"      ⚠️  Seller name appears to be email: {seller_name}")
                    print(f"      ⚠️  Should be username: {seller_username}")
                
                enrichment_tests.append(("Username Priority Over Email", name_is_username or not seller_email or '@' not in seller_name))
                
                # Test 4: Business account detection
                is_business = seller.get('is_business', False)
                business_name = seller.get('business_name', '')
                
                if is_business:
                    print(f"      ✅ Business account detected: {business_name}")
                    has_business_name = bool(business_name.strip())
                    enrichment_tests.append(("Business Name Present", has_business_name))
                else:
                    print(f"      ℹ️  Regular account: {seller_name}")
                    enrichment_tests.append(("Business Account Handling", True))  # Regular accounts are handled correctly
                
                # Test 5: Location information
                location = seller.get('location', '')
                has_location = bool(location.strip()) and location != 'Location not specified'
                enrichment_tests.append(("Location Information", has_location))
                
                if not has_location:
                    print(f"      ⚠️  Location not specified or empty")
                else:
                    print(f"      ✅ Location: {location}")

        # Summary of enrichment tests
        passed_tests = sum(1 for _, success in enrichment_tests if success)
        total_tests = len(enrichment_tests)
        
        print(f"\n   📊 Seller Enrichment Summary: {passed_tests}/{total_tests} tests passed")
        
        overall_success = passed_tests >= (total_tests * 0.8)  # 80% pass rate
        self.log_test("Seller Information Enrichment", overall_success, 
                     f"{passed_tests}/{total_tests} enrichment tests passed")
        
        return overall_success

    def test_business_account_detection(self):
        """Test specific business account detection"""
        print("\n🏢 Testing Business Account Detection...")
        
        success, response = self.run_test(
            "Browse for Business Account Detection",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False

        business_listings = []
        regular_listings = []
        
        for listing in response:
            seller = listing.get('seller', {})
            is_business = seller.get('is_business', False)
            
            if is_business:
                business_listings.append(listing)
            else:
                regular_listings.append(listing)

        print(f"   Found {len(business_listings)} business listings")
        print(f"   Found {len(regular_listings)} regular listings")
        
        # Test business listings
        business_tests_passed = 0
        for listing in business_listings:
            seller = listing.get('seller', {})
            title = listing.get('title', 'Unknown')
            
            print(f"\n   🏢 Business Listing: {title[:50]}...")
            
            # Check business account fields
            is_business = seller.get('is_business', False)
            business_name = seller.get('business_name', '')
            seller_name = seller.get('name', '')
            
            print(f"      is_business: {is_business}")
            print(f"      business_name: '{business_name}'")
            print(f"      seller_name: '{seller_name}'")
            
            # Business account should have is_business=True and business_name
            if is_business and business_name.strip():
                business_tests_passed += 1
                print(f"      ✅ Business account properly detected")
            else:
                print(f"      ❌ Business account detection failed")

        # Test regular listings
        regular_tests_passed = 0
        for listing in regular_listings[:3]:  # Test first 3 regular listings
            seller = listing.get('seller', {})
            title = listing.get('title', 'Unknown')
            
            print(f"\n   👤 Regular Listing: {title[:50]}...")
            
            is_business = seller.get('is_business', False)
            business_name = seller.get('business_name', '')
            
            print(f"      is_business: {is_business}")
            print(f"      business_name: '{business_name}'")
            
            # Regular account should have is_business=False
            if not is_business:
                regular_tests_passed += 1
                print(f"      ✅ Regular account properly detected")
            else:
                print(f"      ❌ Regular account incorrectly marked as business")

        total_business_tests = len(business_listings)
        total_regular_tests = min(3, len(regular_listings))
        
        business_success = business_tests_passed == total_business_tests if total_business_tests > 0 else True
        regular_success = regular_tests_passed == total_regular_tests if total_regular_tests > 0 else True
        
        self.log_test("Business Account Detection", business_success, 
                     f"{business_tests_passed}/{total_business_tests} business accounts correct")
        self.log_test("Regular Account Detection", regular_success, 
                     f"{regular_tests_passed}/{total_regular_tests} regular accounts correct")
        
        return business_success and regular_success

    def test_username_vs_email_priority(self):
        """Test username vs email priority in seller.name field"""
        print("\n📧 Testing Username vs Email Priority...")
        
        success, response = self.run_test(
            "Browse for Username vs Email Test",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False

        username_tests = []
        
        for listing in response:
            seller = listing.get('seller', {})
            title = listing.get('title', 'Unknown')
            
            seller_name = seller.get('name', '')
            seller_username = seller.get('username', '')
            seller_email = seller.get('email', '')
            
            print(f"\n   📋 Listing: {title[:50]}...")
            print(f"      seller.name: '{seller_name}'")
            print(f"      seller.username: '{seller_username}'")
            print(f"      seller.email: '{seller_email}'")
            
            # Test: seller.name should be username, not email
            if seller_name and seller_username:
                if seller_name == seller_username:
                    print(f"      ✅ Name matches username")
                    username_tests.append(True)
                elif '@' in seller_name and seller_name == seller_email:
                    print(f"      ❌ Name is email instead of username")
                    username_tests.append(False)
                else:
                    print(f"      ⚠️  Name is neither username nor email")
                    username_tests.append(True)  # Acceptable if it's a display name
            else:
                print(f"      ⚠️  Missing name or username data")
                username_tests.append(False)

        passed_tests = sum(username_tests)
        total_tests = len(username_tests)
        
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        overall_success = success_rate >= 0.8  # 80% success rate
        
        self.log_test("Username vs Email Priority", overall_success, 
                     f"{passed_tests}/{total_tests} listings use username over email")
        
        return overall_success

    def test_data_consistency(self):
        """Test data consistency across all listings"""
        print("\n🔄 Testing Data Consistency...")
        
        success, response = self.run_test(
            "Browse for Data Consistency Test",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False

        consistency_issues = []
        enriched_listings = 0
        
        for listing in response:
            listing_id = listing.get('id', 'Unknown')
            seller = listing.get('seller', {})
            
            # Check if listing has enriched seller information
            if 'seller' in listing and isinstance(seller, dict):
                enriched_listings += 1
                
                # Check for required fields
                required_fields = ['name', 'username', 'is_business', 'business_name', 'verified', 'location']
                missing_fields = [field for field in required_fields if field not in seller]
                
                if missing_fields:
                    consistency_issues.append(f"Listing {listing_id}: Missing fields {missing_fields}")
                
                # Check for empty/null values in critical fields
                if not seller.get('name', '').strip():
                    consistency_issues.append(f"Listing {listing_id}: Empty seller name")
                
                if not seller.get('username', '').strip():
                    consistency_issues.append(f"Listing {listing_id}: Empty seller username")
                
                # Check business account consistency
                is_business = seller.get('is_business', False)
                business_name = seller.get('business_name', '')
                
                if is_business and not business_name.strip():
                    consistency_issues.append(f"Listing {listing_id}: Business account without business name")
            else:
                consistency_issues.append(f"Listing {listing_id}: No seller object or invalid seller data")

        total_listings = len(response)
        enrichment_rate = enriched_listings / total_listings if total_listings > 0 else 0
        
        print(f"   📊 Enrichment Rate: {enriched_listings}/{total_listings} ({enrichment_rate:.1%})")
        print(f"   📊 Consistency Issues: {len(consistency_issues)}")
        
        if consistency_issues:
            print("   ⚠️  Issues found:")
            for issue in consistency_issues[:5]:  # Show first 5 issues
                print(f"      - {issue}")
            if len(consistency_issues) > 5:
                print(f"      ... and {len(consistency_issues) - 5} more issues")

        # Success criteria: 90% enrichment rate and fewer than 10% consistency issues
        enrichment_success = enrichment_rate >= 0.9
        consistency_success = len(consistency_issues) <= (total_listings * 0.1)
        
        self.log_test("Data Enrichment Rate", enrichment_success, 
                     f"{enrichment_rate:.1%} listings enriched (target: 90%)")
        self.log_test("Data Consistency", consistency_success, 
                     f"{len(consistency_issues)} issues found (target: <{total_listings * 0.1:.0f})")
        
        return enrichment_success and consistency_success

    def cleanup_test_data(self):
        """Clean up test listings"""
        print("\n🧹 Cleaning up test data...")
        
        for listing_id in self.test_listing_ids:
            success, response = self.run_test(
                f"Delete Test Listing {listing_id[:8]}...",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                print(f"   ✅ Deleted test listing: {listing_id}")

    def run_seller_enrichment_tests(self):
        """Run complete seller enrichment test suite"""
        print("🚀 Starting Seller Information Enrichment Tests")
        print("=" * 60)

        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False

        # Create test data
        if not self.create_test_listings():
            print("❌ Failed to create test listings - stopping tests")
            return False

        # Run enrichment tests
        print("\n🔥 TESTING SELLER INFORMATION ENRICHMENT FIX...")
        
        test_results = []
        
        # Test 1: Seller Information Enrichment
        test_results.append(self.test_seller_information_enrichment())
        
        # Test 2: Business Account Detection
        test_results.append(self.test_business_account_detection())
        
        # Test 3: Username vs Email Priority
        test_results.append(self.test_username_vs_email_priority())
        
        # Test 4: Data Consistency
        test_results.append(self.test_data_consistency())

        # Cleanup
        self.cleanup_test_data()

        # Results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print("\n" + "=" * 60)
        print(f"📊 Seller Enrichment Test Results: {passed_tests}/{total_tests} test suites passed")
        print(f"📊 Overall Test Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All seller enrichment tests passed!")
            print("✅ Seller information enrichment fix is working correctly!")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} test suites failed")
            print("❌ Seller information enrichment fix needs attention")
            return False

def main():
    """Main test execution"""
    tester = SellerEnrichmentTester()
    success = tester.run_seller_enrichment_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())