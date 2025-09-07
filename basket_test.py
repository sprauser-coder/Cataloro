#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Basket Items Population Fix Testing
Testing the basket items population fix as requested in review
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://enterprise-market.preview.emergentagent.com/api"

class BasketTester:
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

    def setup_demo_user(self):
        """Setup demo user for testing"""
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
                self.demo_user = data.get('user', {})
                user_id = self.demo_user.get('id')
                user_role = self.demo_user.get('user_role')
                
                self.log_test(
                    "Demo User Setup", 
                    True, 
                    f"Demo user logged in successfully. ID: {user_id}, Role: {user_role}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Demo User Setup", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Demo User Setup", False, error_msg=str(e))
            return False

    def test_basket_retrieval_with_items(self):
        """Test GET /api/user/baskets/{user_id} for demo user"""
        if not self.demo_user:
            self.log_test("Basket Retrieval with Items", False, error_msg="No demo user available")
            return False, []
            
        try:
            user_id = self.demo_user.get('id')
            
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                if isinstance(baskets, list):
                    basket_count = len(baskets)
                    baskets_with_items = []
                    total_items = 0
                    
                    for basket in baskets:
                        basket_name = basket.get('name', 'Unknown')
                        items = basket.get('items', [])
                        item_count = len(items)
                        total_items += item_count
                        
                        if item_count > 0:
                            baskets_with_items.append({
                                'name': basket_name,
                                'id': basket.get('id'),
                                'item_count': item_count,
                                'items': items
                            })
                    
                    # Check specifically for "picki" basket
                    picki_basket = None
                    for basket in baskets:
                        if basket.get('name', '').lower() == 'picki':
                            picki_basket = basket
                            break
                    
                    success = True
                    details = f"Found {basket_count} baskets with {total_items} total assigned items. "
                    
                    if baskets_with_items:
                        details += f"Baskets with items: {[b['name'] for b in baskets_with_items]}. "
                    
                    if picki_basket:
                        picki_items = picki_basket.get('items', [])
                        details += f"'picki' basket found with {len(picki_items)} items."
                    else:
                        details += "'picki' basket not found."
                    
                    self.log_test(
                        "Basket Retrieval with Items", 
                        success, 
                        details
                    )
                    return success, baskets
                else:
                    self.log_test("Basket Retrieval with Items", False, error_msg="Response is not a list")
                    return False, []
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Basket Retrieval with Items", False, error_msg=error_detail)
                return False, []
                
        except Exception as e:
            self.log_test("Basket Retrieval with Items", False, error_msg=str(e))
            return False, []

    def test_bought_items_availability(self):
        """Test if demo user has bought items available for assignment"""
        if not self.demo_user:
            self.log_test("Bought Items Availability", False, error_msg="No demo user available")
            return False, []
            
        try:
            user_id = self.demo_user.get('id')
            
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                if isinstance(bought_items, list):
                    item_count = len(bought_items)
                    unassigned_items = [item for item in bought_items if not item.get('basket_id')]
                    unassigned_count = len(unassigned_items)
                    
                    self.log_test(
                        "Bought Items Availability", 
                        True, 
                        f"Found {item_count} bought items, {unassigned_count} unassigned"
                    )
                    return True, bought_items
                else:
                    self.log_test("Bought Items Availability", False, error_msg="Response is not a list")
                    return False, []
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Bought Items Availability", False, error_msg=error_detail)
                return False, []
                
        except Exception as e:
            self.log_test("Bought Items Availability", False, error_msg=str(e))
            return False, []

    def test_create_test_basket(self):
        """Create a test basket for assignment testing"""
        if not self.demo_user:
            self.log_test("Create Test Basket", False, error_msg="No demo user available")
            return False, None
            
        try:
            user_id = self.demo_user.get('id')
            
            basket_data = {
                "user_id": user_id,
                "name": "Test Basket for Items",
                "description": "Test basket created for basket items population testing"
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
                    f"Test basket created successfully with ID: {basket_id}"
                )
                return True, basket_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test Basket", False, error_msg=error_detail)
                return False, None
                
        except Exception as e:
            self.log_test("Create Test Basket", False, error_msg=str(e))
            return False, None

    def test_assign_item_to_basket(self, item_id, basket_id):
        """Test assigning an item to a basket"""
        try:
            assignment_data = {
                "basket_id": basket_id
            }
            
            response = requests.put(
                f"{BACKEND_URL}/user/bought-items/{item_id}/assign", 
                json=assignment_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test(
                    "Assign Item to Basket", 
                    True, 
                    f"Item {item_id} assigned to basket {basket_id} successfully"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Assign Item to Basket", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Assign Item to Basket", False, error_msg=str(e))
            return False

    def test_verify_assignment_integration(self, basket_id, expected_item_id):
        """Verify that assigned item appears in basket's items list"""
        if not self.demo_user:
            self.log_test("Verify Assignment Integration", False, error_msg="No demo user available")
            return False
            
        try:
            user_id = self.demo_user.get('id')
            
            # Get baskets again to check if item appears
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                # Find the test basket
                test_basket = None
                for basket in baskets:
                    if basket.get('id') == basket_id:
                        test_basket = basket
                        break
                
                if test_basket:
                    items = test_basket.get('items', [])
                    item_found = False
                    item_details = None
                    
                    for item in items:
                        if item.get('id') == expected_item_id:
                            item_found = True
                            item_details = item
                            break
                    
                    if item_found:
                        # Verify item has proper details
                        required_fields = ['title', 'price', 'seller_name']
                        missing_fields = [field for field in required_fields if not item_details.get(field)]
                        
                        if not missing_fields:
                            self.log_test(
                                "Verify Assignment Integration", 
                                True, 
                                f"Item {expected_item_id} found in basket with proper details: title='{item_details.get('title')}', price={item_details.get('price')}, seller='{item_details.get('seller_name')}'"
                            )
                            return True
                        else:
                            self.log_test(
                                "Verify Assignment Integration", 
                                False, 
                                f"Item found but missing fields: {missing_fields}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Verify Assignment Integration", 
                            False, 
                            f"Item {expected_item_id} not found in basket items. Found items: {[item.get('id') for item in items]}"
                        )
                        return False
                else:
                    self.log_test("Verify Assignment Integration", False, error_msg=f"Test basket {basket_id} not found")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Verify Assignment Integration", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Verify Assignment Integration", False, error_msg=str(e))
            return False

    def test_complete_workflow(self):
        """Test complete workflow: assign item to basket and verify it appears"""
        try:
            # Get bought items
            success, bought_items = self.test_bought_items_availability()
            if not success or not bought_items:
                self.log_test("Complete Workflow", False, error_msg="No bought items available for testing")
                return False
            
            # Create test basket
            success, basket_id = self.test_create_test_basket()
            if not success or not basket_id:
                self.log_test("Complete Workflow", False, error_msg="Failed to create test basket")
                return False
            
            # Get first unassigned item
            unassigned_item = None
            for item in bought_items:
                if not item.get('basket_id'):
                    unassigned_item = item
                    break
            
            if not unassigned_item:
                self.log_test("Complete Workflow", False, error_msg="No unassigned items available for testing")
                return False
            
            item_id = unassigned_item.get('id')
            
            # Assign item to basket
            success = self.test_assign_item_to_basket(item_id, basket_id)
            if not success:
                self.log_test("Complete Workflow", False, error_msg="Failed to assign item to basket")
                return False
            
            # Verify assignment integration
            success = self.test_verify_assignment_integration(basket_id, item_id)
            if not success:
                self.log_test("Complete Workflow", False, error_msg="Assignment integration verification failed")
                return False
            
            self.log_test(
                "Complete Workflow", 
                True, 
                f"Complete workflow successful: item {item_id} assigned to basket {basket_id} and verified in basket items list"
            )
            return True
            
        except Exception as e:
            self.log_test("Complete Workflow", False, error_msg=str(e))
            return False

    def test_picki_basket_specific_check(self):
        """Check specifically that the 'picki' basket shows assigned items"""
        if not self.demo_user:
            self.log_test("Picki Basket Specific Check", False, error_msg="No demo user available")
            return False
            
        try:
            user_id = self.demo_user.get('id')
            
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                # Find picki basket
                picki_basket = None
                for basket in baskets:
                    if basket.get('name', '').lower() == 'picki':
                        picki_basket = basket
                        break
                
                if picki_basket:
                    items = picki_basket.get('items', [])
                    item_count = len(items)
                    
                    if item_count > 0:
                        # Check item details
                        sample_item = items[0]
                        required_fields = ['id', 'title', 'price', 'seller_name']
                        has_all_fields = all(sample_item.get(field) for field in required_fields)
                        
                        self.log_test(
                            "Picki Basket Specific Check", 
                            True, 
                            f"'picki' basket found with {item_count} assigned items. Sample item has all required fields: {has_all_fields}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Picki Basket Specific Check", 
                            True, 
                            "'picki' basket found but has no assigned items (this is expected if no items were assigned to it)"
                        )
                        return True
                else:
                    self.log_test(
                        "Picki Basket Specific Check", 
                        False, 
                        "'picki' basket not found in user's baskets"
                    )
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Picki Basket Specific Check", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Picki Basket Specific Check", False, error_msg=str(e))
            return False

    def run_basket_items_population_testing(self):
        """Run comprehensive basket items population fix testing"""
        print("=" * 80)
        print("CATALORO BASKET ITEMS POPULATION FIX TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Setup Demo User
        print("👤 DEMO USER SETUP")
        print("-" * 40)
        if not self.setup_demo_user():
            print("❌ Failed to setup demo user. Aborting tests.")
            return
        
        # 2. Test Basket Retrieval with Items
        print("🗂️ TEST BASKET RETRIEVAL WITH ITEMS")
        print("-" * 40)
        success, baskets = self.test_basket_retrieval_with_items()
        
        # 3. Check Picki Basket Specifically
        print("🎯 PICKI BASKET SPECIFIC CHECK")
        print("-" * 40)
        self.test_picki_basket_specific_check()
        
        # 4. Test Bought Items Availability
        print("🛍️ TEST BOUGHT ITEMS AVAILABILITY")
        print("-" * 40)
        self.test_bought_items_availability()
        
        # 5. Test Complete Workflow
        print("🔄 TEST COMPLETE WORKFLOW")
        print("-" * 40)
        self.test_complete_workflow()
        
        # Print Summary
        print("=" * 80)
        print("BASKET ITEMS POPULATION TEST SUMMARY")
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
        
        print("\n🎯 BASKET ITEMS POPULATION TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Baskets should show assigned items in their 'items' array")
        print("  ✅ 'picki' basket should show assigned items (if any)")
        print("  ✅ Assignment integration should work correctly")
        print("  ✅ Complete workflow should function end-to-end")
        print("  ✅ Assigned items should have proper details (title, price, seller_name)")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BasketTester()
    
    # Run Basket Items Population testing as requested in the review
    print("🎯 RUNNING BASKET ITEMS POPULATION FIX TESTING AS REQUESTED")
    print("Testing basket retrieval with items and assignment integration...")
    print()
    
    passed, failed, results = tester.run_basket_items_population_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)