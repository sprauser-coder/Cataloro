"""
Database Optimization Script for Cataloro Marketplace
Adds critical indexes and optimizes database performance
"""

import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def optimize_database():
    """Add critical indexes to improve database performance"""
    
    # Connect to MongoDB
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.cataloro_marketplace
    
    print("🔧 Starting database optimization...")
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Add indexes for listings collection
        print("📊 Adding indexes for listings collection...")
        await db.listings.create_index("seller_id")
        await db.listings.create_index("status") 
        await db.listings.create_index("created_at")
        await db.listings.create_index([("seller_id", 1), ("status", 1)])
        await db.listings.create_index([("status", 1), ("created_at", -1)])
        print("✅ Listings indexes created")
        
        # Add indexes for tenders collection
        print("📊 Adding indexes for tenders collection...")
        await db.tenders.create_index("listing_id")
        await db.tenders.create_index("bidder_id")
        await db.tenders.create_index("status")
        await db.tenders.create_index("created_at")
        await db.tenders.create_index([("listing_id", 1), ("status", 1)])
        print("✅ Tenders indexes created")
        
        # Add indexes for user_messages collection
        print("📊 Adding indexes for user_messages collection...")
        await db.user_messages.create_index("sender_id")
        await db.user_messages.create_index("recipient_id")
        await db.user_messages.create_index("created_at")
        await db.user_messages.create_index([("sender_id", 1), ("created_at", -1)])
        await db.user_messages.create_index([("recipient_id", 1), ("created_at", -1)])
        print("✅ User messages indexes created")
        
        # Add indexes for ads collection
        print("📊 Adding indexes for ads collection...")
        await db.ads.create_index("is_active")
        await db.ads.create_index("expires_at")
        await db.ads.create_index("created_at")
        print("✅ Ads indexes created")
        
        # Add indexes for deals collection
        print("📊 Adding indexes for deals collection...")
        await db.deals.create_index("buyer_id")
        await db.deals.create_index("seller_id")
        await db.deals.create_index("status")
        await db.deals.create_index("created_at")
        print("✅ Deals indexes created")
        
        # Show existing indexes
        print("\n📋 Current indexes:")
        collections = ['listings', 'tenders', 'user_messages', 'ads', 'deals']
        for collection_name in collections:
            collection = getattr(db, collection_name)
            indexes = await collection.list_indexes().to_list(length=None)
            print(f"\n{collection_name}:")
            for index in indexes:
                print(f"  - {index.get('name', 'unnamed')}: {index.get('key', {})}")
        
        print("\n✅ Database optimization completed successfully!")
        
    except Exception as e:
        print(f"❌ Database optimization failed: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(optimize_database())