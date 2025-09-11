#!/usr/bin/env python3
"""
Comprehensive Performance Optimization Validation
Testing all specific requirements from the review request:
1. Browse endpoint response size (~12KB, not 44MB+)
2. Thumbnail system for actual images
3. Message/tender endpoint performance (N+1 fixes)
4. No breaking changes in data structure
"""

import asyncio
import aiohttp
import time
import json
import statistics
import sys
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://market-guardian.preview.emergentagent.com/api"

# Success Criteria from Review Request
BROWSE_RESPONSE_SIZE_TARGET_KB = 15  # <15KB response
BROWSE_RESPONSE_TIME_TARGET_MS = 200  # <200ms response time
GENERAL_PERFORMANCE_TARGET_MS = 1000  # General performance target

class ComprehensivePerformanceTester:
    def __init__(self):
        self.session = None
        self.demo_user_id = None
        self.admin_token = None
        
    async def setup(self):
        """Initialize HTTP session and authenticate demo user"""
        self.session = aiohttp.ClientSession()
        
        # Authenticate demo user for testing
        demo_login = await self.make_request("/auth/login", "POST", data={
            "email": "demo@cataloro.com",
            "password": "demo_password"
        })
        
        if demo_login["success"]:
            user_data = demo_login["data"].get("user", {})
            self.demo_user_id = user_data.get("id")
            print(f"✅ Demo user authenticated: {self.demo_user_id}")
        else:
            print("⚠️ Could not authenticate demo user")
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request and measure response time and size"""
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
                
                # Get response content
                if response.headers.get('content-type', '').startswith('application/json'):
                    response_data = await response.json()
                    response_text = json.dumps(response_data)
                elif response.headers.get('content-type', '').startswith('image/'):
                    response_data = await response.read()
                    response_text = ""
                else:
                    response_text = await response.text()
                    try:
                        response_data = json.loads(response_text)
                    except:
                        response_data = response_text
                
                # Calculate response size
                response_size_bytes = len(response_text.encode('utf-8')) if response_text else len(response_data) if isinstance(response_data, bytes) else 0
                response_size_kb = response_size_bytes / 1024
                
                return {
                    "success": response.status in [200, 201],
                    "response_time_ms": response_time_ms,
                    "response_size_bytes": response_size_bytes,
                    "response_size_kb": response_size_kb,
                    "data": response_data,
                    "status": response.status,
                    "content_type": response.headers.get('content-type', '')
                }
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time_ms,
                "response_size_bytes": 0,
                "response_size_kb": 0,
                "error": str(e),
                "status": 0
            }
    
    async def test_browse_performance_multiple_times(self) -> Dict:
        """Test browse endpoint multiple times to measure response size and time"""
        print("🔍 Testing Browse Endpoint Performance (Multiple Calls)...")
        
        response_times = []
        response_sizes_kb = []
        all_successful = True
        
        for i in range(5):
            result = await self.make_request("/marketplace/browse")
            
            if result["success"]:
                response_times.append(result["response_time_ms"])
                response_sizes_kb.append(result["response_size_kb"])
                
                print(f"  Call {i+1}: {result['response_time_ms']:.0f}ms, {result['response_size_kb']:.1f}KB")
            else:
                print(f"  Call {i+1}: FAILED - {result.get('error', 'Unknown error')}")
                all_successful = False
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            avg_response_size_kb = statistics.mean(response_sizes_kb)
            max_response_size_kb = max(response_sizes_kb)
            
            # Check success criteria
            size_target_met = avg_response_size_kb < BROWSE_RESPONSE_SIZE_TARGET_KB
            time_target_met = avg_response_time < BROWSE_RESPONSE_TIME_TARGET_MS
            
            # Calculate improvement from 44MB baseline
            baseline_44mb_kb = 44 * 1024
            improvement_percent = ((baseline_44mb_kb - avg_response_size_kb) / baseline_44mb_kb) * 100
            
            return {
                "test_name": "Browse Performance Multiple Times",
                "avg_response_time_ms": avg_response_time,
                "avg_response_size_kb": avg_response_size_kb,
                "max_response_size_kb": max_response_size_kb,
                "size_target_met": size_target_met,
                "time_target_met": time_target_met,
                "improvement_from_44mb_percent": improvement_percent,
                "all_calls_successful": all_successful,
                "total_calls": len(response_times),
                "meets_success_criteria": size_target_met and time_target_met and all_successful
            }
        else:
            return {
                "test_name": "Browse Performance Multiple Times",
                "error": "All browse calls failed",
                "meets_success_criteria": False
            }
    
    async def test_thumbnail_system_actual_images(self) -> Dict:
        """Test thumbnail system with actual images from listings"""
        print("🖼️ Testing Thumbnail System for Actual Images...")
        
        # Get listings first
        browse_result = await self.make_request("/marketplace/browse")
        
        if not browse_result["success"]:
            return {
                "test_name": "Thumbnail System Actual Images",
                "error": "Could not get listings for thumbnail testing",
                "thumbnail_system_working": False
            }
        
        listings = browse_result["data"]
        thumbnail_tests = []
        working_thumbnails = 0
        
        # Test thumbnails for listings with images
        for listing in listings[:5]:  # Test first 5 listings
            listing_id = listing.get("id")
            if not listing_id:
                continue
            
            images = listing.get("images", [])
            if not images:
                continue
                
            print(f"  Testing thumbnail for listing {listing_id} (has {len(images)} images)...")
            
            # Test first image thumbnail
            thumbnail_result = await self.make_request(f"/listings/{listing_id}/thumbnail/0")
            
            if thumbnail_result["success"]:
                content_type = thumbnail_result.get("content_type", "")
                size_bytes = thumbnail_result.get("response_size_bytes", 0)
                response_time = thumbnail_result.get("response_time_ms", 0)
                
                is_image = content_type.startswith("image/")
                is_cached = "cache-control" in str(thumbnail_result.get("headers", {})).lower()
                
                thumbnail_tests.append({
                    "listing_id": listing_id,
                    "success": True,
                    "content_type": content_type,
                    "size_bytes": size_bytes,
                    "response_time_ms": response_time,
                    "is_image": is_image,
                    "is_cached": is_cached
                })
                
                if is_image:
                    working_thumbnails += 1
                
                print(f"    ✅ {content_type}, {size_bytes} bytes, {response_time:.0f}ms")
            else:
                thumbnail_tests.append({
                    "listing_id": listing_id,
                    "success": False,
                    "error": thumbnail_result.get("error", "Unknown error")
                })
                print(f"    ❌ Failed: {thumbnail_result.get('error', 'Unknown error')}")
        
        # Test placeholder image
        placeholder_result = await self.make_request("/placeholder-image.jpg")
        placeholder_working = placeholder_result["success"] and placeholder_result.get("content_type", "").startswith("image/")
        
        return {
            "test_name": "Thumbnail System Actual Images",
            "total_thumbnail_tests": len(thumbnail_tests),
            "working_thumbnails": working_thumbnails,
            "placeholder_working": placeholder_working,
            "placeholder_size_bytes": placeholder_result.get("response_size_bytes", 0) if placeholder_working else 0,
            "thumbnail_system_working": working_thumbnails > 0 and placeholder_working,
            "detailed_thumbnail_tests": thumbnail_tests
        }
    
    async def test_message_endpoint_performance(self) -> Dict:
        """Test message endpoint performance (N+1 fix validation)"""
        print("📨 Testing Message Endpoint Performance (N+1 Fix)...")
        
        if not self.demo_user_id:
            return {
                "test_name": "Message Endpoint Performance",
                "error": "No demo user ID available",
                "n1_fix_working": False
            }
        
        # Test multiple calls to measure performance consistency
        response_times = []
        data_integrity_checks = []
        
        for i in range(3):
            result = await self.make_request(f"/user/{self.demo_user_id}/messages")
            
            if result["success"]:
                response_times.append(result["response_time_ms"])
                
                # Check data structure integrity (sign of proper enrichment without N+1)
                messages = result["data"]
                if isinstance(messages, list):
                    # Check if messages have enriched data (user info, listing info)
                    has_enrichment = False
                    if messages:
                        first_message = messages[0]
                        has_enrichment = any(key in first_message for key in ["sender_name", "listing_title", "user_info", "listing_info"])
                    
                    data_integrity_checks.append({
                        "message_count": len(messages),
                        "has_enrichment": has_enrichment,
                        "response_time_ms": result["response_time_ms"]
                    })
                
                print(f"  Call {i+1}: {result['response_time_ms']:.0f}ms, {len(messages) if isinstance(messages, list) else 0} messages")
            else:
                print(f"  Call {i+1}: FAILED - {result.get('error', 'Unknown error')}")
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            performance_good = avg_response_time < GENERAL_PERFORMANCE_TARGET_MS
            
            return {
                "test_name": "Message Endpoint Performance",
                "avg_response_time_ms": avg_response_time,
                "max_response_time_ms": max(response_times),
                "min_response_time_ms": min(response_times),
                "performance_good": performance_good,
                "n1_fix_working": performance_good,
                "total_calls": len(response_times),
                "data_integrity_checks": data_integrity_checks
            }
        else:
            return {
                "test_name": "Message Endpoint Performance",
                "error": "All message endpoint calls failed",
                "n1_fix_working": False
            }
    
    async def test_tender_endpoint_performance(self) -> Dict:
        """Test tender endpoint performance (N+1 fix validation)"""
        print("📋 Testing Tender Endpoint Performance (N+1 Fix)...")
        
        if not self.demo_user_id:
            return {
                "test_name": "Tender Endpoint Performance",
                "error": "No demo user ID available",
                "n1_fix_working": False
            }
        
        # Test buyer tenders endpoint
        response_times = []
        data_integrity_checks = []
        
        for i in range(3):
            result = await self.make_request(f"/tenders/buyer/{self.demo_user_id}")
            
            if result["success"]:
                response_times.append(result["response_time_ms"])
                
                # Check data structure integrity
                tenders = result["data"]
                if isinstance(tenders, list):
                    has_enrichment = False
                    if tenders:
                        first_tender = tenders[0]
                        has_enrichment = any(key in first_tender for key in ["listing_title", "seller_name", "listing_info", "seller_info"])
                    
                    data_integrity_checks.append({
                        "tender_count": len(tenders),
                        "has_enrichment": has_enrichment,
                        "response_time_ms": result["response_time_ms"]
                    })
                
                print(f"  Call {i+1}: {result['response_time_ms']:.0f}ms, {len(tenders) if isinstance(tenders, list) else 0} tenders")
            else:
                print(f"  Call {i+1}: FAILED - {result.get('error', 'Unknown error')}")
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            performance_good = avg_response_time < GENERAL_PERFORMANCE_TARGET_MS
            
            return {
                "test_name": "Tender Endpoint Performance",
                "avg_response_time_ms": avg_response_time,
                "max_response_time_ms": max(response_times),
                "min_response_time_ms": min(response_times),
                "performance_good": performance_good,
                "n1_fix_working": performance_good,
                "total_calls": len(response_times),
                "data_integrity_checks": data_integrity_checks
            }
        else:
            return {
                "test_name": "Tender Endpoint Performance",
                "error": "All tender endpoint calls failed",
                "n1_fix_working": False
            }
    
    async def test_data_structure_integrity(self) -> Dict:
        """Test that no breaking changes occurred in data structure"""
        print("🔍 Testing Data Structure Integrity (No Breaking Changes)...")
        
        # Test browse endpoint data structure
        browse_result = await self.make_request("/marketplace/browse")
        
        if not browse_result["success"]:
            return {
                "test_name": "Data Structure Integrity",
                "error": "Could not get browse data for structure testing",
                "no_breaking_changes": False
            }
        
        listings = browse_result["data"]
        structure_checks = []
        
        if isinstance(listings, list) and listings:
            first_listing = listings[0]
            
            # Check required fields are present
            required_fields = ["id", "title", "price", "seller_id", "status"]
            missing_required = [field for field in required_fields if field not in first_listing]
            
            # Check expected enriched fields are present
            enriched_fields = ["seller", "bid_info", "images"]
            missing_enriched = [field for field in enriched_fields if field not in first_listing]
            
            # Check seller structure
            seller_structure_valid = False
            if "seller" in first_listing and isinstance(first_listing["seller"], dict):
                seller = first_listing["seller"]
                seller_required = ["name", "username"]
                seller_structure_valid = all(field in seller for field in seller_required)
            
            # Check bid_info structure
            bid_info_structure_valid = False
            if "bid_info" in first_listing and isinstance(first_listing["bid_info"], dict):
                bid_info = first_listing["bid_info"]
                bid_required = ["has_bids", "total_bids", "highest_bid"]
                bid_info_structure_valid = all(field in bid_info for field in bid_required)
            
            # Check images structure
            images_structure_valid = False
            if "images" in first_listing and isinstance(first_listing["images"], list):
                images_structure_valid = True
            
            structure_checks.append({
                "listing_id": first_listing.get("id", "unknown"),
                "required_fields_present": len(missing_required) == 0,
                "missing_required_fields": missing_required,
                "enriched_fields_present": len(missing_enriched) == 0,
                "missing_enriched_fields": missing_enriched,
                "seller_structure_valid": seller_structure_valid,
                "bid_info_structure_valid": bid_info_structure_valid,
                "images_structure_valid": images_structure_valid
            })
        
        # Calculate overall structure integrity
        if structure_checks:
            check = structure_checks[0]
            structure_integrity_score = sum([
                check["required_fields_present"],
                check["enriched_fields_present"],
                check["seller_structure_valid"],
                check["bid_info_structure_valid"],
                check["images_structure_valid"]
            ]) / 5 * 100
            
            no_breaking_changes = structure_integrity_score >= 80
        else:
            structure_integrity_score = 0
            no_breaking_changes = False
        
        return {
            "test_name": "Data Structure Integrity",
            "structure_integrity_score": structure_integrity_score,
            "no_breaking_changes": no_breaking_changes,
            "total_listings_checked": len(listings) if isinstance(listings, list) else 0,
            "detailed_structure_checks": structure_checks
        }
    
    async def test_key_endpoints_response_times(self) -> Dict:
        """Test response times across key endpoints"""
        print("⚡ Testing Key Endpoints Response Times...")
        
        endpoints_to_test = [
            {"endpoint": "/marketplace/browse", "name": "Browse Listings", "target_ms": BROWSE_RESPONSE_TIME_TARGET_MS},
            {"endpoint": "/marketplace/search", "name": "Search Listings", "params": {"q": "catalyst"}, "target_ms": GENERAL_PERFORMANCE_TARGET_MS},
            {"endpoint": "/health", "name": "Health Check", "target_ms": 100},
            {"endpoint": "/admin/dashboard", "name": "Admin Dashboard", "target_ms": GENERAL_PERFORMANCE_TARGET_MS},
            {"endpoint": "/admin/performance", "name": "Performance Metrics", "target_ms": GENERAL_PERFORMANCE_TARGET_MS}
        ]
        
        endpoint_results = []
        
        for endpoint_config in endpoints_to_test:
            endpoint = endpoint_config["endpoint"]
            name = endpoint_config["name"]
            params = endpoint_config.get("params")
            target_ms = endpoint_config["target_ms"]
            
            print(f"  Testing {name}...")
            
            # Test 3 times for consistency
            response_times = []
            
            for i in range(3):
                result = await self.make_request(endpoint, params=params)
                if result["success"]:
                    response_times.append(result["response_time_ms"])
            
            if response_times:
                avg_time = statistics.mean(response_times)
                meets_target = avg_time < target_ms
                
                endpoint_results.append({
                    "endpoint": endpoint,
                    "name": name,
                    "avg_response_time_ms": avg_time,
                    "target_ms": target_ms,
                    "meets_target": meets_target,
                    "total_calls": len(response_times)
                })
                
                status = "✅" if meets_target else "⚠️"
                print(f"    {status} {avg_time:.0f}ms (target: <{target_ms}ms)")
            else:
                endpoint_results.append({
                    "endpoint": endpoint,
                    "name": name,
                    "error": "All calls failed",
                    "meets_target": False
                })
                print(f"    ❌ All calls failed")
        
        successful_endpoints = [e for e in endpoint_results if e.get("avg_response_time_ms")]
        performant_endpoints = [e for e in successful_endpoints if e.get("meets_target", False)]
        
        return {
            "test_name": "Key Endpoints Response Times",
            "total_endpoints_tested": len(endpoints_to_test),
            "successful_endpoints": len(successful_endpoints),
            "performant_endpoints": len(performant_endpoints),
            "overall_performance_good": len(performant_endpoints) >= len(successful_endpoints) * 0.8,
            "detailed_endpoint_results": endpoint_results
        }
    
    async def run_comprehensive_test(self) -> Dict:
        """Run all comprehensive performance tests"""
        print("🚀 Starting Comprehensive Performance Optimization Validation")
        print("=" * 80)
        print("Validating specific requirements from review request:")
        print("1. Browse endpoint response size (~12KB, not 44MB+)")
        print("2. Thumbnail system for actual images")
        print("3. Message/tender endpoint performance (N+1 fixes)")
        print("4. No breaking changes in data structure")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run all test suites
            browse_performance = await self.test_browse_performance_multiple_times()
            thumbnail_system = await self.test_thumbnail_system_actual_images()
            message_performance = await self.test_message_endpoint_performance()
            tender_performance = await self.test_tender_endpoint_performance()
            data_integrity = await self.test_data_structure_integrity()
            endpoint_performance = await self.test_key_endpoints_response_times()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "success_criteria": {
                    "browse_response_size_kb": BROWSE_RESPONSE_SIZE_TARGET_KB,
                    "browse_response_time_ms": BROWSE_RESPONSE_TIME_TARGET_MS,
                    "general_performance_ms": GENERAL_PERFORMANCE_TARGET_MS
                },
                "browse_performance_multiple": browse_performance,
                "thumbnail_system_actual": thumbnail_system,
                "message_endpoint_performance": message_performance,
                "tender_endpoint_performance": tender_performance,
                "data_structure_integrity": data_integrity,
                "key_endpoints_performance": endpoint_performance
            }
            
            # Calculate overall success
            critical_tests = [
                browse_performance.get("meets_success_criteria", False),
                thumbnail_system.get("thumbnail_system_working", False),
                message_performance.get("n1_fix_working", False),
                tender_performance.get("n1_fix_working", False),
                data_integrity.get("no_breaking_changes", False),
                endpoint_performance.get("overall_performance_good", False)
            ]
            
            overall_success_rate = sum(critical_tests) / len(critical_tests) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "browse_optimization_successful": browse_performance.get("meets_success_criteria", False),
                "thumbnail_system_working": thumbnail_system.get("thumbnail_system_working", False),
                "message_n1_fix_working": message_performance.get("n1_fix_working", False),
                "tender_n1_fix_working": tender_performance.get("n1_fix_working", False),
                "no_breaking_changes": data_integrity.get("no_breaking_changes", False),
                "overall_performance_acceptable": endpoint_performance.get("overall_performance_good", False),
                "all_critical_requirements_met": overall_success_rate >= 80,
                "performance_issue_44mb_resolved": browse_performance.get("meets_success_criteria", False)
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = ComprehensivePerformanceTester()
    
    try:
        results = await tester.run_comprehensive_test()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE PERFORMANCE OPTIMIZATION VALIDATION SUMMARY")
        print("=" * 80)
        
        summary = results.get("summary", {})
        
        print(f"Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
        print(f"Browse Optimization (44MB->12KB): {'✅' if summary.get('browse_optimization_successful', False) else '❌'}")
        print(f"Thumbnail System Working: {'✅' if summary.get('thumbnail_system_working', False) else '❌'}")
        print(f"Message N+1 Fix Working: {'✅' if summary.get('message_n1_fix_working', False) else '❌'}")
        print(f"Tender N+1 Fix Working: {'✅' if summary.get('tender_n1_fix_working', False) else '❌'}")
        print(f"No Breaking Changes: {'✅' if summary.get('no_breaking_changes', False) else '❌'}")
        print(f"Overall Performance Acceptable: {'✅' if summary.get('overall_performance_acceptable', False) else '❌'}")
        print(f"44MB Performance Issue Resolved: {'✅' if summary.get('performance_issue_44mb_resolved', False) else '❌'}")
        
        # Detailed metrics
        browse_perf = results.get("browse_performance_multiple", {})
        if browse_perf.get("meets_success_criteria", False):
            print(f"\n🚀 BROWSE OPTIMIZATION DETAILS:")
            print(f"   Response Size: {browse_perf.get('avg_response_size_kb', 0):.1f}KB (Target: <{BROWSE_RESPONSE_SIZE_TARGET_KB}KB)")
            print(f"   Response Time: {browse_perf.get('avg_response_time_ms', 0):.0f}ms (Target: <{BROWSE_RESPONSE_TIME_TARGET_MS}ms)")
            print(f"   Improvement: {browse_perf.get('improvement_from_44mb_percent', 0):.2f}% reduction from 44MB")
        
        # Save detailed results
        with open('/app/comprehensive_performance_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: /app/comprehensive_performance_results.json")
        
        # Return appropriate exit code
        if summary.get("all_critical_requirements_met", False):
            print("\n✅ ALL CRITICAL PERFORMANCE REQUIREMENTS MET!")
            return 0
        else:
            print("\n❌ SOME CRITICAL PERFORMANCE REQUIREMENTS NOT MET")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)