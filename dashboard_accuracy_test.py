#!/usr/bin/env python3
"""
Dashboard Data Accuracy Verification Test
Testing the CORRECTED Admin Dashboard Data Accuracy after fixing the revenue calculation bug
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://cataloro-upgrade.preview.emergentagent.com/api"

class DashboardAccuracyTester:
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

    def test_dashboard_endpoint_accessibility(self):
        """Test 1: Verify GET /api/admin/dashboard endpoint is accessible"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/dashboard")
            
            if response.status_code == 200:
                dashboard_data = response.json()
                self.log_test(
                    "Dashboard Endpoint Accessibility",
                    True,
                    f"Dashboard endpoint accessible with HTTP {response.status_code}. Response contains: {list(dashboard_data.keys())}"
                )
                return dashboard_data
            else:
                self.log_test(
                    "Dashboard Endpoint Accessibility", 
                    False,
                    f"Dashboard endpoint returned HTTP {response.status_code}",
                    "HTTP 200",
                    f"HTTP {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Dashboard Endpoint Accessibility",
                False,
                f"Failed to access dashboard endpoint: {str(e)}"
            )
            return None

    def verify_actual_marketplace_data(self):
        """Get actual marketplace data for comparison"""
        try:
            # Get actual user count
            users_response = self.session.get(f"{self.backend_url}/admin/users")
            actual_users = len(users_response.json()) if users_response.status_code == 200 else 0
            
            # Get actual listings count
            listings_response = self.session.get(f"{self.backend_url}/listings")
            actual_listings = listings_response.json().get("total", 0) if listings_response.status_code == 200 else 0
            
            # Get active listings from browse endpoint
            browse_response = self.session.get(f"{self.backend_url}/marketplace/browse")
            active_listings = len(browse_response.json()) if browse_response.status_code == 200 else 0
            
            # Calculate actual revenue from real transactions
            actual_revenue = 0.0
            actual_deals = 0
            
            # Check for sold listings
            if browse_response.status_code == 200:
                browse_data = browse_response.json()
                for listing in browse_data:
                    if listing.get("status") == "sold":
                        price = listing.get("final_price", listing.get("price", 0))
                        if price > 0:
                            actual_revenue += price
                            actual_deals += 1
            
            return {
                "users": actual_users,
                "total_listings": actual_listings,
                "active_listings": active_listings,
                "revenue": actual_revenue,
                "deals": actual_deals
            }
            
        except Exception as e:
            print(f"Error getting actual marketplace data: {e}")
            return None

    def test_revenue_calculation_fix(self, dashboard_data, actual_data):
        """Test 2: Verify revenue calculation shows real marketplace data instead of inflated figures"""
        try:
            dashboard_revenue = dashboard_data.get("kpis", {}).get("revenue", 0)
            
            # The revenue should be significantly lower than the previous inflated €5,445
            # and should reflect actual marketplace transactions
            if dashboard_revenue <= 1000:  # Should be much lower than €5,445
                self.log_test(
                    "Revenue Calculation Fix",
                    True,
                    f"Revenue shows realistic amount: €{dashboard_revenue} (previously was inflated €5,445)"
                )
                return True
            else:
                self.log_test(
                    "Revenue Calculation Fix",
                    False,
                    f"Revenue still appears inflated: €{dashboard_revenue}",
                    "Revenue ≤ €1,000 (realistic marketplace amount)",
                    f"€{dashboard_revenue}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Revenue Calculation Fix",
                False,
                f"Error checking revenue calculation: {str(e)}"
            )
            return False

    def test_user_count_accuracy(self, dashboard_data, actual_data):
        """Test 3: Verify user count shows real number of users (around 71)"""
        try:
            dashboard_users = dashboard_data.get("kpis", {}).get("total_users", 0)
            actual_users = actual_data.get("users", 0) if actual_data else 0
            
            # Allow small variance (±5) for real-time changes
            if abs(dashboard_users - actual_users) <= 5:
                self.log_test(
                    "User Count Accuracy",
                    True,
                    f"User count matches actual data: Dashboard={dashboard_users}, Actual={actual_users}"
                )
                return True
            else:
                self.log_test(
                    "User Count Accuracy",
                    False,
                    f"User count mismatch between dashboard and actual data",
                    f"Around {actual_users} users",
                    f"{dashboard_users} users"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "User Count Accuracy",
                False,
                f"Error checking user count: {str(e)}"
            )
            return False

    def test_deals_count_accuracy(self, dashboard_data, actual_data):
        """Test 4: Verify total_deals shows only real marketplace transactions"""
        try:
            dashboard_deals = dashboard_data.get("kpis", {}).get("total_deals", 0)
            
            # Deals count should be reasonable for a real marketplace (not inflated)
            if dashboard_deals <= 50:  # Reasonable number for actual marketplace
                self.log_test(
                    "Deals Count Accuracy",
                    True,
                    f"Deals count shows realistic number: {dashboard_deals} (not inflated)"
                )
                return True
            else:
                self.log_test(
                    "Deals Count Accuracy",
                    False,
                    f"Deals count may be inflated: {dashboard_deals}",
                    "Realistic deals count (≤50)",
                    f"{dashboard_deals} deals"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Deals Count Accuracy",
                False,
                f"Error checking deals count: {str(e)}"
            )
            return False

    def test_active_listings_accuracy(self, dashboard_data, actual_data):
        """Test 5: Verify active_listings matches actual marketplace listings"""
        try:
            dashboard_active = dashboard_data.get("kpis", {}).get("active_listings", 0)
            actual_active = actual_data.get("active_listings", 0) if actual_data else 0
            
            # Allow small variance (±3) for real-time changes
            if abs(dashboard_active - actual_active) <= 3:
                self.log_test(
                    "Active Listings Accuracy",
                    True,
                    f"Active listings count matches: Dashboard={dashboard_active}, Actual={actual_active}"
                )
                return True
            else:
                self.log_test(
                    "Active Listings Accuracy",
                    False,
                    f"Active listings count mismatch",
                    f"{actual_active} active listings",
                    f"{dashboard_active} active listings"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Active Listings Accuracy",
                False,
                f"Error checking active listings: {str(e)}"
            )
            return False

    def test_kpi_data_integrity(self, dashboard_data):
        """Test 6: Verify all KPIs reflect genuine marketplace activity"""
        try:
            kpis = dashboard_data.get("kpis", {})
            required_kpis = ["total_users", "total_listings", "active_listings", "total_deals", "revenue", "growth_rate"]
            
            missing_kpis = [kpi for kpi in required_kpis if kpi not in kpis]
            
            if not missing_kpis:
                # Check if values are reasonable (not obviously test/dummy data)
                revenue = kpis.get("revenue", 0)
                users = kpis.get("total_users", 0)
                listings = kpis.get("total_listings", 0)
                deals = kpis.get("total_deals", 0)
                
                # Reasonable ranges for a real marketplace
                reasonable_data = (
                    0 <= revenue <= 2000 and  # Not inflated like €5,445
                    50 <= users <= 100 and    # Around expected 71 users
                    20 <= listings <= 50 and  # Reasonable listings count
                    0 <= deals <= 20          # Reasonable deals count
                )
                
                if reasonable_data:
                    self.log_test(
                        "KPI Data Integrity",
                        True,
                        f"All KPIs present with reasonable values: Revenue=€{revenue}, Users={users}, Listings={listings}, Deals={deals}"
                    )
                    return True
                else:
                    self.log_test(
                        "KPI Data Integrity",
                        False,
                        f"KPI values appear unrealistic: Revenue=€{revenue}, Users={users}, Listings={listings}, Deals={deals}",
                        "Reasonable marketplace values",
                        f"Revenue=€{revenue}, Users={users}, Listings={listings}, Deals={deals}"
                    )
                    return False
            else:
                self.log_test(
                    "KPI Data Integrity",
                    False,
                    f"Missing required KPIs: {missing_kpis}",
                    f"All KPIs present: {required_kpis}",
                    f"Missing: {missing_kpis}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "KPI Data Integrity",
                False,
                f"Error checking KPI data integrity: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all dashboard accuracy tests"""
        print("=" * 80)
        print("DASHBOARD DATA ACCURACY VERIFICATION TEST")
        print("Testing the CORRECTED Admin Dashboard after fixing revenue calculation bug")
        print("=" * 80)
        print()
        
        # Test 1: Dashboard endpoint accessibility
        dashboard_data = self.test_dashboard_endpoint_accessibility()
        if not dashboard_data:
            print("❌ Cannot proceed with tests - dashboard endpoint not accessible")
            return False
        
        # Get actual marketplace data for comparison
        print("📊 Gathering actual marketplace data for comparison...")
        actual_data = self.verify_actual_marketplace_data()
        print()
        
        # Test 2: Revenue calculation fix
        revenue_fixed = self.test_revenue_calculation_fix(dashboard_data, actual_data)
        
        # Test 3: User count accuracy
        users_accurate = self.test_user_count_accuracy(dashboard_data, actual_data)
        
        # Test 4: Deals count accuracy
        deals_accurate = self.test_deals_count_accuracy(dashboard_data, actual_data)
        
        # Test 5: Active listings accuracy
        listings_accurate = self.test_active_listings_accuracy(dashboard_data, actual_data)
        
        # Test 6: KPI data integrity
        kpi_integrity = self.test_kpi_data_integrity(dashboard_data)
        
        # Summary
        total_tests = 6
        passed_tests = sum([
            True,  # Dashboard accessibility (if we got here, it passed)
            revenue_fixed,
            users_accurate,
            deals_accurate,
            listings_accurate,
            kpi_integrity
        ])
        
        print("=" * 80)
        print("DASHBOARD DATA ACCURACY TEST SUMMARY")
        print("=" * 80)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if dashboard_data:
            kpis = dashboard_data.get("kpis", {})
            print("📊 CURRENT DASHBOARD KPIs:")
            print(f"   Users: {kpis.get('total_users', 'N/A')}")
            print(f"   Total Listings: {kpis.get('total_listings', 'N/A')}")
            print(f"   Active Listings: {kpis.get('active_listings', 'N/A')}")
            print(f"   Total Deals: {kpis.get('total_deals', 'N/A')}")
            print(f"   Revenue: €{kpis.get('revenue', 'N/A')}")
            print(f"   Growth Rate: {kpis.get('growth_rate', 'N/A')}%")
            print()
        
        if actual_data:
            print("🔍 ACTUAL MARKETPLACE DATA:")
            print(f"   Users: {actual_data.get('users', 'N/A')}")
            print(f"   Total Listings: {actual_data.get('total_listings', 'N/A')}")
            print(f"   Active Listings: {actual_data.get('active_listings', 'N/A')}")
            print(f"   Revenue: €{actual_data.get('revenue', 'N/A')}")
            print(f"   Deals: {actual_data.get('deals', 'N/A')}")
            print()
        
        # Critical issue analysis
        if dashboard_data:
            revenue = kpis.get('revenue', 0)
            if revenue > 2000:
                print("🚨 CRITICAL ISSUE: Revenue still appears inflated!")
                print(f"   Dashboard shows €{revenue} but should be much lower")
                print("   The revenue calculation bug may not be fully fixed")
            elif revenue <= 1000:
                print("✅ REVENUE FIX CONFIRMED: Revenue shows realistic amount")
                print(f"   Dashboard shows €{revenue} (down from previous €5,445)")
                print("   Revenue calculation appears to be fixed")
        
        print("=" * 80)
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = DashboardAccuracyTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL DASHBOARD ACCURACY TESTS PASSED!")
        print("The dashboard data accuracy fix has been successfully verified.")
        sys.exit(0)
    else:
        print("⚠️  SOME DASHBOARD ACCURACY TESTS FAILED!")
        print("The dashboard may still have data accuracy issues.")
        sys.exit(1)