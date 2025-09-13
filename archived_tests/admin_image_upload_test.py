#!/usr/bin/env python3
"""
Admin Image Upload Functionality Testing
Testing the /api/admin/upload-image endpoint as requested in the review
"""

import asyncio
import aiohttp
import time
import json
import io
import base64
import os
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-marketplace-6.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

class AdminImageUploadTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.uploaded_files = []  # Track uploaded files for cleanup
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None, form_data=None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
            if form_data:
                request_kwargs['data'] = form_data
            if headers:
                request_kwargs['headers'] = headers
            
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **request_kwargs) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "response_time_ms": response_time_ms,
                    "data": response_data,
                    "status": response.status
                }
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time_ms,
                "error": str(e),
                "status": 0
            }
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            user_data = result["data"].get("user", {})
            print(f"  ✅ Admin authentication successful")
            print(f"  👤 User: {user_data.get('full_name', 'Unknown')} ({user_data.get('email')})")
            print(f"  🔑 Role: {user_data.get('user_role', user_data.get('role', 'Unknown'))}")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            print(f"  📊 Status: {result.get('status', 0)}")
            return False
    
    def create_test_image(self, size: str = "small") -> bytes:
        """Create test images of different sizes"""
        if size == "small":
            # 1x1 transparent PNG (smallest possible valid image)
            return base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            )
        elif size == "medium":
            # Simple 10x10 red square PNG
            return base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABYSURBVBiVY/z//z8DJQAggBhJVQgQQIykKgQIIEZSFQIEECOpCgECiJFUhQABxEiqQoAAYiRVIUAAMZKqECCAGElVCBBAjKQqBAggRlIVAgQQI6kKAQKIkVSFAAEEAKYQAwHjdQjDAAAAAElFTkSuQmCC"
            )
        else:
            # Default to small
            return self.create_test_image("small")
    
    async def test_endpoint_availability(self) -> Dict:
        """Test if /api/admin/upload-image endpoint exists and requires authentication"""
        print("🔍 Testing upload endpoint availability...")
        
        # Test without authentication (should return 401/403)
        no_auth_result = await self.make_request("/admin/upload-image", "POST")
        
        # Test with invalid authentication
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        invalid_auth_result = await self.make_request("/admin/upload-image", "POST", headers=invalid_headers)
        
        # Test with valid admin token but no data (should return 422)
        if self.admin_token:
            valid_headers = {"Authorization": f"Bearer {self.admin_token}"}
            no_data_result = await self.make_request("/admin/upload-image", "POST", headers=valid_headers)
        else:
            no_data_result = {"success": False, "status": 0, "error": "No admin token"}
        
        endpoint_exists = (
            no_auth_result["status"] in [401, 403] and
            invalid_auth_result["status"] in [401, 403] and
            no_data_result["status"] in [400, 422]
        )
        
        print(f"  📊 No auth: {no_auth_result['status']}")
        print(f"  📊 Invalid auth: {invalid_auth_result['status']}")
        print(f"  📊 Valid auth, no data: {no_data_result['status']}")
        print(f"  {'✅' if endpoint_exists else '❌'} Endpoint {'exists and properly secured' if endpoint_exists else 'not found or improperly secured'}")
        
        return {
            "test_name": "Endpoint Availability",
            "success": endpoint_exists,
            "no_auth_status": no_auth_result["status"],
            "invalid_auth_status": invalid_auth_result["status"],
            "valid_auth_no_data_status": no_data_result["status"],
            "endpoint_properly_secured": endpoint_exists
        }
    
    async def test_valid_image_upload(self) -> Dict:
        """Test uploading a valid image file"""
        print("📤 Testing valid image upload...")
        
        if not self.admin_token:
            return {"test_name": "Valid Image Upload", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create test image
        test_image = self.create_test_image("small")
        
        # Create form data
        form_data = aiohttp.FormData()
        form_data.add_field('image', io.BytesIO(test_image), filename='test_ad_image.png', content_type='image/png')
        form_data.add_field('section', 'ads_browsePageAd')
        form_data.add_field('field', 'image')
        
        result = await self.make_request("/admin/upload-image", "POST", headers=headers, form_data=form_data)
        
        upload_successful = result["success"]
        has_url = False
        image_url = None
        
        if upload_successful and isinstance(result["data"], dict):
            response_data = result["data"]
            has_url = "url" in response_data or "imageUrl" in response_data
            image_url = response_data.get("url") or response_data.get("imageUrl")
            
            if image_url:
                self.uploaded_files.append(image_url)
        
        print(f"  📊 Upload status: {result['status']}")
        print(f"  {'✅' if upload_successful else '❌'} Upload {'successful' if upload_successful else 'failed'}")
        if has_url:
            print(f"  📷 Image URL: {image_url}")
        
        return {
            "test_name": "Valid Image Upload",
            "success": upload_successful,
            "response_time_ms": result["response_time_ms"],
            "upload_status": result["status"],
            "has_image_url": has_url,
            "image_url": image_url,
            "response_data": result.get("data"),
            "error": result.get("error")
        }
    
    async def test_file_validation(self) -> Dict:
        """Test file validation (invalid file types, missing fields)"""
        print("🔍 Testing file validation...")
        
        if not self.admin_token:
            return {"test_name": "File Validation", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        validation_tests = []
        
        # Test 1: Invalid file type (text file)
        print("  Testing invalid file type...")
        invalid_form_data = aiohttp.FormData()
        invalid_form_data.add_field('image', io.BytesIO(b"This is not an image"), filename='test.txt', content_type='text/plain')
        invalid_form_data.add_field('section', 'ads')
        invalid_form_data.add_field('field', 'image')
        
        invalid_result = await self.make_request("/admin/upload-image", "POST", headers=headers, form_data=invalid_form_data)
        
        validation_tests.append({
            "test": "Invalid File Type",
            "success": not invalid_result["success"],  # Should fail
            "status": invalid_result["status"],
            "properly_rejected": invalid_result["status"] in [400, 422]
        })
        
        # Test 2: Missing image file
        print("  Testing missing image file...")
        no_file_form = aiohttp.FormData()
        no_file_form.add_field('section', 'ads')
        no_file_form.add_field('field', 'image')
        
        no_file_result = await self.make_request("/admin/upload-image", "POST", headers=headers, form_data=no_file_form)
        
        validation_tests.append({
            "test": "Missing Image File",
            "success": not no_file_result["success"],  # Should fail
            "status": no_file_result["status"],
            "properly_rejected": no_file_result["status"] in [400, 422]
        })
        
        # Test 3: Missing required fields (section, field)
        print("  Testing missing required fields...")
        test_image = self.create_test_image("small")
        missing_fields_form = aiohttp.FormData()
        missing_fields_form.add_field('image', io.BytesIO(test_image), filename='test.png', content_type='image/png')
        # Missing section and field
        
        missing_result = await self.make_request("/admin/upload-image", "POST", headers=headers, form_data=missing_fields_form)
        
        validation_tests.append({
            "test": "Missing Required Fields",
            "success": not missing_result["success"],  # Should fail
            "status": missing_result["status"],
            "properly_rejected": missing_result["status"] in [400, 422]
        })
        
        # Calculate validation results
        successful_validations = sum(1 for test in validation_tests if test.get("success", False))
        validation_working = successful_validations >= 2  # At least 2 validations should work
        
        print(f"  📊 Validation tests: {successful_validations}/{len(validation_tests)} passed")
        
        return {
            "test_name": "File Validation",
            "success": validation_working,
            "total_validation_tests": len(validation_tests),
            "successful_validations": successful_validations,
            "detailed_tests": validation_tests
        }
    
    async def test_static_file_serving(self) -> Dict:
        """Test if uploaded files are accessible via static file serving"""
        print("🌐 Testing static file serving...")
        
        if not self.uploaded_files:
            return {
                "test_name": "Static File Serving",
                "success": False,
                "error": "No uploaded files to test"
            }
        
        # Test accessing the uploaded file
        image_url = self.uploaded_files[0]  # Use first uploaded file
        
        # Remove /api prefix if present and test direct access
        if image_url.startswith('/'):
            test_url = image_url
        else:
            test_url = f"/{image_url}"
        
        # Test accessing the file directly
        file_result = await self.make_request(test_url, "GET")
        
        # Also test with full backend URL
        full_url = f"{BACKEND_URL.replace('/api', '')}{test_url}"
        try:
            async with self.session.get(full_url) as response:
                file_accessible = response.status == 200
                content_type = response.headers.get('content-type', '')
                is_image = content_type.startswith('image/')
        except:
            file_accessible = False
            is_image = False
        
        print(f"  📊 File URL: {image_url}")
        print(f"  📊 Direct access status: {file_result['status']}")
        print(f"  {'✅' if file_accessible else '❌'} File {'accessible' if file_accessible else 'not accessible'}")
        print(f"  {'✅' if is_image else '❌'} Content type {'is image' if is_image else 'not image'}")
        
        return {
            "test_name": "Static File Serving",
            "success": file_accessible and is_image,
            "file_url": image_url,
            "file_accessible": file_accessible,
            "is_image_content": is_image,
            "direct_access_status": file_result["status"]
        }
    
    async def test_different_image_formats(self) -> Dict:
        """Test uploading different image formats (PNG, JPG, etc.)"""
        print("🎨 Testing different image formats...")
        
        if not self.admin_token:
            return {"test_name": "Different Image Formats", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        format_tests = []
        
        # Test PNG (already tested above, but let's be explicit)
        print("  Testing PNG format...")
        png_image = self.create_test_image("small")
        
        png_form_data = aiohttp.FormData()
        png_form_data.add_field('image', io.BytesIO(png_image), filename='test.png', content_type='image/png')
        png_form_data.add_field('section', 'ads')
        png_form_data.add_field('field', 'test_png')
        
        png_result = await self.make_request("/admin/upload-image", "POST", headers=headers, form_data=png_form_data)
        
        format_tests.append({
            "format": "PNG",
            "success": png_result["success"],
            "status": png_result["status"],
            "has_url": bool(png_result.get("data", {}).get("url"))
        })
        
        # Test JPEG (simulate by changing content type and filename)
        print("  Testing JPEG format...")
        jpeg_form_data = aiohttp.FormData()
        jpeg_form_data.add_field('image', io.BytesIO(png_image), filename='test.jpg', content_type='image/jpeg')
        jpeg_form_data.add_field('section', 'ads')
        jpeg_form_data.add_field('field', 'test_jpg')
        
        jpeg_result = await self.make_request("/admin/upload-image", "POST", headers=headers, form_data=jpeg_form_data)
        
        format_tests.append({
            "format": "JPEG",
            "success": jpeg_result["success"],
            "status": jpeg_result["status"],
            "has_url": bool(jpeg_result.get("data", {}).get("url"))
        })
        
        # Calculate format support
        successful_formats = sum(1 for test in format_tests if test.get("success", False))
        format_support_working = successful_formats >= 1  # At least one format should work
        
        print(f"  📊 Format tests: {successful_formats}/{len(format_tests)} passed")
        
        return {
            "test_name": "Different Image Formats",
            "success": format_support_working,
            "total_format_tests": len(format_tests),
            "successful_formats": successful_formats,
            "detailed_tests": format_tests
        }
    
    async def test_ads_management_integration(self) -> Dict:
        """Test the complete ads management workflow with image upload"""
        print("🔄 Testing ads management integration...")
        
        if not self.admin_token:
            return {"test_name": "Ads Management Integration", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        workflow_steps = []
        
        # Step 1: Upload image for ads
        print("  Step 1: Uploading image for ads...")
        test_image = self.create_test_image("medium")
        
        form_data = aiohttp.FormData()
        form_data.add_field('image', io.BytesIO(test_image), filename='ads_test_image.png', content_type='image/png')
        form_data.add_field('section', 'ads_browsePageAd')
        form_data.add_field('field', 'image')
        
        upload_result = await self.make_request("/admin/upload-image", "POST", headers=headers, form_data=form_data)
        
        workflow_steps.append({
            "step": "Image Upload for Ads",
            "success": upload_result["success"],
            "status": upload_result["status"],
            "has_url": bool(upload_result.get("data", {}).get("url"))
        })
        
        # Step 2: Test if we can create an ad with the uploaded image (if ads endpoint exists)
        print("  Step 2: Testing ad creation with uploaded image...")
        if upload_result["success"]:
            image_url = upload_result["data"].get("url") or upload_result["data"].get("imageUrl")
            
            # Try to create an ad (this might not exist, but let's test)
            ad_data = {
                "title": "Test Ad with Uploaded Image",
                "description": "Testing ads upload functionality",
                "image_url": image_url,
                "placement": "browse_page",
                "enabled": True
            }
            
            create_ad_result = await self.make_request("/admin/ads", "POST", data=ad_data, headers=headers)
            
            workflow_steps.append({
                "step": "Ad Creation with Image",
                "success": create_ad_result["success"],
                "status": create_ad_result["status"],
                "image_url_used": image_url
            })
        else:
            workflow_steps.append({
                "step": "Ad Creation with Image",
                "success": False,
                "error": "Image upload failed"
            })
        
        # Step 3: Test error handling
        print("  Step 3: Testing error handling...")
        invalid_form_data = aiohttp.FormData()
        invalid_form_data.add_field('image', io.BytesIO(b"not an image"), filename='invalid.txt', content_type='text/plain')
        invalid_form_data.add_field('section', 'ads_browsePageAd')
        invalid_form_data.add_field('field', 'image')
        
        error_result = await self.make_request("/admin/upload-image", "POST", headers=headers, form_data=invalid_form_data)
        
        workflow_steps.append({
            "step": "Error Handling",
            "success": not error_result["success"],  # Should fail
            "status": error_result["status"],
            "properly_rejected": error_result["status"] in [400, 422]
        })
        
        # Calculate workflow success
        successful_steps = sum(1 for step in workflow_steps if step.get("success", False))
        workflow_success = successful_steps >= 2  # At least upload and error handling should work
        
        print(f"  📊 Workflow steps: {successful_steps}/{len(workflow_steps)} successful")
        
        return {
            "test_name": "Ads Management Integration",
            "success": workflow_success,
            "total_steps": len(workflow_steps),
            "successful_steps": successful_steps,
            "detailed_steps": workflow_steps
        }
    
    async def run_comprehensive_test(self) -> Dict:
        """Run all admin image upload tests"""
        print("🚀 Starting Admin Image Upload Functionality Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_admin()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Admin authentication failed - cannot proceed with tests"
                }
            
            # Run all test suites
            endpoint_availability = await self.test_endpoint_availability()
            valid_image_upload = await self.test_valid_image_upload()
            file_validation = await self.test_file_validation()
            static_file_serving = await self.test_static_file_serving()
            different_formats = await self.test_different_image_formats()
            ads_integration = await self.test_ads_management_integration()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "endpoint_availability": endpoint_availability,
                "valid_image_upload": valid_image_upload,
                "file_validation": file_validation,
                "static_file_serving": static_file_serving,
                "different_image_formats": different_formats,
                "ads_management_integration": ads_integration
            }
            
            # Calculate overall success metrics
            test_results = [
                endpoint_availability.get("success", False),
                valid_image_upload.get("success", False),
                file_validation.get("success", False),
                static_file_serving.get("success", False),
                different_formats.get("success", False),
                ads_integration.get("success", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "endpoint_available": endpoint_availability.get("success", False),
                "image_upload_working": valid_image_upload.get("success", False),
                "file_validation_working": file_validation.get("success", False),
                "static_serving_working": static_file_serving.get("success", False),
                "format_support_working": different_formats.get("success", False),
                "ads_integration_working": ads_integration.get("success", False),
                "all_tests_passed": overall_success_rate == 100,
                "critical_functionality_working": (
                    endpoint_availability.get("success", False) and
                    valid_image_upload.get("success", False) and
                    file_validation.get("success", False)
                ),
                "upload_failure_identified": not valid_image_upload.get("success", False)
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution"""
    tester = AdminImageUploadTester()
    results = await tester.run_comprehensive_test()
    
    # Print summary
    print("\n" + "=" * 70)
    print("🎯 ADMIN IMAGE UPLOAD TEST RESULTS SUMMARY")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print("📊 Individual Test Results:")
    for test_name, test_result in results.items():
        if test_name not in ["test_timestamp", "summary"] and isinstance(test_result, dict):
            status = "✅" if test_result.get("success", False) else "❌"
            print(f"   {status} {test_result.get('test_name', test_name)}")
    
    print(f"\n🏆 OVERALL RESULTS:")
    print(f"   {'✅' if summary.get('all_tests_passed', False) else '❌'} ALL TESTS {'PASSED' if summary.get('all_tests_passed', False) else 'FAILED'}")
    print(f"   Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"   Critical Functionality: {'✅' if summary.get('critical_functionality_working', False) else '❌'} {'Working' if summary.get('critical_functionality_working', False) else 'Failed'}")
    
    print(f"\n📋 Detailed Breakdown:")
    print(f"   Endpoint Available: {'✅' if summary.get('endpoint_available', False) else '❌'}")
    print(f"   Image Upload Working: {'✅' if summary.get('image_upload_working', False) else '❌'}")
    print(f"   File Validation Working: {'✅' if summary.get('file_validation_working', False) else '❌'}")
    print(f"   Static Serving Working: {'✅' if summary.get('static_serving_working', False) else '❌'}")
    print(f"   Format Support Working: {'✅' if summary.get('format_support_working', False) else '❌'}")
    print(f"   Ads Integration Working: {'✅' if summary.get('ads_integration_working', False) else '❌'}")
    
    # Save results to file
    results_file = "/app/admin_image_upload_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed test results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())