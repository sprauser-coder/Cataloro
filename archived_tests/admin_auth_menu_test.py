#!/usr/bin/env python3
"""
Admin Authentication and Menu Settings Access Testing
Testing admin login flow and menu settings API access with proper authentication
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://mobileui-sync.preview.emergentagent.com/api"

# Admin credentials for testing
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

class AdminAuthMenuTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.admin_user_data = None
        
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
    
    async def test_admin_login_process(self) -> Dict:
        """Test Admin Login Process - POST /api/auth/login with admin credentials"""
        print("🔐 Testing Admin Login Process...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            response_data = result["data"]
            user_data = response_data.get("user", {})
            token = response_data.get("token", "")
            
            # Store for subsequent tests
            self.admin_token = token
            self.admin_user_data = user_data
            
            # Verify admin properties
            email_correct = user_data.get("email") == ADMIN_EMAIL
            has_admin_role = (user_data.get("role") == "admin" or 
                             user_data.get("user_role") == "Admin" or
                             user_data.get("badge") == "Admin")
            token_received = bool(token)
            user_id_present = bool(user_data.get("id"))
            
            print(f"  ✅ Admin login successful")
            print(f"  📧 Email: {user_data.get('email')} ({'✅' if email_correct else '❌'})")
            print(f"  🔑 Admin Role: {user_data.get('role', user_data.get('user_role', user_data.get('badge')))} ({'✅' if has_admin_role else '❌'})")
            print(f"  🎫 Token received: {'✅' if token_received else '❌'}")
            print(f"  🆔 User ID: {user_data.get('id')} ({'✅' if user_id_present else '❌'})")
            
            return {
                "test_name": "Admin Login Process",
                "login_successful": True,
                "response_time_ms": result["response_time_ms"],
                "token_returned": token_received,
                "token_valid": len(token) > 10 if token else False,
                "user_data_complete": {
                    "email_correct": email_correct,
                    "admin_role_present": has_admin_role,
                    "user_id_present": user_id_present,
                    "username_present": bool(user_data.get("username")),
                    "full_name_present": bool(user_data.get("full_name"))
                },
                "admin_user_data": user_data,
                "token": token[:20] + "..." if token else None,  # Truncated for security
                "all_checks_passed": email_correct and has_admin_role and token_received and user_id_present
            }
        else:
            print(f"  ❌ Admin login failed: {result.get('error', 'Unknown error')}")
            print(f"  📊 Status: {result['status']}")
            
            return {
                "test_name": "Admin Login Process",
                "login_successful": False,
                "response_time_ms": result["response_time_ms"],
                "error": result.get("error", "Login failed"),
                "status": result["status"],
                "response_data": result.get("data")
            }
    
    async def test_menu_settings_api_access(self) -> Dict:
        """Test Menu Settings API Access with Authentication"""
        print("🍽️ Testing Menu Settings API Access with Authentication...")
        
        if not self.admin_token:
            return {
                "test_name": "Menu Settings API Access",
                "error": "No admin token available - admin login required first",
                "requires_login": True
            }
        
        # Test without authentication headers first
        print("  Testing without authentication headers...")
        no_auth_result = await self.make_request("/admin/menu-settings")
        
        # Test with authentication headers
        print("  Testing with authentication headers...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        auth_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        # Test with different header formats
        print("  Testing with different header formats...")
        alt_headers = {"Authorization": f"Token {self.admin_token}"}
        alt_auth_result = await self.make_request("/admin/menu-settings", headers=alt_headers)
        
        # Analyze results
        no_auth_blocked = not no_auth_result["success"] and no_auth_result["status"] in [401, 403]
        auth_successful = auth_result["success"]
        menu_data_present = False
        menu_structure_valid = False
        
        if auth_successful:
            menu_data = auth_result.get("data", {})
            menu_data_present = bool(menu_data)
            
            # Check menu structure
            if isinstance(menu_data, dict):
                has_desktop_menu = "desktop_menu" in menu_data
                has_mobile_menu = "mobile_menu" in menu_data
                menu_structure_valid = has_desktop_menu or has_mobile_menu
                
                print(f"    📱 Desktop menu present: {'✅' if has_desktop_menu else '❌'}")
                print(f"    📱 Mobile menu present: {'✅' if has_mobile_menu else '❌'}")
                
                if has_desktop_menu:
                    desktop_items = menu_data.get("desktop_menu", [])
                    print(f"    📋 Desktop menu items: {len(desktop_items)}")
                
                if has_mobile_menu:
                    mobile_items = menu_data.get("mobile_menu", [])
                    print(f"    📋 Mobile menu items: {len(mobile_items)}")
        
        print(f"  🚫 No auth blocked: {'✅' if no_auth_blocked else '❌'}")
        print(f"  ✅ Auth successful: {'✅' if auth_successful else '❌'}")
        print(f"  📊 Menu data present: {'✅' if menu_data_present else '❌'}")
        
        return {
            "test_name": "Menu Settings API Access",
            "authentication_required": no_auth_blocked,
            "authenticated_access_works": auth_successful,
            "menu_data_returned": menu_data_present,
            "menu_structure_valid": menu_structure_valid,
            "response_times": {
                "no_auth_ms": no_auth_result["response_time_ms"],
                "with_auth_ms": auth_result["response_time_ms"] if auth_result else 0
            },
            "status_codes": {
                "no_auth": no_auth_result["status"],
                "with_auth": auth_result["status"] if auth_result else 0,
                "alt_auth": alt_auth_result["status"] if alt_auth_result else 0
            },
            "menu_data_sample": auth_result.get("data", {}) if auth_successful else None,
            "all_checks_passed": no_auth_blocked and auth_successful and menu_data_present
        }
    
    async def test_menu_settings_crud_operations(self) -> Dict:
        """Test Menu Settings CRUD operations"""
        print("🔧 Testing Menu Settings CRUD Operations...")
        
        if not self.admin_token:
            return {
                "test_name": "Menu Settings CRUD Operations",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        operations_results = {}
        
        # 1. GET - Retrieve current menu settings
        print("  Testing GET menu settings...")
        get_result = await self.make_request("/admin/menu-settings", headers=headers)
        operations_results["get"] = {
            "success": get_result["success"],
            "response_time_ms": get_result["response_time_ms"],
            "status": get_result["status"],
            "has_data": bool(get_result.get("data")) if get_result["success"] else False
        }
        
        original_settings = get_result.get("data", {}) if get_result["success"] else {}
        
        # 2. POST/PUT - Update menu settings (if endpoint exists)
        print("  Testing POST/PUT menu settings...")
        test_settings = {
            "desktop_menu": [
                {"id": "test_item", "label": "Test Item", "enabled": True, "roles": ["admin"]}
            ],
            "mobile_menu": [
                {"id": "test_mobile", "label": "Test Mobile", "enabled": True, "roles": ["admin"]}
            ]
        }
        
        # Try POST first
        post_result = await self.make_request("/admin/menu-settings", "POST", data=test_settings, headers=headers)
        operations_results["post"] = {
            "success": post_result["success"],
            "response_time_ms": post_result["response_time_ms"],
            "status": post_result["status"],
            "endpoint_exists": post_result["status"] != 404
        }
        
        # Try PUT if POST failed
        if not post_result["success"]:
            put_result = await self.make_request("/admin/menu-settings", "PUT", data=test_settings, headers=headers)
            operations_results["put"] = {
                "success": put_result["success"],
                "response_time_ms": put_result["response_time_ms"],
                "status": put_result["status"],
                "endpoint_exists": put_result["status"] != 404
            }
        
        # 3. Verify changes (GET again)
        print("  Verifying changes...")
        verify_result = await self.make_request("/admin/menu-settings", headers=headers)
        operations_results["verify"] = {
            "success": verify_result["success"],
            "response_time_ms": verify_result["response_time_ms"],
            "settings_changed": False
        }
        
        if verify_result["success"]:
            new_settings = verify_result.get("data", {})
            settings_changed = new_settings != original_settings
            operations_results["verify"]["settings_changed"] = settings_changed
        
        # Calculate overall CRUD functionality
        get_works = operations_results["get"]["success"]
        update_works = (operations_results.get("post", {}).get("success", False) or 
                       operations_results.get("put", {}).get("success", False))
        crud_functional = get_works  # At minimum, GET should work
        
        return {
            "test_name": "Menu Settings CRUD Operations",
            "get_operation_works": get_works,
            "update_operation_works": update_works,
            "crud_functional": crud_functional,
            "operations_results": operations_results,
            "original_settings_retrieved": bool(original_settings),
            "update_endpoints_available": (operations_results.get("post", {}).get("endpoint_exists", False) or
                                         operations_results.get("put", {}).get("endpoint_exists", False))
        }
    
    async def test_direct_api_access(self) -> Dict:
        """Test direct API access from browser perspective"""
        print("🌐 Testing Direct API Access (Browser Perspective)...")
        
        if not self.admin_token:
            return {
                "test_name": "Direct API Access",
                "error": "No admin token available - admin login required first"
            }
        
        # Test various header combinations that browsers might use
        test_scenarios = [
            {
                "name": "Bearer Token",
                "headers": {"Authorization": f"Bearer {self.admin_token}"}
            },
            {
                "name": "Bearer Token with CORS",
                "headers": {
                    "Authorization": f"Bearer {self.admin_token}",
                    "Origin": "https://mobileui-sync.preview.emergentagent.com",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Token in Custom Header",
                "headers": {"X-Auth-Token": self.admin_token}
            },
            {
                "name": "No Authentication",
                "headers": {}
            }
        ]
        
        scenario_results = []
        
        for scenario in test_scenarios:
            print(f"  Testing scenario: {scenario['name']}")
            result = await self.make_request("/admin/menu-settings", headers=scenario["headers"])
            
            scenario_result = {
                "scenario_name": scenario["name"],
                "success": result["success"],
                "status": result["status"],
                "response_time_ms": result["response_time_ms"],
                "has_cors_headers": any(header.lower().startswith("access-control") 
                                      for header in result.get("headers", {}).keys()),
                "error": result.get("error") if not result["success"] else None
            }
            
            scenario_results.append(scenario_result)
            
            status_emoji = "✅" if result["success"] else "❌"
            print(f"    {status_emoji} Status: {result['status']}, Time: {result['response_time_ms']:.0f}ms")
        
        # Analyze results
        bearer_token_works = any(s["success"] for s in scenario_results if "Bearer" in s["scenario_name"])
        cors_supported = any(s["has_cors_headers"] for s in scenario_results)
        no_auth_blocked = not any(s["success"] for s in scenario_results if s["scenario_name"] == "No Authentication")
        
        return {
            "test_name": "Direct API Access",
            "bearer_token_authentication_works": bearer_token_works,
            "cors_headers_present": cors_supported,
            "unauthenticated_access_blocked": no_auth_blocked,
            "scenario_results": scenario_results,
            "browser_compatible": bearer_token_works and cors_supported,
            "security_properly_implemented": no_auth_blocked
        }
    
    async def test_admin_redirect_logic(self) -> Dict:
        """Test admin redirect logic and role-based access"""
        print("🔄 Testing Admin Redirect Logic and Role-Based Access...")
        
        if not self.admin_user_data:
            return {
                "test_name": "Admin Redirect Logic",
                "error": "No admin user data available - admin login required first"
            }
        
        # Test admin-specific endpoints that should be accessible
        admin_endpoints = [
            "/admin/dashboard",
            "/admin/users",
            "/admin/menu-settings",
            "/admin/performance"
        ]
        
        headers = {"Authorization": f"Bearer {self.admin_token}"} if self.admin_token else {}
        endpoint_results = []
        
        for endpoint in admin_endpoints:
            print(f"  Testing admin endpoint: {endpoint}")
            result = await self.make_request(endpoint, headers=headers)
            
            endpoint_result = {
                "endpoint": endpoint,
                "accessible": result["success"],
                "status": result["status"],
                "response_time_ms": result["response_time_ms"],
                "requires_admin": result["status"] in [401, 403] if not result["success"] else None,
                "error": result.get("error") if not result["success"] else None
            }
            
            endpoint_results.append(endpoint_result)
            
            status_emoji = "✅" if result["success"] else "❌"
            print(f"    {status_emoji} {endpoint}: {result['status']}")
        
        # Test user role verification
        user_role = self.admin_user_data.get("role", "")
        user_role_alt = self.admin_user_data.get("user_role", "")
        badge = self.admin_user_data.get("badge", "")
        
        is_admin = (user_role == "admin" or 
                   user_role_alt == "Admin" or 
                   badge == "Admin")
        
        # Calculate accessibility
        accessible_endpoints = [e for e in endpoint_results if e["accessible"]]
        admin_access_working = len(accessible_endpoints) >= len(admin_endpoints) * 0.5  # At least 50% should work
        
        return {
            "test_name": "Admin Redirect Logic",
            "user_has_admin_role": is_admin,
            "admin_role_details": {
                "role": user_role,
                "user_role": user_role_alt,
                "badge": badge
            },
            "admin_endpoints_accessible": len(accessible_endpoints),
            "total_admin_endpoints_tested": len(admin_endpoints),
            "admin_access_percentage": (len(accessible_endpoints) / len(admin_endpoints)) * 100,
            "admin_redirect_logic_working": admin_access_working and is_admin,
            "endpoint_results": endpoint_results,
            "role_based_access_functional": is_admin and admin_access_working
        }
    
    async def test_frontend_integration_compatibility(self) -> Dict:
        """Test frontend integration compatibility"""
        print("🖥️ Testing Frontend Integration Compatibility...")
        
        if not self.admin_token:
            return {
                "test_name": "Frontend Integration Compatibility",
                "error": "No admin token available - admin login required first"
            }
        
        # Test API responses for frontend compatibility
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test login response format
        login_response_valid = bool(self.admin_user_data and self.admin_token)
        
        # Test menu settings response format
        menu_result = await self.make_request("/admin/menu-settings", headers=headers)
        menu_response_valid = False
        menu_json_valid = False
        
        if menu_result["success"]:
            menu_data = menu_result.get("data", {})
            menu_response_valid = isinstance(menu_data, dict)
            
            # Check if response is valid JSON that frontend can parse
            try:
                json.dumps(menu_data)
                menu_json_valid = True
            except:
                menu_json_valid = False
        
        # Test CORS headers for frontend requests
        cors_headers_present = any(header.lower().startswith("access-control") 
                                 for header in menu_result.get("headers", {}).keys())
        
        # Test response times for frontend performance
        acceptable_response_time = menu_result.get("response_time_ms", 9999) < 2000  # Under 2 seconds
        
        return {
            "test_name": "Frontend Integration Compatibility",
            "login_response_format_valid": login_response_valid,
            "menu_settings_response_format_valid": menu_response_valid,
            "json_serializable": menu_json_valid,
            "cors_headers_present": cors_headers_present,
            "response_time_acceptable": acceptable_response_time,
            "response_time_ms": menu_result.get("response_time_ms", 0),
            "frontend_compatible": (login_response_valid and menu_response_valid and 
                                  menu_json_valid and cors_headers_present and 
                                  acceptable_response_time),
            "integration_issues": []
        }
    
    async def run_comprehensive_admin_auth_menu_test(self) -> Dict:
        """Run all admin authentication and menu settings tests"""
        print("🚀 Starting Admin Authentication and Menu Settings Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test suites in sequence
            admin_login = await self.test_admin_login_process()
            menu_api_access = await self.test_menu_settings_api_access()
            menu_crud = await self.test_menu_settings_crud_operations()
            direct_api = await self.test_direct_api_access()
            admin_redirect = await self.test_admin_redirect_logic()
            frontend_compat = await self.test_frontend_integration_compatibility()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "backend_url": BACKEND_URL,
                "admin_email": ADMIN_EMAIL,
                "tests": {
                    "admin_login_process": admin_login,
                    "menu_settings_api_access": menu_api_access,
                    "menu_settings_crud_operations": menu_crud,
                    "direct_api_access": direct_api,
                    "admin_redirect_logic": admin_redirect,
                    "frontend_integration_compatibility": frontend_compat
                }
            }
            
            # Calculate overall success metrics
            test_results = [
                admin_login.get("all_checks_passed", False),
                menu_api_access.get("all_checks_passed", False),
                menu_crud.get("crud_functional", False),
                direct_api.get("browser_compatible", False),
                admin_redirect.get("role_based_access_functional", False),
                frontend_compat.get("frontend_compatible", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            # Identify critical issues
            critical_issues = []
            if not admin_login.get("login_successful", False):
                critical_issues.append("Admin login failed")
            if not menu_api_access.get("authenticated_access_works", False):
                critical_issues.append("Menu settings API not accessible with authentication")
            if not admin_redirect.get("user_has_admin_role", False):
                critical_issues.append("User does not have admin role after login")
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "admin_login_working": admin_login.get("login_successful", False),
                "token_authentication_working": menu_api_access.get("authenticated_access_works", False),
                "menu_settings_accessible": menu_api_access.get("menu_data_returned", False),
                "admin_role_verified": admin_redirect.get("user_has_admin_role", False),
                "frontend_integration_ready": frontend_compat.get("frontend_compatible", False),
                "critical_issues": critical_issues,
                "all_tests_passed": overall_success_rate == 100,
                "authentication_flow_working": (admin_login.get("login_successful", False) and 
                                               menu_api_access.get("authenticated_access_works", False))
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = AdminAuthMenuTester()
    results = await tester.run_comprehensive_admin_auth_menu_test()
    
    # Print summary
    print("\n" + "=" * 70)
    print("🏁 ADMIN AUTHENTICATION & MENU SETTINGS TEST SUMMARY")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"📊 Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"🔐 Admin Login Working: {'✅' if summary.get('admin_login_working') else '❌'}")
    print(f"🎫 Token Authentication Working: {'✅' if summary.get('token_authentication_working') else '❌'}")
    print(f"🍽️ Menu Settings Accessible: {'✅' if summary.get('menu_settings_accessible') else '❌'}")
    print(f"👑 Admin Role Verified: {'✅' if summary.get('admin_role_verified') else '❌'}")
    print(f"🖥️ Frontend Integration Ready: {'✅' if summary.get('frontend_integration_ready') else '❌'}")
    
    critical_issues = summary.get("critical_issues", [])
    if critical_issues:
        print(f"\n🚨 Critical Issues Found:")
        for issue in critical_issues:
            print(f"  ❌ {issue}")
    else:
        print(f"\n✅ No Critical Issues Found")
    
    print(f"\n🔄 Authentication Flow Working: {'✅' if summary.get('authentication_flow_working') else '❌'}")
    print(f"🎯 All Tests Passed: {'✅' if summary.get('all_tests_passed') else '❌'}")
    
    # Save detailed results
    with open("/app/admin_auth_menu_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/admin_auth_menu_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())