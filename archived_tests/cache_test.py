#!/usr/bin/env python3
"""
Focused Redis Cache Performance Testing
"""

import asyncio
import aiohttp
import time
import statistics

BACKEND_URL = "https://cataloro-marketplace-5.preview.emergentagent.com/api"

async def test_cache_effectiveness():
    """Test cache effectiveness with multiple scenarios"""
    print("🚀 Redis Cache Effectiveness Testing")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Same parameters multiple times
        print("\n📋 Test 1: Same parameters (should show caching)")
        params = {"page": 1, "limit": 8}
        times = []
        
        for i in range(5):
            start = time.time()
            async with session.get(f"{BACKEND_URL}/marketplace/browse", params=params) as response:
                end = time.time()
                response_time = (end - start) * 1000
                times.append(response_time)
                
                if response.status == 200:
                    data = await response.json()
                    print(f"  Call {i+1}: {response_time:.0f}ms - {len(data)} listings")
                else:
                    print(f"  Call {i+1}: FAILED - HTTP {response.status}")
        
        if len(times) >= 2:
            first_call = times[0]
            avg_cached = statistics.mean(times[1:])
            improvement = ((first_call - avg_cached) / first_call) * 100
            print(f"  📈 First call: {first_call:.0f}ms")
            print(f"  📈 Avg cached: {avg_cached:.0f}ms")
            print(f"  📈 Cache improvement: {improvement:.1f}%")
        
        # Test 2: Different parameters (should not use cache)
        print("\n📋 Test 2: Different parameters (fresh queries)")
        different_params = [
            {"page": 1, "limit": 5},
            {"page": 2, "limit": 5},
            {"type": "Private"},
            {"price_from": 100, "price_to": 500}
        ]
        
        for i, params in enumerate(different_params):
            start = time.time()
            async with session.get(f"{BACKEND_URL}/marketplace/browse", params=params) as response:
                end = time.time()
                response_time = (end - start) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    print(f"  Query {i+1}: {response_time:.0f}ms - {len(data)} listings - {params}")
                else:
                    print(f"  Query {i+1}: FAILED - HTTP {response.status}")
        
        # Test 3: Repeat one of the different parameters (should be cached now)
        print("\n📋 Test 3: Repeat previous query (should be cached)")
        repeat_params = {"page": 1, "limit": 5}
        
        start = time.time()
        async with session.get(f"{BACKEND_URL}/marketplace/browse", params=repeat_params) as response:
            end = time.time()
            response_time = (end - start) * 1000
            
            if response.status == 200:
                data = await response.json()
                print(f"  Cached repeat: {response_time:.0f}ms - {len(data)} listings")
            else:
                print(f"  Cached repeat: FAILED - HTTP {response.status}")

if __name__ == "__main__":
    asyncio.run(test_cache_effectiveness())