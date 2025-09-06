#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Listings Count Discrepancy Debug
Investigating the admin panel listings count issue where 6 total listings show but only 2 in tabs
"""

import requests
import json
from datetime import datetime
from collections import Counter

# Get backend URL from environment
BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

class ListingsDebugTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
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

    def test_get_all_listings_with_status_analysis(self):
        """Get ALL listings and analyze status values"""
        try:
            print("🔍 FETCHING ALL LISTINGS WITH STATUS=ALL")
            print("-" * 60)
            
            response = requests.get(f"{BACKEND_URL}/listings?status=all", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                listings = data.get('listings', [])
                total_count = data.get('total', 0)
                
                print(f"📊 TOTAL LISTINGS FOUND: {len(listings)}")
                print(f"📊 TOTAL COUNT FROM API: {total_count}")
                print()
                
                # Analyze status values
                status_counter = Counter()
                status_details = {}
                
                for i, listing in enumerate(listings):
                    listing_id = listing.get('id', listing.get('_id', f'unknown_{i}'))
                    status = listing.get('status', 'NO_STATUS')
                    title = listing.get('title', 'No Title')
                    price = listing.get('price', 0)
                    created_at = listing.get('created_at', 'No Date')
                    
                    status_counter[status] += 1
                    
                    if status not in status_details:
                        status_details[status] = []
                    
                    status_details[status].append({
                        'id': listing_id,
                        'title': title,
                        'price': price,
                        'created_at': created_at
                    })
                
                # Print detailed status analysis
                print("📋 STATUS BREAKDOWN:")
                print("-" * 40)
                for status, count in status_counter.items():
                    print(f"  {status}: {count} listings")
                print()
                
                # Print detailed listings by status
                print("📝 DETAILED LISTINGS BY STATUS:")
                print("-" * 60)
                for status, listings_list in status_details.items():
                    print(f"\n🏷️  STATUS: {status} ({len(listings_list)} listings)")
                    print("   " + "-" * 50)
                    for listing in listings_list:
                        print(f"   ID: {listing['id']}")
                        print(f"   Title: {listing['title']}")
                        print(f"   Price: €{listing['price']}")
                        print(f"   Created: {listing['created_at']}")
                        print()
                
                # Check for unexpected status values
                expected_statuses = ['active', 'sold', 'inactive', 'draft', 'pending']
                unexpected_statuses = [status for status in status_counter.keys() if status not in expected_statuses]
                
                if unexpected_statuses:
                    print("⚠️  UNEXPECTED STATUS VALUES FOUND:")
                    for status in unexpected_statuses:
                        print(f"   - {status}: {status_counter[status]} listings")
                    print()
                
                # Check for null/undefined status values
                null_status_count = status_counter.get('NO_STATUS', 0) + status_counter.get(None, 0) + status_counter.get('', 0)
                if null_status_count > 0:
                    print(f"⚠️  LISTINGS WITH NULL/EMPTY STATUS: {null_status_count}")
                    print()
                
                self.log_test(
                    "Get All Listings with Status Analysis", 
                    True, 
                    f"Found {len(listings)} total listings. Status breakdown: {dict(status_counter)}"
                )
                
                return listings, status_counter, status_details
                
            else:
                self.log_test(
                    "Get All Listings with Status Analysis", 
                    False, 
                    f"HTTP {response.status_code}"
                )
                return [], Counter(), {}
                
        except Exception as e:
            self.log_test(
                "Get All Listings with Status Analysis", 
                False, 
                error_msg=str(e)
            )
            return [], Counter(), {}

    def test_admin_panel_tab_simulation(self, status_counter):
        """Simulate admin panel tab counts to identify discrepancy"""
        try:
            print("🎯 SIMULATING ADMIN PANEL TAB COUNTS")
            print("-" * 50)
            
            # Admin panel typically shows these tabs
            active_count = status_counter.get('active', 0)
            sold_count = status_counter.get('sold', 0)
            inactive_count = status_counter.get('inactive', 0)
            draft_count = status_counter.get('draft', 0)
            pending_count = status_counter.get('pending', 0)
            
            # Calculate total shown in tabs
            total_in_tabs = active_count + sold_count + inactive_count + draft_count + pending_count
            
            # Calculate total listings
            total_listings = sum(status_counter.values())
            
            # Calculate missing listings
            missing_listings = total_listings - total_in_tabs
            
            print(f"📊 ADMIN PANEL TAB SIMULATION:")
            print(f"   Active: {active_count}")
            print(f"   Sold: {sold_count}")
            print(f"   Inactive: {inactive_count}")
            print(f"   Draft: {draft_count}")
            print(f"   Pending: {pending_count}")
            print(f"   ─────────────────")
            print(f"   Total in Tabs: {total_in_tabs}")
            print(f"   Total Listings: {total_listings}")
            print(f"   Missing from Tabs: {missing_listings}")
            print()
            
            if missing_listings > 0:
                print("🔍 LISTINGS NOT COVERED BY STANDARD TABS:")
                for status, count in status_counter.items():
                    if status not in ['active', 'sold', 'inactive', 'draft', 'pending']:
                        print(f"   - {status}: {count} listings")
                print()
            
            self.log_test(
                "Admin Panel Tab Simulation", 
                True, 
                f"Total: {total_listings}, In Tabs: {total_in_tabs}, Missing: {missing_listings}"
            )
            
            return {
                'total_listings': total_listings,
                'total_in_tabs': total_in_tabs,
                'missing_listings': missing_listings,
                'active': active_count,
                'sold': sold_count,
                'inactive': inactive_count,
                'draft': draft_count,
                'pending': pending_count
            }
            
        except Exception as e:
            self.log_test(
                "Admin Panel Tab Simulation", 
                False, 
                error_msg=str(e)
            )
            return {}

    def test_data_structure_validation(self, listings):
        """Examine data structure for issues"""
        try:
            print("🔬 DATA STRUCTURE VALIDATION")
            print("-" * 40)
            
            structure_issues = []
            valid_listings = 0
            
            for i, listing in enumerate(listings):
                listing_id = listing.get('id', listing.get('_id', f'listing_{i}'))
                issues = []
                
                # Check required fields
                if not listing.get('title'):
                    issues.append('Missing title')
                if not listing.get('status'):
                    issues.append('Missing status')
                if listing.get('price') is None:
                    issues.append('Missing price')
                if not listing.get('seller_id'):
                    issues.append('Missing seller_id')
                
                # Check for null/undefined values
                if listing.get('status') in [None, '', 'null', 'undefined']:
                    issues.append(f'Invalid status value: {listing.get("status")}')
                
                if issues:
                    structure_issues.append({
                        'id': listing_id,
                        'title': listing.get('title', 'No Title'),
                        'issues': issues
                    })
                else:
                    valid_listings += 1
            
            print(f"📊 STRUCTURE VALIDATION RESULTS:")
            print(f"   Valid Listings: {valid_listings}")
            print(f"   Listings with Issues: {len(structure_issues)}")
            print()
            
            if structure_issues:
                print("⚠️  LISTINGS WITH STRUCTURE ISSUES:")
                for issue_listing in structure_issues:
                    print(f"   ID: {issue_listing['id']}")
                    print(f"   Title: {issue_listing['title']}")
                    print(f"   Issues: {', '.join(issue_listing['issues'])}")
                    print()
            
            self.log_test(
                "Data Structure Validation", 
                True, 
                f"Valid: {valid_listings}, Issues: {len(structure_issues)}"
            )
            
            return structure_issues
            
        except Exception as e:
            self.log_test(
                "Data Structure Validation", 
                False, 
                error_msg=str(e)
            )
            return []

    def test_specific_status_queries(self):
        """Test specific status queries to verify filtering"""
        try:
            print("🎯 TESTING SPECIFIC STATUS QUERIES")
            print("-" * 45)
            
            status_results = {}
            
            # Test each status individually
            statuses_to_test = ['active', 'sold', 'inactive', 'draft', 'pending']
            
            for status in statuses_to_test:
                try:
                    response = requests.get(f"{BACKEND_URL}/listings?status={status}", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        listings = data.get('listings', [])
                        count = len(listings)
                        status_results[status] = count
                        print(f"   {status}: {count} listings")
                    else:
                        status_results[status] = f"Error: HTTP {response.status_code}"
                        print(f"   {status}: Error HTTP {response.status_code}")
                except Exception as e:
                    status_results[status] = f"Error: {str(e)}"
                    print(f"   {status}: Error - {str(e)}")
            
            print()
            
            self.log_test(
                "Specific Status Queries", 
                True, 
                f"Status query results: {status_results}"
            )
            
            return status_results
            
        except Exception as e:
            self.log_test(
                "Specific Status Queries", 
                False, 
                error_msg=str(e)
            )
            return {}

    def run_listings_debug_analysis(self):
        """Run comprehensive listings debug analysis"""
        print("=" * 80)
        print("CATALORO LISTINGS COUNT DISCREPANCY DEBUG")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Debug Started: {datetime.now().isoformat()}")
        print()
        print("🎯 OBJECTIVE: Find the missing 4 listings in admin panel")
        print("   Admin shows: 6 total, but only 2 in tabs (Active:1, Sold:1)")
        print("   Expected: Find where the other 4 listings are")
        print()
        
        # 1. Get all listings and analyze status values
        listings, status_counter, status_details = self.test_get_all_listings_with_status_analysis()
        
        # 2. Simulate admin panel tab counts
        if status_counter:
            tab_analysis = self.test_admin_panel_tab_simulation(status_counter)
        
        # 3. Validate data structure
        if listings:
            structure_issues = self.test_data_structure_validation(listings)
        
        # 4. Test specific status queries
        status_query_results = self.test_specific_status_queries()
        
        # 5. Generate comprehensive report
        print("=" * 80)
        print("🔍 COMPREHENSIVE ANALYSIS REPORT")
        print("=" * 80)
        
        if listings:
            total_found = len(listings)
            print(f"📊 TOTAL LISTINGS FOUND: {total_found}")
            print()
            
            print("📋 STATUS DISTRIBUTION:")
            for status, count in status_counter.most_common():
                print(f"   {status}: {count} listings")
            print()
            
            # Identify the discrepancy
            if 'tab_analysis' in locals():
                missing = tab_analysis.get('missing_listings', 0)
                if missing > 0:
                    print(f"🚨 DISCREPANCY IDENTIFIED:")
                    print(f"   {missing} listings are not covered by standard admin panel tabs")
                    print()
                    
                    print("🔍 ORPHANED LISTINGS (not in standard tabs):")
                    for status, count in status_counter.items():
                        if status not in ['active', 'sold', 'inactive', 'draft', 'pending']:
                            print(f"   Status '{status}': {count} listings")
                            if status in status_details:
                                for listing in status_details[status]:
                                    print(f"     - {listing['title']} (ID: {listing['id']})")
                    print()
                else:
                    print("✅ NO DISCREPANCY: All listings are covered by standard tabs")
                    print()
        
        # Print Summary
        print("=" * 80)
        print("DEBUG SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = ListingsDebugTester()
    passed, failed, results = tester.run_listings_debug_analysis()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)