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
    def __init__(self, base_url="http://localhost:8001"):
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