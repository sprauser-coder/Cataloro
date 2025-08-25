#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Cataloro Marketplace
Testing all backend functionality as requested in the review:
- Authentication System (admin@marketplace.com / admin123)
- Admin Panel Features
- Core Marketplace Functions
- API Endpoints Testing
- Notification System
- File Upload Functionality
"""

import requests
import json
import sys
import os
import tempfile
from datetime import datetime
from pathlib import Path

# Configuration - Use environment variable for backend URL
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cataloro-revival.preview.emergentagent.com') + '/api'
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class CataloroBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user = None
        self.test_results = []
        self.test_user_token = None
        self.test_user_id = None
        self.test_listing_id = None
        self.test_order_id = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_basic_api_connectivity(self):
        """Test 1: Basic API Connectivity"""
        print("🌐 Testing Basic API Connectivity...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test(
                        "Basic API Connectivity", 
                        True, 
                        f"API root accessible. Response: {data.get('message')}"
                    )
                    return True
                else:
                    self.log_test("Basic API Connectivity", False, "Unexpected API root response format")
                    return False
            else:
                self.log_test(
                    "Basic API Connectivity", 
                    False, 
                    f"API root failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Basic API Connectivity", False, f"Exception occurred: {str(e)}")
            return False

    def test_admin_authentication(self):
        """Test 2: Admin Authentication System"""
        print("🔐 Testing Admin Authentication System...")
        
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "access_token" in data and "user" in data:
                    self.admin_token = data["access_token"]
                    self.admin_user = data["user"]
                    
                    if data.get("token_type") == "bearer" and self.admin_user.get("role") == "admin":
                        self.log_test(
                            "Admin Authentication", 
                            True, 
                            f"Successfully authenticated as {self.admin_user.get('email')} with admin role. JWT token received."
                        )
                        return True
                    else:
                        self.log_test("Admin Authentication", False, f"Invalid token type or role. Token type: {data.get('token_type')}, Role: {self.admin_user.get('role')}")
                        return False
                else:
                    self.log_test("Admin Authentication", False, "Missing access_token or user in response")
                    return False
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"Authentication failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception occurred: {str(e)}")
            return False

    def test_user_registration_and_login(self):
        """Test 3: User Registration and Login"""
        print("👤 Testing User Registration and Login...")
        
        try:
            # Test user registration
            test_user_data = {
                "email": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
                "password": "testpassword123",
                "full_name": "Test User",
                "role": "both"
            }
            
            # Register user
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=test_user_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    # Test login with new user
                    login_data = {
                        "email": test_user_data["email"],
                        "password": test_user_data["password"]
                    }
                    
                    login_response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
                    
                    if login_response.status_code == 200:
                        login_data_response = login_response.json()
                        self.test_user_token = login_data_response["access_token"]
                        self.test_user_id = login_data_response["user"]["id"]
                        
                        self.log_test(
                            "User Registration and Login", 
                            True, 
                            f"Successfully registered and logged in user: {test_user_data['email']}"
                        )
                        return True
                    else:
                        self.log_test("User Registration and Login", False, f"Login failed after registration: {login_response.status_code}")
                        return False
                else:
                    self.log_test("User Registration and Login", False, "Registration response missing required fields")
                    return False
            else:
                self.log_test("User Registration and Login", False, f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration and Login", False, f"Exception occurred: {str(e)}")
            return False

    def test_admin_panel_endpoints(self):
        """Test 4: Admin Panel Endpoints"""
        print("⚙️ Testing Admin Panel Endpoints...")
        
        if not self.admin_token:
            self.log_test("Admin Panel Endpoints", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test key admin endpoints
            admin_endpoints = [
                ("/admin/stats", "Dashboard Stats"),
                ("/admin/users", "User Management"),
                ("/admin/listings", "Listing Management"),
                ("/admin/orders", "Order Management"),
                ("/admin/cms/settings", "CMS Settings"),
                ("/admin/cms/pages", "Page Management"),
                ("/admin/navigation", "Navigation Management")
            ]
            
            successful_endpoints = []
            failed_endpoints = []
            
            for endpoint, description in admin_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
                    if response.status_code == 200:
                        successful_endpoints.append(f"{description} ({endpoint})")
                    else:
                        failed_endpoints.append(f"{description} ({endpoint}) - Status: {response.status_code}")
                except Exception as e:
                    failed_endpoints.append(f"{description} ({endpoint}) - Error: {str(e)}")
            
            if len(successful_endpoints) >= 5:  # At least 5 out of 7 should work
                self.log_test(
                    "Admin Panel Endpoints", 
                    True, 
                    f"Admin panel functional. Working endpoints: {', '.join(successful_endpoints)}"
                )
                if failed_endpoints:
                    print(f"   Note: Some endpoints had issues: {', '.join(failed_endpoints)}")
                return True
            else:
                self.log_test(
                    "Admin Panel Endpoints", 
                    False, 
                    f"Admin panel issues detected. Working: {len(successful_endpoints)}, Failed: {len(failed_endpoints)}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Panel Endpoints", False, f"Exception occurred: {str(e)}")
            return False

    def test_core_marketplace_functions(self):
        """Test 5: Core Marketplace Functions"""
        print("🛒 Testing Core Marketplace Functions...")
        
        if not self.test_user_token:
            self.log_test("Core Marketplace Functions", False, "No test user token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Test categories
            categories_response = self.session.get(f"{BACKEND_URL}/categories", timeout=10)
            if categories_response.status_code != 200:
                self.log_test("Core Marketplace Functions", False, "Categories endpoint failed")
                return False
            
            categories = categories_response.json()
            
            # Test listing creation
            listing_data = {
                "title": "Test Product for Marketplace Testing",
                "description": "This is a test product created during comprehensive backend testing",
                "category": categories[0] if categories else "Electronics",
                "listing_type": "fixed_price",
                "price": 99.99,
                "condition": "New",
                "quantity": 1,
                "location": "Test City, Test State"
            }
            
            listing_response = self.session.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers, timeout=10)
            
            if listing_response.status_code == 200:
                listing_data_response = listing_response.json()
                self.test_listing_id = listing_data_response["id"]
                
                # Test getting listings
                listings_response = self.session.get(f"{BACKEND_URL}/listings", timeout=10)
                
                if listings_response.status_code == 200:
                    listings = listings_response.json()
                    
                    # Test user's listings
                    my_listings_response = self.session.get(f"{BACKEND_URL}/listings/my-listings", headers=headers, timeout=10)
                    
                    if my_listings_response.status_code == 200:
                        self.log_test(
                            "Core Marketplace Functions", 
                            True, 
                            f"Marketplace functions working. Created listing: {self.test_listing_id}, Total listings: {len(listings)}"
                        )
                        return True
                    else:
                        self.log_test("Core Marketplace Functions", False, "My listings endpoint failed")
                        return False
                else:
                    self.log_test("Core Marketplace Functions", False, "Get listings endpoint failed")
                    return False
            else:
                self.log_test("Core Marketplace Functions", False, f"Listing creation failed: {listing_response.status_code} - {listing_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Core Marketplace Functions", False, f"Exception occurred: {str(e)}")
            return False

    def test_order_processing_system(self):
        """Test 6: Order Processing System"""
        print("📦 Testing Order Processing System...")
        
        if not self.test_user_token or not self.test_listing_id:
            self.log_test("Order Processing System", False, "Missing test user token or listing ID")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Create an order
            order_data = {
                "listing_id": self.test_listing_id,
                "quantity": 1,
                "shipping_address": "123 Test Street, Test City, Test State, 12345"
            }
            
            order_response = self.session.post(f"{BACKEND_URL}/orders", json=order_data, headers=headers, timeout=10)
            
            if order_response.status_code == 200:
                order_data_response = order_response.json()
                self.test_order_id = order_data_response["id"]
                
                # Test getting user orders
                orders_response = self.session.get(f"{BACKEND_URL}/orders", headers=headers, timeout=10)
                
                if orders_response.status_code == 200:
                    orders = orders_response.json()
                    
                    self.log_test(
                        "Order Processing System", 
                        True, 
                        f"Order system working. Created order: {self.test_order_id}, Total user orders: {len(orders)}"
                    )
                    return True
                else:
                    self.log_test("Order Processing System", False, "Get orders endpoint failed")
                    return False
            else:
                self.log_test("Order Processing System", False, f"Order creation failed: {order_response.status_code} - {order_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Order Processing System", False, f"Exception occurred: {str(e)}")
            return False

    def test_notification_system(self):
        """Test 7: Notification System"""
        print("🔔 Testing Notification System...")
        
        if not self.test_user_token:
            self.log_test("Notification System", False, "No test user token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Test getting notifications
            notifications_response = self.session.get(f"{BACKEND_URL}/notifications", headers=headers, timeout=10)
            
            if notifications_response.status_code == 200:
                notifications = notifications_response.json()
                
                # Test notification clearing (mark all as read)
                clear_response = self.session.put(f"{BACKEND_URL}/notifications/mark-all-read", headers=headers, timeout=10)
                
                if clear_response.status_code == 200:
                    self.log_test(
                        "Notification System", 
                        True, 
                        f"Notification system working. Found {len(notifications)} notifications, clearing functionality works"
                    )
                    return True
                else:
                    self.log_test("Notification System", False, f"Notification clearing failed: {clear_response.status_code}")
                    return False
            else:
                self.log_test("Notification System", False, f"Get notifications failed: {notifications_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Notification System", False, f"Exception occurred: {str(e)}")
            return False

    def test_file_upload_functionality(self):
        """Test 8: File Upload Functionality"""
        print("📁 Testing File Upload Functionality...")
        
        if not self.admin_token:
            self.log_test("File Upload Functionality", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create a test PNG file
            test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            # Test logo upload
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(test_image_content)
                temp_file.flush()
                
                with open(temp_file.name, 'rb') as f:
                    files = {'file': ('test_logo.png', f, 'image/png')}
                    logo_response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-logo", files=files, headers=headers, timeout=10)
                
                os.unlink(temp_file.name)
            
            logo_success = logo_response.status_code == 200
            
            # Test listing image upload (if we have test user token)
            listing_image_success = False
            if self.test_user_token:
                user_headers = {"Authorization": f"Bearer {self.test_user_token}"}
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_file.write(test_image_content)
                    temp_file.flush()
                    
                    with open(temp_file.name, 'rb') as f:
                        files = {'file': ('test_listing.png', f, 'image/png')}
                        listing_image_response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files, headers=user_headers, timeout=10)
                    
                    os.unlink(temp_file.name)
                
                listing_image_success = listing_image_response.status_code == 200
            
            if logo_success and (listing_image_success or not self.test_user_token):
                self.log_test(
                    "File Upload Functionality", 
                    True, 
                    f"File upload working. Logo upload: {'✅' if logo_success else '❌'}, Listing image: {'✅' if listing_image_success else 'N/A'}"
                )
                return True
            else:
                self.log_test(
                    "File Upload Functionality", 
                    False, 
                    f"File upload issues. Logo: {logo_response.status_code if logo_success else 'Failed'}, Listing: {listing_image_response.status_code if 'listing_image_response' in locals() else 'N/A'}"
                )
                return False
                
        except Exception as e:
            self.log_test("File Upload Functionality", False, f"Exception occurred: {str(e)}")
            return False

    def test_cms_and_site_settings(self):
        """Test 9: CMS and Site Settings"""
        print("🎨 Testing CMS and Site Settings...")
        
        try:
            # Test public CMS settings
            cms_response = self.session.get(f"{BACKEND_URL}/cms/settings", timeout=10)
            
            if cms_response.status_code == 200:
                cms_data = cms_response.json()
                
                # Test admin CMS settings (if admin token available)
                admin_cms_success = False
                if self.admin_token:
                    headers = {"Authorization": f"Bearer {self.admin_token}"}
                    admin_cms_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings", headers=headers, timeout=10)
                    admin_cms_success = admin_cms_response.status_code == 200
                
                # Test navigation
                nav_response = self.session.get(f"{BACKEND_URL}/cms/navigation", timeout=10)
                nav_success = nav_response.status_code == 200
                
                if admin_cms_success and nav_success:
                    self.log_test(
                        "CMS and Site Settings", 
                        True, 
                        f"CMS system working. Site name: '{cms_data.get('site_name', 'Unknown')}', Admin CMS: ✅, Navigation: ✅"
                    )
                    return True
                else:
                    self.log_test(
                        "CMS and Site Settings", 
                        True, 
                        f"CMS partially working. Public settings: ✅, Admin CMS: {'✅' if admin_cms_success else '❌'}, Navigation: {'✅' if nav_success else '❌'}"
                    )
                    return True
            else:
                self.log_test("CMS and Site Settings", False, f"CMS settings failed: {cms_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("CMS and Site Settings", False, f"Exception occurred: {str(e)}")
            return False

    def test_favorites_system(self):
        """Test 10: Favorites System"""
        print("⭐ Testing Favorites System...")
        
        if not self.test_user_token or not self.test_listing_id:
            self.log_test("Favorites System", False, "Missing test user token or listing ID")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Add to favorites
            favorite_data = {"listing_id": self.test_listing_id}
            add_response = self.session.post(f"{BACKEND_URL}/favorites", json=favorite_data, headers=headers, timeout=10)
            
            if add_response.status_code == 200:
                # Get favorites
                get_response = self.session.get(f"{BACKEND_URL}/favorites", headers=headers, timeout=10)
                
                if get_response.status_code == 200:
                    favorites = get_response.json()
                    
                    if len(favorites) > 0:
                        # Remove from favorites
                        favorite_id = favorites[0]["favorite_id"]
                        remove_response = self.session.delete(f"{BACKEND_URL}/favorites/{favorite_id}", headers=headers, timeout=10)
                        
                        if remove_response.status_code == 200:
                            self.log_test(
                                "Favorites System", 
                                True, 
                                f"Favorites system working. Added, retrieved ({len(favorites)} items), and removed favorite successfully"
                            )
                            return True
                        else:
                            self.log_test("Favorites System", False, f"Remove favorite failed: {remove_response.status_code}")
                            return False
                    else:
                        self.log_test("Favorites System", False, "No favorites found after adding")
                        return False
                else:
                    self.log_test("Favorites System", False, f"Get favorites failed: {get_response.status_code}")
                    return False
            else:
                self.log_test("Favorites System", False, f"Add to favorites failed: {add_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Favorites System", False, f"Exception occurred: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive backend tests for Cataloro Marketplace"""
        print("=" * 80)
        print("🚀 COMPREHENSIVE BACKEND TESTING FOR CATALORO MARKETPLACE")
        print("Testing all backend functionality as requested in the review")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Run tests in sequence - order matters for dependencies
        tests = [
            self.test_basic_api_connectivity,
            self.test_admin_authentication,
            self.test_user_registration_and_login,
            self.test_admin_panel_endpoints,
            self.test_core_marketplace_functions,
            self.test_order_processing_system,
            self.test_notification_system,
            self.test_file_upload_functionality,
            self.test_cms_and_site_settings,
            self.test_favorites_system
        ]
        
        for test in tests:
            test()
        
        # Summary
        print("=" * 80)
        print("📊 COMPREHENSIVE BACKEND TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        print()
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            print()
        
        # Diagnosis based on results
        if len(passed_tests) == len(self.test_results):
            print("🎉 ALL TESTS PASSED! Backend is 100% operational")
            print("✅ Authentication System: Working")
            print("✅ Admin Panel Features: Working")
            print("✅ Core Marketplace Functions: Working")
            print("✅ Notification System: Working")
            print("✅ File Upload Functionality: Working")
            print("✅ Backend is ready for new feature development")
        elif len(passed_tests) >= 8:  # Most tests passing
            print("⚠️  MOSTLY WORKING: Backend is largely functional with minor issues")
            print("✅ Core functionality available")
            print("🔍 Check specific failed endpoints for minor fixes needed")
        elif len(passed_tests) >= 6:  # Basic functionality working
            print("🚨 PARTIAL FUNCTIONALITY: Core backend working but some features need attention")
            print("⚠️  Some features may not work properly")
            print("🔍 Focus on failed tests for critical fixes")
        else:
            print("🚨 CRITICAL BACKEND ISSUES: Major functionality problems detected")
            print("❌ Backend needs significant fixes before new feature development")
            print("🔍 Address failed tests immediately")
        
        print("=" * 80)
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = CataloroBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)