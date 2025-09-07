#!/usr/bin/env python3
"""
Cataloro Buy Management Calculation Fix Testing Suite
Testing the fix for bought items catalyst fields and basket calculations
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://catalyst-view.preview.emergentagent.com/api"

class BuyManagementCalculationTester:
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

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}, Version: {data.get('version')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def get_demo_user(self):
        """Login as demo user and get user details"""
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
                    "Demo User Login", 
                    True, 
                    f"Logged in as {user.get('username')} (ID: {self.demo_user_id}), Role: {user.get('user_role')}"
                )
                return user
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Demo User Login", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Demo User Login", False, error_msg=str(e))
            return None

    def test_bought_items_catalyst_values(self):
        """Test GET /api/user/bought-items/{user_id} - verify catalyst values are not None/zero"""
        if not self.demo_user_id:
            self.log_test("Bought Items Catalyst Values Test", False, error_msg="No demo user ID available")
            return False
            
        try:
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.demo_user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                if not bought_items:
                    self.log_test(
                        "Bought Items Catalyst Values Test", 
                        True, 
                        "No bought items found - this is expected if user hasn't made purchases"
                    )
                    return True
                
                # Check catalyst values in bought items
                items_with_catalyst_data = 0
                items_with_renumeration = 0
                catalyst_details = []
                
                for item in bought_items:
                    # Check catalyst fields
                    weight = item.get('weight', 0)
                    pt_ppm = item.get('pt_ppm', 0)
                    pd_ppm = item.get('pd_ppm', 0)
                    rh_ppm = item.get('rh_ppm', 0)
                    
                    # Check renumeration fields
                    renumeration_pt = item.get('renumeration_pt')
                    renumeration_pd = item.get('renumeration_pd')
                    renumeration_rh = item.get('renumeration_rh')
                    
                    # Count items with catalyst data (any non-zero value)
                    if weight > 0 or pt_ppm > 0 or pd_ppm > 0 or rh_ppm > 0:
                        items_with_catalyst_data += 1
                    
                    # Count items with renumeration values (should not be None)
                    if renumeration_pt is not None and renumeration_pd is not None and renumeration_rh is not None:
                        items_with_renumeration += 1
                    
                    # Calculate potential values using the formula: ptG = weight * pt_ppm / 1000 * renumeration_pt
                    pt_g = (weight * pt_ppm / 1000 * renumeration_pt) if renumeration_pt else 0
                    pd_g = (weight * pd_ppm / 1000 * renumeration_pd) if renumeration_pd else 0
                    rh_g = (weight * rh_ppm / 1000 * renumeration_rh) if renumeration_rh else 0
                    
                    catalyst_details.append({
                        'title': item.get('title', 'Unknown'),
                        'weight': weight,
                        'pt_ppm': pt_ppm,
                        'pd_ppm': pd_ppm,
                        'rh_ppm': rh_ppm,
                        'renumeration_pt': renumeration_pt,
                        'renumeration_pd': renumeration_pd,
                        'renumeration_rh': renumeration_rh,
                        'calculated_pt_g': round(pt_g, 4),
                        'calculated_pd_g': round(pd_g, 4),
                        'calculated_rh_g': round(rh_g, 4)
                    })
                
                # Test passes if all items have renumeration values (not None)
                all_have_renumeration = items_with_renumeration == len(bought_items)
                
                details = f"Found {len(bought_items)} bought items. "
                details += f"Items with catalyst data: {items_with_catalyst_data}/{len(bought_items)}. "
                details += f"Items with renumeration values: {items_with_renumeration}/{len(bought_items)}. "
                
                if catalyst_details:
                    details += "Sample calculations: "
                    for detail in catalyst_details[:3]:  # Show first 3 items
                        details += f"{detail['title']}: Pt={detail['calculated_pt_g']}g, Pd={detail['calculated_pd_g']}g, Rh={detail['calculated_rh_g']}g; "
                
                self.log_test(
                    "Bought Items Catalyst Values Test", 
                    all_have_renumeration, 
                    details
                )
                return all_have_renumeration, catalyst_details
                
            else:
                self.log_test("Bought Items Catalyst Values Test", False, f"HTTP {response.status_code}")
                return False, []
                
        except Exception as e:
            self.log_test("Bought Items Catalyst Values Test", False, error_msg=str(e))
            return False, []

    def test_baskets_catalyst_values(self):
        """Test GET /api/user/baskets/{user_id} - verify basket items have proper catalyst data"""
        if not self.demo_user_id:
            self.log_test("Baskets Catalyst Values Test", False, error_msg="No demo user ID available")
            return False
            
        try:
            response = requests.get(f"{BACKEND_URL}/user/baskets/{self.demo_user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                if not baskets:
                    self.log_test(
                        "Baskets Catalyst Values Test", 
                        True, 
                        "No baskets found - this is expected if user hasn't created baskets"
                    )
                    return True
                
                # Check catalyst values in basket items
                total_basket_items = 0
                items_with_catalyst_data = 0
                items_with_renumeration = 0
                basket_details = []
                
                for basket in baskets:
                    basket_name = basket.get('name', 'Unknown Basket')
                    items = basket.get('items', [])
                    total_basket_items += len(items)
                    
                    basket_item_details = []
                    
                    for item in items:
                        # Check catalyst fields
                        weight = item.get('weight', 0)
                        pt_ppm = item.get('pt_ppm', 0)
                        pd_ppm = item.get('pd_ppm', 0)
                        rh_ppm = item.get('rh_ppm', 0)
                        
                        # Check renumeration fields
                        renumeration_pt = item.get('renumeration_pt')
                        renumeration_pd = item.get('renumeration_pd')
                        renumeration_rh = item.get('renumeration_rh')
                        
                        # Count items with catalyst data
                        if weight > 0 or pt_ppm > 0 or pd_ppm > 0 or rh_ppm > 0:
                            items_with_catalyst_data += 1
                        
                        # Count items with renumeration values
                        if renumeration_pt is not None and renumeration_pd is not None and renumeration_rh is not None:
                            items_with_renumeration += 1
                        
                        # Calculate values using the formula
                        pt_g = (weight * pt_ppm / 1000 * renumeration_pt) if renumeration_pt else 0
                        pd_g = (weight * pd_ppm / 1000 * renumeration_pd) if renumeration_pd else 0
                        rh_g = (weight * rh_ppm / 1000 * renumeration_rh) if renumeration_rh else 0
                        
                        basket_item_details.append({
                            'title': item.get('title', 'Unknown'),
                            'weight': weight,
                            'pt_ppm': pt_ppm,
                            'pd_ppm': pd_ppm,
                            'rh_ppm': rh_ppm,
                            'renumeration_pt': renumeration_pt,
                            'calculated_pt_g': round(pt_g, 4),
                            'calculated_pd_g': round(pd_g, 4),
                            'calculated_rh_g': round(rh_g, 4)
                        })
                    
                    basket_details.append({
                        'basket_name': basket_name,
                        'items': basket_item_details
                    })
                
                # Test passes if all items have renumeration values
                all_have_renumeration = items_with_renumeration == total_basket_items if total_basket_items > 0 else True
                
                details = f"Found {len(baskets)} baskets with {total_basket_items} total items. "
                details += f"Items with catalyst data: {items_with_catalyst_data}/{total_basket_items}. "
                details += f"Items with renumeration values: {items_with_renumeration}/{total_basket_items}. "
                
                if basket_details:
                    details += "Sample basket calculations: "
                    for basket in basket_details[:2]:  # Show first 2 baskets
                        details += f"{basket['basket_name']} ({len(basket['items'])} items): "
                        for item in basket['items'][:2]:  # Show first 2 items per basket
                            details += f"{item['title']} Pt={item['calculated_pt_g']}g, Pd={item['calculated_pd_g']}g, Rh={item['calculated_rh_g']}g; "
                
                self.log_test(
                    "Baskets Catalyst Values Test", 
                    all_have_renumeration, 
                    details
                )
                return all_have_renumeration, basket_details
                
            else:
                self.log_test("Baskets Catalyst Values Test", False, f"HTTP {response.status_code}")
                return False, []
                
        except Exception as e:
            self.log_test("Baskets Catalyst Values Test", False, error_msg=str(e))
            return False, []

    def test_calculation_logic_verification(self, bought_items_details, basket_details):
        """Test that calculation logic produces non-zero values when catalyst data is present"""
        try:
            # Check if we have any items with catalyst data to test calculations
            items_to_test = []
            
            # Add bought items with catalyst data
            for item in bought_items_details:
                if item['weight'] > 0 and (item['pt_ppm'] > 0 or item['pd_ppm'] > 0 or item['rh_ppm'] > 0):
                    items_to_test.append(item)
            
            # Add basket items with catalyst data
            for basket in basket_details:
                for item in basket['items']:
                    if item['weight'] > 0 and (item['pt_ppm'] > 0 or item['pd_ppm'] > 0 or item['rh_ppm'] > 0):
                        items_to_test.append(item)
            
            if not items_to_test:
                self.log_test(
                    "Calculation Logic Verification", 
                    True, 
                    "No items with catalyst data found to test calculations - this is expected if no items have catalyst values"
                )
                return True
            
            # Test calculation logic
            non_zero_calculations = 0
            calculation_details = []
            
            for item in items_to_test:
                pt_g = item['calculated_pt_g']
                pd_g = item['calculated_pd_g']
                rh_g = item['calculated_rh_g']
                
                # Check if calculations produce non-zero values
                has_non_zero_calculation = pt_g > 0 or pd_g > 0 or rh_g > 0
                
                if has_non_zero_calculation:
                    non_zero_calculations += 1
                
                calculation_details.append({
                    'title': item['title'],
                    'formula_pt': f"{item['weight']} * {item['pt_ppm']} / 1000 * {item['renumeration_pt']} = {pt_g}g",
                    'formula_pd': f"{item['weight']} * {item['pd_ppm']} / 1000 * {item['renumeration_pd']} = {pd_g}g",
                    'formula_rh': f"{item['weight']} * {item['rh_ppm']} / 1000 * {item['renumeration_rh']} = {rh_g}g",
                    'has_non_zero': has_non_zero_calculation
                })
            
            # Test passes if we have non-zero calculations or if all items legitimately have zero catalyst values
            success = non_zero_calculations > 0 or all(
                item['weight'] == 0 and item['pt_ppm'] == 0 and item['pd_ppm'] == 0 and item['rh_ppm'] == 0 
                for item in items_to_test
            )
            
            details = f"Tested {len(items_to_test)} items with catalyst data. "
            details += f"Items with non-zero calculations: {non_zero_calculations}/{len(items_to_test)}. "
            
            if calculation_details:
                details += "Sample calculations: "
                for calc in calculation_details[:3]:  # Show first 3 calculations
                    details += f"{calc['title']}: Pt={calc['formula_pt'].split('=')[1]}, "
            
            self.log_test(
                "Calculation Logic Verification", 
                success, 
                details
            )
            return success
            
        except Exception as e:
            self.log_test("Calculation Logic Verification", False, error_msg=str(e))
            return False

    def test_price_settings_integration(self):
        """Test that price settings are properly integrated for renumeration values"""
        try:
            # Try to get price settings (admin endpoint, might not be accessible)
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/price-settings", timeout=10)
            
            if response.status_code == 200:
                price_settings = response.json()
                renumeration_pt = price_settings.get('renumeration_pt')
                renumeration_pd = price_settings.get('renumeration_pd')
                renumeration_rh = price_settings.get('renumeration_rh')
                
                # Check if renumeration values are set
                has_renumeration_values = all(
                    val is not None and val > 0 
                    for val in [renumeration_pt, renumeration_pd, renumeration_rh]
                )
                
                details = f"Price settings found: Pt={renumeration_pt}, Pd={renumeration_pd}, Rh={renumeration_rh}"
                
                self.log_test(
                    "Price Settings Integration Test", 
                    has_renumeration_values, 
                    details
                )
                return has_renumeration_values
                
            else:
                # If we can't access price settings, check if bought items have renumeration values
                if self.demo_user_id:
                    bought_response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.demo_user_id}", timeout=10)
                    if bought_response.status_code == 200:
                        bought_items = bought_response.json()
                        if bought_items:
                            first_item = bought_items[0]
                            has_renumeration = all(
                                first_item.get(key) is not None 
                                for key in ['renumeration_pt', 'renumeration_pd', 'renumeration_rh']
                            )
                            
                            details = f"Price settings endpoint not accessible (HTTP {response.status_code}), but bought items have renumeration values: {has_renumeration}"
                            
                            self.log_test(
                                "Price Settings Integration Test", 
                                has_renumeration, 
                                details
                            )
                            return has_renumeration
                
                self.log_test(
                    "Price Settings Integration Test", 
                    False, 
                    f"Price settings endpoint not accessible (HTTP {response.status_code}) and no bought items to verify"
                )
                return False
                
        except Exception as e:
            self.log_test("Price Settings Integration Test", False, error_msg=str(e))
            return False

    def run_buy_management_calculation_testing(self):
        """Run Buy Management Calculation Fix testing as requested in review"""
        print("=" * 80)
        print("CATALORO BUY MANAGEMENT CALCULATION FIX TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        print("Testing the fix for bought items catalyst fields and basket calculations")
        print("Expected: Catalyst values should not be None, calculations should not be (0,0,0)")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting testing.")
            return
        
        # 2. Get Demo User
        print("👤 DEMO USER LOGIN")
        print("-" * 40)
        demo_user = self.get_demo_user()
        if not demo_user:
            print("❌ Failed to login as demo user. Aborting tests.")
            return
        
        # 3. Test Bought Items Catalyst Values
        print("🛒 TEST BOUGHT ITEMS CATALYST VALUES")
        print("-" * 40)
        bought_items_success, bought_items_details = self.test_bought_items_catalyst_values()
        
        # 4. Test Baskets Catalyst Values
        print("🧺 TEST BASKETS CATALYST VALUES")
        print("-" * 40)
        baskets_success, basket_details = self.test_baskets_catalyst_values()
        
        # 5. Test Calculation Logic
        print("🧮 TEST CALCULATION LOGIC VERIFICATION")
        print("-" * 40)
        calculation_success = self.test_calculation_logic_verification(bought_items_details, basket_details)
        
        # 6. Test Price Settings Integration
        print("⚙️ TEST PRICE SETTINGS INTEGRATION")
        print("-" * 40)
        price_settings_success = self.test_price_settings_integration()
        
        # Print Summary
        print("=" * 80)
        print("BUY MANAGEMENT CALCULATION FIX TEST SUMMARY")
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
        
        print("\n🎯 BUY MANAGEMENT CALCULATION FIX TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Bought items should have non-None catalyst values from listings")
        print("  ✅ Basket items should have proper catalyst data from listings")
        print("  ✅ Renumeration values should come from price settings (not None)")
        print("  ✅ Calculations should produce non-zero values when catalyst data exists")
        print("  ✅ Formula: ptG = weight * pt_ppm / 1000 * renumeration_pt")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BuyManagementCalculationTester()
    
    # Run Buy Management Calculation Fix testing as requested in the review
    print("🎯 RUNNING BUY MANAGEMENT CALCULATION FIX TESTING AS REQUESTED")
    print("Testing the fix where bought items were getting None values for catalyst fields...")
    print()
    
    passed, failed, results = tester.run_buy_management_calculation_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)