#!/usr/bin/env python3
"""
Fix Menu Database Inconsistency
Fix the database inconsistency where desktop Messages is enabled while mobile Messages is disabled.
"""

import asyncio
import motor.motor_asyncio
import json
from datetime import datetime, timezone
import os

# MongoDB Connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/cataloro_marketplace')

async def fix_menu_database_inconsistency():
    """Fix the database inconsistency for Messages enabled state"""
    print("🔧 Starting Menu Database Inconsistency Fix")
    print("=" * 60)
    
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.cataloro_marketplace
    
    try:
        # Get current menu settings
        menu_settings = await db.menu_settings.find_one({"type": "menu_config"})
        
        if not menu_settings:
            print("❌ No menu settings found in database")
            return False
        
        print("📊 Current State:")
        desktop_messages = menu_settings.get("desktop_menu", {}).get("messages", {})
        mobile_messages = menu_settings.get("mobile_menu", {}).get("messages", {})
        
        desktop_enabled = desktop_messages.get("enabled")
        mobile_enabled = mobile_messages.get("enabled")
        
        print(f"  Desktop Messages enabled: {desktop_enabled}")
        print(f"  Mobile Messages enabled: {mobile_enabled}")
        
        if desktop_enabled == mobile_enabled:
            print("✅ Messages settings are already consistent - no fix needed")
            return True
        
        print(f"\n🔧 Fixing inconsistency...")
        print(f"  Setting desktop Messages enabled: false to match mobile")
        
        # Update desktop Messages to match mobile (disabled)
        update_result = await db.menu_settings.update_one(
            {"type": "menu_config"},
            {
                "$set": {
                    "desktop_menu.messages.enabled": False,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "fix_applied": {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "description": "Fixed desktop Messages enabled inconsistency to match mobile",
                        "previous_desktop_enabled": desktop_enabled,
                        "new_desktop_enabled": False
                    }
                }
            }
        )
        
        if update_result.modified_count > 0:
            print("✅ Database inconsistency fixed successfully")
            
            # Verify the fix
            updated_settings = await db.menu_settings.find_one({"type": "menu_config"})
            updated_desktop_enabled = updated_settings.get("desktop_menu", {}).get("messages", {}).get("enabled")
            updated_mobile_enabled = updated_settings.get("mobile_menu", {}).get("messages", {}).get("enabled")
            
            print(f"\n📊 Updated State:")
            print(f"  Desktop Messages enabled: {updated_desktop_enabled}")
            print(f"  Mobile Messages enabled: {updated_mobile_enabled}")
            print(f"  Consistent: {updated_desktop_enabled == updated_mobile_enabled}")
            
            if updated_desktop_enabled == updated_mobile_enabled:
                print("✅ Fix verified - Messages settings now consistent")
                return True
            else:
                print("❌ Fix verification failed - settings still inconsistent")
                return False
        else:
            print("❌ Failed to update database")
            return False
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False
    finally:
        client.close()

async def main():
    """Run the database fix"""
    success = await fix_menu_database_inconsistency()
    
    if success:
        print(f"\n🎉 Database inconsistency fix completed successfully!")
        print(f"📋 Next steps:")
        print(f"  1. Test desktop navigation - Messages should now be hidden")
        print(f"  2. Test mobile navigation - Messages should remain hidden")
        print(f"  3. Verify admin settings show both as disabled")
        print(f"  4. Confirm loading state fix continues working")
    else:
        print(f"\n❌ Database inconsistency fix failed!")
        print(f"📋 Manual intervention may be required")

if __name__ == "__main__":
    asyncio.run(main())