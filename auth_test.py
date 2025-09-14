#!/usr/bin/env python3
"""
Test authentication requirements for messages endpoint
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://mobilefixed-market.preview.emergentagent.com/api"

async def test_auth_requirements():
    """Test if messages endpoint requires authentication"""
    async with aiohttp.ClientSession() as session:
        # First, login to get a valid user_id
        login_data = {"email": "admin@cataloro.com", "password": "admin123"}
        
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                user_id = data.get("user", {}).get("id")
                token = data.get("token")
                
                print(f"✅ Logged in successfully, user_id: {user_id}")
                
                # Test 1: Access messages WITHOUT authentication
                print("\n🔍 Testing messages endpoint WITHOUT authentication:")
                async with session.get(f"{BACKEND_URL}/user/{user_id}/messages") as msg_response:
                    print(f"Status: {msg_response.status}")
                    if msg_response.status == 200:
                        messages = await msg_response.json()
                        print(f"❌ SECURITY ISSUE: Messages accessible without auth! Retrieved {len(messages)} messages")
                    elif msg_response.status in [401, 403]:
                        print(f"✅ SECURITY OK: Authentication required (Status {msg_response.status})")
                    else:
                        error_text = await msg_response.text()
                        print(f"⚠️ Unexpected status: {msg_response.status} - {error_text}")
                
                # Test 2: Access messages WITH authentication
                print("\n🔍 Testing messages endpoint WITH authentication:")
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(f"{BACKEND_URL}/user/{user_id}/messages", headers=headers) as msg_response:
                    print(f"Status: {msg_response.status}")
                    if msg_response.status == 200:
                        messages = await msg_response.json()
                        print(f"✅ Messages retrieved with auth: {len(messages)} messages")
                        
                        # Check if messages have proper structure for conversations
                        if messages:
                            print(f"\n📋 Sample message structure:")
                            sample = messages[0]
                            print(f"Keys: {list(sample.keys())}")
                            print(f"Has sender info: {'sender_name' in sample}")
                            print(f"Has recipient info: {'recipient_name' in sample}")
                            print(f"Has timestamp: {'created_at' in sample}")
                            
                            # Check for conversation grouping potential
                            senders = set(msg.get('sender_id') for msg in messages)
                            recipients = set(msg.get('recipient_id') for msg in messages)
                            print(f"Unique senders: {len(senders)}")
                            print(f"Unique recipients: {len(recipients)}")
                            print(f"Total unique participants: {len(senders | recipients)}")
                        else:
                            print("📋 No messages found")
                    else:
                        error_text = await msg_response.text()
                        print(f"❌ Failed to get messages with auth: {msg_response.status} - {error_text}")
                
                # Test 3: Try to access another user's messages
                print("\n🔍 Testing cross-user access (security test):")
                other_user_id = "68bfff790e4e46bc28d43631"  # Demo user ID
                async with session.get(f"{BACKEND_URL}/user/{other_user_id}/messages", headers=headers) as msg_response:
                    print(f"Status: {msg_response.status}")
                    if msg_response.status == 200:
                        messages = await msg_response.json()
                        print(f"⚠️ POTENTIAL SECURITY ISSUE: Can access other user's messages! Retrieved {len(messages)} messages")
                    elif msg_response.status in [401, 403]:
                        print(f"✅ SECURITY OK: Cannot access other user's messages (Status {msg_response.status})")
                    else:
                        error_text = await msg_response.text()
                        print(f"Status {msg_response.status}: {error_text}")
                        
            else:
                print(f"❌ Login failed: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_auth_requirements())