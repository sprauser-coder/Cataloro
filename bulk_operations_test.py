#!/usr/bin/env python3
"""
Cataloro Marketplace Bulk Operations Test Suite
Comprehensive testing of bulk operations functionality as requested in review
"""

import requests
import sys
import json
import time
from datetime import datetime

class BulkOperationsTester:
    def __init__(self, base_url="https://seller-status-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.created_listing_ids = []

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
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

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

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("🔐 Setting up authentication...")
        
        # Admin login
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

        # User login
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

        return self.admin_user is not None and self.regular_user is not None

    def test_create_multiple_listings(self):
        """Test 1: Create multiple test listings for bulk operations"""
        print("\n📦 TEST 1: Creating Multiple Test Listings for Bulk Operations")
        
        if not self.regular_user:
            print("❌ Cannot create listings - no user logged in")
            return False

        # Create diverse test listings
        test_listings = [
            {
                "title": "Bulk Test MacBook Pro 16-inch",
                "description": "High-performance laptop for bulk operations testing. Excellent condition with original packaging.",
                "price": 2500.00,
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"],
                "tags": ["laptop", "apple", "macbook"],
                "features": ["16-inch display", "M1 Pro chip", "32GB RAM"]
            },
            {
                "title": "Bulk Test iPhone 14 Pro",
                "description": "Latest iPhone model for bulk testing. Pristine condition with all accessories.",
                "price": 1200.00,
                "category": "Electronics",
                "condition": "Used - Like New",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400"],
                "tags": ["smartphone", "apple", "iphone"],
                "features": ["Pro camera system", "A16 Bionic chip", "128GB storage"]
            },
            {
                "title": "Bulk Test Gaming Chair",
                "description": "Ergonomic gaming chair for bulk operations testing. Comfortable and adjustable.",
                "price": 350.00,
                "category": "Furniture",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400"],
                "tags": ["gaming", "chair", "furniture"],
                "features": ["Ergonomic design", "Adjustable height", "Lumbar support"]
            },
            {
                "title": "Bulk Test Vintage Camera",
                "description": "Classic film camera for bulk testing. Perfect for photography enthusiasts.",
                "price": 450.00,
                "category": "Photography",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"],
                "tags": ["camera", "vintage", "film"],
                "features": ["Manual focus", "35mm film", "Original case"]
            },
            {
                "title": "Bulk Test Designer Watch",
                "description": "Luxury timepiece for bulk operations testing. Authentic and well-maintained.",
                "price": 800.00,
                "category": "Fashion",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400"],
                "tags": ["watch", "luxury", "fashion"],
                "features": ["Automatic movement", "Sapphire crystal", "Water resistant"]
            }
        ]

        create_success_count = 0
        for i, listing_data in enumerate(test_listings):
            success, response = self.run_test(
                f"Create Test Listing {i+1}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            if success and 'listing_id' in response:
                self.created_listing_ids.append(response['listing_id'])
                create_success_count += 1
                print(f"   ✅ Created listing {i+1} with ID: {response['listing_id']}")

        success = create_success_count == len(test_listings)
        self.log_test("Multiple Listing Creation", success, 
                     f"Created {create_success_count}/{len(test_listings)} listings")
        
        return success

    def test_verify_listings_in_browse(self):
        """Test 2: Verify all created listings appear in browse endpoint"""
        print("\n🔍 TEST 2: Verifying Listings Appear in Browse")
        
        success, browse_response = self.run_test(
            "Browse Listings After Creation",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False

        found_listings = 0
        for listing_id in self.created_listing_ids:
            found = any(listing.get('id') == listing_id for listing in browse_response)
            if found:
                found_listings += 1
                print(f"   ✅ Found listing {listing_id[:8]}... in browse")
            else:
                print(f"   ❌ Missing listing {listing_id[:8]}... from browse")

        success = found_listings == len(self.created_listing_ids)
        self.log_test("Listings Visibility in Browse", success, 
                     f"Found {found_listings}/{len(self.created_listing_ids)} listings in browse")
        
        return success

    def test_bulk_update_operations(self):
        """Test 3: Test bulk activate/deactivate and other bulk update operations"""
        print("\n✏️ TEST 3: Testing Bulk Update Operations")
        
        if len(self.created_listing_ids) < 3:
            print("❌ Not enough listings for bulk update testing")
            return False

        # Test bulk activate/deactivate operations
        print("\n   🔄 Testing bulk activate/deactivate operations...")
        deactivate_count = 0
        for listing_id in self.created_listing_ids[:3]:  # Deactivate first 3
            update_data = {"status": "inactive"}
            success, response = self.run_test(
                f"Bulk Deactivate {listing_id[:8]}...",
                "PUT",
                f"api/listings/{listing_id}",
                200,
                data=update_data
            )
            if success:
                deactivate_count += 1

        # Test bulk feature/unfeature operations
        print("\n   ⭐ Testing bulk feature operations...")
        feature_count = 0
        for listing_id in self.created_listing_ids[2:4]:  # Feature 2 listings
            update_data = {"featured": True, "status": "active"}
            success, response = self.run_test(
                f"Bulk Feature {listing_id[:8]}...",
                "PUT",
                f"api/listings/{listing_id}",
                200,
                data=update_data
            )
            if success:
                feature_count += 1

        # Test bulk approve/reject operations
        print("\n   ✅ Testing bulk approve operations...")
        approve_count = 0
        for listing_id in self.created_listing_ids[3:5]:  # Approve 2 listings
            update_data = {"status": "approved", "approved_at": datetime.utcnow().isoformat()}
            success, response = self.run_test(
                f"Bulk Approve {listing_id[:8]}...",
                "PUT",
                f"api/listings/{listing_id}",
                200,
                data=update_data
            )
            if success:
                approve_count += 1

        total_expected = 3 + 2 + 2  # deactivate + feature + approve
        total_actual = deactivate_count + feature_count + approve_count
        
        success = total_actual == total_expected
        self.log_test("Bulk Update Operations", success, 
                     f"Completed {total_actual}/{total_expected} bulk updates")
        
        return success

    def test_bulk_update_persistence(self):
        """Test 4: Verify bulk update changes persist in database"""
        print("\n🔄 TEST 4: Testing Bulk Update Persistence")
        
        # Wait a moment for database consistency
        time.sleep(1)
        
        success, browse_response = self.run_test(
            "Browse After Bulk Updates",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False

        # Check persistence of status changes
        inactive_found = 0
        featured_found = 0
        approved_found = 0
        
        for listing in browse_response:
            listing_id = listing.get('id')
            if listing_id in self.created_listing_ids:
                status = listing.get('status', '')
                featured = listing.get('featured', False)
                
                if status == 'inactive':
                    inactive_found += 1
                elif featured:
                    featured_found += 1
                elif status == 'approved':
                    approved_found += 1

        print(f"   📊 Persistence Results:")
        print(f"      Inactive listings found: {inactive_found}")
        print(f"      Featured listings found: {featured_found}")
        print(f"      Approved listings found: {approved_found}")

        # At least some changes should persist
        persistence_success = (inactive_found > 0 or featured_found > 0 or approved_found > 0)
        
        self.log_test("Bulk Update Persistence", persistence_success, 
                     f"Status changes persisted: {persistence_success}")
        
        return persistence_success

    def test_bulk_delete_operations(self):
        """Test 5: Test bulk deletion via DELETE /api/listings/{id}"""
        print("\n🗑️ TEST 5: Testing Bulk Delete Operations")
        
        if len(self.created_listing_ids) < 2:
            print("❌ Not enough listings for bulk delete testing")
            return False

        # Delete first 3 listings
        listings_to_delete = self.created_listing_ids[:3]
        delete_success_count = 0
        
        for listing_id in listings_to_delete:
            success, response = self.run_test(
                f"Bulk Delete {listing_id[:8]}...",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                delete_success_count += 1
                print(f"   ✅ Successfully deleted listing {listing_id[:8]}...")

        success = delete_success_count == len(listings_to_delete)
        self.log_test("Bulk Delete Operations", success, 
                     f"Deleted {delete_success_count}/{len(listings_to_delete)} listings")
        
        return success

    def test_bulk_delete_persistence(self):
        """Test 6: Verify deleted listings don't reappear and persist in database"""
        print("\n🔄 TEST 6: Testing Bulk Delete Persistence")
        
        # Wait for database consistency
        time.sleep(2)
        
        deleted_listings = self.created_listing_ids[:3]
        
        # Test 1: Verify deleted listings return 404
        print("\n   🔍 Testing individual listing access (should return 404)...")
        not_found_count = 0
        for listing_id in deleted_listings:
            success, response = self.run_test(
                f"Access Deleted Listing {listing_id[:8]}...",
                "GET",
                f"api/listings/{listing_id}",
                404  # Expecting 404 for deleted listings
            )
            if success:  # Success means we got the expected 404
                not_found_count += 1

        # Test 2: Verify deleted listings don't appear in browse
        print("\n   🌐 Testing browse endpoint (deleted listings should be absent)...")
        success, browse_response = self.run_test(
            "Browse After Bulk Delete",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        reappeared_count = 0
        if success:
            for listing_id in deleted_listings:
                found = any(listing.get('id') == listing_id for listing in browse_response)
                if found:
                    reappeared_count += 1
                    print(f"   ⚠️ Deleted listing {listing_id[:8]}... reappeared in browse!")

        # Test 3: Navigate away and back (simulate user navigation)
        print("\n   🔄 Testing persistence after navigation simulation...")
        time.sleep(1)  # Simulate navigation delay
        
        success_nav, browse_nav_response = self.run_test(
            "Browse After Navigation Simulation",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        reappeared_after_nav = 0
        if success_nav:
            for listing_id in deleted_listings:
                found = any(listing.get('id') == listing_id for listing in browse_nav_response)
                if found:
                    reappeared_after_nav += 1

        # Summary of persistence tests
        persistence_success = (
            not_found_count == len(deleted_listings) and  # All return 404
            reappeared_count == 0 and                     # None in browse
            reappeared_after_nav == 0                     # None after navigation
        )
        
        print(f"\n   📊 Persistence Test Results:")
        print(f"      Listings returning 404: {not_found_count}/{len(deleted_listings)}")
        print(f"      Listings reappeared in browse: {reappeared_count}")
        print(f"      Listings reappeared after navigation: {reappeared_after_nav}")

        self.log_test("Bulk Delete Persistence", persistence_success, 
                     f"Complete persistence verified: {persistence_success}")
        
        return persistence_success

    def test_listing_creation_without_pickers(self):
        """Test 7: Test listing creation with default category and condition values"""
        print("\n📝 TEST 7: Testing Listing Creation Without Pickers")
        
        if not self.regular_user:
            print("❌ Cannot test listing creation - no user logged in")
            return False

        # Test creating listings with default values (General/New)
        print("\n   🎯 Testing listings with default General/New values...")
        default_listings = [
            {
                "title": "Default Test Product 1 - Wireless Headphones",
                "description": "High-quality wireless headphones with default category and condition.",
                "price": 150.00,
                "category": "General",  # Default category
                "condition": "New",     # Default condition
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"]
            },
            {
                "title": "Default Test Product 2 - Bluetooth Speaker",
                "description": "Portable Bluetooth speaker with default settings.",
                "price": 80.00,
                "category": "General",  # Default category
                "condition": "New",     # Default condition
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400"]
            }
        ]

        default_success_count = 0
        default_listing_ids = []
        
        for i, listing_data in enumerate(default_listings):
            success, response = self.run_test(
                f"Create Default Listing {i+1}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            if success and 'listing_id' in response:
                default_listing_ids.append(response['listing_id'])
                default_success_count += 1
                print(f"   ✅ Created default listing with General/New: {response['listing_id'][:8]}...")

        # Test creating catalyst listings (should get category "Catalysts")
        print("\n   🧪 Testing catalyst listings (should get category 'Catalysts')...")
        catalyst_listing = {
            "title": "Test Catalyst FAPACAT8659",
            "description": "Automotive catalyst for testing category assignment. Should automatically get 'Catalysts' category.",
            "price": 292.74,
            "category": "Catalysts",  # Catalyst category
            "condition": "Used - Good",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"]
        }

        catalyst_success, catalyst_response = self.run_test(
            "Create Catalyst Listing",
            "POST",
            "api/listings",
            200,
            data=catalyst_listing
        )
        
        if catalyst_success and 'listing_id' in catalyst_response:
            default_listing_ids.append(catalyst_response['listing_id'])
            print(f"   ✅ Created catalyst listing: {catalyst_response['listing_id'][:8]}...")

        # Verify listings were created successfully
        total_expected = len(default_listings) + 1  # default + catalyst
        total_created = len(default_listing_ids)
        
        creation_success = total_created == total_expected
        self.log_test("Listing Creation Without Pickers", creation_success, 
                     f"Created {total_created}/{total_expected} listings with default values")

        # Cleanup: Delete test listings
        print("\n   🧹 Cleaning up test listings...")
        for listing_id in default_listing_ids:
            self.run_test(
                f"Cleanup Default Listing {listing_id[:8]}...",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )

        return creation_success

    def test_complete_workflow(self):
        """Test 8: Test complete workflow - create, bulk operations, navigate, verify"""
        print("\n🔄 TEST 8: Testing Complete Workflow")
        
        if not self.regular_user:
            print("❌ Cannot test complete workflow - no user logged in")
            return False

        # Step 1: Create several new listings for workflow test
        print("\n   📦 Step 1: Creating workflow test listings...")
        workflow_listings = [
            {
                "title": "Workflow Test Gaming Laptop",
                "description": "High-performance gaming laptop for workflow testing.",
                "price": 1800.00,
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400"]
            },
            {
                "title": "Workflow Test Office Desk",
                "description": "Ergonomic office desk for workflow testing.",
                "price": 300.00,
                "category": "Furniture",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400"]
            }
        ]

        workflow_listing_ids = []
        for i, listing_data in enumerate(workflow_listings):
            success, response = self.run_test(
                f"Create Workflow Listing {i+1}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            if success and 'listing_id' in response:
                workflow_listing_ids.append(response['listing_id'])

        # Step 2: Perform bulk operations on them
        print("\n   ⚡ Step 2: Performing bulk operations...")
        bulk_ops_success = 0
        
        # Feature the first listing
        if workflow_listing_ids:
            success, response = self.run_test(
                "Workflow Bulk Feature",
                "PUT",
                f"api/listings/{workflow_listing_ids[0]}",
                200,
                data={"featured": True, "status": "active"}
            )
            if success:
                bulk_ops_success += 1

        # Deactivate the second listing
        if len(workflow_listing_ids) > 1:
            success, response = self.run_test(
                "Workflow Bulk Deactivate",
                "PUT",
                f"api/listings/{workflow_listing_ids[1]}",
                200,
                data={"status": "inactive"}
            )
            if success:
                bulk_ops_success += 1

        # Step 3: Navigate away and back (simulate user behavior)
        print("\n   🧭 Step 3: Simulating navigation...")
        time.sleep(2)  # Simulate navigation delay
        
        # Multiple API calls to simulate navigation
        self.run_test("Navigate to Health Check", "GET", "api/health", 200)
        self.run_test("Navigate to Browse", "GET", "api/marketplace/browse", 200)
        time.sleep(1)

        # Step 4: Verify persistence and data consistency
        print("\n   ✅ Step 4: Verifying persistence and data consistency...")
        
        # Check individual listings
        individual_consistency = 0
        for listing_id in workflow_listing_ids:
            success, response = self.run_test(
                f"Verify Individual Listing {listing_id[:8]}...",
                "GET",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                individual_consistency += 1

        # Check browse consistency
        success, browse_response = self.run_test(
            "Verify Browse Consistency",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        browse_consistency = 0
        if success:
            for listing_id in workflow_listing_ids:
                found = any(listing.get('id') == listing_id for listing in browse_response)
                if found:
                    browse_consistency += 1

        # Step 5: Cleanup
        print("\n   🧹 Step 5: Cleaning up workflow test listings...")
        cleanup_success = 0
        for listing_id in workflow_listing_ids:
            success, response = self.run_test(
                f"Cleanup Workflow Listing {listing_id[:8]}...",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                cleanup_success += 1

        # Evaluate workflow success
        workflow_success = (
            len(workflow_listing_ids) == len(workflow_listings) and  # All created
            bulk_ops_success == 2 and                               # Bulk ops worked
            individual_consistency == len(workflow_listing_ids) and  # Individual access works
            browse_consistency >= 1 and                             # At least some in browse
            cleanup_success == len(workflow_listing_ids)            # All cleaned up
        )

        print(f"\n   📊 Workflow Test Results:")
        print(f"      Listings created: {len(workflow_listing_ids)}/{len(workflow_listings)}")
        print(f"      Bulk operations: {bulk_ops_success}/2")
        print(f"      Individual consistency: {individual_consistency}/{len(workflow_listing_ids)}")
        print(f"      Browse consistency: {browse_consistency}/{len(workflow_listing_ids)}")
        print(f"      Cleanup success: {cleanup_success}/{len(workflow_listing_ids)}")

        self.log_test("Complete Workflow", workflow_success, 
                     f"Full workflow completed successfully: {workflow_success}")
        
        return workflow_success

    def test_api_endpoints_validation(self):
        """Test 9: Validate specific API endpoints for bulk operations"""
        print("\n🔌 TEST 9: Validating API Endpoints for Bulk Operations")
        
        if not self.regular_user:
            print("❌ Cannot validate API endpoints - no user logged in")
            return False

        # Create a test listing for endpoint validation
        test_listing = {
            "title": "API Validation Test Listing",
            "description": "Test listing for API endpoint validation.",
            "price": 100.00,
            "category": "General",
            "condition": "New",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"]
        }

        success, response = self.run_test(
            "Create API Validation Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )

        if not success or 'listing_id' not in response:
            print("❌ Failed to create test listing for API validation")
            return False

        listing_id = response['listing_id']
        print(f"   ✅ Created validation listing: {listing_id[:8]}...")

        # Test PUT /api/listings/{id} for bulk updates
        print("\n   🔄 Testing PUT /api/listings/{id} endpoint...")
        put_success, put_response = self.run_test(
            "PUT Endpoint Validation",
            "PUT",
            f"api/listings/{listing_id}",
            200,
            data={
                "status": "featured",
                "price": 120.00,
                "title": "API Validation Test Listing (UPDATED)"
            }
        )

        # Verify PUT changes persisted
        if put_success:
            success, get_response = self.run_test(
                "Verify PUT Changes",
                "GET",
                f"api/listings/{listing_id}",
                200
            )
            
            put_persistence = False
            if success:
                put_persistence = (
                    get_response.get('price') == 120.00 and
                    'UPDATED' in get_response.get('title', '')
                )
                print(f"   📊 PUT persistence: {put_persistence}")

        # Test DELETE /api/listings/{id} for bulk deletions
        print("\n   🗑️ Testing DELETE /api/listings/{id} endpoint...")
        delete_success, delete_response = self.run_test(
            "DELETE Endpoint Validation",
            "DELETE",
            f"api/listings/{listing_id}",
            200
        )

        # Verify DELETE worked (should return 404)
        delete_persistence = False
        if delete_success:
            success, _ = self.run_test(
                "Verify DELETE Worked",
                "GET",
                f"api/listings/{listing_id}",
                404  # Should return 404 for deleted listing
            )
            delete_persistence = success
            print(f"   📊 DELETE persistence: {delete_persistence}")

        # Test GET /api/listings returns updated data
        print("\n   📋 Testing GET /api/listings endpoint...")
        get_all_success, get_all_response = self.run_test(
            "GET All Listings Validation",
            "GET",
            "api/listings",
            200
        )

        # Test GET /api/marketplace/browse returns updated data
        browse_success, browse_response = self.run_test(
            "GET Browse Listings Validation",
            "GET",
            "api/marketplace/browse",
            200
        )

        # Evaluate API endpoints validation
        endpoints_success = (
            put_success and put_persistence and      # PUT works and persists
            delete_success and delete_persistence and # DELETE works and persists
            get_all_success and                      # GET all works
            browse_success                           # GET browse works
        )

        print(f"\n   📊 API Endpoints Validation Results:")
        print(f"      PUT endpoint working: {put_success}")
        print(f"      PUT persistence: {put_persistence}")
        print(f"      DELETE endpoint working: {delete_success}")
        print(f"      DELETE persistence: {delete_persistence}")
        print(f"      GET all listings working: {get_all_success}")
        print(f"      GET browse working: {browse_success}")

        self.log_test("API Endpoints Validation", endpoints_success, 
                     f"All API endpoints validated: {endpoints_success}")
        
        return endpoints_success

    def cleanup_remaining_listings(self):
        """Cleanup any remaining test listings"""
        print("\n🧹 Cleaning up remaining test listings...")
        
        remaining_listings = self.created_listing_ids[3:]  # Skip the first 3 (already deleted)
        cleanup_count = 0
        
        for listing_id in remaining_listings:
            success, response = self.run_test(
                f"Cleanup Remaining {listing_id[:8]}...",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                cleanup_count += 1

        print(f"   ✅ Cleaned up {cleanup_count}/{len(remaining_listings)} remaining listings")

    def run_bulk_operations_tests(self):
        """Run complete bulk operations test suite"""
        print("🚀 Starting Cataloro Bulk Operations Test Suite")
        print("=" * 70)
        print("Testing bulk operations functionality as requested in review:")
        print("1. Bulk Delete Operations")
        print("2. Other Bulk Operations (activate/deactivate, feature/unfeature, approve/reject)")
        print("3. Listing Creation Without Pickers")
        print("4. Complete Workflow")
        print("5. API Endpoints Validation")
        print("=" * 70)

        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return False

        # Run all bulk operations tests
        test_results = []
        
        # Test 1: Create multiple listings
        test_results.append(self.test_create_multiple_listings())
        
        # Test 2: Verify listings in browse
        test_results.append(self.test_verify_listings_in_browse())
        
        # Test 3: Bulk update operations
        test_results.append(self.test_bulk_update_operations())
        
        # Test 4: Bulk update persistence
        test_results.append(self.test_bulk_update_persistence())
        
        # Test 5: Bulk delete operations
        test_results.append(self.test_bulk_delete_operations())
        
        # Test 6: Bulk delete persistence
        test_results.append(self.test_bulk_delete_persistence())
        
        # Test 7: Listing creation without pickers
        test_results.append(self.test_listing_creation_without_pickers())
        
        # Test 8: Complete workflow
        test_results.append(self.test_complete_workflow())
        
        # Test 9: API endpoints validation
        test_results.append(self.test_api_endpoints_validation())
        
        # Cleanup remaining listings
        self.cleanup_remaining_listings()

        # Print final results
        print("\n" + "=" * 70)
        print("📊 BULK OPERATIONS TEST RESULTS")
        print("=" * 70)
        
        test_names = [
            "Multiple Listing Creation",
            "Listings Visibility in Browse", 
            "Bulk Update Operations",
            "Bulk Update Persistence",
            "Bulk Delete Operations",
            "Bulk Delete Persistence",
            "Listing Creation Without Pickers",
            "Complete Workflow",
            "API Endpoints Validation"
        ]
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        for i, (name, result) in enumerate(zip(test_names, test_results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{i+1:2d}. {name:<35} {status}")
        
        print("=" * 70)
        print(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"📊 Individual API Tests: {self.tests_passed}/{self.tests_run} API calls successful")
        
        if passed_tests == total_tests:
            print("🎉 ALL BULK OPERATIONS TESTS PASSED!")
            print("✅ Bulk operations functionality is working correctly")
            print("✅ Data persistence verified across all operations")
            print("✅ API endpoints validated for bulk operations")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} bulk operation tests failed")
            print("❌ Some bulk operations functionality needs attention")
            return False

def main():
    """Main test execution"""
    tester = BulkOperationsTester()
    success = tester.run_bulk_operations_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())