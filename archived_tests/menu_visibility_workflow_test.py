#!/usr/bin/env python3
"""
Menu Visibility Workflow Test
Testing the specific workflow mentioned in the review request:
- Admin disables "Browse" menu item
- Verify it doesn't appear in user API response
- Test the exact scenario described in the review
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://mobileui-sync.preview.emergentagent.com/api"

# Test Users Configuration
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "demo@cataloro.com"

class MenuVisibilityWorkflowTester:
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
    
    async def test_browse_menu_visibility_workflow(self) -> Dict:
        """Test the complete Browse menu visibility workflow as described in review"""
        print("🔍 Testing Browse menu visibility workflow...")
        
        if not self.admin_token or not self.demo_user_id:
            return {"test_name": "Browse Menu Visibility Workflow", "error": "Missing authentication"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        workflow_results = {}
        
        # Step 1: Get initial state - check if Browse is visible for demo user
        print("  Step 1: Checking initial Browse visibility for demo user...")
        initial_demo_result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
        
        if initial_demo_result["success"]:
            initial_data = initial_demo_result["data"]
            initial_desktop_browse = initial_data.get("desktop_menu", {}).get("browse", {})
            initial_mobile_browse = initial_data.get("mobile_menu", {}).get("browse", {})
            
            workflow_results["initial_state"] = {
                "demo_has_desktop_browse": "browse" in initial_data.get("desktop_menu", {}),
                "demo_has_mobile_browse": "browse" in initial_data.get("mobile_menu", {}),
                "desktop_browse_enabled": initial_desktop_browse.get("enabled", False),
                "mobile_browse_enabled": initial_mobile_browse.get("enabled", False),
                "desktop_browse_data": initial_desktop_browse,
                "mobile_browse_data": initial_mobile_browse
            }
            
            print(f"    📊 Demo user initially has desktop Browse: {workflow_results['initial_state']['demo_has_desktop_browse']}")
            print(f"    📊 Demo user initially has mobile Browse: {workflow_results['initial_state']['demo_has_mobile_browse']}")
            print(f"    📊 Desktop Browse enabled: {workflow_results['initial_state']['desktop_browse_enabled']}")
            print(f"    📊 Mobile Browse enabled: {workflow_results['initial_state']['mobile_browse_enabled']}")
        else:
            workflow_results["initial_state"] = {"error": "Failed to get initial demo user menu"}
        
        # Step 2: Get current admin menu settings and backup
        print("  Step 2: Getting current admin menu settings...")
        admin_settings_result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if not admin_settings_result["success"]:
            return {
                "test_name": "Browse Menu Visibility Workflow",
                "success": False,
                "error": "Failed to get admin menu settings"
            }
        
        self.original_menu_settings = admin_settings_result["data"]
        current_settings = admin_settings_result["data"]
        
        workflow_results["admin_settings"] = {
            "desktop_browse_exists": "browse" in current_settings.get("desktop_menu", {}),
            "mobile_browse_exists": "browse" in current_settings.get("mobile_menu", {}),
            "desktop_browse_enabled": current_settings.get("desktop_menu", {}).get("browse", {}).get("enabled", False),
            "mobile_browse_enabled": current_settings.get("mobile_menu", {}).get("browse", {}).get("enabled", False)
        }
        
        print(f"    📊 Admin settings - Desktop Browse enabled: {workflow_results['admin_settings']['desktop_browse_enabled']}")
        print(f"    📊 Admin settings - Mobile Browse enabled: {workflow_results['admin_settings']['mobile_browse_enabled']}")
        
        # Step 3: Disable Browse menu item in admin settings
        print("  Step 3: Disabling Browse menu item via admin API...")
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
        
        workflow_results["disable_operation"] = {
            "success": disable_result["success"],
            "response_time_ms": disable_result.get("response_time_ms", 0),
            "error": disable_result.get("error") if not disable_result["success"] else None
        }
        
        print(f"    📊 Browse disable operation successful: {workflow_results['disable_operation']['success']}")
        
        if not disable_result["success"]:
            return {
                "test_name": "Browse Menu Visibility Workflow",
                "success": False,
                "error": f"Failed to disable Browse: {disable_result.get('error')}",
                "workflow_results": workflow_results
            }
        
        # Step 4: Verify admin settings were updated
        print("  Step 4: Verifying admin settings were updated...")
        verify_admin_result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if verify_admin_result["success"]:
            verify_data = verify_admin_result["data"]
            workflow_results["admin_verification"] = {
                "desktop_browse_disabled": verify_data.get("desktop_menu", {}).get("browse", {}).get("enabled") == False,
                "mobile_browse_disabled": verify_data.get("mobile_menu", {}).get("browse", {}).get("enabled") == False,
                "desktop_browse_data": verify_data.get("desktop_menu", {}).get("browse", {}),
                "mobile_browse_data": verify_data.get("mobile_menu", {}).get("browse", {})
            }
            
            print(f"    📊 Admin verification - Desktop Browse disabled: {workflow_results['admin_verification']['desktop_browse_disabled']}")
            print(f"    📊 Admin verification - Mobile Browse disabled: {workflow_results['admin_verification']['mobile_browse_disabled']}")
        else:
            workflow_results["admin_verification"] = {"error": "Failed to verify admin settings"}
        
        # Step 5: Test user API to see if Browse is filtered out
        print("  Step 5: Testing user API after Browse disable...")
        
        # Test demo user
        demo_after_disable = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
        
        # Test admin user
        admin_after_disable = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
        
        if demo_after_disable["success"]:
            demo_data = demo_after_disable["data"]
            workflow_results["demo_user_after_disable"] = {
                "has_desktop_browse": "browse" in demo_data.get("desktop_menu", {}),
                "has_mobile_browse": "browse" in demo_data.get("mobile_menu", {}),
                "desktop_browse_enabled": demo_data.get("desktop_menu", {}).get("browse", {}).get("enabled", False),
                "mobile_browse_enabled": demo_data.get("mobile_menu", {}).get("browse", {}).get("enabled", False),
                "total_desktop_items": len(demo_data.get("desktop_menu", {})),
                "total_mobile_items": len(demo_data.get("mobile_menu", {})),
                "desktop_items": list(demo_data.get("desktop_menu", {}).keys()),
                "mobile_items": list(demo_data.get("mobile_menu", {}).keys())
            }
            
            print(f"    📊 Demo user after disable - Has desktop Browse: {workflow_results['demo_user_after_disable']['has_desktop_browse']}")
            print(f"    📊 Demo user after disable - Has mobile Browse: {workflow_results['demo_user_after_disable']['has_mobile_browse']}")
            print(f"    📊 Demo user after disable - Desktop items: {workflow_results['demo_user_after_disable']['desktop_items']}")
            print(f"    📊 Demo user after disable - Mobile items: {workflow_results['demo_user_after_disable']['mobile_items']}")
        else:
            workflow_results["demo_user_after_disable"] = {"error": "Failed to get demo user menu after disable"}
        
        if admin_after_disable["success"]:
            admin_data = admin_after_disable["data"]
            workflow_results["admin_user_after_disable"] = {
                "has_desktop_browse": "browse" in admin_data.get("desktop_menu", {}),
                "has_mobile_browse": "browse" in admin_data.get("mobile_menu", {}),
                "desktop_browse_enabled": admin_data.get("desktop_menu", {}).get("browse", {}).get("enabled", False),
                "mobile_browse_enabled": admin_data.get("mobile_menu", {}).get("browse", {}).get("enabled", False),
                "total_desktop_items": len(admin_data.get("desktop_menu", {})),
                "total_mobile_items": len(admin_data.get("mobile_menu", {}))
            }
            
            print(f"    📊 Admin user after disable - Has desktop Browse: {workflow_results['admin_user_after_disable']['has_desktop_browse']}")
            print(f"    📊 Admin user after disable - Has mobile Browse: {workflow_results['admin_user_after_disable']['has_mobile_browse']}")
        else:
            workflow_results["admin_user_after_disable"] = {"error": "Failed to get admin user menu after disable"}
        
        # Step 6: Restore original settings
        print("  Step 6: Restoring original settings...")
        if self.original_menu_settings:
            restore_result = await self.make_request("/admin/menu-settings", "POST", data=self.original_menu_settings, headers=headers)
            workflow_results["restore_operation"] = {
                "success": restore_result["success"],
                "error": restore_result.get("error") if not restore_result["success"] else None
            }
            print(f"    📊 Settings restored successfully: {workflow_results['restore_operation']['success']}")
        
        # Step 7: Analyze results
        print("  Step 7: Analyzing workflow results...")
        
        # Check if filtering is working correctly
        demo_browse_filtered = not workflow_results.get("demo_user_after_disable", {}).get("has_desktop_browse", True)
        admin_browse_filtered = not workflow_results.get("admin_user_after_disable", {}).get("has_desktop_browse", True)
        
        # The key question: Are disabled items completely filtered out, or returned with enabled=false?
        demo_browse_completely_filtered = not workflow_results.get("demo_user_after_disable", {}).get("has_desktop_browse", True)
        admin_browse_completely_filtered = not workflow_results.get("admin_user_after_disable", {}).get("has_desktop_browse", True)
        
        workflow_success = demo_browse_filtered and admin_browse_filtered
        
        workflow_results["analysis"] = {
            "demo_browse_filtered_correctly": demo_browse_filtered,
            "admin_browse_filtered_correctly": admin_browse_filtered,
            "disabled_items_completely_filtered": demo_browse_completely_filtered and admin_browse_completely_filtered,
            "backend_filtering_working": workflow_success,
            "workflow_success": workflow_success
        }
        
        print(f"    📊 Demo Browse filtered correctly: {workflow_results['analysis']['demo_browse_filtered_correctly']}")
        print(f"    📊 Admin Browse filtered correctly: {workflow_results['analysis']['admin_browse_filtered_correctly']}")
        print(f"    📊 Disabled items completely filtered: {workflow_results['analysis']['disabled_items_completely_filtered']}")
        print(f"    📊 Backend filtering working: {workflow_results['analysis']['backend_filtering_working']}")
        
        return {
            "test_name": "Browse Menu Visibility Workflow",
            "success": workflow_success,
            "workflow_results": workflow_results
        }
    
    async def test_menu_item_properties_analysis(self) -> Dict:
        """Analyze what exact properties each menu item has"""
        print("🔬 Analyzing menu item properties...")
        
        if not self.demo_user_id:
            return {"test_name": "Menu Item Properties Analysis", "error": "No demo user ID"}
        
        result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
        
        if result["success"]:
            data = result["data"]
            
            # Analyze all menu items
            all_items_analysis = []
            
            # Desktop menu items
            desktop_menu = data.get("desktop_menu", {})
            for item_key, item_data in desktop_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    all_items_analysis.append({
                        "menu_type": "desktop",
                        "item_key": item_key,
                        "all_properties": list(item_data.keys()),
                        "enabled": item_data.get("enabled"),
                        "visible": item_data.get("visible"),
                        "disabled": item_data.get("disabled"),
                        "label": item_data.get("label"),
                        "roles": item_data.get("roles"),
                        "raw_data": item_data
                    })
            
            # Mobile menu items
            mobile_menu = data.get("mobile_menu", {})
            for item_key, item_data in mobile_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    all_items_analysis.append({
                        "menu_type": "mobile",
                        "item_key": item_key,
                        "all_properties": list(item_data.keys()),
                        "enabled": item_data.get("enabled"),
                        "visible": item_data.get("visible"),
                        "disabled": item_data.get("disabled"),
                        "label": item_data.get("label"),
                        "roles": item_data.get("roles"),
                        "raw_data": item_data
                    })
            
            # Property usage statistics
            property_stats = {
                "total_items": len(all_items_analysis),
                "items_with_enabled": sum(1 for item in all_items_analysis if "enabled" in item["all_properties"]),
                "items_with_visible": sum(1 for item in all_items_analysis if "visible" in item["all_properties"]),
                "items_with_disabled": sum(1 for item in all_items_analysis if "disabled" in item["all_properties"]),
                "enabled_true_count": sum(1 for item in all_items_analysis if item["enabled"] == True),
                "enabled_false_count": sum(1 for item in all_items_analysis if item["enabled"] == False),
                "enabled_null_count": sum(1 for item in all_items_analysis if item["enabled"] is None),
                "common_properties": []
            }
            
            # Find common properties
            if all_items_analysis:
                common_props = set(all_items_analysis[0]["all_properties"])
                for item in all_items_analysis[1:]:
                    common_props = common_props.intersection(set(item["all_properties"]))
                property_stats["common_properties"] = list(common_props)
            
            print(f"    📊 Total items analyzed: {property_stats['total_items']}")
            print(f"    📊 Items with 'enabled' property: {property_stats['items_with_enabled']}")
            print(f"    📊 Items with 'visible' property: {property_stats['items_with_visible']}")
            print(f"    📊 Items with 'disabled' property: {property_stats['items_with_disabled']}")
            print(f"    📊 Items with enabled=true: {property_stats['enabled_true_count']}")
            print(f"    📊 Items with enabled=false: {property_stats['enabled_false_count']}")
            print(f"    📊 Common properties: {property_stats['common_properties']}")
            
            return {
                "test_name": "Menu Item Properties Analysis",
                "success": True,
                "all_items_analysis": all_items_analysis,
                "property_stats": property_stats,
                "user_role": data.get("user_role"),
                "full_response": data
            }
        else:
            print(f"    ❌ Failed to analyze menu properties: {result.get('error')}")
            return {
                "test_name": "Menu Item Properties Analysis",
                "success": False,
                "error": result.get("error")
            }
    
    async def run_comprehensive_workflow_test(self) -> Dict:
        """Run the comprehensive workflow test as requested in review"""
        print("🚀 Starting Menu Visibility Workflow Test")
        print("=" * 70)
        print("TESTING: Exact scenario described in review request")
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
            
            # Run the main workflow test
            print("\n1. Testing Browse menu visibility workflow...")
            browse_workflow_test = await self.test_browse_menu_visibility_workflow()
            
            print("\n2. Analyzing menu item properties...")
            properties_analysis_test = await self.test_menu_item_properties_analysis()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Menu Visibility Workflow - Review Request Scenario",
                "browse_workflow_test": browse_workflow_test,
                "properties_analysis_test": properties_analysis_test
            }
            
            # Key findings
            workflow_success = browse_workflow_test.get("success", False)
            workflow_results = browse_workflow_test.get("workflow_results", {})
            analysis = workflow_results.get("analysis", {})
            
            key_findings = {
                "backend_api_filtering_works": analysis.get("backend_filtering_working", False),
                "disabled_items_completely_filtered": analysis.get("disabled_items_completely_filtered", False),
                "admin_can_disable_items": workflow_results.get("disable_operation", {}).get("success", False),
                "user_api_respects_admin_settings": analysis.get("demo_browse_filtered_correctly", False),
                "property_used_for_visibility": "enabled" if properties_analysis_test.get("property_stats", {}).get("items_with_enabled", 0) > 0 else "unknown"
            }
            
            all_results["summary"] = {
                "workflow_success": workflow_success,
                "key_findings": key_findings,
                "conclusion": "Backend filtering working correctly" if workflow_success else "Backend filtering has issues"
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution"""
    tester = MenuVisibilityWorkflowTester()
    results = await tester.run_comprehensive_workflow_test()
    
    print("\n" + "=" * 70)
    print("📋 MENU VISIBILITY WORKFLOW TEST RESULTS")
    print("=" * 70)
    
    summary = results.get("summary", {})
    key_findings = summary.get("key_findings", {})
    
    print(f"Workflow Success: {'✅' if summary.get('workflow_success') else '❌'}")
    print(f"Conclusion: {summary.get('conclusion', 'Unknown')}")
    
    print("\n🔍 KEY FINDINGS:")
    for finding, value in key_findings.items():
        status = "✅" if value else "❌"
        print(f"  {status} {finding.replace('_', ' ').title()}: {value}")
    
    print("\n" + "=" * 70)
    
    # Save detailed results to file
    with open("/app/menu_workflow_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("📄 Detailed results saved to: /app/menu_workflow_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())