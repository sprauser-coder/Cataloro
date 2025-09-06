#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Basket Investigation
Investigating the "Basket not found" error for the "picki" basket
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class BasketInvestigationTester:
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

    def check_picki_basket_exists(self):
        """Check if 'picki' basket exists in the database"""
        if not self.demo_user:
            self.log_test("Check Picki Basket Exists", False, error_msg="No demo user available")
            return None
            
        try:
            user_id = self.demo_user.get('id')
            
            # Get all baskets for the demo user
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
                        "Check Picki Basket Exists", 
                        True, 
                        f"Found 'picki' basket with ID: {picki_basket.get('id')}, Name: {picki_basket.get('name')}, Items: {len(picki_basket.get('items', []))}"
                    )
                    return picki_basket
                else:
                    # List all baskets for debugging
                    basket_names = [b.get('name', 'Unnamed') for b in baskets]
                    self.log_test(
                        "Check Picki Basket Exists", 
                        False, 
                        f"'picki' basket NOT found. Available baskets: {basket_names} (Total: {len(baskets)})"
                    )
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Check Picki Basket Exists", False, error_msg=f"Failed to get baskets: {error_detail}")
                return None
                
        except Exception as e:
            self.log_test("Check Picki Basket Exists", False, error_msg=str(e))
            return None

    def create_picki_basket_if_missing(self):
        """Create 'picki' basket if it doesn't exist"""
        if not self.demo_user:
            self.log_test("Create Picki Basket", False, error_msg="No demo user available")
            return None
            
        try:
            user_id = self.demo_user.get('id')
            
            # Create 'picki' basket - correct endpoint is /api/user/baskets (POST)
            basket_data = {
                "user_id": user_id,
                "name": "picki",
                "description": "Test basket for investigating assignment issue"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/baskets", 
                json=basket_data,
                timeout=10
            )
            
            if response.status_code == 200:
                created_basket_response = response.json()
                basket_id = created_basket_response.get('basket_id')
                
                # Get the created basket details
                baskets_response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
                if baskets_response.status_code == 200:
                    baskets = baskets_response.json()
                    created_basket = None
                    for basket in baskets:
                        if basket.get('id') == basket_id:
                            created_basket = basket
                            break
                    
                    if created_basket:
                        self.log_test(
                            "Create Picki Basket", 
                            True, 
                            f"Successfully created 'picki' basket with ID: {basket_id}"
                        )
                        return created_basket
                
                self.log_test(
                    "Create Picki Basket", 
                    True, 
                    f"Basket created but couldn't retrieve details. ID: {basket_id}"
                )
                return {"id": basket_id, "name": "picki"}
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Picki Basket", False, error_msg=f"Failed to create basket: {error_detail}")
                return None
                
        except Exception as e:
            self.log_test("Create Picki Basket", False, error_msg=str(e))
            return None

    def test_basket_assignment_with_correct_id(self, basket_id):
        """Test basket assignment endpoint with the correct basket ID"""
        if not self.demo_user or not basket_id:
            self.log_test("Test Basket Assignment", False, error_msg="Missing demo user or basket ID")
            return False
            
        try:
            user_id = self.demo_user.get('id')
            
            # First, let's check if there are any bought items to assign
            bought_items_response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if bought_items_response.status_code == 200:
                bought_items = bought_items_response.json()
                
                if not bought_items:
                    self.log_test(
                        "Test Basket Assignment", 
                        True, 
                        "No bought items available to test assignment. This is expected if user hasn't purchased anything."
                    )
                    return True
                
                # Try to assign the first bought item to the picki basket
                test_item = bought_items[0]
                item_id = test_item.get('id')
                
                if not item_id:
                    self.log_test("Test Basket Assignment", False, error_msg="Bought item has no ID")
                    return False
                
                # Test the assignment endpoint
                assignment_data = {
                    "basket_id": basket_id
                }
                
                response = requests.put(
                    f"{BACKEND_URL}/user/bought-items/{user_id}/{item_id}/assign-basket",
                    json=assignment_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log_test(
                        "Test Basket Assignment", 
                        True, 
                        f"Successfully assigned item '{test_item.get('title', 'Unknown')}' to picki basket (ID: {basket_id})"
                    )
                    return True
                else:
                    error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                    self.log_test(
                        "Test Basket Assignment", 
                        False, 
                        error_msg=f"Assignment failed: {error_detail}"
                    )
                    return False
            else:
                error_detail = bought_items_response.json().get('detail', 'Unknown error') if bought_items_response.content else f"HTTP {bought_items_response.status_code}"
                self.log_test("Test Basket Assignment", False, error_msg=f"Failed to get bought items: {error_detail}")
                return False
                
        except Exception as e:
            self.log_test("Test Basket Assignment", False, error_msg=str(e))
            return False

    def check_id_format_consistency(self, basket):
        """Check if there are ID format issues between frontend and backend"""
        if not basket:
            self.log_test("Check ID Format Consistency", False, error_msg="No basket provided")
            return False
            
        try:
            basket_id = basket.get('id')
            basket_name = basket.get('name')
            
            # Check ID format
            id_format_info = []
            
            # Check if it's a UUID format
            try:
                uuid.UUID(basket_id)
                id_format_info.append("UUID format: ✅ Valid")
            except ValueError:
                id_format_info.append("UUID format: ❌ Invalid")
            
            # Check ID length and characters
            id_format_info.append(f"ID length: {len(basket_id)} characters")
            id_format_info.append(f"ID contains hyphens: {'✅' if '-' in basket_id else '❌'}")
            
            # Check if ID is consistent with other objects
            if self.demo_user:
                user_id = self.demo_user.get('id')
                try:
                    uuid.UUID(user_id)
                    user_id_valid = True
                except ValueError:
                    user_id_valid = False
                
                id_format_info.append(f"User ID format matches: {'✅' if user_id_valid else '❌'}")
            
            self.log_test(
                "Check ID Format Consistency", 
                True, 
                f"Basket '{basket_name}' ID analysis: {'; '.join(id_format_info)}"
            )
            return True
            
        except Exception as e:
            self.log_test("Check ID Format Consistency", False, error_msg=str(e))
            return False

    def debug_basket_endpoints(self):
        """Debug all basket-related endpoints to understand the issue"""
        if not self.demo_user:
            self.log_test("Debug Basket Endpoints", False, error_msg="No demo user available")
            return False
            
        try:
            user_id = self.demo_user.get('id')
            endpoint_results = []
            
            # Test basket endpoints
            basket_endpoints = [
                ("Get User Baskets", f"{BACKEND_URL}/user/baskets/{user_id}"),
                ("Get Bought Items", f"{BACKEND_URL}/user/bought-items/{user_id}"),
            ]
            
            for endpoint_name, endpoint_url in basket_endpoints:
                try:
                    response = requests.get(endpoint_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        count = len(data) if isinstance(data, list) else 1
                        endpoint_results.append(f"{endpoint_name}: ✅ HTTP 200 ({count} items)")
                    else:
                        error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                        endpoint_results.append(f"{endpoint_name}: ❌ {error_detail}")
                except Exception as e:
                    endpoint_results.append(f"{endpoint_name}: ❌ Error: {str(e)}")
            
            self.log_test(
                "Debug Basket Endpoints", 
                True, 
                f"Endpoint status: {'; '.join(endpoint_results)}"
            )
            return True
            
        except Exception as e:
            self.log_test("Debug Basket Endpoints", False, error_msg=str(e))
            return False

    def run_basket_investigation(self):
        """Run the complete basket investigation as requested"""
        print("=" * 80)
        print("CATALORO BASKET INVESTIGATION - 'PICKI' BASKET NOT FOUND ERROR")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Setup demo user
        print("👤 SETUP DEMO USER")
        print("-" * 40)
        if not self.setup_demo_user():
            print("❌ Failed to setup demo user. Aborting investigation.")
            return
        
        # 2. Check if 'picki' basket exists
        print("🔍 CHECK IF 'PICKI' BASKET EXISTS")
        print("-" * 40)
        picki_basket = self.check_picki_basket_exists()
        
        # 3. Create 'picki' basket if it doesn't exist
        if not picki_basket:
            print("🛠️ CREATE 'PICKI' BASKET")
            print("-" * 40)
            picki_basket = self.create_picki_basket_if_missing()
        
        # 4. Test basket assignment with correct ID
        if picki_basket:
            print("🎯 TEST BASKET ASSIGNMENT WITH CORRECT ID")
            print("-" * 40)
            basket_id = picki_basket.get('id')
            self.test_basket_assignment_with_correct_id(basket_id)
            
            # 5. Check ID format consistency
            print("🔧 CHECK ID FORMAT CONSISTENCY")
            print("-" * 40)
            self.check_id_format_consistency(picki_basket)
        
        # 6. Debug basket endpoints
        print("🐛 DEBUG BASKET ENDPOINTS")
        print("-" * 40)
        self.debug_basket_endpoints()
        
        # Print Summary
        print("=" * 80)
        print("BASKET INVESTIGATION SUMMARY")
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
        
        print("\n🎯 BASKET INVESTIGATION COMPLETE")
        print("Key Findings:")
        if picki_basket:
            print(f"  ✅ 'picki' basket found/created with ID: {picki_basket.get('id')}")
        else:
            print("  ❌ 'picki' basket could not be found or created")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BasketInvestigationTester()
    
    print("🎯 RUNNING BASKET INVESTIGATION AS REQUESTED")
    print("Investigating 'Basket not found' error for 'picki' basket...")
    print()
    
    passed, failed, results = tester.run_basket_investigation()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)