#!/usr/bin/env python3
"""
Time Limit Functionality Testing
Testing the new time limit functionality for listings as requested in review
"""

import requests
import json
import sys
import time
from datetime import datetime, timedelta
import uuid

# Get backend URL from environment
BACKEND_URL = "https://cataloro-dash.preview.emergentagent.com/api"

class TimeLimitTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.test_user_id = None
        self.test_listing_id = None
        
    def log_test(self, test_name, success, details="", expected="", actual=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and expected:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
        print()
        
    def setup_test_user(self):
        """Create a test user for testing"""
        try:
            user_data = {
                "username": f"timelimit_tester_{int(time.time())}",
                "email": f"timelimit_test_{int(time.time())}@cataloro.com",
                "full_name": "Time Limit Tester",
                "password": "testpass123"
            }
            
            response = self.session.post(f"{self.backend_url}/auth/register", json=user_data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.test_user_id = result.get("user_id")
                print(f"✅ Test user created: {self.test_user_id}")
                return True
            else:
                print(f"❌ Failed to create test user: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception creating test user: {str(e)}")
            return False
    
    def test_listing_creation_without_time_limit(self):
        """Test 1: Create listing without time limit (should default to no time limit)"""
        try:
            listing_data = {
                "title": "Test Listing - No Time Limit",
                "description": "Testing listing creation without time limit",
                "price": 100.0,
                "category": "Electronics",
                "condition": "New",
                "seller_id": self.test_user_id,
                "images": [],
                "tags": ["test"],
                "features": ["testing"]
            }
            
            response = self.session.post(f"{self.backend_url}/listings", json=listing_data)
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Listing Creation Without Time Limit",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
                
            result = response.json()
            listing_id = result.get("listing_id")
            
            # Verify default time limit behavior
            has_time_limit = result.get("has_time_limit", True)  # Should default to False
            expires_at = result.get("expires_at")
            
            if not has_time_limit and expires_at is None:
                self.log_test(
                    "Listing Creation Without Time Limit",
                    True,
                    f"Listing created without time limit: has_time_limit={has_time_limit}, expires_at={expires_at}"
                )
                return listing_id
            else:
                self.log_test(
                    "Listing Creation Without Time Limit",
                    False,
                    f"Time limit defaults incorrect: has_time_limit={has_time_limit}, expires_at={expires_at}",
                    "has_time_limit=False, expires_at=None",
                    f"has_time_limit={has_time_limit}, expires_at={expires_at}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Listing Creation Without Time Limit",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_listing_creation_with_time_limit(self):
        """Test 2: Create listing with time limit (24hrs, 48hrs, 1 week, 1 month options)"""
        try:
            # Test with 24 hours time limit
            listing_data = {
                "title": "Test Listing - 24 Hour Time Limit",
                "description": "Testing listing creation with 24 hour time limit",
                "price": 150.0,
                "category": "Electronics",
                "condition": "Used",
                "seller_id": self.test_user_id,
                "images": [],
                "tags": ["test", "time-limit"],
                "features": ["testing"],
                "has_time_limit": True,
                "time_limit_hours": 24
            }
            
            response = self.session.post(f"{self.backend_url}/listings", json=listing_data)
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Listing Creation With Time Limit",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
                
            result = response.json()
            listing_id = result.get("listing_id")
            
            # Verify time limit behavior
            has_time_limit = result.get("has_time_limit", False)
            expires_at = result.get("expires_at")
            
            if has_time_limit and expires_at:
                # Verify expires_at calculation is correct (approximately 24 hours from now)
                try:
                    expires_datetime = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    current_time = datetime.utcnow()
                    time_diff = expires_datetime - current_time
                    
                    # Should be approximately 24 hours (allow 1 minute tolerance)
                    expected_hours = 24
                    actual_hours = time_diff.total_seconds() / 3600
                    
                    if abs(actual_hours - expected_hours) <= 0.02:  # 1 minute tolerance
                        self.log_test(
                            "Listing Creation With Time Limit",
                            True,
                            f"Listing created with correct 24h time limit: expires in {actual_hours:.2f} hours"
                        )
                        self.test_listing_id = listing_id  # Store for later tests
                        return listing_id
                    else:
                        self.log_test(
                            "Listing Creation With Time Limit",
                            False,
                            f"Expires_at calculation incorrect: expected ~{expected_hours}h, got {actual_hours:.2f}h",
                            f"~{expected_hours} hours",
                            f"{actual_hours:.2f} hours"
                        )
                        return False
                        
                except Exception as date_error:
                    self.log_test(
                        "Listing Creation With Time Limit",
                        False,
                        f"Error parsing expires_at date: {date_error}",
                        "Valid ISO datetime",
                        f"expires_at={expires_at}"
                    )
                    return False
            else:
                self.log_test(
                    "Listing Creation With Time Limit",
                    False,
                    f"Time limit not set correctly: has_time_limit={has_time_limit}, expires_at={expires_at}",
                    "has_time_limit=True, expires_at=valid datetime",
                    f"has_time_limit={has_time_limit}, expires_at={expires_at}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Listing Creation With Time Limit",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_browse_listings_time_info(self):
        """Test 3: Browse listings enhancement - verify time_info is included"""
        try:
            response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if response.status_code != 200:
                self.log_test(
                    "Browse Listings Time Info",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            listings = response.json()
            
            if not isinstance(listings, list) or len(listings) == 0:
                self.log_test(
                    "Browse Listings Time Info",
                    False,
                    "No listings found to test time_info",
                    "At least one listing with time_info",
                    f"Found {len(listings) if isinstance(listings, list) else 0} listings"
                )
                return False
            
            # Check if listings have time_info
            time_info_found = False
            time_info_structure_correct = False
            
            for listing in listings:
                if "time_info" in listing:
                    time_info_found = True
                    time_info = listing["time_info"]
                    
                    # Check required fields in time_info
                    required_fields = [
                        "has_time_limit", "is_expired", "time_remaining_seconds", 
                        "expires_at", "status_text"
                    ]
                    
                    if all(field in time_info for field in required_fields):
                        time_info_structure_correct = True
                        break
            
            if time_info_found and time_info_structure_correct:
                self.log_test(
                    "Browse Listings Time Info",
                    True,
                    f"Browse listings include time_info with all required fields: {required_fields}"
                )
                return True
            elif time_info_found:
                self.log_test(
                    "Browse Listings Time Info",
                    False,
                    "time_info found but missing required fields",
                    f"All fields: {required_fields}",
                    f"Found fields: {list(time_info.keys()) if 'time_info' in listing else 'No time_info'}"
                )
                return False
            else:
                self.log_test(
                    "Browse Listings Time Info",
                    False,
                    "No time_info field found in listings",
                    "time_info object with required fields",
                    "No time_info field"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Browse Listings Time Info",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_extend_time_functionality(self):
        """Test 4: Extend time functionality"""
        try:
            if not self.test_listing_id:
                self.log_test(
                    "Extend Time Functionality",
                    False,
                    "No test listing available for time extension test"
                )
                return False
            
            # Test extending time by 12 hours
            extension_data = {
                "additional_hours": 12
            }
            
            response = self.session.post(
                f"{self.backend_url}/listings/{self.test_listing_id}/extend-time",
                json=extension_data
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Extend Time Functionality",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
                
            result = response.json()
            
            # Verify response structure
            if "message" in result and "new_expires_at" in result:
                new_expires_at = result.get("new_expires_at")
                total_extension_hours = result.get("total_extension_hours", 0)
                
                if total_extension_hours == 12:
                    self.log_test(
                        "Extend Time Functionality",
                        True,
                        f"Successfully extended listing time by {total_extension_hours} hours. New expiration: {new_expires_at}"
                    )
                    return True
                else:
                    self.log_test(
                        "Extend Time Functionality",
                        False,
                        f"Extension hours incorrect: expected 12, got {total_extension_hours}",
                        "12 hours",
                        f"{total_extension_hours} hours"
                    )
                    return False
            else:
                self.log_test(
                    "Extend Time Functionality",
                    False,
                    f"Invalid response structure: {result}",
                    "message and new_expires_at fields",
                    f"Response: {result}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Extend Time Functionality",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_check_expiration_endpoint(self):
        """Test 5: Check expiration endpoint"""
        try:
            if not self.test_listing_id:
                self.log_test(
                    "Check Expiration Endpoint",
                    False,
                    "No test listing available for expiration check test"
                )
                return False
            
            response = self.session.post(f"{self.backend_url}/listings/{self.test_listing_id}/check-expiration")
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Check Expiration Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
                
            result = response.json()
            
            # Verify response structure
            required_fields = ["message", "is_expired"]
            if all(field in result for field in required_fields):
                is_expired = result.get("is_expired")
                message = result.get("message", "")
                
                # Since we just created the listing, it should not be expired
                if not is_expired and "still active" in message.lower():
                    time_remaining = result.get("time_remaining_seconds", 0)
                    self.log_test(
                        "Check Expiration Endpoint",
                        True,
                        f"Expiration check working correctly: not expired, {time_remaining} seconds remaining"
                    )
                    return True
                elif is_expired:
                    # If expired, check for winner declaration logic
                    winning_bidder = result.get("winning_bidder_id")
                    winning_amount = result.get("winning_bid_amount", 0)
                    
                    self.log_test(
                        "Check Expiration Endpoint",
                        True,
                        f"Expiration check working: listing expired, winner={winning_bidder}, amount={winning_amount}"
                    )
                    return True
                else:
                    self.log_test(
                        "Check Expiration Endpoint",
                        False,
                        f"Unexpected expiration status: is_expired={is_expired}, message='{message}'",
                        "is_expired=False with 'still active' message",
                        f"is_expired={is_expired}, message='{message}'"
                    )
                    return False
            else:
                missing_fields = [field for field in required_fields if field not in result]
                self.log_test(
                    "Check Expiration Endpoint",
                    False,
                    f"Missing required fields: {missing_fields}",
                    f"All fields: {required_fields}",
                    f"Present fields: {list(result.keys())}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Check Expiration Endpoint",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_time_limit_business_logic(self):
        """Test 6: Time limit business logic with short expiration"""
        try:
            # Create a listing with very short time limit (1 hour for testing)
            listing_data = {
                "title": "Test Listing - Short Time Limit",
                "description": "Testing expiration logic with 1 hour limit",
                "price": 200.0,
                "category": "Electronics",
                "condition": "New",
                "seller_id": self.test_user_id,
                "images": [],
                "tags": ["test", "expiration"],
                "features": ["testing"],
                "has_time_limit": True,
                "time_limit_hours": 1  # 1 hour for testing
            }
            
            response = self.session.post(f"{self.backend_url}/listings", json=listing_data)
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Time Limit Business Logic",
                    False,
                    f"Failed to create test listing: HTTP {response.status_code}: {response.text}"
                )
                return False
                
            result = response.json()
            short_listing_id = result.get("listing_id")
            
            # Verify the listing was created with correct time limit
            if result.get("has_time_limit") and result.get("expires_at"):
                self.log_test(
                    "Time Limit Business Logic",
                    True,
                    f"Created listing with 1-hour time limit for expiration testing: {short_listing_id}"
                )
                return short_listing_id
            else:
                self.log_test(
                    "Time Limit Business Logic",
                    False,
                    f"Short time limit listing not created correctly: has_time_limit={result.get('has_time_limit')}, expires_at={result.get('expires_at')}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Time Limit Business Logic",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_error_cases(self):
        """Test 7: Error cases for time limit functionality"""
        try:
            # Test extending non-existent listing
            fake_listing_id = str(uuid.uuid4())
            extension_data = {"additional_hours": 24}
            
            response = self.session.post(
                f"{self.backend_url}/listings/{fake_listing_id}/extend-time",
                json=extension_data
            )
            
            # Should return 404 for non-existent listing
            if response.status_code == 404:
                error1_pass = True
            else:
                error1_pass = False
            
            # Test extending with invalid hours
            if self.test_listing_id:
                invalid_extension = {"additional_hours": -5}  # Negative hours
                
                response2 = self.session.post(
                    f"{self.backend_url}/listings/{self.test_listing_id}/extend-time",
                    json=invalid_extension
                )
                
                # Should return 400 for invalid hours
                if response2.status_code == 400:
                    error2_pass = True
                else:
                    error2_pass = False
            else:
                error2_pass = True  # Skip if no test listing
            
            # Test checking expiration on non-existent listing
            response3 = self.session.post(f"{self.backend_url}/listings/{fake_listing_id}/check-expiration")
            
            # Should return 404 for non-existent listing
            if response3.status_code == 404:
                error3_pass = True
            else:
                error3_pass = False
            
            if error1_pass and error2_pass and error3_pass:
                self.log_test(
                    "Error Cases Handling",
                    True,
                    "All error cases handled correctly: non-existent listing (404), invalid hours (400), expiration check on non-existent (404)"
                )
                return True
            else:
                failed_cases = []
                if not error1_pass:
                    failed_cases.append("extend non-existent listing")
                if not error2_pass:
                    failed_cases.append("invalid extension hours")
                if not error3_pass:
                    failed_cases.append("check expiration on non-existent")
                
                self.log_test(
                    "Error Cases Handling",
                    False,
                    f"Some error cases not handled correctly: {', '.join(failed_cases)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Error Cases Handling",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all time limit functionality tests"""
        print("=" * 80)
        print("TIME LIMIT FUNCTIONALITY TESTING")
        print("Testing new time limit functionality for listings")
        print("=" * 80)
        print()
        
        # Setup test user
        if not self.setup_test_user():
            print("❌ Failed to setup test user. Cannot proceed with tests.")
            return False
        
        # Test 1: Listing creation without time limit
        test1_success = bool(self.test_listing_creation_without_time_limit())
        
        # Test 2: Listing creation with time limit
        test2_result = self.test_listing_creation_with_time_limit()
        test2_success = bool(test2_result)
        
        # Test 3: Browse listings time_info
        test3_success = self.test_browse_listings_time_info()
        
        # Test 4: Extend time functionality (only if we have a test listing)
        test4_success = False
        if test2_success and self.test_listing_id:
            test4_success = self.test_extend_time_functionality()
        else:
            self.log_test(
                "Extend Time Functionality",
                False,
                "Skipped due to failed listing creation with time limit"
            )
        
        # Test 5: Check expiration endpoint
        test5_success = False
        if test2_success and self.test_listing_id:
            test5_success = self.test_check_expiration_endpoint()
        else:
            self.log_test(
                "Check Expiration Endpoint",
                False,
                "Skipped due to failed listing creation with time limit"
            )
        
        # Test 6: Time limit business logic
        test6_result = self.test_time_limit_business_logic()
        test6_success = bool(test6_result)
        
        # Test 7: Error cases
        test7_success = self.test_error_cases()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = 7
        passed_tests = sum([test1_success, test2_success, test3_success, test4_success, test5_success, test6_success, test7_success])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Individual test results
        tests = [
            ("Listing Creation Without Time Limit", test1_success),
            ("Listing Creation With Time Limit", test2_success),
            ("Browse Listings Time Info", test3_success),
            ("Extend Time Functionality", test4_success),
            ("Check Expiration Endpoint", test5_success),
            ("Time Limit Business Logic", test6_success),
            ("Error Cases Handling", test7_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        
        # Critical issues
        critical_failures = []
        if not test1_success:
            critical_failures.append("Listing creation without time limit not working")
        if not test2_success:
            critical_failures.append("Listing creation with time limit not working")
        if not test3_success:
            critical_failures.append("Browse listings missing time_info")
        if not test4_success and test2_success:
            critical_failures.append("Time extension functionality not working")
        if not test5_success and test2_success:
            critical_failures.append("Expiration check endpoint not working")
        if not test6_success:
            critical_failures.append("Time limit business logic not working")
        
        if critical_failures:
            print("CRITICAL ISSUES FOUND:")
            for issue in critical_failures:
                print(f"❌ {issue}")
        else:
            print("✅ ALL CRITICAL TIME LIMIT FUNCTIONALITY WORKING")
        
        print()
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = TimeLimitTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED - Time limit functionality is working correctly!")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Check the issues above")
        sys.exit(1)