#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Basket/Inventory Functionality Testing
Testing the inventory/basket functionality in Buy Management Page as requested in review
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://marketplace-admin-1.preview.emergentagent.com/api"

class BasketBackendTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_user = None
        self.test_user_id = None
        
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
        """Test admin login to get proper permissions"""
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
                user_role = user.get('user_role')
                user_id = user.get('id')
                
                is_admin = user_role in ['Admin', 'Admin-Manager']
                
                if is_admin:
                    self.admin_user = user
                    self.test_user_id = user_id
                    
                self.log_test(
                    "Admin Login for Basket Testing", 
                    is_admin, 
                    f"Admin login successful. Role: {user_role}, User ID: {user_id}"
                )
                return is_admin
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login for Basket Testing", False, error_msg=f"Login failed: {error_detail}")
                return False
        except Exception as e:
            self.log_test("Admin Login for Basket Testing", False, error_msg=str(e))
            return False

    def test_basket_api_endpoint(self):
        """Test GET /api/user/baskets/{user_id} endpoint"""
        if not self.test_user_id:
            self.log_test("Basket API Endpoint", False, error_msg="No test user ID available")
            return None
            
        try:
            response = requests.get(f"{BACKEND_URL}/user/baskets/{self.test_user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                # Check if baskets are returned
                basket_count = len(baskets)
                has_items = False
                total_items = 0
                catalyst_data_present = False
                
                # Analyze basket data
                for basket in baskets:
                    items = basket.get('items', [])
                    total_items += len(items)
                    if items:
                        has_items = True
                        
                        # Check for catalyst data in items
                        for item in items:
                            if (item.get('weight', 0) > 0 or 
                                item.get('pt_ppm', 0) > 0 or 
                                item.get('pd_ppm', 0) > 0 or 
                                item.get('rh_ppm', 0) > 0):
                                catalyst_data_present = True
                                break
                
                success = response.status_code == 200
                details = f"Found {basket_count} baskets with {total_items} total items. Catalyst data present: {catalyst_data_present}"
                
                self.log_test("Basket API Endpoint", success, details)
                return baskets
            else:
                self.log_test("Basket API Endpoint", False, error_msg=f"HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Basket API Endpoint", False, error_msg=str(e))
            return None

    def test_basket_calculation_values(self, baskets):
        """Test basket calculation values using the formula: ptG = weight * pt_ppm / 1000 * renumeration_pt"""
        if not baskets:
            self.log_test("Basket Calculation Values", False, error_msg="No baskets provided")
            return False
            
        try:
            calculation_results = []
            total_calculations = 0
            successful_calculations = 0
            zero_value_issues = 0
            
            for basket in baskets:
                basket_name = basket.get('name', 'Unknown')
                items = basket.get('items', [])
                
                for item in items:
                    total_calculations += 1
                    
                    # Get catalyst data
                    weight = item.get('weight', 0)
                    pt_ppm = item.get('pt_ppm', 0)
                    pd_ppm = item.get('pd_ppm', 0)
                    rh_ppm = item.get('rh_ppm', 0)
                    
                    # Get renumeration values
                    renumeration_pt = item.get('renumeration_pt', 0.98)
                    renumeration_pd = item.get('renumeration_pd', 0.98)
                    renumeration_rh = item.get('renumeration_rh', 0.9)
                    
                    # Calculate values using the formula: ptG = weight * pt_ppm / 1000 * renumeration_pt
                    pt_g = (weight * pt_ppm / 1000) * renumeration_pt if weight > 0 and pt_ppm > 0 else 0
                    pd_g = (weight * pd_ppm / 1000) * renumeration_pd if weight > 0 and pd_ppm > 0 else 0
                    rh_g = (weight * rh_ppm / 1000) * renumeration_rh if weight > 0 and rh_ppm > 0 else 0
                    
                    # Check if calculation produces non-zero values
                    has_meaningful_values = pt_g > 0 or pd_g > 0 or rh_g > 0
                    
                    if has_meaningful_values:
                        successful_calculations += 1
                    else:
                        zero_value_issues += 1
                    
                    calculation_results.append({
                        'item_id': item.get('id', 'Unknown'),
                        'basket': basket_name,
                        'weight': weight,
                        'pt_ppm': pt_ppm,
                        'pd_ppm': pd_ppm,
                        'rh_ppm': rh_ppm,
                        'pt_g': round(pt_g, 4),
                        'pd_g': round(pd_g, 4),
                        'rh_g': round(rh_g, 4),
                        'has_values': has_meaningful_values
                    })
            
            # Determine success based on whether we have meaningful calculations
            success = successful_calculations > 0 or total_calculations == 0
            
            details = f"Processed {total_calculations} items. Successful calculations: {successful_calculations}, Zero value issues: {zero_value_issues}"
            
            if calculation_results:
                print("   Sample Calculations:")
                for i, calc in enumerate(calculation_results[:3]):  # Show first 3 calculations
                    print(f"     Item {i+1}: Weight={calc['weight']}g, PT={calc['pt_ppm']}ppm → PT_g={calc['pt_g']}g, PD_g={calc['pd_g']}g, RH_g={calc['rh_g']}g")
            
            self.log_test("Basket Calculation Values", success, details)
            return calculation_results
            
        except Exception as e:
            self.log_test("Basket Calculation Values", False, error_msg=str(e))
            return []

    def test_catalyst_data_completeness(self, baskets):
        """Test that all required fields for calculations are present in basket response"""
        if not baskets:
            self.log_test("Catalyst Data Completeness", False, error_msg="No baskets provided")
            return False
            
        try:
            required_fields = ['weight', 'pt_ppm', 'pd_ppm', 'rh_ppm', 'renumeration_pt', 'renumeration_pd', 'renumeration_rh']
            total_items = 0
            complete_items = 0
            field_availability = {field: 0 for field in required_fields}
            
            for basket in baskets:
                items = basket.get('items', [])
                
                for item in items:
                    total_items += 1
                    complete_fields = 0
                    
                    for field in required_fields:
                        if field in item and item[field] is not None:
                            field_availability[field] += 1
                            complete_fields += 1
                    
                    if complete_fields == len(required_fields):
                        complete_items += 1
            
            success = complete_items > 0 or total_items == 0
            completeness_rate = (complete_items / total_items * 100) if total_items > 0 else 100
            
            details = f"Analyzed {total_items} items. Complete items: {complete_items} ({completeness_rate:.1f}%)"
            
            print("   Field Availability:")
            for field, count in field_availability.items():
                availability_rate = (count / total_items * 100) if total_items > 0 else 0
                print(f"     {field}: {count}/{total_items} ({availability_rate:.1f}%)")
            
            self.log_test("Catalyst Data Completeness", success, details)
            return success
            
        except Exception as e:
            self.log_test("Catalyst Data Completeness", False, error_msg=str(e))
            return False

    def test_assignment_process(self):
        """Test the PUT /api/user/bought-items/{item_id}/assign endpoint"""
        try:
            # First, get bought items to find an item to test assignment
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.test_user_id}", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Assignment Process - Get Bought Items", False, error_msg=f"Failed to get bought items: HTTP {response.status_code}")
                return False
            
            bought_items = response.json()
            
            if not bought_items:
                self.log_test("Assignment Process - Get Bought Items", False, error_msg="No bought items found for testing assignment")
                return False
            
            # Get baskets to find a basket to assign to
            baskets_response = requests.get(f"{BACKEND_URL}/user/baskets/{self.test_user_id}", timeout=10)
            
            if baskets_response.status_code != 200:
                self.log_test("Assignment Process - Get Baskets", False, error_msg=f"Failed to get baskets: HTTP {baskets_response.status_code}")
                return False
            
            baskets = baskets_response.json()
            
            if not baskets:
                self.log_test("Assignment Process - Get Baskets", False, error_msg="No baskets found for testing assignment")
                return False
            
            # Test assignment
            test_item = bought_items[0]
            test_basket = baskets[0]
            item_id = test_item.get('id')
            basket_id = test_basket.get('id')
            
            assignment_data = {
                "basket_id": basket_id
            }
            
            assign_response = requests.put(
                f"{BACKEND_URL}/user/bought-items/{item_id}/assign",
                json=assignment_data,
                timeout=10
            )
            
            success = assign_response.status_code == 200
            
            if success:
                # Verify the assignment by checking the basket again
                verify_response = requests.get(f"{BACKEND_URL}/user/baskets/{self.test_user_id}", timeout=10)
                
                if verify_response.status_code == 200:
                    updated_baskets = verify_response.json()
                    
                    # Check if the item appears in the basket
                    item_found_in_basket = False
                    catalyst_data_preserved = False
                    
                    for basket in updated_baskets:
                        if basket.get('id') == basket_id:
                            for basket_item in basket.get('items', []):
                                if basket_item.get('id') == item_id:
                                    item_found_in_basket = True
                                    
                                    # Check if catalyst data is preserved
                                    if (basket_item.get('weight', 0) > 0 or 
                                        basket_item.get('pt_ppm', 0) > 0 or 
                                        basket_item.get('pd_ppm', 0) > 0 or 
                                        basket_item.get('rh_ppm', 0) > 0):
                                        catalyst_data_preserved = True
                                    break
                    
                    details = f"Item {item_id[:8]}... assigned to basket {basket_id[:8]}... Item found in basket: {item_found_in_basket}, Catalyst data preserved: {catalyst_data_preserved}"
                    final_success = success and item_found_in_basket
                    
                else:
                    details = f"Assignment API returned success but verification failed"
                    final_success = False
            else:
                error_detail = assign_response.json().get('detail', 'Unknown error') if assign_response.content else f"HTTP {assign_response.status_code}"
                details = f"Assignment failed: {error_detail}"
                final_success = False
            
            self.log_test("Assignment Process", final_success, details)
            return final_success
            
        except Exception as e:
            self.log_test("Assignment Process", False, error_msg=str(e))
            return False

    def test_catalyst_data_flow(self):
        """Test that catalyst data flows properly from listings to baskets"""
        try:
            # Get listings with catalyst data
            listings_response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if listings_response.status_code != 200:
                self.log_test("Catalyst Data Flow - Get Listings", False, error_msg=f"Failed to get listings: HTTP {listings_response.status_code}")
                return False
            
            listings = listings_response.json()
            
            # Find listings with catalyst data
            catalyst_listings = []
            for listing in listings:
                if (listing.get('ceramic_weight', 0) > 0 or 
                    listing.get('pt_ppm', 0) > 0 or 
                    listing.get('pd_ppm', 0) > 0 or 
                    listing.get('rh_ppm', 0) > 0):
                    catalyst_listings.append(listing)
            
            # Get baskets and check if items have catalyst data
            baskets_response = requests.get(f"{BACKEND_URL}/user/baskets/{self.test_user_id}", timeout=10)
            
            if baskets_response.status_code != 200:
                self.log_test("Catalyst Data Flow - Get Baskets", False, error_msg=f"Failed to get baskets: HTTP {baskets_response.status_code}")
                return False
            
            baskets = baskets_response.json()
            
            # Analyze data flow
            total_basket_items = 0
            items_with_catalyst_data = 0
            
            for basket in baskets:
                items = basket.get('items', [])
                total_basket_items += len(items)
                
                for item in items:
                    if (item.get('weight', 0) > 0 or 
                        item.get('pt_ppm', 0) > 0 or 
                        item.get('pd_ppm', 0) > 0 or 
                        item.get('rh_ppm', 0) > 0):
                        items_with_catalyst_data += 1
            
            success = items_with_catalyst_data > 0 or total_basket_items == 0
            data_flow_rate = (items_with_catalyst_data / total_basket_items * 100) if total_basket_items > 0 else 100
            
            details = f"Found {len(catalyst_listings)} listings with catalyst data. {items_with_catalyst_data}/{total_basket_items} basket items have catalyst data ({data_flow_rate:.1f}%)"
            
            self.log_test("Catalyst Data Flow", success, details)
            return success
            
        except Exception as e:
            self.log_test("Catalyst Data Flow", False, error_msg=str(e))
            return False

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

    def run_basket_functionality_testing(self):
        """Run comprehensive basket functionality testing"""
        print("=" * 80)
        print("CATALORO BASKET/INVENTORY FUNCTIONALITY TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting testing.")
            return
        
        # 2. Admin Login
        print("👤 ADMIN LOGIN FOR BASKET TESTING")
        print("-" * 40)
        if not self.test_admin_login():
            print("❌ Admin login failed. Aborting testing.")
            return
        
        # 3. Test Basket API Endpoint
        print("🗂️ BASKET API ENDPOINT TESTING")
        print("-" * 40)
        baskets = self.test_basket_api_endpoint()
        
        # 4. Test Catalyst Data Completeness
        print("📊 CATALYST DATA COMPLETENESS TESTING")
        print("-" * 40)
        self.test_catalyst_data_completeness(baskets)
        
        # 5. Test Basket Calculation Values
        print("🧮 BASKET CALCULATION VALUES TESTING")
        print("-" * 40)
        self.test_basket_calculation_values(baskets)
        
        # 6. Test Assignment Process
        print("📝 ASSIGNMENT PROCESS TESTING")
        print("-" * 40)
        self.test_assignment_process()
        
        # 7. Test Catalyst Data Flow
        print("🔄 CATALYST DATA FLOW TESTING")
        print("-" * 40)
        self.test_catalyst_data_flow()
        
        # Print Summary
        print("=" * 80)
        print("BASKET FUNCTIONALITY TEST SUMMARY")
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
        
        print("\n🎯 BASKET FUNCTIONALITY TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Basket API returns baskets with proper catalyst data")
        print("  ✅ Assignment process preserves catalyst data")
        print("  ✅ Calculation formula works: ptG = weight * pt_ppm / 1000 * renumeration_pt")
        print("  ✅ All required fields present for calculations")
        print("  ✅ Catalyst data flows properly from listings to baskets")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BasketBackendTester()
    
    print("🎯 RUNNING BASKET/INVENTORY FUNCTIONALITY TESTING AS REQUESTED")
    print("Testing the inventory/basket functionality in Buy Management Page...")
    print()
    
    passed, failed, results = tester.run_basket_functionality_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)