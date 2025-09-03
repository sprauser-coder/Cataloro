#!/usr/bin/env python3
"""
Simple System Notification Test - Final Verification
Tests the system notification fix as requested in review
"""

import requests
import json
import time

def test_system_notifications():
    base_url = "https://market-upgrade-2.preview.emergentagent.com"
    
    print("🚀 SYSTEM NOTIFICATION FIX - FINAL VERIFICATION")
    print("=" * 60)
    
    # Test users as specified in review
    test_users = [
        ("demo@cataloro.com", "Demo User"),
        ("admin@cataloro.com", "Admin User")
    ]
    
    results = []
    
    for email, user_type in test_users:
        print(f"\n🔐 Testing {user_type}: {email}")
        print("-" * 40)
        
        # Step 1: Login
        try:
            login_response = requests.post(
                f"{base_url}/api/auth/login",
                json={"email": email, "password": "demo123"},
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                results.append((email, False, "Login failed"))
                continue
            
            login_data = login_response.json()
            user = login_data.get('user')
            
            if not user or not user.get('id'):
                print(f"❌ No user data in login response")
                results.append((email, False, "No user data"))
                continue
            
            user_id = user.get('id')
            print(f"✅ Login successful - User ID: {user_id}")
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            results.append((email, False, f"Login error: {e}"))
            continue
        
        # Step 2: Wait for notification processing
        print("⏳ Waiting 3 seconds for notification processing...")
        time.sleep(3)
        
        # Step 3: Check notifications
        try:
            notif_response = requests.get(
                f"{base_url}/api/user/{user_id}/notifications",
                headers={'Content-Type': 'application/json'}
            )
            
            if notif_response.status_code != 200:
                print(f"❌ Notification retrieval failed: {notif_response.status_code}")
                results.append((email, False, "Notification retrieval failed"))
                continue
            
            notifications = notif_response.json()
            print(f"📬 Retrieved {len(notifications)} notifications")
            
            # Check for login notifications and user ID consistency
            login_notifications = 0
            matching_user_ids = 0
            mismatched_user_ids = 0
            hardcoded_messages = 0
            
            for notif in notifications:
                # Handle both dict and string formats
                if isinstance(notif, dict):
                    notif_user_id = notif.get('user_id')
                    notif_type = notif.get('type', '')
                    message = notif.get('message', '')
                    title = notif.get('title', '')
                    
                    # Check user ID consistency
                    if notif_user_id == user_id:
                        matching_user_ids += 1
                    else:
                        mismatched_user_ids += 1
                        print(f"   ⚠️  User ID mismatch - Expected: {user_id}, Found: {notif_user_id}")
                    
                    # Check for login notifications
                    if (notif_type == 'system' and 
                        ('login' in message.lower() or 'welcome' in message.lower() or
                         'login' in title.lower() or 'welcome' in title.lower())):
                        login_notifications += 1
                        print(f"   🎯 Login notification found: {title}")
                    
                    # Check for hardcoded messages
                    if 'Welcome back to the new Cataloro' in message:
                        hardcoded_messages += 1
                        print(f"   ⚠️  Hardcoded message found: {message}")
                
                elif isinstance(notif, str):
                    print(f"   ⚠️  Notification is string format: {notif[:50]}...")
            
            print(f"📊 Login notifications: {login_notifications}")
            print(f"📊 Matching user IDs: {matching_user_ids}")
            print(f"📊 Mismatched user IDs: {mismatched_user_ids}")
            print(f"📊 Hardcoded messages: {hardcoded_messages}")
            
            # Determine success
            success = (
                login_notifications > 0 and 
                matching_user_ids > 0 and 
                mismatched_user_ids == 0 and
                hardcoded_messages == 0
            )
            
            if success:
                print(f"✅ {user_type} - ALL TESTS PASSED")
                results.append((email, True, "All tests passed"))
            else:
                issues = []
                if login_notifications == 0:
                    issues.append("No login notifications")
                if matching_user_ids == 0:
                    issues.append("No matching user IDs")
                if mismatched_user_ids > 0:
                    issues.append(f"{mismatched_user_ids} mismatched user IDs")
                if hardcoded_messages > 0:
                    issues.append(f"{hardcoded_messages} hardcoded messages")
                
                print(f"❌ {user_type} - ISSUES: {', '.join(issues)}")
                results.append((email, False, ', '.join(issues)))
            
        except Exception as e:
            print(f"❌ Notification check error: {e}")
            results.append((email, False, f"Notification error: {e}"))
    
    # Final Summary
    print(f"\n{'='*60}")
    print("FINAL SYSTEM NOTIFICATION TEST RESULTS")
    print(f"{'='*60}")
    
    successful_users = sum(1 for _, success, _ in results if success)
    total_users = len(results)
    
    for email, success, details in results:
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{email}: {status} - {details}")
    
    print(f"\n🎯 Overall Result: {successful_users}/{total_users} users working")
    
    if successful_users == total_users:
        print(f"\n🎉 SYSTEM NOTIFICATION FIX: ✅ WORKING COMPLETELY")
        print("✅ Login notification creation with proper user ID - WORKING")
        print("✅ User ID consistency between login and notifications - WORKING") 
        print("✅ Notification retrieval via API - WORKING")
        print("✅ Complete flow (Login → Creation → Retrieval) - WORKING")
        print("✅ No hardcoded 'Welcome back to the new Cataloro' messages - WORKING")
        print("\n🎯 The ENTIRE system notification system is now working end-to-end.")
        return True
    else:
        print(f"\n❌ SYSTEM NOTIFICATION FIX: ❌ ISSUES FOUND")
        print("The system notification fix needs additional work.")
        return False

if __name__ == "__main__":
    success = test_system_notifications()
    exit(0 if success else 1)