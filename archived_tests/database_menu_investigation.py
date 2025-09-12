#!/usr/bin/env python3
"""
Database Menu Investigation
Direct MongoDB investigation to understand the exact database state
"""

import asyncio
import motor.motor_asyncio
import json
from datetime import datetime
import os

# MongoDB Connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/cataloro_marketplace')

async def investigate_menu_database():
    """Investigate the exact database state for menu settings"""
    print("🔍 Starting Database Menu Investigation")
    print("=" * 60)
    
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.cataloro_marketplace
    
    try:
        # Get menu settings document
        menu_settings = await db.menu_settings.find_one({"type": "menu_config"})
        
        if not menu_settings:
            print("❌ No menu settings found in database")
            return
        
        print("📊 Raw Menu Settings Document:")
        print(json.dumps(menu_settings, indent=2, default=str))
        
        # Analyze desktop and mobile menu
        desktop_menu = menu_settings.get("desktop_menu", {})
        mobile_menu = menu_settings.get("mobile_menu", {})
        
        print(f"\n🖥️ Desktop Menu Analysis:")
        print(f"  Total items: {len(desktop_menu)}")
        
        desktop_messages = desktop_menu.get("messages", {})
        if desktop_messages:
            print(f"  Messages configuration:")
            print(f"    enabled: {desktop_messages.get('enabled')} ({type(desktop_messages.get('enabled'))})")
            print(f"    roles: {desktop_messages.get('roles', [])}")
            print(f"    label: {desktop_messages.get('label')}")
            print(f"    path: {desktop_messages.get('path')}")
        else:
            print("  Messages: NOT FOUND")
        
        print(f"\n📱 Mobile Menu Analysis:")
        print(f"  Total items: {len(mobile_menu)}")
        
        mobile_messages = mobile_menu.get("messages", {})
        if mobile_messages:
            print(f"  Messages configuration:")
            print(f"    enabled: {mobile_messages.get('enabled')} ({type(mobile_messages.get('enabled'))})")
            print(f"    roles: {mobile_messages.get('roles', [])}")
            print(f"    label: {mobile_messages.get('label')}")
            print(f"    path: {mobile_messages.get('path')}")
        else:
            print("  Messages: NOT FOUND")
        
        # Compare the two
        desktop_enabled = desktop_messages.get("enabled") if desktop_messages else None
        mobile_enabled = mobile_messages.get("enabled") if mobile_messages else None
        
        print(f"\n🔍 Comparison:")
        print(f"  Desktop Messages enabled: {desktop_enabled}")
        print(f"  Mobile Messages enabled: {mobile_enabled}")
        print(f"  Consistent: {desktop_enabled == mobile_enabled}")
        
        if desktop_enabled != mobile_enabled:
            print(f"  🚨 INCONSISTENCY DETECTED!")
            print(f"     Desktop: {desktop_enabled}")
            print(f"     Mobile: {mobile_enabled}")
            print(f"     This explains why desktop filtering fails while mobile works!")
        
        # Check when this was last updated
        updated_at = menu_settings.get("updated_at")
        if updated_at:
            print(f"\n📅 Last Updated: {updated_at}")
        
        # Save results
        results = {
            "investigation_timestamp": datetime.now().isoformat(),
            "menu_settings_found": bool(menu_settings),
            "desktop_menu_items": len(desktop_menu),
            "mobile_menu_items": len(mobile_menu),
            "desktop_messages_config": desktop_messages,
            "mobile_messages_config": mobile_messages,
            "desktop_messages_enabled": desktop_enabled,
            "mobile_messages_enabled": mobile_enabled,
            "settings_consistent": desktop_enabled == mobile_enabled,
            "inconsistency_detected": desktop_enabled != mobile_enabled,
            "full_menu_settings": menu_settings
        }
        
        with open('/app/database_menu_investigation_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: /app/database_menu_investigation_results.json")
        
        return results
        
    except Exception as e:
        print(f"❌ Error investigating database: {e}")
        return None
    finally:
        client.close()

async def main():
    """Run the database investigation"""
    await investigate_menu_database()

if __name__ == "__main__":
    asyncio.run(main())