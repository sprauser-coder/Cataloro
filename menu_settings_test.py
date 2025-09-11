#!/usr/bin/env python3
"""
Menu Settings API Testing
Comprehensive testing of Menu Settings API functionality end-to-end
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-repair.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"
ADMIN_ROLE = "admin"
ADMIN_ID = "admin_user_1"

class MenuSettingsTester:
    def __init__(self):
        self.session = None
        self.test_results = []
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
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin user...")
        
        login_data = {
            "email": "admin@cataloro.com",
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            print(f"  ✅ Admin authentication successful")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error')}")
            return False
    
    async def test_get_default_menu_settings(self) -> Dict:
        """Test GET /api/admin/menu-settings - should return default menu configuration"""
        print("📋 Testing GET /api/admin/menu-settings (default configuration)...")
        
        result = await self.make_request("/admin/menu-settings")
        
        if result["success"]:
            menu_data = result["data"]
            
            # Validate structure
            has_desktop_menu = "desktop_menu" in menu_data
            has_mobile_menu = "mobile_menu" in menu_data
            
            # Check default desktop menu items
            desktop_menu = menu_data.get("desktop_menu", {})
            expected_desktop_items = ["about", "browse", "create_listing", "messages", "tenders", "profile", "admin_panel", "buy_management", "my_listings", "favorites"]
            desktop_items_present = all(item in desktop_menu for item in expected_desktop_items)
            
            # Check default mobile menu items
            mobile_menu = menu_data.get("mobile_menu", {})
            expected_mobile_items = ["browse", "messages", "create", "tenders", "listings", "profile", "admin_drawer"]
            mobile_items_present = all(item in mobile_menu for item in expected_mobile_items)
            
            # Check role configurations
            desktop_roles_valid = True
            mobile_roles_valid = True
            
            for item_key, item_config in desktop_menu.items():
                if not isinstance(item_config.get("roles", []), list):
                    desktop_roles_valid = False
                    break
                if not isinstance(item_config.get("enabled", True), bool):
                    desktop_roles_valid = False
                    break
            
            for item_key, item_config in mobile_menu.items():
                if not isinstance(item_config.get("roles", []), list):
                    mobile_roles_valid = False
                    break
                if not isinstance(item_config.get("enabled", True), bool):
                    mobile_roles_valid = False
                    break
            
            print(f"  ✅ Default menu settings retrieved successfully")
            print(f"  📱 Desktop menu items: {len(desktop_menu)} (expected: {len(expected_desktop_items)})")
            print(f"  📱 Mobile menu items: {len(mobile_menu)} (expected: {len(expected_mobile_items)})")
            
            return {
                "test_name": "Get Default Menu Settings",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "has_desktop_menu": has_desktop_menu,
                "has_mobile_menu": has_mobile_menu,
                "desktop_items_count": len(desktop_menu),
                "mobile_items_count": len(mobile_menu),
                "desktop_items_present": desktop_items_present,
                "mobile_items_present": mobile_items_present,
                "desktop_roles_valid": desktop_roles_valid,
                "mobile_roles_valid": mobile_roles_valid,
                "structure_valid": has_desktop_menu and has_mobile_menu and desktop_roles_valid and mobile_roles_valid,
                "menu_data": menu_data
            }
        else:
            print(f"  ❌ Failed to get default menu settings: {result.get('error')}")
            return {
                "test_name": "Get Default Menu Settings",
                "success": False,
                "error": result.get("error"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"]
            }
    
    async def test_update_menu_settings(self) -> Dict:
        """Test POST /api/admin/menu-settings - test updating menu settings"""
        print("✏️ Testing POST /api/admin/menu-settings (update configuration)...")
        
        # Test data with some items disabled and role changes
        # Note: Using both legacy roles (admin, user) and new roles (buyer, seller) for compatibility
        test_settings = {
            "desktop_menu": {
                "about": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer", "user"]},
                "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer", "user"]},
                "create_listing": {"enabled": False, "roles": ["admin", "manager", "seller"]},  # Disabled for testing
                "messages": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer", "user"]},
                "tenders": {"enabled": True, "roles": ["admin", "manager"]},  # Limited to admin/manager only
                "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer", "user"]},
                "admin_panel": {"enabled": True, "roles": ["admin"]},  # Admin only
                "buy_management": {"enabled": True, "roles": ["admin", "manager", "buyer", "user"]},
                "my_listings": {"enabled": True, "roles": ["admin", "manager", "seller"]},
                "favorites": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer", "user"]}  # Disabled for testing
            },
            "mobile_menu": {
                "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer", "user"]},
                "messages": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer", "user"]},
                "create": {"enabled": False, "roles": ["admin", "manager", "seller"]},  # Disabled for testing
                "tenders": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer", "user"]},
                "listings": {"enabled": True, "roles": ["admin", "manager", "seller"]},
                "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer", "user"]},
                "admin_drawer": {"enabled": True, "roles": ["admin"]}  # Admin only
            }
        }
        
        result = await self.make_request("/admin/menu-settings", "POST", data=test_settings)
        
        if result["success"]:
            response_data = result["data"]
            
            # Validate response structure
            has_message = "message" in response_data
            has_settings = "settings" in response_data
            
            settings_data = response_data.get("settings", {})
            desktop_updated = "desktop_menu" in settings_data
            mobile_updated = "mobile_menu" in settings_data
            
            # Verify specific changes were applied
            desktop_menu = settings_data.get("desktop_menu", {})
            mobile_menu = settings_data.get("mobile_menu", {})
            
            create_listing_disabled = not desktop_menu.get("create_listing", {}).get("enabled", True)
            favorites_disabled = not desktop_menu.get("favorites", {}).get("enabled", True)
            mobile_create_disabled = not mobile_menu.get("create", {}).get("enabled", True)
            
            tenders_admin_only = set(desktop_menu.get("tenders", {}).get("roles", [])) == {"admin", "manager"}
            admin_panel_admin_only = set(desktop_menu.get("admin_panel", {}).get("roles", [])) == {"admin"}
            
            print(f"  ✅ Menu settings updated successfully")
            print(f"  🔧 Create listing disabled: {create_listing_disabled}")
            print(f"  🔧 Favorites disabled: {favorites_disabled}")
            print(f"  🔧 Tenders admin/manager only: {tenders_admin_only}")
            
            return {
                "test_name": "Update Menu Settings",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "has_message": has_message,
                "has_settings": has_settings,
                "desktop_updated": desktop_updated,
                "mobile_updated": mobile_updated,
                "create_listing_disabled": create_listing_disabled,
                "favorites_disabled": favorites_disabled,
                "mobile_create_disabled": mobile_create_disabled,
                "tenders_admin_only": tenders_admin_only,
                "admin_panel_admin_only": admin_panel_admin_only,
                "update_successful": has_message and has_settings and desktop_updated and mobile_updated,
                "test_settings": test_settings,
                "response_data": response_data
            }
        else:
            print(f"  ❌ Failed to update menu settings: {result.get('error')}")
            return {
                "test_name": "Update Menu Settings",
                "success": False,
                "error": result.get("error"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"]
            }
    
    async def test_user_specific_menu_filtering(self) -> Dict:
        """Test GET /api/menu-settings/user/{user_id} - test user-specific menu filtering"""
        print("👤 Testing GET /api/menu-settings/user/{user_id} (user-specific filtering)...")
        
        # Test with admin user
        admin_user_id = "admin_user_1"
        admin_result = await self.make_request(f"/menu-settings/user/{admin_user_id}")
        
        # Test with demo user (buyer role)
        demo_user_id = "68bfff790e4e46bc28d43631"
        demo_result = await self.make_request(f"/menu-settings/user/{demo_user_id}")
        
        test_results = {
            "admin_test": {},
            "demo_test": {}
        }
        
        # Process admin user results
        if admin_result["success"]:
            admin_data = admin_result["data"]
            admin_role = admin_data.get("user_role", "unknown")
            admin_desktop = admin_data.get("desktop_menu", {})
            admin_mobile = admin_data.get("mobile_menu", {})
            
            # Admin should see admin_panel and tenders (based on our test settings)
            admin_has_admin_panel = "admin_panel" in admin_desktop
            admin_has_tenders = "tenders" in admin_desktop
            admin_missing_disabled = "create_listing" not in admin_desktop and "favorites" not in admin_desktop
            
            test_results["admin_test"] = {
                "success": True,
                "response_time_ms": admin_result["response_time_ms"],
                "user_role": admin_role,
                "desktop_items_count": len(admin_desktop),
                "mobile_items_count": len(admin_mobile),
                "has_admin_panel": admin_has_admin_panel,
                "has_tenders": admin_has_tenders,
                "missing_disabled_items": admin_missing_disabled,
                "role_filtering_correct": admin_has_admin_panel and admin_has_tenders
            }
            
            print(f"  ✅ Admin user menu retrieved (role: {admin_role})")
            print(f"  📋 Desktop items: {len(admin_desktop)}, Mobile items: {len(admin_mobile)}")
            print(f"  🔑 Has admin panel: {admin_has_admin_panel}, Has tenders: {admin_has_tenders}")
        else:
            test_results["admin_test"] = {
                "success": False,
                "error": admin_result.get("error"),
                "response_time_ms": admin_result["response_time_ms"]
            }
            print(f"  ❌ Failed to get admin user menu: {admin_result.get('error')}")
        
        # Process demo user results
        if demo_result["success"]:
            demo_data = demo_result["data"]
            demo_role = demo_data.get("user_role", "unknown")
            demo_desktop = demo_data.get("desktop_menu", {})
            demo_mobile = demo_data.get("mobile_menu", {})
            
            # Demo user (buyer) should NOT see admin_panel, should see limited tenders based on our test settings
            demo_missing_admin_panel = "admin_panel" not in demo_desktop
            demo_missing_tenders = "tenders" not in demo_desktop  # We limited tenders to admin/manager only
            demo_missing_disabled = "create_listing" not in demo_desktop and "favorites" not in demo_desktop
            
            test_results["demo_test"] = {
                "success": True,
                "response_time_ms": demo_result["response_time_ms"],
                "user_role": demo_role,
                "desktop_items_count": len(demo_desktop),
                "mobile_items_count": len(demo_mobile),
                "missing_admin_panel": demo_missing_admin_panel,
                "missing_tenders": demo_missing_tenders,
                "missing_disabled_items": demo_missing_disabled,
                "role_filtering_correct": demo_missing_admin_panel and demo_missing_tenders
            }
            
            print(f"  ✅ Demo user menu retrieved (role: {demo_role})")
            print(f"  📋 Desktop items: {len(demo_desktop)}, Mobile items: {len(demo_mobile)}")
            print(f"  🚫 Missing admin panel: {demo_missing_admin_panel}, Missing tenders: {demo_missing_tenders}")
        else:
            test_results["demo_test"] = {
                "success": False,
                "error": demo_result.get("error"),
                "response_time_ms": demo_result["response_time_ms"]
            }
            print(f"  ❌ Failed to get demo user menu: {demo_result.get('error')}")
        
        # Calculate overall success
        admin_success = test_results["admin_test"].get("success", False)
        demo_success = test_results["demo_test"].get("success", False)
        admin_filtering = test_results["admin_test"].get("role_filtering_correct", False)
        demo_filtering = test_results["demo_test"].get("role_filtering_correct", False)
        
        return {
            "test_name": "User Specific Menu Filtering",
            "admin_test_success": admin_success,
            "demo_test_success": demo_success,
            "admin_role_filtering_correct": admin_filtering,
            "demo_role_filtering_correct": demo_filtering,
            "both_users_tested": admin_success and demo_success,
            "role_based_filtering_working": admin_filtering and demo_filtering,
            "detailed_results": test_results
        }
    
    async def test_menu_configuration_logic(self) -> Dict:
        """Test menu configuration logic - toggling items and role assignments"""
        print("⚙️ Testing menu configuration logic (toggle items and roles)...")
        
        # Test 1: Toggle specific items on/off
        toggle_test_settings = {
            "desktop_menu": {
                "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
                "messages": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"]},  # Disabled
                "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
                "admin_panel": {"enabled": True, "roles": ["admin", "manager"]}
            },
            "mobile_menu": {
                "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
                "messages": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"]},  # Disabled
                "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]}
            }
        }
        
        # Update settings
        update_result = await self.make_request("/admin/menu-settings", "POST", data=toggle_test_settings)
        
        if not update_result["success"]:
            return {
                "test_name": "Menu Configuration Logic",
                "success": False,
                "error": f"Failed to update settings: {update_result.get('error')}",
                "response_time_ms": update_result["response_time_ms"]
            }
        
        # Test with different user roles
        test_users = [
            {"id": "admin_user_1", "expected_role": "admin"},
            {"id": "68bfff790e4e46bc28d43631", "expected_role": "user"}  # Demo user
        ]
        
        role_tests = []
        
        for user in test_users:
            user_result = await self.make_request(f"/menu-settings/user/{user['id']}")
            
            if user_result["success"]:
                user_data = user_result["data"]
                desktop_menu = user_data.get("desktop_menu", {})
                mobile_menu = user_data.get("mobile_menu", {})
                
                # Check that messages is disabled (should not appear)
                messages_hidden_desktop = "messages" not in desktop_menu
                messages_hidden_mobile = "messages" not in mobile_menu
                
                # Check that enabled items appear
                browse_visible_desktop = "browse" in desktop_menu
                profile_visible_desktop = "profile" in desktop_menu
                
                # Check role-based filtering
                admin_panel_visibility = "admin_panel" in desktop_menu
                admin_panel_correct = (admin_panel_visibility and user["expected_role"] == "admin") or (not admin_panel_visibility and user["expected_role"] != "admin")
                
                role_tests.append({
                    "user_id": user["id"],
                    "expected_role": user["expected_role"],
                    "actual_role": user_data.get("user_role", "unknown"),
                    "messages_hidden_desktop": messages_hidden_desktop,
                    "messages_hidden_mobile": messages_hidden_mobile,
                    "browse_visible": browse_visible_desktop,
                    "profile_visible": profile_visible_desktop,
                    "admin_panel_visibility_correct": admin_panel_correct,
                    "toggle_logic_working": messages_hidden_desktop and messages_hidden_mobile and browse_visible_desktop,
                    "role_logic_working": admin_panel_correct
                })
                
                print(f"  👤 User {user['id']}: Messages hidden: {messages_hidden_desktop}, Admin panel correct: {admin_panel_correct}")
            else:
                role_tests.append({
                    "user_id": user["id"],
                    "success": False,
                    "error": user_result.get("error")
                })
        
        # Calculate overall success
        successful_tests = [t for t in role_tests if t.get("toggle_logic_working", False) and t.get("role_logic_working", False)]
        toggle_logic_working = all(t.get("toggle_logic_working", False) for t in role_tests if "toggle_logic_working" in t)
        role_logic_working = all(t.get("role_logic_working", False) for t in role_tests if "role_logic_working" in t)
        
        return {
            "test_name": "Menu Configuration Logic",
            "success": len(successful_tests) > 0,
            "users_tested": len(test_users),
            "successful_tests": len(successful_tests),
            "toggle_logic_working": toggle_logic_working,
            "role_assignment_working": role_logic_working,
            "both_desktop_mobile_working": toggle_logic_working,  # Both desktop and mobile tested
            "configuration_logic_working": toggle_logic_working and role_logic_working,
            "detailed_role_tests": role_tests
        }
    
    async def test_admin_usage_simulation(self) -> Dict:
        """Simulate admin usage - disable menu item and verify it doesn't appear for users"""
        print("👨‍💼 Testing admin usage simulation (disable item and verify filtering)...")
        
        # Step 1: Admin disables a specific menu item
        admin_disable_settings = {
            "desktop_menu": {
                "about": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
                "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
                "create_listing": {"enabled": True, "roles": ["admin", "manager", "seller"]},
                "messages": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
                "tenders": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"]},  # DISABLED by admin
                "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
                "admin_panel": {"enabled": True, "roles": ["admin", "manager"]},
                "buy_management": {"enabled": True, "roles": ["admin", "manager", "buyer"]},
                "my_listings": {"enabled": True, "roles": ["admin", "manager", "seller"]},
                "favorites": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]}
            },
            "mobile_menu": {
                "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
                "messages": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
                "create": {"enabled": True, "roles": ["admin", "manager", "seller"]},
                "tenders": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"]},  # DISABLED by admin
                "listings": {"enabled": True, "roles": ["admin", "manager", "seller"]},
                "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
                "admin_drawer": {"enabled": True, "roles": ["admin", "manager"]}
            }
        }
        
        # Apply the admin's settings
        update_result = await self.make_request("/admin/menu-settings", "POST", data=admin_disable_settings)
        
        if not update_result["success"]:
            return {
                "test_name": "Admin Usage Simulation",
                "success": False,
                "error": f"Failed to apply admin settings: {update_result.get('error')}",
                "response_time_ms": update_result["response_time_ms"]
            }
        
        print(f"  ✅ Admin disabled 'tenders' menu item")
        
        # Step 2: Test that disabled item doesn't appear for different user types
        test_users = [
            {"id": "admin_user_1", "role": "admin", "description": "Admin User"},
            {"id": "68bfff790e4e46bc28d43631", "role": "buyer", "description": "Demo User (Buyer)"}
        ]
        
        user_verification_tests = []
        
        for user in test_users:
            user_result = await self.make_request(f"/menu-settings/user/{user['id']}")
            
            if user_result["success"]:
                user_data = user_result["data"]
                desktop_menu = user_data.get("desktop_menu", {})
                mobile_menu = user_data.get("mobile_menu", {})
                
                # Verify that 'tenders' is NOT present in either menu
                tenders_hidden_desktop = "tenders" not in desktop_menu
                tenders_hidden_mobile = "tenders" not in mobile_menu
                
                # Verify that other items are still present
                browse_present = "browse" in desktop_menu
                messages_present = "messages" in desktop_menu
                profile_present = "profile" in desktop_menu
                
                # Role-specific checks
                admin_panel_present = "admin_panel" in desktop_menu
                admin_panel_correct = (admin_panel_present and user["role"] == "admin") or (not admin_panel_present and user["role"] != "admin")
                
                user_verification_tests.append({
                    "user_id": user["id"],
                    "user_role": user["role"],
                    "description": user["description"],
                    "tenders_hidden_desktop": tenders_hidden_desktop,
                    "tenders_hidden_mobile": tenders_hidden_mobile,
                    "browse_present": browse_present,
                    "messages_present": messages_present,
                    "profile_present": profile_present,
                    "admin_panel_correct": admin_panel_correct,
                    "disabled_item_filtered": tenders_hidden_desktop and tenders_hidden_mobile,
                    "enabled_items_present": browse_present and messages_present and profile_present,
                    "role_filtering_correct": admin_panel_correct,
                    "verification_successful": tenders_hidden_desktop and tenders_hidden_mobile and browse_present and admin_panel_correct
                })
                
                print(f"  👤 {user['description']}: Tenders hidden: {tenders_hidden_desktop and tenders_hidden_mobile}, Other items present: {browse_present and messages_present}")
            else:
                user_verification_tests.append({
                    "user_id": user["id"],
                    "success": False,
                    "error": user_result.get("error")
                })
        
        # Step 3: Verify admin can still see the configuration
        admin_config_result = await self.make_request("/admin/menu-settings")
        admin_can_see_config = admin_config_result["success"]
        
        if admin_can_see_config:
            config_data = admin_config_result["data"]
            tenders_in_config = "tenders" in config_data.get("desktop_menu", {})
            tenders_disabled_in_config = not config_data.get("desktop_menu", {}).get("tenders", {}).get("enabled", True)
            admin_config_correct = tenders_in_config and tenders_disabled_in_config
            
            print(f"  ⚙️ Admin can see configuration: {admin_can_see_config}, Tenders disabled in config: {tenders_disabled_in_config}")
        else:
            admin_config_correct = False
        
        # Calculate overall success
        successful_verifications = [t for t in user_verification_tests if t.get("verification_successful", False)]
        all_users_verified = len(successful_verifications) == len(test_users)
        disabled_item_filtered_for_all = all(t.get("disabled_item_filtered", False) for t in user_verification_tests if "disabled_item_filtered" in t)
        role_filtering_works = all(t.get("role_filtering_correct", False) for t in user_verification_tests if "role_filtering_correct" in t)
        
        return {
            "test_name": "Admin Usage Simulation",
            "success": all_users_verified and admin_config_correct,
            "admin_settings_applied": update_result["success"],
            "users_tested": len(test_users),
            "successful_verifications": len(successful_verifications),
            "all_users_verified": all_users_verified,
            "disabled_item_filtered_correctly": disabled_item_filtered_for_all,
            "role_based_filtering_working": role_filtering_works,
            "admin_can_see_configuration": admin_can_see_config,
            "admin_config_shows_disabled_state": admin_config_correct,
            "simulation_successful": all_users_verified and admin_config_correct and disabled_item_filtered_for_all,
            "detailed_user_tests": user_verification_tests
        }
    
    async def run_comprehensive_menu_settings_test(self) -> Dict:
        """Run all menu settings tests"""
        print("🚀 Starting Menu Settings API Comprehensive Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Authenticate as admin first
            admin_auth_success = await self.authenticate_admin()
            if not admin_auth_success:
                return {
                    "error": "Failed to authenticate as admin user",
                    "test_timestamp": datetime.now().isoformat()
                }
            
            # Run all test suites
            default_settings_test = await self.test_get_default_menu_settings()
            update_settings_test = await self.test_update_menu_settings()
            user_filtering_test = await self.test_user_specific_menu_filtering()
            configuration_logic_test = await self.test_menu_configuration_logic()
            admin_simulation_test = await self.test_admin_usage_simulation()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "admin_authentication": {"success": admin_auth_success},
                "default_menu_settings": default_settings_test,
                "update_menu_settings": update_settings_test,
                "user_specific_filtering": user_filtering_test,
                "menu_configuration_logic": configuration_logic_test,
                "admin_usage_simulation": admin_simulation_test
            }
            
            # Calculate overall success metrics
            test_results = [
                default_settings_test.get("structure_valid", False),
                update_settings_test.get("update_successful", False),
                user_filtering_test.get("role_based_filtering_working", False),
                configuration_logic_test.get("configuration_logic_working", False),
                admin_simulation_test.get("simulation_successful", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "admin_authentication_working": admin_auth_success,
                "default_settings_working": default_settings_test.get("structure_valid", False),
                "update_settings_working": update_settings_test.get("update_successful", False),
                "user_filtering_working": user_filtering_test.get("role_based_filtering_working", False),
                "configuration_logic_working": configuration_logic_test.get("configuration_logic_working", False),
                "admin_simulation_working": admin_simulation_test.get("simulation_successful", False),
                "all_endpoints_working": all(test_results),
                "menu_settings_api_functional": overall_success_rate >= 80
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Run Menu Settings API tests"""
    print("🚀 Starting Menu Settings API Testing Suite")
    print("=" * 60)
    
    # Run Menu Settings API Tests
    menu_tester = MenuSettingsTester()
    menu_results = await menu_tester.run_comprehensive_menu_settings_test()
    
    print("\n" + "=" * 60)
    print("📊 MENU SETTINGS API TEST SUMMARY")
    print("=" * 60)
    
    menu_summary = menu_results.get("summary", {})
    
    print(f"Overall Success Rate: {menu_summary.get('overall_success_rate', 0):.1f}%")
    print(f"Admin Authentication: {'✅' if menu_summary.get('admin_authentication_working') else '❌'}")
    print(f"Default Settings: {'✅' if menu_summary.get('default_settings_working') else '❌'}")
    print(f"Update Settings: {'✅' if menu_summary.get('update_settings_working') else '❌'}")
    print(f"User Filtering: {'✅' if menu_summary.get('user_filtering_working') else '❌'}")
    print(f"Configuration Logic: {'✅' if menu_summary.get('configuration_logic_working') else '❌'}")
    print(f"Admin Simulation: {'✅' if menu_summary.get('admin_simulation_working') else '❌'}")
    
    if menu_summary.get('all_endpoints_working'):
        print("\n🎉 ALL MENU SETTINGS API TESTS PASSED! Menu Settings system is fully operational.")
    else:
        print(f"\n⚠️ Some menu settings tests failed. Success rate: {menu_summary.get('overall_success_rate', 0):.1f}%")
    
    # Save detailed results to file
    with open("menu_settings_test_results.json", "w") as f:
        json.dump(menu_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to menu_settings_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())