#!/usr/bin/env python3
"""
Debug script to examine the exact API response from admin menu settings
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://nginx-config-fix.preview.emergentagent.com/api"

async def debug_menu_api():
    async with aiohttp.ClientSession() as session:
        # Login first
        login_data = {"email": "admin@cataloro.com", "password": "password123"}
        
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                token = login_result.get("token")
                print(f"✅ Login successful, token: {token[:20]}...")
                
                # Get menu settings
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(f"{BACKEND_URL}/admin/menu-settings", headers=headers) as menu_response:
                    if menu_response.status == 200:
                        menu_data = await menu_response.json()
                        print("\n🔍 RAW MENU SETTINGS API RESPONSE:")
                        print("=" * 60)
                        print(json.dumps(menu_data, indent=2))
                        
                        print("\n🎯 SPECIFIC BUY/SELL/INVENTORY ITEMS:")
                        print("=" * 60)
                        desktop_menu = menu_data.get('desktop_menu', {})
                        
                        for item_name in ['buy', 'sell', 'buy_management']:
                            if item_name in desktop_menu:
                                item_config = desktop_menu[item_name]
                                print(f"{item_name}:")
                                print(f"  enabled: {item_config.get('enabled')}")
                                print(f"  label: {item_config.get('label')}")
                                print(f"  roles: {item_config.get('roles')}")
                                print()
                            else:
                                print(f"{item_name}: NOT FOUND")
                                print()
                    else:
                        error_text = await menu_response.text()
                        print(f"❌ Menu settings API failed: {menu_response.status} - {error_text}")
            else:
                error_text = await response.text()
                print(f"❌ Login failed: {response.status} - {error_text}")

if __name__ == "__main__":
    asyncio.run(debug_menu_api())