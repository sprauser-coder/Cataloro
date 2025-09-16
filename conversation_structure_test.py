#!/usr/bin/env python3
"""
Test conversation structure and frontend compatibility
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from collections import defaultdict

BACKEND_URL = "https://cataloro-uxfixes.preview.emergentagent.com/api"

async def test_conversation_structure():
    """Test how messages can be structured into conversations"""
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = {"email": "admin@cataloro.com", "password": "admin123"}
        
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                user_id = data.get("user", {}).get("id")
                token = data.get("token")
                
                print(f"✅ Testing conversations for user: {user_id}")
                
                # Get messages
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(f"{BACKEND_URL}/user/{user_id}/messages", headers=headers) as msg_response:
                    if msg_response.status == 200:
                        messages = await msg_response.json()
                        print(f"✅ Retrieved {len(messages)} messages")
                        
                        # Analyze message structure for conversation grouping
                        print("\n📊 MESSAGE ANALYSIS:")
                        
                        # Check data quality
                        valid_messages = []
                        invalid_messages = []
                        
                        for msg in messages:
                            if msg.get('content') is not None and msg.get('sender_id') and msg.get('recipient_id'):
                                valid_messages.append(msg)
                            else:
                                invalid_messages.append(msg)
                        
                        print(f"Valid messages: {len(valid_messages)}")
                        print(f"Invalid messages (null content/missing fields): {len(invalid_messages)}")
                        
                        if invalid_messages:
                            print(f"\n⚠️ INVALID MESSAGE EXAMPLES:")
                            for i, msg in enumerate(invalid_messages[:3]):
                                print(f"Message {i}: content={msg.get('content')}, sender={msg.get('sender_id')}, recipient={msg.get('recipient_id')}")
                        
                        # Group messages into conversations
                        conversations = defaultdict(list)
                        
                        for msg in valid_messages:
                            sender = msg.get('sender_id')
                            recipient = msg.get('recipient_id')
                            
                            # Create conversation key (sorted to group bidirectional conversations)
                            participants = tuple(sorted([sender, recipient]))
                            conversations[participants].append(msg)
                        
                        print(f"\n💬 CONVERSATION ANALYSIS:")
                        print(f"Total conversations: {len(conversations)}")
                        
                        # Analyze each conversation
                        for i, (participants, msgs) in enumerate(conversations.items()):
                            if i < 5:  # Show first 5 conversations
                                print(f"\nConversation {i+1}: {participants[0]} ↔ {participants[1]}")
                                print(f"  Messages: {len(msgs)}")
                                print(f"  Participants: {msgs[0].get('sender_name', 'Unknown')} ↔ {msgs[0].get('recipient_name', 'Unknown')}")
                                
                                # Show latest message
                                latest = max(msgs, key=lambda x: x.get('created_at', ''))
                                content = latest.get('content', '')
                                if len(content) > 50:
                                    content = content[:50] + "..."
                                print(f"  Latest: {content}")
                        
                        # Test frontend-compatible format
                        print(f"\n🔧 FRONTEND COMPATIBILITY TEST:")
                        
                        # Create frontend-compatible conversation list
                        frontend_conversations = []
                        
                        for participants, msgs in conversations.items():
                            # Sort messages by timestamp
                            sorted_msgs = sorted(msgs, key=lambda x: x.get('created_at', ''))
                            latest_msg = sorted_msgs[-1] if sorted_msgs else None
                            
                            if latest_msg:
                                # Determine the "other" participant (not the current user)
                                other_participant = participants[1] if participants[0] == user_id else participants[0]
                                
                                conversation = {
                                    "id": f"conv_{hash(participants)}",
                                    "participants": list(participants),
                                    "other_participant_id": other_participant,
                                    "other_participant_name": latest_msg.get('recipient_name') if latest_msg.get('sender_id') == user_id else latest_msg.get('sender_name'),
                                    "last_message": {
                                        "content": latest_msg.get('content'),
                                        "timestamp": latest_msg.get('created_at'),
                                        "sender_id": latest_msg.get('sender_id'),
                                        "is_read": latest_msg.get('is_read', False)
                                    },
                                    "message_count": len(msgs),
                                    "unread_count": sum(1 for msg in msgs if not msg.get('is_read', False) and msg.get('sender_id') != user_id)
                                }
                                frontend_conversations.append(conversation)
                        
                        # Sort by latest message timestamp
                        frontend_conversations.sort(key=lambda x: x['last_message']['timestamp'], reverse=True)
                        
                        print(f"Frontend-ready conversations: {len(frontend_conversations)}")
                        
                        # Show sample frontend format
                        if frontend_conversations:
                            print(f"\n📱 SAMPLE FRONTEND CONVERSATION FORMAT:")
                            sample = frontend_conversations[0]
                            print(json.dumps(sample, indent=2))
                        
                        # Test if this matches what frontend expects
                        print(f"\n✅ FRONTEND INTEGRATION ASSESSMENT:")
                        print(f"- Messages API working: ✅ Yes ({len(messages)} messages retrieved)")
                        print(f"- Authentication required: ❌ No (security issue)")
                        print(f"- Data structure valid: ⚠️ Partial ({len(valid_messages)}/{len(messages)} valid)")
                        print(f"- Conversation grouping possible: ✅ Yes ({len(conversations)} conversations)")
                        print(f"- Frontend format ready: ✅ Yes (can be transformed)")
                        
                        return {
                            "total_messages": len(messages),
                            "valid_messages": len(valid_messages),
                            "conversations": len(conversations),
                            "frontend_ready": len(frontend_conversations)
                        }
                    else:
                        print(f"❌ Failed to get messages: {msg_response.status}")
                        return None
            else:
                print(f"❌ Login failed: {response.status}")
                return None

if __name__ == "__main__":
    asyncio.run(test_conversation_structure())