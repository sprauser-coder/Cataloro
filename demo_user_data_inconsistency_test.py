#!/usr/bin/env python3
"""
Demo User Data Inconsistency Investigation
Testing the exact data inconsistency issue reported by user about demo_user listings
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://market-guardian.preview.emergentagent.com/api"

# Demo User IDs to test (from review request)
DEMO_USER_ID_1 = "2ae84d11-f762-4462-9467-d283fd719d21"
DEMO_USER_ID_2 = "demo_user_1"

class DemoUserDataInconsistencyTester:
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
    
    async def test_browse_page_data_analysis(self) -> Dict:
        """Test /api/marketplace/browse endpoint and analyze seller information"""
        print("🔍 Testing Browse Page Data Analysis...")
        
        result = await self.make_request("/marketplace/browse")
        
        if not result["success"]:
            return {
                "test_name": "Browse Page Data Analysis",
                "success": False,
                "error": result.get("error", "Browse endpoint failed"),
                "status": result["status"]
            }
        
        listings = result["data"]
        demo_user_listings = []
        all_seller_info = []
        
        print(f"  📋 Found {len(listings)} total listings on browse page")
        
        # Analyze each listing for seller information
        for listing in listings:
            seller_info = {
                "listing_id": listing.get("id", "unknown"),
                "listing_title": listing.get("title", "unknown"),
                "seller_id": listing.get("seller_id", "unknown"),
                "seller": listing.get("seller", {}),
                "seller_name": listing.get("seller", {}).get("name", "unknown"),
                "seller_username": listing.get("seller", {}).get("username", "unknown")
            }
            all_seller_info.append(seller_info)
            
            # Check if this listing belongs to demo_user
            seller_id = listing.get("seller_id", "")
            seller_name = listing.get("seller", {}).get("name", "")
            seller_username = listing.get("seller", {}).get("username", "")
            
            # Check for demo_user matches
            is_demo_user = (
                seller_id in [DEMO_USER_ID_1, DEMO_USER_ID_2] or
                seller_name.lower() == "demo user" or
                seller_username.lower() in ["demo_user", "demo user"]
            )
            
            if is_demo_user:
                demo_user_listings.append({
                    "listing_id": listing.get("id"),
                    "title": listing.get("title"),
                    "seller_id": seller_id,
                    "seller_name": seller_name,
                    "seller_username": seller_username,
                    "price": listing.get("price"),
                    "match_reason": self._get_demo_user_match_reason(seller_id, seller_name, seller_username)
                })
        
        print(f"  👤 Found {len(demo_user_listings)} listings belonging to demo_user on browse page")
        
        for listing in demo_user_listings:
            print(f"    - {listing['title']} (ID: {listing['listing_id']})")
            print(f"      Seller ID: {listing['seller_id']}")
            print(f"      Seller Name: {listing['seller_name']}")
            print(f"      Seller Username: {listing['seller_username']}")
            print(f"      Match Reason: {listing['match_reason']}")
        
        return {
            "test_name": "Browse Page Data Analysis",
            "success": True,
            "response_time_ms": result["response_time_ms"],
            "total_listings": len(listings),
            "demo_user_listings_count": len(demo_user_listings),
            "demo_user_listings": demo_user_listings,
            "all_seller_info": all_seller_info[:10]  # First 10 for analysis
        }
    
    async def test_management_center_data_analysis(self) -> Dict:
        """Test user's own listings endpoints with both demo_user IDs"""
        print("🏢 Testing Management Center Data Analysis...")
        
        results = {}
        
        # Test with both demo_user IDs
        for user_id in [DEMO_USER_ID_1, DEMO_USER_ID_2]:
            print(f"  Testing with user ID: {user_id}")
            
            result = await self.make_request(f"/user/my-listings/{user_id}")
            
            if result["success"]:
                listings = result["data"]
                print(f"    ✅ Found {len(listings)} listings for user {user_id}")
                
                results[user_id] = {
                    "success": True,
                    "response_time_ms": result["response_time_ms"],
                    "listings_count": len(listings),
                    "listings": listings
                }
                
                # Show details of found listings
                for listing in listings:
                    print(f"      - {listing.get('title', 'Unknown')} (ID: {listing.get('id', 'Unknown')})")
                    print(f"        Seller ID: {listing.get('seller_id', 'Unknown')}")
                    print(f"        Price: {listing.get('price', 'Unknown')}")
            else:
                print(f"    ❌ Failed to get listings for user {user_id}: {result.get('error', 'Unknown error')}")
                results[user_id] = {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "status": result["status"],
                    "response_time_ms": result["response_time_ms"]
                }
        
        return {
            "test_name": "Management Center Data Analysis",
            "results_by_user_id": results
        }
    
    async def test_database_user_identity_verification(self) -> Dict:
        """Check all user accounts in the system to identify demo_user accounts"""
        print("🗄️ Testing Database User Identity Verification...")
        
        # Try to login with demo user credentials to get user data
        demo_login_attempts = [
            {"email": "demo@cataloro.com", "expected_username": "demo_user"},
            {"email": "demo_user@cataloro.com", "expected_username": "demo_user"},
            {"email": "test@cataloro.com", "expected_username": "demo_user"}
        ]
        
        user_accounts = []
        
        for login_attempt in demo_login_attempts:
            print(f"  Attempting login with: {login_attempt['email']}")
            
            login_data = {
                "email": login_attempt["email"],
                "password": "demo_password"
            }
            
            result = await self.make_request("/auth/login", "POST", data=login_data)
            
            if result["success"]:
                user_data = result["data"].get("user", {})
                user_id = user_data.get("id", "unknown")
                username = user_data.get("username", "unknown")
                email = user_data.get("email", "unknown")
                
                print(f"    ✅ Login successful")
                print(f"      User ID: {user_id}")
                print(f"      Username: {username}")
                print(f"      Email: {email}")
                
                user_accounts.append({
                    "login_email": login_attempt["email"],
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "is_demo_user": username.lower() in ["demo_user", "demo user"] or "demo" in username.lower(),
                    "matches_expected_ids": user_id in [DEMO_USER_ID_1, DEMO_USER_ID_2]
                })
            else:
                print(f"    ❌ Login failed: {result.get('error', 'Unknown error')}")
        
        # Check which user IDs correspond to "demo_user"
        demo_user_accounts = [acc for acc in user_accounts if acc["is_demo_user"]]
        
        return {
            "test_name": "Database User Identity Verification",
            "total_login_attempts": len(demo_login_attempts),
            "successful_logins": len(user_accounts),
            "demo_user_accounts_found": len(demo_user_accounts),
            "user_accounts": user_accounts,
            "demo_user_accounts": demo_user_accounts
        }
    
    async def test_listing_ownership_analysis(self) -> Dict:
        """Analyze listing ownership for any listings that appear to belong to demo_user"""
        print("📊 Testing Listing Ownership Analysis...")
        
        # First get browse data to find demo_user listings
        browse_result = await self.test_browse_page_data_analysis()
        
        if not browse_result["success"]:
            return {
                "test_name": "Listing Ownership Analysis",
                "success": False,
                "error": "Could not get browse data for analysis"
            }
        
        demo_listings = browse_result["demo_user_listings"]
        ownership_analysis = []
        
        print(f"  Analyzing {len(demo_listings)} demo_user listings from browse page...")
        
        for listing in demo_listings:
            listing_id = listing["listing_id"]
            seller_id = listing["seller_id"]
            
            print(f"  Analyzing listing: {listing['title']} (ID: {listing_id})")
            print(f"    Seller ID from browse: {seller_id}")
            
            # Get detailed listing information
            detail_result = await self.make_request(f"/listings/{listing_id}")
            
            analysis = {
                "listing_id": listing_id,
                "title": listing["title"],
                "seller_id_from_browse": seller_id,
                "seller_name_from_browse": listing["seller_name"],
                "seller_username_from_browse": listing["seller_username"]
            }
            
            if detail_result["success"]:
                detail_data = detail_result["data"]
                analysis.update({
                    "seller_id_from_detail": detail_data.get("seller_id", "unknown"),
                    "detail_endpoint_working": True,
                    "seller_id_consistent": seller_id == detail_data.get("seller_id", "unknown")
                })
                
                print(f"    Seller ID from detail: {detail_data.get('seller_id', 'unknown')}")
                print(f"    IDs consistent: {analysis['seller_id_consistent']}")
            else:
                analysis.update({
                    "detail_endpoint_working": False,
                    "detail_error": detail_result.get("error", "Unknown error")
                })
                print(f"    ❌ Could not get listing details: {detail_result.get('error')}")
            
            # Check if this seller_id matches expected demo_user IDs
            analysis["matches_demo_user_id_1"] = seller_id == DEMO_USER_ID_1
            analysis["matches_demo_user_id_2"] = seller_id == DEMO_USER_ID_2
            analysis["matches_any_expected_demo_id"] = seller_id in [DEMO_USER_ID_1, DEMO_USER_ID_2]
            
            ownership_analysis.append(analysis)
        
        return {
            "test_name": "Listing Ownership Analysis",
            "success": True,
            "demo_listings_analyzed": len(demo_listings),
            "ownership_analysis": ownership_analysis
        }
    
    async def test_authentication_state_check(self) -> Dict:
        """Verify which user ID is actually being used when demo_user logs in"""
        print("🔐 Testing Authentication State Check...")
        
        # Try different demo user login scenarios
        login_scenarios = [
            {"email": "demo@cataloro.com", "password": "demo_password", "scenario": "Standard demo login"},
            {"email": "demo_user@cataloro.com", "password": "demo_password", "scenario": "Alternative demo email"},
            {"email": "test@cataloro.com", "password": "test_password", "scenario": "Test user login"}
        ]
        
        authentication_results = []
        
        for scenario in login_scenarios:
            print(f"  Testing scenario: {scenario['scenario']}")
            
            login_data = {
                "email": scenario["email"],
                "password": scenario["password"]
            }
            
            result = await self.make_request("/auth/login", "POST", data=login_data)
            
            if result["success"]:
                user_data = result["data"].get("user", {})
                user_id = user_data.get("id")
                
                print(f"    ✅ Login successful")
                print(f"      User ID: {user_id}")
                print(f"      Username: {user_data.get('username')}")
                
                # Test management center with this user ID
                mgmt_result = await self.make_request(f"/user/my-listings/{user_id}")
                
                auth_result = {
                    "scenario": scenario["scenario"],
                    "login_successful": True,
                    "user_id": user_id,
                    "username": user_data.get("username"),
                    "email": user_data.get("email"),
                    "matches_demo_id_1": user_id == DEMO_USER_ID_1,
                    "matches_demo_id_2": user_id == DEMO_USER_ID_2,
                    "management_center_accessible": mgmt_result["success"],
                    "management_center_listings_count": len(mgmt_result["data"]) if mgmt_result["success"] else 0
                }
                
                if mgmt_result["success"]:
                    print(f"      Management center: {len(mgmt_result['data'])} listings")
                else:
                    print(f"      Management center failed: {mgmt_result.get('error')}")
                    auth_result["management_center_error"] = mgmt_result.get("error")
                
            else:
                print(f"    ❌ Login failed: {result.get('error')}")
                auth_result = {
                    "scenario": scenario["scenario"],
                    "login_successful": False,
                    "error": result.get("error"),
                    "status": result["status"]
                }
            
            authentication_results.append(auth_result)
        
        return {
            "test_name": "Authentication State Check",
            "scenarios_tested": len(login_scenarios),
            "successful_logins": len([r for r in authentication_results if r.get("login_successful", False)]),
            "authentication_results": authentication_results
        }
    
    def _get_demo_user_match_reason(self, seller_id: str, seller_name: str, seller_username: str) -> str:
        """Get the reason why this listing was identified as belonging to demo_user"""
        reasons = []
        
        if seller_id == DEMO_USER_ID_1:
            reasons.append(f"Seller ID matches demo_user_id_1 ({DEMO_USER_ID_1})")
        if seller_id == DEMO_USER_ID_2:
            reasons.append(f"Seller ID matches demo_user_id_2 ({DEMO_USER_ID_2})")
        if seller_name.lower() == "demo user":
            reasons.append(f"Seller name is 'Demo User'")
        if seller_username.lower() in ["demo_user", "demo user"]:
            reasons.append(f"Seller username is '{seller_username}'")
        
        return "; ".join(reasons) if reasons else "Unknown match"
    
    async def run_comprehensive_investigation(self) -> Dict:
        """Run comprehensive investigation of demo_user data inconsistency"""
        print("🔍 Starting Demo User Data Inconsistency Investigation")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all investigation tests
            browse_analysis = await self.test_browse_page_data_analysis()
            management_analysis = await self.test_management_center_data_analysis()
            user_identity = await self.test_database_user_identity_verification()
            ownership_analysis = await self.test_listing_ownership_analysis()
            auth_state = await self.test_authentication_state_check()
            
            # Compile comprehensive results
            investigation_results = {
                "investigation_timestamp": datetime.now().isoformat(),
                "demo_user_ids_tested": [DEMO_USER_ID_1, DEMO_USER_ID_2],
                "browse_page_analysis": browse_analysis,
                "management_center_analysis": management_analysis,
                "user_identity_verification": user_identity,
                "listing_ownership_analysis": ownership_analysis,
                "authentication_state_check": auth_state
            }
            
            # Analyze the inconsistency
            browse_demo_listings = browse_analysis.get("demo_user_listings_count", 0)
            
            # Check management center results for both user IDs
            mgmt_results = management_analysis.get("results_by_user_id", {})
            mgmt_listings_id1 = mgmt_results.get(DEMO_USER_ID_1, {}).get("listings_count", 0)
            mgmt_listings_id2 = mgmt_results.get(DEMO_USER_ID_2, {}).get("listings_count", 0)
            
            # Identify the inconsistency
            inconsistency_detected = browse_demo_listings > 0 and (mgmt_listings_id1 == 0 and mgmt_listings_id2 == 0)
            
            investigation_results["inconsistency_analysis"] = {
                "inconsistency_detected": inconsistency_detected,
                "browse_page_demo_listings": browse_demo_listings,
                "management_center_listings_id1": mgmt_listings_id1,
                "management_center_listings_id2": mgmt_listings_id2,
                "potential_causes": self._analyze_potential_causes(investigation_results)
            }
            
            return investigation_results
            
        finally:
            await self.cleanup()
    
    def _analyze_potential_causes(self, results: Dict) -> List[str]:
        """Analyze potential causes of the inconsistency"""
        causes = []
        
        browse_data = results.get("browse_page_analysis", {})
        mgmt_data = results.get("management_center_analysis", {})
        user_data = results.get("user_identity_verification", {})
        auth_data = results.get("authentication_state_check", {})
        
        # Check for different user IDs being used
        demo_listings = browse_data.get("demo_user_listings", [])
        if demo_listings:
            seller_ids_in_browse = set(listing["seller_id"] for listing in demo_listings)
            tested_user_ids = set([DEMO_USER_ID_1, DEMO_USER_ID_2])
            
            if not seller_ids_in_browse.intersection(tested_user_ids):
                causes.append("Browse page shows demo_user listings with different seller_id than expected demo_user IDs")
        
        # Check for user ID format inconsistencies
        auth_results = auth_data.get("authentication_results", [])
        successful_logins = [r for r in auth_results if r.get("login_successful", False)]
        
        if successful_logins:
            actual_user_ids = [r["user_id"] for r in successful_logins]
            if not any(uid in [DEMO_USER_ID_1, DEMO_USER_ID_2] for uid in actual_user_ids):
                causes.append("Authenticated demo_user has different user_id than expected")
        
        # Check for endpoint query logic differences
        mgmt_results = mgmt_data.get("results_by_user_id", {})
        if all(not result.get("success", False) for result in mgmt_results.values()):
            causes.append("Management center endpoints may have different query logic or user_id format requirements")
        
        # Check for multiple demo_user accounts
        user_accounts = user_data.get("demo_user_accounts", [])
        if len(user_accounts) > 1:
            causes.append("Multiple demo_user accounts exist with different user_ids")
        
        if not causes:
            causes.append("No clear inconsistency pattern identified - may require deeper database investigation")
        
        return causes

