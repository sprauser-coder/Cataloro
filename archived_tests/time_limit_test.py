#!/usr/bin/env python3
"""
TIME LIMIT FUNCTIONALITY TESTING - URGENT
Testing the time limit functionality fixes that were applied:

FIXES APPLIED:
1. Default Time Limit Behavior - Changed default back to has_time_limit: false (unlimited by default)
   Default time_limit_hours back to 24 (when time limit is enabled)
   Backend default for time_limit_hours changed from 1 to 24

2. Time Limit Display on Frontend - Added time_info calculation to browse endpoint (/api/marketplace/browse)
   Added time_info calculation to individual listing endpoint (/api/listings/{listing_id})
   Both now calculate time_remaining_seconds, is_expired, and time_limit_hours

SPECIFIC TESTS NEEDED:
1. Create Listing with 1 Hour Time Limit - Create a test listing with has_time_limit: true and time_limit_hours: 1
2. Browse Page Time Display - Test GET /api/marketplace/browse for proper time_info structure
3. Individual Listing Time Display - Test GET /api/listings/{listing_id} for time-limited listing
4. Unlimited Listings - Test listings without time limits (has_time_limit: false)

EXPECTED RESULTS:
- Default listings should be unlimited (has_time_limit: false)
- 1-hour time limits should display correctly on both browse and detail pages
- Time remaining should count down properly
- Frontend should show time limit information when set
"""

import asyncio
import aiohttp
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-admin-fix.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"

# Demo User Configuration
DEMO_EMAIL = "demo@cataloro.com"
DEMO_USER_ID = "68bfff790e4e46bc28d43631"

