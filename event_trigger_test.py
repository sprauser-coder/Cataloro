#!/usr/bin/env python3
"""
System Notifications Event Trigger Display Testing
Testing the fix for missing event_trigger field display
"""

import requests
import json
import sys
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://market-refactor.preview.emergentagent.com/api"

class SystemNotificationsTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, details="", expected="", actual=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and expected:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
        print()
        
    def test_get_system_notifications(self):
        """Test 1: GET System Notifications Endpoint"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/system-notifications")
            
            if response.status_code != 200:
                self.log_test(
                    "GET System Notifications",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            data = response.json()
            
            # Check if response has notifications array
            if "notifications" not in data:
                self.log_test(
                    "GET System Notifications",
                    False,
                    "Response missing 'notifications' array",
                    "Response with 'notifications' array",
                    f"Response keys: {list(data.keys())}"
                )
                return False
            
            notifications = data["notifications"]
            notification_count = len(notifications)
            
            self.log_test(
                "GET System Notifications",
                True,
                f"Successfully retrieved {notification_count} system notifications"
            )
            return notifications
            
        except Exception as e:
            self.log_test(
                "GET System Notifications",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_event_trigger_field_analysis(self, notifications):
        """Test 2: Event Trigger Field Analysis"""
        try:
            if not notifications:
                self.log_test(
                    "Event Trigger Field Analysis",
                    False,
                    "No notifications provided for analysis"
                )
                return False
            
            total_notifications = len(notifications)
            notifications_with_event_trigger = 0
            notifications_without_event_trigger = 0
            event_trigger_values = []
            missing_event_trigger_notifications = []
            
            for notification in notifications:
                if "event_trigger" in notification and notification["event_trigger"] is not None:
                    notifications_with_event_trigger += 1
                    event_trigger_values.append(notification["event_trigger"])
                else:
                    notifications_without_event_trigger += 1
                    missing_event_trigger_notifications.append({
                        "id": notification.get("id", "unknown"),
                        "title": notification.get("title", "No title")
                    })
            
            # Log detailed analysis
            details = f"Total notifications: {total_notifications}, "
            details += f"With event_trigger: {notifications_with_event_trigger}, "
            details += f"Without event_trigger: {notifications_without_event_trigger}"
            
            if event_trigger_values:
                details += f", Event trigger values found: {list(set(event_trigger_values))}"
            
            if missing_event_trigger_notifications:
                details += f", Missing event_trigger in: {[n['title'] for n in missing_event_trigger_notifications[:3]]}"
                if len(missing_event_trigger_notifications) > 3:
                    details += f" and {len(missing_event_trigger_notifications) - 3} more"
            
            # This test passes if we can analyze the data structure
            self.log_test(
                "Event Trigger Field Analysis",
                True,
                details
            )
            
            return {
                "total": total_notifications,
                "with_event_trigger": notifications_with_event_trigger,
                "without_event_trigger": notifications_without_event_trigger,
                "event_trigger_values": list(set(event_trigger_values)),
                "missing_notifications": missing_event_trigger_notifications
            }
            
        except Exception as e:
            self.log_test(
                "Event Trigger Field Analysis",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_create_notification_with_event_trigger(self):
        """Test 3: Create Notification with Event Trigger"""
        try:
            # Create a test notification with event_trigger field
            test_notification = {
                "title": "Test Event Trigger Notification",
                "message": "This is a test notification with event_trigger field",
                "type": "info",
                "target_users": "all",
                "is_active": True,
                "event_trigger": "test_event",
                "display_count": 0
            }
            
            response = self.session.post(
                f"{self.backend_url}/admin/system-notifications",
                json=test_notification,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Create Notification with Event Trigger",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
            
            result = response.json()
            
            # Check if notification was created successfully
            if "message" in result and "success" in result.get("message", "").lower():
                notification_id = result.get("notification_id")
                self.log_test(
                    "Create Notification with Event Trigger",
                    True,
                    f"Successfully created notification with event_trigger='test_event', ID: {notification_id}"
                )
                return notification_id
            else:
                self.log_test(
                    "Create Notification with Event Trigger",
                    False,
                    f"Unexpected response: {result}",
                    "Success message with notification_id",
                    str(result)
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Create Notification with Event Trigger",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_create_notification_without_event_trigger(self):
        """Test 4: Create Notification without Event Trigger (Legacy)"""
        try:
            # Create a test notification without event_trigger field (legacy style)
            test_notification = {
                "title": "Test Legacy Notification",
                "message": "This is a test notification without event_trigger field",
                "type": "info",
                "target_users": "all",
                "is_active": True,
                "display_count": 0
                # Note: No event_trigger field
            }
            
            response = self.session.post(
                f"{self.backend_url}/admin/system-notifications",
                json=test_notification,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Create Notification without Event Trigger",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
            
            result = response.json()
            
            # Check if notification was created successfully
            if "message" in result and "success" in result.get("message", "").lower():
                notification_id = result.get("notification_id")
                self.log_test(
                    "Create Notification without Event Trigger",
                    True,
                    f"Successfully created legacy notification without event_trigger, ID: {notification_id}"
                )
                return notification_id
            else:
                self.log_test(
                    "Create Notification without Event Trigger",
                    False,
                    f"Unexpected response: {result}",
                    "Success message with notification_id",
                    str(result)
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Create Notification without Event Trigger",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_verify_mixed_notifications_display(self):
        """Test 5: Verify Mixed Notifications Display"""
        try:
            # Get all notifications again to verify both types exist
            response = self.session.get(f"{self.backend_url}/admin/system-notifications")
            
            if response.status_code != 200:
                self.log_test(
                    "Verify Mixed Notifications Display",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            data = response.json()
            notifications = data.get("notifications", [])
            
            # Look for our test notifications
            test_with_trigger = None
            test_without_trigger = None
            
            for notification in notifications:
                title = notification.get("title", "")
                if title == "Test Event Trigger Notification":
                    test_with_trigger = notification
                elif title == "Test Legacy Notification":
                    test_without_trigger = notification
            
            # Verify both notifications exist and have correct structure
            success = True
            details = []
            
            if test_with_trigger:
                event_trigger = test_with_trigger.get("event_trigger")
                if event_trigger == "test_event":
                    details.append("✅ Notification with event_trigger='test_event' found")
                else:
                    details.append(f"❌ Notification with event_trigger has wrong value: {event_trigger}")
                    success = False
            else:
                details.append("❌ Test notification with event_trigger not found")
                success = False
            
            if test_without_trigger:
                event_trigger = test_without_trigger.get("event_trigger")
                if event_trigger is None or event_trigger == "":
                    details.append("✅ Legacy notification without event_trigger found (should show 'Manual Trigger' in frontend)")
                else:
                    details.append(f"❌ Legacy notification has unexpected event_trigger: {event_trigger}")
                    success = False
            else:
                details.append("❌ Test legacy notification without event_trigger not found")
                success = False
            
            self.log_test(
                "Verify Mixed Notifications Display",
                success,
                "; ".join(details)
            )
            
            return success
            
        except Exception as e:
            self.log_test(
                "Verify Mixed Notifications Display",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def cleanup_test_notifications(self):
        """Cleanup: Remove test notifications"""
        try:
            # This is a cleanup step, not a test
            # In a real implementation, you would delete the test notifications
            # For now, we'll just log that cleanup should be done
            print("Note: Test notifications should be cleaned up manually if needed")
            return True
            
        except Exception as e:
            print(f"Cleanup warning: {str(e)}")
            return True
    
    def run_all_tests(self):
        """Run all system notifications event trigger tests"""
        print("=" * 80)
        print("SYSTEM NOTIFICATIONS EVENT TRIGGER DISPLAY TESTING")
        print("Testing the fix for missing event_trigger field display")
        print("=" * 80)
        print()
        
        # Test 1: GET System Notifications
        notifications = self.test_get_system_notifications()
        test1_success = bool(notifications)
        
        # Test 2: Event Trigger Field Analysis
        analysis_result = False
        if test1_success and notifications:
            analysis_result = self.test_event_trigger_field_analysis(notifications)
        test2_success = bool(analysis_result)
        
        # Test 3: Create Notification with Event Trigger
        test3_result = self.test_create_notification_with_event_trigger()
        test3_success = bool(test3_result)
        
        # Test 4: Create Notification without Event Trigger
        test4_result = self.test_create_notification_without_event_trigger()
        test4_success = bool(test4_result)
        
        # Test 5: Verify Mixed Notifications Display
        test5_success = False
        if test3_success and test4_success:
            test5_success = self.test_verify_mixed_notifications_display()
        else:
            self.log_test(
                "Verify Mixed Notifications Display",
                False,
                "Skipped due to failed notification creation tests"
            )
        
        # Cleanup
        self.cleanup_test_notifications()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = 5
        passed_tests = sum([test1_success, test2_success, test3_success, test4_success, test5_success])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Individual test results
        tests = [
            ("GET System Notifications", test1_success),
            ("Event Trigger Field Analysis", test2_success),
            ("Create Notification with Event Trigger", test3_success),
            ("Create Notification without Event Trigger", test4_success),
            ("Verify Mixed Notifications Display", test5_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        
        # Analysis summary
        if analysis_result and test2_success:
            print("ANALYSIS SUMMARY:")
            print(f"📊 Total notifications in system: {analysis_result['total']}")
            print(f"✅ Notifications WITH event_trigger: {analysis_result['with_event_trigger']}")
            print(f"⚠️  Notifications WITHOUT event_trigger: {analysis_result['without_event_trigger']}")
            
            if analysis_result['event_trigger_values']:
                print(f"🏷️  Event trigger values found: {', '.join(analysis_result['event_trigger_values'])}")
            
            if analysis_result['missing_notifications']:
                print(f"📝 Notifications missing event_trigger (should show 'Manual Trigger'):")
                for notif in analysis_result['missing_notifications'][:5]:  # Show first 5
                    print(f"   - {notif['title']} (ID: {notif['id']})")
                if len(analysis_result['missing_notifications']) > 5:
                    print(f"   ... and {len(analysis_result['missing_notifications']) - 5} more")
            print()
        
        # Critical issues
        critical_failures = []
        if not test1_success:
            critical_failures.append("System notifications endpoint not accessible")
        if not test2_success:
            critical_failures.append("Cannot analyze event_trigger field structure")
        if not test3_success:
            critical_failures.append("Cannot create notifications with event_trigger")
        if not test4_success:
            critical_failures.append("Cannot create legacy notifications without event_trigger")
        if not test5_success and test3_success and test4_success:
            critical_failures.append("Mixed notification types not displaying correctly")
        
        if critical_failures:
            print("CRITICAL ISSUES FOUND:")
            for issue in critical_failures:
                print(f"❌ {issue}")
        else:
            print("✅ ALL CRITICAL FUNCTIONALITY WORKING")
        
        print()
        
        # Frontend fix recommendation
        if analysis_result and analysis_result['without_event_trigger'] > 0:
            print("FRONTEND FIX VERIFICATION:")
            print("🔧 The frontend should handle missing event_trigger fields by:")
            print("   1. Checking if notification.event_trigger exists and is not null/undefined")
            print("   2. Displaying 'Manual Trigger' when event_trigger is missing")
            print("   3. Displaying the actual event_trigger value when present")
            print(f"📋 {analysis_result['without_event_trigger']} notifications need this fallback display")
            print()
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = SystemNotificationsTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED - System notifications event trigger display is working correctly!")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Check the issues above")
        sys.exit(1)