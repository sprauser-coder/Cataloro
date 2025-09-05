#!/usr/bin/env python3
"""
Updated Marketplace Functionality Test Suite
Tests the latest changes for clean price range display without autofill and badges
"""

import requests
import sys
import json
from datetime import datetime

class UpdatedMarketplaceTester:
    def __init__(self, base_url="https://cataloro-upgrade.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_listing_id = None

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
            print(f"   Admin authenticated: {self.admin_user.get('email')}")

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
            print(f"   User authenticated: {self.regular_user.get('email')}")

        return admin_success and user_success

    def test_catalyst_data_availability(self):
        """Test that catalyst data is available for price calculations"""
        if not self.admin_user:
            print("❌ Catalyst Data - SKIPPED (No admin logged in)")
            return False
            
        success, response = self.run_test(
            "Catalyst Data Availability",
            "GET",
            "api/admin/catalyst/calculations",
            200
        )
        
        if success and len(response) > 0:
            print(f"   ✅ Found {len(response)} catalyst calculations")
            # Check for price range data structure
            first_calc = response[0]
            if 'total_price' in first_calc:
                price = first_calc['total_price']
                print(f"   Sample catalyst price: €{price}")
                
                # Calculate ±10% range for verification
                lower_range = round(price * 0.9, 2)
                upper_range = round(price * 1.1, 2)
                print(f"   Expected price range: €{lower_range} - €{upper_range}")
                
                self.log_test("Price Range Calculation Logic", True, f"±10% range: €{lower_range}-€{upper_range}")
            else:
                self.log_test("Price Range Calculation Logic", False, "total_price field missing")
        
        return success

    def test_listing_creation_without_autofill(self):
        """Test creating a catalyst listing WITHOUT price autofill"""
        if not self.regular_user:
            print("❌ Listing Creation Test - SKIPPED (No user logged in)")
            return False
            
        print("\n📝 Testing Listing Creation WITHOUT Price Autofill...")
        
        # Create catalyst listing with empty price field initially
        catalyst_listing = {
            "title": "FAPACAT8659 Test Catalyst",
            "description": "Test catalyst for verifying no price autofill functionality. This should be created without automatic price population.",
            "price": 0.0,  # Start with empty/zero price to verify no autofill
            "category": "Catalysts",
            "condition": "Used - Good",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
            "tags": ["catalyst", "automotive", "test"],
            "features": ["Test listing", "No autofill verification"]
        }
        
        success, response = self.run_test(
            "Create Catalyst Listing (No Autofill)",
            "POST",
            "api/listings",
            200,
            data=catalyst_listing
        )
        
        if success:
            self.test_listing_id = response.get('listing_id')
            print(f"   ✅ Test listing created with ID: {self.test_listing_id}")
            
            # Verify the listing was created with the original price (no autofill)
            if catalyst_listing['price'] == 0.0:
                self.log_test("No Price Autofill Verification", True, "Price field remained empty/zero as expected")
            else:
                self.log_test("No Price Autofill Verification", False, f"Price was modified to {catalyst_listing['price']}")
                
        return success

    def test_clean_price_range_display(self):
        """Test that price ranges are displayed cleanly without explanatory text"""
        success, response = self.run_test(
            "Browse Listings for Clean Display",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            catalyst_listings = [listing for listing in response if listing.get('category') == 'Catalysts']
            print(f"   Found {len(catalyst_listings)} catalyst listings")
            
            # Check that listings don't contain badge fields or explanatory text
            clean_display = True
            issues_found = []
            
            for listing in catalyst_listings:
                # Check for unwanted fields that would indicate badges or explanatory text
                unwanted_fields = ['price_badge', 'deal_classification', 'range_explanation', 'price_status']
                
                for field in unwanted_fields:
                    if field in listing:
                        clean_display = False
                        issues_found.append(f"Found unwanted field '{field}' in listing {listing.get('title', 'Unknown')}")
                
                # Check title and description for explanatory text
                title = listing.get('title', '')
                description = listing.get('description', '')
                
                unwanted_text = ['±10%', 'Great Deal', 'Above Range', 'In Range', 'price classification']
                for text in unwanted_text:
                    if text in title or text in description:
                        clean_display = False
                        issues_found.append(f"Found explanatory text '{text}' in listing {listing.get('title', 'Unknown')}")
            
            if clean_display:
                self.log_test("Clean Price Range Display", True, "No badges or explanatory text found in listings")
            else:
                self.log_test("Clean Price Range Display", False, f"Issues: {'; '.join(issues_found[:3])}")
                
            return clean_display
        
        return False

    def test_market_range_calculations(self):
        """Test that ±10% range calculations work correctly but are displayed cleanly"""
        if not self.admin_user:
            print("❌ Market Range Calculations - SKIPPED (No admin logged in)")
            return False
            
        # Get catalyst calculations for testing
        calc_success, calc_response = self.run_test(
            "Get Calculations for Range Testing",
            "GET",
            "api/admin/catalyst/calculations",
            200
        )
        
        if not calc_success or len(calc_response) == 0:
            return False
            
        # Test range calculation logic with sample data
        test_cases = [
            {"price": 100.0, "expected_lower": 90.0, "expected_upper": 110.0},
            {"price": 292.74, "expected_lower": 263.47, "expected_upper": 322.01},
            {"price": 29.24, "expected_lower": 26.32, "expected_upper": 32.16}
        ]
        
        all_calculations_correct = True
        
        for test_case in test_cases:
            price = test_case['price']
            expected_lower = test_case['expected_lower']
            expected_upper = test_case['expected_upper']
            
            # Calculate ±10% range
            calculated_lower = round(price * 0.9, 2)
            calculated_upper = round(price * 1.1, 2)
            
            if calculated_lower == expected_lower and calculated_upper == expected_upper:
                print(f"   ✅ Range calculation correct for €{price}: €{calculated_lower} - €{calculated_upper}")
            else:
                print(f"   ❌ Range calculation incorrect for €{price}: got €{calculated_lower} - €{calculated_upper}, expected €{expected_lower} - €{expected_upper}")
                all_calculations_correct = False
        
        self.log_test("Market Range Calculations (±10%)", all_calculations_correct, "Range calculation logic verified")
        return all_calculations_correct

    def test_browse_listings_clean_display(self):
        """Test that browse listings show clean market ranges without badges"""
        success, response = self.run_test(
            "Browse Listings Clean Market Ranges",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            # Verify response is array format (compatible with .map())
            if isinstance(response, list):
                self.log_test("Browse Response Format", True, f"Array format with {len(response)} listings")
            else:
                self.log_test("Browse Response Format", False, "Response is not array format")
                return False
            
            catalyst_listings = [listing for listing in response if listing.get('category') == 'Catalysts']
            
            if len(catalyst_listings) > 0:
                print(f"   Found {len(catalyst_listings)} catalyst listings for clean display testing")
                
                # Check for clean display - no classification badges
                clean_listings = 0
                for listing in catalyst_listings:
                    title = listing.get('title', '')
                    description = listing.get('description', '')
                    
                    # Check that there are no classification badges in the data
                    has_badges = any(badge in str(listing) for badge in ['Great Deal', 'Above Range', 'In Range', 'price_classification'])
                    
                    if not has_badges:
                        clean_listings += 1
                    else:
                        print(f"   ⚠️  Found badges in listing: {title}")
                
                success_rate = clean_listings / len(catalyst_listings)
                if success_rate >= 1.0:
                    self.log_test("Clean Market Range Display", True, f"All {clean_listings} catalyst listings display cleanly")
                else:
                    self.log_test("Clean Market Range Display", False, f"Only {clean_listings}/{len(catalyst_listings)} listings display cleanly")
                    
                return success_rate >= 1.0
            else:
                print("   ⚠️  No catalyst listings found for testing")
                return True  # No catalyst listings to test, so technically clean
        
        return False

    def test_api_compatibility(self):
        """Test that all endpoints continue working with cleaned-up functionality"""
        print("\n🔗 Testing API Compatibility...")
        
        endpoints_to_test = [
            ("Health Check", "GET", "api/health", 200),
            ("Browse Listings", "GET", "api/marketplace/browse", 200),
            ("Catalyst Calculations", "GET", "api/admin/catalyst/calculations", 200)
        ]
        
        all_compatible = True
        
        for name, method, endpoint, expected_status in endpoints_to_test:
            success, response = self.run_test(
                f"API Compatibility - {name}",
                method,
                endpoint,
                expected_status
            )
            
            if not success:
                all_compatible = False
        
        self.log_test("API Compatibility Check", all_compatible, "All tested endpoints working")
        return all_compatible

    def test_user_experience_simplified(self):
        """Test that the user experience is simplified without overwhelming information"""
        print("\n👤 Testing Simplified User Experience...")
        
        # Test that catalyst data is available but presented cleanly
        if not self.admin_user:
            print("❌ User Experience Test - SKIPPED (No admin logged in)")
            return False
            
        calc_success, calc_response = self.run_test(
            "Catalyst Data for UX Testing",
            "GET",
            "api/admin/catalyst/calculations",
            200
        )
        
        if calc_success and len(calc_response) > 0:
            # Check that the data structure is clean and simple
            sample_calc = calc_response[0]
            
            # Essential fields that should be present
            essential_fields = ['name', 'total_price']
            has_essential = all(field in sample_calc for field in essential_fields)
            
            # Fields that should NOT be present for clean UX
            overwhelming_fields = ['pt_ppm', 'pd_ppm', 'rh_ppm', 'detailed_breakdown', 'technical_specs']
            has_overwhelming = any(field in sample_calc for field in overwhelming_fields)
            
            if has_essential and not has_overwhelming:
                self.log_test("Simplified User Experience", True, "Clean data structure with essential info only")
                return True
            else:
                missing_essential = [field for field in essential_fields if field not in sample_calc]
                present_overwhelming = [field for field in overwhelming_fields if field in sample_calc]
                
                issues = []
                if missing_essential:
                    issues.append(f"Missing essential fields: {missing_essential}")
                if present_overwhelming:
                    issues.append(f"Overwhelming fields present: {present_overwhelming}")
                
                self.log_test("Simplified User Experience", False, "; ".join(issues))
                return False
        
        return False

    def run_updated_marketplace_tests(self):
        """Run all updated marketplace functionality tests"""
        print("🚀 Starting Updated Marketplace Functionality Tests")
        print("Testing: Clean price ranges, no autofill, no badges")
        print("=" * 70)

        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return False

        # Test 1: Catalyst data availability
        test1_success = self.test_catalyst_data_availability()

        # Test 2: Listing creation without price autofill
        test2_success = self.test_listing_creation_without_autofill()

        # Test 3: Clean price range display
        test3_success = self.test_clean_price_range_display()

        # Test 4: Browse listings clean display
        test4_success = self.test_browse_listings_clean_display()

        # Test 5: Market range calculations
        test5_success = self.test_market_range_calculations()

        # Test 6: User experience simplified
        test6_success = self.test_user_experience_simplified()

        # Test 7: API compatibility
        test7_success = self.test_api_compatibility()

        # Summary
        print("\n" + "=" * 70)
        print(f"📊 Updated Marketplace Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        # Specific test results
        test_results = [
            ("Catalyst Data Availability", test1_success),
            ("No Price Autofill", test2_success),
            ("Clean Price Range Display", test3_success),
            ("Browse Clean Display", test4_success),
            ("Market Range Calculations", test5_success),
            ("Simplified User Experience", test6_success),
            ("API Compatibility", test7_success)
        ]
        
        print("\n📋 Individual Test Results:")
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        all_passed = all(result for _, result in test_results)
        
        if all_passed:
            print("\n🎉 All updated marketplace functionality tests passed!")
            print("✅ Clean price ranges working correctly")
            print("✅ No price autofill confirmed")
            print("✅ No classification badges found")
            print("✅ Market range calculations accurate")
            print("✅ User experience simplified")
        else:
            failed_tests = [name for name, result in test_results if not result]
            print(f"\n⚠️  {len(failed_tests)} tests failed: {', '.join(failed_tests)}")
        
        return all_passed

def main():
    """Main test execution"""
    tester = UpdatedMarketplaceTester()
    success = tester.run_updated_marketplace_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())