#!/usr/bin/env python3
"""
Phase 2 Backend Testing - Typography Preview and Header Link Colors
Testing the remaining Phase 2 bug fixes for CMS settings functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class Phase2BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
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
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Authentication", True, "Successfully authenticated as admin")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_phase2_fields_retrieval(self):
        """Test that Phase 2 fields are properly retrieved from site settings"""
        try:
            # Test admin endpoint
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            
            if response.status_code == 200:
                settings = response.json()
                
                # Check for Phase 2 fields
                phase2_fields = {
                    "font_color": settings.get("font_color"),
                    "link_color": settings.get("link_color"),
                    "link_hover_color": settings.get("link_hover_color"),
                    "hero_image_url": settings.get("hero_image_url"),
                    "hero_background_image_url": settings.get("hero_background_image_url"),
                    "hero_background_size": settings.get("hero_background_size"),
                    "global_font_family": settings.get("global_font_family")
                }
                
                missing_fields = [field for field, value in phase2_fields.items() if value is None and field not in ["hero_image_url", "hero_background_image_url"]]
                
                if not missing_fields:
                    self.log_test("Phase 2 Fields Retrieval (Admin)", True, "All Phase 2 fields present in admin settings", phase2_fields)
                else:
                    self.log_test("Phase 2 Fields Retrieval (Admin)", False, f"Missing fields: {missing_fields}", phase2_fields)
                
                return phase2_fields
            else:
                self.log_test("Phase 2 Fields Retrieval (Admin)", False, f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Phase 2 Fields Retrieval (Admin)", False, f"Exception occurred: {str(e)}")
            return None
    
    def test_public_phase2_fields_retrieval(self):
        """Test that Phase 2 fields are available in public CMS API"""
        try:
            # Test public endpoint (no auth required)
            response = requests.get(f"{BACKEND_URL}/cms/settings")
            
            if response.status_code == 200:
                settings = response.json()
                
                # Check for Phase 2 fields
                phase2_fields = {
                    "font_color": settings.get("font_color"),
                    "link_color": settings.get("link_color"),
                    "link_hover_color": settings.get("link_hover_color"),
                    "global_font_family": settings.get("global_font_family")
                }
                
                missing_fields = [field for field, value in phase2_fields.items() if value is None]
                
                if not missing_fields:
                    self.log_test("Phase 2 Fields Retrieval (Public)", True, "All Phase 2 fields present in public settings", phase2_fields)
                else:
                    self.log_test("Phase 2 Fields Retrieval (Public)", False, f"Missing fields: {missing_fields}", phase2_fields)
                
                return phase2_fields
            else:
                self.log_test("Phase 2 Fields Retrieval (Public)", False, f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Phase 2 Fields Retrieval (Public)", False, f"Exception occurred: {str(e)}")
            return None
    
    def test_typography_settings_update(self):
        """Test updating typography settings including global_font_family"""
        try:
            # Test updating global font family and other typography settings
            test_settings = {
                "global_font_family": "Poppins",
                "font_color": "#2d3748",
                "h1_color": "#1a202c",
                "h2_color": "#2d3748"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=test_settings)
            
            if response.status_code == 200:
                self.log_test("Typography Settings Update", True, "Successfully updated typography settings", test_settings)
                
                # Verify the update by retrieving settings
                verify_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
                if verify_response.status_code == 200:
                    updated_settings = verify_response.json()
                    
                    # Check if our updates were saved
                    verification_passed = True
                    for key, expected_value in test_settings.items():
                        actual_value = updated_settings.get(key)
                        if actual_value != expected_value:
                            verification_passed = False
                            self.log_test("Typography Settings Verification", False, f"Field {key}: expected {expected_value}, got {actual_value}")
                    
                    if verification_passed:
                        self.log_test("Typography Settings Verification", True, "All typography settings saved correctly")
                        return True
                    else:
                        return False
                else:
                    self.log_test("Typography Settings Verification", False, f"Failed to verify with status {verify_response.status_code}")
                    return False
            else:
                self.log_test("Typography Settings Update", False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Typography Settings Update", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_link_color_settings_update(self):
        """Test updating link color settings"""
        try:
            # Test updating link colors
            test_settings = {
                "link_color": "#e53e3e",
                "link_hover_color": "#c53030",
                "font_color": "#2d3748"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=test_settings)
            
            if response.status_code == 200:
                self.log_test("Link Color Settings Update", True, "Successfully updated link color settings", test_settings)
                
                # Verify the update by retrieving settings
                verify_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
                if verify_response.status_code == 200:
                    updated_settings = verify_response.json()
                    
                    # Check if our updates were saved
                    verification_passed = True
                    for key, expected_value in test_settings.items():
                        actual_value = updated_settings.get(key)
                        if actual_value != expected_value:
                            verification_passed = False
                            self.log_test("Link Color Settings Verification", False, f"Field {key}: expected {expected_value}, got {actual_value}")
                    
                    if verification_passed:
                        self.log_test("Link Color Settings Verification", True, "All link color settings saved correctly")
                        return True
                    else:
                        return False
                else:
                    self.log_test("Link Color Settings Verification", False, f"Failed to verify with status {verify_response.status_code}")
                    return False
            else:
                self.log_test("Link Color Settings Update", False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Link Color Settings Update", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_public_settings_include_phase2_fields(self):
        """Test that public settings endpoint includes Phase 2 fields for frontend consumption"""
        try:
            # First update some Phase 2 fields
            test_settings = {
                "global_font_family": "Inter",
                "link_color": "#3182ce",
                "link_hover_color": "#2c5282",
                "font_color": "#1a202c"
            }
            
            # Update via admin endpoint
            update_response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=test_settings)
            
            if update_response.status_code != 200:
                self.log_test("Public Settings Phase 2 Fields", False, "Failed to update settings for test")
                return False
            
            # Now check public endpoint
            public_response = requests.get(f"{BACKEND_URL}/cms/settings")
            
            if public_response.status_code == 200:
                public_settings = public_response.json()
                
                # Verify Phase 2 fields are present and correct
                verification_passed = True
                for key, expected_value in test_settings.items():
                    actual_value = public_settings.get(key)
                    if actual_value != expected_value:
                        verification_passed = False
                        self.log_test("Public Settings Field Check", False, f"Field {key}: expected {expected_value}, got {actual_value}")
                
                if verification_passed:
                    self.log_test("Public Settings Phase 2 Fields", True, "All Phase 2 fields correctly available in public API", test_settings)
                    return True
                else:
                    return False
            else:
                self.log_test("Public Settings Phase 2 Fields", False, f"Public endpoint failed with status {public_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Public Settings Phase 2 Fields", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_complete_phase2_workflow(self):
        """Test complete Phase 2 workflow: update settings and verify they're available for frontend"""
        try:
            # Complete Phase 2 settings update
            complete_settings = {
                "global_font_family": "Roboto",
                "font_color": "#2d3748",
                "link_color": "#4299e1",
                "link_hover_color": "#3182ce",
                "h1_color": "#1a202c",
                "h2_color": "#2d3748",
                "primary_color": "#4299e1",
                "secondary_color": "#805ad5"
            }
            
            # Step 1: Update settings
            update_response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=complete_settings)
            
            if update_response.status_code != 200:
                self.log_test("Complete Phase 2 Workflow", False, f"Settings update failed with status {update_response.status_code}")
                return False
            
            # Step 2: Verify admin endpoint has all fields
            admin_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            if admin_response.status_code != 200:
                self.log_test("Complete Phase 2 Workflow", False, "Admin settings retrieval failed")
                return False
            
            admin_settings = admin_response.json()
            
            # Step 3: Verify public endpoint has all fields
            public_response = requests.get(f"{BACKEND_URL}/cms/settings")
            if public_response.status_code != 200:
                self.log_test("Complete Phase 2 Workflow", False, "Public settings retrieval failed")
                return False
            
            public_settings = public_response.json()
            
            # Step 4: Verify all fields are present and consistent
            workflow_passed = True
            for key, expected_value in complete_settings.items():
                admin_value = admin_settings.get(key)
                public_value = public_settings.get(key)
                
                if admin_value != expected_value:
                    workflow_passed = False
                    self.log_test("Workflow Admin Consistency", False, f"Admin {key}: expected {expected_value}, got {admin_value}")
                
                if public_value != expected_value:
                    workflow_passed = False
                    self.log_test("Workflow Public Consistency", False, f"Public {key}: expected {expected_value}, got {public_value}")
                
                if admin_value != public_value:
                    workflow_passed = False
                    self.log_test("Workflow Admin-Public Consistency", False, f"{key}: admin={admin_value}, public={public_value}")
            
            if workflow_passed:
                self.log_test("Complete Phase 2 Workflow", True, "All Phase 2 settings work correctly across admin and public APIs")
                return True
            else:
                return False
                
        except Exception as e:
            self.log_test("Complete Phase 2 Workflow", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_default_values_integrity(self):
        """Test that Phase 2 fields have proper default values"""
        try:
            # Reset to defaults by creating fresh settings
            response = self.session.get(f"{BACKEND_URL}/admin/cms/test-settings")
            
            if response.status_code == 200:
                test_data = response.json()
                phase2_fields = test_data.get("phase2_fields", {})
                
                expected_defaults = {
                    "font_color": "#1f2937",
                    "link_color": "#3b82f6",
                    "link_hover_color": "#1d4ed8",
                    "hero_background_size": "cover"
                }
                
                defaults_correct = True
                for field, expected_default in expected_defaults.items():
                    actual_value = phase2_fields.get(field)
                    if actual_value != expected_default:
                        defaults_correct = False
                        self.log_test("Default Value Check", False, f"{field}: expected {expected_default}, got {actual_value}")
                
                if defaults_correct:
                    self.log_test("Default Values Integrity", True, "All Phase 2 fields have correct default values", expected_defaults)
                    return True
                else:
                    return False
            else:
                self.log_test("Default Values Integrity", False, f"Test endpoint failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Default Values Integrity", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Phase 2 backend tests"""
        print("🚀 Starting Phase 2 Backend Testing - Typography Preview and Header Link Colors")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Run all tests
        tests = [
            self.test_phase2_fields_retrieval,
            self.test_public_phase2_fields_retrieval,
            self.test_default_values_integrity,
            self.test_typography_settings_update,
            self.test_link_color_settings_update,
            self.test_public_settings_include_phase2_fields,
            self.test_complete_phase2_workflow
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 PHASE 2 BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🎉 PHASE 2 BACKEND FUNCTIONALITY: WORKING CORRECTLY")
            return True
        elif success_rate >= 70:
            print("⚠️  PHASE 2 BACKEND FUNCTIONALITY: MOSTLY WORKING (Minor Issues)")
            return True
        else:
            print("❌ PHASE 2 BACKEND FUNCTIONALITY: CRITICAL ISSUES FOUND")
            return False

def main():
    """Main test execution"""
    tester = Phase2BackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()