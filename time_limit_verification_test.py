#!/usr/bin/env python3
"""
Time Limit Functionality Verification Test
Quick verification test to ensure the time limit functionality is still working correctly after frontend changes
"""

import requests
import json
import sys
import time
from datetime import datetime, timedelta

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-3.preview.emergentagent.com/api"

class TimeLimitVerificationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
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
        
    def test_browse_endpoint_time_info(self):
        """Test 1: Verify Browse Endpoint Time Info Structure"""
        try:
            response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if response.status_code != 200:
                self.log_test(
                    "Browse Endpoint Time Info",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            listings = response.json()
            
            if not isinstance(listings, list):
                self.log_test(
                    "Browse Endpoint Time Info",
                    False,
                    "Response is not a list of listings",
                    "List of listings",
                    f"Type: {type(listings)}"
                )
                return False
            
            # Check if any listings have time_info structure
            time_info_found = False
            time_limited_listing = None
            
            for listing in listings:
                if 'time_info' in listing:
                    time_info_found = True
                    time_info = listing['time_info']
                    
                    # Verify time_info structure
                    required_fields = ['has_time_limit', 'is_expired', 'time_remaining_seconds', 'expires_at', 'status_text']
                    missing_fields = [field for field in required_fields if field not in time_info]
                    
                    if missing_fields:
                        self.log_test(
                            "Browse Endpoint Time Info",
                            False,
                            f"Missing time_info fields: {', '.join(missing_fields)}",
                            f"All fields: {', '.join(required_fields)}",
                            f"Present fields: {', '.join(time_info.keys())}"
                        )
                        return False
                    
                    # Check if this is a time-limited listing
                    if time_info.get('has_time_limit', False):
                        time_limited_listing = listing
                        break
            
            if not time_info_found:
                self.log_test(
                    "Browse Endpoint Time Info",
                    False,
                    "No listings found with time_info structure",
                    "At least one listing with time_info",
                    "No time_info found in any listing"
                )
                return False
            
            # Verify time calculations for time-limited listings
            if time_limited_listing:
                time_info = time_limited_listing['time_info']
                if time_info['has_time_limit'] and not time_info['is_expired']:
                    # Verify time calculation accuracy
                    expires_at_str = time_info['expires_at']
                    if expires_at_str:
                        try:
                            expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                            current_time = datetime.utcnow()
                            calculated_seconds = int((expires_at - current_time).total_seconds())
                            reported_seconds = time_info['time_remaining_seconds']
                            
                            # Allow 5 second tolerance for processing time
                            if abs(calculated_seconds - reported_seconds) <= 5:
                                self.log_test(
                                    "Browse Endpoint Time Info",
                                    True,
                                    f"Time calculations accurate. Reported: {reported_seconds}s, Calculated: {calculated_seconds}s"
                                )
                                return True
                            else:
                                self.log_test(
                                    "Browse Endpoint Time Info",
                                    False,
                                    f"Time calculation mismatch. Difference: {abs(calculated_seconds - reported_seconds)}s",
                                    f"Within 5 seconds tolerance",
                                    f"Reported: {reported_seconds}s, Calculated: {calculated_seconds}s"
                                )
                                return False
                        except Exception as time_error:
                            self.log_test(
                                "Browse Endpoint Time Info",
                                False,
                                f"Error parsing time: {str(time_error)}"
                            )
                            return False
            
            self.log_test(
                "Browse Endpoint Time Info",
                True,
                f"Browse endpoint returns proper time_info structure for {len(listings)} listings"
            )
            return True
                
        except Exception as e:
            self.log_test(
                "Browse Endpoint Time Info",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_listing_creation_with_time_limit(self):
        """Test 2: Test Listing Creation with Time Limits"""
        try:
            # Create a test listing with 24-hour time limit
            test_listing = {
                "title": "Time Limit Test - Premium Catalyst",
                "description": "Testing time limit functionality with 24-hour duration",
                "price": 750.0,
                "category": "Automotive",
                "condition": "Used",
                "seller_id": "test_seller_time_limit",
                "images": [],
                "tags": ["catalyst", "automotive", "time-limited"],
                "features": ["Premium grade", "Tested functionality"],
                "has_time_limit": True,
                "time_limit_hours": 24
            }
            
            response = self.session.post(
                f"{self.backend_url}/listings",
                json=test_listing,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Listing Creation with Time Limit",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
                
            result = response.json()
            
            # Verify response structure
            if "listing_id" not in result:
                self.log_test(
                    "Listing Creation with Time Limit",
                    False,
                    "No listing_id in response",
                    "listing_id field",
                    str(result.keys())
                )
                return False
            
            self.test_listing_id = result["listing_id"]
            
            # Verify time limit fields
            expected_fields = ["has_time_limit", "expires_at"]
            missing_fields = [field for field in expected_fields if field not in result]
            
            if missing_fields:
                self.log_test(
                    "Listing Creation with Time Limit",
                    False,
                    f"Missing time limit fields: {', '.join(missing_fields)}",
                    f"All fields: {', '.join(expected_fields)}",
                    f"Present fields: {', '.join(result.keys())}"
                )
                return False
            
            # Verify has_time_limit is set correctly
            if not result.get("has_time_limit", False):
                self.log_test(
                    "Listing Creation with Time Limit",
                    False,
                    "has_time_limit not set to True",
                    "True",
                    str(result.get("has_time_limit"))
                )
                return False
            
            # Verify expires_at is calculated correctly (should be ~24 hours from now)
            expires_at_str = result.get("expires_at")
            if expires_at_str:
                try:
                    expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                    current_time = datetime.utcnow()
                    time_diff_hours = (expires_at - current_time).total_seconds() / 3600
                    
                    # Should be approximately 24 hours (allow 1 minute tolerance)
                    if 23.98 <= time_diff_hours <= 24.02:
                        self.log_test(
                            "Listing Creation with Time Limit",
                            True,
                            f"Listing created with correct 24-hour expiration. Time diff: {time_diff_hours:.2f} hours"
                        )
                        return True
                    else:
                        self.log_test(
                            "Listing Creation with Time Limit",
                            False,
                            f"Incorrect expiration time calculation",
                            "~24 hours from now",
                            f"{time_diff_hours:.2f} hours from now"
                        )
                        return False
                except Exception as time_error:
                    self.log_test(
                        "Listing Creation with Time Limit",
                        False,
                        f"Error parsing expires_at: {str(time_error)}"
                    )
                    return False
            else:
                self.log_test(
                    "Listing Creation with Time Limit",
                    False,
                    "No expires_at field in response",
                    "expires_at timestamp",
                    "None"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Listing Creation with Time Limit",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_time_extension_functionality(self):
        """Test 3: Verify Time Extension Functionality"""
        try:
            if not self.test_listing_id:
                self.log_test(
                    "Time Extension Functionality",
                    False,
                    "No test listing available for extension test",
                    "Valid listing ID",
                    "None"
                )
                return False
            
            # Get current listing details before extension
            get_response = self.session.get(f"{self.backend_url}/listings/{self.test_listing_id}")
            if get_response.status_code != 200:
                self.log_test(
                    "Time Extension Functionality",
                    False,
                    f"Failed to get listing details: HTTP {get_response.status_code}",
                    "200 OK",
                    f"{get_response.status_code}"
                )
                return False
            
            original_listing = get_response.json()
            original_expires_at = original_listing.get("expires_at")
            
            if not original_expires_at:
                self.log_test(
                    "Time Extension Functionality",
                    False,
                    "Original listing has no expires_at field",
                    "expires_at timestamp",
                    "None"
                )
                return False
            
            # Extend time by 6 hours
            extension_data = {
                "additional_hours": 6
            }
            
            response = self.session.post(
                f"{self.backend_url}/listings/{self.test_listing_id}/extend-time",
                json=extension_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Time Extension Functionality",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
                
            result = response.json()
            
            # Verify response structure
            if "new_expires_at" not in result:
                self.log_test(
                    "Time Extension Functionality",
                    False,
                    "No new_expires_at in response",
                    "new_expires_at field",
                    str(result.keys())
                )
                return False
            
            new_expires_at = result["new_expires_at"]
            
            # Verify time extension calculation
            try:
                original_time = datetime.fromisoformat(original_expires_at.replace('Z', '+00:00'))
                new_time = datetime.fromisoformat(new_expires_at.replace('Z', '+00:00'))
                
                time_diff_hours = (new_time - original_time).total_seconds() / 3600
                
                # Should be exactly 6 hours (allow small tolerance for processing)
                if 5.98 <= time_diff_hours <= 6.02:
                    self.log_test(
                        "Time Extension Functionality",
                        True,
                        f"Time extended correctly by {time_diff_hours:.2f} hours"
                    )
                    return True
                else:
                    self.log_test(
                        "Time Extension Functionality",
                        False,
                        f"Incorrect time extension calculation",
                        "6 hours extension",
                        f"{time_diff_hours:.2f} hours extension"
                    )
                    return False
            except Exception as time_error:
                self.log_test(
                    "Time Extension Functionality",
                    False,
                    f"Error calculating time extension: {str(time_error)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Time Extension Functionality",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def cleanup_test_data(self):
        """Clean up test listing if created"""
        if self.test_listing_id:
            try:
                response = self.session.delete(f"{self.backend_url}/listings/{self.test_listing_id}")
                if response.status_code in [200, 204]:
                    print(f"✅ Cleaned up test listing: {self.test_listing_id}")
                else:
                    print(f"⚠️  Failed to clean up test listing: HTTP {response.status_code}")
            except Exception as e:
                print(f"⚠️  Error during cleanup: {str(e)}")
    
    def run_all_tests(self):
        """Run all time limit verification tests"""
        print("=" * 80)
        print("TIME LIMIT FUNCTIONALITY VERIFICATION TEST")
        print("Quick verification after frontend changes")
        print("=" * 80)
        print()
        
        # Test 1: Browse Endpoint Time Info
        test1_success = self.test_browse_endpoint_time_info()
        
        # Test 2: Listing Creation with Time Limits
        test2_success = self.test_listing_creation_with_time_limit()
        
        # Test 3: Time Extension Functionality
        test3_success = self.test_time_extension_functionality()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = 3
        passed_tests = sum([test1_success, test2_success, test3_success])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Individual test results
        tests = [
            ("Browse Endpoint Time Info", test1_success),
            ("Listing Creation with Time Limit", test2_success),
            ("Time Extension Functionality", test3_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        
        # Critical issues
        critical_failures = []
        if not test1_success:
            critical_failures.append("Browse endpoint time_info structure broken")
        if not test2_success:
            critical_failures.append("Listing creation with time limits not working")
        if not test3_success:
            critical_failures.append("Time extension functionality broken")
        
        if critical_failures:
            print("CRITICAL ISSUES FOUND:")
            for issue in critical_failures:
                print(f"❌ {issue}")
        else:
            print("✅ ALL TIME LIMIT FUNCTIONALITY WORKING CORRECTLY")
        
        print()
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = TimeLimitVerificationTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED - Time limit functionality is working correctly after frontend changes!")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Time limit functionality may have issues")
        sys.exit(1)