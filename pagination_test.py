#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - SERVER-SIDE PAGINATION IMPLEMENTATION TESTING
Testing the complete server-side pagination implementation as requested

SPECIFIC TESTS REQUESTED:
1. **Test Backend Pagination API**:
   - Call GET /api/marketplace/browse with different pagination parameters:
     - Page 1: offset=0, limit=40
     - Page 2: offset=40, limit=40  
     - Page 3: offset=80, limit=40
   - Verify new API response format includes:
     - listings: array of listings
     - pagination: {current_page, total_pages, total_count, page_size, has_next, has_prev}

2. **Test Total Count and Pages**:
   - Verify total_count shows ALL listings in database (not just 40)
   - Verify total_pages is calculated correctly (total_count / page_size)
   - Verify current_page matches the requested page
   - Verify has_next and has_prev flags are correct

3. **Test Different Page Scenarios**:
   - Test page 1 (should have has_prev: false)
   - Test middle page (should have both has_next: true, has_prev: true)
   - Test last page (should have has_next: false)
   - Test pagination with different limits (20, 40, 60)

4. **Test Edge Cases**:
   - Test offset beyond total count (should return empty listings)
   - Test limit=0 (should return empty listings)
   - Test very large offset values

CRITICAL ENDPOINTS BEING TESTED:
- GET /api/marketplace/browse with offset and limit parameters
- Verify pagination metadata in response

EXPECTED RESULTS:
- Backend returns ALL listings count but only requested page's listings
- Each page request loads exactly the requested number of items
- Pagination metadata allows frontend to build proper page controls
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://cataloro-partners.preview.emergentagent.com/api"

class PaginationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, details, response_time=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        time_info = f" ({response_time:.1f}ms)" if response_time else ""
        print(f"{status}: {test_name}{time_info}")
        print(f"   Details: {details}")
        print()
    
    async def test_database_connectivity(self):
        """Test if backend can connect to database"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Database Connectivity", 
                        True, 
                        f"Backend health check passed: {data.get('status', 'unknown')}",
                        response_time
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Database Connectivity", 
                        False, 
                        f"Health check failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Database Connectivity", 
                False, 
                f"Health check failed with exception: {str(e)}",
                response_time
            )
            return False

    async def test_pagination_api_basic(self, offset=0, limit=40):
        """Test basic pagination API call"""
        start_time = datetime.now()
        
        try:
            url = f"{BACKEND_URL}/marketplace/browse?offset={offset}&limit={limit}"
            async with self.session.get(url) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response is in new pagination format or old format
                    if isinstance(data, dict) and 'listings' in data and 'pagination' in data:
                        # New pagination format
                        listings = data['listings']
                        pagination = data['pagination']
                        
                        self.log_result(
                            f"Pagination API (offset={offset}, limit={limit})", 
                            True, 
                            f"✅ NEW FORMAT: Got {len(listings)} listings with pagination metadata: {pagination}",
                            response_time
                        )
                        return data
                    elif isinstance(data, list):
                        # Old format - just array of listings
                        self.log_result(
                            f"Pagination API (offset={offset}, limit={limit})", 
                            False, 
                            f"❌ OLD FORMAT: Got {len(data)} listings but NO pagination metadata (still using old format)",
                            response_time
                        )
                        return {"listings": data, "pagination": None}
                    else:
                        self.log_result(
                            f"Pagination API (offset={offset}, limit={limit})", 
                            False, 
                            f"❌ UNEXPECTED FORMAT: Response format not recognized: {type(data)}",
                            response_time
                        )
                        return None
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Pagination API (offset={offset}, limit={limit})", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Pagination API (offset={offset}, limit={limit})", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None

    async def test_pagination_metadata_structure(self, response_data):
        """Test that pagination metadata has correct structure"""
        if not response_data or not response_data.get('pagination'):
            self.log_result(
                "Pagination Metadata Structure", 
                False, 
                "❌ NO PAGINATION METADATA: Response does not contain pagination object"
            )
            return False
        
        pagination = response_data['pagination']
        required_fields = ['current_page', 'total_pages', 'total_count', 'page_size', 'has_next', 'has_prev']
        
        missing_fields = []
        for field in required_fields:
            if field not in pagination:
                missing_fields.append(field)
        
        if missing_fields:
            self.log_result(
                "Pagination Metadata Structure", 
                False, 
                f"❌ MISSING FIELDS: Pagination metadata missing required fields: {missing_fields}"
            )
            return False
        
        # Validate field types
        type_errors = []
        if not isinstance(pagination['current_page'], int):
            type_errors.append(f"current_page should be int, got {type(pagination['current_page'])}")
        if not isinstance(pagination['total_pages'], int):
            type_errors.append(f"total_pages should be int, got {type(pagination['total_pages'])}")
        if not isinstance(pagination['total_count'], int):
            type_errors.append(f"total_count should be int, got {type(pagination['total_count'])}")
        if not isinstance(pagination['page_size'], int):
            type_errors.append(f"page_size should be int, got {type(pagination['page_size'])}")
        if not isinstance(pagination['has_next'], bool):
            type_errors.append(f"has_next should be bool, got {type(pagination['has_next'])}")
        if not isinstance(pagination['has_prev'], bool):
            type_errors.append(f"has_prev should be bool, got {type(pagination['has_prev'])}")
        
        if type_errors:
            self.log_result(
                "Pagination Metadata Structure", 
                False, 
                f"❌ TYPE ERRORS: {'; '.join(type_errors)}"
            )
            return False
        
        self.log_result(
            "Pagination Metadata Structure", 
            True, 
            f"✅ STRUCTURE CORRECT: All required fields present with correct types: {pagination}"
        )
        return True

    async def test_pagination_calculations(self, response_data, expected_offset, expected_limit):
        """Test that pagination calculations are correct"""
        if not response_data or not response_data.get('pagination'):
            self.log_result(
                "Pagination Calculations", 
                False, 
                "❌ NO PAGINATION DATA: Cannot test calculations without pagination metadata"
            )
            return False
        
        pagination = response_data['pagination']
        listings = response_data['listings']
        
        # Calculate expected current page
        expected_current_page = (expected_offset // expected_limit) + 1
        
        # Test current_page calculation
        if pagination['current_page'] != expected_current_page:
            self.log_result(
                "Pagination Calculations - Current Page", 
                False, 
                f"❌ WRONG CURRENT PAGE: Expected {expected_current_page}, got {pagination['current_page']}"
            )
            return False
        
        # Test page_size matches requested limit
        if pagination['page_size'] != expected_limit:
            self.log_result(
                "Pagination Calculations - Page Size", 
                False, 
                f"❌ WRONG PAGE SIZE: Expected {expected_limit}, got {pagination['page_size']}"
            )
            return False
        
        # Test total_pages calculation
        expected_total_pages = (pagination['total_count'] + expected_limit - 1) // expected_limit
        if pagination['total_pages'] != expected_total_pages:
            self.log_result(
                "Pagination Calculations - Total Pages", 
                False, 
                f"❌ WRONG TOTAL PAGES: Expected {expected_total_pages}, got {pagination['total_pages']} (total_count: {pagination['total_count']}, page_size: {expected_limit})"
            )
            return False
        
        # Test has_prev flag
        expected_has_prev = expected_current_page > 1
        if pagination['has_prev'] != expected_has_prev:
            self.log_result(
                "Pagination Calculations - Has Previous", 
                False, 
                f"❌ WRONG HAS_PREV: Expected {expected_has_prev}, got {pagination['has_prev']} (current_page: {expected_current_page})"
            )
            return False
        
        # Test has_next flag
        expected_has_next = expected_current_page < pagination['total_pages']
        if pagination['has_next'] != expected_has_next:
            self.log_result(
                "Pagination Calculations - Has Next", 
                False, 
                f"❌ WRONG HAS_NEXT: Expected {expected_has_next}, got {pagination['has_next']} (current_page: {expected_current_page}, total_pages: {pagination['total_pages']})"
            )
            return False
        
        # Test actual listings count matches expected (up to page_size)
        expected_listings_count = min(expected_limit, max(0, pagination['total_count'] - expected_offset))
        if len(listings) != expected_listings_count:
            self.log_result(
                "Pagination Calculations - Listings Count", 
                False, 
                f"❌ WRONG LISTINGS COUNT: Expected {expected_listings_count}, got {len(listings)} (total_count: {pagination['total_count']}, offset: {expected_offset})"
            )
            return False
        
        self.log_result(
            "Pagination Calculations", 
            True, 
            f"✅ ALL CALCULATIONS CORRECT: current_page={pagination['current_page']}, total_pages={pagination['total_pages']}, total_count={pagination['total_count']}, has_prev={pagination['has_prev']}, has_next={pagination['has_next']}"
        )
        return True

    async def test_different_page_scenarios(self):
        """Test different page scenarios (first, middle, last)"""
        print("\n📄 TESTING DIFFERENT PAGE SCENARIOS:")
        
        # First, get total count to determine scenarios
        first_page_data = await self.test_pagination_api_basic(offset=0, limit=40)
        if not first_page_data or not first_page_data.get('pagination'):
            self.log_result(
                "Page Scenarios Setup", 
                False, 
                "❌ Cannot test page scenarios without pagination metadata"
            )
            return False
        
        total_count = first_page_data['pagination']['total_count']
        page_size = 40
        total_pages = (total_count + page_size - 1) // page_size
        
        print(f"   Total listings: {total_count}, Page size: {page_size}, Total pages: {total_pages}")
        
        # Test Page 1 (should have has_prev: false)
        page1_success = await self.test_first_page_scenario(first_page_data)
        
        # Test Middle Page (if exists)
        middle_page_success = True
        if total_pages > 2:
            middle_page = total_pages // 2
            middle_offset = (middle_page - 1) * page_size
            middle_page_data = await self.test_pagination_api_basic(offset=middle_offset, limit=page_size)
            if middle_page_data:
                middle_page_success = await self.test_middle_page_scenario(middle_page_data, middle_page, total_pages)
        
        # Test Last Page (if different from first)
        last_page_success = True
        if total_pages > 1:
            last_offset = (total_pages - 1) * page_size
            last_page_data = await self.test_pagination_api_basic(offset=last_offset, limit=page_size)
            if last_page_data:
                last_page_success = await self.test_last_page_scenario(last_page_data, total_pages)
        
        overall_success = page1_success and middle_page_success and last_page_success
        self.log_result(
            "Page Scenarios Summary", 
            overall_success, 
            f"Page scenarios test: First={page1_success}, Middle={middle_page_success}, Last={last_page_success}"
        )
        
        return overall_success

    async def test_first_page_scenario(self, page_data):
        """Test first page scenario (has_prev should be false)"""
        if not page_data or not page_data.get('pagination'):
            return False
        
        pagination = page_data['pagination']
        
        # First page should have has_prev: false
        if pagination['has_prev'] != False:
            self.log_result(
                "First Page Scenario", 
                False, 
                f"❌ FIRST PAGE ERROR: has_prev should be false, got {pagination['has_prev']}"
            )
            return False
        
        # First page should have current_page: 1
        if pagination['current_page'] != 1:
            self.log_result(
                "First Page Scenario", 
                False, 
                f"❌ FIRST PAGE ERROR: current_page should be 1, got {pagination['current_page']}"
            )
            return False
        
        self.log_result(
            "First Page Scenario", 
            True, 
            f"✅ FIRST PAGE CORRECT: current_page=1, has_prev=false, has_next={pagination['has_next']}"
        )
        return True

    async def test_middle_page_scenario(self, page_data, expected_page, total_pages):
        """Test middle page scenario (both has_next and has_prev should be true)"""
        if not page_data or not page_data.get('pagination'):
            return False
        
        pagination = page_data['pagination']
        
        # Middle page should have both has_prev and has_next as true
        if pagination['has_prev'] != True:
            self.log_result(
                "Middle Page Scenario", 
                False, 
                f"❌ MIDDLE PAGE ERROR: has_prev should be true, got {pagination['has_prev']}"
            )
            return False
        
        if pagination['has_next'] != True:
            self.log_result(
                "Middle Page Scenario", 
                False, 
                f"❌ MIDDLE PAGE ERROR: has_next should be true, got {pagination['has_next']}"
            )
            return False
        
        # Current page should match expected
        if pagination['current_page'] != expected_page:
            self.log_result(
                "Middle Page Scenario", 
                False, 
                f"❌ MIDDLE PAGE ERROR: current_page should be {expected_page}, got {pagination['current_page']}"
            )
            return False
        
        self.log_result(
            "Middle Page Scenario", 
            True, 
            f"✅ MIDDLE PAGE CORRECT: current_page={expected_page}, has_prev=true, has_next=true"
        )
        return True

    async def test_last_page_scenario(self, page_data, total_pages):
        """Test last page scenario (has_next should be false)"""
        if not page_data or not page_data.get('pagination'):
            return False
        
        pagination = page_data['pagination']
        
        # Last page should have has_next: false
        if pagination['has_next'] != False:
            self.log_result(
                "Last Page Scenario", 
                False, 
                f"❌ LAST PAGE ERROR: has_next should be false, got {pagination['has_next']}"
            )
            return False
        
        # Last page should have current_page equal to total_pages
        if pagination['current_page'] != total_pages:
            self.log_result(
                "Last Page Scenario", 
                False, 
                f"❌ LAST PAGE ERROR: current_page should be {total_pages}, got {pagination['current_page']}"
            )
            return False
        
        # Last page should have has_prev: true (unless it's also the first page)
        expected_has_prev = total_pages > 1
        if pagination['has_prev'] != expected_has_prev:
            self.log_result(
                "Last Page Scenario", 
                False, 
                f"❌ LAST PAGE ERROR: has_prev should be {expected_has_prev}, got {pagination['has_prev']}"
            )
            return False
        
        self.log_result(
            "Last Page Scenario", 
            True, 
            f"✅ LAST PAGE CORRECT: current_page={total_pages}, has_prev={expected_has_prev}, has_next=false"
        )
        return True

    async def test_different_page_sizes(self):
        """Test pagination with different page sizes (20, 40, 60)"""
        print("\n📏 TESTING DIFFERENT PAGE SIZES:")
        
        page_sizes = [20, 40, 60]
        results = []
        
        for page_size in page_sizes:
            page_data = await self.test_pagination_api_basic(offset=0, limit=page_size)
            if page_data and page_data.get('pagination'):
                pagination = page_data['pagination']
                
                # Verify page_size matches requested limit
                if pagination['page_size'] == page_size:
                    # Verify listings count doesn't exceed page_size
                    listings_count = len(page_data['listings'])
                    if listings_count <= page_size:
                        self.log_result(
                            f"Page Size {page_size}", 
                            True, 
                            f"✅ PAGE SIZE CORRECT: Requested {page_size}, got {listings_count} listings, page_size={pagination['page_size']}"
                        )
                        results.append(True)
                    else:
                        self.log_result(
                            f"Page Size {page_size}", 
                            False, 
                            f"❌ TOO MANY LISTINGS: Requested {page_size}, got {listings_count} listings (exceeds limit)"
                        )
                        results.append(False)
                else:
                    self.log_result(
                        f"Page Size {page_size}", 
                        False, 
                        f"❌ WRONG PAGE SIZE: Requested {page_size}, got page_size={pagination['page_size']}"
                    )
                    results.append(False)
            else:
                self.log_result(
                    f"Page Size {page_size}", 
                    False, 
                    f"❌ NO PAGINATION DATA: Failed to get pagination data for page size {page_size}"
                )
                results.append(False)
        
        success_count = sum(results)
        overall_success = success_count == len(page_sizes)
        
        self.log_result(
            "Different Page Sizes Summary", 
            overall_success, 
            f"Successfully tested {success_count}/{len(page_sizes)} different page sizes"
        )
        
        return overall_success

    async def test_edge_cases(self):
        """Test edge cases for pagination"""
        print("\n🔍 TESTING PAGINATION EDGE CASES:")
        
        edge_case_results = []
        
        # Test 1: Offset beyond total count
        large_offset_data = await self.test_pagination_api_basic(offset=999999, limit=40)
        if large_offset_data:
            listings = large_offset_data['listings']
            if len(listings) == 0:
                self.log_result(
                    "Edge Case: Large Offset", 
                    True, 
                    f"✅ LARGE OFFSET HANDLED: offset=999999 returned {len(listings)} listings (empty as expected)"
                )
                edge_case_results.append(True)
            else:
                self.log_result(
                    "Edge Case: Large Offset", 
                    False, 
                    f"❌ LARGE OFFSET ERROR: offset=999999 returned {len(listings)} listings (should be empty)"
                )
                edge_case_results.append(False)
        else:
            edge_case_results.append(False)
        
        # Test 2: Limit = 0
        zero_limit_data = await self.test_pagination_api_basic(offset=0, limit=0)
        if zero_limit_data:
            listings = zero_limit_data['listings']
            if len(listings) == 0:
                self.log_result(
                    "Edge Case: Zero Limit", 
                    True, 
                    f"✅ ZERO LIMIT HANDLED: limit=0 returned {len(listings)} listings (empty as expected)"
                )
                edge_case_results.append(True)
            else:
                self.log_result(
                    "Edge Case: Zero Limit", 
                    False, 
                    f"❌ ZERO LIMIT ERROR: limit=0 returned {len(listings)} listings (should be empty)"
                )
                edge_case_results.append(False)
        else:
            edge_case_results.append(False)
        
        # Test 3: Very large limit
        large_limit_data = await self.test_pagination_api_basic(offset=0, limit=1000)
        if large_limit_data and large_limit_data.get('pagination'):
            pagination = large_limit_data['pagination']
            listings = large_limit_data['listings']
            
            # Should return all available listings (up to total_count)
            if len(listings) <= pagination['total_count']:
                self.log_result(
                    "Edge Case: Large Limit", 
                    True, 
                    f"✅ LARGE LIMIT HANDLED: limit=1000 returned {len(listings)} listings (≤ total_count={pagination['total_count']})"
                )
                edge_case_results.append(True)
            else:
                self.log_result(
                    "Edge Case: Large Limit", 
                    False, 
                    f"❌ LARGE LIMIT ERROR: limit=1000 returned {len(listings)} listings (> total_count={pagination['total_count']})"
                )
                edge_case_results.append(False)
        else:
            edge_case_results.append(False)
        
        success_count = sum(edge_case_results)
        overall_success = success_count == len(edge_case_results)
        
        self.log_result(
            "Edge Cases Summary", 
            overall_success, 
            f"Successfully handled {success_count}/{len(edge_case_results)} edge cases"
        )
        
        return overall_success

    async def test_pagination_consistency(self):
        """Test that pagination is consistent across multiple requests"""
        print("\n🔄 TESTING PAGINATION CONSISTENCY:")
        
        # Make multiple requests to the same endpoint
        consistency_results = []
        
        for i in range(3):
            page_data = await self.test_pagination_api_basic(offset=0, limit=40)
            if page_data and page_data.get('pagination'):
                consistency_results.append(page_data['pagination'])
            else:
                self.log_result(
                    "Pagination Consistency", 
                    False, 
                    f"❌ CONSISTENCY ERROR: Request {i+1} failed to return pagination data"
                )
                return False
        
        # Check if all requests returned the same pagination metadata
        first_pagination = consistency_results[0]
        
        for i, pagination in enumerate(consistency_results[1:], 2):
            if (pagination['total_count'] != first_pagination['total_count'] or
                pagination['total_pages'] != first_pagination['total_pages']):
                self.log_result(
                    "Pagination Consistency", 
                    False, 
                    f"❌ INCONSISTENT DATA: Request {i} returned different pagination metadata"
                )
                return False
        
        self.log_result(
            "Pagination Consistency", 
            True, 
            f"✅ CONSISTENT DATA: All 3 requests returned consistent pagination metadata (total_count={first_pagination['total_count']})"
        )
        return True

    async def run_comprehensive_pagination_tests(self):
        """Run all pagination tests comprehensively"""
        print("🚀 STARTING COMPREHENSIVE SERVER-SIDE PAGINATION TESTS")
        print("=" * 80)
        
        # Test 1: Database connectivity
        if not await self.test_database_connectivity():
            print("❌ Database connectivity failed - aborting tests")
            return False
        
        # Test 2: Basic pagination API calls
        print("\n📋 TESTING BASIC PAGINATION API CALLS:")
        
        # Page 1: offset=0, limit=40
        page1_data = await self.test_pagination_api_basic(offset=0, limit=40)
        if not page1_data:
            print("❌ Page 1 test failed - aborting further tests")
            return False
        
        # Test pagination metadata structure
        if not await self.test_pagination_metadata_structure(page1_data):
            print("❌ Pagination metadata structure test failed")
            return False
        
        # Test pagination calculations
        if not await self.test_pagination_calculations(page1_data, 0, 40):
            print("❌ Pagination calculations test failed")
            return False
        
        # Page 2: offset=40, limit=40
        page2_data = await self.test_pagination_api_basic(offset=40, limit=40)
        if page2_data and page2_data.get('pagination'):
            await self.test_pagination_calculations(page2_data, 40, 40)
        
        # Page 3: offset=80, limit=40
        page3_data = await self.test_pagination_api_basic(offset=80, limit=40)
        if page3_data and page3_data.get('pagination'):
            await self.test_pagination_calculations(page3_data, 80, 40)
        
        # Test 3: Different page scenarios
        await self.test_different_page_scenarios()
        
        # Test 4: Different page sizes
        await self.test_different_page_sizes()
        
        # Test 5: Edge cases
        await self.test_edge_cases()
        
        # Test 6: Consistency
        await self.test_pagination_consistency()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 PAGINATION TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return failed_tests == 0

async def main():
    """Main test execution"""
    async with PaginationTester() as tester:
        success = await tester.run_comprehensive_pagination_tests()
        
        if success:
            print("\n🎉 ALL PAGINATION TESTS PASSED!")
            sys.exit(0)
        else:
            print("\n💥 SOME PAGINATION TESTS FAILED!")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())