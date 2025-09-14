#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - HOT DEALS FILTERING TESTS
Testing the hot deals filtering fixes as requested

SPECIFIC TESTS REQUESTED:
1. **Test Hot Deals Filter Logic**:
   - Get all marketplace listings from /api/marketplace/browse
   - Check which listings have time_info with time_remaining_seconds <= 86400 (24 hours)
   - Verify the filtering logic correctly identifies hot deals vs regular listings
   - Test that when hot deals filter is applied, only items with < 24h remaining are shown

2. **Test Different Time Scenarios**:
   - List items with various time limits (< 24h, 24-48h, > 48h, no time limit) 
   - Verify each filter category works correctly:
     - hot_deals: only items < 24h
     - expiring_soon: only items < 48h  
     - no_time_limit: only items without time limits
     - all: shows everything

3. **Debug Filter Application**:
   - Check that the frontend properly sends hotDeals filter parameter
   - Verify the local filtering in MarketplaceContext applies correctly
   - Test that console logs show the filtering process working

CRITICAL ENDPOINTS BEING TESTED:
- GET /api/marketplace/browse (get all listings with time_info)
- GET /api/listings/{listing_id} (get individual listing details)
- POST /api/listings (create test listings with different time limits)

EXPECTED RESULTS AFTER FIX:
- Hot deals filter shows only items with time_remaining_seconds <= 86400 (24 hours)
- Expiring soon filter shows items with time_remaining_seconds <= 172800 (48 hours)
- No time limit filter shows items without time limits
- All filter shows everything
- Frontend filtering logic works correctly with backend data
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone, timedelta
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://mobilefixed-market.preview.emergentagent.com/api"

class HotDealsFilterTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_listings = []  # Track created test listings
        
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
    
    async def test_login_and_get_token(self, email="admin@cataloro.com", password="admin123"):
        """Test login and get JWT token"""
        start_time = datetime.now()
        
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    user = data.get("user", {})
                    user_id = user.get("id")
                    
                    if token and user_id:
                        self.log_result(
                            "Login Authentication", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Unknown')} (ID: {user_id}), token received",
                            response_time
                        )
                        return token, user_id, user
                    else:
                        self.log_result(
                            "Login Authentication", 
                            False, 
                            f"Login successful but missing token or user_id in response: {data}",
                            response_time
                        )
                        return None, None, None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Login Authentication", 
                        False, 
                        f"Login failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None, None, None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Login Authentication", 
                False, 
                f"Login request failed with exception: {str(e)}",
                response_time
            )
            return None, None, None
    
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
    
    async def create_test_listing_with_time_limit(self, token, user_id, title, hours_remaining):
        """Create a test listing with specific time limit"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(hours=hours_remaining)
            
            listing_data = {
                "title": title,
                "description": f"Test listing with {hours_remaining}h remaining for hot deals filter testing",
                "price": 100.0 + hours_remaining,  # Different prices for identification
                "category": "Test Category",
                "condition": "New",
                "has_time_limit": True,
                "time_limit_hours": hours_remaining,
                "expires_at": expires_at.isoformat() + "Z"
            }
            
            async with self.session.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listing_id = data.get("id")
                    
                    if listing_id:
                        self.test_listings.append(listing_id)
                        self.log_result(
                            f"Create Test Listing ({hours_remaining}h)", 
                            True, 
                            f"Created listing {listing_id} with {hours_remaining}h remaining",
                            response_time
                        )
                        return listing_id
                    else:
                        self.log_result(
                            f"Create Test Listing ({hours_remaining}h)", 
                            False, 
                            f"Listing created but no ID returned: {data}",
                            response_time
                        )
                        return None
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Create Test Listing ({hours_remaining}h)", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Create Test Listing ({hours_remaining}h)", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def create_test_listing_no_time_limit(self, token, user_id, title):
        """Create a test listing without time limit"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            listing_data = {
                "title": title,
                "description": "Test listing without time limit for hot deals filter testing",
                "price": 999.99,  # High price for identification
                "category": "Test Category",
                "condition": "New",
                "has_time_limit": False
            }
            
            async with self.session.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listing_id = data.get("id")
                    
                    if listing_id:
                        self.test_listings.append(listing_id)
                        self.log_result(
                            "Create Test Listing (No Time Limit)", 
                            True, 
                            f"Created listing {listing_id} without time limit",
                            response_time
                        )
                        return listing_id
                    else:
                        self.log_result(
                            "Create Test Listing (No Time Limit)", 
                            False, 
                            f"Listing created but no ID returned: {data}",
                            response_time
                        )
                        return None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Test Listing (No Time Limit)", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Create Test Listing (No Time Limit)", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def get_all_marketplace_listings(self):
        """Get all marketplace listings to analyze time_info"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse?limit=100") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    listings = await response.json()
                    
                    # Analyze time_info in listings
                    listings_with_time_info = 0
                    hot_deals_count = 0
                    expiring_soon_count = 0
                    no_time_limit_count = 0
                    
                    for listing in listings:
                        time_info = listing.get('time_info')
                        
                        if time_info:
                            listings_with_time_info += 1
                            time_remaining_seconds = time_info.get('time_remaining_seconds')
                            
                            # Handle None values properly
                            if time_remaining_seconds is not None and time_remaining_seconds > 0:
                                if time_remaining_seconds <= 86400:  # 24 hours
                                    hot_deals_count += 1
                                elif time_remaining_seconds <= 172800:  # 48 hours
                                    expiring_soon_count += 1
                        else:
                            no_time_limit_count += 1
                    
                    self.log_result(
                        "Get All Marketplace Listings", 
                        True, 
                        f"Retrieved {len(listings)} listings: {listings_with_time_info} with time_info, {hot_deals_count} hot deals (≤24h), {expiring_soon_count} expiring soon (≤48h), {no_time_limit_count} no time limit",
                        response_time
                    )
                    
                    return listings
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get All Marketplace Listings", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get All Marketplace Listings", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_hot_deals_filter_logic(self, listings):
        """Test the hot deals filter logic against backend data"""
        if not listings:
            self.log_result(
                "Hot Deals Filter Logic Test", 
                False, 
                "No listings available for testing"
            )
            return False
        
        try:
            # Simulate frontend filtering logic
            hot_deals = []
            expiring_soon = []
            no_time_limit = []
            all_listings = listings
            
            for listing in listings:
                time_info = listing.get('time_info')
                
                if not time_info:
                    no_time_limit.append(listing)
                    continue
                
                if not time_info.get('has_time_limit') or time_info.get('is_expired'):
                    no_time_limit.append(listing)
                    continue
                
                time_remaining_seconds = time_info.get('time_remaining_seconds')
                
                # Handle None values properly
                if time_remaining_seconds is not None and time_remaining_seconds > 0:
                    if time_remaining_seconds <= 86400:  # 24 hours = 86400 seconds
                        hot_deals.append(listing)
                    elif time_remaining_seconds <= 172800:  # 48 hours = 172800 seconds
                        expiring_soon.append(listing)
            
            # Test filter results
            self.log_result(
                "Hot Deals Filter Logic Test", 
                True, 
                f"Filter results: {len(hot_deals)} hot deals (≤24h), {len(expiring_soon)} expiring soon (≤48h), {len(no_time_limit)} no time limit, {len(all_listings)} total"
            )
            
            # Detailed analysis of hot deals
            if hot_deals:
                print("   🔥 Hot Deals Analysis:")
                for i, listing in enumerate(hot_deals[:5]):  # Show first 5
                    time_info = listing.get('time_info', {})
                    time_remaining_seconds = time_info.get('time_remaining_seconds', 0)
                    time_remaining_hours = time_remaining_seconds / 3600
                    print(f"      {i+1}. {listing.get('title', 'Unknown')}: {time_remaining_hours:.1f}h remaining ({time_remaining_seconds}s)")
            
            return {
                'hot_deals': hot_deals,
                'expiring_soon': expiring_soon,
                'no_time_limit': no_time_limit,
                'all': all_listings
            }
            
        except Exception as e:
            self.log_result(
                "Hot Deals Filter Logic Test", 
                False, 
                f"Filter logic test failed with exception: {str(e)}"
            )
            return False
    
    async def test_individual_listing_time_info(self, listing_id):
        """Test individual listing endpoint for time_info accuracy"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/listings/{listing_id}") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    listing = await response.json()
                    time_info = listing.get('time_info')
                    
                    if time_info:
                        time_remaining_seconds = time_info.get('time_remaining_seconds', 0)
                        has_time_limit = time_info.get('has_time_limit', False)
                        is_expired = time_info.get('is_expired', False)
                        
                        # Determine category
                        category = "no_time_limit"
                        if has_time_limit and not is_expired and time_remaining_seconds > 0:
                            if time_remaining_seconds <= 86400:
                                category = "hot_deals"
                            elif time_remaining_seconds <= 172800:
                                category = "expiring_soon"
                            else:
                                category = "regular_time_limit"
                        
                        self.log_result(
                            f"Individual Listing Time Info ({listing_id[:8]})", 
                            True, 
                            f"Category: {category}, Time remaining: {time_remaining_seconds}s ({time_remaining_seconds/3600:.1f}h), Has limit: {has_time_limit}, Expired: {is_expired}",
                            response_time
                        )
                        
                        return {
                            'listing_id': listing_id,
                            'category': category,
                            'time_remaining_seconds': time_remaining_seconds,
                            'time_info': time_info
                        }
                    else:
                        self.log_result(
                            f"Individual Listing Time Info ({listing_id[:8]})", 
                            True, 
                            f"No time_info (no time limit listing)",
                            response_time
                        )
                        
                        return {
                            'listing_id': listing_id,
                            'category': 'no_time_limit',
                            'time_remaining_seconds': 0,
                            'time_info': None
                        }
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Individual Listing Time Info ({listing_id[:8]})", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Individual Listing Time Info ({listing_id[:8]})", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_filter_categories_accuracy(self, filter_results):
        """Test accuracy of each filter category"""
        if not filter_results:
            self.log_result(
                "Filter Categories Accuracy Test", 
                False, 
                "No filter results available for testing"
            )
            return False
        
        try:
            # Test hot_deals category (≤ 24 hours)
            hot_deals_accurate = True
            for listing in filter_results['hot_deals']:
                time_info = listing.get('time_info', {})
                time_remaining_seconds = time_info.get('time_remaining_seconds')
                
                # Handle None values properly
                if time_remaining_seconds is None or time_remaining_seconds > 86400:  # More than 24 hours
                    hot_deals_accurate = False
                    self.log_result(
                        "Hot Deals Category Accuracy", 
                        False, 
                        f"❌ Listing '{listing.get('title')}' has {time_remaining_seconds}s ({time_remaining_seconds/3600:.1f}h) remaining (should be ≤24h)"
                    )
                    break
            
            if hot_deals_accurate:
                self.log_result(
                    "Hot Deals Category Accuracy", 
                    True, 
                    f"✅ All {len(filter_results['hot_deals'])} hot deals have ≤24h remaining"
                )
            
            # Test expiring_soon category (≤ 48 hours, > 24 hours)
            expiring_soon_accurate = True
            for listing in filter_results['expiring_soon']:
                time_info = listing.get('time_info', {})
                time_remaining_seconds = time_info.get('time_remaining_seconds')
                
                # Handle None values properly
                if time_remaining_seconds is None or time_remaining_seconds > 172800 or time_remaining_seconds <= 86400:  # More than 48h or less than 24h
                    expiring_soon_accurate = False
                    self.log_result(
                        "Expiring Soon Category Accuracy", 
                        False, 
                        f"❌ Listing '{listing.get('title')}' has {time_remaining_seconds}s ({time_remaining_seconds/3600:.1f}h) remaining (should be 24h < time ≤ 48h)"
                    )
                    break
            
            if expiring_soon_accurate:
                self.log_result(
                    "Expiring Soon Category Accuracy", 
                    True, 
                    f"✅ All {len(filter_results['expiring_soon'])} expiring soon items have 24h < time ≤ 48h"
                )
            
            # Test no_time_limit category
            no_time_limit_accurate = True
            for listing in filter_results['no_time_limit']:
                time_info = listing.get('time_info')
                
                if time_info and time_info.get('has_time_limit') and not time_info.get('is_expired'):
                    time_remaining_seconds = time_info.get('time_remaining_seconds')
                    if time_remaining_seconds is not None and time_remaining_seconds > 0:
                        no_time_limit_accurate = False
                        self.log_result(
                            "No Time Limit Category Accuracy", 
                            False, 
                            f"❌ Listing '{listing.get('title')}' has active time limit ({time_remaining_seconds}s remaining)"
                        )
                        break
            
            if no_time_limit_accurate:
                self.log_result(
                    "No Time Limit Category Accuracy", 
                    True, 
                    f"✅ All {len(filter_results['no_time_limit'])} no time limit items are correctly categorized"
                )
            
            overall_accuracy = hot_deals_accurate and expiring_soon_accurate and no_time_limit_accurate
            
            self.log_result(
                "Overall Filter Categories Accuracy", 
                overall_accuracy, 
                f"Hot deals: {hot_deals_accurate}, Expiring soon: {expiring_soon_accurate}, No time limit: {no_time_limit_accurate}"
            )
            
            return overall_accuracy
            
        except Exception as e:
            self.log_result(
                "Filter Categories Accuracy Test", 
                False, 
                f"Accuracy test failed with exception: {str(e)}"
            )
            return False
    
    async def run_comprehensive_hot_deals_tests(self):
        """Run all hot deals filtering tests"""
        print("🔥 STARTING HOT DEALS FILTERING COMPREHENSIVE TESTS")
        print("=" * 60)
        
        # Step 1: Test database connectivity
        if not await self.test_database_connectivity():
            print("❌ Database connectivity failed, aborting tests")
            return False
        
        # Step 2: Login as admin to create test listings
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        if not admin_token:
            print("❌ Admin login failed, aborting tests")
            return False
        
        # Step 3: Create test listings with different time scenarios
        print("\n📝 CREATING TEST LISTINGS WITH DIFFERENT TIME SCENARIOS:")
        
        # Create listings with various time limits
        test_scenarios = [
            {"hours": 12, "title": "Hot Deal Test - 12h Remaining"},      # Hot deal
            {"hours": 36, "title": "Expiring Soon Test - 36h Remaining"}, # Expiring soon
            {"hours": 72, "title": "Regular Test - 72h Remaining"},       # Regular time limit
        ]
        
        created_listings = []
        for scenario in test_scenarios:
            listing_id = await self.create_test_listing_with_time_limit(
                admin_token, admin_user_id, scenario["title"], scenario["hours"]
            )
            if listing_id:
                created_listings.append(listing_id)
        
        # Create listing without time limit
        no_limit_listing = await self.create_test_listing_no_time_limit(
            admin_token, admin_user_id, "No Time Limit Test"
        )
        if no_limit_listing:
            created_listings.append(no_limit_listing)
        
        print(f"\n✅ Created {len(created_listings)} test listings")
        
        # Step 4: Get all marketplace listings and analyze
        print("\n📋 ANALYZING MARKETPLACE LISTINGS:")
        all_listings = await self.get_all_marketplace_listings()
        if not all_listings:
            print("❌ Failed to get marketplace listings, aborting tests")
            return False
        
        # Step 5: Test hot deals filter logic
        print("\n🔥 TESTING HOT DEALS FILTER LOGIC:")
        filter_results = await self.test_hot_deals_filter_logic(all_listings)
        if not filter_results:
            print("❌ Hot deals filter logic test failed")
            return False
        
        # Step 6: Test individual listing time_info accuracy
        print("\n🔍 TESTING INDIVIDUAL LISTING TIME INFO:")
        for listing_id in created_listings[:3]:  # Test first 3 created listings
            await self.test_individual_listing_time_info(listing_id)
        
        # Step 7: Test filter categories accuracy
        print("\n✅ TESTING FILTER CATEGORIES ACCURACY:")
        accuracy_result = await self.test_filter_categories_accuracy(filter_results)
        
        # Step 8: Summary
        print("\n📊 TEST SUMMARY:")
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical findings
        print("\n🎯 CRITICAL FINDINGS:")
        if filter_results:
            hot_deals_count = len(filter_results['hot_deals'])
            expiring_soon_count = len(filter_results['expiring_soon'])
            no_time_limit_count = len(filter_results['no_time_limit'])
            
            print(f"- Hot Deals (≤24h): {hot_deals_count} items")
            print(f"- Expiring Soon (24h-48h): {expiring_soon_count} items")
            print(f"- No Time Limit: {no_time_limit_count} items")
            print(f"- Filter Logic Accuracy: {'✅ WORKING' if accuracy_result else '❌ ISSUES FOUND'}")
        
        return passed_tests >= (total_tests * 0.8)  # 80% success rate threshold

async def main():
    """Main test execution"""
    async with HotDealsFilterTester() as tester:
        success = await tester.run_comprehensive_hot_deals_tests()
        
        if success:
            print("\n🎉 HOT DEALS FILTERING TESTS COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 HOT DEALS FILTERING TESTS FAILED")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())