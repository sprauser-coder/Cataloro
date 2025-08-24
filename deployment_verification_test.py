#!/usr/bin/env python3
"""
Cataloro Deployment Verification Test
Testing backend API functionality after URL configuration fix for 217.154.0.82 deployment.

Focus areas:
1. Core API endpoints accessibility on http://217.154.0.82/api/
2. Authentication endpoint (POST /api/auth/login) with admin@marketplace.com/admin123
3. CMS settings endpoint (GET /api/cms/settings) 
4. Categories endpoint (GET /api/categories)
5. Basic listings endpoint (GET /api/listings)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Using the new deployment URL
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class DeploymentVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
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
    
    def test_root_api_endpoint(self):
        """Test 1: Core API Root Endpoint - GET /api/"""
        print("🌐 Testing Core API Root Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "API" in data["message"]:
                    self.log_test(
                        "Core API Root Endpoint", 
                        True, 
                        f"API accessible at {BACKEND_URL}. Response: {data}"
                    )
                    return True
                else:
                    self.log_test(
                        "Core API Root Endpoint", 
                        False, 
                        f"Unexpected response format: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Core API Root Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Core API Root Endpoint", False, f"Connection error: {str(e)}")
            return False
    
    def test_authentication_endpoint(self):
        """Test 2: Authentication Endpoint - POST /api/auth/login"""
        print("🔐 Testing Authentication Endpoint...")
        
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "access_token" in data and "user" in data and "token_type" in data:
                    self.admin_token = data["access_token"]
                    user_info = data["user"]
                    
                    # Verify admin role
                    if user_info.get("role") == "admin":
                        self.log_test(
                            "Authentication Endpoint", 
                            True, 
                            f"Admin login successful. User: {user_info.get('email')}, Role: {user_info.get('role')}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Authentication Endpoint", 
                            False, 
                            f"Expected admin role, got: {user_info.get('role')}"
                        )
                        return False
                else:
                    self.log_test(
                        "Authentication Endpoint", 
                        False, 
                        "Missing required fields in login response"
                    )
                    return False
            else:
                self.log_test(
                    "Authentication Endpoint", 
                    False, 
                    f"Login failed - HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Authentication Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_cms_settings_endpoint(self):
        """Test 3: CMS Settings Endpoint - GET /api/cms/settings"""
        print("⚙️ Testing CMS Settings Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/cms/settings")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected CMS settings fields
                expected_fields = ["site_name", "site_tagline", "primary_color", "secondary_color"]
                missing_fields = [field for field in expected_fields if field not in data]
                
                if not missing_fields:
                    site_name = data.get("site_name", "Unknown")
                    self.log_test(
                        "CMS Settings Endpoint", 
                        True, 
                        f"CMS settings accessible. Site name: '{site_name}', Total fields: {len(data)}"
                    )
                    return True
                else:
                    self.log_test(
                        "CMS Settings Endpoint", 
                        False, 
                        f"Missing expected fields: {missing_fields}"
                    )
                    return False
            else:
                self.log_test(
                    "CMS Settings Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("CMS Settings Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_categories_endpoint(self):
        """Test 4: Categories Endpoint - GET /api/categories"""
        print("📂 Testing Categories Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/categories")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return a list of categories
                if isinstance(data, list) and len(data) > 0:
                    # Check for expected categories
                    expected_categories = ["Electronics", "Fashion", "Home & Garden"]
                    found_categories = [cat for cat in expected_categories if cat in data]
                    
                    self.log_test(
                        "Categories Endpoint", 
                        True, 
                        f"Categories retrieved successfully. Total: {len(data)}, Sample: {data[:3]}"
                    )
                    return True
                else:
                    self.log_test(
                        "Categories Endpoint", 
                        False, 
                        f"Expected non-empty list, got: {type(data)} with {len(data) if isinstance(data, list) else 'N/A'} items"
                    )
                    return False
            else:
                self.log_test(
                    "Categories Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Categories Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_listings_endpoint(self):
        """Test 5: Basic Listings Endpoint - GET /api/listings"""
        print("📋 Testing Basic Listings Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/listings")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return a list (even if empty)
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check structure of first listing
                        first_listing = data[0]
                        required_fields = ["id", "title", "seller_id", "status", "created_at"]
                        missing_fields = [field for field in required_fields if field not in first_listing]
                        
                        if not missing_fields:
                            self.log_test(
                                "Basic Listings Endpoint", 
                                True, 
                                f"Listings retrieved successfully. Total: {len(data)}, First listing: '{first_listing.get('title', 'Unknown')}'"
                            )
                            return True
                        else:
                            self.log_test(
                                "Basic Listings Endpoint", 
                                False, 
                                f"Listing structure incomplete. Missing fields: {missing_fields}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Basic Listings Endpoint", 
                            True, 
                            "Listings endpoint accessible (no listings found, but endpoint working)"
                        )
                        return True
                else:
                    self.log_test(
                        "Basic Listings Endpoint", 
                        False, 
                        f"Expected list, got: {type(data)}"
                    )
                    return False
            else:
                self.log_test(
                    "Basic Listings Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Basic Listings Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_authenticated_endpoint(self):
        """Test 6: Authenticated Endpoint Access - Verify token works"""
        print("🔑 Testing Authenticated Endpoint Access...")
        
        if not self.admin_token:
            self.log_test("Authenticated Endpoint Access", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify profile data structure
                if "email" in data and "role" in data:
                    self.log_test(
                        "Authenticated Endpoint Access", 
                        True, 
                        f"Authenticated access working. Profile for: {data.get('email')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Authenticated Endpoint Access", 
                        False, 
                        "Profile data structure incomplete"
                    )
                    return False
            elif response.status_code == 401:
                self.log_test(
                    "Authenticated Endpoint Access", 
                    False, 
                    "Token authentication failed - 401 Unauthorized"
                )
                return False
            else:
                self.log_test(
                    "Authenticated Endpoint Access", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Authenticated Endpoint Access", False, f"Exception: {str(e)}")
            return False
    
    def test_cors_configuration(self):
        """Test 7: CORS Configuration - Verify CORS headers are present"""
        print("🌐 Testing CORS Configuration...")
        
        try:
            # Make a simple request and check for CORS headers
            response = self.session.get(f"{BACKEND_URL}/categories")
            
            if response.status_code == 200:
                # Check for CORS headers
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
                }
                
                # At least Access-Control-Allow-Origin should be present
                if cors_headers["Access-Control-Allow-Origin"]:
                    self.log_test(
                        "CORS Configuration", 
                        True, 
                        f"CORS headers present. Origin: {cors_headers['Access-Control-Allow-Origin']}"
                    )
                    return True
                else:
                    self.log_test(
                        "CORS Configuration", 
                        False, 
                        "No CORS headers found in response"
                    )
                    return False
            else:
                self.log_test(
                    "CORS Configuration", 
                    False, 
                    f"Could not test CORS - HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all deployment verification tests"""
        print("=" * 80)
        print("🚀 CATALORO DEPLOYMENT VERIFICATION TEST SUITE")
        print("Testing backend API functionality after URL configuration fix")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        tests = [
            self.test_root_api_endpoint,
            self.test_authentication_endpoint,
            self.test_cms_settings_endpoint,
            self.test_categories_endpoint,
            self.test_listings_endpoint,
            self.test_authenticated_endpoint,
            self.test_cors_configuration
        ]
        
        for test in tests:
            test()
        
        # Summary
        print("=" * 80)
        print("📊 DEPLOYMENT VERIFICATION SUMMARY")
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
        
        if len(passed_tests) == len(self.test_results):
            print("🎉 ALL TESTS PASSED! Deployment verification successful.")
            print("✅ Backend is fully accessible from 217.154.0.82")
            print("✅ URL configuration fix is working correctly")
        elif len(passed_tests) >= 5:  # At least core functionality working
            print("⚠️  MOSTLY WORKING: Core functionality is accessible.")
            print("✅ Backend deployment is functional with minor issues")
        else:
            print("🚨 CRITICAL ISSUES FOUND: Deployment has significant problems.")
            print("❌ URL configuration may not be working correctly")
        
        print("=" * 80)
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = DeploymentVerificationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)