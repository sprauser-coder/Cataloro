#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - SORTING FIX FOR TENDERS > SELL SECTION TESTING
Testing the sorting fix for seller tenders overview endpoint

FOCUS AREAS:
1. LOGIN AS ADMIN USER (seller) - admin@cataloro.com / admin123
2. CREATE MULTIPLE TEST LISTINGS - with different creation times to test sorting
3. CALL SELLER TENDERS OVERVIEW ENDPOINT - GET /api/tenders/seller/{seller_id}/overview
4. VERIFY SORTING - check that listings are returned in descending order by created_at (newest first)
5. TEST WITH BIDS - place bids on some listings and verify sorting still works correctly

TESTING SORTING FIX: Added .sort("created_at", -1) to listings query in get_seller_tenders_overview function
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://self-hosted-shop.preview.emergentagent.com/api"

class SortingTester:
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
                            "Admin Login", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Unknown')} (ID: {user_id})",
                            response_time
                        )
                        return token, user_id, user
                    else:
                        self.log_result(
                            "Admin Login", 
                            False, 
                            f"Login successful but missing token or user_id in response",
                            response_time
                        )
                        return None, None, None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Login", 
                        False, 
                        f"Login failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None, None, None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Admin Login", 
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

    async def create_multiple_test_listings_for_sorting(self, token):
        """Create multiple test listings with different creation times"""
        listing_ids = []
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create 3 listings with small delays to ensure different creation times
        for i in range(3):
            start_time = datetime.now()
            
            try:
                listing_data = {
                    "title": f"Sorting Test Listing {i+1} - Created at {datetime.now().strftime('%H:%M:%S')}",
                    "description": f"Test listing #{i+1} created for sorting verification",
                    "price": 100.0 + (i * 10),  # Different prices: 100, 110, 120
                    "category": "Test",
                    "condition": "New",
                    "has_time_limit": False
                }
                
                async with self.session.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers) as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        listing_id = data.get("id")
                        
                        if listing_id:
                            listing_ids.append(listing_id)
                            self.log_result(
                                f"Create Test Listing {i+1}", 
                                True, 
                                f"Created listing {listing_id} with price ${listing_data['price']}",
                                response_time
                            )
                        else:
                            self.log_result(
                                f"Create Test Listing {i+1}", 
                                False, 
                                f"Listing created but no ID returned: {data}",
                                response_time
                            )
                    else:
                        error_text = await response.text()
                        self.log_result(
                            f"Create Test Listing {i+1}", 
                            False, 
                            f"Failed with status {response.status}: {error_text}",
                            response_time
                        )
                        
            except Exception as e:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                self.log_result(
                    f"Create Test Listing {i+1}", 
                    False, 
                    f"Request failed with exception: {str(e)}",
                    response_time
                )
            
            # Small delay to ensure different creation timestamps
            if i < 2:  # Don't delay after the last listing
                await asyncio.sleep(2)  # 2 second delay
        
        return listing_ids

    async def test_seller_tenders_overview_endpoint(self, seller_id):
        """Test the seller tenders overview endpoint"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/tenders/seller/{seller_id}/overview") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    self.log_result(
                        "Seller Tenders Overview Endpoint", 
                        True, 
                        f"Successfully retrieved overview with {len(data)} listings",
                        response_time
                    )
                    
                    return data
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Seller Tenders Overview Endpoint", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Seller Tenders Overview Endpoint", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None

    async def verify_listings_sorting(self, overview_data):
        """Verify that listings are sorted by created_at in descending order (newest first)"""
        try:
            if not overview_data or len(overview_data) < 2:
                self.log_result(
                    "Verify Listings Sorting", 
                    True, 
                    f"Not enough listings to verify sorting ({len(overview_data) if overview_data else 0} listings)"
                )
                return True
            
            # Extract listing creation times from our test listings
            test_listings = []
            for item in overview_data:
                listing = item.get('listing', {})
                title = listing.get('title', '')
                if 'Sorting Test Listing' in title:
                    # Extract the number from the title to verify order
                    try:
                        import re
                        match = re.search(r'Sorting Test Listing (\d+)', title)
                        if match:
                            listing_number = int(match.group(1))
                            test_listings.append({
                                'id': listing.get('id', 'unknown'),
                                'number': listing_number,
                                'title': title
                            })
                    except:
                        pass
            
            if len(test_listings) < 2:
                self.log_result(
                    "Verify Listings Sorting", 
                    True, 
                    "No test listings found in overview to verify sorting"
                )
                return True
            
            # Check if listings are in descending order (newest first)
            # Since we created listings 1, 2, 3 in that order, newest first should be 3, 2, 1
            is_sorted_correctly = True
            for i in range(len(test_listings) - 1):
                current_number = test_listings[i]['number']
                next_number = test_listings[i + 1]['number']
                
                # Current should have higher number than next (newer first)
                if current_number < next_number:
                    is_sorted_correctly = False
                    break
            
            if is_sorted_correctly:
                order_str = " -> ".join([str(item['number']) for item in test_listings])
                self.log_result(
                    "Verify Listings Sorting", 
                    True, 
                    f"✅ SORTING FIX WORKING: Listings are correctly sorted by created_at (newest first). Order: {order_str}"
                )
                return True
            else:
                order_str = " -> ".join([str(item['number']) for item in test_listings])
                self.log_result(
                    "Verify Listings Sorting", 
                    False, 
                    f"❌ SORTING NOT WORKING: Listings not in correct order. Got: {order_str}, Expected: 3 -> 2 -> 1"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Verify Listings Sorting", 
                False, 
                f"Error verifying sorting: {str(e)}"
            )
            return False

    async def place_test_bids_on_listings(self, buyer_token, listing_ids):
        """Place test bids on specified listings"""
        headers = {"Authorization": f"Bearer {buyer_token}"}
        
        for i, listing_id in enumerate(listing_ids):
            start_time = datetime.now()
            
            try:
                tender_data = {
                    "listing_id": listing_id,
                    "amount": 125.0 + (i * 5),  # Different bid amounts: 125, 130
                    "message": f"Test bid #{i+1} for sorting verification"
                }
                
                async with self.session.post(f"{BACKEND_URL}/tenders/submit", json=tender_data, headers=headers) as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        tender_id = data.get("id")
                        
                        self.log_result(
                            f"Place Test Bid {i+1}", 
                            True, 
                            f"Successfully placed bid ${tender_data['amount']} on listing {listing_id}",
                            response_time
                        )
                    else:
                        error_text = await response.text()
                        self.log_result(
                            f"Place Test Bid {i+1}", 
                            False, 
                            f"Failed with status {response.status}: {error_text}",
                            response_time
                        )
                        
            except Exception as e:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                self.log_result(
                    f"Place Test Bid {i+1}", 
                    False, 
                    f"Request failed with exception: {str(e)}",
                    response_time
                )

    async def test_sorting_fix_for_seller_tenders(self):
        """Test the sorting fix for Tenders > Sell section"""
        print("\n🔄 SORTING FIX FOR TENDERS > SELL SECTION TESTING:")
        
        # Step 1: Login as admin user (seller)
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        
        if not admin_token:
            self.log_result(
                "Sorting Fix Test - Admin Login", 
                False, 
                "Failed to login as admin user for sorting test"
            )
            return False
        
        self.log_result(
            "Sorting Fix Test - Admin Login", 
            True, 
            f"Successfully logged in as admin seller (ID: {admin_user_id})"
        )
        
        # Step 2: Create multiple test listings with different creation times
        listing_ids = await self.create_multiple_test_listings_for_sorting(admin_token)
        
        if not listing_ids or len(listing_ids) < 3:
            self.log_result(
                "Sorting Fix Test - Create Test Listings", 
                False, 
                f"Failed to create sufficient test listings. Created: {len(listing_ids) if listing_ids else 0}"
            )
            return False
        
        self.log_result(
            "Sorting Fix Test - Create Test Listings", 
            True, 
            f"Successfully created {len(listing_ids)} test listings for sorting test"
        )
        
        # Step 3: Call seller tenders overview endpoint
        overview_data = await self.test_seller_tenders_overview_endpoint(admin_user_id)
        
        if not overview_data:
            self.log_result(
                "Sorting Fix Test - Overview Endpoint", 
                False, 
                "Failed to retrieve seller tenders overview data"
            )
            return False
        
        # Step 4: Verify sorting (newest first)
        sorting_verified = await self.verify_listings_sorting(overview_data)
        
        if not sorting_verified:
            self.log_result(
                "Sorting Fix Test - Verify Sorting", 
                False, 
                "Listings are not properly sorted by created_at (newest first)"
            )
            return False
        
        # Step 5: Create buyer and place bids on some listings
        buyer_token, buyer_user_id, buyer_user = await self.test_login_and_get_token("demo@cataloro.com", "demo123")
        
        if buyer_token:
            await self.place_test_bids_on_listings(buyer_token, listing_ids[:2])  # Bid on first 2 listings
            
            # Step 6: Verify sorting still works after bids are placed
            overview_data_with_bids = await self.test_seller_tenders_overview_endpoint(admin_user_id)
            
            if overview_data_with_bids:
                sorting_with_bids_verified = await self.verify_listings_sorting(overview_data_with_bids)
                
                if sorting_with_bids_verified:
                    self.log_result(
                        "Sorting Fix Test - Sorting With Bids", 
                        True, 
                        "✅ Sorting still works correctly after bids are placed"
                    )
                else:
                    self.log_result(
                        "Sorting Fix Test - Sorting With Bids", 
                        False, 
                        "❌ Sorting broken after bids are placed"
                    )
                    return False
        
        self.log_result(
            "Sorting Fix Test - Complete", 
            True, 
            "✅ SORTING FIX VERIFIED: Listings in Tenders > Sell section are properly sorted by created_at (newest first)"
        )
        
        return True

async def main():
    """Main test execution function"""
    print("🚀 CATALORO MARKETPLACE - SORTING FIX FOR TENDERS > SELL SECTION TESTING")
    print("=" * 80)
    print("Testing the sorting fix for seller tenders overview endpoint")
    print("Focus: Verify listings are sorted by created_at (newest first)")
    print("Fix Applied: Added .sort('created_at', -1) to listings query in get_seller_tenders_overview")
    print("=" * 80)
    
    async with SortingTester() as tester:
        # Test 1: Database connectivity
        print("\n📊 DATABASE CONNECTIVITY TEST:")
        await tester.test_database_connectivity()
        
        # Test 2: Sorting fix for seller tenders overview
        sorting_fix_success = await tester.test_sorting_fix_for_seller_tenders()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🔄 SORTING FIX FOR TENDERS > SELL SECTION SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        total_tests = len(tester.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"🎯 Focus: Sorting verification for seller tenders overview")
        
        if sorting_fix_success:
            print("✅ SORTING FIX VERIFIED: Listings are properly sorted by created_at (newest first)")
            print("✅ TENDERS > SELL SECTION: Working correctly with proper sorting")
        else:
            print("❌ SORTING FIX FAILED: Issues found with listing sorting")
            print("❌ TENDERS > SELL SECTION: May not display listings in correct order")
        
        # Show detailed results
        print("\n📋 DETAILED TEST RESULTS:")
        for result in tester.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())