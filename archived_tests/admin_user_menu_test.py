#!/usr/bin/env python3
"""
Admin User Menu Testing
Test the user menu API with admin credentials to see if disabled items show up for admin users
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://cataloro-partners.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"

class AdminUserMenuTester:
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
        """Authenticate as admin and get user ID"""
        print("🔐 Authenticating as admin...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            user_data = result["data"].get("user", {})
            self.admin_user_id = user_data.get("id")
            
            print(f"  ✅ Admin authentication successful")
            print(f"  👤 Admin user ID: {self.admin_user_id}")
            print(f"  🏷️ Admin role: {user_data.get('user_role', 'unknown')}")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            return False
    
    async def test_admin_user_menu(self):
        """Test user menu API with admin user ID"""
        print(f"\n👑 Testing user menu API with admin user ID...")
        
        if not self.admin_user_id:
            print("  ❌ No admin user ID available")
            return None
        
        result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
        
        if result["success"]:
            data = result["data"]
            
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            user_role = data.get("user_role", "unknown")
            
            print(f"  ✅ Admin user menu retrieved successfully")
            print(f"  👤 User role: {user_role}")
            print(f"  🖥️ Desktop menu items: {len(desktop_menu)}")
            print(f"  📱 Mobile menu items: {len(mobile_menu)}")
            
            # Check for disabled items
            disabled_items = []
            enabled_items = []
            
            print(f"\n  🔍 Desktop menu analysis:")
            for item_key, item_data in desktop_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    enabled = item_data.get("enabled", True)
                    print(f"    - {item_key}: enabled={enabled}, label='{item_data.get('label', 'N/A')}'")
                    if enabled:
                        enabled_items.append(f"desktop_{item_key}")
                    else:
                        disabled_items.append(f"desktop_{item_key}")
            
            print(f"\n  🔍 Mobile menu analysis:")
            for item_key, item_data in mobile_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    enabled = item_data.get("enabled", True)
                    print(f"    - {item_key}: enabled={enabled}, label='{item_data.get('label', 'N/A')}'")
                    if enabled:
                        enabled_items.append(f"mobile_{item_key}")
                    else:
                        disabled_items.append(f"mobile_{item_key}")
            
            print(f"\n  📊 Summary:")
            print(f"    - Total enabled items: {len(enabled_items)}")
            print(f"    - Total disabled items: {len(disabled_items)}")
            print(f"    - Disabled items: {disabled_items}")
            
            # Check if admin sees disabled items (this would be the issue)
            admin_sees_disabled_items = len(disabled_items) > 0
            
            return {
                "success": True,
                "user_role": user_role,
                "desktop_items_count": len(desktop_menu),
                "mobile_items_count": len(mobile_menu),
                "enabled_items": enabled_items,
                "disabled_items": disabled_items,
                "admin_sees_disabled_items": admin_sees_disabled_items,
                "full_data": data
            }
        else:
            print(f"  ❌ Failed to get admin user menu: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"]
            }
    
    async def compare_admin_vs_regular_user(self):
        """Compare admin user menu vs regular user menu"""
        print(f"\n🔄 Comparing admin vs regular user menu responses...")
        
        # Get admin user menu
        admin_result = await self.test_admin_user_menu()
        
        # Get regular user menu (using demo user)
        regular_user_id = "68bfff790e4e46bc28d43631"  # Demo user ID
        regular_result = await self.make_request(f"/menu-settings/user/{regular_user_id}")
        
        if admin_result and admin_result["success"] and regular_result["success"]:
            regular_data = regular_result["data"]
            
            print(f"\n  📊 Comparison Results:")
            print(f"    Admin user:")
            print(f"      - Role: {admin_result['user_role']}")
            print(f"      - Desktop items: {admin_result['desktop_items_count']}")
            print(f"      - Mobile items: {admin_result['mobile_items_count']}")
            print(f"      - Sees disabled items: {admin_result['admin_sees_disabled_items']}")
            print(f"      - Disabled items: {admin_result['disabled_items']}")
            
            print(f"    Regular user:")
            regular_desktop = regular_data.get("desktop_menu", {})
            regular_mobile = regular_data.get("mobile_menu", {})
            print(f"      - Role: {regular_data.get('user_role', 'unknown')}")
            print(f"      - Desktop items: {len(regular_desktop)}")
            print(f"      - Mobile items: {len(regular_mobile)}")
            
            # Check if regular user sees any disabled items
            regular_disabled_items = []
            for item_key, item_data in regular_desktop.items():
                if isinstance(item_data, dict) and item_data.get("enabled") == False:
                    regular_disabled_items.append(f"desktop_{item_key}")
            for item_key, item_data in regular_mobile.items():
                if isinstance(item_data, dict) and item_data.get("enabled") == False:
                    regular_disabled_items.append(f"mobile_{item_key}")
            
            print(f"      - Sees disabled items: {len(regular_disabled_items) > 0}")
            print(f"      - Disabled items: {regular_disabled_items}")
            
            # Analysis
            issue_identified = admin_result['admin_sees_disabled_items'] or len(regular_disabled_items) > 0
            
            print(f"\n  🔍 Analysis:")
            print(f"    - Issue identified: {issue_identified}")
            if issue_identified:
                print(f"    - Problem: Users are seeing disabled menu items in API response")
                print(f"    - This suggests the filtering is not working properly")
            else:
                print(f"    - Backend filtering appears to be working correctly")
                print(f"    - Issue may be in frontend implementation")
            
            return {
                "admin_result": admin_result,
                "regular_result": {
                    "success": True,
                    "user_role": regular_data.get('user_role'),
                    "desktop_items_count": len(regular_desktop),
                    "mobile_items_count": len(regular_mobile),
                    "disabled_items": regular_disabled_items
                },
                "issue_identified": issue_identified,
                "analysis": "Users seeing disabled items" if issue_identified else "Backend filtering working"
            }
        else:
            print(f"  ❌ Failed to complete comparison")
            return None
    
    async def run_test(self):
        """Run the complete test"""
        print("🚀 Starting Admin User Menu Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Authenticate
            auth_success = await self.authenticate_admin()
            if not auth_success:
                return {"error": "Authentication failed"}
            
            # Run comparison test
            comparison_result = await self.compare_admin_vs_regular_user()
            
            return {
                "test_timestamp": datetime.now().isoformat(),
                "comparison_result": comparison_result
            }
            
        finally:
            await self.cleanup()

async def main():
    tester = AdminUserMenuTester()
    results = await tester.run_test()
    
    print("\n" + "=" * 60)
    print("📊 ADMIN USER MENU TEST RESULTS")
    print("=" * 60)
    
    if "error" in results:
        print(f"❌ Test failed: {results['error']}")
    else:
        comparison = results.get("comparison_result", {})
        if comparison:
            print(f"🔍 Issue identified: {comparison.get('issue_identified', False)}")
            print(f"📝 Analysis: {comparison.get('analysis', 'Unknown')}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Save results
    with open("/app/admin_user_menu_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to /app/admin_user_menu_test_results.json")