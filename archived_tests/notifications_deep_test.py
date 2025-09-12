#!/usr/bin/env python3
"""
DEEP NOTIFICATIONS INVESTIGATION
The initial test shows notifications API working but users getting empty arrays despite 68 notifications in database.
This suggests a data association issue - notifications exist but aren't linked to the test users.
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://dynamic-marketplace.preview.emergentagent.com/api"

# Test User Configurations
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "demo@cataloro.com"
DEMO_USER_ID = "68bfff790e4e46bc28d43631"

class NotificationsDeepInvestigator:
    """
    DEEP INVESTIGATION: Why users get empty notifications despite 68 notifications in database
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.admin_user_id = None
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
        """Authenticate both admin and demo users"""
        print("🔐 Authenticating users for deep investigation...")
        
        # Authenticate admin
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            self.admin_user_id = admin_result["data"].get("user", {}).get("id", "")
            print(f"  ✅ Admin authentication successful (ID: {self.admin_user_id})")
        else:
            print(f"  ❌ Admin authentication failed: {admin_result.get('error', 'Unknown error')}")
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
    
    async def create_test_notification(self) -> Dict:
        """
        Create a test notification for the demo user to verify the system works
        """
        print("📝 Creating test notification for demo user...")
        
        if not self.admin_token or not self.demo_user_id:
            return {"error": "No admin token or demo user ID available"}
        
        # Try to create a notification via admin endpoint (if available)
        test_notification_data = {
            "user_id": self.demo_user_id,
            "title": "Test Notification",
            "message": "This is a test notification to verify the notifications system is working",
            "type": "test",
            "read": False
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Try different endpoints that might create notifications
        endpoints_to_try = [
            "/admin/notifications",
            "/notifications",
            f"/user/{self.demo_user_id}/notifications"
        ]
        
        for endpoint in endpoints_to_try:
            print(f"  🔍 Trying to create notification via {endpoint}...")
            result = await self.make_request(endpoint, "POST", data=test_notification_data, headers=headers)
            
            if result["success"]:
                print(f"    ✅ Test notification created successfully via {endpoint}")
                return {"success": True, "endpoint": endpoint, "result": result}
            else:
                print(f"    ❌ Failed to create via {endpoint}: Status {result['status']}")
        
        print(f"  ⚠️ Could not create test notification via any endpoint")
        return {"success": False, "error": "No working notification creation endpoint found"}
    
    async def investigate_user_id_formats(self) -> Dict:
        """
        Investigate if there are user ID format mismatches causing the issue
        """
        print("🔍 Investigating user ID formats and database associations...")
        
        investigation_results = {
            "demo_user_id_used": self.demo_user_id,
            "admin_user_id_used": self.admin_user_id,
            "alternative_user_ids_tested": [],
            "notifications_found_for_ids": {},
            "success": False
        }
        
        # Test different possible user ID formats for demo user
        possible_demo_ids = [
            self.demo_user_id,  # Current ID from login
            DEMO_USER_ID,       # Fixed ID from config
            "demo_user",        # Username-based
            "user@cataloro.com", # Email-based
            "demo@cataloro.com"  # Current email
        ]
        
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        for test_id in possible_demo_ids:
            if test_id and test_id not in investigation_results["alternative_user_ids_tested"]:
                investigation_results["alternative_user_ids_tested"].append(test_id)
                print(f"  🔍 Testing notifications for user ID: {test_id}")
                
                result = await self.make_request(f"/user/{test_id}/notifications", headers=headers)
                
                if result["success"]:
                    notifications = result.get("data", [])
                    count = len(notifications) if isinstance(notifications, list) else 0
                    investigation_results["notifications_found_for_ids"][test_id] = count
                    
                    if count > 0:
                        print(f"    ✅ Found {count} notifications for user ID: {test_id}")
                        investigation_results["success"] = True
                        
                        # Show sample notification
                        if notifications and isinstance(notifications, list):
                            sample = notifications[0]
                            print(f"    📋 Sample notification: '{sample.get('title', 'No title')}' - {sample.get('type', 'No type')}")
                    else:
                        print(f"    ℹ️ No notifications found for user ID: {test_id}")
                else:
                    print(f"    ❌ Failed to get notifications for user ID {test_id}: Status {result['status']}")
                    investigation_results["notifications_found_for_ids"][test_id] = f"Error: {result['status']}"
        
        return investigation_results
    
    async def check_notification_user_associations(self) -> Dict:
        """
        Check what user IDs are actually associated with the 68 notifications in the database
        """
        print("🗄️ Checking notification-user associations in database...")
        
        if not self.admin_token:
            return {"error": "No admin token available"}
        
        # Get all users to see what user IDs exist
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        users_result = await self.make_request("/admin/users", headers=headers)
        
        association_results = {
            "total_users_in_system": 0,
            "user_ids_in_system": [],
            "notifications_per_user": {},
            "orphaned_notifications": 0,
            "success": False
        }
        
        if users_result["success"]:
            users = users_result.get("data", [])
            if isinstance(users, list):
                association_results["total_users_in_system"] = len(users)
                
                print(f"  📊 Found {len(users)} users in system")
                
                # Test notifications for each user
                for user in users[:10]:  # Limit to first 10 users to avoid too many requests
                    if isinstance(user, dict):
                        user_id = user.get("id")
                        username = user.get("username", "Unknown")
                        email = user.get("email", "Unknown")
                        
                        if user_id:
                            association_results["user_ids_in_system"].append(user_id)
                            print(f"  🔍 Checking notifications for user: {username} ({email}) - ID: {user_id}")
                            
                            # Try to get notifications for this user
                            notif_result = await self.make_request(f"/user/{user_id}/notifications", headers=headers)
                            
                            if notif_result["success"]:
                                notifications = notif_result.get("data", [])
                                count = len(notifications) if isinstance(notifications, list) else 0
                                association_results["notifications_per_user"][user_id] = {
                                    "count": count,
                                    "username": username,
                                    "email": email
                                }
                                
                                if count > 0:
                                    print(f"    ✅ User {username} has {count} notifications")
                                    association_results["success"] = True
                                else:
                                    print(f"    ℹ️ User {username} has no notifications")
                            else:
                                print(f"    ❌ Failed to get notifications for user {username}: Status {notif_result['status']}")
                                association_results["notifications_per_user"][user_id] = {
                                    "count": f"Error: {notif_result['status']}",
                                    "username": username,
                                    "email": email
                                }
        else:
            print(f"  ❌ Failed to get users list: Status {users_result['status']}")
        
        return association_results
    
    async def test_notification_creation_and_retrieval(self) -> Dict:
        """
        Test creating a notification and immediately retrieving it to verify the full flow
        """
        print("🔄 Testing notification creation and retrieval flow...")
        
        if not self.admin_token or not self.demo_user_id:
            return {"error": "No admin token or demo user ID available"}
        
        flow_results = {
            "notification_created": False,
            "notification_retrieved": False,
            "creation_method": None,
            "retrieval_count": 0,
            "full_flow_working": False,
            "success": False
        }
        
        # Try to create a notification using direct database insertion simulation
        # Since we might not have a direct API, let's test if we can trigger system notifications
        
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        # Try to trigger a system notification by updating profile (this should trigger notifications)
        print("  🔄 Attempting to trigger system notification via profile update...")
        profile_update_data = {
            "profile": {
                "bio": f"Updated bio at {datetime.now().isoformat()}"
            }
        }
        
        profile_result = await self.make_request(f"/auth/profile/{self.demo_user_id}", "PUT", 
                                               data=profile_update_data, headers=headers)
        
        if profile_result["success"]:
            print("    ✅ Profile update successful - should trigger system notification")
            flow_results["notification_created"] = True
            flow_results["creation_method"] = "profile_update_trigger"
            
            # Wait a moment for notification to be created
            await asyncio.sleep(2)
            
            # Now check if notification appears
            notif_result = await self.make_request(f"/user/{self.demo_user_id}/notifications", headers=headers)
            
            if notif_result["success"]:
                notifications = notif_result.get("data", [])
                count = len(notifications) if isinstance(notifications, list) else 0
                flow_results["retrieval_count"] = count
                
                if count > 0:
                    print(f"    ✅ Retrieved {count} notifications after profile update")
                    flow_results["notification_retrieved"] = True
                    flow_results["full_flow_working"] = True
                    flow_results["success"] = True
                    
                    # Show the notification
                    sample = notifications[0]
                    print(f"    📋 Latest notification: '{sample.get('title', 'No title')}' - {sample.get('type', 'No type')}")
                else:
                    print(f"    ⚠️ No notifications retrieved after profile update")
            else:
                print(f"    ❌ Failed to retrieve notifications after profile update: Status {notif_result['status']}")
        else:
            print(f"    ❌ Profile update failed: Status {profile_result['status']}")
        
        return flow_results
    
    async def run_deep_investigation(self) -> Dict:
        """
        Run complete deep investigation
        """
        print("🚨 STARTING DEEP NOTIFICATIONS INVESTIGATION")
        print("=" * 80)
        print("ISSUE: 68 notifications in database but users get empty arrays")
        print("INVESTIGATING: User ID associations, data flow, and notification creation")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_users()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "User authentication failed - cannot proceed with investigation"
                }
            
            # Run deep investigation tests
            user_id_investigation = await self.investigate_user_id_formats()
            association_check = await self.check_notification_user_associations()
            flow_test = await self.test_notification_creation_and_retrieval()
            
            # Compile comprehensive results
            investigation_results = {
                "test_timestamp": datetime.now().isoformat(),
                "investigation_focus": "Why 68 notifications exist in database but users get empty arrays",
                "user_id_format_investigation": user_id_investigation,
                "notification_user_associations": association_check,
                "notification_flow_test": flow_test
            }
            
            # Determine findings
            findings = []
            
            if user_id_investigation.get("success", False):
                findings.append("✅ Found notifications for at least one user ID format")
            else:
                findings.append("❌ No notifications found for any tested user ID formats")
            
            if association_check.get("success", False):
                findings.append("✅ Found users with notifications in the system")
            else:
                findings.append("❌ No users found with notifications despite 68 notifications in database")
            
            if flow_test.get("full_flow_working", False):
                findings.append("✅ Notification creation and retrieval flow working")
            else:
                findings.append("❌ Notification creation and retrieval flow not working")
            
            investigation_results["findings"] = findings
            investigation_results["issue_identified"] = len([f for f in findings if f.startswith("❌")]) > 0
            
            return investigation_results
            
        finally:
            await self.cleanup()


