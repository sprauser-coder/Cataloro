#!/usr/bin/env python3
"""
Tender Offerer Visibility Test
Tests the tender offerer visibility issue by creating test tender data 
and verifying that buyer information is properly returned in the seller overview endpoint.
"""

import requests
import sys
import json
from datetime import datetime

class TenderVisibilityTester:
    def __init__(self, base_url="https://cataloro-marketplace-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test data storage
        self.seller_user = None
        self.buyer_user = None
        self.test_listing_id = None
        self.test_tender_ids = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_api_call(self, method, endpoint, expected_status, data=None):
        """Make API call and return response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            return success, response.json() if success and response.text else {}, response.status_code
            
        except Exception as e:
            print(f"API call error: {str(e)}")
            return False, {}, 0

    def setup_test_users(self):
        """Create test users for tender testing"""
        print("\n🔧 Setting up test users...")
        
        # Create seller user (business account)
        seller_data = {
            "email": "seller@tendertest.com",
            "password": "test123",
            "username": "tender_seller",
            "full_name": "John Doe Business",
            "is_business": True,
            "business_name": "Doe Enterprises Ltd"
        }
        
        success, response, status = self.run_api_call('POST', 'api/auth/login', 200, seller_data)
        if success:
            self.seller_user = response.get('user')
            print(f"   ✅ Seller user created/logged in: {self.seller_user.get('username')} (Business: {self.seller_user.get('is_business', False)})")
        else:
            print(f"   ⚠️  Seller login failed with status {status}, trying registration...")
            # Try registration if login fails
            reg_success, reg_response, reg_status = self.run_api_call('POST', 'api/auth/register', 200, seller_data)
            if reg_success:
                # Login after registration
                success, response, status = self.run_api_call('POST', 'api/auth/login', 200, seller_data)
                if success:
                    self.seller_user = response.get('user')
                    print(f"   ✅ Seller user registered and logged in: {self.seller_user.get('username')}")
        
        # Create buyer user (individual account)
        buyer_data = {
            "email": "buyer@tendertest.com", 
            "password": "test123",
            "username": "tender_buyer",
            "full_name": "Jane Smith",
            "is_business": False,
            "business_name": ""
        }
        
        success, response, status = self.run_api_call('POST', 'api/auth/login', 200, buyer_data)
        if success:
            self.buyer_user = response.get('user')
            print(f"   ✅ Buyer user created/logged in: {self.buyer_user.get('username')} (Business: {self.buyer_user.get('is_business', False)})")
        else:
            print(f"   ⚠️  Buyer login failed with status {status}, trying registration...")
            # Try registration if login fails
            reg_success, reg_response, reg_status = self.run_api_call('POST', 'api/auth/register', 200, buyer_data)
            if reg_success:
                # Login after registration
                success, response, status = self.run_api_call('POST', 'api/auth/login', 200, buyer_data)
                if success:
                    self.buyer_user = response.get('user')
                    print(f"   ✅ Buyer user registered and logged in: {self.buyer_user.get('username')}")
        
        self.log_test("Test Users Setup", 
                     self.seller_user is not None and self.buyer_user is not None,
                     f"Seller: {self.seller_user.get('username') if self.seller_user else 'None'}, Buyer: {self.buyer_user.get('username') if self.buyer_user else 'None'}")
        
        return self.seller_user is not None and self.buyer_user is not None

    def create_test_listing(self):
        """Create a test listing for tender testing"""
        print("\n📝 Creating test listing...")
        
        if not self.seller_user:
            print("❌ No seller user available")
            return False
        
        listing_data = {
            "title": "Tender Test Item - Premium Laptop",
            "description": "High-end laptop for tender testing. Excellent condition with warranty.",
            "price": 1500.00,
            "category": "Electronics",
            "condition": "Used - Excellent", 
            "seller_id": self.seller_user['id'],
            "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400"],
            "tags": ["laptop", "computer", "premium"],
            "features": ["16GB RAM", "512GB SSD", "Intel i7"]
        }
        
        success, response, status = self.run_api_call('POST', 'api/listings', 200, listing_data)
        if success:
            self.test_listing_id = response.get('listing_id')
            print(f"   ✅ Test listing created: {self.test_listing_id}")
            print(f"   📋 Listing: {listing_data['title']} - €{listing_data['price']}")
        
        self.log_test("Test Listing Creation", success, 
                     f"Listing ID: {self.test_listing_id if success else 'Failed'}")
        
        return success

    def submit_test_tenders(self):
        """Submit multiple test tender offers"""
        print("\n💰 Submitting test tender offers...")
        
        if not self.buyer_user or not self.test_listing_id:
            print("❌ Missing buyer user or test listing")
            return False
        
        # Submit multiple tender offers with different amounts (must be >= listing price of 1500)
        tender_offers = [
            {"amount": 1500.00, "description": "First offer - starting price"},
            {"amount": 1600.00, "description": "Second offer - better price"},
            {"amount": 1750.00, "description": "Third offer - competitive price"}
        ]
        
        success_count = 0
        for i, offer in enumerate(tender_offers):
            tender_data = {
                "listing_id": self.test_listing_id,
                "buyer_id": self.buyer_user['id'],
                "offer_amount": offer["amount"]
            }
            
            success, response, status = self.run_api_call('POST', 'api/tenders/submit', 200, tender_data)
            if success:
                tender_id = response.get('tender_id')
                self.test_tender_ids.append(tender_id)
                success_count += 1
                print(f"   ✅ Tender {i+1} submitted: €{offer['amount']} (ID: {tender_id})")
            else:
                print(f"   ❌ Tender {i+1} failed: Status {status}")
        
        self.log_test("Test Tender Submissions", success_count > 0,
                     f"Successfully submitted {success_count}/{len(tender_offers)} tenders")
        
        return success_count > 0

    def test_seller_overview_endpoint(self):
        """Test the seller overview endpoint for buyer information visibility"""
        print("\n🔍 Testing seller overview endpoint for buyer information...")
        
        if not self.seller_user:
            print("❌ No seller user available")
            return False
        
        # Call the seller overview endpoint
        success, response, status = self.run_api_call('GET', f'api/tenders/seller/{self.seller_user["id"]}/overview', 200)
        
        if not success:
            self.log_test("Seller Overview Endpoint Access", False, f"Status: {status}")
            return False
        
        self.log_test("Seller Overview Endpoint Access", True, f"Status: {status}")
        
        # Analyze the response structure
        print(f"\n📊 Analyzing seller overview response...")
        print(f"   Response type: {type(response)}")
        print(f"   Response length: {len(response) if isinstance(response, list) else 'Not a list'}")
        
        if not isinstance(response, list):
            self.log_test("Response Structure", False, "Expected list, got different type")
            return False
        
        if len(response) == 0:
            print("   ⚠️  No listings found in seller overview")
            self.log_test("Listings Found", False, "No listings in overview")
            return False
        
        # Check the first listing for structure
        first_listing = response[0]
        print(f"\n🔍 Examining first listing structure:")
        print(f"   Keys: {list(first_listing.keys())}")
        
        # Check required top-level fields
        required_fields = ['listing', 'seller', 'tender_count', 'highest_offer', 'tenders']
        missing_fields = [field for field in required_fields if field not in first_listing]
        
        if missing_fields:
            self.log_test("Response Structure - Required Fields", False, f"Missing fields: {missing_fields}")
            return False
        
        self.log_test("Response Structure - Required Fields", True, "All required fields present")
        
        # Check seller information
        seller_info = first_listing.get('seller', {})
        print(f"\n👤 Examining seller information:")
        print(f"   Seller info: {seller_info}")
        print(f"   Seller info type: {type(seller_info)}")
        print(f"   Seller info keys: {list(seller_info.keys()) if isinstance(seller_info, dict) else 'Not a dict'}")
        
        # Check if seller info is populated
        seller_populated = bool(seller_info and isinstance(seller_info, dict) and seller_info.get('id'))
        self.log_test("Seller Information Population", seller_populated, 
                     f"Seller info populated: {seller_populated}")
        
        if seller_populated:
            # Check seller business information
            seller_business_fields = ['is_business', 'business_name', 'full_name', 'username']
            seller_business_present = any(field in seller_info for field in seller_business_fields)
            self.log_test("Seller Business Information", seller_business_present,
                         f"Business fields present: {seller_business_present}")
        
        # Check tender information and buyer data
        tenders = first_listing.get('tenders', [])
        print(f"\n💰 Examining tender information:")
        print(f"   Tender count: {len(tenders)}")
        print(f"   Tender count field: {first_listing.get('tender_count', 'Missing')}")
        
        if len(tenders) == 0:
            print("   ⚠️  No tenders found for this listing")
            self.log_test("Tenders Found", False, "No tenders in listing")
            return False
        
        # Check buyer information in tenders
        buyer_info_issues = []
        for i, tender in enumerate(tenders):
            print(f"\n   Tender {i+1}:")
            print(f"     Tender keys: {list(tender.keys())}")
            
            buyer_info = tender.get('buyer', {})
            print(f"     Buyer info: {buyer_info}")
            print(f"     Buyer info type: {type(buyer_info)}")
            
            # Check if buyer info is populated
            if not buyer_info or not isinstance(buyer_info, dict):
                buyer_info_issues.append(f"Tender {i+1}: Buyer info missing or invalid type")
                continue
            
            # Check required buyer fields
            required_buyer_fields = ['id', 'username', 'full_name']
            missing_buyer_fields = [field for field in required_buyer_fields if not buyer_info.get(field)]
            
            if missing_buyer_fields:
                buyer_info_issues.append(f"Tender {i+1}: Missing buyer fields: {missing_buyer_fields}")
            else:
                print(f"     ✅ Buyer info complete: {buyer_info.get('full_name')} ({buyer_info.get('username')})")
        
        # Log buyer information test results
        buyer_info_success = len(buyer_info_issues) == 0
        self.log_test("Buyer Information Visibility", buyer_info_success,
                     f"Issues found: {len(buyer_info_issues)}")
        
        if buyer_info_issues:
            print("\n❌ Buyer Information Issues:")
            for issue in buyer_info_issues:
                print(f"   - {issue}")
        
        # Check business information visibility
        business_info_visible = False
        for tender in tenders:
            buyer = tender.get('buyer', {})
            if buyer.get('is_business') is not None or buyer.get('business_name'):
                business_info_visible = True
                break
        
        self.log_test("Business Information Visibility", business_info_visible,
                     f"Business fields visible in buyer data: {business_info_visible}")
        
        return buyer_info_success

    def verify_buyer_data_completeness(self):
        """Verify that buyer data includes all necessary fields for frontend display"""
        print("\n🔍 Verifying buyer data completeness for frontend display...")
        
        if not self.buyer_user:
            print("❌ No buyer user available")
            return False
        
        # Get buyer profile directly to compare
        success, profile_response, status = self.run_api_call('GET', f'api/auth/profile/{self.buyer_user["id"]}', 200)
        
        if not success:
            self.log_test("Buyer Profile Access", False, f"Status: {status}")
            return False
        
        print(f"   ✅ Buyer profile retrieved: {profile_response.get('full_name', 'Unknown')}")
        print(f"   📋 Profile fields: {list(profile_response.keys())}")
        
        # Now get seller overview and compare buyer data
        success, overview_response, status = self.run_api_call('GET', f'api/tenders/seller/{self.seller_user["id"]}/overview', 200)
        
        if not success or not overview_response:
            self.log_test("Seller Overview for Comparison", False, "Could not get overview")
            return False
        
        # Find buyer data in tenders
        buyer_data_in_tenders = []
        for listing in overview_response:
            for tender in listing.get('tenders', []):
                buyer_info = tender.get('buyer', {})
                if buyer_info.get('id') == self.buyer_user['id']:
                    buyer_data_in_tenders.append(buyer_info)
        
        if not buyer_data_in_tenders:
            self.log_test("Buyer Data in Tenders", False, "Buyer not found in tender data")
            return False
        
        # Compare profile data with tender buyer data
        profile_fields = ['id', 'username', 'full_name', 'is_business', 'business_name']
        comparison_results = []
        
        for buyer_data in buyer_data_in_tenders:
            for field in profile_fields:
                profile_value = profile_response.get(field)
                tender_value = buyer_data.get(field)
                
                if profile_value != tender_value:
                    comparison_results.append(f"Field '{field}': Profile='{profile_value}' vs Tender='{tender_value}'")
        
        data_consistency = len(comparison_results) == 0
        self.log_test("Buyer Data Consistency", data_consistency,
                     f"Inconsistencies: {len(comparison_results)}")
        
        if comparison_results:
            print("   ⚠️  Data inconsistencies found:")
            for result in comparison_results:
                print(f"     - {result}")
        
        # Check if all required fields for frontend display are present
        required_for_frontend = ['full_name', 'username']
        frontend_ready = all(buyer_data_in_tenders[0].get(field) for field in required_for_frontend)
        
        self.log_test("Frontend Display Ready", frontend_ready,
                     f"Required fields present: {frontend_ready}")
        
        return data_consistency and frontend_ready

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test listing
        if self.test_listing_id:
            success, response, status = self.run_api_call('DELETE', f'api/listings/{self.test_listing_id}', 200)
            if success:
                print(f"   ✅ Test listing deleted: {self.test_listing_id}")
            else:
                print(f"   ⚠️  Failed to delete test listing: Status {status}")

    def run_all_tests(self):
        """Run all tender visibility tests"""
        print("🎯 TENDER OFFERER VISIBILITY TESTING")
        print("=" * 50)
        
        # Test sequence
        tests = [
            ("Setup Test Users", self.setup_test_users),
            ("Create Test Listing", self.create_test_listing),
            ("Submit Test Tenders", self.submit_test_tenders),
            ("Test Seller Overview Endpoint", self.test_seller_overview_endpoint),
            ("Verify Buyer Data Completeness", self.verify_buyer_data_completeness)
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                success = test_func()
                if not success:
                    print(f"\n❌ {test_name} failed - stopping test sequence")
                    break
            except Exception as e:
                print(f"\n❌ {test_name} error: {str(e)}")
                break
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print(f"\n{'='*50}")
        print(f"🎯 TENDER VISIBILITY TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "No tests run")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Tender offerer visibility working correctly!")
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed - Issues found with tender offerer visibility")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = TenderVisibilityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)