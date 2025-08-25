#!/usr/bin/env python3
"""
Route Discovery and Debugging Test Suite
Testing route registration and availability as requested in review
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Configuration
BASE_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class RouteDiscoveryTestSuite:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, details="", status_code=None):
        """Log test results with status codes"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "status_code": status_code
        })
        print(f"{status}: {test_name}")
        if status_code:
            print(f"   Status Code: {status_code}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_basic_connectivity(self):
        """Test basic connectivity to GET /api/ endpoint"""
        print("=== TESTING BASIC CONNECTIVITY ===")
        try:
            response = self.session.get(f"{BASE_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Basic API Connectivity", True, 
                             f"Response: {data}", response.status_code)
                return True
            else:
                self.log_test("Basic API Connectivity", False, 
                             f"Unexpected status code", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Basic API Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_admin(self):
        """Test admin authentication"""
        print("=== TESTING ADMIN AUTHENTICATION ===")
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                user_info = data.get("user", {})
                self.log_test("Admin Authentication", True, 
                             f"User ID: {user_info.get('id')}, Role: {user_info.get('role')}, Name: {user_info.get('full_name')}", 
                             response.status_code)
                return True
            else:
                self.log_test("Admin Authentication", False, 
                             f"Login failed: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_routes(self):
        """Test all available admin routes"""
        print("=== TESTING ADMIN ROUTES ===")
        
        if not self.admin_token:
            self.log_test("Admin Routes Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # List of admin routes to test
        admin_routes = [
            ("GET", "/admin/stats", "Admin Statistics"),
            ("GET", "/admin/users", "Admin Users List"),
            ("GET", "/admin/listings", "Admin Listings List"),
            ("GET", "/admin/orders", "Admin Orders List"),
        ]
        
        for method, route, description in admin_routes:
            try:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{route}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"{description} ({method} {route})", True, 
                                     f"Returned {len(data)} items", response.status_code)
                    elif isinstance(data, dict):
                        self.log_test(f"{description} ({method} {route})", True, 
                                     f"Returned data with keys: {list(data.keys())}", response.status_code)
                    else:
                        self.log_test(f"{description} ({method} {route})", True, 
                                     f"Response type: {type(data)}", response.status_code)
                else:
                    self.log_test(f"{description} ({method} {route})", False, 
                                 f"Error: {response.text[:200]}", response.status_code)
                    
            except Exception as e:
                self.log_test(f"{description} ({method} {route})", False, f"Exception: {str(e)}")
    
    def test_new_routes_404_debug(self):
        """Test new routes that are expected but showing 404"""
        print("=== TESTING NEW ROUTES (404 DEBUG) ===")
        
        if not self.admin_token:
            self.log_test("New Routes Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Routes that are expected but might be showing 404
        new_routes = [
            ("GET", "/admin/stats-by-timeframe", "Admin Stats by Timeframe"),
            ("GET", "/admin/stats/time-based", "Admin Time-based Stats"),
            ("POST", "/track-activity", "Track Activity"),
            ("GET", "/favorites/count", "Favorites Count"),
        ]
        
        for method, route, description in new_routes:
            try:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{route}", headers=headers)
                elif method == "POST":
                    # Try with minimal data for POST requests
                    response = self.session.post(f"{BASE_URL}{route}", headers=headers, json={})
                
                if response.status_code == 200:
                    self.log_test(f"{description} ({method} {route})", True, 
                                 "Route is working", response.status_code)
                elif response.status_code == 404:
                    self.log_test(f"{description} ({method} {route})", False, 
                                 "Route not found (404)", response.status_code)
                elif response.status_code == 422:
                    self.log_test(f"{description} ({method} {route})", True, 
                                 "Route exists but validation error (expected for POST)", response.status_code)
                else:
                    self.log_test(f"{description} ({method} {route})", False, 
                                 f"Unexpected response: {response.text[:200]}", response.status_code)
                    
            except Exception as e:
                self.log_test(f"{description} ({method} {route})", False, f"Exception: {str(e)}")
    
    def test_profile_stats(self):
        """Test profile stats endpoints"""
        print("=== TESTING PROFILE STATS ===")
        
        if not self.admin_token:
            self.log_test("Profile Stats Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test profile stats with admin user
        try:
            response = self.session.get(f"{BASE_URL}/profile/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Profile Stats (Admin User)", True, 
                             f"Stats keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}", 
                             response.status_code)
            else:
                self.log_test("Profile Stats (Admin User)", False, 
                             f"Error: {response.text[:200]}", response.status_code)
                
        except Exception as e:
            self.log_test("Profile Stats (Admin User)", False, f"Exception: {str(e)}")
    
    def test_fastapi_docs(self):
        """Test FastAPI documentation endpoints"""
        print("=== TESTING FASTAPI DOCS ===")
        
        # Test /docs endpoint
        try:
            response = self.session.get(f"http://217.154.0.82/docs")
            
            if response.status_code == 200:
                self.log_test("FastAPI Docs (/docs)", True, 
                             f"Content length: {len(response.content)} bytes", response.status_code)
            else:
                self.log_test("FastAPI Docs (/docs)", False, 
                             "Docs not accessible", response.status_code)
                
        except Exception as e:
            self.log_test("FastAPI Docs (/docs)", False, f"Exception: {str(e)}")
        
        # Test /openapi.json endpoint
        try:
            response = self.session.get(f"http://217.154.0.82/openapi.json")
            
            if response.status_code == 200:
                data = response.json()
                paths = data.get("paths", {})
                self.log_test("OpenAPI JSON (/openapi.json)", True, 
                             f"Found {len(paths)} registered paths", response.status_code)
                
                # List some of the registered paths
                if paths:
                    print("   Registered paths sample:")
                    for i, path in enumerate(list(paths.keys())[:10]):  # Show first 10 paths
                        print(f"     {path}")
                    if len(paths) > 10:
                        print(f"     ... and {len(paths) - 10} more paths")
                    print()
            else:
                self.log_test("OpenAPI JSON (/openapi.json)", False, 
                             "OpenAPI spec not accessible", response.status_code)
                
        except Exception as e:
            self.log_test("OpenAPI JSON (/openapi.json)", False, f"Exception: {str(e)}")
    
    def test_additional_route_patterns(self):
        """Test additional common admin route patterns"""
        print("=== TESTING ADDITIONAL ROUTE PATTERNS ===")
        
        if not self.admin_token:
            self.log_test("Additional Routes Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Additional routes to test
        additional_routes = [
            ("GET", "/admin/cms/settings", "CMS Settings"),
            ("GET", "/cms/settings", "Public CMS Settings"),
            ("GET", "/categories", "Categories List"),
            ("GET", "/listings/count", "Listings Count"),
            ("GET", "/admin/navigation", "Navigation Items"),
        ]
        
        for method, route, description in additional_routes:
            try:
                if method == "GET":
                    # For public routes, don't use auth headers
                    if route.startswith("/cms/") or route == "/categories" or route == "/listings/count":
                        response = self.session.get(f"{BASE_URL}{route}")
                    else:
                        response = self.session.get(f"{BASE_URL}{route}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"{description} ({method} {route})", True, 
                                     f"Returned {len(data)} items", response.status_code)
                    elif isinstance(data, dict):
                        self.log_test(f"{description} ({method} {route})", True, 
                                     f"Returned data with keys: {list(data.keys())}", response.status_code)
                    else:
                        self.log_test(f"{description} ({method} {route})", True, 
                                     f"Response: {data}", response.status_code)
                else:
                    self.log_test(f"{description} ({method} {route})", False, 
                                 f"Error: {response.text[:200]}", response.status_code)
                    
            except Exception as e:
                self.log_test(f"{description} ({method} {route})", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all route discovery tests"""
        print("🚀 STARTING ROUTE DISCOVERY AND DEBUGGING TESTS")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Stopping tests.")
            return
        
        # Test admin authentication
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Some tests will be skipped.")
        
        # Run all test suites
        self.test_admin_routes()
        self.test_new_routes_404_debug()
        self.test_profile_stats()
        self.test_fastapi_docs()
        self.test_additional_route_patterns()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    status_info = f" (Status: {result['status_code']})" if result.get('status_code') else ""
                    print(f"   • {result['test']}{status_info}")
                    if result["details"]:
                        print(f"     {result['details']}")
            print()
        
        print("✅ WORKING ROUTES:")
        for result in self.test_results:
            if result["success"]:
                status_info = f" (Status: {result['status_code']})" if result.get('status_code') else ""
                print(f"   • {result['test']}{status_info}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    print("Route Discovery and Debugging Test Suite")
    print("Testing route registration and availability")
    print()
    
    test_suite = RouteDiscoveryTestSuite()
    test_suite.run_all_tests()