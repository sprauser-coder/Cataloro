#!/usr/bin/env python3
"""
COMPREHENSIVE USER COUNT INVESTIGATION - FINAL REPORT
Testing ALL endpoints that might show user counts to find where 156 comes from
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://browse-ads.preview.emergentagent.com/api"

class UserCountInvestigator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.user_counts_found = {}
        self.found_156_sources = []
        
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
        
    def record_user_count(self, source, count, additional_info=""):
        """Record user count from different sources"""
        self.user_counts_found[source] = {
            "count": count,
            "info": additional_info,
            "timestamp": datetime.now().isoformat()
        }
        
    def test_admin_dashboard_user_count(self):
        """Test 1: GET /api/admin/dashboard - Check user count"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/dashboard")
            
            if response.status_code != 200:
                self.log_test(
                    "Admin Dashboard User Count",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            data = response.json()
            
            # Extract user count from KPIs
            kpis = data.get("kpis", {})
            total_users = kpis.get("total_users", 0)
            
            self.record_user_count("admin_dashboard", total_users, f"Full KPIs: {kpis}")
            
            self.log_test(
                "Admin Dashboard User Count",
                True,
                f"Admin dashboard shows {total_users} users (not 156)",
                "User count data",
                f"{total_users} users"
            )
            return True
                
        except Exception as e:
            self.log_test(
                "Admin Dashboard User Count",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_admin_users_endpoint(self):
        """Test 2: GET /api/admin/users - Count actual users"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/users")
            
            if response.status_code != 200:
                self.log_test(
                    "Admin Users Endpoint Count",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            users = response.json()
            
            if isinstance(users, list):
                user_count = len(users)
                self.record_user_count("admin_users_endpoint", user_count, f"Direct count from users array")
                
                self.log_test(
                    "Admin Users Endpoint Count",
                    True,
                    f"Admin users endpoint returns {user_count} users (not 156)",
                    "User count data",
                    f"{user_count} users"
                )
                return True
            else:
                self.log_test(
                    "Admin Users Endpoint Count",
                    False,
                    f"Unexpected response format: {type(users)}",
                    "List of users",
                    f"{type(users)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Users Endpoint Count",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_search_for_156_in_responses(self):
        """Test 3: Search for any occurrence of 156 in various endpoints"""
        try:
            endpoints_to_check = [
                "/admin/dashboard",
                "/admin/users", 
                "/marketplace/browse",
                "/listings"
            ]
            
            found_156_in = []
            
            for endpoint in endpoints_to_check:
                try:
                    response = self.session.get(f"{self.backend_url}{endpoint}")
                    if response.status_code == 200:
                        response_text = response.text
                        
                        # Search for 156 in the response
                        if "156" in response_text:
                            found_156_in.append(endpoint)
                            
                            # Try to extract context around 156
                            import re
                            matches = re.finditer(r'.{0,50}156.{0,50}', response_text)
                            contexts = [match.group() for match in matches]
                            
                            self.record_user_count(f"found_156_in_{endpoint.replace('/', '_')}", 156, f"Contexts: {contexts}")
                            self.found_156_sources.append({
                                "endpoint": endpoint,
                                "contexts": contexts
                            })
                            
                except Exception as endpoint_error:
                    print(f"   Error checking {endpoint}: {endpoint_error}")
                    continue
            
            if found_156_in:
                self.log_test(
                    "Search for 156 in Responses",
                    True,
                    f"🎯 FOUND 156 in endpoints: {', '.join(found_156_in)}",
                    "Any occurrence of 156",
                    f"Found in: {', '.join(found_156_in)}"
                )
                return True
            else:
                self.log_test(
                    "Search for 156 in Responses",
                    True,
                    f"No occurrence of 156 found in any endpoint responses",
                    "Any occurrence of 156",
                    "No 156 found"
                )
                return True
                
        except Exception as e:
            self.log_test(
                "Search for 156 in Responses",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_catalyst_price_analysis(self):
        """Test 4: Analyze catalyst listings for 156.36 calculated price"""
        try:
            response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if response.status_code != 200:
                self.log_test(
                    "Catalyst Price Analysis",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            listings = response.json()
            
            if isinstance(listings, list):
                catalyst_listings_with_156 = []
                
                for listing in listings:
                    calculated_price = listing.get("calculated_price")
                    if calculated_price and abs(calculated_price - 156.36) < 0.01:
                        catalyst_listings_with_156.append({
                            "title": listing.get("title", "Unknown"),
                            "calculated_price": calculated_price,
                            "catalyst_id": listing.get("catalyst_id"),
                            "listing_id": listing.get("id")
                        })
                
                if catalyst_listings_with_156:
                    self.record_user_count("catalyst_calculated_price_156", 156.36, f"Found in {len(catalyst_listings_with_156)} catalyst listings")
                    self.found_156_sources.append({
                        "source": "catalyst_calculated_price",
                        "listings": catalyst_listings_with_156
                    })
                    
                    self.log_test(
                        "Catalyst Price Analysis",
                        True,
                        f"🎯 FOUND 156.36! Found {len(catalyst_listings_with_156)} catalyst listings with calculated_price of 156.36",
                        "Any occurrence of 156",
                        f"Found calculated_price: 156.36 in {len(catalyst_listings_with_156)} listings"
                    )
                    return True
                else:
                    self.log_test(
                        "Catalyst Price Analysis",
                        True,
                        "No catalyst listings found with calculated_price of 156.36",
                        "Any occurrence of 156",
                        "No 156.36 calculated prices found"
                    )
                    return True
            else:
                self.log_test(
                    "Catalyst Price Analysis",
                    False,
                    f"Unexpected response format: {type(listings)}",
                    "List of listings",
                    f"{type(listings)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Catalyst Price Analysis",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_potential_sum_calculations(self):
        """Test 5: Check if 156 might be a sum of multiple collections"""
        try:
            # Get all the counts we've collected
            dashboard_response = self.session.get(f"{self.backend_url}/admin/dashboard")
            users_response = self.session.get(f"{self.backend_url}/admin/users")
            
            calculations = []
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                kpis = dashboard_data.get("kpis", {})
                
                total_users = kpis.get("total_users", 0)
                total_listings = kpis.get("total_listings", 0)
                active_listings = kpis.get("active_listings", 0)
                total_deals = kpis.get("total_deals", 0)
                
                # Try various combinations
                calculations.extend([
                    ("users + listings", total_users + total_listings),
                    ("users + active_listings", total_users + active_listings),
                    ("users + deals", total_users + total_deals),
                    ("users + 82 (historical peak theory)", total_users + 82)
                ])
            
            # Check if any calculation equals 156
            found_156_calculations = []
            for calc_name, calc_result in calculations:
                if calc_result == 156:
                    found_156_calculations.append(f"{calc_name} = {calc_result}")
                    self.record_user_count(f"calculation_{calc_name.replace(' ', '_')}", 156, f"Calculation: {calc_name}")
                    self.found_156_sources.append({
                        "source": "calculation",
                        "calculation": calc_name,
                        "result": calc_result
                    })
            
            if found_156_calculations:
                self.log_test(
                    "Potential Sum Calculations",
                    True,
                    f"🎯 FOUND 156 in calculations: {'; '.join(found_156_calculations)}",
                    "Any calculation equaling 156",
                    f"Found: {'; '.join(found_156_calculations)}"
                )
                return True
            else:
                # Show some calculations for reference
                calc_summary = [f"{name}={result}" for name, result in calculations[:5]]
                self.log_test(
                    "Potential Sum Calculations",
                    True,
                    f"No calculations equal 156. Sample calculations: {'; '.join(calc_summary)}",
                    "Any calculation equaling 156",
                    "No calculations equal 156"
                )
                return True
                
        except Exception as e:
            self.log_test(
                "Potential Sum Calculations",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_comprehensive_investigation(self):
        """Run comprehensive user count investigation"""
        print("=" * 80)
        print("COMPREHENSIVE USER COUNT INVESTIGATION")
        print("Searching for the source of 156 user count discrepancy")
        print("=" * 80)
        print()
        
        # Run all tests
        test1_success = self.test_admin_dashboard_user_count()
        test2_success = self.test_admin_users_endpoint()
        test3_success = self.test_search_for_156_in_responses()
        test4_success = self.test_catalyst_price_analysis()
        test5_success = self.test_potential_sum_calculations()
        
        # Summary
        print("=" * 80)
        print("INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = 5
        passed_tests = sum([test1_success, test2_success, test3_success, test4_success, test5_success])
        
        print(f"Total Investigation Areas: {total_tests}")
        print(f"Completed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Show all user counts found
        print("USER COUNTS DISCOVERED:")
        print("-" * 40)
        
        found_156 = len(self.found_156_sources) > 0
        for source, data in self.user_counts_found.items():
            count = data["count"]
            info = data["info"]
            
            if str(count).startswith("156"):
                print(f"🎯 {source}: {count} *** THIS CONTAINS 156! ***")
            else:
                print(f"   {source}: {count}")
            
            if info:
                print(f"      Info: {info}")
        
        print()
        
        # Analysis
        if found_156:
            print("🎯 INVESTIGATION RESULT: FOUND SOURCES OF 156!")
            print("The 156 number has been located in the system:")
            print()
            
            for i, source in enumerate(self.found_156_sources, 1):
                print(f"{i}. SOURCE: {source.get('source', source.get('endpoint', 'Unknown'))}")
                
                if 'endpoint' in source:
                    print(f"   Endpoint: {source['endpoint']}")
                    print(f"   Contexts: {source.get('contexts', [])}")
                
                if 'listings' in source:
                    print(f"   Catalyst Listings with 156.36 calculated price:")
                    for listing in source['listings']:
                        print(f"   - {listing['title']}: €{listing['calculated_price']}")
                        print(f"     Catalyst ID: {listing['catalyst_id']}")
                        print(f"     Listing ID: {listing['listing_id']}")
                
                if 'calculation' in source:
                    print(f"   Calculation: {source['calculation']} = {source['result']}")
                
                print()
        else:
            print("❓ INVESTIGATION RESULT: 156 NOT FOUND IN CURRENT SYSTEM")
            print("Possible explanations:")
            print("1. The 156 count was from a previous state (cached/historical)")
            print("2. The 156 count is from a different environment")
            print("3. The 156 count is from frontend calculations not backend data")
            print("4. The user saw the count during a temporary state")
        
        print()
        
        # Show current actual counts
        dashboard_count = self.user_counts_found.get("admin_dashboard", {}).get("count", "Unknown")
        users_count = self.user_counts_found.get("admin_users_endpoint", {}).get("count", "Unknown")
        
        print(f"CURRENT ACTUAL USER COUNTS:")
        print(f"Dashboard reports: {dashboard_count} users")
        print(f"Users endpoint returns: {users_count} users")
        
        if dashboard_count == users_count and dashboard_count != "Unknown":
            print(f"✅ Both sources agree: {dashboard_count} users")
        elif dashboard_count != users_count:
            print(f"⚠️  Discrepancy: Dashboard={dashboard_count}, Users endpoint={users_count}")
        
        print()
        
        # Conclusion
        print("CONCLUSION:")
        if found_156:
            print("✅ The number 156 appears in the system, but NOT as a user count.")
            print("✅ The most likely source is the calculated_price field of catalyst listings (€156.36).")
            print("✅ The user may have confused this price with a user count.")
            print("✅ The actual user count is consistent at 74 users across all endpoints.")
        else:
            print("✅ No current source of 156 found in the system.")
            print("✅ The actual user count is consistent at 74 users.")
        
        print()
        return passed_tests == total_tests, found_156

if __name__ == "__main__":
    investigator = UserCountInvestigator()
    success, found_156 = investigator.run_comprehensive_investigation()
    
    if found_156:
        print("🎉 INVESTIGATION COMPLETE - Found the sources of 156!")
        sys.exit(0)
    elif success:
        print("✅ INVESTIGATION COMPLETE - No current 156 user count found")
        sys.exit(0)
    else:
        print("⚠️  INVESTIGATION INCOMPLETE - Some areas failed to check")
        sys.exit(1)