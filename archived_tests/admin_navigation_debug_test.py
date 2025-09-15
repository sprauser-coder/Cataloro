#!/usr/bin/env python3
"""
URGENT: Admin Navigation Visibility Debug Test
Testing admin user navigation visibility issue - admin can't see any menu items
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://nginx-config-fix.preview.emergentagent.com/api"

# Admin User Configuration (from review request)
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

class AdminNavigationDebugTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.admin_user_data = None
        
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
    
    async def test_admin_authentication_check(self) -> Dict:
        """Test 1: Admin Authentication Check - verify admin can login and get proper JWT token"""
        print("🔐 TESTING: Admin Authentication Check")
        print("=" * 50)
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            token = result["data"].get("token", "")
            
            # Store for subsequent tests
            self.admin_token = token
            self.admin_user_data = user_data
            
            # Analyze JWT token structure
            token_parts = token.split('.') if token else []
            token_valid_structure = len(token_parts) == 3
            
            # Check user role information
            user_role = user_data.get("user_role", "")
            legacy_role = user_data.get("role", "")
            user_id = user_data.get("id", "")
            email = user_data.get("email", "")
            
            print(f"✅ Admin login successful")
            print(f"📧 Email: {email}")
            print(f"🆔 User ID: {user_id}")
            print(f"🔑 User Role: {user_role}")
            print(f"🔑 Legacy Role: {legacy_role}")
            print(f"🎫 JWT Token: {'Valid structure' if token_valid_structure else 'Invalid structure'}")
            print(f"⏱️ Response time: {result['response_time_ms']:.2f}ms")
            
            return {
                "test_name": "Admin Authentication Check",
                "success": True,
                "login_successful": True,
                "user_id": user_id,
                "email": email,
                "user_role": user_role,
                "legacy_role": legacy_role,
                "token_received": bool(token),
                "token_valid_structure": token_valid_structure,
                "response_time_ms": result["response_time_ms"],
                "user_data": user_data
            }
        else:
            print(f"❌ Admin login failed: {result.get('error', 'Unknown error')}")
            print(f"📊 Status: {result['status']}")
            
            return {
                "test_name": "Admin Authentication Check",
                "success": False,
                "login_successful": False,
                "error": result.get("error", "Login failed"),
                "status": result["status"],
                "response_time_ms": result["response_time_ms"]
            }
    
    async def test_admin_menu_settings_api(self) -> Dict:
        """Test 2: Admin Menu Settings API - check current admin menu configuration"""
        print("\n⚙️ TESTING: Admin Menu Settings API")
        print("=" * 50)
        
        if not self.admin_token:
            return {"test_name": "Admin Menu Settings API", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if result["success"]:
            data = result["data"]
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            
            # Analyze menu configuration
            desktop_items = []
            mobile_items = []
            disabled_items = []
            admin_items = []
            
            # Process desktop menu
            for key, item in desktop_menu.items():
                if isinstance(item, dict):
                    desktop_items.append({
                        "key": key,
                        "enabled": item.get("enabled", False),
                        "roles": item.get("roles", []),
                        "label": item.get("label", key)
                    })
                    
                    if not item.get("enabled", False):
                        disabled_items.append(f"desktop_{key}")
                    
                    if "admin" in item.get("roles", []):
                        admin_items.append(f"desktop_{key}")
            
            # Process mobile menu
            for key, item in mobile_menu.items():
                if isinstance(item, dict):
                    mobile_items.append({
                        "key": key,
                        "enabled": item.get("enabled", False),
                        "roles": item.get("roles", []),
                        "label": item.get("label", key)
                    })
                    
                    if not item.get("enabled", False):
                        disabled_items.append(f"mobile_{key}")
                    
                    if "admin" in item.get("roles", []):
                        admin_items.append(f"mobile_{key}")
            
            print(f"✅ Admin menu settings retrieved")
            print(f"🖥️ Desktop menu items: {len(desktop_items)}")
            print(f"📱 Mobile menu items: {len(mobile_items)}")
            print(f"❌ Disabled items: {len(disabled_items)}")
            print(f"👑 Admin-accessible items: {len(admin_items)}")
            print(f"⏱️ Response time: {result['response_time_ms']:.2f}ms")
            
            # Show disabled items
            if disabled_items:
                print(f"\n🚫 DISABLED ITEMS:")
                for item in disabled_items[:10]:  # Show first 10
                    print(f"   - {item}")
                if len(disabled_items) > 10:
                    print(f"   ... and {len(disabled_items) - 10} more")
            
            # Show admin items
            if admin_items:
                print(f"\n👑 ADMIN ITEMS:")
                for item in admin_items[:10]:  # Show first 10
                    print(f"   - {item}")
            
            return {
                "test_name": "Admin Menu Settings API",
                "success": True,
                "desktop_items_count": len(desktop_items),
                "mobile_items_count": len(mobile_items),
                "disabled_items_count": len(disabled_items),
                "admin_items_count": len(admin_items),
                "disabled_items": disabled_items,
                "admin_items": admin_items,
                "desktop_items": desktop_items,
                "mobile_items": mobile_items,
                "response_time_ms": result["response_time_ms"],
                "raw_data": data
            }
        else:
            print(f"❌ Admin menu settings failed: {result.get('error')}")
            print(f"📊 Status: {result['status']}")
            
            return {
                "test_name": "Admin Menu Settings API",
                "success": False,
                "error": result.get("error"),
                "status": result["status"],
                "response_time_ms": result["response_time_ms"]
            }
    
    async def test_user_menu_settings_for_admin(self) -> Dict:
        """Test 3: User Menu Settings for Admin - check what admin user receives in filtered menu"""
        print("\n👤 TESTING: User Menu Settings for Admin")
        print("=" * 50)
        
        if not self.admin_user_data:
            return {"test_name": "User Menu Settings for Admin", "error": "No admin user data available"}
        
        admin_user_id = self.admin_user_data.get("id")
        if not admin_user_id:
            return {"test_name": "User Menu Settings for Admin", "error": "No admin user ID available"}
        
        result = await self.make_request(f"/menu-settings/user/{admin_user_id}")
        
        if result["success"]:
            data = result["data"]
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            user_role = data.get("user_role", "")
            
            # Analyze what admin receives
            desktop_items = []
            mobile_items = []
            
            # Process desktop menu items
            for key, item in desktop_menu.items():
                if isinstance(item, dict) and item.get("enabled", False):
                    desktop_items.append({
                        "key": key,
                        "label": item.get("label", key),
                        "roles": item.get("roles", [])
                    })
            
            # Process mobile menu items
            for key, item in mobile_menu.items():
                if isinstance(item, dict) and item.get("enabled", False):
                    mobile_items.append({
                        "key": key,
                        "label": item.get("label", key),
                        "roles": item.get("roles", [])
                    })
            
            print(f"✅ User menu settings retrieved for admin")
            print(f"👤 User Role: {user_role}")
            print(f"🆔 User ID: {admin_user_id}")
            print(f"🖥️ Desktop items received: {len(desktop_items)}")
            print(f"📱 Mobile items received: {len(mobile_items)}")
            print(f"⏱️ Response time: {result['response_time_ms']:.2f}ms")
            
            # Show items received
            if desktop_items:
                print(f"\n🖥️ DESKTOP ITEMS RECEIVED:")
                for item in desktop_items:
                    print(f"   - {item['key']}: {item['label']}")
            else:
                print(f"\n🚫 NO DESKTOP ITEMS RECEIVED!")
            
            if mobile_items:
                print(f"\n📱 MOBILE ITEMS RECEIVED:")
                for item in mobile_items:
                    print(f"   - {item['key']}: {item['label']}")
            else:
                print(f"\n🚫 NO MOBILE ITEMS RECEIVED!")
            
            return {
                "test_name": "User Menu Settings for Admin",
                "success": True,
                "user_role": user_role,
                "user_id": admin_user_id,
                "desktop_items_count": len(desktop_items),
                "mobile_items_count": len(mobile_items),
                "desktop_items": desktop_items,
                "mobile_items": mobile_items,
                "total_items_received": len(desktop_items) + len(mobile_items),
                "no_items_received": len(desktop_items) == 0 and len(mobile_items) == 0,
                "response_time_ms": result["response_time_ms"],
                "raw_data": data
            }
        else:
            print(f"❌ User menu settings failed: {result.get('error')}")
            print(f"📊 Status: {result['status']}")
            
            return {
                "test_name": "User Menu Settings for Admin",
                "success": False,
                "error": result.get("error"),
                "status": result["status"],
                "response_time_ms": result["response_time_ms"]
            }
    
    async def test_database_state_investigation(self) -> Dict:
        """Test 4: Database State Investigation - check current menu settings in database"""
        print("\n🗄️ TESTING: Database State Investigation")
        print("=" * 50)
        
        if not self.admin_token:
            return {"test_name": "Database State Investigation", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get raw admin menu settings to investigate database state
        admin_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not admin_result["success"]:
            return {
                "test_name": "Database State Investigation",
                "success": False,
                "error": "Could not retrieve admin menu settings"
            }
        
        admin_data = admin_result["data"]
        
        # Analyze database state
        analysis = {
            "total_desktop_items": 0,
            "total_mobile_items": 0,
            "enabled_desktop_items": 0,
            "enabled_mobile_items": 0,
            "disabled_desktop_items": 0,
            "disabled_mobile_items": 0,
            "admin_accessible_desktop": 0,
            "admin_accessible_mobile": 0,
            "inconsistent_items": [],
            "all_disabled": False
        }
        
        # Analyze desktop menu
        desktop_menu = admin_data.get("desktop_menu", {})
        for key, item in desktop_menu.items():
            if isinstance(item, dict):
                analysis["total_desktop_items"] += 1
                
                enabled = item.get("enabled", False)
                roles = item.get("roles", [])
                
                if enabled:
                    analysis["enabled_desktop_items"] += 1
                else:
                    analysis["disabled_desktop_items"] += 1
                
                if "admin" in roles:
                    analysis["admin_accessible_desktop"] += 1
        
        # Analyze mobile menu
        mobile_menu = admin_data.get("mobile_menu", {})
        for key, item in mobile_menu.items():
            if isinstance(item, dict):
                analysis["total_mobile_items"] += 1
                
                enabled = item.get("enabled", False)
                roles = item.get("roles", [])
                
                if enabled:
                    analysis["enabled_mobile_items"] += 1
                else:
                    analysis["disabled_mobile_items"] += 1
                
                if "admin" in roles:
                    analysis["admin_accessible_mobile"] += 1
        
        # Check for data corruption or inconsistencies
        for key in desktop_menu.keys():
            if key in mobile_menu:
                desktop_item = desktop_menu[key]
                mobile_item = mobile_menu[key]
                
                if isinstance(desktop_item, dict) and isinstance(mobile_item, dict):
                    desktop_enabled = desktop_item.get("enabled", False)
                    mobile_enabled = mobile_item.get("enabled", False)
                    
                    if desktop_enabled != mobile_enabled:
                        analysis["inconsistent_items"].append({
                            "item": key,
                            "desktop_enabled": desktop_enabled,
                            "mobile_enabled": mobile_enabled
                        })
        
        # Check if all admin navigation items are disabled
        analysis["all_disabled"] = (
            analysis["enabled_desktop_items"] == 0 and 
            analysis["enabled_mobile_items"] == 0
        )
        
        print(f"✅ Database state analysis completed")
        print(f"🖥️ Desktop: {analysis['enabled_desktop_items']}/{analysis['total_desktop_items']} enabled")
        print(f"📱 Mobile: {analysis['enabled_mobile_items']}/{analysis['total_mobile_items']} enabled")
        print(f"👑 Admin accessible desktop: {analysis['admin_accessible_desktop']}")
        print(f"👑 Admin accessible mobile: {analysis['admin_accessible_mobile']}")
        print(f"⚠️ Inconsistent items: {len(analysis['inconsistent_items'])}")
        print(f"🚫 All items disabled: {analysis['all_disabled']}")
        
        if analysis["inconsistent_items"]:
            print(f"\n⚠️ INCONSISTENT ITEMS:")
            for item in analysis["inconsistent_items"]:
                print(f"   - {item['item']}: desktop={item['desktop_enabled']}, mobile={item['mobile_enabled']}")
        
        if analysis["all_disabled"]:
            print(f"\n🚨 CRITICAL: ALL MENU ITEMS ARE DISABLED!")
            print(f"   This explains why admin can't see any navigation items.")
        
        return {
            "test_name": "Database State Investigation",
            "success": True,
            "analysis": analysis,
            "response_time_ms": admin_result["response_time_ms"],
            "critical_issue_found": analysis["all_disabled"],
            "inconsistencies_found": len(analysis["inconsistent_items"]) > 0
        }
    
    async def test_role_mapping_debug(self) -> Dict:
        """Test 5: Role Mapping Debug - test user role mapping for admin user"""
        print("\n🔄 TESTING: Role Mapping Debug")
        print("=" * 50)
        
        if not self.admin_user_data:
            return {"test_name": "Role Mapping Debug", "error": "No admin user data available"}
        
        # Analyze admin user role mapping
        user_role = self.admin_user_data.get("user_role", "")
        legacy_role = self.admin_user_data.get("role", "")
        email = self.admin_user_data.get("email", "")
        user_id = self.admin_user_data.get("id", "")
        
        # Test role mapping logic
        role_mapping_tests = {
            "user_role_is_admin": user_role in ["Admin", "Admin-Manager"],
            "legacy_role_is_admin": legacy_role == "admin",
            "email_is_admin": email == "admin@cataloro.com",
            "has_admin_privileges": (
                user_role in ["Admin", "Admin-Manager"] or 
                legacy_role == "admin"
            )
        }
        
        # Test with user menu settings to see role filtering
        if user_id:
            user_menu_result = await self.make_request(f"/menu-settings/user/{user_id}")
            
            if user_menu_result["success"]:
                user_menu_data = user_menu_result["data"]
                returned_user_role = user_menu_data.get("user_role", "")
                
                role_mapping_tests["user_menu_role_consistent"] = returned_user_role == user_role
                role_mapping_tests["user_menu_recognizes_admin"] = returned_user_role in ["Admin", "Admin-Manager"]
            else:
                role_mapping_tests["user_menu_accessible"] = False
        
        print(f"✅ Role mapping analysis completed")
        print(f"👤 User Role: {user_role}")
        print(f"🔑 Legacy Role: {legacy_role}")
        print(f"📧 Email: {email}")
        print(f"🆔 User ID: {user_id}")
        
        print(f"\n🔍 ROLE MAPPING TESTS:")
        for test_name, result in role_mapping_tests.items():
            status = "✅" if result else "❌"
            print(f"   {status} {test_name}: {result}")
        
        # Determine if role mapping is working
        role_mapping_working = (
            role_mapping_tests.get("user_role_is_admin", False) and
            role_mapping_tests.get("has_admin_privileges", False)
        )
        
        if not role_mapping_working:
            print(f"\n🚨 CRITICAL: Role mapping appears to be broken!")
            print(f"   Admin user is not properly recognized as admin.")
        
        return {
            "test_name": "Role Mapping Debug",
            "success": True,
            "user_role": user_role,
            "legacy_role": legacy_role,
            "email": email,
            "user_id": user_id,
            "role_mapping_tests": role_mapping_tests,
            "role_mapping_working": role_mapping_working,
            "critical_issue_found": not role_mapping_working
        }
    
    async def run_admin_navigation_debug(self) -> Dict:
        """Run all admin navigation debug tests"""
        print("🚨 URGENT: Admin Navigation Visibility Debug Test")
        print("=" * 70)
        print("Testing why admin user can't see any menu items...")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all debug tests
            auth_test = await self.test_admin_authentication_check()
            menu_settings_test = await self.test_admin_menu_settings_api()
            user_menu_test = await self.test_user_menu_settings_for_admin()
            database_test = await self.test_database_state_investigation()
            role_mapping_test = await self.test_role_mapping_debug()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "admin_authentication_check": auth_test,
                "admin_menu_settings_api": menu_settings_test,
                "user_menu_settings_for_admin": user_menu_test,
                "database_state_investigation": database_test,
                "role_mapping_debug": role_mapping_test
            }
            
            # Analyze root cause
            root_cause_analysis = {
                "admin_login_working": auth_test.get("success", False),
                "admin_menu_api_working": menu_settings_test.get("success", False),
                "user_menu_api_working": user_menu_test.get("success", False),
                "admin_receives_no_items": user_menu_test.get("no_items_received", True),
                "all_items_disabled_in_db": database_test.get("critical_issue_found", False),
                "role_mapping_broken": role_mapping_test.get("critical_issue_found", False),
                "database_inconsistencies": database_test.get("inconsistencies_found", False)
            }
            
            # Determine most likely root cause
            likely_causes = []
            
            if root_cause_analysis["all_items_disabled_in_db"]:
                likely_causes.append("ALL_MENU_ITEMS_DISABLED")
            
            if root_cause_analysis["role_mapping_broken"]:
                likely_causes.append("ROLE_MAPPING_BROKEN")
            
            if root_cause_analysis["database_inconsistencies"]:
                likely_causes.append("DATABASE_INCONSISTENCIES")
            
            if not root_cause_analysis["admin_login_working"]:
                likely_causes.append("ADMIN_AUTHENTICATION_FAILED")
            
            if not likely_causes and root_cause_analysis["admin_receives_no_items"]:
                likely_causes.append("MENU_FILTERING_LOGIC_ISSUE")
            
            all_results["root_cause_analysis"] = {
                "analysis": root_cause_analysis,
                "likely_causes": likely_causes,
                "primary_cause": likely_causes[0] if likely_causes else "UNKNOWN",
                "issue_severity": "CRITICAL" if likely_causes else "UNKNOWN"
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Run the admin navigation debug test"""
    tester = AdminNavigationDebugTester()
    results = await tester.run_admin_navigation_debug()
    
    print("\n" + "=" * 70)
    print("🔍 ROOT CAUSE ANALYSIS SUMMARY")
    print("=" * 70)
    
    root_cause = results.get("root_cause_analysis", {})
    likely_causes = root_cause.get("likely_causes", [])
    primary_cause = root_cause.get("primary_cause", "UNKNOWN")
    
    print(f"🎯 Primary Cause: {primary_cause}")
    print(f"📋 All Likely Causes: {', '.join(likely_causes) if likely_causes else 'None identified'}")
    
    # Show specific recommendations
    if "ALL_MENU_ITEMS_DISABLED" in likely_causes:
        print(f"\n💡 RECOMMENDATION: All menu items are disabled in database.")
        print(f"   - Check menu_settings collection in MongoDB")
        print(f"   - Enable required menu items for admin access")
        print(f"   - Ensure admin_panel and admin_drawer are enabled")
    
    if "ROLE_MAPPING_BROKEN" in likely_causes:
        print(f"\n💡 RECOMMENDATION: Admin role mapping is not working.")
        print(f"   - Verify admin user has correct user_role field")
        print(f"   - Check backend role mapping logic")
        print(f"   - Ensure admin user is recognized as admin")
    
    if "DATABASE_INCONSISTENCIES" in likely_causes:
        print(f"\n💡 RECOMMENDATION: Database has inconsistent menu settings.")
        print(f"   - Fix inconsistent enabled values between desktop/mobile")
        print(f"   - Run database consistency check and repair")
    
    print(f"\n📊 Test completed at: {results.get('test_timestamp')}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())