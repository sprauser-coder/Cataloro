#!/usr/bin/env python3
"""
SEO Settings Endpoints Testing
Testing the new SEO settings endpoints that were just added.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class SEOEndpointsTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Token: {self.admin_token[:20]}...")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_get_seo_settings_default(self):
        """Test GET /api/admin/seo - should return defaults if none exist"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/seo")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if default values are returned
                expected_defaults = {
                    "site_title": "Cataloro - Your Trusted Marketplace",
                    "meta_description": "Buy and sell with confidence on Cataloro marketplace",
                    "meta_keywords": "marketplace, buy, sell, ecommerce, cataloro",
                    "og_title": "Cataloro Marketplace",
                    "og_description": "Your trusted marketplace for amazing deals"
                }
                
                all_defaults_correct = True
                for key, expected_value in expected_defaults.items():
                    if data.get(key) != expected_value:
                        all_defaults_correct = False
                        break
                
                if all_defaults_correct:
                    self.log_test("GET SEO Settings (Default)", True, f"Returned default values correctly")
                else:
                    self.log_test("GET SEO Settings (Default)", False, f"Default values incorrect. Got: {json.dumps(data, indent=2)}")
                
                return data
            else:
                self.log_test("GET SEO Settings (Default)", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("GET SEO Settings (Default)", False, f"Exception: {str(e)}")
            return None
    
    def test_post_seo_settings(self):
        """Test POST /api/admin/seo - save SEO settings with sample data"""
        try:
            # Sample SEO data as specified in the review request
            sample_seo_data = {
                "site_title": "Cataloro Test - SEO Update",
                "meta_description": "Test meta description for SEO",
                "meta_keywords": "test, seo, marketplace",
                "og_title": "Test OG Title",
                "og_description": "Test OG Description"
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/seo", json=sample_seo_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("message") == "SEO settings saved successfully":
                    self.log_test("POST SEO Settings (Save)", True, f"Successfully saved SEO settings")
                    return True
                else:
                    self.log_test("POST SEO Settings (Save)", False, f"Unexpected response: {json.dumps(data, indent=2)}")
                    return False
            else:
                self.log_test("POST SEO Settings (Save)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST SEO Settings (Save)", False, f"Exception: {str(e)}")
            return False
    
    def test_get_seo_settings_saved(self):
        """Test GET /api/admin/seo - verify saved SEO settings persistence"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/seo")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if saved values are returned correctly
                expected_saved_values = {
                    "site_title": "Cataloro Test - SEO Update",
                    "meta_description": "Test meta description for SEO",
                    "meta_keywords": "test, seo, marketplace",
                    "og_title": "Test OG Title",
                    "og_description": "Test OG Description"
                }
                
                all_saved_correct = True
                incorrect_fields = []
                
                for key, expected_value in expected_saved_values.items():
                    if data.get(key) != expected_value:
                        all_saved_correct = False
                        incorrect_fields.append(f"{key}: expected '{expected_value}', got '{data.get(key)}'")
                
                if all_saved_correct:
                    self.log_test("GET SEO Settings (Saved)", True, f"All saved values retrieved correctly")
                    return True
                else:
                    self.log_test("GET SEO Settings (Saved)", False, f"Saved values incorrect: {', '.join(incorrect_fields)}")
                    return False
            else:
                self.log_test("GET SEO Settings (Saved)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET SEO Settings (Saved)", False, f"Exception: {str(e)}")
            return False
    
    def test_seo_settings_data_integrity(self):
        """Test that all SEO settings fields are properly handled"""
        try:
            # Test with comprehensive SEO data
            comprehensive_seo_data = {
                "site_title": "Comprehensive Test Title",
                "meta_description": "Comprehensive test meta description",
                "meta_keywords": "comprehensive, test, keywords",
                "favicon_url": "/test-favicon.ico",
                "og_title": "Comprehensive OG Title",
                "og_description": "Comprehensive OG Description",
                "og_image": "https://example.com/og-image.jpg",
                "twitter_card": "summary",
                "robots_txt": "User-agent: *\nDisallow: /admin",
                "canonical_url": "https://cataloro.com",
                "structured_data": '{"@context": "https://schema.org", "@type": "Organization", "name": "Test Cataloro"}'
            }
            
            # Save comprehensive data
            response = self.session.post(f"{BACKEND_URL}/admin/seo", json=comprehensive_seo_data)
            
            if response.status_code != 200:
                self.log_test("SEO Data Integrity (Save)", False, f"Failed to save comprehensive data: {response.status_code}")
                return False
            
            # Retrieve and verify
            response = self.session.get(f"{BACKEND_URL}/admin/seo")
            
            if response.status_code == 200:
                data = response.json()
                
                all_fields_correct = True
                incorrect_fields = []
                
                for key, expected_value in comprehensive_seo_data.items():
                    if data.get(key) != expected_value:
                        all_fields_correct = False
                        incorrect_fields.append(f"{key}: expected '{expected_value}', got '{data.get(key)}'")
                
                if all_fields_correct:
                    self.log_test("SEO Data Integrity", True, f"All comprehensive SEO fields handled correctly")
                    return True
                else:
                    self.log_test("SEO Data Integrity", False, f"Field integrity issues: {', '.join(incorrect_fields)}")
                    return False
            else:
                self.log_test("SEO Data Integrity (Retrieve)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("SEO Data Integrity", False, f"Exception: {str(e)}")
            return False
    
    def test_seo_authentication_required(self):
        """Test that SEO endpoints require admin authentication"""
        try:
            # Remove authorization header temporarily
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Test GET without auth
            response = self.session.get(f"{BACKEND_URL}/admin/seo")
            get_auth_required = response.status_code == 403
            
            # Test POST without auth
            response = self.session.post(f"{BACKEND_URL}/admin/seo", json={"site_title": "Test"})
            post_auth_required = response.status_code == 403
            
            # Restore headers
            self.session.headers.update(original_headers)
            
            if get_auth_required and post_auth_required:
                self.log_test("SEO Authentication Required", True, "Both GET and POST properly require admin authentication")
                return True
            else:
                self.log_test("SEO Authentication Required", False, f"GET auth required: {get_auth_required}, POST auth required: {post_auth_required}")
                return False
                
        except Exception as e:
            self.log_test("SEO Authentication Required", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all SEO endpoint tests"""
        print("=" * 60)
        print("SEO SETTINGS ENDPOINTS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print()
        
        # Step 2: Test authentication requirement
        self.test_seo_authentication_required()
        print()
        
        # Step 3: Test GET default settings
        print("Testing GET /api/admin/seo (default values)...")
        default_settings = self.test_get_seo_settings_default()
        print()
        
        # Step 4: Test POST save settings
        print("Testing POST /api/admin/seo (save sample data)...")
        save_success = self.test_post_seo_settings()
        print()
        
        # Step 5: Test GET saved settings
        print("Testing GET /api/admin/seo (verify persistence)...")
        persistence_success = self.test_get_seo_settings_saved()
        print()
        
        # Step 6: Test comprehensive data integrity
        print("Testing SEO data integrity...")
        integrity_success = self.test_seo_settings_data_integrity()
        print()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"] and not result["success"]:
                print(f"   {result['details']}")
        
        print()
        
        # Overall assessment
        if success_rate >= 100:
            print("🎉 ALL TESTS PASSED - SEO endpoints are working perfectly!")
            return True
        elif success_rate >= 80:
            print("⚠️  MOSTLY WORKING - SEO endpoints have minor issues")
            return True
        else:
            print("❌ CRITICAL ISSUES - SEO endpoints have major problems")
            return False

def main():
    """Main test execution"""
    tester = SEOEndpointsTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()