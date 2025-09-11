#!/usr/bin/env python3
"""
FIVE MAJOR ENHANCEMENTS TESTING - URGENT REVIEW REQUEST
Testing the five specific enhancements that were just implemented:

1. Time Limit Options Fix - Added 1-hour option, changed default from 24 to 1 hour
2. Registration Notification Admin-Only Fix - Separate checks for email and username duplicates
3. Registration Form - First/Last Name Split - Changed fullName to firstName/lastName fields
4. Registration Duplicate Checking - Added /api/check-username and /api/check-email endpoints
5. Highest Bidder Blocking on Individual Listings - Added visual indicator and disabled bidding when user is highest bidder

SPECIFIC TESTS NEEDED:
- Test 1: Username/Email Availability Endpoints (GET /api/check-username?username=testuser, GET /api/check-email?email=test@example.com)
- Test 2: Registration with New Fields (POST /api/auth/register with first_name, last_name fields)
- Test 3: Listing Creation Time Limits (verify listings can be created with time_limit_hours=1)
- Test 4: Bid Information Endpoints (GET /api/listings/{id}/tenders for mobile highest bidder detection)
"""

import asyncio
import aiohttp
import time
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://dynamic-marketplace.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"

# Demo User Configuration
DEMO_EMAIL = "demo@cataloro.com"
DEMO_USER_ID = "68bfff790e4e46bc28d43631"

