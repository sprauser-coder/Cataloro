#!/usr/bin/env python3
from config_loader import get_config, get_backend_url, get_admin_credentials, get_paths, get_database_url
"""
Authentication System Testing for Cataloro Marketplace
Testing authentication functionality after frontend enhancements as requested
"""

import requests
import json
import sys
from datetime import datetime

# Configuration from review request
BASE_URL = "get_backend_url()/api"
ADMIN_EMAIL = "get_admin_credentials()[0]"
ADMIN_PASSWORD = "get_admin_credentials()[1]"

class AuthenticationTestSuite:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.session = requests.Session()
        
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
        """Test basic API connectivity to get_backend_url()/api/"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                version = data.get("version", "")
                
                self.log_test("Basic API Connectivity", True, 
                            f"Connected successfully. Message: '{message}', Version: '{version}'")
                return True
            else:
                self.log_test("Basic API Connectivity", False, 
                            f"Failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Basic API Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_login_functionality(self):
        """Test admin login functionality with get_admin_credentials()[0]/get_admin_credentials()[1] credentials"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.admin_token = data["access_token"]
                    user_data = data["user"]
                    
                    # Validate user data
                    if (user_data.get("email") == ADMIN_EMAIL and 
                        user_data.get("role") == "admin" and
                        data.get("token_type") == "bearer"):
                        
                        self.log_test("Admin Login Functionality", True,
                                    f"Login successful. User ID: {user_data.get('id')}, "
                                    f"Role: {user_data.get('role')}, "
                                    f"Full Name: {user_data.get('full_name')}, "
                                    f"Token Length: {len(self.admin_token)} characters")
                        return True
                    else:
                        self.log_test("Admin Login Functionality", False,
                                    f"Invalid user data: Email={user_data.get('email')}, "
                                    f"Role={user_data.get('role')}, Token Type={data.get('token_type')}")
                        return False
                else:
                    self.log_test("Admin Login Functionality", False,
                                f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("Admin Login Functionality", False,
                            f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_jwt_token_generation_and_validation(self):
        """Test JWT token generation and validation"""
        if not self.admin_token:
            self.log_test("JWT Token Generation and Validation", False, "No admin token available")
            return False
        
        try:
            # Test token validation by making an authenticated request
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate that we get admin-specific data
                required_fields = ["total_users", "active_users", "total_listings", "active_listings"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("JWT Token Generation and Validation", True,
                                f"Token validation successful. Admin stats retrieved: "
                                f"Users={data.get('total_users')}, "
                                f"Listings={data.get('total_listings')}, "
                                f"Orders={data.get('total_orders')}")
                    return True
                else:
                    self.log_test("JWT Token Generation and Validation", False,
                                f"Token valid but missing admin data fields: {missing_fields}")
                    return False
            elif response.status_code == 401:
                self.log_test("JWT Token Generation and Validation", False,
                            "Token validation failed - 401 Unauthorized")
                return False
            elif response.status_code == 403:
                self.log_test("JWT Token Generation and Validation", False,
                            "Token valid but insufficient permissions - 403 Forbidden")
                return False
            else:
                self.log_test("JWT Token Generation and Validation", False,
                            f"Unexpected status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("JWT Token Generation and Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_protected_endpoints_access(self):
        """Test protected endpoints access with authentication"""
        if not self.admin_token:
            self.log_test("Protected Endpoints Access", False, "No admin token available")
            return False
        
        protected_endpoints = [
            ("/admin/stats", "Admin Statistics"),
            ("/admin/users", "User Management"),
            ("/profile/stats", "Profile Statistics"),
            ("/favorites/count", "Favorites Count")
        ]
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        successful_endpoints = 0
        
        for endpoint, description in protected_endpoints:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    successful_endpoints += 1
                    self.log_test(f"Protected Endpoint Access - {description}", True,
                                f"Successfully accessed {endpoint}")
                elif response.status_code == 401:
                    self.log_test(f"Protected Endpoint Access - {description}", False,
                                f"Authentication failed for {endpoint}")
                elif response.status_code == 403:
                    self.log_test(f"Protected Endpoint Access - {description}", False,
                                f"Insufficient permissions for {endpoint}")
                else:
                    self.log_test(f"Protected Endpoint Access - {description}", False,
                                f"Unexpected status {response.status_code} for {endpoint}")
                    
            except Exception as e:
                self.log_test(f"Protected Endpoint Access - {description}", False,
                            f"Exception accessing {endpoint}: {str(e)}")
        
        # Test without authentication
        try:
            response = self.session.get(f"{BASE_URL}/admin/stats")
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_test("Protected Endpoints - Unauthenticated Access", True,
                            "Correctly blocked unauthenticated access to protected endpoint")
            else:
                self.log_test("Protected Endpoints - Unauthenticated Access", False,
                            f"Should block unauthenticated access, got status {response.status_code}")
                
        except Exception as e:
            self.log_test("Protected Endpoints - Unauthenticated Access", False,
                        f"Exception: {str(e)}")
        
        return successful_endpoints >= 3  # At least 3 out of 4 should work
    
    def test_cors_headers_configuration(self):
        """Test CORS headers configuration for frontend communication"""
        try:
            # Test with Origin header (simulating frontend request)
            headers = {
                "Origin": "get_backend_url()",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            
            # Test preflight OPTIONS request
            response = self.session.options(f"{BASE_URL}/auth/login", headers=headers)
            
            cors_headers = {
                "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
                "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
                "access-control-allow-headers": response.headers.get("access-control-allow-headers"),
                "access-control-allow-credentials": response.headers.get("access-control-allow-credentials")
            }
            
            # Check if CORS headers are present
            cors_issues = []
            
            if not cors_headers["access-control-allow-origin"]:
                cors_issues.append("Missing Access-Control-Allow-Origin header")
            elif cors_headers["access-control-allow-origin"] not in ["*", "get_backend_url()"]:
                cors_issues.append(f"Unexpected Access-Control-Allow-Origin: {cors_headers['access-control-allow-origin']}")
            
            if not cors_headers["access-control-allow-methods"]:
                cors_issues.append("Missing Access-Control-Allow-Methods header")
            elif "POST" not in cors_headers["access-control-allow-methods"]:
                cors_issues.append("POST method not allowed in CORS")
            
            if not cors_headers["access-control-allow-headers"]:
                cors_issues.append("Missing Access-Control-Allow-Headers header")
            elif "authorization" not in cors_headers["access-control-allow-headers"].lower():
                cors_issues.append("Authorization header not allowed in CORS")
            
            if not cors_issues:
                self.log_test("CORS Headers Configuration", True,
                            f"CORS properly configured. "
                            f"Origin: {cors_headers['access-control-allow-origin']}, "
                            f"Methods: {cors_headers['access-control-allow-methods']}, "
                            f"Headers: {cors_headers['access-control-allow-headers']}, "
                            f"Credentials: {cors_headers['access-control-allow-credentials']}")
                
                # Test actual request with CORS
                login_headers = {"Origin": "get_backend_url()"}
                login_response = self.session.post(f"{BASE_URL}/auth/login", 
                                                 json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                                                 headers=login_headers)
                
                if login_response.status_code == 200:
                    response_cors = login_response.headers.get("access-control-allow-origin")
                    if response_cors:
                        self.log_test("CORS - Actual Request", True,
                                    f"CORS headers present in actual response: {response_cors}")
                    else:
                        self.log_test("CORS - Actual Request", False,
                                    "CORS headers missing in actual response")
                else:
                    self.log_test("CORS - Actual Request", False,
                                f"Login request failed: {login_response.status_code}")
                
                return True
            else:
                self.log_test("CORS Headers Configuration", False,
                            f"CORS configuration issues: {'; '.join(cors_issues)}")
                return False
                
        except Exception as e:
            self.log_test("CORS Headers Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication_edge_cases(self):
        """Test authentication edge cases and error handling"""
        test_cases = [
            {
                "name": "Invalid Email",
                "data": {"email": "invalid@example.com", "password": ADMIN_PASSWORD},
                "expected_status": 401
            },
            {
                "name": "Invalid Password",
                "data": {"email": ADMIN_EMAIL, "password": "wrongpassword"},
                "expected_status": 401
            },
            {
                "name": "Missing Email",
                "data": {"password": ADMIN_PASSWORD},
                "expected_status": 422
            },
            {
                "name": "Missing Password",
                "data": {"email": ADMIN_EMAIL},
                "expected_status": 422
            },
            {
                "name": "Empty Credentials",
                "data": {},
                "expected_status": 422
            }
        ]
        
        successful_cases = 0
        
        for case in test_cases:
            try:
                response = self.session.post(f"{BASE_URL}/auth/login", json=case["data"])
                
                if response.status_code == case["expected_status"]:
                    successful_cases += 1
                    self.log_test(f"Authentication Edge Case - {case['name']}", True,
                                f"Correctly returned status {response.status_code}")
                else:
                    self.log_test(f"Authentication Edge Case - {case['name']}", False,
                                f"Expected status {case['expected_status']}, got {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Authentication Edge Case - {case['name']}", False,
                            f"Exception: {str(e)}")
        
        return successful_cases >= 4  # At least 4 out of 5 should work correctly
    
    def test_token_expiry_handling(self):
        """Test token expiry and invalid token handling"""
        try:
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            response = self.session.get(f"{BASE_URL}/admin/stats", headers=invalid_headers)
            
            if response.status_code == 401:
                self.log_test("Token Expiry - Invalid Token", True,
                            "Correctly rejected invalid token")
            else:
                self.log_test("Token Expiry - Invalid Token", False,
                            f"Should reject invalid token, got status {response.status_code}")
            
            # Test with malformed token
            malformed_headers = {"Authorization": "Bearer"}
            response = self.session.get(f"{BASE_URL}/admin/stats", headers=malformed_headers)
            
            if response.status_code == 401:
                self.log_test("Token Expiry - Malformed Token", True,
                            "Correctly rejected malformed token")
            else:
                self.log_test("Token Expiry - Malformed Token", False,
                            f"Should reject malformed token, got status {response.status_code}")
            
            # Test with missing Bearer prefix
            no_bearer_headers = {"Authorization": self.admin_token}
            response = self.session.get(f"{BASE_URL}/admin/stats", headers=no_bearer_headers)
            
            if response.status_code == 401:
                self.log_test("Token Expiry - Missing Bearer Prefix", True,
                            "Correctly rejected token without Bearer prefix")
            else:
                self.log_test("Token Expiry - Missing Bearer Prefix", False,
                            f"Should reject token without Bearer prefix, got status {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Token Expiry Handling", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🔐 Starting Authentication System Testing for Cataloro Marketplace")
        print(f"Testing against: {BASE_URL}")
        print("=" * 80)
        
        # Test sequence
        tests = [
            ("Basic API Connectivity", self.test_basic_api_connectivity),
            ("Admin Login Functionality", self.test_admin_login_functionality),
            ("JWT Token Generation and Validation", self.test_jwt_token_generation_and_validation),
            ("Protected Endpoints Access", self.test_protected_endpoints_access),
            ("CORS Headers Configuration", self.test_cors_headers_configuration),
            ("Authentication Edge Cases", self.test_authentication_edge_cases),
            ("Token Expiry Handling", self.test_token_expiry_handling)
        ]
        
        passed = 0
        total = 0
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                total += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                total += 1
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 AUTHENTICATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed}/{total} tests passed)")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        # Critical findings
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for failed in failed_tests:
                print(f"   • {failed['test']}: {failed['details']}")
        
        print(f"\n✅ WORKING FEATURES:")
        passed_tests = [r for r in self.test_results if r["success"]]
        for passed_test in passed_tests:
            print(f"   • {passed_test['test']}")
        
        # Specific authentication readiness assessment
        print(f"\n🔍 AUTHENTICATION SYSTEM READINESS:")
        core_auth_tests = ["Basic API Connectivity", "Admin Login Functionality", 
                          "JWT Token Generation and Validation", "Protected Endpoints Access"]
        core_passed = sum(1 for r in self.test_results 
                         if r["success"] and any(core in r["test"] for core in core_auth_tests))
        
        if core_passed >= 3:
            print("✅ Authentication system is READY for frontend integration")
        else:
            print("❌ Authentication system has CRITICAL ISSUES that need fixing")
        
        return success_rate >= 80  # Consider 80%+ as success

if __name__ == "__main__":
    tester = AuthenticationTestSuite()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 AUTHENTICATION TESTING COMPLETED SUCCESSFULLY")
        print("The enhanced login page should work correctly with the backend services.")
        sys.exit(0)
    else:
        print(f"\n⚠️  AUTHENTICATION TESTING COMPLETED WITH ISSUES")
        print("Some authentication features may not work properly with the frontend.")
        sys.exit(1)