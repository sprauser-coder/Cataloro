#!/usr/bin/env python3
"""
Menu Settings API Testing - Comprehensive Data Structure Analysis
Testing the user menu settings API to understand exact data structure and logic
as requested in the review request.
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://marketplace-debug-3.preview.emergentagent.com/api"

# Test Users Configuration
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "demo@cataloro.com"

class MenuSettingsAPITester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_user_id = None
        self.admin_user_id = None
        self.original_menu_settings = None
        
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
        """Authenticate both admin and demo users"""
        print("🔐 Authenticating users...")
        
        # Authenticate admin
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            admin_user_data = admin_result["data"].get("user", {})
            self.admin_user_id = admin_user_data.get("id", "admin_user_1")
            print(f"  ✅ Admin authentication successful (ID: {self.admin_user_id})")
        else:
            print(f"  ❌ Admin authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
        
        # Authenticate demo user
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": "demo_password"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if demo_result["success"]:
            demo_user_data = demo_result["data"].get("user", {})
            self.demo_user_id = demo_user_data.get("id", "68bfff790e4e46bc28d43631")
            print(f"  ✅ Demo user authentication successful (ID: {self.demo_user_id})")
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error', 'Unknown error')}")
            return False
        
        return True
    
    async def test_user_menu_api_regular_user(self) -> Dict:
        """Test /api/menu-settings/user/{user_id} with regular user ID (demo user)"""
        print("👤 Testing user menu API with regular user (demo)...")
        
        if not self.demo_user_id:
            return {"test_name": "User Menu API - Regular User", "error": "No demo user ID available"}
        
        result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
        
        if result["success"]:
            data = result["data"]
            
            # Analyze data structure
            structure_analysis = {
                "has_desktop_menu": "desktop_menu" in data,
                "has_mobile_menu": "mobile_menu" in data,
                "has_user_role": "user_role" in data,
                "user_role": data.get("user_role", "unknown"),
                "desktop_items_count": len(data.get("desktop_menu", {})),
                "mobile_items_count": len(data.get("mobile_menu", {}))
            }
            
            # Analyze menu items structure
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            
            # Check for enabled/disabled states
            desktop_items_analysis = []
            for item_key, item_data in desktop_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    desktop_items_analysis.append({
                        "item": item_key,
                        "enabled": item_data.get("enabled"),
                        "label": item_data.get("label"),
                        "roles": item_data.get("roles", []),
                        "has_enabled_property": "enabled" in item_data,
                        "has_visible_property": "visible" in item_data
                    })
            
            mobile_items_analysis = []
            for item_key, item_data in mobile_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    mobile_items_analysis.append({
                        "item": item_key,
                        "enabled": item_data.get("enabled"),
                        "label": item_data.get("label"),
                        "roles": item_data.get("roles", []),
                        "has_enabled_property": "enabled" in item_data,
                        "has_visible_property": "visible" in item_data
                    })
            
            # Check for disabled items (should be filtered out)
            disabled_items_count = 0
            for item in desktop_items_analysis + mobile_items_analysis:
                if item["enabled"] == False:
                    disabled_items_count += 1
            
            print(f"  📊 User role: {structure_analysis['user_role']}")
            print(f"  🖥️ Desktop items: {structure_analysis['desktop_items_count']}")
            print(f"  📱 Mobile items: {structure_analysis['mobile_items_count']}")
            print(f"  ❌ Disabled items found: {disabled_items_count}")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.1f}ms")
            
            return {
                "test_name": "User Menu API - Regular User",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "user_id": self.demo_user_id,
                "structure_analysis": structure_analysis,
                "desktop_items_analysis": desktop_items_analysis,
                "mobile_items_analysis": mobile_items_analysis,
                "disabled_items_count": disabled_items_count,
                "full_response": data
            }
        else:
            print(f"  ❌ Regular user menu API failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "User Menu API - Regular User",
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"],
                "user_id": self.demo_user_id
            }
    
    async def test_user_menu_api_admin_user(self) -> Dict:
        """Test /api/menu-settings/user/{user_id} with admin user ID"""
        print("👑 Testing user menu API with admin user...")
        
        if not self.admin_user_id:
            return {"test_name": "User Menu API - Admin User", "error": "No admin user ID available"}
        
        result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
        
        if result["success"]:
            data = result["data"]
            
            # Analyze data structure
            structure_analysis = {
                "has_desktop_menu": "desktop_menu" in data,
                "has_mobile_menu": "mobile_menu" in data,
                "has_user_role": "user_role" in data,
                "user_role": data.get("user_role", "unknown"),
                "desktop_items_count": len(data.get("desktop_menu", {})),
                "mobile_items_count": len(data.get("mobile_menu", {}))
            }
            
            # Analyze menu items structure
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            
            # Check for admin-specific items
            admin_items_desktop = []
            admin_items_mobile = []
            
            for item_key, item_data in desktop_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    if "admin" in item_data.get("roles", []):
                        admin_items_desktop.append({
                            "item": item_key,
                            "enabled": item_data.get("enabled"),
                            "label": item_data.get("label"),
                            "roles": item_data.get("roles", [])
                        })
            
            for item_key, item_data in mobile_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    if "admin" in item_data.get("roles", []):
                        admin_items_mobile.append({
                            "item": item_key,
                            "enabled": item_data.get("enabled"),
                            "label": item_data.get("label"),
                            "roles": item_data.get("roles", [])
                        })
            
            # Check for disabled items (should be filtered out)
            disabled_items_count = 0
            all_items = []
            for item_key, item_data in desktop_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    all_items.append(item_data)
            for item_key, item_data in mobile_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    all_items.append(item_data)
            
            for item in all_items:
                if item.get("enabled") == False:
                    disabled_items_count += 1
            
            print(f"  📊 User role: {structure_analysis['user_role']}")
            print(f"  🖥️ Desktop items: {structure_analysis['desktop_items_count']}")
            print(f"  📱 Mobile items: {structure_analysis['mobile_items_count']}")
            print(f"  🔑 Admin items desktop: {len(admin_items_desktop)}")
            print(f"  🔑 Admin items mobile: {len(admin_items_mobile)}")
            print(f"  ❌ Disabled items found: {disabled_items_count}")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.1f}ms")
            
            return {
                "test_name": "User Menu API - Admin User",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "user_id": self.admin_user_id,
                "structure_analysis": structure_analysis,
                "admin_items_desktop": admin_items_desktop,
                "admin_items_mobile": admin_items_mobile,
                "disabled_items_count": disabled_items_count,
                "full_response": data
            }
        else:
            print(f"  ❌ Admin user menu API failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "User Menu API - Admin User",
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"],
                "user_id": self.admin_user_id
            }
    
    async def test_disable_menu_item_workflow(self) -> Dict:
        """Disable a menu item via admin API, then test user API to see if it's filtered out"""
        print("🔧 Testing disable menu item workflow...")
        
        if not self.admin_token:
            return {"test_name": "Disable Menu Item Workflow", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Step 1: Get current admin menu settings
        print("  Step 1: Getting current admin menu settings...")
        current_result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if not current_result["success"]:
            return {
                "test_name": "Disable Menu Item Workflow",
                "success": False,
                "error": "Failed to get current admin menu settings"
            }
        
        self.original_menu_settings = current_result["data"]
        current_settings = current_result["data"]
        
        # Step 2: Disable "browse" menu item
        print("  Step 2: Disabling 'browse' menu item...")
        modified_settings = {
            "desktop_menu": {**current_settings.get("desktop_menu", {})},
            "mobile_menu": {**current_settings.get("mobile_menu", {})}
        }
        
        # Disable browse in both desktop and mobile
        if "browse" in modified_settings["desktop_menu"]:
            modified_settings["desktop_menu"]["browse"]["enabled"] = False
        if "browse" in modified_settings["mobile_menu"]:
            modified_settings["mobile_menu"]["browse"]["enabled"] = False
        
        disable_result = await self.make_request("/admin/menu-settings", "POST", data=modified_settings, headers=headers)
        
        if not disable_result["success"]:
            return {
                "test_name": "Disable Menu Item Workflow",
                "success": False,
                "error": f"Failed to disable browse item: {disable_result.get('error')}"
            }
        
        # Step 3: Test user API to see if browse is filtered out
        print("  Step 3: Testing user API after disabling browse...")
        
        # Test with demo user
        demo_after_disable = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
        
        # Test with admin user
        admin_after_disable = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
        
        # Analyze results
        demo_has_browse = False
        admin_has_browse = False
        
        if demo_after_disable["success"]:
            demo_data = demo_after_disable["data"]
            demo_desktop = demo_data.get("desktop_menu", {})
            demo_mobile = demo_data.get("mobile_menu", {})
            
            # Check if browse exists and is enabled
            demo_has_browse = (
                ("browse" in demo_desktop and demo_desktop["browse"].get("enabled", False)) or
                ("browse" in demo_mobile and demo_mobile["browse"].get("enabled", False))
            )
        
        if admin_after_disable["success"]:
            admin_data = admin_after_disable["data"]
            admin_desktop = admin_data.get("desktop_menu", {})
            admin_mobile = admin_data.get("mobile_menu", {})
            
            # Check if browse exists and is enabled
            admin_has_browse = (
                ("browse" in admin_desktop and admin_desktop["browse"].get("enabled", False)) or
                ("browse" in admin_mobile and admin_mobile["browse"].get("enabled", False))
            )
        
        # Step 4: Restore original settings
        print("  Step 4: Restoring original settings...")
        if self.original_menu_settings:
            await self.make_request("/admin/menu-settings", "POST", data=self.original_menu_settings, headers=headers)
        
        filtering_working = not demo_has_browse and not admin_has_browse
        
        print(f"  📊 Browse disabled successfully: {disable_result['success']}")
        print(f"  👤 Demo user has browse after disable: {demo_has_browse}")
        print(f"  👑 Admin user has browse after disable: {admin_has_browse}")
        print(f"  ✅ Filtering working correctly: {filtering_working}")
        
        return {
            "test_name": "Disable Menu Item Workflow",
            "success": filtering_working,
            "disable_successful": disable_result["success"],
            "demo_has_browse_after_disable": demo_has_browse,
            "admin_has_browse_after_disable": admin_has_browse,
            "filtering_working": filtering_working,
            "demo_user_response": demo_after_disable.get("data") if demo_after_disable["success"] else None,
            "admin_user_response": admin_after_disable.get("data") if admin_after_disable["success"] else None
        }
    
    async def test_response_format_analysis(self) -> Dict:
        """Check the exact format of the response - specifically the enabled/disabled states"""
        print("📋 Testing response format analysis...")
        
        if not self.demo_user_id:
            return {"test_name": "Response Format Analysis", "error": "No demo user ID available"}
        
        result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
        
        if result["success"]:
            data = result["data"]
            
            # Analyze response format
            format_analysis = {
                "top_level_keys": list(data.keys()),
                "has_desktop_menu": "desktop_menu" in data,
                "has_mobile_menu": "mobile_menu" in data,
                "has_user_role": "user_role" in data
            }
            
            # Analyze menu item properties
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            
            # Sample item analysis
            sample_items = []
            
            # Get first few desktop items
            for item_key, item_data in list(desktop_menu.items())[:3]:
                if isinstance(item_data, dict) and item_key != "custom_items":
                    sample_items.append({
                        "menu_type": "desktop",
                        "item_key": item_key,
                        "properties": list(item_data.keys()),
                        "enabled_value": item_data.get("enabled"),
                        "enabled_type": type(item_data.get("enabled")).__name__,
                        "has_enabled": "enabled" in item_data,
                        "has_visible": "visible" in item_data,
                        "has_disabled": "disabled" in item_data,
                        "label": item_data.get("label"),
                        "roles": item_data.get("roles"),
                        "full_item": item_data
                    })
            
            # Get first few mobile items
            for item_key, item_data in list(mobile_menu.items())[:3]:
                if isinstance(item_data, dict) and item_key != "custom_items":
                    sample_items.append({
                        "menu_type": "mobile",
                        "item_key": item_key,
                        "properties": list(item_data.keys()),
                        "enabled_value": item_data.get("enabled"),
                        "enabled_type": type(item_data.get("enabled")).__name__,
                        "has_enabled": "enabled" in item_data,
                        "has_visible": "visible" in item_data,
                        "has_disabled": "disabled" in item_data,
                        "label": item_data.get("label"),
                        "roles": item_data.get("roles"),
                        "full_item": item_data
                    })
            
            # Property consistency analysis
            property_consistency = {
                "all_items_have_enabled": all(item["has_enabled"] for item in sample_items),
                "any_items_have_visible": any(item["has_visible"] for item in sample_items),
                "any_items_have_disabled": any(item["has_disabled"] for item in sample_items),
                "enabled_value_types": list(set(item["enabled_type"] for item in sample_items)),
                "common_properties": []
            }
            
            # Find common properties across all items
            if sample_items:
                common_props = set(sample_items[0]["properties"])
                for item in sample_items[1:]:
                    common_props = common_props.intersection(set(item["properties"]))
                property_consistency["common_properties"] = list(common_props)
            
            print(f"  📊 Top level keys: {format_analysis['top_level_keys']}")
            print(f"  🔧 All items have 'enabled': {property_consistency['all_items_have_enabled']}")
            print(f"  👁️ Any items have 'visible': {property_consistency['any_items_have_visible']}")
            print(f"  🚫 Any items have 'disabled': {property_consistency['any_items_have_disabled']}")
            print(f"  📝 Common properties: {property_consistency['common_properties']}")
            print(f"  🔢 Enabled value types: {property_consistency['enabled_value_types']}")
            
            return {
                "test_name": "Response Format Analysis",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "format_analysis": format_analysis,
                "sample_items": sample_items,
                "property_consistency": property_consistency,
                "full_response": data
            }
        else:
            print(f"  ❌ Response format analysis failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Response Format Analysis",
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"]
            }
    
    async def test_role_based_filtering(self) -> Dict:
        """Test role-based filtering - see if different user roles get different menu items"""
        print("🎭 Testing role-based filtering...")
        
        if not self.demo_user_id or not self.admin_user_id:
            return {"test_name": "Role-Based Filtering", "error": "Missing user IDs"}
        
        # Get menu for demo user (buyer role)
        demo_result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
        
        # Get menu for admin user (admin role)
        admin_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
        
        if demo_result["success"] and admin_result["success"]:
            demo_data = demo_result["data"]
            admin_data = admin_result["data"]
            
            # Analyze role differences
            demo_role = demo_data.get("user_role", "unknown")
            admin_role = admin_data.get("user_role", "unknown")
            
            # Count items for each user
            demo_desktop_count = len(demo_data.get("desktop_menu", {}))
            demo_mobile_count = len(demo_data.get("mobile_menu", {}))
            admin_desktop_count = len(admin_data.get("desktop_menu", {}))
            admin_mobile_count = len(admin_data.get("mobile_menu", {}))
            
            # Find items unique to each role
            demo_desktop_items = set(demo_data.get("desktop_menu", {}).keys())
            demo_mobile_items = set(demo_data.get("mobile_menu", {}).keys())
            admin_desktop_items = set(admin_data.get("desktop_menu", {}).keys())
            admin_mobile_items = set(admin_data.get("mobile_menu", {}).keys())
            
            # Items only admin has
            admin_only_desktop = admin_desktop_items - demo_desktop_items
            admin_only_mobile = admin_mobile_items - demo_mobile_items
            
            # Items only demo has
            demo_only_desktop = demo_desktop_items - admin_desktop_items
            demo_only_mobile = demo_mobile_items - admin_mobile_items
            
            # Common items
            common_desktop = demo_desktop_items.intersection(admin_desktop_items)
            common_mobile = demo_mobile_items.intersection(admin_mobile_items)
            
            # Check for admin-specific items
            admin_specific_items = []
            for item_key, item_data in admin_data.get("desktop_menu", {}).items():
                if isinstance(item_data, dict) and "admin" in item_data.get("roles", []):
                    admin_specific_items.append(f"desktop:{item_key}")
            
            for item_key, item_data in admin_data.get("mobile_menu", {}).items():
                if isinstance(item_data, dict) and "admin" in item_data.get("roles", []):
                    admin_specific_items.append(f"mobile:{item_key}")
            
            role_filtering_working = len(admin_only_desktop) > 0 or len(admin_only_mobile) > 0 or len(admin_specific_items) > 0
            
            print(f"  👤 Demo user role: {demo_role}")
            print(f"  👑 Admin user role: {admin_role}")
            print(f"  📊 Demo items (D/M): {demo_desktop_count}/{demo_mobile_count}")
            print(f"  📊 Admin items (D/M): {admin_desktop_count}/{admin_mobile_count}")
            print(f"  🔑 Admin-only desktop items: {list(admin_only_desktop)}")
            print(f"  🔑 Admin-only mobile items: {list(admin_only_mobile)}")
            print(f"  🎯 Admin-specific items: {admin_specific_items}")
            print(f"  ✅ Role filtering working: {role_filtering_working}")
            
            return {
                "test_name": "Role-Based Filtering",
                "success": role_filtering_working,
                "demo_role": demo_role,
                "admin_role": admin_role,
                "demo_desktop_count": demo_desktop_count,
                "demo_mobile_count": demo_mobile_count,
                "admin_desktop_count": admin_desktop_count,
                "admin_mobile_count": admin_mobile_count,
                "admin_only_desktop": list(admin_only_desktop),
                "admin_only_mobile": list(admin_only_mobile),
                "demo_only_desktop": list(demo_only_desktop),
                "demo_only_mobile": list(demo_only_mobile),
                "common_desktop": list(common_desktop),
                "common_mobile": list(common_mobile),
                "admin_specific_items": admin_specific_items,
                "role_filtering_working": role_filtering_working,
                "demo_response": demo_data,
                "admin_response": admin_data
            }
        else:
            error_msg = []
            if not demo_result["success"]:
                error_msg.append(f"Demo user failed: {demo_result.get('error')}")
            if not admin_result["success"]:
                error_msg.append(f"Admin user failed: {admin_result.get('error')}")
            
            print(f"  ❌ Role-based filtering test failed: {'; '.join(error_msg)}")
            return {
                "test_name": "Role-Based Filtering",
                "success": False,
                "error": "; ".join(error_msg),
                "demo_success": demo_result["success"],
                "admin_success": admin_result["success"]
            }
    
    async def run_comprehensive_menu_api_test(self) -> Dict:
        """Run all menu settings API tests as requested in the review"""
        print("🚀 Starting Menu Settings API Comprehensive Testing")
        print("=" * 70)
        print("FOCUS: Understanding exact data structure and logic for menu visibility")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Authenticate users first
            auth_success = await self.authenticate_users()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "User authentication failed - cannot proceed with tests"
                }
            
            # Run all test suites as requested in review
            print("\n1. Testing user menu API with regular user (demo)...")
            regular_user_test = await self.test_user_menu_api_regular_user()
            
            print("\n2. Testing user menu API with admin user...")
            admin_user_test = await self.test_user_menu_api_admin_user()
            
            print("\n3. Testing disable menu item workflow...")
            disable_workflow_test = await self.test_disable_menu_item_workflow()
            
            print("\n4. Testing response format analysis...")
            response_format_test = await self.test_response_format_analysis()
            
            print("\n5. Testing role-based filtering...")
            role_filtering_test = await self.test_role_based_filtering()
            
            # Compile comprehensive results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Menu Settings API Data Structure and Logic Analysis",
                "regular_user_test": regular_user_test,
                "admin_user_test": admin_user_test,
                "disable_workflow_test": disable_workflow_test,
                "response_format_test": response_format_test,
                "role_filtering_test": role_filtering_test
            }
            
            # Calculate overall success metrics
            test_results = [
                regular_user_test.get("success", False),
                admin_user_test.get("success", False),
                disable_workflow_test.get("success", False),
                response_format_test.get("success", False),
                role_filtering_test.get("success", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            # Key findings summary
            key_findings = {
                "api_endpoints_working": regular_user_test.get("success", False) and admin_user_test.get("success", False),
                "filtering_mechanism": "enabled property" if response_format_test.get("success") else "unknown",
                "disabled_items_filtered": disable_workflow_test.get("filtering_working", False),
                "role_based_filtering_working": role_filtering_test.get("role_filtering_working", False),
                "property_used_for_visibility": "enabled" if response_format_test.get("property_consistency", {}).get("all_items_have_enabled") else "unknown",
                "admin_gets_different_items": role_filtering_test.get("admin_specific_items", []) != [],
                "backend_filtering_correctly": disable_workflow_test.get("filtering_working", False)
            }
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "all_tests_passed": overall_success_rate == 100,
                "key_findings": key_findings,
                "critical_issues": [],
                "recommendations": []
            }
            
            # Add critical issues and recommendations based on findings
            if not key_findings["disabled_items_filtered"]:
                all_results["summary"]["critical_issues"].append("Disabled menu items are NOT being filtered out in user API")
            
            if not key_findings["role_based_filtering_working"]:
                all_results["summary"]["critical_issues"].append("Role-based filtering is NOT working correctly")
            
            if key_findings["property_used_for_visibility"] == "unknown":
                all_results["summary"]["critical_issues"].append("Cannot determine which property controls menu item visibility")
            
            if not key_findings["backend_filtering_correctly"]:
                all_results["summary"]["recommendations"].append("Fix backend API filtering logic for disabled menu items")
            
            if key_findings["property_used_for_visibility"] != "enabled":
                all_results["summary"]["recommendations"].append("Ensure frontend uses correct property for menu visibility")
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution"""
    tester = MenuSettingsAPITester()
    results = await tester.run_comprehensive_menu_api_test()
    
    print("\n" + "=" * 70)
    print("📋 MENU SETTINGS API TEST RESULTS SUMMARY")
    print("=" * 70)
    
    summary = results.get("summary", {})
    key_findings = summary.get("key_findings", {})
    
    print(f"Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"All Tests Passed: {'✅' if summary.get('all_tests_passed') else '❌'}")
    
    print("\n🔍 KEY FINDINGS:")
    for finding, value in key_findings.items():
        status = "✅" if value else "❌"
        print(f"  {status} {finding.replace('_', ' ').title()}: {value}")
    
    critical_issues = summary.get("critical_issues", [])
    if critical_issues:
        print("\n🚨 CRITICAL ISSUES:")
        for issue in critical_issues:
            print(f"  ❌ {issue}")
    
    recommendations = summary.get("recommendations", [])
    if recommendations:
        print("\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  🔧 {rec}")
    
    print("\n" + "=" * 70)
    
    # Save detailed results to file
    with open("/app/menu_api_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("📄 Detailed results saved to: /app/menu_api_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())