#!/usr/bin/env python3
"""
MANAGEMENT CENTER SELL FIXES TESTING
Testing the critical API fixes implemented for Management Center Sell
Verifying seller-specific endpoints, status filtering, and pagination functionality
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://marketplace-debug-3.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "demo@cataloro.com"
DEMO_USER_ID = "68bfff790e4e46bc28d43631"

class ManagementCenterSellFixesTester:
    """
    URGENT: Test Management Center Sell fixes implementation
    Testing the critical fixes for seller-specific endpoints, status filtering, and pagination
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.test_results = {}
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
            if headers:
                request_kwargs['headers'] = headers
            
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **request_kwargs) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "response_time_ms": response_time_ms,
                    "data": response_data,
                    "status": response.status
                }
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time_ms,
                "error": str(e),
                "status": 0
            }
    
    async def authenticate_users(self) -> bool:
        """Authenticate both admin and demo users"""
        print("🔐 Authenticating users for Management Center Sell testing...")
        
        # Authenticate admin
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            print(f"  ✅ Admin authentication successful")
        else:
            print(f"  ❌ Admin authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
        
        # Authenticate demo user
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": "demo_password"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            print(f"  ✅ Demo user authentication successful")
            return True
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error', 'Unknown error')}")
            return False
    
    async def test_seller_specific_endpoints(self) -> Dict:
        """
        Test the new seller-specific endpoints that Management Center Sell depends on:
        - /api/marketplace/seller/{id}/listings
        - /api/marketplace/my-listings  
        - /api/marketplace/seller/{id}/dashboard
        """
        print("🏪 Testing seller-specific endpoints...")
        
        if not self.demo_token:
            return {"test_name": "Seller-Specific Endpoints", "error": "No demo token available"}
        
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        endpoint_results = {
            "seller_listings": {"working": False, "count": 0, "error": None, "response_time": 0},
            "my_listings": {"working": False, "count": 0, "error": None, "response_time": 0},
            "seller_dashboard": {"working": False, "data": None, "error": None, "response_time": 0},
            "total_endpoints": 3,
            "working_endpoints": 0
        }
        
        # Get demo user profile to get seller ID
        demo_profile_result = await self.make_request(f"/auth/profile/{DEMO_USER_ID}")
        if not demo_profile_result["success"]:
            return {
                "test_name": "Seller-Specific Endpoints",
                "success": False,
                "error": "Failed to get demo user profile"
            }
        
        demo_user = demo_profile_result["data"]
        seller_id = demo_user.get("id")
        
        # 1. Test /api/marketplace/seller/{id}/listings
        print("  📋 Testing seller listings endpoint...")
        seller_listings_result = await self.make_request(f"/marketplace/seller/{seller_id}/listings", headers=headers)
        
        if seller_listings_result["success"]:
            seller_listings = seller_listings_result.get("data", [])
            endpoint_results["seller_listings"]["working"] = True
            endpoint_results["seller_listings"]["count"] = len(seller_listings)
            endpoint_results["seller_listings"]["response_time"] = seller_listings_result["response_time_ms"]
            endpoint_results["working_endpoints"] += 1
            print(f"    ✅ Seller listings endpoint working: {len(seller_listings)} listings found")
        else:
            endpoint_results["seller_listings"]["error"] = seller_listings_result.get("error", f"Status {seller_listings_result.get('status', 'unknown')}")
            print(f"    ❌ Seller listings endpoint failed: {endpoint_results['seller_listings']['error']}")
        
        # 2. Test /api/marketplace/my-listings
        print("  📝 Testing my listings endpoint...")
        my_listings_result = await self.make_request("/marketplace/my-listings", headers=headers)
        
        if my_listings_result["success"]:
            my_listings = my_listings_result.get("data", [])
            endpoint_results["my_listings"]["working"] = True
            endpoint_results["my_listings"]["count"] = len(my_listings)
            endpoint_results["my_listings"]["response_time"] = my_listings_result["response_time_ms"]
            endpoint_results["working_endpoints"] += 1
            print(f"    ✅ My listings endpoint working: {len(my_listings)} listings found")
        else:
            endpoint_results["my_listings"]["error"] = my_listings_result.get("error", f"Status {my_listings_result.get('status', 'unknown')}")
            print(f"    ❌ My listings endpoint failed: {endpoint_results['my_listings']['error']}")
        
        # 3. Test /api/marketplace/seller/{id}/dashboard
        print("  📊 Testing seller dashboard endpoint...")
        seller_dashboard_result = await self.make_request(f"/marketplace/seller/{seller_id}/dashboard", headers=headers)
        
        if seller_dashboard_result["success"]:
            dashboard_data = seller_dashboard_result.get("data", {})
            endpoint_results["seller_dashboard"]["working"] = True
            endpoint_results["seller_dashboard"]["data"] = dashboard_data
            endpoint_results["seller_dashboard"]["response_time"] = seller_dashboard_result["response_time_ms"]
            endpoint_results["working_endpoints"] += 1
            print(f"    ✅ Seller dashboard endpoint working: {type(dashboard_data).__name__} data returned")
        else:
            endpoint_results["seller_dashboard"]["error"] = seller_dashboard_result.get("error", f"Status {seller_dashboard_result.get('status', 'unknown')}")
            print(f"    ❌ Seller dashboard endpoint failed: {endpoint_results['seller_dashboard']['error']}")
        
        success_rate = (endpoint_results["working_endpoints"] / endpoint_results["total_endpoints"]) * 100
        overall_success = endpoint_results["working_endpoints"] == endpoint_results["total_endpoints"]
        
        print(f"  📊 Seller-specific endpoints test complete:")
        print(f"    - Working endpoints: {endpoint_results['working_endpoints']}/{endpoint_results['total_endpoints']}")
        print(f"    - Success rate: {success_rate:.1f}%")
        
        return {
            "test_name": "Seller-Specific Endpoints",
            "success": overall_success,
            "endpoint_results": endpoint_results,
            "success_rate": success_rate,
            "seller_id": seller_id,
            "critical_issues": [
                endpoint for endpoint, data in endpoint_results.items() 
                if isinstance(data, dict) and not data.get("working", True) and endpoint not in ["total_endpoints", "working_endpoints"]
            ]
        }
    
    async def test_status_filtering_improvements(self) -> Dict:
        """
        Test the improved status filtering functionality:
        - /api/marketplace/search?status=active/pending/expired/all
        - /api/marketplace/browse?status=all
        """
        print("🔍 Testing status filtering improvements...")
        
        status_results = {
            "active_filter": {"working": False, "count": 0, "error": None},
            "pending_filter": {"working": False, "count": 0, "error": None},
            "expired_filter": {"working": False, "count": 0, "error": None},
            "all_filter": {"working": False, "count": 0, "error": None},
            "browse_all_filter": {"working": False, "count": 0, "error": None},
            "total_filters": 5,
            "working_filters": 0
        }
        
        # Test different status filters
        status_filters = [
            ("active", "active_filter"),
            ("pending", "pending_filter"), 
            ("expired", "expired_filter"),
            ("all", "all_filter")
        ]
        
        for status, result_key in status_filters:
            print(f"  🔍 Testing search with status={status}...")
            search_result = await self.make_request("/marketplace/search", params={"status": status})
            
            if search_result["success"]:
                search_data = search_result.get("data", {})
                
                # Handle different response formats
                if isinstance(search_data, dict):
                    listings = search_data.get("results", [])
                    total = search_data.get("total", len(listings))
                else:
                    listings = search_data if isinstance(search_data, list) else []
                    total = len(listings)
                
                status_results[result_key]["working"] = True
                status_results[result_key]["count"] = total
                status_results["working_filters"] += 1
                print(f"    ✅ Status {status} filter working: {total} listings found")
            else:
                status_results[result_key]["error"] = search_result.get("error", f"Status {search_result.get('status', 'unknown')}")
                print(f"    ❌ Status {status} filter failed: {status_results[result_key]['error']}")
        
        # Test browse with status=all (should return all 12 listings from database)
        print("  📋 Testing browse with status=all...")
        browse_all_result = await self.make_request("/marketplace/browse", params={"status": "all"})
        
        if browse_all_result["success"]:
            browse_listings = browse_all_result.get("data", [])
            status_results["browse_all_filter"]["working"] = True
            status_results["browse_all_filter"]["count"] = len(browse_listings)
            status_results["working_filters"] += 1
            print(f"    ✅ Browse status=all working: {len(browse_listings)} listings found")
            
            # Check if we're getting all 12 listings as expected
            if len(browse_listings) == 12:
                print(f"    ✅ All 12 listings from database are now accessible!")
            elif len(browse_listings) > 0:
                print(f"    ⚠️ Found {len(browse_listings)} listings, expected 12 from database")
            else:
                print(f"    ❌ No listings returned with status=all")
        else:
            status_results["browse_all_filter"]["error"] = browse_all_result.get("error", f"Status {browse_all_result.get('status', 'unknown')}")
            print(f"    ❌ Browse status=all failed: {status_results['browse_all_filter']['error']}")
        
        success_rate = (status_results["working_filters"] / status_results["total_filters"]) * 100
        overall_success = status_results["working_filters"] >= 4  # At least 4/5 filters working
        
        print(f"  📊 Status filtering test complete:")
        print(f"    - Working filters: {status_results['working_filters']}/{status_results['total_filters']}")
        print(f"    - Success rate: {success_rate:.1f}%")
        
        return {
            "test_name": "Status Filtering Improvements",
            "success": overall_success,
            "status_results": status_results,
            "success_rate": success_rate,
            "all_listings_accessible": status_results["browse_all_filter"]["count"] >= 12,
            "critical_issues": [
                filter_name for filter_name, data in status_results.items() 
                if isinstance(data, dict) and not data.get("working", True) and filter_name not in ["total_filters", "working_filters"]
            ]
        }
    
    async def test_pagination_functionality(self) -> Dict:
        """
        Test pagination functionality to ensure different pages return different results
        """
        print("📄 Testing pagination functionality...")
        
        pagination_results = {
            "page1_working": False,
            "page2_working": False,
            "different_results": False,
            "page1_count": 0,
            "page2_count": 0,
            "overlap_count": 0,
            "total_unique_items": 0
        }
        
        # Test page 1
        print("  📄 Testing page 1...")
        page1_result = await self.make_request("/marketplace/browse", params={"page": 1, "limit": 5})
        
        if page1_result["success"]:
            page1_data = page1_result.get("data", [])
            pagination_results["page1_working"] = True
            pagination_results["page1_count"] = len(page1_data)
            print(f"    ✅ Page 1 working: {len(page1_data)} listings")
        else:
            print(f"    ❌ Page 1 failed: {page1_result.get('error', 'Unknown error')}")
        
        # Test page 2
        print("  📄 Testing page 2...")
        page2_result = await self.make_request("/marketplace/browse", params={"page": 2, "limit": 5})
        
        if page2_result["success"]:
            page2_data = page2_result.get("data", [])
            pagination_results["page2_working"] = True
            pagination_results["page2_count"] = len(page2_data)
            print(f"    ✅ Page 2 working: {len(page2_data)} listings")
        else:
            print(f"    ❌ Page 2 failed: {page2_result.get('error', 'Unknown error')}")
        
        # Check if pagination returns different results
        if pagination_results["page1_working"] and pagination_results["page2_working"]:
            page1_data = page1_result.get("data", [])
            page2_data = page2_result.get("data", [])
            
            # Get IDs from both pages
            page1_ids = [item.get("id") for item in page1_data if isinstance(item, dict) and item.get("id")]
            page2_ids = [item.get("id") for item in page2_data if isinstance(item, dict) and item.get("id")]
            
            # Check for overlap
            overlap = set(page1_ids) & set(page2_ids)
            pagination_results["overlap_count"] = len(overlap)
            pagination_results["different_results"] = len(overlap) == 0  # No overlap means pagination working
            pagination_results["total_unique_items"] = len(set(page1_ids) | set(page2_ids))
            
            if pagination_results["different_results"]:
                print(f"    ✅ Pagination working correctly: no overlap between pages")
            else:
                print(f"    ⚠️ Pagination issue: {len(overlap)} items overlap between pages")
        
        overall_success = (
            pagination_results["page1_working"] and 
            pagination_results["page2_working"] and 
            pagination_results["different_results"]
        )
        
        print(f"  📊 Pagination test complete:")
        print(f"    - Page 1 working: {pagination_results['page1_working']}")
        print(f"    - Page 2 working: {pagination_results['page2_working']}")
        print(f"    - Different results: {pagination_results['different_results']}")
        print(f"    - Total unique items: {pagination_results['total_unique_items']}")
        
        return {
            "test_name": "Pagination Functionality",
            "success": overall_success,
            "pagination_results": pagination_results,
            "pagination_working": pagination_results["different_results"]
        }
    
    async def test_database_listings_accessibility(self) -> Dict:
        """
        Verify that all 12 listings from database are now accessible through the APIs
        """
        print("🗄️ Testing database listings accessibility...")
        
        if not self.admin_token:
            return {"test_name": "Database Listings Accessibility", "error": "No admin token available"}
        
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        accessibility_results = {
            "database_total": 0,
            "browse_api_count": 0,
            "search_api_count": 0,
            "all_listings_accessible": False,
            "missing_listings": 0
        }
        
        # Get database total from admin performance endpoint
        print("  📊 Getting database total from admin performance endpoint...")
        perf_result = await self.make_request("/admin/performance", headers=admin_headers)
        
        if perf_result["success"]:
            perf_data = perf_result.get("data", {})
            collections_stats = perf_data.get("collections", {})
            if "listings" in collections_stats:
                accessibility_results["database_total"] = collections_stats["listings"].get("document_count", 0)
                print(f"    Database total listings: {accessibility_results['database_total']}")
            else:
                print("    ⚠️ No listings collection stats found in performance endpoint")
        else:
            print(f"    ❌ Performance endpoint failed: {perf_result.get('error', 'Unknown error')}")
        
        # Get browse API count with status=all
        print("  📋 Getting browse API count with status=all...")
        browse_result = await self.make_request("/marketplace/browse", params={"status": "all"})
        
        if browse_result["success"]:
            browse_listings = browse_result.get("data", [])
            accessibility_results["browse_api_count"] = len(browse_listings)
            print(f"    Browse API count: {accessibility_results['browse_api_count']}")
        else:
            print(f"    ❌ Browse API failed: {browse_result.get('error', 'Unknown error')}")
        
        # Get search API count with status=all
        print("  🔍 Getting search API count with status=all...")
        search_result = await self.make_request("/marketplace/search", params={"status": "all", "limit": 50})
        
        if search_result["success"]:
            search_data = search_result.get("data", {})
            if isinstance(search_data, dict):
                search_listings = search_data.get("results", [])
                total_reported = search_data.get("total", len(search_listings))
            else:
                search_listings = search_data if isinstance(search_data, list) else []
                total_reported = len(search_listings)
            
            accessibility_results["search_api_count"] = total_reported
            print(f"    Search API count: {accessibility_results['search_api_count']}")
        else:
            print(f"    ❌ Search API failed: {search_result.get('error', 'Unknown error')}")
        
        # Check if all listings are accessible
        if accessibility_results["database_total"] > 0:
            accessibility_results["missing_listings"] = max(0, accessibility_results["database_total"] - accessibility_results["browse_api_count"])
            accessibility_results["all_listings_accessible"] = accessibility_results["missing_listings"] == 0
        
        print(f"  📊 Database accessibility test complete:")
        print(f"    - Database total: {accessibility_results['database_total']}")
        print(f"    - Browse API accessible: {accessibility_results['browse_api_count']}")
        print(f"    - Search API accessible: {accessibility_results['search_api_count']}")
        print(f"    - Missing listings: {accessibility_results['missing_listings']}")
        print(f"    - All listings accessible: {accessibility_results['all_listings_accessible']}")
        
        return {
            "test_name": "Database Listings Accessibility",
            "success": accessibility_results["all_listings_accessible"],
            "accessibility_results": accessibility_results,
            "database_api_discrepancy": accessibility_results["missing_listings"] > 0
        }
    
    async def test_authentication_with_both_tokens(self) -> Dict:
        """
        Test that both admin and demo user tokens work with the APIs
        """
        print("🔐 Testing authentication with both admin and demo tokens...")
        
        auth_results = {
            "admin_token_working": False,
            "demo_token_working": False,
            "admin_endpoints_accessible": 0,
            "demo_endpoints_accessible": 0
        }
        
        # Test admin token
        if self.admin_token:
            print("  🔑 Testing admin token...")
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test admin-specific endpoint
            admin_perf_result = await self.make_request("/admin/performance", headers=admin_headers)
            if admin_perf_result["success"]:
                auth_results["admin_token_working"] = True
                auth_results["admin_endpoints_accessible"] += 1
                print("    ✅ Admin token working with admin endpoints")
            
            # Test general endpoint with admin token
            admin_browse_result = await self.make_request("/marketplace/browse", headers=admin_headers)
            if admin_browse_result["success"]:
                auth_results["admin_endpoints_accessible"] += 1
                print("    ✅ Admin token working with general endpoints")
        
        # Test demo token
        if self.demo_token:
            print("  👤 Testing demo token...")
            demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
            
            # Test seller-specific endpoint
            demo_listings_result = await self.make_request("/marketplace/my-listings", headers=demo_headers)
            if demo_listings_result["success"]:
                auth_results["demo_token_working"] = True
                auth_results["demo_endpoints_accessible"] += 1
                print("    ✅ Demo token working with seller endpoints")
            
            # Test general endpoint with demo token
            demo_browse_result = await self.make_request("/marketplace/browse", headers=demo_headers)
            if demo_browse_result["success"]:
                auth_results["demo_endpoints_accessible"] += 1
                print("    ✅ Demo token working with general endpoints")
        
        overall_success = auth_results["admin_token_working"] and auth_results["demo_token_working"]
        
        print(f"  📊 Authentication test complete:")
        print(f"    - Admin token working: {auth_results['admin_token_working']}")
        print(f"    - Demo token working: {auth_results['demo_token_working']}")
        print(f"    - Admin endpoints accessible: {auth_results['admin_endpoints_accessible']}")
        print(f"    - Demo endpoints accessible: {auth_results['demo_endpoints_accessible']}")
        
        return {
            "test_name": "Authentication with Both Tokens",
            "success": overall_success,
            "auth_results": auth_results
        }
    
    async def run_management_center_sell_fixes_test(self) -> Dict:
        """
        Run complete Management Center Sell fixes testing
        """
        print("🚨 STARTING MANAGEMENT CENTER SELL FIXES TESTING")
        print("=" * 80)
        print("TESTING: Critical API fixes for Management Center Sell functionality")
        print("ENDPOINTS: Seller-specific endpoints, status filtering, pagination")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_users()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "User authentication failed - cannot proceed with testing"
                }
            
            # Run all tests
            seller_endpoints_test = await self.test_seller_specific_endpoints()
            status_filtering_test = await self.test_status_filtering_improvements()
            pagination_test = await self.test_pagination_functionality()
            database_accessibility_test = await self.test_database_listings_accessibility()
            authentication_test = await self.test_authentication_with_both_tokens()
            
            # Compile comprehensive test results
            test_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Management Center Sell fixes verification",
                "seller_endpoints_test": seller_endpoints_test,
                "status_filtering_test": status_filtering_test,
                "pagination_test": pagination_test,
                "database_accessibility_test": database_accessibility_test,
                "authentication_test": authentication_test
            }
            
            # Determine overall success and critical findings
            critical_issues = []
            successful_tests = 0
            total_tests = 5
            
            if seller_endpoints_test.get("success", False):
                successful_tests += 1
            else:
                critical_issues.append("Seller-specific endpoints not working properly")
            
            if status_filtering_test.get("success", False):
                successful_tests += 1
            else:
                critical_issues.append("Status filtering improvements not working")
            
            if pagination_test.get("success", False):
                successful_tests += 1
            else:
                critical_issues.append("Pagination functionality not working")
            
            if database_accessibility_test.get("success", False):
                successful_tests += 1
            else:
                critical_issues.append("Not all database listings are accessible")
            
            if authentication_test.get("success", False):
                successful_tests += 1
            else:
                critical_issues.append("Authentication issues with admin/demo tokens")
            
            # Calculate success rate
            success_rate = (successful_tests / total_tests) * 100
            overall_success = success_rate >= 80  # At least 80% of tests passing
            
            test_results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate,
                "overall_success": overall_success,
                "critical_issues": critical_issues,
                "management_center_sell_ready": (
                    seller_endpoints_test.get("success", False) and
                    status_filtering_test.get("success", False) and
                    database_accessibility_test.get("success", False)
                ),
                "fixes_verification_status": "PASSED" if overall_success else "FAILED"
            }
            
            return test_results
            
        finally:
            await self.cleanup()


