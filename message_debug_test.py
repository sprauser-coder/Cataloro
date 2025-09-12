#!/usr/bin/env python3
"""
Debug script to examine message data structure issues
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://cataloro-admin-fix.preview.emergentagent.com/api"

async def debug_messages():
    """Debug message data structure"""
    async with aiohttp.ClientSession() as session:
        # Login first
        login_data = {"email": "admin@cataloro.com", "password": "admin123"}
        
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                token = data.get("token")
                user_id = data.get("user", {}).get("id")
                
                if token and user_id:
                    print(f"✅ Logged in as user: {user_id}")
                    
                    # Get messages
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(f"{BACKEND_URL}/user/{user_id}/messages", headers=headers) as msg_response:
                        if msg_response.status == 200:
                            messages = await msg_response.json()
                            print(f"✅ Retrieved {len(messages)} messages")
                            
                            # Examine first few messages in detail
                            for i, message in enumerate(messages[:5]):
                                print(f"\n--- Message {i} ---")
                                print(f"Keys: {list(message.keys())}")
                                print(f"Content type: {type(message.get('content'))}")
                                print(f"Content value: {repr(message.get('content'))}")
                                
                                if 'content' in message:
                                    content = message['content']
                                    if isinstance(content, dict):
                                        print(f"Content is dict with keys: {list(content.keys())}")
                                    elif isinstance(content, list):
                                        print(f"Content is list with {len(content)} items")
                                    else:
                                        print(f"Content is {type(content)}: {content}")
                        else:
                            print(f"❌ Failed to get messages: {msg_response.status}")
                else:
                    print("❌ No token or user_id in login response")
            else:
                print(f"❌ Login failed: {response.status}")

if __name__ == "__main__":
    asyncio.run(debug_messages())