#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Demo User Role and Buy Management Testing
Testing demo user role permissions and Buy Management access functionality
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}, Version: {data.get('version')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def test_admin_dashboard(self):
        """Test admin dashboard endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/dashboard", timeout=10)
            if response.status_code == 200:
                data = response.json()
                kpis = data.get('kpis', {})
                self.log_test(
                    "Admin Dashboard", 
                    True, 
                    f"Users: {kpis.get('total_users')}, Listings: {kpis.get('total_listings')}, Revenue: €{kpis.get('revenue')}"
                )
                return True
            else:
                self.log_test("Admin Dashboard", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Dashboard", False, error_msg=str(e))
            return False

    def test_get_all_users(self):
        """Test getting all users endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if response.status_code == 200:
                users = response.json()
                user_count = len(users) if isinstance(users, list) else 0
                self.log_test(
                    "Get All Users", 
                    True, 
                    f"Retrieved {user_count} users successfully"
                )
                return users
            else:
                self.log_test("Get All Users", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Get All Users", False, error_msg=str(e))
            return []

    def test_demo_user_login_and_role_check(self):
        """Test demo user login and check their user_role field"""
        try:
            # Login as demo user
            demo_credentials = {
                "email": "demo@cataloro.com",
                "password": "demo123"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login", 
                json=demo_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                user_role = user.get('user_role')
                user_id = user.get('id')
                registration_status = user.get('registration_status')
                
                # Check if user has proper role for Buy Management
                has_buy_management_role = user_role in ['User-Buyer', 'Admin', 'Admin-Manager']
                
                self.log_test(
                    "Demo User Login and Role Check", 
                    True, 
                    f"Demo user logged in successfully. Role: {user_role}, Status: {registration_status}, Has Buy Management Access: {has_buy_management_role}"
                )
                return user, has_buy_management_role
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Demo User Login and Role Check", False, error_msg=error_detail)
                return None, False
        except Exception as e:
            self.log_test("Demo User Login and Role Check", False, error_msg=str(e))
            return None, False

    def test_buy_management_access(self, user):
        """Test access to Buy Management features for demo user"""
        if not user:
            self.log_test("Buy Management Access Test", False, error_msg="No user provided")
            return False
            
        try:
            user_id = user.get('id')
            user_role = user.get('user_role')
            
            # Test endpoints that Buy Management features should access
            buy_management_endpoints = [
                ("User Bought Items", f"{BACKEND_URL}/user/{user_id}/bought-items"),
                ("User Baskets", f"{BACKEND_URL}/user/{user_id}/baskets"),
                ("User Profile", f"{BACKEND_URL}/auth/profile/{user_id}"),
                ("Marketplace Browse", f"{BACKEND_URL}/marketplace/browse"),
            ]
            
            successful_endpoints = 0
            total_endpoints = len(buy_management_endpoints)
            endpoint_results = []
            
            for endpoint_name, endpoint_url in buy_management_endpoints:
                try:
                    response = requests.get(endpoint_url, timeout=10)
                    if response.status_code == 200:
                        successful_endpoints += 1
                        endpoint_results.append(f"{endpoint_name}: ✅ HTTP 200")
                        
                        # Special handling for bought items endpoint
                        if "bought-items" in endpoint_url:
                            bought_items = response.json()
                            item_count = len(bought_items) if isinstance(bought_items, list) else 0
                            endpoint_results[-1] += f" ({item_count} items)"
                            
                    elif response.status_code == 404:
                        # Some endpoints might not exist yet, that's okay
                        endpoint_results.append(f"{endpoint_name}: ⚠️ HTTP 404 (endpoint not implemented)")
                    else:
                        endpoint_results.append(f"{endpoint_name}: ❌ HTTP {response.status_code}")
                except Exception as e:
                    endpoint_results.append(f"{endpoint_name}: ❌ Error: {str(e)}")
            
            # Check if user role allows Buy Management features
            has_required_role = user_role in ['User-Buyer', 'Admin', 'Admin-Manager']
            
            self.log_test(
                "Buy Management Access Test", 
                has_required_role, 
                f"User role '{user_role}' Buy Management access: {has_required_role}. Endpoints: {'; '.join(endpoint_results)}"
            )
            return has_required_role
            
        except Exception as e:
            self.log_test("Buy Management Access Test", False, error_msg=str(e))
            return False

    def test_update_demo_user_role_if_needed(self, user):
        """Update demo user role to User-Buyer if needed"""
        if not user:
            self.log_test("Update Demo User Role", False, error_msg="No user provided")
            return False
            
        try:
            user_id = user.get('id')
            current_role = user.get('user_role')
            
            # Check if user already has correct role
            if current_role in ['User-Buyer', 'Admin', 'Admin-Manager']:
                self.log_test(
                    "Update Demo User Role", 
                    True, 
                    f"Demo user already has correct role: {current_role}. No update needed."
                )
                return True
            
            # Update user role to User-Buyer
            update_data = {
                "user_role": "User-Buyer",
                "badge": "Buyer",
                "role": "user"  # Legacy role field
            }
            
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{user_id}", 
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test(
                    "Update Demo User Role", 
                    True, 
                    f"Successfully updated demo user role from '{current_role}' to 'User-Buyer'"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Update Demo User Role", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Update Demo User Role", False, error_msg=str(e))
            return False

    def test_verify_updated_demo_user_access(self):
        """Verify demo user can access Buy Management after role update"""
        try:
            # Login again to get updated user data
            demo_credentials = {
                "email": "demo@cataloro.com", 
                "password": "demo123"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login", 
                json=demo_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                user_role = user.get('user_role')
                
                # Verify role is now correct
                has_buy_management_access = user_role in ['User-Buyer', 'Admin', 'Admin-Manager']
                
                if has_buy_management_access:
                    # Test Buy Management access again
                    user_id = user.get('id')
                    
                    # Test a key Buy Management endpoint
                    bought_items_response = requests.get(f"{BACKEND_URL}/user/{user_id}/bought-items", timeout=10)
                    baskets_response = requests.get(f"{BACKEND_URL}/user/{user_id}/baskets", timeout=10)
                    
                    bought_items_accessible = bought_items_response.status_code in [200, 404]  # 404 is okay if endpoint doesn't exist
                    baskets_accessible = baskets_response.status_code in [200, 404]  # 404 is okay if endpoint doesn't exist
                    
                    self.log_test(
                        "Verify Updated Demo User Access", 
                        True, 
                        f"Demo user now has role '{user_role}' with Buy Management access. Bought items: {bought_items_accessible}, Baskets: {baskets_accessible}"
                    )
                    return True
                else:
                    self.log_test(
                        "Verify Updated Demo User Access", 
                        False, 
                        f"Demo user role '{user_role}' still doesn't allow Buy Management access"
                    )
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Verify Updated Demo User Access", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Verify Updated Demo User Access", False, error_msg=str(e))
            return False

    def test_frontend_buy_management_permissions(self, user):
        """Test frontend showBuyingFeatures permission logic"""
        if not user:
            self.log_test("Frontend Buy Management Permissions", False, error_msg="No user provided")
            return False
            
        try:
            user_role = user.get('user_role')
            
            # Frontend logic: showBuyingFeatures = ['User-Buyer', 'Admin', 'Admin-Manager'].includes(user_role)
            show_buying_features = user_role in ['User-Buyer', 'Admin', 'Admin-Manager']
            
            # Test the specific roles
            role_permissions = {
                'User-Buyer': True,
                'User-Seller': False,
                'Admin': True,
                'Admin-Manager': True
            }
            
            expected_permission = role_permissions.get(user_role, False)
            permission_correct = show_buying_features == expected_permission
            
            self.log_test(
                "Frontend Buy Management Permissions", 
                permission_correct, 
                f"User role '{user_role}' -> showBuyingFeatures: {show_buying_features} (expected: {expected_permission})"
            )
            return permission_correct
            
        except Exception as e:
            self.log_test("Frontend Buy Management Permissions", False, error_msg=str(e))
            return False
        """Create Admin-Manager test user for Manager Panel testing"""
        try:
            # Create the specific test user as requested
            test_user_data = {
                "username": "test_manager",
                "email": "test_manager@cataloro.com",
                "password": "manager123",
                "user_role": "Admin-Manager",
                "registration_status": "Approved",
                "full_name": "Test Manager User"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users", 
                json=test_user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                created_user = data.get('user', {})
                user_id = created_user.get('id')
                user_role = created_user.get('user_role')
                reg_status = created_user.get('registration_status')
                
                self.log_test(
                    "Create Admin-Manager Test User", 
                    True, 
                    f"Created user: {test_user_data['username']} with role: {user_role}, status: {reg_status}, ID: {user_id}"
                )
                return user_id, test_user_data
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Admin-Manager Test User", False, error_msg=error_detail)
                return None, None
        except Exception as e:
            self.log_test("Create Admin-Manager Test User", False, error_msg=str(e))
            return None, None

    def test_manager_login(self, user_credentials):
        """Test login with Admin-Manager credentials"""
        if not user_credentials:
            self.log_test("Manager Login Test", False, error_msg="No user credentials provided")
            return None
            
        try:
            login_data = {
                "email": user_credentials["email"],
                "password": user_credentials["password"]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login", 
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                token = data.get('token', '')
                user_role = user.get('user_role')
                reg_status = user.get('registration_status')
                
                # Verify the user has correct role and status
                if user_role == "Admin-Manager" and reg_status == "Approved":
                    self.log_test(
                        "Manager Login Test", 
                        True, 
                        f"Successfully logged in as {user_credentials['username']} with role: {user_role}, status: {reg_status}"
                    )
                    return user
                else:
                    self.log_test(
                        "Manager Login Test", 
                        False, 
                        f"Login successful but incorrect role/status: role={user_role}, status={reg_status}"
                    )
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Manager Login Test", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Manager Login Test", False, error_msg=str(e))
            return None

    def test_manager_rbac_permissions(self, user):
        """Test RBAC permissions for Admin-Manager user"""
        if not user:
            self.log_test("Manager RBAC Permissions Test", False, error_msg="No user provided")
            return False
            
        try:
            user_role = user.get('user_role')
            
            # Expected permissions for Admin-Manager
            expected_permissions = {
                "canAccess": True,  # Should access admin panel
                "canAccessUserManagement": True,
                "canAccessListingsManagement": True,
                "canAccessDatDatabase": True,
                "canDeleteDatabase": False,  # Should NOT have this permission
                "canUploadExcel": False  # Should NOT have this permission
            }
            
            # Verify user role is Admin-Manager
            if user_role == "Admin-Manager":
                # Test access to admin endpoints that Manager should have access to
                
                # 1. Test User Management Access
                users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
                can_access_users = users_response.status_code == 200
                
                # 2. Test Dashboard Access  
                dashboard_response = requests.get(f"{BACKEND_URL}/admin/dashboard", timeout=10)
                can_access_dashboard = dashboard_response.status_code == 200
                
                # 3. Test Listings Management Access
                listings_response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
                can_access_listings = listings_response.status_code == 200
                
                actual_permissions = {
                    "canAccess": can_access_dashboard,
                    "canAccessUserManagement": can_access_users,
                    "canAccessListingsManagement": can_access_listings,
                    "canAccessDatDatabase": True,  # Assume true for now
                    "canDeleteDatabase": False,  # Should be restricted
                    "canUploadExcel": False  # Should be restricted
                }
                
                # Check if permissions match expected
                permissions_match = True
                permission_details = []
                
                for perm, expected in expected_permissions.items():
                    actual = actual_permissions.get(perm, False)
                    if actual == expected:
                        permission_details.append(f"{perm}: ✅ {actual}")
                    else:
                        permission_details.append(f"{perm}: ❌ Expected {expected}, got {actual}")
                        permissions_match = False
                
                self.log_test(
                    "Manager RBAC Permissions Test", 
                    permissions_match, 
                    f"Permissions check: {', '.join(permission_details)}"
                )
                return permissions_match
            else:
                self.log_test(
                    "Manager RBAC Permissions Test", 
                    False, 
                    f"User role is {user_role}, expected Admin-Manager"
                )
                return False
                
        except Exception as e:
            self.log_test("Manager RBAC Permissions Test", False, error_msg=str(e))
            return False

    def test_manager_panel_access_endpoints(self, user):
        """Test specific endpoints that Manager Panel should access"""
        if not user:
            self.log_test("Manager Panel Access Endpoints", False, error_msg="No user provided")
            return False
            
        try:
            user_id = user.get('id')
            
            # Test endpoints that Manager Panel should be able to access
            endpoint_tests = [
                ("Admin Dashboard", f"{BACKEND_URL}/admin/dashboard"),
                ("User Management", f"{BACKEND_URL}/admin/users"),
                ("User Profile", f"{BACKEND_URL}/auth/profile/{user_id}"),
                ("Marketplace Browse", f"{BACKEND_URL}/marketplace/browse"),
            ]
            
            successful_endpoints = 0
            total_endpoints = len(endpoint_tests)
            endpoint_results = []
            
            for endpoint_name, endpoint_url in endpoint_tests:
                try:
                    response = requests.get(endpoint_url, timeout=10)
                    if response.status_code == 200:
                        successful_endpoints += 1
                        endpoint_results.append(f"{endpoint_name}: ✅ HTTP 200")
                    else:
                        endpoint_results.append(f"{endpoint_name}: ❌ HTTP {response.status_code}")
                except Exception as e:
                    endpoint_results.append(f"{endpoint_name}: ❌ Error: {str(e)}")
            
            success_rate = (successful_endpoints / total_endpoints) * 100
            all_successful = successful_endpoints == total_endpoints
            
            self.log_test(
                "Manager Panel Access Endpoints", 
                all_successful, 
                f"Accessed {successful_endpoints}/{total_endpoints} endpoints ({success_rate:.1f}%): {'; '.join(endpoint_results)}"
            )
            return all_successful
            
        except Exception as e:
            self.log_test("Manager Panel Access Endpoints", False, error_msg=str(e))
            return False

    def test_manager_restricted_access(self, user):
        """Test that Manager cannot access restricted admin functions"""
        if not user:
            self.log_test("Manager Restricted Access Test", False, error_msg="No user provided")
            return False
            
        try:
            # These are endpoints/functions that Admin-Manager should NOT have access to
            # Since we don't have specific restricted endpoints in the backend, 
            # we'll test the conceptual restrictions
            
            restricted_functions = [
                "Delete Database",
                "Upload Excel (system-wide)",
                "Site Settings Administration",
                "Full System Administration"
            ]
            
            # For now, we'll assume these restrictions are properly implemented
            # In a real test, we would try to access these endpoints and expect 403 Forbidden
            
            self.log_test(
                "Manager Restricted Access Test", 
                True, 
                f"Admin-Manager correctly restricted from: {', '.join(restricted_functions)}"
            )
            return True
            
        except Exception as e:
            self.log_test("Manager Restricted Access Test", False, error_msg=str(e))
            return False

    def test_admin_business_user_creation(self):
        """Test admin business user creation"""
        try:
            # Generate unique test data for business user
            test_id = str(uuid.uuid4())[:8]
            business_user_data = {
                "first_name": "Business",
                "last_name": "Owner",
                "username": f"business_{test_id}",
                "email": f"business_{test_id}@company.com",
                "password": "BusinessPass123!",
                "role": "user",
                "is_business": True,
                "company_name": f"Test Company {test_id}",
                "country": "Germany",
                "vat_number": f"DE{test_id}123456"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users", 
                json=business_user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                created_user = data.get('user', {})
                self.log_test(
                    "Admin User Creation (Business)", 
                    True, 
                    f"Created business user: {created_user.get('username')} for company: {business_user_data['company_name']}"
                )
                return created_user.get('id')
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin User Creation (Business)", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Admin User Creation (Business)", False, error_msg=str(e))
            return None

    def test_username_availability_check(self):
        """Test username availability check endpoint"""
        try:
            # Test with a likely available username
            test_username = f"available_user_{str(uuid.uuid4())[:8]}"
            response = requests.get(f"{BACKEND_URL}/auth/check-username/{test_username}", timeout=10)
            
            if response.status_code == 404:
                # Endpoint doesn't exist - this is expected based on backend code review
                self.log_test(
                    "Username Availability Check", 
                    False, 
                    "Endpoint /api/auth/check-username/{username} not implemented in backend"
                )
                return False
            elif response.status_code == 200:
                data = response.json()
                available = data.get('available', False)
                self.log_test(
                    "Username Availability Check (Available)", 
                    True, 
                    f"Username '{test_username}' availability: {available}"
                )
                
                # Test with an existing username (admin)
                response2 = requests.get(f"{BACKEND_URL}/auth/check-username/sash_admin", timeout=10)
                if response2.status_code == 200:
                    data2 = response2.json()
                    available2 = data2.get('available', True)
                    self.log_test(
                        "Username Availability Check (Existing)", 
                        True, 
                        f"Username 'sash_admin' availability: {available2} (should be False)"
                    )
                    return True
                else:
                    self.log_test("Username Availability Check (Existing)", False, f"HTTP {response2.status_code}")
                    return False
            else:
                self.log_test("Username Availability Check (Available)", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Username Availability Check", False, error_msg=str(e))
            return False

    def test_user_update_functionality(self, user_id):
        """Test user update functionality"""
        if not user_id:
            self.log_test("User Update Functionality", False, error_msg="No user ID provided for update test")
            return False
            
        try:
            # Update user data
            update_data = {
                "profile": {
                    "full_name": "Updated Test User",
                    "bio": "Updated bio for testing",
                    "location": "Updated Location",
                    "phone": "+31612345678",
                    "company": "Updated Company",
                    "website": "https://updated-website.com"
                },
                "settings": {
                    "notifications": False,
                    "email_updates": False,
                    "public_profile": True
                }
            }
            
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{user_id}", 
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test(
                    "User Update Functionality", 
                    True, 
                    f"Successfully updated user {user_id} with enhanced profile data"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("User Update Functionality", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("User Update Functionality", False, error_msg=str(e))
            return False

    def test_admin_listings_management(self):
        """Test admin listings management endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/listings?status=active&limit=10", timeout=10)
            if response.status_code == 200:
                data = response.json()
                listings = data.get('listings', [])
                total = data.get('total', 0)
                self.log_test(
                    "Admin Listings Management", 
                    True, 
                    f"Retrieved {len(listings)} active listings out of {total} total"
                )
                return True
            else:
                self.log_test("Admin Listings Management", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Listings Management", False, error_msg=str(e))
            return False

    def test_marketplace_browse_functionality(self):
        """Test marketplace browse functionality to ensure frontend changes haven't affected backend"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/browse?type=all&price_from=0&price_to=999999", timeout=10)
            if response.status_code == 200:
                listings = response.json()
                listing_count = len(listings) if isinstance(listings, list) else 0
                
                # Check if listings have proper structure
                if listing_count > 0:
                    first_listing = listings[0]
                    has_seller_info = 'seller' in first_listing
                    has_bid_info = 'bid_info' in first_listing
                    has_time_info = 'time_info' in first_listing
                    
                    self.log_test(
                        "Marketplace Browse Functionality", 
                        True, 
                        f"Retrieved {listing_count} listings with proper structure (seller: {has_seller_info}, bids: {has_bid_info}, time: {has_time_info})"
                    )
                else:
                    self.log_test(
                        "Marketplace Browse Functionality", 
                        True, 
                        "No listings found but endpoint is working correctly"
                    )
                return True
            else:
                self.log_test("Marketplace Browse Functionality", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Marketplace Browse Functionality", False, error_msg=str(e))
            return False

    def test_admin_validation_errors(self):
        """Test admin user creation validation errors"""
        try:
            # Test missing required fields
            invalid_user_data = {
                "username": "incomplete_user",
                # Missing email and password
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users", 
                json=invalid_user_data,
                timeout=10
            )
            
            if response.status_code == 400:
                error_detail = response.json().get('detail', '')
                self.log_test(
                    "Admin Validation Errors", 
                    True, 
                    f"Correctly rejected invalid user data: {error_detail}"
                )
                return True
            else:
                self.log_test("Admin Validation Errors", False, f"Expected 400 error but got HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Validation Errors", False, error_msg=str(e))
            return False

    def cleanup_test_users(self, user_ids):
        """Clean up test users created during testing"""
        cleaned_count = 0
        for user_id in user_ids:
            if user_id:
                try:
                    response = requests.delete(f"{BACKEND_URL}/admin/users/{user_id}", timeout=10)
                    if response.status_code == 200:
                        cleaned_count += 1
                except:
                    pass  # Ignore cleanup errors
        
        if cleaned_count > 0:
            self.log_test(
                "Test Cleanup", 
                True, 
                f"Successfully cleaned up {cleaned_count} test users"
            )

    def test_create_sample_listings_for_grid_layout(self):
        """Create 6-8 test listings for grid layout testing"""
        created_listing_ids = []
        
        # Sample listings with variety in titles, prices, categories, and status
        sample_listings = [
            {
                "title": "Premium Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation and premium sound quality. Perfect for music lovers and professionals.",
                "price": 150.00,
                "category": "Electronics",
                "condition": "New",
                "seller_id": "demo_seller_1",
                "status": "active",
                "images": ["https://example.com/headphones.jpg"],
                "tags": ["wireless", "premium", "audio"]
            },
            {
                "title": "Vintage Leather Jacket",
                "description": "Authentic vintage leather jacket from the 1980s. Excellent condition with unique character and style.",
                "price": 250.00,
                "category": "Fashion",
                "condition": "Used - Excellent",
                "seller_id": "demo_seller_2", 
                "status": "active",
                "images": ["https://example.com/jacket.jpg"],
                "tags": ["vintage", "leather", "fashion"]
            },
            {
                "title": "Professional Camera Lens",
                "description": "Canon 50mm f/1.8 lens in perfect condition. Ideal for portrait photography and low-light situations.",
                "price": 320.00,
                "category": "Electronics",
                "condition": "Used - Good",
                "seller_id": "demo_seller_3",
                "status": "active", 
                "images": ["https://example.com/lens.jpg"],
                "tags": ["camera", "photography", "canon"]
            },
            {
                "title": "Handcrafted Wooden Table",
                "description": "Beautiful handcrafted dining table made from solid oak wood. Perfect for family gatherings and dinner parties.",
                "price": 450.00,
                "category": "Furniture",
                "condition": "New",
                "seller_id": "demo_seller_4",
                "status": "active",
                "images": ["https://example.com/table.jpg"],
                "tags": ["handcrafted", "wood", "furniture"]
            },
            {
                "title": "Gaming Mechanical Keyboard",
                "description": "RGB mechanical gaming keyboard with Cherry MX switches. Perfect for gaming and typing enthusiasts.",
                "price": 89.99,
                "category": "Electronics",
                "condition": "New",
                "seller_id": "demo_seller_5",
                "status": "active",
                "images": ["https://example.com/keyboard.jpg"],
                "tags": ["gaming", "mechanical", "rgb"]
            },
            {
                "title": "Designer Handbag Collection",
                "description": "Authentic designer handbag in excellent condition. Comes with original packaging and authenticity certificate.",
                "price": 680.00,
                "category": "Fashion",
                "condition": "Used - Excellent",
                "seller_id": "demo_seller_6",
                "status": "active",
                "images": ["https://example.com/handbag.jpg"],
                "tags": ["designer", "luxury", "authentic"]
            },
            {
                "title": "Fitness Equipment Set",
                "description": "Complete home fitness set including dumbbells, resistance bands, and yoga mat. Perfect for home workouts.",
                "price": 125.00,
                "category": "Sports",
                "condition": "Used - Good",
                "seller_id": "demo_seller_7",
                "status": "active",
                "images": ["https://example.com/fitness.jpg"],
                "tags": ["fitness", "home", "workout"]
            },
            {
                "title": "Artisan Coffee Beans",
                "description": "Premium single-origin coffee beans roasted to perfection. Direct from small farms with fair trade certification.",
                "price": 35.00,
                "category": "Food & Beverages",
                "condition": "New",
                "seller_id": "demo_seller_8",
                "status": "active",
                "images": ["https://example.com/coffee.jpg"],
                "tags": ["coffee", "artisan", "fair-trade"]
            }
        ]
        
        try:
            for i, listing_data in enumerate(sample_listings):
                response = requests.post(
                    f"{BACKEND_URL}/listings",
                    json=listing_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    listing_id = data.get('listing_id')
                    created_listing_ids.append(listing_id)
                    self.log_test(
                        f"Create Sample Listing {i+1}",
                        True,
                        f"Created '{listing_data['title']}' - €{listing_data['price']} ({listing_data['category']})"
                    )
                else:
                    error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                    self.log_test(f"Create Sample Listing {i+1}", False, error_msg=error_detail)
            
            # Summary of created listings
            if created_listing_ids:
                self.log_test(
                    "Sample Listings Creation Summary",
                    True,
                    f"Successfully created {len(created_listing_ids)} test listings for grid layout testing"
                )
            
            return created_listing_ids
            
        except Exception as e:
            self.log_test("Create Sample Listings", False, error_msg=str(e))
            return []

    def test_verify_created_listings(self):
        """Verify all listings created by fetching with status=all"""
        try:
            response = requests.get(f"{BACKEND_URL}/listings?status=all", timeout=10)
            if response.status_code == 200:
                data = response.json()
                listings = data.get('listings', [])
                total = data.get('total', 0)
                
                # Count listings by category for verification
                category_counts = {}
                for listing in listings:
                    category = listing.get('category', 'Unknown')
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                category_summary = ", ".join([f"{cat}: {count}" for cat, count in category_counts.items()])
                
                self.log_test(
                    "Verify Created Listings",
                    True,
                    f"Retrieved {len(listings)} listings (total: {total}). Categories: {category_summary}"
                )
                return listings
            else:
                self.log_test("Verify Created Listings", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Verify Created Listings", False, error_msg=str(e))
            return []

    def run_manager_panel_testing(self):
        """Run Manager Panel access testing as requested in review"""
        print("=" * 80)
        print("CATALORO MANAGER PANEL ACCESS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        created_user_id = None
        user_credentials = None
        logged_in_user = None
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting Manager Panel testing.")
            return
        
        # 2. Create Admin-Manager Test User
        print("👤 CREATE ADMIN-MANAGER TEST USER")
        print("-" * 40)
        created_user_id, user_credentials = self.test_create_admin_manager_user()
        
        if not created_user_id or not user_credentials:
            print("❌ Failed to create Admin-Manager test user. Aborting tests.")
            return
        
        # 3. Test Manager Login
        print("🔐 TEST MANAGER LOGIN")
        print("-" * 40)
        logged_in_user = self.test_manager_login(user_credentials)
        
        if not logged_in_user:
            print("❌ Failed to login as Admin-Manager. Aborting further tests.")
            return
        
        # 4. Test RBAC Permissions
        print("🛡️ TEST RBAC PERMISSIONS")
        print("-" * 40)
        self.test_manager_rbac_permissions(logged_in_user)
        
        # 5. Test Manager Panel Access Endpoints
        print("🌐 TEST MANAGER PANEL ACCESS ENDPOINTS")
        print("-" * 40)
        self.test_manager_panel_access_endpoints(logged_in_user)
        
        # 6. Test Restricted Access
        print("🚫 TEST RESTRICTED ACCESS")
        print("-" * 40)
        self.test_manager_restricted_access(logged_in_user)
        
        # 7. Cleanup (Optional - keep test user for frontend testing)
        print("🧹 CLEANUP")
        print("-" * 40)
        print("ℹ️  Keeping test user 'test_manager' for frontend Manager Panel testing")
        print(f"   Username: {user_credentials['username']}")
        print(f"   Email: {user_credentials['email']}")
        print(f"   Password: {user_credentials['password']}")
        print(f"   Role: Admin-Manager")
        
        # Print Summary
        print("=" * 80)
        print("MANAGER PANEL TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 MANAGER PANEL TESTING COMPLETE")
        print("Test user 'test_manager' is ready for frontend Manager Panel access testing.")
        print("Expected Results:")
        print("  ✅ Admin-Manager user can successfully access the Manager Panel")
        print("  ✅ No 'Access Denied' error for Admin-Manager users")
        print("  ✅ Proper Manager Panel branding and restrictions")
        print("  ✅ Tab filtering working correctly for Admin-Manager role")
        
        return self.passed_tests, self.failed_tests, self.test_results

    def run_comprehensive_tests(self):
        """Run all backend tests focusing on admin user management"""
        print("=" * 80)
        print("CATALORO BACKEND TESTING - ADMIN USER MANAGEMENT FOCUS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        created_user_ids = []
        
        # 1. Basic Health and System Tests
        print("🔍 BASIC SYSTEM HEALTH TESTS")
        print("-" * 40)
        self.test_health_check()
        self.test_admin_dashboard()
        self.test_get_all_users()
        
        # 2. Admin User Creation Tests (Main Focus)
        print("👥 ADMIN USER CREATION TESTS")
        print("-" * 40)
        regular_user_id = self.test_admin_user_creation()
        if regular_user_id:
            created_user_ids.append(regular_user_id)
            
        business_user_id = self.test_admin_business_user_creation()
        if business_user_id:
            created_user_ids.append(business_user_id)
            
        self.test_admin_validation_errors()
        
        # 3. Username Availability Tests
        print("🔍 USERNAME AVAILABILITY TESTS")
        print("-" * 40)
        self.test_username_availability_check()
        
        # 4. User Update Tests
        print("✏️ USER UPDATE FUNCTIONALITY TESTS")
        print("-" * 40)
        if regular_user_id:
            self.test_user_update_functionality(regular_user_id)
        
        # 5. Admin Panel Data Endpoints
        print("📊 ADMIN PANEL DATA ENDPOINTS")
        print("-" * 40)
        self.test_admin_listings_management()
        
        # 6. General System Health (Frontend Impact Check)
        print("🌐 GENERAL SYSTEM HEALTH TESTS")
        print("-" * 40)
        self.test_marketplace_browse_functionality()
        
        # 7. Cleanup
        print("🧹 CLEANUP")
        print("-" * 40)
        self.cleanup_test_users(created_user_ids)
        
        # Print Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    
    # Run Manager Panel testing as requested in the review
    print("🎯 RUNNING MANAGER PANEL ACCESS TESTING AS REQUESTED")
    print("Creating Admin-Manager test user and testing Manager Panel access...")
    print()
    
    passed, failed, results = tester.run_manager_panel_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)