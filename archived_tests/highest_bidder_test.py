#!/usr/bin/env python3
"""
HIGHEST BIDDER FUNCTIONALITY TESTING - INDIVIDUAL LISTING PAGE
Testing the highest bidder functionality fix on individual listing page as requested:

ISSUE REPORTED:
- "Individual listing page does not show highest bidder functionality"
- "User is able to place a bid although he is already the highest bidder on individual listing page"

FIXES APPLIED:
1. Added highest_bidder_id calculation: Updated ProductDetailPage.js to include `highest_bidder_id` in the bid_info structure
2. Added blocking logic: Added check in `handleSubmitTender` to prevent highest bidder from placing another bid
3. Added visual indicators: Visual indicator shows "You're the highest bidder!" when user is highest bidder
4. Disabled form elements: Input field and submit button are disabled when user is highest bidder

SPECIFIC TESTS NEEDED:
1. Individual Listing Data Structure - Test GET `/api/listings/{listing_id}` for listings with active tenders
2. Tender Submission Blocking - Test POST `/api/tenders/submit` when user is already highest bidder
3. Bid Flow Validation - Create test listing with multiple bids and verify highest bidder identification
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-marketplace-6.preview.emergentagent.com/api"

# Test Users Configuration
ADMIN_EMAIL = "admin@cataloro.com"
DEMO_EMAIL = "demo@cataloro.com"
DEMO_USER_ID = "68bfff790e4e46bc28d43631"

class HighestBidderTester:
    """
    HIGHEST BIDDER FUNCTIONALITY TESTING
    Testing the highest bidder functionality fix on individual listing page
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.buyer2_token = None
        self.admin_user_id = None
        self.demo_user_id = None
        self.buyer2_user_id = None
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
        """Authenticate test users"""
        print("🔐 Authenticating users for highest bidder testing...")
        
        # Authenticate admin (seller)
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            self.admin_user_id = admin_result["data"].get("user", {}).get("id", "admin_user_1")
            print(f"  ✅ Admin user (seller) authentication successful (ID: {self.admin_user_id})")
        else:
            print(f"  ❌ Admin user authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
        
        # Authenticate demo user (buyer 1)
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": "demo_password"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            self.demo_user_id = demo_result["data"].get("user", {}).get("id", DEMO_USER_ID)
            print(f"  ✅ Demo user (buyer 1) authentication successful (ID: {self.demo_user_id})")
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error', 'Unknown error')}")
            return False
        
        # Create and authenticate second buyer
        buyer2_email = "buyer2@test.com"
        buyer2_login_data = {
            "email": buyer2_email,
            "password": "buyer2_password"
        }
        
        buyer2_result = await self.make_request("/auth/login", "POST", data=buyer2_login_data)
        
        if buyer2_result["success"]:
            self.buyer2_token = buyer2_result["data"].get("token", "")
            self.buyer2_user_id = buyer2_result["data"].get("user", {}).get("id")
            print(f"  ✅ Buyer 2 authentication successful (ID: {self.buyer2_user_id})")
            return True
        else:
            print(f"  ❌ Buyer 2 authentication failed: {buyer2_result.get('error', 'Unknown error')}")
            return False
    
    async def create_test_listing(self) -> Dict:
        """Create a test listing for highest bidder testing"""
        print("📝 Creating test listing for highest bidder testing...")
        
        listing_data = {
            "title": "Test Catalyst for Highest Bidder Testing",
            "description": "Test listing to verify highest bidder functionality on individual listing page",
            "price": 100.0,
            "category": "Catalysts",
            "condition": "Used",
            "seller_id": self.admin_user_id,
            "images": [],
            "tags": ["test", "highest_bidder"],
            "features": ["test feature"]
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/listings", "POST", data=listing_data, headers=headers)
        
        if result["success"]:
            listing_id = result["data"].get("id")
            print(f"  ✅ Test listing created: {listing_id}")
            return {"listing_id": listing_id, "success": True}
        else:
            print(f"  ❌ Failed to create test listing: {result.get('error', 'Unknown error')}")
            return {"error": f"Failed to create test listing: {result.get('error', 'Unknown error')}"}
    
    async def create_multiple_bids(self, listing_id: str) -> Dict:
        """Create multiple bids to test highest bidder functionality"""
        print("💰 Creating multiple bids for highest bidder testing...")
        
        bids_created = []
        
        # Bid 1: Demo user bids 150
        bid1_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": 150.0
        }
        
        headers1 = {"Authorization": f"Bearer {self.demo_token}"}
        bid1_result = await self.make_request("/tenders/submit", "POST", data=bid1_data, headers=headers1)
        
        if bid1_result["success"]:
            bid1_id = bid1_result["data"].get("tender_id")
            bids_created.append({"bidder": "demo", "amount": 150.0, "tender_id": bid1_id})
            print(f"  ✅ Bid 1 created: Demo user bid €150 (ID: {bid1_id})")
        else:
            print(f"  ❌ Bid 1 failed: {bid1_result.get('error', 'Unknown error')}")
        
        # Bid 2: Buyer2 bids 200 (becomes highest bidder)
        bid2_data = {
            "listing_id": listing_id,
            "buyer_id": self.buyer2_user_id,
            "offer_amount": 200.0
        }
        
        headers2 = {"Authorization": f"Bearer {self.buyer2_token}"}
        bid2_result = await self.make_request("/tenders/submit", "POST", data=bid2_data, headers=headers2)
        
        if bid2_result["success"]:
            bid2_id = bid2_result["data"].get("tender_id")
            bids_created.append({"bidder": "buyer2", "amount": 200.0, "tender_id": bid2_id})
            print(f"  ✅ Bid 2 created: Buyer2 bid €200 (ID: {bid2_id}) - Should be highest bidder")
        else:
            print(f"  ❌ Bid 2 failed: {bid2_result.get('error', 'Unknown error')}")
        
        # Bid 3: Demo user bids 250 (becomes new highest bidder)
        bid3_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": 250.0
        }
        
        bid3_result = await self.make_request("/tenders/submit", "POST", data=bid3_data, headers=headers1)
        
        if bid3_result["success"]:
            bid3_id = bid3_result["data"].get("tender_id")
            bids_created.append({"bidder": "demo", "amount": 250.0, "tender_id": bid3_id})
            print(f"  ✅ Bid 3 created: Demo user bid €250 (ID: {bid3_id}) - Should be new highest bidder")
        else:
            print(f"  ❌ Bid 3 failed: {bid3_result.get('error', 'Unknown error')}")
        
        return {
            "success": len(bids_created) > 0,
            "bids_created": bids_created,
            "expected_highest_bidder": self.demo_user_id if len(bids_created) >= 3 else (self.buyer2_user_id if len(bids_created) >= 2 else None),
            "expected_highest_bid": 250.0 if len(bids_created) >= 3 else (200.0 if len(bids_created) >= 2 else 150.0)
        }
    
    async def test_individual_listing_data_structure(self, listing_id: str, expected_highest_bidder: str, expected_highest_bid: float) -> Dict:
        """
        Test 1: Individual Listing Data Structure
        Test GET `/api/listings/{listing_id}` for listings with active tenders
        Verify that bid_info includes highest_bidder_id
        """
        print("🔍 Testing individual listing data structure with highest_bidder_id...")
        
        test_results = {
            "endpoint": f"/listings/{listing_id}",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "has_bid_info": False,
            "has_highest_bidder_id": False,
            "highest_bidder_id_correct": False,
            "highest_bid_correct": False,
            "bid_info_structure_valid": False,
            "error_messages": [],
            "success": False
        }
        
        # Test individual listing endpoint
        result = await self.make_request(f"/listings/{listing_id}")
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            listing_data = result.get("data", {})
            
            # Check if bid_info exists
            if "bid_info" in listing_data:
                test_results["has_bid_info"] = True
                bid_info = listing_data["bid_info"]
                print(f"    ✅ bid_info found in listing data")
                
                # Check if highest_bidder_id exists
                if "highest_bidder_id" in bid_info:
                    test_results["has_highest_bidder_id"] = True
                    actual_highest_bidder = bid_info["highest_bidder_id"]
                    print(f"    ✅ highest_bidder_id found: {actual_highest_bidder}")
                    
                    # Check if highest_bidder_id is correct
                    if actual_highest_bidder == expected_highest_bidder:
                        test_results["highest_bidder_id_correct"] = True
                        print(f"    ✅ highest_bidder_id is correct: {actual_highest_bidder}")
                    else:
                        test_results["error_messages"].append(f"highest_bidder_id incorrect: expected {expected_highest_bidder}, got {actual_highest_bidder}")
                        print(f"    ❌ highest_bidder_id incorrect: expected {expected_highest_bidder}, got {actual_highest_bidder}")
                else:
                    test_results["error_messages"].append("highest_bidder_id not found in bid_info")
                    print(f"    ❌ highest_bidder_id not found in bid_info")
                
                # Check if highest_bid is correct
                if "highest_bid" in bid_info:
                    actual_highest_bid = bid_info["highest_bid"]
                    if actual_highest_bid == expected_highest_bid:
                        test_results["highest_bid_correct"] = True
                        print(f"    ✅ highest_bid is correct: €{actual_highest_bid}")
                    else:
                        test_results["error_messages"].append(f"highest_bid incorrect: expected €{expected_highest_bid}, got €{actual_highest_bid}")
                        print(f"    ❌ highest_bid incorrect: expected €{expected_highest_bid}, got €{actual_highest_bid}")
                
                # Check bid_info structure
                required_fields = ["has_bids", "total_bids", "highest_bid", "highest_bidder_id"]
                missing_fields = [field for field in required_fields if field not in bid_info]
                if not missing_fields:
                    test_results["bid_info_structure_valid"] = True
                    print(f"    ✅ bid_info has all required fields: {required_fields}")
                else:
                    test_results["error_messages"].append(f"bid_info missing fields: {missing_fields}")
                    print(f"    ❌ bid_info missing fields: {missing_fields}")
            else:
                test_results["error_messages"].append("bid_info not found in listing data")
                print(f"    ❌ bid_info not found in listing data")
            
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
        else:
            test_results["error_messages"].append(f"Individual listing request failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Individual listing request failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        # Determine overall success
        test_results["success"] = (
            test_results["actual_status"] == 200 and
            test_results["has_bid_info"] and
            test_results["has_highest_bidder_id"] and
            test_results["highest_bidder_id_correct"] and
            test_results["bid_info_structure_valid"]
        )
        
        return {
            "test_name": "Individual Listing Data Structure",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def test_tender_submission_blocking(self, listing_id: str, highest_bidder_id: str) -> Dict:
        """
        Test 2: Tender Submission Blocking
        Test POST `/api/tenders/submit` when user is already highest bidder
        Should be blocked at frontend level before reaching backend
        """
        print("🚫 Testing tender submission blocking for highest bidder...")
        
        test_results = {
            "endpoint": "/tenders/submit",
            "highest_bidder_can_bid": False,
            "non_highest_bidder_can_bid": False,
            "blocking_logic_working": False,
            "error_messages": [],
            "success": False
        }
        
        # Test 1: Try to submit another bid as highest bidder (should be blocked)
        print("  🔐 Testing highest bidder attempting another bid...")
        
        # Determine which user is the highest bidder and use their token
        if highest_bidder_id == self.demo_user_id:
            highest_bidder_token = self.demo_token
            non_highest_bidder_token = self.buyer2_token
            non_highest_bidder_id = self.buyer2_user_id
            print(f"    📊 Demo user is highest bidder, testing with demo token")
        else:
            highest_bidder_token = self.buyer2_token
            non_highest_bidder_token = self.demo_token
            non_highest_bidder_id = self.demo_user_id
            print(f"    📊 Buyer2 is highest bidder, testing with buyer2 token")
        
        # Attempt to bid as highest bidder (should fail with appropriate message)
        highest_bidder_bid_data = {
            "listing_id": listing_id,
            "buyer_id": highest_bidder_id,
            "offer_amount": 300.0  # Higher than current highest bid
        }
        
        headers = {"Authorization": f"Bearer {highest_bidder_token}"}
        highest_bidder_result = await self.make_request("/tenders/submit", "POST", data=highest_bidder_bid_data, headers=headers)
        
        if highest_bidder_result["success"]:
            test_results["highest_bidder_can_bid"] = True
            test_results["error_messages"].append("Highest bidder was able to place another bid (should be blocked)")
            print(f"    ❌ Highest bidder was able to place another bid (should be blocked)")
        else:
            # Check if it's blocked for the right reason (not just a generic error)
            error_message = highest_bidder_result.get("data", {}).get("detail", "") if isinstance(highest_bidder_result.get("data"), dict) else str(highest_bidder_result.get("data", ""))
            if "highest" in error_message.lower() or "already" in error_message.lower():
                print(f"    ✅ Highest bidder correctly blocked with appropriate message: {error_message}")
            else:
                print(f"    ⚠️ Highest bidder blocked but with generic error: {error_message}")
        
        # Test 2: Try to submit bid as non-highest bidder (should succeed)
        print("  💰 Testing non-highest bidder attempting to bid...")
        
        non_highest_bidder_bid_data = {
            "listing_id": listing_id,
            "buyer_id": non_highest_bidder_id,
            "offer_amount": 275.0  # Higher than current highest bid
        }
        
        non_highest_headers = {"Authorization": f"Bearer {non_highest_bidder_token}"}
        non_highest_result = await self.make_request("/tenders/submit", "POST", data=non_highest_bidder_bid_data, headers=non_highest_headers)
        
        if non_highest_result["success"]:
            test_results["non_highest_bidder_can_bid"] = True
            print(f"    ✅ Non-highest bidder can place bid successfully")
        else:
            test_results["error_messages"].append(f"Non-highest bidder could not place bid: {non_highest_result.get('error', 'Unknown error')}")
            print(f"    ❌ Non-highest bidder could not place bid: {non_highest_result.get('error', 'Unknown error')}")
        
        # Determine if blocking logic is working
        test_results["blocking_logic_working"] = (
            not test_results["highest_bidder_can_bid"] and 
            test_results["non_highest_bidder_can_bid"]
        )
        
        test_results["success"] = test_results["blocking_logic_working"]
        
        return {
            "test_name": "Tender Submission Blocking",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def test_bid_flow_validation(self, listing_id: str) -> Dict:
        """
        Test 3: Bid Flow Validation
        Create test listing with multiple bids and verify highest bidder identification works correctly
        """
        print("🔄 Testing bid flow validation and highest bidder identification...")
        
        test_results = {
            "listing_tenders_endpoint": f"/listings/{listing_id}/tenders",
            "tenders_count": 0,
            "highest_bid_identified": False,
            "bid_ordering_correct": False,
            "all_bids_active": False,
            "error_messages": [],
            "success": False
        }
        
        # Get all tenders for the listing
        tenders_result = await self.make_request(f"/listings/{listing_id}/tenders")
        
        if tenders_result["success"]:
            tenders = tenders_result.get("data", [])
            test_results["tenders_count"] = len(tenders)
            print(f"    📊 Found {len(tenders)} active tenders for listing")
            
            if tenders:
                # Check if tenders are ordered by offer_amount (highest first)
                tender_amounts = [tender.get("offer_amount", 0) for tender in tenders]
                sorted_amounts = sorted(tender_amounts, reverse=True)
                
                if tender_amounts == sorted_amounts:
                    test_results["bid_ordering_correct"] = True
                    print(f"    ✅ Tenders correctly ordered by amount: {tender_amounts}")
                else:
                    test_results["error_messages"].append(f"Tenders not ordered correctly: {tender_amounts} vs {sorted_amounts}")
                    print(f"    ❌ Tenders not ordered correctly: {tender_amounts} vs {sorted_amounts}")
                
                # Check if highest bid is identified correctly
                if tenders[0].get("offer_amount") == max(tender_amounts):
                    test_results["highest_bid_identified"] = True
                    highest_bidder = tenders[0].get("buyer_id")
                    highest_amount = tenders[0].get("offer_amount")
                    print(f"    ✅ Highest bid correctly identified: €{highest_amount} by {highest_bidder}")
                else:
                    test_results["error_messages"].append("Highest bid not correctly identified")
                    print(f"    ❌ Highest bid not correctly identified")
                
                # Check if all tenders are active
                active_tenders = [tender for tender in tenders if tender.get("status") == "active"]
                if len(active_tenders) == len(tenders):
                    test_results["all_bids_active"] = True
                    print(f"    ✅ All {len(tenders)} tenders are active")
                else:
                    test_results["error_messages"].append(f"Not all tenders are active: {len(active_tenders)}/{len(tenders)}")
                    print(f"    ❌ Not all tenders are active: {len(active_tenders)}/{len(tenders)}")
            else:
                test_results["error_messages"].append("No tenders found for listing")
                print(f"    ❌ No tenders found for listing")
        else:
            test_results["error_messages"].append(f"Failed to get listing tenders: {tenders_result.get('error', 'Unknown error')}")
            print(f"    ❌ Failed to get listing tenders: {tenders_result.get('error', 'Unknown error')}")
        
        # Determine overall success
        test_results["success"] = (
            test_results["tenders_count"] > 0 and
            test_results["highest_bid_identified"] and
            test_results["bid_ordering_correct"] and
            test_results["all_bids_active"]
        )
        
        return {
            "test_name": "Bid Flow Validation",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def run_highest_bidder_tests(self) -> Dict:
        """
        Run complete highest bidder functionality tests
        """
        print("🚨 STARTING HIGHEST BIDDER FUNCTIONALITY TESTING")
        print("=" * 80)
        print("TESTING: Highest bidder functionality fix on individual listing page")
        print("ISSUE: Individual listing page does not show highest bidder functionality")
        print("ISSUE: User is able to place a bid although he is already the highest bidder")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate users
            auth_success = await self.authenticate_users()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "User authentication failed - cannot proceed with testing"
                }
            
            # Create test listing
            listing_result = await self.create_test_listing()
            if "error" in listing_result:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": listing_result["error"]
                }
            
            listing_id = listing_result["listing_id"]
            
            # Create multiple bids
            bids_result = await self.create_multiple_bids(listing_id)
            if not bids_result["success"]:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Failed to create test bids"
                }
            
            expected_highest_bidder = bids_result["expected_highest_bidder"]
            expected_highest_bid = bids_result["expected_highest_bid"]
            
            # Run all highest bidder tests
            data_structure_test = await self.test_individual_listing_data_structure(
                listing_id, expected_highest_bidder, expected_highest_bid
            )
            
            blocking_test = await self.test_tender_submission_blocking(
                listing_id, expected_highest_bidder
            )
            
            bid_flow_test = await self.test_bid_flow_validation(listing_id)
            
            # Compile comprehensive test results
            test_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_focus": "Highest bidder functionality fix on individual listing page",
                "test_listing_id": listing_id,
                "bids_created": bids_result["bids_created"],
                "expected_highest_bidder": expected_highest_bidder,
                "expected_highest_bid": expected_highest_bid,
                "individual_listing_data_structure_test": data_structure_test,
                "tender_submission_blocking_test": blocking_test,
                "bid_flow_validation_test": bid_flow_test
            }
            
            # Determine critical findings
            critical_issues = []
            working_features = []
            
            tests = [data_structure_test, blocking_test, bid_flow_test]
            
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
            
            test_results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": success_rate,
                "critical_issues": critical_issues,
                "working_features": working_features,
                "highest_bidder_functionality_working": len(critical_issues) == 0
            }
            
            return test_results
            
        finally:
            await self.cleanup()


