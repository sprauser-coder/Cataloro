#!/usr/bin/env python3
"""
URGENT: Redis Cache Clearing & Data Consistency Testing
Testing cache clearing, phantom listings detection, and data consistency issues
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-repair.preview.emergentagent.com/api"
PERFORMANCE_TARGET_MS = 1000  # Browse endpoint should respond in under 1 second

# Phantom listings to check for (from review request)
PHANTOM_LISTINGS = ["BMW 320d", "Mercedes E-Class", "Audi A4"]

class UrgentCacheAndDataTester:
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
    
    async def test_cache_clearing_functionality(self) -> Dict:
        """Test if there's a cache clearing endpoint or create one"""
        print("🧹 Testing Redis cache clearing functionality...")
        
        cache_tests = []
        
        # Test 1: Check if cache clearing endpoint exists
        print("  Testing cache clearing endpoint...")
        clear_result = await self.make_request("/admin/cache/clear", "POST")
        
        if clear_result["success"]:
            cache_tests.append({
                "test": "Cache Clear Endpoint Exists",
                "success": True,
                "response_time_ms": clear_result["response_time_ms"],
                "message": "Cache clearing endpoint available"
            })
            print("    ✅ Cache clearing endpoint found and working")
        else:
            cache_tests.append({
                "test": "Cache Clear Endpoint Exists", 
                "success": False,
                "status": clear_result["status"],
                "error": clear_result.get("error", "Endpoint not found")
            })
            print(f"    ❌ Cache clearing endpoint not found (status: {clear_result['status']})")
        
        # Test 2: Try alternative cache endpoints
        alternative_endpoints = [
            "/admin/cache/flush",
            "/admin/redis/clear", 
            "/admin/redis/flush",
            "/cache/clear",
            "/cache/flush"
        ]
        
        for endpoint in alternative_endpoints:
            print(f"  Testing alternative endpoint: {endpoint}")
            alt_result = await self.make_request(endpoint, "POST")
            
            if alt_result["success"]:
                cache_tests.append({
                    "test": f"Alternative Cache Clear: {endpoint}",
                    "success": True,
                    "response_time_ms": alt_result["response_time_ms"],
                    "endpoint": endpoint
                })
                print(f"    ✅ Alternative cache endpoint working: {endpoint}")
                break
            else:
                cache_tests.append({
                    "test": f"Alternative Cache Clear: {endpoint}",
                    "success": False,
                    "status": alt_result["status"],
                    "endpoint": endpoint
                })
        
        # Test 3: Check cache status/health
        print("  Testing cache health status...")
        health_result = await self.make_request("/admin/performance")
        
        cache_health = {}
        if health_result["success"]:
            perf_data = health_result["data"]
            cache_info = perf_data.get("cache", {})
            cache_health = {
                "cache_connected": cache_info.get("connected", False),
                "cache_status": cache_info.get("status", "unknown"),
                "cache_type": cache_info.get("type", "unknown")
            }
            
            cache_tests.append({
                "test": "Cache Health Check",
                "success": True,
                "cache_health": cache_health,
                "response_time_ms": health_result["response_time_ms"]
            })
            print(f"    ✅ Cache health: {cache_health}")
        else:
            cache_tests.append({
                "test": "Cache Health Check",
                "success": False,
                "error": health_result.get("error")
            })
            print("    ❌ Could not check cache health")
        
        # Calculate results
        successful_tests = [t for t in cache_tests if t.get("success", False)]
        cache_clear_available = any("Cache Clear" in t.get("test", "") and t.get("success", False) for t in cache_tests)
        
        return {
            "test_name": "Cache Clearing Functionality",
            "total_tests": len(cache_tests),
            "successful_tests": len(successful_tests),
            "cache_clear_endpoint_available": cache_clear_available,
            "cache_health_info": cache_health,
            "detailed_results": cache_tests,
            "recommendation": "Create cache clearing endpoint if not available" if not cache_clear_available else "Cache clearing available"
        }
    
    async def test_browse_endpoint_phantom_listings(self) -> Dict:
        """Test browse endpoint for phantom listings (BMW 320d, Mercedes E-Class, Audi A4)"""
        print("👻 Testing browse endpoint for phantom listings...")
        
        # Test browse endpoint
        browse_result = await self.make_request("/marketplace/browse")
        
        if not browse_result["success"]:
            return {
                "test_name": "Browse Endpoint Phantom Listings",
                "success": False,
                "error": browse_result.get("error"),
                "status": browse_result["status"]
            }
        
        listings = browse_result["data"]
        print(f"  📋 Found {len(listings)} listings in browse endpoint")
        
        # Check for phantom listings
        phantom_found = []
        all_titles = []
        
        for listing in listings:
            title = listing.get("title", "").lower()
            all_titles.append(listing.get("title", ""))
            
            # Check for phantom listings
            for phantom in PHANTOM_LISTINGS:
                if phantom.lower() in title:
                    phantom_found.append({
                        "phantom_title": phantom,
                        "found_title": listing.get("title"),
                        "listing_id": listing.get("id"),
                        "price": listing.get("price"),
                        "seller": listing.get("seller", {}).get("name", "Unknown")
                    })
        
        # Analyze listing data structure
        data_analysis = self.analyze_listing_data_structure(listings)
        
        print(f"  👻 Phantom listings found: {len(phantom_found)}")
        if phantom_found:
            for phantom in phantom_found:
                print(f"    - {phantom['phantom_title']} found as '{phantom['found_title']}' (ID: {phantom['listing_id']})")
        
        return {
            "test_name": "Browse Endpoint Phantom Listings",
            "success": True,
            "response_time_ms": browse_result["response_time_ms"],
            "total_listings": len(listings),
            "phantom_listings_found": len(phantom_found),
            "phantom_details": phantom_found,
            "all_listing_titles": all_titles[:10],  # First 10 titles for inspection
            "data_structure_analysis": data_analysis,
            "has_phantom_data": len(phantom_found) > 0
        }
    
    async def test_listings_endpoint_comparison(self) -> Dict:
        """Test /api/listings endpoint and compare with browse endpoint"""
        print("📊 Testing listings endpoint and comparing with browse...")
        
        # Test listings endpoint
        listings_result = await self.make_request("/listings")
        
        if not listings_result["success"]:
            return {
                "test_name": "Listings Endpoint Comparison",
                "success": False,
                "error": f"Listings endpoint failed: {listings_result.get('error')}",
                "status": listings_result["status"]
            }
        
        # Test browse endpoint for comparison
        browse_result = await self.make_request("/marketplace/browse")
        
        if not browse_result["success"]:
            return {
                "test_name": "Listings Endpoint Comparison", 
                "success": False,
                "error": f"Browse endpoint failed: {browse_result.get('error')}",
                "status": browse_result["status"]
            }
        
        listings_data = listings_result["data"]
        browse_data = browse_result["data"]
        
        print(f"  📋 Listings endpoint: {len(listings_data)} items")
        print(f"  🔍 Browse endpoint: {len(browse_data)} items")
        
        # Compare data
        comparison = self.compare_endpoint_data(listings_data, browse_data)
        
        # Check for phantom listings in both endpoints
        listings_phantoms = self.find_phantom_listings(listings_data)
        browse_phantoms = self.find_phantom_listings(browse_data)
        
        return {
            "test_name": "Listings Endpoint Comparison",
            "success": True,
            "listings_endpoint": {
                "count": len(listings_data),
                "response_time_ms": listings_result["response_time_ms"],
                "phantom_listings": listings_phantoms
            },
            "browse_endpoint": {
                "count": len(browse_data),
                "response_time_ms": browse_result["response_time_ms"],
                "phantom_listings": browse_phantoms
            },
            "comparison": comparison,
            "data_consistency_issue": comparison["count_mismatch"] or comparison["phantom_mismatch"]
        }
    
    async def test_performance_measurements(self) -> Dict:
        """Measure response times of both endpoints"""
        print("⏱️ Testing performance of browse and listings endpoints...")
        
        # Test browse endpoint multiple times
        browse_times = []
        for i in range(5):
            result = await self.make_request("/marketplace/browse")
            if result["success"]:
                browse_times.append(result["response_time_ms"])
        
        # Test listings endpoint multiple times  
        listings_times = []
        for i in range(5):
            result = await self.make_request("/listings")
            if result["success"]:
                listings_times.append(result["response_time_ms"])
        
        # Calculate statistics
        browse_stats = {
            "avg_ms": statistics.mean(browse_times) if browse_times else 0,
            "min_ms": min(browse_times) if browse_times else 0,
            "max_ms": max(browse_times) if browse_times else 0,
            "successful_calls": len(browse_times)
        }
        
        listings_stats = {
            "avg_ms": statistics.mean(listings_times) if listings_times else 0,
            "min_ms": min(listings_times) if listings_times else 0,
            "max_ms": max(listings_times) if listings_times else 0,
            "successful_calls": len(listings_times)
        }
        
        print(f"  🔍 Browse endpoint: {browse_stats['avg_ms']:.0f}ms avg ({browse_stats['successful_calls']}/5 successful)")
        print(f"  📋 Listings endpoint: {listings_stats['avg_ms']:.0f}ms avg ({listings_stats['successful_calls']}/5 successful)")
        
        return {
            "test_name": "Performance Measurements",
            "browse_performance": browse_stats,
            "listings_performance": listings_stats,
            "browse_meets_target": browse_stats["avg_ms"] < PERFORMANCE_TARGET_MS,
            "listings_meets_target": listings_stats["avg_ms"] < PERFORMANCE_TARGET_MS,
            "performance_issue_detected": browse_stats["avg_ms"] > PERFORMANCE_TARGET_MS or listings_stats["avg_ms"] > PERFORMANCE_TARGET_MS
        }
    
    async def test_ai_recommendation_service_errors(self) -> Dict:
        """Check for AI recommendation service errors, specifically _get_similarity_reasons method"""
        print("🤖 Testing AI recommendation service for errors...")
        
        # Check backend logs for AI service errors
        error_tests = []
        
        # Test 1: Check if AI recommendation service is initialized
        print("  Testing AI recommendation service initialization...")
        health_result = await self.make_request("/admin/performance")
        
        ai_service_status = "unknown"
        if health_result["success"]:
            perf_data = health_result["data"]
            phase5_services = perf_data.get("phase5_services", {})
            ai_service_status = phase5_services.get("ai_recommendations", "unknown")
            
            error_tests.append({
                "test": "AI Service Status Check",
                "success": True,
                "ai_service_enabled": ai_service_status == "enabled",
                "status": ai_service_status
            })
            print(f"    ✅ AI service status: {ai_service_status}")
        else:
            error_tests.append({
                "test": "AI Service Status Check",
                "success": False,
                "error": "Could not check AI service status"
            })
        
        # Test 2: Try to trigger AI recommendation functionality
        print("  Testing AI recommendation functionality...")
        
        # Try to get similar listings (this might trigger the AI service)
        similar_result = await self.make_request("/marketplace/listings/test-listing-id/similar")
        
        if similar_result["success"]:
            error_tests.append({
                "test": "AI Similarity Function",
                "success": True,
                "response_time_ms": similar_result["response_time_ms"],
                "has_recommendations": len(similar_result.get("data", {}).get("similar_listings", [])) > 0
            })
            print("    ✅ AI similarity function working")
        else:
            error_tests.append({
                "test": "AI Similarity Function",
                "success": False,
                "status": similar_result["status"],
                "error": similar_result.get("error", "Unknown error")
            })
            print(f"    ❌ AI similarity function failed: {similar_result.get('error')}")
        
        # Test 3: Check for specific _get_similarity_reasons error
        # This would typically be found in backend logs, but we can test indirectly
        print("  Testing for _get_similarity_reasons method availability...")
        
        # Try multiple listing IDs to see if we can trigger the error
        test_listing_ids = ["test-1", "test-2", "nonexistent-listing"]
        similarity_errors = []
        
        for listing_id in test_listing_ids:
            result = await self.make_request(f"/marketplace/listings/{listing_id}/similar")
            if not result["success"] and "similarity" in str(result.get("error", "")).lower():
                similarity_errors.append({
                    "listing_id": listing_id,
                    "error": result.get("error"),
                    "status": result["status"]
                })
        
        error_tests.append({
            "test": "Similarity Reasons Method Check",
            "success": len(similarity_errors) == 0,
            "similarity_errors_found": len(similarity_errors),
            "error_details": similarity_errors
        })
        
        if similarity_errors:
            print(f"    ⚠️ Found {len(similarity_errors)} similarity-related errors")
        else:
            print("    ✅ No similarity method errors detected")
        
        return {
            "test_name": "AI Recommendation Service Errors",
            "ai_service_enabled": ai_service_status == "enabled",
            "total_tests": len(error_tests),
            "successful_tests": len([t for t in error_tests if t.get("success", False)]),
            "similarity_method_errors": len(similarity_errors),
            "missing_get_similarity_reasons": len(similarity_errors) > 0,
            "detailed_results": error_tests,
            "recommendation": "Check AI service implementation for _get_similarity_reasons method" if similarity_errors else "AI service appears functional"
        }
    
    def analyze_listing_data_structure(self, listings: List[Dict]) -> Dict:
        """Analyze the structure of listing data"""
        if not listings:
            return {"empty_data": True}
        
        # Analyze first listing structure
        sample_listing = listings[0]
        
        structure_analysis = {
            "has_id": "id" in sample_listing,
            "has_title": "title" in sample_listing,
            "has_price": "price" in sample_listing,
            "has_seller_info": "seller" in sample_listing,
            "has_bid_info": "bid_info" in sample_listing,
            "has_time_info": "time_info" in sample_listing,
            "seller_structure": list(sample_listing.get("seller", {}).keys()) if "seller" in sample_listing else [],
            "total_fields": len(sample_listing.keys()),
            "all_fields": list(sample_listing.keys())
        }
        
        return structure_analysis
    
    def find_phantom_listings(self, listings: List[Dict]) -> List[Dict]:
        """Find phantom listings in a dataset"""
        phantoms = []
        
        for listing in listings:
            title = listing.get("title", "").lower()
            for phantom in PHANTOM_LISTINGS:
                if phantom.lower() in title:
                    phantoms.append({
                        "phantom_type": phantom,
                        "found_title": listing.get("title"),
                        "listing_id": listing.get("id"),
                        "price": listing.get("price")
                    })
        
        return phantoms
    
    def compare_endpoint_data(self, listings_data: List[Dict], browse_data: List[Dict]) -> Dict:
        """Compare data between listings and browse endpoints"""
        
        # Count comparison
        count_mismatch = len(listings_data) != len(browse_data)
        
        # Phantom comparison
        listings_phantoms = self.find_phantom_listings(listings_data)
        browse_phantoms = self.find_phantom_listings(browse_data)
        phantom_mismatch = len(listings_phantoms) != len(browse_phantoms)
        
        # ID comparison (if both have data)
        id_overlap = 0
        if listings_data and browse_data:
            listings_ids = set(item.get("id") for item in listings_data if item.get("id"))
            browse_ids = set(item.get("id") for item in browse_data if item.get("id"))
            id_overlap = len(listings_ids.intersection(browse_ids))
        
        return {
            "count_mismatch": count_mismatch,
            "listings_count": len(listings_data),
            "browse_count": len(browse_data),
            "phantom_mismatch": phantom_mismatch,
            "listings_phantoms": len(listings_phantoms),
            "browse_phantoms": len(browse_phantoms),
            "id_overlap": id_overlap,
            "data_consistency_score": 100 - (count_mismatch * 50 + phantom_mismatch * 50)
        }
    
    async def run_urgent_cache_and_data_tests(self) -> Dict:
        """Run all urgent cache and data consistency tests"""
        print("🚨 URGENT: Starting Redis Cache & Data Consistency Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all urgent tests
            cache_clearing = await self.test_cache_clearing_functionality()
            phantom_listings = await self.test_browse_endpoint_phantom_listings()
            endpoint_comparison = await self.test_listings_endpoint_comparison()
            performance = await self.test_performance_measurements()
            ai_errors = await self.test_ai_recommendation_service_errors()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "urgent_priority": "HIGH",
                "cache_clearing_test": cache_clearing,
                "phantom_listings_test": phantom_listings,
                "endpoint_comparison_test": endpoint_comparison,
                "performance_test": performance,
                "ai_service_errors_test": ai_errors
            }
            
            # Calculate critical issues
            critical_issues = []
            
            if not cache_clearing.get("cache_clear_endpoint_available", False):
                critical_issues.append("No cache clearing endpoint available")
            
            if phantom_listings.get("has_phantom_data", False):
                critical_issues.append(f"Phantom listings detected: {phantom_listings.get('phantom_listings_found', 0)} found")
            
            if endpoint_comparison.get("data_consistency_issue", False):
                critical_issues.append("Data inconsistency between browse and listings endpoints")
            
            if performance.get("performance_issue_detected", False):
                critical_issues.append("Performance issues detected (>1000ms response times)")
            
            if ai_errors.get("missing_get_similarity_reasons", False):
                critical_issues.append("AI recommendation service _get_similarity_reasons method missing")
            
            all_results["summary"] = {
                "total_critical_issues": len(critical_issues),
                "critical_issues": critical_issues,
                "cache_clearing_available": cache_clearing.get("cache_clear_endpoint_available", False),
                "phantom_data_detected": phantom_listings.get("has_phantom_data", False),
                "data_consistency_ok": not endpoint_comparison.get("data_consistency_issue", True),
                "performance_acceptable": not performance.get("performance_issue_detected", True),
                "ai_service_functional": not ai_errors.get("missing_get_similarity_reasons", True),
                "urgent_action_required": len(critical_issues) > 0
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main function to run urgent tests"""
    tester = UrgentCacheAndDataTester()
    results = await tester.run_urgent_cache_and_data_tests()
    
    print("\n" + "=" * 70)
    print("🚨 URGENT TEST RESULTS SUMMARY")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"📊 Total Critical Issues: {summary.get('total_critical_issues', 0)}")
    print(f"🧹 Cache Clearing Available: {'✅' if summary.get('cache_clearing_available', False) else '❌'}")
    print(f"👻 Phantom Data Detected: {'❌' if summary.get('phantom_data_detected', False) else '✅'}")
    print(f"📊 Data Consistency OK: {'✅' if summary.get('data_consistency_ok', False) else '❌'}")
    print(f"⏱️ Performance Acceptable: {'✅' if summary.get('performance_acceptable', False) else '❌'}")
    print(f"🤖 AI Service Functional: {'✅' if summary.get('ai_service_functional', False) else '❌'}")
    
    if summary.get("critical_issues"):
        print("\n🚨 CRITICAL ISSUES FOUND:")
        for issue in summary.get("critical_issues", []):
            print(f"  - {issue}")
    
    if summary.get("urgent_action_required", False):
        print("\n⚠️ URGENT ACTION REQUIRED!")
    else:
        print("\n✅ All urgent tests passed!")
    
    # Print detailed results as JSON for debugging
    print(f"\n📋 Full Results JSON:")
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())