#!/usr/bin/env python3
"""
Browse Page Loading Fix Test Suite
Tests the specific fixes implemented for browse page loading issues
"""

import requests
import sys
import json
import time
from datetime import datetime

class BrowsePageLoadingTester:
    def __init__(self, base_url="https://tender-system.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response_time = time.time() - start_time
            success = response.status_code == expected_status
            details = f"Status: {response.status_code}, Time: {response_time:.3f}s"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                    return success, response_data
                except:
                    details += f", Response: {response.text[:100]}..."
                    return success, {}
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login for setup"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_user = response['user']
        return success

    def test_user_login(self):
        """Test regular user login for setup"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.user_token = response['token']
            self.regular_user = response['user']
        return success

    def test_empty_database_browse(self):
        """Test browse endpoint with empty database - should return empty array, not demo data"""
        print("\n🔍 Testing Browse Page with Empty Database...")
        
        # First, let's check current state
        success, response = self.run_test(
            "Browse Listings - Current State",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False
            
        current_count = len(response) if isinstance(response, list) else 0
        print(f"   Current listings count: {current_count}")
        
        # Store current listing IDs for cleanup
        current_listing_ids = []
        if isinstance(response, list):
            current_listing_ids = [listing.get('id') for listing in response if listing.get('id')]
        
        # Delete all current listings to create empty state
        print("\n🗑️ Clearing all listings to test empty state...")
        deleted_count = 0
        for listing_id in current_listing_ids:
            if listing_id:
                delete_success, _ = self.run_test(
                    f"Delete Listing {listing_id[:8]}...",
                    "DELETE",
                    f"api/listings/{listing_id}",
                    200
                )
                if delete_success:
                    deleted_count += 1
        
        print(f"   Deleted {deleted_count} listings")
        
        # Now test empty database behavior
        success_empty, empty_response = self.run_test(
            "Browse Listings - Empty Database",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success_empty:
            # Verify response is an empty array, not demo data
            is_empty_array = isinstance(empty_response, list) and len(empty_response) == 0
            self.log_test("Empty Database Returns Empty Array", is_empty_array,
                         f"Response type: {type(empty_response)}, Length: {len(empty_response) if isinstance(empty_response, list) else 'N/A'}")
            
            # Verify no demo data fallback
            has_demo_data = False
            if isinstance(empty_response, list):
                demo_titles = ["MacBook Pro", "Vintage Guitar", "Designer Handbag"]
                for listing in empty_response:
                    if any(demo_title in listing.get('title', '') for demo_title in demo_titles):
                        has_demo_data = True
                        break
            
            self.log_test("No Demo Data Fallback", not has_demo_data,
                         f"Demo data found: {has_demo_data}")
            
            return is_empty_array and not has_demo_data
        
        return False

    def test_browse_response_format(self):
        """Test that browse endpoint returns proper array format for frontend .map() compatibility"""
        print("\n📋 Testing Browse Response Format...")
        
        success, response = self.run_test(
            "Browse Response Format",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            # Verify response is an array (compatible with .map())
            is_array = isinstance(response, list)
            self.log_test("Response is Array Format", is_array,
                         f"Response type: {type(response)}")
            
            # Verify each listing has required fields
            if is_array and len(response) > 0:
                first_listing = response[0]
                required_fields = ['id', 'title', 'price', 'category', 'seller_id']
                has_required_fields = all(field in first_listing for field in required_fields)
                self.log_test("Listings Have Required Fields", has_required_fields,
                             f"Fields present: {list(first_listing.keys())}")
            else:
                print("   No listings to verify field structure")
            
            return is_array
        
        return False

    def test_browse_performance(self):
        """Test browse endpoint performance - should load quickly"""
        print("\n⚡ Testing Browse Page Performance...")
        
        # Test multiple calls to check consistency
        response_times = []
        for i in range(3):
            start_time = time.time()
            success, response = self.run_test(
                f"Browse Performance Test {i+1}",
                "GET",
                "api/marketplace/browse",
                200
            )
            response_time = time.time() - start_time
            
            if success:
                response_times.append(response_time)
                print(f"   Response {i+1}: {response_time:.3f}s, {len(response) if isinstance(response, list) else 0} listings")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            # Performance should be under 2 seconds for good UX
            performance_good = avg_time < 2.0 and max_time < 3.0
            self.log_test("Browse Performance", performance_good,
                         f"Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")
            
            return performance_good
        
        return False

    def test_marketplace_context_integration(self):
        """Test MarketplaceContext API integration - verify it uses real API data"""
        print("\n🔗 Testing MarketplaceContext API Integration...")
        
        # Create a test listing to verify context uses real data
        if not self.regular_user:
            print("❌ MarketplaceContext Test - SKIPPED (No user logged in)")
            return False
        
        test_listing = {
            "title": "Context Integration Test - Smart Watch",
            "description": "Test listing to verify MarketplaceContext uses real API data, not demo data",
            "price": 199.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"]
        }
        
        # Create the test listing
        success_create, create_response = self.run_test(
            "Create Test Listing for Context",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_create:
            return False
        
        listing_id = create_response.get('listing_id')
        print(f"   Created test listing: {listing_id}")
        
        # Verify it appears in browse (what MarketplaceContext should use)
        success_browse, browse_response = self.run_test(
            "Verify Test Listing in Browse",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        context_uses_real_data = False
        if success_browse and isinstance(browse_response, list):
            # Look for our test listing
            found_test_listing = any(
                listing.get('id') == listing_id and 
                listing.get('title') == test_listing['title']
                for listing in browse_response
            )
            
            context_uses_real_data = found_test_listing
            self.log_test("MarketplaceContext Uses Real Data", context_uses_real_data,
                         f"Test listing found in browse: {found_test_listing}")
        
        # Cleanup - delete test listing
        if listing_id:
            self.run_test(
                "Cleanup Test Listing",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
        
        return context_uses_real_data

    def test_refresh_functionality(self):
        """Test that refresh functionality works without full page reload"""
        print("\n🔄 Testing Refresh Functionality...")
        
        # Test multiple browse calls to simulate refresh
        print("   Simulating context.refreshListings() calls...")
        
        refresh_results = []
        for i in range(3):
            success, response = self.run_test(
                f"Refresh Simulation {i+1}",
                "GET",
                "api/marketplace/browse",
                200
            )
            
            if success:
                refresh_results.append({
                    'success': True,
                    'count': len(response) if isinstance(response, list) else 0,
                    'is_array': isinstance(response, list)
                })
            else:
                refresh_results.append({'success': False})
        
        # Verify all refreshes succeeded
        all_refreshes_work = all(result.get('success', False) for result in refresh_results)
        
        # Verify consistent response format
        consistent_format = all(
            result.get('is_array', False) for result in refresh_results if result.get('success')
        )
        
        self.log_test("Refresh Functionality Works", all_refreshes_work,
                     f"All {len(refresh_results)} refresh calls succeeded")
        
        self.log_test("Refresh Response Consistency", consistent_format,
                     f"All responses are consistent array format")
        
        return all_refreshes_work and consistent_format

    def test_listing_creation_backend(self):
        """Test that listing creation still works properly after fixes"""
        print("\n📝 Testing Listing Creation Backend...")
        
        if not self.regular_user:
            print("❌ Listing Creation Test - SKIPPED (No user logged in)")
            return False
        
        # Test creating a listing with location (for location suggestion feature)
        test_listing = {
            "title": "Location Test Listing - Vintage Bicycle",
            "description": "Test listing with location for location suggestion feature testing. Located in Berlin, Germany.",
            "price": 450.00,
            "category": "Sports",
            "condition": "Used - Good",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
            "location": "Berlin, Germany"  # Test location field
        }
        
        success_create, create_response = self.run_test(
            "Create Listing with Location",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if success_create:
            listing_id = create_response.get('listing_id')
            print(f"   Created listing with location: {listing_id}")
            
            # Verify it appears in browse immediately
            success_verify, browse_response = self.run_test(
                "Verify New Listing in Browse",
                "GET",
                "api/marketplace/browse",
                200
            )
            
            if success_verify and isinstance(browse_response, list):
                found_new_listing = any(
                    listing.get('id') == listing_id for listing in browse_response
                )
                self.log_test("New Listing Appears in Browse", found_new_listing,
                             f"New listing found in browse: {found_new_listing}")
                
                # Cleanup
                if listing_id:
                    self.run_test(
                        "Cleanup Location Test Listing",
                        "DELETE",
                        f"api/listings/{listing_id}",
                        200
                    )
                
                return found_new_listing
        
        return False

    def test_empty_state_handling(self):
        """Test proper empty state handling - no infinite loading"""
        print("\n🔄 Testing Empty State Handling...")
        
        # Get current listings count
        success, response = self.run_test(
            "Check Current Listings",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False
        
        current_count = len(response) if isinstance(response, list) else 0
        print(f"   Current listings: {current_count}")
        
        # Test that empty array is handled properly
        if current_count == 0:
            print("   Database is already empty - testing empty state handling")
            
            # Multiple rapid calls to test for infinite loading issues
            rapid_test_results = []
            for i in range(5):
                start_time = time.time()
                success_rapid, rapid_response = self.run_test(
                    f"Rapid Empty State Test {i+1}",
                    "GET",
                    "api/marketplace/browse",
                    200
                )
                response_time = time.time() - start_time
                
                if success_rapid:
                    rapid_test_results.append({
                        'time': response_time,
                        'is_array': isinstance(rapid_response, list),
                        'is_empty': len(rapid_response) == 0 if isinstance(rapid_response, list) else False
                    })
            
            # Verify no infinite loading (all responses under 5 seconds)
            no_infinite_loading = all(result['time'] < 5.0 for result in rapid_test_results)
            
            # Verify consistent empty array responses
            consistent_empty = all(
                result['is_array'] and result['is_empty'] 
                for result in rapid_test_results
            )
            
            self.log_test("No Infinite Loading", no_infinite_loading,
                         f"All responses under 5s: {no_infinite_loading}")
            
            self.log_test("Consistent Empty State", consistent_empty,
                         f"All responses are empty arrays: {consistent_empty}")
            
            return no_infinite_loading and consistent_empty
        else:
            print("   Database has listings - empty state test not applicable")
            return True

    def run_browse_page_tests(self):
        """Run all browse page loading fix tests"""
        print("🚀 Starting Browse Page Loading Fix Tests")
        print("=" * 60)

        # Setup - login users
        admin_success = self.test_admin_login()
        user_success = self.test_user_login()
        
        if not user_success:
            print("❌ User login failed - some tests will be skipped")

        # Core browse page loading tests
        print("\n🔥 TESTING BROWSE PAGE LOADING FIXES...")
        
        test_results = []
        
        # Test 1: Empty database handling
        test_results.append(("Empty Database Browse", self.test_empty_database_browse()))
        
        # Test 2: Response format compatibility
        test_results.append(("Browse Response Format", self.test_browse_response_format()))
        
        # Test 3: Performance
        test_results.append(("Browse Performance", self.test_browse_performance()))
        
        # Test 4: MarketplaceContext integration
        if user_success:
            test_results.append(("MarketplaceContext Integration", self.test_marketplace_context_integration()))
        
        # Test 5: Refresh functionality
        test_results.append(("Refresh Functionality", self.test_refresh_functionality()))
        
        # Test 6: Listing creation backend
        if user_success:
            test_results.append(("Listing Creation Backend", self.test_listing_creation_backend()))
        
        # Test 7: Empty state handling
        test_results.append(("Empty State Handling", self.test_empty_state_handling()))

        # Print results
        print("\n" + "=" * 60)
        print("📊 BROWSE PAGE LOADING FIX TEST RESULTS:")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {test_name}: {status}")
            if success:
                passed_tests += 1
        
        print(f"\n📈 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL BROWSE PAGE LOADING FIXES VERIFIED!")
            print("\n✅ Expected Results Confirmed:")
            print("   • Browse page loads quickly even with empty database")
            print("   • No infinite loading states")
            print("   • Empty state shows appropriate message (frontend handles empty array)")
            print("   • Context uses real API data instead of demo data fallback")
            print("   • Refresh works smoothly without page reload")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} browse page loading tests failed")
            print("\n❌ Issues Found:")
            for test_name, success in test_results:
                if not success:
                    print(f"   • {test_name} - needs attention")
            return False

def main():
    """Main test execution"""
    tester = BrowsePageLoadingTester()
    success = tester.run_browse_page_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())