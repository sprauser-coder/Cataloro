#!/usr/bin/env python3
"""
Time Limit Functionality Debug Testing
Debugging the time listing counter visibility issue as requested in review
"""

import requests
import json
import sys
import time
from datetime import datetime, timedelta

# Get backend URL from environment
BACKEND_URL = "https://cataloro-dash.preview.emergentagent.com/api"

class TimeLimitDebugTester:
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
        
    def test_check_existing_time_limited_listings(self):
        """Test 1: Check Current Listings for Time Limits"""
        try:
            response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if response.status_code != 200:
                self.log_test(
                    "Check Existing Time Limited Listings",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            listings = response.json()
            
            # Check for time-limited listings
            time_limited_listings = []
            for listing in listings:
                time_info = listing.get('time_info', {})
                if time_info.get('has_time_limit', False):
                    time_limited_listings.append({
                        'id': listing.get('id'),
                        'title': listing.get('title'),
                        'has_time_limit': time_info.get('has_time_limit'),
                        'is_expired': time_info.get('is_expired'),
                        'time_remaining_seconds': time_info.get('time_remaining_seconds'),
                        'status_text': time_info.get('status_text')
                    })
            
            if time_limited_listings:
                self.log_test(
                    "Check Existing Time Limited Listings",
                    True,
                    f"Found {len(time_limited_listings)} time-limited listings: {[l['title'] for l in time_limited_listings]}"
                )
                
                # Print detailed info for each time-limited listing
                print("   TIME-LIMITED LISTINGS DETAILS:")
                for listing in time_limited_listings:
                    print(f"     - {listing['title']} (ID: {listing['id']})")
                    print(f"       Has Time Limit: {listing['has_time_limit']}")
                    print(f"       Is Expired: {listing['is_expired']}")
                    print(f"       Time Remaining: {listing['time_remaining_seconds']} seconds")
                    print(f"       Status Text: {listing['status_text']}")
                print()
                
                return time_limited_listings
            else:
                self.log_test(
                    "Check Existing Time Limited Listings",
                    True,
                    f"No time-limited listings found in {len(listings)} total listings"
                )
                return []
                
        except Exception as e:
            self.log_test(
                "Check Existing Time Limited Listings",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_create_time_limited_listing(self):
        """Test 2: Create Test Listing with Time Limit"""
        try:
            # Create a test listing with 2-hour time limit for quick testing
            test_listing = {
                "title": "Time Limit Debug Test - Catalyst Unit",
                "description": "Test listing created for debugging time limit counter visibility",
                "price": 299.99,
                "category": "Automotive",
                "condition": "Used",
                "seller_id": "68b191ec38e6062fee10bd27",  # Admin user ID
                "images": [],
                "tags": ["test", "debug", "time-limit"],
                "features": ["Time Limited", "Debug Test"],
                "has_time_limit": True,
                "time_limit_hours": 2  # 2 hours for quick testing
            }
            
            response = self.session.post(
                f"{self.backend_url}/listings",
                json=test_listing,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Create Time Limited Listing",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
                
            result = response.json()
            listing_id = result.get("listing_id")
            
            if listing_id:
                self.test_listing_id = listing_id
                expires_at = result.get("expires_at")
                
                self.log_test(
                    "Create Time Limited Listing",
                    True,
                    f"Created test listing with ID: {listing_id}, expires at: {expires_at}"
                )
                return {
                    "listing_id": listing_id,
                    "expires_at": expires_at,
                    "has_time_limit": result.get("has_time_limit", False)
                }
            else:
                self.log_test(
                    "Create Time Limited Listing",
                    False,
                    f"No listing_id in response: {result}",
                    "listing_id field",
                    "Missing listing_id"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Create Time Limited Listing",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_browse_endpoint_time_info_analysis(self):
        """Test 3: Detailed Browse Endpoint Time Info Analysis"""
        try:
            response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if response.status_code != 200:
                self.log_test(
                    "Browse Endpoint Time Info Analysis",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
            listings = response.json()
            
            # Find our test listing if it exists
            test_listing = None
            if self.test_listing_id:
                for listing in listings:
                    if listing.get('id') == self.test_listing_id:
                        test_listing = listing
                        break
            
            if test_listing:
                time_info = test_listing.get('time_info', {})
                
                # Analyze time_info structure
                required_fields = ['has_time_limit', 'is_expired', 'time_remaining_seconds', 'expires_at', 'status_text']
                missing_fields = []
                present_fields = {}
                
                for field in required_fields:
                    if field in time_info:
                        present_fields[field] = time_info[field]
                    else:
                        missing_fields.append(field)
                
                if not missing_fields:
                    # Calculate expected time remaining
                    expires_at_str = time_info.get('expires_at')
                    if expires_at_str:
                        try:
                            expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                            current_time = datetime.utcnow()
                            expected_remaining = int((expires_at - current_time).total_seconds())
                            actual_remaining = time_info.get('time_remaining_seconds', 0)
                            
                            # Allow 5 second tolerance for calculation differences
                            time_diff = abs(expected_remaining - actual_remaining)
                            time_calculation_correct = time_diff <= 5
                            
                            self.log_test(
                                "Browse Endpoint Time Info Analysis",
                                True,
                                f"Complete time_info structure found. Time calculation accuracy: {time_diff}s difference"
                            )
                            
                            print("   TIME_INFO STRUCTURE DETAILS:")
                            for field, value in present_fields.items():
                                print(f"     {field}: {value}")
                            print(f"     Expected remaining: {expected_remaining}s")
                            print(f"     Actual remaining: {actual_remaining}s")
                            print(f"     Time calculation correct: {time_calculation_correct}")
                            print()
                            
                            return {
                                "time_info_complete": True,
                                "time_calculation_correct": time_calculation_correct,
                                "time_info": time_info,
                                "time_diff": time_diff
                            }
                        except Exception as time_error:
                            self.log_test(
                                "Browse Endpoint Time Info Analysis",
                                False,
                                f"Time calculation error: {str(time_error)}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Browse Endpoint Time Info Analysis",
                            False,
                            "expires_at field is missing or empty"
                        )
                        return False
                else:
                    self.log_test(
                        "Browse Endpoint Time Info Analysis",
                        False,
                        f"Missing required time_info fields: {', '.join(missing_fields)}",
                        f"All fields: {', '.join(required_fields)}",
                        f"Present fields: {', '.join(present_fields.keys())}"
                    )
                    return False
            else:
                self.log_test(
                    "Browse Endpoint Time Info Analysis",
                    False,
                    f"Test listing not found in browse results (ID: {self.test_listing_id})"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Browse Endpoint Time Info Analysis",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_data_structure_verification(self):
        """Test 4: Comprehensive Data Structure Verification"""
        try:
            response = self.session.get(f"{self.backend_url}/marketplace/browse")
            
            if response.status_code != 200:
                self.log_test(
                    "Data Structure Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
            listings = response.json()
            
            # Check all listings for proper time_info structure
            structure_issues = []
            time_limited_count = 0
            non_time_limited_count = 0
            
            for listing in listings:
                listing_id = listing.get('id', 'unknown')
                time_info = listing.get('time_info', {})
                
                # Every listing should have time_info
                if not time_info:
                    structure_issues.append(f"Listing {listing_id}: Missing time_info")
                    continue
                
                # Check has_time_limit field
                has_time_limit = time_info.get('has_time_limit')
                if has_time_limit is None:
                    structure_issues.append(f"Listing {listing_id}: Missing has_time_limit field")
                    continue
                
                if has_time_limit:
                    time_limited_count += 1
                    # For time-limited listings, check required fields
                    required_fields = ['is_expired', 'time_remaining_seconds', 'expires_at', 'status_text']
                    for field in required_fields:
                        if field not in time_info:
                            structure_issues.append(f"Listing {listing_id}: Missing {field} field")
                else:
                    non_time_limited_count += 1
                    # For non-time-limited listings, check expected structure
                    expected_values = {
                        'is_expired': False,
                        'time_remaining_seconds': None,
                        'expires_at': None,
                        'status_text': None
                    }
                    for field, expected_value in expected_values.items():
                        if field not in time_info:
                            structure_issues.append(f"Listing {listing_id}: Missing {field} field")
                        elif time_info[field] != expected_value:
                            structure_issues.append(f"Listing {listing_id}: {field} should be {expected_value}, got {time_info[field]}")
            
            if not structure_issues:
                self.log_test(
                    "Data Structure Verification",
                    True,
                    f"All {len(listings)} listings have proper time_info structure. Time-limited: {time_limited_count}, Non-time-limited: {non_time_limited_count}"
                )
                return {
                    "total_listings": len(listings),
                    "time_limited_count": time_limited_count,
                    "non_time_limited_count": non_time_limited_count,
                    "structure_valid": True
                }
            else:
                self.log_test(
                    "Data Structure Verification",
                    False,
                    f"Found {len(structure_issues)} structure issues",
                    "All listings with proper time_info structure",
                    f"Issues: {'; '.join(structure_issues[:5])}"  # Show first 5 issues
                )
                
                print("   STRUCTURE ISSUES FOUND:")
                for issue in structure_issues[:10]:  # Show first 10 issues
                    print(f"     - {issue}")
                if len(structure_issues) > 10:
                    print(f"     ... and {len(structure_issues) - 10} more issues")
                print()
                
                return False
                
        except Exception as e:
            self.log_test(
                "Data Structure Verification",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def cleanup_test_listing(self):
        """Clean up test listing after testing"""
        if self.test_listing_id:
            try:
                response = self.session.delete(f"{self.backend_url}/listings/{self.test_listing_id}")
                if response.status_code in [200, 204]:
                    print(f"✅ Cleaned up test listing: {self.test_listing_id}")
                else:
                    print(f"⚠️  Failed to clean up test listing: HTTP {response.status_code}")
            except Exception as e:
                print(f"⚠️  Error cleaning up test listing: {str(e)}")
    
    def run_debug_tests(self):
        """Run all time limit debug tests"""
        print("=" * 80)
        print("TIME LIMIT FUNCTIONALITY DEBUG TESTING")
        print("Debugging time listing counter visibility issue")
        print("=" * 80)
        print()
        
        # Test 1: Check existing time-limited listings
        existing_listings = self.test_check_existing_time_limited_listings()
        
        # Test 2: Create test listing with time limit
        test_listing_result = self.test_create_time_limited_listing()
        
        # Test 3: Analyze browse endpoint time_info
        time_info_analysis = self.test_browse_endpoint_time_info_analysis()
        
        # Test 4: Verify data structure
        structure_verification = self.test_data_structure_verification()
        
        # Summary
        print("=" * 80)
        print("DEBUG TEST SUMMARY")
        print("=" * 80)
        
        # Analyze findings
        print("FINDINGS:")
        print()
        
        if existing_listings is not False:
            if existing_listings:
                print(f"✅ Found {len(existing_listings)} existing time-limited listings")
                for listing in existing_listings:
                    status = "EXPIRED" if listing['is_expired'] else f"{listing['time_remaining_seconds']}s remaining"
                    print(f"   - {listing['title']}: {status}")
            else:
                print("⚠️  No existing time-limited listings found in system")
        else:
            print("❌ Failed to check existing listings")
        
        print()
        
        if test_listing_result:
            print(f"✅ Successfully created test listing: {test_listing_result['listing_id']}")
            print(f"   Expires at: {test_listing_result['expires_at']}")
        else:
            print("❌ Failed to create test listing")
        
        print()
        
        if time_info_analysis:
            print("✅ Browse endpoint returns proper time_info structure")
            if time_info_analysis.get('time_calculation_correct'):
                print("✅ Time calculations are accurate")
            else:
                print(f"⚠️  Time calculation has {time_info_analysis.get('time_diff', 'unknown')}s difference")
        else:
            print("❌ Browse endpoint time_info analysis failed")
        
        print()
        
        if structure_verification:
            print(f"✅ All {structure_verification['total_listings']} listings have proper structure")
            print(f"   Time-limited: {structure_verification['time_limited_count']}")
            print(f"   Non-time-limited: {structure_verification['non_time_limited_count']}")
        else:
            print("❌ Data structure verification failed")
        
        print()
        
        # Root cause analysis
        print("ROOT CAUSE ANALYSIS:")
        print()
        
        if existing_listings is not False and not existing_listings:
            print("🔍 POTENTIAL ISSUE: No time-limited listings exist in the system")
            print("   This could explain why users don't see time counters")
            print("   Recommendation: Check if users are creating time-limited listings")
        
        if not test_listing_result:
            print("🔍 CRITICAL ISSUE: Cannot create time-limited listings")
            print("   This would prevent any time counters from appearing")
            print("   Recommendation: Check listing creation endpoint")
        
        if not time_info_analysis:
            print("🔍 CRITICAL ISSUE: Browse endpoint not returning proper time_info")
            print("   This would prevent frontend from displaying counters")
            print("   Recommendation: Check browse endpoint time_info logic")
        
        if not structure_verification:
            print("🔍 CRITICAL ISSUE: Inconsistent time_info data structure")
            print("   This could cause frontend rendering issues")
            print("   Recommendation: Check time_info field population logic")
        
        # Clean up
        self.cleanup_test_listing()
        
        print()
        return True

if __name__ == "__main__":
    tester = TimeLimitDebugTester()
    tester.run_debug_tests()
    
    print("🔍 TIME LIMIT DEBUG TESTING COMPLETED")
    print("Check the findings above to identify the root cause of counter visibility issues")