async def main():
    """Run deep notifications investigation"""
    investigator = NotificationsDeepInvestigator()
    results = await investigator.run_deep_investigation()
    
    print("\n" + "=" * 80)
    print("🔍 DEEP NOTIFICATIONS INVESTIGATION RESULTS")
    print("=" * 80)
    
    findings = results.get("findings", [])
    
    print(f"🔍 Investigation Findings:")
    for finding in findings:
        print(f"   {finding}")
    
    if results.get("issue_identified", False):
        print(f"\n❌ ISSUE IDENTIFIED: Notifications exist in database but aren't properly associated with users")
        
        # Show user ID investigation results
        user_id_inv = results.get("user_id_format_investigation", {})
        if user_id_inv.get("notifications_found_for_ids"):
            print(f"\n📊 Notifications found for user IDs:")
            for user_id, count in user_id_inv["notifications_found_for_ids"].items():
                print(f"   {user_id}: {count}")
        
        # Show association results
        assoc_check = results.get("notification_user_associations", {})
        if assoc_check.get("notifications_per_user"):
            print(f"\n👥 Users with notifications:")
            for user_id, info in assoc_check["notifications_per_user"].items():
                if isinstance(info, dict) and info.get("count", 0) > 0:
                    print(f"   {info.get('username', 'Unknown')} ({info.get('email', 'Unknown')}): {info['count']} notifications")
    else:
        print(f"\n✅ NO MAJOR ISSUES: Investigation shows notifications system is working correctly")
    
    print(f"\n📅 Investigation completed at: {results.get('test_timestamp', 'Unknown')}")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())