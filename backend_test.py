#!/usr/bin/env python3
"""
Cataloro Marketplace Admin Authentication & Database Consistency Testing
Testing admin user authentication and database integrity after recent fixes
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-boost.preview.emergentagent.com/api"
PERFORMANCE_TARGET_MS = 1000  # Browse endpoint should respond in under 1 second
CACHE_IMPROVEMENT_TARGET = 20  # Cached responses should be at least 20% faster

# Admin User Configuration (from review request)
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"
ADMIN_ROLE = "admin"
ADMIN_ID = "admin_user_1"

class AdminAuthenticationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.admin_token = None
        
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
        """Run all admin authentication and database consistency tests"""
        print("🚀 Starting Cataloro Admin Authentication & Database Consistency Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test suites
            admin_auth = await self.test_admin_user_authentication()
            db_consistency = await self.test_database_user_consistency()
            user_management = await self.test_user_management_endpoints()
            browse_performance = await self.test_browse_endpoint_performance()
            admin_functionality = await self.test_admin_functionality()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "admin_authentication": admin_auth,
                "database_consistency": db_consistency,
                "user_management_endpoints": user_management,
                "browse_endpoint_performance": browse_performance,
                "admin_functionality": admin_functionality
            }
            
            # Calculate overall success metrics
            test_results = [
                admin_auth.get("all_admin_properties_correct", False),
                db_consistency.get("all_users_consistent", False),
                user_management.get("all_endpoints_working", False),
                browse_performance.get("endpoint_working", False),
                admin_functionality.get("all_admin_features_working", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "admin_authentication_working": admin_auth.get("all_admin_properties_correct", False),
                "database_consistency_verified": db_consistency.get("all_users_consistent", False),
                "user_management_operational": user_management.get("all_endpoints_working", False),
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

async def main():
    """Main test execution"""
    tester = BrowseEndpointTester()
    results = await tester.run_comprehensive_test()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("=" * 60)
    
    summary = results["summary"]
    basic = results["basic_performance"]
    cache = results["cache_performance"]
    filtering = results["filtering_performance"]
    concurrent = results["concurrent_performance"]
    pagination = results["pagination_performance"]
    
    print(f"🎯 Performance Target: {results['performance_target_ms']}ms")
    print(f"📈 Cache Improvement Target: {results['cache_improvement_target_percent']}%")
    print()
    
    # Basic Performance
    status = "✅" if basic.get("meets_performance_target") else "❌"
    print(f"{status} Basic Browse Performance: {basic.get('avg_response_time_ms', 0):.0f}ms avg")
    
    # Cache Performance
    cache_status = "✅" if cache.get("cache_working") else "❌"
    improvement = cache.get("cache_improvement_percent", 0)
    print(f"{cache_status} Cache Performance: {improvement:.1f}% improvement")
    
    # Data Integrity
    integrity_status = "✅" if summary.get("data_integrity_excellent") else "❌"
    integrity = summary.get("average_data_integrity_score", 0)
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
    print("🏆 OVERALL RESULTS:")
    overall_status = "✅ EXCELLENT" if summary.get("performance_target_met") and summary.get("cache_target_met") else "⚠️ NEEDS IMPROVEMENT"
    print(f"   {overall_status}")
    print(f"   Performance Success Rate: {summary.get('overall_performance_success_rate', 0):.0f}%")
    print(f"   Cache Working: {'Yes' if summary.get('cache_functionality_working') else 'No'}")
    print(f"   Data Integrity: {summary.get('average_data_integrity_score', 0):.0f}%")
    
    # Save detailed results
    with open("/app/browse_performance_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/browse_performance_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())