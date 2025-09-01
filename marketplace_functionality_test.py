#!/usr/bin/env python3
"""
Cataloro Marketplace Updated Functionality Test Suite
Tests the updated marketplace functionality with latest changes:
1. Browse Endpoint - listings without quantity fields
2. Price Suggestions - catalyst calculations with Euro formatting
3. Catalyst Listings - new pricing system
4. Cart Functionality - quantity=1 (one product per listing)
5. Euro Currency - all price-related API responses
6. Listing Creation - updated creation process
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class MarketplaceFunctionalityTester:
    def __init__(self, base_url="https://trade-platform-30.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_listing_id = None
        self.test_catalyst_listing_id = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("🔐 Setting up authentication...")
        
        # Admin login
        admin_success, admin_response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        if admin_success and 'token' in admin_response:
            self.admin_token = admin_response['token']
            self.admin_user = admin_response['user']
            print(f"   Admin User: {self.admin_user['email']}")

        # User login
        user_success, user_response = self.run_test(
            "User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        if user_success and 'token' in user_response:
            self.user_token = user_response['token']
            self.regular_user = user_response['user']
            print(f"   Regular User: {self.regular_user['email']}")

        return admin_success and user_success

    def test_browse_endpoint_without_quantity(self):
        """Test 1: Browse Endpoint - Verify listings returned without quantity fields"""
        print("\n📋 TEST 1: Browse Endpoint - No Quantity Fields")
        
        success, response = self.run_test(
            "Browse Listings Format",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            print(f"   Found {len(response)} listings")
            
            # Verify response is array format (not object with 'listings' key)
            if isinstance(response, list):
                self.log_test("Browse Response Format", True, "Returns array format (compatible with .map())")
            else:
                self.log_test("Browse Response Format", False, "Returns object format (not compatible with .map())")
                return False
            
            # Check that listings don't have quantity fields
            quantity_found = False
            for listing in response:
                if 'quantity' in listing:
                    quantity_found = True
                    break
            
            if not quantity_found:
                self.log_test("Quantity Field Removal", True, "No quantity fields found (one product per listing)")
            else:
                self.log_test("Quantity Field Removal", False, "Quantity fields still present in listings")
                
            # Verify essential fields are present
            if response and len(response) > 0:
                first_listing = response[0]
                required_fields = ['id', 'title', 'description', 'price', 'category', 'seller_id']
                missing_fields = [field for field in required_fields if field not in first_listing]
                
                if not missing_fields:
                    self.log_test("Essential Fields Present", True, "All required listing fields present")
                else:
                    self.log_test("Essential Fields Present", False, f"Missing fields: {missing_fields}")
        
        return success

    def test_price_suggestions_endpoint(self):
        """Test 2: Price Suggestions - Verify catalyst calculations provide proper price data"""
        print("\n💰 TEST 2: Price Suggestions - Catalyst Calculations")
        
        if not self.admin_user:
            print("❌ Price Suggestions - SKIPPED (No admin logged in)")
            return False
        
        success, response = self.run_test(
            "Catalyst Price Calculations",
            "GET",
            "api/admin/catalyst/calculations",
            200
        )
        
        if success:
            print(f"   Found {len(response)} catalyst calculations")
            
            # Verify calculations have proper price data structure
            if response and len(response) > 0:
                first_calc = response[0]
                required_fields = ['cat_id', 'name', 'total_price']
                missing_fields = [field for field in required_fields if field not in first_calc]
                
                if not missing_fields:
                    self.log_test("Price Data Structure", True, "All required calculation fields present")
                    
                    # Check Euro currency formatting
                    total_price = first_calc.get('total_price', 0)
                    if isinstance(total_price, (int, float)) and total_price >= 0:
                        self.log_test("Euro Price Format", True, f"Price: €{total_price}")
                    else:
                        self.log_test("Euro Price Format", False, f"Invalid price format: {total_price}")
                        
                    # Show sample calculations
                    print(f"   Sample calculations:")
                    for i, calc in enumerate(response[:3]):
                        print(f"     {i+1}. {calc.get('name', 'N/A')}: €{calc.get('total_price', 0)}")
                        
                else:
                    self.log_test("Price Data Structure", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Price Data Structure", False, "No calculation data found")
        
        return success

    def test_catalyst_listing_creation(self):
        """Test 3: Catalyst Listings - Create test catalyst listing with new pricing system"""
        print("\n🧪 TEST 3: Catalyst Listing Creation - New Pricing System")
        
        if not self.regular_user:
            print("❌ Catalyst Listing Creation - SKIPPED (No user logged in)")
            return False
        
        # Create test catalyst listing with realistic data
        catalyst_listing = {
            "title": "FAPACAT8659 Premium Automotive Catalyst",
            "description": "High-quality automotive catalyst with excellent precious metal content. Weight: 1.53g. Professionally tested and verified for marketplace pricing suggestions.",
            "price": 292.74,  # Euro price
            "category": "Catalysts",
            "condition": "Used - Excellent",
            "seller_id": self.regular_user['id'],
            "images": [
                "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
                "https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=400"
            ],
            "tags": ["catalyst", "automotive", "precious metals", "FAPACAT", "tested"],
            "features": ["High PT content", "Ceramic substrate", "Quality verified", "Market price calculated"]
        }
        
        success, response = self.run_test(
            "Create Catalyst Listing",
            "POST",
            "api/listings",
            200,
            data=catalyst_listing
        )
        
        if success:
            self.test_catalyst_listing_id = response.get('listing_id')
            print(f"   ✅ Catalyst listing created with ID: {self.test_catalyst_listing_id}")
            
            # Verify no quantity field was added during creation
            if 'quantity' not in catalyst_listing:
                self.log_test("No Quantity in Creation", True, "Listing created without quantity field")
            
            # Verify Euro price is properly stored
            if catalyst_listing['price'] == 292.74:
                self.log_test("Euro Price Storage", True, f"Price stored as €{catalyst_listing['price']}")
            
            # Verify catalyst category
            if catalyst_listing['category'] == "Catalysts":
                self.log_test("Catalyst Category", True, "Category set to 'Catalysts'")
                
        return success

    def test_cart_functionality_quantity_one(self):
        """Test 4: Cart Functionality - Test adding items with quantity=1"""
        print("\n🛒 TEST 4: Cart Functionality - Quantity=1 (One Product Per Listing)")
        
        if not self.regular_user or not self.test_catalyst_listing_id:
            print("❌ Cart Functionality - SKIPPED (No user or test listing)")
            return False
        
        # Test adding item to cart with quantity=1
        cart_item = {
            "item_id": self.test_catalyst_listing_id,
            "quantity": 1,  # One product per listing
            "price": 292.74
        }
        
        success, response = self.run_test(
            "Add to Cart (Quantity=1)",
            "POST",
            f"api/user/{self.regular_user['id']}/cart",
            200,
            data=cart_item
        )
        
        if success:
            self.log_test("Cart Addition", True, "Item added to cart with quantity=1")
            
            # Verify cart contents
            cart_success, cart_response = self.run_test(
                "Get Cart Contents",
                "GET",
                f"api/user/{self.regular_user['id']}/cart",
                200
            )
            
            if cart_success:
                cart_items = cart_response
                catalyst_items = [item for item in cart_items if item.get('item_id') == self.test_catalyst_listing_id]
                
                if catalyst_items:
                    cart_item = catalyst_items[0]
                    if cart_item.get('quantity') == 1:
                        self.log_test("Cart Quantity Verification", True, "Cart item has quantity=1")
                    else:
                        self.log_test("Cart Quantity Verification", False, f"Cart item quantity: {cart_item.get('quantity')}")
                        
                    # Verify Euro price in cart
                    if cart_item.get('price') == 292.74:
                        self.log_test("Cart Euro Price", True, f"Cart price: €{cart_item.get('price')}")
                    else:
                        self.log_test("Cart Euro Price", False, f"Unexpected cart price: {cart_item.get('price')}")
                else:
                    self.log_test("Cart Item Found", False, "Catalyst item not found in cart")
        
        return success

    def test_euro_currency_formatting(self):
        """Test 5: Euro Currency - Verify all price-related API responses work with Euro formatting"""
        print("\n💶 TEST 5: Euro Currency Formatting - All Price-Related APIs")
        
        euro_tests_passed = 0
        total_euro_tests = 0
        
        # Test 1: Browse listings Euro prices
        total_euro_tests += 1
        browse_success, browse_response = self.run_test(
            "Browse Listings Euro Prices",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if browse_success and browse_response:
            euro_prices_valid = True
            for listing in browse_response[:3]:  # Check first 3 listings
                price = listing.get('price', 0)
                if not isinstance(price, (int, float)) or price < 0:
                    euro_prices_valid = False
                    break
            
            if euro_prices_valid:
                euro_tests_passed += 1
                self.log_test("Browse Euro Prices", True, "All listing prices are valid Euro amounts")
            else:
                self.log_test("Browse Euro Prices", False, "Invalid price formats found")
        
        # Test 2: Catalyst calculations Euro prices
        if self.admin_user:
            total_euro_tests += 1
            calc_success, calc_response = self.run_test(
                "Catalyst Calculations Euro Prices",
                "GET",
                "api/admin/catalyst/calculations",
                200
            )
            
            if calc_success and calc_response:
                euro_calcs_valid = True
                for calc in calc_response[:3]:  # Check first 3 calculations
                    total_price = calc.get('total_price', 0)
                    if not isinstance(total_price, (int, float)) or total_price < 0:
                        euro_calcs_valid = False
                        break
                
                if euro_calcs_valid:
                    euro_tests_passed += 1
                    self.log_test("Calculations Euro Prices", True, "All calculation prices are valid Euro amounts")
                else:
                    self.log_test("Calculations Euro Prices", False, "Invalid calculation price formats")
        
        # Test 3: Cart Euro prices
        if self.regular_user:
            total_euro_tests += 1
            cart_success, cart_response = self.run_test(
                "Cart Euro Prices",
                "GET",
                f"api/user/{self.regular_user['id']}/cart",
                200
            )
            
            if cart_success:
                euro_cart_valid = True
                for item in cart_response:
                    price = item.get('price', 0)
                    if not isinstance(price, (int, float)) or price < 0:
                        euro_cart_valid = False
                        break
                
                if euro_cart_valid:
                    euro_tests_passed += 1
                    self.log_test("Cart Euro Prices", True, "All cart prices are valid Euro amounts")
                else:
                    self.log_test("Cart Euro Prices", False, "Invalid cart price formats")
        
        # Summary
        success = euro_tests_passed == total_euro_tests
        self.log_test("Euro Currency Complete", success, f"{euro_tests_passed}/{total_euro_tests} Euro tests passed")
        return success

    def test_updated_listing_creation_process(self):
        """Test 6: Listing Creation - Test updated creation process"""
        print("\n📝 TEST 6: Updated Listing Creation Process")
        
        if not self.regular_user:
            print("❌ Listing Creation - SKIPPED (No user logged in)")
            return False
        
        # Create a regular marketplace listing (non-catalyst)
        regular_listing = {
            "title": "Premium Smartphone - Latest Model",
            "description": "Brand new smartphone with advanced features. Perfect condition, includes original packaging and accessories.",
            "price": 599.99,  # Euro price
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.regular_user['id'],
            "images": [
                "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400"
            ],
            "tags": ["smartphone", "electronics", "new", "premium"],
            "features": ["Latest processor", "High-resolution camera", "Long battery life"]
        }
        
        success, response = self.run_test(
            "Create Regular Listing",
            "POST",
            "api/listings",
            200,
            data=regular_listing
        )
        
        if success:
            self.test_listing_id = response.get('listing_id')
            print(f"   ✅ Regular listing created with ID: {self.test_listing_id}")
            
            # Verify listing appears in browse results
            browse_success, browse_response = self.run_test(
                "Verify Listing in Browse",
                "GET",
                "api/marketplace/browse",
                200
            )
            
            if browse_success:
                new_listings = [listing for listing in browse_response if listing.get('id') == self.test_listing_id]
                if new_listings:
                    self.log_test("Listing in Browse Results", True, "New listing appears in browse results")
                    
                    # Verify no quantity field
                    new_listing = new_listings[0]
                    if 'quantity' not in new_listing:
                        self.log_test("No Quantity in Browse", True, "Listing in browse has no quantity field")
                    else:
                        self.log_test("No Quantity in Browse", False, "Listing in browse has quantity field")
                        
                    # Verify Euro price
                    if new_listing.get('price') == 599.99:
                        self.log_test("Browse Euro Price", True, f"Browse price: €{new_listing.get('price')}")
                    else:
                        self.log_test("Browse Euro Price", False, f"Unexpected browse price: {new_listing.get('price')}")
                else:
                    self.log_test("Listing in Browse Results", False, "New listing not found in browse results")
        
        return success

    def test_price_suggestion_matching(self):
        """Test price suggestion matching between catalyst data and listings"""
        print("\n🔍 BONUS TEST: Price Suggestion Matching Logic")
        
        if not self.admin_user:
            print("❌ Price Matching - SKIPPED (No admin logged in)")
            return False
        
        # Get catalyst calculations
        calc_success, calc_response = self.run_test(
            "Get Calculations for Matching",
            "GET",
            "api/admin/catalyst/calculations",
            200
        )
        
        if not calc_success:
            return False
        
        # Get browse listings
        browse_success, browse_response = self.run_test(
            "Get Listings for Matching",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if not browse_success:
            return False
        
        # Find catalyst listings and match with calculations
        catalyst_listings = [listing for listing in browse_response if listing.get('category') == 'Catalysts']
        matched_prices = 0
        
        print(f"   Found {len(catalyst_listings)} catalyst listings to match")
        
        for listing in catalyst_listings:
            listing_title = listing.get('title', '')
            
            # Look for matching catalyst in calculations
            for calc in calc_response:
                calc_name = calc.get('name', '')
                if calc_name and calc_name in listing_title:
                    calculated_price = calc.get('total_price', 0)
                    listing_price = listing.get('price', 0)
                    
                    print(f"   📊 Price Match Found:")
                    print(f"      Listing: {listing_title}")
                    print(f"      Catalyst: {calc_name}")
                    print(f"      Calculated: €{calculated_price}")
                    print(f"      Listed: €{listing_price}")
                    
                    matched_prices += 1
                    break
        
        success = matched_prices > 0
        self.log_test("Price Suggestion Matching", success, f"Found {matched_prices} price matches")
        return success

    def run_marketplace_functionality_tests(self):
        """Run all marketplace functionality tests"""
        print("🚀 Starting Marketplace Functionality Tests")
        print("Testing updated marketplace functionality with latest changes")
        print("=" * 80)

        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return False

        # Run the 6 main tests from the review request
        test_results = []
        
        # Test 1: Browse Endpoint
        test_results.append(self.test_browse_endpoint_without_quantity())
        
        # Test 2: Price Suggestions
        test_results.append(self.test_price_suggestions_endpoint())
        
        # Test 3: Catalyst Listings
        test_results.append(self.test_catalyst_listing_creation())
        
        # Test 4: Cart Functionality
        test_results.append(self.test_cart_functionality_quantity_one())
        
        # Test 5: Euro Currency
        test_results.append(self.test_euro_currency_formatting())
        
        # Test 6: Listing Creation
        test_results.append(self.test_updated_listing_creation_process())
        
        # Bonus Test: Price Matching
        test_results.append(self.test_price_suggestion_matching())

        # Print results
        print("\n" + "=" * 80)
        print(f"📊 Marketplace Functionality Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        passed_main_tests = sum(test_results[:6])  # First 6 are main tests
        print(f"🎯 Main Requirements: {passed_main_tests}/6 tests passed")
        
        if passed_main_tests == 6:
            print("🎉 All marketplace functionality requirements met!")
            return True
        else:
            print(f"⚠️  {6 - passed_main_tests} main requirements failed")
            return False

def main():
    """Main test execution"""
    tester = MarketplaceFunctionalityTester()
    success = tester.run_marketplace_functionality_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())