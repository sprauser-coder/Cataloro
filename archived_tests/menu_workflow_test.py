#!/usr/bin/env python3
"""
Menu Settings Admin Workflow Testing
Testing the specific data flow issue where items marked as "hidden" in admin menu settings 
are still showing up in the actual menu.

SPECIFIC FOCUS:
- Check if menu items use "enabled" vs "visible" property
- Test the full workflow: Admin disables item → Database update → User API response
- Verify the `/api/menu-settings/user/{user_id}` endpoint reflects the admin changes
- Check what properties are actually being set/read in both APIs
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

# Test User Configuration (for user menu testing)
TEST_USER_EMAIL = "demo@cataloro.com"
TEST_USER_ID = "68bfff790e4e46bc28d43631"  # Fixed demo user ID

class MenuWorkflowTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_user_token = None
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
    
    async def authenticate_test_user(self) -> bool:
        """Authenticate as test user"""
        print("🔐 Authenticating as test user...")
        
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": "test_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.test_user_token = result["data"].get("token", "")
            print(f"  ✅ Test user authentication successful")
            return True
        else:
            print(f"  ❌ Test user authentication failed: {result.get('error', 'Unknown error')}")
            return False
    
    async def step1_get_current_admin_menu_settings(self) -> Dict:
        """Step 1: Get the current menu settings from the admin API"""
        print("\n📋 STEP 1: Getting current menu settings from admin API...")
        
        if not self.admin_token:
            return {"test_name": "Admin Menu Settings GET", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if result["success"]:
            data = result["data"]
            self.original_menu_settings = data  # Store for restoration
            
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            
            print(f"  ✅ Admin menu settings retrieved successfully")
            print(f"  🖥️ Desktop menu items: {len(desktop_menu)}")
            print(f"  📱 Mobile menu items: {len(mobile_menu)}")
            
            # Analyze property names used
            property_analysis = self.analyze_menu_properties(desktop_menu, mobile_menu)
            
            print(f"  🔍 Property analysis:")
            print(f"    - Uses 'enabled' property: {property_analysis['uses_enabled']}")
            print(f"    - Uses 'visible' property: {property_analysis['uses_visible']}")
            print(f"    - Sample item structure: {property_analysis['sample_item']}")
            
            return {
                "test_name": "Admin Menu Settings GET",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "desktop_items_count": len(desktop_menu),
                "mobile_items_count": len(mobile_menu),
                "property_analysis": property_analysis,
                "full_data": data
            }
        else:
            print(f"  ❌ Failed to get admin menu settings: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Admin Menu Settings GET",
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"]
            }
    
    async def step2_disable_menu_item(self, item_to_disable: str = "browse") -> Dict:
        """Step 2: Update a menu item to set it as disabled (enabled: false) via admin API"""
        print(f"\n🔧 STEP 2: Disabling menu item '{item_to_disable}' via admin API...")
        
        if not self.admin_token or not self.original_menu_settings:
            return {"test_name": "Disable Menu Item", "error": "No admin token or original settings available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create modified settings with the specified item disabled
        modified_settings = json.loads(json.dumps(self.original_menu_settings))  # Deep copy
        
        # Disable the item in both desktop and mobile menus
        desktop_menu = modified_settings.get("desktop_menu", {})
        mobile_menu = modified_settings.get("mobile_menu", {})
        
        item_found = False
        original_enabled_state = {}
        
        if item_to_disable in desktop_menu:
            original_enabled_state["desktop"] = desktop_menu[item_to_disable].get("enabled", True)
            desktop_menu[item_to_disable]["enabled"] = False
            item_found = True
            print(f"  🖥️ Disabled '{item_to_disable}' in desktop menu (was: {original_enabled_state['desktop']})")
        
        if item_to_disable in mobile_menu:
            original_enabled_state["mobile"] = mobile_menu[item_to_disable].get("enabled", True)
            mobile_menu[item_to_disable]["enabled"] = False
            item_found = True
            print(f"  📱 Disabled '{item_to_disable}' in mobile menu (was: {original_enabled_state['mobile']})")
        
        if not item_found:
            print(f"  ❌ Item '{item_to_disable}' not found in menu settings")
            return {
                "test_name": "Disable Menu Item",
                "success": False,
                "error": f"Item '{item_to_disable}' not found in menu settings"
            }
        
        # Save the modified settings
        result = await self.make_request("/admin/menu-settings", "POST", data=modified_settings, headers=headers)
        
        if result["success"]:
            print(f"  ✅ Successfully disabled '{item_to_disable}' in admin menu settings")
            
            # Verify the change was saved by getting settings again
            verify_result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
            
            verification_success = False
            if verify_result["success"]:
                verify_data = verify_result["data"]
                desktop_verify = verify_data.get("desktop_menu", {}).get(item_to_disable, {})
                mobile_verify = verify_data.get("mobile_menu", {}).get(item_to_disable, {})
                
                desktop_disabled = desktop_verify.get("enabled") == False
                mobile_disabled = mobile_verify.get("enabled") == False
                
                verification_success = desktop_disabled and mobile_disabled
                print(f"  🔍 Verification: Desktop disabled={desktop_disabled}, Mobile disabled={mobile_disabled}")
            
            return {
                "test_name": "Disable Menu Item",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "item_disabled": item_to_disable,
                "original_enabled_state": original_enabled_state,
                "verification_success": verification_success,
                "modified_settings": modified_settings
            }
        else:
            print(f"  ❌ Failed to disable menu item: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Disable Menu Item",
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"]
            }
    
    async def step3_check_user_menu_response(self, user_id: str = None) -> Dict:
        """Step 3: Check what the user menu settings API returns for a regular user"""
        print(f"\n👤 STEP 3: Checking user menu settings API response...")
        
        if not user_id:
            user_id = TEST_USER_ID
        
        result = await self.make_request(f"/menu-settings/user/{user_id}")
        
        if result["success"]:
            data = result["data"]
            
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            user_role = data.get("user_role", "unknown")
            
            print(f"  ✅ User menu settings retrieved successfully")
            print(f"  👤 User role: {user_role}")
            print(f"  🖥️ Desktop menu items: {len(desktop_menu)}")
            print(f"  📱 Mobile menu items: {len(mobile_menu)}")
            
            # Check if disabled items are present or absent
            disabled_item_analysis = self.analyze_disabled_items(desktop_menu, mobile_menu)
            
            print(f"  🔍 Disabled item analysis:")
            for item, analysis in disabled_item_analysis.items():
                print(f"    - {item}: Desktop present={analysis['desktop_present']}, Mobile present={analysis['mobile_present']}")
                if analysis['desktop_present']:
                    print(f"      Desktop enabled={analysis['desktop_enabled']}")
                if analysis['mobile_present']:
                    print(f"      Mobile enabled={analysis['mobile_enabled']}")
            
            return {
                "test_name": "User Menu Settings Response",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "user_role": user_role,
                "desktop_items_count": len(desktop_menu),
                "mobile_items_count": len(mobile_menu),
                "disabled_item_analysis": disabled_item_analysis,
                "full_data": data
            }
        else:
            print(f"  ❌ Failed to get user menu settings: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "User Menu Settings Response",
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"]
            }
    
    async def step4_verify_data_structure_consistency(self, admin_data: Dict, user_data: Dict) -> Dict:
        """Step 4: Verify the data structure and property names being used"""
        print(f"\n🔍 STEP 4: Verifying data structure and property consistency...")
        
        consistency_analysis = {
            "admin_uses_enabled": False,
            "admin_uses_visible": False,
            "user_uses_enabled": False,
            "user_uses_visible": False,
            "property_mismatch": False,
            "disabled_items_filtered": True,
            "structure_consistent": True
        }
        
        # Analyze admin API structure
        admin_desktop = admin_data.get("desktop_menu", {})
        admin_mobile = admin_data.get("mobile_menu", {})
        
        for item_key, item_data in admin_desktop.items():
            if isinstance(item_data, dict):
                if "enabled" in item_data:
                    consistency_analysis["admin_uses_enabled"] = True
                if "visible" in item_data:
                    consistency_analysis["admin_uses_visible"] = True
                break
        
        # Analyze user API structure
        user_desktop = user_data.get("desktop_menu", {})
        user_mobile = user_data.get("mobile_menu", {})
        
        for item_key, item_data in user_desktop.items():
            if isinstance(item_data, dict):
                if "enabled" in item_data:
                    consistency_analysis["user_uses_enabled"] = True
                if "visible" in item_data:
                    consistency_analysis["user_uses_visible"] = True
                break
        
        # Check for property mismatch
        consistency_analysis["property_mismatch"] = (
            (consistency_analysis["admin_uses_enabled"] and not consistency_analysis["user_uses_enabled"]) or
            (consistency_analysis["admin_uses_visible"] and not consistency_analysis["user_uses_visible"]) or
            (consistency_analysis["admin_uses_enabled"] != consistency_analysis["user_uses_enabled"])
        )
        
        # Check if disabled items are properly filtered in user API
        disabled_items_in_user = []
        for item_key, item_data in user_desktop.items():
            if isinstance(item_data, dict) and item_data.get("enabled") == False:
                disabled_items_in_user.append(f"desktop_{item_key}")
        
        for item_key, item_data in user_mobile.items():
            if isinstance(item_data, dict) and item_data.get("enabled") == False:
                disabled_items_in_user.append(f"mobile_{item_key}")
        
        consistency_analysis["disabled_items_filtered"] = len(disabled_items_in_user) == 0
        consistency_analysis["disabled_items_in_user"] = disabled_items_in_user
        
        # Overall structure consistency check
        admin_structure = set(admin_desktop.keys()) | set(admin_mobile.keys())
        user_structure = set(user_desktop.keys()) | set(user_mobile.keys())
        
        # User structure should be subset of admin structure (due to filtering)
        consistency_analysis["structure_consistent"] = user_structure.issubset(admin_structure)
        consistency_analysis["admin_items"] = list(admin_structure)
        consistency_analysis["user_items"] = list(user_structure)
        consistency_analysis["missing_in_user"] = list(admin_structure - user_structure)
        
        print(f"  🔍 Property usage:")
        print(f"    - Admin API uses 'enabled': {consistency_analysis['admin_uses_enabled']}")
        print(f"    - Admin API uses 'visible': {consistency_analysis['admin_uses_visible']}")
        print(f"    - User API uses 'enabled': {consistency_analysis['user_uses_enabled']}")
        print(f"    - User API uses 'visible': {consistency_analysis['user_uses_visible']}")
        print(f"    - Property mismatch detected: {consistency_analysis['property_mismatch']}")
        
        print(f"  🔍 Filtering analysis:")
        print(f"    - Disabled items properly filtered: {consistency_analysis['disabled_items_filtered']}")
        print(f"    - Disabled items in user response: {len(disabled_items_in_user)}")
        print(f"    - Structure consistent: {consistency_analysis['structure_consistent']}")
        print(f"    - Items missing in user API: {consistency_analysis['missing_in_user']}")
        
        overall_success = (
            not consistency_analysis["property_mismatch"] and
            consistency_analysis["disabled_items_filtered"] and
            consistency_analysis["structure_consistent"]
        )
        
        return {
            "test_name": "Data Structure Consistency",
            "success": overall_success,
            "consistency_analysis": consistency_analysis,
            "root_cause_identified": consistency_analysis["property_mismatch"] or not consistency_analysis["disabled_items_filtered"]
        }
    
    def analyze_menu_properties(self, desktop_menu: Dict, mobile_menu: Dict) -> Dict:
        """Analyze what properties are used in menu items"""
        analysis = {
            "uses_enabled": False,
            "uses_visible": False,
            "sample_item": None,
            "all_properties": set()
        }
        
        # Check desktop menu
        for item_key, item_data in desktop_menu.items():
            if isinstance(item_data, dict) and item_key != "custom_items":
                if "enabled" in item_data:
                    analysis["uses_enabled"] = True
                if "visible" in item_data:
                    analysis["uses_visible"] = True
                
                if not analysis["sample_item"]:
                    analysis["sample_item"] = {
                        "item_key": item_key,
                        "properties": list(item_data.keys()),
                        "data": item_data
                    }
                
                analysis["all_properties"].update(item_data.keys())
        
        analysis["all_properties"] = list(analysis["all_properties"])
        return analysis
    
    def analyze_disabled_items(self, desktop_menu: Dict, mobile_menu: Dict) -> Dict:
        """Analyze which items are disabled and their presence in user menu"""
        analysis = {}
        
        # Common menu items to check
        common_items = ["browse", "create_listing", "messages", "my_listings", "tenders", "inventory", "admin_panel", "admin_drawer"]
        
        for item in common_items:
            item_analysis = {
                "desktop_present": item in desktop_menu,
                "mobile_present": item in mobile_menu,
                "desktop_enabled": None,
                "mobile_enabled": None
            }
            
            if item_analysis["desktop_present"]:
                desktop_item = desktop_menu[item]
                if isinstance(desktop_item, dict):
                    item_analysis["desktop_enabled"] = desktop_item.get("enabled", True)
            
            if item_analysis["mobile_present"]:
                mobile_item = mobile_menu[item]
                if isinstance(mobile_item, dict):
                    item_analysis["mobile_enabled"] = mobile_item.get("enabled", True)
            
            analysis[item] = item_analysis
        
        return analysis
    
    async def restore_original_settings(self):
        """Restore original menu settings"""
        if not self.admin_token or not self.original_menu_settings:
            return
        
        print("\n🔄 Restoring original menu settings...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            result = await self.make_request("/admin/menu-settings", "POST", data=self.original_menu_settings, headers=headers)
            if result["success"]:
                print("  ✅ Original menu settings restored successfully")
            else:
                print(f"  ⚠️ Failed to restore original settings: {result.get('error')}")
        except Exception as e:
            print(f"  ⚠️ Error restoring original settings: {e}")
    
    async def run_complete_workflow_test(self) -> Dict:
        """Run the complete menu settings workflow test"""
        print("🚀 Starting Menu Settings Admin Workflow Testing")
        print("=" * 80)
        print("FOCUS: Testing data flow issue where items marked as 'hidden' still show up")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate users
            admin_auth = await self.authenticate_admin()
            if not admin_auth:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Admin authentication failed - cannot proceed with tests"
                }
            
            # Run the workflow steps
            step1_result = await self.step1_get_current_admin_menu_settings()
            if not step1_result["success"]:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Failed to get admin menu settings",
                    "step1_result": step1_result
                }
            
            step2_result = await self.step2_disable_menu_item("browse")
            if not step2_result["success"]:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Failed to disable menu item",
                    "step1_result": step1_result,
                    "step2_result": step2_result
                }
            
            step3_result = await self.step3_check_user_menu_response()
            if not step3_result["success"]:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Failed to get user menu settings",
                    "step1_result": step1_result,
                    "step2_result": step2_result,
                    "step3_result": step3_result
                }
            
            step4_result = await self.step4_verify_data_structure_consistency(
                step1_result["full_data"], 
                step3_result["full_data"]
            )
            
            # Restore original settings
            await self.restore_original_settings()
            
            # Compile final analysis
            workflow_results = {
                "test_timestamp": datetime.now().isoformat(),
                "step1_admin_menu_get": step1_result,
                "step2_disable_item": step2_result,
                "step3_user_menu_get": step3_result,
                "step4_consistency_check": step4_result
            }
            
            # Determine root cause
            root_cause_analysis = self.determine_root_cause(step1_result, step2_result, step3_result, step4_result)
            workflow_results["root_cause_analysis"] = root_cause_analysis
            
            # Overall success
            all_steps_successful = all([
                step1_result["success"],
                step2_result["success"], 
                step3_result["success"],
                step4_result["success"]
            ])
            
            workflow_results["summary"] = {
                "all_steps_successful": all_steps_successful,
                "workflow_working_correctly": step4_result["success"],
                "root_cause_identified": root_cause_analysis["issue_identified"],
                "issue_description": root_cause_analysis["issue_description"],
                "recommended_fix": root_cause_analysis["recommended_fix"]
            }
            
            return workflow_results
            
        finally:
            await self.cleanup()
    
    def determine_root_cause(self, step1: Dict, step2: Dict, step3: Dict, step4: Dict) -> Dict:
        """Determine the root cause of the menu visibility issue"""
        analysis = {
            "issue_identified": False,
            "issue_description": "No issues detected",
            "recommended_fix": "No action needed",
            "technical_details": {}
        }
        
        consistency = step4.get("consistency_analysis", {})
        
        # Check for property mismatch
        if consistency.get("property_mismatch", False):
            analysis["issue_identified"] = True
            analysis["issue_description"] = "Property mismatch between admin and user APIs"
            analysis["recommended_fix"] = "Ensure both APIs use the same property names (enabled vs visible)"
            analysis["technical_details"]["property_mismatch"] = {
                "admin_uses_enabled": consistency.get("admin_uses_enabled"),
                "admin_uses_visible": consistency.get("admin_uses_visible"),
                "user_uses_enabled": consistency.get("user_uses_enabled"),
                "user_uses_visible": consistency.get("user_uses_visible")
            }
        
        # Check if disabled items are not being filtered
        elif not consistency.get("disabled_items_filtered", True):
            analysis["issue_identified"] = True
            analysis["issue_description"] = "Disabled items are not being filtered from user menu response"
            analysis["recommended_fix"] = "Fix user menu filtering logic to exclude items with enabled=false"
            analysis["technical_details"]["disabled_items_in_user"] = consistency.get("disabled_items_in_user", [])
        
        # Check if admin changes are not being saved
        elif not step2.get("verification_success", True):
            analysis["issue_identified"] = True
            analysis["issue_description"] = "Admin menu changes are not being saved to database"
            analysis["recommended_fix"] = "Fix admin menu settings POST endpoint to properly save changes"
            analysis["technical_details"]["save_verification"] = step2.get("verification_success")
        
        # Check for frontend implementation issues
        else:
            # If all backend tests pass, the issue might be in frontend
            analysis["issue_identified"] = True
            analysis["issue_description"] = "Backend APIs working correctly - issue likely in frontend isMenuItemVisible function"
            analysis["recommended_fix"] = "Check frontend isMenuItemVisible function implementation and ensure it reads the correct property"
            analysis["technical_details"]["backend_working"] = True
        
        return analysis


async def main():
    """Main test execution"""
    tester = MenuWorkflowTester()
    results = await tester.run_complete_workflow_test()
    
    print("\n" + "=" * 80)
    print("📊 MENU WORKFLOW TEST RESULTS")
    print("=" * 80)
    
    summary = results.get("summary", {})
    root_cause = results.get("root_cause_analysis", {})
    
    print(f"✅ All steps successful: {summary.get('all_steps_successful', False)}")
    print(f"🔧 Workflow working correctly: {summary.get('workflow_working_correctly', False)}")
    print(f"🔍 Root cause identified: {root_cause.get('issue_identified', False)}")
    
    if root_cause.get("issue_identified", False):
        print(f"\n🚨 ISSUE IDENTIFIED:")
        print(f"   Description: {root_cause.get('issue_description', 'Unknown')}")
        print(f"   Recommended Fix: {root_cause.get('recommended_fix', 'Unknown')}")
        
        technical_details = root_cause.get("technical_details", {})
        if technical_details:
            print(f"   Technical Details: {json.dumps(technical_details, indent=2)}")
    
    print(f"\n📄 Full results saved to test output")
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Save results to file for analysis
    with open("/app/menu_workflow_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to /app/menu_workflow_test_results.json")