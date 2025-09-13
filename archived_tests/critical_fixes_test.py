#!/usr/bin/env python3
"""
CRITICAL FIXES TESTING - URGENT REVIEW REQUEST
Testing the two critical issues that were just fixed:

1. Catalyst Database Access for All Users:
   - Changed `/api/admin/catalyst/unified-calculations` from `require_admin_role` to `require_auth`
   - Should now allow all authenticated users to access catalyst data

2. Mobile Messages Authentication:
   - Added authentication headers and `/api` prefix to liveService methods
   - getUserMessages(), sendMessage(), markMessageRead()
   - Also fixed getUserFavorites(), addToFavorites(), removeFromFavorites()
"""

import asyncio
import aiohttp
import time
import json
import base64
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-marketplace-6.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

# Demo User Configuration (Non-admin)
DEMO_EMAIL = "demo@cataloro.com"
DEMO_PASSWORD = "demo_password"
DEMO_USER_ID = "68bfff790e4e46bc28d43631"

class CriticalFixesTester:
    """
    Test the two critical fixes mentioned in the review request
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
        print("🔐 Authenticating users for critical fixes testing...")
        
        # Authenticate admin
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            self.admin_user_id = admin_result["data"].get("user", {}).get("id", "")
            print(f"  ✅ Admin authentication successful (ID: {self.admin_user_id})")
        else:
            print(f"  ❌ Admin authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
        
        # Authenticate demo user (non-admin)
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
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
    
    async def test_catalyst_access_for_all_users(self) -> Dict:
        """
        CRITICAL FIX 1: Test catalyst database access for all users
        The endpoint `/api/admin/catalyst/unified-calculations` was changed from 
        `require_admin_role` to `require_auth` to allow all authenticated users
        """
        print("🧪 TESTING CRITICAL FIX 1: Catalyst Database Access for All Users")
        print("=" * 70)
        
        test_results = {
            "fix_description": "Changed /api/admin/catalyst/unified-calculations from require_admin_role to require_auth",
            "admin_access": {"success": False, "status": 0, "entries_count": 0, "response_time_ms": 0},
            "demo_access": {"success": False, "status": 0, "entries_count": 0, "response_time_ms": 0},
            "unauthenticated_access": {"success": False, "status": 0, "response_time_ms": 0},
            "fix_working": False,
            "critical_issues": [],
            "success_messages": []
        }
        
        # Test 1: Admin access (should work)
        print("  🔐 Testing admin access to catalyst endpoint...")
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            result = await self.make_request("/admin/catalyst/unified-calculations", headers=headers)
            
            test_results["admin_access"]["success"] = result["success"]
            test_results["admin_access"]["status"] = result["status"]
            test_results["admin_access"]["response_time_ms"] = result["response_time_ms"]
            
            if result["success"]:
                catalyst_data = result.get("data", [])
                entries_count = len(catalyst_data) if isinstance(catalyst_data, list) else 0
                test_results["admin_access"]["entries_count"] = entries_count
                print(f"    ✅ Admin access successful: {entries_count} catalyst entries ({result['response_time_ms']:.1f}ms)")
                test_results["success_messages"].append(f"Admin access working: {entries_count} catalyst entries")
            else:
                print(f"    ❌ Admin access failed: Status {result['status']}")
                test_results["critical_issues"].append(f"Admin access failed: Status {result['status']}")
        
        # Test 2: Demo user (non-admin) access (CRITICAL - should work after fix)
        print("  👤 Testing non-admin user access to catalyst endpoint...")
        if self.demo_token:
            headers = {"Authorization": f"Bearer {self.demo_token}"}
            result = await self.make_request("/admin/catalyst/unified-calculations", headers=headers)
            
            test_results["demo_access"]["success"] = result["success"]
            test_results["demo_access"]["status"] = result["status"]
            test_results["demo_access"]["response_time_ms"] = result["response_time_ms"]
            
            if result["success"]:
                catalyst_data = result.get("data", [])
                entries_count = len(catalyst_data) if isinstance(catalyst_data, list) else 0
                test_results["demo_access"]["entries_count"] = entries_count
                print(f"    ✅ Non-admin access successful: {entries_count} catalyst entries ({result['response_time_ms']:.1f}ms)")
                test_results["success_messages"].append(f"Non-admin access working: {entries_count} catalyst entries")
                test_results["fix_working"] = True
            else:
                print(f"    ❌ Non-admin access failed: Status {result['status']}")
                if result["status"] == 403:
                    test_results["critical_issues"].append("CRITICAL: Non-admin users still getting 403 - fix not working")
                else:
                    test_results["critical_issues"].append(f"Non-admin access failed: Status {result['status']}")
        
        # Test 3: Unauthenticated access (should still fail)
        print("  🚫 Testing unauthenticated access (should fail)...")
        result = await self.make_request("/admin/catalyst/unified-calculations")
        
        test_results["unauthenticated_access"]["success"] = result["success"]
        test_results["unauthenticated_access"]["status"] = result["status"]
        test_results["unauthenticated_access"]["response_time_ms"] = result["response_time_ms"]
        
        if result["status"] in [401, 403]:
            print(f"    ✅ Unauthenticated access properly rejected: Status {result['status']}")
            test_results["success_messages"].append("Unauthenticated access properly rejected")
        else:
            print(f"    ⚠️ Unauthenticated access not properly rejected: Status {result['status']}")
            test_results["critical_issues"].append("Authentication not properly enforced")
        
        return {
            "test_name": "Catalyst Database Access for All Users",
            "success": test_results["fix_working"] and test_results["admin_access"]["success"],
            "test_results": test_results,
            "critical_issue": not test_results["fix_working"],
            "fix_verified": test_results["fix_working"]
        }
    
    async def test_mobile_messages_authentication(self) -> Dict:
        """
        CRITICAL FIX 2: Test mobile messages authentication
        Added authentication headers and `/api` prefix to liveService methods:
        - getUserMessages(), sendMessage(), markMessageRead()
        - Also fixed getUserFavorites(), addToFavorites(), removeFromFavorites()
        """
        print("📱 TESTING CRITICAL FIX 2: Mobile Messages Authentication")
        print("=" * 70)
        
        test_results = {
            "fix_description": "Added authentication headers and /api prefix to liveService methods",
            "get_messages": {"success": False, "status": 0, "messages_count": 0, "response_time_ms": 0},
            "send_message": {"success": False, "status": 0, "response_time_ms": 0},
            "get_favorites": {"success": False, "status": 0, "favorites_count": 0, "response_time_ms": 0},
            "unauthenticated_messages": {"success": False, "status": 0, "response_time_ms": 0},
            "fix_working": False,
            "critical_issues": [],
            "success_messages": []
        }
        
        if not self.demo_token or not self.demo_user_id:
            test_results["critical_issues"].append("No demo user token or ID available")
            return {
                "test_name": "Mobile Messages Authentication",
                "success": False,
                "test_results": test_results,
                "critical_issue": True,
                "fix_verified": False
            }
        
        # Test 1: Get user messages with authentication
        print("  📨 Testing getUserMessages() with authentication...")
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        result = await self.make_request(f"/user/{self.demo_user_id}/messages", headers=headers)
        
        test_results["get_messages"]["success"] = result["success"]
        test_results["get_messages"]["status"] = result["status"]
        test_results["get_messages"]["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            messages = result.get("data", [])
            messages_count = len(messages) if isinstance(messages, list) else 0
            test_results["get_messages"]["messages_count"] = messages_count
            print(f"    ✅ Get messages successful: {messages_count} messages ({result['response_time_ms']:.1f}ms)")
            test_results["success_messages"].append(f"Get messages working: {messages_count} messages")
        else:
            print(f"    ❌ Get messages failed: Status {result['status']}")
            if result["status"] == 404:
                test_results["critical_issues"].append("CRITICAL: Messages endpoint still returning 404 - fix not working")
            else:
                test_results["critical_issues"].append(f"Get messages failed: Status {result['status']}")
        
        # Test 2: Send message with authentication
        print("  📤 Testing sendMessage() with authentication...")
        message_data = {
            "recipient_id": self.admin_user_id,
            "subject": "Test Message from Critical Fixes Test",
            "message": "This is a test message to verify the mobile messages authentication fix is working.",
            "message_type": "general"
        }
        
        result = await self.make_request(f"/user/{self.demo_user_id}/messages", "POST", data=message_data, headers=headers)
        
        test_results["send_message"]["success"] = result["success"]
        test_results["send_message"]["status"] = result["status"]
        test_results["send_message"]["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            print(f"    ✅ Send message successful ({result['response_time_ms']:.1f}ms)")
            test_results["success_messages"].append("Send message working")
        else:
            print(f"    ❌ Send message failed: Status {result['status']}")
            if result["status"] == 404:
                test_results["critical_issues"].append("CRITICAL: Send message endpoint still returning 404 - fix not working")
            else:
                test_results["critical_issues"].append(f"Send message failed: Status {result['status']}")
        
        # Test 3: Get user favorites with authentication
        print("  ⭐ Testing getUserFavorites() with authentication...")
        result = await self.make_request(f"/user/{self.demo_user_id}/favorites", headers=headers)
        
        test_results["get_favorites"]["success"] = result["success"]
        test_results["get_favorites"]["status"] = result["status"]
        test_results["get_favorites"]["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            favorites = result.get("data", [])
            favorites_count = len(favorites) if isinstance(favorites, list) else 0
            test_results["get_favorites"]["favorites_count"] = favorites_count
            print(f"    ✅ Get favorites successful: {favorites_count} favorites ({result['response_time_ms']:.1f}ms)")
            test_results["success_messages"].append(f"Get favorites working: {favorites_count} favorites")
        else:
            print(f"    ❌ Get favorites failed: Status {result['status']}")
            if result["status"] == 404:
                test_results["critical_issues"].append("CRITICAL: Favorites endpoint still returning 404 - fix not working")
            else:
                test_results["critical_issues"].append(f"Get favorites failed: Status {result['status']}")
        
        # Test 4: Unauthenticated messages access (should fail)
        print("  🚫 Testing unauthenticated messages access (should fail)...")
        result = await self.make_request(f"/user/{self.demo_user_id}/messages")
        
        test_results["unauthenticated_messages"]["success"] = result["success"]
        test_results["unauthenticated_messages"]["status"] = result["status"]
        test_results["unauthenticated_messages"]["response_time_ms"] = result["response_time_ms"]
        
        if result["status"] in [401, 403]:
            print(f"    ✅ Unauthenticated messages access properly rejected: Status {result['status']}")
            test_results["success_messages"].append("Unauthenticated access properly rejected")
        else:
            print(f"    ⚠️ Unauthenticated messages access not properly rejected: Status {result['status']}")
            test_results["critical_issues"].append("Authentication not properly enforced for messages")
        
        # Determine if fix is working
        messages_working = test_results["get_messages"]["success"]
        send_working = test_results["send_message"]["success"]
        favorites_working = test_results["get_favorites"]["success"]
        
        test_results["fix_working"] = messages_working and (send_working or favorites_working)
        
        return {
            "test_name": "Mobile Messages Authentication",
            "success": test_results["fix_working"],
            "test_results": test_results,
            "critical_issue": not test_results["fix_working"],
            "fix_verified": test_results["fix_working"]
        }
    
    async def run_critical_fixes_testing(self) -> Dict:
        """
        Run complete critical fixes testing
        """
        print("🚨 STARTING CRITICAL FIXES TESTING - URGENT REVIEW REQUEST")
        print("=" * 80)
        print("TESTING: Two critical issues that were just fixed")
        print("FIX 1: Catalyst Database Access for All Users")
        print("FIX 2: Mobile Messages Authentication")
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
            catalyst_test = await self.test_catalyst_access_for_all_users()
            messages_test = await self.test_mobile_messages_authentication()
            
            # Compile comprehensive test results
            test_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Critical fixes verification - Catalyst access and Mobile messages authentication",
                "catalyst_access_test": catalyst_test,
                "mobile_messages_test": messages_test
            }
            
            # Determine overall success
            catalyst_success = catalyst_test.get("success", False)
            messages_success = messages_test.get("success", False)
            
            critical_issues = []
            working_fixes = []
            
            if not catalyst_success:
                critical_issues.extend(catalyst_test.get("test_results", {}).get("critical_issues", []))
            else:
                working_fixes.append("Catalyst Database Access for All Users: ✅ Working")
            
            if not messages_success:
                critical_issues.extend(messages_test.get("test_results", {}).get("critical_issues", []))
            else:
                working_fixes.append("Mobile Messages Authentication: ✅ Working")
            
            test_results["summary"] = {
                "total_fixes_tested": 2,
                "working_fixes": len(working_fixes),
                "failed_fixes": 2 - len(working_fixes),
                "success_rate": (len(working_fixes) / 2) * 100,
                "critical_issues": critical_issues,
                "working_fixes": working_fixes,
                "all_fixes_working": len(working_fixes) == 2,
                "catalyst_fix_verified": catalyst_success,
                "messages_fix_verified": messages_success
            }
            
            return test_results
            
        finally:
            await self.cleanup()


async def main():
    """Run the critical fixes testing"""
    tester = CriticalFixesTester()
    results = await tester.run_critical_fixes_testing()
    
    print("\n" + "=" * 80)
    print("🏁 CRITICAL FIXES TESTING COMPLETED")
    print("=" * 80)
    
    if "error" in results:
        print(f"❌ Testing failed: {results['error']}")
        return
    
    summary = results.get("summary", {})
    
    print(f"📊 RESULTS SUMMARY:")
    print(f"   Total fixes tested: {summary.get('total_fixes_tested', 0)}")
    print(f"   Working fixes: {summary.get('working_fixes', 0)}")
    print(f"   Failed fixes: {summary.get('failed_fixes', 0)}")
    print(f"   Success rate: {summary.get('success_rate', 0):.1f}%")
    
    print(f"\n✅ WORKING FIXES:")
    for fix in summary.get('working_fixes', []):
        print(f"   {fix}")
    
    if summary.get('critical_issues'):
        print(f"\n❌ CRITICAL ISSUES:")
        for issue in summary.get('critical_issues', []):
            print(f"   {issue}")
    
    print(f"\n🎯 SPECIFIC FIX VERIFICATION:")
    print(f"   Catalyst Database Access: {'✅ VERIFIED' if summary.get('catalyst_fix_verified') else '❌ FAILED'}")
    print(f"   Mobile Messages Authentication: {'✅ VERIFIED' if summary.get('messages_fix_verified') else '❌ FAILED'}")
    
    if summary.get('all_fixes_working'):
        print(f"\n🎉 ALL CRITICAL FIXES ARE WORKING CORRECTLY!")
    else:
        print(f"\n⚠️ SOME CRITICAL FIXES NEED ATTENTION")
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())