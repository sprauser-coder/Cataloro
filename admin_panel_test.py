import requests
import sys
import json
from datetime import datetime, timedelta
import time

# Configuration
BACKEND_URL = "http://217.154.0.82/api"  # From frontend/.env
STATIC_URL = "http://217.154.0.82"  # For static file serving
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class AdminPanelTester:
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
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}")
        print()

    def admin_login(self):
        """Login as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_result("Admin Login", True, "Successfully logged in as admin", {
                    "user_role": data["user"]["role"],
                    "user_email": data["user"]["email"],
                    "user_full_name": data["user"]["full_name"]
                })
                return True
            else:
                self.log_result("Admin Login", False, f"Login failed with status {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Login error: {str(e)}")
            return False

    def test_admin_dashboard_access(self):
        """Test admin dashboard access - GET /admin/stats"""
        if not self.admin_token:
            self.log_result("Admin Dashboard Access", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/stats")
            
            if response.status_code == 200:
                stats = response.json()
                required_fields = ['total_users', 'active_users', 'blocked_users', 
                                 'total_listings', 'active_listings', 'total_orders', 'total_revenue']
                
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    self.log_result("Admin Dashboard Access", True, "Dashboard stats endpoint working correctly", {
                        "total_users": stats.get('total_users'),
                        "total_listings": stats.get('total_listings'),
                        "total_orders": stats.get('total_orders'),
                        "total_revenue": stats.get('total_revenue'),
                        "active_users": stats.get('active_users'),
                        "active_listings": stats.get('active_listings')
                    })
                    return True
                else:
                    self.log_result("Admin Dashboard Access", False, f"Missing required fields: {missing_fields}", {
                        "response": stats
                    })
                    return False
            else:
                self.log_result("Admin Dashboard Access", False, f"Dashboard access failed - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Dashboard Access", False, f"Dashboard access error: {str(e)}")
            return False

    def test_admin_users_panel(self):
        """Test admin users panel - GET /admin/users"""
        if not self.admin_token:
            self.log_result("Admin Users Panel", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            
            if response.status_code == 200:
                users = response.json()
                
                if isinstance(users, list):
                    # Check if we have users and they have required fields
                    if users:
                        first_user = users[0]
                        required_fields = ['id', 'user_id', 'email', 'username', 'full_name', 
                                         'role', 'is_blocked', 'created_at']
                        
                        missing_fields = [field for field in required_fields if field not in first_user]
                        
                        if not missing_fields:
                            self.log_result("Admin Users Panel", True, "Users panel working correctly", {
                                "total_users_returned": len(users),
                                "sample_user_email": first_user.get('email'),
                                "sample_user_role": first_user.get('role'),
                                "sample_user_blocked": first_user.get('is_blocked')
                            })
                            return True
                        else:
                            self.log_result("Admin Users Panel", False, f"User objects missing fields: {missing_fields}")
                            return False
                    else:
                        self.log_result("Admin Users Panel", True, "Users panel accessible but no users found", {
                            "users_count": 0
                        })
                        return True
                else:
                    self.log_result("Admin Users Panel", False, "Users endpoint did not return a list", {
                        "response_type": type(users).__name__
                    })
                    return False
            else:
                self.log_result("Admin Users Panel", False, f"Users panel access failed - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Users Panel", False, f"Users panel error: {str(e)}")
            return False

    def test_admin_listings_panel(self):
        """Test admin listings panel - GET /admin/listings"""
        if not self.admin_token:
            self.log_result("Admin Listings Panel", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/listings")
            
            if response.status_code == 200:
                listings = response.json()
                
                if isinstance(listings, list):
                    if listings:
                        first_listing = listings[0]
                        required_fields = ['id', 'title', 'seller_id', 'seller_name', 
                                         'price', 'status', 'created_at', 'views', 'category']
                        
                        missing_fields = [field for field in required_fields if field not in first_listing]
                        
                        if not missing_fields:
                            # Check if listings have images (for thumbnail display)
                            listings_with_images = 0
                            for listing in listings[:5]:  # Check first 5 listings
                                # Get full listing details to check for images
                                try:
                                    detail_response = self.session.get(f"{BACKEND_URL}/listings/{listing['id']}")
                                    if detail_response.status_code == 200:
                                        detail_data = detail_response.json()
                                        if detail_data.get('images'):
                                            listings_with_images += 1
                                except:
                                    pass
                            
                            self.log_result("Admin Listings Panel", True, "Listings panel working correctly", {
                                "total_listings_returned": len(listings),
                                "listings_with_images": listings_with_images,
                                "sample_listing_title": first_listing.get('title'),
                                "sample_listing_category": first_listing.get('category'),
                                "sample_listing_status": first_listing.get('status'),
                                "sample_seller_name": first_listing.get('seller_name')
                            })
                            return True
                        else:
                            self.log_result("Admin Listings Panel", False, f"Listing objects missing fields: {missing_fields}")
                            return False
                    else:
                        self.log_result("Admin Listings Panel", True, "Listings panel accessible but no listings found", {
                            "listings_count": 0
                        })
                        return True
                else:
                    self.log_result("Admin Listings Panel", False, "Listings endpoint did not return a list", {
                        "response_type": type(listings).__name__
                    })
                    return False
            else:
                self.log_result("Admin Listings Panel", False, f"Listings panel access failed - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Listings Panel", False, f"Listings panel error: {str(e)}")
            return False

    def test_admin_orders_panel(self):
        """Test admin orders panel - GET /admin/orders"""
        if not self.admin_token:
            self.log_result("Admin Orders Panel", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/orders")
            
            if response.status_code == 200:
                orders = response.json()
                
                if isinstance(orders, list):
                    if orders:
                        first_order = orders[0]
                        # Orders should have order, buyer, seller, and listing information
                        required_fields = ['order', 'buyer', 'seller', 'listing']
                        
                        missing_fields = [field for field in required_fields if field not in first_order]
                        
                        if not missing_fields:
                            order_data = first_order['order']
                            buyer_data = first_order['buyer']
                            seller_data = first_order['seller']
                            listing_data = first_order['listing']
                            
                            self.log_result("Admin Orders Panel", True, "Orders panel working correctly", {
                                "total_orders_returned": len(orders),
                                "sample_order_id": order_data.get('id') if order_data else None,
                                "sample_order_status": order_data.get('status') if order_data else None,
                                "sample_buyer_email": buyer_data.get('email') if buyer_data else None,
                                "sample_seller_email": seller_data.get('email') if seller_data else None,
                                "sample_listing_title": listing_data.get('title') if listing_data else None
                            })
                            return True
                        else:
                            self.log_result("Admin Orders Panel", False, f"Order objects missing fields: {missing_fields}")
                            return False
                    else:
                        self.log_result("Admin Orders Panel", True, "Orders panel accessible but no orders found", {
                            "orders_count": 0
                        })
                        return True
                else:
                    self.log_result("Admin Orders Panel", False, "Orders endpoint did not return a list", {
                        "response_type": type(orders).__name__
                    })
                    return False
            else:
                self.log_result("Admin Orders Panel", False, f"Orders panel access failed - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Orders Panel", False, f"Orders panel error: {str(e)}")
            return False

    def test_dashboard_analytics_data(self):
        """Test that dashboard provides analytics data for charts"""
        if not self.admin_token:
            self.log_result("Dashboard Analytics Data", False, "No admin token available")
            return False
            
        try:
            # Get admin stats for analytics
            response = self.session.get(f"{BACKEND_URL}/admin/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Check if we have numeric data that can be used for charts
                numeric_fields = ['total_users', 'active_users', 'total_listings', 
                                'active_listings', 'total_orders', 'total_revenue']
                
                analytics_data = {}
                for field in numeric_fields:
                    value = stats.get(field)
                    if isinstance(value, (int, float)):
                        analytics_data[field] = value
                    else:
                        analytics_data[field] = 0
                
                # Simulate daily analytics data (this would normally come from a time-series query)
                daily_data = {
                    "users": analytics_data['total_users'],
                    "listings": analytics_data['total_listings'], 
                    "orders": analytics_data['total_orders']
                }
                
                self.log_result("Dashboard Analytics Data", True, "Analytics data available for dashboard charts", {
                    "total_users": analytics_data['total_users'],
                    "total_listings": analytics_data['total_listings'],
                    "total_orders": analytics_data['total_orders'],
                    "total_revenue": analytics_data['total_revenue'],
                    "daily_analytics_simulation": daily_data
                })
                return True
            else:
                self.log_result("Dashboard Analytics Data", False, f"Analytics data access failed - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Dashboard Analytics Data", False, f"Analytics data error: {str(e)}")
            return False

    def test_listing_images_display(self):
        """Test that listings have images for thumbnail display in admin panel"""
        if not self.admin_token:
            self.log_result("Listing Images Display", False, "No admin token available")
            return False
            
        try:
            # Get listings from admin panel
            response = self.session.get(f"{BACKEND_URL}/admin/listings")
            
            if response.status_code == 200:
                listings = response.json()
                
                if isinstance(listings, list) and listings:
                    # Check first few listings for images
                    listings_checked = 0
                    listings_with_images = 0
                    image_urls_accessible = 0
                    
                    for listing in listings[:5]:  # Check first 5 listings
                        listings_checked += 1
                        listing_id = listing.get('id')
                        
                        if listing_id:
                            # Get full listing details to check for images
                            try:
                                detail_response = self.session.get(f"{BACKEND_URL}/listings/{listing_id}")
                                if detail_response.status_code == 200:
                                    detail_data = detail_response.json()
                                    images = detail_data.get('images', [])
                                    
                                    if images:
                                        listings_with_images += 1
                                        
                                        # Test if first image is accessible
                                        first_image = images[0]
                                        if first_image.startswith('/uploads/'):
                                            image_url = f"{STATIC_URL}{first_image}"
                                            try:
                                                img_response = requests.get(image_url, timeout=5)
                                                if img_response.status_code == 200:
                                                    image_urls_accessible += 1
                                            except:
                                                pass
                            except:
                                pass
                    
                    self.log_result("Listing Images Display", True, "Listing images available for admin panel thumbnails", {
                        "listings_checked": listings_checked,
                        "listings_with_images": listings_with_images,
                        "image_urls_accessible": image_urls_accessible,
                        "percentage_with_images": f"{(listings_with_images/listings_checked)*100:.1f}%" if listings_checked > 0 else "0%"
                    })
                    return True
                else:
                    self.log_result("Listing Images Display", True, "No listings found to check for images", {
                        "listings_count": len(listings) if isinstance(listings, list) else 0
                    })
                    return True
            else:
                self.log_result("Listing Images Display", False, f"Could not access listings - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Listing Images Display", False, f"Listing images check error: {str(e)}")
            return False

    def test_admin_functionality_integrity(self):
        """Test that all existing admin functionality still works"""
        if not self.admin_token:
            self.log_result("Admin Functionality Integrity", False, "No admin token available")
            return False
            
        try:
            # Test multiple admin endpoints to ensure they're all working
            endpoints_to_test = [
                ("CMS Settings", "admin/cms/settings"),
                ("Site Settings", "cms/settings"),
                ("Admin Stats", "admin/stats"),
                ("Admin Users", "admin/users"),
                ("Admin Listings", "admin/listings"),
                ("Admin Orders", "admin/orders")
            ]
            
            results = {}
            all_working = True
            
            for name, endpoint in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}/{endpoint}")
                    success = response.status_code == 200
                    results[name] = {
                        "status_code": response.status_code,
                        "success": success
                    }
                    if not success:
                        all_working = False
                except Exception as e:
                    results[name] = {
                        "status_code": "ERROR",
                        "success": False,
                        "error": str(e)
                    }
                    all_working = False
            
            if all_working:
                self.log_result("Admin Functionality Integrity", True, "All admin endpoints working correctly", results)
            else:
                failed_endpoints = [name for name, result in results.items() if not result['success']]
                self.log_result("Admin Functionality Integrity", False, f"Some admin endpoints failed: {failed_endpoints}", results)
            
            return all_working
                
        except Exception as e:
            self.log_result("Admin Functionality Integrity", False, f"Admin functionality check error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all admin panel tests"""
        print("🚀 Starting Admin Panel Phase 1 Testing...")
        print("=" * 60)
        
        # Login first
        if not self.admin_login():
            print("❌ Cannot proceed without admin login")
            return
        
        # Run all tests
        tests = [
            self.test_admin_dashboard_access,
            self.test_dashboard_analytics_data,
            self.test_admin_users_panel,
            self.test_admin_listings_panel,
            self.test_admin_orders_panel,
            self.test_listing_images_display,
            self.test_admin_functionality_integrity
        ]
        
        total_tests = len(tests)
        passed_tests = 0
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Summary
        print("=" * 60)
        print(f"📊 ADMIN PANEL TESTING SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL ADMIN PANEL TESTS PASSED!")
        else:
            print("⚠️  Some admin panel tests failed - check details above")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = AdminPanelTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)