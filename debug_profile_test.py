#!/usr/bin/env python3
"""
Debug Profile Issues
"""

import asyncio
import aiohttp
import json

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://cataloro-menueditor.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

async def debug_profile_issues():
    connector = aiohttp.TCPConnector(ssl=False)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # First, login and get user ID
        print("🔍 Debugging profile issues...")
        
        # Login as admin
        async with session.post(f"{API_BASE}/auth/login", json={
            "email": "admin@cataloro.com",
            "password": "admin123"
        }) as response:
            login_data = await response.json()
            print(f"Login response: {json.dumps(login_data, indent=2)}")
            
            if "user" in login_data:
                user = login_data["user"]
                user_id = user["id"]
                print(f"User ID: {user_id}")
                
                # Test basic profile access
                async with session.get(f"{API_BASE}/auth/profile/{user_id}") as response:
                    profile_data = await response.json()
                    print(f"Profile response status: {response.status}")
                    print(f"Profile data: {json.dumps(profile_data, indent=2)}")
                
                # Test profile stats
                async with session.get(f"{API_BASE}/auth/profile/{user_id}/stats") as response:
                    stats_data = await response.json()
                    print(f"Stats response status: {response.status}")
                    if response.status != 200:
                        print(f"Stats error: {json.dumps(stats_data, indent=2)}")
                    else:
                        print("Stats working correctly")
                
                # Test public profile
                async with session.get(f"{API_BASE}/profile/{user_id}/public") as response:
                    public_data = await response.json()
                    print(f"Public profile response status: {response.status}")
                    if response.status != 200:
                        print(f"Public profile error: {json.dumps(public_data, indent=2)}")
                    else:
                        print("Public profile working correctly")
                
                # Test export
                async with session.post(f"{API_BASE}/auth/profile/{user_id}/export") as response:
                    export_data = await response.json()
                    print(f"Export response status: {response.status}")
                    if response.status != 200:
                        print(f"Export error: {json.dumps(export_data, indent=2)}")
                    else:
                        print("Export working correctly")

if __name__ == "__main__":
    asyncio.run(debug_profile_issues())