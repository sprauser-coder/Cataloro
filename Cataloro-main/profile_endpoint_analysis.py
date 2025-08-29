#!/usr/bin/env python3
from config_loader import get_config, get_backend_url, get_admin_credentials, get_paths, get_database_url
"""
Profile Endpoint Analysis - Check which endpoints exist and work
"""

import requests
import json

BACKEND_URL = "get_backend_url()/api"
session = requests.Session()

# Login first
response = session.post(f"{BACKEND_URL}/auth/login", json={
    "email": "get_admin_credentials()[0]",
    "password": "get_admin_credentials()[1]"
})

if response.status_code == 200:
    token = response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("✅ Authentication successful\n")
    
    # Test all requested endpoints
    endpoints = [
        ("GET /api/profile/stats", "/profile/stats"),
        ("GET /api/profile/activity", "/profile/activity"),
        ("PUT /api/profile", "/profile"),
        ("POST /api/profile/upload-picture", "/profile/upload-picture"),
        ("GET /api/messages", "/messages"),
        ("GET /api/reviews/user", "/reviews/user"),
        ("GET /api/orders", "/orders"),
        ("GET /api/listings/user", "/listings/user"),
        ("GET /api/listings/my-listings", "/listings/my-listings"),  # Alternative
    ]
    
    for name, endpoint in endpoints:
        try:
            if "POST" in name:
                # Skip POST tests for now
                print(f"{name}: SKIPPED (POST test)")
                continue
            elif "PUT" in name:
                # Test PUT with minimal data
                resp = session.put(f"{BACKEND_URL}{endpoint}", json={"full_name": "Test Update"})
            else:
                resp = session.get(f"{BACKEND_URL}{endpoint}")
            
            print(f"{name}: Status {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    print(f"  ✅ Returns list with {len(data)} items")
                    if len(data) > 0:
                        print(f"  Sample keys: {list(data[0].keys())}")
                elif isinstance(data, dict):
                    print(f"  ✅ Returns dict with keys: {list(data.keys())}")
                else:
                    print(f"  ✅ Returns: {type(data)}")
            else:
                print(f"  ❌ Error: {resp.text[:100]}")
                
        except Exception as e:
            print(f"{name}: Exception {str(e)}")
        
        print()

else:
    print("❌ Authentication failed")