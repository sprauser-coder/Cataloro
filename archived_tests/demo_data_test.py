#!/usr/bin/env python3
"""
Demo Data Creation and Verification Test
Creates demo listings and messages data for testing the My Listings functionality
"""

import asyncio
import aiohttp
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://market-refactor-1.preview.emergentagent.com/api"

# Demo User Configuration (from review request)
DEMO_USER_ID = "68bfff790e4e46bc28d43631"
DEMO_USER_EMAIL = "user@cataloro.com"

class DemoDataTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_user_data = None
        self.admin_user_data = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
            if headers:
                request_kwargs['headers'] = headers
            
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **request_kwargs) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "response_time_ms": response_time_ms,
                    "data": response_data,
                    "status": response.status
                }
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time_ms,
                "error": str(e),
                "status": 0
            }
    
    async def verify_database_state(self) -> Dict:
        """Check the current state of the listings and users collections"""
        print("🔍 Verifying database state...")
        
        # Check demo user exists
        print("  Checking demo user...")
        demo_login = await self.make_request("/auth/login", "POST", data={
            "email": DEMO_USER_EMAIL,
            "password": "demo123"
        })
        
        if demo_login["success"]:
            self.demo_user_data = demo_login["data"]["user"]
            demo_user_id = self.demo_user_data.get("id")
            print(f"    ✅ Demo user found: {demo_user_id}")
            print(f"    📧 Email: {self.demo_user_data.get('email')}")
            print(f"    👤 Username: {self.demo_user_data.get('username')}")
            
            # Verify the user ID matches expected
            id_matches = demo_user_id == DEMO_USER_ID
            print(f"    🆔 ID matches expected: {id_matches} ({demo_user_id})")
        else:
            print(f"    ❌ Demo user login failed: {demo_login.get('error')}")
            return {
                "demo_user_exists": False,
                "error": demo_login.get("error")
            }
        
        # Check admin user exists
        print("  Checking admin user...")
        admin_login = await self.make_request("/auth/login", "POST", data={
            "email": "admin@cataloro.com",
            "password": "admin123"
        })
        
        if admin_login["success"]:
            self.admin_user_data = admin_login["data"]["user"]
            admin_user_id = self.admin_user_data.get("id")
            print(f"    ✅ Admin user found: {admin_user_id}")
            print(f"    📧 Email: {self.admin_user_data.get('email')}")
            print(f"    👤 Username: {self.admin_user_data.get('username')}")
        else:
            print(f"    ❌ Admin user login failed: {admin_login.get('error')}")
        
        # Check current listings count
        print("  Checking current listings...")
        browse_result = await self.make_request("/marketplace/browse")
        
        if browse_result["success"]:
            current_listings = browse_result["data"]
            print(f"    📋 Total listings in database: {len(current_listings)}")
            
            # Check demo user's current listings
            demo_listings = [l for l in current_listings if l.get("seller_id") == DEMO_USER_ID]
            print(f"    👤 Demo user's current listings: {len(demo_listings)}")
            
            # Check admin user's current listings if admin exists
            admin_listings = []
            if self.admin_user_data:
                admin_user_id = self.admin_user_data.get("id")
                admin_listings = [l for l in current_listings if l.get("seller_id") == admin_user_id]
                print(f"    🔧 Admin user's current listings: {len(admin_listings)}")
        else:
            print(f"    ❌ Failed to browse listings: {browse_result.get('error')}")
            current_listings = []
            demo_listings = []
            admin_listings = []
        
        # Check my-listings endpoint specifically
        print("  Checking my-listings endpoint...")
        my_listings_result = await self.make_request(f"/user/my-listings/{DEMO_USER_ID}")
        
        if my_listings_result["success"]:
            my_listings_data = my_listings_result["data"]
            print(f"    📊 My-listings endpoint returns: {len(my_listings_data)} listings")
        else:
            print(f"    ❌ My-listings endpoint failed: {my_listings_result.get('error')}")
            my_listings_data = []
        
        # Check messages collection
        print("  Checking messages...")
        messages_result = await self.make_request(f"/user/{DEMO_USER_ID}/messages")
        
        if messages_result["success"]:
            messages_data = messages_result["data"]
            print(f"    💬 Demo user's messages: {len(messages_data)}")
        else:
            print(f"    ❌ Messages endpoint failed: {messages_result.get('error')}")
            messages_data = []
        
        return {
            "demo_user_exists": demo_login["success"],
            "demo_user_id": self.demo_user_data.get("id") if self.demo_user_data else None,
            "demo_user_id_matches": demo_user_id == DEMO_USER_ID if demo_login["success"] else False,
            "admin_user_exists": admin_login["success"],
            "admin_user_id": self.admin_user_data.get("id") if self.admin_user_data else None,
            "total_listings": len(current_listings),
            "demo_user_listings": len(demo_listings),
            "admin_user_listings": len(admin_listings),
            "my_listings_endpoint_working": my_listings_result["success"],
            "my_listings_count": len(my_listings_data),
            "messages_endpoint_working": messages_result["success"],
            "messages_count": len(messages_data),
            "database_empty": len(current_listings) == 0
        }
    
    async def create_demo_listings(self) -> Dict:
        """Create demo listings for testing"""
        print("📝 Creating demo listings...")
        
        if not self.demo_user_data:
            return {"error": "Demo user not available"}
        
        demo_user_id = self.demo_user_data.get("id")
        admin_user_id = self.admin_user_data.get("id") if self.admin_user_data else None
        
        # Demo listings for demo user
        demo_listings_data = [
            {
                "title": "BMW 320d Catalytic Converter",
                "description": "High-quality catalytic converter from BMW 320d. Excellent condition with minimal wear. Perfect for replacement or recycling.",
                "price": 150.0,
                "category": "Catalysts",
                "condition": "Used",
                "seller_id": demo_user_id,
                "images": ["/api/placeholder-image.jpg"],
                "tags": ["BMW", "320d", "catalytic", "converter"],
                "features": ["OEM Part", "Tested", "Warranty Included"],
                "status": "active"
            },
            {
                "title": "Mercedes E-Class Catalyst Unit",
                "description": "Original Mercedes E-Class catalytic converter. Removed from 2018 model. Contains precious metals suitable for recycling.",
                "price": 220.0,
                "category": "Catalysts", 
                "condition": "Used",
                "seller_id": demo_user_id,
                "images": ["/api/placeholder-image.jpg"],
                "tags": ["Mercedes", "E-Class", "catalyst", "precious metals"],
                "features": ["Original Part", "2018 Model", "High Metal Content"],
                "status": "active"
            },
            {
                "title": "Audi A4 Exhaust Catalyst",
                "description": "Audi A4 catalytic converter in good working condition. Suitable for both replacement and metal recovery.",
                "price": 180.0,
                "category": "Catalysts",
                "condition": "Good",
                "seller_id": demo_user_id,
                "images": ["/api/placeholder-image.jpg"],
                "tags": ["Audi", "A4", "exhaust", "catalyst"],
                "features": ["Good Condition", "Working Order", "Metal Recovery"],
                "status": "active"
            },
            {
                "title": "Ford Focus Catalytic Converter Set",
                "description": "Complete set of catalytic converters from Ford Focus. Both primary and secondary units included.",
                "price": 95.0,
                "category": "Automotive",
                "condition": "Used",
                "seller_id": demo_user_id,
                "images": ["/api/placeholder-image.jpg"],
                "tags": ["Ford", "Focus", "complete set", "primary", "secondary"],
                "features": ["Complete Set", "Both Units", "Ford Original"],
                "status": "active"
            },
            {
                "title": "Toyota Prius Hybrid Catalyst",
                "description": "Specialized hybrid catalytic converter from Toyota Prius. Higher precious metal content due to hybrid technology.",
                "price": 280.0,
                "category": "Catalysts",
                "condition": "Excellent",
                "seller_id": demo_user_id,
                "images": ["/api/placeholder-image.jpg"],
                "tags": ["Toyota", "Prius", "hybrid", "high value"],
                "features": ["Hybrid Technology", "High Metal Content", "Excellent Condition"],
                "status": "active"
            },
            {
                "title": "Volkswagen Golf Catalyst - SOLD",
                "description": "Volkswagen Golf catalytic converter - This item has been sold to demonstrate sold listings.",
                "price": 120.0,
                "category": "Catalysts",
                "condition": "Used",
                "seller_id": demo_user_id,
                "images": ["/api/placeholder-image.jpg"],
                "tags": ["Volkswagen", "Golf", "sold"],
                "features": ["Sold Item", "Demo Purpose"],
                "status": "sold"
            },
            {
                "title": "Honda Civic Exhaust System Parts",
                "description": "Various exhaust system parts from Honda Civic including catalytic converter and related components.",
                "price": 75.0,
                "category": "Automotive",
                "condition": "Fair",
                "seller_id": demo_user_id,
                "images": ["/api/placeholder-image.jpg"],
                "tags": ["Honda", "Civic", "exhaust", "parts"],
                "features": ["Multiple Parts", "Fair Condition", "Honda Original"],
                "status": "active"
            }
        ]
        
        # Admin listings (if admin user exists)
        admin_listings_data = []
        if admin_user_id:
            admin_listings_data = [
                {
                    "title": "Premium Platinum Catalyst Collection",
                    "description": "High-grade catalytic converters with premium platinum content. Admin-curated collection for serious buyers.",
                    "price": 450.0,
                    "category": "Catalysts",
                    "condition": "Excellent",
                    "seller_id": admin_user_id,
                    "images": ["/api/placeholder-image.jpg"],
                    "tags": ["premium", "platinum", "admin", "collection"],
                    "features": ["Admin Curated", "Premium Grade", "High Platinum"],
                    "status": "active"
                },
                {
                    "title": "Luxury Vehicle Catalyst Bundle",
                    "description": "Catalytic converters from luxury vehicles. Perfect for high-end recycling operations.",
                    "price": 380.0,
                    "category": "Catalysts",
                    "condition": "Good",
                    "seller_id": admin_user_id,
                    "images": ["/api/placeholder-image.jpg"],
                    "tags": ["luxury", "bundle", "admin", "high-end"],
                    "features": ["Luxury Vehicles", "Bundle Deal", "Admin Verified"],
                    "status": "active"
                },
                {
                    "title": "Rare Catalyst Sample - SOLD",
                    "description": "Rare catalytic converter sample for testing purposes. This item has been sold.",
                    "price": 200.0,
                    "category": "Catalysts",
                    "condition": "Used",
                    "seller_id": admin_user_id,
                    "images": ["/api/placeholder-image.jpg"],
                    "tags": ["rare", "sample", "admin", "sold"],
                    "features": ["Rare Sample", "Testing Purpose", "Admin Item"],
                    "status": "sold"
                }
            ]
        
        # Create demo user listings
        created_demo_listings = []
        print(f"  Creating {len(demo_listings_data)} listings for demo user...")
        
        for i, listing_data in enumerate(demo_listings_data):
            # Add unique ID and timestamps
            listing_data["id"] = str(uuid.uuid4())
            listing_data["created_at"] = (datetime.now() - timedelta(days=i)).isoformat()
            
            result = await self.make_request("/listings", "POST", data=listing_data)
            if result["success"]:
                created_demo_listings.append(result["data"])
                print(f"    ✅ Created: {listing_data['title']}")
            else:
                print(f"    ❌ Failed to create: {listing_data['title']} - {result.get('error')}")
        
        # Create admin listings
        created_admin_listings = []
        if admin_user_id and admin_listings_data:
            print(f"  Creating {len(admin_listings_data)} listings for admin user...")
            
            for i, listing_data in enumerate(admin_listings_data):
                # Add unique ID and timestamps
                listing_data["id"] = str(uuid.uuid4())
                listing_data["created_at"] = (datetime.now() - timedelta(days=i+10)).isoformat()
                
                result = await self.make_request("/listings", "POST", data=listing_data)
                if result["success"]:
                    created_admin_listings.append(result["data"])
                    print(f"    ✅ Created: {listing_data['title']}")
                else:
                    print(f"    ❌ Failed to create: {listing_data['title']} - {result.get('error')}")
        
        return {
            "demo_listings_created": len(created_demo_listings),
            "admin_listings_created": len(created_admin_listings),
            "total_listings_created": len(created_demo_listings) + len(created_admin_listings),
            "demo_listings": created_demo_listings,
            "admin_listings": created_admin_listings
        }
    
    async def create_demo_bids(self) -> Dict:
        """Create some demo bids on listings to test bid functionality"""
        print("💰 Creating demo bids...")
        
        if not self.demo_user_data or not self.admin_user_data:
            print("  ⚠️ Skipping bid creation - need both demo and admin users")
            return {"bids_created": 0, "reason": "Missing users"}
        
        demo_user_id = self.demo_user_data.get("id")
        admin_user_id = self.admin_user_data.get("id")
        
        # Get current listings to bid on
        browse_result = await self.make_request("/marketplace/browse")
        if not browse_result["success"]:
            return {"error": "Failed to get listings for bidding"}
        
        listings = browse_result["data"]
        
        # Find listings to bid on (demo user bids on admin listings, admin bids on demo listings)
        demo_listings = [l for l in listings if l.get("seller_id") == demo_user_id and l.get("status") == "active"]
        admin_listings = [l for l in listings if l.get("seller_id") == admin_user_id and l.get("status") == "active"]
        
        created_bids = []
        
        # Admin bids on demo listings
        for listing in demo_listings[:3]:  # Bid on first 3 demo listings
            listing_id = listing.get("id")
            starting_price = listing.get("price", 100)
            bid_amount = starting_price + 25  # Bid 25 more than starting price
            
            bid_data = {
                "listing_id": listing_id,
                "buyer_id": admin_user_id,
                "offer_amount": bid_amount,
                "message": f"Admin bid on {listing.get('title', 'listing')}"
            }
            
            result = await self.make_request("/tenders/submit", "POST", data=bid_data)
            if result["success"]:
                created_bids.append({
                    "listing_title": listing.get("title"),
                    "bidder": "admin",
                    "amount": bid_amount,
                    "bid_id": result["data"].get("tender_id")
                })
                print(f"    ✅ Admin bid ${bid_amount} on '{listing.get('title')}'")
            else:
                print(f"    ❌ Failed admin bid on '{listing.get('title')}': {result.get('error')}")
        
        # Demo user bids on admin listings
        for listing in admin_listings[:2]:  # Bid on first 2 admin listings
            listing_id = listing.get("id")
            starting_price = listing.get("price", 100)
            bid_amount = starting_price + 50  # Bid 50 more than starting price
            
            bid_data = {
                "listing_id": listing_id,
                "buyer_id": demo_user_id,
                "offer_amount": bid_amount,
                "message": f"Demo user bid on {listing.get('title', 'listing')}"
            }
            
            result = await self.make_request("/tenders/submit", "POST", data=bid_data)
            if result["success"]:
                created_bids.append({
                    "listing_title": listing.get("title"),
                    "bidder": "demo",
                    "amount": bid_amount,
                    "bid_id": result["data"].get("tender_id")
                })
                print(f"    ✅ Demo bid ${bid_amount} on '{listing.get('title')}'")
            else:
                print(f"    ❌ Failed demo bid on '{listing.get('title')}': {result.get('error')}")
        
        return {
            "bids_created": len(created_bids),
            "bid_details": created_bids
        }
    
    async def create_demo_messages(self) -> Dict:
        """Create demo messages for testing messaging functionality"""
        print("💬 Creating demo messages...")
        
        if not self.demo_user_data or not self.admin_user_data:
            print("  ⚠️ Skipping message creation - need both demo and admin users")
            return {"messages_created": 0, "reason": "Missing users"}
        
        demo_user_id = self.demo_user_data.get("id")
        admin_user_id = self.admin_user_data.get("id")
        
        # Create conversation between demo user and admin
        messages_data = [
            {
                "sender_id": demo_user_id,
                "recipient_id": admin_user_id,
                "subject": "Question about BMW Catalytic Converter",
                "message": "Hi, I'm interested in your BMW catalytic converter listing. Can you provide more details about the condition?",
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                "sender_id": admin_user_id,
                "recipient_id": demo_user_id,
                "subject": "Re: Question about BMW Catalytic Converter",
                "message": "Hello! The BMW catalytic converter is in excellent condition. It was removed from a 2019 model with only 45,000 miles. All precious metals are intact.",
                "created_at": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat()
            },
            {
                "sender_id": demo_user_id,
                "recipient_id": admin_user_id,
                "subject": "Re: Question about BMW Catalytic Converter",
                "message": "That sounds great! What's your best price for this item? I'm a serious buyer.",
                "created_at": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            {
                "sender_id": admin_user_id,
                "recipient_id": demo_user_id,
                "subject": "Re: Question about BMW Catalytic Converter",
                "message": "I can offer it for $140 if you're ready to purchase today. This includes free local pickup.",
                "created_at": (datetime.now() - timedelta(minutes=30)).isoformat()
            },
            {
                "sender_id": demo_user_id,
                "recipient_id": admin_user_id,
                "subject": "Inquiry about Platinum Collection",
                "message": "I saw your premium platinum catalyst collection. Do you have certificates of analysis for the metal content?",
                "created_at": (datetime.now() - timedelta(days=1)).isoformat()
            }
        ]
        
        created_messages = []
        
        for message_data in messages_data:
            # Add unique ID
            message_data["id"] = str(uuid.uuid4())
            
            # Create message for sender
            sender_result = await self.make_request(f"/user/{message_data['sender_id']}/messages", "POST", data=message_data)
            
            if sender_result["success"]:
                created_messages.append({
                    "message_id": message_data["id"],
                    "from": "demo" if message_data["sender_id"] == demo_user_id else "admin",
                    "to": "admin" if message_data["recipient_id"] == admin_user_id else "demo",
                    "subject": message_data["subject"]
                })
                print(f"    ✅ Created message: {message_data['subject'][:50]}...")
            else:
                print(f"    ❌ Failed to create message: {sender_result.get('error')}")
        
        return {
            "messages_created": len(created_messages),
            "message_details": created_messages
        }
    
    async def verify_endpoints(self) -> Dict:
        """Verify that all endpoints work correctly with the new data"""
        print("🔍 Verifying endpoints with new data...")
        
        if not self.demo_user_data:
            return {"error": "Demo user not available"}
        
        demo_user_id = self.demo_user_data.get("id")
        
        # Test my-listings endpoint
        print("  Testing my-listings endpoint...")
        my_listings_result = await self.make_request(f"/user/my-listings/{demo_user_id}")
        
        if my_listings_result["success"]:
            my_listings = my_listings_result["data"]
            print(f"    ✅ My-listings returns {len(my_listings)} listings")
            
            # Check for different statuses
            active_listings = [l for l in my_listings if l.get("status") == "active"]
            sold_listings = [l for l in my_listings if l.get("status") == "sold"]
            
            print(f"    📊 Active listings: {len(active_listings)}")
            print(f"    📊 Sold listings: {len(sold_listings)}")
        else:
            print(f"    ❌ My-listings failed: {my_listings_result.get('error')}")
            my_listings = []
        
        # Test browse endpoint
        print("  Testing browse endpoint...")
        browse_result = await self.make_request("/marketplace/browse")
        
        if browse_result["success"]:
            all_listings = browse_result["data"]
            print(f"    ✅ Browse returns {len(all_listings)} total listings")
            
            # Check for demo user listings in browse
            demo_in_browse = [l for l in all_listings if l.get("seller_id") == demo_user_id]
            print(f"    📊 Demo user listings in browse: {len(demo_in_browse)}")
        else:
            print(f"    ❌ Browse failed: {browse_result.get('error')}")
            all_listings = []
        
        # Test messages endpoint
        print("  Testing messages endpoint...")
        messages_result = await self.make_request(f"/user/{demo_user_id}/messages")
        
        if messages_result["success"]:
            messages = messages_result["data"]
            print(f"    ✅ Messages returns {len(messages)} conversations")
        else:
            print(f"    ❌ Messages failed: {messages_result.get('error')}")
            messages = []
        
        # Test individual listing endpoints
        print("  Testing individual listing endpoints...")
        if my_listings:
            test_listing = my_listings[0]
            listing_id = test_listing.get("id")
            
            listing_detail_result = await self.make_request(f"/listings/{listing_id}")
            if listing_detail_result["success"]:
                print(f"    ✅ Individual listing detail working")
            else:
                print(f"    ❌ Individual listing detail failed: {listing_detail_result.get('error')}")
            
            # Test tenders endpoint
            tenders_result = await self.make_request(f"/listings/{listing_id}/tenders")
            if tenders_result["success"]:
                tenders = tenders_result["data"]
                print(f"    ✅ Tenders endpoint returns {len(tenders)} bids")
            else:
                print(f"    ❌ Tenders endpoint failed: {tenders_result.get('error')}")
        
        return {
            "my_listings_working": my_listings_result["success"],
            "my_listings_count": len(my_listings),
            "browse_working": browse_result["success"],
            "browse_total_count": len(all_listings),
            "demo_listings_in_browse": len([l for l in all_listings if l.get("seller_id") == demo_user_id]) if browse_result["success"] else 0,
            "messages_working": messages_result["success"],
            "messages_count": len(messages),
            "all_endpoints_working": my_listings_result["success"] and browse_result["success"] and messages_result["success"]
        }
    
    async def run_comprehensive_demo_data_test(self) -> Dict:
        """Run complete demo data creation and verification test"""
        print("🚀 Starting Demo Data Creation and Verification Test")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Step 1: Verify current database state
            print("\n📋 STEP 1: Database State Verification")
            print("-" * 40)
            db_state = await self.verify_database_state()
            
            # Step 2: Create demo listings
            print("\n📝 STEP 2: Demo Listings Creation")
            print("-" * 40)
            listings_result = await self.create_demo_listings()
            
            # Step 3: Create demo bids
            print("\n💰 STEP 3: Demo Bids Creation")
            print("-" * 40)
            bids_result = await self.create_demo_bids()
            
            # Step 4: Create demo messages
            print("\n💬 STEP 4: Demo Messages Creation")
            print("-" * 40)
            messages_result = await self.create_demo_messages()
            
            # Step 5: Verify endpoints work
            print("\n🔍 STEP 5: Endpoint Verification")
            print("-" * 40)
            verification_result = await self.verify_endpoints()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "database_state": db_state,
                "listings_creation": listings_result,
                "bids_creation": bids_result,
                "messages_creation": messages_result,
                "endpoint_verification": verification_result
            }
            
            # Calculate success metrics
            demo_data_created = (
                listings_result.get("demo_listings_created", 0) > 0 and
                messages_result.get("messages_created", 0) > 0
            )
            
            endpoints_working = verification_result.get("all_endpoints_working", False)
            my_listings_populated = verification_result.get("my_listings_count", 0) > 0
            
            all_results["summary"] = {
                "demo_user_verified": db_state.get("demo_user_exists", False),
                "demo_user_id_correct": db_state.get("demo_user_id_matches", False),
                "demo_data_created_successfully": demo_data_created,
                "demo_listings_created": listings_result.get("demo_listings_created", 0),
                "admin_listings_created": listings_result.get("admin_listings_created", 0),
                "demo_bids_created": bids_result.get("bids_created", 0),
                "demo_messages_created": messages_result.get("messages_created", 0),
                "my_listings_now_populated": my_listings_populated,
                "my_listings_count": verification_result.get("my_listings_count", 0),
                "all_endpoints_working": endpoints_working,
                "test_successful": demo_data_created and endpoints_working and my_listings_populated
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Run the demo data test"""
    tester = DemoDataTester()
    results = await tester.run_comprehensive_demo_data_test()
    
    print("\n" + "=" * 70)
    print("📊 DEMO DATA TEST RESULTS SUMMARY")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"✅ Demo User Verified: {summary.get('demo_user_verified', False)}")
    print(f"✅ Demo User ID Correct: {summary.get('demo_user_id_correct', False)}")
    print(f"✅ Demo Listings Created: {summary.get('demo_listings_created', 0)}")
    print(f"✅ Admin Listings Created: {summary.get('admin_listings_created', 0)}")
    print(f"✅ Demo Bids Created: {summary.get('demo_bids_created', 0)}")
    print(f"✅ Demo Messages Created: {summary.get('demo_messages_created', 0)}")
    print(f"✅ My Listings Now Populated: {summary.get('my_listings_now_populated', False)}")
    print(f"✅ My Listings Count: {summary.get('my_listings_count', 0)}")
    print(f"✅ All Endpoints Working: {summary.get('all_endpoints_working', False)}")
    
    overall_success = summary.get('test_successful', False)
    print(f"\n🎯 OVERALL TEST SUCCESS: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    
    if not overall_success:
        print("\n❌ Issues Found:")
        if not summary.get('demo_user_verified', False):
            print("  - Demo user not found or login failed")
        if not summary.get('demo_data_created_successfully', False):
            print("  - Failed to create demo data")
        if not summary.get('my_listings_now_populated', False):
            print("  - My Listings endpoint still empty")
        if not summary.get('all_endpoints_working', False):
            print("  - Some endpoints not working correctly")
    
    # Save detailed results
    with open('/app/demo_data_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/demo_data_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())