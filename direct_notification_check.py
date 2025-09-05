#!/usr/bin/env python3
"""
Direct Notification Database Check
Check what's actually in the user_notifications collection
"""

import requests
import json
import time

BACKEND_URL = "https://market-refactor.preview.emergentagent.com/api"

def check_all_notifications():
    """Check notifications for all known users"""
    print("🔍 DIRECT NOTIFICATION DATABASE CHECK")
    print("=" * 60)
    
    # Get all users first
    print("\n1. Getting all users...")
    
    users_response = requests.get(
        f"{BACKEND_URL}/admin/users",
        headers={"Content-Type": "application/json"}
    )
    
    if users_response.status_code == 200:
        users = users_response.json()
        print(f"📋 Found {len(users)} users")
        
        for i, user in enumerate(users):
            user_id = user.get('id')
            email = user.get('email', 'No email')
            print(f"   User {i+1}: {email} -> ID: {user_id}")
            
            # Check notifications for each user
            notif_response = requests.get(
                f"{BACKEND_URL}/user/notifications/{user_id}",
                headers={"Content-Type": "application/json"}
            )
            
            if notif_response.status_code == 200:
                notifications = notif_response.json()
                login_notifs = [
                    n for n in notifications 
                    if n.get('type') == 'system' and 'login' in n.get('message', '').lower()
                ]
                
                print(f"      📧 Total notifications: {len(notifications)}")
                print(f"      🔐 Login notifications: {len(login_notifs)}")
                
                if login_notifs:
                    print(f"      ✅ LOGIN NOTIFICATIONS FOUND!")
                    for j, notif in enumerate(login_notifs):
                        print(f"         Login {j+1}: {notif.get('title')} - {notif.get('message')}")
                        print(f"         Created: {notif.get('created_at')}")
                        print(f"         Notification user_id: {notif.get('user_id')}")
                
                # Show all notification types and user_ids
                if notifications:
                    print(f"      📋 All notification details:")
                    for j, notif in enumerate(notifications):
                        print(f"         {j+1}. Type: {notif.get('type')}, User ID: {notif.get('user_id')}, Title: {notif.get('title')}")
            else:
                print(f"      ❌ Failed to get notifications: {notif_response.status_code}")
            
            print()  # Empty line between users
    else:
        print(f"❌ Failed to get users: {users_response.status_code}")
    
    # Also try to trigger a fresh login and see what happens
    print("\n2. Triggering fresh login to see real-time behavior...")
    
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": "demo@cataloro.com", "password": "demo123"},
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        user_data = login_data.get('user', {})
        user_id = user_data.get('id')
        
        print(f"📋 Fresh login user ID: {user_id}")
        
        # Wait a moment
        time.sleep(2)
        
        # Check notifications immediately after login
        fresh_notif_response = requests.get(
            f"{BACKEND_URL}/user/notifications/{user_id}",
            headers={"Content-Type": "application/json"}
        )
        
        if fresh_notif_response.status_code == 200:
            fresh_notifications = fresh_notif_response.json()
            fresh_login_notifs = [
                n for n in fresh_notifications 
                if n.get('type') == 'system' and 'login' in n.get('message', '').lower()
            ]
            
            print(f"📧 Notifications after fresh login: {len(fresh_notifications)}")
            print(f"🔐 Login notifications after fresh login: {len(fresh_login_notifs)}")
            
            if fresh_login_notifs:
                print(f"✅ FRESH LOGIN NOTIFICATIONS FOUND!")
                for notif in fresh_login_notifs:
                    print(f"   - {notif.get('title')}: {notif.get('message')}")
                    print(f"   - Notification user_id: {notif.get('user_id')}")
                    print(f"   - Login response user_id: {user_id}")
                    print(f"   - IDs match: {notif.get('user_id') == user_id}")
            else:
                print(f"❌ No login notifications found after fresh login")
                print(f"📋 Available notification types: {[n.get('type') for n in fresh_notifications]}")
    
    print(f"\n" + "=" * 60)
    print("🔍 DIRECT CHECK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    check_all_notifications()