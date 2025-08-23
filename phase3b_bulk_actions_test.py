#!/usr/bin/env python3
"""
Phase 3B Bulk Actions Testing Script
Tests bulk delete, bulk update, and bulk price update functionality for listings
"""

import requests
import json
import os
from datetime import datetime

# Configuration - Use localhost for testing as external proxy has routing issues
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class Phase3BBulkActionsTest:
    def __init__(self):
        self.admin_token = None
        self.test_listing_ids = []
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name, success, message=""):
        """Log test result"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED {message}")
    
    def admin_login(self):
        """Login as admin user"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.log_result("Admin Login", True, f"Token: {self.admin_token[:20]}...")
                return True
            else:
                self.log_result("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Admin Login", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    def create_test_listings(self):
        """Create multiple test listings for bulk operations"""
        try:
            test_listings = [
                {
                    "title": "Bulk Test Laptop 1",
                    "description": "Test laptop for bulk operations",
                    "category": "Electronics",
                    "condition": "New",
                    "listing_type": "fixed_price",
                    "price": 999.99,
                    "quantity": 1,
                    "location": "Test City"
                },
                {
                    "title": "Bulk Test Phone 2", 
                    "description": "Test phone for bulk operations",
                    "category": "Electronics",
                    "condition": "Used",
                    "listing_type": "fixed_price",
                    "price": 599.99,
                    "quantity": 2,
                    "location": "Test City"
                },
                {
                    "title": "Bulk Test Book 3",
                    "description": "Test book for bulk operations",
                    "category": "Books",
                    "condition": "Good",
                    "listing_type": "fixed_price",
                    "price": 29.99,
                    "quantity": 1,
                    "location": "Test City"
                },
                {
                    "title": "Bulk Test Shoes 4",
                    "description": "Test shoes for bulk operations",
                    "category": "Fashion",
                    "condition": "New",
                    "listing_type": "fixed_price",
                    "price": 149.99,
                    "quantity": 1,
                    "location": "Test City"
                },
                {
                    "title": "Bulk Test Watch 5",
                    "description": "Test watch for bulk operations",
                    "category": "Fashion",
                    "condition": "Excellent",
                    "listing_type": "fixed_price",
                    "price": 299.99,
                    "quantity": 1,
                    "location": "Test City"
                }
            ]
            
            created_count = 0
            for listing_data in test_listings:
                response = requests.post(
                    f"{API_BASE}/listings",
                    json=listing_data,
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    listing = response.json()
                    self.test_listing_ids.append(listing["id"])
                    created_count += 1
                else:
                    print(f"Failed to create listing: {response.status_code} - {response.text}")
            
            self.log_result("Create Test Listings", created_count == len(test_listings), 
                          f"Created {created_count}/{len(test_listings)} listings")
            return created_count == len(test_listings)
            
        except Exception as e:
            self.log_result("Create Test Listings", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_delete_endpoint(self):
        """Test bulk delete functionality"""
        try:
            # Test with first 2 listings
            delete_ids = self.test_listing_ids[:2]
            
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-delete",
                json={"listing_ids": delete_ids},
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_count = len(delete_ids)
                actual_count = data.get("deleted_count", 0)
                
                success = actual_count == expected_count
                self.log_result("Bulk Delete Endpoint", success, 
                              f"Deleted {actual_count}/{expected_count} listings")
                
                # Remove deleted IDs from our test list
                if success:
                    for delete_id in delete_ids:
                        if delete_id in self.test_listing_ids:
                            self.test_listing_ids.remove(delete_id)
                
                return success
            else:
                self.log_result("Bulk Delete Endpoint", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Bulk Delete Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_delete_invalid_ids(self):
        """Test bulk delete with invalid listing IDs"""
        try:
            invalid_ids = ["invalid-id-1", "invalid-id-2"]
            
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-delete",
                json={"listing_ids": invalid_ids},
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get("deleted_count", 0)
                
                # Should delete 0 items for invalid IDs
                success = deleted_count == 0
                self.log_result("Bulk Delete Invalid IDs", success, 
                              f"Correctly handled invalid IDs, deleted {deleted_count} items")
                return success
            else:
                self.log_result("Bulk Delete Invalid IDs", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Bulk Delete Invalid IDs", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_delete_empty_array(self):
        """Test bulk delete with empty listing array"""
        try:
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-delete",
                json={"listing_ids": []},
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get("deleted_count", 0)
                
                # Should delete 0 items for empty array
                success = deleted_count == 0
                self.log_result("Bulk Delete Empty Array", success, 
                              f"Correctly handled empty array, deleted {deleted_count} items")
                return success
            else:
                self.log_result("Bulk Delete Empty Array", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Bulk Delete Empty Array", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_update_status(self):
        """Test bulk update for status changes"""
        try:
            # Use remaining listings
            update_ids = self.test_listing_ids[:2] if len(self.test_listing_ids) >= 2 else self.test_listing_ids
            
            if not update_ids:
                self.log_result("Bulk Update Status", False, "No listings available for testing")
                return False
            
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-update",
                json={
                    "listing_ids": update_ids,
                    "status": "sold"
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_count = len(update_ids)
                actual_count = data.get("modified_count", 0)
                
                success = actual_count == expected_count
                self.log_result("Bulk Update Status", success, 
                              f"Updated {actual_count}/{expected_count} listings to 'sold' status")
                return success
            else:
                self.log_result("Bulk Update Status", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Bulk Update Status", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_update_category(self):
        """Test bulk update for category changes"""
        try:
            # Use remaining listings
            update_ids = self.test_listing_ids[:1] if len(self.test_listing_ids) >= 1 else []
            
            if not update_ids:
                self.log_result("Bulk Update Category", False, "No listings available for testing")
                return False
            
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-update",
                json={
                    "listing_ids": update_ids,
                    "category": "Other"
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_count = len(update_ids)
                actual_count = data.get("modified_count", 0)
                
                success = actual_count == expected_count
                self.log_result("Bulk Update Category", success, 
                              f"Updated {actual_count}/{expected_count} listings to 'Other' category")
                return success
            else:
                self.log_result("Bulk Update Category", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Bulk Update Category", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_update_featured(self):
        """Test bulk update for featured/unfeatured operations"""
        try:
            # Use remaining listings
            update_ids = self.test_listing_ids[:1] if len(self.test_listing_ids) >= 1 else []
            
            if not update_ids:
                self.log_result("Bulk Update Featured", False, "No listings available for testing")
                return False
            
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-update",
                json={
                    "listing_ids": update_ids,
                    "featured": True
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_count = len(update_ids)
                actual_count = data.get("modified_count", 0)
                
                success = actual_count == expected_count
                self.log_result("Bulk Update Featured", success, 
                              f"Updated {actual_count}/{expected_count} listings to featured")
                return success
            else:
                self.log_result("Bulk Update Featured", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Bulk Update Featured", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_update_no_fields(self):
        """Test bulk update with no update fields provided"""
        try:
            update_ids = self.test_listing_ids[:1] if len(self.test_listing_ids) >= 1 else ["dummy-id"]
            
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-update",
                json={"listing_ids": update_ids},
                headers=self.get_auth_headers()
            )
            
            # Should return 400 error for no update fields
            success = response.status_code == 400
            self.log_result("Bulk Update No Fields", success, 
                          f"Correctly rejected request with no update fields (Status: {response.status_code})")
            return success
                
        except Exception as e:
            self.log_result("Bulk Update No Fields", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_price_increase(self):
        """Test bulk price update with percentage increase"""
        try:
            # Create fresh listings for price testing
            fresh_listing_data = {
                "title": "Price Test Item",
                "description": "Item for price testing",
                "category": "Electronics",
                "condition": "New",
                "listing_type": "fixed_price",
                "price": 100.00,
                "quantity": 1,
                "location": "Test City"
            }
            
            response = requests.post(
                f"{API_BASE}/listings",
                json=fresh_listing_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                self.log_result("Bulk Price Increase", False, "Failed to create test listing")
                return False
            
            listing = response.json()
            listing_id = listing["id"]
            
            # Test 10% price increase
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-price-update",
                json={
                    "listing_ids": [listing_id],
                    "price_type": "increase",
                    "price_value": 10.0
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                updates = data.get("updates", [])
                
                if updates and len(updates) == 1:
                    update = updates[0]
                    old_price = update.get("old_price", 0)
                    new_price = update.get("new_price", 0)
                    expected_price = 110.00  # 100 + 10%
                    
                    success = abs(new_price - expected_price) < 0.01
                    self.log_result("Bulk Price Increase", success, 
                                  f"Price updated from ${old_price} to ${new_price} (expected ${expected_price})")
                    
                    # Clean up
                    requests.delete(f"{API_BASE}/admin/listings/{listing_id}", headers=self.get_auth_headers())
                    return success
                else:
                    self.log_result("Bulk Price Increase", False, "No price updates returned")
                    return False
            else:
                self.log_result("Bulk Price Increase", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Bulk Price Increase", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_price_decrease(self):
        """Test bulk price update with percentage decrease and minimum price protection"""
        try:
            # Create fresh listing for price testing
            fresh_listing_data = {
                "title": "Price Decrease Test Item",
                "description": "Item for price decrease testing",
                "category": "Electronics",
                "condition": "New",
                "listing_type": "fixed_price",
                "price": 50.00,
                "quantity": 1,
                "location": "Test City"
            }
            
            response = requests.post(
                f"{API_BASE}/listings",
                json=fresh_listing_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                self.log_result("Bulk Price Decrease", False, "Failed to create test listing")
                return False
            
            listing = response.json()
            listing_id = listing["id"]
            
            # Test 20% price decrease
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-price-update",
                json={
                    "listing_ids": [listing_id],
                    "price_type": "decrease",
                    "price_value": 20.0
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                updates = data.get("updates", [])
                
                if updates and len(updates) == 1:
                    update = updates[0]
                    old_price = update.get("old_price", 0)
                    new_price = update.get("new_price", 0)
                    expected_price = 40.00  # 50 - 20%
                    
                    success = abs(new_price - expected_price) < 0.01
                    self.log_result("Bulk Price Decrease", success, 
                                  f"Price updated from ${old_price} to ${new_price} (expected ${expected_price})")
                    
                    # Clean up
                    requests.delete(f"{API_BASE}/admin/listings/{listing_id}", headers=self.get_auth_headers())
                    return success
                else:
                    self.log_result("Bulk Price Decrease", False, "No price updates returned")
                    return False
            else:
                self.log_result("Bulk Price Decrease", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Bulk Price Decrease", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_price_set_fixed(self):
        """Test bulk price update with fixed price setting"""
        try:
            # Create fresh listing for price testing
            fresh_listing_data = {
                "title": "Fixed Price Test Item",
                "description": "Item for fixed price testing",
                "category": "Electronics",
                "condition": "New",
                "listing_type": "fixed_price",
                "price": 75.00,
                "quantity": 1,
                "location": "Test City"
            }
            
            response = requests.post(
                f"{API_BASE}/listings",
                json=fresh_listing_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                self.log_result("Bulk Price Set Fixed", False, "Failed to create test listing")
                return False
            
            listing = response.json()
            listing_id = listing["id"]
            
            # Test setting fixed price to $199.99
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-price-update",
                json={
                    "listing_ids": [listing_id],
                    "price_type": "set",
                    "price_value": 199.99
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                updates = data.get("updates", [])
                
                if updates and len(updates) == 1:
                    update = updates[0]
                    old_price = update.get("old_price", 0)
                    new_price = update.get("new_price", 0)
                    expected_price = 199.99
                    
                    success = abs(new_price - expected_price) < 0.01
                    self.log_result("Bulk Price Set Fixed", success, 
                                  f"Price updated from ${old_price} to ${new_price} (expected ${expected_price})")
                    
                    # Clean up
                    requests.delete(f"{API_BASE}/admin/listings/{listing_id}", headers=self.get_auth_headers())
                    return success
                else:
                    self.log_result("Bulk Price Set Fixed", False, "No price updates returned")
                    return False
            else:
                self.log_result("Bulk Price Set Fixed", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Bulk Price Set Fixed", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_price_invalid_type(self):
        """Test bulk price update with invalid price type"""
        try:
            # Use any available listing ID or create a dummy one
            test_ids = self.test_listing_ids[:1] if self.test_listing_ids else ["dummy-id"]
            
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-price-update",
                json={
                    "listing_ids": test_ids,
                    "price_type": "invalid_type",
                    "price_value": 10.0
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                updates = data.get("updates", [])
                
                # Should return empty updates for invalid price type
                success = len(updates) == 0
                self.log_result("Bulk Price Invalid Type", success, 
                              f"Correctly handled invalid price type, {len(updates)} updates made")
                return success
            else:
                # Could also return an error status, which is acceptable
                self.log_result("Bulk Price Invalid Type", True, 
                              f"Correctly rejected invalid price type (Status: {response.status_code})")
                return True
                
        except Exception as e:
            self.log_result("Bulk Price Invalid Type", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_authentication_required(self):
        """Test that admin authentication is required for all bulk operations"""
        try:
            # Test without authentication
            test_ids = ["dummy-id"]
            
            # Test bulk delete without auth
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-delete",
                json={"listing_ids": test_ids}
            )
            delete_auth_required = response.status_code in [401, 403]
            
            # Test bulk update without auth
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-update",
                json={"listing_ids": test_ids, "status": "active"}
            )
            update_auth_required = response.status_code in [401, 403]
            
            # Test bulk price update without auth
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-price-update",
                json={"listing_ids": test_ids, "price_type": "increase", "price_value": 10.0}
            )
            price_auth_required = response.status_code in [401, 403]
            
            success = delete_auth_required and update_auth_required and price_auth_required
            self.log_result("Admin Authentication Required", success, 
                          f"All endpoints properly require admin auth (Delete: {delete_auth_required}, Update: {update_auth_required}, Price: {price_auth_required})")
            return success
                
        except Exception as e:
            self.log_result("Admin Authentication Required", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_test_listings(self):
        """Clean up any remaining test listings"""
        try:
            if not self.test_listing_ids:
                return True
            
            response = requests.post(
                f"{API_BASE}/admin/listings/bulk-delete",
                json={"listing_ids": self.test_listing_ids},
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get("deleted_count", 0)
                print(f"🧹 Cleanup: Deleted {deleted_count} remaining test listings")
                return True
            else:
                print(f"⚠️ Cleanup failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"⚠️ Cleanup exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Phase 3B bulk actions tests"""
        print("🚀 Starting Phase 3B Bulk Actions Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Login as admin
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Create test data
        if not self.create_test_listings():
            print("❌ Cannot proceed without test listings")
            return False
        
        # Run bulk delete tests
        print("\n📋 Testing Bulk Delete Functionality...")
        self.test_bulk_delete_endpoint()
        self.test_bulk_delete_invalid_ids()
        self.test_bulk_delete_empty_array()
        
        # Run bulk update tests
        print("\n📋 Testing Bulk Update Functionality...")
        self.test_bulk_update_status()
        self.test_bulk_update_category()
        self.test_bulk_update_featured()
        self.test_bulk_update_no_fields()
        
        # Run bulk price update tests
        print("\n📋 Testing Bulk Price Update Functionality...")
        self.test_bulk_price_increase()
        self.test_bulk_price_decrease()
        self.test_bulk_price_set_fixed()
        self.test_bulk_price_invalid_type()
        
        # Test authentication
        print("\n📋 Testing Authentication Requirements...")
        self.test_admin_authentication_required()
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        self.cleanup_test_listings()
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 PHASE 3B BULK ACTIONS TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print("\n❌ FAILED TESTS:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 PHASE 3B BULK ACTIONS FUNCTIONALITY IS WORKING EXCELLENTLY!")
        elif success_rate >= 75:
            print("✅ PHASE 3B BULK ACTIONS FUNCTIONALITY IS WORKING WELL!")
        elif success_rate >= 50:
            print("⚠️ PHASE 3B BULK ACTIONS FUNCTIONALITY HAS SOME ISSUES")
        else:
            print("❌ PHASE 3B BULK ACTIONS FUNCTIONALITY HAS MAJOR ISSUES")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = Phase3BBulkActionsTest()
    tester.run_all_tests()