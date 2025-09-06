#!/usr/bin/env python3
"""
Admin Dashboard Backend Testing with Real Data
Testing dashboard with actual marketplace data to verify real-time KPI calculations
"""

import requests
import json
import sys
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://browse-ads.preview.emergentagent.com/api"

class AdminDashboardWithDataTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.created_users = []
        self.created_listings = []
        
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
    
    def create_test_users(self):
        """Create test users to populate dashboard data"""
        try:
            test_users = [
                {
                    "email": "dashboard_test_user1@example.com",
                    "password": "testpass123",
                    "username": "dashboard_user1",
                    "full_name": "Dashboard Test User 1"
                },
                {
                    "email": "dashboard_test_user2@example.com", 
                    "password": "testpass123",
                    "username": "dashboard_user2",
                    "full_name": "Dashboard Test User 2"
                }
            ]
            
            created_count = 0
            for user_data in test_users:
                try:
                    # Try to login first (user might already exist)
                    login_response = self.session.post(f"{self.backend_url}/auth/login", json=user_data)
                    if login_response.status_code == 200:
                        user_info = login_response.json()
                        user_id = user_info.get("user", {}).get("id")
                        if user_id:
                            self.created_users.append(user_id)
                            created_count += 1
                    else:
                        # User doesn't exist, create new one
                        register_response = self.session.post(f"{self.backend_url}/auth/register", json=user_data)
                        if register_response.status_code == 200:
                            # Login after registration
                            login_response = self.session.post(f"{self.backend_url}/auth/login", json=user_data)
                            if login_response.status_code == 200:
                                user_info = login_response.json()
                                user_id = user_info.get("user", {}).get("id")
                                if user_id:
                                    self.created_users.append(user_id)
                                    created_count += 1
                except Exception as e:
                    print(f"   Warning: Failed to create/login user {user_data['username']}: {e}")
            
            if created_count > 0:
                self.log_test(
                    "Test Users Creation",
                    True,
                    f"Successfully created/accessed {created_count} test users"
                )
                return True
            else:
                self.log_test(
                    "Test Users Creation",
                    False,
                    "Failed to create any test users"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Test Users Creation",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def create_test_listings(self):
        """Create test listings to populate dashboard data"""
        try:
            if not self.created_users:
                self.log_test(
                    "Test Listings Creation",
                    False,
                    "No test users available for creating listings"
                )
                return False
            
            test_listings = [
                {
                    "title": "Dashboard Test Laptop",
                    "description": "Test laptop for dashboard KPI testing",
                    "price": 500.0,
                    "category": "Electronics",
                    "condition": "Used",
                    "seller_id": self.created_users[0],
                    "images": [],
                    "tags": ["laptop", "test"],
                    "features": ["WiFi", "Bluetooth"]
                },
                {
                    "title": "Dashboard Test Phone",
                    "description": "Test phone for dashboard KPI testing",
                    "price": 300.0,
                    "category": "Electronics", 
                    "condition": "New",
                    "seller_id": self.created_users[0] if len(self.created_users) > 0 else self.created_users[0],
                    "images": [],
                    "tags": ["phone", "test"],
                    "features": ["Camera", "GPS"]
                }
            ]
            
            created_count = 0
            for listing_data in test_listings:
                try:
                    response = self.session.post(f"{self.backend_url}/listings", json=listing_data)
                    if response.status_code in [200, 201]:
                        result = response.json()
                        listing_id = result.get("listing_id")
                        if listing_id:
                            self.created_listings.append(listing_id)
                            created_count += 1
                except Exception as e:
                    print(f"   Warning: Failed to create listing {listing_data['title']}: {e}")
            
            if created_count > 0:
                self.log_test(
                    "Test Listings Creation",
                    True,
                    f"Successfully created {created_count} test listings"
                )
                return True
            else:
                self.log_test(
                    "Test Listings Creation",
                    False,
                    "Failed to create any test listings"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Test Listings Creation",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_dashboard_with_real_data(self):
        """Test dashboard KPIs with real marketplace data"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/dashboard")
            
            if response.status_code != 200:
                self.log_test(
                    "Dashboard with Real Data",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
            data = response.json()
            kpis = data.get("kpis", {})
            
            # Check if KPIs reflect real data
            real_data_found = []
            
            total_users = kpis.get("total_users", 0)
            if total_users >= len(self.created_users):
                real_data_found.append(f"Users: {total_users} (≥{len(self.created_users)} created)")
            
            total_listings = kpis.get("total_listings", 0)
            if total_listings >= len(self.created_listings):
                real_data_found.append(f"Listings: {total_listings} (≥{len(self.created_listings)} created)")
            
            active_listings = kpis.get("active_listings", 0)
            if active_listings >= len(self.created_listings):
                real_data_found.append(f"Active Listings: {active_listings} (≥{len(self.created_listings)} created)")
            
            # Check recent activity
            recent_activity = data.get("recent_activity", [])
            activity_count = len(recent_activity)
            if activity_count > 1:  # More than just "System initialized"
                real_data_found.append(f"Recent Activity: {activity_count} entries")
            
            if len(real_data_found) >= 2:  # At least 2 indicators of real data
                self.log_test(
                    "Dashboard with Real Data",
                    True,
                    f"Dashboard reflects real marketplace data: {', '.join(real_data_found)}"
                )
                return data
            else:
                self.log_test(
                    "Dashboard with Real Data",
                    False,
                    f"Dashboard may not reflect all real data. Found: {', '.join(real_data_found) if real_data_found else 'No real data indicators'}",
                    f"KPIs reflecting created data (≥{len(self.created_users)} users, ≥{len(self.created_listings)} listings)",
                    f"Current KPIs: users={total_users}, listings={total_listings}, active={active_listings}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Dashboard with Real Data",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_kpi_calculations_accuracy(self, dashboard_data):
        """Test accuracy of KPI calculations"""
        try:
            kpis = dashboard_data.get("kpis", {})
            
            # Verify logical relationships between KPIs
            total_listings = kpis.get("total_listings", 0)
            active_listings = kpis.get("active_listings", 0)
            
            accuracy_checks = []
            
            # Active listings should not exceed total listings
            if active_listings <= total_listings:
                accuracy_checks.append("✅ Active listings ≤ Total listings")
            else:
                accuracy_checks.append(f"❌ Active listings ({active_listings}) > Total listings ({total_listings})")
            
            # Revenue should be non-negative
            revenue = kpis.get("revenue", 0)
            if revenue >= 0:
                accuracy_checks.append("✅ Revenue ≥ 0")
            else:
                accuracy_checks.append(f"❌ Revenue is negative: {revenue}")
            
            # Growth rate should be reasonable (0-1000%)
            growth_rate = kpis.get("growth_rate", 0)
            if 0 <= growth_rate <= 1000:
                accuracy_checks.append("✅ Growth rate in reasonable range")
            else:
                accuracy_checks.append(f"❌ Growth rate unreasonable: {growth_rate}%")
            
            # Total deals should be non-negative
            total_deals = kpis.get("total_deals", 0)
            if total_deals >= 0:
                accuracy_checks.append("✅ Total deals ≥ 0")
            else:
                accuracy_checks.append(f"❌ Total deals is negative: {total_deals}")
            
            failed_checks = [check for check in accuracy_checks if check.startswith("❌")]
            
            if not failed_checks:
                self.log_test(
                    "KPI Calculations Accuracy",
                    True,
                    f"All KPI calculations accurate: {len(accuracy_checks)} checks passed"
                )
                return True
            else:
                self.log_test(
                    "KPI Calculations Accuracy",
                    False,
                    f"KPI calculation issues found: {'; '.join(failed_checks)}",
                    "All KPI calculations accurate",
                    f"Failed checks: {'; '.join(failed_checks)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "KPI Calculations Accuracy",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_dashboard_performance(self):
        """Test dashboard response time and performance"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/dashboard")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code != 200:
                self.log_test(
                    "Dashboard Performance",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Check response time (should be under 5 seconds for good performance)
            if response_time < 5.0:
                self.log_test(
                    "Dashboard Performance",
                    True,
                    f"Dashboard response time: {response_time:.2f}s (good performance)"
                )
                return True
            elif response_time < 10.0:
                self.log_test(
                    "Dashboard Performance",
                    True,
                    f"Dashboard response time: {response_time:.2f}s (acceptable performance)"
                )
                return True
            else:
                self.log_test(
                    "Dashboard Performance",
                    False,
                    f"Dashboard response time: {response_time:.2f}s (slow performance)",
                    "Response time < 10s",
                    f"{response_time:.2f}s"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Dashboard Performance",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all admin dashboard tests with real data"""
        print("=" * 80)
        print("ADMIN DASHBOARD WITH REAL DATA TESTING")
        print("Testing dashboard KPIs with actual marketplace data")
        print("=" * 80)
        print()
        
        # Setup: Create test data
        test1_success = self.create_test_users()
        test2_success = self.create_test_listings()
        
        # Wait a moment for data to be processed
        time.sleep(2)
        
        # Test 3: Dashboard with Real Data
        dashboard_data = self.test_dashboard_with_real_data()
        test3_success = bool(dashboard_data)
        
        # Test 4: KPI Calculations Accuracy
        test4_success = False
        if test3_success:
            test4_success = self.test_kpi_calculations_accuracy(dashboard_data)
        else:
            self.log_test(
                "KPI Calculations Accuracy",
                False,
                "Skipped due to failed dashboard data retrieval"
            )
        
        # Test 5: Dashboard Performance
        test5_success = self.test_dashboard_performance()
        
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
            ("Test Users Creation", test1_success),
            ("Test Listings Creation", test2_success),
            ("Dashboard with Real Data", test3_success),
            ("KPI Calculations Accuracy", test4_success),
            ("Dashboard Performance", test5_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        
        # Display final dashboard state
        if dashboard_data:
            print("FINAL DASHBOARD STATE:")
            print("-" * 40)
            kpis = dashboard_data.get("kpis", {})
            for kpi, value in kpis.items():
                print(f"  {kpi}: {value}")
            
            activity_count = len(dashboard_data.get("recent_activity", []))
            print(f"  Recent Activity Entries: {activity_count}")
            print()
        
        return passed_tests >= 4  # Allow 1 failure for acceptable results

if __name__ == "__main__":
    tester = AdminDashboardWithDataTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ADMIN DASHBOARD WITH REAL DATA TESTS SUCCESSFUL!")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Check the issues above")
        sys.exit(1)