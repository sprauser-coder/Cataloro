#!/usr/bin/env python3
"""
URGENT IMAGE UPLOAD TESTING - 403 ERROR INVESTIGATION
Testing image upload failing with 403 error in Admin Panel > Ads Manager
"""

import asyncio
import aiohttp
import time
import json
import base64
import io
import os
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://self-hosted-shop.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"
ADMIN_ROLE = "admin"

class ImageUploadTester:
    """
    URGENT: Test image upload functionality for Admin Panel > Ads Manager
    Investigate 403 error: "Image upload error: Error: Upload failed: 403"
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = {}
        
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
                    "status": response.status,
                    "headers": dict(response.headers)
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
        print("🔐 Testing admin authentication for image upload...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            user_data = result["data"].get("user", {})
            user_role = user_data.get("user_role", "unknown")
            
            print(f"  ✅ Admin authentication successful")
            print(f"  👤 User role: {user_role}")
            print(f"  🎫 Token length: {len(self.admin_token)} characters")
            
            self.test_results["admin_authentication"] = {
                "success": True,
                "user_role": user_role,
                "token_received": bool(self.admin_token),
                "response_time_ms": result["response_time_ms"]
            }
            return True
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            print(f"  📊 Status code: {result.get('status', 'Unknown')}")
            
            self.test_results["admin_authentication"] = {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result.get("status", 0)
            }
            return False
    
    def create_test_image(self) -> bytes:
        """Create a small test image (PNG format)"""
        # Create a simple 10x10 red PNG image
        from PIL import Image
        import io
        
        try:
            # Create a small red image
            img = Image.new('RGB', (10, 10), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes.getvalue()
        except ImportError:
            # Fallback: create a minimal PNG manually if PIL not available
            # This is a 1x1 red PNG (minimal valid PNG)
            png_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            )
            return png_data
    
    async def test_upload_image_endpoint_access(self) -> Dict:
        """Test if the upload-image endpoint is accessible"""
        print("🔍 Testing upload-image endpoint accessibility...")
        
        if not self.admin_token:
            return {"test_name": "Upload Image Endpoint Access", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test different possible endpoints
        endpoints_to_test = [
            "/upload-image",           # What user might be calling
            "/admin/upload-image",     # What actually exists
            "/admin/ads/upload-image", # Possible ads-specific endpoint
            "/ads/upload-image"        # Alternative
        ]
        
        endpoint_results = {}
        
        for endpoint in endpoints_to_test:
            print(f"  🔍 Testing {endpoint}...")
            
            # Test with OPTIONS method first (CORS preflight)
            options_result = await self.make_request(endpoint, "OPTIONS", headers=headers)
            
            # Test with GET method to see if endpoint exists
            get_result = await self.make_request(endpoint, "GET", headers=headers)
            
            endpoint_results[endpoint] = {
                "options_status": options_result["status"],
                "options_success": options_result["success"],
                "get_status": get_result["status"],
                "get_success": get_result["success"],
                "get_error": get_result.get("error", ""),
                "cors_headers": {
                    "access_control_allow_origin": options_result["headers"].get("access-control-allow-origin", ""),
                    "access_control_allow_methods": options_result["headers"].get("access-control-allow-methods", ""),
                    "access_control_allow_headers": options_result["headers"].get("access-control-allow-headers", "")
                }
            }
            
            print(f"    OPTIONS: {options_result['status']}, GET: {get_result['status']}")
        
        # Determine which endpoint is most likely correct
        working_endpoint = None
        for endpoint, result in endpoint_results.items():
            if result["get_status"] in [200, 405]:  # 405 = Method Not Allowed (but endpoint exists)
                working_endpoint = endpoint
                break
        
        print(f"  📊 Endpoint accessibility test complete")
        print(f"  🎯 Most likely working endpoint: {working_endpoint or 'None found'}")
        
        return {
            "test_name": "Upload Image Endpoint Access",
            "success": working_endpoint is not None,
            "working_endpoint": working_endpoint,
            "endpoint_results": endpoint_results,
            "cors_support": any(result["cors_headers"]["access_control_allow_origin"] for result in endpoint_results.values())
        }
    
    async def test_image_upload_with_multipart(self) -> Dict:
        """Test actual image upload with multipart/form-data"""
        print("📤 Testing image upload with multipart/form-data...")
        
        if not self.admin_token:
            return {"test_name": "Image Upload Multipart", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create test image
        test_image_data = self.create_test_image()
        
        # Test the actual endpoint that exists: /api/admin/upload-image
        endpoint = "/admin/upload-image"
        
        # Create multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field('image', 
                           test_image_data, 
                           filename='test_ad_image.png', 
                           content_type='image/png')
        form_data.add_field('section', 'ads')
        form_data.add_field('field', 'main_image')
        
        print(f"  📤 Uploading to {endpoint}...")
        print(f"  📊 Image size: {len(test_image_data)} bytes")
        print(f"  🏷️ Content type: image/png")
        
        result = await self.make_request(endpoint, "POST", headers=headers, form_data=form_data)
        
        if result["success"]:
            response_data = result["data"]
            image_url = response_data.get("url", "") if isinstance(response_data, dict) else ""
            
            print(f"  ✅ Image upload successful!")
            print(f"  🔗 Image URL: {image_url}")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.1f}ms")
            
            return {
                "test_name": "Image Upload Multipart",
                "success": True,
                "image_url": image_url,
                "response_time_ms": result["response_time_ms"],
                "response_data": response_data,
                "image_size_bytes": len(test_image_data)
            }
        else:
            error_msg = result.get("error", "Unknown error")
            status_code = result.get("status", 0)
            
            print(f"  ❌ Image upload failed!")
            print(f"  📊 Status code: {status_code}")
            print(f"  💬 Error: {error_msg}")
            
            # Check for specific 403 error details
            if status_code == 403:
                print(f"  🚨 403 FORBIDDEN ERROR DETECTED!")
                print(f"  🔍 This matches the user's reported issue")
                
                # Analyze the error response
                error_analysis = {
                    "is_403_error": True,
                    "likely_causes": [],
                    "response_data": result.get("data", "")
                }
                
                if "admin" in str(error_msg).lower():
                    error_analysis["likely_causes"].append("Admin access required")
                if "token" in str(error_msg).lower() or "auth" in str(error_msg).lower():
                    error_analysis["likely_causes"].append("Authentication token issue")
                if "cors" in str(error_msg).lower():
                    error_analysis["likely_causes"].append("CORS policy issue")
                if not error_analysis["likely_causes"]:
                    error_analysis["likely_causes"].append("Unknown authorization issue")
                
                return {
                    "test_name": "Image Upload Multipart",
                    "success": False,
                    "status": status_code,
                    "error": error_msg,
                    "error_analysis": error_analysis,
                    "matches_user_issue": True
                }
            
            return {
                "test_name": "Image Upload Multipart",
                "success": False,
                "status": status_code,
                "error": error_msg,
                "response_data": result.get("data", ""),
                "matches_user_issue": status_code == 403
            }
    
    async def test_wrong_endpoint_call(self) -> Dict:
        """Test what happens when calling the wrong endpoint (like frontend might be doing)"""
        print("🔍 Testing wrong endpoint call (simulating frontend issue)...")
        
        if not self.admin_token:
            return {"test_name": "Wrong Endpoint Call", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test calling /api/upload-image (without admin prefix) - what user might be calling
        wrong_endpoint = "/upload-image"
        
        # Create test image
        test_image_data = self.create_test_image()
        
        # Create multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field('image', 
                           test_image_data, 
                           filename='test_ad_image.png', 
                           content_type='image/png')
        form_data.add_field('section', 'ads')
        form_data.add_field('field', 'main_image')
        
        print(f"  📤 Testing wrong endpoint: {wrong_endpoint}")
        
        result = await self.make_request(wrong_endpoint, "POST", headers=headers, form_data=form_data)
        
        status_code = result.get("status", 0)
        error_msg = result.get("error", "Unknown error")
        
        if status_code == 404:
            print(f"  ✅ Expected 404 error for wrong endpoint")
            print(f"  💡 This suggests frontend might be calling wrong URL")
            
            return {
                "test_name": "Wrong Endpoint Call",
                "success": True,  # Expected behavior
                "status": status_code,
                "error": error_msg,
                "analysis": "Frontend likely calling wrong endpoint URL",
                "recommendation": "Frontend should call /api/admin/upload-image instead of /api/upload-image"
            }
        elif status_code == 403:
            print(f"  🚨 403 error on wrong endpoint too!")
            print(f"  🔍 This might indicate a broader auth issue")
            
            return {
                "test_name": "Wrong Endpoint Call",
                "success": False,
                "status": status_code,
                "error": error_msg,
                "analysis": "403 error even on wrong endpoint suggests auth issue",
                "recommendation": "Check authentication token and admin permissions"
            }
        else:
            print(f"  ❓ Unexpected response: {status_code}")
            
            return {
                "test_name": "Wrong Endpoint Call",
                "success": False,
                "status": status_code,
                "error": error_msg,
                "analysis": f"Unexpected status code: {status_code}",
                "recommendation": "Investigate server configuration"
            }
    
    async def test_cors_preflight(self) -> Dict:
        """Test CORS preflight request for image upload"""
        print("🌐 Testing CORS preflight for image upload...")
        
        endpoint = "/admin/upload-image"
        
        # Simulate browser CORS preflight request
        cors_headers = {
            "Origin": "https://self-hosted-shop.preview.emergentagent.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
        
        result = await self.make_request(endpoint, "OPTIONS", headers=cors_headers)
        
        response_headers = result.get("headers", {})
        cors_analysis = {
            "preflight_status": result["status"],
            "access_control_allow_origin": response_headers.get("access-control-allow-origin", ""),
            "access_control_allow_methods": response_headers.get("access-control-allow-methods", ""),
            "access_control_allow_headers": response_headers.get("access-control-allow-headers", ""),
            "access_control_allow_credentials": response_headers.get("access-control-allow-credentials", "")
        }
        
        cors_working = (
            result["status"] in [200, 204] and
            cors_analysis["access_control_allow_origin"] in ["*", "https://self-hosted-shop.preview.emergentagent.com"]
        )
        
        print(f"  📊 CORS preflight status: {result['status']}")
        print(f"  🌐 Allow origin: {cors_analysis['access_control_allow_origin']}")
        print(f"  📝 Allow methods: {cors_analysis['access_control_allow_methods']}")
        print(f"  🔑 Allow headers: {cors_analysis['access_control_allow_headers']}")
        print(f"  {'✅' if cors_working else '❌'} CORS {'working' if cors_working else 'may have issues'}")
        
        return {
            "test_name": "CORS Preflight",
            "success": cors_working,
            "cors_analysis": cors_analysis,
            "potential_cors_issue": not cors_working
        }
    
    async def test_directory_permissions(self) -> Dict:
        """Test if upload directory has proper permissions"""
        print("📁 Testing upload directory permissions...")
        
        # We can't directly test file system permissions from here,
        # but we can test if the upload endpoint can create directories
        
        if not self.admin_token:
            return {"test_name": "Directory Permissions", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a small test image
        test_image_data = self.create_test_image()
        
        # Test upload to a subdirectory that might not exist
        form_data = aiohttp.FormData()
        form_data.add_field('image', 
                           test_image_data, 
                           filename='permission_test.png', 
                           content_type='image/png')
        form_data.add_field('section', 'test_permissions')
        form_data.add_field('field', 'test_field')
        
        result = await self.make_request("/admin/upload-image", "POST", headers=headers, form_data=form_data)
        
        if result["success"]:
            print(f"  ✅ Directory permissions working - upload successful")
            return {
                "test_name": "Directory Permissions",
                "success": True,
                "can_create_directories": True,
                "can_write_files": True
            }
        else:
            error_msg = result.get("error", "")
            status_code = result.get("status", 0)
            
            # Check if error is permission-related
            permission_keywords = ["permission", "denied", "access", "write", "directory", "folder"]
            is_permission_error = any(keyword in str(error_msg).lower() for keyword in permission_keywords)
            
            print(f"  ❌ Upload failed - Status: {status_code}")
            print(f"  💬 Error: {error_msg}")
            print(f"  {'🚨' if is_permission_error else '❓'} {'Permission issue detected' if is_permission_error else 'Non-permission error'}")
            
            return {
                "test_name": "Directory Permissions",
                "success": False,
                "status": status_code,
                "error": error_msg,
                "is_permission_error": is_permission_error,
                "can_create_directories": False,
                "can_write_files": False
            }
    
    async def test_admin_role_verification(self) -> Dict:
        """Test if admin role is properly verified"""
        print("👤 Testing admin role verification...")
        
        if not self.admin_token:
            return {"test_name": "Admin Role Verification", "error": "No admin token available"}
        
        # Test accessing an admin-only endpoint to verify role
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test admin endpoints that should work
        admin_endpoints = [
            "/admin/ads",
            "/admin/menu-settings",
            "/admin/performance"
        ]
        
        role_verification_results = {}
        
        for endpoint in admin_endpoints:
            result = await self.make_request(endpoint, "GET", headers=headers)
            role_verification_results[endpoint] = {
                "status": result["status"],
                "success": result["success"],
                "error": result.get("error", "")
            }
            
            print(f"  🔍 {endpoint}: {result['status']}")
        
        # Count successful admin endpoint accesses
        successful_admin_calls = sum(1 for result in role_verification_results.values() if result["success"])
        total_admin_calls = len(admin_endpoints)
        
        admin_role_working = successful_admin_calls > 0
        
        print(f"  📊 Admin endpoints accessible: {successful_admin_calls}/{total_admin_calls}")
        print(f"  {'✅' if admin_role_working else '❌'} Admin role {'verified' if admin_role_working else 'verification failed'}")
        
        return {
            "test_name": "Admin Role Verification",
            "success": admin_role_working,
            "successful_admin_calls": successful_admin_calls,
            "total_admin_calls": total_admin_calls,
            "role_verification_results": role_verification_results,
            "admin_access_working": admin_role_working
        }
    
    async def run_comprehensive_image_upload_test(self) -> Dict:
        """Run complete image upload investigation"""
        print("🚨 STARTING URGENT IMAGE UPLOAD INVESTIGATION")
        print("=" * 80)
        print("USER REPORT: 'Image upload error: Error: Upload failed: 403'")
        print("LOCATION: Admin Panel > Ads Manager")
        print("INVESTIGATING: Image upload endpoint authentication and functionality")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Step 1: Authenticate as admin
            auth_success = await self.authenticate_admin()
            if not auth_success:
                return {
                    "investigation_timestamp": datetime.now().isoformat(),
                    "error": "Admin authentication failed - cannot proceed with investigation",
                    "user_issue_reproduced": False
                }
            
            # Step 2: Test endpoint accessibility
            endpoint_access = await self.test_upload_image_endpoint_access()
            
            # Step 3: Test actual image upload
            image_upload = await self.test_image_upload_with_multipart()
            
            # Step 4: Test wrong endpoint call (common frontend issue)
            wrong_endpoint = await self.test_wrong_endpoint_call()
            
            # Step 5: Test CORS
            cors_test = await self.test_cors_preflight()
            
            # Step 6: Test directory permissions
            directory_permissions = await self.test_directory_permissions()
            
            # Step 7: Test admin role verification
            admin_role = await self.test_admin_role_verification()
            
            # Compile investigation results
            investigation_results = {
                "investigation_timestamp": datetime.now().isoformat(),
                "user_report": "Image upload error: Error: Upload failed: 403",
                "location": "Admin Panel > Ads Manager",
                "admin_authentication": self.test_results.get("admin_authentication", {}),
                "endpoint_accessibility": endpoint_access,
                "image_upload_test": image_upload,
                "wrong_endpoint_test": wrong_endpoint,
                "cors_test": cors_test,
                "directory_permissions": directory_permissions,
                "admin_role_verification": admin_role
            }
            
            # Analyze findings
            issue_reproduced = image_upload.get("matches_user_issue", False)
            
            # Determine root cause
            root_causes = []
            solutions = []
            
            if not admin_role.get("success", False):
                root_causes.append("Admin role verification failed")
                solutions.append("Check user admin permissions in database")
            
            if image_upload.get("status") == 403:
                root_causes.append("403 Forbidden error on correct endpoint")
                if "admin" in str(image_upload.get("error", "")).lower():
                    solutions.append("Verify admin role assignment")
                else:
                    solutions.append("Check authentication token validity")
            
            if wrong_endpoint.get("recommendation"):
                root_causes.append("Frontend calling wrong endpoint")
                solutions.append(wrong_endpoint["recommendation"])
            
            if cors_test.get("potential_cors_issue", False):
                root_causes.append("CORS configuration issue")
                solutions.append("Fix CORS headers for image upload endpoint")
            
            if directory_permissions.get("is_permission_error", False):
                root_causes.append("File system permission issue")
                solutions.append("Fix upload directory permissions")
            
            if not root_causes:
                if image_upload.get("success", False):
                    root_causes.append("No issues found - upload working correctly")
                    solutions.append("Check frontend implementation and error handling")
                else:
                    root_causes.append("Unknown issue")
                    solutions.append("Review server logs for detailed error information")
            
            investigation_results["analysis"] = {
                "issue_reproduced": issue_reproduced,
                "root_causes": root_causes,
                "recommended_solutions": solutions,
                "critical_findings": [
                    f"Admin authentication: {'✅ Working' if auth_success else '❌ Failed'}",
                    f"Image upload endpoint: {'✅ Working' if image_upload.get('success') else '❌ Failed'}",
                    f"Admin role verification: {'✅ Working' if admin_role.get('success') else '❌ Failed'}",
                    f"CORS configuration: {'✅ Working' if not cors_test.get('potential_cors_issue') else '❌ Issues detected'}",
                    f"Directory permissions: {'✅ Working' if directory_permissions.get('success') else '❌ Issues detected'}"
                ],
                "investigation_status": "COMPLETE",
                "user_issue_status": "REPRODUCED" if issue_reproduced else "NOT_REPRODUCED"
            }
            
            return investigation_results
            
        finally:
            await self.cleanup()


async def main():
    """Run the image upload investigation"""
    tester = ImageUploadTester()
    results = await tester.run_comprehensive_image_upload_test()
    
    print("\n" + "=" * 80)
    print("🔍 IMAGE UPLOAD INVESTIGATION RESULTS")
    print("=" * 80)
    
    analysis = results.get("analysis", {})
    
    print(f"📅 Investigation completed: {results.get('investigation_timestamp', 'Unknown')}")
    print(f"🎯 User issue reproduced: {analysis.get('issue_reproduced', False)}")
    print(f"📊 Investigation status: {analysis.get('investigation_status', 'Unknown')}")
    
    print("\n🔍 CRITICAL FINDINGS:")
    for finding in analysis.get("critical_findings", []):
        print(f"  {finding}")
    
    print("\n🚨 ROOT CAUSES IDENTIFIED:")
    for cause in analysis.get("root_causes", []):
        print(f"  • {cause}")
    
    print("\n💡 RECOMMENDED SOLUTIONS:")
    for solution in analysis.get("recommended_solutions", []):
        print(f"  • {solution}")
    
    # Print detailed results for debugging
    print("\n📋 DETAILED TEST RESULTS:")
    
    # Admin Authentication
    auth_result = results.get("admin_authentication", {})
    print(f"  🔐 Admin Authentication: {'✅ Success' if auth_result.get('success') else '❌ Failed'}")
    if not auth_result.get("success"):
        print(f"    Error: {auth_result.get('error', 'Unknown')}")
    
    # Image Upload Test
    upload_result = results.get("image_upload_test", {})
    print(f"  📤 Image Upload: {'✅ Success' if upload_result.get('success') else '❌ Failed'}")
    if not upload_result.get("success"):
        print(f"    Status: {upload_result.get('status', 'Unknown')}")
        print(f"    Error: {upload_result.get('error', 'Unknown')}")
        if upload_result.get("error_analysis"):
            print(f"    Likely causes: {', '.join(upload_result['error_analysis'].get('likely_causes', []))}")
    
    # Endpoint Access
    endpoint_result = results.get("endpoint_accessibility", {})
    print(f"  🔍 Endpoint Access: {'✅ Found' if endpoint_result.get('success') else '❌ Issues'}")
    if endpoint_result.get("working_endpoint"):
        print(f"    Working endpoint: {endpoint_result['working_endpoint']}")
    
    # CORS Test
    cors_result = results.get("cors_test", {})
    print(f"  🌐 CORS: {'✅ Working' if cors_result.get('success') else '❌ Issues'}")
    
    # Directory Permissions
    dir_result = results.get("directory_permissions", {})
    print(f"  📁 Directory Permissions: {'✅ Working' if dir_result.get('success') else '❌ Issues'}")
    
    print("\n" + "=" * 80)
    print("🎯 INVESTIGATION COMPLETE")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())