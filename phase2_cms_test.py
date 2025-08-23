import requests
import sys
import json
from datetime import datetime
import time
import io
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://217.154.0.82/api"  # From frontend/.env
STATIC_URL = "http://217.154.0.82"  # For static file serving
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class Phase2CMSTester:
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
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_result("Admin Login", True, "Successfully authenticated as admin")
                return True
            else:
                self.log_result("Admin Login", False, f"Login failed with status {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Login error: {str(e)}")
            return False

    def test_new_color_fields(self):
        """Test that new color fields can be saved and retrieved"""
        print("=== TESTING NEW COLOR FIELDS ===")
        
        # Test data for new color fields
        test_colors = {
            "font_color": "#2d3748",  # gray-800
            "link_color": "#4299e1",  # blue-400
            "link_hover_color": "#2b6cb0"  # blue-600
        }
        
        try:
            # First, get current settings
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            if response.status_code != 200:
                self.log_result("Get Current Settings", False, f"Failed to get settings: {response.status_code}")
                return False
                
            current_settings = response.json()
            self.log_result("Get Current Settings", True, "Retrieved current CMS settings")
            
            # Update settings with new color fields
            update_data = current_settings.copy()
            update_data.update(test_colors)
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=update_data)
            if response.status_code != 200:
                self.log_result("Update Color Fields", False, f"Failed to update settings: {response.status_code}",
                              {"response": response.text})
                return False
                
            self.log_result("Update Color Fields", True, "Successfully updated CMS settings with new color fields")
            
            # Verify the fields were saved by retrieving settings again
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            if response.status_code != 200:
                self.log_result("Verify Color Fields", False, f"Failed to retrieve updated settings: {response.status_code}")
                return False
                
            updated_settings = response.json()
            
            # Check each color field
            all_fields_correct = True
            for field, expected_value in test_colors.items():
                actual_value = updated_settings.get(field)
                if actual_value == expected_value:
                    self.log_result(f"Verify {field}", True, f"Field correctly saved: {actual_value}")
                else:
                    self.log_result(f"Verify {field}", False, f"Field mismatch - Expected: {expected_value}, Got: {actual_value}")
                    all_fields_correct = False
            
            # Also test via public API
            response = self.session.get(f"{BACKEND_URL}/cms/settings")
            if response.status_code == 200:
                public_settings = response.json()
                for field, expected_value in test_colors.items():
                    actual_value = public_settings.get(field)
                    if actual_value == expected_value:
                        self.log_result(f"Public API {field}", True, f"Field available in public API: {actual_value}")
                    else:
                        self.log_result(f"Public API {field}", False, f"Field not in public API or incorrect value")
                        all_fields_correct = False
            
            return all_fields_correct
            
        except Exception as e:
            self.log_result("Color Fields Test", False, f"Exception during color fields test: {str(e)}")
            return False

    def test_new_hero_fields(self):
        """Test that new hero section fields can be saved and retrieved"""
        print("=== TESTING NEW HERO SECTION FIELDS ===")
        
        # Test data for new hero fields
        test_hero_data = {
            "hero_image_url": "/uploads/test_hero_image.jpg",
            "hero_background_image_url": "/uploads/test_hero_bg.jpg", 
            "hero_background_size": "contain"
        }
        
        try:
            # Get current settings
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            if response.status_code != 200:
                self.log_result("Get Settings for Hero Test", False, f"Failed to get settings: {response.status_code}")
                return False
                
            current_settings = response.json()
            
            # Update settings with new hero fields
            update_data = current_settings.copy()
            update_data.update(test_hero_data)
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=update_data)
            if response.status_code != 200:
                self.log_result("Update Hero Fields", False, f"Failed to update settings: {response.status_code}",
                              {"response": response.text})
                return False
                
            self.log_result("Update Hero Fields", True, "Successfully updated CMS settings with new hero fields")
            
            # Verify the fields were saved
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            if response.status_code != 200:
                self.log_result("Verify Hero Fields", False, f"Failed to retrieve updated settings: {response.status_code}")
                return False
                
            updated_settings = response.json()
            
            # Check each hero field
            all_fields_correct = True
            for field, expected_value in test_hero_data.items():
                actual_value = updated_settings.get(field)
                if actual_value == expected_value:
                    self.log_result(f"Verify {field}", True, f"Field correctly saved: {actual_value}")
                else:
                    self.log_result(f"Verify {field}", False, f"Field mismatch - Expected: {expected_value}, Got: {actual_value}")
                    all_fields_correct = False
            
            # Test via public API
            response = self.session.get(f"{BACKEND_URL}/cms/settings")
            if response.status_code == 200:
                public_settings = response.json()
                for field, expected_value in test_hero_data.items():
                    actual_value = public_settings.get(field)
                    if actual_value == expected_value:
                        self.log_result(f"Public API {field}", True, f"Field available in public API: {actual_value}")
                    else:
                        self.log_result(f"Public API {field}", False, f"Field not in public API or incorrect value")
                        all_fields_correct = False
            
            return all_fields_correct
            
        except Exception as e:
            self.log_result("Hero Fields Test", False, f"Exception during hero fields test: {str(e)}")
            return False

    def create_test_image(self, size_mb=1):
        """Create a test image file in memory"""
        from PIL import Image
        import io
        
        # Create a simple test image
        img = Image.new('RGB', (800, 600), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # If we need a larger file, repeat the data
        if size_mb > 1:
            data = img_bytes.getvalue()
            target_size = size_mb * 1024 * 1024
            multiplier = (target_size // len(data)) + 1
            large_data = data * multiplier
            img_bytes = io.BytesIO(large_data[:target_size])
            img_bytes.seek(0)
        
        return img_bytes

    def test_hero_image_upload(self):
        """Test hero image upload endpoint"""
        print("=== TESTING HERO IMAGE UPLOAD ENDPOINT ===")
        
        try:
            # Test 1: Valid PNG upload
            test_image = self.create_test_image(1)  # 1MB image
            files = {'file': ('test_hero.png', test_image, 'image/png')}
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                hero_image_url = data.get('hero_image_url')
                self.log_result("Hero Image Upload - Valid PNG", True, f"Successfully uploaded hero image: {hero_image_url}")
                
                # Test if the uploaded file is accessible
                if hero_image_url:
                    file_response = requests.get(f"{STATIC_URL}{hero_image_url}")
                    if file_response.status_code == 200:
                        self.log_result("Hero Image Accessibility", True, f"Uploaded hero image is accessible via HTTP")
                    else:
                        self.log_result("Hero Image Accessibility", False, f"Uploaded hero image not accessible: {file_response.status_code}")
            else:
                self.log_result("Hero Image Upload - Valid PNG", False, f"Upload failed: {response.status_code}",
                              {"response": response.text})
                return False
            
            # Test 2: Invalid file type (GIF)
            gif_data = io.BytesIO(b'GIF89a\x01\x00\x01\x00\x00\x00\x00!')  # Minimal GIF header
            files = {'file': ('test.gif', gif_data, 'image/gif')}
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            if response.status_code == 400:
                self.log_result("Hero Image Upload - Invalid Type", True, "Correctly rejected GIF file")
            else:
                self.log_result("Hero Image Upload - Invalid Type", False, f"Should reject GIF files, got: {response.status_code}")
            
            # Test 3: File size limit (6MB file should be rejected)
            try:
                large_image = self.create_test_image(6)  # 6MB image
                files = {'file': ('large_test.png', large_image, 'image/png')}
                
                response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
                
                if response.status_code == 400 or response.status_code == 413:
                    self.log_result("Hero Image Upload - Size Limit", True, f"Correctly rejected large file: {response.status_code}")
                else:
                    self.log_result("Hero Image Upload - Size Limit", False, f"Should reject large files, got: {response.status_code}")
            except Exception as e:
                self.log_result("Hero Image Upload - Size Limit", False, f"Error testing size limit: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_result("Hero Image Upload Test", False, f"Exception during hero image upload test: {str(e)}")
            return False

    def test_hero_background_upload(self):
        """Test hero background upload endpoint"""
        print("=== TESTING HERO BACKGROUND UPLOAD ENDPOINT ===")
        
        try:
            # Test 1: Valid PNG upload
            test_image = self.create_test_image(2)  # 2MB image
            files = {'file': ('test_hero_bg.png', test_image, 'image/png')}
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-background", files=files)
            
            if response.status_code == 200:
                data = response.json()
                hero_bg_url = data.get('hero_background_image_url')
                self.log_result("Hero Background Upload - Valid PNG", True, f"Successfully uploaded hero background: {hero_bg_url}")
                
                # Test if the uploaded file is accessible
                if hero_bg_url:
                    file_response = requests.get(f"{STATIC_URL}{hero_bg_url}")
                    if file_response.status_code == 200:
                        self.log_result("Hero Background Accessibility", True, f"Uploaded hero background is accessible via HTTP")
                    else:
                        self.log_result("Hero Background Accessibility", False, f"Uploaded hero background not accessible: {file_response.status_code}")
            else:
                self.log_result("Hero Background Upload - Valid PNG", False, f"Upload failed: {response.status_code}",
                              {"response": response.text})
                return False
            
            # Test 2: Invalid file type (GIF)
            gif_data = io.BytesIO(b'GIF89a\x01\x00\x01\x00\x00\x00\x00!')  # Minimal GIF header
            files = {'file': ('test.gif', gif_data, 'image/gif')}
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-background", files=files)
            
            if response.status_code == 400:
                self.log_result("Hero Background Upload - Invalid Type", True, "Correctly rejected GIF file")
            else:
                self.log_result("Hero Background Upload - Invalid Type", False, f"Should reject GIF files, got: {response.status_code}")
            
            # Test 3: Large file (test with smaller size due to nginx limits)
            try:
                large_image = self.create_test_image(10)  # 10MB image (smaller than 25MB limit)
                files = {'file': ('large_bg.png', large_image, 'image/png')}
                
                response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-background", files=files)
                
                if response.status_code == 200:
                    self.log_result("Hero Background Upload - Large File", True, "Successfully uploaded large background image")
                elif response.status_code == 413:
                    self.log_result("Hero Background Upload - Large File", False, "Nginx file size limit blocking upload (infrastructure issue)")
                else:
                    self.log_result("Hero Background Upload - Large File", False, f"Unexpected response: {response.status_code}")
            except Exception as e:
                self.log_result("Hero Background Upload - Large File", False, f"Error testing large file: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_result("Hero Background Upload Test", False, f"Exception during hero background upload test: {str(e)}")
            return False

    def test_cms_settings_integration(self):
        """Test that all new fields can be included in site settings updates"""
        print("=== TESTING CMS SETTINGS INTEGRATION ===")
        
        # Complete test data with all Phase 2 fields
        phase2_fields = {
            "font_color": "#1a202c",  # gray-900
            "link_color": "#3182ce",  # blue-600
            "link_hover_color": "#2c5282",  # blue-800
            "hero_image_url": "/uploads/integration_test_hero.jpg",
            "hero_background_image_url": "/uploads/integration_test_bg.jpg",
            "hero_background_size": "cover"
        }
        
        try:
            # Get current settings
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            if response.status_code != 200:
                self.log_result("Get Settings for Integration", False, f"Failed to get settings: {response.status_code}")
                return False
                
            current_settings = response.json()
            
            # Update with all Phase 2 fields at once
            update_data = current_settings.copy()
            update_data.update(phase2_fields)
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=update_data)
            if response.status_code != 200:
                self.log_result("Update All Phase 2 Fields", False, f"Failed to update settings: {response.status_code}",
                              {"response": response.text})
                return False
                
            self.log_result("Update All Phase 2 Fields", True, "Successfully updated all Phase 2 fields together")
            
            # Verify all fields were saved correctly
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            if response.status_code != 200:
                self.log_result("Verify Integration", False, f"Failed to retrieve updated settings: {response.status_code}")
                return False
                
            updated_settings = response.json()
            
            all_correct = True
            for field, expected_value in phase2_fields.items():
                actual_value = updated_settings.get(field)
                if actual_value == expected_value:
                    self.log_result(f"Integration {field}", True, f"Field correctly saved: {actual_value}")
                else:
                    self.log_result(f"Integration {field}", False, f"Field mismatch - Expected: {expected_value}, Got: {actual_value}")
                    all_correct = False
            
            # Test database persistence by making another request
            time.sleep(1)  # Brief pause
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            if response.status_code == 200:
                persistent_settings = response.json()
                for field, expected_value in phase2_fields.items():
                    actual_value = persistent_settings.get(field)
                    if actual_value == expected_value:
                        self.log_result(f"Persistence {field}", True, f"Field persisted correctly: {actual_value}")
                    else:
                        self.log_result(f"Persistence {field}", False, f"Field not persisted correctly")
                        all_correct = False
            
            return all_correct
            
        except Exception as e:
            self.log_result("CMS Settings Integration", False, f"Exception during integration test: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all Phase 2 CMS tests"""
        print("🚀 STARTING PHASE 2 CMS SETTINGS TESTING")
        print("=" * 60)
        
        # Login first
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Run all tests
        tests_passed = 0
        total_tests = 5
        
        if self.test_new_color_fields():
            tests_passed += 1
            
        if self.test_new_hero_fields():
            tests_passed += 1
            
        if self.test_hero_image_upload():
            tests_passed += 1
            
        if self.test_hero_background_upload():
            tests_passed += 1
            
        if self.test_cms_settings_integration():
            tests_passed += 1
        
        # Print summary
        print("=" * 60)
        print("🏁 PHASE 2 CMS TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (tests_passed / total_tests) * 100
        print(f"Tests Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        
        passed_tests = [r for r in self.test_results if "✅ PASS" in r["status"]]
        failed_tests = [r for r in self.test_results if "❌ FAIL" in r["status"]]
        
        if passed_tests:
            print(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
            for result in passed_tests:
                print(f"  • {result['test']}")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"  • {result['test']}: {result['message']}")
        
        return tests_passed == total_tests

if __name__ == "__main__":
    # Install PIL if not available
    try:
        from PIL import Image
    except ImportError:
        print("Installing Pillow for image testing...")
        os.system("pip install Pillow")
        from PIL import Image
    
    tester = Phase2CMSTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL PHASE 2 CMS TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME PHASE 2 CMS TESTS FAILED")
        sys.exit(1)