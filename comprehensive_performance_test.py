#!/usr/bin/env python3
"""
Cataloro Marketplace - Comprehensive Performance Testing Suite
Focused on identifying performance bottlenecks causing system slowness.

This test suite analyzes:
1. API Response Time Analysis for all major endpoints
2. Database Performance Testing (MongoDB queries, indexes)
3. Service Health & Resource Usage
4. Critical Endpoint Performance (listings, auth, admin, messaging)
5. Error Detection & Optimization Opportunities
"""

import requests
import json
import time
import statistics
import concurrent.futures
from datetime import datetime
import threading

# Get backend URL from environment
BACKEND_URL = "https://listing-repair-4.preview.emergentagent.com/api"

class ComprehensivePerformanceTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_user = None
        self.admin_token = None
        self.demo_user = None
        self.demo_token = None
        self.performance_data = {}
        self.bottlenecks = []
        self.optimization_recommendations = []
        
    def log_test(self, test_name, success, details="", error_msg="", performance_data=None, is_critical=False):
        """Log test results with performance metrics"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            if is_critical:
                status = "🚨 CRITICAL FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "performance": performance_data,
            "is_critical": is_critical,
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
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            return result, response_time, None
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return None, response_time, str(e)

    def test_admin_authentication(self):
        """Test admin login performance and store credentials"""
        try:
            admin_credentials = {
                "email": "admin@cataloro.com",
                "password": "admin123"
            }
            
            response, response_time, error = self.measure_response_time(
                requests.post,
                f"{BACKEND_URL}/auth/login", 
                json=admin_credentials,
                timeout=15
            )
            
            if error:
                self.log_test("Admin Authentication", False, error_msg=error, is_critical=True)
                return False
            
            if response and response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                token = data.get('token', '')
                
                self.admin_user = user
                self.admin_token = token
                
                user_role = user.get('user_role')
                is_admin = user_role in ['Admin', 'Admin-Manager']
                
                # Check if response time is acceptable
                performance_good = response_time < 2000  # 2 seconds max for login
                
                if response_time > 1000:
                    self.bottlenecks.append(f"Admin login slow: {response_time:.2f}ms")
                
                self.log_test(
                    "Admin Authentication", 
                    is_admin and performance_good, 
                    f"Role: {user_role}, User: {user.get('username')}",
                    performance_data=f"Response time: {response_time:.2f}ms",
                    is_critical=True
                )
                return is_admin and performance_good
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response and response.content else f"HTTP {response.status_code if response else 'No response'}"
                self.log_test("Admin Authentication", False, error_msg=f"Login failed: {error_detail}", is_critical=True)
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, error_msg=str(e), is_critical=True)
            return False

    def test_demo_user_authentication(self):
        """Test demo user login performance"""
        try:
            demo_credentials = {
                "email": "user@cataloro.com",
                "password": "user123"
            }
            
            response, response_time, error = self.measure_response_time(
                requests.post,
                f"{BACKEND_URL}/auth/login", 
                json=demo_credentials,
                timeout=15
            )
            
            if error:
                self.log_test("Demo User Authentication", False, error_msg=error)
                return False
            
            if response and response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                token = data.get('token', '')
                
                self.demo_user = user
                self.demo_token = token
                
                performance_good = response_time < 2000
                
                if response_time > 1000:
                    self.bottlenecks.append(f"Demo user login slow: {response_time:.2f}ms")
                
                self.log_test(
                    "Demo User Authentication", 
                    performance_good, 
                    f"User: {user.get('username')}, Role: {user.get('user_role')}",
                    performance_data=f"Response time: {response_time:.2f}ms"
                )
                return performance_good
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response and response.content else f"HTTP {response.status_code if response else 'No response'}"
                self.log_test("Demo User Authentication", False, error_msg=f"Login failed: {error_detail}")
                return False
        except Exception as e:
            self.log_test("Demo User Authentication", False, error_msg=str(e))
            return False

    def test_api_health_and_performance_metrics(self):
        """Test basic API health and performance metrics endpoint"""
        try:
            # Test health endpoint
            health_response, health_time, health_error = self.measure_response_time(
                requests.get,
                f"{BACKEND_URL}/health",
                timeout=10
            )
            
            # Test performance metrics endpoint
            perf_response, perf_time, perf_error = self.measure_response_time(
                requests.get,
                f"{BACKEND_URL}/admin/performance",
                timeout=20
            )
            
            health_ok = health_response and health_response.status_code == 200 and not health_error
            perf_ok = perf_response and perf_response.status_code == 200 and not perf_error
            
            if health_ok and perf_ok:
                health_data = health_response.json()
                perf_data = perf_response.json()
                
                # Store performance data for later analysis
                self.performance_data = perf_data
                
                # Check response times
                health_fast = health_time < 500  # Health should be very fast
                perf_acceptable = perf_time < 5000  # Performance metrics can take longer
                
                if health_time > 200:
                    self.bottlenecks.append(f"Health endpoint slow: {health_time:.2f}ms")
                if perf_time > 3000:
                    self.bottlenecks.append(f"Performance metrics slow: {perf_time:.2f}ms")
                
                # Check database statistics
                db_info = perf_data.get('database', {})
                collections_count = db_info.get('collections', 0)
                
                success = health_fast and perf_acceptable and collections_count > 0
                
                self.log_test(
                    "API Health & Performance Metrics", 
                    success, 
                    f"Health: {health_data.get('status')}, DB Collections: {collections_count}, "
                    f"Performance Status: {perf_data.get('performance_status')}",
                    performance_data=f"Health: {health_time:.2f}ms, Performance: {perf_time:.2f}ms",
                    is_critical=True
                )
                return success
            else:
                errors = []
                if health_error:
                    errors.append(f"Health: {health_error}")
                if perf_error:
                    errors.append(f"Performance: {perf_error}")
                if not health_ok:
                    errors.append(f"Health HTTP: {health_response.status_code if health_response else 'No response'}")
                if not perf_ok:
                    errors.append(f"Performance HTTP: {perf_response.status_code if perf_response else 'No response'}")
                
                self.log_test("API Health & Performance Metrics", False, error_msg="; ".join(errors), is_critical=True)
                return False
                
        except Exception as e:
            self.log_test("API Health & Performance Metrics", False, error_msg=str(e), is_critical=True)
            return False

    def test_database_performance_analysis(self):
        """Analyze database performance and identify bottlenecks"""
        try:
            if not self.performance_data:
                self.log_test("Database Performance Analysis", False, error_msg="Performance data not available")
                return False
            
            db_info = self.performance_data.get('database', {})
            collections_info = self.performance_data.get('collections', {})
            
            # Analyze database size and performance
            total_size = db_info.get('total_size', 0)
            index_size = db_info.get('index_size', 0)
            collections_count = db_info.get('collections', 0)
            
            # Check index coverage
            total_indexes = 0
            collections_with_indexes = 0
            slow_collections = []
            
            for collection_name, collection_data in collections_info.items():
                if isinstance(collection_data, dict):
                    index_count = collection_data.get('index_count', 0)
                    document_count = collection_data.get('document_count', 0)
                    
                    total_indexes += index_count
                    if index_count > 1:  # More than just _id index
                        collections_with_indexes += 1
                    
                    # Identify potentially slow collections (many documents, few indexes)
                    if document_count > 1000 and index_count <= 2:
                        slow_collections.append(f"{collection_name} ({document_count} docs, {index_count} indexes)")
            
            # Performance analysis
            index_coverage_good = total_indexes >= 30  # Should have many indexes for performance
            size_reasonable = total_size < 100 * 1024 * 1024  # Less than 100MB is reasonable for testing
            
            # Check for performance issues
            performance_issues = []
            if total_indexes < 20:
                performance_issues.append("Insufficient database indexes")
                self.optimization_recommendations.append("Add more database indexes for frequently queried fields")
            
            if slow_collections:
                performance_issues.append(f"Collections with poor indexing: {', '.join(slow_collections)}")
                self.optimization_recommendations.append("Add indexes to collections with many documents")
            
            if total_size > 50 * 1024 * 1024:  # 50MB+
                performance_issues.append("Large database size may impact performance")
                self.optimization_recommendations.append("Consider data archiving or cleanup")
            
            success = index_coverage_good and len(performance_issues) == 0
            
            self.log_test(
                "Database Performance Analysis", 
                success, 
                f"Total indexes: {total_indexes}, Collections: {collections_count}, "
                f"Size: {total_size/1024/1024:.2f}MB, Issues: {len(performance_issues)}",
                error_msg="; ".join(performance_issues) if performance_issues else ""
            )
            
            return success
            
        except Exception as e:
            self.log_test("Database Performance Analysis", False, error_msg=str(e))
            return False

    def test_critical_endpoints_performance(self):
        """Test performance of critical marketplace endpoints"""
        try:
            critical_endpoints = [
                ("Browse Listings", "GET", f"{BACKEND_URL}/marketplace/browse", None, 1000),
                ("Browse with Filters", "GET", f"{BACKEND_URL}/marketplace/browse?type=all&price_from=0&price_to=1000", None, 1500),
                ("Search Listings", "GET", f"{BACKEND_URL}/marketplace/search?q=catalyst", None, 2000),
                ("Search Suggestions", "GET", f"{BACKEND_URL}/marketplace/search/suggestions?q=cat", None, 500),
                ("Admin Dashboard", "GET", f"{BACKEND_URL}/admin/dashboard", None, 2000),
                ("Admin Users", "GET", f"{BACKEND_URL}/admin/users", None, 3000),
            ]
            
            if self.admin_user:
                user_id = self.admin_user.get('id')
                critical_endpoints.extend([
                    ("User Profile", "GET", f"{BACKEND_URL}/auth/profile/{user_id}", None, 500),
                    ("User Listings", "GET", f"{BACKEND_URL}/user/my-listings/{user_id}", None, 1000),
                    ("User Notifications", "GET", f"{BACKEND_URL}/user/notifications/{user_id}", None, 1000),
                ])
            
            endpoint_results = []
            slow_endpoints = []
            failed_endpoints = []
            
            for name, method, url, data, max_time in critical_endpoints:
                try:
                    if method == "GET":
                        response, response_time, error = self.measure_response_time(
                            requests.get, url, timeout=15
                        )
                    else:
                        response, response_time, error = self.measure_response_time(
                            requests.post, url, json=data, timeout=15
                        )
                    
                    if error:
                        failed_endpoints.append(f"{name}: {error}")
                        endpoint_results.append((name, False, response_time, error))
                        continue
                    
                    success = response and response.status_code == 200
                    performance_ok = response_time < max_time
                    
                    if success and not performance_ok:
                        slow_endpoints.append(f"{name}: {response_time:.2f}ms (target: <{max_time}ms)")
                        self.bottlenecks.append(f"{name} endpoint slow: {response_time:.2f}ms")
                    
                    if not success:
                        failed_endpoints.append(f"{name}: HTTP {response.status_code if response else 'No response'}")
                    
                    endpoint_results.append((name, success and performance_ok, response_time, None))
                    
                except Exception as e:
                    failed_endpoints.append(f"{name}: {str(e)}")
                    endpoint_results.append((name, False, 0, str(e)))
            
            # Calculate statistics
            successful_endpoints = [r for r in endpoint_results if r[1]]
            total_endpoints = len(endpoint_results)
            success_rate = len(successful_endpoints) / total_endpoints if total_endpoints > 0 else 0
            
            avg_response_time = statistics.mean([r[2] for r in endpoint_results if r[2] > 0]) if endpoint_results else 0
            
            # Overall success criteria
            success = success_rate >= 0.8 and len(slow_endpoints) <= 2 and len(failed_endpoints) == 0
            
            details = f"Success rate: {success_rate:.1%} ({len(successful_endpoints)}/{total_endpoints}), "
            details += f"Avg response time: {avg_response_time:.2f}ms"
            
            error_msg = ""
            if slow_endpoints:
                error_msg += f"Slow endpoints: {'; '.join(slow_endpoints)}. "
            if failed_endpoints:
                error_msg += f"Failed endpoints: {'; '.join(failed_endpoints)}"
            
            self.log_test(
                "Critical Endpoints Performance", 
                success, 
                details,
                error_msg=error_msg.strip(),
                is_critical=True
            )
            
            return success
            
        except Exception as e:
            self.log_test("Critical Endpoints Performance", False, error_msg=str(e), is_critical=True)
            return False

    def test_concurrent_load_handling(self):
        """Test how the system handles concurrent requests"""
        try:
            def make_request():
                try:
                    response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
                    return response.status_code == 200, time.time()
                except:
                    return False, time.time()
            
            # Test with 5 concurrent requests
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            total_time = (end_time - start_time) * 1000
            
            successful_requests = sum(1 for success, _ in results if success)
            success_rate = successful_requests / len(results)
            
            # Check if concurrent handling is acceptable
            concurrent_performance_ok = total_time < 5000  # All 5 requests should complete within 5 seconds
            success_rate_ok = success_rate >= 0.8  # At least 80% should succeed
            
            if total_time > 3000:
                self.bottlenecks.append(f"Concurrent request handling slow: {total_time:.2f}ms for 5 requests")
            
            success = concurrent_performance_ok and success_rate_ok
            
            self.log_test(
                "Concurrent Load Handling", 
                success, 
                f"Success rate: {success_rate:.1%} ({successful_requests}/5 requests)",
                performance_data=f"Total time for 5 concurrent requests: {total_time:.2f}ms"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Concurrent Load Handling", False, error_msg=str(e))
            return False

    def test_memory_and_resource_usage(self):
        """Test for potential memory leaks and resource usage"""
        try:
            # Make multiple requests to the same endpoint to check for memory leaks
            endpoint = f"{BACKEND_URL}/marketplace/browse"
            response_times = []
            
            for i in range(10):
                response, response_time, error = self.measure_response_time(
                    requests.get, endpoint, timeout=10
                )
                
                if not error and response and response.status_code == 200:
                    response_times.append(response_time)
                else:
                    # If requests start failing, it might indicate resource issues
                    break
                
                time.sleep(0.1)  # Small delay between requests
            
            if len(response_times) >= 8:  # At least 8 out of 10 should succeed
                # Check if response times are increasing (potential memory leak)
                first_half_avg = statistics.mean(response_times[:len(response_times)//2])
                second_half_avg = statistics.mean(response_times[len(response_times)//2:])
                
                # Response times shouldn't increase significantly
                performance_degradation = second_half_avg > first_half_avg * 1.5
                
                if performance_degradation:
                    self.bottlenecks.append(f"Potential memory leak detected: response times increasing from {first_half_avg:.2f}ms to {second_half_avg:.2f}ms")
                    self.optimization_recommendations.append("Investigate potential memory leaks in request handling")
                
                avg_response_time = statistics.mean(response_times)
                consistent_performance = not performance_degradation and avg_response_time < 1000
                
                self.log_test(
                    "Memory & Resource Usage", 
                    consistent_performance, 
                    f"Completed {len(response_times)}/10 requests, Avg time: {avg_response_time:.2f}ms, "
                    f"Performance degradation: {performance_degradation}",
                    error_msg="Performance degradation detected" if performance_degradation else ""
                )
                
                return consistent_performance
            else:
                self.log_test("Memory & Resource Usage", False, error_msg=f"Only {len(response_times)}/10 requests succeeded")
                return False
                
        except Exception as e:
            self.log_test("Memory & Resource Usage", False, error_msg=str(e))
            return False

    def test_error_detection_and_logging(self):
        """Test for hidden errors that might cause slowdowns"""
        try:
            # Test various endpoints that might have hidden errors
            test_endpoints = [
                (f"{BACKEND_URL}/marketplace/browse?page=999", "High page number"),
                (f"{BACKEND_URL}/marketplace/search?q=", "Empty search query"),
                (f"{BACKEND_URL}/auth/profile/nonexistent-user", "Non-existent user profile"),
                (f"{BACKEND_URL}/user/my-listings/invalid-id", "Invalid user ID"),
            ]
            
            error_responses = []
            slow_error_responses = []
            
            for url, description in test_endpoints:
                response, response_time, error = self.measure_response_time(
                    requests.get, url, timeout=10
                )
                
                if error:
                    error_responses.append(f"{description}: {error}")
                elif response:
                    # Check if error responses are taking too long
                    if response_time > 2000:  # Error responses should be fast
                        slow_error_responses.append(f"{description}: {response_time:.2f}ms")
                    
                    # Log response codes for analysis
                    if response.status_code >= 500:
                        error_responses.append(f"{description}: HTTP {response.status_code}")
            
            # Check for patterns that indicate performance issues
            has_server_errors = any("HTTP 5" in error for error in error_responses)
            has_slow_errors = len(slow_error_responses) > 0
            
            if has_server_errors:
                self.bottlenecks.append("Server errors detected - may indicate backend issues")
                self.optimization_recommendations.append("Investigate server errors and improve error handling")
            
            if has_slow_errors:
                self.bottlenecks.append(f"Slow error responses: {'; '.join(slow_error_responses)}")
                self.optimization_recommendations.append("Optimize error handling performance")
            
            success = not has_server_errors and not has_slow_errors
            
            self.log_test(
                "Error Detection & Logging", 
                success, 
                f"Server errors: {has_server_errors}, Slow error responses: {len(slow_error_responses)}",
                error_msg="; ".join(error_responses + slow_error_responses) if error_responses or slow_error_responses else ""
            )
            
            return success
            
        except Exception as e:
            self.log_test("Error Detection & Logging", False, error_msg=str(e))
            return False

    def analyze_performance_bottlenecks(self):
        """Analyze all collected performance data and identify bottlenecks"""
        print("\n" + "=" * 80)
        print("PERFORMANCE BOTTLENECK ANALYSIS")
        print("=" * 80)
        
        if self.bottlenecks:
            print("🚨 IDENTIFIED BOTTLENECKS:")
            for i, bottleneck in enumerate(self.bottlenecks, 1):
                print(f"  {i}. {bottleneck}")
        else:
            print("✅ No significant performance bottlenecks detected")
        
        print("\n📊 OPTIMIZATION RECOMMENDATIONS:")
        if self.optimization_recommendations:
            for i, recommendation in enumerate(self.optimization_recommendations, 1):
                print(f"  {i}. {recommendation}")
        else:
            print("  No specific optimizations needed - system performance is acceptable")
        
        # Analyze performance data if available
        if self.performance_data:
            print("\n🔍 SYSTEM PERFORMANCE ANALYSIS:")
            
            # Database analysis
            db_info = self.performance_data.get('database', {})
            if db_info:
                print(f"  Database Size: {db_info.get('total_size', 0) / 1024 / 1024:.2f} MB")
                print(f"  Index Size: {db_info.get('index_size', 0) / 1024 / 1024:.2f} MB")
                print(f"  Collections: {db_info.get('collections', 0)}")
            
            # Cache analysis
            cache_info = self.performance_data.get('cache', {})
            if cache_info:
                print(f"  Cache Status: {cache_info.get('status', 'Unknown')}")
                print(f"  Cache Mode: {cache_info.get('mode', 'Unknown')}")
            
            # Optimizations status
            optimizations = self.performance_data.get('optimizations', {})
            if optimizations:
                print("  Optimizations:")
                for key, value in optimizations.items():
                    print(f"    {key}: {value}")
        
        print()

    def run_comprehensive_performance_testing(self):
        """Run the complete performance testing suite"""
        print("=" * 80)
        print("CATALORO MARKETPLACE - COMPREHENSIVE PERFORMANCE TESTING")
        print("Identifying performance bottlenecks causing system slowness")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Authentication Performance
        print("🔐 AUTHENTICATION PERFORMANCE TESTING")
        print("-" * 50)
        admin_auth_ok = self.test_admin_authentication()
        self.test_demo_user_authentication()
        
        if not admin_auth_ok:
            print("❌ Admin authentication failed. Some tests may be limited.")
        
        # 2. API Health & Performance Metrics
        print("🏥 API HEALTH & PERFORMANCE METRICS")
        print("-" * 50)
        self.test_api_health_and_performance_metrics()
        
        # 3. Database Performance Analysis
        print("🗄️ DATABASE PERFORMANCE ANALYSIS")
        print("-" * 50)
        self.test_database_performance_analysis()
        
        # 4. Critical Endpoints Performance
        print("⚡ CRITICAL ENDPOINTS PERFORMANCE")
        print("-" * 50)
        self.test_critical_endpoints_performance()
        
        # 5. Concurrent Load Handling
        print("🔄 CONCURRENT LOAD HANDLING")
        print("-" * 50)
        self.test_concurrent_load_handling()
        
        # 6. Memory & Resource Usage
        print("💾 MEMORY & RESOURCE USAGE")
        print("-" * 50)
        self.test_memory_and_resource_usage()
        
        # 7. Error Detection & Logging
        print("🔍 ERROR DETECTION & LOGGING")
        print("-" * 50)
        self.test_error_detection_and_logging()
        
        # 8. Performance Analysis
        self.analyze_performance_bottlenecks()
        
        # Print Summary
        print("=" * 80)
        print("COMPREHENSIVE PERFORMANCE TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        # Critical issues summary
        critical_failures = [r for r in self.test_results if not r["status"].startswith("✅") and r.get("is_critical")]
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES: {len(critical_failures)}")
            for result in critical_failures:
                print(f"  - {result['test']}: {result['error']}")
        
        # Performance summary
        print(f"\n📊 PERFORMANCE SUMMARY:")
        print(f"  Bottlenecks Identified: {len(self.bottlenecks)}")
        print(f"  Optimization Recommendations: {len(self.optimization_recommendations)}")
        
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["status"].startswith("✅"):
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 PERFORMANCE TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results, self.bottlenecks, self.optimization_recommendations

if __name__ == "__main__":
    tester = ComprehensivePerformanceTester()
    
    print("🎯 RUNNING COMPREHENSIVE PERFORMANCE TESTING")
    print("Analyzing system performance and identifying bottlenecks...")
    print()
    
    result = tester.run_comprehensive_performance_testing()
    if result:
        passed, failed, results, bottlenecks, recommendations = result
        # Exit with appropriate code
        exit(0 if failed == 0 else 1)
    else:
        exit(1)