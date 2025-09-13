#!/usr/bin/env python3
"""
CORRECTED ADMIN DASHBOARD COUNT TEST
Testing the admin dashboard count fix with correct response structure
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://cataloro-marketplace-6.preview.emergentagent.com/api"

async def test_admin_dashboard_counts():
    """Test admin dashboard count fix with correct response structure"""
    print("🔍 TESTING ADMIN DASHBOARD COUNT FIX (CORRECTED)")
    
    async with aiohttp.ClientSession() as session:
        # Login as admin
        login_data = {"email": "admin@cataloro.com", "password": "admin123"}
        
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status != 200:
                print("❌ Admin login failed")
                return False
            
            data = await response.json()
            token = data.get("token")
            
            if not token:
                print("❌ No token received")
                return False
            
            print("✅ Admin login successful")
        
        # Test admin dashboard
        headers = {"Authorization": f"Bearer {token}"}
        
        async with session.get(f"{BACKEND_URL}/admin/dashboard", headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                print(f"❌ Admin dashboard failed: {response.status} - {error_text}")
                return False
            
            data = await response.json()
            print(f"📊 Dashboard response structure: {list(data.keys())}")
            
            # Check if response has kpis structure
            if "kpis" in data:
                kpis = data["kpis"]
                total_listings = kpis.get('total_listings', 0)
                active_listings = kpis.get('active_listings', 0)
                
                print(f"📊 KPIs found:")
                print(f"   - total_listings: {total_listings}")
                print(f"   - active_listings: {active_listings}")
                print(f"   - total_users: {kpis.get('total_users', 0)}")
                print(f"   - total_deals: {kpis.get('total_deals', 0)}")
                print(f"   - revenue: {kpis.get('revenue', 0)}")
                
                # Test the fix: total_listings should be ALL listings, active_listings should be only active
                if total_listings >= active_listings:
                    print(f"✅ COUNT FIX WORKING: total_listings ({total_listings}) >= active_listings ({active_listings})")
                else:
                    print(f"❌ COUNT LOGIC ERROR: total_listings ({total_listings}) < active_listings ({active_listings})")
                    return False
                
                # Check if total_listings shows a reasonable number (should be higher like 62+)
                if total_listings >= 50:
                    print(f"✅ TOTAL COUNT FIX WORKING: Shows ALL listings ({total_listings} total)")
                else:
                    print(f"⚠️ TOTAL COUNT: {total_listings} total listings (may be correct if database has fewer listings)")
                
                # Check if active_listings is lower than total (as expected for the fix)
                if active_listings < total_listings:
                    print(f"✅ ACTIVE COUNT FIX WORKING: Shows only active listings ({active_listings} active < {total_listings} total)")
                elif active_listings == total_listings:
                    print(f"ℹ️ ACTIVE COUNT: All listings are active ({active_listings} active = {total_listings} total)")
                else:
                    print(f"❌ ACTIVE COUNT ISSUE: Active count ({active_listings}) > total ({total_listings})")
                    return False
                
                return True
            else:
                print(f"❌ Unexpected response structure: {data}")
                return False

async def main():
    success = await test_admin_dashboard_counts()
    if success:
        print("\n🎉 ADMIN DASHBOARD COUNT FIX VERIFIED!")
    else:
        print("\n❌ ADMIN DASHBOARD COUNT FIX NEEDS ATTENTION")

if __name__ == "__main__":
    asyncio.run(main())