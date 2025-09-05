#!/usr/bin/env python3
"""
CATALORO - Enhanced TendersPage Backend Testing
Testing the new sold items endpoint and TendersPage functionality
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timedelta
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-3.preview.emergentagent.com"

class TendersPageTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.admin_user = None
        self.demo_user = None
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": "✅ PASSED" if status else "❌ FAILED", 
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{result['status']} - {test_name}: {details}")
        
    async def test_health_check(self):
        """Test basic health check"""
        try:
            async with self.session.get(f"{BACKEND_URL}/api/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Health Check", True, f"Backend healthy: {data.get('app', 'Unknown')}")
                    return True
                else:
                    self.log_result("Health Check", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_result("Health Check", False, f"Error: {str(e)}")
            return False
            
    async def setup_test_users(self):
        """Setup test users for testing"""
        try:
            # Login as admin
            admin_credentials = {"email": "admin@cataloro.com", "password": "admin123"}
            async with self.session.post(f"{BACKEND_URL}/api/auth/login", json=admin_credentials) as response:
                if response.status == 200:
                    admin_data = await response.json()
                    self.admin_user = admin_data.get("user")
                    self.log_result("Admin Login", True, f"Admin ID: {self.admin_user.get('id')}")
                else:
                    self.log_result("Admin Login", False, f"Status: {response.status}")
                    return False
                    
            # Login as demo user
            demo_credentials = {"email": "demo@cataloro.com", "password": "demo123"}
            async with self.session.post(f"{BACKEND_URL}/api/auth/login", json=demo_credentials) as response:
                if response.status == 200:
                    demo_data = await response.json()
                    self.demo_user = demo_data.get("user")
                    self.log_result("Demo User Login", True, f"Demo ID: {self.demo_user.get('id')}")
                else:
                    self.log_result("Demo User Login", False, f"Status: {response.status}")
                    return False
                    
            return True
        except Exception as e:
            self.log_result("User Setup", False, f"Error: {str(e)}")
            return False
            
    async def test_sold_items_endpoint(self):
        """Test the new sold items endpoint GET /api/user/{user_id}/sold-items"""
        try:
            if not self.admin_user:
                self.log_result("Sold Items Endpoint", False, "No admin user available")
                return False
                
            user_id = self.admin_user.get('id')
            async with self.session.get(f"{BACKEND_URL}/api/user/{user_id}/sold-items") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if 'items' in data and 'stats' in data:
                        stats = data.get('stats', {})
                        items = data.get('items', [])
                        
                        # Check stats structure
                        required_stats = ['totalSold', 'totalRevenue', 'averagePrice', 'thisMonth']
                        missing_stats = [stat for stat in required_stats if stat not in stats]
                        
                        if missing_stats:
                            self.log_result("Sold Items Endpoint", False, f"Missing stats: {missing_stats}")
                            return False
                            
                        # Verify data types
                        if not isinstance(stats['totalSold'], int):
                            self.log_result("Sold Items Endpoint", False, "totalSold should be integer")
                            return False
                            
                        if not isinstance(stats['totalRevenue'], (int, float)):
                            self.log_result("Sold Items Endpoint", False, "totalRevenue should be number")
                            return False
                            
                        if not isinstance(stats['averagePrice'], (int, float)):
                            self.log_result("Sold Items Endpoint", False, "averagePrice should be number")
                            return False
                            
                        if not isinstance(stats['thisMonth'], int):
                            self.log_result("Sold Items Endpoint", False, "thisMonth should be integer")
                            return False
                            
                        # Check items structure if any exist
                        if items:
                            item = items[0]
                            required_fields = ['id', 'listing', 'buyer', 'final_price', 'sold_at', 'deal_id']
                            missing_fields = [field for field in required_fields if field not in item]
                            
                            if missing_fields:
                                self.log_result("Sold Items Endpoint", False, f"Missing item fields: {missing_fields}")
                                return False
                                
                        self.log_result("Sold Items Endpoint", True, 
                                      f"Structure valid - {stats['totalSold']} sold items, €{stats['totalRevenue']:.2f} revenue")
                        return True
                    else:
                        self.log_result("Sold Items Endpoint", False, "Missing 'items' or 'stats' in response")
                        return False
                else:
                    self.log_result("Sold Items Endpoint", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_result("Sold Items Endpoint", False, f"Error: {str(e)}")
            return False
            
    async def test_tenders_overview_endpoint(self):
        """Test the tenders overview endpoint for My Listings tab"""
        try:
            if not self.admin_user:
                self.log_result("Tenders Overview Endpoint", False, "No admin user available")
                return False
                
            user_id = self.admin_user.get('id')
            async with self.session.get(f"{BACKEND_URL}/api/tenders/seller/{user_id}/overview") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Should return array of listings with tender information
                    if isinstance(data, list):
                        self.log_result("Tenders Overview Endpoint", True, 
                                      f"Retrieved {len(data)} listings with tender data")
                        
                        # Check structure if data exists
                        if data:
                            item = data[0]
                            required_fields = ['listing', 'seller', 'tender_count', 'highest_offer', 'tenders']
                            missing_fields = [field for field in required_fields if field not in item]
                            
                            if missing_fields:
                                self.log_result("Tenders Overview Structure", False, f"Missing fields: {missing_fields}")
                                return False
                            else:
                                self.log_result("Tenders Overview Structure", True, "All required fields present")
                                
                        return True
                    else:
                        self.log_result("Tenders Overview Endpoint", False, "Response should be array")
                        return False
                else:
                    self.log_result("Tenders Overview Endpoint", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_result("Tenders Overview Endpoint", False, f"Error: {str(e)}")
            return False
            
    async def test_buyer_tenders_endpoint(self):
        """Test the buyer tenders endpoint for Tenders tab"""
        try:
            if not self.demo_user:
                self.log_result("Buyer Tenders Endpoint", False, "No demo user available")
                return False
                
            user_id = self.demo_user.get('id')
            async with self.session.get(f"{BACKEND_URL}/api/tenders/buyer/{user_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Should return array of tenders
                    if isinstance(data, list):
                        self.log_result("Buyer Tenders Endpoint", True, 
                                      f"Retrieved {len(data)} tenders for buyer")
                        
                        # Check structure if data exists
                        if data:
                            tender = data[0]
                            required_fields = ['id', 'offer_amount', 'status', 'created_at', 'listing', 'seller']
                            missing_fields = [field for field in required_fields if field not in tender]
                            
                            if missing_fields:
                                self.log_result("Buyer Tenders Structure", False, f"Missing fields: {missing_fields}")
                                return False
                            else:
                                self.log_result("Buyer Tenders Structure", True, "All required fields present")
                                
                        return True
                    else:
                        self.log_result("Buyer Tenders Endpoint", False, "Response should be array")
                        return False
                else:
                    self.log_result("Buyer Tenders Endpoint", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_result("Buyer Tenders Endpoint", False, f"Error: {str(e)}")
            return False
            
    async def test_create_test_data(self):
        """Create test data for comprehensive testing"""
        try:
            if not self.admin_user:
                self.log_result("Create Test Data", False, "No admin user available")
                return False
                
            # Create a test listing
            listing_data = {
                "title": "Test Catalyst for Sold Items Testing",
                "description": "High-quality catalyst for testing sold items functionality",
                "price": 850.0,
                "category": "Automotive",
                "condition": "Used",
                "seller_id": self.admin_user.get('id'),
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"],
                "tags": ["catalyst", "automotive", "test"],
                "features": ["High efficiency", "Tested quality"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/api/listings", json=listing_data) as response:
                if response.status == 200:
                    listing_response = await response.json()
                    listing_id = listing_response.get('listing_id')
                    self.log_result("Create Test Listing", True, f"Created listing: {listing_id}")
                    
                    # Create a test tender from demo user
                    if self.demo_user and listing_id:
                        tender_data = {
                            "listing_id": listing_id,
                            "buyer_id": self.demo_user.get('id'),
                            "offer_amount": 900.0
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/api/tenders/submit", json=tender_data) as tender_response:
                            if tender_response.status == 200:
                                tender_result = await tender_response.json()
                                tender_id = tender_result.get('tender_id')
                                self.log_result("Create Test Tender", True, f"Created tender: {tender_id}")
                                return {"listing_id": listing_id, "tender_id": tender_id}
                            else:
                                self.log_result("Create Test Tender", False, f"Status: {tender_response.status}")
                                return {"listing_id": listing_id}
                    
                    return {"listing_id": listing_id}
                else:
                    self.log_result("Create Test Listing", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_result("Create Test Data", False, f"Error: {str(e)}")
            return False
            
    async def test_tender_acceptance_workflow(self, test_data):
        """Test tender acceptance to create sold items"""
        try:
            if not test_data or 'tender_id' not in test_data:
                self.log_result("Tender Acceptance Workflow", False, "No tender ID available")
                return False
                
            tender_id = test_data['tender_id']
            
            # Accept the tender
            acceptance_data = {
                "seller_id": self.admin_user.get('id')
            }
            
            async with self.session.put(f"{BACKEND_URL}/api/tenders/{tender_id}/accept", json=acceptance_data) as response:
                if response.status == 200:
                    self.log_result("Tender Acceptance", True, "Tender accepted successfully")
                    
                    # Wait a moment for processing
                    await asyncio.sleep(1)
                    
                    # Now test sold items endpoint again to see if it includes the new sale
                    user_id = self.admin_user.get('id')
                    async with self.session.get(f"{BACKEND_URL}/api/user/{user_id}/sold-items") as sold_response:
                        if sold_response.status == 200:
                            sold_data = await sold_response.json()
                            stats = sold_data.get('stats', {})
                            
                            self.log_result("Sold Items After Acceptance", True, 
                                          f"Updated stats - {stats.get('totalSold', 0)} sold items")
                            return True
                        else:
                            self.log_result("Sold Items After Acceptance", False, f"Status: {sold_response.status}")
                            return False
                else:
                    self.log_result("Tender Acceptance", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_result("Tender Acceptance Workflow", False, f"Error: {str(e)}")
            return False
            
    async def test_navigation_endpoints(self):
        """Test endpoints that support navigation functionality"""
        try:
            # Test browse listings (for navigation verification)
            async with self.session.get(f"{BACKEND_URL}/api/marketplace/browse") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Browse Listings Navigation", True, f"Retrieved {len(data)} listings")
                else:
                    self.log_result("Browse Listings Navigation", False, f"Status: {response.status}")
                    
            # Test user listings (My Listings functionality)
            if self.admin_user:
                user_id = self.admin_user.get('id')
                async with self.session.get(f"{BACKEND_URL}/api/user/my-listings/{user_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_result("My Listings Navigation", True, f"Retrieved {len(data)} user listings")
                    else:
                        self.log_result("My Listings Navigation", False, f"Status: {response.status}")
                        
            return True
        except Exception as e:
            self.log_result("Navigation Endpoints", False, f"Error: {str(e)}")
            return False
            
    async def test_tab_navigation_functionality(self):
        """Test that all three tabs have working backend endpoints"""
        try:
            if not self.admin_user:
                self.log_result("Tab Navigation Test", False, "No admin user available")
                return False
                
            user_id = self.admin_user.get('id')
            
            # Test My Listings tab endpoint
            async with self.session.get(f"{BACKEND_URL}/api/tenders/seller/{user_id}/overview") as response:
                my_listings_works = response.status == 200
                
            # Test Tenders tab endpoint (using demo user)
            tenders_works = False
            if self.demo_user:
                demo_id = self.demo_user.get('id')
                async with self.session.get(f"{BACKEND_URL}/api/tenders/buyer/{demo_id}") as response:
                    tenders_works = response.status == 200
                    
            # Test Sold Items tab endpoint
            async with self.session.get(f"{BACKEND_URL}/api/user/{user_id}/sold-items") as response:
                sold_items_works = response.status == 200
                
            # Summary
            working_tabs = sum([my_listings_works, tenders_works, sold_items_works])
            
            if working_tabs == 3:
                self.log_result("Tab Navigation Functionality", True, "All 3 tabs have working endpoints")
                return True
            else:
                tab_status = []
                if my_listings_works:
                    tab_status.append("My Listings ✅")
                else:
                    tab_status.append("My Listings ❌")
                    
                if tenders_works:
                    tab_status.append("Tenders ✅")
                else:
                    tab_status.append("Tenders ❌")
                    
                if sold_items_works:
                    tab_status.append("Sold Items ✅")
                else:
                    tab_status.append("Sold Items ❌")
                    
                self.log_result("Tab Navigation Functionality", False, f"{working_tabs}/3 tabs working: {', '.join(tab_status)}")
                return False
                
        except Exception as e:
            self.log_result("Tab Navigation Functionality", False, f"Error: {str(e)}")
            return False
            
    async def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Enhanced TendersPage Backend Testing...")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Basic connectivity
            if not await self.test_health_check():
                return False
                
            # Setup test users
            if not await self.setup_test_users():
                return False
                
            # Test 1: New sold items endpoint
            print("\n📊 Testing Sold Items Endpoint...")
            await self.test_sold_items_endpoint()
            
            # Test 2: Tenders overview for My Listings tab
            print("\n📋 Testing My Listings (Tenders Overview)...")
            await self.test_tenders_overview_endpoint()
            
            # Test 3: Buyer tenders for Tenders tab
            print("\n🎯 Testing Tenders Tab (Buyer Tenders)...")
            await self.test_buyer_tenders_endpoint()
            
            # Test 4: Tab navigation functionality
            print("\n🔄 Testing Tab Navigation Functionality...")
            await self.test_tab_navigation_functionality()
            
            # Test 5: Create test data for workflow testing
            print("\n🔧 Creating Test Data...")
            test_data = await self.test_create_test_data()
            
            # Test 6: Test tender acceptance workflow
            if test_data:
                print("\n✅ Testing Tender Acceptance Workflow...")
                await self.test_tender_acceptance_workflow(test_data)
            
            # Test 7: Navigation endpoints
            print("\n🧭 Testing Navigation Endpoints...")
            await self.test_navigation_endpoints()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if "✅ PASSED" in result['status'])
        failed = sum(1 for result in self.test_results if "❌ FAILED" in result['status'])
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAILED" in result['status']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 KEY FINDINGS:")
        
        # Check sold items endpoint
        sold_items_test = next((r for r in self.test_results if r['test'] == 'Sold Items Endpoint'), None)
        if sold_items_test and "✅ PASSED" in sold_items_test['status']:
            print("  ✅ Sold Items Endpoint: Working correctly with proper data structure")
        else:
            print("  ❌ Sold Items Endpoint: Issues detected")
            
        # Check tenders overview
        tenders_overview_test = next((r for r in self.test_results if r['test'] == 'Tenders Overview Endpoint'), None)
        if tenders_overview_test and "✅ PASSED" in tenders_overview_test['status']:
            print("  ✅ My Listings Tab: Tenders overview endpoint functional")
        else:
            print("  ❌ My Listings Tab: Issues with tenders overview")
            
        # Check buyer tenders
        buyer_tenders_test = next((r for r in self.test_results if r['test'] == 'Buyer Tenders Endpoint'), None)
        if buyer_tenders_test and "✅ PASSED" in buyer_tenders_test['status']:
            print("  ✅ Tenders Tab: Buyer tenders endpoint functional")
        else:
            print("  ❌ Tenders Tab: Issues with buyer tenders")
            
        # Check tab navigation
        tab_nav_test = next((r for r in self.test_results if r['test'] == 'Tab Navigation Functionality'), None)
        if tab_nav_test and "✅ PASSED" in tab_nav_test['status']:
            print("  ✅ Tab Navigation: All three tabs (My Listings, Tenders, Sold Items) working")
        else:
            print("  ❌ Tab Navigation: Some tab endpoints not working")
            
        # Check navigation
        nav_tests = [r for r in self.test_results if 'Navigation' in r['test'] and r['test'] != 'Tab Navigation Functionality']
        nav_passed = sum(1 for r in nav_tests if "✅ PASSED" in r['status'])
        if nav_passed == len(nav_tests) and nav_tests:
            print("  ✅ Navigation: All navigation endpoints working")
        else:
            print("  ❌ Navigation: Some navigation issues detected")
            
        return failed == 0

async def main():
    """Main test execution"""
    tester = TendersPageTester()
    success = await tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests passed! Enhanced TendersPage functionality is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())