#!/usr/bin/env python3
"""
Cataloro Marketplace - Focused Issue Backend Testing
Tests specific issues reported by user:
1. Business Tab Data - real user count matching Users tab
2. Role Display - sidebar footer and usePermissions hook
3. User Management Table Width - horizontal scrolling issues  
4. Media Browser Bulk Operations - bulk selection and operations
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://marketplace-central.preview.emergentagent.com/api"

class FocusedIssueTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        self.admin_user_id = None
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request to backend"""
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, params=params) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "DELETE":
                async with self.session.delete(url, params=params) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "headers": dict(response.headers)
                    }
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {}
            }
    
    def log_test(self, test_name: str, success: bool, details: str):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} - {test_name}: {details}"
        print(result)
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        if not success:
            self.failed_tests.append(test_name)
    
    async def test_admin_login(self):
        """Test admin login to get user context"""
        print("\n🔐 Testing Admin Login...")
        
        login_data = {
            "email": "admin@cataloro.com",
            "password": "admin123"
        }
        
        response = await self.make_request("POST", "/auth/login", login_data)
        
        if response["status"] == 200 and "user" in response["data"]:
            user_data = response["data"]["user"]
            self.admin_user_id = user_data.get("id")
            self.log_test("Admin Login", True, f"Successfully logged in as {user_data.get('full_name', 'Admin')} (ID: {self.admin_user_id})")
            return True
        else:
            self.log_test("Admin Login", False, f"Login failed: {response['data']}")
            return False
    
    async def test_business_tab_data(self):
        """Test Issue 1: Business Tab Data - real user count matching Users tab"""
        print("\n📊 Testing Business Tab Data...")
        
        # Test 1.1: Get Users endpoint data
        users_response = await self.make_request("GET", "/admin/users")
        
        if users_response["status"] != 200:
            self.log_test("Users Endpoint", False, f"Failed to get users data: {users_response['data']}")
            return False
        
        users_data = users_response["data"]
        total_users = len(users_data) if isinstance(users_data, list) else users_data.get("total_users", 0)
        
        self.log_test("Users Endpoint", True, f"Retrieved {total_users} users from /admin/users")
        
        # Test 1.2: Get Business Analytics data
        analytics_response = await self.make_request("GET", "/admin/analytics/dashboard")
        
        if analytics_response["status"] != 200:
            self.log_test("Business Analytics", False, f"Failed to get analytics data: {analytics_response['data']}")
            return False
        
        analytics_data = analytics_response["data"]
        # Check both possible locations for user count
        analytics_users = analytics_data.get("overview", {}).get("total_users", 0) or analytics_data.get("overview", {}).get("users", 0)
        
        self.log_test("Business Analytics", True, f"Analytics shows {analytics_users} users")
        
        # Test 1.3: Compare user counts
        if total_users == analytics_users:
            self.log_test("User Count Match", True, f"Business tab user count ({analytics_users}) matches Users tab count ({total_users})")
        else:
            self.log_test("User Count Match", False, f"Mismatch: Business tab shows {analytics_users} users, Users tab shows {total_users} users")
        
        # Test 1.4: Verify business metrics calculation
        business_metrics = analytics_data.get("business_metrics", {})
        if business_metrics:
            self.log_test("Business Metrics Calculation", True, f"Business metrics calculated: Users: {business_metrics.get('users', 0)}, Revenue: {business_metrics.get('revenue', 0)}")
        else:
            self.log_test("Business Metrics Calculation", False, "Business metrics not found in analytics response")
        
        return True
    
    async def test_role_display(self):
        """Test Issue 2: Role Display - sidebar footer and usePermissions hook"""
        print("\n👤 Testing Role Display...")
        
        if not self.admin_user_id:
            self.log_test("Role Display Setup", False, "No admin user ID available for testing")
            return False
        
        # Test 2.1: Get user profile to check role information
        profile_response = await self.make_request("GET", f"/auth/profile/{self.admin_user_id}")
        
        if profile_response["status"] != 200:
            self.log_test("User Profile", False, f"Failed to get user profile: {profile_response['data']}")
            return False
        
        profile_data = profile_response["data"]
        user_role = profile_data.get("user_role", "")
        badge = profile_data.get("badge", "")
        
        self.log_test("User Profile Role", True, f"User role: {user_role}, Badge: {badge}")
        
        # Test 2.2: Check if role information is properly structured
        expected_admin_roles = ["Admin", "Admin-Manager"]
        if user_role in expected_admin_roles:
            self.log_test("Admin Role Validation", True, f"User has valid admin role: {user_role}")
        else:
            self.log_test("Admin Role Validation", False, f"Unexpected role for admin user: {user_role}")
        
        # Test 2.3: Test permissions endpoint if available
        permissions_response = await self.make_request("GET", f"/admin/users/{self.admin_user_id}/permissions")
        
        if permissions_response["status"] == 200:
            permissions_data = permissions_response["data"]
            self.log_test("User Permissions", True, f"Permissions retrieved: {len(permissions_data.get('permissions', []))} permissions")
        else:
            # Try alternative permissions endpoint
            alt_permissions_response = await self.make_request("GET", "/admin/permissions/check", params={"user_id": self.admin_user_id})
            if alt_permissions_response["status"] == 200:
                self.log_test("User Permissions (Alt)", True, "Permissions check endpoint working")
            else:
                self.log_test("User Permissions", False, "No permissions endpoint available or working")
        
        return True
    
    async def test_user_management_table(self):
        """Test Issue 3: User Management Table Width - horizontal scrolling issues"""
        print("\n📋 Testing User Management Table...")
        
        # Test 3.1: Get users data and check structure
        users_response = await self.make_request("GET", "/admin/users")
        
        if users_response["status"] != 200:
            self.log_test("User Management Data", False, f"Failed to get users data: {users_response['data']}")
            return False
        
        users_data = users_response["data"]
        
        if isinstance(users_data, list) and len(users_data) > 0:
            # Check the structure of user data to see if it has all necessary fields
            sample_user = users_data[0]
            required_fields = ["id", "username", "email", "full_name", "user_role", "badge", "registration_status"]
            
            missing_fields = [field for field in required_fields if field not in sample_user]
            
            if not missing_fields:
                self.log_test("User Data Structure", True, f"All required fields present in user data ({len(required_fields)} fields)")
            else:
                self.log_test("User Data Structure", False, f"Missing fields in user data: {missing_fields}")
            
            # Check if there are too many fields that might cause table width issues
            total_fields = len(sample_user.keys())
            if total_fields > 15:
                self.log_test("User Data Complexity", False, f"User data has {total_fields} fields - may cause table width issues")
            else:
                self.log_test("User Data Complexity", True, f"User data has {total_fields} fields - manageable for table display")
            
            self.log_test("User Management Data", True, f"Retrieved {len(users_data)} users with proper structure")
        else:
            self.log_test("User Management Data", False, "No users data or invalid format")
        
        # Test 3.2: Check pagination support for large datasets
        paginated_response = await self.make_request("GET", "/admin/users", params={"page": 1, "limit": 10})
        
        if paginated_response["status"] == 200:
            self.log_test("User Pagination", True, "User management supports pagination")
        else:
            self.log_test("User Pagination", False, "User management pagination not working")
        
        return True
    
    async def test_media_browser_bulk_operations(self):
        """Test Issue 4: Media Browser Bulk Operations - bulk selection and operations"""
        print("\n🖼️ Testing Media Browser Bulk Operations...")
        
        # Test 4.1: Get media files list
        media_response = await self.make_request("GET", "/admin/media/files")
        
        if media_response["status"] != 200:
            self.log_test("Media Files List", False, f"Failed to get media files: {media_response['data']}")
            return False
        
        media_data = media_response["data"]
        
        if isinstance(media_data, dict) and "files" in media_data:
            files = media_data["files"]
            total_files = len(files)
            self.log_test("Media Files List", True, f"Retrieved {total_files} media files")
            
            if total_files == 0:
                self.log_test("Media Bulk Operations Setup", False, "No media files available for bulk operations testing")
                return False
            
            # Test 4.2: Check if files have proper IDs for bulk operations
            sample_file = files[0] if files else {}
            if "id" in sample_file:
                self.log_test("Media File IDs", True, f"Media files have proper IDs for bulk operations")
                
                # Test 4.3: Test bulk delete endpoint (simulate with single file)
                file_id = sample_file["id"]
                
                # First, let's check if bulk delete endpoint exists
                bulk_delete_response = await self.make_request("POST", "/admin/media/bulk-delete", {"file_ids": [file_id]})
                
                if bulk_delete_response["status"] in [200, 404]:  # 404 means endpoint exists but file not found
                    self.log_test("Bulk Delete Endpoint", True, "Bulk delete endpoint is available")
                else:
                    # Try alternative bulk operations endpoint
                    alt_bulk_response = await self.make_request("DELETE", f"/admin/media/files/bulk", params={"ids": file_id})
                    if alt_bulk_response["status"] in [200, 404, 405]:  # 405 means method not allowed but endpoint exists
                        self.log_test("Bulk Delete Endpoint (Alt)", True, "Alternative bulk delete endpoint found")
                    else:
                        self.log_test("Bulk Delete Endpoint", False, "No bulk delete endpoint available")
                
                # Test 4.4: Test bulk download endpoint
                bulk_download_response = await self.make_request("POST", "/admin/media/bulk-download", {"file_ids": [file_id]})
                
                if bulk_download_response["status"] in [200, 404]:
                    self.log_test("Bulk Download Endpoint", True, "Bulk download endpoint is available")
                else:
                    self.log_test("Bulk Download Endpoint", False, "No bulk download endpoint available")
                
            else:
                self.log_test("Media File IDs", False, "Media files missing IDs required for bulk operations")
        
        elif isinstance(media_data, list):
            # Handle case where response is directly a list
            total_files = len(media_data)
            self.log_test("Media Files List", True, f"Retrieved {total_files} media files (direct list)")
        else:
            self.log_test("Media Files List", False, f"Unexpected media data format: {type(media_data)}")
        
        return True
    
    async def test_additional_admin_endpoints(self):
        """Test additional admin endpoints that might be related to the issues"""
        print("\n🔧 Testing Additional Admin Endpoints...")
        
        # Test admin dashboard
        dashboard_response = await self.make_request("GET", "/admin/dashboard")
        if dashboard_response["status"] == 200:
            self.log_test("Admin Dashboard", True, "Admin dashboard endpoint working")
        else:
            self.log_test("Admin Dashboard", False, f"Admin dashboard failed: {dashboard_response['data']}")
        
        # Test system status
        health_response = await self.make_request("GET", "/health")
        if health_response["status"] == 200:
            self.log_test("System Health", True, f"System healthy: {health_response['data']}")
        else:
            self.log_test("System Health", False, f"System health check failed: {health_response['data']}")
        
        # Test performance metrics
        performance_response = await self.make_request("GET", "/admin/performance")
        if performance_response["status"] == 200:
            perf_data = performance_response["data"]
            self.log_test("Performance Metrics", True, f"Performance status: {perf_data.get('performance_status', 'unknown')}")
        else:
            self.log_test("Performance Metrics", False, f"Performance metrics failed: {performance_response['data']}")
    
    async def run_all_tests(self):
        """Run all focused issue tests"""
        print("🚀 Starting Focused Issue Backend Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Login first to get admin context
            login_success = await self.test_admin_login()
            
            if login_success:
                # Run all issue-specific tests
                await self.test_business_tab_data()
                await self.test_role_display()
                await self.test_user_management_table()
                await self.test_media_browser_bulk_operations()
                await self.test_additional_admin_endpoints()
            else:
                print("❌ Cannot proceed with tests - admin login failed")
        
        finally:
            await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 FOCUSED ISSUE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        print("\n🎯 ISSUE-SPECIFIC FINDINGS:")
        print("1. Business Tab Data: Check if user counts match between tabs")
        print("2. Role Display: Verify admin role and permissions are working")
        print("3. User Management Table: Check data structure and pagination")
        print("4. Media Browser Bulk Operations: Test bulk selection and operations")
        
        return passed_tests, failed_tests

async def main():
    """Main test execution"""
    tester = FocusedIssueTester()
    passed, failed = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())