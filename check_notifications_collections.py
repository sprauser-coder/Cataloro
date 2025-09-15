#!/usr/bin/env python3
"""
Check which notifications collections exist and have data
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://nginx-config-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"

class NotificationsCollectionChecker:
    def __init__(self):
        self.session = None
        self.admin_token = None
        
    async def setup(self):
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params=None, data=None, headers=None):
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
    
    async def authenticate_admin(self):
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            print(f"✅ Admin authentication successful")
            return True
        else:
            print(f"❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            return False
    
    async def check_collections(self):
        if not self.admin_token:
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/performance", headers=headers)
        
        if result["success"]:
            performance_data = result.get("data", {})
            collections = performance_data.get("collections", {})
            
            print("📊 Database Collections Analysis:")
            print("=" * 50)
            
            notification_collections = [
                "notifications", 
                "user_notifications", 
                "system_notifications"
            ]
            
            for collection_name in notification_collections:
                if collection_name in collections:
                    info = collections[collection_name]
                    count = info.get("document_count", 0)
                    indexes = info.get("index_count", 0)
                    print(f"✅ {collection_name}: {count} documents, {indexes} indexes")
                else:
                    print(f"❌ {collection_name}: Collection not found")
            
            print("\n📋 All Collections:")
            for name, info in collections.items():
                count = info.get("document_count", 0)
                if count > 0:
                    print(f"   {name}: {count} documents")
        else:
            print(f"❌ Failed to get database info: {result.get('error', 'Unknown error')}")

async def main():
    checker = NotificationsCollectionChecker()
    await checker.setup()
    
    try:
        if await checker.authenticate_admin():
            await checker.check_collections()
    finally:
        await checker.cleanup()

if __name__ == "__main__":
    asyncio.run(main())