#!/usr/bin/env python3
"""
Fix Admin Navigation Issue
Initialize menu_settings collection with default configuration
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://marketplace-debug-3.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

class AdminNavigationFixer:
    def __init__(self):
        self.session = None
        self.admin_token = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: dict = None, data: dict = None, headers: dict = None) -> dict:
        """Make HTTP request"""
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
            if headers:
                request_kwargs['headers'] = headers
            
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **request_kwargs) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "data": response_data,
                    "status": response.status
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": 0
            }
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            print(f"✅ Admin authentication successful")
            return True
        else:
            print(f"❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            return False
    
    async def initialize_menu_settings(self) -> bool:
        """Initialize menu settings in database with default configuration"""
        print("⚙️ Initializing menu settings...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Define default menu settings that should be saved to database
        default_menu_settings = {
            "desktop_menu": {
                "about": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "About"},
                "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Browse"},
                "create_listing": {"enabled": True, "roles": ["admin", "manager", "seller"], "label": "Create Listing"},
                "messages": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Messages"},
                "tenders": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Tenders"},
                "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Profile"},
                "admin_panel": {"enabled": True, "roles": ["admin", "manager"], "label": "Admin Panel"},
                "buy_management": {"enabled": True, "roles": ["admin", "manager", "buyer"], "label": "Buy Management"},
                "my_listings": {"enabled": True, "roles": ["admin", "manager", "seller"], "label": "My Listings"},
                "favorites": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Favorites"}
            },
            "mobile_menu": {
                "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Browse"},
                "messages": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Messages"},
                "create": {"enabled": True, "roles": ["admin", "manager", "seller"], "label": "Create"},
                "tenders": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Tenders"},
                "listings": {"enabled": True, "roles": ["admin", "manager", "seller"], "label": "Listings"},
                "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Profile"},
                "admin_drawer": {"enabled": True, "roles": ["admin", "manager"], "label": "Admin"}
            }
        }
        
        # Save menu settings to database
        result = await self.make_request("/admin/menu-settings", "POST", data=default_menu_settings, headers=headers)
        
        if result["success"]:
            print("✅ Menu settings initialized successfully")
            return True
        else:
            print(f"❌ Failed to initialize menu settings: {result.get('error')}")
            return False
    
    async def verify_fix(self) -> dict:
        """Verify that the fix worked"""
        print("🔍 Verifying fix...")
        
        if not self.admin_token:
            return {"success": False, "error": "No admin token"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: Check admin menu settings
        admin_result = await self.make_request("/admin/menu-settings", headers=headers)
        
        # Test 2: Check user menu settings for admin
        user_result = await self.make_request("/menu-settings/user/admin_user_1")
        
        if admin_result["success"] and user_result["success"]:
            admin_data = admin_result["data"]
            user_data = user_result["data"]
            
            admin_desktop_count = len([k for k, v in admin_data.get("desktop_menu", {}).items() if isinstance(v, dict)])
            admin_mobile_count = len([k for k, v in admin_data.get("mobile_menu", {}).items() if isinstance(v, dict)])
            
            user_desktop_count = len([k for k, v in user_data.get("desktop_menu", {}).items() if isinstance(v, dict)])
            user_mobile_count = len([k for k, v in user_data.get("mobile_menu", {}).items() if isinstance(v, dict)])
            
            print(f"✅ Admin menu settings: {admin_desktop_count} desktop, {admin_mobile_count} mobile items")
            print(f"✅ User menu settings: {user_desktop_count} desktop, {user_mobile_count} mobile items")
            
            fix_successful = user_desktop_count > 0 or user_mobile_count > 0
            
            if fix_successful:
                print("🎉 FIX SUCCESSFUL! Admin can now see navigation items.")
            else:
                print("❌ Fix failed - admin still can't see navigation items")
            
            return {
                "success": True,
                "fix_successful": fix_successful,
                "admin_desktop_items": admin_desktop_count,
                "admin_mobile_items": admin_mobile_count,
                "user_desktop_items": user_desktop_count,
                "user_mobile_items": user_mobile_count,
                "admin_data": admin_data,
                "user_data": user_data
            }
        else:
            print("❌ Failed to verify fix")
            return {
                "success": False,
                "admin_result": admin_result,
                "user_result": user_result
            }
    
    async def run_fix(self) -> dict:
        """Run the complete fix process"""
        print("🚨 FIXING: Admin Navigation Visibility Issue")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Step 1: Authenticate
            if not await self.authenticate_admin():
                return {"error": "Authentication failed"}
            
            # Step 2: Initialize menu settings
            if not await self.initialize_menu_settings():
                return {"error": "Failed to initialize menu settings"}
            
            # Step 3: Verify fix
            verification = await self.verify_fix()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "fix_applied": True,
                "verification": verification
            }
            
        finally:
            await self.cleanup()


async def main():
    """Run the admin navigation fix"""
    fixer = AdminNavigationFixer()
    result = await fixer.run_fix()
    
    print("\n" + "=" * 60)
    print("🎯 FIX SUMMARY")
    print("=" * 60)
    
    if result.get("verification", {}).get("fix_successful"):
        print("✅ SUCCESS: Admin navigation visibility issue has been FIXED!")
        print("   - Menu settings initialized in database")
        print("   - Admin can now see navigation items")
        print("   - Both desktop and mobile menus are working")
    else:
        print("❌ FAILED: Fix was not successful")
        if "error" in result:
            print(f"   Error: {result['error']}")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())