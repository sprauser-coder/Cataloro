#!/usr/bin/env python3
"""
COMPREHENSIVE USER COUNT INVESTIGATION TEST
Testing ALL endpoints that might show user counts to find where 156 comes from
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class UserCountInvestigator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.user_counts_found = {}
        
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
            
            # Check if this is 156
            if total_users == 156:
                self.log_test(
                    "Admin Dashboard User Count",
                    True,
                    f"🎯 FOUND 156! Admin dashboard shows {total_users} users",
                    "Any user count",
                    f"{total_users} users"
                )
                return True
            else:
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
                
                # Check if this is 156
                if user_count == 156:
                    self.log_test(
                        "Admin Users Endpoint Count",
                        True,
                        f"🎯 FOUND 156! Admin users endpoint returns {user_count} users",
                        "Any user count",
                        f"{user_count} users"
                    )
                    return True
                else:
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
    
    def test_browse_listings_for_user_data(self):
        """Test 3: GET /api/marketplace/browse - Check for user-related counts"""
        try:
            response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if response.status_code != 200:
                self.log_test(
                    "Browse Listings User Data",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            listings = response.json()
            
            if isinstance(listings, list):
                listing_count = len(listings)
                
                # Extract unique sellers
                unique_sellers = set()
                seller_ids = []
                
                for listing in listings:
                    seller_id = listing.get("seller_id")
                    if seller_id:
                        unique_sellers.add(seller_id)
                        seller_ids.append(seller_id)
                
                unique_seller_count = len(unique_sellers)
                total_seller_references = len(seller_ids)
                
                self.record_user_count("browse_unique_sellers", unique_seller_count, f"Unique sellers from {listing_count} listings")
                self.record_user_count("browse_total_seller_refs", total_seller_references, f"Total seller references from {listing_count} listings")
                
                # Check if any of these counts are 156
                if unique_seller_count == 156:
                    self.log_test(
                        "Browse Listings User Data",
                        True,
                        f"🎯 FOUND 156! Unique sellers in browse: {unique_seller_count}",
                        "Any user count",
                        f"{unique_seller_count} unique sellers"
                    )
                    return True
                elif total_seller_references == 156:
                    self.log_test(
                        "Browse Listings User Data",
                        True,
                        f"🎯 FOUND 156! Total seller references: {total_seller_references}",
                        "Any user count",
                        f"{total_seller_references} seller references"
                    )
                    return True
                elif listing_count == 156:
                    self.log_test(
                        "Browse Listings User Data",
                        True,
                        f"🎯 FOUND 156! Total listings: {listing_count}",
                        "Any user count",
                        f"{listing_count} listings"
                    )
                    return True
                else:
                    self.log_test(
                        "Browse Listings User Data",
                        True,
                        f"Browse data: {listing_count} listings, {unique_seller_count} unique sellers, {total_seller_references} seller refs (none are 156)",
                        "User count data",
                        f"Listings: {listing_count}, Sellers: {unique_seller_count}"
                    )
                    return True
            else:
                self.log_test(
                    "Browse Listings User Data",
                    False,
                    f"Unexpected response format: {type(listings)}",
                    "List of listings",
                    f"{type(listings)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Browse Listings User Data",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_all_listings_endpoint(self):
        """Test 4: GET /api/listings - Check for user-related counts"""
        try:
            response = self.session.get(f"{self.backend_url}/listings")
            
            if response.status_code != 200:
                self.log_test(
                    "All Listings Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            data = response.json()
            
            # Handle both direct list and object with listings array
            if isinstance(data, dict) and "listings" in data:
                listings = data["listings"]
                total_count = data.get("total", len(listings))
            elif isinstance(data, list):
                listings = data
                total_count = len(listings)
            else:
                self.log_test(
                    "All Listings Endpoint",
                    False,
                    f"Unexpected response format: {type(data)}",
                    "List or object with listings",
                    f"{type(data)}"
                )
                return False
            
            listing_count = len(listings)
            
            self.record_user_count("all_listings_count", listing_count, f"Total listings from /api/listings")
            self.record_user_count("all_listings_total", total_count, f"Total count field from /api/listings")
            
            # Check if any counts are 156
            if listing_count == 156:
                self.log_test(
                    "All Listings Endpoint",
                    True,
                    f"🎯 FOUND 156! All listings count: {listing_count}",
                    "Any user count",
                    f"{listing_count} listings"
                )
                return True
            elif total_count == 156:
                self.log_test(
                    "All Listings Endpoint",
                    True,
                    f"🎯 FOUND 156! All listings total: {total_count}",
                    "Any user count",
                    f"{total_count} total"
                )
                return True
            else:
                self.log_test(
                    "All Listings Endpoint",
                    True,
                    f"All listings: {listing_count} listings, {total_count} total (none are 156)",
                    "User count data",
                    f"Listings: {listing_count}, Total: {total_count}"
                )
                return True
                
        except Exception as e:
            self.log_test(
                "All Listings Endpoint",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_search_for_156_in_responses(self):
        """Test 5: Search for any occurrence of 156 in various endpoints"""
        try:
            endpoints_to_check = [
                "/admin/dashboard",
                "/admin/users", 
                "/marketplace/browse",
                "/listings",
                "/admin/settings",
                "/admin/content"
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
    
    def test_potential_sum_calculations(self):
        """Test 6: Check if 156 might be a sum of multiple collections"""
        try:
            # Get all the counts we've collected
            dashboard_response = self.session.get(f"{self.backend_url}/admin/dashboard")
            users_response = self.session.get(f"{self.backend_url}/admin/users")
            browse_response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
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
                    ("listings + deals", total_listings + total_deals),
                    ("users + listings + deals", total_users + total_listings + total_deals),
                    ("users * 2", total_users * 2),
                    ("listings * 2", total_listings * 2)
                ])
            
            if users_response.status_code == 200:
                users = users_response.json()
                if isinstance(users, list):
                    user_count = len(users)
                    
                    # Count different user types
                    admin_count = sum(1 for user in users if user.get("role") == "admin")
                    regular_count = sum(1 for user in users if user.get("role") != "admin")
                    
                    calculations.extend([
                        ("admin_users + regular_users", admin_count + regular_count),
                        ("users * 2.1", int(user_count * 2.1)),
                        ("users + 82", user_count + 82)  # If 156 was peak and 82 were deleted
                    ])
            
            # Check if any calculation equals 156
            found_156_calculations = []
            for calc_name, calc_result in calculations:
                if calc_result == 156:
                    found_156_calculations.append(f"{calc_name} = {calc_result}")
                    self.record_user_count(f"calculation_{calc_name.replace(' ', '_')}", 156, f"Calculation: {calc_name}")
            
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
        test3_success = self.test_browse_listings_for_user_data()
        test4_success = self.test_all_listings_endpoint()
        test5_success = self.test_search_for_156_in_responses()
        test6_success = self.test_potential_sum_calculations()
        
        # Summary
        print("=" * 80)
        print("INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = 6
        passed_tests = sum([test1_success, test2_success, test3_success, test4_success, test5_success, test6_success])
        
        print(f"Total Investigation Areas: {total_tests}")
        print(f"Completed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Show all user counts found
        print("USER COUNTS DISCOVERED:")
        print("-" * 40)
        
        found_156 = False
        for source, data in self.user_counts_found.items():
            count = data["count"]
            info = data["info"]
            
            if count == 156:
                print(f"🎯 {source}: {count} *** THIS IS 156! ***")
                found_156 = True
            else:
                print(f"   {source}: {count}")
            
            if info:
                print(f"      Info: {info}")
        
        print()
        
        # Analysis
        if found_156:
            print("🎯 INVESTIGATION RESULT: FOUND SOURCE OF 156!")
            print("The 156 user count has been located in the system.")
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
        
        print(f"CURRENT ACTUAL COUNTS:")
        print(f"Dashboard reports: {dashboard_count} users")
        print(f"Users endpoint returns: {users_count} users")
        
        if dashboard_count == users_count and dashboard_count != "Unknown":
            print(f"✅ Both sources agree: {dashboard_count} users")
        elif dashboard_count != users_count:
            print(f"⚠️  Discrepancy: Dashboard={dashboard_count}, Users endpoint={users_count}")
        
        print()
        return passed_tests == total_tests, found_156

if __name__ == "__main__":
    investigator = UserCountInvestigator()
    success, found_156 = investigator.run_comprehensive_investigation()
    
    if found_156:
        print("🎉 INVESTIGATION COMPLETE - Found the source of 156!")
        sys.exit(0)
    elif success:
        print("✅ INVESTIGATION COMPLETE - No current 156 count found")
        sys.exit(0)
    else:
        print("⚠️  INVESTIGATION INCOMPLETE - Some areas failed to check")
        sys.exit(1)