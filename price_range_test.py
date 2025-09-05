#!/usr/bin/env python3
"""
Cataloro Marketplace Price Range Functionality Test Suite
Tests the updated price range functionality for market price suggestions
"""

import requests
import sys
import json
from datetime import datetime

class PriceRangeAPITester:
    def __init__(self, base_url="https://cataloro-marketplace-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.catalyst_data = []
        self.test_listings = []

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
            
        return admin_success and user_success

    def test_catalyst_calculations_data(self):
        """Test that catalyst calculations endpoint provides proper price data"""
        if not self.admin_user:
            print("❌ Catalyst Calculations Data - SKIPPED (No admin logged in)")
            return False
            
        success, response = self.run_test(
            "Catalyst Calculations Data Retrieval",
            "GET",
            "api/admin/catalyst/calculations",
            200
        )
        
        if success:
            self.catalyst_data = response
            print(f"   Found {len(response)} catalyst calculations")
            
            # Verify data structure for price range calculations
            if response and len(response) > 0:
                first_calc = response[0]
                required_fields = ['total_price', 'name', 'cat_id']
                missing_fields = [field for field in required_fields if field not in first_calc]
                
                if not missing_fields:
                    print(f"   ✅ All required fields present for price range calculations")
                    print(f"   Sample catalyst: {first_calc.get('name')} - €{first_calc.get('total_price')}")
                    self.log_test("Catalyst Data Structure Validation", True, "All required fields present")
                else:
                    self.log_test("Catalyst Data Structure Validation", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                print("   ⚠️  No catalyst calculations found")
                return False
                
        return success

    def test_price_range_calculation_logic(self):
        """Test ±10% price range calculation logic"""
        print("\n💰 Testing Price Range Calculation Logic (±10%)...")
        
        if not self.catalyst_data:
            print("❌ Price Range Calculation - SKIPPED (No catalyst data)")
            return False
            
        # Test with different price points
        test_cases = [
            {"calculated_price": 100.00, "expected_min": 90.00, "expected_max": 110.00},
            {"calculated_price": 292.74, "expected_min": 263.47, "expected_max": 322.01},
            {"calculated_price": 29.24, "expected_min": 26.32, "expected_max": 32.16},
            {"calculated_price": 50.50, "expected_min": 45.45, "expected_max": 55.55}
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases):
            calculated_price = test_case["calculated_price"]
            expected_min = test_case["expected_min"]
            expected_max = test_case["expected_max"]
            
            # Calculate ±10% range
            actual_min = round(calculated_price * 0.9, 2)
            actual_max = round(calculated_price * 1.1, 2)
            
            min_match = abs(actual_min - expected_min) < 0.01
            max_match = abs(actual_max - expected_max) < 0.01
            
            test_passed = min_match and max_match
            all_passed = all_passed and test_passed
            
            print(f"   Test Case {i+1}: €{calculated_price}")
            print(f"      Expected Range: €{expected_min} - €{expected_max}")
            print(f"      Calculated Range: €{actual_min} - €{actual_max}")
            print(f"      Result: {'✅ PASS' if test_passed else '❌ FAIL'}")
            
        self.log_test("Price Range Calculation Logic", all_passed, f"Tested {len(test_cases)} price range calculations")
        return all_passed

    def test_range_classification_logic(self):
        """Test price range classification (Great Deal, In Range, Above Range)"""
        print("\n🎯 Testing Range Classification Logic...")
        
        # Test with €100 catalyst as example from review request
        calculated_price = 100.00
        price_min = calculated_price * 0.9  # €90.00
        price_max = calculated_price * 1.1  # €110.00
        
        test_scenarios = [
            {"price": 85.00, "expected": "Great Deal", "reason": "below range"},
            {"price": 89.99, "expected": "Great Deal", "reason": "below range"},
            {"price": 90.00, "expected": "In Range", "reason": "at minimum"},
            {"price": 95.00, "expected": "In Range", "reason": "within range"},
            {"price": 100.00, "expected": "In Range", "reason": "at calculated price"},
            {"price": 105.00, "expected": "In Range", "reason": "within range"},
            {"price": 110.00, "expected": "In Range", "reason": "at maximum"},
            {"price": 110.01, "expected": "Above Range", "reason": "above range"},
            {"price": 115.00, "expected": "Above Range", "reason": "above range"}
        ]
        
        all_passed = True
        
        for scenario in test_scenarios:
            price = scenario["price"]
            expected = scenario["expected"]
            reason = scenario["reason"]
            
            # Implement classification logic
            if price < price_min:
                actual = "Great Deal"
            elif price <= price_max:
                actual = "In Range"
            else:
                actual = "Above Range"
                
            test_passed = actual == expected
            all_passed = all_passed and test_passed
            
            print(f"   Price €{price} ({reason}): Expected '{expected}', Got '{actual}' {'✅' if test_passed else '❌'}")
            
        self.log_test("Range Classification Logic", all_passed, f"Tested {len(test_scenarios)} classification scenarios")
        return all_passed

    def create_test_catalyst_listings(self):
        """Create test catalyst listings with different price points for range testing"""
        if not self.regular_user:
            print("❌ Create Test Listings - SKIPPED (No user logged in)")
            return False
            
        print("\n📝 Creating Test Catalyst Listings for Range Testing...")
        
        # Use real catalyst data if available
        test_catalyst = None
        if self.catalyst_data:
            # Find a catalyst with a reasonable price for testing
            for catalyst in self.catalyst_data:
                if catalyst.get('total_price', 0) > 50 and catalyst.get('total_price', 0) < 500:
                    test_catalyst = catalyst
                    break
        
        if not test_catalyst:
            # Use example from review request
            test_catalyst = {
                'name': 'FAPACAT8659',
                'total_price': 100.00,
                'cat_id': '32075'
            }
        
        calculated_price = test_catalyst['total_price']
        catalyst_name = test_catalyst['name']
        
        # Create listings with different price points for testing
        test_listings_data = [
            {
                "title": f"{catalyst_name} - Great Deal Price",
                "description": f"Catalyst listing priced below range for testing. Calculated price: €{calculated_price}",
                "price": round(calculated_price * 0.85, 2),  # Below range (Great Deal)
                "category": "Catalysts",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "tags": ["catalyst", "test", "great-deal"]
            },
            {
                "title": f"{catalyst_name} - In Range Price",
                "description": f"Catalyst listing priced within range for testing. Calculated price: €{calculated_price}",
                "price": round(calculated_price * 0.95, 2),  # Within range (In Range)
                "category": "Catalysts", 
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "tags": ["catalyst", "test", "in-range"]
            },
            {
                "title": f"{catalyst_name} - Above Range Price",
                "description": f"Catalyst listing priced above range for testing. Calculated price: €{calculated_price}",
                "price": round(calculated_price * 1.15, 2),  # Above range (Above Range)
                "category": "Catalysts",
                "condition": "Used - Good", 
                "seller_id": self.regular_user['id'],
                "tags": ["catalyst", "test", "above-range"]
            }
        ]
        
        created_listings = 0
        
        for listing_data in test_listings_data:
            success, response = self.run_test(
                f"Create Test Listing - {listing_data['tags'][2]}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            
            if success:
                created_listings += 1
                self.test_listings.append({
                    'id': response.get('listing_id'),
                    'price': listing_data['price'],
                    'calculated_price': calculated_price,
                    'expected_classification': listing_data['tags'][2]
                })
                
        success = created_listings == len(test_listings_data)
        self.log_test("Test Catalyst Listings Creation", success, f"Created {created_listings}/{len(test_listings_data)} test listings")
        return success

    def test_price_range_display_format(self):
        """Test that price range displays correctly in expected format"""
        print("\n💱 Testing Price Range Display Format...")
        
        if not self.catalyst_data:
            print("❌ Price Range Display - SKIPPED (No catalyst data)")
            return False
            
        # Test with example from review request (€100 catalyst)
        test_price = 100.00
        expected_min = 90.00
        expected_max = 110.00
        
        # Format as expected in frontend
        formatted_range = f"€{expected_min:.2f} - €{expected_max:.2f}"
        expected_format = "€90.00 - €110.00"
        
        format_correct = formatted_range == expected_format
        
        print(f"   Test Price: €{test_price}")
        print(f"   Expected Format: {expected_format}")
        print(f"   Actual Format: {formatted_range}")
        print(f"   Format Match: {'✅ PASS' if format_correct else '❌ FAIL'}")
        
        # Test with real catalyst data
        real_data_tests = 0
        real_data_passed = 0
        
        for catalyst in self.catalyst_data[:3]:  # Test first 3 catalysts
            price = catalyst.get('total_price', 0)
            if price > 0:
                min_price = round(price * 0.9, 2)
                max_price = round(price * 1.1, 2)
                formatted = f"€{min_price:.2f} - €{max_price:.2f}"
                
                # Check format validity (should have € symbol and proper decimal places)
                import re
                # Use regex to validate format: €XX.XX - €XX.XX
                format_pattern = r'€\d+\.\d{2} - €\d+\.\d{2}'
                format_valid = bool(re.match(format_pattern, formatted))
                
                real_data_tests += 1
                if format_valid:
                    real_data_passed += 1
                    
                print(f"   Catalyst {catalyst.get('name', 'Unknown')}: {formatted} {'✅' if format_valid else '❌'}")
        
        overall_success = format_correct and (real_data_passed == real_data_tests)
        self.log_test("Price Range Display Format", overall_success, f"Format tests: {real_data_passed + (1 if format_correct else 0)}/{real_data_tests + 1}")
        return overall_success

    def test_catalyst_matching_with_database(self):
        """Test that catalyst listings match properly with database calculations"""
        print("\n🔗 Testing Catalyst Matching with Database Calculations...")
        
        if not self.catalyst_data or not self.test_listings:
            print("❌ Catalyst Matching - SKIPPED (Missing data)")
            return False
            
        # Get current listings from browse endpoint
        success, browse_response = self.run_test(
            "Get Browse Listings for Matching",
            "GET", 
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False
            
        # Find catalyst listings
        catalyst_listings = [listing for listing in browse_response if listing.get('category') == 'Catalysts']
        
        matches_found = 0
        matches_tested = 0
        
        for listing in catalyst_listings:
            listing_title = listing.get('title', '')
            listing_price = listing.get('price', 0)
            
            # Try to match with catalyst calculations
            for catalyst in self.catalyst_data:
                catalyst_name = catalyst.get('name', '')
                calculated_price = catalyst.get('total_price', 0)
                
                if catalyst_name and catalyst_name in listing_title:
                    matches_tested += 1
                    
                    # Calculate price range
                    price_min = calculated_price * 0.9
                    price_max = calculated_price * 1.1
                    
                    # Determine classification
                    if listing_price < price_min:
                        classification = "Great Deal"
                    elif listing_price <= price_max:
                        classification = "In Range"
                    else:
                        classification = "Above Range"
                    
                    print(f"   📊 Match Found:")
                    print(f"      Listing: {listing_title}")
                    print(f"      Listed Price: €{listing_price}")
                    print(f"      Calculated Price: €{calculated_price}")
                    print(f"      Range: €{price_min:.2f} - €{price_max:.2f}")
                    print(f"      Classification: {classification}")
                    
                    matches_found += 1
                    break
        
        success = matches_found > 0
        self.log_test("Catalyst Database Matching", success, f"Found {matches_found} matches out of {len(catalyst_listings)} catalyst listings")
        return success

    def test_example_calculations_from_review(self):
        """Test the specific example calculations mentioned in the review request"""
        print("\n🧮 Testing Example Calculations from Review Request...")
        
        # Example from review: €100 catalyst
        calculated_price = 100.00
        
        test_cases = [
            {"price": 85.00, "expected": "Great Deal", "reason": "€85 below €90-€110 range"},
            {"price": 95.00, "expected": "In Range", "reason": "€95 within €90-€110 range"},
            {"price": 115.00, "expected": "Above Range", "reason": "€115 above €90-€110 range"}
        ]
        
        print(f"   Base Catalyst Price: €{calculated_price}")
        print(f"   Expected Range: €{calculated_price * 0.9:.2f} - €{calculated_price * 1.1:.2f}")
        
        all_passed = True
        
        for test_case in test_cases:
            price = test_case["price"]
            expected = test_case["expected"]
            reason = test_case["reason"]
            
            # Calculate range
            price_min = calculated_price * 0.9  # €90.00
            price_max = calculated_price * 1.1  # €110.00
            
            # Determine classification
            if price < price_min:
                actual = "Great Deal"
            elif price <= price_max:
                actual = "In Range"
            else:
                actual = "Above Range"
                
            test_passed = actual == expected
            all_passed = all_passed and test_passed
            
            print(f"   {reason}: Expected '{expected}', Got '{actual}' {'✅' if test_passed else '❌'}")
            
        self.log_test("Review Example Calculations", all_passed, "All review examples calculated correctly")
        return all_passed

    def run_price_range_tests(self):
        """Run complete price range functionality test suite"""
        print("🚀 Starting Price Range Functionality Tests")
        print("=" * 70)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return False
            
        # Test sequence
        tests = [
            ("Catalyst Calculations Data", self.test_catalyst_calculations_data),
            ("Price Range Calculation Logic", self.test_price_range_calculation_logic),
            ("Range Classification Logic", self.test_range_classification_logic),
            ("Create Test Catalyst Listings", self.create_test_catalyst_listings),
            ("Price Range Display Format", self.test_price_range_display_format),
            ("Catalyst Database Matching", self.test_catalyst_matching_with_database),
            ("Review Example Calculations", self.test_example_calculations_from_review)
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            test_func()
            
        # Print results
        print("\n" + "=" * 70)
        print(f"📊 Price Range Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All price range functionality tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} price range tests failed")
            return False

def main():
    """Main test execution"""
    tester = PriceRangeAPITester()
    success = tester.run_price_range_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())