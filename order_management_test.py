#!/usr/bin/env python3
"""
Order Management Testing
Testing the order management functionality including:
1. GET /api/admin/orders - Verify we can get existing orders
2. Bulk endpoints status check
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class OrderManagementTester:
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
                
                # Extract order IDs for analysis
                order_ids = []
                order_statuses = {}
                if orders:
                    for order_data in orders:
                        if isinstance(order_data, dict) and 'order' in order_data:
                            order_id = order_data['order']['id']
                            status = order_data['order']['status']
                            order_ids.append(order_id)
                            order_statuses[status] = order_statuses.get(status, 0) + 1
                        elif isinstance(order_data, dict) and 'id' in order_data:
                            order_ids.append(order_data['id'])
                
                self.log_result("GET Admin Orders", True, 
                              f"Successfully retrieved {order_count} orders", 
                              {"order_count": order_count, "status_breakdown": order_statuses, "sample_order_ids": order_ids[:3]})
                return order_ids
            else:
                self.log_result("GET Admin Orders", False, 
                              f"Failed to get orders: {response.status_code}", 
                              {"response": response.text})
                return []
                
        except Exception as e:
            self.log_result("GET Admin Orders", False, f"Error getting orders: {str(e)}")
            return []
    
    def test_admin_orders_with_filters(self):
        """Test GET /api/admin/orders with various filters"""
        filters_to_test = [
            ("status_filter=pending", "pending orders"),
            ("status_filter=completed", "completed orders"),
            ("time_frame=today", "today's orders"),
            ("time_frame=last_week", "last week's orders"),
        ]
        
        for filter_param, description in filters_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}/admin/orders?{filter_param}")
                
                if response.status_code == 200:
                    orders = response.json()
                    order_count = len(orders)
                    self.log_result(f"GET Admin Orders ({description})", True, 
                                  f"Successfully retrieved {order_count} {description}")
                else:
                    self.log_result(f"GET Admin Orders ({description})", False, 
                                  f"Failed to get {description}: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"GET Admin Orders ({description})", False, f"Error getting {description}: {str(e)}")
    
    def test_bulk_endpoints_availability(self):
        """Test if bulk endpoints are available"""
        bulk_endpoints = [
            ("POST", "/admin/orders/bulk-update", "Bulk Update Orders"),
            ("POST", "/admin/orders/bulk-delete", "Bulk Delete Orders")
        ]
        
        for method, endpoint, name in bulk_endpoints:
            try:
                # Test with empty payload to check if endpoint exists
                response = self.session.post(f"{BACKEND_URL}{endpoint}", json={
                    "order_ids": []
                })
                
                if response.status_code == 404:
                    self.log_result(f"{name} Endpoint Availability", False, 
                                  f"Endpoint {endpoint} not found (404)", 
                                  {"endpoint": endpoint, "method": method})
                elif response.status_code == 400:
                    # 400 means endpoint exists but validation failed (expected for empty order_ids)
                    self.log_result(f"{name} Endpoint Availability", True, 
                                  f"Endpoint {endpoint} exists and validates input correctly")
                else:
                    self.log_result(f"{name} Endpoint Availability", True, 
                                  f"Endpoint {endpoint} is available (status: {response.status_code})")
                    
            except Exception as e:
                self.log_result(f"{name} Endpoint Availability", False, f"Error testing {endpoint}: {str(e)}")
    
    def run_all_tests(self):
        """Run all order management tests"""
        print("=" * 60)
        print("ORDER MANAGEMENT ENDPOINTS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}")
        print("-" * 60)
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test GET admin orders (basic functionality)
        order_ids = self.test_get_admin_orders()
        
        # Step 3: Test GET admin orders with filters
        self.test_admin_orders_with_filters()
        
        # Step 4: Test bulk endpoints availability
        self.test_bulk_endpoints_availability()
        
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
    tester = OrderManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All order management tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()