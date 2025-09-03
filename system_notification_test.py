#!/usr/bin/env python3
"""
System Notification Fix Testing
Testing the system notification implementation and hardcoded message fix
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://tender-fix.preview.emergentagent.com/api"

def test_system_notification_fix():
    """Test the system notification fix implementation"""
    print("🔔 SYSTEM NOTIFICATION FIX TESTING")
    print("=" * 60)
    
    results = {
        "admin_notification_creation": False,
        "login_event_triggering": False,
        "system_notification_retrieval": False,
        "hardcoded_message_fix": False,
        "total_tests": 4,
        "passed_tests": 0
    }
    
    notification_id = None
    test_user_id = None
    
    try:
        # Test 1: System notification creation via admin API
        print("\n1. Testing system notification creation via admin API...")
        
        # Create a system notification with login event trigger
        notification_data = {
            "title": "Login Event Test",
            "message": "This is a test system notification triggered by login events",
            "type": "success",
            "target_users": "all",
            "show_duration": 5000,
            "is_active": True,
            "auto_dismiss": True
        }
        
        response = requests.post(
            f"{BACKEND_URL}/admin/system-notifications",
            json=notification_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("   ✅ Admin system notification creation: WORKING")
            admin_notification = response.json()
            notification_id = admin_notification.get("notification_id")
            print(f"   📝 Created notification ID: {notification_id}")
            results["admin_notification_creation"] = True
            results["passed_tests"] += 1
        else:
            print(f"   ❌ Admin system notification creation: FAILED ({response.status_code})")
            print(f"   📝 Response: {response.text}")
        
        # Test 2: Login event triggering
        print("\n2. Testing login event triggering...")
        
        # Login with demo user to trigger system notifications
        login_data = {
            "email": "demo@cataloro.com",
            "password": "demo123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("   ✅ Login endpoint: WORKING")
            login_result = response.json()
            test_user_id = login_result.get("user", {}).get("id")
            print(f"   📝 Logged in user ID: {test_user_id}")
            
            # Wait a moment for notification to be created
            time.sleep(2)
            
            # Check if login notification was created in user_notifications collection
            if test_user_id:
                response = requests.get(f"{BACKEND_URL}/user/{test_user_id}/notifications")
                if response.status_code == 200:
                    notifications = response.json()
                    
                    # Look for login-triggered notifications
                    login_notifications = [n for n in notifications if 
                                         "Welcome back" in n.get("title", "") or 
                                         "logged in" in n.get("message", "")]
                    
                    if login_notifications:
                        print("   ✅ Login event notification triggering: WORKING")
                        print(f"   📝 Found {len(login_notifications)} login notification(s)")
                        for notif in login_notifications[:1]:  # Show first one
                            print(f"   📝 Notification: {notif.get('title')} - {notif.get('message')}")
                        results["login_event_triggering"] = True
                        results["passed_tests"] += 1
                    else:
                        print("   ❌ Login event notification triggering: NO NOTIFICATIONS FOUND")
                        print(f"   📝 Total notifications found: {len(notifications)}")
                else:
                    print(f"   ❌ Could not fetch user notifications ({response.status_code})")
            else:
                print("   ❌ Could not get user ID from login response")
        else:
            print(f"   ❌ Login endpoint: FAILED ({response.status_code})")
            print(f"   📝 Response: {response.text}")
        
        # Test 3: System notification retrieval
        print("\n3. Testing system notification retrieval...")
        
        if test_user_id:
            response = requests.get(f"{BACKEND_URL}/user/{test_user_id}/system-notifications")
            
            if response.status_code == 200:
                print("   ✅ System notification retrieval endpoint: WORKING")
                system_notifications = response.json()
                notifications_list = system_notifications.get("notifications", [])
                print(f"   📝 Found {len(notifications_list)} system notification(s)")
                
                if notifications_list:
                    for notif in notifications_list[:2]:  # Show first 2
                        print(f"   📝 System notification: {notif.get('title')} - {notif.get('message')}")
                
                results["system_notification_retrieval"] = True
                results["passed_tests"] += 1
            else:
                print(f"   ❌ System notification retrieval: FAILED ({response.status_code})")
                print(f"   📝 Response: {response.text}")
        else:
            print("   ❌ Cannot test system notification retrieval without user ID")
        
        # Test 4: Verify hardcoded message fix
        print("\n4. Verifying hardcoded message fix...")
        
        # Check if the hardcoded "Welcome back to the new Cataloro" message is no longer generated
        if test_user_id:
            # Get all user notifications
            response = requests.get(f"{BACKEND_URL}/user/{test_user_id}/notifications")
            
            if response.status_code == 200:
                notifications = response.json()
                
                # Look for the old hardcoded message
                hardcoded_messages = [n for n in notifications if 
                                    "Welcome back to the new Cataloro" in n.get("message", "")]
                
                if not hardcoded_messages:
                    print("   ✅ Hardcoded message fix: VERIFIED")
                    print("   📝 No hardcoded 'Welcome back to the new Cataloro' messages found")
                    results["hardcoded_message_fix"] = True
                    results["passed_tests"] += 1
                else:
                    print("   ❌ Hardcoded message fix: FAILED")
                    print(f"   📝 Found {len(hardcoded_messages)} hardcoded message(s)")
                    for msg in hardcoded_messages[:1]:
                        print(f"   📝 Hardcoded message: {msg.get('message')}")
            else:
                print(f"   ❌ Could not verify hardcoded message fix ({response.status_code})")
        else:
            print("   ❌ Cannot verify hardcoded message fix without user ID")
        
        # Additional test: Test admin system notification management
        print("\n5. Testing admin system notification management...")
        
        # Get all system notifications
        response = requests.get(f"{BACKEND_URL}/admin/system-notifications")
        
        if response.status_code == 200:
            print("   ✅ Admin system notification listing: WORKING")
            admin_notifications = response.json()
            notifications_list = admin_notifications.get("notifications", [])
            print(f"   📝 Found {len(notifications_list)} admin system notification(s)")
            
            if notifications_list:
                for notif in notifications_list[:2]:  # Show first 2
                    print(f"   📝 Admin notification: {notif.get('title')} - {notif.get('type')}")
        else:
            print(f"   ❌ Admin system notification listing: FAILED ({response.status_code})")
        
        # Test notification view tracking
        if test_user_id and notification_id:
            print("\n6. Testing notification view tracking...")
            
            response = requests.post(f"{BACKEND_URL}/user/{test_user_id}/system-notifications/{notification_id}/view")
            
            if response.status_code == 200:
                print("   ✅ Notification view tracking: WORKING")
                print("   📝 Successfully marked notification as viewed")
            else:
                print(f"   ❌ Notification view tracking: FAILED ({response.status_code})")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SYSTEM NOTIFICATION FIX TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Tests Passed: {results['passed_tests']}/{results['total_tests']}")
    print(f"❌ Tests Failed: {results['total_tests'] - results['passed_tests']}/{results['total_tests']}")
    
    success_rate = (results['passed_tests'] / results['total_tests']) * 100
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print("\nDetailed Results:")
    print(f"  • Admin notification creation: {'✅ PASS' if results['admin_notification_creation'] else '❌ FAIL'}")
    print(f"  • Login event triggering: {'✅ PASS' if results['login_event_triggering'] else '❌ FAIL'}")
    print(f"  • System notification retrieval: {'✅ PASS' if results['system_notification_retrieval'] else '❌ FAIL'}")
    print(f"  • Hardcoded message fix: {'✅ PASS' if results['hardcoded_message_fix'] else '❌ FAIL'}")
    
    if results['passed_tests'] == results['total_tests']:
        print("\n🎉 ALL SYSTEM NOTIFICATION TESTS PASSED!")
        print("The system notification fix is working correctly.")
    else:
        print(f"\n⚠️  {results['total_tests'] - results['passed_tests']} TEST(S) FAILED")
        print("Some system notification functionality needs attention.")
    
    return results

if __name__ == "__main__":
    test_system_notification_fix()