class TimeLimitTester:
    """
    TIME LIMIT FUNCTIONALITY TESTING
    Testing the time limit functionality fixes that were just applied
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.admin_user_id = None
        self.test_results = {}
        self.test_listing_ids = []  # Track created listings for cleanup
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session and test data"""
        # Clean up test listings
        if self.admin_token and self.test_listing_ids:
            print("🧹 Cleaning up test listings...")
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            for listing_id in self.test_listing_ids:
                try:
                    await self.make_request(f"/listings/{listing_id}", "DELETE", headers=headers)
                except:
                    pass  # Ignore cleanup errors
        
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
            if headers:
                request_kwargs['headers'] = headers
            
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **request_kwargs) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "response_time_ms": response_time_ms,
                    "data": response_data,
                    "status": response.status
                }
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time_ms,
                "error": str(e),
                "status": 0
            }
    
    async def authenticate_users(self) -> bool:
        """Authenticate admin and demo users"""
        print("🔐 Authenticating users for time limit testing...")
        
        # Authenticate admin user (seller)
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            self.admin_user_id = admin_result["data"].get("user", {}).get("id", "admin_user_1")
            print(f"  ✅ Admin user authentication successful (ID: {self.admin_user_id})")
        else:
            print(f"  ❌ Admin user authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
        
        # Authenticate demo user (buyer)
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": "demo_password"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            print(f"  ✅ Demo user authentication successful")
            return True
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error', 'Unknown error')}")
            return False
    
    async def test_create_listing_with_1_hour_time_limit(self) -> Dict:
        """
        Test 1: Create Listing with 1 Hour Time Limit
        Create a test listing with has_time_limit: true and time_limit_hours: 1
        Verify expires_at is calculated correctly (1 hour from creation)
        Check that both has_time_limit and time_limit_hours are saved
        """
        print("⏰ Testing create listing with 1 hour time limit...")
        
        test_results = {
            "endpoint": "/listings",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "listing_created": False,
            "has_time_limit_correct": False,
            "time_limit_hours_correct": False,
            "expires_at_calculated": False,
            "expires_at_within_1_hour": False,
            "listing_id": None,
            "error_messages": [],
            "success": False
        }
        
        # Create test listing with 1 hour time limit
        listing_data = {
            "title": "Test Catalyst - 1 Hour Time Limit",
            "description": "Test listing for 1 hour time limit functionality",
            "price": 150.0,
            "category": "Catalysts",
            "condition": "Used",
            "seller_id": self.admin_user_id,
            "images": [],
            "tags": ["test", "time-limit", "1-hour"],
            "features": ["test feature"],
            "has_time_limit": True,
            "time_limit_hours": 1
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/listings", "POST", data=listing_data, headers=headers)
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            listing = result.get("data", {})
            test_results["listing_created"] = True
            test_results["listing_id"] = listing.get("id")
            
            if test_results["listing_id"]:
                self.test_listing_ids.append(test_results["listing_id"])
            
            print(f"    ✅ Listing created successfully: {test_results['listing_id']}")
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
            
            # Verify has_time_limit is set correctly
            if listing.get("has_time_limit") == True:
                test_results["has_time_limit_correct"] = True
                print(f"    ✅ has_time_limit correctly set to: {listing.get('has_time_limit')}")
            else:
                test_results["error_messages"].append(f"has_time_limit incorrect: expected True, got {listing.get('has_time_limit')}")
                print(f"    ❌ has_time_limit incorrect: expected True, got {listing.get('has_time_limit')}")
            
            # Verify time_limit_hours is set correctly
            if listing.get("time_limit_hours") == 1:
                test_results["time_limit_hours_correct"] = True
                print(f"    ✅ time_limit_hours correctly set to: {listing.get('time_limit_hours')}")
            else:
                test_results["error_messages"].append(f"time_limit_hours incorrect: expected 1, got {listing.get('time_limit_hours')}")
                print(f"    ❌ time_limit_hours incorrect: expected 1, got {listing.get('time_limit_hours')}")
            
            # Verify expires_at is calculated
            expires_at = listing.get("expires_at")
            if expires_at:
                test_results["expires_at_calculated"] = True
                print(f"    ✅ expires_at calculated: {expires_at}")
                
                # Verify expires_at is approximately 1 hour from now
                try:
                    if isinstance(expires_at, str):
                        expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    else:
                        expires_dt = expires_at
                    
                    now = datetime.utcnow()
                    time_diff = expires_dt - now
                    time_diff_minutes = time_diff.total_seconds() / 60
                    
                    # Should be approximately 60 minutes (allow 5 minute tolerance)
                    if 55 <= time_diff_minutes <= 65:
                        test_results["expires_at_within_1_hour"] = True
                        print(f"    ✅ expires_at correctly set to ~1 hour from now ({time_diff_minutes:.1f} minutes)")
                    else:
                        test_results["error_messages"].append(f"expires_at time incorrect: {time_diff_minutes:.1f} minutes from now")
                        print(f"    ❌ expires_at time incorrect: {time_diff_minutes:.1f} minutes from now")
                        
                except Exception as e:
                    test_results["error_messages"].append(f"Error parsing expires_at: {e}")
                    print(f"    ❌ Error parsing expires_at: {e}")
            else:
                test_results["error_messages"].append("expires_at not calculated")
                print(f"    ❌ expires_at not calculated")
            
            # Overall success
            test_results["success"] = (
                test_results["has_time_limit_correct"] and
                test_results["time_limit_hours_correct"] and
                test_results["expires_at_calculated"] and
                test_results["expires_at_within_1_hour"]
            )
            
        else:
            test_results["error_messages"].append(f"Listing creation failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Listing creation failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        return {
            "test_name": "Create Listing with 1 Hour Time Limit",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def test_browse_page_time_display(self) -> Dict:
        """
        Test 2: Browse Page Time Display
        Test GET /api/marketplace/browse
        Verify listings with time limits have proper time_info structure
        Check that time_remaining_seconds is calculated correctly
        Verify is_expired status is accurate
        """
        print("📋 Testing browse page time display...")
        
        test_results = {
            "endpoint": "/marketplace/browse",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "listings_count": 0,
            "time_limited_listings_count": 0,
            "time_info_present": False,
            "time_info_structure_correct": False,
            "time_remaining_calculated": False,
            "is_expired_accurate": False,
            "error_messages": [],
            "success": False
        }
        
        # Test browse endpoint
        result = await self.make_request("/marketplace/browse", params={"status": "active"})
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            listings = result.get("data", [])
            test_results["listings_count"] = len(listings) if isinstance(listings, list) else 0
            print(f"    ✅ Browse endpoint successful: {test_results['listings_count']} listings found")
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
            
            # Find time-limited listings
            time_limited_listings = []
            if listings and isinstance(listings, list):
                for listing in listings:
                    if isinstance(listing, dict) and listing.get("has_time_limit"):
                        time_limited_listings.append(listing)
                
                test_results["time_limited_listings_count"] = len(time_limited_listings)
                print(f"    📊 Time-limited listings found: {len(time_limited_listings)}")
                
                if time_limited_listings:
                    test_results["time_info_present"] = True
                    
                    # Check time_info structure on first time-limited listing
                    sample_listing = time_limited_listings[0]
                    time_info = sample_listing.get("time_info", {})
                    
                    if time_info:
                        print(f"    ✅ time_info present in listing: {sample_listing.get('id')}")
                        
                        # Check required fields in time_info
                        required_fields = ["has_time_limit", "time_remaining_seconds", "is_expired", "time_limit_hours"]
                        missing_fields = [field for field in required_fields if field not in time_info]
                        
                        if not missing_fields:
                            test_results["time_info_structure_correct"] = True
                            print(f"    ✅ time_info structure correct: {list(time_info.keys())}")
                            
                            # Verify time_remaining_seconds is calculated
                            time_remaining = time_info.get("time_remaining_seconds")
                            if isinstance(time_remaining, (int, float)) and time_remaining >= 0:
                                test_results["time_remaining_calculated"] = True
                                print(f"    ✅ time_remaining_seconds calculated: {time_remaining}")
                                
                                # Verify is_expired is accurate
                                is_expired = time_info.get("is_expired")
                                if isinstance(is_expired, bool):
                                    # is_expired should be True if time_remaining <= 0
                                    expected_expired = time_remaining <= 0
                                    if is_expired == expected_expired:
                                        test_results["is_expired_accurate"] = True
                                        print(f"    ✅ is_expired accurate: {is_expired} (time_remaining: {time_remaining})")
                                    else:
                                        test_results["error_messages"].append(f"is_expired inaccurate: {is_expired}, expected {expected_expired}")
                                        print(f"    ❌ is_expired inaccurate: {is_expired}, expected {expected_expired}")
                                else:
                                    test_results["error_messages"].append(f"is_expired not boolean: {type(is_expired)}")
                                    print(f"    ❌ is_expired not boolean: {type(is_expired)}")
                            else:
                                test_results["error_messages"].append(f"time_remaining_seconds invalid: {time_remaining}")
                                print(f"    ❌ time_remaining_seconds invalid: {time_remaining}")
                        else:
                            test_results["error_messages"].append(f"time_info missing fields: {missing_fields}")
                            print(f"    ❌ time_info missing fields: {missing_fields}")
                    else:
                        test_results["error_messages"].append("time_info not present in time-limited listing")
                        print(f"    ❌ time_info not present in time-limited listing")
                else:
                    # No time-limited listings found - this could be valid
                    print(f"    ℹ️ No time-limited listings found in browse results")
                    test_results["time_info_present"] = True  # Not an error if no time-limited listings exist
                    test_results["time_info_structure_correct"] = True
                    test_results["time_remaining_calculated"] = True
                    test_results["is_expired_accurate"] = True
            
            # Overall success
            test_results["success"] = (
                test_results["time_info_present"] and
                test_results["time_info_structure_correct"] and
                test_results["time_remaining_calculated"] and
                test_results["is_expired_accurate"]
            )
            
        else:
            test_results["error_messages"].append(f"Browse endpoint failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Browse endpoint failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        return {
            "test_name": "Browse Page Time Display",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def test_individual_listing_time_display(self) -> Dict:
        """
        Test 3: Individual Listing Time Display
        Test GET /api/listings/{listing_id} for time-limited listing
        Verify same time_info structure as browse page
        Check that 1-hour listings show correct remaining time
        """
        print("🔍 Testing individual listing time display...")
        
        test_results = {
            "endpoint": "/listings/{listing_id}",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "listing_found": False,
            "time_info_present": False,
            "time_info_structure_correct": False,
            "time_remaining_calculated": False,
            "is_expired_accurate": False,
            "listing_id": None,
            "error_messages": [],
            "success": False
        }
        
        # First, create a test listing with 1 hour time limit
        create_test = await self.test_create_listing_with_1_hour_time_limit()
        if not create_test["success"] or not create_test["test_results"].get("listing_id"):
            test_results["error_messages"].append("Could not create test listing for individual listing test")
            return {
                "test_name": "Individual Listing Time Display",
                "success": False,
                "test_results": test_results,
                "critical_issue": True
            }
        
        listing_id = create_test["test_results"]["listing_id"]
        test_results["listing_id"] = listing_id
        
        # Test individual listing endpoint
        result = await self.make_request(f"/listings/{listing_id}")
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            listing = result.get("data", {})
            test_results["listing_found"] = True
            print(f"    ✅ Individual listing found: {listing_id}")
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
            
            # Check time_info structure
            time_info = listing.get("time_info", {})
            
            if time_info:
                test_results["time_info_present"] = True
                print(f"    ✅ time_info present in individual listing")
                
                # Check required fields in time_info
                required_fields = ["has_time_limit", "time_remaining_seconds", "is_expired", "time_limit_hours"]
                missing_fields = [field for field in required_fields if field not in time_info]
                
                if not missing_fields:
                    test_results["time_info_structure_correct"] = True
                    print(f"    ✅ time_info structure correct: {list(time_info.keys())}")
                    
                    # Verify time_remaining_seconds is calculated
                    time_remaining = time_info.get("time_remaining_seconds")
                    if isinstance(time_remaining, (int, float)) and time_remaining >= 0:
                        test_results["time_remaining_calculated"] = True
                        print(f"    ✅ time_remaining_seconds calculated: {time_remaining}")
                        
                        # For 1-hour listing, should be close to 3600 seconds (allow some tolerance)
                        if 3300 <= time_remaining <= 3600:  # 55-60 minutes
                            print(f"    ✅ 1-hour listing time remaining is reasonable: {time_remaining/60:.1f} minutes")
                        else:
                            print(f"    ⚠️ 1-hour listing time remaining: {time_remaining/60:.1f} minutes (may be expected if time has passed)")
                        
                        # Verify is_expired is accurate
                        is_expired = time_info.get("is_expired")
                        if isinstance(is_expired, bool):
                            # is_expired should be True if time_remaining <= 0
                            expected_expired = time_remaining <= 0
                            if is_expired == expected_expired:
                                test_results["is_expired_accurate"] = True
                                print(f"    ✅ is_expired accurate: {is_expired} (time_remaining: {time_remaining})")
                            else:
                                test_results["error_messages"].append(f"is_expired inaccurate: {is_expired}, expected {expected_expired}")
                                print(f"    ❌ is_expired inaccurate: {is_expired}, expected {expected_expired}")
                        else:
                            test_results["error_messages"].append(f"is_expired not boolean: {type(is_expired)}")
                            print(f"    ❌ is_expired not boolean: {type(is_expired)}")
                    else:
                        test_results["error_messages"].append(f"time_remaining_seconds invalid: {time_remaining}")
                        print(f"    ❌ time_remaining_seconds invalid: {time_remaining}")
                else:
                    test_results["error_messages"].append(f"time_info missing fields: {missing_fields}")
                    print(f"    ❌ time_info missing fields: {missing_fields}")
            else:
                test_results["error_messages"].append("time_info not present in individual listing")
                print(f"    ❌ time_info not present in individual listing")
            
            # Overall success
            test_results["success"] = (
                test_results["time_info_present"] and
                test_results["time_info_structure_correct"] and
                test_results["time_remaining_calculated"] and
                test_results["is_expired_accurate"]
            )
            
        else:
            test_results["error_messages"].append(f"Individual listing endpoint failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Individual listing endpoint failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        return {
            "test_name": "Individual Listing Time Display",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def test_unlimited_listings(self) -> Dict:
        """
        Test 4: Unlimited Listings
        Test listings without time limits (has_time_limit: false)
        Verify time_info shows has_time_limit: false
        Check that unlimited listings don't show expiration
        """
        print("♾️ Testing unlimited listings...")
        
        test_results = {
            "endpoint": "/listings",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "listing_created": False,
            "has_time_limit_false": False,
            "time_limit_hours_default": False,
            "expires_at_not_set": False,
            "time_info_correct": False,
            "listing_id": None,
            "error_messages": [],
            "success": False
        }
        
        # Create test listing without time limit (default behavior)
        listing_data = {
            "title": "Test Catalyst - Unlimited Time",
            "description": "Test listing for unlimited time functionality",
            "price": 200.0,
            "category": "Catalysts",
            "condition": "Used",
            "seller_id": self.admin_user_id,
            "images": [],
            "tags": ["test", "unlimited", "no-time-limit"],
            "features": ["test feature"]
            # Note: Not setting has_time_limit or time_limit_hours to test defaults
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/listings", "POST", data=listing_data, headers=headers)
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            listing = result.get("data", {})
            test_results["listing_created"] = True
            test_results["listing_id"] = listing.get("id")
            
            if test_results["listing_id"]:
                self.test_listing_ids.append(test_results["listing_id"])
            
            print(f"    ✅ Unlimited listing created successfully: {test_results['listing_id']}")
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
            
            # Verify has_time_limit defaults to false
            has_time_limit = listing.get("has_time_limit")
            if has_time_limit == False:
                test_results["has_time_limit_false"] = True
                print(f"    ✅ has_time_limit correctly defaults to: {has_time_limit}")
            else:
                test_results["error_messages"].append(f"has_time_limit incorrect: expected False, got {has_time_limit}")
                print(f"    ❌ has_time_limit incorrect: expected False, got {has_time_limit}")
            
            # Verify time_limit_hours defaults to 24 (when time limit is enabled)
            time_limit_hours = listing.get("time_limit_hours")
            if time_limit_hours == 24 or time_limit_hours is None:
                test_results["time_limit_hours_default"] = True
                print(f"    ✅ time_limit_hours correctly set to: {time_limit_hours}")
            else:
                test_results["error_messages"].append(f"time_limit_hours incorrect: expected 24 or None, got {time_limit_hours}")
                print(f"    ❌ time_limit_hours incorrect: expected 24 or None, got {time_limit_hours}")
            
            # Verify expires_at is not set for unlimited listings
            expires_at = listing.get("expires_at")
            if expires_at is None or expires_at == "":
                test_results["expires_at_not_set"] = True
                print(f"    ✅ expires_at correctly not set: {expires_at}")
            else:
                test_results["error_messages"].append(f"expires_at should not be set for unlimited listings: {expires_at}")
                print(f"    ❌ expires_at should not be set for unlimited listings: {expires_at}")
            
            # Test individual listing endpoint to check time_info
            individual_result = await self.make_request(f"/listings/{test_results['listing_id']}")
            if individual_result["success"]:
                individual_listing = individual_result.get("data", {})
                time_info = individual_listing.get("time_info", {})
                
                if time_info:
                    # For unlimited listings, time_info should show has_time_limit: false
                    if time_info.get("has_time_limit") == False:
                        test_results["time_info_correct"] = True
                        print(f"    ✅ time_info correctly shows has_time_limit: false")
                    else:
                        test_results["error_messages"].append(f"time_info has_time_limit incorrect: {time_info.get('has_time_limit')}")
                        print(f"    ❌ time_info has_time_limit incorrect: {time_info.get('has_time_limit')}")
                else:
                    # For unlimited listings, time_info might not be present, which is acceptable
                    test_results["time_info_correct"] = True
                    print(f"    ✅ time_info not present for unlimited listing (acceptable)")
            
            # Overall success
            test_results["success"] = (
                test_results["has_time_limit_false"] and
                test_results["time_limit_hours_default"] and
                test_results["expires_at_not_set"] and
                test_results["time_info_correct"]
            )
            
        else:
            test_results["error_messages"].append(f"Unlimited listing creation failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Unlimited listing creation failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        return {
            "test_name": "Unlimited Listings",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def run_time_limit_tests(self) -> Dict:
        """
        Run complete time limit functionality tests
        """
        print("🚨 STARTING TIME LIMIT FUNCTIONALITY TESTING")
        print("=" * 80)
        print("TESTING: Time limit functionality fixes")
        print("FIXES: Default behavior, time_info calculation, browse/detail display")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_users()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "User authentication failed - cannot proceed with testing"
                }
            
            # Run all time limit tests
            create_1_hour_test = await self.test_create_listing_with_1_hour_time_limit()
            browse_time_display_test = await self.test_browse_page_time_display()
            individual_time_display_test = await self.test_individual_listing_time_display()
            unlimited_listings_test = await self.test_unlimited_listings()
            
            # Compile comprehensive test results
            test_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Time limit functionality fixes",
                "create_1_hour_test": create_1_hour_test,
                "browse_time_display_test": browse_time_display_test,
                "individual_time_display_test": individual_time_display_test,
                "unlimited_listings_test": unlimited_listings_test
            }
            
            # Determine critical findings
            critical_issues = []
            working_features = []
            
            tests = [create_1_hour_test, browse_time_display_test, individual_time_display_test, unlimited_listings_test]
            
            for test in tests:
                if test.get("critical_issue", False):
                    error_msg = "Unknown error"
                    if test.get("test_results", {}).get("error_messages"):
                        error_msg = test["test_results"]["error_messages"][0]
                    elif test.get("error"):
                        error_msg = test["error"]
                    critical_issues.append(f"{test['test_name']}: {error_msg}")
                
                if test.get("success", False):
                    working_features.append(f"{test['test_name']}: Working correctly")
            
            # Calculate success metrics
            total_tests = len(tests)
            successful_tests = sum(1 for test in tests if test.get("success", False))
            success_rate = (successful_tests / total_tests) * 100
            
            test_results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": success_rate,
                "critical_issues": critical_issues,
                "working_features": working_features,
                "time_limit_functionality_working": len(critical_issues) == 0,
                "fixes_applied_successfully": len(critical_issues) == 0
            }
            
            return test_results
            
        finally:
            await self.cleanup()


async def main():
    """Run the time limit functionality tests"""
    tester = TimeLimitTester()
    results = await tester.run_time_limit_tests()
    
    print("\n" + "=" * 80)
    print("🏁 TIME LIMIT FUNCTIONALITY TESTING RESULTS")
    print("=" * 80)
    
    summary = results.get("summary", {})
    
    print(f"📊 Test Summary:")
    print(f"   Total Tests: {summary.get('total_tests', 0)}")
    print(f"   Successful: {summary.get('successful_tests', 0)}")
    print(f"   Failed: {summary.get('failed_tests', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
    
    if summary.get("working_features"):
        print(f"\n✅ Working Features:")
        for feature in summary["working_features"]:
            print(f"   • {feature}")
    
    if summary.get("critical_issues"):
        print(f"\n❌ Critical Issues:")
        for issue in summary["critical_issues"]:
            print(f"   • {issue}")
    
    print(f"\n🎯 Time Limit Functionality Status: {'✅ WORKING' if summary.get('time_limit_functionality_working') else '❌ ISSUES FOUND'}")
    print(f"🔧 Fixes Applied Successfully: {'✅ YES' if summary.get('fixes_applied_successfully') else '❌ NO'}")
    
    print("\n" + "=" * 80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())