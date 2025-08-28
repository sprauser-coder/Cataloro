#!/usr/bin/env python3
"""
Comprehensive Live Admin Panel Backend Testing
Testing all admin panel backend functionality as requested in the review.

Focus Areas:
1. Live Dashboard Functions
2. Live User Management  
3. Live Product Management
4. Live Order Management

Admin Credentials: admin@marketplace.com / admin123
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BASE_URL = "https://cataloro-hub.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ComprehensiveAdminTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", endpoint=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "endpoint": endpoint,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if endpoint:
            print(f"   Endpoint: {endpoint}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{self.base_url}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.admin_user_id = data["user"]["id"]
                self.log_test(
                    "Admin Authentication", 
                    True, 
                    f"Successfully authenticated as {data['user']['full_name']} (Role: {data['user']['role']})",
                    "POST /auth/login"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    "POST /auth/login"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}", "POST /auth/login")
            return False

    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}

    def test_dashboard_functions(self):
        """Test Live Dashboard Functions"""
        print("🔍 TESTING LIVE DASHBOARD FUNCTIONS")
        print("=" * 50)
        
        # Test 1: GET /api/admin/stats (for live dashboard data)
        try:
            response = requests.get(f"{self.base_url}/admin/stats", headers=self.get_headers())
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_users", "active_users", "total_listings", "active_listings", "total_orders", "total_revenue"]
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    self.log_test(
                        "Dashboard Stats Endpoint", 
                        True, 
                        f"Retrieved complete stats: Users={stats['total_users']}, Listings={stats['total_listings']}, Orders={stats['total_orders']}, Revenue=€{stats['total_revenue']:.2f}",
                        "GET /admin/stats"
                    )
                else:
                    self.log_test(
                        "Dashboard Stats Endpoint", 
                        False, 
                        f"Missing required fields: {missing_fields}",
                        "GET /admin/stats"
                    )
            else:
                self.log_test(
                    "Dashboard Stats Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    "GET /admin/stats"
                )
        except Exception as e:
            self.log_test("Dashboard Stats Endpoint", False, f"Exception: {str(e)}", "GET /admin/stats")

        # Test 2: POST /api/admin/system/clear-cache (dashboard action)
        try:
            response = requests.post(f"{self.base_url}/admin/system/clear-cache", headers=self.get_headers())
            if response.status_code == 200:
                self.log_test(
                    "Clear Cache System Action", 
                    True, 
                    "Cache cleared successfully",
                    "POST /admin/system/clear-cache"
                )
            elif response.status_code == 404:
                self.log_test(
                    "Clear Cache System Action", 
                    False, 
                    "Endpoint not implemented - missing from backend",
                    "POST /admin/system/clear-cache"
                )
            else:
                self.log_test(
                    "Clear Cache System Action", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    "POST /admin/system/clear-cache"
                )
        except Exception as e:
            self.log_test("Clear Cache System Action", False, f"Exception: {str(e)}", "POST /admin/system/clear-cache")

        # Test 3: POST /api/admin/system/backup (dashboard action)
        try:
            response = requests.post(f"{self.base_url}/admin/system/backup", headers=self.get_headers())
            if response.status_code == 200:
                self.log_test(
                    "System Backup Action", 
                    True, 
                    "Backup created successfully",
                    "POST /admin/system/backup"
                )
            elif response.status_code == 404:
                self.log_test(
                    "System Backup Action", 
                    False, 
                    "Endpoint not implemented - missing from backend",
                    "POST /admin/system/backup"
                )
            else:
                self.log_test(
                    "System Backup Action", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    "POST /admin/system/backup"
                )
        except Exception as e:
            self.log_test("System Backup Action", False, f"Exception: {str(e)}", "POST /admin/system/backup")

    def test_user_management(self):
        """Test Live User Management"""
        print("👥 TESTING LIVE USER MANAGEMENT")
        print("=" * 50)
        
        # Test 1: GET /api/admin/users (fetch all users for live display)
        try:
            response = requests.get(f"{self.base_url}/admin/users", headers=self.get_headers())
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list) and len(users) > 0:
                    user_sample = users[0]
                    required_fields = ["id", "email", "username", "full_name", "role", "is_blocked"]
                    missing_fields = [field for field in required_fields if field not in user_sample]
                    
                    if not missing_fields:
                        self.log_test(
                            "Fetch All Users", 
                            True, 
                            f"Retrieved {len(users)} users with complete data",
                            "GET /admin/users"
                        )
                        
                        # Store a test user ID for further testing (non-admin user)
                        self.test_user_id = None
                        for user in users:
                            if user.get("role") != "admin":
                                self.test_user_id = user["id"]
                                break
                                
                    else:
                        self.log_test(
                            "Fetch All Users", 
                            False, 
                            f"Missing required fields in user data: {missing_fields}",
                            "GET /admin/users"
                        )
                else:
                    self.log_test(
                        "Fetch All Users", 
                        False, 
                        "No users returned or invalid response format",
                        "GET /admin/users"
                    )
            else:
                self.log_test(
                    "Fetch All Users", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    "GET /admin/users"
                )
        except Exception as e:
            self.log_test("Fetch All Users", False, f"Exception: {str(e)}", "GET /admin/users")

        # Test user management actions if we have a test user
        if hasattr(self, 'test_user_id') and self.test_user_id:
            
            # Test 2: PUT /api/admin/users/{user_id} (edit user functionality)
            try:
                # First get current user data
                response = requests.get(f"{self.base_url}/admin/users", headers=self.get_headers())
                if response.status_code == 200:
                    users = response.json()
                    test_user = next((u for u in users if u["id"] == self.test_user_id), None)
                    
                    if test_user:
                        # Try to update user (this endpoint might not exist, checking)
                        update_data = {"full_name": f"Updated {test_user['full_name']}"}
                        response = requests.put(
                            f"{self.base_url}/admin/users/{self.test_user_id}", 
                            headers=self.get_headers(),
                            json=update_data
                        )
                        
                        if response.status_code == 200:
                            self.log_test(
                                "Edit User Functionality", 
                                True, 
                                "User updated successfully",
                                f"PUT /admin/users/{self.test_user_id}"
                            )
                        elif response.status_code == 404:
                            self.log_test(
                                "Edit User Functionality", 
                                False, 
                                "Endpoint not implemented - missing from backend",
                                f"PUT /admin/users/{self.test_user_id}"
                            )
                        else:
                            self.log_test(
                                "Edit User Functionality", 
                                False, 
                                f"HTTP {response.status_code}: {response.text}",
                                f"PUT /admin/users/{self.test_user_id}"
                            )
            except Exception as e:
                self.log_test("Edit User Functionality", False, f"Exception: {str(e)}", f"PUT /admin/users/{self.test_user_id}")

            # Test 3: PUT /api/admin/users/{user_id}/block (live block action)
            try:
                response = requests.put(f"{self.base_url}/admin/users/{self.test_user_id}/block", headers=self.get_headers())
                if response.status_code == 200:
                    self.log_test(
                        "Block User Action", 
                        True, 
                        "User blocked successfully",
                        f"PUT /admin/users/{self.test_user_id}/block"
                    )
                else:
                    self.log_test(
                        "Block User Action", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"PUT /admin/users/{self.test_user_id}/block"
                    )
            except Exception as e:
                self.log_test("Block User Action", False, f"Exception: {str(e)}", f"PUT /admin/users/{self.test_user_id}/block")

            # Test 4: PUT /api/admin/users/{user_id}/unblock (live unblock action)
            try:
                response = requests.put(f"{self.base_url}/admin/users/{self.test_user_id}/unblock", headers=self.get_headers())
                if response.status_code == 200:
                    self.log_test(
                        "Unblock User Action", 
                        True, 
                        "User unblocked successfully",
                        f"PUT /admin/users/{self.test_user_id}/unblock"
                    )
                else:
                    self.log_test(
                        "Unblock User Action", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"PUT /admin/users/{self.test_user_id}/unblock"
                    )
            except Exception as e:
                self.log_test("Unblock User Action", False, f"Exception: {str(e)}", f"PUT /admin/users/{self.test_user_id}/unblock")

            # Test 5: DELETE /api/admin/users/{user_id} (live delete action)
            try:
                response = requests.delete(f"{self.base_url}/admin/users/{self.test_user_id}", headers=self.get_headers())
                if response.status_code == 200:
                    self.log_test(
                        "Delete User Action", 
                        True, 
                        "User deleted successfully",
                        f"DELETE /admin/users/{self.test_user_id}"
                    )
                elif response.status_code == 404:
                    self.log_test(
                        "Delete User Action", 
                        False, 
                        "Endpoint not implemented - missing from backend",
                        f"DELETE /admin/users/{self.test_user_id}"
                    )
                else:
                    self.log_test(
                        "Delete User Action", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"DELETE /admin/users/{self.test_user_id}"
                    )
            except Exception as e:
                self.log_test("Delete User Action", False, f"Exception: {str(e)}", f"DELETE /admin/users/{self.test_user_id}")

        # Test bulk operations
        # Test 6: POST /api/admin/users/bulk-block (bulk operations)
        try:
            test_user_ids = [self.test_user_id] if hasattr(self, 'test_user_id') and self.test_user_id else []
            response = requests.put(  # Note: backend uses PUT, not POST
                f"{self.base_url}/admin/users/bulk-block", 
                headers=self.get_headers(),
                json=test_user_ids
            )
            if response.status_code == 200:
                self.log_test(
                    "Bulk Block Users", 
                    True, 
                    "Bulk block operation successful",
                    "PUT /admin/users/bulk-block"
                )
            else:
                self.log_test(
                    "Bulk Block Users", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    "PUT /admin/users/bulk-block"
                )
        except Exception as e:
            self.log_test("Bulk Block Users", False, f"Exception: {str(e)}", "PUT /admin/users/bulk-block")

        # Test 7: POST /api/admin/users/bulk-unblock (bulk operations)
        try:
            test_user_ids = [self.test_user_id] if hasattr(self, 'test_user_id') and self.test_user_id else []
            response = requests.put(  # Note: backend uses PUT, not POST
                f"{self.base_url}/admin/users/bulk-unblock", 
                headers=self.get_headers(),
                json=test_user_ids
            )
            if response.status_code == 200:
                self.log_test(
                    "Bulk Unblock Users", 
                    True, 
                    "Bulk unblock operation successful",
                    "PUT /admin/users/bulk-unblock"
                )
            else:
                self.log_test(
                    "Bulk Unblock Users", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    "PUT /admin/users/bulk-unblock"
                )
        except Exception as e:
            self.log_test("Bulk Unblock Users", False, f"Exception: {str(e)}", "PUT /admin/users/bulk-unblock")

        # Test 8: POST /api/admin/users/bulk-delete (bulk operations)
        try:
            test_user_ids = [self.test_user_id] if hasattr(self, 'test_user_id') and self.test_user_id else []
            response = requests.delete(  # Note: backend uses DELETE, not POST
                f"{self.base_url}/admin/users/bulk-delete", 
                headers=self.get_headers(),
                json=test_user_ids
            )
            if response.status_code == 200:
                self.log_test(
                    "Bulk Delete Users", 
                    True, 
                    "Bulk delete operation successful",
                    "DELETE /admin/users/bulk-delete"
                )
            else:
                self.log_test(
                    "Bulk Delete Users", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    "DELETE /admin/users/bulk-delete"
                )
        except Exception as e:
            self.log_test("Bulk Delete Users", False, f"Exception: {str(e)}", "DELETE /admin/users/bulk-delete")

    def test_product_management(self):
        """Test Live Product Management"""
        print("📦 TESTING LIVE PRODUCT MANAGEMENT")
        print("=" * 50)
        
        # Test 1: GET /api/admin/listings (fetch all products)
        try:
            response = requests.get(f"{self.base_url}/admin/listings", headers=self.get_headers())
            if response.status_code == 200:
                listings = response.json()
                if isinstance(listings, list):
                    self.log_test(
                        "Fetch All Products", 
                        True, 
                        f"Retrieved {len(listings)} product listings",
                        "GET /admin/listings"
                    )
                    
                    # Store a test listing ID for further testing
                    self.test_listing_id = None
                    if len(listings) > 0:
                        self.test_listing_id = listings[0]["id"]
                        
                else:
                    self.log_test(
                        "Fetch All Products", 
                        False, 
                        "Invalid response format - expected list",
                        "GET /admin/listings"
                    )
            else:
                self.log_test(
                    "Fetch All Products", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    "GET /admin/listings"
                )
        except Exception as e:
            self.log_test("Fetch All Products", False, f"Exception: {str(e)}", "GET /admin/listings")

        # Test product management actions if we have a test listing
        if hasattr(self, 'test_listing_id') and self.test_listing_id:
            
            # Test 2: PUT /api/admin/listings/{product_id} (edit product functionality)
            try:
                update_data = {"status": "active"}
                response = requests.put(
                    f"{self.base_url}/admin/listings/{self.test_listing_id}", 
                    headers=self.get_headers(),
                    json=update_data
                )
                if response.status_code == 200:
                    self.log_test(
                        "Edit Product Functionality", 
                        True, 
                        "Product updated successfully",
                        f"PUT /admin/listings/{self.test_listing_id}"
                    )
                else:
                    self.log_test(
                        "Edit Product Functionality", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"PUT /admin/listings/{self.test_listing_id}"
                    )
            except Exception as e:
                self.log_test("Edit Product Functionality", False, f"Exception: {str(e)}", f"PUT /admin/listings/{self.test_listing_id}")

            # Test 3: GET /api/admin/listings/{product_id}/views (live view tracking)
            try:
                response = requests.get(f"{self.base_url}/admin/listings/{self.test_listing_id}/views", headers=self.get_headers())
                if response.status_code == 200:
                    self.log_test(
                        "Product View Tracking", 
                        True, 
                        "View tracking data retrieved successfully",
                        f"GET /admin/listings/{self.test_listing_id}/views"
                    )
                elif response.status_code == 404:
                    self.log_test(
                        "Product View Tracking", 
                        False, 
                        "Endpoint not implemented - missing from backend",
                        f"GET /admin/listings/{self.test_listing_id}/views"
                    )
                else:
                    self.log_test(
                        "Product View Tracking", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"GET /admin/listings/{self.test_listing_id}/views"
                    )
            except Exception as e:
                self.log_test("Product View Tracking", False, f"Exception: {str(e)}", f"GET /admin/listings/{self.test_listing_id}/views")

            # Test 4: PUT /api/admin/listings/{product_id}/approve (approve products)
            try:
                response = requests.put(f"{self.base_url}/admin/listings/{self.test_listing_id}/approve", headers=self.get_headers())
                if response.status_code == 200:
                    self.log_test(
                        "Approve Product", 
                        True, 
                        "Product approved successfully",
                        f"PUT /admin/listings/{self.test_listing_id}/approve"
                    )
                elif response.status_code == 404:
                    self.log_test(
                        "Approve Product", 
                        False, 
                        "Endpoint not implemented - missing from backend",
                        f"PUT /admin/listings/{self.test_listing_id}/approve"
                    )
                else:
                    self.log_test(
                        "Approve Product", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"PUT /admin/listings/{self.test_listing_id}/approve"
                    )
            except Exception as e:
                self.log_test("Approve Product", False, f"Exception: {str(e)}", f"PUT /admin/listings/{self.test_listing_id}/approve")

            # Test 5: PUT /api/admin/listings/{product_id}/feature (feature products)
            try:
                response = requests.put(f"{self.base_url}/admin/listings/{self.test_listing_id}/feature", headers=self.get_headers())
                if response.status_code == 200:
                    self.log_test(
                        "Feature Product", 
                        True, 
                        "Product featured successfully",
                        f"PUT /admin/listings/{self.test_listing_id}/feature"
                    )
                elif response.status_code == 404:
                    self.log_test(
                        "Feature Product", 
                        False, 
                        "Endpoint not implemented - missing from backend",
                        f"PUT /admin/listings/{self.test_listing_id}/feature"
                    )
                else:
                    self.log_test(
                        "Feature Product", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"PUT /admin/listings/{self.test_listing_id}/feature"
                    )
            except Exception as e:
                self.log_test("Feature Product", False, f"Exception: {str(e)}", f"PUT /admin/listings/{self.test_listing_id}/feature")

            # Test 6: DELETE /api/admin/listings/{product_id} (delete products)
            try:
                response = requests.delete(f"{self.base_url}/admin/listings/{self.test_listing_id}", headers=self.get_headers())
                if response.status_code == 200:
                    self.log_test(
                        "Delete Product", 
                        True, 
                        "Product deleted successfully",
                        f"DELETE /admin/listings/{self.test_listing_id}"
                    )
                else:
                    self.log_test(
                        "Delete Product", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"DELETE /admin/listings/{self.test_listing_id}"
                    )
            except Exception as e:
                self.log_test("Delete Product", False, f"Exception: {str(e)}", f"DELETE /admin/listings/{self.test_listing_id}")

    def test_order_management(self):
        """Test Live Order Management"""
        print("📋 TESTING LIVE ORDER MANAGEMENT")
        print("=" * 50)
        
        # Test 1: GET /api/admin/orders (fetch all orders)
        try:
            response = requests.get(f"{self.base_url}/admin/orders", headers=self.get_headers())
            if response.status_code == 200:
                orders = response.json()
                if isinstance(orders, list):
                    self.log_test(
                        "Fetch All Orders", 
                        True, 
                        f"Retrieved {len(orders)} orders",
                        "GET /admin/orders"
                    )
                    
                    # Store a test order ID for further testing
                    self.test_order_id = None
                    if len(orders) > 0:
                        self.test_order_id = orders[0]["id"]
                        
                else:
                    self.log_test(
                        "Fetch All Orders", 
                        False, 
                        "Invalid response format - expected list",
                        "GET /admin/orders"
                    )
            else:
                self.log_test(
                    "Fetch All Orders", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    "GET /admin/orders"
                )
        except Exception as e:
            self.log_test("Fetch All Orders", False, f"Exception: {str(e)}", "GET /admin/orders")

        # Test order management actions if we have a test order
        if hasattr(self, 'test_order_id') and self.test_order_id:
            
            # Test 2: PUT /api/admin/orders/{order_id}/status (update order status)
            try:
                update_data = {"status": "completed"}
                response = requests.put(
                    f"{self.base_url}/admin/orders/{self.test_order_id}/status", 
                    headers=self.get_headers(),
                    json=update_data
                )
                if response.status_code == 200:
                    self.log_test(
                        "Update Order Status", 
                        True, 
                        "Order status updated successfully",
                        f"PUT /admin/orders/{self.test_order_id}/status"
                    )
                elif response.status_code == 404:
                    self.log_test(
                        "Update Order Status", 
                        False, 
                        "Endpoint not implemented - missing from backend",
                        f"PUT /admin/orders/{self.test_order_id}/status"
                    )
                else:
                    self.log_test(
                        "Update Order Status", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"PUT /admin/orders/{self.test_order_id}/status"
                    )
            except Exception as e:
                self.log_test("Update Order Status", False, f"Exception: {str(e)}", f"PUT /admin/orders/{self.test_order_id}/status")

            # Test 3: PUT /api/admin/orders/{order_id}/cancel (cancel orders)
            try:
                response = requests.put(f"{self.base_url}/admin/orders/{self.test_order_id}/cancel", headers=self.get_headers())
                if response.status_code == 200:
                    self.log_test(
                        "Cancel Order", 
                        True, 
                        "Order cancelled successfully",
                        f"PUT /admin/orders/{self.test_order_id}/cancel"
                    )
                elif response.status_code == 404:
                    self.log_test(
                        "Cancel Order", 
                        False, 
                        "Endpoint not implemented - missing from backend",
                        f"PUT /admin/orders/{self.test_order_id}/cancel"
                    )
                else:
                    self.log_test(
                        "Cancel Order", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"PUT /admin/orders/{self.test_order_id}/cancel"
                    )
            except Exception as e:
                self.log_test("Cancel Order", False, f"Exception: {str(e)}", f"PUT /admin/orders/{self.test_order_id}/cancel")

            # Test 4: POST /api/admin/orders/{order_id}/refund (refund orders)
            try:
                refund_data = {"amount": 50.00, "reason": "Test refund"}
                response = requests.post(
                    f"{self.base_url}/admin/orders/{self.test_order_id}/refund", 
                    headers=self.get_headers(),
                    json=refund_data
                )
                if response.status_code == 200:
                    self.log_test(
                        "Refund Order", 
                        True, 
                        "Order refunded successfully",
                        f"POST /admin/orders/{self.test_order_id}/refund"
                    )
                elif response.status_code == 404:
                    self.log_test(
                        "Refund Order", 
                        False, 
                        "Endpoint not implemented - missing from backend",
                        f"POST /admin/orders/{self.test_order_id}/refund"
                    )
                else:
                    self.log_test(
                        "Refund Order", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        f"POST /admin/orders/{self.test_order_id}/refund"
                    )
            except Exception as e:
                self.log_test("Refund Order", False, f"Exception: {str(e)}", f"POST /admin/orders/{self.test_order_id}/refund")

    def run_all_tests(self):
        """Run all admin panel tests"""
        print("🚀 COMPREHENSIVE LIVE ADMIN PANEL BACKEND TESTING")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Admin credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print("=" * 60)
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all test suites
        self.test_dashboard_functions()
        self.test_user_management()
        self.test_product_management()
        self.test_order_management()
        
        # Generate summary
        self.generate_summary()
        
        return True

    def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # List failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  • {result['test']} - {result['details']}")
            print()
        
        # List missing endpoints
        missing_endpoints = []
        for result in self.test_results:
            if "not implemented" in result["details"].lower() or "missing from backend" in result["details"].lower():
                missing_endpoints.append(result["endpoint"])
        
        if missing_endpoints:
            print("🚧 MISSING ENDPOINTS (Not Implemented in Backend):")
            for endpoint in missing_endpoints:
                print(f"  • {endpoint}")
            print()
        
        # Working endpoints
        working_endpoints = []
        for result in self.test_results:
            if "✅ PASS" in result["status"]:
                working_endpoints.append(result["endpoint"])
        
        if working_endpoints:
            print("✅ WORKING ENDPOINTS:")
            for endpoint in working_endpoints:
                print(f"  • {endpoint}")
            print()

if __name__ == "__main__":
    tester = ComprehensiveAdminTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 Admin panel backend testing completed!")
    else:
        print("💥 Admin panel backend testing failed!")
        sys.exit(1)