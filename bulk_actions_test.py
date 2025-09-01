#!/usr/bin/env python3
"""
Focused test for bulk actions and add_info search functionality
As requested in the review
"""

import requests
import json
import time
from datetime import datetime

class BulkActionsAPITester:
    def __init__(self, base_url="https://trade-platform-30.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_user = None
        self.regular_user = None
        self.session = requests.Session()
        self.created_listings = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        if success:
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def api_call(self, method, endpoint, data=None, expected_status=200):
        """Make API call and return success, response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            success = response.status_code == expected_status
            if success and response.text:
                return True, response.json()
            elif success:
                return True, {}
            else:
                print(f"   API Error: {response.status_code} - {response.text[:200]}")
                return False, {}
                
        except Exception as e:
            print(f"   Exception: {str(e)}")
            return False, {}

    def setup_users(self):
        """Setup admin and regular users"""
        print("🔐 Setting up test users...")
        
        # Admin login
        success, response = self.api_call('POST', 'api/auth/login', {
            "email": "admin@cataloro.com", 
            "password": "demo123"
        })
        if success and 'user' in response:
            self.admin_user = response['user']
            print(f"   ✅ Admin user: {self.admin_user['email']}")
        
        # Regular user login
        success, response = self.api_call('POST', 'api/auth/login', {
            "email": "user@cataloro.com", 
            "password": "demo123"
        })
        if success and 'user' in response:
            self.regular_user = response['user']
            print(f"   ✅ Regular user: {self.regular_user['email']}")
        
        return self.admin_user is not None and self.regular_user is not None

    def test_bulk_listing_creation(self):
        """Test creating multiple listings for bulk operations"""
        print("\n📦 Testing Bulk Listing Creation...")
        
        if not self.regular_user:
            return self.log_test("Bulk Creation", False, "No regular user available")
        
        # Create 5 test listings
        test_listings = [
            {
                "title": f"Bulk Test Item {i+1} - Electronics",
                "description": f"Test listing {i+1} for bulk operations testing",
                "price": 100.00 + (i * 50),
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id'],
                "images": [f"https://images.unsplash.com/photo-{1500000000000 + i}?w=400"]
            }
            for i in range(5)
        ]
        
        created_count = 0
        for i, listing_data in enumerate(test_listings):
            success, response = self.api_call('POST', 'api/listings', listing_data)
            if success and 'listing_id' in response:
                self.created_listings.append(response['listing_id'])
                created_count += 1
                print(f"   ✅ Created listing {i+1}: {response['listing_id']}")
            else:
                print(f"   ❌ Failed to create listing {i+1}")
        
        return self.log_test("Bulk Listing Creation", created_count == 5, 
                           f"Created {created_count}/5 listings")

    def test_bulk_delete_operations(self):
        """Test bulk delete operations via DELETE /api/listings/{id}"""
        print("\n🗑️  Testing Bulk Delete Operations...")
        
        if len(self.created_listings) < 3:
            return self.log_test("Bulk Delete", False, "Not enough listings to test")
        
        # Delete first 3 listings
        delete_count = 0
        deleted_ids = []
        
        for listing_id in self.created_listings[:3]:
            success, response = self.api_call('DELETE', f'api/listings/{listing_id}')
            if success:
                delete_count += 1
                deleted_ids.append(listing_id)
                print(f"   ✅ Deleted listing: {listing_id}")
            else:
                print(f"   ❌ Failed to delete listing: {listing_id}")
        
        # Test persistence - verify deleted listings don't appear
        print("   🔍 Verifying deletion persistence...")
        success, browse_response = self.api_call('GET', 'api/marketplace/browse')
        
        if success:
            found_deleted = 0
            for listing in browse_response:
                if listing.get('id') in deleted_ids:
                    found_deleted += 1
                    print(f"   ⚠️  Deleted listing still appears: {listing.get('id')}")
            
            persistence_ok = found_deleted == 0
            print(f"   {'✅' if persistence_ok else '❌'} Persistence check: {found_deleted} deleted listings found (should be 0)")
        else:
            persistence_ok = False
        
        return self.log_test("Bulk Delete Operations", 
                           delete_count == 3 and persistence_ok,
                           f"Deleted {delete_count}/3 listings, persistence: {persistence_ok}")

    def test_bulk_update_operations(self):
        """Test bulk update operations via PUT /api/listings/{id}"""
        print("\n📝 Testing Bulk Update Operations...")
        
        remaining_listings = self.created_listings[3:]  # Use remaining listings after delete test
        if len(remaining_listings) < 2:
            return self.log_test("Bulk Update", False, "Not enough listings remaining")
        
        # Update status and price for remaining listings
        update_count = 0
        updated_ids = []
        
        for listing_id in remaining_listings:
            update_data = {
                "status": "featured",
                "price": 999.99,
                "title": f"UPDATED - Bulk Test Item"
            }
            
            success, response = self.api_call('PUT', f'api/listings/{listing_id}', update_data)
            if success:
                update_count += 1
                updated_ids.append(listing_id)
                print(f"   ✅ Updated listing: {listing_id}")
            else:
                print(f"   ❌ Failed to update listing: {listing_id}")
        
        # Verify updates persisted
        print("   🔍 Verifying update persistence...")
        persistence_count = 0
        
        for listing_id in updated_ids:
            success, listing_data = self.api_call('GET', f'api/listings/{listing_id}')
            if success:
                if (listing_data.get('price') == 999.99 and 
                    'UPDATED' in listing_data.get('title', '')):
                    persistence_count += 1
                    print(f"   ✅ Updates persisted for: {listing_id}")
                else:
                    print(f"   ❌ Updates not persisted for: {listing_id}")
        
        persistence_ok = persistence_count == len(updated_ids)
        
        return self.log_test("Bulk Update Operations",
                           update_count >= 2 and persistence_ok,
                           f"Updated {update_count} listings, persistence: {persistence_ok}")

    def test_add_info_integration(self):
        """Test add_info integration in listing creation"""
        print("\n📋 Testing add_info Integration...")
        
        if not self.admin_user:
            return self.log_test("add_info Integration", False, "No admin user available")
        
        # Get catalyst data with add_info
        success, catalyst_data = self.api_call('GET', 'api/admin/catalyst/data')
        if not success or not catalyst_data:
            return self.log_test("add_info Integration", False, "Could not retrieve catalyst data")
        
        # Find catalyst with add_info content
        test_catalyst = None
        for catalyst in catalyst_data[:10]:  # Check first 10
            if catalyst.get('add_info') and catalyst['add_info'].strip():
                test_catalyst = catalyst
                break
        
        if not test_catalyst:
            return self.log_test("add_info Integration", False, "No catalyst with add_info found")
        
        print(f"   📊 Using catalyst: {test_catalyst['name']}")
        print(f"   📊 add_info content: {test_catalyst['add_info'][:50]}...")
        
        # Create listing with add_info content in description
        listing_data = {
            "title": f"Catalyst: {test_catalyst['name']}",
            "description": f"Premium automotive catalyst. Additional Information: {test_catalyst['add_info']}",
            "price": 250.00,
            "category": "Catalysts",
            "condition": "Used - Good",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"]
        }
        
        success, create_response = self.api_call('POST', 'api/listings', listing_data)
        if not success or 'listing_id' not in create_response:
            return self.log_test("add_info Integration", False, "Failed to create catalyst listing")
        
        listing_id = create_response['listing_id']
        print(f"   ✅ Created catalyst listing: {listing_id}")
        
        # Verify add_info content is preserved
        success, listing_details = self.api_call('GET', f'api/listings/{listing_id}')
        if success:
            description = listing_details.get('description', '')
            add_info_preserved = test_catalyst['add_info'] in description
            print(f"   {'✅' if add_info_preserved else '❌'} add_info preserved: {add_info_preserved}")
        else:
            add_info_preserved = False
        
        # Cleanup
        self.api_call('DELETE', f'api/listings/{listing_id}')
        
        return self.log_test("add_info Integration", add_info_preserved,
                           f"add_info content preserved in listing description")

    def test_search_functionality_backend(self):
        """Test search functionality backend support"""
        print("\n🔍 Testing Search Functionality Backend Support...")
        
        if not self.admin_user:
            return self.log_test("Search Backend", False, "No admin user available")
        
        # Test catalyst data endpoint for search integration
        success, catalyst_data = self.api_call('GET', 'api/admin/catalyst/data')
        if not success:
            return self.log_test("Search Backend", False, "Catalyst data endpoint failed")
        
        # Verify complete catalyst objects with add_info field
        complete_objects = 0
        add_info_objects = 0
        
        for catalyst in catalyst_data[:10]:  # Check first 10
            required_fields = ['cat_id', 'name', 'ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm']
            if all(field in catalyst for field in required_fields):
                complete_objects += 1
                if 'add_info' in catalyst and catalyst['add_info']:
                    add_info_objects += 1
        
        print(f"   📊 Complete catalyst objects: {complete_objects}/10")
        print(f"   📊 Objects with add_info: {add_info_objects}/10")
        
        # Test calculations endpoint
        success, calc_data = self.api_call('GET', 'api/admin/catalyst/calculations')
        calc_ok = success and len(calc_data) > 0
        
        if calc_ok:
            print(f"   📊 Catalyst calculations available: {len(calc_data)}")
        
        search_ready = complete_objects >= 5 and add_info_objects >= 3 and calc_ok
        
        return self.log_test("Search Functionality Backend Support", search_ready,
                           f"Complete objects: {complete_objects}, add_info: {add_info_objects}, calculations: {calc_ok}")

    def test_listing_crud_operations(self):
        """Test comprehensive listing CRUD operations"""
        print("\n🔧 Testing Listing CRUD Operations...")
        
        if not self.regular_user:
            return self.log_test("CRUD Operations", False, "No regular user available")
        
        # CREATE
        listing_data = {
            "title": "CRUD Test - Professional Camera",
            "description": "High-end camera for CRUD testing with detailed specifications",
            "price": 1500.00,
            "category": "Photography",
            "condition": "Used - Excellent",
            "seller_id": self.regular_user['id'],
            "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"]
        }
        
        success, create_response = self.api_call('POST', 'api/listings', listing_data)
        if not success or 'listing_id' not in create_response:
            return self.log_test("CRUD Operations", False, "CREATE failed")
        
        listing_id = create_response['listing_id']
        print(f"   ✅ CREATE: {listing_id}")
        
        # READ
        success, read_response = self.api_call('GET', f'api/listings/{listing_id}')
        read_ok = (success and 
                  read_response.get('title') == listing_data['title'] and
                  read_response.get('price') == listing_data['price'])
        print(f"   {'✅' if read_ok else '❌'} READ: Data integrity {read_ok}")
        
        # UPDATE
        update_data = {
            "title": "CRUD Test - Professional Camera (UPDATED)",
            "price": 1350.00,
            "description": "Updated description with new price"
        }
        
        success, update_response = self.api_call('PUT', f'api/listings/{listing_id}', update_data)
        print(f"   {'✅' if success else '❌'} UPDATE: {success}")
        
        # Verify UPDATE persistence
        if success:
            success, verify_response = self.api_call('GET', f'api/listings/{listing_id}')
            update_persisted = (success and 
                              verify_response.get('title') == update_data['title'] and
                              verify_response.get('price') == update_data['price'])
            print(f"   {'✅' if update_persisted else '❌'} UPDATE Persistence: {update_persisted}")
        else:
            update_persisted = False
        
        # DELETE
        success, delete_response = self.api_call('DELETE', f'api/listings/{listing_id}')
        print(f"   {'✅' if success else '❌'} DELETE: {success}")
        
        # Verify DELETE persistence
        if success:
            success, read_deleted = self.api_call('GET', f'api/listings/{listing_id}', expected_status=404)
            delete_persisted = success  # Should get 404 for deleted listing
            print(f"   {'✅' if delete_persisted else '❌'} DELETE Persistence: {delete_persisted}")
        else:
            delete_persisted = False
        
        all_operations_ok = read_ok and success and update_persisted and delete_persisted
        
        return self.log_test("Listing CRUD Operations", all_operations_ok,
                           f"CREATE/READ/UPDATE/DELETE all working: {all_operations_ok}")

    def run_all_tests(self):
        """Run all bulk actions and add_info tests"""
        print("🚀 Starting Bulk Actions and add_info Search Functionality Tests")
        print("=" * 70)
        
        # Setup
        if not self.setup_users():
            print("❌ Failed to setup users - stopping tests")
            return False
        
        # Run tests as requested in review
        results = []
        
        print("\n1️⃣ Testing Bulk Listing Operations")
        results.append(self.test_bulk_listing_creation())
        results.append(self.test_bulk_delete_operations())
        results.append(self.test_bulk_update_operations())
        
        print("\n2️⃣ Testing Listing CRUD Operations")
        results.append(self.test_listing_crud_operations())
        
        print("\n3️⃣ Testing add_info Integration in Listing Creation")
        results.append(self.test_add_info_integration())
        
        print("\n4️⃣ Testing Search Functionality Backend Support")
        results.append(self.test_search_functionality_backend())
        
        # Summary
        passed_tests = sum(results)
        total_tests = len(results)
        
        print("\n" + "=" * 70)
        print(f"📊 Bulk Actions & add_info Test Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All bulk actions and add_info functionality tests passed!")
            print("✅ Backend properly supports:")
            print("   - Persistent bulk operations (create, delete, update)")
            print("   - Complete catalyst data with add_info for search functionality")
            print("   - Proper listing CRUD operations for admin panel")
            print("   - Data persistence across API calls")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed")
            print("❌ Some functionality may need attention")
            return False

def main():
    """Main test execution"""
    tester = BulkActionsAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())