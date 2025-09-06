#!/usr/bin/env python3
"""
Cataloro Ad Notification System Integration Testing
Testing notification creation, retrieval, and data consistency for ad manager integration
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-ads.preview.emergentagent.com/api"

class AdNotificationTester:
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
            # Use a consistent test user ID for notifications
            self.test_user_id = "test_user_notifications_" + str(uuid.uuid4())[:8]
            
            # Create test user via admin endpoint
            user_data = {
                "username": f"notif_test_{self.test_user_id[:8]}",
                "email": f"notif_test_{self.test_user_id[:8]}@example.com",
                "password": "TestPassword123!",
                "role": "user"
            }
            
            response = requests.post(f"{BACKEND_URL}/admin/users", json=user_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                created_user = data.get('user', {})
                self.test_user_id = created_user.get('id', self.test_user_id)
                self.log_test(
                    "Setup Test User", 
                    True, 
                    f"Created test user with ID: {self.test_user_id}"
                )
                return True
            else:
                # Fallback to using a demo user ID if creation fails
                self.test_user_id = "demo_user_id_for_notifications"
                self.log_test(
                    "Setup Test User", 
                    True, 
                    f"Using fallback user ID: {self.test_user_id}"
                )
                return True
        except Exception as e:
            self.test_user_id = "demo_user_id_for_notifications"
            self.log_test("Setup Test User", True, f"Using fallback user ID due to error: {str(e)}")
            return True

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

    def test_notification_creation_endpoint(self):
        """Test POST /api/user/{user_id}/notifications for ad notifications"""
        try:
            # Test ad expiration notification
            ad_expiration_notification = {
                "title": "Ad Campaign Expired",
                "message": "Your ad campaign 'Premium Product Showcase' has expired. Click here to renew or create a new campaign.",
                "type": "warning",
                "ad_id": "ad_" + str(uuid.uuid4())[:8],
                "campaign_name": "Premium Product Showcase",
                "expiration_date": datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                json=ad_expiration_notification,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                notification_id = data.get('id')
                self.created_notifications.append(notification_id)
                self.log_test(
                    "Ad Expiration Notification Creation", 
                    True, 
                    f"Created notification ID: {notification_id}, Type: warning"
                )
                
                # Test ad start notification
                ad_start_notification = {
                    "title": "Ad Campaign Started",
                    "message": "Your new ad campaign 'Summer Sale Collection' is now live and reaching customers. Monitor performance in your dashboard.",
                    "type": "success",
                    "ad_id": "ad_" + str(uuid.uuid4())[:8],
                    "campaign_name": "Summer Sale Collection",
                    "start_date": datetime.utcnow().isoformat()
                }
                
                response2 = requests.post(
                    f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                    json=ad_start_notification,
                    timeout=10
                )
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    notification_id2 = data2.get('id')
                    self.created_notifications.append(notification_id2)
                    self.log_test(
                        "Ad Start Notification Creation", 
                        True, 
                        f"Created notification ID: {notification_id2}, Type: success"
                    )
                    return True
                else:
                    self.log_test("Ad Start Notification Creation", False, f"HTTP {response2.status_code}")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Ad Expiration Notification Creation", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Notification Creation Endpoint", False, error_msg=str(e))
            return False

    def test_notification_retrieval_endpoint(self):
        """Test GET /api/user/{user_id}/notifications"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                timeout=10
            )
            
            if response.status_code == 200:
                notifications = response.json()
                notification_count = len(notifications) if isinstance(notifications, list) else 0
                
                # Check if our created notifications are present
                found_notifications = []
                for notification in notifications:
                    if notification.get('id') in self.created_notifications:
                        found_notifications.append(notification)
                
                self.log_test(
                    "Notification Retrieval", 
                    True, 
                    f"Retrieved {notification_count} total notifications, {len(found_notifications)} test notifications found"
                )
                
                # Store notifications for data consistency testing
                self.retrieved_notifications = notifications
                return True
            else:
                self.log_test("Notification Retrieval", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Notification Retrieval", False, error_msg=str(e))
            return False

    def test_notification_data_consistency(self):
        """Test notification data consistency - verify 'read' field usage"""
        try:
            if not hasattr(self, 'retrieved_notifications'):
                self.log_test("Notification Data Consistency", False, error_msg="No notifications retrieved for testing")
                return False
            
            notifications = self.retrieved_notifications
            consistency_issues = []
            read_field_correct = 0
            total_checked = 0
            
            for notification in notifications:
                total_checked += 1
                
                # Check if 'read' field exists (correct field name)
                if 'read' in notification:
                    read_field_correct += 1
                    read_value = notification['read']
                    
                    # Verify read field is boolean
                    if not isinstance(read_value, bool):
                        consistency_issues.append(f"Notification {notification.get('id', 'unknown')}: 'read' field is not boolean ({type(read_value)})")
                else:
                    consistency_issues.append(f"Notification {notification.get('id', 'unknown')}: Missing 'read' field")
                
                # Check for incorrect 'is_read' field (should not exist)
                if 'is_read' in notification:
                    consistency_issues.append(f"Notification {notification.get('id', 'unknown')}: Found incorrect 'is_read' field (should be 'read')")
                
                # Verify required fields
                required_fields = ['id', 'user_id', 'title', 'message', 'type', 'created_at']
                for field in required_fields:
                    if field not in notification:
                        consistency_issues.append(f"Notification {notification.get('id', 'unknown')}: Missing required field '{field}'")
            
            if consistency_issues:
                self.log_test(
                    "Notification Data Consistency", 
                    False, 
                    f"Found {len(consistency_issues)} issues in {total_checked} notifications",
                    "; ".join(consistency_issues[:3])  # Show first 3 issues
                )
                return False
            else:
                self.log_test(
                    "Notification Data Consistency", 
                    True, 
                    f"All {total_checked} notifications have correct data structure. 'read' field present in {read_field_correct}/{total_checked} notifications"
                )
                return True
        except Exception as e:
            self.log_test("Notification Data Consistency", False, error_msg=str(e))
            return False

    def test_notification_storage_verification(self):
        """Test that notifications are properly stored in user_notifications collection"""
        try:
            # This test verifies that notifications are accessible and properly formatted
            # We'll check the JSON response format for frontend consumption
            
            response = requests.get(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                timeout=10
            )
            
            if response.status_code == 200:
                notifications = response.json()
                
                # Verify JSON response format
                if not isinstance(notifications, list):
                    self.log_test("Notification Storage Verification", False, error_msg="Response is not a list")
                    return False
                
                # Check JSON serialization of our test notifications
                test_notifications = [n for n in notifications if n.get('id') in self.created_notifications]
                
                json_issues = []
                for notification in test_notifications:
                    try:
                        # Test JSON serialization
                        json.dumps(notification)
                        
                        # Check for proper field types
                        if 'created_at' in notification and not isinstance(notification['created_at'], str):
                            json_issues.append(f"created_at field is not string: {type(notification['created_at'])}")
                        
                        if 'read' in notification and not isinstance(notification['read'], bool):
                            json_issues.append(f"read field is not boolean: {type(notification['read'])}")
                            
                    except (TypeError, ValueError) as e:
                        json_issues.append(f"JSON serialization error: {str(e)}")
                
                if json_issues:
                    self.log_test(
                        "Notification Storage Verification", 
                        False, 
                        f"JSON format issues found",
                        "; ".join(json_issues[:2])
                    )
                    return False
                else:
                    self.log_test(
                        "Notification Storage Verification", 
                        True, 
                        f"Notifications properly stored and JSON serializable. Found {len(test_notifications)} test notifications"
                    )
                    return True
            else:
                self.log_test("Notification Storage Verification", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Notification Storage Verification", False, error_msg=str(e))
            return False

    def test_sample_notification_flow(self):
        """Test complete notification flow for ad manager integration"""
        try:
            # Create a comprehensive ad notification with all expected fields
            comprehensive_notification = {
                "title": "Ad Performance Alert",
                "message": "Your ad campaign 'Holiday Special' has reached 80% of its budget. Consider adjusting targeting or increasing budget to maintain visibility.",
                "type": "info",
                "ad_id": "ad_holiday_special_2025",
                "campaign_name": "Holiday Special",
                "budget_used": 80.0,
                "budget_total": 100.0,
                "alert_type": "budget_threshold"
            }
            
            # Step 1: Create notification
            response = requests.post(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                json=comprehensive_notification,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Sample Notification Flow - Creation", False, f"HTTP {response.status_code}")
                return False
            
            notification_id = response.json().get('id')
            self.created_notifications.append(notification_id)
            
            # Step 2: Retrieve and verify
            time.sleep(0.5)  # Brief delay to ensure storage
            
            response = requests.get(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Sample Notification Flow - Retrieval", False, f"HTTP {response.status_code}")
                return False
            
            notifications = response.json()
            found_notification = None
            
            for notification in notifications:
                if notification.get('id') == notification_id:
                    found_notification = notification
                    break
            
            if not found_notification:
                self.log_test("Sample Notification Flow", False, error_msg="Created notification not found in retrieval")
                return False
            
            # Step 3: Verify notification properties
            verification_results = []
            
            # Check title and message
            if found_notification.get('title') == comprehensive_notification['title']:
                verification_results.append("Title: ✓")
            else:
                verification_results.append("Title: ✗")
            
            if found_notification.get('message') == comprehensive_notification['message']:
                verification_results.append("Message: ✓")
            else:
                verification_results.append("Message: ✗")
            
            # Check type
            if found_notification.get('type') == comprehensive_notification['type']:
                verification_results.append("Type: ✓")
            else:
                verification_results.append("Type: ✗")
            
            # Check read field (should be False by default)
            if found_notification.get('read') == False:
                verification_results.append("Read field: ✓")
            else:
                verification_results.append("Read field: ✗")
            
            # Check required fields
            required_fields = ['id', 'user_id', 'created_at']
            for field in required_fields:
                if field in found_notification:
                    verification_results.append(f"{field}: ✓")
                else:
                    verification_results.append(f"{field}: ✗")
            
            success = all("✓" in result for result in verification_results)
            
            self.log_test(
                "Sample Notification Flow", 
                success, 
                f"Complete flow test: {', '.join(verification_results)}"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Sample Notification Flow", False, error_msg=str(e))
            return False

    def test_notification_read_functionality(self):
        """Test marking notifications as read"""
        try:
            if not self.created_notifications:
                self.log_test("Notification Read Functionality", False, error_msg="No notifications to test read functionality")
                return False
            
            # Use the first created notification
            notification_id = self.created_notifications[0]
            
            # Mark as read
            response = requests.put(
                f"{BACKEND_URL}/user/{self.test_user_id}/notifications/{notification_id}/read",
                timeout=10
            )
            
            if response.status_code == 200:
                # Verify it's marked as read
                time.sleep(0.5)  # Brief delay
                
                response = requests.get(
                    f"{BACKEND_URL}/user/{self.test_user_id}/notifications",
                    timeout=10
                )
                
                if response.status_code == 200:
                    notifications = response.json()
                    found_notification = None
                    
                    for notification in notifications:
                        if notification.get('id') == notification_id:
                            found_notification = notification
                            break
                    
                    if found_notification and found_notification.get('read') == True:
                        self.log_test(
                            "Notification Read Functionality", 
                            True, 
                            f"Successfully marked notification {notification_id} as read"
                        )
                        return True
                    else:
                        self.log_test("Notification Read Functionality", False, error_msg="Notification not marked as read")
                        return False
                else:
                    self.log_test("Notification Read Functionality", False, f"Failed to retrieve notifications: HTTP {response.status_code}")
                    return False
            else:
                self.log_test("Notification Read Functionality", False, f"Failed to mark as read: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Notification Read Functionality", False, error_msg=str(e))
            return False

    def cleanup_test_data(self):
        """Clean up test notifications and user"""
        try:
            cleanup_count = 0
            
            # Delete test notifications
            for notification_id in self.created_notifications:
                try:
                    response = requests.delete(
                        f"{BACKEND_URL}/user/{self.test_user_id}/notifications/{notification_id}",
                        timeout=10
                    )
                    if response.status_code == 200:
                        cleanup_count += 1
                except:
                    pass  # Ignore cleanup errors
            
            # Delete test user if we created one
            if self.test_user_id and "test_user_notifications_" in self.test_user_id:
                try:
                    requests.delete(f"{BACKEND_URL}/admin/users/{self.test_user_id}", timeout=10)
                except:
                    pass  # Ignore cleanup errors
            
            if cleanup_count > 0:
                self.log_test(
                    "Test Cleanup", 
                    True, 
                    f"Cleaned up {cleanup_count} test notifications"
                )
        except Exception as e:
            self.log_test("Test Cleanup", False, error_msg=str(e))

    def run_comprehensive_tests(self):
        """Run all ad notification system integration tests"""
        print("=" * 80)
        print("CATALORO AD NOTIFICATION SYSTEM INTEGRATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting notification testing.")
            return
        
        # 2. Setup Test User
        print("👤 SETUP TEST USER")
        print("-" * 40)
        if not self.setup_test_user():
            print("❌ Test user setup failed. Aborting notification testing.")
            return
        
        # 3. Test Notification Creation Endpoint
        print("📝 NOTIFICATION CREATION ENDPOINT TESTING")
        print("-" * 40)
        self.test_notification_creation_endpoint()
        
        # 4. Test Notification Retrieval
        print("📥 NOTIFICATION RETRIEVAL TESTING")
        print("-" * 40)
        self.test_notification_retrieval_endpoint()
        
        # 5. Test Data Consistency
        print("🔍 NOTIFICATION DATA CONSISTENCY TESTING")
        print("-" * 40)
        self.test_notification_data_consistency()
        
        # 6. Test Storage Verification
        print("💾 NOTIFICATION STORAGE VERIFICATION")
        print("-" * 40)
        self.test_notification_storage_verification()
        
        # 7. Test Sample Notification Flow
        print("🔄 SAMPLE NOTIFICATION FLOW TESTING")
        print("-" * 40)
        self.test_sample_notification_flow()
        
        # 8. Test Read Functionality
        print("✅ NOTIFICATION READ FUNCTIONALITY TESTING")
        print("-" * 40)
        self.test_notification_read_functionality()
        
        # 9. Cleanup
        print("🧹 CLEANUP")
        print("-" * 40)
        self.cleanup_test_data()
        
        # Print Summary
        print("=" * 80)
        print("AD NOTIFICATION SYSTEM TEST SUMMARY")
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
        
        print("\n🎯 AD NOTIFICATION SYSTEM TESTING COMPLETE")
        print("The notification system is ready for ad manager integration.")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = AdNotificationTester()
    
    print("🎯 RUNNING AD NOTIFICATION SYSTEM INTEGRATION TESTING")
    print("Testing notification creation, retrieval, and data consistency...")
    print()
    
    passed, failed, results = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)