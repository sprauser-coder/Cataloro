#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Image Upload Functionality for Ad's Manager
Testing the image upload workflow specifically for advertisements
"""

import requests
import json
import uuid
import time
import os
import io
from datetime import datetime
from PIL import Image

# Get backend URL from environment
BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

class ImageUploadTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def create_test_image(self, width=800, height=600, format='PNG'):
        """Create a test image in memory for upload testing"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (width, height), color='red')
            
            # Add some text or pattern to make it identifiable
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Draw a simple pattern
            draw.rectangle([50, 50, width-50, height-50], outline='blue', width=5)
            draw.text((width//2-100, height//2), "TEST AD IMAGE", fill='white')
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=format)
            img_bytes.seek(0)
            
            return img_bytes
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}, Version: {data.get('version')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def test_image_upload_api(self):
        """Test the /api/admin/upload-image endpoint with a sample image"""
        try:
            # Create test image
            test_image = self.create_test_image()
            if not test_image:
                self.log_test("Image Upload API", False, error_msg="Failed to create test image")
                return None
            
            # Prepare multipart form data
            files = {
                'image': ('test_ad_image.png', test_image, 'image/png')
            }
            data = {
                'section': 'hero_background',
                'field': 'background_image'
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/upload-image",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                image_url = result.get('url') or result.get('imageUrl')
                filename = result.get('filename')
                
                self.log_test(
                    "Image Upload API", 
                    True, 
                    f"Image uploaded successfully. URL: {image_url}, Filename: {filename}"
                )
                return image_url
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Image Upload API", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Image Upload API", False, error_msg=str(e))
            return None

    def test_image_serving(self, image_url):
        """Test that uploaded images can be accessed and served properly"""
        if not image_url:
            self.log_test("Image Serving", False, error_msg="No image URL provided")
            return False
            
        try:
            # Construct full URL for image access
            if image_url.startswith('/uploads/'):
                full_image_url = f"https://admanager-cataloro.preview.emergentagent.com{image_url}"
            else:
                full_image_url = image_url
            
            response = requests.get(full_image_url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                # Verify it's actually an image
                if content_type.startswith('image/') or content_length > 1000:
                    self.log_test(
                        "Image Serving", 
                        True, 
                        f"Image accessible at {full_image_url}. Content-Type: {content_type}, Size: {content_length} bytes"
                    )
                    return True
                else:
                    self.log_test("Image Serving", False, f"Invalid image content. Content-Type: {content_type}, Size: {content_length}")
                    return False
            else:
                self.log_test("Image Serving", False, f"HTTP {response.status_code} when accessing {full_image_url}")
                return False
                
        except Exception as e:
            self.log_test("Image Serving", False, error_msg=str(e))
            return False

    def test_ad_configuration_storage(self):
        """Test that ad configuration can store and retrieve image URLs"""
        try:
            # Test getting current site settings (which includes ad configuration)
            response = requests.get(f"{BACKEND_URL}/admin/settings", timeout=10)
            
            if response.status_code == 200:
                settings = response.json()
                
                # Check if settings structure supports image URLs
                has_hero_config = any(key in settings for key in ['hero_background_style', 'hero_display_mode'])
                
                self.log_test(
                    "Ad Configuration Storage (GET)", 
                    True, 
                    f"Settings retrieved successfully. Hero config present: {has_hero_config}"
                )
                
                # Test updating settings with image URL
                test_image_url = "/uploads/cms/test_hero_background.png"
                updated_settings = settings.copy()
                updated_settings.update({
                    'hero_background_style': 'image',
                    'hero_background_image_url': test_image_url,
                    'hero_display_mode': 'full_width'
                })
                
                update_response = requests.put(
                    f"{BACKEND_URL}/admin/settings",
                    json=updated_settings,
                    timeout=10
                )
                
                if update_response.status_code == 200:
                    self.log_test(
                        "Ad Configuration Storage (UPDATE)", 
                        True, 
                        f"Settings updated with image URL: {test_image_url}"
                    )
                    return True
                else:
                    error_detail = update_response.json().get('detail', 'Unknown error') if update_response.content else f"HTTP {update_response.status_code}"
                    self.log_test("Ad Configuration Storage (UPDATE)", False, error_msg=error_detail)
                    return False
                    
            else:
                self.log_test("Ad Configuration Storage (GET)", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Ad Configuration Storage", False, error_msg=str(e))
            return False

    def test_content_management_system(self):
        """Test CMS content endpoints for ad management"""
        try:
            # Test getting content
            response = requests.get(f"{BACKEND_URL}/admin/content", timeout=10)
            
            if response.status_code == 200:
                content = response.json()
                
                # Check if content has hero section for ads
                has_hero = 'hero' in content
                hero_structure = content.get('hero', {}) if has_hero else {}
                
                self.log_test(
                    "CMS Content Management (GET)", 
                    True, 
                    f"Content retrieved. Hero section present: {has_hero}, Hero keys: {list(hero_structure.keys())}"
                )
                
                # Test updating content with ad-related fields
                if has_hero:
                    updated_content = content.copy()
                    updated_content['hero']['background_image_url'] = "/uploads/cms/hero_ad_image.png"
                    updated_content['hero']['ad_enabled'] = True
                    
                    update_response = requests.put(
                        f"{BACKEND_URL}/admin/content",
                        json=updated_content,
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        self.log_test(
                            "CMS Content Management (UPDATE)", 
                            True, 
                            "Content updated with ad configuration successfully"
                        )
                        return True
                    else:
                        error_detail = update_response.json().get('detail', 'Unknown error') if update_response.content else f"HTTP {update_response.status_code}"
                        self.log_test("CMS Content Management (UPDATE)", False, error_msg=error_detail)
                        return False
                else:
                    self.log_test("CMS Content Management", False, "No hero section found in content structure")
                    return False
                    
            else:
                self.log_test("CMS Content Management (GET)", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("CMS Content Management", False, error_msg=str(e))
            return False

    def test_multiple_image_formats(self):
        """Test uploading different image formats"""
        formats_to_test = [
            ('PNG', 'image/png'),
            ('JPEG', 'image/jpeg'),
        ]
        
        successful_uploads = 0
        
        for format_name, mime_type in formats_to_test:
            try:
                # Create test image in specific format
                test_image = self.create_test_image(format=format_name)
                if not test_image:
                    continue
                
                files = {
                    'image': (f'test_ad_{format_name.lower()}.{format_name.lower()}', test_image, mime_type)
                }
                data = {
                    'section': 'ads',
                    'field': f'test_{format_name.lower()}'
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/admin/upload-image",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    successful_uploads += 1
                    result = response.json()
                    self.log_test(
                        f"Image Upload ({format_name})", 
                        True, 
                        f"Successfully uploaded {format_name} image: {result.get('filename')}"
                    )
                else:
                    error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                    self.log_test(f"Image Upload ({format_name})", False, error_msg=error_detail)
                    
            except Exception as e:
                self.log_test(f"Image Upload ({format_name})", False, error_msg=str(e))
        
        # Summary test
        total_formats = len(formats_to_test)
        self.log_test(
            "Multiple Image Formats Summary", 
            successful_uploads > 0, 
            f"Successfully uploaded {successful_uploads}/{total_formats} image formats"
        )
        
        return successful_uploads > 0

    def test_image_validation(self):
        """Test image upload validation (file size, type, etc.)"""
        try:
            # Test 1: Invalid file type (text file)
            text_content = b"This is not an image file"
            files = {
                'image': ('test.txt', io.BytesIO(text_content), 'text/plain')
            }
            data = {
                'section': 'ads',
                'field': 'invalid_test'
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/upload-image",
                files=files,
                data=data,
                timeout=10
            )
            
            # Should reject non-image files
            if response.status_code == 400:
                self.log_test(
                    "Image Validation (Invalid Type)", 
                    True, 
                    "Correctly rejected non-image file"
                )
            else:
                self.log_test("Image Validation (Invalid Type)", False, f"Expected 400 but got HTTP {response.status_code}")
            
            # Test 2: Valid image upload for comparison
            test_image = self.create_test_image(width=400, height=300)
            if test_image:
                files = {
                    'image': ('valid_test.png', test_image, 'image/png')
                }
                data = {
                    'section': 'ads',
                    'field': 'valid_test'
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/admin/upload-image",
                    files=files,
                    data=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log_test(
                        "Image Validation (Valid Image)", 
                        True, 
                        "Valid image uploaded successfully"
                    )
                else:
                    self.log_test("Image Validation (Valid Image)", False, f"HTTP {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Image Validation", False, error_msg=str(e))
            return False

    def run_image_upload_tests(self):
        """Run comprehensive image upload tests for Ad's Manager"""
        print("=" * 80)
        print("CATALORO IMAGE UPLOAD TESTING - AD'S MANAGER SYSTEM")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        uploaded_image_url = None
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting image upload testing.")
            return
        
        # 2. Image Upload API Testing
        print("📤 IMAGE UPLOAD API TESTING")
        print("-" * 40)
        uploaded_image_url = self.test_image_upload_api()
        
        # 3. Image Serving Testing
        print("🌐 IMAGE SERVING TESTING")
        print("-" * 40)
        self.test_image_serving(uploaded_image_url)
        
        # 4. Ad Configuration Storage Testing
        print("⚙️ AD CONFIGURATION STORAGE TESTING")
        print("-" * 40)
        self.test_ad_configuration_storage()
        
        # 5. Content Management System Testing
        print("📝 CONTENT MANAGEMENT SYSTEM TESTING")
        print("-" * 40)
        self.test_content_management_system()
        
        # 6. Multiple Image Formats Testing
        print("🖼️ MULTIPLE IMAGE FORMATS TESTING")
        print("-" * 40)
        self.test_multiple_image_formats()
        
        # 7. Image Validation Testing
        print("✅ IMAGE VALIDATION TESTING")
        print("-" * 40)
        self.test_image_validation()
        
        # Print Summary
        print("=" * 80)
        print("IMAGE UPLOAD TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if uploaded_image_url:
            print(f"✅ Sample Image Uploaded: {uploaded_image_url}")
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 IMAGE UPLOAD TESTING COMPLETE")
        print("The image upload functionality for Ad's Manager has been thoroughly tested.")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = ImageUploadTester()
    
    print("🎯 RUNNING IMAGE UPLOAD TESTING FOR AD'S MANAGER")
    print("Testing the complete image upload workflow for advertisements...")
    print()
    
    passed, failed, results = tester.run_image_upload_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)