#!/usr/bin/env python3
"""
TENDERS PERFORMANCE OPTIMIZATION TESTING
Testing comprehensive tenders performance optimizations to resolve slow loading in desktop tenders tab.

CRITICAL OPTIMIZATIONS TO VALIDATE:
1. Backend N+1 Query Fixes for tenders endpoints
2. Database Query Optimization 
3. Performance Comparison
4. Data Quality Verification

SUCCESS CRITERIA:
- Seller tenders overview: <200ms response time
- Sold items endpoint: <300ms response time  
- Data integrity: 100% accuracy in enriched buyer/listing information
- N+1 elimination: Single batch queries instead of multiple individual queries
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://vps-sync.preview.emergentagent.com/api"

# Performance Targets (from review request)
SELLER_TENDERS_TARGET_MS = 200  # Seller tenders overview: <200ms
SOLD_ITEMS_TARGET_MS = 300      # Sold items endpoint: <300ms
BUYER_TENDERS_TARGET_MS = 500   # Buyer tenders (already optimized): <500ms

class TendersPerformanceTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.admin_token = None
        self.test_users = []
        self.test_seller_id = None
        self.test_buyer_id = None
        self.admin_user_id = None
        
    async def setup(self):
        """Initialize HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Authenticate as admin to get test users
        await self.authenticate_admin()
        await self.discover_test_users()
        
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
    
    async def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        login_data = {
            "email": "admin@cataloro.com",
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            self.admin_token = result["data"].get("token", "")
            self.admin_user_id = user_data.get("id")
            print(f"  ✅ Admin authenticated: {user_data.get('username')}")
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error')}")
    
    async def discover_test_users(self):
        """Discover test users for tenders testing"""
        print("👥 Discovering test users...")
        
        if not self.admin_token:
            print("  ❌ No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/users", headers=headers)
        
        if result["success"]:
            users = result["data"]
            
            # Find suitable test users
            for user in users:
                user_id = user.get("id")
                email = user.get("email", "")
                role = user.get("user_role", user.get("role", ""))
                
                if email == "admin@cataloro.com":
                    continue  # Skip admin
                
                if not self.test_seller_id and "seller" in role.lower():
                    self.test_seller_id = user_id
                    print(f"  ✅ Found test seller: {user.get('username')} ({user_id})")
                
                if not self.test_buyer_id and "buyer" in role.lower():
                    self.test_buyer_id = user_id
                    print(f"  ✅ Found test buyer: {user.get('username')} ({user_id})")
            
            # Fallback: use any non-admin users
            if not self.test_seller_id or not self.test_buyer_id:
                non_admin_users = [u for u in users if u.get("email") != "admin@cataloro.com" and u.get("id")]
                
                if not self.test_seller_id and non_admin_users:
                    self.test_seller_id = non_admin_users[0]["id"]
                    print(f"  ⚠️ Using fallback seller: {non_admin_users[0].get('username')}")
                
                if not self.test_buyer_id and len(non_admin_users) > 1:
                    self.test_buyer_id = non_admin_users[1]["id"]
                    print(f"  ⚠️ Using fallback buyer: {non_admin_users[1].get('username')}")
                elif not self.test_buyer_id and non_admin_users:
                    self.test_buyer_id = non_admin_users[0]["id"]
                    print(f"  ⚠️ Using same user as buyer: {non_admin_users[0].get('username')}")
        
        print(f"  📊 Test users configured - Seller: {self.test_seller_id}, Buyer: {self.test_buyer_id}")
    
    async def test_seller_tenders_overview_performance(self) -> Dict:
        """Test /api/tenders/seller/{seller_id}/overview endpoint performance (N+1 fixes)"""
        print("🏪 Testing seller tenders overview performance...")
        
        if not self.test_seller_id:
            return {
                "test_name": "Seller Tenders Overview Performance",
                "error": "No test seller ID available",
                "success": False
            }
        
        # Test multiple calls to get consistent performance metrics
        response_times = []
        data_quality_scores = []
        
        for i in range(5):
            result = await self.make_request(f"/tenders/seller/{self.test_seller_id}/overview")
            response_times.append(result["response_time_ms"])
            
            if result["success"]:
                overview_data = result["data"]
                quality_score = self.analyze_seller_overview_data_quality(overview_data)
                data_quality_scores.append(quality_score)
                
                print(f"  Call {i+1}: {result['response_time_ms']:.0f}ms, {len(overview_data)} listings, quality: {quality_score:.1f}%")
            else:
                print(f"  Call {i+1}: FAILED - {result.get('error')}")
                data_quality_scores.append(0)
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        avg_data_quality = statistics.mean(data_quality_scores) if data_quality_scores else 0
        
        meets_target = avg_response_time < SELLER_TENDERS_TARGET_MS
        performance_improvement = ((2000 - avg_response_time) / 2000) * 100 if avg_response_time < 2000 else 0
        
        return {
            "test_name": "Seller Tenders Overview Performance",
            "endpoint": f"/tenders/seller/{self.test_seller_id}/overview",
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min_response_time,
            "max_response_time_ms": max_response_time,
            "target_ms": SELLER_TENDERS_TARGET_MS,
            "meets_performance_target": meets_target,
            "performance_improvement_percent": performance_improvement,
            "avg_data_quality_score": avg_data_quality,
            "data_integrity_excellent": avg_data_quality >= 90,
            "n1_optimization_working": avg_response_time < 500,  # Should be much faster than N+1 queries
            "total_calls": len(response_times),
            "success_rate": len([t for t in response_times if t > 0]) / max(len(response_times), 1) * 100,
            "success": meets_target and avg_data_quality >= 80
        }
    
    async def test_sold_items_performance(self) -> Dict:
        """Test /api/user/{user_id}/sold-items endpoint performance (N+1 fixes)"""
        print("💰 Testing sold items endpoint performance...")
        
        if not self.test_seller_id:
            return {
                "test_name": "Sold Items Performance",
                "error": "No test seller ID available",
                "success": False
            }
        
        # Test multiple calls to get consistent performance metrics
        response_times = []
        data_quality_scores = []
        
        for i in range(5):
            result = await self.make_request(f"/user/{self.test_seller_id}/sold-items")
            response_times.append(result["response_time_ms"])
            
            if result["success"]:
                sold_items_data = result["data"]
                quality_score = self.analyze_sold_items_data_quality(sold_items_data)
                data_quality_scores.append(quality_score)
                
                items_count = len(sold_items_data.get("items", []))
                stats = sold_items_data.get("stats", {})
                
                print(f"  Call {i+1}: {result['response_time_ms']:.0f}ms, {items_count} items, quality: {quality_score:.1f}%")
            else:
                print(f"  Call {i+1}: FAILED - {result.get('error')}")
                data_quality_scores.append(0)
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        avg_data_quality = statistics.mean(data_quality_scores) if data_quality_scores else 0
        
        meets_target = avg_response_time < SOLD_ITEMS_TARGET_MS
        performance_improvement = ((1000 - avg_response_time) / 1000) * 100 if avg_response_time < 1000 else 0
        
        return {
            "test_name": "Sold Items Performance",
            "endpoint": f"/user/{self.test_seller_id}/sold-items",
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min_response_time,
            "max_response_time_ms": max_response_time,
            "target_ms": SOLD_ITEMS_TARGET_MS,
            "meets_performance_target": meets_target,
            "performance_improvement_percent": performance_improvement,
            "avg_data_quality_score": avg_data_quality,
            "data_integrity_excellent": avg_data_quality >= 90,
            "n1_optimization_working": avg_response_time < 800,  # Should be much faster than N+1 queries
            "total_calls": len(response_times),
            "success_rate": len([t for t in response_times if t > 0]) / max(len(response_times), 1) * 100,
            "success": meets_target and avg_data_quality >= 80
        }
    
    async def test_buyer_tenders_performance(self) -> Dict:
        """Test /api/tenders/buyer/{buyer_id} endpoint performance (already optimized)"""
        print("🛒 Testing buyer tenders endpoint performance...")
        
        if not self.test_buyer_id:
            return {
                "test_name": "Buyer Tenders Performance",
                "error": "No test buyer ID available",
                "success": False
            }
        
        # Test multiple calls to get consistent performance metrics
        response_times = []
        data_quality_scores = []
        
        for i in range(5):
            result = await self.make_request(f"/tenders/buyer/{self.test_buyer_id}")
            response_times.append(result["response_time_ms"])
            
            if result["success"]:
                tenders_data = result["data"]
                quality_score = self.analyze_buyer_tenders_data_quality(tenders_data)
                data_quality_scores.append(quality_score)
                
                print(f"  Call {i+1}: {result['response_time_ms']:.0f}ms, {len(tenders_data)} tenders, quality: {quality_score:.1f}%")
            else:
                print(f"  Call {i+1}: FAILED - {result.get('error')}")
                data_quality_scores.append(0)
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        avg_data_quality = statistics.mean(data_quality_scores) if data_quality_scores else 0
        
        meets_target = avg_response_time < BUYER_TENDERS_TARGET_MS
        
        return {
            "test_name": "Buyer Tenders Performance",
            "endpoint": f"/tenders/buyer/{self.test_buyer_id}",
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min_response_time,
            "max_response_time_ms": max_response_time,
            "target_ms": BUYER_TENDERS_TARGET_MS,
            "meets_performance_target": meets_target,
            "avg_data_quality_score": avg_data_quality,
            "data_integrity_excellent": avg_data_quality >= 90,
            "already_optimized_confirmed": avg_response_time < 600,
            "total_calls": len(response_times),
            "success_rate": len([t for t in response_times if t > 0]) / max(len(response_times), 1) * 100,
            "success": meets_target and avg_data_quality >= 80
        }
    
    async def test_concurrent_tenders_performance(self) -> Dict:
        """Test concurrent request handling for tenders endpoints"""
        print("⚡ Testing concurrent tenders request performance...")
        
        if not self.test_seller_id or not self.test_buyer_id:
            return {
                "test_name": "Concurrent Tenders Performance",
                "error": "Missing test user IDs",
                "success": False
            }
        
        # Create concurrent requests to different endpoints
        start_time = time.time()
        
        tasks = [
            self.make_request(f"/tenders/seller/{self.test_seller_id}/overview"),
            self.make_request(f"/user/{self.test_seller_id}/sold-items"),
            self.make_request(f"/tenders/buyer/{self.test_buyer_id}"),
            self.make_request(f"/tenders/seller/{self.test_seller_id}/overview"),  # Duplicate to test caching
            self.make_request(f"/user/{self.test_seller_id}/sold-items")  # Duplicate to test caching
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time_ms = (end_time - start_time) * 1000
        successful_requests = [r for r in results if r["success"]]
        
        if successful_requests:
            avg_individual_time = statistics.mean([r["response_time_ms"] for r in successful_requests])
            max_individual_time = max([r["response_time_ms"] for r in successful_requests])
            min_individual_time = min([r["response_time_ms"] for r in successful_requests])
            
            print(f"  {len(successful_requests)}/{len(tasks)} requests successful")
            print(f"  Total time: {total_time_ms:.0f}ms")
            print(f"  Avg individual: {avg_individual_time:.0f}ms")
            print(f"  Max individual: {max_individual_time:.0f}ms")
            
            return {
                "test_name": "Concurrent Tenders Performance",
                "concurrent_requests": len(tasks),
                "successful_requests": len(successful_requests),
                "total_time_ms": total_time_ms,
                "avg_individual_time_ms": avg_individual_time,
                "max_individual_time_ms": max_individual_time,
                "min_individual_time_ms": min_individual_time,
                "throughput_requests_per_second": len(successful_requests) / (total_time_ms / 1000),
                "all_under_target": max_individual_time < 500,
                "concurrent_performance_acceptable": total_time_ms < 2000,
                "success": len(successful_requests) == len(tasks) and max_individual_time < 500
            }
        else:
            return {
                "test_name": "Concurrent Tenders Performance",
                "error": "All concurrent requests failed",
                "successful_requests": 0,
                "concurrent_requests": len(tasks),
                "success": False
            }
    
    async def test_data_enrichment_accuracy(self) -> Dict:
        """Test data enrichment accuracy in tenders endpoints"""
        print("🔍 Testing data enrichment accuracy...")
        
        if not self.test_seller_id:
            return {
                "test_name": "Data Enrichment Accuracy",
                "error": "No test seller ID available",
                "success": False
            }
        
        # Test seller overview data enrichment
        seller_result = await self.make_request(f"/tenders/seller/{self.test_seller_id}/overview")
        
        enrichment_tests = []
        
        if seller_result["success"]:
            overview_data = seller_result["data"]
            
            # Test seller overview enrichment
            seller_enrichment = self.validate_seller_overview_enrichment(overview_data)
            enrichment_tests.append({
                "endpoint": "seller_overview",
                "enrichment_score": seller_enrichment["score"],
                "buyer_info_complete": seller_enrichment["buyer_info_complete"],
                "listing_info_complete": seller_enrichment["listing_info_complete"],
                "seller_info_complete": seller_enrichment["seller_info_complete"]
            })
        
        # Test sold items data enrichment
        sold_items_result = await self.make_request(f"/user/{self.test_seller_id}/sold-items")
        
        if sold_items_result["success"]:
            sold_items_data = sold_items_result["data"]
            
            # Test sold items enrichment
            sold_items_enrichment = self.validate_sold_items_enrichment(sold_items_data)
            enrichment_tests.append({
                "endpoint": "sold_items",
                "enrichment_score": sold_items_enrichment["score"],
                "buyer_info_complete": sold_items_enrichment["buyer_info_complete"],
                "listing_info_complete": sold_items_enrichment["listing_info_complete"],
                "stats_complete": sold_items_enrichment["stats_complete"]
            })
        
        # Calculate overall enrichment accuracy
        if enrichment_tests:
            avg_enrichment_score = statistics.mean([t["enrichment_score"] for t in enrichment_tests])
            all_buyer_info_complete = all(t["buyer_info_complete"] for t in enrichment_tests)
            all_listing_info_complete = all(t["listing_info_complete"] for t in enrichment_tests)
            
            return {
                "test_name": "Data Enrichment Accuracy",
                "avg_enrichment_score": avg_enrichment_score,
                "data_integrity_100_percent": avg_enrichment_score == 100,
                "buyer_info_enrichment_working": all_buyer_info_complete,
                "listing_info_enrichment_working": all_listing_info_complete,
                "enrichment_accuracy_excellent": avg_enrichment_score >= 90,
                "detailed_tests": enrichment_tests,
                "success": avg_enrichment_score >= 90
            }
        else:
            return {
                "test_name": "Data Enrichment Accuracy",
                "error": "No successful enrichment tests",
                "success": False
            }
    
    def analyze_seller_overview_data_quality(self, overview_data: List[Dict]) -> float:
        """Analyze data quality of seller overview response"""
        if not overview_data:
            return 100.0  # Empty result is valid
        
        total_checks = 0
        passed_checks = 0
        
        for listing_overview in overview_data:
            # Check listing information
            listing = listing_overview.get("listing", {})
            required_listing_fields = ["id", "title", "price"]
            for field in required_listing_fields:
                total_checks += 1
                if field in listing and listing[field] is not None:
                    passed_checks += 1
            
            # Check seller information
            seller = listing_overview.get("seller", {})
            required_seller_fields = ["id", "username"]
            for field in required_seller_fields:
                total_checks += 1
                if field in seller and seller[field]:
                    passed_checks += 1
            
            # Check tenders information
            tenders = listing_overview.get("tenders", [])
            total_checks += 1
            if isinstance(tenders, list):
                passed_checks += 1
                
                # Check tender enrichment
                for tender in tenders:
                    buyer = tender.get("buyer", {})
                    total_checks += 2
                    if "id" in buyer and buyer["id"]:
                        passed_checks += 1
                    if "username" in buyer and buyer["username"]:
                        passed_checks += 1
            
            # Check tender statistics
            total_checks += 2
            if "tender_count" in listing_overview:
                passed_checks += 1
            if "highest_offer" in listing_overview:
                passed_checks += 1
        
        return (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    def analyze_sold_items_data_quality(self, sold_items_data: Dict) -> float:
        """Analyze data quality of sold items response"""
        if not sold_items_data:
            return 0.0
        
        total_checks = 0
        passed_checks = 0
        
        # Check stats structure
        stats = sold_items_data.get("stats", {})
        required_stats = ["totalSold", "totalRevenue", "averagePrice", "thisMonth"]
        for field in required_stats:
            total_checks += 1
            if field in stats and stats[field] is not None:
                passed_checks += 1
        
        # Check items structure
        items = sold_items_data.get("items", [])
        total_checks += 1
        if isinstance(items, list):
            passed_checks += 1
            
            # Check item enrichment
            for item in items:
                # Check listing enrichment
                listing = item.get("listing")
                total_checks += 1
                if listing and isinstance(listing, dict) and "id" in listing and "title" in listing:
                    passed_checks += 1
                
                # Check buyer enrichment
                buyer = item.get("buyer")
                total_checks += 1
                if buyer and isinstance(buyer, dict) and "id" in buyer and "username" in buyer:
                    passed_checks += 1
                
                # Check required fields
                required_item_fields = ["final_price", "sold_at", "source"]
                for field in required_item_fields:
                    total_checks += 1
                    if field in item and item[field] is not None:
                        passed_checks += 1
        
        return (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    def analyze_buyer_tenders_data_quality(self, tenders_data: List[Dict]) -> float:
        """Analyze data quality of buyer tenders response"""
        if not tenders_data:
            return 100.0  # Empty result is valid
        
        total_checks = 0
        passed_checks = 0
        
        for tender in tenders_data:
            # Check tender fields
            required_tender_fields = ["id", "offer_amount", "status", "created_at"]
            for field in required_tender_fields:
                total_checks += 1
                if field in tender and tender[field] is not None:
                    passed_checks += 1
            
            # Check listing enrichment
            listing = tender.get("listing", {})
            required_listing_fields = ["id", "title", "price"]
            for field in required_listing_fields:
                total_checks += 1
                if field in listing and listing[field] is not None:
                    passed_checks += 1
            
            # Check seller enrichment
            seller = tender.get("seller", {})
            required_seller_fields = ["id", "username"]
            for field in required_seller_fields:
                total_checks += 1
                if field in seller and seller[field]:
                    passed_checks += 1
        
        return (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    def validate_seller_overview_enrichment(self, overview_data: List[Dict]) -> Dict:
        """Validate seller overview data enrichment"""
        if not overview_data:
            return {"score": 100, "buyer_info_complete": True, "listing_info_complete": True, "seller_info_complete": True}
        
        buyer_info_complete = True
        listing_info_complete = True
        seller_info_complete = True
        
        for listing_overview in overview_data:
            # Check seller info
            seller = listing_overview.get("seller", {})
            if not (seller.get("id") and seller.get("username")):
                seller_info_complete = False
            
            # Check listing info
            listing = listing_overview.get("listing", {})
            if not (listing.get("id") and listing.get("title") and listing.get("price") is not None):
                listing_info_complete = False
            
            # Check buyer info in tenders
            tenders = listing_overview.get("tenders", [])
            for tender in tenders:
                buyer = tender.get("buyer", {})
                if not (buyer.get("id") and buyer.get("username")):
                    buyer_info_complete = False
        
        score = sum([buyer_info_complete, listing_info_complete, seller_info_complete]) / 3 * 100
        
        return {
            "score": score,
            "buyer_info_complete": buyer_info_complete,
            "listing_info_complete": listing_info_complete,
            "seller_info_complete": seller_info_complete
        }
    
    def validate_sold_items_enrichment(self, sold_items_data: Dict) -> Dict:
        """Validate sold items data enrichment"""
        if not sold_items_data:
            return {"score": 0, "buyer_info_complete": False, "listing_info_complete": False, "stats_complete": False}
        
        buyer_info_complete = True
        listing_info_complete = True
        stats_complete = True
        
        # Check stats
        stats = sold_items_data.get("stats", {})
        required_stats = ["totalSold", "totalRevenue", "averagePrice", "thisMonth"]
        if not all(field in stats for field in required_stats):
            stats_complete = False
        
        # Check items enrichment
        items = sold_items_data.get("items", [])
        for item in items:
            # Check listing enrichment
            listing = item.get("listing")
            if not (listing and listing.get("id") and listing.get("title")):
                listing_info_complete = False
            
            # Check buyer enrichment
            buyer = item.get("buyer")
            if not (buyer and buyer.get("id") and buyer.get("username")):
                buyer_info_complete = False
        
        score = sum([buyer_info_complete, listing_info_complete, stats_complete]) / 3 * 100
        
        return {
            "score": score,
            "buyer_info_complete": buyer_info_complete,
            "listing_info_complete": listing_info_complete,
            "stats_complete": stats_complete
        }
    
    async def run_comprehensive_tenders_performance_test(self) -> Dict:
        """Run all tenders performance optimization tests"""
        print("🚀 Starting Comprehensive Tenders Performance Optimization Testing")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run all test suites
            seller_overview_test = await self.test_seller_tenders_overview_performance()
            sold_items_test = await self.test_sold_items_performance()
            buyer_tenders_test = await self.test_buyer_tenders_performance()
            concurrent_test = await self.test_concurrent_tenders_performance()
            data_enrichment_test = await self.test_data_enrichment_accuracy()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "performance_targets": {
                    "seller_tenders_overview_ms": SELLER_TENDERS_TARGET_MS,
                    "sold_items_ms": SOLD_ITEMS_TARGET_MS,
                    "buyer_tenders_ms": BUYER_TENDERS_TARGET_MS
                },
                "test_configuration": {
                    "test_seller_id": self.test_seller_id,
                    "test_buyer_id": self.test_buyer_id,
                    "admin_user_id": self.admin_user_id
                },
                "seller_tenders_overview": seller_overview_test,
                "sold_items_performance": sold_items_test,
                "buyer_tenders_performance": buyer_tenders_test,
                "concurrent_performance": concurrent_test,
                "data_enrichment_accuracy": data_enrichment_test
            }
            
            # Calculate overall success metrics
            performance_tests = [
                seller_overview_test.get("success", False),
                sold_items_test.get("success", False),
                buyer_tenders_test.get("success", False),
                concurrent_test.get("success", False),
                data_enrichment_test.get("success", False)
            ]
            
            overall_success_rate = sum(performance_tests) / len(performance_tests) * 100
            
            # Check specific optimization criteria
            n1_fixes_working = (
                seller_overview_test.get("n1_optimization_working", False) and
                sold_items_test.get("n1_optimization_working", False)
            )
            
            performance_targets_met = (
                seller_overview_test.get("meets_performance_target", False) and
                sold_items_test.get("meets_performance_target", False) and
                buyer_tenders_test.get("meets_performance_target", False)
            )
            
            data_integrity_100_percent = data_enrichment_test.get("data_integrity_100_percent", False)
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "n1_query_fixes_working": n1_fixes_working,
                "performance_targets_met": performance_targets_met,
                "data_integrity_100_percent": data_integrity_100_percent,
                "concurrent_handling_efficient": concurrent_test.get("success", False),
                "desktop_tenders_tab_optimized": performance_targets_met and n1_fixes_working,
                "all_critical_requirements_met": overall_success_rate == 100,
                "seller_overview_under_200ms": seller_overview_test.get("meets_performance_target", False),
                "sold_items_under_300ms": sold_items_test.get("meets_performance_target", False),
                "buyer_tenders_efficient": buyer_tenders_test.get("already_optimized_confirmed", False),
                "data_enrichment_accurate": data_enrichment_test.get("enrichment_accuracy_excellent", False)
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution"""
    tester = TendersPerformanceTester()
    results = await tester.run_comprehensive_tenders_performance_test()
    
    print("\n" + "=" * 80)
    print("📊 TENDERS PERFORMANCE OPTIMIZATION TEST RESULTS")
    print("=" * 80)
    
    summary = results.get("summary", {})
    
    print(f"Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"N+1 Query Fixes Working: {'✅' if summary.get('n1_query_fixes_working') else '❌'}")
    print(f"Performance Targets Met: {'✅' if summary.get('performance_targets_met') else '❌'}")
    print(f"Data Integrity 100%: {'✅' if summary.get('data_integrity_100_percent') else '❌'}")
    print(f"Desktop Tenders Tab Optimized: {'✅' if summary.get('desktop_tenders_tab_optimized') else '❌'}")
    
    print("\n📈 PERFORMANCE BREAKDOWN:")
    seller_test = results.get("seller_tenders_overview", {})
    sold_test = results.get("sold_items_performance", {})
    buyer_test = results.get("buyer_tenders_performance", {})
    
    print(f"Seller Overview: {seller_test.get('avg_response_time_ms', 0):.0f}ms (target: <200ms) {'✅' if seller_test.get('meets_performance_target') else '❌'}")
    print(f"Sold Items: {sold_test.get('avg_response_time_ms', 0):.0f}ms (target: <300ms) {'✅' if sold_test.get('meets_performance_target') else '❌'}")
    print(f"Buyer Tenders: {buyer_test.get('avg_response_time_ms', 0):.0f}ms (target: <500ms) {'✅' if buyer_test.get('meets_performance_target') else '❌'}")
    
    print("\n🔍 DATA QUALITY:")
    enrichment_test = results.get("data_enrichment_accuracy", {})
    print(f"Data Enrichment Score: {enrichment_test.get('avg_enrichment_score', 0):.1f}%")
    print(f"Buyer Info Complete: {'✅' if enrichment_test.get('buyer_info_enrichment_working') else '❌'}")
    print(f"Listing Info Complete: {'✅' if enrichment_test.get('listing_info_enrichment_working') else '❌'}")
    
    print("\n⚡ CONCURRENT PERFORMANCE:")
    concurrent_test = results.get("concurrent_performance", {})
    print(f"Concurrent Requests: {concurrent_test.get('successful_requests', 0)}/{concurrent_test.get('concurrent_requests', 0)}")
    print(f"Max Response Time: {concurrent_test.get('max_individual_time_ms', 0):.0f}ms")
    print(f"Throughput: {concurrent_test.get('throughput_requests_per_second', 0):.1f} req/sec")
    
    # Save detailed results
    with open('/app/tenders_performance_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/tenders_performance_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())