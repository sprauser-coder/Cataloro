#!/usr/bin/env python3
"""
Cataloro Backend Debug Testing Suite - Permissions and Content Display Issue
Debug the permissions and content display issue as requested in review
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://mega-dashboard.preview.emergentagent.com/api"

class PermissionsDebugTester:
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

    def test_admin_login_user_role_field(self):
        """Test admin login and check what user_role is set"""
        try:
            # Login as demo admin
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
                username = user.get('username')
                full_name = user.get('full_name')
                role = user.get('role')  # Legacy role field
                badge = user.get('badge')
                registration_status = user.get('registration_status')
                
                self.log_test(
                    "Admin Login - User Role Field Check", 
                    True, 
                    f"Demo admin login successful. Username: {username}, Full Name: {full_name}, user_role: {user_role}, legacy role: {role}, badge: {badge}, registration_status: {registration_status}, user_id: {user_id}"
                )
                return user
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login - User Role Field Check", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Admin Login - User Role Field Check", False, error_msg=str(e))
            return None

    def test_catalyst_data_with_content_values(self):
        """Find catalysts that actually have non-zero pt_g, pd_g, rh_g values"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/data", timeout=10)
            
            if response.status_code == 200:
                catalyst_data = response.json()
                
                if isinstance(catalyst_data, list) and len(catalyst_data) > 0:
                    # Find catalysts with non-zero content values
                    catalysts_with_content = []
                    
                    for catalyst in catalyst_data:
                        pt_g = catalyst.get('pt_g', 0)
                        pd_g = catalyst.get('pd_g', 0) 
                        rh_g = catalyst.get('rh_g', 0)
                        
                        if pt_g > 0 or pd_g > 0 or rh_g > 0:
                            catalysts_with_content.append({
                                'cat_id': catalyst.get('cat_id'),
                                'name': catalyst.get('name'),
                                'pt_g': pt_g,
                                'pd_g': pd_g,
                                'rh_g': rh_g,
                                'ceramic_weight': catalyst.get('ceramic_weight', 0)
                            })
                    
                    # Get first 5 catalysts with content values for testing
                    sample_catalysts = catalysts_with_content[:5]
                    
                    details = f"Found {len(catalysts_with_content)} catalysts with non-zero content values out of {len(catalyst_data)} total catalysts."
                    if sample_catalysts:
                        details += "\n\nSample catalysts with content values:"
                        for i, cat in enumerate(sample_catalysts, 1):
                            details += f"\n{i}. {cat['name']} (ID: {cat['cat_id']}) - PT: {cat['pt_g']}g, PD: {cat['pd_g']}g, RH: {cat['rh_g']}g, Weight: {cat['ceramic_weight']}g"
                    
                    self.log_test(
                        "Catalyst Data with Content Values", 
                        len(catalysts_with_content) > 0, 
                        details
                    )
                    return catalysts_with_content
                else:
                    self.log_test("Catalyst Data with Content Values", False, "No catalyst data found")
                    return []
            else:
                self.log_test("Catalyst Data with Content Values", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Catalyst Data with Content Values", False, error_msg=str(e))
            return []

    def test_unified_calculations_data_structure(self):
        """Verify the unified endpoint returns catalysts with proper content values"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations", timeout=10)
            
            if response.status_code == 200:
                unified_data = response.json()
                
                if isinstance(unified_data, list) and len(unified_data) > 0:
                    # Check data structure and find items with content values
                    items_with_content = []
                    required_fields = ['catalyst_id', 'cat_id', 'name', 'weight', 'total_price', 'pt_g', 'pd_g', 'rh_g']
                    
                    for item in unified_data:
                        # Check if all required fields are present
                        has_all_fields = all(field in item for field in required_fields)
                        
                        if has_all_fields:
                            pt_g = item.get('pt_g', 0)
                            pd_g = item.get('pd_g', 0)
                            rh_g = item.get('rh_g', 0)
                            
                            if pt_g > 0 or pd_g > 0 or rh_g > 0:
                                items_with_content.append({
                                    'catalyst_id': item.get('catalyst_id'),
                                    'cat_id': item.get('cat_id'),
                                    'name': item.get('name'),
                                    'weight': item.get('weight'),
                                    'total_price': item.get('total_price'),
                                    'pt_g': pt_g,
                                    'pd_g': pd_g,
                                    'rh_g': rh_g,
                                    'is_override': item.get('is_override', False)
                                })
                    
                    # Get sample items for display
                    sample_items = items_with_content[:5]
                    
                    details = f"Unified calculations endpoint returned {len(unified_data)} items. Found {len(items_with_content)} items with non-zero content values."
                    if sample_items:
                        details += "\n\nSample unified calculation items with content values:"
                        for i, item in enumerate(sample_items, 1):
                            details += f"\n{i}. {item['name']} (ID: {item['cat_id']}) - Weight: {item['weight']}g, Price: €{item['total_price']:.2f}, PT: {item['pt_g']}g, PD: {item['pd_g']}g, RH: {item['rh_g']}g"
                    
                    self.log_test(
                        "Unified Calculations Data Structure", 
                        len(items_with_content) > 0, 
                        details
                    )
                    return items_with_content
                else:
                    self.log_test("Unified Calculations Data Structure", False, "No unified calculation data found")
                    return []
            else:
                self.log_test("Unified Calculations Data Structure", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Unified Calculations Data Structure", False, error_msg=str(e))
            return []

    def test_user_permissions_for_content_values(self, admin_user):
        """Check what permissions the demo admin user should have"""
        if not admin_user:
            self.log_test("User Permissions for Content Values", False, error_msg="No admin user provided")
            return False
            
        try:
            user_role = admin_user.get('user_role')
            user_id = admin_user.get('id')
            
            # Check if user has permissions to see content values
            has_admin_permissions = user_role in ['Admin', 'Admin-Manager']
            
            # Test access to admin-only endpoints
            admin_endpoints_accessible = []
            admin_endpoints_failed = []
            
            # Test catalyst data endpoint (admin only)
            try:
                response = requests.get(f"{BACKEND_URL}/admin/catalyst/data", timeout=5)
                if response.status_code == 200:
                    admin_endpoints_accessible.append("catalyst/data")
                else:
                    admin_endpoints_failed.append(f"catalyst/data (HTTP {response.status_code})")
            except Exception as e:
                admin_endpoints_failed.append(f"catalyst/data (Error: {str(e)})")
            
            # Test unified calculations endpoint (admin only)
            try:
                response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations", timeout=5)
                if response.status_code == 200:
                    admin_endpoints_accessible.append("unified-calculations")
                else:
                    admin_endpoints_failed.append(f"unified-calculations (HTTP {response.status_code})")
            except Exception as e:
                admin_endpoints_failed.append(f"unified-calculations (Error: {str(e)})")
            
            # Test price settings endpoint (admin only)
            try:
                response = requests.get(f"{BACKEND_URL}/admin/catalyst/price-settings", timeout=5)
                if response.status_code == 200:
                    admin_endpoints_accessible.append("price-settings")
                else:
                    admin_endpoints_failed.append(f"price-settings (HTTP {response.status_code})")
            except Exception as e:
                admin_endpoints_failed.append(f"price-settings (Error: {str(e)})")
            
            # Test admin dashboard endpoint
            try:
                response = requests.get(f"{BACKEND_URL}/admin/dashboard", timeout=5)
                if response.status_code == 200:
                    admin_endpoints_accessible.append("dashboard")
                else:
                    admin_endpoints_failed.append(f"dashboard (HTTP {response.status_code})")
            except Exception as e:
                admin_endpoints_failed.append(f"dashboard (Error: {str(e)})")
            
            success = has_admin_permissions and len(admin_endpoints_accessible) >= 3
            
            details = f"User role: {user_role}, Has admin permissions: {has_admin_permissions}"
            details += f"\nAccessible admin endpoints: {admin_endpoints_accessible}"
            if admin_endpoints_failed:
                details += f"\nFailed admin endpoints: {admin_endpoints_failed}"
            
            self.log_test(
                "User Permissions for Content Values", 
                success, 
                details
            )
            return success
            
        except Exception as e:
            self.log_test("User Permissions for Content Values", False, error_msg=str(e))
            return False

    def test_sample_catalyst_data_for_testing(self, catalysts_with_content):
        """Provide sample catalyst data with actual content values for testing"""
        if not catalysts_with_content:
            self.log_test("Sample Catalyst Data for Testing", False, error_msg="No catalysts with content values provided")
            return []
            
        try:
            # Select 3-5 best examples for testing
            sample_catalysts = []
            
            for catalyst in catalysts_with_content[:5]:
                # Calculate PPM values for better understanding
                weight = catalyst.get('ceramic_weight', 0)
                if weight > 0:
                    pt_ppm = (catalyst.get('pt_g', 0) * 1000) / weight
                    pd_ppm = (catalyst.get('pd_g', 0) * 1000) / weight
                    rh_ppm = (catalyst.get('rh_g', 0) * 1000) / weight
                else:
                    pt_ppm = pd_ppm = rh_ppm = 0
                
                sample_catalysts.append({
                    'cat_id': catalyst.get('cat_id'),
                    'name': catalyst.get('name'),
                    'ceramic_weight': weight,
                    'pt_g': catalyst.get('pt_g', 0),
                    'pd_g': catalyst.get('pd_g', 0),
                    'rh_g': catalyst.get('rh_g', 0),
                    'pt_ppm': round(pt_ppm, 2),
                    'pd_ppm': round(pd_ppm, 2),
                    'rh_ppm': round(rh_ppm, 2)
                })
            
            details = f"Selected {len(sample_catalysts)} sample catalysts with actual content values for testing:"
            for i, cat in enumerate(sample_catalysts, 1):
                details += f"\n\n{i}. Catalyst: {cat['name']}"
                details += f"\n   Cat ID: {cat['cat_id']}"
                details += f"\n   Weight: {cat['ceramic_weight']}g"
                details += f"\n   Content Values: PT={cat['pt_g']}g, PD={cat['pd_g']}g, RH={cat['rh_g']}g"
                details += f"\n   PPM Values: PT={cat['pt_ppm']}ppm, PD={cat['pd_ppm']}ppm, RH={cat['rh_ppm']}ppm"
            
            self.log_test(
                "Sample Catalyst Data for Testing", 
                True, 
                details
            )
            return sample_catalysts
            
        except Exception as e:
            self.log_test("Sample Catalyst Data for Testing", False, error_msg=str(e))
            return []

    def run_permissions_debug_testing(self):
        """Run permissions and content display debug testing"""
        print("=" * 80)
        print("CATALORO PERMISSIONS AND CONTENT DISPLAY DEBUG TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Admin Login Details - What user_role is set when logging in as demo admin?
        print("🔍 1. ADMIN LOGIN DETAILS - USER_ROLE FIELD CHECK")
        print("-" * 60)
        admin_user = self.test_admin_login_user_role_field()
        
        # 2. Catalyst Data with Content Values - Find catalysts that actually have non-zero pt_g, pd_g, rh_g values
        print("💎 2. CATALYST DATA WITH CONTENT VALUES")
        print("-" * 60)
        catalysts_with_content = self.test_catalyst_data_with_content_values()
        
        # 3. Unified Calculations Data - Verify the unified endpoint returns catalysts with proper content values
        print("🧮 3. UNIFIED CALCULATIONS DATA STRUCTURE")
        print("-" * 60)
        unified_items_with_content = self.test_unified_calculations_data_structure()
        
        # 4. User Permissions - Check what permissions the demo admin user should have
        print("🔐 4. USER PERMISSIONS FOR CONTENT VALUES")
        print("-" * 60)
        self.test_user_permissions_for_content_values(admin_user)
        
        # 5. Sample Catalyst Data - Provide sample catalyst data with actual content values for testing
        print("📋 5. SAMPLE CATALYST DATA FOR TESTING")
        print("-" * 60)
        sample_catalysts = self.test_sample_catalyst_data_for_testing(catalysts_with_content)
        
        # Print Summary
        print("=" * 80)
        print("PERMISSIONS AND CONTENT DISPLAY DEBUG TEST SUMMARY")
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
        
        print("\n🎯 DEBUG FINDINGS SUMMARY:")
        print("=" * 50)
        
        if admin_user:
            print(f"✅ Demo Admin User Role: {admin_user.get('user_role', 'Unknown')}")
            print(f"✅ Demo Admin Username: {admin_user.get('username', 'Unknown')}")
            print(f"✅ Demo Admin Full Name: {admin_user.get('full_name', 'Unknown')}")
        else:
            print("❌ Demo Admin Login Failed")
        
        if catalysts_with_content:
            print(f"✅ Found {len(catalysts_with_content)} catalysts with non-zero content values")
        else:
            print("❌ No catalysts with content values found")
        
        if unified_items_with_content:
            print(f"✅ Unified endpoint returns {len(unified_items_with_content)} items with content values")
        else:
            print("❌ Unified endpoint has no items with content values")
        
        if sample_catalysts:
            print(f"✅ Provided {len(sample_catalysts)} sample catalysts for testing")
        else:
            print("❌ No sample catalysts available for testing")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = PermissionsDebugTester()
    
    # Run Permissions and Content Display Debug testing as requested in the review
    print("🎯 RUNNING PERMISSIONS AND CONTENT DISPLAY DEBUG TESTING AS REQUESTED")
    print("Debug the permissions and content display issue...")
    print()
    
    passed, failed, results = tester.run_permissions_debug_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)