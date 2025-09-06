#!/usr/bin/env python3
"""
System Notification Fix Testing using curl
Testing the system notification implementation and hardcoded message fix
"""

import subprocess
import json
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

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

def test_system_notification_fix():
    """Test the system notification fix implementation"""
    print("🔔 SYSTEM NOTIFICATION FIX TESTING (CURL VERSION)")
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
        
        notification_data = {
            "title": "Login Event Test",
            "message": "This is a test system notification triggered by login events",
            "type": "success",
            "target_users": "all",
            "show_duration": 5000,
            "is_active": True,
            "auto_dismiss": True
        }
        
        success, response = run_curl("POST", "admin/system-notifications", notification_data)
        
        if success and isinstance(response, dict):
            print("   ✅ Admin system notification creation: WORKING")
            notification_id = response.get("notification_id")
            print(f"   📝 Created notification ID: {notification_id}")
            results["admin_notification_creation"] = True
            results["passed_tests"] += 1
        else:
            print(f"   ❌ Admin system notification creation: FAILED")
            print(f"   📝 Response: {response}")
        
        # Test 2: Login event triggering
        print("\n2. Testing login event triggering...")
        
        login_data = {
            "email": "demo@cataloro.com",
            "password": "demo123"
        }
        
        success, response = run_curl("POST", "auth/login", login_data)
        
        if success and isinstance(response, dict):
            print("   ✅ Login endpoint: WORKING")
            test_user_id = response.get("user", {}).get("id")
            print(f"   📝 Logged in user ID: {test_user_id}")
            
            # Wait a moment for notification to be created
            time.sleep(2)
            
            # Check if login notification was created in user_notifications collection
            if test_user_id:
                success_notif, notif_response = run_curl("GET", f"user/{test_user_id}/notifications")
                if success_notif and isinstance(notif_response, list):
                    notifications = notif_response
                    
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
                    print(f"   ❌ Could not fetch user notifications")
            else:
                print("   ❌ Could not get user ID from login response")
        else:
            print(f"   ❌ Login endpoint: FAILED")
            print(f"   📝 Response: {response}")
        
        # Test 3: System notification retrieval
        print("\n3. Testing system notification retrieval...")
        
        if test_user_id:
            success, response = run_curl("GET", f"user/{test_user_id}/system-notifications")
            
            if success and isinstance(response, dict):
                print("   ✅ System notification retrieval endpoint: WORKING")
                notifications_list = response.get("notifications", [])
                print(f"   📝 Found {len(notifications_list)} system notification(s)")
                
                if notifications_list:
                    for notif in notifications_list[:2]:  # Show first 2
                        print(f"   📝 System notification: {notif.get('title')} - {notif.get('message')}")
                
                results["system_notification_retrieval"] = True
                results["passed_tests"] += 1
            else:
                print(f"   ❌ System notification retrieval: FAILED")
                print(f"   📝 Response: {response}")
        else:
            print("   ❌ Cannot test system notification retrieval without user ID")
        
        # Test 4: Verify hardcoded message fix
        print("\n4. Verifying hardcoded message fix...")
        
        # Check if the hardcoded "Welcome back to the new Cataloro" message is no longer generated
        if test_user_id:
            # Get all user notifications
            success, response = run_curl("GET", f"user/{test_user_id}/notifications")
            
            if success and isinstance(response, list):
                notifications = response
                
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
                print(f"   ❌ Could not verify hardcoded message fix")
        else:
            print("   ❌ Cannot verify hardcoded message fix without user ID")
        
        # Additional test: Test admin system notification management
        print("\n5. Testing admin system notification management...")
        
        success, response = run_curl("GET", "admin/system-notifications")
        
        if success and isinstance(response, dict):
            print("   ✅ Admin system notification listing: WORKING")
            notifications_list = response.get("notifications", [])
            print(f"   📝 Found {len(notifications_list)} admin system notification(s)")
            
            if notifications_list:
                for notif in notifications_list[:2]:  # Show first 2
                    print(f"   📝 Admin notification: {notif.get('title')} - {notif.get('type')}")
        else:
            print(f"   ❌ Admin system notification listing: FAILED")
        
        # Test notification view tracking
        if test_user_id and notification_id:
            print("\n6. Testing notification view tracking...")
            
            success, response = run_curl("POST", f"user/{test_user_id}/system-notifications/{notification_id}/view")
            
            if success:
                print("   ✅ Notification view tracking: WORKING")
                print("   📝 Successfully marked notification as viewed")
            else:
                print(f"   ❌ Notification view tracking: FAILED")
        
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