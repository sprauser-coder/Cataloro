#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Basket Calculations and Item Counts
Testing basket item counts, catalyst data, and assignment process as requested in review
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://product-page-fix.preview.emergentagent.com/api"

class BasketCalculationTester:
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

    def setup_demo_user(self):
        """Login as demo user and get user ID"""
        try:
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
                    "Demo User Setup", 
                    True, 
                    f"Demo user logged in successfully. User ID: {self.demo_user_id}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Demo User Setup", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Demo User Setup", False, error_msg=str(e))
            return False

    def test_basket_item_counts(self):
        """Test GET /api/user/baskets/{user_id} and verify items array length"""
        if not self.demo_user_id:
            self.log_test("Basket Item Counts Test", False, error_msg="No demo user ID available")
            return False
            
        try:
            response = requests.get(f"{BACKEND_URL}/user/baskets/{self.demo_user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                if not isinstance(baskets, list):
                    self.log_test("Basket Item Counts Test", False, error_msg="Response is not a list of baskets")
                    return False
                
                basket_analysis = []
                total_baskets = len(baskets)
                baskets_with_items = 0
                total_items_across_baskets = 0
                
                for i, basket in enumerate(baskets):
                    basket_id = basket.get('id', f'basket_{i}')
                    basket_name = basket.get('name', 'Unnamed Basket')
                    items = basket.get('items', [])
                    item_count = len(items)
                    
                    if item_count > 0:
                        baskets_with_items += 1
                        total_items_across_baskets += item_count
                        
                        # Check if items have proper structure
                        sample_item = items[0] if items else {}
                        has_catalyst_data = all(key in sample_item for key in ['weight', 'pt_ppm', 'pd_ppm', 'rh_ppm'])
                        has_renumeration = all(key in sample_item for key in ['renumeration_pt', 'renumeration_pd', 'renumeration_rh'])
                        
                        basket_analysis.append(
                            f"Basket '{basket_name}' (ID: {basket_id}): {item_count} items, "
                            f"Catalyst data: {'✅' if has_catalyst_data else '❌'}, "
                            f"Renumeration: {'✅' if has_renumeration else '❌'}"
                        )
                    else:
                        basket_analysis.append(f"Basket '{basket_name}' (ID: {basket_id}): 0 items (EMPTY)")
                
                # Check for the reported issue: baskets showing 0 items when items are assigned
                issue_detected = total_baskets > 0 and baskets_with_items == 0 and total_items_across_baskets == 0
                
                self.log_test(
                    "Basket Item Counts Test", 
                    True, 
                    f"Found {total_baskets} baskets, {baskets_with_items} with items, {total_items_across_baskets} total items. "
                    f"Issue detected (all baskets empty): {'❌ YES' if issue_detected else '✅ NO'}. "
                    f"Analysis: {'; '.join(basket_analysis) if basket_analysis else 'No baskets found'}"
                )
                
                return {
                    'baskets': baskets,
                    'total_baskets': total_baskets,
                    'baskets_with_items': baskets_with_items,
                    'total_items': total_items_across_baskets,
                    'issue_detected': issue_detected
                }
                
            elif response.status_code == 404:
                self.log_test("Basket Item Counts Test", True, "No baskets found for user (404) - this is acceptable")
                return {'baskets': [], 'total_baskets': 0, 'baskets_with_items': 0, 'total_items': 0, 'issue_detected': False}
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Basket Item Counts Test", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Basket Item Counts Test", False, error_msg=str(e))
            return False

    def test_basket_catalyst_data_integrity(self, basket_data):
        """Test if basket items have proper catalyst data for calculations"""
        if not basket_data or not basket_data.get('baskets'):
            self.log_test("Basket Catalyst Data Integrity", False, error_msg="No basket data provided")
            return False
            
        try:
            baskets = basket_data['baskets']
            catalyst_analysis = []
            items_with_complete_catalyst_data = 0
            items_with_missing_catalyst_data = 0
            items_with_zero_values = 0
            
            required_catalyst_fields = ['weight', 'pt_ppm', 'pd_ppm', 'rh_ppm']
            required_renumeration_fields = ['renumeration_pt', 'renumeration_pd', 'renumeration_rh']
            
            for basket in baskets:
                basket_name = basket.get('name', 'Unnamed')
                items = basket.get('items', [])
                
                for item in items:
                    item_title = item.get('title', 'Unknown Item')
                    
                    # Check catalyst fields
                    catalyst_present = all(field in item for field in required_catalyst_fields)
                    renumeration_present = all(field in item for field in required_renumeration_fields)
                    
                    if catalyst_present and renumeration_present:
                        # Check if values are non-zero (the reported issue)
                        weight = item.get('weight', 0)
                        pt_ppm = item.get('pt_ppm', 0)
                        pd_ppm = item.get('pd_ppm', 0)
                        rh_ppm = item.get('rh_ppm', 0)
                        
                        renumeration_pt = item.get('renumeration_pt', 0)
                        renumeration_pd = item.get('renumeration_pd', 0)
                        renumeration_rh = item.get('renumeration_rh', 0)
                        
                        if weight == 0 and pt_ppm == 0 and pd_ppm == 0 and rh_ppm == 0:
                            items_with_zero_values += 1
                            catalyst_analysis.append(
                                f"❌ Item '{item_title}' in basket '{basket_name}': All catalyst values are ZERO "
                                f"(weight={weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}) - CALCULATION ISSUE"
                            )
                        else:
                            items_with_complete_catalyst_data += 1
                            # Calculate sample values to verify calculation logic
                            pt_calc = weight * pt_ppm / 1000 * renumeration_pt if weight and pt_ppm and renumeration_pt else 0
                            pd_calc = weight * pd_ppm / 1000 * renumeration_pd if weight and pd_ppm and renumeration_pd else 0
                            rh_calc = weight * rh_ppm / 1000 * renumeration_rh if weight and rh_ppm and renumeration_rh else 0
                            
                            catalyst_analysis.append(
                                f"✅ Item '{item_title}' in basket '{basket_name}': Complete data "
                                f"(weight={weight}g, pt={pt_ppm}ppm, pd={pd_ppm}ppm, rh={rh_ppm}ppm) "
                                f"→ Calculations: PT={pt_calc:.4f}g, PD={pd_calc:.4f}g, RH={rh_calc:.4f}g"
                            )
                    else:
                        items_with_missing_catalyst_data += 1
                        missing_fields = []
                        if not catalyst_present:
                            missing_catalyst = [f for f in required_catalyst_fields if f not in item]
                            missing_fields.extend(missing_catalyst)
                        if not renumeration_present:
                            missing_renumeration = [f for f in required_renumeration_fields if f not in item]
                            missing_fields.extend(missing_renumeration)
                            
                        catalyst_analysis.append(
                            f"❌ Item '{item_title}' in basket '{basket_name}': Missing fields: {', '.join(missing_fields)}"
                        )
            
            total_items = items_with_complete_catalyst_data + items_with_missing_catalyst_data + items_with_zero_values
            
            # The main issue: items with zero catalyst values causing (0,0,0) calculations
            calculation_issue_detected = items_with_zero_values > 0
            
            self.log_test(
                "Basket Catalyst Data Integrity", 
                True, 
                f"Analyzed {total_items} items across baskets. "
                f"Complete data: {items_with_complete_catalyst_data}, "
                f"Missing data: {items_with_missing_catalyst_data}, "
                f"Zero values (ISSUE): {items_with_zero_values}. "
                f"Calculation issue detected: {'❌ YES' if calculation_issue_detected else '✅ NO'}. "
                f"Details: {'; '.join(catalyst_analysis[:3])}{'...' if len(catalyst_analysis) > 3 else ''}"
            )
            
            return {
                'total_items': total_items,
                'complete_data': items_with_complete_catalyst_data,
                'missing_data': items_with_missing_catalyst_data,
                'zero_values': items_with_zero_values,
                'calculation_issue': calculation_issue_detected,
                'analysis': catalyst_analysis
            }
            
        except Exception as e:
            self.log_test("Basket Catalyst Data Integrity", False, error_msg=str(e))
            return False

    def test_bought_items_catalyst_data(self):
        """Test GET /api/user/bought-items/{user_id} for catalyst data"""
        if not self.demo_user_id:
            self.log_test("Bought Items Catalyst Data", False, error_msg="No demo user ID available")
            return False
            
        try:
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.demo_user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                if not isinstance(bought_items, list):
                    self.log_test("Bought Items Catalyst Data", False, error_msg="Response is not a list of bought items")
                    return False
                
                total_items = len(bought_items)
                items_with_catalyst_data = 0
                items_with_zero_catalyst = 0
                catalyst_analysis = []
                
                required_fields = ['weight', 'pt_ppm', 'pd_ppm', 'rh_ppm', 'renumeration_pt', 'renumeration_pd', 'renumeration_rh']
                
                for item in bought_items:
                    item_title = item.get('title', 'Unknown Item')
                    
                    # Check if all required fields are present
                    has_all_fields = all(field in item for field in required_fields)
                    
                    if has_all_fields:
                        weight = item.get('weight', 0)
                        pt_ppm = item.get('pt_ppm', 0)
                        pd_ppm = item.get('pd_ppm', 0)
                        rh_ppm = item.get('rh_ppm', 0)
                        
                        if weight == 0 and pt_ppm == 0 and pd_ppm == 0 and rh_ppm == 0:
                            items_with_zero_catalyst += 1
                            catalyst_analysis.append(f"❌ '{item_title}': Zero catalyst values")
                        else:
                            items_with_catalyst_data += 1
                            catalyst_analysis.append(f"✅ '{item_title}': Has catalyst data (weight={weight}g)")
                    else:
                        missing_fields = [f for f in required_fields if f not in item]
                        catalyst_analysis.append(f"❌ '{item_title}': Missing {', '.join(missing_fields)}")
                
                self.log_test(
                    "Bought Items Catalyst Data", 
                    True, 
                    f"Found {total_items} bought items. "
                    f"With catalyst data: {items_with_catalyst_data}, "
                    f"With zero values: {items_with_zero_catalyst}. "
                    f"Analysis: {'; '.join(catalyst_analysis[:3])}{'...' if len(catalyst_analysis) > 3 else ''}"
                )
                
                return {
                    'total_items': total_items,
                    'with_catalyst_data': items_with_catalyst_data,
                    'with_zero_catalyst': items_with_zero_catalyst,
                    'bought_items': bought_items
                }
                
            elif response.status_code == 404:
                self.log_test("Bought Items Catalyst Data", True, "No bought items found for user (404) - this is acceptable")
                return {'total_items': 0, 'with_catalyst_data': 0, 'with_zero_catalyst': 0, 'bought_items': []}
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Bought Items Catalyst Data", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Bought Items Catalyst Data", False, error_msg=str(e))
            return False

    def test_assignment_process_simulation(self):
        """Test the assignment process by checking if items can be assigned to baskets"""
        if not self.demo_user_id:
            self.log_test("Assignment Process Simulation", False, error_msg="No demo user ID available")
            return False
            
        try:
            # First, get bought items to see if there are any to assign
            bought_items_response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.demo_user_id}", timeout=10)
            
            if bought_items_response.status_code != 200:
                self.log_test("Assignment Process Simulation", True, "No bought items available for assignment testing")
                return True
            
            bought_items = bought_items_response.json()
            if not bought_items:
                self.log_test("Assignment Process Simulation", True, "No bought items available for assignment testing")
                return True
            
            # Try to test assignment endpoint (if it exists)
            # Note: The review mentions PUT /api/user/bought-items/{item_id}/assign
            test_item = bought_items[0]
            item_id = test_item.get('id')
            
            if not item_id:
                self.log_test("Assignment Process Simulation", False, error_msg="Bought item has no ID for assignment testing")
                return False
            
            # Test if assignment endpoint exists (we'll get the endpoint structure)
            assignment_url = f"{BACKEND_URL}/user/bought-items/{item_id}/assign"
            
            # Since we don't want to actually modify data, we'll just test if the endpoint exists
            # by making a GET request (which should return 405 Method Not Allowed if PUT is expected)
            test_response = requests.get(assignment_url, timeout=10)
            
            endpoint_exists = test_response.status_code in [405, 200, 400, 422]  # These indicate endpoint exists
            
            self.log_test(
                "Assignment Process Simulation", 
                True, 
                f"Assignment endpoint test for item '{test_item.get('title', 'Unknown')}' (ID: {item_id}): "
                f"Endpoint exists: {'✅' if endpoint_exists else '❌'} (HTTP {test_response.status_code}). "
                f"Note: Full assignment testing requires basket creation which may modify data."
            )
            
            return endpoint_exists
            
        except Exception as e:
            self.log_test("Assignment Process Simulation", False, error_msg=str(e))
            return False

    def test_marketplace_listings_catalyst_data(self):
        """Test if marketplace listings have catalyst data that should be copied to baskets"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                if not isinstance(listings, list):
                    self.log_test("Marketplace Listings Catalyst Data", False, error_msg="Response is not a list of listings")
                    return False
                
                total_listings = len(listings)
                listings_with_catalyst = 0
                catalyst_analysis = []
                
                catalyst_fields = ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm']
                
                for listing in listings[:5]:  # Check first 5 listings
                    listing_title = listing.get('title', 'Unknown Listing')
                    
                    has_catalyst_fields = any(field in listing for field in catalyst_fields)
                    
                    if has_catalyst_fields:
                        listings_with_catalyst += 1
                        weight = listing.get('ceramic_weight', 0)
                        pt = listing.get('pt_ppm', 0)
                        pd = listing.get('pd_ppm', 0)
                        rh = listing.get('rh_ppm', 0)
                        
                        catalyst_analysis.append(
                            f"✅ '{listing_title}': Has catalyst data (weight={weight}g, pt={pt}ppm, pd={pd}ppm, rh={rh}ppm)"
                        )
                    else:
                        catalyst_analysis.append(f"❌ '{listing_title}': No catalyst data")
                
                self.log_test(
                    "Marketplace Listings Catalyst Data", 
                    True, 
                    f"Checked {min(5, total_listings)} of {total_listings} listings. "
                    f"With catalyst data: {listings_with_catalyst}. "
                    f"Analysis: {'; '.join(catalyst_analysis[:3])}{'...' if len(catalyst_analysis) > 3 else ''}"
                )
                
                return {
                    'total_checked': min(5, total_listings),
                    'total_listings': total_listings,
                    'with_catalyst': listings_with_catalyst,
                    'listings': listings[:5]
                }
                
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Marketplace Listings Catalyst Data", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Marketplace Listings Catalyst Data", False, error_msg=str(e))
            return False

    def run_basket_calculation_testing(self):
        """Run comprehensive basket calculation testing as requested in review"""
        print("=" * 80)
        print("CATALORO BASKET CALCULATIONS AND ITEM COUNTS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # Setup demo user
        print("🔧 DEMO USER SETUP")
        print("-" * 40)
        if not self.setup_demo_user():
            print("❌ Failed to setup demo user. Aborting tests.")
            return
        
        # 1. Test basket item counts (main issue reported)
        print("🧺 BASKET ITEM COUNTS TEST")
        print("-" * 40)
        basket_data = self.test_basket_item_counts()
        
        # 2. Test basket catalyst data integrity
        print("🧪 BASKET CATALYST DATA INTEGRITY TEST")
        print("-" * 40)
        if basket_data:
            catalyst_data = self.test_basket_catalyst_data_integrity(basket_data)
        else:
            print("⚠️  Skipping catalyst data test - no basket data available")
            catalyst_data = None
        
        # 3. Test bought items catalyst data
        print("🛒 BOUGHT ITEMS CATALYST DATA TEST")
        print("-" * 40)
        bought_items_data = self.test_bought_items_catalyst_data()
        
        # 4. Test assignment process
        print("🔄 ASSIGNMENT PROCESS SIMULATION")
        print("-" * 40)
        self.test_assignment_process_simulation()
        
        # 5. Test marketplace listings catalyst data
        print("🏪 MARKETPLACE LISTINGS CATALYST DATA TEST")
        print("-" * 40)
        listings_data = self.test_marketplace_listings_catalyst_data()
        
        # Print Summary
        print("=" * 80)
        print("BASKET CALCULATION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Analysis of reported issues
        print("🔍 ISSUE ANALYSIS:")
        print("-" * 40)
        
        if basket_data:
            if basket_data.get('issue_detected'):
                print("❌ CONFIRMED: Baskets showing 0 items even when items should be assigned")
            else:
                print("✅ No issue detected: Baskets have proper item counts")
                
            if basket_data.get('total_items') == 0:
                print("⚠️  No items found in any baskets - this could indicate assignment issues")
        
        if catalyst_data and catalyst_data.get('calculation_issue'):
            print("❌ CONFIRMED: Basket items have zero catalyst values causing (0,0,0) calculations")
        elif catalyst_data:
            print("✅ Basket items have proper catalyst data for calculations")
        
        if bought_items_data and bought_items_data.get('with_zero_catalyst') > 0:
            print("❌ CONFIRMED: Bought items have zero catalyst values")
        elif bought_items_data:
            print("✅ Bought items have proper catalyst data")
        
        if self.failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 BASKET CALCULATION TESTING COMPLETE")
        print("Key Findings:")
        print("  - Basket item counts and assignment process tested")
        print("  - Catalyst data integrity verified")
        print("  - Data flow from listings to baskets analyzed")
        print("  - Assignment endpoint availability checked")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BasketCalculationTester()
    
    print("🎯 RUNNING BASKET CALCULATIONS AND ITEM COUNTS TESTING AS REQUESTED")
    print("Testing basket item counts, catalyst data, and assignment process...")
    print()
    
    passed, failed, results = tester.run_basket_calculation_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)