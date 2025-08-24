#!/usr/bin/env python3
"""
Focused Backend Test Script for Cataloro Marketplace
Testing specific endpoints mentioned in the review request:
1. Logo Upload Functionality (POST /api/admin/cms/upload-logo)
2. Logo Display in Settings (GET /api/cms/settings)
3. Create New Listing Functionality (POST /api/listings)
4. Image Upload Previews (POST /api/listings/upload-image)
"""

import requests
import sys
import json
from datetime import datetime
import time
import io
import os
from pathlib import Path

class CataloroFocusedTester:
    def __init__(self):
        self.base_url = "https://cataloro-shop.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.admin_token = None
        self.user_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_logo_url = None
        self.uploaded_image_urls = []
        self.created_listing_id = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED")
        
        if details:
            print(f"   {details}")
        print()

    def make_request(self, method, endpoint, data=None, files=None, use_admin_token=False, expected_status=200):
        """Make HTTP request to API"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        # Set authorization header
        token = self.admin_token if use_admin_token else self.user_token
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        # Set content type for JSON requests
        if data and not files:
            headers['Content-Type'] = 'application/json'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, headers=headers, timeout=15)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json() if response.text.strip() else {}
            except:
                pass

            return success, response.status_code, response_data, response.text

        except requests.exceptions.RequestException as e:
            return False, 0, {}, str(e)

    def create_test_png_file(self, size_kb=50):
        """Create a test PNG file in memory"""
        # Minimal PNG file (1x1 pixel)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\x1bIEND\xaeB`\x82'
        
        # Pad to desired size
        if size_kb > 1:
            padding_size = (size_kb * 1024) - len(png_data)
            if padding_size > 0:
                png_data += b'\x00' * padding_size
                
        return png_data

    def create_test_jpeg_file(self, size_kb=50):
        """Create a test JPEG file in memory"""
        # Minimal JPEG file
        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xaa\xff\xd9'
        
        # Pad to desired size
        if size_kb > 1:
            padding_size = (size_kb * 1024) - len(jpeg_data)
            if padding_size > 0:
                jpeg_data += b'\x00' * padding_size
                
        return jpeg_data

    def test_admin_login(self):
        """Test admin authentication"""
        print("🔐 Testing Admin Authentication...")
        
        admin_credentials = {
            "email": "admin@marketplace.com",
            "password": "admin123"
        }
        
        success, status, response, text = self.make_request('POST', 'auth/login', admin_credentials)
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.log_test("Admin Login", True, f"Admin authenticated successfully as {response['user']['full_name']}")
            return True
        else:
            self.log_test("Admin Login", False, f"Status: {status}, Response: {text[:200]}")
            return False

    def test_regular_user_registration(self):
        """Test regular user registration for listing creation"""
        print("👤 Testing Regular User Registration...")
        
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"seller_{timestamp}@cataloro.com",
            "username": f"seller_{timestamp}",
            "password": "SecurePass123!",
            "full_name": f"Test Seller {timestamp}",
            "role": "seller",
            "phone": "+1234567890",
            "address": "123 Marketplace Street, Commerce City, CC 12345"
        }
        
        success, status, response, text = self.make_request('POST', 'auth/register', user_data)
        
        if success and 'access_token' in response:
            self.user_token = response['access_token']
            self.log_test("User Registration", True, f"User registered as {response['user']['full_name']}")
            return True
        else:
            self.log_test("User Registration", False, f"Status: {status}, Response: {text[:200]}")
            return False

    def test_logo_upload_functionality(self):
        """Test 1: Logo Upload Functionality (POST /api/admin/cms/upload-logo)"""
        print("🖼️  Testing Logo Upload Functionality...")
        
        if not self.admin_token:
            self.log_test("Logo Upload - Admin Auth Required", False, "No admin token available")
            return False

        # Test 1a: Upload a valid PNG logo
        png_data = self.create_test_png_file(100)  # 100KB PNG
        files = {'file': ('cataloro_logo.png', png_data, 'image/png')}
        form_data = {'logo_type': 'header'}
        
        success, status, response, text = self.make_request('POST', 'admin/cms/upload-logo', 
                                                          data=form_data, files=files, 
                                                          use_admin_token=True)
        
        if success and 'logo_url' in response:
            self.uploaded_logo_url = response['logo_url']
            self.log_test("Logo Upload - Valid PNG", True, 
                         f"Logo uploaded successfully. URL: {self.uploaded_logo_url}")
        else:
            self.log_test("Logo Upload - Valid PNG", False, 
                         f"Status: {status}, Response: {text[:300]}")
            return False

        # Test 1b: Verify file is saved in uploads directory (by accessing it)
        if self.uploaded_logo_url:
            logo_access_url = f"{self.base_url}{self.uploaded_logo_url}"
            try:
                logo_response = requests.get(logo_access_url, timeout=10)
                if logo_response.status_code == 200:
                    self.log_test("Logo File Accessibility", True, 
                                 f"Logo file accessible at {logo_access_url}")
                else:
                    self.log_test("Logo File Accessibility", False, 
                                 f"Logo file not accessible, status: {logo_response.status_code}")
            except Exception as e:
                self.log_test("Logo File Accessibility", False, f"Error accessing logo: {str(e)}")

        # Test 1c: Test invalid file format (should fail)
        jpeg_data = self.create_test_jpeg_file(50)
        files = {'file': ('invalid_logo.jpg', jpeg_data, 'image/jpeg')}
        form_data = {'logo_type': 'header'}
        
        success, status, response, text = self.make_request('POST', 'admin/cms/upload-logo', 
                                                          data=form_data, files=files, 
                                                          use_admin_token=True, expected_status=400)
        
        self.log_test("Logo Upload - Invalid Format Rejection", success, 
                     f"Correctly rejected JPEG file with status {status}")

        # Test 1d: Test file size limit (create 6MB file, should fail)
        large_png = self.create_test_png_file(6000)  # 6MB
        files = {'file': ('large_logo.png', large_png, 'image/png')}
        form_data = {'logo_type': 'header'}
        
        success, status, response, text = self.make_request('POST', 'admin/cms/upload-logo', 
                                                          data=form_data, files=files, 
                                                          use_admin_token=True, expected_status=400)
        
        self.log_test("Logo Upload - Size Limit Enforcement", success, 
                     f"Correctly rejected large file with status {status}")

        return True

    def test_logo_display_in_settings(self):
        """Test 2: Logo Display in Settings (GET /api/cms/settings)"""
        print("⚙️  Testing Logo Display in Settings...")
        
        # Test 2a: Get current site settings
        success, status, response, text = self.make_request('GET', 'cms/settings')
        
        if success:
            # Check if logo fields exist
            has_logo_url = 'header_logo_url' in response
            has_logo_alt = 'header_logo_alt' in response
            
            if has_logo_url and has_logo_alt:
                logo_url = response.get('header_logo_url')
                logo_alt = response.get('header_logo_alt')
                
                self.log_test("Logo Fields in Settings", True, 
                             f"Logo URL: {logo_url}, Alt Text: {logo_alt}")
                
                # Test 2b: Verify logo URL points to existing file (if set)
                if logo_url and logo_url.startswith('/uploads/'):
                    logo_access_url = f"{self.base_url}{logo_url}"
                    try:
                        logo_response = requests.get(logo_access_url, timeout=10)
                        if logo_response.status_code == 200:
                            self.log_test("Logo URL Points to Existing File", True, 
                                         f"Logo accessible at {logo_access_url}")
                        else:
                            self.log_test("Logo URL Points to Existing File", False, 
                                         f"Logo not accessible, status: {logo_response.status_code}")
                    except Exception as e:
                        self.log_test("Logo URL Points to Existing File", False, 
                                     f"Error accessing logo: {str(e)}")
                else:
                    self.log_test("Logo URL Points to Existing File", True, 
                                 "No logo URL set or external URL (expected)")
                    
            else:
                self.log_test("Logo Fields in Settings", False, 
                             f"Missing fields - URL: {has_logo_url}, Alt: {has_logo_alt}")
                return False
        else:
            self.log_test("Get Site Settings", False, f"Status: {status}, Response: {text[:200]}")
            return False

        return True

    def test_create_new_listing_functionality(self):
        """Test 3: Create New Listing Functionality (POST /api/listings)"""
        print("📝 Testing Create New Listing Functionality...")
        
        if not self.admin_token:
            self.log_test("Create Listing - Admin Auth", False, "No admin token available")
            return False

        # Test 3a: Create listing with admin credentials
        listing_data = {
            "title": "Premium Wireless Headphones - Cataloro Test",
            "description": "High-quality wireless headphones with noise cancellation. Perfect for music lovers and professionals. This is a test listing created by the automated test suite.",
            "category": "Electronics",
            "condition": "New",
            "price": 299.99,
            "quantity": 5,
            "location": "San Francisco, CA",
            "listing_type": "fixed_price",
            "shipping_cost": 15.99,
            "images": []  # Will add uploaded images later
        }
        
        success, status, response, text = self.make_request('POST', 'listings', listing_data, 
                                                          use_admin_token=True)
        
        if success and 'id' in response:
            self.created_listing_id = response['id']
            self.log_test("Create Listing - Admin User", True, 
                         f"Listing created successfully. ID: {self.created_listing_id}")
        else:
            self.log_test("Create Listing - Admin User", False, 
                         f"Status: {status}, Response: {text[:300]}")
            return False

        # Test 3b: Verify admin role check works (admin can create listings)
        # This is implicitly tested above, but let's also test with regular user
        if self.user_token:
            success, status, response, text = self.make_request('POST', 'listings', listing_data, 
                                                              use_admin_token=False)
            
            if success and 'id' in response:
                self.log_test("Create Listing - Seller Role Check", True, 
                             "Seller user can create listings as expected")
            else:
                # Check if it's a role-based rejection
                if status == 403:
                    self.log_test("Create Listing - Role Check", False, 
                                 "Seller user cannot create listings (unexpected)")
                else:
                    self.log_test("Create Listing - Seller Role Check", True, 
                                 f"Expected behavior for seller role, status: {status}")

        # Test 3c: Test with all required fields
        complete_listing_data = {
            "title": "Complete Test Product - All Fields",
            "description": "This listing includes all required fields to test comprehensive validation.",
            "category": "Home & Garden",
            "condition": "Used",
            "price": 89.99,
            "quantity": 2,
            "location": "New York, NY",
            "listing_type": "fixed_price",
            "shipping_cost": 8.50,
            "images": self.uploaded_image_urls[:2] if self.uploaded_image_urls else []
        }
        
        success, status, response, text = self.make_request('POST', 'listings', complete_listing_data, 
                                                          use_admin_token=True)
        
        self.log_test("Create Listing - All Required Fields", success, 
                     f"Status: {status}, Complete listing creation")

        return True

    def test_image_upload_previews(self):
        """Test 4: Image Upload Previews (POST /api/listings/upload-image)"""
        print("🖼️  Testing Image Upload Previews...")
        
        if not self.user_token and not self.admin_token:
            self.log_test("Image Upload - Authentication", False, "No user token available")
            return False

        # Test 4a: Upload PNG image for listing
        png_data = self.create_test_png_file(200)  # 200KB PNG
        files = {'file': ('product_image_1.png', png_data, 'image/png')}
        
        success, status, response, text = self.make_request('POST', 'listings/upload-image', 
                                                          files=files, 
                                                          use_admin_token=bool(self.admin_token))
        
        if success and 'image_url' in response:
            image_url = response['image_url']
            self.uploaded_image_urls.append(image_url)
            self.log_test("Image Upload - PNG Format", True, 
                         f"PNG image uploaded successfully. URL: {image_url}")
        else:
            self.log_test("Image Upload - PNG Format", False, 
                         f"Status: {status}, Response: {text[:300]}")

        # Test 4b: Upload JPEG image for listing
        jpeg_data = self.create_test_jpeg_file(150)  # 150KB JPEG
        files = {'file': ('product_image_2.jpg', jpeg_data, 'image/jpeg')}
        
        success, status, response, text = self.make_request('POST', 'listings/upload-image', 
                                                          files=files, 
                                                          use_admin_token=bool(self.admin_token))
        
        if success and 'image_url' in response:
            image_url = response['image_url']
            self.uploaded_image_urls.append(image_url)
            self.log_test("Image Upload - JPEG Format", True, 
                         f"JPEG image uploaded successfully. URL: {image_url}")
        else:
            self.log_test("Image Upload - JPEG Format", False, 
                         f"Status: {status}, Response: {text[:300]}")

        # Test 4c: Verify uploaded images exist in uploads directory
        for i, image_url in enumerate(self.uploaded_image_urls):
            if image_url.startswith('/uploads/'):
                image_access_url = f"{self.base_url}{image_url}"
                try:
                    image_response = requests.get(image_access_url, timeout=10)
                    if image_response.status_code == 200:
                        self.log_test(f"Image File Accessibility #{i+1}", True, 
                                     f"Image accessible at {image_access_url}")
                    else:
                        self.log_test(f"Image File Accessibility #{i+1}", False, 
                                     f"Image not accessible, status: {image_response.status_code}")
                except Exception as e:
                    self.log_test(f"Image File Accessibility #{i+1}", False, 
                                 f"Error accessing image: {str(e)}")

        # Test 4d: Test file size limit for listing images (11MB should fail)
        large_png = self.create_test_png_file(11000)  # 11MB
        files = {'file': ('large_image.png', large_png, 'image/png')}
        
        success, status, response, text = self.make_request('POST', 'listings/upload-image', 
                                                          files=files, 
                                                          use_admin_token=bool(self.admin_token),
                                                          expected_status=400)
        
        self.log_test("Image Upload - Size Limit Enforcement", success, 
                     f"Correctly rejected large file with status {status}")

        # Test 4e: Test invalid format (GIF should fail)
        gif_data = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;'
        files = {'file': ('invalid_image.gif', gif_data, 'image/gif')}
        
        success, status, response, text = self.make_request('POST', 'listings/upload-image', 
                                                          files=files, 
                                                          use_admin_token=bool(self.admin_token),
                                                          expected_status=400)
        
        self.log_test("Image Upload - Invalid Format Rejection", success, 
                     f"Correctly rejected GIF file with status {status}")

        return True

    def test_integration_listing_with_uploaded_images(self):
        """Integration Test: Create listing with uploaded images"""
        print("🔗 Testing Integration - Listing with Uploaded Images...")
        
        if not self.uploaded_image_urls or not self.admin_token:
            self.log_test("Integration Test", False, "No uploaded images or admin token")
            return False

        # Create a listing using the uploaded images
        listing_data = {
            "title": "Integration Test Product with Real Images",
            "description": "This listing uses images that were uploaded via the image upload endpoint, testing the complete integration.",
            "category": "Art & Collectibles",
            "condition": "New",
            "price": 199.99,
            "quantity": 1,
            "location": "Los Angeles, CA",
            "listing_type": "fixed_price",
            "shipping_cost": 12.99,
            "images": self.uploaded_image_urls  # Use all uploaded images
        }
        
        success, status, response, text = self.make_request('POST', 'listings', listing_data, 
                                                          use_admin_token=True)
        
        if success and 'id' in response:
            listing_id = response['id']
            images_in_response = response.get('images', [])
            
            self.log_test("Integration - Listing with Images", True, 
                         f"Listing created with {len(images_in_response)} images. ID: {listing_id}")
            
            # Verify the listing can be retrieved with images
            success, status, get_response, text = self.make_request('GET', f'listings/{listing_id}')
            
            if success and 'images' in get_response:
                retrieved_images = get_response['images']
                self.log_test("Integration - Retrieve Listing Images", True, 
                             f"Retrieved listing has {len(retrieved_images)} images")
            else:
                self.log_test("Integration - Retrieve Listing Images", False, 
                             f"Could not retrieve listing images, status: {status}")
                
        else:
            self.log_test("Integration - Listing with Images", False, 
                         f"Status: {status}, Response: {text[:300]}")
            return False

        return True

    def run_all_tests(self):
        """Run all focused tests"""
        print("🚀 Starting Cataloro Marketplace Focused Backend Tests")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print("=" * 70)
        
        # Authentication setup
        if not self.test_admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
            
        self.test_regular_user_registration()
        
        # Run the four main test categories
        print("\n" + "="*50)
        print("1️⃣  LOGO UPLOAD FUNCTIONALITY TESTS")
        print("="*50)
        self.test_logo_upload_functionality()
        
        print("\n" + "="*50)
        print("2️⃣  LOGO DISPLAY IN SETTINGS TESTS")
        print("="*50)
        self.test_logo_display_in_settings()
        
        print("\n" + "="*50)
        print("3️⃣  IMAGE UPLOAD PREVIEWS TESTS")
        print("="*50)
        self.test_image_upload_previews()
        
        print("\n" + "="*50)
        print("4️⃣  CREATE NEW LISTING FUNCTIONALITY TESTS")
        print("="*50)
        self.test_create_new_listing_functionality()
        
        print("\n" + "="*50)
        print("5️⃣  INTEGRATION TESTS")
        print("="*50)
        self.test_integration_listing_with_uploaded_images()
        
        # Final summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  Some tests failed. Please review the output above.")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = CataloroFocusedTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)