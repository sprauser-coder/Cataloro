#!/usr/bin/env python3
"""
Browse Page Filter Functionality Test Suite
Tests the updated /api/marketplace/browse endpoint with new filter parameters
"""

import requests
import sys
import json
from datetime import datetime

class BrowseFilterTester:
    def __init__(self, base_url="https://market-upgrade-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.business_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_listings = []  # Store created test listings for cleanup

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers, params=params)
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
        """Setup test users including business user"""
        print("\n🔧 Setting up test users...")
        
        # Admin login
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

        # Regular user login
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
            "Business User Registration",
            "POST",
            "api/auth/register",
            200,
            data={
                "username": "business_user",
                "email": "business@cataloro.com",
                "full_name": "Business Account",
                "is_business": True,
                "business_name": "Test Business Solutions",
                "company_name": "Test Business Solutions"
            }
        )
        
        # Login business user
        success, response = self.run_test(
            "Business User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "business@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.business_user = response['user']
            print(f"   Business User: {self.business_user}")

        return self.admin_user and self.regular_user and self.business_user

    def create_test_listings(self):
        """Create test listings with different seller types and price ranges"""
        print("\n📝 Creating test listings for filter testing...")
        
        # Private seller listings (regular user)
        private_listings = [
            {
                "title": "Private Seller - MacBook Pro 16-inch",
                "description": "Personal MacBook Pro for sale. Excellent condition.",
                "price": 2500.00,
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"]
            },
            {
                "title": "Private Seller - Vintage Guitar",
                "description": "Beautiful vintage acoustic guitar from private collection.",
                "price": 800.00,
                "category": "Musical Instruments",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400"]
            },
            {
                "title": "Private Seller - Designer Watch",
                "description": "Luxury designer watch, barely used.",
                "price": 150.00,
                "category": "Fashion",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400"]
            }
        ]

        # Business seller listings (business user)
        business_listings = [
            {
                "title": "Business - Professional Camera Equipment",
                "description": "Professional camera equipment from authorized dealer.",
                "price": 1800.00,
                "category": "Photography",
                "condition": "New",
                "seller_id": self.business_user['id'],
                "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"]
            },
            {
                "title": "Business - Office Furniture Set",
                "description": "Complete office furniture set from business supplier.",
                "price": 1200.00,
                "category": "Furniture",
                "condition": "New",
                "seller_id": self.business_user['id'],
                "images": ["https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400"]
            },
            {
                "title": "Business - Gaming Laptop",
                "description": "High-performance gaming laptop from authorized retailer.",
                "price": 50.00,  # Low price for price range testing
                "category": "Electronics",
                "condition": "New",
                "seller_id": self.business_user['id'],
                "images": ["https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400"]
            }
        ]

        # Create all test listings
        all_listings = private_listings + business_listings
        created_count = 0
        
        for listing_data in all_listings:
            success, response = self.run_test(
                f"Create Test Listing: {listing_data['title'][:30]}...",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            if success and 'listing_id' in response:
                self.test_listings.append(response['listing_id'])
                created_count += 1
                print(f"   ✅ Created listing: {response['listing_id']}")

        print(f"\n📊 Created {created_count}/{len(all_listings)} test listings")
        return created_count == len(all_listings)

    def test_browse_no_filters(self):
        """Test browse endpoint with no filters (default behavior)"""
        print("\n🔍 Testing browse endpoint with no filters...")
        
        success, response = self.run_test(
            "Browse - No Filters (Default)",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            print(f"   Found {len(response)} total listings")
            
            # Verify response is array format
            if isinstance(response, list):
                self.log_test("Default Response Format", True, "Returns array format")
                
                # Check seller data enrichment
                if response:
                    first_listing = response[0]
                    has_seller_info = 'seller' in first_listing
                    if has_seller_info:
                        seller = first_listing['seller']
                        has_business_field = 'is_business' in seller
                        self.log_test("Seller Data Enrichment", has_business_field, 
                                     f"Seller has is_business field: {has_business_field}")
                    else:
                        self.log_test("Seller Data Enrichment", False, "No seller info in listings")
            else:
                self.log_test("Default Response Format", False, "Response is not array format")
        
        return success

    def test_type_filter_private(self):
        """Test type filter for Private sellers"""
        print("\n🏠 Testing type filter: Private...")
        
        success, response = self.run_test(
            "Browse - Type Filter: Private",
            "GET",
            "api/marketplace/browse",
            200,
            params={"type": "Private"}
        )
        
        if success:
            print(f"   Found {len(response)} private listings")
            
            # Verify all listings are from private sellers
            all_private = True
            for listing in response:
                seller = listing.get('seller', {})
                is_business = seller.get('is_business', False)
                if is_business:
                    all_private = False
                    print(f"   ❌ Found business listing in private filter: {listing.get('title', 'Unknown')}")
                    break
            
            self.log_test("Private Filter Accuracy", all_private, 
                         f"All {len(response)} listings are from private sellers: {all_private}")
        
        return success

    def test_type_filter_business(self):
        """Test type filter for Business sellers"""
        print("\n🏢 Testing type filter: Business...")
        
        success, response = self.run_test(
            "Browse - Type Filter: Business",
            "GET",
            "api/marketplace/browse",
            200,
            params={"type": "Business"}
        )
        
        if success:
            print(f"   Found {len(response)} business listings")
            
            # Verify all listings are from business sellers
            all_business = True
            for listing in response:
                seller = listing.get('seller', {})
                is_business = seller.get('is_business', False)
                if not is_business:
                    all_business = False
                    print(f"   ❌ Found private listing in business filter: {listing.get('title', 'Unknown')}")
                    break
            
            self.log_test("Business Filter Accuracy", all_business, 
                         f"All {len(response)} listings are from business sellers: {all_business}")
        
        return success

    def test_price_range_filter(self):
        """Test price range filtering"""
        print("\n💰 Testing price range filters...")
        
        # Test price range: 100-1000
        success1, response1 = self.run_test(
            "Browse - Price Range: 100-1000",
            "GET",
            "api/marketplace/browse",
            200,
            params={"price_from": 100, "price_to": 1000}
        )
        
        if success1:
            print(f"   Found {len(response1)} listings in price range 100-1000")
            
            # Verify all listings are within price range
            price_range_correct = True
            for listing in response1:
                price = listing.get('price', 0)
                if not (100 <= price <= 1000):
                    price_range_correct = False
                    print(f"   ❌ Listing outside price range: {listing.get('title', 'Unknown')} - €{price}")
                    break
            
            self.log_test("Price Range 100-1000 Accuracy", price_range_correct,
                         f"All {len(response1)} listings within range: {price_range_correct}")

        # Test minimum price filter
        success2, response2 = self.run_test(
            "Browse - Minimum Price: 500",
            "GET",
            "api/marketplace/browse",
            200,
            params={"price_from": 500}
        )
        
        if success2:
            print(f"   Found {len(response2)} listings with price >= 500")
            
            # Verify all listings meet minimum price
            min_price_correct = True
            for listing in response2:
                price = listing.get('price', 0)
                if price < 500:
                    min_price_correct = False
                    print(f"   ❌ Listing below minimum price: {listing.get('title', 'Unknown')} - €{price}")
                    break
            
            self.log_test("Minimum Price Filter Accuracy", min_price_correct,
                         f"All {len(response2)} listings >= €500: {min_price_correct}")

        # Test maximum price filter
        success3, response3 = self.run_test(
            "Browse - Maximum Price: 200",
            "GET",
            "api/marketplace/browse",
            200,
            params={"price_to": 200}
        )
        
        if success3:
            print(f"   Found {len(response3)} listings with price <= 200")
            
            # Verify all listings meet maximum price
            max_price_correct = True
            for listing in response3:
                price = listing.get('price', 0)
                if price > 200:
                    max_price_correct = False
                    print(f"   ❌ Listing above maximum price: {listing.get('title', 'Unknown')} - €{price}")
                    break
            
            self.log_test("Maximum Price Filter Accuracy", max_price_correct,
                         f"All {len(response3)} listings <= €200: {max_price_correct}")

        return success1 and success2 and success3

    def test_combined_filters(self):
        """Test combined type and price filters"""
        print("\n🔄 Testing combined filters...")
        
        # Test Business + Price Range 500-2000
        success1, response1 = self.run_test(
            "Browse - Business + Price 500-2000",
            "GET",
            "api/marketplace/browse",
            200,
            params={"type": "Business", "price_from": 500, "price_to": 2000}
        )
        
        if success1:
            print(f"   Found {len(response1)} business listings in price range 500-2000")
            
            # Verify all listings meet both criteria
            criteria_met = True
            for listing in response1:
                seller = listing.get('seller', {})
                is_business = seller.get('is_business', False)
                price = listing.get('price', 0)
                
                if not is_business or not (500 <= price <= 2000):
                    criteria_met = False
                    print(f"   ❌ Listing doesn't meet criteria: {listing.get('title', 'Unknown')} - Business: {is_business}, Price: €{price}")
                    break
            
            self.log_test("Combined Filter Accuracy", criteria_met,
                         f"All {len(response1)} listings meet both criteria: {criteria_met}")

        # Test Private + Low Price Range 0-300
        success2, response2 = self.run_test(
            "Browse - Private + Price 0-300",
            "GET",
            "api/marketplace/browse",
            200,
            params={"type": "Private", "price_from": 0, "price_to": 300}
        )
        
        if success2:
            print(f"   Found {len(response2)} private listings in price range 0-300")
            
            # Verify all listings meet both criteria
            criteria_met2 = True
            for listing in response2:
                seller = listing.get('seller', {})
                is_business = seller.get('is_business', False)
                price = listing.get('price', 0)
                
                if is_business or not (0 <= price <= 300):
                    criteria_met2 = False
                    print(f"   ❌ Listing doesn't meet criteria: {listing.get('title', 'Unknown')} - Business: {is_business}, Price: €{price}")
                    break
            
            self.log_test("Combined Filter Accuracy 2", criteria_met2,
                         f"All {len(response2)} listings meet both criteria: {criteria_met2}")

        return success1 and success2

    def test_edge_cases(self):
        """Test edge cases and invalid parameters"""
        print("\n⚠️ Testing edge cases...")
        
        # Test invalid type value
        success1, response1 = self.run_test(
            "Browse - Invalid Type",
            "GET",
            "api/marketplace/browse",
            200,  # Should still return 200 but treat as "all"
            params={"type": "InvalidType"}
        )
        
        if success1:
            self.log_test("Invalid Type Handling", True, "Endpoint handles invalid type gracefully")

        # Test price_from = 0, price_to = 0
        success2, response2 = self.run_test(
            "Browse - Zero Price Range",
            "GET",
            "api/marketplace/browse",
            200,
            params={"price_from": 0, "price_to": 0}
        )
        
        if success2:
            # Should return listings with price = 0 or handle gracefully
            self.log_test("Zero Price Range Handling", True, "Endpoint handles zero price range")

        # Test very high price range
        success3, response3 = self.run_test(
            "Browse - High Price Range",
            "GET",
            "api/marketplace/browse",
            200,
            params={"price_from": 10000, "price_to": 999999}
        )
        
        if success3:
            print(f"   Found {len(response3)} listings in high price range")
            self.log_test("High Price Range Handling", True, "Endpoint handles high price range")

        return success1 and success2 and success3

    def test_default_values(self):
        """Test default parameter values"""
        print("\n🔧 Testing default parameter values...")
        
        # Test with explicit defaults
        success1, response1 = self.run_test(
            "Browse - Explicit Defaults",
            "GET",
            "api/marketplace/browse",
            200,
            params={"type": "all", "price_from": 0, "price_to": 999999}
        )
        
        # Test with no parameters (implicit defaults)
        success2, response2 = self.run_test(
            "Browse - Implicit Defaults",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success1 and success2:
            # Results should be identical
            same_results = len(response1) == len(response2)
            if same_results and response1 and response2:
                # Check if first few listings are the same
                same_listings = True
                for i in range(min(3, len(response1), len(response2))):
                    if response1[i].get('id') != response2[i].get('id'):
                        same_listings = False
                        break
                same_results = same_listings
            
            self.log_test("Default Values Consistency", same_results,
                         f"Explicit and implicit defaults return same results: {same_results}")

        return success1 and success2

    def test_mongodb_query_construction(self):
        """Test MongoDB query construction for price ranges"""
        print("\n🗄️ Testing MongoDB query construction...")
        
        # Test various price combinations to ensure proper query construction
        test_cases = [
            {"price_from": 100, "expected_min": 100},
            {"price_to": 500, "expected_max": 500},
            {"price_from": 200, "price_to": 800, "expected_min": 200, "expected_max": 800},
        ]
        
        all_queries_work = True
        
        for i, case in enumerate(test_cases):
            params = {k: v for k, v in case.items() if k.startswith('price_')}
            
            success, response = self.run_test(
                f"MongoDB Query Test {i+1}",
                "GET",
                "api/marketplace/browse",
                200,
                params=params
            )
            
            if success:
                # Verify query worked by checking price constraints
                query_correct = True
                for listing in response:
                    price = listing.get('price', 0)
                    
                    if 'expected_min' in case and price < case['expected_min']:
                        query_correct = False
                        break
                    if 'expected_max' in case and price > case['expected_max']:
                        query_correct = False
                        break
                
                if not query_correct:
                    all_queries_work = False
                    print(f"   ❌ Query {i+1} returned listings outside expected range")
            else:
                all_queries_work = False
        
        self.log_test("MongoDB Query Construction", all_queries_work,
                     f"All price range queries work correctly: {all_queries_work}")
        
        return all_queries_work

    def cleanup_test_listings(self):
        """Clean up created test listings"""
        print("\n🧹 Cleaning up test listings...")
        
        deleted_count = 0
        for listing_id in self.test_listings:
            success, response = self.run_test(
                f"Delete Test Listing {listing_id[:8]}...",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                deleted_count += 1
        
        print(f"   Cleaned up {deleted_count}/{len(self.test_listings)} test listings")
        return deleted_count == len(self.test_listings)

    def run_all_tests(self):
        """Run complete browse filter test suite"""
        print("🚀 Starting Browse Page Filter Functionality Tests")
        print("=" * 70)

        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False

        if not self.create_test_listings():
            print("❌ Failed to create test listings - stopping tests")
            return False

        # Core filter tests
        print("\n" + "=" * 50)
        print("🔍 CORE FILTER FUNCTIONALITY TESTS")
        print("=" * 50)
        
        test_results = []
        
        # Test 1: No filters (default behavior)
        test_results.append(self.test_browse_no_filters())
        
        # Test 2: Type filters
        test_results.append(self.test_type_filter_private())
        test_results.append(self.test_type_filter_business())
        
        # Test 3: Price range filters
        test_results.append(self.test_price_range_filter())
        
        # Test 4: Combined filters
        test_results.append(self.test_combined_filters())
        
        # Test 5: Edge cases
        test_results.append(self.test_edge_cases())
        
        # Test 6: Default values
        test_results.append(self.test_default_values())
        
        # Test 7: MongoDB query construction
        test_results.append(self.test_mongodb_query_construction())

        # Cleanup
        self.cleanup_test_listings()

        # Results summary
        print("\n" + "=" * 70)
        print(f"📊 Browse Filter Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        passed_suites = sum(test_results)
        total_suites = len(test_results)
        
        print(f"📋 Test Suites: {passed_suites}/{total_suites} suites passed")
        
        if self.tests_passed == self.tests_run and passed_suites == total_suites:
            print("🎉 All browse filter tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} individual tests failed")
            print(f"⚠️  {total_suites - passed_suites} test suites failed")
            return False

def main():
    """Main test execution"""
    tester = BrowseFilterTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())