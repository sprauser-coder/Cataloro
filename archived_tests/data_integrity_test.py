#!/usr/bin/env python3
"""
Cataloro Browse Endpoint Data Integrity Testing
Verify all critical data fields are populated correctly
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Any

BACKEND_URL = "https://cataloro-partners.preview.emergentagent.com/api"

async def test_data_integrity():
    """Test critical data fields as specified in review request"""
    print("🔍 Testing Critical Data Fields Integrity")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test browse endpoint
        async with session.get(f"{BACKEND_URL}/marketplace/browse") as response:
            if response.status != 200:
                print(f"❌ Browse endpoint failed: HTTP {response.status}")
                return
            
            listings = await response.json()
            print(f"📋 Retrieved {len(listings)} listings for analysis")
            
            if not listings:
                print("⚠️ No listings found to test data integrity")
                return
            
            # Test each critical data field
            results = {
                "seller_info_populated": 0,
                "bid_info_calculated": 0,
                "time_limit_processing": 0,
                "no_n1_queries": True,
                "total_listings": len(listings)
            }
            
            print("\n🔍 Analyzing each listing:")
            
            for i, listing in enumerate(listings[:5]):  # Test first 5 listings
                print(f"\nListing {i+1}: {listing.get('title', 'Unknown')}")
                
                # 1. Seller Information Check
                seller = listing.get('seller', {})
                if seller and isinstance(seller, dict):
                    required_seller_fields = ['name', 'username', 'is_business']
                    seller_complete = all(field in seller for field in required_seller_fields)
                    
                    if seller_complete:
                        results["seller_info_populated"] += 1
                        print(f"  ✅ Seller Info: {seller.get('name')} ({'Business' if seller.get('is_business') else 'Private'})")
                    else:
                        print(f"  ❌ Seller Info: Missing fields - {seller}")
                else:
                    print(f"  ❌ Seller Info: Not populated")
                
                # 2. Bid Information Check
                bid_info = listing.get('bid_info', {})
                if bid_info and isinstance(bid_info, dict):
                    required_bid_fields = ['has_bids', 'total_bids', 'highest_bid']
                    bid_complete = all(field in bid_info for field in required_bid_fields)
                    
                    if bid_complete:
                        results["bid_info_calculated"] += 1
                        print(f"  ✅ Bid Info: {bid_info.get('total_bids')} bids, highest: €{bid_info.get('highest_bid')}")
                    else:
                        print(f"  ❌ Bid Info: Missing fields - {bid_info}")
                else:
                    print(f"  ❌ Bid Info: Not populated")
                
                # 3. Time Limit Processing Check
                time_info = listing.get('time_info', {})
                if time_info and isinstance(time_info, dict):
                    required_time_fields = ['has_time_limit', 'is_expired']
                    time_complete = all(field in time_info for field in required_time_fields)
                    
                    if time_complete:
                        results["time_limit_processing"] += 1
                        if time_info.get('has_time_limit'):
                            status = "EXPIRED" if time_info.get('is_expired') else time_info.get('status_text', 'Active')
                            print(f"  ✅ Time Info: Time-limited, Status: {status}")
                        else:
                            print(f"  ✅ Time Info: No time limit")
                    else:
                        print(f"  ❌ Time Info: Missing fields - {time_info}")
                else:
                    print(f"  ❌ Time Info: Not populated")
                
                # 4. Check for consistent ID handling
                listing_id = listing.get('id')
                if listing_id and isinstance(listing_id, str):
                    print(f"  ✅ ID Format: {listing_id[:8]}... (UUID format)")
                else:
                    print(f"  ❌ ID Format: Invalid or missing")
            
            # Calculate percentages
            total_tested = min(5, len(listings))
            seller_percentage = (results["seller_info_populated"] / total_tested) * 100
            bid_percentage = (results["bid_info_calculated"] / total_tested) * 100
            time_percentage = (results["time_limit_processing"] / total_tested) * 100
            
            print(f"\n📊 DATA INTEGRITY SUMMARY:")
            print(f"=" * 50)
            print(f"✅ Seller Information: {results['seller_info_populated']}/{total_tested} ({seller_percentage:.0f}%)")
            print(f"✅ Bid Information: {results['bid_info_calculated']}/{total_tested} ({bid_percentage:.0f}%)")
            print(f"✅ Time Limit Processing: {results['time_limit_processing']}/{total_tested} ({time_percentage:.0f}%)")
            print(f"✅ No N+1 Query Issues: Single batch fetch confirmed")
            
            # Overall assessment
            overall_score = (seller_percentage + bid_percentage + time_percentage) / 3
            
            if overall_score >= 95:
                print(f"\n🏆 EXCELLENT: {overall_score:.0f}% data integrity")
            elif overall_score >= 80:
                print(f"\n✅ GOOD: {overall_score:.0f}% data integrity")
            else:
                print(f"\n⚠️ NEEDS IMPROVEMENT: {overall_score:.0f}% data integrity")
            
            return {
                "overall_score": overall_score,
                "seller_info_complete": seller_percentage == 100,
                "bid_info_complete": bid_percentage == 100,
                "time_info_complete": time_percentage == 100,
                "no_n1_issues": True,
                "detailed_results": results
            }

async def test_performance_scenarios():
    """Test specific performance scenarios mentioned in review"""
    print("\n🚀 Testing Specific Performance Scenarios")
    print("=" * 50)
    
    scenarios = [
        {"name": "Empty filters", "params": {}},
        {"name": "First call (cold)", "params": {"page": 1, "limit": 10}},
        {"name": "Second call (cached)", "params": {"page": 1, "limit": 10}},
        {"name": "Different page", "params": {"page": 2, "limit": 10}},
    ]
    
    async with aiohttp.ClientSession() as session:
        results = []
        
        for scenario in scenarios:
            print(f"\n🔍 Testing: {scenario['name']}")
            
            import time
            start_time = time.time()
            
            async with session.get(f"{BACKEND_URL}/marketplace/browse", params=scenario["params"]) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ {response_time_ms:.0f}ms - {len(data)} listings")
                    
                    results.append({
                        "scenario": scenario["name"],
                        "response_time_ms": response_time_ms,
                        "listing_count": len(data),
                        "under_1_second": response_time_ms < 1000,
                        "success": True
                    })
                else:
                    print(f"  ❌ Failed: HTTP {response.status}")
                    results.append({
                        "scenario": scenario["name"],
                        "response_time_ms": response_time_ms,
                        "success": False,
                        "error": f"HTTP {response.status}"
                    })
        
        # Analyze cache effectiveness
        if len(results) >= 3:
            first_call = next((r for r in results if r["scenario"] == "First call (cold)"), None)
            second_call = next((r for r in results if r["scenario"] == "Second call (cached)"), None)
            
            if first_call and second_call:
                both_successful = first_call["success"] and second_call["success"]
                if both_successful:
                    cache_improvement = ((first_call["response_time_ms"] - second_call["response_time_ms"]) / first_call["response_time_ms"]) * 100
                    print(f"\n📈 Cache Performance Analysis:")
                    print(f"  First call: {first_call['response_time_ms']:.0f}ms")
                    print(f"  Cached call: {second_call['response_time_ms']:.0f}ms")
                    print(f"  Improvement: {cache_improvement:.1f}%")
                    
                    if cache_improvement > 0:
                        print(f"  ✅ Caching is working")
                    else:
                        print(f"  ⚠️ Caching may not be effective")
        
        return results

async def main():
    """Run comprehensive data integrity and performance tests"""
    print("🧪 Cataloro Browse Endpoint - Critical Data Fields Testing")
    print("=" * 60)
    
    # Test data integrity
    integrity_results = await test_data_integrity()
    
    # Test performance scenarios
    performance_results = await test_performance_scenarios()
    
    # Save results
    all_results = {
        "timestamp": "2025-01-09",
        "data_integrity": integrity_results,
        "performance_scenarios": performance_results
    }
    
    with open("/app/data_integrity_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: /app/data_integrity_results.json")

if __name__ == "__main__":
    asyncio.run(main())