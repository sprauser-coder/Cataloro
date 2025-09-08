#!/usr/bin/env python3
"""
Targeted Performance Test - Test specific optimizations and identify remaining bottlenecks
"""

import requests
import time
import json

BACKEND_URL = "https://listing-repair-4.preview.emergentagent.com/api"

def test_cache_effectiveness():
    """Test if caching is actually working"""
    print("🔍 TESTING CACHE EFFECTIVENESS")
    print("-" * 40)
    
    # Clear any existing cache by using unique parameters
    unique_param = int(time.time())
    
    # Test 1: First call (should populate cache)
    print("1. First call (populating cache):")
    start = time.time()
    response1 = requests.get(f"{BACKEND_URL}/marketplace/browse?page=1&limit=8&test={unique_param}", timeout=15)
    end = time.time()
    time1 = (end - start) * 1000
    print(f"   Time: {time1:.2f}ms")
    
    # Small delay
    time.sleep(0.5)
    
    # Test 2: Second call (should hit cache)
    print("2. Second call (should hit cache):")
    start = time.time()
    response2 = requests.get(f"{BACKEND_URL}/marketplace/browse?page=1&limit=8&test={unique_param}", timeout=15)
    end = time.time()
    time2 = (end - start) * 1000
    print(f"   Time: {time2:.2f}ms")
    
    # Test 3: Third call (verify cache consistency)
    print("3. Third call (verify cache):")
    start = time.time()
    response3 = requests.get(f"{BACKEND_URL}/marketplace/browse?page=1&limit=8&test={unique_param}", timeout=15)
    end = time.time()
    time3 = (end - start) * 1000
    print(f"   Time: {time3:.2f}ms")
    
    if all(r.status_code == 200 for r in [response1, response2, response3]):
        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()
        
        # Check data consistency
        consistent = len(data1) == len(data2) == len(data3)
        print(f"   Data consistent: {consistent}")
        print(f"   Listings count: {len(data1)}")
        
        # Check cache improvement
        cache_improvement = ((time1 - time2) / time1) * 100 if time1 > 0 else 0
        print(f"   Cache improvement: {cache_improvement:.1f}%")
        
        if cache_improvement < 10:
            print("   ⚠️ Cache not providing expected speedup")
        else:
            print("   ✅ Cache working effectively")
    else:
        print("   ❌ Some requests failed")

def test_simplified_browse():
    """Test a simplified version to isolate bottlenecks"""
    print("\n🔍 TESTING SIMPLIFIED BROWSE SCENARIOS")
    print("-" * 40)
    
    scenarios = [
        ("Minimal request", f"{BACKEND_URL}/marketplace/browse?page=1&limit=1"),
        ("Small batch", f"{BACKEND_URL}/marketplace/browse?page=1&limit=3"),
        ("Medium batch", f"{BACKEND_URL}/marketplace/browse?page=1&limit=8"),
        ("Business filter (likely empty)", f"{BACKEND_URL}/marketplace/browse?type=Business&page=1&limit=5"),
        ("Price filter", f"{BACKEND_URL}/marketplace/browse?price_from=100&price_to=500&page=1&limit=5"),
    ]
    
    for scenario_name, url in scenarios:
        print(f"\n{scenario_name}:")
        
        # Run multiple times to get average
        times = []
        for i in range(3):
            start = time.time()
            try:
                response = requests.get(url, timeout=15)
                end = time.time()
                response_time = (end - start) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    listing_count = len(data) if isinstance(data, list) else 0
                    times.append(response_time)
                    print(f"   Run {i+1}: {response_time:.2f}ms ({listing_count} listings)")
                else:
                    print(f"   Run {i+1}: ERROR - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   Run {i+1}: ERROR - {str(e)}")
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            print(f"   Average: {avg_time:.2f}ms (Range: {min_time:.2f}ms - {max_time:.2f}ms)")
            
            # Performance assessment
            if avg_time < 200:
                print("   ✅ Excellent performance")
            elif avg_time < 500:
                print("   ⚠️ Acceptable performance")
            else:
                print("   ❌ Poor performance")

