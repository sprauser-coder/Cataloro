#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - PAGINATION AND HOT DEALS FILTER TESTING
Testing the pagination fix and hot deals data structure improvements

SPECIFIC FIXES BEING TESTED:
1. **Pagination Fix**: Increased browse API limit from 50 to 200 listings
2. **Hot Deals Data Structure**: Added enhanced time_info structure with:
   - has_time_limit (boolean)
   - time_remaining_seconds (number)
   - is_expired (boolean)
   - expires_at (timestamp)
3. **Time-based Filtering Logic**: Verify filtering logic for different time scenarios

SPECIFIC TESTS REQUESTED:
1. **Test Pagination Fix**:
   - Call GET /api/marketplace/browse with limit=200 parameter
   - Verify more than 50 listings are returned
   - Check total number of active listings in database
   - Confirm pagination is working

2. **Test Hot Deals Data Structure**:
   - Get sample listings from browse endpoint
   - Check if listings have proper time_info structure
   - Verify some listings have time limits < 24 hours (hot deals)

3. **Test Time-based Filtering Logic**:
   - Identify listings with different time scenarios:
     - Items with < 24 hours remaining (hot deals)
     - Items with 24-48 hours remaining (expiring soon)  
     - Items with > 48 hours remaining (regular)
     - Items with no time limit
   - Verify filtering logic would work correctly

4. **Debug Information**:
   - Check what actual time_info data is returned by API
   - Verify time calculations are correct
   - Confirm filtering criteria match expectations

CRITICAL ENDPOINTS BEING TESTED:
- GET /api/marketplace/browse?limit=200 (pagination fix)
- GET /api/marketplace/browse (hot deals data structure)
- GET /api/listings/{listing_id} (individual listing time_info)

EXPECTED RESULTS AFTER FIX:
- Browse API returns more than 50 listings when limit=200
- Listings have proper time_info structure with all required fields
- Time calculations are accurate for filtering logic
- Hot deals filter can identify items with < 24 hours remaining
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone, timedelta
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://cataloro-uxfixes.preview.emergentagent.com/api"

