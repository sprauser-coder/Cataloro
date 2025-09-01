#!/usr/bin/env python3
"""
Debug script to investigate user lookup issues in messaging
"""

import requests
import json

def debug_user_lookup():
    base_url = "https://trade-platform-30.preview.emergentagent.com"
    
    # Get all users to see how they're stored
    print("Getting all users from admin endpoint...")
    admin_login = requests.post(f"{base_url}/api/auth/login", json={"email": "admin@cataloro.com", "password": "demo123"})
    if admin_login.status_code == 200:
        print("Admin login successful")
        
        users_response = requests.get(f"{base_url}/api/admin/users")
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"Found {len(users)} users in database:")
            
            for i, user in enumerate(users[:5]):  # Show first 5 users
                print(f"  User {i+1}:")
                print(f"    ID: {user.get('id')}")
                print(f"    Username: {user.get('username')}")
                print(f"    Full Name: {user.get('full_name')}")
                print(f"    Email: {user.get('email')}")
                print(f"    MongoDB _id: {user.get('_id')}")
                print()
            
            # Test user lookup directly
            if users:
                test_user = users[0]
                user_id = test_user.get('id')
                print(f"Testing user profile lookup for ID: {user_id}")
                
                profile_response = requests.get(f"{base_url}/api/auth/profile/{user_id}")
                print(f"Profile lookup response: {profile_response.status_code}")
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(f"Profile data: {json.dumps(profile_data, indent=2)}")
                else:
                    print(f"Profile lookup failed: {profile_response.text}")
        else:
            print(f"Failed to get users: {users_response.status_code}")
    else:
        print(f"Admin login failed: {admin_login.status_code}")

if __name__ == "__main__":
    debug_user_lookup()