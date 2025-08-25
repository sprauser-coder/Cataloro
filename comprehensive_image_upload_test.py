#!/usr/bin/env python3
"""
Comprehensive Backend Testing Script for Listing Image Upload Functionality
Focus: Testing POST /api/listings/upload-image endpoint with detailed verification
"""

import requests
import json
import os
import io
from PIL import Image
import tempfile

# Configuration
BACKEND_URL = "https://cataloro-profile-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ComprehensiveImageUploadTester:
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
                self.log_result("Admin Authentication", False, f"Failed to authenticate: {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False

    def create_test_png_image(self, size=(100, 100), color=(255, 0, 0)):
        """Create a test PNG image in memory"""
        img = Image.new('RGB', size, color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes

    def create_large_png_image(self):
        """Create a large PNG image (>10MB)"""
        # Create a 2000x2000 image which should be >10MB
        img = Image.new('RGB', (2000, 2000), (128, 128, 128))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes

    def test_get_listings_endpoint(self):
        """Test GET /api/listings endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings")
            
            if response.status_code == 200:
                listings = response.json()
                self.log_result("GET /api/listings", True, f"Successfully retrieved {len(listings)} listings", {
                    "total_listings": len(listings),
                    "response_type": type(listings).__name__
                })
                return True
            else:
                self.log_result("GET /api/listings", False, f"Failed to get listings: {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("GET /api/listings", False, f"Error getting listings: {str(e)}")
            return False

    def test_upload_png_image(self):
        """Test uploading a PNG image"""
        try:
            # Create test PNG image
            png_image = self.create_test_png_image()
            file_size = len(png_image.getvalue())
            
            files = {
                'file': ('test_image.png', png_image, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("image_url")
                self.log_result("Upload PNG Image", True, "Successfully uploaded PNG image", {
                    "image_url": image_url,
                    "message": data.get("message"),
                    "file_size": f"{file_size} bytes",
                    "expected_format": "PNG"
                })
                return image_url
            else:
                self.log_result("Upload PNG Image", False, f"Failed to upload PNG: {response.status_code}", {
                    "response": response.text,
                    "file_size": f"{file_size} bytes"
                })
                return None
                
        except Exception as e:
            self.log_result("Upload PNG Image", False, f"Error uploading PNG: {str(e)}")
            return None

    def test_file_validation_png_only(self):
        """Test that only PNG files are accepted (as per review request)"""
        try:
            # Test GIF rejection
            gif_image = Image.new('RGB', (50, 50), (0, 0, 255))
            gif_bytes = io.BytesIO()
            gif_image.save(gif_bytes, format='GIF')
            gif_bytes.seek(0)
            
            files = {
                'file': ('test_image.gif', gif_bytes, 'image/gif')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            if response.status_code == 400:
                self.log_result("File Validation - Reject GIF", True, "Correctly rejected GIF file", {
                    "status_code": response.status_code,
                    "response": response.json()
                })
                return True
            else:
                self.log_result("File Validation - Reject GIF", False, f"Should have rejected GIF but got: {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("File Validation - Reject GIF", False, f"Error testing GIF rejection: {str(e)}")
            return False

    def test_file_size_validation(self):
        """Test file size validation (10MB limit)"""
        try:
            # Create large image
            large_image = self.create_large_png_image()
            file_size = len(large_image.getvalue())
            
            files = {
                'file': ('large_image.png', large_image, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            # Should reject if >10MB
            if file_size > 10 * 1024 * 1024:
                if response.status_code == 400 or response.status_code == 413:
                    self.log_result("File Size Validation", True, "Correctly rejected large file", {
                        "status_code": response.status_code,
                        "file_size": f"{file_size} bytes ({file_size/(1024*1024):.1f}MB)",
                        "limit": "10MB"
                    })
                    return True
                else:
                    self.log_result("File Size Validation", False, f"Should have rejected large file but got: {response.status_code}", {
                        "file_size": f"{file_size} bytes ({file_size/(1024*1024):.1f}MB)",
                        "response": response.text
                    })
                    return False
            else:
                # File is within limits, should succeed
                if response.status_code == 200:
                    self.log_result("File Size Validation", True, "File within limits accepted", {
                        "file_size": f"{file_size} bytes ({file_size/(1024*1024):.1f}MB)",
                        "limit": "10MB"
                    })
                    return True
                else:
                    self.log_result("File Size Validation", False, f"File within limits should be accepted: {response.status_code}", {
                        "file_size": f"{file_size} bytes ({file_size/(1024*1024):.1f}MB)",
                        "response": response.text
                    })
                    return False
                
        except Exception as e:
            self.log_result("File Size Validation", False, f"Error testing file size: {str(e)}")
            return False

    def test_image_saved_to_disk(self, image_url):
        """Test that images are properly saved to disk"""
        if not image_url:
            self.log_result("Image Saved to Disk", False, "No image URL provided")
            return False
            
        try:
            # Extract filename from URL
            filename = image_url.split('/')[-1]
            file_path = f"/app/backend/uploads/{filename}"
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.log_result("Image Saved to Disk", True, "Image file exists on disk", {
                    "file_path": file_path,
                    "file_size": f"{file_size} bytes",
                    "filename": filename
                })
                return True
            else:
                self.log_result("Image Saved to Disk", False, "Image file not found on disk", {
                    "expected_path": file_path,
                    "filename": filename
                })
                return False
                
        except Exception as e:
            self.log_result("Image Saved to Disk", False, f"Error checking disk file: {str(e)}")
            return False

    def test_image_url_returned_correctly(self, image_url):
        """Test that correct image URL is returned"""
        if not image_url:
            self.log_result("Image URL Format", False, "No image URL provided")
            return False
            
        try:
            # Check URL format
            if image_url.startswith('/uploads/') and (image_url.endswith('.png') or image_url.endswith('.jpg')):
                self.log_result("Image URL Format", True, "Image URL format is correct", {
                    "url": image_url,
                    "format": "Valid /uploads/ path with proper extension"
                })
                return True
            else:
                self.log_result("Image URL Format", False, "Image URL format is incorrect", {
                    "url": image_url,
                    "expected_format": "/uploads/filename.png or .jpg"
                })
                return False
                
        except Exception as e:
            self.log_result("Image URL Format", False, f"Error checking URL format: {str(e)}")
            return False

    def test_image_accessible_via_http(self, image_url):
        """Test that uploaded images are accessible via HTTP"""
        if not image_url:
            self.log_result("Image HTTP Accessibility", False, "No image URL provided")
            return False
            
        try:
            # Test API endpoint access
            api_url = f"{BACKEND_URL}{image_url}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                # Check if it's actually an image
                is_image = content_type.startswith('image/') or response.content.startswith(b'\x89PNG') or response.content.startswith(b'\xff\xd8\xff')
                
                self.log_result("Image HTTP Accessibility", True, "Image is accessible via HTTP API", {
                    "api_url": api_url,
                    "status_code": response.status_code,
                    "content_type": content_type,
                    "content_length": content_length,
                    "is_image_content": is_image
                })
                return True
            else:
                self.log_result("Image HTTP Accessibility", False, f"Image not accessible via API: {response.status_code}", {
                    "api_url": api_url,
                    "response": response.text[:200]
                })
                return False
                
        except Exception as e:
            self.log_result("Image HTTP Accessibility", False, f"Error accessing image via HTTP: {str(e)}")
            return False

    def test_authentication_required(self):
        """Test that authentication is required for upload"""
        try:
            # Remove auth header temporarily
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Try to upload without auth
            png_image = self.create_test_png_image()
            files = {
                'file': ('test_image.png', png_image, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            # Restore auth header
            self.session.headers.update(original_headers)
            
            if response.status_code in [401, 403]:
                self.log_result("Authentication Required", True, "Correctly requires authentication", {
                    "status_code": response.status_code,
                    "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                })
                return True
            else:
                self.log_result("Authentication Required", False, f"Should require authentication but got: {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Authentication Required", False, f"Error testing authentication: {str(e)}")
            return False

    def run_comprehensive_tests(self):
        """Run comprehensive listing image upload tests"""
        print("=" * 80)
        print("COMPREHENSIVE LISTING IMAGE UPLOAD FUNCTIONALITY TESTING")
        print("Focus: PNG file upload, validation, storage, and accessibility")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return
        
        # Step 2: Test GET /api/listings endpoint (baseline)
        self.test_get_listings_endpoint()
        
        # Step 3: Test PNG image upload (main functionality)
        png_image_url = self.test_upload_png_image()
        
        # Step 4: Test file validation (PNG files specifically)
        self.test_file_validation_png_only()
        
        # Step 5: Test file size validation
        self.test_file_size_validation()
        
        # Step 6: Test authentication requirement
        self.test_authentication_required()
        
        # Step 7: Verify image storage and accessibility (if upload succeeded)
        if png_image_url:
            self.test_image_saved_to_disk(png_image_url)
            self.test_image_url_returned_correctly(png_image_url)
            self.test_image_accessible_via_http(png_image_url)
        
        # Summary
        print("=" * 80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Critical functionality assessment
        critical_tests = [
            "Upload PNG Image",
            "File Validation - Reject GIF", 
            "Image Saved to Disk",
            "Image URL Format",
            "Image HTTP Accessibility",
            "Authentication Required"
        ]
        
        critical_passed = 0
        for result in self.test_results:
            if result["test"] in critical_tests and "✅ PASS" in result["status"]:
                critical_passed += 1
        
        print(f"Critical Tests Passed: {critical_passed}/{len(critical_tests)}")
        print(f"Critical Success Rate: {(critical_passed/len(critical_tests))*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print()
        
        # Final assessment
        if critical_passed == len(critical_tests):
            print("🎉 LISTING IMAGE UPLOAD FUNCTIONALITY IS WORKING CORRECTLY!")
            print("✅ PNG files can be uploaded")
            print("✅ File validation works correctly")
            print("✅ Images are saved to disk properly")
            print("✅ Image URLs are returned correctly")
            print("✅ Uploaded images are accessible via HTTP")
            print("✅ Authentication is properly enforced")
        else:
            print("⚠️  SOME CRITICAL ISSUES FOUND IN IMAGE UPLOAD FUNCTIONALITY")
        
        print("=" * 80)
        
        return passed_tests, failed_tests, critical_passed

if __name__ == "__main__":
    tester = ComprehensiveImageUploadTester()
    passed, failed, critical_passed = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)