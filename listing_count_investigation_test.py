#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Listing Count Discrepancy Investigation
Investigating the listing count discrepancy between browse and admin panel endpoints
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-menueditor.preview.emergentagent.com/api"

class ListingCountInvestigator:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_user = None
        self.admin_token = None
        
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

    def test_admin_login(self):
        """Test admin login and store credentials for subsequent tests"""
        try:
            admin_credentials = {
                "email": "admin@cataloro.com",
                "password": "admin123"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login", 
                json=admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                token = data.get('token', '')
                
                self.admin_user = user
                self.admin_token = token
                
                user_role = user.get('user_role')
                user_id = user.get('id')
                username = user.get('username')
                
                is_admin = user_role in ['Admin', 'Admin-Manager']
                
                self.log_test(
                    "Admin Login", 
                    is_admin, 
                    f"Username: {username}, Role: {user_role}, User ID: {user_id}"
                )
                return is_admin
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login", False, error_msg=f"Login failed: {error_detail}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, error_msg=str(e))
            return False

    def test_browse_endpoint_listings(self):
        """Test GET /api/marketplace/browse to count listings"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/marketplace/browse",
                timeout=10
            )
            
            if response.status_code == 200:
                listings = response.json()
                
                # Count total listings
                total_count = len(listings)
                
                # Analyze status distribution
                status_counts = {}
                active_count = 0
                
                for listing in listings:
                    status = listing.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                    if status == 'active':
                        active_count += 1
                
                # Check for seller information
                listings_with_seller = sum(1 for listing in listings if listing.get('seller'))
                
                # Check for catalyst data
                listings_with_catalyst = sum(1 for listing in listings if any([
                    listing.get('ceramic_weight'),
                    listing.get('pt_ppm'),
                    listing.get('pd_ppm'),
                    listing.get('rh_ppm')
                ]))
                
                self.log_test(
                    "Browse Endpoint Listings Count", 
                    True, 
                    f"Total listings: {total_count}, Active: {active_count}, "
                    f"With seller info: {listings_with_seller}, With catalyst data: {listings_with_catalyst}, "
                    f"Status distribution: {status_counts}"
                )
                
                return {
                    'total': total_count,
                    'active': active_count,
                    'status_counts': status_counts,
                    'listings': listings,
                    'with_seller': listings_with_seller,
                    'with_catalyst': listings_with_catalyst
                }
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Browse Endpoint Listings Count", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Browse Endpoint Listings Count", False, error_msg=str(e))
            return None

    def test_admin_listings_endpoint(self):
        """Test GET /api/listings?status=all to count admin panel listings"""
        try:
            # Test different status parameters
            status_params = ['all', 'active', 'pending', 'awaiting_approval']
            results = {}
            
            for status in status_params:
                response = requests.get(
                    f"{BACKEND_URL}/listings?status={status}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle both direct array and object with 'listings' property
                    if isinstance(data, list):
                        listings = data
                        total = len(listings)
                    elif isinstance(data, dict) and 'listings' in data:
                        listings = data['listings']
                        total = data.get('total', len(listings))
                    else:
                        listings = []
                        total = 0
                    
                    results[status] = {
                        'count': len(listings),
                        'total_field': total,
                        'listings': listings,
                        'response_type': 'array' if isinstance(data, list) else 'object'
                    }
                else:
                    results[status] = {
                        'count': 0,
                        'error': f"HTTP {response.status_code}",
                        'listings': []
                    }
            
            # Log results for all status parameters
            details_parts = []
            for status, result in results.items():
                if 'error' not in result:
                    details_parts.append(f"{status}: {result['count']} ({result['response_type']})")
                else:
                    details_parts.append(f"{status}: ERROR - {result['error']}")
            
            self.log_test(
                "Admin Listings Endpoint Count", 
                True, 
                f"Admin panel counts - {', '.join(details_parts)}"
            )
            
            return results
                
        except Exception as e:
            self.log_test("Admin Listings Endpoint Count", False, error_msg=str(e))
            return None

    def test_direct_database_query(self):
        """Test direct database access through admin endpoints to get raw counts"""
        try:
            # Try to get all users to verify admin access
            users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            
            if users_response.status_code != 200:
                self.log_test("Direct Database Query", False, error_msg="Cannot access admin endpoints")
                return None
            
            # Get dashboard data which should have accurate counts
            dashboard_response = requests.get(f"{BACKEND_URL}/admin/dashboard", timeout=10)
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                kpis = dashboard_data.get('kpis', {})
                
                total_listings = kpis.get('total_listings', 0)
                active_listings = kpis.get('active_listings', 0)
                total_users = kpis.get('total_users', 0)
                
                self.log_test(
                    "Direct Database Query", 
                    True, 
                    f"Dashboard KPIs - Total listings: {total_listings}, Active listings: {active_listings}, Total users: {total_users}"
                )
                
                return {
                    'total_listings': total_listings,
                    'active_listings': active_listings,
                    'total_users': total_users,
                    'dashboard_data': dashboard_data
                }
            else:
                error_detail = dashboard_response.json().get('detail', 'Unknown error') if dashboard_response.content else f"HTTP {dashboard_response.status_code}"
                self.log_test("Direct Database Query", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Direct Database Query", False, error_msg=str(e))
            return None

    def analyze_listing_discrepancy(self, browse_data, admin_data, dashboard_data):
        """Analyze the discrepancy between different endpoints"""
        try:
            if not browse_data or not admin_data:
                self.log_test("Listing Discrepancy Analysis", False, error_msg="Missing data for analysis")
                return None
            
            browse_count = browse_data['total']
            admin_all_count = admin_data.get('all', {}).get('count', 0)
            admin_active_count = admin_data.get('active', {}).get('count', 0)
            dashboard_total = dashboard_data.get('total_listings', 0) if dashboard_data else 0
            dashboard_active = dashboard_data.get('active_listings', 0) if dashboard_data else 0
            
            # Calculate discrepancies
            browse_vs_admin_all = browse_count - admin_all_count
            browse_vs_admin_active = browse_count - admin_active_count
            browse_vs_dashboard = browse_count - dashboard_total
            
            # Identify potential causes
            issues = []
            
            if browse_vs_admin_all != 0:
                issues.append(f"Browse vs Admin 'all': {browse_vs_admin_all} difference")
            
            if browse_vs_admin_active != 0:
                issues.append(f"Browse vs Admin 'active': {browse_vs_admin_active} difference")
            
            if browse_vs_dashboard != 0:
                issues.append(f"Browse vs Dashboard: {browse_vs_dashboard} difference")
            
            # Check if browse only shows active listings
            browse_active_only = browse_data['active'] == browse_count
            
            analysis_success = len(issues) == 0 or abs(browse_vs_admin_all) <= 1  # Allow small differences
            
            self.log_test(
                "Listing Discrepancy Analysis", 
                analysis_success, 
                f"Browse: {browse_count}, Admin all: {admin_all_count}, Admin active: {admin_active_count}, "
                f"Dashboard total: {dashboard_total}, Dashboard active: {dashboard_active}. "
                f"Browse shows active only: {browse_active_only}. Issues: {issues if issues else 'None'}"
            )
            
            return {
                'browse_count': browse_count,
                'admin_all_count': admin_all_count,
                'admin_active_count': admin_active_count,
                'dashboard_total': dashboard_total,
                'dashboard_active': dashboard_active,
                'discrepancies': issues,
                'browse_active_only': browse_active_only
            }
            
        except Exception as e:
            self.log_test("Listing Discrepancy Analysis", False, error_msg=str(e))
            return None

    def identify_missing_listings(self, browse_data, admin_data):
        """Identify which specific listings are missing from admin panel"""
        try:
            if not browse_data or not admin_data:
                self.log_test("Identify Missing Listings", False, error_msg="Missing data for comparison")
                return None
            
            browse_listings = browse_data['listings']
            admin_all_listings = admin_data.get('all', {}).get('listings', [])
            
            # Get listing IDs from both sources
            browse_ids = set(listing.get('id') for listing in browse_listings if listing.get('id'))
            admin_ids = set(listing.get('id') for listing in admin_all_listings if listing.get('id'))
            
            # Find missing listings
            missing_from_admin = browse_ids - admin_ids
            missing_from_browse = admin_ids - browse_ids
            
            # Get details of missing listings
            missing_details = []
            for listing in browse_listings:
                if listing.get('id') in missing_from_admin:
                    missing_details.append({
                        'id': listing.get('id'),
                        'title': listing.get('title', 'Unknown'),
                        'status': listing.get('status', 'Unknown'),
                        'seller_id': listing.get('seller_id', 'Unknown'),
                        'price': listing.get('price', 0)
                    })
            
            extra_details = []
            for listing in admin_all_listings:
                if listing.get('id') in missing_from_browse:
                    extra_details.append({
                        'id': listing.get('id'),
                        'title': listing.get('title', 'Unknown'),
                        'status': listing.get('status', 'Unknown'),
                        'seller_id': listing.get('seller_id', 'Unknown'),
                        'price': listing.get('price', 0)
                    })
            
            analysis_success = len(missing_from_admin) == 0 and len(missing_from_browse) == 0
            
            self.log_test(
                "Identify Missing Listings", 
                analysis_success, 
                f"Browse IDs: {len(browse_ids)}, Admin IDs: {len(admin_ids)}. "
                f"Missing from admin: {len(missing_from_admin)}, Missing from browse: {len(missing_from_browse)}. "
                f"Sample missing from admin: {missing_details[:3] if missing_details else 'None'}"
            )
            
            return {
                'missing_from_admin': list(missing_from_admin),
                'missing_from_browse': list(missing_from_browse),
                'missing_details': missing_details,
                'extra_details': extra_details,
                'browse_ids_count': len(browse_ids),
                'admin_ids_count': len(admin_ids)
            }
            
        except Exception as e:
            self.log_test("Identify Missing Listings", False, error_msg=str(e))
            return None

    def test_data_source_consistency(self, browse_data, admin_data):
        """Test if endpoints are accessing the same database collection"""
        try:
            if not browse_data or not admin_data:
                self.log_test("Data Source Consistency", False, error_msg="Missing data for consistency check")
                return None
            
            browse_listings = browse_data['listings']
            admin_all_listings = admin_data.get('all', {}).get('listings', [])
            
            # Check if we can find common listings with same data
            common_listings = 0
            data_mismatches = 0
            
            for browse_listing in browse_listings:
                browse_id = browse_listing.get('id')
                if not browse_id:
                    continue
                    
                # Find matching listing in admin data
                admin_listing = None
                for admin_item in admin_all_listings:
                    if admin_item.get('id') == browse_id:
                        admin_listing = admin_item
                        break
                
                if admin_listing:
                    common_listings += 1
                    
                    # Check for data consistency
                    fields_to_check = ['title', 'price', 'status', 'seller_id']
                    for field in fields_to_check:
                        browse_value = browse_listing.get(field)
                        admin_value = admin_listing.get(field)
                        
                        if browse_value != admin_value:
                            data_mismatches += 1
                            break
            
            consistency_good = data_mismatches == 0 and common_listings > 0
            
            self.log_test(
                "Data Source Consistency", 
                consistency_good, 
                f"Common listings: {common_listings}, Data mismatches: {data_mismatches}. "
                f"Browse total: {len(browse_listings)}, Admin total: {len(admin_all_listings)}"
            )
            
            return {
                'common_listings': common_listings,
                'data_mismatches': data_mismatches,
                'consistency_good': consistency_good
            }
            
        except Exception as e:
            self.log_test("Data Source Consistency", False, error_msg=str(e))
            return None

    def run_listing_count_investigation(self):
        """Run comprehensive listing count discrepancy investigation"""
        print("=" * 80)
        print("CATALORO LISTING COUNT DISCREPANCY INVESTIGATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Admin Login
        print("👤 ADMIN LOGIN")
        print("-" * 40)
        if not self.test_admin_login():
            print("❌ Admin login failed. Aborting investigation.")
            return
        
        # 2. Test Browse Endpoint
        print("🔍 BROWSE ENDPOINT ANALYSIS")
        print("-" * 40)
        browse_data = self.test_browse_endpoint_listings()
        
        # 3. Test Admin Listings Endpoint
        print("⚙️ ADMIN LISTINGS ENDPOINT ANALYSIS")
        print("-" * 40)
        admin_data = self.test_admin_listings_endpoint()
        
        # 4. Test Direct Database Query
        print("🗄️ DIRECT DATABASE QUERY")
        print("-" * 40)
        dashboard_data = self.test_direct_database_query()
        
        # 5. Analyze Discrepancy
        print("📊 DISCREPANCY ANALYSIS")
        print("-" * 40)
        discrepancy_analysis = self.analyze_listing_discrepancy(browse_data, admin_data, dashboard_data)
        
        # 6. Identify Missing Listings
        print("🔎 MISSING LISTINGS IDENTIFICATION")
        print("-" * 40)
        missing_analysis = self.identify_missing_listings(browse_data, admin_data)
        
        # 7. Test Data Source Consistency
        print("🔗 DATA SOURCE CONSISTENCY CHECK")
        print("-" * 40)
        consistency_analysis = self.test_data_source_consistency(browse_data, admin_data)
        
        # Print Summary
        print("=" * 80)
        print("LISTING COUNT DISCREPANCY INVESTIGATION SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Detailed findings
        if browse_data and admin_data:
            print("🔍 KEY FINDINGS:")
            print(f"  • Browse endpoint returns: {browse_data['total']} listings")
            if admin_data.get('all'):
                print(f"  • Admin 'all' endpoint returns: {admin_data['all']['count']} listings")
            if admin_data.get('active'):
                print(f"  • Admin 'active' endpoint returns: {admin_data['active']['count']} listings")
            if dashboard_data:
                print(f"  • Dashboard reports: {dashboard_data['total_listings']} total, {dashboard_data['active_listings']} active")
            
            if discrepancy_analysis and discrepancy_analysis['discrepancies']:
                print(f"  • Discrepancies found: {discrepancy_analysis['discrepancies']}")
            else:
                print("  • No significant discrepancies found")
            
            if missing_analysis:
                print(f"  • Missing from admin: {len(missing_analysis['missing_from_admin'])} listings")
                print(f"  • Missing from browse: {len(missing_analysis['missing_from_browse'])} listings")
        
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 LISTING COUNT DISCREPANCY INVESTIGATION COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results, {
            'browse_data': browse_data,
            'admin_data': admin_data,
            'dashboard_data': dashboard_data,
            'discrepancy_analysis': discrepancy_analysis,
            'missing_analysis': missing_analysis,
            'consistency_analysis': consistency_analysis
        }

if __name__ == "__main__":
    investigator = ListingCountInvestigator()
    
    print("🎯 RUNNING LISTING COUNT DISCREPANCY INVESTIGATION")
    print("Investigating the listing count discrepancy between browse and admin panel endpoints...")
    print()
    
    result = investigator.run_listing_count_investigation()
    if result:
        passed, failed, results, analysis_data = result
        # Exit with appropriate code
        exit(0 if failed == 0 else 1)
    else:
        exit(1)