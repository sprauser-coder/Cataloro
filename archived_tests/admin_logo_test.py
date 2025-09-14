#!/usr/bin/env python3
"""
Admin Logo Implementation Testing
Testing admin logo API endpoints, database structure, and frontend integration
"""

import asyncio
import aiohttp
import time
import json
import base64
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://marketplace-fix-9.preview.emergentagent.com/api"

class AdminLogoTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.admin_user_id = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None, files: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data and not files:
                request_kwargs['json'] = data
            if headers:
                request_kwargs['headers'] = headers
            if files:
                # For file uploads, use FormData
                form_data = aiohttp.FormData()
                if data:
                    for key, value in data.items():
                        form_data.add_field(key, str(value))
                for key, file_data in files.items():
                    form_data.add_field(key, file_data, filename='logo.png', content_type='image/png')
                request_kwargs['data'] = form_data
            
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
    
    async def authenticate_admin(self) -> Dict:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin user...")
        
        login_data = {
            "email": "admin@cataloro.com",
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            self.admin_token = result["data"].get("token", "")
            self.admin_user_id = user_data.get("id")
            
            print(f"  ✅ Admin authentication successful")
            print(f"  👤 Admin ID: {self.admin_user_id}")
            print(f"  🔑 Token received: {bool(self.admin_token)}")
            
            return {
                "test_name": "Admin Authentication",
                "success": True,
                "admin_id": self.admin_user_id,
                "token_received": bool(self.admin_token),
                "response_time_ms": result["response_time_ms"]
            }
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Admin Authentication",
                "success": False,
                "error": result.get("error", "Authentication failed"),
                "status": result["status"]
            }
    
    async def test_admin_logo_get_endpoint(self) -> Dict:
        """Test GET /api/admin/logo endpoint"""
        print("🖼️ Testing GET /api/admin/logo endpoint...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"} if self.admin_token else {}
        result = await self.make_request("/admin/logo", "GET", headers=headers)
        
        print(f"  📊 Status: {result['status']}")
        print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
        
        if result["success"]:
            data = result["data"]
            print(f"  ✅ Endpoint exists and responds successfully")
            print(f"  📄 Response data: {json.dumps(data, indent=2)}")
            
            # Check response structure
            has_logo_url = "logo_url" in data if isinstance(data, dict) else False
            logo_url_value = data.get("logo_url") if isinstance(data, dict) else None
            
            return {
                "test_name": "GET Admin Logo Endpoint",
                "success": True,
                "endpoint_exists": True,
                "response_time_ms": result["response_time_ms"],
                "response_data": data,
                "has_logo_url_field": has_logo_url,
                "logo_url_value": logo_url_value,
                "logo_url_is_null": logo_url_value is None,
                "response_structure_valid": isinstance(data, dict)
            }
        else:
            error_msg = result.get("error", "Unknown error")
            print(f"  ❌ Endpoint failed: {error_msg}")
            
            # Check if endpoint exists but has issues vs doesn't exist
            endpoint_exists = result["status"] != 404
            
            return {
                "test_name": "GET Admin Logo Endpoint",
                "success": False,
                "endpoint_exists": endpoint_exists,
                "error": error_msg,
                "status": result["status"],
                "response_time_ms": result["response_time_ms"]
            }
    
    async def test_site_settings_database_structure(self) -> Dict:
        """Test site_settings collection structure by checking admin endpoints"""
        print("🗄️ Testing site_settings database structure...")
        
        # Try to access site settings through admin endpoints
        headers = {"Authorization": f"Bearer {self.admin_token}"} if self.admin_token else {}
        
        # Test various potential admin endpoints for site settings
        endpoints_to_test = [
            "/admin/settings",
            "/admin/site-settings", 
            "/admin/site_settings",
            "/admin/config",
            "/admin/logo/settings"
        ]
        
        endpoint_results = []
        
        for endpoint in endpoints_to_test:
            print(f"  Testing endpoint: {endpoint}")
            result = await self.make_request(endpoint, "GET", headers=headers)
            
            endpoint_results.append({
                "endpoint": endpoint,
                "success": result["success"],
                "status": result["status"],
                "exists": result["status"] != 404,
                "response_data": result["data"] if result["success"] else None,
                "error": result.get("error") if not result["success"] else None
            })
            
            if result["success"]:
                print(f"    ✅ {endpoint} exists and responds")
                print(f"    📄 Data: {json.dumps(result['data'], indent=4)}")
            elif result["status"] == 404:
                print(f"    ❌ {endpoint} not found (404)")
            else:
                print(f"    ⚠️ {endpoint} error: {result.get('error')}")
        
        # Check if any endpoints exist
        existing_endpoints = [r for r in endpoint_results if r["exists"]]
        successful_endpoints = [r for r in endpoint_results if r["success"]]
        
        return {
            "test_name": "Site Settings Database Structure",
            "total_endpoints_tested": len(endpoints_to_test),
            "existing_endpoints": len(existing_endpoints),
            "successful_endpoints": len(successful_endpoints),
            "any_settings_endpoint_exists": len(existing_endpoints) > 0,
            "any_settings_endpoint_working": len(successful_endpoints) > 0,
            "detailed_results": endpoint_results
        }
    
    async def test_logo_upload_functionality(self) -> Dict:
        """Test logo upload functionality"""
        print("📤 Testing logo upload functionality...")
        
        if not self.admin_token:
            return {
                "test_name": "Logo Upload Functionality",
                "success": False,
                "error": "No admin token available"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a simple test image (1x1 PNG)
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        test_image_data = base64.b64decode(test_image_base64)
        
        # Test different potential upload endpoints
        upload_endpoints = [
            "/admin/logo/upload",
            "/admin/logo", 
            "/admin/settings/logo",
            "/admin/site-settings/logo"
        ]
        
        upload_results = []
        
        for endpoint in upload_endpoints:
            print(f"  Testing upload endpoint: {endpoint}")
            
            # Try POST with file upload
            files = {"logo": test_image_data}
            result = await self.make_request(endpoint, "POST", headers=headers, files=files)
            
            upload_results.append({
                "endpoint": endpoint,
                "method": "POST",
                "success": result["success"],
                "status": result["status"],
                "exists": result["status"] != 404,
                "response_data": result["data"] if result["success"] else None,
                "error": result.get("error") if not result["success"] else None
            })
            
            if result["success"]:
                print(f"    ✅ {endpoint} upload successful")
                print(f"    📄 Response: {json.dumps(result['data'], indent=4)}")
            elif result["status"] == 404:
                print(f"    ❌ {endpoint} not found (404)")
            else:
                print(f"    ⚠️ {endpoint} error: {result.get('error')}")
            
            # Also try PUT method
            result_put = await self.make_request(endpoint, "PUT", headers=headers, files=files)
            
            upload_results.append({
                "endpoint": endpoint,
                "method": "PUT", 
                "success": result_put["success"],
                "status": result_put["status"],
                "exists": result_put["status"] != 404,
                "response_data": result_put["data"] if result_put["success"] else None,
                "error": result_put.get("error") if not result_put["success"] else None
            })
            
            if result_put["success"]:
                print(f"    ✅ {endpoint} PUT upload successful")
        
        # Check results
        existing_endpoints = [r for r in upload_results if r["exists"]]
        successful_uploads = [r for r in upload_results if r["success"]]
        
        return {
            "test_name": "Logo Upload Functionality",
            "total_upload_attempts": len(upload_results),
            "existing_upload_endpoints": len(existing_endpoints),
            "successful_uploads": len(successful_uploads),
            "any_upload_endpoint_exists": len(existing_endpoints) > 0,
            "any_upload_working": len(successful_uploads) > 0,
            "detailed_results": upload_results
        }
    
    async def test_database_direct_inspection(self) -> Dict:
        """Test database inspection through available admin endpoints"""
        print("🔍 Testing database inspection for logo data...")
        
        if not self.admin_token:
            return {
                "test_name": "Database Direct Inspection",
                "success": False,
                "error": "No admin token available"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test admin dashboard to see if it shows any logo-related data
        print("  Checking admin dashboard for logo data...")
        dashboard_result = await self.make_request("/admin/dashboard", "GET", headers=headers)
        
        dashboard_has_logo_data = False
        if dashboard_result["success"]:
            dashboard_data = dashboard_result["data"]
            # Check if dashboard contains any logo-related fields
            dashboard_str = json.dumps(dashboard_data).lower()
            dashboard_has_logo_data = any(keyword in dashboard_str for keyword in ["logo", "site_settings", "branding"])
            print(f"    Dashboard logo data found: {dashboard_has_logo_data}")
        
        # Test performance endpoint to see database collections
        print("  Checking performance metrics for database collections...")
        performance_result = await self.make_request("/admin/performance", "GET", headers=headers)
        
        site_settings_collection_exists = False
        if performance_result["success"]:
            performance_data = performance_result["data"]
            collections = performance_data.get("collections", {})
            site_settings_collection_exists = "site_settings" in collections
            print(f"    site_settings collection exists: {site_settings_collection_exists}")
            
            if site_settings_collection_exists:
                site_settings_info = collections["site_settings"]
                print(f"    site_settings collection info: {json.dumps(site_settings_info, indent=4)}")
        
        # Try to access any users endpoint to see if logo data is stored in user profiles
        print("  Checking if logo data is stored in user profiles...")
        users_result = await self.make_request("/admin/users", "GET", headers=headers)
        
        user_logo_data = False
        if users_result["success"]:
            users_data = users_result["data"]
            if users_data and len(users_data) > 0:
                # Check first user for logo-related fields
                first_user = users_data[0]
                user_str = json.dumps(first_user).lower()
                user_logo_data = any(keyword in user_str for keyword in ["logo", "avatar", "profile_image"])
                print(f"    User profile logo data found: {user_logo_data}")
        
        return {
            "test_name": "Database Direct Inspection",
            "dashboard_accessible": dashboard_result["success"],
            "dashboard_has_logo_data": dashboard_has_logo_data,
            "performance_metrics_accessible": performance_result["success"],
            "site_settings_collection_exists": site_settings_collection_exists,
            "users_endpoint_accessible": users_result["success"],
            "user_profiles_have_logo_data": user_logo_data,
            "any_logo_data_found": dashboard_has_logo_data or user_logo_data
        }
    
    async def test_frontend_logo_url_access(self) -> Dict:
        """Test if frontend can access logo through expected URLs"""
        print("🌐 Testing frontend logo URL access...")
        
        # Test common logo URL patterns
        logo_url_patterns = [
            "/api/admin/logo",
            "/api/logo",
            "/api/site/logo", 
            "/api/settings/logo",
            "/uploads/logo.png",
            "/static/logo.png",
            "/api/admin/logo/current"
        ]
        
        url_test_results = []
        
        for url_pattern in logo_url_patterns:
            print(f"  Testing URL: {url_pattern}")
            result = await self.make_request(url_pattern, "GET")
            
            url_test_results.append({
                "url": url_pattern,
                "success": result["success"],
                "status": result["status"],
                "exists": result["status"] != 404,
                "response_time_ms": result["response_time_ms"],
                "content_type": "unknown",  # We'd need to check headers for this
                "error": result.get("error") if not result["success"] else None
            })
            
            if result["success"]:
                print(f"    ✅ {url_pattern} accessible")
            elif result["status"] == 404:
                print(f"    ❌ {url_pattern} not found (404)")
            else:
                print(f"    ⚠️ {url_pattern} error: {result.get('error')}")
        
        # Check CORS and network issues by testing a known working endpoint
        print("  Testing CORS and network connectivity...")
        health_result = await self.make_request("/health", "GET")
        
        network_working = health_result["success"]
        
        accessible_urls = [r for r in url_test_results if r["success"]]
        existing_urls = [r for r in url_test_results if r["exists"]]
        
        return {
            "test_name": "Frontend Logo URL Access",
            "total_urls_tested": len(logo_url_patterns),
            "accessible_urls": len(accessible_urls),
            "existing_urls": len(existing_urls),
            "network_connectivity_working": network_working,
            "any_logo_url_accessible": len(accessible_urls) > 0,
            "cors_issues_detected": not network_working,
            "detailed_url_results": url_test_results
        }
    
    async def test_logo_implementation_completeness(self) -> Dict:
        """Test overall logo implementation completeness"""
        print("🎯 Testing logo implementation completeness...")
        
        # Run a comprehensive check of all logo-related functionality
        completeness_checks = []
        
        # Check 1: Admin logo endpoint exists
        logo_endpoint_result = await self.test_admin_logo_get_endpoint()
        completeness_checks.append({
            "check": "Admin Logo Endpoint Exists",
            "passed": logo_endpoint_result.get("endpoint_exists", False),
            "details": f"Status: {logo_endpoint_result.get('status', 'Unknown')}"
        })
        
        # Check 2: Logo endpoint returns valid structure
        completeness_checks.append({
            "check": "Logo Endpoint Returns Valid Structure", 
            "passed": logo_endpoint_result.get("response_structure_valid", False),
            "details": f"Has logo_url field: {logo_endpoint_result.get('has_logo_url_field', False)}"
        })
        
        # Check 3: Database has logo storage capability
        db_structure_result = await self.test_site_settings_database_structure()
        completeness_checks.append({
            "check": "Database Has Logo Storage",
            "passed": db_structure_result.get("any_settings_endpoint_working", False),
            "details": f"Settings endpoints working: {db_structure_result.get('successful_endpoints', 0)}"
        })
        
        # Check 4: Logo upload functionality exists
        upload_result = await self.test_logo_upload_functionality()
        completeness_checks.append({
            "check": "Logo Upload Functionality Exists",
            "passed": upload_result.get("any_upload_endpoint_exists", False),
            "details": f"Upload endpoints found: {upload_result.get('existing_upload_endpoints', 0)}"
        })
        
        # Check 5: Frontend can access logo URLs
        frontend_result = await self.test_frontend_logo_url_access()
        completeness_checks.append({
            "check": "Frontend Logo URL Access",
            "passed": frontend_result.get("any_logo_url_accessible", False),
            "details": f"Accessible URLs: {frontend_result.get('accessible_urls', 0)}"
        })
        
        # Calculate overall completeness
        passed_checks = [c for c in completeness_checks if c["passed"]]
        completeness_percentage = (len(passed_checks) / len(completeness_checks)) * 100
        
        # Determine implementation status
        if completeness_percentage >= 80:
            implementation_status = "MOSTLY_COMPLETE"
        elif completeness_percentage >= 50:
            implementation_status = "PARTIALLY_IMPLEMENTED"
        elif completeness_percentage >= 20:
            implementation_status = "BASIC_STRUCTURE_EXISTS"
        else:
            implementation_status = "NOT_IMPLEMENTED"
        
        return {
            "test_name": "Logo Implementation Completeness",
            "total_checks": len(completeness_checks),
            "passed_checks": len(passed_checks),
            "completeness_percentage": completeness_percentage,
            "implementation_status": implementation_status,
            "detailed_checks": completeness_checks,
            "critical_issues": [c for c in completeness_checks if not c["passed"]]
        }
    
    async def run_comprehensive_logo_test(self) -> Dict:
        """Run all admin logo tests"""
        print("🚀 Starting Cataloro Admin Logo Implementation Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Step 1: Authenticate as admin
            auth_result = await self.authenticate_admin()
            if not auth_result["success"]:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "overall_status": "FAILED",
                    "error": "Admin authentication failed",
                    "authentication": auth_result
                }
            
            # Step 2: Test admin logo GET endpoint
            logo_get_result = await self.test_admin_logo_get_endpoint()
            
            # Step 3: Test database structure
            db_structure_result = await self.test_site_settings_database_structure()
            
            # Step 4: Test logo upload functionality
            upload_result = await self.test_logo_upload_functionality()
            
            # Step 5: Test database inspection
            db_inspection_result = await self.test_database_direct_inspection()
            
            # Step 6: Test frontend URL access
            frontend_result = await self.test_frontend_logo_url_access()
            
            # Step 7: Test overall completeness
            completeness_result = await self.test_logo_implementation_completeness()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "authentication": auth_result,
                "admin_logo_get_endpoint": logo_get_result,
                "site_settings_database_structure": db_structure_result,
                "logo_upload_functionality": upload_result,
                "database_direct_inspection": db_inspection_result,
                "frontend_logo_url_access": frontend_result,
                "logo_implementation_completeness": completeness_result
            }
            
            # Determine overall status
            critical_tests = [
                logo_get_result.get("endpoint_exists", False),
                db_structure_result.get("any_settings_endpoint_exists", False) or db_inspection_result.get("any_logo_data_found", False),
                frontend_result.get("network_connectivity_working", False)
            ]
            
            overall_success_rate = sum(critical_tests) / len(critical_tests) * 100
            
            if overall_success_rate >= 66:
                overall_status = "PARTIALLY_WORKING"
            elif overall_success_rate >= 33:
                overall_status = "BASIC_FUNCTIONALITY_EXISTS"
            else:
                overall_status = "MAJOR_ISSUES_FOUND"
            
            all_results["summary"] = {
                "overall_status": overall_status,
                "overall_success_rate": overall_success_rate,
                "admin_logo_endpoint_exists": logo_get_result.get("endpoint_exists", False),
                "admin_logo_endpoint_working": logo_get_result.get("success", False),
                "database_logo_storage_exists": db_structure_result.get("any_settings_endpoint_exists", False),
                "logo_upload_capability_exists": upload_result.get("any_upload_endpoint_exists", False),
                "frontend_can_access_logo": frontend_result.get("any_logo_url_accessible", False),
                "implementation_completeness": completeness_result.get("completeness_percentage", 0),
                "critical_issues_found": len(completeness_result.get("critical_issues", [])),
                "network_connectivity_working": frontend_result.get("network_connectivity_working", False)
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Run the admin logo testing"""
    tester = AdminLogoTester()
    results = await tester.run_comprehensive_logo_test()
    
    print("\n" + "=" * 70)
    print("🎯 ADMIN LOGO TESTING RESULTS SUMMARY")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"Overall Status: {summary.get('overall_status', 'UNKNOWN')}")
    print(f"Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"Implementation Completeness: {summary.get('implementation_completeness', 0):.1f}%")
    
    print("\n🔍 Key Findings:")
    print(f"  • Admin logo endpoint exists: {'✅' if summary.get('admin_logo_endpoint_exists') else '❌'}")
    print(f"  • Admin logo endpoint working: {'✅' if summary.get('admin_logo_endpoint_working') else '❌'}")
    print(f"  • Database logo storage exists: {'✅' if summary.get('database_logo_storage_exists') else '❌'}")
    print(f"  • Logo upload capability exists: {'✅' if summary.get('logo_upload_capability_exists') else '❌'}")
    print(f"  • Frontend can access logo: {'✅' if summary.get('frontend_can_access_logo') else '❌'}")
    print(f"  • Network connectivity working: {'✅' if summary.get('network_connectivity_working') else '❌'}")
    
    critical_issues = summary.get('critical_issues_found', 0)
    if critical_issues > 0:
        print(f"\n⚠️ Critical Issues Found: {critical_issues}")
    
    print(f"\n📄 Full results saved to test output")
    
    # Save detailed results
    with open('/app/admin_logo_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())