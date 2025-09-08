#!/usr/bin/env python3
"""
Cataloro Backend Hybrid Performance Testing Suite - Final Performance Verification
Testing the newly implemented hybrid optimization approach for the browse endpoint
to verify the performance issues have been resolved.

Target Performance Goals:
- Browse endpoint response time: <200ms (from baseline 1226ms-1248ms)
- Concurrent load: 5-10 requests <1 second total
- 80-90% performance improvement expected
- Cache hit rates and Redis performance validation
"""

import requests
import json
import time
import asyncio
import aiohttp
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Get backend URL from environment
BACKEND_URL = "https://listing-repair-4.preview.emergentagent.com/api"

class HybridPerformanceTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_user = None
        self.admin_token = None
        self.baseline_performance = {
            "original_browse_time": 1237,  # Average of 1226ms-1248ms baseline
            "target_improvement": 80,      # 80% improvement target
            "target_response_time": 200    # <200ms target
        }
        
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

    def test_hybrid_browse_endpoint_performance(self):
        """Test the hybrid browse endpoint performance - PRIMARY TEST"""
        try:
            print("🎯 Testing Hybrid Browse Endpoint Performance...")
            
            # Test multiple calls to get accurate average
            response_times = []
            responses = []
            
            # Test different parameter combinations
            test_scenarios = [
                ("Default browse", f"{BACKEND_URL}/marketplace/browse"),
                ("Filtered browse", f"{BACKEND_URL}/marketplace/browse?type=all&price_from=0&price_to=999999"),
                ("Paginated browse", f"{BACKEND_URL}/marketplace/browse?page=1&limit=10"),
                ("Business filter", f"{BACKEND_URL}/marketplace/browse?type=Business&page=1&limit=20"),
                ("Price range filter", f"{BACKEND_URL}/marketplace/browse?price_from=100&price_to=500&page=1&limit=15")
            ]
            
            scenario_results = []
            
            for scenario_name, url in test_scenarios:
                try:
                    response, response_time = self.measure_response_time(
                        requests.get,
                        url,
                        timeout=15
                    )
                    
                    responses.append(response)
                    response_times.append(response_time)
                    
                    if response.status_code == 200:
                        listings = response.json()
                        listing_count = len(listings) if isinstance(listings, list) else 0
                        
                        # Check if seller information is populated (N+1 query fix verification)
                        has_seller_info = False
                        has_bid_info = False
                        
                        if listing_count > 0 and isinstance(listings, list):
                            first_listing = listings[0]
                            has_seller_info = 'seller' in first_listing and first_listing['seller'].get('name') != 'Unknown User'
                            has_bid_info = 'bid_info' in first_listing
                        
                        scenario_results.append({
                            'name': scenario_name,
                            'time': response_time,
                            'count': listing_count,
                            'seller_info': has_seller_info,
                            'bid_info': has_bid_info,
                            'success': True
                        })
                        
                        print(f"   {scenario_name}: {response_time:.2f}ms ({listing_count} listings)")
                        
                    else:
                        scenario_results.append({
                            'name': scenario_name,
                            'time': response_time,
                            'success': False,
                            'error': f"HTTP {response.status_code}"
                        })
                        
                except Exception as e:
                    scenario_results.append({
                        'name': scenario_name,
                        'time': 0,
                        'success': False,
                        'error': str(e)
                    })
            
            # Calculate performance metrics
            successful_times = [r['time'] for r in scenario_results if r['success']]
            
            if successful_times:
                avg_response_time = statistics.mean(successful_times)
                min_response_time = min(successful_times)
                max_response_time = max(successful_times)
                
                # Check if target performance is met
                target_met = avg_response_time < self.baseline_performance['target_response_time']
                
                # Calculate improvement percentage
                baseline_time = self.baseline_performance['original_browse_time']
                improvement_percent = ((baseline_time - avg_response_time) / baseline_time) * 100
                target_improvement = self.baseline_performance['target_improvement']
                
                improvement_target_met = improvement_percent >= target_improvement
                
                # Check data integrity
                successful_scenarios = [r for r in scenario_results if r['success']]
                data_integrity_good = all(
                    r.get('seller_info', False) and r.get('bid_info', False) 
                    for r in successful_scenarios if r.get('count', 0) > 0
                )
                
                success = target_met and improvement_target_met and data_integrity_good
                
                self.log_test(
                    "Hybrid Browse Endpoint Performance", 
                    success, 
                    f"Avg: {avg_response_time:.2f}ms (Target: <{self.baseline_performance['target_response_time']}ms), "
                    f"Range: {min_response_time:.2f}ms - {max_response_time:.2f}ms, "
                    f"Improvement: {improvement_percent:.1f}% (Target: ≥{target_improvement}%), "
                    f"Data integrity: {data_integrity_good}, Scenarios passed: {len(successful_scenarios)}/{len(scenario_results)}",
                    performance_data=f"Baseline: {baseline_time}ms → Current: {avg_response_time:.2f}ms ({improvement_percent:.1f}% improvement)"
                )
                
                return success
            else:
                self.log_test("Hybrid Browse Endpoint Performance", False, error_msg="No successful responses")
                return False
                
        except Exception as e:
            self.log_test("Hybrid Browse Endpoint Performance", False, error_msg=str(e))
            return False

    def test_concurrent_load_performance(self):
        """Test concurrent load handling - 5-10 concurrent requests"""
        try:
            print("🚀 Testing Concurrent Load Performance...")
            
            # Test with 8 concurrent requests (middle of 5-10 range)
            num_concurrent = 8
            url = f"{BACKEND_URL}/marketplace/browse?page=1&limit=10"
            
            def make_request():
                start_time = time.time()
                try:
                    response = requests.get(url, timeout=15)
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    return {
                        'success': response.status_code == 200,
                        'time': response_time,
                        'status_code': response.status_code,
                        'data_size': len(response.json()) if response.status_code == 200 else 0
                    }
                except Exception as e:
                    end_time = time.time()
                    return {
                        'success': False,
                        'time': (end_time - start_time) * 1000,
                        'error': str(e)
                    }
            
            # Execute concurrent requests
            start_total_time = time.time()
            
            with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                futures = [executor.submit(make_request) for _ in range(num_concurrent)]
                results = [future.result() for future in as_completed(futures)]
            
            end_total_time = time.time()
            total_time = (end_total_time - start_total_time) * 1000  # Convert to ms
            
            # Analyze results
            successful_results = [r for r in results if r['success']]
            successful_count = len(successful_results)
            
            if successful_results:
                individual_times = [r['time'] for r in successful_results]
                avg_individual_time = statistics.mean(individual_times)
                max_individual_time = max(individual_times)
                min_individual_time = min(individual_times)
                
                # Performance targets
                individual_target_met = avg_individual_time < 200  # Each request <200ms
                total_target_met = total_time < 1000  # Total time <1 second
                all_requests_successful = successful_count == num_concurrent
                
                success = individual_target_met and total_target_met and all_requests_successful
                
                self.log_test(
                    "Concurrent Load Performance", 
                    success, 
                    f"Concurrent requests: {num_concurrent}, Successful: {successful_count}, "
                    f"Total time: {total_time:.2f}ms (Target: <1000ms), "
                    f"Avg individual: {avg_individual_time:.2f}ms (Target: <200ms), "
                    f"Range: {min_individual_time:.2f}ms - {max_individual_time:.2f}ms",
                    performance_data=f"Throughput: {num_concurrent/total_time*1000:.1f} requests/second"
                )
                
                return success
            else:
                self.log_test("Concurrent Load Performance", False, error_msg="No successful concurrent requests")
                return False
                
        except Exception as e:
            self.log_test("Concurrent Load Performance", False, error_msg=str(e))
            return False

    def test_cache_performance_validation(self):
        """Test Redis cache performance and hit rates"""
        try:
            print("💾 Testing Cache Performance Validation...")
            
            # Test cache cold vs warm performance
            cache_test_url = f"{BACKEND_URL}/marketplace/browse?type=all&page=1&limit=20"
            
            # First call (cold cache)
            response1, time1 = self.measure_response_time(
                requests.get,
                cache_test_url,
                timeout=15
            )
            
            # Small delay to ensure cache is set
            time.sleep(0.1)
            
            # Second call (should hit cache)
            response2, time2 = self.measure_response_time(
                requests.get,
                cache_test_url,
                timeout=15
            )
            
            # Third call (verify cache consistency)
            response3, time3 = self.measure_response_time(
                requests.get,
                cache_test_url,
                timeout=15
            )
            
            all_successful = all(r.status_code == 200 for r in [response1, response2, response3])
            
            if all_successful:
                data1 = response1.json()
                data2 = response2.json()
                data3 = response3.json()
                
                # Check data consistency
                data_consistent = (
                    len(data1) == len(data2) == len(data3) and
                    isinstance(data1, list) and isinstance(data2, list) and isinstance(data3, list)
                )
                
                # Check cache performance improvement
                cache_times = [time2, time3]
                avg_cache_time = statistics.mean(cache_times)
                
                # Cache should be faster or at least not significantly slower
                cache_effective = avg_cache_time <= time1 * 1.2  # Allow 20% variance
                
                # Check if cache keys are being used (browse_v3_* pattern)
                # This would be visible in performance improvement
                performance_good = avg_cache_time < 300  # Should be fast with caching
                
                success = data_consistent and cache_effective and performance_good
                
                self.log_test(
                    "Cache Performance Validation", 
                    success, 
                    f"Data consistent: {data_consistent}, Cache effective: {cache_effective}, "
                    f"Cold cache: {time1:.2f}ms, Warm cache avg: {avg_cache_time:.2f}ms, "
                    f"Cache improvement: {((time1 - avg_cache_time) / time1 * 100):.1f}%, "
                    f"Data size: {len(data1)} listings",
                    performance_data=f"Cache hit performance: {avg_cache_time:.2f}ms vs cold: {time1:.2f}ms"
                )
                
                return success
            else:
                failed_responses = [f"Call {i+1}: HTTP {r.status_code}" for i, r in enumerate([response1, response2, response3]) if r.status_code != 200]
                self.log_test("Cache Performance Validation", False, error_msg=f"Failed responses: {', '.join(failed_responses)}")
                return False
                
        except Exception as e:
            self.log_test("Cache Performance Validation", False, error_msg=str(e))
            return False

    def test_data_integrity_verification(self):
        """Verify data integrity in hybrid approach"""
        try:
            print("🔍 Testing Data Integrity Verification...")
            
            # Get sample listings to verify data structure
            response, response_time = self.measure_response_time(
                requests.get,
                f"{BACKEND_URL}/marketplace/browse?page=1&limit=5",
                timeout=15
            )
            
            if response.status_code == 200:
                listings = response.json()
                
                if isinstance(listings, list) and len(listings) > 0:
                    # Check data structure integrity
                    integrity_checks = {
                        'has_listings': len(listings) > 0,
                        'seller_info_populated': False,
                        'bid_info_present': False,
                        'time_limit_processing': False,
                        'seller_type_filtering': False,
                        'consistent_ids': True
                    }
                    
                    for listing in listings:
                        # Check seller information
                        if 'seller' in listing:
                            seller = listing['seller']
                            if (seller.get('name') and seller.get('name') != 'Unknown User' and
                                'username' in seller and 'is_business' in seller):
                                integrity_checks['seller_info_populated'] = True
                        
                        # Check bid information
                        if 'bid_info' in listing:
                            bid_info = listing['bid_info']
                            if ('has_bids' in bid_info and 'total_bids' in bid_info and 
                                'highest_bid' in bid_info):
                                integrity_checks['bid_info_present'] = True
                        
                        # Check time limit processing
                        if 'time_info' in listing:
                            time_info = listing['time_info']
                            if ('has_time_limit' in time_info and 'is_expired' in time_info):
                                integrity_checks['time_limit_processing'] = True
                        
                        # Check seller type (business/private)
                        if 'seller' in listing and 'is_business' in listing['seller']:
                            integrity_checks['seller_type_filtering'] = True
                        
                        # Check ID consistency
                        if 'id' not in listing or not listing['id']:
                            integrity_checks['consistent_ids'] = False
                    
                    # Test seller type filtering
                    business_response, _ = self.measure_response_time(
                        requests.get,
                        f"{BACKEND_URL}/marketplace/browse?type=Business&page=1&limit=5",
                        timeout=15
                    )
                    
                    if business_response.status_code == 200:
                        business_listings = business_response.json()
                        if isinstance(business_listings, list):
                            # Verify business filter works
                            business_filter_works = all(
                                listing.get('seller', {}).get('is_business', False) 
                                for listing in business_listings if len(business_listings) > 0
                            )
                            integrity_checks['seller_type_filtering'] = business_filter_works or len(business_listings) == 0
                    
                    # Calculate integrity score
                    passed_checks = sum(1 for check in integrity_checks.values() if check)
                    total_checks = len(integrity_checks)
                    integrity_score = (passed_checks / total_checks) * 100
                    
                    success = integrity_score >= 80  # 80% of checks should pass
                    
                    check_details = [f"{key}: {'✅' if value else '❌'}" for key, value in integrity_checks.items()]
                    
                    self.log_test(
                        "Data Integrity Verification", 
                        success, 
                        f"Integrity score: {integrity_score:.1f}% ({passed_checks}/{total_checks} checks passed), "
                        f"Sample size: {len(listings)} listings, "
                        f"Checks: {', '.join(check_details)}",
                        performance_data=f"Data verification time: {response_time:.2f}ms"
                    )
                    
                    return success
                else:
                    self.log_test("Data Integrity Verification", False, error_msg="No listings returned for integrity check")
                    return False
            else:
                self.log_test("Data Integrity Verification", False, error_msg=f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Data Integrity Verification", False, error_msg=str(e))
            return False

    def test_performance_comparison_baseline(self):
        """Final performance comparison against baseline"""
        try:
            print("📊 Testing Performance Comparison vs Baseline...")
            
            # Run multiple tests to get accurate baseline comparison
            test_runs = 5
            response_times = []
            
            for i in range(test_runs):
                response, response_time = self.measure_response_time(
                    requests.get,
                    f"{BACKEND_URL}/marketplace/browse?page=1&limit=20",
                    timeout=15
                )
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    print(f"   Run {i+1}: {response_time:.2f}ms")
                
                # Small delay between runs
                time.sleep(0.2)
            
            if response_times:
                avg_current_time = statistics.mean(response_times)
                min_time = min(response_times)
                max_time = max(response_times)
                
                # Calculate improvement metrics
                baseline_time = self.baseline_performance['original_browse_time']
                improvement_percent = ((baseline_time - avg_current_time) / baseline_time) * 100
                
                # Performance targets
                target_improvement = self.baseline_performance['target_improvement']
                target_response_time = self.baseline_performance['target_response_time']
                
                improvement_target_met = improvement_percent >= target_improvement
                response_time_target_met = avg_current_time < target_response_time
                
                # Calculate performance multiplier
                performance_multiplier = baseline_time / avg_current_time
                
                success = improvement_target_met and response_time_target_met
                
                self.log_test(
                    "Performance Comparison vs Baseline", 
                    success, 
                    f"Baseline: {baseline_time}ms → Current: {avg_current_time:.2f}ms, "
                    f"Improvement: {improvement_percent:.1f}% (Target: ≥{target_improvement}%), "
                    f"Performance multiplier: {performance_multiplier:.1f}x faster, "
                    f"Response time target met: {response_time_target_met} (<{target_response_time}ms), "
                    f"Range: {min_time:.2f}ms - {max_time:.2f}ms",
                    performance_data=f"Expected 6x-8x improvement, Achieved: {performance_multiplier:.1f}x"
                )
                
                return success
            else:
                self.log_test("Performance Comparison vs Baseline", False, error_msg="No successful response times recorded")
                return False
                
        except Exception as e:
            self.log_test("Performance Comparison vs Baseline", False, error_msg=str(e))
            return False

    def run_hybrid_performance_testing(self):
        """Run comprehensive hybrid performance testing suite"""
        print("=" * 80)
        print("CATALORO HYBRID PERFORMANCE TESTING - Final Performance Verification")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print(f"Baseline Performance: {self.baseline_performance['original_browse_time']}ms")
        print(f"Target Improvement: {self.baseline_performance['target_improvement']}%")
        print(f"Target Response Time: <{self.baseline_performance['target_response_time']}ms")
        print()
        
        # 1. Admin Login
        print("👤 ADMIN LOGIN")
        print("-" * 40)
        if not self.test_admin_login():
            print("❌ Admin login failed. Continuing with public endpoint testing.")
        
        # 2. Hybrid Browse Endpoint Performance (PRIMARY TEST)
        print("🎯 HYBRID BROWSE ENDPOINT PERFORMANCE")
        print("-" * 40)
        self.test_hybrid_browse_endpoint_performance()
        
        # 3. Concurrent Load Testing
        print("🚀 CONCURRENT LOAD TESTING")
        print("-" * 40)
        self.test_concurrent_load_performance()
        
        # 4. Data Integrity Verification
        print("🔍 DATA INTEGRITY VERIFICATION")
        print("-" * 40)
        self.test_data_integrity_verification()
        
        # 5. Cache Performance Validation
        print("💾 CACHE PERFORMANCE VALIDATION")
        print("-" * 40)
        self.test_cache_performance_validation()
        
        # 6. Final Performance Comparison
        print("📊 FINAL PERFORMANCE COMPARISON")
        print("-" * 40)
        self.test_performance_comparison_baseline()
        
        # Print Summary
        print("=" * 80)
        print("HYBRID PERFORMANCE TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Performance Analysis
        print("PERFORMANCE ANALYSIS:")
        print(f"  Original Baseline: {self.baseline_performance['original_browse_time']}ms")
        print(f"  Target Improvement: ≥{self.baseline_performance['target_improvement']}%")
        print(f"  Target Response Time: <{self.baseline_performance['target_response_time']}ms")
        print(f"  Expected Performance Gain: 6x to 8x faster")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
            print()
        
        # Final Assessment
        critical_tests = [
            "Hybrid Browse Endpoint Performance",
            "Concurrent Load Performance", 
            "Performance Comparison vs Baseline"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and "✅ PASS" in result['status'])
        
        print("🎯 HYBRID OPTIMIZATION ASSESSMENT:")
        if critical_passed == len(critical_tests):
            print("  ✅ HYBRID OPTIMIZATION SUCCESSFUL - All performance targets met")
            print("  ✅ Browse endpoint performance issues RESOLVED")
            print("  ✅ 80-90% performance improvement ACHIEVED")
            print("  ✅ Concurrent load handling IMPROVED")
            print("  ✅ System ready for production load")
        elif critical_passed >= 2:
            print("  ⚠️ HYBRID OPTIMIZATION PARTIALLY SUCCESSFUL - Some targets met")
            print("  ⚠️ Further optimization may be needed")
        else:
            print("  ❌ HYBRID OPTIMIZATION NEEDS WORK - Performance targets not met")
            print("  ❌ Additional optimization required")
        
        print("\n🎯 HYBRID PERFORMANCE TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = HybridPerformanceTester()
    
    print("🎯 RUNNING HYBRID PERFORMANCE TESTING")
    print("Testing hybrid optimization approach for browse endpoint performance...")
    print("Expected: 80-90% improvement from 1226ms-1248ms baseline to <200ms target")
    print()
    
    result = tester.run_hybrid_performance_testing()
    if result:
        passed, failed, results = result
        # Exit with appropriate code
        exit(0 if failed == 0 else 1)
    else:
        exit(1)