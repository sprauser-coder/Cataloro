#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Comprehensive Basket Cat Database Fields Testing
Testing basket functionality with cat database fields for calculations including assignment
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://mega-dashboard.preview.emergentagent.com/api"

class ComprehensiveBasketTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
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
        """Login as demo user and get user data"""
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
                self.demo_user = user
                self.log_test(
                    "Demo User Login", 
                    True, 
                    f"Logged in as {user.get('username', 'Unknown')} (ID: {user.get('id')})"
                )
                return user
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Demo User Login", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Demo User Login", False, error_msg=str(e))
            return None

    def test_get_user_baskets_with_cat_fields(self, user_id):
        """Test GET /api/user/baskets/{user_id} and verify cat database fields"""
        try:
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                if not isinstance(baskets, list):
                    self.log_test(
                        "Get User Baskets Structure", 
                        False, 
                        error_msg="Response is not a list"
                    )
                    return False, []
                
                # Check if we have baskets with items
                baskets_with_items = [b for b in baskets if b.get('items', [])]
                
                if not baskets_with_items:
                    self.log_test(
                        "Get User Baskets with Cat Fields", 
                        True, 
                        f"Found {len(baskets)} baskets, but no baskets have assigned items to test cat fields"
                    )
                    return True, baskets
                
                # Test cat fields in assigned items
                cat_fields_found = 0
                total_items = 0
                missing_fields = []
                field_details = []
                
                for basket in baskets_with_items:
                    basket_name = basket.get('name', 'Unknown')
                    items = basket.get('items', [])
                    
                    for item in items:
                        total_items += 1
                        required_cat_fields = [
                            'weight', 'pt_ppm', 'pd_ppm', 'rh_ppm',
                            'renumeration_pt', 'renumeration_pd', 'renumeration_rh'
                        ]
                        
                        item_has_all_fields = True
                        item_field_values = {}
                        for field in required_cat_fields:
                            if field not in item or item[field] is None:
                                missing_fields.append(f"Item {item.get('id', 'Unknown')} missing {field}")
                                item_has_all_fields = False
                            else:
                                item_field_values[field] = item[field]
                        
                        if item_has_all_fields:
                            cat_fields_found += 1
                            field_details.append(f"Item '{item.get('title', 'Unknown')}': weight={item_field_values.get('weight')}, pt_ppm={item_field_values.get('pt_ppm')}, pd_ppm={item_field_values.get('pd_ppm')}, rh_ppm={item_field_values.get('rh_ppm')}")
                
                success = cat_fields_found == total_items
                details = f"Found {len(baskets)} baskets, {len(baskets_with_items)} with items. {cat_fields_found}/{total_items} items have all cat fields"
                if field_details:
                    details += f". Sample fields: {field_details[0]}"
                
                self.log_test(
                    "Get User Baskets with Cat Fields", 
                    success, 
                    details,
                    "; ".join(missing_fields[:3]) if missing_fields and not success else ""
                )
                return success, baskets
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Get User Baskets with Cat Fields", False, error_msg=error_detail)
                return False, []
                
        except Exception as e:
            self.log_test("Get User Baskets with Cat Fields", False, error_msg=str(e))
            return False, []

    def test_verify_calculation_fields_values(self, baskets):
        """Verify that calculation fields have non-zero values and renumeration comes from price settings"""
        try:
            if not baskets:
                self.log_test(
                    "Verify Calculation Fields Values", 
                    True, 
                    "No baskets to test calculation fields"
                )
                return True
            
            # Get price settings to verify renumeration values
            try:
                price_settings_response = requests.get(f"{BACKEND_URL}/admin/catalyst/price-settings", timeout=10)
                price_settings = {}
                if price_settings_response.status_code == 200:
                    price_settings = price_settings_response.json()
            except:
                price_settings = {}
            
            expected_renumeration_pt = price_settings.get('renumeration_pt', 0.98)
            expected_renumeration_pd = price_settings.get('renumeration_pd', 0.98)
            expected_renumeration_rh = price_settings.get('renumeration_rh', 0.9)
            
            items_with_items = []
            for basket in baskets:
                items_with_items.extend(basket.get('items', []))
            
            if not items_with_items:
                self.log_test(
                    "Verify Calculation Fields Values", 
                    True, 
                    "No assigned items found to test calculation field values"
                )
                return True
            
            non_zero_fields = 0
            correct_renumeration = 0
            total_items = len(items_with_items)
            field_issues = []
            
            for item in items_with_items:
                item_id = item.get('id', 'Unknown')
                
                # Check non-zero values for calculation fields
                calc_fields = ['weight', 'pt_ppm', 'pd_ppm', 'rh_ppm']
                has_non_zero = all(
                    item.get(field, 0) > 0 for field in calc_fields
                )
                if has_non_zero:
                    non_zero_fields += 1
                else:
                    zero_fields = [f for f in calc_fields if item.get(f, 0) <= 0]
                    field_issues.append(f"Item {item_id} has zero values in: {', '.join(zero_fields)}")
                
                # Check renumeration values match price settings
                renumeration_correct = (
                    item.get('renumeration_pt') == expected_renumeration_pt and
                    item.get('renumeration_pd') == expected_renumeration_pd and
                    item.get('renumeration_rh') == expected_renumeration_rh
                )
                if renumeration_correct:
                    correct_renumeration += 1
                else:
                    field_issues.append(
                        f"Item {item_id} renumeration mismatch: "
                        f"Pt={item.get('renumeration_pt')} (expected {expected_renumeration_pt}), "
                        f"Pd={item.get('renumeration_pd')} (expected {expected_renumeration_pd}), "
                        f"Rh={item.get('renumeration_rh')} (expected {expected_renumeration_rh})"
                    )
            
            success = non_zero_fields == total_items and correct_renumeration == total_items
            details = (
                f"Tested {total_items} items. "
                f"Non-zero calculation fields: {non_zero_fields}/{total_items}. "
                f"Correct renumeration values: {correct_renumeration}/{total_items}. "
                f"Expected renumeration: Pt={expected_renumeration_pt}, Pd={expected_renumeration_pd}, Rh={expected_renumeration_rh}"
            )
            
            self.log_test(
                "Verify Calculation Fields Values", 
                success, 
                details,
                "; ".join(field_issues[:2]) if field_issues and not success else ""
            )
            return success
            
        except Exception as e:
            self.log_test("Verify Calculation Fields Values", False, error_msg=str(e))
            return False

    def test_create_basket_for_assignment_test(self, user_id):
        """Create a test basket for assignment testing"""
        try:
            basket_data = {
                "user_id": user_id,
                "name": f"Test Basket for Cat Fields {datetime.now().strftime('%H:%M:%S')}",
                "description": "Test basket for verifying cat database fields in assignments"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/baskets",
                json=basket_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                basket_id = data.get('basket_id')
                self.log_test(
                    "Create Test Basket", 
                    True, 
                    f"Created test basket with ID: {basket_id}"
                )
                return basket_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test Basket", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Create Test Basket", False, error_msg=str(e))
            return None

    def test_get_bought_items_for_assignment(self, user_id):
        """Get bought items to find one for assignment testing"""
        try:
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                if not isinstance(bought_items, list):
                    self.log_test(
                        "Get Bought Items for Assignment", 
                        False, 
                        error_msg="Response is not a list"
                    )
                    return None
                
                # Find an unassigned item (no basket_id)
                unassigned_items = [item for item in bought_items if not item.get('basket_id')]
                
                if unassigned_items:
                    test_item = unassigned_items[0]
                    self.log_test(
                        "Get Bought Items for Assignment", 
                        True, 
                        f"Found {len(bought_items)} bought items, {len(unassigned_items)} unassigned. Using item: {test_item.get('title', 'Unknown')} (ID: {test_item.get('id')})"
                    )
                    return test_item
                else:
                    self.log_test(
                        "Get Bought Items for Assignment", 
                        True, 
                        f"Found {len(bought_items)} bought items, but all are already assigned to baskets"
                    )
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Get Bought Items for Assignment", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Get Bought Items for Assignment", False, error_msg=str(e))
            return None

    def test_assign_item_and_verify_cat_fields(self, item_id, basket_id, user_id):
        """Assign an item to basket and verify it has cat database fields"""
        try:
            # Assign item to basket
            assignment_data = {"basket_id": basket_id}
            
            response = requests.put(
                f"{BACKEND_URL}/user/bought-items/{item_id}/assign",
                json=assignment_data,
                timeout=10
            )
            
            if response.status_code != 200:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Assign Item and Verify Cat Fields", False, error_msg=f"Assignment failed: {error_detail}")
                return False
            
            # Wait a moment for assignment to be processed
            time.sleep(1)
            
            # Get baskets again to verify the assignment and cat fields
            baskets_response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if baskets_response.status_code != 200:
                self.log_test("Assign Item and Verify Cat Fields", False, error_msg="Failed to retrieve baskets after assignment")
                return False
            
            baskets = baskets_response.json()
            
            # Find the test basket and the assigned item
            test_basket = None
            for basket in baskets:
                if basket.get('id') == basket_id:
                    test_basket = basket
                    break
            
            if not test_basket:
                self.log_test("Assign Item and Verify Cat Fields", False, error_msg="Test basket not found after assignment")
                return False
            
            # Find the assigned item
            assigned_item = None
            for item in test_basket.get('items', []):
                if item.get('id') == item_id:
                    assigned_item = item
                    break
            
            if not assigned_item:
                self.log_test("Assign Item and Verify Cat Fields", False, error_msg="Assigned item not found in basket")
                return False
            
            # Verify cat database fields are present and populated
            required_cat_fields = [
                'weight', 'pt_ppm', 'pd_ppm', 'rh_ppm',
                'renumeration_pt', 'renumeration_pd', 'renumeration_rh'
            ]
            
            missing_fields = []
            field_values = {}
            
            for field in required_cat_fields:
                if field not in assigned_item or assigned_item[field] is None:
                    missing_fields.append(field)
                else:
                    field_values[field] = assigned_item[field]
            
            success = len(missing_fields) == 0
            details = f"Assigned item '{assigned_item.get('title', 'Unknown')}' to basket. Cat fields: weight={field_values.get('weight')}, pt_ppm={field_values.get('pt_ppm')}, pd_ppm={field_values.get('pd_ppm')}, rh_ppm={field_values.get('rh_ppm')}, renumeration_pt={field_values.get('renumeration_pt')}, renumeration_pd={field_values.get('renumeration_pd')}, renumeration_rh={field_values.get('renumeration_rh')}"
            
            self.log_test(
                "Assign Item and Verify Cat Fields", 
                success, 
                details,
                f"Missing fields: {', '.join(missing_fields)}" if missing_fields else ""
            )
            return success
            
        except Exception as e:
            self.log_test("Assign Item and Verify Cat Fields", False, error_msg=str(e))
            return False

    def cleanup_test_basket(self, basket_id):
        """Clean up the test basket"""
        try:
            response = requests.delete(f"{BACKEND_URL}/user/baskets/{basket_id}", timeout=10)
            if response.status_code == 200:
                print(f"✅ Cleaned up test basket: {basket_id}")
            else:
                print(f"⚠️  Failed to clean up test basket: {basket_id}")
        except Exception as e:
            print(f"⚠️  Error cleaning up test basket: {e}")

    def run_comprehensive_basket_testing(self):
        """Run comprehensive basket cat database fields testing"""
        print("=" * 80)
        print("CATALORO COMPREHENSIVE BASKET CAT DATABASE FIELDS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting basket testing.")
            return
        
        # 2. Get Demo User
        print("👤 DEMO USER LOGIN")
        print("-" * 40)
        demo_user = self.get_demo_user()
        if not demo_user:
            print("❌ Failed to login as demo user. Aborting tests.")
            return
        
        user_id = demo_user.get('id')
        
        # 3. Test Basket Items with Cat Fields
        print("🧺 TEST BASKET ITEMS WITH CAT FIELDS")
        print("-" * 40)
        baskets_success, baskets = self.test_get_user_baskets_with_cat_fields(user_id)
        
        # 4. Verify Calculation Fields
        print("🧮 VERIFY CALCULATION FIELDS")
        print("-" * 40)
        self.test_verify_calculation_fields_values(baskets)
        
        # 5. Test Assignment with Cat Fields
        print("📦 TEST ASSIGNMENT WITH CAT FIELDS")
        print("-" * 40)
        
        # Create test basket
        test_basket_id = self.test_create_basket_for_assignment_test(user_id)
        
        if test_basket_id:
            # Get bought items for assignment
            test_item = self.test_get_bought_items_for_assignment(user_id)
            
            if test_item:
                # Test assignment and cat fields
                assignment_success = self.test_assign_item_and_verify_cat_fields(
                    test_item.get('id'), 
                    test_basket_id, 
                    user_id
                )
                
                if assignment_success:
                    print("✅ Assignment with cat fields test completed successfully")
                else:
                    print("❌ Assignment with cat fields test failed")
            else:
                print("⚠️  No unassigned bought items found for assignment testing")
            
            # Clean up test basket
            self.cleanup_test_basket(test_basket_id)
        else:
            print("❌ Failed to create test basket for assignment testing")
        
        # Print Summary
        print("=" * 80)
        print("COMPREHENSIVE BASKET CAT DATABASE FIELDS TEST SUMMARY")
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
        
        print("\n🎯 COMPREHENSIVE BASKET CAT DATABASE FIELDS TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Basket items should include cat database fields (weight, pt_ppm, pd_ppm, rh_ppm)")
        print("  ✅ Basket items should include renumeration fields from price settings")
        print("  ✅ Calculation fields should have non-zero values")
        print("  ✅ Assigned items should have all cat database fields populated")
        print("  ✅ Assignment functionality should work with cat fields")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = ComprehensiveBasketTester()
    
    print("🎯 RUNNING COMPREHENSIVE BASKET CAT DATABASE FIELDS TESTING AS REQUESTED")
    print("Testing basket calculations with cat database fields including assignment...")
    print()
    
    passed, failed, results = tester.run_comprehensive_basket_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)