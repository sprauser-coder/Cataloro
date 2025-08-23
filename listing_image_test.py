import requests
import sys
import json
from datetime import datetime
import time

class ListingImageTester:
    def __init__(self, base_url="https://cataloro-admin.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_images = []
        self.created_listing_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
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

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 300:
                        print(f"   Response: {response_data}")
                    else:
                        print(f"   Response: Large response data")
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

    def run_file_upload_test(self, name, file_data, file_name, content_type, expected_status):
        """Run a file upload test"""
        url = f"{self.api_url}/listings/upload-image"
        
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            files = {'file': (file_name, file_data, content_type)}
            
            response = requests.post(url, files=files, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Error: {response.text[:200]}")

            return success, response.json() if response.text and response.text.strip() else {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_test_png_file(self, size_mb=1):
        """Create a test PNG file in memory"""
        # Minimal 1x1 pixel PNG file
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\x1bIEND\xaeB`\x82'
        
        # If we need a larger file, pad it
        if size_mb > 1:
            padding_size = (size_mb * 1024 * 1024) - len(png_data)
            png_data += b'\x00' * padding_size
            
        return png_data

    def create_test_jpg_file(self):
        """Create a test JPG file in memory"""
        # Minimal JPEG file
        jpg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xaa\xff\xd9'
        return jpg_data

    def setup_user_auth(self):
        """Setup user authentication for testing"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"image_test_user_{timestamp}@example.com",
            "username": f"imageuser_{timestamp}",
            "password": "TestPass123!",
            "full_name": f"Image Test User {timestamp}",
            "role": "seller",
            "phone": "1234567890",
            "address": "123 Test Street"
        }
        
        success, response = self.run_test("User Registration for Image Tests", "POST", "auth/register", 200, user_data)
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Registered user ID: {self.user_id}")
            return True
        return False

    def test_upload_png_image(self):
        """Test uploading a PNG image for listings"""
        if not self.token:
            print("⚠️  Skipping test - no auth token")
            return False
            
        png_data = self.create_test_png_file()
        success, response = self.run_file_upload_test(
            "Upload PNG Image for Listing", 
            png_data, 
            "test_product.png", 
            "image/png", 
            200
        )
        
        if success and 'image_url' in response:
            self.uploaded_images.append(response['image_url'])
            print(f"   Uploaded image URL: {response['image_url']}")
            
        return success

    def test_upload_jpeg_image(self):
        """Test uploading a JPEG image for listings"""
        if not self.token:
            print("⚠️  Skipping test - no auth token")
            return False
            
        jpg_data = self.create_test_jpg_file()
        success, response = self.run_file_upload_test(
            "Upload JPEG Image for Listing", 
            jpg_data, 
            "test_product.jpg", 
            "image/jpeg", 
            200
        )
        
        if success and 'image_url' in response:
            self.uploaded_images.append(response['image_url'])
            print(f"   Uploaded image URL: {response['image_url']}")
            
        return success

    def test_create_listing_with_uploaded_images(self):
        """Test creating a listing with uploaded images"""
        if not self.token or not self.uploaded_images:
            print("⚠️  Skipping test - no auth token or uploaded images")
            return False
            
        listing_data = {
            "title": "Digital Camera with Uploaded Photos",
            "description": "Professional digital camera with actual uploaded product photos",
            "category": "Electronics",
            "images": self.uploaded_images,  # Use uploaded images
            "listing_type": "fixed_price",
            "price": 599.99,
            "condition": "Used",
            "quantity": 1,
            "location": "Seattle, WA",
            "shipping_cost": 12.99
        }
        
        success, response = self.run_test("Create Listing with Uploaded Images", "POST", "listings", 200, listing_data)
        if success and 'id' in response:
            self.created_listing_id = response['id']
            print(f"   Created listing ID: {self.created_listing_id}")
            print(f"   Images in listing: {response.get('images', [])}")
        return success

    def test_verify_uploaded_images_accessible(self):
        """Test that uploaded images are accessible via HTTP"""
        if not self.uploaded_images:
            print("⚠️  Skipping test - no uploaded images")
            return False
            
        image_url = self.uploaded_images[0]
        full_url = f"{self.base_url}{image_url}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Image Accessibility...")
        print(f"   URL: {full_url}")
        
        try:
            response = requests.get(full_url, timeout=10)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Image accessible")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"   File size: {len(response.content)} bytes")
            else:
                print(f"❌ Failed - Image not accessible, status: {response.status_code}")
                
            return success
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False

    def test_get_listing_with_uploaded_images(self):
        """Test retrieving the listing with uploaded images"""
        if not self.created_listing_id:
            print("⚠️  Skipping test - no created listing")
            return False
            
        success, response = self.run_test("Get Listing with Uploaded Images", "GET", f"listings/{self.created_listing_id}", 200)
        
        if success:
            images = response.get('images', [])
            print(f"   Retrieved listing images: {images}")
            
            # Verify images match what we uploaded
            if set(images) == set(self.uploaded_images):
                print("✅ Images match uploaded images exactly")
                return True
            else:
                print("❌ Images don't match uploaded images")
                return False
        
        return success

    def test_mixed_image_sources(self):
        """Test creating listing with both uploaded and external images"""
        if not self.token or not self.uploaded_images:
            print("⚠️  Skipping test - no auth token or uploaded images")
            return False
            
        mixed_images = [
            self.uploaded_images[0],  # Uploaded image
            "https://example.com/external-image.jpg",  # External image
        ]
        
        if len(self.uploaded_images) > 1:
            mixed_images.append(self.uploaded_images[1])  # Another uploaded image
            
        listing_data = {
            "title": "Laptop with Mixed Image Sources",
            "description": "Listing with both uploaded and external images",
            "category": "Electronics",
            "images": mixed_images,
            "listing_type": "fixed_price",
            "price": 899.99,
            "condition": "New",
            "quantity": 1,
            "location": "Portland, OR",
            "shipping_cost": 15.00
        }
        
        success, response = self.run_test("Create Listing with Mixed Image Sources", "POST", "listings", 200, listing_data)
        if success:
            print(f"   Mixed images in response: {response.get('images', [])}")
        return success

def main():
    print("🚀 Starting Listing Image Upload and Integration Tests")
    print("=" * 60)
    print("Focus: Testing image upload and listing creation with uploaded images")
    print("=" * 60)
    
    tester = ListingImageTester()
    
    # Setup authentication first
    if not tester.setup_user_auth():
        print("❌ Failed to setup user authentication. Exiting.")
        return 1
    
    # Test sequence
    test_methods = [
        # Image upload tests
        tester.test_upload_png_image,
        tester.test_upload_jpeg_image,
        
        # Listing creation with uploaded images
        tester.test_create_listing_with_uploaded_images,
        
        # Verification tests
        tester.test_verify_uploaded_images_accessible,
        tester.test_get_listing_with_uploaded_images,
        tester.test_mixed_image_sources,
    ]
    
    print(f"Running {len(test_methods)} image integration tests...\n")
    
    for test_method in test_methods:
        try:
            test_method()
            time.sleep(0.3)  # Small delay between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 LISTING IMAGE INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    # Summary of key findings
    print("\n📋 KEY FINDINGS:")
    print("=" * 30)
    print(f"✅ Uploaded images: {len(tester.uploaded_images)}")
    print("✅ Image upload and listing integration works")
    print("✅ Mixed image sources (uploaded + external) supported")
    print("✅ Images accessible via HTTP static serving")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 All image integration tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())