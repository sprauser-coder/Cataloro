#!/usr/bin/env python3
"""
Debug script to investigate messaging user lookup issues
"""

import requests
import json

def debug_messaging():
    base_url = "https://cat-db-market.preview.emergentagent.com"
    
    # Create a test user
    user_data = {
        "username": "debug_user",
        "email": "debug_user@example.com",
        "full_name": "Debug User"
    }
    
    print("Creating debug user...")
    response = requests.post(f"{base_url}/api/auth/register", json=user_data)
    print(f"Register response: {response.status_code}")
    if response.status_code == 200:
        print(f"Register data: {response.json()}")
    
    # Login to get user details
    print("\nLogging in debug user...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={"email": user_data["email"], "password": "test123"})
    print(f"Login response: {login_response.status_code}")
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"Login data: {json.dumps(login_data, indent=2)}")
        
        user = login_data['user']
        user_id = user['id']
        
        # Send a message to self to test
        print(f"\nSending message from user {user_id} to self...")
        message_data = {
            "recipient_id": user_id,
            "subject": "Debug Test",
            "content": "This is a debug test message"
        }
        
        send_response = requests.post(f"{base_url}/api/user/{user_id}/messages", json=message_data)
        print(f"Send message response: {send_response.status_code}")
        if send_response.status_code == 200:
            print(f"Send data: {send_response.json()}")
            
            # Get messages to see what happens
            print(f"\nGetting messages for user {user_id}...")
            get_response = requests.get(f"{base_url}/api/user/{user_id}/messages")
            print(f"Get messages response: {get_response.status_code}")
            if get_response.status_code == 200:
                messages = get_response.json()
                print(f"Messages: {json.dumps(messages, indent=2)}")
                
                if messages:
                    message = messages[0]
                    print(f"\nAnalyzing first message:")
                    print(f"  Sender ID: {message.get('sender_id')}")
                    print(f"  Recipient ID: {message.get('recipient_id')}")
                    print(f"  Sender Name: {message.get('sender_name')}")
                    print(f"  Recipient Name: {message.get('recipient_name')}")
                    print(f"  Expected User ID: {user_id}")
                    print(f"  Expected Full Name: {user['full_name']}")
                    
                    # Check if IDs match
                    if message.get('sender_id') == user_id:
                        print("  ✅ Sender ID matches")
                    else:
                        print("  ❌ Sender ID mismatch")
                    
                    if message.get('recipient_id') == user_id:
                        print("  ✅ Recipient ID matches")
                    else:
                        print("  ❌ Recipient ID mismatch")

if __name__ == "__main__":
    debug_messaging()