def test_database_operations():
    """Test individual database operations"""
    print("\n🔍 TESTING DATABASE OPERATIONS")
    print("-" * 40)
    
    # Login first to get user ID
    admin_credentials = {
        "email": "admin@cataloro.com",
        "password": "admin123"
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=admin_credentials, timeout=10)
    
    if login_response.status_code == 200:
        user_data = login_response.json().get('user', {})
        user_id = user_data.get('id')
        
        db_operations = [
            ("User profile", f"{BACKEND_URL}/auth/profile/{user_id}"),
            ("User listings", f"{BACKEND_URL}/user/my-listings/{user_id}"),
            ("Admin users", f"{BACKEND_URL}/admin/users"),
        ]
        
        for op_name, url in db_operations:
            start = time.time()
            try:
                response = requests.get(url, timeout=10)
                end = time.time()
                response_time = (end - start) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    data_size = len(data) if isinstance(data, list) else 1
                    print(f"   {op_name}: {response_time:.2f}ms ({data_size} items)")
                else:
                    print(f"   {op_name}: ERROR - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   {op_name}: ERROR - {str(e)}")
    else:
        print("   ❌ Could not login to test database operations")

def test_performance_under_load():
    """Test performance degradation under load"""
    print("\n🔍 TESTING PERFORMANCE UNDER LOAD")
    print("-" * 40)
    
    import threading
    import queue
    
    def run_load_test(num_requests, request_name):
        print(f"\n{request_name} ({num_requests} requests):")
        
        results_queue = queue.Queue()
        
        def make_request(request_id):
            start = time.time()
            try:
                response = requests.get(f"{BACKEND_URL}/marketplace/browse?page=1&limit=5", timeout=20)
                end = time.time()
                results_queue.put({
                    'id': request_id,
                    'time': (end-start)*1000,
                    'success': response.status_code == 200
                })
            except Exception as e:
                end = time.time()
                results_queue.put({
                    'id': request_id,
                    'time': (end-start)*1000,
                    'success': False,
                    'error': str(e)
                })
        
        # Start requests
        threads = []
        start_total = time.time()
        
        for i in range(num_requests):
            thread = threading.Thread(target=make_request, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        end_total = time.time()
        total_time = (end_total - start_total) * 1000
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        successful_results = [r for r in results if r['success']]
        
        if successful_results:
            times = [r['time'] for r in successful_results]
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"   Total time: {total_time:.2f}ms")
            print(f"   Successful: {len(successful_results)}/{num_requests}")
            print(f"   Individual avg: {avg_time:.2f}ms (Range: {min_time:.2f}ms - {max_time:.2f}ms)")
            print(f"   Throughput: {len(successful_results)/total_time*1000:.2f} requests/second")
            
            # Performance assessment
            if avg_time < 500 and total_time < 2000:
                print("   ✅ Good performance under load")
            elif avg_time < 1000 and total_time < 5000:
                print("   ⚠️ Acceptable performance under load")
            else:
                print("   ❌ Poor performance under load")
        else:
            print("   ❌ All requests failed")
    
    # Test different load levels
    run_load_test(2, "Light load")
    run_load_test(5, "Medium load")

def main():
    print("🎯 TARGETED PERFORMANCE ANALYSIS")
    print("=" * 60)
    print("Identifying specific bottlenecks in the hybrid optimization")
    print()
    
    test_cache_effectiveness()
    test_simplified_browse()
    test_database_operations()
    test_performance_under_load()
    
    print("\n" + "=" * 60)
    print("TARGETED ANALYSIS COMPLETE")
    print("\nKey findings to look for:")
    print("- Cache should provide 20%+ speedup on repeated calls")
    print("- Smaller result sets should be faster than larger ones")
    print("- Database operations should be <100ms")
    print("- Performance should not degrade significantly under load")

if __name__ == "__main__":
    main()