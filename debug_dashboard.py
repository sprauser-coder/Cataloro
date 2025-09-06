#!/usr/bin/env python3
"""
Debug Dashboard Database Connection
Check if the dashboard endpoint can access the database correctly
"""

import requests
import json

BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

def test_database_access():
    """Test various endpoints to debug database access"""
    
    print("=== DEBUGGING DASHBOARD DATABASE ACCESS ===")
    print()
    
    # Test 1: Check dashboard endpoint
    print("1. Testing dashboard endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/admin/dashboard")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Dashboard accessible")
            print(f"   KPIs: {data.get('kpis', {})}")
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")
    
    print()
    
    # Test 2: Check browse endpoint (should show listings)
    print("2. Testing browse endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/marketplace/browse")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Browse accessible, found {len(data)} listings")
            if len(data) > 0:
                print(f"   Sample listing: {data[0].get('title', 'Unknown')}")
        else:
            print(f"   ❌ Browse failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Browse error: {e}")
    
    print()
    
    # Test 3: Check users endpoint
    print("3. Testing admin users endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/admin/users")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Users accessible, found {len(data)} users")
            if len(data) > 0:
                print(f"   Sample user: {data[0].get('username', 'Unknown')}")
        else:
            print(f"   ❌ Users failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Users error: {e}")
    
    print()
    
    # Test 4: Check health endpoint
    print("4. Testing health endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check: {data}")
        else:
            print(f"   ❌ Health failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health error: {e}")
    
    print()
    print("=== ANALYSIS ===")
    print("If browse and users endpoints work but dashboard shows 0 values,")
    print("the issue is likely in the dashboard KPI calculation logic.")
    print("The database connection is working, but the count queries might be failing.")

if __name__ == "__main__":
    test_database_access()