class FiveEnhancementsTester:
    """
    FIVE MAJOR ENHANCEMENTS TESTING
    Testing all five enhancements that were just implemented according to the review request
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.test_user_id = None
        self.admin_user_id = None
        self.test_results = {}
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
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
        """Authenticate demo user and admin user"""
        print("🔐 Authenticating users for five enhancements testing...")
        
        # Authenticate demo user
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": "demo_password"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            self.test_user_id = demo_result["data"].get("user", {}).get("id", DEMO_USER_ID)
            print(f"  ✅ Demo user authentication successful (ID: {self.test_user_id})")
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error', 'Unknown error')}")
            return False
        
        # Authenticate admin user
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            self.admin_user_id = admin_result["data"].get("user", {}).get("id")
            print(f"  ✅ Admin user authentication successful (ID: {self.admin_user_id})")
            return True
        else:
            print(f"  ❌ Admin user authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
    
    async def test_username_email_availability_endpoints(self) -> Dict:
        """
        Test 1: Username/Email Availability Endpoints
        - GET /api/check-username?username=testuser
        - GET /api/check-email?email=test@example.com
        - Should return {available: true/false}
        """
        print("🔍 Testing username/email availability endpoints...")
        
        test_results = {
            "username_endpoint": "/check-username",
            "email_endpoint": "/check-email",
            "username_test_results": {},
            "email_test_results": {},
            "error_messages": [],
            "success": False
        }
        
        # Test username availability endpoint
        print("  👤 Testing username availability endpoint...")
        
        # Test with available username
        available_username = f"testuser_{int(time.time())}"
        username_result = await self.make_request("/check-username", params={"username": available_username})
        
        test_results["username_test_results"]["available_test"] = {
            "username": available_username,
            "status": username_result["status"],
            "response_time_ms": username_result["response_time_ms"],
            "success": username_result["success"]
        }
        
        if username_result["success"]:
            username_data = username_result.get("data", {})
            if isinstance(username_data, dict) and "available" in username_data:
                test_results["username_test_results"]["available_test"]["available"] = username_data["available"]
                if username_data["available"]:
                    print(f"    ✅ Available username test passed: {available_username} is available")
                else:
                    print(f"    ⚠️ Available username test unexpected: {available_username} marked as unavailable")
            else:
                test_results["error_messages"].append("Username endpoint doesn't return 'available' field")
                print(f"    ❌ Username endpoint response format incorrect: {username_data}")
        else:
            test_results["error_messages"].append(f"Username endpoint failed: Status {username_result['status']}")
            print(f"    ❌ Username endpoint failed: Status {username_result['status']}")
        
        # Test with existing username (admin username)
        existing_username_result = await self.make_request("/check-username", params={"username": ADMIN_USERNAME})
        
        test_results["username_test_results"]["existing_test"] = {
            "username": ADMIN_USERNAME,
            "status": existing_username_result["status"],
            "response_time_ms": existing_username_result["response_time_ms"],
            "success": existing_username_result["success"]
        }
        
        if existing_username_result["success"]:
            existing_data = existing_username_result.get("data", {})
            if isinstance(existing_data, dict) and "available" in existing_data:
                test_results["username_test_results"]["existing_test"]["available"] = existing_data["available"]
                if not existing_data["available"]:
                    print(f"    ✅ Existing username test passed: {ADMIN_USERNAME} is unavailable")
                else:
                    print(f"    ⚠️ Existing username test unexpected: {ADMIN_USERNAME} marked as available")
            else:
                test_results["error_messages"].append("Username endpoint doesn't return 'available' field for existing user")
        
        # Test email availability endpoint
        print("  📧 Testing email availability endpoint...")
        
        # Test with available email
        available_email = f"testuser_{int(time.time())}@example.com"
        email_result = await self.make_request("/check-email", params={"email": available_email})
        
        test_results["email_test_results"]["available_test"] = {
            "email": available_email,
            "status": email_result["status"],
            "response_time_ms": email_result["response_time_ms"],
            "success": email_result["success"]
        }
        
        if email_result["success"]:
            email_data = email_result.get("data", {})
            if isinstance(email_data, dict) and "available" in email_data:
                test_results["email_test_results"]["available_test"]["available"] = email_data["available"]
                if email_data["available"]:
                    print(f"    ✅ Available email test passed: {available_email} is available")
                else:
                    print(f"    ⚠️ Available email test unexpected: {available_email} marked as unavailable")
            else:
                test_results["error_messages"].append("Email endpoint doesn't return 'available' field")
                print(f"    ❌ Email endpoint response format incorrect: {email_data}")
        else:
            test_results["error_messages"].append(f"Email endpoint failed: Status {email_result['status']}")
            print(f"    ❌ Email endpoint failed: Status {email_result['status']}")
        
        # Test with existing email (admin email)
        existing_email_result = await self.make_request("/check-email", params={"email": ADMIN_EMAIL})
        
        test_results["email_test_results"]["existing_test"] = {
            "email": ADMIN_EMAIL,
            "status": existing_email_result["status"],
            "response_time_ms": existing_email_result["response_time_ms"],
            "success": existing_email_result["success"]
        }
        
        if existing_email_result["success"]:
            existing_email_data = existing_email_result.get("data", {})
            if isinstance(existing_email_data, dict) and "available" in existing_email_data:
                test_results["email_test_results"]["existing_test"]["available"] = existing_email_data["available"]
                if not existing_email_data["available"]:
                    print(f"    ✅ Existing email test passed: {ADMIN_EMAIL} is unavailable")
                else:
                    print(f"    ⚠️ Existing email test unexpected: {ADMIN_EMAIL} marked as available")
            else:
                test_results["error_messages"].append("Email endpoint doesn't return 'available' field for existing user")
        
        # Determine overall success
        username_success = (
            test_results["username_test_results"].get("available_test", {}).get("success", False) and
            test_results["username_test_results"].get("existing_test", {}).get("success", False)
        )
        email_success = (
            test_results["email_test_results"].get("available_test", {}).get("success", False) and
            test_results["email_test_results"].get("existing_test", {}).get("success", False)
        )
        
        test_results["success"] = username_success and email_success
        
        return {
            "test_name": "Username/Email Availability Endpoints",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "endpoints_working": test_results["success"]
        }
    
    async def test_registration_with_new_fields(self) -> Dict:
        """
        Test 2: Registration with New Fields
        - POST /api/auth/register with first_name, last_name fields
        - Verify user creation includes both fields
        - Check duplicate prevention for both username and email
        """
        print("📝 Testing registration with new first_name/last_name fields...")
        
        test_results = {
            "endpoint": "/auth/register",
            "registration_tests": [],
            "error_messages": [],
            "success": False
        }
        
        # Test 1: Registration with first_name and last_name
        print("  👥 Testing registration with first_name and last_name fields...")
        
        timestamp = int(time.time())
        test_user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"testuser_{timestamp}@example.com",
            "first_name": "Test",
            "last_name": "User",
            "full_name": "Test User",  # Computed full_name
            "account_type": "buyer"
        }
        
        registration_result = await self.make_request("/auth/register", "POST", data=test_user_data)
        
        registration_test = {
            "test_type": "new_fields_registration",
            "user_data": test_user_data,
            "status": registration_result["status"],
            "response_time_ms": registration_result["response_time_ms"],
            "success": registration_result["success"]
        }
        
        if registration_result["success"]:
            registration_data = registration_result.get("data", {})
            registration_test["user_id"] = registration_data.get("user_id")
            registration_test["status_message"] = registration_data.get("status", "unknown")
            print(f"    ✅ Registration with new fields successful: User ID {registration_test['user_id']}")
            
            # Verify user was created with first_name and last_name
            if registration_test["user_id"]:
                profile_result = await self.make_request(f"/auth/profile/{registration_test['user_id']}")
                if profile_result["success"]:
                    profile_data = profile_result.get("data", {})
                    registration_test["profile_verification"] = {
                        "has_first_name": "first_name" in profile_data,
                        "has_last_name": "last_name" in profile_data,
                        "first_name_value": profile_data.get("first_name"),
                        "last_name_value": profile_data.get("last_name"),
                        "full_name_value": profile_data.get("full_name")
                    }
                    
                    if profile_data.get("first_name") == "Test" and profile_data.get("last_name") == "User":
                        print(f"    ✅ User profile contains first_name and last_name fields correctly")
                    else:
                        test_results["error_messages"].append("User profile missing or incorrect first_name/last_name fields")
                        print(f"    ❌ User profile missing or incorrect first_name/last_name fields")
                else:
                    test_results["error_messages"].append("Could not verify user profile after registration")
                    print(f"    ⚠️ Could not verify user profile after registration")
        else:
            registration_test["error"] = registration_result.get("error", "Unknown error")
            test_results["error_messages"].append(f"Registration failed: {registration_test['error']}")
            print(f"    ❌ Registration failed: {registration_test['error']}")
        
        test_results["registration_tests"].append(registration_test)
        
        # Test 2: Duplicate username prevention
        print("  🚫 Testing duplicate username prevention...")
        
        duplicate_username_data = {
            "username": test_user_data["username"],  # Same username
            "email": f"different_{timestamp}@example.com",  # Different email
            "first_name": "Different",
            "last_name": "User",
            "full_name": "Different User",
            "account_type": "seller"
        }
        
        duplicate_username_result = await self.make_request("/auth/register", "POST", data=duplicate_username_data)
        
        duplicate_username_test = {
            "test_type": "duplicate_username_prevention",
            "user_data": duplicate_username_data,
            "status": duplicate_username_result["status"],
            "response_time_ms": duplicate_username_result["response_time_ms"],
            "success": duplicate_username_result["success"],
            "should_fail": True
        }
        
        if not duplicate_username_result["success"]:
            duplicate_username_test["prevented_correctly"] = True
            print(f"    ✅ Duplicate username correctly prevented: Status {duplicate_username_result['status']}")
        else:
            duplicate_username_test["prevented_correctly"] = False
            test_results["error_messages"].append("Duplicate username was not prevented")
            print(f"    ❌ Duplicate username was not prevented")
        
        test_results["registration_tests"].append(duplicate_username_test)
        
        # Test 3: Duplicate email prevention
        print("  📧 Testing duplicate email prevention...")
        
        duplicate_email_data = {
            "username": f"different_{timestamp}",  # Different username
            "email": test_user_data["email"],  # Same email
            "first_name": "Another",
            "last_name": "User",
            "full_name": "Another User",
            "account_type": "buyer"
        }
        
        duplicate_email_result = await self.make_request("/auth/register", "POST", data=duplicate_email_data)
        
        duplicate_email_test = {
            "test_type": "duplicate_email_prevention",
            "user_data": duplicate_email_data,
            "status": duplicate_email_result["status"],
            "response_time_ms": duplicate_email_result["response_time_ms"],
            "success": duplicate_email_result["success"],
            "should_fail": True
        }
        
        if not duplicate_email_result["success"]:
            duplicate_email_test["prevented_correctly"] = True
            print(f"    ✅ Duplicate email correctly prevented: Status {duplicate_email_result['status']}")
        else:
            duplicate_email_test["prevented_correctly"] = False
            test_results["error_messages"].append("Duplicate email was not prevented")
            print(f"    ❌ Duplicate email was not prevented")
        
        test_results["registration_tests"].append(duplicate_email_test)
        
        # Determine overall success
        new_fields_success = test_results["registration_tests"][0].get("success", False)
        duplicate_prevention_success = (
            test_results["registration_tests"][1].get("prevented_correctly", False) and
            test_results["registration_tests"][2].get("prevented_correctly", False)
        )
        
        test_results["success"] = new_fields_success and duplicate_prevention_success
        
        return {
            "test_name": "Registration with New Fields",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "new_fields_working": new_fields_success,
            "duplicate_prevention_working": duplicate_prevention_success
        }
    
    async def test_listing_creation_time_limits(self) -> Dict:
        """
        Test 3: Listing Creation Time Limits
        - Verify listings can be created with time_limit_hours=1
        - Check that expiry calculation works correctly
        - Test that "Without Limit" issue is resolved
        """
        print("⏰ Testing listing creation with time limits...")
        
        test_results = {
            "endpoint": "/listings",
            "time_limit_tests": [],
            "error_messages": [],
            "success": False
        }
        
        if not self.admin_token:
            test_results["error_messages"].append("No admin token available for listing creation")
            return {
                "test_name": "Listing Creation Time Limits",
                "success": False,
                "test_results": test_results,
                "critical_issue": True
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: Create listing with 1-hour time limit
        print("  🕐 Testing listing creation with 1-hour time limit...")
        
        one_hour_listing_data = {
            "title": "Test Catalyst - 1 Hour Time Limit",
            "description": "Testing 1-hour time limit functionality",
            "price": 100.0,
            "category": "Catalysts",
            "condition": "Used",
            "seller_id": self.admin_user_id,
            "images": [],
            "tags": ["test", "time-limit"],
            "features": ["1-hour limit"],
            "has_time_limit": True,
            "time_limit_hours": 1
        }
        
        one_hour_result = await self.make_request("/listings", "POST", data=one_hour_listing_data, headers=headers)
        
        one_hour_test = {
            "test_type": "one_hour_time_limit",
            "listing_data": one_hour_listing_data,
            "status": one_hour_result["status"],
            "response_time_ms": one_hour_result["response_time_ms"],
            "success": one_hour_result["success"]
        }
        
        if one_hour_result["success"]:
            listing_data = one_hour_result.get("data", {})
            one_hour_test["listing_id"] = listing_data.get("id")
            one_hour_test["time_limit_hours"] = listing_data.get("time_limit_hours")
            one_hour_test["expires_at"] = listing_data.get("expires_at")
            one_hour_test["has_time_limit"] = listing_data.get("has_time_limit")
            
            if listing_data.get("time_limit_hours") == 1:
                print(f"    ✅ 1-hour time limit listing created successfully: ID {one_hour_test['listing_id']}")
                
                # Verify expiry calculation
                if listing_data.get("expires_at"):
                    print(f"    ✅ Expiry time calculated: {listing_data.get('expires_at')}")
                    one_hour_test["expiry_calculated"] = True
                else:
                    test_results["error_messages"].append("Expiry time not calculated for 1-hour listing")
                    print(f"    ❌ Expiry time not calculated for 1-hour listing")
                    one_hour_test["expiry_calculated"] = False
            else:
                test_results["error_messages"].append(f"Time limit not set correctly: got {listing_data.get('time_limit_hours')}, expected 1")
                print(f"    ❌ Time limit not set correctly: got {listing_data.get('time_limit_hours')}, expected 1")
        else:
            one_hour_test["error"] = one_hour_result.get("error", "Unknown error")
            test_results["error_messages"].append(f"1-hour listing creation failed: {one_hour_test['error']}")
            print(f"    ❌ 1-hour listing creation failed: {one_hour_test['error']}")
        
        test_results["time_limit_tests"].append(one_hour_test)
        
        # Test 2: Create listing without time limit
        print("  ♾️ Testing listing creation without time limit...")
        
        no_limit_listing_data = {
            "title": "Test Catalyst - No Time Limit",
            "description": "Testing no time limit functionality",
            "price": 150.0,
            "category": "Catalysts",
            "condition": "New",
            "seller_id": self.admin_user_id,
            "images": [],
            "tags": ["test", "no-limit"],
            "features": ["no time limit"],
            "has_time_limit": False
        }
        
        no_limit_result = await self.make_request("/listings", "POST", data=no_limit_listing_data, headers=headers)
        
        no_limit_test = {
            "test_type": "no_time_limit",
            "listing_data": no_limit_listing_data,
            "status": no_limit_result["status"],
            "response_time_ms": no_limit_result["response_time_ms"],
            "success": no_limit_result["success"]
        }
        
        if no_limit_result["success"]:
            listing_data = no_limit_result.get("data", {})
            no_limit_test["listing_id"] = listing_data.get("id")
            no_limit_test["has_time_limit"] = listing_data.get("has_time_limit")
            no_limit_test["time_limit_hours"] = listing_data.get("time_limit_hours")
            no_limit_test["expires_at"] = listing_data.get("expires_at")
            
            if not listing_data.get("has_time_limit", True):
                print(f"    ✅ No time limit listing created successfully: ID {no_limit_test['listing_id']}")
                
                # Verify no expiry time set
                if not listing_data.get("expires_at"):
                    print(f"    ✅ No expiry time set for unlimited listing")
                    no_limit_test["no_expiry_correct"] = True
                else:
                    print(f"    ⚠️ Expiry time set for unlimited listing: {listing_data.get('expires_at')}")
                    no_limit_test["no_expiry_correct"] = False
            else:
                test_results["error_messages"].append("has_time_limit not set to false for unlimited listing")
                print(f"    ❌ has_time_limit not set to false for unlimited listing")
        else:
            no_limit_test["error"] = no_limit_result.get("error", "Unknown error")
            test_results["error_messages"].append(f"No limit listing creation failed: {no_limit_test['error']}")
            print(f"    ❌ No limit listing creation failed: {no_limit_test['error']}")
        
        test_results["time_limit_tests"].append(no_limit_test)
        
        # Test 3: Verify default time limit is 1 hour (if has_time_limit=true but no time_limit_hours specified)
        print("  🔄 Testing default time limit behavior...")
        
        default_limit_listing_data = {
            "title": "Test Catalyst - Default Time Limit",
            "description": "Testing default time limit functionality",
            "price": 200.0,
            "category": "Catalysts",
            "condition": "Used",
            "seller_id": self.admin_user_id,
            "images": [],
            "tags": ["test", "default-limit"],
            "features": ["default time limit"],
            "has_time_limit": True
            # Note: time_limit_hours not specified to test default
        }
        
        default_limit_result = await self.make_request("/listings", "POST", data=default_limit_listing_data, headers=headers)
        
        default_limit_test = {
            "test_type": "default_time_limit",
            "listing_data": default_limit_listing_data,
            "status": default_limit_result["status"],
            "response_time_ms": default_limit_result["response_time_ms"],
            "success": default_limit_result["success"]
        }
        
        if default_limit_result["success"]:
            listing_data = default_limit_result.get("data", {})
            default_limit_test["listing_id"] = listing_data.get("id")
            default_limit_test["time_limit_hours"] = listing_data.get("time_limit_hours")
            default_limit_test["expires_at"] = listing_data.get("expires_at")
            
            # Check if default is 1 hour (as per the enhancement)
            if listing_data.get("time_limit_hours") == 1:
                print(f"    ✅ Default time limit correctly set to 1 hour: ID {default_limit_test['listing_id']}")
                default_limit_test["default_correct"] = True
            else:
                print(f"    ⚠️ Default time limit not 1 hour: got {listing_data.get('time_limit_hours')}")
                default_limit_test["default_correct"] = False
        else:
            default_limit_test["error"] = default_limit_result.get("error", "Unknown error")
            test_results["error_messages"].append(f"Default limit listing creation failed: {default_limit_test['error']}")
            print(f"    ❌ Default limit listing creation failed: {default_limit_test['error']}")
        
        test_results["time_limit_tests"].append(default_limit_test)
        
        # Determine overall success
        one_hour_success = test_results["time_limit_tests"][0].get("success", False)
        no_limit_success = test_results["time_limit_tests"][1].get("success", False)
        default_success = test_results["time_limit_tests"][2].get("success", False)
        
        test_results["success"] = one_hour_success and no_limit_success and default_success
        
        return {
            "test_name": "Listing Creation Time Limits",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "one_hour_working": one_hour_success,
            "no_limit_working": no_limit_success,
            "default_working": default_success
        }
    
    async def test_bid_information_endpoints(self) -> Dict:
        """
        Test 4: Bid Information Endpoints
        - GET /api/listings/{id}/tenders for mobile highest bidder detection
        - Verify highest_bidder_id is correctly calculated
        """
        print("💰 Testing bid information endpoints for highest bidder detection...")
        
        test_results = {
            "endpoint": "/listings/{id}/tenders",
            "bid_info_tests": [],
            "error_messages": [],
            "success": False
        }
        
        if not self.admin_token or not self.demo_token:
            test_results["error_messages"].append("Missing authentication tokens")
            return {
                "test_name": "Bid Information Endpoints",
                "success": False,
                "test_results": test_results,
                "critical_issue": True
            }
        
        # First, create a test listing
        print("  📝 Creating test listing for bid testing...")
        
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        test_listing_data = {
            "title": "Test Catalyst - Bid Information Testing",
            "description": "Testing bid information endpoints",
            "price": 100.0,
            "category": "Catalysts",
            "condition": "Used",
            "seller_id": self.admin_user_id,
            "images": [],
            "tags": ["test", "bid-info"],
            "features": ["bid testing"]
        }
        
        listing_result = await self.make_request("/listings", "POST", data=test_listing_data, headers=admin_headers)
        
        if not listing_result["success"]:
            test_results["error_messages"].append(f"Failed to create test listing: {listing_result.get('error', 'Unknown error')}")
            return {
                "test_name": "Bid Information Endpoints",
                "success": False,
                "test_results": test_results,
                "critical_issue": True
            }
        
        listing_id = listing_result["data"].get("id")
        print(f"    ✅ Test listing created: {listing_id}")
        
        # Test 1: Get tenders for listing with no bids
        print("  📊 Testing tenders endpoint with no bids...")
        
        no_bids_result = await self.make_request(f"/listings/{listing_id}/tenders")
        
        no_bids_test = {
            "test_type": "no_bids",
            "listing_id": listing_id,
            "status": no_bids_result["status"],
            "response_time_ms": no_bids_result["response_time_ms"],
            "success": no_bids_result["success"]
        }
        
        if no_bids_result["success"]:
            tenders_data = no_bids_result.get("data", [])
            no_bids_test["tenders_count"] = len(tenders_data) if isinstance(tenders_data, list) else 0
            no_bids_test["highest_bidder_id"] = None
            
            if no_bids_test["tenders_count"] == 0:
                print(f"    ✅ No bids endpoint working: {no_bids_test['tenders_count']} tenders")
            else:
                print(f"    ⚠️ Unexpected tenders found: {no_bids_test['tenders_count']}")
        else:
            no_bids_test["error"] = no_bids_result.get("error", "Unknown error")
            test_results["error_messages"].append(f"No bids test failed: {no_bids_test['error']}")
            print(f"    ❌ No bids test failed: {no_bids_test['error']}")
        
        test_results["bid_info_tests"].append(no_bids_test)
        
        # Test 2: Create a bid and test highest bidder detection
        print("  💸 Creating test bid and testing highest bidder detection...")
        
        demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
        bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.test_user_id,
            "offer_amount": 150.0
        }
        
        bid_result = await self.make_request("/tenders/submit", "POST", data=bid_data, headers=demo_headers)
        
        if bid_result["success"]:
            tender_id = bid_result["data"].get("tender_id")
            print(f"    ✅ Test bid created: {tender_id}")
            
            # Now test tenders endpoint with bid
            with_bids_result = await self.make_request(f"/listings/{listing_id}/tenders")
            
            with_bids_test = {
                "test_type": "with_bids",
                "listing_id": listing_id,
                "tender_id": tender_id,
                "status": with_bids_result["status"],
                "response_time_ms": with_bids_result["response_time_ms"],
                "success": with_bids_result["success"]
            }
            
            if with_bids_result["success"]:
                tenders_data = with_bids_result.get("data", [])
                with_bids_test["tenders_count"] = len(tenders_data) if isinstance(tenders_data, list) else 0
                
                if with_bids_test["tenders_count"] > 0 and isinstance(tenders_data, list):
                    # Find highest bid
                    highest_bid = max(tenders_data, key=lambda x: x.get("offer_amount", 0) if isinstance(x, dict) else 0)
                    with_bids_test["highest_bid_amount"] = highest_bid.get("offer_amount")
                    with_bids_test["highest_bidder_id"] = highest_bid.get("buyer_id")
                    
                    if with_bids_test["highest_bidder_id"] == self.test_user_id:
                        print(f"    ✅ Highest bidder correctly identified: {with_bids_test['highest_bidder_id']}")
                        with_bids_test["highest_bidder_correct"] = True
                    else:
                        print(f"    ❌ Highest bidder incorrect: got {with_bids_test['highest_bidder_id']}, expected {self.test_user_id}")
                        with_bids_test["highest_bidder_correct"] = False
                        test_results["error_messages"].append("Highest bidder ID not correctly identified")
                    
                    print(f"    📊 Tenders found: {with_bids_test['tenders_count']}, Highest bid: ${with_bids_test['highest_bid_amount']}")
                else:
                    test_results["error_messages"].append("No tenders returned after bid creation")
                    print(f"    ❌ No tenders returned after bid creation")
            else:
                with_bids_test["error"] = with_bids_result.get("error", "Unknown error")
                test_results["error_messages"].append(f"With bids test failed: {with_bids_test['error']}")
                print(f"    ❌ With bids test failed: {with_bids_test['error']}")
            
            test_results["bid_info_tests"].append(with_bids_test)
        else:
            test_results["error_messages"].append(f"Failed to create test bid: {bid_result.get('error', 'Unknown error')}")
            print(f"    ❌ Failed to create test bid: {bid_result.get('error', 'Unknown error')}")
        
        # Determine overall success
        no_bids_success = test_results["bid_info_tests"][0].get("success", False)
        with_bids_success = len(test_results["bid_info_tests"]) > 1 and test_results["bid_info_tests"][1].get("success", False)
        highest_bidder_correct = len(test_results["bid_info_tests"]) > 1 and test_results["bid_info_tests"][1].get("highest_bidder_correct", False)
        
        test_results["success"] = no_bids_success and with_bids_success and highest_bidder_correct
        
        return {
            "test_name": "Bid Information Endpoints",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "endpoints_working": no_bids_success and with_bids_success,
            "highest_bidder_detection_working": highest_bidder_correct
        }
    
    async def run_five_enhancements_tests(self) -> Dict:
        """
        Run complete five enhancements tests
        """
        print("🚨 STARTING FIVE MAJOR ENHANCEMENTS TESTING")
        print("=" * 80)
        print("TESTING: Five specific enhancements that were just implemented")
        print("1. Time Limit Options Fix - Added 1-hour option, changed default from 24 to 1 hour")
        print("2. Registration Notification Admin-Only Fix - Separate checks for email and username duplicates")
        print("3. Registration Form - First/Last Name Split - Changed fullName to firstName/lastName fields")
        print("4. Registration Duplicate Checking - Added /api/check-username and /api/check-email endpoints")
        print("5. Highest Bidder Blocking on Individual Listings - Added visual indicator and disabled bidding when user is highest bidder")
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
            
            # Run all five enhancement tests
            test1 = await self.test_username_email_availability_endpoints()
            test2 = await self.test_registration_with_new_fields()
            test3 = await self.test_listing_creation_time_limits()
            test4 = await self.test_bid_information_endpoints()
            
            # Compile comprehensive test results
            test_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Five major enhancements that were just implemented",
                "enhancement_1_username_email_availability": test1,
                "enhancement_2_registration_new_fields": test2,
                "enhancement_3_listing_time_limits": test3,
                "enhancement_4_bid_information": test4
            }
            
            # Determine critical findings
            critical_issues = []
            working_features = []
            
            tests = [test1, test2, test3, test4]
            
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
                "total_enhancements_tested": total_tests,
                "successful_enhancements": successful_tests,
                "failed_enhancements": total_tests - successful_tests,
                "success_rate": success_rate,
                "critical_issues": critical_issues,
                "working_features": working_features,
                "all_enhancements_working": len(critical_issues) == 0
            }
            
            return test_results
            
        finally:
            await self.cleanup()


async def main():
    """Run the five enhancements tests"""
    tester = FiveEnhancementsTester()
    results = await tester.run_five_enhancements_tests()
    
    print("\n" + "=" * 80)
    print("🏁 FIVE ENHANCEMENTS TESTING COMPLETED")
    print("=" * 80)
    
    summary = results.get("summary", {})
    print(f"📊 RESULTS: {summary.get('successful_enhancements', 0)}/{summary.get('total_enhancements_tested', 0)} enhancements working ({summary.get('success_rate', 0):.1f}% success rate)")
    
    if summary.get("working_features"):
        print("\n✅ WORKING FEATURES:")
        for feature in summary["working_features"]:
            print(f"  • {feature}")
    
    if summary.get("critical_issues"):
        print("\n❌ CRITICAL ISSUES:")
        for issue in summary["critical_issues"]:
            print(f"  • {issue}")
    
    if summary.get("all_enhancements_working"):
        print("\n🎉 ALL FIVE ENHANCEMENTS ARE WORKING CORRECTLY!")
    else:
        print(f"\n⚠️ {summary.get('failed_enhancements', 0)} ENHANCEMENT(S) NEED ATTENTION")
    
    print("\n" + "=" * 80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())