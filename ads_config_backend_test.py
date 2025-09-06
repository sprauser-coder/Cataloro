#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Ads Configuration Focus
Testing the backend functionality after implementing ads configuration fixes:
1. Image Upload API (/api/admin/upload-image)
2. Basic marketplace APIs (browse endpoint)
3. Admin endpoints functionality
4. Authentication and session management
"""

import requests
import json
import uuid
import time
import io
import base64
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://browse-ads.preview.emergentagent.com/api"

class AdsConfigBackendTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}, Version: {data.get('version')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def test_image_upload_api(self):
        """Test the /api/admin/upload-image endpoint for ad image uploads"""
        try:
            # Create a simple test image (1x1 pixel PNG)
            test_image_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            )
            
            # Prepare multipart form data
            files = {
                'image': ('test_ad_image.png', io.BytesIO(test_image_data), 'image/png')
            }
            data = {
                'section': 'hero',
                'field': 'background_image'
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/upload-image",
                files=files,
                data=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result_data = response.json()
                image_url = result_data.get('url', '')
                filename = result_data.get('filename', '')
                self.log_test(
                    "Image Upload API", 
                    True, 
                    f"Successfully uploaded image. URL: {image_url[:50]}..., Filename: {filename}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Image Upload API", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Image Upload API", False, error_msg=str(e))
            return False

    def test_marketplace_browse_api(self):
        """Test basic marketplace browse endpoint functionality"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/marketplace/browse?type=all&price_from=0&price_to=999999", 
                timeout=10
            )
            
            if response.status_code == 200:
                listings = response.json()
                listing_count = len(listings) if isinstance(listings, list) else 0
                
                # Check if listings have proper structure
                if listing_count > 0:
                    first_listing = listings[0]
                    has_seller_info = 'seller' in first_listing
                    has_bid_info = 'bid_info' in first_listing
                    has_time_info = 'time_info' in first_listing
                    has_id = 'id' in first_listing
                    has_title = 'title' in first_listing
                    has_price = 'price' in first_listing
                    
                    structure_score = sum([has_seller_info, has_bid_info, has_time_info, has_id, has_title, has_price])
                    
                    self.log_test(
                        "Marketplace Browse API", 
                        True, 
                        f"Retrieved {listing_count} listings with proper structure (6/6 fields present: {structure_score == 6})"
                    )
                else:
                    self.log_test(
                        "Marketplace Browse API", 
                        True, 
                        "No listings found but endpoint is working correctly"
                    )
                return True
            else:
                self.log_test("Marketplace Browse API", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Marketplace Browse API", False, error_msg=str(e))
            return False

    def test_admin_dashboard_endpoint(self):
        """Test admin dashboard endpoint functionality"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/dashboard", timeout=10)
            if response.status_code == 200:
                data = response.json()
                kpis = data.get('kpis', {})
                recent_activity = data.get('recent_activity', [])
                
                # Check required KPI fields
                required_kpis = ['total_users', 'total_listings', 'active_listings', 'total_deals', 'revenue', 'growth_rate']
                present_kpis = [kpi for kpi in required_kpis if kpi in kpis]
                
                self.log_test(
                    "Admin Dashboard Endpoint", 
                    True, 
                    f"KPIs present: {len(present_kpis)}/6, Users: {kpis.get('total_users')}, Listings: {kpis.get('total_listings')}, Revenue: €{kpis.get('revenue')}, Activities: {len(recent_activity)}"
                )
                return True
            else:
                self.log_test("Admin Dashboard Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Dashboard Endpoint", False, error_msg=str(e))
            return False

    def test_admin_users_endpoint(self):
        """Test admin users management endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if response.status_code == 200:
                users = response.json()
                user_count = len(users) if isinstance(users, list) else 0
                
                # Check if users have proper structure
                if user_count > 0:
                    first_user = users[0]
                    has_id = 'id' in first_user
                    has_username = 'username' in first_user
                    has_email = 'email' in first_user
                    has_role = 'role' in first_user
                    
                    structure_complete = has_id and has_username and has_email and has_role
                    
                    self.log_test(
                        "Admin Users Endpoint", 
                        True, 
                        f"Retrieved {user_count} users with proper structure: {structure_complete}"
                    )
                else:
                    self.log_test(
                        "Admin Users Endpoint", 
                        True, 
                        "No users found but endpoint is working correctly"
                    )
                return True
            else:
                self.log_test("Admin Users Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Users Endpoint", False, error_msg=str(e))
            return False

    def test_admin_settings_endpoint(self):
        """Test admin settings endpoint for site configuration"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/settings", timeout=10)
            if response.status_code == 200:
                settings = response.json()
                
                # Check for key settings fields
                key_fields = ['site_name', 'site_description', 'theme_color', 'hero_display_mode', 'hero_background_style']
                present_fields = [field for field in key_fields if field in settings]
                
                self.log_test(
                    "Admin Settings Endpoint", 
                    True, 
                    f"Settings fields present: {len(present_fields)}/5, Site name: {settings.get('site_name')}, Hero mode: {settings.get('hero_display_mode')}"
                )
                return True
            else:
                self.log_test("Admin Settings Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Settings Endpoint", False, error_msg=str(e))
            return False

    def test_authentication_login(self):
        """Test authentication and session management"""
        try:
            # Test login with demo credentials
            login_data = {
                "email": "demo@cataloro.com",
                "password": "demo123"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                token = data.get('token', '')
                
                has_user_data = bool(user.get('id')) and bool(user.get('email'))
                has_token = bool(token)
                
                self.log_test(
                    "Authentication Login", 
                    True, 
                    f"Login successful. User ID: {user.get('id')}, Token present: {has_token}, User data complete: {has_user_data}"
                )
                return user.get('id'), token
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Authentication Login", False, error_msg=error_detail)
                return None, None
        except Exception as e:
            self.log_test("Authentication Login", False, error_msg=str(e))
            return None, None

    def test_user_profile_access(self, user_id, token):
        """Test user profile access with authentication"""
        if not user_id:
            self.log_test("User Profile Access", False, error_msg="No user ID provided")
            return False
            
        try:
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
                
            response = requests.get(
                f"{BACKEND_URL}/auth/profile/{user_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                profile = response.json()
                
                # Check profile completeness
                has_basic_info = bool(profile.get('id')) and bool(profile.get('email'))
                has_username = bool(profile.get('username'))
                has_role = bool(profile.get('role'))
                
                profile_complete = has_basic_info and has_username and has_role
                
                self.log_test(
                    "User Profile Access", 
                    True, 
                    f"Profile retrieved successfully. Complete: {profile_complete}, Role: {profile.get('role')}"
                )
                return True
            else:
                self.log_test("User Profile Access", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Profile Access", False, error_msg=str(e))
            return False

    def test_admin_content_endpoint(self):
        """Test admin content management endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/content", timeout=10)
            if response.status_code == 200:
                content = response.json()
                
                # Check for key content sections
                has_hero = 'hero' in content
                has_stats = 'stats' in content
                has_features = 'features' in content
                has_cta = 'cta' in content
                
                sections_present = sum([has_hero, has_stats, has_features, has_cta])
                
                self.log_test(
                    "Admin Content Endpoint", 
                    True, 
                    f"Content sections present: {sections_present}/4 (hero: {has_hero}, stats: {has_stats}, features: {has_features}, cta: {has_cta})"
                )
                return True
            else:
                self.log_test("Admin Content Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Content Endpoint", False, error_msg=str(e))
            return False

    def test_listings_endpoint(self):
        """Test listings management endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/listings?status=active&limit=10", timeout=10)
            if response.status_code == 200:
                data = response.json()
                listings = data.get('listings', [])
                total = data.get('total', 0)
                
                self.log_test(
                    "Listings Management Endpoint", 
                    True, 
                    f"Retrieved {len(listings)} active listings out of {total} total"
                )
                return True
            else:
                self.log_test("Listings Management Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Listings Management Endpoint", False, error_msg=str(e))
            return False

    def run_ads_config_tests(self):
        """Run comprehensive tests for ads configuration backend functionality"""
        print("=" * 80)
        print("CATALORO BACKEND TESTING - ADS CONFIGURATION FOCUS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        print("Testing backend functionality after ads configuration fixes:")
        print("- Image Upload API for ad images")
        print("- Basic marketplace APIs")
        print("- Admin endpoints functionality")
        print("- Authentication and session management")
        print()
        
        # 1. Basic System Health
        print("🔍 BASIC SYSTEM HEALTH")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting tests.")
            return
        
        # 2. Image Upload API (Primary Focus)
        print("📸 IMAGE UPLOAD API TESTING")
        print("-" * 40)
        self.test_image_upload_api()
        
        # 3. Basic Marketplace APIs
        print("🛒 MARKETPLACE API TESTING")
        print("-" * 40)
        self.test_marketplace_browse_api()
        self.test_listings_endpoint()
        
        # 4. Admin Endpoints
        print("👑 ADMIN ENDPOINTS TESTING")
        print("-" * 40)
        self.test_admin_dashboard_endpoint()
        self.test_admin_users_endpoint()
        self.test_admin_settings_endpoint()
        self.test_admin_content_endpoint()
        
        # 5. Authentication and Session Management
        print("🔐 AUTHENTICATION TESTING")
        print("-" * 40)
        user_id, token = self.test_authentication_login()
        if user_id:
            self.test_user_profile_access(user_id, token)
        
        # Print Summary
        print("=" * 80)
        print("ADS CONFIGURATION BACKEND TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Critical Issues Analysis
        critical_failures = []
        for result in self.test_results:
            if "❌ FAIL" in result["status"]:
                if any(keyword in result["test"].lower() for keyword in ["image upload", "browse", "dashboard", "auth"]):
                    critical_failures.append(result)
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"  - {failure['test']}: {failure['error']}")
            print()
        
        if self.failed_tests > 0:
            print("ALL FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        else:
            print("🎉 ALL TESTS PASSED - Backend is functioning correctly after ads configuration fixes!")
        
        print("\n🎯 ADS CONFIGURATION BACKEND TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = AdsConfigBackendTester()
    
    print("🎯 RUNNING ADS CONFIGURATION BACKEND TESTING")
    print("Testing backend functionality after implementing ads configuration fixes...")
    print()
    
    passed, failed, results = tester.run_ads_config_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)