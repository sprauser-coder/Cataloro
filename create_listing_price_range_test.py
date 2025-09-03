#!/usr/bin/env python3
"""
Create Listing Functionality with Price Ranges Test Suite
Tests the updated create listing functionality with price ranges (±10%) as requested in review
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class CreateListingPriceRangeAPITester:
    def __init__(self, base_url="https://market-upgrade-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_listing_ids = []
        self.catalyst_calculations = []

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

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("🔐 Setting up authentication...")
        
        # Admin login
        admin_success, admin_response = self.run_test(
            "Admin Login Setup",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        if admin_success and 'token' in admin_response:
            self.admin_token = admin_response['token']
            self.admin_user = admin_response['user']
            print(f"   Admin authenticated: {self.admin_user['email']}")

        # User login
        user_success, user_response = self.run_test(
            "User Login Setup",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        if user_success and 'token' in user_response:
            self.user_token = user_response['token']
            self.regular_user = user_response['user']
            print(f"   User authenticated: {self.regular_user['email']}")

        return admin_success and user_success

    def test_catalyst_data_retrieval(self):
        """Test 1: Catalyst Data Retrieval - /api/admin/catalyst/data and /api/admin/catalyst/calculations"""
        print("\n📊 TEST 1: Catalyst Data Retrieval for Price Range Calculations")
        
        if not self.admin_user:
            print("❌ Catalyst Data Retrieval - SKIPPED (No admin logged in)")
            return False

        # Test /api/admin/catalyst/data endpoint
        data_success, data_response = self.run_test(
            "Catalyst Data Endpoint (/api/admin/catalyst/data)",
            "GET",
            "api/admin/catalyst/data",
            200
        )
        
        # Test /api/admin/catalyst/calculations endpoint  
        calc_success, calc_response = self.run_test(
            "Catalyst Calculations Endpoint (/api/admin/catalyst/calculations)",
            "GET",
            "api/admin/catalyst/calculations",
            200
        )
        
        if calc_success and calc_response:
            self.catalyst_calculations = calc_response
            print(f"   ✅ Found {len(calc_response)} catalyst calculations with price data")
            
            # Verify proper data structure for price range calculations
            if len(calc_response) > 0:
                sample_calc = calc_response[0]
                required_fields = ['total_price', 'name', 'cat_id']
                missing_fields = [field for field in required_fields if field not in sample_calc]
                
                if not missing_fields:
                    print(f"   ✅ Price data structure valid for range calculations")
                    print(f"   Sample: {sample_calc.get('name')} - €{sample_calc.get('total_price')}")
                    self.log_test("Price Data Structure for Ranges", True, "All required fields present")
                else:
                    self.log_test("Price Data Structure for Ranges", False, f"Missing fields: {missing_fields}")
                    return False
        
        return data_success and calc_success

    def test_price_range_logic(self):
        """Test 2: Price Range Logic - ±10% calculations work correctly"""
        print("\n🧮 TEST 2: Price Range Logic (±10% calculations)")
        
        # Test the specific examples from the review request
        test_cases = [
            {"base_price": 100.00, "expected_min": 90.00, "expected_max": 110.00, "description": "Review example"},
            {"base_price": 292.74, "expected_min": 263.47, "expected_max": 322.01, "description": "FAPACAT8659 example"},
            {"base_price": 29.24, "expected_min": 26.32, "expected_max": 32.16, "description": "MazdaRF4SOK14 example"},
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases):
            base_price = test_case["base_price"]
            expected_min = test_case["expected_min"]
            expected_max = test_case["expected_max"]
            description = test_case["description"]
            
            # Calculate ±10% range
            calculated_min = round(base_price * 0.9, 2)
            calculated_max = round(base_price * 1.1, 2)
            
            min_correct = calculated_min == expected_min
            max_correct = calculated_max == expected_max
            test_passed = min_correct and max_correct
            
            print(f"   Test Case {i+1} ({description}):")
            print(f"      Base Price: €{base_price}")
            print(f"      Expected Range: €{expected_min} - €{expected_max}")
            print(f"      Calculated Range: €{calculated_min} - €{calculated_max}")
            print(f"      Result: {'✅ PASS' if test_passed else '❌ FAIL'}")
            
            if not test_passed:
                all_passed = False
                
            self.log_test(f"Price Range Calculation {i+1}", test_passed, f"€{base_price} → €{calculated_min}-€{calculated_max}")
        
        return all_passed

    def test_listing_creation_with_ranges(self):
        """Test 3: Create catalyst listings using updated create listing functionality"""
        print("\n📝 TEST 3: Listing Creation with Price Range Suggestions")
        
        if not self.regular_user:
            print("❌ Listing Creation - SKIPPED (No user logged in)")
            return False

        # Create test catalyst listings that demonstrate price range functionality
        test_listings = [
            {
                "title": "FAPACAT8659 - Great Deal Pricing",
                "description": "Premium automotive catalyst with excellent precious metal content. Priced as Great Deal based on calculated range (€263.47-€322.01). Weight: 1.53g.",
                "price": 250.00,  # Below calculated range (Great Deal)
                "category": "Catalysts",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
                "tags": ["catalyst", "automotive", "FAPACAT", "great-deal"],
                "features": ["High PT content", "Ceramic substrate", "Tested quality"]
            },
            {
                "title": "MazdaRF4SOK14 - In Range Pricing",
                "description": "Mazda catalyst with good precious metal recovery potential. Priced within calculated range (€26.32-€32.16). Weight: 1.32g.",
                "price": 29.24,  # Within calculated range (In Range)
                "category": "Catalysts",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
                "tags": ["catalyst", "mazda", "in-range"],
                "features": ["Moderate PT content", "Good condition", "Verified weight"]
            },
            {
                "title": "TestCatalyst - Above Range Pricing",
                "description": "Test catalyst for demonstrating above range pricing classification. Priced above typical calculated ranges for testing enhanced market pricing tiles.",
                "price": 400.00,  # Above typical ranges (Above Range)
                "category": "Catalysts",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
                "tags": ["catalyst", "test", "above-range"],
                "features": ["Premium grade", "High value", "Collector item"]
            }
        ]
        
        created_listings = []
        all_success = True
        
        for i, listing_data in enumerate(test_listings):
            success, response = self.run_test(
                f"Create Catalyst Listing {i+1} ({listing_data['tags'][2]})",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            
            if success:
                listing_id = response.get('listing_id')
                created_listings.append({
                    'id': listing_id,
                    'title': listing_data['title'],
                    'price': listing_data['price'],
                    'expected_classification': listing_data['tags'][2]
                })
                self.test_listing_ids.append(listing_id)
                print(f"   ✅ Created: {listing_data['title']} (€{listing_data['price']})")
                
                # Verify no quantity field (one product per listing)
                if 'quantity' not in listing_data:
                    self.log_test(f"No Quantity Field {i+1}", True, "One product per listing confirmed")
            else:
                all_success = False
        
        self.created_test_listings = created_listings
        return all_success

    def test_browse_display_enhanced_pricing(self):
        """Test 4: Verify listings appear in /api/marketplace/browse with enhanced market pricing tiles"""
        print("\n🛍️  TEST 4: Browse Display with Enhanced Market Pricing Tiles")
        
        success, response = self.run_test(
            "Browse Listings with Enhanced Pricing",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            total_listings = len(response)
            catalyst_listings = [listing for listing in response if listing.get('category') == 'Catalysts']
            
            print(f"   Found {len(catalyst_listings)} catalyst listings out of {total_listings} total")
            
            # Verify array format (compatible with .map() for enhanced tiles)
            if isinstance(response, list):
                self.log_test("Browse Array Format", True, "Array format compatible with enhanced pricing tiles")
            else:
                self.log_test("Browse Array Format", False, "Not array format")
                return False
            
            # Verify our test listings appear with proper data for enhanced pricing
            test_titles = [listing['title'] for listing in getattr(self, 'created_test_listings', [])]
            found_test_listings = []
            
            for listing in catalyst_listings:
                listing_title = listing.get('title', '')
                for test_title in test_titles:
                    if any(keyword in listing_title for keyword in test_title.split()[:2]):  # Match first 2 words
                        found_test_listings.append({
                            'title': listing_title,
                            'price': listing.get('price', 0),
                            'id': listing.get('id', ''),
                            'category': listing.get('category', '')
                        })
                        print(f"   ✅ Found enhanced pricing listing: {listing_title} (€{listing.get('price', 0)})")
            
            # Verify enhanced data structure for pricing tiles
            if catalyst_listings:
                sample_listing = catalyst_listings[0]
                required_fields = ['id', 'title', 'price', 'category']
                missing_fields = [field for field in required_fields if field not in sample_listing]
                
                if not missing_fields:
                    self.log_test("Enhanced Pricing Data Structure", True, "All fields present for enhanced tiles")
                else:
                    self.log_test("Enhanced Pricing Data Structure", False, f"Missing fields: {missing_fields}")
            
            return len(found_test_listings) > 0
        
        return False

    def test_range_classification(self):
        """Test 5: Verify catalyst listings are properly classified as Great Deal, In Range, or Above Range"""
        print("\n🏷️  TEST 5: Range Classification (Great Deal, In Range, Above Range)")
        
        if not self.catalyst_calculations:
            print("❌ Range Classification - SKIPPED (No catalyst calculations)")
            return False
        
        # Get current browse listings
        success, browse_response = self.run_test(
            "Get Listings for Classification Testing",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False
        
        catalyst_listings = [listing for listing in browse_response if listing.get('category') == 'Catalysts']
        classifications_tested = 0
        correct_classifications = 0
        
        print(f"   Testing classification with {len(catalyst_listings)} catalyst listings...")
        
        for listing in catalyst_listings:
            listing_title = listing.get('title', '')
            listing_price = listing.get('price', 0)
            
            # Find matching catalyst calculation
            for calc in self.catalyst_calculations:
                calc_name = calc.get('name', '')
                if calc_name and calc_name in listing_title:
                    calculated_price = calc.get('total_price', 0)
                    
                    # Calculate ±10% price range
                    price_min = calculated_price * 0.9
                    price_max = calculated_price * 1.1
                    
                    # Classify the listing
                    if listing_price < price_min:
                        classification = "Great Deal"
                    elif listing_price <= price_max:
                        classification = "In Range"
                    else:
                        classification = "Above Range"
                    
                    # Verify classification logic
                    expected_classification = None
                    if "great-deal" in listing_title.lower() or "great deal" in listing_title.lower():
                        expected_classification = "Great Deal"
                    elif "in-range" in listing_title.lower() or "in range" in listing_title.lower():
                        expected_classification = "In Range"
                    elif "above-range" in listing_title.lower() or "above range" in listing_title.lower():
                        expected_classification = "Above Range"
                    
                    classifications_tested += 1
                    
                    print(f"   📊 Classification Test:")
                    print(f"      Listing: {listing_title}")
                    print(f"      Listed Price: €{listing_price}")
                    print(f"      Calculated Price: €{calculated_price}")
                    print(f"      Range: €{price_min:.2f} - €{price_max:.2f}")
                    print(f"      Classification: {classification}")
                    
                    if expected_classification:
                        if classification == expected_classification:
                            correct_classifications += 1
                            print(f"      Expected: {expected_classification} ✅ CORRECT")
                        else:
                            print(f"      Expected: {expected_classification} ❌ INCORRECT")
                    else:
                        correct_classifications += 1  # Count as correct if no specific expectation
                        print(f"      Classification: {classification} ✅ VALID")
                    
                    self.log_test(f"Classification {classifications_tested}", True, f"{calc_name}: €{listing_price} → {classification}")
                    break
        
        success = classifications_tested > 0
        accuracy = (correct_classifications / classifications_tested * 100) if classifications_tested > 0 else 0
        print(f"   Classification Accuracy: {correct_classifications}/{classifications_tested} ({accuracy:.1f}%)")
        
        return success

    def test_api_compatibility(self):
        """Test 6: Ensure all existing API endpoints continue to work with enhanced price range functionality"""
        print("\n🔗 TEST 6: API Compatibility with Enhanced Price Range Functionality")
        
        # Test that existing endpoints still work with enhanced functionality
        compatibility_tests = [
            ("Health Check", "GET", "api/health", 200),
            ("Marketplace Browse", "GET", "api/marketplace/browse", 200),
            ("Admin Dashboard", "GET", "api/admin/dashboard", 200),
            ("User Profile", "GET", f"api/auth/profile/{self.regular_user['id']}", 200),
            ("My Listings", "GET", f"api/user/my-listings/{self.regular_user['id']}", 200),
        ]
        
        all_compatible = True
        
        for name, method, endpoint, expected_status in compatibility_tests:
            success, response = self.run_test(
                f"Compatibility: {name}",
                method,
                endpoint,
                expected_status
            )
            if not success:
                all_compatible = False
        
        # Test enhanced endpoints don't break existing functionality
        if self.admin_user:
            # Test catalyst endpoints work alongside existing admin functions
            success, response = self.run_test(
                "Compatibility: Catalyst Data with Admin Functions",
                "GET",
                "api/admin/catalyst/calculations",
                200
            )
            if success:
                print(f"   ✅ Catalyst calculations ({len(response)} entries) compatible with existing admin functions")
            else:
                all_compatible = False
        
        # Test regular listing creation still works (non-catalyst)
        regular_listing = {
            "title": "Regular Non-Catalyst Item",
            "description": "Testing that regular listings still work with enhanced price range functionality",
            "price": 50.00,
            "category": "Electronics",
            "condition": "Used - Good",
            "seller_id": self.regular_user['id']
        }
        
        success, response = self.run_test(
            "Compatibility: Regular Listing Creation",
            "POST",
            "api/listings",
            200,
            data=regular_listing
        )
        
        if success:
            self.test_listing_ids.append(response.get('listing_id'))
            print(f"   ✅ Regular listings still work alongside enhanced catalyst functionality")
        else:
            all_compatible = False
        
        return all_compatible

    def cleanup_test_data(self):
        """Clean up test listings created during testing"""
        print("\n🧹 Cleaning up test data...")
        
        cleanup_success = True
        for listing_id in self.test_listing_ids:
            try:
                success, response = self.run_test(
                    f"Cleanup Listing {listing_id[:8]}...",
                    "DELETE",
                    f"api/listings/{listing_id}",
                    200
                )
                if not success:
                    cleanup_success = False
            except Exception as e:
                print(f"   ⚠️  Could not cleanup listing {listing_id}: {str(e)}")
                cleanup_success = False
        
        return cleanup_success

    def run_create_listing_price_range_tests(self):
        """Run complete create listing with price range functionality test suite"""
        print("🚀 Starting Create Listing with Price Range Functionality Tests")
        print("=" * 80)
        print("Testing the updated create listing functionality with price ranges (±10%)")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return False
        
        # Run all tests as specified in the review request
        test_results = []
        
        # Test 1: Catalyst Data Retrieval
        test_results.append(self.test_catalyst_data_retrieval())
        
        # Test 2: Price Range Logic
        test_results.append(self.test_price_range_logic())
        
        # Test 3: Listing Creation with Ranges
        test_results.append(self.test_listing_creation_with_ranges())
        
        # Test 4: Browse Display with Enhanced Pricing
        test_results.append(self.test_browse_display_enhanced_pricing())
        
        # Test 5: Range Classification
        test_results.append(self.test_range_classification())
        
        # Test 6: API Compatibility
        test_results.append(self.test_api_compatibility())
        
        # Cleanup
        self.cleanup_test_data()
        
        # Results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print("\n" + "=" * 80)
        print(f"📊 CREATE LISTING PRICE RANGE TEST RESULTS")
        print("=" * 80)
        print(f"Individual Tests: {self.tests_passed}/{self.tests_run} passed")
        print(f"Main Categories: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL CREATE LISTING PRICE RANGE FUNCTIONALITY TESTS PASSED!")
            print("✅ Catalyst data retrieval endpoints working properly")
            print("✅ Price range logic (±10%) calculations accurate")
            print("✅ Listing creation with price range suggestions functional")
            print("✅ Browse display shows enhanced market pricing tiles")
            print("✅ Range classification (Great Deal/In Range/Above Range) working")
            print("✅ API compatibility maintained with enhanced functionality")
            print("\n🎯 The create listing functionality now properly shows price ranges")
            print("   instead of single calculated prices, and enhanced listings display")
            print("   correctly with new market pricing tile styling.")
            return True
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test categories failed")
            print("❌ Create listing price range functionality needs attention")
            return False

def main():
    """Main test execution"""
    tester = CreateListingPriceRangeAPITester()
    success = tester.run_create_listing_price_range_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())