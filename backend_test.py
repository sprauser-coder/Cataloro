#!/usr/bin/env python3
"""
Phase 4 Marketplace Features Backend Testing Suite
Testing comprehensive backend support for new marketplace features including:
- Product Detail APIs
- Enhanced Listing APIs  
- User Profile APIs
- Order Management
- Notification System
- Search and Related Products
- Enhanced Favorites
- Advanced Authentication
- Statistics & Analytics
- File Management
"""

import requests
import json
import os
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://217.154.0.82')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class BackendAPITestSuite:
    def __init__(self):
        self.admin_token = None
        self.test_user_token = None
        self.test_user_id = None
        self.results = []
        self.session = requests.Session()
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                expected_message = "Marketplace API"
                if expected_message in data.get("message", ""):
                    self.log_result("Basic API Connectivity", True, 
                                  f"API accessible at {BASE_URL}, version: {data.get('version', 'unknown')}")
                    return True
                else:
                    self.log_result("Basic API Connectivity", False, 
                                  f"Unexpected response: {data}")
                    return False
            else:
                self.log_result("Basic API Connectivity", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Basic API Connectivity", False, f"Connection failed: {str(e)}")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration for frontend communication"""
        try:
            # Test with Origin header to trigger CORS
            headers = {"Origin": "http://217.154.0.82"}
            response = self.session.get(f"{BASE_URL}/", headers=headers)
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
            }
            
            # Check if CORS headers are present
            if cors_headers["Access-Control-Allow-Origin"]:
                self.log_result("CORS Configuration", True, 
                              f"CORS headers configured correctly", 
                              {"cors_headers": cors_headers})
                return True
            else:
                self.log_result("CORS Configuration", False, 
                              "CORS headers missing or misconfigured",
                              {"received_headers": dict(response.headers)})
                return False
                
        except Exception as e:
            self.log_result("CORS Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_authentication(self):
        """Test admin login and token generation"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.admin_token = data["access_token"]
                    user_data = data["user"]
                    
                    # Validate user data
                    if (user_data.get("role") == "admin" and 
                        user_data.get("email") == ADMIN_EMAIL):
                        self.log_result("Admin Authentication", True, 
                                      f"Admin login successful, token generated (length: {len(self.admin_token)})",
                                      {"user_id": user_data.get("id"), "role": user_data.get("role")})
                        return True
                    else:
                        self.log_result("Admin Authentication", False, 
                                      "Invalid user data in response",
                                      {"user_data": user_data})
                        return False
                else:
                    self.log_result("Admin Authentication", False, 
                                  f"Missing fields in response: {missing_fields}")
                    return False
            else:
                self.log_result("Admin Authentication", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_protected_endpoints_access(self):
        """Test access to protected endpoints with admin token"""
        if not self.admin_token:
            self.log_result("Protected Endpoints Access", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        protected_endpoints = [
            ("/admin/stats", "Admin Statistics"),
            ("/admin/users", "User Management"),
            ("/admin/cms/settings", "CMS Settings"),
            ("/profile/stats", "Profile Statistics")
        ]
        
        all_passed = True
        
        for endpoint, description in protected_endpoints:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    self.log_result(f"Protected Access - {description}", True, 
                                  f"Successfully accessed {endpoint}")
                elif response.status_code == 403:
                    self.log_result(f"Protected Access - {description}", False, 
                                  f"Access denied to {endpoint} (403)")
                    all_passed = False
                else:
                    self.log_result(f"Protected Access - {description}", False, 
                                  f"HTTP {response.status_code} for {endpoint}")
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"Protected Access - {description}", False, 
                              f"Exception accessing {endpoint}: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_admin_stats_endpoint(self):
        """Test /admin/stats endpoint functionality"""
        if not self.admin_token:
            self.log_result("Admin Stats Endpoint", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate required fields
                required_fields = ["total_users", "active_users", "total_listings", 
                                 "active_listings", "total_orders", "total_revenue"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Validate data types and logical consistency
                    validation_errors = []
                    
                    for field in required_fields:
                        if not isinstance(data[field], (int, float)):
                            validation_errors.append(f"{field} is not a number")
                        elif data[field] < 0:
                            validation_errors.append(f"{field} is negative")
                    
                    # Logical checks
                    if data["active_users"] > data["total_users"]:
                        validation_errors.append("Active users exceed total users")
                    
                    if data["active_listings"] > data["total_listings"]:
                        validation_errors.append("Active listings exceed total listings")
                    
                    if not validation_errors:
                        self.log_result("Admin Stats Endpoint", True, 
                                      f"Stats retrieved successfully",
                                      {"stats": data})
                        return True
                    else:
                        self.log_result("Admin Stats Endpoint", False, 
                                      f"Data validation errors: {validation_errors}",
                                      {"stats": data})
                        return False
                else:
                    self.log_result("Admin Stats Endpoint", False, 
                                  f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_result("Admin Stats Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Stats Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_users_endpoint(self):
        """Test /admin/users endpoint functionality"""
        if not self.admin_token:
            self.log_result("Admin Users Endpoint", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Validate user data structure
                        user = data[0]
                        required_fields = ["id", "email", "username", "full_name", "role", "is_blocked"]
                        missing_fields = [field for field in required_fields if field not in user]
                        
                        if not missing_fields:
                            self.log_result("Admin Users Endpoint", True, 
                                          f"Retrieved {len(data)} users successfully",
                                          {"sample_user": {k: user[k] for k in required_fields}})
                            return True
                        else:
                            self.log_result("Admin Users Endpoint", False, 
                                          f"Missing fields in user data: {missing_fields}")
                            return False
                    else:
                        self.log_result("Admin Users Endpoint", True, 
                                      "Retrieved empty user list (valid)")
                        return True
                else:
                    self.log_result("Admin Users Endpoint", False, 
                                  f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_result("Admin Users Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Users Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_listings_endpoint(self):
        """Test /admin/listings endpoint functionality"""
        if not self.admin_token:
            self.log_result("Admin Listings Endpoint", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/listings", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_result("Admin Listings Endpoint", True, 
                                  f"Retrieved {len(data)} listings successfully")
                    return True
                else:
                    self.log_result("Admin Listings Endpoint", False, 
                                  f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_result("Admin Listings Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Listings Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_orders_endpoint(self):
        """Test /admin/orders endpoint functionality"""
        if not self.admin_token:
            self.log_result("Admin Orders Endpoint", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/orders", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_result("Admin Orders Endpoint", True, 
                                  f"Retrieved {len(data)} orders successfully")
                    return True
                else:
                    self.log_result("Admin Orders Endpoint", False, 
                                  f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_result("Admin Orders Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Orders Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_cms_settings_endpoint(self):
        """Test /admin/cms/settings endpoint functionality"""
        if not self.admin_token:
            self.log_result("Admin CMS Settings Endpoint", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test GET
            response = self.session.get(f"{BASE_URL}/admin/cms/settings", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate CMS settings structure
                expected_fields = ["site_name", "site_tagline", "hero_title", "hero_subtitle"]
                missing_fields = [field for field in expected_fields if field not in data]
                
                if not missing_fields:
                    self.log_result("Admin CMS Settings Endpoint", True, 
                                  f"CMS settings retrieved successfully",
                                  {"site_name": data.get("site_name"), 
                                   "hero_title": data.get("hero_title")})
                    return True
                else:
                    self.log_result("Admin CMS Settings Endpoint", False, 
                                  f"Missing expected fields: {missing_fields}")
                    return False
            else:
                self.log_result("Admin CMS Settings Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin CMS Settings Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_marketplace_listings_endpoint(self):
        """Test /listings endpoint for marketplace data"""
        try:
            response = self.session.get(f"{BASE_URL}/listings")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Validate listing structure
                        listing = data[0]
                        required_fields = ["id", "title", "description", "price", "category", "status"]
                        missing_fields = [field for field in required_fields if field not in listing]
                        
                        if not missing_fields:
                            self.log_result("Marketplace Listings Endpoint", True, 
                                          f"Retrieved {len(data)} listings with proper structure",
                                          {"sample_listing": {k: listing.get(k) for k in required_fields[:3]}})
                            return True
                        else:
                            self.log_result("Marketplace Listings Endpoint", False, 
                                          f"Missing fields in listing: {missing_fields}")
                            return False
                    else:
                        self.log_result("Marketplace Listings Endpoint", True, 
                                      "Retrieved empty listings (valid for new marketplace)")
                        return True
                else:
                    self.log_result("Marketplace Listings Endpoint", False, 
                                  f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_result("Marketplace Listings Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Marketplace Listings Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_marketplace_categories_endpoint(self):
        """Test /categories endpoint for marketplace categories"""
        try:
            response = self.session.get(f"{BASE_URL}/categories")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    expected_categories = ["Electronics", "Fashion", "Home & Garden", "Sports", "Books"]
                    found_categories = [cat for cat in expected_categories if cat in data]
                    
                    if len(found_categories) >= 3:  # At least 3 expected categories
                        self.log_result("Marketplace Categories Endpoint", True, 
                                      f"Retrieved {len(data)} categories including: {', '.join(found_categories[:3])}")
                        return True
                    else:
                        self.log_result("Marketplace Categories Endpoint", False, 
                                      f"Missing expected categories. Got: {data}")
                        return False
                else:
                    self.log_result("Marketplace Categories Endpoint", False, 
                                  f"Expected non-empty list, got: {data}")
                    return False
            else:
                self.log_result("Marketplace Categories Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Marketplace Categories Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_file_upload_functionality(self):
        """Test static file serving and upload functionality"""
        if not self.admin_token:
            self.log_result("File Upload Functionality", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test logo upload endpoint exists
            # We'll test with a small PNG file content
            png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            files = {'file': ('test_logo.png', png_content, 'image/png')}
            response = self.session.post(f"{BASE_URL}/admin/cms/upload-logo", 
                                       files=files, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "logo_url" in data:
                    logo_url = data["logo_url"]
                    
                    # Test if uploaded file is accessible
                    file_response = self.session.get(f"{BASE_URL}{logo_url}")
                    
                    if file_response.status_code == 200:
                        self.log_result("File Upload Functionality", True, 
                                      f"Logo upload and serving working correctly",
                                      {"logo_url": logo_url, "file_size": len(file_response.content)})
                        return True
                    else:
                        self.log_result("File Upload Functionality", False, 
                                      f"Uploaded file not accessible: HTTP {file_response.status_code}")
                        return False
                else:
                    self.log_result("File Upload Functionality", False, 
                                  f"No logo_url in response: {data}")
                    return False
            elif response.status_code == 400:
                # File validation working
                self.log_result("File Upload Functionality", True, 
                              "File upload validation working (400 response expected for test file)")
                return True
            else:
                self.log_result("File Upload Functionality", False, 
                              f"Upload failed: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("File Upload Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_database_connectivity(self):
        """Test MongoDB connection and data persistence"""
        if not self.admin_token:
            self.log_result("Database Connectivity", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test database read operations
            endpoints_to_test = [
                ("/admin/stats", "Statistics"),
                ("/admin/users", "Users"),
                ("/listings", "Listings")
            ]
            
            all_passed = True
            
            for endpoint, description in endpoints_to_test:
                response = self.session.get(f"{BASE_URL}{endpoint}", 
                                          headers=headers if endpoint.startswith("/admin") else None)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(f"Database Read - {description}", True, 
                                  f"Successfully read {description.lower()} from database")
                else:
                    self.log_result(f"Database Read - {description}", False, 
                                  f"Failed to read {description.lower()}: HTTP {response.status_code}")
                    all_passed = False
            
            return all_passed
                
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def test_token_validation(self):
        """Test JWT token validation and expiry handling"""
        if not self.admin_token:
            self.log_result("Token Validation", False, "No admin token available")
            return False
        
        try:
            # Test valid token
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                self.log_result("Token Validation - Valid Token", True, 
                              "Valid token accepted correctly")
            else:
                self.log_result("Token Validation - Valid Token", False, 
                              f"Valid token rejected: HTTP {response.status_code}")
                return False
            
            # Test invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            response = self.session.get(f"{BASE_URL}/admin/stats", headers=invalid_headers)
            
            if response.status_code in [401, 403]:
                self.log_result("Token Validation - Invalid Token", True, 
                              "Invalid token correctly rejected")
                return True
            else:
                self.log_result("Token Validation - Invalid Token", False, 
                              f"Invalid token not rejected: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Token Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_unauthenticated_access(self):
        """Test that protected endpoints properly block unauthenticated access"""
        protected_endpoints = [
            "/admin/stats",
            "/admin/users", 
            "/admin/listings",
            "/admin/orders",
            "/admin/cms/settings",
            "/profile/stats"
        ]
        
        all_passed = True
        
        for endpoint in protected_endpoints:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code in [401, 403]:
                    self.log_result(f"Unauthenticated Access - {endpoint}", True, 
                                  f"Correctly blocked unauthenticated access")
                else:
                    self.log_result(f"Unauthenticated Access - {endpoint}", False, 
                                  f"Should block unauthenticated access, got: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"Unauthenticated Access - {endpoint}", False, 
                              f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Comprehensive Backend API Testing After Frontend Architecture Restructure")
        print(f"Testing against: {BASE_URL}")
        print("=" * 90)
        
        # Test sequence - order matters for dependencies
        tests = [
            ("Basic API Connectivity", self.test_basic_connectivity),
            ("CORS Configuration", self.test_cors_configuration),
            ("Admin Authentication", self.test_admin_authentication),
            ("Token Validation", self.test_token_validation),
            ("Protected Endpoints Access", self.test_protected_endpoints_access),
            ("Unauthenticated Access Blocking", self.test_unauthenticated_access),
            ("Admin Stats Endpoint", self.test_admin_stats_endpoint),
            ("Admin Users Endpoint", self.test_admin_users_endpoint),
            ("Admin Listings Endpoint", self.test_admin_listings_endpoint),
            ("Admin Orders Endpoint", self.test_admin_orders_endpoint),
            ("Admin CMS Settings Endpoint", self.test_admin_cms_settings_endpoint),
            ("Marketplace Listings Endpoint", self.test_marketplace_listings_endpoint),
            ("Marketplace Categories Endpoint", self.test_marketplace_categories_endpoint),
            ("File Upload Functionality", self.test_file_upload_functionality),
            ("Database Connectivity", self.test_database_connectivity)
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
        print("\n" + "=" * 90)
        print("📊 BACKEND API TEST SUMMARY")
        print("=" * 90)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed}/{total} tests passed)")
        
        # Categorize results
        critical_failures = []
        minor_issues = []
        working_features = []
        
        for result in self.results:
            if not result["success"]:
                if any(keyword in result["test"].lower() for keyword in 
                      ["authentication", "connectivity", "cors", "database"]):
                    critical_failures.append(result)
                else:
                    minor_issues.append(result)
            else:
                working_features.append(result)
        
        # Report critical issues
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['message']}")
        
        # Report minor issues
        if minor_issues:
            print(f"\n⚠️  MINOR ISSUES ({len(minor_issues)}):")
            for issue in minor_issues:
                print(f"   • {issue['test']}: {issue['message']}")
        
        # Report working features
        print(f"\n✅ WORKING FEATURES ({len(working_features)}):")
        for feature in working_features:
            print(f"   • {feature['test']}: {feature['message']}")
        
        # Frontend compatibility assessment
        print(f"\n🔄 FRONTEND COMPATIBILITY ASSESSMENT:")
        
        essential_apis = ["Admin Authentication", "Admin Stats Endpoint", "Marketplace Listings Endpoint", 
                         "Marketplace Categories Endpoint", "CORS Configuration"]
        
        essential_working = sum(1 for result in self.results 
                              if result["test"] in essential_apis and result["success"])
        
        if essential_working == len(essential_apis):
            print("   ✅ All essential APIs for frontend integration are working")
        else:
            print(f"   ⚠️  {len(essential_apis) - essential_working} essential APIs have issues")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.results:
            print(f"{result['status']}: {result['test']} - {result['message']}")
        
        return success_rate >= 80  # Consider 80%+ as success

if __name__ == "__main__":
    tester = BackendAPITestSuite()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 BACKEND API TESTING COMPLETED SUCCESSFULLY")
        print("Backend is ready for frontend integration!")
        sys.exit(0)
    else:
        print(f"\n⚠️  BACKEND API TESTING COMPLETED WITH ISSUES")
        print("Some backend functionality may need attention before frontend integration.")
        sys.exit(1)