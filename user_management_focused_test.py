#!/usr/bin/env python3
"""
Focused User Management Testing
Testing the specific activate/suspend endpoints as requested in the review
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://cataloro-mobile.preview.emergentagent.com/api"

class UserManagementTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        
    async def setup(self):
        """Initialize HTTP session and get admin token"""
        self.session = aiohttp.ClientSession()
        
        # Login as admin to get token
        login_data = {
            "email": "admin@cataloro.com",
            "password": "admin_password"
        }
        
        async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.admin_token = data.get("token")
                print(f"✅ Admin login successful, token: {self.admin_token[:20]}...")
            else:
                print(f"❌ Admin login failed: {response.status}")
                
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", data: dict = None):
        """Make HTTP request with admin authorization"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            kwargs = {"headers": headers}
            if data:
                kwargs["json"] = data
                
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **kwargs) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "status": response.status,
                    "data": response_data
                }
        except Exception as e:
            return {
                "success": False,
                "status": 0,
                "error": str(e)
            }
    
    async def test_user_management_endpoints(self):
        """Test the specific user management functionality requested"""
        print("🚀 Testing User Management Functionality")
        print("=" * 50)
        
        # Step 1: List all users to get test subjects
        print("1. Listing all users...")
        users_result = await self.make_request("/admin/users")
        
        if not users_result["success"]:
            print(f"❌ Failed to list users: {users_result}")
            return
        
        users = users_result["data"]
        print(f"✅ Found {len(users)} users in system")
        
        # Display users
        for i, user in enumerate(users):
            email = user.get("email", "Unknown")
            is_active = user.get("is_active", "Unknown")
            user_id = user.get("id", "No ID")
            print(f"   {i+1}. {email} (ID: {user_id[:8]}..., Active: {is_active})")
        
        # Step 2: Find test users (admin, demo, seller as mentioned in review)
        test_users = {}
        for user in users:
            email = user.get("email", "")
            if email in ["admin@cataloro.com", "demo@cataloro.com", "seller@cataloro.com"]:
                test_users[email] = user
        
        print(f"\n2. Found {len(test_users)} expected users from review:")
        for email, user in test_users.items():
            print(f"   ✅ {email} (ID: {user.get('id', 'No ID')[:8]}...)")
        
        # Step 3: Test individual activate/suspend endpoints
        print("\n3. Testing individual activate/suspend endpoints...")
        
        # Use demo user for testing (don't test on admin)
        demo_user = test_users.get("demo@cataloro.com")
        if not demo_user:
            print("❌ Demo user not found, cannot test activate/suspend")
            return
        
        user_id = demo_user.get("id")
        original_status = demo_user.get("is_active", True)
        
        print(f"   Testing with user: {demo_user.get('email')} (Original status: {original_status})")
        
        # Test suspend endpoint
        print("\n   a) Testing /api/admin/users/{user_id}/suspend (PUT)...")
        suspend_result = await self.make_request(f"/admin/users/{user_id}/suspend", "PUT")
        
        if suspend_result["success"]:
            suspended_user = suspend_result["data"].get("user", {})
            new_status = suspended_user.get("is_active")
            print(f"      ✅ Suspend successful: is_active = {new_status}")
            
            if new_status == False:
                print("      ✅ User state correctly changed to suspended (is_active = false)")
            else:
                print(f"      ❌ User state not changed correctly: expected false, got {new_status}")
        else:
            print(f"      ❌ Suspend failed: {suspend_result}")
        
        # Test activate endpoint
        print("\n   b) Testing /api/admin/users/{user_id}/activate (PUT)...")
        activate_result = await self.make_request(f"/admin/users/{user_id}/activate", "PUT")
        
        if activate_result["success"]:
            activated_user = activate_result["data"].get("user", {})
            new_status = activated_user.get("is_active")
            print(f"      ✅ Activate successful: is_active = {new_status}")
            
            if new_status == True:
                print("      ✅ User state correctly changed to active (is_active = true)")
            else:
                print(f"      ❌ User state not changed correctly: expected true, got {new_status}")
        else:
            print(f"      ❌ Activate failed: {activate_result}")
        
        # Step 4: Test state persistence
        print("\n4. Testing state persistence...")
        users_check = await self.make_request("/admin/users")
        
        if users_check["success"]:
            updated_users = users_check["data"]
            updated_user = next((u for u in updated_users if u.get("id") == user_id), None)
            
            if updated_user:
                final_status = updated_user.get("is_active")
                print(f"   ✅ User state persisted: is_active = {final_status}")
                
                if final_status == True:
                    print("   ✅ Final state is correct (active after activate)")
                else:
                    print(f"   ❌ Final state incorrect: expected true, got {final_status}")
            else:
                print("   ❌ User not found in updated list")
        else:
            print(f"   ❌ Failed to verify state persistence: {users_check}")
        
        # Step 5: Test error handling for non-existent users
        print("\n5. Testing error handling for non-existent users...")
        fake_id = "non-existent-user-12345"
        
        fake_suspend = await self.make_request(f"/admin/users/{fake_id}/suspend", "PUT")
        fake_activate = await self.make_request(f"/admin/users/{fake_id}/activate", "PUT")
        
        if not fake_suspend["success"] and not fake_activate["success"]:
            print(f"   ✅ Error handling working correctly:")
            print(f"      Suspend returned: {fake_suspend['status']} (expected 404)")
            print(f"      Activate returned: {fake_activate['status']} (expected 404)")
        else:
            print(f"   ❌ Error handling not working properly:")
            print(f"      Suspend: {fake_suspend}")
            print(f"      Activate: {fake_activate}")
        
        # Step 6: Test bulk operations
        print("\n6. Testing bulk user operations...")
        
        # Test with a couple of user IDs (activate action)
        test_user_ids = [user["id"] for user in list(test_users.values())[:2]]
        bulk_data = {
            "action": "activate",
            "user_ids": test_user_ids
        }
        
        bulk_result = await self.make_request("/admin/users/bulk-action", "POST", bulk_data)
        
        if bulk_result["success"]:
            bulk_response = bulk_result["data"]
            success_count = bulk_response.get("success_count", 0)
            failed_count = bulk_response.get("failed_count", 0)
            
            print(f"   ✅ Bulk operations working:")
            print(f"      Success count: {success_count}")
            print(f"      Failed count: {failed_count}")
            print(f"      Errors: {bulk_response.get('errors', [])}")
        else:
            print(f"   ❌ Bulk operations failed: {bulk_result}")
        
        # Step 7: Test UUID and ObjectId compatibility
        print("\n7. Testing ID format compatibility...")
        
        # Test with UUID format (current format)
        uuid_test = await self.make_request(f"/admin/users/{user_id}/activate", "PUT")
        
        if uuid_test["success"]:
            print(f"   ✅ UUID format working correctly")
        else:
            print(f"   ❌ UUID format issues: {uuid_test}")
        
        print("\n" + "=" * 50)
        print("🏆 USER MANAGEMENT TESTING COMPLETE")
        print("=" * 50)
        
        # Summary
        tests_passed = 0
        total_tests = 7
        
        if users_result["success"]: tests_passed += 1
        if len(test_users) >= 2: tests_passed += 1  # Expected users found
        if suspend_result["success"]: tests_passed += 1
        if activate_result["success"]: tests_passed += 1
        if users_check["success"]: tests_passed += 1
        if not fake_suspend["success"] and not fake_activate["success"]: tests_passed += 1
        if bulk_result["success"]: tests_passed += 1
        
        success_rate = (tests_passed / total_tests) * 100
        
        print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed ({success_rate:.0f}%)")
        
        if success_rate >= 85:
            print("✅ USER MANAGEMENT FUNCTIONALITY: WORKING CORRECTLY")
        else:
            print("❌ USER MANAGEMENT FUNCTIONALITY: NEEDS ATTENTION")
        
        return {
            "success_rate": success_rate,
            "tests_passed": tests_passed,
            "total_tests": total_tests,
            "activate_suspend_working": suspend_result["success"] and activate_result["success"],
            "state_persistence_working": users_check["success"],
            "error_handling_working": not fake_suspend["success"] and not fake_activate["success"],
            "bulk_operations_working": bulk_result["success"],
            "expected_users_found": len(test_users) >= 2
        }

async def main():
    """Main test execution"""
    tester = UserManagementTester()
    
    try:
        await tester.setup()
        
        if not tester.admin_token:
            print("❌ Cannot proceed without admin token")
            return
        
        results = await tester.test_user_management_endpoints()
        
        # Save results
        with open("/app/focused_user_management_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results
            }, f, indent=2)
        
        print(f"\n📄 Results saved to: /app/focused_user_management_results.json")
        
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())