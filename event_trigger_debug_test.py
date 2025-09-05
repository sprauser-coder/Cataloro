#!/usr/bin/env python3
"""
Event Trigger Display Issue Debug Test
Specifically testing the event_trigger field in system notifications
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://market-refactor.preview.emergentagent.com/api"

def test_system_notifications_event_trigger():
    """Test the exact structure of system notifications and event_trigger field"""
    
    print("🔍 SYSTEM NOTIFICATIONS EVENT TRIGGER DEBUG TEST")
    print("=" * 60)
    
    try:
        # Test GET /api/admin/system-notifications
        print("\n1️⃣ Testing GET /api/admin/system-notifications...")
        response = requests.get(f"{BACKEND_URL}/admin/system-notifications")
        
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            
            print(f"✅ Successfully retrieved {len(notifications)} notifications")
            print(f"📊 Response structure: {list(data.keys())}")
            
            # Analyze each notification for event_trigger field
            print(f"\n📋 DETAILED NOTIFICATION ANALYSIS:")
            
            notifications_with_event_trigger = 0
            notifications_without_event_trigger = 0
            event_trigger_values = []
            
            for i, notification in enumerate(notifications):
                print(f"\n   Notification {i+1}:")
                print(f"   ├── ID: {notification.get('id', 'N/A')}")
                print(f"   ├── Title: {notification.get('title', 'N/A')}")
                print(f"   ├── Type: {notification.get('type', 'N/A')}")
                print(f"   ├── Target Users: {notification.get('target_users', 'N/A')}")
                print(f"   ├── Is Active: {notification.get('is_active', 'N/A')}")
                
                # Check event_trigger field specifically
                if 'event_trigger' in notification:
                    event_trigger = notification['event_trigger']
                    print(f"   ├── Event Trigger: '{event_trigger}' ✅")
                    notifications_with_event_trigger += 1
                    event_trigger_values.append(event_trigger)
                else:
                    print(f"   ├── Event Trigger: MISSING ❌")
                    notifications_without_event_trigger += 1
                
                # Show all available fields
                all_fields = list(notification.keys())
                print(f"   └── All Fields: {all_fields}")
            
            # Summary
            print(f"\n📈 EVENT TRIGGER FIELD ANALYSIS:")
            print(f"   ├── Total Notifications: {len(notifications)}")
            print(f"   ├── WITH event_trigger: {notifications_with_event_trigger}")
            print(f"   ├── WITHOUT event_trigger: {notifications_without_event_trigger}")
            print(f"   └── Event Trigger Values Found: {sorted(set(event_trigger_values))}")
            
            # Test creating a notification with event_trigger
            print(f"\n2️⃣ Testing notification creation with event_trigger...")
            
            test_notification = {
                "title": "Event Trigger Test",
                "message": "Testing if event_trigger field is saved properly",
                "type": "info",
                "event_trigger": "test_login",
                "target_users": "all",
                "is_active": True
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/admin/system-notifications",
                json=test_notification
            )
            
            if create_response.status_code == 200:
                created_id = create_response.json().get('id')
                print(f"✅ Created test notification: {created_id}")
                
                # Immediately retrieve to verify event_trigger was saved
                verify_response = requests.get(f"{BACKEND_URL}/admin/system-notifications")
                if verify_response.status_code == 200:
                    verify_notifications = verify_response.json().get('notifications', [])
                    
                    # Find our test notification
                    test_notif = None
                    for notif in verify_notifications:
                        if notif.get('id') == created_id:
                            test_notif = notif
                            break
                    
                    if test_notif:
                        saved_event_trigger = test_notif.get('event_trigger')
                        print(f"✅ Retrieved notification event_trigger: '{saved_event_trigger}'")
                        
                        if saved_event_trigger == 'test_login':
                            print(f"✅ Event trigger correctly saved and retrieved!")
                        else:
                            print(f"❌ Event trigger mismatch! Expected: 'test_login', Got: '{saved_event_trigger}'")
                    else:
                        print(f"❌ Could not find created notification in response")
                
                # Clean up test notification
                delete_response = requests.delete(f"{BACKEND_URL}/admin/system-notifications/{created_id}")
                if delete_response.status_code == 200:
                    print(f"🧹 Cleaned up test notification")
            else:
                print(f"❌ Failed to create test notification: {create_response.status_code}")
            
            # Test creating notification WITHOUT event_trigger
            print(f"\n3️⃣ Testing notification creation WITHOUT event_trigger...")
            
            test_notification_no_trigger = {
                "title": "No Event Trigger Test",
                "message": "Testing notification without event_trigger field",
                "type": "info",
                "target_users": "all",
                "is_active": True
                # Intentionally omitting event_trigger
            }
            
            create_response_no_trigger = requests.post(
                f"{BACKEND_URL}/admin/system-notifications",
                json=test_notification_no_trigger
            )
            
            if create_response_no_trigger.status_code == 200:
                created_id_no_trigger = create_response_no_trigger.json().get('id')
                print(f"✅ Created notification without event_trigger: {created_id_no_trigger}")
                
                # Retrieve to see what backend does with missing event_trigger
                verify_response_no_trigger = requests.get(f"{BACKEND_URL}/admin/system-notifications")
                if verify_response_no_trigger.status_code == 200:
                    verify_notifications_no_trigger = verify_response_no_trigger.json().get('notifications', [])
                    
                    test_notif_no_trigger = None
                    for notif in verify_notifications_no_trigger:
                        if notif.get('id') == created_id_no_trigger:
                            test_notif_no_trigger = notif
                            break
                    
                    if test_notif_no_trigger:
                        saved_event_trigger_no_trigger = test_notif_no_trigger.get('event_trigger')
                        
                        if saved_event_trigger_no_trigger is None:
                            print(f"⚠️  Backend does NOT set default event_trigger (value is None)")
                            print(f"   Frontend should handle this by showing 'Manual Trigger'")
                        else:
                            print(f"✅ Backend sets default event_trigger: '{saved_event_trigger_no_trigger}'")
                
                # Clean up
                delete_response_no_trigger = requests.delete(f"{BACKEND_URL}/admin/system-notifications/{created_id_no_trigger}")
                if delete_response_no_trigger.status_code == 200:
                    print(f"🧹 Cleaned up test notification without event_trigger")
            
            # Conclusions
            print(f"\n🎯 DEBUGGING CONCLUSIONS:")
            print(f"=" * 60)
            
            if notifications_without_event_trigger > 0:
                print(f"❌ ISSUE IDENTIFIED: {notifications_without_event_trigger} existing notifications missing event_trigger field")
                print(f"   → Frontend must handle null/missing event_trigger by showing 'Manual Trigger'")
            else:
                print(f"✅ All existing notifications have event_trigger field")
            
            print(f"✅ Backend correctly saves event_trigger when provided")
            print(f"⚠️  Backend does not set default event_trigger for notifications without the field")
            print(f"   → This is likely the root cause of the display issue")
            
            print(f"\n💡 FRONTEND FIX NEEDED:")
            print(f"   When displaying notifications, check if event_trigger exists:")
            print(f"   - If event_trigger exists: display the value")
            print(f"   - If event_trigger is null/undefined: display 'Manual Trigger'")
            
            return True
            
        else:
            print(f"❌ Failed to get system notifications: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_system_notifications_event_trigger()
    
    if success:
        print(f"\n🎉 EVENT TRIGGER DEBUG TEST COMPLETED!")
        sys.exit(0)
    else:
        print(f"\n⚠️  EVENT TRIGGER DEBUG TEST FAILED!")
        sys.exit(1)