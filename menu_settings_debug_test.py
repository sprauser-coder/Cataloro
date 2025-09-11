#!/usr/bin/env python3
"""
Menu Settings Visibility Debug Testing
Testing user menu settings endpoint to verify disabled items are properly filtered out.

TESTING REQUIREMENTS:
1. Admin Settings Verification - verify current admin menu settings show messages as disabled
2. User Menu Settings API Debug - test user-specific endpoint with debug details  
3. Database State Verification - check actual database state
4. End-to-End Visibility Chain Debug - test complete chain
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://admin-nav-control.preview.emergentagent.com/api"

# Test Users
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "demo@cataloro.com"

class MenuSettingsDebugTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.admin_user_id = None
        self.demo_user_id = None
        
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
    
    async def authenticate_users(self) -> Dict:
        """Authenticate admin and demo users"""
        print("🔐 Authenticating test users...")
        
        # Admin login
        admin_login = await self.make_request("/auth/login", "POST", data={
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        })
        
        if admin_login["success"]:
            self.admin_token = admin_login["data"].get("token")
            self.admin_user_id = admin_login["data"].get("user", {}).get("id")
            print(f"  ✅ Admin authenticated: {self.admin_user_id}")
        else:
            print(f"  ❌ Admin authentication failed: {admin_login.get('error')}")
            return {"success": False, "error": "Admin authentication failed"}
        
        # Demo user login
        demo_login = await self.make_request("/auth/login", "POST", data={
            "email": DEMO_EMAIL,
            "password": "demo_password"
        })
        
        if demo_login["success"]:
            self.demo_token = demo_login["data"].get("token")
            self.demo_user_id = demo_login["data"].get("user", {}).get("id")
            print(f"  ✅ Demo user authenticated: {self.demo_user_id}")
        else:
            print(f"  ❌ Demo user authentication failed: {demo_login.get('error')}")
            return {"success": False, "error": "Demo user authentication failed"}
        
        return {
            "success": True,
            "admin_user_id": self.admin_user_id,
            "demo_user_id": self.demo_user_id
        }
    
    async def test_admin_menu_settings_verification(self) -> Dict:
        """1. Admin Settings Verification - verify current admin menu settings show messages as disabled"""
        print("📋 Testing Admin Menu Settings Verification...")
        
        if not self.admin_token:
            return {"test_name": "Admin Menu Settings Verification", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get current admin menu settings
        admin_settings_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not admin_settings_result["success"]:
            return {
                "test_name": "Admin Menu Settings Verification",
                "success": False,
                "error": f"Failed to get admin menu settings: {admin_settings_result.get('error')}",
                "status": admin_settings_result["status"]
            }
        
        admin_settings = admin_settings_result["data"]
        
        # Check if messages is disabled in mobile_menu
        mobile_menu = admin_settings.get("mobile_menu", {})
        messages_config = mobile_menu.get("messages", {})
        messages_enabled = messages_config.get("enabled", True)
        
        print(f"  📱 Mobile menu messages enabled: {messages_enabled}")
        print(f"  📋 Full messages config: {messages_config}")
        
        # Check desktop menu as well
        desktop_menu = admin_settings.get("desktop_menu", {})
        desktop_messages_config = desktop_menu.get("messages", {})
        desktop_messages_enabled = desktop_messages_config.get("enabled", True)
        
        print(f"  🖥️ Desktop menu messages enabled: {desktop_messages_enabled}")
        
        return {
            "test_name": "Admin Menu Settings Verification",
            "success": True,
            "response_time_ms": admin_settings_result["response_time_ms"],
            "mobile_messages_enabled": messages_enabled,
            "desktop_messages_enabled": desktop_messages_enabled,
            "mobile_messages_config": messages_config,
            "desktop_messages_config": desktop_messages_config,
            "admin_settings_accessible": True,
            "messages_properly_configured": not messages_enabled,  # Should be False (disabled)
            "full_admin_settings": admin_settings
        }
    
    async def test_user_menu_settings_api_debug(self) -> Dict:
        """2. User Menu Settings API Debug - test user-specific endpoint with debug details"""
        print("🔍 Testing User Menu Settings API Debug...")
        
        results = {}
        
        # Test admin user endpoint
        if self.admin_user_id:
            print(f"  Testing admin user endpoint: /menu-settings/user/{self.admin_user_id}")
            admin_user_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
            
            if admin_user_result["success"]:
                admin_user_settings = admin_user_result["data"]
                mobile_menu = admin_user_settings.get("mobile_menu", [])
                
                # Check if messages is in the mobile menu
                print(f"    📋 Mobile menu data type: {type(mobile_menu)}")
                print(f"    📋 Mobile menu content: {mobile_menu}")
                
                messages_in_mobile = False
                mobile_menu_keys = []
                
                if isinstance(mobile_menu, list):
                    messages_in_mobile = any(item.get("key") == "messages" for item in mobile_menu if isinstance(item, dict))
                    mobile_menu_keys = [item.get("key") for item in mobile_menu if isinstance(item, dict)]
                elif isinstance(mobile_menu, dict):
                    messages_in_mobile = "messages" in mobile_menu
                    mobile_menu_keys = list(mobile_menu.keys())
                
                print(f"    ✅ Admin user settings retrieved")
                print(f"    📱 Mobile menu items: {len(mobile_menu) if isinstance(mobile_menu, (list, dict)) else 'N/A'}")
                print(f"    📨 Messages in mobile menu: {messages_in_mobile}")
                print(f"    🔑 Mobile menu keys: {mobile_menu_keys}")
                
                results["admin_user"] = {
                    "success": True,
                    "response_time_ms": admin_user_result["response_time_ms"],
                    "mobile_menu_count": len(mobile_menu) if isinstance(mobile_menu, (list, dict)) else 0,
                    "messages_in_mobile_menu": messages_in_mobile,
                    "mobile_menu_keys": mobile_menu_keys,
                    "mobile_menu_type": type(mobile_menu).__name__,
                    "full_settings": admin_user_settings
                }
            else:
                print(f"    ❌ Admin user settings failed: {admin_user_result.get('error')}")
                results["admin_user"] = {
                    "success": False,
                    "error": admin_user_result.get("error"),
                    "status": admin_user_result["status"]
                }
        
        # Test demo user endpoint
        if self.demo_user_id:
            print(f"  Testing demo user endpoint: /menu-settings/user/{self.demo_user_id}")
            demo_user_result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
            
            if demo_user_result["success"]:
                demo_user_settings = demo_user_result["data"]
                mobile_menu = demo_user_settings.get("mobile_menu", [])
                
                # Check if messages is in the mobile menu
                print(f"    📋 Mobile menu data type: {type(mobile_menu)}")
                print(f"    📋 Mobile menu content: {mobile_menu}")
                
                messages_in_mobile = False
                mobile_menu_keys = []
                
                if isinstance(mobile_menu, list):
                    messages_in_mobile = any(item.get("key") == "messages" for item in mobile_menu if isinstance(item, dict))
                    mobile_menu_keys = [item.get("key") for item in mobile_menu if isinstance(item, dict)]
                elif isinstance(mobile_menu, dict):
                    messages_in_mobile = "messages" in mobile_menu
                    mobile_menu_keys = list(mobile_menu.keys())
                
                print(f"    ✅ Demo user settings retrieved")
                print(f"    📱 Mobile menu items: {len(mobile_menu) if isinstance(mobile_menu, (list, dict)) else 'N/A'}")
                print(f"    📨 Messages in mobile menu: {messages_in_mobile}")
                print(f"    🔑 Mobile menu keys: {mobile_menu_keys}")
                
                results["demo_user"] = {
                    "success": True,
                    "response_time_ms": demo_user_result["response_time_ms"],
                    "mobile_menu_count": len(mobile_menu) if isinstance(mobile_menu, (list, dict)) else 0,
                    "messages_in_mobile_menu": messages_in_mobile,
                    "mobile_menu_keys": mobile_menu_keys,
                    "mobile_menu_type": type(mobile_menu).__name__,
                    "full_settings": demo_user_settings
                }
            else:
                print(f"    ❌ Demo user settings failed: {demo_user_result.get('error')}")
                results["demo_user"] = {
                    "success": False,
                    "error": demo_user_result.get("error"),
                    "status": demo_user_result["status"]
                }
        
        # Check role mapping
        admin_user_data = results.get("admin_user", {}).get("full_settings", {})
        demo_user_data = results.get("demo_user", {}).get("full_settings", {})
        
        admin_role = admin_user_data.get("user_role")
        demo_role = demo_user_data.get("user_role")
        
        print(f"  🔑 Admin user role mapping: {admin_role}")
        print(f"  🔑 Demo user role mapping: {demo_role}")
        
        return {
            "test_name": "User Menu Settings API Debug",
            "admin_user_test": results.get("admin_user", {}),
            "demo_user_test": results.get("demo_user", {}),
            "role_mapping": {
                "admin_role": admin_role,
                "demo_role": demo_role,
                "role_mapping_working": admin_role == "admin" and demo_role in ["buyer", "user"]
            },
            "filtering_working": {
                "admin_messages_filtered": not results.get("admin_user", {}).get("messages_in_mobile_menu", True),
                "demo_messages_filtered": not results.get("demo_user", {}).get("messages_in_mobile_menu", True)
            }
        }
    
    async def test_database_state_verification(self) -> Dict:
        """3. Database State Verification - check actual database state"""
        print("🗄️ Testing Database State Verification...")
        
        if not self.admin_token:
            return {"test_name": "Database State Verification", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get admin menu settings to check database state
        admin_settings_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not admin_settings_result["success"]:
            return {
                "test_name": "Database State Verification",
                "success": False,
                "error": "Failed to get admin settings for database verification"
            }
        
        admin_settings = admin_settings_result["data"]
        
        # Check if settings are properly persisted
        mobile_menu = admin_settings.get("mobile_menu", {})
        messages_config = mobile_menu.get("messages", {})
        
        # Try to update settings to ensure database persistence
        print("  🔄 Testing database persistence by updating settings...")
        
        # Disable messages in mobile menu
        updated_settings = admin_settings.copy()
        if "mobile_menu" not in updated_settings:
            updated_settings["mobile_menu"] = {}
        if "messages" not in updated_settings["mobile_menu"]:
            updated_settings["mobile_menu"]["messages"] = {}
        
        updated_settings["mobile_menu"]["messages"]["enabled"] = False
        
        # Save updated settings
        save_result = await self.make_request("/admin/menu-settings", "POST", data=updated_settings, headers=headers)
        
        if not save_result["success"]:
            return {
                "test_name": "Database State Verification",
                "success": False,
                "error": f"Failed to save settings: {save_result.get('error')}"
            }
        
        print("  ✅ Settings saved successfully")
        
        # Verify settings were saved by retrieving them again
        verify_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if verify_result["success"]:
            verified_settings = verify_result["data"]
            verified_mobile_menu = verified_settings.get("mobile_menu", {})
            verified_messages_config = verified_mobile_menu.get("messages", {})
            verified_messages_enabled = verified_messages_config.get("enabled", True)
            
            print(f"  📋 Verified messages enabled: {verified_messages_enabled}")
            
            return {
                "test_name": "Database State Verification",
                "success": True,
                "database_accessible": True,
                "settings_save_successful": True,
                "settings_persistence_working": not verified_messages_enabled,
                "original_messages_config": messages_config,
                "updated_messages_config": verified_messages_config,
                "messages_properly_disabled": not verified_messages_enabled
            }
        else:
            return {
                "test_name": "Database State Verification",
                "success": False,
                "error": "Failed to verify saved settings"
            }
    
    async def test_end_to_end_visibility_chain(self) -> Dict:
        """4. End-to-End Visibility Chain Debug - test complete chain"""
        print("🔗 Testing End-to-End Visibility Chain Debug...")
        
        if not self.admin_token:
            return {"test_name": "End-to-End Visibility Chain Debug", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Step 1: Admin saves settings (messages disabled)
        print("  Step 1: Admin disables messages in settings...")
        
        # Get current settings
        current_settings_result = await self.make_request("/admin/menu-settings", headers=headers)
        if not current_settings_result["success"]:
            return {
                "test_name": "End-to-End Visibility Chain Debug",
                "success": False,
                "error": "Failed to get current settings"
            }
        
        current_settings = current_settings_result["data"]
        
        # Ensure messages is disabled
        if "mobile_menu" not in current_settings:
            current_settings["mobile_menu"] = {}
        if "messages" not in current_settings["mobile_menu"]:
            current_settings["mobile_menu"]["messages"] = {}
        
        current_settings["mobile_menu"]["messages"]["enabled"] = False
        
        # Save settings
        save_result = await self.make_request("/admin/menu-settings", "POST", data=current_settings, headers=headers)
        step1_success = save_result["success"]
        
        print(f"    {'✅' if step1_success else '❌'} Admin settings save: {step1_success}")
        
        # Step 2: Database stores settings correctly
        print("  Step 2: Verify database storage...")
        
        verify_storage_result = await self.make_request("/admin/menu-settings", headers=headers)
        step2_success = False
        if verify_storage_result["success"]:
            stored_settings = verify_storage_result["data"]
            stored_messages_enabled = stored_settings.get("mobile_menu", {}).get("messages", {}).get("enabled", True)
            step2_success = not stored_messages_enabled
        
        print(f"    {'✅' if step2_success else '❌'} Database storage correct: {step2_success}")
        
        # Step 3: User endpoint filters out disabled messages
        print("  Step 3: Test user endpoint filtering...")
        
        step3_results = {}
        
        # Test admin user
        if self.admin_user_id:
            admin_user_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
            if admin_user_result["success"]:
                admin_mobile_menu = admin_user_result["data"].get("mobile_menu", [])
                
                if isinstance(admin_mobile_menu, list):
                    admin_messages_filtered = not any(item.get("key") == "messages" for item in admin_mobile_menu if isinstance(item, dict))
                elif isinstance(admin_mobile_menu, dict):
                    admin_messages_filtered = "messages" not in admin_mobile_menu
                else:
                    admin_messages_filtered = True  # If no mobile menu, messages is filtered
                
                step3_results["admin_filtered"] = admin_messages_filtered
                print(f"    {'✅' if admin_messages_filtered else '❌'} Admin user messages filtered: {admin_messages_filtered}")
        
        # Test demo user
        if self.demo_user_id:
            demo_user_result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
            if demo_user_result["success"]:
                demo_mobile_menu = demo_user_result["data"].get("mobile_menu", [])
                
                if isinstance(demo_mobile_menu, list):
                    demo_messages_filtered = not any(item.get("key") == "messages" for item in demo_mobile_menu if isinstance(item, dict))
                elif isinstance(demo_mobile_menu, dict):
                    demo_messages_filtered = "messages" not in demo_mobile_menu
                else:
                    demo_messages_filtered = True  # If no mobile menu, messages is filtered
                
                step3_results["demo_filtered"] = demo_messages_filtered
                print(f"    {'✅' if demo_messages_filtered else '❌'} Demo user messages filtered: {demo_messages_filtered}")
        
        step3_success = all(step3_results.values())
        
        # Step 4: Frontend should receive filtered results without messages
        print("  Step 4: Verify complete chain working...")
        
        complete_chain_working = step1_success and step2_success and step3_success
        
        print(f"  🔗 Complete visibility chain working: {'✅' if complete_chain_working else '❌'}")
        
        return {
            "test_name": "End-to-End Visibility Chain Debug",
            "success": complete_chain_working,
            "step1_admin_saves_settings": step1_success,
            "step2_database_stores_correctly": step2_success,
            "step3_user_endpoint_filters": step3_success,
            "step3_filtering_details": step3_results,
            "step4_complete_chain_working": complete_chain_working,
            "chain_breakdown_point": self.identify_chain_breakdown(step1_success, step2_success, step3_success)
        }
    
    def identify_chain_breakdown(self, step1: bool, step2: bool, step3: bool) -> str:
        """Identify where the visibility chain breaks down"""
        if not step1:
            return "Admin settings save failing"
        elif not step2:
            return "Database persistence failing"
        elif not step3:
            return "User endpoint filtering failing"
        else:
            return "No breakdown - chain working correctly"
    
    async def run_comprehensive_debug_test(self) -> Dict:
        """Run all menu settings visibility debug tests"""
        print("🚀 Starting Menu Settings Visibility Debug Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Authenticate users first
            auth_result = await self.authenticate_users()
            if not auth_result["success"]:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Authentication failed",
                    "details": auth_result
                }
            
            # Run all test suites
            admin_verification = await self.test_admin_menu_settings_verification()
            user_api_debug = await self.test_user_menu_settings_api_debug()
            database_verification = await self.test_database_state_verification()
            end_to_end_chain = await self.test_end_to_end_visibility_chain()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "authentication": auth_result,
                "admin_settings_verification": admin_verification,
                "user_menu_settings_api_debug": user_api_debug,
                "database_state_verification": database_verification,
                "end_to_end_visibility_chain_debug": end_to_end_chain
            }
            
            # Calculate overall success metrics
            test_results = [
                admin_verification.get("success", False),
                user_api_debug.get("admin_user_test", {}).get("success", False),
                user_api_debug.get("demo_user_test", {}).get("success", False),
                database_verification.get("success", False),
                end_to_end_chain.get("success", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            # Check specific issues
            messages_properly_disabled = admin_verification.get("messages_properly_configured", False)
            filtering_working = user_api_debug.get("filtering_working", {})
            admin_filtered = filtering_working.get("admin_messages_filtered", False)
            demo_filtered = filtering_working.get("demo_messages_filtered", False)
            database_persistence = database_verification.get("settings_persistence_working", False)
            complete_chain = end_to_end_chain.get("step4_complete_chain_working", False)
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "admin_settings_accessible": admin_verification.get("admin_settings_accessible", False),
                "messages_properly_disabled_in_admin": messages_properly_disabled,
                "admin_user_messages_filtered": admin_filtered,
                "demo_user_messages_filtered": demo_filtered,
                "database_persistence_working": database_persistence,
                "complete_visibility_chain_working": complete_chain,
                "role_mapping_working": user_api_debug.get("role_mapping", {}).get("role_mapping_working", False),
                "chain_breakdown_point": end_to_end_chain.get("chain_breakdown_point", "Unknown"),
                "critical_issue_identified": not (admin_filtered and demo_filtered),
                "all_tests_passed": overall_success_rate == 100
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution"""
    tester = MenuSettingsDebugTester()
    results = await tester.run_comprehensive_debug_test()
    
    print("\n" + "=" * 70)
    print("📊 MENU SETTINGS VISIBILITY DEBUG TEST RESULTS")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"🎯 Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"⚙️ Admin Settings Accessible: {'✅' if summary.get('admin_settings_accessible') else '❌'}")
    print(f"📋 Messages Disabled in Admin: {'✅' if summary.get('messages_properly_disabled_in_admin') else '❌'}")
    print(f"👤 Admin User Messages Filtered: {'✅' if summary.get('admin_user_messages_filtered') else '❌'}")
    print(f"👥 Demo User Messages Filtered: {'✅' if summary.get('demo_user_messages_filtered') else '❌'}")
    print(f"🗄️ Database Persistence Working: {'✅' if summary.get('database_persistence_working') else '❌'}")
    print(f"🔗 Complete Chain Working: {'✅' if summary.get('complete_visibility_chain_working') else '❌'}")
    print(f"🔑 Role Mapping Working: {'✅' if summary.get('role_mapping_working') else '❌'}")
    
    if summary.get('critical_issue_identified'):
        print(f"🚨 CRITICAL ISSUE: {summary.get('chain_breakdown_point', 'Unknown issue')}")
    
    print(f"\n📝 Chain Breakdown Point: {summary.get('chain_breakdown_point', 'Unknown')}")
    
    # Save detailed results to file
    with open('/app/menu_settings_debug_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: /app/menu_settings_debug_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())