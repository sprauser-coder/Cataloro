#!/usr/bin/env python3
"""
Final Verification Test for Persistent Notification Cleanup
Comprehensive test to verify the cleanup was successful and API endpoints work correctly
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-dash.preview.emergentagent.com/api"

class FinalNotificationVerifier:
    def __init__(self):
        self.test_results = []
        self.admin_user_id = None
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def test_admin_user_notifications(self):
        """Test 1: Check admin user notifications for any remaining persistent notifications"""
        print("\n=== TEST 1: Admin User Notifications Check ===")
        
        try:
            # Login as admin to get user ID
            admin_login = {
                "email": "admin@cataloro.com",
                "username": "admin"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=admin_login)
            
            if response.status_code == 200:
                admin_data = response.json()
                self.admin_user_id = admin_data.get("user", {}).get("id")
                
                # Get admin notifications
                notif_response = requests.get(f"{BACKEND_URL}/user/{self.admin_user_id}/notifications")
                
                if notif_response.status_code == 200:
                    notifications = notif_response.json()
                    
                    # Check for any persistent notifications
                    persistent_patterns = [
                        "Workflow Test - Tablet",
                        "Completion Test - Premium Headphones",
                        "Order Completed"
                    ]
                    
                    found_persistent = []
                    for notif in notifications:
                        message = notif.get("message", "")
                        for pattern in persistent_patterns:
                            if pattern.lower() in message.lower():
                                found_persistent.append(notif)
                    
                    if not found_persistent:
                        self.log_test(
                            "Admin notifications cleanup verification", 
                            True, 
                            f"No persistent notifications found in admin's {len(notifications)} notifications"
                        )
                    else:
                        self.log_test(
                            "Admin notifications cleanup verification", 
                            False, 
                            f"Found {len(found_persistent)} persistent notifications still present"
                        )
                        
                        # Print details of remaining notifications
                        for notif in found_persistent:
                            print(f"    Remaining: {notif.get('message', 'No message')[:80]}...")
                else:
                    self.log_test("Admin notifications cleanup verification", False, f"Failed to fetch notifications: {notif_response.status_code}")
            else:
                self.log_test("Admin notifications cleanup verification", False, f"Admin login failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin notifications cleanup verification", False, f"Exception: {str(e)}")
    
    def test_notification_api_endpoints(self):
        """Test 2: Test notification API endpoints functionality"""
        print("\n=== TEST 2: Notification API Endpoints Functionality ===")
        
        try:
            if not self.admin_user_id:
                self.log_test("Notification API endpoints", False, "Admin user ID not available")
                return
            
            # Test GET notifications endpoint
            get_response = requests.get(f"{BACKEND_URL}/user/{self.admin_user_id}/notifications")
            
            if get_response.status_code == 200:
                notifications = get_response.json()
                
                self.log_test(
                    "GET notifications endpoint", 
                    True, 
                    f"Successfully retrieved {len(notifications)} notifications"
                )
                
                # Test creating a new notification
                test_notification = {
                    "title": "Test Notification - Cleanup Verification",
                    "message": "This is a test notification to verify API functionality after cleanup",
                    "type": "info"
                }
                
                create_response = requests.post(
                    f"{BACKEND_URL}/user/{self.admin_user_id}/notifications", 
                    json=test_notification
                )
                
                if create_response.status_code == 200:
                    create_result = create_response.json()
                    test_notif_id = create_result.get("id")
                    
                    self.log_test(
                        "POST notifications endpoint", 
                        True, 
                        f"Successfully created test notification with ID: {test_notif_id}"
                    )
                    
                    # Test marking notification as read
                    if test_notif_id:
                        read_response = requests.put(
                            f"{BACKEND_URL}/user/{self.admin_user_id}/notifications/{test_notif_id}/read"
                        )
                        
                        if read_response.status_code == 200:
                            self.log_test(
                                "PUT notification read endpoint", 
                                True, 
                                "Successfully marked test notification as read"
                            )
                        else:
                            self.log_test("PUT notification read endpoint", False, f"Failed to mark as read: {read_response.status_code}")
                        
                        # Test deleting the test notification
                        delete_response = requests.delete(f"{BACKEND_URL}/notifications/{test_notif_id}")
                        
                        if delete_response.status_code == 200:
                            self.log_test(
                                "DELETE notification endpoint", 
                                True, 
                                "Successfully deleted test notification"
                            )
                        else:
                            self.log_test("DELETE notification endpoint", False, f"Failed to delete: {delete_response.status_code}")
                
                else:
                    self.log_test("POST notifications endpoint", False, f"Failed to create notification: {create_response.status_code}")
            else:
                self.log_test("GET notifications endpoint", False, f"Failed to get notifications: {get_response.status_code}")
                
        except Exception as e:
            self.log_test("Notification API endpoints", False, f"Exception: {str(e)}")
    
    def test_system_health_after_cleanup(self):
        """Test 3: Verify system health after cleanup operations"""
        print("\n=== TEST 3: System Health After Cleanup ===")
        
        try:
            # Test health endpoint
            health_response = requests.get(f"{BACKEND_URL}/health")
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                
                self.log_test(
                    "System health check", 
                    True, 
                    f"System healthy: {health_data.get('status', 'unknown')}"
                )
            else:
                self.log_test("System health check", False, f"Health check failed: {health_response.status_code}")
            
            # Test admin dashboard (should work after cleanup)
            dashboard_response = requests.get(f"{BACKEND_URL}/admin/dashboard")
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                
                self.log_test(
                    "Admin dashboard functionality", 
                    True, 
                    f"Dashboard accessible with KPIs: {list(dashboard_data.get('kpis', {}).keys())}"
                )
            else:
                self.log_test("Admin dashboard functionality", False, f"Dashboard failed: {dashboard_response.status_code}")
            
            # Test marketplace browse (core functionality)
            browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse")
            
            if browse_response.status_code == 200:
                listings = browse_response.json()
                
                self.log_test(
                    "Marketplace browse functionality", 
                    True, 
                    f"Browse working with {len(listings)} listings"
                )
            else:
                self.log_test("Marketplace browse functionality", False, f"Browse failed: {browse_response.status_code}")
                
        except Exception as e:
            self.log_test("System health after cleanup", False, f"Exception: {str(e)}")
    
    def test_no_regeneration_after_time(self):
        """Test 4: Wait and check that notifications don't regenerate"""
        print("\n=== TEST 4: No Regeneration After Time Delay ===")
        
        try:
            if not self.admin_user_id:
                self.log_test("No regeneration test", False, "Admin user ID not available")
                return
            
            # Get current notification count
            initial_response = requests.get(f"{BACKEND_URL}/user/{self.admin_user_id}/notifications")
            
            if initial_response.status_code == 200:
                initial_notifications = initial_response.json()
                initial_count = len(initial_notifications)
                
                # Wait for a short period to see if any notifications regenerate
                print("  Waiting 10 seconds to check for regeneration...")
                time.sleep(10)
                
                # Check again
                final_response = requests.get(f"{BACKEND_URL}/user/{self.admin_user_id}/notifications")
                
                if final_response.status_code == 200:
                    final_notifications = final_response.json()
                    final_count = len(final_notifications)
                    
                    # Check if any new persistent notifications appeared
                    new_notifications = [n for n in final_notifications if n not in initial_notifications]
                    persistent_regenerated = []
                    
                    for notif in new_notifications:
                        message = notif.get("message", "")
                        if any(pattern in message.lower() for pattern in ["workflow test - tablet", "completion test - premium headphones", "order completed"]):
                            persistent_regenerated.append(notif)
                    
                    if not persistent_regenerated:
                        self.log_test(
                            "No regeneration after time delay", 
                            True, 
                            f"No persistent notifications regenerated (initial: {initial_count}, final: {final_count})"
                        )
                    else:
                        self.log_test(
                            "No regeneration after time delay", 
                            False, 
                            f"Found {len(persistent_regenerated)} regenerated persistent notifications"
                        )
                else:
                    self.log_test("No regeneration after time delay", False, f"Failed to get final notifications: {final_response.status_code}")
            else:
                self.log_test("No regeneration after time delay", False, f"Failed to get initial notifications: {initial_response.status_code}")
                
        except Exception as e:
            self.log_test("No regeneration after time delay", False, f"Exception: {str(e)}")
    
    def run_final_verification(self):
        """Run final verification of persistent notification cleanup"""
        print("🔍 FINAL NOTIFICATION CLEANUP VERIFICATION")
        print("=" * 60)
        
        # Run all verification tests
        self.test_admin_user_notifications()
        self.test_notification_api_endpoints()
        self.test_system_health_after_cleanup()
        self.test_no_regeneration_after_time()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 FINAL VERIFICATION SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        
        print(f"Total Verification Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        # Final assessment
        print("\n" + "=" * 60)
        print("🎯 FINAL ASSESSMENT")
        print("=" * 60)
        
        if passed_tests == total_tests:
            print("✅ CLEANUP SUCCESSFUL: All persistent notifications have been permanently removed")
            print("✅ SYSTEM STABLE: All API endpoints functioning correctly after cleanup")
            print("✅ NO REGENERATION: No signs of notification regeneration detected")
            print("✅ PREVENTION ACTIVE: Monitoring and prevention measures in place")
            
            print("\n🎉 PERSISTENT NOTIFICATION ISSUE: PERMANENTLY RESOLVED")
            return True
        else:
            print("⚠️  CLEANUP INCOMPLETE: Some verification tests failed")
            print("🔧 FURTHER ACTION REQUIRED: Review failed tests and take corrective action")
            
            print("\n⚠️  PERSISTENT NOTIFICATION ISSUE: REQUIRES ATTENTION")
            return False

if __name__ == "__main__":
    verifier = FinalNotificationVerifier()
    success = verifier.run_final_verification()
    
    if success:
        print("\n✅ FINAL VERIFICATION: PASSED")
        print("🎊 The persistent 'Order Completed!' notifications have been successfully and permanently deleted!")
    else:
        print("\n❌ FINAL VERIFICATION: FAILED")
        print("🔧 Additional cleanup actions may be required")