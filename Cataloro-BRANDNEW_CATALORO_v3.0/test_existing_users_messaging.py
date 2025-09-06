#!/usr/bin/env python3
"""
Test messaging with existing users to verify sender_name and recipient_name functionality
"""

import requests
import json

def test_existing_users_messaging():
    base_url = "https://cataloro-ads.preview.emergentagent.com"
    
    # Login as admin user
    print("Logging in as admin user...")
    admin_login = requests.post(f"{base_url}/api/auth/login", json={"email": "admin@cataloro.com", "password": "demo123"})
    if admin_login.status_code != 200:
        print("Failed to login as admin")
        return
    
    admin_data = admin_login.json()
    admin_user = admin_data['user']
    admin_id = admin_user['id']
    print(f"Admin user: {admin_user['full_name']} (ID: {admin_id})")
    
    # Login as regular user
    print("\nLogging in as regular user...")
    user_login = requests.post(f"{base_url}/api/auth/login", json={"email": "user@cataloro.com", "password": "demo123"})
    if user_login.status_code != 200:
        print("Failed to login as regular user")
        return
    
    user_data = user_login.json()
    regular_user = user_data['user']
    user_id = regular_user['id']
    print(f"Regular user: {regular_user['full_name']} (ID: {user_id})")
    
    # Send message from admin to regular user
    print(f"\nSending message from admin ({admin_user['full_name']}) to regular user ({regular_user['full_name']})...")
    message_data = {
        "recipient_id": user_id,
        "subject": "Test Enhanced Messaging",
        "content": f"Hello {regular_user['full_name']}! This is a test message from {admin_user['full_name']} to verify enhanced messaging functionality."
    }
    
    send_response = requests.post(f"{base_url}/api/user/{admin_id}/messages", json=message_data)
    print(f"Send message response: {send_response.status_code}")
    if send_response.status_code == 200:
        send_data = send_response.json()
        print(f"Message sent successfully: {send_data}")
        message_id = send_data.get('id')
        
        # Get messages for regular user to see if sender_name is populated
        print(f"\nGetting messages for regular user ({regular_user['full_name']})...")
        get_response = requests.get(f"{base_url}/api/user/{user_id}/messages")
        print(f"Get messages response: {get_response.status_code}")
        
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
                print(f"\nTest message found:")
                print(f"  Subject: {test_message.get('subject')}")
                print(f"  Sender ID: {test_message.get('sender_id')}")
                print(f"  Recipient ID: {test_message.get('recipient_id')}")
                print(f"  Sender Name: {test_message.get('sender_name')}")
                print(f"  Recipient Name: {test_message.get('recipient_name')}")
                print(f"  Expected Sender: {admin_user['full_name']}")
                print(f"  Expected Recipient: {regular_user['full_name']}")
                
                # Verify enhanced fields
                if test_message.get('sender_name') == admin_user['full_name']:
                    print("  ✅ Sender name is correct")
                else:
                    print(f"  ❌ Sender name incorrect: expected '{admin_user['full_name']}', got '{test_message.get('sender_name')}'")
                
                if test_message.get('recipient_name') == regular_user['full_name']:
                    print("  ✅ Recipient name is correct")
                else:
                    print(f"  ❌ Recipient name incorrect: expected '{regular_user['full_name']}', got '{test_message.get('recipient_name')}'")
            else:
                print("  ❌ Test message not found in response")
        else:
            print(f"Failed to get messages: {get_response.text}")
    else:
        print(f"Failed to send message: {send_response.text}")
    
    # Test user search functionality
    print(f"\n\nTesting user search functionality...")
    search_response = requests.get(f"{base_url}/api/users/search", params={"q": "demo"})
    print(f"User search response: {search_response.status_code}")
    if search_response.status_code == 200:
        search_results = search_response.json()
        print(f"Found {len(search_results)} users matching 'demo':")
        for user in search_results:
            print(f"  - {user.get('display_name')} ({user.get('username')}) - ID: {user.get('id')}")
    else:
        print(f"User search failed: {search_response.text}")

if __name__ == "__main__":
    test_existing_users_messaging()