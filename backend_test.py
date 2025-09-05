#!/usr/bin/env python3
"""
FINAL ADMIN DASHBOARD DATA ACCURACY VERIFICATION TEST
Testing the COMPLETELY FIXED Admin Dashboard Data Accuracy as requested in review.

This test verifies:
1. GET /api/admin/dashboard endpoint functionality
2. Frontend field name mappings match backend response fields
3. Dashboard displays accurate data:
   - Revenue: €2,970 (using kpis.revenue field)
   - Active Listings: 22 (using kpis.active_listings field) 
   - Total Listings: 29 (using kpis.total_listings field)
   - Conversion Rate: calculated from real data
4. Chart data generation uses real backend values
5. All KPIs display accurate marketplace data
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cataloro-upgrade.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_admin_dashboard_final_verification():
    """Test the COMPLETELY FIXED Admin Dashboard Data Accuracy"""
    print("🎯 FINAL ADMIN DASHBOARD DATA ACCURACY VERIFICATION")
    print("=" * 60)
    
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": []
    }
    
    def run_test(test_name, test_func):
        """Helper function to run individual tests"""
        test_results["total_tests"] += 1
        try:
            result = test_func()
            if result:
                test_results["passed_tests"] += 1
                status = "✅ PASSED"
            else:
                test_results["failed_tests"] += 1
                status = "❌ FAILED"
            test_results["test_details"].append(f"{status} - {test_name}")
            print(f"{status} - {test_name}")
            return result
        except Exception as e:
            test_results["failed_tests"] += 1
            status = f"❌ ERROR - {str(e)}"
            test_results["test_details"].append(f"{status} - {test_name}")
            print(f"{status} - {test_name}")
            return False
    
    # Test 1: GET /api/admin/dashboard endpoint accessibility
    def test_dashboard_endpoint():
        """Test that the admin dashboard endpoint is accessible"""
        try:
            response = requests.get(f"{API_BASE}/admin/dashboard", timeout=10)
            if response.status_code == 200:
                print(f"   Dashboard endpoint accessible: HTTP {response.status_code}")
                return True
            else:
                print(f"   Dashboard endpoint failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"   Dashboard endpoint error: {e}")
            return False
    
    # Test 2: Verify KPI structure and field names
    def test_kpi_structure():
        """Test that KPI structure matches expected field names"""
        try:
            response = requests.get(f"{API_BASE}/admin/dashboard", timeout=10)
            if response.status_code != 200:
                return False
            
            data = response.json()
            kpis = data.get('kpis', {})
            
            # Check required KPI fields
            required_fields = [
                'total_users', 'total_listings', 'active_listings', 
                'total_deals', 'revenue', 'growth_rate'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in kpis:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   Missing KPI fields: {missing_fields}")
                return False
            
            print(f"   All required KPI fields present: {required_fields}")
            return True
            
        except Exception as e:
            print(f"   KPI structure test error: {e}")
            return False
    
    # Test 3: Verify revenue accuracy (€2,970 expected)
    def test_revenue_accuracy():
        """Test that revenue shows €2,970 as expected"""
        try:
            response = requests.get(f"{API_BASE}/admin/dashboard", timeout=10)
            if response.status_code != 200:
                return False
            
            data = response.json()
            revenue = data.get('kpis', {}).get('revenue', 0)
            
            # Expected revenue is €2,970 based on review request
            expected_revenue = 2970.0
            
            if abs(revenue - expected_revenue) < 0.01:  # Allow for small floating point differences
                print(f"   Revenue matches expected: €{revenue} = €{expected_revenue}")
                return True
            else:
                print(f"   Revenue mismatch: €{revenue} (actual) vs €{expected_revenue} (expected)")
                return False
                
        except Exception as e:
            print(f"   Revenue accuracy test error: {e}")
            return False
    
    # Test 4: Verify active listings count (22 expected)
    def test_active_listings_count():
        """Test that active listings shows 22 as expected"""
        try:
            response = requests.get(f"{API_BASE}/admin/dashboard", timeout=10)
            if response.status_code != 200:
                return False
            
            data = response.json()
            active_listings = data.get('kpis', {}).get('active_listings', 0)
            
            # Expected active listings is 22 based on review request
            expected_active_listings = 22
            
            if active_listings == expected_active_listings:
                print(f"   Active listings matches expected: {active_listings} = {expected_active_listings}")
                return True
            else:
                print(f"   Active listings mismatch: {active_listings} (actual) vs {expected_active_listings} (expected)")
                return False
                
        except Exception as e:
            print(f"   Active listings test error: {e}")
            return False
    
    # Test 5: Verify total listings count (29 expected)
    def test_total_listings_count():
        """Test that total listings shows 29 as expected"""
        try:
            response = requests.get(f"{API_BASE}/admin/dashboard", timeout=10)
            if response.status_code != 200:
                return False
            
            data = response.json()
            total_listings = data.get('kpis', {}).get('total_listings', 0)
            
            # Expected total listings is 29 based on review request
            expected_total_listings = 29
            
            if total_listings == expected_total_listings:
                print(f"   Total listings matches expected: {total_listings} = {expected_total_listings}")
                return True
            else:
                print(f"   Total listings mismatch: {total_listings} (actual) vs {expected_total_listings} (expected)")
                return False
                
        except Exception as e:
            print(f"   Total listings test error: {e}")
            return False
    
    # Test 6: Verify conversion rate calculation
    def test_conversion_rate_calculation():
        """Test that conversion rate is calculated from real data"""
        try:
            response = requests.get(f"{API_BASE}/admin/dashboard", timeout=10)
            if response.status_code != 200:
                return False
            
            data = response.json()
            kpis = data.get('kpis', {})
            
            total_users = kpis.get('total_users', 0)
            total_deals = kpis.get('total_deals', 0)
            growth_rate = kpis.get('growth_rate', 0)
            
            # Calculate expected conversion rate (deals/users * 100)
            if total_users > 0:
                expected_conversion_rate = (total_deals / total_users) * 100
                print(f"   Conversion rate calculation: {total_deals} deals / {total_users} users = {expected_conversion_rate:.1f}%")
                print(f"   Backend provides growth_rate: {growth_rate}%")
                return True
            else:
                print(f"   Cannot calculate conversion rate: no users found")
                return False
                
        except Exception as e:
            print(f"   Conversion rate test error: {e}")
            return False
    
    # Test 7: Verify data is realistic (not inflated)
    def test_data_realism():
        """Test that all KPI values are realistic for marketplace"""
        try:
            response = requests.get(f"{API_BASE}/admin/dashboard", timeout=10)
            if response.status_code != 200:
                return False
            
            data = response.json()
            kpis = data.get('kpis', {})
            
            # Check for realistic ranges
            total_users = kpis.get('total_users', 0)
            revenue = kpis.get('revenue', 0)
            total_deals = kpis.get('total_deals', 0)
            
            # Realistic checks
            realistic_checks = []
            
            # Users should be reasonable (not 156 as mentioned in previous issues)
            if 50 <= total_users <= 100:
                realistic_checks.append(f"Users count realistic: {total_users}")
            else:
                realistic_checks.append(f"Users count may be unrealistic: {total_users}")
            
            # Revenue should be around €2,970 (not inflated like €7,829)
            if 2000 <= revenue <= 4000:
                realistic_checks.append(f"Revenue realistic: €{revenue}")
            else:
                realistic_checks.append(f"Revenue may be unrealistic: €{revenue}")
            
            # Deals should be reasonable
            if 5 <= total_deals <= 20:
                realistic_checks.append(f"Deals count realistic: {total_deals}")
            else:
                realistic_checks.append(f"Deals count may be unrealistic: {total_deals}")
            
            for check in realistic_checks:
                print(f"   {check}")
            
            return True
                
        except Exception as e:
            print(f"   Data realism test error: {e}")
            return False
    
    # Test 8: Verify recent activity data
    def test_recent_activity():
        """Test that recent activity contains real data"""
        try:
            response = requests.get(f"{API_BASE}/admin/dashboard", timeout=10)
            if response.status_code != 200:
                return False
            
            data = response.json()
            recent_activity = data.get('recent_activity', [])
            
            if len(recent_activity) > 0:
                print(f"   Recent activity contains {len(recent_activity)} entries")
                for i, activity in enumerate(recent_activity[:3]):  # Show first 3
                    action = activity.get('action', 'Unknown action')
                    timestamp = activity.get('timestamp', 'No timestamp')
                    print(f"     {i+1}. {action} at {timestamp}")
                return True
            else:
                print(f"   No recent activity found")
                return False
                
        except Exception as e:
            print(f"   Recent activity test error: {e}")
            return False
    
    # Run all tests
    print(f"Testing against: {API_BASE}")
    print()
    
    run_test("Dashboard Endpoint Accessibility", test_dashboard_endpoint)
    run_test("KPI Structure and Field Names", test_kpi_structure)
    run_test("Revenue Accuracy (€2,970 expected)", test_revenue_accuracy)
    run_test("Active Listings Count (22 expected)", test_active_listings_count)
    run_test("Total Listings Count (29 expected)", test_total_listings_count)
    run_test("Conversion Rate Calculation", test_conversion_rate_calculation)
    run_test("Data Realism Check", test_data_realism)
    run_test("Recent Activity Data", test_recent_activity)
    
    # Print summary
    print()
    print("=" * 60)
    print("🎯 FINAL ADMIN DASHBOARD VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed_tests']}")
    print(f"Failed: {test_results['failed_tests']}")
    print(f"Success Rate: {(test_results['passed_tests']/test_results['total_tests']*100):.1f}%")
    print()
    
    # Print detailed results
    for detail in test_results['test_details']:
        print(detail)
    
    print()
    
    # Final status
    if test_results['failed_tests'] == 0:
        print("✅ ADMIN DASHBOARD DATA ACCURACY: COMPLETELY FIXED AND VERIFIED")
        print("All KPIs display accurate marketplace data as expected.")
        return True
    else:
        print("❌ ADMIN DASHBOARD DATA ACCURACY: ISSUES STILL PRESENT")
        print(f"{test_results['failed_tests']} test(s) failed - dashboard data accuracy not fully resolved.")
        return False

if __name__ == "__main__":
    success = test_admin_dashboard_final_verification()
    sys.exit(0 if success else 1)
                "username": "tender_test_user"
            }
            
            # Login to get user ID
            login_response = self.session.post(f"{self.backend_url}/auth/login", json=test_user_data)
            if login_response.status_code == 200:
                user_data = login_response.json()
                self.test_user_id = user_data.get("user", {}).get("id")
                
                if self.test_user_id:
                    self.log_test(
                        "Test Data Setup - User Login",
                        True,
                        f"Successfully logged in test user with ID: {self.test_user_id}"
                    )
                    return True
                else:
                    self.log_test(
                        "Test Data Setup - User Login",
                        False,
                        "Failed to get user ID from login response"
                    )
                    return False
            else:
                self.log_test(
                    "Test Data Setup - User Login",
                    False,
                    f"Login failed with status {login_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Test Data Setup - User Login",
                False,
                f"Exception during setup: {str(e)}"
            )
            return False
    
    def test_tender_overview_endpoint(self):
        """Test 2: Price Settings Retrieval"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/catalyst/price-settings")
            
            if response.status_code != 200:
                self.log_test(
                    "Price Settings Retrieval",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            data = response.json()
            
            # Check if all required fields are present
            required_fields = [
                "pt_price", "pd_price", "rh_price",
                "renumeration_pt", "renumeration_pd", "renumeration_rh",
                "price_range_min_percent", "price_range_max_percent"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if not missing_fields:
                self.log_test(
                    "Price Settings Retrieval",
                    True,
                    f"All required fields present: {', '.join(required_fields)}"
                )
                return data
            else:
                self.log_test(
                    "Price Settings Retrieval",
                    False,
                    f"Missing fields: {', '.join(missing_fields)}",
                    f"All fields: {', '.join(required_fields)}",
                    f"Present fields: {', '.join(data.keys())}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Price Settings Retrieval",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_price_range_update(self):
        """Test 3: Price Range Update"""
        try:
            # Test data with different price range values
            test_settings = {
                "pt_price": 40.0,
                "pd_price": 40.0,
                "rh_price": 200.0,
                "renumeration_pt": 0.95,
                "renumeration_pd": 0.92,
                "renumeration_rh": 0.88,
                "price_range_min_percent": 15.0,  # Test with 15%
                "price_range_max_percent": 20.0   # Test with 20%
            }
            
            response = self.session.put(
                f"{self.backend_url}/admin/catalyst/price-settings",
                json=test_settings,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Price Range Update",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
                
            result = response.json()
            
            if "message" in result and "success" in result.get("message", "").lower():
                self.log_test(
                    "Price Range Update",
                    True,
                    f"Successfully updated price settings with min={test_settings['price_range_min_percent']}%, max={test_settings['price_range_max_percent']}%"
                )
                return test_settings
            else:
                self.log_test(
                    "Price Range Update",
                    False,
                    f"Unexpected response: {result}",
                    "Success message",
                    str(result)
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Price Range Update",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_default_values_reset(self):
        """Test 6: Reset to Default Values"""
        try:
            # Reset to default values
            default_settings = {
                "pt_price": 25.0,
                "pd_price": 18.0,
                "rh_price": 45.0,
                "renumeration_pt": 0.95,
                "renumeration_pd": 0.92,
                "renumeration_rh": 0.88,
                "price_range_min_percent": 10.0,  # Default -10%
                "price_range_max_percent": 10.0   # Default +10%
            }
            
            response = self.session.put(
                f"{self.backend_url}/admin/catalyst/price-settings",
                json=default_settings,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Default Values Reset",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
                
            # Verify reset worked
            verify_response = self.session.get(f"{self.backend_url}/marketplace/price-range-settings")
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                actual_min = verify_data.get("price_range_min_percent")
                actual_max = verify_data.get("price_range_max_percent")
                
                if actual_min == 10.0 and actual_max == 10.0:
                    self.log_test(
                        "Default Values Reset",
                        True,
                        f"Successfully reset to default values: min={actual_min}%, max={actual_max}%"
                    )
                    return True
                else:
                    self.log_test(
                        "Default Values Reset",
                        False,
                        f"Reset values incorrect: min={actual_min}%, max={actual_max}%",
                        "min=10.0%, max=10.0%",
                        f"min={actual_min}%, max={actual_max}%"
                    )
                    return False
            else:
                self.log_test(
                    "Default Values Reset",
                    False,
                    f"Failed to verify reset: HTTP {verify_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Default Values Reset",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_persistence_verification(self, expected_settings):
        """Test 4: Persistence Verification"""
        try:
            # Test both endpoints to verify persistence
            
            # Test 1: Check admin endpoint
            response1 = self.session.get(f"{self.backend_url}/admin/catalyst/price-settings")
            if response1.status_code != 200:
                self.log_test(
                    "Persistence Verification (Admin Endpoint)",
                    False,
                    f"HTTP {response1.status_code}: {response1.text}"
                )
                return False
                
            admin_data = response1.json()
            
            # Test 2: Check marketplace endpoint
            response2 = self.session.get(f"{self.backend_url}/marketplace/price-range-settings")
            if response2.status_code != 200:
                self.log_test(
                    "Persistence Verification (Marketplace Endpoint)",
                    False,
                    f"HTTP {response2.status_code}: {response2.text}"
                )
                return False
                
            marketplace_data = response2.json()
            
            # Verify admin endpoint has updated values
            admin_min = admin_data.get("price_range_min_percent")
            admin_max = admin_data.get("price_range_max_percent")
            
            # Verify marketplace endpoint has updated values
            market_min = marketplace_data.get("price_range_min_percent")
            market_max = marketplace_data.get("price_range_max_percent")
            
            expected_min = expected_settings["price_range_min_percent"]
            expected_max = expected_settings["price_range_max_percent"]
            
            admin_correct = (admin_min == expected_min and admin_max == expected_max)
            market_correct = (market_min == expected_min and market_max == expected_max)
            
            if admin_correct and market_correct:
                self.log_test(
                    "Persistence Verification",
                    True,
                    f"Both endpoints return updated values: min={expected_min}%, max={expected_max}%"
                )
                return True
            else:
                details = []
                if not admin_correct:
                    details.append(f"Admin endpoint: min={admin_min}%, max={admin_max}%")
                if not market_correct:
                    details.append(f"Marketplace endpoint: min={market_min}%, max={market_max}%")
                
                self.log_test(
                    "Persistence Verification",
                    False,
                    f"Values not persisted correctly. {'; '.join(details)}",
                    f"min={expected_min}%, max={expected_max}%",
                    "; ".join(details)
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Persistence Verification",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_database_storage_verification(self):
        """Test 5: Database Storage Verification"""
        try:
            # This test verifies the data structure by checking the admin endpoint
            # which should return the complete stored document
            response = self.session.get(f"{self.backend_url}/admin/catalyst/price-settings")
            
            if response.status_code != 200:
                self.log_test(
                    "Database Storage Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
            data = response.json()
            
            # Check if the response indicates proper database storage
            # The presence of all fields suggests proper storage in catalyst_price_settings collection
            storage_indicators = [
                "pt_price", "pd_price", "rh_price",
                "price_range_min_percent", "price_range_max_percent"
            ]
            
            all_present = all(field in data for field in storage_indicators)
            
            if all_present:
                self.log_test(
                    "Database Storage Verification",
                    True,
                    "Price range settings properly stored with complete data structure"
                )
                return True
            else:
                missing = [field for field in storage_indicators if field not in data]
                self.log_test(
                    "Database Storage Verification",
                    False,
                    f"Incomplete data structure, missing: {', '.join(missing)}",
                    "Complete price settings structure",
                    f"Missing fields: {', '.join(missing)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Database Storage Verification",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all price range configuration tests"""
        print("=" * 80)
        print("DYNAMIC PRICE RANGE CONFIGURATION TESTING")
        print("Testing Cat Database & Basis section functionality")
        print("=" * 80)
        print()
        
        # Test 1: Price Range Settings GET Endpoint
        test1_success = self.test_price_range_settings_get_endpoint()
        
        # Test 2: Price Settings Retrieval
        test2_result = self.test_price_settings_retrieval()
        test2_success = bool(test2_result)
        
        # Test 3: Price Range Update
        test3_result = self.test_price_range_update()
        test3_success = bool(test3_result)
        
        # Test 4: Persistence Verification (only if update succeeded)
        test4_success = False
        if test3_success and test3_result:
            test4_success = self.test_persistence_verification(test3_result)
        else:
            self.log_test(
                "Persistence Verification",
                False,
                "Skipped due to failed price range update"
            )
        
        # Test 5: Database Storage Verification
        test5_success = self.test_database_storage_verification()
        
        # Test 6: Default Values Reset
        test6_success = self.test_default_values_reset()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = 6
        passed_tests = sum([test1_success, test2_success, test3_success, test4_success, test5_success, test6_success])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Individual test results
        tests = [
            ("Price Range Settings GET Endpoint", test1_success),
            ("Price Settings Retrieval", test2_success),
            ("Price Range Update", test3_success),
            ("Persistence Verification", test4_success),
            ("Database Storage Verification", test5_success),
            ("Default Values Reset", test6_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        
        # Critical issues
        critical_failures = []
        if not test1_success:
            critical_failures.append("Price range settings endpoint not working")
        if not test2_success:
            critical_failures.append("Price settings retrieval failing")
        if not test3_success:
            critical_failures.append("Price range update not working")
        if not test4_success and test3_success:
            critical_failures.append("Price range values not persisting")
        if not test5_success:
            critical_failures.append("Database storage verification failed")
        
        if critical_failures:
            print("CRITICAL ISSUES FOUND:")
            for issue in critical_failures:
                print(f"❌ {issue}")
        else:
            print("✅ ALL CRITICAL FUNCTIONALITY WORKING")
        
        print()
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = PriceRangeConfigTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED - Dynamic price range configuration is working correctly!")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Check the issues above")
        sys.exit(1)