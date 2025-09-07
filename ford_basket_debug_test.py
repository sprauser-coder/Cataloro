#!/usr/bin/env python3
"""
Ford Listing Basket Calculation Debug Test
Debug why basket calculations are not showing correctly after Ford listing update
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://catalyst-calc.preview.emergentagent.com/api"

class FordBasketDebugTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.demo_user_id = None
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def get_demo_user_id(self):
        """Get demo user ID for testing"""
        try:
            # Login as demo user
            demo_credentials = {
                "email": "demo@cataloro.com",
                "password": "demo123"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login", 
                json=demo_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                self.demo_user_id = user.get('id')
                self.log_test(
                    "Get Demo User ID", 
                    True, 
                    f"Demo user ID: {self.demo_user_id}"
                )
                return self.demo_user_id
            else:
                self.log_test("Get Demo User ID", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Demo User ID", False, error_msg=str(e))
            return None

    def test_ford_listing_catalyst_fields(self):
        """1. Verify Ford Listing Update - GET the Ford listing directly to confirm catalyst fields are saved"""
        try:
            # Get all listings to find Ford listing
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                ford_listing = None
                
                # Look for Ford listing
                for listing in listings:
                    title = listing.get('title', '').lower()
                    if 'ford' in title or 'f150' in title or 'f-150' in title:
                        ford_listing = listing
                        break
                
                if ford_listing:
                    # Check catalyst fields
                    ceramic_weight = ford_listing.get('ceramic_weight')
                    pt_ppm = ford_listing.get('pt_ppm')
                    pd_ppm = ford_listing.get('pd_ppm')
                    rh_ppm = ford_listing.get('rh_ppm')
                    
                    # Expected values from review request
                    expected_ceramic_weight = 1.3686
                    expected_pt_ppm = 0.9398
                    expected_pd_ppm = 0.0000
                    expected_rh_ppm = 0.0000
                    
                    catalyst_fields_present = all([
                        ceramic_weight is not None,
                        pt_ppm is not None,
                        pd_ppm is not None,
                        rh_ppm is not None
                    ])
                    
                    values_match_expected = (
                        abs(float(ceramic_weight or 0) - expected_ceramic_weight) < 0.001 and
                        abs(float(pt_ppm or 0) - expected_pt_ppm) < 0.001 and
                        abs(float(pd_ppm or 0) - expected_pd_ppm) < 0.001 and
                        abs(float(rh_ppm or 0) - expected_rh_ppm) < 0.001
                    )
                    
                    self.log_test(
                        "Ford Listing Catalyst Fields Verification", 
                        catalyst_fields_present and values_match_expected, 
                        f"Ford listing '{ford_listing.get('title')}' - Ceramic Weight: {ceramic_weight}, PT PPM: {pt_ppm}, PD PPM: {pd_ppm}, RH PPM: {rh_ppm}. Expected: {expected_ceramic_weight}, {expected_pt_ppm}, {expected_pd_ppm}, {expected_rh_ppm}. Fields Present: {catalyst_fields_present}, Values Match: {values_match_expected}",
                        "" if catalyst_fields_present and values_match_expected else "Catalyst fields missing or values don't match expected"
                    )
                    return ford_listing
                else:
                    self.log_test("Ford Listing Catalyst Fields Verification", False, error_msg="Ford listing not found in browse results")
                    return None
            else:
                self.log_test("Ford Listing Catalyst Fields Verification", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Ford Listing Catalyst Fields Verification", False, error_msg=str(e))
            return None

    def test_basket_api_response(self):
        """2. Test Basket API Response - GET /api/user/baskets/{user_id} for demo user"""
        if not self.demo_user_id:
            self.log_test("Basket API Response Test", False, error_msg="Demo user ID not available")
            return None
            
        try:
            response = requests.get(f"{BACKEND_URL}/user/baskets/{self.demo_user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                # Look for picki basket or any basket with Ford item
                ford_basket = None
                ford_item = None
                
                for basket in baskets:
                    basket_name = basket.get('name', '').lower()
                    items = basket.get('items', [])
                    
                    # Check if this is picki basket or has Ford item
                    if 'picki' in basket_name:
                        ford_basket = basket
                        # Look for Ford item in this basket
                        for item in items:
                            item_title = item.get('title', '').lower()
                            if 'ford' in item_title or 'f150' in item_title or 'f-150' in item_title:
                                ford_item = item
                                break
                        break
                    else:
                        # Check all baskets for Ford items
                        for item in items:
                            item_title = item.get('title', '').lower()
                            if 'ford' in item_title or 'f150' in item_title or 'f-150' in item_title:
                                ford_basket = basket
                                ford_item = item
                                break
                        if ford_item:
                            break
                
                if ford_basket and ford_item:
                    # Check if Ford item has updated catalyst fields
                    weight = ford_item.get('weight')
                    pt_ppm = ford_item.get('pt_ppm')
                    pd_ppm = ford_item.get('pd_ppm')
                    rh_ppm = ford_item.get('rh_ppm')
                    
                    # Check renumeration values
                    renumeration_pt = ford_item.get('renumeration_pt')
                    renumeration_pd = ford_item.get('renumeration_pd')
                    renumeration_rh = ford_item.get('renumeration_rh')
                    
                    self.log_test(
                        "Basket API Response Test", 
                        True, 
                        f"Found Ford item in basket '{ford_basket.get('name')}'. Item: '{ford_item.get('title')}' - Weight: {weight}, PT PPM: {pt_ppm}, PD PPM: {pd_ppm}, RH PPM: {rh_ppm}, Renumeration PT: {renumeration_pt}, PD: {renumeration_pd}, RH: {renumeration_rh}"
                    )
                    return ford_basket, ford_item
                else:
                    self.log_test(
                        "Basket API Response Test", 
                        False, 
                        f"Found {len(baskets)} baskets but no Ford item found",
                        "Ford item not found in any basket"
                    )
                    return baskets, None
            else:
                self.log_test("Basket API Response Test", False, f"HTTP {response.status_code}")
                return None, None
        except Exception as e:
            self.log_test("Basket API Response Test", False, error_msg=str(e))
            return None, None

    def test_assignment_data_debug(self, ford_listing):
        """3. Debug Assignment Data - Check if assignment is still active and using correct listing data"""
        if not ford_listing:
            self.log_test("Assignment Data Debug", False, error_msg="Ford listing not available")
            return False
            
        try:
            listing_id = ford_listing.get('id')
            
            # Check if there are any assignments for this listing
            # Since we don't have a direct assignment endpoint, we'll check through baskets
            if self.demo_user_id:
                response = requests.get(f"{BACKEND_URL}/user/baskets/{self.demo_user_id}", timeout=10)
                
                if response.status_code == 200:
                    baskets = response.json()
                    assignment_found = False
                    
                    for basket in baskets:
                        items = basket.get('items', [])
                        for item in items:
                            if item.get('listing_id') == listing_id:
                                assignment_found = True
                                
                                # Check if assignment is using updated listing data
                                listing_weight = ford_listing.get('ceramic_weight')
                                listing_pt = ford_listing.get('pt_ppm')
                                listing_pd = ford_listing.get('pd_ppm')
                                listing_rh = ford_listing.get('rh_ppm')
                                
                                item_weight = item.get('weight')
                                item_pt = item.get('pt_ppm')
                                item_pd = item.get('pd_ppm')
                                item_rh = item.get('rh_ppm')
                                
                                data_matches = (
                                    listing_weight == item_weight and
                                    listing_pt == item_pt and
                                    listing_pd == item_pd and
                                    listing_rh == item_rh
                                )
                                
                                self.log_test(
                                    "Assignment Data Debug", 
                                    data_matches, 
                                    f"Assignment found for Ford listing. Listing data: W={listing_weight}, PT={listing_pt}, PD={listing_pd}, RH={listing_rh}. Item data: W={item_weight}, PT={item_pt}, PD={item_pd}, RH={item_rh}. Data matches: {data_matches}",
                                    "" if data_matches else "Assignment data doesn't match updated listing data"
                                )
                                return data_matches
                    
                    if not assignment_found:
                        self.log_test("Assignment Data Debug", False, error_msg="No assignment found for Ford listing")
                        return False
                else:
                    self.log_test("Assignment Data Debug", False, f"HTTP {response.status_code}")
                    return False
            else:
                self.log_test("Assignment Data Debug", False, error_msg="Demo user ID not available")
                return False
        except Exception as e:
            self.log_test("Assignment Data Debug", False, error_msg=str(e))
            return False

    def test_complete_calculation_flow(self, ford_item):
        """4. Test Complete Flow - Get current basket data and check exact calculation values"""
        if not ford_item:
            self.log_test("Complete Calculation Flow Test", False, error_msg="Ford item not available")
            return False
            
        try:
            # Get calculation values from Ford item
            weight = float(ford_item.get('weight', 0))
            pt_ppm = float(ford_item.get('pt_ppm', 0))
            pd_ppm = float(ford_item.get('pd_ppm', 0))
            rh_ppm = float(ford_item.get('rh_ppm', 0))
            
            renumeration_pt = float(ford_item.get('renumeration_pt', 0))
            renumeration_pd = float(ford_item.get('renumeration_pd', 0))
            renumeration_rh = float(ford_item.get('renumeration_rh', 0))
            
            # Calculate expected values using formula: weight × ppm ÷ 1000 × renumeration
            expected_pt_value = (weight * pt_ppm / 1000) * renumeration_pt
            expected_pd_value = (weight * pd_ppm / 1000) * renumeration_pd
            expected_rh_value = (weight * rh_ppm / 1000) * renumeration_rh
            
            total_expected_value = expected_pt_value + expected_pd_value + expected_rh_value
            
            # Check if the expected values match the review request expectations
            # Expected catalyst values: 1.3686, 0.9398, 0.0000
            expected_weight = 1.3686
            expected_pt = 0.9398
            expected_pd = 0.0000
            expected_rh = 0.0000
            
            values_correct = (
                abs(weight - expected_weight) < 0.001 and
                abs(pt_ppm - expected_pt) < 0.001 and
                abs(pd_ppm - expected_pd) < 0.001 and
                abs(rh_ppm - expected_rh) < 0.001
            )
            
            self.log_test(
                "Complete Calculation Flow Test", 
                values_correct, 
                f"Ford item calculation: Weight={weight}, PT PPM={pt_ppm}, PD PPM={pd_ppm}, RH PPM={rh_ppm}. Renumeration: PT={renumeration_pt}, PD={renumeration_pd}, RH={renumeration_rh}. Calculated values: PT={expected_pt_value:.4f}, PD={expected_pd_value:.4f}, RH={expected_rh_value:.4f}, Total={total_expected_value:.4f}. Values match expected: {values_correct}",
                "" if values_correct else f"Values don't match expected: Weight={expected_weight}, PT={expected_pt}, PD={expected_pd}, RH={expected_rh}"
            )
            return values_correct
        except Exception as e:
            self.log_test("Complete Calculation Flow Test", False, error_msg=str(e))
            return False

    def test_get_specific_ford_listing_by_id(self):
        """Get specific Ford listing by searching for known Ford identifiers"""
        try:
            # Get all listings
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                # Look for Ford listings with various identifiers
                ford_identifiers = ['ford', 'f150', 'f-150', 'catalyst converter ford', 'trpsak']
                
                ford_listings = []
                for listing in listings:
                    title = listing.get('title', '').lower()
                    description = listing.get('description', '').lower()
                    
                    for identifier in ford_identifiers:
                        if identifier in title or identifier in description:
                            ford_listings.append(listing)
                            break
                
                if ford_listings:
                    self.log_test(
                        "Get Specific Ford Listing", 
                        True, 
                        f"Found {len(ford_listings)} Ford listings: {[listing.get('title') for listing in ford_listings]}"
                    )
                    
                    # Return the first Ford listing with catalyst fields
                    for listing in ford_listings:
                        if listing.get('ceramic_weight') is not None:
                            return listing
                    
                    # If no listing has catalyst fields, return the first one
                    return ford_listings[0]
                else:
                    self.log_test("Get Specific Ford Listing", False, error_msg="No Ford listings found")
                    return None
            else:
                self.log_test("Get Specific Ford Listing", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Specific Ford Listing", False, error_msg=str(e))
            return None

    def run_ford_basket_debug_testing(self):
        """Run Ford Basket Debug testing as requested in review"""
        print("=" * 80)
        print("FORD LISTING BASKET CALCULATION DEBUG TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # Get demo user ID
        print("👤 GET DEMO USER ID")
        print("-" * 40)
        if not self.get_demo_user_id():
            print("❌ Failed to get demo user ID. Aborting tests.")
            return
        
        # 1. Verify Ford Listing Update
        print("🚗 1. VERIFY FORD LISTING UPDATE")
        print("-" * 40)
        ford_listing = self.test_ford_listing_catalyst_fields()
        
        if not ford_listing:
            # Try alternative method to find Ford listing
            print("🔍 SEARCHING FOR FORD LISTING BY ID")
            print("-" * 40)
            ford_listing = self.test_get_specific_ford_listing_by_id()
        
        # 2. Test Basket API Response
        print("🧺 2. TEST BASKET API RESPONSE")
        print("-" * 40)
        ford_basket, ford_item = self.test_basket_api_response()
        
        # 3. Debug Assignment Data
        print("🔗 3. DEBUG ASSIGNMENT DATA")
        print("-" * 40)
        assignment_correct = self.test_assignment_data_debug(ford_listing)
        
        # 4. Test Complete Flow
        print("🧮 4. TEST COMPLETE CALCULATION FLOW")
        print("-" * 40)
        calculation_correct = self.test_complete_calculation_flow(ford_item)
        
        # Print Summary
        print("=" * 80)
        print("FORD BASKET DEBUG TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 FORD BASKET DEBUG TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Ford listing should have catalyst fields: ceramic_weight=1.3686, pt_ppm=0.9398, pd_ppm=0.0000, rh_ppm=0.0000")
        print("  ✅ Ford item in picki basket should have updated catalyst fields")
        print("  ✅ Assignment should be using correct listing data")
        print("  ✅ Basket calculation should use formula: weight × ppm ÷ 1000 × renumeration")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = FordBasketDebugTester()
    
    # Run Ford Basket Debug testing as requested in the review
    print("🎯 RUNNING FORD LISTING BASKET CALCULATION DEBUG TESTING")
    print("Debugging why basket calculations are not showing correctly after Ford listing update...")
    print()
    
    passed, failed, results = tester.run_ford_basket_debug_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)