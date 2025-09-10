#!/usr/bin/env python3
"""
Seller ID Resolution Fix Testing
Testing the fix for admin listings visibility in my-listings endpoint
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-repair.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_ID = "admin_user_1"
LEGACY_ADMIN_ID = "68bff934bdb9d78bad2b925c"

# Demo User Configuration
DEMO_USER_ID = "68bfff790e4e46bc28d43631"
DEMO_EMAIL = "demo@cataloro.com"

# Target listing that should now appear in admin my-listings
TARGET_LISTING_NAME = "walker351631A"
TARGET_LISTING_ID = "1628284f-8d0f-4c18-b776-11d2b9fd11a4"

class SellerIdResolutionTester:
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
    
    async def authenticate_admin(self) -> Dict:
        """Authenticate admin user"""
        print("🔐 Authenticating admin user...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            self.admin_token = result["data"].get("token", "")
            
            print(f"  ✅ Admin authenticated: {user_data.get('username')} (ID: {user_data.get('id')})")
            return {
                "success": True,
                "user_id": user_data.get('id'),
                "username": user_data.get('username'),
                "token": self.admin_token
            }
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error')}")
            return {"success": False, "error": result.get("error")}
    
    async def authenticate_demo_user(self) -> Dict:
        """Authenticate demo user"""
        print("🔐 Authenticating demo user...")
        
        login_data = {
            "email": DEMO_EMAIL,
            "password": "demo_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            self.demo_token = result["data"].get("token", "")
            
            print(f"  ✅ Demo user authenticated: {user_data.get('username')} (ID: {user_data.get('id')})")
            return {
                "success": True,
                "user_id": user_data.get('id'),
                "username": user_data.get('username'),
                "token": self.demo_token
            }
        else:
            print(f"  ❌ Demo user authentication failed: {result.get('error')}")
            return {"success": False, "error": result.get("error")}
    
    async def test_admin_my_listings_after_fix(self) -> Dict:
        """Test GET /api/user/my-listings/admin_user_1 to verify walker351631A now appears"""
        print("📋 Testing admin my-listings after seller_id resolution fix...")
        
        if not self.admin_token:
            return {"success": False, "error": "Admin not authenticated"}
        
        # Test admin my-listings endpoint
        result = await self.make_request(f"/user/my-listings/{ADMIN_ID}")
        
        if result["success"]:
            listings = result["data"]
            
            # Look for the target listing
            target_listing = None
            for listing in listings:
                if (listing.get("title") == TARGET_LISTING_NAME or 
                    listing.get("id") == TARGET_LISTING_ID):
                    target_listing = listing
                    break
            
            walker_found = target_listing is not None
            total_listings = len(listings)
            
            print(f"  📊 Admin has {total_listings} listings in my-listings")
            print(f"  🎯 Target listing '{TARGET_LISTING_NAME}' found: {'✅' if walker_found else '❌'}")
            
            if walker_found:
                print(f"    - Listing ID: {target_listing.get('id')}")
                print(f"    - Seller ID: {target_listing.get('seller_id')}")
                print(f"    - Title: {target_listing.get('title')}")
                print(f"    - Price: €{target_listing.get('price', 0)}")
            
            return {
                "test_name": "Admin My-Listings After Fix",
                "success": True,
                "total_listings": total_listings,
                "walker351631A_found": walker_found,
                "target_listing_details": target_listing,
                "expected_count": 4,  # Should be 4 listings now instead of 3
                "count_matches_expectation": total_listings == 4,
                "fix_successful": walker_found and total_listings == 4,
                "response_time_ms": result["response_time_ms"]
            }
        else:
            print(f"  ❌ Failed to get admin my-listings: {result.get('error')}")
            return {
                "test_name": "Admin My-Listings After Fix",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def test_browse_listings_consistency(self) -> Dict:
        """Test that walker351631A appears in browse listings"""
        print("🔍 Testing browse listings for walker351631A...")
        
        result = await self.make_request("/marketplace/browse")
        
        if result["success"]:
            listings = result["data"]
            
            # Look for the target listing
            target_listing = None
            admin_listings = []
            
            for listing in listings:
                # Check if this is the target listing
                if (listing.get("title") == TARGET_LISTING_NAME or 
                    listing.get("id") == TARGET_LISTING_ID):
                    target_listing = listing
                
                # Check if this is an admin listing (by seller_id)
                seller_id = listing.get("seller_id")
                if seller_id in [ADMIN_ID, LEGACY_ADMIN_ID]:
                    admin_listings.append(listing)
            
            walker_in_browse = target_listing is not None
            admin_listings_count = len(admin_listings)
            
            print(f"  📊 Total listings in browse: {len(listings)}")
            print(f"  🎯 Target listing '{TARGET_LISTING_NAME}' in browse: {'✅' if walker_in_browse else '❌'}")
            print(f"  👤 Admin listings in browse: {admin_listings_count}")
            
            if walker_in_browse:
                print(f"    - Listing ID: {target_listing.get('id')}")
                print(f"    - Seller ID: {target_listing.get('seller_id')}")
                print(f"    - Title: {target_listing.get('title')}")
            
            return {
                "test_name": "Browse Listings Consistency",
                "success": True,
                "total_listings": len(listings),
                "walker351631A_in_browse": walker_in_browse,
                "admin_listings_in_browse": admin_listings_count,
                "target_listing_details": target_listing,
                "admin_listings": admin_listings,
                "response_time_ms": result["response_time_ms"]
            }
        else:
            print(f"  ❌ Failed to get browse listings: {result.get('error')}")
            return {
                "test_name": "Browse Listings Consistency",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def test_seller_id_resolution_logic(self) -> Dict:
        """Test that the ID resolution function works correctly"""
        print("🔧 Testing seller_id resolution logic...")
        
        # Test admin profile endpoint to verify ID resolution
        admin_profile_result = await self.make_request(f"/auth/profile/{ADMIN_ID}")
        legacy_profile_result = await self.make_request(f"/auth/profile/{LEGACY_ADMIN_ID}")
        
        admin_profile_works = admin_profile_result["success"]
        legacy_profile_works = legacy_profile_result["success"]
        
        # Check if both IDs resolve to the same user
        profiles_match = False
        if admin_profile_works and legacy_profile_works:
            admin_data = admin_profile_result["data"]
            legacy_data = legacy_profile_result["data"]
            
            # They should resolve to the same user (admin)
            profiles_match = (
                admin_data.get("email") == legacy_data.get("email") and
                admin_data.get("username") == legacy_data.get("username")
            )
        
        print(f"  🆔 Admin ID '{ADMIN_ID}' profile access: {'✅' if admin_profile_works else '❌'}")
        print(f"  🆔 Legacy ID '{LEGACY_ADMIN_ID}' profile access: {'✅' if legacy_profile_works else '❌'}")
        print(f"  🔗 ID resolution working: {'✅' if profiles_match else '❌'}")
        
        return {
            "test_name": "Seller ID Resolution Logic",
            "admin_id_works": admin_profile_works,
            "legacy_id_works": legacy_profile_works,
            "profiles_match": profiles_match,
            "id_resolution_working": profiles_match,
            "admin_profile": admin_profile_result["data"] if admin_profile_works else None,
            "legacy_profile": legacy_profile_result["data"] if legacy_profile_works else None
        }
    
    async def test_demo_user_listings_regression(self) -> Dict:
        """Test that demo user listings still work correctly (no regression)"""
        print("👤 Testing demo user listings for regression...")
        
        result = await self.make_request(f"/user/my-listings/{DEMO_USER_ID}")
        
        if result["success"]:
            listings = result["data"]
            total_listings = len(listings)
            
            print(f"  📊 Demo user has {total_listings} listings")
            print(f"  ✅ Demo user my-listings endpoint working")
            
            # Check some listing details
            sample_listings = listings[:3] if listings else []
            for i, listing in enumerate(sample_listings):
                print(f"    {i+1}. {listing.get('title', 'Unknown')} - €{listing.get('price', 0)}")
            
            return {
                "test_name": "Demo User Listings Regression",
                "success": True,
                "total_listings": total_listings,
                "demo_listings_working": True,
                "sample_listings": sample_listings,
                "response_time_ms": result["response_time_ms"]
            }
        else:
            print(f"  ❌ Demo user my-listings failed: {result.get('error')}")
            return {
                "test_name": "Demo User Listings Regression",
                "success": False,
                "demo_listings_working": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def test_data_consistency_cross_verification(self) -> Dict:
        """Cross-verify data consistency between browse and my-listings"""
        print("🔄 Cross-verifying data consistency...")
        
        # Get browse listings
        browse_result = await self.make_request("/marketplace/browse")
        
        # Get admin my-listings
        admin_listings_result = await self.make_request(f"/user/my-listings/{ADMIN_ID}")
        
        if not browse_result["success"] or not admin_listings_result["success"]:
            return {
                "test_name": "Data Consistency Cross-Verification",
                "success": False,
                "error": "Failed to get required data for comparison"
            }
        
        browse_listings = browse_result["data"]
        admin_my_listings = admin_listings_result["data"]
        
        # Find admin listings in browse
        admin_in_browse = []
        for listing in browse_listings:
            seller_id = listing.get("seller_id")
            if seller_id in [ADMIN_ID, LEGACY_ADMIN_ID]:
                admin_in_browse.append(listing)
        
        # Check consistency
        admin_browse_count = len(admin_in_browse)
        admin_my_listings_count = len(admin_my_listings)
        
        # Look for walker351631A specifically
        walker_in_browse = any(
            l.get("title") == TARGET_LISTING_NAME or l.get("id") == TARGET_LISTING_ID 
            for l in admin_in_browse
        )
        walker_in_my_listings = any(
            l.get("title") == TARGET_LISTING_NAME or l.get("id") == TARGET_LISTING_ID 
            for l in admin_my_listings
        )
        
        consistency_achieved = walker_in_browse and walker_in_my_listings
        
        print(f"  📊 Admin listings in browse: {admin_browse_count}")
        print(f"  📊 Admin listings in my-listings: {admin_my_listings_count}")
        print(f"  🎯 walker351631A in browse: {'✅' if walker_in_browse else '❌'}")
        print(f"  🎯 walker351631A in my-listings: {'✅' if walker_in_my_listings else '❌'}")
        print(f"  🔄 Data consistency achieved: {'✅' if consistency_achieved else '❌'}")
        
        return {
            "test_name": "Data Consistency Cross-Verification",
            "success": True,
            "admin_listings_in_browse": admin_browse_count,
            "admin_listings_in_my_listings": admin_my_listings_count,
            "walker_in_browse": walker_in_browse,
            "walker_in_my_listings": walker_in_my_listings,
            "data_consistency_achieved": consistency_achieved,
            "fix_working_correctly": consistency_achieved
        }
    
    async def test_legacy_seller_id_mapping(self) -> Dict:
        """Test that legacy seller_id mapping includes the expected ID"""
        print("🗂️ Testing legacy seller_id mapping...")
        
        # Get the specific listing by ID to check its seller_id
        browse_result = await self.make_request("/marketplace/browse")
        
        if not browse_result["success"]:
            return {
                "test_name": "Legacy Seller ID Mapping",
                "success": False,
                "error": "Failed to get browse listings"
            }
        
        listings = browse_result["data"]
        target_listing = None
        
        # Find the target listing
        for listing in listings:
            if (listing.get("title") == TARGET_LISTING_NAME or 
                listing.get("id") == TARGET_LISTING_ID):
                target_listing = listing
                break
        
        if not target_listing:
            return {
                "test_name": "Legacy Seller ID Mapping",
                "success": False,
                "error": f"Target listing '{TARGET_LISTING_NAME}' not found in browse"
            }
        
        listing_seller_id = target_listing.get("seller_id")
        has_legacy_id = listing_seller_id == LEGACY_ADMIN_ID
        
        print(f"  🎯 Target listing found: {target_listing.get('title')}")
        print(f"  🆔 Listing seller_id: {listing_seller_id}")
        print(f"  🔗 Has legacy admin ID: {'✅' if has_legacy_id else '❌'}")
        print(f"  📝 Expected legacy ID: {LEGACY_ADMIN_ID}")
        
        return {
            "test_name": "Legacy Seller ID Mapping",
            "success": True,
            "target_listing_found": True,
            "listing_seller_id": listing_seller_id,
            "expected_legacy_id": LEGACY_ADMIN_ID,
            "has_legacy_admin_id": has_legacy_id,
            "target_listing_details": target_listing
        }
    
    async def run_comprehensive_seller_id_test(self) -> Dict:
        """Run all seller ID resolution tests"""
        print("🚀 Starting Seller ID Resolution Fix Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Authenticate users
            admin_auth = await self.authenticate_admin()
            demo_auth = await self.authenticate_demo_user()
            
            if not admin_auth["success"]:
                return {
                    "error": "Failed to authenticate admin user",
                    "admin_auth": admin_auth
                }
            
            # Run all tests
            admin_my_listings = await self.test_admin_my_listings_after_fix()
            browse_consistency = await self.test_browse_listings_consistency()
            id_resolution = await self.test_seller_id_resolution_logic()
            demo_regression = await self.test_demo_user_listings_regression()
            data_consistency = await self.test_data_consistency_cross_verification()
            legacy_mapping = await self.test_legacy_seller_id_mapping()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "target_listing": TARGET_LISTING_NAME,
                "target_listing_id": TARGET_LISTING_ID,
                "admin_id": ADMIN_ID,
                "legacy_admin_id": LEGACY_ADMIN_ID,
                "demo_user_id": DEMO_USER_ID,
                "admin_authentication": admin_auth,
                "demo_authentication": demo_auth,
                "admin_my_listings_test": admin_my_listings,
                "browse_consistency_test": browse_consistency,
                "id_resolution_test": id_resolution,
                "demo_regression_test": demo_regression,
                "data_consistency_test": data_consistency,
                "legacy_mapping_test": legacy_mapping
            }
            
            # Calculate success metrics
            test_results = [
                admin_my_listings.get("fix_successful", False),
                browse_consistency.get("walker351631A_in_browse", False),
                id_resolution.get("id_resolution_working", False),
                demo_regression.get("demo_listings_working", False),
                data_consistency.get("data_consistency_achieved", False),
                legacy_mapping.get("has_legacy_admin_id", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            fix_completely_successful = all(test_results)
            
            # Key metrics for the fix
            walker_now_in_admin_listings = admin_my_listings.get("walker351631A_found", False)
            admin_listing_count_correct = admin_my_listings.get("count_matches_expectation", False)
            data_consistency_achieved = data_consistency.get("data_consistency_achieved", False)
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "fix_completely_successful": fix_completely_successful,
                "walker351631A_now_in_admin_listings": walker_now_in_admin_listings,
                "admin_listing_count_now_4": admin_listing_count_correct,
                "data_consistency_achieved": data_consistency_achieved,
                "id_resolution_working": id_resolution.get("id_resolution_working", False),
                "demo_user_no_regression": demo_regression.get("demo_listings_working", False),
                "legacy_seller_id_mapping_confirmed": legacy_mapping.get("has_legacy_admin_id", False),
                "all_critical_tests_passed": fix_completely_successful
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = SellerIdResolutionTester()
    results = await tester.run_comprehensive_seller_id_test()
    
    print("\n" + "=" * 60)
    print("📊 SELLER ID RESOLUTION FIX TEST RESULTS")
    print("=" * 60)
    
    summary = results.get("summary", {})
    
    print(f"🎯 Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"✅ Fix Completely Successful: {summary.get('fix_completely_successful', False)}")
    print(f"📋 walker351631A in Admin My-Listings: {summary.get('walker351631A_now_in_admin_listings', False)}")
    print(f"📊 Admin Listing Count Now 4: {summary.get('admin_listing_count_now_4', False)}")
    print(f"🔄 Data Consistency Achieved: {summary.get('data_consistency_achieved', False)}")
    print(f"🔧 ID Resolution Working: {summary.get('id_resolution_working', False)}")
    print(f"👤 Demo User No Regression: {summary.get('demo_user_no_regression', False)}")
    print(f"🗂️ Legacy Seller ID Mapping Confirmed: {summary.get('legacy_seller_id_mapping_confirmed', False)}")
    
    print("\n📋 DETAILED TEST RESULTS:")
    
    # Admin My-Listings Test
    admin_test = results.get("admin_my_listings_test", {})
    if admin_test.get("success"):
        print(f"  Admin My-Listings: {admin_test.get('total_listings', 0)} listings, walker351631A found: {admin_test.get('walker351631A_found', False)}")
    else:
        print(f"  Admin My-Listings: FAILED - {admin_test.get('error', 'Unknown error')}")
    
    # Browse Consistency Test
    browse_test = results.get("browse_consistency_test", {})
    if browse_test.get("success"):
        print(f"  Browse Consistency: {browse_test.get('total_listings', 0)} total listings, walker351631A in browse: {browse_test.get('walker351631A_in_browse', False)}")
    else:
        print(f"  Browse Consistency: FAILED - {browse_test.get('error', 'Unknown error')}")
    
    # Data Consistency Test
    consistency_test = results.get("data_consistency_test", {})
    if consistency_test.get("success"):
        print(f"  Data Consistency: Browse({consistency_test.get('admin_listings_in_browse', 0)}) vs My-Listings({consistency_test.get('admin_listings_in_my_listings', 0)}) admin listings")
    else:
        print(f"  Data Consistency: FAILED - {consistency_test.get('error', 'Unknown error')}")
    
    # Demo User Regression Test
    demo_test = results.get("demo_regression_test", {})
    if demo_test.get("success"):
        print(f"  Demo User Regression: {demo_test.get('total_listings', 0)} listings, working: {demo_test.get('demo_listings_working', False)}")
    else:
        print(f"  Demo User Regression: FAILED - {demo_test.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    
    if summary.get('fix_completely_successful', False):
        print("🎉 SELLER ID RESOLUTION FIX SUCCESSFUL!")
        print("✅ Admin can now see walker351631A in my-listings")
        print("✅ Data consistency achieved between browse and my-listings")
        print("✅ Legacy seller_id resolution working correctly")
    else:
        print("❌ SELLER ID RESOLUTION FIX NEEDS ATTENTION")
        failed_tests = []
        if not summary.get('walker351631A_now_in_admin_listings', False):
            failed_tests.append("walker351631A not in admin my-listings")
        if not summary.get('data_consistency_achieved', False):
            failed_tests.append("data consistency not achieved")
        if not summary.get('id_resolution_working', False):
            failed_tests.append("ID resolution not working")
        
        print(f"❌ Issues: {', '.join(failed_tests)}")
    
    # Save detailed results to file
    with open('/app/seller_id_resolution_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/seller_id_resolution_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())