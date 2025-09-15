#!/usr/bin/env python3
"""
Menu Settings Database Fix Script
This script demonstrates the issue and provides a solution to remove test items
and restore proper real navigation items in the menu_settings collection.
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://vps-sync.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

# Correct real navigation structure (from backend code)
CORRECT_MENU_SETTINGS = {
    "desktop_menu": {
        "about": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "create_listing": {"enabled": True, "roles": ["admin", "manager", "seller"]},
        "messages": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "tenders": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "admin_panel": {"enabled": True, "roles": ["admin", "manager"]},
        "buy_management": {"enabled": True, "roles": ["admin", "manager", "buyer"]},
        "my_listings": {"enabled": True, "roles": ["admin", "manager", "seller"]},
        "favorites": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "notifications": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]}
    },
    "mobile_menu": {
        "browse": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "messages": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "create": {"enabled": True, "roles": ["admin", "manager", "seller"]},
        "tenders": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "listings": {"enabled": True, "roles": ["admin", "manager", "seller"]},
        "profile": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "admin_drawer": {"enabled": True, "roles": ["admin", "manager"]},
        "favorites": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]},
        "notifications": {"enabled": True, "roles": ["admin", "manager", "seller", "buyer"]}
    }
}

async def demonstrate_issue_and_fix():
    """Demonstrate the test items issue and provide fix"""
    
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
        
        # 2. Show current contaminated menu settings
        print("\n🔍 Current Menu Settings (CONTAMINATED WITH TEST DATA):")
        async with session.get(f"{BACKEND_URL}/admin/menu-settings", headers=headers) as response:
            if response.status == 200:
                current_settings = await response.json()
                print("  Desktop menu items:", list(current_settings.get("desktop_menu", {}).keys()))
                print("  Mobile menu items:", list(current_settings.get("mobile_menu", {}).keys()))
                
                # Identify test items
                test_items = []
                for section_name, section_data in current_settings.items():
                    if isinstance(section_data, dict):
                        for item_key in section_data.keys():
                            if any(pattern in item_key.lower() for pattern in ["test", "dummy", "sample"]):
                                test_items.append(f"{section_name}.{item_key}")
                
                if test_items:
                    print(f"  🚨 TEST ITEMS FOUND: {test_items}")
                else:
                    print("  ✅ No test items found")
            else:
                print("  ❌ Failed to get current menu settings")
                return
        
        # 3. Show what admin user receives (with test items)
        print("\n👤 What Admin User Currently Receives:")
        async with session.get(f"{BACKEND_URL}/menu-settings/user/admin_user_1") as response:
            if response.status == 200:
                user_menu = await response.json()
                print("  Admin desktop items:", list(user_menu.get("desktop_menu", {}).keys()))
                print("  Admin mobile items:", list(user_menu.get("mobile_menu", {}).keys()))
                
                # Check for test items in user menu
                user_test_items = []
                for section_name, section_data in user_menu.items():
                    if isinstance(section_data, dict):
                        for item_key in section_data.keys():
                            if any(pattern in item_key.lower() for pattern in ["test", "dummy", "sample"]):
                                user_test_items.append(f"{section_name}.{item_key}")
                
                if user_test_items:
                    print(f"  🚨 ADMIN USER RECEIVING TEST ITEMS: {user_test_items}")
                else:
                    print("  ✅ Admin user not receiving test items")
        
        # 4. Apply fix (restore correct menu settings)
        print("\n🔧 APPLYING FIX - Restoring Correct Menu Settings:")
        async with session.post(f"{BACKEND_URL}/admin/menu-settings", 
                               json=CORRECT_MENU_SETTINGS, headers=headers) as response:
            if response.status == 200:
                print("  ✅ Menu settings updated successfully")
            else:
                print("  ❌ Failed to update menu settings")
                return
        
        # 5. Verify fix worked
        print("\n✅ VERIFICATION - Menu Settings After Fix:")
        async with session.get(f"{BACKEND_URL}/admin/menu-settings", headers=headers) as response:
            if response.status == 200:
                fixed_settings = await response.json()
                print("  Desktop menu items:", list(fixed_settings.get("desktop_menu", {}).keys()))
                print("  Mobile menu items:", list(fixed_settings.get("mobile_menu", {}).keys()))
                
                # Check for test items after fix
                test_items_after = []
                for section_name, section_data in fixed_settings.items():
                    if isinstance(section_data, dict):
                        for item_key in section_data.keys():
                            if any(pattern in item_key.lower() for pattern in ["test", "dummy", "sample"]):
                                test_items_after.append(f"{section_name}.{item_key}")
                
                if test_items_after:
                    print(f"  ❌ TEST ITEMS STILL PRESENT: {test_items_after}")
                else:
                    print("  ✅ All test items removed successfully")
        
        # 6. Verify admin user now receives correct menu
        print("\n👤 What Admin User Now Receives (After Fix):")
        async with session.get(f"{BACKEND_URL}/menu-settings/user/admin_user_1") as response:
            if response.status == 200:
                fixed_user_menu = await response.json()
                print("  Admin desktop items:", list(fixed_user_menu.get("desktop_menu", {}).keys()))
                print("  Admin mobile items:", list(fixed_user_menu.get("mobile_menu", {}).keys()))
                
                # Check for test items in user menu after fix
                user_test_items_after = []
                for section_name, section_data in fixed_user_menu.items():
                    if isinstance(section_data, dict):
                        for item_key in section_data.keys():
                            if any(pattern in item_key.lower() for pattern in ["test", "dummy", "sample"]):
                                user_test_items_after.append(f"{section_name}.{item_key}")
                
                if user_test_items_after:
                    print(f"  ❌ ADMIN USER STILL RECEIVING TEST ITEMS: {user_test_items_after}")
                else:
                    print("  ✅ Admin user now receiving only real navigation items")
        
        print("\n" + "="*60)
        print("🎯 SUMMARY:")
        print("- Issue: Test items (test_item, frontend_test) were in menu_settings database")
        print("- Impact: Admin users were seeing test items in their navigation menus")
        print("- Root Cause: Test data contamination in menu_settings collection")
        print("- Solution: Restored correct real navigation items structure")
        print("- Status: Menu Settings now contains proper real navigation items")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(demonstrate_issue_and_fix())