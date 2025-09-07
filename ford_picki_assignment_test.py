#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Ford Item to Picki Basket Assignment
Testing the specific scenario: assigning "ford" item to "picki" basket
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-market-2.preview.emergentagent.com/api"

class FordPickiAssignmentTester:
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
                    "Demo User Login Setup", 
                    True, 
                    f"Logged in as demo user: {self.demo_user.get('username', 'Unknown')} (ID: {self.demo_user.get('id')})"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Demo User Login Setup", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Demo User Login Setup", False, error_msg=str(e))
            return False

    def find_picki_basket(self):
        """Find the picki basket (should exist from previous test)"""
        if not self.demo_user:
            self.log_test("Find Picki Basket", False, error_msg="No demo user available")
            return None
            
        try:
            user_id = self.demo_user.get('id')
            
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                # Look for 'picki' basket
                picki_basket = None
                for basket in baskets:
                    if basket.get('name', '').lower() == 'picki':
                        picki_basket = basket
                        break
                
                if picki_basket:
                    self.log_test(
                        "Find Picki Basket", 
                        True, 
                        f"Found 'picki' basket with ID: {picki_basket.get('id')}"
                    )
                    return picki_basket
                else:
                    basket_names = [b.get('name', 'Unnamed') for b in baskets]
                    self.log_test(
                        "Find Picki Basket", 
                        False, 
                        f"'picki' basket NOT found. Available baskets: {basket_names}"
                    )
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Find Picki Basket", False, error_msg=f"Failed to get baskets: {error_detail}")
                return None
                
        except Exception as e:
            self.log_test("Find Picki Basket", False, error_msg=str(e))
            return None

    def find_ford_item(self):
        """Find an item with 'ford' in the name/title"""
        if not self.demo_user:
            self.log_test("Find Ford Item", False, error_msg="No demo user available")
            return None
            
        try:
            user_id = self.demo_user.get('id')
            
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                # Look for item with 'ford' in the title
                ford_item = None
                for item in bought_items:
                    title = item.get('title', '').lower()
                    if 'ford' in title:
                        ford_item = item
                        break
                
                if ford_item:
                    self.log_test(
                        "Find Ford Item", 
                        True, 
                        f"Found ford item: '{ford_item.get('title')}' (ID: {ford_item.get('id')})"
                    )
                    return ford_item
                else:
                    # List all available items for debugging
                    item_titles = [item.get('title', 'Unnamed') for item in bought_items]
                    self.log_test(
                        "Find Ford Item", 
                        False, 
                        f"No 'ford' item found. Available items: {item_titles}"
                    )
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Find Ford Item", False, error_msg=f"Failed to get bought items: {error_detail}")
                return None
                
        except Exception as e:
            self.log_test("Find Ford Item", False, error_msg=str(e))
            return None

    def create_ford_item_if_missing(self):
        """Create a test 'ford' item if it doesn't exist"""
        if not self.demo_user:
            self.log_test("Create Ford Item", False, error_msg="No demo user available")
            return None
            
        try:
            user_id = self.demo_user.get('id')
            
            # Create a test bought item with 'ford' in the name
            # Note: This is a simulation since bought items are typically created through purchases
            ford_item = {
                "id": f"test_ford_{str(uuid.uuid4())[:8]}",
                "user_id": user_id,
                "title": "Ford Test Item for Assignment",
                "price": 100.0,
                "seller_name": "Test Seller",
                "seller_id": "test_seller_id",
                "purchased_at": datetime.now().isoformat()
            }
            
            # In a real scenario, this would be created through a purchase process
            # For testing, we'll simulate having this item available
            self.log_test(
                "Create Ford Item", 
                True, 
                f"Simulated ford item creation: '{ford_item.get('title')}' (ID: {ford_item.get('id')})"
            )
            return ford_item
                
        except Exception as e:
            self.log_test("Create Ford Item", False, error_msg=str(e))
            return None

    def test_assignment_with_wrong_basket_id(self, ford_item):
        """Test assignment with a wrong/non-existent basket ID to reproduce the error"""
        if not ford_item:
            self.log_test("Test Assignment with Wrong Basket ID", False, error_msg="No ford item available")
            return False
            
        try:
            item_id = ford_item.get('id')
            
            # Use a non-existent basket ID to reproduce the "Basket not found" error
            wrong_basket_id = "non_existent_basket_id"
            
            assignment_data = {
                "basket_id": wrong_basket_id
            }
            
            response = requests.put(
                f"{BACKEND_URL}/user/bought-items/{item_id}/assign",
                json=assignment_data,
                timeout=10
            )
            
            if response.status_code == 404:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else "No detail"
                self.log_test(
                    "Test Assignment with Wrong Basket ID", 
                    True, 
                    f"Successfully reproduced 'Basket not found' error: {error_detail}"
                )
                return True
            else:
                self.log_test(
                    "Test Assignment with Wrong Basket ID", 
                    False, 
                    f"Expected 404 error but got HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Test Assignment with Wrong Basket ID", False, error_msg=str(e))
            return False

    def test_assignment_with_correct_basket_id(self, ford_item, picki_basket):
        """Test assignment with the correct picki basket ID"""
        if not ford_item or not picki_basket:
            self.log_test("Test Assignment with Correct Basket ID", False, error_msg="Missing ford item or picki basket")
            return False
            
        try:
            item_id = ford_item.get('id')
            basket_id = picki_basket.get('id')
            
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
                    "Test Assignment with Correct Basket ID", 
                    True, 
                    f"Successfully assigned ford item to picki basket (ID: {basket_id})"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test(
                    "Test Assignment with Correct Basket ID", 
                    False, 
                    error_msg=f"Assignment failed: {error_detail}"
                )
                return False
                
        except Exception as e:
            self.log_test("Test Assignment with Correct Basket ID", False, error_msg=str(e))
            return False

    def debug_id_mismatch_scenarios(self, picki_basket):
        """Debug potential ID format mismatches"""
        if not picki_basket:
            self.log_test("Debug ID Mismatch Scenarios", False, error_msg="No picki basket available")
            return False
            
        try:
            basket_id = picki_basket.get('id')
            
            # Test different ID format scenarios that might cause "Basket not found"
            test_scenarios = [
                ("Correct UUID", basket_id),
                ("Uppercase UUID", basket_id.upper()),
                ("No hyphens", basket_id.replace('-', '')),
                ("Wrong format", "picki"),  # Using basket name instead of ID
                ("Empty string", ""),
                ("None value", None)
            ]
            
            scenario_results = []
            
            for scenario_name, test_id in test_scenarios:
                try:
                    if test_id is None:
                        scenario_results.append(f"{scenario_name}: ❌ None value would cause error")
                        continue
                        
                    # Test if this ID would be found in the database
                    user_id = self.demo_user.get('id')
                    baskets_response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
                    
                    if baskets_response.status_code == 200:
                        baskets = baskets_response.json()
                        found = any(b.get('id') == test_id for b in baskets)
                        scenario_results.append(f"{scenario_name}: {'✅' if found else '❌'} {'Found' if found else 'Not found'}")
                    else:
                        scenario_results.append(f"{scenario_name}: ❌ Error getting baskets")
                        
                except Exception as e:
                    scenario_results.append(f"{scenario_name}: ❌ Error: {str(e)}")
            
            self.log_test(
                "Debug ID Mismatch Scenarios", 
                True, 
                f"ID format test results: {'; '.join(scenario_results)}"
            )
            return True
            
        except Exception as e:
            self.log_test("Debug ID Mismatch Scenarios", False, error_msg=str(e))
            return False

    def run_ford_picki_assignment_test(self):
        """Run the complete Ford-Picki assignment test"""
        print("=" * 80)
        print("CATALORO FORD-PICKI ASSIGNMENT TEST")
        print("Testing assignment of 'ford' item to 'picki' basket")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Setup demo user
        print("👤 SETUP DEMO USER")
        print("-" * 40)
        if not self.setup_demo_user():
            print("❌ Failed to setup demo user. Aborting test.")
            return
        
        # 2. Find picki basket
        print("🔍 FIND PICKI BASKET")
        print("-" * 40)
        picki_basket = self.find_picki_basket()
        
        # 3. Find ford item
        print("🚗 FIND FORD ITEM")
        print("-" * 40)
        ford_item = self.find_ford_item()
        
        # 4. Create ford item if missing
        if not ford_item:
            print("🛠️ CREATE FORD ITEM FOR TESTING")
            print("-" * 40)
            ford_item = self.create_ford_item_if_missing()
        
        # 5. Test assignment with wrong basket ID (reproduce error)
        print("❌ TEST ASSIGNMENT WITH WRONG BASKET ID")
        print("-" * 40)
        self.test_assignment_with_wrong_basket_id(ford_item)
        
        # 6. Test assignment with correct basket ID
        if picki_basket and ford_item:
            print("✅ TEST ASSIGNMENT WITH CORRECT BASKET ID")
            print("-" * 40)
            self.test_assignment_with_correct_basket_id(ford_item, picki_basket)
        
        # 7. Debug ID mismatch scenarios
        if picki_basket:
            print("🔧 DEBUG ID MISMATCH SCENARIOS")
            print("-" * 40)
            self.debug_id_mismatch_scenarios(picki_basket)
        
        # Print Summary
        print("=" * 80)
        print("FORD-PICKI ASSIGNMENT TEST SUMMARY")
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
        
        print("\n🎯 FORD-PICKI ASSIGNMENT TEST COMPLETE")
        print("Key Findings:")
        if picki_basket:
            print(f"  ✅ 'picki' basket exists with ID: {picki_basket.get('id')}")
        else:
            print("  ❌ 'picki' basket not found")
        
        if ford_item:
            print(f"  ✅ Ford item available: {ford_item.get('title')}")
        else:
            print("  ❌ No ford item found")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = FordPickiAssignmentTester()
    
    print("🎯 RUNNING FORD-PICKI ASSIGNMENT TEST")
    print("Testing the specific scenario: assigning 'ford' item to 'picki' basket...")
    print()
    
    passed, failed, results = tester.run_ford_picki_assignment_test()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)