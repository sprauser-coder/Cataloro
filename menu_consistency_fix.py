#!/usr/bin/env python3
"""
Menu Settings Database Consistency Fix
Fix all database inconsistencies by setting consistent enabled values
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://admin-nav-control.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

class MenuConsistencyFixer:
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
    
    async def make_request(self, endpoint: str, method: str = "GET", params=None, data=None, headers=None):
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
    
    async def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            print("  ✅ Admin authentication successful")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error')}")
            return False
    
    async def get_current_menu_settings(self):
        """Get current menu settings"""
        print("📋 Getting current menu settings...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if result["success"]:
            print("  ✅ Current menu settings retrieved")
            return result["data"]
        else:
            print(f"  ❌ Failed to get menu settings: {result.get('error')}")
            return None
    
    async def fix_inconsistencies(self, current_settings):
        """Fix all database inconsistencies"""
        print("🔧 Fixing database inconsistencies...")
        
        desktop_menu = current_settings.get("desktop_menu", {})
        mobile_menu = current_settings.get("mobile_menu", {})
        
        # Get all unique items
        all_items = set(desktop_menu.keys()) | set(mobile_menu.keys())
        
        # Create fixed settings
        fixed_desktop = {}
        fixed_mobile = {}
        
        inconsistencies_fixed = 0
        
        for item_key in all_items:
            desktop_config = desktop_menu.get(item_key, {})
            mobile_config = mobile_menu.get(item_key, {})
            
            desktop_enabled = desktop_config.get("enabled", True)
            mobile_enabled = mobile_config.get("enabled", True)
            
            # If there's an inconsistency, set both to the more restrictive value (False)
            if desktop_enabled != mobile_enabled:
                target_enabled = False  # Set both to disabled if inconsistent
                inconsistencies_fixed += 1
                
                print(f"  🔧 Fixing {item_key}: desktop={desktop_enabled}, mobile={mobile_enabled} → both={target_enabled}")
            else:
                target_enabled = desktop_enabled  # Keep consistent value
            
            # Update desktop config
            if item_key in desktop_menu:
                fixed_desktop[item_key] = {
                    **desktop_config,
                    "enabled": target_enabled
                }
            
            # Update mobile config  
            if item_key in mobile_menu:
                fixed_mobile[item_key] = {
                    **mobile_config,
                    "enabled": target_enabled
                }
        
        print(f"  📊 Fixed {inconsistencies_fixed} inconsistencies")
        
        return {
            "desktop_menu": fixed_desktop,
            "mobile_menu": fixed_mobile
        }, inconsistencies_fixed
    
    async def apply_fixes(self, fixed_settings):
        """Apply the fixed settings to the database"""
        print("💾 Applying fixes to database...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", "POST", data=fixed_settings, headers=headers)
        
        if result["success"]:
            print("  ✅ Fixes applied successfully")
            return True
        else:
            print(f"  ❌ Failed to apply fixes: {result.get('error')}")
            return False
    
    async def verify_fixes(self):
        """Verify that fixes have been applied"""
        print("✅ Verifying fixes...")
        
        # Get updated settings
        updated_settings = await self.get_current_menu_settings()
        if not updated_settings:
            return False
        
        desktop_menu = updated_settings.get("desktop_menu", {})
        mobile_menu = updated_settings.get("mobile_menu", {})
        
        # Check for remaining inconsistencies
        all_items = set(desktop_menu.keys()) | set(mobile_menu.keys())
        remaining_inconsistencies = 0
        
        for item_key in all_items:
            desktop_enabled = desktop_menu.get(item_key, {}).get("enabled", True)
            mobile_enabled = mobile_menu.get(item_key, {}).get("enabled", True)
            
            if desktop_enabled != mobile_enabled:
                remaining_inconsistencies += 1
                print(f"  ❌ Still inconsistent: {item_key} (desktop={desktop_enabled}, mobile={mobile_enabled})")
        
        if remaining_inconsistencies == 0:
            print("  ✅ All inconsistencies resolved!")
            return True
        else:
            print(f"  ❌ {remaining_inconsistencies} inconsistencies remain")
            return False
    
    async def run_fix(self):
        """Run the complete fix process"""
        print("🚀 Starting Menu Settings Database Consistency Fix")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Step 1: Authenticate
            if not await self.authenticate_admin():
                return False
            
            # Step 2: Get current settings
            current_settings = await self.get_current_menu_settings()
            if not current_settings:
                return False
            
            # Step 3: Fix inconsistencies
            fixed_settings, fixes_count = await self.fix_inconsistencies(current_settings)
            
            if fixes_count == 0:
                print("✅ No inconsistencies found - database is already consistent!")
                return True
            
            # Step 4: Apply fixes
            if not await self.apply_fixes(fixed_settings):
                return False
            
            # Step 5: Verify fixes
            if await self.verify_fixes():
                print("\n🎉 ALL DATABASE INCONSISTENCIES HAVE BEEN FIXED!")
                return True
            else:
                print("\n⚠️ Some issues may still remain")
                return False
                
        finally:
            await self.cleanup()

async def main():
    """Run the fix"""
    fixer = MenuConsistencyFixer()
    success = await fixer.run_fix()
    
    if success:
        print("\n✅ Menu settings database consistency fix completed successfully!")
    else:
        print("\n❌ Menu settings database consistency fix failed!")

if __name__ == "__main__":
    asyncio.run(main())