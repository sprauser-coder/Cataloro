#!/usr/bin/env python3
"""
CATALORO - CENTRALIZED ADMIN USER FIX
====================================
Uses centralized configuration from get_paths()["app_root"]/directions
"""

import asyncio
import sys
import os

# Add current directory to path to import config_loader
sys.path.append('get_paths()["app_root"]')
from config_loader import get_config, get_database_url, get_admin_credentials

from motor.motor_asyncio import AsyncIOMotorClient

async def fix_admin_user():
    """Fix admin user authentication using centralized config"""
    
    print("=== CATALORO ADMIN USER FIX ===")
    print("Using centralized configuration from get_paths()["app_root"]/directions")
    print()
    
    # Get configuration
    mongo_url = get_database_url()
    db_name = get_config('DB_NAME', 'get_config("DB_NAME")')
    admin_email, admin_password = get_admin_credentials()
    
    print(f"📍 Database URL: {mongo_url}")
    print(f"📍 Database Name: {db_name}")
    print(f"📍 Admin Email: {admin_email}")
    print()
    
    try:
        # Connect to database
        print("🔌 Connecting to MongoDB...")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Find admin user
        print("🔍 Looking for admin user...")
        admin_user = await db.users.find_one({'email': admin_email})
        
        if admin_user:
            print(f"✅ Found admin user: {admin_user.get('full_name', 'Unknown')}")
            print(f"   Current is_blocked: {admin_user.get('is_blocked')}")
            print(f"   Current is_active: {admin_user.get('is_active')}")
            print(f"   User ID: {admin_user.get('id')}")
            
            # Update admin user to ensure access
            print()
            print("🔧 Updating admin user...")
            result = await db.users.update_one(
                {'email': admin_email},
                {'$set': {
                    'is_blocked': False,
                    'is_active': True,
                    'role': 'admin'
                }}
            )
            
            print(f"📝 Modified {result.modified_count} document(s)")
            
            # Verify the update
            print()
            print("✅ Verifying update...")
            updated_user = await db.users.find_one({'email': admin_email})
            print(f"   Final is_blocked: {updated_user.get('is_blocked')}")
            print(f"   Final is_active: {updated_user.get('is_active')}")
            print(f"   Final role: {updated_user.get('role')}")
            
            if not updated_user.get('is_blocked') and updated_user.get('is_active'):
                print()
                print("🎉 SUCCESS: Admin user is now properly configured!")
                print("   ✓ is_blocked = False")
                print("   ✓ is_active = True") 
                print("   ✓ role = admin")
            else:
                print()
                print("⚠️  WARNING: Admin user may still have issues")
                
        else:
            print("❌ Admin user not found in database!")
            print(f"   Searched for email: {admin_email}")
            print(f"   Database: {db_name}")
            
            # List all users for debugging
            print()
            print("📋 All users in database:")
            all_users = await db.users.find({}, {'email': 1, 'role': 1, 'is_blocked': 1}).to_list(None)
            for user in all_users:
                print(f"   - {user.get('email')} (role: {user.get('role')}, blocked: {user.get('is_blocked')})")
        
        client.close()
        print()
        print("🔚 Admin fix completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

async def test_admin_login():
    """Test admin login after fix"""
    print()
    print("=== TESTING ADMIN LOGIN ===")
    
    # This would typically make an HTTP request to test login
    # For now, just confirm the configuration
    backend_url = get_config('BACKEND_URL_PRODUCTION')
    admin_email, admin_password = get_admin_credentials()
    
    print(f"🌐 Backend URL: {backend_url}")
    print(f"📧 Admin Email: {admin_email}")
    print(f"🔑 Admin Password: {'*' * len(admin_password)}")
    print()
    print("💡 To test login manually, run:")
    print(f'   curl -X POST "{backend_url}/api/auth/login" \\')
    print('     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"email": "{admin_email}", "password": "{admin_password}"}}\'')

if __name__ == "__main__":
    print("Starting admin user fix with centralized configuration...")
    
    # Run the admin fix
    success = asyncio.run(fix_admin_user())
    
    if success:
        # Test configuration
        asyncio.run(test_admin_login())
    else:
        print("❌ Admin fix failed!")
        sys.exit(1)