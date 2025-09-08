#!/usr/bin/env python3
"""
Cataloro Marketplace - Focused Backend Stress Test
Tests key backend endpoints with moderate load to evaluate performance
"""

import asyncio
import aiohttp
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any
import statistics

# Backend URL from environment
BACKEND_URL = "https://marketplace-central.preview.emergentagent.com/api"

class FocusedStressTester:
    def __init__(self):
        self.session = None
        self.results = []
        self.response_times = {
            "browse": [],
            "search": [],
            "currency": [],
            "webhooks": [],
            "analytics": []
        }
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(ssl=False, limit=100)
        )
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request with timing"""
        url = f"{BACKEND_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    response_time = time.time() - start_time
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "success": response.status < 400,
                        "response_time": response_time
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, params=params) as response:
                    response_time = time.time() - start_time
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "success": response.status < 400,
                        "response_time": response_time
                    }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "status": 500,
                "data": {"error": str(e)},
                "success": False,
                "response_time": response_time
            }
    
    def log_result(self, test_name: str, success: bool, response_time: float, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "response_time": response_time,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {response_time*1000:.2f}ms - {details}")
    
    async def test_browse_pagination_performance(self):
        """Test browse endpoint with new pagination (40 items per page)"""
        print("\n📋 Testing Browse Pagination Performance...")
        
        test_scenarios = [
            {"page": 1, "limit": 40, "type": "all"},
            {"page": 2, "limit": 40, "type": "Private"},
            {"page": 3, "limit": 40, "type": "Business"},
            {"page": 1, "limit": 40, "bid_status": "highest_bidder"},
            {"page": 1, "limit": 40, "bid_status": "not_bid_yet"},
        ]
        
        for scenario in test_scenarios:
            response = await self.make_request("GET", "/marketplace/browse", params=scenario)
            
            if response["success"]:
                data = response["data"]
                listings = data.get("listings", [])
                pagination = data.get("pagination", {})
                
                details = f"Page {scenario['page']}: {len(listings)} listings, {pagination.get('total_items', 0)} total"
                self.response_times["browse"].append(response["response_time"])
                self.log_result("Browse Pagination", True, response["response_time"], details)
                
                # Verify 40 items per page limit
                if pagination.get("items_per_page") != 40:
                    self.log_result("Pagination Limit Check", False, 0, f"Expected 40, got {pagination.get('items_per_page')}")
                else:
                    self.log_result("Pagination Limit Check", True, 0, "40 items per page confirmed")
            else:
                self.log_result("Browse Pagination", False, response["response_time"], f"Status: {response['status']}")
    
    async def test_search_performance(self):
        """Test search endpoint performance"""
        print("\n🔍 Testing Search Performance...")
        
        search_queries = [
            {"q": "automotive", "category": "Automotive"},
            {"q": "electronics", "sort_by": "price_low"},
            {"q": "premium", "price_min": 100, "price_max": 1000},
            {"q": "", "category": "Fashion", "condition": "New"},
        ]
        
        for query in search_queries:
            response = await self.make_request("GET", "/marketplace/search", params=query)
            
            if response["success"]:
                data = response["data"]
                results = data.get("results", [])
                total = data.get("total", 0)
                
                details = f"Query '{query.get('q', 'empty')}': {len(results)} results, {total} total"
                self.response_times["search"].append(response["response_time"])
                self.log_result("Search Performance", True, response["response_time"], details)
            else:
                self.log_result("Search Performance", False, response["response_time"], f"Status: {response['status']}")
    
    async def test_currency_conversion_performance(self):
        """Test currency conversion performance"""
        print("\n💱 Testing Currency Conversion Performance...")
        
        # Test supported currencies
        response = await self.make_request("GET", "/v2/advanced/currency/supported")
        if response["success"]:
            currencies_data = response["data"]
            currencies = currencies_data.get("currencies", [])
            currency_codes = [c.get("code") for c in currencies if c.get("code")]
            
            self.response_times["currency"].append(response["response_time"])
            self.log_result("Supported Currencies", True, response["response_time"], f"Found {len(currencies)} currencies")
            
            # Test exchange rates
            rates_response = await self.make_request("GET", "/v2/advanced/currency/rates")
            if rates_response["success"]:
                self.response_times["currency"].append(rates_response["response_time"])
                self.log_result("Exchange Rates", True, rates_response["response_time"], "Rates retrieved")
                
                # Test currency conversions
                conversion_tests = [
                    {"amount": 100, "from_currency": "EUR", "to_currency": "USD"},
                    {"amount": 250, "from_currency": "USD", "to_currency": "GBP"},
                    {"amount": 500, "from_currency": "GBP", "to_currency": "CHF"},
                ]
                
                for conversion in conversion_tests:
                    conv_response = await self.make_request("POST", "/v2/advanced/currency/convert", data=conversion)
                    
                    if conv_response["success"]:
                        conv_data = conv_response["data"]
                        conversion_result = conv_data.get("conversion", {})
                        converted_amount = conversion_result.get("converted_amount", 0)
                        
                        details = f"{conversion['amount']} {conversion['from_currency']} → {converted_amount} {conversion['to_currency']}"
                        self.response_times["currency"].append(conv_response["response_time"])
                        self.log_result("Currency Conversion", True, conv_response["response_time"], details)
                    else:
                        self.log_result("Currency Conversion", False, conv_response["response_time"], f"Status: {conv_response['status']}")
            else:
                self.log_result("Exchange Rates", False, rates_response["response_time"], f"Status: {rates_response['status']}")
        else:
            self.log_result("Supported Currencies", False, response["response_time"], f"Status: {response['status']}")
    
    async def test_webhook_performance(self):
        """Test webhook system performance"""
        print("\n🔗 Testing Webhook Performance...")
        
        # Test webhook endpoints
        webhook_tests = [
            {"endpoint": "/v2/advanced/webhooks", "method": "GET", "name": "List Webhooks"},
            {"endpoint": "/v2/advanced/webhook-events", "method": "GET", "name": "Webhook Events"},
        ]
        
        for test in webhook_tests:
            response = await self.make_request(test["method"], test["endpoint"])
            
            if response["success"]:
                data = response["data"]
                
                if test["name"] == "List Webhooks":
                    webhooks = data.get("webhooks", [])
                    details = f"Found {len(webhooks)} webhooks"
                elif test["name"] == "Webhook Events":
                    events = data.get("events", [])
                    details = f"Found {len(events)} webhook events"
                else:
                    details = "Success"
                
                self.response_times["webhooks"].append(response["response_time"])
                self.log_result(test["name"], True, response["response_time"], details)
            else:
                self.log_result(test["name"], False, response["response_time"], f"Status: {response['status']}")
    
    async def test_analytics_performance(self):
        """Test analytics endpoints performance"""
        print("\n📊 Testing Analytics Performance...")
        
        analytics_tests = [
            {"endpoint": "/v2/advanced/analytics/dashboard", "name": "Analytics Dashboard"},
            {"endpoint": "/v2/advanced/analytics/user", "params": {"days": 30}, "name": "User Analytics"},
            {"endpoint": "/v2/advanced/analytics/sales", "params": {"days": 30}, "name": "Sales Analytics"},
            {"endpoint": "/v2/advanced/analytics/marketplace", "params": {"days": 30}, "name": "Marketplace Analytics"},
        ]
        
        for test in analytics_tests:
            response = await self.make_request("GET", test["endpoint"], params=test.get("params"))
            
            if response["success"]:
                data = response["data"]
                
                if test["name"] == "Analytics Dashboard":
                    dashboard = data.get("dashboard_data", {})
                    overview = dashboard.get("overview", {})
                    details = f"Users: {overview.get('total_users', 0)}, Revenue: €{overview.get('total_revenue', 0)}"
                elif "Analytics" in test["name"]:
                    analytics = data.get("analytics", {})
                    summary = analytics.get("summary", {})
                    details = f"Analytics data retrieved: {len(summary)} metrics"
                else:
                    details = "Success"
                
                self.response_times["analytics"].append(response["response_time"])
                self.log_result(test["name"], True, response["response_time"], details)
            else:
                self.log_result(test["name"], False, response["response_time"], f"Status: {response['status']}")
    
    async def test_concurrent_load(self, concurrent_requests: int = 50):
        """Test concurrent load on key endpoints"""
        print(f"\n⚡ Testing Concurrent Load ({concurrent_requests} requests)...")
        
        async def concurrent_browse_request():
            params = {
                "page": random.randint(1, 5),
                "limit": 40,
                "type": random.choice(["all", "Private", "Business"])
            }
            return await self.make_request("GET", "/marketplace/browse", params=params)
        
        # Run concurrent requests
        start_time = time.time()
        tasks = [concurrent_browse_request() for _ in range(concurrent_requests)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Analyze results
        successful_responses = [r for r in responses if isinstance(r, dict) and r.get("success")]
        failed_responses = [r for r in responses if not (isinstance(r, dict) and r.get("success"))]
        
        if successful_responses:
            response_times = [r["response_time"] for r in successful_responses]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            details = f"Success: {len(successful_responses)}/{concurrent_requests}, Avg: {avg_response_time*1000:.2f}ms, Max: {max_response_time*1000:.2f}ms"
            self.log_result("Concurrent Load Test", True, avg_response_time, details)
            
            # Calculate requests per second
            rps = concurrent_requests / total_time
            self.log_result("Requests Per Second", True, 0, f"{rps:.2f} RPS")
        else:
            self.log_result("Concurrent Load Test", False, 0, f"All {concurrent_requests} requests failed")
    
    async def run_focused_stress_test(self):
        """Run the focused stress test"""
        print("🚀 Starting Focused Backend Stress Test")
        print(f"📡 Target: {BACKEND_URL}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all performance tests
        await self.test_browse_pagination_performance()
        await self.test_search_performance()
        await self.test_currency_conversion_performance()
        await self.test_webhook_performance()
        await self.test_analytics_performance()
        await self.test_concurrent_load(50)  # 50 concurrent requests
        
        total_time = time.time() - start_time
        
        # Print summary
        self.print_summary(total_time)
    
    def print_summary(self, total_time: float):
        """Print test summary with performance metrics"""
        print("\n" + "=" * 80)
        print("📊 FOCUSED STRESS TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"   Total Duration: {total_time:.2f} seconds")
        
        # Performance metrics by category
        print(f"\n⚡ PERFORMANCE METRICS:")
        
        for category, times in self.response_times.items():
            if times:
                avg_time = statistics.mean(times) * 1000
                max_time = max(times) * 1000
                min_time = min(times) * 1000
                
                print(f"   {category.upper()}:")
                print(f"      Average: {avg_time:.2f}ms")
                print(f"      Min: {min_time:.2f}ms")
                print(f"      Max: {max_time:.2f}ms")
                print(f"      Requests: {len(times)}")
        
        # Performance benchmarks
        print(f"\n🎯 PERFORMANCE BENCHMARKS:")
        
        browse_times = self.response_times.get("browse", [])
        if browse_times:
            avg_browse = statistics.mean(browse_times) * 1000
            print(f"   Browse API (<500ms): {avg_browse:.2f}ms {'✅' if avg_browse < 500 else '❌'}")
        
        search_times = self.response_times.get("search", [])
        if search_times:
            avg_search = statistics.mean(search_times) * 1000
            print(f"   Search API (<500ms): {avg_search:.2f}ms {'✅' if avg_search < 500 else '❌'}")
        
        currency_times = self.response_times.get("currency", [])
        if currency_times:
            avg_currency = statistics.mean(currency_times) * 1000
            print(f"   Currency API (<2000ms): {avg_currency:.2f}ms {'✅' if avg_currency < 2000 else '❌'}")
        
        # Failed tests
        failed_results = [r for r in self.results if not r["success"]]
        if failed_results:
            print(f"\n❌ FAILED TESTS:")
            for result in failed_results:
                print(f"   • {result['test']}: {result['details']}")
        
        # Overall assessment
        print(f"\n🏆 OVERALL ASSESSMENT:")
        if failed_tests == 0 and browse_times and statistics.mean(browse_times) * 1000 < 500:
            print("   🎉 EXCELLENT: All tests passed with good performance!")
        elif failed_tests <= 2:
            print("   ✅ GOOD: Most tests passed with acceptable performance")
        elif failed_tests <= 5:
            print("   ⚠️ ACCEPTABLE: Some issues detected, optimization recommended")
        else:
            print("   ❌ POOR: Multiple failures detected, investigation required")
        
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = FocusedStressTester()
    
    try:
        await tester.setup()
        await tester.run_focused_stress_test()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())