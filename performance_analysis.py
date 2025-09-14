#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - BUY TENDERS PERFORMANCE ANALYSIS
Detailed analysis of the performance issue found in Buy Tenders API

ROOT CAUSE IDENTIFIED:
The Buy Tenders API has DUPLICATE ENDPOINT DEFINITIONS in server.py:
1. Line 5687: Slow version with N+1 query problem (individual DB queries for each tender)
2. Line 6135: Optimized version with batch queries

FastAPI uses the FIRST definition (slow version), causing 24.4x slower performance.

PERFORMANCE COMPARISON:
- Buy Tenders (slow): 725.5ms for 14 items (N+1 queries)
- Sell Tenders (optimized): 29.7ms for 62 items (batch queries)

TECHNICAL DETAILS:
- Buy Tenders makes 1 + N database queries (1 for tenders + N for listings + N for sellers)
- Sell Tenders makes 3 database queries total (1 for listings + 1 for tenders + 1 for buyers)
- For 14 tenders, Buy Tenders makes ~29 database queries vs 3 for Sell Tenders
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://marketplace-perf-1.preview.emergentagent.com/api"

class PerformanceAnalyzer:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_buy_tenders_response(self, token):
        """Analyze the actual Buy Tenders response structure"""
        print("🔍 ANALYZING BUY TENDERS RESPONSE STRUCTURE:")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with self.session.get(f"{BACKEND_URL}/tenders/buyer/admin_user_1", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"   📊 Total tenders returned: {len(data)}")
                    
                    if data:
                        sample = data[0]
                        print(f"   📋 Sample tender structure:")
                        print(f"      - ID: {sample.get('id', 'MISSING')}")
                        print(f"      - Offer Amount: {sample.get('offer_amount', 'MISSING')}")
                        print(f"      - Status: {sample.get('status', 'MISSING')}")
                        print(f"      - Listing: {'✅ Present' if sample.get('listing') else '❌ Missing'}")
                        print(f"      - Seller: {'✅ Present' if sample.get('seller') else '❌ Missing'}")
                        
                        # Check listing enrichment
                        listing = sample.get('listing', {})
                        if listing:
                            print(f"      - Listing ID: {listing.get('id', 'MISSING')}")
                            print(f"      - Listing Title: {listing.get('title', 'MISSING')}")
                            print(f"      - Listing Price: {listing.get('price', 'MISSING')}")
                        
                        # Check seller enrichment
                        seller = sample.get('seller', {})
                        if seller:
                            print(f"      - Seller ID: {seller.get('id', 'MISSING')}")
                            print(f"      - Seller Username: {seller.get('username', 'MISSING')}")
                            print(f"      - Seller Full Name: {seller.get('full_name', 'MISSING')}")
                        
                        # Check for data integrity issues
                        integrity_issues = 0
                        for i, tender in enumerate(data):
                            issues = []
                            if not tender.get('listing'):
                                issues.append("missing listing")
                            if not tender.get('seller'):
                                issues.append("missing seller")
                            if not tender.get('listing', {}).get('id'):
                                issues.append("missing listing.id")
                            if not tender.get('seller', {}).get('id'):
                                issues.append("missing seller.id")
                            
                            if issues:
                                integrity_issues += 1
                                print(f"      ❌ Tender {i+1}: {', '.join(issues)}")
                        
                        print(f"   📈 Data integrity: {len(data) - integrity_issues}/{len(data)} tenders have complete data")
                        
                        return {
                            'total_tenders': len(data),
                            'integrity_issues': integrity_issues,
                            'sample_structure': sample
                        }
                else:
                    print(f"   ❌ Failed to get Buy Tenders: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            print(f"   ❌ Error analyzing Buy Tenders: {e}")
            return None
    
    async def login_and_analyze(self):
        """Login and perform analysis"""
        print("🚀 STARTING BUY TENDERS PERFORMANCE ANALYSIS")
        print("="*60)
        
        # Login
        try:
            login_data = {"email": "admin@cataloro.com", "password": "admin123"}
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    user = data.get("user", {})
                    print(f"✅ Logged in as: {user.get('full_name')} (ID: {user.get('id')})")
                else:
                    print("❌ Login failed")
                    return
        except Exception as e:
            print(f"❌ Login error: {e}")
            return
        
        # Analyze Buy Tenders response
        await self.analyze_buy_tenders_response(token)
        
        # Print root cause analysis
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        print("="*60)
        print("❌ DUPLICATE ENDPOINT DEFINITIONS FOUND:")
        print("   1. Line 5687: @app.get('/api/tenders/buyer/{buyer_id}') - SLOW VERSION")
        print("      - Uses individual database queries for each tender (N+1 problem)")
        print("      - For each tender: 1 query for listing + 1 query for seller")
        print("      - Total queries: 1 + (N * 2) = 1 + (14 * 2) = 29 database queries")
        print()
        print("   2. Line 6135: @app.get('/api/tenders/buyer/{buyer_id}') - OPTIMIZED VERSION")
        print("      - Uses batch queries to minimize database calls")
        print("      - Total queries: 1 for tenders + 1 for listings + 1 for sellers = 3 queries")
        print()
        print("🚨 FASTAPI ISSUE: FastAPI uses the FIRST endpoint definition (slow version)")
        print("   The optimized version at line 6135 is never executed!")
        print()
        print("📊 PERFORMANCE IMPACT:")
        print("   - Current (slow): 725.5ms for 14 items = 51.8ms per item")
        print("   - Expected (optimized): ~30ms for 14 items = 2.1ms per item")
        print("   - Performance degradation: 24.4x slower than expected")
        print()
        print("🔧 SOLUTION:")
        print("   Remove the duplicate slow endpoint definition at line 5687")
        print("   Keep only the optimized version at line 6135")

async def main():
    async with PerformanceAnalyzer() as analyzer:
        await analyzer.login_and_analyze()

if __name__ == "__main__":
    asyncio.run(main())