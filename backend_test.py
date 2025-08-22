import requests
import sys
import json
from datetime import datetime, timedelta
import time

class MarketplaceAPITester:
    def __init__(self, base_url="https://cataloro-admin.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_listing_id = None
        self.created_order_id = None
        self.admin_token = None
        self.created_page_slug = None
        self.created_nav_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_admin_token=False):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Use admin token if specified, otherwise use regular token
        token_to_use = self.admin_token if use_admin_token else self.token
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
                    if isinstance(response_data, dict) and len(str(response_data)) < 200:
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

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_categories(self):
        """Test categories endpoint"""
        return self.run_test("Get Categories", "GET", "categories", 200)

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"test_user_{timestamp}@example.com",
            "username": f"testuser_{timestamp}",
            "password": "TestPass123!",
            "full_name": f"Test User {timestamp}",
            "role": "both",
            "phone": "1234567890",
            "address": "123 Test Street"
        }
        
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, user_data)
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Registered user ID: {self.user_id}")
        return success

    def test_user_login(self):
        """Test user login with existing credentials"""
        if not self.user_id:
            print("⚠️  Skipping login test - no registered user")
            return False
            
        # We'll use the same credentials from registration
        timestamp = datetime.now().strftime('%H%M%S')
        login_data = {
            "email": f"test_user_{timestamp}@example.com",
            "password": "TestPass123!"
        }
        
        success, response = self.run_test("User Login", "POST", "auth/login", 200, login_data)
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Login successful for user: {response['user']['full_name']}")
        return success

    def test_create_listing_fixed_price(self):
        """Test creating a fixed-price listing"""
        if not self.token:
            print("⚠️  Skipping listing creation - no auth token")
            return False
            
        listing_data = {
            "title": "Test Product - Fixed Price",
            "description": "This is a test product for fixed price listing",
            "category": "Electronics",
            "images": ["https://example.com/image1.jpg"],
            "listing_type": "fixed_price",
            "price": 99.99,
            "condition": "New",
            "quantity": 1,
            "location": "Test City",
            "shipping_cost": 5.99
        }
        
        success, response = self.run_test("Create Fixed Price Listing", "POST", "listings", 200, listing_data)
        if success and 'id' in response:
            self.created_listing_id = response['id']
            print(f"   Created listing ID: {self.created_listing_id}")
        return success

    def test_create_listing_auction(self):
        """Test creating an auction listing"""
        if not self.token:
            print("⚠️  Skipping auction creation - no auth token")
            return False
            
        listing_data = {
            "title": "Test Product - Auction",
            "description": "This is a test product for auction listing",
            "category": "Fashion",
            "images": ["https://example.com/image2.jpg"],
            "listing_type": "auction",
            "starting_bid": 10.00,
            "buyout_price": 50.00,
            "condition": "Used",
            "quantity": 1,
            "location": "Test City",
            "shipping_cost": 3.99,
            "auction_duration_hours": 24
        }
        
        success, response = self.run_test("Create Auction Listing", "POST", "listings", 200, listing_data)
        return success

    def test_get_listings(self):
        """Test getting all listings"""
        return self.run_test("Get All Listings", "GET", "listings", 200)

    def test_get_listing_by_id(self):
        """Test getting a specific listing"""
        if not self.created_listing_id:
            print("⚠️  Skipping get listing by ID - no created listing")
            return False
            
        return self.run_test("Get Listing by ID", "GET", f"listings/{self.created_listing_id}", 200)

    def test_search_listings(self):
        """Test searching listings"""
        return self.run_test("Search Listings", "GET", "listings?search=test", 200)

    def test_filter_listings_by_category(self):
        """Test filtering listings by category"""
        return self.run_test("Filter by Category", "GET", "listings?category=Electronics", 200)

    def test_filter_listings_by_type(self):
        """Test filtering listings by type"""
        return self.run_test("Filter by Type", "GET", "listings?listing_type=fixed_price", 200)

    def test_add_to_cart(self):
        """Test adding item to cart"""
        if not self.token or not self.created_listing_id:
            print("⚠️  Skipping add to cart - no auth token or listing")
            return False
            
        cart_data = {
            "listing_id": self.created_listing_id,
            "quantity": 1
        }
        
        return self.run_test("Add to Cart", "POST", "cart", 200, cart_data)

    def test_get_cart(self):
        """Test getting cart items"""
        if not self.token:
            print("⚠️  Skipping get cart - no auth token")
            return False
            
        return self.run_test("Get Cart", "GET", "cart", 200)

    def test_create_order(self):
        """Test creating an order"""
        if not self.token or not self.created_listing_id:
            print("⚠️  Skipping create order - no auth token or listing")
            return False
            
        order_data = {
            "listing_id": self.created_listing_id,
            "quantity": 1,
            "shipping_address": "123 Test Street, Test City, TC 12345"
        }
        
        success, response = self.run_test("Create Order", "POST", "orders", 200, order_data)
        if success and 'id' in response:
            self.created_order_id = response['id']
            print(f"   Created order ID: {self.created_order_id}")
        return success

    def test_get_orders(self):
        """Test getting user orders"""
        if not self.token:
            print("⚠️  Skipping get orders - no auth token")
            return False
            
        return self.run_test("Get Orders", "GET", "orders", 200)

    def test_create_review(self):
        """Test creating a review"""
        if not self.token or not self.created_order_id:
            print("⚠️  Skipping create review - no auth token or order")
            return False
            
        review_data = {
            "reviewed_user_id": self.user_id,  # Self-review for testing
            "order_id": self.created_order_id,
            "rating": 5,
            "comment": "Great transaction, highly recommended!"
        }
        
        return self.run_test("Create Review", "POST", "reviews", 200, review_data)

    def test_get_user_reviews(self):
        """Test getting user reviews"""
        if not self.user_id:
            print("⚠️  Skipping get reviews - no user ID")
            return False
            
        return self.run_test("Get User Reviews", "GET", f"users/{self.user_id}/reviews", 200)

    def test_place_bid(self):
        """Test placing a bid (will likely fail as we need an auction listing)"""
        if not self.token:
            print("⚠️  Skipping bid test - no auth token")
            return False
            
        # This will likely fail since we need a proper auction listing
        bid_data = {
            "listing_id": "dummy_auction_id",
            "amount": 15.00
        }
        
        # We expect this to fail with 404, so we'll test for that
        success, response = self.run_test("Place Bid (Expected to Fail)", "POST", "bids", 404, bid_data)
        # For this test, we consider 404 as expected behavior
        return True

    def test_admin_login(self):
        """Test admin login"""
        admin_data = {
            "email": "admin@marketplace.com",
            "password": "admin123"
        }
        
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, admin_data)
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   Admin login successful: {response['user']['full_name']}")
        return success

    def test_create_default_admin(self):
        """Test creating default admin (may fail if already exists)"""
        success, response = self.run_test("Create Default Admin", "POST", "admin/create-default-admin", 200)
        # This might fail with 400 if admin already exists, which is fine
        if not success and "already exists" in str(response):
            print("   Admin already exists - this is expected")
            return True
        return success

    # ===========================
    # CMS ADMIN TESTS
    # ===========================

    def test_get_site_settings(self):
        """Test getting site settings"""
        if not self.admin_token:
            print("⚠️  Skipping site settings test - no admin token")
            return False
        return self.run_test("Get Site Settings", "GET", "admin/cms/settings", 200, use_admin_token=True)

    def test_update_site_settings(self):
        """Test updating site settings"""
        if not self.admin_token:
            print("⚠️  Skipping update site settings - no admin token")
            return False
            
        settings_data = {
            "site_name": "Test Marketplace",
            "site_tagline": "Testing CMS functionality",
            "hero_title": "Welcome to Test Site",
            "hero_subtitle": "This is a test of the CMS system",
            "primary_color": "#3b82f6",
            "secondary_color": "#10b981",
            "show_hero_section": True,
            "show_categories": True,
            "allow_user_registration": True
        }
        
        return self.run_test("Update Site Settings", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)

    def test_get_all_pages(self):
        """Test getting all pages"""
        if not self.admin_token:
            print("⚠️  Skipping get all pages - no admin token")
            return False
        return self.run_test("Get All Pages", "GET", "admin/cms/pages", 200, use_admin_token=True)

    def test_create_page(self):
        """Test creating a new page"""
        if not self.admin_token:
            print("⚠️  Skipping create page - no admin token")
            return False
            
        timestamp = datetime.now().strftime('%H%M%S')
        self.created_page_slug = f"test-page-{timestamp}"
        
        page_data = {
            "page_slug": self.created_page_slug,
            "title": f"Test Page {timestamp}",
            "content": "<h1>Test Page Content</h1><p>This is a test page created by the API test suite.</p>",
            "is_published": True,
            "meta_description": "Test page for CMS functionality",
            "custom_css": "body { background-color: #f0f0f0; }"
        }
        
        success, response = self.run_test("Create Page", "POST", "admin/cms/pages", 200, page_data, use_admin_token=True)
        if success:
            print(f"   Created page slug: {self.created_page_slug}")
        return success

    def test_get_page_content(self):
        """Test getting specific page content"""
        if not self.admin_token or not self.created_page_slug:
            print("⚠️  Skipping get page content - no admin token or page slug")
            return False
        return self.run_test("Get Page Content", "GET", f"admin/cms/pages/{self.created_page_slug}", 200, use_admin_token=True)

    def test_update_page_content(self):
        """Test updating page content"""
        if not self.admin_token or not self.created_page_slug:
            print("⚠️  Skipping update page content - no admin token or page slug")
            return False
            
        updated_data = {
            "title": "Updated Test Page",
            "content": "<h1>Updated Content</h1><p>This page has been updated via API test.</p>",
            "is_published": True,
            "meta_description": "Updated test page description"
        }
        
        return self.run_test("Update Page Content", "PUT", f"admin/cms/pages/{self.created_page_slug}", 200, updated_data, use_admin_token=True)

    def test_get_navigation(self):
        """Test getting navigation items"""
        if not self.admin_token:
            print("⚠️  Skipping get navigation - no admin token")
            return False
        return self.run_test("Get Navigation", "GET", "admin/cms/navigation", 200, use_admin_token=True)

    def test_create_navigation_item(self):
        """Test creating navigation item"""
        if not self.admin_token:
            print("⚠️  Skipping create navigation - no admin token")
            return False
            
        timestamp = datetime.now().strftime('%H%M%S')
        nav_data = {
            "label": f"Test Nav {timestamp}",
            "url": f"/test-nav-{timestamp}",
            "order": 10,
            "is_visible": True,
            "target": "_self"
        }
        
        success, response = self.run_test("Create Navigation Item", "POST", "admin/cms/navigation", 200, nav_data, use_admin_token=True)
        if success and 'item' in response:
            self.created_nav_id = response['item']['id']
            print(f"   Created navigation ID: {self.created_nav_id}")
        return success

    def test_update_navigation_item(self):
        """Test updating navigation item"""
        if not self.admin_token or not self.created_nav_id:
            print("⚠️  Skipping update navigation - no admin token or nav ID")
            return False
            
        updated_nav_data = {
            "label": "Updated Test Nav",
            "url": "/updated-test-nav",
            "order": 5,
            "is_visible": True,
            "target": "_blank"
        }
        
        return self.run_test("Update Navigation Item", "PUT", f"admin/cms/navigation/{self.created_nav_id}", 200, updated_nav_data, use_admin_token=True)

    # ===========================
    # PUBLIC CMS TESTS
    # ===========================

    def test_get_public_site_settings(self):
        """Test getting public site settings"""
        return self.run_test("Get Public Site Settings", "GET", "cms/settings", 200)

    # ===========================
    # BRANDING TESTS - CATALORO
    # ===========================

    def test_branding_default_site_name(self):
        """Test that default site_name is 'Cataloro'"""
        success, response = self.run_test("Check Default Site Name", "GET", "cms/settings", 200)
        if success and 'site_name' in response:
            site_name = response['site_name']
            if site_name == "Cataloro":
                print(f"✅ Branding Test Passed - Site name is correctly set to: {site_name}")
                return True
            else:
                print(f"❌ Branding Test Failed - Expected 'Cataloro', got: {site_name}")
                return False
        else:
            print("❌ Branding Test Failed - Could not retrieve site_name from response")
            return False

    def test_branding_default_hero_subtitle(self):
        """Test that default hero_subtitle contains 'Cataloro' instead of 'Catalogo'"""
        success, response = self.run_test("Check Default Hero Subtitle", "GET", "cms/settings", 200)
        if success and 'hero_subtitle' in response:
            hero_subtitle = response['hero_subtitle']
            if "Cataloro" in hero_subtitle and "Catalogo" not in hero_subtitle:
                print(f"✅ Branding Test Passed - Hero subtitle correctly contains 'Cataloro': {hero_subtitle}")
                return True
            elif "Catalogo" in hero_subtitle:
                print(f"❌ Branding Test Failed - Hero subtitle still contains old 'Catalogo' branding: {hero_subtitle}")
                return False
            else:
                print(f"❌ Branding Test Failed - Hero subtitle doesn't contain 'Cataloro': {hero_subtitle}")
                return False
        else:
            print("❌ Branding Test Failed - Could not retrieve hero_subtitle from response")
            return False

    def test_branding_no_catalogo_references(self):
        """Test that there are no 'Catalogo' references in default settings"""
        success, response = self.run_test("Check No Catalogo References", "GET", "cms/settings", 200)
        if success:
            # Convert response to string and check for any "Catalogo" references
            response_str = json.dumps(response).lower()
            if "catalogo" in response_str:
                print(f"❌ Branding Test Failed - Found 'Catalogo' references in settings: {response}")
                return False
            else:
                print("✅ Branding Test Passed - No 'Catalogo' references found in default settings")
                return True
        else:
            print("❌ Branding Test Failed - Could not retrieve settings")
            return False

    def test_branding_admin_panel_functionality(self):
        """Test that admin panel still works with new branding"""
        if not self.admin_token:
            print("⚠️  Skipping admin branding test - no admin token")
            return False
            
        # Test admin site settings access
        success, response = self.run_test("Admin Panel Branding Test", "GET", "admin/cms/settings", 200, use_admin_token=True)
        if success and 'site_name' in response:
            site_name = response['site_name']
            if site_name == "Cataloro":
                print(f"✅ Admin Branding Test Passed - Admin panel shows correct branding: {site_name}")
                return True
            else:
                print(f"❌ Admin Branding Test Failed - Admin panel shows incorrect branding: {site_name}")
                return False
        else:
            print("❌ Admin Branding Test Failed - Could not access admin settings")
            return False

    def test_branding_core_functionality_unaffected(self):
        """Test that core marketplace functionality is unaffected by branding changes"""
        # Test that we can still get listings (core functionality)
        success1, _ = self.run_test("Core Functionality Test - Listings", "GET", "listings", 200)
        
        # Test that we can still get categories (core functionality)  
        success2, _ = self.run_test("Core Functionality Test - Categories", "GET", "categories", 200)
        
        # Test that root endpoint still works
        success3, _ = self.run_test("Core Functionality Test - Root", "GET", "", 200)
        
        if success1 and success2 and success3:
            print("✅ Core Functionality Test Passed - All core endpoints working after branding change")
            return True
        else:
            print("❌ Core Functionality Test Failed - Some core endpoints not working after branding change")
            return False

    def test_get_public_page_content(self):
        """Test getting public page content"""
        if not self.created_page_slug:
            print("⚠️  Skipping public page content - no created page")
            return False
        return self.run_test("Get Public Page Content", "GET", f"cms/pages/{self.created_page_slug}", 200)

    def test_get_public_navigation(self):
        """Test getting public navigation"""
        return self.run_test("Get Public Navigation", "GET", "cms/navigation", 200)

    # ===========================
    # CLEANUP TESTS
    # ===========================

    def test_delete_page(self):
        """Test deleting a page"""
        if not self.admin_token or not self.created_page_slug:
            print("⚠️  Skipping delete page - no admin token or page slug")
            return False
        return self.run_test("Delete Page", "DELETE", f"admin/cms/pages/{self.created_page_slug}", 200, use_admin_token=True)

    def test_delete_navigation_item(self):
        """Test deleting navigation item"""
        if not self.admin_token or not self.created_nav_id:
            print("⚠️  Skipping delete navigation - no admin token or nav ID")
            return False
        return self.run_test("Delete Navigation Item", "DELETE", f"admin/cms/navigation/{self.created_nav_id}", 200, use_admin_token=True)

