#!/usr/bin/env python3
"""
IMAGE UPLOAD INVESTIGATION - Test image upload functionality thoroughly
Focus: Investigate the "serious connection error" reported by user
"""

import requests
import json
import sys
from PIL import Image
import io

# Configuration
BACKEND_URL = "https://marketplace-fix-6.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ImageUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
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
                print("✅ Admin authenticated successfully")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def create_test_images(self):
        """Create test images of different sizes and formats"""
        test_images = {}
        
        try:
            # Small PNG (valid)
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            test_images['small_png'] = img_bytes.getvalue()
            
            # Large PNG (might exceed limits)
            img = Image.new('RGB', (2000, 2000), color='blue')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            test_images['large_png'] = img_bytes.getvalue()
            
            # JPEG (valid for listings, invalid for logo)
            img = Image.new('RGB', (500, 500), color='green')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            test_images['jpeg'] = img_bytes.getvalue()
            
            # Very large image (should fail)
            img = Image.new('RGB', (5000, 5000), color='yellow')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            test_images['very_large_png'] = img_bytes.getvalue()
            
            print("✅ Test images created successfully")
            for name, data in test_images.items():
                print(f"   {name}: {len(data)} bytes")
            
            return test_images
            
        except Exception as e:
            print(f"❌ Error creating test images: {str(e)}")
            return {}

    def test_listing_image_upload_comprehensive(self, test_images):
        """Comprehensive test of listing image upload"""
        print("\n🔍 COMPREHENSIVE LISTING IMAGE UPLOAD TEST")
        print("=" * 60)
        
        test_cases = [
            ('small_png', 'test_small.png', 'image/png', "Small PNG (should work)"),
            ('large_png', 'test_large.png', 'image/png', "Large PNG (might fail size limit)"),
            ('jpeg', 'test_image.jpg', 'image/jpeg', "JPEG (should work)"),
            ('very_large_png', 'test_huge.png', 'image/png', "Very large PNG (should fail)")
        ]
        
        for image_key, filename, content_type, description in test_cases:
            if image_key not in test_images:
                print(f"❌ {description}: Test image not available")
                continue
                
            try:
                files = {
                    'file': (filename, test_images[image_key], content_type)
                }
                
                print(f"🧪 Testing: {description}")
                response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    image_url = data.get("image_url", "")
                    print(f"   ✅ SUCCESS: {image_url}")
                    
                    # Test accessibility
                    self.test_image_url_accessibility(image_url)
                    
                elif response.status_code == 413:
                    print(f"   ⚠️  FILE TOO LARGE: {response.status_code}")
                elif response.status_code == 400:
                    print(f"   ⚠️  BAD REQUEST: {response.text}")
                else:
                    print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError as e:
                print(f"   🚨 CONNECTION ERROR: {str(e)}")
                print("   This matches the user's 'serious connection error' report!")
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")

    def test_logo_upload_comprehensive(self, test_images):
        """Comprehensive test of logo upload"""
        print("\n🔍 COMPREHENSIVE LOGO UPLOAD TEST")
        print("=" * 60)
        
        test_cases = [
            ('small_png', 'test_logo_small.png', 'image/png', "Small PNG (should work)"),
            ('large_png', 'test_logo_large.png', 'image/png', "Large PNG (might fail size limit)"),
            ('jpeg', 'test_logo.jpg', 'image/jpeg', "JPEG (should fail - PNG only)"),
            ('very_large_png', 'test_logo_huge.png', 'image/png', "Very large PNG (should fail)")
        ]
        
        for image_key, filename, content_type, description in test_cases:
            if image_key not in test_images:
                print(f"❌ {description}: Test image not available")
                continue
                
            try:
                files = {
                    'file': (filename, test_images[image_key], content_type)
                }
                
                print(f"🧪 Testing: {description}")
                response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-logo", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    logo_url = data.get("logo_url", "")
                    print(f"   ✅ SUCCESS: {logo_url}")
                    
                    # Test accessibility
                    self.test_image_url_accessibility(logo_url)
                    
                elif response.status_code == 413:
                    print(f"   ⚠️  FILE TOO LARGE: {response.status_code}")
                elif response.status_code == 400:
                    print(f"   ⚠️  BAD REQUEST: {response.text}")
                else:
                    print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError as e:
                print(f"   🚨 CONNECTION ERROR: {str(e)}")
                print("   This matches the user's 'serious connection error' report!")
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")

    def test_image_url_accessibility(self, image_url):
        """Test if uploaded image URL is accessible"""
        if not image_url:
            return
            
        try:
            # Convert relative URL to full URL if needed
            if image_url.startswith('/'):
                full_url = f"https://marketplace-fix-6.preview.emergentagent.com{image_url}"
            else:
                full_url = image_url
            
            response = self.session.get(full_url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                if 'image' in content_type:
                    print(f"   ✅ Image accessible: {content_type}, {content_length} bytes")
                else:
                    print(f"   ⚠️  URL accessible but not serving image: {content_type}")
            else:
                print(f"   ❌ Image not accessible: {response.status_code}")
                
        except requests.exceptions.ConnectionError as e:
            print(f"   🚨 CONNECTION ERROR accessing image: {str(e)}")
        except Exception as e:
            print(f"   ❌ Error accessing image: {str(e)}")

    def test_network_connectivity(self):
        """Test network connectivity to different parts of the system"""
        print("\n🔍 NETWORK CONNECTIVITY TEST")
        print("=" * 60)
        
        endpoints_to_test = [
            (f"{BACKEND_URL}/", "Main API endpoint"),
            (f"https://marketplace-fix-6.preview.emergentagent.com/uploads/", "Static files endpoint"),
            (f"{BACKEND_URL}/categories", "Simple GET endpoint"),
            (f"{BACKEND_URL}/listings", "Listings endpoint")
        ]
        
        for url, description in endpoints_to_test:
            try:
                print(f"🧪 Testing: {description}")
                response = self.session.get(url, timeout=10)
                print(f"   ✅ SUCCESS: {response.status_code}")
                
            except requests.exceptions.ConnectionError as e:
                print(f"   🚨 CONNECTION ERROR: {str(e)}")
            except requests.exceptions.Timeout as e:
                print(f"   ⏰ TIMEOUT: {str(e)}")
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")

    def test_upload_with_different_methods(self, test_images):
        """Test upload with different HTTP methods and configurations"""
        print("\n🔍 UPLOAD METHOD VARIATIONS TEST")
        print("=" * 60)
        
        if 'small_png' not in test_images:
            print("❌ No test image available")
            return
        
        # Test with different session configurations
        test_configs = [
            ("Default session", self.session),
            ("New session with timeout", requests.Session()),
            ("Session with different headers", requests.Session())
        ]
        
        for config_name, session in test_configs:
            try:
                print(f"🧪 Testing: {config_name}")
                
                # Configure session
                if config_name == "New session with timeout":
                    session.timeout = 30
                elif config_name == "Session with different headers":
                    session.headers.update({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                
                # Add auth header
                if self.admin_token:
                    session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                
                files = {
                    'file': ('test_upload.png', test_images['small_png'], 'image/png')
                }
                
                response = session.post(f"{BACKEND_URL}/listings/upload-image", files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS: {data.get('image_url', 'No URL')}")
                else:
                    print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError as e:
                print(f"   🚨 CONNECTION ERROR: {str(e)}")
            except requests.exceptions.Timeout as e:
                print(f"   ⏰ TIMEOUT: {str(e)}")
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")

    def run_comprehensive_investigation(self):
        """Run comprehensive image upload investigation"""
        print("🔍 COMPREHENSIVE IMAGE UPLOAD INVESTIGATION")
        print("=" * 80)
        print("Investigating the 'serious connection error' reported by user")
        print("=" * 80)
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Test basic network connectivity
        self.test_network_connectivity()
        
        # Create test images
        test_images = self.create_test_images()
        if not test_images:
            print("❌ Cannot proceed without test images")
            return False
        
        # Test listing image upload comprehensively
        self.test_listing_image_upload_comprehensive(test_images)
        
        # Test logo upload comprehensively
        self.test_logo_upload_comprehensive(test_images)
        
        # Test different upload methods
        self.test_upload_with_different_methods(test_images)
        
        print("\n" + "=" * 80)
        print("IMAGE UPLOAD INVESTIGATION COMPLETE")
        print("=" * 80)
        print("🔍 If connection errors were found, this explains the user's issue")
        print("🔍 Check for network/proxy/firewall issues between frontend and backend")
        
        return True

if __name__ == "__main__":
    tester = ImageUploadTester()
    tester.run_comprehensive_investigation()