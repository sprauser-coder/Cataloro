#!/usr/bin/env python3
"""
Cataloro Backend Redis Optimization Performance Testing Suite
Testing Redis caching functionality and optimized browse/listings endpoints
after Redis installation and N+1 query optimization implementation.
"""

import requests
import json
import time
from datetime import datetime
import statistics
import concurrent.futures
import threading

# Get backend URL from environment
BACKEND_URL = "https://listing-repair-4.preview.emergentagent.com/api"

class RedisOptimizationTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_user = None
        self.admin_token = None
        self.baseline_performance = {}
        
    def log_test(self, test_name, success, details="", error_msg="", performance_data=None):
        """Log test results with performance metrics"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "performance": performance_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if performance_data:
            print(f"   Performance: {performance_data}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def measure_response_time(self, func, *args, **kwargs):
        """Measure response time of a function call"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        return result, response_time

    def test_admin_login(self):
        """Test admin login and store credentials for subsequent tests"""
        try:
            admin_credentials = {
                "email": "admin@cataloro.com",
                "password": "admin123"
            }
            
            response, response_time = self.measure_response_time(
                requests.post,
                f"{BACKEND_URL}/auth/login", 
                json=admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                token = data.get('token', '')
                
                self.admin_user = user
                self.admin_token = token
                
                user_role = user.get('user_role')
                user_id = user.get('id')
                username = user.get('username')
                
                is_admin = user_role in ['Admin', 'Admin-Manager']
                
                self.log_test(
                    "Admin Login", 
                    is_admin, 
                    f"Username: {username}, Role: {user_role}, User ID: {user_id}",
                    performance_data=f"Response time: {response_time:.2f}ms"
                )
                return is_admin
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login", False, error_msg=f"Login failed: {error_detail}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, error_msg=str(e))
            return False

    def test_redis_connection_status(self):
        """Test Redis connection and caching status"""
        try:
            response, response_time = self.measure_response_time(
                requests.get,
                f"{BACKEND_URL}/admin/performance",
                timeout=15
            )
            
            if response.status_code == 200:
                metrics = response.json()
                
                # Check cache service health
                cache_info = metrics.get('cache', {})
                cache_status = cache_info.get('status', 'unknown')
                cache_connected = cache_info.get('connected', False)
                cache_mode = cache_info.get('mode', 'unknown')
                
                # Check optimizations section for Redis status
                optimizations = metrics.get('optimizations', {})
                caching_status = optimizations.get('caching', '')
                
                # Redis should be working (not in fallback mode)
                redis_working = (
                    cache_status in ['healthy', 'active', 'connected'] and
                    cache_connected and
                    'fallback' not in caching_status.lower()
                )
                
                # Check if Redis ping is working
                redis_ping = cache_info.get('ping', 'unknown')
                ping_working = redis_ping in ['PONG', 'OK', True]
                
                success = redis_working and ping_working
                
                self.log_test(
                    "Redis Connection Status", 
                    success, 
                    f"Cache status: {cache_status}, Connected: {cache_connected}, "
                    f"Mode: {cache_mode}, Ping: {redis_ping}, Caching: {caching_status}",
                    performance_data=f"Response time: {response_time:.2f}ms"
                )
                
                return success
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Redis Connection Status", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Redis Connection Status", False, error_msg=str(e))
            return False

    def test_optimized_browse_endpoint_performance(self):
        """Test optimized browse endpoint performance - Target: <300ms"""
        try:
            # Test multiple calls to measure performance and caching
            response_times = []
            cache_hits = []
            
            for i in range(5):
                response, response_time = self.measure_response_time(
                    requests.get,
                    f"{BACKEND_URL}/marketplace/browse?page=1&limit=20",
                    timeout=15
                )
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    listings = response.json()
                    
                    # Check if we got listings data
                    if isinstance(listings, list) and len(listings) > 0:
                        # Check for seller information (N+1 query optimization)
                        first_listing = listings[0]
                        has_seller_info = 'seller' in first_listing and isinstance(first_listing['seller'], dict)
                        has_seller_name = has_seller_info and 'name' in first_listing['seller']
                        
                        cache_hits.append({
                            'response_time': response_time,
                            'listings_count': len(listings),
                            'has_seller_info': has_seller_info,
                            'has_seller_name': has_seller_name
                        })
                else:
                    self.log_test("Optimized Browse Endpoint Performance", False, 
                                error_msg=f"HTTP {response.status_code} on call {i+1}")
                    return False
                
                # Small delay between calls
                time.sleep(0.2)
            
            if response_times:
                avg_response_time = statistics.mean(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
                
                # Performance targets
                meets_target = avg_response_time < 300  # Target: <300ms
                improved_from_baseline = avg_response_time < 1226  # Previous baseline: 1226ms
                
                # Check N+1 optimization (all listings should have seller info)
                n1_optimized = all(hit['has_seller_info'] and hit['has_seller_name'] for hit in cache_hits)
                
                # Check caching effectiveness (subsequent calls should be faster or similar)
                caching_effective = len(response_times) > 1 and response_times[-1] <= response_times[0] * 1.5
                
                success = meets_target and improved_from_baseline and n1_optimized
                
                improvement_percentage = ((1226 - avg_response_time) / 1226) * 100 if avg_response_time < 1226 else 0
                
                self.log_test(
                    "Optimized Browse Endpoint Performance", 
                    success, 
                    f"Target met (<300ms): {meets_target}, N+1 optimized: {n1_optimized}, "
                    f"Caching effective: {caching_effective}, Listings: {cache_hits[0]['listings_count'] if cache_hits else 0}, "
                    f"Improvement: {improvement_percentage:.1f}% from baseline (1226ms)",
                    performance_data=f"Avg: {avg_response_time:.2f}ms, Min: {min_response_time:.2f}ms, Max: {max_response_time:.2f}ms"
                )
                
                # Store for comparison
                self.baseline_performance['browse_avg'] = avg_response_time
                
                return success
            else:
                self.log_test("Optimized Browse Endpoint Performance", False, error_msg="No successful responses")
                return False
                
        except Exception as e:
            self.log_test("Optimized Browse Endpoint Performance", False, error_msg=str(e))
            return False

    def test_optimized_listings_endpoint_performance(self):
        """Test optimized listings endpoint performance - Target: <200ms"""
        try:
            if not self.admin_user:
                self.log_test("Optimized Listings Endpoint Performance", False, error_msg="Admin user not available")
                return False
            
            user_id = self.admin_user.get('id')
            
            # Test multiple calls to measure performance and caching
            response_times = []
            
            for i in range(5):
                response, response_time = self.measure_response_time(
                    requests.get,
                    f"{BACKEND_URL}/user/my-listings/{user_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    listings = response.json()
                else:
                    self.log_test("Optimized Listings Endpoint Performance", False, 
                                error_msg=f"HTTP {response.status_code} on call {i+1}")
                    return False
                
                # Small delay between calls
                time.sleep(0.1)
            
            if response_times:
                avg_response_time = statistics.mean(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
                
                # Performance targets
                meets_target = avg_response_time < 200  # Target: <200ms
                
                # Check caching effectiveness (subsequent calls should be faster)
                caching_effective = len(response_times) > 1 and response_times[-1] <= response_times[0] * 1.2
                
                success = meets_target
                
                self.log_test(
                    "Optimized Listings Endpoint Performance", 
                    success, 
                    f"Target met (<200ms): {meets_target}, Caching effective: {caching_effective}, "
                    f"User listings: {len(listings) if isinstance(listings, list) else 0}",
                    performance_data=f"Avg: {avg_response_time:.2f}ms, Min: {min_response_time:.2f}ms, Max: {max_response_time:.2f}ms"
                )
                
                # Store for comparison
                self.baseline_performance['listings_avg'] = avg_response_time
                
                return success
            else:
                self.log_test("Optimized Listings Endpoint Performance", False, error_msg="No successful responses")
                return False
                
        except Exception as e:
            self.log_test("Optimized Listings Endpoint Performance", False, error_msg=str(e))
            return False

    def test_cache_hit_miss_rates(self):
        """Test cache hit/miss rates for listing endpoints"""
        try:
            # Test browse endpoint caching
            cache_key_base = "browse_v2_all_0_999999"
            
            # First call (should be cache miss)
            response1, time1 = self.measure_response_time(
                requests.get,
                f"{BACKEND_URL}/marketplace/browse?type=all&price_from=0&price_to=999999&page=1&limit=10",
                timeout=10
            )
            
            # Second call immediately (should be cache hit)
            response2, time2 = self.measure_response_time(
                requests.get,
                f"{BACKEND_URL}/marketplace/browse?type=all&price_from=0&price_to=999999&page=1&limit=10",
                timeout=10
            )
            
            # Third call with different parameters (should be cache miss)
            response3, time3 = self.measure_response_time(
                requests.get,
                f"{BACKEND_URL}/marketplace/browse?type=all&price_from=100&price_to=500&page=1&limit=10",
                timeout=10
            )
            
            all_successful = all(r.status_code == 200 for r in [response1, response2, response3])
            
            if all_successful:
                # Cache hit should be faster than cache miss
                cache_hit_faster = time2 < time1 * 0.8  # At least 20% faster
                
                # Different parameters should take similar time to first call (both cache misses)
                different_params_similar = abs(time3 - time1) < time1 * 0.5  # Within 50%
                
                # Check data consistency
                data1 = response1.json()
                data2 = response2.json()
                data_consistent = len(data1) == len(data2) if isinstance(data1, list) and isinstance(data2, list) else True
                
                success = cache_hit_faster and data_consistent
                
                self.log_test(
                    "Cache Hit/Miss Rates", 
                    success, 
                    f"Cache hit faster: {cache_hit_faster}, Data consistent: {data_consistent}, "
                    f"Different params similar: {different_params_similar}",
                    performance_data=f"Miss: {time1:.2f}ms, Hit: {time2:.2f}ms, Miss2: {time3:.2f}ms"
                )
                
                return success
            else:
                failed_responses = [f"Call {i+1}: HTTP {r.status_code}" for i, r in enumerate([response1, response2, response3]) if r.status_code != 200]
                self.log_test("Cache Hit/Miss Rates", False, error_msg=f"Failed responses: {', '.join(failed_responses)}")
                return False
                
        except Exception as e:
            self.log_test("Cache Hit/Miss Rates", False, error_msg=str(e))
            return False

    def test_concurrent_load_performance(self):
        """Test concurrent load performance - 5-10 concurrent requests"""
        try:
            def make_request(request_id):
                """Make a single request and return timing data"""
                try:
                    start_time = time.time()
                    response = requests.get(
                        f"{BACKEND_URL}/marketplace/browse?page=1&limit=15",
                        timeout=20
                    )
                    end_time = time.time()
                    
                    return {
                        'id': request_id,
                        'status_code': response.status_code,
                        'response_time': (end_time - start_time) * 1000,
                        'success': response.status_code == 200,
                        'data_size': len(response.json()) if response.status_code == 200 and isinstance(response.json(), list) else 0
                    }
                except Exception as e:
                    return {
                        'id': request_id,
                        'status_code': 0,
                        'response_time': 0,
                        'success': False,
                        'error': str(e)
                    }
            
            # Test with 8 concurrent requests
            num_concurrent = 8
            
            start_time = time.time()
            
            # Use ThreadPoolExecutor for concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                futures = [executor.submit(make_request, i) for i in range(num_concurrent)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            total_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Analyze results
            successful_requests = [r for r in results if r['success']]
            failed_requests = [r for r in results if not r['success']]
            
            if successful_requests:
                response_times = [r['response_time'] for r in successful_requests]
                avg_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
                
                # Performance targets
                all_successful = len(failed_requests) == 0
                avg_under_target = avg_response_time < 500  # Average should be under 500ms
                max_under_limit = max_response_time < 1000  # No request should take more than 1s
                total_time_reasonable = total_time < 3000  # Total time should be under 3s
                
                success = all_successful and avg_under_target and max_under_limit and total_time_reasonable
                
                self.log_test(
                    "Concurrent Load Performance", 
                    success, 
                    f"Concurrent requests: {num_concurrent}, Successful: {len(successful_requests)}, "
                    f"Failed: {len(failed_requests)}, All targets met: {success}",
                    performance_data=f"Total: {total_time:.2f}ms, Avg: {avg_response_time:.2f}ms, "
                                   f"Min: {min_response_time:.2f}ms, Max: {max_response_time:.2f}ms"
                )
                
                return success
            else:
                self.log_test("Concurrent Load Performance", False, error_msg="No successful concurrent requests")
                return False
                
        except Exception as e:
            self.log_test("Concurrent Load Performance", False, error_msg=str(e))
            return False

    def test_performance_baseline_comparison(self):
        """Compare current performance to previous baseline (1226ms)"""
        try:
            if not self.baseline_performance:
                self.log_test("Performance Baseline Comparison", False, error_msg="No baseline performance data available")
                return False
            
            browse_avg = self.baseline_performance.get('browse_avg', 0)
            listings_avg = self.baseline_performance.get('listings_avg', 0)
            
            # Previous baseline from test_result.md
            previous_browse_baseline = 1226  # ms
            
            # Calculate improvements
            browse_improvement = ((previous_browse_baseline - browse_avg) / previous_browse_baseline) * 100 if browse_avg > 0 else 0
            
            # Performance targets
            browse_improved = browse_improvement >= 60  # At least 60% improvement
            browse_under_300 = browse_avg < 300  # Under 300ms target
            listings_under_200 = listings_avg < 200 if listings_avg > 0 else True  # Under 200ms target
            
            # Overall success
            success = browse_improved and browse_under_300 and listings_under_200
            
            self.log_test(
                "Performance Baseline Comparison", 
                success, 
                f"Browse improvement: {browse_improvement:.1f}% (target: ≥60%), "
                f"Browse <300ms: {browse_under_300}, Listings <200ms: {listings_under_200}",
                performance_data=f"Previous: {previous_browse_baseline}ms → Current: {browse_avg:.2f}ms (browse), {listings_avg:.2f}ms (listings)"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Performance Baseline Comparison", False, error_msg=str(e))
            return False

    def test_aggregation_pipeline_optimization(self):
        """Test that MongoDB aggregation pipeline is working correctly"""
        try:
            # Test browse endpoint with complex query that should use aggregation
            response, response_time = self.measure_response_time(
                requests.get,
                f"{BACKEND_URL}/marketplace/browse?type=all&price_from=0&price_to=999999&page=1&limit=20",
                timeout=15
            )
            
            if response.status_code == 200:
                listings = response.json()
                
                if isinstance(listings, list) and len(listings) > 0:
                    # Check that seller information is properly populated (aggregation working)
                    seller_info_complete = True
                    bid_info_complete = True
                    
                    for listing in listings:
                        # Check seller information (should be populated by aggregation)
                        seller = listing.get('seller', {})
                        if not isinstance(seller, dict) or not seller.get('name'):
                            seller_info_complete = False
                        
                        # Check bid information (should be populated by aggregation)
                        bid_info = listing.get('bid_info', {})
                        if not isinstance(bid_info, dict) or 'has_bids' not in bid_info:
                            bid_info_complete = False
                    
                    # Check performance (aggregation should be fast)
                    performance_good = response_time < 500  # Should be under 500ms
                    
                    success = seller_info_complete and bid_info_complete and performance_good
                    
                    self.log_test(
                        "Aggregation Pipeline Optimization", 
                        success, 
                        f"Seller info complete: {seller_info_complete}, Bid info complete: {bid_info_complete}, "
                        f"Performance good: {performance_good}, Listings processed: {len(listings)}",
                        performance_data=f"Response time: {response_time:.2f}ms (target: <500ms)"
                    )
                    
                    return success
                else:
                    self.log_test("Aggregation Pipeline Optimization", False, error_msg="No listings returned")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Aggregation Pipeline Optimization", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Aggregation Pipeline Optimization", False, error_msg=str(e))
            return False

    def run_redis_optimization_testing(self):
        """Run comprehensive Redis optimization testing suite"""
        print("=" * 80)
        print("CATALORO REDIS OPTIMIZATION PERFORMANCE TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print("Testing Redis caching and N+1 query optimizations...")
        print()
        
        # 1. Admin Login
        print("👤 ADMIN LOGIN")
        print("-" * 40)
        if not self.test_admin_login():
            print("❌ Admin login failed. Aborting testing.")
            return
        
        # 2. Redis Connection Status
        print("🔴 REDIS CONNECTION STATUS")
        print("-" * 40)
        self.test_redis_connection_status()
        
        # 3. Optimized Browse Endpoint Performance
        print("🚀 OPTIMIZED BROWSE ENDPOINT PERFORMANCE")
        print("-" * 40)
        self.test_optimized_browse_endpoint_performance()
        
        # 4. Optimized Listings Endpoint Performance
        print("📋 OPTIMIZED LISTINGS ENDPOINT PERFORMANCE")
        print("-" * 40)
        self.test_optimized_listings_endpoint_performance()
        
        # 5. Cache Hit/Miss Rates
        print("💾 CACHE HIT/MISS RATES")
        print("-" * 40)
        self.test_cache_hit_miss_rates()
        
        # 6. Concurrent Load Performance
        print("⚡ CONCURRENT LOAD PERFORMANCE")
        print("-" * 40)
        self.test_concurrent_load_performance()
        
        # 7. Aggregation Pipeline Optimization
        print("🔄 AGGREGATION PIPELINE OPTIMIZATION")
        print("-" * 40)
        self.test_aggregation_pipeline_optimization()
        
        # 8. Performance Baseline Comparison
        print("📊 PERFORMANCE BASELINE COMPARISON")
        print("-" * 40)
        self.test_performance_baseline_comparison()
        
        # Print Summary
        print("=" * 80)
        print("REDIS OPTIMIZATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Performance Summary
        if self.baseline_performance:
            print("PERFORMANCE METRICS SUMMARY:")
            for key, value in self.baseline_performance.items():
                print(f"  {key}: {value:.2f}ms")
            print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 REDIS OPTIMIZATION TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Redis caching connected and working")
        print("  ✅ Browse endpoint <300ms (60-80% improvement from 1226ms baseline)")
        print("  ✅ Listings endpoint <200ms with caching")
        print("  ✅ Cache hit/miss rates showing caching effectiveness")
        print("  ✅ Concurrent load handling 5-10 requests efficiently")
        print("  ✅ MongoDB aggregation pipeline eliminating N+1 queries")
        print("  ✅ Overall system performance improved by 60-80%")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = RedisOptimizationTester()
    
    print("🎯 RUNNING REDIS OPTIMIZATION PERFORMANCE TESTING")
    print("Testing Redis caching and optimized endpoints after performance improvements...")
    print()
    
    result = tester.run_redis_optimization_testing()
    if result:
        passed, failed, results = result
        # Exit with appropriate code
        exit(0 if failed == 0 else 1)
    else:
        exit(1)