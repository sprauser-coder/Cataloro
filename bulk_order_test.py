#!/usr/bin/env python3
"""
Bulk Order Management Endpoints Testing
Testing the new bulk order management functionality:
1. GET /api/admin/orders - Verify we can get existing orders
2. POST /api/admin/orders/bulk-update - Test bulk updating order status
3. POST /api/admin/orders/bulk-delete - Test bulk deleting orders
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
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
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
                self.log_result("Admin Authentication", True, f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Failed to authenticate: {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_get_admin_orders(self):
        """Test GET /api/admin/orders endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/orders")
            
            if response.status_code == 200:
                orders = response.json()
                order_count = len(orders)
                
                # Extract order IDs for later bulk operations
                order_ids = []
                if orders:
                    for order_data in orders:
                        if isinstance(order_data, dict) and 'order' in order_data:
                            order_ids.append(order_data['order']['id'])
                        elif isinstance(order_data, dict) and 'id' in order_data:
                            order_ids.append(order_data['id'])
                
                self.log_result("GET Admin Orders", True, 
                              f"Successfully retrieved {order_count} orders", 
                              {"order_count": order_count, "sample_order_ids": order_ids[:3]})
                return order_ids
            else:
                self.log_result("GET Admin Orders", False, 
                              f"Failed to get orders: {response.status_code}", 
                              {"response": response.text})
                return []
                
        except Exception as e:
            self.log_result("GET Admin Orders", False, f"Error getting orders: {str(e)}")
            return []
    
    def test_bulk_update_orders(self, order_ids):
        """Test POST /api/admin/orders/bulk-update endpoint"""
        if not order_ids:
            self.log_result("Bulk Update Orders", False, "No order IDs available for testing")
            return
        
        # Test with first few order IDs (max 3 for safety)
        test_order_ids = order_ids[:3]
        
        try:
            # Test bulk update to 'completed' status
            response = self.session.post(f"{BACKEND_URL}/admin/orders/bulk-update", json={
                "order_ids": test_order_ids,
                "status": "completed"
            })
            
            if response.status_code == 200:
                data = response.json()
                updated_count = data.get("updated_count", 0)
                self.log_result("Bulk Update Orders", True, 
                              f"Successfully updated {updated_count} orders to completed status", 
                              {"updated_count": updated_count, "order_ids": test_order_ids})
            else:
                self.log_result("Bulk Update Orders", False, 
                              f"Failed to bulk update orders: {response.status_code}", 
                              {"response": response.text, "order_ids": test_order_ids})
                
        except Exception as e:
            self.log_result("Bulk Update Orders", False, f"Error bulk updating orders: {str(e)}")
    
    def test_bulk_update_validation(self):
        """Test bulk update validation with empty order IDs"""
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/orders/bulk-update", json={
                "order_ids": [],
                "status": "completed"
            })
            
            if response.status_code == 400:
                self.log_result("Bulk Update Validation", True, 
                              "Correctly rejected empty order IDs with 400 error")
            else:
                self.log_result("Bulk Update Validation", False, 
                              f"Expected 400 error for empty order IDs, got {response.status_code}", 
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Bulk Update Validation", False, f"Error testing validation: {str(e)}")
    
    def test_bulk_delete_orders(self, order_ids):
        """Test POST /api/admin/orders/bulk-delete endpoint"""
        if not order_ids:
            self.log_result("Bulk Delete Orders", False, "No order IDs available for testing")
            return
        
        # Only test deletion if we have test orders (be careful not to delete real orders)
        # For safety, we'll test with non-existent order IDs first
        test_order_ids = ["test-order-1", "test-order-2"]
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/orders/bulk-delete", json={
                "order_ids": test_order_ids
            })
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get("deleted_count", 0)
                self.log_result("Bulk Delete Orders (Test IDs)", True, 
                              f"Bulk delete endpoint working - deleted {deleted_count} orders", 
                              {"deleted_count": deleted_count, "test_order_ids": test_order_ids})
            else:
                self.log_result("Bulk Delete Orders (Test IDs)", False, 
                              f"Failed to bulk delete orders: {response.status_code}", 
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Bulk Delete Orders (Test IDs)", False, f"Error bulk deleting orders: {str(e)}")
    
    def test_bulk_delete_validation(self):
        """Test bulk delete validation with empty order IDs"""
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/orders/bulk-delete", json={
                "order_ids": []
            })
            
            if response.status_code == 400:
                self.log_result("Bulk Delete Validation", True, 
                              "Correctly rejected empty order IDs with 400 error")
            else:
                self.log_result("Bulk Delete Validation", False, 
                              f"Expected 400 error for empty order IDs, got {response.status_code}", 
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Bulk Delete Validation", False, f"Error testing validation: {str(e)}")
    
    def test_admin_authentication_required(self):
        """Test that admin authentication is required for bulk operations"""
        # Remove auth header temporarily
        original_auth = self.session.headers.get("Authorization")
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        
        try:
            # Test bulk update without auth
            response = self.session.post(f"{BACKEND_URL}/admin/orders/bulk-update", json={
                "order_ids": ["test-id"],
                "status": "completed"
            })
            
            if response.status_code in [401, 403]:
                self.log_result("Admin Auth Required", True, 
                              f"Correctly blocked unauthenticated request with {response.status_code}")
            else:
                self.log_result("Admin Auth Required", False, 
                              f"Expected 401/403 for unauthenticated request, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Admin Auth Required", False, f"Error testing auth requirement: {str(e)}")
        finally:
            # Restore auth header
            if original_auth:
                self.session.headers["Authorization"] = original_auth
    
    def run_all_tests(self):
        """Run all bulk order management tests"""
        print("=" * 60)
        print("BULK ORDER MANAGEMENT ENDPOINTS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}")
        print("-" * 60)
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test admin authentication requirement
        self.test_admin_authentication_required()
        
        # Step 3: Test GET admin orders
        order_ids = self.test_get_admin_orders()
        
        # Step 4: Test bulk update validation
        self.test_bulk_update_validation()
        
        # Step 5: Test bulk update functionality
        self.test_bulk_update_orders(order_ids)
        
        # Step 6: Test bulk delete validation
        self.test_bulk_delete_validation()
        
        # Step 7: Test bulk delete functionality (with test IDs)
        self.test_bulk_delete_orders(order_ids)
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
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