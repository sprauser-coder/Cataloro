#!/usr/bin/env python3
"""
Mobile Interface Backend API Testing
Testing backend APIs that are used by mobile interface components
Focus: Browse/Marketplace, Authentication, Admin, User Management, Mobile Performance
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://market-refactor-1.preview.emergentagent.com/api"
MOBILE_PERFORMANCE_TARGET_MS = 800  # Mobile should be faster than desktop
MOBILE_TIMEOUT_MS = 5000  # Mobile timeout threshold

# Test User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "demo@cataloro.com"
TEST_USER_ID = "test-mobile-user-123"

class MobileBackendTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.test_results = []
        
    async def setup(self):
        """Initialize HTTP session with mobile-appropriate timeout"""
        timeout = aiohttp.ClientTimeout(total=MOBILE_TIMEOUT_MS/1000)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
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
                    "status": response.status,
                    "mobile_performance_ok": response_time_ms < MOBILE_PERFORMANCE_TARGET_MS
                }
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time_ms,
                "error": str(e),
                "status": 0,
                "mobile_performance_ok": False
            }
    
    async def test_mobile_authentication_apis(self) -> Dict:
        """Test authentication APIs used by mobile interface"""
        print("📱 Testing Mobile Authentication APIs...")
        
        auth_tests = []
        
        # Test 1: Admin Login for Mobile Admin Drawer
        print("  Testing admin login for mobile admin drawer...")
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            user_data = admin_result["data"].get("user", {})
            
            auth_tests.append({
                "test": "Admin Login",
                "success": True,
                "response_time_ms": admin_result["response_time_ms"],
                "mobile_performance_ok": admin_result["mobile_performance_ok"],
                "has_admin_role": user_data.get("role") == "admin" or user_data.get("user_role") == "Admin",
                "token_received": bool(self.admin_token)
            })
            print(f"    ✅ Admin login successful ({admin_result['response_time_ms']:.0f}ms)")
        else:
            auth_tests.append({
                "test": "Admin Login",
                "success": False,
                "response_time_ms": admin_result["response_time_ms"],
                "error": admin_result.get("error", "Login failed")
            })
            print(f"    ❌ Admin login failed: {admin_result.get('error')}")
        
        # Test 2: Demo User Login for Mobile Interface
        print("  Testing demo user login for mobile interface...")
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": "demo_password"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            user_data = demo_result["data"].get("user", {})
            
            auth_tests.append({
                "test": "Demo User Login",
                "success": True,
                "response_time_ms": demo_result["response_time_ms"],
                "mobile_performance_ok": demo_result["mobile_performance_ok"],
                "user_id": user_data.get("id"),
                "token_received": bool(self.demo_token)
            })
            print(f"    ✅ Demo user login successful ({demo_result['response_time_ms']:.0f}ms)")
        else:
            auth_tests.append({
                "test": "Demo User Login",
                "success": False,
                "response_time_ms": demo_result["response_time_ms"],
                "error": demo_result.get("error", "Login failed")
            })
            print(f"    ❌ Demo user login failed: {demo_result.get('error')}")
        
        # Test 3: Profile API for Mobile Bottom Nav
        if self.demo_token:
            demo_user_id = demo_result["data"].get("user", {}).get("id")
            if demo_user_id:
                print("  Testing profile API for mobile bottom nav...")
                profile_result = await self.make_request(f"/auth/profile/{demo_user_id}")
                
                if profile_result["success"]:
                    profile_data = profile_result["data"]
                    auth_tests.append({
                        "test": "Profile API",
                        "success": True,
                        "response_time_ms": profile_result["response_time_ms"],
                        "mobile_performance_ok": profile_result["mobile_performance_ok"],
                        "has_user_data": bool(profile_data.get("id")),
                        "has_email": bool(profile_data.get("email"))
                    })
                    print(f"    ✅ Profile API working ({profile_result['response_time_ms']:.0f}ms)")
                else:
                    auth_tests.append({
                        "test": "Profile API",
                        "success": False,
                        "response_time_ms": profile_result["response_time_ms"],
                        "error": profile_result.get("error", "Profile fetch failed")
                    })
                    print(f"    ❌ Profile API failed: {profile_result.get('error')}")
        
        # Calculate success metrics
        successful_tests = [t for t in auth_tests if t["success"]]
        mobile_performance_ok = [t for t in successful_tests if t.get("mobile_performance_ok", False)]
        
        return {
            "test_name": "Mobile Authentication APIs",
            "total_tests": len(auth_tests),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(auth_tests) * 100 if auth_tests else 0,
            "mobile_performance_tests": len(mobile_performance_ok),
            "mobile_performance_rate": len(mobile_performance_ok) / len(successful_tests) * 100 if successful_tests else 0,
            "admin_login_working": any(t.get("test") == "Admin Login" and t.get("success") for t in auth_tests),
            "demo_login_working": any(t.get("test") == "Demo User Login" and t.get("success") for t in auth_tests),
            "profile_api_working": any(t.get("test") == "Profile API" and t.get("success") for t in auth_tests),
            "detailed_results": auth_tests
        }
    
    async def test_mobile_browse_marketplace_apis(self) -> Dict:
        """Test browse/marketplace APIs for mobile listing cards"""
        print("🛒 Testing Mobile Browse/Marketplace APIs...")
        
        browse_tests = []
        
        # Test 1: Basic Browse API for Mobile Listing Cards
        print("  Testing basic browse API for mobile listing cards...")
        browse_result = await self.make_request("/marketplace/browse")
        
        if browse_result["success"]:
            listings = browse_result["data"]
            
            # Check mobile-specific data structure
            mobile_data_complete = self.check_mobile_listing_data(listings)
            
            browse_tests.append({
                "test": "Basic Browse API",
                "success": True,
                "response_time_ms": browse_result["response_time_ms"],
                "mobile_performance_ok": browse_result["mobile_performance_ok"],
                "listings_count": len(listings),
                "mobile_data_complete": mobile_data_complete,
                "has_seller_info": any("seller" in listing for listing in listings),
                "has_bid_info": any("bid_info" in listing for listing in listings)
            })
            print(f"    ✅ Browse API working ({browse_result['response_time_ms']:.0f}ms, {len(listings)} listings)")
        else:
            browse_tests.append({
                "test": "Basic Browse API",
                "success": False,
                "response_time_ms": browse_result["response_time_ms"],
                "error": browse_result.get("error", "Browse API failed")
            })
            print(f"    ❌ Browse API failed: {browse_result.get('error')}")
        
        # Test 2: Mobile-Optimized Browse with Filters
        print("  Testing mobile-optimized browse with filters...")
        mobile_params = {
            "limit": 10,  # Mobile-appropriate page size
            "type": "all",
            "page": 1
        }
        
        filtered_result = await self.make_request("/marketplace/browse", params=mobile_params)
        
        if filtered_result["success"]:
            filtered_listings = filtered_result["data"]
            
            browse_tests.append({
                "test": "Mobile Filtered Browse",
                "success": True,
                "response_time_ms": filtered_result["response_time_ms"],
                "mobile_performance_ok": filtered_result["mobile_performance_ok"],
                "listings_count": len(filtered_listings),
                "respects_limit": len(filtered_listings) <= 10,
                "mobile_optimized": len(filtered_listings) <= 10 and filtered_result["mobile_performance_ok"]
            })
            print(f"    ✅ Filtered browse working ({filtered_result['response_time_ms']:.0f}ms, {len(filtered_listings)} listings)")
        else:
            browse_tests.append({
                "test": "Mobile Filtered Browse",
                "success": False,
                "response_time_ms": filtered_result["response_time_ms"],
                "error": filtered_result.get("error", "Filtered browse failed")
            })
            print(f"    ❌ Filtered browse failed: {filtered_result.get('error')}")
        
        # Test 3: Mobile Search API
        print("  Testing mobile search API...")
        search_result = await self.make_request("/marketplace/search", params={"q": "catalyst", "limit": 5})
        
        if search_result["success"]:
            search_data = search_result["data"]
            search_results = search_data.get("results", []) if isinstance(search_data, dict) else search_data
            
            browse_tests.append({
                "test": "Mobile Search API",
                "success": True,
                "response_time_ms": search_result["response_time_ms"],
                "mobile_performance_ok": search_result["mobile_performance_ok"],
                "search_results_count": len(search_results),
                "has_search_results": len(search_results) > 0
            })
            print(f"    ✅ Search API working ({search_result['response_time_ms']:.0f}ms, {len(search_results)} results)")
        else:
            browse_tests.append({
                "test": "Mobile Search API",
                "success": False,
                "response_time_ms": search_result["response_time_ms"],
                "error": search_result.get("error", "Search API failed")
            })
            print(f"    ❌ Search API failed: {search_result.get('error')}")
        
        # Calculate success metrics
        successful_tests = [t for t in browse_tests if t["success"]]
        mobile_performance_ok = [t for t in successful_tests if t.get("mobile_performance_ok", False)]
        
        return {
            "test_name": "Mobile Browse/Marketplace APIs",
            "total_tests": len(browse_tests),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(browse_tests) * 100 if browse_tests else 0,
            "mobile_performance_tests": len(mobile_performance_ok),
            "mobile_performance_rate": len(mobile_performance_ok) / len(successful_tests) * 100 if successful_tests else 0,
            "browse_api_working": any(t.get("test") == "Basic Browse API" and t.get("success") for t in browse_tests),
            "filtered_browse_working": any(t.get("test") == "Mobile Filtered Browse" and t.get("success") for t in browse_tests),
            "search_api_working": any(t.get("test") == "Mobile Search API" and t.get("success") for t in browse_tests),
            "detailed_results": browse_tests
        }
    
    async def test_mobile_admin_apis(self) -> Dict:
        """Test admin APIs used by MobileAdminDrawer"""
        print("⚙️ Testing Mobile Admin APIs...")
        
        if not self.admin_token:
            return {
                "test_name": "Mobile Admin APIs",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        admin_tests = []
        
        # Test 1: Admin Dashboard for Mobile Admin Drawer
        print("  Testing admin dashboard for mobile admin drawer...")
        dashboard_result = await self.make_request("/admin/dashboard", headers=headers)
        
        if dashboard_result["success"]:
            dashboard_data = dashboard_result["data"]
            has_kpis = any(key in dashboard_data for key in ["total_users", "total_revenue", "total_listings"])
            
            admin_tests.append({
                "test": "Admin Dashboard",
                "success": True,
                "response_time_ms": dashboard_result["response_time_ms"],
                "mobile_performance_ok": dashboard_result["mobile_performance_ok"],
                "has_kpis": has_kpis,
                "mobile_friendly": has_kpis and dashboard_result["mobile_performance_ok"]
            })
            print(f"    ✅ Admin dashboard working ({dashboard_result['response_time_ms']:.0f}ms)")
        else:
            admin_tests.append({
                "test": "Admin Dashboard",
                "success": False,
                "response_time_ms": dashboard_result["response_time_ms"],
                "error": dashboard_result.get("error", "Dashboard failed")
            })
            print(f"    ❌ Admin dashboard failed: {dashboard_result.get('error')}")
        
        # Test 2: User Management for Mobile Admin
        print("  Testing user management for mobile admin...")
        users_result = await self.make_request("/admin/users", headers=headers)
        
        if users_result["success"]:
            users_data = users_result["data"]
            
            admin_tests.append({
                "test": "User Management",
                "success": True,
                "response_time_ms": users_result["response_time_ms"],
                "mobile_performance_ok": users_result["mobile_performance_ok"],
                "users_count": len(users_data),
                "has_user_data": len(users_data) > 0
            })
            print(f"    ✅ User management working ({users_result['response_time_ms']:.0f}ms, {len(users_data)} users)")
        else:
            admin_tests.append({
                "test": "User Management",
                "success": False,
                "response_time_ms": users_result["response_time_ms"],
                "error": users_result.get("error", "User management failed")
            })
            print(f"    ❌ User management failed: {users_result.get('error')}")
        
        # Test 3: Performance Metrics for Mobile Admin
        print("  Testing performance metrics for mobile admin...")
        performance_result = await self.make_request("/admin/performance", headers=headers)
        
        if performance_result["success"]:
            performance_data = performance_result["data"]
            has_metrics = any(key in performance_data for key in ["performance_status", "database", "cache"])
            
            admin_tests.append({
                "test": "Performance Metrics",
                "success": True,
                "response_time_ms": performance_result["response_time_ms"],
                "mobile_performance_ok": performance_result["mobile_performance_ok"],
                "has_metrics": has_metrics
            })
            print(f"    ✅ Performance metrics working ({performance_result['response_time_ms']:.0f}ms)")
        else:
            admin_tests.append({
                "test": "Performance Metrics",
                "success": False,
                "response_time_ms": performance_result["response_time_ms"],
                "error": performance_result.get("error", "Performance metrics failed")
            })
            print(f"    ❌ Performance metrics failed: {performance_result.get('error')}")
        
        # Calculate success metrics
        successful_tests = [t for t in admin_tests if t["success"]]
        mobile_performance_ok = [t for t in successful_tests if t.get("mobile_performance_ok", False)]
        
        return {
            "test_name": "Mobile Admin APIs",
            "total_tests": len(admin_tests),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(admin_tests) * 100 if admin_tests else 0,
            "mobile_performance_tests": len(mobile_performance_ok),
            "mobile_performance_rate": len(mobile_performance_ok) / len(successful_tests) * 100 if successful_tests else 0,
            "dashboard_working": any(t.get("test") == "Admin Dashboard" and t.get("success") for t in admin_tests),
            "user_management_working": any(t.get("test") == "User Management" and t.get("success") for t in admin_tests),
            "performance_metrics_working": any(t.get("test") == "Performance Metrics" and t.get("success") for t in admin_tests),
            "detailed_results": admin_tests
        }
    
    async def test_mobile_user_management_apis(self) -> Dict:
        """Test user management APIs for mobile bottom nav and profile"""
        print("👤 Testing Mobile User Management APIs...")
        
        user_tests = []
        
        # Test 1: User Profile Management
        if self.demo_token:
            demo_user_id = None
            # Get user ID from login response
            demo_login_data = {"email": DEMO_EMAIL, "password": "demo_password"}
            demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
            if demo_result["success"]:
                demo_user_id = demo_result["data"].get("user", {}).get("id")
            
            if demo_user_id:
                print("  Testing user profile management for mobile...")
                profile_result = await self.make_request(f"/auth/profile/{demo_user_id}")
                
                if profile_result["success"]:
                    profile_data = profile_result["data"]
                    
                    user_tests.append({
                        "test": "User Profile Management",
                        "success": True,
                        "response_time_ms": profile_result["response_time_ms"],
                        "mobile_performance_ok": profile_result["mobile_performance_ok"],
                        "has_profile_data": bool(profile_data.get("id")),
                        "has_mobile_fields": all(field in profile_data for field in ["email", "username"])
                    })
                    print(f"    ✅ Profile management working ({profile_result['response_time_ms']:.0f}ms)")
                else:
                    user_tests.append({
                        "test": "User Profile Management",
                        "success": False,
                        "response_time_ms": profile_result["response_time_ms"],
                        "error": profile_result.get("error", "Profile management failed")
                    })
                    print(f"    ❌ Profile management failed: {profile_result.get('error')}")
                
                # Test 2: User Listings for Mobile Bottom Nav
                print("  Testing user listings for mobile bottom nav...")
                listings_result = await self.make_request(f"/user/my-listings/{demo_user_id}")
                
                if listings_result["success"]:
                    user_listings = listings_result["data"]
                    
                    user_tests.append({
                        "test": "User Listings",
                        "success": True,
                        "response_time_ms": listings_result["response_time_ms"],
                        "mobile_performance_ok": listings_result["mobile_performance_ok"],
                        "listings_count": len(user_listings),
                        "mobile_optimized": listings_result["mobile_performance_ok"]
                    })
                    print(f"    ✅ User listings working ({listings_result['response_time_ms']:.0f}ms, {len(user_listings)} listings)")
                else:
                    user_tests.append({
                        "test": "User Listings",
                        "success": False,
                        "response_time_ms": listings_result["response_time_ms"],
                        "error": listings_result.get("error", "User listings failed")
                    })
                    print(f"    ❌ User listings failed: {listings_result.get('error')}")
                
                # Test 3: User Deals for Mobile
                print("  Testing user deals for mobile...")
                deals_result = await self.make_request(f"/user/my-deals/{demo_user_id}")
                
                if deals_result["success"]:
                    user_deals = deals_result["data"]
                    
                    user_tests.append({
                        "test": "User Deals",
                        "success": True,
                        "response_time_ms": deals_result["response_time_ms"],
                        "mobile_performance_ok": deals_result["mobile_performance_ok"],
                        "deals_count": len(user_deals),
                        "mobile_optimized": deals_result["mobile_performance_ok"]
                    })
                    print(f"    ✅ User deals working ({deals_result['response_time_ms']:.0f}ms, {len(user_deals)} deals)")
                else:
                    user_tests.append({
                        "test": "User Deals",
                        "success": False,
                        "response_time_ms": deals_result["response_time_ms"],
                        "error": deals_result.get("error", "User deals failed")
                    })
                    print(f"    ❌ User deals failed: {deals_result.get('error')}")
        
        # Test 4: Health Check for Mobile
        print("  Testing health check for mobile...")
        health_result = await self.make_request("/health")
        
        if health_result["success"]:
            health_data = health_result["data"]
            
            user_tests.append({
                "test": "Health Check",
                "success": True,
                "response_time_ms": health_result["response_time_ms"],
                "mobile_performance_ok": health_result["mobile_performance_ok"],
                "status_healthy": health_data.get("status") == "healthy"
            })
            print(f"    ✅ Health check working ({health_result['response_time_ms']:.0f}ms)")
        else:
            user_tests.append({
                "test": "Health Check",
                "success": False,
                "response_time_ms": health_result["response_time_ms"],
                "error": health_result.get("error", "Health check failed")
            })
            print(f"    ❌ Health check failed: {health_result.get('error')}")
        
        # Calculate success metrics
        successful_tests = [t for t in user_tests if t["success"]]
        mobile_performance_ok = [t for t in successful_tests if t.get("mobile_performance_ok", False)]
        
        return {
            "test_name": "Mobile User Management APIs",
            "total_tests": len(user_tests),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(user_tests) * 100 if user_tests else 0,
            "mobile_performance_tests": len(mobile_performance_ok),
            "mobile_performance_rate": len(mobile_performance_ok) / len(successful_tests) * 100 if successful_tests else 0,
            "profile_management_working": any(t.get("test") == "User Profile Management" and t.get("success") for t in user_tests),
            "user_listings_working": any(t.get("test") == "User Listings" and t.get("success") for t in user_tests),
            "user_deals_working": any(t.get("test") == "User Deals" and t.get("success") for t in user_tests),
            "health_check_working": any(t.get("test") == "Health Check" and t.get("success") for t in user_tests),
            "detailed_results": user_tests
        }
    
    async def test_mobile_performance_analysis(self) -> Dict:
        """Test mobile-specific performance requirements"""
        print("📊 Testing Mobile Performance Analysis...")
        
        performance_tests = []
        
        # Test multiple endpoints for mobile performance
        endpoints_to_test = [
            {"endpoint": "/marketplace/browse", "name": "Browse API", "params": {"limit": 10}},
            {"endpoint": "/health", "name": "Health Check", "params": None},
            {"endpoint": "/marketplace/search", "name": "Search API", "params": {"q": "test", "limit": 5}}
        ]
        
        for endpoint_test in endpoints_to_test:
            print(f"  Testing mobile performance: {endpoint_test['name']}...")
            
            # Test multiple times for consistency
            response_times = []
            success_count = 0
            
            for i in range(3):
                result = await self.make_request(endpoint_test["endpoint"], params=endpoint_test["params"])
                response_times.append(result["response_time_ms"])
                if result["success"]:
                    success_count += 1
            
            avg_response_time = statistics.mean(response_times) if response_times else 0
            mobile_performance_ok = avg_response_time < MOBILE_PERFORMANCE_TARGET_MS
            
            performance_tests.append({
                "endpoint": endpoint_test["name"],
                "avg_response_time_ms": avg_response_time,
                "min_response_time_ms": min(response_times) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0,
                "success_rate": (success_count / 3) * 100,
                "mobile_performance_ok": mobile_performance_ok,
                "mobile_target_ms": MOBILE_PERFORMANCE_TARGET_MS
            })
            
            print(f"    {'✅' if mobile_performance_ok else '⚠️'} {endpoint_test['name']}: {avg_response_time:.0f}ms avg")
        
        # Calculate overall mobile performance
        mobile_ready_endpoints = [t for t in performance_tests if t["mobile_performance_ok"]]
        overall_mobile_performance = len(mobile_ready_endpoints) / len(performance_tests) * 100 if performance_tests else 0
        
        return {
            "test_name": "Mobile Performance Analysis",
            "total_endpoints_tested": len(performance_tests),
            "mobile_ready_endpoints": len(mobile_ready_endpoints),
            "mobile_performance_rate": overall_mobile_performance,
            "mobile_target_ms": MOBILE_PERFORMANCE_TARGET_MS,
            "all_endpoints_mobile_ready": overall_mobile_performance == 100,
            "performance_acceptable": overall_mobile_performance >= 75,
            "detailed_results": performance_tests
        }
    
    def check_mobile_listing_data(self, listings: List[Dict]) -> bool:
        """Check if listing data contains mobile-required fields"""
        if not listings:
            return True  # Empty result is valid
        
        required_mobile_fields = ["id", "title", "price"]
        optional_mobile_fields = ["seller", "bid_info", "time_info"]
        
        for listing in listings[:3]:  # Check first 3 listings
            # Check required fields
            for field in required_mobile_fields:
                if field not in listing:
                    return False
            
            # Check seller info for mobile cards
            if "seller" in listing:
                seller = listing["seller"]
                if not isinstance(seller, dict) or "name" not in seller:
                    return False
        
        return True
    
    async def run_comprehensive_mobile_test(self) -> Dict:
        """Run all mobile backend API tests"""
        print("📱 Starting Mobile Interface Backend API Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run all mobile test suites
            auth_results = await self.test_mobile_authentication_apis()
            browse_results = await self.test_mobile_browse_marketplace_apis()
            admin_results = await self.test_mobile_admin_apis()
            user_results = await self.test_mobile_user_management_apis()
            performance_results = await self.test_mobile_performance_analysis()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "mobile_performance_target_ms": MOBILE_PERFORMANCE_TARGET_MS,
                "mobile_timeout_ms": MOBILE_TIMEOUT_MS,
                "authentication_apis": auth_results,
                "browse_marketplace_apis": browse_results,
                "admin_apis": admin_results,
                "user_management_apis": user_results,
                "mobile_performance_analysis": performance_results
            }
            
            # Calculate overall success metrics
            test_categories = [auth_results, browse_results, admin_results, user_results, performance_results]
            category_success_rates = [cat.get("success_rate", 0) for cat in test_categories if "success_rate" in cat]
            
            overall_success_rate = statistics.mean(category_success_rates) if category_success_rates else 0
            
            # Mobile-specific metrics
            mobile_performance_rates = [cat.get("mobile_performance_rate", 0) for cat in test_categories if "mobile_performance_rate" in cat]
            overall_mobile_performance = statistics.mean(mobile_performance_rates) if mobile_performance_rates else 0
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "overall_mobile_performance_rate": overall_mobile_performance,
                "authentication_working": auth_results.get("success_rate", 0) >= 75,
                "browse_marketplace_working": browse_results.get("success_rate", 0) >= 75,
                "admin_apis_working": admin_results.get("success_rate", 0) >= 75,
                "user_management_working": user_results.get("success_rate", 0) >= 75,
                "mobile_performance_acceptable": performance_results.get("performance_acceptable", False),
                "all_mobile_apis_working": overall_success_rate >= 80,
                "mobile_ready": overall_mobile_performance >= 70
            }
            
            return all_results
            
        finally:
            await self.cleanup()

# Main execution
async def main():
    """Run mobile backend API tests"""
    tester = MobileBackendTester()
    results = await tester.run_comprehensive_mobile_test()
    
    print("\n" + "=" * 60)
    print("📱 MOBILE BACKEND API TEST RESULTS")
    print("=" * 60)
    
    summary = results.get("summary", {})
    
    print(f"Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"Mobile Performance Rate: {summary.get('overall_mobile_performance_rate', 0):.1f}%")
    print(f"Mobile Ready: {'✅' if summary.get('mobile_ready', False) else '❌'}")
    
    print("\nAPI Category Results:")
    print(f"  Authentication APIs: {'✅' if summary.get('authentication_working', False) else '❌'}")
    print(f"  Browse/Marketplace APIs: {'✅' if summary.get('browse_marketplace_working', False) else '❌'}")
    print(f"  Admin APIs: {'✅' if summary.get('admin_apis_working', False) else '❌'}")
    print(f"  User Management APIs: {'✅' if summary.get('user_management_working', False) else '❌'}")
    print(f"  Mobile Performance: {'✅' if summary.get('mobile_performance_acceptable', False) else '❌'}")
    
    # Save detailed results
    with open('/app/mobile_backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: /app/mobile_backend_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())