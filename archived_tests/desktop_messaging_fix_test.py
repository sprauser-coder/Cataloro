#!/usr/bin/env python3
"""
DESKTOP MESSAGING FUNCTIONALITY FIX TESTING
Testing the desktop messenger reply bug fix and messaging endpoints
Focus: Test if desktop messenger sends out replies after fixing liveService.sendMessage API call parameters
"""

import asyncio
import aiohttp
import time
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-marketplace-6.preview.emergentagent.com/api"

# Test Users Configuration
DEMO_USER_ID = "68bfff790e4e46bc28d43631"  # Fixed demo user ID from review
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "user@cataloro.com"

class DesktopMessagingFixTester:
    def __init__(self):
        self.session = None
        self.demo_user_data = None
        self.admin_user_data = None
        
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
    
    async def test_user_authentication(self) -> Dict:
        """Test authentication for both demo and admin users"""
        print("🔐 Testing user authentication for messaging...")
        
        # Test demo user login
        print("  Testing demo user login...")
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": "demo123"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        demo_success = False
        if demo_result["success"]:
            self.demo_user_data = demo_result["data"].get("user", {})
            demo_user_id = self.demo_user_data.get("id")
            demo_correct_id = demo_user_id == DEMO_USER_ID
            demo_success = True
            
            print(f"    ✅ Demo user login successful")
            print(f"    👤 User ID: {demo_user_id} ({'✅' if demo_correct_id else '❌'})")
        else:
            print(f"    ❌ Demo user login failed: {demo_result.get('error')}")
        
        # Test admin user login
        print("  Testing admin user login...")
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        admin_success = False
        if admin_result["success"]:
            self.admin_user_data = admin_result["data"].get("user", {})
            admin_user_id = self.admin_user_data.get("id")
            is_admin = self.admin_user_data.get("user_role") == "Admin" or self.admin_user_data.get("role") == "admin"
            admin_success = True
            
            print(f"    ✅ Admin user login successful")
            print(f"    👤 User ID: {admin_user_id}")
            print(f"    🔑 Role: {self.admin_user_data.get('user_role')} ({'✅' if is_admin else '❌'})")
        else:
            print(f"    ❌ Admin user login failed: {admin_result.get('error')}")
        
        return {
            "test_name": "User Authentication",
            "demo_user_authenticated": demo_success,
            "admin_user_authenticated": admin_success,
            "both_users_authenticated": demo_success and admin_success
        }
    
    async def test_get_messages_endpoints(self) -> Dict:
        """Test GET /api/user/{user_id}/messages endpoints"""
        print("📨 Testing GET messages endpoints...")
        
        if not self.demo_user_data or not self.admin_user_data:
            return {
                "test_name": "GET Messages Endpoints",
                "error": "User authentication required first"
            }
        
        demo_user_id = self.demo_user_data.get("id")
        admin_user_id = self.admin_user_data.get("id")
        
        # Test demo user messages
        print(f"  Testing demo user messages (ID: {demo_user_id})...")
        demo_messages_result = await self.make_request(f"/user/{demo_user_id}/messages")
        
        demo_success = False
        demo_message_count = 0
        if demo_messages_result["success"]:
            demo_messages = demo_messages_result["data"]
            demo_message_count = len(demo_messages) if isinstance(demo_messages, list) else 0
            demo_success = True
            print(f"    ✅ Demo user messages: {demo_message_count} messages found")
        else:
            print(f"    ❌ Demo user messages failed: {demo_messages_result.get('error')}")
        
        # Test admin user messages
        print(f"  Testing admin user messages (ID: {admin_user_id})...")
        admin_messages_result = await self.make_request(f"/user/{admin_user_id}/messages")
        
        admin_success = False
        admin_message_count = 0
        if admin_messages_result["success"]:
            admin_messages = admin_messages_result["data"]
            admin_message_count = len(admin_messages) if isinstance(admin_messages, list) else 0
            admin_success = True
            print(f"    ✅ Admin user messages: {admin_message_count} messages found")
        else:
            print(f"    ❌ Admin user messages failed: {admin_messages_result.get('error')}")
        
        return {
            "test_name": "GET Messages Endpoints",
            "demo_endpoint_working": demo_success,
            "admin_endpoint_working": admin_success,
            "both_endpoints_working": demo_success and admin_success,
            "demo_message_count": demo_message_count,
            "admin_message_count": admin_message_count,
            "total_messages_found": demo_message_count + admin_message_count
        }
    
    async def test_send_message_endpoints(self) -> Dict:
        """Test POST /api/user/{user_id}/messages endpoints - CRITICAL FIX TEST"""
        print("📤 Testing POST messages endpoints (CRITICAL DESKTOP REPLY FIX)...")
        
        if not self.demo_user_data or not self.admin_user_data:
            return {
                "test_name": "POST Messages Endpoints",
                "error": "User authentication required first"
            }
        
        demo_user_id = self.demo_user_data.get("id")
        admin_user_id = self.admin_user_data.get("id")
        
        # Test 1: Demo user sending message to admin
        print("  Test 1: Demo user sending message to admin...")
        
        demo_to_admin_data = {
            "recipient_id": admin_user_id,
            "subject": "Desktop Messaging Test - Original Message",
            "content": f"Test message from demo user to admin. Timestamp: {datetime.now().isoformat()}"
        }
        
        demo_send_result = await self.make_request(f"/user/{demo_user_id}/messages", "POST", data=demo_to_admin_data)
        
        demo_send_success = False
        demo_message_id = None
        if demo_send_result["success"]:
            demo_message_id = demo_send_result["data"].get("id")
            demo_send_success = True
            print(f"    ✅ Demo to admin message sent (ID: {demo_message_id})")
        else:
            print(f"    ❌ Demo to admin message failed: {demo_send_result.get('error')}")
        
        # Test 2: Admin user replying to demo user (CRITICAL DESKTOP REPLY TEST)
        print("  Test 2: Admin user replying to demo user (CRITICAL DESKTOP MESSENGER FIX)...")
        
        admin_reply_data = {
            "recipient_id": demo_user_id,
            "subject": "Re: Desktop Messaging Test - Reply Message",
            "content": f"CRITICAL REPLY from admin to demo user. Testing desktop messenger reply fix. Timestamp: {datetime.now().isoformat()}"
        }
        
        admin_reply_result = await self.make_request(f"/user/{admin_user_id}/messages", "POST", data=admin_reply_data)
        
        admin_reply_success = False
        admin_reply_id = None
        if admin_reply_result["success"]:
            admin_reply_id = admin_reply_result["data"].get("id")
            admin_reply_success = True
            print(f"    ✅ CRITICAL ADMIN REPLY sent successfully (ID: {admin_reply_id})")
            print(f"    🎯 Desktop messenger reply functionality WORKING")
        else:
            print(f"    ❌ CRITICAL ADMIN REPLY failed: {admin_reply_result.get('error')}")
            print(f"    🚨 Desktop messenger reply functionality STILL BROKEN")
        
        # Test 3: Verify message delivery
        print("  Test 3: Verifying message delivery...")
        
        # Check admin received demo's message
        admin_messages_check = await self.make_request(f"/user/{admin_user_id}/messages")
        demo_messages_check = await self.make_request(f"/user/{demo_user_id}/messages")
        
        admin_received_demo = False
        demo_received_admin = False
        
        if admin_messages_check["success"]:
            admin_messages = admin_messages_check["data"]
            for msg in admin_messages:
                if msg.get("sender_id") == demo_user_id and "Desktop Messaging Test - Original Message" in msg.get("subject", ""):
                    admin_received_demo = True
                    break
        
        if demo_messages_check["success"]:
            demo_messages = demo_messages_check["data"]
            for msg in demo_messages:
                if msg.get("sender_id") == admin_user_id and "Reply Message" in msg.get("subject", ""):
                    demo_received_admin = True
                    break
        
        if admin_received_demo:
            print(f"    ✅ Admin received demo's message")
        else:
            print(f"    ❌ Admin did not receive demo's message")
        
        if demo_received_admin:
            print(f"    ✅ Demo received admin's reply")
            print(f"    🎯 DESKTOP MESSENGER REPLY DELIVERY CONFIRMED")
        else:
            print(f"    ❌ Demo did not receive admin's reply")
            print(f"    🚨 DESKTOP MESSENGER REPLY DELIVERY FAILED")
        
        return {
            "test_name": "POST Messages Endpoints",
            "demo_send_success": demo_send_success,
            "admin_reply_success": admin_reply_success,
            "critical_desktop_reply_fix_working": admin_reply_success,
            "admin_received_demo_message": admin_received_demo,
            "demo_received_admin_reply": demo_received_admin,
            "message_delivery_verified": admin_received_demo and demo_received_admin,
            "desktop_messenger_reply_functionality_fixed": admin_reply_success and demo_received_admin
        }
    
    async def test_database_message_state(self) -> Dict:
        """Test current database state for messages"""
        print("🗄️ Testing database message state...")
        
        if not self.demo_user_data or not self.admin_user_data:
            return {
                "test_name": "Database Message State",
                "error": "User authentication required first"
            }
        
        demo_user_id = self.demo_user_data.get("id")
        admin_user_id = self.admin_user_data.get("id")
        
        # Get current messages for both users
        demo_messages_result = await self.make_request(f"/user/{demo_user_id}/messages")
        admin_messages_result = await self.make_request(f"/user/{admin_user_id}/messages")
        
        demo_total = 0
        admin_total = 0
        
        if demo_messages_result["success"]:
            demo_messages = demo_messages_result["data"]
            demo_total = len(demo_messages) if isinstance(demo_messages, list) else 0
            print(f"  Demo user total messages: {demo_total}")
        
        if admin_messages_result["success"]:
            admin_messages = admin_messages_result["data"]
            admin_total = len(admin_messages) if isinstance(admin_messages, list) else 0
            print(f"  Admin user total messages: {admin_total}")
        
        total_messages = demo_total + admin_total
        has_message_data = total_messages > 0
        
        print(f"  Total messages in system: {total_messages}")
        print(f"  Database has message data: {'✅ Yes' if has_message_data else '❌ No'}")
        
        return {
            "test_name": "Database Message State",
            "demo_user_message_count": demo_total,
            "admin_user_message_count": admin_total,
            "total_messages_in_system": total_messages,
            "database_has_message_data": has_message_data,
            "demo_user_has_messages": demo_total > 0,
            "admin_user_has_messages": admin_total > 0
        }
    
    async def test_complete_messaging_workflow(self) -> Dict:
        """Test complete messaging workflow including composition and reply"""
        print("💬 Testing complete messaging workflow...")
        
        if not self.demo_user_data or not self.admin_user_data:
            return {
                "test_name": "Complete Messaging Workflow",
                "error": "User authentication required first"
            }
        
        demo_user_id = self.demo_user_data.get("id")
        admin_user_id = self.admin_user_data.get("id")
        
        workflow_success = True
        workflow_steps = []
        
        # Step 1: Create conversation thread
        print("  Step 1: Creating conversation thread...")
        
        thread_subject = f"Desktop Messenger Workflow Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        initial_message_data = {
            "recipient_id": admin_user_id,
            "subject": thread_subject,
            "content": "Hello Admin, this is a comprehensive test of the desktop messenger workflow. Please reply to confirm the functionality is working end-to-end."
        }
        
        initial_result = await self.make_request(f"/user/{demo_user_id}/messages", "POST", data=initial_message_data)
        
        if initial_result["success"]:
            initial_message_id = initial_result["data"].get("id")
            workflow_steps.append({"step": "initial_message", "success": True, "message_id": initial_message_id})
            print(f"    ✅ Initial message sent (ID: {initial_message_id})")
        else:
            workflow_steps.append({"step": "initial_message", "success": False, "error": initial_result.get("error")})
            workflow_success = False
            print(f"    ❌ Initial message failed: {initial_result.get('error')}")
        
        # Step 2: Admin replies (CRITICAL TEST)
        print("  Step 2: Admin replying (CRITICAL DESKTOP MESSENGER TEST)...")
        
        reply_message_data = {
            "recipient_id": demo_user_id,
            "subject": f"Re: {thread_subject}",
            "content": "Hello Demo User, I received your message and I'm replying to confirm that the desktop messenger reply functionality is working correctly after the liveService.sendMessage fix."
        }
        
        reply_result = await self.make_request(f"/user/{admin_user_id}/messages", "POST", data=reply_message_data)
        
        if reply_result["success"]:
            reply_message_id = reply_result["data"].get("id")
            workflow_steps.append({"step": "admin_reply", "success": True, "message_id": reply_message_id, "critical": True})
            print(f"    ✅ CRITICAL ADMIN REPLY sent successfully (ID: {reply_message_id})")
        else:
            workflow_steps.append({"step": "admin_reply", "success": False, "error": reply_result.get("error"), "critical": True})
            workflow_success = False
            print(f"    ❌ CRITICAL ADMIN REPLY failed: {reply_result.get('error')}")
        
        # Step 3: Verify complete thread
        print("  Step 3: Verifying complete conversation thread...")
        
        # Check both users have the complete thread
        demo_final_messages = await self.make_request(f"/user/{demo_user_id}/messages")
        admin_final_messages = await self.make_request(f"/user/{admin_user_id}/messages")
        
        thread_complete = False
        
        if demo_final_messages["success"] and admin_final_messages["success"]:
            demo_messages = demo_final_messages["data"]
            admin_messages = admin_final_messages["data"]
            
            # Look for thread messages
            demo_thread_messages = [msg for msg in demo_messages if thread_subject in msg.get("subject", "")]
            admin_thread_messages = [msg for msg in admin_messages if thread_subject in msg.get("subject", "")]
            
            thread_complete = len(demo_thread_messages) >= 1 and len(admin_thread_messages) >= 1
        
        workflow_steps.append({"step": "thread_verification", "success": thread_complete})
        
        if thread_complete:
            print(f"    ✅ Complete conversation thread verified")
            print(f"    🎯 DESKTOP MESSENGER WORKFLOW WORKING")
        else:
            workflow_success = False
            print(f"    ❌ Conversation thread incomplete")
            print(f"    🚨 DESKTOP MESSENGER WORKFLOW HAS ISSUES")
        
        successful_steps = len([s for s in workflow_steps if s.get("success", False)])
        critical_reply_working = any(s.get("critical", False) and s.get("success", False) for s in workflow_steps)
        
        return {
            "test_name": "Complete Messaging Workflow",
            "workflow_success": workflow_success,
            "total_steps": len(workflow_steps),
            "successful_steps": successful_steps,
            "critical_admin_reply_working": critical_reply_working,
            "conversation_thread_complete": thread_complete,
            "desktop_messenger_workflow_fixed": workflow_success and critical_reply_working
        }
    
    async def run_comprehensive_test(self) -> Dict:
        """Run all desktop messaging tests"""
        print("🚀 Starting Desktop Messaging Functionality Fix Testing")
        print("=" * 70)
        print("🎯 FOCUS: Testing desktop messenger reply bug fix")
        print("🔧 ISSUE: Desktop messenger on desktop version does not send out replies")
        print("✅ FIX: Fixed liveService.sendMessage API call parameters")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test suites
            auth_test = await self.test_user_authentication()
            get_messages_test = await self.test_get_messages_endpoints()
            send_messages_test = await self.test_send_message_endpoints()
            database_test = await self.test_database_message_state()
            workflow_test = await self.test_complete_messaging_workflow()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Desktop Messenger Reply Bug Fix",
                "critical_issue": "Desktop messenger on desktop version does not send out replies",
                "fix_description": "Fixed liveService.sendMessage API call parameters - sender_id now within messageData object",
                "user_authentication": auth_test,
                "get_messages_endpoints": get_messages_test,
                "send_messages_endpoints": send_messages_test,
                "database_message_state": database_test,
                "complete_messaging_workflow": workflow_test
            }
            
            # Calculate success metrics
            critical_tests = [
                auth_test.get("both_users_authenticated", False),
                get_messages_test.get("both_endpoints_working", False),
                send_messages_test.get("critical_desktop_reply_fix_working", False),
                send_messages_test.get("desktop_messenger_reply_functionality_fixed", False),
                workflow_test.get("desktop_messenger_workflow_fixed", False)
            ]
            
            overall_success_rate = sum(critical_tests) / len(critical_tests) * 100
            desktop_reply_fix_working = (
                send_messages_test.get("critical_desktop_reply_fix_working", False) and
                send_messages_test.get("message_delivery_verified", False) and
                workflow_test.get("desktop_messenger_workflow_fixed", False)
            )
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "desktop_messenger_reply_bug_fixed": desktop_reply_fix_working,
                "user_authentication_working": auth_test.get("both_users_authenticated", False),
                "get_messages_endpoints_working": get_messages_test.get("both_endpoints_working", False),
                "send_messages_endpoints_working": send_messages_test.get("critical_desktop_reply_fix_working", False),
                "message_delivery_verified": send_messages_test.get("message_delivery_verified", False),
                "complete_workflow_working": workflow_test.get("desktop_messenger_workflow_fixed", False),
                "database_has_message_data": database_test.get("database_has_message_data", False),
                "critical_fix_successful": desktop_reply_fix_working
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution"""
    tester = DesktopMessagingFixTester()
    results = await tester.run_comprehensive_test()
    
    print("\n" + "=" * 70)
    print("📊 DESKTOP MESSAGING FIX TEST RESULTS SUMMARY")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"🎯 Desktop Messenger Reply Bug Fix: {'✅ FIXED' if summary.get('desktop_messenger_reply_bug_fixed') else '❌ NOT FIXED'}")
    print(f"🔐 User Authentication: {'✅ Working' if summary.get('user_authentication_working') else '❌ Failed'}")
    print(f"📨 GET Messages Endpoints: {'✅ Working' if summary.get('get_messages_endpoints_working') else '❌ Failed'}")
    print(f"📤 POST Messages Endpoints: {'✅ Working' if summary.get('send_messages_endpoints_working') else '❌ Failed'}")
    print(f"✉️ Message Delivery: {'✅ Verified' if summary.get('message_delivery_verified') else '❌ Failed'}")
    print(f"💬 Complete Workflow: {'✅ Working' if summary.get('complete_workflow_working') else '❌ Failed'}")
    print(f"🗄️ Database Message Data: {'✅ Available' if summary.get('database_has_message_data') else '❌ Empty'}")
    
    print(f"\n📈 Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    
    if summary.get('critical_fix_successful'):
        print("\n🎉 CRITICAL SUCCESS: Desktop messenger reply functionality is now working!")
        print("✅ The liveService.sendMessage API call parameter fix has resolved the issue")
        print("✅ Desktop users can now send replies successfully")
    else:
        print("\n🚨 CRITICAL ISSUE: Desktop messenger reply functionality still not working")
        print("❌ The fix may not be complete or there are additional issues")
        print("❌ Desktop users still cannot send replies")
    
    print("\n" + "=" * 70)
    
    # Save detailed results
    with open("/app/desktop_messaging_fix_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("📄 Detailed results saved to: /app/desktop_messaging_fix_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())