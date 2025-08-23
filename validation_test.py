#!/usr/bin/env python3
"""
Additional validation testing for listing creation
"""

import requests
import json

BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    """Get admin token"""
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_validation_details():
    """Test specific validation scenarios"""
    token = get_admin_token()
    if not token:
        print("❌ Could not get admin token")
        return
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test cases
    test_cases = [
        {
            "name": "Missing price field",
            "data": {
                "title": "Test Product",
                "description": "Test description",
                "category": "Electronics",
                "condition": "New",
                "quantity": 1,
                "location": "Test City",
                "listing_type": "fixed_price"
                # price missing
            }
        },
        {
            "name": "Missing quantity field",
            "data": {
                "title": "Test Product",
                "description": "Test description", 
                "category": "Electronics",
                "condition": "New",
                "price": 99.99,
                "location": "Test City",
                "listing_type": "fixed_price"
                # quantity missing
            }
        },
        {
            "name": "Price as null",
            "data": {
                "title": "Test Product",
                "description": "Test description",
                "category": "Electronics", 
                "condition": "New",
                "price": None,
                "quantity": 1,
                "location": "Test City",
                "listing_type": "fixed_price"
            }
        },
        {
            "name": "Quantity as null",
            "data": {
                "title": "Test Product",
                "description": "Test description",
                "category": "Electronics",
                "condition": "New", 
                "price": 99.99,
                "quantity": None,
                "location": "Test City",
                "listing_type": "fixed_price"
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n🧪 Testing: {case['name']}")
        response = requests.post(f"{BACKEND_URL}/listings", json=case['data'], headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response: {response.text}")
        else:
            result = response.json()
            print(f"Created listing ID: {result.get('id')}")
            print(f"Price in response: {result.get('price')}")
            print(f"Quantity in response: {result.get('quantity')}")

if __name__ == "__main__":
    test_validation_details()