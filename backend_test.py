#!/usr/bin/env python3
"""
Bulk Order Management Endpoints Testing
Testing the fixed bulk order management endpoints after resolving FastAPI parameter conflict.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class BulkOrderTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })
    
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
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Authentication", True, 
                            f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                            f"Failed to authenticate: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_get_admin_orders(self):
        """Test GET /api/admin/orders endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/orders")
            
            if response.status_code == 200:
                orders = response.json()
                self.log_test("GET Admin Orders", True, 
                            f"Successfully retrieved {len(orders)} orders",
                            f"Orders data structure verified")
                return orders
            else:
                self.log_test("GET Admin Orders", False, 
                            f"Failed to get orders: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.log_test("GET Admin Orders", False, f"Error getting orders: {str(e)}")
            return []
    
    def create_test_orders(self):
        """Create some test orders for bulk operations"""
        test_orders = []
        
        try:
            # First, let's get some listings to create orders with
            listings_response = self.session.get(f"{BACKEND_URL}/listings?limit=2")
            if listings_response.status_code != 200:
                self.log_test("Create Test Orders", False, "No listings available for test orders")
                return []
            
            listings = listings_response.json()
            if not listings:
                self.log_test("Create Test Orders", False, "No listings found to create test orders")
                return []
            
            # Create a test buyer user first
            test_buyer_data = {
                "email": "testbuyer@example.com",
                "username": "testbuyer",
                "password": "testpass123",
                "full_name": "Test Buyer",
                "role": "buyer"
            }
            
            # Try to register test buyer (might already exist)
            buyer_response = self.session.post(f"{BACKEND_URL}/auth/register", json=test_buyer_data)
            if buyer_response.status_code in [200, 400]:  # 400 if user already exists
                # Login as buyer
                buyer_login = self.session.post(f"{BACKEND_URL}/auth/login", json={
                    "email": "testbuyer@example.com",
                    "password": "testpass123"
                })
                
                if buyer_login.status_code == 200:
                    buyer_token = buyer_login.json()["access_token"]
                    
                    # Create orders as buyer
                    for i, listing in enumerate(listings[:2]):
                        if listing.get("listing_type") == "fixed_price" and listing.get("price"):
                            order_data = {
                                "listing_id": listing["id"],
                                "quantity": 1,
                                "shipping_address": f"Test Address {i+1}, Test City"
                            }
                            
                            # Use buyer token for creating order
                            headers = {"Authorization": f"Bearer {buyer_token}"}
                            order_response = requests.post(f"{BACKEND_URL}/orders", 
                                                         json=order_data, headers=headers)
                            
                            if order_response.status_code == 200:
                                order = order_response.json()
                                test_orders.append(order["id"])
            
            # Restore admin token
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
            
            if test_orders:
                self.log_test("Create Test Orders", True, 
                            f"Created {len(test_orders)} test orders for bulk operations")
            else:
                self.log_test("Create Test Orders", False, "Could not create test orders")
            
            return test_orders
            
        except Exception as e:
            self.log_test("Create Test Orders", False, f"Error creating test orders: {str(e)}")
            return []
    
    def test_bulk_update_orders(self, order_ids):
        """Test POST /api/admin/orders/bulk-update endpoint"""
        if not order_ids:
            self.log_test("Bulk Update Orders", False, "No order IDs available for testing")
            return False
        
        try:
            # Test bulk update with proper request body format
            update_data = {
                "order_ids": order_ids,
                "status": "completed"
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/orders/bulk-update", 
                                       json=update_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Bulk Update Orders", True, 
                            f"Successfully updated {result.get('updated_count', 0)} orders to completed status",
                            f"Response: {result}")
                return True
            else:
                self.log_test("Bulk Update Orders", False, 
                            f"Failed to bulk update orders: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bulk Update Orders", False, f"Error in bulk update: {str(e)}")
            return False
    
    def test_bulk_delete_orders(self, order_ids):
        """Test POST /api/admin/orders/bulk-delete endpoint"""
        if not order_ids:
            self.log_test("Bulk Delete Orders", False, "No order IDs available for testing")
            return False
        
        try:
            # Test bulk delete with proper request body format
            delete_data = {
                "order_ids": order_ids
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/orders/bulk-delete", 
                                       json=delete_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Bulk Delete Orders", True, 
                            f"Successfully deleted {result.get('deleted_count', 0)} orders",
                            f"Response: {result}")
                return True
            else:
                self.log_test("Bulk Delete Orders", False, 
                            f"Failed to bulk delete orders: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bulk Delete Orders", False, f"Error in bulk delete: {str(e)}")
            return False
    
    def test_bulk_operations_validation(self):
        """Test bulk operations with invalid data"""
        try:
            # Test bulk update with empty order_ids
            empty_update = self.session.post(f"{BACKEND_URL}/admin/orders/bulk-update", 
                                           json={"order_ids": [], "status": "completed"})
            
            if empty_update.status_code == 400:
                self.log_test("Bulk Update Validation", True, 
                            "Correctly rejected empty order_ids list")
            else:
                self.log_test("Bulk Update Validation", False, 
                            f"Should reject empty order_ids: {empty_update.status_code}")
            
            # Test bulk delete with empty order_ids
            empty_delete = self.session.post(f"{BACKEND_URL}/admin/orders/bulk-delete", 
                                           json={"order_ids": []})
            
            if empty_delete.status_code == 400:
                self.log_test("Bulk Delete Validation", True, 
                            "Correctly rejected empty order_ids list")
            else:
                self.log_test("Bulk Delete Validation", False, 
                            f"Should reject empty order_ids: {empty_delete.status_code}")
            
            # Test with non-existent order IDs
            fake_ids = ["fake-order-1", "fake-order-2"]
            fake_update = self.session.post(f"{BACKEND_URL}/admin/orders/bulk-update", 
                                          json={"order_ids": fake_ids, "status": "completed"})
            
            if fake_update.status_code == 200:
                result = fake_update.json()
                if result.get("updated_count", 0) == 0:
                    self.log_test("Non-existent Order IDs", True, 
                                "Correctly handled non-existent order IDs (0 updated)")
                else:
                    self.log_test("Non-existent Order IDs", False, 
                                f"Should not update non-existent orders: {result}")
            
        except Exception as e:
            self.log_test("Bulk Operations Validation", False, f"Error in validation tests: {str(e)}")
    
    def run_all_tests(self):
        """Run all bulk order management tests"""
        print("=" * 60)
        print("BULK ORDER MANAGEMENT ENDPOINTS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test GET admin orders
        existing_orders = self.test_get_admin_orders()
        
        # Step 3: Create test orders for bulk operations
        test_order_ids = self.create_test_orders()
        
        # Use existing orders if we couldn't create test orders
        if not test_order_ids and existing_orders:
            test_order_ids = [order["order"]["id"] for order in existing_orders[:2]]
            self.log_test("Using Existing Orders", True, 
                        f"Using {len(test_order_ids)} existing orders for bulk testing")
        
        # Step 4: Test bulk update orders
        self.test_bulk_update_orders(test_order_ids)
        
        # Step 5: Create fresh test orders for delete test (since we updated the previous ones)
        fresh_test_orders = self.create_test_orders()
        if not fresh_test_orders and existing_orders:
            # Use different existing orders for delete test
            fresh_test_orders = [order["order"]["id"] for order in existing_orders[2:4]]
        
        # Step 6: Test bulk delete orders
        self.test_bulk_delete_orders(fresh_test_orders)
        
        # Step 7: Test validation scenarios
        self.test_bulk_operations_validation()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = BulkOrderTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All bulk order management tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()