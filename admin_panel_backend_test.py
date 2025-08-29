#!/usr/bin/env python3
from config_loader import get_config, get_backend_url, get_admin_credentials, get_paths, get_database_url
"""
Comprehensive Admin Panel Backend Testing Suite
Testing backend functionality for AdminPanelNew.js implementation including:
- Admin Authentication & Stats
- User Management APIs (block/unblock/delete/bulk operations)
- Product/Listing Management APIs (status updates/delete)
- Analytics & CMS APIs (settings/logo upload)
"""

import requests
import json
import os
from datetime import datetime
import uuid

# Configuration - Use correct backend URL
BACKEND_URL = "get_backend_url()"  # Correct URL from backend .env
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "get_admin_credentials()[0]"
ADMIN_PASSWORD = "get_admin_credentials()[1]"

class AdminPanelBackendTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.test_user_ids = []
        self.test_listing_ids = []
        
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

    def test_admin_authentication_and_stats(self):
        """Test Admin Authentication & Stats APIs"""
        print("=== Testing Admin Authentication & Stats ===")
        
        # Test admin login
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                user_data = data["user"]
                self.log_result("Admin Authentication", True, 
                              f"Token: {self.admin_token[:20]}..., Role: {user_data['role']}, Name: {user_data['full_name']}")
            else:
                self.log_result("Admin Authentication", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, error=str(e))
            return False

        # Test admin stats endpoint
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{API_BASE}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_users", "active_users", "blocked_users", "total_listings", "active_listings", "total_orders", "total_revenue"]
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    self.log_result("Admin Dashboard Stats", True, 
                                  f"Users: {stats['total_users']} (Active: {stats['active_users']}, Blocked: {stats['blocked_users']}), "
                                  f"Listings: {stats['total_listings']} (Active: {stats['active_listings']}), "
                                  f"Orders: {stats['total_orders']}, Revenue: €{stats['total_revenue']}")
                else:
                    self.log_result("Admin Dashboard Stats", False, 
                                  error=f"Missing required fields: {missing_fields}")
            else:
                self.log_result("Admin Dashboard Stats", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Admin Dashboard Stats", False, error=str(e))
            
        return True

    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}

    def test_user_management_apis(self):
        """Test User Management APIs"""
        print("=== Testing User Management APIs ===")
        
        # Test get all users
        try:
            response = requests.get(f"{API_BASE}/admin/users", headers=self.get_headers())
            
            if response.status_code == 200:
                users = response.json()
                if users:
                    # Store some test user IDs (excluding admin)
                    self.test_user_ids = [user["id"] for user in users if user["role"] != "admin"][:3]
                    
                    self.log_result("Get All Users", True, 
                                  f"Retrieved {len(users)} users. Sample user: {users[0]['email']} ({users[0]['role']})")
                else:
                    self.log_result("Get All Users", True, "No users found (empty database)")
            else:
                self.log_result("Get All Users", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Get All Users", False, error=str(e))

        # Test individual user operations if we have test users
        if self.test_user_ids:
            test_user_id = self.test_user_ids[0]
            
            # Test block user
            try:
                response = requests.put(f"{API_BASE}/admin/users/{test_user_id}/block", 
                                      headers=self.get_headers())
                
                if response.status_code == 200:
                    self.log_result("Block User", True, f"Successfully blocked user {test_user_id}")
                else:
                    self.log_result("Block User", False, 
                                  error=f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("Block User", False, error=str(e))

            # Test unblock user
            try:
                response = requests.put(f"{API_BASE}/admin/users/{test_user_id}/unblock", 
                                      headers=self.get_headers())
                
                if response.status_code == 200:
                    self.log_result("Unblock User", True, f"Successfully unblocked user {test_user_id}")
                else:
                    self.log_result("Unblock User", False, 
                                  error=f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("Unblock User", False, error=str(e))

        # Test bulk operations if we have multiple test users
        if len(self.test_user_ids) >= 2:
            bulk_user_ids = self.test_user_ids[:2]
            
            # Test bulk block
            try:
                response = requests.put(f"{API_BASE}/admin/users/bulk-block", 
                                      json=bulk_user_ids,
                                      headers=self.get_headers())
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_result("Bulk Block Users", True, 
                                  f"Bulk block operation: {result.get('message', 'Success')}")
                else:
                    self.log_result("Bulk Block Users", False, 
                                  error=f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("Bulk Block Users", False, error=str(e))

            # Test bulk unblock
            try:
                response = requests.put(f"{API_BASE}/admin/users/bulk-unblock", 
                                      json=bulk_user_ids,
                                      headers=self.get_headers())
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_result("Bulk Unblock Users", True, 
                                  f"Bulk unblock operation: {result.get('message', 'Success')}")
                else:
                    self.log_result("Bulk Unblock Users", False, 
                                  error=f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("Bulk Unblock Users", False, error=str(e))

            # Test bulk delete (careful - this is destructive)
            try:
                # Only test with one user to minimize impact
                single_user_for_delete = [bulk_user_ids[0]] if bulk_user_ids else []
                if single_user_for_delete:
                    response = requests.delete(f"{API_BASE}/admin/users/bulk-delete", 
                                             json=single_user_for_delete,
                                             headers=self.get_headers())
                    
                    if response.status_code == 200:
                        result = response.json()
                        self.log_result("Bulk Delete Users", True, 
                                      f"Bulk delete operation: {result.get('message', 'Success')}")
                    else:
                        self.log_result("Bulk Delete Users", False, 
                                      error=f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("Bulk Delete Users", False, error=str(e))

    def test_listing_management_apis(self):
        """Test Product/Listing Management APIs"""
        print("=== Testing Listing Management APIs ===")
        
        # Test get all listings (admin view)
        try:
            response = requests.get(f"{API_BASE}/admin/listings", headers=self.get_headers())
            
            if response.status_code == 200:
                listings = response.json()
                if listings:
                    # Store some test listing IDs
                    self.test_listing_ids = [listing["id"] for listing in listings][:3]
                    
                    self.log_result("Get All Listings (Admin)", True, 
                                  f"Retrieved {len(listings)} listings. Sample: {listings[0]['title']} - {listings[0]['status']}")
                else:
                    self.log_result("Get All Listings (Admin)", True, "No listings found (empty database)")
            else:
                self.log_result("Get All Listings (Admin)", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Get All Listings (Admin)", False, error=str(e))

        # Test listing status update if we have test listings
        if self.test_listing_ids:
            test_listing_id = self.test_listing_ids[0]
            
            # Test update listing status
            try:
                # Status should be passed as query parameter
                response = requests.put(f"{API_BASE}/admin/listings/{test_listing_id}/status?status=active", 
                                      headers=self.get_headers())
                
                if response.status_code == 200:
                    self.log_result("Update Listing Status", True, 
                                  f"Successfully updated listing {test_listing_id} status to active")
                else:
                    self.log_result("Update Listing Status", False, 
                                  error=f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("Update Listing Status", False, error=str(e))

            # Test delete listing
            try:
                response = requests.delete(f"{API_BASE}/admin/listings/{test_listing_id}", 
                                         headers=self.get_headers())
                
                if response.status_code == 200:
                    self.log_result("Delete Listing", True, 
                                  f"Successfully deleted listing {test_listing_id}")
                else:
                    self.log_result("Delete Listing", False, 
                                  error=f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("Delete Listing", False, error=str(e))

    def test_cms_and_analytics_apis(self):
        """Test Analytics & CMS APIs"""
        print("=== Testing CMS & Analytics APIs ===")
        
        # Test get CMS settings
        try:
            response = requests.get(f"{API_BASE}/admin/cms/settings", headers=self.get_headers())
            
            if response.status_code == 200:
                settings = response.json()
                required_fields = ["site_name", "site_tagline", "hero_title", "hero_subtitle"]
                missing_fields = [field for field in required_fields if field not in settings]
                
                if not missing_fields:
                    self.log_result("Get CMS Settings", True, 
                                  f"Site: {settings['site_name']}, Tagline: {settings['site_tagline']}")
                else:
                    self.log_result("Get CMS Settings", False, 
                                  error=f"Missing required fields: {missing_fields}")
            else:
                self.log_result("Get CMS Settings", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Get CMS Settings", False, error=str(e))

        # Test update CMS settings
        try:
            update_data = {
                "site_name": "Cataloro Test",
                "site_tagline": "Testing Admin Panel Backend",
                "hero_title": "Test Hero Title",
                "hero_subtitle": "Test Hero Subtitle for Admin Panel Testing"
            }
            response = requests.put(f"{API_BASE}/admin/cms/settings", 
                                  json=update_data,
                                  headers=self.get_headers())
            
            if response.status_code == 200:
                self.log_result("Update CMS Settings", True, 
                              f"Successfully updated CMS settings")
            else:
                self.log_result("Update CMS Settings", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Update CMS Settings", False, error=str(e))

        # Test logo upload functionality
        try:
            # Create a minimal valid PNG file
            test_png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01IEND\xaeB`\x82'
            
            files = {'file': ('test_logo.png', test_png_data, 'image/png')}
            response = requests.post(f"{API_BASE}/admin/cms/upload-logo", 
                                   files=files, 
                                   headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                if "logo_url" in result:
                    self.log_result("Logo Upload", True, 
                                  f"Logo uploaded successfully: {result['logo_url']}")
                else:
                    self.log_result("Logo Upload", False, 
                                  error="Missing logo_url in response")
            else:
                self.log_result("Logo Upload", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Logo Upload", False, error=str(e))

        # Test public CMS settings endpoint (should work without auth)
        try:
            response = requests.get(f"{API_BASE}/cms/settings")  # No auth headers
            
            if response.status_code == 200:
                settings = response.json()
                self.log_result("Public CMS Settings", True, 
                              f"Public settings accessible: {settings.get('site_name', 'N/A')}")
            else:
                self.log_result("Public CMS Settings", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Public CMS Settings", False, error=str(e))

    def test_additional_admin_endpoints(self):
        """Test Additional Admin Panel Endpoints"""
        print("=== Testing Additional Admin Endpoints ===")
        
        # Test admin orders endpoint
        try:
            response = requests.get(f"{API_BASE}/admin/orders", headers=self.get_headers())
            
            if response.status_code == 200:
                orders = response.json()
                self.log_result("Admin Orders", True, 
                              f"Retrieved {len(orders)} orders for admin management")
            else:
                self.log_result("Admin Orders", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Admin Orders", False, error=str(e))

        # Test categories endpoint (should be accessible)
        try:
            response = requests.get(f"{API_BASE}/categories")
            
            if response.status_code == 200:
                categories = response.json()
                self.log_result("Categories Endpoint", True, 
                              f"Retrieved {len(categories)} categories")
            else:
                self.log_result("Categories Endpoint", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Categories Endpoint", False, error=str(e))

        # Test basic API endpoint
        try:
            response = requests.get(f"{API_BASE}/")
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Basic API Endpoint", True, 
                              f"API Response: {result.get('message', 'N/A')} v{result.get('version', 'N/A')}")
            else:
                self.log_result("Basic API Endpoint", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Basic API Endpoint", False, error=str(e))

    def run_all_tests(self):
        """Run all admin panel backend tests"""
        print("🚀 Starting Comprehensive Admin Panel Backend Testing")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print("=" * 70)
        
        # Authenticate first
        if not self.test_admin_authentication_and_stats():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Run all test suites
        self.test_user_management_apis()
        self.test_listing_management_apis()
        self.test_cms_and_analytics_apis()
        self.test_additional_admin_endpoints()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 70)
        print("📊 ADMIN PANEL BACKEND TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
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
        
        print("\n" + "=" * 70)
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Admin panel backend is working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: Admin panel backend is mostly working well.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Admin panel backend has some issues.")
        else:
            print("❌ CRITICAL: Admin panel backend needs significant work.")

if __name__ == "__main__":
    tester = AdminPanelBackendTester()
    tester.run_all_tests()