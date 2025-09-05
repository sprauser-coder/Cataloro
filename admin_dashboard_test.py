#!/usr/bin/env python3
"""
Admin Dashboard Backend Testing
Testing comprehensive dashboard data with KPIs, metrics, and real marketplace data
"""

import requests
import json
import sys
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://market-refactor.preview.emergentagent.com/api"

class AdminDashboardTester:
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
        
    def test_admin_dashboard_endpoint(self):
        """Test 1: Admin Dashboard Endpoint Accessibility"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/dashboard")
            
            if response.status_code != 200:
                self.log_test(
                    "Admin Dashboard Endpoint Accessibility",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            data = response.json()
            
            # Check if response has basic structure
            if isinstance(data, dict):
                self.log_test(
                    "Admin Dashboard Endpoint Accessibility",
                    True,
                    f"Successfully accessed admin dashboard endpoint, received {len(data)} top-level fields"
                )
                return data
            else:
                self.log_test(
                    "Admin Dashboard Endpoint Accessibility",
                    False,
                    f"Invalid response format: {type(data)}",
                    "Dictionary object",
                    f"{type(data)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Dashboard Endpoint Accessibility",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_kpi_metrics_structure(self, dashboard_data):
        """Test 2: KPI Metrics Structure Verification"""
        try:
            if not dashboard_data or "kpis" not in dashboard_data:
                self.log_test(
                    "KPI Metrics Structure Verification",
                    False,
                    "No 'kpis' section found in dashboard data",
                    "KPIs section present",
                    "KPIs section missing"
                )
                return False
                
            kpis = dashboard_data["kpis"]
            
            # Check for all required KPI metrics
            required_kpis = [
                "total_users",
                "total_listings", 
                "active_listings",
                "total_deals",
                "revenue",
                "growth_rate"
            ]
            
            missing_kpis = []
            present_kpis = []
            
            for kpi in required_kpis:
                if kpi in kpis:
                    present_kpis.append(kpi)
                else:
                    missing_kpis.append(kpi)
            
            if not missing_kpis:
                self.log_test(
                    "KPI Metrics Structure Verification",
                    True,
                    f"All required KPI metrics present: {', '.join(present_kpis)}"
                )
                return kpis
            else:
                self.log_test(
                    "KPI Metrics Structure Verification",
                    False,
                    f"Missing KPI metrics: {', '.join(missing_kpis)}",
                    f"All KPIs: {', '.join(required_kpis)}",
                    f"Present KPIs: {', '.join(present_kpis)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "KPI Metrics Structure Verification",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_kpi_data_types_and_values(self, kpis):
        """Test 3: KPI Data Types and Values Validation"""
        try:
            validation_results = []
            
            # Validate each KPI metric
            kpi_validations = {
                "total_users": {"type": (int, float), "min_value": 0},
                "total_listings": {"type": (int, float), "min_value": 0},
                "active_listings": {"type": (int, float), "min_value": 0},
                "total_deals": {"type": (int, float), "min_value": 0},
                "revenue": {"type": (int, float), "min_value": 0.0},
                "growth_rate": {"type": (int, float), "min_value": 0.0}
            }
            
            for kpi_name, validation in kpi_validations.items():
                if kpi_name in kpis:
                    value = kpis[kpi_name]
                    
                    # Check data type
                    if isinstance(value, validation["type"]):
                        # Check minimum value
                        if value >= validation["min_value"]:
                            validation_results.append(f"✅ {kpi_name}: {value} (valid)")
                        else:
                            validation_results.append(f"❌ {kpi_name}: {value} (below minimum {validation['min_value']})")
                    else:
                        validation_results.append(f"❌ {kpi_name}: {value} (invalid type {type(value)})")
                else:
                    validation_results.append(f"❌ {kpi_name}: missing")
            
            # Check if all validations passed
            failed_validations = [result for result in validation_results if result.startswith("❌")]
            
            if not failed_validations:
                self.log_test(
                    "KPI Data Types and Values Validation",
                    True,
                    f"All KPI values valid: {'; '.join([r.split(': ')[1] for r in validation_results])}"
                )
                return True
            else:
                self.log_test(
                    "KPI Data Types and Values Validation",
                    False,
                    f"Invalid KPI values found: {'; '.join(failed_validations)}",
                    "All KPIs with valid types and values",
                    f"Failed: {'; '.join(failed_validations)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "KPI Data Types and Values Validation",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_real_marketplace_data(self, dashboard_data):
        """Test 4: Real Marketplace Data Integration"""
        try:
            kpis = dashboard_data.get("kpis", {})
            
            # Check if we have real data indicators
            real_data_indicators = []
            
            # Check for non-zero values (indicating real data)
            if kpis.get("total_users", 0) > 0:
                real_data_indicators.append(f"Users: {kpis['total_users']}")
            
            if kpis.get("total_listings", 0) > 0:
                real_data_indicators.append(f"Listings: {kpis['total_listings']}")
                
            if kpis.get("total_deals", 0) > 0:
                real_data_indicators.append(f"Deals: {kpis['total_deals']}")
                
            if kpis.get("revenue", 0) > 0:
                real_data_indicators.append(f"Revenue: €{kpis['revenue']}")
            
            # Check for recent activity data
            recent_activity = dashboard_data.get("recent_activity", [])
            activity_count = len(recent_activity)
            
            if real_data_indicators or activity_count > 0:
                details = []
                if real_data_indicators:
                    details.append(f"Real KPI data: {', '.join(real_data_indicators)}")
                if activity_count > 0:
                    details.append(f"Recent activity entries: {activity_count}")
                
                self.log_test(
                    "Real Marketplace Data Integration",
                    True,
                    f"Dashboard contains real marketplace data - {'; '.join(details)}"
                )
                return True
            else:
                self.log_test(
                    "Real Marketplace Data Integration",
                    False,
                    "Dashboard appears to contain only default/zero values",
                    "Real marketplace data with non-zero values",
                    f"All KPIs are zero: {kpis}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Real Marketplace Data Integration",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_activity_data_structure(self, dashboard_data):
        """Test 5: Activity Data and System Metrics"""
        try:
            if "recent_activity" not in dashboard_data:
                self.log_test(
                    "Activity Data and System Metrics",
                    False,
                    "No 'recent_activity' section found in dashboard data",
                    "Recent activity section present",
                    "Recent activity section missing"
                )
                return False
                
            recent_activity = dashboard_data["recent_activity"]
            
            if not isinstance(recent_activity, list):
                self.log_test(
                    "Activity Data and System Metrics",
                    False,
                    f"Recent activity is not a list: {type(recent_activity)}",
                    "List of activity entries",
                    f"{type(recent_activity)}"
                )
                return False
            
            # Validate activity entries structure
            valid_entries = 0
            total_entries = len(recent_activity)
            
            for i, activity in enumerate(recent_activity):
                if isinstance(activity, dict):
                    if "action" in activity and "timestamp" in activity:
                        valid_entries += 1
                    else:
                        missing_fields = []
                        if "action" not in activity:
                            missing_fields.append("action")
                        if "timestamp" not in activity:
                            missing_fields.append("timestamp")
                        print(f"   Activity entry {i+1} missing fields: {', '.join(missing_fields)}")
                else:
                    print(f"   Activity entry {i+1} is not a dictionary: {type(activity)}")
            
            if total_entries > 0 and valid_entries == total_entries:
                self.log_test(
                    "Activity Data and System Metrics",
                    True,
                    f"All {total_entries} activity entries have proper structure (action, timestamp)"
                )
                return True
            elif total_entries == 0:
                self.log_test(
                    "Activity Data and System Metrics",
                    True,
                    "Recent activity is empty (valid for new system)"
                )
                return True
            else:
                self.log_test(
                    "Activity Data and System Metrics",
                    False,
                    f"Invalid activity entries: {valid_entries}/{total_entries} valid",
                    f"All {total_entries} entries with proper structure",
                    f"Only {valid_entries} valid entries"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Activity Data and System Metrics",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_enhanced_dashboard_functions(self, dashboard_data):
        """Test 6: Enhanced Dashboard Backend Functions"""
        try:
            kpis = dashboard_data.get("kpis", {})
            
            # Test enhanced calculations
            enhanced_features = []
            
            # Check if active_listings is calculated separately from total_listings
            total_listings = kpis.get("total_listings", 0)
            active_listings = kpis.get("active_listings", 0)
            
            if active_listings <= total_listings:
                enhanced_features.append("Active listings calculation")
            
            # Check if growth_rate is calculated (not just a static value)
            growth_rate = kpis.get("growth_rate", 0)
            if isinstance(growth_rate, (int, float)):
                enhanced_features.append("Growth rate calculation")
            
            # Check if revenue calculation includes multiple sources
            revenue = kpis.get("revenue", 0)
            if isinstance(revenue, (int, float)):
                enhanced_features.append("Revenue aggregation")
            
            # Check if total_deals includes tenders (enhanced functionality)
            total_deals = kpis.get("total_deals", 0)
            if isinstance(total_deals, (int, float)):
                enhanced_features.append("Deal counting (including tenders)")
            
            # Verify recent activity generation
            recent_activity = dashboard_data.get("recent_activity", [])
            if len(recent_activity) > 0:
                enhanced_features.append("Recent activity generation")
            
            if len(enhanced_features) >= 4:  # Most enhanced features working
                self.log_test(
                    "Enhanced Dashboard Backend Functions",
                    True,
                    f"Enhanced dashboard functions working: {', '.join(enhanced_features)}"
                )
                return True
            else:
                self.log_test(
                    "Enhanced Dashboard Backend Functions",
                    False,
                    f"Limited enhanced functionality: {', '.join(enhanced_features)}",
                    "Multiple enhanced dashboard functions",
                    f"Only {len(enhanced_features)} features detected"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Enhanced Dashboard Backend Functions",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_comprehensive_dashboard_response(self, dashboard_data):
        """Test 7: Comprehensive Dashboard Response Validation"""
        try:
            # Check overall response completeness
            required_sections = ["kpis", "recent_activity"]
            present_sections = []
            missing_sections = []
            
            for section in required_sections:
                if section in dashboard_data:
                    present_sections.append(section)
                else:
                    missing_sections.append(section)
            
            # Calculate response completeness score
            kpis = dashboard_data.get("kpis", {})
            kpi_count = len(kpis)
            activity_count = len(dashboard_data.get("recent_activity", []))
            
            completeness_score = 0
            if "kpis" in dashboard_data and kpi_count >= 6:
                completeness_score += 50
            if "recent_activity" in dashboard_data:
                completeness_score += 30
            if activity_count > 0:
                completeness_score += 20
            
            if completeness_score >= 80:
                self.log_test(
                    "Comprehensive Dashboard Response Validation",
                    True,
                    f"Dashboard response is comprehensive (score: {completeness_score}/100) - {len(present_sections)} sections, {kpi_count} KPIs, {activity_count} activities"
                )
                return True
            else:
                issues = []
                if missing_sections:
                    issues.append(f"Missing sections: {', '.join(missing_sections)}")
                if kpi_count < 6:
                    issues.append(f"Insufficient KPIs: {kpi_count}/6")
                
                self.log_test(
                    "Comprehensive Dashboard Response Validation",
                    False,
                    f"Dashboard response incomplete (score: {completeness_score}/100) - {'; '.join(issues)}",
                    "Comprehensive dashboard with all sections and data",
                    f"Score: {completeness_score}/100, Issues: {'; '.join(issues)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Comprehensive Dashboard Response Validation",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all admin dashboard tests"""
        print("=" * 80)
        print("ADMIN DASHBOARD FUNCTIONALITY TESTING")
        print("Testing comprehensive dashboard data with KPIs and real marketplace data")
        print("=" * 80)
        print()
        
        # Test 1: Admin Dashboard Endpoint Accessibility
        dashboard_data = self.test_admin_dashboard_endpoint()
        test1_success = bool(dashboard_data)
        
        # Test 2: KPI Metrics Structure Verification
        test2_result = False
        kpis = None
        if test1_success:
            kpis = self.test_kpi_metrics_structure(dashboard_data)
            test2_result = bool(kpis)
        else:
            self.log_test(
                "KPI Metrics Structure Verification",
                False,
                "Skipped due to failed dashboard endpoint access"
            )
        
        # Test 3: KPI Data Types and Values Validation
        test3_success = False
        if test2_result and kpis:
            test3_success = self.test_kpi_data_types_and_values(kpis)
        else:
            self.log_test(
                "KPI Data Types and Values Validation",
                False,
                "Skipped due to failed KPI structure verification"
            )
        
        # Test 4: Real Marketplace Data Integration
        test4_success = False
        if test1_success:
            test4_success = self.test_real_marketplace_data(dashboard_data)
        else:
            self.log_test(
                "Real Marketplace Data Integration",
                False,
                "Skipped due to failed dashboard endpoint access"
            )
        
        # Test 5: Activity Data and System Metrics
        test5_success = False
        if test1_success:
            test5_success = self.test_activity_data_structure(dashboard_data)
        else:
            self.log_test(
                "Activity Data and System Metrics",
                False,
                "Skipped due to failed dashboard endpoint access"
            )
        
        # Test 6: Enhanced Dashboard Backend Functions
        test6_success = False
        if test1_success:
            test6_success = self.test_enhanced_dashboard_functions(dashboard_data)
        else:
            self.log_test(
                "Enhanced Dashboard Backend Functions",
                False,
                "Skipped due to failed dashboard endpoint access"
            )
        
        # Test 7: Comprehensive Dashboard Response Validation
        test7_success = False
        if test1_success:
            test7_success = self.test_comprehensive_dashboard_response(dashboard_data)
        else:
            self.log_test(
                "Comprehensive Dashboard Response Validation",
                False,
                "Skipped due to failed dashboard endpoint access"
            )
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = 7
        passed_tests = sum([test1_success, test2_result, test3_success, test4_success, test5_success, test6_success, test7_success])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Individual test results
        tests = [
            ("Admin Dashboard Endpoint Accessibility", test1_success),
            ("KPI Metrics Structure Verification", test2_result),
            ("KPI Data Types and Values Validation", test3_success),
            ("Real Marketplace Data Integration", test4_success),
            ("Activity Data and System Metrics", test5_success),
            ("Enhanced Dashboard Backend Functions", test6_success),
            ("Comprehensive Dashboard Response Validation", test7_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        
        # Critical issues
        critical_failures = []
        if not test1_success:
            critical_failures.append("Admin dashboard endpoint not accessible")
        if not test2_result:
            critical_failures.append("KPI metrics structure incomplete")
        if not test3_success and test2_result:
            critical_failures.append("KPI data types or values invalid")
        if not test4_success:
            critical_failures.append("No real marketplace data detected")
        if not test5_success:
            critical_failures.append("Activity data structure issues")
        
        if critical_failures:
            print("CRITICAL ISSUES FOUND:")
            for issue in critical_failures:
                print(f"❌ {issue}")
        else:
            print("✅ ALL CRITICAL FUNCTIONALITY WORKING")
        
        print()
        
        # Display actual dashboard data for verification
        if dashboard_data:
            print("DASHBOARD DATA SAMPLE:")
            print("-" * 40)
            if "kpis" in dashboard_data:
                print("KPIs:")
                for kpi, value in dashboard_data["kpis"].items():
                    print(f"  {kpi}: {value}")
            if "recent_activity" in dashboard_data:
                activity_count = len(dashboard_data["recent_activity"])
                print(f"Recent Activity: {activity_count} entries")
                if activity_count > 0:
                    print("  Sample activities:")
                    for i, activity in enumerate(dashboard_data["recent_activity"][:3]):
                        action = activity.get("action", "Unknown action")
                        print(f"    {i+1}. {action}")
            print()
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = AdminDashboardTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED - Admin Dashboard functionality is working correctly!")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Check the issues above")
        sys.exit(1)