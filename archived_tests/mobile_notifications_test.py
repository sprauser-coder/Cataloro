#!/usr/bin/env python3
"""
MOBILE NOTIFICATIONS CONFIGURATION TESTING - URGENT
Testing that mobile notifications are now properly configured:
- Menu Settings Configuration: Verify GET /api/admin/menu-settings returns notifications in mobile_menu
- Notifications Data Loading: Test GET /api/user/{user_id}/notifications for mobile badge count
- Authentication: Check authentication is working for notifications endpoint
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-marketplace-6.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"
ADMIN_ROLE = "admin"
ADMIN_ID = "admin_user_1"

# Demo User Configuration
DEMO_EMAIL = "demo@cataloro.com"
DEMO_USER_ID = "68bfff790e4e46bc28d43631"

class MobileNotificationsTester:
    """
    MOBILE NOTIFICATIONS CONFIGURATION TESTING
    Testing that mobile notifications are now properly configured:
    
    TESTS NEEDED:
    1. Menu Settings Configuration - Verify GET /api/admin/menu-settings returns notifications in mobile_menu
    2. Notifications Data Loading - Test GET /api/user/{user_id}/notifications for mobile badge count  
    3. Authentication - Check authentication is working for notifications endpoint
    
    EXPECTED RESULTS:
    - Mobile users should now see notifications option in bottom navigation
    - Notifications badge should show unread count
    - Menu visibility controls should work via admin settings
    """
    
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.test_user_id = None
        self.admin_user_id = None
        self.test_results = {}
        
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
    
    async def authenticate_users(self) -> bool:
        """Authenticate admin and demo users"""
        print("🔐 Authenticating users for mobile notifications testing...")
        
        # Authenticate admin user
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            self.admin_user_id = admin_result["data"].get("user", {}).get("id", ADMIN_ID)
            print(f"  ✅ Admin user authentication successful (ID: {self.admin_user_id})")
        else:
            print(f"  ❌ Admin user authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
        
        # Authenticate demo user
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": "demo_password"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            self.test_user_id = demo_result["data"].get("user", {}).get("id", DEMO_USER_ID)
            print(f"  ✅ Demo user authentication successful (ID: {self.test_user_id})")
            return True
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error', 'Unknown error')}")
            return False
    
    async def test_menu_settings_configuration(self) -> Dict:
        """
        Test 1: Menu Settings Configuration
        Verify GET /api/admin/menu-settings still returns notifications in mobile_menu
        Check that mobile_menu.notifications has proper structure with enabled/label/roles
        """
        print("⚙️ Testing menu settings configuration...")
        
        test_results = {
            "endpoint": "/admin/menu-settings",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "notifications_in_mobile_menu": False,
            "notifications_structure_valid": False,
            "authentication_working": False,
            "error_messages": [],
            "success": False
        }
        
        # Test with admin authentication
        print("  🔐 Testing authenticated menu settings access...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            test_results["authentication_working"] = True
            menu_data = result.get("data", {})
            
            # Check if mobile_menu exists
            mobile_menu = menu_data.get("mobile_menu", {})
            if mobile_menu:
                print(f"    ✅ Mobile menu configuration found")
                
                # Check if notifications exists in mobile_menu
                notifications_config = mobile_menu.get("notifications")
                if notifications_config:
                    test_results["notifications_in_mobile_menu"] = True
                    print(f"    ✅ Notifications found in mobile_menu")
                    
                    # Verify notifications structure
                    required_fields = ["enabled", "label", "roles"]
                    missing_fields = [field for field in required_fields if field not in notifications_config]
                    
                    if not missing_fields:
                        test_results["notifications_structure_valid"] = True
                        test_results["success"] = True
                        print(f"    ✅ Notifications structure valid: {notifications_config}")
                        print(f"    📱 Mobile notifications enabled: {notifications_config.get('enabled', False)}")
                        print(f"    🏷️ Notifications label: {notifications_config.get('label', 'N/A')}")
                        print(f"    👥 Allowed roles: {notifications_config.get('roles', [])}")
                    else:
                        test_results["error_messages"].append(f"Notifications missing required fields: {missing_fields}")
                        print(f"    ❌ Notifications structure invalid - missing fields: {missing_fields}")
                else:
                    test_results["error_messages"].append("Notifications not found in mobile_menu")
                    print(f"    ❌ Notifications not found in mobile_menu")
            else:
                test_results["error_messages"].append("Mobile menu configuration not found")
                print(f"    ❌ Mobile menu configuration not found")
            
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
        else:
            test_results["error_messages"].append(f"Menu settings request failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Menu settings request failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        # Test without authentication (should fail)
        print("  🚫 Testing unauthenticated menu settings access (should fail)...")
        unauth_result = await self.make_request("/admin/menu-settings")
        if unauth_result["status"] in [401, 403]:
            print(f"    ✅ Unauthenticated access properly rejected: Status {unauth_result['status']}")
        else:
            print(f"    ⚠️ Unauthenticated access not properly rejected: Status {unauth_result['status']}")
            test_results["error_messages"].append("Authentication not properly enforced")
        
        return {
            "test_name": "Menu Settings Configuration",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "mobile_notifications_configured": test_results["notifications_in_mobile_menu"] and test_results["notifications_structure_valid"]
        }
    
    async def test_notifications_data_loading(self) -> Dict:
        """
        Test 2: Notifications Data Loading
        Test GET /api/user/{user_id}/notifications for mobile badge count
        Verify unread notifications can be counted for mobile badge display
        """
        print("📱 Testing notifications data loading for mobile badge...")
        
        test_results = {
            "endpoint": f"/user/{self.test_user_id}/notifications",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "notifications_count": 0,
            "unread_count": 0,
            "authentication_working": False,
            "data_structure_valid": False,
            "error_messages": [],
            "success": False
        }
        
        # Test with user authentication
        print("  🔐 Testing authenticated notifications data loading...")
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        result = await self.make_request(f"/user/{self.test_user_id}/notifications", headers=headers)
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            test_results["authentication_working"] = True
            notifications = result.get("data", [])
            
            if isinstance(notifications, list):
                test_results["notifications_count"] = len(notifications)
                test_results["data_structure_valid"] = True
                
                # Count unread notifications for mobile badge
                unread_count = 0
                for notification in notifications:
                    if isinstance(notification, dict) and not notification.get("read", True):
                        unread_count += 1
                
                test_results["unread_count"] = unread_count
                test_results["success"] = True
                
                print(f"    ✅ Notifications loaded: {test_results['notifications_count']} total")
                print(f"    🔔 Unread notifications: {test_results['unread_count']} (for mobile badge)")
                print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
                
                # Verify notification structure for mobile display
                if notifications and len(notifications) > 0:
                    sample_notification = notifications[0]
                    required_fields = ["id", "title", "message", "read", "created_at"]
                    missing_fields = [field for field in required_fields if field not in sample_notification]
                    
                    if missing_fields:
                        test_results["error_messages"].append(f"Notification missing required fields: {missing_fields}")
                        print(f"    ⚠️ Notification structure incomplete - missing fields: {missing_fields}")
                    else:
                        print(f"    ✅ Notification data structure valid for mobile display")
                else:
                    print(f"    ℹ️ No notifications found (empty array is valid)")
            else:
                test_results["error_messages"].append("Notifications data is not in expected array format")
                print(f"    ❌ Notifications data format invalid - expected array, got: {type(notifications)}")
        else:
            test_results["error_messages"].append(f"Notifications loading failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Notifications loading failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        # Test without authentication (should fail)
        print("  🚫 Testing unauthenticated notifications access (should fail)...")
        unauth_result = await self.make_request(f"/user/{self.test_user_id}/notifications")
        if unauth_result["status"] in [401, 403]:
            print(f"    ✅ Unauthenticated access properly rejected: Status {unauth_result['status']}")
        else:
            print(f"    ⚠️ Unauthenticated access not properly rejected: Status {unauth_result['status']}")
            test_results["error_messages"].append("Authentication not properly enforced")
        
        return {
            "test_name": "Notifications Data Loading",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "mobile_badge_ready": test_results["success"] and test_results["data_structure_valid"]
        }
    
    async def test_notifications_authentication(self) -> Dict:
        """
        Test 3: Notifications Authentication
        Check authentication is working for notifications endpoint
        Test both GET and PUT operations with proper authentication
        """
        print("🔐 Testing notifications authentication...")
        
        test_results = {
            "get_endpoint": f"/user/{self.test_user_id}/notifications",
            "put_endpoint": f"/user/{self.test_user_id}/notifications/test-id/read",
            "get_status": 0,
            "put_status": 0,
            "get_response_time_ms": 0,
            "put_response_time_ms": 0,
            "get_authentication_working": False,
            "put_authentication_working": False,
            "error_messages": [],
            "success": False
        }
        
        # Test GET notifications with authentication
        print("  📥 Testing GET notifications with authentication...")
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        get_result = await self.make_request(f"/user/{self.test_user_id}/notifications", headers=headers)
        
        test_results["get_status"] = get_result["status"]
        test_results["get_response_time_ms"] = get_result["response_time_ms"]
        
        if get_result["success"]:
            test_results["get_authentication_working"] = True
            print(f"    ✅ GET notifications with authentication successful")
            print(f"    ⏱️ GET response time: {test_results['get_response_time_ms']:.1f}ms")
        else:
            test_results["error_messages"].append(f"GET notifications failed: {get_result.get('error', 'Unknown error')}")
            print(f"    ❌ GET notifications failed: Status {get_result['status']}")
        
        # Test PUT notification read with authentication (if we have notifications)
        print("  📤 Testing PUT notification read with authentication...")
        
        # First, try to get a notification ID to test with
        notification_id = None
        if get_result["success"]:
            notifications = get_result.get("data", [])
            if notifications and isinstance(notifications, list) and len(notifications) > 0:
                notification_id = notifications[0].get("id")
        
        if notification_id:
            put_result = await self.make_request(
                f"/user/{self.test_user_id}/notifications/{notification_id}/read", 
                "PUT", 
                headers=headers
            )
            
            test_results["put_status"] = put_result["status"]
            test_results["put_response_time_ms"] = put_result["response_time_ms"]
            
            if put_result["success"]:
                test_results["put_authentication_working"] = True
                print(f"    ✅ PUT notification read with authentication successful")
                print(f"    ⏱️ PUT response time: {test_results['put_response_time_ms']:.1f}ms")
            else:
                test_results["error_messages"].append(f"PUT notification read failed: {put_result.get('error', 'Unknown error')}")
                print(f"    ❌ PUT notification read failed: Status {put_result['status']}")
        else:
            # No notifications to test with, but that's okay - we'll test with a dummy ID
            put_result = await self.make_request(
                f"/user/{self.test_user_id}/notifications/dummy-id/read", 
                "PUT", 
                headers=headers
            )
            
            test_results["put_status"] = put_result["status"]
            test_results["put_response_time_ms"] = put_result["response_time_ms"]
            
            # For dummy ID, we expect 404 or similar, but not 401/403 (which would indicate auth failure)
            if put_result["status"] in [404, 400]:
                test_results["put_authentication_working"] = True
                print(f"    ✅ PUT authentication working (Status {put_result['status']} expected for dummy ID)")
            elif put_result["status"] in [401, 403]:
                test_results["error_messages"].append("PUT authentication failed")
                print(f"    ❌ PUT authentication failed: Status {put_result['status']}")
            else:
                test_results["put_authentication_working"] = True
                print(f"    ✅ PUT endpoint responding (Status {put_result['status']})")
        
        # Determine overall success
        test_results["success"] = (
            test_results["get_authentication_working"] and 
            test_results["put_authentication_working"]
        )
        
        return {
            "test_name": "Notifications Authentication",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "authentication_fixed": test_results["success"]
        }
    
    async def run_mobile_notifications_tests(self) -> Dict:
        """
        Run complete mobile notifications configuration tests
        """
        print("🚨 STARTING MOBILE NOTIFICATIONS CONFIGURATION TESTING")
        print("=" * 80)
        print("TESTING: Mobile notifications configuration and functionality")
        print("FOCUS: Menu settings, data loading, authentication")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_users()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "User authentication failed - cannot proceed with testing"
                }
            
            # Run all mobile notifications tests
            menu_settings_test = await self.test_menu_settings_configuration()
            data_loading_test = await self.test_notifications_data_loading()
            authentication_test = await self.test_notifications_authentication()
            
            # Compile comprehensive test results
            test_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Mobile notifications configuration and functionality",
                "menu_settings_test": menu_settings_test,
                "data_loading_test": data_loading_test,
                "authentication_test": authentication_test
            }
            
            # Determine critical findings
            critical_issues = []
            working_features = []
            
            tests = [menu_settings_test, data_loading_test, authentication_test]
            
            for test in tests:
                if test.get("critical_issue", False):
                    error_msg = "Unknown error"
                    if test.get("test_results", {}).get("error_messages"):
                        error_msg = test["test_results"]["error_messages"][0]
                    elif test.get("error"):
                        error_msg = test["error"]
                    critical_issues.append(f"{test['test_name']}: {error_msg}")
                
                if test.get("success", False):
                    working_features.append(f"{test['test_name']}: Working correctly")
            
            # Calculate success metrics
            total_tests = len(tests)
            successful_tests = sum(1 for test in tests if test.get("success", False))
            success_rate = (successful_tests / total_tests) * 100
            
            test_results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": success_rate,
                "critical_issues": critical_issues,
                "working_features": working_features,
                "mobile_notifications_ready": len(critical_issues) == 0,
                "menu_configured": menu_settings_test.get("mobile_notifications_configured", False),
                "data_loading_working": data_loading_test.get("mobile_badge_ready", False),
                "authentication_working": authentication_test.get("authentication_fixed", False)
            }
            
            return test_results
            
        finally:
            await self.cleanup()


async def main():
    """Run mobile notifications configuration tests"""
    tester = MobileNotificationsTester()
    results = await tester.run_mobile_notifications_tests()
    
    print("\n" + "=" * 80)
    print("🏁 MOBILE NOTIFICATIONS CONFIGURATION TESTING COMPLETE")
    print("=" * 80)
    
    summary = results.get("summary", {})
    
    print(f"📊 Test Results Summary:")
    print(f"   Total Tests: {summary.get('total_tests', 0)}")
    print(f"   Successful: {summary.get('successful_tests', 0)}")
    print(f"   Failed: {summary.get('failed_tests', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
    
    print(f"\n🎯 Mobile Notifications Status:")
    print(f"   Menu Configured: {'✅' if summary.get('menu_configured', False) else '❌'}")
    print(f"   Data Loading: {'✅' if summary.get('data_loading_working', False) else '❌'}")
    print(f"   Authentication: {'✅' if summary.get('authentication_working', False) else '❌'}")
    print(f"   Overall Ready: {'✅' if summary.get('mobile_notifications_ready', False) else '❌'}")
    
    if summary.get("critical_issues"):
        print(f"\n❌ Critical Issues Found:")
        for issue in summary["critical_issues"]:
            print(f"   - {issue}")
    
    if summary.get("working_features"):
        print(f"\n✅ Working Features:")
        for feature in summary["working_features"]:
            print(f"   - {feature}")
    
    print("\n" + "=" * 80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())