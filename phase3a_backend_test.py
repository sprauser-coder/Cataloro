import requests
import sys
import json
from datetime import datetime, timedelta
import time
import io
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://217.154.0.82/api"  # From frontend/.env
STATIC_URL = "http://217.154.0.82"  # For static file serving
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class Phase3ATester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.created_pages = []  # Track created pages for cleanup
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}")
        print()

    def admin_login(self):
        """Login as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.log_result("Admin Login", True, "Successfully logged in as admin", {
                    "user_id": data["user"]["id"],
                    "role": data["user"]["role"]
                })
                return True
            else:
                self.log_result("Admin Login", False, f"Login failed with status {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Login error: {str(e)}")
            return False

    def create_test_user(self):
        """Create a test user for profile testing"""
        try:
            user_data = {
                "email": "testuser@example.com",
                "username": "testuser",
                "password": "testpass123",
                "full_name": "Test User",
                "role": "buyer",
                "phone": "123-456-7890",
                "address": "123 Test Street, Test City"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["access_token"]
                self.log_result("Test User Creation", True, "Successfully created test user", {
                    "user_id": data["user"]["id"],
                    "email": data["user"]["email"]
                })
                return True
            else:
                # User might already exist, try to login
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                
                login_response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.user_token = data["access_token"]
                    self.log_result("Test User Login", True, "Successfully logged in existing test user", {
                        "user_id": data["user"]["id"],
                        "email": data["user"]["email"]
                    })
                    return True
                else:
                    self.log_result("Test User Creation", False, f"Failed to create or login test user: {response.status_code}", {
                        "response": response.text
                    })
                    return False
                
        except Exception as e:
            self.log_result("Test User Creation", False, f"User creation error: {str(e)}")
            return False

    def test_page_management_create(self):
        """Test POST /admin/cms/pages - Create new page"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            page_data = {
                "page_slug": "test-page-phase3a",
                "title": "Test Page Phase 3A",
                "content": "<h1>Test Page Content</h1><p>This is a test page for Phase 3A testing.</p>",
                "is_published": True,
                "meta_description": "Test page for Phase 3A functionality",
                "custom_css": ".test-class { color: blue; }"
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/pages", json=page_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.created_pages.append(page_data["page_slug"])
                self.log_result("Page Creation", True, "Successfully created new page", {
                    "page_slug": page_data["page_slug"],
                    "title": page_data["title"],
                    "response": data.get("message", "")
                })
                return True
            else:
                self.log_result("Page Creation", False, f"Failed to create page: {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Page Creation", False, f"Page creation error: {str(e)}")
            return False

    def test_page_management_list(self):
        """Test GET /admin/cms/pages - List all pages"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = self.session.get(f"{BACKEND_URL}/admin/cms/pages", headers=headers)
            
            if response.status_code == 200:
                pages = response.json()
                self.log_result("Page List", True, f"Successfully retrieved {len(pages)} pages", {
                    "total_pages": len(pages),
                    "page_slugs": [page.get("page_slug", "unknown") for page in pages[:5]]  # Show first 5
                })
                return True
            else:
                self.log_result("Page List", False, f"Failed to retrieve pages: {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Page List", False, f"Page list error: {str(e)}")
            return False

    def test_page_management_update(self):
        """Test PUT /admin/cms/pages/{id} - Update page"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Update the test page we created
            page_slug = "test-page-phase3a"
            update_data = {
                "title": "Updated Test Page Phase 3A",
                "content": "<h1>Updated Content</h1><p>This page has been updated during Phase 3A testing.</p>",
                "is_published": False,  # Test unpublished functionality
                "meta_description": "Updated test page for Phase 3A functionality"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/pages/{page_slug}", json=update_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Page Update", True, "Successfully updated page", {
                    "page_slug": page_slug,
                    "new_title": update_data["title"],
                    "published": update_data["is_published"],
                    "response": data.get("message", "")
                })
                return True
            else:
                self.log_result("Page Update", False, f"Failed to update page: {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Page Update", False, f"Page update error: {str(e)}")
            return False

    def test_page_management_delete(self):
        """Test DELETE /admin/cms/pages/{id} - Delete page"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Delete the test page we created
            page_slug = "test-page-phase3a"
            
            response = self.session.delete(f"{BACKEND_URL}/admin/cms/pages/{page_slug}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if page_slug in self.created_pages:
                    self.created_pages.remove(page_slug)
                self.log_result("Page Delete", True, "Successfully deleted page", {
                    "page_slug": page_slug,
                    "response": data.get("message", "")
                })
                return True
            else:
                self.log_result("Page Delete", False, f"Failed to delete page: {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Page Delete", False, f"Page delete error: {str(e)}")
            return False

    def test_page_published_unpublished(self):
        """Test published/unpublished page functionality"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create a test page
            page_data = {
                "page_slug": "publish-test-page",
                "title": "Publish Test Page",
                "content": "<h1>Publish Test</h1>",
                "is_published": True,
                "meta_description": "Test page for publish functionality"
            }
            
            # Create page
            create_response = self.session.post(f"{BACKEND_URL}/admin/cms/pages", json=page_data, headers=headers)
            if create_response.status_code != 200:
                self.log_result("Published/Unpublished Test", False, "Failed to create test page for publish test")
                return False
            
            self.created_pages.append(page_data["page_slug"])
            
            # Test published page is accessible publicly
            public_response = self.session.get(f"{BACKEND_URL}/cms/pages/{page_data['page_slug']}")
            published_accessible = public_response.status_code == 200
            
            # Update page to unpublished
            update_data = {"is_published": False}
            update_response = self.session.put(f"{BACKEND_URL}/admin/cms/pages/{page_data['page_slug']}", json=update_data, headers=headers)
            
            if update_response.status_code != 200:
                self.log_result("Published/Unpublished Test", False, "Failed to update page to unpublished")
                return False
            
            # Test unpublished page is not accessible publicly
            unpublic_response = self.session.get(f"{BACKEND_URL}/cms/pages/{page_data['page_slug']}")
            unpublished_not_accessible = unpublic_response.status_code == 404
            
            success = published_accessible and unpublished_not_accessible
            self.log_result("Published/Unpublished Test", success, "Tested page publish/unpublish functionality", {
                "published_accessible": published_accessible,
                "unpublished_not_accessible": unpublished_not_accessible,
                "public_status_published": public_response.status_code,
                "public_status_unpublished": unpublic_response.status_code
            })
            
            return success
                
        except Exception as e:
            self.log_result("Published/Unpublished Test", False, f"Publish test error: {str(e)}")
            return False

    def test_profile_endpoints(self):
        """Test profile endpoints - GET /profile, PUT /profile, GET /profile/stats, GET /listings/my-listings"""
        try:
            if not self.user_token:
                self.log_result("Profile Endpoints Test", False, "No user token available for profile testing")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test GET /profile
            profile_response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            profile_success = profile_response.status_code == 200
            
            if not profile_success:
                self.log_result("Profile Endpoints Test", False, f"GET /profile failed: {profile_response.status_code}", {
                    "response": profile_response.text
                })
                return False
            
            # Test PUT /profile
            profile_update_data = {
                "full_name": "Updated Test User",
                "phone": "987-654-3210",
                "address": "456 Updated Street, New City"
            }
            
            profile_update_response = self.session.put(f"{BACKEND_URL}/profile", json=profile_update_data, headers=headers)
            profile_update_success = profile_update_response.status_code == 200
            
            # Test GET /profile/stats
            stats_response = self.session.get(f"{BACKEND_URL}/profile/stats", headers=headers)
            stats_success = stats_response.status_code == 200
            
            # Test GET /listings/my-listings
            my_listings_response = self.session.get(f"{BACKEND_URL}/listings/my-listings", headers=headers)
            my_listings_success = my_listings_response.status_code == 200
            
            overall_success = profile_success and profile_update_success and stats_success and my_listings_success
            
            self.log_result("Profile Endpoints Test", overall_success, "Tested all profile endpoints", {
                "GET_profile": f"{profile_response.status_code} {'✅' if profile_success else '❌'}",
                "PUT_profile": f"{profile_update_response.status_code} {'✅' if profile_update_success else '❌'}",
                "GET_profile_stats": f"{stats_response.status_code} {'✅' if stats_success else '❌'}",
                "GET_my_listings": f"{my_listings_response.status_code} {'✅' if my_listings_success else '❌'}"
            })
            
            return overall_success
                
        except Exception as e:
            self.log_result("Profile Endpoints Test", False, f"Profile endpoints error: {str(e)}")
            return False

    def test_hero_height_settings(self):
        """Test that hero_height is properly managed in Appearance > Hero section only"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get current site settings
            settings_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings", headers=headers)
            
            if settings_response.status_code != 200:
                self.log_result("Hero Height Settings Test", False, f"Failed to get site settings: {settings_response.status_code}")
                return False
            
            settings = settings_response.json()
            
            # Check if hero_height field exists and has a default value
            hero_height_exists = "hero_height" in settings
            hero_height_value = settings.get("hero_height", None)
            
            # Test updating hero_height
            update_data = {
                "hero_height": "800px"
            }
            
            update_response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=update_data, headers=headers)
            update_success = update_response.status_code == 200
            
            # Verify the update
            verify_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings", headers=headers)
            if verify_response.status_code == 200:
                updated_settings = verify_response.json()
                hero_height_updated = updated_settings.get("hero_height") == "800px"
            else:
                hero_height_updated = False
            
            # Test public access to hero_height
            public_settings_response = self.session.get(f"{BACKEND_URL}/cms/settings")
            public_success = public_settings_response.status_code == 200
            
            if public_success:
                public_settings = public_settings_response.json()
                hero_height_public = public_settings.get("hero_height")
            else:
                hero_height_public = None
            
            overall_success = hero_height_exists and update_success and hero_height_updated and public_success
            
            self.log_result("Hero Height Settings Test", overall_success, "Tested hero height settings functionality", {
                "hero_height_exists": hero_height_exists,
                "current_value": hero_height_value,
                "update_success": update_success,
                "value_updated": hero_height_updated,
                "public_accessible": public_success,
                "public_value": hero_height_public
            })
            
            return overall_success
                
        except Exception as e:
            self.log_result("Hero Height Settings Test", False, f"Hero height test error: {str(e)}")
            return False

    def test_footer_version_functionality(self):
        """Test footer version functionality"""
        try:
            # Test that CMS settings are properly loaded for footer display
            public_settings_response = self.session.get(f"{BACKEND_URL}/cms/settings")
            
            if public_settings_response.status_code != 200:
                self.log_result("Footer Version Test", False, f"Failed to get public settings: {public_settings_response.status_code}")
                return False
            
            settings = public_settings_response.json()
            
            # Check if site_name is available for footer display
            site_name = settings.get("site_name")
            site_name_exists = site_name is not None and site_name != ""
            
            # Check if other footer-relevant settings are available
            footer_relevant_fields = ["site_name", "site_tagline", "primary_color", "secondary_color"]
            footer_fields_available = all(field in settings for field in footer_relevant_fields)
            
            self.log_result("Footer Version Test", footer_fields_available and site_name_exists, "Tested footer version functionality", {
                "site_name": site_name,
                "site_name_exists": site_name_exists,
                "footer_fields_available": footer_fields_available,
                "available_fields": [field for field in footer_relevant_fields if field in settings]
            })
            
            return footer_fields_available and site_name_exists
                
        except Exception as e:
            self.log_result("Footer Version Test", False, f"Footer version test error: {str(e)}")
            return False

    def cleanup(self):
        """Clean up created test pages"""
        if not self.admin_token:
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for page_slug in self.created_pages:
            try:
                self.session.delete(f"{BACKEND_URL}/admin/cms/pages/{page_slug}", headers=headers)
                print(f"Cleaned up test page: {page_slug}")
            except:
                pass

    def run_all_tests(self):
        """Run all Phase 3A tests"""
        print("=" * 80)
        print("PHASE 3A BACKEND TESTING - CORE CONTENT MANAGEMENT FEATURES")
        print("=" * 80)
        print()
        
        # Login as admin
        if not self.admin_login():
            print("❌ Cannot proceed without admin login")
            return
        
        # Create test user for profile testing
        self.create_test_user()
        
        # Test Page Management endpoints
        print("🔍 TESTING PAGE MANAGEMENT ENDPOINTS")
        print("-" * 50)
        self.test_page_management_create()
        self.test_page_management_list()
        self.test_page_management_update()
        self.test_page_published_unpublished()
        self.test_page_management_delete()
        
        print("\n🔍 TESTING PROFILE ENDPOINTS")
        print("-" * 50)
        self.test_profile_endpoints()
        
        print("\n🔍 TESTING GENERAL SETTINGS CHANGES")
        print("-" * 50)
        self.test_hero_height_settings()
        
        print("\n🔍 TESTING FOOTER VERSION FUNCTIONALITY")
        print("-" * 50)
        self.test_footer_version_functionality()
        
        # Cleanup
        self.cleanup()
        
        # Summary
        print("\n" + "=" * 80)
        print("PHASE 3A TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 80)
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = Phase3ATester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)