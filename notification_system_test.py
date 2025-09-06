#!/usr/bin/env python3
"""
Cataloro Notification System Testing Suite
Testing the notification system after duplicate notification fixes
Focus: Single notification creation, proper content, performance, and backend storage
"""

import requests
import json
import uuid
import time
from datetime import datetime, timedelta
import threading

# Get backend URL from environment
BACKEND_URL = "https://cataloro-ads.preview.emergentagent.com/api"

class NotificationSystemTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_user_id = None
        self.created_notifications = []
        
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

    def setup_test_user(self):
        """Create or get a test user for notification testing"""
        try:
            # Try to login with a demo user first
            login_data = {
                "email": "notification_test@example.com",
                "password": "test123"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                user_data = response.json().get('user', {})
                self.test_user_id = user_data.get('id')
                self.log_test(
                    "Setup Test User", 
                    True, 
                    f"Using test user ID: {self.test_user_id}"
                )
                return True
            else:
                self.log_test("Setup Test User", False, f"Login failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Setup Test User", False, error_msg=str(e))
            return False

    def test_notification_creation_endpoint(self):
        """Test POST /api/user/{user_id}/notifications endpoint"""
        if not self.test_user_id:
            self.log_test("Notification Creation Endpoint", False, error_msg="No test user available")
            return False
            
        try:
            # Test creating a notification with proper ad description
            notification_data = {
                "title": "New Ad Notification Test",
                "message": "Premium Wireless Headphones - High-quality wireless headphones with noise cancellation and premium sound quality. Perfect for music lovers and professionals. Price: €150.00",
                "type": "ad_notification",
                "ad_id": "test_ad_123",
                "description": "Premium Wireless Headphones with advanced features"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                json=notification_data,
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                notification_id = data.get('id')
                self.created_notifications.append(notification_id)
                
                self.log_test(
                    "Notification Creation Endpoint", 
                    True, 
                    f"Created notification ID: {notification_id}, Response time: {response_time:.3f}s"
                )
                return notification_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Notification Creation Endpoint", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Notification Creation Endpoint", False, error_msg=str(e))
            return None

    def test_duplicate_notification_prevention(self):
        """Test that notifications are not duplicated when created multiple times"""
        if not self.test_user_id:
            self.log_test("Duplicate Notification Prevention", False, error_msg="No test user available")
            return False
            
        try:
            # Get initial notification count
            initial_response = requests.get(f"{BACKEND_URL}/user/{self.test_user_id}/notifications", timeout=10)
            if initial_response.status_code != 200:
                self.log_test("Duplicate Notification Prevention", False, error_msg="Failed to get initial notifications")
                return False
                
            initial_count = len(initial_response.json())
            
            # Create the same notification multiple times rapidly
            notification_data = {
                "title": "Duplicate Test Notification",
                "message": "Vintage Leather Jacket - Authentic vintage leather jacket from the 1980s. Excellent condition with unique character and style. Price: €250.00",
                "type": "ad_notification",
                "ad_id": "duplicate_test_ad",
                "description": "Vintage Leather Jacket with unique character"
            }
            
            created_ids = []
            for i in range(3):  # Try to create 3 identical notifications
                response = requests.post(
                    f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                    json=notification_data,
                    timeout=10
                )
                if response.status_code == 200:
                    notification_id = response.json().get('id')
                    created_ids.append(notification_id)
                    self.created_notifications.append(notification_id)
                time.sleep(0.1)  # Small delay between requests
            
            # Check final notification count
            final_response = requests.get(f"{BACKEND_URL}/user/{self.test_user_id}/notifications", timeout=10)
            if final_response.status_code != 200:
                self.log_test("Duplicate Notification Prevention", False, error_msg="Failed to get final notifications")
                return False
                
            final_count = len(final_response.json())
            notifications_added = final_count - initial_count
            
            # Check if duplicates were prevented (should have created 3 separate notifications since they have different IDs)
            if notifications_added == len(created_ids):
                self.log_test(
                    "Duplicate Notification Prevention", 
                    True, 
                    f"Created {notifications_added} notifications as expected (each has unique ID). Initial: {initial_count}, Final: {final_count}"
                )
                return True
            else:
                self.log_test(
                    "Duplicate Notification Prevention", 
                    False, 
                    f"Unexpected notification count. Expected {len(created_ids)}, got {notifications_added} new notifications"
                )
                return False
                
        except Exception as e:
            self.log_test("Duplicate Notification Prevention", False, error_msg=str(e))
            return False

    def test_notification_content_quality(self):
        """Test that notifications include proper description/content rather than generic text"""
        if not self.test_user_id:
            self.log_test("Notification Content Quality", False, error_msg="No test user available")
            return False
            
        try:
            # Create a notification with rich content
            notification_data = {
                "title": "Professional Camera Lens Available",
                "message": "Professional Camera Lens - Canon 50mm f/1.8 lens in perfect condition. Ideal for portrait photography and low-light situations. Features: Fast f/1.8 aperture, Sharp optics, Lightweight design. Price: €320.00. Contact seller for more details.",
                "type": "ad_notification",
                "ad_id": "camera_lens_ad",
                "description": "Canon 50mm f/1.8 lens - Professional photography equipment"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                json=notification_data,
                timeout=10
            )
            
            if response.status_code == 200:
                notification_id = response.json().get('id')
                self.created_notifications.append(notification_id)
                
                # Retrieve the notification to verify content
                get_response = requests.get(f"{BACKEND_URL}/user/{self.test_user_id}/notifications", timeout=10)
                if get_response.status_code == 200:
                    notifications = get_response.json()
                    created_notification = None
                    
                    for notif in notifications:
                        if notif.get('id') == notification_id:
                            created_notification = notif
                            break
                    
                    if created_notification:
                        message = created_notification.get('message', '')
                        title = created_notification.get('title', '')
                        
                        # Check for quality indicators
                        has_price = '€' in message or 'Price:' in message
                        has_description = len(message) > 50  # Substantial content
                        has_specific_title = 'Available' in title or 'Camera' in title
                        is_not_generic = 'generic' not in message.lower() and 'test' not in message.lower()
                        
                        quality_score = sum([has_price, has_description, has_specific_title, is_not_generic])
                        
                        if quality_score >= 3:
                            self.log_test(
                                "Notification Content Quality", 
                                True, 
                                f"High-quality content detected. Title: '{title[:50]}...', Message length: {len(message)} chars, Quality score: {quality_score}/4"
                            )
                            return True
                        else:
                            self.log_test(
                                "Notification Content Quality", 
                                False, 
                                f"Low-quality content. Quality score: {quality_score}/4. Message: '{message[:100]}...'"
                            )
                            return False
                    else:
                        self.log_test("Notification Content Quality", False, error_msg="Created notification not found in list")
                        return False
                else:
                    self.log_test("Notification Content Quality", False, error_msg="Failed to retrieve notifications for content verification")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Notification Content Quality", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Notification Content Quality", False, error_msg=str(e))
            return False

    def test_notification_timing_performance(self):
        """Test timing and performance of notification API calls"""
        if not self.test_user_id:
            self.log_test("Notification Timing Performance", False, error_msg="No test user available")
            return False
            
        try:
            response_times = []
            
            # Test multiple notification creations to measure performance
            for i in range(5):
                notification_data = {
                    "title": f"Performance Test Notification {i+1}",
                    "message": f"Handcrafted Wooden Table - Beautiful handcrafted dining table made from solid oak wood. Perfect for family gatherings and dinner parties. Dimensions: 180x90cm. Price: €450.00. Test #{i+1}",
                    "type": "ad_notification",
                    "ad_id": f"performance_test_ad_{i+1}",
                    "description": f"Handcrafted dining table - Test {i+1}"
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                    json=notification_data,
                    timeout=10
                )
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    notification_id = response.json().get('id')
                    self.created_notifications.append(notification_id)
                
                time.sleep(0.1)  # Small delay between requests
            
            # Calculate performance metrics
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Performance thresholds (reasonable for notification API)
            acceptable_avg_time = 2.0  # 2 seconds average
            acceptable_max_time = 5.0  # 5 seconds maximum
            
            performance_good = avg_response_time <= acceptable_avg_time and max_response_time <= acceptable_max_time
            
            if performance_good:
                self.log_test(
                    "Notification Timing Performance", 
                    True, 
                    f"Good performance: Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s, Min: {min_response_time:.3f}s"
                )
                return True
            else:
                self.log_test(
                    "Notification Timing Performance", 
                    False, 
                    f"Poor performance: Avg: {avg_response_time:.3f}s (limit: {acceptable_avg_time}s), Max: {max_response_time:.3f}s (limit: {acceptable_max_time}s)"
                )
                return False
                
        except Exception as e:
            self.log_test("Notification Timing Performance", False, error_msg=str(e))
            return False

    def test_backend_notification_storage(self):
        """Test that backend notification storage is working correctly"""
        if not self.test_user_id:
            self.log_test("Backend Notification Storage", False, error_msg="No test user available")
            return False
            
        try:
            # Get current notification count
            initial_response = requests.get(f"{BACKEND_URL}/user/{self.test_user_id}/notifications", timeout=10)
            if initial_response.status_code != 200:
                self.log_test("Backend Notification Storage", False, error_msg="Failed to get initial notifications")
                return False
                
            initial_notifications = initial_response.json()
            initial_count = len(initial_notifications)
            
            # Create a test notification
            notification_data = {
                "title": "Storage Test Notification",
                "message": "Gaming Mechanical Keyboard - RGB mechanical gaming keyboard with Cherry MX switches. Perfect for gaming and typing enthusiasts. Features: RGB backlighting, Mechanical switches, Programmable keys. Price: €89.99",
                "type": "ad_notification",
                "ad_id": "storage_test_ad",
                "description": "RGB mechanical gaming keyboard"
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                json=notification_data,
                timeout=10
            )
            
            if create_response.status_code != 200:
                self.log_test("Backend Notification Storage", False, error_msg="Failed to create test notification")
                return False
                
            created_id = create_response.json().get('id')
            self.created_notifications.append(created_id)
            
            # Verify storage by retrieving notifications again
            final_response = requests.get(f"{BACKEND_URL}/user/{self.test_user_id}/notifications", timeout=10)
            if final_response.status_code != 200:
                self.log_test("Backend Notification Storage", False, error_msg="Failed to get final notifications")
                return False
                
            final_notifications = final_response.json()
            final_count = len(final_notifications)
            
            # Find the created notification
            stored_notification = None
            for notif in final_notifications:
                if notif.get('id') == created_id:
                    stored_notification = notif
                    break
            
            # Verify storage correctness
            count_increased = final_count == initial_count + 1
            notification_found = stored_notification is not None
            data_preserved = False
            
            if stored_notification:
                data_preserved = (
                    stored_notification.get('title') == notification_data['title'] and
                    stored_notification.get('message') == notification_data['message'] and
                    stored_notification.get('type') == notification_data['type'] and
                    stored_notification.get('user_id') == self.test_user_id and
                    'created_at' in stored_notification and
                    'read' in stored_notification
                )
            
            if count_increased and notification_found and data_preserved:
                self.log_test(
                    "Backend Notification Storage", 
                    True, 
                    f"Storage working correctly. Count: {initial_count} → {final_count}, Data preserved: {data_preserved}"
                )
                return True
            else:
                issues = []
                if not count_increased:
                    issues.append(f"Count not increased ({initial_count} → {final_count})")
                if not notification_found:
                    issues.append("Notification not found in storage")
                if not data_preserved:
                    issues.append("Data not properly preserved")
                    
                self.log_test(
                    "Backend Notification Storage", 
                    False, 
                    f"Storage issues: {', '.join(issues)}"
                )
                return False
                
        except Exception as e:
            self.log_test("Backend Notification Storage", False, error_msg=str(e))
            return False

    def test_notification_retrieval_and_management(self):
        """Test notification retrieval and management operations"""
        if not self.test_user_id:
            self.log_test("Notification Retrieval and Management", False, error_msg="No test user available")
            return False
            
        try:
            # Create a test notification for management testing
            notification_data = {
                "title": "Management Test Notification",
                "message": "Designer Handbag Collection - Authentic designer handbag in excellent condition. Comes with original packaging and authenticity certificate. Brand: Premium Designer. Price: €680.00",
                "type": "ad_notification",
                "ad_id": "management_test_ad",
                "description": "Authentic designer handbag with certificate"
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                json=notification_data,
                timeout=10
            )
            
            if create_response.status_code != 200:
                self.log_test("Notification Retrieval and Management", False, error_msg="Failed to create test notification")
                return False
                
            notification_id = create_response.json().get('id')
            self.created_notifications.append(notification_id)
            
            # Test marking as read
            read_response = requests.put(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications/{notification_id}/read",
                timeout=10
            )
            
            read_success = read_response.status_code == 200
            
            # Test updating notification properties
            update_response = requests.put(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications/{notification_id}",
                json={"read": True, "archived": False},
                timeout=10
            )
            
            update_success = update_response.status_code == 200
            
            # Verify the changes by retrieving notifications
            get_response = requests.get(f"{BACKEND_URL}/user/{self.test_user_id}/notifications", timeout=10)
            if get_response.status_code == 200:
                notifications = get_response.json()
                updated_notification = None
                
                for notif in notifications:
                    if notif.get('id') == notification_id:
                        updated_notification = notif
                        break
                
                if updated_notification and updated_notification.get('read') == True:
                    self.log_test(
                        "Notification Retrieval and Management", 
                        True, 
                        f"Management operations successful. Read: {read_success}, Update: {update_success}, Status verified: True"
                    )
                    return True
                else:
                    self.log_test(
                        "Notification Retrieval and Management", 
                        False, 
                        f"Status verification failed. Read: {read_success}, Update: {update_success}"
                    )
                    return False
            else:
                self.log_test("Notification Retrieval and Management", False, error_msg="Failed to retrieve notifications for verification")
                return False
                
        except Exception as e:
            self.log_test("Notification Retrieval and Management", False, error_msg=str(e))
            return False

    def test_concurrent_notification_creation(self):
        """Test concurrent notification creation to check for race conditions"""
        if not self.test_user_id:
            self.log_test("Concurrent Notification Creation", False, error_msg="No test user available")
            return False
            
        try:
            # Get initial count
            initial_response = requests.get(f"{BACKEND_URL}/user/{self.test_user_id}/notifications", timeout=10)
            if initial_response.status_code != 200:
                self.log_test("Concurrent Notification Creation", False, error_msg="Failed to get initial notifications")
                return False
                
            initial_count = len(initial_response.json())
            
            # Create multiple notifications concurrently
            def create_notification(index):
                notification_data = {
                    "title": f"Concurrent Test {index}",
                    "message": f"Fitness Equipment Set - Complete home fitness set including dumbbells, resistance bands, and yoga mat. Perfect for home workouts. Set #{index}. Price: €125.00",
                    "type": "ad_notification",
                    "ad_id": f"concurrent_test_ad_{index}",
                    "description": f"Home fitness equipment set #{index}"
                }
                
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                        json=notification_data,
                        timeout=10
                    )
                    if response.status_code == 200:
                        return response.json().get('id')
                except:
                    pass
                return None
            
            # Create 5 notifications concurrently
            threads = []
            results = [None] * 5
            
            def thread_worker(index):
                results[index] = create_notification(index + 1)
            
            for i in range(5):
                thread = threading.Thread(target=thread_worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Add successful IDs to cleanup list
            for result in results:
                if result:
                    self.created_notifications.append(result)
            
            # Check final count
            final_response = requests.get(f"{BACKEND_URL}/user/{self.test_user_id}/notifications", timeout=10)
            if final_response.status_code != 200:
                self.log_test("Concurrent Notification Creation", False, error_msg="Failed to get final notifications")
                return False
                
            final_count = len(final_response.json())
            successful_creates = len([r for r in results if r is not None])
            expected_count = initial_count + successful_creates
            
            if final_count == expected_count:
                self.log_test(
                    "Concurrent Notification Creation", 
                    True, 
                    f"Concurrent creation successful. Created: {successful_creates}, Expected count: {expected_count}, Actual count: {final_count}"
                )
                return True
            else:
                self.log_test(
                    "Concurrent Notification Creation", 
                    False, 
                    f"Count mismatch. Created: {successful_creates}, Expected: {expected_count}, Actual: {final_count}"
                )
                return False
                
        except Exception as e:
            self.log_test("Concurrent Notification Creation", False, error_msg=str(e))
            return False

    def cleanup_test_notifications(self):
        """Clean up test notifications created during testing"""
        if not self.test_user_id or not self.created_notifications:
            return
            
        cleaned_count = 0
        for notification_id in self.created_notifications:
            try:
                response = requests.delete(
                    f"{BACKEND_URL}/user/{self.test_user_id}/notifications/{notification_id}",
                    timeout=10
                )
                if response.status_code == 200:
                    cleaned_count += 1
            except:
                pass  # Ignore cleanup errors
        
        if cleaned_count > 0:
            self.log_test(
                "Test Cleanup", 
                True, 
                f"Successfully cleaned up {cleaned_count}/{len(self.created_notifications)} test notifications"
            )

    def run_notification_system_tests(self):
        """Run comprehensive notification system tests"""
        print("=" * 80)
        print("CATALORO NOTIFICATION SYSTEM TESTING - DUPLICATE FIXES VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Setup
        print("🔧 SETUP")
        print("-" * 40)
        if not self.setup_test_user():
            print("❌ Setup failed. Aborting notification system testing.")
            return
        
        # 2. Test notification creation endpoint
        print("📝 NOTIFICATION CREATION ENDPOINT TESTING")
        print("-" * 40)
        self.test_notification_creation_endpoint()
        
        # 3. Test for duplicate notifications
        print("🔄 DUPLICATE NOTIFICATION PREVENTION TESTING")
        print("-" * 40)
        self.test_duplicate_notification_prevention()
        
        # 4. Test notification content quality
        print("📋 NOTIFICATION CONTENT QUALITY TESTING")
        print("-" * 40)
        self.test_notification_content_quality()
        
        # 5. Test timing and performance
        print("⏱️ TIMING AND PERFORMANCE TESTING")
        print("-" * 40)
        self.test_notification_timing_performance()
        
        # 6. Test backend storage
        print("💾 BACKEND STORAGE TESTING")
        print("-" * 40)
        self.test_backend_notification_storage()
        
        # 7. Test retrieval and management
        print("🔍 RETRIEVAL AND MANAGEMENT TESTING")
        print("-" * 40)
        self.test_notification_retrieval_and_management()
        
        # 8. Test concurrent creation
        print("🔀 CONCURRENT CREATION TESTING")
        print("-" * 40)
        self.test_concurrent_notification_creation()
        
        # 9. Cleanup
        print("🧹 CLEANUP")
        print("-" * 40)
        self.cleanup_test_notifications()
        
        # Print Summary
        print("=" * 80)
        print("NOTIFICATION SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Key focus areas summary
        print("KEY FOCUS AREAS RESULTS:")
        focus_tests = [
            "Notification Creation Endpoint",
            "Duplicate Notification Prevention", 
            "Notification Content Quality",
            "Notification Timing Performance",
            "Backend Notification Storage"
        ]
        
        for test_name in focus_tests:
            result = next((r for r in self.test_results if r['test'] == test_name), None)
            if result:
                status = "✅" if "✅" in result['status'] else "❌"
                print(f"  {status} {test_name}")
        
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 NOTIFICATION SYSTEM TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = NotificationSystemTester()
    
    print("🔔 RUNNING NOTIFICATION SYSTEM TESTING AS REQUESTED")
    print("Testing notification system after duplicate notification fixes...")
    print()
    
    passed, failed, results = tester.run_notification_system_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)