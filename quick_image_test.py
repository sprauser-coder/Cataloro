#!/usr/bin/env python3
"""
Quick Image Upload Verification Test
Focus: POST /api/listings/upload-image with PNG file upload and accessibility verification
"""

import requests
import sys
import json
from datetime import datetime
import io
from PIL import Image

class QuickImageTester:
    def __init__(self):
        self.base_url = "http://217.154.0.82"
        self.api_url = f"{self.base_url}/api"
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_images = []

    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "email": "admin@marketplace.com",
                "password": "admin123"
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log_test("Admin Authentication", True, "Successfully authenticated as admin@marketplace.com")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def create_test_png_image(self):
        """Create a test PNG image in memory"""
        try:
            # Create a simple 100x100 PNG image
            img = Image.new('RGB', (100, 100), color='red')
            
            # Save to bytes buffer
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception as e:
            self.log_test("PNG Image Creation", False, f"Failed to create test PNG: {str(e)}")
            return None
    
    def test_image_upload(self):
        """Test PNG image upload to /api/listings/upload-image"""
        try:
            # Create test PNG image
            png_data = self.create_test_png_image()
            if not png_data:
                return False
            
            # Prepare file upload
            files = {
                'file': ('test_image.png', png_data, 'image/png')
            }
            
            headers = {
                'Authorization': f'Bearer {self.admin_token}'
            }
            
            response = requests.post(f"{self.api_url}/listings/upload-image", files=files, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("image_url")
                
                if image_url:
                    self.uploaded_images.append(image_url)
                    self.log_test("PNG Image Upload", True, f"Image uploaded successfully: {image_url}")
                    return image_url
                else:
                    self.log_test("PNG Image Upload", False, "No image_url in response", data)
                    return False
            else:
                self.log_test("PNG Image Upload", False, f"Upload failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("PNG Image Upload", False, f"Upload error: {str(e)}")
            return False
    
    def test_image_accessibility(self, image_url):
        """Test if uploaded image is accessible via API endpoint"""
        try:
            if not image_url:
                self.log_test("Image Accessibility", False, "No image URL provided")
                return False
            
            # Extract filename from URL
            if image_url.startswith('/uploads/'):
                filename = image_url.replace('/uploads/', '')
                full_url = f"{self.api_url}/uploads/{filename}"
            else:
                full_url = f"{self.base_url}{image_url}"
            
            response = requests.get(full_url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                if 'image/png' in content_type and content_length > 0:
                    self.log_test("Image Accessibility", True, f"Image accessible at {full_url} (Content-Type: {content_type}, Size: {content_length} bytes)")
                    return True
                else:
                    self.log_test("Image Accessibility", False, f"Invalid image response - Content-Type: {content_type}, Size: {content_length}")
                    return False
            else:
                self.log_test("Image Accessibility", False, f"Image not accessible - Status: {response.status_code}", full_url)
                return False
                
        except Exception as e:
            self.log_test("Image Accessibility", False, f"Accessibility test error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all image upload verification tests"""
        print("=" * 80)
        print("QUICK IMAGE UPLOAD VERIFICATION TEST")
        print("=" * 80)
        print(f"Backend URL: {self.api_url}")
        print(f"Admin Credentials: admin@marketplace.com")
        print("-" * 80)
        
        # Test 1: Admin Authentication
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Test 2: PNG Image Upload
        image_url = self.test_image_upload()
        
        # Test 3: Image Accessibility
        if image_url:
            self.test_image_accessibility(image_url)
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = self.tests_passed
        total = self.tests_run
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - Image upload functionality is working correctly!")
            return True
        else:
            print("⚠️  SOME TESTS FAILED - Image upload functionality needs attention")
            return False

def main():
    """Main test execution"""
    tester = QuickImageTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()