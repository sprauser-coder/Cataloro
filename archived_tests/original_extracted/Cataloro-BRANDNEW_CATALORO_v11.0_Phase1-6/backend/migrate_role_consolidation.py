#!/usr/bin/env python3
"""
Role Consolidation Migration Script
Consolidates legacy 'role' field into 'user_role' field for all users
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

async def migrate_user_roles():
    """Migrate all users from legacy role field to user_role field"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        db = client.cataloro_marketplace
        
        print("🔄 Starting user role consolidation migration...")
        
        # Get all users
        users = await db.users.find({}).to_list(length=None)
        print(f"📊 Found {len(users)} users to process")
        
        migration_count = 0
        
        for user in users:
            user_id = user.get('id')
            current_user_role = user.get('user_role')
            legacy_role = user.get('role')
            
            # Determine the consolidated role
            consolidated_role = None
            
            if current_user_role:
                # User already has RBAC role, keep it
                consolidated_role = current_user_role
            elif legacy_role:
                # Migrate legacy role to RBAC format
                if legacy_role == 'admin':
                    consolidated_role = 'Admin'
                elif legacy_role == 'seller':
                    consolidated_role = 'User-Seller'
                elif legacy_role == 'buyer':
                    consolidated_role = 'User-Buyer'
                else:
                    consolidated_role = 'User-Buyer'  # Default for unknown roles
            else:
                # No role specified, set default
                consolidated_role = 'User-Buyer'
            
            # Update user record
            update_data = {
                'user_role': consolidated_role
            }
            
            # Remove legacy role field if it exists
            unset_data = {}
            if 'role' in user:
                unset_data['role'] = ""
            
            # Perform the update
            update_query = {'$set': update_data}
            if unset_data:
                update_query['$unset'] = unset_data
            
            result = await db.users.update_one(
                {'id': user_id},
                update_query
            )
            
            if result.modified_count > 0:
                migration_count += 1
                print(f"✅ Migrated user {user.get('username', user_id)}: {legacy_role or 'none'} → {consolidated_role}")
            
        print(f"\n🎉 Migration completed successfully!")
        print(f"📈 Total users migrated: {migration_count}/{len(users)}")
        
        # Verify migration
        print("\n🔍 Verifying migration results...")
        role_counts = {}
        users_after = await db.users.find({}).to_list(length=None)
        
        for user in users_after:
            user_role = user.get('user_role', 'Unknown')
            role_counts[user_role] = role_counts.get(user_role, 0) + 1
            
            # Check if any legacy role fields remain
            if 'role' in user:
                print(f"⚠️  Warning: User {user.get('username')} still has legacy role field: {user.get('role')}")
        
        print("📊 Final role distribution:")
        for role, count in role_counts.items():
            print(f"   {role}: {count} users")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate_user_roles())