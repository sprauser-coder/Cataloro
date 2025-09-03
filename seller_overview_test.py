#!/usr/bin/env python3
"""
Seller Information Visibility Fix Test
Tests the seller overview endpoint to verify complete seller information including business details
"""

import requests
import sys
import json
from datetime import datetime

class SellerOverviewTester:
    def __init__(self, base_url="https://cataloro-marketplace-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

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
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response length: {len(response_data) if isinstance(response_data, list) else 'object'}"
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_test_users(self):
        """Setup test users for testing"""
        print("\n🔧 Setting up test users...")
        
        # Login as admin
        success_admin, admin_response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success_admin and 'user' in admin_response:
            self.admin_user = admin_response['user']
            print(f"   Admin User: {self.admin_user.get('username', 'Unknown')}")
        
        # Login as regular user
        success_user, user_response = self.run_test(
            "Regular User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "user@cataloro.com", "password": "demo123"}
        )
        
        if success_user and 'user' in user_response:
            self.regular_user = user_response['user']
            print(f"   Regular User: {self.regular_user.get('username', 'Unknown')}")
        
        return success_admin and success_user

    def create_business_user(self):
        """Create a business user for testing business information"""
        print("\n🏢 Creating business user for testing...")
        
        business_user_data = {
            "username": "business_seller",
            "email": "business@cataloro.com",
            "full_name": "Business Seller Account",
            "is_business": True,
            "business_name": "Cataloro Business Solutions",
            "company_name": "Cataloro Business Solutions"
        }
        
        success, response = self.run_test(
            "Create Business User",
            "POST",
            "api/auth/register",
            200,
            data=business_user_data
        )
        
        if success:
            # Login as business user to get full user object
            success_login, login_response = self.run_test(
                "Business User Login",
                "POST",
                "api/auth/login",
                200,
                data={"email": "business@cataloro.com", "password": "demo123"}
            )
            
            if success_login and 'user' in login_response:
                business_user = login_response['user']
                print(f"   Business User: {business_user.get('username', 'Unknown')}")
                print(f"   Is Business: {business_user.get('is_business', False)}")
                print(f"   Business Name: {business_user.get('business_name', 'N/A')}")
                return business_user
        
        return None

    def create_test_listing(self, seller_id, title_suffix=""):
        """Create a test listing for a seller"""
        listing_data = {
            "title": f"Test Listing for Seller Overview{title_suffix}",
            "description": "Test listing to verify seller information visibility in overview endpoint",
            "price": 299.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": seller_id,
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"],
            "tags": ["test", "seller", "overview"],
            "features": ["Test feature 1", "Test feature 2"]
        }
        
        success, response = self.run_test(
            f"Create Test Listing{title_suffix}",
            "POST",
            "api/listings",
            200,
            data=listing_data
        )
        
        if success and 'listing_id' in response:
            return response['listing_id']
        return None

    def test_seller_overview_endpoint(self):
        """Test the seller overview endpoint for complete seller information"""
        print("\n🎯 Testing Seller Overview Endpoint...")
        
        if not self.admin_user:
            print("❌ Seller Overview Test - SKIPPED (No admin user)")
            return False
        
        # Test with admin user (regular seller)
        success, response = self.run_test(
            "GET Seller Overview - Admin User",
            "GET",
            f"api/tenders/seller/{self.admin_user['id']}/overview",
            200
        )
        
        if success:
            print(f"   Found {len(response)} listings in overview")
            
            # Verify response structure
            if response:
                first_listing = response[0]
                
                # Check if seller information is present
                seller_info_present = 'seller' in first_listing
                self.log_test("Seller Information Present", seller_info_present,
                             f"Seller field in response: {seller_info_present}")
                
                if seller_info_present:
                    seller = first_listing['seller']
                    
                    # Check required seller fields
                    required_fields = ['id', 'username', 'full_name', 'is_business', 'business_name']
                    fields_present = all(field in seller for field in required_fields)
                    self.log_test("Seller Required Fields", fields_present,
                                 f"All required fields present: {fields_present}")
                    
                    # Verify seller data structure
                    print(f"   Seller ID: {seller.get('id', 'N/A')}")
                    print(f"   Username: {seller.get('username', 'N/A')}")
                    print(f"   Full Name: {seller.get('full_name', 'N/A')}")
                    print(f"   Is Business: {seller.get('is_business', 'N/A')}")
                    print(f"   Business Name: {seller.get('business_name', 'N/A')}")
                    
                    # Verify business indicators are available
                    business_indicators_present = (
                        'is_business' in seller and 
                        'business_name' in seller
                    )
                    self.log_test("Business Indicators Available", business_indicators_present,
                                 f"Business fields present: {business_indicators_present}")
                
                # Check if tenders have buyer information with business details
                if first_listing.get('tenders'):
                    first_tender = first_listing['tenders'][0]
                    if 'buyer' in first_tender:
                        buyer = first_tender['buyer']
                        buyer_business_fields = (
                            'is_business' in buyer and 
                            'business_name' in buyer
                        )
                        self.log_test("Buyer Business Fields", buyer_business_fields,
                                     f"Buyer business fields present: {buyer_business_fields}")
                        
                        print(f"   Buyer Is Business: {buyer.get('is_business', 'N/A')}")
                        print(f"   Buyer Business Name: {buyer.get('business_name', 'N/A')}")
            else:
                print("   No listings found in overview - creating test listing...")
                # Create a test listing for this seller
                listing_id = self.create_test_listing(self.admin_user['id'], " - Admin")
                if listing_id:
                    # Re-test the overview endpoint
                    success_retry, response_retry = self.run_test(
                        "GET Seller Overview - After Creating Listing",
                        "GET",
                        f"api/tenders/seller/{self.admin_user['id']}/overview",
                        200
                    )
                    
                    if success_retry and response_retry:
                        first_listing = response_retry[0]
                        seller_info_present = 'seller' in first_listing
                        self.log_test("Seller Information Present (Retry)", seller_info_present,
                                     f"Seller field in response: {seller_info_present}")
        
        return success

    def test_business_seller_overview(self):
        """Test seller overview with business user"""
        print("\n🏢 Testing Business Seller Overview...")
        
        # Create business user
        business_user = self.create_business_user()
        if not business_user:
            print("❌ Business Seller Overview - SKIPPED (Could not create business user)")
            return False
        
        # Create test listing for business user
        listing_id = self.create_test_listing(business_user['id'], " - Business")
        if not listing_id:
            print("❌ Business Seller Overview - SKIPPED (Could not create business listing)")
            return False
        
        # Test overview endpoint for business user
        success, response = self.run_test(
            "GET Business Seller Overview",
            "GET",
            f"api/tenders/seller/{business_user['id']}/overview",
            200
        )
        
        if success and response:
            first_listing = response[0]
            
            # Verify business seller information
            if 'seller' in first_listing:
                seller = first_listing['seller']
                
                # Check business-specific fields
                is_business = seller.get('is_business', False)
                business_name = seller.get('business_name', '')
                
                self.log_test("Business Seller is_business Flag", is_business,
                             f"is_business: {is_business}")
                self.log_test("Business Seller business_name Field", bool(business_name),
                             f"business_name: '{business_name}'")
                
                print(f"   Business Seller Details:")
                print(f"   - Username: {seller.get('username', 'N/A')}")
                print(f"   - Full Name: {seller.get('full_name', 'N/A')}")
                print(f"   - Is Business: {is_business}")
                print(f"   - Business Name: {business_name}")
                
                # Verify enhanced data structure
                enhanced_structure = (
                    is_business and 
                    business_name and 
                    'id' in seller and 
                    'username' in seller
                )
                self.log_test("Enhanced Business Data Structure", enhanced_structure,
                             f"Complete business data structure: {enhanced_structure}")
        
        # Cleanup: Delete test listing
        if listing_id:
            self.run_test(
                "Cleanup Business Test Listing",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
        
        return success

    def test_response_structure_completeness(self):
        """Test that the response structure includes all expected fields"""
        print("\n📋 Testing Response Structure Completeness...")
        
        if not self.regular_user:
            print("❌ Response Structure Test - SKIPPED (No regular user)")
            return False
        
        # Create test listing for regular user
        listing_id = self.create_test_listing(self.regular_user['id'], " - Structure Test")
        if not listing_id:
            print("❌ Response Structure Test - SKIPPED (Could not create test listing)")
            return False
        
        # Test overview endpoint
        success, response = self.run_test(
            "GET Seller Overview - Structure Test",
            "GET",
            f"api/tenders/seller/{self.regular_user['id']}/overview",
            200
        )
        
        if success and response:
            first_listing = response[0]
            
            # Check top-level structure
            expected_top_level = ['listing', 'seller', 'tender_count', 'highest_offer', 'tenders']
            top_level_complete = all(field in first_listing for field in expected_top_level)
            self.log_test("Top-Level Structure Complete", top_level_complete,
                         f"All top-level fields present: {top_level_complete}")
            
            # Check listing structure
            if 'listing' in first_listing:
                listing = first_listing['listing']
                expected_listing_fields = ['id', 'title', 'price', 'images', 'seller_id']
                listing_complete = all(field in listing for field in expected_listing_fields)
                self.log_test("Listing Structure Complete", listing_complete,
                             f"All listing fields present: {listing_complete}")
            
            # Check seller structure (main focus of this test)
            if 'seller' in first_listing:
                seller = first_listing['seller']
                expected_seller_fields = ['id', 'username', 'full_name', 'is_business', 'business_name']
                seller_complete = all(field in seller for field in expected_seller_fields)
                self.log_test("Seller Structure Complete", seller_complete,
                             f"All seller fields present: {seller_complete}")
                
                # Verify seller field types
                field_types_correct = (
                    isinstance(seller.get('id'), str) and
                    isinstance(seller.get('username'), str) and
                    isinstance(seller.get('full_name'), str) and
                    isinstance(seller.get('is_business'), bool) and
                    isinstance(seller.get('business_name'), str)
                )
                self.log_test("Seller Field Types Correct", field_types_correct,
                             f"All seller field types correct: {field_types_correct}")
            
            # Check tenders structure (if any tenders exist)
            tenders = first_listing.get('tenders', [])
            print(f"   Found {len(tenders)} tenders for structure testing")
            
            if tenders:
                first_tender = tenders[0]
                expected_tender_fields = ['id', 'offer_amount', 'created_at', 'buyer']
                tender_complete = all(field in first_tender for field in expected_tender_fields)
                self.log_test("Tender Structure Complete", tender_complete,
                             f"All tender fields present: {tender_complete}")
                
                # Check buyer structure in tenders
                if 'buyer' in first_tender:
                    buyer = first_tender['buyer']
                    expected_buyer_fields = ['id', 'username', 'full_name', 'is_business', 'business_name']
                    buyer_complete = all(field in buyer for field in expected_buyer_fields)
                    self.log_test("Buyer Structure Complete", buyer_complete,
                                 f"All buyer fields present: {buyer_complete}")
        
        # Cleanup: Delete test listing
        if listing_id:
            self.run_test(
                "Cleanup Structure Test Listing",
                "DELETE",
                f"api/listings/{listing_id}",
                200
            )
        
        return success

    def run_all_tests(self):
        """Run all seller overview tests"""
        print("🎯 SELLER INFORMATION VISIBILITY FIX TESTING")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users - stopping tests")
            return False
        
        # Run tests
        test_results = []
        
        # Test 1: Basic seller overview endpoint
        test_results.append(self.test_seller_overview_endpoint())
        
        # Test 2: Business seller overview
        test_results.append(self.test_business_seller_overview())
        
        # Test 3: Response structure completeness
        test_results.append(self.test_response_structure_completeness())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"\n📊 SELLER OVERVIEW TESTING SUMMARY")
        print("=" * 60)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        print(f"Major Test Categories: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL SELLER OVERVIEW TESTS PASSED!")
            print("✅ Seller information visibility fix is working correctly")
            print("✅ Complete seller information including business details is available")
            print("✅ Response structure includes all required fields")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} major test categories failed")
            print("❌ Seller information visibility fix needs attention")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = SellerOverviewTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)