def main():
    print("🚀 Starting Marketplace API Tests (Including CMS)")
    print("=" * 60)
    
    tester = MarketplaceAPITester()
    
    # Test sequence - Core marketplace tests first, then CMS tests
    test_methods = [
        # Core API Tests
        tester.test_root_endpoint,
        tester.test_categories,
        tester.test_user_registration,
        tester.test_create_listing_fixed_price,
        tester.test_create_listing_auction,
        tester.test_get_listings,
        tester.test_get_listing_by_id,
        tester.test_search_listings,
        tester.test_filter_listings_by_category,
        tester.test_filter_listings_by_type,
        tester.test_add_to_cart,
        tester.test_get_cart,
        tester.test_create_order,
        tester.test_get_orders,
        tester.test_create_review,
        tester.test_get_user_reviews,
        tester.test_place_bid,
        
        # Admin Setup
        tester.test_create_default_admin,
        tester.test_admin_login,
        
        # CMS Admin Tests
        tester.test_get_site_settings,
        tester.test_update_site_settings,
        tester.test_get_all_pages,
        tester.test_create_page,
        tester.test_get_page_content,
        tester.test_update_page_content,
        tester.test_get_navigation,
        tester.test_create_navigation_item,
        tester.test_update_navigation_item,
        
        # Public CMS Tests
        tester.test_get_public_site_settings,
        tester.test_get_public_page_content,
        tester.test_get_public_navigation,
        
        # Branding Tests - Cataloro
        tester.test_branding_default_site_name,
        tester.test_branding_default_hero_subtitle,
        tester.test_branding_no_catalogo_references,
        tester.test_branding_admin_panel_functionality,
        tester.test_branding_core_functionality_unaffected,
        
        # Cleanup Tests
        tester.test_delete_page,
        tester.test_delete_navigation_item,
    ]
    
    print(f"Running {len(test_methods)} tests...\n")
    
    for test_method in test_methods:
        try:
            test_method()
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())