#!/usr/bin/env python3
"""
Menu Settings Database Consistency Investigation
Testing all menu items marked as "Hidden" to find and fix database inconsistencies beyond Messages
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
ADMIN_PASSWORD = "admin_password"

class MenuConsistencyTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.admin_user_id = None
        
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
            self.admin_user_id = user_data.get("id")
            
            print(f"  ✅ Admin login successful")
            print(f"  👤 Admin ID: {self.admin_user_id}")
            print(f"  🔑 Token received: {bool(token)}")
            
            return {
                "success": True,
                "admin_id": self.admin_user_id,
                "token": token,
                "user_data": user_data
            }
        else:
            print(f"  ❌ Admin login failed: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error", "Login failed")
            }
    
    async def get_admin_menu_settings(self) -> Dict:
        """Get complete admin menu settings to identify all items marked as Hidden"""
        print("📋 Getting complete admin menu settings...")
        
        if not self.admin_token:
            return {"success": False, "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if result["success"]:
            menu_data = result["data"]
            desktop_menu = menu_data.get("desktop_menu", {})
            mobile_menu = menu_data.get("mobile_menu", {})
            
            print(f"  ✅ Admin menu settings retrieved")
            print(f"  📱 Desktop menu items: {len(desktop_menu)}")
            print(f"  📱 Mobile menu items: {len(mobile_menu)}")
            
            # Identify all items marked as Hidden (enabled: false)
            hidden_items = []
            
            # Check desktop menu for hidden items
            for item_key, item_config in desktop_menu.items():
                if not item_config.get("enabled", True):
                    hidden_items.append({
                        "item": item_key,
                        "menu_type": "desktop",
                        "enabled": item_config.get("enabled"),
                        "label": item_config.get("label", item_key),
                        "roles": item_config.get("roles", [])
                    })
            
            # Check mobile menu for hidden items
            for item_key, item_config in mobile_menu.items():
                if not item_config.get("enabled", True):
                    hidden_items.append({
                        "item": item_key,
                        "menu_type": "mobile", 
                        "enabled": item_config.get("enabled"),
                        "label": item_config.get("label", item_key),
                        "roles": item_config.get("roles", [])
                    })
            
            print(f"  🔍 Found {len(hidden_items)} items marked as Hidden:")
            for item in hidden_items:
                print(f"    - {item['item']} ({item['menu_type']}): {item['label']}")
            
            return {
                "success": True,
                "desktop_menu": desktop_menu,
                "mobile_menu": mobile_menu,
                "hidden_items": hidden_items,
                "total_hidden_items": len(hidden_items)
            }
        else:
            print(f"  ❌ Failed to get admin menu settings: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error", "Failed to get admin menu settings")
            }
    
    async def check_database_consistency(self, admin_menu_data: Dict) -> Dict:
        """Check for database inconsistencies across all disabled items"""
        print("🔍 Checking database consistency for all items...")
        
        desktop_menu = admin_menu_data.get("desktop_menu", {})
        mobile_menu = admin_menu_data.get("mobile_menu", {})
        
        inconsistencies = []
        consistent_items = []
        
        # Get all unique menu items
        all_items = set(desktop_menu.keys()) | set(mobile_menu.keys())
        
        print(f"  📊 Analyzing {len(all_items)} total menu items for consistency...")
        
        for item_key in all_items:
            desktop_config = desktop_menu.get(item_key, {})
            mobile_config = mobile_menu.get(item_key, {})
            
            desktop_enabled = desktop_config.get("enabled", True)
            mobile_enabled = mobile_config.get("enabled", True)
            
            # Check for inconsistencies
            if desktop_enabled != mobile_enabled:
                inconsistency = {
                    "item": item_key,
                    "label": desktop_config.get("label") or mobile_config.get("label", item_key),
                    "desktop_enabled": desktop_enabled,
                    "mobile_enabled": mobile_enabled,
                    "inconsistent": True,
                    "desktop_config": desktop_config,
                    "mobile_config": mobile_config
                }
                inconsistencies.append(inconsistency)
                
                print(f"    ❌ INCONSISTENCY: {item_key}")
                print(f"       Desktop enabled: {desktop_enabled}")
                print(f"       Mobile enabled: {mobile_enabled}")
            else:
                consistent_items.append({
                    "item": item_key,
                    "label": desktop_config.get("label") or mobile_config.get("label", item_key),
                    "desktop_enabled": desktop_enabled,
                    "mobile_enabled": mobile_enabled,
                    "consistent": True
                })
        
        print(f"  ✅ Consistent items: {len(consistent_items)}")
        print(f"  ❌ Inconsistent items: {len(inconsistencies)}")
        
        return {
            "success": True,
            "total_items_analyzed": len(all_items),
            "consistent_items": consistent_items,
            "inconsistent_items": inconsistencies,
            "inconsistency_count": len(inconsistencies),
            "consistency_rate": (len(consistent_items) / len(all_items)) * 100 if all_items else 100
        }
    
    async def check_user_api_response(self) -> Dict:
        """Check what disabled items are still being returned to users"""
        print("👤 Checking user API response for disabled items...")
        
        if not self.admin_user_id:
            return {"success": False, "error": "No admin user ID available"}
        
        result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
        
        if result["success"]:
            user_menu_data = result["data"]
            desktop_menu = user_menu_data.get("desktop_menu", {})
            mobile_menu = user_menu_data.get("mobile_menu", {})
            
            print(f"  ✅ User menu settings retrieved")
            print(f"  📱 Desktop menu items returned: {len(desktop_menu)}")
            print(f"  📱 Mobile menu items returned: {len(mobile_menu)}")
            
            # List all items returned to user
            desktop_items = list(desktop_menu.keys())
            mobile_items = list(mobile_menu.keys())
            
            print(f"  📋 Desktop items returned to user:")
            for item in desktop_items:
                print(f"    - {item}")
            
            print(f"  📋 Mobile items returned to user:")
            for item in mobile_items:
                print(f"    - {item}")
            
            return {
                "success": True,
                "desktop_menu": desktop_menu,
                "mobile_menu": mobile_menu,
                "desktop_items": desktop_items,
                "mobile_items": mobile_items,
                "total_desktop_items": len(desktop_items),
                "total_mobile_items": len(mobile_items)
            }
        else:
            print(f"  ❌ Failed to get user menu settings: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error", "Failed to get user menu settings")
            }
    
    async def identify_items_still_visible(self, admin_menu_data: Dict, user_menu_data: Dict) -> Dict:
        """Identify items that are marked as hidden but still appearing in user API response"""
        print("🔍 Identifying items marked as hidden but still visible to users...")
        
        desktop_admin = admin_menu_data.get("desktop_menu", {})
        mobile_admin = admin_menu_data.get("mobile_menu", {})
        
        desktop_user = user_menu_data.get("desktop_menu", {})
        mobile_user = user_menu_data.get("mobile_menu", {})
        
        problematic_items = []
        
        # Check desktop items
        for item_key in desktop_user.keys():
            admin_config = desktop_admin.get(item_key, {})
            if not admin_config.get("enabled", True):
                problematic_items.append({
                    "item": item_key,
                    "menu_type": "desktop",
                    "marked_as_hidden": True,
                    "still_visible_to_user": True,
                    "admin_enabled": admin_config.get("enabled"),
                    "label": admin_config.get("label", item_key)
                })
                print(f"    ❌ PROBLEM: {item_key} (desktop) - marked as hidden but still visible")
        
        # Check mobile items
        for item_key in mobile_user.keys():
            admin_config = mobile_admin.get(item_key, {})
            if not admin_config.get("enabled", True):
                problematic_items.append({
                    "item": item_key,
                    "menu_type": "mobile",
                    "marked_as_hidden": True,
                    "still_visible_to_user": True,
                    "admin_enabled": admin_config.get("enabled"),
                    "label": admin_config.get("label", item_key)
                })
                print(f"    ❌ PROBLEM: {item_key} (mobile) - marked as hidden but still visible")
        
        print(f"  📊 Found {len(problematic_items)} items marked as hidden but still visible to users")
        
        return {
            "success": True,
            "problematic_items": problematic_items,
            "problem_count": len(problematic_items)
        }
    
    async def fix_database_inconsistencies(self, inconsistent_items: List[Dict]) -> Dict:
        """Apply fixes for all inconsistent items found"""
        print("🔧 Fixing database inconsistencies...")
        
        if not self.admin_token:
            return {"success": False, "error": "No admin token available"}
        
        if not inconsistent_items:
            print("  ✅ No inconsistencies found to fix")
            return {"success": True, "fixes_applied": 0, "message": "No inconsistencies to fix"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        fixes_applied = []
        fix_errors = []
        
        for item in inconsistent_items:
            item_key = item["item"]
            desktop_enabled = item["desktop_enabled"]
            mobile_enabled = item["mobile_enabled"]
            
            print(f"  🔧 Fixing {item_key}...")
            print(f"     Current: desktop={desktop_enabled}, mobile={mobile_enabled}")
            
            # Determine the correct state (if either is disabled, both should be disabled)
            target_enabled = desktop_enabled and mobile_enabled
            
            # If either desktop or mobile is disabled, set both to disabled
            if not desktop_enabled or not mobile_enabled:
                target_enabled = False
            
            print(f"     Target: both={target_enabled}")
            
            # Prepare the fix data
            fix_data = {
                "menu_type": "both",  # Fix both desktop and mobile
                "item_key": item_key,
                "enabled": target_enabled
            }
            
            # Apply the fix
            fix_result = await self.make_request("/admin/menu-settings/fix-consistency", "POST", data=fix_data, headers=headers)
            
            if fix_result["success"]:
                fixes_applied.append({
                    "item": item_key,
                    "previous_desktop_enabled": desktop_enabled,
                    "previous_mobile_enabled": mobile_enabled,
                    "new_enabled": target_enabled,
                    "fix_successful": True
                })
                print(f"     ✅ Fixed {item_key} - set both to enabled={target_enabled}")
            else:
                # Try manual fix by updating the database directly
                manual_fix_data = {
                    "desktop_menu": {item_key: {"enabled": target_enabled}},
                    "mobile_menu": {item_key: {"enabled": target_enabled}}
                }
                
                manual_result = await self.make_request("/admin/menu-settings", "PUT", data=manual_fix_data, headers=headers)
                
                if manual_result["success"]:
                    fixes_applied.append({
                        "item": item_key,
                        "previous_desktop_enabled": desktop_enabled,
                        "previous_mobile_enabled": mobile_enabled,
                        "new_enabled": target_enabled,
                        "fix_successful": True,
                        "method": "manual"
                    })
                    print(f"     ✅ Manually fixed {item_key} - set both to enabled={target_enabled}")
                else:
                    fix_errors.append({
                        "item": item_key,
                        "error": manual_result.get("error", "Fix failed"),
                        "fix_successful": False
                    })
                    print(f"     ❌ Failed to fix {item_key}: {manual_result.get('error')}")
        
        print(f"  📊 Applied {len(fixes_applied)} fixes, {len(fix_errors)} errors")
        
        return {
            "success": True,
            "fixes_applied": len(fixes_applied),
            "fix_errors": len(fix_errors),
            "detailed_fixes": fixes_applied,
            "detailed_errors": fix_errors
        }
    
    async def verify_fixes(self) -> Dict:
        """Verify that all fixes have been applied correctly"""
        print("✅ Verifying fixes have been applied correctly...")
        
        # Re-check admin menu settings
        admin_check = await self.get_admin_menu_settings()
        if not admin_check["success"]:
            return {"success": False, "error": "Failed to verify admin menu settings"}
        
        # Re-check database consistency
        consistency_check = await self.check_database_consistency(admin_check)
        if not consistency_check["success"]:
            return {"success": False, "error": "Failed to verify database consistency"}
        
        # Re-check user API response
        user_check = await self.check_user_api_response()
        if not user_check["success"]:
            return {"success": False, "error": "Failed to verify user API response"}
        
        # Check if all hidden items are properly filtered from user API
        hidden_items = admin_check.get("hidden_items", [])
        user_desktop_items = user_check.get("desktop_items", [])
        user_mobile_items = user_check.get("mobile_items", [])
        
        still_problematic = []
        
        for hidden_item in hidden_items:
            item_key = hidden_item["item"]
            menu_type = hidden_item["menu_type"]
            
            if menu_type == "desktop" and item_key in user_desktop_items:
                still_problematic.append({
                    "item": item_key,
                    "menu_type": "desktop",
                    "still_visible": True
                })
            elif menu_type == "mobile" and item_key in user_mobile_items:
                still_problematic.append({
                    "item": item_key,
                    "menu_type": "mobile", 
                    "still_visible": True
                })
        
        verification_successful = len(still_problematic) == 0 and consistency_check.get("inconsistency_count", 0) == 0
        
        print(f"  📊 Verification results:")
        print(f"     Database inconsistencies remaining: {consistency_check.get('inconsistency_count', 0)}")
        print(f"     Items still problematically visible: {len(still_problematic)}")
        print(f"     Overall verification: {'✅ PASSED' if verification_successful else '❌ FAILED'}")
        
        return {
            "success": True,
            "verification_passed": verification_successful,
            "remaining_inconsistencies": consistency_check.get("inconsistency_count", 0),
            "still_problematic_items": still_problematic,
            "consistency_rate": consistency_check.get("consistency_rate", 0),
            "admin_menu_check": admin_check,
            "consistency_check": consistency_check,
            "user_api_check": user_check
        }
    
    async def run_comprehensive_investigation(self) -> Dict:
        """Run complete investigation and fix process"""
        print("🚀 Starting Menu Settings Database Consistency Investigation")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Step 1: Authenticate as admin
            auth_result = await self.authenticate_admin()
            if not auth_result["success"]:
                return {"error": "Failed to authenticate as admin", "details": auth_result}
            
            # Step 2: Get complete admin menu settings
            admin_menu_result = await self.get_admin_menu_settings()
            if not admin_menu_result["success"]:
                return {"error": "Failed to get admin menu settings", "details": admin_menu_result}
            
            # Step 3: Check database consistency for all items
            consistency_result = await self.check_database_consistency(admin_menu_result)
            if not consistency_result["success"]:
                return {"error": "Failed to check database consistency", "details": consistency_result}
            
            # Step 4: Check user API response
            user_api_result = await self.check_user_api_response()
            if not user_api_result["success"]:
                return {"error": "Failed to check user API response", "details": user_api_result}
            
            # Step 5: Identify items still visible despite being hidden
            visibility_result = await self.identify_items_still_visible(admin_menu_result, user_api_result)
            if not visibility_result["success"]:
                return {"error": "Failed to identify visibility issues", "details": visibility_result}
            
            # Step 6: Fix database inconsistencies
            inconsistent_items = consistency_result.get("inconsistent_items", [])
            fix_result = await self.fix_database_inconsistencies(inconsistent_items)
            if not fix_result["success"]:
                return {"error": "Failed to fix database inconsistencies", "details": fix_result}
            
            # Step 7: Verify fixes
            verification_result = await self.verify_fixes()
            if not verification_result["success"]:
                return {"error": "Failed to verify fixes", "details": verification_result}
            
            # Compile comprehensive results
            investigation_results = {
                "test_timestamp": datetime.now().isoformat(),
                "investigation_successful": True,
                "authentication": auth_result,
                "admin_menu_analysis": admin_menu_result,
                "database_consistency_check": consistency_result,
                "user_api_analysis": user_api_result,
                "visibility_issues": visibility_result,
                "database_fixes": fix_result,
                "verification": verification_result
            }
            
            # Summary statistics
            investigation_results["summary"] = {
                "total_menu_items_analyzed": consistency_result.get("total_items_analyzed", 0),
                "items_marked_as_hidden": admin_menu_result.get("total_hidden_items", 0),
                "database_inconsistencies_found": consistency_result.get("inconsistency_count", 0),
                "items_still_visible_despite_hidden": visibility_result.get("problem_count", 0),
                "fixes_applied": fix_result.get("fixes_applied", 0),
                "fix_errors": fix_result.get("fix_errors", 0),
                "verification_passed": verification_result.get("verification_passed", False),
                "final_consistency_rate": verification_result.get("consistency_rate", 0),
                "investigation_complete": True
            }
            
            return investigation_results
            
        finally:
            await self.cleanup()

async def main():
    """Run the menu consistency investigation"""
    tester = MenuConsistencyTester()
    results = await tester.run_comprehensive_investigation()
    
    print("\n" + "=" * 70)
    print("📊 INVESTIGATION RESULTS SUMMARY")
    print("=" * 70)
    
    if "error" in results:
        print(f"❌ Investigation failed: {results['error']}")
        return
    
    summary = results.get("summary", {})
    
    print(f"📋 Total menu items analyzed: {summary.get('total_menu_items_analyzed', 0)}")
    print(f"🔍 Items marked as Hidden: {summary.get('items_marked_as_hidden', 0)}")
    print(f"❌ Database inconsistencies found: {summary.get('database_inconsistencies_found', 0)}")
    print(f"👁️ Items still visible despite being hidden: {summary.get('items_still_visible_despite_hidden', 0)}")
    print(f"🔧 Fixes applied: {summary.get('fixes_applied', 0)}")
    print(f"⚠️ Fix errors: {summary.get('fix_errors', 0)}")
    print(f"✅ Verification passed: {summary.get('verification_passed', False)}")
    print(f"📊 Final consistency rate: {summary.get('final_consistency_rate', 0):.1f}%")
    
    if summary.get("verification_passed", False):
        print("\n🎉 ALL MENU ITEMS DATABASE INCONSISTENCIES HAVE BEEN RESOLVED!")
    else:
        print("\n⚠️ Some issues may still remain - check detailed results")
    
    # Save detailed results to file
    with open("/app/menu_consistency_investigation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/menu_consistency_investigation_results.json")

if __name__ == "__main__":
    asyncio.run(main())