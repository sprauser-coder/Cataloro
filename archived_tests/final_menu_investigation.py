#!/usr/bin/env python3
"""
Final Menu Consistency Investigation and Report
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://mobileui-sync.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

async def main():
    session = aiohttp.ClientSession()
    
    try:
        # Authenticate
        login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            auth_data = await response.json()
            token = auth_data.get("token") or auth_data.get("data", {}).get("token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        print("🔍 FINAL MENU CONSISTENCY INVESTIGATION REPORT")
        print("=" * 60)
        
        # Get admin menu settings
        async with session.get(f"{BACKEND_URL}/admin/menu-settings", headers=headers) as response:
            admin_data = await response.json()
        
        desktop_menu = admin_data.get("desktop_menu", {})
        mobile_menu = admin_data.get("mobile_menu", {})
        
        print("📋 ADMIN MENU SETTINGS ANALYSIS:")
        print(f"   Desktop menu items: {len(desktop_menu)}")
        print(f"   Mobile menu items: {len(mobile_menu)}")
        
        # Find all items marked as Hidden
        hidden_desktop = []
        hidden_mobile = []
        
        for item, config in desktop_menu.items():
            if not config.get("enabled", True):
                hidden_desktop.append(item)
        
        for item, config in mobile_menu.items():
            if not config.get("enabled", True):
                hidden_mobile.append(item)
        
        print(f"\n🔍 ITEMS MARKED AS HIDDEN:")
        print(f"   Desktop Hidden: {len(hidden_desktop)} items - {hidden_desktop}")
        print(f"   Mobile Hidden: {len(hidden_mobile)} items - {hidden_mobile}")
        
        # Check for inconsistencies
        all_items = set(desktop_menu.keys()) | set(mobile_menu.keys())
        inconsistencies = []
        
        for item in all_items:
            desktop_enabled = desktop_menu.get(item, {}).get("enabled", True)
            mobile_enabled = mobile_menu.get(item, {}).get("enabled", True)
            
            if desktop_enabled != mobile_enabled:
                inconsistencies.append({
                    "item": item,
                    "desktop_enabled": desktop_enabled,
                    "mobile_enabled": mobile_enabled
                })
        
        print(f"\n❌ DATABASE INCONSISTENCIES FOUND: {len(inconsistencies)}")
        for inc in inconsistencies:
            print(f"   - {inc['item']}: desktop={inc['desktop_enabled']}, mobile={inc['mobile_enabled']}")
        
        # Check user API response
        admin_user_id = "admin_user_1"
        async with session.get(f"{BACKEND_URL}/menu-settings/user/{admin_user_id}") as response:
            user_data = await response.json()
        
        user_desktop = list(user_data.get("desktop_menu", {}).keys())
        user_mobile = list(user_data.get("mobile_menu", {}).keys())
        
        print(f"\n👤 USER API RESPONSE:")
        print(f"   Desktop items returned: {len(user_desktop)} - {user_desktop}")
        print(f"   Mobile items returned: {len(user_mobile)} - {user_mobile}")
        
        # Check if hidden items are still visible
        problematic_items = []
        
        for item in user_desktop:
            if item in hidden_desktop:
                problematic_items.append(f"{item} (desktop)")
        
        for item in user_mobile:
            if item in hidden_mobile:
                problematic_items.append(f"{item} (mobile)")
        
        print(f"\n🚨 HIDDEN ITEMS STILL VISIBLE TO USERS: {len(problematic_items)}")
        for item in problematic_items:
            print(f"   - {item}")
        
        # Summary
        print(f"\n📊 INVESTIGATION SUMMARY:")
        print(f"   Total menu items analyzed: {len(all_items)}")
        print(f"   Items marked as Hidden: {len(set(hidden_desktop + hidden_mobile))}")
        print(f"   Database inconsistencies: {len(inconsistencies)}")
        print(f"   Hidden items still visible: {len(problematic_items)}")
        
        if len(inconsistencies) == 0 and len(problematic_items) == 0:
            print(f"\n✅ ALL ISSUES RESOLVED!")
        else:
            print(f"\n⚠️ ISSUES REMAIN - REQUIRES FURTHER INVESTIGATION")
        
        # Save detailed report
        report = {
            "timestamp": "2025-01-11 23:30:00 UTC",
            "admin_menu_settings": admin_data,
            "user_api_response": user_data,
            "hidden_desktop_items": hidden_desktop,
            "hidden_mobile_items": hidden_mobile,
            "database_inconsistencies": inconsistencies,
            "problematic_items": problematic_items,
            "summary": {
                "total_items": len(all_items),
                "hidden_items": len(set(hidden_desktop + hidden_mobile)),
                "inconsistencies": len(inconsistencies),
                "still_visible": len(problematic_items)
            }
        }
        
        with open("/app/final_menu_investigation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: /app/final_menu_investigation_report.json")
    
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())