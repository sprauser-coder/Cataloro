#!/usr/bin/env python3
"""
Cataloro Marketplace - Bulk Delete Debug Test Suite
Specifically tests the admin panel bulk delete issue reported by user
"""

import requests
import sys
import json
import time
from datetime import datetime

class BulkDeleteDebugTester:
    def __init__(self, base_url="https://trade-platform-30.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.admin_user = None
        self.session = requests.Session()
        self.created_listing_ids = []
        self.tests_run = 0
        self.tests_passed = 0

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

    def setup_admin_session(self):
        """Setup admin session for testing"""
        print("\n🔐 Setting up admin session...")
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
            print(f"   ✅ Admin logged in: {self.admin_user.get('full_name', 'Admin')}")
            return True
        return False

    def create_test_listings(self, count=5):
        """Create multiple test listings for bulk delete testing"""
        print(f"\n📝 Creating {count} test listings for bulk delete testing...")
        
        if not self.admin_user:
            print("❌ No admin user - cannot create test listings")
            return False

        test_listings = [
            {
                "title": f"Bulk Delete Test #{i+1} - Gaming Laptop",
                "description": f"Test listing #{i+1} for bulk delete functionality testing. High-performance gaming laptop with RTX graphics.",
                "price": 1500.00 + (i * 100),
                "category": "Electronics",
                "condition": "Used - Excellent",
                "seller_id": self.admin_user['id'],
                "images": ["https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400"],
                "tags": ["gaming", "laptop", "test"],
                "features": ["RTX Graphics", "16GB RAM", "1TB SSD"]
            }
            for i in range(count)
        ]

        created_count = 0
        for i, listing_data in enumerate(test_listings):
            success, response = self.run_test(
                f"Create Test Listing {i+1}",
                "POST",
                "api/listings",
                200,
                data=listing_data
            )
            
            if success and 'listing_id' in response:
                listing_id = response['listing_id']
                self.created_listing_ids.append(listing_id)
                created_count += 1
                print(f"   ✅ Created listing {i+1}: {listing_id}")
            else:
                print(f"   ❌ Failed to create listing {i+1}")

        success = created_count == count
        self.log_test(f"Create {count} Test Listings", success, f"Created {created_count}/{count} listings")
        return success

    def verify_listings_in_browse(self):
        """Verify all created listings appear in browse endpoint"""
        print(f"\n🔍 Verifying {len(self.created_listing_ids)} listings appear in browse...")
        
        success, response = self.run_test(
            "Browse Listings (Before Delete)",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success:
            return False

        found_count = 0
        for listing_id in self.created_listing_ids:
            found = any(listing.get('id') == listing_id for listing in response)
            if found:
                found_count += 1
                print(f"   ✅ Found listing {listing_id[:8]}... in browse")
            else:
                print(f"   ❌ Missing listing {listing_id[:8]}... in browse")

        success = found_count == len(self.created_listing_ids)
        self.log_test("All Listings in Browse", success, f"Found {found_count}/{len(self.created_listing_ids)} listings")
        return success

    def test_individual_delete(self):
        """Test individual DELETE operations (should work according to user report)"""
        print(f"\n🗑️ Testing individual DELETE operations...")
        
        if not self.created_listing_ids:
            print("❌ No test listings available for individual delete test")
            return False

        # Test deleting the first listing individually
        test_listing_id = self.created_listing_ids[0]
        
        print(f"   Testing DELETE /api/listings/{test_listing_id}")
        success, response = self.run_test(
            "Individual DELETE Operation",
            "DELETE",
            f"api/listings/{test_listing_id}",
            200
        )
        
        if success:
            deleted_count = response.get('deleted_count', 0)
            print(f"   ✅ Individual delete successful, deleted_count: {deleted_count}")
            
            # Verify the listing is actually removed
            time.sleep(1)  # Brief pause to ensure database consistency
            
            success_verify, browse_response = self.run_test(
                "Verify Individual Delete",
                "GET",
                "api/marketplace/browse",
                200
            )
            
            if success_verify:
                still_exists = any(listing.get('id') == test_listing_id for listing in browse_response)
                if not still_exists:
                    print(f"   ✅ Listing {test_listing_id[:8]}... successfully removed from browse")
                    self.log_test("Individual Delete Verification", True, "Listing removed from browse")
                    # Remove from our tracking list
                    self.created_listing_ids.remove(test_listing_id)
                    return True
                else:
                    print(f"   ❌ Listing {test_listing_id[:8]}... still appears in browse after delete")
                    self.log_test("Individual Delete Verification", False, "Listing still in browse")
                    return False
        
        return success

    def test_bulk_delete_simulation(self):
        """Simulate bulk delete operations as the frontend would do"""
        print(f"\n📦 Testing bulk DELETE operations (simulating frontend bulk delete)...")
        
        if len(self.created_listing_ids) < 2:
            print("❌ Need at least 2 listings for bulk delete test")
            return False

        # Take the remaining listings for bulk delete
        bulk_delete_ids = self.created_listing_ids.copy()
        print(f"   Attempting to bulk delete {len(bulk_delete_ids)} listings...")
        
        # Simulate what the frontend bulk delete would do:
        # Make multiple DELETE requests in sequence
        successful_deletes = 0
        failed_deletes = 0
        
        for i, listing_id in enumerate(bulk_delete_ids):
            print(f"\n   Bulk Delete {i+1}/{len(bulk_delete_ids)}: {listing_id[:8]}...")
            
            success, response = self.run_test(
                f"Bulk Delete Item {i+1}",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
            
            if success:
                successful_deletes += 1
                deleted_count = response.get('deleted_count', 0)
                print(f"     ✅ Delete successful, deleted_count: {deleted_count}")
            else:
                failed_deletes += 1
                print(f"     ❌ Delete failed")

        print(f"\n   📊 Bulk Delete Results: {successful_deletes} successful, {failed_deletes} failed")
        
        # Verify bulk delete results
        time.sleep(2)  # Longer pause for bulk operations
        
        success_verify, browse_response = self.run_test(
            "Verify Bulk Delete Results",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success_verify:
            remaining_count = 0
            for listing_id in bulk_delete_ids:
                still_exists = any(listing.get('id') == listing_id for listing in browse_response)
                if still_exists:
                    remaining_count += 1
                    print(f"     ⚠️ Listing {listing_id[:8]}... still exists after bulk delete")
                else:
                    print(f"     ✅ Listing {listing_id[:8]}... successfully removed")
            
            bulk_success = remaining_count == 0
            self.log_test("Bulk Delete Verification", bulk_success, 
                         f"{remaining_count}/{len(bulk_delete_ids)} listings still exist (should be 0)")
            
            return bulk_success
        
        return False

    def test_api_response_analysis(self):
        """Analyze API responses for bulk delete operations"""
        print(f"\n🔬 Analyzing API responses for delete operations...")
        
        # Create one more test listing for detailed analysis
        test_listing = {
            "title": "API Response Analysis Test - Smartphone",
            "description": "Test listing for analyzing API response details during delete operations.",
            "price": 899.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400"]
        }
        
        success_create, create_response = self.run_test(
            "Create Analysis Test Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_create:
            return False
        
        analysis_listing_id = create_response['listing_id']
        print(f"   ✅ Created analysis listing: {analysis_listing_id}")
        
        # Detailed DELETE request analysis
        url = f"{self.base_url}/api/listings/{analysis_listing_id}"
        print(f"\n   🔍 Detailed DELETE analysis for: {url}")
        
        try:
            # Make DELETE request with detailed logging
            response = self.session.delete(url, headers={'Content-Type': 'application/json'})
            
            print(f"   📊 Response Status Code: {response.status_code}")
            print(f"   📊 Response Headers: {dict(response.headers)}")
            
            if response.text:
                try:
                    response_json = response.json()
                    print(f"   📊 Response JSON: {json.dumps(response_json, indent=2)}")
                    
                    # Check for specific fields
                    if 'message' in response_json:
                        print(f"   ✅ Success message: {response_json['message']}")
                    if 'deleted_count' in response_json:
                        print(f"   ✅ Deleted count: {response_json['deleted_count']}")
                    
                except json.JSONDecodeError:
                    print(f"   📊 Response Text (not JSON): {response.text}")
            else:
                print(f"   ⚠️ Empty response body")
            
            # Check if the delete was actually successful
            success = response.status_code == 200
            self.log_test("API Response Analysis", success, f"Status: {response.status_code}")
            
            return success
            
        except Exception as e:
            print(f"   ❌ Error during API analysis: {str(e)}")
            self.log_test("API Response Analysis", False, f"Error: {str(e)}")
            return False

    def test_listing_count_verification(self):
        """Test if total listing count decreases after deletions"""
        print(f"\n📊 Testing listing count changes...")
        
        # Get initial count
        success_before, browse_before = self.run_test(
            "Get Initial Listing Count",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not success_before:
            return False
        
        initial_count = len(browse_before)
        print(f"   📊 Initial listing count: {initial_count}")
        
        # Create a test listing
        test_listing = {
            "title": "Count Test Listing - Tablet",
            "description": "Test listing for count verification during delete operations.",
            "price": 599.99,
            "category": "Electronics",
            "condition": "Used - Good",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400"]
        }
        
        success_create, create_response = self.run_test(
            "Create Count Test Listing",
            "POST",
            "api/listings",
            200,
            data=test_listing
        )
        
        if not success_create:
            return False
        
        count_test_id = create_response['listing_id']
        
        # Verify count increased
        success_after_create, browse_after_create = self.run_test(
            "Get Count After Create",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success_after_create:
            count_after_create = len(browse_after_create)
            print(f"   📊 Count after create: {count_after_create}")
            
            if count_after_create == initial_count + 1:
                print(f"   ✅ Count increased correctly after create")
            else:
                print(f"   ⚠️ Count did not increase as expected")
        
        # Delete the listing
        success_delete, delete_response = self.run_test(
            "Delete Count Test Listing",
            "DELETE",
            f"api/listings/{count_test_id}",
            200
        )
        
        if not success_delete:
            return False
        
        # Verify count decreased
        time.sleep(1)
        success_after_delete, browse_after_delete = self.run_test(
            "Get Count After Delete",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success_after_delete:
            count_after_delete = len(browse_after_delete)
            print(f"   📊 Count after delete: {count_after_delete}")
            
            count_decreased = count_after_delete == initial_count
            if count_decreased:
                print(f"   ✅ Count decreased correctly after delete")
            else:
                print(f"   ❌ Count did not decrease as expected (expected: {initial_count}, got: {count_after_delete})")
            
            self.log_test("Listing Count Verification", count_decreased, 
                         f"Count: {initial_count} → {count_after_create} → {count_after_delete}")
            return count_decreased
        
        return False

    def run_bulk_delete_debug_tests(self):
        """Run the complete bulk delete debug test suite"""
        print("🚀 Starting Bulk Delete Debug Test Suite")
        print("=" * 60)
        print("🎯 Focus: Debug admin panel bulk delete issue")
        print("   1. ✅ Confirmation modal appears (working)")
        print("   2. ❌ No success notification after confirmation")
        print("   3. ❌ Listings don't get deleted (still appear after refresh)")
        print("   4. ❌ Total count doesn't decrease")
        print("=" * 60)

        # Setup
        if not self.setup_admin_session():
            print("❌ Failed to setup admin session - stopping tests")
            return False

        # Test 1: Create Test Listings
        print(f"\n1️⃣ CREATE TEST LISTINGS")
        if not self.create_test_listings(5):
            print("❌ Failed to create test listings - stopping tests")
            return False

        # Test 2: Verify Listings in Browse
        print(f"\n2️⃣ VERIFY LISTINGS IN BROWSE")
        if not self.verify_listings_in_browse():
            print("⚠️ Not all listings appear in browse - continuing with available listings")

        # Test 3: Test Individual Delete (should work)
        print(f"\n3️⃣ TEST INDIVIDUAL DELETE (BASELINE)")
        individual_success = self.test_individual_delete()
        if individual_success:
            print("✅ Individual delete works correctly")
        else:
            print("❌ Individual delete failed - this indicates a deeper issue")

        # Test 4: Test Bulk Delete Simulation
        print(f"\n4️⃣ TEST BULK DELETE SIMULATION")
        bulk_success = self.test_bulk_delete_simulation()
        if bulk_success:
            print("✅ Bulk delete operations work correctly")
        else:
            print("❌ Bulk delete operations failed - this matches user report")

        # Test 5: API Response Analysis
        print(f"\n5️⃣ API RESPONSE ANALYSIS")
        api_success = self.test_api_response_analysis()

        # Test 6: Listing Count Verification
        print(f"\n6️⃣ LISTING COUNT VERIFICATION")
        count_success = self.test_listing_count_verification()

        # Summary
        print("\n" + "=" * 60)
        print("📊 BULK DELETE DEBUG TEST RESULTS")
        print("=" * 60)
        
        test_results = [
            ("Individual Delete (Baseline)", individual_success),
            ("Bulk Delete Operations", bulk_success),
            ("API Response Analysis", api_success),
            ("Listing Count Verification", count_success)
        ]
        
        passed_tests = sum(1 for _, success in test_results if success)
        total_tests = len(test_results)
        
        for test_name, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n📊 Overall Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        print(f"📊 Test Categories: {passed_tests}/{total_tests} categories passed")
        
        # Diagnosis
        print("\n🔬 DIAGNOSIS:")
        if individual_success and not bulk_success:
            print("   ⚠️ Individual delete works but bulk delete fails")
            print("   💡 This suggests the issue is in bulk operation handling")
            print("   💡 Frontend may not be handling multiple DELETE requests correctly")
        elif not individual_success:
            print("   ❌ Individual delete also fails")
            print("   💡 This suggests a fundamental issue with the DELETE endpoint")
        elif bulk_success:
            print("   ✅ Both individual and bulk delete work correctly")
            print("   💡 The issue may be in frontend notification/UI update logic")
        
        if not count_success:
            print("   ❌ Listing count doesn't update correctly")
            print("   💡 This confirms the user's report about count not decreasing")
        
        return passed_tests >= 3  # Consider success if most tests pass

def main():
    """Main test execution"""
    tester = BulkDeleteDebugTester()
    success = tester.run_bulk_delete_debug_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())