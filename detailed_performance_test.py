#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - DETAILED PERFORMANCE INVESTIGATION
Deep dive into the Buy Tenders performance issue after fixing duplicate endpoints
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

BACKEND_URL = "https://vps-sync.preview.emergentagent.com/api"

class DetailedPerformanceTester:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login(self):
        """Login and get token"""
        try:
            login_data = {"email": "admin@cataloro.com", "password": "admin123"}
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("token"), data.get("user", {}).get("id")
                else:
                    print(f"❌ Login failed: {response.status}")
                    return None, None
        except Exception as e:
            print(f"❌ Login error: {e}")
            return None, None
    
    async def test_single_request_timing(self, endpoint, headers, label):
        """Test a single request with detailed timing"""
        print(f"   🔍 Testing {label}...")
        
        # Warm-up request
        async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as response:
            if response.status != 200:
                print(f"   ❌ Warm-up failed: {response.status}")
                return None
        
        # Actual timed requests
        times = []
        data_sizes = []
        
        for i in range(3):
            start_time = time.time()
            
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        end_time = time.time()
                        
                        response_time = (end_time - start_time) * 1000
                        data_size = len(data) if isinstance(data, list) else 1
                        
                        times.append(response_time)
                        data_sizes.append(data_size)
                        
                        print(f"      Request {i+1}: {response_time:.1f}ms ({data_size} items)")
                    else:
                        print(f"   ❌ Request {i+1} failed: {response.status}")
                        return None
                        
            except Exception as e:
                print(f"   ❌ Request {i+1} error: {e}")
                return None
        
        avg_time = sum(times) / len(times)
        avg_size = sum(data_sizes) / len(data_sizes)
        
        print(f"   📊 {label} Average: {avg_time:.1f}ms ({avg_size:.0f} items)")
        
        return {
            'avg_time': avg_time,
            'avg_size': avg_size,
            'times': times,
            'sizes': data_sizes,
            'last_data': data
        }
    
    async def analyze_buy_tenders_data_structure(self, data):
        """Analyze the data structure returned by Buy Tenders"""
        print(f"   🔍 Analyzing Buy Tenders data structure...")
        
        if not isinstance(data, list):
            print(f"   ❌ Expected list, got {type(data)}")
            return
        
        print(f"   📊 Total tenders: {len(data)}")
        
        if not data:
            print(f"   ⚠️ No tenders found")
            return
        
        # Analyze first tender
        sample = data[0]
        print(f"   📋 Sample tender structure:")
        for key, value in sample.items():
            if isinstance(value, dict):
                print(f"      - {key}: dict with {len(value)} keys")
                for subkey in value.keys():
                    print(f"        - {subkey}: {type(value[subkey]).__name__}")
            else:
                print(f"      - {key}: {type(value).__name__}")
        
        # Check for missing data
        missing_listings = 0
        missing_sellers = 0
        
        for tender in data:
            if not tender.get('listing') or not tender.get('listing', {}).get('id'):
                missing_listings += 1
            if not tender.get('seller') or not tender.get('seller', {}).get('id'):
                missing_sellers += 1
        
        print(f"   📈 Data completeness:")
        print(f"      - Tenders with listings: {len(data) - missing_listings}/{len(data)}")
        print(f"      - Tenders with sellers: {len(data) - missing_sellers}/{len(data)}")
        
        return {
            'total_tenders': len(data),
            'missing_listings': missing_listings,
            'missing_sellers': missing_sellers
        }
    
    async def compare_endpoint_structures(self, buy_data, sell_data):
        """Compare the data structures of both endpoints"""
        print(f"   🔍 Comparing endpoint data structures...")
        
        # Buy Tenders structure
        buy_structure = "Unknown"
        if isinstance(buy_data, list) and buy_data:
            buy_sample = buy_data[0]
            buy_structure = f"List of {len(buy_data)} tenders, each with keys: {list(buy_sample.keys())}"
        
        # Sell Tenders structure
        sell_structure = "Unknown"
        sell_total_tenders = 0
        if isinstance(sell_data, list) and sell_data:
            sell_sample = sell_data[0]
            sell_structure = f"List of {len(sell_data)} listings, each with keys: {list(sell_sample.keys())}"
            
            # Count total tenders in sell data
            for listing in sell_data:
                tenders = listing.get('tenders', [])
                sell_total_tenders += len(tenders)
        
        print(f"   📊 Structure comparison:")
        print(f"      Buy Tenders: {buy_structure}")
        print(f"      Sell Tenders: {sell_structure}")
        print(f"      Sell Tenders total tender count: {sell_total_tenders}")
        
        return {
            'buy_structure': buy_structure,
            'sell_structure': sell_structure,
            'sell_total_tenders': sell_total_tenders
        }
    
    async def run_detailed_analysis(self):
        """Run detailed performance analysis"""
        print("🚀 DETAILED BUY TENDERS PERFORMANCE INVESTIGATION")
        print("="*60)
        
        # Login
        token, user_id = await self.login()
        if not token:
            return
        
        print(f"✅ Logged in as user: {user_id}")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test Buy Tenders endpoint
        print(f"\n📊 TESTING BUY TENDERS ENDPOINT:")
        buy_result = await self.test_single_request_timing(
            f"/tenders/buyer/{user_id}", 
            headers, 
            "Buy Tenders"
        )
        
        # Test Sell Tenders endpoint
        print(f"\n📊 TESTING SELL TENDERS ENDPOINT:")
        sell_result = await self.test_single_request_timing(
            f"/tenders/seller/{user_id}/overview", 
            headers, 
            "Sell Tenders"
        )
        
        if not buy_result or not sell_result:
            print("❌ Failed to get results from both endpoints")
            return
        
        # Analyze data structures
        print(f"\n🔍 DATA STRUCTURE ANALYSIS:")
        buy_analysis = await self.analyze_buy_tenders_data_structure(buy_result['last_data'])
        structure_comparison = await self.compare_endpoint_structures(
            buy_result['last_data'], 
            sell_result['last_data']
        )
        
        # Performance comparison
        print(f"\n⚖️ PERFORMANCE COMPARISON:")
        buy_time = buy_result['avg_time']
        sell_time = sell_result['avg_time']
        buy_size = buy_result['avg_size']
        sell_size = sell_result['avg_size']
        
        time_ratio = buy_time / sell_time if sell_time > 0 else float('inf')
        efficiency_buy = buy_size / buy_time if buy_time > 0 else 0
        efficiency_sell = sell_size / sell_time if sell_time > 0 else 0
        
        print(f"   📊 Performance metrics:")
        print(f"      Buy Tenders: {buy_time:.1f}ms for {buy_size:.0f} items")
        print(f"      Sell Tenders: {sell_time:.1f}ms for {sell_size:.0f} items")
        print(f"      Time ratio: {time_ratio:.1f}x (Buy is {time_ratio:.1f}x slower)")
        print(f"      Efficiency Buy: {efficiency_buy:.3f} items/ms")
        print(f"      Efficiency Sell: {efficiency_sell:.3f} items/ms")
        
        # Root cause analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        if time_ratio > 10:
            print(f"   🚨 CRITICAL PERFORMANCE ISSUE: Buy Tenders is {time_ratio:.1f}x slower")
            
            if buy_analysis and buy_analysis['missing_listings'] > 0:
                print(f"   🔍 POTENTIAL CAUSE: {buy_analysis['missing_listings']} tenders missing listing data")
            
            if buy_analysis and buy_analysis['missing_sellers'] > 0:
                print(f"   🔍 POTENTIAL CAUSE: {buy_analysis['missing_sellers']} tenders missing seller data")
            
            print(f"   🔍 INVESTIGATION NEEDED:")
            print(f"      - Check database indexes on tenders.listing_id and tenders.seller_id")
            print(f"      - Check if listings and users collections have proper indexes")
            print(f"      - Verify data integrity in database")
            print(f"      - Consider adding database query logging")
        
        elif time_ratio > 2:
            print(f"   ⚠️ MODERATE PERFORMANCE ISSUE: Buy Tenders is {time_ratio:.1f}x slower")
            print(f"   🔍 This may be acceptable given different data structures")
        
        else:
            print(f"   ✅ PERFORMANCE ACCEPTABLE: Buy Tenders is only {time_ratio:.1f}x slower")

async def main():
    async with DetailedPerformanceTester() as tester:
        await tester.run_detailed_analysis()

if __name__ == "__main__":
    asyncio.run(main())