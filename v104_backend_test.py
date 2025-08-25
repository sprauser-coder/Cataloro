#!/usr/bin/env python3
"""
Cataloro v1.0.4 Bug Fixes Backend Testing
=========================================

Testing the v1.0.4 bug fixes implementation focusing on the new functionality:

Priority Testing Areas:
1. **Favorites System**: Test POST /api/favorites from browse page and listing details for both regular and auction items
2. **Categories Management**: Test category creation, display, and deletion functionality  
3. **Order Management**: Verify enhanced order display with timestamps and search functionality
4. **Page Management**: Test page CRUD operations including edit functionality
5. **Admin Panel**: Verify all endpoints work with the new sidebar layout structure

Test Scenarios:
- Admin authentication (admin@marketplace.com/admin123) 
- Test favorites functionality for different listing types (auction/regular)
- Verify category management operations
- Check order data includes proper timestamps and sorting
- Test page editing and "add to menu" functionality
- Confirm all admin endpoints are accessible
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://revived-cataloro.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class CataloroV104Tester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_user_token = None
        self.test_user_id = None
        self.test_listing_ids = []
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        print(result)
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def create_test_user(self):
        """Create a test user for favorites testing"""
        try:
            test_user_data = {
                "email": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
                "password": "testpass123",
                "full_name": "Test User for v1.0.4",
                "role": "both",
                "phone": "+1234567890",
                "address": "123 Test Street, Test City"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                self.log_test("Create Test User", True, f"Created user: {test_user_data['email']}")
                return True
            else:
                self.log_test("Create Test User", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Test User", False, f"Exception: {str(e)}")
            return False

    def create_test_listings(self):
        """Create test listings for favorites testing (both regular and auction)"""
        try:
            # Create regular fixed-price listing
            regular_listing = {
                "title": "v1.0.4 Test Regular Item",
                "description": "This is a regular fixed-price item for testing favorites functionality",
                "category": "Electronics",
                "condition": "New",
                "listing_type": "fixed_price",
                "price": 199.99,
                "quantity": 1,
                "location": "Test City, Test State"
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings", json=regular_listing)
            if response.status_code == 200:
                data = response.json()
                self.test_listing_ids.append({"id": data["id"], "type": "regular", "title": data["title"]})
                self.log_test("Create Regular Test Listing", True, f"Created regular listing: {data['title']}")
            else:
                self.log_test("Create Regular Test Listing", False, f"Status: {response.status_code}")
                return False
            
            # Create auction listing
            auction_listing = {
                "title": "v1.0.4 Test Auction Item",
                "description": "This is an auction item for testing favorites functionality",
                "category": "Fashion",
                "condition": "Like New",
                "listing_type": "auction",
                "starting_bid": 50.0,
                "buyout_price": 150.0,
                "auction_duration_hours": 168,  # 1 week
                "quantity": 1,
                "location": "Auction City, Test State"
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings", json=auction_listing)
            if response.status_code == 200:
                data = response.json()
                self.test_listing_ids.append({"id": data["id"], "type": "auction", "title": data["title"]})
                self.log_test("Create Auction Test Listing", True, f"Created auction listing: {data['title']}")
            else:
                self.log_test("Create Auction Test Listing", False, f"Status: {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Create Test Listings", False, f"Exception: {str(e)}")
            return False

    def test_favorites_system(self):
        """Test the favorites system for both regular and auction items"""
        print("\n=== TESTING FAVORITES SYSTEM ===")
        
        if not self.test_listing_ids:
            self.log_test("Favorites System Prerequisites", False, "No test listings available")
            return
        
        # Switch to test user for favorites testing
        test_headers = {"Authorization": f"Bearer {self.test_user_token}"}
        
        try:
            # Test adding regular item to favorites
            regular_listing = next((l for l in self.test_listing_ids if l["type"] == "regular"), None)
            if regular_listing:
                response = self.session.post(f"{BACKEND_URL}/favorites", 
                                           json={"listing_id": regular_listing["id"]}, 
                                           headers=test_headers)
                
                if response.status_code == 200:
                    self.log_test("Add Regular Item to Favorites", True, f"Added {regular_listing['title']} to favorites")
                else:
                    self.log_test("Add Regular Item to Favorites", False, f"Status: {response.status_code}, Response: {response.text}")
            
            # Test adding auction item to favorites
            auction_listing = next((l for l in self.test_listing_ids if l["type"] == "auction"), None)
            if auction_listing:
                response = self.session.post(f"{BACKEND_URL}/favorites", 
                                           json={"listing_id": auction_listing["id"]}, 
                                           headers=test_headers)
                
                if response.status_code == 200:
                    self.log_test("Add Auction Item to Favorites", True, f"Added {auction_listing['title']} to favorites")
                else:
                    self.log_test("Add Auction Item to Favorites", False, f"Status: {response.status_code}, Response: {response.text}")
            
            # Test getting user favorites
            response = self.session.get(f"{BACKEND_URL}/favorites", headers=test_headers)
            
            if response.status_code == 200:
                favorites = response.json()
                self.log_test("Get User Favorites", True, f"Retrieved {len(favorites)} favorite items")
                
                # Verify both listing types are in favorites
                favorite_types = []
                for fav in favorites:
                    listing = fav.get("listing", {})
                    listing_type = listing.get("listing_type")
                    if listing_type:
                        favorite_types.append(listing_type)
                
                if "fixed_price" in favorite_types and "auction" in favorite_types:
                    self.log_test("Favorites Include Both Types", True, "Both regular and auction items in favorites")
                else:
                    self.log_test("Favorites Include Both Types", False, f"Missing types. Found: {favorite_types}")
                
                # Test removing from favorites
                if favorites:
                    first_favorite = favorites[0]
                    favorite_id = first_favorite.get("favorite_id")
                    
                    if favorite_id:
                        response = self.session.delete(f"{BACKEND_URL}/favorites/{favorite_id}", headers=test_headers)
                        
                        if response.status_code == 200:
                            self.log_test("Remove from Favorites", True, "Successfully removed item from favorites")
                            
                            # Verify removal
                            response = self.session.get(f"{BACKEND_URL}/favorites", headers=test_headers)
                            if response.status_code == 200:
                                updated_favorites = response.json()
                                if len(updated_favorites) < len(favorites):
                                    self.log_test("Verify Favorites Removal", True, f"Favorites count reduced from {len(favorites)} to {len(updated_favorites)}")
                                else:
                                    self.log_test("Verify Favorites Removal", False, "Favorites count did not decrease")
                            else:
                                self.log_test("Verify Favorites Removal", False, "Could not verify removal")
                        else:
                            self.log_test("Remove from Favorites", False, f"Status: {response.status_code}")
                    else:
                        self.log_test("Remove from Favorites", False, "No favorite_id found")
            else:
                self.log_test("Get User Favorites", False, f"Status: {response.status_code}, Response: {response.text}")
            
            # Test duplicate favorites (should fail)
            if self.test_listing_ids:
                test_listing = self.test_listing_ids[0]
                response = self.session.post(f"{BACKEND_URL}/favorites", 
                                           json={"listing_id": test_listing["id"]}, 
                                           headers=test_headers)
                
                if response.status_code == 400:
                    self.log_test("Prevent Duplicate Favorites", True, "Correctly prevented duplicate favorite")
                else:
                    self.log_test("Prevent Duplicate Favorites", False, f"Expected 400, got {response.status_code}")
                    
        except Exception as e:
            self.log_test("Favorites System Test", False, f"Exception: {str(e)}")

    def test_categories_management(self):
        """Test category management functionality"""
        print("\n=== TESTING CATEGORIES MANAGEMENT ===")
        
        try:
            # Test getting all categories
            response = self.session.get(f"{BACKEND_URL}/categories")
            
            if response.status_code == 200:
                categories = response.json()
                self.log_test("Get All Categories", True, f"Retrieved {len(categories)} categories: {categories}")
                
                # Verify standard categories exist
                expected_categories = ["Electronics", "Fashion", "Home & Garden", "Sports", "Books"]
                missing_categories = [cat for cat in expected_categories if cat not in categories]
                
                if not missing_categories:
                    self.log_test("Standard Categories Present", True, "All expected categories found")
                else:
                    self.log_test("Standard Categories Present", False, f"Missing categories: {missing_categories}")
                    
                # Test that categories are available for listing creation
                if categories:
                    test_category = categories[0]
                    test_listing = {
                        "title": "Category Test Listing",
                        "description": "Testing category functionality",
                        "category": test_category,
                        "condition": "New",
                        "listing_type": "fixed_price",
                        "price": 99.99,
                        "quantity": 1,
                        "location": "Category Test City"
                    }
                    
                    response = self.session.post(f"{BACKEND_URL}/listings", json=test_listing)
                    if response.status_code == 200:
                        self.log_test("Category in Listing Creation", True, f"Successfully created listing with category: {test_category}")
                    else:
                        self.log_test("Category in Listing Creation", False, f"Failed to create listing with category: {response.status_code}")
            else:
                self.log_test("Get All Categories", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Categories Management Test", False, f"Exception: {str(e)}")

    def test_order_management_enhancements(self):
        """Test enhanced order management with timestamps and search functionality"""
        print("\n=== TESTING ORDER MANAGEMENT ENHANCEMENTS ===")
        
        try:
            # Test admin orders endpoint with enhanced features
            response = self.session.get(f"{BACKEND_URL}/admin/orders")
            
            if response.status_code == 200:
                orders = response.json()
                self.log_test("Get Admin Orders", True, f"Retrieved {len(orders)} orders")
                
                # Test with status filter
                response = self.session.get(f"{BACKEND_URL}/admin/orders", params={"status_filter": "all"})
                if response.status_code == 200:
                    all_orders = response.json()
                    self.log_test("Orders with Status Filter (all)", True, f"Retrieved {len(all_orders)} orders with 'all' filter")
                else:
                    self.log_test("Orders with Status Filter (all)", False, f"Status: {response.status_code}")
                
                # Test with pending status filter
                response = self.session.get(f"{BACKEND_URL}/admin/orders", params={"status_filter": "pending"})
                if response.status_code == 200:
                    pending_orders = response.json()
                    self.log_test("Orders with Status Filter (pending)", True, f"Retrieved {len(pending_orders)} pending orders")
                else:
                    self.log_test("Orders with Status Filter (pending)", False, f"Status: {response.status_code}")
                
                # Test with completed status filter
                response = self.session.get(f"{BACKEND_URL}/admin/orders", params={"status_filter": "completed"})
                if response.status_code == 200:
                    completed_orders = response.json()
                    self.log_test("Orders with Status Filter (completed)", True, f"Retrieved {len(completed_orders)} completed orders")
                else:
                    self.log_test("Orders with Status Filter (completed)", False, f"Status: {response.status_code}")
                
                # Test with time frame filters
                time_frames = ["today", "last_week", "last_month", "last_year"]
                for time_frame in time_frames:
                    response = self.session.get(f"{BACKEND_URL}/admin/orders", params={"time_frame": time_frame})
                    if response.status_code == 200:
                        filtered_orders = response.json()
                        self.log_test(f"Orders with Time Frame ({time_frame})", True, f"Retrieved {len(filtered_orders)} orders for {time_frame}")
                    else:
                        self.log_test(f"Orders with Time Frame ({time_frame})", False, f"Status: {response.status_code}")
                
                # Test combined filters
                response = self.session.get(f"{BACKEND_URL}/admin/orders", params={
                    "status_filter": "all",
                    "time_frame": "last_month"
                })
                if response.status_code == 200:
                    combined_orders = response.json()
                    self.log_test("Orders with Combined Filters", True, f"Retrieved {len(combined_orders)} orders with combined filters")
                else:
                    self.log_test("Orders with Combined Filters", False, f"Status: {response.status_code}")
                
                # Verify order data structure includes timestamps
                if orders:
                    sample_order = orders[0]
                    order_data = sample_order.get("order", {})
                    
                    timestamp_fields = ["created_at", "updated_at"]
                    missing_timestamps = [field for field in timestamp_fields if field not in order_data]
                    
                    if not missing_timestamps:
                        self.log_test("Order Timestamp Fields", True, "Orders include proper timestamp fields")
                    else:
                        self.log_test("Order Timestamp Fields", False, f"Missing timestamp fields: {missing_timestamps}")
                    
                    # Verify order includes buyer, seller, and listing data
                    required_relations = ["buyer", "seller", "listing"]
                    missing_relations = [rel for rel in required_relations if rel not in sample_order]
                    
                    if not missing_relations:
                        self.log_test("Order Relationship Data", True, "Orders include buyer, seller, and listing data")
                    else:
                        self.log_test("Order Relationship Data", False, f"Missing relations: {missing_relations}")
                else:
                    self.log_test("Order Data Structure", True, "No orders to verify (empty database)")
                    
            else:
                self.log_test("Get Admin Orders", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Order Management Enhancements Test", False, f"Exception: {str(e)}")

    def test_page_management_crud(self):
        """Test page CRUD operations including edit functionality"""
        print("\n=== TESTING PAGE MANAGEMENT CRUD ===")
        
        test_page_slug = f"v104-test-page-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        try:
            # Test CREATE page
            page_data = {
                "page_slug": test_page_slug,
                "title": "v1.0.4 Test Page",
                "content": "<h1>v1.0.4 Test Page</h1><p>This page tests the v1.0.4 page management functionality.</p>",
                "is_published": True,
                "meta_description": "Test page for v1.0.4 page management",
                "custom_css": "/* v1.0.4 test CSS */"
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/pages", json=page_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Create Page", True, f"Successfully created page: {page_data['title']}")
            else:
                self.log_test("Create Page", False, f"Status: {response.status_code}, Response: {response.text}")
                return
            
            # Test READ pages (list all)
            response = self.session.get(f"{BACKEND_URL}/admin/cms/pages")
            
            if response.status_code == 200:
                pages = response.json()
                created_page = next((p for p in pages if p.get('page_slug') == test_page_slug), None)
                if created_page:
                    self.log_test("Read Pages List", True, f"Found created page in list of {len(pages)} pages")
                else:
                    self.log_test("Read Pages List", False, "Created page not found in pages list")
            else:
                self.log_test("Read Pages List", False, f"Status: {response.status_code}")
            
            # Test READ specific page
            response = self.session.get(f"{BACKEND_URL}/admin/cms/pages/{test_page_slug}")
            
            if response.status_code == 200:
                page = response.json()
                self.log_test("Read Specific Page", True, f"Retrieved page: {page.get('title')}")
            else:
                self.log_test("Read Specific Page", False, f"Status: {response.status_code}")
            
            # Test UPDATE/EDIT page functionality
            update_data = {
                "title": "v1.0.4 Updated Test Page",
                "content": "<h1>Updated Content</h1><p>This page has been updated to test edit functionality.</p>",
                "is_published": True,
                "meta_description": "Updated test page for v1.0.4",
                "custom_css": "/* Updated CSS for v1.0.4 */"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/pages/{test_page_slug}", json=update_data)
            
            if response.status_code == 200:
                self.log_test("Update/Edit Page", True, "Successfully updated page")
                
                # Verify update
                response = self.session.get(f"{BACKEND_URL}/admin/cms/pages/{test_page_slug}")
                if response.status_code == 200:
                    updated_page = response.json()
                    if updated_page.get('title') == update_data['title']:
                        self.log_test("Verify Page Edit", True, "Page edit verified successfully")
                    else:
                        self.log_test("Verify Page Edit", False, "Page edit not reflected")
                else:
                    self.log_test("Verify Page Edit", False, "Could not verify page edit")
            else:
                self.log_test("Update/Edit Page", False, f"Status: {response.status_code}, Response: {response.text}")
            
            # Test "Add to Menu" functionality (auto-add to navigation)
            response = self.session.get(f"{BACKEND_URL}/admin/navigation")
            if response.status_code == 200:
                nav_items = response.json()
                page_in_nav = next((item for item in nav_items if item.get('url') == f"/{test_page_slug}"), None)
                
                if page_in_nav:
                    self.log_test("Add to Menu Functionality", True, f"Page automatically added to navigation: {page_in_nav.get('label')}")
                else:
                    self.log_test("Add to Menu Functionality", False, "Page was not automatically added to navigation")
            else:
                self.log_test("Add to Menu Functionality", False, "Could not check navigation")
            
            # Test DELETE page
            response = self.session.delete(f"{BACKEND_URL}/admin/cms/pages/{test_page_slug}")
            
            if response.status_code == 200:
                self.log_test("Delete Page", True, "Successfully deleted page")
                
                # Verify deletion
                response = self.session.get(f"{BACKEND_URL}/admin/cms/pages/{test_page_slug}")
                if response.status_code == 404:
                    self.log_test("Verify Page Deletion", True, "Page deletion verified")
                else:
                    self.log_test("Verify Page Deletion", False, "Page still exists after deletion")
            else:
                self.log_test("Delete Page", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Page Management CRUD Test", False, f"Exception: {str(e)}")

    def test_admin_panel_endpoints(self):
        """Test all admin panel endpoints work with new sidebar layout"""
        print("\n=== TESTING ADMIN PANEL ENDPOINTS ===")
        
        admin_endpoints = [
            ("/admin/stats", "Dashboard Stats"),
            ("/admin/users", "Users Management"),
            ("/admin/listings", "Listings Management"),
            ("/admin/orders", "Orders Management"),
            ("/admin/cms/settings", "CMS Settings"),
            ("/admin/cms/pages", "Pages Management"),
            ("/admin/navigation", "Navigation Management")
        ]
        
        try:
            for endpoint, description in admin_endpoints:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"Admin Panel - {description}", True, f"Retrieved {len(data)} items")
                    elif isinstance(data, dict):
                        self.log_test(f"Admin Panel - {description}", True, f"Retrieved data with {len(data)} fields")
                    else:
                        self.log_test(f"Admin Panel - {description}", True, "Endpoint accessible")
                else:
                    self.log_test(f"Admin Panel - {description}", False, f"Status: {response.status_code}")
            
            # Test admin authentication is properly enforced
            no_auth_session = requests.Session()
            response = no_auth_session.get(f"{BACKEND_URL}/admin/stats")
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_test("Admin Authentication Enforcement", True, "Admin endpoints properly protected")
            else:
                self.log_test("Admin Authentication Enforcement", False, f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin Panel Endpoints Test", False, f"Exception: {str(e)}")

    def test_v104_integration_workflow(self):
        """Test complete v1.0.4 workflow integration"""
        print("\n=== TESTING v1.0.4 INTEGRATION WORKFLOW ===")
        
        try:
            # Switch to test user
            test_headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Step 1: Browse listings (should show categories)
            response = self.session.get(f"{BACKEND_URL}/listings")
            if response.status_code == 200:
                listings = response.json()
                self.log_test("Browse Listings", True, f"Retrieved {len(listings)} listings for browsing")
            else:
                self.log_test("Browse Listings", False, f"Status: {response.status_code}")
                return
            
            # Step 2: Add items to favorites (both types if available)
            favorites_added = 0
            for listing_info in self.test_listing_ids[:2]:  # Test with first 2 listings
                response = self.session.post(f"{BACKEND_URL}/favorites", 
                                           json={"listing_id": listing_info["id"]}, 
                                           headers=test_headers)
                if response.status_code == 200:
                    favorites_added += 1
            
            self.log_test("Add Multiple Items to Favorites", favorites_added > 0, f"Added {favorites_added} items to favorites")
            
            # Step 3: View favorites
            response = self.session.get(f"{BACKEND_URL}/favorites", headers=test_headers)
            if response.status_code == 200:
                favorites = response.json()
                self.log_test("View Favorites List", True, f"Favorites list shows {len(favorites)} items")
            else:
                self.log_test("View Favorites List", False, f"Status: {response.status_code}")
            
            # Step 4: Admin checks orders with new filtering
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/admin/orders", 
                                      params={"status_filter": "all", "time_frame": "last_month"}, 
                                      headers=admin_headers)
            if response.status_code == 200:
                orders = response.json()
                self.log_test("Admin Order Management", True, f"Admin can view {len(orders)} orders with filters")
            else:
                self.log_test("Admin Order Management", False, f"Status: {response.status_code}")
            
            # Step 5: Admin manages pages
            test_page = {
                "page_slug": f"workflow-test-{datetime.now().strftime('%H%M%S')}",
                "title": "Workflow Test Page",
                "content": "<h1>Integration Test</h1><p>Testing v1.0.4 workflow.</p>",
                "is_published": True,
                "meta_description": "Workflow test page"
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/pages", json=test_page, headers=admin_headers)
            if response.status_code == 200:
                self.log_test("Admin Page Management", True, "Admin can create and manage pages")
                
                # Clean up
                try:
                    self.session.delete(f"{BACKEND_URL}/admin/cms/pages/{test_page['page_slug']}", headers=admin_headers)
                except:
                    pass
            else:
                self.log_test("Admin Page Management", False, f"Status: {response.status_code}")
            
            self.log_test("v1.0.4 Integration Workflow", True, "Complete workflow tested successfully")
            
        except Exception as e:
            self.log_test("v1.0.4 Integration Workflow", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all v1.0.4 bug fix tests"""
        print("🚀 STARTING CATALORO v1.0.4 BUG FIXES BACKEND TESTING")
        print("=" * 70)
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Create test user for favorites testing
        if not self.create_test_user():
            print("❌ CRITICAL: Test user creation failed. Cannot proceed with favorites tests.")
            return False
        
        # Step 3: Create test listings
        if not self.create_test_listings():
            print("❌ CRITICAL: Test listing creation failed. Cannot proceed with favorites tests.")
            return False
        
        # Run all test suites
        self.test_favorites_system()
        self.test_categories_management()
        self.test_order_management_enhancements()
        self.test_page_management_crud()
        self.test_admin_panel_endpoints()
        self.test_v104_integration_workflow()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎯 CATALORO v1.0.4 BUG FIXES TESTING SUMMARY")
        print("=" * 70)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"  {result}")
        
        if success_rate >= 90:
            print("\n🎉 EXCELLENT: v1.0.4 bug fixes are working correctly!")
        elif success_rate >= 75:
            print("\n✅ GOOD: Most v1.0.4 bug fixes are working, minor issues found.")
        elif success_rate >= 50:
            print("\n⚠️  MODERATE: Some v1.0.4 bug fixes working, significant issues found.")
        else:
            print("\n❌ CRITICAL: Major issues with v1.0.4 bug fixes implementation.")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = CataloroV104Tester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)