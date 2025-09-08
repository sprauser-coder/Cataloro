#!/usr/bin/env python3
"""
Cataloro Marketplace - Browse Pagination API Testing
Focused testing of the browse pagination endpoint as requested in review:
1. Test the browse endpoint: GET /api/marketplace/browse?page=1&limit=40
2. Check pagination response structure with listings array and pagination object
3. Test different pages (page=1, page=2) to verify pagination works
4. Test new bid status filters (bid_status=not_bid_yet and bid_status=highest_bidder)
5. Verify 40 items per page limit
6. Check if there are listings in database that would trigger pagination
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://mega-dashboard.preview.emergentagent.com/api"

class BrowsePaginationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, params: Dict = None) -> Dict:
        """Make HTTP request to backend"""
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "success": response.status < 400
                    }
        except Exception as e:
            return {
                "status": 500,
                "data": {"error": str(e)},
                "success": False
            }
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        
        self.test_results.append(result)
        
        if success:
            print(f"✅ {test_name}: {details}")
        else:
            print(f"❌ {test_name}: {details}")
            self.failed_tests.append(result)
    
    # ==== BROWSE PAGINATION TESTS ====
    
    async def test_browse_endpoint_basic(self):
        """Test basic browse endpoint with page=1&limit=40 (HIGH PRIORITY)"""
        params = {
            "page": 1,
            "limit": 40
        }
        
        response = await self.make_request("GET", "/marketplace/browse", params=params)
        
        if response["success"]:
            data = response["data"]
            
            # Check required response structure
            if "listings" in data and "pagination" in data:
                listings = data["listings"]
                pagination = data["pagination"]
                
                # Verify pagination structure
                required_pagination_fields = ["current_page", "total_pages", "total_items", "has_next", "has_prev"]
                missing_fields = [field for field in required_pagination_fields if field not in pagination]
                
                if not missing_fields:
                    listings_count = len(listings)
                    total_items = pagination.get("total_items", 0)
                    
                    self.log_test(
                        "Browse Endpoint Basic (page=1, limit=40)",
                        True,
                        f"Found {listings_count} listings, Total: {total_items}, Page: {pagination.get('current_page')}/{pagination.get('total_pages')}",
                        {
                            "listings_count": listings_count,
                            "pagination": pagination,
                            "first_listing": listings[0] if listings else None
                        }
                    )
                    
                    # Store data for other tests
                    self.total_listings = total_items
                    self.first_page_count = listings_count
                    
                else:
                    self.log_test(
                        "Browse Endpoint Basic (page=1, limit=40)",
                        False,
                        f"Missing pagination fields: {missing_fields}",
                        data
                    )
            else:
                self.log_test(
                    "Browse Endpoint Basic (page=1, limit=40)",
                    False,
                    "Missing required 'listings' or 'pagination' fields in response",
                    data
                )
        else:
            self.log_test(
                "Browse Endpoint Basic (page=1, limit=40)",
                False,
                f"Request failed with status {response['status']}",
                response["data"]
            )
    
    async def test_pagination_structure_validation(self):
        """Test pagination response structure validation (HIGH PRIORITY)"""
        params = {
            "page": 1,
            "limit": 40
        }
        
        response = await self.make_request("GET", "/marketplace/browse", params=params)
        
        if response["success"]:
            data = response["data"]
            
            if "pagination" in data:
                pagination = data["pagination"]
                
                # Check all required pagination fields
                expected_fields = {
                    "current_page": int,
                    "total_pages": int,
                    "total_items": int,
                    "items_per_page": int,
                    "has_next": bool,
                    "has_prev": bool
                }
                
                validation_results = []
                for field, expected_type in expected_fields.items():
                    if field in pagination:
                        actual_type = type(pagination[field])
                        if actual_type == expected_type:
                            validation_results.append(f"✅ {field}: {pagination[field]} ({actual_type.__name__})")
                        else:
                            validation_results.append(f"❌ {field}: Expected {expected_type.__name__}, got {actual_type.__name__}")
                    else:
                        validation_results.append(f"❌ {field}: Missing")
                
                all_valid = all("✅" in result for result in validation_results)
                
                self.log_test(
                    "Pagination Structure Validation",
                    all_valid,
                    f"Pagination fields validation: {len([r for r in validation_results if '✅' in r])}/{len(expected_fields)} valid",
                    {
                        "validation_results": validation_results,
                        "pagination": pagination
                    }
                )
            else:
                self.log_test(
                    "Pagination Structure Validation",
                    False,
                    "No pagination object found in response",
                    data
                )
        else:
            self.log_test(
                "Pagination Structure Validation",
                False,
                f"Request failed with status {response['status']}",
                response["data"]
            )
    
    async def test_page_2_navigation(self):
        """Test page 2 navigation to verify pagination works (HIGH PRIORITY)"""
        params = {
            "page": 2,
            "limit": 40
        }
        
        response = await self.make_request("GET", "/marketplace/browse", params=params)
        
        if response["success"]:
            data = response["data"]
            
            if "listings" in data and "pagination" in data:
                listings = data["listings"]
                pagination = data["pagination"]
                
                current_page = pagination.get("current_page")
                total_pages = pagination.get("total_pages")
                has_prev = pagination.get("has_prev")
                
                if current_page == 2:
                    listings_count = len(listings)
                    
                    # Check if page 2 should have content
                    if total_pages >= 2:
                        if listings_count > 0:
                            self.log_test(
                                "Page 2 Navigation",
                                True,
                                f"Page 2 loaded with {listings_count} listings, has_prev: {has_prev}",
                                {
                                    "listings_count": listings_count,
                                    "pagination": pagination,
                                    "first_listing_page2": listings[0] if listings else None
                                }
                            )
                        else:
                            self.log_test(
                                "Page 2 Navigation",
                                False,
                                "Page 2 exists but has no listings",
                                pagination
                            )
                    else:
                        # Only 1 page exists, so page 2 should be empty
                        self.log_test(
                            "Page 2 Navigation",
                            True,
                            f"Page 2 correctly empty (only {total_pages} page(s) exist), listings: {listings_count}",
                            pagination
                        )
                else:
                    self.log_test(
                        "Page 2 Navigation",
                        False,
                        f"Expected current_page=2, got {current_page}",
                        pagination
                    )
            else:
                self.log_test(
                    "Page 2 Navigation",
                    False,
                    "Missing required 'listings' or 'pagination' fields",
                    data
                )
        else:
            self.log_test(
                "Page 2 Navigation",
                False,
                f"Request failed with status {response['status']}",
                response["data"]
            )
    
    async def test_40_items_limit(self):
        """Test 40 items per page limit (HIGH PRIORITY)"""
        params = {
            "page": 1,
            "limit": 40
        }
        
        response = await self.make_request("GET", "/marketplace/browse", params=params)
        
        if response["success"]:
            data = response["data"]
            
            if "listings" in data and "pagination" in data:
                listings = data["listings"]
                pagination = data["pagination"]
                
                listings_count = len(listings)
                items_per_page = pagination.get("items_per_page", 0)
                total_items = pagination.get("total_items", 0)
                
                # Check if limit is respected
                if listings_count <= 40:
                    # Check if we got the expected number based on total items
                    expected_count = min(40, total_items)
                    
                    if listings_count == expected_count:
                        self.log_test(
                            "40 Items Per Page Limit",
                            True,
                            f"Correct limit: {listings_count}/{expected_count} items (Total: {total_items})",
                            {
                                "listings_count": listings_count,
                                "items_per_page": items_per_page,
                                "total_items": total_items
                            }
                        )
                    else:
                        self.log_test(
                            "40 Items Per Page Limit",
                            False,
                            f"Expected {expected_count} items, got {listings_count}",
                            pagination
                        )
                else:
                    self.log_test(
                        "40 Items Per Page Limit",
                        False,
                        f"Limit exceeded: {listings_count} > 40 items returned",
                        pagination
                    )
            else:
                self.log_test(
                    "40 Items Per Page Limit",
                    False,
                    "Missing required 'listings' or 'pagination' fields",
                    data
                )
        else:
            self.log_test(
                "40 Items Per Page Limit",
                False,
                f"Request failed with status {response['status']}",
                response["data"]
            )
    
    async def test_bid_status_not_bid_yet(self):
        """Test bid_status=not_bid_yet filter (HIGH PRIORITY)"""
        params = {
            "page": 1,
            "limit": 40,
            "bid_status": "not_bid_yet"
        }
        
        response = await self.make_request("GET", "/marketplace/browse", params=params)
        
        if response["success"]:
            data = response["data"]
            
            if "listings" in data and "filters_applied" in data:
                listings = data["listings"]
                filters = data["filters_applied"]
                
                # Verify filter was applied
                if filters.get("bid_status") == "not_bid_yet":
                    listings_count = len(listings)
                    
                    # Check if listings have correct bid status
                    valid_listings = 0
                    for listing in listings:
                        bid_info = listing.get("bid_info", {})
                        has_bids = bid_info.get("has_bids", False)
                        
                        if not has_bids:
                            valid_listings += 1
                    
                    if valid_listings == listings_count:
                        self.log_test(
                            "Bid Status Filter: not_bid_yet",
                            True,
                            f"Found {listings_count} listings with no bids, all valid",
                            {
                                "listings_count": listings_count,
                                "filters_applied": filters,
                                "sample_bid_info": listings[0].get("bid_info") if listings else None
                            }
                        )
                    else:
                        self.log_test(
                            "Bid Status Filter: not_bid_yet",
                            False,
                            f"Filter validation failed: {valid_listings}/{listings_count} listings have no bids",
                            {
                                "listings_count": listings_count,
                                "valid_listings": valid_listings
                            }
                        )
                else:
                    self.log_test(
                        "Bid Status Filter: not_bid_yet",
                        False,
                        f"Filter not applied correctly: {filters.get('bid_status')}",
                        filters
                    )
            else:
                self.log_test(
                    "Bid Status Filter: not_bid_yet",
                    False,
                    "Missing required 'listings' or 'filters_applied' fields",
                    data
                )
        else:
            self.log_test(
                "Bid Status Filter: not_bid_yet",
                False,
                f"Request failed with status {response['status']}",
                response["data"]
            )
    
    async def test_bid_status_highest_bidder(self):
        """Test bid_status=highest_bidder filter (HIGH PRIORITY)"""
        params = {
            "page": 1,
            "limit": 40,
            "bid_status": "highest_bidder"
        }
        
        response = await self.make_request("GET", "/marketplace/browse", params=params)
        
        if response["success"]:
            data = response["data"]
            
            if "listings" in data and "filters_applied" in data:
                listings = data["listings"]
                filters = data["filters_applied"]
                
                # Verify filter was applied
                if filters.get("bid_status") == "highest_bidder":
                    listings_count = len(listings)
                    
                    # Check if listings have correct bid status
                    valid_listings = 0
                    for listing in listings:
                        bid_info = listing.get("bid_info", {})
                        has_bids = bid_info.get("has_bids", False)
                        highest_bidder = bid_info.get("highest_bidder_id", "")
                        
                        if has_bids and highest_bidder:
                            valid_listings += 1
                    
                    if listings_count == 0:
                        self.log_test(
                            "Bid Status Filter: highest_bidder",
                            True,
                            "No listings with highest bidder found (expected if no bids exist)",
                            {
                                "listings_count": listings_count,
                                "filters_applied": filters
                            }
                        )
                    elif valid_listings == listings_count:
                        self.log_test(
                            "Bid Status Filter: highest_bidder",
                            True,
                            f"Found {listings_count} listings with highest bidder, all valid",
                            {
                                "listings_count": listings_count,
                                "filters_applied": filters,
                                "sample_bid_info": listings[0].get("bid_info") if listings else None
                            }
                        )
                    else:
                        self.log_test(
                            "Bid Status Filter: highest_bidder",
                            False,
                            f"Filter validation failed: {valid_listings}/{listings_count} listings have highest bidder",
                            {
                                "listings_count": listings_count,
                                "valid_listings": valid_listings
                            }
                        )
                else:
                    self.log_test(
                        "Bid Status Filter: highest_bidder",
                        False,
                        f"Filter not applied correctly: {filters.get('bid_status')}",
                        filters
                    )
            else:
                self.log_test(
                    "Bid Status Filter: highest_bidder",
                    False,
                    "Missing required 'listings' or 'filters_applied' fields",
                    data
                )
        else:
            self.log_test(
                "Bid Status Filter: highest_bidder",
                False,
                f"Request failed with status {response['status']}",
                response["data"]
            )
    
    async def test_database_listings_count(self):
        """Check if there are listings in database that would trigger pagination (MEDIUM PRIORITY)"""
        params = {
            "page": 1,
            "limit": 100  # Use higher limit to see total available
        }
        
        response = await self.make_request("GET", "/marketplace/browse", params=params)
        
        if response["success"]:
            data = response["data"]
            
            if "pagination" in data:
                pagination = data["pagination"]
                
                total_items = pagination.get("total_items", 0)
                total_pages = pagination.get("total_pages", 0)
                
                if total_items > 40:
                    self.log_test(
                        "Database Listings Count (Pagination Trigger)",
                        True,
                        f"Sufficient listings for pagination: {total_items} items across {total_pages} pages",
                        {
                            "total_items": total_items,
                            "total_pages": total_pages,
                            "pagination_needed": True
                        }
                    )
                elif total_items > 0:
                    self.log_test(
                        "Database Listings Count (Pagination Trigger)",
                        True,
                        f"Limited listings: {total_items} items in {total_pages} page(s) - pagination not needed",
                        {
                            "total_items": total_items,
                            "total_pages": total_pages,
                            "pagination_needed": False
                        }
                    )
                else:
                    self.log_test(
                        "Database Listings Count (Pagination Trigger)",
                        False,
                        "No listings found in database",
                        pagination
                    )
            else:
                self.log_test(
                    "Database Listings Count (Pagination Trigger)",
                    False,
                    "No pagination data in response",
                    data
                )
        else:
            self.log_test(
                "Database Listings Count (Pagination Trigger)",
                False,
                f"Request failed with status {response['status']}",
                response["data"]
            )
    
    async def test_pagination_controls_visibility(self):
        """Test if pagination controls should be visible on frontend (MEDIUM PRIORITY)"""
        params = {
            "page": 1,
            "limit": 40
        }
        
        response = await self.make_request("GET", "/marketplace/browse", params=params)
        
        if response["success"]:
            data = response["data"]
            
            if "pagination" in data:
                pagination = data["pagination"]
                
                total_pages = pagination.get("total_pages", 0)
                has_next = pagination.get("has_next", False)
                has_prev = pagination.get("has_prev", False)
                current_page = pagination.get("current_page", 1)
                
                # Determine if pagination controls should be visible
                should_show_pagination = total_pages > 1
                
                pagination_info = {
                    "should_show_pagination": should_show_pagination,
                    "total_pages": total_pages,
                    "current_page": current_page,
                    "has_next": has_next,
                    "has_prev": has_prev,
                    "next_button_enabled": has_next,
                    "prev_button_enabled": has_prev
                }
                
                self.log_test(
                    "Pagination Controls Visibility",
                    True,
                    f"Pagination controls should be {'visible' if should_show_pagination else 'hidden'} - {total_pages} page(s)",
                    pagination_info
                )
            else:
                self.log_test(
                    "Pagination Controls Visibility",
                    False,
                    "No pagination data in response",
                    data
                )
        else:
            self.log_test(
                "Pagination Controls Visibility",
                False,
                f"Request failed with status {response['status']}",
                response["data"]
            )
    
    # ==== MAIN TEST EXECUTION ====
    
    async def run_all_tests(self):
        """Run all browse pagination tests"""
        print("🚀 Starting Cataloro Marketplace Browse Pagination API Testing...")
        print(f"📡 Testing against: {BACKEND_URL}")
        print("=" * 80)
        
        # HIGH PRIORITY TESTS - Core Pagination Functionality
        print("\n🔍 HIGH PRIORITY: Core Browse Pagination Tests")
        await self.test_browse_endpoint_basic()
        await self.test_pagination_structure_validation()
        await self.test_page_2_navigation()
        await self.test_40_items_limit()
        
        # HIGH PRIORITY TESTS - Bid Status Filters
        print("\n🎯 HIGH PRIORITY: Bid Status Filter Tests")
        await self.test_bid_status_not_bid_yet()
        await self.test_bid_status_highest_bidder()
        
        # MEDIUM PRIORITY TESTS - Database and UI Considerations
        print("\n📊 MEDIUM PRIORITY: Database and UI Tests")
        await self.test_database_listings_count()
        await self.test_pagination_controls_visibility()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📋 BROWSE PAGINATION API TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = len(self.failed_tests)
        
        print(f"✅ Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print(f"\n🎯 BROWSE PAGINATION VERIFICATION:")
        print(f"   • Basic Browse Endpoint: {'✅' if any('Browse Endpoint Basic' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Pagination Structure: {'✅' if any('Pagination Structure' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Page Navigation: {'✅' if any('Page 2 Navigation' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • 40 Items Limit: {'✅' if any('40 Items' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Bid Status Filters: {'✅' if any('Bid Status Filter' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        
        # Extract key findings for main agent
        print(f"\n📊 KEY FINDINGS:")
        
        # Find total listings info
        for test in self.test_results:
            if test['test'] == 'Database Listings Count (Pagination Trigger)' and test['success']:
                response_data = test.get('response_data', {})
                total_items = response_data.get('total_items', 0)
                pagination_needed = response_data.get('pagination_needed', False)
                print(f"   • Database contains {total_items} listings")
                print(f"   • Pagination {'is' if pagination_needed else 'is not'} needed")
                break
        
        # Find pagination controls info
        for test in self.test_results:
            if test['test'] == 'Pagination Controls Visibility' and test['success']:
                response_data = test.get('response_data', {})
                should_show = response_data.get('should_show_pagination', False)
                total_pages = response_data.get('total_pages', 0)
                print(f"   • Pagination controls should be {'visible' if should_show else 'hidden'} ({total_pages} page(s))")
                break
        
        if failed_tests == 0:
            print(f"\n🎉 ALL BROWSE PAGINATION TESTS PASSED! The API is working correctly.")
        elif failed_tests <= 2:
            print(f"\n⚠️  MOSTLY SUCCESSFUL with {failed_tests} minor issues.")
        else:
            print(f"\n🚨 PAGINATION ISSUES DETECTED - {failed_tests} tests failed.")

async def main():
    """Main test execution"""
    tester = BrowsePaginationTester()
    
    try:
        await tester.setup()
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())