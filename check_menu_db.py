#!/usr/bin/env python3
"""
Check Menu Settings Database State
"""

import asyncio
import motor.motor_asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def check_menu_settings():
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.cataloro_marketplace
    
    try:
        # Check if menu_settings collection exists and has data
        menu_settings = await db.menu_settings.find_one({'type': 'menu_config'})
        print('Menu Settings in Database:')
        if menu_settings:
            desktop_menu = menu_settings.get('desktop_menu', {})
            mobile_menu = menu_settings.get('mobile_menu', {})
            print(f'Desktop menu items: {len(desktop_menu)}')
            print(f'Mobile menu items: {len(mobile_menu)}')
            print('Desktop items:', list(desktop_menu.keys()))
            print('Mobile items:', list(mobile_menu.keys()))
            
            # Show sample structure
            if desktop_menu:
                first_item = list(desktop_menu.keys())[0]
                print(f'Sample desktop item structure ({first_item}):')
                print(json.dumps(desktop_menu[first_item], indent=2))
        else:
            print('No menu settings found in database')
            
            # Check if collection exists at all
            collections = await db.list_collection_names()
            if 'menu_settings' in collections:
                print('menu_settings collection exists but is empty')
                # Get all documents
                all_docs = await db.menu_settings.find({}).to_list(length=None)
                print(f'Total documents in menu_settings: {len(all_docs)}')
                for doc in all_docs:
                    print(f'Document type: {doc.get("type", "unknown")}')
            else:
                print('menu_settings collection does not exist')
    
    except Exception as e:
        print(f'Error checking menu settings: {e}')
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_menu_settings())