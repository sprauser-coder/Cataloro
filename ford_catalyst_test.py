#!/usr/bin/env python3
"""
Ford Listing Catalyst Values Debug Test
Testing Ford listing catalyst values and basket calculations as requested in review
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class FordCatalystTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.ford_listing = None
        self.demo_user = None
        
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
                    f"Status: {data.get('status')}, App: {data.get('app')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def login_demo_user(self):
        """Login as demo user to get user context"""
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
                self.demo_user = data.get('user', {})
                self.log_test(
                    "Demo User Login", 
                    True, 
                    f"Logged in as {self.demo_user.get('username', 'Unknown')}"
                )
                return True
            else:
                self.log_test("Demo User Login", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Demo User Login", False, error_msg=str(e))
            return False

    def find_ford_listing(self):
        """Find Ford listing in marketplace"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                # Look for Ford listing
                ford_listings = []
                for listing in listings:
                    title = listing.get('title', '').lower()
                    if 'ford' in title or 'f150' in title or 'f-150' in title:
                        ford_listings.append(listing)
                
                if ford_listings:
                    self.ford_listing = ford_listings[0]  # Take first Ford listing
                    self.log_test(
                        "Find Ford Listing", 
                        True, 
                        f"Found Ford listing: '{self.ford_listing.get('title')}' (ID: {self.ford_listing.get('id')})"
                    )
                    return True
                else:
                    self.log_test("Find Ford Listing", False, "No Ford listing found in marketplace")
                    return False
            else:
                self.log_test("Find Ford Listing", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Find Ford Listing", False, error_msg=str(e))
            return False

    def check_ford_catalyst_values(self):
        """Check Ford listing catalyst values directly"""
        if not self.ford_listing:
            self.log_test("Check Ford Catalyst Values", False, error_msg="No Ford listing found")
            return False
            
        try:
            listing_id = self.ford_listing.get('id')
            
            # Get listing details directly
            response = requests.get(f"{BACKEND_URL}/listings/{listing_id}", timeout=10)
            
            if response.status_code == 200:
                listing_data = response.json()
                
                # Extract catalyst values
                ceramic_weight = listing_data.get('ceramic_weight')
                pt_ppm = listing_data.get('pt_ppm')
                pd_ppm = listing_data.get('pd_ppm')
                rh_ppm = listing_data.get('rh_ppm')
                
                # Expected values from review request
                expected_weight = 139.7
                expected_pt_ppm = 1394
                expected_pd_ppm = 959
                expected_rh_ppm = 0
                
                # Check if values match expected
                weight_match = ceramic_weight == expected_weight
                pt_match = pt_ppm == expected_pt_ppm
                pd_match = pd_ppm == expected_pd_ppm
                rh_match = rh_ppm == expected_rh_ppm
                
                all_match = weight_match and pt_match and pd_match and rh_match
                
                details = f"Current values - Weight: {ceramic_weight}, PT PPM: {pt_ppm}, PD PPM: {pd_ppm}, RH PPM: {rh_ppm}"
                details += f" | Expected - Weight: {expected_weight}, PT PPM: {expected_pt_ppm}, PD PPM: {expected_pd_ppm}, RH PPM: {expected_rh_ppm}"
                details += f" | Matches: Weight={weight_match}, PT={pt_match}, PD={pd_match}, RH={rh_match}"
                
                self.log_test(
                    "Check Ford Catalyst Values", 
                    all_match, 
                    details
                )
                return all_match, listing_data
            else:
                self.log_test("Check Ford Catalyst Values", False, f"HTTP {response.status_code}")
                return False, None
        except Exception as e:
            self.log_test("Check Ford Catalyst Values", False, error_msg=str(e))
            return False, None

    def fix_ford_catalyst_values(self):
        """Fix Ford listing with correct catalyst values"""
        if not self.ford_listing:
            self.log_test("Fix Ford Catalyst Values", False, error_msg="No Ford listing found")
            return False
            
        try:
            listing_id = self.ford_listing.get('id')
            
            # Correct catalyst values from review request
            correct_values = {
                "ceramic_weight": 139.7,
                "pt_ppm": 1394.0,
                "pd_ppm": 959.0,
                "rh_ppm": 0.0
            }
            
            # Update listing with correct values
            response = requests.put(
                f"{BACKEND_URL}/listings/{listing_id}",
                json=correct_values,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test(
                    "Fix Ford Catalyst Values", 
                    True, 
                    f"Successfully updated Ford listing with correct catalyst values: {correct_values}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Fix Ford Catalyst Values", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Fix Ford Catalyst Values", False, error_msg=str(e))
            return False

    def verify_ford_catalyst_fix(self):
        """Verify Ford listing now has correct catalyst values"""
        if not self.ford_listing:
            self.log_test("Verify Ford Catalyst Fix", False, error_msg="No Ford listing found")
            return False
            
        try:
            listing_id = self.ford_listing.get('id')
            
            # Get updated listing details
            response = requests.get(f"{BACKEND_URL}/listings/{listing_id}", timeout=10)
            
            if response.status_code == 200:
                listing_data = response.json()
                
                # Extract catalyst values
                ceramic_weight = listing_data.get('ceramic_weight')
                pt_ppm = listing_data.get('pt_ppm')
                pd_ppm = listing_data.get('pd_ppm')
                rh_ppm = listing_data.get('rh_ppm')
                
                # Expected values
                expected_weight = 139.7
                expected_pt_ppm = 1394.0
                expected_pd_ppm = 959.0
                expected_rh_ppm = 0.0
                
                # Check if values now match
                weight_match = ceramic_weight == expected_weight
                pt_match = pt_ppm == expected_pt_ppm
                pd_match = pd_ppm == expected_pd_ppm
                rh_match = rh_ppm == expected_rh_ppm
                
                all_match = weight_match and pt_match and pd_match and rh_match
                
                details = f"Updated values - Weight: {ceramic_weight}, PT PPM: {pt_ppm}, PD PPM: {pd_ppm}, RH PPM: {rh_ppm}"
                details += f" | All values correct: {all_match}"
                
                self.log_test(
                    "Verify Ford Catalyst Fix", 
                    all_match, 
                    details
                )
                return all_match
            else:
                self.log_test("Verify Ford Catalyst Fix", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Verify Ford Catalyst Fix", False, error_msg=str(e))
            return False

    def create_ford_tender(self):
        """Create a tender for Ford listing to simulate purchase"""
        if not self.demo_user or not self.ford_listing:
            self.log_test("Create Ford Tender", False, error_msg="Missing demo user or Ford listing")
            return False, None
            
        try:
            user_id = self.demo_user.get('id')
            listing_id = self.ford_listing.get('id')
            
            # Create tender data
            tender_data = {
                "listing_id": listing_id,
                "buyer_id": user_id,
                "offer_amount": 250.0,  # Reasonable offer amount
                "message": "Test tender for Ford catalyst calculation verification"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/tenders",
                json=tender_data,
                timeout=10
            )
            
            if response.status_code == 200:
                tender = response.json()
                tender_id = tender.get('id')
                self.log_test(
                    "Create Ford Tender", 
                    True, 
                    f"Created tender for Ford listing: {tender_id}"
                )
                return True, tender_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Ford Tender", False, error_msg=error_detail)
                return False, None
        except Exception as e:
            self.log_test("Create Ford Tender", False, error_msg=str(e))
            return False, None

    def accept_ford_tender(self, tender_id):
        """Accept the Ford tender to create bought item"""
        if not tender_id:
            self.log_test("Accept Ford Tender", False, error_msg="No tender ID provided")
            return False
            
        try:
            # Accept tender
            acceptance_data = {
                "acceptance_message": "Accepting tender for Ford catalyst testing"
            }
            
            response = requests.put(
                f"{BACKEND_URL}/tenders/{tender_id}/accept",
                json=acceptance_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test(
                    "Accept Ford Tender", 
                    True, 
                    f"Successfully accepted Ford tender: {tender_id}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Accept Ford Tender", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Accept Ford Tender", False, error_msg=str(e))
            return False

    def create_test_basket(self):
        """Create a test basket for Ford item assignment"""
        if not self.demo_user:
            self.log_test("Create Test Basket", False, error_msg="No demo user")
            return False, None
            
        try:
            user_id = self.demo_user.get('id')
            
            basket_data = {
                "name": "Ford Catalyst Test Basket",
                "description": "Test basket for Ford catalyst calculation verification"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/baskets/{user_id}",
                json=basket_data,
                timeout=10
            )
            
            if response.status_code == 200:
                basket = response.json()
                basket_id = basket.get('id')
                self.log_test(
                    "Create Test Basket", 
                    True, 
                    f"Created test basket: {basket_id}"
                )
                return True, basket_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test Basket", False, error_msg=error_detail)
                return False, None
        except Exception as e:
            self.log_test("Create Test Basket", False, error_msg=str(e))
            return False, None

    def assign_ford_to_basket(self, basket_id):
        """Assign Ford bought item to basket"""
        if not self.demo_user or not basket_id:
            self.log_test("Assign Ford to Basket", False, error_msg="Missing demo user or basket ID")
            return False
            
        try:
            user_id = self.demo_user.get('id')
            listing_id = self.ford_listing.get('id')
            
            # Get bought items to find Ford item
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                # Find Ford item
                ford_bought_item = None
                for item in bought_items:
                    if item.get('listing_id') == listing_id:
                        ford_bought_item = item
                        break
                
                if ford_bought_item:
                    item_id = ford_bought_item.get('id')
                    
                    # Assign to basket
                    assignment_data = {
                        "item_ids": [item_id]
                    }
                    
                    response = requests.post(
                        f"{BACKEND_URL}/user/baskets/{basket_id}/assign",
                        json=assignment_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        self.log_test(
                            "Assign Ford to Basket", 
                            True, 
                            f"Successfully assigned Ford item {item_id} to basket {basket_id}"
                        )
                        return True
                    else:
                        error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                        self.log_test("Assign Ford to Basket", False, error_msg=error_detail)
                        return False
                else:
                    self.log_test("Assign Ford to Basket", False, "Ford bought item not found")
                    return False
            else:
                self.log_test("Assign Ford to Basket", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Assign Ford to Basket", False, error_msg=str(e))
            return False

    def test_basket_calculation_with_ford(self, basket_id):
        """Test basket calculation with Ford item after assignment"""
        if not self.demo_user or not basket_id:
            self.log_test("Test Basket Calculation", False, error_msg="Missing demo user or basket ID")
            return False
            
        try:
            user_id = self.demo_user.get('id')
            listing_id = self.ford_listing.get('id')
            
            # Get basket with items
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                # Find our test basket
                test_basket = None
                for basket in baskets:
                    if basket.get('id') == basket_id:
                        test_basket = basket
                        break
                
                if test_basket:
                    basket_items = test_basket.get('items', [])
                    ford_item = None
                    
                    for item in basket_items:
                        if item.get('listing_id') == listing_id:
                            ford_item = item
                            break
                    
                    if ford_item:
                        # Get price settings for renumeration values
                        price_response = requests.get(f"{BACKEND_URL}/admin/catalyst/price-settings", timeout=10)
                        
                        if price_response.status_code == 200:
                            price_settings = price_response.json()
                            renumeration_pt = price_settings.get('renumeration_pt', 0.98)
                            renumeration_pd = price_settings.get('renumeration_pd', 0.98)
                            renumeration_rh = price_settings.get('renumeration_rh', 0.9)
                        else:
                            # Use default values
                            renumeration_pt = 0.98
                            renumeration_pd = 0.98
                            renumeration_rh = 0.9
                        
                        # Calculate expected values based on correct catalyst data
                        # Formula: (weight * ppm / 1000000) * renumeration
                        weight = 139.7
                        pt_ppm = 1394.0
                        pd_ppm = 959.0
                        rh_ppm = 0.0
                        
                        expected_pt_g = (weight * pt_ppm / 1000000) * renumeration_pt
                        expected_pd_g = (weight * pd_ppm / 1000000) * renumeration_pd
                        expected_rh_g = (weight * rh_ppm / 1000000) * renumeration_rh
                        
                        # Get actual values from item (these should be calculated when assigned)
                        actual_weight = ford_item.get('weight', 0)
                        actual_pt_ppm = ford_item.get('pt_ppm', 0)
                        actual_pd_ppm = ford_item.get('pd_ppm', 0)
                        actual_rh_ppm = ford_item.get('rh_ppm', 0)
                        actual_renumeration_pt = ford_item.get('renumeration_pt', 0)
                        actual_renumeration_pd = ford_item.get('renumeration_pd', 0)
                        actual_renumeration_rh = ford_item.get('renumeration_rh', 0)
                        
                        # Calculate actual grams based on item values
                        if actual_weight and actual_pt_ppm and actual_renumeration_pt:
                            calculated_pt_g = (actual_weight * actual_pt_ppm / 1000000) * actual_renumeration_pt
                        else:
                            calculated_pt_g = 0
                            
                        if actual_weight and actual_pd_ppm and actual_renumeration_pd:
                            calculated_pd_g = (actual_weight * actual_pd_ppm / 1000000) * actual_renumeration_pd
                        else:
                            calculated_pd_g = 0
                            
                        if actual_weight and actual_rh_ppm and actual_renumeration_rh:
                            calculated_rh_g = (actual_weight * actual_rh_ppm / 1000000) * actual_renumeration_rh
                        else:
                            calculated_rh_g = 0
                        
                        # Check if values match expected (with tolerance for floating point)
                        pt_correct = abs(calculated_pt_g - expected_pt_g) < 0.001
                        pd_correct = abs(calculated_pd_g - expected_pd_g) < 0.001
                        rh_correct = abs(calculated_rh_g - expected_rh_g) < 0.001
                        
                        # Also check if the item has correct catalyst values from listing
                        weight_correct = actual_weight == weight
                        pt_ppm_correct = actual_pt_ppm == pt_ppm
                        pd_ppm_correct = actual_pd_ppm == pd_ppm
                        rh_ppm_correct = actual_rh_ppm == rh_ppm
                        
                        all_correct = pt_correct and pd_correct and rh_correct and weight_correct and pt_ppm_correct and pd_ppm_correct and rh_ppm_correct
                        
                        details = f"Item catalyst values - Weight: {actual_weight}, PT PPM: {actual_pt_ppm}, PD PPM: {actual_pd_ppm}, RH PPM: {actual_rh_ppm}"
                        details += f" | Expected: Weight={weight}, PT PPM={pt_ppm}, PD PPM={pd_ppm}, RH PPM={rh_ppm}"
                        details += f" | Calculated grams - Pt: {calculated_pt_g:.4f}g, Pd: {calculated_pd_g:.4f}g, Rh: {calculated_rh_g:.4f}g"
                        details += f" | Expected grams - Pt: {expected_pt_g:.4f}g, Pd: {expected_pd_g:.4f}g, Rh: {expected_rh_g:.4f}g"
                        
                        self.log_test(
                            "Test Basket Calculation", 
                            all_correct, 
                            details
                        )
                        return all_correct
                    else:
                        self.log_test("Test Basket Calculation", False, "Ford item not found in basket")
                        return False
                else:
                    self.log_test("Test Basket Calculation", False, "Test basket not found")
                    return False
            else:
                self.log_test("Test Basket Calculation", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Test Basket Calculation", False, error_msg=str(e))
            return False

    def run_ford_catalyst_testing(self):
        """Run Ford catalyst values testing as requested in review"""
        print("=" * 80)
        print("FORD LISTING CATALYST VALUES DEBUG TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting Ford catalyst testing.")
            return
        
        # 2. Login Demo User
        print("👤 DEMO USER LOGIN")
        print("-" * 40)
        if not self.login_demo_user():
            print("❌ Failed to login as demo user. Aborting tests.")
            return
        
        # 3. Find Ford Listing
        print("🔍 FIND FORD LISTING")
        print("-" * 40)
        if not self.find_ford_listing():
            print("❌ Failed to find Ford listing. Aborting tests.")
            return
        
        # 4. Check Ford Catalyst Values
        print("🧪 CHECK FORD CATALYST VALUES")
        print("-" * 40)
        values_correct, listing_data = self.check_ford_catalyst_values()
        
        # 5. Fix Ford Catalyst Values if needed
        if not values_correct:
            print("🔧 FIX FORD CATALYST VALUES")
            print("-" * 40)
            if self.fix_ford_catalyst_values():
                # 6. Verify Fix
                print("✅ VERIFY FORD CATALYST FIX")
                print("-" * 40)
                self.verify_ford_catalyst_fix()
        else:
            print("✅ Ford catalyst values are already correct!")
        
        # 7. Test Basket Calculation
        print("🧮 TEST BASKET CALCULATION WITH FORD")
        print("-" * 40)
        self.test_basket_calculation_with_ford()
        
        # Print Summary
        print("=" * 80)
        print("FORD CATALYST TEST SUMMARY")
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
        
        print("\n🎯 FORD CATALYST TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Ford listing should have correct catalyst values (weight: 139.7, pt_ppm: 1394, pd_ppm: 959, rh_ppm: 0)")
        print("  ✅ Basket calculations should show: Pt g: 1.3686, Pd g: 0.9398, Rh g: 0.0000")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = FordCatalystTester()
    
    # Run Ford catalyst testing as requested in the review
    print("🎯 RUNNING FORD LISTING CATALYST VALUES DEBUG TESTING AS REQUESTED")
    print("Checking Ford listing catalyst values and fixing calculations...")
    print()
    
    passed, failed, results = tester.run_ford_catalyst_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)