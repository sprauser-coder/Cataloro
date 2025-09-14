#!/usr/bin/env python3
"""
Admin User Specific Testing
Testing admin user authentication, listings visibility, database state, and message functionality
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://marketplace-fix-9.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"
ADMIN_USERNAME = "sash_admin"

class AdminUserTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.admin_user_data = None
        self.admin_user_id = None
        
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
    
    async def test_admin_user_authentication(self) -> Dict:
        """Test admin login with admin@cataloro.com / admin_password"""
        print("🔐 Testing admin user authentication...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            token = result["data"].get("token", "")
            
            # Store admin data for subsequent tests
            self.admin_token = token
            self.admin_user_data = user_data
            self.admin_user_id = user_data.get("id")
            
            # Verify admin user properties
            email_correct = user_data.get("email") == ADMIN_EMAIL
            username_correct = user_data.get("username") == ADMIN_USERNAME
            role_correct = user_data.get("role") == "admin" or user_data.get("user_role") == "Admin"
            is_active = user_data.get("is_active", True)
            
            print(f"  ✅ Admin login successful")
            print(f"  📧 Email: {user_data.get('email')} ({'✅' if email_correct else '❌'})")
            print(f"  👤 Username: {user_data.get('username')} ({'✅' if username_correct else '❌'})")
            print(f"  🔑 Role: {user_data.get('role', user_data.get('user_role'))} ({'✅' if role_correct else '❌'})")
            print(f"  🟢 Active: {is_active} ({'✅' if is_active else '❌'})")
            print(f"  🆔 Admin User ID: {self.admin_user_id}")
            
            return {
                "test_name": "Admin User Authentication",
                "login_successful": True,
                "response_time_ms": result["response_time_ms"],
                "admin_email_correct": email_correct,
                "admin_username_correct": username_correct,
                "admin_role_correct": role_correct,
                "admin_is_active": is_active,
                "admin_user_id": self.admin_user_id,
                "user_data": user_data,
                "token_received": bool(token),
                "all_admin_properties_correct": email_correct and username_correct and role_correct and is_active
            }
        else:
            print(f"  ❌ Admin login failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Admin User Authentication",
                "login_successful": False,
                "response_time_ms": result["response_time_ms"],
                "error": result.get("error", "Login failed"),
                "status": result["status"]
            }
    
    async def test_admin_listings_visibility(self) -> Dict:
        """Check if admin user has any listings and test GET /api/user/my-listings/{admin_user_id} endpoint"""
        print("📋 Testing admin listings visibility...")
        
        if not self.admin_user_id:
            return {
                "test_name": "Admin Listings Visibility",
                "error": "Admin user ID not available - authentication required first"
            }
        
        # Test the my-listings endpoint for admin user
        my_listings_result = await self.make_request(f"/user/my-listings/{self.admin_user_id}")
        
        if my_listings_result["success"]:
            admin_listings = my_listings_result["data"]
            listing_count = len(admin_listings) if isinstance(admin_listings, list) else 0
            
            print(f"  ✅ Admin my-listings endpoint working")
            print(f"  📊 Admin has {listing_count} listings")
            
            # Check if admin has any listings in the general marketplace
            browse_result = await self.make_request("/marketplace/browse")
            admin_listings_in_browse = []
            
            if browse_result["success"]:
                all_listings = browse_result["data"]
                admin_listings_in_browse = [
                    listing for listing in all_listings 
                    if listing.get("seller_id") == self.admin_user_id
                ]
                
                print(f"  📋 Admin listings visible in browse: {len(admin_listings_in_browse)}")
            
            # Test management center visibility (if endpoint exists)
            management_result = await self.make_request("/admin/listings")
            management_listings = []
            
            if management_result["success"]:
                management_listings = management_result["data"]
                admin_management_listings = [
                    listing for listing in management_listings 
                    if listing.get("seller_id") == self.admin_user_id
                ]
                print(f"  🏢 Admin listings in management center: {len(admin_management_listings)}")
            
            return {
                "test_name": "Admin Listings Visibility",
                "my_listings_endpoint_working": True,
                "response_time_ms": my_listings_result["response_time_ms"],
                "admin_listings_count": listing_count,
                "admin_listings_in_browse": len(admin_listings_in_browse),
                "management_center_accessible": management_result["success"],
                "admin_listings_data": admin_listings,
                "listings_visible_in_management": management_result["success"]
            }
        else:
            print(f"  ❌ Admin my-listings endpoint failed: {my_listings_result.get('error')}")
            return {
                "test_name": "Admin Listings Visibility",
                "my_listings_endpoint_working": False,
                "response_time_ms": my_listings_result["response_time_ms"],
                "error": my_listings_result.get("error"),
                "status": my_listings_result["status"]
            }
    
    async def test_admin_user_database_state(self) -> Dict:
        """Check what admin user data exists in the database"""
        print("🗄️ Testing admin user database state...")
        
        if not self.admin_user_id:
            return {
                "test_name": "Admin User Database State",
                "error": "Admin user ID not available - authentication required first"
            }
        
        # Get admin user profile
        profile_result = await self.make_request(f"/auth/profile/{self.admin_user_id}")
        
        if profile_result["success"]:
            profile_data = profile_result["data"]
            
            # Check essential admin fields
            has_id = bool(profile_data.get("id"))
            has_email = bool(profile_data.get("email"))
            has_username = bool(profile_data.get("username"))
            has_role = bool(profile_data.get("role") or profile_data.get("user_role"))
            has_full_name = bool(profile_data.get("full_name"))
            is_active = profile_data.get("is_active", True)
            registration_status = profile_data.get("registration_status", "Unknown")
            
            print(f"  ✅ Admin profile accessible")
            print(f"  🆔 Has ID: {has_id} ({profile_data.get('id')})")
            print(f"  📧 Has Email: {has_email} ({profile_data.get('email')})")
            print(f"  👤 Has Username: {has_username} ({profile_data.get('username')})")
            print(f"  🔑 Has Role: {has_role} ({profile_data.get('role', profile_data.get('user_role'))})")
            print(f"  📝 Has Full Name: {has_full_name} ({profile_data.get('full_name')})")
            print(f"  🟢 Is Active: {is_active}")
            print(f"  ✅ Registration Status: {registration_status}")
            
            # Check for any missing admin data
            missing_fields = []
            if not has_id: missing_fields.append("id")
            if not has_email: missing_fields.append("email")
            if not has_username: missing_fields.append("username")
            if not has_role: missing_fields.append("role")
            if not has_full_name: missing_fields.append("full_name")
            
            return {
                "test_name": "Admin User Database State",
                "profile_accessible": True,
                "response_time_ms": profile_result["response_time_ms"],
                "admin_id": profile_data.get("id"),
                "admin_email": profile_data.get("email"),
                "admin_username": profile_data.get("username"),
                "admin_role": profile_data.get("role", profile_data.get("user_role")),
                "admin_full_name": profile_data.get("full_name"),
                "admin_is_active": is_active,
                "registration_status": registration_status,
                "has_all_essential_fields": len(missing_fields) == 0,
                "missing_fields": missing_fields,
                "complete_profile_data": profile_data
            }
        else:
            print(f"  ❌ Admin profile not accessible: {profile_result.get('error')}")
            return {
                "test_name": "Admin User Database State",
                "profile_accessible": False,
                "response_time_ms": profile_result["response_time_ms"],
                "error": profile_result.get("error"),
                "status": profile_result["status"]
            }
    
    async def test_admin_messages_historical_data(self) -> Dict:
        """Check if admin has historical messages that should be visible"""
        print("💬 Testing admin messages historical data...")
        
        if not self.admin_user_id:
            return {
                "test_name": "Admin Messages Historical Data",
                "error": "Admin user ID not available - authentication required first"
            }
        
        # Test admin messages endpoint
        admin_messages_result = await self.make_request(f"/user/{self.admin_user_id}/messages")
        
        admin_message_count = 0
        admin_messages_accessible = False
        
        if admin_messages_result["success"]:
            admin_messages = admin_messages_result["data"]
            admin_message_count = len(admin_messages) if isinstance(admin_messages, list) else 0
            admin_messages_accessible = True
            
            print(f"  ✅ Admin messages endpoint accessible")
            print(f"  💬 Admin has {admin_message_count} messages")
        else:
            print(f"  ❌ Admin messages endpoint failed: {admin_messages_result.get('error')}")
        
        # Compare with demo user message count for reference
        demo_user_id = "68bfff790e4e46bc28d43631"  # Fixed demo user ID from backend
        demo_messages_result = await self.make_request(f"/user/{demo_user_id}/messages")
        
        demo_message_count = 0
        demo_messages_accessible = False
        
        if demo_messages_result["success"]:
            demo_messages = demo_messages_result["data"]
            demo_message_count = len(demo_messages) if isinstance(demo_messages, list) else 0
            demo_messages_accessible = True
            
            print(f"  📊 Demo user has {demo_message_count} messages for comparison")
        else:
            print(f"  ⚠️ Demo user messages not accessible for comparison")
        
        # Check for data access issues
        data_access_issues = []
        if not admin_messages_accessible:
            data_access_issues.append("Admin messages endpoint not accessible")
        
        if admin_messages_accessible and admin_message_count == 0 and demo_message_count > 0:
            data_access_issues.append("Admin has no messages while demo user has messages - potential data filtering issue")
        
        return {
            "test_name": "Admin Messages Historical Data",
            "admin_messages_accessible": admin_messages_accessible,
            "admin_message_count": admin_message_count,
            "demo_message_count": demo_message_count,
            "demo_messages_accessible": demo_messages_accessible,
            "message_count_comparison": f"Admin: {admin_message_count}, Demo: {demo_message_count}",
            "potential_data_access_issues": data_access_issues,
            "has_data_access_issues": len(data_access_issues) > 0,
            "admin_messages_response_time_ms": admin_messages_result.get("response_time_ms", 0),
            "admin_messages_data": admin_messages_result.get("data", []) if admin_messages_accessible else []
        }
    
    async def test_cross_platform_message_visibility(self) -> Dict:
        """Test admin message visibility differences and cross-platform functionality"""
        print("🔄 Testing cross-platform message visibility...")
        
        if not self.admin_user_id:
            return {
                "test_name": "Cross-platform Message Visibility",
                "error": "Admin user ID not available - authentication required first"
            }
        
        # Test admin message sending capability
        test_message_data = {
            "recipient_id": "68bfff790e4e46bc28d43631",  # Demo user
            "content": "Test message from admin user for visibility testing",
            "sender_id": self.admin_user_id
        }
        
        send_message_result = await self.make_request(f"/user/{self.admin_user_id}/messages", "POST", data=test_message_data)
        
        message_sent_successfully = send_message_result["success"]
        sent_message_id = None
        
        if message_sent_successfully:
            sent_message_id = send_message_result["data"].get("id")
            print(f"  ✅ Admin can send messages (Message ID: {sent_message_id})")
        else:
            print(f"  ❌ Admin cannot send messages: {send_message_result.get('error')}")
        
        # Test admin message receiving capability
        # Send a message TO admin from demo user
        demo_to_admin_data = {
            "recipient_id": self.admin_user_id,
            "content": "Test message to admin user for visibility testing",
            "sender_id": "68bfff790e4e46bc28d43631"
        }
        
        receive_test_result = await self.make_request("/user/68bfff790e4e46bc28d43631/messages", "POST", data=demo_to_admin_data)
        
        message_received_successfully = receive_test_result["success"]
        received_message_id = None
        
        if message_received_successfully:
            received_message_id = receive_test_result["data"].get("id")
            print(f"  ✅ Admin can receive messages (Message ID: {received_message_id})")
        else:
            print(f"  ❌ Admin cannot receive messages: {receive_test_result.get('error')}")
        
        # Verify messages appear in admin's message list
        await asyncio.sleep(1)  # Brief delay to ensure message persistence
        
        updated_admin_messages_result = await self.make_request(f"/user/{self.admin_user_id}/messages")
        
        admin_can_see_messages = False
        updated_message_count = 0
        
        if updated_admin_messages_result["success"]:
            updated_messages = updated_admin_messages_result["data"]
            updated_message_count = len(updated_messages) if isinstance(updated_messages, list) else 0
            admin_can_see_messages = updated_message_count > 0
            
            print(f"  📊 Admin now has {updated_message_count} total messages")
        
        # Check for admin-specific data filtering issues
        filtering_issues = []
        
        if message_sent_successfully and not admin_can_see_messages:
            filtering_issues.append("Admin sent messages but cannot see them in message list")
        
        if message_received_successfully and not admin_can_see_messages:
            filtering_issues.append("Messages sent to admin but admin cannot see them")
        
        if not message_sent_successfully and not message_received_successfully:
            filtering_issues.append("Admin cannot send or receive messages - complete messaging failure")
        
        return {
            "test_name": "Cross-platform Message Visibility",
            "admin_can_send_messages": message_sent_successfully,
            "admin_can_receive_messages": message_received_successfully,
            "admin_can_see_messages": admin_can_see_messages,
            "sent_message_id": sent_message_id,
            "received_message_id": received_message_id,
            "updated_admin_message_count": updated_message_count,
            "admin_specific_filtering_issues": filtering_issues,
            "has_filtering_issues": len(filtering_issues) > 0,
            "messaging_fully_functional": message_sent_successfully and message_received_successfully and admin_can_see_messages,
            "send_response_time_ms": send_message_result.get("response_time_ms", 0),
            "receive_response_time_ms": receive_test_result.get("response_time_ms", 0)
        }
    
    async def test_admin_specific_data_filtering(self) -> Dict:
        """Test if there are any admin-specific data filtering issues"""
        print("🔍 Testing admin-specific data filtering issues...")
        
        if not self.admin_user_id:
            return {
                "test_name": "Admin Specific Data Filtering",
                "error": "Admin user ID not available - authentication required first"
            }
        
        filtering_tests = []
        
        # Test 1: Admin access to all users (should work for admin)
        all_users_result = await self.make_request("/admin/users")
        
        if all_users_result["success"]:
            all_users = all_users_result["data"]
            user_count = len(all_users) if isinstance(all_users, list) else 0
            admin_in_list = any(user.get("id") == self.admin_user_id for user in all_users)
            
            filtering_tests.append({
                "test": "Admin Access to All Users",
                "success": True,
                "user_count": user_count,
                "admin_in_user_list": admin_in_list,
                "response_time_ms": all_users_result["response_time_ms"]
            })
            
            print(f"  ✅ Admin can access all users ({user_count} users, admin in list: {admin_in_list})")
        else:
            filtering_tests.append({
                "test": "Admin Access to All Users",
                "success": False,
                "error": all_users_result.get("error"),
                "response_time_ms": all_users_result["response_time_ms"]
            })
            print(f"  ❌ Admin cannot access all users: {all_users_result.get('error')}")
        
        # Test 2: Admin access to all listings (should work for admin)
        all_listings_result = await self.make_request("/admin/listings")
        
        if all_listings_result["success"]:
            all_listings = all_listings_result["data"]
            listing_count = len(all_listings) if isinstance(all_listings, list) else 0
            
            filtering_tests.append({
                "test": "Admin Access to All Listings",
                "success": True,
                "listing_count": listing_count,
                "response_time_ms": all_listings_result["response_time_ms"]
            })
            
            print(f"  ✅ Admin can access all listings ({listing_count} listings)")
        else:
            filtering_tests.append({
                "test": "Admin Access to All Listings",
                "success": False,
                "error": all_listings_result.get("error"),
                "response_time_ms": all_listings_result["response_time_ms"]
            })
            print(f"  ❌ Admin cannot access all listings: {all_listings_result.get('error')}")
        
        # Test 3: Admin dashboard access (should work for admin)
        dashboard_result = await self.make_request("/admin/dashboard")
        
        if dashboard_result["success"]:
            dashboard_data = dashboard_result["data"]
            has_kpis = any(key in dashboard_data for key in ["total_users", "total_listings", "total_revenue"])
            
            filtering_tests.append({
                "test": "Admin Dashboard Access",
                "success": True,
                "has_kpis": has_kpis,
                "response_time_ms": dashboard_result["response_time_ms"]
            })
            
            print(f"  ✅ Admin can access dashboard (has KPIs: {has_kpis})")
        else:
            filtering_tests.append({
                "test": "Admin Dashboard Access",
                "success": False,
                "error": dashboard_result.get("error"),
                "response_time_ms": dashboard_result["response_time_ms"]
            })
            print(f"  ❌ Admin cannot access dashboard: {dashboard_result.get('error')}")
        
        # Calculate overall filtering health
        successful_tests = [t for t in filtering_tests if t["success"]]
        filtering_health_score = (len(successful_tests) / len(filtering_tests)) * 100 if filtering_tests else 0
        
        # Identify specific filtering issues
        filtering_issues = []
        for test in filtering_tests:
            if not test["success"]:
                filtering_issues.append(f"{test['test']}: {test.get('error', 'Unknown error')}")
        
        return {
            "test_name": "Admin Specific Data Filtering",
            "total_filtering_tests": len(filtering_tests),
            "successful_filtering_tests": len(successful_tests),
            "filtering_health_score": filtering_health_score,
            "admin_filtering_working_correctly": filtering_health_score == 100,
            "identified_filtering_issues": filtering_issues,
            "has_filtering_issues": len(filtering_issues) > 0,
            "detailed_filtering_tests": filtering_tests
        }
    
    async def run_comprehensive_admin_test(self) -> Dict:
        """Run all admin user specific tests"""
        print("🚀 Starting Cataloro Admin User Specific Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test suites in sequence
            admin_auth = await self.test_admin_user_authentication()
            
            # Only proceed with other tests if authentication succeeds
            if admin_auth.get("login_successful", False):
                admin_listings = await self.test_admin_listings_visibility()
                admin_database = await self.test_admin_user_database_state()
                admin_messages = await self.test_admin_messages_historical_data()
                cross_platform_messages = await self.test_cross_platform_message_visibility()
                data_filtering = await self.test_admin_specific_data_filtering()
                
                # Compile overall results
                all_results = {
                    "test_timestamp": datetime.now().isoformat(),
                    "admin_authentication": admin_auth,
                    "admin_listings_visibility": admin_listings,
                    "admin_database_state": admin_database,
                    "admin_messages_historical": admin_messages,
                    "cross_platform_message_visibility": cross_platform_messages,
                    "admin_data_filtering": data_filtering
                }
                
                # Calculate overall success metrics
                test_results = [
                    admin_auth.get("all_admin_properties_correct", False),
                    admin_listings.get("my_listings_endpoint_working", False),
                    admin_database.get("profile_accessible", False),
                    admin_messages.get("admin_messages_accessible", False),
                    cross_platform_messages.get("messaging_fully_functional", False),
                    data_filtering.get("admin_filtering_working_correctly", False)
                ]
                
                overall_success_rate = sum(test_results) / len(test_results) * 100
                
                # Identify critical issues
                critical_issues = []
                
                if not admin_auth.get("all_admin_properties_correct", False):
                    critical_issues.append("Admin authentication has issues")
                
                if not admin_listings.get("my_listings_endpoint_working", False):
                    critical_issues.append("Admin listings visibility problems")
                
                if admin_messages.get("has_data_access_issues", False):
                    critical_issues.append("Admin message data access issues")
                
                if cross_platform_messages.get("has_filtering_issues", False):
                    critical_issues.append("Admin message filtering issues")
                
                if data_filtering.get("has_filtering_issues", False):
                    critical_issues.append("Admin data filtering problems")
                
                all_results["summary"] = {
                    "overall_success_rate": overall_success_rate,
                    "admin_authentication_working": admin_auth.get("all_admin_properties_correct", False),
                    "admin_listings_accessible": admin_listings.get("my_listings_endpoint_working", False),
                    "admin_database_state_healthy": admin_database.get("has_all_essential_fields", False),
                    "admin_messages_working": admin_messages.get("admin_messages_accessible", False),
                    "cross_platform_messaging_working": cross_platform_messages.get("messaging_fully_functional", False),
                    "admin_data_filtering_working": data_filtering.get("admin_filtering_working_correctly", False),
                    "critical_issues_identified": critical_issues,
                    "has_critical_issues": len(critical_issues) > 0,
                    "all_admin_functionality_working": overall_success_rate == 100
                }
                
                return all_results
            else:
                # Authentication failed, return limited results
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "admin_authentication": admin_auth,
                    "summary": {
                        "overall_success_rate": 0,
                        "admin_authentication_working": False,
                        "critical_issues_identified": ["Admin authentication failed - cannot proceed with other tests"],
                        "has_critical_issues": True,
                        "all_admin_functionality_working": False
                    }
                }
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution function"""
    tester = AdminUserTester()
    results = await tester.run_comprehensive_admin_test()
    
    print("\n" + "=" * 70)
    print("🎯 ADMIN USER TESTING SUMMARY")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"Admin Authentication: {'✅' if summary.get('admin_authentication_working', False) else '❌'}")
    print(f"Admin Listings Access: {'✅' if summary.get('admin_listings_accessible', False) else '❌'}")
    print(f"Admin Database State: {'✅' if summary.get('admin_database_state_healthy', False) else '❌'}")
    print(f"Admin Messages: {'✅' if summary.get('admin_messages_working', False) else '❌'}")
    print(f"Cross-platform Messaging: {'✅' if summary.get('cross_platform_messaging_working', False) else '❌'}")
    print(f"Admin Data Filtering: {'✅' if summary.get('admin_data_filtering_working', False) else '❌'}")
    
    if summary.get("has_critical_issues", False):
        print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
        for issue in summary.get("critical_issues_identified", []):
            print(f"  ❌ {issue}")
    else:
        print("\n✅ No critical issues identified")
    
    print(f"\n🎉 All Admin Functionality Working: {'YES' if summary.get('all_admin_functionality_working', False) else 'NO'}")
    
    # Save detailed results to file
    with open("/app/admin_user_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/admin_user_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())