#!/usr/bin/env python3
"""
Browse Page & Hero Functionality Backend Testing
Testing browse page API endpoints and hero-related functionality after frontend hero section fixes
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

class BrowseHeroTester:
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
    
    async def test_browse_endpoint_basic(self) -> Dict:
        """Test basic browse endpoint functionality"""
        print("🔍 Testing browse endpoint basic functionality...")
        
        result = await self.make_request("/marketplace/browse")
        
        if result["success"]:
            listings = result["data"]
            
            # Check data structure
            has_seller_info = all("seller" in listing for listing in listings[:3]) if listings else True
            has_bid_info = all("bid_info" in listing for listing in listings[:3]) if listings else True
            has_time_info = all("time_info" in listing for listing in listings[:3]) if listings else True
            
            print(f"  ✅ Browse endpoint working: {len(listings)} listings found")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            print(f"  📊 Seller info present: {has_seller_info}")
            print(f"  📊 Bid info present: {has_bid_info}")
            print(f"  📊 Time info present: {has_time_info}")
            
            return {
                "test_name": "Browse Endpoint Basic",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "listings_count": len(listings),
                "has_seller_info": has_seller_info,
                "has_bid_info": has_bid_info,
                "has_time_info": has_time_info,
                "data_structure_complete": has_seller_info and has_bid_info and has_time_info
            }
        else:
            print(f"  ❌ Browse endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Browse Endpoint Basic",
                "success": False,
                "error": result.get("error", "Browse endpoint failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"]
            }
    
    async def test_browse_endpoint_filters(self) -> Dict:
        """Test browse endpoint with various filters"""
        print("🔧 Testing browse endpoint filters...")
        
        filter_tests = [
            {"name": "All listings", "params": {}},
            {"name": "Private sellers", "params": {"type": "Private"}},
            {"name": "Business sellers", "params": {"type": "Business"}},
            {"name": "Price range", "params": {"price_from": 100, "price_to": 500}},
            {"name": "Pagination", "params": {"page": 1, "limit": 5}}
        ]
        
        results = []
        
        for test in filter_tests:
            print(f"  Testing: {test['name']}")
            result = await self.make_request("/marketplace/browse", params=test["params"])
            
            if result["success"]:
                listings = result["data"]
                
                test_result = {
                    "filter_name": test["name"],
                    "success": True,
                    "response_time_ms": result["response_time_ms"],
                    "listings_count": len(listings)
                }
                
                print(f"    ✅ {result['response_time_ms']:.0f}ms, {len(listings)} listings")
            else:
                test_result = {
                    "filter_name": test["name"],
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "response_time_ms": result["response_time_ms"]
                }
                print(f"    ❌ FAILED - {result.get('error', 'Unknown error')}")
            
            results.append(test_result)
        
        successful_tests = [r for r in results if r["success"]]
        
        return {
            "test_name": "Browse Endpoint Filters",
            "total_filter_tests": len(filter_tests),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(filter_tests) * 100,
            "all_filters_working": len(successful_tests) == len(filter_tests),
            "detailed_results": results
        }
    
    async def test_hero_related_endpoints(self) -> Dict:
        """Test for any hero-related backend endpoints"""
        print("🦸 Testing hero-related endpoints...")
        
        # Common hero-related endpoint patterns
        hero_endpoints = [
            "/hero",
            "/hero/data",
            "/hero/content",
            "/hero/banner",
            "/hero/featured",
            "/marketplace/hero",
            "/marketplace/featured",
            "/marketplace/banner",
            "/content/hero",
            "/admin/hero",
            "/admin/hero/settings"
        ]
        
        results = []
        
        for endpoint in hero_endpoints:
            print(f"  Testing: {endpoint}")
            result = await self.make_request(endpoint)
            
            if result["success"]:
                print(f"    ✅ Found hero endpoint: {endpoint}")
                results.append({
                    "endpoint": endpoint,
                    "exists": True,
                    "response_time_ms": result["response_time_ms"],
                    "has_data": bool(result.get("data"))
                })
            elif result["status"] == 404:
                print(f"    ⚪ Not found: {endpoint}")
                results.append({
                    "endpoint": endpoint,
                    "exists": False,
                    "status": 404
                })
            else:
                print(f"    ❌ Error: {endpoint} - {result.get('error', 'Unknown error')}")
                results.append({
                    "endpoint": endpoint,
                    "exists": False,
                    "error": result.get("error", "Unknown error"),
                    "status": result["status"]
                })
        
        existing_endpoints = [r for r in results if r.get("exists", False)]
        
        return {
            "test_name": "Hero Related Endpoints",
            "total_endpoints_tested": len(hero_endpoints),
            "existing_endpoints": len(existing_endpoints),
            "hero_endpoints_found": existing_endpoints,
            "no_hero_endpoints": len(existing_endpoints) == 0,
            "detailed_results": results
        }
    
    async def test_health_check(self) -> Dict:
        """Test general API health check"""
        print("🏥 Testing API health check...")
        
        result = await self.make_request("/health")
        
        if result["success"]:
            health_data = result["data"]
            
            print(f"  ✅ Health check passed")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            print(f"  📊 Status: {health_data.get('status', 'Unknown')}")
            
            return {
                "test_name": "API Health Check",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "status": health_data.get("status", "Unknown"),
                "app_name": health_data.get("app", "Unknown"),
                "version": health_data.get("version", "Unknown")
            }
        else:
            print(f"  ❌ Health check failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "API Health Check",
                "success": False,
                "error": result.get("error", "Health check failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"]
            }
    
    async def test_marketplace_search(self) -> Dict:
        """Test marketplace search functionality"""
        print("🔍 Testing marketplace search functionality...")
        
        search_tests = [
            {"name": "Empty search", "params": {}},
            {"name": "Text search", "params": {"q": "catalytic"}},
            {"name": "Category search", "params": {"category": "automotive"}},
            {"name": "Price range search", "params": {"price_min": 100, "price_max": 500}}
        ]
        
        results = []
        
        for test in search_tests:
            print(f"  Testing: {test['name']}")
            result = await self.make_request("/marketplace/search", params=test["params"])
            
            if result["success"]:
                search_data = result["data"]
                results_count = len(search_data.get("results", [])) if isinstance(search_data, dict) else len(search_data)
                
                test_result = {
                    "search_name": test["name"],
                    "success": True,
                    "response_time_ms": result["response_time_ms"],
                    "results_count": results_count
                }
                
                print(f"    ✅ {result['response_time_ms']:.0f}ms, {results_count} results")
            else:
                test_result = {
                    "search_name": test["name"],
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "response_time_ms": result["response_time_ms"]
                }
                print(f"    ❌ FAILED - {result.get('error', 'Unknown error')}")
            
            results.append(test_result)
        
        successful_tests = [r for r in results if r["success"]]
        
        return {
            "test_name": "Marketplace Search",
            "total_search_tests": len(search_tests),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(search_tests) * 100,
            "all_searches_working": len(successful_tests) == len(search_tests),
            "detailed_results": results
        }
    
    async def test_performance_consistency(self) -> Dict:
        """Test performance consistency of browse endpoint"""
        print("⚡ Testing browse endpoint performance consistency...")
        
        # Test multiple calls to check consistency
        response_times = []
        
        for i in range(5):
            result = await self.make_request("/marketplace/browse")
            if result["success"]:
                response_times.append(result["response_time_ms"])
                print(f"  Call {i+1}: {result['response_time_ms']:.0f}ms")
            else:
                print(f"  Call {i+1}: FAILED - {result.get('error', 'Unknown error')}")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            
            print(f"  📊 Average: {avg_time:.0f}ms")
            print(f"  📊 Range: {min_time:.0f}ms - {max_time:.0f}ms")
            print(f"  📊 Std Dev: {std_dev:.0f}ms")
            
            return {
                "test_name": "Performance Consistency",
                "success": True,
                "total_calls": len(response_times),
                "avg_response_time_ms": avg_time,
                "min_response_time_ms": min_time,
                "max_response_time_ms": max_time,
                "std_deviation_ms": std_dev,
                "performance_consistent": std_dev < 100,  # Less than 100ms variation
                "all_calls_under_1s": max_time < 1000
            }
        else:
            return {
                "test_name": "Performance Consistency",
                "success": False,
                "error": "All performance test calls failed"
            }
    
    async def run_comprehensive_test(self) -> Dict:
        """Run all browse and hero functionality tests"""
        print("🚀 Starting Browse Page & Hero Functionality Backend Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test suites
            browse_basic = await self.test_browse_endpoint_basic()
            browse_filters = await self.test_browse_endpoint_filters()
            hero_endpoints = await self.test_hero_related_endpoints()
            health_check = await self.test_health_check()
            marketplace_search = await self.test_marketplace_search()
            performance_consistency = await self.test_performance_consistency()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "browse_basic": browse_basic,
                "browse_filters": browse_filters,
                "hero_endpoints": hero_endpoints,
                "health_check": health_check,
                "marketplace_search": marketplace_search,
                "performance_consistency": performance_consistency
            }
            
            # Calculate overall success metrics
            test_results = [
                browse_basic.get("success", False),
                browse_filters.get("all_filters_working", False),
                health_check.get("success", False),
                marketplace_search.get("all_searches_working", False),
                performance_consistency.get("success", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "browse_endpoint_working": browse_basic.get("success", False),
                "browse_filters_working": browse_filters.get("all_filters_working", False),
                "hero_endpoints_found": len(hero_endpoints.get("hero_endpoints_found", [])),
                "api_health_good": health_check.get("success", False),
                "search_functionality_working": marketplace_search.get("all_searches_working", False),
                "performance_consistent": performance_consistency.get("performance_consistent", False),
                "all_tests_passed": overall_success_rate == 100,
                "backend_stable_after_hero_changes": overall_success_rate >= 80
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = BrowseHeroTester()
    results = await tester.run_comprehensive_test()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 BROWSE PAGE & HERO FUNCTIONALITY TEST SUMMARY")
    print("=" * 70)
    
    summary = results["summary"]
    
    print(f"🎯 Overall Success Rate: {summary['overall_success_rate']:.1f}%")
    print()
    
    # Browse functionality
    if summary["browse_endpoint_working"]:
        print("✅ Browse Endpoint: Working")
    else:
        print("❌ Browse Endpoint: Failed")
    
    if summary["browse_filters_working"]:
        print("✅ Browse Filters: All working")
    else:
        print("❌ Browse Filters: Some failed")
    
    # Hero endpoints
    hero_count = summary["hero_endpoints_found"]
    if hero_count > 0:
        print(f"🦸 Hero Endpoints: {hero_count} found")
    else:
        print("⚪ Hero Endpoints: None found (expected)")
    
    # API health
    if summary["api_health_good"]:
        print("✅ API Health: Good")
    else:
        print("❌ API Health: Issues detected")
    
    # Search functionality
    if summary["search_functionality_working"]:
        print("✅ Search Functionality: Working")
    else:
        print("❌ Search Functionality: Issues detected")
    
    # Performance
    if summary["performance_consistent"]:
        print("✅ Performance: Consistent")
    else:
        print("⚠️ Performance: Inconsistent")
    
    print()
    
    # Overall assessment
    if summary["backend_stable_after_hero_changes"]:
        print("🏆 BACKEND STABLE AFTER HERO CHANGES")
        print("   The hero functionality changes did not break backend functionality")
    else:
        print("⚠️ BACKEND ISSUES DETECTED")
        print("   Some backend functionality may have been affected by hero changes")
    
    # Save results
    with open("/app/browse_hero_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Test results saved to: /app/browse_hero_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())