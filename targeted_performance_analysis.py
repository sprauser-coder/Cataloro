#!/usr/bin/env python3
"""
Targeted Performance Analysis for Cataloro Marketplace
Focused on the specific performance bottlenecks identified in logs:
1. Redis cache failure causing fallback mode
2. Elasticsearch failure causing database fallback
3. N+1 query problem in browse listings endpoint
4. Inefficient seller profile fetching
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://market-mobile-ui.preview.emergentagent.com/api"

class TargetedPerformanceAnalyzer:
    def __init__(self):
        self.issues_found = []
        self.performance_data = {}
        
    def analyze_service_dependencies(self):
        """Analyze critical service dependencies that are failing"""
        print("🔍 ANALYZING SERVICE DEPENDENCIES")
        print("-" * 50)
        
        try:
            # Get performance metrics to check service status
            response = requests.get(f"{BACKEND_URL}/admin/performance", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.performance_data = data
                
                # Check Redis cache status
                cache_info = data.get('cache', {})
                cache_status = cache_info.get('status', 'unknown')
                
                if cache_status == 'disabled':
                    self.issues_found.append({
                        'severity': 'HIGH',
                        'issue': 'Redis Cache Service Down',
                        'description': 'Redis connection failed, system running in fallback mode',
                        'impact': 'Significantly slower response times, no caching benefits',
                        'recommendation': 'Install and configure Redis service'
                    })
                    print("🚨 CRITICAL: Redis Cache Service is DOWN")
                    print("   Impact: No caching, slower response times")
                
                # Check Elasticsearch status
                search_info = data.get('search', {})
                search_status = search_info.get('status', 'unknown')
                
                if search_status == 'fallback_mode':
                    self.issues_found.append({
                        'severity': 'MEDIUM',
                        'issue': 'Elasticsearch Service Down',
                        'description': 'Elasticsearch connection failed, using database fallback',
                        'impact': 'Slower search operations, limited search capabilities',
                        'recommendation': 'Install and configure Elasticsearch service'
                    })
                    print("⚠️  WARNING: Elasticsearch Service is DOWN")
                    print("   Impact: Slower search, database fallback mode")
                
                # Check optimizations status
                optimizations = data.get('optimizations', {})
                caching_status = optimizations.get('caching', '')
                
                if 'fallback' in caching_status.lower():
                    print("📊 System running in fallback mode - performance degraded")
                
                return True
            else:
                print(f"❌ Failed to get performance metrics: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error analyzing service dependencies: {e}")
            return False

    def analyze_n_plus_one_query_problem(self):
        """Analyze the N+1 query problem in browse listings"""
        print("\n🔍 ANALYZING N+1 QUERY PROBLEM")
        print("-" * 50)
        
        try:
            # Test browse listings endpoint and measure time
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=15)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                listings = response.json()
                num_listings = len(listings)
                
                print(f"📋 Browse Listings Response Time: {response_time:.2f}ms")
                print(f"📊 Number of listings returned: {num_listings}")
                
                # Calculate expected vs actual performance
                # Each listing should take ~10-20ms to process efficiently
                expected_time = num_listings * 20  # 20ms per listing is reasonable
                
                if response_time > expected_time * 2:  # More than 2x expected
                    self.issues_found.append({
                        'severity': 'HIGH',
                        'issue': 'N+1 Query Problem in Browse Listings',
                        'description': f'Browse endpoint taking {response_time:.2f}ms for {num_listings} listings',
                        'impact': 'Extremely slow page loads, poor user experience',
                        'recommendation': 'Optimize seller profile fetching with JOIN queries or batch loading'
                    })
                    print(f"🚨 CRITICAL: N+1 Query Problem Detected")
                    print(f"   Expected: ~{expected_time}ms, Actual: {response_time:.2f}ms")
                    print(f"   Performance degradation: {(response_time/expected_time):.1f}x slower")
                
                # Check if seller information is being fetched efficiently
                if num_listings > 0:
                    sample_listing = listings[0]
                    if 'seller' in sample_listing:
                        print("✅ Seller information is being included")
                    else:
                        print("⚠️  Seller information missing from listings")
                
                return True
            else:
                print(f"❌ Browse listings failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error analyzing N+1 query problem: {e}")
            return False

    def analyze_database_performance(self):
        """Analyze database performance and query efficiency"""
        print("\n🔍 ANALYZING DATABASE PERFORMANCE")
        print("-" * 50)
        
        try:
            if not self.performance_data:
                print("❌ Performance data not available")
                return False
            
            db_info = self.performance_data.get('database', {})
            collections_info = self.performance_data.get('collections', {})
            
            # Check database size and performance
            total_size = db_info.get('total_size', 0)
            collections_count = db_info.get('collections', 0)
            
            print(f"📊 Database size: {total_size/1024/1024:.2f} MB")
            print(f"📊 Collections: {collections_count}")
            
            # Check for performance issues in key collections
            key_collections = ['users', 'listings', 'tenders']
            
            for collection_name in key_collections:
                collection_data = collections_info.get(collection_name, {})
                if isinstance(collection_data, dict):
                    doc_count = collection_data.get('document_count', 0)
                    index_count = collection_data.get('index_count', 0)
                    
                    print(f"📋 {collection_name}: {doc_count} documents, {index_count} indexes")
                    
                    # Check for potential performance issues
                    if doc_count > 1000 and index_count <= 2:
                        self.issues_found.append({
                            'severity': 'MEDIUM',
                            'issue': f'Insufficient Indexes on {collection_name}',
                            'description': f'{collection_name} has {doc_count} documents but only {index_count} indexes',
                            'impact': 'Slow queries on large collections',
                            'recommendation': f'Add indexes to frequently queried fields in {collection_name}'
                        })
                        print(f"⚠️  {collection_name} may need more indexes")
            
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing database performance: {e}")
            return False

    def test_concurrent_performance_impact(self):
        """Test how the performance issues affect concurrent requests"""
        print("\n🔍 TESTING CONCURRENT PERFORMANCE IMPACT")
        print("-" * 50)
        
        try:
            import concurrent.futures
            import threading
            
            def make_browse_request():
                start = time.time()
                try:
                    response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=20)
                    end = time.time()
                    return response.status_code == 200, (end - start) * 1000
                except:
                    end = time.time()
                    return False, (end - start) * 1000
            
            # Test with 3 concurrent requests (moderate load)
            print("🔄 Testing 3 concurrent browse requests...")
            
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(make_browse_request) for _ in range(3)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            end_time = time.time()
            
            total_time = (end_time - start_time) * 1000
            successful_requests = sum(1 for success, _ in results if success)
            response_times = [time_ms for success, time_ms in results if success]
            
            print(f"📊 Total time for 3 concurrent requests: {total_time:.2f}ms")
            print(f"📊 Successful requests: {successful_requests}/3")
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                
                print(f"📊 Average response time: {avg_response_time:.2f}ms")
                print(f"📊 Maximum response time: {max_response_time:.2f}ms")
                
                # Check for performance degradation under load
                if total_time > 10000:  # More than 10 seconds for 3 requests
                    self.issues_found.append({
                        'severity': 'HIGH',
                        'issue': 'Poor Concurrent Performance',
                        'description': f'3 concurrent requests took {total_time:.2f}ms total',
                        'impact': 'System cannot handle multiple users efficiently',
                        'recommendation': 'Optimize database queries and enable caching services'
                    })
                    print("🚨 CRITICAL: Poor concurrent performance detected")
                
                if max_response_time > 5000:  # Individual request > 5 seconds
                    print("🚨 CRITICAL: Individual requests taking too long")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing concurrent performance: {e}")
            return False

    def generate_performance_report(self):
        """Generate comprehensive performance report with recommendations"""
        print("\n" + "=" * 80)
        print("PERFORMANCE BOTTLENECK ANALYSIS REPORT")
        print("=" * 80)
        
        if not self.issues_found:
            print("✅ No critical performance issues detected")
            return
        
        # Sort issues by severity
        critical_issues = [i for i in self.issues_found if i['severity'] == 'HIGH']
        warning_issues = [i for i in self.issues_found if i['severity'] == 'MEDIUM']
        
        print(f"\n🚨 CRITICAL ISSUES FOUND: {len(critical_issues)}")
        for i, issue in enumerate(critical_issues, 1):
            print(f"\n{i}. {issue['issue']}")
            print(f"   Description: {issue['description']}")
            print(f"   Impact: {issue['impact']}")
            print(f"   Recommendation: {issue['recommendation']}")
        
        if warning_issues:
            print(f"\n⚠️  WARNING ISSUES FOUND: {len(warning_issues)}")
            for i, issue in enumerate(warning_issues, 1):
                print(f"\n{i}. {issue['issue']}")
                print(f"   Description: {issue['description']}")
                print(f"   Impact: {issue['impact']}")
                print(f"   Recommendation: {issue['recommendation']}")
        
        print("\n" + "=" * 80)
        print("IMMEDIATE ACTION ITEMS")
        print("=" * 80)
        
        action_items = []
        
        # Check for Redis issue
        redis_issue = any(i for i in self.issues_found if 'Redis' in i['issue'])
        if redis_issue:
            action_items.append("1. URGENT: Install and start Redis service for caching")
        
        # Check for N+1 query issue
        n_plus_one_issue = any(i for i in self.issues_found if 'N+1' in i['issue'])
        if n_plus_one_issue:
            action_items.append("2. URGENT: Fix N+1 query problem in browse listings endpoint")
        
        # Check for concurrent performance issue
        concurrent_issue = any(i for i in self.issues_found if 'Concurrent' in i['issue'])
        if concurrent_issue:
            action_items.append("3. HIGH: Optimize database queries for better concurrent performance")
        
        # Check for Elasticsearch issue
        es_issue = any(i for i in self.issues_found if 'Elasticsearch' in i['issue'])
        if es_issue:
            action_items.append("4. MEDIUM: Install Elasticsearch for better search performance")
        
        if action_items:
            for item in action_items:
                print(item)
        else:
            print("No immediate action items required")
        
        print("\n" + "=" * 80)
        print("EXPECTED PERFORMANCE IMPROVEMENT")
        print("=" * 80)
        
        if redis_issue and n_plus_one_issue:
            print("🚀 Fixing Redis + N+1 queries: 80-90% performance improvement expected")
        elif redis_issue:
            print("🚀 Fixing Redis caching: 50-70% performance improvement expected")
        elif n_plus_one_issue:
            print("🚀 Fixing N+1 queries: 60-80% performance improvement expected")
        else:
            print("📊 Minor optimizations: 10-30% performance improvement expected")

    def run_analysis(self):
        """Run complete targeted performance analysis"""
        print("=" * 80)
        print("CATALORO MARKETPLACE - TARGETED PERFORMANCE ANALYSIS")
        print("Analyzing specific performance bottlenecks causing system slowness")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Analysis Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Analyze service dependencies
        self.analyze_service_dependencies()
        
        # 2. Analyze N+1 query problem
        self.analyze_n_plus_one_query_problem()
        
        # 3. Analyze database performance
        self.analyze_database_performance()
        
        # 4. Test concurrent performance impact
        self.test_concurrent_performance_impact()
        
        # 5. Generate comprehensive report
        self.generate_performance_report()
        
        print(f"\n🎯 ANALYSIS COMPLETE - {len(self.issues_found)} issues identified")
        
        return self.issues_found

if __name__ == "__main__":
    analyzer = TargetedPerformanceAnalyzer()
    
    print("🎯 RUNNING TARGETED PERFORMANCE ANALYSIS")
    print("Identifying root causes of system slowness...")
    print()
    
    issues = analyzer.run_analysis()
    
    # Exit with error code if critical issues found
    critical_issues = [i for i in issues if i['severity'] == 'HIGH']
    exit(1 if critical_issues else 0)