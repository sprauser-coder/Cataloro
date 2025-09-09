#!/usr/bin/env python3
"""
Cataloro Marketplace Browse Endpoint Performance Testing
Testing performance and functionality after recent optimizations
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