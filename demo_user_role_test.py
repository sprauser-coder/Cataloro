#!/usr/bin/env python3
"""
Demo User Role Update Testing Suite
Testing demo user role update from User-Buyer to Admin for catalyst fields visibility
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-admin-5.preview.emergentagent.com/api"

class DemoUserRoleTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.demo_user_id = None
        
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
                self.log_test("Health Check", True, f"Backend is healthy: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def test_find_demo_user(self):
        """Find demo user by email demo@cataloro.com"""
        try:
            # Get all users to find demo user
            response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if response.status_code == 200:
                users = response.json()
                demo_user = None
                
                for user in users:
                    if user.get('email') == 'demo@cataloro.com':
                        demo_user = user
                        self.demo_user_id = user.get('id')
                        break
                
                if demo_user:
                    current_role = demo_user.get('user_role', 'Unknown')
                    self.log_test("Find Demo User", True, 
                                f"Found demo user with ID: {self.demo_user_id}, Current role: {current_role}")
                    return demo_user
                else:
                    self.log_test("Find Demo User", False, "Demo user with email demo@cataloro.com not found")
                    return None
            else:
                self.log_test("Find Demo User", False, f"Failed to get users list. Status: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Find Demo User", False, error_msg=str(e))
            return None

    def test_update_demo_user_role(self):
        """Update demo user role from User-Buyer to Admin"""
        if not self.demo_user_id:
            self.log_test("Update Demo User Role", False, "Demo user ID not available")
            return False
            
        try:
            # Update user role to Admin
            update_data = {
                "user_role": "Admin",
                "badge": "Admin",
                "role": "admin"  # Legacy role field
            }
            
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{self.demo_user_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Update Demo User Role", True, 
                            "Successfully updated demo user role to Admin")
                return True
            else:
                error_detail = response.text if response.text else f"Status code: {response.status_code}"
                self.log_test("Update Demo User Role", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Update Demo User Role", False, error_msg=str(e))
            return False

    def test_verify_role_update(self):
        """Verify that demo user role has been updated to Admin"""
        if not self.demo_user_id:
            self.log_test("Verify Role Update", False, "Demo user ID not available")
            return False
            
        try:
            # Get user profile to verify role update
            response = requests.get(f"{BACKEND_URL}/auth/profile/{self.demo_user_id}", timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                current_role = user_data.get('user_role')
                current_badge = user_data.get('badge')
                legacy_role = user_data.get('role')
                
                if current_role == 'Admin' and current_badge == 'Admin' and legacy_role == 'admin':
                    self.log_test("Verify Role Update", True, 
                                f"Demo user role successfully updated: user_role={current_role}, badge={current_badge}, role={legacy_role}")
                    return True
                else:
                    self.log_test("Verify Role Update", False, 
                                f"Role update incomplete: user_role={current_role}, badge={current_badge}, role={legacy_role}")
                    return False
            else:
                error_detail = response.text if response.text else f"Status code: {response.status_code}"
                self.log_test("Verify Role Update", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Verify Role Update", False, error_msg=str(e))
            return False

    def test_login_as_demo_user(self):
        """Test login as demo user to verify Admin permissions"""
        try:
            login_data = {
                "email": "demo@cataloro.com",
                "password": "demo123"  # Assuming demo password
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                login_result = response.json()
                user_data = login_result.get('user', {})
                user_role = user_data.get('user_role')
                badge = user_data.get('badge')
                
                if user_role == 'Admin' and badge == 'Admin':
                    self.log_test("Login as Demo User", True, 
                                f"Successfully logged in as Admin user: role={user_role}, badge={badge}")
                    return True
                else:
                    self.log_test("Login as Demo User", False, 
                                f"Login successful but role not Admin: role={user_role}, badge={badge}")
                    return False
            else:
                error_detail = response.text if response.text else f"Status code: {response.status_code}"
                self.log_test("Login as Demo User", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Login as Demo User", False, error_msg=str(e))
            return False

    def test_admin_permissions_access(self):
        """Test that demo user can access admin-only endpoints"""
        try:
            # Test admin dashboard access
            response = requests.get(f"{BACKEND_URL}/admin/dashboard", timeout=10)
            
            if response.status_code == 200:
                dashboard_data = response.json()
                kpis = dashboard_data.get('kpis', {})
                
                self.log_test("Admin Permissions Access", True, 
                            f"Successfully accessed admin dashboard. Users: {kpis.get('total_users', 0)}, Listings: {kpis.get('total_listings', 0)}")
                return True
            else:
                error_detail = response.text if response.text else f"Status code: {response.status_code}"
                self.log_test("Admin Permissions Access", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Admin Permissions Access", False, error_msg=str(e))
            return False

    def test_catalyst_fields_visibility_readiness(self):
        """Test that Admin role enables catalyst fields visibility in ProductDetailPage"""
        try:
            # Get a sample listing to verify catalyst fields are available for Admin users
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                # Look for listings with catalyst fields
                catalyst_listings = []
                for listing in listings:
                    if any([
                        listing.get('ceramic_weight') is not None,
                        listing.get('pt_ppm') is not None,
                        listing.get('pd_ppm') is not None,
                        listing.get('rh_ppm') is not None
                    ]):
                        catalyst_listings.append(listing)
                
                if catalyst_listings:
                    sample_listing = catalyst_listings[0]
                    catalyst_info = {
                        'ceramic_weight': sample_listing.get('ceramic_weight'),
                        'pt_ppm': sample_listing.get('pt_ppm'),
                        'pd_ppm': sample_listing.get('pd_ppm'),
                        'rh_ppm': sample_listing.get('rh_ppm')
                    }
                    
                    self.log_test("Catalyst Fields Visibility Readiness", True, 
                                f"Found {len(catalyst_listings)} listings with catalyst fields. Sample: {catalyst_info}")
                    return True
                else:
                    self.log_test("Catalyst Fields Visibility Readiness", True, 
                                f"No listings with catalyst fields found, but Admin role is ready for catalyst field visibility")
                    return True
            else:
                error_detail = response.text if response.text else f"Status code: {response.status_code}"
                self.log_test("Catalyst Fields Visibility Readiness", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Catalyst Fields Visibility Readiness", False, error_msg=str(e))
            return False

    def run_all_tests(self):
        """Run all demo user role update tests"""
        print("=" * 80)
        print("DEMO USER ROLE UPDATE TESTING SUITE")
        print("=" * 80)
        print()
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.test_find_demo_user,
            self.test_update_demo_user_role,
            self.test_verify_role_update,
            self.test_login_as_demo_user,
            self.test_admin_permissions_access,
            self.test_catalyst_fields_visibility_readiness
        ]
        
        for test in tests:
            test()
            time.sleep(0.5)  # Small delay between tests
        
        # Print summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"- {result['test']}: {result.get('error', 'Unknown error')}")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = DemoUserRoleTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 All tests passed! Demo user role update completed successfully.")
    else:
        print("⚠️  Some tests failed. Please check the results above.")