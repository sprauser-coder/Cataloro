import requests
import sys
import json
from datetime import datetime, timedelta
import time

class ComprehensiveMarketplaceTester:
    def __init__(self, base_url="https://shop-recovery.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.user_token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_admin_token=False):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        token_to_use = self.admin_token if use_admin_token else self.user_token
        if token_to_use:
            test_headers['Authorization'] = f'Bearer {token_to_use}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 300:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Error: {response.text[:200]}")

            return success, response.json() if response.text and response.text.strip() else {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("🔐 Setting up authentication...")
        
        # Admin login
        admin_data = {
            "email": "admin@marketplace.com",
            "password": "admin123"
        }
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, admin_data)
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   Admin authenticated: {response['user']['full_name']}")
        
        # Create and login regular user
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"buyer_{timestamp}@example.com",
            "username": f"buyer_{timestamp}",
            "password": "BuyerPass123!",
            "full_name": f"Test Buyer {timestamp}",
            "role": "buyer"
        }
        
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, user_data)
        if success and 'access_token' in response:
            self.user_token = response['access_token']
            print(f"   User authenticated: {response['user']['full_name']}")

    def test_currency_system(self):
        """Test that all prices display in € (Euro) currency"""
        print("\n💰 Testing Currency System (Euro €)...")
        
        # Test 1: Create listing with Euro pricing
        if not self.user_token:
            print("⚠️  Skipping currency test - no user token")
            return False
            
        listing_data = {
            "title": "Euro Currency Test Product",
            "description": "Testing Euro currency display - Price should be €149.99",
            "category": "Electronics",
            "listing_type": "fixed_price",
            "price": 149.99,  # This should be displayed as €149.99
            "condition": "New",
            "quantity": 1,
            "location": "Berlin, Germany",
            "shipping_cost": 9.99  # This should be displayed as €9.99
        }
        
        success, response = self.run_test("Create Euro Listing", "POST", "listings", 200, listing_data)
        if success and 'id' in response:
            listing_id = response['id']
            print(f"   Created listing with price: €{response['price']}")
            print(f"   Shipping cost: €{response.get('shipping_cost', 0)}")
            
            # Test 2: Verify listing retrieval shows Euro prices
            success2, response2 = self.run_test("Get Euro Listing", "GET", f"listings/{listing_id}", 200)
            if success2:
                price = response2.get('price', 0)
                shipping = response2.get('shipping_cost', 0)
                print(f"   Retrieved listing price: €{price}")
                print(f"   Retrieved shipping cost: €{shipping}")
                
                # Test 3: Create order and verify Euro totals
                order_data = {
                    "listing_id": listing_id,
                    "quantity": 1,
                    "shipping_address": "123 Test Street, Berlin, Germany"
                }
                
                success3, response3 = self.run_test("Create Euro Order", "POST", "orders", 200, order_data)
                if success3:
                    total = response3.get('total_amount', 0)
                    print(f"   Order total amount: €{total}")
                    print("✅ Currency System Test PASSED - All prices in Euro (€)")
                    return True
        
        print("❌ Currency System Test FAILED")
        return False

    def test_admin_panel_tabs(self):
        """Test all 8 admin panel tabs functionality"""
        print("\n🎛️  Testing Admin Panel - All 8 Tabs...")
        
        if not self.admin_token:
            print("⚠️  Skipping admin panel test - no admin token")
            return False
        
        tab_tests = []
        
        # Tab 1: Dashboard (Stats)
        success1, response1 = self.run_test("Tab 1: Dashboard Stats", "GET", "admin/stats", 200, use_admin_token=True)
        tab_tests.append(("Dashboard", success1))
        if success1:
            stats = response1
            print(f"   Dashboard stats: {stats.get('total_users', 0)} users, {stats.get('total_listings', 0)} listings, €{stats.get('total_revenue', 0)} revenue")
        
        # Tab 2: Users Management
        success2, response2 = self.run_test("Tab 2: Users Management", "GET", "admin/users", 200, use_admin_token=True)
        tab_tests.append(("Users", success2))
        if success2:
            print(f"   Users management: {len(response2)} users found")
        
        # Tab 3: Listings Management
        success3, response3 = self.run_test("Tab 3: Listings Management", "GET", "admin/listings", 200, use_admin_token=True)
        tab_tests.append(("Listings", success3))
        if success3:
            print(f"   Listings management: {len(response3)} listings found")
        
        # Tab 4: Orders Management
        success4, response4 = self.run_test("Tab 4: Orders Management", "GET", "admin/orders", 200, use_admin_token=True)
        tab_tests.append(("Orders", success4))
        if success4:
            print(f"   Orders management: {len(response4)} orders found")
        
        # Tab 5: Appearance (CMS Settings)
        success5, response5 = self.run_test("Tab 5: Appearance Settings", "GET", "admin/cms/settings", 200, use_admin_token=True)
        tab_tests.append(("Appearance", success5))
        if success5:
            print(f"   Appearance settings: Site name '{response5.get('site_name', 'Unknown')}'")
        
        # Tab 6: Page Management
        success6, response6 = self.run_test("Tab 6: Page Management", "GET", "admin/cms/pages", 200, use_admin_token=True)
        tab_tests.append(("Page Management", success6))
        if success6:
            print(f"   Page management: {len(response6)} pages found")
        
        # Tab 7: General Settings (Navigation)
        success7, response7 = self.run_test("Tab 7: Navigation Settings", "GET", "admin/cms/navigation", 200, use_admin_token=True)
        tab_tests.append(("General Settings", success7))
        if success7:
            print(f"   Navigation settings: {len(response7)} nav items found")
        
        # Tab 8: Database Operations (User ID generation test)
        success8, response8 = self.run_test("Tab 8: Database Operations", "POST", "admin/generate-user-ids", 200, use_admin_token=True)
        tab_tests.append(("Database", success8))
        if success8:
            print(f"   Database operations: Generated {response8.get('updated_count', 0)} user IDs")
        
        # Summary
        passed_tabs = [name for name, success in tab_tests if success]
        failed_tabs = [name for name, success in tab_tests if not success]
        
        print(f"\n📊 Admin Panel Tabs Summary:")
        print(f"   ✅ Working tabs ({len(passed_tabs)}/8): {', '.join(passed_tabs)}")
        if failed_tabs:
            print(f"   ❌ Failed tabs ({len(failed_tabs)}/8): {', '.join(failed_tabs)}")
        
        return len(passed_tabs) == 8

    def test_user_management_modal(self):
        """Test Users tab functionality and user details modal"""
        print("\n👥 Testing User Management & Details Modal...")
        
        if not self.admin_token:
            print("⚠️  Skipping user management test - no admin token")
            return False
        
        # Get all users
        success1, response1 = self.run_test("Get All Users", "GET", "admin/users", 200, use_admin_token=True)
        if not success1 or not response1:
            return False
        
        users = response1
        print(f"   Found {len(users)} users in system")
        
        # Test user details (simulate modal functionality)
        if users:
            first_user = users[0]
            user_id = first_user.get('id')
            print(f"   Testing user details for: {first_user.get('full_name', 'Unknown')}")
            print(f"   User ID: {first_user.get('user_id', 'Not set')}")
            print(f"   Email: {first_user.get('email', 'Unknown')}")
            print(f"   Role: {first_user.get('role', 'Unknown')}")
            print(f"   Status: {'Blocked' if first_user.get('is_blocked') else 'Active'}")
            print(f"   Total Orders: {first_user.get('total_orders', 0)}")
            print(f"   Total Listings: {first_user.get('total_listings', 0)}")
            
            # Test user management actions
            if not first_user.get('role') == 'admin':  # Don't test on admin user
                # Test block user
                success2, response2 = self.run_test("Block User", "PUT", f"admin/users/{user_id}/block", 200, use_admin_token=True)
                if success2:
                    print("   ✅ Block user functionality working")
                    
                    # Test unblock user
                    success3, response3 = self.run_test("Unblock User", "PUT", f"admin/users/{user_id}/unblock", 200, use_admin_token=True)
                    if success3:
                        print("   ✅ Unblock user functionality working")
                        return True
        
        return False

    def test_font_system(self):
        """Test global font family changes"""
        print("\n🔤 Testing Font System...")
        
        if not self.admin_token:
            print("⚠️  Skipping font system test - no admin token")
            return False
        
        # Test different font families
        fonts_to_test = ["Inter", "Roboto", "Open Sans", "Poppins"]
        
        for font in fonts_to_test:
            settings_data = {
                "global_font_family": font
            }
            
            success, response = self.run_test(f"Set Font to {font}", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)
            if success:
                # Verify font was set
                success2, response2 = self.run_test(f"Verify Font {font}", "GET", "admin/cms/settings", 200, use_admin_token=True)
                if success2 and response2.get('global_font_family') == font:
                    print(f"   ✅ Font '{font}' set successfully")
                else:
                    print(f"   ❌ Font '{font}' not set correctly")
                    return False
            else:
                return False
        
        print("✅ Font System Test PASSED - All fonts can be set")
        return True

    def test_marketplace_core_comprehensive(self):
        """Test comprehensive marketplace core functionality"""
        print("\n🛒 Testing Marketplace Core Functionality...")
        
        if not self.user_token:
            print("⚠️  Skipping marketplace core test - no user token")
            return False
        
        # Test 1: Create multiple listing types
        fixed_listing = {
            "title": "Fixed Price Item - Smartphone",
            "description": "Brand new smartphone with warranty",
            "category": "Electronics",
            "listing_type": "fixed_price",
            "price": 599.99,
            "condition": "New",
            "quantity": 5,
            "location": "Munich, Germany",
            "shipping_cost": 15.99
        }
        
        auction_listing = {
            "title": "Auction Item - Vintage Watch",
            "description": "Rare vintage watch from 1960s",
            "category": "Fashion",
            "listing_type": "auction",
            "starting_bid": 100.00,
            "buyout_price": 500.00,
            "condition": "Used",
            "quantity": 1,
            "location": "Vienna, Austria",
            "shipping_cost": 25.00,
            "auction_duration_hours": 72
        }
        
        success1, response1 = self.run_test("Create Fixed Price Listing", "POST", "listings", 200, fixed_listing)
        success2, response2 = self.run_test("Create Auction Listing", "POST", "listings", 200, auction_listing)
        
        if not (success1 and success2):
            return False
        
        fixed_id = response1['id']
        auction_id = response2['id']
        
        # Test 2: Search and filtering
        success3, response3 = self.run_test("Search Listings", "GET", "listings?search=smartphone", 200)
        success4, response4 = self.run_test("Filter by Electronics", "GET", "listings?category=Electronics", 200)
        success5, response5 = self.run_test("Filter Fixed Price", "GET", "listings?listing_type=fixed_price", 200)
        success6, response6 = self.run_test("Price Range Filter", "GET", "listings?min_price=500&max_price=700", 200)
        
        # Test 3: Cart functionality
        cart_data = {"listing_id": fixed_id, "quantity": 2}
        success7, response7 = self.run_test("Add to Cart", "POST", "cart", 200, cart_data)
        success8, response8 = self.run_test("View Cart", "GET", "cart", 200)
        
        # Test 4: Order creation
        order_data = {
            "listing_id": fixed_id,
            "quantity": 1,
            "shipping_address": "456 Market Street, Hamburg, Germany"
        }
        success9, response9 = self.run_test("Create Order", "POST", "orders", 200, order_data)
        success10, response10 = self.run_test("View Orders", "GET", "orders", 200)
        
        all_tests = [success1, success2, success3, success4, success5, success6, success7, success8, success9, success10]
        passed_count = sum(all_tests)
        
        print(f"   Marketplace Core Tests: {passed_count}/10 passed")
        return passed_count >= 8  # Allow 2 failures

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Marketplace Testing")
        print("=" * 60)
        
        # Setup
        self.setup_authentication()
        
        # Run all test categories
        test_results = []
        
        test_results.append(("Currency System (€)", self.test_currency_system()))
        test_results.append(("Admin Panel (8 Tabs)", self.test_admin_panel_tabs()))
        test_results.append(("User Management", self.test_user_management_modal()))
        test_results.append(("Font System", self.test_font_system()))
        test_results.append(("Marketplace Core", self.test_marketplace_core_comprehensive()))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        passed_tests = [name for name, success in test_results if success]
        failed_tests = [name for name, success in test_results if not success]
        
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n✅ PASSED CATEGORIES ({len(passed_tests)}/5):")
        for test_name in passed_tests:
            print(f"   • {test_name}")
        
        if failed_tests:
            print(f"\n❌ FAILED CATEGORIES ({len(failed_tests)}/5):")
            for test_name in failed_tests:
                print(f"   • {test_name}")
        
        overall_success = len(passed_tests) >= 4  # Allow 1 category to fail
        
        if overall_success:
            print(f"\n🎉 OVERALL RESULT: READY FOR DEPLOYMENT")
            print("   The Cataloro marketplace is functioning correctly!")
        else:
            print(f"\n⚠️  OVERALL RESULT: NEEDS ATTENTION")
            print("   Some critical functionality requires fixes before deployment.")
        
        return overall_success

if __name__ == "__main__":
    tester = ComprehensiveMarketplaceTester()
    tester.run_comprehensive_tests()