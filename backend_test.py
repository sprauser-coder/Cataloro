#!/usr/bin/env python3
"""
Backend API Testing Script for Cataloro Marketplace
Focus: Core endpoints verification after recent changes
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://revived-cataloro.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_basic_connectivity(self):
        """Test 1: Basic connectivity - GET /api/ endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Marketplace API":
                    self.log_test("Basic Connectivity", True, "Root API endpoint responding correctly")
                    return True
                else:
                    self.log_test("Basic Connectivity", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Basic Connectivity", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Basic Connectivity", False, f"Connection error: {str(e)}")
            return False
    
    def test_admin_authentication(self):
        """Test 2: Authentication endpoints - POST /api/auth/login"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.admin_token = data["access_token"]
                    user = data["user"]
                    if user.get("role") == "admin":
                        self.log_test("Admin Authentication", True, f"Admin login successful for {user.get('email')}")
                        return True
                    else:
                        self.log_test("Admin Authentication", False, f"User role is {user.get('role')}, expected 'admin'")
                        return False
                else:
                    self.log_test("Admin Authentication", False, f"Missing token or user in response: {data}")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_listings_endpoint(self):
        """Test 3: Core marketplace endpoints - GET /api/listings"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Listings Endpoint", True, f"Retrieved {len(data)} listings successfully")
                    return True
                else:
                    self.log_test("Listings Endpoint", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Listings Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Listings Endpoint", False, f"Request error: {str(e)}")
            return False
    
    def test_categories_endpoint(self):
        """Test 4: Core marketplace endpoints - GET /api/categories"""
        try:
            response = self.session.get(f"{BACKEND_URL}/categories")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    expected_categories = ["Electronics", "Fashion", "Home & Garden", "Sports", "Books"]
                    found_categories = [cat for cat in expected_categories if cat in data]
                    if len(found_categories) >= 3:  # At least 3 expected categories found
                        self.log_test("Categories Endpoint", True, f"Retrieved {len(data)} categories including {found_categories}")
                        return True
                    else:
                        self.log_test("Categories Endpoint", False, f"Missing expected categories. Got: {data}")
                        return False
                else:
                    self.log_test("Categories Endpoint", False, f"Expected non-empty list, got: {data}")
                    return False
            else:
                self.log_test("Categories Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Categories Endpoint", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_stats_endpoint(self):
        """Test 5: Admin endpoints - GET /api/admin/stats (with admin credentials)"""
        if not self.admin_token:
            self.log_test("Admin Stats Endpoint", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_users", "active_users", "total_listings", "active_listings", "total_orders", "total_revenue"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    stats_summary = {k: data[k] for k in required_fields}
                    self.log_test("Admin Stats Endpoint", True, f"Admin stats retrieved successfully: {stats_summary}")
                    return True
                else:
                    self.log_test("Admin Stats Endpoint", False, f"Missing required fields: {missing_fields}")
                    return False
            elif response.status_code == 403:
                self.log_test("Admin Stats Endpoint", False, "Access denied - admin authentication failed")
                return False
            else:
                self.log_test("Admin Stats Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Stats Endpoint", False, f"Request error: {str(e)}")
            return False
    
    def test_cms_settings_endpoint(self):
        """Test 6: CMS settings endpoint - GET /api/cms/settings (important for Footer)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/cms/settings")
            
            if response.status_code == 200:
                data = response.json()
                # Check for key fields that Footer component depends on
                required_fields = ["site_name", "font_color", "global_font_family"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    footer_relevant = {
                        "site_name": data.get("site_name"),
                        "font_color": data.get("font_color"),
                        "global_font_family": data.get("global_font_family"),
                        "primary_color": data.get("primary_color"),
                        "secondary_color": data.get("secondary_color")
                    }
                    self.log_test("CMS Settings Endpoint", True, f"CMS settings retrieved successfully. Footer fields: {footer_relevant}")
                    return True
                else:
                    self.log_test("CMS Settings Endpoint", False, f"Missing required fields for Footer: {missing_fields}")
                    return False
            else:
                self.log_test("CMS Settings Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("CMS Settings Endpoint", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("CATALORO BACKEND API TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}")
        print("=" * 80)
        
        # Run tests in sequence
        tests = [
            self.test_basic_connectivity,
            self.test_admin_authentication,
            self.test_listings_endpoint,
            self.test_categories_endpoint,
            self.test_admin_stats_endpoint,
            self.test_cms_settings_endpoint
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Backend API is fully operational!")
        else:
            print("⚠️  SOME TESTS FAILED - Check details above")
        
        print("=" * 80)
        
        return passed == total

def main():
    """Main test execution"""
    tester = BackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()