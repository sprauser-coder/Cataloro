#!/usr/bin/env python3
"""
Critical Bugs Testing - Page Management Creation Bug Fix Verification
Testing the two specific bugs that were just fixed:
1. Page Management Creation Bug - corrected field names
2. Verify existing functionality still works
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class CriticalBugsTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }

    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed_tests"] += 1
            status = "✅ PASS"
        else:
            self.results["failed_tests"] += 1
            status = "❌ FAIL"
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.results["test_details"].append({
            "test": test_name,
            "passed": passed,
            "details": details
        })

    def admin_login(self):
        """Login as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Login", True, f"Successfully logged in as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False

    def test_page_creation_bug_fix(self):
        """Test POST /api/admin/cms/pages with corrected field names"""
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test page data with CORRECTED field names (the bug fix)
            test_page_data = {
                "title": "Test Page",
                "page_slug": "test-page",  # CORRECTED: was 'slug' before
                "content": "<p>This is test content</p>",
                "is_published": True,  # CORRECTED: was 'published' before
                "meta_description": "Test page description"
                # NOTE: 'show_in_navigation' field removed (didn't exist in backend model)
            }
            
            print(f"   Testing with corrected field names: {list(test_page_data.keys())}")
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/pages", json=test_page_data, headers=admin_headers)
            
            if response.status_code == 200:
                response_data = response.json()
                created_page = response_data.get("page", {})
                
                # Verify the page was created with correct data
                checks = [
                    (created_page.get("title") == test_page_data["title"], "Title matches"),
                    (created_page.get("page_slug") == test_page_data["page_slug"], "Page slug matches"),
                    (created_page.get("content") == test_page_data["content"], "Content matches"),
                    (created_page.get("is_published") == test_page_data["is_published"], "Published status matches"),
                    (created_page.get("meta_description") == test_page_data["meta_description"], "Meta description matches")
                ]
                
                all_checks_passed = all(check[0] for check in checks)
                failed_checks = [check[1] for check in checks if not check[0]]
                
                if all_checks_passed:
                    self.log_test("Page Creation Bug Fix - Field Names", True, "All corrected field names work properly")
                    
                    # Store page slug for retrieval test
                    self.test_page_slug = test_page_data["page_slug"]
                    return True
                else:
                    self.log_test("Page Creation Bug Fix - Field Names", False, f"Failed checks: {failed_checks}")
                    return False
            else:
                self.log_test("Page Creation Bug Fix - Field Names", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Page Creation Bug Fix", False, f"Exception: {str(e)}")
            return False

    def test_page_retrieval_after_creation(self):
        """Test that created page can be retrieved via GET /api/admin/cms/pages"""
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all pages
            response = self.session.get(f"{BACKEND_URL}/admin/cms/pages", headers=admin_headers)
            
            if response.status_code == 200:
                pages = response.json()
                
                # Find our test page
                test_page = None
                for page in pages:
                    if page.get("page_slug") == getattr(self, 'test_page_slug', 'test-page'):
                        test_page = page
                        break
                
                if test_page:
                    # Verify all fields are present and correct
                    required_fields = ["id", "title", "page_slug", "content", "is_published", "meta_description", "created_at"]
                    missing_fields = [field for field in required_fields if field not in test_page]
                    
                    if not missing_fields:
                        self.log_test("Page Retrieval After Creation", True, f"Page found with all required fields: {test_page['title']}")
                        return True
                    else:
                        self.log_test("Page Retrieval After Creation", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Page Retrieval After Creation", False, "Test page not found in pages list")
                    return False
            else:
                self.log_test("Page Retrieval After Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Page Retrieval After Creation", False, f"Exception: {str(e)}")
            return False

    def test_existing_functionality_admin_stats(self):
        """Test GET /api/admin/stats to ensure fixes didn't break existing functionality"""
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = self.session.get(f"{BACKEND_URL}/admin/stats", headers=admin_headers)
            
            if response.status_code == 200:
                stats_data = response.json()
                
                # Verify expected stats fields are present
                required_fields = ["total_users", "active_users", "blocked_users", "total_listings", "active_listings", "total_orders", "total_revenue"]
                missing_fields = [field for field in required_fields if field not in stats_data]
                
                if not missing_fields:
                    # Verify data types
                    numeric_fields = ["total_users", "active_users", "blocked_users", "total_listings", "active_listings", "total_orders", "total_revenue"]
                    type_errors = []
                    
                    for field in numeric_fields:
                        value = stats_data.get(field)
                        if not isinstance(value, (int, float)):
                            type_errors.append(f"{field} is not numeric")
                    
                    if not type_errors:
                        stats_summary = f"Users: {stats_data['total_users']}, Listings: {stats_data['total_listings']}, Orders: {stats_data['total_orders']}, Revenue: ${stats_data['total_revenue']}"
                        self.log_test("Existing Functionality - Admin Stats", True, f"All stats working correctly - {stats_summary}")
                        return True
                    else:
                        self.log_test("Existing Functionality - Admin Stats", False, f"Type errors: {type_errors}")
                        return False
                else:
                    self.log_test("Existing Functionality - Admin Stats", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("Existing Functionality - Admin Stats", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Existing Functionality - Admin Stats", False, f"Exception: {str(e)}")
            return False

    def test_existing_functionality_cms_settings(self):
        """Test GET /api/admin/cms/settings to ensure CMS functionality still works"""
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings", headers=admin_headers)
            
            if response.status_code == 200:
                settings_data = response.json()
                
                # Verify key CMS settings fields are present
                key_fields = ["site_name", "site_tagline", "hero_title", "hero_subtitle", "primary_color", "secondary_color"]
                missing_fields = [field for field in key_fields if field not in settings_data]
                
                if not missing_fields:
                    site_name = settings_data.get("site_name", "Unknown")
                    self.log_test("Existing Functionality - CMS Settings", True, f"CMS settings working correctly - Site: {site_name}")
                    return True
                else:
                    self.log_test("Existing Functionality - CMS Settings", False, f"Missing key fields: {missing_fields}")
                    return False
            else:
                self.log_test("Existing Functionality - CMS Settings", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Existing Functionality - CMS Settings", False, f"Exception: {str(e)}")
            return False

    def test_page_creation_with_old_field_names(self):
        """Test that old incorrect field names are properly rejected (negative test)"""
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test page data with OLD INCORRECT field names (should fail or be ignored)
            old_incorrect_data = {
                "title": "Old Field Names Test",
                "slug": "old-field-test",  # INCORRECT: should be 'page_slug'
                "content": "<p>Testing old field names</p>",
                "published": True,  # INCORRECT: should be 'is_published'
                "show_in_navigation": True,  # INCORRECT: doesn't exist in backend model
                "meta_description": "Old field names test"
            }
            
            print(f"   Testing with old incorrect field names: {list(old_incorrect_data.keys())}")
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/pages", json=old_incorrect_data, headers=admin_headers)
            
            # This should either fail with 422 validation error or succeed but ignore incorrect fields
            if response.status_code == 422:
                self.log_test("Page Creation - Old Field Names Rejection", True, "Correctly rejected old incorrect field names with 422 validation error")
                return True
            elif response.status_code == 400:
                self.log_test("Page Creation - Old Field Names Rejection", True, "Correctly rejected old incorrect field names with 400 error")
                return True
            else:
                # If it somehow succeeds, that's actually a problem since the old field names should not work
                self.log_test("Page Creation - Old Field Names Rejection", False, f"Unexpected success with old field names - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Page Creation - Old Field Names Rejection", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all critical bug fix tests"""
        print("=" * 80)
        print("CRITICAL BUGS TESTING - PAGE MANAGEMENT CREATION BUG FIX VERIFICATION")
        print("Testing the two specific bugs that were just fixed")
        print("=" * 80)
        
        # Step 1: Admin login
        if not self.admin_login():
            print("❌ Cannot proceed without admin access")
            return False
        
        print("\n🔍 TESTING BUG FIX #1: PAGE MANAGEMENT CREATION WITH CORRECTED FIELD NAMES")
        print("-" * 70)
        
        # Test the main bug fix - corrected field names
        self.test_page_creation_bug_fix()
        self.test_page_retrieval_after_creation()
        
        # Test that old field names are properly rejected
        self.test_page_creation_with_old_field_names()
        
        print("\n🔍 TESTING BUG FIX #2: VERIFY EXISTING FUNCTIONALITY STILL WORKS")
        print("-" * 70)
        
        # Test existing functionality to ensure fixes didn't break anything
        self.test_existing_functionality_admin_stats()
        self.test_existing_functionality_cms_settings()
        
        # Print summary
        print("\n" + "=" * 80)
        print("CRITICAL BUGS TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.results["passed_tests"] / self.results["total_tests"]) * 100 if self.results["total_tests"] > 0 else 0
        
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']} ✅")
        print(f"Failed: {self.results['failed_tests']} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results["failed_tests"] > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.results["test_details"]:
                if not test["passed"]:
                    print(f"  • {test['test']}: {test['details']}")
        else:
            print("\n🎉 ALL CRITICAL BUG FIXES VERIFIED SUCCESSFULLY!")
            print("✅ Page creation with corrected field names works")
            print("✅ Existing admin functionality remains operational")
        
        print("\n" + "=" * 80)
        
        return self.results["failed_tests"] == 0

if __name__ == "__main__":
    tester = CriticalBugsTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL CRITICAL BUG FIXES VERIFIED - Both bugs have been successfully resolved!")
        sys.exit(0)
    else:
        print("⚠️  Some critical bug fix tests failed - review the issues above")
        sys.exit(1)