#!/usr/bin/env python3
from config_loader import get_config, get_backend_url, get_admin_credentials, get_paths, get_database_url
"""
Fix admin account - unblock the admin user
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

async def fix_admin_account():
    """Unblock the admin account"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        # Unblock admin account
        result = await db.users.update_one(
            {"email": "get_admin_credentials()[0]"},
            {"$set": {"is_blocked": False}}
        )
        
        if result.modified_count > 0:
            print("✅ Admin account unblocked successfully")
        else:
            print("⚠️ Admin account was already unblocked or not found")
            
        # Verify the change
        admin_user = await db.users.find_one({"email": "get_admin_credentials()[0]"})
        if admin_user:
            print(f"✅ Admin account status: is_blocked = {admin_user.get('is_blocked', False)}")
        else:
            print("❌ Admin account not found")
            
        client.close()
        
    except Exception as e:
        print(f"❌ Error fixing admin account: {str(e)}")

if __name__ == "__main__":
    asyncio.run(fix_admin_account())