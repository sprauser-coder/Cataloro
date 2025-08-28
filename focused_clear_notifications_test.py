#!/usr/bin/env python3
"""
Focused Clear Notifications Endpoint Testing
============================================

This script specifically tests the clear notifications endpoint functionality:
1. GET /api/notifications - Check existing notifications
2. DELETE /api/notifications/clear-all - Test the new clear all notifications endpoint
3. GET /api/notifications - Verify notifications are permanently cleared

Admin credentials: admin@marketplace.com / admin123
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://admin-rebuild.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def test_clear_notifications():
    """Test the clear notifications functionality"""
    session = requests.Session()
    
    print("=" * 60)
    print("FOCUSED CLEAR NOTIFICATIONS ENDPOINT TESTING")
    print("=" * 60)
    
    # Step 1: Authenticate
    print("\n1. Authenticating as admin...")
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            session.headers.update({"Authorization": f"Bearer {token}"})
            print("✅ Successfully authenticated as admin")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False
    
    # Step 2: Check initial notifications
    print("\n2. Checking existing notifications...")
    try:
        response = session.get(f"{BACKEND_URL}/notifications")
        
        if response.status_code == 200:
            data = response.json()
            initial_notifications = data.get("notifications", [])
            initial_unread = data.get("unread_count", 0)
            print(f"✅ Found {len(initial_notifications)} notifications ({initial_unread} unread)")
        else:
            print(f"❌ Failed to get notifications: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting notifications: {str(e)}")
        return False
    
    # Step 3: Test clear all notifications endpoint
    print("\n3. Testing DELETE /api/notifications/clear-all endpoint...")
    try:
        response = session.delete(f"{BACKEND_URL}/notifications/clear-all")
        
        if response.status_code == 200:
            data = response.json()
            deleted_count = data.get("deleted_count", 0)
            message = data.get("message", "")
            print(f"✅ Clear endpoint successful: {message}")
            print(f"   Deleted {deleted_count} notifications")
        else:
            print(f"❌ Clear endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error calling clear endpoint: {str(e)}")
        return False
    
    # Step 4: Verify notifications are cleared
    print("\n4. Verifying notifications are permanently cleared...")
    try:
        response = session.get(f"{BACKEND_URL}/notifications")
        
        if response.status_code == 200:
            data = response.json()
            final_notifications = data.get("notifications", [])
            final_unread = data.get("unread_count", 0)
            
            if len(final_notifications) == 0 and final_unread == 0:
                print("✅ All notifications successfully cleared from database")
                print("   No notifications remaining")
            else:
                print(f"❌ Notifications not fully cleared: {len(final_notifications)} remaining ({final_unread} unread)")
                return False
        else:
            print(f"❌ Failed to verify clearing: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verifying clearing: {str(e)}")
        return False
    
    # Step 5: Test endpoint behavior with no notifications
    print("\n5. Testing clear endpoint with no notifications...")
    try:
        response = session.delete(f"{BACKEND_URL}/notifications/clear-all")
        
        if response.status_code == 200:
            data = response.json()
            deleted_count = data.get("deleted_count", 0)
            message = data.get("message", "")
            print(f"✅ Clear endpoint handles empty state correctly: {message}")
            print(f"   Deleted {deleted_count} notifications (expected 0)")
        else:
            print(f"❌ Clear endpoint failed on empty state: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing empty state: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("✅ GET /api/notifications endpoint working")
    print("✅ DELETE /api/notifications/clear-all endpoint working")
    print("✅ Notifications permanently cleared from database")
    print("✅ Endpoint handles empty state correctly")
    print("=" * 60)
    
    return True

def main():
    """Main test execution"""
    try:
        success = test_clear_notifications()
        
        if success:
            print("\n🎉 CLEAR NOTIFICATIONS FUNCTIONALITY CONFIRMED WORKING!")
            sys.exit(0)
        else:
            print("\n💥 CLEAR NOTIFICATIONS FUNCTIONALITY HAS ISSUES!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()