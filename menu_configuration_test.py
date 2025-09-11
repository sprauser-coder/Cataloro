#!/usr/bin/env python3
"""
Menu Configuration Issue Testing
Testing the specific issue where menu is showing "External Page" and "Internal Page" instead of normal menu items.
This test will check for corrupted custom menu items and clean up the menu configuration.
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
ADMIN_USERNAME = "sash_admin"
ADMIN_ROLE = "admin"
ADMIN_ID = "admin_user_1"

class MenuConfigurationTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.original_menu_settings = None
        self.corrupted_items_found = []
        
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
    
    async def check_menu_settings_database(self) -> Dict:
        """Check the menu settings database for corrupted custom menu items"""
        print("🔍 Checking menu settings database for corrupted data...")
        
        if not self.admin_token:
            return {"test_name": "Menu Settings Database Check", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get current menu settings from admin endpoint
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not result["success"]:
            print(f"  ❌ Failed to retrieve menu settings: {result.get('error')}")
            return {
                "test_name": "Menu Settings Database Check",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
        
        # Store original settings for potential restoration
        self.original_menu_settings = result["data"]
        
        # Check for corrupted custom menu items
        desktop_menu = result["data"].get("desktop_menu", {})
        mobile_menu = result["data"].get("mobile_menu", {})
        
        desktop_custom_items = desktop_menu.get("custom_items", [])
        mobile_custom_items = mobile_menu.get("custom_items", [])
        
        # Look for corrupted items with labels "External Page" and "Internal Page"
        corrupted_desktop_items = []
        corrupted_mobile_items = []
        
        for item in desktop_custom_items:
            label = item.get("label", "")
            if label in ["External Page", "Internal Page"]:
                corrupted_desktop_items.append(item)
                self.corrupted_items_found.append({"platform": "desktop", "item": item})
        
        for item in mobile_custom_items:
            label = item.get("label", "")
            if label in ["External Page", "Internal Page"]:
                corrupted_mobile_items.append(item)
                self.corrupted_items_found.append({"platform": "mobile", "item": item})
        
        total_corrupted = len(corrupted_desktop_items) + len(corrupted_mobile_items)
        
        print(f"  📊 Desktop custom items: {len(desktop_custom_items)}")
        print(f"  📊 Mobile custom items: {len(mobile_custom_items)}")
        print(f"  ⚠️ Corrupted desktop items found: {len(corrupted_desktop_items)}")
        print(f"  ⚠️ Corrupted mobile items found: {len(corrupted_mobile_items)}")
        print(f"  🚨 Total corrupted items: {total_corrupted}")
        
        if total_corrupted > 0:
            print("  🔍 Corrupted items details:")
            for corrupted in self.corrupted_items_found:
                item = corrupted["item"]
                platform = corrupted["platform"]
                print(f"    - {platform.upper()}: '{item.get('label')}' (ID: {item.get('id', 'N/A')})")
        
        return {
            "test_name": "Menu Settings Database Check",
            "success": True,
            "response_time_ms": result["response_time_ms"],
            "desktop_custom_items_count": len(desktop_custom_items),
            "mobile_custom_items_count": len(mobile_custom_items),
            "corrupted_desktop_items": len(corrupted_desktop_items),
            "corrupted_mobile_items": len(corrupted_mobile_items),
            "total_corrupted_items": total_corrupted,
            "corrupted_items_found": total_corrupted > 0,
            "corrupted_items_details": self.corrupted_items_found,
            "original_settings_stored": True
        }
    
    async def clear_corrupted_menu_items(self) -> Dict:
        """Clear or reset the corrupted custom menu items data"""
        print("🧹 Clearing corrupted custom menu items...")
        
        if not self.admin_token:
            return {"test_name": "Clear Corrupted Menu Items", "error": "No admin token available"}
        
        if not self.original_menu_settings:
            return {"test_name": "Clear Corrupted Menu Items", "error": "No original menu settings available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create clean menu settings by removing corrupted items
        clean_settings = {
            "desktop_menu": {},
            "mobile_menu": {}
        }
        
        # Copy original settings but filter out corrupted items
        original_desktop = self.original_menu_settings.get("desktop_menu", {})
        original_mobile = self.original_menu_settings.get("mobile_menu", {})
        
        # Clean desktop menu
        clean_settings["desktop_menu"] = original_desktop.copy()
        if "custom_items" in original_desktop:
            clean_desktop_items = []
            for item in original_desktop["custom_items"]:
                label = item.get("label", "")
                if label not in ["External Page", "Internal Page"]:
                    clean_desktop_items.append(item)
            clean_settings["desktop_menu"]["custom_items"] = clean_desktop_items
        
        # Clean mobile menu
        clean_settings["mobile_menu"] = original_mobile.copy()
        if "custom_items" in original_mobile:
            clean_mobile_items = []
            for item in original_mobile["custom_items"]:
                label = item.get("label", "")
                if label not in ["External Page", "Internal Page"]:
                    clean_mobile_items.append(item)
            clean_settings["mobile_menu"]["custom_items"] = clean_mobile_items
        
        # Save the cleaned settings
        result = await self.make_request("/admin/menu-settings", "POST", data=clean_settings, headers=headers)
        
        if result["success"]:
            response_data = result["data"]
            settings = response_data.get("settings", {})
            
            # Verify cleaning was successful
            desktop_custom = settings.get("desktop_menu", {}).get("custom_items", [])
            mobile_custom = settings.get("mobile_menu", {}).get("custom_items", [])
            
            # Check if any corrupted items remain
            remaining_corrupted = 0
            for item in desktop_custom + mobile_custom:
                if item.get("label") in ["External Page", "Internal Page"]:
                    remaining_corrupted += 1
            
            cleaning_successful = remaining_corrupted == 0
            
            print(f"  ✅ Menu settings updated successfully")
            print(f"  📊 Desktop custom items after cleaning: {len(desktop_custom)}")
            print(f"  📊 Mobile custom items after cleaning: {len(mobile_custom)}")
            print(f"  🧹 Remaining corrupted items: {remaining_corrupted}")
            print(f"  {'✅' if cleaning_successful else '❌'} Cleaning {'successful' if cleaning_successful else 'failed'}")
            
            return {
                "test_name": "Clear Corrupted Menu Items",
                "success": cleaning_successful,
                "response_time_ms": result["response_time_ms"],
                "desktop_items_after_cleaning": len(desktop_custom),
                "mobile_items_after_cleaning": len(mobile_custom),
                "remaining_corrupted_items": remaining_corrupted,
                "cleaning_successful": cleaning_successful,
                "cleaned_settings_saved": True
            }
        else:
            print(f"  ❌ Failed to save cleaned menu settings: {result.get('error')}")
            return {
                "test_name": "Clear Corrupted Menu Items",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def verify_user_menu_endpoint(self) -> Dict:
        """Verify the /api/menu-settings/user/{userId} endpoint returns clean data structure"""
        print("🔍 Verifying user menu endpoint returns clean data...")
        
        # Test with admin user ID
        result = await self.make_request(f"/menu-settings/user/{ADMIN_ID}")
        
        if result["success"]:
            user_menu_data = result["data"]
            desktop_menu = user_menu_data.get("desktop_menu", {})
            mobile_menu = user_menu_data.get("mobile_menu", {})
            
            # Check for corrupted items in user menu response
            desktop_custom = desktop_menu.get("custom_items", [])
            mobile_custom = mobile_menu.get("custom_items", [])
            
            corrupted_in_user_menu = 0
            for item in desktop_custom + mobile_custom:
                if item.get("label") in ["External Page", "Internal Page"]:
                    corrupted_in_user_menu += 1
            
            # Verify data structure integrity
            has_desktop_menu = "desktop_menu" in user_menu_data
            has_mobile_menu = "mobile_menu" in user_menu_data
            has_user_role = "user_role" in user_menu_data
            
            structure_valid = has_desktop_menu and has_mobile_menu and has_user_role
            data_clean = corrupted_in_user_menu == 0
            
            print(f"  ✅ User menu endpoint accessible")
            print(f"  📊 Desktop menu items: {len(desktop_custom)}")
            print(f"  📊 Mobile menu items: {len(mobile_custom)}")
            print(f"  🚨 Corrupted items in user menu: {corrupted_in_user_menu}")
            print(f"  🏗️ Data structure valid: {structure_valid}")
            print(f"  🧹 Data clean: {data_clean}")
            
            return {
                "test_name": "User Menu Endpoint Verification",
                "success": structure_valid and data_clean,
                "response_time_ms": result["response_time_ms"],
                "desktop_menu_items": len(desktop_custom),
                "mobile_menu_items": len(mobile_custom),
                "corrupted_items_in_user_menu": corrupted_in_user_menu,
                "data_structure_valid": structure_valid,
                "data_clean": data_clean,
                "user_role": user_menu_data.get("user_role", "unknown")
            }
        else:
            print(f"  ❌ User menu endpoint failed: {result.get('error')}")
            return {
                "test_name": "User Menu Endpoint Verification",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def test_menu_settings_api_endpoints(self) -> Dict:
        """Test the menu settings API endpoints to ensure they work properly"""
        print("🔧 Testing menu settings API endpoints...")
        
        if not self.admin_token:
            return {"test_name": "Menu Settings API Endpoints", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        endpoint_tests = []
        
        # Test 1: GET /api/admin/menu-settings
        print("  Testing GET /api/admin/menu-settings...")
        get_result = await self.make_request("/admin/menu-settings", headers=headers)
        endpoint_tests.append({
            "endpoint": "GET /api/admin/menu-settings",
            "success": get_result["success"],
            "status": get_result["status"],
            "response_time_ms": get_result["response_time_ms"],
            "has_data": bool(get_result.get("data"))
        })
        
        # Test 2: POST /api/admin/menu-settings (with valid data)
        print("  Testing POST /api/admin/menu-settings...")
        if get_result["success"]:
            # Use current settings for POST test
            current_settings = get_result["data"]
            post_result = await self.make_request("/admin/menu-settings", "POST", data=current_settings, headers=headers)
            endpoint_tests.append({
                "endpoint": "POST /api/admin/menu-settings",
                "success": post_result["success"],
                "status": post_result["status"],
                "response_time_ms": post_result["response_time_ms"],
                "settings_saved": post_result["success"]
            })
        else:
            endpoint_tests.append({
                "endpoint": "POST /api/admin/menu-settings",
                "success": False,
                "error": "GET failed, cannot test POST"
            })
        
        # Test 3: GET /api/menu-settings/user/{userId}
        print("  Testing GET /api/menu-settings/user/{userId}...")
        user_result = await self.make_request(f"/menu-settings/user/{ADMIN_ID}")
        endpoint_tests.append({
            "endpoint": f"GET /api/menu-settings/user/{ADMIN_ID}",
            "success": user_result["success"],
            "status": user_result["status"],
            "response_time_ms": user_result["response_time_ms"],
            "has_user_data": bool(user_result.get("data"))
        })
        
        # Test 4: GET /api/admin/available-pages
        print("  Testing GET /api/admin/available-pages...")
        pages_result = await self.make_request("/admin/available-pages", headers=headers)
        endpoint_tests.append({
            "endpoint": "GET /api/admin/available-pages",
            "success": pages_result["success"],
            "status": pages_result["status"],
            "response_time_ms": pages_result["response_time_ms"],
            "has_pages": bool(pages_result.get("data", {}).get("available_pages"))
        })
        
        # Test 5: GET /api/admin/available-icons
        print("  Testing GET /api/admin/available-icons...")
        icons_result = await self.make_request("/admin/available-icons", headers=headers)
        endpoint_tests.append({
            "endpoint": "GET /api/admin/available-icons",
            "success": icons_result["success"],
            "status": icons_result["status"],
            "response_time_ms": icons_result["response_time_ms"],
            "has_icons": bool(icons_result.get("data", {}).get("available_icons"))
        })
        
        # Calculate overall API health
        successful_endpoints = sum(1 for test in endpoint_tests if test.get("success", False))
        api_health = successful_endpoints / len(endpoint_tests) * 100
        
        print(f"  📊 API endpoints tested: {len(endpoint_tests)}")
        print(f"  ✅ Successful endpoints: {successful_endpoints}")
        print(f"  📈 API health: {api_health:.1f}%")
        
        return {
            "test_name": "Menu Settings API Endpoints",
            "success": api_health >= 80,  # Consider successful if 80% or more endpoints work
            "total_endpoints_tested": len(endpoint_tests),
            "successful_endpoints": successful_endpoints,
            "api_health_percentage": api_health,
            "all_endpoints_working": api_health == 100,
            "detailed_tests": endpoint_tests
        }
    
    async def reset_menu_to_default_state(self) -> Dict:
        """Reset the menu configuration to default state if needed"""
        print("🔄 Resetting menu configuration to default state...")
        
        if not self.admin_token:
            return {"test_name": "Reset Menu to Default", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Define default menu configuration
        default_menu_settings = {
            "desktop_menu": {
                "about": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "path": "/about"},
                "browse": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "path": "/browse"},
                "create_listing": {"enabled": False, "roles": ["admin", "manager", "seller"], "path": "/create-listing"},
                "messages": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "path": "/messages"},
                "my_listings": {"enabled": False, "roles": ["admin", "manager", "seller"], "path": "/my-listings"},
                "favorites": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "path": "/favorites"},
                "tenders": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "path": "/tenders"},
                "buy_management": {"enabled": False, "roles": ["admin", "manager", "buyer"], "path": "/buy-management"},
                "sell_management": {"enabled": False, "roles": ["admin", "manager", "seller"], "path": "/sell-management"},
                "admin_panel": {"enabled": True, "roles": ["admin", "manager"], "path": "/admin"},
                "custom_items": []  # Clear any custom items
            },
            "mobile_menu": {
                "about": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "path": "/about"},
                "browse": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "path": "/browse"},
                "create_listing": {"enabled": False, "roles": ["admin", "manager", "seller"], "path": "/create-listing"},
                "messages": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "path": "/messages"},
                "my_listings": {"enabled": False, "roles": ["admin", "manager", "seller"], "path": "/my-listings"},
                "favorites": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "path": "/favorites"},
                "tenders": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "path": "/tenders"},
                "admin_drawer": {"enabled": True, "roles": ["admin", "manager"], "path": "/admin"},
                "custom_items": []  # Clear any custom items
            }
        }
        
        # Apply default settings
        result = await self.make_request("/admin/menu-settings", "POST", data=default_menu_settings, headers=headers)
        
        if result["success"]:
            response_data = result["data"]
            settings = response_data.get("settings", {})
            
            # Verify reset was successful
            desktop_custom = settings.get("desktop_menu", {}).get("custom_items", [])
            mobile_custom = settings.get("mobile_menu", {}).get("custom_items", [])
            
            # Check that admin panel is enabled
            admin_panel_enabled = settings.get("desktop_menu", {}).get("admin_panel", {}).get("enabled", False)
            admin_drawer_enabled = settings.get("mobile_menu", {}).get("admin_drawer", {}).get("enabled", False)
            
            reset_successful = (
                len(desktop_custom) == 0 and 
                len(mobile_custom) == 0 and 
                admin_panel_enabled and 
                admin_drawer_enabled
            )
            
            print(f"  ✅ Default menu settings applied")
            print(f"  📊 Desktop custom items after reset: {len(desktop_custom)}")
            print(f"  📊 Mobile custom items after reset: {len(mobile_custom)}")
            print(f"  🖥️ Admin panel enabled: {admin_panel_enabled}")
            print(f"  📱 Admin drawer enabled: {admin_drawer_enabled}")
            print(f"  {'✅' if reset_successful else '❌'} Reset {'successful' if reset_successful else 'failed'}")
            
            return {
                "test_name": "Reset Menu to Default",
                "success": reset_successful,
                "response_time_ms": result["response_time_ms"],
                "desktop_custom_items_after_reset": len(desktop_custom),
                "mobile_custom_items_after_reset": len(mobile_custom),
                "admin_panel_enabled": admin_panel_enabled,
                "admin_drawer_enabled": admin_drawer_enabled,
                "reset_successful": reset_successful,
                "default_settings_applied": True
            }
        else:
            print(f"  ❌ Failed to apply default menu settings: {result.get('error')}")
            return {
                "test_name": "Reset Menu to Default",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def final_verification_test(self) -> Dict:
        """Final verification that menu configuration is clean and working"""
        print("🔍 Final verification of menu configuration...")
        
        verification_results = []
        
        # Test 1: Admin menu settings should be clean
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            admin_result = await self.make_request("/admin/menu-settings", headers=headers)
            
            if admin_result["success"]:
                settings = admin_result["data"]
                desktop_custom = settings.get("desktop_menu", {}).get("custom_items", [])
                mobile_custom = settings.get("mobile_menu", {}).get("custom_items", [])
                
                # Check for any remaining corrupted items
                corrupted_count = 0
                for item in desktop_custom + mobile_custom:
                    if item.get("label") in ["External Page", "Internal Page"]:
                        corrupted_count += 1
                
                verification_results.append({
                    "test": "Admin Menu Settings Clean",
                    "success": corrupted_count == 0,
                    "corrupted_items_found": corrupted_count,
                    "total_custom_items": len(desktop_custom) + len(mobile_custom)
                })
            else:
                verification_results.append({
                    "test": "Admin Menu Settings Clean",
                    "success": False,
                    "error": "Failed to retrieve admin menu settings"
                })
        
        # Test 2: User menu endpoint should return clean data
        user_result = await self.make_request(f"/menu-settings/user/{ADMIN_ID}")
        
        if user_result["success"]:
            user_data = user_result["data"]
            desktop_menu = user_data.get("desktop_menu", {})
            mobile_menu = user_data.get("mobile_menu", {})
            
            desktop_custom = desktop_menu.get("custom_items", [])
            mobile_custom = mobile_menu.get("custom_items", [])
            
            # Check for corrupted items in user response
            user_corrupted_count = 0
            for item in desktop_custom + mobile_custom:
                if item.get("label") in ["External Page", "Internal Page"]:
                    user_corrupted_count += 1
            
            verification_results.append({
                "test": "User Menu Endpoint Clean",
                "success": user_corrupted_count == 0,
                "corrupted_items_in_user_response": user_corrupted_count,
                "user_desktop_items": len(desktop_custom),
                "user_mobile_items": len(mobile_custom)
            })
        else:
            verification_results.append({
                "test": "User Menu Endpoint Clean",
                "success": False,
                "error": "Failed to retrieve user menu settings"
            })
        
        # Test 3: Menu structure should be valid
        if user_result["success"]:
            user_data = user_result["data"]
            has_required_fields = all(field in user_data for field in ["desktop_menu", "mobile_menu", "user_role"])
            
            verification_results.append({
                "test": "Menu Structure Valid",
                "success": has_required_fields,
                "has_desktop_menu": "desktop_menu" in user_data,
                "has_mobile_menu": "mobile_menu" in user_data,
                "has_user_role": "user_role" in user_data
            })
        
        # Calculate overall verification success
        successful_verifications = sum(1 for result in verification_results if result.get("success", False))
        verification_success = successful_verifications == len(verification_results)
        
        print(f"  📊 Verification tests: {successful_verifications}/{len(verification_results)} passed")
        print(f"  {'✅' if verification_success else '❌'} Final verification {'successful' if verification_success else 'failed'}")
        
        return {
            "test_name": "Final Verification",
            "success": verification_success,
            "total_verification_tests": len(verification_results),
            "successful_verifications": successful_verifications,
            "verification_complete": verification_success,
            "detailed_results": verification_results
        }
    
    async def run_comprehensive_menu_configuration_test(self) -> Dict:
        """Run all menu configuration tests"""
        print("🚀 Starting Menu Configuration Issue Testing")
        print("=" * 70)
        print("🎯 OBJECTIVE: Fix menu showing 'External Page' and 'Internal Page' instead of normal menu items")
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
            
            # Run all test suites in sequence
            database_check = await self.check_menu_settings_database()
            
            # Only proceed with cleaning if corrupted items were found
            if database_check.get("corrupted_items_found", False):
                print("\n🚨 CORRUPTED MENU ITEMS DETECTED - PROCEEDING WITH CLEANUP")
                clear_corrupted = await self.clear_corrupted_menu_items()
            else:
                print("\n✅ NO CORRUPTED MENU ITEMS FOUND - SKIPPING CLEANUP")
                clear_corrupted = {
                    "test_name": "Clear Corrupted Menu Items",
                    "success": True,
                    "note": "No corrupted items found, cleanup not needed"
                }
            
            user_menu_verification = await self.verify_user_menu_endpoint()
            api_endpoints_test = await self.test_menu_settings_api_endpoints()
            
            # Reset to default state if there were issues
            if not clear_corrupted.get("success", True) or not user_menu_verification.get("success", True):
                print("\n🔄 ISSUES DETECTED - RESETTING TO DEFAULT STATE")
                reset_default = await self.reset_menu_to_default_state()
            else:
                print("\n✅ NO RESET NEEDED - MENU CONFIGURATION IS CLEAN")
                reset_default = {
                    "test_name": "Reset Menu to Default",
                    "success": True,
                    "note": "Reset not needed, menu configuration is clean"
                }
            
            final_verification = await self.final_verification_test()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "objective": "Fix menu showing 'External Page' and 'Internal Page' instead of normal menu items",
                "database_check": database_check,
                "clear_corrupted_items": clear_corrupted,
                "user_menu_verification": user_menu_verification,
                "api_endpoints_test": api_endpoints_test,
                "reset_to_default": reset_default,
                "final_verification": final_verification
            }
            
            # Calculate overall success metrics
            test_results = [
                database_check.get("success", False),
                clear_corrupted.get("success", False),
                user_menu_verification.get("success", False),
                api_endpoints_test.get("success", False),
                reset_default.get("success", False),
                final_verification.get("success", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            # Determine if the main issue was resolved
            corrupted_items_found = database_check.get("corrupted_items_found", False)
            corrupted_items_cleared = clear_corrupted.get("cleaning_successful", True)  # True if no cleaning was needed
            user_menu_clean = user_menu_verification.get("data_clean", False)
            final_verification_passed = final_verification.get("success", False)
            
            issue_resolved = (
                not corrupted_items_found or  # No corrupted items found, OR
                (corrupted_items_found and corrupted_items_cleared and user_menu_clean and final_verification_passed)  # Items found and successfully cleaned
            )
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "corrupted_items_initially_found": corrupted_items_found,
                "corrupted_items_count": database_check.get("total_corrupted_items", 0),
                "corrupted_items_cleared": corrupted_items_cleared,
                "user_menu_endpoint_clean": user_menu_clean,
                "api_endpoints_working": api_endpoints_test.get("success", False),
                "menu_reset_successful": reset_default.get("success", False),
                "final_verification_passed": final_verification_passed,
                "main_issue_resolved": issue_resolved,
                "all_tests_passed": overall_success_rate == 100,
                "critical_functionality_working": (
                    user_menu_verification.get("success", False) and
                    api_endpoints_test.get("success", False) and
                    final_verification.get("success", False)
                )
            }
            
            # Print final summary
            print("\n" + "=" * 70)
            print("📋 MENU CONFIGURATION TEST SUMMARY")
            print("=" * 70)
            print(f"🎯 Main Issue Resolved: {'✅ YES' if issue_resolved else '❌ NO'}")
            print(f"📊 Overall Success Rate: {overall_success_rate:.1f}%")
            print(f"🚨 Corrupted Items Found: {database_check.get('total_corrupted_items', 0)}")
            print(f"🧹 Corrupted Items Cleared: {'✅' if corrupted_items_cleared else '❌'}")
            print(f"🔍 User Menu Clean: {'✅' if user_menu_clean else '❌'}")
            print(f"🔧 API Endpoints Working: {'✅' if api_endpoints_test.get('success', False) else '❌'}")
            print(f"✅ Final Verification: {'✅' if final_verification_passed else '❌'}")
            print("=" * 70)
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main function to run the menu configuration tests"""
    tester = MenuConfigurationTester()
    results = await tester.run_comprehensive_menu_configuration_test()
    
    # Print results in a formatted way
    print("\n" + "=" * 70)
    print("📊 DETAILED TEST RESULTS")
    print("=" * 70)
    
    for test_name, test_result in results.items():
        if test_name in ["test_timestamp", "objective", "summary"]:
            continue
            
        if isinstance(test_result, dict):
            success = test_result.get("success", False)
            print(f"\n{test_result.get('test_name', test_name)}: {'✅ PASS' if success else '❌ FAIL'}")
            
            if not success and "error" in test_result:
                print(f"  Error: {test_result['error']}")
            
            # Print key metrics
            for key, value in test_result.items():
                if key in ["test_name", "success", "error", "detailed_tests", "detailed_results", "detailed_steps"]:
                    continue
                if isinstance(value, (int, float, bool, str)) and len(str(value)) < 100:
                    print(f"  {key}: {value}")
    
    # Print summary
    if "summary" in results:
        summary = results["summary"]
        print(f"\n📋 FINAL SUMMARY:")
        print(f"  Main Issue Resolved: {'✅' if summary.get('main_issue_resolved', False) else '❌'}")
        print(f"  Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
        print(f"  Critical Functionality Working: {'✅' if summary.get('critical_functionality_working', False) else '❌'}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())