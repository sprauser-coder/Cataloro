#!/usr/bin/env python3
"""
Time Limit Edge Cases and Integration Testing
Additional comprehensive testing for edge scenarios
"""

import requests
import json
import sys
import time
from datetime import datetime, timedelta
import uuid

# Get backend URL from environment
BACKEND_URL = "https://cataloro-ads.preview.emergentagent.com/api"

class TimeLimitEdgeCasesTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.test_user_id = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
        
    def setup_test_user(self):
        """Create a test user for testing"""
        try:
            user_data = {
                "username": f"edge_tester_{int(time.time())}",
                "email": f"edge_test_{int(time.time())}@example.com",
                "full_name": "Edge Case Tester",
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
    
    def test_different_time_limits(self):
        """Test creating listings with different time limit durations"""
        try:
            if not self.test_user_id:
                return False
            
            time_limits = [24, 48, 168, 720]  # 24h, 48h, 1week, 1month
            results = []
            
            for hours in time_limits:
                listing_data = {
                    "title": f"Test Listing - {hours}h Time Limit",
                    "description": f"Testing {hours} hour time limit",
                    "price": 300.0 + hours,  # Different prices
                    "category": "Automotive Catalysts",
                    "condition": "Used - Good",
                    "seller_id": self.test_user_id,
                    "has_time_limit": True,
                    "time_limit_hours": hours,
                    "images": [],
                    "tags": ["test", f"{hours}h-limit"]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/listings",
                    json=listing_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    expires_at = result.get("expires_at")
                    
                    if expires_at:
                        # Verify expiration time calculation
                        expires_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        expected_time = datetime.utcnow() + timedelta(hours=hours)
                        time_diff = abs((expires_time - expected_time).total_seconds())
                        
                        if time_diff < 300:  # Within 5 minutes tolerance
                            results.append(f"{hours}h ✅")
                        else:
                            results.append(f"{hours}h ❌ (diff: {time_diff}s)")
                    else:
                        results.append(f"{hours}h ❌ (no expires_at)")
                else:
                    results.append(f"{hours}h ❌ (HTTP {response.status_code})")
            
            success_count = len([r for r in results if "✅" in r])
            
            if success_count == len(time_limits):
                self.log_test(
                    "Different Time Limits",
                    True,
                    f"All time limits working: {', '.join(results)}"
                )
                return True
            else:
                self.log_test(
                    "Different Time Limits",
                    False,
                    f"Some time limits failed: {', '.join(results)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Different Time Limits",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_non_time_limited_listings(self):
        """Test that non-time-limited listings have proper time_info structure"""
        try:
            if not self.test_user_id:
                return False
            
            # Create regular listing without time limit
            listing_data = {
                "title": "Regular Listing - No Time Limit",
                "description": "Testing regular listing without time constraints",
                "price": 450.0,
                "category": "Automotive Catalysts",
                "condition": "New",
                "seller_id": self.test_user_id,
                "has_time_limit": False,
                "images": [],
                "tags": ["test", "no-time-limit"]
            }
            
            response = self.session.post(
                f"{self.backend_url}/listings",
                json=listing_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Non-Time-Limited Listings",
                    False,
                    f"Failed to create listing: HTTP {response.status_code}"
                )
                return False
            
            result = response.json()
            listing_id = result.get("listing_id")
            
            # Check browse endpoint for time_info structure
            browse_response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if browse_response.status_code != 200:
                self.log_test(
                    "Non-Time-Limited Listings",
                    False,
                    f"Browse endpoint failed: HTTP {browse_response.status_code}"
                )
                return False
            
            listings = browse_response.json()
            
            # Find our test listing
            test_listing = None
            for listing in listings:
                if listing.get("id") == listing_id:
                    test_listing = listing
                    break
            
            if not test_listing:
                self.log_test(
                    "Non-Time-Limited Listings",
                    False,
                    "Test listing not found in browse results"
                )
                return False
            
            # Verify time_info structure for non-time-limited listing
            time_info = test_listing.get("time_info", {})
            
            expected_values = {
                "has_time_limit": False,
                "is_expired": False,
                "time_remaining_seconds": None,
                "expires_at": None,
                "status_text": None
            }
            
            mismatches = []
            for key, expected_value in expected_values.items():
                actual_value = time_info.get(key)
                if actual_value != expected_value:
                    mismatches.append(f"{key}: expected {expected_value}, got {actual_value}")
            
            if not mismatches:
                self.log_test(
                    "Non-Time-Limited Listings",
                    True,
                    "Non-time-limited listing has correct time_info structure"
                )
                return True
            else:
                self.log_test(
                    "Non-Time-Limited Listings",
                    False,
                    f"Time_info mismatches: {'; '.join(mismatches)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Non-Time-Limited Listings",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_extend_non_time_limited_listing(self):
        """Test error handling when trying to extend non-time-limited listing"""
        try:
            if not self.test_user_id:
                return False
            
            # Create regular listing without time limit
            listing_data = {
                "title": "Regular Listing for Extension Test",
                "description": "Testing extension error handling",
                "price": 350.0,
                "category": "Automotive Catalysts",
                "condition": "Used - Fair",
                "seller_id": self.test_user_id,
                "has_time_limit": False,
                "images": []
            }
            
            response = self.session.post(
                f"{self.backend_url}/listings",
                json=listing_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Extend Non-Time-Limited Listing",
                    False,
                    f"Failed to create listing: HTTP {response.status_code}"
                )
                return False
            
            result = response.json()
            listing_id = result.get("listing_id")
            
            # Try to extend the non-time-limited listing
            extension_data = {"additional_hours": 12}
            
            extend_response = self.session.post(
                f"{self.backend_url}/listings/{listing_id}/extend-time",
                json=extension_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 400 error
            if extend_response.status_code == 400:
                error_data = extend_response.json()
                error_detail = error_data.get("detail", "")
                
                if "time limit" in error_detail.lower():
                    self.log_test(
                        "Extend Non-Time-Limited Listing",
                        True,
                        f"Correctly rejected extension: {error_detail}"
                    )
                    return True
                else:
                    self.log_test(
                        "Extend Non-Time-Limited Listing",
                        False,
                        f"Wrong error message: {error_detail}"
                    )
                    return False
            else:
                self.log_test(
                    "Extend Non-Time-Limited Listing",
                    False,
                    f"Should have returned 400, got {extend_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Extend Non-Time-Limited Listing",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_time_display_formats(self):
        """Test time display formatting for different remaining times"""
        try:
            # This test checks the browse endpoint time formatting
            # by creating listings with different time limits and checking status_text
            
            browse_response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if browse_response.status_code != 200:
                self.log_test(
                    "Time Display Formats",
                    False,
                    f"Browse endpoint failed: HTTP {browse_response.status_code}"
                )
                return False
            
            listings = browse_response.json()
            
            # Find listings with time limits and check their status_text formatting
            time_limited_listings = [l for l in listings if l.get("time_info", {}).get("has_time_limit")]
            
            if not time_limited_listings:
                self.log_test(
                    "Time Display Formats",
                    True,
                    "No time-limited listings found to test formatting (acceptable)"
                )
                return True
            
            format_checks = []
            for listing in time_limited_listings[:3]:  # Check first 3
                time_info = listing.get("time_info", {})
                status_text = time_info.get("status_text", "")
                time_remaining = time_info.get("time_remaining_seconds", 0)
                
                # Check if status_text format is reasonable
                if time_remaining > 0:
                    # Should contain time units (h, m, s, d)
                    has_time_units = any(unit in status_text for unit in ['h', 'm', 's', 'd'])
                    if has_time_units:
                        format_checks.append(f"✅ {status_text}")
                    else:
                        format_checks.append(f"❌ {status_text} (no time units)")
                elif status_text == "EXPIRED":
                    format_checks.append(f"✅ {status_text}")
                else:
                    format_checks.append(f"❌ {status_text} (unexpected format)")
            
            success_count = len([c for c in format_checks if "✅" in c])
            
            if success_count == len(format_checks):
                self.log_test(
                    "Time Display Formats",
                    True,
                    f"All time formats correct: {'; '.join(format_checks)}"
                )
                return True
            else:
                self.log_test(
                    "Time Display Formats",
                    False,
                    f"Some formats incorrect: {'; '.join(format_checks)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Time Display Formats",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_integration_with_tenders(self):
        """Test time limit integration with tender/bidding system"""
        try:
            if not self.test_user_id:
                return False
            
            # Create time-limited listing
            listing_data = {
                "title": "Time Limited Tender Integration Test",
                "description": "Testing time limits with tender system",
                "price": 600.0,
                "category": "Automotive Catalysts",
                "condition": "Used - Good",
                "seller_id": self.test_user_id,
                "has_time_limit": True,
                "time_limit_hours": 48,  # 48 hours
                "images": []
            }
            
            response = self.session.post(
                f"{self.backend_url}/listings",
                json=listing_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Integration with Tenders",
                    False,
                    f"Failed to create listing: HTTP {response.status_code}"
                )
                return False
            
            result = response.json()
            listing_id = result.get("listing_id")
            
            # Submit a tender
            tender_data = {
                "listing_id": listing_id,
                "buyer_id": self.test_user_id,  # Using same user for simplicity
                "offer_amount": 650.0,
                "message": "Test tender for time limit integration"
            }
            
            tender_response = self.session.post(
                f"{self.backend_url}/tenders/submit",
                json=tender_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Check if tender was submitted (may fail due to same user, but that's OK)
            tender_success = tender_response.status_code in [200, 201]
            
            # Check browse endpoint to see if bid_info is properly integrated with time_info
            browse_response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if browse_response.status_code != 200:
                self.log_test(
                    "Integration with Tenders",
                    False,
                    f"Browse endpoint failed: HTTP {browse_response.status_code}"
                )
                return False
            
            listings = browse_response.json()
            
            # Find our test listing
            test_listing = None
            for listing in listings:
                if listing.get("id") == listing_id:
                    test_listing = listing
                    break
            
            if not test_listing:
                self.log_test(
                    "Integration with Tenders",
                    False,
                    "Test listing not found in browse results"
                )
                return False
            
            # Check that both time_info and bid_info are present
            time_info = test_listing.get("time_info", {})
            bid_info = test_listing.get("bid_info", {})
            
            has_time_info = time_info.get("has_time_limit", False)
            has_bid_structure = "has_bids" in bid_info
            
            if has_time_info and has_bid_structure:
                tender_status = "with tender" if tender_success else "without tender (expected)"
                self.log_test(
                    "Integration with Tenders",
                    True,
                    f"Time and bid info properly integrated {tender_status}"
                )
                return True
            else:
                self.log_test(
                    "Integration with Tenders",
                    False,
                    f"Missing info structures: time_info={has_time_info}, bid_info={has_bid_structure}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Integration with Tenders",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all edge case tests"""
        print("=" * 80)
        print("TIME LIMIT EDGE CASES AND INTEGRATION TESTING")
        print("Additional comprehensive testing for edge scenarios")
        print("=" * 80)
        print()
        
        # Setup
        setup_success = self.setup_test_user()
        if not setup_success:
            print("❌ Failed to setup test environment")
            return False
        
        # Run tests
        test1_success = self.test_different_time_limits()
        test2_success = self.test_non_time_limited_listings()
        test3_success = self.test_extend_non_time_limited_listing()
        test4_success = self.test_time_display_formats()
        test5_success = self.test_integration_with_tenders()
        
        # Summary
        print("=" * 80)
        print("EDGE CASES TEST SUMMARY")
        print("=" * 80)
        
        total_tests = 5
        passed_tests = sum([test1_success, test2_success, test3_success, test4_success, test5_success])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Individual test results
        tests = [
            ("Different Time Limits", test1_success),
            ("Non-Time-Limited Listings", test2_success),
            ("Extend Non-Time-Limited Listing", test3_success),
            ("Time Display Formats", test4_success),
            ("Integration with Tenders", test5_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = TimeLimitEdgeCasesTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL EDGE CASE TESTS PASSED!")
        sys.exit(0)
    else:
        print("⚠️  SOME EDGE CASE TESTS FAILED")
        sys.exit(1)