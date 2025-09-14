#!/usr/bin/env python3
"""
CATALYST DATABASE ACCESS FIX TESTING - URGENT
Testing the specific catalyst database access fix for all users (buyers and sellers)

SPECIFIC ISSUE TO TEST:
- User reported: "on desktop version, as buyer and seller - it is not possible to search for catalysts in the add listing function"
- Screenshot shows: "Type to search Cat Database - 0 catalysts available"
- Backend fix applied: Changed endpoint from `require_admin_role` to `require_auth` 
- Frontend fix applied: Removed `isAdminOrManager` condition from `fetchUnifiedCalculations()` call

REQUIRED TESTS:
1. Backend endpoint verification:
   - Test `/api/admin/catalyst/unified-calculations` with admin user (should work)
   - Test `/api/admin/catalyst/unified-calculations` with demo user (non-admin buyer/seller - should work after fix)
   - Verify endpoint returns catalyst data (should be 4000+ entries)

2. Authentication scenarios:
   - Test with valid admin token
   - Test with valid non-admin user token (buyer/seller)
   - Test with no token (should fail with 401/403)

3. Data validation:
   - Verify returned data has catalyst entries with cat_id, name, add_info fields
   - Check response time is reasonable (< 500ms)
   - Confirm data structure is suitable for frontend autocomplete
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://mobileui-sync.preview.emergentagent.com/api"
EXPECTED_CATALYST_COUNT = 4000  # Should be 4000+ entries as mentioned in review

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

# Demo User Configuration (Non-admin buyer/seller)
DEMO_EMAIL = "demo@cataloro.com"
DEMO_PASSWORD = "demo_password"

class CatalystAccessTester:
    """
    CATALYST DATABASE ACCESS FIX TESTING
    Testing the fix that changed endpoint from require_admin_role to require_auth
    to allow all authenticated users (buyers and sellers) to access catalyst database
    """
    
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.admin_user_data = None
        self.demo_user_data = None
        
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
        print("🔐 Authenticating users for catalyst access testing...")
        
        # Authenticate admin user
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            self.admin_user_data = admin_result["data"].get("user", {})
            admin_role = self.admin_user_data.get("user_role", "Unknown")
            print(f"  ✅ Admin authentication successful - Role: {admin_role}")
        else:
            print(f"  ❌ Admin authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
        
        # Authenticate demo user (non-admin buyer/seller)
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            self.demo_user_data = demo_result["data"].get("user", {})
            demo_role = self.demo_user_data.get("user_role", "Unknown")
            print(f"  ✅ Demo user authentication successful - Role: {demo_role}")
            return True
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error', 'Unknown error')}")
            return False
    
    async def test_admin_catalyst_access(self) -> Dict:
        """
        Test 1: Admin user access to catalyst database (should work before and after fix)
        """
        print("👑 Testing admin user access to catalyst database...")
        
        test_results = {
            "endpoint": "/admin/catalyst/unified-calculations",
            "user_type": "admin",
            "user_role": self.admin_user_data.get("user_role", "Unknown") if self.admin_user_data else "Unknown",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "catalyst_count": 0,
            "has_required_fields": False,
            "sample_entry": None,
            "error_messages": [],
            "success": False
        }
        
        if not self.admin_token:
            test_results["error_messages"].append("No admin token available")
            return {"test_name": "Admin Catalyst Access", "success": False, "test_results": test_results}
        
        # Test admin access to catalyst database
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/catalyst/unified-calculations", headers=headers)
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            catalyst_data = result.get("data", [])
            test_results["catalyst_count"] = len(catalyst_data) if isinstance(catalyst_data, list) else 0
            test_results["success"] = True
            
            print(f"    ✅ Admin access successful: {test_results['catalyst_count']} catalyst entries")
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
            
            # Verify catalyst entries have required fields for autocomplete
            if catalyst_data and isinstance(catalyst_data, list) and len(catalyst_data) > 0:
                sample_entry = catalyst_data[0]
                test_results["sample_entry"] = sample_entry
                required_fields = ["cat_id", "name", "add_info"]
                missing_fields = [field for field in required_fields if field not in sample_entry]
                
                if missing_fields:
                    test_results["error_messages"].append(f"Missing required fields: {missing_fields}")
                    print(f"    ⚠️ Missing required fields: {missing_fields}")
                else:
                    test_results["has_required_fields"] = True
                    print(f"    ✅ Catalyst entries have required fields: {required_fields}")
                    print(f"    📋 Sample: cat_id='{sample_entry.get('cat_id')}', name='{sample_entry.get('name')}'")
            
            # Check if we have expected number of entries
            if test_results["catalyst_count"] >= EXPECTED_CATALYST_COUNT:
                print(f"    ✅ Catalyst count meets expectations: {test_results['catalyst_count']} >= {EXPECTED_CATALYST_COUNT}")
            else:
                print(f"    ⚠️ Catalyst count below expectations: {test_results['catalyst_count']} < {EXPECTED_CATALYST_COUNT}")
                
        else:
            test_results["error_messages"].append(f"Admin access failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Admin access failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        return {
            "test_name": "Admin Catalyst Access",
            "success": test_results["success"] and test_results["catalyst_count"] > 0,
            "test_results": test_results,
            "critical_issue": not test_results["success"] or test_results["catalyst_count"] == 0
        }
    
    async def test_non_admin_catalyst_access(self) -> Dict:
        """
        Test 2: Non-admin user (buyer/seller) access to catalyst database (should work after fix)
        This is the main test for the reported issue
        """
        print("👤 Testing non-admin user (buyer/seller) access to catalyst database...")
        
        test_results = {
            "endpoint": "/admin/catalyst/unified-calculations",
            "user_type": "non-admin",
            "user_role": self.demo_user_data.get("user_role", "Unknown") if self.demo_user_data else "Unknown",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "catalyst_count": 0,
            "has_required_fields": False,
            "sample_entry": None,
            "error_messages": [],
            "success": False,
            "fix_working": False
        }
        
        if not self.demo_token:
            test_results["error_messages"].append("No demo token available")
            return {"test_name": "Non-Admin Catalyst Access", "success": False, "test_results": test_results}
        
        # Test non-admin access to catalyst database
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        result = await self.make_request("/admin/catalyst/unified-calculations", headers=headers)
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            catalyst_data = result.get("data", [])
            test_results["catalyst_count"] = len(catalyst_data) if isinstance(catalyst_data, list) else 0
            test_results["success"] = True
            test_results["fix_working"] = True
            
            print(f"    ✅ Non-admin access successful: {test_results['catalyst_count']} catalyst entries")
            print(f"    ✅ FIX WORKING: Non-admin users can now access catalyst database!")
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
            
            # Verify catalyst entries have required fields for autocomplete
            if catalyst_data and isinstance(catalyst_data, list) and len(catalyst_data) > 0:
                sample_entry = catalyst_data[0]
                test_results["sample_entry"] = sample_entry
                required_fields = ["cat_id", "name", "add_info"]
                missing_fields = [field for field in required_fields if field not in sample_entry]
                
                if missing_fields:
                    test_results["error_messages"].append(f"Missing required fields: {missing_fields}")
                    print(f"    ⚠️ Missing required fields: {missing_fields}")
                else:
                    test_results["has_required_fields"] = True
                    print(f"    ✅ Catalyst entries have required fields: {required_fields}")
                    print(f"    📋 Sample: cat_id='{sample_entry.get('cat_id')}', name='{sample_entry.get('name')}'")
            
            # Check if we have expected number of entries
            if test_results["catalyst_count"] >= EXPECTED_CATALYST_COUNT:
                print(f"    ✅ Catalyst count meets expectations: {test_results['catalyst_count']} >= {EXPECTED_CATALYST_COUNT}")
            else:
                print(f"    ⚠️ Catalyst count below expectations: {test_results['catalyst_count']} < {EXPECTED_CATALYST_COUNT}")
                
        else:
            test_results["error_messages"].append(f"Non-admin access failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Non-admin access failed: Status {result['status']}")
            print(f"    ❌ FIX NOT WORKING: Non-admin users still cannot access catalyst database")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        return {
            "test_name": "Non-Admin Catalyst Access",
            "success": test_results["success"] and test_results["catalyst_count"] > 0,
            "test_results": test_results,
            "critical_issue": not test_results["success"] or test_results["catalyst_count"] == 0,
            "fix_working": test_results["fix_working"]
        }
    
    async def test_unauthenticated_access(self) -> Dict:
        """
        Test 3: Unauthenticated access (should fail with 401/403)
        """
        print("🚫 Testing unauthenticated access to catalyst database (should fail)...")
        
        test_results = {
            "endpoint": "/admin/catalyst/unified-calculations",
            "user_type": "unauthenticated",
            "expected_status": [401, 403],
            "actual_status": 0,
            "response_time_ms": 0,
            "properly_rejected": False,
            "error_messages": [],
            "success": False
        }
        
        # Test without authentication
        result = await self.make_request("/admin/catalyst/unified-calculations")
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["status"] in [401, 403]:
            test_results["properly_rejected"] = True
            test_results["success"] = True
            print(f"    ✅ Unauthenticated access properly rejected: Status {result['status']}")
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
        else:
            test_results["error_messages"].append(f"Unauthenticated access not properly rejected: Status {result['status']}")
            print(f"    ❌ Unauthenticated access not properly rejected: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        return {
            "test_name": "Unauthenticated Access",
            "success": test_results["success"] and test_results["properly_rejected"],
            "test_results": test_results,
            "critical_issue": not test_results["properly_rejected"]
        }
    
    async def test_data_consistency(self) -> Dict:
        """
        Test 4: Verify admin and non-admin users get the same catalyst data
        """
        print("🔄 Testing data consistency between admin and non-admin access...")
        
        test_results = {
            "admin_count": 0,
            "non_admin_count": 0,
            "data_consistent": False,
            "admin_sample": None,
            "non_admin_sample": None,
            "error_messages": [],
            "success": False
        }
        
        if not self.admin_token or not self.demo_token:
            test_results["error_messages"].append("Missing authentication tokens")
            return {"test_name": "Data Consistency", "success": False, "test_results": test_results}
        
        # Get admin data
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        admin_result = await self.make_request("/admin/catalyst/unified-calculations", headers=admin_headers)
        
        if admin_result["success"]:
            admin_data = admin_result.get("data", [])
            test_results["admin_count"] = len(admin_data) if isinstance(admin_data, list) else 0
            if admin_data and isinstance(admin_data, list) and len(admin_data) > 0:
                test_results["admin_sample"] = admin_data[0]
        
        # Get non-admin data
        demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
        demo_result = await self.make_request("/admin/catalyst/unified-calculations", headers=demo_headers)
        
        if demo_result["success"]:
            demo_data = demo_result.get("data", [])
            test_results["non_admin_count"] = len(demo_data) if isinstance(demo_data, list) else 0
            if demo_data and isinstance(demo_data, list) and len(demo_data) > 0:
                test_results["non_admin_sample"] = demo_data[0]
        
        # Check consistency
        if test_results["admin_count"] == test_results["non_admin_count"] and test_results["admin_count"] > 0:
            test_results["data_consistent"] = True
            test_results["success"] = True
            print(f"    ✅ Data consistent: Both admin and non-admin get {test_results['admin_count']} entries")
            
            # Compare sample entries
            if test_results["admin_sample"] and test_results["non_admin_sample"]:
                admin_cat_id = test_results["admin_sample"].get("cat_id")
                demo_cat_id = test_results["non_admin_sample"].get("cat_id")
                if admin_cat_id == demo_cat_id:
                    print(f"    ✅ Sample entries match: cat_id='{admin_cat_id}'")
                else:
                    print(f"    ⚠️ Sample entries differ: admin='{admin_cat_id}', demo='{demo_cat_id}'")
        else:
            test_results["error_messages"].append(f"Data inconsistent: admin={test_results['admin_count']}, non-admin={test_results['non_admin_count']}")
            print(f"    ❌ Data inconsistent: admin={test_results['admin_count']}, non-admin={test_results['non_admin_count']}")
        
        return {
            "test_name": "Data Consistency",
            "success": test_results["success"] and test_results["data_consistent"],
            "test_results": test_results,
            "critical_issue": not test_results["data_consistent"]
        }
    
    async def test_performance(self) -> Dict:
        """
        Test 5: Verify response time is reasonable (< 500ms as specified)
        """
        print("⚡ Testing catalyst database response performance...")
        
        test_results = {
            "admin_response_time": 0,
            "non_admin_response_time": 0,
            "target_time_ms": 500,
            "admin_meets_target": False,
            "non_admin_meets_target": False,
            "error_messages": [],
            "success": False
        }
        
        if not self.admin_token or not self.demo_token:
            test_results["error_messages"].append("Missing authentication tokens")
            return {"test_name": "Performance", "success": False, "test_results": test_results}
        
        # Test admin performance
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        admin_result = await self.make_request("/admin/catalyst/unified-calculations", headers=admin_headers)
        test_results["admin_response_time"] = admin_result["response_time_ms"]
        test_results["admin_meets_target"] = admin_result["response_time_ms"] < test_results["target_time_ms"]
        
        # Test non-admin performance
        demo_headers = {"Authorization": f"Bearer {self.demo_token}"}
        demo_result = await self.make_request("/admin/catalyst/unified-calculations", headers=demo_headers)
        test_results["non_admin_response_time"] = demo_result["response_time_ms"]
        test_results["non_admin_meets_target"] = demo_result["response_time_ms"] < test_results["target_time_ms"]
        
        # Evaluate performance
        if test_results["admin_meets_target"] and test_results["non_admin_meets_target"]:
            test_results["success"] = True
            print(f"    ✅ Performance excellent:")
            print(f"      Admin: {test_results['admin_response_time']:.1f}ms < {test_results['target_time_ms']}ms")
            print(f"      Non-admin: {test_results['non_admin_response_time']:.1f}ms < {test_results['target_time_ms']}ms")
        else:
            if not test_results["admin_meets_target"]:
                test_results["error_messages"].append(f"Admin response too slow: {test_results['admin_response_time']:.1f}ms")
                print(f"    ❌ Admin response too slow: {test_results['admin_response_time']:.1f}ms > {test_results['target_time_ms']}ms")
            if not test_results["non_admin_meets_target"]:
                test_results["error_messages"].append(f"Non-admin response too slow: {test_results['non_admin_response_time']:.1f}ms")
                print(f"    ❌ Non-admin response too slow: {test_results['non_admin_response_time']:.1f}ms > {test_results['target_time_ms']}ms")
        
        return {
            "test_name": "Performance",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def run_catalyst_access_tests(self) -> Dict:
        """
        Run complete catalyst database access fix testing
        """
        print("🚨 STARTING CATALYST DATABASE ACCESS FIX TESTING")
        print("=" * 80)
        print("ISSUE: User reported 'it is not possible to search for catalysts in the add listing function'")
        print("FIX: Changed endpoint from require_admin_role to require_auth")
        print("TESTING: Verify all authenticated users (buyers and sellers) can access catalyst database")
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
            
            # Run all catalyst access tests
            admin_test = await self.test_admin_catalyst_access()
            non_admin_test = await self.test_non_admin_catalyst_access()
            unauth_test = await self.test_unauthenticated_access()
            consistency_test = await self.test_data_consistency()
            performance_test = await self.test_performance()
            
            # Compile comprehensive test results
            test_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Catalyst database access fix for all users (buyers and sellers)",
                "issue_description": "User reported: 'it is not possible to search for catalysts in the add listing function'",
                "fix_description": "Changed endpoint from require_admin_role to require_auth",
                "admin_access_test": admin_test,
                "non_admin_access_test": non_admin_test,
                "unauthenticated_access_test": unauth_test,
                "data_consistency_test": consistency_test,
                "performance_test": performance_test
            }
            
            # Determine critical findings
            critical_issues = []
            working_features = []
            
            tests = [admin_test, non_admin_test, unauth_test, consistency_test, performance_test]
            
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
            
            # Determine if the fix is working
            fix_working = non_admin_test.get("fix_working", False)
            
            test_results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": success_rate,
                "critical_issues": critical_issues,
                "working_features": working_features,
                "fix_working": fix_working,
                "all_tests_passed": len(critical_issues) == 0,
                "admin_access_working": admin_test.get("success", False),
                "non_admin_access_working": non_admin_test.get("success", False),
                "authentication_enforced": unauth_test.get("success", False),
                "data_consistent": consistency_test.get("success", False),
                "performance_acceptable": performance_test.get("success", False)
            }
            
            return test_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution"""
    tester = CatalystAccessTester()
    results = await tester.run_catalyst_access_tests()
    
    print("\n" + "=" * 80)
    print("🏁 CATALYST DATABASE ACCESS FIX TESTING COMPLETE")
    print("=" * 80)
    
    summary = results.get("summary", {})
    
    print(f"📊 Test Results:")
    print(f"   Total Tests: {summary.get('total_tests', 0)}")
    print(f"   Successful: {summary.get('successful_tests', 0)}")
    print(f"   Failed: {summary.get('failed_tests', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
    
    print(f"\n🎯 Fix Status:")
    if summary.get("fix_working", False):
        print("   ✅ FIX WORKING: Non-admin users can now access catalyst database")
    else:
        print("   ❌ FIX NOT WORKING: Non-admin users still cannot access catalyst database")
    
    print(f"\n🔍 Detailed Results:")
    print(f"   Admin Access: {'✅' if summary.get('admin_access_working', False) else '❌'}")
    print(f"   Non-Admin Access: {'✅' if summary.get('non_admin_access_working', False) else '❌'}")
    print(f"   Authentication Enforced: {'✅' if summary.get('authentication_enforced', False) else '❌'}")
    print(f"   Data Consistent: {'✅' if summary.get('data_consistent', False) else '❌'}")
    print(f"   Performance Acceptable: {'✅' if summary.get('performance_acceptable', False) else '❌'}")
    
    if summary.get("critical_issues"):
        print(f"\n❌ Critical Issues:")
        for issue in summary["critical_issues"]:
            print(f"   - {issue}")
    
    if summary.get("working_features"):
        print(f"\n✅ Working Features:")
        for feature in summary["working_features"]:
            print(f"   - {feature}")
    
    print("\n" + "=" * 80)
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())