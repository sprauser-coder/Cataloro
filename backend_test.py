#!/usr/bin/env python3
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