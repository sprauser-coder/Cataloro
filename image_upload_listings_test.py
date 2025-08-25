#!/usr/bin/env python3
"""
Backend Testing for Image Upload and Listings API Endpoints
Testing image upload functionality and listings API endpoints as requested.
"""

import requests
import json
import sys
from datetime import datetime
import os

# Configuration - Using the requested backend URL
BACKEND_URL = "https://cataloro-profile-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ImageUploadAndListingsTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.uploaded_image_url = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
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
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Token: {self.admin_token[:20]}...")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_jwt_token_functionality(self):
        """Test JWT token functionality with protected endpoints"""
        try:
            # Test with valid token
            response = self.session.get(f"{BACKEND_URL}/admin/stats")
            
            if response.status_code == 200:
                data = response.json()
                if "total_users" in data and "total_listings" in data:
                    self.log_test("JWT Token Functionality", True, 
                                f"Protected endpoint accessible. Stats: {data.get('total_users')} users, {data.get('total_listings')} listings")
                    return True
                else:
                    self.log_test("JWT Token Functionality", False, f"Unexpected response structure: {data}")
                    return False
            else:
                self.log_test("JWT Token Functionality", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("JWT Token Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_image_upload_png(self):
        """Test POST /api/listings/upload-image with PNG file"""
        try:
            # Create a small test PNG file (1x1 pixel)
            png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01IEND\xaeB`\x82'
            
            files = {
                'file': ('test_listing.png', png_content, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if "image_url" in data:
                    self.uploaded_image_url = data["image_url"]
                    self.log_test("PNG Image Upload", True, f"PNG uploaded successfully: {data['image_url']}")
                    return True
                else:
                    self.log_test("PNG Image Upload", False, f"Missing image_url in response: {data}")
                    return False
            else:
                self.log_test("PNG Image Upload", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PNG Image Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_image_upload_jpeg(self):
        """Test POST /api/listings/upload-image with JPEG file"""
        try:
            # Create a small test JPEG file (minimal JPEG header)
            jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
            
            files = {
                'file': ('test_listing.jpg', jpeg_content, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if "image_url" in data:
                    self.log_test("JPEG Image Upload", True, f"JPEG uploaded successfully: {data['image_url']}")
                    return True
                else:
                    self.log_test("JPEG Image Upload", False, f"Missing image_url in response: {data}")
                    return False
            else:
                self.log_test("JPEG Image Upload", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("JPEG Image Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_image_upload_invalid_file(self):
        """Test POST /api/listings/upload-image with invalid file type"""
        try:
            # Create a text file (invalid format)
            invalid_content = b'This is not an image file'
            
            files = {
                'file': ('test_file.txt', invalid_content, 'text/plain')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            if response.status_code == 400:
                self.log_test("Invalid File Upload Error Handling", True, "Correctly rejected invalid file type")
                return True
            else:
                self.log_test("Invalid File Upload Error Handling", False, 
                            f"Expected 400 error, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Invalid File Upload Error Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_image_accessibility(self):
        """Test if uploaded images are accessible via HTTP"""
        if not self.uploaded_image_url:
            self.log_test("Image Accessibility", False, "No uploaded image URL to test")
            return False
            
        try:
            # Test image accessibility
            image_response = requests.get(f"{BACKEND_URL.replace('/api', '')}{self.uploaded_image_url}")
            
            if image_response.status_code == 200:
                content_type = image_response.headers.get('content-type', '')
                if 'image' in content_type:
                    self.log_test("Image Accessibility", True, 
                                f"Image accessible at {self.uploaded_image_url}, Content-Type: {content_type}")
                    return True
                else:
                    self.log_test("Image Accessibility", False, 
                                f"Image accessible but wrong content-type: {content_type}")
                    return False
            else:
                self.log_test("Image Accessibility", False, 
                            f"Image not accessible: {image_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Image Accessibility", False, f"Exception: {str(e)}")
            return False
    
    def test_listings_endpoint(self):
        """Test GET /api/listings endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("GET /api/listings", True, 
                                f"Retrieved {len(data)} listings successfully")
                    return True
                else:
                    self.log_test("GET /api/listings", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("GET /api/listings", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/listings", False, f"Exception: {str(e)}")
            return False
    
    def test_listings_count_endpoint(self):
        """Test GET /api/listings/count endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings/count")
            
            if response.status_code == 200:
                data = response.json()
                if "total_count" in data and isinstance(data["total_count"], int):
                    self.log_test("GET /api/listings/count", True, 
                                f"Total count: {data['total_count']} listings")
                    return True
                else:
                    self.log_test("GET /api/listings/count", False, f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("GET /api/listings/count", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/listings/count", False, f"Exception: {str(e)}")
            return False
    
    def test_pagination_functionality(self):
        """Test pagination with limit and skip parameters"""
        try:
            # Test with limit=5
            response = self.session.get(f"{BACKEND_URL}/listings?limit=5&skip=0")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) <= 5:
                    self.log_test("Pagination Functionality", True, 
                                f"Pagination working: requested 5, got {len(data)} listings")
                    return True
                else:
                    self.log_test("Pagination Functionality", False, 
                                f"Pagination issue: requested 5, got {len(data)} listings")
                    return False
            else:
                self.log_test("Pagination Functionality", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Pagination Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_unauthenticated_image_upload(self):
        """Test image upload without authentication"""
        try:
            # Remove authorization header temporarily
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01IEND\xaeB`\x82'
            
            files = {
                'file': ('test_unauth.png', png_content, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            # Restore headers
            self.session.headers.update(original_headers)
            
            if response.status_code == 403 or response.status_code == 401:
                self.log_test("Unauthenticated Upload Protection", True, 
                            f"Correctly blocked unauthenticated upload: {response.status_code}")
                return True
            else:
                self.log_test("Unauthenticated Upload Protection", False, 
                            f"Should block unauthenticated upload, got: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unauthenticated Upload Protection", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all image upload and listings tests"""
        print("=" * 80)
        print("IMAGE UPLOAD AND LISTINGS API TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 TESTING IMAGE UPLOAD AND LISTINGS FUNCTIONALITY:")
        print("-" * 60)
        
        # Test all endpoints
        tests = [
            self.test_jwt_token_functionality,
            self.test_image_upload_png,
            self.test_image_upload_jpeg,
            self.test_image_upload_invalid_file,
            self.test_image_accessibility,
            self.test_unauthenticated_image_upload,
            self.test_listings_endpoint,
            self.test_listings_count_endpoint,
            self.test_pagination_functionality
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL IMAGE UPLOAD AND LISTINGS TESTS PASSED!")
            print("✅ Image upload functionality working correctly")
            print("✅ Listings API endpoints operational")
            print("✅ Authentication and security working properly")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            print("❌ Some functionality may not work correctly")
        
        return passed == total

def main():
    """Main test execution"""
    tester = ImageUploadAndListingsTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()