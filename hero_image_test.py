#!/usr/bin/env python3
"""
Hero Image Upload Functionality Testing
Testing hero image upload, validation, storage, and serving functionality
"""

import requests
import json
import os
import tempfile
from PIL import Image
import io

# Configuration
BACKEND_URL = "https://cataloro-profile-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class HeroImageTester:
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
                self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Failed with status {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def create_test_image(self, format="PNG", size_mb=1):
        """Create a test image file"""
        try:
            # Create image with specified size
            width = int((size_mb * 1024 * 1024 / 3) ** 0.5)  # Approximate size calculation
            height = width
            
            # Create RGB image
            img = Image.new('RGB', (width, height), color='red')
            
            # Save to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=format, quality=85)
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None

    def test_hero_image_upload_endpoint(self):
        """Test hero image upload endpoint functionality"""
        print("=== TESTING HERO IMAGE UPLOAD ENDPOINT ===")
        
        # Test 1: Valid PNG upload
        try:
            png_data = self.create_test_image("PNG", 1)  # 1MB PNG
            if not png_data:
                self.log_result("Hero Image Upload - PNG", False, "Failed to create test PNG image")
                return
                
            files = {"file": ("test_hero.png", png_data, "image/png")}
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                hero_url = data.get("hero_image_url")
                self.log_result("Hero Image Upload - PNG", True, "PNG upload successful", 
                              {"hero_image_url": hero_url, "response": data})
                
                # Test if uploaded file is accessible
                if hero_url:
                    self.test_hero_image_accessibility(hero_url)
                    
            else:
                self.log_result("Hero Image Upload - PNG", False, f"Upload failed with status {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Hero Image Upload - PNG", False, f"Exception: {str(e)}")

        # Test 2: Valid JPEG upload
        try:
            jpeg_data = self.create_test_image("JPEG", 2)  # 2MB JPEG
            if not jpeg_data:
                self.log_result("Hero Image Upload - JPEG", False, "Failed to create test JPEG image")
                return
                
            files = {"file": ("test_hero.jpg", jpeg_data, "image/jpeg")}
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Hero Image Upload - JPEG", True, "JPEG upload successful", 
                              {"hero_image_url": data.get("hero_image_url")})
            else:
                self.log_result("Hero Image Upload - JPEG", False, f"Upload failed with status {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Hero Image Upload - JPEG", False, f"Exception: {str(e)}")

        # Test 3: Invalid format (GIF) - should be rejected
        try:
            gif_data = self.create_test_image("GIF", 1)  # 1MB GIF
            if gif_data:
                files = {"file": ("test_hero.gif", gif_data, "image/gif")}
                response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
                
                if response.status_code == 400:
                    self.log_result("Hero Image Upload - Invalid Format", True, "GIF correctly rejected with 400 error")
                else:
                    self.log_result("Hero Image Upload - Invalid Format", False, 
                                  f"Expected 400 error, got {response.status_code}")
            else:
                self.log_result("Hero Image Upload - Invalid Format", False, "Failed to create test GIF")
                
        except Exception as e:
            self.log_result("Hero Image Upload - Invalid Format", False, f"Exception: {str(e)}")

        # Test 4: File size limit (6MB should be rejected)
        try:
            large_png = self.create_test_image("PNG", 6)  # 6MB PNG
            if large_png:
                files = {"file": ("large_hero.png", large_png, "image/png")}
                response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
                
                if response.status_code in [400, 413]:  # 400 for app validation, 413 for nginx
                    self.log_result("Hero Image Upload - Size Limit", True, 
                                  f"Large file correctly rejected with {response.status_code} error")
                else:
                    self.log_result("Hero Image Upload - Size Limit", False, 
                                  f"Expected 400/413 error, got {response.status_code}")
            else:
                self.log_result("Hero Image Upload - Size Limit", False, "Failed to create large test image")
                
        except Exception as e:
            self.log_result("Hero Image Upload - Size Limit", False, f"Exception: {str(e)}")

        # Test 5: Authentication required
        try:
            # Remove auth header temporarily
            auth_header = self.session.headers.pop("Authorization", None)
            
            png_data = self.create_test_image("PNG", 1)
            files = {"file": ("test_hero.png", png_data, "image/png")}
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            # Restore auth header
            if auth_header:
                self.session.headers["Authorization"] = auth_header
            
            if response.status_code == 403:
                self.log_result("Hero Image Upload - Auth Required", True, "Authentication properly enforced")
            else:
                self.log_result("Hero Image Upload - Auth Required", False, 
                              f"Expected 403 error, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Hero Image Upload - Auth Required", False, f"Exception: {str(e)}")

    def test_hero_image_accessibility(self, hero_url):
        """Test if uploaded hero image is accessible via HTTP"""
        print("=== TESTING HERO IMAGE ACCESSIBILITY ===")
        
        try:
            # Convert relative URL to absolute URL
            if hero_url.startswith('/'):
                full_url = BACKEND_URL.replace('/api', '') + hero_url
            else:
                full_url = hero_url
                
            # Test direct URL access
            response = requests.get(full_url)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    self.log_result("Hero Image Accessibility", True, "Hero image accessible via HTTP", 
                                  {"url": full_url, "content_type": content_type, "size": len(response.content)})
                else:
                    self.log_result("Hero Image Accessibility", False, "URL returns non-image content", 
                                  {"content_type": content_type, "content_preview": response.text[:200]})
            else:
                self.log_result("Hero Image Accessibility", False, f"Image not accessible, status {response.status_code}",
                              {"url": full_url, "response": response.text[:200]})
                
        except Exception as e:
            self.log_result("Hero Image Accessibility", False, f"Exception accessing image: {str(e)}")

    def test_hero_image_settings_integration(self):
        """Test hero image URL integration with site settings"""
        print("=== TESTING HERO IMAGE SETTINGS INTEGRATION ===")
        
        try:
            # Get current site settings
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            
            if response.status_code == 200:
                settings = response.json()
                hero_image_url = settings.get("hero_image_url")
                
                if hero_image_url:
                    self.log_result("Hero Image Settings - URL Present", True, "Hero image URL found in settings", 
                                  {"hero_image_url": hero_image_url})
                    
                    # Test if the URL from settings is accessible
                    self.test_hero_image_accessibility(hero_image_url)
                    
                else:
                    self.log_result("Hero Image Settings - URL Present", False, "No hero_image_url in settings")
                    
            else:
                self.log_result("Hero Image Settings - Retrieval", False, f"Failed to get settings, status {response.status_code}")
                
        except Exception as e:
            self.log_result("Hero Image Settings - Integration", False, f"Exception: {str(e)}")

        # Test public settings endpoint
        try:
            public_url = f"{BACKEND_URL.replace('/api', '')}/cms/settings"
            response = requests.get(public_url)
            
            if response.status_code == 200:
                public_settings = response.json()
                hero_image_url = public_settings.get("hero_image_url")
                
                if hero_image_url:
                    self.log_result("Hero Image Public Settings", True, "Hero image URL available in public settings", 
                                  {"hero_image_url": hero_image_url})
                else:
                    self.log_result("Hero Image Public Settings", False, "No hero_image_url in public settings")
                    
            else:
                self.log_result("Hero Image Public Settings", False, f"Failed to get public settings, status {response.status_code}",
                              {"url": public_url, "response": response.text[:200]})
                
        except Exception as e:
            self.log_result("Hero Image Public Settings", False, f"Exception: {str(e)}")

    def test_static_file_serving(self):
        """Test static file serving through different routes"""
        print("=== TESTING STATIC FILE SERVING ROUTES ===")
        
        # First upload a test image to get a filename
        try:
            png_data = self.create_test_image("PNG", 1)
            files = {"file": ("route_test_hero.png", png_data, "image/png")}
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                hero_url = data.get("hero_image_url")
                
                if hero_url:
                    # Extract filename from URL
                    filename = hero_url.split('/')[-1]
                    base_url = BACKEND_URL.replace('/api', '')
                    
                    # Test /uploads/ route
                    uploads_url = f"{base_url}/uploads/{filename}"
                    uploads_response = requests.get(uploads_url)
                    
                    if uploads_response.status_code == 200 and 'image' in uploads_response.headers.get('content-type', ''):
                        self.log_result("Static Serving - /uploads/ Route", True, "Image accessible via /uploads/ route",
                                      {"url": uploads_url, "content_type": uploads_response.headers.get('content-type')})
                    else:
                        self.log_result("Static Serving - /uploads/ Route", False, 
                                      f"Image not accessible via /uploads/, status {uploads_response.status_code}",
                                      {"url": uploads_url, "content_preview": uploads_response.text[:200]})
                    
                    # Test /api/uploads/ route
                    api_uploads_url = f"{BACKEND_URL}/uploads/{filename}"
                    api_response = requests.get(api_uploads_url)
                    
                    if api_response.status_code == 200 and 'image' in api_response.headers.get('content-type', ''):
                        self.log_result("Static Serving - /api/uploads/ Route", True, "Image accessible via /api/uploads/ route",
                                      {"url": api_uploads_url, "content_type": api_response.headers.get('content-type')})
                    else:
                        self.log_result("Static Serving - /api/uploads/ Route", False, 
                                      f"Image not accessible via /api/uploads/, status {api_response.status_code}",
                                      {"url": api_uploads_url, "content_preview": api_response.text[:200]})
                        
                else:
                    self.log_result("Static Serving Test Setup", False, "No hero_image_url returned from upload")
            else:
                self.log_result("Static Serving Test Setup", False, f"Failed to upload test image, status {response.status_code}")
                
        except Exception as e:
            self.log_result("Static File Serving", False, f"Exception: {str(e)}")

    def test_complete_workflow(self):
        """Test complete hero image workflow"""
        print("=== TESTING COMPLETE HERO IMAGE WORKFLOW ===")
        
        try:
            # Step 1: Upload hero image
            png_data = self.create_test_image("PNG", 2)
            files = {"file": ("workflow_hero.png", png_data, "image/png")}
            upload_response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            if upload_response.status_code != 200:
                self.log_result("Complete Workflow", False, "Failed at upload step")
                return
                
            upload_data = upload_response.json()
            hero_url = upload_data.get("hero_image_url")
            
            # Step 2: Verify settings are updated
            settings_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            if settings_response.status_code != 200:
                self.log_result("Complete Workflow", False, "Failed to retrieve settings after upload")
                return
                
            settings = settings_response.json()
            settings_hero_url = settings.get("hero_image_url")
            
            # Step 3: Verify image is accessible
            if hero_url:
                if hero_url.startswith('/'):
                    full_hero_url = BACKEND_URL.replace('/api', '') + hero_url
                else:
                    full_hero_url = hero_url
                image_response = requests.get(full_hero_url)
                image_accessible = image_response.status_code == 200 and 'image' in image_response.headers.get('content-type', '')
            else:
                image_accessible = False
            
            # Step 4: Verify public settings include hero image
            public_response = requests.get(f"{BACKEND_URL.replace('/api', '')}/cms/settings")
            public_accessible = public_response.status_code == 200
            public_hero_url = public_response.json().get("hero_image_url") if public_accessible else None
            
            # Evaluate complete workflow
            workflow_success = all([
                hero_url is not None,
                settings_hero_url == hero_url,
                image_accessible,
                public_accessible,
                public_hero_url == hero_url
            ])
            
            if workflow_success:
                self.log_result("Complete Hero Image Workflow", True, "All workflow steps completed successfully",
                              {
                                  "upload_url": hero_url,
                                  "settings_match": settings_hero_url == hero_url,
                                  "image_accessible": image_accessible,
                                  "public_settings_accessible": public_accessible,
                                  "public_url_match": public_hero_url == hero_url
                              })
            else:
                self.log_result("Complete Hero Image Workflow", False, "Workflow failed at one or more steps",
                              {
                                  "upload_url": hero_url,
                                  "settings_url": settings_hero_url,
                                  "image_accessible": image_accessible,
                                  "public_accessible": public_accessible,
                                  "public_url": public_hero_url
                              })
                
        except Exception as e:
            self.log_result("Complete Hero Image Workflow", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all hero image tests"""
        print("🚀 STARTING HERO IMAGE UPLOAD FUNCTIONALITY TESTING")
        print("=" * 60)
        
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
            
        # Run all test suites
        self.test_hero_image_upload_endpoint()
        self.test_hero_image_settings_integration()
        self.test_static_file_serving()
        self.test_complete_workflow()
        
        # Summary
        print("=" * 60)
        print("📊 HERO IMAGE TESTING SUMMARY")
        print("=" * 60)
        
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
        
        print("\n" + "=" * 60)
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = HeroImageTester()
    passed, failed = tester.run_all_tests()
    
    if failed == 0:
        print("🎉 ALL HERO IMAGE TESTS PASSED!")
    else:
        print(f"⚠️  {failed} TESTS FAILED - HERO IMAGE FUNCTIONALITY NEEDS ATTENTION")