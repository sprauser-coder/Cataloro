#!/usr/bin/env python3
"""
Populate Menu Settings Database with Real Navigation Structure
Based on actual frontend navigation components
"""

import asyncio
import motor.motor_asyncio
import os
from datetime import datetime, timezone

# MongoDB Connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

async def populate_real_menu_settings():
    """Populate database with real menu settings from the frontend components"""
    
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.cataloro_marketplace
    
    # Real menu settings based on the actual frontend navigation structure
    real_menu_settings = {
        "type": "menu_config",
        "desktop_menu": {
            # Main navigation items (from ModernHeader.js)
            "browse": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Browse",
                "icon": "Store",
                "path": "/browse"
            },
            "messages": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Messages",
                "icon": "MessageCircle", 
                "path": "/messages"
            },
            "create_listing": {
                "enabled": True,
                "roles": ["admin", "manager", "seller"],
                "label": "Create Listing",
                "icon": "Plus",
                "path": "/create-listing"
            },
            "favorites": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Favorites",
                "icon": "Heart",
                "path": "/favorites"
            },
            # User dropdown menu items (from ModernHeader.js user menu)
            "profile": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Profile Settings",
                "icon": "User",
                "path": "/profile"
            },
            "my_listings": {
                "enabled": True,
                "roles": ["admin", "manager", "seller"],
                "label": "My Listings",
                "icon": "Package",
                "path": "/my-listings"
            },
            "public_profile": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "View Public Profile",
                "icon": "Globe",
                "path": "/profile/{user_id}"
            },
            "admin_panel": {
                "enabled": True,
                "roles": ["admin", "manager"],
                "label": "Admin Panel",
                "icon": "Shield",
                "path": "/admin"
            },
            # Additional navigation items (from MobileNav.js and routes)
            "about": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "About Platform",
                "icon": "Globe",
                "path": "/info"
            },
            "buy_management": {
                "enabled": True,
                "roles": ["admin", "manager", "buyer"],
                "label": "Buy Management",
                "icon": "ShoppingCart",
                "path": "/buy-management"
            },
            "tenders": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Tenders",
                "icon": "DollarSign",
                "path": "/tenders"
            },
            "notifications": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Notifications",
                "icon": "Bell",
                "path": "/notifications"
            }
        },
        "mobile_menu": {
            # Bottom navigation items (from MobileBottomNav.js)
            "browse": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Browse",
                "icon": "Store",
                "path": "/browse"
            },
            "messages": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Messages",
                "icon": "MessageCircle",
                "path": "/messages"
            },
            "create": {
                "enabled": True,
                "roles": ["admin", "manager", "seller"],
                "label": "Create",
                "icon": "Plus",
                "path": "/create-listing",
                "highlight": True  # Central create button
            },
            "tenders": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Tenders",
                "icon": "DollarSign",
                "path": "/mobile-tenders"
            },
            "listings": {
                "enabled": True,
                "roles": ["admin", "manager", "seller"],
                "label": "Listings",
                "icon": "Package",
                "path": "/mobile-my-listings"
            },
            # Hamburger menu items (from MobileNav.js)
            "about": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "About Platform",
                "icon": "Globe",
                "path": "/info"
            },
            "buy_management": {
                "enabled": True,
                "roles": ["admin", "manager", "buyer"],
                "label": "Buy Management",
                "icon": "ShoppingCart",
                "path": "/buy-management"
            },
            "favorites": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Favorites",
                "icon": "Heart",
                "path": "/favorites"
            },
            "profile": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Profile",
                "icon": "User",
                "path": "/profile"
            },
            "notifications": {
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"],
                "label": "Notifications",
                "icon": "Bell",
                "path": "/notifications"
            },
            # Admin drawer (special mobile admin access)
            "admin_drawer": {
                "enabled": True,
                "roles": ["admin", "manager"],
                "label": "Admin Panel",
                "icon": "BarChart3",
                "path": "/admin"
            }
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "description": "Real menu settings based on actual frontend navigation structure"
    }
    
    try:
        # Update or insert the real menu settings
        result = await db.menu_settings.update_one(
            {"type": "menu_config"},
            {"$set": real_menu_settings},
            upsert=True
        )
        
        if result.upserted_id:
            print("✅ Real menu settings created successfully!")
        else:
            print("✅ Real menu settings updated successfully!")
        
        print(f"📊 Desktop menu items: {len(real_menu_settings['desktop_menu'])}")
        print(f"📱 Mobile menu items: {len(real_menu_settings['mobile_menu'])}")
        
        # Print summary
        print("\n📋 Desktop Menu Items:")
        for key, item in real_menu_settings['desktop_menu'].items():
            print(f"  - {item['label']} ({key}): {', '.join(item['roles'])}")
        
        print("\n📋 Mobile Menu Items:")
        for key, item in real_menu_settings['mobile_menu'].items():
            print(f"  - {item['label']} ({key}): {', '.join(item['roles'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating menu settings: {e}")
        return False
    finally:
        client.close()

if __name__ == '__main__':
    asyncio.run(populate_real_menu_settings())