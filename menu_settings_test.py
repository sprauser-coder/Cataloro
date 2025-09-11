#!/usr/bin/env python3
"""
Menu Settings Visibility Functionality End-to-End Testing
Testing role mapping fixes and navigation integration for Menu Settings visibility workflow
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://market-guardian.preview.emergentagent.com/api"

# Test Users Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"
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
        print("🔐 Authenticating test users...")
        
        # Authenticate admin user
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            admin_user = admin_result["data"].get("user", {})
            self.admin_token = admin_result["data"].get("token", "")
            self.admin_user_id = admin_user.get("id")
            
            print(f"  ✅ Admin authenticated: {admin_user.get('email')} (ID: {self.admin_user_id})")
            print(f"     Role: {admin_user.get('role')} / User Role: {admin_user.get('user_role')}")
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
            demo_user = demo_result["data"].get("user", {})
            self.demo_token = demo_result["data"].get("token", "")
            self.demo_user_id = demo_user.get("id")
            
            print(f"  ✅ Demo user authenticated: {demo_user.get('email')} (ID: {self.demo_user_id})")
            print(f"     Role: {demo_user.get('role')} / User Role: {demo_user.get('user_role')}")
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error')}")
            return {"success": False, "error": "Demo user authentication failed"}
        
        return {
            "success": True,
            "admin_user": admin_user,
            "demo_user": demo_user,
            "admin_token": self.admin_token,
            "demo_token": self.demo_token
        }
    
    async def test_role_mapping_verification(self) -> Dict:
        """Test 1: Role Mapping Fix Verification"""
        print("🎭 Testing Role Mapping Fix Verification...")
        
        if not self.admin_token or not self.demo_token:
            return {"test_name": "Role Mapping Verification", "error": "Authentication required"}
        
        role_mapping_tests = []
        
        # Test admin user role mapping
        print("  Testing admin user role mapping...")
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        admin_menu_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}", headers=admin_headers)
        
        if admin_menu_result["success"]:
            admin_menu_data = admin_menu_result["data"]
            
            # Check if admin gets admin role
            admin_role_correct = False
            admin_items = []
            if isinstance(admin_menu_data, dict):
                # Look for admin-only items like admin_panel
                desktop_menu = admin_menu_data.get("desktop_menu", {})
                mobile_menu = admin_menu_data.get("mobile_menu", {})
                
                # Check desktop menu items
                for key, item in desktop_menu.items():
                    if key in ["admin_panel", "admin_drawer"]:
                        admin_items.append({"key": key, **item})
                
                # Check mobile menu items
                for key, item in mobile_menu.items():
                    if key in ["admin_panel", "admin_drawer"]:
                        admin_items.append({"key": key, **item})
                
                admin_role_correct = len(admin_items) > 0
            
            role_mapping_tests.append({
                "user": "admin",
                "user_id": self.admin_user_id,
                "email": ADMIN_EMAIL,
                "menu_settings_accessible": True,
                "response_time_ms": admin_menu_result["response_time_ms"],
                "admin_role_mapped_correctly": admin_role_correct,
                "admin_items_count": len(admin_items),
                "success": True
            })
            
            print(f"    ✅ Admin menu settings accessible ({admin_menu_result['response_time_ms']:.0f}ms)")
            print(f"    {'✅' if admin_role_correct else '❌'} Admin role mapping: {admin_role_correct}")
        else:
            role_mapping_tests.append({
                "user": "admin",
                "user_id": self.admin_user_id,
                "email": ADMIN_EMAIL,
                "menu_settings_accessible": False,
                "error": admin_menu_result.get("error"),
                "success": False
            })
            print(f"    ❌ Admin menu settings failed: {admin_menu_result.get('error')}")
        
        # Test demo user role mapping (should get buyer role from User-Buyer)
        print("  Testing demo user role mapping...")
        demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
        demo_menu_result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}", headers=demo_headers)
        
        if demo_menu_result["success"]:
            demo_menu_data = demo_menu_result["data"]
            
            # Check if demo user gets buyer role (should NOT see seller-only items)
            buyer_role_correct = False
            seller_items_hidden = True
            seller_only_items = []
            buyer_items = []
            
            if isinstance(demo_menu_data, dict):
                desktop_menu = demo_menu_data.get("desktop_menu", {})
                mobile_menu = demo_menu_data.get("mobile_menu", {})
                
                # Check for seller-only items (should NOT be present for buyer)
                for key, item in desktop_menu.items():
                    if key in ["create_listing", "my_listings", "listings"]:
                        seller_items_hidden = False
                        seller_only_items.append({"key": key, **item})
                    elif key in ["browse", "favorites", "profile"]:
                        buyer_items.append({"key": key, **item})
                
                for key, item in mobile_menu.items():
                    if key in ["create_listing", "my_listings", "listings"]:
                        seller_items_hidden = False
                        seller_only_items.append({"key": key, **item})
                    elif key in ["browse", "favorites", "profile"]:
                        buyer_items.append({"key": key, **item})
                
                buyer_role_correct = seller_items_hidden and len(buyer_items) > 0
            
            role_mapping_tests.append({
                "user": "demo",
                "user_id": self.demo_user_id,
                "email": DEMO_EMAIL,
                "menu_settings_accessible": True,
                "response_time_ms": demo_menu_result["response_time_ms"],
                "buyer_role_mapped_correctly": buyer_role_correct,
                "seller_items_properly_hidden": seller_items_hidden,
                "buyer_items_count": len(buyer_items),
                "seller_items_found": len(seller_only_items),
                "success": True
            })
            
            print(f"    ✅ Demo user menu settings accessible ({demo_menu_result['response_time_ms']:.0f}ms)")
            print(f"    {'✅' if buyer_role_correct else '❌'} Buyer role mapping: {buyer_role_correct}")
            print(f"    {'✅' if seller_items_hidden else '❌'} Seller items hidden: {seller_items_hidden}")
        else:
            role_mapping_tests.append({
                "user": "demo",
                "user_id": self.demo_user_id,
                "email": DEMO_EMAIL,
                "menu_settings_accessible": False,
                "error": demo_menu_result.get("error"),
                "success": False
            })
            print(f"    ❌ Demo user menu settings failed: {demo_menu_result.get('error')}")
        
        # Calculate overall success
        successful_tests = [t for t in role_mapping_tests if t["success"]]
        admin_role_working = any(t.get("admin_role_mapped_correctly") for t in role_mapping_tests if t["user"] == "admin")
        buyer_role_working = any(t.get("buyer_role_mapped_correctly") for t in role_mapping_tests if t["user"] == "demo")
        
        return {
            "test_name": "Role Mapping Fix Verification",
            "total_users_tested": len(role_mapping_tests),
            "successful_authentications": len(successful_tests),
            "admin_role_mapping_working": admin_role_working,
            "buyer_role_mapping_working": buyer_role_working,
            "user_buyer_to_buyer_mapping_working": buyer_role_working,
            "admin_to_admin_mapping_working": admin_role_working,
            "role_mapping_fix_successful": admin_role_working and buyer_role_working,
            "detailed_role_tests": role_mapping_tests
        }
    
    async def test_menu_visibility_workflow(self) -> Dict:
        """Test 2: Menu Visibility Workflow Test - Complete admin → user visibility workflow"""
        print("👁️ Testing Menu Visibility Workflow...")
        
        if not self.admin_token:
            return {"test_name": "Menu Visibility Workflow", "error": "Admin authentication required"}
        
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        workflow_steps = []
        
        # Step 1: Get current menu settings
        print("  Step 1: Getting current admin menu settings...")
        current_settings_result = await self.make_request("/admin/menu-settings", headers=admin_headers)
        
        if current_settings_result["success"]:
            current_settings = current_settings_result["data"]
            
            workflow_steps.append({
                "step": "Get Current Settings",
                "success": True,
                "response_time_ms": current_settings_result["response_time_ms"],
                "settings_retrieved": True
            })
            
            print(f"    ✅ Current settings retrieved ({current_settings_result['response_time_ms']:.0f}ms)")
        else:
            workflow_steps.append({
                "step": "Get Current Settings",
                "success": False,
                "error": current_settings_result.get("error")
            })
            print(f"    ❌ Failed to get current settings: {current_settings_result.get('error')}")
            return {"test_name": "Menu Visibility Workflow", "error": "Failed to get current settings"}
        
        # Step 2: Find and disable "Messages" menu item
        print("  Step 2: Disabling 'Messages' menu item...")
        
        # Find messages in mobile menu and disable it
        modified_settings = current_settings.copy()
        messages_found = False
        
        if "mobile_menu" in modified_settings:
            for item in modified_settings["mobile_menu"]:
                if item.get("key") == "messages":
                    item["enabled"] = False
                    messages_found = True
                    print(f"    📱 Found and disabled 'messages' in mobile menu")
                    break
        
        if not messages_found and "desktop_menu" in modified_settings:
            for item in modified_settings["desktop_menu"]:
                if item.get("key") == "messages":
                    item["enabled"] = False
                    messages_found = True
                    print(f"    🖥️ Found and disabled 'messages' in desktop menu")
                    break
        
        if not messages_found:
            print("    ⚠️ Messages menu item not found in current settings")
            return {"test_name": "Menu Visibility Workflow", "error": "Messages menu item not found"}
        
        # Step 3: Save modified settings
        print("  Step 3: Saving modified menu settings...")
        save_result = await self.make_request("/admin/menu-settings", "POST", data=modified_settings, headers=admin_headers)
        
        if save_result["success"]:
            workflow_steps.append({
                "step": "Save Modified Settings",
                "success": True,
                "response_time_ms": save_result["response_time_ms"],
                "messages_disabled": True
            })
            
            print(f"    ✅ Modified settings saved ({save_result['response_time_ms']:.0f}ms)")
        else:
            workflow_steps.append({
                "step": "Save Modified Settings",
                "success": False,
                "error": save_result.get("error")
            })
            print(f"    ❌ Failed to save settings: {save_result.get('error')}")
            return {"test_name": "Menu Visibility Workflow", "error": "Failed to save modified settings"}
        
        # Step 4: Verify change is saved in database by retrieving settings again
        print("  Step 4: Verifying changes saved in database...")
        verify_result = await self.make_request("/admin/menu-settings", headers=admin_headers)
        
        if verify_result["success"]:
            verified_settings = verify_result["data"]
            messages_disabled_confirmed = False
            
            # Check if messages is disabled in the retrieved settings
            for menu_type in ["mobile_menu", "desktop_menu"]:
                if menu_type in verified_settings:
                    for item in verified_settings[menu_type]:
                        if item.get("key") == "messages" and not item.get("enabled", True):
                            messages_disabled_confirmed = True
                            break
            
            workflow_steps.append({
                "step": "Verify Database Persistence",
                "success": True,
                "response_time_ms": verify_result["response_time_ms"],
                "messages_disabled_in_db": messages_disabled_confirmed
            })
            
            print(f"    {'✅' if messages_disabled_confirmed else '❌'} Database persistence verified: {messages_disabled_confirmed}")
        else:
            workflow_steps.append({
                "step": "Verify Database Persistence",
                "success": False,
                "error": verify_result.get("error")
            })
            print(f"    ❌ Failed to verify database persistence: {verify_result.get('error')}")
        
        # Step 5: Test user menu settings filtering (admin user)
        print("  Step 5: Testing admin user menu settings filtering...")
        admin_user_menu_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}", headers=admin_headers)
        
        admin_messages_filtered = False
        if admin_user_menu_result["success"]:
            admin_user_menu = admin_user_menu_result["data"]
            
            # Check if messages is filtered out for admin user
            messages_found_in_admin = False
            for menu_type in ["mobile_menu", "desktop_menu"]:
                if menu_type in admin_user_menu:
                    for item in admin_user_menu[menu_type]:
                        if item.get("key") == "messages":
                            messages_found_in_admin = True
                            break
            
            admin_messages_filtered = not messages_found_in_admin
            
            workflow_steps.append({
                "step": "Admin User Filtering",
                "success": True,
                "response_time_ms": admin_user_menu_result["response_time_ms"],
                "messages_filtered_for_admin": admin_messages_filtered
            })
            
            print(f"    {'✅' if admin_messages_filtered else '❌'} Messages filtered for admin: {admin_messages_filtered}")
        else:
            workflow_steps.append({
                "step": "Admin User Filtering",
                "success": False,
                "error": admin_user_menu_result.get("error")
            })
            print(f"    ❌ Failed to test admin user filtering: {admin_user_menu_result.get('error')}")
        
        # Step 6: Test user menu settings filtering (demo user)
        print("  Step 6: Testing demo user menu settings filtering...")
        demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
        demo_user_menu_result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}", headers=demo_headers)
        
        demo_messages_filtered = False
        if demo_user_menu_result["success"]:
            demo_user_menu = demo_user_menu_result["data"]
            
            # Check if messages is filtered out for demo user
            messages_found_in_demo = False
            for menu_type in ["mobile_menu", "desktop_menu"]:
                if menu_type in demo_user_menu:
                    for item in demo_user_menu[menu_type]:
                        if item.get("key") == "messages":
                            messages_found_in_demo = True
                            break
            
            demo_messages_filtered = not messages_found_in_demo
            
            workflow_steps.append({
                "step": "Demo User Filtering",
                "success": True,
                "response_time_ms": demo_user_menu_result["response_time_ms"],
                "messages_filtered_for_demo": demo_messages_filtered
            })
            
            print(f"    {'✅' if demo_messages_filtered else '❌'} Messages filtered for demo user: {demo_messages_filtered}")
        else:
            workflow_steps.append({
                "step": "Demo User Filtering",
                "success": False,
                "error": demo_user_menu_result.get("error")
            })
            print(f"    ❌ Failed to test demo user filtering: {demo_user_menu_result.get('error')}")
        
        # Calculate overall workflow success
        successful_steps = [s for s in workflow_steps if s["success"]]
        workflow_complete = len(successful_steps) == len(workflow_steps)
        
        # Check critical functionality
        database_persistence_working = any(s.get("messages_disabled_in_db") for s in workflow_steps)
        user_filtering_working = any(s.get("messages_filtered_for_admin") for s in workflow_steps) and any(s.get("messages_filtered_for_demo") for s in workflow_steps)
        
        return {
            "test_name": "Menu Visibility Workflow Test",
            "total_workflow_steps": len(workflow_steps),
            "successful_steps": len(successful_steps),
            "workflow_success_rate": len(successful_steps) / len(workflow_steps) * 100,
            "complete_workflow_working": workflow_complete,
            "database_persistence_working": database_persistence_working,
            "user_filtering_working": user_filtering_working,
            "admin_filtering_working": any(s.get("messages_filtered_for_admin") for s in workflow_steps),
            "demo_filtering_working": any(s.get("messages_filtered_for_demo") for s in workflow_steps),
            "messages_disabled_successfully": any(s.get("messages_disabled") for s in workflow_steps),
            "detailed_workflow_steps": workflow_steps
        }
    
    async def test_different_user_role_testing(self) -> Dict:
        """Test 3: Different User Role Testing - Test visibility with different user types"""
        print("👥 Testing Different User Role Visibility...")
        
        if not self.admin_token or not self.demo_token:
            return {"test_name": "Different User Role Testing", "error": "Authentication required"}
        
        role_visibility_tests = []
        
        # Test admin user visibility
        print("  Testing admin user role-based visibility...")
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        admin_menu_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}", headers=admin_headers)
        
        if admin_menu_result["success"]:
            admin_menu = admin_menu_result["data"]
            
            # Check admin-only items
            admin_only_items = []
            seller_items = []
            buyer_items = []
            
            for menu_type in ["mobile_menu", "desktop_menu"]:
                if menu_type in admin_menu:
                    for item in admin_menu[menu_type]:
                        item_key = item.get("key", "")
                        if item_key in ["admin_panel", "admin_drawer"]:
                            admin_only_items.append(item)
                        elif item_key in ["create_listing", "my_listings", "listings"]:
                            seller_items.append(item)
                        elif item_key in ["browse", "favorites", "profile"]:
                            buyer_items.append(item)
            
            admin_can_see_admin_items = len(admin_only_items) > 0
            admin_can_see_seller_items = len(seller_items) > 0  # Admin should see seller items too
            
            role_visibility_tests.append({
                "user_type": "admin",
                "user_id": self.admin_user_id,
                "response_time_ms": admin_menu_result["response_time_ms"],
                "can_see_admin_items": admin_can_see_admin_items,
                "can_see_seller_items": admin_can_see_seller_items,
                "admin_items_count": len(admin_only_items),
                "seller_items_count": len(seller_items),
                "buyer_items_count": len(buyer_items),
                "role_restrictions_working": admin_can_see_admin_items,
                "success": True
            })
            
            print(f"    ✅ Admin menu retrieved ({admin_menu_result['response_time_ms']:.0f}ms)")
            print(f"    {'✅' if admin_can_see_admin_items else '❌'} Admin can see admin-only items: {admin_can_see_admin_items} ({len(admin_only_items)} items)")
            print(f"    {'✅' if admin_can_see_seller_items else '❌'} Admin can see seller items: {admin_can_see_seller_items} ({len(seller_items)} items)")
        else:
            role_visibility_tests.append({
                "user_type": "admin",
                "user_id": self.admin_user_id,
                "error": admin_menu_result.get("error"),
                "success": False
            })
            print(f"    ❌ Admin menu retrieval failed: {admin_menu_result.get('error')}")
        
        # Test demo user (buyer) visibility
        print("  Testing demo user (buyer) role-based visibility...")
        demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
        demo_menu_result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}", headers=demo_headers)
        
        if demo_menu_result["success"]:
            demo_menu = demo_menu_result["data"]
            
            # Check what demo user can see
            admin_only_items = []
            seller_items = []
            buyer_items = []
            
            for menu_type in ["mobile_menu", "desktop_menu"]:
                if menu_type in demo_menu:
                    for item in demo_menu[menu_type]:
                        item_key = item.get("key", "")
                        if item_key in ["admin_panel", "admin_drawer"]:
                            admin_only_items.append(item)
                        elif item_key in ["create_listing", "my_listings", "listings"]:
                            seller_items.append(item)
                        elif item_key in ["browse", "favorites", "profile"]:
                            buyer_items.append(item)
            
            demo_cannot_see_admin_items = len(admin_only_items) == 0
            demo_cannot_see_seller_items = len(seller_items) == 0
            demo_can_see_buyer_items = len(buyer_items) > 0
            
            role_visibility_tests.append({
                "user_type": "buyer",
                "user_id": self.demo_user_id,
                "response_time_ms": demo_menu_result["response_time_ms"],
                "cannot_see_admin_items": demo_cannot_see_admin_items,
                "cannot_see_seller_items": demo_cannot_see_seller_items,
                "can_see_buyer_items": demo_can_see_buyer_items,
                "admin_items_count": len(admin_only_items),
                "seller_items_count": len(seller_items),
                "buyer_items_count": len(buyer_items),
                "role_restrictions_working": demo_cannot_see_admin_items and demo_cannot_see_seller_items and demo_can_see_buyer_items,
                "success": True
            })
            
            print(f"    ✅ Demo user menu retrieved ({demo_menu_result['response_time_ms']:.0f}ms)")
            print(f"    {'✅' if demo_cannot_see_admin_items else '❌'} Demo user cannot see admin items: {demo_cannot_see_admin_items} ({len(admin_only_items)} items)")
            print(f"    {'✅' if demo_cannot_see_seller_items else '❌'} Demo user cannot see seller items: {demo_cannot_see_seller_items} ({len(seller_items)} items)")
            print(f"    {'✅' if demo_can_see_buyer_items else '❌'} Demo user can see buyer items: {demo_can_see_buyer_items} ({len(buyer_items)} items)")
        else:
            role_visibility_tests.append({
                "user_type": "buyer",
                "user_id": self.demo_user_id,
                "error": demo_menu_result.get("error"),
                "success": False
            })
            print(f"    ❌ Demo user menu retrieval failed: {demo_menu_result.get('error')}")
        
        # Calculate overall success
        successful_tests = [t for t in role_visibility_tests if t["success"]]
        admin_role_restrictions_working = any(t.get("role_restrictions_working") for t in role_visibility_tests if t["user_type"] == "admin")
        buyer_role_restrictions_working = any(t.get("role_restrictions_working") for t in role_visibility_tests if t["user_type"] == "buyer")
        
        return {
            "test_name": "Different User Role Testing",
            "total_users_tested": len(role_visibility_tests),
            "successful_tests": len(successful_tests),
            "admin_role_restrictions_working": admin_role_restrictions_working,
            "buyer_role_restrictions_working": buyer_role_restrictions_working,
            "role_based_filtering_working": admin_role_restrictions_working and buyer_role_restrictions_working,
            "admin_can_see_admin_items": any(t.get("can_see_admin_items") for t in role_visibility_tests if t["user_type"] == "admin"),
            "buyer_cannot_see_seller_items": any(t.get("cannot_see_seller_items") for t in role_visibility_tests if t["user_type"] == "buyer"),
            "buyer_cannot_see_admin_items": any(t.get("cannot_see_admin_items") for t in role_visibility_tests if t["user_type"] == "buyer"),
            "detailed_role_visibility_tests": role_visibility_tests
        }
    
    async def test_complete_end_to_end_scenario(self) -> Dict:
        """Test 4: Complete End-to-End Scenario - Realistic admin scenario"""
        print("🎯 Testing Complete End-to-End Scenario...")
        
        if not self.admin_token or not self.demo_token:
            return {"test_name": "Complete End-to-End Scenario", "error": "Authentication required"}
        
        scenario_steps = []
        
        # Step 1: Admin logs in and gets current menu settings
        print("  Step 1: Admin retrieves current menu settings...")
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        current_settings_result = await self.make_request("/admin/menu-settings", headers=admin_headers)
        
        if current_settings_result["success"]:
            current_settings = current_settings_result["data"]
            
            scenario_steps.append({
                "step": "Admin Get Current Settings",
                "success": True,
                "response_time_ms": current_settings_result["response_time_ms"]
            })
            
            print(f"    ✅ Admin retrieved current settings ({current_settings_result['response_time_ms']:.0f}ms)")
        else:
            scenario_steps.append({
                "step": "Admin Get Current Settings",
                "success": False,
                "error": current_settings_result.get("error")
            })
            print(f"    ❌ Failed to get current settings: {current_settings_result.get('error')}")
            return {"test_name": "Complete End-to-End Scenario", "error": "Failed to get current settings"}
        
        # Step 2: Admin disables "Messages" for all users
        print("  Step 2: Admin disables 'Messages' for all users...")
        
        modified_settings = current_settings.copy()
        messages_disabled = False
        
        # Disable messages in both desktop and mobile menus
        for menu_type in ["desktop_menu", "mobile_menu"]:
            if menu_type in modified_settings:
                for item in modified_settings[menu_type]:
                    if item.get("key") == "messages":
                        item["enabled"] = False
                        messages_disabled = True
                        print(f"    📝 Disabled 'messages' in {menu_type}")
        
        if not messages_disabled:
            print("    ⚠️ Messages item not found to disable")
            return {"test_name": "Complete End-to-End Scenario", "error": "Messages item not found"}
        
        # Save the modified settings
        save_result = await self.make_request("/admin/menu-settings", "POST", data=modified_settings, headers=admin_headers)
        
        if save_result["success"]:
            scenario_steps.append({
                "step": "Admin Disable Messages",
                "success": True,
                "response_time_ms": save_result["response_time_ms"],
                "messages_disabled": True
            })
            
            print(f"    ✅ Messages disabled and saved ({save_result['response_time_ms']:.0f}ms)")
        else:
            scenario_steps.append({
                "step": "Admin Disable Messages",
                "success": False,
                "error": save_result.get("error")
            })
            print(f"    ❌ Failed to save disabled messages: {save_result.get('error')}")
            return {"test_name": "Complete End-to-End Scenario", "error": "Failed to save disabled messages"}
        
        # Step 3: Demo user (buyer) should not receive "Messages" in their menu settings
        print("  Step 3: Verifying demo user does not receive 'Messages'...")
        demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
        demo_menu_result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}", headers=demo_headers)
        
        demo_messages_hidden = False
        if demo_menu_result["success"]:
            demo_menu = demo_menu_result["data"]
            
            # Check if messages is NOT in demo user's menu
            messages_found = False
            for menu_type in ["desktop_menu", "mobile_menu"]:
                if menu_type in demo_menu:
                    for item in demo_menu[menu_type]:
                        if item.get("key") == "messages":
                            messages_found = True
                            break
            
            demo_messages_hidden = not messages_found
            
            scenario_steps.append({
                "step": "Demo User Messages Hidden",
                "success": True,
                "response_time_ms": demo_menu_result["response_time_ms"],
                "messages_hidden_from_demo": demo_messages_hidden
            })
            
            print(f"    {'✅' if demo_messages_hidden else '❌'} Messages hidden from demo user: {demo_messages_hidden}")
        else:
            scenario_steps.append({
                "step": "Demo User Messages Hidden",
                "success": False,
                "error": demo_menu_result.get("error")
            })
            print(f"    ❌ Failed to get demo user menu: {demo_menu_result.get('error')}")
        
        # Step 4: Admin user should still see "Messages" if it's enabled for admin role (check role-based vs disabled)
        print("  Step 4: Checking admin user Messages visibility...")
        admin_menu_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}", headers=admin_headers)
        
        admin_messages_behavior = "unknown"
        if admin_menu_result["success"]:
            admin_menu = admin_menu_result["data"]
            
            # Check if admin sees messages (should be hidden due to disabled setting)
            admin_messages_found = False
            for menu_type in ["desktop_menu", "mobile_menu"]:
                if menu_type in admin_menu:
                    for item in admin_menu[menu_type]:
                        if item.get("key") == "messages":
                            admin_messages_found = True
                            break
            
            # Admin should also NOT see messages when it's disabled globally
            admin_messages_behavior = "hidden" if not admin_messages_found else "visible"
            admin_behavior_correct = not admin_messages_found  # Should be hidden for admin too
            
            scenario_steps.append({
                "step": "Admin User Messages Behavior",
                "success": True,
                "response_time_ms": admin_menu_result["response_time_ms"],
                "admin_messages_behavior": admin_messages_behavior,
                "admin_behavior_correct": admin_behavior_correct
            })
            
            print(f"    {'✅' if admin_behavior_correct else '❌'} Admin messages behavior: {admin_messages_behavior} (correct: {admin_behavior_correct})")
        else:
            scenario_steps.append({
                "step": "Admin User Messages Behavior",
                "success": False,
                "error": admin_menu_result.get("error")
            })
            print(f"    ❌ Failed to get admin user menu: {admin_menu_result.get('error')}")
        
        # Step 5: Test scenario where items are disabled vs role-restricted
        print("  Step 5: Testing disabled vs role-restricted scenarios...")
        
        # Check if admin can see admin-only items (should still work)
        admin_only_items_count = 0
        if admin_menu_result["success"]:
            admin_menu = admin_menu_result["data"]
            
            for menu_type in ["desktop_menu", "mobile_menu"]:
                if menu_type in admin_menu:
                    for item in admin_menu[menu_type]:
                        if item.get("key") in ["admin_panel", "admin_drawer"]:
                            admin_only_items_count += 1
        
        role_restrictions_still_working = admin_only_items_count > 0
        
        scenario_steps.append({
            "step": "Disabled vs Role-Restricted Test",
            "success": True,
            "role_restrictions_still_working": role_restrictions_still_working,
            "admin_only_items_count": admin_only_items_count,
            "disabled_items_filtered": demo_messages_hidden,
            "role_and_disabled_both_working": role_restrictions_still_working and demo_messages_hidden
        })
        
        print(f"    {'✅' if role_restrictions_still_working else '❌'} Role restrictions still working: {role_restrictions_still_working}")
        print(f"    {'✅' if demo_messages_hidden else '❌'} Disabled items filtered: {demo_messages_hidden}")
        
        # Calculate overall scenario success
        successful_steps = [s for s in scenario_steps if s["success"]]
        scenario_complete = len(successful_steps) == len(scenario_steps)
        
        # Check critical end-to-end functionality
        admin_can_disable = any(s.get("messages_disabled") for s in scenario_steps)
        demo_user_filtered = any(s.get("messages_hidden_from_demo") for s in scenario_steps)
        admin_behavior_correct = any(s.get("admin_behavior_correct") for s in scenario_steps)
        role_and_disabled_working = any(s.get("role_and_disabled_both_working") for s in scenario_steps)
        
        return {
            "test_name": "Complete End-to-End Scenario",
            "total_scenario_steps": len(scenario_steps),
            "successful_steps": len(successful_steps),
            "scenario_success_rate": len(successful_steps) / len(scenario_steps) * 100,
            "complete_scenario_working": scenario_complete,
            "admin_can_disable_items": admin_can_disable,
            "demo_user_properly_filtered": demo_user_filtered,
            "admin_behavior_correct": admin_behavior_correct,
            "role_restrictions_and_disabled_both_working": role_and_disabled_working,
            "end_to_end_workflow_functional": admin_can_disable and demo_user_filtered and role_and_disabled_working,
            "detailed_scenario_steps": scenario_steps
        }
    
    async def run_comprehensive_menu_settings_test(self) -> Dict:
        """Run all Menu Settings visibility tests"""
        print("🚀 Starting Menu Settings Visibility Functionality End-to-End Testing")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate users first
            auth_result = await self.authenticate_users()
            if not auth_result["success"]:
                return {"error": "Authentication failed", "details": auth_result}
            
            # Run all test suites
            role_mapping_test = await self.test_role_mapping_verification()
            menu_visibility_test = await self.test_menu_visibility_workflow()
            user_role_test = await self.test_different_user_role_testing()
            end_to_end_test = await self.test_complete_end_to_end_scenario()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "authentication": auth_result,
                "role_mapping_verification": role_mapping_test,
                "menu_visibility_workflow": menu_visibility_test,
                "different_user_role_testing": user_role_test,
                "complete_end_to_end_scenario": end_to_end_test
            }
            
            # Calculate overall success metrics
            test_results = [
                role_mapping_test.get("role_mapping_fix_successful", False),
                menu_visibility_test.get("complete_workflow_working", False),
                user_role_test.get("role_based_filtering_working", False),
                end_to_end_test.get("end_to_end_workflow_functional", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "role_mapping_fix_working": role_mapping_test.get("role_mapping_fix_successful", False),
                "menu_visibility_workflow_working": menu_visibility_test.get("complete_workflow_working", False),
                "role_based_filtering_working": user_role_test.get("role_based_filtering_working", False),
                "end_to_end_scenario_working": end_to_end_test.get("end_to_end_workflow_functional", False),
                "admin_role_mapping_correct": role_mapping_test.get("admin_role_mapping_working", False),
                "buyer_role_mapping_correct": role_mapping_test.get("buyer_role_mapping_working", False),
                "database_persistence_working": menu_visibility_test.get("database_persistence_working", False),
                "user_filtering_working": menu_visibility_test.get("user_filtering_working", False),
                "admin_can_see_admin_items": user_role_test.get("admin_can_see_admin_items", False),
                "buyer_cannot_see_seller_items": user_role_test.get("buyer_cannot_see_seller_items", False),
                "all_tests_passed": overall_success_rate == 100
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution function"""
    tester = MenuSettingsVisibilityTester()
    results = await tester.run_comprehensive_menu_settings_test()
    
    print("\n" + "=" * 80)
    print("📊 MENU SETTINGS VISIBILITY TEST RESULTS SUMMARY")
    print("=" * 80)
    
    summary = results.get("summary", {})
    
    print(f"🎯 Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"🔐 Role Mapping Fix: {'✅ WORKING' if summary.get('role_mapping_fix_working') else '❌ FAILED'}")
    print(f"👁️ Menu Visibility Workflow: {'✅ WORKING' if summary.get('menu_visibility_workflow_working') else '❌ FAILED'}")
    print(f"👥 Role-Based Filtering: {'✅ WORKING' if summary.get('role_based_filtering_working') else '❌ FAILED'}")
    print(f"🎯 End-to-End Scenario: {'✅ WORKING' if summary.get('end_to_end_scenario_working') else '❌ FAILED'}")
    
    print("\n📋 Detailed Results:")
    print(f"   Admin Role Mapping: {'✅' if summary.get('admin_role_mapping_correct') else '❌'}")
    print(f"   Buyer Role Mapping: {'✅' if summary.get('buyer_role_mapping_correct') else '❌'}")
    print(f"   Database Persistence: {'✅' if summary.get('database_persistence_working') else '❌'}")
    print(f"   User Filtering: {'✅' if summary.get('user_filtering_working') else '❌'}")
    print(f"   Admin Can See Admin Items: {'✅' if summary.get('admin_can_see_admin_items') else '❌'}")
    print(f"   Buyer Cannot See Seller Items: {'✅' if summary.get('buyer_cannot_see_seller_items') else '❌'}")
    
    if summary.get('all_tests_passed'):
        print("\n🎉 ALL MENU SETTINGS VISIBILITY TESTS PASSED!")
        print("✅ Role mapping fixes are working correctly")
        print("✅ Navigation integration is functional")
        print("✅ Complete visibility workflow is operational")
    else:
        print("\n⚠️ SOME TESTS FAILED - Review detailed results above")
    
    print("=" * 80)
    
    # Save detailed results to file
    with open('/app/menu_settings_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("📄 Detailed results saved to: /app/menu_settings_test_results.json")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())