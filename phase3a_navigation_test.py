import requests
import sys
import json

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class NavigationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
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
                return True
            else:
                self.log_result("Admin Login", False, f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Login error: {str(e)}")
            return False

    def test_show_in_navigation_functionality(self):
        """Test show_in_navigation functionality for pages"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get initial navigation count
            initial_nav_response = self.session.get(f"{BACKEND_URL}/cms/navigation")
            if initial_nav_response.status_code == 200:
                initial_nav_count = len(initial_nav_response.json())
            else:
                initial_nav_count = 0
            
            # Create a page that should appear in navigation (published)
            page_data_visible = {
                "page_slug": "nav-test-visible",
                "title": "Navigation Test Visible",
                "content": "<h1>This page should appear in navigation</h1>",
                "is_published": True,
                "meta_description": "Test page for navigation visibility"
            }
            
            create_response = self.session.post(f"{BACKEND_URL}/admin/cms/pages", json=page_data_visible, headers=headers)
            
            if create_response.status_code != 200:
                self.log_result("Show in Navigation Test", False, "Failed to create test page")
                return False
            
            # Check if navigation was automatically updated
            nav_response = self.session.get(f"{BACKEND_URL}/cms/navigation")
            
            if nav_response.status_code == 200:
                nav_items = nav_response.json()
                new_nav_count = len(nav_items)
                
                # Check if our page was added to navigation
                page_in_nav = any(item.get("url") == f"/{page_data_visible['page_slug']}" for item in nav_items)
                
                # Create an unpublished page
                page_data_hidden = {
                    "page_slug": "nav-test-hidden",
                    "title": "Navigation Test Hidden",
                    "content": "<h1>This page should not appear in navigation</h1>",
                    "is_published": False,
                    "meta_description": "Test page for navigation hiding"
                }
                
                create_hidden_response = self.session.post(f"{BACKEND_URL}/admin/cms/pages", json=page_data_hidden, headers=headers)
                
                # Check navigation again
                nav_response2 = self.session.get(f"{BACKEND_URL}/cms/navigation")
                if nav_response2.status_code == 200:
                    nav_items2 = nav_response2.json()
                    hidden_page_in_nav = any(item.get("url") == f"/{page_data_hidden['page_slug']}" for item in nav_items2)
                    
                    # Test updating page to unpublished and check navigation
                    update_data = {"is_published": False}
                    update_response = self.session.put(f"{BACKEND_URL}/admin/cms/pages/{page_data_visible['page_slug']}", json=update_data, headers=headers)
                    
                    if update_response.status_code == 200:
                        # Check if navigation item was updated to invisible
                        nav_response3 = self.session.get(f"{BACKEND_URL}/cms/navigation")
                        if nav_response3.status_code == 200:
                            nav_items3 = nav_response3.json()
                            visible_nav_items = [item for item in nav_items3 if item.get("is_visible", True)]
                            updated_page_visible = any(item.get("url") == f"/{page_data_visible['page_slug']}" for item in visible_nav_items)
                        else:
                            updated_page_visible = True  # Assume visible if can't check
                    else:
                        updated_page_visible = True
                    
                    success = page_in_nav and not hidden_page_in_nav and not updated_page_visible
                    
                    self.log_result("Show in Navigation Test", success, "Tested show_in_navigation functionality", {
                        "initial_nav_count": initial_nav_count,
                        "nav_count_after_published": new_nav_count,
                        "published_page_in_nav": page_in_nav,
                        "unpublished_page_in_nav": hidden_page_in_nav,
                        "updated_page_still_visible": updated_page_visible,
                        "auto_add_pages_working": new_nav_count > initial_nav_count
                    })
                    
                    # Cleanup
                    self.session.delete(f"{BACKEND_URL}/admin/cms/pages/{page_data_visible['page_slug']}", headers=headers)
                    self.session.delete(f"{BACKEND_URL}/admin/cms/pages/{page_data_hidden['page_slug']}", headers=headers)
                    
                    return success
                else:
                    self.log_result("Show in Navigation Test", False, "Failed to get navigation items after creating hidden page")
                    return False
            else:
                self.log_result("Show in Navigation Test", False, "Failed to get navigation items")
                return False
                
        except Exception as e:
            self.log_result("Show in Navigation Test", False, f"Navigation test error: {str(e)}")
            return False

    def run_navigation_tests(self):
        """Run navigation-specific tests"""
        print("=" * 80)
        print("PHASE 3A NAVIGATION TESTING")
        print("=" * 80)
        print()
        
        # Login as admin
        if not self.admin_login():
            print("❌ Cannot proceed without admin login")
            return
        
        # Test navigation functionality
        self.test_show_in_navigation_functionality()
        
        # Summary
        print("\n" + "=" * 80)
        print("NAVIGATION TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = NavigationTester()
    passed, failed = tester.run_navigation_tests()
    sys.exit(0 if failed == 0 else 1)