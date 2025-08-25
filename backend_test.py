#!/usr/bin/env python3
"""
Backend Testing Script for Listings Count Endpoint
Focus: Test the fixed listings count endpoint with proper route ordering
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Authentication", True, f"Token: {self.admin_token[:20]}...")
                return True
            else:
                self.log_test("Admin Authentication", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, error=str(e))
            return False

    def test_listings_count_endpoint(self):
        """Test GET /api/listings/count endpoint"""
        try:
            # Test basic count endpoint
            response = self.session.get(f"{BACKEND_URL}/listings/count")
            
            if response.status_code == 200:
                data = response.json()
                if "total_count" in data:
                    count = data["total_count"]
                    self.log_test("Listings Count Endpoint", True, f"Total count: {count}")
                    return count
                else:
                    self.log_test("Listings Count Endpoint", False, error="Missing 'total_count' field in response")
                    return None
            else:
                self.log_test("Listings Count Endpoint", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Listings Count Endpoint", False, error=str(e))
            return None

    def test_listings_count_with_filters(self):
        """Test listings count with various filters"""
        filters_to_test = [
            {"category": "Electronics"},
            {"listing_type": "fixed_price"},
            {"listing_type": "auction"},
            {"search": "test"},
            {"min_price": 10},
            {"max_price": 100},
            {"min_price": 10, "max_price": 100}
        ]
        
        for filter_params in filters_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings/count", params=filter_params)
                
                if response.status_code == 200:
                    data = response.json()
                    if "total_count" in data:
                        count = data["total_count"]
                        filter_str = ", ".join([f"{k}={v}" for k, v in filter_params.items()])
                        self.log_test(f"Count with Filters ({filter_str})", True, f"Count: {count}")
                    else:
                        self.log_test(f"Count with Filters ({filter_str})", False, error="Missing 'total_count' field")
                else:
                    filter_str = ", ".join([f"{k}={v}" for k, v in filter_params.items()])
                    self.log_test(f"Count with Filters ({filter_str})", False, error=f"Status: {response.status_code}")
                    
            except Exception as e:
                filter_str = ", ".join([f"{k}={v}" for k, v in filter_params.items()])
                self.log_test(f"Count with Filters ({filter_str})", False, error=str(e))

    def get_actual_listings(self, limit=1000):
        """Get actual listings to verify count accuracy"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings", params={"limit": limit})
            
            if response.status_code == 200:
                listings = response.json()
                actual_count = len(listings)
                self.log_test("Get Actual Listings", True, f"Retrieved {actual_count} listings (limit: {limit})")
                return actual_count, listings
            else:
                self.log_test("Get Actual Listings", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return None, None
                
        except Exception as e:
            self.log_test("Get Actual Listings", False, error=str(e))
            return None, None

    def compare_counts(self, count_endpoint_result, actual_listings_count):
        """Compare count endpoint result with actual listings count"""
        if count_endpoint_result is not None and actual_listings_count is not None:
            if count_endpoint_result == actual_listings_count:
                self.log_test("Count Accuracy Verification", True, 
                            f"Count endpoint: {count_endpoint_result}, Actual listings: {actual_listings_count} - MATCH")
                return True
            else:
                self.log_test("Count Accuracy Verification", False, 
                            f"Count endpoint: {count_endpoint_result}, Actual listings: {actual_listings_count} - MISMATCH")
                return False
        else:
            self.log_test("Count Accuracy Verification", False, error="Unable to compare - missing data")
            return False

    def test_route_ordering_fix(self):
        """Test that route ordering fix works - specific listing ID should work"""
        try:
            # First get some listings to get a valid ID
            response = self.session.get(f"{BACKEND_URL}/listings", params={"limit": 1})
            
            if response.status_code == 200:
                listings = response.json()
                if listings:
                    listing_id = listings[0]["id"]
                    
                    # Test specific listing endpoint
                    response = self.session.get(f"{BACKEND_URL}/listings/{listing_id}")
                    
                    if response.status_code == 200:
                        listing_data = response.json()
                        self.log_test("Route Ordering Fix - Specific Listing", True, 
                                    f"Successfully retrieved listing: {listing_data.get('title', 'Unknown')}")
                        return True
                    else:
                        self.log_test("Route Ordering Fix - Specific Listing", False, 
                                    error=f"Status: {response.status_code}, Response: {response.text}")
                        return False
                else:
                    self.log_test("Route Ordering Fix - Specific Listing", False, error="No listings available to test")
                    return False
            else:
                self.log_test("Route Ordering Fix - Specific Listing", False, 
                            error=f"Failed to get listings: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Route Ordering Fix - Specific Listing", False, error=str(e))
            return False

    def test_count_endpoint_edge_cases(self):
        """Test edge cases for count endpoint"""
        edge_cases = [
            {"min_price": 0},  # Zero price
            {"max_price": 999999},  # Very high price
            {"search": "nonexistentproduct12345"},  # Search with no results
            {"category": "NonExistentCategory"},  # Invalid category
            {"listing_type": "invalid_type"},  # Invalid listing type
        ]
        
        for case in edge_cases:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings/count", params=case)
                
                # Should return 200 even for edge cases (with count 0 for no results)
                if response.status_code == 200:
                    data = response.json()
                    if "total_count" in data:
                        count = data["total_count"]
                        case_str = ", ".join([f"{k}={v}" for k, v in case.items()])
                        self.log_test(f"Edge Case ({case_str})", True, f"Count: {count}")
                    else:
                        self.log_test(f"Edge Case ({case_str})", False, error="Missing 'total_count' field")
                else:
                    case_str = ", ".join([f"{k}={v}" for k, v in case.items()])
                    # For invalid listing_type, 422 is acceptable
                    if response.status_code == 422 and "listing_type" in case:
                        self.log_test(f"Edge Case ({case_str})", True, "Correctly rejected invalid listing_type")
                    else:
                        self.log_test(f"Edge Case ({case_str})", False, 
                                    error=f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                case_str = ", ".join([f"{k}={v}" for k, v in case.items()])
                self.log_test(f"Edge Case ({case_str})", False, error=str(e))

    def run_all_tests(self):
        """Run all tests for listings count endpoint"""
        print("=" * 80)
        print("BACKEND TESTING: LISTINGS COUNT ENDPOINT WITH ROUTE ORDERING FIX")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test basic count endpoint
        count_result = self.test_listings_count_endpoint()
        
        # Step 3: Test count with filters
        self.test_listings_count_with_filters()
        
        # Step 4: Get actual listings for comparison
        actual_count, listings = self.get_actual_listings(1000)
        
        # Step 5: Compare counts
        self.compare_counts(count_result, actual_count)
        
        # Step 6: Test route ordering fix
        self.test_route_ordering_fix()
        
        # Step 7: Test edge cases
        self.test_count_endpoint_edge_cases()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['error']}")
            print()
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED! Listings count endpoint is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED. Check the details above.")
        sys.exit(1)
"""
Backend Testing Script for Listings Count Endpoint
Testing the fixed listings count endpoint (route ordering issue resolved)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Failed to authenticate: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_listings_count_no_filters(self):
        """Test GET /api/listings/count - total count of all active listings"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings/count")
            
            if response.status_code == 200:
                data = response.json()
                if "total_count" in data:
                    count = data["total_count"]
                    self.log_test(
                        "Listings Count (No Filters)", 
                        True, 
                        f"Successfully retrieved total count: {count} active listings",
                        {"total_count": count, "response": data}
                    )
                    return count
                else:
                    self.log_test("Listings Count (No Filters)", False, "Response missing 'total_count' field", data)
                    return None
            else:
                self.log_test("Listings Count (No Filters)", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Listings Count (No Filters)", False, f"Request error: {str(e)}")
            return None

    def test_listings_count_with_category_filter(self):
        """Test GET /api/listings/count?category=Electronics - count with category filter"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings/count?category=Electronics")
            
            if response.status_code == 200:
                data = response.json()
                if "total_count" in data:
                    count = data["total_count"]
                    self.log_test(
                        "Listings Count (Electronics Filter)", 
                        True, 
                        f"Successfully retrieved Electronics count: {count} listings",
                        {"category": "Electronics", "total_count": count, "response": data}
                    )
                    return count
                else:
                    self.log_test("Listings Count (Electronics Filter)", False, "Response missing 'total_count' field", data)
                    return None
            else:
                self.log_test("Listings Count (Electronics Filter)", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Listings Count (Electronics Filter)", False, f"Request error: {str(e)}")
            return None

    def test_listings_actual_count(self):
        """Test GET /api/listings - get actual listings to verify count accuracy"""
        try:
            # Get all listings with a high limit to ensure we get everything
            response = self.session.get(f"{BACKEND_URL}/listings?limit=1000")
            
            if response.status_code == 200:
                listings = response.json()
                total_listings = len(listings)
                
                # Count Electronics listings
                electronics_listings = [l for l in listings if l.get("category") == "Electronics"]
                electronics_count = len(electronics_listings)
                
                self.log_test(
                    "Actual Listings Retrieval", 
                    True, 
                    f"Retrieved {total_listings} total listings, {electronics_count} Electronics listings",
                    {
                        "total_listings": total_listings,
                        "electronics_count": electronics_count,
                        "sample_categories": list(set([l.get("category", "Unknown") for l in listings[:10]]))
                    }
                )
                return total_listings, electronics_count
            else:
                self.log_test("Actual Listings Retrieval", False, f"HTTP {response.status_code}: {response.text}")
                return None, None
                
        except Exception as e:
            self.log_test("Actual Listings Retrieval", False, f"Request error: {str(e)}")
            return None, None

    def verify_count_accuracy(self, count_total, count_electronics, actual_total, actual_electronics):
        """Verify that count endpoint returns accurate counts"""
        if count_total is None or actual_total is None:
            self.log_test("Count Accuracy Verification", False, "Missing data for verification")
            return False
            
        total_match = count_total == actual_total
        electronics_match = count_electronics == actual_electronics
        
        if total_match and electronics_match:
            self.log_test(
                "Count Accuracy Verification", 
                True, 
                f"Count endpoint accuracy verified: Total={count_total}, Electronics={count_electronics}",
                {
                    "count_endpoint_total": count_total,
                    "actual_listings_total": actual_total,
                    "count_endpoint_electronics": count_electronics,
                    "actual_listings_electronics": actual_electronics
                }
            )
            return True
        else:
            self.log_test(
                "Count Accuracy Verification", 
                False, 
                f"Count mismatch - Total: {count_total} vs {actual_total}, Electronics: {count_electronics} vs {actual_electronics}",
                {
                    "count_endpoint_total": count_total,
                    "actual_listings_total": actual_total,
                    "count_endpoint_electronics": count_electronics,
                    "actual_listings_electronics": actual_electronics,
                    "total_match": total_match,
                    "electronics_match": electronics_match
                }
            )
            return False

    def test_route_ordering_fix(self):
        """Test that the route ordering fix works - count endpoint should not conflict with {listing_id}"""
        try:
            # Test that /listings/count works (should not be interpreted as listing_id="count")
            count_response = self.session.get(f"{BACKEND_URL}/listings/count")
            
            # Test that /listings/{actual_id} still works
            # First get a real listing ID
            listings_response = self.session.get(f"{BACKEND_URL}/listings?limit=1")
            
            if listings_response.status_code == 200 and count_response.status_code == 200:
                listings = listings_response.json()
                count_data = count_response.json()
                
                if listings and "total_count" in count_data:
                    # Test accessing a real listing by ID
                    listing_id = listings[0]["id"]
                    listing_response = self.session.get(f"{BACKEND_URL}/listings/{listing_id}")
                    
                    if listing_response.status_code == 200:
                        listing_data = listing_response.json()
                        self.log_test(
                            "Route Ordering Fix Verification", 
                            True, 
                            "Both /listings/count and /listings/{id} work correctly - route ordering fixed",
                            {
                                "count_endpoint_works": True,
                                "count_response": count_data,
                                "listing_id_endpoint_works": True,
                                "tested_listing_id": listing_id,
                                "listing_title": listing_data.get("title", "Unknown")
                            }
                        )
                        return True
                    else:
                        self.log_test("Route Ordering Fix Verification", False, f"Listing by ID failed: {listing_response.status_code}")
                        return False
                else:
                    self.log_test("Route Ordering Fix Verification", False, "No listings found or count endpoint failed")
                    return False
            else:
                self.log_test("Route Ordering Fix Verification", False, f"Count: {count_response.status_code}, Listings: {listings_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Route Ordering Fix Verification", False, f"Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all listings count endpoint tests"""
        print("=" * 80)
        print("LISTINGS COUNT ENDPOINT TESTING")
        print("Testing the fixed listings count endpoint (route ordering issue resolved)")
        print("=" * 80)
        print()
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Test 1: Get total count of all active listings
        count_total = self.test_listings_count_no_filters()
        
        # Test 2: Get count with category filter
        count_electronics = self.test_listings_count_with_category_filter()
        
        # Test 3: Get actual listings to verify count accuracy
        actual_total, actual_electronics = self.test_listings_actual_count()
        
        # Test 4: Verify count accuracy
        accuracy_verified = self.verify_count_accuracy(count_total, count_electronics, actual_total, actual_electronics)
        
        # Test 5: Verify route ordering fix
        route_ordering_fixed = self.test_route_ordering_fix()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Listings count endpoint is working correctly!")
            print("✅ Route ordering issue has been resolved")
            print("✅ Count endpoint returns accurate counts")
            print("✅ Category filtering works properly")
        else:
            print("⚠️  Some tests failed - see details above")
            
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)