#!/usr/bin/env python3
"""
Menu Settings Visibility Functionality End-to-End Testing
Testing the complete visibility workflow from admin settings to user navigation
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://marketplace-fix-9.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

# Demo User Configuration  
DEMO_EMAIL = "demo@cataloro.com"
DEMO_PASSWORD = "demo_password"

class MenuSettingsVisibilityTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.admin_user_id = None
        self.demo_user_id = None
        self.test_results = []
        
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
        print("🔐 Authenticating users...")
        
        # Authenticate admin user
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            self.admin_user_id = admin_result["data"].get("user", {}).get("id", "")
            print(f"  ✅ Admin authenticated: {self.admin_user_id}")
        else:
            print(f"  ❌ Admin authentication failed: {admin_result.get('error')}")
            return {"success": False, "error": "Admin authentication failed"}
        
        # Authenticate demo user
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            self.demo_user_id = demo_result["data"].get("user", {}).get("id", "")
            print(f"  ✅ Demo user authenticated: {self.demo_user_id}")
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error')}")
            return {"success": False, "error": "Demo user authentication failed"}
        
        return {
            "success": True,
            "admin_token": bool(self.admin_token),
            "demo_token": bool(self.demo_token),
            "admin_user_id": self.admin_user_id,
            "demo_user_id": self.demo_user_id
        }
    
    async def test_admin_menu_settings_update(self) -> Dict:
        """Test 1: Admin Menu Settings Update Test - disabling a menu item via admin interface"""
        print("🔧 Testing Admin Menu Settings Update...")
        
        if not self.admin_token:
            return {"test_name": "Admin Menu Settings Update", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Step 1: Get current menu settings
        print("  Step 1: Getting current menu settings...")
        current_settings_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not current_settings_result["success"]:
            return {
                "test_name": "Admin Menu Settings Update",
                "error": f"Failed to get current settings: {current_settings_result.get('error')}",
                "step_failed": "get_current_settings"
            }
        
        current_settings = current_settings_result["data"]
        print(f"    ✅ Current settings retrieved ({current_settings_result['response_time_ms']:.0f}ms)")
        
        # Step 2: Modify settings to disable "messages" menu item
        print("  Step 2: Disabling 'messages' menu item...")
        
        # Create modified settings with messages disabled
        modified_settings = json.loads(json.dumps(current_settings))  # Deep copy
        
        # Find and disable messages in both desktop and mobile menus
        messages_disabled = False
        
        if "desktop" in modified_settings:
            for item in modified_settings["desktop"]:
                if item.get("key") == "messages" or "message" in item.get("key", "").lower():
                    item["enabled"] = False
                    messages_disabled = True
                    print(f"    📱 Disabled messages in desktop menu: {item.get('key')}")
        
        if "mobile" in modified_settings:
            for item in modified_settings["mobile"]:
                if item.get("key") == "messages" or "message" in item.get("key", "").lower():
                    item["enabled"] = False
                    messages_disabled = True
                    print(f"    📱 Disabled messages in mobile menu: {item.get('key')}")
        
        if not messages_disabled:
            # If no messages key found, try to find it by label
            for menu_type in ["desktop", "mobile"]:
                if menu_type in modified_settings:
                    for item in modified_settings[menu_type]:
                        if "message" in item.get("label", "").lower():
                            item["enabled"] = False
                            messages_disabled = True
                            print(f"    📱 Disabled messages by label in {menu_type} menu: {item.get('label')}")
                            break
        
        if not messages_disabled:
            return {
                "test_name": "Admin Menu Settings Update",
                "error": "Messages menu item not found in current settings",
                "current_settings_structure": {
                    "desktop_keys": [item.get("key") for item in current_settings.get("desktop", [])],
                    "mobile_keys": [item.get("key") for item in current_settings.get("mobile", [])]
                }
            }
        
        # Step 3: Save modified settings
        print("  Step 3: Saving modified settings...")
        save_result = await self.make_request("/admin/menu-settings", "POST", data=modified_settings, headers=headers)
        
        if not save_result["success"]:
            return {
                "test_name": "Admin Menu Settings Update",
                "error": f"Failed to save settings: {save_result.get('error')}",
                "step_failed": "save_settings"
            }
        
        print(f"    ✅ Settings saved successfully ({save_result['response_time_ms']:.0f}ms)")
        
        # Step 4: Verify settings were saved correctly
        print("  Step 4: Verifying settings were saved...")
        verify_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not verify_result["success"]:
            return {
                "test_name": "Admin Menu Settings Update",
                "error": f"Failed to verify settings: {verify_result.get('error')}",
                "step_failed": "verify_settings"
            }
        
        saved_settings = verify_result["data"]
        
        # Check if messages is disabled in saved settings
        messages_disabled_in_saved = False
        disabled_items = []
        
        for menu_type in ["desktop", "mobile"]:
            if menu_type in saved_settings:
                for item in saved_settings[menu_type]:
                    if (item.get("key") == "messages" or "message" in item.get("key", "").lower() or 
                        "message" in item.get("label", "").lower()) and not item.get("enabled", True):
                        messages_disabled_in_saved = True
                        disabled_items.append(f"{menu_type}:{item.get('key', item.get('label'))}")
        
        print(f"    ✅ Settings verification complete - Messages disabled: {messages_disabled_in_saved}")
        
        return {
            "test_name": "Admin Menu Settings Update",
            "success": True,
            "messages_found_and_disabled": messages_disabled,
            "settings_saved_successfully": save_result["success"],
            "settings_verified_correctly": messages_disabled_in_saved,
            "disabled_items": disabled_items,
            "save_response_time_ms": save_result["response_time_ms"],
            "verify_response_time_ms": verify_result["response_time_ms"],
            "database_persistence_working": messages_disabled_in_saved
        }
    
    async def test_user_menu_settings_retrieval(self) -> Dict:
        """Test 2: User Menu Settings Retrieval Test - getting user-specific menu settings"""
        print("👤 Testing User Menu Settings Retrieval...")
        
        if not self.admin_user_id or not self.demo_user_id:
            return {"test_name": "User Menu Settings Retrieval", "error": "User IDs not available"}
        
        # Test both admin and demo user menu settings retrieval
        test_results = {}
        
        # Test admin user menu settings
        print("  Testing admin user menu settings...")
        admin_menu_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
        
        if admin_menu_result["success"]:
            admin_menu_data = admin_menu_result["data"]
            
            # Check if disabled items are filtered out or marked as disabled
            messages_visible_admin = self.check_messages_visibility(admin_menu_data)
            
            test_results["admin_user"] = {
                "endpoint_accessible": True,
                "response_time_ms": admin_menu_result["response_time_ms"],
                "has_menu_data": bool(admin_menu_data),
                "messages_visible": messages_visible_admin,
                "menu_structure": self.analyze_menu_structure(admin_menu_data)
            }
            
            print(f"    ✅ Admin menu settings retrieved - Messages visible: {messages_visible_admin}")
        else:
            test_results["admin_user"] = {
                "endpoint_accessible": False,
                "error": admin_menu_result.get("error"),
                "status": admin_menu_result["status"]
            }
            print(f"    ❌ Admin menu settings failed: {admin_menu_result.get('error')}")
        
        # Test demo user menu settings
        print("  Testing demo user menu settings...")
        demo_menu_result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
        
        if demo_menu_result["success"]:
            demo_menu_data = demo_menu_result["data"]
            
            # Check if disabled items are filtered out or marked as disabled
            messages_visible_demo = self.check_messages_visibility(demo_menu_data)
            
            test_results["demo_user"] = {
                "endpoint_accessible": True,
                "response_time_ms": demo_menu_result["response_time_ms"],
                "has_menu_data": bool(demo_menu_data),
                "messages_visible": messages_visible_demo,
                "menu_structure": self.analyze_menu_structure(demo_menu_data)
            }
            
            print(f"    ✅ Demo menu settings retrieved - Messages visible: {messages_visible_demo}")
        else:
            test_results["demo_user"] = {
                "endpoint_accessible": False,
                "error": demo_menu_result.get("error"),
                "status": demo_menu_result["status"]
            }
            print(f"    ❌ Demo menu settings failed: {demo_menu_result.get('error')}")
        
        # Test role-based filtering
        admin_accessible = test_results.get("admin_user", {}).get("endpoint_accessible", False)
        demo_accessible = test_results.get("demo_user", {}).get("endpoint_accessible", False)
        
        # Check if filtering logic is working correctly
        admin_messages_visible = test_results.get("admin_user", {}).get("messages_visible", True)
        demo_messages_visible = test_results.get("demo_user", {}).get("messages_visible", True)
        
        filtering_working = not admin_messages_visible and not demo_messages_visible  # Both should have messages disabled
        
        return {
            "test_name": "User Menu Settings Retrieval",
            "success": admin_accessible and demo_accessible,
            "admin_user_endpoint_working": admin_accessible,
            "demo_user_endpoint_working": demo_accessible,
            "filtering_logic_working": filtering_working,
            "messages_properly_filtered": not admin_messages_visible and not demo_messages_visible,
            "role_based_access_working": admin_accessible and demo_accessible,
            "detailed_results": test_results
        }
    
    async def test_visibility_logic_chain(self) -> Dict:
        """Test 3: Visibility Logic Chain Test - complete visibility chain from backend to frontend"""
        print("🔗 Testing Visibility Logic Chain...")
        
        if not self.admin_token:
            return {"test_name": "Visibility Logic Chain", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        chain_results = {}
        
        # Step 1: Verify admin settings are saved correctly with enabled: false
        print("  Step 1: Verifying admin settings storage...")
        admin_settings_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if admin_settings_result["success"]:
            admin_settings = admin_settings_result["data"]
            
            # Check if messages is disabled in admin settings
            messages_disabled_in_admin = False
            for menu_type in ["desktop", "mobile"]:
                if menu_type in admin_settings:
                    for item in admin_settings[menu_type]:
                        if (item.get("key") == "messages" or "message" in item.get("key", "").lower() or 
                            "message" in item.get("label", "").lower()) and not item.get("enabled", True):
                            messages_disabled_in_admin = True
                            break
            
            chain_results["admin_settings_storage"] = {
                "success": True,
                "messages_disabled": messages_disabled_in_admin,
                "response_time_ms": admin_settings_result["response_time_ms"]
            }
            
            print(f"    ✅ Admin settings verified - Messages disabled: {messages_disabled_in_admin}")
        else:
            chain_results["admin_settings_storage"] = {
                "success": False,
                "error": admin_settings_result.get("error")
            }
            print(f"    ❌ Admin settings verification failed")
        
        # Step 2: Verify user endpoint filters/processes disabled items correctly
        print("  Step 2: Verifying user endpoint filtering...")
        
        if self.admin_user_id:
            user_settings_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
            
            if user_settings_result["success"]:
                user_settings = user_settings_result["data"]
                
                # Check if messages is filtered out or marked as disabled
                messages_in_user_settings = self.check_messages_visibility(user_settings)
                
                chain_results["user_endpoint_filtering"] = {
                    "success": True,
                    "messages_filtered_correctly": not messages_in_user_settings,
                    "response_time_ms": user_settings_result["response_time_ms"],
                    "user_settings_structure": self.analyze_menu_structure(user_settings)
                }
                
                print(f"    ✅ User endpoint filtering verified - Messages filtered: {not messages_in_user_settings}")
            else:
                chain_results["user_endpoint_filtering"] = {
                    "success": False,
                    "error": user_settings_result.get("error")
                }
                print(f"    ❌ User endpoint filtering failed")
        
        # Step 3: Test the complete chain consistency
        print("  Step 3: Testing complete chain consistency...")
        
        admin_disabled = chain_results.get("admin_settings_storage", {}).get("messages_disabled", False)
        user_filtered = chain_results.get("user_endpoint_filtering", {}).get("messages_filtered_correctly", False)
        
        chain_consistency = admin_disabled and user_filtered
        
        chain_results["chain_consistency"] = {
            "admin_settings_consistent": admin_disabled,
            "user_filtering_consistent": user_filtered,
            "complete_chain_working": chain_consistency
        }
        
        print(f"    ✅ Chain consistency verified: {chain_consistency}")
        
        return {
            "test_name": "Visibility Logic Chain",
            "success": chain_consistency,
            "admin_settings_working": chain_results.get("admin_settings_storage", {}).get("success", False),
            "user_endpoint_working": chain_results.get("user_endpoint_filtering", {}).get("success", False),
            "complete_chain_working": chain_consistency,
            "messages_properly_disabled_throughout_chain": admin_disabled and user_filtered,
            "detailed_chain_results": chain_results
        }
    
    async def test_menu_item_key_matching(self) -> Dict:
        """Test 4: Menu Item Key Matching Test - verify menu item keys match between admin and user contexts"""
        print("🔑 Testing Menu Item Key Matching...")
        
        if not self.admin_token or not self.admin_user_id:
            return {"test_name": "Menu Item Key Matching", "error": "Admin token or user ID not available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get admin menu settings
        print("  Getting admin menu settings...")
        admin_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not admin_result["success"]:
            return {
                "test_name": "Menu Item Key Matching",
                "error": f"Failed to get admin settings: {admin_result.get('error')}"
            }
        
        # Get user menu settings
        print("  Getting user menu settings...")
        user_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
        
        if not user_result["success"]:
            return {
                "test_name": "Menu Item Key Matching",
                "error": f"Failed to get user settings: {user_result.get('error')}"
            }
        
        admin_settings = admin_result["data"]
        user_settings = user_result["data"]
        
        # Extract keys from both contexts
        admin_keys = self.extract_menu_keys(admin_settings)
        user_keys = self.extract_menu_keys(user_settings)
        
        # Check for key consistency
        key_matching_results = self.compare_menu_keys(admin_keys, user_keys)
        
        # Check specific keys mentioned in the review
        expected_keys = ["messages", "create_listing", "admin_panel", "browse", "profile", "favorites"]
        key_presence = {}
        
        for key in expected_keys:
            key_presence[key] = {
                "in_admin": key in admin_keys.get("all_keys", []),
                "in_user": key in user_keys.get("all_keys", [])
            }
        
        print(f"    ✅ Key matching analysis complete")
        print(f"    📊 Admin keys: {len(admin_keys.get('all_keys', []))}, User keys: {len(user_keys.get('all_keys', []))}")
        
        return {
            "test_name": "Menu Item Key Matching",
            "success": True,
            "admin_keys_extracted": len(admin_keys.get("all_keys", [])),
            "user_keys_extracted": len(user_keys.get("all_keys", [])),
            "key_matching_results": key_matching_results,
            "expected_key_presence": key_presence,
            "keys_consistent_between_contexts": key_matching_results.get("keys_match", False),
            "no_key_mismatches": len(key_matching_results.get("mismatched_keys", [])) == 0,
            "admin_keys": admin_keys,
            "user_keys": user_keys
        }
    
    def check_messages_visibility(self, menu_data: Dict) -> bool:
        """Check if messages menu item is visible in menu data"""
        if not menu_data:
            return False
        
        for menu_type in ["desktop", "mobile"]:
            if menu_type in menu_data:
                for item in menu_data[menu_type]:
                    if (item.get("key") == "messages" or "message" in item.get("key", "").lower() or 
                        "message" in item.get("label", "").lower()):
                        # Check if item is enabled (visible)
                        return item.get("enabled", True)
        
        return False  # Messages not found, so not visible
    
    def analyze_menu_structure(self, menu_data: Dict) -> Dict:
        """Analyze menu structure and return summary"""
        if not menu_data:
            return {"total_items": 0, "desktop_items": 0, "mobile_items": 0}
        
        desktop_items = len(menu_data.get("desktop", []))
        mobile_items = len(menu_data.get("mobile", []))
        
        return {
            "total_items": desktop_items + mobile_items,
            "desktop_items": desktop_items,
            "mobile_items": mobile_items,
            "has_desktop_menu": "desktop" in menu_data,
            "has_mobile_menu": "mobile" in menu_data
        }
    
    def extract_menu_keys(self, menu_data: Dict) -> Dict:
        """Extract all menu keys from menu data"""
        all_keys = []
        desktop_keys = []
        mobile_keys = []
        
        if "desktop" in menu_data:
            for item in menu_data["desktop"]:
                key = item.get("key", item.get("label", "")).lower()
                desktop_keys.append(key)
                all_keys.append(key)
        
        if "mobile" in menu_data:
            for item in menu_data["mobile"]:
                key = item.get("key", item.get("label", "")).lower()
                mobile_keys.append(key)
                if key not in all_keys:
                    all_keys.append(key)
        
        return {
            "all_keys": all_keys,
            "desktop_keys": desktop_keys,
            "mobile_keys": mobile_keys
        }
    
    def compare_menu_keys(self, admin_keys: Dict, user_keys: Dict) -> Dict:
        """Compare menu keys between admin and user contexts"""
        admin_all = set(admin_keys.get("all_keys", []))
        user_all = set(user_keys.get("all_keys", []))
        
        common_keys = admin_all.intersection(user_all)
        admin_only = admin_all - user_all
        user_only = user_all - admin_all
        
        return {
            "keys_match": len(admin_only) == 0 and len(user_only) == 0,
            "common_keys": list(common_keys),
            "admin_only_keys": list(admin_only),
            "user_only_keys": list(user_only),
            "mismatched_keys": list(admin_only.union(user_only))
        }
    
    async def run_comprehensive_menu_settings_test(self) -> Dict:
        """Run all menu settings visibility tests"""
        print("🚀 Starting Menu Settings Visibility Functionality Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Authenticate users first
            auth_result = await self.authenticate_users()
            if not auth_result["success"]:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Authentication failed",
                    "auth_result": auth_result
                }
            
            # Run all test suites
            admin_update_test = await self.test_admin_menu_settings_update()
            user_retrieval_test = await self.test_user_menu_settings_retrieval()
            visibility_chain_test = await self.test_visibility_logic_chain()
            key_matching_test = await self.test_menu_item_key_matching()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "authentication": auth_result,
                "admin_menu_settings_update": admin_update_test,
                "user_menu_settings_retrieval": user_retrieval_test,
                "visibility_logic_chain": visibility_chain_test,
                "menu_item_key_matching": key_matching_test
            }
            
            # Calculate overall success metrics
            test_results = [
                admin_update_test.get("success", False),
                user_retrieval_test.get("success", False),
                visibility_chain_test.get("success", False),
                key_matching_test.get("success", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            # Check specific functionality
            admin_settings_working = admin_update_test.get("database_persistence_working", False)
            user_filtering_working = user_retrieval_test.get("filtering_logic_working", False)
            complete_chain_working = visibility_chain_test.get("complete_chain_working", False)
            key_consistency_working = key_matching_test.get("keys_consistent_between_contexts", False)
            
            # Determine if the reported issue is resolved
            messages_properly_disabled = (
                admin_update_test.get("messages_found_and_disabled", False) and
                user_retrieval_test.get("messages_properly_filtered", False) and
                visibility_chain_test.get("messages_properly_disabled_throughout_chain", False)
            )
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "admin_settings_update_working": admin_settings_working,
                "user_settings_retrieval_working": user_filtering_working,
                "complete_visibility_chain_working": complete_chain_working,
                "menu_key_consistency_working": key_consistency_working,
                "messages_visibility_issue_resolved": messages_properly_disabled,
                "all_tests_passed": overall_success_rate == 100,
                "critical_functionality_working": admin_settings_working and user_filtering_working and complete_chain_working
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution function"""
    tester = MenuSettingsVisibilityTester()
    results = await tester.run_comprehensive_menu_settings_test()
    
    print("\n" + "=" * 70)
    print("📊 MENU SETTINGS VISIBILITY TEST RESULTS")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"Admin Settings Update: {'✅' if summary.get('admin_settings_update_working') else '❌'}")
    print(f"User Settings Retrieval: {'✅' if summary.get('user_settings_retrieval_working') else '❌'}")
    print(f"Complete Visibility Chain: {'✅' if summary.get('complete_visibility_chain_working') else '❌'}")
    print(f"Menu Key Consistency: {'✅' if summary.get('menu_key_consistency_working') else '❌'}")
    print(f"Messages Visibility Issue Resolved: {'✅' if summary.get('messages_visibility_issue_resolved') else '❌'}")
    
    print("\n📋 Detailed Results:")
    print(json.dumps(results, indent=2, default=str))
    
    return results

if __name__ == "__main__":
    asyncio.run(main())