async def main():
    """Main function to run the Management Center Sell fixes testing"""
    tester = ManagementCenterSellFixesTester()
    
    try:
        results = await tester.run_management_center_sell_fixes_test()
        
        print("\n" + "=" * 80)
        print("🚨 MANAGEMENT CENTER SELL FIXES TEST RESULTS")
        print("=" * 80)
        
        # Print summary
        summary = results.get("summary", {})
        print(f"📊 OVERALL RESULTS:")
        print(f"   - Total tests: {summary.get('total_tests', 0)}")
        print(f"   - Successful tests: {summary.get('successful_tests', 0)}")
        print(f"   - Success rate: {summary.get('success_rate', 0):.1f}%")
        print(f"   - Overall success: {summary.get('overall_success', False)}")
        print(f"   - Management Center Sell ready: {summary.get('management_center_sell_ready', False)}")
        print(f"   - Fixes verification: {summary.get('fixes_verification_status', 'UNKNOWN')}")
        
        # Print critical issues
        critical_issues = summary.get("critical_issues", [])
        if critical_issues:
            print(f"\n❌ CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES FOUND")
        
        # Print detailed results for each test
        print(f"\n📋 DETAILED TEST RESULTS:")
        
        for test_key, test_result in results.items():
            if test_key in ["test_timestamp", "test_focus", "summary"]:
                continue
                
            if isinstance(test_result, dict):
                test_name = test_result.get("test_name", test_key)
                success = test_result.get("success", False)
                status_icon = "✅" if success else "❌"
                print(f"   {status_icon} {test_name}: {'PASSED' if success else 'FAILED'}")
                
                # Print specific details for failed tests
                if not success:
                    if "critical_issues" in test_result:
                        issues = test_result["critical_issues"]
                        if issues:
                            print(f"      Issues: {', '.join(issues)}")
                    if "error" in test_result:
                        print(f"      Error: {test_result['error']}")
        
        print("\n" + "=" * 80)
        
        return results
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    asyncio.run(main())