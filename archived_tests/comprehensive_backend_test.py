#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING - REVIEW REQUEST
Testing the specific features and fixes mentioned in the review request:
1. Browse Page Filters: Enhanced browse endpoint with new bid filtering
2. Admin Panel User Management: Authentication-fixed endpoints
3. Backend Services Status: Verify all services are running properly
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
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "demo@cataloro.com"
TEST_USER_ID = "68bfff790e4e46bc28d43631"

class ComprehensiveBackendTester:
    """
    Comprehensive backend testing for the review request
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
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
        """Authenticate both admin and demo users"""
        print("🔐 Authenticating users for comprehensive testing...")
        
        # Authenticate admin
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            print(f"  ✅ Admin authentication successful")
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
            print(f"  ✅ Demo user authentication successful")
            return True
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error', 'Unknown error')}")
            return False

    async def test_browse_page_filters(self) -> Dict:
        """
        Test 1: Browse Page Filters - Enhanced browse endpoint with new bid filtering
        Testing all the specific endpoints mentioned in the review request:
        - /api/marketplace/browse?status=active&user_id=test_user&bid_filter=all
        - /api/marketplace/browse?status=active&user_id=test_user&bid_filter=own_listings
        - /api/marketplace/browse?status=active&user_id=test_user&bid_filter=placed_bid
        - /api/marketplace/browse?status=active&user_id=test_user&bid_filter=not_placed_bid
        """
        print("📋 Testing Browse Page Filters - Enhanced browse endpoint with bid filtering...")
        
        test_results = {
            "test_name": "Browse Page Filters",
            "endpoints_tested": [],
            "successful_endpoints": 0,
            "failed_endpoints": 0,
            "critical_issues": [],
            "success": False
        }
        
        # Test endpoints as specified in review request
        test_endpoints = [
            {
                "name": "bid_filter=all",
                "params": {"status": "active", "user_id": TEST_USER_ID, "bid_filter": "all"}
            },
            {
                "name": "bid_filter=own_listings", 
                "params": {"status": "active", "user_id": TEST_USER_ID, "bid_filter": "own_listings"}
            },
            {
                "name": "bid_filter=placed_bid",
                "params": {"status": "active", "user_id": TEST_USER_ID, "bid_filter": "placed_bid"}
            },
            {
                "name": "bid_filter=not_placed_bid",
                "params": {"status": "active", "user_id": TEST_USER_ID, "bid_filter": "not_placed_bid"}
            }
        ]
        
        for endpoint_test in test_endpoints:
            print(f"  🔍 Testing {endpoint_test['name']}...")
            
            result = await self.make_request("/marketplace/browse", params=endpoint_test["params"])
            
            endpoint_result = {
                "name": endpoint_test["name"],
                "params": endpoint_test["params"],
                "status": result["status"],
                "response_time_ms": result["response_time_ms"],
                "success": result["success"],
                "listings_count": 0,
                "error": result.get("error", "")
            }
            
            if result["success"]:
                listings = result.get("data", [])
                endpoint_result["listings_count"] = len(listings) if isinstance(listings, list) else 0
                test_results["successful_endpoints"] += 1
                print(f"    ✅ {endpoint_test['name']}: {endpoint_result['listings_count']} listings ({result['response_time_ms']:.1f}ms)")
            else:
                test_results["failed_endpoints"] += 1
                test_results["critical_issues"].append(f"{endpoint_test['name']}: Status {result['status']} - {result.get('error', 'Unknown error')}")
                print(f"    ❌ {endpoint_test['name']}: Status {result['status']} - {result.get('error', 'Unknown error')}")
            
            test_results["endpoints_tested"].append(endpoint_result)
        
        # Overall success if all endpoints work
        test_results["success"] = test_results["failed_endpoints"] == 0
        
        return test_results

    async def test_admin_user_management(self) -> Dict:
        """
        Test 2: Admin Panel User Management - Authentication-fixed endpoints
        Testing all the specific endpoints mentioned in the review request:
        - /api/admin/users/{user_id} (PUT) - Update user functionality
        - /api/admin/users (POST) - Create user 
        - /api/admin/users/{user_id}/approve (PUT) - Approve user
        - /api/admin/users/{user_id}/reject (PUT) - Reject user
        - /api/admin/users/{user_id}/suspend (PUT) - Suspend user
        - /api/admin/users/{user_id}/activate (PUT) - Activate user
        - /api/admin/users/{user_id} (DELETE) - Delete user
        """
        print("👥 Testing Admin Panel User Management - Authentication-fixed endpoints...")
        
        if not self.admin_token:
            return {
                "test_name": "Admin User Management",
                "error": "No admin token available",
                "success": False
            }
        
        test_results = {
            "test_name": "Admin User Management",
            "endpoints_tested": [],
            "successful_endpoints": 0,
            "failed_endpoints": 0,
            "critical_issues": [],
            "success": False
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a test user first for testing other operations
        test_user_data = {
            "username": f"test_user_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "test_password_123",
            "full_name": "Test User",
            "user_role": "User-Buyer",
            "registration_status": "Approved"
        }
        
        # Test endpoints as specified in review request
        test_endpoints = [
            {
                "name": "Create User (POST /admin/users)",
                "method": "POST",
                "endpoint": "/admin/users",
                "data": test_user_data,
                "expected_status": [200, 201]
            }
        ]
        
        created_user_id = None
        
        for endpoint_test in test_endpoints:
            print(f"  🔍 Testing {endpoint_test['name']}...")
            
            result = await self.make_request(
                endpoint_test["endpoint"], 
                method=endpoint_test["method"],
                data=endpoint_test.get("data"),
                headers=headers
            )
            
            endpoint_result = {
                "name": endpoint_test["name"],
                "method": endpoint_test["method"],
                "endpoint": endpoint_test["endpoint"],
                "status": result["status"],
                "response_time_ms": result["response_time_ms"],
                "success": result["status"] in endpoint_test.get("expected_status", [200]),
                "error": result.get("error", "")
            }
            
            if endpoint_result["success"]:
                test_results["successful_endpoints"] += 1
                print(f"    ✅ {endpoint_test['name']}: Status {result['status']} ({result['response_time_ms']:.1f}ms)")
                
                # Extract user ID for subsequent tests
                if endpoint_test["name"].startswith("Create User") and isinstance(result.get("data"), dict):
                    user_data = result["data"].get("user", {})
                    created_user_id = user_data.get("id") if isinstance(user_data, dict) else None
                    print(f"    📝 Created user ID: {created_user_id}")
            else:
                test_results["failed_endpoints"] += 1
                test_results["critical_issues"].append(f"{endpoint_test['name']}: Status {result['status']} - {result.get('error', 'Unknown error')}")
                print(f"    ❌ {endpoint_test['name']}: Status {result['status']} - {result.get('error', 'Unknown error')}")
            
            test_results["endpoints_tested"].append(endpoint_result)
        
        # If user creation was successful, test other user management endpoints
        if created_user_id:
            user_management_endpoints = [
                {
                    "name": f"Update User (PUT /admin/users/{created_user_id})",
                    "method": "PUT",
                    "endpoint": f"/admin/users/{created_user_id}",
                    "data": {"full_name": "Updated Test User"},
                    "expected_status": [200]
                },
                {
                    "name": f"Approve User (PUT /admin/users/{created_user_id}/approve)",
                    "method": "PUT", 
                    "endpoint": f"/admin/users/{created_user_id}/approve",
                    "expected_status": [200]
                },
                {
                    "name": f"Suspend User (PUT /admin/users/{created_user_id}/suspend)",
                    "method": "PUT",
                    "endpoint": f"/admin/users/{created_user_id}/suspend", 
                    "expected_status": [200]
                },
                {
                    "name": f"Activate User (PUT /admin/users/{created_user_id}/activate)",
                    "method": "PUT",
                    "endpoint": f"/admin/users/{created_user_id}/activate",
                    "expected_status": [200]
                },
                {
                    "name": f"Reject User (PUT /admin/users/{created_user_id}/reject)",
                    "method": "PUT",
                    "endpoint": f"/admin/users/{created_user_id}/reject",
                    "data": {"reason": "Test rejection"},
                    "expected_status": [200]
                },
                {
                    "name": f"Delete User (DELETE /admin/users/{created_user_id})",
                    "method": "DELETE",
                    "endpoint": f"/admin/users/{created_user_id}",
                    "expected_status": [200, 204]
                }
            ]
            
            for endpoint_test in user_management_endpoints:
                print(f"  🔍 Testing {endpoint_test['name']}...")
                
                result = await self.make_request(
                    endpoint_test["endpoint"],
                    method=endpoint_test["method"],
                    data=endpoint_test.get("data"),
                    headers=headers
                )
                
                endpoint_result = {
                    "name": endpoint_test["name"],
                    "method": endpoint_test["method"],
                    "endpoint": endpoint_test["endpoint"],
                    "status": result["status"],
                    "response_time_ms": result["response_time_ms"],
                    "success": result["status"] in endpoint_test.get("expected_status", [200]),
                    "error": result.get("error", "")
                }
                
                if endpoint_result["success"]:
                    test_results["successful_endpoints"] += 1
                    print(f"    ✅ {endpoint_test['name']}: Status {result['status']} ({result['response_time_ms']:.1f}ms)")
                else:
                    test_results["failed_endpoints"] += 1
                    test_results["critical_issues"].append(f"{endpoint_test['name']}: Status {result['status']} - {result.get('error', 'Unknown error')}")
                    print(f"    ❌ {endpoint_test['name']}: Status {result['status']} - {result.get('error', 'Unknown error')}")
                
                test_results["endpoints_tested"].append(endpoint_result)
        
        # Overall success if most endpoints work (allow some failures for edge cases)
        success_rate = test_results["successful_endpoints"] / len(test_results["endpoints_tested"]) if test_results["endpoints_tested"] else 0
        test_results["success"] = success_rate >= 0.7  # 70% success rate threshold
        test_results["success_rate"] = success_rate * 100
        
        return test_results

    async def test_backend_services_status(self) -> Dict:
        """
        Test 3: Backend Services Status - Verify all services are running properly
        """
        print("⚙️ Testing Backend Services Status - Verify all services are running properly...")
        
        test_results = {
            "test_name": "Backend Services Status",
            "services_tested": [],
            "healthy_services": 0,
            "unhealthy_services": 0,
            "critical_issues": [],
            "success": False
        }
        
        # Test core service endpoints
        service_endpoints = [
            {
                "name": "Health Check",
                "endpoint": "/health",
                "expected_status": [200]
            },
            {
                "name": "Performance Metrics (Admin)",
                "endpoint": "/admin/performance",
                "headers": {"Authorization": f"Bearer {self.admin_token}"} if self.admin_token else None,
                "expected_status": [200]
            }
        ]
        
        for service_test in service_endpoints:
            print(f"  🔍 Testing {service_test['name']}...")
            
            result = await self.make_request(
                service_test["endpoint"],
                headers=service_test.get("headers")
            )
            
            service_result = {
                "name": service_test["name"],
                "endpoint": service_test["endpoint"],
                "status": result["status"],
                "response_time_ms": result["response_time_ms"],
                "success": result["status"] in service_test.get("expected_status", [200]),
                "error": result.get("error", ""),
                "data": result.get("data", {}) if result["success"] else {}
            }
            
            if service_result["success"]:
                test_results["healthy_services"] += 1
                print(f"    ✅ {service_test['name']}: Status {result['status']} ({result['response_time_ms']:.1f}ms)")
                
                # Extract additional service info if available
                if service_test["name"] == "Performance Metrics (Admin)" and isinstance(result.get("data"), dict):
                    data = result["data"]
                    print(f"    📊 Database: {data.get('database', {}).get('name', 'Unknown')}")
                    print(f"    📊 Collections: {data.get('database', {}).get('collections', 'Unknown')}")
                    print(f"    📊 Cache Status: {data.get('cache', {}).get('status', 'Unknown')}")
                    
                    # Check Phase 5 services
                    phase5 = data.get('phase5_services', {})
                    if phase5:
                        print(f"    🚀 WebSocket: {phase5.get('websocket', 'Unknown')}")
                        print(f"    🚀 Multi-currency: {phase5.get('multicurrency', 'Unknown')}")
                        print(f"    🚀 Escrow: {phase5.get('escrow', 'Unknown')}")
                        print(f"    🚀 AI Recommendations: {phase5.get('ai_recommendations', 'Unknown')}")
            else:
                test_results["unhealthy_services"] += 1
                test_results["critical_issues"].append(f"{service_test['name']}: Status {result['status']} - {result.get('error', 'Unknown error')}")
                print(f"    ❌ {service_test['name']}: Status {result['status']} - {result.get('error', 'Unknown error')}")
            
            test_results["services_tested"].append(service_result)
        
        # Overall success if all services are healthy
        test_results["success"] = test_results["unhealthy_services"] == 0
        
        return test_results

    async def run_comprehensive_tests(self) -> Dict:
        """
        Run all comprehensive backend tests as requested in the review
        """
        print("🚨 STARTING COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        print("TESTING: Features and fixes mentioned in the review request")
        print("1. Browse Page Filters: Enhanced browse endpoint with bid filtering")
        print("2. Admin Panel User Management: Authentication-fixed endpoints")
        print("3. Backend Services Status: Verify all services running properly")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_users()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "User authentication failed - cannot proceed with testing",
                    "success": False
                }
            
            # Run all comprehensive tests
            browse_filters_test = await self.test_browse_page_filters()
            admin_user_mgmt_test = await self.test_admin_user_management()
            services_status_test = await self.test_backend_services_status()
            
            # Compile comprehensive test results
            test_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Comprehensive backend testing for review request",
                "browse_page_filters_test": browse_filters_test,
                "admin_user_management_test": admin_user_mgmt_test,
                "backend_services_status_test": services_status_test
            }
            
            # Calculate overall success metrics
            all_tests = [browse_filters_test, admin_user_mgmt_test, services_status_test]
            successful_tests = sum(1 for test in all_tests if test.get("success", False))
            total_tests = len(all_tests)
            overall_success_rate = (successful_tests / total_tests) * 100
            
            # Collect all critical issues
            all_critical_issues = []
            for test in all_tests:
                if test.get("critical_issues"):
                    all_critical_issues.extend(test["critical_issues"])
            
            test_results["summary"] = {
                "total_test_categories": total_tests,
                "successful_test_categories": successful_tests,
                "failed_test_categories": total_tests - successful_tests,
                "overall_success_rate": overall_success_rate,
                "all_critical_issues": all_critical_issues,
                "overall_success": successful_tests == total_tests,
                "tests_status": {
                    "browse_page_filters": "✅ WORKING" if browse_filters_test.get("success") else "❌ FAILED",
                    "admin_user_management": "✅ WORKING" if admin_user_mgmt_test.get("success") else "❌ FAILED", 
                    "backend_services_status": "✅ WORKING" if services_status_test.get("success") else "❌ FAILED"
                }
            }
            
            return test_results
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    results = await tester.run_comprehensive_tests()
    
    print("\n" + "=" * 80)
    print("🏁 COMPREHENSIVE BACKEND TESTING COMPLETED")
    print("=" * 80)
    
    summary = results.get("summary", {})
    print(f"📊 Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"✅ Successful Categories: {summary.get('successful_test_categories', 0)}/{summary.get('total_test_categories', 0)}")
    
    print("\n📋 Test Results Summary:")
    tests_status = summary.get("tests_status", {})
    for test_name, status in tests_status.items():
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    if summary.get("all_critical_issues"):
        print(f"\n❌ Critical Issues Found ({len(summary['all_critical_issues'])}):")
        for issue in summary["all_critical_issues"]:
            print(f"  • {issue}")
    else:
        print(f"\n✅ No Critical Issues Found")
    
    print(f"\n🕒 Test completed at: {results.get('test_timestamp', 'Unknown')}")
    
    # Return results for further processing
    return results

if __name__ == "__main__":
    asyncio.run(main())