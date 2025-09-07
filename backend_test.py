#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - MazdaRF4SOK14 Listing and Admin Authentication Testing
Testing the specific individual listing endpoint for MazdaRF4SOK14 listing and admin login functionality
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://product-page-fix.preview.emergentagent.com/api"

# Specific listing ID to test as requested in review
MAZDA_LISTING_ID = "6b7961e7-3191-4a3b-84cb-cdcbe74a6ea3"

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

    def test_admin_authentication(self):
        """Test admin login functionality to ensure it works properly"""
        try:
            # Test admin login with correct credentials
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
                
                # Verify admin user details
                is_admin = user_role in ['Admin', 'Admin-Manager']
                has_token = 'token' in data
                
                self.log_test(
                    "Admin Authentication", 
                    is_admin and has_token, 
                    f"Admin login successful. Username: {username}, Role: {user_role}, User ID: {user_id}, Token provided: {has_token}"
                )
                return user if is_admin else None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Authentication", False, error_msg=f"Login failed: {error_detail}")
                return None
        except Exception as e:
            self.log_test("Admin Authentication", False, error_msg=str(e))
            return None

    def test_mazda_listing_endpoint(self):
        """Test the specific MazdaRF4SOK14 listing endpoint to verify it returns listing data with catalyst content fields"""
        try:
            # First, check if the listing exists in browse endpoint
            browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            mazda_listing_found = False
            mazda_listing_data = None
            
            if browse_response.status_code == 200:
                listings = browse_response.json()
                for listing in listings:
                    if listing.get('id') == MAZDA_LISTING_ID:
                        mazda_listing_found = True
                        mazda_listing_data = listing
                        break
            
            if not mazda_listing_found:
                self.log_test(
                    "MazdaRF4SOK14 Listing Endpoint", 
                    False, 
                    error_msg=f"MazdaRF4SOK14 listing with ID {MAZDA_LISTING_ID} not found in browse endpoint"
                )
                return None
            
            # Test the individual listing endpoint
            response = requests.get(f"{BACKEND_URL}/listings/{MAZDA_LISTING_ID}", timeout=10)
            
            if response.status_code == 200:
                listing_data = response.json()
                
                # Check for catalyst content fields
                catalyst_fields = {
                    'ceramic_weight': listing_data.get('ceramic_weight'),
                    'pt_ppm': listing_data.get('pt_ppm'),
                    'pd_ppm': listing_data.get('pd_ppm'),
                    'rh_ppm': listing_data.get('rh_ppm'),
                    'pt_g': listing_data.get('pt_g'),
                    'pd_g': listing_data.get('pd_g'),
                    'rh_g': listing_data.get('rh_g')
                }
                
                # Count available catalyst fields
                available_fields = {k: v for k, v in catalyst_fields.items() if v is not None}
                has_catalyst_data = len(available_fields) > 0
                
                # Get basic listing info
                title = listing_data.get('title', 'Unknown')
                price = listing_data.get('price', 0)
                
                self.log_test(
                    "MazdaRF4SOK14 Listing Endpoint", 
                    has_catalyst_data, 
                    f"Listing found: {title} (€{price}). Catalyst fields available: {len(available_fields)}/7. Fields: {list(available_fields.keys())}"
                )
                
                # Print detailed catalyst data for verification
                if available_fields:
                    print("   Catalyst Content Fields:")
                    for field, value in available_fields.items():
                        print(f"     - {field}: {value}")
                
                return listing_data if has_catalyst_data else None
            else:
                self.log_test(
                    "MazdaRF4SOK14 Listing Endpoint", 
                    False, 
                    error_msg=f"Individual listing endpoint failed: HTTP {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_test("MazdaRF4SOK14 Listing Endpoint", False, error_msg=str(e))
            return None

    def test_catalyst_data_structure_compatibility(self, listing_data):
        """Test that the listing data structure is compatible with frontend expectations"""
        if not listing_data:
            self.log_test("Catalyst Data Structure Compatibility", False, error_msg="No listing data provided")
            return False
            
        try:
            # Check required fields for frontend compatibility
            required_fields = ['id', 'title', 'description', 'price', 'seller_id']
            catalyst_fields = ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm', 'pt_g', 'pd_g', 'rh_g']
            
            # Check required fields
            missing_required = [field for field in required_fields if field not in listing_data]
            
            # Check catalyst fields availability
            available_catalyst_fields = [field for field in catalyst_fields if listing_data.get(field) is not None]
            
            # Check seller information (should be enriched by browse endpoint)
            has_seller_info = 'seller' in listing_data or 'seller_id' in listing_data
            
            success = len(missing_required) == 0 and len(available_catalyst_fields) > 0
            
            self.log_test(
                "Catalyst Data Structure Compatibility", 
                success, 
                f"Required fields present: {len(required_fields) - len(missing_required)}/{len(required_fields)}, "
                f"Catalyst fields available: {len(available_catalyst_fields)}/{len(catalyst_fields)}, "
                f"Seller info present: {has_seller_info}"
            )
            
            if missing_required:
                print(f"   Missing required fields: {missing_required}")
            
            return success
            
        except Exception as e:
            self.log_test("Catalyst Data Structure Compatibility", False, error_msg=str(e))
            return False

    def test_admin_permissions_for_catalyst_content(self, admin_user):
        """Test that admin user has proper permissions to view catalyst content"""
        if not admin_user:
            self.log_test("Admin Permissions for Catalyst Content", False, error_msg="No admin user provided")
            return False
            
        try:
            user_role = admin_user.get('user_role')
            
            # Test permission logic that would be used in frontend
            has_admin_permissions = user_role in ['Admin', 'Admin-Manager']
            
            # Test alternative permission check (Admin-Manager mapped to Manager)
            mapped_role = 'Manager' if user_role == 'Admin-Manager' else user_role
            alternative_permission = mapped_role in ['Admin', 'Manager']
            
            success = has_admin_permissions or alternative_permission
            
            self.log_test(
                "Admin Permissions for Catalyst Content", 
                success, 
                f"User role: {user_role}, Has admin permissions: {has_admin_permissions}, Alternative check: {alternative_permission}"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Admin Permissions for Catalyst Content", False, error_msg=str(e))
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
        """Test admin login and verify permissions for catalyst content visibility"""
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
                
                # Check if user has admin/manager permissions for catalyst content
                has_catalyst_permissions = user_role in ['Admin', 'Admin-Manager']
                
                self.log_test(
                    "Admin Login and Catalyst Permissions", 
                    has_catalyst_permissions, 
                    f"Admin logged in successfully. Role: {user_role}, Has catalyst permissions: {has_catalyst_permissions}, User ID: {user_id}"
                )
                return user if has_catalyst_permissions else None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login and Catalyst Permissions", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Admin Login and Catalyst Permissions", False, error_msg=str(e))
            return None



    def run_mazda_listing_and_admin_testing(self):
        """Run MazdaRF4SOK14 listing and admin authentication testing as requested in review"""
        print("=" * 80)
        print("CATALORO MAZDA RF4SOK14 LISTING AND ADMIN AUTHENTICATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Target Listing ID: {MAZDA_LISTING_ID}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting testing.")
            return
        
        # 2. Test Admin Authentication
        print("👤 ADMIN AUTHENTICATION TESTING")
        print("-" * 40)
        admin_user = self.test_admin_authentication()
        
        # 3. Test MazdaRF4SOK14 Listing Endpoint
        print("🚗 MAZDA RF4SOK14 LISTING ENDPOINT TESTING")
        print("-" * 40)
        mazda_listing = self.test_mazda_listing_endpoint()
        
        # 4. Test Catalyst Data Structure Compatibility
        print("📊 CATALYST DATA STRUCTURE COMPATIBILITY TESTING")
        print("-" * 40)
        self.test_catalyst_data_structure_compatibility(mazda_listing)
        
        # 5. Test Admin Permissions for Catalyst Content
        print("🔐 ADMIN PERMISSIONS FOR CATALYST CONTENT TESTING")
        print("-" * 40)
        self.test_admin_permissions_for_catalyst_content(admin_user)
        
        # Print Summary
        print("=" * 80)
        print("MAZDA RF4SOK14 LISTING AND ADMIN AUTHENTICATION TEST SUMMARY")
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
        
        print("\n🎯 MAZDA RF4SOK14 LISTING AND ADMIN AUTHENTICATION TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Admin login works properly with correct credentials")
        print("  ✅ MazdaRF4SOK14 listing endpoint returns listing data")
        print("  ✅ Listing contains catalyst content fields for admin users")
        print("  ✅ Data structure is compatible with frontend expectations")
        print("  ✅ Admin user has proper permissions for catalyst content")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    
    # Run MazdaRF4SOK14 listing and admin authentication testing as requested in the review
    print("🎯 RUNNING MAZDA RF4SOK14 LISTING AND ADMIN AUTHENTICATION TESTING AS REQUESTED")
    print("Testing the specific individual listing endpoint for MazdaRF4SOK14 listing and admin login functionality...")
    print()
    
    passed, failed, results = tester.run_mazda_listing_and_admin_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)