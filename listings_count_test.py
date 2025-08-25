#!/usr/bin/env python3
"""
Listings Count Endpoint Testing
Testing the new GET /api/listings/count endpoint to verify it returns correct total count.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ListingsCountTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })
    
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
                self.log_test("Admin Authentication", True, f"Successfully authenticated as admin")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Failed to authenticate: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_listings_count_no_filters(self):
        """Test GET /api/listings/count with no filters"""
        try:
            # Get count from count endpoint
            count_response = self.session.get(f"{BACKEND_URL}/listings/count")
            
            if count_response.status_code != 200:
                self.log_test("Listings Count - No Filters", False, 
                            f"Count endpoint failed: {count_response.status_code}")
                return False
            
            count_data = count_response.json()
            total_count = count_data.get("total_count", 0)
            
            # Get actual listings to verify count
            listings_response = self.session.get(f"{BACKEND_URL}/listings?limit=1000")
            
            if listings_response.status_code != 200:
                self.log_test("Listings Count - No Filters", False, 
                            f"Listings endpoint failed: {listings_response.status_code}")
                return False
            
            listings_data = listings_response.json()
            actual_count = len(listings_data)
            
            # Compare counts
            if total_count == actual_count:
                self.log_test("Listings Count - No Filters", True, 
                            f"Count matches: {total_count} listings found",
                            f"Count endpoint: {total_count}, Actual listings: {actual_count}")
                return True
            else:
                self.log_test("Listings Count - No Filters", False, 
                            f"Count mismatch: count endpoint returned {total_count}, but found {actual_count} actual listings")
                return False
                
        except Exception as e:
            self.log_test("Listings Count - No Filters", False, f"Error: {str(e)}")
            return False
    
    def test_listings_count_category_filter(self):
        """Test GET /api/listings/count with category filter"""
        try:
            category = "Electronics"
            
            # Get count from count endpoint with category filter
            count_response = self.session.get(f"{BACKEND_URL}/listings/count?category={category}")
            
            if count_response.status_code != 200:
                self.log_test("Listings Count - Category Filter", False, 
                            f"Count endpoint failed: {count_response.status_code}")
                return False
            
            count_data = count_response.json()
            total_count = count_data.get("total_count", 0)
            
            # Get actual listings with same category filter to verify count
            listings_response = self.session.get(f"{BACKEND_URL}/listings?category={category}&limit=1000")
            
            if listings_response.status_code != 200:
                self.log_test("Listings Count - Category Filter", False, 
                            f"Listings endpoint failed: {listings_response.status_code}")
                return False
            
            listings_data = listings_response.json()
            actual_count = len(listings_data)
            
            # Compare counts
            if total_count == actual_count:
                self.log_test("Listings Count - Category Filter", True, 
                            f"Category '{category}' count matches: {total_count} listings found",
                            f"Count endpoint: {total_count}, Actual listings: {actual_count}")
                return True
            else:
                self.log_test("Listings Count - Category Filter", False, 
                            f"Category '{category}' count mismatch: count endpoint returned {total_count}, but found {actual_count} actual listings")
                return False
                
        except Exception as e:
            self.log_test("Listings Count - Category Filter", False, f"Error: {str(e)}")
            return False
    
    def test_listings_count_search_filter(self):
        """Test GET /api/listings/count with search filter"""
        try:
            search_term = "test"
            
            # Get count from count endpoint with search filter
            count_response = self.session.get(f"{BACKEND_URL}/listings/count?search={search_term}")
            
            if count_response.status_code != 200:
                self.log_test("Listings Count - Search Filter", False, 
                            f"Count endpoint failed: {count_response.status_code}")
                return False
            
            count_data = count_response.json()
            total_count = count_data.get("total_count", 0)
            
            # Get actual listings with same search filter to verify count
            listings_response = self.session.get(f"{BACKEND_URL}/listings?search={search_term}&limit=1000")
            
            if listings_response.status_code != 200:
                self.log_test("Listings Count - Search Filter", False, 
                            f"Listings endpoint failed: {listings_response.status_code}")
                return False
            
            listings_data = listings_response.json()
            actual_count = len(listings_data)
            
            # Compare counts
            if total_count == actual_count:
                self.log_test("Listings Count - Search Filter", True, 
                            f"Search '{search_term}' count matches: {total_count} listings found",
                            f"Count endpoint: {total_count}, Actual listings: {actual_count}")
                return True
            else:
                self.log_test("Listings Count - Search Filter", False, 
                            f"Search '{search_term}' count mismatch: count endpoint returned {total_count}, but found {actual_count} actual listings")
                return False
                
        except Exception as e:
            self.log_test("Listings Count - Search Filter", False, f"Error: {str(e)}")
            return False
    
    def test_listings_count_multiple_filters(self):
        """Test GET /api/listings/count with multiple filters"""
        try:
            category = "Electronics"
            search_term = "phone"
            
            # Get count from count endpoint with multiple filters
            count_response = self.session.get(f"{BACKEND_URL}/listings/count?category={category}&search={search_term}")
            
            if count_response.status_code != 200:
                self.log_test("Listings Count - Multiple Filters", False, 
                            f"Count endpoint failed: {count_response.status_code}")
                return False
            
            count_data = count_response.json()
            total_count = count_data.get("total_count", 0)
            
            # Get actual listings with same filters to verify count
            listings_response = self.session.get(f"{BACKEND_URL}/listings?category={category}&search={search_term}&limit=1000")
            
            if listings_response.status_code != 200:
                self.log_test("Listings Count - Multiple Filters", False, 
                            f"Listings endpoint failed: {listings_response.status_code}")
                return False
            
            listings_data = listings_response.json()
            actual_count = len(listings_data)
            
            # Compare counts
            if total_count == actual_count:
                self.log_test("Listings Count - Multiple Filters", True, 
                            f"Multiple filters count matches: {total_count} listings found",
                            f"Count endpoint: {total_count}, Actual listings: {actual_count}")
                return True
            else:
                self.log_test("Listings Count - Multiple Filters", False, 
                            f"Multiple filters count mismatch: count endpoint returned {total_count}, but found {actual_count} actual listings")
                return False
                
        except Exception as e:
            self.log_test("Listings Count - Multiple Filters", False, f"Error: {str(e)}")
            return False
    
    def test_listings_count_edge_cases(self):
        """Test edge cases for listings count endpoint"""
        try:
            # Test with non-existent category
            count_response = self.session.get(f"{BACKEND_URL}/listings/count?category=NonExistentCategory")
            
            if count_response.status_code != 200:
                self.log_test("Listings Count - Edge Cases", False, 
                            f"Non-existent category test failed: {count_response.status_code}")
                return False
            
            count_data = count_response.json()
            total_count = count_data.get("total_count", 0)
            
            # Should return 0 for non-existent category
            if total_count == 0:
                self.log_test("Listings Count - Edge Cases", True, 
                            f"Non-existent category correctly returns 0 count")
            else:
                self.log_test("Listings Count - Edge Cases", False, 
                            f"Non-existent category should return 0, but returned {total_count}")
                return False
            
            # Test with empty search term
            count_response = self.session.get(f"{BACKEND_URL}/listings/count?search=")
            
            if count_response.status_code != 200:
                self.log_test("Listings Count - Edge Cases", False, 
                            f"Empty search test failed: {count_response.status_code}")
                return False
            
            # Empty search should return all listings (same as no filter)
            return True
                
        except Exception as e:
            self.log_test("Listings Count - Edge Cases", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all listings count tests"""
        print("=" * 60)
        print("LISTINGS COUNT ENDPOINT TESTING")
        print("=" * 60)
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Run all tests
        tests = [
            self.test_listings_count_no_filters,
            self.test_listings_count_category_filter,
            self.test_listings_count_search_filter,
            self.test_listings_count_multiple_filters,
            self.test_listings_count_edge_cases
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Summary
        print("=" * 60)
        print("LISTINGS COUNT TESTING SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL LISTINGS COUNT TESTS PASSED!")
        else:
            print("⚠️  Some listings count tests failed")
        
        return passed == total

def main():
    """Main function"""
    tester = ListingsCountTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Listings count endpoint is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Listings count endpoint has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()