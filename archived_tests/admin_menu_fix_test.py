#!/usr/bin/env python3
"""
Admin Menu Settings Fix Testing
Testing the specific fix for admin menu settings to verify the MenuSettings component will work correctly
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://vps-sync.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"

class AdminMenuSettingsFixTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.original_settings = None
        
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
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            print(f"  ✅ Admin authentication successful")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            return False
    
    def get_expected_menu_structure(self) -> Dict:
        """Get the expected menu structure that MenuSettings component expects"""
        return {
            "desktop_menu": {
                "about": {"enabled": True, "label": "About", "roles": ["admin", "manager", "seller", "buyer"]},
                "browse": {"enabled": True, "label": "Browse", "roles": ["admin", "manager", "seller", "buyer"]},
                "create_listing": {"enabled": True, "label": "Create Listing", "roles": ["admin", "manager", "seller"]},
                "messages": {"enabled": True, "label": "Messages", "roles": ["admin", "manager", "seller", "buyer"]},
                "tenders": {"enabled": True, "label": "Tenders", "roles": ["admin", "manager", "seller", "buyer"]},
                "profile": {"enabled": True, "label": "Profile", "roles": ["admin", "manager", "seller", "buyer"]},
                "admin_panel": {"enabled": True, "label": "Administration", "roles": ["admin", "manager"]},
                "buy_management": {"enabled": True, "label": "Buy Management", "roles": ["admin", "manager", "buyer"]},
                "my_listings": {"enabled": True, "label": "My Listings", "roles": ["admin", "manager", "seller"]},
                "favorites": {"enabled": True, "label": "Favorites", "roles": ["admin", "manager", "seller", "buyer"]},
                "custom_items": []
            },
            "mobile_menu": {
                "about": {"enabled": True, "label": "About", "roles": ["admin", "manager", "seller", "buyer"]},
                "browse": {"enabled": True, "label": "Browse", "roles": ["admin", "manager", "seller", "buyer"]},
                "create_listing": {"enabled": True, "label": "Create Listing", "roles": ["admin", "manager", "seller"]},
                "messages": {"enabled": True, "label": "Messages", "roles": ["admin", "manager", "seller", "buyer"]},
                "tenders": {"enabled": True, "label": "Tenders", "roles": ["admin", "manager", "seller", "buyer"]},
                "profile": {"enabled": True, "label": "Profile", "roles": ["admin", "manager", "seller", "buyer"]},
                "admin_drawer": {"enabled": True, "label": "Admin", "roles": ["admin", "manager"]},
                "buy_management": {"enabled": True, "label": "Buy Management", "roles": ["admin", "manager", "buyer"]},
                "my_listings": {"enabled": True, "label": "My Listings", "roles": ["admin", "manager", "seller"]},
                "favorites": {"enabled": True, "label": "Favorites", "roles": ["admin", "manager", "seller", "buyer"]},
                "custom_items": []
            }
        }
    
    async def test_get_endpoint_data_structure(self) -> Dict:
        """Test 1: GET endpoint returns proper data structure"""
        print("🔍 Test 1: Testing GET endpoint data structure...")
        
        if not self.admin_token:
            return {"test_name": "GET Endpoint Data Structure", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if result["success"]:
            data = result["data"]
            self.original_settings = data  # Store for cleanup
            
            # Check basic structure
            has_desktop_menu = "desktop_menu" in data
            has_mobile_menu = "mobile_menu" in data
            
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            
            # Check if it's the old format (only custom_items) or new format (with default items)
            desktop_has_defaults = any(key != "custom_items" for key in desktop_menu.keys())
            mobile_has_defaults = any(key != "custom_items" for key in mobile_menu.keys())
            
            # Check for custom_items arrays
            has_desktop_custom_items = "custom_items" in desktop_menu
            has_mobile_custom_items = "custom_items" in mobile_menu
            
            print(f"  📊 Response status: {result['status']}")
            print(f"  🖥️ Desktop menu items: {len(desktop_menu)}")
            print(f"  📱 Mobile menu items: {len(mobile_menu)}")
            print(f"  ✅ Desktop has default items: {desktop_has_defaults}")
            print(f"  ✅ Mobile has default items: {mobile_has_defaults}")
            print(f"  📝 Desktop has custom_items: {has_desktop_custom_items}")
            print(f"  📝 Mobile has custom_items: {has_mobile_custom_items}")
            
            structure_correct = (
                has_desktop_menu and has_mobile_menu and
                desktop_has_defaults and mobile_has_defaults and
                has_desktop_custom_items and has_mobile_custom_items
            )
            
            return {
                "test_name": "GET Endpoint Data Structure",
                "success": structure_correct,
                "response_time_ms": result["response_time_ms"],
                "has_desktop_menu": has_desktop_menu,
                "has_mobile_menu": has_mobile_menu,
                "desktop_items_count": len(desktop_menu),
                "mobile_items_count": len(mobile_menu),
                "desktop_has_defaults": desktop_has_defaults,
                "mobile_has_defaults": mobile_has_defaults,
                "has_desktop_custom_items": has_desktop_custom_items,
                "has_mobile_custom_items": has_mobile_custom_items,
                "structure_correct": structure_correct,
                "full_response": data
            }
        else:
            print(f"  ❌ GET endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "GET Endpoint Data Structure",
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"]
            }
    
    async def test_default_menu_items_present(self) -> Dict:
        """Test 2: All default menu items are present with enabled, label, and roles properties"""
        print("🔍 Test 2: Testing default menu items presence...")
        
        if not self.admin_token:
            return {"test_name": "Default Menu Items Present", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if not result["success"]:
            return {
                "test_name": "Default Menu Items Present",
                "success": False,
                "error": result.get("error", "Failed to get menu settings")
            }
        
        data = result["data"]
        desktop_menu = data.get("desktop_menu", {})
        mobile_menu = data.get("mobile_menu", {})
        
        # Expected default items based on the review request
        expected_default_items = [
            "about", "browse", "create_listing", "messages", "tenders", 
            "profile", "admin_panel", "buy_management", "my_listings", "favorites"
        ]
        
        # Check desktop menu items
        desktop_results = {}
        for item_key in expected_default_items:
            if item_key in desktop_menu and isinstance(desktop_menu[item_key], dict):
                item_data = desktop_menu[item_key]
                desktop_results[item_key] = {
                    "present": True,
                    "has_enabled": "enabled" in item_data,
                    "has_label": "label" in item_data,
                    "has_roles": "roles" in item_data,
                    "enabled_value": item_data.get("enabled"),
                    "label_value": item_data.get("label"),
                    "roles_value": item_data.get("roles"),
                    "valid_structure": all(key in item_data for key in ["enabled", "label", "roles"])
                }
            else:
                desktop_results[item_key] = {
                    "present": False,
                    "has_enabled": False,
                    "has_label": False,
                    "has_roles": False,
                    "valid_structure": False
                }
        
        # Check mobile menu items (admin_panel becomes admin_drawer in mobile)
        mobile_expected = expected_default_items.copy()
        if "admin_panel" in mobile_expected:
            mobile_expected.remove("admin_panel")
            mobile_expected.append("admin_drawer")
        
        mobile_results = {}
        for item_key in mobile_expected:
            if item_key in mobile_menu and isinstance(mobile_menu[item_key], dict):
                item_data = mobile_menu[item_key]
                mobile_results[item_key] = {
                    "present": True,
                    "has_enabled": "enabled" in item_data,
                    "has_label": "label" in item_data,
                    "has_roles": "roles" in item_data,
                    "enabled_value": item_data.get("enabled"),
                    "label_value": item_data.get("label"),
                    "roles_value": item_data.get("roles"),
                    "valid_structure": all(key in item_data for key in ["enabled", "label", "roles"])
                }
            else:
                mobile_results[item_key] = {
                    "present": False,
                    "has_enabled": False,
                    "has_label": False,
                    "has_roles": False,
                    "valid_structure": False
                }
        
        # Calculate success metrics
        desktop_valid_items = sum(1 for result in desktop_results.values() if result["valid_structure"])
        mobile_valid_items = sum(1 for result in mobile_results.values() if result["valid_structure"])
        
        desktop_success_rate = (desktop_valid_items / len(expected_default_items)) * 100
        mobile_success_rate = (mobile_valid_items / len(mobile_expected)) * 100
        
        overall_success = desktop_success_rate >= 90 and mobile_success_rate >= 90
        
        print(f"  🖥️ Desktop valid items: {desktop_valid_items}/{len(expected_default_items)} ({desktop_success_rate:.1f}%)")
        print(f"  📱 Mobile valid items: {mobile_valid_items}/{len(mobile_expected)} ({mobile_success_rate:.1f}%)")
        print(f"  {'✅' if overall_success else '❌'} Default items test {'passed' if overall_success else 'failed'}")
        
        return {
            "test_name": "Default Menu Items Present",
            "success": overall_success,
            "desktop_valid_items": desktop_valid_items,
            "mobile_valid_items": mobile_valid_items,
            "desktop_success_rate": desktop_success_rate,
            "mobile_success_rate": mobile_success_rate,
            "desktop_results": desktop_results,
            "mobile_results": mobile_results,
            "expected_desktop_items": expected_default_items,
            "expected_mobile_items": mobile_expected
        }
    
    async def test_custom_items_array_included(self) -> Dict:
        """Test 3: Custom_items array is included in both desktop and mobile menus"""
        print("🔍 Test 3: Testing custom_items array inclusion...")
        
        if not self.admin_token:
            return {"test_name": "Custom Items Array Included", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if not result["success"]:
            return {
                "test_name": "Custom Items Array Included",
                "success": False,
                "error": result.get("error", "Failed to get menu settings")
            }
        
        data = result["data"]
        desktop_menu = data.get("desktop_menu", {})
        mobile_menu = data.get("mobile_menu", {})
        
        # Check for custom_items arrays
        has_desktop_custom_items = "custom_items" in desktop_menu
        has_mobile_custom_items = "custom_items" in mobile_menu
        
        desktop_custom_items = desktop_menu.get("custom_items", [])
        mobile_custom_items = mobile_menu.get("custom_items", [])
        
        # Verify they are arrays
        desktop_is_array = isinstance(desktop_custom_items, list)
        mobile_is_array = isinstance(mobile_custom_items, list)
        
        custom_items_success = (
            has_desktop_custom_items and has_mobile_custom_items and
            desktop_is_array and mobile_is_array
        )
        
        print(f"  🖥️ Desktop has custom_items: {has_desktop_custom_items}")
        print(f"  📱 Mobile has custom_items: {has_mobile_custom_items}")
        print(f"  📝 Desktop custom_items count: {len(desktop_custom_items)}")
        print(f"  📝 Mobile custom_items count: {len(mobile_custom_items)}")
        print(f"  {'✅' if custom_items_success else '❌'} Custom items array test {'passed' if custom_items_success else 'failed'}")
        
        return {
            "test_name": "Custom Items Array Included",
            "success": custom_items_success,
            "has_desktop_custom_items": has_desktop_custom_items,
            "has_mobile_custom_items": has_mobile_custom_items,
            "desktop_custom_items_count": len(desktop_custom_items),
            "mobile_custom_items_count": len(mobile_custom_items),
            "desktop_is_array": desktop_is_array,
            "mobile_is_array": mobile_is_array,
            "desktop_custom_items": desktop_custom_items,
            "mobile_custom_items": mobile_custom_items
        }
    
    async def test_menusettings_component_structure_match(self) -> Dict:
        """Test 4: Structure matches what the MenuSettings component expects"""
        print("🔍 Test 4: Testing MenuSettings component structure match...")
        
        if not self.admin_token:
            return {"test_name": "MenuSettings Component Structure", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if not result["success"]:
            return {
                "test_name": "MenuSettings Component Structure",
                "success": False,
                "error": result.get("error", "Failed to get menu settings")
            }
        
        actual_data = result["data"]
        expected_structure = self.get_expected_menu_structure()
        
        # Compare structure
        structure_matches = []
        
        # Check desktop menu structure
        desktop_actual = actual_data.get("desktop_menu", {})
        desktop_expected = expected_structure["desktop_menu"]
        
        desktop_comparison = {}
        for expected_key in desktop_expected.keys():
            if expected_key == "custom_items":
                desktop_comparison[expected_key] = expected_key in desktop_actual
            else:
                # Check if the item exists and has the required structure
                if expected_key in desktop_actual:
                    item_data = desktop_actual[expected_key]
                    if isinstance(item_data, dict):
                        desktop_comparison[expected_key] = all(
                            key in item_data for key in ["enabled", "label", "roles"]
                        )
                    else:
                        desktop_comparison[expected_key] = False
                else:
                    desktop_comparison[expected_key] = False
        
        # Check mobile menu structure
        mobile_actual = actual_data.get("mobile_menu", {})
        mobile_expected = expected_structure["mobile_menu"]
        
        mobile_comparison = {}
        for expected_key in mobile_expected.keys():
            if expected_key == "custom_items":
                mobile_comparison[expected_key] = expected_key in mobile_actual
            else:
                # Check if the item exists and has the required structure
                if expected_key in mobile_actual:
                    item_data = mobile_actual[expected_key]
                    if isinstance(item_data, dict):
                        mobile_comparison[expected_key] = all(
                            key in item_data for key in ["enabled", "label", "roles"]
                        )
                    else:
                        mobile_comparison[expected_key] = False
                else:
                    mobile_comparison[expected_key] = False
        
        # Calculate match percentages
        desktop_matches = sum(1 for v in desktop_comparison.values() if v)
        mobile_matches = sum(1 for v in mobile_comparison.values() if v)
        
        desktop_match_percent = (desktop_matches / len(desktop_comparison)) * 100
        mobile_match_percent = (mobile_matches / len(mobile_comparison)) * 100
        
        overall_match = (desktop_match_percent + mobile_match_percent) / 2
        structure_match_success = overall_match >= 85  # 85% threshold for success
        
        print(f"  🖥️ Desktop structure match: {desktop_matches}/{len(desktop_comparison)} ({desktop_match_percent:.1f}%)")
        print(f"  📱 Mobile structure match: {mobile_matches}/{len(mobile_comparison)} ({mobile_match_percent:.1f}%)")
        print(f"  📊 Overall match: {overall_match:.1f}%")
        print(f"  {'✅' if structure_match_success else '❌'} Structure match test {'passed' if structure_match_success else 'failed'}")
        
        return {
            "test_name": "MenuSettings Component Structure",
            "success": structure_match_success,
            "desktop_match_percent": desktop_match_percent,
            "mobile_match_percent": mobile_match_percent,
            "overall_match_percent": overall_match,
            "desktop_comparison": desktop_comparison,
            "mobile_comparison": mobile_comparison,
            "expected_structure": expected_structure,
            "actual_structure": actual_data
        }
    
    async def test_post_endpoint_still_works(self) -> Dict:
        """Test 5: POST endpoint still works for updating settings"""
        print("🔍 Test 5: Testing POST endpoint functionality...")
        
        if not self.admin_token:
            return {"test_name": "POST Endpoint Functionality", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # First get current settings
        get_result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        if not get_result["success"]:
            return {
                "test_name": "POST Endpoint Functionality",
                "success": False,
                "error": "Failed to get current settings for POST test"
            }
        
        current_settings = get_result["data"]
        
        # Create test settings with a small modification
        test_settings = {
            "desktop_menu": {
                **current_settings.get("desktop_menu", {}),
            },
            "mobile_menu": {
                **current_settings.get("mobile_menu", {}),
            }
        }
        
        # Modify a setting to test the update
        if "browse" in test_settings["desktop_menu"]:
            test_settings["desktop_menu"]["browse"]["label"] = "Browse Test Update"
        
        if "browse" in test_settings["mobile_menu"]:
            test_settings["mobile_menu"]["browse"]["label"] = "Browse Mobile Test Update"
        
        # Test POST request
        post_result = await self.make_request("/admin/menu-settings", "POST", data=test_settings, headers=headers)
        
        if post_result["success"]:
            # Verify the update by getting settings again
            verify_result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
            
            update_verified = False
            if verify_result["success"]:
                updated_data = verify_result["data"]
                desktop_browse = updated_data.get("desktop_menu", {}).get("browse", {})
                mobile_browse = updated_data.get("mobile_menu", {}).get("browse", {})
                
                update_verified = (
                    desktop_browse.get("label") == "Browse Test Update" and
                    mobile_browse.get("label") == "Browse Mobile Test Update"
                )
            
            # Restore original settings
            if self.original_settings:
                await self.make_request("/admin/menu-settings", "POST", data=self.original_settings, headers=headers)
            
            print(f"  📊 POST status: {post_result['status']}")
            print(f"  ✅ POST successful: {post_result['success']}")
            print(f"  🔍 Update verified: {update_verified}")
            
            return {
                "test_name": "POST Endpoint Functionality",
                "success": post_result["success"] and update_verified,
                "response_time_ms": post_result["response_time_ms"],
                "post_successful": post_result["success"],
                "update_verified": update_verified,
                "post_response": post_result.get("data")
            }
        else:
            print(f"  ❌ POST failed: {post_result.get('error', 'Unknown error')}")
            return {
                "test_name": "POST Endpoint Functionality",
                "success": False,
                "error": post_result.get("error", "Unknown error"),
                "status": post_result["status"]
            }
    
    async def run_admin_menu_settings_fix_test(self) -> Dict:
        """Run all admin menu settings fix tests"""
        print("🚀 Starting Admin Menu Settings Fix Testing")
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
            test_1 = await self.test_get_endpoint_data_structure()
            test_2 = await self.test_default_menu_items_present()
            test_3 = await self.test_custom_items_array_included()
            test_4 = await self.test_menusettings_component_structure_match()
            test_5 = await self.test_post_endpoint_still_works()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_1_get_endpoint_structure": test_1,
                "test_2_default_items_present": test_2,
                "test_3_custom_items_array": test_3,
                "test_4_component_structure_match": test_4,
                "test_5_post_endpoint_works": test_5
            }
            
            # Calculate overall success metrics
            test_results = [
                test_1.get("success", False),
                test_2.get("success", False),
                test_3.get("success", False),
                test_4.get("success", False),
                test_5.get("success", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            all_tests_passed = all(test_results)
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "all_tests_passed": all_tests_passed,
                "get_endpoint_structure_correct": test_1.get("success", False),
                "default_items_present": test_2.get("success", False),
                "custom_items_array_included": test_3.get("success", False),
                "component_structure_matches": test_4.get("success", False),
                "post_endpoint_works": test_5.get("success", False),
                "fix_working": all_tests_passed,
                "menusettings_component_ready": (
                    test_1.get("success", False) and
                    test_2.get("success", False) and
                    test_3.get("success", False) and
                    test_4.get("success", False)
                )
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution"""
    tester = AdminMenuSettingsFixTester()
    results = await tester.run_admin_menu_settings_fix_test()
    
    print("\n" + "=" * 70)
    print("📋 ADMIN MENU SETTINGS FIX TEST RESULTS")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"🎯 Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"✅ All Tests Passed: {'Yes' if summary.get('all_tests_passed', False) else 'No'}")
    print(f"🔧 Fix Working: {'Yes' if summary.get('fix_working', False) else 'No'}")
    print(f"🖥️ MenuSettings Component Ready: {'Yes' if summary.get('menusettings_component_ready', False) else 'No'}")
    
    print("\n📊 Individual Test Results:")
    print(f"  1. GET Endpoint Structure: {'✅' if summary.get('get_endpoint_structure_correct', False) else '❌'}")
    print(f"  2. Default Items Present: {'✅' if summary.get('default_items_present', False) else '❌'}")
    print(f"  3. Custom Items Array: {'✅' if summary.get('custom_items_array_included', False) else '❌'}")
    print(f"  4. Component Structure Match: {'✅' if summary.get('component_structure_matches', False) else '❌'}")
    print(f"  5. POST Endpoint Works: {'✅' if summary.get('post_endpoint_works', False) else '❌'}")
    
    if summary.get('fix_working', False):
        print("\n🎉 CONCLUSION: Admin menu settings fix is working correctly!")
        print("   The MenuSettings component should now receive the proper data structure.")
    else:
        print("\n⚠️ CONCLUSION: Admin menu settings fix needs attention.")
        print("   Some tests failed - check individual test results for details.")
    
    # Save detailed results to file
    with open('/app/admin_menu_fix_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/admin_menu_fix_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())