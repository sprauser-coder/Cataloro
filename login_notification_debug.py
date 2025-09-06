#!/usr/bin/env python3
"""
Debug login notification creation
"""

import subprocess
import json
import time

BACKEND_URL = "https://cataloro-ads.preview.emergentagent.com/api"

def run_curl(method, endpoint, data=None):
    """Run curl command and return response"""
    url = f"{BACKEND_URL}/{endpoint}"
    
    if method == "GET":
        cmd = ["curl", "-s", url]
    elif method == "POST":
        cmd = ["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json"]
        if data:
            cmd.extend(["-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            try:
                return True, json.loads(result.stdout)
            except json.JSONDecodeError:
                return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def test_login_notification():
    print("🔍 DEBUGGING LOGIN NOTIFICATION CREATION")
    print("=" * 50)
    
    # Step 1: Login with a new user
    print("\n1. Logging in with new user...")
    login_data = {
        "email": f"testlogin{int(time.time())}@cataloro.com",
        "password": "demo123"
    }
    
    success, response = run_curl("POST", "auth/login", login_data)
    
    if not success or not isinstance(response, dict):
        print(f"❌ Login failed: {response}")
        return
    
    user_id = response.get("user", {}).get("id")
    print(f"✅ Login successful, user ID: {user_id}")
    
    # Step 2: Check notifications immediately
    print("\n2. Checking notifications immediately after login...")
    success, notifications = run_curl("GET", f"user/{user_id}/notifications")
    
    if success and isinstance(notifications, list):
        print(f"📝 Found {len(notifications)} notifications immediately after login")
        for notif in notifications:
            print(f"   - {notif.get('title')}: {notif.get('message')}")
    else:
        print(f"❌ Failed to get notifications: {notifications}")
    
    # Step 3: Wait and check again
    print("\n3. Waiting 3 seconds and checking again...")
    time.sleep(3)
    
    success, notifications = run_curl("GET", f"user/{user_id}/notifications")
    
    if success and isinstance(notifications, list):
        print(f"📝 Found {len(notifications)} notifications after waiting")
        for notif in notifications:
            print(f"   - {notif.get('title')}: {notif.get('message')}")
    else:
        print(f"❌ Failed to get notifications: {notifications}")
    
    # Step 4: Manually create a notification to verify the endpoint works
    print("\n4. Manually creating a notification to verify endpoint...")
    manual_notif = {
        "title": "Manual Test",
        "message": "This is a manually created notification",
        "type": "info"
    }
    
    success, response = run_curl("POST", f"user/{user_id}/notifications", manual_notif)
    
    if success:
        print(f"✅ Manual notification created: {response}")
        
        # Check if it appears
        success, notifications = run_curl("GET", f"user/{user_id}/notifications")
        if success and isinstance(notifications, list):
            print(f"📝 Now found {len(notifications)} notifications total")
            for notif in notifications:
                print(f"   - {notif.get('title')}: {notif.get('message')}")
    else:
        print(f"❌ Failed to create manual notification: {response}")
    
    # Step 5: Check if login notifications are in a different collection
    print("\n5. Checking system notifications for this user...")
    success, sys_notifications = run_curl("GET", f"user/{user_id}/system-notifications")
    
    if success and isinstance(sys_notifications, dict):
        sys_notif_list = sys_notifications.get("notifications", [])
        print(f"📝 Found {len(sys_notif_list)} system notifications")
        for notif in sys_notif_list:
            print(f"   - {notif.get('title')}: {notif.get('message')}")
    else:
        print(f"❌ Failed to get system notifications: {sys_notifications}")

if __name__ == "__main__":
    test_login_notification()