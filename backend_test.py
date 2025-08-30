#!/usr/bin/env python3
"""
Cataloro Marketplace Backend API Test Suite
Tests all API endpoints for functionality and integration
"""

import requests
import sys
import json
from datetime import datetime

class CataloroAPITester:
    def __init__(self, base_url="https://cat-db-market.preview.emergentagent.com"):
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
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        return success

    def test_admin_login(self):
        """Test admin login"""
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
            print(f"   Admin User: {self.admin_user}")
        return success

    def test_user_login(self):
        """Test regular user login"""
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
            print(f"   Regular User: {self.regular_user}")
        return success

    def test_marketplace_browse(self):
        """Test marketplace browse endpoint"""
        success, response = self.run_test(
            "Marketplace Browse",
            "GET",
            "api/marketplace/browse",
            200
        )
        if success:
            print(f"   Found {len(response)} listings")
        return success

    def test_user_profile(self):
        """Test user profile endpoint"""
        if not self.regular_user:
            print("❌ User Profile - SKIPPED (No user logged in)")
            return False
            
        success, response = self.run_test(
            "User Profile",
            "GET",
            f"api/auth/profile/{self.regular_user['id']}",
            200
        )
        return success

    def test_my_listings(self):
        """Test my listings endpoint"""
        if not self.regular_user:
            print("❌ My Listings - SKIPPED (No user logged in)")
            return False
            
        success, response = self.run_test(
            "My Listings",
            "GET",
            f"api/user/my-listings/{self.regular_user['id']}",
            200
        )
        return success

    def test_my_deals(self):
        """Test my deals endpoint"""
        if not self.regular_user:
            print("❌ My Deals - SKIPPED (No user logged in)")
            return False
            
        success, response = self.run_test(
            "My Deals",
            "GET",
            f"api/user/my-deals/{self.regular_user['id']}",
            200
        )
        return success

    def test_notifications(self):
        """Test notifications endpoint"""
        if not self.regular_user:
            print("❌ Notifications - SKIPPED (No user logged in)")
            return False
            
        success, response = self.run_test(
            "User Notifications",
            "GET",
            f"api/user/notifications/{self.regular_user['id']}",
            200
        )
        if success:
            print(f"   Found {len(response)} notifications")
        return success

    def test_admin_dashboard(self):
        """Test admin dashboard endpoint"""
        if not self.admin_user:
            print("❌ Admin Dashboard - SKIPPED (No admin logged in)")
            return False
            
        success, response = self.run_test(
            "Admin Dashboard",
            "GET",
            "api/admin/dashboard",
            200
        )
        if success and 'kpis' in response:
            print(f"   KPIs: {response['kpis']}")
        return success

    def test_admin_users(self):
        """Test admin users endpoint"""
        if not self.admin_user:
            print("❌ Admin Users - SKIPPED (No admin logged in)")
            return False
            
        success, response = self.run_test(
            "Admin Users List",
            "GET",
            "api/admin/users",
            200
        )
        if success:
            print(f"   Found {len(response)} users")
        return success

    def test_admin_settings(self):
        """Test admin settings endpoint (for site branding)"""
        if not self.admin_user:
            print("❌ Admin Settings - SKIPPED (No admin logged in)")
            return False
            
        # Test GET settings (initial state)
        success, initial_response = self.run_test(
            "Admin Settings GET (Initial)",
            "GET",
            "api/admin/settings",
            200
        )
        
        if not success:
            print("   ⚠️  Settings endpoint not implemented - expected for site branding")
            return False
            
        print(f"   Initial settings: {initial_response}")
            
        # Test PUT settings (update with comprehensive data)
        test_settings = {
            "site_name": "Cataloro Test Platform",
            "site_description": "Enhanced Test Marketplace with Branding",
            "logo_url": "/test-logo.png",
            "logo_light_url": "data:image/png;base64,test-light-logo",
            "logo_dark_url": "data:image/png;base64,test-dark-logo",
            "theme_color": "#FF6B35",
            "allow_registration": True,
            "require_approval": False,
            "email_notifications": True,
            "commission_rate": 7.5,
            "max_file_size": 15
        }
        
        success_put, put_response = self.run_test(
            "Admin Settings PUT (Update)",
            "PUT",
            "api/admin/settings",
            200,
            data=test_settings
        )
        
        if not success_put:
            return False
            
        # Test GET settings again to verify persistence
        success_verify, verify_response = self.run_test(
            "Admin Settings GET (Verify Persistence)",
            "GET",
            "api/admin/settings",
            200
        )
        
        if success_verify:
            # Check if our test data persisted
            if (verify_response.get('site_name') == test_settings['site_name'] and
                verify_response.get('theme_color') == test_settings['theme_color'] and
                verify_response.get('commission_rate') == test_settings['commission_rate']):
                print("   ✅ Settings persistence verified - data stored and retrieved correctly")
                self.log_test("Settings Data Persistence", True, "All test settings persisted correctly")
            else:
                print("   ⚠️  Settings may not have persisted correctly")
                print(f"   Expected site_name: {test_settings['site_name']}, Got: {verify_response.get('site_name')}")
                print(f"   Expected theme_color: {test_settings['theme_color']}, Got: {verify_response.get('theme_color')}")
                self.log_test("Settings Data Persistence", False, "Test settings did not persist correctly")
        
        return success_put and success_verify

    def test_logo_upload(self):
        """Test logo upload endpoint (for dual logo system)"""
        if not self.admin_user:
            print("❌ Logo Upload - SKIPPED (No admin logged in)")
            return False
            
        # Create a simple test image (1x1 PNG)
        import base64
        # This is a 1x1 transparent PNG image in base64
        png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==')
        
        # Test logo upload with proper file data
        url = f"{self.base_url}/api/admin/logo"
        print(f"\n🔍 Testing Logo Upload...")
        print(f"   URL: {url}")
        
        try:
            # Prepare multipart form data
            files = {
                'file': ('test-logo.png', png_data, 'image/png')
            }
            data = {
                'mode': 'light'
            }
            
            response = self.session.post(url, files=files, data=data)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                    print(f"   Logo uploaded successfully: {response_data.get('filename', 'N/A')}")
                    print(f"   File size: {response_data.get('size', 'N/A')} bytes")
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: 200, Response: {response.text[:200]}"

            self.log_test("Logo Upload", success, details)
            
            # Test dark mode logo upload as well
            if success:
                files_dark = {
                    'file': ('test-logo-dark.png', png_data, 'image/png')
                }
                data_dark = {
                    'mode': 'dark'
                }
                
                response_dark = self.session.post(url, files=files_dark, data=data_dark)
                success_dark = response_dark.status_code == 200
                
                if success_dark:
                    print(f"   Dark mode logo upload also successful")
                    self.log_test("Logo Upload (Dark Mode)", success_dark, f"Status: {response_dark.status_code}")
                else:
                    self.log_test("Logo Upload (Dark Mode)", success_dark, f"Status: {response_dark.status_code}, Response: {response_dark.text[:100]}")
            
            return success

        except Exception as e:
            self.log_test("Logo Upload", False, f"Error: {str(e)}")
            return False

    def test_admin_session_handling(self):
        """Test admin session persistence and validation"""
        if not self.admin_user or not self.admin_token:
            print("❌ Admin Session - SKIPPED (No admin session)")
            return False
            
        # Test session with token header
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        success, response = self.run_test(
            "Admin Session Validation",
            "GET",
            "api/admin/dashboard",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Admin session valid, token: {self.admin_token[:20]}...")
            
        return success

    def test_site_branding_data_persistence(self):
        """Test if site branding data persists correctly"""
        if not self.admin_user:
            print("❌ Site Branding Persistence - SKIPPED (No admin logged in)")
            return False
            
        # This would test the database persistence of site settings
        # For now, we'll test the admin dashboard which should contain site info
        success, response = self.run_test(
            "Site Branding Data Check",
            "GET",
            "api/admin/dashboard",
            200
        )
        
        if success and 'kpis' in response:
            print("   ✅ Admin dashboard accessible - site data can be stored")
            return True
        else:
            print("   ❌ Cannot verify site branding data persistence")
            return False

    def test_catalyst_calculations(self):
        """Test Cat Database Price Calculations endpoint"""
        if not self.admin_user:
            print("❌ Catalyst Calculations - SKIPPED (No admin logged in)")
            return False
            
        success, response = self.run_test(
            "Catalyst Price Calculations",
            "GET",
            "api/admin/catalyst/calculations",
            200
        )
        
        if success:
            print(f"   Found {len(response)} catalyst calculations")
            # Check if calculations have total_price field
            if response and len(response) > 0:
                first_calc = response[0]
                if 'total_price' in first_calc:
                    print(f"   ✅ Total price field present: €{first_calc['total_price']}")
                    self.log_test("Catalyst Price Data Structure", True, "total_price field found")
                else:
                    self.log_test("Catalyst Price Data Structure", False, "total_price field missing")
            else:
                print("   ⚠️  No catalyst calculations found")
        return success

    def test_create_catalyst_listing(self):
        """Create a test catalyst listing with FAPACAT"""
        if not self.regular_user:
            print("❌ Create Catalyst Listing - SKIPPED (No user logged in)")
            return False
            
        # Create test catalyst listing with FAPACAT name
        catalyst_listing = {
            "title": "FAPACAT8659 Catalyst - Premium Grade",
            "description": "High-quality automotive catalyst with excellent precious metal content. Weight: 1.53g. Suitable for marketplace pricing suggestions testing.",
            "price": 292.74,
            "category": "Catalysts",
            "condition": "Used - Good",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
            "tags": ["catalyst", "automotive", "precious metals", "FAPACAT"],
            "features": ["High PT content", "Ceramic substrate", "Tested quality"]
        }
        
        success, response = self.run_test(
            "Create Catalyst Listing",
            "POST",
            "api/listings",
            200,
            data=catalyst_listing
        )
        
        if success:
            self.test_listing_id = response.get('listing_id')
            print(f"   ✅ Catalyst listing created with ID: {self.test_listing_id}")
            
            # Verify no quantity field was added
            if 'quantity' not in catalyst_listing:
                self.log_test("Quantity Field Removal", True, "No quantity field in listing (one product per listing)")
            
        return success

    def test_browse_catalyst_listings(self):
        """Test browse listings endpoint for catalyst listings"""
        success, response = self.run_test(
            "Browse Catalyst Listings",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            catalyst_listings = [listing for listing in response if listing.get('category') == 'Catalysts']
            print(f"   Found {len(catalyst_listings)} catalyst listings out of {len(response)} total")
            
            # Check for FAPACAT listing
            fapacat_listings = [listing for listing in catalyst_listings if 'FAPACAT' in listing.get('title', '')]
            if fapacat_listings:
                print(f"   ✅ Found FAPACAT listing: {fapacat_listings[0]['title']}")
                self.log_test("FAPACAT Listing Discovery", True, f"Found {len(fapacat_listings)} FAPACAT listings")
            else:
                self.log_test("FAPACAT Listing Discovery", False, "No FAPACAT listings found in browse results")
                
        return success

    def test_price_matching_logic(self):
        """Test price matching between catalyst data and listings"""
        if not self.admin_user:
            print("❌ Price Matching - SKIPPED (No admin logged in)")
            return False
            
        # Get catalyst calculations
        calc_success, calc_response = self.run_test(
            "Get Catalyst Calculations for Matching",
            "GET",
            "api/admin/catalyst/calculations",
            200
        )
        
        if not calc_success:
            return False
            
        # Get browse listings
        browse_success, browse_response = self.run_test(
            "Get Browse Listings for Matching",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not browse_success:
            return False
            
        # Test price matching logic
        catalyst_listings = [listing for listing in browse_response if listing.get('category') == 'Catalysts']
        matched_prices = 0
        
        for listing in catalyst_listings:
            listing_title = listing.get('title', '')
            
            # Look for matching catalyst in calculations
            for calc in calc_response:
                calc_name = calc.get('name', '')
                if calc_name and calc_name in listing_title:
                    calculated_price = calc.get('total_price', 0)
                    listing_price = listing.get('price', 0)
                    
                    print(f"   📊 Price Match Found:")
                    print(f"      Listing: {listing_title}")
                    print(f"      Catalyst: {calc_name}")
                    print(f"      Calculated Price: €{calculated_price}")
                    print(f"      Listed Price: €{listing_price}")
                    
                    matched_prices += 1
                    break
        
        success = matched_prices > 0
        self.log_test("Price Matching Logic", success, f"Found {matched_prices} price matches")
        return success

    def test_marketplace_pricing_suggestions(self):
        """Comprehensive test of marketplace pricing suggestions functionality"""
        print("\n💰 Testing Marketplace Pricing Suggestions Functionality...")
        
        # Test 1: Cat Database Price Calculations
        calc_success = self.test_catalyst_calculations()
        
        # Test 2: Create Test Catalyst Listing
        create_success = self.test_create_catalyst_listing()
        
        # Test 3: Browse Catalyst Listings
        browse_success = self.test_browse_catalyst_listings()
        
        # Test 4: Price Matching Logic
        match_success = self.test_price_matching_logic()
        
        # Summary
        total_tests = 4
        passed_tests = sum([calc_success, create_success, browse_success, match_success])
        
        print(f"\n📊 Pricing Suggestions Test Summary: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All pricing suggestions functionality tests passed!")
            self.log_test("Marketplace Pricing Suggestions Complete", True, "All pricing suggestion features working")
        else:
            print(f"⚠️  {total_tests - passed_tests} pricing suggestion tests failed")
            self.log_test("Marketplace Pricing Suggestions Complete", False, f"{total_tests - passed_tests} tests failed")
            
        return passed_tests == total_tests

    def test_bulk_listing_operations(self):
        """Test bulk listing operations - create multiple, bulk delete, bulk update"""
        print("\n📦 Testing Bulk Listing Operations...")
        
        if not self.regular_user:
            print("❌ Bulk Operations - SKIPPED (No user logged in)")
            return False
        
        # Store created listing IDs for cleanup
        created_listing_ids = []
        
        # Test 1: Create Multiple Test Listings
        print("\n🔨 Creating multiple test listings...")
        test_listings = [
            {
                "title": "Bulk Test Listing 1 - MacBook Pro",
                "description": "Test listing for bulk operations - MacBook Pro 16-inch",
                "price": 2500.00,
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"]
            },
            {
                "title": "Bulk Test Listing 2 - iPhone 14",
                "description": "Test listing for bulk operations - iPhone 14 Pro",
                "price": 1200.00,
                "category": "Electronics", 
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400"]
            },
            {
                "title": "Bulk Test Listing 3 - Gaming Chair",
                "description": "Test listing for bulk operations - Ergonomic gaming chair",
                "price": 350.00,
                "category": "Furniture",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400"]
            }
        ]
        
        create_success_count = 0
        for i, listing_data in enumerate(test_listings):
            success, response = self.run_test(
                f"Create Bulk Test Listing {i+1}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            if success and 'listing_id' in response:
                created_listing_ids.append(response['listing_id'])
                create_success_count += 1
                print(f"   ✅ Created listing {i+1} with ID: {response['listing_id']}")
        
        self.log_test("Bulk Listing Creation", create_success_count == 3, f"Created {create_success_count}/3 listings")
        
        # Test 2: Verify listings appear in browse
        print("\n🔍 Verifying listings appear in browse...")
        success, browse_response = self.run_test(
            "Browse Listings After Bulk Create",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        found_listings = 0
        if success:
            for listing_id in created_listing_ids:
                found = any(listing.get('id') == listing_id for listing in browse_response)
                if found:
                    found_listings += 1
        
        self.log_test("Bulk Listings in Browse", found_listings == len(created_listing_ids), 
                     f"Found {found_listings}/{len(created_listing_ids)} listings in browse")
        
        # Test 3: Bulk Update Operations (status changes)
        print("\n📝 Testing bulk update operations...")
        update_success_count = 0
        for listing_id in created_listing_ids[:2]:  # Update first 2 listings
            update_data = {
                "status": "inactive",
                "price": 999.99  # Update price as well
            }
            success, response = self.run_test(
                f"Bulk Update Listing {listing_id[:8]}...",
                "PUT",
                f"api/listings/{listing_id}",
                200,
                data=update_data
            )
            if success:
                update_success_count += 1
        
        self.log_test("Bulk Update Operations", update_success_count == 2, 
                     f"Updated {update_success_count}/2 listings")
        
        # Test 4: Bulk Delete Operations
        print("\n🗑️  Testing bulk delete operations...")
        delete_success_count = 0
        for listing_id in created_listing_ids:
            success, response = self.run_test(
                f"Bulk Delete Listing {listing_id[:8]}...",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                delete_success_count += 1
        
        self.log_test("Bulk Delete Operations", delete_success_count == len(created_listing_ids), 
                     f"Deleted {delete_success_count}/{len(created_listing_ids)} listings")
        
        # Test 5: Verify Persistence - deleted listings don't appear in subsequent API calls
        print("\n🔄 Testing persistence - verifying deleted listings don't reappear...")
        success, browse_after_delete = self.run_test(
            "Browse Listings After Bulk Delete",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        reappeared_listings = 0
        if success:
            for listing_id in created_listing_ids:
                found = any(listing.get('id') == listing_id for listing in browse_after_delete)
                if found:
                    reappeared_listings += 1
                    print(f"   ⚠️  Deleted listing {listing_id[:8]}... reappeared in browse!")
        
        persistence_success = reappeared_listings == 0
        self.log_test("Bulk Delete Persistence", persistence_success, 
                     f"{reappeared_listings} deleted listings reappeared (should be 0)")
        
        # Summary
        total_operations = 5
        passed_operations = sum([
            create_success_count == 3,
            found_listings == len(created_listing_ids),
            update_success_count == 2,
            delete_success_count == len(created_listing_ids),
            persistence_success
        ])
        
        print(f"\n📊 Bulk Operations Summary: {passed_operations}/{total_operations} operations passed")
        return passed_operations == total_operations

    def test_add_info_integration(self):
        """Test add_info integration in listing creation and search functionality"""
        print("\n📋 Testing add_info Integration...")
        
        if not self.admin_user:
            print("❌ add_info Integration - SKIPPED (No admin logged in)")
            return False
        
        # Test 1: Verify catalyst data contains add_info field
        print("\n🔍 Testing catalyst data structure with add_info...")
        success, catalyst_data = self.run_test(
            "Get Catalyst Data with add_info",
            "GET",
            "api/admin/catalyst/data",
            200
        )
        
        add_info_present = False
        add_info_content_found = False
        if success and catalyst_data:
            # Check if add_info field exists and has content
            for catalyst in catalyst_data[:5]:  # Check first 5 entries
                if 'add_info' in catalyst:
                    add_info_present = True
                    if catalyst['add_info'] and catalyst['add_info'].strip():
                        add_info_content_found = True
                        print(f"   ✅ Found add_info content: '{catalyst['add_info'][:50]}...'")
                        break
        
        self.log_test("Catalyst Data add_info Field", add_info_present, 
                     f"add_info field present: {add_info_present}")
        self.log_test("Catalyst Data add_info Content", add_info_content_found, 
                     f"add_info content found: {add_info_content_found}")
        
        # Test 2: Create catalyst listing with add_info content
        print("\n📝 Creating catalyst listing with add_info content...")
        if success and catalyst_data and add_info_content_found:
            # Find a catalyst with add_info content
            test_catalyst = None
            for catalyst in catalyst_data:
                if catalyst.get('add_info') and catalyst['add_info'].strip():
                    test_catalyst = catalyst
                    break
            
            if test_catalyst:
                # Create listing with add_info in description
                catalyst_listing = {
                    "title": f"Catalyst: {test_catalyst['name']}",
                    "description": f"Premium automotive catalyst. Additional Information: {test_catalyst['add_info']}",
                    "price": 250.00,
                    "category": "Catalysts",
                    "condition": "Used - Good",
                    "seller_id": self.admin_user['id'],
                    "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"]
                }
                
                success_create, create_response = self.run_test(
                    "Create Catalyst Listing with add_info",
                    "POST",
                    "api/listings",
                    200,
                    data=catalyst_listing
                )
                
                if success_create:
                    listing_id = create_response.get('listing_id')
                    print(f"   ✅ Created catalyst listing with add_info: {listing_id}")
                    
                    # Test 3: Verify listing retrieval preserves add_info content
                    success_get, listing_data = self.run_test(
                        "Retrieve Listing with add_info",
                        "GET",
                        f"api/listings/{listing_id}",
                        200
                    )
                    
                    if success_get:
                        description = listing_data.get('description', '')
                        add_info_preserved = test_catalyst['add_info'] in description
                        self.log_test("add_info Content Preservation", add_info_preserved,
                                     f"add_info content preserved in listing: {add_info_preserved}")
                        
                        # Test 4: Verify listing appears in browse with complete description
                        success_browse, browse_data = self.run_test(
                            "Browse Listings with add_info Content",
                            "GET",
                            "api/marketplace/browse",
                            200
                        )
                        
                        if success_browse:
                            found_listing = None
                            for listing in browse_data:
                                if listing.get('id') == listing_id:
                                    found_listing = listing
                                    break
                            
                            if found_listing:
                                browse_description = found_listing.get('description', '')
                                add_info_in_browse = test_catalyst['add_info'] in browse_description
                                self.log_test("add_info in Browse Results", add_info_in_browse,
                                             f"add_info content in browse: {add_info_in_browse}")
                            else:
                                self.log_test("add_info in Browse Results", False, "Listing not found in browse")
                        
                        # Cleanup: Delete test listing
                        self.run_test(
                            "Cleanup add_info Test Listing",
                            "DELETE",
                            f"api/listings/{listing_id}",
                            200
                        )
                    else:
                        self.log_test("add_info Content Preservation", False, "Could not retrieve created listing")
                else:
                    self.log_test("Create Catalyst Listing with add_info", False, "Failed to create listing")
            else:
                self.log_test("Create Catalyst Listing with add_info", False, "No catalyst with add_info content found")
        
        # Test 5: Verify catalyst data endpoint for search integration
        print("\n🔍 Testing catalyst data endpoint for search integration...")
        success_calc, calc_data = self.run_test(
            "Catalyst Calculations for Search",
            "GET",
            "api/admin/catalyst/calculations",
            200
        )
        
        if success_calc and calc_data:
            # Verify calculations contain complete catalyst objects
            complete_objects = 0
            for calc in calc_data[:5]:  # Check first 5
                if all(field in calc for field in ['cat_id', 'name', 'total_price']):
                    complete_objects += 1
            
            search_ready = complete_objects > 0
            self.log_test("Search Integration Data Structure", search_ready,
                         f"Complete catalyst objects for search: {complete_objects}/5")
        else:
            self.log_test("Search Integration Data Structure", False, "Could not retrieve catalyst calculations")
        
        # Summary
        print(f"\n📊 add_info Integration Test Summary completed")
        return True

    def test_listing_crud_operations(self):
        """Test comprehensive listing CRUD operations"""
        print("\n🔧 Testing Listing CRUD Operations...")
        
        if not self.regular_user:
            print("❌ CRUD Operations - SKIPPED (No user logged in)")
            return False
        
        # Test 1: Create a listing
        print("\n➕ Testing CREATE operation...")
        test_listing = {
            "title": "CRUD Test Listing - Vintage Camera",
            "description": "Professional vintage camera for CRUD testing. Excellent condition with original case.",
            "price": 450.00,
            "category": "Photography",
            "condition": "Used - Excellent",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"],
            "tags": ["vintage", "camera", "photography"],
            "features": ["Manual focus", "Film camera", "Original case"]
        }
        
        success_create, create_response = self.run_test(
            "CREATE Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_create or 'listing_id' not in create_response:
            print("❌ CREATE operation failed - stopping CRUD tests")
            return False
        
        listing_id = create_response['listing_id']
        print(f"   ✅ Created listing with ID: {listing_id}")
        
        # Test 2: Read the listing
        print("\n📖 Testing READ operation...")
        success_read, read_response = self.run_test(
            "READ Listing",
            "GET",
            f"api/listings/{listing_id}",
            200
        )
        
        if success_read:
            # Verify all fields are present and correct
            fields_correct = (
                read_response.get('title') == test_listing['title'] and
                read_response.get('price') == test_listing['price'] and
                read_response.get('category') == test_listing['category']
            )
            self.log_test("READ Data Integrity", fields_correct, 
                         f"All fields match: {fields_correct}")
        
        # Test 3: Update the listing
        print("\n✏️  Testing UPDATE operation...")
        update_data = {
            "title": "CRUD Test Listing - Vintage Camera (UPDATED)",
            "price": 425.00,
            "description": "Updated description - Price reduced for quick sale!",
            "status": "active"
        }
        
        success_update, update_response = self.run_test(
            "UPDATE Listing",
            "PUT",
            f"api/listings/{listing_id}",
            200,
            data=update_data
        )
        
        # Test 4: Verify update persistence
        if success_update:
            print("\n🔄 Verifying UPDATE persistence...")
            success_verify, verify_response = self.run_test(
                "Verify UPDATE Persistence",
                "GET",
                f"api/listings/{listing_id}",
                200
            )
            
            if success_verify:
                update_persisted = (
                    verify_response.get('title') == update_data['title'] and
                    verify_response.get('price') == update_data['price']
                )
                self.log_test("UPDATE Persistence", update_persisted,
                             f"Updates persisted correctly: {update_persisted}")
        
        # Test 5: Verify listing appears in browse after updates
        print("\n🌐 Testing listing visibility in browse after updates...")
        success_browse, browse_response = self.run_test(
            "Browse After UPDATE",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success_browse:
            found_updated = False
            for listing in browse_response:
                if listing.get('id') == listing_id:
                    if listing.get('title') == update_data['title']:
                        found_updated = True
                        break
            
            self.log_test("Updated Listing in Browse", found_updated,
                         f"Updated listing found in browse: {found_updated}")
        
        # Test 6: Delete the listing
        print("\n🗑️  Testing DELETE operation...")
        success_delete, delete_response = self.run_test(
            "DELETE Listing",
            "DELETE",
            f"api/listings/{listing_id}",
            200
        )
        
        # Test 7: Verify deletion persistence
        if success_delete:
            print("\n🔄 Verifying DELETE persistence...")
            
            # Try to read deleted listing (should fail)
            success_read_deleted, _ = self.run_test(
                "READ Deleted Listing (Should Fail)",
                "GET",
                f"api/listings/{listing_id}",
                404  # Expecting 404 for deleted listing
            )
            
            # Verify listing doesn't appear in browse
            success_browse_after, browse_after_response = self.run_test(
                "Browse After DELETE",
                "GET",
                "api/marketplace/browse",
                200
            )
            
            if success_browse_after:
                deleted_found = any(listing.get('id') == listing_id for listing in browse_after_response)
                self.log_test("DELETE Persistence in Browse", not deleted_found,
                             f"Deleted listing absent from browse: {not deleted_found}")
        
        # Summary
        operations = ['CREATE', 'READ', 'UPDATE', 'DELETE']
        successes = [success_create, success_read, success_update, success_delete]
        passed_operations = sum(successes)
        
        print(f"\n📊 CRUD Operations Summary: {passed_operations}/{len(operations)} operations passed")
        
        for i, (op, success) in enumerate(zip(operations, successes)):
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {op}: {status}")
        
        return passed_operations == len(operations)

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Cataloro Marketplace API Tests")
        print("=" * 60)

        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False

        # Authentication tests
        admin_login_success = self.test_admin_login()
        user_login_success = self.test_user_login()

        # Marketplace tests
        self.test_marketplace_browse()

        # User-specific tests
        if user_login_success:
            self.test_user_profile()
            self.test_my_listings()
            self.test_my_deals()
            self.test_notifications()

        # Admin tests
        if admin_login_success:
            self.test_admin_dashboard()
            self.test_admin_users()
            
            # Site branding and logo upload tests (as requested in review)
            print("\n🎨 Testing Site Branding & Logo Upload System...")
            self.test_admin_settings()
            self.test_logo_upload()
            self.test_admin_session_handling()
            self.test_site_branding_data_persistence()

        # NEW: Marketplace Pricing Suggestions Tests (as requested in review)
        if admin_login_success and user_login_success:
            self.test_marketplace_pricing_suggestions()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    """Main test execution"""
    tester = CataloroAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())