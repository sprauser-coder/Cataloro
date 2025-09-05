#!/usr/bin/env python3
"""
Debug the complete message flow to identify the specific issue
"""

import requests
import json

def test_complete_flow():
    base_url = "https://market-refactor.preview.emergentagent.com"
    
    # Create two test users
    user1_data = {
        "username": "flow_test_alice",
        "email": "flow_test_alice@example.com",
        "full_name": "Flow Test Alice"
    }
    
    user2_data = {
        "username": "flow_test_bob",
        "email": "flow_test_bob@example.com",
        "full_name": "Flow Test Bob"
    }
    
    # Register and login users
    print("Creating test users...")
    requests.post(f"{base_url}/api/auth/register", json=user1_data)
    requests.post(f"{base_url}/api/auth/register", json=user2_data)
    
    user1_login = requests.post(f"{base_url}/api/auth/login", json={"email": user1_data["email"], "password": "test123"})
    user2_login = requests.post(f"{base_url}/api/auth/login", json={"email": user2_data["email"], "password": "test123"})
    
    if user1_login.status_code != 200 or user2_login.status_code != 200:
        print("Failed to create/login users")
        return
    
    user1 = user1_login.json()['user']
    user2 = user2_login.json()['user']
    
    print(f"User1: {user1['full_name']} (ID: {user1['id']})")
    print(f"User2: {user2['full_name']} (ID: {user2['id']})")
    
    # Step 1: Search for user2
    print(f"\nStep 1: Searching for user2 by username...")
    search_term = user2['username'][:4]
    search_response = requests.get(f"{base_url}/api/users/search", params={"q": search_term})
    print(f"Search response: {search_response.status_code}")
    
    if search_response.status_code == 200:
        search_results = search_response.json()
        print(f"Found {len(search_results)} users")
        
        user_found = False
        for user in search_results:
            if user['id'] == user2['id']:
                user_found = True
                print(f"✅ Found target user: {user['display_name']}")
                break
        
        if not user_found:
            print(f"❌ Target user not found in search results")
            return
    else:
        print(f"❌ Search failed: {search_response.text}")
        return
    
    # Step 2: Send message
    print(f"\nStep 2: Sending message from user1 to user2...")
    message_data = {
        "recipient_id": user2['id'],
        "subject": "Complete Flow Test",
        "content": f"Hi {user2['full_name']}! This is a complete flow test message."
    }
    
    send_response = requests.post(f"{base_url}/api/user/{user1['id']}/messages", json=message_data)
    print(f"Send response: {send_response.status_code}")
    
    if send_response.status_code == 200:
        send_data = send_response.json()
        message_id = send_data.get('id')
        print(f"✅ Message sent successfully: {message_id}")
    else:
        print(f"❌ Failed to send message: {send_response.text}")
        return
    
    # Step 3: Retrieve messages with user information
    print(f"\nStep 3: Retrieving messages for user2...")
    get_response = requests.get(f"{base_url}/api/user/{user2['id']}/messages")
    print(f"Get response: {get_response.status_code}")
    
    if get_response.status_code == 200:
        messages = get_response.json()
        print(f"Retrieved {len(messages)} messages")
        
        # Find our test message
        test_message = None
        for msg in messages:
            if msg.get('id') == message_id:
                test_message = msg
                break
        
        if test_message:
            print(f"✅ Found test message")
            print(f"  Sender Name: {test_message.get('sender_name')}")
            print(f"  Recipient Name: {test_message.get('recipient_name')}")
            print(f"  Expected Sender: {user1['full_name']}")
            print(f"  Expected Recipient: {user2['full_name']}")
            
            # Check if user information is correct
            sender_correct = test_message.get('sender_name') == user1['full_name']
            recipient_correct = test_message.get('recipient_name') == user2['full_name']
            
            if sender_correct and recipient_correct:
                print(f"✅ User information is correct")
            else:
                print(f"❌ User information incorrect - Sender: {sender_correct}, Recipient: {recipient_correct}")
        else:
            print(f"❌ Test message not found")
            return
    else:
        print(f"❌ Failed to retrieve messages: {get_response.text}")
        return
    
    # Step 4: Test conversation grouping
    print(f"\nStep 4: Testing conversation grouping...")
    user1_messages_response = requests.get(f"{base_url}/api/user/{user1['id']}/messages")
    
    if user1_messages_response.status_code == 200:
        user1_messages = user1_messages_response.json()
        
        # Group messages by conversation partner
        conversations = {}
        for message in user1_messages:
            other_user_name = message['recipient_name'] if message['sender_id'] == user1['id'] else message['sender_name']
            if other_user_name not in conversations:
                conversations[other_user_name] = []
            conversations[other_user_name].append(message)
        
        if user2['full_name'] in conversations:
            print(f"✅ Conversation grouping works - found conversation with {user2['full_name']}")
        else:
            print(f"❌ Conversation grouping failed - {user2['full_name']} not found")
            print(f"Available conversations: {list(conversations.keys())}")
    else:
        print(f"❌ Failed to get user1 messages for conversation test")
    
    # Step 5: Test mark as read
    print(f"\nStep 5: Testing mark as read...")
    read_response = requests.put(f"{base_url}/api/user/{user2['id']}/messages/{message_id}/read")
    print(f"Mark as read response: {read_response.status_code}")
    
    if read_response.status_code == 200:
        print(f"✅ Message marked as read successfully")
    else:
        print(f"❌ Failed to mark message as read: {read_response.text}")
    
    print(f"\n🎯 Complete flow test completed!")

if __name__ == "__main__":
    test_complete_flow()