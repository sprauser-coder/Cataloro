#!/usr/bin/env python3
"""
Desktop Menu Filtering Debug Test
Debug backend filtering logic specifically for desktop menu items as requested in review.

TESTING REQUIREMENTS:
1. Database State Verification - Check exact database state for desktop_menu.messages.enabled
2. Admin Settings Debug - Verify admin menu settings for desktop menu
3. User Filtering Logic Debug - Test desktop menu filtering in user API
4. Filtering Condition Analysis - Debug why desktop filtering fails while mobile works
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://marketplace-debug-3.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"
ADMIN_USER_ID = "admin_user_1"

class DesktopMenuFilteringDebugTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        
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
    
    async def authenticate_admin(self) -> Dict:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin user...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            token = result["data"].get("token", "")
            self.admin_token = token
            
            print(f"  ✅ Admin login successful")
            print(f"  📧 Email: {user_data.get('email')}")
            print(f"  👤 Username: {user_data.get('username')}")
            print(f"  🔑 Role: {user_data.get('role', user_data.get('user_role'))}")
            
            return {"success": True, "user_data": user_data, "token": token}
        else:
            print(f"  ❌ Admin login failed: {result.get('error', 'Unknown error')}")
            return {"success": False, "error": result.get("error", "Login failed")}
    
    async def test_database_state_verification(self) -> Dict:
        """Test 1: Database State Verification - Check exact database state"""
        print("🗄️ Testing Database State Verification...")
        
        if not self.admin_token:
            return {"test_name": "Database State Verification", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get raw menu settings from database
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if result["success"]:
            menu_settings = result["data"]
            
            # Check exact values for Messages in desktop and mobile
            desktop_menu = menu_settings.get("desktop_menu", {})
            mobile_menu = menu_settings.get("mobile_menu", {})
            
            desktop_messages = desktop_menu.get("messages", {})
            mobile_messages = mobile_menu.get("messages", {})
            
            desktop_enabled = desktop_messages.get("enabled")
            mobile_enabled = mobile_messages.get("enabled")
            
            print(f"  📊 Raw Database State:")
            print(f"    🖥️ Desktop Messages enabled: {desktop_enabled} (type: {type(desktop_enabled)})")
            print(f"    📱 Mobile Messages enabled: {mobile_enabled} (type: {type(mobile_enabled)})")
            
            # Check if Messages is consistently disabled
            messages_consistently_disabled = (desktop_enabled is False and mobile_enabled is False)
            
            print(f"    🔍 Messages consistently disabled: {messages_consistently_disabled}")
            
            return {
                "test_name": "Database State Verification",
                "success": True,
                "desktop_messages_enabled": desktop_enabled,
                "mobile_messages_enabled": mobile_enabled,
                "desktop_enabled_type": str(type(desktop_enabled)),
                "mobile_enabled_type": str(type(mobile_enabled)),
                "messages_consistently_disabled": messages_consistently_disabled,
                "raw_desktop_messages": desktop_messages,
                "raw_mobile_messages": mobile_messages
            }
        else:
            print(f"  ❌ Failed to get menu settings: {result.get('error')}")
            return {"test_name": "Database State Verification", "success": False, "error": result.get("error")}
    
    async def test_admin_settings_debug(self) -> Dict:
        """Test 2: Admin Settings Debug - Verify admin menu settings"""
        print("⚙️ Testing Admin Settings Debug...")
        
        if not self.admin_token:
            return {"test_name": "Admin Settings Debug", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get admin menu settings
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if result["success"]:
            menu_settings = result["data"]
            
            # Check Messages configuration in both menus
            desktop_menu = menu_settings.get("desktop_menu", {})
            mobile_menu = menu_settings.get("mobile_menu", {})
            
            desktop_messages = desktop_menu.get("messages", {})
            mobile_messages = mobile_menu.get("messages", {})
            
            # Verify Messages shows enabled: false for both
            desktop_disabled = desktop_messages.get("enabled") is False
            mobile_disabled = mobile_messages.get("enabled") is False
            
            # Check roles array
            desktop_roles = desktop_messages.get("roles", [])
            mobile_roles = mobile_messages.get("roles", [])
            
            print(f"  📋 Admin Settings Analysis:")
            print(f"    🖥️ Desktop Messages disabled: {desktop_disabled}")
            print(f"    📱 Mobile Messages disabled: {mobile_disabled}")
            print(f"    🖥️ Desktop Messages roles: {desktop_roles}")
            print(f"    📱 Mobile Messages roles: {mobile_roles}")
            
            return {
                "test_name": "Admin Settings Debug",
                "success": True,
                "desktop_messages_disabled": desktop_disabled,
                "mobile_messages_disabled": mobile_disabled,
                "desktop_messages_roles": desktop_roles,
                "mobile_messages_roles": mobile_roles,
                "admin_settings_correct": desktop_disabled and mobile_disabled,
                "roles_include_admin": "admin" in desktop_roles and "admin" in mobile_roles
            }
        else:
            print(f"  ❌ Failed to get admin settings: {result.get('error')}")
            return {"test_name": "Admin Settings Debug", "success": False, "error": result.get("error")}
    
    async def test_user_filtering_logic_debug(self) -> Dict:
        """Test 3: User Filtering Logic Debug - Test desktop menu filtering"""
        print("🔍 Testing User Filtering Logic Debug...")
        
        if not self.admin_token:
            return {"test_name": "User Filtering Logic Debug", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test user menu settings endpoint for admin user
        result = await self.make_request(f"/menu-settings/user/{ADMIN_USER_ID}", headers=headers)
        
        if result["success"]:
            user_menu_settings = result["data"]
            
            # Check what's returned for desktop and mobile menus
            desktop_menu = user_menu_settings.get("desktop_menu", {})
            mobile_menu = user_menu_settings.get("mobile_menu", {})
            
            # Check if Messages is present in each menu
            desktop_has_messages = "messages" in desktop_menu
            mobile_has_messages = "messages" in mobile_menu
            
            # Get Messages configuration if present
            desktop_messages = desktop_menu.get("messages", {}) if desktop_has_messages else None
            mobile_messages = mobile_menu.get("messages", {}) if mobile_has_messages else None
            
            print(f"  🔍 User Filtering Results:")
            print(f"    🖥️ Desktop menu has Messages: {desktop_has_messages}")
            print(f"    📱 Mobile menu has Messages: {mobile_has_messages}")
            
            if desktop_has_messages:
                print(f"    🖥️ Desktop Messages config: {desktop_messages}")
            if mobile_has_messages:
                print(f"    📱 Mobile Messages config: {mobile_messages}")
            
            # This is the critical finding - desktop should NOT have Messages if it's disabled
            filtering_working_correctly = not desktop_has_messages and not mobile_has_messages
            
            print(f"    🎯 Expected: Desktop=False, Mobile=False")
            print(f"    🎯 Actual: Desktop={desktop_has_messages}, Mobile={mobile_has_messages}")
            print(f"    🚨 CRITICAL BUG: Desktop filtering broken = {desktop_has_messages}")
            
            return {
                "test_name": "User Filtering Logic Debug",
                "success": True,
                "desktop_has_messages": desktop_has_messages,
                "mobile_has_messages": mobile_has_messages,
                "desktop_messages_config": desktop_messages,
                "mobile_messages_config": mobile_messages,
                "filtering_working_correctly": filtering_working_correctly,
                "desktop_filtering_broken": desktop_has_messages,  # This should be False
                "mobile_filtering_working": not mobile_has_messages,  # This should be True
                "critical_bug_confirmed": desktop_has_messages and not mobile_has_messages
            }
        else:
            print(f"  ❌ Failed to get user menu settings: {result.get('error')}")
            return {"test_name": "User Filtering Logic Debug", "success": False, "error": result.get("error")}
    
    async def test_filtering_condition_analysis(self) -> Dict:
        """Test 4: Filtering Condition Analysis - Debug the filtering logic"""
        print("🧮 Testing Filtering Condition Analysis...")
        
        if not self.admin_token:
            return {"test_name": "Filtering Condition Analysis", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get both admin settings and user settings to compare
        admin_result = await self.make_request("/admin/menu-settings", headers=headers)
        user_result = await self.make_request(f"/menu-settings/user/{ADMIN_USER_ID}", headers=headers)
        
        if admin_result["success"] and user_result["success"]:
            admin_settings = admin_result["data"]
            user_settings = user_result["data"]
            
            # Analyze desktop menu filtering
            admin_desktop = admin_settings.get("desktop_menu", {})
            admin_desktop_messages = admin_desktop.get("messages", {})
            
            user_desktop = user_settings.get("desktop_menu", {})
            user_has_desktop_messages = "messages" in user_desktop
            
            # Analyze mobile menu filtering
            admin_mobile = admin_settings.get("mobile_menu", {})
            admin_mobile_messages = admin_mobile.get("messages", {})
            
            user_mobile = user_settings.get("mobile_menu", {})
            user_has_mobile_messages = "messages" in user_mobile
            
            # Check the filtering conditions
            desktop_enabled = admin_desktop_messages.get("enabled", True)
            desktop_roles = admin_desktop_messages.get("roles", [])
            desktop_admin_in_roles = "admin" in desktop_roles
            
            mobile_enabled = admin_mobile_messages.get("enabled", True)
            mobile_roles = admin_mobile_messages.get("roles", [])
            mobile_admin_in_roles = "admin" in mobile_roles
            
            # Simulate the filtering logic: item_config.get("enabled", True) and menu_role in item_config.get("roles", [])
            desktop_should_be_included = desktop_enabled and desktop_admin_in_roles
            mobile_should_be_included = mobile_enabled and mobile_admin_in_roles
            
            print(f"  🧮 Filtering Condition Analysis:")
            print(f"    🖥️ Desktop - enabled: {desktop_enabled}, admin in roles: {desktop_admin_in_roles}")
            print(f"    🖥️ Desktop - should be included: {desktop_should_be_included}, actually included: {user_has_desktop_messages}")
            print(f"    📱 Mobile - enabled: {mobile_enabled}, admin in roles: {mobile_admin_in_roles}")
            print(f"    📱 Mobile - should be included: {mobile_should_be_included}, actually included: {user_has_mobile_messages}")
            
            # Identify the issue
            desktop_filtering_correct = desktop_should_be_included == user_has_desktop_messages
            mobile_filtering_correct = mobile_should_be_included == user_has_mobile_messages
            
            print(f"    🎯 Desktop filtering correct: {desktop_filtering_correct}")
            print(f"    🎯 Mobile filtering correct: {mobile_filtering_correct}")
            
            if not desktop_filtering_correct:
                print(f"    🚨 ROOT CAUSE: Desktop filtering logic not working correctly!")
                print(f"       Expected: {desktop_should_be_included}, Got: {user_has_desktop_messages}")
            
            return {
                "test_name": "Filtering Condition Analysis",
                "success": True,
                "desktop_enabled": desktop_enabled,
                "desktop_admin_in_roles": desktop_admin_in_roles,
                "desktop_should_be_included": desktop_should_be_included,
                "desktop_actually_included": user_has_desktop_messages,
                "desktop_filtering_correct": desktop_filtering_correct,
                "mobile_enabled": mobile_enabled,
                "mobile_admin_in_roles": mobile_admin_in_roles,
                "mobile_should_be_included": mobile_should_be_included,
                "mobile_actually_included": user_has_mobile_messages,
                "mobile_filtering_correct": mobile_filtering_correct,
                "filtering_logic_consistent": desktop_filtering_correct and mobile_filtering_correct,
                "root_cause_identified": not desktop_filtering_correct and mobile_filtering_correct
            }
        else:
            print(f"  ❌ Failed to get settings for comparison")
            return {"test_name": "Filtering Condition Analysis", "success": False, "error": "Failed to get both admin and user settings"}
    
    async def run_comprehensive_debug_test(self) -> Dict:
        """Run all desktop menu filtering debug tests"""
        print("🚀 Starting Desktop Menu Filtering Debug Test")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_result = await self.authenticate_admin()
            if not auth_result["success"]:
                return {"error": "Failed to authenticate admin user", "auth_result": auth_result}
            
            # Run all debug tests
            database_state = await self.test_database_state_verification()
            admin_settings = await self.test_admin_settings_debug()
            user_filtering = await self.test_user_filtering_logic_debug()
            filtering_conditions = await self.test_filtering_condition_analysis()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "admin_authentication": auth_result,
                "database_state_verification": database_state,
                "admin_settings_debug": admin_settings,
                "user_filtering_logic_debug": user_filtering,
                "filtering_condition_analysis": filtering_conditions
            }
            
            # Analyze findings
            desktop_filtering_broken = user_filtering.get("desktop_filtering_broken", False)
            mobile_filtering_working = user_filtering.get("mobile_filtering_working", False)
            messages_consistently_disabled = database_state.get("messages_consistently_disabled", False)
            critical_bug_confirmed = user_filtering.get("critical_bug_confirmed", False)
            root_cause_identified = filtering_conditions.get("root_cause_identified", False)
            
            all_results["critical_findings"] = {
                "messages_disabled_in_database": messages_consistently_disabled,
                "desktop_filtering_broken": desktop_filtering_broken,
                "mobile_filtering_working": mobile_filtering_working,
                "inconsistent_filtering_behavior": desktop_filtering_broken and mobile_filtering_working,
                "critical_bug_confirmed": critical_bug_confirmed,
                "root_cause_identified": root_cause_identified,
                "backend_bug_confirmed": desktop_filtering_broken and mobile_filtering_working and messages_consistently_disabled
            }
            
            # Summary
            all_results["summary"] = {
                "test_completed": True,
                "admin_authentication_successful": auth_result["success"],
                "database_state_verified": database_state["success"],
                "admin_settings_verified": admin_settings["success"],
                "user_filtering_analyzed": user_filtering["success"],
                "filtering_conditions_analyzed": filtering_conditions["success"],
                "critical_bug_confirmed": critical_bug_confirmed,
                "expected_finding_confirmed": "desktop_menu.messages should have enabled: false in database, and backend filtering should exclude it from user API response just like mobile_menu.messages"
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Run the desktop menu filtering debug test"""
    tester = DesktopMenuFilteringDebugTester()
    results = await tester.run_comprehensive_debug_test()
    
    print("\n" + "=" * 70)
    print("🎯 DESKTOP MENU FILTERING DEBUG TEST RESULTS")
    print("=" * 70)
    
    # Print critical findings
    critical_findings = results.get("critical_findings", {})
    print("\n🚨 CRITICAL FINDINGS:")
    for key, value in critical_findings.items():
        status = "🚨" if value and "broken" in key else "✅" if value else "❌"
        print(f"  {status} {key.replace('_', ' ').title()}: {value}")
    
    # Print summary
    summary = results.get("summary", {})
    print(f"\n📊 SUMMARY:")
    print(f"  Test Completed: {'✅' if summary.get('test_completed') else '❌'}")
    print(f"  Critical Bug Confirmed: {'🚨 YES' if summary.get('critical_bug_confirmed') else '✅ NO'}")
    
    # Save results to file
    with open('/app/desktop_menu_filtering_debug_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: /app/desktop_menu_filtering_debug_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())