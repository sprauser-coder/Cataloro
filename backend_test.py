#!/usr/bin/env python3
"""
URGENT Authentication Testing - Post URL Fix Verification
Testing authentication functionality after fixing frontend URL configuration from preview URL to IP address (http://217.154.0.82)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_result(success, message, details=None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if details:
        print(f"   Details: {details}")

def test_basic_connectivity():
    """Test 1: GET /api/ - Test basic connectivity"""
    print_test_header("Basic API Connectivity Test")
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            expected_message = "Marketplace API"
            
            if data.get("message") == expected_message:
                print_result(True, f"Basic connectivity working - Status: {response.status_code}")
                print(f"   Response: {data}")
                return True
            else:
                print_result(False, f"Unexpected response message: {data}")
                return False
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Connection failed: {str(e)}")
        return False

def test_cors_headers():
    """Test 3: Verify CORS headers are working correctly"""
    print_test_header("CORS Headers Verification")
    
    try:
        # Test preflight request
        headers = {
            'Origin': 'http://217.154.0.82',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options(f"{BACKEND_URL}/auth/login", headers=headers, timeout=10)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print(f"   CORS Headers received:")
        for header, value in cors_headers.items():
            print(f"     {header}: {value}")
        
        # Check if CORS is properly configured
        if cors_headers['Access-Control-Allow-Origin']:
            print_result(True, "CORS headers are present and configured")
            return True
        else:
            print_result(False, "CORS headers missing or misconfigured")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"CORS test failed: {str(e)}")
        return False

def test_admin_authentication():
    """Test 2: POST /api/auth/login - Test admin login with admin@marketplace.com / admin123"""
    print_test_header("Admin Authentication Test")
    
    try:
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login", 
            json=login_data, 
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ['access_token', 'token_type', 'user']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print_result(False, f"Missing required fields: {missing_fields}")
                return False, None
            
            # Verify user data
            user = data['user']
            if user.get('email') == ADMIN_EMAIL and user.get('role') == 'admin':
                print_result(True, f"Admin authentication successful")
                print(f"   User ID: {user.get('id')}")
                print(f"   User Role: {user.get('role')}")
                print(f"   Full Name: {user.get('full_name')}")
                print(f"   Token Type: {data.get('token_type')}")
                print(f"   Token Length: {len(data.get('access_token', ''))}")
                
                return True, data['access_token']
            else:
                print_result(False, f"User data mismatch - Email: {user.get('email')}, Role: {user.get('role')}")
                return False, None
                
        elif response.status_code == 401:
            print_result(False, "Authentication failed - Invalid credentials")
            print(f"   Response: {response.text}")
            return False, None
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Authentication request failed: {str(e)}")
        return False, None

def test_authenticated_endpoint(token):
    """Test authenticated endpoint to verify token works"""
    print_test_header("Token Validation Test")
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test a protected endpoint
        response = requests.get(f"{BACKEND_URL}/admin/stats", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Token validation successful - Admin endpoint accessible")
            print(f"   Stats retrieved: {list(data.keys())}")
            return True
        elif response.status_code == 403:
            print_result(False, "Token valid but insufficient permissions")
            return False
        elif response.status_code == 401:
            print_result(False, "Token validation failed - Invalid or expired token")
            return False
        else:
            print_result(False, f"Unexpected response: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Token validation request failed: {str(e)}")
        return False

def main():
    print("🚀 URGENT AUTHENTICATION TESTING - POST URL FIX VERIFICATION")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    
    results = []
    
    # Test 1: Basic Connectivity
    connectivity_result = test_basic_connectivity()
    results.append(("Basic Connectivity", connectivity_result))
    
    # Test 2: Admin Authentication
    auth_result, token = test_admin_authentication()
    results.append(("Admin Authentication", auth_result))
    
    # Test 3: CORS Headers
    cors_result = test_cors_headers()
    results.append(("CORS Headers", cors_result))
    
    # Test 4: Token Validation (if authentication succeeded)
    if auth_result and token:
        token_result = test_authenticated_endpoint(token)
        results.append(("Token Validation", token_result))
    else:
        results.append(("Token Validation", False))
        print_test_header("Token Validation Test")
        print_result(False, "Skipped - Authentication failed")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Authentication system is working correctly!")
        print("✅ Backend is ready for frontend integration")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Authentication issues detected")
        print("❌ Backend needs attention before frontend can work properly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
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