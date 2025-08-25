#!/usr/bin/env python3
"""
Backend Testing Script for Basic Listings Functionality
Focus: Test the basic listings functionality as requested in review:
1. GET /api/listings - Test basic listings endpoint without parameters
2. GET /api/listings?limit=10&skip=0 - Test with pagination parameters
3. GET /api/listings/count - Test count endpoint (fallback functionality)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ListingsBasicTester:
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
                self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, error=str(e))
            return False

    def test_basic_listings_endpoint(self):
        """Test GET /api/listings - basic listings endpoint without parameters"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings")
            
            if response.status_code == 200:
                listings = response.json()
                if isinstance(listings, list):
                    count = len(listings)
                    # Check if listings have required fields
                    sample_fields = []
                    if listings:
                        sample_listing = listings[0]
                        required_fields = ['id', 'title', 'description', 'price', 'category', 'status']
                        sample_fields = [field for field in required_fields if field in sample_listing]
                    
                    self.log_test(
                        "Basic Listings Endpoint", 
                        True, 
                        f"Retrieved {count} listings successfully. Sample fields: {sample_fields}"
                    )
                    return count, listings
                else:
                    self.log_test("Basic Listings Endpoint", False, error="Response is not a list")
                    return None, None
            else:
                self.log_test("Basic Listings Endpoint", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return None, None
                
        except Exception as e:
            self.log_test("Basic Listings Endpoint", False, error=str(e))
            return None, None

    def test_listings_with_pagination(self):
        """Test GET /api/listings?limit=10&skip=0 - listings with pagination parameters"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings?limit=10&skip=0")
            
            if response.status_code == 200:
                listings = response.json()
                if isinstance(listings, list):
                    count = len(listings)
                    # Should return at most 10 listings
                    if count <= 10:
                        self.log_test(
                            "Listings with Pagination (limit=10, skip=0)", 
                            True, 
                            f"Retrieved {count} listings (respecting limit=10)"
                        )
                        return count, listings
                    else:
                        self.log_test(
                            "Listings with Pagination (limit=10, skip=0)", 
                            False, 
                            error=f"Returned {count} listings, expected max 10"
                        )
                        return count, listings
                else:
                    self.log_test("Listings with Pagination (limit=10, skip=0)", False, error="Response is not a list")
                    return None, None
            else:
                self.log_test("Listings with Pagination (limit=10, skip=0)", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return None, None
                
        except Exception as e:
            self.log_test("Listings with Pagination (limit=10, skip=0)", False, error=str(e))
            return None, None

    def test_listings_count_endpoint(self):
        """Test GET /api/listings/count - count endpoint (fallback functionality)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings/count")
            
            if response.status_code == 200:
                data = response.json()
                if "total_count" in data:
                    count = data["total_count"]
                    if isinstance(count, int) and count >= 0:
                        self.log_test(
                            "Listings Count Endpoint", 
                            True, 
                            f"Successfully retrieved total count: {count}"
                        )
                        return count
                    else:
                        self.log_test("Listings Count Endpoint", False, error=f"Invalid count value: {count}")
                        return None
                else:
                    self.log_test("Listings Count Endpoint", False, error="Response missing 'total_count' field")
                    return None
            else:
                self.log_test("Listings Count Endpoint", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Listings Count Endpoint", False, error=str(e))
            return None

    def test_pagination_consistency(self, basic_count, paginated_count, total_count):
        """Test consistency between different endpoint results"""
        try:
            # If we have all the data, verify consistency
            if basic_count is not None and paginated_count is not None and total_count is not None:
                # Basic endpoint should return default number of listings (usually 20)
                # Paginated endpoint should return at most 10
                # Count endpoint should return total count
                
                consistency_checks = []
                
                # Check 1: Paginated count should be <= 10
                if paginated_count <= 10:
                    consistency_checks.append("✓ Pagination limit respected")
                else:
                    consistency_checks.append("✗ Pagination limit not respected")
                
                # Check 2: If total count > 0, we should get some listings
                if total_count > 0 and (basic_count > 0 or paginated_count > 0):
                    consistency_checks.append("✓ Non-zero count matches non-empty listings")
                elif total_count == 0 and basic_count == 0 and paginated_count == 0:
                    consistency_checks.append("✓ Zero count matches empty listings")
                else:
                    consistency_checks.append("✗ Count/listings mismatch")
                
                # Check 3: Basic count should be >= paginated count (unless basic has default limit)
                if basic_count >= paginated_count or basic_count == 20:  # 20 is common default
                    consistency_checks.append("✓ Basic vs paginated count relationship valid")
                else:
                    consistency_checks.append("✗ Unexpected count relationship")
                
                all_consistent = all("✓" in check for check in consistency_checks)
                
                self.log_test(
                    "Pagination Consistency Check", 
                    all_consistent, 
                    f"Checks: {', '.join(consistency_checks)}"
                )
                return all_consistent
            else:
                self.log_test("Pagination Consistency Check", False, error="Missing data for consistency check")
                return False
                
        except Exception as e:
            self.log_test("Pagination Consistency Check", False, error=str(e))
            return False

    def test_error_handling(self):
        """Test error handling for invalid parameters"""
        try:
            # Test invalid limit parameter
            response = self.session.get(f"{BACKEND_URL}/listings?limit=invalid")
            
            # Should handle gracefully (either 422 validation error or default behavior)
            if response.status_code in [200, 422]:
                self.log_test(
                    "Error Handling (Invalid Limit)", 
                    True, 
                    f"Handled invalid limit parameter gracefully (status: {response.status_code})"
                )
            else:
                self.log_test(
                    "Error Handling (Invalid Limit)", 
                    False, 
                    error=f"Unexpected status: {response.status_code}"
                )
                
            # Test negative skip parameter
            response = self.session.get(f"{BACKEND_URL}/listings?skip=-1")
            
            if response.status_code in [200, 422]:
                self.log_test(
                    "Error Handling (Negative Skip)", 
                    True, 
                    f"Handled negative skip parameter gracefully (status: {response.status_code})"
                )
            else:
                self.log_test(
                    "Error Handling (Negative Skip)", 
                    False, 
                    error=f"Unexpected status: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Error Handling Tests", False, error=str(e))

    def run_all_tests(self):
        """Run all basic listings functionality tests"""
        print("=" * 80)
        print("BASIC LISTINGS FUNCTIONALITY TESTING")
        print("Testing core listings endpoints after recent changes")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test basic listings endpoint
        basic_count, basic_listings = self.test_basic_listings_endpoint()
        
        # Step 3: Test listings with pagination
        paginated_count, paginated_listings = self.test_listings_with_pagination()
        
        # Step 4: Test count endpoint
        total_count = self.test_listings_count_endpoint()
        
        # Step 5: Test consistency between endpoints
        self.test_pagination_consistency(basic_count, paginated_count, total_count)
        
        # Step 6: Test error handling
        self.test_error_handling()
        
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
        
        # Show key metrics
        print("KEY METRICS:")
        print(f"• Basic listings endpoint: {basic_count if basic_count is not None else 'FAILED'} listings")
        print(f"• Paginated listings (limit=10): {paginated_count if paginated_count is not None else 'FAILED'} listings")
        print(f"• Total count endpoint: {total_count if total_count is not None else 'FAILED'} listings")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['error']}")
            print()
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = ListingsBasicTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED! Basic listings functionality is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED. Check the details above.")
        sys.exit(1)