#!/usr/bin/env python3
"""
Demo User Data Consistency Testing
Testing the fix for demo_user data inconsistency issue where browse page showed 9 demo_user listings 
but management center showed 0. The fix ensures demo_user authentication returns the correct user ID 
that matches existing listing seller_ids in the database.
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-partners.preview.emergentagent.com/api"

# Demo User Configuration (from review request)
DEMO_EMAILS = ["user@cataloro.com", "demo@cataloro.com", "demo_user@cataloro.com"]
EXPECTED_DEMO_USER_ID = "68bfff790e4e46bc28d43631"  # Fixed user ID that should match existing listings
EXPECTED_DEMO_LISTINGS_COUNT = 9  # Expected number of demo_user listings

class DemoUserConsistencyTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
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
    
    async def test_demo_user_authentication(self) -> Dict:
        """Test Demo User Authentication - login with demo emails should return correct user ID"""
        print("🔐 Testing Demo User Authentication...")
        
        auth_results = []
        
        for email in DEMO_EMAILS:
            print(f"  Testing login with: {email}")
            
            login_data = {
                "email": email,
                "password": "demo_password"  # Mock password for testing
            }
            
            result = await self.make_request("/auth/login", "POST", data=login_data)
            
            if result["success"]:
                user_data = result["data"].get("user", {})
                returned_user_id = user_data.get("id")
                username = user_data.get("username")
                
                # Check if returned user ID matches expected fixed ID
                user_id_correct = returned_user_id == EXPECTED_DEMO_USER_ID
                
                auth_results.append({
                    "email": email,
                    "login_successful": True,
                    "returned_user_id": returned_user_id,
                    "expected_user_id": EXPECTED_DEMO_USER_ID,
                    "user_id_correct": user_id_correct,
                    "username": username,
                    "response_time_ms": result["response_time_ms"]
                })
                
                print(f"    ✅ Login successful")
                print(f"    👤 User ID: {returned_user_id} ({'✅' if user_id_correct else '❌'})")
                print(f"    📧 Username: {username}")
                
            else:
                auth_results.append({
                    "email": email,
                    "login_successful": False,
                    "error": result.get("error", "Login failed"),
                    "status": result["status"],
                    "response_time_ms": result["response_time_ms"]
                })
                print(f"    ❌ Login failed: {result.get('error', 'Unknown error')}")
        
        # Calculate overall authentication success
        successful_logins = [r for r in auth_results if r.get("login_successful", False)]
        correct_user_ids = [r for r in successful_logins if r.get("user_id_correct", False)]
        
        return {
            "test_name": "Demo User Authentication",
            "total_demo_emails_tested": len(DEMO_EMAILS),
            "successful_logins": len(successful_logins),
            "correct_user_ids": len(correct_user_ids),
            "authentication_success_rate": len(successful_logins) / len(DEMO_EMAILS) * 100,
            "user_id_consistency_rate": len(correct_user_ids) / len(DEMO_EMAILS) * 100,
            "all_authentications_successful": len(successful_logins) == len(DEMO_EMAILS),
            "all_user_ids_correct": len(correct_user_ids) == len(DEMO_EMAILS),
            "expected_user_id": EXPECTED_DEMO_USER_ID,
            "detailed_auth_results": auth_results
        }
    
    async def test_management_center_listings(self) -> Dict:
        """Test Management Center Listings - /api/user/my-listings/{user_id} should return 9 demo_user listings"""
        print("📋 Testing Management Center Listings...")
        
        # Test the my-listings endpoint with the expected demo user ID
        endpoint = f"/user/my-listings/{EXPECTED_DEMO_USER_ID}"
        result = await self.make_request(endpoint)
        
        if result["success"]:
            listings = result["data"]
            listings_count = len(listings)
            
            # Check if we get the expected number of listings
            count_correct = listings_count == EXPECTED_DEMO_LISTINGS_COUNT
            
            # Verify all listings belong to the demo user
            seller_id_consistency = True
            demo_user_listings = 0
            
            for listing in listings:
                if listing.get("seller_id") == EXPECTED_DEMO_USER_ID:
                    demo_user_listings += 1
                else:
                    seller_id_consistency = False
            
            print(f"  ✅ Management center endpoint accessible")
            print(f"  📊 Found {listings_count} listings ({'✅' if count_correct else '❌'})")
            print(f"  👤 Demo user listings: {demo_user_listings}")
            print(f"  🔗 Seller ID consistency: {'✅' if seller_id_consistency else '❌'}")
            
            return {
                "test_name": "Management Center Listings",
                "endpoint_accessible": True,
                "response_time_ms": result["response_time_ms"],
                "listings_count": listings_count,
                "expected_count": EXPECTED_DEMO_LISTINGS_COUNT,
                "count_correct": count_correct,
                "demo_user_listings": demo_user_listings,
                "seller_id_consistency": seller_id_consistency,
                "management_center_working": count_correct and seller_id_consistency,
                "listings_data": listings[:3] if listings else []  # Sample of first 3 listings
            }
        else:
            print(f"  ❌ Management center endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Management Center Listings",
                "endpoint_accessible": False,
                "error": result.get("error", "Endpoint failed"),
                "status": result["status"],
                "response_time_ms": result["response_time_ms"],
                "management_center_working": False
            }
    
    async def test_browse_page_consistency(self) -> Dict:
        """Test Browse Page Consistency - /api/marketplace/browse should show demo_user listings with matching seller_id"""
        print("🔍 Testing Browse Page Consistency...")
        
        result = await self.make_request("/marketplace/browse")
        
        if result["success"]:
            all_listings = result["data"]
            
            # Find listings that belong to the demo user
            demo_user_listings = []
            for listing in all_listings:
                if listing.get("seller_id") == EXPECTED_DEMO_USER_ID:
                    demo_user_listings.append(listing)
            
            demo_listings_count = len(demo_user_listings)
            browse_consistency = demo_listings_count > 0  # Should have some demo user listings
            
            # Check if seller_id matches expected demo user ID
            seller_id_matches = all(
                listing.get("seller_id") == EXPECTED_DEMO_USER_ID 
                for listing in demo_user_listings
            )
            
            print(f"  ✅ Browse endpoint accessible")
            print(f"  📊 Total listings: {len(all_listings)}")
            print(f"  👤 Demo user listings: {demo_listings_count}")
            print(f"  🔗 Seller ID matches: {'✅' if seller_id_matches else '❌'}")
            
            return {
                "test_name": "Browse Page Consistency",
                "endpoint_accessible": True,
                "response_time_ms": result["response_time_ms"],
                "total_listings": len(all_listings),
                "demo_user_listings_count": demo_listings_count,
                "expected_demo_user_id": EXPECTED_DEMO_USER_ID,
                "seller_id_matches": seller_id_matches,
                "browse_consistency": browse_consistency,
                "demo_listings_visible": demo_listings_count > 0,
                "sample_demo_listings": demo_user_listings[:3] if demo_user_listings else []
            }
        else:
            print(f"  ❌ Browse endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Browse Page Consistency",
                "endpoint_accessible": False,
                "error": result.get("error", "Browse endpoint failed"),
                "status": result["status"],
                "response_time_ms": result["response_time_ms"],
                "browse_consistency": False
            }
    
    async def test_authentication_flow_verification(self) -> Dict:
        """Test Authentication Flow Verification - Complete flow: login → get user ID → query my-listings → verify consistency"""
        print("🔄 Testing Authentication Flow Verification...")
        
        flow_results = []
        
        # Test the complete flow with the primary demo email
        primary_email = "user@cataloro.com"
        print(f"  Testing complete flow with: {primary_email}")
        
        # Step 1: Login as demo user
        login_data = {
            "email": primary_email,
            "password": "demo_password"
        }
        
        login_result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if login_result["success"]:
            user_data = login_result["data"].get("user", {})
            authenticated_user_id = user_data.get("id")
            
            print(f"    ✅ Step 1 - Login successful")
            print(f"    👤 Authenticated User ID: {authenticated_user_id}")
            
            # Step 2: Use authenticated user ID to query my-listings
            my_listings_result = await self.make_request(f"/user/my-listings/{authenticated_user_id}")
            
            if my_listings_result["success"]:
                my_listings = my_listings_result["data"]
                my_listings_count = len(my_listings)
                
                print(f"    ✅ Step 2 - My-listings query successful")
                print(f"    📊 My listings count: {my_listings_count}")
                
                # Step 3: Verify consistency with browse page
                browse_result = await self.make_request("/marketplace/browse")
                
                if browse_result["success"]:
                    browse_listings = browse_result["data"]
                    
                    # Count demo user listings in browse page
                    browse_demo_listings = [
                        listing for listing in browse_listings 
                        if listing.get("seller_id") == authenticated_user_id
                    ]
                    browse_demo_count = len(browse_demo_listings)
                    
                    print(f"    ✅ Step 3 - Browse page query successful")
                    print(f"    📊 Browse demo listings count: {browse_demo_count}")
                    
                    # Check consistency between my-listings and browse page
                    consistency_check = my_listings_count == browse_demo_count
                    data_consistency_resolved = consistency_check and my_listings_count > 0
                    
                    print(f"    🔗 Data consistency: {'✅' if consistency_check else '❌'}")
                    print(f"    🎯 Issue resolved: {'✅' if data_consistency_resolved else '❌'}")
                    
                    flow_results.append({
                        "step": "Complete Authentication Flow",
                        "login_successful": True,
                        "authenticated_user_id": authenticated_user_id,
                        "expected_user_id": EXPECTED_DEMO_USER_ID,
                        "user_id_matches_expected": authenticated_user_id == EXPECTED_DEMO_USER_ID,
                        "my_listings_count": my_listings_count,
                        "browse_demo_listings_count": browse_demo_count,
                        "data_consistency": consistency_check,
                        "issue_resolved": data_consistency_resolved,
                        "flow_successful": True
                    })
                    
                else:
                    flow_results.append({
                        "step": "Complete Authentication Flow",
                        "error": "Browse page query failed",
                        "flow_successful": False
                    })
            else:
                flow_results.append({
                    "step": "Complete Authentication Flow", 
                    "error": "My-listings query failed",
                    "flow_successful": False
                })
        else:
            flow_results.append({
                "step": "Complete Authentication Flow",
                "error": "Login failed",
                "flow_successful": False
            })
        
        # Calculate flow success
        successful_flows = [r for r in flow_results if r.get("flow_successful", False)]
        resolved_issues = [r for r in successful_flows if r.get("issue_resolved", False)]
        
        return {
            "test_name": "Authentication Flow Verification",
            "total_flows_tested": len(flow_results),
            "successful_flows": len(successful_flows),
            "resolved_issues": len(resolved_issues),
            "flow_success_rate": len(successful_flows) / len(flow_results) * 100 if flow_results else 0,
            "issue_resolution_rate": len(resolved_issues) / len(flow_results) * 100 if flow_results else 0,
            "complete_flow_working": len(successful_flows) > 0,
            "data_inconsistency_resolved": len(resolved_issues) > 0,
            "detailed_flow_results": flow_results
        }
    
    async def test_edge_case_testing(self) -> Dict:
        """Test Edge Cases - other demo emails should return same fixed user ID, admin login should still work"""
        print("🧪 Testing Edge Cases...")
        
        edge_case_results = []
        
        # Test all demo emails return the same user ID
        print("  Testing all demo emails return same user ID...")
        user_ids_collected = []
        
        for email in DEMO_EMAILS:
            login_data = {
                "email": email,
                "password": "demo_password"
            }
            
            result = await self.make_request("/auth/login", "POST", data=login_data)
            
            if result["success"]:
                user_id = result["data"].get("user", {}).get("id")
                user_ids_collected.append(user_id)
                
                edge_case_results.append({
                    "test": f"Demo email consistency - {email}",
                    "success": True,
                    "user_id": user_id,
                    "matches_expected": user_id == EXPECTED_DEMO_USER_ID
                })
            else:
                edge_case_results.append({
                    "test": f"Demo email consistency - {email}",
                    "success": False,
                    "error": result.get("error")
                })
        
        # Check if all demo emails return the same user ID
        all_same_user_id = len(set(user_ids_collected)) <= 1 if user_ids_collected else False
        all_match_expected = all(uid == EXPECTED_DEMO_USER_ID for uid in user_ids_collected)
        
        print(f"    📊 Collected user IDs: {user_ids_collected}")
        print(f"    🔗 All same user ID: {'✅' if all_same_user_id else '❌'}")
        print(f"    🎯 All match expected: {'✅' if all_match_expected else '❌'}")
        
        # Test admin login still works correctly
        print("  Testing admin login still works...")
        admin_login_data = {
            "email": "admin@cataloro.com",
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            admin_user = admin_result["data"].get("user", {})
            admin_user_id = admin_user.get("id")
            admin_role = admin_user.get("role") or admin_user.get("user_role")
            
            # Admin should have different user ID than demo users
            admin_id_different = admin_user_id != EXPECTED_DEMO_USER_ID
            admin_role_correct = admin_role in ["admin", "Admin"]
            
            edge_case_results.append({
                "test": "Admin login functionality",
                "success": True,
                "admin_user_id": admin_user_id,
                "admin_id_different_from_demo": admin_id_different,
                "admin_role": admin_role,
                "admin_role_correct": admin_role_correct,
                "admin_login_working": admin_id_different and admin_role_correct
            })
            
            print(f"    ✅ Admin login successful")
            print(f"    👤 Admin User ID: {admin_user_id}")
            print(f"    🔑 Admin Role: {admin_role}")
            print(f"    🔗 Different from demo: {'✅' if admin_id_different else '❌'}")
            
        else:
            edge_case_results.append({
                "test": "Admin login functionality",
                "success": False,
                "error": admin_result.get("error"),
                "admin_login_working": False
            })
            print(f"    ❌ Admin login failed: {admin_result.get('error')}")
        
        # Calculate edge case success
        successful_edge_cases = [r for r in edge_case_results if r.get("success", False)]
        demo_consistency_working = all_same_user_id and all_match_expected
        admin_working = any(r.get("admin_login_working", False) for r in edge_case_results)
        
        return {
            "test_name": "Edge Case Testing",
            "total_edge_cases_tested": len(edge_case_results),
            "successful_edge_cases": len(successful_edge_cases),
            "edge_case_success_rate": len(successful_edge_cases) / len(edge_case_results) * 100 if edge_case_results else 0,
            "demo_emails_user_id_consistency": demo_consistency_working,
            "all_demo_emails_return_same_id": all_same_user_id,
            "all_demo_emails_match_expected": all_match_expected,
            "admin_login_still_working": admin_working,
            "collected_demo_user_ids": user_ids_collected,
            "expected_demo_user_id": EXPECTED_DEMO_USER_ID,
            "detailed_edge_case_results": edge_case_results
        }
    
    async def run_comprehensive_demo_user_test(self) -> Dict:
        """Run all demo user consistency tests"""
        print("🚀 Starting Demo User Data Consistency Testing")
        print("=" * 70)
        print(f"Expected Demo User ID: {EXPECTED_DEMO_USER_ID}")
        print(f"Expected Demo Listings Count: {EXPECTED_DEMO_LISTINGS_COUNT}")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test suites
            demo_auth = await self.test_demo_user_authentication()
            management_center = await self.test_management_center_listings()
            browse_consistency = await self.test_browse_page_consistency()
            auth_flow = await self.test_authentication_flow_verification()
            edge_cases = await self.test_edge_case_testing()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "expected_demo_user_id": EXPECTED_DEMO_USER_ID,
                "expected_demo_listings_count": EXPECTED_DEMO_LISTINGS_COUNT,
                "demo_user_authentication": demo_auth,
                "management_center_listings": management_center,
                "browse_page_consistency": browse_consistency,
                "authentication_flow_verification": auth_flow,
                "edge_case_testing": edge_cases
            }
            
            # Calculate overall success metrics
            test_results = [
                demo_auth.get("all_user_ids_correct", False),
                management_center.get("management_center_working", False),
                browse_consistency.get("browse_consistency", False),
                auth_flow.get("data_inconsistency_resolved", False),
                edge_cases.get("demo_emails_user_id_consistency", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            critical_issue_resolved = (
                demo_auth.get("all_user_ids_correct", False) and
                management_center.get("management_center_working", False) and
                auth_flow.get("data_inconsistency_resolved", False)
            )
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "demo_user_authentication_working": demo_auth.get("all_user_ids_correct", False),
                "management_center_listings_working": management_center.get("management_center_working", False),
                "browse_page_consistency_verified": browse_consistency.get("browse_consistency", False),
                "authentication_flow_working": auth_flow.get("complete_flow_working", False),
                "data_inconsistency_resolved": auth_flow.get("data_inconsistency_resolved", False),
                "edge_cases_working": edge_cases.get("demo_emails_user_id_consistency", False),
                "admin_login_still_working": edge_cases.get("admin_login_still_working", False),
                "critical_issue_resolved": critical_issue_resolved,
                "all_tests_passed": overall_success_rate == 100
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Main function to run the demo user consistency tests"""
    tester = DemoUserConsistencyTester()
    results = await tester.run_comprehensive_demo_user_test()
    
    print("\n" + "=" * 70)
    print("📊 DEMO USER CONSISTENCY TEST RESULTS")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"Critical Issue Resolved: {'✅' if summary.get('critical_issue_resolved', False) else '❌'}")
    print(f"Demo User Authentication: {'✅' if summary.get('demo_user_authentication_working', False) else '❌'}")
    print(f"Management Center Working: {'✅' if summary.get('management_center_listings_working', False) else '❌'}")
    print(f"Browse Page Consistency: {'✅' if summary.get('browse_page_consistency_verified', False) else '❌'}")
    print(f"Data Inconsistency Resolved: {'✅' if summary.get('data_inconsistency_resolved', False) else '❌'}")
    print(f"Edge Cases Working: {'✅' if summary.get('edge_cases_working', False) else '❌'}")
    print(f"Admin Login Still Working: {'✅' if summary.get('admin_login_still_working', False) else '❌'}")
    
    print("\n" + "=" * 70)
    print("📋 DETAILED RESULTS")
    print("=" * 70)
    print(json.dumps(results, indent=2, default=str))
    
    return results

if __name__ == "__main__":
    asyncio.run(main())