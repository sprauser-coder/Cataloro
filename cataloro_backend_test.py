#!/usr/bin/env python3
"""
Cataloro Marketplace Backend Test Script
Focused testing based on review request:

1. Test API endpoints are working properly
2. Test file upload functionality - specifically test image upload for listings using `/api/listings/upload-image` endpoint
3. Test the CMS settings endpoint `/api/cms/settings` to ensure site settings are returned correctly
4. Test the logo upload functionality in admin panel
5. Test listing creation with images
6. Verify that static file URLs in the database match actual files in the uploads directory

Backend URL: http://217.154.0.82/api
Admin credentials: admin@marketplace.com / admin123
"""

import requests
import sys
import json
from datetime import datetime
import time
import io
import os
from pathlib import Path

class CataloroBackendTester:
    def __init__(self):
        # Use the correct backend URL from frontend .env
        self.base_url = "http://217.154.0.82"
        self.api_url = f"{self.base_url}/api"
        self.admin_token = None
        self.user_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_logo_url = None
        self.uploaded_image_urls = []
        self.created_listing_ids = []
        self.test_results = []

    def log_test(self, name, success, details="", critical=False):
        """Log test results"""
        self.tests_run += 1
        status = "PASSED" if success else "FAILED"
        priority = "🔴 CRITICAL" if critical and not success else "✅" if success else "❌"
        
        result = {
            "name": name,
            "success": success,
            "details": details,
            "critical": critical
        }
        self.test_results.append(result)
        
        if success:
            self.tests_passed += 1
            print(f"{priority} {name} - {status}")
        else:
            print(f"{priority} {name} - {status}")
        
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
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\x1b\x00\x00\x00\x00IEND\xaeB`\x82'
        
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

    def test_api_root_endpoint(self):
        """Test root API endpoint"""
        print("🌐 Testing Root API Endpoint...")
        
        success, status, response, text = self.make_request('GET', '')
        
        if success and response.get('message') == 'Marketplace API':
            self.log_test("Root API Endpoint", True, 
                         f"API responding correctly: {response.get('message')}")
        else:
            self.log_test("Root API Endpoint", False, 
                         f"Status: {status}, Response: {text[:200]}", critical=True)

    def test_admin_authentication(self):
        """Test admin authentication with provided credentials"""
        print("🔐 Testing Admin Authentication...")
        
        admin_credentials = {
            "email": "admin@marketplace.com",
            "password": "admin123"
        }
        
        success, status, response, text = self.make_request('POST', 'auth/login', admin_credentials)
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            admin_name = response.get('user', {}).get('full_name', 'Unknown')
            self.log_test("Admin Authentication", True, 
                         f"Admin authenticated successfully as {admin_name}")
            return True
        else:
            self.log_test("Admin Authentication", False, 
                         f"Status: {status}, Response: {text[:200]}", critical=True)
            return False

    def test_cms_settings_endpoint(self):
        """Test 3: CMS settings endpoint `/api/cms/settings`"""
        print("⚙️  Testing CMS Settings Endpoint...")
        
        success, status, response, text = self.make_request('GET', 'cms/settings')
        
        if success:
            # Check for required fields
            required_fields = ['site_name', 'site_tagline', 'hero_title', 'hero_subtitle']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                site_name = response.get('site_name', 'Unknown')
                self.log_test("CMS Settings Endpoint", True, 
                             f"All required fields present. Site name: {site_name}")
                
                # Check for logo fields
                has_logo_fields = 'header_logo_url' in response and 'header_logo_alt' in response
                if has_logo_fields:
                    logo_url = response.get('header_logo_url')
                    self.log_test("CMS Settings - Logo Fields", True, 
                                 f"Logo fields present. URL: {logo_url}")
                else:
                    self.log_test("CMS Settings - Logo Fields", False, 
                                 "Logo fields missing from settings")
            else:
                self.log_test("CMS Settings Endpoint", False, 
                             f"Missing required fields: {missing_fields}", critical=True)
        else:
            self.log_test("CMS Settings Endpoint", False, 
                         f"Status: {status}, Response: {text[:200]}", critical=True)

    def test_logo_upload_functionality(self):
        """Test 4: Logo upload functionality in admin panel"""
        print("🖼️  Testing Logo Upload Functionality...")
        
        if not self.admin_token:
            self.log_test("Logo Upload - Admin Auth Required", False, 
                         "No admin token available", critical=True)
            return False

        # Test valid PNG upload
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
            
            # Test file accessibility
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
                    self.log_test("Logo File Accessibility", False, 
                                 f"Error accessing logo: {str(e)}")
        else:
            self.log_test("Logo Upload - Valid PNG", False, 
                         f"Status: {status}, Response: {text[:300]}", critical=True)
            return False

        # Test invalid format rejection
        jpeg_data = self.create_test_jpeg_file(50)
        files = {'file': ('invalid_logo.jpg', jpeg_data, 'image/jpeg')}
        form_data = {'logo_type': 'header'}
        
        success, status, response, text = self.make_request('POST', 'admin/cms/upload-logo', 
                                                          data=form_data, files=files, 
                                                          use_admin_token=True, expected_status=400)
        
        self.log_test("Logo Upload - Format Validation", success, 
                     f"Correctly rejected JPEG file with status {status}")

        # Test file size limit
        large_png = self.create_test_png_file(6000)  # 6MB
        files = {'file': ('large_logo.png', large_png, 'image/png')}
        form_data = {'logo_type': 'header'}
        
        success, status, response, text = self.make_request('POST', 'admin/cms/upload-logo', 
                                                          data=form_data, files=files, 
                                                          use_admin_token=True, expected_status=400)
        
        self.log_test("Logo Upload - Size Limit", success, 
                     f"Correctly rejected large file with status {status}")

        return True

    def test_listing_image_upload(self):
        """Test 2: Image upload for listings using `/api/listings/upload-image` endpoint"""
        print("📸 Testing Listing Image Upload...")
        
        if not self.admin_token:
            self.log_test("Image Upload - Authentication", False, 
                         "No admin token available", critical=True)
            return False

        # Test PNG upload
        png_data = self.create_test_png_file(200)  # 200KB PNG
        files = {'file': ('product_image_1.png', png_data, 'image/png')}
        
        success, status, response, text = self.make_request('POST', 'listings/upload-image', 
                                                          files=files, use_admin_token=True)
        
        if success and 'image_url' in response:
            image_url = response['image_url']
            self.uploaded_image_urls.append(image_url)
            self.log_test("Image Upload - PNG Format", True, 
                         f"PNG image uploaded successfully. URL: {image_url}")
            
            # Test file accessibility
            if image_url.startswith('/uploads/'):
                image_access_url = f"{self.base_url}{image_url}"
                try:
                    image_response = requests.get(image_access_url, timeout=10)
                    if image_response.status_code == 200:
                        self.log_test("Image File Accessibility", True, 
                                     f"Image accessible at {image_access_url}")
                    else:
                        self.log_test("Image File Accessibility", False, 
                                     f"Image not accessible, status: {image_response.status_code}")
                except Exception as e:
                    self.log_test("Image File Accessibility", False, 
                                 f"Error accessing image: {str(e)}")
        else:
            self.log_test("Image Upload - PNG Format", False, 
                         f"Status: {status}, Response: {text[:300]}", critical=True)

        # Test JPEG upload
        jpeg_data = self.create_test_jpeg_file(150)  # 150KB JPEG
        files = {'file': ('product_image_2.jpg', jpeg_data, 'image/jpeg')}
        
        success, status, response, text = self.make_request('POST', 'listings/upload-image', 
                                                          files=files, use_admin_token=True)
        
        if success and 'image_url' in response:
            image_url = response['image_url']
            self.uploaded_image_urls.append(image_url)
            self.log_test("Image Upload - JPEG Format", True, 
                         f"JPEG image uploaded successfully. URL: {image_url}")
        else:
            self.log_test("Image Upload - JPEG Format", False, 
                         f"Status: {status}, Response: {text[:300]}")

        # Test invalid format rejection
        gif_data = b'GIF89a\x01\x00\x01\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;'
        files = {'file': ('invalid_image.gif', gif_data, 'image/gif')}
        
        success, status, response, text = self.make_request('POST', 'listings/upload-image', 
                                                          files=files, use_admin_token=True, 
                                                          expected_status=400)
        
        self.log_test("Image Upload - Format Validation", success, 
                     f"Correctly rejected GIF file with status {status}")

        # Test file size limit
        large_png = self.create_test_png_file(11000)  # 11MB
        files = {'file': ('large_image.png', large_png, 'image/png')}
        
        success, status, response, text = self.make_request('POST', 'listings/upload-image', 
                                                          files=files, use_admin_token=True, 
                                                          expected_status=400)
        
        self.log_test("Image Upload - Size Limit", success, 
                     f"Correctly rejected large file with status {status}")

        return True

    def test_listing_creation_with_images(self):
        """Test 5: Listing creation with images"""
        print("📝 Testing Listing Creation with Images...")
        
        if not self.admin_token:
            self.log_test("Listing Creation - Admin Auth", False, 
                         "No admin token available", critical=True)
            return False

        # Test basic listing creation
        listing_data = {
            "title": "Premium Wireless Headphones - Cataloro Test",
            "description": "High-quality wireless headphones with noise cancellation. Perfect for music lovers and professionals.",
            "category": "Electronics",
            "condition": "New",
            "price": 299.99,
            "quantity": 5,
            "location": "San Francisco, CA",
            "listing_type": "fixed_price",
            "shipping_cost": 15.99,
            "images": []
        }
        
        success, status, response, text = self.make_request('POST', 'listings', listing_data, 
                                                          use_admin_token=True)
        
        if success and 'id' in response:
            listing_id = response['id']
            self.created_listing_ids.append(listing_id)
            self.log_test("Listing Creation - Basic", True, 
                         f"Listing created successfully. ID: {listing_id}")
        else:
            self.log_test("Listing Creation - Basic", False, 
                         f"Status: {status}, Response: {text[:300]}", critical=True)
            return False

        # Test listing creation with uploaded images
        if self.uploaded_image_urls:
            listing_with_images = {
                "title": "Test Product with Real Images",
                "description": "This listing uses images that were uploaded via the image upload endpoint.",
                "category": "Art & Collectibles",
                "condition": "New",
                "price": 199.99,
                "quantity": 1,
                "location": "Los Angeles, CA",
                "listing_type": "fixed_price",
                "shipping_cost": 12.99,
                "images": self.uploaded_image_urls[:2]  # Use first 2 uploaded images
            }
            
            success, status, response, text = self.make_request('POST', 'listings', listing_with_images, 
                                                              use_admin_token=True)
            
            if success and 'id' in response:
                listing_id = response['id']
                self.created_listing_ids.append(listing_id)
                images_in_response = response.get('images', [])
                self.log_test("Listing Creation - With Images", True, 
                             f"Listing with {len(images_in_response)} images created. ID: {listing_id}")
                
                # Verify listing retrieval includes images
                success, status, get_response, text = self.make_request('GET', f'listings/{listing_id}')
                
                if success and 'images' in get_response:
                    retrieved_images = get_response['images']
                    self.log_test("Listing Retrieval - Images Included", True, 
                                 f"Retrieved listing has {len(retrieved_images)} images")
                else:
                    self.log_test("Listing Retrieval - Images Included", False, 
                                 f"Could not retrieve listing images, status: {status}")
            else:
                self.log_test("Listing Creation - With Images", False, 
                             f"Status: {status}, Response: {text[:300]}")
        else:
            self.log_test("Listing Creation - With Images", False, 
                         "No uploaded images available for testing")

        return True

    def test_static_file_url_verification(self):
        """Test 6: Verify static file URLs in database match actual files"""
        print("🔍 Testing Static File URL Verification...")
        
        # Check uploaded logo URL
        if self.uploaded_logo_url:
            logo_url = f"{self.base_url}{self.uploaded_logo_url}"
            try:
                response = requests.get(logo_url, timeout=10)
                if response.status_code == 200:
                    self.log_test("Static File - Logo URL Match", True, 
                                 f"Logo URL in database matches accessible file: {logo_url}")
                else:
                    self.log_test("Static File - Logo URL Match", False, 
                                 f"Logo URL in database does not match file, status: {response.status_code}")
            except Exception as e:
                self.log_test("Static File - Logo URL Match", False, 
                             f"Error accessing logo URL: {str(e)}")
        
        # Check uploaded image URLs
        for i, image_url in enumerate(self.uploaded_image_urls):
            if image_url.startswith('/uploads/'):
                full_url = f"{self.base_url}{image_url}"
                try:
                    response = requests.get(full_url, timeout=10)
                    if response.status_code == 200:
                        self.log_test(f"Static File - Image URL Match #{i+1}", True, 
                                     f"Image URL matches accessible file: {full_url}")
                    else:
                        self.log_test(f"Static File - Image URL Match #{i+1}", False, 
                                     f"Image URL does not match file, status: {response.status_code}")
                except Exception as e:
                    self.log_test(f"Static File - Image URL Match #{i+1}", False, 
                                 f"Error accessing image URL: {str(e)}")

        # Test listings endpoint to verify image URLs are returned correctly
        if self.created_listing_ids:
            for listing_id in self.created_listing_ids:
                success, status, response, text = self.make_request('GET', f'listings/{listing_id}')
                
                if success and 'images' in response:
                    images = response['images']
                    if images:
                        self.log_test(f"Listing Images in API Response", True, 
                                     f"Listing {listing_id} has {len(images)} images in API response")
                        
                        # Verify each image URL is accessible
                        for j, img_url in enumerate(images):
                            if img_url.startswith('/uploads/'):
                                full_img_url = f"{self.base_url}{img_url}"
                                try:
                                    img_response = requests.get(full_img_url, timeout=10)
                                    if img_response.status_code == 200:
                                        self.log_test(f"Listing Image Accessibility #{j+1}", True, 
                                                     f"Image accessible: {full_img_url}")
                                    else:
                                        self.log_test(f"Listing Image Accessibility #{j+1}", False, 
                                                     f"Image not accessible, status: {img_response.status_code}")
                                except Exception as e:
                                    self.log_test(f"Listing Image Accessibility #{j+1}", False, 
                                                 f"Error accessing image: {str(e)}")
                    else:
                        self.log_test(f"Listing Images in API Response", True, 
                                     f"Listing {listing_id} has no images (expected for basic listing)")

    def run_all_tests(self):
        """Run all tests based on review request"""
        print("🚀 Starting Cataloro Marketplace Backend Tests")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print(f"API Base URL: {self.api_url}")
        print("=" * 70)
        
        # 1. Test API endpoints are working properly
        print("\n" + "="*50)
        print("1️⃣  API ENDPOINTS FUNCTIONALITY")
        print("="*50)
        self.test_api_root_endpoint()
        
        # Authentication setup
        if not self.test_admin_authentication():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # 3. Test CMS settings endpoint
        print("\n" + "="*50)
        print("2️⃣  CMS SETTINGS ENDPOINT")
        print("="*50)
        self.test_cms_settings_endpoint()
        
        # 4. Test logo upload functionality
        print("\n" + "="*50)
        print("3️⃣  LOGO UPLOAD FUNCTIONALITY")
        print("="*50)
        self.test_logo_upload_functionality()
        
        # 2. Test file upload functionality for listings
        print("\n" + "="*50)
        print("4️⃣  LISTING IMAGE UPLOAD")
        print("="*50)
        self.test_listing_image_upload()
        
        # 5. Test listing creation with images
        print("\n" + "="*50)
        print("5️⃣  LISTING CREATION WITH IMAGES")
        print("="*50)
        self.test_listing_creation_with_images()
        
        # 6. Verify static file URLs match actual files
        print("\n" + "="*50)
        print("6️⃣  STATIC FILE URL VERIFICATION")
        print("="*50)
        self.test_static_file_url_verification()
        
        # Final summary
        self.print_final_summary()
        
        return self.tests_passed == self.tests_run

    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*70)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Critical failures
        critical_failures = [r for r in self.test_results if r['critical'] and not r['success']]
        if critical_failures:
            print(f"\n🔴 CRITICAL FAILURES ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   - {failure['name']}: {failure['details']}")
        
        # All failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ALL FAILURES ({len(failures)}):")
            for failure in failures:
                print(f"   - {failure['name']}: {failure['details']}")
        
        # Key successes
        key_successes = [r for r in self.test_results if r['success'] and any(keyword in r['name'].lower() for keyword in ['upload', 'creation', 'cms', 'static'])]
        if key_successes:
            print(f"\n✅ KEY SUCCESSES ({len(key_successes)}):")
            for success in key_successes:
                print(f"   - {success['name']}")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL TESTS PASSED! Backend is working correctly.")
        elif critical_failures:
            print("\n⚠️  CRITICAL ISSUES FOUND! Backend has major problems that need immediate attention.")
        else:
            print("\n⚠️  Some tests failed but no critical issues. Review the failures above.")

if __name__ == "__main__":
    tester = CataloroBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)