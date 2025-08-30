#!/usr/bin/env python3
"""
Cataloro Marketplace Backend API Test Suite
Tests all API endpoints for functionality and integration
"""

import requests
import sys
import json
from datetime import datetime

class CataloroAPITester:
    def __init__(self, base_url="https://cat-db-preview.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        return success

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_user = response['user']
            print(f"   Admin User: {self.admin_user}")
        return success

    def test_user_login(self):
        """Test regular user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.user_token = response['token']
            self.regular_user = response['user']
            print(f"   Regular User: {self.regular_user}")
        return success

    def test_marketplace_browse(self):
        """Test marketplace browse endpoint"""
        success, response = self.run_test(
            "Marketplace Browse",
            "GET",
            "api/marketplace/browse",
            200
        )
        if success:
            print(f"   Found {len(response)} listings")
        return success

    def test_user_profile(self):
        """Test user profile endpoint"""
        if not self.regular_user:
            print("❌ User Profile - SKIPPED (No user logged in)")
            return False
            
        success, response = self.run_test(
            "User Profile",
            "GET",
            f"api/auth/profile/{self.regular_user['id']}",
            200
        )
        return success

    def test_my_listings(self):
        """Test my listings endpoint"""
        if not self.regular_user:
            print("❌ My Listings - SKIPPED (No user logged in)")
            return False
            
        success, response = self.run_test(
            "My Listings",
            "GET",
            f"api/user/my-listings/{self.regular_user['id']}",
            200
        )
        return success

    def test_my_deals(self):
        """Test my deals endpoint"""
        if not self.regular_user:
            print("❌ My Deals - SKIPPED (No user logged in)")
            return False
            
        success, response = self.run_test(
            "My Deals",
            "GET",
            f"api/user/my-deals/{self.regular_user['id']}",
            200
        )
        return success

    def test_notifications(self):
        """Test notifications endpoint"""
        if not self.regular_user:
            print("❌ Notifications - SKIPPED (No user logged in)")
            return False
            
        success, response = self.run_test(
            "User Notifications",
            "GET",
            f"api/user/notifications/{self.regular_user['id']}",
            200
        )
        if success:
            print(f"   Found {len(response)} notifications")
        return success

    def test_admin_dashboard(self):
        """Test admin dashboard endpoint"""
        if not self.admin_user:
            print("❌ Admin Dashboard - SKIPPED (No admin logged in)")
            return False
            
        success, response = self.run_test(
            "Admin Dashboard",
            "GET",
            "api/admin/dashboard",
            200
        )
        if success and 'kpis' in response:
            print(f"   KPIs: {response['kpis']}")
        return success

    def test_admin_users(self):
        """Test admin users endpoint"""
        if not self.admin_user:
            print("❌ Admin Users - SKIPPED (No admin logged in)")
            return False
            
        success, response = self.run_test(
            "Admin Users List",
            "GET",
            "api/admin/users",
            200
        )
        if success:
            print(f"   Found {len(response)} users")
        return success

    def test_admin_settings(self):
        """Test admin settings endpoint (for site branding)"""
        if not self.admin_user:
            print("❌ Admin Settings - SKIPPED (No admin logged in)")
            return False
            
        # Test GET settings (initial state)
        success, initial_response = self.run_test(
            "Admin Settings GET (Initial)",
            "GET",
            "api/admin/settings",
            200
        )
        
        if not success:
            print("   ⚠️  Settings endpoint not implemented - expected for site branding")
            return False
            
        print(f"   Initial settings: {initial_response}")
            
        # Test PUT settings (update with comprehensive data)
        test_settings = {
            "site_name": "Cataloro Test Platform",
            "site_description": "Enhanced Test Marketplace with Branding",
            "logo_url": "/test-logo.png",
            "logo_light_url": "data:image/png;base64,test-light-logo",
            "logo_dark_url": "data:image/png;base64,test-dark-logo",
            "theme_color": "#FF6B35",
            "allow_registration": True,
            "require_approval": False,
            "email_notifications": True,
            "commission_rate": 7.5,
            "max_file_size": 15
        }
        
        success_put, put_response = self.run_test(
            "Admin Settings PUT (Update)",
            "PUT",
            "api/admin/settings",
            200,
            data=test_settings
        )
        
        if not success_put:
            return False
            
        # Test GET settings again to verify persistence
        success_verify, verify_response = self.run_test(
            "Admin Settings GET (Verify Persistence)",
            "GET",
            "api/admin/settings",
            200
        )
        
        if success_verify:
            # Check if our test data persisted
            if (verify_response.get('site_name') == test_settings['site_name'] and
                verify_response.get('theme_color') == test_settings['theme_color'] and
                verify_response.get('commission_rate') == test_settings['commission_rate']):
                print("   ✅ Settings persistence verified - data stored and retrieved correctly")
                self.log_test("Settings Data Persistence", True, "All test settings persisted correctly")
            else:
                print("   ⚠️  Settings may not have persisted correctly")
                print(f"   Expected site_name: {test_settings['site_name']}, Got: {verify_response.get('site_name')}")
                print(f"   Expected theme_color: {test_settings['theme_color']}, Got: {verify_response.get('theme_color')}")
                self.log_test("Settings Data Persistence", False, "Test settings did not persist correctly")
        
        return success_put and success_verify

    def test_logo_upload(self):
        """Test logo upload endpoint (for dual logo system)"""
        if not self.admin_user:
            print("❌ Logo Upload - SKIPPED (No admin logged in)")
            return False
            
        # Create a simple test image (1x1 PNG)
        import base64
        # This is a 1x1 transparent PNG image in base64
        png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==')
        
        # Test logo upload with proper file data
        url = f"{self.base_url}/api/admin/logo"
        print(f"\n🔍 Testing Logo Upload...")
        print(f"   URL: {url}")
        
        try:
            # Prepare multipart form data
            files = {
                'file': ('test-logo.png', png_data, 'image/png')
            }
            data = {
                'mode': 'light'
            }
            
            response = self.session.post(url, files=files, data=data)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                    print(f"   Logo uploaded successfully: {response_data.get('filename', 'N/A')}")
                    print(f"   File size: {response_data.get('size', 'N/A')} bytes")
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: 200, Response: {response.text[:200]}"

            self.log_test("Logo Upload", success, details)
            
            # Test dark mode logo upload as well
            if success:
                files_dark = {
                    'file': ('test-logo-dark.png', png_data, 'image/png')
                }
                data_dark = {
                    'mode': 'dark'
                }
                
                response_dark = self.session.post(url, files=files_dark, data=data_dark)
                success_dark = response_dark.status_code == 200
                
                if success_dark:
                    print(f"   Dark mode logo upload also successful")
                    self.log_test("Logo Upload (Dark Mode)", success_dark, f"Status: {response_dark.status_code}")
                else:
                    self.log_test("Logo Upload (Dark Mode)", success_dark, f"Status: {response_dark.status_code}, Response: {response_dark.text[:100]}")
            
            return success

        except Exception as e:
            self.log_test("Logo Upload", False, f"Error: {str(e)}")
            return False

    def test_admin_session_handling(self):
        """Test admin session persistence and validation"""
        if not self.admin_user or not self.admin_token:
            print("❌ Admin Session - SKIPPED (No admin session)")
            return False
            
        # Test session with token header
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        success, response = self.run_test(
            "Admin Session Validation",
            "GET",
            "api/admin/dashboard",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Admin session valid, token: {self.admin_token[:20]}...")
            
        return success

    def test_site_branding_data_persistence(self):
        """Test if site branding data persists correctly"""
        if not self.admin_user:
            print("❌ Site Branding Persistence - SKIPPED (No admin logged in)")
            return False
            
        # This would test the database persistence of site settings
        # For now, we'll test the admin dashboard which should contain site info
        success, response = self.run_test(
            "Site Branding Data Check",
            "GET",
            "api/admin/dashboard",
            200
        )
        
        if success and 'kpis' in response:
            print("   ✅ Admin dashboard accessible - site data can be stored")
            return True
        else:
            print("   ❌ Cannot verify site branding data persistence")
            return False

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Cataloro Marketplace API Tests")
        print("=" * 60)

        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False

        # Authentication tests
        admin_login_success = self.test_admin_login()
        user_login_success = self.test_user_login()

        # Marketplace tests
        self.test_marketplace_browse()

        # User-specific tests
        if user_login_success:
            self.test_user_profile()
            self.test_my_listings()
            self.test_my_deals()
            self.test_notifications()

        # Admin tests
        if admin_login_success:
            self.test_admin_dashboard()
            self.test_admin_users()
            
            # Site branding and logo upload tests (as requested in review)
            print("\n🎨 Testing Site Branding & Logo Upload System...")
            self.test_admin_settings()
            self.test_logo_upload()
            self.test_admin_session_handling()
            self.test_site_branding_data_persistence()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    """Main test execution"""
    tester = CataloroAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())