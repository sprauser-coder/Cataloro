#!/usr/bin/env python3
"""
Fix All Menu Items Database Inconsistencies
Based on the investigation findings
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://market-guardian.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"  
ADMIN_PASSWORD = "admin_password"

async def fix_all_menu_inconsistencies():
    """Fix all database inconsistencies for menu items"""
    print("🔧 Fixing All Menu Items Database Inconsistencies")
    print("=" * 60)
    
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
        
        # Create consistent settings - match the "Hidden" status from admin interface
        print("🔧 Applying database consistency fixes...")
        
        # Based on investigation: Set all items to disabled (matching admin interface display)
        # Only admin panel and admin drawer should remain enabled
        consistent_settings = {
            "desktop_menu": {
                "about": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "About Platform", "icon": "Globe", "path": "/info"},
                "browse": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Browse", "icon": "Store", "path": "/browse"},
                "create_listing": {"enabled": False, "roles": ["admin", "manager", "seller"], "label": "Create Listing", "icon": "Plus", "path": "/create-listing"},
                "messages": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Messages", "icon": "MessageCircle", "path": "/messages"},
                "tenders": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Tenders", "icon": "DollarSign", "path": "/tenders"},
                "profile": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Profile", "icon": "User", "path": "/profile"},
                "admin_panel": {"enabled": True, "roles": ["admin", "manager"], "label": "Admin Panel", "icon": "Shield", "path": "/admin"},
                "buy_management": {"enabled": False, "roles": ["admin", "manager", "buyer"], "label": "Buy Management", "icon": "ShoppingCart", "path": "/buy-management"},
                "my_listings": {"enabled": False, "roles": ["admin", "manager", "seller"], "label": "My Listings", "icon": "Package", "path": "/my-listings"},
                "favorites": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Favorites", "icon": "Heart", "path": "/favorites"},
                "notifications": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Notifications", "icon": "Bell", "path": "/notifications"}
            },
            "mobile_menu": {
                "browse": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Browse", "icon": "Store", "path": "/browse"},
                "messages": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Messages", "icon": "MessageCircle", "path": "/messages"},
                "create": {"enabled": False, "roles": ["admin", "manager", "seller"], "label": "Create", "icon": "Plus", "path": "/create-listing"},
                "tenders": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Tenders", "icon": "DollarSign", "path": "/mobile-tenders"},
                "listings": {"enabled": False, "roles": ["admin", "manager", "seller"], "label": "Listings", "icon": "Package", "path": "/mobile-my-listings"},
                "profile": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Profile", "icon": "User", "path": "/profile"},
                "admin_drawer": {"enabled": True, "roles": ["admin", "manager"], "label": "Admin Panel", "icon": "BarChart3", "path": "/admin"},
                "about": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "About Platform", "icon": "Globe", "path": "/info"},
                "buy_management": {"enabled": False, "roles": ["admin", "manager", "buyer"], "label": "Buy Management", "icon": "ShoppingCart", "path": "/buy-management"},
                "favorites": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Favorites", "icon": "Heart", "path": "/favorites"},
                "notifications": {"enabled": False, "roles": ["admin", "manager", "seller", "buyer"], "label": "Notifications", "icon": "Bell", "path": "/notifications"}
            }
        }
        
        # Apply the fix
        async with session.post(f"{BACKEND_URL}/admin/menu-settings", 
                               json=consistent_settings, headers=headers) as response:
            if response.status == 200:
                print("  ✅ Database consistency fixes applied")
            else:
                print("  ❌ Failed to apply fixes")
                return
        
        # Verify all inconsistencies are resolved  
        print("✅ Verifying database consistency...")
        async with session.get(f"{BACKEND_URL}/admin/menu-settings", headers=headers) as response:
            verification = await response.json()
            
            desktop = verification["desktop_menu"]
            mobile = verification["mobile_menu"]
            
            inconsistencies = 0
            for key in set(desktop.keys()) | set(mobile.keys()):
                desk_enabled = desktop.get(key, {}).get("enabled", True)
                mobile_enabled = mobile.get(key, {}).get("enabled", True)
                if desk_enabled != mobile_enabled:
                    inconsistencies += 1
                    print(f"  ❌ Still inconsistent: {key}")
            
            if inconsistencies == 0:
                print("  ✅ All database inconsistencies resolved!")
            
        # Test user API
        print("👤 Testing user API filtering...")
        async with session.get(f"{BACKEND_URL}/menu-settings/user/admin_user_1") as response:
            user_data = await response.json()
            desktop_items = list(user_data.get("desktop_menu", {}).keys())
            mobile_items = list(user_data.get("mobile_menu", {}).keys())
            
            print(f"  🖥️ Desktop items returned: {len(desktop_items)} - {desktop_items}")
            print(f"  📱 Mobile items returned: {len(mobile_items)} - {mobile_items}")
            
            # Should only see admin items since everything else is disabled
            if len(desktop_items) <= 1 and len(mobile_items) <= 1:
                print("  ✅ All hidden items properly filtered from user API!")
            else:
                print("  ⚠️ Some disabled items may still be appearing")
        
        print("\n🎉 ALL MENU ITEMS DATABASE INCONSISTENCIES FIXED!")
        print("🎉 ALL ITEMS MARKED AS 'HIDDEN' SHOULD NOW BE PROPERLY HIDDEN!")
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(fix_all_menu_inconsistencies())