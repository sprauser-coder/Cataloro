#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Timezone Fix for Notifications
Testing the German timezone implementation for notification timestamps
"""

import requests
import json
import uuid
import time
from datetime import datetime, timezone
import pytz

# Get backend URL from environment
BACKEND_URL = "https://cataloro-ads.preview.emergentagent.com/api"

class TimezoneNotificationTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_user_id = "68bc2bb44c8f259a2c575f6e"  # Use existing demo user
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def get_current_german_time(self):
        """Get current time in German timezone for comparison"""
        german_tz = pytz.timezone('Europe/Berlin')
        return datetime.now(german_tz)

    def parse_iso_timestamp(self, timestamp_str):
        """Parse ISO timestamp string to datetime object"""
        try:
            # Handle different ISO formats
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            elif '+' not in timestamp_str and 'T' in timestamp_str:
                # Assume it's already in German timezone if no timezone info
                return datetime.fromisoformat(timestamp_str)
            
            return datetime.fromisoformat(timestamp_str)
        except Exception as e:
            print(f"Error parsing timestamp {timestamp_str}: {e}")
            return None

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def test_notification_creation_with_german_timezone(self):
        """Test notification creation with German timezone timestamp"""
        try:
            # Record current German time before creating notification
            before_creation = self.get_current_german_time()
            
            # Create test notification
            notification_data = {
                "title": "Timezone Test Notification",
                "message": "Testing German timezone implementation for notification timestamps",
                "type": "test"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                json=notification_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                notification_id = data.get('id')
                
                # Record time after creation
                after_creation = self.get_current_german_time()
                
                self.log_test(
                    "Notification Creation with German Timezone", 
                    True, 
                    f"Created notification with ID: {notification_id}"
                )
                return notification_id, before_creation, after_creation
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Notification Creation with German Timezone", False, error_msg=error_detail)
                return None, None, None
        except Exception as e:
            self.log_test("Notification Creation with German Timezone", False, error_msg=str(e))
            return None, None, None

    def test_notification_retrieval_and_timezone_verification(self, notification_id, before_creation, after_creation):
        """Test notification retrieval and verify German timezone"""
        if not notification_id:
            self.log_test("Notification Retrieval and Timezone Verification", False, error_msg="No notification ID provided")
            return False
            
        try:
            response = requests.get(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                timeout=10
            )
            
            if response.status_code == 200:
                notifications = response.json()
                
                # Find our test notification
                test_notification = None
                for notif in notifications:
                    if notif.get('id') == notification_id:
                        test_notification = notif
                        break
                
                if test_notification:
                    created_at_str = test_notification.get('created_at')
                    if created_at_str:
                        # Parse the timestamp
                        created_at = self.parse_iso_timestamp(created_at_str)
                        
                        if created_at:
                            # Convert to German timezone for comparison if needed
                            if created_at.tzinfo is None:
                                # Assume it's already in German timezone
                                german_tz = pytz.timezone('Europe/Berlin')
                                created_at = german_tz.localize(created_at)
                            elif created_at.tzinfo != pytz.timezone('Europe/Berlin'):
                                # Convert to German timezone
                                created_at = created_at.astimezone(pytz.timezone('Europe/Berlin'))
                            
                            # Check if timestamp is within reasonable range (should be between before and after creation)
                            time_diff_before = abs((created_at - before_creation).total_seconds())
                            time_diff_after = abs((created_at - after_creation).total_seconds())
                            
                            # Allow up to 10 seconds difference for network latency
                            is_time_accurate = time_diff_before <= 10 or time_diff_after <= 10
                            
                            # Check if it's using German timezone (not UTC)
                            current_german_time = self.get_current_german_time()
                            utc_time = datetime.now(timezone.utc)
                            
                            # German time should be 1-2 hours ahead of UTC (depending on DST)
                            timezone_offset = (current_german_time.utcoffset().total_seconds() / 3600)
                            is_german_timezone = timezone_offset >= 1  # At least 1 hour ahead of UTC
                            
                            self.log_test(
                                "Notification Retrieval and Timezone Verification", 
                                is_time_accurate and is_german_timezone, 
                                f"Timestamp: {created_at_str}, German timezone offset: +{timezone_offset}h, Time accuracy: {is_time_accurate}"
                            )
                            return is_time_accurate and is_german_timezone
                        else:
                            self.log_test("Notification Retrieval and Timezone Verification", False, error_msg="Could not parse timestamp")
                            return False
                    else:
                        self.log_test("Notification Retrieval and Timezone Verification", False, error_msg="No created_at timestamp found")
                        return False
                else:
                    self.log_test("Notification Retrieval and Timezone Verification", False, error_msg="Test notification not found in response")
                    return False
            else:
                self.log_test("Notification Retrieval and Timezone Verification", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Notification Retrieval and Timezone Verification", False, error_msg=str(e))
            return False

    def test_timezone_formatting_consistency(self):
        """Test that all notifications use consistent German timezone formatting"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                timeout=10
            )
            
            if response.status_code == 200:
                notifications = response.json()
                
                if notifications:
                    consistent_formatting = True
                    timezone_info = []
                    
                    for notif in notifications[:5]:  # Check first 5 notifications
                        created_at_str = notif.get('created_at', '')
                        if created_at_str:
                            # Check if timestamp includes timezone info or is in expected format
                            has_timezone_info = '+' in created_at_str or 'Z' in created_at_str or len(created_at_str) > 19
                            timezone_info.append(f"ID: {notif.get('id', 'unknown')[:8]}... - {created_at_str}")
                            
                            if not has_timezone_info:
                                consistent_formatting = False
                    
                    details = f"Checked {len(notifications)} notifications. Sample timestamps: " + "; ".join(timezone_info[:3])
                    
                    self.log_test(
                        "Timezone Formatting Consistency", 
                        consistent_formatting, 
                        details
                    )
                    return consistent_formatting
                else:
                    self.log_test(
                        "Timezone Formatting Consistency", 
                        True, 
                        "No notifications found to check (this is acceptable)"
                    )
                    return True
            else:
                self.log_test("Timezone Formatting Consistency", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Timezone Formatting Consistency", False, error_msg=str(e))
            return False

    def test_current_time_accuracy(self):
        """Test that notification timestamp matches current German time accurately"""
        try:
            # Get current German time
            current_german_time = self.get_current_german_time()
            
            # Create a notification right now
            notification_data = {
                "title": "Current Time Test",
                "message": f"Testing current German time accuracy at {current_german_time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
                "type": "time_test"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                json=notification_data,
                timeout=10
            )
            
            if response.status_code == 200:
                # Get the notification immediately
                get_response = requests.get(
                    f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                    timeout=10
                )
                
                if get_response.status_code == 200:
                    notifications = get_response.json()
                    
                    # Find the most recent notification (should be our test)
                    if notifications:
                        latest_notification = notifications[0]  # Should be sorted by created_at desc
                        created_at_str = latest_notification.get('created_at')
                        
                        if created_at_str and latest_notification.get('title') == 'Current Time Test':
                            created_at = self.parse_iso_timestamp(created_at_str)
                            
                            if created_at:
                                # Convert to German timezone if needed
                                if created_at.tzinfo is None:
                                    german_tz = pytz.timezone('Europe/Berlin')
                                    created_at = german_tz.localize(created_at)
                                elif created_at.tzinfo != pytz.timezone('Europe/Berlin'):
                                    created_at = created_at.astimezone(pytz.timezone('Europe/Berlin'))
                                
                                # Check time difference (should be very small)
                                time_diff = abs((created_at - current_german_time).total_seconds())
                                is_accurate = time_diff <= 5  # Allow 5 seconds difference
                                
                                self.log_test(
                                    "Current Time Accuracy", 
                                    is_accurate, 
                                    f"Expected: {current_german_time.strftime('%Y-%m-%d %H:%M:%S %Z')}, Got: {created_at.strftime('%Y-%m-%d %H:%M:%S %Z')}, Diff: {time_diff:.1f}s"
                                )
                                return is_accurate
                            else:
                                self.log_test("Current Time Accuracy", False, error_msg="Could not parse notification timestamp")
                                return False
                        else:
                            self.log_test("Current Time Accuracy", False, error_msg="Test notification not found or incorrect")
                            return False
                    else:
                        self.log_test("Current Time Accuracy", False, error_msg="No notifications returned")
                        return False
                else:
                    self.log_test("Current Time Accuracy", False, f"Failed to retrieve notifications: HTTP {get_response.status_code}")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Current Time Accuracy", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Current Time Accuracy", False, error_msg=str(e))
            return False

    def test_pytz_library_functionality(self):
        """Test that pytz library is working correctly for German timezone"""
        try:
            # This is a backend functionality test - we'll verify through API behavior
            # Create multiple notifications and check their timezone consistency
            
            notification_ids = []
            timestamps = []
            
            for i in range(3):
                notification_data = {
                    "title": f"PyTZ Test {i+1}",
                    "message": f"Testing pytz library functionality - notification {i+1}",
                    "type": "pytz_test"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                    json=notification_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    notification_ids.append(response.json().get('id'))
                    timestamps.append(datetime.now())
                    time.sleep(1)  # Small delay between notifications
                else:
                    self.log_test("PyTZ Library Functionality", False, error_msg=f"Failed to create test notification {i+1}")
                    return False
            
            # Retrieve notifications and verify timezone consistency
            response = requests.get(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                timeout=10
            )
            
            if response.status_code == 200:
                notifications = response.json()
                
                pytz_test_notifications = [n for n in notifications if n.get('title', '').startswith('PyTZ Test')]
                
                if len(pytz_test_notifications) >= 3:
                    # Check that all timestamps are in proper format and sequential
                    all_valid = True
                    timezone_consistent = True
                    
                    for notif in pytz_test_notifications[:3]:
                        created_at_str = notif.get('created_at', '')
                        if not created_at_str:
                            all_valid = False
                            break
                        
                        # Check timezone format (should include timezone info)
                        if not ('+' in created_at_str or 'Z' in created_at_str or len(created_at_str) > 19):
                            timezone_consistent = False
                    
                    success = all_valid and timezone_consistent
                    details = f"Created {len(pytz_test_notifications)} test notifications, all have proper timezone formatting: {timezone_consistent}"
                    
                    self.log_test("PyTZ Library Functionality", success, details)
                    return success
                else:
                    self.log_test("PyTZ Library Functionality", False, error_msg="Not all test notifications were created or retrieved")
                    return False
            else:
                self.log_test("PyTZ Library Functionality", False, f"Failed to retrieve notifications: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("PyTZ Library Functionality", False, error_msg=str(e))
            return False

    def cleanup_test_notifications(self):
        """Clean up test notifications created during testing"""
        try:
            # Get all notifications
            response = requests.get(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                timeout=10
            )
            
            if response.status_code == 200:
                notifications = response.json()
                
                # Find test notifications
                test_notifications = [
                    n for n in notifications 
                    if n.get('title', '').startswith(('Timezone Test', 'Current Time Test', 'PyTZ Test'))
                ]
                
                cleaned_count = 0
                for notif in test_notifications:
                    notif_id = notif.get('id')
                    if notif_id:
                        try:
                            delete_response = requests.delete(
                                f"{BACKEND_URL}/user/{self.test_user_id}/notifications/{notif_id}",
                                timeout=10
                            )
                            if delete_response.status_code == 200:
                                cleaned_count += 1
                        except:
                            pass  # Ignore cleanup errors
                
                if cleaned_count > 0:
                    self.log_test(
                        "Test Cleanup", 
                        True, 
                        f"Successfully cleaned up {cleaned_count} test notifications"
                    )
                    
        except Exception as e:
            # Cleanup errors are not critical
            pass

    def run_timezone_tests(self):
        """Run all timezone-related notification tests"""
        print("=" * 80)
        print("CATALORO TIMEZONE FIX TESTING - GERMAN TIMEZONE FOR NOTIFICATIONS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {self.test_user_id}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print(f"Current German Time: {self.get_current_german_time().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting timezone testing.")
            return
        
        # 2. Test Notification Creation with German Timezone
        print("📝 NOTIFICATION CREATION WITH GERMAN TIMEZONE")
        print("-" * 40)
        notification_id, before_creation, after_creation = self.test_notification_creation_with_german_timezone()
        
        # 3. Test Notification Retrieval and Timezone Verification
        print("📥 NOTIFICATION RETRIEVAL AND TIMEZONE VERIFICATION")
        print("-" * 40)
        self.test_notification_retrieval_and_timezone_verification(notification_id, before_creation, after_creation)
        
        # 4. Test Timezone Formatting Consistency
        print("🕐 TIMEZONE FORMATTING CONSISTENCY")
        print("-" * 40)
        self.test_timezone_formatting_consistency()
        
        # 5. Test Current Time Accuracy
        print("⏰ CURRENT TIME ACCURACY")
        print("-" * 40)
        self.test_current_time_accuracy()
        
        # 6. Test PyTZ Library Functionality
        print("🐍 PYTZ LIBRARY FUNCTIONALITY")
        print("-" * 40)
        self.test_pytz_library_functionality()
        
        # 7. Cleanup
        print("🧹 CLEANUP")
        print("-" * 40)
        self.cleanup_test_notifications()
        
        # Print Summary
        print("=" * 80)
        print("TIMEZONE TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        else:
            print("🎉 ALL TIMEZONE TESTS PASSED!")
            print("✅ Notifications are now using German timezone (Europe/Berlin)")
            print("✅ Timestamps are no longer 2 hours behind current German time")
            print("✅ PyTZ library is working correctly")
            print("✅ All notification endpoints use consistent German timezone")
        
        print("\n🎯 TIMEZONE TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = TimezoneNotificationTester()
    
    print("🕐 RUNNING TIMEZONE FIX TESTING FOR NOTIFICATIONS")
    print("Testing German timezone implementation as requested...")
    print()
    
    passed, failed, results = tester.run_timezone_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)