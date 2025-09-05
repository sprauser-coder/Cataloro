#!/usr/bin/env python3
"""
Dashboard Data Accuracy Debug Testing
Comprehensive testing to identify dashboard data accuracy issues
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://cataloro-upgrade.preview.emergentagent.com/api"

class DashboardDataDebugger:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.actual_data = {}
        
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
        
    def test_database_collections_count(self):
        """Test 1: Check actual database collections and document counts"""
        try:
            print("🔍 CHECKING DATABASE COLLECTIONS AND COUNTS")
            print("-" * 60)
            
            # Test users collection via GET /api/admin/users
            users_response = self.session.get(f"{self.backend_url}/admin/users")
            if users_response.status_code == 200:
                users_data = users_response.json()
                actual_users_count = len(users_data) if isinstance(users_data, list) else 0
                self.actual_data['users_count'] = actual_users_count
                
                self.log_test(
                    "Database Users Collection Count",
                    True,
                    f"Found {actual_users_count} users in database via /api/admin/users"
                )
                
                # Show sample user data structure
                if users_data and len(users_data) > 0:
                    sample_user = users_data[0]
                    print(f"   Sample user structure: {list(sample_user.keys())}")
                    print(f"   Sample user: {sample_user.get('username', 'N/A')} ({sample_user.get('email', 'N/A')})")
                
            else:
                self.log_test(
                    "Database Users Collection Count",
                    False,
                    f"Failed to access users collection: HTTP {users_response.status_code}"
                )
                self.actual_data['users_count'] = 0
            
            # Test listings collection via GET /api/listings
            listings_response = self.session.get(f"{self.backend_url}/listings?limit=1000")
            if listings_response.status_code == 200:
                listings_data = listings_response.json()
                if isinstance(listings_data, dict) and 'listings' in listings_data:
                    actual_listings_count = len(listings_data['listings'])
                    total_from_api = listings_data.get('total', actual_listings_count)
                elif isinstance(listings_data, list):
                    actual_listings_count = len(listings_data)
                    total_from_api = actual_listings_count
                else:
                    actual_listings_count = 0
                    total_from_api = 0
                
                self.actual_data['listings_count'] = actual_listings_count
                self.actual_data['listings_total'] = total_from_api
                
                self.log_test(
                    "Database Listings Collection Count",
                    True,
                    f"Found {actual_listings_count} listings in response, API reports total: {total_from_api}"
                )
                
                # Show sample listing data structure
                if isinstance(listings_data, dict) and 'listings' in listings_data and listings_data['listings']:
                    sample_listing = listings_data['listings'][0]
                    print(f"   Sample listing structure: {list(sample_listing.keys())}")
                    print(f"   Sample listing: {sample_listing.get('title', 'N/A')} - €{sample_listing.get('price', 0)}")
                elif isinstance(listings_data, list) and listings_data:
                    sample_listing = listings_data[0]
                    print(f"   Sample listing structure: {list(sample_listing.keys())}")
                    print(f"   Sample listing: {sample_listing.get('title', 'N/A')} - €{sample_listing.get('price', 0)}")
                
            else:
                self.log_test(
                    "Database Listings Collection Count",
                    False,
                    f"Failed to access listings collection: HTTP {listings_response.status_code}"
                )
                self.actual_data['listings_count'] = 0
                self.actual_data['listings_total'] = 0
            
            return True
            
        except Exception as e:
            self.log_test(
                "Database Collections Count",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_marketplace_browse_endpoint(self):
        """Test 2: Check marketplace browse endpoint for real user count"""
        try:
            print("🔍 CHECKING MARKETPLACE BROWSE ENDPOINT")
            print("-" * 60)
            
            # Test browse endpoint which should show real marketplace data
            browse_response = self.session.get(f"{self.backend_url}/marketplace/browse")
            if browse_response.status_code == 200:
                browse_data = browse_response.json()
                if isinstance(browse_data, list):
                    browse_listings_count = len(browse_data)
                    self.actual_data['browse_listings_count'] = browse_listings_count
                    
                    # Count unique sellers to get real user count
                    unique_sellers = set()
                    active_listings = 0
                    total_revenue_potential = 0
                    
                    for listing in browse_data:
                        seller_id = listing.get('seller_id')
                        if seller_id:
                            unique_sellers.add(seller_id)
                        
                        if listing.get('status') == 'active':
                            active_listings += 1
                        
                        # Check for bid info to calculate potential revenue
                        bid_info = listing.get('bid_info', {})
                        if bid_info.get('has_bids', False):
                            total_revenue_potential += bid_info.get('highest_bid', 0)
                        else:
                            total_revenue_potential += listing.get('price', 0)
                    
                    self.actual_data['unique_sellers_count'] = len(unique_sellers)
                    self.actual_data['active_listings_from_browse'] = active_listings
                    self.actual_data['potential_revenue'] = total_revenue_potential
                    
                    self.log_test(
                        "Marketplace Browse Data Analysis",
                        True,
                        f"Browse endpoint: {browse_listings_count} listings, {len(unique_sellers)} unique sellers, {active_listings} active listings, €{total_revenue_potential:.2f} potential revenue"
                    )
                    
                    # Show sample enriched listing
                    if browse_data:
                        sample = browse_data[0]
                        seller_info = sample.get('seller', {})
                        bid_info = sample.get('bid_info', {})
                        print(f"   Sample enriched listing: {sample.get('title', 'N/A')}")
                        print(f"   Seller: {seller_info.get('name', 'N/A')} (Business: {seller_info.get('is_business', False)})")
                        print(f"   Bid info: {bid_info.get('total_bids', 0)} bids, highest: €{bid_info.get('highest_bid', 0)}")
                    
                    return True
                else:
                    self.log_test(
                        "Marketplace Browse Data Analysis",
                        False,
                        f"Unexpected browse data format: {type(browse_data)}"
                    )
                    return False
            else:
                self.log_test(
                    "Marketplace Browse Data Analysis",
                    False,
                    f"Failed to access browse endpoint: HTTP {browse_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Marketplace Browse Data Analysis",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_deals_and_transactions(self):
        """Test 3: Check for actual deals and completed transactions"""
        try:
            print("🔍 CHECKING DEALS AND TRANSACTIONS")
            print("-" * 60)
            
            # We need a test user to check deals
            test_user_data = {
                "email": "dashboard_test_user@example.com",
                "password": "testpass123",
                "username": "dashboard_test_user"
            }
            
            # Login to get user ID
            login_response = self.session.post(f"{self.backend_url}/auth/login", json=test_user_data)
            if login_response.status_code == 200:
                user_data = login_response.json()
                test_user_id = user_data.get("user", {}).get("id")
                
                if test_user_id:
                    # Check user's deals
                    deals_response = self.session.get(f"{self.backend_url}/user/my-deals/{test_user_id}")
                    if deals_response.status_code == 200:
                        deals_data = deals_response.json()
                        deals_count = len(deals_data) if isinstance(deals_data, list) else 0
                        
                        total_deal_revenue = 0
                        completed_deals = 0
                        
                        if isinstance(deals_data, list):
                            for deal in deals_data:
                                if deal.get('status') in ['approved', 'completed']:
                                    completed_deals += 1
                                    total_deal_revenue += deal.get('amount', 0)
                        
                        self.actual_data['user_deals_count'] = deals_count
                        self.actual_data['completed_deals_count'] = completed_deals
                        self.actual_data['actual_deal_revenue'] = total_deal_revenue
                        
                        self.log_test(
                            "User Deals Analysis",
                            True,
                            f"Found {deals_count} deals for test user, {completed_deals} completed, €{total_deal_revenue:.2f} revenue"
                        )
                        
                        if deals_data and len(deals_data) > 0:
                            sample_deal = deals_data[0]
                            print(f"   Sample deal: {sample_deal.get('listing', {}).get('title', 'N/A')} - €{sample_deal.get('amount', 0)} ({sample_deal.get('status', 'N/A')})")
                    else:
                        self.log_test(
                            "User Deals Analysis",
                            False,
                            f"Failed to get user deals: HTTP {deals_response.status_code}"
                        )
                        self.actual_data['user_deals_count'] = 0
                        self.actual_data['completed_deals_count'] = 0
                        self.actual_data['actual_deal_revenue'] = 0
                else:
                    self.log_test(
                        "User Deals Analysis",
                        False,
                        "Failed to get user ID from login"
                    )
                    return False
            else:
                self.log_test(
                    "User Deals Analysis",
                    False,
                    f"Failed to login test user: HTTP {login_response.status_code}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_test(
                "Deals and Transactions Analysis",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_admin_dashboard_data(self):
        """Test 4: Get admin dashboard data and compare with actual data"""
        try:
            print("🔍 CHECKING ADMIN DASHBOARD DATA")
            print("-" * 60)
            
            dashboard_response = self.session.get(f"{self.backend_url}/admin/dashboard")
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                kpis = dashboard_data.get('kpis', {})
                
                dashboard_users = kpis.get('total_users', 0)
                dashboard_listings = kpis.get('total_listings', 0)
                dashboard_active_listings = kpis.get('active_listings', 0)
                dashboard_deals = kpis.get('total_deals', 0)
                dashboard_revenue = kpis.get('revenue', 0)
                dashboard_growth = kpis.get('growth_rate', 0)
                
                self.actual_data['dashboard_users'] = dashboard_users
                self.actual_data['dashboard_listings'] = dashboard_listings
                self.actual_data['dashboard_active_listings'] = dashboard_active_listings
                self.actual_data['dashboard_deals'] = dashboard_deals
                self.actual_data['dashboard_revenue'] = dashboard_revenue
                self.actual_data['dashboard_growth'] = dashboard_growth
                
                self.log_test(
                    "Admin Dashboard KPIs",
                    True,
                    f"Dashboard reports: {dashboard_users} users, {dashboard_listings} listings, {dashboard_active_listings} active, {dashboard_deals} deals, €{dashboard_revenue} revenue, {dashboard_growth}% growth"
                )
                
                # Show recent activity
                recent_activity = dashboard_data.get('recent_activity', [])
                print(f"   Recent activity entries: {len(recent_activity)}")
                if recent_activity:
                    for i, activity in enumerate(recent_activity[:3]):
                        print(f"   Activity {i+1}: {activity.get('action', 'N/A')}")
                
                return True
            else:
                self.log_test(
                    "Admin Dashboard KPIs",
                    False,
                    f"Failed to get dashboard data: HTTP {dashboard_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Dashboard Data",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def compare_dashboard_vs_actual_data(self):
        """Test 5: Compare dashboard figures with actual marketplace data"""
        try:
            print("🔍 COMPARING DASHBOARD VS ACTUAL DATA")
            print("-" * 60)
            
            # Compare users count
            dashboard_users = self.actual_data.get('dashboard_users', 0)
            actual_users = self.actual_data.get('users_count', 0)
            
            users_match = dashboard_users == actual_users
            self.log_test(
                "Users Count Comparison",
                users_match,
                f"Dashboard: {dashboard_users}, Actual: {actual_users}",
                str(actual_users),
                str(dashboard_users)
            )
            
            # Compare listings count
            dashboard_listings = self.actual_data.get('dashboard_listings', 0)
            actual_listings = self.actual_data.get('listings_count', 0)
            listings_total = self.actual_data.get('listings_total', 0)
            
            listings_match = dashboard_listings == actual_listings or dashboard_listings == listings_total
            self.log_test(
                "Listings Count Comparison",
                listings_match,
                f"Dashboard: {dashboard_listings}, Actual from /api/listings: {actual_listings}, API total: {listings_total}",
                str(max(actual_listings, listings_total)),
                str(dashboard_listings)
            )
            
            # Compare active listings
            dashboard_active = self.actual_data.get('dashboard_active_listings', 0)
            browse_active = self.actual_data.get('active_listings_from_browse', 0)
            
            active_match = dashboard_active == browse_active
            self.log_test(
                "Active Listings Comparison",
                active_match,
                f"Dashboard: {dashboard_active}, Browse endpoint: {browse_active}",
                str(browse_active),
                str(dashboard_active)
            )
            
            # Compare revenue
            dashboard_revenue = self.actual_data.get('dashboard_revenue', 0)
            actual_deal_revenue = self.actual_data.get('actual_deal_revenue', 0)
            potential_revenue = self.actual_data.get('potential_revenue', 0)
            
            revenue_reasonable = dashboard_revenue <= potential_revenue
            self.log_test(
                "Revenue Comparison",
                revenue_reasonable,
                f"Dashboard: €{dashboard_revenue}, Actual deals: €{actual_deal_revenue}, Potential: €{potential_revenue}",
                f"≤ €{potential_revenue}",
                f"€{dashboard_revenue}"
            )
            
            # Summary of discrepancies
            discrepancies = []
            if not users_match:
                discrepancies.append(f"Users: Dashboard shows {dashboard_users}, actual is {actual_users}")
            if not listings_match:
                discrepancies.append(f"Listings: Dashboard shows {dashboard_listings}, actual is {actual_listings}")
            if not active_match:
                discrepancies.append(f"Active listings: Dashboard shows {dashboard_active}, browse shows {browse_active}")
            if not revenue_reasonable:
                discrepancies.append(f"Revenue: Dashboard shows €{dashboard_revenue}, but potential is only €{potential_revenue}")
            
            if discrepancies:
                print("\n❌ DATA DISCREPANCIES FOUND:")
                for discrepancy in discrepancies:
                    print(f"   • {discrepancy}")
            else:
                print("\n✅ ALL DATA MATCHES BETWEEN DASHBOARD AND ACTUAL SOURCES")
            
            return len(discrepancies) == 0
            
        except Exception as e:
            self.log_test(
                "Dashboard vs Actual Data Comparison",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def identify_data_source_issues(self):
        """Test 6: Identify which collections the dashboard should be reading from"""
        try:
            print("🔍 IDENTIFYING DATA SOURCE ISSUES")
            print("-" * 60)
            
            print("DASHBOARD DATA SOURCES ANALYSIS:")
            print(f"• Users collection (/api/admin/users): {self.actual_data.get('users_count', 0)} documents")
            print(f"• Listings collection (/api/listings): {self.actual_data.get('listings_count', 0)} documents")
            print(f"• Browse endpoint active listings: {self.actual_data.get('active_listings_from_browse', 0)} active")
            print(f"• User deals found: {self.actual_data.get('user_deals_count', 0)} deals")
            print(f"• Completed deals revenue: €{self.actual_data.get('actual_deal_revenue', 0)}")
            
            print("\nDASHBOARD REPORTED VALUES:")
            print(f"• Total users: {self.actual_data.get('dashboard_users', 0)}")
            print(f"• Total listings: {self.actual_data.get('dashboard_listings', 0)}")
            print(f"• Active listings: {self.actual_data.get('dashboard_active_listings', 0)}")
            print(f"• Total deals: {self.actual_data.get('dashboard_deals', 0)}")
            print(f"• Revenue: €{self.actual_data.get('dashboard_revenue', 0)}")
            print(f"• Growth rate: {self.actual_data.get('dashboard_growth', 0)}%")
            
            # Recommendations
            print("\nRECOMMENDATIONS:")
            
            dashboard_users = self.actual_data.get('dashboard_users', 0)
            actual_users = self.actual_data.get('users_count', 0)
            if dashboard_users != actual_users:
                print(f"• Users count mismatch: Dashboard uses db.users.count_documents({{}}), should return {actual_users}")
            
            dashboard_listings = self.actual_data.get('dashboard_listings', 0)
            actual_listings = self.actual_data.get('listings_count', 0)
            if dashboard_listings != actual_listings:
                print(f"• Listings count mismatch: Dashboard uses db.listings.count_documents({{}}), should return {actual_listings}")
            
            dashboard_revenue = self.actual_data.get('dashboard_revenue', 0)
            if dashboard_revenue > 0:
                print(f"• Revenue calculation: Dashboard shows €{dashboard_revenue}, verify if this comes from real completed transactions")
            
            self.log_test(
                "Data Source Issues Identification",
                True,
                "Analysis completed - see recommendations above"
            )
            
            return True
            
        except Exception as e:
            self.log_test(
                "Data Source Issues Identification",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all dashboard data accuracy debug tests"""
        print("=" * 80)
        print("DASHBOARD DATA ACCURACY DEBUG TESTING")
        print("Investigating dashboard inflated numbers vs reality")
        print("=" * 80)
        print()
        
        # Test 1: Check database collections and counts
        test1_success = self.test_database_collections_count()
        
        # Test 2: Check marketplace browse endpoint
        test2_success = self.test_marketplace_browse_endpoint()
        
        # Test 3: Check deals and transactions
        test3_success = self.test_deals_and_transactions()
        
        # Test 4: Get admin dashboard data
        test4_success = self.test_admin_dashboard_data()
        
        # Test 5: Compare dashboard vs actual data
        test5_success = self.compare_dashboard_vs_actual_data()
        
        # Test 6: Identify data source issues
        test6_success = self.identify_data_source_issues()
        
        # Summary
        print("\n" + "=" * 80)
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
            ("Database Collections Count", test1_success),
            ("Marketplace Browse Analysis", test2_success),
            ("Deals and Transactions", test3_success),
            ("Admin Dashboard Data", test4_success),
            ("Dashboard vs Actual Comparison", test5_success),
            ("Data Source Issues Identification", test6_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        
        # Final analysis
        if test5_success:
            print("✅ DASHBOARD DATA ACCURACY: All figures match actual marketplace data")
        else:
            print("❌ DASHBOARD DATA ACCURACY ISSUE CONFIRMED: Dashboard shows inflated numbers")
            print("\nROOT CAUSE ANALYSIS:")
            print("The dashboard endpoint /api/admin/dashboard is calculating KPIs that don't match")
            print("the actual marketplace data available through other endpoints.")
            print("\nNEXT STEPS:")
            print("1. Review the dashboard calculation logic in backend/server.py")
            print("2. Ensure dashboard queries match the same collections used by marketplace endpoints")
            print("3. Verify that test/dummy data isn't being included in dashboard calculations")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    debugger = DashboardDataDebugger()
    success = debugger.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - Dashboard data accuracy verified!")
        sys.exit(0)
    else:
        print("\n⚠️  DASHBOARD DATA ACCURACY ISSUES FOUND - Check analysis above")
        sys.exit(1)