async def main():
    """Run the demo user data inconsistency investigation"""
    tester = DemoUserDataInconsistencyTester()
    results = await tester.run_comprehensive_investigation()
    
    print("\n" + "=" * 70)
    print("🔍 DEMO USER DATA INCONSISTENCY INVESTIGATION RESULTS")
    print("=" * 70)
    
    # Print summary
    inconsistency = results.get("inconsistency_analysis", {})
    print(f"\n📊 INCONSISTENCY DETECTED: {inconsistency.get('inconsistency_detected', False)}")
    print(f"📋 Browse page demo_user listings: {inconsistency.get('browse_page_demo_listings', 0)}")
    print(f"🏢 Management center listings (ID1): {inconsistency.get('management_center_listings_id1', 0)}")
    print(f"🏢 Management center listings (ID2): {inconsistency.get('management_center_listings_id2', 0)}")
    
    print(f"\n🔍 POTENTIAL CAUSES:")
    for cause in inconsistency.get("potential_causes", []):
        print(f"  - {cause}")
    
    # Print detailed findings
    browse_data = results.get("browse_page_analysis", {})
    if browse_data.get("success") and browse_data.get("demo_user_listings"):
        print(f"\n📋 DEMO USER LISTINGS FOUND ON BROWSE PAGE:")
        for listing in browse_data["demo_user_listings"]:
            print(f"  - {listing['title']}")
            print(f"    Listing ID: {listing['listing_id']}")
            print(f"    Seller ID: {listing['seller_id']}")
            print(f"    Seller Name: {listing['seller_name']}")
            print(f"    Seller Username: {listing['seller_username']}")
            print(f"    Match Reason: {listing['match_reason']}")
    
    # Print authentication findings
    auth_data = results.get("authentication_state_check", {})
    successful_auths = [r for r in auth_data.get("authentication_results", []) if r.get("login_successful", False)]
    if successful_auths:
        print(f"\n🔐 SUCCESSFUL DEMO USER AUTHENTICATIONS:")
        for auth in successful_auths:
            print(f"  - {auth['scenario']}")
            print(f"    User ID: {auth['user_id']}")
            print(f"    Username: {auth['username']}")
            print(f"    Management Center Listings: {auth['management_center_listings_count']}")
    
    # Save detailed results to file
    with open("/app/demo_user_investigation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: /app/demo_user_investigation_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())