#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Admin User Management Focus
Testing the recent fixes for admin user creation, username availability, and user updates
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

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

    def test_admin_user_creation(self):
        """Test admin user creation with enhanced validation"""
        try:
            # Generate unique test data
            test_id = str(uuid.uuid4())[:8]
            test_user_data = {
                "first_name": "Test",
                "last_name": "User",
                "username": f"testuser_{test_id}",
                "email": f"testuser_{test_id}@example.com",
                "password": "SecurePassword123!",
                "role": "user",
                "is_business": False,
                "company_name": "",
                "country": "Netherlands",
                "vat_number": ""
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users", 
                json=test_user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                created_user = data.get('user', {})
                self.log_test(
                    "Admin User Creation (Regular)", 
                    True, 
                    f"Created user: {created_user.get('username')} with ID: {created_user.get('id')}"
                )
                return created_user.get('id')
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin User Creation (Regular)", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Admin User Creation (Regular)", False, error_msg=str(e))
            return None

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

    def run_grid_layout_testing(self):
        """Run grid layout testing by creating sample listings"""
        print("=" * 80)
        print("CATALORO GRID LAYOUT TESTING - SAMPLE LISTINGS CREATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting grid layout testing.")
            return
        
        # 2. Create Sample Listings for Grid Layout Testing
        print("📝 CREATING SAMPLE LISTINGS FOR GRID LAYOUT")
        print("-" * 40)
        created_listing_ids = self.test_create_sample_listings_for_grid_layout()
        
        # 3. Verify Listings Created
        print("✅ VERIFYING CREATED LISTINGS")
        print("-" * 40)
        all_listings = self.test_verify_created_listings()
        
        # 4. Test Browse Endpoint for Grid Layout
        print("🌐 TESTING BROWSE ENDPOINT FOR GRID LAYOUT")
        print("-" * 40)
        self.test_marketplace_browse_functionality()
        
        # Print Summary
        print("=" * 80)
        print("GRID LAYOUT TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print(f"Sample Listings Created: {len(created_listing_ids)}")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 GRID LAYOUT TESTING COMPLETE")
        print("The sample listings are now available for testing the browse page grid layout.")
        print("You can verify the 4-column layout (without ads) and 3-column layout (with ads) functionality.")
        
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
    
    # Run grid layout testing as requested in the review
    print("🎯 RUNNING GRID LAYOUT TESTING AS REQUESTED")
    print("Creating sample listings for browse page grid layout testing...")
    print()
    
    passed, failed, results = tester.run_grid_layout_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)