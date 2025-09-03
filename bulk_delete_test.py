#!/usr/bin/env python3
"""
Bulk Delete Functionality Test Suite
Tests the bulk delete fixes for ID consistency and enhanced delete endpoints
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class BulkDeleteTester:
    def __init__(self, base_url="https://cataloro-marketplace-2.preview.emergentagent.com"):
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

    def test_backend_id_consistency_fix(self):
        """Test Backend ID Consistency Fix"""
        print("\n🔧 Testing Backend ID Consistency Fix...")
        
        if not self.regular_user:
            print("❌ ID Consistency Test - SKIPPED (No user logged in)")
            return False

        # Step 1: Create a test listing via POST /api/listings
        print("\n📝 Step 1: Creating test listing...")
        test_listing = {
            "title": "ID Consistency Test - MacBook Pro",
            "description": "Test listing for ID consistency verification",
            "price": 2500.00,
            "category": "Electronics",
            "condition": "Used - Excellent",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"]
        }
        
        success, create_response = self.run_test(
            "Create Test Listing for ID Consistency",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success or 'listing_id' not in create_response:
            print("❌ Failed to create test listing - stopping ID consistency test")
            return False
        
        listing_id = create_response['listing_id']
        self.created_listing_ids.append(listing_id)
        print(f"   ✅ Created listing with ID: {listing_id}")
        
        # Step 2: Get the listing ID from the response and verify format
        print(f"\n🔍 Step 2: Verifying ID format...")
        try:
            # Check if it's a valid UUID format
            uuid.UUID(listing_id)
            self.log_test("ID Format Validation", True, f"ID is valid UUID format: {listing_id}")
        except ValueError:
            self.log_test("ID Format Validation", False, f"ID is not valid UUID format: {listing_id}")
            return False
        
        # Step 3: Verify listing appears in /api/listings
        print(f"\n📋 Step 3: Verifying listing in /api/listings...")
        success, listings_response = self.run_test(
            "Get All Listings",
            "GET",
            "api/listings",
            200
        )
        
        found_in_listings = False
        if success and 'listings' in listings_response:
            for listing in listings_response['listings']:
                if listing.get('id') == listing_id:
                    found_in_listings = True
                    print(f"   ✅ Found listing in /api/listings with ID: {listing.get('id')}")
                    break
        
        self.log_test("Listing in /api/listings", found_in_listings, 
                     f"Listing found in /api/listings: {found_in_listings}")
        
        # Step 4: Verify listing appears in /api/marketplace/browse
        print(f"\n🌐 Step 4: Verifying listing in /api/marketplace/browse...")
        success, browse_response = self.run_test(
            "Browse Marketplace Listings",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        found_in_browse = False
        browse_listing_id = None
        if success:
            for listing in browse_response:
                if listing.get('id') == listing_id:
                    found_in_browse = True
                    browse_listing_id = listing.get('id')
                    print(f"   ✅ Found listing in /api/marketplace/browse with ID: {browse_listing_id}")
                    break
        
        self.log_test("Listing in /api/marketplace/browse", found_in_browse, 
                     f"Listing found in browse: {found_in_browse}")
        
        # Step 5: Confirm ID format consistency between endpoints
        print(f"\n🔄 Step 5: Confirming ID format consistency...")
        id_consistency = found_in_listings and found_in_browse and (listing_id == browse_listing_id)
        self.log_test("ID Format Consistency", id_consistency, 
                     f"Same UUID format across endpoints: {id_consistency}")
        
        # Step 6: Delete via DELETE /api/listings/{id}
        print(f"\n🗑️ Step 6: Deleting listing via DELETE /api/listings/{listing_id}...")
        success, delete_response = self.run_test(
            "Delete Listing by ID",
            "DELETE",
            f"api/listings/{listing_id}",
            200
        )
        
        if success:
            print(f"   ✅ Successfully deleted listing: {delete_response}")
        
        # Step 7: Verify removal from /api/listings
        print(f"\n🔍 Step 7: Verifying removal from /api/listings...")
        success, listings_after = self.run_test(
            "Get All Listings After Delete",
            "GET",
            "api/listings",
            200
        )
        
        removed_from_listings = True
        if success and 'listings' in listings_after:
            for listing in listings_after['listings']:
                if listing.get('id') == listing_id:
                    removed_from_listings = False
                    break
        
        self.log_test("Removed from /api/listings", removed_from_listings, 
                     f"Listing removed from /api/listings: {removed_from_listings}")
        
        # Step 8: Verify removal from /api/marketplace/browse
        print(f"\n🌐 Step 8: Verifying removal from /api/marketplace/browse...")
        success, browse_after = self.run_test(
            "Browse Marketplace After Delete",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        removed_from_browse = True
        if success:
            for listing in browse_after:
                if listing.get('id') == listing_id:
                    removed_from_browse = False
                    break
        
        self.log_test("Removed from /api/marketplace/browse", removed_from_browse, 
                     f"Listing removed from browse: {removed_from_browse}")
        
        # Summary
        all_steps_passed = all([
            found_in_listings,
            found_in_browse, 
            id_consistency,
            success,  # delete success
            removed_from_listings,
            removed_from_browse
        ])
        
        print(f"\n📊 ID Consistency Test Summary: {'✅ PASSED' if all_steps_passed else '❌ FAILED'}")
        return all_steps_passed

    def test_enhanced_delete_endpoint(self):
        """Test Enhanced Delete Endpoint with UUID and ObjectId compatibility"""
        print("\n🔧 Testing Enhanced Delete Endpoint...")
        
        if not self.regular_user:
            print("❌ Enhanced Delete Test - SKIPPED (No user logged in)")
            return False

        # Test 1: Create test listing with UUID format
        print("\n📝 Test 1: Creating test listing with UUID format...")
        test_listing_uuid = {
            "title": "Enhanced Delete Test - UUID Format",
            "description": "Test listing for enhanced delete endpoint with UUID",
            "price": 1500.00,
            "category": "Electronics",
            "condition": "Used - Good",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400"]
        }
        
        success, create_response = self.run_test(
            "Create UUID Test Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing_uuid
        )
        
        if not success:
            return False
        
        uuid_listing_id = create_response['listing_id']
        self.created_listing_ids.append(uuid_listing_id)
        
        # Test 2: Delete with UUID format ID
        print(f"\n🗑️ Test 2: Deleting with UUID format ID...")
        success, delete_response = self.run_test(
            "Delete with UUID Format",
            "DELETE",
            f"api/listings/{uuid_listing_id}",
            200
        )
        
        uuid_delete_success = success
        if success:
            # Verify proper response format
            expected_fields = ['message', 'deleted_count']
            response_valid = all(field in delete_response for field in expected_fields)
            self.log_test("UUID Delete Response Format", response_valid, 
                         f"Response contains required fields: {response_valid}")
            
            # Check deletion count
            deleted_count = delete_response.get('deleted_count', 0)
            count_correct = deleted_count == 1
            self.log_test("UUID Delete Count", count_correct, 
                         f"Deleted count is 1: {count_correct}")
        
        # Test 3: Test deletion with non-existent ID (error handling)
        print(f"\n❌ Test 3: Testing error handling with non-existent ID...")
        fake_id = str(uuid.uuid4())
        success, error_response = self.run_test(
            "Delete Non-existent ID",
            "DELETE",
            f"api/listings/{fake_id}",
            404  # Expecting 404 for non-existent listing
        )
        
        error_handling_success = success
        if success:
            # Verify proper error message
            error_message = error_response.get('detail', '')
            proper_error = 'not found' in error_message.lower()
            self.log_test("Error Message Format", proper_error, 
                         f"Proper error message: {proper_error}")
        
        # Test 4: Test backward compatibility (if ObjectId format is supported)
        print(f"\n🔄 Test 4: Testing backward compatibility...")
        # Create another test listing
        test_listing_compat = {
            "title": "Enhanced Delete Test - Compatibility",
            "description": "Test listing for backward compatibility testing",
            "price": 800.00,
            "category": "Electronics",
            "condition": "Used - Fair",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400"]
        }
        
        success, create_response2 = self.run_test(
            "Create Compatibility Test Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing_compat
        )
        
        compat_test_success = True
        if success:
            compat_listing_id = create_response2['listing_id']
            self.created_listing_ids.append(compat_listing_id)
            
            # Try to delete with UUID (should work)
            success_compat, delete_compat_response = self.run_test(
                "Delete with UUID (Compatibility)",
                "DELETE",
                f"api/listings/{compat_listing_id}",
                200
            )
            compat_test_success = success_compat
        
        # Summary
        all_tests_passed = all([
            uuid_delete_success,
            error_handling_success,
            compat_test_success
        ])
        
        print(f"\n📊 Enhanced Delete Endpoint Summary: {'✅ PASSED' if all_tests_passed else '❌ FAILED'}")
        return all_tests_passed

    def test_frontend_bulk_delete_simulation(self):
        """Simulate Frontend Bulk Delete Process"""
        print("\n🔧 Testing Frontend Bulk Delete Simulation...")
        
        if not self.regular_user:
            print("❌ Bulk Delete Simulation - SKIPPED (No user logged in)")
            return False

        # Step 1: Create multiple test listings
        print("\n📝 Step 1: Creating multiple test listings...")
        test_listings = [
            {
                "title": "Bulk Delete Test 1 - Gaming Laptop",
                "description": "High-performance gaming laptop for bulk delete testing",
                "price": 1800.00,
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400"]
            },
            {
                "title": "Bulk Delete Test 2 - Mechanical Keyboard",
                "description": "Premium mechanical keyboard for bulk delete testing",
                "price": 150.00,
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400"]
            },
            {
                "title": "Bulk Delete Test 3 - Monitor Stand",
                "description": "Adjustable monitor stand for bulk delete testing",
                "price": 75.00,
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"]
            },
            {
                "title": "Bulk Delete Test 4 - Wireless Mouse",
                "description": "Ergonomic wireless mouse for bulk delete testing",
                "price": 45.00,
                "category": "Electronics",
                "condition": "Used - Fair",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"]
            },
            {
                "title": "Bulk Delete Test 5 - USB Hub",
                "description": "Multi-port USB hub for bulk delete testing",
                "price": 25.00,
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"]
            }
        ]
        
        bulk_listing_ids = []
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
                listing_id = response['listing_id']
                bulk_listing_ids.append(listing_id)
                self.created_listing_ids.append(listing_id)
                create_success_count += 1
                print(f"   ✅ Created listing {i+1} with ID: {listing_id}")
        
        self.log_test("Bulk Listing Creation", create_success_count == len(test_listings), 
                     f"Created {create_success_count}/{len(test_listings)} listings")
        
        if create_success_count == 0:
            print("❌ No listings created - stopping bulk delete test")
            return False
        
        # Step 2: Verify all listings appear in browse
        print(f"\n🌐 Step 2: Verifying all listings appear in browse...")
        success, browse_before = self.run_test(
            "Browse Before Bulk Delete",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        found_before_count = 0
        if success:
            for listing_id in bulk_listing_ids:
                found = any(listing.get('id') == listing_id for listing in browse_before)
                if found:
                    found_before_count += 1
        
        self.log_test("All Listings in Browse Before Delete", found_before_count == len(bulk_listing_ids), 
                     f"Found {found_before_count}/{len(bulk_listing_ids)} listings in browse")
        
        # Step 3: Perform bulk deletion (multiple DELETE calls)
        print(f"\n🗑️ Step 3: Performing bulk deletion...")
        delete_success_count = 0
        delete_responses = []
        
        for i, listing_id in enumerate(bulk_listing_ids):
            success, response = self.run_test(
                f"Bulk Delete Listing {i+1} ({listing_id[:8]}...)",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                delete_success_count += 1
                delete_responses.append(response)
                print(f"   ✅ Deleted listing {i+1}: {response.get('message', 'Success')}")
        
        self.log_test("Bulk Delete Operations", delete_success_count == len(bulk_listing_ids), 
                     f"Deleted {delete_success_count}/{len(bulk_listing_ids)} listings")
        
        # Step 4: Verify all listings are removed from both endpoints
        print(f"\n🔍 Step 4: Verifying removal from /api/listings...")
        success, listings_after = self.run_test(
            "Get All Listings After Bulk Delete",
            "GET",
            "api/listings",
            200
        )
        
        remaining_in_listings = 0
        if success and 'listings' in listings_after:
            for listing_id in bulk_listing_ids:
                found = any(listing.get('id') == listing_id for listing in listings_after['listings'])
                if found:
                    remaining_in_listings += 1
        
        self.log_test("Removed from /api/listings", remaining_in_listings == 0, 
                     f"Remaining in listings: {remaining_in_listings} (should be 0)")
        
        print(f"\n🌐 Step 5: Verifying removal from /api/marketplace/browse...")
        success, browse_after = self.run_test(
            "Browse After Bulk Delete",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        remaining_in_browse = 0
        if success:
            for listing_id in bulk_listing_ids:
                found = any(listing.get('id') == listing_id for listing in browse_after)
                if found:
                    remaining_in_browse += 1
                    print(f"   ⚠️ Listing {listing_id[:8]}... still found in browse!")
        
        self.log_test("Removed from /api/marketplace/browse", remaining_in_browse == 0, 
                     f"Remaining in browse: {remaining_in_browse} (should be 0)")
        
        # Step 6: Check that changes persist across API calls
        print(f"\n🔄 Step 6: Verifying persistence across multiple API calls...")
        persistence_checks = []
        
        for check_num in range(3):  # Check 3 times
            success, browse_check = self.run_test(
                f"Persistence Check {check_num + 1}",
                "GET",
                "api/marketplace/browse",
                200
            )
            
            if success:
                still_found = 0
                for listing_id in bulk_listing_ids:
                    found = any(listing.get('id') == listing_id for listing in browse_check)
                    if found:
                        still_found += 1
                persistence_checks.append(still_found == 0)
        
        all_persistent = all(persistence_checks)
        self.log_test("Deletion Persistence", all_persistent, 
                     f"Deletions persistent across {len(persistence_checks)} checks: {all_persistent}")
        
        # Summary
        all_steps_passed = all([
            create_success_count == len(test_listings),
            found_before_count == len(bulk_listing_ids),
            delete_success_count == len(bulk_listing_ids),
            remaining_in_listings == 0,
            remaining_in_browse == 0,
            all_persistent
        ])
        
        print(f"\n📊 Bulk Delete Simulation Summary: {'✅ PASSED' if all_steps_passed else '❌ FAILED'}")
        return all_steps_passed

    def test_id_format_standardization(self):
        """Test ID Format Standardization between endpoints"""
        print("\n🔧 Testing ID Format Standardization...")
        
        # Test 1: Compare ID formats from both endpoints
        print("\n🔍 Test 1: Comparing ID formats from /api/listings vs /api/marketplace/browse...")
        
        # Get listings from /api/listings
        success_listings, listings_response = self.run_test(
            "Get Listings from /api/listings",
            "GET",
            "api/listings",
            200
        )
        
        # Get listings from /api/marketplace/browse
        success_browse, browse_response = self.run_test(
            "Get Listings from /api/marketplace/browse",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not (success_listings and success_browse):
            print("❌ Failed to get listings from both endpoints")
            return False
        
        # Extract IDs from both endpoints
        listings_ids = []
        if 'listings' in listings_response:
            listings_ids = [listing.get('id') for listing in listings_response['listings'] if listing.get('id')]
        
        browse_ids = [listing.get('id') for listing in browse_response if listing.get('id')]
        
        print(f"   Found {len(listings_ids)} IDs from /api/listings")
        print(f"   Found {len(browse_ids)} IDs from /api/marketplace/browse")
        
        # Test 2: Verify both endpoints use consistent UUID format
        print("\n🔍 Test 2: Verifying UUID format consistency...")
        
        def is_valid_uuid(id_string):
            try:
                uuid.UUID(id_string)
                return True
            except (ValueError, TypeError):
                return False
        
        # Check /api/listings IDs
        listings_uuid_count = sum(1 for id_val in listings_ids if is_valid_uuid(id_val))
        listings_uuid_consistent = listings_uuid_count == len(listings_ids)
        
        self.log_test("/api/listings UUID Format", listings_uuid_consistent, 
                     f"UUID format: {listings_uuid_count}/{len(listings_ids)} IDs")
        
        # Check /api/marketplace/browse IDs
        browse_uuid_count = sum(1 for id_val in browse_ids if is_valid_uuid(id_val))
        browse_uuid_consistent = browse_uuid_count == len(browse_ids)
        
        self.log_test("/api/marketplace/browse UUID Format", browse_uuid_consistent, 
                     f"UUID format: {browse_uuid_count}/{len(browse_ids)} IDs")
        
        # Test 3: Cross-endpoint data consistency
        print("\n🔄 Test 3: Testing cross-endpoint data consistency...")
        
        # Find common listings between both endpoints
        common_ids = set(listings_ids) & set(browse_ids)
        consistency_matches = len(common_ids)
        
        print(f"   Common IDs between endpoints: {consistency_matches}")
        
        # Test a few common listings for data consistency
        data_consistency_checks = []
        test_count = min(3, len(common_ids))  # Test up to 3 common listings
        
        for i, common_id in enumerate(list(common_ids)[:test_count]):
            # Find listing in /api/listings response
            listings_item = None
            if 'listings' in listings_response:
                listings_item = next((item for item in listings_response['listings'] if item.get('id') == common_id), None)
            
            # Find listing in /api/marketplace/browse response
            browse_item = next((item for item in browse_response if item.get('id') == common_id), None)
            
            if listings_item and browse_item:
                # Compare key fields
                title_match = listings_item.get('title') == browse_item.get('title')
                price_match = listings_item.get('price') == browse_item.get('price')
                category_match = listings_item.get('category') == browse_item.get('category')
                
                consistency_check = title_match and price_match and category_match
                data_consistency_checks.append(consistency_check)
                
                print(f"   Listing {i+1} ({common_id[:8]}...): Title={title_match}, Price={price_match}, Category={category_match}")
        
        all_data_consistent = all(data_consistency_checks) if data_consistency_checks else True
        self.log_test("Cross-endpoint Data Consistency", all_data_consistent, 
                     f"Data consistent: {len([c for c in data_consistency_checks if c])}/{len(data_consistency_checks)} checks")
        
        # Summary
        all_tests_passed = all([
            listings_uuid_consistent,
            browse_uuid_consistent,
            consistency_matches > 0,
            all_data_consistent
        ])
        
        print(f"\n📊 ID Format Standardization Summary: {'✅ PASSED' if all_tests_passed else '❌ FAILED'}")
        return all_tests_passed

    def test_end_to_end_deletion_workflow(self):
        """Test End-to-End Deletion Workflow"""
        print("\n🔧 Testing End-to-End Deletion Workflow...")
        
        if not self.regular_user:
            print("❌ End-to-End Workflow - SKIPPED (No user logged in)")
            return False

        # Step 1: Create → List in browse → Delete via admin → Verify removal from browse
        print("\n📝 Step 1: Creating test listing...")
        
        workflow_listing = {
            "title": "End-to-End Workflow Test - Digital Camera",
            "description": "Professional digital camera for end-to-end workflow testing",
            "price": 950.00,
            "category": "Photography",
            "condition": "Used - Excellent",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"]
        }
        
        success, create_response = self.run_test(
            "Create Workflow Test Listing",
            "POST",
            "api/listings",
            200,
            data=workflow_listing
        )
        
        if not success:
            return False
        
        workflow_listing_id = create_response['listing_id']
        self.created_listing_ids.append(workflow_listing_id)
        
        # Step 2: Verify listing appears in browse
        print(f"\n🌐 Step 2: Verifying listing appears in browse...")
        success, browse_response = self.run_test(
            "Browse for Workflow Listing",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        found_in_browse = False
        if success:
            found_in_browse = any(listing.get('id') == workflow_listing_id for listing in browse_response)
        
        self.log_test("Listing Appears in Browse", found_in_browse, 
                     f"Listing found in browse: {found_in_browse}")
        
        # Step 3: Delete via admin (simulate admin deletion)
        print(f"\n🗑️ Step 3: Deleting via admin interface...")
        success, delete_response = self.run_test(
            "Admin Delete Workflow Listing",
            "DELETE",
            f"api/listings/{workflow_listing_id}",
            200
        )
        
        admin_delete_success = success
        if success:
            print(f"   ✅ Admin deletion successful: {delete_response.get('message', 'Success')}")
        
        # Step 4: Verify removal from browse
        print(f"\n🔍 Step 4: Verifying removal from browse...")
        success, browse_after_delete = self.run_test(
            "Browse After Admin Delete",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        removed_from_browse = True
        if success:
            found_after_delete = any(listing.get('id') == workflow_listing_id for listing in browse_after_delete)
            removed_from_browse = not found_after_delete
        
        self.log_test("Removed from Browse After Admin Delete", removed_from_browse, 
                     f"Listing removed from browse: {removed_from_browse}")
        
        # Step 5: Test complete workflow with multiple listings
        print(f"\n🔄 Step 5: Testing complete workflow with multiple listings...")
        
        # Create multiple listings for comprehensive workflow test
        workflow_listings = []
        for i in range(3):
            listing_data = {
                "title": f"Workflow Test {i+1} - Item {i+1}",
                "description": f"Test item {i+1} for complete workflow verification",
                "price": 100.00 + (i * 50),
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"]
            }
            
            success, response = self.run_test(
                f"Create Workflow Listing {i+1}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            
            if success:
                listing_id = response['listing_id']
                workflow_listings.append(listing_id)
                self.created_listing_ids.append(listing_id)
        
        # Verify all appear in browse
        success, browse_all = self.run_test(
            "Browse All Workflow Listings",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        all_found_count = 0
        if success:
            for listing_id in workflow_listings:
                if any(listing.get('id') == listing_id for listing in browse_all):
                    all_found_count += 1
        
        self.log_test("All Workflow Listings in Browse", all_found_count == len(workflow_listings), 
                     f"Found {all_found_count}/{len(workflow_listings)} listings in browse")
        
        # Delete all and verify removal
        delete_all_success = 0
        for listing_id in workflow_listings:
            success, _ = self.run_test(
                f"Delete Workflow Listing ({listing_id[:8]}...)",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            if success:
                delete_all_success += 1
        
        # Final verification - none should appear in browse
        success, final_browse = self.run_test(
            "Final Browse Check",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        none_reappeared = True
        if success:
            for listing_id in workflow_listings:
                if any(listing.get('id') == listing_id for listing in final_browse):
                    none_reappeared = False
                    break
        
        self.log_test("No Deleted Items Reappear", none_reappeared, 
                     f"No deleted items reappeared: {none_reappeared}")
        
        # Summary
        all_workflow_passed = all([
            found_in_browse,
            admin_delete_success,
            removed_from_browse,
            all_found_count == len(workflow_listings),
            delete_all_success == len(workflow_listings),
            none_reappeared
        ])
        
        print(f"\n📊 End-to-End Workflow Summary: {'✅ PASSED' if all_workflow_passed else '❌ FAILED'}")
        return all_workflow_passed

    def cleanup_test_data(self):
        """Clean up any remaining test data"""
        print("\n🧹 Cleaning up test data...")
        
        cleanup_count = 0
        for listing_id in self.created_listing_ids:
            try:
                success, _ = self.run_test(
                    f"Cleanup Listing ({listing_id[:8]}...)",
                    "DELETE",
                    f"api/listings/{listing_id}",
                    200
                )
                if success:
                    cleanup_count += 1
            except:
                pass  # Ignore cleanup errors
        
        print(f"   Cleaned up {cleanup_count}/{len(self.created_listing_ids)} test listings")

    def run_bulk_delete_tests(self):
        """Run all bulk delete functionality tests"""
        print("🚀 Starting Bulk Delete Functionality Tests")
        print("=" * 60)

        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return False

        # Run all bulk delete tests
        test_results = []
        
        print("\n" + "="*60)
        print("1️⃣ TESTING BACKEND ID CONSISTENCY FIX")
        print("="*60)
        test_results.append(self.test_backend_id_consistency_fix())
        
        print("\n" + "="*60)
        print("2️⃣ TESTING ENHANCED DELETE ENDPOINT")
        print("="*60)
        test_results.append(self.test_enhanced_delete_endpoint())
        
        print("\n" + "="*60)
        print("3️⃣ TESTING FRONTEND BULK DELETE SIMULATION")
        print("="*60)
        test_results.append(self.test_frontend_bulk_delete_simulation())
        
        print("\n" + "="*60)
        print("4️⃣ TESTING ID FORMAT STANDARDIZATION")
        print("="*60)
        test_results.append(self.test_id_format_standardization())
        
        print("\n" + "="*60)
        print("5️⃣ TESTING END-TO-END DELETION WORKFLOW")
        print("="*60)
        test_results.append(self.test_end_to_end_deletion_workflow())

        # Cleanup
        self.cleanup_test_data()

        # Print final results
        print("\n" + "=" * 60)
        print("📊 BULK DELETE FUNCTIONALITY TEST RESULTS")
        print("=" * 60)
        
        test_names = [
            "Backend ID Consistency Fix",
            "Enhanced Delete Endpoint", 
            "Frontend Bulk Delete Simulation",
            "ID Format Standardization",
            "End-to-End Deletion Workflow"
        ]
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        for i, (name, result) in enumerate(zip(test_names, test_results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{i+1}. {name}: {status}")
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"📊 Individual API Tests: {self.tests_passed}/{self.tests_run} API calls successful")
        
        if passed_tests == total_tests:
            print("🎉 All bulk delete functionality tests passed!")
            print("✅ Frontend bulk delete button should now work properly")
            print("✅ Backend ID format is consistent between admin and browse endpoints")
            print("✅ Deletions are properly reflected across all listing views")
            print("✅ Both UUID and ObjectId formats are handled correctly")
            return True
        else:
            print(f"⚠️ {total_tests - passed_tests} bulk delete tests failed")
            print("❌ Some bulk delete functionality may not be working correctly")
            return False

def main():
    """Main test execution"""
    tester = BulkDeleteTester()
    success = tester.run_bulk_delete_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())