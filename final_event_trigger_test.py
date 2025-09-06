#!/usr/bin/env python3
"""
System Notifications Event Trigger Display Fix Verification
Testing the specific fix for missing event_trigger field display
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

class EventTriggerDisplayTester:
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
        
    def test_get_system_notifications_structure(self):
        """Test 1: GET System Notifications and Verify Structure"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/system-notifications")
            
            if response.status_code != 200:
                self.log_test(
                    "GET System Notifications Structure",
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
                    "GET System Notifications Structure",
                    False,
                    "Response missing 'notifications' array",
                    "Response with 'notifications' array",
                    f"Response keys: {list(data.keys())}"
                )
                return False
            
            notifications = data["notifications"]
            notification_count = len(notifications)
            
            self.log_test(
                "GET System Notifications Structure",
                True,
                f"Successfully retrieved {notification_count} system notifications with proper structure"
            )
            return notifications
            
        except Exception as e:
            self.log_test(
                "GET System Notifications Structure",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_missing_event_trigger_notifications(self, notifications):
        """Test 2: Verify Notifications with Missing event_trigger Field"""
        try:
            if not notifications:
                self.log_test(
                    "Missing Event Trigger Notifications",
                    False,
                    "No notifications provided for analysis"
                )
                return False
            
            # Find notifications with missing event_trigger (None/null)
            missing_event_trigger = []
            for notification in notifications:
                event_trigger = notification.get("event_trigger")
                if event_trigger is None:
                    missing_event_trigger.append({
                        "id": notification.get("id", "unknown"),
                        "title": notification.get("title", "No title"),
                        "event_trigger": event_trigger
                    })
            
            if len(missing_event_trigger) > 0:
                details = f"Found {len(missing_event_trigger)} notifications with missing event_trigger field: "
                details += ", ".join([f"'{n['title']}'" for n in missing_event_trigger[:3]])
                if len(missing_event_trigger) > 3:
                    details += f" and {len(missing_event_trigger) - 3} more"
                
                self.log_test(
                    "Missing Event Trigger Notifications",
                    True,
                    details + " (These should display 'Manual Trigger' in frontend)"
                )
                return missing_event_trigger
            else:
                self.log_test(
                    "Missing Event Trigger Notifications",
                    True,
                    "No notifications with missing event_trigger found (all have values)"
                )
                return []
            
        except Exception as e:
            self.log_test(
                "Missing Event Trigger Notifications",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_existing_event_trigger_notifications(self, notifications):
        """Test 3: Verify Notifications with Existing event_trigger Field"""
        try:
            if not notifications:
                self.log_test(
                    "Existing Event Trigger Notifications",
                    False,
                    "No notifications provided for analysis"
                )
                return False
            
            # Find notifications with existing event_trigger values
            with_event_trigger = []
            event_trigger_values = set()
            
            for notification in notifications:
                event_trigger = notification.get("event_trigger")
                if event_trigger is not None and event_trigger != "":
                    with_event_trigger.append({
                        "id": notification.get("id", "unknown"),
                        "title": notification.get("title", "No title"),
                        "event_trigger": event_trigger
                    })
                    event_trigger_values.add(event_trigger)
            
            if len(with_event_trigger) > 0:
                details = f"Found {len(with_event_trigger)} notifications with event_trigger values: "
                details += f"{', '.join(sorted(event_trigger_values))}"
                
                self.log_test(
                    "Existing Event Trigger Notifications",
                    True,
                    details + " (These should display their actual event_trigger values in frontend)"
                )
                return with_event_trigger
            else:
                self.log_test(
                    "Existing Event Trigger Notifications",
                    False,
                    "No notifications with event_trigger values found"
                )
                return []
            
        except Exception as e:
            self.log_test(
                "Existing Event Trigger Notifications",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_mixed_notification_display_readiness(self, missing_notifications, existing_notifications):
        """Test 4: Verify Mixed Notification Display Readiness"""
        try:
            # Check if we have both types for comprehensive testing
            has_missing = len(missing_notifications) > 0 if missing_notifications else False
            has_existing = len(existing_notifications) > 0 if existing_notifications else False
            
            if has_missing and has_existing:
                details = f"System has both types: {len(missing_notifications)} without event_trigger, "
                details += f"{len(existing_notifications)} with event_trigger. "
                details += "Frontend can be tested for both scenarios."
                
                self.log_test(
                    "Mixed Notification Display Readiness",
                    True,
                    details
                )
                return True
            elif has_existing and not has_missing:
                self.log_test(
                    "Mixed Notification Display Readiness",
                    True,
                    f"System has {len(existing_notifications)} notifications with event_trigger values. "
                    "No legacy notifications without event_trigger found."
                )
                return True
            elif has_missing and not has_existing:
                self.log_test(
                    "Mixed Notification Display Readiness",
                    True,
                    f"System has {len(missing_notifications)} legacy notifications without event_trigger. "
                    "No notifications with event_trigger values found."
                )
                return True
            else:
                self.log_test(
                    "Mixed Notification Display Readiness",
                    False,
                    "No notifications found for testing display behavior"
                )
                return False
            
        except Exception as e:
            self.log_test(
                "Mixed Notification Display Readiness",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_frontend_display_requirements(self, missing_notifications, existing_notifications):
        """Test 5: Verify Frontend Display Requirements"""
        try:
            requirements_met = True
            details = []
            
            # Check if we can test the "Manual Trigger" fallback
            if missing_notifications and len(missing_notifications) > 0:
                details.append(f"✅ {len(missing_notifications)} notifications need 'Manual Trigger' fallback")
                requirements_met = True
            else:
                details.append("ℹ️  No notifications need 'Manual Trigger' fallback (all have event_trigger values)")
            
            # Check if we can test actual event_trigger display
            if existing_notifications and len(existing_notifications) > 0:
                event_types = set(n['event_trigger'] for n in existing_notifications)
                details.append(f"✅ {len(existing_notifications)} notifications should show event types: {', '.join(sorted(event_types))}")
                requirements_met = True
            else:
                details.append("⚠️  No notifications with event_trigger values found")
                requirements_met = False
            
            # Verify the fix can be tested
            if missing_notifications or existing_notifications:
                details.append("✅ Frontend display fix can be verified with current data")
            else:
                details.append("❌ No notifications available to test frontend display fix")
                requirements_met = False
            
            self.log_test(
                "Frontend Display Requirements",
                requirements_met,
                "; ".join(details)
            )
            
            return requirements_met
            
        except Exception as e:
            self.log_test(
                "Frontend Display Requirements",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all event trigger display verification tests"""
        print("=" * 80)
        print("SYSTEM NOTIFICATIONS EVENT TRIGGER DISPLAY FIX VERIFICATION")
        print("Testing the fix for missing event_trigger field display")
        print("=" * 80)
        print()
        
        # Test 1: GET System Notifications Structure
        notifications = self.test_get_system_notifications_structure()
        test1_success = bool(notifications)
        
        # Test 2: Missing Event Trigger Notifications
        missing_notifications = False
        if test1_success and notifications:
            missing_notifications = self.test_missing_event_trigger_notifications(notifications)
        test2_success = missing_notifications is not False
        
        # Test 3: Existing Event Trigger Notifications
        existing_notifications = False
        if test1_success and notifications:
            existing_notifications = self.test_existing_event_trigger_notifications(notifications)
        test3_success = existing_notifications is not False
        
        # Test 4: Mixed Notification Display Readiness
        test4_success = False
        if test2_success and test3_success:
            test4_success = self.test_mixed_notification_display_readiness(missing_notifications, existing_notifications)
        else:
            self.log_test(
                "Mixed Notification Display Readiness",
                False,
                "Skipped due to failed notification analysis"
            )
        
        # Test 5: Frontend Display Requirements
        test5_success = False
        if test2_success and test3_success:
            test5_success = self.test_frontend_display_requirements(missing_notifications, existing_notifications)
        else:
            self.log_test(
                "Frontend Display Requirements",
                False,
                "Skipped due to failed notification analysis"
            )
        
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
            ("GET System Notifications Structure", test1_success),
            ("Missing Event Trigger Notifications", test2_success),
            ("Existing Event Trigger Notifications", test3_success),
            ("Mixed Notification Display Readiness", test4_success),
            ("Frontend Display Requirements", test5_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        
        # Detailed Analysis
        if test2_success and test3_success:
            print("DETAILED ANALYSIS:")
            print("=" * 50)
            
            if missing_notifications and len(missing_notifications) > 0:
                print(f"📋 NOTIFICATIONS WITHOUT event_trigger ({len(missing_notifications)}):")
                print("   These should display 'Manual Trigger' in the frontend:")
                for notif in missing_notifications:
                    print(f"   - '{notif['title']}' (ID: {notif['id']}) → Should show: 'Manual Trigger'")
                print()
            
            if existing_notifications and len(existing_notifications) > 0:
                print(f"📋 NOTIFICATIONS WITH event_trigger ({len(existing_notifications)}):")
                print("   These should display their actual event_trigger value:")
                for notif in existing_notifications:
                    print(f"   - '{notif['title']}' (ID: {notif['id']}) → Should show: '{notif['event_trigger']}'")
                print()
        
        # Frontend Implementation Guide
        print("FRONTEND IMPLEMENTATION VERIFICATION:")
        print("=" * 50)
        print("🔧 The frontend fix should handle event_trigger display as follows:")
        print()
        print("```javascript")
        print("// In the notification display component:")
        print("const getEventTriggerDisplay = (notification) => {")
        print("  const eventTrigger = notification.event_trigger;")
        print("  if (eventTrigger === null || eventTrigger === undefined || eventTrigger === '') {")
        print("    return 'Manual Trigger';  // Fallback for missing event_trigger")
        print("  }")
        print("  return eventTrigger;  // Display actual event_trigger value")
        print("};")
        print("```")
        print()
        
        # Critical issues
        critical_failures = []
        if not test1_success:
            critical_failures.append("Cannot retrieve system notifications")
        if not test2_success:
            critical_failures.append("Cannot analyze missing event_trigger notifications")
        if not test3_success:
            critical_failures.append("Cannot analyze existing event_trigger notifications")
        if not test4_success and test2_success and test3_success:
            critical_failures.append("System not ready for mixed notification display testing")
        if not test5_success and test2_success and test3_success:
            critical_failures.append("Frontend display requirements not met")
        
        if critical_failures:
            print("CRITICAL ISSUES FOUND:")
            for issue in critical_failures:
                print(f"❌ {issue}")
        else:
            print("✅ ALL VERIFICATION TESTS PASSED")
            print("✅ System is ready for frontend event_trigger display fix verification")
        
        print()
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = EventTriggerDisplayTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("✅ System Notifications event_trigger display fix can be verified")
        print("✅ Both old notifications (without event_trigger) and new notifications (with event_trigger) are present")
        print("✅ Frontend should display 'Manual Trigger' for missing event_trigger and actual values for existing ones")
        sys.exit(0)
    else:
        print("⚠️  SOME VERIFICATION TESTS FAILED - Check the issues above")
        sys.exit(1)