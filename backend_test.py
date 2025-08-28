#!/usr/bin/env python3
"""
Phase 4 Marketplace Features Backend Testing Suite
Testing comprehensive backend support for new marketplace features including:
- Product Detail APIs
- Enhanced Listing APIs  
- User Profile APIs
- Order Management
- Notification System
- Search and Related Products
- Enhanced Favorites
- Advanced Authentication
- Statistics & Analytics
- File Management
"""

import requests
import json
import os
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://217.154.0.82')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class Phase4BackendTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.test_listing_id = None
        self.test_user_id = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                self.log_result("Admin Authentication", True, f"Token: {self.admin_token[:20]}...")
                return True
            else:
                self.log_result("Admin Authentication", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, error=str(e))
            return False

    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}

    def test_product_detail_apis(self):
        """Test Product Detail APIs - /api/listings/{id} endpoint"""
        print("=== Testing Product Detail APIs ===")
        
        # First get a listing ID to test with
        try:
            response = requests.get(f"{API_BASE}/listings?limit=1")
            if response.status_code == 200:
                listings = response.json()
                if listings:
                    self.test_listing_id = listings[0]["id"]
                    self.log_result("Get Listing ID for Testing", True, f"Using listing ID: {self.test_listing_id}")
                else:
                    self.log_result("Get Listing ID for Testing", False, error="No listings found")
                    return
            else:
                self.log_result("Get Listing ID for Testing", False, error=f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Get Listing ID for Testing", False, error=str(e))
            return

        # Test individual listing endpoint
        try:
            response = requests.get(f"{API_BASE}/listings/{self.test_listing_id}")
            if response.status_code == 200:
                listing = response.json()
                required_fields = ["id", "title", "description", "price", "category", "seller_id", "status", "views"]
                missing_fields = [field for field in required_fields if field not in listing]
                
                if not missing_fields:
                    self.log_result("Individual Listing Retrieval", True, 
                                  f"Retrieved listing: {listing['title']}, Views: {listing['views']}")
                else:
                    self.log_result("Individual Listing Retrieval", False, 
                                  error=f"Missing fields: {missing_fields}")
            else:
                self.log_result("Individual Listing Retrieval", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Individual Listing Retrieval", False, error=str(e))

        # Test listing bids endpoint
        try:
            response = requests.get(f"{API_BASE}/listings/{self.test_listing_id}/bids")
            if response.status_code == 200:
                bids = response.json()
                self.log_result("Listing Bids Retrieval", True, f"Retrieved {len(bids)} bids")
            else:
                self.log_result("Listing Bids Retrieval", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Listing Bids Retrieval", False, error=str(e))

    def test_enhanced_listing_apis(self):
        """Test Enhanced Listing APIs with exclude parameter and detailed information"""
        print("=== Testing Enhanced Listing APIs ===")
        
        # Test listings with pagination and filtering
        try:
            response = requests.get(f"{API_BASE}/listings", params={
                "limit": 10,
                "skip": 0,
                "sort_by": "created_desc"
            })
            if response.status_code == 200:
                listings = response.json()
                self.log_result("Enhanced Listings with Pagination", True, 
                              f"Retrieved {len(listings)} listings with pagination")
            else:
                self.log_result("Enhanced Listings with Pagination", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Enhanced Listings with Pagination", False, error=str(e))

        # Test listings count endpoint
        try:
            response = requests.get(f"{API_BASE}/listings/count")
            if response.status_code == 200:
                count_data = response.json()
                if "total_count" in count_data:
                    self.log_result("Listings Count Endpoint", True, 
                                  f"Total listings count: {count_data['total_count']}")
                else:
                    self.log_result("Listings Count Endpoint", False, 
                                  error="Missing total_count field")
            else:
                self.log_result("Listings Count Endpoint", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Listings Count Endpoint", False, error=str(e))

        # Test advanced filtering
        try:
            response = requests.get(f"{API_BASE}/listings", params={
                "category": "Electronics",
                "min_price": 10,
                "max_price": 1000,
                "condition": "New"
            })
            if response.status_code == 200:
                listings = response.json()
                self.log_result("Advanced Listing Filtering", True, 
                              f"Filtered listings: {len(listings)} results")
            else:
                self.log_result("Advanced Listing Filtering", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Advanced Listing Filtering", False, error=str(e))

        # Test related products functionality (exclude parameter)
        if self.test_listing_id:
            try:
                response = requests.get(f"{API_BASE}/listings", params={
                    "category": "Electronics",
                    "exclude": self.test_listing_id,
                    "limit": 5
                })
                if response.status_code == 200:
                    listings = response.json()
                    # Check if the excluded listing is not in results
                    excluded_found = any(listing["id"] == self.test_listing_id for listing in listings)
                    if not excluded_found:
                        self.log_result("Related Products (Exclude Parameter)", True, 
                                      f"Retrieved {len(listings)} related products, excluded listing not present")
                    else:
                        self.log_result("Related Products (Exclude Parameter)", False, 
                                      error="Excluded listing found in results")
                else:
                    self.log_result("Related Products (Exclude Parameter)", False, 
                                  error=f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Related Products (Exclude Parameter)", False, error=str(e))

    def test_user_profile_apis(self):
        """Test User Profile APIs for user information, statistics, settings"""
        print("=== Testing User Profile APIs ===")
        
        # Test profile stats endpoint
        try:
            response = requests.get(f"{API_BASE}/profile/stats", headers=self.get_headers())
            if response.status_code == 200:
                stats = response.json()
                expected_fields = ["total_orders", "total_listings", "total_spent", "total_earned"]
                missing_fields = [field for field in expected_fields if field not in stats]
                
                if not missing_fields:
                    self.log_result("Profile Statistics", True, 
                                  f"Orders: {stats['total_orders']}, Listings: {stats['total_listings']}, Earned: €{stats['total_earned']}")
                else:
                    self.log_result("Profile Statistics", False, 
                                  error=f"Missing fields: {missing_fields}")
            else:
                self.log_result("Profile Statistics", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Profile Statistics", False, error=str(e))

        # Test profile information endpoint
        try:
            response = requests.get(f"{API_BASE}/profile", headers=self.get_headers())
            if response.status_code == 200:
                profile = response.json()
                self.log_result("Profile Information", True, 
                              f"User: {profile.get('full_name', 'N/A')}, Role: {profile.get('role', 'N/A')}")
            else:
                self.log_result("Profile Information", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Profile Information", False, error=str(e))

        # Test profile update endpoint
        try:
            update_data = {
                "bio": "Updated bio for Phase 4 testing",
                "location": "Test Location",
                "website": "https://example.com"
            }
            response = requests.put(f"{API_BASE}/profile", 
                                  json=update_data, 
                                  headers=self.get_headers())
            if response.status_code == 200:
                self.log_result("Profile Update", True, "Profile updated successfully")
            else:
                self.log_result("Profile Update", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Profile Update", False, error=str(e))

        # Test user activity endpoint
        try:
            response = requests.get(f"{API_BASE}/profile/activity", headers=self.get_headers())
            if response.status_code == 200:
                activities = response.json()
                self.log_result("User Activity Timeline", True, 
                              f"Retrieved {len(activities)} activities")
            else:
                self.log_result("User Activity Timeline", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("User Activity Timeline", False, error=str(e))

    def test_order_management(self):
        """Test Order Management with buyer/seller details, order history, status tracking"""
        print("=== Testing Order Management ===")
        
        # Test orders endpoint with detailed information
        try:
            response = requests.get(f"{API_BASE}/orders", headers=self.get_headers())
            if response.status_code == 200:
                orders = response.json()
                if orders:
                    # Check if orders have detailed buyer/seller information
                    first_order = orders[0]
                    if "order" in first_order and "buyer" in first_order and "seller" in first_order:
                        self.log_result("Detailed Order Information", True, 
                                      f"Retrieved {len(orders)} orders with buyer/seller details")
                    else:
                        self.log_result("Detailed Order Information", False, 
                                      error="Orders missing detailed buyer/seller information")
                else:
                    self.log_result("Detailed Order Information", True, "No orders found (empty result)")
            else:
                self.log_result("Detailed Order Information", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Detailed Order Information", False, error=str(e))

        # Test profile orders endpoint
        try:
            response = requests.get(f"{API_BASE}/profile/orders", headers=self.get_headers())
            if response.status_code == 200:
                orders = response.json()
                self.log_result("Profile Orders Endpoint", True, 
                              f"Retrieved {len(orders)} user orders")
            else:
                self.log_result("Profile Orders Endpoint", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Profile Orders Endpoint", False, error=str(e))

        # Test admin orders with filtering
        try:
            response = requests.get(f"{API_BASE}/admin/orders", 
                                  params={"status": "all", "time_frame": "last_month"},
                                  headers=self.get_headers())
            if response.status_code == 200:
                orders = response.json()
                self.log_result("Admin Orders with Filtering", True, 
                              f"Retrieved {len(orders)} orders with filters")
            else:
                self.log_result("Admin Orders with Filtering", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Orders with Filtering", False, error=str(e))

    def test_notification_system(self):
        """Test Notification System endpoints for real-time updates"""
        print("=== Testing Notification System ===")
        
        # Test notifications endpoint
        try:
            response = requests.get(f"{API_BASE}/notifications", headers=self.get_headers())
            if response.status_code == 200:
                notifications = response.json()
                self.log_result("Notifications Retrieval", True, 
                              f"Retrieved {len(notifications)} notifications")
            else:
                self.log_result("Notifications Retrieval", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Notifications Retrieval", False, error=str(e))

        # Test unread notifications
        try:
            response = requests.get(f"{API_BASE}/notifications", 
                                  params={"unread_only": True},
                                  headers=self.get_headers())
            if response.status_code == 200:
                notifications = response.json()
                self.log_result("Unread Notifications", True, 
                              f"Retrieved {len(notifications)} unread notifications")
            else:
                self.log_result("Unread Notifications", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Unread Notifications", False, error=str(e))

        # Test notification count endpoint
        try:
            response = requests.get(f"{API_BASE}/notifications/count", headers=self.get_headers())
            if response.status_code == 200:
                count_data = response.json()
                self.log_result("Notification Count", True, 
                              f"Notification counts: {count_data}")
            else:
                self.log_result("Notification Count", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Notification Count", False, error=str(e))

    def test_enhanced_favorites(self):
        """Test Enhanced Favorites with detailed listing information"""
        print("=== Testing Enhanced Favorites ===")
        
        # Test favorites with detailed listing info
        try:
            response = requests.get(f"{API_BASE}/favorites", headers=self.get_headers())
            if response.status_code == 200:
                favorites = response.json()
                if favorites:
                    # Check if favorites include detailed listing information
                    first_favorite = favorites[0]
                    if "listing" in first_favorite and "favorite_id" in first_favorite:
                        listing = first_favorite["listing"]
                        required_fields = ["id", "title", "price", "category", "status"]
                        missing_fields = [field for field in required_fields if field not in listing]
                        
                        if not missing_fields:
                            self.log_result("Enhanced Favorites with Listing Details", True, 
                                          f"Retrieved {len(favorites)} favorites with complete listing info")
                        else:
                            self.log_result("Enhanced Favorites with Listing Details", False, 
                                          error=f"Listing missing fields: {missing_fields}")
                    else:
                        self.log_result("Enhanced Favorites with Listing Details", False, 
                                      error="Favorites missing detailed listing information")
                else:
                    self.log_result("Enhanced Favorites with Listing Details", True, 
                                  "No favorites found (empty result)")
            else:
                self.log_result("Enhanced Favorites with Listing Details", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Enhanced Favorites with Listing Details", False, error=str(e))

        # Test favorites count
        try:
            response = requests.get(f"{API_BASE}/favorites/count", headers=self.get_headers())
            if response.status_code == 200:
                count_data = response.json()
                self.log_result("Favorites Count", True, 
                              f"Favorites count: {count_data.get('count', 0)}")
            else:
                self.log_result("Favorites Count", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Favorites Count", False, error=str(e))

        # Test profile favorites endpoint
        try:
            response = requests.get(f"{API_BASE}/profile/favorites", headers=self.get_headers())
            if response.status_code == 200:
                favorites = response.json()
                self.log_result("Profile Favorites Endpoint", True, 
                              f"Retrieved {len(favorites)} favorites via profile endpoint")
            else:
                self.log_result("Profile Favorites Endpoint", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Profile Favorites Endpoint", False, error=str(e))

    def test_file_management(self):
        """Test File Management - avatar and image upload capabilities"""
        print("=== Testing File Management ===")
        
        # Test listing image upload endpoint
        try:
            # Create a small test PNG file
            test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            files = {'file': ('test.png', test_image_data, 'image/png')}
            response = requests.post(f"{API_BASE}/listings/upload-image", 
                                   files=files, 
                                   headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                if "image_url" in result:
                    self.log_result("Listing Image Upload", True, 
                                  f"Image uploaded: {result['image_url']}")
                else:
                    self.log_result("Listing Image Upload", False, 
                                  error="Missing image_url in response")
            else:
                self.log_result("Listing Image Upload", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Listing Image Upload", False, error=str(e))

        # Test profile picture upload endpoint
        try:
            test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            files = {'file': ('avatar.png', test_image_data, 'image/png')}
            response = requests.post(f"{API_BASE}/profile/upload-picture", 
                                   files=files, 
                                   headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                if "profile_picture_url" in result:
                    self.log_result("Profile Picture Upload", True, 
                                  f"Avatar uploaded: {result['profile_picture_url']}")
                else:
                    self.log_result("Profile Picture Upload", False, 
                                  error="Missing profile_picture_url in response")
            else:
                self.log_result("Profile Picture Upload", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Profile Picture Upload", False, error=str(e))

        # Test logo upload (admin functionality)
        try:
            test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            files = {'file': ('logo.png', test_image_data, 'image/png')}
            response = requests.post(f"{API_BASE}/admin/cms/upload-logo", 
                                   files=files, 
                                   headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                if "logo_url" in result:
                    self.log_result("Logo Upload (Admin)", True, 
                                  f"Logo uploaded: {result['logo_url']}")
                else:
                    self.log_result("Logo Upload (Admin)", False, 
                                  error="Missing logo_url in response")
            else:
                self.log_result("Logo Upload (Admin)", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Logo Upload (Admin)", False, error=str(e))

    def test_statistics_analytics(self):
        """Test Statistics & Analytics endpoints for user-specific data"""
        print("=== Testing Statistics & Analytics ===")
        
        # Test admin stats
        try:
            response = requests.get(f"{API_BASE}/admin/stats", headers=self.get_headers())
            if response.status_code == 200:
                stats = response.json()
                expected_fields = ["total_users", "active_users", "total_listings", "active_listings", "total_orders", "total_revenue"]
                missing_fields = [field for field in expected_fields if field not in stats]
                
                if not missing_fields:
                    self.log_result("Admin Statistics", True, 
                                  f"Users: {stats['total_users']}, Listings: {stats['total_listings']}, Revenue: €{stats['total_revenue']}")
                else:
                    self.log_result("Admin Statistics", False, 
                                  error=f"Missing fields: {missing_fields}")
            else:
                self.log_result("Admin Statistics", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Statistics", False, error=str(e))

        # Test user-specific statistics
        try:
            response = requests.get(f"{API_BASE}/profile/stats", headers=self.get_headers())
            if response.status_code == 200:
                stats = response.json()
                self.log_result("User-Specific Statistics", True, 
                              f"Personal stats retrieved successfully")
            else:
                self.log_result("User-Specific Statistics", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("User-Specific Statistics", False, error=str(e))

        # Test analytics endpoints
        try:
            response = requests.get(f"{API_BASE}/admin/analytics/overview", headers=self.get_headers())
            if response.status_code == 200:
                analytics = response.json()
                self.log_result("Analytics Overview", True, 
                              f"Analytics data retrieved")
            else:
                self.log_result("Analytics Overview", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Analytics Overview", False, error=str(e))

    def run_all_tests(self):
        """Run all Phase 4 marketplace feature tests"""
        print("🚀 Starting Phase 4 Marketplace Features Backend Testing")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Run all test suites
        self.test_product_detail_apis()
        self.test_enhanced_listing_apis()
        self.test_user_profile_apis()
        self.test_order_management()
        self.test_notification_system()
        self.test_enhanced_favorites()
        self.test_file_management()
        self.test_statistics_analytics()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📊 PHASE 4 MARKETPLACE FEATURES TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        print("\n" + "=" * 60)
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Phase 4 marketplace features are working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: Phase 4 marketplace features are mostly working well.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Phase 4 marketplace features have some issues.")
        else:
            print("❌ CRITICAL: Phase 4 marketplace features need significant work.")

if __name__ == "__main__":
    tester = Phase4BackendTester()
    tester.run_all_tests()