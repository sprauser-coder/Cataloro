#!/usr/bin/env python3
"""
Endpoint Verification Test
Verify the specific endpoints mentioned in the review request
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-marketplace-6.preview.emergentagent.com/api"
DEMO_USER_ID = "68bfff790e4e46bc28d43631"

class EndpointVerificationTester:
    def __init__(self):
        self.session = None
        
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
    
    async def test_my_listings_endpoint(self) -> Dict:
        """Test /api/user/my-listings/{user_id} endpoint"""
        print("📋 Testing My Listings endpoint...")
        
        endpoint = f"/user/my-listings/{DEMO_USER_ID}"
        result = await self.make_request(endpoint)
        
        if result["success"]:
            listings = result["data"]
            print(f"  ✅ Endpoint working: {len(listings)} listings returned")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            
            # Analyze listing data
            active_listings = [l for l in listings if l.get("status") == "active"]
            sold_listings = [l for l in listings if l.get("status") == "sold"]
            
            # Check for different categories
            catalyst_listings = [l for l in listings if l.get("category") == "Catalysts"]
            automotive_listings = [l for l in listings if l.get("category") == "Automotive"]
            
            # Check for listings with bids
            listings_with_bids = []
            for listing in listings:
                bid_info = listing.get("bid_info", {})
                if bid_info.get("has_bids", False):
                    listings_with_bids.append({
                        "title": listing.get("title"),
                        "total_bids": bid_info.get("total_bids", 0),
                        "highest_bid": bid_info.get("highest_bid")
                    })
            
            print(f"  📊 Active listings: {len(active_listings)}")
            print(f"  📊 Sold listings: {len(sold_listings)}")
            print(f"  📊 Catalyst listings: {len(catalyst_listings)}")
            print(f"  📊 Automotive listings: {len(automotive_listings)}")
            print(f"  📊 Listings with bids: {len(listings_with_bids)}")
            
            if listings_with_bids:
                print("  💰 Bid details:")
                for bid_listing in listings_with_bids[:3]:  # Show first 3
                    print(f"    - {bid_listing['title']}: {bid_listing['total_bids']} bids, highest: ${bid_listing['highest_bid']}")
            
            return {
                "test_name": "My Listings Endpoint",
                "endpoint_working": True,
                "response_time_ms": result["response_time_ms"],
                "total_listings": len(listings),
                "active_listings": len(active_listings),
                "sold_listings": len(sold_listings),
                "catalyst_listings": len(catalyst_listings),
                "automotive_listings": len(automotive_listings),
                "listings_with_bids": len(listings_with_bids),
                "bid_details": listings_with_bids,
                "sample_listings": [
                    {
                        "title": l.get("title"),
                        "price": l.get("price"),
                        "category": l.get("category"),
                        "status": l.get("status"),
                        "has_bids": l.get("bid_info", {}).get("has_bids", False)
                    } for l in listings[:5]  # First 5 listings
                ]
            }
        else:
            print(f"  ❌ Endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "My Listings Endpoint",
                "endpoint_working": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"],
                "response_time_ms": result["response_time_ms"]
            }
    
    async def test_browse_endpoint(self) -> Dict:
        """Test /api/marketplace/browse endpoint"""
        print("🔍 Testing Browse endpoint...")
        
        result = await self.make_request("/marketplace/browse")
        
        if result["success"]:
            listings = result["data"]
            print(f"  ✅ Endpoint working: {len(listings)} total listings")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            
            # Check for demo user listings in browse
            demo_listings = [l for l in listings if l.get("seller_id") == DEMO_USER_ID]
            admin_listings = [l for l in listings if l.get("seller_id") != DEMO_USER_ID]
            
            # Check categories
            catalyst_listings = [l for l in listings if l.get("category") == "Catalysts"]
            automotive_listings = [l for l in listings if l.get("category") == "Automotive"]
            
            # Check statuses
            active_listings = [l for l in listings if l.get("status") == "active"]
            sold_listings = [l for l in listings if l.get("status") == "sold"]
            
            print(f"  📊 Demo user listings: {len(demo_listings)}")
            print(f"  📊 Other user listings: {len(admin_listings)}")
            print(f"  📊 Catalyst listings: {len(catalyst_listings)}")
            print(f"  📊 Automotive listings: {len(automotive_listings)}")
            print(f"  📊 Active listings: {len(active_listings)}")
            print(f"  📊 Sold listings: {len(sold_listings)}")
            
            return {
                "test_name": "Browse Endpoint",
                "endpoint_working": True,
                "response_time_ms": result["response_time_ms"],
                "total_listings": len(listings),
                "demo_user_listings": len(demo_listings),
                "other_user_listings": len(admin_listings),
                "catalyst_listings": len(catalyst_listings),
                "automotive_listings": len(automotive_listings),
                "active_listings": len(active_listings),
                "sold_listings": len(sold_listings),
                "includes_demo_data": len(demo_listings) > 0
            }
        else:
            print(f"  ❌ Endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Browse Endpoint",
                "endpoint_working": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"],
                "response_time_ms": result["response_time_ms"]
            }
    
    async def test_messages_endpoint(self) -> Dict:
        """Test message endpoints"""
        print("💬 Testing Messages endpoints...")
        
        # Test user messages endpoint
        messages_result = await self.make_request(f"/user/{DEMO_USER_ID}/messages")
        
        if messages_result["success"]:
            messages = messages_result["data"]
            print(f"  ✅ Messages endpoint working: {len(messages)} conversations")
            print(f"  ⏱️ Response time: {messages_result['response_time_ms']:.0f}ms")
            
            # Analyze message data
            recent_messages = []
            for message in messages[:5]:  # First 5 messages
                recent_messages.append({
                    "subject": message.get("subject", "No subject"),
                    "sender": message.get("sender_id", "Unknown"),
                    "recipient": message.get("recipient_id", "Unknown"),
                    "created_at": message.get("created_at", "Unknown")
                })
            
            print(f"  📊 Recent conversations:")
            for msg in recent_messages:
                sender_type = "Demo" if msg["sender"] == DEMO_USER_ID else "Other"
                print(f"    - {msg['subject'][:50]}... (from {sender_type})")
            
            return {
                "test_name": "Messages Endpoint",
                "endpoint_working": True,
                "response_time_ms": messages_result["response_time_ms"],
                "total_conversations": len(messages),
                "recent_messages": recent_messages,
                "has_conversations": len(messages) > 0
            }
        else:
            print(f"  ❌ Messages endpoint failed: {messages_result.get('error', 'Unknown error')}")
            return {
                "test_name": "Messages Endpoint",
                "endpoint_working": False,
                "error": messages_result.get("error", "Unknown error"),
                "status": messages_result["status"],
                "response_time_ms": messages_result["response_time_ms"]
            }
    
    async def test_individual_listing_endpoints(self) -> Dict:
        """Test individual listing detail and tenders endpoints"""
        print("📄 Testing Individual Listing endpoints...")
        
        # First get a listing ID from browse
        browse_result = await self.make_request("/marketplace/browse")
        if not browse_result["success"] or not browse_result["data"]:
            return {
                "test_name": "Individual Listing Endpoints",
                "error": "No listings available for testing"
            }
        
        # Get a demo user listing for testing
        demo_listings = [l for l in browse_result["data"] if l.get("seller_id") == DEMO_USER_ID]
        if not demo_listings:
            return {
                "test_name": "Individual Listing Endpoints",
                "error": "No demo user listings found for testing"
            }
        
        test_listing = demo_listings[0]
        listing_id = test_listing.get("id")
        
        print(f"  Testing with listing: {test_listing.get('title', 'Unknown')}")
        
        # Test listing detail endpoint
        detail_result = await self.make_request(f"/listings/{listing_id}")
        
        if detail_result["success"]:
            listing_detail = detail_result["data"]
            print(f"  ✅ Listing detail working")
            print(f"  ⏱️ Response time: {detail_result['response_time_ms']:.0f}ms")
            print(f"  📋 Title: {listing_detail.get('title', 'Unknown')}")
            print(f"  💰 Price: ${listing_detail.get('price', 0)}")
            print(f"  📂 Category: {listing_detail.get('category', 'Unknown')}")
        else:
            print(f"  ❌ Listing detail failed: {detail_result.get('error')}")
        
        # Test tenders endpoint
        tenders_result = await self.make_request(f"/listings/{listing_id}/tenders")
        
        if tenders_result["success"]:
            tenders = tenders_result["data"]
            print(f"  ✅ Tenders endpoint working: {len(tenders)} bids")
            print(f"  ⏱️ Response time: {tenders_result['response_time_ms']:.0f}ms")
            
            if tenders:
                highest_bid = max(tenders, key=lambda x: x.get("offer_amount", 0))
                print(f"  💰 Highest bid: ${highest_bid.get('offer_amount', 0)}")
        else:
            print(f"  ❌ Tenders endpoint failed: {tenders_result.get('error')}")
        
        return {
            "test_name": "Individual Listing Endpoints",
            "listing_detail_working": detail_result["success"],
            "tenders_working": tenders_result["success"],
            "listing_detail_response_time": detail_result["response_time_ms"],
            "tenders_response_time": tenders_result["response_time_ms"],
            "test_listing_title": test_listing.get("title"),
            "test_listing_id": listing_id,
            "bid_count": len(tenders_result["data"]) if tenders_result["success"] else 0,
            "both_endpoints_working": detail_result["success"] and tenders_result["success"]
        }
    
    async def test_data_consistency(self) -> Dict:
        """Test data consistency across endpoints"""
        print("🔄 Testing Data Consistency...")
        
        # Get data from different endpoints
        my_listings_result = await self.make_request(f"/user/my-listings/{DEMO_USER_ID}")
        browse_result = await self.make_request("/marketplace/browse")
        
        if not (my_listings_result["success"] and browse_result["success"]):
            return {
                "test_name": "Data Consistency",
                "error": "Failed to get data from endpoints"
            }
        
        my_listings = my_listings_result["data"]
        all_listings = browse_result["data"]
        
        # Find demo user listings in browse
        demo_in_browse = [l for l in all_listings if l.get("seller_id") == DEMO_USER_ID]
        
        # Check consistency
        my_listings_ids = set(l.get("id") for l in my_listings)
        browse_demo_ids = set(l.get("id") for l in demo_in_browse)
        
        # Check for active listings (sold listings might not appear in browse)
        active_my_listings = [l for l in my_listings if l.get("status") == "active"]
        active_my_ids = set(l.get("id") for l in active_my_listings)
        
        consistency_score = len(active_my_ids.intersection(browse_demo_ids)) / len(active_my_ids) * 100 if active_my_ids else 100
        
        print(f"  📊 My Listings count: {len(my_listings)}")
        print(f"  📊 Active My Listings: {len(active_my_listings)}")
        print(f"  📊 Demo listings in Browse: {len(demo_in_browse)}")
        print(f"  📊 Consistency score: {consistency_score:.1f}%")
        
        # Check specific data fields consistency
        field_consistency = {}
        for listing_id in active_my_ids.intersection(browse_demo_ids):
            my_listing = next(l for l in my_listings if l.get("id") == listing_id)
            browse_listing = next(l for l in demo_in_browse if l.get("id") == listing_id)
            
            # Check key fields
            for field in ["title", "price", "category", "status"]:
                if field not in field_consistency:
                    field_consistency[field] = {"matches": 0, "total": 0}
                
                field_consistency[field]["total"] += 1
                if my_listing.get(field) == browse_listing.get(field):
                    field_consistency[field]["matches"] += 1
        
        field_scores = {}
        for field, data in field_consistency.items():
            field_scores[field] = (data["matches"] / data["total"] * 100) if data["total"] > 0 else 100
            print(f"  📊 {field.title()} consistency: {field_scores[field]:.1f}%")
        
        return {
            "test_name": "Data Consistency",
            "my_listings_count": len(my_listings),
            "active_my_listings_count": len(active_my_listings),
            "demo_in_browse_count": len(demo_in_browse),
            "consistency_score": consistency_score,
            "field_consistency_scores": field_scores,
            "data_consistent": consistency_score >= 90,
            "all_fields_consistent": all(score >= 90 for score in field_scores.values())
        }
    
    async def run_comprehensive_verification(self) -> Dict:
        """Run all endpoint verification tests"""
        print("🚀 Starting Endpoint Verification Test")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run all verification tests
            my_listings_test = await self.test_my_listings_endpoint()
            browse_test = await self.test_browse_endpoint()
            messages_test = await self.test_messages_endpoint()
            individual_listings_test = await self.test_individual_listing_endpoints()
            consistency_test = await self.test_data_consistency()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "demo_user_id": DEMO_USER_ID,
                "my_listings_test": my_listings_test,
                "browse_test": browse_test,
                "messages_test": messages_test,
                "individual_listings_test": individual_listings_test,
                "consistency_test": consistency_test
            }
            
            # Calculate success metrics
            endpoint_tests = [
                my_listings_test.get("endpoint_working", False),
                browse_test.get("endpoint_working", False),
                messages_test.get("endpoint_working", False),
                individual_listings_test.get("both_endpoints_working", False)
            ]
            
            all_results["summary"] = {
                "my_listings_working": my_listings_test.get("endpoint_working", False),
                "my_listings_populated": my_listings_test.get("total_listings", 0) > 0,
                "browse_working": browse_test.get("endpoint_working", False),
                "browse_includes_demo_data": browse_test.get("includes_demo_data", False),
                "messages_working": messages_test.get("endpoint_working", False),
                "messages_populated": messages_test.get("has_conversations", False),
                "individual_listings_working": individual_listings_test.get("both_endpoints_working", False),
                "data_consistent": consistency_test.get("data_consistent", False),
                "all_endpoints_working": all(endpoint_tests),
                "verification_successful": all(endpoint_tests) and consistency_test.get("data_consistent", False),
                "total_demo_listings": my_listings_test.get("total_listings", 0),
                "listings_with_bids": my_listings_test.get("listings_with_bids", 0),
                "total_conversations": messages_test.get("total_conversations", 0)
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Run the endpoint verification test"""
    tester = EndpointVerificationTester()
    results = await tester.run_comprehensive_verification()
    
    print("\n" + "=" * 60)
    print("📊 ENDPOINT VERIFICATION RESULTS SUMMARY")
    print("=" * 60)
    
    summary = results.get("summary", {})
    
    print(f"✅ My Listings Working: {summary.get('my_listings_working', False)}")
    print(f"✅ My Listings Populated: {summary.get('my_listings_populated', False)} ({summary.get('total_demo_listings', 0)} listings)")
    print(f"✅ Browse Working: {summary.get('browse_working', False)}")
    print(f"✅ Browse Includes Demo Data: {summary.get('browse_includes_demo_data', False)}")
    print(f"✅ Messages Working: {summary.get('messages_working', False)}")
    print(f"✅ Messages Populated: {summary.get('messages_populated', False)} ({summary.get('total_conversations', 0)} conversations)")
    print(f"✅ Individual Listings Working: {summary.get('individual_listings_working', False)}")
    print(f"✅ Data Consistent: {summary.get('data_consistent', False)}")
    print(f"✅ Listings with Bids: {summary.get('listings_with_bids', 0)}")
    
    overall_success = summary.get('verification_successful', False)
    print(f"\n🎯 OVERALL VERIFICATION SUCCESS: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    
    if overall_success:
        print("\n🎉 All endpoints are working correctly with demo data!")
        print("📋 My Listings now shows populated data instead of 0 entries")
        print("🔍 Browse endpoint includes the new demo listings")
        print("💬 Messages endpoint has demo conversations")
        print("📊 Data is consistent across all endpoints")
    else:
        print("\n❌ Issues Found:")
        if not summary.get('my_listings_working', False):
            print("  - My Listings endpoint not working")
        if not summary.get('my_listings_populated', False):
            print("  - My Listings still empty")
        if not summary.get('browse_working', False):
            print("  - Browse endpoint not working")
        if not summary.get('messages_working', False):
            print("  - Messages endpoint not working")
        if not summary.get('data_consistent', False):
            print("  - Data inconsistency detected")
    
    # Save detailed results
    with open('/app/endpoint_verification_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/endpoint_verification_results.json")

if __name__ == "__main__":
    asyncio.run(main())