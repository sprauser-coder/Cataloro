#!/usr/bin/env python3
"""
Direct Database Menu Settings Fix
Directly update the database to fix inconsistencies
"""

import asyncio
import aiohttp
import json

# Test Configuration
BACKEND_URL = "https://mobileui-sync.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

async def main():
    """Direct fix approach"""
    print("🚀 Direct Database Menu Settings Fix")
    print("=" * 50)
    
    session = aiohttp.ClientSession()
    
    try:
        # Authenticate
        print("🔐 Authenticating...")
        login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                auth_data = await response.json()
                token = auth_data.get("token") or auth_data.get("data", {}).get("token")
                if token:
                    print("  ✅ Authenticated")
                else:
                    print(f"  ❌ No token in response: {auth_data}")
                    return
            else:
                error_text = await response.text()
                print(f"  ❌ Authentication failed: {error_text}")
                return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get current settings
        print("📋 Getting current settings...")
        async with session.get(f"{BACKEND_URL}/admin/menu-settings", headers=headers) as response:
            if response.status == 200:
                current_data = await response.json()
                print("  ✅ Current settings retrieved")
            else:
                print("  ❌ Failed to get settings")
                return
        
        # Create completely consistent settings
        print("🔧 Creating consistent settings...")
        
        # Set all items to disabled for consistency (matching the desktop state)
        consistent_settings = {
            "desktop_menu": {
                "about": {"enabled": False, "label": "About Platform", "icon": "info", "path": "/about", "roles": ["admin", "manager", "seller", "buyer"]},
                "browse": {"enabled": False, "label": "Browse", "icon": "search", "path": "/browse", "roles": ["admin", "manager", "seller", "buyer"]},
                "create_listing": {"enabled": False, "label": "Create Listing", "icon": "plus", "path": "/create", "roles": ["admin", "manager", "seller"]},
                "messages": {"enabled": False, "label": "Messages", "icon": "message-circle", "path": "/messages", "roles": ["admin", "manager", "seller", "buyer"]},
                "tenders": {"enabled": False, "label": "Tenders", "icon": "file-text", "path": "/tenders", "roles": ["admin", "manager", "seller", "buyer"]},
                "profile": {"enabled": False, "label": "Profile", "icon": "user", "path": "/profile", "roles": ["admin", "manager", "seller", "buyer"]},
                "admin_panel": {"enabled": True, "label": "Admin Panel", "icon": "settings", "path": "/admin", "roles": ["admin", "manager"]},
                "buy_management": {"enabled": False, "label": "Buy Management", "icon": "shopping-cart", "path": "/buy-management", "roles": ["admin", "manager", "buyer"]},
                "my_listings": {"enabled": False, "label": "My Listings", "icon": "list", "path": "/my-listings", "roles": ["admin", "manager", "seller"]},
                "favorites": {"enabled": False, "label": "Favorites", "icon": "heart", "path": "/favorites", "roles": ["admin", "manager", "seller", "buyer"]},
                "notifications": {"enabled": False, "label": "Notifications", "icon": "bell", "path": "/notifications", "roles": ["admin", "manager", "seller", "buyer"]}
            },
            "mobile_menu": {
                "browse": {"enabled": False, "label": "Browse", "icon": "search", "path": "/browse", "roles": ["admin", "manager", "seller", "buyer"]},
                "messages": {"enabled": False, "label": "Messages", "icon": "message-circle", "path": "/messages", "roles": ["admin", "manager", "seller", "buyer"]},
                "create": {"enabled": False, "label": "Create", "icon": "plus", "path": "/create", "roles": ["admin", "manager", "seller"]},
                "tenders": {"enabled": False, "label": "Tenders", "icon": "file-text", "path": "/tenders", "roles": ["admin", "manager", "seller", "buyer"]},
                "listings": {"enabled": False, "label": "My Listings", "icon": "list", "path": "/my-listings", "roles": ["admin", "manager", "seller"]},
                "profile": {"enabled": False, "label": "Profile", "icon": "user", "path": "/profile", "roles": ["admin", "manager", "seller", "buyer"]},
                "admin_drawer": {"enabled": True, "label": "Admin", "icon": "settings", "path": "/admin", "roles": ["admin", "manager"]},
                "about": {"enabled": False, "label": "About", "icon": "info", "path": "/about", "roles": ["admin", "manager", "seller", "buyer"]},
                "buy_management": {"enabled": False, "label": "Buy Management", "icon": "shopping-cart", "path": "/buy-management", "roles": ["admin", "manager", "buyer"]},
                "favorites": {"enabled": False, "label": "Favorites", "icon": "heart", "path": "/favorites", "roles": ["admin", "manager", "seller", "buyer"]},
                "notifications": {"enabled": False, "label": "Notifications", "icon": "bell", "path": "/notifications", "roles": ["admin", "manager", "seller", "buyer"]}
            }
        }
        
        # Apply the consistent settings
        print("💾 Applying consistent settings...")
        async with session.post(f"{BACKEND_URL}/admin/menu-settings", json=consistent_settings, headers=headers) as response:
            if response.status == 200:
                print("  ✅ Consistent settings applied")
            else:
                error_text = await response.text()
                print(f"  ❌ Failed to apply settings: {error_text}")
                return
        
        # Verify the fix
        print("✅ Verifying consistency...")
        async with session.get(f"{BACKEND_URL}/admin/menu-settings", headers=headers) as response:
            if response.status == 200:
                verification_data = await response.json()
                
                desktop_menu = verification_data.get("desktop_menu", {})
                mobile_menu = verification_data.get("mobile_menu", {})
                
                # Check for inconsistencies
                all_items = set(desktop_menu.keys()) | set(mobile_menu.keys())
                inconsistencies = 0
                
                for item_key in all_items:
                    desktop_enabled = desktop_menu.get(item_key, {}).get("enabled", True)
                    mobile_enabled = mobile_menu.get(item_key, {}).get("enabled", True)
                    
                    if desktop_enabled != mobile_enabled:
                        inconsistencies += 1
                        print(f"  ❌ Still inconsistent: {item_key} (desktop={desktop_enabled}, mobile={mobile_enabled})")
                
                if inconsistencies == 0:
                    print("  ✅ All inconsistencies resolved!")
                    
                    # Test user API to confirm filtering works
                    print("👤 Testing user API filtering...")
                    admin_user_id = "admin_user_1"
                    async with session.get(f"{BACKEND_URL}/menu-settings/user/{admin_user_id}") as user_response:
                        if user_response.status == 200:
                            user_data = await user_response.json()
                            desktop_items = list(user_data.get("desktop_menu", {}).keys())
                            mobile_items = list(user_data.get("mobile_menu", {}).keys())
                            
                            print(f"  📱 Desktop items returned to user: {len(desktop_items)} - {desktop_items}")
                            print(f"  📱 Mobile items returned to user: {len(mobile_items)} - {mobile_items}")
                            
                            # Should only see admin_panel and admin_drawer since everything else is disabled
                            expected_desktop = ["admin_panel"]
                            expected_mobile = ["admin_drawer"]
                            
                            desktop_correct = set(desktop_items) == set(expected_desktop)
                            mobile_correct = set(mobile_items) == set(expected_mobile)
                            
                            if desktop_correct and mobile_correct:
                                print("  ✅ User API filtering working correctly!")
                                print("\n🎉 ALL MENU ITEMS DATABASE INCONSISTENCIES HAVE BEEN RESOLVED!")
                                print("🎉 ALL HIDDEN ITEMS ARE NOW PROPERLY FILTERED FROM USER API RESPONSES!")
                            else:
                                print("  ⚠️ User API filtering may have issues")
                        else:
                            print("  ❌ Failed to test user API")
                else:
                    print(f"  ❌ {inconsistencies} inconsistencies remain")
            else:
                print("  ❌ Failed to verify settings")
    
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())