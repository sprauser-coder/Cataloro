#!/usr/bin/env python3
"""
UNIFIED CALCULATIONS ENDPOINT FIX TEST
Testing the fix for the "0 entries" issue in add listing function
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://cataloro-admin-fix.preview.emergentagent.com/api"

# Test Users
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "demo@cataloro.com"

class UnifiedCalculationsFixTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", data: dict = None, headers: dict = None):
        """Make HTTP request"""
        try:
            request_kwargs = {}
            if data:
                request_kwargs['json'] = data
            if headers:
                request_kwargs['headers'] = headers
            
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **request_kwargs) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "data": response_data,
                    "status": response.status
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": 0
            }
    
    async def authenticate_users(self):
        """Authenticate both admin and demo users"""
        print("🔐 Authenticating users...")
        
        # Authenticate admin
        admin_result = await self.make_request("/auth/login", "POST", data={
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        })
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            print(f"  ✅ Admin authentication successful")
        else:
            print(f"  ❌ Admin authentication failed")
            return False
        
        # Authenticate demo user
        demo_result = await self.make_request("/auth/login", "POST", data={
            "email": DEMO_EMAIL,
            "password": "demo_password"
        })
        
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            demo_user = demo_result["data"].get("user", {})
            print(f"  ✅ Demo user authentication successful")
            print(f"    - Role: {demo_user.get('user_role', 'Unknown')}")
            print(f"    - Badge: {demo_user.get('badge', 'Unknown')}")
        else:
            print(f"  ❌ Demo user authentication failed")
            return False
        
        return True
    
    async def test_admin_access(self):
        """Test admin access to unified calculations"""
        print("\n🔑 Testing ADMIN access to unified calculations...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/catalyst/unified-calculations", headers=headers)
        
        if result["success"]:
            catalyst_data = result.get("data", [])
            count = len(catalyst_data) if isinstance(catalyst_data, list) else 0
            print(f"  ✅ Admin can access endpoint: {count} catalyst entries returned")
            
            if count > 0:
                sample = catalyst_data[0]
                print(f"  📋 Sample entry: cat_id='{sample.get('cat_id')}', name='{sample.get('name')}'")
            
            return {"success": True, "count": count, "sample": catalyst_data[0] if count > 0 else None}
        else:
            print(f"  ❌ Admin access failed: Status {result['status']}")
            return {"success": False, "error": result.get("error", "Unknown error")}
    
    async def test_demo_user_access(self):
        """Test demo user (non-admin) access to unified calculations"""
        print("\n👤 Testing DEMO USER (non-admin) access to unified calculations...")
        
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        result = await self.make_request("/admin/catalyst/unified-calculations", headers=headers)
        
        if result["success"]:
            catalyst_data = result.get("data", [])
            count = len(catalyst_data) if isinstance(catalyst_data, list) else 0
            print(f"  ⚠️ Demo user can access endpoint: {count} catalyst entries returned")
            print(f"    This should NOT happen - endpoint should be admin-only!")
            return {"success": True, "count": count, "should_fail": True}
        else:
            expected_status = result["status"] in [401, 403]
            print(f"  {'✅' if expected_status else '❌'} Demo user access {'properly rejected' if expected_status else 'failed unexpectedly'}: Status {result['status']}")
            return {"success": False, "status": result["status"], "expected_rejection": expected_status}
    
    async def test_unauthenticated_access(self):
        """Test unauthenticated access to unified calculations"""
        print("\n🚫 Testing UNAUTHENTICATED access to unified calculations...")
        
        result = await self.make_request("/admin/catalyst/unified-calculations")
        
        if result["success"]:
            print(f"  ❌ Unauthenticated access should not succeed!")
            return {"success": True, "should_fail": True}
        else:
            expected_status = result["status"] in [401, 403]
            print(f"  {'✅' if expected_status else '❌'} Unauthenticated access {'properly rejected' if expected_status else 'failed unexpectedly'}: Status {result['status']}")
            return {"success": False, "status": result["status"], "expected_rejection": expected_status}
    
    async def run_comprehensive_test(self):
        """Run comprehensive test of unified calculations endpoint access"""
        print("🚨 UNIFIED CALCULATIONS ENDPOINT ACCESS TEST")
        print("=" * 80)
        print("TESTING: Who can access /api/admin/catalyst/unified-calculations")
        print("ISSUE: Add listing shows 0 entries for non-admin users")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate users
            if not await self.authenticate_users():
                return {"error": "Authentication failed"}
            
            # Test different access levels
            admin_test = await self.test_admin_access()
            demo_test = await self.test_demo_user_access()
            unauth_test = await self.test_unauthenticated_access()
            
            # Analyze results
            print("\n" + "=" * 80)
            print("📊 TEST RESULTS ANALYSIS")
            print("=" * 80)
            
            # Root cause analysis
            root_cause_identified = False
            fix_needed = False
            
            if admin_test.get("success") and admin_test.get("count", 0) > 0:
                print(f"✅ ADMIN ACCESS: Working correctly ({admin_test['count']} entries)")
            else:
                print(f"❌ ADMIN ACCESS: Failed - this is a critical issue")
            
            if not demo_test.get("success") and demo_test.get("expected_rejection"):
                print(f"✅ DEMO USER ACCESS: Properly rejected (Status {demo_test['status']})")
                print(f"🔍 ROOT CAUSE IDENTIFIED: Non-admin users cannot access catalyst data")
                print(f"💡 SOLUTION: Frontend should only call endpoint for admin users")
                root_cause_identified = True
                fix_needed = True
            elif demo_test.get("success"):
                print(f"⚠️ DEMO USER ACCESS: Unexpectedly succeeded - security issue!")
            else:
                print(f"❌ DEMO USER ACCESS: Failed unexpectedly")
            
            if not unauth_test.get("success") and unauth_test.get("expected_rejection"):
                print(f"✅ UNAUTHENTICATED ACCESS: Properly rejected (Status {unauth_test['status']})")
            else:
                print(f"❌ UNAUTHENTICATED ACCESS: Security issue!")
            
            # Summary
            print("\n🎯 CONCLUSION:")
            if root_cause_identified:
                print("✅ Root cause identified: Frontend calls admin-only endpoint for all users")
                print("🔧 Fix needed: Add role check before calling fetchUnifiedCalculations()")
                print("📝 Frontend should only call endpoint if user is admin/manager")
            else:
                print("❌ Root cause not clearly identified - further investigation needed")
            
            return {
                "test_timestamp": datetime.now().isoformat(),
                "admin_test": admin_test,
                "demo_test": demo_test,
                "unauth_test": unauth_test,
                "root_cause_identified": root_cause_identified,
                "fix_needed": fix_needed,
                "conclusion": "Frontend calls admin-only endpoint for all users" if root_cause_identified else "Further investigation needed"
            }
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = UnifiedCalculationsFixTester()
    results = await tester.run_comprehensive_test()
    
    # Save results
    with open('/app/unified_calculations_fix_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Test results saved to: /app/unified_calculations_fix_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())