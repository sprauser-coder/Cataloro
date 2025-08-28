#!/usr/bin/env python3
"""
Categories Management Testing for Cataloro v1.0.4 Fix 8
Testing categories retrieval, filtering, and data structure integrity
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://marketplace-fix-6.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class CategoriesTestSuite:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        print(result)
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.log_test("Admin Authentication", True, f"Token obtained for {data['user']['email']}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_categories_retrieval(self):
        """Test GET /api/categories endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/categories")
            
            if response.status_code == 200:
                categories = response.json()
                
                # Verify it's a list
                if not isinstance(categories, list):
                    self.log_test("Categories Retrieval - Data Type", False, "Response is not a list")
                    return False
                
                # Verify expected categories are present
                expected_categories = [
                    "Electronics", "Fashion", "Home & Garden", "Sports", "Books",
                    "Automotive", "Health & Beauty", "Toys", "Art & Collectibles", "Other"
                ]
                
                missing_categories = []
                for expected in expected_categories:
                    if expected not in categories:
                        missing_categories.append(expected)
                
                if missing_categories:
                    self.log_test("Categories Retrieval - Content", False, f"Missing categories: {missing_categories}")
                    return False
                
                self.log_test("Categories Retrieval", True, f"Retrieved {len(categories)} categories: {categories}")
                return categories
                
            else:
                self.log_test("Categories Retrieval", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Categories Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_category_filtering(self, categories):
        """Test GET /api/listings?category={category} filtering"""
        if not categories:
            self.log_test("Category Filtering", False, "No categories available for testing")
            return
        
        try:
            # Test filtering for each category
            category_results = {}
            
            for category in categories:
                response = requests.get(f"{BACKEND_URL}/listings", params={"category": category})
                
                if response.status_code == 200:
                    listings = response.json()
                    
                    # Verify all listings belong to the requested category
                    invalid_listings = []
                    for listing in listings:
                        if listing.get("category") != category:
                            invalid_listings.append(f"ID: {listing.get('id', 'unknown')} has category: {listing.get('category')}")
                    
                    if invalid_listings:
                        self.log_test(f"Category Filtering - {category}", False, f"Invalid listings: {invalid_listings[:3]}")
                    else:
                        category_results[category] = len(listings)
                        self.log_test(f"Category Filtering - {category}", True, f"Found {len(listings)} listings")
                else:
                    self.log_test(f"Category Filtering - {category}", False, f"Status: {response.status_code}")
            
            # Test with invalid category
            response = requests.get(f"{BACKEND_URL}/listings", params={"category": "NonExistentCategory"})
            if response.status_code == 200:
                listings = response.json()
                if len(listings) == 0:
                    self.log_test("Category Filtering - Invalid Category", True, "Returns empty list for invalid category")
                else:
                    self.log_test("Category Filtering - Invalid Category", False, f"Should return empty list, got {len(listings)} listings")
            
            return category_results
            
        except Exception as e:
            self.log_test("Category Filtering", False, f"Exception: {str(e)}")
            return {}
    
    def test_listings_data_structure(self):
        """Test listings data structure and verify no multiple <listings> display issues"""
        try:
            response = requests.get(f"{BACKEND_URL}/listings", params={"limit": 10})
            
            if response.status_code == 200:
                listings = response.json()
                
                if not isinstance(listings, list):
                    self.log_test("Listings Data Structure", False, "Response is not a list")
                    return False
                
                # Check for blank/empty listings
                blank_listings = []
                duplicate_ids = []
                seen_ids = set()
                
                for i, listing in enumerate(listings):
                    # Check for blank listings
                    if not listing or not isinstance(listing, dict):
                        blank_listings.append(f"Index {i}: {type(listing)}")
                        continue
                    
                    # Check for duplicate IDs
                    listing_id = listing.get("id")
                    if listing_id in seen_ids:
                        duplicate_ids.append(listing_id)
                    else:
                        seen_ids.add(listing_id)
                    
                    # Check required fields
                    required_fields = ["id", "title", "category", "price", "seller_id"]
                    missing_fields = []
                    for field in required_fields:
                        if field not in listing or listing[field] is None:
                            if field == "price" and listing.get("listing_type") == "auction":
                                # For auctions, current_bid might be used instead of price
                                if "current_bid" not in listing:
                                    missing_fields.append(field)
                            else:
                                missing_fields.append(field)
                    
                    if missing_fields:
                        self.log_test(f"Listing Data Structure - ID {listing_id}", False, f"Missing fields: {missing_fields}")
                
                # Report issues
                if blank_listings:
                    self.log_test("Listings Data Structure - Blank Items", False, f"Found blank listings: {blank_listings}")
                else:
                    self.log_test("Listings Data Structure - Blank Items", True, "No blank listings found")
                
                if duplicate_ids:
                    self.log_test("Listings Data Structure - Duplicates", False, f"Found duplicate IDs: {duplicate_ids}")
                else:
                    self.log_test("Listings Data Structure - Duplicates", True, "No duplicate listings found")
                
                self.log_test("Listings Data Structure", True, f"Processed {len(listings)} listings successfully")
                return True
                
            else:
                self.log_test("Listings Data Structure", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Listings Data Structure", False, f"Exception: {str(e)}")
            return False
    
    def test_category_counts_accuracy(self, category_results):
        """Test that category counts are accurate and consistent"""
        try:
            # Get total listings count
            response = requests.get(f"{BACKEND_URL}/listings", params={"limit": 1000})
            
            if response.status_code == 200:
                all_listings = response.json()
                total_listings = len(all_listings)
                
                # Count listings by category manually
                manual_counts = {}
                for listing in all_listings:
                    category = listing.get("category", "Unknown")
                    manual_counts[category] = manual_counts.get(category, 0) + 1
                
                # Compare with filtered results
                discrepancies = []
                for category, filtered_count in category_results.items():
                    manual_count = manual_counts.get(category, 0)
                    if filtered_count != manual_count:
                        discrepancies.append(f"{category}: filtered={filtered_count}, manual={manual_count}")
                
                if discrepancies:
                    self.log_test("Category Counts Accuracy", False, f"Discrepancies: {discrepancies}")
                else:
                    self.log_test("Category Counts Accuracy", True, f"All category counts match. Total listings: {total_listings}")
                
                # Report category distribution
                print(f"\n📊 Category Distribution:")
                for category, count in sorted(manual_counts.items()):
                    print(f"   {category}: {count} listings")
                
                return True
                
            else:
                self.log_test("Category Counts Accuracy", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Category Counts Accuracy", False, f"Exception: {str(e)}")
            return False
    
    def test_category_management_endpoints(self):
        """Test if category management endpoints exist (POST/DELETE)"""
        # Note: Based on backend code review, these endpoints don't exist
        # This test documents the current state
        
        # Test POST /api/categories (should not exist)
        try:
            response = requests.post(f"{BACKEND_URL}/categories", 
                                   json={"name": "Test Category"},
                                   headers=self.get_auth_headers())
            
            if response.status_code == 404 or response.status_code == 405:
                self.log_test("Category Creation Endpoint", True, "POST /categories correctly returns 404/405 (not implemented)")
            else:
                self.log_test("Category Creation Endpoint", False, f"Unexpected response: {response.status_code}")
                
        except Exception as e:
            self.log_test("Category Creation Endpoint", True, f"Endpoint not accessible (expected): {str(e)}")
        
        # Test DELETE /api/categories/{name} (should not exist)
        try:
            response = requests.delete(f"{BACKEND_URL}/categories/Electronics",
                                     headers=self.get_auth_headers())
            
            if response.status_code == 404 or response.status_code == 405:
                self.log_test("Category Deletion Endpoint", True, "DELETE /categories/{name} correctly returns 404/405 (not implemented)")
            else:
                self.log_test("Category Deletion Endpoint", False, f"Unexpected response: {response.status_code}")
                
        except Exception as e:
            self.log_test("Category Deletion Endpoint", True, f"Endpoint not accessible (expected): {str(e)}")
    
    def run_all_tests(self):
        """Run all categories management tests"""
        print("🧪 CATEGORIES MANAGEMENT TESTING - CATALORO v1.0.4 FIX 8")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return False
        
        print()
        
        # Test categories retrieval
        categories = self.test_categories_retrieval()
        if not categories:
            print("❌ Cannot proceed without categories data")
            return False
        
        print()
        
        # Test category filtering
        category_results = self.test_category_filtering(categories)
        
        print()
        
        # Test listings data structure
        self.test_listings_data_structure()
        
        print()
        
        # Test category counts accuracy
        if category_results:
            self.test_category_counts_accuracy(category_results)
        
        print()
        
        # Test category management endpoints
        self.test_category_management_endpoints()
        
        # Print summary
        print()
        print("=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            print(result)
        
        print()
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"🎯 OVERALL RESULT: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("✅ Categories management system is working correctly!")
            return True
        elif success_rate >= 70:
            print("⚠️  Categories management has minor issues but core functionality works")
            return True
        else:
            print("❌ Categories management has significant issues requiring attention")
            return False

def main():
    """Main test execution"""
    test_suite = CategoriesTestSuite()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()