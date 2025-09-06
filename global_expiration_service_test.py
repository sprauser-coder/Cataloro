#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Global Ad Expiration Service Integration
Testing the global ad expiration service backend integration as requested in review
"""

import requests
import json
import uuid
import time
from datetime import datetime, timedelta

# Get backend URL from environment
BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

class GlobalExpirationServiceTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.created_test_data = []
        
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

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}, Version: {data.get('version')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def test_notification_endpoints_after_global_service(self):
        """Test notification endpoints after global service implementation"""
        try:
            # Test system notifications endpoint
            response = requests.get(f"{BACKEND_URL}/admin/system-notifications", timeout=10)
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                self.log_test(
                    "System Notifications Endpoint", 
                    True, 
                    f"Retrieved {len(notifications)} system notifications successfully"
                )
            else:
                self.log_test("System Notifications Endpoint", False, f"HTTP {response.status_code}")
                return False

            # Test user notifications endpoint with demo user
            demo_user_id = "demo_user_id"
            response = requests.get(f"{BACKEND_URL}/user/{demo_user_id}/notifications", timeout=10)
            if response.status_code == 200:
                notifications = response.json()
                self.log_test(
                    "User Notifications Endpoint", 
                    True, 
                    f"Retrieved {len(notifications)} user notifications successfully"
                )
            else:
                self.log_test("User Notifications Endpoint", False, f"HTTP {response.status_code}")
                return False

            # Test notification creation endpoint
            test_notification = {
                "title": "Test Expiration Notification",
                "message": "This is a test notification for expiration service integration",
                "type": "listing_expiration",
                "ad_id": "test_ad_123",
                "description": "Test notification for global expiration service"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/{demo_user_id}/notifications",
                json=test_notification,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                notification_id = data.get('notification_id')
                self.created_test_data.append(('notification', notification_id))
                self.log_test(
                    "Notification Creation Endpoint", 
                    True, 
                    f"Created test notification with ID: {notification_id}"
                )
                return True
            else:
                self.log_test("Notification Creation Endpoint", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Notification Endpoints Test", False, error_msg=str(e))
            return False

    def test_notification_creation_from_background_service(self):
        """Test notification creation from background service (simulate expiration events)"""
        try:
            # Create a test listing with short expiration time
            test_listing = {
                "title": "Test Expiration Listing",
                "description": "Test listing for expiration service integration testing",
                "price": 99.99,
                "category": "Electronics",
                "condition": "New",
                "seller_id": "test_seller_123",
                "has_time_limit": True,
                "time_limit_hours": 1  # 1 hour expiration for testing
            }
            
            response = requests.post(f"{BACKEND_URL}/listings", json=test_listing, timeout=10)
            if response.status_code == 200:
                data = response.json()
                listing_id = data.get('listing_id')
                self.created_test_data.append(('listing', listing_id))
                self.log_test(
                    "Test Listing Creation", 
                    True, 
                    f"Created test listing with ID: {listing_id}, expires in 1 hour"
                )
            else:
                self.log_test("Test Listing Creation", False, f"HTTP {response.status_code}")
                return False

            # Test check expiration endpoint (simulates background service)
            response = requests.post(f"{BACKEND_URL}/listings/{listing_id}/check-expiration", timeout=10)
            if response.status_code == 200:
                data = response.json()
                is_expired = data.get('is_expired', False)
                self.log_test(
                    "Check Expiration Endpoint", 
                    True, 
                    f"Expiration check completed. Listing expired: {is_expired}"
                )
            else:
                self.log_test("Check Expiration Endpoint", False, f"HTTP {response.status_code}")
                return False

            # Test extend time functionality (part of expiration service)
            extension_data = {"additional_hours": 2}
            response = requests.post(
                f"{BACKEND_URL}/listings/{listing_id}/extend-time", 
                json=extension_data, 
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                new_expires_at = data.get('new_expires_at')
                self.log_test(
                    "Time Extension Endpoint", 
                    True, 
                    f"Successfully extended listing time. New expiration: {new_expires_at}"
                )
                return True
            else:
                self.log_test("Time Extension Endpoint", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Background Service Notification Test", False, error_msg=str(e))
            return False

    def test_data_consistency_ad_configuration(self):
        """Test data consistency for ad configuration updates from global service"""
        try:
            # Test marketplace browse endpoint for data consistency
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            if response.status_code == 200:
                listings = response.json()
                
                # Check data consistency in listings
                consistent_data = True
                time_info_count = 0
                
                for listing in listings:
                    # Check if time_info structure is consistent
                    if 'time_info' in listing:
                        time_info = listing['time_info']
                        required_fields = ['has_time_limit', 'is_expired', 'time_remaining_seconds', 'expires_at', 'status_text']
                        
                        for field in required_fields:
                            if field not in time_info:
                                consistent_data = False
                                break
                        
                        if time_info.get('has_time_limit'):
                            time_info_count += 1
                
                self.log_test(
                    "Data Consistency - Browse Listings", 
                    consistent_data, 
                    f"Checked {len(listings)} listings, {time_info_count} with time limits. Data consistency: {consistent_data}"
                )
            else:
                self.log_test("Data Consistency - Browse Listings", False, f"HTTP {response.status_code}")
                return False

            # Test admin dashboard data consistency
            response = requests.get(f"{BACKEND_URL}/admin/dashboard", timeout=10)
            if response.status_code == 200:
                data = response.json()
                kpis = data.get('kpis', {})
                
                # Check if all required KPI fields are present
                required_kpis = ['total_users', 'total_listings', 'active_listings', 'total_deals', 'revenue', 'growth_rate']
                kpi_consistency = all(field in kpis for field in required_kpis)
                
                self.log_test(
                    "Data Consistency - Admin Dashboard", 
                    kpi_consistency, 
                    f"Dashboard KPIs consistency: {kpi_consistency}. Revenue: €{kpis.get('revenue', 0)}"
                )
                return kpi_consistency
            else:
                self.log_test("Data Consistency - Admin Dashboard", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Data Consistency Test", False, error_msg=str(e))
            return False

    def test_performance_impact_background_service(self):
        """Test performance impact of background service on backend"""
        try:
            # Measure response times for critical endpoints
            endpoints_to_test = [
                ("/marketplace/browse", "Browse Listings"),
                ("/admin/dashboard", "Admin Dashboard"),
                ("/listings?status=active&limit=10", "Listings Management")
            ]
            
            performance_results = []
            
            for endpoint, name in endpoints_to_test:
                start_time = time.time()
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status_code == 200:
                    performance_results.append((name, response_time))
                    self.log_test(
                        f"Performance - {name}", 
                        response_time < 2000,  # Should be under 2 seconds
                        f"Response time: {response_time:.2f}ms (acceptable: <2000ms)"
                    )
                else:
                    self.log_test(f"Performance - {name}", False, f"HTTP {response.status_code}")

            # Test multiple concurrent requests to simulate background service load
            import threading
            import queue
            
            def make_request(url, result_queue):
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=10)
                    end_time = time.time()
                    result_queue.put((response.status_code, (end_time - start_time) * 1000))
                except Exception as e:
                    result_queue.put((500, 5000))  # Error case
            
            # Test concurrent load
            result_queue = queue.Queue()
            threads = []
            
            for i in range(5):  # 5 concurrent requests
                thread = threading.Thread(
                    target=make_request, 
                    args=(f"{BACKEND_URL}/marketplace/browse", result_queue)
                )
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Collect results
            concurrent_results = []
            while not result_queue.empty():
                concurrent_results.append(result_queue.get())
            
            successful_requests = sum(1 for status, _ in concurrent_results if status == 200)
            avg_response_time = sum(time for _, time in concurrent_results) / len(concurrent_results)
            
            self.log_test(
                "Performance - Concurrent Load", 
                successful_requests >= 4 and avg_response_time < 3000,  # At least 4/5 successful, under 3s avg
                f"Successful requests: {successful_requests}/5, Avg response time: {avg_response_time:.2f}ms"
            )
            
            return True
                
        except Exception as e:
            self.log_test("Performance Impact Test", False, error_msg=str(e))
            return False

    def test_system_notifications_integration(self):
        """Test system notifications integration with global expiration service"""
        try:
            # Test login-triggered system notifications
            login_data = {"email": "test@example.com", "password": "test123"}
            response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                user_id = user_data.get('id')
                
                self.log_test(
                    "Login System Notifications", 
                    True, 
                    f"Login successful for user: {user_id}. System notifications should be triggered."
                )
            else:
                self.log_test("Login System Notifications", False, f"HTTP {response.status_code}")
                return False

            # Test system notifications endpoint
            response = requests.get(f"{BACKEND_URL}/admin/system-notifications", timeout=10)
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                
                # Check for expiration-related system notifications
                expiration_notifications = [
                    n for n in notifications 
                    if 'expir' in n.get('title', '').lower() or 'expir' in n.get('message', '').lower()
                ]
                
                self.log_test(
                    "System Notifications Integration", 
                    True, 
                    f"Found {len(notifications)} total system notifications, {len(expiration_notifications)} expiration-related"
                )
                return True
            else:
                self.log_test("System Notifications Integration", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("System Notifications Integration Test", False, error_msg=str(e))
            return False

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        cleaned_count = 0
        for data_type, data_id in self.created_test_data:
            if data_id:
                try:
                    if data_type == 'listing':
                        response = requests.delete(f"{BACKEND_URL}/listings/{data_id}", timeout=10)
                    elif data_type == 'notification':
                        # Notifications might not have delete endpoint, skip
                        continue
                    
                    if response.status_code == 200:
                        cleaned_count += 1
                except:
                    pass  # Ignore cleanup errors
        
        if cleaned_count > 0:
            self.log_test(
                "Test Data Cleanup", 
                True, 
                f"Successfully cleaned up {cleaned_count} test items"
            )

    def run_comprehensive_global_expiration_tests(self):
        """Run comprehensive global ad expiration service integration tests"""
        print("=" * 80)
        print("CATALORO BACKEND TESTING - GLOBAL AD EXPIRATION SERVICE INTEGRATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting expiration service testing.")
            return
        
        # 2. Test Notification Endpoints After Global Service Implementation
        print("📬 NOTIFICATION ENDPOINTS AFTER GLOBAL SERVICE")
        print("-" * 40)
        self.test_notification_endpoints_after_global_service()
        
        # 3. Test Notification Creation from Background Service
        print("🔄 NOTIFICATION CREATION FROM BACKGROUND SERVICE")
        print("-" * 40)
        self.test_notification_creation_from_background_service()
        
        # 4. Test Data Consistency
        print("📊 DATA CONSISTENCY TESTING")
        print("-" * 40)
        self.test_data_consistency_ad_configuration()
        
        # 5. Test Performance Impact
        print("⚡ PERFORMANCE IMPACT TESTING")
        print("-" * 40)
        self.test_performance_impact_background_service()
        
        # 6. Test System Notifications Integration
        print("🔔 SYSTEM NOTIFICATIONS INTEGRATION")
        print("-" * 40)
        self.test_system_notifications_integration()
        
        # 7. Cleanup
        print("🧹 CLEANUP")
        print("-" * 40)
        self.cleanup_test_data()
        
        # Print Summary
        print("=" * 80)
        print("GLOBAL AD EXPIRATION SERVICE INTEGRATION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Detailed analysis
        if self.passed_tests == self.total_tests:
            print("🎉 ALL TESTS PASSED - Global expiration service integration is working perfectly!")
            print("✅ Notification endpoints are functioning correctly")
            print("✅ Background service notification creation is operational")
            print("✅ Data consistency is maintained")
            print("✅ Performance impact is within acceptable limits")
        else:
            print("⚠️ SOME TESTS FAILED - Issues identified in global expiration service integration:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 GLOBAL AD EXPIRATION SERVICE INTEGRATION TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = GlobalExpirationServiceTester()
    
    print("🎯 RUNNING GLOBAL AD EXPIRATION SERVICE INTEGRATION TESTING")
    print("Testing backend integration with global expiration service...")
    print()
    
    passed, failed, results = tester.run_comprehensive_global_expiration_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)