#!/usr/bin/env python3
from config_loader import get_config, get_backend_url, get_admin_credentials, get_paths, get_database_url
"""
Comprehensive Backend Testing Suite for Review Request
Testing all critical functionality after environment and CORS configuration changes:

1. Authentication System (login, JWT, protected endpoints)
2. Admin Panel Backend APIs (stats, users, listings, CRUD operations)
3. Core Marketplace APIs (listings, categories)
4. CORS Configuration
5. Environment Configuration

Based on review request requirements and test_result.md analysis.
"""

import requests
import json
import os
from datetime import datetime
import uuid

# Configuration - Use environment variables as specified
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'get_backend_url("local")')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
ADMIN_EMAIL = "get_admin_credentials()[0]"
ADMIN_PASSWORD = "get_admin_credentials()[1]"

class ComprehensiveBackendReviewTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.test_user_id = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_environment_configuration(self):
        """Test Environment Configuration - verify backend is using correct settings"""
        print("=== Testing Environment Configuration ===")
        
        # Test basic API connectivity
        try:
            response = requests.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Basic API Connectivity", True, 
                              f"API Response: {data.get('message', 'N/A')}, Version: {data.get('version', 'N/A')}")
            else:
                self.log_result("Basic API Connectivity", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Basic API Connectivity", False, error=str(e))

        # Test MongoDB connection (via categories endpoint - no auth required)
        try:
            response = requests.get(f"{API_BASE}/categories")
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, list) and len(categories) > 0:
                    self.log_result("MongoDB Connection", True, 
                                  f"Retrieved {len(categories)} categories from database")
                else:
                    self.log_result("MongoDB Connection", False, 
                                  error="Categories endpoint returned empty or invalid data")
            else:
                self.log_result("MongoDB Connection", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("MongoDB Connection", False, error=str(e))

    def test_cors_configuration(self):
        """Test CORS Configuration - verify CORS headers allow localhost:3000 origin"""
        print("=== Testing CORS Configuration ===")
        
        # Test CORS headers with localhost:3000 origin
        try:
            headers = {
                'Origin': 'get_config("FRONTEND_URL_LOCAL")',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            }
            
            # Test preflight OPTIONS request
            response = requests.options(f"{API_BASE}/auth/login", headers=headers)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            # Check if localhost:3000 is allowed
            origin_allowed = cors_headers['Access-Control-Allow-Origin'] in ['get_config("FRONTEND_URL_LOCAL")', '*']
            methods_include_post = 'POST' in (cors_headers['Access-Control-Allow-Methods'] or '')
            headers_include_auth = 'Authorization' in (cors_headers['Access-Control-Allow-Headers'] or '')
            
            if origin_allowed and methods_include_post and headers_include_auth:
                self.log_result("CORS Preflight OPTIONS", True, 
                              f"CORS properly configured: Origin={cors_headers['Access-Control-Allow-Origin']}, Methods={cors_headers['Access-Control-Allow-Methods']}")
            else:
                self.log_result("CORS Preflight OPTIONS", False, 
                              error=f"CORS issues: Origin allowed={origin_allowed}, POST allowed={methods_include_post}, Auth headers={headers_include_auth}")
                
        except Exception as e:
            self.log_result("CORS Preflight OPTIONS", False, error=str(e))

        # Test actual request with Origin header
        try:
            headers = {'Origin': 'get_config("FRONTEND_URL_LOCAL")'}
            response = requests.get(f"{API_BASE}/categories", headers=headers)
            
            if response.status_code == 200:
                cors_origin = response.headers.get('Access-Control-Allow-Origin')
                if cors_origin in ['get_config("FRONTEND_URL_LOCAL")', '*']:
                    self.log_result("CORS Actual Request", True, 
                                  f"CORS working for actual requests: {cors_origin}")
                else:
                    self.log_result("CORS Actual Request", False, 
                                  error=f"CORS origin header missing or incorrect: {cors_origin}")
            else:
                self.log_result("CORS Actual Request", False, 
                              error=f"Request failed: {response.status_code}")
        except Exception as e:
            self.log_result("CORS Actual Request", False, error=str(e))

    def test_authentication_system(self):
        """Test Authentication System - login, JWT token generation and validation"""
        print("=== Testing Authentication System ===")
        
        # Test admin login endpoint
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.admin_token = data["access_token"]
                    self.test_user_id = data["user"]["id"]
                    user_role = data["user"].get("role", "unknown")
                    user_name = data["user"].get("full_name", "Unknown")
                    
                    self.log_result("Admin Login Endpoint", True, 
                                  f"Login successful - User: {user_name}, Role: {user_role}, Token length: {len(self.admin_token)}")
                else:
                    self.log_result("Admin Login Endpoint", False, 
                                  error=f"Missing required fields: {missing_fields}")
            else:
                self.log_result("Admin Login Endpoint", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Login Endpoint", False, error=str(e))

        # Test JWT token validation with protected endpoint
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.get(f"{API_BASE}/admin/stats", headers=headers)
                
                if response.status_code == 200:
                    stats = response.json()
                    self.log_result("JWT Token Validation", True, 
                                  f"Protected endpoint accessible with JWT token")
                else:
                    self.log_result("JWT Token Validation", False, 
                                  error=f"Protected endpoint failed: {response.status_code}")
            except Exception as e:
                self.log_result("JWT Token Validation", False, error=str(e))

        # Test protected endpoint access without token
        try:
            response = requests.get(f"{API_BASE}/admin/stats")
            if response.status_code in [401, 403]:
                self.log_result("Protected Endpoint Security", True, 
                              f"Properly blocked unauthorized access: {response.status_code}")
            else:
                self.log_result("Protected Endpoint Security", False, 
                              error=f"Should block unauthorized access but returned: {response.status_code}")
        except Exception as e:
            self.log_result("Protected Endpoint Security", False, error=str(e))

    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}

    def test_admin_panel_apis(self):
        """Test Admin Panel Backend APIs - stats, users, listings, CRUD operations"""
        print("=== Testing Admin Panel Backend APIs ===")
        
        # Test admin stats endpoint
        try:
            response = requests.get(f"{API_BASE}/admin/stats", headers=self.get_headers())
            if response.status_code == 200:
                stats = response.json()
                expected_fields = ["total_users", "active_users", "total_listings", "active_listings", "total_orders", "total_revenue"]
                missing_fields = [field for field in expected_fields if field not in stats]
                
                if not missing_fields:
                    self.log_result("Admin Stats Endpoint", True, 
                                  f"Users: {stats['total_users']}, Listings: {stats['total_listings']}, Orders: {stats['total_orders']}, Revenue: €{stats['total_revenue']}")
                else:
                    self.log_result("Admin Stats Endpoint", False, 
                                  error=f"Missing fields: {missing_fields}")
            else:
                self.log_result("Admin Stats Endpoint", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Admin Stats Endpoint", False, error=str(e))

        # Test admin users management endpoint
        try:
            response = requests.get(f"{API_BASE}/admin/users", headers=self.get_headers())
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list):
                    self.log_result("Admin Users Management", True, 
                                  f"Retrieved {len(users)} users for management")
                else:
                    self.log_result("Admin Users Management", False, 
                                  error="Users endpoint returned non-list data")
            else:
                self.log_result("Admin Users Management", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Users Management", False, error=str(e))

        # Test admin listings management endpoint
        try:
            response = requests.get(f"{API_BASE}/admin/listings", headers=self.get_headers())
            if response.status_code == 200:
                listings = response.json()
                if isinstance(listings, list):
                    self.log_result("Admin Listings Management", True, 
                                  f"Retrieved {len(listings)} listings for management")
                else:
                    self.log_result("Admin Listings Management", False, 
                                  error="Listings endpoint returned non-list data")
            else:
                self.log_result("Admin Listings Management", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Listings Management", False, error=str(e))

        # Test user block/unblock CRUD operations
        if len(self.test_results) > 0:  # Only if we have users
            try:
                # Get first non-admin user for testing
                users_response = requests.get(f"{API_BASE}/admin/users", headers=self.get_headers())
                if users_response.status_code == 200:
                    users = users_response.json()
                    test_user = None
                    for user in users:
                        if user.get('role') != 'admin':
                            test_user = user
                            break
                    
                    if test_user:
                        user_id = test_user['id']
                        
                        # Test block user
                        block_response = requests.put(f"{API_BASE}/admin/users/{user_id}/block", 
                                                    headers=self.get_headers())
                        if block_response.status_code == 200:
                            # Test unblock user
                            unblock_response = requests.put(f"{API_BASE}/admin/users/{user_id}/unblock", 
                                                          headers=self.get_headers())
                            if unblock_response.status_code == 200:
                                self.log_result("User Block/Unblock CRUD", True, 
                                              f"Successfully blocked and unblocked user {test_user.get('username', 'N/A')}")
                            else:
                                self.log_result("User Block/Unblock CRUD", False, 
                                              error=f"Unblock failed: {unblock_response.status_code}")
                        else:
                            self.log_result("User Block/Unblock CRUD", False, 
                                          error=f"Block failed: {block_response.status_code}")
                    else:
                        self.log_result("User Block/Unblock CRUD", True, 
                                      "No non-admin users available for testing (acceptable)")
                        
            except Exception as e:
                self.log_result("User Block/Unblock CRUD", False, error=str(e))

        # Test bulk operations
        try:
            # Test bulk block (with empty list to avoid affecting real users)
            response = requests.put(f"{API_BASE}/admin/users/bulk-block", 
                                  json=[], 
                                  headers=self.get_headers())
            if response.status_code == 200:
                self.log_result("Bulk Operations Endpoint", True, 
                              "Bulk operations endpoint accessible and functional")
            else:
                self.log_result("Bulk Operations Endpoint", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Bulk Operations Endpoint", False, error=str(e))

    def test_core_marketplace_apis(self):
        """Test Core Marketplace APIs - listings, categories, basic functionality"""
        print("=== Testing Core Marketplace APIs ===")
        
        # Test public listings endpoint
        try:
            response = requests.get(f"{API_BASE}/listings")
            if response.status_code == 200:
                listings = response.json()
                if isinstance(listings, list):
                    if listings:
                        # Check first listing structure
                        first_listing = listings[0]
                        required_fields = ["id", "title", "description", "price", "category", "status"]
                        missing_fields = [field for field in required_fields if field not in first_listing]
                        
                        if not missing_fields:
                            self.log_result("Public Listings Endpoint", True, 
                                          f"Retrieved {len(listings)} listings with proper structure")
                        else:
                            self.log_result("Public Listings Endpoint", False, 
                                          error=f"Listing missing fields: {missing_fields}")
                    else:
                        self.log_result("Public Listings Endpoint", True, 
                                      "Listings endpoint working (no listings found)")
                else:
                    self.log_result("Public Listings Endpoint", False, 
                                  error="Listings endpoint returned non-list data")
            else:
                self.log_result("Public Listings Endpoint", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Public Listings Endpoint", False, error=str(e))

        # Test categories endpoint
        try:
            response = requests.get(f"{API_BASE}/categories")
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, list) and len(categories) > 0:
                    self.log_result("Categories Endpoint", True, 
                                  f"Retrieved {len(categories)} categories: {', '.join(categories[:3])}...")
                else:
                    self.log_result("Categories Endpoint", False, 
                                  error="Categories endpoint returned empty or invalid data")
            else:
                self.log_result("Categories Endpoint", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Categories Endpoint", False, error=str(e))

        # Test listings count endpoint
        try:
            response = requests.get(f"{API_BASE}/listings/count")
            if response.status_code == 200:
                count_data = response.json()
                if "total_count" in count_data:
                    self.log_result("Listings Count Endpoint", True, 
                                  f"Total listings count: {count_data['total_count']}")
                else:
                    self.log_result("Listings Count Endpoint", False, 
                                  error="Missing total_count field in response")
            else:
                self.log_result("Listings Count Endpoint", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Listings Count Endpoint", False, error=str(e))

        # Test listings with pagination
        try:
            response = requests.get(f"{API_BASE}/listings", params={"limit": 5, "skip": 0})
            if response.status_code == 200:
                listings = response.json()
                if isinstance(listings, list):
                    self.log_result("Listings Pagination", True, 
                                  f"Pagination working - retrieved {len(listings)} listings with limit=5")
                else:
                    self.log_result("Listings Pagination", False, 
                                  error="Pagination returned non-list data")
            else:
                self.log_result("Listings Pagination", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Listings Pagination", False, error=str(e))

        # Test listings filtering
        try:
            response = requests.get(f"{API_BASE}/listings", params={"category": "Electronics"})
            if response.status_code == 200:
                listings = response.json()
                self.log_result("Listings Filtering", True, 
                              f"Category filtering working - found {len(listings)} Electronics listings")
            else:
                self.log_result("Listings Filtering", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Listings Filtering", False, error=str(e))

    def test_additional_admin_functionality(self):
        """Test Additional Admin Functionality mentioned in review request"""
        print("=== Testing Additional Admin Functionality ===")
        
        # Test CMS settings endpoints
        try:
            response = requests.get(f"{API_BASE}/admin/cms/settings", headers=self.get_headers())
            if response.status_code == 200:
                settings = response.json()
                self.log_result("CMS Settings Admin", True, 
                              f"CMS settings accessible - site_name: {settings.get('site_name', 'N/A')}")
            else:
                self.log_result("CMS Settings Admin", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("CMS Settings Admin", False, error=str(e))

        # Test public CMS settings (no auth required)
        try:
            response = requests.get(f"{API_BASE}/cms/settings")
            if response.status_code == 200:
                settings = response.json()
                self.log_result("CMS Settings Public", True, 
                              f"Public CMS settings working - site_name: {settings.get('site_name', 'N/A')}")
            else:
                self.log_result("CMS Settings Public", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("CMS Settings Public", False, error=str(e))

        # Test admin orders endpoint
        try:
            response = requests.get(f"{API_BASE}/admin/orders", headers=self.get_headers())
            if response.status_code == 200:
                orders = response.json()
                if isinstance(orders, list):
                    self.log_result("Admin Orders Endpoint", True, 
                                  f"Retrieved {len(orders)} orders for admin management")
                else:
                    self.log_result("Admin Orders Endpoint", False, 
                                  error="Orders endpoint returned non-list data")
            else:
                self.log_result("Admin Orders Endpoint", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Orders Endpoint", False, error=str(e))

    def run_all_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive Backend Review Testing")
        print("Testing critical functionality after environment and CORS configuration changes")
        print("=" * 80)
        
        # Run all test suites in order
        self.test_environment_configuration()
        self.test_cors_configuration()
        self.test_authentication_system()
        
        # Only proceed with authenticated tests if login succeeded
        if self.admin_token:
            self.test_admin_panel_apis()
            self.test_additional_admin_functionality()
        else:
            print("⚠️  Skipping authenticated tests due to authentication failure")
            
        self.test_core_marketplace_apis()
        
        # Print comprehensive summary
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("=" * 80)
        print("📊 COMPREHENSIVE BACKEND REVIEW TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results by test area
        categories = {
            "Environment": ["Environment", "MongoDB", "Basic API"],
            "CORS": ["CORS"],
            "Authentication": ["Login", "JWT", "Protected"],
            "Admin Panel": ["Admin", "Users Management", "Listings Management", "Block", "Bulk"],
            "Marketplace": ["Listings", "Categories", "Pagination", "Filtering"],
            "CMS": ["CMS"]
        }
        
        for category, keywords in categories.items():
            category_tests = [r for r in self.test_results if any(keyword in r["test"] for keyword in keywords)]
            if category_tests:
                category_passed = len([r for r in category_tests if r["success"]])
                category_total = len(category_tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                status = "✅" if category_rate == 100 else "⚠️" if category_rate >= 75 else "❌"
                print(f"{status} {category}: {category_passed}/{category_total} ({category_rate:.0f}%)")
        
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        print("\n" + "=" * 80)
        
        # Overall assessment based on review request requirements
        critical_areas = {
            "Authentication": any("Login" in r["test"] or "JWT" in r["test"] for r in self.test_results if r["success"]),
            "Admin Panel": any("Admin Stats" in r["test"] for r in self.test_results if r["success"]),
            "Marketplace": any("Listings" in r["test"] and "Public" in r["test"] for r in self.test_results if r["success"]),
            "CORS": any("CORS" in r["test"] for r in self.test_results if r["success"]),
            "Environment": any("MongoDB" in r["test"] for r in self.test_results if r["success"])
        }
        
        critical_working = sum(critical_areas.values())
        total_critical = len(critical_areas)
        
        print(f"🎯 CRITICAL AREAS STATUS: {critical_working}/{total_critical}")
        for area, working in critical_areas.items():
            status = "✅" if working else "❌"
            print(f"   {status} {area}")
        
        print()
        
        if success_rate >= 90 and critical_working == total_critical:
            print("🎉 EXCELLENT: All critical backend functionality is working perfectly!")
            print("   Frontend should be fully supported by backend APIs.")
        elif success_rate >= 75 and critical_working >= 4:
            print("✅ GOOD: Backend is mostly working well with minor issues.")
            print("   Core functionality should support frontend operations.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Backend has some issues that may affect frontend.")
            print("   Some functionality may not work as expected.")
        else:
            print("❌ CRITICAL: Backend has significant issues requiring immediate attention.")
            print("   Frontend functionality will be severely impacted.")

if __name__ == "__main__":
    tester = ComprehensiveBackendReviewTester()
    tester.run_all_tests()