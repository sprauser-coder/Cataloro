#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Phase 2 Search Comprehensive Testing
Additional comprehensive tests for search and discovery features
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://marketplace-central.preview.emergentagent.com/api"

class ComprehensiveSearchTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
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
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def test_search_edge_cases(self):
        """Test search with edge cases and special characters"""
        try:
            test_cases = [
                ("", "empty query"),
                ("   ", "whitespace query"),
                ("a", "single character"),
                ("test@#$%", "special characters"),
                ("very long search query that might exceed normal limits and test system robustness", "very long query")
            ]
            
            passed_cases = 0
            total_cases = len(test_cases)
            
            for query, description in test_cases:
                try:
                    response = requests.get(f"{BACKEND_URL}/marketplace/search", params={"q": query})
                    if response.status_code == 200:
                        data = response.json()
                        results_count = len(data.get("results", []))
                        passed_cases += 1
                        print(f"      ✓ {description}: {results_count} results")
                    else:
                        print(f"      ✗ {description}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"      ✗ {description}: {str(e)}")
            
            success_rate = (passed_cases / total_cases) * 100
            self.log_test(
                "Search Edge Cases",
                passed_cases == total_cases,
                f"Passed {passed_cases}/{total_cases} edge cases ({success_rate:.1f}%)"
            )
            return passed_cases == total_cases
            
        except Exception as e:
            self.log_test(
                "Search Edge Cases",
                False,
                error_msg=f"Test execution failed: {str(e)}"
            )
            return False

    def test_search_pagination_comprehensive(self):
        """Test search pagination with various parameters"""
        try:
            # Test different page sizes
            pagination_tests = [
                (1, 5),   # Small page
                (1, 10),  # Medium page
                (1, 20),  # Large page
                (2, 10),  # Second page
                (1, 50),  # Very large page
            ]
            
            passed_tests = 0
            total_tests = len(pagination_tests)
            
            for page, limit in pagination_tests:
                try:
                    response = requests.get(f"{BACKEND_URL}/marketplace/search", params={
                        "page": page,
                        "limit": limit
                    })
                    
                    if response.status_code == 200:
                        data = response.json()
                        returned_count = len(data.get("results", []))
                        expected_max = min(limit, data.get("total", 0))
                        
                        # For page 2+, we might get fewer results
                        if page > 1:
                            expected_max = min(limit, max(0, data.get("total", 0) - (page - 1) * limit))
                        
                        if returned_count <= limit:
                            passed_tests += 1
                            print(f"      ✓ Page {page}, Limit {limit}: {returned_count} results (≤{limit})")
                        else:
                            print(f"      ✗ Page {page}, Limit {limit}: {returned_count} results (>{limit})")
                    else:
                        print(f"      ✗ Page {page}, Limit {limit}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"      ✗ Page {page}, Limit {limit}: {str(e)}")
            
            success_rate = (passed_tests / total_tests) * 100
            self.log_test(
                "Search Pagination Comprehensive",
                passed_tests == total_tests,
                f"Passed {passed_tests}/{total_tests} pagination tests ({success_rate:.1f}%)"
            )
            return passed_tests == total_tests
            
        except Exception as e:
            self.log_test(
                "Search Pagination Comprehensive",
                False,
                error_msg=f"Test execution failed: {str(e)}"
            )
            return False

    def test_search_sorting_options(self):
        """Test all search sorting options"""
        try:
            sort_options = [
                "relevance",
                "price_low", 
                "price_high",
                "newest",
                "oldest"
            ]
            
            passed_sorts = 0
            total_sorts = len(sort_options)
            
            for sort_by in sort_options:
                try:
                    response = requests.get(f"{BACKEND_URL}/marketplace/search", params={
                        "q": "test",
                        "sort_by": sort_by,
                        "limit": 5
                    })
                    
                    if response.status_code == 200:
                        data = response.json()
                        results_count = len(data.get("results", []))
                        passed_sorts += 1
                        print(f"      ✓ Sort by {sort_by}: {results_count} results")
                    else:
                        print(f"      ✗ Sort by {sort_by}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"      ✗ Sort by {sort_by}: {str(e)}")
            
            success_rate = (passed_sorts / total_sorts) * 100
            self.log_test(
                "Search Sorting Options",
                passed_sorts == total_sorts,
                f"Passed {passed_sorts}/{total_sorts} sorting options ({success_rate:.1f}%)"
            )
            return passed_sorts == total_sorts
            
        except Exception as e:
            self.log_test(
                "Search Sorting Options",
                False,
                error_msg=f"Test execution failed: {str(e)}"
            )
            return False

    def test_search_filter_combinations(self):
        """Test various filter combinations"""
        try:
            filter_combinations = [
                {"category": "Electronics"},
                {"price_min": 10, "price_max": 100},
                {"condition": "New"},
                {"category": "Electronics", "price_min": 20},
                {"category": "Automotive", "condition": "Used"},
                {"price_min": 0, "price_max": 50, "condition": "New"}
            ]
            
            passed_filters = 0
            total_filters = len(filter_combinations)
            
            for filters in filter_combinations:
                try:
                    response = requests.get(f"{BACKEND_URL}/marketplace/search", params=filters)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results_count = len(data.get("results", []))
                        total_results = data.get("total", 0)
                        passed_filters += 1
                        
                        filter_desc = ", ".join([f"{k}={v}" for k, v in filters.items()])
                        print(f"      ✓ Filters ({filter_desc}): {results_count}/{total_results} results")
                    else:
                        filter_desc = ", ".join([f"{k}={v}" for k, v in filters.items()])
                        print(f"      ✗ Filters ({filter_desc}): HTTP {response.status_code}")
                        
                except Exception as e:
                    filter_desc = ", ".join([f"{k}={v}" for k, v in filters.items()])
                    print(f"      ✗ Filters ({filter_desc}): {str(e)}")
            
            success_rate = (passed_filters / total_filters) * 100
            self.log_test(
                "Search Filter Combinations",
                passed_filters == total_filters,
                f"Passed {passed_filters}/{total_filters} filter combinations ({success_rate:.1f}%)"
            )
            return passed_filters == total_filters
            
        except Exception as e:
            self.log_test(
                "Search Filter Combinations",
                False,
                error_msg=f"Test execution failed: {str(e)}"
            )
            return False

    def test_suggestions_various_queries(self):
        """Test search suggestions with various query types"""
        try:
            suggestion_queries = [
                "c",      # Single letter
                "ca",     # Two letters
                "cat",    # Three letters
                "ford",   # Brand name
                "test",   # Common word
                "xyz123", # Non-existent
            ]
            
            passed_suggestions = 0
            total_suggestions = len(suggestion_queries)
            
            for query in suggestion_queries:
                try:
                    response = requests.get(f"{BACKEND_URL}/marketplace/search/suggestions", params={"q": query})
                    
                    if response.status_code == 200:
                        data = response.json()
                        suggestions = data.get("suggestions", [])
                        source = data.get("source", "unknown")
                        passed_suggestions += 1
                        print(f"      ✓ Query '{query}': {len(suggestions)} suggestions ({source})")
                    else:
                        print(f"      ✗ Query '{query}': HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"      ✗ Query '{query}': {str(e)}")
            
            success_rate = (passed_suggestions / total_suggestions) * 100
            self.log_test(
                "Search Suggestions Various Queries",
                passed_suggestions == total_suggestions,
                f"Passed {passed_suggestions}/{total_suggestions} suggestion queries ({success_rate:.1f}%)"
            )
            return passed_suggestions == total_suggestions
            
        except Exception as e:
            self.log_test(
                "Search Suggestions Various Queries",
                False,
                error_msg=f"Test execution failed: {str(e)}"
            )
            return False

    def test_similar_listings_multiple_ids(self):
        """Test similar listings with multiple listing IDs"""
        try:
            # Get some listing IDs first
            response = requests.get(f"{BACKEND_URL}/marketplace/browse?limit=5")
            
            if response.status_code != 200:
                self.log_test(
                    "Similar Listings Multiple IDs",
                    False,
                    error_msg="Could not fetch listings for testing"
                )
                return False
            
            listings = response.json()
            if not listings or len(listings) == 0:
                self.log_test(
                    "Similar Listings Multiple IDs",
                    False,
                    error_msg="No listings available for testing"
                )
                return False
            
            passed_similar = 0
            total_similar = min(3, len(listings))  # Test up to 3 listings
            
            for i in range(total_similar):
                listing_id = listings[i].get("id")
                if not listing_id:
                    continue
                    
                try:
                    response = requests.get(f"{BACKEND_URL}/marketplace/listings/{listing_id}/similar")
                    
                    if response.status_code == 200:
                        data = response.json()
                        similar_listings = data.get("similar_listings", [])
                        source = data.get("source", "unknown")
                        passed_similar += 1
                        print(f"      ✓ Listing {listing_id[:8]}...: {len(similar_listings)} similar ({source})")
                    else:
                        print(f"      ✗ Listing {listing_id[:8]}...: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"      ✗ Listing {listing_id[:8]}...: {str(e)}")
            
            success_rate = (passed_similar / total_similar) * 100 if total_similar > 0 else 0
            self.log_test(
                "Similar Listings Multiple IDs",
                passed_similar == total_similar,
                f"Passed {passed_similar}/{total_similar} similar listing tests ({success_rate:.1f}%)"
            )
            return passed_similar == total_similar
            
        except Exception as e:
            self.log_test(
                "Similar Listings Multiple IDs",
                False,
                error_msg=f"Test execution failed: {str(e)}"
            )
            return False

    def test_performance_response_times(self):
        """Test search performance and response times"""
        try:
            endpoints_to_test = [
                ("/marketplace/search", "Advanced Search"),
                ("/marketplace/search/suggestions?q=test", "Search Suggestions"),
                ("/marketplace/search/trending", "Trending Searches"),
                ("/admin/performance", "Performance Metrics")
            ]
            
            passed_performance = 0
            total_performance = len(endpoints_to_test)
            response_times = []
            
            for endpoint, name in endpoints_to_test:
                try:
                    start_time = time.time()
                    response = requests.get(f"{BACKEND_URL}{endpoint}")
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    response_times.append(response_time)
                    
                    if response.status_code == 200 and response_time < 5000:  # 5 second timeout
                        passed_performance += 1
                        print(f"      ✓ {name}: {response_time:.0f}ms")
                    else:
                        print(f"      ✗ {name}: {response_time:.0f}ms (status: {response.status_code})")
                        
                except Exception as e:
                    print(f"      ✗ {name}: {str(e)}")
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            success_rate = (passed_performance / total_performance) * 100
            
            self.log_test(
                "Search Performance Response Times",
                passed_performance == total_performance,
                f"Passed {passed_performance}/{total_performance} performance tests ({success_rate:.1f}%), Avg: {avg_response_time:.0f}ms"
            )
            return passed_performance == total_performance
            
        except Exception as e:
            self.log_test(
                "Search Performance Response Times",
                False,
                error_msg=f"Test execution failed: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all comprehensive search tests"""
        print("🔍 CATALORO PHASE 2 SEARCH COMPREHENSIVE TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # Test sequence
        tests = [
            self.test_search_edge_cases,
            self.test_search_pagination_comprehensive,
            self.test_search_sorting_options,
            self.test_search_filter_combinations,
            self.test_suggestions_various_queries,
            self.test_similar_listings_multiple_ids,
            self.test_performance_response_times
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                self.log_test(
                    test.__name__,
                    False,
                    error_msg=f"Test execution failed: {str(e)}"
                )
        
        # Print summary
        print("\n" + "=" * 70)
        print("🔍 PHASE 2 SEARCH COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        print()
        
        # Print failed tests details
        if self.failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌" in result["status"]:
                    print(f"   - {result['test']}: {result['error']}")
            print()
        
        print(f"Test Completed: {datetime.now().isoformat()}")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0,
            "test_results": self.test_results
        }

if __name__ == "__main__":
    tester = ComprehensiveSearchTester()
    results = tester.run_all_tests()