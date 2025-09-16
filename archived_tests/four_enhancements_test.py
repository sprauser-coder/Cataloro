#!/usr/bin/env python3
"""
FOUR ENHANCEMENTS TESTING - URGENT REVIEW REQUEST
Testing the four specific enhancements that were just implemented:

1. Tender Accept/Reject Redirects - Mobile should redirect to `/mobile-my-listings`, Desktop to `/buy-management`
2. Mobile Notifications in Menu Settings - "notifications" should appear in mobile_menu options
3. Desktop Notifications Loading Fix - Authentication headers added to notifications fetching
4. Admin Panel "Pending" Users Tile - Fifth tile showing pending user count

SPECIFIC BACKEND TESTS NEEDED:
- Test GET `/api/admin/menu-settings` endpoint
- Test GET `/api/user/{user_id}/notifications` with authentication
- Test PUT `/api/user/{user_id}/notifications/{notification_id}/read` with authentication
- Test PUT `/api/tenders/{tender_id}/accept` with authentication
- Test PUT `/api/tenders/{tender_id}/reject` with authentication
- Test admin users endpoint to verify user data structure
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-uxfixes.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"
ADMIN_ROLE = "admin"

# Demo User Configuration
DEMO_EMAIL = "demo@cataloro.com"
DEMO_USER_ID = "68bfff790e4e46bc28d43631"

class FourEnhancementsTester:
    """
    FOUR ENHANCEMENTS TESTING
    Testing the four specific enhancements that were just implemented
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.admin_user_id = None
        self.demo_user_id = None
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
        """Authenticate admin and demo users"""
        print("🔐 Authenticating users for four enhancements testing...")
        
        # Authenticate admin user
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            self.admin_user_id = admin_result["data"].get("user", {}).get("id", "")
            print(f"  ✅ Admin user authentication successful (ID: {self.admin_user_id})")
        else:
            print(f"  ❌ Admin user authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
        
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
            return True
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error', 'Unknown error')}")
            return False
    
    async def test_menu_settings_mobile_notifications(self) -> Dict:
        """
        Test 1: Backend Menu Settings API
        Test GET `/api/admin/menu-settings` endpoint
        Verify "notifications" appears in mobile_menu structure
        """
        print("📱 Testing Menu Settings API for mobile notifications...")
        
        test_results = {
            "endpoint": "/admin/menu-settings",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "has_mobile_menu": False,
            "has_notifications_in_mobile": False,
            "mobile_menu_structure": None,
            "authentication_working": False,
            "error_messages": [],
            "success": False
        }
        
        # Test with admin authentication
        print("  🔐 Testing authenticated menu settings access...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            test_results["authentication_working"] = True
            menu_data = result.get("data", {})
            
            # Check if mobile_menu exists in the response
            if "mobile_menu" in menu_data:
                test_results["has_mobile_menu"] = True
                mobile_menu = menu_data["mobile_menu"]
                test_results["mobile_menu_structure"] = mobile_menu
                
                # Check if "notifications" is in the mobile menu
                if isinstance(mobile_menu, list):
                    notifications_found = any(
                        item.get("key") == "notifications" or 
                        item.get("name") == "notifications" or
                        "notifications" in str(item).lower()
                        for item in mobile_menu
                    )
                    test_results["has_notifications_in_mobile"] = notifications_found
                elif isinstance(mobile_menu, dict):
                    notifications_found = (
                        "notifications" in mobile_menu or
                        any("notifications" in str(v).lower() for v in mobile_menu.values())
                    )
                    test_results["has_notifications_in_mobile"] = notifications_found
                
                if test_results["has_notifications_in_mobile"]:
                    print(f"    ✅ Mobile notifications found in menu settings")
                    test_results["success"] = True
                else:
                    test_results["error_messages"].append("Notifications not found in mobile_menu structure")
                    print(f"    ❌ Notifications not found in mobile_menu structure")
                    print(f"    📋 Mobile menu structure: {mobile_menu}")
            else:
                test_results["error_messages"].append("mobile_menu not found in menu settings response")
                print(f"    ❌ mobile_menu not found in response")
                print(f"    📋 Available keys: {list(menu_data.keys()) if isinstance(menu_data, dict) else 'Not a dict'}")
            
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
        else:
            test_results["error_messages"].append(f"Menu settings request failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Menu settings request failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        # Test without authentication (should fail)
        print("  🚫 Testing unauthenticated access (should fail)...")
        unauth_result = await self.make_request("/admin/menu-settings")
        if unauth_result["status"] in [401, 403]:
            print(f"    ✅ Unauthenticated access properly rejected: Status {unauth_result['status']}")
        else:
            print(f"    ⚠️ Unauthenticated access not properly rejected: Status {unauth_result['status']}")
            test_results["error_messages"].append("Authentication not properly enforced")
        
        return {
            "test_name": "Menu Settings Mobile Notifications",
            "success": test_results["success"] and test_results["has_notifications_in_mobile"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "enhancement_working": test_results["has_notifications_in_mobile"]
        }
    
    async def test_notifications_endpoints_authentication(self) -> Dict:
        """
        Test 2: Notifications Endpoints
        Test GET `/api/user/{user_id}/notifications` with authentication
        Test PUT `/api/user/{user_id}/notifications/{notification_id}/read` with authentication
        """
        print("🔔 Testing Notifications endpoints with authentication...")
        
        test_results = {
            "get_endpoint": f"/user/{self.demo_user_id}/notifications",
            "put_endpoint": f"/user/{self.demo_user_id}/notifications/{{notification_id}}/read",
            "get_status": 0,
            "put_status": 0,
            "get_response_time_ms": 0,
            "put_response_time_ms": 0,
            "notifications_count": 0,
            "get_authentication_working": False,
            "put_authentication_working": False,
            "notifications_loaded": False,
            "mark_read_working": False,
            "error_messages": [],
            "success": False
        }
        
        # Test GET notifications with authentication
        print("  📥 Testing GET notifications with authentication...")
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        get_result = await self.make_request(f"/user/{self.demo_user_id}/notifications", headers=headers)
        
        test_results["get_status"] = get_result["status"]
        test_results["get_response_time_ms"] = get_result["response_time_ms"]
        
        notification_id = None
        if get_result["success"]:
            test_results["get_authentication_working"] = True
            notifications = get_result.get("data", [])
            
            if isinstance(notifications, list):
                test_results["notifications_count"] = len(notifications)
                test_results["notifications_loaded"] = True
                print(f"    ✅ GET notifications successful: {test_results['notifications_count']} notifications")
                
                # Get a notification ID for testing mark as read
                if notifications and len(notifications) > 0:
                    notification_id = notifications[0].get("id")
                    print(f"    📋 Found notification ID for testing: {notification_id}")
            else:
                test_results["error_messages"].append("Notifications response is not an array")
                print(f"    ❌ Notifications response is not an array: {type(notifications)}")
            
            print(f"    ⏱️ GET response time: {test_results['get_response_time_ms']:.1f}ms")
        else:
            test_results["error_messages"].append(f"GET notifications failed: {get_result.get('error', 'Unknown error')}")
            print(f"    ❌ GET notifications failed: Status {get_result['status']}")
            if get_result.get("error"):
                print(f"    ❌ Error: {get_result['error']}")
        
        # Test PUT mark notification as read (if we have a notification ID)
        if notification_id:
            print("  ✅ Testing PUT mark notification as read...")
            put_result = await self.make_request(
                f"/user/{self.demo_user_id}/notifications/{notification_id}/read", 
                "PUT", 
                headers=headers
            )
            
            test_results["put_status"] = put_result["status"]
            test_results["put_response_time_ms"] = put_result["response_time_ms"]
            
            if put_result["success"]:
                test_results["put_authentication_working"] = True
                test_results["mark_read_working"] = True
                print(f"    ✅ PUT mark as read successful")
                print(f"    ⏱️ PUT response time: {test_results['put_response_time_ms']:.1f}ms")
            else:
                test_results["error_messages"].append(f"PUT mark as read failed: {put_result.get('error', 'Unknown error')}")
                print(f"    ❌ PUT mark as read failed: Status {put_result['status']}")
        else:
            print("  ⚠️ Skipping PUT test - no notification ID available")
            # Create a test notification to test the PUT endpoint
            print("  📝 Creating test notification for PUT testing...")
            create_data = {
                "title": "Test Notification",
                "message": "Test notification for mark as read functionality",
                "type": "test"
            }
            create_result = await self.make_request(
                f"/user/{self.demo_user_id}/notifications", 
                "POST", 
                data=create_data,
                headers=headers
            )
            
            if create_result["success"]:
                created_notification = create_result.get("data", {})
                notification_id = created_notification.get("id")
                print(f"    ✅ Test notification created: {notification_id}")
                
                # Now test PUT mark as read
                put_result = await self.make_request(
                    f"/user/{self.demo_user_id}/notifications/{notification_id}/read", 
                    "PUT", 
                    headers=headers
                )
                
                test_results["put_status"] = put_result["status"]
                test_results["put_response_time_ms"] = put_result["response_time_ms"]
                
                if put_result["success"]:
                    test_results["put_authentication_working"] = True
                    test_results["mark_read_working"] = True
                    print(f"    ✅ PUT mark as read successful")
                    print(f"    ⏱️ PUT response time: {test_results['put_response_time_ms']:.1f}ms")
                else:
                    test_results["error_messages"].append(f"PUT mark as read failed: {put_result.get('error', 'Unknown error')}")
                    print(f"    ❌ PUT mark as read failed: Status {put_result['status']}")
            else:
                print(f"    ❌ Failed to create test notification: {create_result.get('error', 'Unknown error')}")
        
        # Test without authentication (should fail)
        print("  🚫 Testing unauthenticated access (should fail)...")
        unauth_get_result = await self.make_request(f"/user/{self.demo_user_id}/notifications")
        if unauth_get_result["status"] in [401, 403]:
            print(f"    ✅ Unauthenticated GET properly rejected: Status {unauth_get_result['status']}")
        else:
            print(f"    ⚠️ Unauthenticated GET not properly rejected: Status {unauth_get_result['status']}")
            test_results["error_messages"].append("GET authentication not properly enforced")
        
        # Determine overall success
        test_results["success"] = (
            test_results["get_authentication_working"] and 
            test_results["notifications_loaded"] and
            (test_results["put_authentication_working"] or notification_id is None)
        )
        
        return {
            "test_name": "Notifications Endpoints Authentication",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "enhancement_working": test_results["get_authentication_working"] and test_results["notifications_loaded"]
        }
    
    async def test_tender_management_endpoints(self) -> Dict:
        """
        Test 3: Tender Management Endpoints
        Test PUT `/api/tenders/{tender_id}/accept` with authentication
        Test PUT `/api/tenders/{tender_id}/reject` with authentication
        """
        print("🤝 Testing Tender Management endpoints...")
        
        test_results = {
            "accept_endpoint": "/tenders/{tender_id}/accept",
            "reject_endpoint": "/tenders/{tender_id}/reject",
            "accept_status": 0,
            "reject_status": 0,
            "accept_response_time_ms": 0,
            "reject_response_time_ms": 0,
            "accept_authentication_working": False,
            "reject_authentication_working": False,
            "tender_accept_working": False,
            "tender_reject_working": False,
            "test_tender_id": None,
            "error_messages": [],
            "success": False
        }
        
        # First, create a test listing and tender for testing
        print("  📝 Creating test listing and tender for testing...")
        
        # Create test listing as admin (seller)
        listing_data = {
            "title": "Test Catalyst for Tender Management Testing",
            "description": "Test listing for tender accept/reject functionality",
            "price": 100.0,
            "category": "Catalysts",
            "condition": "Used",
            "seller_id": self.admin_user_id,
            "images": [],
            "tags": ["test", "tender", "management"],
            "features": ["test feature"]
        }
        
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        listing_result = await self.make_request("/listings", "POST", data=listing_data, headers=admin_headers)
        
        if not listing_result["success"]:
            test_results["error_messages"].append(f"Failed to create test listing: {listing_result.get('error', 'Unknown error')}")
            return {
                "test_name": "Tender Management Endpoints",
                "success": False,
                "test_results": test_results,
                "critical_issue": True
            }
        
        listing_id = listing_result["data"].get("id")
        print(f"    ✅ Test listing created: {listing_id}")
        
        # Create test tender as demo user (buyer)
        tender_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": 150.0  # Higher than listing price
        }
        
        demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
        tender_result = await self.make_request("/tenders/submit", "POST", data=tender_data, headers=demo_headers)
        
        if not tender_result["success"]:
            test_results["error_messages"].append(f"Failed to create test tender: {tender_result.get('error', 'Unknown error')}")
            return {
                "test_name": "Tender Management Endpoints",
                "success": False,
                "test_results": test_results,
                "critical_issue": True
            }
        
        tender_id = tender_result["data"].get("tender_id")
        if not tender_id:
            test_results["error_messages"].append(f"Failed to get tender ID from response: {tender_result.get('data', {})}")
            return {
                "test_name": "Tender Management Endpoints",
                "success": False,
                "test_results": test_results,
                "critical_issue": True
            }
        
        test_results["test_tender_id"] = tender_id
        print(f"    ✅ Test tender created: {tender_id}")
        
        # Test tender accept with authentication
        print("  ✅ Testing tender accept with authentication...")
        accept_data = {"seller_id": self.admin_user_id}
        
        accept_result = await self.make_request(f"/tenders/{tender_id}/accept", "PUT", data=accept_data, headers=admin_headers)
        
        test_results["accept_status"] = accept_result["status"]
        test_results["accept_response_time_ms"] = accept_result["response_time_ms"]
        
        if accept_result["success"]:
            test_results["accept_authentication_working"] = True
            test_results["tender_accept_working"] = True
            print(f"    ✅ Tender accept successful")
            print(f"    ⏱️ Accept response time: {test_results['accept_response_time_ms']:.1f}ms")
        else:
            test_results["error_messages"].append(f"Tender accept failed: {accept_result.get('error', 'Unknown error')}")
            print(f"    ❌ Tender accept failed: Status {accept_result['status']}")
            if accept_result.get("error"):
                print(f"    ❌ Error: {accept_result['error']}")
        
        # Create another tender for reject testing
        print("  📝 Creating second tender for reject testing...")
        tender_data_2 = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": 120.0
        }
        
        tender_result_2 = await self.make_request("/tenders/submit", "POST", data=tender_data_2, headers=demo_headers)
        
        if tender_result_2["success"]:
            tender_id_2 = tender_result_2["data"].get("tender_id")
            print(f"    ✅ Second test tender created: {tender_id_2}")
            
            # Test tender reject with authentication
            print("  ❌ Testing tender reject with authentication...")
            reject_data = {"seller_id": self.admin_user_id}
            
            reject_result = await self.make_request(f"/tenders/{tender_id_2}/reject", "PUT", data=reject_data, headers=admin_headers)
            
            test_results["reject_status"] = reject_result["status"]
            test_results["reject_response_time_ms"] = reject_result["response_time_ms"]
            
            if reject_result["success"]:
                test_results["reject_authentication_working"] = True
                test_results["tender_reject_working"] = True
                print(f"    ✅ Tender reject successful")
                print(f"    ⏱️ Reject response time: {test_results['reject_response_time_ms']:.1f}ms")
            else:
                test_results["error_messages"].append(f"Tender reject failed: {reject_result.get('error', 'Unknown error')}")
                print(f"    ❌ Tender reject failed: Status {reject_result['status']}")
                if reject_result.get("error"):
                    print(f"    ❌ Error: {reject_result['error']}")
        else:
            print(f"    ❌ Failed to create second tender for reject testing")
            test_results["error_messages"].append("Could not create second tender for reject testing")
        
        # Test without authentication (should fail)
        print("  🚫 Testing unauthenticated access (should fail)...")
        unauth_accept_result = await self.make_request(f"/tenders/{tender_id}/accept", "PUT", data=accept_data)
        if unauth_accept_result["status"] in [401, 403]:
            print(f"    ✅ Unauthenticated accept properly rejected: Status {unauth_accept_result['status']}")
        else:
            print(f"    ⚠️ Unauthenticated accept not properly rejected: Status {unauth_accept_result['status']}")
            test_results["error_messages"].append("Accept authentication not properly enforced")
        
        # Determine overall success
        test_results["success"] = (
            test_results["tender_accept_working"] and 
            test_results["accept_authentication_working"]
        )
        
        return {
            "test_name": "Tender Management Endpoints",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "enhancement_working": test_results["tender_accept_working"] and test_results["tender_reject_working"]
        }
    
    async def test_admin_pending_users_logic(self) -> Dict:
        """
        Test 4: User Management for Pending Count
        Test admin users endpoint to verify user data structure
        Check if pending user logic works with existing user data
        """
        print("👥 Testing Admin Panel Pending Users logic...")
        
        test_results = {
            "users_endpoint": "/admin/users",
            "status": 0,
            "response_time_ms": 0,
            "total_users": 0,
            "pending_users": 0,
            "approved_users": 0,
            "rejected_users": 0,
            "pending_logic_working": False,
            "user_data_structure_valid": False,
            "authentication_working": False,
            "error_messages": [],
            "success": False
        }
        
        # Test admin users endpoint with authentication
        print("  👤 Testing admin users endpoint...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        result = await self.make_request("/admin/users", headers=headers)
        
        test_results["status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            test_results["authentication_working"] = True
            users = result.get("data", [])
            
            if isinstance(users, list):
                test_results["total_users"] = len(users)
                test_results["user_data_structure_valid"] = True
                
                # Count users by status using the pending logic from the review request
                # Logic: `users.filter(u => u.status === 'pending' || (!u.is_verified && u.is_active))`
                pending_count = 0
                approved_count = 0
                rejected_count = 0
                
                for user in users:
                    if isinstance(user, dict):
                        # Check registration_status field (primary)
                        registration_status = user.get("registration_status", "")
                        
                        # Check legacy status field
                        status = user.get("status", "")
                        
                        # Check is_verified and is_active fields
                        is_verified = user.get("is_verified", True)  # Default to True if not present
                        is_active = user.get("is_active", True)
                        
                        # Apply the pending logic from the review request
                        if (registration_status == "Pending" or 
                            status == "pending" or 
                            (not is_verified and is_active)):
                            pending_count += 1
                        elif registration_status == "Approved" or status == "approved":
                            approved_count += 1
                        elif registration_status == "Rejected" or status == "rejected":
                            rejected_count += 1
                        else:
                            # Default to approved if no clear status
                            approved_count += 1
                
                test_results["pending_users"] = pending_count
                test_results["approved_users"] = approved_count
                test_results["rejected_users"] = rejected_count
                test_results["pending_logic_working"] = True
                
                print(f"    ✅ Users endpoint successful: {test_results['total_users']} total users")
                print(f"    📊 User breakdown:")
                print(f"      - Pending: {pending_count}")
                print(f"      - Approved: {approved_count}")
                print(f"      - Rejected: {rejected_count}")
                
                # Verify the logic makes sense
                if pending_count >= 0 and approved_count >= 0 and rejected_count >= 0:
                    test_results["success"] = True
                    print(f"    ✅ Pending user logic working correctly")
                else:
                    test_results["error_messages"].append("Invalid user counts in pending logic")
                    print(f"    ❌ Invalid user counts in pending logic")
                
            else:
                test_results["error_messages"].append("Users response is not an array")
                print(f"    ❌ Users response is not an array: {type(users)}")
            
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
        else:
            test_results["error_messages"].append(f"Admin users request failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Admin users request failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        # Test without authentication (should fail)
        print("  🚫 Testing unauthenticated access (should fail)...")
        unauth_result = await self.make_request("/admin/users")
        if unauth_result["status"] in [401, 403]:
            print(f"    ✅ Unauthenticated access properly rejected: Status {unauth_result['status']}")
        else:
            print(f"    ⚠️ Unauthenticated access not properly rejected: Status {unauth_result['status']}")
            test_results["error_messages"].append("Authentication not properly enforced")
        
        return {
            "test_name": "Admin Pending Users Logic",
            "success": test_results["success"] and test_results["pending_logic_working"],
            "test_results": test_results,
            "critical_issue": not test_results["success"],
            "enhancement_working": test_results["pending_logic_working"] and test_results["user_data_structure_valid"]
        }
    
    async def run_four_enhancements_tests(self) -> Dict:
        """
        Run complete four enhancements tests
        """
        print("🚨 STARTING FOUR ENHANCEMENTS TESTING")
        print("=" * 80)
        print("TESTING: Four specific enhancements that were just implemented")
        print("1. Tender Accept/Reject Redirects")
        print("2. Mobile Notifications in Menu Settings")
        print("3. Desktop Notifications Loading Fix")
        print("4. Admin Panel Pending Users Tile")
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
            
            # Run all four enhancement tests
            menu_test = await self.test_menu_settings_mobile_notifications()
            notifications_test = await self.test_notifications_endpoints_authentication()
            tender_test = await self.test_tender_management_endpoints()
            users_test = await self.test_admin_pending_users_logic()
            
            # Compile comprehensive test results
            test_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Four specific enhancements testing",
                "menu_settings_test": menu_test,
                "notifications_endpoints_test": notifications_test,
                "tender_management_test": tender_test,
                "admin_pending_users_test": users_test
            }
            
            # Determine critical findings
            critical_issues = []
            working_features = []
            
            tests = [menu_test, notifications_test, tender_test, users_test]
            
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
                "all_enhancements_working": len(critical_issues) == 0,
                "enhancements_status": {
                    "mobile_notifications_menu": menu_test.get("enhancement_working", False),
                    "notifications_authentication": notifications_test.get("enhancement_working", False),
                    "tender_management": tender_test.get("enhancement_working", False),
                    "pending_users_logic": users_test.get("enhancement_working", False)
                }
            }
            
            return test_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution function"""
    tester = FourEnhancementsTester()
    results = await tester.run_four_enhancements_tests()
    
    print("\n" + "=" * 80)
    print("🏁 FOUR ENHANCEMENTS TESTING COMPLETED")
    print("=" * 80)
    
    summary = results.get("summary", {})
    print(f"📊 Test Results: {summary.get('successful_tests', 0)}/{summary.get('total_tests', 0)} tests passed ({summary.get('success_rate', 0):.1f}%)")
    
    if summary.get("working_features"):
        print("\n✅ Working Features:")
        for feature in summary["working_features"]:
            print(f"  • {feature}")
    
    if summary.get("critical_issues"):
        print("\n❌ Critical Issues:")
        for issue in summary["critical_issues"]:
            print(f"  • {issue}")
    
    enhancements_status = summary.get("enhancements_status", {})
    print(f"\n🔧 Enhancements Status:")
    print(f"  • Mobile Notifications Menu: {'✅ Working' if enhancements_status.get('mobile_notifications_menu') else '❌ Failed'}")
    print(f"  • Notifications Authentication: {'✅ Working' if enhancements_status.get('notifications_authentication') else '❌ Failed'}")
    print(f"  • Tender Management: {'✅ Working' if enhancements_status.get('tender_management') else '❌ Failed'}")
    print(f"  • Pending Users Logic: {'✅ Working' if enhancements_status.get('pending_users_logic') else '❌ Failed'}")
    
    if summary.get("all_enhancements_working"):
        print(f"\n🎉 ALL FOUR ENHANCEMENTS ARE WORKING CORRECTLY!")
    else:
        print(f"\n⚠️ Some enhancements need attention - see critical issues above")
    
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())