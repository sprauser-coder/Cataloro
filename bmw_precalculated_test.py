#!/usr/bin/env python3
"""
BMW75364089 Links Pre-calculated Values Fix Testing
Testing the fix for BMW75364089 Links to use pre-calculated values when PPM data is missing
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://listing-repair-4.preview.emergentagent.com/api"

class BMWPreCalculatedTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_user = None
        self.admin_token = None
        
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

    def test_admin_login(self):
        """Test admin login and store credentials for subsequent tests"""
        try:
            admin_credentials = {
                "email": "admin@cataloro.com",
                "password": "admin123"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login", 
                json=admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                token = data.get('token', '')
                
                self.admin_user = user
                self.admin_token = token
                
                user_role = user.get('user_role')
                user_id = user.get('id')
                username = user.get('username')
                
                is_admin = user_role in ['Admin', 'Admin-Manager']
                
                self.log_test(
                    "Admin Login", 
                    is_admin, 
                    f"Username: {username}, Role: {user_role}, User ID: {user_id}"
                )
                return is_admin
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login", False, error_msg=f"Login failed: {error_detail}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, error_msg=str(e))
            return False

    def test_find_bmw_listing(self):
        """Find BMW75364089 Links listing in the system"""
        try:
            # Search for BMW75364089 Links in listings
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                # Look for BMW75364089 Links
                bmw_listing = None
                for listing in listings:
                    title = listing.get('title', '').lower()
                    if 'bmw75364089' in title or 'bmw' in title and '75364089' in title:
                        bmw_listing = listing
                        break
                
                if bmw_listing:
                    self.log_test(
                        "Find BMW75364089 Links Listing", 
                        True, 
                        f"Found BMW listing: {bmw_listing.get('title')} (ID: {bmw_listing.get('id')}, Price: €{bmw_listing.get('price')})"
                    )
                    return bmw_listing
                else:
                    self.log_test("Find BMW75364089 Links Listing", False, error_msg="BMW75364089 Links listing not found in marketplace")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Find BMW75364089 Links Listing", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Find BMW75364089 Links Listing", False, error_msg=str(e))
            return None

    def test_check_catalyst_database_entry(self):
        """Check BMW75364089 Links entry in catalyst database"""
        try:
            # Get unified calculations to check catalyst database
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations", timeout=10)
            
            if response.status_code == 200:
                catalysts = response.json()
                
                # Look for BMW75364089 Links in catalyst database
                bmw_catalyst = None
                for catalyst in catalysts:
                    name = catalyst.get('name', '').lower()
                    if 'bmw75364089' in name or ('bmw' in name and '75364089' in name):
                        bmw_catalyst = catalyst
                        break
                
                if bmw_catalyst:
                    # Check if it has pre-calculated values
                    pt_g = bmw_catalyst.get('pt_g', 0)
                    pd_g = bmw_catalyst.get('pd_g', 0)
                    rh_g = bmw_catalyst.get('rh_g', 0)
                    weight = bmw_catalyst.get('weight', 0)
                    
                    has_precalculated = any([pt_g > 0, pd_g > 0, rh_g > 0])
                    
                    self.log_test(
                        "Check BMW Catalyst Database Entry", 
                        has_precalculated, 
                        f"BMW catalyst: {bmw_catalyst.get('name')}, Weight: {weight}g, "
                        f"Pre-calculated values: PT={pt_g}g, PD={pd_g}g, RH={rh_g}g"
                    )
                    return bmw_catalyst
                else:
                    self.log_test("Check BMW Catalyst Database Entry", False, error_msg="BMW75364089 Links not found in catalyst database")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Check BMW Catalyst Database Entry", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Check BMW Catalyst Database Entry", False, error_msg=str(e))
            return None

    def test_create_bmw_listing_with_precalculated_values(self, catalyst_data):
        """Create BMW listing with pre-calculated values from catalyst database"""
        try:
            if not catalyst_data or not self.admin_user:
                self.log_test("Create BMW Listing with Pre-calculated Values", False, error_msg="Catalyst data or admin user not available")
                return None
                
            # Create BMW listing with pre-calculated values
            listing_data = {
                "title": "BMW75364089 Links Test Listing",
                "description": f"BMW75364089 Links catalyst converter with pre-calculated values: PT={catalyst_data.get('pt_g')}g, PD={catalyst_data.get('pd_g')}g, RH={catalyst_data.get('rh_g')}g",
                "price": 170.0,
                "category": "Automotive",
                "condition": "Used",
                "seller_id": self.admin_user.get('id'),
                "images": [],
                "tags": ["bmw", "catalyst", "75364089"],
                "features": ["Pre-calculated values", "BMW OEM part"],
                # Catalyst database fields - simulate missing PPM data but with pre-calculated values
                "ceramic_weight": catalyst_data.get('weight', 0.52),
                "pt_ppm": None,  # Missing PPM data (the issue we're fixing)
                "pd_ppm": None,  # Missing PPM data
                "rh_ppm": None,  # Missing PPM data
                # Pre-calculated content values (should be used when PPM is missing)
                "pt_g": catalyst_data.get('pt_g', 0.0),
                "pd_g": catalyst_data.get('pd_g', 2.4902),
                "rh_g": catalyst_data.get('rh_g', 0.2406),
                "status": "active"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/listings",
                json=listing_data,
                timeout=10
            )
            
            if response.status_code == 200:
                create_response = response.json()
                listing_id = create_response.get('listing_id')
                
                if listing_id:
                    # Get the created listing to verify data
                    get_response = requests.get(f"{BACKEND_URL}/listings/{listing_id}", timeout=10)
                    if get_response.status_code == 200:
                        created_listing = get_response.json()
                        
                        # Verify pre-calculated values were stored
                        has_precalculated = any([
                            created_listing.get('pt_g', 0) > 0,
                            created_listing.get('pd_g', 0) > 0,
                            created_listing.get('rh_g', 0) > 0
                        ])
                        
                        self.log_test(
                            "Create BMW Listing with Pre-calculated Values", 
                            has_precalculated, 
                            f"Listing ID: {listing_id}, Weight: {created_listing.get('ceramic_weight')}g, "
                            f"Pre-calculated: PT={created_listing.get('pt_g')}g, PD={created_listing.get('pd_g')}g, RH={created_listing.get('rh_g')}g"
                        )
                        
                        return created_listing if has_precalculated else None
                    else:
                        self.log_test("Create BMW Listing with Pre-calculated Values", False, error_msg="Failed to retrieve created listing")
                        return None
                else:
                    self.log_test("Create BMW Listing with Pre-calculated Values", False, error_msg="No listing ID returned")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create BMW Listing with Pre-calculated Values", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Create BMW Listing with Pre-calculated Values", False, error_msg=str(e))
            return None

    def test_create_tender_for_bmw_listing(self, bmw_listing):
        """Create and accept tender for BMW listing to test preservation logic"""
        try:
            if not bmw_listing or not self.admin_user:
                self.log_test("Create Tender for BMW Listing", False, error_msg="BMW listing or admin user not available")
                return None
                
            listing_id = bmw_listing.get('id')
            seller_id = bmw_listing.get('seller_id')
            
            # Get users to find a buyer
            users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if users_response.status_code != 200:
                self.log_test("Create Tender for BMW Listing", False, error_msg="Could not get users list")
                return None
                
            users = users_response.json()
            buyer_user = None
            
            # Find a user that's not the seller
            for user in users:
                if user.get('id') != seller_id and user.get('registration_status') == 'Approved':
                    buyer_user = user
                    break
            
            if not buyer_user:
                self.log_test("Create Tender for BMW Listing", False, error_msg="No suitable buyer user found")
                return None
            
            # Create tender
            tender_data = {
                "listing_id": listing_id,
                "buyer_id": buyer_user.get('id'),
                "offer_amount": bmw_listing.get('price', 170.0),
                "message": "Test tender for BMW75364089 Links pre-calculated values testing"
            }
            
            tender_response = requests.post(
                f"{BACKEND_URL}/tenders/submit",
                json=tender_data,
                timeout=10
            )
            
            if tender_response.status_code != 200:
                error_detail = tender_response.json().get('detail', 'Unknown error') if tender_response.content else f"HTTP {tender_response.status_code}"
                self.log_test("Create Tender for BMW Listing", False, error_msg=f"Tender creation failed: {error_detail}")
                return None
                
            tender = tender_response.json()
            tender_id = tender.get('tender_id') or tender.get('id')
            
            if not tender_id:
                self.log_test("Create Tender for BMW Listing", False, error_msg="No tender ID returned from creation")
                return None
            
            # Accept the tender
            accept_data = {"seller_id": seller_id}
            accept_response = requests.put(
                f"{BACKEND_URL}/tenders/{tender_id}/accept",
                json=accept_data,
                timeout=10
            )
            
            if accept_response.status_code == 200:
                accepted_tender = accept_response.json()
                
                self.log_test(
                    "Create Tender for BMW Listing", 
                    True, 
                    f"Tender ID: {tender_id}, Amount: €{tender.get('offer_amount')}, Buyer: {buyer_user.get('username')}"
                )
                
                self.buyer_user = buyer_user
                return accepted_tender
            else:
                error_detail = accept_response.json().get('detail', 'Unknown error') if accept_response.content else f"HTTP {accept_response.status_code}"
                self.log_test("Create Tender for BMW Listing", False, error_msg=f"Tender acceptance failed: {error_detail}")
                return None
                
        except Exception as e:
            self.log_test("Create Tender for BMW Listing", False, error_msg=str(e))
            return None

    def test_verify_precalculated_values_preserved(self):
        """Verify that pre-calculated values are preserved in bought items"""
        try:
            test_user = getattr(self, 'buyer_user', self.admin_user)
            if not test_user:
                self.log_test("Verify Pre-calculated Values Preserved", False, error_msg="No test user available")
                return None
                
            user_id = test_user.get('id')
            
            # Get bought items
            response = requests.get(
                f"{BACKEND_URL}/user/bought-items/{user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                bought_items = response.json()
                
                if not bought_items:
                    self.log_test("Verify Pre-calculated Values Preserved", False, error_msg="No bought items found")
                    return None
                
                # Find BMW item
                bmw_item = None
                for item in bought_items:
                    title = item.get('title', '').lower()
                    if 'bmw75364089' in title or ('bmw' in title and 'test' in title):
                        bmw_item = item
                        break
                
                if bmw_item:
                    # Check if pre-calculated values are preserved
                    pt_g = bmw_item.get('pt_g', 0)
                    pd_g = bmw_item.get('pd_g', 0)
                    rh_g = bmw_item.get('rh_g', 0)
                    weight = bmw_item.get('weight', 0)
                    
                    # Check if PPM values are missing (as expected)
                    pt_ppm = bmw_item.get('pt_ppm')
                    pd_ppm = bmw_item.get('pd_ppm')
                    rh_ppm = bmw_item.get('rh_ppm')
                    
                    # Expected values for BMW75364089 Links
                    expected_pt_g = 0.0
                    expected_pd_g = 2.4902
                    expected_rh_g = 0.2406
                    
                    # Check if we have the expected pre-calculated values
                    pt_correct = abs(pt_g - expected_pt_g) < 0.01
                    pd_correct = abs(pd_g - expected_pd_g) < 0.01
                    rh_correct = abs(rh_g - expected_rh_g) < 0.01
                    
                    # This is the key test - we should have pre-calculated values matching expected BMW values
                    fix_working = pt_correct and pd_correct and rh_correct
                    
                    self.log_test(
                        "Verify Pre-calculated Values Preserved", 
                        fix_working, 
                        f"BMW Item: {bmw_item.get('title')}, Weight: {weight}g, "
                        f"PPM values: PT={pt_ppm}, PD={pd_ppm}, RH={rh_ppm} (should be None/missing), "
                        f"Pre-calculated: PT={pt_g}g, PD={pd_g}g, RH={rh_g}g. "
                        f"Expected: PT={expected_pt_g}g, PD={expected_pd_g}g, RH={expected_rh_g}g"
                    )
                    
                    return bmw_item if fix_working else None
                else:
                    self.log_test("Verify Pre-calculated Values Preserved", False, error_msg="BMW item not found in bought items")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Verify Pre-calculated Values Preserved", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Verify Pre-calculated Values Preserved", False, error_msg=str(e))
            return None

    def test_basket_calculation_with_precalculated_values(self, bmw_item):
        """Test basket calculation uses pre-calculated values when PPM is missing"""
        try:
            if not bmw_item:
                self.log_test("Basket Calculation with Pre-calculated Values", False, error_msg="BMW item not available")
                return False
                
            test_user = getattr(self, 'buyer_user', self.admin_user)
            if not test_user:
                self.log_test("Basket Calculation with Pre-calculated Values", False, error_msg="No test user available")
                return False
                
            user_id = test_user.get('id')
            
            # Create basket
            basket_data = {
                "user_id": user_id,
                "name": "BMW Pre-calculated Values Test Basket",
                "description": "Test basket for BMW75364089 Links pre-calculated values fix"
            }
            
            basket_response = requests.post(
                f"{BACKEND_URL}/user/baskets",
                json=basket_data,
                timeout=10
            )
            
            if basket_response.status_code != 200:
                error_detail = basket_response.json().get('detail', 'Unknown error') if basket_response.content else f"HTTP {basket_response.status_code}"
                self.log_test("Basket Calculation with Pre-calculated Values", False, error_msg=f"Basket creation failed: {error_detail}")
                return False
                
            basket = basket_response.json()
            basket_id = basket.get('basket_id') or basket.get('id')
            
            # Assign BMW item to basket
            item_id = bmw_item.get('id')
            assign_data = {"basket_id": basket_id}
            
            assign_response = requests.put(
                f"{BACKEND_URL}/user/bought-items/{item_id}/assign",
                json=assign_data,
                timeout=10
            )
            
            if assign_response.status_code != 200:
                error_detail = assign_response.json().get('detail', 'Unknown error') if assign_response.content else f"HTTP {assign_response.status_code}"
                self.log_test("Basket Calculation with Pre-calculated Values", False, error_msg=f"Item assignment failed: {error_detail}")
                return False
            
            # Get basket with calculations
            baskets_response = requests.get(
                f"{BACKEND_URL}/user/baskets/{user_id}",
                timeout=10
            )
            
            if baskets_response.status_code == 200:
                baskets = baskets_response.json()
                
                # Find our test basket
                test_basket = None
                for b in baskets:
                    if b.get('id') == basket_id:
                        test_basket = b
                        break
                
                if test_basket and test_basket.get('items'):
                    item = test_basket['items'][0]
                    
                    # Check calculated values
                    calc_pt_g = item.get('pt_g', 0)
                    calc_pd_g = item.get('pd_g', 0)
                    calc_rh_g = item.get('rh_g', 0)
                    
                    # Expected values for BMW75364089 Links (from review request)
                    expected_pt_g = 0.0
                    expected_pd_g = 2.4902
                    expected_rh_g = 0.2406
                    
                    # Check if calculations match expected values (allow small tolerance)
                    pt_correct = abs(calc_pt_g - expected_pt_g) < 0.01
                    pd_correct = abs(calc_pd_g - expected_pd_g) < 0.01
                    rh_correct = abs(calc_rh_g - expected_rh_g) < 0.01
                    
                    calculations_correct = pt_correct and pd_correct and rh_correct
                    
                    # Also check that we're not getting (0,0,0) anymore
                    not_zero_values = any([calc_pt_g > 0, calc_pd_g > 0, calc_rh_g > 0])
                    
                    fix_working = calculations_correct and not_zero_values
                    
                    self.log_test(
                        "Basket Calculation with Pre-calculated Values", 
                        fix_working, 
                        f"BMW basket calculations - Got: PT={calc_pt_g:.4f}g, PD={calc_pd_g:.4f}g, RH={calc_rh_g:.4f}g. "
                        f"Expected: PT={expected_pt_g:.4f}g, PD={expected_pd_g:.4f}g, RH={expected_rh_g:.4f}g. "
                        f"Fix working: {fix_working} (should show expected values, not (0,0,0))"
                    )
                    
                    return fix_working
                else:
                    self.log_test("Basket Calculation with Pre-calculated Values", False, error_msg="Test basket or items not found")
                    return False
            else:
                error_detail = baskets_response.json().get('detail', 'Unknown error') if baskets_response.content else f"HTTP {baskets_response.status_code}"
                self.log_test("Basket Calculation with Pre-calculated Values", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Basket Calculation with Pre-calculated Values", False, error_msg=str(e))
            return False

    def run_bmw_precalculated_testing(self):
        """Run comprehensive BMW75364089 Links pre-calculated values fix testing"""
        print("=" * 80)
        print("BMW75364089 LINKS PRE-CALCULATED VALUES FIX TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        print("Testing the fix for BMW75364089 Links to use pre-calculated values when PPM data is missing")
        print("Expected Result: BMW should show approximately (0.0, 2.4902, 0.2406) instead of (0,0,0)")
        print()
        
        # 1. Admin Login
        print("👤 ADMIN LOGIN")
        print("-" * 40)
        if not self.test_admin_login():
            print("❌ Admin login failed. Aborting testing.")
            return
        
        # 2. Check BMW in Catalyst Database
        print("🔍 CHECK BMW75364089 LINKS IN CATALYST DATABASE")
        print("-" * 40)
        catalyst_data = self.test_check_catalyst_database_entry()
        if not catalyst_data:
            print("❌ BMW catalyst data not found. Aborting testing.")
            return
        
        # 3. Find or Create BMW Listing
        print("📝 FIND OR CREATE BMW75364089 LINKS LISTING")
        print("-" * 40)
        bmw_listing = self.test_find_bmw_listing()
        if not bmw_listing:
            print("BMW listing not found. Creating new listing with pre-calculated values...")
            bmw_listing = self.test_create_bmw_listing_with_precalculated_values(catalyst_data)
            if not bmw_listing:
                print("❌ Failed to create BMW listing. Aborting testing.")
                return
        
        # 4. Create Tender for BMW Listing
        print("🤝 CREATE TENDER FOR BMW LISTING")
        print("-" * 40)
        accepted_tender = self.test_create_tender_for_bmw_listing(bmw_listing)
        if not accepted_tender:
            print("❌ Failed to create and accept tender for BMW listing. Aborting testing.")
            return
        
        # Wait for processing
        time.sleep(2)
        
        # 5. Verify Pre-calculated Values Preserved
        print("🔍 VERIFY PRE-CALCULATED VALUES PRESERVED IN BOUGHT ITEMS")
        print("-" * 40)
        bmw_item = self.test_verify_precalculated_values_preserved()
        if not bmw_item:
            print("❌ Pre-calculated values not preserved. The fix may not be working.")
        
        # 6. Test Basket Calculation with Pre-calculated Values
        print("🧮 TEST BASKET CALCULATION WITH PRE-CALCULATED VALUES")
        print("-" * 40)
        self.test_basket_calculation_with_precalculated_values(bmw_item)
        
        # Print Summary
        print("=" * 80)
        print("BMW75364089 LINKS PRE-CALCULATED VALUES FIX TEST SUMMARY")
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
        
        print("\n🎯 BMW75364089 LINKS PRE-CALCULATED VALUES FIX TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ BMW75364089 Links has pre-calculated values in catalyst database")
        print("  ✅ New purchase preserves pre-calculated values even when PPM is missing")
        print("  ✅ Basket calculation shows (0.0, 2.4902, 0.2406) instead of (0,0,0)")
        print("  ✅ Fix resolves the issue for catalysts with incomplete raw PPM data")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BMWPreCalculatedTester()
    
    print("🎯 RUNNING BMW75364089 LINKS PRE-CALCULATED VALUES FIX TESTING")
    print("Testing the fix to use pre-calculated gram values when PPM data is missing...")
    print()
    
    result = tester.run_bmw_precalculated_testing()
    if result:
        passed, failed, results = result
        # Exit with appropriate code
        exit(0 if failed == 0 else 1)
    else:
        exit(1)