class PaginationHotDealsTest:
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

    async def test_pagination_fix(self):
        """Test pagination fix - verify more than 50 listings returned with limit=200"""
        print("\n📋 PAGINATION FIX TESTS:")
        
        # Test 1: Default limit (should be 50 or less)
        await self.test_browse_with_default_limit()
        
        # Test 2: Limit=200 (should return more than 50 if available)
        await self.test_browse_with_limit_200()
        
        # Test 3: Compare results
        await self.test_pagination_comparison()
    
    async def test_browse_with_default_limit(self):
        """Test browse with default limit"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    self.log_result(
                        "Browse API (Default Limit)", 
                        True, 
                        f"Retrieved {len(data)} listings with default limit",
                        response_time
                    )
                    
                    return len(data)
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Browse API (Default Limit)", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return 0
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Browse API (Default Limit)", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return 0
    
    async def test_browse_with_limit_200(self):
        """Test browse with limit=200 parameter"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse?limit=200") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if we got more than 50 listings
                    pagination_fix_working = len(data) > 50
                    
                    self.log_result(
                        "Browse API (Limit=200)", 
                        True, 
                        f"Retrieved {len(data)} listings with limit=200",
                        response_time
                    )
                    
                    if pagination_fix_working:
                        self.log_result(
                            "Pagination Fix Verification", 
                            True, 
                            f"✅ PAGINATION FIX WORKING: Got {len(data)} listings (> 50), pagination limit increased successfully"
                        )
                    else:
                        self.log_result(
                            "Pagination Fix Verification", 
                            False, 
                            f"❌ PAGINATION ISSUE: Only got {len(data)} listings (≤ 50), pagination fix may not be working or insufficient data"
                        )
                    
                    return data
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Browse API (Limit=200)", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return []
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Browse API (Limit=200)", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return []
    
    async def test_pagination_comparison(self):
        """Compare pagination results between default and limit=200"""
        start_time = datetime.now()
        
        try:
            # Get both results
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse") as default_response:
                if default_response.status == 200:
                    default_data = await default_response.json()
                    default_count = len(default_data)
                else:
                    default_count = 0
            
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse?limit=200") as limit_response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if limit_response.status == 200:
                    limit_data = await limit_response.json()
                    limit_count = len(limit_data)
                    
                    # Compare results
                    improvement = limit_count - default_count
                    pagination_working = limit_count >= default_count
                    
                    if improvement > 0:
                        self.log_result(
                            "Pagination Comparison", 
                            True, 
                            f"✅ PAGINATION IMPROVEMENT: limit=200 returned {improvement} more listings ({limit_count} vs {default_count})",
                            response_time
                        )
                    elif improvement == 0:
                        self.log_result(
                            "Pagination Comparison", 
                            True, 
                            f"⚠️ SAME RESULTS: Both queries returned {default_count} listings (may indicate limited data or same effective limit)",
                            response_time
                        )
                    else:
                        self.log_result(
                            "Pagination Comparison", 
                            False, 
                            f"❌ PAGINATION REGRESSION: limit=200 returned fewer listings ({limit_count} vs {default_count})",
                            response_time
                        )
                    
                    return pagination_working
                else:
                    self.log_result(
                        "Pagination Comparison", 
                        False, 
                        f"Failed to get limit=200 results for comparison",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Pagination Comparison", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return False

    async def test_hot_deals_data_structure(self):
        """Test hot deals data structure in listings"""
        print("\n🔥 HOT DEALS DATA STRUCTURE TESTS:")
        
        # Get listings with limit=200 to test data structure
        listings = await self.test_browse_with_limit_200()
        
        if not listings:
            self.log_result(
                "Hot Deals Data Structure Test", 
                False, 
                "No listings available to test data structure"
            )
            return False
        
        # Analyze time_info structure
        await self.analyze_time_info_structure(listings)
        
        # Test individual listing time_info
        await self.test_individual_listing_time_info(listings)
        
        return True
    
    async def analyze_time_info_structure(self, listings):
        """Analyze time_info structure across all listings"""
        
        # Count listings with different time_info characteristics
        total_listings = len(listings)
        listings_with_time_info = 0
        listings_with_time_limit = 0
        listings_with_complete_time_info = 0
        hot_deals_candidates = 0
        expiring_soon_candidates = 0
        regular_time_limit_candidates = 0
        no_time_limit_candidates = 0
        
        required_time_info_fields = ['has_time_limit', 'time_remaining_seconds', 'is_expired', 'expires_at']
        
        for listing in listings:
            # Check if listing has time_info
            if 'time_info' in listing:
                listings_with_time_info += 1
                time_info = listing['time_info']
                
                # Check if has_time_limit is true
                if time_info.get('has_time_limit'):
                    listings_with_time_limit += 1
                    
                    # Check if all required fields are present
                    has_all_fields = all(field in time_info for field in required_time_info_fields)
                    if has_all_fields:
                        listings_with_complete_time_info += 1
                        
                        # Categorize by time remaining
                        time_remaining = time_info.get('time_remaining_seconds', 0)
                        
                        if time_remaining <= 0:
                            # Expired
                            pass
                        elif time_remaining < 24 * 3600:  # < 24 hours
                            hot_deals_candidates += 1
                        elif time_remaining < 48 * 3600:  # 24-48 hours
                            expiring_soon_candidates += 1
                        else:  # > 48 hours
                            regular_time_limit_candidates += 1
                else:
                    no_time_limit_candidates += 1
            else:
                no_time_limit_candidates += 1
        
        # Log comprehensive analysis
        self.log_result(
            "Time Info Structure Analysis", 
            True, 
            f"Analyzed {total_listings} listings: {listings_with_time_info} with time_info, {listings_with_complete_time_info} with complete structure"
        )
        
        self.log_result(
            "Time Limit Categories", 
            True, 
            f"Hot deals (< 24h): {hot_deals_candidates}, Expiring soon (24-48h): {expiring_soon_candidates}, Regular (> 48h): {regular_time_limit_candidates}, No limit: {no_time_limit_candidates}"
        )
        
        # Check if data structure fix is working
        if listings_with_complete_time_info > 0:
            self.log_result(
                "Hot Deals Data Structure Fix", 
                True, 
                f"✅ DATA STRUCTURE FIX WORKING: {listings_with_complete_time_info} listings have complete time_info structure with all required fields"
            )
        else:
            self.log_result(
                "Hot Deals Data Structure Fix", 
                False, 
                f"❌ DATA STRUCTURE ISSUE: No listings found with complete time_info structure"
            )
        
        # Check if hot deals filtering would work
        if hot_deals_candidates > 0:
            self.log_result(
                "Hot Deals Filter Readiness", 
                True, 
                f"✅ HOT DEALS FILTER READY: {hot_deals_candidates} listings qualify as hot deals (< 24 hours remaining)"
            )
        else:
            self.log_result(
                "Hot Deals Filter Readiness", 
                False, 
                f"⚠️ NO HOT DEALS: No listings found with < 24 hours remaining (may be normal depending on data)"
            )
        
        return {
            'total': total_listings,
            'with_time_info': listings_with_time_info,
            'with_complete_structure': listings_with_complete_time_info,
            'hot_deals': hot_deals_candidates,
            'expiring_soon': expiring_soon_candidates,
            'regular': regular_time_limit_candidates,
            'no_limit': no_time_limit_candidates
        }
    
    async def test_individual_listing_time_info(self, listings):
        """Test individual listing endpoint for time_info structure"""
        
        if not listings:
            return False
        
        # Test first few listings with time_info
        test_count = 0
        max_tests = 3
        
        for listing in listings:
            if test_count >= max_tests:
                break
                
            if 'time_info' in listing and listing['time_info'].get('has_time_limit'):
                await self.test_single_listing_time_info(listing['id'])
                test_count += 1
        
        if test_count == 0:
            self.log_result(
                "Individual Listing Time Info Test", 
                False, 
                "No listings with time limits found to test individual endpoint"
            )
        
        return test_count > 0
    
    async def test_single_listing_time_info(self, listing_id):
        """Test individual listing time_info structure"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/listings/{listing_id}") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    listing = await response.json()
                    
                    # Check time_info structure
                    if 'time_info' in listing:
                        time_info = listing['time_info']
                        required_fields = ['has_time_limit', 'time_remaining_seconds', 'is_expired', 'expires_at']
                        
                        missing_fields = [field for field in required_fields if field not in time_info]
                        
                        if not missing_fields:
                            # Validate data types and values
                            validation_issues = []
                            
                            if not isinstance(time_info.get('has_time_limit'), bool):
                                validation_issues.append("has_time_limit should be boolean")
                            
                            if not isinstance(time_info.get('time_remaining_seconds'), (int, float)):
                                validation_issues.append("time_remaining_seconds should be number")
                            
                            if not isinstance(time_info.get('is_expired'), bool):
                                validation_issues.append("is_expired should be boolean")
                            
                            if not time_info.get('expires_at'):
                                validation_issues.append("expires_at should not be empty")
                            
                            if not validation_issues:
                                self.log_result(
                                    f"Individual Listing {listing_id[:8]}... Time Info", 
                                    True, 
                                    f"✅ Complete time_info structure: {time_info}",
                                    response_time
                                )
                            else:
                                self.log_result(
                                    f"Individual Listing {listing_id[:8]}... Time Info", 
                                    False, 
                                    f"❌ Validation issues: {', '.join(validation_issues)}",
                                    response_time
                                )
                        else:
                            self.log_result(
                                f"Individual Listing {listing_id[:8]}... Time Info", 
                                False, 
                                f"❌ Missing required fields: {missing_fields}",
                                response_time
                            )
                    else:
                        self.log_result(
                            f"Individual Listing {listing_id[:8]}... Time Info", 
                            False, 
                            f"❌ No time_info found in individual listing",
                            response_time
                        )
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Individual Listing {listing_id[:8]}... Time Info", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Individual Listing {listing_id[:8]}... Time Info", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )

    async def test_time_based_filtering_logic(self):
        """Test time-based filtering logic for hot deals"""
        print("\n⏰ TIME-BASED FILTERING LOGIC TESTS:")
        
        # Get listings to analyze
        listings = await self.test_browse_with_limit_200()
        
        if not listings:
            self.log_result(
                "Time-based Filtering Logic Test", 
                False, 
                "No listings available to test filtering logic"
            )
            return False
        
        # Analyze filtering scenarios
        await self.analyze_filtering_scenarios(listings)
        
        # Test time calculations
        await self.test_time_calculations(listings)
        
        return True
    
    async def analyze_filtering_scenarios(self, listings):
        """Analyze different time-based filtering scenarios"""
        
        scenarios = {
            'hot_deals': [],      # < 24 hours
            'expiring_soon': [],  # 24-48 hours
            'regular': [],        # > 48 hours
            'no_time_limit': [],  # no time limit
            'expired': []         # already expired
        }
        
        current_time = datetime.utcnow()
        
        for listing in listings:
            if 'time_info' not in listing:
                scenarios['no_time_limit'].append(listing['id'])
                continue
            
            time_info = listing['time_info']
            
            if not time_info.get('has_time_limit'):
                scenarios['no_time_limit'].append(listing['id'])
                continue
            
            time_remaining = time_info.get('time_remaining_seconds', 0)
            
            if time_remaining <= 0 or time_info.get('is_expired'):
                scenarios['expired'].append(listing['id'])
            elif time_remaining < 24 * 3600:  # < 24 hours
                scenarios['hot_deals'].append(listing['id'])
            elif time_remaining < 48 * 3600:  # 24-48 hours
                scenarios['expiring_soon'].append(listing['id'])
            else:  # > 48 hours
                scenarios['regular'].append(listing['id'])
        
        # Log scenario analysis
        for scenario, listing_ids in scenarios.items():
            count = len(listing_ids)
            if count > 0:
                sample_ids = listing_ids[:3]  # Show first 3 IDs as examples
                self.log_result(
                    f"Filtering Scenario: {scenario.replace('_', ' ').title()}", 
                    True, 
                    f"Found {count} listings, examples: {[id[:8] + '...' for id in sample_ids]}"
                )
        
        # Test filtering logic effectiveness
        total_with_time_limits = len(scenarios['hot_deals']) + len(scenarios['expiring_soon']) + len(scenarios['regular']) + len(scenarios['expired'])
        
        if total_with_time_limits > 0:
            self.log_result(
                "Time-based Filtering Effectiveness", 
                True, 
                f"✅ FILTERING LOGIC READY: {total_with_time_limits} listings with time limits can be filtered by time remaining"
            )
        else:
            self.log_result(
                "Time-based Filtering Effectiveness", 
                False, 
                f"❌ NO TIME-LIMITED LISTINGS: No listings found with time limits to filter"
            )
        
        return scenarios
    
    async def test_time_calculations(self, listings):
        """Test accuracy of time calculations"""
        
        calculation_tests = 0
        accurate_calculations = 0
        
        for listing in listings:
            if 'time_info' not in listing:
                continue
            
            time_info = listing['time_info']
            
            if not time_info.get('has_time_limit') or not time_info.get('expires_at'):
                continue
            
            calculation_tests += 1
            
            try:
                # Parse expires_at timestamp
                expires_at_str = time_info['expires_at']
                if expires_at_str.endswith('Z'):
                    expires_at_str = expires_at_str[:-1] + '+00:00'
                
                expires_at = datetime.fromisoformat(expires_at_str)
                current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
                
                # Calculate expected time remaining
                time_diff = expires_at - current_time
                expected_seconds = int(time_diff.total_seconds())
                
                # Get actual time remaining from API
                actual_seconds = time_info.get('time_remaining_seconds', 0)
                
                # Allow for small differences due to processing time (up to 60 seconds)
                difference = abs(expected_seconds - actual_seconds)
                
                if difference <= 60:  # Within 1 minute tolerance
                    accurate_calculations += 1
                
                # Check is_expired flag accuracy
                expected_expired = expected_seconds <= 0
                actual_expired = time_info.get('is_expired', False)
                
                expired_flag_correct = expected_expired == actual_expired
                
                if difference <= 60 and expired_flag_correct:
                    self.log_result(
                        f"Time Calculation {listing['id'][:8]}...", 
                        True, 
                        f"✅ Accurate: expected {expected_seconds}s, got {actual_seconds}s (diff: {difference}s), expired: {actual_expired}"
                    )
                else:
                    self.log_result(
                        f"Time Calculation {listing['id'][:8]}...", 
                        False, 
                        f"❌ Inaccurate: expected {expected_seconds}s, got {actual_seconds}s (diff: {difference}s), expired: {actual_expired} vs {expected_expired}"
                    )
                
                # Only test first few to avoid spam
                if calculation_tests >= 5:
                    break
                    
            except Exception as e:
                self.log_result(
                    f"Time Calculation {listing['id'][:8]}...", 
                    False, 
                    f"❌ Calculation error: {str(e)}"
                )
        
        if calculation_tests > 0:
            accuracy_rate = (accurate_calculations / calculation_tests) * 100
            
            self.log_result(
                "Time Calculation Accuracy", 
                accuracy_rate >= 80, 
                f"Time calculations accurate for {accurate_calculations}/{calculation_tests} listings ({accuracy_rate:.1f}%)"
            )
        else:
            self.log_result(
                "Time Calculation Accuracy", 
                False, 
                "No time-limited listings found to test calculations"
            )

    async def test_debug_information(self):
        """Test debug information and data quality"""
        print("\n🔍 DEBUG INFORMATION TESTS:")
        
        # Get sample of listings for detailed analysis
        listings = await self.test_browse_with_limit_200()
        
        if not listings:
            return False
        
        # Debug time_info data quality
        await self.debug_time_info_data_quality(listings)
        
        # Debug API response structure
        await self.debug_api_response_structure(listings)
        
        return True
    
    async def debug_time_info_data_quality(self, listings):
        """Debug time_info data quality issues"""
        
        issues_found = []
        quality_stats = {
            'total_listings': len(listings),
            'with_time_info': 0,
            'with_valid_time_info': 0,
            'with_invalid_expires_at': 0,
            'with_negative_time_remaining': 0,
            'with_inconsistent_expired_flag': 0
        }
        
        for listing in listings:
            if 'time_info' not in listing:
                continue
            
            quality_stats['with_time_info'] += 1
            time_info = listing['time_info']
            
            # Check for valid time_info structure
            required_fields = ['has_time_limit', 'time_remaining_seconds', 'is_expired', 'expires_at']
            if all(field in time_info for field in required_fields):
                quality_stats['with_valid_time_info'] += 1
                
                # Check expires_at format
                try:
                    expires_at_str = time_info['expires_at']
                    if expires_at_str:
                        if expires_at_str.endswith('Z'):
                            expires_at_str = expires_at_str[:-1] + '+00:00'
                        datetime.fromisoformat(expires_at_str)
                    else:
                        quality_stats['with_invalid_expires_at'] += 1
                        issues_found.append(f"Listing {listing['id'][:8]}... has empty expires_at")
                except:
                    quality_stats['with_invalid_expires_at'] += 1
                    issues_found.append(f"Listing {listing['id'][:8]}... has invalid expires_at format")
                
                # Check for negative time remaining
                time_remaining = time_info.get('time_remaining_seconds', 0)
                if time_remaining is not None and time_remaining < 0:
                    quality_stats['with_negative_time_remaining'] += 1
                    issues_found.append(f"Listing {listing['id'][:8]}... has negative time_remaining_seconds: {time_remaining}")
                
                # Check expired flag consistency
                is_expired = time_info.get('is_expired', False)
                if time_remaining is not None:
                    if time_remaining <= 0 and not is_expired:
                        quality_stats['with_inconsistent_expired_flag'] += 1
                        issues_found.append(f"Listing {listing['id'][:8]}... should be expired (time_remaining: {time_remaining}) but is_expired: {is_expired}")
                    elif time_remaining > 0 and is_expired:
                        quality_stats['with_inconsistent_expired_flag'] += 1
                        issues_found.append(f"Listing {listing['id'][:8]}... has time remaining ({time_remaining}s) but is_expired: {is_expired}")
        
        # Log quality statistics
        self.log_result(
            "Time Info Data Quality Stats", 
            True, 
            f"Total: {quality_stats['total_listings']}, With time_info: {quality_stats['with_time_info']}, Valid: {quality_stats['with_valid_time_info']}"
        )
        
        # Log issues found
        if issues_found:
            for issue in issues_found[:5]:  # Show first 5 issues
                self.log_result(
                    "Data Quality Issue", 
                    False, 
                    f"❌ {issue}"
                )
            
            if len(issues_found) > 5:
                self.log_result(
                    "Additional Data Quality Issues", 
                    False, 
                    f"❌ {len(issues_found) - 5} more issues found (showing first 5)"
                )
        else:
            self.log_result(
                "Data Quality Check", 
                True, 
                f"✅ No data quality issues found in time_info structure"
            )
    
    async def debug_api_response_structure(self, listings):
        """Debug API response structure for consistency"""
        
        if not listings:
            return
        
        # Analyze first listing structure
        sample_listing = listings[0]
        
        # Check for required marketplace fields
        required_fields = ['id', 'title', 'price', 'seller_id', 'status']
        optional_fields = ['time_info', 'bid_info', 'seller', 'images', 'description']
        
        missing_required = [field for field in required_fields if field not in sample_listing]
        present_optional = [field for field in optional_fields if field in sample_listing]
        
        self.log_result(
            "API Response Structure", 
            len(missing_required) == 0, 
            f"Required fields present: {len(required_fields) - len(missing_required)}/{len(required_fields)}, Optional fields: {len(present_optional)}/{len(optional_fields)}"
        )
        
        if missing_required:
            self.log_result(
                "Missing Required Fields", 
                False, 
                f"❌ Missing: {missing_required}"
            )
        
        # Check time_info structure if present
        if 'time_info' in sample_listing:
            time_info = sample_listing['time_info']
            self.log_result(
                "Sample Time Info Structure", 
                True, 
                f"✅ Sample time_info: {json.dumps(time_info, indent=2)}"
            )
        else:
            self.log_result(
                "Sample Time Info Structure", 
                False, 
                f"❌ No time_info in sample listing"
            )

    async def run_all_tests(self):
        """Run all pagination and hot deals tests"""
        print("🚀 STARTING PAGINATION AND HOT DEALS FILTER TESTING")
        print("=" * 80)
        
        # Test database connectivity first
        db_connected = await self.test_database_connectivity()
        if not db_connected:
            print("❌ Database connectivity failed - aborting tests")
            return False
        
        # Run all test categories
        test_results = []
        
        # 1. Test Pagination Fix
        test_results.append(await self.test_pagination_fix())
        
        # 2. Test Hot Deals Data Structure
        test_results.append(await self.test_hot_deals_data_structure())
        
        # 3. Test Time-based Filtering Logic
        test_results.append(await self.test_time_based_filtering_logic())
        
        # 4. Test Debug Information
        test_results.append(await self.test_debug_information())
        
        # Summary
        await self.print_test_summary()
        
        return all(test_results)
    
    async def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 PAGINATION AND HOT DEALS TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result['test'].split(' ')[0]
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0}
            
            if result['success']:
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
        
        print("\n📋 Results by Category:")
        for category, stats in categories.items():
            total = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total) * 100 if total > 0 else 0
            print(f"  {category}: {stats['passed']}/{total} ({rate:.1f}%)")
        
        # Show critical failures
        critical_failures = [r for r in self.test_results if not r['success'] and 'CRITICAL' in r['details']]
        if critical_failures:
            print(f"\n🚨 Critical Issues Found: {len(critical_failures)}")
            for failure in critical_failures:
                print(f"  - {failure['test']}: {failure['details']}")
        
        print("\n" + "=" * 80)

async def main():
    """Main test execution"""
    async with PaginationHotDealsTest() as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("🎉 All pagination and hot deals tests completed successfully!")
            return 0
        else:
            print("⚠️ Some tests failed - check results above")
            return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)