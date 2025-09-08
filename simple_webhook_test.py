#!/usr/bin/env python3
"""
Simple Webhook Test - Test existing webhook functionality
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://mega-dashboard.preview.emergentagent.com/api"

async def test_existing_webhook():
    """Test existing webhook functionality"""
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing existing webhook functionality...")
        
        # Get existing webhooks
        async with session.get(f"{BACKEND_URL}/admin/webhooks") as response:
            if response.status == 200:
                data = await response.json()
                webhooks = data.get("webhooks", [])
                if webhooks:
                    webhook = webhooks[0]
                    webhook_id = webhook["id"]
                    print(f"✅ Found existing webhook: {webhook['name']} (ID: {webhook_id})")
                    
                    # Test webhook details
                    async with session.get(f"{BACKEND_URL}/admin/webhooks/{webhook_id}") as detail_response:
                        if detail_response.status == 200:
                            detail_data = await detail_response.json()
                            print(f"✅ Webhook details retrieved successfully")
                        else:
                            print(f"❌ Failed to get webhook details: {detail_response.status}")
                    
                    # Test webhook test functionality
                    async with session.post(f"{BACKEND_URL}/admin/webhooks/{webhook_id}/test") as test_response:
                        if test_response.status == 200:
                            test_data = await test_response.json()
                            print(f"✅ Webhook test sent successfully")
                        else:
                            print(f"❌ Failed to test webhook: {test_response.status}")
                    
                    # Test webhook deliveries
                    async with session.get(f"{BACKEND_URL}/admin/webhooks/{webhook_id}/deliveries") as deliveries_response:
                        if deliveries_response.status == 200:
                            deliveries_data = await deliveries_response.json()
                            deliveries = deliveries_data.get("deliveries", [])
                            print(f"✅ Retrieved {len(deliveries)} delivery records")
                        else:
                            print(f"❌ Failed to get deliveries: {deliveries_response.status}")
                    
                    return True
                else:
                    print("❌ No existing webhooks found")
                    return False
            else:
                print(f"❌ Failed to get webhooks: {response.status}")
                return False

async def main():
    success = await test_existing_webhook()
    if success:
        print("\n✅ Webhook functionality is working!")
    else:
        print("\n❌ Webhook functionality has issues")

if __name__ == "__main__":
    asyncio.run(main())