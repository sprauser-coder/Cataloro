#!/usr/bin/env python3
"""
Purple Modern Design Backend Testing
Testing backend API functionality after implementing purple modern design styling
Focus: Admin authentication, basic endpoints, listings API, core functionality integrity
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BASE_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class PurpleDesignBackendTest:
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
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Marketplace API" in data["message"]:
                    self.log_test("Basic API Connectivity", True, 
                                f"API responding correctly: {data['message']}")
                    return True
                else:
                    self.log_test("Basic API Connectivity", False, 
                                f"Unexpected response format: {data}")
                    return False
            else:
                self.log_test("Basic API Connectivity", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Basic API Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_authentication(self):
        """Test admin authentication with admin@marketplace.com / admin123"""
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
                    if (user_data.get("email") == ADMIN_EMAIL and 
                        user_data.get("role") == "admin"):
                        self.log_test("Admin Authentication", True, 
                                    f"Successfully authenticated admin user: {user_data.get('full_name', 'Admin')}")
                        return True
                    else:
                        self.log_test("Admin Authentication", False, 
                                    f"Invalid user data: email={user_data.get('email')}, role={user_data.get('role')}")
                        return False
                else:
                    self.log_test("Admin Authentication", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("Admin Authentication", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_cors_headers(self):
        """Test CORS configuration for frontend integration"""
        try:
            # Test preflight request
            response = self.session.options(f"{BASE_URL}/auth/login")
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
            }
            
            # Check if CORS is properly configured
            if cors_headers["Access-Control-Allow-Origin"]:
                self.log_test("CORS Configuration", True, 
                            f"CORS headers present: Origin={cors_headers['Access-Control-Allow-Origin']}")
                return True
            else:
                self.log_test("CORS Configuration", False, 
                            "CORS headers missing or incomplete")
                return False
                
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_listings_api_basic(self):
        """Test basic listings API functionality"""
        try:
            # Test GET /listings endpoint
            response = self.session.get(f"{BASE_URL}/listings")
            
            if response.status_code == 200:
                listings = response.json()
                
                if isinstance(listings, list):
                    self.log_test("Listings API - Basic GET", True, 
                                f"Retrieved {len(listings)} listings successfully")
                    
                    # Test listings structure if any exist
                    if listings:
                        first_listing = listings[0]
                        required_fields = ["id", "title", "description", "price", "category", "status"]
                        missing_fields = [field for field in required_fields if field not in first_listing]
                        
                        if not missing_fields:
                            self.log_test("Listings API - Data Structure", True, 
                                        f"Listing structure valid: {first_listing.get('title', 'N/A')}")
                        else:
                            self.log_test("Listings API - Data Structure", False, 
                                        f"Missing fields in listing: {missing_fields}")
                    
                    return True
                else:
                    self.log_test("Listings API - Basic GET", False, 
                                f"Expected list, got: {type(listings)}")
                    return False
            else:
                self.log_test("Listings API - Basic GET", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Listings API - Basic GET", False, f"Exception: {str(e)}")
            return False
    
    def test_listings_count_endpoint(self):
        """Test listings count endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/listings/count")
            
            if response.status_code == 200:
                data = response.json()
                
                if "total_count" in data and isinstance(data["total_count"], int):
                    self.log_test("Listings Count Endpoint", True, 
                                f"Count endpoint working: {data['total_count']} total listings")
                    return True
                else:
                    self.log_test("Listings Count Endpoint", False, 
                                f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Listings Count Endpoint", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Listings Count Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_listings_pagination(self):
        """Test listings pagination functionality"""
        try:
            # Test with limit and skip parameters
            response = self.session.get(f"{BASE_URL}/listings?limit=5&skip=0")
            
            if response.status_code == 200:
                listings = response.json()
                
                if isinstance(listings, list) and len(listings) <= 5:
                    self.log_test("Listings Pagination", True, 
                                f"Pagination working: requested 5, got {len(listings)}")
                    return True
                else:
                    self.log_test("Listings Pagination", False, 
                                f"Pagination not working correctly: got {len(listings)} items")
                    return False
            else:
                self.log_test("Listings Pagination", False, 
                            f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Listings Pagination", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_protected_endpoints(self):
        """Test admin-protected endpoints work correctly"""
        if not self.admin_token:
            self.log_test("Admin Protected Endpoints", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test admin stats endpoint
            response = self.session.get(f"{BASE_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                
                # Validate stats structure
                required_fields = ["total_users", "active_users", "total_listings", "active_listings"]
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    self.log_test("Admin Stats Endpoint", True, 
                                f"Admin stats working: {stats['total_users']} users, {stats['active_listings']} active listings")
                    return True
                else:
                    self.log_test("Admin Stats Endpoint", False, 
                                f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("Admin Stats Endpoint", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Protected Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_categories_endpoint(self):
        """Test categories endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/categories")
            
            if response.status_code == 200:
                categories = response.json()
                
                if isinstance(categories, list) and len(categories) > 0:
                    expected_categories = ["Electronics", "Fashion", "Home & Garden", "Sports", "Books"]
                    found_categories = [cat for cat in expected_categories if cat in categories]
                    
                    if len(found_categories) >= 3:  # At least 3 expected categories
                        self.log_test("Categories Endpoint", True, 
                                    f"Categories working: {len(categories)} categories available")
                        return True
                    else:
                        self.log_test("Categories Endpoint", False, 
                                    f"Missing expected categories. Found: {found_categories}")
                        return False
                else:
                    self.log_test("Categories Endpoint", False, 
                                f"Invalid categories response: {categories}")
                    return False
            else:
                self.log_test("Categories Endpoint", False, 
                            f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Categories Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_cms_public_endpoints(self):
        """Test public CMS endpoints for frontend integration"""
        try:
            # Test site settings endpoint
            response = self.session.get(f"{BASE_URL}/cms/settings")
            
            if response.status_code == 200:
                settings = response.json()
                
                # Check for key settings that frontend needs
                key_fields = ["site_name", "hero_title", "primary_color", "secondary_color"]
                missing_fields = [field for field in key_fields if field not in settings]
                
                if not missing_fields:
                    self.log_test("CMS Public Settings", True, 
                                f"CMS settings working: site_name='{settings.get('site_name', 'N/A')}'")
                    return True
                else:
                    self.log_test("CMS Public Settings", False, 
                                f"Missing key fields: {missing_fields}")
                    return False
            else:
                self.log_test("CMS Public Settings", False, 
                            f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("CMS Public Settings", False, f"Exception: {str(e)}")
            return False
    
    def test_token_validation(self):
        """Test JWT token validation"""
        if not self.admin_token:
            self.log_test("Token Validation", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test a protected endpoint that requires authentication
            response = self.session.get(f"{BASE_URL}/profile/stats", headers=headers)
            
            if response.status_code == 200:
                self.log_test("Token Validation", True, "JWT token validation working correctly")
                return True
            else:
                self.log_test("Token Validation", False, 
                            f"Token validation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Token Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test API error handling"""
        try:
            # Test invalid endpoint
            response = self.session.get(f"{BASE_URL}/invalid-endpoint")
            
            if response.status_code == 404:
                self.log_test("Error Handling - 404", True, "404 errors handled correctly")
            else:
                self.log_test("Error Handling - 404", False, 
                            f"Expected 404, got: {response.status_code}")
            
            # Test unauthorized access
            response = self.session.get(f"{BASE_URL}/admin/stats")
            
            if response.status_code in [401, 403]:
                self.log_test("Error Handling - Unauthorized", True, "Unauthorized access blocked correctly")
                return True
            else:
                self.log_test("Error Handling - Unauthorized", False, 
                            f"Expected 401/403, got: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🎨 Purple Modern Design Backend Testing")
        print("Testing backend API functionality after styling changes")
        print("=" * 60)
        print(f"Backend URL: {BASE_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print("=" * 60)
        
        # Test sequence - order matters for dependencies
        tests = [
            ("Basic API Connectivity", self.test_basic_connectivity),
            ("CORS Configuration", self.test_cors_headers),
            ("Admin Authentication", self.test_admin_authentication),
            ("Token Validation", self.test_token_validation),
            ("Listings API - Basic", self.test_listings_api_basic),
            ("Listings Count Endpoint", self.test_listings_count_endpoint),
            ("Listings Pagination", self.test_listings_pagination),
            ("Admin Protected Endpoints", self.test_admin_protected_endpoints),
            ("Categories Endpoint", self.test_categories_endpoint),
            ("CMS Public Endpoints", self.test_cms_public_endpoints),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed = 0
        total = 0
        
        for test_name, test_func in tests:
            print(f"🧪 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                total += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                total += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PURPLE DESIGN BACKEND TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed}/{total} tests passed)")
        
        # Critical findings
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n🚨 ISSUES FOUND:")
            for failed in failed_tests:
                print(f"   ❌ {failed['test']}: {failed['details']}")
        
        print(f"\n✅ WORKING FEATURES:")
        passed_tests = [r for r in self.test_results if r['success']]
        for passed_test in passed_tests:
            print(f"   ✅ {passed_test['test']}")
        
        # Specific conclusions for the review request
        print(f"\n🎯 REVIEW REQUEST CONCLUSIONS:")
        
        auth_working = any("Admin Authentication" in r['test'] and r['success'] for r in self.test_results)
        api_working = any("Basic API Connectivity" in r['test'] and r['success'] for r in self.test_results)
        listings_working = any("Listings API" in r['test'] and r['success'] for r in self.test_results)
        
        print(f"   • Admin Authentication (admin@marketplace.com/admin123): {'✅ WORKING' if auth_working else '❌ FAILED'}")
        print(f"   • Basic API Endpoints: {'✅ WORKING' if api_working else '❌ FAILED'}")
        print(f"   • Listings API: {'✅ WORKING' if listings_working else '❌ FAILED'}")
        
        if success_rate >= 90:
            print(f"   • Backend Issues from Styling Changes: ✅ NONE DETECTED")
        elif success_rate >= 70:
            print(f"   • Backend Issues from Styling Changes: ⚠️ MINOR ISSUES")
        else:
            print(f"   • Backend Issues from Styling Changes: ❌ SIGNIFICANT ISSUES")
        
        return success_rate >= 80  # 80%+ success rate considered acceptable

if __name__ == "__main__":
    tester = PurpleDesignBackendTest()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 BACKEND TESTING COMPLETED SUCCESSFULLY")
        print("✅ Core functionality intact after purple design styling changes")
        sys.exit(0)
    else:
        print(f"\n⚠️ BACKEND TESTING COMPLETED WITH ISSUES")
        print("❌ Some backend functionality may have been affected by styling changes")
        sys.exit(1)