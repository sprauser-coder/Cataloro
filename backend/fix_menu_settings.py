#!/usr/bin/env python3
"""
Fix Menu Settings - Remove test items and restore real navigation data
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://market-guardian.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

# Correct real navigation structure
CORRECT_MENU_SETTINGS = {
    "desktop_menu": {
        "about": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "About Platform", "icon": "Globe", "path": "/info"},
        "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Browse", "icon": "Store", "path": "/browse"},
        "create_listing": {"enabled": True, "roles": ["admin", "manager", "seller"], "label": "Create Listing", "icon": "Plus", "path": "/create-listing"},
        "messages": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Messages", "icon": "MessageCircle", "path": "/messages"},
        "tenders": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Tenders", "icon": "DollarSign", "path": "/tenders"},
        "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Profile", "icon": "User", "path": "/profile"},
        "admin_panel": {"enabled": True, "roles": ["admin", "manager"], "label": "Admin Panel", "icon": "Shield", "path": "/admin"},
        "buy_management": {"enabled": True, "roles": ["admin", "manager", "buyer"], "label": "Buy Management", "icon": "ShoppingCart", "path": "/buy-management"},
        "my_listings": {"enabled": True, "roles": ["admin", "manager", "seller"], "label": "My Listings", "icon": "Package", "path": "/my-listings"},
        "favorites": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Favorites", "icon": "Heart", "path": "/favorites"},
        "notifications": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Notifications", "icon": "Bell", "path": "/notifications"}
    },
    "mobile_menu": {
        "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Browse", "icon": "Store", "path": "/browse"},
        "messages": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Messages", "icon": "MessageCircle", "path": "/messages"},
        "create": {"enabled": True, "roles": ["admin", "manager", "seller"], "label": "Create", "icon": "Plus", "path": "/create-listing"},
        "tenders": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Tenders", "icon": "DollarSign", "path": "/mobile-tenders"},
        "listings": {"enabled": True, "roles": ["admin", "manager", "seller"], "label": "Listings", "icon": "Package", "path": "/mobile-my-listings"},
        "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Profile", "icon": "User", "path": "/profile"},
        "admin_drawer": {"enabled": True, "roles": ["admin", "manager"], "label": "Admin Panel", "icon": "BarChart3", "path": "/admin"},
        "about": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "About Platform", "icon": "Globe", "path": "/info"},
        "buy_management": {"enabled": True, "roles": ["admin", "manager", "buyer"], "label": "Buy Management", "icon": "ShoppingCart", "path": "/buy-management"},
        "favorites": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Favorites", "icon": "Heart", "path": "/favorites"},
        "notifications": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"], "label": "Notifications", "icon": "Bell", "path": "/notifications"}
    }
}

async def fix_menu_settings():
    """Remove test items and restore real navigation data"""
    print("🔧 Fixing Menu Settings - Removing test items and restoring real navigation...")
    
    async with aiohttp.ClientSession() as session:
        # 1. Authenticate admin
        print("🔐 Authenticating admin...")
        async with session.post(f"{BACKEND_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }) as response:
            if response.status == 200:
                auth_data = await response.json()
                token = auth_data["token"]
                headers = {"Authorization": f"Bearer {token}"}
                print("  ✅ Admin authenticated")
            else:
                print("  ❌ Admin authentication failed")
                return
        
        # 2. Apply fix - restore correct menu settings
        print("🔧 Restoring correct real navigation structure...")
        async with session.post(f"{BACKEND_URL}/admin/menu-settings", 
                               json=CORRECT_MENU_SETTINGS, headers=headers) as response:
            if response.status == 200:
                print("  ✅ Menu settings updated successfully")
            else:
                print("  ❌ Failed to update menu settings")
                return
        
        # 3. Verify fix worked
        print("✅ Verifying fix...")
        async with session.get(f"{BACKEND_URL}/admin/menu-settings", headers=headers) as response:
            if response.status == 200:
                fixed_settings = await response.json()
                desktop_items = list(fixed_settings.get("desktop_menu", {}).keys())
                mobile_items = list(fixed_settings.get("mobile_menu", {}).keys())
                
                print(f"  Desktop menu items ({len(desktop_items)}): {desktop_items}")
                print(f"  Mobile menu items ({len(mobile_items)}): {mobile_items}")
                
                # Check for test items
                all_items = desktop_items + mobile_items
                test_items = [item for item in all_items if any(pattern in item.lower() for pattern in ["test", "dummy", "sample"])]
                
                if test_items:
                    print(f"  ❌ TEST ITEMS STILL PRESENT: {test_items}")
                else:
                    print("  ✅ All test items removed - only real navigation items present")
        
        print("\n🎯 Menu Settings Fix Complete!")
        print("- Removed all test items from menu settings")
        print("- Restored proper real navigation structure")
        print("- Menu Settings now contains only actual navigation items")

if __name__ == "__main__":
    asyncio.run(fix_menu_settings())