#!/usr/bin/env python3
"""
LISTING VISIBILITY INVESTIGATION TEST
Testing specific listing visibility issues reported by the user:
1. Admin listing "walker351631A" visible in browse but NOT in "My Listings"
2. Demo user listings not loading with ID "68bfff790e4e46bc28d43631"
3. Data consistency between browse and my-listings endpoints
4. Cross-reference seller_id mappings
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://admin-nav-control.preview.emergentagent.com/api"

# User IDs from review request
ADMIN_USER_ID = "admin_user_1"  # Admin user ID
DEMO_USER_ID = "68bfff790e4e46bc28d43631"  # Demo user ID from review
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "demo@cataloro.com"

# Listing to investigate
TARGET_LISTING_TITLE = "walker351631A"

class ListingVisibilityTester:
    def __init__(self):
        self.session = None
        self.admin_user_data = None
        self.demo_user_data = None
        self.browse_listings = []
        self.admin_listings = []
        self.demo_listings = []
        
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
    
    async def authenticate_users(self) -> Dict:
        """Authenticate both admin and demo users"""
        print("🔐 Authenticating users...")
        
        results = {"admin": None, "demo": None}
        
        # Authenticate admin user
        admin_login = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login)
        if admin_result["success"]:
            self.admin_user_data = admin_result["data"]["user"]
            results["admin"] = {
                "success": True,
                "user_id": self.admin_user_data.get("id"),
                "username": self.admin_user_data.get("username"),
                "email": self.admin_user_data.get("email"),
                "role": self.admin_user_data.get("role", self.admin_user_data.get("user_role"))
            }
            print(f"  ✅ Admin authenticated: {self.admin_user_data.get('id')} ({self.admin_user_data.get('username')})")
        else:
            results["admin"] = {
                "success": False,
                "error": admin_result.get("error", "Login failed")
            }
            print(f"  ❌ Admin authentication failed: {admin_result.get('error')}")
        
        # Authenticate demo user
        demo_login = {
            "email": DEMO_EMAIL,
            "password": "demo_password"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login)
        if demo_result["success"]:
            self.demo_user_data = demo_result["data"]["user"]
            results["demo"] = {
                "success": True,
                "user_id": self.demo_user_data.get("id"),
                "username": self.demo_user_data.get("username"),
                "email": self.demo_user_data.get("email"),
                "role": self.demo_user_data.get("role", self.demo_user_data.get("user_role"))
            }
            print(f"  ✅ Demo user authenticated: {self.demo_user_data.get('id')} ({self.demo_user_data.get('username')})")
        else:
            results["demo"] = {
                "success": False,
                "error": demo_result.get("error", "Login failed")
            }
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error')}")
        
        return results
    
    async def test_browse_listings(self) -> Dict:
        """Test GET /api/marketplace/browse to see all listings"""
        print("🔍 Testing browse listings endpoint...")
        
        result = await self.make_request("/marketplace/browse")
        
        if result["success"]:
            self.browse_listings = result["data"]
            
            # Look for the target listing
            target_listing = None
            admin_listings_in_browse = []
            demo_listings_in_browse = []
            
            for listing in self.browse_listings:
                # Check for target listing
                if TARGET_LISTING_TITLE.lower() in listing.get("title", "").lower():
                    target_listing = listing
                
                # Check seller_id mappings
                seller_id = listing.get("seller_id")
                if seller_id == ADMIN_USER_ID or (self.admin_user_data and seller_id == self.admin_user_data.get("id")):
                    admin_listings_in_browse.append(listing)
                elif seller_id == DEMO_USER_ID or (self.demo_user_data and seller_id == self.demo_user_data.get("id")):
                    demo_listings_in_browse.append(listing)
            
            print(f"  ✅ Browse endpoint returned {len(self.browse_listings)} listings")
            print(f"  🎯 Target listing '{TARGET_LISTING_TITLE}' found: {'✅' if target_listing else '❌'}")
            print(f"  👤 Admin listings in browse: {len(admin_listings_in_browse)}")
            print(f"  👤 Demo listings in browse: {len(demo_listings_in_browse)}")
            
            if target_listing:
                print(f"    📋 Target listing details:")
                print(f"      - ID: {target_listing.get('id')}")
                print(f"      - Title: {target_listing.get('title')}")
                print(f"      - Seller ID: {target_listing.get('seller_id')}")
                print(f"      - Price: {target_listing.get('price')}")
            
            return {
                "test_name": "Browse Listings",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "total_listings": len(self.browse_listings),
                "target_listing_found": target_listing is not None,
                "target_listing_details": target_listing,
                "admin_listings_count": len(admin_listings_in_browse),
                "demo_listings_count": len(demo_listings_in_browse),
                "admin_listings_in_browse": admin_listings_in_browse,
                "demo_listings_in_browse": demo_listings_in_browse
            }
        else:
            print(f"  ❌ Browse endpoint failed: {result.get('error')}")
            return {
                "test_name": "Browse Listings",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def test_admin_my_listings(self) -> Dict:
        """Test GET /api/user/my-listings/{admin_user_id}"""
        print("👑 Testing admin 'My Listings' endpoint...")
        
        if not self.admin_user_data:
            return {
                "test_name": "Admin My Listings",
                "success": False,
                "error": "Admin user not authenticated"
            }
        
        admin_id = self.admin_user_data.get("id")
        result = await self.make_request(f"/user/my-listings/{admin_id}")
        
        if result["success"]:
            self.admin_listings = result["data"]
            
            # Look for target listing
            target_listing_in_my_listings = None
            for listing in self.admin_listings:
                if TARGET_LISTING_TITLE.lower() in listing.get("title", "").lower():
                    target_listing_in_my_listings = listing
                    break
            
            print(f"  ✅ Admin my-listings returned {len(self.admin_listings)} listings")
            print(f"  🎯 Target listing '{TARGET_LISTING_TITLE}' in my-listings: {'✅' if target_listing_in_my_listings else '❌'}")
            
            if self.admin_listings:
                print(f"    📋 Admin listings in my-listings:")
                for i, listing in enumerate(self.admin_listings[:5]):  # Show first 5
                    print(f"      {i+1}. {listing.get('title')} (ID: {listing.get('id')})")
            
            return {
                "test_name": "Admin My Listings",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "admin_user_id": admin_id,
                "total_listings": len(self.admin_listings),
                "target_listing_in_my_listings": target_listing_in_my_listings is not None,
                "target_listing_details": target_listing_in_my_listings,
                "all_admin_listings": self.admin_listings
            }
        else:
            print(f"  ❌ Admin my-listings failed: {result.get('error')}")
            return {
                "test_name": "Admin My Listings",
                "success": False,
                "error": result.get("error"),
                "status": result["status"],
                "admin_user_id": admin_id
            }
    
    async def test_demo_my_listings(self) -> Dict:
        """Test GET /api/user/my-listings/{demo_user_id}"""
        print("👤 Testing demo user 'My Listings' endpoint...")
        
        # Test with both the provided demo user ID and authenticated user ID
        test_ids = [DEMO_USER_ID]
        if self.demo_user_data and self.demo_user_data.get("id") != DEMO_USER_ID:
            test_ids.append(self.demo_user_data.get("id"))
        
        results = []
        
        for demo_id in test_ids:
            print(f"  Testing with user ID: {demo_id}")
            result = await self.make_request(f"/user/my-listings/{demo_id}")
            
            if result["success"]:
                listings = result["data"]
                print(f"    ✅ Demo my-listings returned {len(listings)} listings")
                
                if listings:
                    print(f"      📋 Demo listings found:")
                    for i, listing in enumerate(listings[:5]):  # Show first 5
                        print(f"        {i+1}. {listing.get('title')} (ID: {listing.get('id')})")
                else:
                    print(f"      ⚠️ No listings found for demo user")
                
                results.append({
                    "user_id": demo_id,
                    "success": True,
                    "response_time_ms": result["response_time_ms"],
                    "total_listings": len(listings),
                    "listings": listings
                })
                
                # Store the first successful result
                if not self.demo_listings:
                    self.demo_listings = listings
                    
            else:
                print(f"    ❌ Demo my-listings failed: {result.get('error')}")
                results.append({
                    "user_id": demo_id,
                    "success": False,
                    "error": result.get("error"),
                    "status": result["status"]
                })
        
        # Return summary of all tests
        successful_tests = [r for r in results if r["success"]]
        return {
            "test_name": "Demo My Listings",
            "demo_user_ids_tested": test_ids,
            "successful_tests": len(successful_tests),
            "total_tests": len(results),
            "demo_listings_loading": len(successful_tests) > 0,
            "demo_listings_count": sum(r.get("total_listings", 0) for r in successful_tests),
            "detailed_results": results
        }
    
    async def test_data_consistency(self) -> Dict:
        """Compare listings between browse and my-listings endpoints"""
        print("🔄 Testing data consistency between browse and my-listings...")
        
        consistency_issues = []
        
        # Check admin listings consistency
        if self.admin_user_data:
            admin_id = self.admin_user_data.get("id")
            
            # Find admin listings in browse
            admin_in_browse = [l for l in self.browse_listings if l.get("seller_id") == admin_id]
            
            # Compare with my-listings
            browse_ids = set(l.get("id") for l in admin_in_browse)
            my_listings_ids = set(l.get("id") for l in self.admin_listings)
            
            # Check for discrepancies
            in_browse_not_my_listings = browse_ids - my_listings_ids
            in_my_listings_not_browse = my_listings_ids - browse_ids
            
            if in_browse_not_my_listings:
                consistency_issues.append({
                    "user": "admin",
                    "issue": "listings_in_browse_not_in_my_listings",
                    "listing_ids": list(in_browse_not_my_listings),
                    "count": len(in_browse_not_my_listings)
                })
                print(f"  ⚠️ Admin listings in browse but NOT in my-listings: {len(in_browse_not_my_listings)}")
                for listing_id in in_browse_not_my_listings:
                    listing = next((l for l in admin_in_browse if l.get("id") == listing_id), None)
                    if listing:
                        print(f"    - {listing.get('title')} (ID: {listing_id})")
            
            if in_my_listings_not_browse:
                consistency_issues.append({
                    "user": "admin",
                    "issue": "listings_in_my_listings_not_in_browse",
                    "listing_ids": list(in_my_listings_not_browse),
                    "count": len(in_my_listings_not_browse)
                })
                print(f"  ⚠️ Admin listings in my-listings but NOT in browse: {len(in_my_listings_not_browse)}")
        
        # Check demo user consistency
        if self.demo_user_data:
            demo_id = self.demo_user_data.get("id")
            
            # Find demo listings in browse
            demo_in_browse = [l for l in self.browse_listings if l.get("seller_id") == demo_id]
            
            # Compare with my-listings
            browse_ids = set(l.get("id") for l in demo_in_browse)
            my_listings_ids = set(l.get("id") for l in self.demo_listings)
            
            # Check for discrepancies
            in_browse_not_my_listings = browse_ids - my_listings_ids
            in_my_listings_not_browse = my_listings_ids - browse_ids
            
            if in_browse_not_my_listings:
                consistency_issues.append({
                    "user": "demo",
                    "issue": "listings_in_browse_not_in_my_listings",
                    "listing_ids": list(in_browse_not_my_listings),
                    "count": len(in_browse_not_my_listings)
                })
                print(f"  ⚠️ Demo listings in browse but NOT in my-listings: {len(in_browse_not_my_listings)}")
            
            if in_my_listings_not_browse:
                consistency_issues.append({
                    "user": "demo",
                    "issue": "listings_in_my_listings_not_in_browse",
                    "listing_ids": list(in_my_listings_not_browse),
                    "count": len(in_my_listings_not_browse)
                })
                print(f"  ⚠️ Demo listings in my-listings but NOT in browse: {len(in_my_listings_not_browse)}")
        
        # Check seller_id consistency
        seller_id_issues = []
        for listing in self.browse_listings:
            listing_id = listing.get("id")
            seller_id = listing.get("seller_id")
            
            if not seller_id:
                seller_id_issues.append({
                    "listing_id": listing_id,
                    "title": listing.get("title"),
                    "issue": "missing_seller_id"
                })
        
        if seller_id_issues:
            consistency_issues.append({
                "issue": "missing_seller_ids",
                "count": len(seller_id_issues),
                "details": seller_id_issues
            })
            print(f"  ⚠️ Listings with missing seller_id: {len(seller_id_issues)}")
        
        if not consistency_issues:
            print("  ✅ No data consistency issues found")
        
        return {
            "test_name": "Data Consistency",
            "consistency_issues_found": len(consistency_issues),
            "data_consistent": len(consistency_issues) == 0,
            "detailed_issues": consistency_issues
        }
    
    async def test_user_id_mappings(self) -> Dict:
        """Test user ID consistency and mappings"""
        print("🆔 Testing user ID mappings and consistency...")
        
        mapping_issues = []
        
        # Check admin user ID consistency
        if self.admin_user_data:
            expected_admin_id = ADMIN_USER_ID
            actual_admin_id = self.admin_user_data.get("id")
            
            if expected_admin_id != actual_admin_id:
                mapping_issues.append({
                    "user": "admin",
                    "issue": "user_id_mismatch",
                    "expected": expected_admin_id,
                    "actual": actual_admin_id
                })
                print(f"  ⚠️ Admin user ID mismatch: expected {expected_admin_id}, got {actual_admin_id}")
            else:
                print(f"  ✅ Admin user ID consistent: {actual_admin_id}")
        
        # Check demo user ID consistency
        if self.demo_user_data:
            expected_demo_id = DEMO_USER_ID
            actual_demo_id = self.demo_user_data.get("id")
            
            if expected_demo_id != actual_demo_id:
                mapping_issues.append({
                    "user": "demo",
                    "issue": "user_id_mismatch",
                    "expected": expected_demo_id,
                    "actual": actual_demo_id
                })
                print(f"  ⚠️ Demo user ID mismatch: expected {expected_demo_id}, got {actual_demo_id}")
            else:
                print(f"  ✅ Demo user ID consistent: {actual_demo_id}")
        
        # Check if listings have valid seller_ids that match existing users
        unique_seller_ids = set()
        for listing in self.browse_listings:
            seller_id = listing.get("seller_id")
            if seller_id:
                unique_seller_ids.add(seller_id)
        
        print(f"  📊 Found {len(unique_seller_ids)} unique seller IDs in browse listings")
        
        # Test if each seller_id corresponds to a valid user
        valid_seller_ids = []
        invalid_seller_ids = []
        
        for seller_id in unique_seller_ids:
            # Try to get user profile
            profile_result = await self.make_request(f"/auth/profile/{seller_id}")
            if profile_result["success"]:
                valid_seller_ids.append(seller_id)
            else:
                invalid_seller_ids.append({
                    "seller_id": seller_id,
                    "error": profile_result.get("error", "Profile not found")
                })
        
        if invalid_seller_ids:
            mapping_issues.append({
                "issue": "invalid_seller_ids",
                "count": len(invalid_seller_ids),
                "details": invalid_seller_ids
            })
            print(f"  ⚠️ Invalid seller IDs found: {len(invalid_seller_ids)}")
        else:
            print(f"  ✅ All seller IDs are valid")
        
        return {
            "test_name": "User ID Mappings",
            "mapping_issues_found": len(mapping_issues),
            "user_id_mappings_consistent": len(mapping_issues) == 0,
            "unique_seller_ids_count": len(unique_seller_ids),
            "valid_seller_ids_count": len(valid_seller_ids),
            "invalid_seller_ids_count": len(invalid_seller_ids),
            "detailed_issues": mapping_issues
        }
    
    async def investigate_target_listing(self) -> Dict:
        """Deep dive investigation of the target listing 'walker351631A'"""
        print(f"🔍 Deep investigation of target listing '{TARGET_LISTING_TITLE}'...")
        
        investigation_results = {
            "target_listing_title": TARGET_LISTING_TITLE,
            "found_in_browse": False,
            "found_in_admin_my_listings": False,
            "found_in_demo_my_listings": False,
            "listing_details": None,
            "seller_id_analysis": None
        }
        
        # Search in browse listings
        target_in_browse = None
        for listing in self.browse_listings:
            if TARGET_LISTING_TITLE.lower() in listing.get("title", "").lower():
                target_in_browse = listing
                investigation_results["found_in_browse"] = True
                investigation_results["listing_details"] = listing
                break
        
        # Search in admin my-listings
        target_in_admin = None
        for listing in self.admin_listings:
            if TARGET_LISTING_TITLE.lower() in listing.get("title", "").lower():
                target_in_admin = listing
                investigation_results["found_in_admin_my_listings"] = True
                break
        
        # Search in demo my-listings
        target_in_demo = None
        for listing in self.demo_listings:
            if TARGET_LISTING_TITLE.lower() in listing.get("title", "").lower():
                target_in_demo = listing
                investigation_results["found_in_demo_my_listings"] = True
                break
        
        if target_in_browse:
            seller_id = target_in_browse.get("seller_id")
            print(f"  ✅ Target listing found in browse")
            print(f"    - Listing ID: {target_in_browse.get('id')}")
            print(f"    - Seller ID: {seller_id}")
            print(f"    - Price: {target_in_browse.get('price')}")
            print(f"    - Status: {target_in_browse.get('status', 'unknown')}")
            
            # Analyze seller_id
            if seller_id:
                if seller_id == self.admin_user_data.get("id") if self.admin_user_data else False:
                    investigation_results["seller_id_analysis"] = "belongs_to_admin"
                    print(f"    - ✅ Seller ID matches admin user")
                elif seller_id == self.demo_user_data.get("id") if self.demo_user_data else False:
                    investigation_results["seller_id_analysis"] = "belongs_to_demo"
                    print(f"    - ✅ Seller ID matches demo user")
                else:
                    investigation_results["seller_id_analysis"] = "belongs_to_other_user"
                    print(f"    - ⚠️ Seller ID belongs to different user: {seller_id}")
                    
                    # Try to get seller profile
                    seller_profile = await self.make_request(f"/auth/profile/{seller_id}")
                    if seller_profile["success"]:
                        seller_data = seller_profile["data"]
                        print(f"    - Seller profile: {seller_data.get('username')} ({seller_data.get('email')})")
                        investigation_results["seller_profile"] = seller_data
            else:
                investigation_results["seller_id_analysis"] = "missing_seller_id"
                print(f"    - ❌ Missing seller_id")
        else:
            print(f"  ❌ Target listing NOT found in browse")
        
        if not target_in_admin and investigation_results["found_in_browse"]:
            print(f"  🚨 ISSUE CONFIRMED: Target listing is in browse but NOT in admin my-listings")
        elif target_in_admin:
            print(f"  ✅ Target listing found in admin my-listings")
        
        return investigation_results
    
    async def run_comprehensive_investigation(self) -> Dict:
        """Run complete listing visibility investigation"""
        print("🚀 Starting Listing Visibility Investigation")
        print("=" * 60)
        print(f"🎯 Target listing: '{TARGET_LISTING_TITLE}'")
        print(f"👑 Admin user ID: {ADMIN_USER_ID}")
        print(f"👤 Demo user ID: {DEMO_USER_ID}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run all investigation steps
            auth_results = await self.authenticate_users()
            browse_results = await self.test_browse_listings()
            admin_my_listings_results = await self.test_admin_my_listings()
            demo_my_listings_results = await self.test_demo_my_listings()
            consistency_results = await self.test_data_consistency()
            mapping_results = await self.test_user_id_mappings()
            target_investigation = await self.investigate_target_listing()
            
            # Compile comprehensive results
            investigation_results = {
                "investigation_timestamp": datetime.now().isoformat(),
                "target_listing": TARGET_LISTING_TITLE,
                "admin_user_id": ADMIN_USER_ID,
                "demo_user_id": DEMO_USER_ID,
                "authentication": auth_results,
                "browse_listings": browse_results,
                "admin_my_listings": admin_my_listings_results,
                "demo_my_listings": demo_my_listings_results,
                "data_consistency": consistency_results,
                "user_id_mappings": mapping_results,
                "target_listing_investigation": target_investigation
            }
            
            # Generate summary of critical findings
            critical_issues = []
            
            # Check for the main reported issue
            if (target_investigation.get("found_in_browse") and 
                not target_investigation.get("found_in_admin_my_listings")):
                critical_issues.append({
                    "issue": "target_listing_visibility_mismatch",
                    "description": f"Listing '{TARGET_LISTING_TITLE}' found in browse but NOT in admin my-listings",
                    "severity": "high"
                })
            
            # Check demo user listings loading
            if not demo_my_listings_results.get("demo_listings_loading"):
                critical_issues.append({
                    "issue": "demo_user_listings_not_loading",
                    "description": f"Demo user listings not loading for ID {DEMO_USER_ID}",
                    "severity": "high"
                })
            
            # Check data consistency issues
            if not consistency_results.get("data_consistent"):
                critical_issues.append({
                    "issue": "data_consistency_problems",
                    "description": f"Found {consistency_results.get('consistency_issues_found')} data consistency issues",
                    "severity": "medium"
                })
            
            # Check user ID mapping issues
            if not mapping_results.get("user_id_mappings_consistent"):
                critical_issues.append({
                    "issue": "user_id_mapping_problems",
                    "description": f"Found {mapping_results.get('mapping_issues_found')} user ID mapping issues",
                    "severity": "medium"
                })
            
            investigation_results["summary"] = {
                "critical_issues_found": len(critical_issues),
                "main_issue_confirmed": any(i["issue"] == "target_listing_visibility_mismatch" for i in critical_issues),
                "demo_listings_issue_confirmed": any(i["issue"] == "demo_user_listings_not_loading" for i in critical_issues),
                "data_consistency_issues": not consistency_results.get("data_consistent"),
                "user_id_mapping_issues": not mapping_results.get("user_id_mappings_consistent"),
                "investigation_successful": auth_results.get("admin", {}).get("success", False) and browse_results.get("success", False),
                "detailed_critical_issues": critical_issues
            }
            
            return investigation_results
            
        finally:
            await self.cleanup()

async def main():
    """Run the listing visibility investigation"""
    tester = ListingVisibilityTester()
    results = await tester.run_comprehensive_investigation()
    
    print("\n" + "=" * 60)
    print("📊 INVESTIGATION SUMMARY")
    print("=" * 60)
    
    summary = results.get("summary", {})
    
    print(f"🎯 Target listing '{TARGET_LISTING_TITLE}' investigation:")
    target_inv = results.get("target_listing_investigation", {})
    print(f"  - Found in browse: {'✅' if target_inv.get('found_in_browse') else '❌'}")
    print(f"  - Found in admin my-listings: {'✅' if target_inv.get('found_in_admin_my_listings') else '❌'}")
    print(f"  - Seller ID analysis: {target_inv.get('seller_id_analysis', 'unknown')}")
    
    print(f"\n👤 Demo user listings (ID: {DEMO_USER_ID}):")
    demo_results = results.get("demo_my_listings", {})
    print(f"  - Listings loading: {'✅' if demo_results.get('demo_listings_loading') else '❌'}")
    print(f"  - Total listings found: {demo_results.get('demo_listings_count', 0)}")
    
    print(f"\n🔄 Data consistency:")
    consistency = results.get("data_consistency", {})
    print(f"  - Data consistent: {'✅' if consistency.get('data_consistent') else '❌'}")
    print(f"  - Issues found: {consistency.get('consistency_issues_found', 0)}")
    
    print(f"\n🆔 User ID mappings:")
    mappings = results.get("user_id_mappings", {})
    print(f"  - Mappings consistent: {'✅' if mappings.get('user_id_mappings_consistent') else '❌'}")
    print(f"  - Issues found: {mappings.get('mapping_issues_found', 0)}")
    
    print(f"\n🚨 Critical Issues Found: {summary.get('critical_issues_found', 0)}")
    for issue in summary.get("detailed_critical_issues", []):
        print(f"  - {issue['description']} (Severity: {issue['severity']})")
    
    print(f"\n✅ Main issue confirmed: {'YES' if summary.get('main_issue_confirmed') else 'NO'}")
    print(f"✅ Demo listings issue confirmed: {'YES' if summary.get('demo_listings_issue_confirmed') else 'NO'}")
    
    # Save detailed results to file
    with open("/app/listing_visibility_investigation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/listing_visibility_investigation_results.json")

if __name__ == "__main__":
    asyncio.run(main())