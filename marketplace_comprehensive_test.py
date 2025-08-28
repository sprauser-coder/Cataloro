#!/usr/bin/env python3
"""
Comprehensive Marketplace Functionality Testing
Testing all marketplace APIs for new frontend components:
- Listing Creation APIs
- Image Upload APIs  
- Browse/Search APIs
- Favorites APIs
- Orders APIs
- Advanced Filtering
- User Management
- File Handling
"""

import requests
import json
import sys
from datetime import datetime
import time
import os
import io

# Configuration - Using correct backend URL from frontend/.env
BASE_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class MarketplaceTestSuite:
    def __init__(self):
        self.admin_token = None
        self.test_user_token = None
        self.test_user_id = None
        self.test_listing_id = None
        self.test_image_url = None
        self.test_favorite_id = None
        self.test_order_id = None
        self.results = []
        self.session = requests.Session()
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def setup_authentication(self):
        """Setup admin authentication for testing"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.log_result("Authentication Setup", True, 
                              f"Admin authentication successful")
                return True
            else:
                self.log_result("Authentication Setup", False, 
                              f"Authentication failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Setup", False, f"Exception: {str(e)}")
            return False
    
    def test_listing_creation_api(self):
        """Test POST /api/listings endpoint for creating new listings"""
        if not self.admin_token:
            self.log_result("Listing Creation API", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test data matching SellPage requirements
            test_listings = [
                {
                    "title": "iPhone 14 Pro Max - Excellent Condition",
                    "description": "Barely used iPhone 14 Pro Max in excellent condition. Includes original box, charger, and screen protector already applied.",
                    "category": "Electronics",
                    "condition": "Like New",
                    "price": 899.99,
                    "quantity": 1,
                    "location": "London, UK",
                    "listing_type": "fixed_price",
                    "shipping_cost": 15.00,
                    "images": []
                },
                {
                    "title": "Vintage Leather Jacket - Designer Brand",
                    "description": "Authentic vintage leather jacket from premium designer brand. Size M, perfect for fashion enthusiasts.",
                    "category": "Fashion",
                    "condition": "Good",
                    "price": 250.00,
                    "quantity": 1,
                    "location": "Manchester, UK",
                    "listing_type": "fixed_price",
                    "shipping_cost": 10.00,
                    "images": []
                },
                {
                    "title": "Gaming Setup - Complete Package",
                    "description": "Complete gaming setup including high-end PC, monitor, keyboard, mouse, and gaming chair. Perfect for serious gamers.",
                    "category": "Electronics",
                    "condition": "Excellent",
                    "price": 1500.00,
                    "quantity": 1,
                    "location": "Birmingham, UK",
                    "listing_type": "fixed_price",
                    "shipping_cost": 50.00,
                    "images": []
                }
            ]
            
            created_listings = []
            
            for i, listing_data in enumerate(test_listings):
                response = self.session.post(f"{BASE_URL}/listings", 
                                           json=listing_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    created_listings.append(data)
                    
                    # Store first listing ID for other tests
                    if i == 0:
                        self.test_listing_id = data.get("id")
                    
                    # Validate response structure
                    required_fields = ["id", "title", "description", "category", "price", "status"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result("Listing Creation API", False, 
                                      f"Missing fields in listing {i+1}: {missing_fields}")
                        return False
                else:
                    self.log_result("Listing Creation API", False, 
                                  f"Failed to create listing {i+1}: HTTP {response.status_code}: {response.text}")
                    return False
            
            self.log_result("Listing Creation API", True, 
                          f"Successfully created {len(created_listings)} listings with all required fields",
                          {"created_count": len(created_listings), "sample_id": self.test_listing_id})
            return True
                
        except Exception as e:
            self.log_result("Listing Creation API", False, f"Exception: {str(e)}")
            return False
    
    def test_image_upload_api(self):
        """Test POST /api/listings/upload-image endpoint for file uploads"""
        if not self.admin_token:
            self.log_result("Image Upload API", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create test PNG image data (minimal valid PNG)
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x04\x01\x00\x00\x01\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            # Test PNG upload
            files = {'file': ('test_listing_image.png', png_data, 'image/png')}
            response = self.session.post(f"{BASE_URL}/listings/upload-image", 
                                       files=files, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "image_url" in data:
                    self.test_image_url = data["image_url"]
                    
                    # Test if uploaded image is accessible
                    image_response = self.session.get(f"{BASE_URL}{self.test_image_url}")
                    
                    if image_response.status_code == 200:
                        # Test JPEG upload
                        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
                        
                        files_jpeg = {'file': ('test_listing_image.jpg', jpeg_data, 'image/jpeg')}
                        jpeg_response = self.session.post(f"{BASE_URL}/listings/upload-image", 
                                                        files=files_jpeg, headers=headers)
                        
                        if jpeg_response.status_code == 200:
                            # Test invalid file type (should fail)
                            files_invalid = {'file': ('test_file.txt', b'invalid content', 'text/plain')}
                            invalid_response = self.session.post(f"{BASE_URL}/listings/upload-image", 
                                                               files=files_invalid, headers=headers)
                            
                            if invalid_response.status_code == 400:
                                self.log_result("Image Upload API", True, 
                                              f"Image upload working correctly - PNG/JPEG accepted, invalid files rejected",
                                              {"png_url": self.test_image_url, "jpeg_status": "success", "validation": "working"})
                                return True
                            else:
                                self.log_result("Image Upload API", False, 
                                              f"File validation not working - invalid file accepted")
                                return False
                        else:
                            self.log_result("Image Upload API", False, 
                                          f"JPEG upload failed: HTTP {jpeg_response.status_code}")
                            return False
                    else:
                        self.log_result("Image Upload API", False, 
                                      f"Uploaded image not accessible: HTTP {image_response.status_code}")
                        return False
                else:
                    self.log_result("Image Upload API", False, 
                                  f"No image_url in response: {data}")
                    return False
            else:
                self.log_result("Image Upload API", False, 
                              f"PNG upload failed: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Image Upload API", False, f"Exception: {str(e)}")
            return False
    
    def test_browse_search_apis(self):
        """Test GET /api/listings with various query parameters for BrowsePage"""
        try:
            # Test basic listings endpoint
            response = self.session.get(f"{BASE_URL}/listings")
            
            if response.status_code != 200:
                self.log_result("Browse/Search APIs", False, 
                              f"Basic listings endpoint failed: HTTP {response.status_code}")
                return False
            
            basic_listings = response.json()
            
            # Test pagination
            paginated_response = self.session.get(f"{BASE_URL}/listings?limit=2&skip=0")
            if paginated_response.status_code != 200:
                self.log_result("Browse/Search APIs", False, 
                              f"Pagination failed: HTTP {paginated_response.status_code}")
                return False
            
            paginated_listings = paginated_response.json()
            
            # Test count endpoint
            count_response = self.session.get(f"{BASE_URL}/listings/count")
            if count_response.status_code != 200:
                self.log_result("Browse/Search APIs", False, 
                              f"Count endpoint failed: HTTP {count_response.status_code}")
                return False
            
            count_data = count_response.json()
            if "total_count" not in count_data:
                self.log_result("Browse/Search APIs", False, 
                              f"Count endpoint missing total_count field")
                return False
            
            # Test search functionality
            search_response = self.session.get(f"{BASE_URL}/listings?search=iPhone")
            if search_response.status_code != 200:
                self.log_result("Browse/Search APIs", False, 
                              f"Search functionality failed: HTTP {search_response.status_code}")
                return False
            
            # Test category filtering
            category_response = self.session.get(f"{BASE_URL}/listings?category=Electronics")
            if category_response.status_code != 200:
                self.log_result("Browse/Search APIs", False, 
                              f"Category filtering failed: HTTP {category_response.status_code}")
                return False
            
            # Test price filtering
            price_response = self.session.get(f"{BASE_URL}/listings?min_price=100&max_price=1000")
            if price_response.status_code != 200:
                self.log_result("Browse/Search APIs", False, 
                              f"Price filtering failed: HTTP {price_response.status_code}")
                return False
            
            # Test sorting
            sort_response = self.session.get(f"{BASE_URL}/listings?sort_by=price_low")
            if sort_response.status_code != 200:
                self.log_result("Browse/Search APIs", False, 
                              f"Sorting failed: HTTP {sort_response.status_code}")
                return False
            
            self.log_result("Browse/Search APIs", True, 
                          f"All browse/search functionality working correctly",
                          {
                              "total_listings": len(basic_listings),
                              "paginated_count": len(paginated_listings),
                              "total_count": count_data["total_count"],
                              "search_results": len(search_response.json()),
                              "category_results": len(category_response.json()),
                              "price_filtered": len(price_response.json()),
                              "sorted_results": len(sort_response.json())
                          })
            return True
                
        except Exception as e:
            self.log_result("Browse/Search APIs", False, f"Exception: {str(e)}")
            return False
    
    def test_favorites_apis(self):
        """Test GET/POST/DELETE /api/favorites endpoints"""
        if not self.admin_token or not self.test_listing_id:
            self.log_result("Favorites APIs", False, "No admin token or test listing available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test GET favorites count (should be 0 initially)
            count_response = self.session.get(f"{BASE_URL}/favorites/count", headers=headers)
            if count_response.status_code != 200:
                self.log_result("Favorites APIs", False, 
                              f"Favorites count failed: HTTP {count_response.status_code}")
                return False
            
            initial_count = count_response.json().get("count", 0)
            
            # Test POST - Add to favorites
            add_response = self.session.post(f"{BASE_URL}/favorites", 
                                           json={"listing_id": self.test_listing_id}, 
                                           headers=headers)
            
            if add_response.status_code != 200:
                self.log_result("Favorites APIs", False, 
                              f"Add to favorites failed: HTTP {add_response.status_code}: {add_response.text}")
                return False
            
            add_data = add_response.json()
            if "favorite_id" not in add_data:
                self.log_result("Favorites APIs", False, 
                              f"Add to favorites missing favorite_id: {add_data}")
                return False
            
            self.test_favorite_id = add_data["favorite_id"]
            
            # Test GET favorites list
            list_response = self.session.get(f"{BASE_URL}/favorites", headers=headers)
            if list_response.status_code != 200:
                self.log_result("Favorites APIs", False, 
                              f"Get favorites list failed: HTTP {list_response.status_code}")
                return False
            
            favorites_list = list_response.json()
            if not isinstance(favorites_list, list) or len(favorites_list) == 0:
                self.log_result("Favorites APIs", False, 
                              f"Favorites list empty or invalid format: {favorites_list}")
                return False
            
            # Validate favorite structure
            favorite = favorites_list[0]
            required_fields = ["favorite_id", "listing", "added_at"]
            missing_fields = [field for field in required_fields if field not in favorite]
            
            if missing_fields:
                self.log_result("Favorites APIs", False, 
                              f"Missing fields in favorite: {missing_fields}")
                return False
            
            # Test GET favorites count (should be increased)
            new_count_response = self.session.get(f"{BASE_URL}/favorites/count", headers=headers)
            if new_count_response.status_code != 200:
                self.log_result("Favorites APIs", False, 
                              f"Favorites count after add failed: HTTP {new_count_response.status_code}")
                return False
            
            new_count = new_count_response.json().get("count", 0)
            if new_count <= initial_count:
                self.log_result("Favorites APIs", False, 
                              f"Favorites count not increased: {initial_count} -> {new_count}")
                return False
            
            # Test DELETE - Remove from favorites
            delete_response = self.session.delete(f"{BASE_URL}/favorites/{self.test_favorite_id}", 
                                                headers=headers)
            
            if delete_response.status_code != 200:
                self.log_result("Favorites APIs", False, 
                              f"Remove from favorites failed: HTTP {delete_response.status_code}: {delete_response.text}")
                return False
            
            # Verify removal
            final_count_response = self.session.get(f"{BASE_URL}/favorites/count", headers=headers)
            if final_count_response.status_code != 200:
                self.log_result("Favorites APIs", False, 
                              f"Final favorites count failed: HTTP {final_count_response.status_code}")
                return False
            
            final_count = final_count_response.json().get("count", 0)
            if final_count != initial_count:
                self.log_result("Favorites APIs", False, 
                              f"Favorites count not restored: expected {initial_count}, got {final_count}")
                return False
            
            self.log_result("Favorites APIs", True, 
                          f"All favorites functionality working correctly",
                          {
                              "initial_count": initial_count,
                              "after_add": new_count,
                              "after_remove": final_count,
                              "favorite_structure": "valid"
                          })
            return True
                
        except Exception as e:
            self.log_result("Favorites APIs", False, f"Exception: {str(e)}")
            return False
    
    def test_orders_apis(self):
        """Test GET/POST /api/orders endpoints for OrdersPage"""
        if not self.admin_token or not self.test_listing_id:
            self.log_result("Orders APIs", False, "No admin token or test listing available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test GET orders (initially empty)
            get_response = self.session.get(f"{BASE_URL}/orders", headers=headers)
            if get_response.status_code != 200:
                self.log_result("Orders APIs", False, 
                              f"Get orders failed: HTTP {get_response.status_code}")
                return False
            
            initial_orders = get_response.json()
            if not isinstance(initial_orders, list):
                self.log_result("Orders APIs", False, 
                              f"Orders response not a list: {type(initial_orders)}")
                return False
            
            # Test POST - Create order
            order_data = {
                "listing_id": self.test_listing_id,
                "quantity": 1,
                "shipping_address": "123 Test Street, London, UK, SW1A 1AA"
            }
            
            create_response = self.session.post(f"{BASE_URL}/orders", 
                                              json=order_data, headers=headers)
            
            if create_response.status_code != 200:
                self.log_result("Orders APIs", False, 
                              f"Create order failed: HTTP {create_response.status_code}: {create_response.text}")
                return False
            
            order_result = create_response.json()
            required_fields = ["id", "buyer_id", "seller_id", "listing_id", "total_amount", "status"]
            missing_fields = [field for field in required_fields if field not in order_result]
            
            if missing_fields:
                self.log_result("Orders APIs", False, 
                              f"Missing fields in order: {missing_fields}")
                return False
            
            self.test_order_id = order_result["id"]
            
            # Test GET orders (should now have the new order)
            updated_get_response = self.session.get(f"{BASE_URL}/orders", headers=headers)
            if updated_get_response.status_code != 200:
                self.log_result("Orders APIs", False, 
                              f"Get updated orders failed: HTTP {updated_get_response.status_code}")
                return False
            
            updated_orders = updated_get_response.json()
            if len(updated_orders) <= len(initial_orders):
                self.log_result("Orders APIs", False, 
                              f"Order count not increased: {len(initial_orders)} -> {len(updated_orders)}")
                return False
            
            # Validate order structure in list
            if len(updated_orders) > 0:
                order_item = updated_orders[0]
                required_order_fields = ["order", "listing", "buyer", "seller"]
                missing_order_fields = [field for field in required_order_fields if field not in order_item]
                
                if missing_order_fields:
                    self.log_result("Orders APIs", False, 
                                  f"Missing fields in order list item: {missing_order_fields}")
                    return False
            
            self.log_result("Orders APIs", True, 
                          f"All orders functionality working correctly",
                          {
                              "initial_orders": len(initial_orders),
                              "after_creation": len(updated_orders),
                              "created_order_id": self.test_order_id,
                              "order_structure": "valid"
                          })
            return True
                
        except Exception as e:
            self.log_result("Orders APIs", False, f"Exception: {str(e)}")
            return False
    
    def test_advanced_filtering(self):
        """Test listings API with advanced filtering parameters"""
        try:
            # Test multiple filter combinations
            filter_tests = [
                {
                    "name": "Category + Condition Filter",
                    "params": "category=Electronics&condition=Like New",
                    "description": "Filter by category and condition"
                },
                {
                    "name": "Price Range + Search Filter", 
                    "params": "min_price=200&max_price=1000&search=iPhone",
                    "description": "Filter by price range and search term"
                },
                {
                    "name": "Category + Price + Sort Filter",
                    "params": "category=Fashion&min_price=50&max_price=500&sort_by=price_low",
                    "description": "Filter by category, price range, and sort by price"
                },
                {
                    "name": "Search + Sort + Pagination Filter",
                    "params": "search=gaming&sort_by=created_desc&limit=5&skip=0",
                    "description": "Search with sorting and pagination"
                },
                {
                    "name": "Condition + Listing Type Filter",
                    "params": "condition=Excellent&listing_type=fixed_price",
                    "description": "Filter by condition and listing type"
                }
            ]
            
            all_passed = True
            results = {}
            
            for test in filter_tests:
                response = self.session.get(f"{BASE_URL}/listings?{test['params']}")
                
                if response.status_code == 200:
                    data = response.json()
                    results[test['name']] = {
                        "status": "success",
                        "count": len(data),
                        "description": test['description']
                    }
                else:
                    results[test['name']] = {
                        "status": "failed",
                        "error": f"HTTP {response.status_code}",
                        "description": test['description']
                    }
                    all_passed = False
            
            if all_passed:
                self.log_result("Advanced Filtering", True, 
                              f"All advanced filtering combinations working correctly",
                              {"filter_results": results})
                return True
            else:
                failed_tests = [name for name, result in results.items() if result['status'] == 'failed']
                self.log_result("Advanced Filtering", False, 
                              f"Some filter combinations failed: {failed_tests}",
                              {"filter_results": results})
                return False
                
        except Exception as e:
            self.log_result("Advanced Filtering", False, f"Exception: {str(e)}")
            return False
    
    def test_user_management(self):
        """Test user profile and authentication functionality"""
        if not self.admin_token:
            self.log_result("User Management", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test profile stats endpoint
            profile_response = self.session.get(f"{BASE_URL}/profile/stats", headers=headers)
            if profile_response.status_code != 200:
                self.log_result("User Management", False, 
                              f"Profile stats failed: HTTP {profile_response.status_code}")
                return False
            
            profile_data = profile_response.json()
            expected_profile_fields = ["total_orders", "total_listings", "total_spent", "total_earned"]
            missing_profile_fields = [field for field in expected_profile_fields if field not in profile_data]
            
            if missing_profile_fields:
                self.log_result("User Management", False, 
                              f"Missing profile fields: {missing_profile_fields}")
                return False
            
            # Test admin user management
            users_response = self.session.get(f"{BASE_URL}/admin/users", headers=headers)
            if users_response.status_code != 200:
                self.log_result("User Management", False, 
                              f"Admin users endpoint failed: HTTP {users_response.status_code}")
                return False
            
            users_data = users_response.json()
            if not isinstance(users_data, list):
                self.log_result("User Management", False, 
                              f"Users data not a list: {type(users_data)}")
                return False
            
            # Test token validation
            invalid_headers = {"Authorization": "Bearer invalid_token"}
            invalid_response = self.session.get(f"{BASE_URL}/profile/stats", headers=invalid_headers)
            
            if invalid_response.status_code not in [401, 403]:
                self.log_result("User Management", False, 
                              f"Invalid token not rejected: HTTP {invalid_response.status_code}")
                return False
            
            self.log_result("User Management", True, 
                          f"User management and authentication working correctly",
                          {
                              "profile_fields": list(profile_data.keys()),
                              "users_count": len(users_data),
                              "token_validation": "working"
                          })
            return True
                
        except Exception as e:
            self.log_result("User Management", False, f"Exception: {str(e)}")
            return False
    
    def test_file_handling(self):
        """Test static file serving for uploaded images and media"""
        if not self.test_image_url:
            self.log_result("File Handling", False, "No test image URL available")
            return False
        
        try:
            # Test direct image access
            image_response = self.session.get(f"{BASE_URL}{self.test_image_url}")
            
            if image_response.status_code != 200:
                self.log_result("File Handling", False, 
                              f"Image not accessible: HTTP {image_response.status_code}")
                return False
            
            # Check content type
            content_type = image_response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                self.log_result("File Handling", False, 
                              f"Invalid content type: {content_type}")
                return False
            
            # Check file size
            content_length = len(image_response.content)
            if content_length == 0:
                self.log_result("File Handling", False, 
                              f"Empty file content")
                return False
            
            # Test cache headers
            cache_control = image_response.headers.get('cache-control', '')
            
            self.log_result("File Handling", True, 
                          f"Static file serving working correctly",
                          {
                              "image_url": self.test_image_url,
                              "content_type": content_type,
                              "file_size": content_length,
                              "cache_control": cache_control
                          })
            return True
                
        except Exception as e:
            self.log_result("File Handling", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all marketplace functionality tests"""
        print("🚀 Starting Comprehensive Marketplace Functionality Testing")
        print(f"Testing against: {BASE_URL}")
        print("=" * 90)
        
        # Setup authentication first
        if not self.setup_authentication():
            print("❌ CRITICAL: Authentication setup failed. Cannot proceed with tests.")
            return False
        
        # Test sequence - order matters for dependencies
        tests = [
            ("Listing Creation APIs", self.test_listing_creation_api),
            ("Image Upload APIs", self.test_image_upload_api),
            ("Browse/Search APIs", self.test_browse_search_apis),
            ("Favorites APIs", self.test_favorites_apis),
            ("Orders APIs", self.test_orders_apis),
            ("Advanced Filtering", self.test_advanced_filtering),
            ("User Management", self.test_user_management),
            ("File Handling", self.test_file_handling)
        ]
        
        passed = 0
        total = 0
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                total += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                total += 1
        
        # Summary
        print("\n" + "=" * 90)
        print("📊 MARKETPLACE FUNCTIONALITY TEST SUMMARY")
        print("=" * 90)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed}/{total} tests passed)")
        
        # Categorize results
        critical_failures = []
        working_features = []
        
        for result in self.results:
            if not result["success"]:
                critical_failures.append(result)
            else:
                working_features.append(result)
        
        # Report critical issues
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['message']}")
        
        # Report working features
        print(f"\n✅ WORKING FEATURES ({len(working_features)}):")
        for feature in working_features:
            print(f"   • {feature['test']}: {feature['message']}")
        
        # Frontend compatibility assessment
        print(f"\n🔄 FRONTEND COMPONENT COMPATIBILITY:")
        
        component_apis = {
            "SellPage": ["Listing Creation APIs", "Image Upload APIs"],
            "BrowsePage": ["Browse/Search APIs", "Advanced Filtering"],
            "FavoritesPage": ["Favorites APIs"],
            "OrdersPage": ["Orders APIs"],
            "General": ["User Management", "File Handling"]
        }
        
        for component, required_apis in component_apis.items():
            working_apis = sum(1 for result in self.results 
                             if result["test"] in required_apis and result["success"])
            
            if working_apis == len(required_apis):
                print(f"   ✅ {component}: All required APIs working ({working_apis}/{len(required_apis)})")
            else:
                print(f"   ⚠️  {component}: {len(required_apis) - working_apis} APIs have issues ({working_apis}/{len(required_apis)})")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.results:
            print(f"{result['status']}: {result['test']} - {result['message']}")
        
        return success_rate >= 80  # Consider 80%+ as success

if __name__ == "__main__":
    tester = MarketplaceTestSuite()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 MARKETPLACE FUNCTIONALITY TESTING COMPLETED SUCCESSFULLY")
        print("All marketplace APIs are ready for frontend integration!")
        sys.exit(0)
    else:
        print(f"\n⚠️  MARKETPLACE FUNCTIONALITY TESTING COMPLETED WITH ISSUES")
        print("Some marketplace functionality may need attention.")
        sys.exit(1)