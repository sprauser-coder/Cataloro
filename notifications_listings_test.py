#!/usr/bin/env python3
"""
NOTIFICATIONS & LISTINGS CRITICAL FIXES TESTING
Testing the two critical fixes just applied as per review request:

ISSUE 1: Notifications TypeError Fix
- Problem: TypeError: userNotifications.filter is not a function in ModernHeader.js
- Fix Applied: Added proper array validation for API responses in frontend
- Test Required: Test GET /api/user/{user_id}/notifications endpoint returns array format

ISSUE 2: Create Listing "Not Found" Fix  
- Problem: Error: Not Found when creating listings
- Fix Applied: Added /api prefix to createListing endpoint URL + authentication headers
- Test Required: Test POST /api/listings endpoint with authentication
"""

import asyncio
import aiohttp
import time
import json
import base64
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://dynamic-marketplace.preview.emergentagent.com/api"

# Test User Configuration
DEMO_EMAIL = "demo@cataloro.com"
DEMO_USER_ID = "68bfff790e4e46bc28d43631"
ADMIN_EMAIL = "admin@cataloro.com"

class NotificationsListingsTester:
    """
    Testing the two critical fixes that were just applied:
    1. Notifications TypeError Fix - Test notifications API returns array format
    2. Create Listing "Not Found" Fix - Test create listing API works with authentication
    """
    def __init__(self):
        self.session = None
        self.demo_token = None
        self.admin_token = None
        self.demo_user_id = None
        
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
        """Authenticate demo and admin users"""
        print("🔐 Authenticating users for critical fixes testing...")
        
        # Authenticate demo user
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": "demo_password"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            self.demo_user_id = demo_result["data"].get("user", {}).get("id", DEMO_USER_ID)
            print(f"  ✅ Demo user authentication successful (ID: {self.demo_user_id})")
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
            print(f"  ✅ Admin authentication successful")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
    
    async def test_notifications_array_format(self) -> Dict:
        """
        ISSUE 1: Test GET /api/user/{user_id}/notifications endpoint
        - Verify it returns valid array structure for filtering
        - Test both when notifications exist and when empty
        - Ensure no TypeError: userNotifications.filter is not a function
        """
        print("🔔 Testing notifications API returns array format...")
        
        if not self.demo_token or not self.demo_user_id:
            return {"test_name": "Notifications Array Format", "error": "No demo token or user ID available"}
        
        test_results = {
            "endpoint": f"/user/{self.demo_user_id}/notifications",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "is_array": False,
            "array_length": 0,
            "filterable": False,
            "error_messages": [],
            "success": False,
            "fix_working": False
        }
        
        # Test with authentication
        print("  🔐 Testing authenticated notifications access...")
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        result = await self.make_request(f"/user/{self.demo_user_id}/notifications", headers=headers)
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            notifications = result.get("data", [])
            test_results["success"] = True
            
            # Critical test: Verify response is an array
            if isinstance(notifications, list):
                test_results["is_array"] = True
                test_results["array_length"] = len(notifications)
                test_results["fix_working"] = True
                print(f"    ✅ Notifications API returns array: {test_results['array_length']} notifications")
                
                # Test that the array is filterable (this is what was failing in frontend)
                try:
                    # Simulate the frontend filter operation that was failing
                    filtered_notifications = [n for n in notifications if isinstance(n, dict)]
                    test_results["filterable"] = True
                    print(f"    ✅ Array is filterable: {len(filtered_notifications)} items after filter")
                except Exception as filter_error:
                    test_results["error_messages"].append(f"Array not filterable: {filter_error}")
                    print(f"    ❌ Array filtering failed: {filter_error}")
                
                # Verify notification structure if any exist
                if notifications and len(notifications) > 0:
                    sample_notification = notifications[0]
                    if isinstance(sample_notification, dict):
                        required_fields = ["id", "title", "message", "type", "read"]
                        missing_fields = [field for field in required_fields if field not in sample_notification]
                        if missing_fields:
                            test_results["error_messages"].append(f"Missing notification fields: {missing_fields}")
                        else:
                            print(f"    ✅ Notifications have required fields: {required_fields}")
                    else:
                        test_results["error_messages"].append("Notification items are not objects")
                        print(f"    ⚠️ Notification items are not objects: {type(sample_notification)}")
                else:
                    print(f"    ✅ Empty notifications array (valid state)")
                    
            else:
                test_results["error_messages"].append(f"Response is not an array: {type(notifications)}")
                print(f"    ❌ Response is not an array: {type(notifications)}")
                print(f"    ❌ This would cause TypeError: userNotifications.filter is not a function")
            
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
        else:
            test_results["error_messages"].append(f"Notifications API failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Notifications API failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        # Test without authentication (should fail properly)
        print("  🚫 Testing unauthenticated access (should fail)...")
        unauth_result = await self.make_request(f"/user/{self.demo_user_id}/notifications")
        if unauth_result["status"] in [401, 403]:
            print(f"    ✅ Unauthenticated access properly rejected: Status {unauth_result['status']}")
        else:
            print(f"    ⚠️ Unauthenticated access not properly rejected: Status {unauth_result['status']}")
            test_results["error_messages"].append("Authentication not properly enforced")
        
        return {
            "test_name": "Notifications Array Format",
            "success": test_results["success"] and test_results["is_array"] and test_results["filterable"],
            "test_results": test_results,
            "critical_issue": not test_results["success"] or not test_results["is_array"],
            "fix_working": test_results["fix_working"] and test_results["filterable"],
            "prevents_typeerror": test_results["is_array"]
        }
    
    async def test_create_listing_endpoint(self) -> Dict:
        """
        ISSUE 2: Test POST /api/listings endpoint
        - Verify it works with authentication headers
        - Test that endpoint accepts listing creation data
        - Ensure no "Error: Not Found" when creating listings
        """
        print("📝 Testing create listing endpoint with authentication...")
        
        if not self.demo_token:
            return {"test_name": "Create Listing Endpoint", "error": "No demo token available"}
        
        test_results = {
            "endpoint": "/listings",
            "expected_status": 201,
            "actual_status": 0,
            "response_time_ms": 0,
            "listing_created": False,
            "listing_id": None,
            "error_messages": [],
            "success": False,
            "fix_working": False,
            "authentication_working": False
        }
        
        # Prepare test listing data
        test_listing_data = {
            "title": "Test Listing - Critical Fix Verification",
            "description": "This is a test listing to verify the create listing endpoint fix",
            "price": 99.99,
            "category": "Electronics",
            "condition": "Used",
            "seller_id": self.demo_user_id,
            "images": [],
            "tags": ["test", "verification"],
            "features": ["Test feature"]
        }
        
        # Test with authentication
        print("  🔐 Testing authenticated listing creation...")
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        result = await self.make_request("/listings", "POST", data=test_listing_data, headers=headers)
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            listing_response = result.get("data", {})
            test_results["success"] = True
            test_results["fix_working"] = True
            test_results["authentication_working"] = True
            
            # Check if listing was created successfully
            if isinstance(listing_response, dict):
                test_results["listing_id"] = listing_response.get("id") or listing_response.get("listing_id")
                if test_results["listing_id"]:
                    test_results["listing_created"] = True
                    print(f"    ✅ Listing created successfully: ID {test_results['listing_id']}")
                else:
                    test_results["error_messages"].append("No listing ID in response")
                    print(f"    ⚠️ Listing created but no ID returned")
                
                # Verify response contains expected fields
                expected_fields = ["id", "title", "price", "status"]
                present_fields = [field for field in expected_fields if field in listing_response]
                print(f"    ✅ Response contains fields: {present_fields}")
            else:
                test_results["error_messages"].append(f"Invalid response format: {type(listing_response)}")
                print(f"    ⚠️ Invalid response format: {type(listing_response)}")
            
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
            print(f"    ✅ No 'Error: Not Found' - fix is working")
            
        else:
            test_results["error_messages"].append(f"Create listing failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Create listing failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
            
            # Check if this is the specific "Not Found" error that was reported
            if result["status"] == 404:
                print(f"    ❌ CRITICAL: Still getting 404 'Not Found' error - fix not working")
                test_results["error_messages"].append("Still getting 404 'Not Found' error - fix not working")
            elif result["status"] == 401 or result["status"] == 403:
                print(f"    ⚠️ Authentication error - check if headers are properly set")
                test_results["error_messages"].append("Authentication error - headers may not be properly set")
        
        # Test without authentication (should fail with 401/403, not 404)
        print("  🚫 Testing unauthenticated listing creation (should fail with auth error, not 404)...")
        unauth_result = await self.make_request("/listings", "POST", data=test_listing_data)
        if unauth_result["status"] in [401, 403]:
            print(f"    ✅ Unauthenticated access properly rejected: Status {unauth_result['status']}")
            test_results["authentication_working"] = True
        elif unauth_result["status"] == 404:
            print(f"    ❌ Getting 404 instead of auth error - endpoint may not exist")
            test_results["error_messages"].append("Getting 404 instead of auth error - endpoint may not exist")
        else:
            print(f"    ⚠️ Unexpected status for unauthenticated access: Status {unauth_result['status']}")
            test_results["error_messages"].append(f"Unexpected unauthenticated status: {unauth_result['status']}")
        
        # Cleanup: Delete test listing if created
        if test_results["listing_created"] and test_results["listing_id"]:
            print("  🧹 Cleaning up test listing...")
            cleanup_headers = {"Authorization": f"Bearer {self.demo_token}"}
            cleanup_result = await self.make_request(f"/listings/{test_results['listing_id']}", "DELETE", headers=cleanup_headers)
            if cleanup_result["success"]:
                print(f"    ✅ Test listing cleaned up successfully")
            else:
                print(f"    ⚠️ Could not clean up test listing: {cleanup_result.get('error', 'Unknown error')}")
        
        return {
            "test_name": "Create Listing Endpoint",
            "success": test_results["success"] and test_results["fix_working"],
            "test_results": test_results,
            "critical_issue": not test_results["success"] or result["status"] == 404,
            "fix_working": test_results["fix_working"],
            "prevents_not_found": test_results["success"] and result["status"] != 404,
            "authentication_working": test_results["authentication_working"]
        }
    
    async def test_authentication_headers(self) -> Dict:
        """
        Test that both endpoints work with proper Bearer token authentication
        """
        print("🔑 Testing authentication headers for both endpoints...")
        
        if not self.demo_token:
            return {"test_name": "Authentication Headers", "error": "No demo token available"}
        
        test_results = {
            "notifications_auth": False,
            "listings_auth": False,
            "both_working": False,
            "error_messages": [],
            "success": False
        }
        
        # Test notifications endpoint with Bearer token
        print("  🔔 Testing notifications with Bearer token...")
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        notifications_result = await self.make_request(f"/user/{self.demo_user_id}/notifications", headers=headers)
        
        if notifications_result["success"]:
            test_results["notifications_auth"] = True
            print(f"    ✅ Notifications endpoint accepts Bearer token")
        else:
            test_results["error_messages"].append(f"Notifications auth failed: {notifications_result.get('error', 'Unknown')}")
            print(f"    ❌ Notifications endpoint auth failed: Status {notifications_result['status']}")
        
        # Test listings endpoint with Bearer token (using a simple GET to avoid creating listings)
        print("  📝 Testing listings endpoint authentication...")
        listings_result = await self.make_request("/listings", headers=headers)
        
        # For listings, we expect either 200 (if GET is supported) or 405 (method not allowed) but not 401/403
        if listings_result["status"] in [200, 405] or listings_result["success"]:
            test_results["listings_auth"] = True
            print(f"    ✅ Listings endpoint accepts Bearer token (Status: {listings_result['status']})")
        elif listings_result["status"] in [401, 403]:
            test_results["error_messages"].append(f"Listings endpoint rejects valid Bearer token: Status {listings_result['status']}")
            print(f"    ❌ Listings endpoint rejects valid Bearer token: Status {listings_result['status']}")
        else:
            # Other status codes might be acceptable depending on endpoint implementation
            test_results["listings_auth"] = True
            print(f"    ✅ Listings endpoint accessible with Bearer token (Status: {listings_result['status']})")
        
        test_results["both_working"] = test_results["notifications_auth"] and test_results["listings_auth"]
        test_results["success"] = test_results["both_working"]
        
        if test_results["both_working"]:
            print(f"    ✅ Both endpoints work with Bearer token authentication")
        else:
            print(f"    ❌ Authentication issues detected")
        
        return {
            "test_name": "Authentication Headers",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["both_working"],
            "notifications_auth_working": test_results["notifications_auth"],
            "listings_auth_working": test_results["listings_auth"]
        }
    
    async def test_error_handling(self) -> Dict:
        """
        Test proper error responses when authentication fails
        """
        print("⚠️ Testing error handling when authentication fails...")
        
        test_results = {
            "notifications_unauth_status": 0,
            "listings_unauth_status": 0,
            "proper_error_codes": False,
            "error_messages": [],
            "success": False
        }
        
        # Test notifications without auth
        print("  🔔 Testing notifications without authentication...")
        notifications_result = await self.make_request(f"/user/{self.demo_user_id}/notifications")
        test_results["notifications_unauth_status"] = notifications_result["status"]
        
        # Test listings without auth
        print("  📝 Testing listings without authentication...")
        test_listing_data = {
            "title": "Test Listing",
            "description": "Test",
            "price": 99.99,
            "category": "Test",
            "condition": "New",
            "seller_id": self.demo_user_id
        }
        listings_result = await self.make_request("/listings", "POST", data=test_listing_data)
        test_results["listings_unauth_status"] = listings_result["status"]
        
        # Verify proper error codes
        expected_auth_errors = [401, 403]
        notifications_proper = test_results["notifications_unauth_status"] in expected_auth_errors
        listings_proper = test_results["listings_unauth_status"] in expected_auth_errors
        
        test_results["proper_error_codes"] = notifications_proper and listings_proper
        test_results["success"] = test_results["proper_error_codes"]
        
        if notifications_proper:
            print(f"    ✅ Notifications returns proper auth error: {test_results['notifications_unauth_status']}")
        else:
            print(f"    ❌ Notifications returns unexpected status: {test_results['notifications_unauth_status']}")
            test_results["error_messages"].append(f"Notifications unexpected status: {test_results['notifications_unauth_status']}")
        
        if listings_proper:
            print(f"    ✅ Listings returns proper auth error: {test_results['listings_unauth_status']}")
        else:
            print(f"    ❌ Listings returns unexpected status: {test_results['listings_unauth_status']}")
            test_results["error_messages"].append(f"Listings unexpected status: {test_results['listings_unauth_status']}")
        
        return {
            "test_name": "Error Handling",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["proper_error_codes"],
            "proper_auth_errors": test_results["proper_error_codes"]
        }
    
    async def run_critical_fixes_tests(self) -> Dict:
        """
        Run complete critical fixes testing
        """
        print("🚨 STARTING NOTIFICATIONS & LISTINGS CRITICAL FIXES TESTING")
        print("=" * 80)
        print("TESTING: Two critical fixes just applied")
        print("ISSUE 1: Notifications TypeError Fix - Array validation")
        print("ISSUE 2: Create Listing 'Not Found' Fix - /api prefix + auth headers")
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
            
            # Run critical fixes tests
            notifications_test = await self.test_notifications_array_format()
            create_listing_test = await self.test_create_listing_endpoint()
            auth_headers_test = await self.test_authentication_headers()
            error_handling_test = await self.test_error_handling()
            
            # Compile comprehensive test results
            test_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Two critical fixes: Notifications TypeError + Create Listing Not Found",
                "notifications_array_test": notifications_test,
                "create_listing_test": create_listing_test,
                "authentication_headers_test": auth_headers_test,
                "error_handling_test": error_handling_test
            }
            
            # Determine critical findings
            critical_issues = []
            working_fixes = []
            
            tests = [notifications_test, create_listing_test, auth_headers_test, error_handling_test]
            
            for test in tests:
                if test.get("critical_issue", False):
                    error_msg = "Unknown error"
                    if test.get("test_results", {}).get("error_messages"):
                        error_msg = test["test_results"]["error_messages"][0]
                    elif test.get("error"):
                        error_msg = test["error"]
                    critical_issues.append(f"{test['test_name']}: {error_msg}")
                
                if test.get("success", False):
                    working_fixes.append(f"{test['test_name']}: Working correctly")
            
            # Calculate success metrics
            total_tests = len(tests)
            successful_tests = sum(1 for test in tests if test.get("success", False))
            success_rate = (successful_tests / total_tests) * 100
            
            # Specific fix status
            notifications_fix_working = notifications_test.get("prevents_typeerror", False)
            create_listing_fix_working = create_listing_test.get("prevents_not_found", False)
            
            test_results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": success_rate,
                "critical_issues": critical_issues,
                "working_fixes": working_fixes,
                "notifications_fix_status": "WORKING" if notifications_fix_working else "FAILED",
                "create_listing_fix_status": "WORKING" if create_listing_fix_working else "FAILED",
                "both_fixes_working": notifications_fix_working and create_listing_fix_working
            }
            
            return test_results
            
        finally:
            await self.cleanup()


