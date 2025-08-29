#!/usr/bin/env python3
from config_loader import get_config, get_backend_url, get_admin_credentials, get_paths, get_database_url
"""
Debug authentication issue
"""

import requests
import json

# Test with fresh login
login_data = {
    "email": "get_admin_credentials()[0]",
    "password": "get_admin_credentials()[1]"
}

print("🔐 Testing fresh login...")
response = requests.post("get_backend_url()/api/auth/login", json=login_data)

if response.status_code == 200:
    data = response.json()
    token = data.get("access_token")
    user = data.get("user", {})
    
    print(f"✅ Login successful")
    print(f"   User: {user.get('full_name')} ({user.get('email')})")
    print(f"   Role: {user.get('role')}")
    print(f"   Blocked: {user.get('is_blocked')}")
    print(f"   Token: {token[:50]}...")
    
    # Test admin endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🧪 Testing admin endpoint...")
    admin_response = requests.get("get_backend_url()/api/admin/stats", headers=headers)
    
    print(f"Admin stats response: {admin_response.status_code}")
    if admin_response.status_code != 200:
        print(f"Error: {admin_response.text}")
    else:
        print("✅ Admin endpoint accessible")
        
    # Test catalyst endpoint
    print("\n🧪 Testing catalyst endpoint...")
    catalyst_response = requests.get("get_backend_url()/api/admin/catalyst-basis", headers=headers)
    
    print(f"Catalyst basis response: {catalyst_response.status_code}")
    if catalyst_response.status_code != 200:
        print(f"Error: {catalyst_response.text}")
    else:
        print("✅ Catalyst endpoint accessible")
        print(f"Response: {catalyst_response.json()}")
        
else:
    print(f"❌ Login failed: {response.status_code}")
    print(f"Error: {response.text}")