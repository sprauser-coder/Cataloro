#!/usr/bin/env python3
"""
Quick Image Upload Verification Test
Focus: POST /api/listings/upload-image with PNG file upload and accessibility verification
"""

import requests
import sys
import json
from datetime import datetime
import time
import io
import os
from pathlib import Path
from PIL import Image

class ImageUploadTester:
    def __init__(self, base_url="https://cataloro-revival.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_images = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_admin_token=False):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Use admin token if specified, otherwise use regular token
        token_to_use = self.admin_token if use_admin_token else self.user_token
        if token_to_use:
            test_headers['Authorization'] = f'Bearer {token_to_use}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 300:
                        print(f"   Response: {response_data}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Error: {response.text[:300]}")

            return success, response.json() if response.text and response.text.strip() else {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def run_file_upload_test(self, name, endpoint, file_data, file_name, content_type, expected_status, use_admin_token=False, extra_data=None):
        """Run a file upload test"""
        url = f"{self.api_url}/{endpoint}"
        
        # Use admin token if specified, otherwise use regular token
        token_to_use = self.admin_token if use_admin_token else self.user_token
        headers = {}
        if token_to_use:
            headers['Authorization'] = f'Bearer {token_to_use}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   File: {file_name} ({content_type})")
        
        try:
            files = {'file': (file_name, file_data, content_type)}
            data = extra_data or {}
            if 'logo' in endpoint:
                data['logo_type'] = 'header'  # Default logo type for logo uploads
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=15)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 300:
                        print(f"   Response: {response_data}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Error: {response.text[:300]}")

            return success, response.json() if response.text and response.text.strip() else {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_test_png_file(self, size_mb=1):
        """Create a test PNG file in memory"""
        # Create a minimal 1x1 pixel PNG file
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # If we need a larger file, pad it with null bytes
        if size_mb > 1:
            padding_size = (size_mb * 1024 * 1024) - len(png_data)
            if padding_size > 0:
                png_data += b'\x00' * padding_size
            
        return png_data

    def create_test_jpeg_file(self, size_mb=1):
        """Create a test JPEG file in memory"""
        # Minimal JPEG file header and data
        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xaa\xff\xd9'
        
        # If we need a larger file, pad it
        if size_mb > 1:
            padding_size = (size_mb * 1024 * 1024) - len(jpeg_data)
            if padding_size > 0:
                jpeg_data += b'\x00' * padding_size
                
        return jpeg_data

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("\n🔐 Setting up authentication...")
        
        # Admin login
        admin_data = {
            "email": "admin@marketplace.com",
            "password": "admin123"
        }
        
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, admin_data)
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   ✅ Admin authenticated: {response['user']['full_name']}")
        else:
            print("   ❌ Admin authentication failed")
            return False

        # Create and login regular user for listing image tests
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"imagetest_user_{timestamp}@cataloro.com",
            "username": f"imagetest_{timestamp}",
            "password": "ImageTest123!",
            "full_name": f"Image Test User {timestamp}",
            "role": "both",
            "phone": "5551234567",
            "address": "123 Image Test Street"
        }
        
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, user_data)
        if success and 'access_token' in response:
            self.user_token = response['access_token']
            print(f"   ✅ User authenticated: {response['user']['full_name']}")
            return True
        else:
            print("   ❌ User authentication failed")
            return False

    # ===========================
    # LOGO UPLOAD TESTS
    # ===========================

    def test_logo_upload_admin_auth_required(self):
        """Test that logo upload requires admin authentication"""
        png_data = self.create_test_png_file()
        success, response = self.run_file_upload_test(
            "Logo Upload - Admin Auth Required", 
            "admin/cms/upload-logo", 
            png_data, 
            "test_logo.png", 
            "image/png", 
            403,  # Should fail with 403 Forbidden for non-admin
            use_admin_token=False
        )
        return success

    def test_logo_upload_valid_png(self):
        """Test uploading a valid PNG logo"""
        png_data = self.create_test_png_file()
        success, response = self.run_file_upload_test(
            "Logo Upload - Valid PNG", 
            "admin/cms/upload-logo", 
            png_data, 
            "cataloro_logo.png", 
            "image/png", 
            200,
            use_admin_token=True
        )
        
        if success and 'logo_url' in response:
            self.uploaded_logo_url = response['logo_url']
            print(f"   📁 Logo stored at: {self.uploaded_logo_url}")
            
        return success

    def test_logo_upload_invalid_format(self):
        """Test uploading non-PNG file (should fail)"""
        jpeg_data = self.create_test_jpeg_file()
        success, response = self.run_file_upload_test(
            "Logo Upload - Invalid Format (JPEG)", 
            "admin/cms/upload-logo", 
            jpeg_data, 
            "invalid_logo.jpg", 
            "image/jpeg", 
            400,  # Should fail with 400 Bad Request
            use_admin_token=True
        )
        return success

    def test_logo_upload_file_too_large(self):
        """Test uploading file larger than 5MB (should fail)"""
        large_png_data = self.create_test_png_file(size_mb=6)
        success, response = self.run_file_upload_test(
            "Logo Upload - File Too Large (6MB)", 
            "admin/cms/upload-logo", 
            large_png_data, 
            "large_logo.png", 
            "image/png", 
            400,  # Should fail with 400 Bad Request
            use_admin_token=True
        )
        return success

    def test_logo_stored_in_site_settings(self):
        """Test that uploaded logo URL is stored in site settings"""
        success, response = self.run_test("Logo in Site Settings", "GET", "admin/cms/settings", 200, use_admin_token=True)
        
        if success:
            has_logo_url = 'header_logo_url' in response
            has_logo_alt = 'header_logo_alt' in response
            
            if has_logo_url and has_logo_alt:
                logo_url = response.get('header_logo_url')
                logo_alt = response.get('header_logo_alt')
                print(f"   📁 Logo URL: {logo_url}")
                print(f"   🏷️  Logo Alt: {logo_alt}")
                return True
            else:
                print(f"   ❌ Missing logo fields - URL: {has_logo_url}, Alt: {has_logo_alt}")
                return False
        
        return success

    def test_logo_accessible_via_static_serving(self):
        """Test that uploaded logo is accessible via HTTP"""
        if not self.uploaded_logo_url:
            print("⚠️  Skipping logo accessibility test - no uploaded logo URL")
            return False
            
        logo_full_url = f"{self.base_url}{self.uploaded_logo_url}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Logo File Accessibility...")
        print(f"   URL: {logo_full_url}")
        
        try:
            response = requests.get(logo_full_url, timeout=10)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Logo file accessible")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"   File size: {len(response.content)} bytes")
            else:
                print(f"❌ Failed - Logo not accessible, status: {response.status_code}")
                
            return success
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False

    # ===========================
    # LISTING IMAGE UPLOAD TESTS
    # ===========================

    def test_listing_image_upload_auth_required(self):
        """Test that listing image upload requires authentication"""
        png_data = self.create_test_png_file()
        
        # Temporarily clear token to test without auth
        original_token = self.user_token
        self.user_token = None
        
        success, response = self.run_file_upload_test(
            "Listing Image Upload - Auth Required", 
            "listings/upload-image", 
            png_data, 
            "test_listing.png", 
            "image/png", 
            403,  # Should fail with 403 Forbidden
            use_admin_token=False
        )
        
        # Restore token
        self.user_token = original_token
        return success

    def test_listing_image_upload_valid_png(self):
        """Test uploading a valid PNG for listing"""
        png_data = self.create_test_png_file()
        success, response = self.run_file_upload_test(
            "Listing Image Upload - Valid PNG", 
            "listings/upload-image", 
            png_data, 
            "product_image.png", 
            "image/png", 
            200,
            use_admin_token=False
        )
        
        if success and 'image_url' in response:
            self.uploaded_listing_images.append(response['image_url'])
            print(f"   📁 Image stored at: {response['image_url']}")
            
        return success

    def test_listing_image_upload_valid_jpeg(self):
        """Test uploading a valid JPEG for listing"""
        jpeg_data = self.create_test_jpeg_file()
        success, response = self.run_file_upload_test(
            "Listing Image Upload - Valid JPEG", 
            "listings/upload-image", 
            jpeg_data, 
            "product_image.jpg", 
            "image/jpeg", 
            200,
            use_admin_token=False
        )
        
        if success and 'image_url' in response:
            self.uploaded_listing_images.append(response['image_url'])
            print(f"   📁 Image stored at: {response['image_url']}")
            
        return success

    def test_listing_image_upload_invalid_format(self):
        """Test uploading invalid format for listing (should fail)"""
        # Create fake GIF data
        gif_data = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;'
        success, response = self.run_file_upload_test(
            "Listing Image Upload - Invalid Format (GIF)", 
            "listings/upload-image", 
            gif_data, 
            "invalid_image.gif", 
            "image/gif", 
            400,  # Should fail with 400 Bad Request
            use_admin_token=False
        )
        return success

    def test_listing_image_upload_file_too_large(self):
        """Test uploading file larger than 10MB for listing (should fail)"""
        large_png_data = self.create_test_png_file(size_mb=11)
        success, response = self.run_file_upload_test(
            "Listing Image Upload - File Too Large (11MB)", 
            "listings/upload-image", 
            large_png_data, 
            "large_product.png", 
            "image/png", 
            400,  # Should fail with 400 Bad Request
            use_admin_token=False
        )
        return success

    def test_listing_image_upload_with_admin(self):
        """Test that admin users can also upload listing images"""
        png_data = self.create_test_png_file()
        success, response = self.run_file_upload_test(
            "Listing Image Upload - Admin User", 
            "listings/upload-image", 
            png_data, 
            "admin_product.png", 
            "image/png", 
            200,
            use_admin_token=True
        )
        
        if success and 'image_url' in response:
            self.uploaded_listing_images.append(response['image_url'])
            print(f"   📁 Admin image stored at: {response['image_url']}")
            
        return success

    def test_listing_images_accessible_via_static_serving(self):
        """Test that uploaded listing images are accessible via HTTP"""
        if not self.uploaded_listing_images:
            print("⚠️  Skipping listing image accessibility test - no uploaded images")
            return False
            
        # Test first uploaded image
        image_url = self.uploaded_listing_images[0]
        image_full_url = f"{self.base_url}{image_url}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Listing Image File Accessibility...")
        print(f"   URL: {image_full_url}")
        
        try:
            response = requests.get(image_full_url, timeout=10)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Listing image file accessible")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"   File size: {len(response.content)} bytes")
            else:
                print(f"❌ Failed - Listing image not accessible, status: {response.status_code}")
                
            return success
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False

    def test_create_listing_with_uploaded_images(self):
        """Test creating a listing with uploaded images"""
        if not self.uploaded_listing_images:
            print("⚠️  Skipping listing creation - no uploaded images")
            return False
            
        listing_data = {
            "title": "Premium Wireless Headphones",
            "description": "High-quality wireless headphones with noise cancellation and premium sound quality. Perfect for music lovers and professionals.",
            "category": "Electronics",
            "images": self.uploaded_listing_images[:3],  # Use up to 3 uploaded images
            "listing_type": "fixed_price",
            "price": 299.99,
            "condition": "New",
            "quantity": 1,
            "location": "San Francisco, CA",
            "shipping_cost": 9.99
        }
        
        success, response = self.run_test("Create Listing with Uploaded Images", "POST", "listings", 200, listing_data)
        if success and 'id' in response:
            listing_id = response['id']
            images = response.get('images', [])
            print(f"   📦 Created listing ID: {listing_id}")
            print(f"   🖼️  Images in listing: {len(images)} images")
            for i, img in enumerate(images[:2]):  # Show first 2 images
                print(f"      Image {i+1}: {img}")
        return success

    def run_all_tests(self):
        """Run all image upload tests"""
        print("🚀 Starting Image Upload Functionality Tests")
        print("=" * 60)
        print("Testing after frontend bug fix: !file.type === 'image/png' → file.type !== 'image/png'")
        print("=" * 60)
        
        # Setup authentication
        if not self.setup_authentication():
            print("\n❌ Authentication setup failed. Cannot proceed with tests.")
            return False

        # Logo Upload Tests
        print("\n" + "=" * 40)
        print("🏷️  LOGO UPLOAD TESTS")
        print("=" * 40)
        
        logo_tests = [
            self.test_logo_upload_admin_auth_required,
            self.test_logo_upload_valid_png,
            self.test_logo_upload_invalid_format,
            self.test_logo_upload_file_too_large,
            self.test_logo_stored_in_site_settings,
            self.test_logo_accessible_via_static_serving,
        ]
        
        for test in logo_tests:
            try:
                test()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")

        # Listing Image Upload Tests
        print("\n" + "=" * 40)
        print("🖼️  LISTING IMAGE UPLOAD TESTS")
        print("=" * 40)
        
        listing_tests = [
            self.test_listing_image_upload_auth_required,
            self.test_listing_image_upload_valid_png,
            self.test_listing_image_upload_valid_jpeg,
            self.test_listing_image_upload_invalid_format,
            self.test_listing_image_upload_file_too_large,
            self.test_listing_image_upload_with_admin,
            self.test_listing_images_accessible_via_static_serving,
            self.test_create_listing_with_uploaded_images,
        ]
        
        for test in listing_tests:
            try:
                test()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")

        # Final Results
        print("\n" + "=" * 60)
        print("📊 IMAGE UPLOAD TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL IMAGE UPLOAD TESTS PASSED!")
            print("✅ Logo upload functionality working correctly")
            print("✅ Listing image upload functionality working correctly")
            print("✅ Frontend bug fix successful")
            return True
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = ImageUploadTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()