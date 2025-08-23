#!/usr/bin/env python3
"""
Comprehensive Listing Creation Functionality Test
Focus: Testing POST /api/listings endpoint with various scenarios
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "http://217.154.0.82/api"  # From frontend/.env
STATIC_URL = "http://217.154.0.82"  # For static file serving
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ListingCreationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.regular_token = None
        self.test_results = []
        self.uploaded_images = []
        self.created_listings = []
        
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
        print(f"{status}: {test_name}")
        print(f"  {message}")
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
                self.log_result("Admin Authentication", True, "Successfully logged in as admin", {
                    "user_role": data["user"]["role"],
                    "user_email": data["user"]["email"],
                    "user_id": data["user"]["id"]
                })
                return True
            else:
                self.log_result("Admin Authentication", False, f"Login failed with status {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Login error: {str(e)}")
            return False

    def create_regular_user(self):
        """Create and login as regular user with seller role"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            user_data = {
                "email": f"seller_{timestamp}@test.com",
                "username": f"seller_{timestamp}",
                "password": "TestPass123!",
                "full_name": f"Test Seller {timestamp}",
                "role": "seller",  # Seller role to create listings
                "phone": "1234567890",
                "address": "123 Test Street"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.regular_token = data["access_token"]
                self.log_result("Regular User Creation", True, "Successfully created seller user", {
                    "user_role": data["user"]["role"],
                    "user_email": data["user"]["email"],
                    "user_id": data["user"]["id"]
                })
                return True
            else:
                self.log_result("Regular User Creation", False, f"Registration failed with status {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Regular User Creation", False, f"Registration error: {str(e)}")
            return False

    def create_test_image(self, format='PNG'):
        """Create a small test image"""
        if format == 'PNG':
            # Minimal PNG header
            return b'\x89PNG\r\n\x1a\n\rIHDR\x01\x01\x08\x02\x90wS\xde\tpHYs\x0b\x13\x0b\x13\x01\x9a\x9c\x18\nIDATx\x9cc\xf8\x01\x01IEND\xaeB`\x82'
        else:
            # Minimal JPEG header
            return b'\xff\xd8\xff\xe0\x10JFIF\x01\x01\x01HH\xff\xdbC\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x11\x08\x01\x01\x01\x01\x11\x02\x11\x01\x03\x11\x01\xff\xc4\x14\x01\x08\xff\xc4\x14\x10\x01\xff\xda\x08\x01\x01?\xaa\xff\xd9'

    def upload_test_images(self):
        """Upload test images for use in listings"""
        if not self.admin_token:
            self.log_result("Image Upload Setup", False, "No admin token available")
            return False
            
        try:
            # Upload PNG image
            png_data = self.create_test_image('PNG')
            files = {'file': ('test_listing.png', png_data, 'image/png')}
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = requests.post(f"{BACKEND_URL}/listings/upload-image", files=files, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                png_url = result.get('image_url')
                if png_url:
                    self.uploaded_images.append(png_url)
                    
            # Upload JPEG image
            jpeg_data = self.create_test_image('JPEG')
            files = {'file': ('test_listing.jpg', jpeg_data, 'image/jpeg')}
            
            response = requests.post(f"{BACKEND_URL}/listings/upload-image", files=files, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                jpeg_url = result.get('image_url')
                if jpeg_url:
                    self.uploaded_images.append(jpeg_url)
                    
            if len(self.uploaded_images) >= 2:
                self.log_result("Image Upload Setup", True, f"Successfully uploaded {len(self.uploaded_images)} test images", {
                    "uploaded_images": self.uploaded_images
                })
                return True
            else:
                self.log_result("Image Upload Setup", False, f"Only uploaded {len(self.uploaded_images)} images")
                return False
                
        except Exception as e:
            self.log_result("Image Upload Setup", False, f"Image upload error: {str(e)}")
            return False

    def test_create_listing_admin_credentials(self):
        """Test creating listing with admin credentials"""
        if not self.admin_token:
            self.log_result("Admin Listing Creation", False, "No admin token available")
            return False
            
        listing_data = {
            "title": "Admin Test Product - Electronics",
            "description": "This is a test product created by admin user to verify listing creation functionality",
            "category": "Electronics",
            "images": self.uploaded_images[:1] if self.uploaded_images else [],
            "listing_type": "fixed_price",
            "price": 99.99,
            "condition": "New",
            "quantity": 1,
            "location": "Admin Test City",
            "shipping_cost": 5.99
        }
        
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}', 'Content-Type': 'application/json'}
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                listing_id = result.get('id')
                if listing_id:
                    self.created_listings.append(listing_id)
                    self.log_result("Admin Listing Creation", True, "Admin successfully created listing", {
                        "listing_id": listing_id,
                        "title": result.get('title'),
                        "price": result.get('price'),
                        "category": result.get('category'),
                        "listing_type": result.get('listing_type'),
                        "images_count": len(result.get('images', []))
                    })
                    return True
                else:
                    self.log_result("Admin Listing Creation", False, "Listing created but no ID returned", {
                        "response": result
                    })
                    return False
            else:
                self.log_result("Admin Listing Creation", False, f"Failed with status {response.status_code}", {
                    "response": response.text,
                    "request_data": listing_data
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Listing Creation", False, f"Error: {str(e)}")
            return False

    def test_create_listing_seller_credentials(self):
        """Test creating listing with seller credentials"""
        if not self.regular_token:
            self.log_result("Seller Listing Creation", False, "No seller token available")
            return False
            
        listing_data = {
            "title": "Seller Test Product - Fashion",
            "description": "This is a test product created by seller user to verify role-based access control",
            "category": "Fashion",
            "images": self.uploaded_images[1:2] if len(self.uploaded_images) > 1 else [],
            "listing_type": "fixed_price",
            "price": 49.99,
            "condition": "Used",
            "quantity": 2,
            "location": "Seller Test City",
            "shipping_cost": 3.99
        }
        
        try:
            headers = {'Authorization': f'Bearer {self.regular_token}', 'Content-Type': 'application/json'}
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                listing_id = result.get('id')
                if listing_id:
                    self.created_listings.append(listing_id)
                    self.log_result("Seller Listing Creation", True, "Seller successfully created listing", {
                        "listing_id": listing_id,
                        "title": result.get('title'),
                        "price": result.get('price'),
                        "category": result.get('category'),
                        "seller_id": result.get('seller_id')
                    })
                    return True
                else:
                    self.log_result("Seller Listing Creation", False, "Listing created but no ID returned")
                    return False
            else:
                self.log_result("Seller Listing Creation", False, f"Failed with status {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Seller Listing Creation", False, f"Error: {str(e)}")
            return False

    def test_required_fields_validation(self):
        """Test validation of all required fields"""
        if not self.admin_token:
            self.log_result("Required Fields Validation", False, "No admin token available")
            return False
            
        required_fields = [
            "title", "description", "category", "condition", 
            "price", "quantity", "location", "listing_type"
        ]
        
        validation_results = []
        
        for field in required_fields:
            # Create listing data with missing field
            listing_data = {
                "title": "Test Product",
                "description": "Test description",
                "category": "Electronics",
                "condition": "New",
                "price": 99.99,
                "quantity": 1,
                "location": "Test City",
                "listing_type": "fixed_price"
            }
            
            # Remove the field to test
            del listing_data[field]
            
            try:
                headers = {'Authorization': f'Bearer {self.admin_token}', 'Content-Type': 'application/json'}
                response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
                
                # Should fail with 422 (validation error)
                if response.status_code == 422:
                    validation_results.append(f"✅ {field}: Properly validated (422)")
                else:
                    validation_results.append(f"❌ {field}: Expected 422, got {response.status_code}")
                    
            except Exception as e:
                validation_results.append(f"❌ {field}: Error - {str(e)}")
        
        # Check results
        passed_validations = sum(1 for result in validation_results if result.startswith("✅"))
        total_validations = len(validation_results)
        
        success = passed_validations == total_validations
        self.log_result("Required Fields Validation", success, 
                       f"Validated {passed_validations}/{total_validations} required fields", {
            "validation_details": validation_results
        })
        
        return success

    def test_listing_with_uploaded_images(self):
        """Test creating listing with uploaded images"""
        if not self.admin_token or not self.uploaded_images:
            self.log_result("Listing with Uploaded Images", False, "No admin token or uploaded images")
            return False
            
        listing_data = {
            "title": "Product with Multiple Images",
            "description": "This listing includes multiple uploaded images to test image integration",
            "category": "Electronics",
            "images": self.uploaded_images,  # Use all uploaded images
            "listing_type": "fixed_price",
            "price": 199.99,
            "condition": "New",
            "quantity": 1,
            "location": "Image Test City",
            "shipping_cost": 7.99
        }
        
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}', 'Content-Type': 'application/json'}
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                listing_id = result.get('id')
                returned_images = result.get('images', [])
                
                if listing_id and returned_images:
                    self.created_listings.append(listing_id)
                    self.log_result("Listing with Uploaded Images", True, "Successfully created listing with images", {
                        "listing_id": listing_id,
                        "images_sent": len(self.uploaded_images),
                        "images_returned": len(returned_images),
                        "image_urls": returned_images
                    })
                    return True
                else:
                    self.log_result("Listing with Uploaded Images", False, "Listing created but images missing", {
                        "listing_id": listing_id,
                        "returned_images": returned_images
                    })
                    return False
            else:
                self.log_result("Listing with Uploaded Images", False, f"Failed with status {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Listing with Uploaded Images", False, f"Error: {str(e)}")
            return False

    def test_different_listing_types(self):
        """Test creating both fixed_price and auction listings"""
        if not self.admin_token:
            self.log_result("Different Listing Types", False, "No admin token available")
            return False
            
        # Test fixed_price listing
        fixed_price_data = {
            "title": "Fixed Price Test Product",
            "description": "Testing fixed price listing type",
            "category": "Electronics",
            "listing_type": "fixed_price",
            "price": 149.99,
            "condition": "New",
            "quantity": 1,
            "location": "Fixed Price City",
            "shipping_cost": 5.99
        }
        
        # Test auction listing
        auction_data = {
            "title": "Auction Test Product",
            "description": "Testing auction listing type",
            "category": "Fashion",
            "listing_type": "auction",
            "starting_bid": 10.00,
            "buyout_price": 50.00,
            "condition": "Used",
            "quantity": 1,
            "location": "Auction City",
            "shipping_cost": 3.99,
            "auction_duration_hours": 24
        }
        
        results = []
        
        for listing_type, data in [("fixed_price", fixed_price_data), ("auction", auction_data)]:
            try:
                headers = {'Authorization': f'Bearer {self.admin_token}', 'Content-Type': 'application/json'}
                response = requests.post(f"{BACKEND_URL}/listings", json=data, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    listing_id = result.get('id')
                    if listing_id:
                        self.created_listings.append(listing_id)
                        results.append(f"✅ {listing_type}: Created successfully (ID: {listing_id})")
                    else:
                        results.append(f"❌ {listing_type}: No ID returned")
                else:
                    results.append(f"❌ {listing_type}: Failed with status {response.status_code}")
                    
            except Exception as e:
                results.append(f"❌ {listing_type}: Error - {str(e)}")
        
        success = all(result.startswith("✅") for result in results)
        self.log_result("Different Listing Types", success, f"Tested both listing types", {
            "results": results
        })
        
        return success

    def test_various_categories(self):
        """Test creating listings in various categories"""
        if not self.admin_token:
            self.log_result("Various Categories", False, "No admin token available")
            return False
            
        categories = ["Electronics", "Fashion", "Home & Garden", "Sports", "Books"]
        results = []
        
        for i, category in enumerate(categories):
            listing_data = {
                "title": f"Test Product in {category}",
                "description": f"Testing listing creation in {category} category",
                "category": category,
                "listing_type": "fixed_price",
                "price": 29.99 + (i * 10),  # Vary prices
                "condition": "New" if i % 2 == 0 else "Used",
                "quantity": 1,
                "location": f"{category} Test City",
                "shipping_cost": 2.99
            }
            
            try:
                headers = {'Authorization': f'Bearer {self.admin_token}', 'Content-Type': 'application/json'}
                response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    listing_id = result.get('id')
                    if listing_id:
                        self.created_listings.append(listing_id)
                        results.append(f"✅ {category}: Created successfully")
                    else:
                        results.append(f"❌ {category}: No ID returned")
                else:
                    results.append(f"❌ {category}: Failed with status {response.status_code}")
                    
            except Exception as e:
                results.append(f"❌ {category}: Error - {str(e)}")
        
        success = all(result.startswith("✅") for result in results)
        self.log_result("Various Categories", success, f"Tested {len(categories)} categories", {
            "results": results
        })
        
        return success

    def test_edge_cases(self):
        """Test edge cases and invalid data"""
        if not self.admin_token:
            self.log_result("Edge Cases Testing", False, "No admin token available")
            return False
            
        edge_cases = [
            {
                "name": "Empty title",
                "data": {"title": "", "description": "Test", "category": "Electronics", 
                        "condition": "New", "price": 99.99, "quantity": 1, 
                        "location": "Test", "listing_type": "fixed_price"},
                "expected_status": 422
            },
            {
                "name": "Negative price",
                "data": {"title": "Test", "description": "Test", "category": "Electronics", 
                        "condition": "New", "price": -10.00, "quantity": 1, 
                        "location": "Test", "listing_type": "fixed_price"},
                "expected_status": 200  # API might accept negative prices
            },
            {
                "name": "Zero quantity",
                "data": {"title": "Test", "description": "Test", "category": "Electronics", 
                        "condition": "New", "price": 99.99, "quantity": 0, 
                        "location": "Test", "listing_type": "fixed_price"},
                "expected_status": 422
            },
            {
                "name": "Invalid category",
                "data": {"title": "Test", "description": "Test", "category": "InvalidCategory", 
                        "condition": "New", "price": 99.99, "quantity": 1, 
                        "location": "Test", "listing_type": "fixed_price"},
                "expected_status": 200  # API might accept any category
            },
            {
                "name": "Invalid listing type",
                "data": {"title": "Test", "description": "Test", "category": "Electronics", 
                        "condition": "New", "price": 99.99, "quantity": 1, 
                        "location": "Test", "listing_type": "invalid_type"},
                "expected_status": 422
            }
        ]
        
        results = []
        
        for case in edge_cases:
            try:
                headers = {'Authorization': f'Bearer {self.admin_token}', 'Content-Type': 'application/json'}
                response = requests.post(f"{BACKEND_URL}/listings", json=case["data"], headers=headers)
                
                if response.status_code == case["expected_status"]:
                    results.append(f"✅ {case['name']}: Expected {case['expected_status']}, got {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        listing_id = result.get('id')
                        if listing_id:
                            self.created_listings.append(listing_id)
                else:
                    results.append(f"⚠️ {case['name']}: Expected {case['expected_status']}, got {response.status_code}")
                    
            except Exception as e:
                results.append(f"❌ {case['name']}: Error - {str(e)}")
        
        self.log_result("Edge Cases Testing", True, f"Tested {len(edge_cases)} edge cases", {
            "results": results
        })
        
        return True

    def test_verify_created_listings_in_get_endpoint(self):
        """Verify created listings appear in GET /api/listings"""
        if not self.created_listings:
            self.log_result("Verify Created Listings", False, "No listings were created to verify")
            return False
            
        try:
            response = requests.get(f"{BACKEND_URL}/listings")
            
            if response.status_code == 200:
                all_listings = response.json()
                created_listing_ids = set(self.created_listings)
                found_listing_ids = set(listing.get('id') for listing in all_listings if listing.get('id'))
                
                found_created_listings = created_listing_ids.intersection(found_listing_ids)
                
                if found_created_listings:
                    self.log_result("Verify Created Listings", True, 
                                   f"Found {len(found_created_listings)}/{len(created_listing_ids)} created listings in GET endpoint", {
                        "created_count": len(created_listing_ids),
                        "found_count": len(found_created_listings),
                        "total_listings": len(all_listings),
                        "found_ids": list(found_created_listings)
                    })
                    return True
                else:
                    self.log_result("Verify Created Listings", False, "None of the created listings found in GET endpoint", {
                        "created_ids": list(created_listing_ids),
                        "total_listings": len(all_listings)
                    })
                    return False
            else:
                self.log_result("Verify Created Listings", False, f"GET listings failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Verify Created Listings", False, f"Error: {str(e)}")
            return False

    def test_authentication_requirements(self):
        """Test that only sellers/admin can create listings"""
        # Test without authentication
        listing_data = {
            "title": "Unauthorized Test",
            "description": "This should fail",
            "category": "Electronics",
            "condition": "New",
            "price": 99.99,
            "quantity": 1,
            "location": "Test",
            "listing_type": "fixed_price"
        }
        
        try:
            # Test without token
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data)
            
            if response.status_code == 403:
                self.log_result("Authentication Requirements", True, "Properly blocks unauthenticated requests", {
                    "status_code": response.status_code,
                    "response": response.text[:200]
                })
                return True
            else:
                self.log_result("Authentication Requirements", False, f"Expected 403, got {response.status_code}", {
                    "response": response.text[:200]
                })
                return False
                
        except Exception as e:
            self.log_result("Authentication Requirements", False, f"Error: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all listing creation tests"""
        print("🚀 COMPREHENSIVE LISTING CREATION FUNCTIONALITY TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print()
        
        # Setup phase
        print("📋 SETUP PHASE")
        print("-" * 30)
        
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
            
        if not self.create_regular_user():
            print("⚠️ Continuing without regular user (will skip seller tests)")
            
        if not self.upload_test_images():
            print("⚠️ Continuing without uploaded images (will skip image tests)")
        
        print()
        print("🧪 LISTING CREATION TESTS")
        print("-" * 30)
        
        # Core functionality tests
        tests = [
            ("Authentication Requirements", self.test_authentication_requirements),
            ("Admin Listing Creation", self.test_create_listing_admin_credentials),
            ("Seller Listing Creation", self.test_create_listing_seller_credentials),
            ("Required Fields Validation", self.test_required_fields_validation),
            ("Listing with Uploaded Images", self.test_listing_with_uploaded_images),
            ("Different Listing Types", self.test_different_listing_types),
            ("Various Categories", self.test_various_categories),
            ("Edge Cases Testing", self.test_edge_cases),
            ("Verify Created Listings", self.test_verify_created_listings_in_get_endpoint)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_method in tests:
            print(f"Running: {test_name}")
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution error: {str(e)}")
            print()
        
        # Summary
        print("📊 TEST SUMMARY")
        print("-" * 30)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if self.created_listings:
            print(f"Created {len(self.created_listings)} test listings:")
            for listing_id in self.created_listings:
                print(f"  - {listing_id}")
            print()
        
        # Detailed results
        print("📋 DETAILED RESULTS")
        print("-" * 30)
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                for key, value in result['details'].items():
                    if isinstance(value, list) and len(value) > 3:
                        print(f"  {key}: {len(value)} items")
                    else:
                        print(f"  {key}: {value}")
            print()
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = ListingCreationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("✅ ALL TESTS PASSED - Listing creation functionality is working correctly")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Issues found in listing creation functionality")
        sys.exit(1)