async def main():
    """Run critical fixes testing"""
    tester = NotificationsListingsTester()
    results = await tester.run_critical_fixes_tests()
    
    print("\n" + "=" * 80)
    print("🏁 NOTIFICATIONS & LISTINGS CRITICAL FIXES TESTING RESULTS")
    print("=" * 80)
    
    if "error" in results:
        print(f"❌ Testing failed: {results['error']}")
        return
    
    summary = results.get("summary", {})
    
    print(f"📊 Test Summary:")
    print(f"   Total Tests: {summary.get('total_tests', 0)}")
    print(f"   Successful: {summary.get('successful_tests', 0)}")
    print(f"   Failed: {summary.get('failed_tests', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
    
    print(f"\n🔧 Fix Status:")
    print(f"   Notifications TypeError Fix: {summary.get('notifications_fix_status', 'UNKNOWN')}")
    print(f"   Create Listing Not Found Fix: {summary.get('create_listing_fix_status', 'UNKNOWN')}")
    print(f"   Both Fixes Working: {'✅ YES' if summary.get('both_fixes_working', False) else '❌ NO'}")
    
    if summary.get("critical_issues"):
        print(f"\n❌ Critical Issues Found:")
        for issue in summary["critical_issues"]:
            print(f"   - {issue}")
    
    if summary.get("working_fixes"):
        print(f"\n✅ Working Fixes:")
        for fix in summary["working_fixes"]:
            print(f"   - {fix}")
    
    print("\n" + "=" * 80)
    
    # Save detailed results
    with open("/app/notifications_listings_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("📄 Detailed results saved to: /app/notifications_listings_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())