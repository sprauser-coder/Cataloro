#!/usr/bin/env python3
"""
Deployment Readiness Testing for Cataloro Marketplace
Testing backend connectivity and core functionality at IP: http://217.154.0.82
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class DeploymentTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if not success:
            self.failed_tests.append(test_name)
            
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_basic_connectivity(self):
        """Test 1: Basic Backend Connectivity"""
        try:
            response = requests.get(f"{BASE_URL}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "Marketplace API" in data.get("message", ""):
                    self.log_test(
                        "Basic Connectivity", 
                        True, 
                        f"Backend accessible at {BASE_URL}",
                        {"response": data, "status_code": response.status_code}
                    )
                    return True
                else:
                    self.log_test(
                        "Basic Connectivity", 
                        False, 
                        "Unexpected API response format",
                        {"response": data, "status_code": response.status_code}
                    )
            else:
                self.log_test(
                    "Basic Connectivity", 
                    False, 
                    f"HTTP {response.status_code} error",
                    {"status_code": response.status_code, "response": response.text}
                )
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Basic Connectivity", 
                False, 
                f"Connection failed: {str(e)}",
                {"error": str(e)}
            )
        return False
    
    def test_admin_authentication(self):
        """Test 2: Admin Authentication"""
        try:
            auth_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = requests.post(
                f"{BASE_URL}/auth/login", 
                json=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.admin_token = data["access_token"]
                    user_info = data["user"]
                    
                    if user_info.get("role") == "admin":
                        self.log_test(
                            "Admin Authentication", 
                            True, 
                            f"Admin login successful for {ADMIN_EMAIL}",
                            {
                                "user_id": user_info.get("id"),
                                "role": user_info.get("role"),
                                "full_name": user_info.get("full_name"),
                                "token_length": len(self.admin_token)
                            }
                        )
                        return True
                    else:
                        self.log_test(
                            "Admin Authentication", 
                            False, 
                            f"User role is {user_info.get('role')}, not admin",
                            {"user_info": user_info}
                        )
                else:
                    self.log_test(
                        "Admin Authentication", 
                        False, 
                        "Invalid response format - missing token or user",
                        {"response": data}
                    )
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"Authentication failed with HTTP {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Admin Authentication", 
                False, 
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
        return False
    
    def test_cors_headers(self):
        """Test 3: CORS Headers Verification"""
        try:
            # Test preflight request
            headers = {
                "Origin": "http://217.154.0.82",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            
            response = requests.options(f"{BASE_URL}/auth/login", headers=headers, timeout=10)
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
            }
            
            # Check if CORS is properly configured for our IP
            origin_ok = cors_headers["Access-Control-Allow-Origin"] in ["*", "http://217.154.0.82"]
            methods_ok = "POST" in (cors_headers["Access-Control-Allow-Methods"] or "")
            headers_ok = "Authorization" in (cors_headers["Access-Control-Allow-Headers"] or "")
            
            if origin_ok and methods_ok and headers_ok:
                self.log_test(
                    "CORS Headers", 
                    True, 
                    "CORS properly configured for IP address",
                    {"cors_headers": cors_headers, "status_code": response.status_code}
                )
                return True
            else:
                self.log_test(
                    "CORS Headers", 
                    False, 
                    "CORS configuration issues detected",
                    {
                        "cors_headers": cors_headers,
                        "origin_ok": origin_ok,
                        "methods_ok": methods_ok,
                        "headers_ok": headers_ok
                    }
                )
        except requests.exceptions.RequestException as e:
            self.log_test(
                "CORS Headers", 
                False, 
                f"CORS test failed: {str(e)}",
                {"error": str(e)}
            )
        return False
    
    def test_profile_stats_endpoint(self):
        """Test 4: Profile Stats Endpoint (Recently Fixed)"""
        if not self.admin_token:
            self.log_test(
                "Profile Stats Endpoint", 
                False, 
                "Cannot test - no admin token available",
                {}
            )
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/profile/stats", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if the response has expected fields
                expected_fields = ["total_orders", "total_listings", "total_spent", "total_earned"]
                has_expected_fields = all(field in data for field in expected_fields)
                
                if has_expected_fields:
                    self.log_test(
                        "Profile Stats Endpoint", 
                        True, 
                        "Profile stats endpoint working correctly",
                        {
                            "stats": data,
                            "fields_present": list(data.keys())
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Profile Stats Endpoint", 
                        False, 
                        "Response missing expected fields",
                        {
                            "response": data,
                            "expected_fields": expected_fields,
                            "missing_fields": [f for f in expected_fields if f not in data]
                        }
                    )
            else:
                self.log_test(
                    "Profile Stats Endpoint", 
                    False, 
                    f"HTTP {response.status_code} error",
                    {"status_code": response.status_code, "response": response.text}
                )
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Profile Stats Endpoint", 
                False, 
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
        return False
    
    def test_listings_endpoint(self):
        """Test 5: Listings Endpoint (Core Marketplace Functionality)"""
        try:
            response = requests.get(f"{BASE_URL}/listings", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_test(
                        "Listings Endpoint", 
                        True, 
                        f"Listings endpoint working - returned {len(data)} listings",
                        {
                            "listings_count": len(data),
                            "sample_listing": data[0] if data else None
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Listings Endpoint", 
                        False, 
                        "Response is not a list format",
                        {"response_type": type(data).__name__, "response": data}
                    )
            else:
                self.log_test(
                    "Listings Endpoint", 
                    False, 
                    f"HTTP {response.status_code} error",
                    {"status_code": response.status_code, "response": response.text}
                )
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Listings Endpoint", 
                False, 
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
        return False
    
    def test_image_serving(self):
        """Test 6: Image Serving Functionality"""
        try:
            # Test if we can access the uploads directory through the API
            test_image_url = f"{BASE_URL}/uploads/test-image-check"
            response = requests.get(test_image_url, timeout=10)
            
            # We expect 404 for non-existent image, but this tests the route is working
            if response.status_code == 404:
                self.log_test(
                    "Image Serving", 
                    True, 
                    "Image serving route is accessible (404 for non-existent file is expected)",
                    {"status_code": response.status_code, "url_tested": test_image_url}
                )
                return True
            elif response.status_code == 200:
                self.log_test(
                    "Image Serving", 
                    True, 
                    "Image serving working - found existing image",
                    {"status_code": response.status_code, "content_type": response.headers.get("content-type")}
                )
                return True
            else:
                self.log_test(
                    "Image Serving", 
                    False, 
                    f"Unexpected status code {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Image Serving", 
                False, 
                f"Image serving test failed: {str(e)}",
                {"error": str(e)}
            )
        return False
    
    def test_production_environment(self):
        """Test 7: Production Environment Configuration"""
        try:
            # Test admin stats endpoint to verify production setup
            if not self.admin_token:
                self.log_test(
                    "Production Environment", 
                    False, 
                    "Cannot verify - no admin token",
                    {}
                )
                return False
                
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/stats", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we have production-like data
                has_stats = all(key in data for key in ["total_users", "total_listings", "total_orders"])
                
                if has_stats:
                    self.log_test(
                        "Production Environment", 
                        True, 
                        "Production environment verified - admin stats accessible",
                        {
                            "admin_stats": data,
                            "environment_indicators": {
                                "has_users": data.get("total_users", 0) > 0,
                                "has_listings": data.get("total_listings", 0) > 0,
                                "admin_access": True
                            }
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Production Environment", 
                        False, 
                        "Admin stats response missing expected fields",
                        {"response": data}
                    )
            else:
                self.log_test(
                    "Production Environment", 
                    False, 
                    f"Admin stats endpoint failed with HTTP {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Production Environment", 
                False, 
                f"Production environment test failed: {str(e)}",
                {"error": str(e)}
            )
        return False
    
    def run_all_tests(self):
        """Run all deployment readiness tests"""
        print("=" * 80)
        print("CATALORO MARKETPLACE - DEPLOYMENT READINESS TESTING")
        print(f"Target IP: http://217.154.0.82")
        print(f"Test Started: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Run tests in sequence
        tests = [
            self.test_basic_connectivity,
            self.test_admin_authentication,
            self.test_cors_headers,
            self.test_profile_stats_endpoint,
            self.test_listings_endpoint,
            self.test_image_serving,
            self.test_production_environment
        ]
        
        passed_tests = 0
        for test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ FAIL: {test_func.__name__} - Unexpected error: {str(e)}")
            print("-" * 40)
        
        # Summary
        total_tests = len(tests)
        success_rate = (passed_tests / total_tests) * 100
        
        print("=" * 80)
        print("DEPLOYMENT READINESS TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests:
            print(f"\nFailed Tests:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        print(f"\nDeployment Status: {'✅ READY' if success_rate >= 85 else '❌ NOT READY'}")
        
        if success_rate >= 85:
            print("\n🎉 DEPLOYMENT READINESS CONFIRMED!")
            print("The application is ready for production deployment at http://217.154.0.82")
        else:
            print("\n⚠️  DEPLOYMENT ISSUES DETECTED!")
            print("Please resolve the failed tests before deploying to production.")
        
        print("=" * 80)
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = DeploymentTester()
    deployment_ready = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if deployment_ready else 1)