#!/usr/bin/env python3
"""
RBAC Migration Script for Cataloro Marketplace
Migrates existing users to new Role-Based Access Control system
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def migrate_users_to_rbac():
    """Migrate existing users to RBAC system"""
    
    # Connect to MongoDB
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.cataloro_marketplace
    
    print("🚀 Starting RBAC migration for existing users...")
    
    try:
        # Get all users without RBAC fields
        users_cursor = db.users.find({
            "$or": [
                {"user_role": {"$exists": False}},
                {"registration_status": {"$exists": False}},
                {"badge": {"$exists": False}}
            ]
        })
        
        migration_count = 0
        admin_count = 0
        user_count = 0
        
        async for user in users_cursor:
            user_id = user.get('id')
            email = user.get('email', '')
            current_role = user.get('role', 'user')
            
            # Determine new RBAC fields based on existing data
            if current_role == 'admin' or email == 'admin@cataloro.com':
                # Existing admin users
                user_role = "Admin"
                badge = "Admin"
                registration_status = "Approved"
                admin_count += 1
            else:
                # Existing regular users - default to User-Buyer
                user_role = "User-Buyer"
                badge = "Buyer"
                registration_status = "Approved"  # Auto-approve existing users
                user_count += 1
            
            # Update user with RBAC fields
            update_result = await db.users.update_one(
                {"id": user_id},
                {"$set": {
                    "user_role": user_role,
                    "registration_status": registration_status,
                    "badge": badge
                }}
            )
            
            if update_result.modified_count > 0:
                migration_count += 1
                print(f"✅ Migrated user: {user.get('username', 'Unknown')} ({email}) -> {user_role}")
            else:
                print(f"⚠️  No changes for user: {user.get('username', 'Unknown')} ({email})")
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"📊 Migration Summary:")
        print(f"   • Total users migrated: {migration_count}")
        print(f"   • Admin users: {admin_count}")
        print(f"   • Regular users (set to User-Buyer): {user_count}")
        print(f"   • All existing users auto-approved for immediate access")
        
        # Verify migration
        print(f"\n🔍 Verifying migration...")
        total_users = await db.users.count_documents({})
        rbac_users = await db.users.count_documents({
            "user_role": {"$exists": True},
            "registration_status": {"$exists": True},
            "badge": {"$exists": True}
        })
        
        print(f"   • Total users in database: {total_users}")
        print(f"   • Users with RBAC fields: {rbac_users}")
        
        if total_users == rbac_users:
            print("✅ All users successfully migrated to RBAC system!")
        else:
            print("⚠️  Some users may not have been migrated properly")
        
        # Show role distribution
        print(f"\n📈 Role Distribution:")
        for role in ["Admin", "Admin-Manager", "User-Seller", "User-Buyer"]:
            count = await db.users.count_documents({"user_role": role})
            print(f"   • {role}: {count} users")
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False
    finally:
        client.close()
    
    return True

if __name__ == "__main__":
    print("🔧 CATALORO RBAC MIGRATION SCRIPT")
    print("=" * 50)
    
    # Run migration
    success = asyncio.run(migrate_users_to_rbac())
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🚀 The RBAC system is now ready to use.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")