#!/usr/bin/env python3
"""
Debug the user search issue
"""

import requests
import json

def debug_search():
    base_url = "https://browse-ads.preview.emergentagent.com"
    
    # Create a test user
    user_data = {
        "username": "search_debug_user",
        "email": "search_debug_user@example.com",
        "full_name": "Search Debug User"
    }
    
    print("Creating test user...")
    register_response = requests.post(f"{base_url}/api/auth/register", json=user_data)
    print(f"Register response: {register_response.status_code}")
    
    if register_response.status_code == 200:
        register_data = register_response.json()
        print(f"Register data: {register_data}")
        
        # Login to get user details
        login_response = requests.post(f"{base_url}/api/auth/login", json={"email": user_data["email"], "password": "test123"})
        print(f"Login response: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            user = login_data['user']
            print(f"User created: {user['full_name']} (ID: {user['id']}, Username: {user['username']})")
            
            # Test different search terms
            search_terms = [
                user['username'][:4],  # First 4 chars of username
                user['username'],      # Full username
                user['full_name'].split()[0],  # First name
                "search",              # Part of username
                "debug"                # Part of username
            ]
            
            for term in search_terms:
                print(f"\nSearching for '{term}'...")
                search_response = requests.get(f"{base_url}/api/users/search", params={"q": term})
                print(f"Search response: {search_response.status_code}")
                
                if search_response.status_code == 200:
                    results = search_response.json()
                    print(f"Found {len(results)} users:")
                    
                    found_our_user = False
                    for result in results:
                        print(f"  - {result.get('display_name')} ({result.get('username')}) - ID: {result.get('id')}")
                        if result.get('id') == user['id']:
                            found_our_user = True
                    
                    if found_our_user:
                        print(f"  ✅ Found our test user")
                    else:
                        print(f"  ❌ Our test user not found")
                else:
                    print(f"Search failed: {search_response.text}")

if __name__ == "__main__":
    debug_search()