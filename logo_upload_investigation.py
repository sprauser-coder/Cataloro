#!/usr/bin/env python3
"""
URGENT LOGO UPLOAD AND IMAGE PREVIEW INVESTIGATION
Testing specific upload functionality as reported by user:

CRITICAL ISSUE REPORTED:
User reports that logo upload and picture previews are not working anywhere in the application.

INVESTIGATION AREAS:
1. Backend Upload Endpoints Testing
2. File Storage System Verification  
3. Upload Functionality Testing
4. Image Serving System Testing
5. API Response Analysis
"""

import requests
import json
import sys
import os
import tempfile
import io
from datetime import datetime
from pathlib import Path
from PIL import Image

# Configuration - Use environment variable for backend URL
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://marketplace-ready.preview.emergentagent.com') + '/api'
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class LogoUploadInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user = None
        self.test_results = []
        self.uploaded_files = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def create_test_image(self, format='PNG', size=(100, 100), file_size_mb=None):
        """Create a test image file"""
        img = Image.new('RGB', size, color='red')
        img_buffer = io.BytesIO()
        
        if file_size_mb:
            # Create larger image to reach target file size
            quality = 95
            while True:
                img_buffer.seek(0)
                img_buffer.truncate()
                img.save(img_buffer, format=format, quality=quality)
                current_size_mb = len(img_buffer.getvalue()) / (1024 * 1024)
                
                if current_size_mb >= file_size_mb:
                    break
                    
                # Increase image size if needed
                if quality > 10:
                    quality -= 5
                else:
                    size = (size[0] + 100, size[1] + 100)
                    img = Image.new('RGB', size, color='red')
        else:
            img.save(img_buffer, format=format)
        
        img_buffer.seek(0)
        return img_buffer
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.admin_token = data["access_token"]
                    self.admin_user = data["user"]
                    
                    if self.admin_user.get("role") == "admin":
                        self.log_test(
                            "Admin Authentication", 
                            True, 
                            f"Successfully authenticated as {self.admin_user.get('email')} with admin role"
                        )
                        return True
                    else:
                        self.log_test("Admin Authentication", False, f"User role is not admin: {self.admin_user.get('role')}")
                        return False
                else:
                    self.log_test("Admin Authentication", False, "Missing access_token or user in response")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Authentication failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_logo_upload_endpoint(self):
        """Test 1: Logo Upload Endpoint - POST /api/admin/cms/upload-logo"""
        print("📤 Testing Logo Upload Endpoint...")
        
        if not self.admin_token:
            self.log_test("Logo Upload Endpoint", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test 1a: Valid PNG upload
            png_image = self.create_test_image('PNG', (200, 200))
            files = {'logo': ('test_logo.png', png_image, 'image/png')}
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-logo", headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'logo_url' in data:
                    logo_url = data['logo_url']
                    self.uploaded_files.append(logo_url)
                    self.log_test(
                        "Logo Upload Endpoint - Valid PNG", 
                        True, 
                        f"PNG logo uploaded successfully. Logo URL: {logo_url}"
                    )
                    
                    # Test 1b: Invalid format (JPEG) should be rejected
                    jpeg_image = self.create_test_image('JPEG', (200, 200))
                    files = {'logo': ('test_logo.jpg', jpeg_image, 'image/jpeg')}
                    
                    response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-logo", headers=headers, files=files, timeout=30)
                    
                    if response.status_code == 400:
                        self.log_test(
                            "Logo Upload Endpoint - Invalid Format Rejection", 
                            True, 
                            "JPEG file correctly rejected (PNG only validation working)"
                        )
                    else:
                        self.log_test(
                            "Logo Upload Endpoint - Invalid Format Rejection", 
                            False, 
                            f"JPEG file should be rejected but got status {response.status_code}"
                        )
                    
                    # Test 1c: Large file size (should be rejected)
                    try:
                        large_image = self.create_test_image('PNG', (1000, 1000), file_size_mb=6)
                        files = {'logo': ('large_logo.png', large_image, 'image/png')}
                        
                        response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-logo", headers=headers, files=files, timeout=30)
                        
                        if response.status_code == 400:
                            self.log_test(
                                "Logo Upload Endpoint - File Size Validation", 
                                True, 
                                "Large file (6MB) correctly rejected"
                            )
                        else:
                            self.log_test(
                                "Logo Upload Endpoint - File Size Validation", 
                                False, 
                                f"Large file should be rejected but got status {response.status_code}"
                            )
                    except Exception as e:
                        self.log_test(
                            "Logo Upload Endpoint - File Size Validation", 
                            False, 
                            f"Error testing large file: {str(e)}"
                        )
                    
                    return True
                else:
                    self.log_test("Logo Upload Endpoint", False, f"No logo_url in response: {data}")
                    return False
            else:
                self.log_test("Logo Upload Endpoint", False, f"Upload failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Logo Upload Endpoint", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_listing_image_upload_endpoint(self):
        """Test 2: Listing Image Upload Endpoint - POST /api/listings/upload-image"""
        print("🖼️ Testing Listing Image Upload Endpoint...")
        
        if not self.admin_token:
            self.log_test("Listing Image Upload Endpoint", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test 2a: Valid PNG upload
            png_image = self.create_test_image('PNG', (300, 300))
            files = {'image': ('test_listing.png', png_image, 'image/png')}
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'image_url' in data:
                    image_url = data['image_url']
                    self.uploaded_files.append(image_url)
                    self.log_test(
                        "Listing Image Upload Endpoint - PNG", 
                        True, 
                        f"PNG listing image uploaded successfully. Image URL: {image_url}"
                    )
                    
                    # Test 2b: Valid JPEG upload
                    jpeg_image = self.create_test_image('JPEG', (300, 300))
                    files = {'image': ('test_listing.jpg', jpeg_image, 'image/jpeg')}
                    
                    response = self.session.post(f"{BACKEND_URL}/listings/upload-image", headers=headers, files=files, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'image_url' in data:
                            image_url = data['image_url']
                            self.uploaded_files.append(image_url)
                            self.log_test(
                                "Listing Image Upload Endpoint - JPEG", 
                                True, 
                                f"JPEG listing image uploaded successfully. Image URL: {image_url}"
                            )
                        else:
                            self.log_test("Listing Image Upload Endpoint - JPEG", False, f"No image_url in JPEG response: {data}")
                    else:
                        self.log_test("Listing Image Upload Endpoint - JPEG", False, f"JPEG upload failed with status {response.status_code}: {response.text}")
                    
                    # Test 2c: Invalid format (GIF) should be rejected
                    gif_image = self.create_test_image('PNG', (200, 200))  # Create as PNG but name as GIF
                    files = {'image': ('test_listing.gif', gif_image, 'image/gif')}
                    
                    response = self.session.post(f"{BACKEND_URL}/listings/upload-image", headers=headers, files=files, timeout=30)
                    
                    if response.status_code == 400:
                        self.log_test(
                            "Listing Image Upload Endpoint - Invalid Format Rejection", 
                            True, 
                            "GIF file correctly rejected (PNG/JPEG only validation working)"
                        )
                    else:
                        self.log_test(
                            "Listing Image Upload Endpoint - Invalid Format Rejection", 
                            False, 
                            f"GIF file should be rejected but got status {response.status_code}"
                        )
                    
                    return True
                else:
                    self.log_test("Listing Image Upload Endpoint", False, f"No image_url in response: {data}")
                    return False
            else:
                self.log_test("Listing Image Upload Endpoint", False, f"Upload failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Listing Image Upload Endpoint", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_file_storage_system(self):
        """Test 3: File Storage System - Check if files are properly saved and accessible"""
        print("💾 Testing File Storage System...")
        
        if not self.uploaded_files:
            self.log_test("File Storage System", False, "No uploaded files to test")
            return False
        
        try:
            accessible_files = []
            inaccessible_files = []
            
            for file_url in self.uploaded_files:
                try:
                    # Convert relative URL to full URL if needed
                    if file_url.startswith('/uploads/'):
                        full_url = BACKEND_URL.replace('/api', '') + file_url
                    elif file_url.startswith('uploads/'):
                        full_url = BACKEND_URL.replace('/api', '') + '/' + file_url
                    else:
                        full_url = file_url
                    
                    response = self.session.get(full_url, timeout=10)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        file_size = len(response.content)
                        accessible_files.append(f"{file_url} ({content_type}, {file_size} bytes)")
                    else:
                        inaccessible_files.append(f"{file_url} (Status: {response.status_code})")
                        
                except Exception as e:
                    inaccessible_files.append(f"{file_url} (Error: {str(e)})")
            
            if len(accessible_files) > 0:
                self.log_test(
                    "File Storage System", 
                    True, 
                    f"Files accessible via HTTP: {', '.join(accessible_files)}"
                )
                if inaccessible_files:
                    print(f"   Note: Some files not accessible: {', '.join(inaccessible_files)}")
                return True
            else:
                self.log_test(
                    "File Storage System", 
                    False, 
                    f"No files accessible. Issues: {', '.join(inaccessible_files)}"
                )
                return False
                
        except Exception as e:
            self.log_test("File Storage System", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_image_serving_headers(self):
        """Test 4: Image Serving Headers - Check proper HTTP headers for image serving"""
        print("📋 Testing Image Serving Headers...")
        
        if not self.uploaded_files:
            self.log_test("Image Serving Headers", False, "No uploaded files to test")
            return False
        
        try:
            for file_url in self.uploaded_files[:1]:  # Test first uploaded file
                # Convert relative URL to full URL if needed
                if file_url.startswith('/uploads/'):
                    full_url = BACKEND_URL.replace('/api', '') + file_url
                elif file_url.startswith('uploads/'):
                    full_url = BACKEND_URL.replace('/api', '') + '/' + file_url
                else:
                    full_url = file_url
                
                response = self.session.get(full_url, timeout=10)
                
                if response.status_code == 200:
                    headers = response.headers
                    content_type = headers.get('content-type', '')
                    cache_control = headers.get('cache-control', '')
                    content_length = headers.get('content-length', '')
                    
                    # Check if proper image headers are present
                    if content_type.startswith('image/'):
                        self.log_test(
                            "Image Serving Headers", 
                            True, 
                            f"Proper image headers. Content-Type: {content_type}, Cache-Control: {cache_control}, Content-Length: {content_length}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Image Serving Headers", 
                            False, 
                            f"Incorrect content-type: {content_type}. Should be image/*"
                        )
                        return False
                else:
                    self.log_test(
                        "Image Serving Headers", 
                        False, 
                        f"File not accessible for header testing. Status: {response.status_code}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Image Serving Headers", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_cms_settings_integration(self):
        """Test 5: CMS Settings Integration - Check if uploaded logo is stored in site settings"""
        print("⚙️ Testing CMS Settings Integration...")
        
        if not self.admin_token:
            self.log_test("CMS Settings Integration", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get current site settings
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if logo URL is stored in settings
                header_logo_url = data.get('header_logo_url')
                if header_logo_url:
                    self.log_test(
                        "CMS Settings Integration", 
                        True, 
                        f"Logo URL stored in site settings: {header_logo_url}"
                    )
                    
                    # Test if the logo URL from settings is accessible
                    if header_logo_url.startswith('/uploads/'):
                        full_url = BACKEND_URL.replace('/api', '') + header_logo_url
                    elif header_logo_url.startswith('uploads/'):
                        full_url = BACKEND_URL.replace('/api', '') + '/' + header_logo_url
                    else:
                        full_url = header_logo_url
                    
                    logo_response = self.session.get(full_url, timeout=10)
                    if logo_response.status_code == 200:
                        self.log_test(
                            "CMS Settings Logo Accessibility", 
                            True, 
                            f"Logo from settings is accessible via HTTP"
                        )
                    else:
                        self.log_test(
                            "CMS Settings Logo Accessibility", 
                            False, 
                            f"Logo from settings not accessible. Status: {logo_response.status_code}"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "CMS Settings Integration", 
                        False, 
                        "No header_logo_url found in site settings"
                    )
                    return False
            else:
                self.log_test(
                    "CMS Settings Integration", 
                    False, 
                    f"Failed to get site settings. Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("CMS Settings Integration", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_public_cms_settings(self):
        """Test 6: Public CMS Settings - Check if logo is available in public settings"""
        print("🌐 Testing Public CMS Settings...")
        
        try:
            # Get public site settings (no authentication required)
            response = self.session.get(f"{BACKEND_URL}/cms/settings", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if logo URL is available in public settings
                header_logo_url = data.get('header_logo_url')
                if header_logo_url:
                    self.log_test(
                        "Public CMS Settings", 
                        True, 
                        f"Logo URL available in public settings: {header_logo_url}"
                    )
                    return True
                else:
                    self.log_test(
                        "Public CMS Settings", 
                        False, 
                        "No header_logo_url found in public site settings"
                    )
                    return False
            else:
                self.log_test(
                    "Public CMS Settings", 
                    False, 
                    f"Failed to get public site settings. Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Public CMS Settings", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_unauthenticated_upload_rejection(self):
        """Test 7: Unauthenticated Upload Rejection - Ensure uploads require authentication"""
        print("🚫 Testing Unauthenticated Upload Rejection...")
        
        try:
            # Test logo upload without authentication
            png_image = self.create_test_image('PNG', (100, 100))
            files = {'logo': ('test_logo.png', png_image, 'image/png')}
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-logo", files=files, timeout=10)
            
            if response.status_code == 403 or response.status_code == 401:
                self.log_test(
                    "Unauthenticated Upload Rejection", 
                    True, 
                    f"Unauthenticated upload correctly rejected with status {response.status_code}"
                )
                return True
            else:
                self.log_test(
                    "Unauthenticated Upload Rejection", 
                    False, 
                    f"Unauthenticated upload should be rejected but got status {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Unauthenticated Upload Rejection", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_investigation(self):
        """Run complete logo upload and image preview investigation"""
        print("=" * 80)
        print("🔍 URGENT LOGO UPLOAD AND IMAGE PREVIEW INVESTIGATION")
        print("Investigating reported issues with logo upload and picture previews")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Run investigation tests
        tests = [
            self.test_unauthenticated_upload_rejection,
            self.test_logo_upload_endpoint,
            self.test_listing_image_upload_endpoint,
            self.test_file_storage_system,
            self.test_image_serving_headers,
            self.test_cms_settings_integration,
            self.test_public_cms_settings
        ]
        
        for test in tests:
            test()
        
        # Summary
        print("=" * 80)
        print("📊 LOGO UPLOAD INVESTIGATION SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        print()
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            print()
        
        # Diagnosis
        if len(failed_tests) == 0:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Logo upload and image preview functionality is working correctly.")
            print("🔍 The reported issue may be frontend-specific or user-specific.")
            print("💡 Recommendations:")
            print("   - Check frontend image display components")
            print("   - Verify frontend URL configuration")
            print("   - Test with different browsers/devices")
            print("   - Check network connectivity from user's location")
        elif len(passed_tests) >= 5:
            print("⚠️  MOSTLY WORKING: Core upload functionality working but some issues detected.")
            print("✅ Basic upload and storage working.")
            print("🔍 Check specific failed areas for potential improvements.")
        else:
            print("🚨 CRITICAL ISSUES DETECTED!")
            print("❌ Logo upload and image preview functionality has significant problems.")
            print("🔧 IMMEDIATE ACTION REQUIRED:")
            print("   - Fix failed upload endpoints")
            print("   - Check file storage permissions")
            print("   - Verify image serving configuration")
            print("   - Test authentication requirements")
        
        print("=" * 80)
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    investigator = LogoUploadInvestigator()
    success = investigator.run_investigation()
    sys.exit(0 if success else 1)