#!/usr/bin/env python3
"""
User ID Mismatch Investigation Test
Tests the specific user ID mismatch issue in login notifications
"""

import requests
import json
import time

BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

def test_user_id_mismatch():
    """Test and demonstrate the user ID mismatch issue"""
    print("🔍 USER ID MISMATCH INVESTIGATION")
    print("=" * 60)
    
    # Step 1: Login and capture all user ID variations
    print("\n1. Testing login and user ID handling...")
    
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": "demo@cataloro.com", "password": "demo123"},
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    login_data = login_response.json()
    user_data = login_data.get('user', {})
    
    print(f"📋 Login response user ID: {user_data.get('id')}")
    print(f"📋 User data keys: {list(user_data.keys())}")
    
    # Step 2: Check what notifications exist for this user ID
    user_id_from_response = user_data.get('id')
    
    print(f"\n2. Checking notifications for user ID from login response...")
    
    notif_response = requests.get(
        f"{BACKEND_URL}/user/notifications/{user_id_from_response}",
        headers={"Content-Type": "application/json"}
    )
    
    if notif_response.status_code == 200:
        notifications = notif_response.json()
        print(f"📧 Notifications found: {len(notifications)}")
        
        login_notifs = [
            n for n in notifications 
            if n.get('type') == 'system' and 'login' in n.get('message', '').lower()
        ]
        print(f"🔐 Login notifications: {len(login_notifs)}")
        
        if login_notifs:
            for i, notif in enumerate(login_notifs):
                print(f"   Login notification {i+1}: user_id={notif.get('user_id')}, message={notif.get('message')}")
        
        # Show all notification user_ids to see the mismatch
        print(f"\n📋 All notification user_ids:")
        for i, notif in enumerate(notifications):
            print(f"   Notification {i+1}: user_id={notif.get('user_id')}, type={notif.get('type')}")
    else:
        print(f"❌ Failed to get notifications: {notif_response.status_code}")
    
    # Step 3: Try to find notifications with different user ID formats
    print(f"\n3. Searching for notifications with different user ID formats...")
    
    # Try some common ObjectId patterns that might be in the database
    potential_user_ids = [
        user_id_from_response,  # The ID from login response
        "68b801f25279c388d71649eb",  # Known ObjectId from logs
        "68b191ec38e6062fee10bd27",  # Admin ObjectId from logs
    ]
    
    for test_user_id in potential_user_ids:
        print(f"\n   Testing user ID: {test_user_id}")
        
        test_response = requests.get(
            f"{BACKEND_URL}/user/notifications/{test_user_id}",
            headers={"Content-Type": "application/json"}
        )
        
        if test_response.status_code == 200:
            test_notifications = test_response.json()
            login_test_notifs = [
                n for n in test_notifications 
                if n.get('type') == 'system' and 'login' in n.get('message', '').lower()
            ]
            
            print(f"   📧 Total notifications: {len(test_notifications)}")
            print(f"   🔐 Login notifications: {len(login_test_notifs)}")
            
            if login_test_notifs:
                print(f"   ✅ FOUND LOGIN NOTIFICATIONS!")
                for notif in login_test_notifs[:2]:
                    print(f"      - {notif.get('title')}: {notif.get('message')}")
                    print(f"      - Created: {notif.get('created_at')}")
                    print(f"      - Notification user_id: {notif.get('user_id')}")
        else:
            print(f"   ❌ No notifications for this user ID: {test_response.status_code}")
    
    print(f"\n" + "=" * 60)
    print("🔍 INVESTIGATION COMPLETE")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_user_id_mismatch()