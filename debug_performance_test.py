#!/usr/bin/env python3
"""
Debug Performance Test - Identify specific bottlenecks in the hybrid approach
"""

import requests
import time
import json

BACKEND_URL = "https://listing-repair-4.preview.emergentagent.com/api"

def test_individual_components():
    """Test individual components to identify bottlenecks"""
    
    print("🔍 DEBUGGING PERFORMANCE BOTTLENECKS")
    print("=" * 60)
    
    # Test 1: Simple health check
    print("1. Health Check Performance:")
    start = time.time()
    response = requests.get(f"{BACKEND_URL}/health", timeout=10)
    end = time.time()
    print(f"   Health check: {(end-start)*1000:.2f}ms (Status: {response.status_code})")
    
    # Test 2: Performance metrics endpoint
    print("\n2. Performance Metrics Endpoint:")
    start = time.time()
    response = requests.get(f"{BACKEND_URL}/admin/performance", timeout=15)
    end = time.time()
    print(f"   Performance metrics: {(end-start)*1000:.2f}ms (Status: {response.status_code})")
    
    if response.status_code == 200:
        data = response.json()
        cache_info = data.get('cache', {})
        print(f"   Cache status: {cache_info.get('status', 'unknown')}")
        print(f"   Cache mode: {cache_info.get('mode', 'unknown')}")
    
    # Test 3: Browse endpoint with different parameters
    print("\n3. Browse Endpoint Performance Analysis:")
    
    test_cases = [
        ("Empty cache - first call", f"{BACKEND_URL}/marketplace/browse?page=1&limit=5&_t={int(time.time())}"),
        ("Cached call - same params", f"{BACKEND_URL}/marketplace/browse?page=1&limit=5"),
        ("Different params", f"{BACKEND_URL}/marketplace/browse?page=1&limit=3"),
        ("Business filter", f"{BACKEND_URL}/marketplace/browse?type=Business&page=1&limit=5"),
    ]
    
    for test_name, url in test_cases:
        print(f"\n   {test_name}:")
        start = time.time()
        try:
            response = requests.get(url, timeout=20)
            end = time.time()
            response_time = (end-start)*1000
            
            if response.status_code == 200:
                data = response.json()
                listing_count = len(data) if isinstance(data, list) else 0
                print(f"     Time: {response_time:.2f}ms")
                print(f"     Listings: {listing_count}")
                
                # Check data structure
                if listing_count > 0:
                    first_listing = data[0]
                    has_seller = 'seller' in first_listing
                    has_bid_info = 'bid_info' in first_listing
                    has_time_info = 'time_info' in first_listing
                    print(f"     Data structure: seller={has_seller}, bid_info={has_bid_info}, time_info={has_time_info}")
            else:
                print(f"     ERROR: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"     ERROR: {str(e)}")
    
    # Test 4: Database query performance (admin endpoints)
    print("\n4. Database Query Performance:")
    
    # Test admin login first
    admin_credentials = {
        "email": "admin@cataloro.com",
        "password": "admin123"
    }
    
    start = time.time()
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=admin_credentials, timeout=10)
    end = time.time()
    print(f"   Admin login: {(end-start)*1000:.2f}ms (Status: {login_response.status_code})")
    
    if login_response.status_code == 200:
        user_data = login_response.json().get('user', {})
        user_id = user_data.get('id')
        
        # Test user listings
        start = time.time()
        listings_response = requests.get(f"{BACKEND_URL}/user/my-listings/{user_id}", timeout=10)
        end = time.time()
        print(f"   User listings: {(end-start)*1000:.2f}ms (Status: {listings_response.status_code})")
        
        # Test admin dashboard
        start = time.time()
        dashboard_response = requests.get(f"{BACKEND_URL}/admin/dashboard", timeout=15)
        end = time.time()
        print(f"   Admin dashboard: {(end-start)*1000:.2f}ms (Status: {dashboard_response.status_code})")
    
    # Test 5: Concurrent requests analysis
    print("\n5. Concurrent Request Analysis:")
    print("   Testing 3 concurrent requests...")
    
    import threading
    import queue
    
    results_queue = queue.Queue()
    
    def make_request(request_id):
        start = time.time()
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/browse?page=1&limit=5", timeout=20)
            end = time.time()
            results_queue.put({
                'id': request_id,
                'time': (end-start)*1000,
                'status': response.status_code,
                'success': response.status_code == 200
            })
        except Exception as e:
            end = time.time()
            results_queue.put({
                'id': request_id,
                'time': (end-start)*1000,
                'status': 'ERROR',
                'success': False,
                'error': str(e)
            })
    
    # Start concurrent requests
    threads = []
    start_concurrent = time.time()
    
    for i in range(3):
        thread = threading.Thread(target=make_request, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_concurrent = time.time()
    total_concurrent_time = (end_concurrent - start_concurrent) * 1000
    
    print(f"   Total concurrent time: {total_concurrent_time:.2f}ms")
    
    # Collect results
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())
    
    for result in sorted(results, key=lambda x: x['id']):
        status = "✅" if result['success'] else "❌"
        print(f"   Request {result['id']}: {status} {result['time']:.2f}ms (Status: {result['status']})")
    
    if results:
        successful_times = [r['time'] for r in results if r['success']]
        if successful_times:
            avg_time = sum(successful_times) / len(successful_times)
            print(f"   Average individual time: {avg_time:.2f}ms")
    
    print("\n" + "=" * 60)
    print("PERFORMANCE ANALYSIS COMPLETE")
    print("Expected findings:")
    print("- Health check should be <100ms")
    print("- Cached browse calls should be faster than uncached")
    print("- Individual requests should be <500ms for good performance")
    print("- Concurrent requests should not degrade significantly")

if __name__ == "__main__":
    test_individual_components()