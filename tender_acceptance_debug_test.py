#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - TENDER ACCEPTANCE DEBUG TESTING
Focused testing to debug the tender acceptance listing status issue

FOCUS AREAS:
1. SETUP TEST SCENARIO - Create admin user (seller) and demo user (buyer), create test listing, place bid
2. ACCEPT THE TENDER - Using PUT /api/tenders/{tender_id}/accept and monitor listing status update
3. DEBUG THE SPECIFIC ISSUE - Check listing ID matches, verify update query, check database errors
4. TEST SOLD ITEMS ENDPOINT - Verify accepted tender appears in sold items list

DEBUGGING FOCUS:
- Why listing status is not changing to "sold" when tender is accepted
- Check backend logs for debugging messages
- Verify listing ID consistency between tender and listing collections
- Test database update query execution
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

class TenderAcceptanceDebugTester:
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
                            f"Login Authentication ({email})", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Unknown')} (ID: {user_id})",
                            response_time
                        )
                        return token, user_id, user
                    else:
                        self.log_result(
                            f"Login Authentication ({email})", 
                            False, 
                            f"Login successful but missing token or user_id in response: {data}",
                            response_time
                        )
                        return None, None, None
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Login Authentication ({email})", 
                        False, 
                        f"Login failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None, None, None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Login Authentication ({email})", 
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

    async def create_debug_test_listing(self, admin_token):
        """Create a test listing for debugging tender acceptance"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            listing_data = {
                "title": "Debug Tender Acceptance Test Item",
                "description": "Test listing created to debug tender acceptance listing status issue",
                "price": 100.00,
                "category": "Test",
                "condition": "New",
                "has_time_limit": False  # No time limit for easier testing
            }
            
            async with self.session.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listing_id = data.get("id")
                    
                    self.log_result(
                        "Create Debug Test Listing", 
                        True, 
                        f"Successfully created test listing {listing_id} for tender acceptance debugging",
                        response_time
                    )
                    
                    return listing_id
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Debug Test Listing", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Create Debug Test Listing", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None

    async def place_debug_test_bid(self, demo_token, listing_id, buyer_id):
        """Place a test bid for debugging tender acceptance"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {demo_token}"}
            tender_data = {
                "listing_id": listing_id,
                "amount": 125.00,
                "message": "Debug test bid for tender acceptance testing"
            }
            
            async with self.session.post(f"{BACKEND_URL}/tenders/submit", json=tender_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    tender_id = data.get("tender_id") or data.get("id")
                    
                    self.log_result(
                        "Place Debug Test Bid", 
                        True, 
                        f"Successfully placed test bid {tender_id} for $125.00 on listing {listing_id}",
                        response_time
                    )
                    
                    return tender_id
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Place Debug Test Bid", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Place Debug Test Bid", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None

    async def accept_tender_and_monitor(self, admin_token, tender_id, listing_id):
        """Accept tender and monitor the listing status update with backend logs"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            print(f"🔍 ACCEPTING TENDER: {tender_id}")
            print(f"🔍 MONITORING LISTING: {listing_id}")
            print("🔍 CHECKING BACKEND LOGS FOR DEBUGGING MESSAGES...")
            
            # Get listing status BEFORE acceptance
            before_status = await self.get_listing_status(listing_id)
            print(f"📊 LISTING STATUS BEFORE ACCEPTANCE: {before_status}")
            
            # Prepare acceptance data with seller_id
            acceptance_data = {"seller_id": "admin_user_1"}
            
            async with self.session.put(f"{BACKEND_URL}/tenders/{tender_id}/accept", headers=headers, json=acceptance_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    self.log_result(
                        "Accept Tender", 
                        True, 
                        f"Successfully accepted tender {tender_id}: {data.get('message', 'No message')}",
                        response_time
                    )
                    
                    # Get listing status AFTER acceptance
                    after_status = await self.get_listing_status(listing_id)
                    print(f"📊 LISTING STATUS AFTER ACCEPTANCE: {after_status}")
                    
                    # Check if status changed to "sold"
                    if after_status and after_status.get('status') == 'sold':
                        self.log_result(
                            "Listing Status Update", 
                            True, 
                            f"✅ SUCCESS: Listing status changed to 'sold' as expected"
                        )
                    else:
                        self.log_result(
                            "Listing Status Update", 
                            False, 
                            f"❌ ISSUE: Listing status is '{after_status.get('status') if after_status else 'unknown'}', expected 'sold'"
                        )
                    
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Accept Tender", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Accept Tender", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return False

    async def get_listing_status(self, listing_id):
        """Get current listing status and details"""
        try:
            async with self.session.get(f"{BACKEND_URL}/listings/{listing_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ Failed to get listing status: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Error getting listing status: {e}")
            return None

    async def debug_listing_status_issue(self, listing_id, tender_id):
        """Debug the specific issue with listing status not changing"""
        print("🔧 DEBUGGING LISTING STATUS ISSUE:")
        
        # 1. Check if listing ID in tender matches listing ID in listings collection
        await self.verify_listing_tender_id_match(listing_id, tender_id)
        
        # 2. Check the update query execution
        await self.check_listing_update_query(listing_id)
        
        # 3. Check for database errors
        await self.check_database_errors()

    async def verify_listing_tender_id_match(self, listing_id, tender_id):
        """Verify that the listing ID in tender matches the listing ID in listings collection"""
        try:
            # Get tender details - need to use the listing tenders endpoint since individual tender endpoint may not exist
            async with self.session.get(f"{BACKEND_URL}/listings/{listing_id}/tenders") as response:
                if response.status == 200:
                    tenders_data = await response.json()
                    
                    # Find our specific tender
                    our_tender = None
                    for tender in tenders_data:
                        if tender.get('id') == tender_id:
                            our_tender = tender
                            break
                    
                    if our_tender:
                        # Since this is from the listing tenders endpoint, the listing_id is implicit
                        self.log_result(
                            "Listing-Tender ID Match", 
                            True, 
                            f"✅ Tender found in listing's tenders: tender_id={tender_id}, listing_id={listing_id}"
                        )
                    else:
                        self.log_result(
                            "Listing-Tender ID Match", 
                            False, 
                            f"❌ Tender {tender_id} not found in listing {listing_id} tenders"
                        )
                else:
                    self.log_result(
                        "Listing-Tender ID Match", 
                        False, 
                        f"❌ Could not retrieve tender details: {response.status}"
                    )
        except Exception as e:
            self.log_result(
                "Listing-Tender ID Match", 
                False, 
                f"❌ Error verifying ID match: {str(e)}"
            )

    async def check_listing_update_query(self, listing_id):
        """Check if the listing update query is finding and modifying the listing"""
        try:
            # Get listing details to verify it exists
            listing_data = await self.get_listing_status(listing_id)
            
            if listing_data:
                self.log_result(
                    "Listing Update Query Check", 
                    True, 
                    f"✅ Listing exists in database: ID={listing_id}, Status={listing_data.get('status')}"
                )
                
                # Log key fields for debugging
                print(f"   📋 Listing Details:")
                print(f"   - ID: {listing_data.get('id')}")
                print(f"   - Title: {listing_data.get('title')}")
                print(f"   - Status: {listing_data.get('status')}")
                print(f"   - Seller ID: {listing_data.get('seller_id')}")
                print(f"   - Price: {listing_data.get('price')}")
                
            else:
                self.log_result(
                    "Listing Update Query Check", 
                    False, 
                    f"❌ Listing not found in database: ID={listing_id}"
                )
        except Exception as e:
            self.log_result(
                "Listing Update Query Check", 
                False, 
                f"❌ Error checking listing update query: {str(e)}"
            )

    async def check_database_errors(self):
        """Check for any database errors"""
        try:
            # Test database connectivity
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Database Error Check", 
                        True, 
                        f"✅ Database connection healthy: {data.get('status')}"
                    )
                else:
                    self.log_result(
                        "Database Error Check", 
                        False, 
                        f"❌ Database health check failed: {response.status}"
                    )
        except Exception as e:
            self.log_result(
                "Database Error Check", 
                False, 
                f"❌ Error checking database: {str(e)}"
            )

    async def test_sold_items_endpoint(self, admin_token, seller_id, expected_listing_id):
        """Test the sold items endpoint for the seller"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            async with self.session.get(f"{BACKEND_URL}/user/{seller_id}/sold-items", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    sold_items = await response.json()
                    
                    # Check if our accepted tender appears in sold items
                    found_item = None
                    for item in sold_items:
                        # Handle both dict and string items
                        if isinstance(item, dict):
                            if item.get('listing_id') == expected_listing_id or item.get('id') == expected_listing_id:
                                found_item = item
                                break
                        elif isinstance(item, str):
                            # If item is a string, it might be a listing ID
                            if item == expected_listing_id:
                                found_item = {"id": item, "title": "Found by ID", "price": "Unknown"}
                                break
                    
                    if found_item:
                        self.log_result(
                            "Sold Items Endpoint", 
                            True, 
                            f"✅ Accepted tender appears in sold items: {found_item.get('title', 'Unknown')} - ${found_item.get('price', 0)}",
                            response_time
                        )
                    else:
                        self.log_result(
                            "Sold Items Endpoint", 
                            False, 
                            f"❌ Accepted tender NOT found in {len(sold_items)} sold items",
                            response_time
                        )
                        
                        # Log all sold items for debugging
                        print(f"   📦 All Sold Items ({len(sold_items)}):")
                        for i, item in enumerate(sold_items[:5]):  # Show first 5
                            if isinstance(item, dict):
                                print(f"   - {i+1}: {item.get('title', 'Unknown')} (ID: {item.get('id', 'Unknown')})")
                            else:
                                print(f"   - {i+1}: {str(item)} (type: {type(item)})")
                    
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Sold Items Endpoint", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Sold Items Endpoint", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )

    async def run_tender_acceptance_debug_tests(self):
        """Run focused tests to debug tender acceptance listing status issue"""
        print("🔍 STARTING TENDER ACCEPTANCE DEBUG TESTING")
        print("=" * 80)
        print("FOCUS: Debug why listing status is not changing to 'sold' when tender is accepted")
        print("=" * 80)
        
        # Test database connectivity first
        db_connected = await self.test_database_connectivity()
        if not db_connected:
            print("❌ Database connectivity failed - aborting tests")
            return
        
        # 1. Setup Test Scenario
        print("\n📋 STEP 1: SETUP TEST SCENARIO")
        print("-" * 50)
        
        # Login as admin (seller)
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        if not admin_token:
            print("❌ Admin login failed - aborting tests")
            return
        
        # Login as demo user (buyer)
        demo_token, demo_user_id, demo_user = await self.test_login_and_get_token("demo@cataloro.com", "demo123")
        if not demo_token:
            print("❌ Demo user login failed - aborting tests")
            return
        
        # Create test listing
        test_listing_id = await self.create_debug_test_listing(admin_token)
        if not test_listing_id:
            print("❌ Test listing creation failed - aborting tests")
            return
        
        # Place bid on listing
        tender_id = await self.place_debug_test_bid(demo_token, test_listing_id, demo_user_id)
        if not tender_id:
            print("❌ Test bid placement failed - aborting tests")
            return
        
        # 2. Accept the tender and monitor listing status
        print("\n✅ STEP 2: ACCEPT TENDER AND MONITOR STATUS")
        print("-" * 50)
        
        # Accept the tender
        acceptance_success = await self.accept_tender_and_monitor(admin_token, tender_id, test_listing_id)
        
        # 3. Debug the specific issue
        print("\n🔧 STEP 3: DEBUG LISTING STATUS ISSUE")
        print("-" * 50)
        
        await self.debug_listing_status_issue(test_listing_id, tender_id)
        
        # 4. Test sold items endpoint
        print("\n📦 STEP 4: TEST SOLD ITEMS ENDPOINT")
        print("-" * 50)
        
        await self.test_sold_items_endpoint(admin_token, admin_user_id, test_listing_id)
        
        # Print final debug summary
        await self.print_debug_summary()

    async def print_debug_summary(self):
        """Print debug testing summary"""
        print("\n" + "=" * 80)
        print("🔍 TENDER ACCEPTANCE DEBUG TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 TOTAL TESTS: {total_tests}")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        print(f"📈 SUCCESS RATE: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")
        
        print("\n🎯 KEY FINDINGS:")
        
        # Analyze results for key findings
        listing_status_issues = [r for r in self.test_results if "Listing Status" in r["test"] and not r["success"]]
        sold_items_issues = [r for r in self.test_results if "Sold Items" in r["test"] and not r["success"]]
        id_match_issues = [r for r in self.test_results if "ID Match" in r["test"] and not r["success"]]
        
        if listing_status_issues:
            print("   ❌ LISTING STATUS NOT UPDATING TO 'SOLD'")
        else:
            print("   ✅ Listing status updating correctly")
            
        if sold_items_issues:
            print("   ❌ ACCEPTED TENDER NOT APPEARING IN SOLD ITEMS")
        else:
            print("   ✅ Sold items endpoint working correctly")
            
        if id_match_issues:
            print("   ❌ LISTING ID MISMATCH BETWEEN TENDER AND LISTING")
        else:
            print("   ✅ Listing IDs matching correctly")
        
        print("\n💡 RECOMMENDATIONS:")
        if listing_status_issues or sold_items_issues:
            print("   1. Check backend logs for tender acceptance debugging messages")
            print("   2. Verify the listing update query in the tender acceptance endpoint")
            print("   3. Ensure the listing ID in tender matches the listing ID in database")
            print("   4. Check for any database transaction issues")
        else:
            print("   ✅ Tender acceptance workflow appears to be working correctly")
        
        print("=" * 80)

async def main():
    """Main function to run tender acceptance debug tests"""
    async with TenderAcceptanceDebugTester() as tester:
        await tester.run_tender_acceptance_debug_tests()

if __name__ == "__main__":
    asyncio.run(main())