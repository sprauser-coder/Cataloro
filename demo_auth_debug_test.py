#!/usr/bin/env python3
"""
Demo User Authentication Debug Test
Testing the specific issue with demo user authentication and management center listings
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://marketplace-debug-3.preview.emergentagent.com/api"

# Demo user credentials from the review request
DEMO_EMAIL = "user@cataloro.com"
DEMO_PASSWORD = "demo123"
EXPECTED_FIXED_ID = "68bfff790e4e46bc28d43631"

class DemoAuthDebugTester:
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
    
    async def test_demo_user_login(self) -> Dict:
        """Test login with demo user credentials and check user ID returned"""
        print("🔐 Testing demo user login...")
        
        login_data = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            token = result["data"].get("token", "")
            actual_user_id = user_data.get("id")
            
            print(f"  ✅ Login successful")
            print(f"  📧 Email: {user_data.get('email')}")
            print(f"  👤 Username: {user_data.get('username')}")
            print(f"  🆔 Actual User ID: {actual_user_id}")
            print(f"  🎯 Expected Fixed ID: {EXPECTED_FIXED_ID}")
            print(f"  ✅ ID Match: {'YES' if actual_user_id == EXPECTED_FIXED_ID else 'NO'}")
            
            return {
                "test_name": "Demo User Login",
                "login_successful": True,
                "response_time_ms": result["response_time_ms"],
                "actual_user_id": actual_user_id,
                "expected_user_id": EXPECTED_FIXED_ID,
                "user_id_matches_expected": actual_user_id == EXPECTED_FIXED_ID,
                "user_data": user_data,
                "token": token
            }
        else:
            print(f"  ❌ Login failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Demo User Login",
                "login_successful": False,
                "response_time_ms": result["response_time_ms"],
                "error": result.get("error", "Login failed"),
                "status": result["status"]
            }
    
    async def test_database_user_state(self) -> Dict:
        """Check what users exist in the database with demo-related emails"""
        print("🗄️ Testing database user state...")
        
        # Test different demo email variations
        demo_emails = [
            "user@cataloro.com",
            "demo@cataloro.com", 
            "demo_user@cataloro.com"
        ]
        
        user_states = []
        
        for email in demo_emails:
            print(f"  Testing email: {email}")
            
            login_data = {
                "email": email,
                "password": DEMO_PASSWORD
            }
            
            result = await self.make_request("/auth/login", "POST", data=login_data)
            
            if result["success"]:
                user_data = result["data"].get("user", {})
                user_id = user_data.get("id")
                
                user_states.append({
                    "email": email,
                    "exists": True,
                    "user_id": user_id,
                    "matches_fixed_id": user_id == EXPECTED_FIXED_ID,
                    "username": user_data.get("username"),
                    "full_name": user_data.get("full_name"),
                    "user_role": user_data.get("user_role"),
                    "badge": user_data.get("badge")
                })
                
                print(f"    ✅ User exists - ID: {user_id} ({'MATCHES' if user_id == EXPECTED_FIXED_ID else 'DIFFERENT'})")
            else:
                user_states.append({
                    "email": email,
                    "exists": False,
                    "error": result.get("error", "User not found")
                })
                print(f"    ❌ User not found or login failed")
        
        # Check if any user has the expected fixed ID
        users_with_fixed_id = [u for u in user_states if u.get("matches_fixed_id", False)]
        
        return {
            "test_name": "Database User State",
            "demo_emails_tested": demo_emails,
            "user_states": user_states,
            "users_with_fixed_id": len(users_with_fixed_id),
            "fixed_id_found": len(users_with_fixed_id) > 0,
            "conflicting_users": len([u for u in user_states if u.get("exists", False)]) > 1
        }
    
    async def test_my_listings_endpoint(self, user_id: str) -> Dict:
        """Test the my-listings endpoint with a specific user ID"""
        print(f"📋 Testing my-listings endpoint with user ID: {user_id}")
        
        result = await self.make_request(f"/user/my-listings/{user_id}")
        
        if result["success"]:
            listings = result["data"]
            print(f"  ✅ Endpoint successful - Found {len(listings)} listings")
            
            # Check if any listings have seller_id matching the expected fixed ID
            matching_listings = [l for l in listings if l.get("seller_id") == EXPECTED_FIXED_ID]
            
            return {
                "test_name": f"My Listings - {user_id}",
                "endpoint_successful": True,
                "response_time_ms": result["response_time_ms"],
                "total_listings": len(listings),
                "listings_with_expected_seller_id": len(matching_listings),
                "user_id_tested": user_id,
                "listings_data": listings[:3] if listings else []  # First 3 for debugging
            }
        else:
            print(f"  ❌ Endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": f"My Listings - {user_id}",
                "endpoint_successful": False,
                "response_time_ms": result["response_time_ms"],
                "error": result.get("error", "Endpoint failed"),
                "status": result["status"],
                "user_id_tested": user_id
            }
    
    async def test_listings_verification(self) -> Dict:
        """Verify the 9 demo_user listings still exist with seller_id matching expected fixed ID"""
        print("📦 Testing listings verification...")
        
        # Get all listings to check for demo user listings
        result = await self.make_request("/marketplace/browse")
        
        if result["success"]:
            all_listings = result["data"]
            
            # Filter listings with the expected seller_id
            demo_listings = [l for l in all_listings if l.get("seller_id") == EXPECTED_FIXED_ID]
            
            # Check if listings are active
            active_demo_listings = [l for l in demo_listings if l.get("status") == "active"]
            
            print(f"  ✅ Browse endpoint successful - Found {len(all_listings)} total listings")
            print(f"  📋 Listings with expected seller_id ({EXPECTED_FIXED_ID}): {len(demo_listings)}")
            print(f"  ✅ Active listings with expected seller_id: {len(active_demo_listings)}")
            
            # Show some details of demo listings
            for i, listing in enumerate(demo_listings[:3]):
                print(f"    Listing {i+1}: {listing.get('title', 'No title')} - Status: {listing.get('status', 'Unknown')}")
            
            return {
                "test_name": "Listings Verification",
                "browse_successful": True,
                "response_time_ms": result["response_time_ms"],
                "total_listings": len(all_listings),
                "demo_user_listings": len(demo_listings),
                "active_demo_listings": len(active_demo_listings),
                "expected_demo_listings": 9,
                "demo_listings_found": len(demo_listings) > 0,
                "expected_count_matches": len(demo_listings) == 9,
                "sample_demo_listings": demo_listings[:3]
            }
        else:
            print(f"  ❌ Browse endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Listings Verification",
                "browse_successful": False,
                "response_time_ms": result["response_time_ms"],
                "error": result.get("error", "Browse failed"),
                "status": result["status"]
            }
    
    async def test_authentication_flow_debug(self) -> Dict:
        """Step through the complete authentication flow and identify disconnects"""
        print("🔍 Testing complete authentication flow...")
        
        # Step 1: Login and get user ID
        login_result = await self.test_demo_user_login()
        
        if not login_result.get("login_successful", False):
            return {
                "test_name": "Authentication Flow Debug",
                "flow_successful": False,
                "error": "Login failed",
                "login_result": login_result
            }
        
        actual_user_id = login_result.get("actual_user_id")
        
        # Step 2: Test my-listings with actual user ID
        actual_listings_result = await self.test_my_listings_endpoint(actual_user_id)
        
        # Step 3: Test my-listings with expected fixed ID (if different)
        expected_listings_result = None
        if actual_user_id != EXPECTED_FIXED_ID:
            expected_listings_result = await self.test_my_listings_endpoint(EXPECTED_FIXED_ID)
        
        # Step 4: Compare results
        actual_listings_count = actual_listings_result.get("total_listings", 0)
        expected_listings_count = expected_listings_result.get("total_listings", 0) if expected_listings_result else 0
        
        print(f"  🔍 Flow Analysis:")
        print(f"    Login User ID: {actual_user_id}")
        print(f"    Expected Fixed ID: {EXPECTED_FIXED_ID}")
        print(f"    Listings with actual ID: {actual_listings_count}")
        print(f"    Listings with expected ID: {expected_listings_count}")
        
        # Identify the disconnect
        disconnect_identified = False
        disconnect_reason = ""
        
        if actual_user_id != EXPECTED_FIXED_ID:
            disconnect_identified = True
            disconnect_reason = f"User ID mismatch: login returns {actual_user_id} but listings expect {EXPECTED_FIXED_ID}"
        elif actual_listings_count == 0 and expected_listings_count > 0:
            disconnect_identified = True
            disconnect_reason = "User ID matches but my-listings endpoint returns no results"
        elif actual_listings_count == 0:
            disconnect_identified = True
            disconnect_reason = "No listings found for either user ID - possible data issue"
        
        return {
            "test_name": "Authentication Flow Debug",
            "flow_successful": actual_listings_count > 0,
            "login_user_id": actual_user_id,
            "expected_fixed_id": EXPECTED_FIXED_ID,
            "user_id_matches": actual_user_id == EXPECTED_FIXED_ID,
            "actual_listings_count": actual_listings_count,
            "expected_listings_count": expected_listings_count,
            "disconnect_identified": disconnect_identified,
            "disconnect_reason": disconnect_reason,
            "login_result": login_result,
            "actual_listings_result": actual_listings_result,
            "expected_listings_result": expected_listings_result
        }
    
    async def run_comprehensive_debug_test(self) -> Dict:
        """Run all debug tests for demo user authentication issue"""
        print("🚀 Starting Demo User Authentication Debug Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all debug tests
            login_test = await self.test_demo_user_login()
            database_state = await self.test_database_user_state()
            listings_verification = await self.test_listings_verification()
            flow_debug = await self.test_authentication_flow_debug()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "demo_credentials": {
                    "email": DEMO_EMAIL,
                    "password": DEMO_PASSWORD,
                    "expected_fixed_id": EXPECTED_FIXED_ID
                },
                "login_test": login_test,
                "database_state": database_state,
                "listings_verification": listings_verification,
                "authentication_flow_debug": flow_debug
            }
            
            # Generate summary and recommendations
            summary = self.generate_debug_summary(all_results)
            all_results["debug_summary"] = summary
            
            return all_results
            
        finally:
            await self.cleanup()
    
    def generate_debug_summary(self, results: Dict) -> Dict:
        """Generate a summary of debug findings and recommendations"""
        login_test = results.get("login_test", {})
        database_state = results.get("database_state", {})
        listings_verification = results.get("listings_verification", {})
        flow_debug = results.get("authentication_flow_debug", {})
        
        # Key findings
        login_successful = login_test.get("login_successful", False)
        user_id_matches = login_test.get("user_id_matches_expected", False)
        actual_user_id = login_test.get("actual_user_id", "Unknown")
        
        fixed_id_found = database_state.get("fixed_id_found", False)
        conflicting_users = database_state.get("conflicting_users", False)
        
        demo_listings_found = listings_verification.get("demo_listings_found", False)
        demo_listings_count = listings_verification.get("demo_user_listings", 0)
        
        disconnect_identified = flow_debug.get("disconnect_identified", False)
        disconnect_reason = flow_debug.get("disconnect_reason", "")
        
        # Generate recommendations
        recommendations = []
        
        if not login_successful:
            recommendations.append("CRITICAL: Demo user login is failing - check user creation logic")
        elif not user_id_matches:
            recommendations.append(f"CRITICAL: User ID mismatch - login returns {actual_user_id} but expected {EXPECTED_FIXED_ID}")
            recommendations.append("Check the fixed ID assignment logic in the login endpoint")
        
        if not fixed_id_found:
            recommendations.append(f"WARNING: No user found with expected fixed ID {EXPECTED_FIXED_ID}")
            recommendations.append("Verify the demo user creation/update logic")
        
        if conflicting_users:
            recommendations.append("WARNING: Multiple demo users found - may cause ID conflicts")
            recommendations.append("Consider consolidating demo users to single fixed ID")
        
        if not demo_listings_found:
            recommendations.append("CRITICAL: No listings found with expected seller_id")
            recommendations.append("Check if demo listings exist and have correct seller_id")
        elif demo_listings_count != 9:
            recommendations.append(f"WARNING: Expected 9 demo listings but found {demo_listings_count}")
        
        if disconnect_identified:
            recommendations.append(f"ROOT CAUSE IDENTIFIED: {disconnect_reason}")
        
        # Overall status
        if login_successful and user_id_matches and demo_listings_found and demo_listings_count > 0:
            overall_status = "WORKING"
            issue_severity = "NONE"
        elif disconnect_identified:
            overall_status = "ISSUE_IDENTIFIED"
            issue_severity = "HIGH"
        else:
            overall_status = "NEEDS_INVESTIGATION"
            issue_severity = "MEDIUM"
        
        return {
            "overall_status": overall_status,
            "issue_severity": issue_severity,
            "key_findings": {
                "login_successful": login_successful,
                "user_id_matches_expected": user_id_matches,
                "actual_user_id": actual_user_id,
                "expected_user_id": EXPECTED_FIXED_ID,
                "demo_listings_found": demo_listings_found,
                "demo_listings_count": demo_listings_count,
                "disconnect_identified": disconnect_identified,
                "disconnect_reason": disconnect_reason
            },
            "recommendations": recommendations,
            "next_steps": [
                "Review the login endpoint logic for demo user ID assignment",
                "Verify demo listings exist with correct seller_id",
                "Test the my-listings endpoint with both user IDs",
                "Check for database consistency issues"
            ]
        }

async def main():
    """Run the demo authentication debug test"""
    tester = DemoAuthDebugTester()
    results = await tester.run_comprehensive_debug_test()
    
    print("\n" + "=" * 70)
    print("🎯 DEMO USER AUTHENTICATION DEBUG RESULTS")
    print("=" * 70)
    
    # Print summary
    summary = results.get("debug_summary", {})
    print(f"Overall Status: {summary.get('overall_status', 'UNKNOWN')}")
    print(f"Issue Severity: {summary.get('issue_severity', 'UNKNOWN')}")
    
    # Print key findings
    findings = summary.get("key_findings", {})
    print(f"\nKey Findings:")
    print(f"  Login Successful: {findings.get('login_successful', False)}")
    print(f"  User ID Matches Expected: {findings.get('user_id_matches_expected', False)}")
    print(f"  Actual User ID: {findings.get('actual_user_id', 'Unknown')}")
    print(f"  Expected User ID: {findings.get('expected_user_id', 'Unknown')}")
    print(f"  Demo Listings Found: {findings.get('demo_listings_found', False)}")
    print(f"  Demo Listings Count: {findings.get('demo_listings_count', 0)}")
    
    # Print disconnect analysis
    if findings.get('disconnect_identified', False):
        print(f"\n🔍 ROOT CAUSE IDENTIFIED:")
        print(f"  {findings.get('disconnect_reason', 'Unknown')}")
    
    # Print recommendations
    recommendations = summary.get("recommendations", [])
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # Print detailed results as JSON for further analysis
    print(f"\n📊 DETAILED RESULTS:")
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())