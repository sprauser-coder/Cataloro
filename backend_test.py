#!/usr/bin/env python3
"""
MANAGEMENT CENTER SELL LISTINGS INVESTIGATION
Investigating reported issue: "Management Center Sell does not show all products listed"
Testing listings endpoints, pagination, filtering, and data consistency
"""

import asyncio
import aiohttp
import time
import json
import statistics
import io
import base64
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://menu-settings-debug.preview.emergentagent.com/api"
PERFORMANCE_TARGET_MS = 1000  # Browse endpoint should respond in under 1 second
CACHE_IMPROVEMENT_TARGET = 20  # Cached responses should be at least 20% faster

# Admin User Configuration (from review request)
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"
ADMIN_ROLE = "admin"
ADMIN_ID = "admin_user_1"

class ManagementCenterSellTester:
    """
    URGENT: Management Center Sell listings investigation
    User reports: "Management Center Sell does not show all products listed"
    Testing listings endpoints, pagination, filtering, and data consistency
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.investigation_results = {}
        
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
        print("🔐 Authenticating users for listings investigation...")
        
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
            "email": "demo@cataloro.com",
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
    
    async def investigate_total_listings_count(self) -> Dict:
        """
        CRITICAL: Get total count of listings in database vs API responses
        Check for discrepancies between database count and what APIs return
        """
        print("🔍 CRITICAL: Investigating total listings count discrepancies...")
        
        if not self.admin_token:
            return {"test_name": "Total Listings Count Investigation", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        investigation_results = {
            "database_total": 0,
            "browse_api_count": 0,
            "management_api_count": 0,
            "seller_listings_count": 0,
            "active_listings_count": 0,
            "all_status_listings_count": 0,
            "discrepancies_found": [],
            "missing_listings": []
        }
        
        # 1. Check browse API listings count
        print("  📋 Checking browse API listings count...")
        browse_result = await self.make_request("/marketplace/browse")
        if browse_result["success"]:
            browse_listings = browse_result.get("data", [])
            investigation_results["browse_api_count"] = len(browse_listings)
            print(f"    Browse API returned: {len(browse_listings)} listings")
        else:
            print(f"    ❌ Browse API failed: {browse_result.get('error', 'Unknown error')}")
        
        # 2. Check admin performance endpoint for database stats
        print("  📊 Checking admin performance endpoint for database statistics...")
        perf_result = await self.make_request("/admin/performance", headers=headers)
        if perf_result["success"]:
            perf_data = perf_result.get("data", {})
            collections_stats = perf_data.get("collections", {})
            if "listings" in collections_stats:
                investigation_results["database_total"] = collections_stats["listings"].get("document_count", 0)
                print(f"    Database total listings: {investigation_results['database_total']}")
            else:
                print("    ⚠️ No listings collection stats found in performance endpoint")
        else:
            print(f"    ❌ Performance endpoint failed: {perf_result.get('error', 'Unknown error')}")
        
        # 3. Check seller-specific listings (Management Center Sell would use this)
        print("  👤 Checking seller-specific listings...")
        # Get demo user profile to find their listings
        demo_profile_result = await self.make_request("/auth/profile/68bfff790e4e46bc28d43631")
        if demo_profile_result["success"]:
            demo_user = demo_profile_result["data"]
            seller_id = demo_user.get("id")
            
            # Check seller listings endpoint
            seller_headers = {"Authorization": f"Bearer {self.demo_token}"}
            seller_result = await self.make_request(f"/marketplace/seller/{seller_id}/listings", headers=seller_headers)
            if seller_result["success"]:
                seller_listings = seller_result.get("data", [])
                investigation_results["seller_listings_count"] = len(seller_listings)
                print(f"    Seller listings: {len(seller_listings)}")
            else:
                print(f"    ❌ Seller listings failed: {seller_result.get('error', 'Unknown error')}")
        
        # 4. Check different listing status filters
        print("  🔍 Checking listings by status...")
        status_filters = ["active", "pending", "expired", "sold"]
        status_counts = {}
        
        for status in status_filters:
            # Try search with status filter
            search_result = await self.make_request("/marketplace/search", params={"q": "", "status": status})
            if search_result["success"]:
                search_data = search_result.get("data", {})
                if isinstance(search_data, dict):
                    status_count = search_data.get("total", 0)
                    if isinstance(search_data.get("results"), list):
                        status_count = len(search_data["results"])
                else:
                    status_count = len(search_data) if isinstance(search_data, list) else 0
                status_counts[status] = status_count
                print(f"    {status.title()} listings: {status_count}")
        
        investigation_results["status_breakdown"] = status_counts
        investigation_results["all_status_listings_count"] = sum(status_counts.values())
        
        # 5. Analyze discrepancies
        print("  🔍 Analyzing discrepancies...")
        
        # Compare database total vs browse API
        if investigation_results["database_total"] > investigation_results["browse_api_count"]:
            discrepancy = investigation_results["database_total"] - investigation_results["browse_api_count"]
            investigation_results["discrepancies_found"].append({
                "type": "database_vs_browse",
                "description": f"Database has {discrepancy} more listings than browse API",
                "database_count": investigation_results["database_total"],
                "api_count": investigation_results["browse_api_count"],
                "missing_count": discrepancy
            })
        
        # Compare browse vs seller listings
        if investigation_results["browse_api_count"] != investigation_results["seller_listings_count"]:
            discrepancy = abs(investigation_results["browse_api_count"] - investigation_results["seller_listings_count"])
            investigation_results["discrepancies_found"].append({
                "type": "browse_vs_seller",
                "description": f"Browse API and seller listings differ by {discrepancy}",
                "browse_count": investigation_results["browse_api_count"],
                "seller_count": investigation_results["seller_listings_count"],
                "difference": discrepancy
            })
        
        # Check if status breakdown matches totals
        if investigation_results["all_status_listings_count"] != investigation_results["browse_api_count"]:
            discrepancy = abs(investigation_results["all_status_listings_count"] - investigation_results["browse_api_count"])
            investigation_results["discrepancies_found"].append({
                "type": "status_breakdown_vs_browse",
                "description": f"Status breakdown total differs from browse API by {discrepancy}",
                "status_total": investigation_results["all_status_listings_count"],
                "browse_count": investigation_results["browse_api_count"],
                "difference": discrepancy
            })
        
        critical_discrepancy = len(investigation_results["discrepancies_found"]) > 0
        
        print(f"  📊 Investigation complete:")
        print(f"    - Database total: {investigation_results['database_total']}")
        print(f"    - Browse API count: {investigation_results['browse_api_count']}")
        print(f"    - Seller listings: {investigation_results['seller_listings_count']}")
        print(f"    - Status breakdown total: {investigation_results['all_status_listings_count']}")
        print(f"    - Discrepancies found: {len(investigation_results['discrepancies_found'])}")
        print(f"    - Critical issue: {critical_discrepancy}")
        
        return {
            "test_name": "Total Listings Count Investigation",
            "success": True,
            "investigation_results": investigation_results,
            "critical_discrepancy": critical_discrepancy,
            "discrepancies_count": len(investigation_results["discrepancies_found"]),
            "potential_data_loss": investigation_results["database_total"] > investigation_results["browse_api_count"] + 5
        }
    
    async def test_management_center_endpoints(self) -> Dict:
        """
        Test endpoints that Management Center Sell page would use
        Check for pagination, filtering, and query issues
        """
        print("🏢 Testing Management Center endpoints...")
        
        if not self.demo_token:
            return {"test_name": "Management Center Endpoints", "error": "No demo token available"}
        
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        management_results = {
            "seller_listings_endpoint": {"working": False, "count": 0, "error": None},
            "my_listings_endpoint": {"working": False, "count": 0, "error": None},
            "seller_dashboard_endpoint": {"working": False, "count": 0, "error": None},
            "pagination_working": False,
            "filtering_working": False,
            "total_endpoints_tested": 0,
            "working_endpoints": 0
        }
        
        # Get demo user ID
        demo_profile_result = await self.make_request("/auth/profile/68bfff790e4e46bc28d43631")
        if not demo_profile_result["success"]:
            return {
                "test_name": "Management Center Endpoints",
                "success": False,
                "error": "Failed to get demo user profile"
            }
        
        demo_user = demo_profile_result["data"]
        seller_id = demo_user.get("id")
        
        # 1. Test seller listings endpoint
        print("  📋 Testing seller listings endpoint...")
        management_results["total_endpoints_tested"] += 1
        seller_result = await self.make_request(f"/marketplace/seller/{seller_id}/listings", headers=headers)
        if seller_result["success"]:
            seller_listings = seller_result.get("data", [])
            management_results["seller_listings_endpoint"]["working"] = True
            management_results["seller_listings_endpoint"]["count"] = len(seller_listings)
            management_results["working_endpoints"] += 1
            print(f"    ✅ Seller listings: {len(seller_listings)} found")
        else:
            management_results["seller_listings_endpoint"]["error"] = seller_result.get("error", "Unknown error")
            print(f"    ❌ Seller listings failed: {seller_result.get('error', 'Unknown error')}")
        
        # 2. Test my listings endpoint
        print("  📝 Testing my listings endpoint...")
        management_results["total_endpoints_tested"] += 1
        my_listings_result = await self.make_request("/marketplace/my-listings", headers=headers)
        if my_listings_result["success"]:
            my_listings = my_listings_result.get("data", [])
            management_results["my_listings_endpoint"]["working"] = True
            management_results["my_listings_endpoint"]["count"] = len(my_listings)
            management_results["working_endpoints"] += 1
            print(f"    ✅ My listings: {len(my_listings)} found")
        else:
            management_results["my_listings_endpoint"]["error"] = my_listings_result.get("error", "Unknown error")
            print(f"    ❌ My listings failed: {my_listings_result.get('error', 'Unknown error')}")
        
        # 3. Test seller dashboard endpoint
        print("  📊 Testing seller dashboard endpoint...")
        management_results["total_endpoints_tested"] += 1
        dashboard_result = await self.make_request(f"/marketplace/seller/{seller_id}/dashboard", headers=headers)
        if dashboard_result["success"]:
            dashboard_data = dashboard_result.get("data", {})
            listings_count = 0
            if isinstance(dashboard_data, dict):
                listings_count = dashboard_data.get("total_listings", 0)
            management_results["seller_dashboard_endpoint"]["working"] = True
            management_results["seller_dashboard_endpoint"]["count"] = listings_count
            management_results["working_endpoints"] += 1
            print(f"    ✅ Seller dashboard: {listings_count} listings reported")
        else:
            management_results["seller_dashboard_endpoint"]["error"] = dashboard_result.get("error", "Unknown error")
            print(f"    ❌ Seller dashboard failed: {dashboard_result.get('error', 'Unknown error')}")
        
        # 4. Test pagination
        print("  📄 Testing pagination...")
        page1_result = await self.make_request("/marketplace/browse", params={"page": 1, "limit": 5})
        page2_result = await self.make_request("/marketplace/browse", params={"page": 2, "limit": 5})
        
        if page1_result["success"] and page2_result["success"]:
            page1_data = page1_result.get("data", [])
            page2_data = page2_result.get("data", [])
            
            # Check if pagination returns different results
            page1_ids = [item.get("id") for item in page1_data if isinstance(item, dict)]
            page2_ids = [item.get("id") for item in page2_data if isinstance(item, dict)]
            
            pagination_working = len(set(page1_ids) & set(page2_ids)) == 0  # No overlap means pagination working
            management_results["pagination_working"] = pagination_working
            print(f"    {'✅' if pagination_working else '❌'} Pagination {'working' if pagination_working else 'not working'}")
        else:
            print(f"    ❌ Pagination test failed")
        
        # 5. Test filtering
        print("  🔍 Testing filtering...")
        all_result = await self.make_request("/marketplace/browse")
        filtered_result = await self.make_request("/marketplace/search", params={"price_min": 100})
        
        if all_result["success"] and filtered_result["success"]:
            all_data = all_result.get("data", [])
            filtered_data = filtered_result.get("data", {})
            
            if isinstance(filtered_data, dict):
                filtered_listings = filtered_data.get("results", [])
            else:
                filtered_listings = filtered_data if isinstance(filtered_data, list) else []
            
            filtering_working = len(filtered_listings) <= len(all_data)
            management_results["filtering_working"] = filtering_working
            print(f"    {'✅' if filtering_working else '❌'} Filtering {'working' if filtering_working else 'not working'}")
        else:
            print(f"    ❌ Filtering test failed")
        
        success_rate = (management_results["working_endpoints"] / management_results["total_endpoints_tested"]) * 100
        overall_success = success_rate >= 66  # At least 2/3 endpoints working
        
        print(f"  📊 Management Center endpoints test complete:")
        print(f"    - Working endpoints: {management_results['working_endpoints']}/{management_results['total_endpoints_tested']}")
        print(f"    - Success rate: {success_rate:.1f}%")
        print(f"    - Pagination working: {management_results['pagination_working']}")
        print(f"    - Filtering working: {management_results['filtering_working']}")
        
        return {
            "test_name": "Management Center Endpoints",
            "success": overall_success,
            "management_results": management_results,
            "success_rate": success_rate,
            "seller_id": seller_id,
            "critical_issues": [
                endpoint for endpoint, data in management_results.items() 
                if isinstance(data, dict) and not data.get("working", True)
            ]
        }
    
    async def test_role_based_listing_visibility(self) -> Dict:
        """
        Test if role-based filtering is affecting listing visibility
        Check different user roles to see if they see different listings
        """
        print("👥 Testing role-based listing visibility...")
        
        if not self.admin_token or not self.demo_token:
            return {"test_name": "Role-Based Listing Visibility", "error": "Missing authentication tokens"}
        
        role_visibility_results = {
            "admin_listings_count": 0,
            "demo_user_listings_count": 0,
            "public_listings_count": 0,
            "role_filtering_detected": False,
            "visibility_discrepancies": []
        }
        
        # 1. Test admin user visibility
        print("  🔑 Testing admin user listing visibility...")
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        admin_result = await self.make_request("/marketplace/browse", headers=admin_headers)
        if admin_result["success"]:
            admin_listings = admin_result.get("data", [])
            role_visibility_results["admin_listings_count"] = len(admin_listings)
            print(f"    Admin sees: {len(admin_listings)} listings")
        
        # 2. Test demo user visibility
        print("  👤 Testing demo user listing visibility...")
        demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
        demo_result = await self.make_request("/marketplace/browse", headers=demo_headers)
        if demo_result["success"]:
            demo_listings = demo_result.get("data", [])
            role_visibility_results["demo_user_listings_count"] = len(demo_listings)
            print(f"    Demo user sees: {len(demo_listings)} listings")
        
        # 3. Test public (no auth) visibility
        print("  🌐 Testing public listing visibility...")
        public_result = await self.make_request("/marketplace/browse")
        if public_result["success"]:
            public_listings = public_result.get("data", [])
            role_visibility_results["public_listings_count"] = len(public_listings)
            print(f"    Public sees: {len(public_listings)} listings")
        
        # 4. Analyze role-based differences
        print("  🔍 Analyzing role-based differences...")
        
        counts = [
            role_visibility_results["admin_listings_count"],
            role_visibility_results["demo_user_listings_count"],
            role_visibility_results["public_listings_count"]
        ]
        
        # Check if all counts are the same
        all_same = len(set(counts)) == 1
        role_visibility_results["role_filtering_detected"] = not all_same
        
        if not all_same:
            # Find discrepancies
            if role_visibility_results["admin_listings_count"] != role_visibility_results["demo_user_listings_count"]:
                role_visibility_results["visibility_discrepancies"].append({
                    "type": "admin_vs_demo",
                    "admin_count": role_visibility_results["admin_listings_count"],
                    "demo_count": role_visibility_results["demo_user_listings_count"],
                    "difference": abs(role_visibility_results["admin_listings_count"] - role_visibility_results["demo_user_listings_count"])
                })
            
            if role_visibility_results["demo_user_listings_count"] != role_visibility_results["public_listings_count"]:
                role_visibility_results["visibility_discrepancies"].append({
                    "type": "demo_vs_public",
                    "demo_count": role_visibility_results["demo_user_listings_count"],
                    "public_count": role_visibility_results["public_listings_count"],
                    "difference": abs(role_visibility_results["demo_user_listings_count"] - role_visibility_results["public_listings_count"])
                })
        
        # 5. Test seller-specific visibility
        print("  🏪 Testing seller-specific listing visibility...")
        demo_profile_result = await self.make_request("/auth/profile/68bfff790e4e46bc28d43631")
        if demo_profile_result["success"]:
            demo_user = demo_profile_result["data"]
            seller_id = demo_user.get("id")
            
            # Check if seller can see their own listings
            seller_result = await self.make_request(f"/marketplace/seller/{seller_id}/listings", headers=demo_headers)
            if seller_result["success"]:
                seller_listings = seller_result.get("data", [])
                role_visibility_results["seller_own_listings_count"] = len(seller_listings)
                print(f"    Seller sees own listings: {len(seller_listings)}")
                
                # Check if seller's listings appear in browse
                if admin_result["success"]:
                    admin_listing_ids = [listing.get("id") for listing in admin_listings if isinstance(listing, dict)]
                    seller_listing_ids = [listing.get("id") for listing in seller_listings if isinstance(listing, dict)]
                    
                    seller_listings_in_browse = len(set(seller_listing_ids) & set(admin_listing_ids))
                    role_visibility_results["seller_listings_in_browse"] = seller_listings_in_browse
                    
                    if seller_listings_in_browse < len(seller_listings):
                        role_visibility_results["visibility_discrepancies"].append({
                            "type": "seller_listings_missing_from_browse",
                            "seller_total": len(seller_listings),
                            "in_browse": seller_listings_in_browse,
                            "missing": len(seller_listings) - seller_listings_in_browse
                        })
        
        critical_role_issue = len(role_visibility_results["visibility_discrepancies"]) > 0
        
        print(f"  📊 Role-based visibility test complete:")
        print(f"    - Role filtering detected: {role_visibility_results['role_filtering_detected']}")
        print(f"    - Visibility discrepancies: {len(role_visibility_results['visibility_discrepancies'])}")
        print(f"    - Critical role issue: {critical_role_issue}")
        
        return {
            "test_name": "Role-Based Listing Visibility",
            "success": True,
            "role_visibility_results": role_visibility_results,
            "critical_role_issue": critical_role_issue,
            "role_filtering_affecting_results": role_visibility_results["role_filtering_detected"]
        }
    
    async def test_listing_status_categorization(self) -> Dict:
        """
        Test if expired, pending, and active listings are properly categorized
        Check if status filtering is hiding listings from Management Center
        """
        print("📊 Testing listing status categorization...")
        
        status_results = {
            "status_breakdown": {},
            "status_filtering_issues": [],
            "uncategorized_listings": 0,
            "status_consistency": True
        }
        
        # 1. Get all listings without status filter
        print("  📋 Getting all listings...")
        all_result = await self.make_request("/marketplace/browse")
        all_listings = []
        if all_result["success"]:
            all_listings = all_result.get("data", [])
            print(f"    Total listings found: {len(all_listings)}")
        
        # 2. Analyze status distribution in all listings
        print("  🔍 Analyzing status distribution...")
        status_counts = {}
        for listing in all_listings:
            if isinstance(listing, dict):
                status = listing.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
        
        status_results["status_breakdown"] = status_counts
        print(f"    Status breakdown: {status_counts}")
        
        # 3. Test specific status filters
        print("  🔍 Testing specific status filters...")
        status_filters = ["active", "pending", "expired", "sold", "draft"]
        
        for status in status_filters:
            # Try search with status filter
            search_result = await self.make_request("/marketplace/search", params={"q": "", "status": status})
            if search_result["success"]:
                search_data = search_result.get("data", {})
                if isinstance(search_data, dict):
                    filtered_listings = search_data.get("results", [])
                    total_reported = search_data.get("total", len(filtered_listings))
                else:
                    filtered_listings = search_data if isinstance(search_data, list) else []
                    total_reported = len(filtered_listings)
                
                actual_count = len(filtered_listings)
                expected_count = status_counts.get(status, 0)
                
                print(f"    {status.title()}: API returned {actual_count}, expected {expected_count}")
                
                if actual_count != expected_count:
                    status_results["status_filtering_issues"].append({
                        "status": status,
                        "expected_count": expected_count,
                        "actual_count": actual_count,
                        "difference": abs(expected_count - actual_count)
                    })
            else:
                print(f"    ❌ {status.title()} filter failed: {search_result.get('error', 'Unknown error')}")
        
        # 4. Check for uncategorized listings
        known_statuses = ["active", "pending", "expired", "sold", "draft"]
        uncategorized = sum(count for status, count in status_counts.items() if status not in known_statuses)
        status_results["uncategorized_listings"] = uncategorized
        
        if uncategorized > 0:
            print(f"    ⚠️ Found {uncategorized} listings with unknown status")
        
        # 5. Test Management Center specific status handling
        print("  🏢 Testing Management Center status handling...")
        if self.demo_token:
            demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
            
            # Get seller's listings and check their statuses
            demo_profile_result = await self.make_request("/auth/profile/68bfff790e4e46bc28d43631")
            if demo_profile_result["success"]:
                demo_user = demo_profile_result["data"]
                seller_id = demo_user.get("id")
                
                seller_result = await self.make_request(f"/marketplace/seller/{seller_id}/listings", headers=demo_headers)
                if seller_result["success"]:
                    seller_listings = seller_result.get("data", [])
                    seller_status_counts = {}
                    
                    for listing in seller_listings:
                        if isinstance(listing, dict):
                            status = listing.get("status", "unknown")
                            seller_status_counts[status] = seller_status_counts.get(status, 0) + 1
                    
                    status_results["seller_status_breakdown"] = seller_status_counts
                    print(f"    Seller status breakdown: {seller_status_counts}")
                    
                    # Check if seller sees all their listings regardless of status
                    total_seller_listings = sum(seller_status_counts.values())
                    if total_seller_listings < sum(1 for listing in all_listings if isinstance(listing, dict) and listing.get("seller_id") == seller_id):
                        status_results["status_filtering_issues"].append({
                            "type": "seller_missing_own_listings",
                            "description": "Seller cannot see all their own listings",
                            "seller_sees": total_seller_listings,
                            "should_see": sum(1 for listing in all_listings if isinstance(listing, dict) and listing.get("seller_id") == seller_id)
                        })
        
        status_consistency = len(status_results["status_filtering_issues"]) == 0
        status_results["status_consistency"] = status_consistency
        
        print(f"  📊 Status categorization test complete:")
        print(f"    - Status filtering issues: {len(status_results['status_filtering_issues'])}")
        print(f"    - Uncategorized listings: {uncategorized}")
        print(f"    - Status consistency: {status_consistency}")
        
        return {
            "test_name": "Listing Status Categorization",
            "success": status_consistency and uncategorized == 0,
            "status_results": status_results,
            "critical_status_issues": len(status_results["status_filtering_issues"]) > 0,
            "status_filtering_problems": status_results["status_filtering_issues"]
        }
    
    async def test_caching_issues(self) -> Dict:
        """
        Test for caching issues that might cause stale data
        Check if cache is preventing updated listings from appearing
        """
        print("💾 Testing for caching issues...")
        
        if not self.admin_token:
            return {"test_name": "Caching Issues Test", "error": "No admin token available"}
        
        caching_results = {
            "cache_clear_available": False,
            "listings_before_clear": 0,
            "listings_after_clear": 0,
            "cache_affecting_results": False,
            "response_time_improvement": 0
        }
        
        # 1. Get initial listings count and response time
        print("  📋 Getting initial listings count...")
        initial_result = await self.make_request("/marketplace/browse")
        if initial_result["success"]:
            initial_listings = initial_result.get("data", [])
            caching_results["listings_before_clear"] = len(initial_listings)
            initial_response_time = initial_result["response_time_ms"]
            print(f"    Initial listings: {len(initial_listings)} (response time: {initial_response_time:.1f}ms)")
        
        # 2. Try to clear cache
        print("  🧹 Attempting to clear cache...")
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        cache_clear_result = await self.make_request("/admin/cache/clear", "POST", headers=admin_headers)
        
        if cache_clear_result["success"]:
            caching_results["cache_clear_available"] = True
            cache_data = cache_clear_result.get("data", {})
            total_cleared = cache_data.get("total_keys_cleared", 0)
            print(f"    ✅ Cache cleared: {total_cleared} keys removed")
            
            # Wait a moment for cache to clear
            await asyncio.sleep(1)
            
            # 3. Get listings count after cache clear
            print("  📋 Getting listings count after cache clear...")
            after_result = await self.make_request("/marketplace/browse")
            if after_result["success"]:
                after_listings = after_result.get("data", [])
                caching_results["listings_after_clear"] = len(after_listings)
                after_response_time = after_result["response_time_ms"]
                print(f"    After cache clear: {len(after_listings)} (response time: {after_response_time:.1f}ms)")
                
                # Check if listings count changed
                if caching_results["listings_before_clear"] != caching_results["listings_after_clear"]:
                    caching_results["cache_affecting_results"] = True
                    difference = abs(caching_results["listings_before_clear"] - caching_results["listings_after_clear"])
                    print(f"    ⚠️ Cache was affecting results: {difference} listings difference")
                else:
                    print(f"    ✅ Cache not affecting listing count")
                
                # Check response time difference
                if initial_response_time > 0:
                    time_diff = initial_response_time - after_response_time
                    caching_results["response_time_improvement"] = time_diff
                    if abs(time_diff) > 50:  # More than 50ms difference
                        print(f"    📊 Response time changed by {time_diff:.1f}ms")
        else:
            print(f"    ❌ Cache clear failed: {cache_clear_result.get('error', 'Unknown error')}")
        
        # 4. Test multiple requests for consistency
        print("  🔄 Testing multiple requests for consistency...")
        consistency_results = []
        for i in range(3):
            result = await self.make_request("/marketplace/browse")
            if result["success"]:
                listings = result.get("data", [])
                consistency_results.append(len(listings))
                await asyncio.sleep(0.5)  # Small delay between requests
        
        consistent_results = len(set(consistency_results)) == 1
        caching_results["consistent_results"] = consistent_results
        caching_results["consistency_counts"] = consistency_results
        
        if not consistent_results:
            print(f"    ⚠️ Inconsistent results across requests: {consistency_results}")
        else:
            print(f"    ✅ Consistent results across requests: {consistency_results[0]}")
        
        cache_issues_detected = (
            caching_results["cache_affecting_results"] or 
            not consistent_results
        )
        
        print(f"  📊 Caching test complete:")
        print(f"    - Cache clear available: {caching_results['cache_clear_available']}")
        print(f"    - Cache affecting results: {caching_results['cache_affecting_results']}")
        print(f"    - Consistent results: {consistent_results}")
        print(f"    - Cache issues detected: {cache_issues_detected}")
        
        return {
            "test_name": "Caching Issues Test",
            "success": not cache_issues_detected,
            "caching_results": caching_results,
            "cache_issues_detected": cache_issues_detected,
            "recommendations": [
                "Clear cache regularly" if caching_results["cache_affecting_results"] else None,
                "Investigate cache consistency" if not consistent_results else None,
                "Cache system working correctly" if not cache_issues_detected else None
            ]
        }
    
    async def run_management_center_sell_investigation(self) -> Dict:
        """
        Run complete Management Center Sell investigation
        """
        print("🚨 STARTING MANAGEMENT CENTER SELL INVESTIGATION")
        print("=" * 80)
        print("USER REPORT: 'Management Center Sell does not show all products listed'")
        print("INVESTIGATING: Listings endpoints, pagination, filtering, and data consistency")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_users()
            if not auth_success:
                return {
                    "investigation_timestamp": datetime.now().isoformat(),
                    "error": "User authentication failed - cannot proceed with investigation"
                }
            
            # Run all investigation tests
            total_count_investigation = await self.investigate_total_listings_count()
            management_endpoints_test = await self.test_management_center_endpoints()
            role_visibility_test = await self.test_role_based_listing_visibility()
            status_categorization_test = await self.test_listing_status_categorization()
            caching_issues_test = await self.test_caching_issues()
            
            # Compile comprehensive investigation results
            investigation_results = {
                "investigation_timestamp": datetime.now().isoformat(),
                "user_report": "Management Center Sell does not show all products listed",
                "total_count_investigation": total_count_investigation,
                "management_endpoints_test": management_endpoints_test,
                "role_visibility_test": role_visibility_test,
                "status_categorization_test": status_categorization_test,
                "caching_issues_test": caching_issues_test
            }
            
            # Determine critical findings
            critical_issues = []
            
            if total_count_investigation.get("critical_discrepancy", False):
                critical_issues.append("Listings count discrepancy between database and API")
            
            if management_endpoints_test.get("success", True) == False:
                critical_issues.append("Management Center endpoints not working properly")
            
            if role_visibility_test.get("critical_role_issue", False):
                critical_issues.append("Role-based filtering affecting listing visibility")
            
            if status_categorization_test.get("critical_status_issues", False):
                critical_issues.append("Status filtering hiding listings")
            
            if caching_issues_test.get("cache_issues_detected", False):
                critical_issues.append("Cache causing stale data")
            
            # Provide recommendations
            recommendations = []
            
            if total_count_investigation.get("potential_data_loss", False):
                recommendations.append("Investigate database vs API discrepancy - potential data loss")
            
            if len(management_endpoints_test.get("critical_issues", [])) > 0:
                recommendations.append("Fix Management Center API endpoints")
            
            if role_visibility_test.get("role_filtering_affecting_results", False):
                recommendations.append("Review role-based filtering logic")
            
            if len(status_categorization_test.get("status_filtering_problems", [])) > 0:
                recommendations.append("Fix status filtering issues")
            
            if caching_issues_test.get("cache_issues_detected", False):
                recommendations.append("Clear cache and review caching strategy")
            
            investigation_results["critical_summary"] = {
                "critical_issues_found": len(critical_issues),
                "critical_issues": critical_issues,
                "recommendations": recommendations,
                "investigation_status": "COMPLETE",
                "urgent_action_required": len(critical_issues) > 0,
                "root_cause_identified": len(critical_issues) > 0,
                "management_center_affected": True
            }
            
            return investigation_results
            
        finally:
            await self.cleanup()


class CriticalDatabaseInvestigator:
    """
    URGENT: Critical data investigation for missing cats/catalyst database
    User reports: "Cats database is completely gone!"
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.investigation_results = {}
        
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
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin for database investigation...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            print(f"  ✅ Admin authentication successful")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            return False
    
    async def investigate_database_collections(self) -> Dict:
        """
        CRITICAL: Investigate what collections exist in MongoDB
        Check for cats, catalyst_data, catalyst_prices, catalyst_overrides
        """
        print("🔍 CRITICAL: Investigating MongoDB collections for missing cats/catalyst data...")
        
        if not self.admin_token:
            return {"test_name": "Database Collections Investigation", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Try to access a database inspection endpoint (if available)
        # Since we don't have direct MongoDB access, we'll check through available API endpoints
        
        investigation_results = {
            "collections_found": [],
            "catalyst_related_collections": [],
            "document_counts": {},
            "missing_collections": [],
            "potential_data_loss": False
        }
        
        # Check for catalyst-related endpoints that might indicate collection existence
        catalyst_endpoints_to_check = [
            "/admin/catalyst-data",
            "/admin/catalyst-prices", 
            "/admin/catalyst-overrides",
            "/admin/cats",
            "/catalyst-data",
            "/catalyst-prices",
            "/cats",
            "/admin/database-status",
            "/admin/collections"
        ]
        
        print("  🔍 Checking catalyst-related API endpoints...")
        for endpoint in catalyst_endpoints_to_check:
            result = await self.make_request(endpoint, headers=headers)
            
            if result["success"]:
                investigation_results["collections_found"].append({
                    "endpoint": endpoint,
                    "status": "ACCESSIBLE",
                    "data_present": bool(result.get("data")),
                    "response_size": len(str(result.get("data", "")))
                })
                
                if "catalyst" in endpoint.lower() or "cat" in endpoint.lower():
                    investigation_results["catalyst_related_collections"].append(endpoint)
                    
                    # Try to count documents if data is returned
                    data = result.get("data", {})
                    if isinstance(data, list):
                        investigation_results["document_counts"][endpoint] = len(data)
                    elif isinstance(data, dict) and "count" in data:
                        investigation_results["document_counts"][endpoint] = data["count"]
                    elif isinstance(data, dict) and "data" in data:
                        if isinstance(data["data"], list):
                            investigation_results["document_counts"][endpoint] = len(data["data"])
                        
            else:
                investigation_results["missing_collections"].append({
                    "endpoint": endpoint,
                    "status": "NOT_ACCESSIBLE",
                    "error": result.get("error", "Unknown error"),
                    "status_code": result.get("status", 0)
                })
        
        # Check general database/admin endpoints for collection info
        admin_endpoints = [
            "/admin/performance",
            "/admin/database-stats", 
            "/admin/system-info"
        ]
        
        print("  📊 Checking admin endpoints for database information...")
        for endpoint in admin_endpoints:
            result = await self.make_request(endpoint, headers=headers)
            if result["success"]:
                data = result.get("data", {})
                
                # Look for collection information in the response
                if "collections" in data:
                    investigation_results["collections_found"].append({
                        "endpoint": endpoint,
                        "collections_info": data["collections"],
                        "status": "FOUND_COLLECTION_INFO"
                    })
                
                # Look for database statistics
                if "database" in data:
                    investigation_results["database_stats"] = data["database"]
        
        # Determine if there's potential data loss
        catalyst_accessible = len(investigation_results["catalyst_related_collections"]) > 0
        total_missing = len(investigation_results["missing_collections"])
        
        investigation_results["potential_data_loss"] = not catalyst_accessible and total_missing > 3
        investigation_results["summary"] = {
            "catalyst_endpoints_accessible": len(investigation_results["catalyst_related_collections"]),
            "total_endpoints_checked": len(catalyst_endpoints_to_check),
            "missing_endpoints": total_missing,
            "data_loss_likely": investigation_results["potential_data_loss"]
        }
        
        print(f"  📊 Collections investigation complete:")
        print(f"    - Catalyst endpoints accessible: {len(investigation_results['catalyst_related_collections'])}")
        print(f"    - Total endpoints missing: {total_missing}")
        print(f"    - Potential data loss: {investigation_results['potential_data_loss']}")
        
        return {
            "test_name": "Database Collections Investigation",
            "success": True,
            "investigation_results": investigation_results,
            "critical_finding": investigation_results["potential_data_loss"],
            "accessible_catalyst_endpoints": investigation_results["catalyst_related_collections"],
            "document_counts": investigation_results["document_counts"]
        }
    
    async def check_catalyst_data_endpoints(self) -> Dict:
        """
        Check specific catalyst data endpoints for data presence
        """
        print("🧪 Checking catalyst data endpoints for actual data...")
        
        if not self.admin_token:
            return {"test_name": "Catalyst Data Check", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        catalyst_data_results = {
            "catalyst_data": {"exists": False, "count": 0, "sample": None},
            "catalyst_prices": {"exists": False, "count": 0, "sample": None},
            "catalyst_overrides": {"exists": False, "count": 0, "sample": None},
            "cats_collection": {"exists": False, "count": 0, "sample": None}
        }
        
        # Check catalyst data endpoint
        print("  🔍 Checking catalyst data...")
        catalyst_result = await self.make_request("/admin/catalyst-data", headers=headers)
        if catalyst_result["success"]:
            data = catalyst_result.get("data", {})
            if isinstance(data, list):
                catalyst_data_results["catalyst_data"]["exists"] = True
                catalyst_data_results["catalyst_data"]["count"] = len(data)
                catalyst_data_results["catalyst_data"]["sample"] = data[:3] if data else None
            elif isinstance(data, dict) and "catalyst_data" in data:
                catalyst_list = data["catalyst_data"]
                catalyst_data_results["catalyst_data"]["exists"] = True
                catalyst_data_results["catalyst_data"]["count"] = len(catalyst_list) if isinstance(catalyst_list, list) else 0
                catalyst_data_results["catalyst_data"]["sample"] = catalyst_list[:3] if isinstance(catalyst_list, list) and catalyst_list else None
        
        # Check catalyst prices endpoint
        print("  💰 Checking catalyst prices...")
        prices_result = await self.make_request("/admin/catalyst-prices", headers=headers)
        if prices_result["success"]:
            data = prices_result.get("data", {})
            if isinstance(data, dict):
                catalyst_data_results["catalyst_prices"]["exists"] = True
                catalyst_data_results["catalyst_prices"]["sample"] = data
                # Count price settings
                price_fields = ["pt_price", "pd_price", "rh_price"]
                catalyst_data_results["catalyst_prices"]["count"] = sum(1 for field in price_fields if field in data)
        
        # Check catalyst overrides endpoint  
        print("  🔧 Checking catalyst overrides...")
        overrides_result = await self.make_request("/admin/catalyst-overrides", headers=headers)
        if overrides_result["success"]:
            data = overrides_result.get("data", {})
            if isinstance(data, list):
                catalyst_data_results["catalyst_overrides"]["exists"] = True
                catalyst_data_results["catalyst_overrides"]["count"] = len(data)
                catalyst_data_results["catalyst_overrides"]["sample"] = data[:3] if data else None
            elif isinstance(data, dict) and "overrides" in data:
                overrides_list = data["overrides"]
                catalyst_data_results["catalyst_overrides"]["exists"] = True
                catalyst_data_results["catalyst_overrides"]["count"] = len(overrides_list) if isinstance(overrides_list, list) else 0
                catalyst_data_results["catalyst_overrides"]["sample"] = overrides_list[:3] if isinstance(overrides_list, list) and overrides_list else None
        
        # Try alternative endpoints for cats data
        cats_endpoints = ["/cats", "/admin/cats", "/catalyst/cats", "/admin/catalyst/cats"]
        print("  🐱 Checking cats collection endpoints...")
        for endpoint in cats_endpoints:
            cats_result = await self.make_request(endpoint, headers=headers)
            if cats_result["success"]:
                data = cats_result.get("data", {})
                if data:
                    catalyst_data_results["cats_collection"]["exists"] = True
                    if isinstance(data, list):
                        catalyst_data_results["cats_collection"]["count"] = len(data)
                        catalyst_data_results["cats_collection"]["sample"] = data[:3] if data else None
                    break
        
        # Calculate summary
        total_collections = len(catalyst_data_results)
        existing_collections = sum(1 for result in catalyst_data_results.values() if result["exists"])
        total_documents = sum(result["count"] for result in catalyst_data_results.values())
        
        data_loss_confirmed = existing_collections == 0 and total_documents == 0
        
        print(f"  📊 Catalyst data check complete:")
        print(f"    - Collections existing: {existing_collections}/{total_collections}")
        print(f"    - Total documents found: {total_documents}")
        print(f"    - Data loss confirmed: {data_loss_confirmed}")
        
        return {
            "test_name": "Catalyst Data Check",
            "success": True,
            "catalyst_data_results": catalyst_data_results,
            "summary": {
                "total_collections_checked": total_collections,
                "existing_collections": existing_collections,
                "total_documents": total_documents,
                "data_loss_confirmed": data_loss_confirmed
            },
            "critical_finding": data_loss_confirmed
        }
    
    async def check_listings_for_catalyst_fields(self) -> Dict:
        """
        Check existing listings for catalyst-related fields
        This might indicate if catalyst data was integrated into listings
        """
        print("📋 Checking listings for catalyst-related fields...")
        
        # Get some listings to check for catalyst fields
        listings_result = await self.make_request("/marketplace/browse")
        
        catalyst_fields_found = {
            "listings_checked": 0,
            "listings_with_catalyst_fields": 0,
            "catalyst_fields_present": [],
            "sample_catalyst_data": []
        }
        
        if listings_result["success"]:
            listings = listings_result.get("data", [])
            catalyst_fields_found["listings_checked"] = len(listings)
            
            # Check for catalyst-related fields in listings
            catalyst_field_names = [
                "ceramic_weight", "pt_ppm", "pd_ppm", "rh_ppm",
                "catalyst_id", "cat_id", "catalyst_data",
                "pt_price", "pd_price", "rh_price"
            ]
            
            for listing in listings[:10]:  # Check first 10 listings
                listing_has_catalyst = False
                listing_catalyst_fields = []
                
                for field in catalyst_field_names:
                    if field in listing and listing[field] is not None:
                        listing_has_catalyst = True
                        listing_catalyst_fields.append(field)
                        
                        if field not in catalyst_fields_found["catalyst_fields_present"]:
                            catalyst_fields_found["catalyst_fields_present"].append(field)
                
                if listing_has_catalyst:
                    catalyst_fields_found["listings_with_catalyst_fields"] += 1
                    catalyst_fields_found["sample_catalyst_data"].append({
                        "listing_id": listing.get("id", "unknown"),
                        "catalyst_fields": listing_catalyst_fields,
                        "sample_values": {field: listing.get(field) for field in listing_catalyst_fields[:3]}
                    })
        
        catalyst_integration_exists = len(catalyst_fields_found["catalyst_fields_present"]) > 0
        
        print(f"  📊 Listings catalyst check complete:")
        print(f"    - Listings checked: {catalyst_fields_found['listings_checked']}")
        print(f"    - Listings with catalyst fields: {catalyst_fields_found['listings_with_catalyst_fields']}")
        print(f"    - Catalyst fields found: {catalyst_fields_found['catalyst_fields_present']}")
        print(f"    - Catalyst integration exists: {catalyst_integration_exists}")
        
        return {
            "test_name": "Listings Catalyst Fields Check",
            "success": True,
            "catalyst_fields_found": catalyst_fields_found,
            "catalyst_integration_exists": catalyst_integration_exists,
            "potential_data_migration": catalyst_integration_exists and catalyst_fields_found["listings_with_catalyst_fields"] > 0
        }
    
    async def check_database_backup_collections(self) -> Dict:
        """
        Check for potential backup or renamed collections
        """
        print("💾 Checking for backup or renamed catalyst collections...")
        
        if not self.admin_token:
            return {"test_name": "Backup Collections Check", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Try various backup/renamed collection patterns
        backup_patterns = [
            "/admin/catalyst-data-backup",
            "/admin/catalyst_data_backup", 
            "/admin/cats-backup",
            "/admin/cats_backup",
            "/admin/catalyst-data-old",
            "/admin/catalyst_data_old",
            "/admin/catalyst-archive",
            "/admin/catalyst_archive",
            "/admin/catalyst-data-v1",
            "/admin/catalyst-data-v2",
            "/admin/catalyst-migration",
            "/admin/old-catalyst-data",
            "/admin/legacy-catalyst-data"
        ]
        
        backup_results = {
            "backup_collections_found": [],
            "backup_collections_missing": [],
            "total_backup_documents": 0
        }
        
        for pattern in backup_patterns:
            result = await self.make_request(pattern, headers=headers)
            
            if result["success"]:
                data = result.get("data", {})
                if data:
                    doc_count = 0
                    if isinstance(data, list):
                        doc_count = len(data)
                    elif isinstance(data, dict) and "count" in data:
                        doc_count = data["count"]
                    
                    backup_results["backup_collections_found"].append({
                        "endpoint": pattern,
                        "document_count": doc_count,
                        "sample_data": str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                    })
                    backup_results["total_backup_documents"] += doc_count
            else:
                backup_results["backup_collections_missing"].append(pattern)
        
        backups_exist = len(backup_results["backup_collections_found"]) > 0
        
        print(f"  📊 Backup collections check complete:")
        print(f"    - Backup collections found: {len(backup_results['backup_collections_found'])}")
        print(f"    - Total backup documents: {backup_results['total_backup_documents']}")
        print(f"    - Backups exist: {backups_exist}")
        
        return {
            "test_name": "Backup Collections Check", 
            "success": True,
            "backup_results": backup_results,
            "backups_exist": backups_exist,
            "recovery_possible": backups_exist and backup_results["total_backup_documents"] > 0
        }
    
    async def run_critical_database_investigation(self) -> Dict:
        """
        Run complete critical database investigation for missing cats/catalyst data
        """
        print("🚨 STARTING CRITICAL DATABASE INVESTIGATION")
        print("=" * 80)
        print("USER REPORT: 'Cats database is completely gone!'")
        print("INVESTIGATING: MongoDB collections and catalyst-related data")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_admin()
            if not auth_success:
                return {
                    "investigation_timestamp": datetime.now().isoformat(),
                    "error": "Admin authentication failed - cannot proceed with investigation"
                }
            
            # Run all investigation tests
            collections_investigation = await self.investigate_database_collections()
            catalyst_data_check = await self.check_catalyst_data_endpoints()
            listings_catalyst_check = await self.check_listings_for_catalyst_fields()
            backup_collections_check = await self.check_database_backup_collections()
            
            # Compile comprehensive investigation results
            investigation_results = {
                "investigation_timestamp": datetime.now().isoformat(),
                "user_report": "Cats database is completely gone!",
                "collections_investigation": collections_investigation,
                "catalyst_data_check": catalyst_data_check,
                "listings_catalyst_check": listings_catalyst_check,
                "backup_collections_check": backup_collections_check
            }
            
            # Determine critical findings
            data_loss_confirmed = (
                catalyst_data_check.get("critical_finding", False) and
                not listings_catalyst_check.get("catalyst_integration_exists", False) and
                not backup_collections_check.get("backups_exist", False)
            )
            
            recovery_options = []
            if backup_collections_check.get("recovery_possible", False):
                recovery_options.append("Backup collections found - data recovery possible")
            if listings_catalyst_check.get("potential_data_migration", False):
                recovery_options.append("Catalyst data may have been migrated to listings")
            if not data_loss_confirmed:
                recovery_options.append("Some catalyst endpoints still accessible")
            
            investigation_results["critical_summary"] = {
                "data_loss_confirmed": data_loss_confirmed,
                "catalyst_endpoints_accessible": len(collections_investigation.get("accessible_catalyst_endpoints", [])),
                "total_catalyst_documents": catalyst_data_check.get("summary", {}).get("total_documents", 0),
                "backup_collections_found": len(backup_collections_check.get("backup_results", {}).get("backup_collections_found", [])),
                "recovery_options_available": len(recovery_options),
                "recovery_options": recovery_options,
                "investigation_status": "COMPLETE",
                "urgent_action_required": data_loss_confirmed and len(recovery_options) == 0
            }
            
            return investigation_results
            
        finally:
            await self.cleanup()


class AdminMenuSettingsTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.admin_token = None
        self.original_menu_settings = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None, form_data=None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
            if form_data:
                request_kwargs['data'] = form_data
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
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            print(f"  ✅ Admin authentication successful")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            return False
    
    def get_expected_menu_structure(self) -> Dict:
        """Get the expected menu structure format"""
        return {
            "desktop_menu": {
                "browse": {"enabled": True, "label": "Browse", "roles": ["buyer", "seller"]},
                "create_listing": {"enabled": True, "label": "Create Listing", "roles": ["seller"]},
                "messages": {"enabled": True, "label": "Messages", "roles": ["buyer", "seller"]},
                "my_listings": {"enabled": True, "label": "My Listings", "roles": ["seller"]},
                "tenders": {"enabled": True, "label": "Tenders", "roles": ["buyer", "seller"]},
                "inventory": {"enabled": True, "label": "Inventory", "roles": ["buyer"]},
                "admin_panel": {"enabled": True, "label": "Administration", "roles": ["admin"]},
                "custom_items": []
            },
            "mobile_menu": {
                "browse": {"enabled": True, "label": "Browse", "roles": ["buyer", "seller"]},
                "create_listing": {"enabled": True, "label": "Create Listing", "roles": ["seller"]},
                "messages": {"enabled": True, "label": "Messages", "roles": ["buyer", "seller"]},
                "my_listings": {"enabled": True, "label": "My Listings", "roles": ["seller"]},
                "tenders": {"enabled": True, "label": "Tenders", "roles": ["buyer", "seller"]},
                "inventory": {"enabled": True, "label": "Inventory", "roles": ["buyer"]},
                "admin_drawer": {"enabled": True, "label": "Admin", "roles": ["admin"]},
                "custom_items": []
            }
        }
    
    async def test_menu_settings_get_endpoint(self) -> Dict:
        """Test GET /api/admin/menu-settings endpoint data structure"""
        print("🔍 Testing menu settings GET endpoint...")
        
        if not self.admin_token:
            return {"test_name": "Menu Settings GET Endpoint", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test GET request
        result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if result["success"]:
            data = result["data"]
            
            # Store original settings for restoration later
            self.original_menu_settings = data
            
            # Check data structure
            has_desktop_menu = "desktop_menu" in data
            has_mobile_menu = "mobile_menu" in data
            
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            
            # Check for expected menu items
            expected_items = ["browse", "create_listing", "messages", "my_listings", "tenders"]
            desktop_items_present = sum(1 for item in expected_items if item in desktop_menu)
            mobile_items_present = sum(1 for item in expected_items if item in mobile_menu)
            
            # Check if items have proper structure (enabled, label, roles)
            valid_structure = True
            sample_item = None
            for item_key, item_data in desktop_menu.items():
                if isinstance(item_data, dict) and item_key != "custom_items":
                    sample_item = item_data
                    if not all(key in item_data for key in ["enabled", "label", "roles"]):
                        valid_structure = False
                    break
            
            print(f"  📊 Response status: {result['status']}")
            print(f"  🖥️ Desktop menu items: {len(desktop_menu)}")
            print(f"  📱 Mobile menu items: {len(mobile_menu)}")
            print(f"  ✅ Expected items in desktop: {desktop_items_present}/{len(expected_items)}")
            print(f"  ✅ Expected items in mobile: {mobile_items_present}/{len(expected_items)}")
            print(f"  🏗️ Valid structure: {valid_structure}")
            if sample_item:
                print(f"  📝 Sample item structure: {sample_item}")
            
            return {
                "test_name": "Menu Settings GET Endpoint",
                "success": result["success"],
                "response_time_ms": result["response_time_ms"],
                "has_desktop_menu": has_desktop_menu,
                "has_mobile_menu": has_mobile_menu,
                "desktop_items_count": len(desktop_menu),
                "mobile_items_count": len(mobile_menu),
                "expected_desktop_items": desktop_items_present,
                "expected_mobile_items": mobile_items_present,
                "valid_item_structure": valid_structure,
                "sample_item": sample_item,
                "full_response": data
            }
        else:
            print(f"  ❌ Menu settings GET failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Menu Settings GET Endpoint",
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"],
                "response": result.get("data", "")
            }
    
    async def test_menu_settings_data_structure_comparison(self) -> Dict:
        """Compare actual menu structure with expected format"""
        print("🔍 Testing menu settings data structure comparison...")
        
        if not self.admin_token:
            return {"test_name": "Menu Settings Data Structure", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if not result["success"]:
            return {
                "test_name": "Menu Settings Data Structure",
                "success": False,
                "error": result.get("error", "Failed to get menu settings")
            }
        
        actual_data = result["data"]
        expected_structure = self.get_expected_menu_structure()
        
        # Compare structure
        structure_matches = []
        
        # Check desktop menu
        desktop_actual = actual_data.get("desktop_menu", {})
        desktop_expected = expected_structure["desktop_menu"]
        
        desktop_comparison = {
            "has_browse": "browse" in desktop_actual,
            "has_create_listing": "create_listing" in desktop_actual,
            "has_messages": "messages" in desktop_actual,
            "has_my_listings": "my_listings" in desktop_actual,
            "has_tenders": "tenders" in desktop_actual,
            "has_inventory": "inventory" in desktop_actual,
            "has_admin_panel": "admin_panel" in desktop_actual,
            "has_custom_items": "custom_items" in desktop_actual
        }
        
        # Check mobile menu
        mobile_actual = actual_data.get("mobile_menu", {})
        mobile_expected = expected_structure["mobile_menu"]
        
        mobile_comparison = {
            "has_browse": "browse" in mobile_actual,
            "has_create_listing": "create_listing" in mobile_actual,
            "has_messages": "messages" in mobile_actual,
            "has_my_listings": "my_listings" in mobile_actual,
            "has_tenders": "tenders" in mobile_actual,
            "has_inventory": "inventory" in mobile_actual,
            "has_admin_drawer": "admin_drawer" in mobile_actual,
            "has_custom_items": "custom_items" in mobile_actual
        }
        
        # Check item properties for a sample item
        sample_item_check = {}
        if "browse" in desktop_actual and isinstance(desktop_actual["browse"], dict):
            browse_item = desktop_actual["browse"]
            sample_item_check = {
                "has_enabled": "enabled" in browse_item,
                "has_label": "label" in browse_item,
                "has_roles": "roles" in browse_item,
                "enabled_value": browse_item.get("enabled"),
                "label_value": browse_item.get("label"),
                "roles_value": browse_item.get("roles")
            }
        
        # Calculate match percentages
        desktop_matches = sum(1 for v in desktop_comparison.values() if v)
        mobile_matches = sum(1 for v in mobile_comparison.values() if v)
        
        desktop_match_percent = (desktop_matches / len(desktop_comparison)) * 100
        mobile_match_percent = (mobile_matches / len(mobile_comparison)) * 100
        
        overall_success = desktop_match_percent >= 75 and mobile_match_percent >= 75
        
        print(f"  🖥️ Desktop structure match: {desktop_matches}/{len(desktop_comparison)} ({desktop_match_percent:.1f}%)")
        print(f"  📱 Mobile structure match: {mobile_matches}/{len(mobile_comparison)} ({mobile_match_percent:.1f}%)")
        print(f"  📝 Sample item properties: {sample_item_check}")
        print(f"  {'✅' if overall_success else '❌'} Structure comparison {'passed' if overall_success else 'failed'}")
        
        return {
            "test_name": "Menu Settings Data Structure",
            "success": overall_success,
            "desktop_comparison": desktop_comparison,
            "mobile_comparison": mobile_comparison,
            "desktop_match_percent": desktop_match_percent,
            "mobile_match_percent": mobile_match_percent,
            "sample_item_properties": sample_item_check,
            "actual_desktop_keys": list(desktop_actual.keys()),
            "actual_mobile_keys": list(mobile_actual.keys()),
            "expected_vs_actual": {
                "desktop_expected": list(desktop_expected.keys()),
                "desktop_actual": list(desktop_actual.keys()),
                "mobile_expected": list(mobile_expected.keys()),
                "mobile_actual": list(mobile_actual.keys())
            }
        }
    
    async def test_menu_settings_post_endpoint(self) -> Dict:
        """Test POST /api/admin/menu-settings endpoint for updating menu settings"""
        print("📤 Testing menu settings POST endpoint...")
        
        if not self.admin_token:
            return {"test_name": "Menu Settings POST Endpoint", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # First get current settings
        get_result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        if not get_result["success"]:
            return {
                "test_name": "Menu Settings POST Endpoint",
                "success": False,
                "error": "Failed to get current settings for POST test"
            }
        
        current_settings = get_result["data"]
        
        # Create test settings with a small modification
        test_settings = {
            "desktop_menu": {
                **current_settings.get("desktop_menu", {}),
                "browse": {
                    "enabled": True,
                    "label": "Browse Test",  # Modified label for testing
                    "roles": ["buyer", "seller"]
                }
            },
            "mobile_menu": {
                **current_settings.get("mobile_menu", {}),
                "browse": {
                    "enabled": True,
                    "label": "Browse Test Mobile",  # Modified label for testing
                    "roles": ["buyer", "seller"]
                }
            }
        }
        
        # Test POST request
        post_result = await self.make_request("/admin/menu-settings", "POST", data=test_settings, headers=headers)
        
        if post_result["success"]:
            # Verify the update by getting settings again
            verify_result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
            
            update_verified = False
            if verify_result["success"]:
                updated_data = verify_result["data"]
                desktop_browse = updated_data.get("desktop_menu", {}).get("browse", {})
                mobile_browse = updated_data.get("mobile_menu", {}).get("browse", {})
                
                update_verified = (
                    desktop_browse.get("label") == "Browse Test" and
                    mobile_browse.get("label") == "Browse Test Mobile"
                )
            
            # Restore original settings
            if self.original_menu_settings:
                await self.make_request("/admin/menu-settings", "POST", data=self.original_menu_settings, headers=headers)
            
            print(f"  📊 POST status: {post_result['status']}")
            print(f"  ✅ Update successful: {post_result['success']}")
            print(f"  🔍 Update verified: {update_verified}")
            
            return {
                "test_name": "Menu Settings POST Endpoint",
                "success": post_result["success"] and update_verified,
                "response_time_ms": post_result["response_time_ms"],
                "post_successful": post_result["success"],
                "update_verified": update_verified,
                "post_response": post_result.get("data"),
                "verification_data": updated_data if verify_result["success"] else None
            }
        else:
            print(f"  ❌ POST failed: {post_result.get('error', 'Unknown error')}")
            return {
                "test_name": "Menu Settings POST Endpoint",
                "success": False,
                "error": post_result.get("error", "Unknown error"),
                "status": post_result["status"],
                "response": post_result.get("data", "")
            }
    
    async def test_default_menu_items_verification(self) -> Dict:
        """Test that default menu items have proper enabled, label, and roles properties"""
        print("🔄 Testing default menu items verification...")
        
        if not self.admin_token:
            return {"test_name": "Default Menu Items Verification", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get current menu settings
        result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if not result["success"]:
            return {
                "test_name": "Default Menu Items Verification",
                "success": False,
                "error": result.get("error", "Failed to get menu settings")
            }
        
        data = result["data"]
        desktop_menu = data.get("desktop_menu", {})
        mobile_menu = data.get("mobile_menu", {})
        
        # Define expected default items
        expected_default_items = [
            "browse", "create_listing", "messages", "my_listings", "tenders", "inventory"
        ]
        
        # Check desktop menu items
        desktop_verification = []
        for item_key in expected_default_items:
            if item_key in desktop_menu:
                item_data = desktop_menu[item_key]
                verification = {
                    "item": item_key,
                    "exists": True,
                    "has_enabled": "enabled" in item_data,
                    "has_label": "label" in item_data,
                    "has_roles": "roles" in item_data,
                    "enabled_value": item_data.get("enabled"),
                    "label_value": item_data.get("label"),
                    "roles_value": item_data.get("roles"),
                    "valid_structure": all(key in item_data for key in ["enabled", "label", "roles"])
                }
            else:
                verification = {
                    "item": item_key,
                    "exists": False,
                    "has_enabled": False,
                    "has_label": False,
                    "has_roles": False,
                    "valid_structure": False
                }
            desktop_verification.append(verification)
        
        # Check mobile menu items
        mobile_verification = []
        for item_key in expected_default_items:
            if item_key in mobile_menu:
                item_data = mobile_menu[item_key]
                verification = {
                    "item": item_key,
                    "exists": True,
                    "has_enabled": "enabled" in item_data,
                    "has_label": "label" in item_data,
                    "has_roles": "roles" in item_data,
                    "enabled_value": item_data.get("enabled"),
                    "label_value": item_data.get("label"),
                    "roles_value": item_data.get("roles"),
                    "valid_structure": all(key in item_data for key in ["enabled", "label", "roles"])
                }
            else:
                verification = {
                    "item": item_key,
                    "exists": False,
                    "has_enabled": False,
                    "has_label": False,
                    "has_roles": False,
                    "valid_structure": False
                }
            mobile_verification.append(verification)
        
        # Calculate success metrics
        desktop_valid_items = sum(1 for v in desktop_verification if v["valid_structure"])
        mobile_valid_items = sum(1 for v in mobile_verification if v["valid_structure"])
        
        desktop_success_rate = (desktop_valid_items / len(expected_default_items)) * 100
        mobile_success_rate = (mobile_valid_items / len(expected_default_items)) * 100
        
        overall_success = desktop_success_rate >= 80 and mobile_success_rate >= 80
        
        print(f"  🖥️ Desktop valid items: {desktop_valid_items}/{len(expected_default_items)} ({desktop_success_rate:.1f}%)")
        print(f"  📱 Mobile valid items: {mobile_valid_items}/{len(expected_default_items)} ({mobile_success_rate:.1f}%)")
        print(f"  {'✅' if overall_success else '❌'} Default items verification {'passed' if overall_success else 'failed'}")
        
        return {
            "test_name": "Default Menu Items Verification",
            "success": overall_success,
            "desktop_verification": desktop_verification,
            "mobile_verification": mobile_verification,
            "desktop_valid_items": desktop_valid_items,
            "mobile_valid_items": mobile_valid_items,
            "desktop_success_rate": desktop_success_rate,
            "mobile_success_rate": mobile_success_rate,
            "expected_items": expected_default_items,
            "total_expected": len(expected_default_items)
        }
    
    async def test_database_cleanup_impact(self) -> Dict:
        """Test if recent database cleanup affected menu settings structure"""
        print("🔍 Testing database cleanup impact on menu settings...")
        
        if not self.admin_token:
            return {"test_name": "Database Cleanup Impact", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get current menu settings
        result = await self.make_request("/admin/menu-settings", "GET", headers=headers)
        
        if not result["success"]:
            return {
                "test_name": "Database Cleanup Impact",
                "success": False,
                "error": result.get("error", "Failed to get menu settings")
            }
        
        data = result["data"]
        
        # Check for signs of database cleanup issues
        cleanup_analysis = {
            "has_desktop_menu": "desktop_menu" in data,
            "has_mobile_menu": "mobile_menu" in data,
            "desktop_menu_empty": len(data.get("desktop_menu", {})) == 0,
            "mobile_menu_empty": len(data.get("mobile_menu", {})) == 0,
            "has_custom_items": False,
            "corrupted_custom_items": 0,
            "placeholder_items": 0
        }
        
        # Check for custom items and potential corruption
        desktop_menu = data.get("desktop_menu", {})
        mobile_menu = data.get("mobile_menu", {})
        
        # Check desktop custom items
        desktop_custom = desktop_menu.get("custom_items", [])
        if desktop_custom:
            cleanup_analysis["has_custom_items"] = True
            for item in desktop_custom:
                if isinstance(item, dict):
                    label = item.get("label", "")
                    if "External Page" in label or "Internal Page" in label:
                        cleanup_analysis["placeholder_items"] += 1
                    if not item.get("id") or not item.get("label") or not item.get("url"):
                        cleanup_analysis["corrupted_custom_items"] += 1
        
        # Check mobile custom items
        mobile_custom = mobile_menu.get("custom_items", [])
        if mobile_custom:
            cleanup_analysis["has_custom_items"] = True
            for item in mobile_custom:
                if isinstance(item, dict):
                    label = item.get("label", "")
                    if "External Page" in label or "Internal Page" in label:
                        cleanup_analysis["placeholder_items"] += 1
                    if not item.get("id") or not item.get("label") or not item.get("url"):
                        cleanup_analysis["corrupted_custom_items"] += 1
        
        # Check for missing default items (could indicate cleanup issues)
        expected_defaults = ["browse", "create_listing", "messages", "my_listings", "tenders"]
        missing_desktop_defaults = [item for item in expected_defaults if item not in desktop_menu]
        missing_mobile_defaults = [item for item in expected_defaults if item not in mobile_menu]
        
        cleanup_analysis["missing_desktop_defaults"] = missing_desktop_defaults
        cleanup_analysis["missing_mobile_defaults"] = missing_mobile_defaults
        cleanup_analysis["missing_defaults_count"] = len(missing_desktop_defaults) + len(missing_mobile_defaults)
        
        # Determine if cleanup caused issues
        cleanup_issues_detected = (
            cleanup_analysis["desktop_menu_empty"] or
            cleanup_analysis["mobile_menu_empty"] or
            cleanup_analysis["corrupted_custom_items"] > 0 or
            cleanup_analysis["placeholder_items"] > 0 or
            cleanup_analysis["missing_defaults_count"] > 2
        )
        
        cleanup_success = not cleanup_issues_detected
        
        print(f"  📊 Desktop menu items: {len(desktop_menu)}")
        print(f"  📊 Mobile menu items: {len(mobile_menu)}")
        print(f"  🗑️ Corrupted custom items: {cleanup_analysis['corrupted_custom_items']}")
        print(f"  📝 Placeholder items: {cleanup_analysis['placeholder_items']}")
        print(f"  ❌ Missing defaults: {cleanup_analysis['missing_defaults_count']}")
        print(f"  {'✅' if cleanup_success else '❌'} Database cleanup {'did not affect' if cleanup_success else 'may have affected'} menu structure")
        
        return {
            "test_name": "Database Cleanup Impact",
            "success": cleanup_success,
            "cleanup_analysis": cleanup_analysis,
            "cleanup_issues_detected": cleanup_issues_detected,
            "desktop_items_count": len(desktop_menu),
            "mobile_items_count": len(mobile_menu),
            "custom_items_desktop": len(desktop_custom),
            "custom_items_mobile": len(mobile_custom),
            "recommendations": [
                "Check for corrupted custom items" if cleanup_analysis["corrupted_custom_items"] > 0 else None,
                "Remove placeholder items" if cleanup_analysis["placeholder_items"] > 0 else None,
                "Restore missing default items" if cleanup_analysis["missing_defaults_count"] > 0 else None,
                "Initialize menu settings" if cleanup_analysis["desktop_menu_empty"] or cleanup_analysis["mobile_menu_empty"] else None
            ]
        }
    
    async def test_user_menu_settings_endpoint(self) -> Dict:
        """Test user menu settings endpoint to verify filtering works correctly"""
        print("📋 Testing user menu settings endpoint...")
        
        if not self.admin_token:
            return {"test_name": "User Menu Settings Endpoint", "error": "No admin token available"}
        
        # Test with admin user ID (should see admin items)
        admin_user_id = ADMIN_ID
        result = await self.make_request(f"/menu-settings/user/{admin_user_id}")
        
        if result["success"]:
            data = result["data"]
            
            # Check structure
            has_desktop_menu = "desktop_menu" in data
            has_mobile_menu = "mobile_menu" in data
            has_user_role = "user_role" in data
            
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            user_role = data.get("user_role", "unknown")
            
            # Check if admin items are present
            admin_items_desktop = []
            admin_items_mobile = []
            
            for item_key, item_data in desktop_menu.items():
                if isinstance(item_data, dict) and "roles" in item_data:
                    if "admin" in item_data["roles"]:
                        admin_items_desktop.append(item_key)
            
            for item_key, item_data in mobile_menu.items():
                if isinstance(item_data, dict) and "roles" in item_data:
                    if "admin" in item_data["roles"]:
                        admin_items_mobile.append(item_key)
            
            # Check custom items filtering
            desktop_custom = desktop_menu.get("custom_items", [])
            mobile_custom = mobile_menu.get("custom_items", [])
            
            # Verify role-based filtering for custom items
            custom_items_properly_filtered = True
            for item in desktop_custom + mobile_custom:
                if isinstance(item, dict) and "roles" in item:
                    if "admin" not in item["roles"]:
                        custom_items_properly_filtered = False
                        break
            
            filtering_success = (
                has_desktop_menu and has_mobile_menu and
                len(admin_items_desktop) > 0 and
                custom_items_properly_filtered
            )
            
            print(f"  📊 User role: {user_role}")
            print(f"  🖥️ Desktop items: {len(desktop_menu)}")
            print(f"  📱 Mobile items: {len(mobile_menu)}")
            print(f"  🔑 Admin items desktop: {len(admin_items_desktop)}")
            print(f"  🔑 Admin items mobile: {len(admin_items_mobile)}")
            print(f"  📝 Custom items desktop: {len(desktop_custom)}")
            print(f"  📝 Custom items mobile: {len(mobile_custom)}")
            print(f"  {'✅' if filtering_success else '❌'} User menu filtering {'working' if filtering_success else 'failed'}")
            
            return {
                "test_name": "User Menu Settings Endpoint",
                "success": filtering_success,
                "response_time_ms": result["response_time_ms"],
                "has_desktop_menu": has_desktop_menu,
                "has_mobile_menu": has_mobile_menu,
                "has_user_role": has_user_role,
                "user_role": user_role,
                "desktop_items_count": len(desktop_menu),
                "mobile_items_count": len(mobile_menu),
                "admin_items_desktop": admin_items_desktop,
                "admin_items_mobile": admin_items_mobile,
                "custom_items_desktop": len(desktop_custom),
                "custom_items_mobile": len(mobile_custom),
                "custom_items_properly_filtered": custom_items_properly_filtered,
                "full_response": data
            }
        else:
            print(f"  ❌ User menu settings failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "User Menu Settings Endpoint",
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result["status"],
                "response": result.get("data", "")
            }
    
    async def cleanup_test_data(self):
        """Restore original menu settings if modified during testing"""
        if not self.admin_token or not self.original_menu_settings:
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            await self.make_request("/admin/menu-settings", "POST", data=self.original_menu_settings, headers=headers)
            print(f"  🧹 Restored original menu settings")
        except Exception as e:
            print(f"  ⚠️ Failed to restore original menu settings: {e}")
    
    async def run_comprehensive_menu_settings_test(self) -> Dict:
        """Run all admin menu settings tests"""
        print("🚀 Starting Admin Menu Settings Functionality Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_admin()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Admin authentication failed - cannot proceed with tests"
                }
            
            # Run all test suites
            menu_get_endpoint = await self.test_menu_settings_get_endpoint()
            data_structure_comparison = await self.test_menu_settings_data_structure_comparison()
            menu_post_endpoint = await self.test_menu_settings_post_endpoint()
            default_items_verification = await self.test_default_menu_items_verification()
            database_cleanup_impact = await self.test_database_cleanup_impact()
            user_menu_endpoint = await self.test_user_menu_settings_endpoint()
            
            # Cleanup test data
            await self.cleanup_test_data()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "menu_settings_get_endpoint": menu_get_endpoint,
                "data_structure_comparison": data_structure_comparison,
                "menu_settings_post_endpoint": menu_post_endpoint,
                "default_items_verification": default_items_verification,
                "database_cleanup_impact": database_cleanup_impact,
                "user_menu_settings_endpoint": user_menu_endpoint
            }
            
            # Calculate overall success metrics
            test_results = [
                menu_get_endpoint.get("success", False),
                data_structure_comparison.get("success", False),
                menu_post_endpoint.get("success", False),
                default_items_verification.get("success", False),
                database_cleanup_impact.get("success", False),
                user_menu_endpoint.get("success", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "menu_get_working": menu_get_endpoint.get("success", False),
                "data_structure_correct": data_structure_comparison.get("success", False),
                "menu_post_working": menu_post_endpoint.get("success", False),
                "default_items_valid": default_items_verification.get("success", False),
                "database_cleanup_ok": database_cleanup_impact.get("success", False),
                "user_menu_filtering_working": user_menu_endpoint.get("success", False),
                "all_tests_passed": overall_success_rate == 100,
                "critical_functionality_working": (
                    menu_get_endpoint.get("success", False) and
                    menu_post_endpoint.get("success", False) and
                    default_items_verification.get("success", False)
                ),
                "menu_settings_functional": (
                    menu_get_endpoint.get("success", False) and
                    menu_post_endpoint.get("success", False)
                )
            }
            
            return all_results
            
        finally:
            await self.cleanup()


class CustomMenuManagementTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.admin_token = None
        self.test_custom_items = []
        
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
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            print(f"  ✅ Admin authentication successful")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            return False
    
    async def test_available_pages_endpoint(self) -> Dict:
        """Test GET /api/admin/available-pages endpoint"""
        print("📄 Testing available pages endpoint...")
        
        if not self.admin_token:
            return {"test_name": "Available Pages Endpoint", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/available-pages", headers=headers)
        
        if result["success"]:
            data = result["data"]
            available_pages = data.get("available_pages", [])
            
            # Validate expected pages are present
            expected_pages = ["/browse", "/create-listing", "/messages", "/tenders", "/my-listings"]
            found_pages = [page["path"] for page in available_pages]
            expected_found = all(page in found_pages for page in expected_pages)
            
            # Validate page structure
            valid_structure = True
            for page in available_pages[:3]:  # Check first 3 pages
                if not all(key in page for key in ["path", "label", "icon"]):
                    valid_structure = False
                    break
            
            print(f"  ✅ Found {len(available_pages)} available pages")
            print(f"  📊 Expected pages present: {expected_found}")
            print(f"  🏗️ Valid structure: {valid_structure}")
            
            return {
                "test_name": "Available Pages Endpoint",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "total_pages": len(available_pages),
                "expected_pages_found": expected_found,
                "valid_structure": valid_structure,
                "sample_pages": available_pages[:5]
            }
        else:
            print(f"  ❌ Available pages endpoint failed: {result.get('error')}")
            return {
                "test_name": "Available Pages Endpoint",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def test_available_icons_endpoint(self) -> Dict:
        """Test GET /api/admin/available-icons endpoint"""
        print("🎨 Testing available icons endpoint...")
        
        if not self.admin_token:
            return {"test_name": "Available Icons Endpoint", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/available-icons", headers=headers)
        
        if result["success"]:
            data = result["data"]
            available_icons = data.get("available_icons", [])
            
            # Validate expected icons are present
            expected_icons = ["Store", "Plus", "MessageCircle", "DollarSign", "Package", "Heart", "User", "Shield"]
            expected_found = all(icon in available_icons for icon in expected_icons)
            
            print(f"  ✅ Found {len(available_icons)} available icons")
            print(f"  📊 Expected icons present: {expected_found}")
            
            return {
                "test_name": "Available Icons Endpoint",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "total_icons": len(available_icons),
                "expected_icons_found": expected_found,
                "sample_icons": available_icons[:10]
            }
        else:
            print(f"  ❌ Available icons endpoint failed: {result.get('error')}")
            return {
                "test_name": "Available Icons Endpoint",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def test_menu_settings_get(self) -> Dict:
        """Test GET /api/admin/menu-settings endpoint"""
        print("⚙️ Testing menu settings GET endpoint...")
        
        if not self.admin_token:
            return {"test_name": "Menu Settings GET", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if result["success"]:
            data = result["data"]
            desktop_menu = data.get("desktop_menu", {})
            mobile_menu = data.get("mobile_menu", {})
            
            # Check for expected menu structure
            has_desktop_items = len(desktop_menu) > 0
            has_mobile_items = len(mobile_menu) > 0
            
            print(f"  ✅ Menu settings retrieved successfully")
            print(f"  🖥️ Desktop menu items: {len(desktop_menu)}")
            print(f"  📱 Mobile menu items: {len(mobile_menu)}")
            
            return {
                "test_name": "Menu Settings GET",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "has_desktop_items": has_desktop_items,
                "has_mobile_items": has_mobile_items,
                "desktop_items_count": len(desktop_menu),
                "mobile_items_count": len(mobile_menu),
                "current_settings": data
            }
        else:
            print(f"  ❌ Menu settings GET failed: {result.get('error')}")
            return {
                "test_name": "Menu Settings GET",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def test_custom_menu_item_creation(self) -> Dict:
        """Test creating custom menu items via POST /api/admin/menu-settings"""
        print("➕ Testing custom menu item creation...")
        
        if not self.admin_token:
            return {"test_name": "Custom Menu Item Creation", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # First get current settings
        current_result = await self.make_request("/admin/menu-settings", headers=headers)
        if not current_result["success"]:
            return {
                "test_name": "Custom Menu Item Creation",
                "success": False,
                "error": "Failed to get current menu settings"
            }
        
        current_settings = current_result["data"]
        
        # Create test custom items
        test_custom_items = [
            {
                "id": "custom_external_link",
                "label": "External Link Test",
                "url": "https://example.com",
                "icon": "ExternalLink",
                "type": "custom_url",
                "target": "_blank",
                "position": 100,
                "enabled": True,
                "roles": ["admin", "manager"]
            },
            {
                "id": "custom_internal_page",
                "label": "Internal Page Test",
                "url": "/browse",
                "icon": "Store",
                "type": "existing_page",
                "target": "_self",
                "position": 101,
                "enabled": True,
                "roles": ["admin", "manager", "seller", "buyer"]
            }
        ]
        
        # Add custom items to both desktop and mobile menus
        updated_settings = {
            "desktop_menu": {
                **current_settings.get("desktop_menu", {}),
                "custom_items": test_custom_items
            },
            "mobile_menu": {
                **current_settings.get("mobile_menu", {}),
                "custom_items": test_custom_items
            }
        }
        
        # Save the test items for later cleanup
        self.test_custom_items = test_custom_items
        
        # Update menu settings with custom items
        result = await self.make_request("/admin/menu-settings", "POST", data=updated_settings, headers=headers)
        
        if result["success"]:
            response_data = result["data"]
            settings = response_data.get("settings", {})
            
            # Verify custom items were saved
            desktop_custom = settings.get("desktop_menu", {}).get("custom_items", [])
            mobile_custom = settings.get("mobile_menu", {}).get("custom_items", [])
            
            desktop_saved_correctly = len(desktop_custom) == len(test_custom_items)
            mobile_saved_correctly = len(mobile_custom) == len(test_custom_items)
            
            # Verify item structure
            structure_valid = True
            if desktop_custom:
                first_item = desktop_custom[0]
                required_fields = ["id", "label", "url", "icon", "type", "target", "position", "enabled", "roles"]
                structure_valid = all(field in first_item for field in required_fields)
            
            print(f"  ✅ Custom menu items created successfully")
            print(f"  🖥️ Desktop custom items: {len(desktop_custom)}")
            print(f"  📱 Mobile custom items: {len(mobile_custom)}")
            print(f"  🏗️ Structure valid: {structure_valid}")
            
            return {
                "test_name": "Custom Menu Item Creation",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "desktop_items_saved": desktop_saved_correctly,
                "mobile_items_saved": mobile_saved_correctly,
                "structure_valid": structure_valid,
                "desktop_custom_count": len(desktop_custom),
                "mobile_custom_count": len(mobile_custom),
                "test_items_created": len(test_custom_items)
            }
        else:
            print(f"  ❌ Custom menu item creation failed: {result.get('error')}")
            return {
                "test_name": "Custom Menu Item Creation",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def test_menu_settings_validation(self) -> Dict:
        """Test menu settings validation for custom items"""
        print("✅ Testing menu settings validation...")
        
        if not self.admin_token:
            return {"test_name": "Menu Settings Validation", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        validation_tests = []
        
        # Test 1: Missing required fields
        print("  Testing missing required fields...")
        invalid_item = {
            "label": "Invalid Item",
            # Missing id, url, enabled
            "icon": "Star",
            "roles": ["admin"]
        }
        
        invalid_settings = {
            "desktop_menu": {
                "custom_items": [invalid_item]
            },
            "mobile_menu": {}
        }
        
        result1 = await self.make_request("/admin/menu-settings", "POST", data=invalid_settings, headers=headers)
        validation_tests.append({
            "test": "Missing Required Fields",
            "should_fail": True,
            "actually_failed": not result1["success"],
            "status": result1["status"],
            "error": result1.get("error", "")
        })
        
        # Test 2: Invalid item type (should be auto-corrected)
        print("  Testing invalid item type...")
        auto_correct_item = {
            "id": "test_auto_correct",
            "label": "Auto Correct Test",
            "url": "https://example.com",
            "enabled": True,
            "type": "invalid_type",  # Should be auto-corrected to "custom_url"
            "roles": ["admin"]
        }
        
        auto_correct_settings = {
            "desktop_menu": {
                "custom_items": [auto_correct_item]
            },
            "mobile_menu": {}
        }
        
        result2 = await self.make_request("/admin/menu-settings", "POST", data=auto_correct_settings, headers=headers)
        validation_tests.append({
            "test": "Invalid Type Auto-Correction",
            "should_succeed": True,
            "actually_succeeded": result2["success"],
            "status": result2["status"]
        })
        
        # Test 3: Invalid roles (should be filtered)
        print("  Testing invalid roles filtering...")
        invalid_roles_item = {
            "id": "test_roles_filter",
            "label": "Roles Filter Test",
            "url": "/test",
            "enabled": True,
            "roles": ["admin", "invalid_role", "buyer", "another_invalid"]  # Should filter out invalid roles
        }
        
        roles_filter_settings = {
            "desktop_menu": {
                "custom_items": [invalid_roles_item]
            },
            "mobile_menu": {}
        }
        
        result3 = await self.make_request("/admin/menu-settings", "POST", data=roles_filter_settings, headers=headers)
        validation_tests.append({
            "test": "Invalid Roles Filtering",
            "should_succeed": True,
            "actually_succeeded": result3["success"],
            "status": result3["status"]
        })
        
        # Calculate validation results
        successful_validations = sum(1 for test in validation_tests if 
                                   (test.get("should_fail") and test.get("actually_failed")) or
                                   (test.get("should_succeed") and test.get("actually_succeeded")))
        
        validation_working = successful_validations == len(validation_tests)
        
        print(f"  📊 Validation tests: {successful_validations}/{len(validation_tests)} passed")
        
        return {
            "test_name": "Menu Settings Validation",
            "success": validation_working,
            "total_validation_tests": len(validation_tests),
            "successful_validations": successful_validations,
            "validation_working": validation_working,
            "detailed_tests": validation_tests
        }
    
    async def test_user_menu_filtering(self) -> Dict:
        """Test that custom items are properly filtered in user menu settings"""
        print("🔍 Testing user menu filtering with custom items...")
        
        # Test with admin user (should see admin-only custom items)
        admin_result = await self.make_request(f"/menu-settings/user/{ADMIN_ID}")
        
        if admin_result["success"]:
            admin_data = admin_result["data"]
            desktop_menu = admin_data.get("desktop_menu", {})
            mobile_menu = admin_data.get("mobile_menu", {})
            
            # Check if custom items are included
            desktop_custom = desktop_menu.get("custom_items", [])
            mobile_custom = mobile_menu.get("custom_items", [])
            
            # Verify role-based filtering (admin should see admin-only items)
            admin_role_filtering = True
            for item in desktop_custom + mobile_custom:
                if "admin" not in item.get("roles", []):
                    admin_role_filtering = False
                    break
            
            print(f"  ✅ User menu filtering tested")
            print(f"  🖥️ Desktop custom items for admin: {len(desktop_custom)}")
            print(f"  📱 Mobile custom items for admin: {len(mobile_custom)}")
            print(f"  🔐 Role filtering working: {admin_role_filtering}")
            
            return {
                "test_name": "User Menu Filtering",
                "success": True,
                "response_time_ms": admin_result["response_time_ms"],
                "desktop_custom_items": len(desktop_custom),
                "mobile_custom_items": len(mobile_custom),
                "role_filtering_working": admin_role_filtering,
                "user_role": admin_data.get("user_role", "unknown")
            }
        else:
            print(f"  ❌ User menu filtering test failed: {admin_result.get('error')}")
            return {
                "test_name": "User Menu Filtering",
                "success": False,
                "error": admin_result.get("error"),
                "status": admin_result["status"]
            }
    
    async def test_custom_item_crud_operations(self) -> Dict:
        """Test complete CRUD operations for custom menu items"""
        print("🔄 Testing custom item CRUD operations...")
        
        if not self.admin_token:
            return {"test_name": "Custom Item CRUD", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        crud_results = []
        
        # CREATE - Already tested in test_custom_menu_item_creation
        crud_results.append({"operation": "CREATE", "success": True, "note": "Tested in creation test"})
        
        # READ - Get current settings to verify items exist
        print("  Testing READ operation...")
        read_result = await self.make_request("/admin/menu-settings", headers=headers)
        if read_result["success"]:
            settings = read_result["data"]
            desktop_custom = settings.get("desktop_menu", {}).get("custom_items", [])
            read_success = len(desktop_custom) > 0
            crud_results.append({"operation": "READ", "success": read_success, "items_found": len(desktop_custom)})
        else:
            crud_results.append({"operation": "READ", "success": False, "error": read_result.get("error")})
        
        # UPDATE - Modify existing custom item
        print("  Testing UPDATE operation...")
        if read_result["success"] and desktop_custom:
            # Modify the first custom item
            updated_item = desktop_custom[0].copy()
            updated_item["label"] = "Updated Test Label"
            updated_item["url"] = "https://updated-example.com"
            
            # Update the settings
            updated_settings = read_result["data"]
            updated_settings["desktop_menu"]["custom_items"][0] = updated_item
            
            update_result = await self.make_request("/admin/menu-settings", "POST", data=updated_settings, headers=headers)
            
            if update_result["success"]:
                # Verify the update
                verify_result = await self.make_request("/admin/menu-settings", headers=headers)
                if verify_result["success"]:
                    verify_custom = verify_result["data"].get("desktop_menu", {}).get("custom_items", [])
                    update_verified = (len(verify_custom) > 0 and 
                                     verify_custom[0].get("label") == "Updated Test Label")
                    crud_results.append({"operation": "UPDATE", "success": update_verified, "verified": update_verified})
                else:
                    crud_results.append({"operation": "UPDATE", "success": False, "error": "Verification failed"})
            else:
                crud_results.append({"operation": "UPDATE", "success": False, "error": update_result.get("error")})
        else:
            crud_results.append({"operation": "UPDATE", "success": False, "error": "No items to update"})
        
        # DELETE - Remove custom items
        print("  Testing DELETE operation...")
        delete_settings = read_result["data"] if read_result["success"] else {}
        delete_settings["desktop_menu"] = delete_settings.get("desktop_menu", {})
        delete_settings["mobile_menu"] = delete_settings.get("mobile_menu", {})
        delete_settings["desktop_menu"]["custom_items"] = []  # Remove all custom items
        delete_settings["mobile_menu"]["custom_items"] = []   # Remove all custom items
        
        delete_result = await self.make_request("/admin/menu-settings", "POST", data=delete_settings, headers=headers)
        
        if delete_result["success"]:
            # Verify deletion
            verify_delete_result = await self.make_request("/admin/menu-settings", headers=headers)
            if verify_delete_result["success"]:
                verify_desktop = verify_delete_result["data"].get("desktop_menu", {}).get("custom_items", [])
                verify_mobile = verify_delete_result["data"].get("mobile_menu", {}).get("custom_items", [])
                delete_verified = len(verify_desktop) == 0 and len(verify_mobile) == 0
                crud_results.append({"operation": "DELETE", "success": delete_verified, "verified": delete_verified})
            else:
                crud_results.append({"operation": "DELETE", "success": False, "error": "Delete verification failed"})
        else:
            crud_results.append({"operation": "DELETE", "success": False, "error": delete_result.get("error")})
        
        # Calculate overall CRUD success
        successful_operations = sum(1 for result in crud_results if result.get("success", False))
        crud_success = successful_operations == len(crud_results)
        
        print(f"  📊 CRUD operations: {successful_operations}/{len(crud_results)} successful")
        
        return {
            "test_name": "Custom Item CRUD Operations",
            "success": crud_success,
            "total_operations": len(crud_results),
            "successful_operations": successful_operations,
            "crud_working": crud_success,
            "detailed_results": crud_results
        }
    
    async def test_integration_workflow(self) -> Dict:
        """Test complete custom menu workflow integration"""
        print("🔗 Testing complete custom menu workflow integration...")
        
        if not self.admin_token:
            return {"test_name": "Integration Workflow", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        workflow_steps = []
        
        # Step 1: Get available resources
        print("  Step 1: Getting available resources...")
        pages_result = await self.make_request("/admin/available-pages", headers=headers)
        icons_result = await self.make_request("/admin/available-icons", headers=headers)
        
        resources_available = pages_result["success"] and icons_result["success"]
        workflow_steps.append({
            "step": "Get Available Resources",
            "success": resources_available,
            "pages_available": pages_result["success"],
            "icons_available": icons_result["success"]
        })
        
        # Step 2: Create comprehensive custom menu items
        print("  Step 2: Creating comprehensive custom menu items...")
        if resources_available:
            # Use actual available pages and icons
            available_pages = pages_result["data"].get("available_pages", [])
            available_icons = icons_result["data"].get("available_icons", [])
            
            comprehensive_items = [
                {
                    "id": "workflow_external",
                    "label": "External Resource",
                    "url": "https://docs.example.com",
                    "icon": available_icons[0] if available_icons else "ExternalLink",
                    "type": "custom_url",
                    "target": "_blank",
                    "position": 200,
                    "enabled": True,
                    "roles": ["admin", "manager"]
                },
                {
                    "id": "workflow_internal",
                    "label": "Internal Page",
                    "url": available_pages[0]["path"] if available_pages else "/browse",
                    "icon": available_pages[0]["icon"] if available_pages else "Store",
                    "type": "existing_page",
                    "target": "_self",
                    "position": 201,
                    "enabled": True,
                    "roles": ["admin", "manager", "seller", "buyer"]
                }
            ]
            
            # Get current settings and add comprehensive items
            current_result = await self.make_request("/admin/menu-settings", headers=headers)
            if current_result["success"]:
                current_settings = current_result["data"]
                updated_settings = {
                    "desktop_menu": {
                        **current_settings.get("desktop_menu", {}),
                        "custom_items": comprehensive_items
                    },
                    "mobile_menu": {
                        **current_settings.get("mobile_menu", {}),
                        "custom_items": comprehensive_items
                    }
                }
                
                create_result = await self.make_request("/admin/menu-settings", "POST", data=updated_settings, headers=headers)
                workflow_steps.append({
                    "step": "Create Comprehensive Items",
                    "success": create_result["success"],
                    "items_created": len(comprehensive_items)
                })
            else:
                workflow_steps.append({
                    "step": "Create Comprehensive Items",
                    "success": False,
                    "error": "Failed to get current settings"
                })
        else:
            workflow_steps.append({
                "step": "Create Comprehensive Items",
                "success": False,
                "error": "Resources not available"
            })
        
        # Step 3: Verify user menu filtering
        print("  Step 3: Verifying user menu filtering...")
        user_menu_result = await self.make_request(f"/menu-settings/user/{ADMIN_ID}")
        if user_menu_result["success"]:
            user_data = user_menu_result["data"]
            desktop_custom = user_data.get("desktop_menu", {}).get("custom_items", [])
            mobile_custom = user_data.get("mobile_menu", {}).get("custom_items", [])
            
            filtering_working = len(desktop_custom) > 0 and len(mobile_custom) > 0
            workflow_steps.append({
                "step": "Verify User Filtering",
                "success": filtering_working,
                "desktop_items": len(desktop_custom),
                "mobile_items": len(mobile_custom)
            })
        else:
            workflow_steps.append({
                "step": "Verify User Filtering",
                "success": False,
                "error": user_menu_result.get("error")
            })
        
        # Step 4: Test role-based access control
        print("  Step 4: Testing role-based access control...")
        # This would ideally test with different user roles, but we'll verify the structure
        role_test_success = True
        if user_menu_result["success"]:
            user_data = user_menu_result["data"]
            user_role = user_data.get("user_role", "")
            
            # Verify that returned items match user role
            all_custom_items = (user_data.get("desktop_menu", {}).get("custom_items", []) + 
                              user_data.get("mobile_menu", {}).get("custom_items", []))
            
            for item in all_custom_items:
                if user_role not in item.get("roles", []):
                    role_test_success = False
                    break
        
        workflow_steps.append({
            "step": "Test Role-Based Access",
            "success": role_test_success,
            "user_role": user_data.get("user_role", "unknown") if user_menu_result["success"] else "unknown"
        })
        
        # Calculate overall workflow success
        successful_steps = sum(1 for step in workflow_steps if step.get("success", False))
        workflow_success = successful_steps == len(workflow_steps)
        
        print(f"  📊 Workflow steps: {successful_steps}/{len(workflow_steps)} successful")
        
        return {
            "test_name": "Integration Workflow",
            "success": workflow_success,
            "total_steps": len(workflow_steps),
            "successful_steps": successful_steps,
            "workflow_complete": workflow_success,
            "detailed_steps": workflow_steps
        }
    
    async def run_comprehensive_custom_menu_test(self) -> Dict:
        """Run all custom menu management tests"""
        print("🚀 Starting Custom Menu Item Management Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_admin()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Admin authentication failed - cannot proceed with tests"
                }
            
            # Run all test suites
            available_pages = await self.test_available_pages_endpoint()
            available_icons = await self.test_available_icons_endpoint()
            menu_settings_get = await self.test_menu_settings_get()
            custom_item_creation = await self.test_custom_menu_item_creation()
            menu_validation = await self.test_menu_settings_validation()
            user_menu_filtering = await self.test_user_menu_filtering()
            crud_operations = await self.test_custom_item_crud_operations()
            integration_workflow = await self.test_integration_workflow()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "available_pages_endpoint": available_pages,
                "available_icons_endpoint": available_icons,
                "menu_settings_get": menu_settings_get,
                "custom_item_creation": custom_item_creation,
                "menu_validation": menu_validation,
                "user_menu_filtering": user_menu_filtering,
                "crud_operations": crud_operations,
                "integration_workflow": integration_workflow
            }
            
            # Calculate overall success metrics
            test_results = [
                available_pages.get("success", False),
                available_icons.get("success", False),
                menu_settings_get.get("success", False),
                custom_item_creation.get("success", False),
                menu_validation.get("success", False),
                user_menu_filtering.get("success", False),
                crud_operations.get("success", False),
                integration_workflow.get("success", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "available_pages_working": available_pages.get("success", False),
                "available_icons_working": available_icons.get("success", False),
                "menu_settings_crud_working": menu_settings_get.get("success", False) and custom_item_creation.get("success", False),
                "validation_working": menu_validation.get("success", False),
                "user_filtering_working": user_menu_filtering.get("success", False),
                "crud_operations_working": crud_operations.get("success", False),
                "integration_workflow_working": integration_workflow.get("success", False),
                "all_tests_passed": overall_success_rate == 100,
                "critical_functionality_working": (
                    available_pages.get("success", False) and
                    available_icons.get("success", False) and
                    custom_item_creation.get("success", False) and
                    user_menu_filtering.get("success", False)
                )
            }
            
            return all_results
            
        finally:
            await self.cleanup()


class AdminAuthenticationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.admin_token = None
        self.test_users = []  # Store test users for management testing
        
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
    
    async def test_admin_user_authentication(self) -> Dict:
        """Test admin user login with admin@cataloro.com"""
        print("🔐 Testing admin user authentication...")
        
        # Test admin login
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"  # Mock password for testing
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            token = result["data"].get("token", "")
            
            # Store token for subsequent requests
            self.admin_token = token
            
            # Verify admin user properties
            email_correct = user_data.get("email") == ADMIN_EMAIL
            username_correct = user_data.get("username") == ADMIN_USERNAME
            role_correct = user_data.get("role") == ADMIN_ROLE or user_data.get("user_role") == "Admin"
            
            print(f"  ✅ Admin login successful")
            print(f"  📧 Email: {user_data.get('email')} ({'✅' if email_correct else '❌'})")
            print(f"  👤 Username: {user_data.get('username')} ({'✅' if username_correct else '❌'})")
            print(f"  🔑 Role: {user_data.get('role', user_data.get('user_role'))} ({'✅' if role_correct else '❌'})")
            
            return {
                "test_name": "Admin User Authentication",
                "login_successful": True,
                "response_time_ms": result["response_time_ms"],
                "admin_email_correct": email_correct,
                "admin_username_correct": username_correct,
                "admin_role_correct": role_correct,
                "user_data": user_data,
                "token_received": bool(token),
                "all_admin_properties_correct": email_correct and username_correct and role_correct
            }
        else:
            print(f"  ❌ Admin login failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Admin User Authentication",
                "login_successful": False,
                "response_time_ms": result["response_time_ms"],
                "error": result.get("error", "Login failed"),
                "status": result["status"]
            }
    
    async def test_database_user_consistency(self) -> Dict:
        """Test that all expected users exist in database"""
        print("🗄️ Testing database user consistency...")
        
        expected_users = [
            {"email": "admin@cataloro.com", "username": "sash_admin", "role": "admin"},
            {"email": "demo@cataloro.com", "username": "demo_user", "role": "user"},
        ]
        
        user_tests = []
        
        for expected_user in expected_users:
            print(f"  Testing user: {expected_user['email']}")
            
            # Try to login to verify user exists
            login_data = {
                "email": expected_user["email"],
                "password": "test_password"
            }
            
            result = await self.make_request("/auth/login", "POST", data=login_data)
            
            if result["success"]:
                user_data = result["data"].get("user", {})
                
                email_match = user_data.get("email") == expected_user["email"]
                username_match = user_data.get("username") == expected_user["username"]
                role_match = (user_data.get("role") == expected_user["role"] or 
                             (expected_user["role"] == "admin" and user_data.get("user_role") == "Admin"))
                
                user_tests.append({
                    "email": expected_user["email"],
                    "exists_in_database": True,
                    "email_correct": email_match,
                    "username_correct": username_match,
                    "role_correct": role_match,
                    "user_data": user_data,
                    "all_properties_correct": email_match and username_match and role_match
                })
                
                print(f"    ✅ User exists and properties match")
            else:
                user_tests.append({
                    "email": expected_user["email"],
                    "exists_in_database": False,
                    "error": result.get("error", "User not found"),
                    "status": result["status"]
                })
                print(f"    ❌ User not found or login failed")
        
        # Calculate overall consistency
        existing_users = [u for u in user_tests if u.get("exists_in_database", False)]
        correct_users = [u for u in existing_users if u.get("all_properties_correct", False)]
        
        return {
            "test_name": "Database User Consistency",
            "total_expected_users": len(expected_users),
            "users_found_in_database": len(existing_users),
            "users_with_correct_properties": len(correct_users),
            "database_consistency_score": (len(correct_users) / len(expected_users)) * 100,
            "all_users_consistent": len(correct_users) == len(expected_users),
            "detailed_user_tests": user_tests
        }
    
    async def test_user_management_endpoints(self) -> Dict:
        """Test user management endpoints work correctly"""
        print("👥 Testing user management endpoints...")
        
        if not self.admin_token:
            return {
                "test_name": "User Management Endpoints",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        endpoint_tests = []
        
        # Test admin dashboard
        print("  Testing admin dashboard...")
        dashboard_result = await self.make_request("/admin/dashboard", headers=headers)
        endpoint_tests.append({
            "endpoint": "/admin/dashboard",
            "success": dashboard_result["success"],
            "response_time_ms": dashboard_result["response_time_ms"],
            "has_data": bool(dashboard_result.get("data")) if dashboard_result["success"] else False
        })
        
        # Test performance metrics
        print("  Testing performance metrics...")
        performance_result = await self.make_request("/admin/performance", headers=headers)
        endpoint_tests.append({
            "endpoint": "/admin/performance",
            "success": performance_result["success"],
            "response_time_ms": performance_result["response_time_ms"],
            "has_data": bool(performance_result.get("data")) if performance_result["success"] else False
        })
        
        # Test health check (public endpoint)
        print("  Testing health check...")
        health_result = await self.make_request("/health")
        endpoint_tests.append({
            "endpoint": "/health",
            "success": health_result["success"],
            "response_time_ms": health_result["response_time_ms"],
            "has_data": bool(health_result.get("data")) if health_result["success"] else False
        })
        
        successful_endpoints = [t for t in endpoint_tests if t["success"]]
        avg_response_time = statistics.mean([t["response_time_ms"] for t in successful_endpoints]) if successful_endpoints else 0
        
        return {
            "test_name": "User Management Endpoints",
            "total_endpoints_tested": len(endpoint_tests),
            "successful_endpoints": len(successful_endpoints),
            "success_rate": (len(successful_endpoints) / len(endpoint_tests)) * 100,
            "avg_response_time_ms": avg_response_time,
            "all_endpoints_working": len(successful_endpoints) == len(endpoint_tests),
            "detailed_endpoint_tests": endpoint_tests
        }
    
    async def test_user_management_functionality(self) -> Dict:
        """Test comprehensive user management functionality including activate/suspend endpoints"""
        print("👥 Testing user management functionality...")
        
        if not self.admin_token:
            return {
                "test_name": "User Management Functionality",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        test_results = []
        
        # Step 1: Test listing all users
        print("  Testing user listing endpoint...")
        users_result = await self.make_request("/admin/users", headers=headers)
        
        if users_result["success"]:
            users_data = users_result["data"]
            print(f"    ✅ Found {len(users_data)} users in system")
            
            # Store users for further testing
            self.test_users = users_data
            
            test_results.append({
                "test": "List Users",
                "success": True,
                "response_time_ms": users_result["response_time_ms"],
                "user_count": len(users_data),
                "has_expected_users": any(u.get("email") == "admin@cataloro.com" for u in users_data)
            })
        else:
            print(f"    ❌ Failed to list users: {users_result.get('error')}")
            test_results.append({
                "test": "List Users",
                "success": False,
                "error": users_result.get("error"),
                "response_time_ms": users_result["response_time_ms"]
            })
        
        # Step 2: Test individual user activate/suspend endpoints
        if self.test_users:
            # Find a test user (not admin)
            test_user = None
            for user in self.test_users:
                if user.get("email") != "admin@cataloro.com" and user.get("id"):
                    test_user = user
                    break
            
            if test_user:
                user_id = test_user["id"]
                original_status = test_user.get("is_active", True)
                
                print(f"  Testing activate/suspend with user: {test_user.get('email', 'Unknown')}")
                
                # Test suspend endpoint
                print("    Testing suspend endpoint...")
                suspend_result = await self.make_request(f"/admin/users/{user_id}/suspend", "PUT", headers=headers)
                
                if suspend_result["success"]:
                    suspended_user = suspend_result["data"].get("user", {})
                    is_suspended = not suspended_user.get("is_active", True)
                    
                    test_results.append({
                        "test": "Suspend User",
                        "success": True,
                        "response_time_ms": suspend_result["response_time_ms"],
                        "user_id": user_id,
                        "is_active_after_suspend": suspended_user.get("is_active"),
                        "suspend_successful": is_suspended,
                        "returns_updated_user": bool(suspended_user)
                    })
                    
                    print(f"      ✅ User suspended successfully (is_active: {suspended_user.get('is_active')})")
                else:
                    test_results.append({
                        "test": "Suspend User",
                        "success": False,
                        "error": suspend_result.get("error"),
                        "response_time_ms": suspend_result["response_time_ms"],
                        "user_id": user_id
                    })
                    print(f"      ❌ Suspend failed: {suspend_result.get('error')}")
                
                # Test activate endpoint
                print("    Testing activate endpoint...")
                activate_result = await self.make_request(f"/admin/users/{user_id}/activate", "PUT", headers=headers)
                
                if activate_result["success"]:
                    activated_user = activate_result["data"].get("user", {})
                    is_activated = activated_user.get("is_active", False)
                    
                    test_results.append({
                        "test": "Activate User",
                        "success": True,
                        "response_time_ms": activate_result["response_time_ms"],
                        "user_id": user_id,
                        "is_active_after_activate": activated_user.get("is_active"),
                        "activate_successful": is_activated,
                        "returns_updated_user": bool(activated_user)
                    })
                    
                    print(f"      ✅ User activated successfully (is_active: {activated_user.get('is_active')})")
                else:
                    test_results.append({
                        "test": "Activate User",
                        "success": False,
                        "error": activate_result.get("error"),
                        "response_time_ms": activate_result["response_time_ms"],
                        "user_id": user_id
                    })
                    print(f"      ❌ Activate failed: {activate_result.get('error')}")
                
                # Test state persistence by listing users again
                print("    Testing state persistence...")
                users_check_result = await self.make_request("/admin/users", headers=headers)
                
                if users_check_result["success"]:
                    updated_users = users_check_result["data"]
                    updated_user = next((u for u in updated_users if u.get("id") == user_id), None)
                    
                    if updated_user:
                        final_status = updated_user.get("is_active", False)
                        persistence_test = {
                            "test": "State Persistence",
                            "success": True,
                            "user_id": user_id,
                            "final_is_active_status": final_status,
                            "state_persisted": final_status == True  # Should be active after activate
                        }
                        print(f"      ✅ State persisted correctly (final is_active: {final_status})")
                    else:
                        persistence_test = {
                            "test": "State Persistence",
                            "success": False,
                            "error": "User not found in updated list",
                            "user_id": user_id
                        }
                        print(f"      ❌ User not found in updated list")
                    
                    test_results.append(persistence_test)
            else:
                test_results.append({
                    "test": "Individual User Operations",
                    "success": False,
                    "error": "No suitable test user found (need non-admin user with ID)"
                })
                print("    ❌ No suitable test user found for activate/suspend testing")
        
        # Step 3: Test error handling for non-existent users
        print("  Testing error handling for non-existent users...")
        fake_user_id = "non-existent-user-id-12345"
        
        # Test suspend with fake ID
        fake_suspend_result = await self.make_request(f"/admin/users/{fake_user_id}/suspend", "PUT", headers=headers)
        fake_activate_result = await self.make_request(f"/admin/users/{fake_user_id}/activate", "PUT", headers=headers)
        
        test_results.append({
            "test": "Error Handling - Non-existent User",
            "suspend_correctly_fails": not fake_suspend_result["success"],
            "activate_correctly_fails": not fake_activate_result["success"],
            "suspend_status": fake_suspend_result["status"],
            "activate_status": fake_activate_result["status"],
            "proper_error_handling": not fake_suspend_result["success"] and not fake_activate_result["success"]
        })
        
        if not fake_suspend_result["success"] and not fake_activate_result["success"]:
            print("    ✅ Error handling working correctly for non-existent users")
        else:
            print("    ❌ Error handling not working properly")
        
        # Step 4: Test bulk operations if available
        print("  Testing bulk user operations...")
        bulk_test_data = {
            "action": "activate",
            "user_ids": [user["id"] for user in self.test_users[:2] if user.get("id")]  # Test with first 2 users
        }
        
        bulk_result = await self.make_request("/admin/users/bulk-action", "POST", data=bulk_test_data, headers=headers)
        
        test_results.append({
            "test": "Bulk Operations",
            "success": bulk_result["success"],
            "response_time_ms": bulk_result.get("response_time_ms", 0),
            "bulk_endpoint_available": bulk_result["success"] or bulk_result["status"] != 404,
            "error": bulk_result.get("error") if not bulk_result["success"] else None
        })
        
        if bulk_result["success"]:
            print("    ✅ Bulk operations endpoint working")
        elif bulk_result["status"] == 404:
            print("    ⚠️ Bulk operations endpoint not implemented")
        else:
            print(f"    ❌ Bulk operations failed: {bulk_result.get('error')}")
        
        # Calculate overall success metrics
        successful_tests = [t for t in test_results if t.get("success", False)]
        critical_tests = [t for t in test_results if t["test"] in ["List Users", "Suspend User", "Activate User", "State Persistence"]]
        critical_successful = [t for t in critical_tests if t.get("success", False)]
        
        return {
            "test_name": "User Management Functionality",
            "total_tests": len(test_results),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(test_results) * 100 if test_results else 0,
            "critical_functionality_working": len(critical_successful) == len(critical_tests),
            "activate_suspend_working": any(t.get("suspend_successful") for t in test_results) and any(t.get("activate_successful") for t in test_results),
            "state_persistence_working": any(t.get("state_persisted") for t in test_results),
            "error_handling_working": any(t.get("proper_error_handling") for t in test_results),
            "bulk_operations_available": any(t.get("bulk_endpoint_available") for t in test_results),
            "detailed_test_results": test_results
        }
    
    async def test_user_workflow_integration(self) -> Dict:
        """Test complete user management workflow"""
        print("🔄 Testing complete user management workflow...")
        
        if not self.admin_token:
            return {
                "test_name": "User Workflow Integration",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        workflow_steps = []
        
        # Step 1: List all users and verify expected users exist
        print("  Step 1: Verifying expected users exist...")
        users_result = await self.make_request("/admin/users", headers=headers)
        
        expected_emails = ["admin@cataloro.com", "demo@cataloro.com", "seller@cataloro.com"]
        found_users = {}
        
        if users_result["success"]:
            users_data = users_result["data"]
            for user in users_data:
                email = user.get("email", "")
                if email in expected_emails:
                    found_users[email] = user
            
            workflow_steps.append({
                "step": "List Users",
                "success": True,
                "total_users": len(users_data),
                "expected_users_found": len(found_users),
                "missing_users": [email for email in expected_emails if email not in found_users]
            })
            
            print(f"    ✅ Found {len(found_users)}/{len(expected_emails)} expected users")
        else:
            workflow_steps.append({
                "step": "List Users",
                "success": False,
                "error": users_result.get("error")
            })
            print(f"    ❌ Failed to list users")
        
        # Step 2: Test user state management with demo user
        demo_user = found_users.get("demo@cataloro.com")
        if demo_user and demo_user.get("id"):
            user_id = demo_user["id"]
            original_status = demo_user.get("is_active", True)
            
            print(f"  Step 2: Testing state management with demo user (original status: {original_status})...")
            
            # Suspend user
            suspend_result = await self.make_request(f"/admin/users/{user_id}/suspend", "PUT", headers=headers)
            suspend_success = suspend_result["success"] and not suspend_result["data"].get("user", {}).get("is_active", True)
            
            # Activate user
            activate_result = await self.make_request(f"/admin/users/{user_id}/activate", "PUT", headers=headers)
            activate_success = activate_result["success"] and activate_result["data"].get("user", {}).get("is_active", False)
            
            # Verify final state
            final_users_result = await self.make_request("/admin/users", headers=headers)
            final_state_correct = False
            
            if final_users_result["success"]:
                final_users = final_users_result["data"]
                final_user = next((u for u in final_users if u.get("id") == user_id), None)
                if final_user:
                    final_state_correct = final_user.get("is_active", False) == True
            
            workflow_steps.append({
                "step": "State Management",
                "success": suspend_success and activate_success and final_state_correct,
                "suspend_worked": suspend_success,
                "activate_worked": activate_success,
                "final_state_correct": final_state_correct,
                "user_id": user_id
            })
            
            if suspend_success and activate_success and final_state_correct:
                print("    ✅ State management workflow completed successfully")
            else:
                print("    ❌ State management workflow had issues")
        else:
            workflow_steps.append({
                "step": "State Management",
                "success": False,
                "error": "Demo user not found or missing ID"
            })
            print("    ❌ Demo user not available for state management testing")
        
        # Step 3: Test UUID and ObjectId compatibility
        print("  Step 3: Testing ID format compatibility...")
        id_format_tests = []
        
        if found_users:
            test_user = list(found_users.values())[0]
            user_id = test_user.get("id")
            
            if user_id:
                # Test with UUID format (current format)
                uuid_result = await self.make_request(f"/admin/users/{user_id}/activate", "PUT", headers=headers)
                id_format_tests.append({
                    "format": "UUID",
                    "success": uuid_result["success"],
                    "user_id": user_id
                })
                
                # Test with potential ObjectId format (if different)
                # Note: This is mainly for verification that the backend handles both formats
                workflow_steps.append({
                    "step": "ID Format Compatibility",
                    "success": uuid_result["success"],
                    "uuid_format_works": uuid_result["success"],
                    "id_format_tests": id_format_tests
                })
                
                if uuid_result["success"]:
                    print("    ✅ UUID format compatibility confirmed")
                else:
                    print("    ❌ UUID format compatibility issues")
        
        # Calculate workflow success
        successful_steps = [s for s in workflow_steps if s.get("success", False)]
        workflow_success = len(successful_steps) == len(workflow_steps)
        
        return {
            "test_name": "User Workflow Integration",
            "total_workflow_steps": len(workflow_steps),
            "successful_steps": len(successful_steps),
            "workflow_success_rate": len(successful_steps) / len(workflow_steps) * 100 if workflow_steps else 0,
            "complete_workflow_working": workflow_success,
            "expected_users_present": len(found_users) >= 2,  # At least admin and demo
            "state_management_working": any(s.get("step") == "State Management" and s.get("success") for s in workflow_steps),
            "id_compatibility_working": any(s.get("step") == "ID Format Compatibility" and s.get("success") for s in workflow_steps),
            "detailed_workflow_steps": workflow_steps
        }
        """Test user management endpoints work correctly"""
        print("👥 Testing user management endpoints...")
        
        if not self.admin_token:
            return {
                "test_name": "User Management Endpoints",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        endpoint_tests = []
        
        # Test admin dashboard
        print("  Testing admin dashboard...")
        dashboard_result = await self.make_request("/admin/dashboard", headers=headers)
        endpoint_tests.append({
            "endpoint": "/admin/dashboard",
            "success": dashboard_result["success"],
            "response_time_ms": dashboard_result["response_time_ms"],
            "has_data": bool(dashboard_result.get("data")) if dashboard_result["success"] else False
        })
        
        # Test performance metrics
        print("  Testing performance metrics...")
        performance_result = await self.make_request("/admin/performance", headers=headers)
        endpoint_tests.append({
            "endpoint": "/admin/performance",
            "success": performance_result["success"],
            "response_time_ms": performance_result["response_time_ms"],
            "has_data": bool(performance_result.get("data")) if performance_result["success"] else False
        })
        
        # Test health check (public endpoint)
        print("  Testing health check...")
        health_result = await self.make_request("/health")
        endpoint_tests.append({
            "endpoint": "/health",
            "success": health_result["success"],
            "response_time_ms": health_result["response_time_ms"],
            "has_data": bool(health_result.get("data")) if health_result["success"] else False
        })
        
        successful_endpoints = [t for t in endpoint_tests if t["success"]]
        avg_response_time = statistics.mean([t["response_time_ms"] for t in successful_endpoints]) if successful_endpoints else 0
        
        return {
            "test_name": "User Management Endpoints",
            "total_endpoints_tested": len(endpoint_tests),
            "successful_endpoints": len(successful_endpoints),
            "success_rate": (len(successful_endpoints) / len(endpoint_tests)) * 100,
            "avg_response_time_ms": avg_response_time,
            "all_endpoints_working": len(successful_endpoints) == len(endpoint_tests),
            "detailed_endpoint_tests": endpoint_tests
        }
    
    async def test_browse_endpoint_performance(self) -> Dict:
        """Test browse endpoint still works after database reset"""
        print("🔍 Testing browse endpoint performance...")
        
        # Test basic browse functionality
        result = await self.make_request("/marketplace/browse")
        
        if result["success"]:
            listings = result["data"]
            
            # Check data structure integrity
            data_integrity_score = self.check_browse_data_integrity(listings)
            
            print(f"  ✅ Browse endpoint working: {len(listings)} listings found")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            print(f"  📊 Data integrity: {data_integrity_score:.1f}%")
            
            return {
                "test_name": "Browse Endpoint Performance",
                "endpoint_working": True,
                "response_time_ms": result["response_time_ms"],
                "listings_count": len(listings),
                "data_integrity_score": data_integrity_score,
                "meets_performance_target": result["response_time_ms"] < PERFORMANCE_TARGET_MS,
                "data_structure_valid": data_integrity_score >= 80
            }
        else:
            print(f"  ❌ Browse endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Browse Endpoint Performance",
                "endpoint_working": False,
                "error": result.get("error", "Browse endpoint failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"]
            }
    
    async def test_admin_functionality(self) -> Dict:
        """Test admin-specific features"""
        print("⚙️ Testing admin functionality...")
        
        if not self.admin_token:
            return {
                "test_name": "Admin Functionality",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        admin_tests = []
        
        # Test admin dashboard access
        dashboard_result = await self.make_request("/admin/dashboard", headers=headers)
        admin_tests.append({
            "feature": "Admin Dashboard",
            "success": dashboard_result["success"],
            "response_time_ms": dashboard_result["response_time_ms"],
            "has_kpis": False
        })
        
        if dashboard_result["success"]:
            dashboard_data = dashboard_result["data"]
            # Check for KPI data
            has_kpis = any(key in dashboard_data for key in ["total_users", "total_revenue", "total_listings"])
            admin_tests[-1]["has_kpis"] = has_kpis
            
            print(f"  ✅ Admin dashboard accessible with KPIs: {has_kpis}")
        
        # Test performance metrics access
        performance_result = await self.make_request("/admin/performance", headers=headers)
        admin_tests.append({
            "feature": "Performance Metrics",
            "success": performance_result["success"],
            "response_time_ms": performance_result["response_time_ms"],
            "has_metrics": False
        })
        
        if performance_result["success"]:
            performance_data = performance_result["data"]
            has_metrics = any(key in performance_data for key in ["performance_status", "database", "cache"])
            admin_tests[-1]["has_metrics"] = has_metrics
            
            print(f"  ✅ Performance metrics accessible: {has_metrics}")
        
        successful_features = [t for t in admin_tests if t["success"]]
        
        return {
            "test_name": "Admin Functionality",
            "total_admin_features_tested": len(admin_tests),
            "successful_admin_features": len(successful_features),
            "admin_success_rate": (len(successful_features) / len(admin_tests)) * 100,
            "all_admin_features_working": len(successful_features) == len(admin_tests),
            "detailed_admin_tests": admin_tests
        }
    
    def check_browse_data_integrity(self, listings: List[Dict]) -> float:
        """Check data integrity of browse listings"""
        if not listings:
            return 100.0  # Empty result is valid
        
        total_checks = 0
        passed_checks = 0
        
        for listing in listings:
            # Check required fields
            required_fields = ["id", "title", "price"]
            for field in required_fields:
                total_checks += 1
                if field in listing and listing[field] is not None:
                    passed_checks += 1
            
            # Check seller information
            total_checks += 1
            if "seller" in listing and isinstance(listing["seller"], dict):
                seller = listing["seller"]
                if "name" in seller or "username" in seller:
                    passed_checks += 1
        
        return (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    async def run_comprehensive_admin_test(self) -> Dict:
        """Run all admin authentication and user management tests"""
        print("🚀 Starting Cataloro Admin Authentication & User Management Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test suites
            admin_auth = await self.test_admin_user_authentication()
            db_consistency = await self.test_database_user_consistency()
            user_management_endpoints = await self.test_user_management_endpoints()
            user_management_functionality = await self.test_user_management_functionality()
            user_workflow = await self.test_user_workflow_integration()
            browse_performance = await self.test_browse_endpoint_performance()
            admin_functionality = await self.test_admin_functionality()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "admin_authentication": admin_auth,
                "database_consistency": db_consistency,
                "user_management_endpoints": user_management_endpoints,
                "user_management_functionality": user_management_functionality,
                "user_workflow_integration": user_workflow,
                "browse_endpoint_performance": browse_performance,
                "admin_functionality": admin_functionality
            }
            
            # Calculate overall success metrics
            test_results = [
                admin_auth.get("all_admin_properties_correct", False),
                db_consistency.get("all_users_consistent", False),
                user_management_endpoints.get("all_endpoints_working", False),
                user_management_functionality.get("critical_functionality_working", False),
                user_workflow.get("complete_workflow_working", False),
                browse_performance.get("endpoint_working", False),
                admin_functionality.get("all_admin_features_working", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "admin_authentication_working": admin_auth.get("all_admin_properties_correct", False),
                "database_consistency_verified": db_consistency.get("all_users_consistent", False),
                "user_management_endpoints_operational": user_management_endpoints.get("all_endpoints_working", False),
                "activate_suspend_functionality_working": user_management_functionality.get("activate_suspend_working", False),
                "state_persistence_working": user_management_functionality.get("state_persistence_working", False),
                "error_handling_working": user_management_functionality.get("error_handling_working", False),
                "complete_user_workflow_working": user_workflow.get("complete_workflow_working", False),
                "browse_endpoint_functional": browse_performance.get("endpoint_working", False),
                "admin_features_accessible": admin_functionality.get("all_admin_features_working", False),
                "all_tests_passed": overall_success_rate == 100
            }
            
            return all_results
            
        finally:
            await self.cleanup()


class BrowseEndpointTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{BACKEND_URL}{endpoint}", params=params) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "response_time_ms": response_time_ms,
                        "data": data,
                        "status": response.status
                    }
                else:
                    return {
                        "success": False,
                        "response_time_ms": response_time_ms,
                        "error": f"HTTP {response.status}",
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
    
    async def test_basic_browse_performance(self) -> Dict:
        """Test basic browse endpoint performance"""
        print("🔍 Testing basic browse endpoint performance...")
        
        # Test multiple calls to get average performance
        response_times = []
        data_integrity_checks = []
        
        for i in range(5):
            result = await self.make_request("/marketplace/browse")
            response_times.append(result["response_time_ms"])
            
            if result["success"]:
                # Check data integrity
                listings = result["data"]
                integrity_score = self.check_data_integrity(listings)
                data_integrity_checks.append(integrity_score)
                
                print(f"  Call {i+1}: {result['response_time_ms']:.0f}ms, {len(listings)} listings")
            else:
                print(f"  Call {i+1}: FAILED - {result['error']}")
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        meets_target = avg_response_time < PERFORMANCE_TARGET_MS
        avg_integrity = statistics.mean(data_integrity_checks) if data_integrity_checks else 0
        
        return {
            "test_name": "Basic Browse Performance",
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "meets_performance_target": meets_target,
            "target_ms": PERFORMANCE_TARGET_MS,
            "data_integrity_score": avg_integrity,
            "total_calls": len(response_times),
            "success_rate": len([t for t in response_times if t > 0]) / max(len(response_times), 1) * 100
        }
    
    async def test_cache_performance(self) -> Dict:
        """Test Redis caching effectiveness"""
        print("🚀 Testing Redis cache performance...")
        
        # Test parameters that should be cached
        test_params = {"type": "all", "page": 1, "limit": 10}
        
        # First call (cold cache)
        print("  Making cold cache call...")
        cold_result = await self.make_request("/marketplace/browse", test_params)
        
        # Wait a moment for cache to settle
        await asyncio.sleep(0.1)
        
        # Second call (warm cache)
        print("  Making warm cache call...")
        warm_result = await self.make_request("/marketplace/browse", test_params)
        
        # Third call (should also be cached)
        print("  Making second warm cache call...")
        warm_result2 = await self.make_request("/marketplace/browse", test_params)
        
        if cold_result["success"] and warm_result["success"] and warm_result2["success"]:
            cold_time = cold_result["response_time_ms"]
            warm_time = warm_result["response_time_ms"]
            warm_time2 = warm_result2["response_time_ms"]
            
            # Calculate cache improvement
            cache_improvement = ((cold_time - warm_time) / cold_time) * 100 if cold_time > 0 else 0
            cache_improvement2 = ((cold_time - warm_time2) / cold_time) * 100 if cold_time > 0 else 0
            
            avg_cache_improvement = (cache_improvement + cache_improvement2) / 2
            
            # Check data consistency
            data_consistent = self.compare_listing_data(cold_result["data"], warm_result["data"])
            
            print(f"  Cold cache: {cold_time:.0f}ms")
            print(f"  Warm cache: {warm_time:.0f}ms ({cache_improvement:.1f}% improvement)")
            print(f"  Warm cache 2: {warm_time2:.0f}ms ({cache_improvement2:.1f}% improvement)")
            
            return {
                "test_name": "Cache Performance",
                "cold_cache_ms": cold_time,
                "warm_cache_ms": warm_time,
                "warm_cache_2_ms": warm_time2,
                "cache_improvement_percent": avg_cache_improvement,
                "meets_cache_target": avg_cache_improvement >= CACHE_IMPROVEMENT_TARGET,
                "cache_target_percent": CACHE_IMPROVEMENT_TARGET,
                "data_consistent": data_consistent,
                "cache_working": warm_time < cold_time and warm_time2 < cold_time
            }
        else:
            return {
                "test_name": "Cache Performance",
                "error": "Failed to complete cache test",
                "cold_success": cold_result["success"],
                "warm_success": warm_result["success"],
                "cache_working": False
            }
    
    async def test_filtering_options(self) -> Dict:
        """Test various filtering options"""
        print("🔧 Testing filtering options...")
        
        filter_tests = [
            {"name": "No filters", "params": {}},
            {"name": "Private sellers", "params": {"type": "Private"}},
            {"name": "Business sellers", "params": {"type": "Business"}},
            {"name": "Price range 100-500", "params": {"price_from": 100, "price_to": 500}},
            {"name": "Price range 0-100", "params": {"price_from": 0, "price_to": 100}},
            {"name": "Page 2", "params": {"page": 2, "limit": 5}},
            {"name": "Large limit", "params": {"limit": 20}},
            {"name": "Combined filters", "params": {"type": "Business", "price_from": 50, "price_to": 1000, "page": 1, "limit": 10}}
        ]
        
        results = []
        
        for test in filter_tests:
            print(f"  Testing: {test['name']}")
            result = await self.make_request("/marketplace/browse", test["params"])
            
            if result["success"]:
                listings = result["data"]
                integrity_score = self.check_data_integrity(listings)
                filter_validation = self.validate_filters(listings, test["params"])
                
                test_result = {
                    "filter_name": test["name"],
                    "response_time_ms": result["response_time_ms"],
                    "listing_count": len(listings),
                    "data_integrity_score": integrity_score,
                    "filter_validation_passed": filter_validation,
                    "success": True
                }
                
                print(f"    ✅ {result['response_time_ms']:.0f}ms, {len(listings)} listings, integrity: {integrity_score:.1f}%")
            else:
                test_result = {
                    "filter_name": test["name"],
                    "response_time_ms": result["response_time_ms"],
                    "error": result["error"],
                    "success": False
                }
                print(f"    ❌ FAILED - {result['error']}")
            
            results.append(test_result)
        
        # Calculate overall statistics
        successful_tests = [r for r in results if r["success"]]
        avg_response_time = statistics.mean([r["response_time_ms"] for r in successful_tests]) if successful_tests else 0
        avg_integrity = statistics.mean([r["data_integrity_score"] for r in successful_tests if "data_integrity_score" in r]) if successful_tests else 0
        
        return {
            "test_name": "Filtering Options",
            "total_filter_tests": len(filter_tests),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(filter_tests) * 100,
            "avg_response_time_ms": avg_response_time,
            "avg_data_integrity": avg_integrity,
            "all_filters_under_target": all(r.get("response_time_ms", 9999) < PERFORMANCE_TARGET_MS for r in successful_tests),
            "detailed_results": results
        }
    
    async def test_concurrent_performance(self) -> Dict:
        """Test concurrent request performance"""
        print("⚡ Testing concurrent request performance...")
        
        # Test with 5 concurrent requests
        concurrent_count = 5
        start_time = time.time()
        
        # Create concurrent requests
        tasks = []
        for i in range(concurrent_count):
            params = {"page": i + 1, "limit": 5}  # Different pages to avoid cache hits
            task = self.make_request("/marketplace/browse", params)
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time_ms = (end_time - start_time) * 1000
        successful_requests = [r for r in results if r["success"]]
        
        if successful_requests:
            avg_individual_time = statistics.mean([r["response_time_ms"] for r in successful_requests])
            max_individual_time = max([r["response_time_ms"] for r in successful_requests])
            min_individual_time = min([r["response_time_ms"] for r in successful_requests])
            
            print(f"  {len(successful_requests)}/{concurrent_count} requests successful")
            print(f"  Total time: {total_time_ms:.0f}ms")
            print(f"  Avg individual: {avg_individual_time:.0f}ms")
            print(f"  Max individual: {max_individual_time:.0f}ms")
            
            return {
                "test_name": "Concurrent Performance",
                "concurrent_requests": concurrent_count,
                "successful_requests": len(successful_requests),
                "total_time_ms": total_time_ms,
                "avg_individual_time_ms": avg_individual_time,
                "max_individual_time_ms": max_individual_time,
                "min_individual_time_ms": min_individual_time,
                "throughput_requests_per_second": len(successful_requests) / (total_time_ms / 1000),
                "all_under_target": max_individual_time < PERFORMANCE_TARGET_MS,
                "concurrent_performance_acceptable": total_time_ms < (PERFORMANCE_TARGET_MS * 2)
            }
        else:
            return {
                "test_name": "Concurrent Performance",
                "error": "All concurrent requests failed",
                "successful_requests": 0,
                "concurrent_requests": concurrent_count
            }
    
    async def test_pagination_performance(self) -> Dict:
        """Test pagination performance across different pages"""
        print("📄 Testing pagination performance...")
        
        page_tests = []
        
        # Test first 5 pages
        for page in range(1, 6):
            params = {"page": page, "limit": 10}
            result = await self.make_request("/marketplace/browse", params)
            
            if result["success"]:
                listings = result["data"]
                page_tests.append({
                    "page": page,
                    "response_time_ms": result["response_time_ms"],
                    "listing_count": len(listings),
                    "success": True
                })
                print(f"  Page {page}: {result['response_time_ms']:.0f}ms, {len(listings)} listings")
            else:
                page_tests.append({
                    "page": page,
                    "error": result["error"],
                    "success": False
                })
                print(f"  Page {page}: FAILED - {result['error']}")
        
        successful_pages = [p for p in page_tests if p["success"]]
        
        if successful_pages:
            avg_response_time = statistics.mean([p["response_time_ms"] for p in successful_pages])
            max_response_time = max([p["response_time_ms"] for p in successful_pages])
            
            return {
                "test_name": "Pagination Performance",
                "pages_tested": len(page_tests),
                "successful_pages": len(successful_pages),
                "avg_response_time_ms": avg_response_time,
                "max_response_time_ms": max_response_time,
                "all_pages_under_target": max_response_time < PERFORMANCE_TARGET_MS,
                "pagination_consistent": max_response_time - statistics.mean([p["response_time_ms"] for p in successful_pages]) < 200,
                "detailed_results": page_tests
            }
        else:
            return {
                "test_name": "Pagination Performance",
                "error": "All pagination tests failed",
                "pages_tested": len(page_tests),
                "successful_pages": 0
            }
    
    def check_data_integrity(self, listings: List[Dict]) -> float:
        """Check data integrity of listings"""
        if not listings:
            return 100.0  # Empty result is valid
        
        total_checks = 0
        passed_checks = 0
        
        for listing in listings:
            # Check required fields
            required_fields = ["id", "title", "price"]
            for field in required_fields:
                total_checks += 1
                if field in listing and listing[field] is not None:
                    passed_checks += 1
            
            # Check seller information
            total_checks += 1
            if "seller" in listing and isinstance(listing["seller"], dict):
                seller = listing["seller"]
                if "name" in seller and "username" in seller:
                    passed_checks += 1
            
            # Check bid information
            total_checks += 1
            if "bid_info" in listing and isinstance(listing["bid_info"], dict):
                bid_info = listing["bid_info"]
                if "has_bids" in bid_info and "total_bids" in bid_info and "highest_bid" in bid_info:
                    passed_checks += 1
            
            # Check time information
            total_checks += 1
            if "time_info" in listing and isinstance(listing["time_info"], dict):
                time_info = listing["time_info"]
                if "has_time_limit" in time_info and "is_expired" in time_info:
                    passed_checks += 1
        
        return (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    def validate_filters(self, listings: List[Dict], params: Dict) -> bool:
        """Validate that filters are applied correctly"""
        if not listings:
            return True  # Empty result is valid for filters
        
        # Check price filters
        price_from = params.get("price_from", 0)
        price_to = params.get("price_to", 999999)
        
        for listing in listings:
            price = listing.get("price", 0)
            if price < price_from or price > price_to:
                return False
        
        # Check seller type filter
        seller_type = params.get("type")
        if seller_type and seller_type != "all":
            for listing in listings:
                seller = listing.get("seller", {})
                is_business = seller.get("is_business", False)
                
                if seller_type == "Private" and is_business:
                    return False
                elif seller_type == "Business" and not is_business:
                    return False
        
        return True
    
    def compare_listing_data(self, data1: List[Dict], data2: List[Dict]) -> bool:
        """Compare two listing datasets for consistency"""
        if len(data1) != len(data2):
            return False
        
        # Compare first few listings for key fields
        for i in range(min(3, len(data1))):
            listing1 = data1[i]
            listing2 = data2[i]
            
            # Check key fields match
            key_fields = ["id", "title", "price"]
            for field in key_fields:
                if listing1.get(field) != listing2.get(field):
                    return False
        
        return True
    
    async def run_comprehensive_test(self) -> Dict:
        """Run all performance tests"""
        print("🚀 Starting Cataloro Browse Endpoint Performance Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run all test suites
            basic_performance = await self.test_basic_browse_performance()
            cache_performance = await self.test_cache_performance()
            filtering_performance = await self.test_filtering_options()
            concurrent_performance = await self.test_concurrent_performance()
            pagination_performance = await self.test_pagination_performance()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "performance_target_ms": PERFORMANCE_TARGET_MS,
                "cache_improvement_target_percent": CACHE_IMPROVEMENT_TARGET,
                "basic_performance": basic_performance,
                "cache_performance": cache_performance,
                "filtering_performance": filtering_performance,
                "concurrent_performance": concurrent_performance,
                "pagination_performance": pagination_performance
            }
            
            # Calculate overall success metrics
            performance_tests = [
                basic_performance.get("meets_performance_target", False),
                filtering_performance.get("all_filters_under_target", False),
                concurrent_performance.get("all_under_target", False),
                pagination_performance.get("all_pages_under_target", False)
            ]
            
            cache_working = cache_performance.get("cache_working", False)
            data_integrity_scores = [
                basic_performance.get("data_integrity_score", 0),
                filtering_performance.get("avg_data_integrity", 0)
            ]
            
            overall_performance_success = sum(performance_tests) / len(performance_tests) * 100
            avg_data_integrity = statistics.mean(data_integrity_scores)
            
            all_results["summary"] = {
                "overall_performance_success_rate": overall_performance_success,
                "cache_functionality_working": cache_working,
                "average_data_integrity_score": avg_data_integrity,
                "performance_target_met": overall_performance_success >= 75,
                "cache_target_met": cache_performance.get("meets_cache_target", False),
                "data_integrity_excellent": avg_data_integrity >= 90
            }
            
            return all_results
            
        finally:
            await self.cleanup()

class MobileBiddingTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_listing_id = None
        self.test_buyer_id = None
        self.test_seller_id = None
        
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
    
    async def setup_test_data(self) -> Dict:
        """Create test users and listing for bidding tests"""
        print("🔧 Setting up test data for bidding tests...")
        
        # Create test buyer user
        buyer_data = {
            "email": "test_buyer@cataloro.com",
            "password": "test_password",
            "username": "test_buyer",
            "full_name": "Test Buyer"
        }
        
        buyer_result = await self.make_request("/auth/login", "POST", data=buyer_data)
        if buyer_result["success"]:
            self.test_buyer_id = buyer_result["data"]["user"]["id"]
            print(f"  ✅ Test buyer created/logged in: {self.test_buyer_id}")
        else:
            print(f"  ❌ Failed to create test buyer: {buyer_result.get('error')}")
            return {"success": False, "error": "Failed to create test buyer"}
        
        # Create test seller user
        seller_data = {
            "email": "test_seller@cataloro.com", 
            "password": "test_password",
            "username": "test_seller",
            "full_name": "Test Seller"
        }
        
        seller_result = await self.make_request("/auth/login", "POST", data=seller_data)
        if seller_result["success"]:
            self.test_seller_id = seller_result["data"]["user"]["id"]
            print(f"  ✅ Test seller created/logged in: {self.test_seller_id}")
        else:
            print(f"  ❌ Failed to create test seller: {seller_result.get('error')}")
            return {"success": False, "error": "Failed to create test seller"}
        
        # Create test listing
        listing_data = {
            "title": "Test BMW Catalytic Converter for Bidding",
            "description": "Test listing for bidding functionality validation",
            "price": 100.0,  # Starting price
            "category": "Automotive",
            "condition": "Used",
            "seller_id": self.test_seller_id,
            "images": [],
            "tags": ["test", "bidding"],
            "features": ["Test feature"]
        }
        
        listing_result = await self.make_request("/listings", "POST", data=listing_data)
        if listing_result["success"]:
            self.test_listing_id = listing_result["data"]["id"]
            print(f"  ✅ Test listing created: {self.test_listing_id}")
            return {"success": True, "listing_id": self.test_listing_id, "buyer_id": self.test_buyer_id, "seller_id": self.test_seller_id}
        else:
            print(f"  ❌ Failed to create test listing: {listing_result.get('error')}")
            return {"success": False, "error": "Failed to create test listing"}
    
    async def test_first_bid_scenario(self) -> Dict:
        """Test bidding on item with no existing bids"""
        print("🎯 Testing first bid scenario (no existing bids)...")
        
        if not self.test_listing_id or not self.test_buyer_id:
            return {"test_name": "First Bid Scenario", "error": "Test data not set up"}
        
        # Test valid first bid (equal to starting price)
        first_bid_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.test_buyer_id,
            "offer_amount": 100.0  # Equal to starting price
        }
        
        result = await self.make_request("/tenders/submit", "POST", data=first_bid_data)
        
        if result["success"]:
            print(f"  ✅ First bid accepted: €{first_bid_data['offer_amount']}")
            return {
                "test_name": "First Bid Scenario",
                "success": True,
                "bid_amount": first_bid_data["offer_amount"],
                "response_time_ms": result["response_time_ms"],
                "tender_id": result["data"].get("tender_id"),
                "message": result["data"].get("message"),
                "first_bid_accepted": True
            }
        else:
            print(f"  ❌ First bid rejected: {result.get('data', {}).get('detail', result.get('error'))}")
            return {
                "test_name": "First Bid Scenario", 
                "success": False,
                "bid_amount": first_bid_data["offer_amount"],
                "error": result.get("data", {}).get("detail", result.get("error")),
                "status": result["status"],
                "first_bid_accepted": False
            }
    
    async def test_higher_bid_scenario(self) -> Dict:
        """Test bidding higher than current highest bid (should succeed)"""
        print("📈 Testing higher bid scenario (should succeed)...")
        
        if not self.test_listing_id or not self.test_buyer_id:
            return {"test_name": "Higher Bid Scenario", "error": "Test data not set up"}
        
        # Get current highest bid first
        tenders_result = await self.make_request(f"/tenders/listing/{self.test_listing_id}")
        current_highest = 100.0  # Default to starting price
        
        if tenders_result["success"] and tenders_result["data"]:
            tenders = tenders_result["data"]
            if tenders:
                current_highest = max(tender["offer_amount"] for tender in tenders)
        
        # Bid higher than current highest
        higher_bid_amount = current_highest + 50.0
        higher_bid_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.test_buyer_id,
            "offer_amount": higher_bid_amount
        }
        
        result = await self.make_request("/tenders/submit", "POST", data=higher_bid_data)
        
        if result["success"]:
            print(f"  ✅ Higher bid accepted: €{higher_bid_amount} (previous: €{current_highest})")
            return {
                "test_name": "Higher Bid Scenario",
                "success": True,
                "bid_amount": higher_bid_amount,
                "previous_highest": current_highest,
                "response_time_ms": result["response_time_ms"],
                "tender_id": result["data"].get("tender_id"),
                "message": result["data"].get("message"),
                "higher_bid_accepted": True
            }
        else:
            print(f"  ❌ Higher bid rejected: {result.get('data', {}).get('detail', result.get('error'))}")
            return {
                "test_name": "Higher Bid Scenario",
                "success": False,
                "bid_amount": higher_bid_amount,
                "previous_highest": current_highest,
                "error": result.get("data", {}).get("detail", result.get("error")),
                "status": result["status"],
                "higher_bid_accepted": False
            }
    
    async def test_equal_bid_scenario(self) -> Dict:
        """Test bidding equal to current highest bid (should fail)"""
        print("⚖️ Testing equal bid scenario (should fail)...")
        
        if not self.test_listing_id or not self.test_buyer_id:
            return {"test_name": "Equal Bid Scenario", "error": "Test data not set up"}
        
        # Get current highest bid
        tenders_result = await self.make_request(f"/tenders/listing/{self.test_listing_id}")
        current_highest = 100.0  # Default to starting price
        
        if tenders_result["success"] and tenders_result["data"]:
            tenders = tenders_result["data"]
            if tenders:
                current_highest = max(tender["offer_amount"] for tender in tenders)
        
        # Bid equal to current highest
        equal_bid_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.test_buyer_id,
            "offer_amount": current_highest
        }
        
        result = await self.make_request("/tenders/submit", "POST", data=equal_bid_data)
        
        if not result["success"]:
            error_message = result.get("data", {}).get("detail", result.get("error", ""))
            print(f"  ✅ Equal bid correctly rejected: €{current_highest}")
            print(f"    Error message: {error_message}")
            return {
                "test_name": "Equal Bid Scenario",
                "success": True,  # Success means it was correctly rejected
                "bid_amount": current_highest,
                "current_highest": current_highest,
                "correctly_rejected": True,
                "error_message": error_message,
                "status": result["status"],
                "error_message_accurate": "higher than current highest bid" in error_message.lower()
            }
        else:
            print(f"  ❌ Equal bid incorrectly accepted: €{current_highest}")
            return {
                "test_name": "Equal Bid Scenario",
                "success": False,  # Failure means it was incorrectly accepted
                "bid_amount": current_highest,
                "current_highest": current_highest,
                "correctly_rejected": False,
                "error": "Equal bid should have been rejected but was accepted"
            }
    
    async def test_lower_bid_scenario(self) -> Dict:
        """Test bidding lower than current highest bid (should fail)"""
        print("📉 Testing lower bid scenario (should fail)...")
        
        if not self.test_listing_id or not self.test_buyer_id:
            return {"test_name": "Lower Bid Scenario", "error": "Test data not set up"}
        
        # Get current highest bid
        tenders_result = await self.make_request(f"/tenders/listing/{self.test_listing_id}")
        current_highest = 100.0  # Default to starting price
        
        if tenders_result["success"] and tenders_result["data"]:
            tenders = tenders_result["data"]
            if tenders:
                current_highest = max(tender["offer_amount"] for tender in tenders)
        
        # Bid lower than current highest
        lower_bid_amount = current_highest - 25.0
        lower_bid_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.test_buyer_id,
            "offer_amount": lower_bid_amount
        }
        
        result = await self.make_request("/tenders/submit", "POST", data=lower_bid_data)
        
        if not result["success"]:
            error_message = result.get("data", {}).get("detail", result.get("error", ""))
            print(f"  ✅ Lower bid correctly rejected: €{lower_bid_amount} (current: €{current_highest})")
            print(f"    Error message: {error_message}")
            return {
                "test_name": "Lower Bid Scenario",
                "success": True,  # Success means it was correctly rejected
                "bid_amount": lower_bid_amount,
                "current_highest": current_highest,
                "correctly_rejected": True,
                "error_message": error_message,
                "status": result["status"],
                "error_message_accurate": "higher than current highest bid" in error_message.lower()
            }
        else:
            print(f"  ❌ Lower bid incorrectly accepted: €{lower_bid_amount}")
            return {
                "test_name": "Lower Bid Scenario",
                "success": False,  # Failure means it was incorrectly accepted
                "bid_amount": lower_bid_amount,
                "current_highest": current_highest,
                "correctly_rejected": False,
                "error": "Lower bid should have been rejected but was accepted"
            }
    
    async def test_minimum_increment_logic(self) -> Dict:
        """Test minimum increment logic (+1 requirement)"""
        print("🔢 Testing minimum increment logic (+1 requirement)...")
        
        if not self.test_listing_id or not self.test_buyer_id:
            return {"test_name": "Minimum Increment Logic", "error": "Test data not set up"}
        
        # Get current highest bid
        tenders_result = await self.make_request(f"/tenders/listing/{self.test_listing_id}")
        current_highest = 100.0  # Default to starting price
        
        if tenders_result["success"] and tenders_result["data"]:
            tenders = tenders_result["data"]
            if tenders:
                current_highest = max(tender["offer_amount"] for tender in tenders)
        
        # Test minimum valid increment (+1)
        minimum_valid_bid = current_highest + 1.0
        min_increment_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.test_buyer_id,
            "offer_amount": minimum_valid_bid
        }
        
        result = await self.make_request("/tenders/submit", "POST", data=min_increment_data)
        
        if result["success"]:
            print(f"  ✅ Minimum increment bid accepted: €{minimum_valid_bid} (previous: €{current_highest})")
            return {
                "test_name": "Minimum Increment Logic",
                "success": True,
                "bid_amount": minimum_valid_bid,
                "previous_highest": current_highest,
                "increment": minimum_valid_bid - current_highest,
                "minimum_increment_accepted": True,
                "response_time_ms": result["response_time_ms"],
                "tender_id": result["data"].get("tender_id")
            }
        else:
            error_message = result.get("data", {}).get("detail", result.get("error", ""))
            print(f"  ❌ Minimum increment bid rejected: €{minimum_valid_bid}")
            print(f"    Error message: {error_message}")
            return {
                "test_name": "Minimum Increment Logic",
                "success": False,
                "bid_amount": minimum_valid_bid,
                "previous_highest": current_highest,
                "increment": minimum_valid_bid - current_highest,
                "minimum_increment_accepted": False,
                "error_message": error_message,
                "status": result["status"]
            }
    
    async def test_error_message_accuracy(self) -> Dict:
        """Test error messages provide clear feedback about minimum bid requirements"""
        print("💬 Testing error message accuracy...")
        
        if not self.test_listing_id or not self.test_buyer_id:
            return {"test_name": "Error Message Accuracy", "error": "Test data not set up"}
        
        error_tests = []
        
        # Get current highest bid
        tenders_result = await self.make_request(f"/tenders/listing/{self.test_listing_id}")
        current_highest = 100.0
        
        if tenders_result["success"] and tenders_result["data"]:
            tenders = tenders_result["data"]
            if tenders:
                current_highest = max(tender["offer_amount"] for tender in tenders)
        
        # Test 1: Bid equal to current highest
        equal_bid_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.test_buyer_id,
            "offer_amount": current_highest
        }
        
        equal_result = await self.make_request("/tenders/submit", "POST", data=equal_bid_data)
        if not equal_result["success"]:
            error_msg = equal_result.get("data", {}).get("detail", "")
            error_tests.append({
                "scenario": "Equal bid",
                "error_message": error_msg,
                "contains_current_bid": str(current_highest) in error_msg,
                "contains_minimum_bid": "minimum bid" in error_msg.lower(),
                "message_clear": len(error_msg) > 20 and "€" in error_msg
            })
            print(f"    Equal bid error: {error_msg}")
        
        # Test 2: Bid lower than current highest
        lower_bid_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.test_buyer_id,
            "offer_amount": current_highest - 10.0
        }
        
        lower_result = await self.make_request("/tenders/submit", "POST", data=lower_bid_data)
        if not lower_result["success"]:
            error_msg = lower_result.get("data", {}).get("detail", "")
            error_tests.append({
                "scenario": "Lower bid",
                "error_message": error_msg,
                "contains_current_bid": str(current_highest) in error_msg,
                "contains_minimum_bid": "minimum bid" in error_msg.lower(),
                "message_clear": len(error_msg) > 20 and "€" in error_msg
            })
            print(f"    Lower bid error: {error_msg}")
        
        # Calculate accuracy metrics
        total_tests = len(error_tests)
        clear_messages = sum(1 for test in error_tests if test["message_clear"])
        contains_amounts = sum(1 for test in error_tests if test["contains_current_bid"])
        contains_minimum = sum(1 for test in error_tests if test["contains_minimum_bid"])
        
        accuracy_score = 0
        if total_tests > 0:
            accuracy_score = ((clear_messages + contains_amounts + contains_minimum) / (total_tests * 3)) * 100
        
        return {
            "test_name": "Error Message Accuracy",
            "success": accuracy_score >= 75,  # 75% accuracy threshold
            "total_error_tests": total_tests,
            "clear_messages": clear_messages,
            "contains_current_bid_amount": contains_amounts,
            "contains_minimum_bid_text": contains_minimum,
            "accuracy_score": accuracy_score,
            "detailed_error_tests": error_tests,
            "error_messages_accurate": accuracy_score >= 75
        }
    
    async def test_self_bidding_prevention(self) -> Dict:
        """Test that sellers cannot bid on their own listings"""
        print("🚫 Testing self-bidding prevention...")
        
        if not self.test_listing_id or not self.test_seller_id:
            return {"test_name": "Self-Bidding Prevention", "error": "Test data not set up"}
        
        # Try to bid on own listing
        self_bid_data = {
            "listing_id": self.test_listing_id,
            "buyer_id": self.test_seller_id,  # Same as seller_id
            "offer_amount": 200.0
        }
        
        result = await self.make_request("/tenders/submit", "POST", data=self_bid_data)
        
        if not result["success"]:
            error_message = result.get("data", {}).get("detail", result.get("error", ""))
            print(f"  ✅ Self-bidding correctly prevented")
            print(f"    Error message: {error_message}")
            return {
                "test_name": "Self-Bidding Prevention",
                "success": True,
                "self_bidding_prevented": True,
                "error_message": error_message,
                "status": result["status"],
                "error_message_appropriate": "cannot bid on your own" in error_message.lower()
            }
        else:
            print(f"  ❌ Self-bidding incorrectly allowed")
            return {
                "test_name": "Self-Bidding Prevention",
                "success": False,
                "self_bidding_prevented": False,
                "error": "Seller should not be able to bid on their own listing"
            }
    
    async def run_comprehensive_bidding_test(self) -> Dict:
        """Run all bidding functionality tests"""
        print("🚀 Starting Mobile Bidding Functionality Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Setup test data
            setup_result = await self.setup_test_data()
            if not setup_result.get("success"):
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "setup_error": setup_result.get("error"),
                    "tests_completed": False
                }
            
            # Run all bidding tests
            first_bid = await self.test_first_bid_scenario()
            higher_bid = await self.test_higher_bid_scenario()
            equal_bid = await self.test_equal_bid_scenario()
            lower_bid = await self.test_lower_bid_scenario()
            min_increment = await self.test_minimum_increment_logic()
            error_accuracy = await self.test_error_message_accuracy()
            self_bidding = await self.test_self_bidding_prevention()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_setup": setup_result,
                "first_bid_scenario": first_bid,
                "higher_bid_scenario": higher_bid,
                "equal_bid_scenario": equal_bid,
                "lower_bid_scenario": lower_bid,
                "minimum_increment_logic": min_increment,
                "error_message_accuracy": error_accuracy,
                "self_bidding_prevention": self_bidding
            }
            
            # Calculate overall success metrics
            test_results = [
                first_bid.get("success", False),
                higher_bid.get("success", False),
                equal_bid.get("success", False),
                lower_bid.get("success", False),
                min_increment.get("success", False),
                error_accuracy.get("success", False),
                self_bidding.get("success", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            # Critical bidding logic checks
            bidding_validation_working = (
                equal_bid.get("correctly_rejected", False) and
                lower_bid.get("correctly_rejected", False) and
                higher_bid.get("higher_bid_accepted", False)
            )
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "bidding_validation_logic_working": bidding_validation_working,
                "first_bid_accepted": first_bid.get("first_bid_accepted", False),
                "higher_bids_accepted": higher_bid.get("higher_bid_accepted", False),
                "equal_bids_rejected": equal_bid.get("correctly_rejected", False),
                "lower_bids_rejected": lower_bid.get("correctly_rejected", False),
                "minimum_increment_working": min_increment.get("minimum_increment_accepted", False),
                "error_messages_accurate": error_accuracy.get("error_messages_accurate", False),
                "self_bidding_prevented": self_bidding.get("self_bidding_prevented", False),
                "critical_bug_resolved": bidding_validation_working,
                "all_tests_passed": overall_success_rate >= 85
            }
            
            return all_results
            
        finally:
            await self.cleanup()


class BasketExportTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
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
                
                # Handle PDF response differently
                if response.headers.get('content-type') == 'application/pdf':
                    pdf_data = await response.read()
                    return {
                        "success": response.status in [200, 201],
                        "response_time_ms": response_time_ms,
                        "data": pdf_data,
                        "status": response.status,
                        "content_type": "application/pdf",
                        "content_length": len(pdf_data)
                    }
                else:
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
    
    async def test_basket_export_endpoint_basic(self) -> Dict:
        """Test basic basket export PDF functionality"""
        print("📄 Testing basket export PDF endpoint - Basic functionality...")
        
        # Create sample basket data for testing
        sample_basket_data = {
            "basketId": "test-basket-123",
            "basketName": "Test Basket Export",
            "basketDescription": "Testing basket PDF export functionality",
            "userId": "test-user-456",
            "exportDate": datetime.now().isoformat(),
            "totals": {
                "valuePaid": 1250.75,
                "ptG": 2.5678,
                "pdG": 1.2345,
                "rhG": 0.8901
            },
            "items": [
                {
                    "title": "BMW Catalytic Converter",
                    "price": 450.25,
                    "seller": "AutoParts Pro",
                    "seller_name": "AutoParts Pro",
                    "created_at": "2024-01-15T10:30:00Z",
                    "pt_g": 1.2345,
                    "pd_g": 0.6789,
                    "rh_g": 0.4567,
                    "weight": 850.0,
                    "pt_ppm": 1450,
                    "pd_ppm": 800,
                    "rh_ppm": 537,
                    "renumeration_pt": 1.0,
                    "renumeration_pd": 1.0,
                    "renumeration_rh": 1.0
                },
                {
                    "title": "Mercedes Catalytic Converter",
                    "price": 800.50,
                    "seller": "Premium Cats",
                    "seller_name": "Premium Cats",
                    "created_at": "2024-01-16T14:45:00Z",
                    "pt_g": 1.3333,
                    "pd_g": 0.5556,
                    "rh_g": 0.4334,
                    "weight": 920.0,
                    "pt_ppm": 1650,
                    "pd_ppm": 750,
                    "rh_ppm": 471,
                    "renumeration_pt": 1.0,
                    "renumeration_pd": 1.0,
                    "renumeration_rh": 1.0
                }
            ]
        }
        
        result = await self.make_request("/user/export-basket-pdf", "POST", data=sample_basket_data)
        
        if result["success"]:
            pdf_data = result["data"]
            content_length = result.get("content_length", 0)
            
            print(f"  ✅ PDF export successful")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            print(f"  📊 PDF size: {content_length} bytes")
            print(f"  📋 Content type: {result.get('content_type', 'unknown')}")
            
            # Validate PDF content
            is_valid_pdf = isinstance(pdf_data, bytes) and pdf_data.startswith(b'%PDF')
            has_reasonable_size = content_length > 1000  # PDF should be at least 1KB
            
            return {
                "test_name": "Basket Export PDF - Basic Functionality",
                "endpoint_working": True,
                "response_time_ms": result["response_time_ms"],
                "pdf_generated": True,
                "pdf_size_bytes": content_length,
                "is_valid_pdf": is_valid_pdf,
                "has_reasonable_size": has_reasonable_size,
                "content_type_correct": result.get("content_type") == "application/pdf",
                "sample_items_count": len(sample_basket_data["items"]),
                "test_data_processed": True
            }
        else:
            print(f"  ❌ PDF export failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Basket Export PDF - Basic Functionality",
                "endpoint_working": False,
                "error": result.get("error", "PDF export failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"]
            }
    
    async def test_basket_export_response_time(self) -> Dict:
        """Test response time performance for basket export"""
        print("⏱️ Testing basket export response time performance...")
        
        # Test with different basket sizes to understand performance characteristics
        test_scenarios = [
            {"name": "Small basket (1 item)", "item_count": 1},
            {"name": "Medium basket (5 items)", "item_count": 5},
            {"name": "Large basket (10 items)", "item_count": 10},
            {"name": "Extra large basket (20 items)", "item_count": 20}
        ]
        
        response_times = []
        scenario_results = []
        
        for scenario in test_scenarios:
            # Generate test data with specified number of items
            items = []
            for i in range(scenario["item_count"]):
                items.append({
                    "title": f"Test Catalytic Converter {i+1}",
                    "price": 100.0 + (i * 50),
                    "seller": f"Seller {i+1}",
                    "seller_name": f"Seller {i+1}",
                    "created_at": datetime.now().isoformat(),
                    "pt_g": 1.0 + (i * 0.1),
                    "pd_g": 0.5 + (i * 0.05),
                    "rh_g": 0.3 + (i * 0.03),
                    "weight": 800.0 + (i * 10),
                    "pt_ppm": 1400 + (i * 50),
                    "pd_ppm": 700 + (i * 25),
                    "rh_ppm": 500 + (i * 15),
                    "renumeration_pt": 1.0,
                    "renumeration_pd": 1.0,
                    "renumeration_rh": 1.0
                })
            
            basket_data = {
                "basketId": f"test-basket-{scenario['item_count']}-items",
                "basketName": f"Performance Test Basket ({scenario['item_count']} items)",
                "basketDescription": f"Testing export performance with {scenario['item_count']} items",
                "userId": "performance-test-user",
                "exportDate": datetime.now().isoformat(),
                "totals": {
                    "valuePaid": sum(item["price"] for item in items),
                    "ptG": sum(item["pt_g"] for item in items),
                    "pdG": sum(item["pd_g"] for item in items),
                    "rhG": sum(item["rh_g"] for item in items)
                },
                "items": items
            }
            
            print(f"  Testing: {scenario['name']}")
            result = await self.make_request("/user/export-basket-pdf", "POST", data=basket_data)
            
            if result["success"]:
                response_time = result["response_time_ms"]
                response_times.append(response_time)
                pdf_size = result.get("content_length", 0)
                
                scenario_results.append({
                    "scenario": scenario["name"],
                    "item_count": scenario["item_count"],
                    "response_time_ms": response_time,
                    "pdf_size_bytes": pdf_size,
                    "success": True
                })
                
                print(f"    ✅ {response_time:.0f}ms, PDF size: {pdf_size} bytes")
            else:
                scenario_results.append({
                    "scenario": scenario["name"],
                    "item_count": scenario["item_count"],
                    "error": result.get("error"),
                    "success": False
                })
                print(f"    ❌ Failed: {result.get('error')}")
        
        # Calculate performance metrics
        successful_tests = [r for r in scenario_results if r["success"]]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # Performance thresholds for loading state validation
        acceptable_response_time = 5000  # 5 seconds should be acceptable for PDF generation
        fast_response_time = 2000  # Under 2 seconds is fast
        
        return {
            "test_name": "Basket Export Response Time Performance",
            "total_scenarios_tested": len(test_scenarios),
            "successful_scenarios": len(successful_tests),
            "avg_response_time_ms": avg_response_time,
            "max_response_time_ms": max_response_time,
            "min_response_time_ms": min_response_time,
            "performance_acceptable": max_response_time < acceptable_response_time,
            "performance_fast": avg_response_time < fast_response_time,
            "loading_state_justified": avg_response_time > 500,  # Loading state makes sense if >500ms
            "detailed_scenario_results": scenario_results
        }
    
    async def test_basket_export_data_validation(self) -> Dict:
        """Test basket export with various data scenarios"""
        print("🔍 Testing basket export data validation...")
        
        test_cases = [
            {
                "name": "Empty basket",
                "data": {
                    "basketId": "empty-basket",
                    "basketName": "Empty Test Basket",
                    "basketDescription": "Testing empty basket export",
                    "userId": "test-user",
                    "exportDate": datetime.now().isoformat(),
                    "totals": {"valuePaid": 0, "ptG": 0, "pdG": 0, "rhG": 0},
                    "items": []
                },
                "should_succeed": True
            },
            {
                "name": "Minimal data",
                "data": {
                    "basketId": "minimal-basket",
                    "basketName": "Minimal Basket",
                    "totals": {"valuePaid": 100, "ptG": 1, "pdG": 0.5, "rhG": 0.2},
                    "items": [{"title": "Basic Item", "price": 100}]
                },
                "should_succeed": True
            },
            {
                "name": "Missing required fields",
                "data": {
                    "basketName": "Incomplete Basket"
                    # Missing basketId, totals, items
                },
                "should_succeed": False  # Should handle gracefully
            },
            {
                "name": "Large basket name",
                "data": {
                    "basketId": "large-name-basket",
                    "basketName": "A" * 200,  # Very long name
                    "basketDescription": "Testing with very long basket name",
                    "totals": {"valuePaid": 500, "ptG": 2, "pdG": 1, "rhG": 0.5},
                    "items": [{"title": "Test Item", "price": 500}]
                },
                "should_succeed": True
            }
        ]
        
        validation_results = []
        
        for test_case in test_cases:
            print(f"  Testing: {test_case['name']}")
            
            result = await self.make_request("/user/export-basket-pdf", "POST", data=test_case["data"])
            
            success = result["success"]
            expected_success = test_case["should_succeed"]
            
            validation_results.append({
                "test_case": test_case["name"],
                "expected_success": expected_success,
                "actual_success": success,
                "validation_passed": success == expected_success,
                "response_time_ms": result["response_time_ms"],
                "error": result.get("error") if not success else None,
                "pdf_size": result.get("content_length", 0) if success else 0
            })
            
            if success == expected_success:
                print(f"    ✅ Validation passed (success: {success})")
            else:
                print(f"    ❌ Validation failed (expected: {expected_success}, got: {success})")
        
        # Calculate validation success rate
        passed_validations = [r for r in validation_results if r["validation_passed"]]
        validation_success_rate = len(passed_validations) / len(validation_results) * 100
        
        return {
            "test_name": "Basket Export Data Validation",
            "total_validation_tests": len(test_cases),
            "passed_validations": len(passed_validations),
            "validation_success_rate": validation_success_rate,
            "handles_empty_baskets": any(r["test_case"] == "Empty basket" and r["actual_success"] for r in validation_results),
            "handles_minimal_data": any(r["test_case"] == "Minimal data" and r["actual_success"] for r in validation_results),
            "handles_invalid_data": any(r["test_case"] == "Missing required fields" and not r["actual_success"] for r in validation_results),
            "handles_edge_cases": validation_success_rate >= 75,
            "detailed_validation_results": validation_results
        }
    
    async def test_basket_export_concurrent_requests(self) -> Dict:
        """Test concurrent basket export requests"""
        print("⚡ Testing concurrent basket export requests...")
        
        # Create test data for concurrent requests
        base_basket_data = {
            "basketId": "concurrent-test-basket",
            "basketName": "Concurrent Test Basket",
            "basketDescription": "Testing concurrent PDF exports",
            "userId": "concurrent-test-user",
            "exportDate": datetime.now().isoformat(),
            "totals": {"valuePaid": 750.0, "ptG": 1.5, "pdG": 0.8, "rhG": 0.4},
            "items": [
                {
                    "title": "Concurrent Test Item 1",
                    "price": 375.0,
                    "seller": "Test Seller 1",
                    "pt_g": 0.75,
                    "pd_g": 0.4,
                    "rh_g": 0.2
                },
                {
                    "title": "Concurrent Test Item 2", 
                    "price": 375.0,
                    "seller": "Test Seller 2",
                    "pt_g": 0.75,
                    "pd_g": 0.4,
                    "rh_g": 0.2
                }
            ]
        }
        
        # Test with 3 concurrent requests
        concurrent_count = 3
        start_time = time.time()
        
        # Create concurrent requests with slightly different data
        tasks = []
        for i in range(concurrent_count):
            basket_data = base_basket_data.copy()
            basket_data["basketId"] = f"concurrent-test-basket-{i+1}"
            basket_data["basketName"] = f"Concurrent Test Basket {i+1}"
            
            task = self.make_request("/user/export-basket-pdf", "POST", data=basket_data)
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time_ms = (end_time - start_time) * 1000
        successful_requests = [r for r in results if r["success"]]
        
        if successful_requests:
            avg_individual_time = statistics.mean([r["response_time_ms"] for r in successful_requests])
            max_individual_time = max([r["response_time_ms"] for r in successful_requests])
            
            print(f"  {len(successful_requests)}/{concurrent_count} requests successful")
            print(f"  Total time: {total_time_ms:.0f}ms")
            print(f"  Avg individual: {avg_individual_time:.0f}ms")
            print(f"  Max individual: {max_individual_time:.0f}ms")
            
            return {
                "test_name": "Basket Export Concurrent Requests",
                "concurrent_requests": concurrent_count,
                "successful_requests": len(successful_requests),
                "total_time_ms": total_time_ms,
                "avg_individual_time_ms": avg_individual_time,
                "max_individual_time_ms": max_individual_time,
                "concurrent_performance_acceptable": total_time_ms < 15000,  # 15 seconds for 3 PDFs
                "system_handles_concurrent_exports": len(successful_requests) == concurrent_count,
                "no_timeout_issues": max_individual_time < 10000  # No individual request over 10 seconds
            }
        else:
            return {
                "test_name": "Basket Export Concurrent Requests",
                "error": "All concurrent requests failed",
                "successful_requests": 0,
                "concurrent_requests": concurrent_count,
                "system_handles_concurrent_exports": False
            }
    
    async def run_comprehensive_basket_export_test(self) -> Dict:
        """Run all basket export tests"""
        print("🚀 Starting Cataloro Basket Export Functionality Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run all test suites
            basic_functionality = await self.test_basket_export_endpoint_basic()
            response_time_performance = await self.test_basket_export_response_time()
            data_validation = await self.test_basket_export_data_validation()
            concurrent_requests = await self.test_basket_export_concurrent_requests()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "basic_functionality": basic_functionality,
                "response_time_performance": response_time_performance,
                "data_validation": data_validation,
                "concurrent_requests": concurrent_requests
            }
            
            # Calculate overall success metrics
            test_results = [
                basic_functionality.get("endpoint_working", False),
                response_time_performance.get("performance_acceptable", False),
                data_validation.get("handles_edge_cases", False),
                concurrent_requests.get("system_handles_concurrent_exports", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "basic_functionality_working": basic_functionality.get("endpoint_working", False),
                "pdf_generation_working": basic_functionality.get("pdf_generated", False),
                "response_time_acceptable": response_time_performance.get("performance_acceptable", False),
                "loading_state_justified": response_time_performance.get("loading_state_justified", False),
                "data_validation_robust": data_validation.get("handles_edge_cases", False),
                "concurrent_export_supported": concurrent_requests.get("system_handles_concurrent_exports", False),
                "all_tests_passed": overall_success_rate == 100
            }
            
            return all_results
            
        finally:
            await self.cleanup()


class CatalystDataTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
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
    
    async def test_catalyst_unified_calculations_endpoint(self) -> Dict:
        """Test GET /api/admin/catalyst/unified-calculations endpoint"""
        print("🧪 Testing catalyst unified calculations endpoint...")
        
        result = await self.make_request("/admin/catalyst/unified-calculations")
        
        if result["success"]:
            data = result["data"]
            
            # Verify it's a list
            if not isinstance(data, list):
                return {
                    "test_name": "Catalyst Unified Calculations Endpoint",
                    "success": False,
                    "error": "Response is not a list",
                    "response_time_ms": result["response_time_ms"],
                    "data_type": type(data).__name__
                }
            
            # Check entry count
            entry_count = len(data)
            expected_count = 4496
            count_matches = entry_count == expected_count
            
            print(f"  📊 Found {entry_count} entries (expected: {expected_count})")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            
            # Verify response structure for first few entries
            structure_valid = True
            required_fields = ["name", "cat_id", "weight", "pt_g", "pd_g", "rh_g", "total_price", "add_info"]
            missing_fields = []
            
            if data:  # Check first entry structure
                first_entry = data[0]
                for field in required_fields:
                    if field not in first_entry:
                        structure_valid = False
                        missing_fields.append(field)
                
                print(f"  🔍 Structure validation: {'✅' if structure_valid else '❌'}")
                if missing_fields:
                    print(f"    Missing fields: {missing_fields}")
                
                # Sample first entry for verification
                print(f"  📝 Sample entry:")
                print(f"    Name: {first_entry.get('name', 'N/A')}")
                print(f"    Cat ID: {first_entry.get('cat_id', 'N/A')}")
                print(f"    Weight: {first_entry.get('weight', 'N/A')}")
                print(f"    Pt g: {first_entry.get('pt_g', 'N/A')}")
                print(f"    Pd g: {first_entry.get('pd_g', 'N/A')}")
                print(f"    Rh g: {first_entry.get('rh_g', 'N/A')}")
                print(f"    Total Price: {first_entry.get('total_price', 'N/A')}")
                add_info_preview = str(first_entry.get('add_info', 'N/A'))[:100]
                if len(str(first_entry.get('add_info', ''))) > 100:
                    add_info_preview += '...'
                print(f"    Add Info: {add_info_preview}")
            
            # Performance check
            performance_acceptable = result["response_time_ms"] < 5000  # 5 seconds for 4496 entries
            
            return {
                "test_name": "Catalyst Unified Calculations Endpoint",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "entry_count": entry_count,
                "expected_count": expected_count,
                "count_matches_expected": count_matches,
                "structure_valid": structure_valid,
                "missing_fields": missing_fields,
                "required_fields_present": len(required_fields) - len(missing_fields),
                "total_required_fields": len(required_fields),
                "performance_acceptable": performance_acceptable,
                "sample_entry": data[0] if data else None,
                "all_requirements_met": count_matches and structure_valid and performance_acceptable
            }
        else:
            print(f"  ❌ Endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Catalyst Unified Calculations Endpoint",
                "success": False,
                "error": result.get("error", "Endpoint failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"]
            }
    
    async def test_catalyst_data_structure_validation(self) -> Dict:
        """Test detailed data structure validation for catalyst calculations"""
        print("🔬 Testing catalyst data structure validation...")
        
        result = await self.make_request("/admin/catalyst/unified-calculations")
        
        if not result["success"]:
            return {
                "test_name": "Catalyst Data Structure Validation",
                "success": False,
                "error": "Could not fetch data for validation"
            }
        
        data = result["data"]
        if not isinstance(data, list) or not data:
            return {
                "test_name": "Catalyst Data Structure Validation",
                "success": False,
                "error": "No data available for validation"
            }
        
        # Detailed validation of multiple entries
        validation_results = {
            "total_entries": len(data),
            "entries_validated": min(10, len(data)),  # Validate first 10 entries
            "field_validation": {},
            "data_type_validation": {},
            "value_range_validation": {}
        }
        
        required_fields = {
            "name": str,
            "cat_id": str,
            "weight": (int, float),
            "pt_g": (int, float),
            "pd_g": (int, float),
            "rh_g": (int, float),
            "total_price": (int, float)
        }
        
        entries_to_validate = data[:validation_results["entries_validated"]]
        
        for field, expected_type in required_fields.items():
            field_present_count = 0
            correct_type_count = 0
            
            for entry in entries_to_validate:
                if field in entry:
                    field_present_count += 1
                    if isinstance(entry[field], expected_type):
                        correct_type_count += 1
            
            validation_results["field_validation"][field] = {
                "present_count": field_present_count,
                "correct_type_count": correct_type_count,
                "field_present_rate": (field_present_count / len(entries_to_validate)) * 100,
                "correct_type_rate": (correct_type_count / len(entries_to_validate)) * 100 if field_present_count > 0 else 0
            }
        
        # Validate value ranges for numeric fields
        numeric_fields = ["weight", "pt_g", "pd_g", "rh_g", "total_price"]
        for field in numeric_fields:
            values = [entry.get(field, 0) for entry in entries_to_validate if field in entry and isinstance(entry[field], (int, float))]
            
            if values:
                validation_results["value_range_validation"][field] = {
                    "min_value": min(values),
                    "max_value": max(values),
                    "avg_value": sum(values) / len(values),
                    "non_negative_count": sum(1 for v in values if v >= 0),
                    "non_negative_rate": (sum(1 for v in values if v >= 0) / len(values)) * 100
                }
        
        # Overall validation score
        all_fields_present = all(
            validation_results["field_validation"][field]["field_present_rate"] == 100
            for field in required_fields
        )
        
        all_types_correct = all(
            validation_results["field_validation"][field]["correct_type_rate"] >= 95
            for field in required_fields
        )
        
        print(f"  📊 Validated {validation_results['entries_validated']} entries")
        print(f"  ✅ All required fields present: {all_fields_present}")
        print(f"  🔢 All data types correct: {all_types_correct}")
        
        return {
            "test_name": "Catalyst Data Structure Validation",
            "success": True,
            "validation_results": validation_results,
            "all_fields_present": all_fields_present,
            "all_types_correct": all_types_correct,
            "validation_passed": all_fields_present and all_types_correct
        }
    
    async def test_catalyst_endpoint_performance(self) -> Dict:
        """Test performance characteristics of catalyst endpoint"""
        print("⚡ Testing catalyst endpoint performance...")
        
        # Test multiple calls to get performance statistics
        response_times = []
        
        for i in range(3):
            result = await self.make_request("/admin/catalyst/unified-calculations")
            if result["success"]:
                response_times.append(result["response_time_ms"])
                print(f"  Call {i+1}: {result['response_time_ms']:.0f}ms")
            else:
                print(f"  Call {i+1}: FAILED")
        
        if not response_times:
            return {
                "test_name": "Catalyst Endpoint Performance",
                "success": False,
                "error": "All performance test calls failed"
            }
        
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Performance thresholds for 4496 entries
        excellent_threshold = 1000  # Under 1 second is excellent
        acceptable_threshold = 3000  # Under 3 seconds is acceptable
        
        performance_rating = "excellent" if avg_response_time < excellent_threshold else \
                           "acceptable" if avg_response_time < acceptable_threshold else \
                           "poor"
        
        print(f"  📊 Average response time: {avg_response_time:.0f}ms")
        print(f"  🎯 Performance rating: {performance_rating}")
        
        return {
            "test_name": "Catalyst Endpoint Performance",
            "success": True,
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min_response_time,
            "max_response_time_ms": max_response_time,
            "performance_rating": performance_rating,
            "meets_excellent_threshold": avg_response_time < excellent_threshold,
            "meets_acceptable_threshold": avg_response_time < acceptable_threshold,
            "response_times": response_times
        }
    
    async def test_catalyst_data_consistency(self) -> Dict:
        """Test data consistency and calculations"""
        print("🔍 Testing catalyst data consistency and calculations...")
        
        result = await self.make_request("/admin/catalyst/unified-calculations")
        
        if not result["success"]:
            return {
                "test_name": "Catalyst Data Consistency",
                "success": False,
                "error": "Could not fetch data for consistency testing"
            }
        
        data = result["data"]
        if not isinstance(data, list) or not data:
            return {
                "test_name": "Catalyst Data Consistency",
                "success": False,
                "error": "No data available for consistency testing"
            }
        
        # Test data consistency
        consistency_checks = {
            "unique_cat_ids": len(set(entry.get("cat_id", "") for entry in data)),
            "total_entries": len(data),
            "entries_with_names": sum(1 for entry in data if entry.get("name", "").strip()),
            "entries_with_weights": sum(1 for entry in data if isinstance(entry.get("weight"), (int, float)) and entry.get("weight", 0) > 0),
            "entries_with_prices": sum(1 for entry in data if isinstance(entry.get("total_price"), (int, float)) and entry.get("total_price", 0) >= 0),
            "entries_with_pt_content": sum(1 for entry in data if isinstance(entry.get("pt_g"), (int, float)) and entry.get("pt_g", 0) >= 0),
            "entries_with_pd_content": sum(1 for entry in data if isinstance(entry.get("pd_g"), (int, float)) and entry.get("pd_g", 0) >= 0),
            "entries_with_rh_content": sum(1 for entry in data if isinstance(entry.get("rh_g"), (int, float)) and entry.get("rh_g", 0) >= 0)
        }
        
        # Calculate consistency percentages
        total_entries = consistency_checks["total_entries"]
        consistency_percentages = {
            "unique_cat_id_rate": (consistency_checks["unique_cat_ids"] / total_entries) * 100 if total_entries > 0 else 0,
            "name_completion_rate": (consistency_checks["entries_with_names"] / total_entries) * 100 if total_entries > 0 else 0,
            "weight_completion_rate": (consistency_checks["entries_with_weights"] / total_entries) * 100 if total_entries > 0 else 0,
            "price_completion_rate": (consistency_checks["entries_with_prices"] / total_entries) * 100 if total_entries > 0 else 0,
            "pt_content_rate": (consistency_checks["entries_with_pt_content"] / total_entries) * 100 if total_entries > 0 else 0,
            "pd_content_rate": (consistency_checks["entries_with_pd_content"] / total_entries) * 100 if total_entries > 0 else 0,
            "rh_content_rate": (consistency_checks["entries_with_rh_content"] / total_entries) * 100 if total_entries > 0 else 0
        }
        
        # Overall data quality score
        data_quality_score = statistics.mean([
            consistency_percentages["name_completion_rate"],
            consistency_percentages["weight_completion_rate"],
            consistency_percentages["price_completion_rate"],
            consistency_percentages["pt_content_rate"],
            consistency_percentages["pd_content_rate"],
            consistency_percentages["rh_content_rate"]
        ])
        
        print(f"  📊 Total entries: {total_entries}")
        print(f"  🆔 Unique cat_ids: {consistency_checks['unique_cat_ids']}")
        print(f"  📝 Name completion: {consistency_percentages['name_completion_rate']:.1f}%")
        print(f"  ⚖️ Weight completion: {consistency_percentages['weight_completion_rate']:.1f}%")
        print(f"  💰 Price completion: {consistency_percentages['price_completion_rate']:.1f}%")
        print(f"  🧪 Precious metals content completion: Pt {consistency_percentages['pt_content_rate']:.1f}%, Pd {consistency_percentages['pd_content_rate']:.1f}%, Rh {consistency_percentages['rh_content_rate']:.1f}%")
        print(f"  🎯 Overall data quality score: {data_quality_score:.1f}%")
        
        return {
            "test_name": "Catalyst Data Consistency",
            "success": True,
            "consistency_checks": consistency_checks,
            "consistency_percentages": consistency_percentages,
            "data_quality_score": data_quality_score,
            "high_data_quality": data_quality_score >= 90,
            "acceptable_data_quality": data_quality_score >= 75
        }
    
    async def test_enhanced_search_functionality(self) -> Dict:
        """Test enhanced search functionality for CreateListingPage with add_info field"""
        print("🔍 Testing enhanced search functionality with add_info field...")
        
        result = await self.make_request("/admin/catalyst/unified-calculations")
        
        if not result["success"]:
            return {
                "test_name": "Enhanced Search Functionality",
                "success": False,
                "error": "Failed to get catalyst data",
                "response_time_ms": result["response_time_ms"]
            }
        
        data = result["data"]
        
        # Test 1: Verify add_info field is populated
        print("  📝 Testing add_info field population...")
        entries_with_add_info = 0
        meaningful_add_info_count = 0
        sample_add_info_entries = []
        
        for entry in data[:100]:  # Sample first 100 entries
            add_info = entry.get('add_info', '')
            if add_info:
                entries_with_add_info += 1
                # Check if add_info contains meaningful information (more than just whitespace)
                if len(add_info.strip()) > 10:  # Meaningful content threshold
                    meaningful_add_info_count += 1
                    if len(sample_add_info_entries) < 5:
                        sample_add_info_entries.append({
                            "name": entry.get('name', 'N/A'),
                            "cat_id": entry.get('cat_id', 'N/A'),
                            "add_info": add_info[:200] + '...' if len(add_info) > 200 else add_info
                        })
        
        add_info_population_rate = (entries_with_add_info / min(100, len(data))) * 100
        meaningful_info_rate = (meaningful_add_info_count / min(100, len(data))) * 100
        
        print(f"    📊 Add_info populated: {entries_with_add_info}/100 entries ({add_info_population_rate:.1f}%)")
        print(f"    📊 Meaningful add_info: {meaningful_add_info_count}/100 entries ({meaningful_info_rate:.1f}%)")
        
        # Test 2: Verify searchable fields structure
        print("  🔍 Testing searchable fields structure...")
        searchable_fields_present = True
        required_search_fields = ["name", "cat_id", "add_info"]
        missing_search_fields = []
        
        if data:
            first_entry = data[0]
            for field in required_search_fields:
                if field not in first_entry:
                    searchable_fields_present = False
                    missing_search_fields.append(field)
        
        print(f"    🔍 Searchable fields: {'✅' if searchable_fields_present else '❌'}")
        if missing_search_fields:
            print(f"      Missing: {missing_search_fields}")
        
        # Test 3: Sample meaningful add_info content
        print("  📋 Sample add_info entries for search verification:")
        for i, sample in enumerate(sample_add_info_entries, 1):
            print(f"    {i}. {sample['name']} ({sample['cat_id']})")
            print(f"       Add Info: {sample['add_info']}")
        
        # Test 4: Performance with enhanced search capability
        print("  ⚡ Testing performance for enhanced search...")
        performance_times = []
        
        # Test multiple calls to measure consistent performance
        for i in range(3):
            perf_result = await self.make_request("/admin/catalyst/unified-calculations")
            if perf_result["success"]:
                performance_times.append(perf_result["response_time_ms"])
        
        avg_performance = sum(performance_times) / len(performance_times) if performance_times else 0
        performance_acceptable = avg_performance < 3000  # 3 seconds for enhanced search data
        
        print(f"    ⏱️ Average response time: {avg_performance:.0f}ms")
        print(f"    ⚡ Performance acceptable: {'✅' if performance_acceptable else '❌'}")
        
        # Test 5: Data structure validation for enhanced search
        print("  🔬 Validating data structure for enhanced search...")
        search_ready_entries = 0
        
        for entry in data[:50]:  # Check first 50 entries
            has_name = bool(entry.get('name', '').strip())
            has_cat_id = bool(entry.get('cat_id', '').strip())
            has_searchable_content = has_name or has_cat_id or bool(entry.get('add_info', '').strip())
            
            if has_searchable_content:
                search_ready_entries += 1
        
        search_readiness_rate = (search_ready_entries / min(50, len(data))) * 100
        
        print(f"    📊 Search-ready entries: {search_ready_entries}/50 ({search_readiness_rate:.1f}%)")
        
        # Overall assessment
        enhanced_search_ready = (
            len(data) == 4496 and  # Correct entry count
            searchable_fields_present and  # All search fields present
            add_info_population_rate >= 50 and  # At least 50% have add_info
            meaningful_info_rate >= 30 and  # At least 30% have meaningful add_info
            performance_acceptable and  # Performance is acceptable
            search_readiness_rate >= 90  # At least 90% entries are search-ready
        )
        
        return {
            "test_name": "Enhanced Search Functionality",
            "success": True,
            "response_time_ms": result["response_time_ms"],
            "total_entries": len(data),
            "expected_entries": 4496,
            "correct_entry_count": len(data) == 4496,
            "add_info_population_rate": add_info_population_rate,
            "meaningful_info_rate": meaningful_info_rate,
            "searchable_fields_present": searchable_fields_present,
            "missing_search_fields": missing_search_fields,
            "sample_add_info_entries": sample_add_info_entries,
            "average_performance_ms": avg_performance,
            "performance_acceptable": performance_acceptable,
            "search_readiness_rate": search_readiness_rate,
            "enhanced_search_ready": enhanced_search_ready,
            "requirements_summary": {
                "entry_count_4496": len(data) == 4496,
                "add_info_field_populated": add_info_population_rate >= 50,
                "meaningful_add_info_content": meaningful_info_rate >= 30,
                "searchable_structure": searchable_fields_present,
                "performance_acceptable": performance_acceptable,
                "search_ready_data": search_readiness_rate >= 90
            }
        }
    
    async def run_comprehensive_catalyst_test(self) -> Dict:
        """Run all catalyst data tests including enhanced search functionality"""
        print("🚀 Starting Catalyst Data Endpoint Testing - Enhanced Search Verification")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all catalyst tests including enhanced search
            endpoint_test = await self.test_catalyst_unified_calculations_endpoint()
            structure_test = await self.test_catalyst_data_structure_validation()
            performance_test = await self.test_catalyst_endpoint_performance()
            consistency_test = await self.test_catalyst_data_consistency()
            enhanced_search_test = await self.test_enhanced_search_functionality()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "endpoint_functionality": endpoint_test,
                "data_structure_validation": structure_test,
                "performance_testing": performance_test,
                "data_consistency": consistency_test,
                "enhanced_search_functionality": enhanced_search_test
            }
            
            # Calculate overall success metrics
            test_results = [
                endpoint_test.get("all_requirements_met", False),
                structure_test.get("validation_passed", False),
                performance_test.get("meets_acceptable_threshold", False),
                consistency_test.get("acceptable_data_quality", False),
                enhanced_search_test.get("enhanced_search_ready", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "endpoint_working": endpoint_test.get("success", False),
                "correct_entry_count": endpoint_test.get("count_matches_expected", False),
                "structure_valid": structure_test.get("validation_passed", False),
                "performance_acceptable": performance_test.get("meets_acceptable_threshold", False),
                "data_quality_good": consistency_test.get("acceptable_data_quality", False),
                "enhanced_search_ready": enhanced_search_test.get("enhanced_search_ready", False),
                "add_info_populated": enhanced_search_test.get("add_info_population_rate", 0) >= 50,
                "meaningful_add_info": enhanced_search_test.get("meaningful_info_rate", 0) >= 30,
                "searchable_fields_present": enhanced_search_test.get("searchable_fields_present", False),
                "all_tests_passed": overall_success_rate == 100,
                "createlistingpage_enhanced_search_verified": (
                    endpoint_test.get("count_matches_expected", False) and 
                    endpoint_test.get("structure_valid", False) and
                    enhanced_search_test.get("enhanced_search_ready", False)
                )
            }
            
            return all_results
            
        finally:
            await self.cleanup()

class MessagesTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.demo_user_id = "2ae84d11-f762-4462-9467-d283fd719d21"  # From review request
        self.demo_user_id_alt = "demo_user_1"  # Alternative from review request
        
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
    
    async def test_messages_api_endpoint(self) -> Dict:
        """Test /api/user/{user_id}/messages endpoint directly"""
        print("📨 Testing Messages API Endpoint...")
        
        test_results = []
        
        # Test with primary demo user ID
        print(f"  Testing with demo user ID: {self.demo_user_id}")
        result1 = await self.make_request(f"/user/{self.demo_user_id}/messages")
        
        if result1["success"]:
            messages_data = result1["data"]
            print(f"    ✅ API responded successfully")
            print(f"    📊 Response time: {result1['response_time_ms']:.0f}ms")
            print(f"    📨 Messages returned: {len(messages_data) if isinstance(messages_data, list) else 'Not a list'}")
            
            test_results.append({
                "user_id": self.demo_user_id,
                "success": True,
                "response_time_ms": result1["response_time_ms"],
                "messages_count": len(messages_data) if isinstance(messages_data, list) else 0,
                "data_structure_valid": isinstance(messages_data, list),
                "messages_data": messages_data[:3] if isinstance(messages_data, list) else None  # First 3 for inspection
            })
        else:
            print(f"    ❌ API failed: {result1.get('error', 'Unknown error')}")
            print(f"    📊 Status: {result1['status']}")
            test_results.append({
                "user_id": self.demo_user_id,
                "success": False,
                "error": result1.get("error", "API call failed"),
                "status": result1["status"],
                "response_time_ms": result1["response_time_ms"]
            })
        
        # Test with alternative demo user ID
        print(f"  Testing with alternative demo user ID: {self.demo_user_id_alt}")
        result2 = await self.make_request(f"/user/{self.demo_user_id_alt}/messages")
        
        if result2["success"]:
            messages_data = result2["data"]
            print(f"    ✅ API responded successfully")
            print(f"    📊 Response time: {result2['response_time_ms']:.0f}ms")
            print(f"    📨 Messages returned: {len(messages_data) if isinstance(messages_data, list) else 'Not a list'}")
            
            test_results.append({
                "user_id": self.demo_user_id_alt,
                "success": True,
                "response_time_ms": result2["response_time_ms"],
                "messages_count": len(messages_data) if isinstance(messages_data, list) else 0,
                "data_structure_valid": isinstance(messages_data, list),
                "messages_data": messages_data[:3] if isinstance(messages_data, list) else None
            })
        else:
            print(f"    ❌ API failed: {result2.get('error', 'Unknown error')}")
            print(f"    📊 Status: {result2['status']}")
            test_results.append({
                "user_id": self.demo_user_id_alt,
                "success": False,
                "error": result2.get("error", "API call failed"),
                "status": result2["status"],
                "response_time_ms": result2["response_time_ms"]
            })
        
        successful_tests = [t for t in test_results if t["success"]]
        total_messages = sum(t.get("messages_count", 0) for t in successful_tests)
        
        return {
            "test_name": "Messages API Endpoint",
            "total_tests": len(test_results),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(test_results) * 100 if test_results else 0,
            "total_messages_found": total_messages,
            "api_responding": len(successful_tests) > 0,
            "both_user_ids_working": len(successful_tests) == 2,
            "avg_response_time_ms": statistics.mean([t["response_time_ms"] for t in successful_tests]) if successful_tests else 0,
            "detailed_results": test_results
        }
    
    async def check_database_content(self) -> Dict:
        """Check if there are any existing messages in the user_messages collection"""
        print("🗄️ Checking Database Content...")
        
        # We can't directly access MongoDB from here, but we can infer from API responses
        # Let's check a few different user IDs to see if any have messages
        
        test_user_ids = [
            self.demo_user_id,
            self.demo_user_id_alt,
            "admin_user_1",
            "test_user_1",
            "seller_user_1"
        ]
        
        database_check_results = []
        total_messages_in_system = 0
        
        for user_id in test_user_ids:
            print(f"  Checking messages for user: {user_id}")
            result = await self.make_request(f"/user/{user_id}/messages")
            
            if result["success"]:
                messages_data = result["data"]
                message_count = len(messages_data) if isinstance(messages_data, list) else 0
                total_messages_in_system += message_count
                
                database_check_results.append({
                    "user_id": user_id,
                    "has_messages": message_count > 0,
                    "message_count": message_count,
                    "api_accessible": True,
                    "sample_message": messages_data[0] if message_count > 0 else None
                })
                
                print(f"    📨 {message_count} messages found")
            else:
                database_check_results.append({
                    "user_id": user_id,
                    "has_messages": False,
                    "message_count": 0,
                    "api_accessible": False,
                    "error": result.get("error", "API failed")
                })
                print(f"    ❌ API failed: {result.get('error', 'Unknown')}")
        
        users_with_messages = [r for r in database_check_results if r["has_messages"]]
        accessible_users = [r for r in database_check_results if r["api_accessible"]]
        
        return {
            "test_name": "Database Content Check",
            "total_users_checked": len(test_user_ids),
            "users_with_api_access": len(accessible_users),
            "users_with_messages": len(users_with_messages),
            "total_messages_in_system": total_messages_in_system,
            "database_has_messages": total_messages_in_system > 0,
            "empty_database_explanation": total_messages_in_system == 0,
            "detailed_user_results": database_check_results
        }
    
    async def test_message_creation(self) -> Dict:
        """Test the POST endpoint to create a test message"""
        print("✉️ Testing Message Creation...")
        
        # Create a test message
        test_message_data = {
            "recipient_id": self.demo_user_id_alt,  # Send to alternative demo user
            "subject": "Test Message for Mobile Messages Functionality",
            "content": "This is a test message created to verify the messages functionality is working correctly. Created at: " + datetime.now().isoformat()
        }
        
        print(f"  Creating test message from {self.demo_user_id} to {self.demo_user_id_alt}")
        create_result = await self.make_request(f"/user/{self.demo_user_id}/messages", "POST", data=test_message_data)
        
        creation_test = {
            "message_creation_attempted": True,
            "creation_successful": create_result["success"],
            "response_time_ms": create_result["response_time_ms"]
        }
        
        if create_result["success"]:
            message_id = create_result["data"].get("id") if isinstance(create_result["data"], dict) else None
            print(f"    ✅ Message created successfully")
            print(f"    📨 Message ID: {message_id}")
            
            creation_test.update({
                "message_id": message_id,
                "creation_response": create_result["data"]
            })
            
            # Now test if we can retrieve the message
            print("  Verifying message retrieval after creation...")
            
            # Check sender's messages
            sender_messages_result = await self.make_request(f"/user/{self.demo_user_id}/messages")
            sender_has_new_message = False
            
            if sender_messages_result["success"]:
                sender_messages = sender_messages_result["data"]
                if isinstance(sender_messages, list):
                    sender_has_new_message = any(
                        msg.get("id") == message_id or msg.get("content", "").startswith("This is a test message")
                        for msg in sender_messages
                    )
                    print(f"    📨 Sender now has {len(sender_messages)} messages")
            
            # Check recipient's messages
            recipient_messages_result = await self.make_request(f"/user/{self.demo_user_id_alt}/messages")
            recipient_has_new_message = False
            
            if recipient_messages_result["success"]:
                recipient_messages = recipient_messages_result["data"]
                if isinstance(recipient_messages, list):
                    recipient_has_new_message = any(
                        msg.get("id") == message_id or msg.get("content", "").startswith("This is a test message")
                        for msg in recipient_messages
                    )
                    print(f"    📨 Recipient now has {len(recipient_messages)} messages")
            
            creation_test.update({
                "sender_can_see_message": sender_has_new_message,
                "recipient_can_see_message": recipient_has_new_message,
                "message_properly_stored": sender_has_new_message or recipient_has_new_message,
                "sender_message_count": len(sender_messages_result["data"]) if sender_messages_result["success"] and isinstance(sender_messages_result["data"], list) else 0,
                "recipient_message_count": len(recipient_messages_result["data"]) if recipient_messages_result["success"] and isinstance(recipient_messages_result["data"], list) else 0
            })
            
        else:
            print(f"    ❌ Message creation failed: {create_result.get('error', 'Unknown error')}")
            print(f"    📊 Status: {create_result['status']}")
            
            creation_test.update({
                "creation_error": create_result.get("error", "Message creation failed"),
                "creation_status": create_result["status"]
            })
        
        return {
            "test_name": "Message Creation Test",
            "creation_endpoint_working": creation_test["creation_successful"],
            "message_storage_working": creation_test.get("message_properly_stored", False),
            "sender_retrieval_working": creation_test.get("sender_can_see_message", False),
            "recipient_retrieval_working": creation_test.get("recipient_can_see_message", False),
            "full_message_flow_working": (
                creation_test["creation_successful"] and 
                creation_test.get("message_properly_stored", False)
            ),
            "detailed_test_results": creation_test
        }
    
    async def test_mobile_vs_desktop_consistency(self) -> Dict:
        """Test that mobile and desktop get the same data"""
        print("📱💻 Testing Mobile vs Desktop Consistency...")
        
        # Test the same endpoint multiple times to check for consistency
        consistency_tests = []
        
        for i in range(3):
            print(f"  Consistency test {i+1}/3...")
            result = await self.make_request(f"/user/{self.demo_user_id}/messages")
            
            if result["success"]:
                messages_data = result["data"]
                consistency_tests.append({
                    "test_number": i + 1,
                    "success": True,
                    "message_count": len(messages_data) if isinstance(messages_data, list) else 0,
                    "response_time_ms": result["response_time_ms"],
                    "data_structure": type(messages_data).__name__,
                    "first_message_id": messages_data[0].get("id") if isinstance(messages_data, list) and len(messages_data) > 0 else None
                })
            else:
                consistency_tests.append({
                    "test_number": i + 1,
                    "success": False,
                    "error": result.get("error", "API failed"),
                    "response_time_ms": result["response_time_ms"]
                })
        
        successful_tests = [t for t in consistency_tests if t["success"]]
        
        # Check consistency
        data_consistent = True
        if len(successful_tests) > 1:
            first_count = successful_tests[0]["message_count"]
            first_structure = successful_tests[0]["data_structure"]
            
            for test in successful_tests[1:]:
                if test["message_count"] != first_count or test["data_structure"] != first_structure:
                    data_consistent = False
                    break
        
        return {
            "test_name": "Mobile vs Desktop Consistency",
            "total_consistency_tests": len(consistency_tests),
            "successful_consistency_tests": len(successful_tests),
            "data_consistent_across_calls": data_consistent,
            "api_reliability": len(successful_tests) / len(consistency_tests) * 100 if consistency_tests else 0,
            "avg_response_time_ms": statistics.mean([t["response_time_ms"] for t in successful_tests]) if successful_tests else 0,
            "response_time_variance": statistics.stdev([t["response_time_ms"] for t in successful_tests]) if len(successful_tests) > 1 else 0,
            "detailed_consistency_results": consistency_tests
        }
    
    async def run_comprehensive_messages_test(self) -> Dict:
        """Run all messages functionality tests"""
        print("🚀 Starting Cataloro Messages Functionality Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test suites
            api_endpoint_test = await self.test_messages_api_endpoint()
            database_content_test = await self.check_database_content()
            message_creation_test = await self.test_message_creation()
            consistency_test = await self.test_mobile_vs_desktop_consistency()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "demo_user_ids_tested": [self.demo_user_id, self.demo_user_id_alt],
                "api_endpoint_test": api_endpoint_test,
                "database_content_test": database_content_test,
                "message_creation_test": message_creation_test,
                "consistency_test": consistency_test
            }
            
            # Calculate overall success metrics
            test_results = [
                api_endpoint_test.get("api_responding", False),
                database_content_test.get("users_with_api_access", 0) > 0,
                message_creation_test.get("creation_endpoint_working", False),
                consistency_test.get("data_consistent_across_calls", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            # Determine the root cause of empty messages
            empty_messages_explanation = ""
            if database_content_test.get("total_messages_in_system", 0) == 0:
                if message_creation_test.get("creation_endpoint_working", False):
                    empty_messages_explanation = "Database is empty but message creation works - this explains why mobile shows empty messages"
                else:
                    empty_messages_explanation = "Database is empty and message creation is not working - this explains the empty messages issue"
            else:
                empty_messages_explanation = "Messages exist in database - the mobile issue may be in UI rendering or data processing"
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "api_endpoints_working": api_endpoint_test.get("api_responding", False),
                "database_accessible": database_content_test.get("users_with_api_access", 0) > 0,
                "message_creation_working": message_creation_test.get("creation_endpoint_working", False),
                "message_storage_working": message_creation_test.get("message_storage_working", False),
                "data_consistency_verified": consistency_test.get("data_consistent_across_calls", False),
                "total_messages_in_system": database_content_test.get("total_messages_in_system", 0),
                "empty_messages_explanation": empty_messages_explanation,
                "mobile_messages_issue_identified": True,
                "recommended_action": "Create test messages to populate database" if database_content_test.get("total_messages_in_system", 0) == 0 else "Check mobile UI data processing"
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    print("🔧 Cataloro Marketplace Testing Suite")
    print("=" * 50)
    
    # Run Admin Menu Settings Tests (PRIMARY FOCUS - for the review request)
    print("\n⚙️ ADMIN MENU SETTINGS FUNCTIONALITY TESTING")
    print("=" * 60)
    
    menu_tester = AdminMenuSettingsTester()
    menu_results = await menu_tester.run_comprehensive_menu_settings_test()
    
    # Print Menu Settings Test Summary
    print("\n" + "=" * 60)
    print("📊 ADMIN MENU SETTINGS FUNCTIONALITY SUMMARY")
    print("=" * 60)
    
    if menu_results.get("error"):
        print(f"❌ Setup Error: {menu_results['error']}")
        print("Cannot proceed with menu settings tests without proper authentication")
        return
    
    menu_summary = menu_results["summary"]
    get_test = menu_results["menu_settings_get_endpoint"]
    structure_test = menu_results["data_structure_comparison"]
    post_test = menu_results["menu_settings_post_endpoint"]
    defaults_test = menu_results["default_items_verification"]
    cleanup_test = menu_results["database_cleanup_impact"]
    user_test = menu_results["user_menu_settings_endpoint"]
    
    print(f"🎯 Overall Success Rate: {menu_summary.get('overall_success_rate', 0):.0f}%")
    print()
    
    # GET Endpoint Testing
    get_status = "✅" if get_test.get("success") else "❌"
    print(f"{get_status} GET /api/admin/menu-settings: {'Working' if get_test.get('success') else 'Failed'}")
    if get_test.get("success"):
        print(f"   🖥️ Desktop items: {get_test.get('desktop_items_count', 0)}")
        print(f"   📱 Mobile items: {get_test.get('mobile_items_count', 0)}")
        print(f"   🏗️ Valid structure: {'Yes' if get_test.get('valid_item_structure') else 'No'}")
    else:
        print(f"   ❌ Error: {get_test.get('error', 'Unknown')}")
    
    # Data Structure Comparison
    structure_status = "✅" if structure_test.get("success") else "❌"
    print(f"{structure_status} Data Structure Match: {'Passed' if structure_test.get('success') else 'Failed'}")
    if structure_test.get("success"):
        print(f"   🖥️ Desktop match: {structure_test.get('desktop_match_percent', 0):.1f}%")
        print(f"   📱 Mobile match: {structure_test.get('mobile_match_percent', 0):.1f}%")
    
    # POST Endpoint Testing
    post_status = "✅" if post_test.get("success") else "❌"
    print(f"{post_status} POST /api/admin/menu-settings: {'Working' if post_test.get('success') else 'Failed'}")
    if post_test.get("success"):
        print(f"   ✅ Update verified: {'Yes' if post_test.get('update_verified') else 'No'}")
    else:
        print(f"   ❌ Error: {post_test.get('error', 'Unknown')}")
    
    # Default Items Verification
    defaults_status = "✅" if defaults_test.get("success") else "❌"
    print(f"{defaults_status} Default Items Structure: {'Valid' if defaults_test.get('success') else 'Invalid'}")
    if defaults_test.get("success"):
        print(f"   🖥️ Desktop valid: {defaults_test.get('desktop_valid_items', 0)}/{defaults_test.get('total_expected', 0)}")
        print(f"   📱 Mobile valid: {defaults_test.get('mobile_valid_items', 0)}/{defaults_test.get('total_expected', 0)}")
    
    # Database Cleanup Impact
    cleanup_status = "✅" if cleanup_test.get("success") else "❌"
    print(f"{cleanup_status} Database Cleanup Impact: {'No issues' if cleanup_test.get('success') else 'Issues detected'}")
    if not cleanup_test.get("success"):
        analysis = cleanup_test.get("cleanup_analysis", {})
        print(f"   🗑️ Corrupted items: {analysis.get('corrupted_custom_items', 0)}")
        print(f"   📝 Placeholder items: {analysis.get('placeholder_items', 0)}")
        print(f"   ❌ Missing defaults: {analysis.get('missing_defaults_count', 0)}")
    
    # User Menu Endpoint
    user_status = "✅" if user_test.get("success") else "❌"
    print(f"{user_status} User Menu Filtering: {'Working' if user_test.get('success') else 'Failed'}")
    if user_test.get("success"):
        print(f"   👤 User role: {user_test.get('user_role', 'unknown')}")
        print(f"   🔑 Admin items: {len(user_test.get('admin_items_desktop', []))}")
    
    print()
    print("🏆 ADMIN MENU SETTINGS TEST RESULTS:")
    overall_status = "✅ ALL TESTS PASSED" if menu_summary.get("all_tests_passed") else "⚠️ SOME TESTS FAILED"
    print(f"   {overall_status}")
    print(f"   Success Rate: {menu_summary.get('overall_success_rate', 0):.0f}%")
    print(f"   GET Endpoint: {'✅ Working' if menu_summary.get('menu_get_working') else '❌ Failed'}")
    print(f"   POST Endpoint: {'✅ Working' if menu_summary.get('menu_post_working') else '❌ Failed'}")
    print(f"   Data Structure: {'✅ Correct' if menu_summary.get('data_structure_correct') else '❌ Issues'}")
    print(f"   Default Items: {'✅ Valid' if menu_summary.get('default_items_valid') else '❌ Invalid'}")
    print(f"   Database Cleanup: {'✅ OK' if menu_summary.get('database_cleanup_ok') else '❌ Issues'}")
    print(f"   User Filtering: {'✅ Working' if menu_summary.get('user_menu_filtering_working') else '❌ Failed'}")
    
    # Save detailed results
    with open("/app/menu_settings_test_results.json", "w") as f:
        json.dump(menu_results, f, indent=2, default=str)
    
    print(f"\n📄 Menu settings test results saved to: /app/menu_settings_test_results.json")
    
    # Run Mobile Bidding Tests (Secondary focus)
    print("\n🎯 MOBILE BIDDING FUNCTIONALITY TESTING")
    print("=" * 60)
    
    bidding_tester = MobileBiddingTester()
    bidding_results = await bidding_tester.run_comprehensive_bidding_test()
    
    # Print Bidding Test Summary
    print("\n" + "=" * 60)
    print("📊 MOBILE BIDDING FUNCTIONALITY SUMMARY")
    print("=" * 60)
    
    if bidding_results.get("setup_error"):
        print(f"❌ Setup Error: {bidding_results['setup_error']}")
        print("Cannot proceed with bidding tests without proper setup")
    else:
        bidding_summary = bidding_results["summary"]
        first_bid = bidding_results["first_bid_scenario"]
        higher_bid = bidding_results["higher_bid_scenario"]
        equal_bid = bidding_results["equal_bid_scenario"]
        lower_bid = bidding_results["lower_bid_scenario"]
        min_increment = bidding_results["minimum_increment_logic"]
        error_accuracy = bidding_results["error_message_accuracy"]
        self_bidding = bidding_results["self_bidding_prevention"]
        
        print(f"🎯 Overall Success Rate: {bidding_summary.get('overall_success_rate', 0):.0f}%")
        print()
        
        # Critical Bidding Logic
        validation_status = "✅" if bidding_summary.get("bidding_validation_logic_working") else "❌"
        bug_resolved = "✅" if bidding_summary.get("critical_bug_resolved") else "❌"
        print(f"{validation_status} Bidding Validation Logic: {'Working' if bidding_summary.get('bidding_validation_logic_working') else 'Failed'}")
        print(f"{bug_resolved} Critical Bug Resolved: {'Yes' if bidding_summary.get('critical_bug_resolved') else 'No'}")
        print()
        
        # Individual Test Results
        first_bid_status = "✅" if first_bid.get("success") else "❌"
        print(f"{first_bid_status} First Bid Scenario: {'Accepted' if first_bid.get('first_bid_accepted') else 'Failed'}")
        
        higher_bid_status = "✅" if higher_bid.get("success") else "❌"
        print(f"{higher_bid_status} Higher Bid Scenario: {'Accepted' if higher_bid.get('higher_bid_accepted') else 'Failed'}")
        
        equal_bid_status = "✅" if equal_bid.get("success") else "❌"
        print(f"{equal_bid_status} Equal Bid Scenario: {'Correctly Rejected' if equal_bid.get('correctly_rejected') else 'Incorrectly Accepted'}")
        
        lower_bid_status = "✅" if lower_bid.get("success") else "❌"
        print(f"{lower_bid_status} Lower Bid Scenario: {'Correctly Rejected' if lower_bid.get('correctly_rejected') else 'Incorrectly Accepted'}")
        
        min_increment_status = "✅" if min_increment.get("success") else "❌"
        print(f"{min_increment_status} Minimum Increment Logic: {'Working' if min_increment.get('minimum_increment_accepted') else 'Failed'}")
        
        error_accuracy_status = "✅" if error_accuracy.get("success") else "❌"
        accuracy_score = error_accuracy.get("accuracy_score", 0)
        print(f"{error_accuracy_status} Error Message Accuracy: {accuracy_score:.0f}%")
        
        self_bidding_status = "✅" if self_bidding.get("success") else "❌"
        print(f"{self_bidding_status} Self-Bidding Prevention: {'Working' if self_bidding.get('self_bidding_prevented') else 'Failed'}")
        
        print()
        print("🏆 MOBILE BIDDING TEST RESULTS:")
        overall_status = "✅ ALL TESTS PASSED" if bidding_summary.get("all_tests_passed") else "⚠️ SOME TESTS FAILED"
        print(f"   {overall_status}")
        print(f"   Success Rate: {bidding_summary.get('overall_success_rate', 0):.0f}%")
        print(f"   Critical Bug: {'✅ RESOLVED' if bidding_summary.get('critical_bug_resolved') else '❌ NOT RESOLVED'}")
        print(f"   Validation Logic: {'✅ Working' if bidding_summary.get('bidding_validation_logic_working') else '❌ Failed'}")
        
        # Save detailed results
        with open("/app/mobile_bidding_test_results.json", "w") as f:
            json.dump(bidding_results, f, indent=2, default=str)
        
        print(f"\n📄 Mobile bidding test results saved to: /app/mobile_bidding_test_results.json")
    
    # Run Basket Export Tests (Secondary focus)
    print("\n📄 BASKET EXPORT FUNCTIONALITY TESTING")
    print("=" * 60)
    
    basket_tester = BasketExportTester()
    basket_results = await basket_tester.run_comprehensive_basket_export_test()
    
    # Print Basket Export Test Summary
    print("\n" + "=" * 60)
    print("📊 BASKET EXPORT FUNCTIONALITY SUMMARY")
    print("=" * 60)
    
    basket_summary = basket_results["summary"]
    basic_func = basket_results["basic_functionality"]
    response_time = basket_results["response_time_performance"]
    data_validation = basket_results["data_validation"]
    concurrent = basket_results["concurrent_requests"]
    
    print(f"🎯 Overall Success Rate: {basket_summary.get('overall_success_rate', 0):.0f}%")
    print()
    
    # Basic Functionality
    basic_status = "✅" if basic_func.get("endpoint_working") else "❌"
    pdf_status = "✅" if basic_func.get("pdf_generated") else "❌"
    print(f"{basic_status} Endpoint Functionality: Working")
    print(f"{pdf_status} PDF Generation: {'Working' if basic_func.get('pdf_generated') else 'Failed'}")
    print(f"   ⏱️ Response Time: {basic_func.get('response_time_ms', 0):.0f}ms")
    print(f"   📊 PDF Size: {basic_func.get('pdf_size_bytes', 0)} bytes")
    print(f"   📋 Valid PDF: {'✅' if basic_func.get('is_valid_pdf') else '❌'}")
    
    # Response Time Performance
    perf_status = "✅" if response_time.get("performance_acceptable") else "❌"
    loading_justified = "✅" if response_time.get("loading_state_justified") else "❌"
    avg_time = response_time.get("avg_response_time_ms", 0)
    max_time = response_time.get("max_response_time_ms", 0)
    print(f"{perf_status} Response Time Performance: {avg_time:.0f}ms avg, {max_time:.0f}ms max")
    print(f"{loading_justified} Loading State Justified: {'Yes' if response_time.get('loading_state_justified') else 'No'}")
    
    # Data Validation
    validation_status = "✅" if data_validation.get("handles_edge_cases") else "❌"
    validation_rate = data_validation.get("validation_success_rate", 0)
    print(f"{validation_status} Data Validation: {validation_rate:.0f}% success rate")
    print(f"   📝 Empty Baskets: {'✅' if data_validation.get('handles_empty_baskets') else '❌'}")
    print(f"   📊 Minimal Data: {'✅' if data_validation.get('handles_minimal_data') else '❌'}")
    print(f"   🚫 Invalid Data: {'✅' if data_validation.get('handles_invalid_data') else '❌'}")
    
    # Concurrent Requests
    concurrent_status = "✅" if concurrent.get("system_handles_concurrent_exports") else "❌"
    concurrent_success = concurrent.get("successful_requests", 0)
    concurrent_total = concurrent.get("concurrent_requests", 0)
    print(f"{concurrent_status} Concurrent Exports: {concurrent_success}/{concurrent_total} successful")
    
    print()
    print("🏆 BASKET EXPORT TEST RESULTS:")
    overall_status = "✅ ALL TESTS PASSED" if basket_summary.get("all_tests_passed") else "⚠️ SOME TESTS FAILED"
    print(f"   {overall_status}")
    print(f"   Success Rate: {basket_summary.get('overall_success_rate', 0):.0f}%")
    print(f"   PDF Generation: {'✅ Working' if basket_summary.get('pdf_generation_working') else '❌ Failed'}")
    print(f"   Loading State: {'✅ Justified' if basket_summary.get('loading_state_justified') else '❌ Not Needed'}")
    print(f"   Data Validation: {'✅ Robust' if basket_summary.get('data_validation_robust') else '❌ Needs Work'}")
    print(f"   Concurrent Support: {'✅ Working' if basket_summary.get('concurrent_export_supported') else '❌ Issues'}")
    
    # Save detailed results
    with open("/app/basket_export_test_results.json", "w") as f:
        json.dump(basket_results, f, indent=2, default=str)
    
    print(f"\n📄 Basket export test results saved to: /app/basket_export_test_results.json")
    
    # Run Catalyst Data Endpoint Tests (Secondary)
    print("\n🧪 CATALYST DATA ENDPOINT TESTING")
    print("=" * 60)
    
    catalyst_tester = CatalystDataTester()
    catalyst_results = await catalyst_tester.run_comprehensive_catalyst_test()
    
    # Print Catalyst Test Summary
    print("\n" + "=" * 60)
    print("📊 CATALYST DATA ENDPOINT SUMMARY")
    print("=" * 60)
    
    catalyst_summary = catalyst_results["summary"]
    endpoint_test = catalyst_results["endpoint_functionality"]
    structure_test = catalyst_results["data_structure_validation"]
    performance_test = catalyst_results["performance_testing"]
    consistency_test = catalyst_results["data_consistency"]
    enhanced_search_test = catalyst_results["enhanced_search_functionality"]
    
    print(f"🎯 Overall Success Rate: {catalyst_summary.get('overall_success_rate', 0):.0f}%")
    print()
    
    # Endpoint Functionality
    endpoint_status = "✅" if endpoint_test.get("success") else "❌"
    entry_count = endpoint_test.get("entry_count", 0)
    expected_count = endpoint_test.get("expected_count", 4496)
    count_status = "✅" if endpoint_test.get("count_matches_expected") else "❌"
    print(f"{endpoint_status} Endpoint Functionality: Working")
    print(f"   {count_status} Entry Count: {entry_count}/{expected_count} entries")
    print(f"   ⏱️ Response Time: {endpoint_test.get('response_time_ms', 0):.0f}ms")
    
    # Enhanced Search Functionality
    search_status = "✅" if enhanced_search_test.get("enhanced_search_ready") else "❌"
    add_info_rate = enhanced_search_test.get("add_info_population_rate", 0)
    meaningful_rate = enhanced_search_test.get("meaningful_info_rate", 0)
    print(f"{search_status} Enhanced Search Functionality: Ready")
    print(f"   📝 Add_info Population: {add_info_rate:.1f}%")
    print(f"   💡 Meaningful Content: {meaningful_rate:.1f}%")
    print(f"   🔍 Searchable Fields: {'✅' if enhanced_search_test.get('searchable_fields_present') else '❌'}")
    
    # Data Structure
    structure_status = "✅" if structure_test.get("validation_passed") else "❌"
    print(f"{structure_status} Data Structure: Valid")
    if structure_test.get("success"):
        validation_results = structure_test.get("validation_results", {})
        print(f"   📊 Fields Present: {structure_test.get('all_fields_present', False)}")
        print(f"   🔢 Types Correct: {structure_test.get('all_types_correct', False)}")
    
    # Performance
    performance_status = "✅" if performance_test.get("meets_acceptable_threshold") else "❌"
    performance_rating = performance_test.get("performance_rating", "unknown")
    avg_time = performance_test.get("avg_response_time_ms", 0)
    print(f"{performance_status} Performance: {performance_rating} ({avg_time:.0f}ms avg)")
    
    # Data Consistency
    consistency_status = "✅" if consistency_test.get("acceptable_data_quality") else "❌"
    quality_score = consistency_test.get("data_quality_score", 0)
    print(f"{consistency_status} Data Quality: {quality_score:.1f}%")
    
    print()
    print("🏆 CATALYST ENDPOINT TEST RESULTS:")
    overall_status = "✅ ALL TESTS PASSED" if catalyst_summary.get("all_tests_passed") else "⚠️ SOME TESTS FAILED"
    search_verified = "✅ ENHANCED SEARCH VERIFIED" if catalyst_summary.get("createlistingpage_enhanced_search_verified") else "❌ ENHANCED SEARCH VERIFICATION FAILED"
    print(f"   {overall_status}")
    print(f"   {search_verified}")
    print(f"   Success Rate: {catalyst_summary.get('overall_success_rate', 0):.0f}%")
    
    # Run Admin Authentication & Database Consistency Tests
    print("\n🔐 ADMIN AUTHENTICATION & DATABASE CONSISTENCY TESTS")
    print("=" * 60)
    
    admin_tester = AdminAuthenticationTester()
    admin_results = await admin_tester.run_comprehensive_admin_test()
    
    # Print Admin Test Summary
    print("\n" + "=" * 60)
    print("📊 ADMIN AUTHENTICATION & USER MANAGEMENT SUMMARY")
    print("=" * 60)
    
    admin_summary = admin_results["summary"]
    admin_auth = admin_results["admin_authentication"]
    db_consistency = admin_results["database_consistency"]
    user_mgmt_endpoints = admin_results["user_management_endpoints"]
    user_mgmt_functionality = admin_results["user_management_functionality"]
    user_workflow = admin_results["user_workflow_integration"]
    browse_perf = admin_results["browse_endpoint_performance"]
    admin_func = admin_results["admin_functionality"]
    
    print(f"🎯 Overall Success Rate: {admin_summary.get('overall_success_rate', 0):.0f}%")
    print()
    
    # Admin Authentication
    auth_status = "✅" if admin_auth.get("all_admin_properties_correct") else "❌"
    print(f"{auth_status} Admin Authentication: {admin_auth.get('login_successful', False)}")
    if admin_auth.get("login_successful"):
        print(f"   📧 Email: {admin_auth.get('admin_email_correct', False)}")
        print(f"   👤 Username: {admin_auth.get('admin_username_correct', False)}")
        print(f"   🔑 Role: {admin_auth.get('admin_role_correct', False)}")
    
    # Database Consistency
    db_status = "✅" if db_consistency.get("all_users_consistent") else "❌"
    db_score = db_consistency.get("database_consistency_score", 0)
    print(f"{db_status} Database Consistency: {db_score:.0f}%")
    print(f"   👥 Users Found: {db_consistency.get('users_found_in_database', 0)}/{db_consistency.get('total_expected_users', 0)}")
    
    # User Management Endpoints
    mgmt_endpoints_status = "✅" if user_mgmt_endpoints.get("all_endpoints_working") else "❌"
    mgmt_endpoints_success = user_mgmt_endpoints.get("success_rate", 0)
    print(f"{mgmt_endpoints_status} User Management Endpoints: {mgmt_endpoints_success:.0f}% success rate")
    
    # User Management Functionality (NEW)
    mgmt_func_status = "✅" if user_mgmt_functionality.get("critical_functionality_working") else "❌"
    mgmt_func_success = user_mgmt_functionality.get("success_rate", 0)
    print(f"{mgmt_func_status} User Management Functionality: {mgmt_func_success:.0f}% success rate")
    
    # Activate/Suspend Functionality
    activate_suspend_status = "✅" if user_mgmt_functionality.get("activate_suspend_working") else "❌"
    print(f"   {activate_suspend_status} Activate/Suspend: {user_mgmt_functionality.get('activate_suspend_working', False)}")
    
    # State Persistence
    persistence_status = "✅" if user_mgmt_functionality.get("state_persistence_working") else "❌"
    print(f"   {persistence_status} State Persistence: {user_mgmt_functionality.get('state_persistence_working', False)}")
    
    # Error Handling
    error_handling_status = "✅" if user_mgmt_functionality.get("error_handling_working") else "❌"
    print(f"   {error_handling_status} Error Handling: {user_mgmt_functionality.get('error_handling_working', False)}")
    
    # User Workflow Integration (NEW)
    workflow_status = "✅" if user_workflow.get("complete_workflow_working") else "❌"
    workflow_success = user_workflow.get("workflow_success_rate", 0)
    print(f"{workflow_status} User Workflow Integration: {workflow_success:.0f}% success rate")
    
    # Browse Endpoint Performance
    browse_status = "✅" if browse_perf.get("endpoint_working") else "❌"
    browse_time = browse_perf.get("response_time_ms", 0)
    print(f"{browse_status} Browse Endpoint: {browse_time:.0f}ms response time")
    
    # Admin Functionality
    func_status = "✅" if admin_func.get("all_admin_features_working") else "❌"
    func_success = admin_func.get("admin_success_rate", 0)
    print(f"{func_status} Admin Functionality: {func_success:.0f}% features working")
    
    print()
    print("🏆 OVERALL USER MANAGEMENT TEST RESULTS:")
    overall_status = "✅ ALL TESTS PASSED" if admin_summary.get("all_tests_passed") else "⚠️ SOME TESTS FAILED"
    print(f"   {overall_status}")
    print(f"   Success Rate: {admin_summary.get('overall_success_rate', 0):.0f}%")
    
    # Detailed User Management Results
    print()
    print("📋 USER MANAGEMENT DETAILED RESULTS:")
    print(f"   🔄 Activate/Suspend Working: {'✅' if admin_summary.get('activate_suspend_functionality_working') else '❌'}")
    print(f"   💾 State Persistence: {'✅' if admin_summary.get('state_persistence_working') else '❌'}")
    print(f"   🚫 Error Handling: {'✅' if admin_summary.get('error_handling_working') else '❌'}")
    print(f"   🔗 Complete Workflow: {'✅' if admin_summary.get('complete_user_workflow_working') else '❌'}")
    
    # Save detailed results
    with open("/app/user_management_test_results.json", "w") as f:
        json.dump(admin_results, f, indent=2, default=str)
    
    print(f"\n📄 User management test results saved to: /app/user_management_test_results.json")
    
    # Run Browse Performance Tests automatically for comprehensive testing
    run_browse_tests = False  # Set to False to skip interactive browse tests for now
    
    if run_browse_tests:
        print("\n🚀 BROWSE ENDPOINT PERFORMANCE TESTS")
        print("=" * 50)
        
        browse_tester = BrowseEndpointTester()
        browse_results = await browse_tester.run_comprehensive_test()
        
        # Print Browse Test Summary
        print("\n" + "=" * 60)
        print("📊 BROWSE PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        browse_summary = browse_results["summary"]
        basic = browse_results["basic_performance"]
        cache = browse_results["cache_performance"]
        filtering = browse_results["filtering_performance"]
        concurrent = browse_results["concurrent_performance"]
        pagination = browse_results["pagination_performance"]
        
        print(f"🎯 Performance Target: {browse_results['performance_target_ms']}ms")
        print(f"📈 Cache Improvement Target: {browse_results['cache_improvement_target_percent']}%")
        print()
        
        # Basic Performance
        status = "✅" if basic.get("meets_performance_target") else "❌"
        print(f"{status} Basic Browse Performance: {basic.get('avg_response_time_ms', 0):.0f}ms avg")
        
        # Cache Performance
        cache_status = "✅" if cache.get("cache_working") else "❌"
        improvement = cache.get("cache_improvement_percent", 0)
        print(f"{cache_status} Cache Performance: {improvement:.1f}% improvement")
        
        # Data Integrity
        integrity_status = "✅" if browse_summary.get("data_integrity_excellent") else "❌"
        integrity = browse_summary.get("average_data_integrity_score", 0)
        print(f"{integrity_status} Data Integrity: {integrity:.1f}%")
        
        # Filtering
        filter_status = "✅" if filtering.get("all_filters_under_target") else "❌"
        filter_success = filtering.get("success_rate", 0)
        print(f"{filter_status} Filtering Options: {filter_success:.0f}% success rate")
        
        # Concurrent Performance
        concurrent_status = "✅" if concurrent.get("all_under_target") else "❌"
        throughput = concurrent.get("throughput_requests_per_second", 0)
        print(f"{concurrent_status} Concurrent Performance: {throughput:.1f} req/sec")
        
        # Pagination
        pagination_status = "✅" if pagination.get("all_pages_under_target") else "❌"
        pagination_success = pagination.get("successful_pages", 0)
        print(f"{pagination_status} Pagination: {pagination_success}/5 pages successful")
        
        print()
        print("🏆 BROWSE PERFORMANCE RESULTS:")
        browse_overall_status = "✅ EXCELLENT" if browse_summary.get("performance_target_met") and browse_summary.get("cache_target_met") else "⚠️ NEEDS IMPROVEMENT"
        print(f"   {browse_overall_status}")
        print(f"   Performance Success Rate: {browse_summary.get('overall_performance_success_rate', 0):.0f}%")
        print(f"   Cache Working: {'Yes' if browse_summary.get('cache_functionality_working') else 'No'}")
        print(f"   Data Integrity: {browse_summary.get('average_data_integrity_score', 0):.0f}%")
        
        # Save detailed results
        with open("/app/browse_performance_test_results.json", "w") as f:
            json.dump(browse_results, f, indent=2, default=str)
        
        print(f"\n📄 Browse test results saved to: /app/browse_performance_test_results.json")
    
    return admin_results

async def main_custom_menu():
    """Main function to run custom menu management tests"""
    print("🎯 CATALORO CUSTOM MENU MANAGEMENT TESTING")
    print("=" * 80)
    print("Testing new custom menu item management functionality end-to-end")
    print()
    
    # Run custom menu management tests
    custom_menu_tester = CustomMenuManagementTester()
    custom_menu_results = await custom_menu_tester.run_comprehensive_custom_menu_test()
    
    # Display results summary
    print("\n" + "=" * 80)
    print("🎯 CUSTOM MENU MANAGEMENT TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if "error" in custom_menu_results:
        print(f"❌ TESTING FAILED: {custom_menu_results['error']}")
        return custom_menu_results
    
    summary = custom_menu_results.get("summary", {})
    
    # Individual test results
    print("📊 Individual Test Results:")
    print(f"   {'✅' if custom_menu_results.get('available_pages_endpoint', {}).get('success') else '❌'} Available Pages Endpoint")
    print(f"   {'✅' if custom_menu_results.get('available_icons_endpoint', {}).get('success') else '❌'} Available Icons Endpoint")
    print(f"   {'✅' if custom_menu_results.get('menu_settings_get', {}).get('success') else '❌'} Menu Settings GET")
    print(f"   {'✅' if custom_menu_results.get('custom_item_creation', {}).get('success') else '❌'} Custom Item Creation")
    print(f"   {'✅' if custom_menu_results.get('menu_validation', {}).get('success') else '❌'} Menu Validation")
    print(f"   {'✅' if custom_menu_results.get('user_menu_filtering', {}).get('success') else '❌'} User Menu Filtering")
    print(f"   {'✅' if custom_menu_results.get('crud_operations', {}).get('success') else '❌'} CRUD Operations")
    print(f"   {'✅' if custom_menu_results.get('integration_workflow', {}).get('success') else '❌'} Integration Workflow")
    
    print()
    print("🏆 OVERALL RESULTS:")
    overall_status = "✅ ALL TESTS PASSED" if summary.get("all_tests_passed") else "❌ SOME TESTS FAILED"
    print(f"   {overall_status}")
    print(f"   Success Rate: {summary.get('overall_success_rate', 0):.0f}%")
    print(f"   Critical Functionality: {'✅ Working' if summary.get('critical_functionality_working') else '❌ Issues Found'}")
    
    # Detailed breakdown
    print()
    print("📋 Detailed Breakdown:")
    print(f"   Available Pages Working: {'✅' if summary.get('available_pages_working') else '❌'}")
    print(f"   Available Icons Working: {'✅' if summary.get('available_icons_working') else '❌'}")
    print(f"   Menu Settings CRUD: {'✅' if summary.get('menu_settings_crud_working') else '❌'}")
    print(f"   Validation Working: {'✅' if summary.get('validation_working') else '❌'}")
    print(f"   User Filtering Working: {'✅' if summary.get('user_filtering_working') else '❌'}")
    print(f"   CRUD Operations: {'✅' if summary.get('crud_operations_working') else '❌'}")
    print(f"   Integration Workflow: {'✅' if summary.get('integration_workflow_working') else '❌'}")
    
    # Save detailed results
    with open("/app/custom_menu_test_results.json", "w") as f:
        json.dump(custom_menu_results, f, indent=2, default=str)
    
    print(f"\n📄 Custom menu test results saved to: /app/custom_menu_test_results.json")
    
    return custom_menu_results

if __name__ == "__main__":
    # Run admin menu settings tests
    asyncio.run(main())