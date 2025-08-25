#!/usr/bin/env python3
"""
Backend Testing Script for Listing Image Upload Functionality
Focus: Testing POST /api/listings/upload-image endpoint
"""

import requests
import json
import os
import io
from PIL import Image
import tempfile

# Configuration
BACKEND_URL = "https://revived-cataloro.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ListingImageUploadTester:
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

    def create_test_jpeg_image(self, size=(100, 100), color=(0, 255, 0)):
        """Create a test JPEG image in memory"""
        img = Image.new('RGB', size, color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes

    def create_test_gif_image(self, size=(100, 100), color=(0, 0, 255)):
        """Create a test GIF image in memory (for negative testing)"""
        img = Image.new('RGB', size, color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='GIF')
        img_bytes.seek(0)
        return img_bytes

    def create_large_image(self, size_mb=11):
        """Create a large image for size limit testing"""
        # Create a large image (approximately size_mb MB)
        width = int((size_mb * 1024 * 1024 / 3) ** 0.5)  # Rough calculation for RGB
        height = width
        img = Image.new('RGB', (width, height), (128, 128, 128))
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
                    "file_size": f"{len(png_image.getvalue())} bytes"
                })
                return image_url
            else:
                self.log_result("Upload PNG Image", False, f"Failed to upload PNG: {response.status_code}", {
                    "response": response.text
                })
                return None
                
        except Exception as e:
            self.log_result("Upload PNG Image", False, f"Error uploading PNG: {str(e)}")
            return None

    def test_upload_jpeg_image(self):
        """Test uploading a JPEG image"""
        try:
            # Create test JPEG image
            jpeg_image = self.create_test_jpeg_image()
            
            files = {
                'file': ('test_image.jpg', jpeg_image, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("image_url")
                self.log_result("Upload JPEG Image", True, "Successfully uploaded JPEG image", {
                    "image_url": image_url,
                    "message": data.get("message"),
                    "file_size": f"{len(jpeg_image.getvalue())} bytes"
                })
                return image_url
            else:
                self.log_result("Upload JPEG Image", False, f"Failed to upload JPEG: {response.status_code}", {
                    "response": response.text
                })
                return None
                
        except Exception as e:
            self.log_result("Upload JPEG Image", False, f"Error uploading JPEG: {str(e)}")
            return None

    def test_upload_invalid_format(self):
        """Test uploading an invalid file format (GIF)"""
        try:
            # Create test GIF image
            gif_image = self.create_test_gif_image()
            
            files = {
                'file': ('test_image.gif', gif_image, 'image/gif')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            if response.status_code == 400:
                self.log_result("Upload Invalid Format (GIF)", True, "Correctly rejected GIF file", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return True
            else:
                self.log_result("Upload Invalid Format (GIF)", False, f"Should have rejected GIF but got: {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Upload Invalid Format (GIF)", False, f"Error testing invalid format: {str(e)}")
            return False

    def test_upload_large_file(self):
        """Test uploading a file that exceeds size limit"""
        try:
            # Create large image (>10MB)
            large_image = self.create_large_image(11)  # 11MB
            
            files = {
                'file': ('large_image.png', large_image, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            if response.status_code == 400 or response.status_code == 413:
                self.log_result("Upload Large File (>10MB)", True, "Correctly rejected large file", {
                    "status_code": response.status_code,
                    "file_size": f"{len(large_image.getvalue())} bytes (~{len(large_image.getvalue())/(1024*1024):.1f}MB)",
                    "response": response.text
                })
                return True
            else:
                self.log_result("Upload Large File (>10MB)", False, f"Should have rejected large file but got: {response.status_code}", {
                    "file_size": f"{len(large_image.getvalue())} bytes",
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Upload Large File (>10MB)", False, f"Error testing large file: {str(e)}")
            return False

    def test_upload_without_auth(self):
        """Test uploading without authentication"""
        try:
            # Temporarily remove auth header
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Create test PNG image
            png_image = self.create_test_png_image()
            
            files = {
                'file': ('test_image.png', png_image, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            # Restore auth header
            self.session.headers.update(original_headers)
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("Upload Without Auth", True, "Correctly rejected unauthenticated request", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return True
            else:
                self.log_result("Upload Without Auth", False, f"Should have rejected unauthenticated request but got: {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Upload Without Auth", False, f"Error testing without auth: {str(e)}")
            return False

    def test_image_accessibility(self, image_url):
        """Test if uploaded image is accessible via HTTP"""
        if not image_url:
            self.log_result("Image Accessibility", False, "No image URL provided")
            return False
            
        try:
            # Construct full URL
            if image_url.startswith('/uploads/'):
                full_url = f"https://revived-cataloro.preview.emergentagent.com{image_url}"
            else:
                full_url = image_url
            
            response = requests.get(full_url)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                self.log_result("Image Accessibility", True, "Image is accessible via HTTP", {
                    "url": full_url,
                    "content_type": content_type,
                    "content_length": len(response.content),
                    "status_code": response.status_code
                })
                return True
            else:
                self.log_result("Image Accessibility", False, f"Image not accessible: {response.status_code}", {
                    "url": full_url,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Image Accessibility", False, f"Error accessing image: {str(e)}")
            return False

    def test_create_listing_with_image(self, image_url):
        """Test creating a listing with uploaded image"""
        if not image_url:
            self.log_result("Create Listing with Image", False, "No image URL provided")
            return False
            
        try:
            listing_data = {
                "title": "Test Listing with Image",
                "description": "This is a test listing created with an uploaded image",
                "category": "Electronics",
                "images": [image_url],
                "listing_type": "fixed_price",
                "price": 99.99,
                "condition": "New",
                "quantity": 1,
                "location": "Test City"
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings", json=listing_data)
            
            if response.status_code == 200:
                data = response.json()
                listing_id = data.get("id")
                self.log_result("Create Listing with Image", True, "Successfully created listing with image", {
                    "listing_id": listing_id,
                    "title": data.get("title"),
                    "images": data.get("images"),
                    "image_count": len(data.get("images", []))
                })
                return listing_id
            else:
                self.log_result("Create Listing with Image", False, f"Failed to create listing: {response.status_code}", {
                    "response": response.text
                })
                return None
                
        except Exception as e:
            self.log_result("Create Listing with Image", False, f"Error creating listing: {str(e)}")
            return None

    def run_all_tests(self):
        """Run all listing image upload tests"""
        print("=" * 80)
        print("LISTING IMAGE UPLOAD FUNCTIONALITY TESTING")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return
        
        # Step 2: Test GET /api/listings endpoint
        self.test_get_listings_endpoint()
        
        # Step 3: Test image upload functionality
        png_image_url = self.test_upload_png_image()
        jpeg_image_url = self.test_upload_jpeg_image()
        
        # Step 4: Test validation
        self.test_upload_invalid_format()
        self.test_upload_large_file()
        self.test_upload_without_auth()
        
        # Step 5: Test image accessibility
        if png_image_url:
            self.test_image_accessibility(png_image_url)
        
        # Step 6: Test listing creation with image
        if png_image_url:
            self.test_create_listing_with_image(png_image_url)
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print()
        print("=" * 80)
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = ListingImageUploadTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)