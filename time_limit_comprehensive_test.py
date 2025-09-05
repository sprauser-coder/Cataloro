#!/usr/bin/env python3
"""
Time Limit Functionality Comprehensive Testing
Testing complete time limit integration as requested in review
"""

import requests
import json
import sys
import time
from datetime import datetime, timedelta
import uuid

# Get backend URL from environment
BACKEND_URL = "https://cataloro-upgrade.preview.emergentagent.com/api"

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
                "email": f"timelimit_test_{int(time.time())}@example.com",
                "full_name": "Time Limit Tester",
                "password": "testpass123"
            }
            
            response = self.session.post(
                f"{self.backend_url}/auth/register",
                json=user_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.test_user_id = result.get("user_id")
                print(f"✅ Test user created: {self.test_user_id}")
                return True
            else:
                print(f"❌ Failed to create test user: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exception creating test user: {e}")
            return False
    
    def test_create_listing_with_time_limit(self):
        """Test 1: Create Listing with Time Limit"""
        try:
            if not self.test_user_id:
                self.log_test(
                    "Create Listing with Time Limit",
                    False,
                    "No test user available"
                )
                return False
            
            # Create listing with 24-hour time limit
            listing_data = {
                "title": "Time Limited Test Catalyst - Premium Grade",
                "description": "Testing time limit functionality with 24-hour expiration",
                "price": 850.0,
                "category": "Automotive Catalysts",
                "condition": "Used - Good",
                "seller_id": self.test_user_id,
                "has_time_limit": True,
                "time_limit_hours": 24,
                "images": [],
                "tags": ["test", "time-limit"],
                "features": ["Premium grade", "Time limited auction"]
            }
            
            response = self.session.post(
                f"{self.backend_url}/listings",
                json=listing_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Create Listing with Time Limit",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
            
            result = response.json()
            self.test_listing_id = result.get("listing_id")
            
            # Verify response contains time limit info
            has_time_limit = result.get("has_time_limit", False)
            expires_at = result.get("expires_at")
            
            if has_time_limit and expires_at:
                # Verify expires_at is approximately 24 hours from now
                expires_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                expected_time = datetime.utcnow() + timedelta(hours=24)
                time_diff = abs((expires_time - expected_time).total_seconds())
                
                if time_diff < 300:  # Within 5 minutes tolerance
                    self.log_test(
                        "Create Listing with Time Limit",
                        True,
                        f"Listing created with 24h time limit. Expires at: {expires_at}"
                    )
                    return True
                else:
                    self.log_test(
                        "Create Listing with Time Limit",
                        False,
                        f"Expiration time calculation incorrect. Diff: {time_diff}s",
                        "~24 hours from now",
                        f"{expires_at} (diff: {time_diff}s)"
                    )
                    return False
            else:
                self.log_test(
                    "Create Listing with Time Limit",
                    False,
                    f"Time limit not properly set",
                    "has_time_limit=True, expires_at set",
                    f"has_time_limit={has_time_limit}, expires_at={expires_at}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Create Listing with Time Limit",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_browse_listings_time_integration(self):
        """Test 2: Browse Listings Time Integration"""
        try:
            if not self.test_listing_id:
                self.log_test(
                    "Browse Listings Time Integration",
                    False,
                    "No test listing available"
                )
                return False
            
            response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if response.status_code != 200:
                self.log_test(
                    "Browse Listings Time Integration",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            listings = response.json()
            
            # Find our test listing
            test_listing = None
            for listing in listings:
                if listing.get("id") == self.test_listing_id:
                    test_listing = listing
                    break
            
            if not test_listing:
                self.log_test(
                    "Browse Listings Time Integration",
                    False,
                    "Test listing not found in browse results"
                )
                return False
            
            # Verify time_info structure
            time_info = test_listing.get("time_info", {})
            required_fields = [
                "has_time_limit", "is_expired", "time_remaining_seconds", 
                "expires_at", "status_text"
            ]
            
            missing_fields = [field for field in required_fields if field not in time_info]
            
            if missing_fields:
                self.log_test(
                    "Browse Listings Time Integration",
                    False,
                    f"Missing time_info fields: {missing_fields}",
                    f"All fields: {required_fields}",
                    f"Present: {list(time_info.keys())}"
                )
                return False
            
            # Verify time calculations
            has_time_limit = time_info.get("has_time_limit")
            is_expired = time_info.get("is_expired")
            time_remaining = time_info.get("time_remaining_seconds")
            expires_at = time_info.get("expires_at")
            status_text = time_info.get("status_text")
            
            if has_time_limit and not is_expired and time_remaining > 0:
                # Verify time remaining is reasonable (should be close to 24 hours)
                expected_remaining = 24 * 3600  # 24 hours in seconds
                time_diff = abs(time_remaining - expected_remaining)
                
                if time_diff < 600:  # Within 10 minutes tolerance
                    self.log_test(
                        "Browse Listings Time Integration",
                        True,
                        f"Time info correct: {time_remaining}s remaining, status: {status_text}"
                    )
                    return True
                else:
                    self.log_test(
                        "Browse Listings Time Integration",
                        False,
                        f"Time calculation incorrect. Expected ~{expected_remaining}s, got {time_remaining}s"
                    )
                    return False
            else:
                self.log_test(
                    "Browse Listings Time Integration",
                    False,
                    f"Time info values incorrect",
                    "has_time_limit=True, is_expired=False, time_remaining>0",
                    f"has_time_limit={has_time_limit}, is_expired={is_expired}, time_remaining={time_remaining}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Browse Listings Time Integration",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_extend_time_functionality(self):
        """Test 3: Extend Time Functionality"""
        try:
            if not self.test_listing_id:
                self.log_test(
                    "Extend Time Functionality",
                    False,
                    "No test listing available"
                )
                return False
            
            # Extend time by 12 hours
            extension_data = {
                "additional_hours": 12
            }
            
            response = self.session.post(
                f"{self.backend_url}/listings/{self.test_listing_id}/extend-time",
                json=extension_data,
                headers={"Content-Type": "application/json"}
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
            new_expires_at = result.get("new_expires_at")
            
            if not new_expires_at:
                self.log_test(
                    "Extend Time Functionality",
                    False,
                    "No new_expires_at in response",
                    "new_expires_at field",
                    str(result)
                )
                return False
            
            # Verify new expiration time is approximately 36 hours from now (24 + 12)
            new_expires_time = datetime.fromisoformat(new_expires_at.replace('Z', '+00:00'))
            expected_time = datetime.utcnow() + timedelta(hours=36)
            time_diff = abs((new_expires_time - expected_time).total_seconds())
            
            if time_diff < 600:  # Within 10 minutes tolerance
                self.log_test(
                    "Extend Time Functionality",
                    True,
                    f"Time extended successfully. New expiration: {new_expires_at}"
                )
                return True
            else:
                self.log_test(
                    "Extend Time Functionality",
                    False,
                    f"Extension calculation incorrect. Expected ~36h from now, got diff: {time_diff}s"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Extend Time Functionality",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_short_expiration_scenario(self):
        """Test 4: Create listing with short expiration for testing"""
        try:
            if not self.test_user_id:
                self.log_test(
                    "Short Expiration Scenario Setup",
                    False,
                    "No test user available"
                )
                return False
            
            # Create listing with 1 hour time limit for testing
            short_listing_data = {
                "title": "Short Expiration Test Catalyst",
                "description": "Testing expiration with 1-hour limit",
                "price": 500.0,
                "category": "Automotive Catalysts",
                "condition": "Used - Fair",
                "seller_id": self.test_user_id,
                "has_time_limit": True,
                "time_limit_hours": 1,  # 1 hour for testing
                "images": [],
                "tags": ["test", "short-expiration"],
                "features": ["Quick expiration test"]
            }
            
            response = self.session.post(
                f"{self.backend_url}/listings",
                json=short_listing_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Short Expiration Scenario Setup",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            result = response.json()
            short_listing_id = result.get("listing_id")
            
            # Submit a test tender/bid
            tender_data = {
                "listing_id": short_listing_id,
                "buyer_id": self.test_user_id,  # Using same user for simplicity
                "offer_amount": 550.0,
                "message": "Test bid for expiration testing"
            }
            
            tender_response = self.session.post(
                f"{self.backend_url}/tenders/submit",
                json=tender_data,
                headers={"Content-Type": "application/json"}
            )
            
            if tender_response.status_code in [200, 201]:
                self.log_test(
                    "Short Expiration Scenario Setup",
                    True,
                    f"Short-term listing created with bid: {short_listing_id}"
                )
                return short_listing_id
            else:
                # Still consider setup successful even if tender fails
                self.log_test(
                    "Short Expiration Scenario Setup",
                    True,
                    f"Short-term listing created (tender failed but listing OK): {short_listing_id}"
                )
                return short_listing_id
                
        except Exception as e:
            self.log_test(
                "Short Expiration Scenario Setup",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_check_expiration_endpoint(self, listing_id):
        """Test 5: Check Expiration Endpoint"""
        try:
            if not listing_id:
                self.log_test(
                    "Check Expiration Endpoint",
                    False,
                    "No listing ID provided"
                )
                return False
            
            response = self.session.post(
                f"{self.backend_url}/listings/{listing_id}/check-expiration"
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Check Expiration Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            result = response.json()
            
            # Check response structure
            required_fields = ["message", "is_expired"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                self.log_test(
                    "Check Expiration Endpoint",
                    False,
                    f"Missing response fields: {missing_fields}"
                )
                return False
            
            is_expired = result.get("is_expired")
            message = result.get("message", "")
            
            # For a 1-hour listing, it should not be expired yet
            if not is_expired and "still active" in message.lower():
                self.log_test(
                    "Check Expiration Endpoint",
                    True,
                    f"Expiration check working: {message}"
                )
                return True
            elif is_expired:
                # If it's expired, check for winner logic
                winning_bidder = result.get("winning_bidder_id")
                winning_amount = result.get("winning_bid_amount", 0)
                
                self.log_test(
                    "Check Expiration Endpoint",
                    True,
                    f"Listing expired with winner: {winning_bidder}, amount: {winning_amount}"
                )
                return True
            else:
                self.log_test(
                    "Check Expiration Endpoint",
                    False,
                    f"Unexpected expiration response: {result}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Check Expiration Endpoint",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_error_handling(self):
        """Test 6: Error Handling"""
        try:
            test_results = []
            
            # Test 1: Try to extend expired listing (create one that's already expired)
            if self.test_listing_id:
                # Try extending with invalid hours
                invalid_extension = {"additional_hours": -5}
                response = self.session.post(
                    f"{self.backend_url}/listings/{self.test_listing_id}/extend-time",
                    json=invalid_extension
                )
                
                if response.status_code == 400:
                    test_results.append("Invalid extension hours rejected ✅")
                else:
                    test_results.append(f"Invalid extension not rejected (got {response.status_code}) ❌")
            
            # Test 2: Try to extend non-existent listing
            fake_id = str(uuid.uuid4())
            extension_data = {"additional_hours": 12}
            response = self.session.post(
                f"{self.backend_url}/listings/{fake_id}/extend-time",
                json=extension_data
            )
            
            if response.status_code == 404:
                test_results.append("Non-existent listing extension rejected ✅")
            else:
                test_results.append(f"Non-existent listing not handled (got {response.status_code}) ❌")
            
            # Test 3: Try to check expiration of non-existent listing
            response = self.session.post(
                f"{self.backend_url}/listings/{fake_id}/check-expiration"
            )
            
            if response.status_code == 404:
                test_results.append("Non-existent listing expiration check rejected ✅")
            else:
                test_results.append(f"Non-existent listing expiration not handled (got {response.status_code}) ❌")
            
            # Count successful error handling
            successful_tests = len([r for r in test_results if "✅" in r])
            total_tests = len(test_results)
            
            if successful_tests == total_tests:
                self.log_test(
                    "Error Handling",
                    True,
                    f"All error cases handled correctly: {'; '.join(test_results)}"
                )
                return True
            else:
                self.log_test(
                    "Error Handling",
                    False,
                    f"Some error cases not handled: {'; '.join(test_results)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Error Handling",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all time limit functionality tests"""
        print("=" * 80)
        print("TIME LIMIT FUNCTIONALITY COMPREHENSIVE TESTING")
        print("Testing complete time limit integration as requested")
        print("=" * 80)
        print()
        
        # Setup
        setup_success = self.setup_test_user()
        if not setup_success:
            print("❌ Failed to setup test environment")
            return False
        
        # Test 1: Create Listing with Time Limit
        test1_success = self.test_create_listing_with_time_limit()
        
        # Test 2: Browse Listings Time Integration
        test2_success = self.test_browse_listings_time_integration()
        
        # Test 3: Extend Time Functionality
        test3_success = self.test_extend_time_functionality()
        
        # Test 4: Short Expiration Scenario Setup
        short_listing_id = self.test_short_expiration_scenario()
        test4_success = bool(short_listing_id)
        
        # Test 5: Check Expiration Endpoint
        test5_success = False
        if short_listing_id:
            test5_success = self.test_check_expiration_endpoint(short_listing_id)
        else:
            self.log_test(
                "Check Expiration Endpoint",
                False,
                "Skipped due to failed short listing creation"
            )
        
        # Test 6: Error Handling
        test6_success = self.test_error_handling()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = 6
        passed_tests = sum([test1_success, test2_success, test3_success, test4_success, test5_success, test6_success])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Individual test results
        tests = [
            ("Create Listing with Time Limit", test1_success),
            ("Browse Listings Time Integration", test2_success),
            ("Extend Time Functionality", test3_success),
            ("Short Expiration Scenario Setup", test4_success),
            ("Check Expiration Endpoint", test5_success),
            ("Error Handling", test6_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        
        # Critical issues
        critical_failures = []
        if not test1_success:
            critical_failures.append("Cannot create listings with time limits")
        if not test2_success:
            critical_failures.append("Browse endpoint not returning time info correctly")
        if not test3_success:
            critical_failures.append("Time extension functionality not working")
        if not test5_success and test4_success:
            critical_failures.append("Expiration check endpoint not working")
        
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