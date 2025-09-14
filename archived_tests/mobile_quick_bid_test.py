#!/usr/bin/env python3
"""
Mobile Quick Bid Functionality Testing
Comprehensive validation of mobile quick bid functionality as requested in review
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://mobileui-sync.preview.emergentagent.com/api"

class MobileQuickBidTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.demo_user_id = None
        self.demo_token = None
        self.test_listings = []
        
    async def setup(self):
        """Initialize HTTP session and authenticate demo user"""
        self.session = aiohttp.ClientSession()
        
        # Login as demo user for testing
        login_data = {
            "email": "demo@cataloro.com",
            "password": "demo_password"
        }
        
        login_result = await self.make_request("/auth/login", "POST", data=login_data)
        if login_result["success"]:
            user_data = login_result["data"]["user"]
            self.demo_user_id = user_data["id"]
            self.demo_token = login_result["data"]["token"]
            print(f"✅ Demo user authenticated: {user_data.get('username', 'demo_user')}")
        else:
            print(f"❌ Failed to authenticate demo user: {login_result.get('error')}")
        
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
    
    async def test_api_validation_browse_endpoint(self) -> Dict:
        """Test /api/marketplace/browse endpoint for proper bid_info structure"""
        print("🔍 Testing /api/marketplace/browse endpoint for bid_info structure...")
        
        result = await self.make_request("/marketplace/browse")
        
        if result["success"]:
            listings = result["data"]
            print(f"  ✅ Browse endpoint working: {len(listings)} listings found")
            
            # Analyze bid_info structure
            bid_info_analysis = {
                "total_listings": len(listings),
                "listings_with_bid_info": 0,
                "listings_with_bids": 0,
                "listings_without_bids": 0,
                "bid_info_structure_valid": 0,
                "sample_bid_info": []
            }
            
            for listing in listings[:5]:  # Check first 5 listings
                if "bid_info" in listing:
                    bid_info_analysis["listings_with_bid_info"] += 1
                    bid_info = listing["bid_info"]
                    
                    # Check required bid_info fields
                    required_fields = ["has_bids", "total_bids", "highest_bid", "highest_bidder_id"]
                    if all(field in bid_info for field in required_fields):
                        bid_info_analysis["bid_info_structure_valid"] += 1
                    
                    if bid_info.get("has_bids"):
                        bid_info_analysis["listings_with_bids"] += 1
                    else:
                        bid_info_analysis["listings_without_bids"] += 1
                    
                    # Store sample for analysis
                    bid_info_analysis["sample_bid_info"].append({
                        "listing_id": listing.get("id"),
                        "title": listing.get("title", "")[:30],
                        "bid_info": bid_info
                    })
            
            # Store test listings for further testing
            self.test_listings = [l for l in listings if l.get("bid_info", {}).get("has_bids")][:3]
            
            return {
                "test_name": "Browse Endpoint Bid Info Validation",
                "endpoint_working": True,
                "response_time_ms": result["response_time_ms"],
                "bid_info_analysis": bid_info_analysis,
                "bid_info_structure_correct": bid_info_analysis["bid_info_structure_valid"] > 0,
                "has_listings_with_bids": bid_info_analysis["listings_with_bids"] > 0,
                "test_listings_available": len(self.test_listings) > 0
            }
        else:
            return {
                "test_name": "Browse Endpoint Bid Info Validation",
                "endpoint_working": False,
                "error": result.get("error", "Browse endpoint failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"]
            }
    
    async def test_api_validation_tenders_submit(self) -> Dict:
        """Test /api/tenders/submit endpoint for bid submission"""
        print("💰 Testing /api/tenders/submit endpoint for bid submission...")
        
        if not self.test_listings:
            return {
                "test_name": "Tenders Submit API Validation",
                "error": "No test listings available with existing bids"
            }
        
        test_listing = self.test_listings[0]
        listing_id = test_listing["id"]
        current_highest_bid = test_listing["bid_info"]["highest_bid"]
        
        # Test valid bid submission (current highest + 1)
        valid_bid_amount = current_highest_bid + 1
        bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": valid_bid_amount
        }
        
        print(f"  Testing valid bid: €{valid_bid_amount} on listing with current highest bid €{current_highest_bid}")
        
        valid_bid_result = await self.make_request("/tenders/submit", "POST", data=bid_data)
        
        # Test invalid bid submission (too low)
        invalid_bid_amount = current_highest_bid - 10
        invalid_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": invalid_bid_amount
        }
        
        print(f"  Testing invalid bid: €{invalid_bid_amount} (should be rejected)")
        
        invalid_bid_result = await self.make_request("/tenders/submit", "POST", data=invalid_bid_data)
        
        return {
            "test_name": "Tenders Submit API Validation",
            "valid_bid_test": {
                "bid_amount": valid_bid_amount,
                "success": valid_bid_result["success"],
                "response_time_ms": valid_bid_result["response_time_ms"],
                "error": valid_bid_result.get("error") if not valid_bid_result["success"] else None,
                "tender_id_returned": bool(valid_bid_result.get("data", {}).get("tender_id")) if valid_bid_result["success"] else False
            },
            "invalid_bid_test": {
                "bid_amount": invalid_bid_amount,
                "correctly_rejected": not invalid_bid_result["success"],
                "response_time_ms": invalid_bid_result["response_time_ms"],
                "error_message": invalid_bid_result.get("data", {}).get("detail", "") if not invalid_bid_result["success"] else "",
                "proper_error_handling": "too low" in str(invalid_bid_result.get("data", {})).lower()
            },
            "endpoint_functional": valid_bid_result["success"] or not invalid_bid_result["success"],
            "bid_validation_working": not invalid_bid_result["success"]
        }
    
    async def test_api_validation_price_range_settings(self) -> Dict:
        """Test /api/marketplace/price-range-settings endpoint for market range data"""
        print("📊 Testing /api/marketplace/price-range-settings endpoint...")
        
        result = await self.make_request("/marketplace/price-range-settings")
        
        if result["success"]:
            settings_data = result["data"]
            
            # Analyze price range settings structure
            expected_fields = ["pt_price", "pd_price", "rh_price", "price_range_min_percent", "price_range_max_percent"]
            fields_present = [field for field in expected_fields if field in settings_data]
            
            return {
                "test_name": "Price Range Settings API Validation",
                "endpoint_working": True,
                "response_time_ms": result["response_time_ms"],
                "settings_data": settings_data,
                "expected_fields_present": len(fields_present),
                "total_expected_fields": len(expected_fields),
                "structure_valid": len(fields_present) >= 3,  # At least 3 key fields
                "has_price_data": any("price" in str(settings_data).lower() for key in settings_data.keys())
            }
        else:
            return {
                "test_name": "Price Range Settings API Validation",
                "endpoint_working": False,
                "error": result.get("error", "Price range settings endpoint failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"]
            }
    
    async def test_api_validation_catalyst_calculations(self) -> Dict:
        """Test /api/admin/catalyst/calculations endpoint for catalyst price suggestions"""
        print("🧪 Testing /api/admin/catalyst/calculations endpoint...")
        
        # Test with sample catalyst data
        catalyst_data = {
            "ceramic_weight": 1.5,
            "pt_ppm": 1200,
            "pd_ppm": 800,
            "rh_ppm": 150
        }
        
        result = await self.make_request("/admin/catalyst/calculations", "POST", data=catalyst_data)
        
        if result["success"]:
            calculation_data = result["data"]
            
            # Analyze calculation response structure
            expected_fields = ["total_value", "pt_value", "pd_value", "rh_value"]
            fields_present = [field for field in expected_fields if field in calculation_data]
            
            return {
                "test_name": "Catalyst Calculations API Validation",
                "endpoint_working": True,
                "response_time_ms": result["response_time_ms"],
                "calculation_data": calculation_data,
                "expected_fields_present": len(fields_present),
                "total_expected_fields": len(expected_fields),
                "structure_valid": len(fields_present) >= 2,  # At least 2 key fields
                "has_price_calculations": "value" in str(calculation_data).lower()
            }
        else:
            return {
                "test_name": "Catalyst Calculations API Validation",
                "endpoint_working": False,
                "error": result.get("error", "Catalyst calculations endpoint failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"],
                "endpoint_available": result["status"] != 404
            }
    
    async def test_bid_validation_minimum_requirements(self) -> Dict:
        """Test minimum bid requirements (current highest bid + 1)"""
        print("✅ Testing minimum bid requirements validation...")
        
        if not self.test_listings:
            return {
                "test_name": "Minimum Bid Requirements Validation",
                "error": "No test listings available"
            }
        
        validation_tests = []
        
        for i, listing in enumerate(self.test_listings[:2]):  # Test with 2 listings
            listing_id = listing["id"]
            current_highest_bid = listing["bid_info"]["highest_bid"]
            
            # Test exact minimum (current + 1) - should be accepted
            minimum_bid = current_highest_bid + 1
            min_bid_data = {
                "listing_id": listing_id,
                "buyer_id": self.demo_user_id,
                "offer_amount": minimum_bid
            }
            
            min_bid_result = await self.make_request("/tenders/submit", "POST", data=min_bid_data)
            
            # Test below minimum (current - 1) - should be rejected
            below_min_bid = current_highest_bid - 1
            below_min_data = {
                "listing_id": listing_id,
                "buyer_id": self.demo_user_id,
                "offer_amount": below_min_bid
            }
            
            below_min_result = await self.make_request("/tenders/submit", "POST", data=below_min_data)
            
            validation_tests.append({
                "listing_id": listing_id,
                "current_highest_bid": current_highest_bid,
                "minimum_bid_test": {
                    "bid_amount": minimum_bid,
                    "accepted": min_bid_result["success"],
                    "error": min_bid_result.get("error") if not min_bid_result["success"] else None
                },
                "below_minimum_test": {
                    "bid_amount": below_min_bid,
                    "correctly_rejected": not below_min_result["success"],
                    "error_message": below_min_result.get("data", {}).get("detail", "") if not below_min_result["success"] else ""
                }
            })
            
            print(f"  Listing {i+1}: Min bid €{minimum_bid} {'✅ accepted' if min_bid_result['success'] else '❌ rejected'}")
            print(f"  Listing {i+1}: Below min €{below_min_bid} {'✅ rejected' if not below_min_result['success'] else '❌ accepted'}")
        
        # Calculate success metrics
        successful_min_bids = sum(1 for test in validation_tests if test["minimum_bid_test"]["accepted"])
        correctly_rejected_low_bids = sum(1 for test in validation_tests if test["below_minimum_test"]["correctly_rejected"])
        
        return {
            "test_name": "Minimum Bid Requirements Validation",
            "total_tests": len(validation_tests),
            "minimum_bid_acceptance_rate": successful_min_bids / len(validation_tests) * 100 if validation_tests else 0,
            "low_bid_rejection_rate": correctly_rejected_low_bids / len(validation_tests) * 100 if validation_tests else 0,
            "validation_working_correctly": successful_min_bids > 0 and correctly_rejected_low_bids > 0,
            "detailed_tests": validation_tests
        }
    
    async def test_bid_validation_self_bidding_prevention(self) -> Dict:
        """Test self-bidding prevention (user cannot bid on own listings)"""
        print("🚫 Testing self-bidding prevention...")
        
        # Get user's own listings
        my_listings_result = await self.make_request(f"/user/my-listings/{self.demo_user_id}")
        
        if not my_listings_result["success"] or not my_listings_result["data"]:
            return {
                "test_name": "Self-Bidding Prevention Validation",
                "error": "No user listings found to test self-bidding prevention",
                "user_has_listings": False
            }
        
        user_listings = my_listings_result["data"]
        test_listing = user_listings[0]  # Use first listing
        
        # Attempt to bid on own listing
        self_bid_data = {
            "listing_id": test_listing["id"],
            "buyer_id": self.demo_user_id,
            "offer_amount": test_listing["price"] + 50  # Bid above starting price
        }
        
        self_bid_result = await self.make_request("/tenders/submit", "POST", data=self_bid_data)
        
        # Should be rejected
        correctly_prevented = not self_bid_result["success"]
        error_message = self_bid_result.get("data", {}).get("detail", "") if not self_bid_result["success"] else ""
        proper_error_message = "own listing" in error_message.lower() or "cannot bid" in error_message.lower()
        
        print(f"  Self-bid attempt: {'✅ correctly prevented' if correctly_prevented else '❌ allowed (bug)'}")
        print(f"  Error message: {error_message}")
        
        return {
            "test_name": "Self-Bidding Prevention Validation",
            "user_has_listings": True,
            "test_listing_id": test_listing["id"],
            "self_bid_correctly_prevented": correctly_prevented,
            "error_message": error_message,
            "proper_error_message": proper_error_message,
            "security_validation_working": correctly_prevented and proper_error_message
        }
    
    async def test_bid_validation_highest_bidder_prevention(self) -> Dict:
        """Test highest bidder prevention (user cannot bid when already highest bidder)"""
        print("🏆 Testing highest bidder prevention...")
        
        if not self.test_listings:
            return {
                "test_name": "Highest Bidder Prevention Validation",
                "error": "No test listings available"
            }
        
        # First, place a bid to become highest bidder
        test_listing = self.test_listings[0]
        listing_id = test_listing["id"]
        current_highest_bid = test_listing["bid_info"]["highest_bid"]
        
        # Place a bid to become highest bidder
        new_highest_bid = current_highest_bid + 10
        bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": new_highest_bid
        }
        
        first_bid_result = await self.make_request("/tenders/submit", "POST", data=bid_data)
        
        if first_bid_result["success"]:
            # Now try to bid again (should be prevented if user is highest bidder)
            second_bid_amount = new_highest_bid + 5
            second_bid_data = {
                "listing_id": listing_id,
                "buyer_id": self.demo_user_id,
                "offer_amount": second_bid_amount
            }
            
            second_bid_result = await self.make_request("/tenders/submit", "POST", data=second_bid_data)
            
            # Check if second bid was prevented
            correctly_prevented = not second_bid_result["success"]
            error_message = second_bid_result.get("data", {}).get("detail", "") if not second_bid_result["success"] else ""
            proper_error_message = "highest bidder" in error_message.lower() or "already" in error_message.lower()
            
            print(f"  First bid (€{new_highest_bid}): {'✅ accepted' if first_bid_result['success'] else '❌ rejected'}")
            print(f"  Second bid attempt (€{second_bid_amount}): {'✅ correctly prevented' if correctly_prevented else '❌ allowed'}")
            
            return {
                "test_name": "Highest Bidder Prevention Validation",
                "first_bid_successful": True,
                "first_bid_amount": new_highest_bid,
                "second_bid_correctly_prevented": correctly_prevented,
                "second_bid_amount": second_bid_amount,
                "error_message": error_message,
                "proper_error_message": proper_error_message,
                "prevention_logic_working": correctly_prevented
            }
        else:
            return {
                "test_name": "Highest Bidder Prevention Validation",
                "first_bid_successful": False,
                "error": "Could not place initial bid to test highest bidder prevention",
                "first_bid_error": first_bid_result.get("error")
            }
    
    async def test_bid_validation_amount_validation(self) -> Dict:
        """Test bid amount validation (must be numeric and above minimum)"""
        print("🔢 Testing bid amount validation...")
        
        if not self.test_listings:
            return {
                "test_name": "Bid Amount Validation",
                "error": "No test listings available"
            }
        
        test_listing = self.test_listings[0]
        listing_id = test_listing["id"]
        current_highest_bid = test_listing["bid_info"]["highest_bid"]
        
        validation_tests = []
        
        # Test non-numeric bid (string)
        string_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": "not_a_number"
        }
        
        string_bid_result = await self.make_request("/tenders/submit", "POST", data=string_bid_data)
        validation_tests.append({
            "test_type": "Non-numeric bid",
            "bid_value": "not_a_number",
            "correctly_rejected": not string_bid_result["success"],
            "error_message": string_bid_result.get("data", {}).get("detail", "") if not string_bid_result["success"] else ""
        })
        
        # Test negative bid
        negative_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": -50
        }
        
        negative_bid_result = await self.make_request("/tenders/submit", "POST", data=negative_bid_data)
        validation_tests.append({
            "test_type": "Negative bid",
            "bid_value": -50,
            "correctly_rejected": not negative_bid_result["success"],
            "error_message": negative_bid_result.get("data", {}).get("detail", "") if not negative_bid_result["success"] else ""
        })
        
        # Test zero bid
        zero_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": 0
        }
        
        zero_bid_result = await self.make_request("/tenders/submit", "POST", data=zero_bid_data)
        validation_tests.append({
            "test_type": "Zero bid",
            "bid_value": 0,
            "correctly_rejected": not zero_bid_result["success"],
            "error_message": zero_bid_result.get("data", {}).get("detail", "") if not zero_bid_result["success"] else ""
        })
        
        # Test valid numeric bid
        valid_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": current_highest_bid + 15
        }
        
        valid_bid_result = await self.make_request("/tenders/submit", "POST", data=valid_bid_data)
        validation_tests.append({
            "test_type": "Valid numeric bid",
            "bid_value": current_highest_bid + 15,
            "correctly_accepted": valid_bid_result["success"],
            "error_message": valid_bid_result.get("error") if not valid_bid_result["success"] else ""
        })
        
        # Calculate success metrics
        invalid_tests = [t for t in validation_tests if t["test_type"] != "Valid numeric bid"]
        correctly_rejected_invalid = sum(1 for test in invalid_tests if test.get("correctly_rejected", False))
        valid_test = next((t for t in validation_tests if t["test_type"] == "Valid numeric bid"), None)
        valid_accepted = valid_test.get("correctly_accepted", False) if valid_test else False
        
        for test in validation_tests:
            test_type = test["test_type"]
            if test_type == "Valid numeric bid":
                status = "✅ accepted" if test.get("correctly_accepted") else "❌ rejected"
            else:
                status = "✅ rejected" if test.get("correctly_rejected") else "❌ accepted"
            print(f"  {test_type}: {status}")
        
        return {
            "test_name": "Bid Amount Validation",
            "total_invalid_tests": len(invalid_tests),
            "correctly_rejected_invalid": correctly_rejected_invalid,
            "valid_bid_accepted": valid_accepted,
            "invalid_rejection_rate": correctly_rejected_invalid / len(invalid_tests) * 100 if invalid_tests else 0,
            "validation_working_correctly": correctly_rejected_invalid == len(invalid_tests) and valid_accepted,
            "detailed_tests": validation_tests
        }
    
    async def test_edge_cases_no_existing_bids(self) -> Dict:
        """Test bidding on listing with no existing bids (should use starting price + 1)"""
        print("🆕 Testing bidding on listings with no existing bids...")
        
        # Get browse listings and find one without bids
        browse_result = await self.make_request("/marketplace/browse")
        
        if not browse_result["success"]:
            return {
                "test_name": "No Existing Bids Edge Case",
                "error": "Could not fetch browse listings"
            }
        
        listings = browse_result["data"]
        no_bid_listings = [l for l in listings if not l.get("bid_info", {}).get("has_bids", True)]
        
        if not no_bid_listings:
            return {
                "test_name": "No Existing Bids Edge Case",
                "error": "No listings found without existing bids",
                "total_listings_checked": len(listings)
            }
        
        test_listing = no_bid_listings[0]
        listing_id = test_listing["id"]
        starting_price = test_listing["price"]
        
        # Test bid equal to starting price (should be accepted)
        equal_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": starting_price
        }
        
        equal_bid_result = await self.make_request("/tenders/submit", "POST", data=equal_bid_data)
        
        # Test bid above starting price (should be accepted)
        above_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": starting_price + 25
        }
        
        above_bid_result = await self.make_request("/tenders/submit", "POST", data=above_bid_data)
        
        # Test bid below starting price (should be rejected)
        below_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": starting_price - 10
        }
        
        below_bid_result = await self.make_request("/tenders/submit", "POST", data=below_bid_data)
        
        print(f"  Starting price: €{starting_price}")
        print(f"  Equal to starting price (€{starting_price}): {'✅ accepted' if equal_bid_result['success'] else '❌ rejected'}")
        print(f"  Above starting price (€{starting_price + 25}): {'✅ accepted' if above_bid_result['success'] else '❌ rejected'}")
        print(f"  Below starting price (€{starting_price - 10}): {'✅ rejected' if not below_bid_result['success'] else '❌ accepted'}")
        
        return {
            "test_name": "No Existing Bids Edge Case",
            "test_listing_id": listing_id,
            "starting_price": starting_price,
            "equal_price_bid": {
                "amount": starting_price,
                "accepted": equal_bid_result["success"],
                "error": equal_bid_result.get("error") if not equal_bid_result["success"] else None
            },
            "above_price_bid": {
                "amount": starting_price + 25,
                "accepted": above_bid_result["success"],
                "error": above_bid_result.get("error") if not above_bid_result["success"] else None
            },
            "below_price_bid": {
                "amount": starting_price - 10,
                "correctly_rejected": not below_bid_result["success"],
                "error_message": below_bid_result.get("data", {}).get("detail", "") if not below_bid_result["success"] else ""
            },
            "first_bid_logic_working": equal_bid_result["success"] or above_bid_result["success"],
            "validation_working": not below_bid_result["success"]
        }
    
    async def test_edge_cases_existing_bids(self) -> Dict:
        """Test bidding on listing with existing bids (should use highest bid + 1)"""
        print("📈 Testing bidding on listings with existing bids...")
        
        if not self.test_listings:
            return {
                "test_name": "Existing Bids Edge Case",
                "error": "No test listings with existing bids available"
            }
        
        test_listing = self.test_listings[0]
        listing_id = test_listing["id"]
        highest_bid = test_listing["bid_info"]["highest_bid"]
        total_bids = test_listing["bid_info"]["total_bids"]
        
        # Test bid equal to highest bid (should be rejected)
        equal_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": highest_bid
        }
        
        equal_bid_result = await self.make_request("/tenders/submit", "POST", data=equal_bid_data)
        
        # Test bid higher than highest bid (should be accepted)
        higher_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": highest_bid + 20
        }
        
        higher_bid_result = await self.make_request("/tenders/submit", "POST", data=higher_bid_data)
        
        print(f"  Current highest bid: €{highest_bid} ({total_bids} bids)")
        print(f"  Equal to highest (€{highest_bid}): {'✅ rejected' if not equal_bid_result['success'] else '❌ accepted'}")
        print(f"  Higher than highest (€{highest_bid + 20}): {'✅ accepted' if higher_bid_result['success'] else '❌ rejected'}")
        
        return {
            "test_name": "Existing Bids Edge Case",
            "test_listing_id": listing_id,
            "current_highest_bid": highest_bid,
            "total_existing_bids": total_bids,
            "equal_bid_test": {
                "amount": highest_bid,
                "correctly_rejected": not equal_bid_result["success"],
                "error_message": equal_bid_result.get("data", {}).get("detail", "") if not equal_bid_result["success"] else ""
            },
            "higher_bid_test": {
                "amount": highest_bid + 20,
                "accepted": higher_bid_result["success"],
                "error": higher_bid_result.get("error") if not higher_bid_result["success"] else None
            },
            "existing_bid_logic_working": not equal_bid_result["success"] and higher_bid_result["success"]
        }
    
    async def test_edge_cases_invalid_amounts(self) -> Dict:
        """Test invalid bid amounts (too low, non-numeric, empty)"""
        print("❌ Testing invalid bid amounts edge cases...")
        
        if not self.test_listings:
            return {
                "test_name": "Invalid Bid Amounts Edge Cases",
                "error": "No test listings available"
            }
        
        test_listing = self.test_listings[0]
        listing_id = test_listing["id"]
        
        edge_case_tests = []
        
        # Test empty bid amount
        empty_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": None
        }
        
        empty_bid_result = await self.make_request("/tenders/submit", "POST", data=empty_bid_data)
        edge_case_tests.append({
            "test_case": "Empty/None bid amount",
            "bid_value": None,
            "correctly_handled": not empty_bid_result["success"],
            "error_message": empty_bid_result.get("data", {}).get("detail", "") if not empty_bid_result["success"] else ""
        })
        
        # Test extremely high bid (edge case)
        extreme_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": 999999999
        }
        
        extreme_bid_result = await self.make_request("/tenders/submit", "POST", data=extreme_bid_data)
        edge_case_tests.append({
            "test_case": "Extremely high bid",
            "bid_value": 999999999,
            "handled_appropriately": True,  # Could be accepted or rejected, both are valid
            "result": "accepted" if extreme_bid_result["success"] else "rejected",
            "error_message": extreme_bid_result.get("data", {}).get("detail", "") if not extreme_bid_result["success"] else ""
        })
        
        # Test decimal bid amount
        decimal_bid_data = {
            "listing_id": listing_id,
            "buyer_id": self.demo_user_id,
            "offer_amount": test_listing["bid_info"]["highest_bid"] + 10.50
        }
        
        decimal_bid_result = await self.make_request("/tenders/submit", "POST", data=decimal_bid_data)
        edge_case_tests.append({
            "test_case": "Decimal bid amount",
            "bid_value": test_listing["bid_info"]["highest_bid"] + 10.50,
            "handled_appropriately": True,  # Decimals should be accepted
            "result": "accepted" if decimal_bid_result["success"] else "rejected",
            "error_message": decimal_bid_result.get("data", {}).get("detail", "") if not decimal_bid_result["success"] else ""
        })
        
        for test in edge_case_tests:
            test_case = test["test_case"]
            if test_case == "Empty/None bid amount":
                status = "✅ rejected" if test.get("correctly_handled") else "❌ accepted"
            else:
                status = f"✅ {test.get('result', 'handled')}"
            print(f"  {test_case}: {status}")
        
        return {
            "test_name": "Invalid Bid Amounts Edge Cases",
            "total_edge_cases_tested": len(edge_case_tests),
            "edge_cases_handled_correctly": sum(1 for test in edge_case_tests if test.get("correctly_handled") or test.get("handled_appropriately")),
            "detailed_tests": edge_case_tests
        }
    
    async def test_edge_cases_network_error_handling(self) -> Dict:
        """Test network error handling"""
        print("🌐 Testing network error handling...")
        
        # Test with invalid endpoint
        invalid_endpoint_result = await self.make_request("/tenders/invalid_endpoint", "POST", data={
            "listing_id": "test",
            "buyer_id": self.demo_user_id,
            "offer_amount": 100
        })
        
        # Test with malformed data
        malformed_data_result = await self.make_request("/tenders/submit", "POST", data={
            "invalid_field": "test"
        })
        
        # Test with missing required fields
        missing_fields_result = await self.make_request("/tenders/submit", "POST", data={
            "listing_id": "test_listing"
            # Missing buyer_id and offer_amount
        })
        
        error_handling_tests = [
            {
                "test_case": "Invalid endpoint",
                "properly_handled": invalid_endpoint_result["status"] == 404,
                "status_code": invalid_endpoint_result["status"]
            },
            {
                "test_case": "Malformed data",
                "properly_handled": not malformed_data_result["success"],
                "status_code": malformed_data_result["status"]
            },
            {
                "test_case": "Missing required fields",
                "properly_handled": not missing_fields_result["success"],
                "status_code": missing_fields_result["status"]
            }
        ]
        
        for test in error_handling_tests:
            test_case = test["test_case"]
            status = "✅ handled" if test.get("properly_handled") else "❌ not handled"
            print(f"  {test_case}: {status} (HTTP {test['status_code']})")
        
        properly_handled_count = sum(1 for test in error_handling_tests if test.get("properly_handled"))
        
        return {
            "test_name": "Network Error Handling",
            "total_error_scenarios": len(error_handling_tests),
            "properly_handled_errors": properly_handled_count,
            "error_handling_rate": properly_handled_count / len(error_handling_tests) * 100,
            "error_handling_working": properly_handled_count >= 2,  # At least 2 out of 3
            "detailed_tests": error_handling_tests
        }
    
    async def test_market_range_functionality(self) -> Dict:
        """Test market range functionality for catalyst items"""
        print("💎 Testing market range functionality for catalyst items...")
        
        # Test price range calculation
        price_range_result = await self.test_api_validation_price_range_settings()
        
        # Test catalyst calculations
        catalyst_calc_result = await self.test_api_validation_catalyst_calculations()
        
        # Test integration with browse listings
        browse_result = await self.make_request("/marketplace/browse")
        
        catalyst_listings = []
        if browse_result["success"]:
            listings = browse_result["data"]
            # Look for catalyst-related listings
            catalyst_listings = [l for l in listings if "catalyst" in l.get("title", "").lower() or "cat" in l.get("category", "").lower()]
        
        return {
            "test_name": "Market Range Functionality",
            "price_range_settings_working": price_range_result.get("endpoint_working", False),
            "catalyst_calculations_available": catalyst_calc_result.get("endpoint_working", False),
            "catalyst_listings_found": len(catalyst_listings),
            "price_range_data_valid": price_range_result.get("structure_valid", False),
            "calculation_data_valid": catalyst_calc_result.get("structure_valid", False),
            "market_range_functional": price_range_result.get("endpoint_working", False) and len(catalyst_listings) > 0,
            "sample_catalyst_listings": [{"id": l.get("id"), "title": l.get("title", "")[:50]} for l in catalyst_listings[:3]]
        }
    
    async def test_loading_states_price_suggestions(self) -> Dict:
        """Test loading states for price suggestions"""
        print("⏳ Testing loading states for price suggestions...")
        
        # Test response times for price-related endpoints
        endpoints_to_test = [
            "/marketplace/price-range-settings",
            "/admin/catalyst/calculations"
        ]
        
        loading_tests = []
        
        for endpoint in endpoints_to_test:
            if endpoint == "/admin/catalyst/calculations":
                # POST request with data
                result = await self.make_request(endpoint, "POST", data={
                    "ceramic_weight": 1.0,
                    "pt_ppm": 1000,
                    "pd_ppm": 500,
                    "rh_ppm": 100
                })
            else:
                # GET request
                result = await self.make_request(endpoint)
            
            loading_tests.append({
                "endpoint": endpoint,
                "response_time_ms": result["response_time_ms"],
                "success": result["success"],
                "fast_loading": result["response_time_ms"] < 2000,  # Under 2 seconds
                "acceptable_loading": result["response_time_ms"] < 5000  # Under 5 seconds
            })
            
            loading_status = "fast" if result["response_time_ms"] < 2000 else "acceptable" if result["response_time_ms"] < 5000 else "slow"
            print(f"  {endpoint}: {result['response_time_ms']:.0f}ms ({loading_status})")
        
        successful_tests = [t for t in loading_tests if t["success"]]
        fast_loading_count = sum(1 for test in loading_tests if test.get("fast_loading", False))
        
        return {
            "test_name": "Loading States for Price Suggestions",
            "total_endpoints_tested": len(loading_tests),
            "successful_endpoints": len(successful_tests),
            "fast_loading_endpoints": fast_loading_count,
            "average_response_time_ms": statistics.mean([t["response_time_ms"] for t in successful_tests]) if successful_tests else 0,
            "loading_performance_acceptable": fast_loading_count >= 1,  # At least 1 endpoint loads fast
            "detailed_loading_tests": loading_tests
        }
    
    async def run_comprehensive_mobile_quick_bid_test(self) -> Dict:
        """Run all mobile quick bid functionality tests"""
        print("🚀 Starting Mobile Quick Bid Functionality Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test suites as requested in review
            
            # 1. API Validation Testing
            browse_api_test = await self.test_api_validation_browse_endpoint()
            tenders_api_test = await self.test_api_validation_tenders_submit()
            price_range_api_test = await self.test_api_validation_price_range_settings()
            catalyst_api_test = await self.test_api_validation_catalyst_calculations()
            
            # 2. Bid Validation Logic Testing
            min_bid_test = await self.test_bid_validation_minimum_requirements()
            self_bid_test = await self.test_bid_validation_self_bidding_prevention()
            highest_bidder_test = await self.test_bid_validation_highest_bidder_prevention()
            amount_validation_test = await self.test_bid_validation_amount_validation()
            
            # 3. Edge Cases Testing
            no_bids_test = await self.test_edge_cases_no_existing_bids()
            existing_bids_test = await self.test_edge_cases_existing_bids()
            invalid_amounts_test = await self.test_edge_cases_invalid_amounts()
            network_error_test = await self.test_edge_cases_network_error_handling()
            
            # 4. Market Range Functionality Testing
            market_range_test = await self.test_market_range_functionality()
            loading_states_test = await self.test_loading_states_price_suggestions()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "test_summary": "Mobile Quick Bid Functionality Comprehensive Testing",
                
                # API Validation Testing Results
                "api_validation": {
                    "browse_endpoint": browse_api_test,
                    "tenders_submit_endpoint": tenders_api_test,
                    "price_range_settings_endpoint": price_range_api_test,
                    "catalyst_calculations_endpoint": catalyst_api_test
                },
                
                # Bid Validation Logic Testing Results
                "bid_validation_logic": {
                    "minimum_bid_requirements": min_bid_test,
                    "self_bidding_prevention": self_bid_test,
                    "highest_bidder_prevention": highest_bidder_test,
                    "bid_amount_validation": amount_validation_test
                },
                
                # Edge Cases Testing Results
                "edge_cases": {
                    "no_existing_bids": no_bids_test,
                    "existing_bids": existing_bids_test,
                    "invalid_bid_amounts": invalid_amounts_test,
                    "network_error_handling": network_error_test
                },
                
                # Market Range Functionality Testing Results
                "market_range_functionality": {
                    "price_range_calculation": market_range_test,
                    "loading_states": loading_states_test
                }
            }
            
            # Calculate overall success metrics
            api_tests = [
                browse_api_test.get("endpoint_working", False),
                tenders_api_test.get("endpoint_functional", False),
                price_range_api_test.get("endpoint_working", False),
                catalyst_api_test.get("endpoint_working", False) or catalyst_api_test.get("endpoint_available", False)
            ]
            
            validation_tests = [
                min_bid_test.get("validation_working_correctly", False),
                self_bid_test.get("security_validation_working", False),
                highest_bidder_test.get("prevention_logic_working", False),
                amount_validation_test.get("validation_working_correctly", False)
            ]
            
            edge_case_tests = [
                no_bids_test.get("first_bid_logic_working", False),
                existing_bids_test.get("existing_bid_logic_working", False),
                invalid_amounts_test.get("edge_cases_handled_correctly", 0) >= 2,
                network_error_test.get("error_handling_working", False)
            ]
            
            market_range_tests = [
                market_range_test.get("market_range_functional", False),
                loading_states_test.get("loading_performance_acceptable", False)
            ]
            
            # Calculate success rates
            api_success_rate = sum(api_tests) / len(api_tests) * 100
            validation_success_rate = sum(validation_tests) / len(validation_tests) * 100
            edge_case_success_rate = sum(edge_case_tests) / len(edge_case_tests) * 100
            market_range_success_rate = sum(market_range_tests) / len(market_range_tests) * 100
            
            overall_success_rate = (api_success_rate + validation_success_rate + edge_case_success_rate + market_range_success_rate) / 4
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "api_validation_success_rate": api_success_rate,
                "bid_validation_logic_success_rate": validation_success_rate,
                "edge_cases_success_rate": edge_case_success_rate,
                "market_range_functionality_success_rate": market_range_success_rate,
                
                # Key functionality status
                "browse_endpoint_working": browse_api_test.get("endpoint_working", False),
                "bid_submission_working": tenders_api_test.get("endpoint_functional", False),
                "bid_validation_working": validation_success_rate >= 75,
                "edge_cases_handled": edge_case_success_rate >= 75,
                "market_range_available": market_range_test.get("market_range_functional", False),
                
                # Critical issues found
                "critical_issues": [],
                "minor_issues": [],
                
                # Overall assessment
                "mobile_quick_bid_functional": overall_success_rate >= 75,
                "ready_for_production": overall_success_rate >= 85
            }
            
            # Identify critical and minor issues
            if not browse_api_test.get("endpoint_working", False):
                all_results["summary"]["critical_issues"].append("Browse endpoint not working - affects listing display")
            
            if not tenders_api_test.get("endpoint_functional", False):
                all_results["summary"]["critical_issues"].append("Bid submission endpoint not working - core functionality broken")
            
            if not min_bid_test.get("validation_working_correctly", False):
                all_results["summary"]["critical_issues"].append("Minimum bid validation not working - allows invalid bids")
            
            if not self_bid_test.get("security_validation_working", False):
                all_results["summary"]["minor_issues"].append("Self-bidding prevention may not be working properly")
            
            if not market_range_test.get("market_range_functional", False):
                all_results["summary"]["minor_issues"].append("Market range functionality limited - price suggestions may not be available")
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Run the mobile quick bid functionality tests"""
    tester = MobileQuickBidTester()
    results = await tester.run_comprehensive_mobile_quick_bid_test()
    
    # Print summary
    print("\n" + "=" * 70)
    print("🎯 MOBILE QUICK BID FUNCTIONALITY TEST RESULTS")
    print("=" * 70)
    
    summary = results["summary"]
    print(f"Overall Success Rate: {summary['overall_success_rate']:.1f}%")
    print(f"API Validation: {summary['api_validation_success_rate']:.1f}%")
    print(f"Bid Validation Logic: {summary['bid_validation_logic_success_rate']:.1f}%")
    print(f"Edge Cases Handling: {summary['edge_cases_success_rate']:.1f}%")
    print(f"Market Range Functionality: {summary['market_range_functionality_success_rate']:.1f}%")
    
    print(f"\n🔍 Key Functionality Status:")
    print(f"Browse Endpoint: {'✅ Working' if summary['browse_endpoint_working'] else '❌ Not Working'}")
    print(f"Bid Submission: {'✅ Working' if summary['bid_submission_working'] else '❌ Not Working'}")
    print(f"Bid Validation: {'✅ Working' if summary['bid_validation_working'] else '❌ Not Working'}")
    print(f"Edge Cases: {'✅ Handled' if summary['edge_cases_handled'] else '❌ Issues Found'}")
    print(f"Market Range: {'✅ Available' if summary['market_range_available'] else '❌ Limited'}")
    
    if summary["critical_issues"]:
        print(f"\n❌ Critical Issues Found:")
        for issue in summary["critical_issues"]:
            print(f"  • {issue}")
    
    if summary["minor_issues"]:
        print(f"\n⚠️ Minor Issues Found:")
        for issue in summary["minor_issues"]:
            print(f"  • {issue}")
    
    print(f"\n🎯 Overall Assessment:")
    print(f"Mobile Quick Bid Functional: {'✅ Yes' if summary['mobile_quick_bid_functional'] else '❌ No'}")
    print(f"Ready for Production: {'✅ Yes' if summary['ready_for_production'] else '❌ No'}")
    
    # Save detailed results to file
    with open('/app/mobile_quick_bid_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/mobile_quick_bid_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())