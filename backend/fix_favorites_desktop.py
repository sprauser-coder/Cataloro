#!/usr/bin/env python3
"""
Fix Favorites Desktop Configuration
Enable Favorites for desktop to provide single controllable icon as requested
"""

import asyncio
import aiohttp

BACKEND_URL = "https://market-guardian.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

async def fix_favorites_desktop_config():
    """Enable Favorites for desktop menu to provide single controllable icon"""
    print("🔧 Fixing Favorites Desktop Configuration")
    print("=" * 50)
    
    session = aiohttp.ClientSession()
    
    try:
        # Authenticate
        print("🔐 Authenticating admin...")
        async with session.post(f"{BACKEND_URL}/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        }) as response:
            if response.status == 200:
                auth_data = await response.json()
                token = auth_data["token"]
                print("  ✅ Admin authenticated")
            else:
                print("  ❌ Authentication failed")
                return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get current settings
        print("📋 Getting current menu settings...")
        async with session.get(f"{BACKEND_URL}/admin/menu-settings", headers=headers) as response:
            current_settings = await response.json()
            
        print(f"Current desktop favorites enabled: {current_settings['desktop_menu']['favorites']['enabled']}")
        print(f"Current mobile favorites enabled: {current_settings['mobile_menu']['favorites']['enabled']}")
        
        # Enable desktop Favorites to match mobile (single controllable icon)
        current_settings['desktop_menu']['favorites']['enabled'] = True
        print("🔧 Enabling desktop Favorites...")
        
        # Apply the fix
        async with session.post(f"{BACKEND_URL}/admin/menu-settings", 
                               json=current_settings, headers=headers) as response:
            if response.status == 200:
                print("  ✅ Desktop Favorites enabled successfully")
            else:
                print("  ❌ Failed to enable desktop Favorites")
                return
        
        # Verify the fix
        print("✅ Verifying desktop Favorites configuration...")
        async with session.get(f"{BACKEND_URL}/admin/menu-settings", headers=headers) as response:
            verification = await response.json()
            desktop_enabled = verification['desktop_menu']['favorites']['enabled']
            mobile_enabled = verification['mobile_menu']['favorites']['enabled']
            
            print(f"  Desktop favorites enabled: {desktop_enabled}")
            print(f"  Mobile favorites enabled: {mobile_enabled}")
            
            if desktop_enabled and mobile_enabled:
                print("  ✅ Both desktop and mobile Favorites now enabled!")
            else:
                print("  ❌ Configuration still inconsistent")
        
        # Test user API
        print("👤 Testing user API response...")
        async with session.get(f"{BACKEND_URL}/menu-settings/user/admin_user_1") as response:
            user_data = await response.json()
            desktop_has_favorites = 'favorites' in user_data.get("desktop_menu", {})
            mobile_has_favorites = 'favorites' in user_data.get("mobile_menu", {})
            
            print(f"  Desktop menu includes favorites: {desktop_has_favorites}")
            print(f"  Mobile menu includes favorites: {mobile_has_favorites}")
            
            if desktop_has_favorites and mobile_has_favorites:
                print("  ✅ User API now returns Favorites for both desktop and mobile!")
                print("\n🎉 DESKTOP FAVORITES NOW AVAILABLE AS SINGLE CONTROLLABLE ICON!")
            else:
                print("  ⚠️ User API may still have issues")
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(fix_favorites_desktop_config())