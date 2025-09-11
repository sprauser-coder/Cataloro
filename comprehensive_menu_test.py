#!/usr/bin/env python3
"""
Comprehensive Menu Settings Test
Test the complete workflow including frontend integration points
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://menu-settings-debug.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"

class ComprehensiveMenuTester:
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
    
    async def make_request(self, endpoint: str, method: str = "GET", params=None, data=None, headers=None):
        """Make HTTP request"""
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
    
    async def authenticate_admin(self):
        """Authenticate as admin"""
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
    
    async def test_menu_property_consistency(self):
        """Test that menu items consistently use 'enabled' property"""
        print("\n🔍 Testing menu property consistency...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get admin menu settings
        admin_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not admin_result["success"]:
            return {"success": False, "error": "Failed to get admin menu settings"}
        
        admin_data = admin_result["data"]
        
        # Test with different user types
        test_users = [
            {"id": "68bfff790e4e46bc28d43631", "type": "regular_user"},
            {"id": "admin_user_1", "type": "admin_user"}
        ]
        
        consistency_results = []
        
        for user in test_users:
            user_result = await self.make_request(f"/menu-settings/user/{user['id']}")
            
            if user_result["success"]:
                user_data = user_result["data"]
                
                # Check property consistency
                admin_properties = set()
                user_properties = set()
                
                # Analyze admin menu properties
                for menu_type in ["desktop_menu", "mobile_menu"]:
                    menu = admin_data.get(menu_type, {})
                    for item_key, item_data in menu.items():
                        if isinstance(item_data, dict) and item_key != "custom_items":
                            admin_properties.update(item_data.keys())
                
                # Analyze user menu properties
                for menu_type in ["desktop_menu", "mobile_menu"]:
                    menu = user_data.get(menu_type, {})
                    for item_key, item_data in menu.items():
                        if isinstance(item_data, dict) and item_key != "custom_items":
                            user_properties.update(item_data.keys())
                
                consistency_results.append({
                    "user_type": user["type"],
                    "user_id": user["id"],
                    "admin_properties": list(admin_properties),
                    "user_properties": list(user_properties),
                    "properties_match": admin_properties == user_properties,
                    "uses_enabled": "enabled" in user_properties,
                    "uses_visible": "visible" in user_properties
                })
        
        print(f"  📊 Property consistency analysis:")
        for result in consistency_results:
            print(f"    {result['user_type']}:")
            print(f"      - Uses 'enabled': {result['uses_enabled']}")
            print(f"      - Uses 'visible': {result['uses_visible']}")
            print(f"      - Properties match admin: {result['properties_match']}")
        
        return {
            "success": True,
            "consistency_results": consistency_results,
            "all_consistent": all(r["properties_match"] for r in consistency_results)
        }
    
    async def test_disabled_item_filtering(self):
        """Test that disabled items are properly filtered from user responses"""
        print("\n🚫 Testing disabled item filtering...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get current settings and store original
        current_result = await self.make_request("/admin/menu-settings", headers=headers)
        if not current_result["success"]:
            return {"success": False, "error": "Failed to get current settings"}
        
        self.original_settings = current_result["data"]
        
        # Create test scenario: disable multiple items
        test_settings = json.loads(json.dumps(self.original_settings))  # Deep copy
        
        items_to_disable = ["browse", "create_listing", "messages"]
        disabled_items = []
        
        for item in items_to_disable:
            # Disable in desktop menu
            if item in test_settings.get("desktop_menu", {}):
                test_settings["desktop_menu"][item]["enabled"] = False
                disabled_items.append(f"desktop_{item}")
            
            # Disable in mobile menu
            if item in test_settings.get("mobile_menu", {}):
                test_settings["mobile_menu"][item]["enabled"] = False
                disabled_items.append(f"mobile_{item}")
        
        print(f"  🔧 Disabling items: {items_to_disable}")
        
        # Save the modified settings
        save_result = await self.make_request("/admin/menu-settings", "POST", data=test_settings, headers=headers)
        
        if not save_result["success"]:
            return {"success": False, "error": "Failed to save modified settings"}
        
        # Test with different users
        test_users = [
            {"id": "68bfff790e4e46bc28d43631", "type": "buyer", "role": "buyer"},
            {"id": "admin_user_1", "type": "admin", "role": "admin"}
        ]
        
        filtering_results = []
        
        for user in test_users:
            user_result = await self.make_request(f"/menu-settings/user/{user['id']}")
            
            if user_result["success"]:
                user_data = user_result["data"]
                
                # Check if disabled items appear in user response
                found_disabled_items = []
                
                for menu_type in ["desktop_menu", "mobile_menu"]:
                    menu = user_data.get(menu_type, {})
                    for item_key, item_data in menu.items():
                        if isinstance(item_data, dict) and item_key != "custom_items":
                            if item_data.get("enabled") == False:
                                found_disabled_items.append(f"{menu_type}_{item_key}")
                
                filtering_results.append({
                    "user_type": user["type"],
                    "user_role": user_data.get("user_role", "unknown"),
                    "disabled_items_found": found_disabled_items,
                    "filtering_working": len(found_disabled_items) == 0,
                    "total_desktop_items": len(user_data.get("desktop_menu", {})),
                    "total_mobile_items": len(user_data.get("mobile_menu", {}))
                })
        
        print(f"  📊 Filtering results:")
        for result in filtering_results:
            print(f"    {result['user_type']} ({result['user_role']}):")
            print(f"      - Filtering working: {result['filtering_working']}")
            print(f"      - Disabled items found: {len(result['disabled_items_found'])}")
            print(f"      - Desktop items: {result['total_desktop_items']}")
            print(f"      - Mobile items: {result['total_mobile_items']}")
            if result['disabled_items_found']:
                print(f"      - Found disabled items: {result['disabled_items_found']}")
        
        # Restore original settings
        await self.make_request("/admin/menu-settings", "POST", data=self.original_settings, headers=headers)
        print(f"  🔄 Restored original settings")
        
        return {
            "success": True,
            "items_disabled": items_to_disable,
            "filtering_results": filtering_results,
            "all_filtering_working": all(r["filtering_working"] for r in filtering_results)
        }
    
    async def test_role_based_visibility(self):
        """Test role-based menu item visibility"""
        print("\n👥 Testing role-based menu visibility...")
        
        # Test different user roles
        test_users = [
            {"id": "68bfff790e4e46bc28d43631", "expected_role": "buyer"},
            {"id": "admin_user_1", "expected_role": "admin"}
        ]
        
        role_results = []
        
        for user in test_users:
            user_result = await self.make_request(f"/menu-settings/user/{user['id']}")
            
            if user_result["success"]:
                user_data = user_result["data"]
                actual_role = user_data.get("user_role", "unknown")
                
                # Analyze menu items by role
                admin_items = []
                user_items = []
                
                for menu_type in ["desktop_menu", "mobile_menu"]:
                    menu = user_data.get(menu_type, {})
                    for item_key, item_data in menu.items():
                        if isinstance(item_data, dict) and item_key != "custom_items":
                            roles = item_data.get("roles", [])
                            if "admin" in roles:
                                admin_items.append(f"{menu_type}_{item_key}")
                            else:
                                user_items.append(f"{menu_type}_{item_key}")
                
                role_results.append({
                    "user_id": user["id"],
                    "expected_role": user["expected_role"],
                    "actual_role": actual_role,
                    "admin_items": admin_items,
                    "user_items": user_items,
                    "role_filtering_correct": (
                        (actual_role == "admin" and len(admin_items) > 0) or
                        (actual_role != "admin" and len(admin_items) == 0)
                    )
                })
        
        print(f"  📊 Role-based visibility results:")
        for result in role_results:
            print(f"    User {result['user_id']} ({result['actual_role']}):")
            print(f"      - Role filtering correct: {result['role_filtering_correct']}")
            print(f"      - Admin items: {len(result['admin_items'])}")
            print(f"      - User items: {len(result['user_items'])}")
        
        return {
            "success": True,
            "role_results": role_results,
            "all_role_filtering_correct": all(r["role_filtering_correct"] for r in role_results)
        }
    
    async def test_frontend_integration_points(self):
        """Test potential frontend integration issues"""
        print("\n🌐 Testing frontend integration points...")
        
        # Get user menu for analysis
        user_result = await self.make_request("/menu-settings/user/68bfff790e4e46bc28d43631")
        
        if not user_result["success"]:
            return {"success": False, "error": "Failed to get user menu"}
        
        user_data = user_result["data"]
        
        # Analyze structure for frontend consumption
        integration_analysis = {
            "has_desktop_menu": "desktop_menu" in user_data,
            "has_mobile_menu": "mobile_menu" in user_data,
            "has_user_role": "user_role" in user_data,
            "menu_items_have_enabled_property": True,
            "menu_items_have_label_property": True,
            "menu_items_have_roles_property": True,
            "custom_items_present": False,
            "structure_issues": []
        }
        
        # Check menu item structure
        for menu_type in ["desktop_menu", "mobile_menu"]:
            menu = user_data.get(menu_type, {})
            
            if "custom_items" in menu:
                integration_analysis["custom_items_present"] = True
            
            for item_key, item_data in menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    if "enabled" not in item_data:
                        integration_analysis["menu_items_have_enabled_property"] = False
                        integration_analysis["structure_issues"].append(f"{menu_type}.{item_key} missing 'enabled'")
                    
                    if "label" not in item_data:
                        integration_analysis["menu_items_have_label_property"] = False
                        integration_analysis["structure_issues"].append(f"{menu_type}.{item_key} missing 'label'")
                    
                    if "roles" not in item_data:
                        integration_analysis["menu_items_have_roles_property"] = False
                        integration_analysis["structure_issues"].append(f"{menu_type}.{item_key} missing 'roles'")
        
        # Check for potential isMenuItemVisible function issues
        frontend_compatibility = {
            "uses_enabled_property": integration_analysis["menu_items_have_enabled_property"],
            "consistent_structure": len(integration_analysis["structure_issues"]) == 0,
            "role_based_filtering_available": integration_analysis["has_user_role"],
            "menu_separation_clear": integration_analysis["has_desktop_menu"] and integration_analysis["has_mobile_menu"]
        }
        
        print(f"  📊 Frontend integration analysis:")
        print(f"    - Uses 'enabled' property: {frontend_compatibility['uses_enabled_property']}")
        print(f"    - Consistent structure: {frontend_compatibility['consistent_structure']}")
        print(f"    - Role-based filtering available: {frontend_compatibility['role_based_filtering_available']}")
        print(f"    - Menu separation clear: {frontend_compatibility['menu_separation_clear']}")
        
        if integration_analysis["structure_issues"]:
            print(f"    - Structure issues found: {integration_analysis['structure_issues']}")
        
        return {
            "success": True,
            "integration_analysis": integration_analysis,
            "frontend_compatibility": frontend_compatibility,
            "frontend_ready": all(frontend_compatibility.values())
        }
    
    async def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Menu Settings Testing")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate
            auth_success = await self.authenticate_admin()
            if not auth_success:
                return {"error": "Authentication failed"}
            
            # Run all tests
            property_test = await self.test_menu_property_consistency()
            filtering_test = await self.test_disabled_item_filtering()
            role_test = await self.test_role_based_visibility()
            frontend_test = await self.test_frontend_integration_points()
            
            # Compile results
            results = {
                "test_timestamp": datetime.now().isoformat(),
                "property_consistency": property_test,
                "disabled_item_filtering": filtering_test,
                "role_based_visibility": role_test,
                "frontend_integration": frontend_test
            }
            
            # Overall analysis
            all_tests_passed = all([
                property_test.get("success", False),
                filtering_test.get("success", False),
                role_test.get("success", False),
                frontend_test.get("success", False)
            ])
            
            backend_working_correctly = all([
                property_test.get("all_consistent", False),
                filtering_test.get("all_filtering_working", False),
                role_test.get("all_role_filtering_correct", False)
            ])
            
            results["summary"] = {
                "all_tests_passed": all_tests_passed,
                "backend_working_correctly": backend_working_correctly,
                "frontend_ready": frontend_test.get("frontend_ready", False),
                "issue_location": "frontend" if backend_working_correctly else "backend"
            }
            
            return results
            
        finally:
            await self.cleanup()

async def main():
    tester = ComprehensiveMenuTester()
    results = await tester.run_comprehensive_test()
    
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE MENU TEST RESULTS")
    print("=" * 80)
    
    if "error" in results:
        print(f"❌ Test failed: {results['error']}")
    else:
        summary = results.get("summary", {})
        print(f"✅ All tests passed: {summary.get('all_tests_passed', False)}")
        print(f"🔧 Backend working correctly: {summary.get('backend_working_correctly', False)}")
        print(f"🌐 Frontend ready: {summary.get('frontend_ready', False)}")
        print(f"🎯 Issue location: {summary.get('issue_location', 'unknown')}")
        
        if summary.get('backend_working_correctly', False):
            print("\n✅ CONCLUSION: Backend APIs are working correctly")
            print("   The issue is likely in the frontend isMenuItemVisible function")
            print("   or how the frontend processes the menu data.")
        else:
            print("\n❌ CONCLUSION: Backend has issues that need to be fixed")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Save results
    with open("/app/comprehensive_menu_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to /app/comprehensive_menu_test_results.json")