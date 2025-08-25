#!/usr/bin/env python3
"""
Backend API Connectivity Test for 217.154.0.82 Server
Testing critical endpoints to diagnose frontend authentication issues and white screen problem.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Updated for 217.154.0.82 server
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class BackendConnectivityTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_basic_api_connectivity(self):
        """Test 1: Basic API Connectivity - GET /api/"""
        print("🌐 Testing Basic API Connectivity...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected API root response
                if "message" in data:
                    self.log_test(
                        "Basic API Connectivity", 
                        True, 
                        f"API root accessible. Response: {data.get('message')}"
                    )
                    return True
                else:
                    self.log_test("Basic API Connectivity", False, "Unexpected API root response format")
                    return False
            else:
                self.log_test(
                    "Basic API Connectivity", 
                    False, 
                    f"API root failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except requests.exceptions.ConnectTimeout:
            self.log_test("Basic API Connectivity", False, "Connection timeout - server may be unreachable")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log_test("Basic API Connectivity", False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Basic API Connectivity", False, f"Exception occurred: {str(e)}")
            return False

    def test_admin_login(self):
        """Test 2: Admin Authentication - POST /api/auth/login with admin credentials"""
        print("🔐 Testing Admin Authentication...")
        
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "access_token" in data and "user" in data:
                    self.admin_token = data["access_token"]
                    self.admin_user = data["user"]
                    
                    # Verify token type and user role
                    if data.get("token_type") == "bearer" and self.admin_user.get("role") == "admin":
                        self.log_test(
                            "Admin Authentication", 
                            True, 
                            f"Successfully authenticated as {self.admin_user.get('email')} with admin role. JWT token received."
                        )
                        return True
                    else:
                        self.log_test("Admin Authentication", False, f"Invalid token type or role. Token type: {data.get('token_type')}, Role: {self.admin_user.get('role')}")
                        return False
                else:
                    self.log_test("Admin Authentication", False, "Missing access_token or user in response")
                    return False
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"Authentication failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except requests.exceptions.ConnectTimeout:
            self.log_test("Admin Authentication", False, "Connection timeout during authentication")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log_test("Admin Authentication", False, f"Connection error during authentication: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_cms_settings(self):
        """Test 3: CMS Settings - GET /api/cms/settings for frontend initialization"""
        print("⚙️ Testing CMS Settings Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/cms/settings", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for essential CMS settings that frontend needs
                essential_fields = ["site_name", "primary_color", "secondary_color", "hero_title", "hero_subtitle"]
                missing_fields = [field for field in essential_fields if field not in data]
                
                if not missing_fields:
                    site_name = data.get("site_name", "Unknown")
                    self.log_test(
                        "CMS Settings", 
                        True, 
                        f"CMS settings accessible. Site name: '{site_name}'. All essential fields present."
                    )
                    return True
                else:
                    self.log_test(
                        "CMS Settings", 
                        False, 
                        f"Missing essential CMS fields: {missing_fields}"
                    )
                    return False
            else:
                self.log_test(
                    "CMS Settings", 
                    False, 
                    f"CMS settings failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except requests.exceptions.ConnectTimeout:
            self.log_test("CMS Settings", False, "Connection timeout accessing CMS settings")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log_test("CMS Settings", False, f"Connection error accessing CMS settings: {str(e)}")
            return False
        except Exception as e:
            self.log_test("CMS Settings", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_categories_endpoint(self):
        """Test 4: Categories Data - GET /api/categories"""
        print("📂 Testing Categories Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/categories", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if categories are returned as a list
                if isinstance(data, list) and len(data) > 0:
                    categories_count = len(data)
                    sample_categories = data[:3]  # Show first 3 categories
                    self.log_test(
                        "Categories Data", 
                        True, 
                        f"Categories endpoint accessible. {categories_count} categories available. Sample: {sample_categories}"
                    )
                    return True
                else:
                    self.log_test(
                        "Categories Data", 
                        False, 
                        f"Categories endpoint returned unexpected data format or empty list: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Categories Data", 
                    False, 
                    f"Categories endpoint failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except requests.exceptions.ConnectTimeout:
            self.log_test("Categories Data", False, "Connection timeout accessing categories")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log_test("Categories Data", False, f"Connection error accessing categories: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Categories Data", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_cors_headers(self):
        """Test 5: CORS Headers - Check if backend properly handles CORS for frontend communication"""
        print("🌐 Testing CORS Headers...")
        
        try:
            # Test preflight request (OPTIONS)
            headers = {
                'Origin': 'http://217.154.0.82',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            }
            
            response = self.session.options(f"{BACKEND_URL}/auth/login", headers=headers, timeout=10)
            
            # Check CORS headers in response
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            # Check if CORS is properly configured
            allow_origin = cors_headers.get('Access-Control-Allow-Origin')
            if allow_origin and (allow_origin == '*' or '217.154.0.82' in allow_origin):
                self.log_test(
                    "CORS Headers", 
                    True, 
                    f"CORS properly configured. Allow-Origin: {allow_origin}. Status: {response.status_code}"
                )
                return True
            else:
                self.log_test(
                    "CORS Headers", 
                    False, 
                    f"CORS may not be properly configured. Headers: {cors_headers}. Status: {response.status_code}"
                )
                return False
                
        except requests.exceptions.ConnectTimeout:
            self.log_test("CORS Headers", False, "Connection timeout during CORS test")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log_test("CORS Headers", False, f"Connection error during CORS test: {str(e)}")
            return False
        except Exception as e:
            self.log_test("CORS Headers", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_authenticated_endpoints(self):
        """Test 6: Authenticated Endpoints - Test protected endpoints with admin token"""
        print("🔐 Testing Authenticated Endpoints...")
        
        if not self.admin_token:
            self.log_test("Authenticated Endpoints", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test multiple authenticated endpoints
            endpoints_to_test = [
                ("/profile", "User Profile"),
                ("/admin/stats", "Admin Stats"),
                ("/listings/my-listings", "My Listings")
            ]
            
            successful_endpoints = []
            failed_endpoints = []
            
            for endpoint, description in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
                    if response.status_code == 200:
                        successful_endpoints.append(f"{description} ({endpoint})")
                    elif response.status_code == 401:
                        failed_endpoints.append(f"{description} ({endpoint}) - 401 Unauthorized")
                    elif response.status_code == 403:
                        failed_endpoints.append(f"{description} ({endpoint}) - 403 Forbidden")
                    else:
                        failed_endpoints.append(f"{description} ({endpoint}) - Status: {response.status_code}")
                except Exception as e:
                    failed_endpoints.append(f"{description} ({endpoint}) - Error: {str(e)}")
            
            if len(successful_endpoints) >= 2:  # At least 2 out of 3 should work
                self.log_test(
                    "Authenticated Endpoints", 
                    True, 
                    f"JWT authentication working. Accessible endpoints: {', '.join(successful_endpoints)}"
                )
                if failed_endpoints:
                    print(f"   Note: Some endpoints had issues: {', '.join(failed_endpoints)}")
                return True
            else:
                self.log_test(
                    "Authenticated Endpoints", 
                    False, 
                    f"JWT authentication failing. Working: {len(successful_endpoints)}, Failed: {len(failed_endpoints)}"
                )
                return False
                
        except Exception as e:
            self.log_test("Authenticated Endpoints", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_frontend_critical_endpoints(self):
        """Test 7: Frontend Critical Endpoints - Test endpoints essential for frontend initialization"""
        print("🎯 Testing Frontend Critical Endpoints...")
        
        try:
            # Test endpoints that frontend needs to initialize properly
            critical_endpoints = [
                ("/", "API Root"),
                ("/categories", "Categories List"),
                ("/cms/settings", "Site Settings"),
                ("/listings", "Public Listings")
            ]
            
            successful_endpoints = []
            failed_endpoints = []
            
            for endpoint, description in critical_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        successful_endpoints.append(f"{description} ({endpoint})")
                    else:
                        failed_endpoints.append(f"{description} ({endpoint}) - Status: {response.status_code}")
                except Exception as e:
                    failed_endpoints.append(f"{description} ({endpoint}) - Error: {str(e)}")
            
            if len(successful_endpoints) >= 3:  # At least 3 out of 4 should work
                self.log_test(
                    "Frontend Critical Endpoints", 
                    True, 
                    f"Frontend initialization endpoints working. Accessible: {', '.join(successful_endpoints)}"
                )
                if failed_endpoints:
                    print(f"   Note: Some endpoints had issues: {', '.join(failed_endpoints)}")
                return True
            else:
                self.log_test(
                    "Frontend Critical Endpoints", 
                    False, 
                    f"Critical frontend endpoints failing. This could cause white screen. Working: {len(successful_endpoints)}, Failed: {len(failed_endpoints)}"
                )
                return False
                
        except Exception as e:
            self.log_test("Frontend Critical Endpoints", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend connectivity tests for 217.154.0.82"""
        print("=" * 80)
        print("🚀 BACKEND API CONNECTIVITY TEST FOR 217.154.0.82")
        print("Diagnosing frontend white screen and authentication issues")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Run tests in sequence - order matters for dependencies
        tests = [
            self.test_basic_api_connectivity,
            self.test_admin_login,
            self.test_cms_settings,
            self.test_categories_endpoint,
            self.test_cors_headers,
            self.test_authenticated_endpoints,
            self.test_frontend_critical_endpoints
        ]
        
        for test in tests:
            test()
        
        # Summary
        print("=" * 80)
        print("📊 BACKEND CONNECTIVITY TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        print()
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            print()
        
        # Diagnosis based on results
        if len(passed_tests) == len(self.test_results):
            print("🎉 ALL TESTS PASSED! Backend is fully accessible from 217.154.0.82")
            print("✅ Frontend white screen issue is NOT caused by backend connectivity problems.")
            print("🔍 Investigate frontend code, React app initialization, or client-side issues.")
        elif len(passed_tests) >= 5:  # Most tests passing
            print("⚠️  MOSTLY WORKING: Backend is largely accessible but has some issues.")
            print("✅ Core functionality available, but some features may cause frontend problems.")
            print("🔍 Check specific failed endpoints and CORS configuration.")
        elif len(passed_tests) >= 3:  # Basic connectivity working
            print("🚨 PARTIAL CONNECTIVITY: Basic backend access working but authentication/data issues.")
            print("⚠️  Frontend may load but fail during authentication or data fetching.")
            print("🔍 Focus on authentication endpoints and data retrieval issues.")
        else:
            print("🚨 CRITICAL BACKEND ISSUES: Server connectivity problems detected.")
            print("❌ Frontend white screen likely caused by backend being unreachable or misconfigured.")
            print("🔍 Check server status, network connectivity, and backend deployment.")
        
        print("=" * 80)
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = BackendConnectivityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
