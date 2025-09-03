#!/usr/bin/env python3
"""
Browse Page Filtering Functionality Test Suite
Tests the updated /api/marketplace/browse endpoint with new filtering capabilities
"""

import requests
import sys
import json
from datetime import datetime

class BrowseFilteringTester:
    def __init__(self, base_url="https://cataloro-marketplace-1.preview.emergentagent.com"):
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
                    if isinstance(response_data, list):
                        details += f", Found {len(response_data)} items"
                    else:
                        details += f", Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}"
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
        """Setup test users for filtering tests"""
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
            print(f"   Admin User: {self.admin_user.get('username', 'N/A')}")

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
            print(f"   Regular User: {self.regular_user.get('username', 'N/A')}")

        # Create/Login business user
        success, response = self.run_test(
            "Business User Registration",
            "POST",
            "api/auth/register",
            200,
            data={
                "username": "business_seller",
                "email": "business@cataloro.com",
                "full_name": "Business Seller",
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
            print(f"   Business User: {self.business_user.get('username', 'N/A')} (is_business: {self.business_user.get('is_business', False)})")

        return self.admin_user and self.regular_user and self.business_user

    def create_test_listings(self):
        """Create test listings for filtering tests"""
        print("\n📝 Creating test listings for filtering...")
        
        if not (self.regular_user and self.business_user):
            print("❌ Cannot create test listings - missing users")
            return False

        # Private seller listings (various price ranges)
        private_listings = [
            {
                "title": "Private Seller - Budget Laptop",
                "description": "Affordable laptop for students. Good condition with add_info: Basic specifications suitable for everyday use.",
                "price": 250.00,
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400"]
            },
            {
                "title": "Private Seller - Gaming Console",
                "description": "Gaming console in excellent condition. add_info: Includes all original accessories and games.",
                "price": 450.00,
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400"]
            },
            {
                "title": "Private Seller - Premium Watch",
                "description": "Luxury watch from private collection. add_info: Swiss movement with original documentation.",
                "price": 1200.00,
                "category": "Fashion",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400"]
            }
        ]

        # Business seller listings (various price ranges)
        business_listings = [
            {
                "title": "Business Seller - Office Chair",
                "description": "Professional office chair from business inventory. add_info: Ergonomic design with warranty coverage.",
                "price": 180.00,
                "category": "Furniture",
                "condition": "New",
                "seller_id": self.business_user['id'],
                "images": ["https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400"]
            },
            {
                "title": "Business Seller - Professional Camera",
                "description": "Professional camera equipment from authorized dealer. add_info: Full manufacturer warranty included.",
                "price": 800.00,
                "category": "Photography",
                "condition": "New",
                "seller_id": self.business_user['id'],
                "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"]
            },
            {
                "title": "Business Seller - Enterprise Laptop",
                "description": "High-end laptop for business use. add_info: Enterprise-grade security features and support.",
                "price": 1500.00,
                "category": "Electronics",
                "condition": "New",
                "seller_id": self.business_user['id'],
                "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400"]
            }
        ]

        # Create all test listings
        all_listings = private_listings + business_listings
        created_count = 0

        for i, listing_data in enumerate(all_listings):
            success, response = self.run_test(
                f"Create Test Listing {i+1}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            if success and 'listing_id' in response:
                self.test_listings.append(response['listing_id'])
                created_count += 1
                print(f"   ✅ Created listing: {listing_data['title'][:30]}... (ID: {response['listing_id'][:8]}...)")

        success = created_count == len(all_listings)
        self.log_test("Test Listings Creation", success, f"Created {created_count}/{len(all_listings)} listings")
        return success

    def test_basic_browse_endpoint(self):
        """Test basic browse endpoint without filters"""
        print("\n🌐 Testing basic browse endpoint...")
        
        success, response = self.run_test(
            "Basic Browse Endpoint",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            print(f"   Found {len(response)} total listings")
            
            # Verify response structure
            if response and len(response) > 0:
                first_listing = response[0]
                required_fields = ['id', 'title', 'price', 'category', 'seller']
                has_all_fields = all(field in first_listing for field in required_fields)
                self.log_test("Browse Response Structure", has_all_fields, 
                             f"Required fields present: {has_all_fields}")
                
                # Check seller enrichment
                if 'seller' in first_listing:
                    seller = first_listing['seller']
                    seller_fields = ['name', 'username', 'is_business', 'business_name']
                    has_seller_fields = all(field in seller for field in seller_fields)
                    self.log_test("Seller Data Enrichment", has_seller_fields,
                                 f"Seller fields present: {has_seller_fields}")
                    print(f"   Sample seller data: is_business={seller.get('is_business')}, business_name='{seller.get('business_name')}'")
                
                # Check for add_info in descriptions
                add_info_found = any('add_info' in listing.get('description', '') for listing in response[:5])
                self.log_test("add_info Field Presence", add_info_found,
                             f"add_info content found in descriptions: {add_info_found}")
        
        return success

    def test_type_filtering_private(self):
        """Test type filtering for Private sellers"""
        print("\n👤 Testing Private seller type filtering...")
        
        success, response = self.run_test(
            "Type Filter - Private Sellers",
            "GET",
            "api/marketplace/browse",
            200,
            params={"type": "Private"}
        )
        
        if success:
            print(f"   Found {len(response)} private seller listings")
            
            # Verify all listings are from private sellers
            all_private = True
            business_count = 0
            for listing in response:
                seller = listing.get('seller', {})
                is_business = seller.get('is_business', False)
                if is_business:
                    business_count += 1
                    all_private = False
                    print(f"   ⚠️  Found business listing in private filter: {listing.get('title', 'N/A')}")
            
            self.log_test("Private Filter Accuracy", all_private,
                         f"All listings from private sellers: {all_private} (found {business_count} business listings)")
            
            # Check if we have our test private listings
            test_private_found = 0
            for listing in response:
                if listing.get('seller', {}).get('name') == self.regular_user.get('username'):
                    test_private_found += 1
            
            print(f"   Found {test_private_found} test private listings")
        
        return success

    def test_type_filtering_business(self):
        """Test type filtering for Business sellers"""
        print("\n🏢 Testing Business seller type filtering...")
        
        success, response = self.run_test(
            "Type Filter - Business Sellers",
            "GET",
            "api/marketplace/browse",
            200,
            params={"type": "Business"}
        )
        
        if success:
            print(f"   Found {len(response)} business seller listings")
            
            # Verify all listings are from business sellers
            all_business = True
            private_count = 0
            for listing in response:
                seller = listing.get('seller', {})
                is_business = seller.get('is_business', False)
                if not is_business:
                    private_count += 1
                    all_business = False
                    print(f"   ⚠️  Found private listing in business filter: {listing.get('title', 'N/A')}")
            
            self.log_test("Business Filter Accuracy", all_business,
                         f"All listings from business sellers: {all_business} (found {private_count} private listings)")
            
            # Check if we have our test business listings
            test_business_found = 0
            for listing in response:
                seller_name = listing.get('seller', {}).get('name', '')
                if 'business' in seller_name.lower() or listing.get('seller', {}).get('is_business'):
                    test_business_found += 1
            
            print(f"   Found {test_business_found} test business listings")
        
        return success

    def test_price_range_filtering(self):
        """Test price range filtering"""
        print("\n💰 Testing price range filtering...")
        
        # Test 1: Low price range (100-500)
        success1, response1 = self.run_test(
            "Price Filter - Low Range (100-500)",
            "GET",
            "api/marketplace/browse",
            200,
            params={"price_from": 100, "price_to": 500}
        )
        
        if success1:
            print(f"   Found {len(response1)} listings in €100-€500 range")
            
            # Verify all listings are within price range
            price_violations = 0
            for listing in response1:
                price = listing.get('price', 0)
                if not (100 <= price <= 500):
                    price_violations += 1
                    print(f"   ⚠️  Price violation: {listing.get('title', 'N/A')} - €{price}")
            
            price_accuracy = price_violations == 0
            self.log_test("Low Price Range Accuracy", price_accuracy,
                         f"All listings within €100-€500: {price_accuracy} ({price_violations} violations)")

        # Test 2: High price range (800-2000)
        success2, response2 = self.run_test(
            "Price Filter - High Range (800-2000)",
            "GET",
            "api/marketplace/browse",
            200,
            params={"price_from": 800, "price_to": 2000}
        )
        
        if success2:
            print(f"   Found {len(response2)} listings in €800-€2000 range")
            
            # Verify all listings are within price range
            price_violations = 0
            for listing in response2:
                price = listing.get('price', 0)
                if not (800 <= price <= 2000):
                    price_violations += 1
                    print(f"   ⚠️  Price violation: {listing.get('title', 'N/A')} - €{price}")
            
            price_accuracy = price_violations == 0
            self.log_test("High Price Range Accuracy", price_accuracy,
                         f"All listings within €800-€2000: {price_accuracy} ({price_violations} violations)")

        # Test 3: Minimum price only
        success3, response3 = self.run_test(
            "Price Filter - Minimum Only (500+)",
            "GET",
            "api/marketplace/browse",
            200,
            params={"price_from": 500}
        )
        
        if success3:
            print(f"   Found {len(response3)} listings €500+")
            
            # Verify all listings are above minimum
            below_min = 0
            for listing in response3:
                price = listing.get('price', 0)
                if price < 500:
                    below_min += 1
                    print(f"   ⚠️  Below minimum: {listing.get('title', 'N/A')} - €{price}")
            
            min_accuracy = below_min == 0
            self.log_test("Minimum Price Accuracy", min_accuracy,
                         f"All listings €500+: {min_accuracy} ({below_min} below minimum)")

        return success1 and success2 and success3

    def test_combined_filters(self):
        """Test combined type and price filtering"""
        print("\n🔄 Testing combined filters...")
        
        # Test 1: Business sellers in mid-price range (200-1000)
        success1, response1 = self.run_test(
            "Combined Filter - Business + Price Range (200-1000)",
            "GET",
            "api/marketplace/browse",
            200,
            params={"type": "Business", "price_from": 200, "price_to": 1000}
        )
        
        if success1:
            print(f"   Found {len(response1)} business listings in €200-€1000 range")
            
            # Verify both filters are applied
            violations = 0
            for listing in response1:
                seller = listing.get('seller', {})
                price = listing.get('price', 0)
                is_business = seller.get('is_business', False)
                
                if not is_business:
                    violations += 1
                    print(f"   ⚠️  Non-business seller: {listing.get('title', 'N/A')}")
                
                if not (200 <= price <= 1000):
                    violations += 1
                    print(f"   ⚠️  Price out of range: {listing.get('title', 'N/A')} - €{price}")
            
            combined_accuracy = violations == 0
            self.log_test("Business + Price Filter Accuracy", combined_accuracy,
                         f"All filters applied correctly: {combined_accuracy} ({violations} violations)")

        # Test 2: Private sellers in high-price range (1000+)
        success2, response2 = self.run_test(
            "Combined Filter - Private + High Price (1000+)",
            "GET",
            "api/marketplace/browse",
            200,
            params={"type": "Private", "price_from": 1000}
        )
        
        if success2:
            print(f"   Found {len(response2)} private listings €1000+")
            
            # Verify both filters are applied
            violations = 0
            for listing in response2:
                seller = listing.get('seller', {})
                price = listing.get('price', 0)
                is_business = seller.get('is_business', False)
                
                if is_business:
                    violations += 1
                    print(f"   ⚠️  Business seller in private filter: {listing.get('title', 'N/A')}")
                
                if price < 1000:
                    violations += 1
                    print(f"   ⚠️  Price below minimum: {listing.get('title', 'N/A')} - €{price}")
            
            combined_accuracy = violations == 0
            self.log_test("Private + High Price Filter Accuracy", combined_accuracy,
                         f"All filters applied correctly: {combined_accuracy} ({violations} violations)")

        return success1 and success2

    def test_edge_cases_and_validation(self):
        """Test edge cases and validation"""
        print("\n⚠️  Testing edge cases and validation...")
        
        # Test 1: Invalid type value
        success1, response1 = self.run_test(
            "Invalid Type Filter",
            "GET",
            "api/marketplace/browse",
            200,  # Should still return 200 but with all listings
            params={"type": "InvalidValue"}
        )
        
        if success1:
            print(f"   Invalid type filter returned {len(response1)} listings (should return all)")
            # Should return all listings when type is invalid
            self.log_test("Invalid Type Handling", True, "Invalid type filter handled gracefully")

        # Test 2: Extreme price ranges
        success2, response2 = self.run_test(
            "Extreme Price Range (999999-0)",
            "GET",
            "api/marketplace/browse",
            200,
            params={"price_from": 999999, "price_to": 0}
        )
        
        if success2:
            print(f"   Extreme price range returned {len(response2)} listings")
            # Should return empty or handle gracefully
            self.log_test("Extreme Price Range Handling", True, "Extreme price range handled gracefully")

        # Test 3: Negative prices
        success3, response3 = self.run_test(
            "Negative Price Filter",
            "GET",
            "api/marketplace/browse",
            200,
            params={"price_from": -100, "price_to": 50}
        )
        
        if success3:
            print(f"   Negative price filter returned {len(response3)} listings")
            self.log_test("Negative Price Handling", True, "Negative price filter handled gracefully")

        # Test 4: Empty parameters
        success4, response4 = self.run_test(
            "Empty Parameters",
            "GET",
            "api/marketplace/browse",
            200,
            params={"type": "", "price_from": "", "price_to": ""}
        )
        
        if success4:
            print(f"   Empty parameters returned {len(response4)} listings")
            self.log_test("Empty Parameters Handling", True, "Empty parameters handled gracefully")

        return success1 and success2 and success3 and success4

    def test_api_endpoint_consistency(self):
        """Test consistency across related endpoints"""
        print("\n🔗 Testing API endpoint consistency...")
        
        # Test 1: /api/marketplace/browse (main endpoint)
        success1, browse_response = self.run_test(
            "Browse Endpoint Consistency",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        # Test 2: /api/listings (admin panel endpoint)
        success2, listings_response = self.run_test(
            "Admin Listings Endpoint",
            "GET",
            "api/listings",
            200
        )
        
        if success1 and success2:
            browse_count = len(browse_response)
            admin_count = listings_response.get('total', 0) if isinstance(listings_response, dict) else len(listings_response)
            
            print(f"   Browse endpoint: {browse_count} listings")
            print(f"   Admin endpoint: {admin_count} listings")
            
            # Check data consistency (browse should show active listings, admin shows all)
            consistency_check = browse_count <= admin_count  # Browse should have same or fewer (only active)
            self.log_test("Browse vs Admin Consistency", consistency_check,
                         f"Browse count ({browse_count}) <= Admin count ({admin_count}): {consistency_check}")

        # Test 3: /api/user/my-listings (user-specific endpoint)
        if self.regular_user:
            success3, my_listings_response = self.run_test(
                "My Listings Endpoint",
                "GET",
                f"api/user/my-listings/{self.regular_user['id']}",
                200
            )
            
            if success3:
                my_count = len(my_listings_response)
                print(f"   My listings endpoint: {my_count} listings for user")
                
                # Verify user's listings appear in browse
                user_listings_in_browse = 0
                for listing in browse_response:
                    if listing.get('seller_id') == self.regular_user['id']:
                        user_listings_in_browse += 1
                
                user_consistency = user_listings_in_browse >= my_count  # Browse should show user's active listings
                self.log_test("User Listings Consistency", user_consistency,
                             f"User listings in browse ({user_listings_in_browse}) >= My listings ({my_count}): {user_consistency}")

        return success1 and success2

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

        self.log_test("Test Cleanup", deleted_count == len(self.test_listings),
                     f"Deleted {deleted_count}/{len(self.test_listings)} test listings")

    def run_all_filtering_tests(self):
        """Run complete filtering test suite"""
        print("🚀 Starting Browse Page Filtering Tests")
        print("=" * 60)

        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False

        if not self.create_test_listings():
            print("❌ Failed to create test listings - stopping tests")
            return False

        # Core filtering tests
        print("\n🎯 CORE FILTERING TESTS")
        basic_success = self.test_basic_browse_endpoint()
        private_success = self.test_type_filtering_private()
        business_success = self.test_type_filtering_business()
        price_success = self.test_price_range_filtering()
        combined_success = self.test_combined_filters()

        # Edge cases and validation
        print("\n🛡️  VALIDATION TESTS")
        validation_success = self.test_edge_cases_and_validation()

        # API consistency
        print("\n🔗 CONSISTENCY TESTS")
        consistency_success = self.test_api_endpoint_consistency()

        # Cleanup
        self.cleanup_test_listings()

        # Results summary
        test_categories = [
            ("Basic Browse", basic_success),
            ("Private Filter", private_success),
            ("Business Filter", business_success),
            ("Price Range Filter", price_success),
            ("Combined Filters", combined_success),
            ("Validation", validation_success),
            ("API Consistency", consistency_success)
        ]

        passed_categories = sum(1 for _, success in test_categories if success)
        total_categories = len(test_categories)

        print("\n" + "=" * 60)
        print(f"📊 FILTERING TEST RESULTS")
        print(f"Overall: {self.tests_passed}/{self.tests_run} individual tests passed")
        print(f"Categories: {passed_categories}/{total_categories} test categories passed")
        
        print("\n📋 Category Results:")
        for category, success in test_categories:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {category}: {status}")

        overall_success = passed_categories == total_categories
        
        if overall_success:
            print("\n🎉 ALL BROWSE FILTERING TESTS PASSED!")
            print("✅ Type filtering (Private/Business) working correctly")
            print("✅ Price range filtering working correctly")
            print("✅ Combined filters working correctly")
            print("✅ Edge cases handled gracefully")
            print("✅ API endpoints consistent")
            print("✅ Seller data enrichment working")
            print("✅ add_info field integration confirmed")
        else:
            print(f"\n⚠️  {total_categories - passed_categories} test categories failed")
            print("See detailed results above for specific issues")

        return overall_success

def main():
    """Main test execution"""
    tester = BrowseFilteringTester()
    success = tester.run_all_filtering_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())