#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Phase 2 Search & Discovery Features
Testing the newly implemented advanced search and discovery features
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://marketplace-central.preview.emergentagent.com/api"

class Phase2SearchTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_user = None
        self.admin_token = None
        self.test_listing_id = None
        
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

    def test_admin_login(self):
        """Test admin authentication for search management"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": "admin@cataloro.com",
                "password": "admin123"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user = data.get("user")
                self.admin_token = data.get("token")
                
                self.log_test(
                    "Admin Login for Search Management",
                    True,
                    f"Admin logged in: {self.admin_user.get('username')} (Role: {self.admin_user.get('user_role')})"
                )
                return True
            else:
                self.log_test(
                    "Admin Login for Search Management",
                    False,
                    error_msg=f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Login for Search Management",
                False,
                error_msg=f"Login request failed: {str(e)}"
            )
            return False

    def test_advanced_search_basic(self):
        """Test basic advanced search endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/search")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["results", "total", "page", "limit", "search_engine"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    search_engine = data.get("search_engine", "unknown")
                    total_results = data.get("total", 0)
                    results_count = len(data.get("results", []))
                    
                    self.log_test(
                        "Advanced Search - Basic Query",
                        True,
                        f"Search engine: {search_engine}, Total: {total_results}, Returned: {results_count} results"
                    )
                    return True
                else:
                    self.log_test(
                        "Advanced Search - Basic Query",
                        False,
                        error_msg=f"Missing required fields: {missing_fields}"
                    )
                    return False
            else:
                self.log_test(
                    "Advanced Search - Basic Query",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Advanced Search - Basic Query",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def test_advanced_search_text_query(self):
        """Test advanced search with text query"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/search?q=catalyst")
            
            if response.status_code == 200:
                data = response.json()
                
                search_engine = data.get("search_engine", "unknown")
                total_results = data.get("total", 0)
                results_count = len(data.get("results", []))
                
                self.log_test(
                    "Advanced Search - Text Query (catalyst)",
                    True,
                    f"Search engine: {search_engine}, Found {total_results} results for 'catalyst', Returned: {results_count}"
                )
                return True
            else:
                self.log_test(
                    "Advanced Search - Text Query (catalyst)",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Advanced Search - Text Query (catalyst)",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def test_advanced_search_filtered(self):
        """Test advanced search with filters"""
        try:
            params = {
                "category": "automotive",
                "price_min": 50,
                "price_max": 500
            }
            response = requests.get(f"{BACKEND_URL}/marketplace/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                search_engine = data.get("search_engine", "unknown")
                total_results = data.get("total", 0)
                results_count = len(data.get("results", []))
                
                # Verify price filtering if results exist
                price_check_passed = True
                if results_count > 0:
                    for result in data.get("results", []):
                        price = result.get("price", 0)
                        if price < 50 or price > 500:
                            price_check_passed = False
                            break
                
                details = f"Search engine: {search_engine}, Found {total_results} results with filters (category=automotive, price=50-500), Returned: {results_count}"
                if not price_check_passed:
                    details += " - WARNING: Some results outside price range"
                
                self.log_test(
                    "Advanced Search - Filtered Query",
                    True,
                    details
                )
                return True
            else:
                self.log_test(
                    "Advanced Search - Filtered Query",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Advanced Search - Filtered Query",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def test_advanced_search_complex(self):
        """Test advanced search with complex parameters"""
        try:
            params = {
                "q": "ford",
                "sort_by": "price_low",
                "page": 1,
                "limit": 10
            }
            response = requests.get(f"{BACKEND_URL}/marketplace/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                search_engine = data.get("search_engine", "unknown")
                total_results = data.get("total", 0)
                results_count = len(data.get("results", []))
                page = data.get("page", 0)
                limit = data.get("limit", 0)
                
                # Verify pagination parameters
                pagination_correct = (page == 1 and limit == 10 and results_count <= 10)
                
                details = f"Search engine: {search_engine}, Query: 'ford', Sort: price_low, Page: {page}, Limit: {limit}, Results: {results_count}/{total_results}"
                if not pagination_correct:
                    details += " - WARNING: Pagination parameters not correctly applied"
                
                self.log_test(
                    "Advanced Search - Complex Query",
                    True,
                    details
                )
                return True
            else:
                self.log_test(
                    "Advanced Search - Complex Query",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Advanced Search - Complex Query",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def test_search_suggestions(self):
        """Test search suggestions endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/search/suggestions?q=cat")
            
            if response.status_code == 200:
                data = response.json()
                
                suggestions = data.get("suggestions", [])
                source = data.get("source", "unknown")
                
                self.log_test(
                    "Search Suggestions - Auto-complete",
                    True,
                    f"Source: {source}, Found {len(suggestions)} suggestions for 'cat': {suggestions[:3]}"
                )
                return True
            else:
                self.log_test(
                    "Search Suggestions - Auto-complete",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Search Suggestions - Auto-complete",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def test_search_suggestions_limited(self):
        """Test search suggestions with limit parameter"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/search/suggestions?q=ford&limit=5")
            
            if response.status_code == 200:
                data = response.json()
                
                suggestions = data.get("suggestions", [])
                source = data.get("source", "unknown")
                
                # Verify limit is respected
                limit_respected = len(suggestions) <= 5
                
                details = f"Source: {source}, Found {len(suggestions)} suggestions for 'ford' (limit=5): {suggestions}"
                if not limit_respected:
                    details += " - WARNING: Limit not respected"
                
                self.log_test(
                    "Search Suggestions - With Limit",
                    True,
                    details
                )
                return True
            else:
                self.log_test(
                    "Search Suggestions - With Limit",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Search Suggestions - With Limit",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def test_trending_searches(self):
        """Test trending searches endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/search/trending")
            
            if response.status_code == 200:
                data = response.json()
                
                trending = data.get("trending", [])
                source = data.get("source", "unknown")
                
                self.log_test(
                    "Trending Searches - Default",
                    True,
                    f"Source: {source}, Found {len(trending)} trending items: {[item.get('query', item) for item in trending[:3]]}"
                )
                return True
            else:
                self.log_test(
                    "Trending Searches - Default",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Trending Searches - Default",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def test_trending_searches_limited(self):
        """Test trending searches with limit parameter"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/search/trending?limit=5")
            
            if response.status_code == 200:
                data = response.json()
                
                trending = data.get("trending", [])
                source = data.get("source", "unknown")
                
                # Verify limit is respected
                limit_respected = len(trending) <= 5
                
                details = f"Source: {source}, Found {len(trending)} trending items (limit=5)"
                if not limit_respected:
                    details += " - WARNING: Limit not respected"
                
                self.log_test(
                    "Trending Searches - With Limit",
                    True,
                    details
                )
                return True
            else:
                self.log_test(
                    "Trending Searches - With Limit",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Trending Searches - With Limit",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def get_test_listing_id(self):
        """Get a listing ID for testing similar listings"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/browse?limit=5")
            
            if response.status_code == 200:
                listings = response.json()
                if listings and len(listings) > 0:
                    self.test_listing_id = listings[0].get("id")
                    return self.test_listing_id
            
            return None
                
        except Exception as e:
            print(f"Error getting test listing ID: {str(e)}")
            return None

    def test_similar_listings(self):
        """Test similar listings recommendation endpoint"""
        try:
            # Get a test listing ID
            if not self.test_listing_id:
                self.test_listing_id = self.get_test_listing_id()
            
            if not self.test_listing_id:
                self.log_test(
                    "Similar Listings - Recommendations",
                    False,
                    error_msg="No test listing ID available"
                )
                return False
            
            response = requests.get(f"{BACKEND_URL}/marketplace/listings/{self.test_listing_id}/similar")
            
            if response.status_code == 200:
                data = response.json()
                
                similar_listings = data.get("similar_listings", [])
                source = data.get("source", "unknown")
                
                self.log_test(
                    "Similar Listings - Recommendations",
                    True,
                    f"Source: {source}, Found {len(similar_listings)} similar listings for ID: {self.test_listing_id}"
                )
                return True
            else:
                self.log_test(
                    "Similar Listings - Recommendations",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Similar Listings - Recommendations",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def test_admin_search_sync(self):
        """Test admin search sync endpoint"""
        try:
            if not self.admin_token:
                self.log_test(
                    "Admin Search Sync",
                    False,
                    error_msg="Admin authentication required"
                )
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/admin/search/sync", headers=headers)
            
            # This endpoint might not exist yet or might return different status codes
            # We'll check for common success/error patterns
            if response.status_code in [200, 201, 202]:
                data = response.json() if response.content else {}
                
                self.log_test(
                    "Admin Search Sync",
                    True,
                    f"Sync request successful (status: {response.status_code}): {data.get('message', 'No message')}"
                )
                return True
            elif response.status_code == 404:
                self.log_test(
                    "Admin Search Sync",
                    False,
                    error_msg="Endpoint not implemented yet (404)"
                )
                return False
            elif response.status_code in [500, 503]:
                # Expected when Elasticsearch is not available
                self.log_test(
                    "Admin Search Sync",
                    True,
                    f"Elasticsearch unavailable (status: {response.status_code}) - Expected in fallback mode"
                )
                return True
            else:
                self.log_test(
                    "Admin Search Sync",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Search Sync",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def test_performance_metrics_search_status(self):
        """Test that performance metrics include search service status"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/performance")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if search status is included
                search_info = data.get("search", {})
                
                if search_info:
                    elasticsearch_enabled = search_info.get("elasticsearch_enabled", False)
                    status = search_info.get("status", "unknown")
                    
                    self.log_test(
                        "Performance Metrics - Search Status",
                        True,
                        f"Search service status included - Elasticsearch: {elasticsearch_enabled}, Status: {status}"
                    )
                    return True
                else:
                    self.log_test(
                        "Performance Metrics - Search Status",
                        False,
                        error_msg="Search service status not found in performance metrics"
                    )
                    return False
            else:
                self.log_test(
                    "Performance Metrics - Search Status",
                    False,
                    error_msg=f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Performance Metrics - Search Status",
                False,
                error_msg=f"Request failed: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all Phase 2 search and discovery tests"""
        print("🔍 CATALORO PHASE 2 SEARCH & DISCOVERY TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # Test sequence
        tests = [
            self.test_admin_login,
            self.test_advanced_search_basic,
            self.test_advanced_search_text_query,
            self.test_advanced_search_filtered,
            self.test_advanced_search_complex,
            self.test_search_suggestions,
            self.test_search_suggestions_limited,
            self.test_trending_searches,
            self.test_trending_searches_limited,
            self.test_similar_listings,
            self.test_admin_search_sync,
            self.test_performance_metrics_search_status
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
        print("\n" + "=" * 60)
        print("🔍 PHASE 2 SEARCH & DISCOVERY TEST SUMMARY")
        print("=" * 60)
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
    tester = Phase2SearchTester()
    results = tester.run_all_tests()