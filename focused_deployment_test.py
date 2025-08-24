#!/usr/bin/env python3
"""
Focused Deployment Test for Cataloro
Testing the specific endpoints mentioned in the review request after URL configuration fix.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Using the new deployment URL
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class FocusedDeploymentTester:
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
    
    def test_core_api_accessibility(self):
        """Test Core API endpoints accessibility on http://217.154.0.82/api/"""
        print("🌐 Testing Core API Accessibility...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Core API Accessibility", 
                    True, 
                    f"API root accessible at {BACKEND_URL}. Response: {data.get('message', 'Unknown')}"
                )
                return True
            else:
                self.log_test(
                    "Core API Accessibility", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Core API Accessibility", False, f"Connection error: {str(e)}")
            return False
    
    def test_authentication_login(self):
        """Test Authentication endpoint (POST /api/auth/login) with admin@marketplace.com/admin123"""
        print("🔐 Testing Authentication Login...")
        
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
                    
                    if user.get("email") == ADMIN_EMAIL and user.get("role") == "admin":
                        self.log_test(
                            "Authentication Login", 
                            True, 
                            f"Admin login successful. Email: {user.get('email')}, Role: {user.get('role')}, Token received"
                        )
                        return True
                    else:
                        self.log_test(
                            "Authentication Login", 
                            False, 
                            f"Login successful but user data incorrect. Email: {user.get('email')}, Role: {user.get('role')}"
                        )
                        return False
                else:
                    self.log_test(
                        "Authentication Login", 
                        False, 
                        "Login response missing required fields (access_token, user)"
                    )
                    return False
            else:
                self.log_test(
                    "Authentication Login", 
                    False, 
                    f"Login failed - HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Authentication Login", False, f"Exception: {str(e)}")
            return False
    
    def test_cms_settings(self):
        """Test CMS settings endpoint (GET /api/cms/settings)"""
        print("⚙️ Testing CMS Settings...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/cms/settings")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for key CMS fields
                key_fields = ["site_name", "site_tagline", "primary_color", "secondary_color", "hero_title"]
                present_fields = [field for field in key_fields if field in data]
                
                if len(present_fields) >= 4:  # Most key fields present
                    site_info = {
                        "site_name": data.get("site_name", "Unknown"),
                        "site_tagline": data.get("site_tagline", "Unknown"),
                        "total_fields": len(data)
                    }
                    self.log_test(
                        "CMS Settings", 
                        True, 
                        f"CMS settings accessible. Site: '{site_info['site_name']}', Fields: {site_info['total_fields']}"
                    )
                    return True
                else:
                    self.log_test(
                        "CMS Settings", 
                        False, 
                        f"CMS settings incomplete. Present fields: {present_fields}, Missing: {set(key_fields) - set(present_fields)}"
                    )
                    return False
            else:
                self.log_test(
                    "CMS Settings", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("CMS Settings", False, f"Exception: {str(e)}")
            return False
    
    def test_categories(self):
        """Test Categories endpoint (GET /api/categories)"""
        print("📂 Testing Categories...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/categories")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    # Check for expected categories
                    expected_categories = ["Electronics", "Fashion", "Home & Garden", "Sports", "Books"]
                    found_expected = [cat for cat in expected_categories if cat in data]
                    
                    self.log_test(
                        "Categories", 
                        True, 
                        f"Categories retrieved. Total: {len(data)}, Expected found: {len(found_expected)}, Categories: {data}"
                    )
                    return True
                else:
                    self.log_test(
                        "Categories", 
                        False, 
                        f"Categories endpoint returned invalid data. Type: {type(data)}, Length: {len(data) if isinstance(data, list) else 'N/A'}"
                    )
                    return False
            else:
                self.log_test(
                    "Categories", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Categories", False, f"Exception: {str(e)}")
            return False
    
    def test_basic_listings(self):
        """Test Basic listings endpoint (GET /api/listings)"""
        print("📋 Testing Basic Listings...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/listings")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check structure of listings
                        first_listing = data[0]
                        required_fields = ["id", "title", "seller_id", "status", "price", "category"]
                        present_fields = [field for field in required_fields if field in first_listing]
                        
                        listing_info = {
                            "total_listings": len(data),
                            "first_title": first_listing.get("title", "Unknown"),
                            "first_category": first_listing.get("category", "Unknown"),
                            "first_price": first_listing.get("price", first_listing.get("current_bid", "Unknown"))
                        }
                        
                        if len(present_fields) >= 4:  # Most required fields present
                            self.log_test(
                                "Basic Listings", 
                                True, 
                                f"Listings retrieved successfully. Count: {listing_info['total_listings']}, Sample: '{listing_info['first_title']}' ({listing_info['first_category']}) - €{listing_info['first_price']}"
                            )
                            return True
                        else:
                            self.log_test(
                                "Basic Listings", 
                                False, 
                                f"Listing structure incomplete. Present: {present_fields}, Missing: {set(required_fields) - set(present_fields)}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Basic Listings", 
                            True, 
                            "Listings endpoint accessible (no listings found, but endpoint working)"
                        )
                        return True
                else:
                    self.log_test(
                        "Basic Listings", 
                        False, 
                        f"Expected list, got: {type(data)}"
                    )
                    return False
            else:
                self.log_test(
                    "Basic Listings", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Basic Listings", False, f"Exception: {str(e)}")
            return False
    
    def test_frontend_backend_communication(self):
        """Test that frontend can communicate with backend using the new URL"""
        print("🔗 Testing Frontend-Backend Communication...")
        
        if not self.admin_token:
            self.log_test("Frontend-Backend Communication", False, "No admin token available for authenticated test")
            return False
        
        try:
            # Test an authenticated endpoint that frontend would use
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                
                if "email" in profile_data and "role" in profile_data:
                    self.log_test(
                        "Frontend-Backend Communication", 
                        True, 
                        f"Authenticated communication working. Profile retrieved for: {profile_data.get('email')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Frontend-Backend Communication", 
                        False, 
                        "Profile data structure incomplete"
                    )
                    return False
            elif response.status_code == 401:
                self.log_test(
                    "Frontend-Backend Communication", 
                    False, 
                    "Authentication failed - token not accepted"
                )
                return False
            else:
                self.log_test(
                    "Frontend-Backend Communication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Frontend-Backend Communication", False, f"Exception: {str(e)}")
            return False
    
    def test_url_configuration_fix(self):
        """Verify the URL configuration fix is working by testing multiple endpoints"""
        print("🔧 Testing URL Configuration Fix...")
        
        endpoints_to_test = [
            ("/", "Root API"),
            ("/categories", "Categories"),
            ("/cms/settings", "CMS Settings"),
            ("/listings", "Listings")
        ]
        
        successful_endpoints = []
        failed_endpoints = []
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    successful_endpoints.append(name)
                else:
                    failed_endpoints.append(f"{name} (HTTP {response.status_code})")
            except Exception as e:
                failed_endpoints.append(f"{name} (Error: {str(e)})")
        
        success_rate = len(successful_endpoints) / len(endpoints_to_test)
        
        if success_rate >= 0.75:  # At least 75% of endpoints working
            self.log_test(
                "URL Configuration Fix", 
                True, 
                f"URL configuration working. Successful endpoints: {', '.join(successful_endpoints)} ({success_rate*100:.0f}% success rate)"
            )
            return True
        else:
            self.log_test(
                "URL Configuration Fix", 
                False, 
                f"URL configuration issues. Failed endpoints: {', '.join(failed_endpoints)} ({success_rate*100:.0f}% success rate)"
            )
            return False
    
    def run_all_tests(self):
        """Run all focused deployment tests"""
        print("=" * 80)
        print("🎯 CATALORO FOCUSED DEPLOYMENT TEST")
        print("Testing specific endpoints after URL configuration fix for 217.154.0.82")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}/{ADMIN_PASSWORD}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        tests = [
            ("Core API Accessibility", self.test_core_api_accessibility),
            ("Authentication Login", self.test_authentication_login),
            ("CMS Settings", self.test_cms_settings),
            ("Categories", self.test_categories),
            ("Basic Listings", self.test_basic_listings),
            ("Frontend-Backend Communication", self.test_frontend_backend_communication),
            ("URL Configuration Fix", self.test_url_configuration_fix)
        ]
        
        for test_name, test_func in tests:
            test_func()
        
        # Summary
        print("=" * 80)
        print("📊 FOCUSED DEPLOYMENT TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print()
        
        if len(passed_tests) == len(self.test_results):
            print("🎉 ALL TESTS PASSED! URL configuration fix is working perfectly.")
            print("✅ Backend is fully accessible from 217.154.0.82")
            print("✅ All specified endpoints are functional")
            print("✅ Frontend-backend communication should work correctly")
        elif len(passed_tests) >= 5:  # Most tests passing
            print("⚠️  MOSTLY WORKING: URL configuration fix is largely successful.")
            print("✅ Core functionality accessible from 217.154.0.82")
            print("⚠️  Minor issues detected but not blocking")
        else:
            print("🚨 CRITICAL ISSUES: URL configuration fix has problems.")
            print("❌ Significant issues with backend accessibility")
        
        print("=" * 80)
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = FocusedDeploymentTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)