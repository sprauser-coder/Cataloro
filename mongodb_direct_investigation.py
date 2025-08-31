#!/usr/bin/env python3
"""
DIRECT MONGODB INVESTIGATION - Database Collections Analysis
Direct database access to identify all collections and their contents
"""

import motor.motor_asyncio
import asyncio
import os
from datetime import datetime
import json

class MongoDBInvestigator:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_url)
            self.db = self.client.cataloro_marketplace
            # Test connection
            await self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    async def list_all_collections(self):
        """List all collections in the database"""
        try:
            collections = await self.db.list_collection_names()
            print(f"\n📊 FOUND {len(collections)} COLLECTIONS:")
            for i, collection in enumerate(collections, 1):
                count = await self.db[collection].count_documents({})
                print(f"   {i}. {collection} ({count} documents)")
            return collections
        except Exception as e:
            print(f"❌ Failed to list collections: {str(e)}")
            return []
    
    async def analyze_listings_collections(self, collections):
        """Analyze all listing-related collections"""
        print(f"\n🔍 ANALYZING LISTING-RELATED COLLECTIONS:")
        
        listing_collections = [col for col in collections if 'listing' in col.lower()]
        
        if not listing_collections:
            print("⚠️  No collections with 'listing' in name found")
            # Check the main collections anyway
            listing_collections = ['listings']
        
        collection_analysis = {}
        
        for collection_name in listing_collections:
            try:
                collection = self.db[collection_name]
                count = await collection.count_documents({})
                
                print(f"\n📋 Collection: {collection_name}")
                print(f"   📊 Total documents: {count}")
                
                if count > 0:
                    # Get sample documents
                    sample_docs = await collection.find({}).limit(3).to_list(length=3)
                    
                    # Analyze structure
                    if sample_docs:
                        sample_doc = sample_docs[0]
                        fields = list(sample_doc.keys())
                        print(f"   🔑 Fields: {fields}")
                        
                        # Check for different ID formats
                        id_formats = set()
                        seller_ids = set()
                        statuses = set()
                        
                        async for doc in collection.find({}).limit(50):
                            if '_id' in doc:
                                id_formats.add(f"_id: {type(doc['_id']).__name__}")
                            if 'id' in doc:
                                id_formats.add(f"id: {type(doc['id']).__name__}")
                            if 'seller_id' in doc:
                                seller_ids.add(doc['seller_id'])
                            if 'status' in doc:
                                statuses.add(doc['status'])
                        
                        print(f"   🆔 ID formats: {list(id_formats)}")
                        print(f"   👤 Unique sellers: {len(seller_ids)}")
                        print(f"   📈 Statuses: {list(statuses)}")
                        
                        # Show sample titles
                        titles = [doc.get('title', 'No title') for doc in sample_docs]
                        print(f"   📝 Sample titles: {titles}")
                
                collection_analysis[collection_name] = {
                    'count': count,
                    'sample_docs': sample_docs if count > 0 else []
                }
                
            except Exception as e:
                print(f"❌ Error analyzing {collection_name}: {str(e)}")
                collection_analysis[collection_name] = {'error': str(e)}
        
        return collection_analysis
    
    async def check_user_specific_collections(self, collections):
        """Check for user-specific listing storage"""
        print(f"\n👥 CHECKING USER-SPECIFIC COLLECTIONS:")
        
        user_collections = [col for col in collections if 'user' in col.lower()]
        
        for collection_name in user_collections:
            try:
                collection = self.db[collection_name]
                count = await collection.count_documents({})
                
                print(f"\n👤 Collection: {collection_name}")
                print(f"   📊 Total documents: {count}")
                
                if count > 0:
                    # Get sample documents
                    sample_docs = await collection.find({}).limit(3).to_list(length=3)
                    
                    if sample_docs:
                        sample_doc = sample_docs[0]
                        fields = list(sample_doc.keys())
                        print(f"   🔑 Fields: {fields}")
                        
                        # Check if this contains listing data
                        if any(field in fields for field in ['title', 'price', 'description', 'item_id']):
                            print(f"   ⚠️  POTENTIAL LISTING DATA FOUND")
                            
                            # Analyze user distribution
                            user_ids = set()
                            async for doc in collection.find({}):
                                if 'user_id' in doc:
                                    user_ids.add(doc['user_id'])
                                elif 'seller_id' in doc:
                                    user_ids.add(doc['seller_id'])
                            
                            print(f"   👥 Unique users: {len(user_ids)}")
                            print(f"   👥 User IDs: {list(user_ids)[:5]}")
            
            except Exception as e:
                print(f"❌ Error analyzing {collection_name}: {str(e)}")
    
    async def cross_reference_collections(self, collection_analysis):
        """Cross-reference data between collections"""
        print(f"\n🔗 CROSS-REFERENCING COLLECTIONS:")
        
        # Get all listing IDs from main listings collection
        main_listings_ids = set()
        try:
            async for doc in self.db.listings.find({}):
                if 'id' in doc:
                    main_listings_ids.add(doc['id'])
                elif '_id' in doc:
                    main_listings_ids.add(str(doc['_id']))
        except Exception as e:
            print(f"❌ Error getting main listings: {str(e)}")
        
        print(f"📋 Main listings collection: {len(main_listings_ids)} unique IDs")
        
        # Check user collections for listings not in main collection
        try:
            # Check users collection for seller_ids
            users = await self.db.users.find({}).to_list(length=None)
            user_ids = [user.get('id', str(user.get('_id', ''))) for user in users]
            
            print(f"👥 Found {len(user_ids)} users")
            
            # For each user, check if they have listings not in main collection
            orphaned_listings = {}
            
            for user_id in user_ids:
                try:
                    # Find listings by this seller in main collection
                    main_user_listings = await self.db.listings.find({'seller_id': user_id}).to_list(length=None)
                    main_user_ids = {doc.get('id', str(doc.get('_id', ''))) for doc in main_user_listings}
                    
                    # Check if there are other collections with this user's data
                    user_specific_listings = set()
                    
                    # Check all collections for this user's listings
                    for collection_name in await self.db.list_collection_names():
                        if collection_name != 'listings':
                            try:
                                user_docs = await self.db[collection_name].find({'seller_id': user_id}).to_list(length=None)
                                for doc in user_docs:
                                    if 'title' in doc and 'price' in doc:  # Looks like a listing
                                        doc_id = doc.get('id', str(doc.get('_id', '')))
                                        user_specific_listings.add(doc_id)
                            except:
                                pass
                    
                    orphaned = user_specific_listings - main_user_ids
                    if orphaned:
                        orphaned_listings[user_id] = orphaned
                        print(f"⚠️  User {user_id}: {len(orphaned)} listings not in main collection")
                
                except Exception as e:
                    print(f"❌ Error checking user {user_id}: {str(e)}")
            
            if orphaned_listings:
                print(f"\n🚨 FOUND ORPHANED LISTINGS:")
                for user_id, orphaned_ids in orphaned_listings.items():
                    print(f"   User {user_id}: {len(orphaned_ids)} orphaned listings")
            else:
                print(f"✅ No orphaned listings found")
                
        except Exception as e:
            print(f"❌ Error in cross-reference: {str(e)}")
    
    async def investigate_status_filtering(self):
        """Investigate if status filtering is causing the issue"""
        print(f"\n📊 INVESTIGATING STATUS FILTERING:")
        
        try:
            # Count listings by status
            pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            status_counts = await self.db.listings.aggregate(pipeline).to_list(length=None)
            
            print(f"📈 Listings by status:")
            for status_doc in status_counts:
                status = status_doc['_id'] or 'null'
                count = status_doc['count']
                print(f"   {status}: {count} listings")
            
            # Check what browse endpoint filters
            active_listings = await self.db.listings.find({"status": "active"}).to_list(length=None)
            all_listings = await self.db.listings.find({}).to_list(length=None)
            
            print(f"\n🔍 Filter Analysis:")
            print(f"   Total listings in DB: {len(all_listings)}")
            print(f"   Active listings: {len(active_listings)}")
            print(f"   Filtered out: {len(all_listings) - len(active_listings)}")
            
            # Check if user listings have different statuses
            non_active_listings = await self.db.listings.find({"status": {"$ne": "active"}}).to_list(length=None)
            if non_active_listings:
                print(f"\n⚠️  NON-ACTIVE LISTINGS FOUND:")
                for listing in non_active_listings[:5]:
                    title = listing.get('title', 'No title')
                    status = listing.get('status', 'No status')
                    seller = listing.get('seller_id', 'No seller')
                    print(f"   '{title}' - Status: {status} - Seller: {seller}")
            
        except Exception as e:
            print(f"❌ Error investigating status filtering: {str(e)}")
    
    async def run_investigation(self):
        """Run complete MongoDB investigation"""
        print("🔍 STARTING DIRECT MONGODB INVESTIGATION")
        print("="*80)
        
        if not await self.connect():
            return False
        
        try:
            # List all collections
            collections = await self.list_all_collections()
            
            # Analyze listing collections
            collection_analysis = await self.analyze_listings_collections(collections)
            
            # Check user-specific collections
            await self.check_user_specific_collections(collections)
            
            # Cross-reference collections
            await self.cross_reference_collections(collection_analysis)
            
            # Investigate status filtering
            await self.investigate_status_filtering()
            
            print(f"\n✅ MONGODB INVESTIGATION COMPLETED")
            return True
            
        except Exception as e:
            print(f"❌ Investigation failed: {str(e)}")
            return False
        finally:
            if self.client:
                self.client.close()

async def main():
    """Main execution function"""
    investigator = MongoDBInvestigator()
    await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())