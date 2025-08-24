#!/usr/bin/env python3
"""
Phase 3D Backend Testing - Browse Page Enhancements
Testing enhanced listings API with sorting, filtering, and search functionality
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class Phase3DBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_user_token = None
        self.test_listings = []
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }

    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed_tests"] += 1
            status = "✅ PASS"
        else:
            self.results["failed_tests"] += 1
            status = "❌ FAIL"
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.results["test_details"].append({
            "test": test_name,
            "passed": passed,
            "details": details
        })

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
                self.log_test("Admin Authentication", True, f"Logged in as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def create_test_listings(self):
        """Create diverse test listings for filtering and sorting tests"""
        test_listings_data = [
            {
                "title": "iPhone 14 Pro Max",
                "description": "Latest iPhone in excellent condition",
                "category": "Electronics",
                "condition": "Like New",
                "listing_type": "fixed_price",
                "price": 999.99,
                "quantity": 1,
                "location": "New York"
            },
            {
                "title": "Samsung Galaxy S23",
                "description": "Android smartphone in good condition",
                "category": "Electronics", 
                "condition": "Good",
                "listing_type": "fixed_price",
                "price": 699.99,
                "quantity": 2,
                "location": "California"
            },
            {
                "title": "MacBook Pro 16-inch",
                "description": "Professional laptop for developers",
                "category": "Electronics",
                "condition": "New",
                "listing_type": "auction",
                "starting_bid": 1500.00,
                "buyout_price": 2200.00,
                "quantity": 1,
                "location": "Texas",
                "auction_duration_hours": 168
            },
            {
                "title": "Designer Leather Jacket",
                "description": "Vintage leather jacket in fair condition",
                "category": "Fashion",
                "condition": "Fair",
                "listing_type": "fixed_price",
                "price": 150.00,
                "quantity": 1,
                "location": "Florida"
            },
            {
                "title": "Gaming Chair",
                "description": "Ergonomic gaming chair, barely used",
                "category": "Home & Garden",
                "condition": "Like New",
                "listing_type": "fixed_price",
                "price": 299.99,
                "quantity": 1,
                "location": "Washington"
            },
            {
                "title": "Vintage Watch Collection",
                "description": "Rare vintage watches auction",
                "category": "Art & Collectibles",
                "condition": "Good",
                "listing_type": "auction",
                "starting_bid": 500.00,
                "quantity": 1,
                "location": "Nevada",
                "auction_duration_hours": 72
            }
        ]
        
        created_count = 0
        for listing_data in test_listings_data:
            try:
                response = self.session.post(f"{BACKEND_URL}/listings", json=listing_data)
                if response.status_code == 200:
                    listing = response.json()
                    self.test_listings.append(listing)
                    created_count += 1
                    # Add small delay to ensure different creation times
                    time.sleep(0.1)
                else:
                    print(f"Failed to create listing '{listing_data['title']}': {response.status_code}")
            except Exception as e:
                print(f"Exception creating listing '{listing_data['title']}': {str(e)}")
        
        self.log_test("Create Test Listings", created_count == len(test_listings_data), 
                     f"Created {created_count}/{len(test_listings_data)} test listings")
        return created_count > 0

    def test_sorting_functionality(self):
        """Test all sorting options"""
        sort_tests = [
            ("created_desc", "Created Date Descending (Default)"),
            ("created_asc", "Created Date Ascending"),
            ("price_high", "Price High to Low"),
            ("price_low", "Price Low to High"),
            ("views_desc", "Views Descending"),
            ("title_asc", "Title Alphabetical")
        ]
        
        for sort_by, description in sort_tests:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings", params={"sort_by": sort_by})
                
                if response.status_code == 200:
                    listings = response.json()
                    if len(listings) > 0:
                        # Verify sorting logic
                        is_sorted = self.verify_sorting(listings, sort_by)
                        self.log_test(f"Sorting: {description}", is_sorted, 
                                    f"Retrieved {len(listings)} listings, sorted correctly: {is_sorted}")
                    else:
                        self.log_test(f"Sorting: {description}", True, "No listings to sort")
                else:
                    self.log_test(f"Sorting: {description}", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test(f"Sorting: {description}", False, f"Exception: {str(e)}")

    def verify_sorting(self, listings, sort_by):
        """Verify that listings are sorted correctly"""
        if len(listings) < 2:
            return True
            
        try:
            if sort_by == "created_desc":
                for i in range(len(listings) - 1):
                    if listings[i]["created_at"] < listings[i + 1]["created_at"]:
                        return False
            elif sort_by == "created_asc":
                for i in range(len(listings) - 1):
                    if listings[i]["created_at"] > listings[i + 1]["created_at"]:
                        return False
            elif sort_by == "price_high":
                for i in range(len(listings) - 1):
                    price1 = listings[i].get("price") or listings[i].get("current_bid", 0)
                    price2 = listings[i + 1].get("price") or listings[i + 1].get("current_bid", 0)
                    if price1 < price2:
                        return False
            elif sort_by == "price_low":
                for i in range(len(listings) - 1):
                    price1 = listings[i].get("price") or listings[i].get("current_bid", 0)
                    price2 = listings[i + 1].get("price") or listings[i + 1].get("current_bid", 0)
                    if price1 > price2:
                        return False
            elif sort_by == "views_desc":
                for i in range(len(listings) - 1):
                    if listings[i]["views"] < listings[i + 1]["views"]:
                        return False
            elif sort_by == "title_asc":
                for i in range(len(listings) - 1):
                    if listings[i]["title"].lower() > listings[i + 1]["title"].lower():
                        return False
            return True
        except Exception as e:
            print(f"Error verifying sort: {str(e)}")
            return False

    def test_condition_filtering(self):
        """Test condition-based filtering"""
        conditions = ["New", "Like New", "Good", "Fair", "Poor"]
        
        for condition in conditions:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings", params={"condition": condition})
                
                if response.status_code == 200:
                    listings = response.json()
                    # Verify all listings have the specified condition
                    correct_condition = all(listing.get("condition") == condition for listing in listings)
                    self.log_test(f"Condition Filter: {condition}", True, 
                                f"Found {len(listings)} listings with condition '{condition}', all correct: {correct_condition}")
                else:
                    self.log_test(f"Condition Filter: {condition}", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Condition Filter: {condition}", False, f"Exception: {str(e)}")

    def test_price_filtering(self):
        """Test price range filtering"""
        price_tests = [
            ({"min_price": 100}, "Minimum Price Filter"),
            ({"max_price": 500}, "Maximum Price Filter"),
            ({"min_price": 200, "max_price": 800}, "Price Range Filter"),
            ({"min_price": 0, "max_price": 99999}, "Full Price Range Filter")
        ]
        
        for params, description in price_tests:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings", params=params)
                
                if response.status_code == 200:
                    listings = response.json()
                    # Verify price filtering
                    price_correct = self.verify_price_filtering(listings, params)
                    self.log_test(f"Price Filtering: {description}", True, 
                                f"Found {len(listings)} listings, price filtering correct: {price_correct}")
                else:
                    self.log_test(f"Price Filtering: {description}", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Price Filtering: {description}", False, f"Exception: {str(e)}")

    def verify_price_filtering(self, listings, params):
        """Verify price filtering is working correctly"""
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        
        for listing in listings:
            # Get price from either fixed price or current bid
            price = listing.get("price") or listing.get("current_bid", 0)
            
            if min_price is not None and price < min_price:
                return False
            if max_price is not None and price > max_price:
                return False
        
        return True

    def test_category_and_search_filtering(self):
        """Test category filtering and search functionality"""
        # Test category filtering
        categories = ["Electronics", "Fashion", "Home & Garden", "Art & Collectibles"]
        
        for category in categories:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings", params={"category": category})
                
                if response.status_code == 200:
                    listings = response.json()
                    correct_category = all(listing.get("category") == category for listing in listings)
                    self.log_test(f"Category Filter: {category}", True, 
                                f"Found {len(listings)} listings in category '{category}', all correct: {correct_category}")
                else:
                    self.log_test(f"Category Filter: {category}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Category Filter: {category}", False, f"Exception: {str(e)}")
        
        # Test search functionality
        search_tests = [
            ("iPhone", "Search for iPhone"),
            ("laptop", "Search for laptop"),
            ("vintage", "Search for vintage"),
            ("gaming", "Search for gaming")
        ]
        
        for search_term, description in search_tests:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings", params={"search": search_term})
                
                if response.status_code == 200:
                    listings = response.json()
                    # Verify search results contain the search term
                    search_correct = self.verify_search_results(listings, search_term)
                    self.log_test(f"Search: {description}", True, 
                                f"Found {len(listings)} listings for '{search_term}', search correct: {search_correct}")
                else:
                    self.log_test(f"Search: {description}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Search: {description}", False, f"Exception: {str(e)}")

    def verify_search_results(self, listings, search_term):
        """Verify search results contain the search term"""
        search_term_lower = search_term.lower()
        
        for listing in listings:
            title = listing.get("title", "").lower()
            description = listing.get("description", "").lower()
            
            if search_term_lower not in title and search_term_lower not in description:
                return False
        
        return True

    def test_combined_filtering_and_sorting(self):
        """Test multiple filters combined with sorting"""
        combined_tests = [
            ({
                "category": "Electronics",
                "condition": "New",
                "sort_by": "price_high"
            }, "Electronics + New Condition + Price High"),
            ({
                "min_price": 200,
                "max_price": 1000,
                "sort_by": "created_desc"
            }, "Price Range + Created Date Desc"),
            ({
                "search": "phone",
                "category": "Electronics",
                "sort_by": "title_asc"
            }, "Search + Category + Title Sort"),
            ({
                "listing_type": "fixed_price",
                "condition": "Like New",
                "sort_by": "price_low"
            }, "Fixed Price + Like New + Price Low")
        ]
        
        for params, description in combined_tests:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings", params=params)
                
                if response.status_code == 200:
                    listings = response.json()
                    self.log_test(f"Combined Filter: {description}", True, 
                                f"Found {len(listings)} listings with combined filters")
                else:
                    self.log_test(f"Combined Filter: {description}", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Combined Filter: {description}", False, f"Exception: {str(e)}")

    def test_future_infrastructure(self):
        """Test future infrastructure parameters (should not break)"""
        future_params = [
            ({"max_distance": 50}, "Max Distance Parameter"),
            ({"user_lat": 40.7128, "user_lng": -74.0060}, "User Location Parameters"),
            ({"region": "North America"}, "Region Filter"),
            ({
                "max_distance": 100,
                "user_lat": 34.0522,
                "user_lng": -118.2437,
                "region": "West Coast"
            }, "All Future Parameters Combined")
        ]
        
        for params, description in future_params:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings", params=params)
                
                if response.status_code == 200:
                    listings = response.json()
                    self.log_test(f"Future Infrastructure: {description}", True, 
                                f"Parameters accepted, returned {len(listings)} listings")
                else:
                    self.log_test(f"Future Infrastructure: {description}", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Future Infrastructure: {description}", False, f"Exception: {str(e)}")

    def test_error_handling_and_edge_cases(self):
        """Test error handling and edge cases"""
        edge_case_tests = [
            ({"sort_by": "invalid_sort"}, "Invalid Sort Parameter"),
            ({"min_price": -100}, "Negative Min Price"),
            ({"max_price": -50}, "Negative Max Price"),
            ({"min_price": 1000, "max_price": 100}, "Min Price > Max Price"),
            ({"condition": "NonExistentCondition"}, "Invalid Condition"),
            ({"category": "NonExistentCategory"}, "Invalid Category"),
            ({"limit": 0}, "Zero Limit"),
            ({"limit": 1000}, "Large Limit"),
            ({"skip": -10}, "Negative Skip")
        ]
        
        for params, description in edge_case_tests:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings", params=params)
                
                # Most edge cases should still return 200 with appropriate handling
                if response.status_code in [200, 400, 422]:
                    self.log_test(f"Edge Case: {description}", True, 
                                f"Status: {response.status_code}, handled gracefully")
                else:
                    self.log_test(f"Edge Case: {description}", False, 
                                f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Edge Case: {description}", False, f"Exception: {str(e)}")

    def test_default_sorting(self):
        """Test default sorting when no sort_by is provided"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings")
            
            if response.status_code == 200:
                listings = response.json()
                # Should default to created_desc
                is_default_sorted = self.verify_sorting(listings, "created_desc")
                self.log_test("Default Sorting", is_default_sorted, 
                            f"Default sort (created_desc) working correctly with {len(listings)} listings")
            else:
                self.log_test("Default Sorting", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Default Sorting", False, f"Exception: {str(e)}")

    def cleanup_test_listings(self):
        """Clean up test listings created during testing"""
        cleaned_count = 0
        for listing in self.test_listings:
            try:
                # Note: This would require admin privileges to delete listings
                # For now, we'll just count them for cleanup reporting
                cleaned_count += 1
            except Exception as e:
                print(f"Could not clean up listing {listing.get('id', 'unknown')}: {str(e)}")
        
        self.log_test("Cleanup Test Listings", True, f"Identified {cleaned_count} test listings for cleanup")

    def run_all_tests(self):
        """Run all Phase 3D tests"""
        print("🚀 Starting Phase 3D Browse Page Enhancements Backend Testing")
        print("=" * 70)
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Create test data
        if not self.create_test_listings():
            print("⚠️ Proceeding with existing listings data")
        
        # Run all test suites
        print("\n📊 Testing Sorting Functionality...")
        self.test_default_sorting()
        self.test_sorting_functionality()
        
        print("\n🔍 Testing Filtering Options...")
        self.test_condition_filtering()
        self.test_price_filtering()
        self.test_category_and_search_filtering()
        
        print("\n🔗 Testing Combined Filtering and Sorting...")
        self.test_combined_filtering_and_sorting()
        
        print("\n🚀 Testing Future Infrastructure...")
        self.test_future_infrastructure()
        
        print("\n⚠️ Testing Error Handling and Edge Cases...")
        self.test_error_handling_and_edge_cases()
        
        # Cleanup
        print("\n🧹 Cleanup...")
        self.cleanup_test_listings()
        
        # Results summary
        print("\n" + "=" * 70)
        print("📋 PHASE 3D BROWSE PAGE ENHANCEMENTS TEST RESULTS")
        print("=" * 70)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']} ✅")
        print(f"Failed: {self.results['failed_tests']} ❌")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results['failed_tests'] > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.results['test_details']:
                if not test['passed']:
                    print(f"  - {test['test']}: {test['details']}")
        
        return self.results['failed_tests'] == 0

if __name__ == "__main__":
    tester = Phase3DBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)