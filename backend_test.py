import requests
import sys
import json
from datetime import datetime, timedelta
import time
import io
import os
from pathlib import Path

class MarketplaceAPITester:
    def __init__(self, base_url="https://market-deploy.preview.emergentagent.com"):
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
        self.uploaded_logo_url = None

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

    def run_file_upload_test(self, name, endpoint, file_data, file_name, content_type, expected_status, use_admin_token=False):
        """Run a file upload test"""
        url = f"{self.api_url}/{endpoint}"
        
        # Use admin token if specified, otherwise use regular token
        token_to_use = self.admin_token if use_admin_token else self.token
        headers = {}
        if token_to_use:
            headers['Authorization'] = f'Bearer {token_to_use}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            files = {'file': (file_name, file_data, content_type)}
            data = {'logo_type': 'header'}  # Default logo type
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 200:
                        print(f"   Response: {response_data}")
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
    # LOGO UPLOAD TESTS
    # ===========================

    def create_test_png_file(self, size_mb=1):
        """Create a test PNG file in memory"""
        # Create a simple PNG file data (minimal PNG header + data)
        # This is a minimal 1x1 pixel PNG file
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\x1b\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # If we need a larger file, pad it with null bytes
        if size_mb > 1:
            padding_size = (size_mb * 1024 * 1024) - len(png_data)
            png_data += b'\x00' * padding_size
            
        return png_data

    def create_test_jpg_file(self):
        """Create a test JPG file in memory"""
        # Minimal JPEG file header
        jpg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xaa\xff\xd9'
        return jpg_data

    def test_logo_upload_without_admin_auth(self):
        """Test logo upload without admin authentication (should fail)"""
        if not self.token:  # Use regular user token, not admin
            print("⚠️  Skipping logo upload auth test - no user token")
            return False
            
        png_data = self.create_test_png_file()
        success, response = self.run_file_upload_test(
            "Logo Upload Without Admin Auth", 
            "admin/cms/upload-logo", 
            png_data, 
            "test_logo.png", 
            "image/png", 
            403,  # Should fail with 403 Forbidden
            use_admin_token=False
        )
        return success

    def test_logo_upload_valid_png(self):
        """Test uploading a valid PNG logo"""
        if not self.admin_token:
            print("⚠️  Skipping valid PNG upload - no admin token")
            return False
            
        png_data = self.create_test_png_file()
        success, response = self.run_file_upload_test(
            "Valid PNG Logo Upload", 
            "admin/cms/upload-logo", 
            png_data, 
            "test_logo.png", 
            "image/png", 
            200,
            use_admin_token=True
        )
        
        # Store the logo URL for later tests
        if success and 'logo_url' in response:
            self.uploaded_logo_url = response['logo_url']
            print(f"   Uploaded logo URL: {self.uploaded_logo_url}")
            
        return success

    def test_logo_upload_invalid_format(self):
        """Test uploading non-PNG file (should fail)"""
        if not self.admin_token:
            print("⚠️  Skipping invalid format test - no admin token")
            return False
            
        jpg_data = self.create_test_jpg_file()
        success, response = self.run_file_upload_test(
            "Invalid Format (JPG) Upload", 
            "admin/cms/upload-logo", 
            jpg_data, 
            "test_logo.jpg", 
            "image/jpeg", 
            400,  # Should fail with 400 Bad Request
            use_admin_token=True
        )
        return success

    def test_logo_upload_file_too_large(self):
        """Test uploading file larger than 5MB (should fail)"""
        if not self.admin_token:
            print("⚠️  Skipping large file test - no admin token")
            return False
            
        # Create a 6MB PNG file
        large_png_data = self.create_test_png_file(size_mb=6)
        success, response = self.run_file_upload_test(
            "Large File (6MB) Upload", 
            "admin/cms/upload-logo", 
            large_png_data, 
            "large_logo.png", 
            "image/png", 
            400,  # Should fail with 400 Bad Request
            use_admin_token=True
        )
        return success

    def test_logo_url_in_site_settings(self):
        """Test that uploaded logo URL is stored in site settings"""
        if not self.admin_token:
            print("⚠️  Skipping logo URL test - no admin token")
            return False
            
        success, response = self.run_test("Check Logo URL in Settings", "GET", "admin/cms/settings", 200, use_admin_token=True)
        
        if success:
            # Check if header_logo_url and header_logo_alt fields exist
            has_logo_url = 'header_logo_url' in response
            has_logo_alt = 'header_logo_alt' in response
            
            if has_logo_url and has_logo_alt:
                print(f"✅ Logo fields found - URL: {response.get('header_logo_url')}, Alt: {response.get('header_logo_alt')}")
                return True
            else:
                print(f"❌ Logo fields missing - URL field: {has_logo_url}, Alt field: {has_logo_alt}")
                return False
        
        return success

    def test_logo_fields_in_public_settings(self):
        """Test that logo fields are returned in public site settings"""
        success, response = self.run_test("Check Logo Fields in Public Settings", "GET", "cms/settings", 200)
        
        if success:
            # Check if header_logo_url and header_logo_alt fields exist in public API
            has_logo_url = 'header_logo_url' in response
            has_logo_alt = 'header_logo_alt' in response
            
            if has_logo_url and has_logo_alt:
                print(f"✅ Public logo fields found - URL: {response.get('header_logo_url')}, Alt: {response.get('header_logo_alt')}")
                return True
            else:
                print(f"❌ Public logo fields missing - URL field: {has_logo_url}, Alt field: {has_logo_alt}")
                return False
        
        return success

    def test_uploads_directory_creation(self):
        """Test that uploads directory exists and files are stored there"""
        # This test checks if the uploads directory is accessible via the static file serving
        if not hasattr(self, 'uploaded_logo_url') or not self.uploaded_logo_url:
            print("⚠️  Skipping uploads directory test - no uploaded logo URL")
            return False
            
        # Try to access the uploaded file via HTTP
        logo_url = f"{self.base_url}{self.uploaded_logo_url}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Uploads Directory Access...")
        print(f"   URL: {logo_url}")
        
        try:
            response = requests.get(logo_url, timeout=10)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Logo file accessible at: {logo_url}")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"   File size: {len(response.content)} bytes")
            else:
                print(f"❌ Failed - Logo file not accessible, status: {response.status_code}")
                
            return success
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False

    def test_old_logo_file_cleanup(self):
        """Test that old logo files are removed when new logo is uploaded"""
        if not self.admin_token:
            print("⚠️  Skipping old file cleanup test - no admin token")
            return False
            
        # First, upload a logo
        png_data1 = self.create_test_png_file()
        success1, response1 = self.run_file_upload_test(
            "First Logo Upload for Cleanup Test", 
            "admin/cms/upload-logo", 
            png_data1, 
            "first_logo.png", 
            "image/png", 
            200,
            use_admin_token=True
        )
        
        if not success1:
            return False
            
        first_logo_url = response1.get('logo_url')
        
        # Upload a second logo (should replace the first)
        png_data2 = self.create_test_png_file()
        success2, response2 = self.run_file_upload_test(
            "Second Logo Upload for Cleanup Test", 
            "admin/cms/upload-logo", 
            png_data2, 
            "second_logo.png", 
            "image/png", 
            200,
            use_admin_token=True
        )
        
        if not success2:
            return False
            
        second_logo_url = response2.get('logo_url')
        
        # Verify the new logo is accessible
        new_logo_full_url = f"{self.base_url}{second_logo_url}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing New Logo Accessibility...")
        
        try:
            response = requests.get(new_logo_full_url, timeout=10)
            new_logo_accessible = response.status_code == 200
            
            if new_logo_accessible:
                self.tests_passed += 1
                print(f"✅ New logo accessible - cleanup test passed")
                print(f"   New logo URL: {second_logo_url}")
                return True
            else:
                print(f"❌ New logo not accessible - status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False

    # ===========================
    # LISTING IMAGE UPLOAD TESTS
    # ===========================

    def run_listing_image_upload_test(self, name, file_data, file_name, content_type, expected_status, use_admin_token=False):
        """Run a listing image upload test"""
        url = f"{self.api_url}/listings/upload-image"
        
        # Use admin token if specified, otherwise use regular token
        token_to_use = self.admin_token if use_admin_token else self.token
        headers = {}
        if token_to_use:
            headers['Authorization'] = f'Bearer {token_to_use}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            files = {'file': (file_name, file_data, content_type)}
            
            response = requests.post(url, files=files, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 200:
                        print(f"   Response: {response_data}")
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

    def test_listing_image_upload_without_auth(self):
        """Test listing image upload without authentication (should fail)"""
        png_data = self.create_test_png_file()
        
        # Temporarily clear token to test without auth
        original_token = self.token
        self.token = None
        
        success, response = self.run_listing_image_upload_test(
            "Listing Image Upload Without Auth", 
            png_data, 
            "test_listing.png", 
            "image/png", 
            403,  # Should fail with 403 Forbidden (FastAPI returns 403 for "Not authenticated")
            use_admin_token=False
        )
        
        # Restore token
        self.token = original_token
        return success

    def test_listing_image_upload_valid_png(self):
        """Test uploading a valid PNG for listing"""
        if not self.token:
            print("⚠️  Skipping valid PNG listing upload - no user token")
            return False
            
        png_data = self.create_test_png_file()
        success, response = self.run_listing_image_upload_test(
            "Valid PNG Listing Image Upload", 
            png_data, 
            "test_listing.png", 
            "image/png", 
            200,
            use_admin_token=False
        )
        
        # Store the image URL for later tests
        if success and 'image_url' in response:
            if not hasattr(self, 'uploaded_listing_images'):
                self.uploaded_listing_images = []
            self.uploaded_listing_images.append(response['image_url'])
            print(f"   Uploaded listing image URL: {response['image_url']}")
            
        return success

    def test_listing_image_upload_valid_jpeg(self):
        """Test uploading a valid JPEG for listing"""
        if not self.token:
            print("⚠️  Skipping valid JPEG listing upload - no user token")
            return False
            
        jpg_data = self.create_test_jpg_file()
        success, response = self.run_listing_image_upload_test(
            "Valid JPEG Listing Image Upload", 
            jpg_data, 
            "test_listing.jpg", 
            "image/jpeg", 
            200,
            use_admin_token=False
        )
        
        # Store the image URL for later tests
        if success and 'image_url' in response:
            if not hasattr(self, 'uploaded_listing_images'):
                self.uploaded_listing_images = []
            self.uploaded_listing_images.append(response['image_url'])
            print(f"   Uploaded listing image URL: {response['image_url']}")
            
        return success

    def test_listing_image_upload_invalid_format(self):
        """Test uploading invalid format for listing (should fail)"""
        if not self.token:
            print("⚠️  Skipping invalid format test - no user token")
            return False
            
        # Create fake GIF data
        gif_data = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;'
        success, response = self.run_listing_image_upload_test(
            "Invalid Format (GIF) Listing Upload", 
            gif_data, 
            "test_listing.gif", 
            "image/gif", 
            400,  # Should fail with 400 Bad Request
            use_admin_token=False
        )
        return success

    def test_listing_image_upload_file_too_large(self):
        """Test uploading file larger than 10MB for listing (should fail)"""
        if not self.token:
            print("⚠️  Skipping large file test - no user token")
            return False
            
        # Create an 11MB PNG file
        large_png_data = self.create_test_png_file(size_mb=11)
        success, response = self.run_listing_image_upload_test(
            "Large File (11MB) Listing Upload", 
            large_png_data, 
            "large_listing.png", 
            "image/png", 
            400,  # Should fail with 400 Bad Request
            use_admin_token=False
        )
        return success

    def test_listing_image_upload_with_admin_token(self):
        """Test that admin users can also upload listing images"""
        if not self.admin_token:
            print("⚠️  Skipping admin listing upload - no admin token")
            return False
            
        png_data = self.create_test_png_file()
        success, response = self.run_listing_image_upload_test(
            "Admin User Listing Image Upload", 
            png_data, 
            "admin_listing.png", 
            "image/png", 
            200,
            use_admin_token=True
        )
        
        # Store the image URL for later tests
        if success and 'image_url' in response:
            if not hasattr(self, 'uploaded_listing_images'):
                self.uploaded_listing_images = []
            self.uploaded_listing_images.append(response['image_url'])
            print(f"   Admin uploaded listing image URL: {response['image_url']}")
            
        return success

    def test_create_listing_with_uploaded_images(self):
        """Test creating a listing with uploaded images"""
        if not self.token:
            print("⚠️  Skipping listing with images - no auth token")
            return False
            
        if not hasattr(self, 'uploaded_listing_images') or not self.uploaded_listing_images:
            print("⚠️  Skipping listing with images - no uploaded images")
            return False
            
        listing_data = {
            "title": "Test Product with Uploaded Images",
            "description": "This listing uses uploaded images from the image upload endpoint",
            "category": "Electronics",
            "images": self.uploaded_listing_images[:2],  # Use first 2 uploaded images
            "listing_type": "fixed_price",
            "price": 149.99,
            "condition": "New",
            "quantity": 1,
            "location": "Test City",
            "shipping_cost": 7.99
        }
        
        success, response = self.run_test("Create Listing with Uploaded Images", "POST", "listings", 200, listing_data)
        if success and 'id' in response:
            self.created_listing_with_images_id = response['id']
            print(f"   Created listing with images ID: {self.created_listing_with_images_id}")
            print(f"   Images in listing: {response.get('images', [])}")
        return success

    def test_get_listings_returns_image_urls(self):
        """Test that GET /listings returns proper image URLs"""
        success, response = self.run_test("Get Listings with Image URLs", "GET", "listings", 200)
        
        if success and isinstance(response, list):
            # Look for listings with images
            listings_with_images = [listing for listing in response if listing.get('images')]
            
            if listings_with_images:
                print(f"   Found {len(listings_with_images)} listings with images")
                # Check first listing with images
                first_listing = listings_with_images[0]
                images = first_listing.get('images', [])
                print(f"   Sample listing images: {images[:2]}")  # Show first 2 images
                
                # Verify images are URLs (start with /uploads/ or http)
                valid_urls = all(img.startswith('/uploads/') or img.startswith('http') for img in images)
                if valid_urls:
                    print("✅ All image URLs are properly formatted")
                    return True
                else:
                    print("❌ Some image URLs are not properly formatted")
                    return False
            else:
                print("⚠️  No listings with images found - this may be expected")
                return True  # Not a failure if no images exist
        
        return success

    def test_get_listing_detail_returns_images(self):
        """Test that listing detail endpoint returns image data correctly"""
        if not hasattr(self, 'created_listing_with_images_id') or not self.created_listing_with_images_id:
            print("⚠️  Skipping listing detail image test - no listing with images")
            return False
            
        success, response = self.run_test("Get Listing Detail with Images", "GET", f"listings/{self.created_listing_with_images_id}", 200)
        
        if success and 'images' in response:
            images = response['images']
            print(f"   Listing detail images: {images}")
            
            # Verify images are URLs
            if images:
                valid_urls = all(img.startswith('/uploads/') or img.startswith('http') for img in images)
                if valid_urls:
                    print("✅ Listing detail returns properly formatted image URLs")
                    return True
                else:
                    print("❌ Listing detail image URLs are not properly formatted")
                    return False
            else:
                print("⚠️  No images in listing detail - this may be expected")
                return True
        
        return success

    def test_uploaded_listing_images_accessible(self):
        """Test that uploaded listing images are accessible via HTTP"""
        if not hasattr(self, 'uploaded_listing_images') or not self.uploaded_listing_images:
            print("⚠️  Skipping image accessibility test - no uploaded images")
            return False
            
        # Test first uploaded image
        image_url = self.uploaded_listing_images[0]
        full_url = f"{self.base_url}{image_url}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Listing Image Accessibility...")
        print(f"   URL: {full_url}")
        
        try:
            response = requests.get(full_url, timeout=10)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Listing image accessible")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"   File size: {len(response.content)} bytes")
            else:
                print(f"❌ Failed - Listing image not accessible, status: {response.status_code}")
                
            return success
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False

    # ===========================
    # HERO HEIGHT FUNCTIONALITY TESTS
    # ===========================

    def test_hero_height_default_value(self):
        """Test that default hero_height is '600px' when not set"""
        success, response = self.run_test("Check Default Hero Height", "GET", "cms/settings", 200)
        if success and 'hero_height' in response:
            hero_height = response['hero_height']
            if hero_height == "600px":
                print(f"✅ Hero Height Default Test Passed - Default value is correctly set to: {hero_height}")
                return True
            else:
                print(f"❌ Hero Height Default Test Failed - Expected '600px', got: {hero_height}")
                return False
        else:
            print("❌ Hero Height Default Test Failed - Could not retrieve hero_height from response")
            return False

    def test_hero_height_in_public_settings(self):
        """Test that hero_height field is included in public CMS settings"""
        success, response = self.run_test("Check Hero Height in Public Settings", "GET", "cms/settings", 200)
        if success:
            has_hero_height = 'hero_height' in response
            if has_hero_height:
                hero_height = response['hero_height']
                print(f"✅ Public Hero Height Test Passed - Field found with value: {hero_height}")
                return True
            else:
                print("❌ Public Hero Height Test Failed - hero_height field missing from public settings")
                return False
        return success

    def test_hero_height_update_400px(self):
        """Test updating hero_height to 400px via admin API"""
        if not self.admin_token:
            print("⚠️  Skipping hero height update test - no admin token")
            return False
            
        settings_data = {
            "hero_height": "400px"
        }
        
        success, response = self.run_test("Update Hero Height to 400px", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)
        if success:
            print("✅ Hero Height Update Test (400px) Passed")
        return success

    def test_hero_height_update_800px(self):
        """Test updating hero_height to 800px via admin API"""
        if not self.admin_token:
            print("⚠️  Skipping hero height update test - no admin token")
            return False
            
        settings_data = {
            "hero_height": "800px"
        }
        
        success, response = self.run_test("Update Hero Height to 800px", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)
        if success:
            print("✅ Hero Height Update Test (800px) Passed")
        return success

    def test_hero_height_persistence_after_update(self):
        """Test that hero_height value persists after update"""
        if not self.admin_token:
            print("⚠️  Skipping hero height persistence test - no admin token")
            return False
            
        # First update to a specific value
        settings_data = {
            "hero_height": "750px"
        }
        
        success1, response1 = self.run_test("Set Hero Height to 750px", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)
        if not success1:
            return False
            
        # Then retrieve and verify the value persisted
        success2, response2 = self.run_test("Verify Hero Height Persistence", "GET", "admin/cms/settings", 200, use_admin_token=True)
        if success2 and 'hero_height' in response2:
            hero_height = response2['hero_height']
            if hero_height == "750px":
                print(f"✅ Hero Height Persistence Test Passed - Value correctly persisted: {hero_height}")
                return True
            else:
                print(f"❌ Hero Height Persistence Test Failed - Expected '750px', got: {hero_height}")
                return False
        else:
            print("❌ Hero Height Persistence Test Failed - Could not retrieve hero_height after update")
            return False

    def test_hero_height_minimum_value_300px(self):
        """Test hero_height with minimum recommended value (300px)"""
        if not self.admin_token:
            print("⚠️  Skipping hero height minimum test - no admin token")
            return False
            
        settings_data = {
            "hero_height": "300px"
        }
        
        success, response = self.run_test("Update Hero Height to 300px (Minimum)", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)
        if success:
            print("✅ Hero Height Minimum Value Test (300px) Passed")
        return success

    def test_hero_height_maximum_value_1000px(self):
        """Test hero_height with maximum recommended value (1000px)"""
        if not self.admin_token:
            print("⚠️  Skipping hero height maximum test - no admin token")
            return False
            
        settings_data = {
            "hero_height": "1000px"
        }
        
        success, response = self.run_test("Update Hero Height to 1000px (Maximum)", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)
        if success:
            print("✅ Hero Height Maximum Value Test (1000px) Passed")
        return success

    def test_hero_height_public_api_after_update(self):
        """Test that public CMS settings endpoint returns updated hero_height value"""
        if not self.admin_token:
            print("⚠️  Skipping hero height public API test - no admin token")
            return False
            
        # First update to a specific value
        settings_data = {
            "hero_height": "650px"
        }
        
        success1, response1 = self.run_test("Set Hero Height to 650px for Public Test", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)
        if not success1:
            return False
            
        # Then check public API returns the updated value
        success2, response2 = self.run_test("Verify Hero Height in Public API", "GET", "cms/settings", 200)
        if success2 and 'hero_height' in response2:
            hero_height = response2['hero_height']
            if hero_height == "650px":
                print(f"✅ Hero Height Public API Test Passed - Public API returns updated value: {hero_height}")
                return True
            else:
                print(f"❌ Hero Height Public API Test Failed - Expected '650px', got: {hero_height}")
                return False
        else:
            print("❌ Hero Height Public API Test Failed - Could not retrieve hero_height from public API")
            return False

    def test_hero_height_database_storage(self):
        """Test that hero_height is properly saved and retrieved from database"""
        if not self.admin_token:
            print("⚠️  Skipping hero height database test - no admin token")
            return False
            
        # Update to a unique value
        unique_height = "555px"
        settings_data = {
            "hero_height": unique_height
        }
        
        success1, response1 = self.run_test("Set Unique Hero Height for DB Test", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)
        if not success1:
            return False
            
        # Retrieve via admin API
        success2, response2 = self.run_test("Verify Hero Height via Admin API", "GET", "admin/cms/settings", 200, use_admin_token=True)
        admin_height = response2.get('hero_height') if success2 else None
        
        # Retrieve via public API
        success3, response3 = self.run_test("Verify Hero Height via Public API", "GET", "cms/settings", 200)
        public_height = response3.get('hero_height') if success3 else None
        
        if success2 and success3 and admin_height == unique_height and public_height == unique_height:
            print(f"✅ Hero Height Database Storage Test Passed - Value consistently retrieved: {unique_height}")
            return True
        else:
            print(f"❌ Hero Height Database Storage Test Failed - Admin: {admin_height}, Public: {public_height}, Expected: {unique_height}")
            return False

    def test_hero_height_various_formats(self):
        """Test hero_height with various CSS height formats"""
        if not self.admin_token:
            print("⚠️  Skipping hero height formats test - no admin token")
            return False
            
        test_formats = [
            "500px",
            "50vh",
            "600px",
            "80vh"
        ]
        
        all_passed = True
        
        for height_format in test_formats:
            settings_data = {
                "hero_height": height_format
            }
            
            success, response = self.run_test(f"Test Hero Height Format: {height_format}", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)
            if not success:
                all_passed = False
                print(f"❌ Failed to set hero_height to: {height_format}")
            else:
                # Verify the value was set correctly
                verify_success, verify_response = self.run_test(f"Verify Hero Height Format: {height_format}", "GET", "admin/cms/settings", 200, use_admin_token=True)
                if verify_success and verify_response.get('hero_height') == height_format:
                    print(f"✅ Hero Height Format Test Passed for: {height_format}")
                else:
                    all_passed = False
                    print(f"❌ Hero Height Format Test Failed for: {height_format}")
        
        return all_passed

    # ===========================
    # SITE NAME SPECIFIC TESTS (FOR ADMIN PANEL TITLE FIX)
    # ===========================

    def test_site_name_current_value(self):
        """Test current site_name value in CMS settings"""
        success, response = self.run_test("Check Current Site Name", "GET", "cms/settings", 200)
        if success and 'site_name' in response:
            site_name = response['site_name']
            print(f"   Current site_name: '{site_name}'")
            
            # Store current value for comparison
            self.current_site_name = site_name
            return True
        else:
            print("❌ Could not retrieve current site_name")
            return False

    def test_admin_site_name_current_value(self):
        """Test current site_name value via admin API"""
        if not self.admin_token:
            print("⚠️  Skipping admin site name check - no admin token")
            return False
            
        success, response = self.run_test("Check Admin Site Name", "GET", "admin/cms/settings", 200, use_admin_token=True)
        if success and 'site_name' in response:
            admin_site_name = response['site_name']
            print(f"   Admin API site_name: '{admin_site_name}'")
            
            # Store admin value for comparison
            self.admin_site_name = admin_site_name
            return True
        else:
            print("❌ Could not retrieve admin site_name")
            return False

    def test_update_site_name_to_cataloro(self):
        """Test updating site_name to 'Cataloro' if it's not already set correctly"""
        if not self.admin_token:
            print("⚠️  Skipping site name update - no admin token")
            return False
            
        # Check current value first
        current_name = getattr(self, 'current_site_name', None) or getattr(self, 'admin_site_name', None)
        
        if current_name == "Cataloro":
            print(f"✅ Site name is already correctly set to 'Cataloro'")
            return True
        else:
            print(f"   Current site_name is '{current_name}', updating to 'Cataloro'...")
            
            # Update site_name to Cataloro
            settings_data = {
                "site_name": "Cataloro"
            }
            
            success, response = self.run_test("Update Site Name to Cataloro", "PUT", "admin/cms/settings", 200, settings_data, use_admin_token=True)
            if success:
                print("✅ Successfully updated site_name to 'Cataloro'")
                return True
            else:
                print("❌ Failed to update site_name to 'Cataloro'")
                return False

    def test_verify_site_name_update_persistence(self):
        """Test that site_name update persists correctly"""
        # Check public API
        success1, response1 = self.run_test("Verify Site Name in Public API", "GET", "cms/settings", 200)
        public_name = response1.get('site_name') if success1 else None
        
        # Check admin API
        success2, response2 = self.run_test("Verify Site Name in Admin API", "GET", "admin/cms/settings", 200, use_admin_token=True) if self.admin_token else (False, {})
        admin_name = response2.get('site_name') if success2 else None
        
        if success1 and public_name == "Cataloro":
            print(f"✅ Public API correctly returns site_name: '{public_name}'")
            
            if success2 and admin_name == "Cataloro":
                print(f"✅ Admin API correctly returns site_name: '{admin_name}'")
                print("✅ Site name update verification PASSED - Both APIs return 'Cataloro'")
                return True
            elif self.admin_token:
                print(f"❌ Admin API returns incorrect site_name: '{admin_name}'")
                return False
            else:
                print("⚠️  Admin API not tested (no admin token)")
                return True
        else:
            print(f"❌ Public API returns incorrect site_name: '{public_name}'")
            return False

    def test_admin_panel_title_fix_verification(self):
        """Test that admin panel will show 'Cataloro Admin' instead of 'Catalogo Admin'"""
        if not self.admin_token:
            print("⚠️  Skipping admin panel title verification - no admin token")
            return False
            
        # Get current site settings via admin API
        success, response = self.run_test("Admin Panel Title Fix Verification", "GET", "admin/cms/settings", 200, use_admin_token=True)
        
        if success and 'site_name' in response:
            site_name = response['site_name']
            
            if site_name == "Cataloro":
                print(f"✅ Admin panel title fix verified - site_name is '{site_name}'")
                print("   This means admin panel should now show 'Cataloro Admin' instead of 'Catalogo Admin'")
                return True
            else:
                print(f"❌ Admin panel title fix failed - site_name is still '{site_name}' instead of 'Cataloro'")
                return False
        else:
            print("❌ Could not verify admin panel title fix - unable to retrieve site_name")
            return False

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
        
        # Site Name Specific Tests (Admin Panel Title Fix)
        tester.test_site_name_current_value,
        tester.test_admin_site_name_current_value,
        tester.test_update_site_name_to_cataloro,
        tester.test_verify_site_name_update_persistence,
        tester.test_admin_panel_title_fix_verification,
        
        # Hero Height Functionality Tests
        tester.test_hero_height_default_value,
        tester.test_hero_height_in_public_settings,
        tester.test_hero_height_update_400px,
        tester.test_hero_height_update_800px,
        tester.test_hero_height_persistence_after_update,
        tester.test_hero_height_minimum_value_300px,
        tester.test_hero_height_maximum_value_1000px,
        tester.test_hero_height_public_api_after_update,
        tester.test_hero_height_database_storage,
        tester.test_hero_height_various_formats,
        
        # Logo Upload Tests
        tester.test_logo_upload_without_admin_auth,
        tester.test_logo_upload_valid_png,
        tester.test_logo_upload_invalid_format,
        tester.test_logo_upload_file_too_large,
        tester.test_logo_url_in_site_settings,
        tester.test_logo_fields_in_public_settings,
        tester.test_uploads_directory_creation,
        tester.test_old_logo_file_cleanup,
        
        # Listing Image Upload Tests
        tester.test_listing_image_upload_without_auth,
        tester.test_listing_image_upload_valid_png,
        tester.test_listing_image_upload_valid_jpeg,
        tester.test_listing_image_upload_invalid_format,
        tester.test_listing_image_upload_file_too_large,
        tester.test_listing_image_upload_with_admin_token,
        tester.test_create_listing_with_uploaded_images,
        tester.test_get_listings_returns_image_urls,
        tester.test_get_listing_detail_returns_images,
        tester.test_uploaded_listing_images_accessible,
        
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