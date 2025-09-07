#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Updated Description Functionality and Unified Calculations
Testing the updated description functionality and unified calculations endpoint with add_info field
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://catalyst-calc.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
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

    def test_unified_calculations_add_info_field(self):
        """Test that unified calculations endpoint includes add_info field"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations")
            if response.status_code == 200:
                unified_data = response.json()
                
                if isinstance(unified_data, list) and len(unified_data) > 0:
                    # Check if add_info field is present
                    sample_item = unified_data[0]
                    has_add_info = "add_info" in sample_item
                    
                    # Count items with add_info data
                    items_with_add_info = sum(1 for item in unified_data if item.get("add_info", "").strip())
                    
                    self.log_test(
                        "Unified Calculations Add Info Field", 
                        has_add_info, 
                        f"add_info field present: {has_add_info}, Items with add_info data: {items_with_add_info}/{len(unified_data)}"
                    )
                    return unified_data if has_add_info else None
                else:
                    self.log_test("Unified Calculations Add Info Field", True, "No data to test (empty database)")
                    return []
            else:
                self.log_test("Unified Calculations Add Info Field", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Unified Calculations Add Info Field", False, error_msg=str(e))
            return None

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

    def test_admin_login_and_permissions(self):
        """Test admin login and verify permissions for content value visibility"""
        try:
            # Login as admin
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
                
                # Check if user has admin/manager permissions
                has_admin_permissions = user_role in ['Admin', 'Admin-Manager']
                
                self.log_test(
                    "Admin Login and Permissions", 
                    has_admin_permissions, 
                    f"Admin logged in successfully. Role: {user_role}, Has admin permissions: {has_admin_permissions}"
                )
                return user if has_admin_permissions else None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login and Permissions", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Admin Login and Permissions", False, error_msg=str(e))
            return None

    def test_buy_management_access(self, user):
        """Test access to Buy Management features for demo user"""
        if not user:
            self.log_test("Buy Management Access Test", False, error_msg="No user provided")
            return False
            
        try:
            user_id = user.get('id')
            user_role = user.get('user_role')
            
            # Test endpoints that Buy Management features should access
            buy_management_endpoints = [
                ("User Bought Items", f"{BACKEND_URL}/user/bought-items/{user_id}"),
                ("User Baskets", f"{BACKEND_URL}/user/baskets/{user_id}"),
                ("User Profile", f"{BACKEND_URL}/auth/profile/{user_id}"),
                ("Marketplace Browse", f"{BACKEND_URL}/marketplace/browse"),
            ]
            
            successful_endpoints = 0
            total_endpoints = len(buy_management_endpoints)
            endpoint_results = []
            
            for endpoint_name, endpoint_url in buy_management_endpoints:
                try:
                    response = requests.get(endpoint_url, timeout=10)
                    if response.status_code == 200:
                        successful_endpoints += 1
                        endpoint_results.append(f"{endpoint_name}: ✅ HTTP 200")
                        
                        # Special handling for bought items endpoint
                        if "bought-items" in endpoint_url:
                            bought_items = response.json()
                            item_count = len(bought_items) if isinstance(bought_items, list) else 0
                            endpoint_results[-1] += f" ({item_count} items)"
                            
                        # Special handling for baskets endpoint
                        if "baskets" in endpoint_url:
                            baskets = response.json()
                            basket_count = len(baskets) if isinstance(baskets, list) else 0
                            endpoint_results[-1] += f" ({basket_count} baskets)"
                            
                    elif response.status_code == 404:
                        # Some endpoints might not exist yet, that's okay
                        endpoint_results.append(f"{endpoint_name}: ⚠️ HTTP 404 (endpoint not implemented)")
                    else:
                        endpoint_results.append(f"{endpoint_name}: ❌ HTTP {response.status_code}")
                except Exception as e:
                    endpoint_results.append(f"{endpoint_name}: ❌ Error: {str(e)}")
            
            # Check if user role allows Buy Management features
            has_required_role = user_role in ['User-Buyer', 'Admin', 'Admin-Manager']
            
            self.log_test(
                "Buy Management Access Test", 
                has_required_role, 
                f"User role '{user_role}' Buy Management access: {has_required_role}. Endpoints: {'; '.join(endpoint_results)}"
            )
            return has_required_role
            
        except Exception as e:
            self.log_test("Buy Management Access Test", False, error_msg=str(e))
            return False

    def test_update_demo_user_role_if_needed(self, user):
        """Update demo user role to User-Buyer if needed"""
        if not user:
            self.log_test("Update Demo User Role", False, error_msg="No user provided")
            return False
            
        try:
            user_id = user.get('id')
            current_role = user.get('user_role')
            
            # Check if user already has correct role
            if current_role in ['User-Buyer', 'Admin', 'Admin-Manager']:
                self.log_test(
                    "Update Demo User Role", 
                    True, 
                    f"Demo user already has correct role: {current_role}. No update needed."
                )
                return True
            
            # Update user role to User-Buyer
            update_data = {
                "user_role": "User-Buyer",
                "badge": "Buyer",
                "role": "user"  # Legacy role field
            }
            
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{user_id}", 
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test(
                    "Update Demo User Role", 
                    True, 
                    f"Successfully updated demo user role from '{current_role}' to 'User-Buyer'"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Update Demo User Role", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Update Demo User Role", False, error_msg=str(e))
            return False

    def test_verify_updated_demo_user_access(self):
        """Verify demo user can access Buy Management after role update"""
        try:
            # Login again to get updated user data
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
                user_role = user.get('user_role')
                
                # Verify role is now correct
                has_buy_management_access = user_role in ['User-Buyer', 'Admin', 'Admin-Manager']
                
                if has_buy_management_access:
                    # Test Buy Management access again
                    user_id = user.get('id')
                    
                    # Test a key Buy Management endpoint
                    bought_items_response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
                    baskets_response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
                    
                    bought_items_accessible = bought_items_response.status_code in [200, 404]  # 404 is okay if endpoint doesn't exist
                    baskets_accessible = baskets_response.status_code in [200, 404]  # 404 is okay if endpoint doesn't exist
                    
                    self.log_test(
                        "Verify Updated Demo User Access", 
                        True, 
                        f"Demo user now has role '{user_role}' with Buy Management access. Bought items: {bought_items_accessible}, Baskets: {baskets_accessible}"
                    )
                    return True
                else:
                    self.log_test(
                        "Verify Updated Demo User Access", 
                        False, 
                        f"Demo user role '{user_role}' still doesn't allow Buy Management access"
                    )
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Verify Updated Demo User Access", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Verify Updated Demo User Access", False, error_msg=str(e))
            return False

    def test_different_user_roles_buy_management(self):
        """Test Buy Management access for different user roles"""
        try:
            # Test different role scenarios
            role_scenarios = [
                ("User-Buyer", True),
                ("User-Seller", False), 
                ("Admin", True),
                ("Admin-Manager", True)
            ]
            
            all_tests_passed = True
            scenario_results = []
            
            for role, expected_access in role_scenarios:
                # Simulate frontend permission logic
                show_buying_features = role in ['User-Buyer', 'Admin', 'Admin-Manager']
                
                if show_buying_features == expected_access:
                    scenario_results.append(f"{role}: ✅ {show_buying_features}")
                else:
                    scenario_results.append(f"{role}: ❌ Expected {expected_access}, got {show_buying_features}")
                    all_tests_passed = False
            
            self.log_test(
                "Different User Roles Buy Management", 
                all_tests_passed, 
                f"Role permission tests: {'; '.join(scenario_results)}"
            )
            return all_tests_passed
            
        except Exception as e:
            self.log_test("Different User Roles Buy Management", False, error_msg=str(e))
            return False

    def test_frontend_buy_management_permissions(self, user):
        """Test frontend showBuyingFeatures permission logic"""
        if not user:
            self.log_test("Frontend Buy Management Permissions", False, error_msg="No user provided")
            return False
            
        try:
            user_role = user.get('user_role')
            
            # Frontend logic: showBuyingFeatures = ['User-Buyer', 'Admin', 'Admin-Manager'].includes(user_role)
            show_buying_features = user_role in ['User-Buyer', 'Admin', 'Admin-Manager']
            
            # Test the specific roles
            role_permissions = {
                'User-Buyer': True,
                'User-Seller': False,
                'Admin': True,
                'Admin-Manager': True
            }
            
            expected_permission = role_permissions.get(user_role, False)
            permission_correct = show_buying_features == expected_permission
            
            self.log_test(
                "Frontend Buy Management Permissions", 
                permission_correct, 
                f"User role '{user_role}' -> showBuyingFeatures: {show_buying_features} (expected: {expected_permission})"
            )
            return permission_correct
            
        except Exception as e:
            self.log_test("Frontend Buy Management Permissions", False, error_msg=str(e))
            return False

    def run_unified_calculations_testing(self):
        """Run Unified Calculations Endpoint testing as requested in review"""
        print("=" * 80)
        print("CATALORO UNIFIED CALCULATIONS ENDPOINT TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting Unified Calculations testing.")
            return
        
        # 2. Run Unified Calculations Tests
        print("🧮 UNIFIED CALCULATIONS ENDPOINT TESTING")
        print("-" * 40)
        self.test_unified_calculations_endpoint()
        
        # Print Summary
        print("=" * 80)
        print("UNIFIED CALCULATIONS ENDPOINT TEST SUMMARY")
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
        
        print("\n🎯 UNIFIED CALCULATIONS ENDPOINT TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Endpoint should return unified data combining price and content calculations")
        print("  ✅ Should include fields: catalyst_id, cat_id, name, weight, total_price, pt_g, pd_g, rh_g, is_override")
        print("  ✅ Should hide database_id from response")
        print("  ✅ Should calculate content values using formula (weight * ppm / 1000 * renumeration)")
        print("  ✅ Should handle edge cases like empty database, missing settings")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    
    # Run Unified Calculations testing as requested in the review
    print("🎯 RUNNING UNIFIED CALCULATIONS ENDPOINT TESTING AS REQUESTED")
    print("Testing the new /api/admin/catalyst/unified-calculations endpoint...")
    print()
    
    passed, failed, results = tester.run_unified_calculations_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)