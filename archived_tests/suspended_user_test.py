#!/usr/bin/env python3
"""
Cataloro Marketplace Suspended User Protection Testing
Testing comprehensive suspended user protection functionality
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://mobilefixed-market.preview.emergentagent.com/api"

# Test User Configuration (using demo_user_1 as requested)
TEST_USER_EMAIL = "demo@cataloro.com"
TEST_USER_PASSWORD = "demo_password"
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

class SuspendedUserProtectionTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.admin_token = None
        self.test_user_id = None
        self.test_user_token = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
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
    
    async def setup_admin_access(self) -> bool:
        """Setup admin access for user management operations"""
        print("🔐 Setting up admin access...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            print(f"  ✅ Admin login successful")
            return True
        else:
            print(f"  ❌ Admin login failed: {result.get('error', 'Unknown error')}")
            return False
    
    async def setup_test_user(self) -> bool:
        """Setup test user and get their ID"""
        print("👤 Setting up test user...")
        
        # First, login as test user to get their ID
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            self.test_user_id = user_data.get("id")
            self.test_user_token = result["data"].get("token", "")
            
            print(f"  ✅ Test user login successful")
            print(f"  👤 User ID: {self.test_user_id}")
            print(f"  📧 Email: {user_data.get('email')}")
            return True
        else:
            print(f"  ❌ Test user login failed: {result.get('error', 'Unknown error')}")
            return False
    
    async def test_login_prevention_for_suspended_users(self) -> Dict:
        """Test 1: Login Prevention for Suspended Users"""
        print("🚫 Testing login prevention for suspended users...")
        
        if not self.admin_token or not self.test_user_id:
            return {
                "test_name": "Login Prevention for Suspended Users",
                "error": "Admin token or test user ID not available"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        test_results = []
        
        # Step 1: Suspend the test user
        print("  Step 1: Suspending test user...")
        suspend_result = await self.make_request(f"/admin/users/{self.test_user_id}/suspend", "PUT", headers=headers)
        
        if suspend_result["success"]:
            suspended_user = suspend_result["data"].get("user", {})
            is_suspended = not suspended_user.get("is_active", True)
            
            test_results.append({
                "step": "Suspend User",
                "success": True,
                "user_suspended": is_suspended,
                "response_time_ms": suspend_result["response_time_ms"]
            })
            
            print(f"    ✅ User suspended successfully (is_active: {suspended_user.get('is_active')})")
        else:
            test_results.append({
                "step": "Suspend User",
                "success": False,
                "error": suspend_result.get("error"),
                "response_time_ms": suspend_result["response_time_ms"]
            })
            print(f"    ❌ Suspend failed: {suspend_result.get('error')}")
            return {
                "test_name": "Login Prevention for Suspended Users",
                "error": "Failed to suspend user",
                "detailed_results": test_results
            }
        
        # Step 2: Try to login with suspended user - should fail with 403
        print("  Step 2: Attempting login with suspended user...")
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        login_result = await self.make_request("/auth/login", "POST", data=login_data)
        
        # Should fail with 403 status and specific message
        login_blocked = not login_result["success"] and login_result["status"] == 403
        correct_error_message = False
        
        if login_blocked:
            error_message = ""
            if isinstance(login_result["data"], dict):
                error_message = login_result["data"].get("detail", "")
            elif isinstance(login_result["data"], str):
                error_message = login_result["data"]
            
            # Check for expected error message
            expected_message = "Your account has been suspended. Please contact support for assistance."
            correct_error_message = expected_message in error_message
            
            test_results.append({
                "step": "Login Attempt with Suspended User",
                "success": True,
                "login_blocked": True,
                "status_code": login_result["status"],
                "correct_error_message": correct_error_message,
                "error_message": error_message,
                "response_time_ms": login_result["response_time_ms"]
            })
            
            print(f"    ✅ Login correctly blocked (Status: {login_result['status']})")
            print(f"    📝 Error message: {error_message}")
            print(f"    ✅ Correct error message: {correct_error_message}")
        else:
            test_results.append({
                "step": "Login Attempt with Suspended User",
                "success": False,
                "login_blocked": False,
                "status_code": login_result["status"],
                "error": "Login should have been blocked but wasn't",
                "response_time_ms": login_result["response_time_ms"]
            })
            print(f"    ❌ Login was not blocked (Status: {login_result['status']})")
        
        # Step 3: Verify active users can still login normally (test with admin)
        print("  Step 3: Verifying active users can still login...")
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        admin_login_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_login_result["success"]:
            test_results.append({
                "step": "Active User Login Verification",
                "success": True,
                "active_user_can_login": True,
                "response_time_ms": admin_login_result["response_time_ms"]
            })
            print(f"    ✅ Active user (admin) can still login normally")
        else:
            test_results.append({
                "step": "Active User Login Verification",
                "success": False,
                "active_user_can_login": False,
                "error": admin_login_result.get("error"),
                "response_time_ms": admin_login_result["response_time_ms"]
            })
            print(f"    ❌ Active user login failed: {admin_login_result.get('error')}")
        
        # Calculate overall success
        successful_steps = [r for r in test_results if r["success"]]
        login_prevention_working = (
            len(successful_steps) == len(test_results) and
            any(r.get("login_blocked") for r in test_results) and
            any(r.get("correct_error_message") for r in test_results) and
            any(r.get("active_user_can_login") for r in test_results)
        )
        
        return {
            "test_name": "Login Prevention for Suspended Users",
            "total_steps": len(test_results),
            "successful_steps": len(successful_steps),
            "login_prevention_working": login_prevention_working,
            "suspended_user_blocked": any(r.get("login_blocked") for r in test_results),
            "correct_error_message": any(r.get("correct_error_message") for r in test_results),
            "active_users_unaffected": any(r.get("active_user_can_login") for r in test_results),
            "detailed_results": test_results
        }
    
    async def test_profile_access_prevention(self) -> Dict:
        """Test 2: Profile Access Prevention"""
        print("👤 Testing profile access prevention for suspended users...")
        
        if not self.test_user_id:
            return {
                "test_name": "Profile Access Prevention",
                "error": "Test user ID not available"
            }
        
        test_results = []
        
        # Test GET /api/auth/profile/{user_id} with suspended user - should fail
        print("  Testing GET profile access...")
        profile_get_result = await self.make_request(f"/auth/profile/{self.test_user_id}")
        
        profile_get_blocked = not profile_get_result["success"] and profile_get_result["status"] == 403
        get_error_message = ""
        
        if profile_get_blocked:
            if isinstance(profile_get_result["data"], dict):
                get_error_message = profile_get_result["data"].get("detail", "")
            elif isinstance(profile_get_result["data"], str):
                get_error_message = profile_get_result["data"]
            
            expected_message = "Your account has been suspended. Please contact support for assistance."
            correct_get_error = expected_message in get_error_message
            
            test_results.append({
                "endpoint": "GET /auth/profile/{user_id}",
                "success": True,
                "access_blocked": True,
                "status_code": profile_get_result["status"],
                "correct_error_message": correct_get_error,
                "error_message": get_error_message,
                "response_time_ms": profile_get_result["response_time_ms"]
            })
            
            print(f"    ✅ GET profile access correctly blocked (Status: {profile_get_result['status']})")
        else:
            test_results.append({
                "endpoint": "GET /auth/profile/{user_id}",
                "success": False,
                "access_blocked": False,
                "status_code": profile_get_result["status"],
                "error": "Profile GET should have been blocked but wasn't",
                "response_time_ms": profile_get_result["response_time_ms"]
            })
            print(f"    ❌ GET profile access was not blocked (Status: {profile_get_result['status']})")
        
        # Test PUT /api/auth/profile/{user_id} with suspended user - should fail
        print("  Testing PUT profile update...")
        profile_update_data = {
            "profile": {
                "full_name": "Updated Name",
                "bio": "Updated bio"
            }
        }
        
        profile_put_result = await self.make_request(f"/auth/profile/{self.test_user_id}", "PUT", data=profile_update_data)
        
        profile_put_blocked = not profile_put_result["success"] and profile_put_result["status"] == 403
        put_error_message = ""
        
        if profile_put_blocked:
            if isinstance(profile_put_result["data"], dict):
                put_error_message = profile_put_result["data"].get("detail", "")
            elif isinstance(profile_put_result["data"], str):
                put_error_message = profile_put_result["data"]
            
            expected_message = "Your account has been suspended. Please contact support for assistance."
            correct_put_error = expected_message in put_error_message
            
            test_results.append({
                "endpoint": "PUT /auth/profile/{user_id}",
                "success": True,
                "access_blocked": True,
                "status_code": profile_put_result["status"],
                "correct_error_message": correct_put_error,
                "error_message": put_error_message,
                "response_time_ms": profile_put_result["response_time_ms"]
            })
            
            print(f"    ✅ PUT profile update correctly blocked (Status: {profile_put_result['status']})")
        else:
            test_results.append({
                "endpoint": "PUT /auth/profile/{user_id}",
                "success": False,
                "access_blocked": False,
                "status_code": profile_put_result["status"],
                "error": "Profile PUT should have been blocked but wasn't",
                "response_time_ms": profile_put_result["response_time_ms"]
            })
            print(f"    ❌ PUT profile update was not blocked (Status: {profile_put_result['status']})")
        
        # Calculate overall success
        successful_tests = [r for r in test_results if r["success"]]
        profile_protection_working = (
            len(successful_tests) == len(test_results) and
            all(r.get("access_blocked") for r in test_results) and
            all(r.get("correct_error_message") for r in test_results)
        )
        
        return {
            "test_name": "Profile Access Prevention",
            "total_endpoints_tested": len(test_results),
            "successful_tests": len(successful_tests),
            "profile_protection_working": profile_protection_working,
            "get_profile_blocked": any(r.get("endpoint") == "GET /auth/profile/{user_id}" and r.get("access_blocked") for r in test_results),
            "put_profile_blocked": any(r.get("endpoint") == "PUT /auth/profile/{user_id}" and r.get("access_blocked") for r in test_results),
            "consistent_error_messages": all(r.get("correct_error_message") for r in test_results),
            "detailed_results": test_results
        }
    
    async def test_user_specific_endpoint_protection(self) -> Dict:
        """Test 3: User-Specific Endpoint Protection"""
        print("🔒 Testing user-specific endpoint protection...")
        
        if not self.test_user_id:
            return {
                "test_name": "User-Specific Endpoint Protection",
                "error": "Test user ID not available"
            }
        
        test_results = []
        
        # Test /api/user/my-listings/{user_id} with suspended user - should fail
        print("  Testing my-listings endpoint...")
        listings_result = await self.make_request(f"/user/my-listings/{self.test_user_id}")
        
        listings_blocked = not listings_result["success"] and listings_result["status"] == 403
        listings_error_message = ""
        
        if listings_blocked:
            if isinstance(listings_result["data"], dict):
                listings_error_message = listings_result["data"].get("detail", "")
            elif isinstance(listings_result["data"], str):
                listings_error_message = listings_result["data"]
            
            expected_message = "Your account has been suspended. Please contact support for assistance."
            correct_listings_error = expected_message in listings_error_message
            
            test_results.append({
                "endpoint": "/user/my-listings/{user_id}",
                "success": True,
                "access_blocked": True,
                "status_code": listings_result["status"],
                "correct_error_message": correct_listings_error,
                "error_message": listings_error_message,
                "response_time_ms": listings_result["response_time_ms"]
            })
            
            print(f"    ✅ My-listings access correctly blocked (Status: {listings_result['status']})")
        else:
            test_results.append({
                "endpoint": "/user/my-listings/{user_id}",
                "success": False,
                "access_blocked": False,
                "status_code": listings_result["status"],
                "error": "My-listings should have been blocked but wasn't",
                "response_time_ms": listings_result["response_time_ms"]
            })
            print(f"    ❌ My-listings access was not blocked (Status: {listings_result['status']})")
        
        # Test /api/user/my-deals/{user_id} with suspended user - should fail
        print("  Testing my-deals endpoint...")
        deals_result = await self.make_request(f"/user/my-deals/{self.test_user_id}")
        
        deals_blocked = not deals_result["success"] and deals_result["status"] == 403
        deals_error_message = ""
        
        if deals_blocked:
            if isinstance(deals_result["data"], dict):
                deals_error_message = deals_result["data"].get("detail", "")
            elif isinstance(deals_result["data"], str):
                deals_error_message = deals_result["data"]
            
            expected_message = "Your account has been suspended. Please contact support for assistance."
            correct_deals_error = expected_message in deals_error_message
            
            test_results.append({
                "endpoint": "/user/my-deals/{user_id}",
                "success": True,
                "access_blocked": True,
                "status_code": deals_result["status"],
                "correct_error_message": correct_deals_error,
                "error_message": deals_error_message,
                "response_time_ms": deals_result["response_time_ms"]
            })
            
            print(f"    ✅ My-deals access correctly blocked (Status: {deals_result['status']})")
        else:
            test_results.append({
                "endpoint": "/user/my-deals/{user_id}",
                "success": False,
                "access_blocked": False,
                "status_code": deals_result["status"],
                "error": "My-deals should have been blocked but wasn't",
                "response_time_ms": deals_result["response_time_ms"]
            })
            print(f"    ❌ My-deals access was not blocked (Status: {deals_result['status']})")
        
        # Calculate overall success
        successful_tests = [r for r in test_results if r["success"]]
        endpoint_protection_working = (
            len(successful_tests) == len(test_results) and
            all(r.get("access_blocked") for r in test_results) and
            all(r.get("correct_error_message") for r in test_results)
        )
        
        return {
            "test_name": "User-Specific Endpoint Protection",
            "total_endpoints_tested": len(test_results),
            "successful_tests": len(successful_tests),
            "endpoint_protection_working": endpoint_protection_working,
            "my_listings_blocked": any(r.get("endpoint") == "/user/my-listings/{user_id}" and r.get("access_blocked") for r in test_results),
            "my_deals_blocked": any(r.get("endpoint") == "/user/my-deals/{user_id}" and r.get("access_blocked") for r in test_results),
            "consistent_error_messages": all(r.get("correct_error_message") for r in test_results),
            "detailed_results": test_results
        }
    
    async def test_reactivation_functionality(self) -> Dict:
        """Test 4: Reactivation Testing"""
        print("🔄 Testing reactivation functionality...")
        
        if not self.admin_token or not self.test_user_id:
            return {
                "test_name": "Reactivation Testing",
                "error": "Admin token or test user ID not available"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        test_results = []
        
        # Step 1: Reactivate the user
        print("  Step 1: Reactivating test user...")
        activate_result = await self.make_request(f"/admin/users/{self.test_user_id}/activate", "PUT", headers=headers)
        
        if activate_result["success"]:
            activated_user = activate_result["data"].get("user", {})
            is_activated = activated_user.get("is_active", False)
            
            test_results.append({
                "step": "Reactivate User",
                "success": True,
                "user_activated": is_activated,
                "response_time_ms": activate_result["response_time_ms"]
            })
            
            print(f"    ✅ User reactivated successfully (is_active: {activated_user.get('is_active')})")
        else:
            test_results.append({
                "step": "Reactivate User",
                "success": False,
                "error": activate_result.get("error"),
                "response_time_ms": activate_result["response_time_ms"]
            })
            print(f"    ❌ Reactivation failed: {activate_result.get('error')}")
            return {
                "test_name": "Reactivation Testing",
                "error": "Failed to reactivate user",
                "detailed_results": test_results
            }
        
        # Step 2: Test login works after reactivation
        print("  Step 2: Testing login after reactivation...")
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        login_result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if login_result["success"]:
            test_results.append({
                "step": "Login After Reactivation",
                "success": True,
                "login_successful": True,
                "response_time_ms": login_result["response_time_ms"]
            })
            print(f"    ✅ Login successful after reactivation")
        else:
            test_results.append({
                "step": "Login After Reactivation",
                "success": False,
                "login_successful": False,
                "error": login_result.get("error"),
                "response_time_ms": login_result["response_time_ms"]
            })
            print(f"    ❌ Login failed after reactivation: {login_result.get('error')}")
        
        # Step 3: Test profile access works after reactivation
        print("  Step 3: Testing profile access after reactivation...")
        profile_result = await self.make_request(f"/auth/profile/{self.test_user_id}")
        
        if profile_result["success"]:
            test_results.append({
                "step": "Profile Access After Reactivation",
                "success": True,
                "profile_accessible": True,
                "response_time_ms": profile_result["response_time_ms"]
            })
            print(f"    ✅ Profile access successful after reactivation")
        else:
            test_results.append({
                "step": "Profile Access After Reactivation",
                "success": False,
                "profile_accessible": False,
                "error": profile_result.get("error"),
                "response_time_ms": profile_result["response_time_ms"]
            })
            print(f"    ❌ Profile access failed after reactivation: {profile_result.get('error')}")
        
        # Step 4: Test user-specific endpoints work after reactivation
        print("  Step 4: Testing user-specific endpoints after reactivation...")
        
        # Test my-listings
        listings_result = await self.make_request(f"/user/my-listings/{self.test_user_id}")
        listings_accessible = listings_result["success"]
        
        # Test my-deals
        deals_result = await self.make_request(f"/user/my-deals/{self.test_user_id}")
        deals_accessible = deals_result["success"]
        
        endpoints_working = listings_accessible and deals_accessible
        
        test_results.append({
            "step": "User Endpoints After Reactivation",
            "success": endpoints_working,
            "my_listings_accessible": listings_accessible,
            "my_deals_accessible": deals_accessible,
            "response_time_ms": (listings_result["response_time_ms"] + deals_result["response_time_ms"]) / 2
        })
        
        if endpoints_working:
            print(f"    ✅ User-specific endpoints accessible after reactivation")
        else:
            print(f"    ❌ Some user-specific endpoints failed after reactivation")
        
        # Calculate overall success
        successful_steps = [r for r in test_results if r["success"]]
        reactivation_working = (
            len(successful_steps) == len(test_results) and
            any(r.get("user_activated") for r in test_results) and
            any(r.get("login_successful") for r in test_results) and
            any(r.get("profile_accessible") for r in test_results) and
            any(r.get("my_listings_accessible") and r.get("my_deals_accessible") for r in test_results)
        )
        
        return {
            "test_name": "Reactivation Testing",
            "total_steps": len(test_results),
            "successful_steps": len(successful_steps),
            "reactivation_working": reactivation_working,
            "user_reactivated": any(r.get("user_activated") for r in test_results),
            "login_works_after_reactivation": any(r.get("login_successful") for r in test_results),
            "profile_works_after_reactivation": any(r.get("profile_accessible") for r in test_results),
            "endpoints_work_after_reactivation": any(r.get("my_listings_accessible") and r.get("my_deals_accessible") for r in test_results),
            "detailed_results": test_results
        }
    
    async def test_error_message_consistency(self) -> Dict:
        """Test 5: Error Message Consistency"""
        print("📝 Testing error message consistency...")
        
        if not self.admin_token or not self.test_user_id:
            return {
                "test_name": "Error Message Consistency",
                "error": "Admin token or test user ID not available"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # First, ensure user is suspended for this test
        print("  Ensuring user is suspended for consistency test...")
        suspend_result = await self.make_request(f"/admin/users/{self.test_user_id}/suspend", "PUT", headers=headers)
        
        if not suspend_result["success"]:
            return {
                "test_name": "Error Message Consistency",
                "error": "Failed to suspend user for consistency test"
            }
        
        test_results = []
        expected_message = "Your account has been suspended. Please contact support for assistance."
        
        # Test all endpoints that should return consistent error messages
        endpoints_to_test = [
            {"endpoint": "/auth/login", "method": "POST", "data": {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}},
            {"endpoint": f"/auth/profile/{self.test_user_id}", "method": "GET"},
            {"endpoint": f"/auth/profile/{self.test_user_id}", "method": "PUT", "data": {"profile": {"full_name": "Test"}}},
            {"endpoint": f"/user/my-listings/{self.test_user_id}", "method": "GET"},
            {"endpoint": f"/user/my-deals/{self.test_user_id}", "method": "GET"}
        ]
        
        for test_endpoint in endpoints_to_test:
            endpoint = test_endpoint["endpoint"]
            method = test_endpoint["method"]
            data = test_endpoint.get("data")
            
            print(f"  Testing {method} {endpoint}...")
            
            result = await self.make_request(endpoint, method, data=data)
            
            # Should return 403 status
            correct_status = result["status"] == 403
            
            # Extract error message
            error_message = ""
            if isinstance(result["data"], dict):
                error_message = result["data"].get("detail", "")
            elif isinstance(result["data"], str):
                error_message = result["data"]
            
            # Check if error message matches expected
            correct_message = expected_message in error_message
            
            test_results.append({
                "endpoint": f"{method} {endpoint}",
                "status_code": result["status"],
                "correct_status": correct_status,
                "error_message": error_message,
                "correct_message": correct_message,
                "consistent": correct_status and correct_message,
                "response_time_ms": result["response_time_ms"]
            })
            
            status_icon = "✅" if correct_status else "❌"
            message_icon = "✅" if correct_message else "❌"
            print(f"    {status_icon} Status 403: {correct_status}")
            print(f"    {message_icon} Consistent message: {correct_message}")
        
        # Calculate consistency metrics
        consistent_endpoints = [r for r in test_results if r["consistent"]]
        all_consistent = len(consistent_endpoints) == len(test_results)
        consistent_status_codes = all(r["correct_status"] for r in test_results)
        consistent_messages = all(r["correct_message"] for r in test_results)
        
        return {
            "test_name": "Error Message Consistency",
            "total_endpoints_tested": len(test_results),
            "consistent_endpoints": len(consistent_endpoints),
            "all_endpoints_consistent": all_consistent,
            "consistent_status_codes": consistent_status_codes,
            "consistent_error_messages": consistent_messages,
            "consistency_score": (len(consistent_endpoints) / len(test_results)) * 100,
            "expected_message": expected_message,
            "detailed_results": test_results
        }
    
    async def run_comprehensive_suspended_user_test(self) -> Dict:
        """Run all suspended user protection tests"""
        print("🚀 Starting Cataloro Suspended User Protection Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Setup admin access and test user
            admin_setup = await self.setup_admin_access()
            if not admin_setup:
                return {"error": "Failed to setup admin access"}
            
            user_setup = await self.setup_test_user()
            if not user_setup:
                return {"error": "Failed to setup test user"}
            
            print("\n" + "=" * 70)
            
            # Run all test suites
            login_prevention = await self.test_login_prevention_for_suspended_users()
            profile_prevention = await self.test_profile_access_prevention()
            endpoint_protection = await self.test_user_specific_endpoint_protection()
            reactivation = await self.test_reactivation_functionality()
            error_consistency = await self.test_error_message_consistency()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_user_email": TEST_USER_EMAIL,
                "test_user_id": self.test_user_id,
                "login_prevention": login_prevention,
                "profile_access_prevention": profile_prevention,
                "user_specific_endpoint_protection": endpoint_protection,
                "reactivation_testing": reactivation,
                "error_message_consistency": error_consistency
            }
            
            # Calculate overall success metrics
            test_results = [
                login_prevention.get("login_prevention_working", False),
                profile_prevention.get("profile_protection_working", False),
                endpoint_protection.get("endpoint_protection_working", False),
                reactivation.get("reactivation_working", False),
                error_consistency.get("all_endpoints_consistent", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "login_prevention_working": login_prevention.get("login_prevention_working", False),
                "profile_protection_working": profile_prevention.get("profile_protection_working", False),
                "endpoint_protection_working": endpoint_protection.get("endpoint_protection_working", False),
                "reactivation_working": reactivation.get("reactivation_working", False),
                "error_consistency_working": error_consistency.get("all_endpoints_consistent", False),
                "all_tests_passed": overall_success_rate == 100,
                "suspended_user_protection_comprehensive": all(test_results)
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    print("🔧 Cataloro Suspended User Protection Testing Suite")
    print("=" * 60)
    
    tester = SuspendedUserProtectionTester()
    results = await tester.run_comprehensive_suspended_user_test()
    
    if "error" in results:
        print(f"\n❌ Test setup failed: {results['error']}")
        return
    
    # Print Test Summary
    print("\n" + "=" * 70)
    print("📊 SUSPENDED USER PROTECTION TEST SUMMARY")
    print("=" * 70)
    
    summary = results["summary"]
    login_prevention = results["login_prevention"]
    profile_prevention = results["profile_access_prevention"]
    endpoint_protection = results["user_specific_endpoint_protection"]
    reactivation = results["reactivation_testing"]
    error_consistency = results["error_message_consistency"]
    
    print(f"🎯 Overall Success Rate: {summary.get('overall_success_rate', 0):.0f}%")
    print(f"👤 Test User: {results.get('test_user_email')} (ID: {results.get('test_user_id')})")
    print()
    
    # Test 1: Login Prevention
    login_status = "✅" if login_prevention.get("login_prevention_working") else "❌"
    print(f"{login_status} Login Prevention for Suspended Users")
    print(f"   🚫 Suspended user blocked: {login_prevention.get('suspended_user_blocked', False)}")
    print(f"   📝 Correct error message: {login_prevention.get('correct_error_message', False)}")
    print(f"   ✅ Active users unaffected: {login_prevention.get('active_users_unaffected', False)}")
    
    # Test 2: Profile Access Prevention
    profile_status = "✅" if profile_prevention.get("profile_protection_working") else "❌"
    print(f"{profile_status} Profile Access Prevention")
    print(f"   🔒 GET profile blocked: {profile_prevention.get('get_profile_blocked', False)}")
    print(f"   🔒 PUT profile blocked: {profile_prevention.get('put_profile_blocked', False)}")
    print(f"   📝 Consistent error messages: {profile_prevention.get('consistent_error_messages', False)}")
    
    # Test 3: User-Specific Endpoint Protection
    endpoint_status = "✅" if endpoint_protection.get("endpoint_protection_working") else "❌"
    print(f"{endpoint_status} User-Specific Endpoint Protection")
    print(f"   🔒 My-listings blocked: {endpoint_protection.get('my_listings_blocked', False)}")
    print(f"   🔒 My-deals blocked: {endpoint_protection.get('my_deals_blocked', False)}")
    print(f"   📝 Consistent error messages: {endpoint_protection.get('consistent_error_messages', False)}")
    
    # Test 4: Reactivation Testing
    reactivation_status = "✅" if reactivation.get("reactivation_working") else "❌"
    print(f"{reactivation_status} Reactivation Testing")
    print(f"   🔄 User reactivated: {reactivation.get('user_reactivated', False)}")
    print(f"   🔐 Login works after reactivation: {reactivation.get('login_works_after_reactivation', False)}")
    print(f"   👤 Profile works after reactivation: {reactivation.get('profile_works_after_reactivation', False)}")
    print(f"   🔗 Endpoints work after reactivation: {reactivation.get('endpoints_work_after_reactivation', False)}")
    
    # Test 5: Error Message Consistency
    consistency_status = "✅" if error_consistency.get("all_endpoints_consistent") else "❌"
    consistency_score = error_consistency.get("consistency_score", 0)
    print(f"{consistency_status} Error Message Consistency")
    print(f"   📊 Consistency score: {consistency_score:.0f}%")
    print(f"   🔢 Consistent status codes (403): {error_consistency.get('consistent_status_codes', False)}")
    print(f"   📝 Consistent error messages: {error_consistency.get('consistent_error_messages', False)}")
    
    print()
    print("🏆 OVERALL SUSPENDED USER PROTECTION RESULTS:")
    overall_status = "✅ ALL TESTS PASSED" if summary.get("all_tests_passed") else "⚠️ SOME TESTS FAILED"
    print(f"   {overall_status}")
    print(f"   Success Rate: {summary.get('overall_success_rate', 0):.0f}%")
    print(f"   Comprehensive Protection: {summary.get('suspended_user_protection_comprehensive', False)}")
    
    # Detailed failure analysis if needed
    if not summary.get("all_tests_passed"):
        print("\n🔍 FAILURE ANALYSIS:")
        
        if not login_prevention.get("login_prevention_working"):
            print("   ❌ Login prevention issues detected")
        
        if not profile_prevention.get("profile_protection_working"):
            print("   ❌ Profile access protection issues detected")
        
        if not endpoint_protection.get("endpoint_protection_working"):
            print("   ❌ User-specific endpoint protection issues detected")
        
        if not reactivation.get("reactivation_working"):
            print("   ❌ Reactivation functionality issues detected")
        
        if not error_consistency.get("all_endpoints_consistent"):
            print("   ❌ Error message consistency issues detected")
    
    print("\n" + "=" * 70)
    print("✅ SUSPENDED USER PROTECTION TESTING COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())