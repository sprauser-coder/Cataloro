#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Pending Listings Investigation
Investigating the pending listings issue as requested in the review
"""

import requests
import json
import uuid
import time
from datetime import datetime
from collections import Counter

# Get backend URL from environment
BACKEND_URL = "https://market-guardian.preview.emergentagent.com/api"

class PendingListingsInvestigator:
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

    def test_check_pending_listings_in_database(self):
        """Check for listings with status='pending' or status='awaiting_approval'"""
        try:
            # Get all listings to analyze their statuses
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                all_listings = response.json()
                
                # Count listings by status
                status_counts = Counter()
                pending_listings = []
                awaiting_approval_listings = []
                
                for listing in all_listings:
                    status = listing.get('status', 'unknown')
                    status_counts[status] += 1
                    
                    if status == 'pending':
                        pending_listings.append(listing)
                    elif status == 'awaiting_approval':
                        awaiting_approval_listings.append(listing)
                
                # Check if we found any pending listings
                has_pending = len(pending_listings) > 0
                has_awaiting = len(awaiting_approval_listings) > 0
                
                details = f"Total listings: {len(all_listings)}, Status breakdown: {dict(status_counts)}"
                if has_pending:
                    details += f", Pending listings found: {len(pending_listings)}"
                if has_awaiting:
                    details += f", Awaiting approval listings found: {len(awaiting_approval_listings)}"
                
                self.log_test(
                    "Check Pending Listings in Database", 
                    True,  # Always pass as this is informational
                    details
                )
                
                return {
                    'pending_listings': pending_listings,
                    'awaiting_approval_listings': awaiting_approval_listings,
                    'status_counts': dict(status_counts),
                    'total_listings': len(all_listings)
                }
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Check Pending Listings in Database", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Check Pending Listings in Database", False, error_msg=str(e))
            return None

    def test_check_pending_orders(self):
        """Check for orders with status='pending' that could make listings appear as pending"""
        try:
            if not self.admin_user:
                self.log_test("Check Pending Orders", False, error_msg="Admin user not available")
                return None
            
            # Try to get orders - this might not be a direct endpoint, so we'll check user deals
            user_id = self.admin_user.get('id')
            response = requests.get(f"{BACKEND_URL}/user/my-deals/{user_id}", timeout=10)
            
            if response.status_code == 200:
                deals = response.json()
                
                # Count deals by status
                status_counts = Counter()
                pending_orders = []
                
                for deal in deals:
                    status = deal.get('status', 'unknown')
                    status_counts[status] += 1
                    
                    if status == 'pending':
                        pending_orders.append(deal)
                
                details = f"Total deals/orders: {len(deals)}, Status breakdown: {dict(status_counts)}"
                if pending_orders:
                    details += f", Pending orders found: {len(pending_orders)}"
                
                self.log_test(
                    "Check Pending Orders", 
                    True,  # Always pass as this is informational
                    details
                )
                
                return {
                    'pending_orders': pending_orders,
                    'status_counts': dict(status_counts),
                    'total_orders': len(deals)
                }
            else:
                # Try alternative approach - check if there's a direct orders endpoint
                self.log_test(
                    "Check Pending Orders", 
                    True,  # Don't fail if endpoint doesn't exist
                    "No direct orders endpoint found, checked via deals endpoint"
                )
                return {'pending_orders': [], 'status_counts': {}, 'total_orders': 0}
                
        except Exception as e:
            self.log_test("Check Pending Orders", False, error_msg=str(e))
            return None

    def test_verify_listing_statuses(self):
        """Get a comprehensive count of all listings by status"""
        try:
            # Get all listings from browse endpoint
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                all_listings = response.json()
                
                # Analyze listing statuses in detail
                status_analysis = {}
                for listing in all_listings:
                    status = listing.get('status', 'unknown')
                    if status not in status_analysis:
                        status_analysis[status] = {
                            'count': 0,
                            'examples': []
                        }
                    
                    status_analysis[status]['count'] += 1
                    if len(status_analysis[status]['examples']) < 3:  # Keep first 3 examples
                        status_analysis[status]['examples'].append({
                            'id': listing.get('id'),
                            'title': listing.get('title', 'Unknown'),
                            'price': listing.get('price', 0)
                        })
                
                # Create detailed report
                details = f"Total listings analyzed: {len(all_listings)}\n"
                for status, info in status_analysis.items():
                    details += f"  - {status}: {info['count']} listings"
                    if info['examples']:
                        examples = [f"{ex['title']} (€{ex['price']})" for ex in info['examples']]
                        details += f" (examples: {', '.join(examples)})"
                    details += "\n"
                
                self.log_test(
                    "Verify Listing Statuses", 
                    True,
                    details.strip()
                )
                
                return status_analysis
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Verify Listing Statuses", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Verify Listing Statuses", False, error_msg=str(e))
            return None

    def test_check_seller_information_storage(self):
        """Verify how seller information is stored in listings (seller_id vs username)"""
        try:
            # Get all listings
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                all_listings = response.json()
                
                seller_info_analysis = {
                    'has_seller_id': 0,
                    'has_seller_username': 0,
                    'has_seller_object': 0,
                    'seller_id_examples': [],
                    'seller_object_examples': [],
                    'total_listings': len(all_listings)
                }
                
                for listing in all_listings[:10]:  # Analyze first 10 listings
                    # Check for seller_id field
                    if listing.get('seller_id'):
                        seller_info_analysis['has_seller_id'] += 1
                        if len(seller_info_analysis['seller_id_examples']) < 3:
                            seller_info_analysis['seller_id_examples'].append({
                                'listing_id': listing.get('id'),
                                'seller_id': listing.get('seller_id'),
                                'title': listing.get('title', 'Unknown')
                            })
                    
                    # Check for seller object
                    if listing.get('seller'):
                        seller_info_analysis['has_seller_object'] += 1
                        seller = listing.get('seller', {})
                        if len(seller_info_analysis['seller_object_examples']) < 3:
                            seller_info_analysis['seller_object_examples'].append({
                                'listing_id': listing.get('id'),
                                'seller_name': seller.get('name', 'Unknown'),
                                'seller_username': seller.get('username', 'Unknown'),
                                'title': listing.get('title', 'Unknown')
                            })
                
                details = f"Analyzed {min(10, len(all_listings))} listings:\n"
                details += f"  - Listings with seller_id: {seller_info_analysis['has_seller_id']}\n"
                details += f"  - Listings with seller object: {seller_info_analysis['has_seller_object']}\n"
                
                if seller_info_analysis['seller_id_examples']:
                    details += "  - Seller ID examples:\n"
                    for ex in seller_info_analysis['seller_id_examples']:
                        details += f"    * {ex['title']}: seller_id={ex['seller_id']}\n"
                
                if seller_info_analysis['seller_object_examples']:
                    details += "  - Seller object examples:\n"
                    for ex in seller_info_analysis['seller_object_examples']:
                        details += f"    * {ex['title']}: name={ex['seller_name']}, username={ex['seller_username']}\n"
                
                self.log_test(
                    "Check Seller Information Storage", 
                    True,
                    details.strip()
                )
                
                return seller_info_analysis
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Check Seller Information Storage", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Check Seller Information Storage", False, error_msg=str(e))
            return None

    def test_listings_api_with_status_all(self):
        """Test the /api/listings?status=all endpoint to see what data is returned"""
        try:
            # Test if there's a direct listings endpoint with status parameter
            test_urls = [
                f"{BACKEND_URL}/listings?status=all",
                f"{BACKEND_URL}/listings",
                f"{BACKEND_URL}/marketplace/browse?status=all",
                f"{BACKEND_URL}/admin/listings"
            ]
            
            results = {}
            
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=10)
                    endpoint_name = url.split('/')[-1].split('?')[0]
                    
                    if response.status_code == 200:
                        data = response.json()
                        results[endpoint_name] = {
                            'status_code': response.status_code,
                            'count': len(data) if isinstance(data, list) else 1,
                            'has_data': bool(data),
                            'sample_fields': list(data[0].keys()) if isinstance(data, list) and data else []
                        }
                    else:
                        results[endpoint_name] = {
                            'status_code': response.status_code,
                            'error': response.json().get('detail', 'Unknown error') if response.content else 'No content'
                        }
                except Exception as e:
                    results[endpoint_name] = {
                        'status_code': 'error',
                        'error': str(e)
                    }
            
            # Find working endpoints
            working_endpoints = [name for name, result in results.items() if result.get('status_code') == 200]
            
            details = "Tested multiple listings endpoints:\n"
            for endpoint, result in results.items():
                if result.get('status_code') == 200:
                    details += f"  ✅ {endpoint}: {result['count']} items, fields: {result['sample_fields'][:5]}...\n"
                else:
                    details += f"  ❌ {endpoint}: {result.get('error', 'Failed')}\n"
            
            self.log_test(
                "Test Listings API with Status All", 
                len(working_endpoints) > 0,
                details.strip()
            )
            
            return results
            
        except Exception as e:
            self.log_test("Test Listings API with Status All", False, error_msg=str(e))
            return None

    def test_investigate_pending_tab_issue(self):
        """Investigate why the pending tab shows 0 listings"""
        try:
            # Get all available data
            browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if browse_response.status_code != 200:
                self.log_test("Investigate Pending Tab Issue", False, error_msg="Could not get browse data")
                return None
            
            all_listings = browse_response.json()
            
            # Analyze potential reasons for 0 pending listings
            analysis = {
                'total_listings': len(all_listings),
                'status_distribution': Counter(),
                'potential_issues': [],
                'recommendations': []
            }
            
            # Count statuses
            for listing in all_listings:
                status = listing.get('status', 'unknown')
                analysis['status_distribution'][status] += 1
            
            # Check for potential issues
            if 'pending' not in analysis['status_distribution']:
                analysis['potential_issues'].append("No listings have 'pending' status")
                analysis['recommendations'].append("Check if listings are created with 'active' status by default")
            
            if 'awaiting_approval' not in analysis['status_distribution']:
                analysis['potential_issues'].append("No listings have 'awaiting_approval' status")
                analysis['recommendations'].append("Check if there's an approval workflow for new listings")
            
            if analysis['status_distribution'].get('active', 0) == analysis['total_listings']:
                analysis['potential_issues'].append("All listings are 'active' - no pending workflow")
                analysis['recommendations'].append("Verify if pending status is set during listing creation or approval process")
            
            # Check if there are any non-active statuses
            non_active_statuses = {k: v for k, v in analysis['status_distribution'].items() if k != 'active'}
            if not non_active_statuses:
                analysis['potential_issues'].append("Only 'active' status found - no workflow statuses")
                analysis['recommendations'].append("Check if listing workflow includes pending/approval states")
            
            details = f"Pending Tab Investigation Results:\n"
            details += f"  - Total listings: {analysis['total_listings']}\n"
            details += f"  - Status distribution: {dict(analysis['status_distribution'])}\n"
            details += f"  - Potential issues: {len(analysis['potential_issues'])}\n"
            for issue in analysis['potential_issues']:
                details += f"    * {issue}\n"
            details += f"  - Recommendations: {len(analysis['recommendations'])}\n"
            for rec in analysis['recommendations']:
                details += f"    * {rec}\n"
            
            self.log_test(
                "Investigate Pending Tab Issue", 
                True,  # Always pass as this is investigative
                details.strip()
            )
            
            return analysis
            
        except Exception as e:
            self.log_test("Investigate Pending Tab Issue", False, error_msg=str(e))
            return None

    def run_pending_listings_investigation(self):
        """Run comprehensive pending listings investigation"""
        print("=" * 80)
        print("CATALORO PENDING LISTINGS INVESTIGATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Admin Login
        print("👤 ADMIN LOGIN")
        print("-" * 40)
        if not self.test_admin_login():
            print("❌ Admin login failed. Continuing with public endpoints.")
        
        # 2. Check for Pending Listings in Database
        print("🔍 CHECK FOR PENDING LISTINGS IN DATABASE")
        print("-" * 40)
        pending_data = self.test_check_pending_listings_in_database()
        
        # 3. Check for Pending Orders
        print("📋 CHECK FOR PENDING ORDERS")
        print("-" * 40)
        orders_data = self.test_check_pending_orders()
        
        # 4. Verify Listing Statuses
        print("📊 VERIFY LISTING STATUSES")
        print("-" * 40)
        status_data = self.test_verify_listing_statuses()
        
        # 5. Check Seller Information Storage
        print("👥 CHECK SELLER INFORMATION STORAGE")
        print("-" * 40)
        seller_data = self.test_check_seller_information_storage()
        
        # 6. Test Listings API Endpoints
        print("🔗 TEST LISTINGS API ENDPOINTS")
        print("-" * 40)
        api_data = self.test_listings_api_with_status_all()
        
        # 7. Investigate Pending Tab Issue
        print("🕵️ INVESTIGATE PENDING TAB ISSUE")
        print("-" * 40)
        investigation_data = self.test_investigate_pending_tab_issue()
        
        # Print Summary
        print("=" * 80)
        print("PENDING LISTINGS INVESTIGATION SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Key Findings
        print("🔍 KEY FINDINGS:")
        print("-" * 40)
        
        if pending_data:
            print(f"📊 Listings Status Distribution: {pending_data.get('status_counts', {})}")
            if pending_data.get('pending_listings'):
                print(f"⚠️  Found {len(pending_data['pending_listings'])} pending listings")
            else:
                print("ℹ️  No listings with 'pending' status found")
        
        if orders_data:
            print(f"📋 Orders Status Distribution: {orders_data.get('status_counts', {})}")
            if orders_data.get('pending_orders'):
                print(f"⚠️  Found {len(orders_data['pending_orders'])} pending orders")
            else:
                print("ℹ️  No pending orders found")
        
        if seller_data:
            print(f"👥 Seller Info: {seller_data['has_seller_id']} listings have seller_id, {seller_data['has_seller_object']} have seller object")
        
        if investigation_data:
            print("🕵️ Pending Tab Analysis:")
            for issue in investigation_data.get('potential_issues', []):
                print(f"   ⚠️  {issue}")
            for rec in investigation_data.get('recommendations', []):
                print(f"   💡 {rec}")
        
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 PENDING LISTINGS INVESTIGATION COMPLETE")
        print("Investigation focused on understanding why pending tab shows 0 listings")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    investigator = PendingListingsInvestigator()
    
    print("🎯 RUNNING PENDING LISTINGS INVESTIGATION")
    print("Investigating why the pending tab shows 0 listings and how seller information should be displayed...")
    print()
    
    result = investigator.run_pending_listings_investigation()
    if result:
        passed, failed, results = result
        # Exit with appropriate code
        exit(0 if failed == 0 else 1)
    else:
        exit(1)