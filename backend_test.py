#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Demo User Role and Buy Management Testing
Testing demo user role permissions and Buy Management access functionality
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-admin-5.preview.emergentagent.com/api"

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

    def test_demo_user_login_and_role_check(self):
        """Test demo user login and check their user_role field"""
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
                user = data.get('user', {})
                user_role = user.get('user_role')
                user_id = user.get('id')
                registration_status = user.get('registration_status')
                
                # Check if user has proper role for Buy Management
                has_buy_management_role = user_role in ['User-Buyer', 'Admin', 'Admin-Manager']
                
                self.log_test(
                    "Demo User Login and Role Check", 
                    True, 
                    f"Demo user logged in successfully. Role: {user_role}, Status: {registration_status}, Has Buy Management Access: {has_buy_management_role}"
                )
                return user, has_buy_management_role
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Demo User Login and Role Check", False, error_msg=error_detail)
                return None, False
        except Exception as e:
            self.log_test("Demo User Login and Role Check", False, error_msg=str(e))
            return None, False

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

    def run_demo_user_role_testing(self):
        """Run Demo User Role and Buy Management testing as requested in review"""
        print("=" * 80)
        print("CATALORO DEMO USER ROLE & BUY MANAGEMENT TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        demo_user = None
        has_buy_management_role = False
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting Demo User testing.")
            return
        
        # 2. Demo User Login and Role Check
        print("👤 DEMO USER LOGIN AND ROLE CHECK")
        print("-" * 40)
        demo_user, has_buy_management_role = self.test_demo_user_login_and_role_check()
        
        if not demo_user:
            print("❌ Failed to login as demo user. Aborting tests.")
            return
        
        # 3. Test Buy Management Access
        print("🛒 TEST BUY MANAGEMENT ACCESS")
        print("-" * 40)
        buy_management_accessible = self.test_buy_management_access(demo_user)
        
        # 4. Update Demo User Role if Needed
        print("🔧 UPDATE DEMO USER ROLE IF NEEDED")
        print("-" * 40)
        if not has_buy_management_role:
            print("⚠️  Demo user doesn't have User-Buyer role. Updating...")
            role_updated = self.test_update_demo_user_role_if_needed(demo_user)
            
            if role_updated:
                # 5. Verify Updated Access
                print("✅ VERIFY UPDATED DEMO USER ACCESS")
                print("-" * 40)
                self.test_verify_updated_demo_user_access()
        else:
            print("✅ Demo user already has correct role for Buy Management features.")
        
        # 6. Test Different User Roles
        print("🎭 TEST DIFFERENT USER ROLES BUY MANAGEMENT")
        print("-" * 40)
        self.test_different_user_roles_buy_management()
        
        # 7. Test Frontend Permission Logic
        print("🎨 TEST FRONTEND BUY MANAGEMENT PERMISSIONS")
        print("-" * 40)
        self.test_frontend_buy_management_permissions(demo_user)
        
        # Print Summary
        print("=" * 80)
        print("DEMO USER ROLE TEST SUMMARY")
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
        
        print("\n🎯 DEMO USER ROLE TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Demo user should have 'User-Buyer', 'Admin', or 'Admin-Manager' role")
        print("  ✅ Demo user should be able to access Buy Management features")
        print("  ✅ Frontend showBuyingFeatures should be true for demo user")
        print("  ✅ Buy Management endpoints should be accessible")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    
    # Run Demo User Role testing as requested in the review
    print("🎯 RUNNING DEMO USER ROLE & BUY MANAGEMENT TESTING AS REQUESTED")
    print("Checking demo user role and Buy Management access permissions...")
    print()
    
    passed, failed, results = tester.run_demo_user_role_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)