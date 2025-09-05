#!/usr/bin/env python3
"""
Dashboard Data Debug Test
Testing GET /api/admin/dashboard endpoint to identify field name mismatches
and data accuracy issues for revenue, listings, conversion rate fields
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://cataloro-upgrade.preview.emergentagent.com/api"

class DashboardDebugTester:
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
        
    def test_dashboard_endpoint_structure(self):
        """Test 1: GET /api/admin/dashboard endpoint structure analysis"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/dashboard")
            
            if response.status_code != 200:
                self.log_test(
                    "Dashboard Endpoint Access",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return None
                
            data = response.json()
            
            # Log the complete structure for analysis
            print("COMPLETE DASHBOARD RESPONSE STRUCTURE:")
            print("=" * 60)
            print(json.dumps(data, indent=2, default=str))
            print("=" * 60)
            print()
            
            self.log_test(
                "Dashboard Endpoint Access",
                True,
                f"Successfully retrieved dashboard data with {len(data)} top-level fields"
            )
            
            return data
                
        except Exception as e:
            self.log_test(
                "Dashboard Endpoint Access",
                False,
                f"Exception: {str(e)}"
            )
            return None
    
    def analyze_kpi_fields(self, dashboard_data):
        """Test 2: Analyze KPI field names and values"""
        try:
            if not dashboard_data or "kpis" not in dashboard_data:
                self.log_test(
                    "KPI Fields Analysis",
                    False,
                    "No 'kpis' section found in dashboard response"
                )
                return None
                
            kpis = dashboard_data["kpis"]
            
            print("KPI FIELDS ANALYSIS:")
            print("=" * 40)
            
            # Check each KPI field
            kpi_analysis = {}
            for field_name, value in kpis.items():
                print(f"Field: '{field_name}' = {value} (type: {type(value).__name__})")
                kpi_analysis[field_name] = {
                    "value": value,
                    "type": type(value).__name__
                }
            
            print("=" * 40)
            print()
            
            # Check for expected fields
            expected_fields = [
                "total_users", "users", "user_count",
                "total_listings", "listings", "listing_count", "active_listings", "active_products",
                "revenue", "total_revenue", "total_sales",
                "total_deals", "deals", "conversion_rate", "growth_rate"
            ]
            
            found_fields = list(kpis.keys())
            
            print("FIELD NAME MAPPING ANALYSIS:")
            print("=" * 40)
            print("Fields found in response:")
            for field in found_fields:
                print(f"  - {field}")
            
            print("\nExpected field variations:")
            for field in expected_fields:
                if field in found_fields:
                    print(f"  ✅ {field} (FOUND)")
                else:
                    print(f"  ❌ {field} (NOT FOUND)")
            
            print("=" * 40)
            print()
            
            self.log_test(
                "KPI Fields Analysis",
                True,
                f"Found {len(found_fields)} KPI fields: {', '.join(found_fields)}"
            )
            
            return kpi_analysis
                
        except Exception as e:
            self.log_test(
                "KPI Fields Analysis",
                False,
                f"Exception: {str(e)}"
            )
            return None
    
    def test_revenue_field_accuracy(self, kpi_data):
        """Test 3: Revenue field accuracy and calculation verification"""
        try:
            if not kpi_data:
                self.log_test(
                    "Revenue Field Accuracy",
                    False,
                    "No KPI data available for revenue analysis"
                )
                return None
            
            # Find revenue field (could be 'revenue', 'total_revenue', etc.)
            revenue_field = None
            revenue_value = None
            
            possible_revenue_fields = ["revenue", "total_revenue", "total_sales", "sales"]
            for field in possible_revenue_fields:
                if field in kpi_data:
                    revenue_field = field
                    revenue_value = kpi_data[field]["value"]
                    break
            
            if revenue_field is None:
                self.log_test(
                    "Revenue Field Accuracy",
                    False,
                    f"No revenue field found. Available fields: {list(kpi_data.keys())}"
                )
                return None
            
            print("REVENUE FIELD ANALYSIS:")
            print("=" * 40)
            print(f"Revenue field name: '{revenue_field}'")
            print(f"Revenue value: {revenue_value}")
            print(f"Revenue type: {type(revenue_value).__name__}")
            
            # Check if revenue seems realistic
            if isinstance(revenue_value, (int, float)):
                if revenue_value < 0:
                    print("⚠️  WARNING: Negative revenue value")
                elif revenue_value == 0:
                    print("ℹ️  INFO: Zero revenue (could be normal for new platform)")
                elif revenue_value > 100000:
                    print("⚠️  WARNING: Very high revenue value (possible inflation)")
                else:
                    print("✅ Revenue value appears reasonable")
            else:
                print("⚠️  WARNING: Revenue is not a number")
            
            print("=" * 40)
            print()
            
            self.log_test(
                "Revenue Field Accuracy",
                True,
                f"Revenue field '{revenue_field}' contains value: {revenue_value}"
            )
            
            return {
                "field_name": revenue_field,
                "value": revenue_value,
                "type": type(revenue_value).__name__
            }
                
        except Exception as e:
            self.log_test(
                "Revenue Field Accuracy",
                False,
                f"Exception: {str(e)}"
            )
            return None
    
    def test_listings_field_accuracy(self, kpi_data):
        """Test 4: Listings field accuracy and naming verification"""
        try:
            if not kpi_data:
                self.log_test(
                    "Listings Field Accuracy",
                    False,
                    "No KPI data available for listings analysis"
                )
                return None
            
            print("LISTINGS FIELDS ANALYSIS:")
            print("=" * 40)
            
            # Find all listing-related fields
            listing_fields = {}
            possible_listing_fields = [
                "total_listings", "listings", "listing_count",
                "active_listings", "active_products", "products"
            ]
            
            for field in possible_listing_fields:
                if field in kpi_data:
                    listing_fields[field] = kpi_data[field]["value"]
                    print(f"Found: '{field}' = {kpi_data[field]['value']}")
            
            if not listing_fields:
                print("❌ No listing fields found")
                self.log_test(
                    "Listings Field Accuracy",
                    False,
                    f"No listing fields found. Available fields: {list(kpi_data.keys())}"
                )
                return None
            else:
                print(f"✅ Found {len(listing_fields)} listing-related fields")
            
            print("=" * 40)
            print()
            
            self.log_test(
                "Listings Field Accuracy",
                True,
                f"Found listing fields: {', '.join(listing_fields.keys())}"
            )
            
            return listing_fields
                
        except Exception as e:
            self.log_test(
                "Listings Field Accuracy",
                False,
                f"Exception: {str(e)}"
            )
            return None
    
    def test_conversion_rate_field(self, kpi_data):
        """Test 5: Conversion rate field verification"""
        try:
            if not kpi_data:
                self.log_test(
                    "Conversion Rate Field",
                    False,
                    "No KPI data available for conversion rate analysis"
                )
                return None
            
            print("CONVERSION RATE ANALYSIS:")
            print("=" * 40)
            
            # Find conversion rate field
            conversion_fields = {}
            possible_conversion_fields = [
                "conversion_rate", "conversion", "success_rate", "deal_rate"
            ]
            
            for field in possible_conversion_fields:
                if field in kpi_data:
                    conversion_fields[field] = kpi_data[field]["value"]
                    print(f"Found: '{field}' = {kpi_data[field]['value']}")
            
            if not conversion_fields:
                print("❌ No conversion rate fields found")
                # Check if there's a growth_rate field instead
                if "growth_rate" in kpi_data:
                    print(f"Found 'growth_rate' instead: {kpi_data['growth_rate']['value']}")
                    conversion_fields["growth_rate"] = kpi_data["growth_rate"]["value"]
                else:
                    print("❌ No growth_rate field either")
            
            print("=" * 40)
            print()
            
            if conversion_fields:
                self.log_test(
                    "Conversion Rate Field",
                    True,
                    f"Found conversion-related fields: {', '.join(conversion_fields.keys())}"
                )
            else:
                self.log_test(
                    "Conversion Rate Field",
                    False,
                    "No conversion rate or growth rate fields found"
                )
            
            return conversion_fields
                
        except Exception as e:
            self.log_test(
                "Conversion Rate Field",
                False,
                f"Exception: {str(e)}"
            )
            return None
    
    def compare_with_browse_endpoint(self):
        """Test 6: Compare dashboard data with browse endpoint for consistency"""
        try:
            # Get browse data for comparison
            browse_response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if browse_response.status_code != 200:
                self.log_test(
                    "Browse Endpoint Comparison",
                    False,
                    f"Failed to access browse endpoint: HTTP {browse_response.status_code}"
                )
                return None
            
            browse_data = browse_response.json()
            browse_count = len(browse_data) if isinstance(browse_data, list) else 0
            
            print("BROWSE ENDPOINT COMPARISON:")
            print("=" * 40)
            print(f"Browse endpoint returns {browse_count} active listings")
            
            # Calculate total bid value from browse data
            total_bid_value = 0
            listings_with_bids = 0
            
            for listing in browse_data:
                if isinstance(listing, dict) and "bid_info" in listing:
                    bid_info = listing["bid_info"]
                    if bid_info.get("has_bids", False):
                        highest_bid = bid_info.get("highest_bid", 0)
                        if isinstance(highest_bid, (int, float)) and highest_bid > 0:
                            total_bid_value += highest_bid
                            listings_with_bids += 1
            
            print(f"Total bid value from browse: €{total_bid_value}")
            print(f"Listings with bids: {listings_with_bids}")
            print("=" * 40)
            print()
            
            self.log_test(
                "Browse Endpoint Comparison",
                True,
                f"Browse shows {browse_count} listings, €{total_bid_value} total bid value"
            )
            
            return {
                "active_listings_count": browse_count,
                "total_bid_value": total_bid_value,
                "listings_with_bids": listings_with_bids
            }
                
        except Exception as e:
            self.log_test(
                "Browse Endpoint Comparison",
                False,
                f"Exception: {str(e)}"
            )
            return None
    
    def identify_field_mismatches(self, dashboard_data, browse_data):
        """Test 7: Identify potential field name mismatches"""
        try:
            if not dashboard_data or not browse_data:
                self.log_test(
                    "Field Mismatch Analysis",
                    False,
                    "Missing dashboard or browse data for comparison"
                )
                return None
            
            print("FIELD MISMATCH ANALYSIS:")
            print("=" * 50)
            
            kpis = dashboard_data.get("kpis", {})
            
            # Compare active listings
            dashboard_active = None
            for field in ["active_listings", "active_products", "listings"]:
                if field in kpis:
                    dashboard_active = kpis[field]
                    print(f"Dashboard '{field}': {dashboard_active}")
                    break
            
            browse_active = browse_data["active_listings_count"]
            print(f"Browse endpoint active listings: {browse_active}")
            
            if dashboard_active is not None:
                if dashboard_active == browse_active:
                    print("✅ Active listings count matches")
                else:
                    print(f"❌ MISMATCH: Dashboard={dashboard_active}, Browse={browse_active}")
            
            # Compare revenue vs bid values
            dashboard_revenue = None
            for field in ["revenue", "total_revenue", "total_sales"]:
                if field in kpis:
                    dashboard_revenue = kpis[field]
                    print(f"Dashboard '{field}': €{dashboard_revenue}")
                    break
            
            browse_bid_value = browse_data["total_bid_value"]
            print(f"Browse total bid value: €{browse_bid_value}")
            
            if dashboard_revenue is not None:
                if abs(dashboard_revenue - browse_bid_value) < 100:  # Allow small differences
                    print("✅ Revenue approximately matches bid values")
                else:
                    print(f"❌ POTENTIAL ISSUE: Large difference between revenue and bid values")
                    print(f"   Difference: €{abs(dashboard_revenue - browse_bid_value)}")
            
            print("=" * 50)
            print()
            
            self.log_test(
                "Field Mismatch Analysis",
                True,
                "Completed field mismatch analysis"
            )
            
            return True
                
        except Exception as e:
            self.log_test(
                "Field Mismatch Analysis",
                False,
                f"Exception: {str(e)}"
            )
            return None
    
    def run_all_tests(self):
        """Run all dashboard debug tests"""
        print("=" * 80)
        print("DASHBOARD DATA DEBUG TESTING")
        print("Analyzing GET /api/admin/dashboard field names and data accuracy")
        print("=" * 80)
        print()
        
        # Test 1: Dashboard endpoint structure
        dashboard_data = self.test_dashboard_endpoint_structure()
        
        # Test 2: KPI fields analysis
        kpi_data = None
        if dashboard_data:
            kpi_data = self.analyze_kpi_fields(dashboard_data)
        
        # Test 3: Revenue field accuracy
        revenue_info = None
        if kpi_data:
            revenue_info = self.test_revenue_field_accuracy(kpi_data)
        
        # Test 4: Listings field accuracy
        listings_info = None
        if kpi_data:
            listings_info = self.test_listings_field_accuracy(kpi_data)
        
        # Test 5: Conversion rate field
        conversion_info = None
        if kpi_data:
            conversion_info = self.test_conversion_rate_field(kpi_data)
        
        # Test 6: Browse endpoint comparison
        browse_data = self.compare_with_browse_endpoint()
        
        # Test 7: Field mismatch analysis
        mismatch_analysis = None
        if dashboard_data and browse_data:
            mismatch_analysis = self.identify_field_mismatches(dashboard_data, browse_data)
        
        # Summary
        print("=" * 80)
        print("DASHBOARD DEBUG SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Key findings
        print("KEY FINDINGS:")
        print("=" * 40)
        
        if dashboard_data and "kpis" in dashboard_data:
            kpis = dashboard_data["kpis"]
            print("Dashboard KPI Fields:")
            for field, value in kpis.items():
                print(f"  - {field}: {value}")
            print()
        
        if revenue_info:
            print(f"Revenue Field: '{revenue_info['field_name']}' = {revenue_info['value']}")
        
        if listings_info:
            print("Listings Fields:")
            for field, value in listings_info.items():
                print(f"  - {field}: {value}")
        
        if conversion_info:
            print("Conversion/Growth Fields:")
            for field, value in conversion_info.items():
                print(f"  - {field}: {value}")
        
        print()
        
        # Critical issues
        critical_issues = []
        if not dashboard_data:
            critical_issues.append("Dashboard endpoint not accessible")
        elif "kpis" not in dashboard_data:
            critical_issues.append("No 'kpis' section in dashboard response")
        
        if not revenue_info:
            critical_issues.append("No revenue field found in dashboard")
        
        if not listings_info:
            critical_issues.append("No listings fields found in dashboard")
        
        if critical_issues:
            print("CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"❌ {issue}")
        else:
            print("✅ ALL CRITICAL FIELDS FOUND")
        
        print()
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = DashboardDebugTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 DASHBOARD DEBUG COMPLETED - Check findings above for field mapping issues")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Check the issues above")
        sys.exit(1)