async def main():
    """Run the highest bidder functionality tests"""
    tester = HighestBidderTester()
    results = await tester.run_highest_bidder_tests()
    
    print("\n" + "=" * 80)
    print("🏁 HIGHEST BIDDER FUNCTIONALITY TESTING RESULTS")
    print("=" * 80)
    
    if "error" in results:
        print(f"❌ TESTING FAILED: {results['error']}")
        return
    
    summary = results.get("summary", {})
    
    print(f"📊 SUMMARY:")
    print(f"   Total Tests: {summary.get('total_tests', 0)}")
    print(f"   Successful: {summary.get('successful_tests', 0)}")
    print(f"   Failed: {summary.get('failed_tests', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
    
    if summary.get("highest_bidder_functionality_working", False):
        print(f"\n✅ HIGHEST BIDDER FUNCTIONALITY: ALL TESTS PASSED")
        print(f"   ✅ Individual listing shows highest_bidder_id correctly")
        print(f"   ✅ Tender submission blocking works for highest bidder")
        print(f"   ✅ Bid flow validation working correctly")
    else:
        print(f"\n❌ HIGHEST BIDDER FUNCTIONALITY: ISSUES FOUND")
        for issue in summary.get("critical_issues", []):
            print(f"   ❌ {issue}")
    
    print(f"\n🔧 WORKING FEATURES:")
    for feature in summary.get("working_features", []):
        print(f"   ✅ {feature}")
    
    print(f"\n📋 TEST DETAILS:")
    print(f"   Test Listing ID: {results.get('test_listing_id', 'N/A')}")
    print(f"   Bids Created: {len(results.get('bids_created', []))}")
    print(f"   Expected Highest Bidder: {results.get('expected_highest_bidder', 'N/A')}")
    print(f"   Expected Highest Bid: €{results.get('expected_highest_bid', 0)}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())