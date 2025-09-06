#!/usr/bin/env python3
"""
Tender Offerer Visibility Fix Test Suite
Tests the ObjectId fallback logic for seller and buyer information visibility
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class TenderVisibilityTester:
    def __init__(self, base_url="https://browse-ads.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_seller_id = None
        self.test_buyer_id = None
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

    def make_request(self, method, endpoint, data=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            return response
        except Exception as e:
            print(f"Request failed: {str(e)}")
            return None

    def setup_test_data(self):
        """Create test users, listing, and tenders for comprehensive testing"""
        print("\n🔧 Setting up test data...")
        
        # Create test seller (business account)
        seller_data = {
            "username": "test_seller_business",
            "email": "seller@testbusiness.com",
            "full_name": "Business Seller",
            "is_business": True,
            "business_name": "Test Business Solutions",
            "company_name": "Test Business Solutions"
        }
        
        response = self.make_request('POST', 'api/auth/register', seller_data)
        if response and response.status_code == 200:
            result = response.json()
            self.test_seller_id = result.get('user_id')
            print(f"   ✅ Created test seller: {self.test_seller_id}")
        else:
            print(f"   ❌ Failed to create test seller: {response.status_code if response else 'No response'}")
            return False
        
        # Create test buyer (individual account)
        buyer_data = {
            "username": "test_buyer_individual",
            "email": "buyer@testindividual.com",
            "full_name": "Individual Buyer",
            "is_business": False
        }
        
        response = self.make_request('POST', 'api/auth/register', buyer_data)
        if response and response.status_code == 200:
            result = response.json()
            self.test_buyer_id = result.get('user_id')
            print(f"   ✅ Created test buyer: {self.test_buyer_id}")
        else:
            print(f"   ❌ Failed to create test buyer: {response.status_code if response else 'No response'}")
            return False
        
        # Create test listing
        listing_data = {
            "title": "Test Product for Tender Visibility",
            "description": "This is a test product to verify tender offerer visibility functionality",
            "price": 1500.00,
            "category": "Electronics",
            "condition": "New",
            "seller_id": self.test_seller_id,
            "images": ["https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=400"],
            "tags": ["test", "tender", "visibility"]
        }
        
        response = self.make_request('POST', 'api/listings', listing_data)
        if response and response.status_code == 200:
            result = response.json()
            self.test_listing_id = result.get('listing_id')
            print(f"   ✅ Created test listing: {self.test_listing_id}")
        else:
            print(f"   ❌ Failed to create test listing: {response.status_code if response else 'No response'}")
            return False
        
        # Create multiple test tenders
        tender_amounts = [1500.00, 1600.00, 1750.00]
        for amount in tender_amounts:
            tender_data = {
                "listing_id": self.test_listing_id,
                "buyer_id": self.test_buyer_id,
                "offer_amount": amount
            }
            
            response = self.make_request('POST', 'api/tenders/submit', tender_data)
            if response and response.status_code == 200:
                result = response.json()
                tender_id = result.get('tender_id')
                self.test_tender_ids.append(tender_id)
                print(f"   ✅ Created tender: €{amount} (ID: {tender_id})")
            else:
                print(f"   ❌ Failed to create tender for €{amount}: {response.status_code if response else 'No response'}")
        
        return len(self.test_tender_ids) > 0

    def test_seller_overview_endpoint_accessibility(self):
        """Test 1: Verify seller overview endpoint is accessible"""
        print("\n🔍 Test 1: Seller Overview Endpoint Accessibility")
        
        response = self.make_request('GET', f'api/tenders/seller/{self.test_seller_id}/overview')
        
        if response and response.status_code == 200:
            self.log_test("Seller Overview Endpoint Access", True, f"Status: {response.status_code}")
            return response.json()
        else:
            self.log_test("Seller Overview Endpoint Access", False, f"Status: {response.status_code if response else 'No response'}")
            return None

    def test_seller_information_population(self, overview_data):
        """Test 2: Verify seller information is properly populated"""
        print("\n🔍 Test 2: Seller Information Population")
        
        if not overview_data or len(overview_data) == 0:
            self.log_test("Seller Information Population", False, "No overview data available")
            return False
        
        # Check first listing's seller information
        first_listing = overview_data[0]
        seller_info = first_listing.get('seller', {})
        
        # Verify seller object is not empty
        if not seller_info or seller_info == {}:
            self.log_test("Seller Information Population", False, "Seller field is empty object {}")
            return False
        
        # Verify required seller fields
        required_fields = ['id', 'username', 'full_name', 'is_business', 'business_name']
        missing_fields = []
        
        for field in required_fields:
            if field not in seller_info:
                missing_fields.append(field)
        
        if missing_fields:
            self.log_test("Seller Information Population", False, f"Missing fields: {missing_fields}")
            return False
        
        # Verify business information is populated
        if seller_info.get('is_business') != True:
            self.log_test("Seller Information Population", False, f"is_business should be True, got: {seller_info.get('is_business')}")
            return False
        
        if not seller_info.get('business_name'):
            self.log_test("Seller Information Population", False, "business_name is empty")
            return False
        
        self.log_test("Seller Information Population", True, f"All seller fields populated correctly")
        print(f"   📋 Seller Info: {json.dumps(seller_info, indent=2)}")
        return True

    def test_buyer_information_population(self, overview_data):
        """Test 3: Verify buyer information is properly populated in tenders"""
        print("\n🔍 Test 3: Buyer Information Population")
        
        if not overview_data or len(overview_data) == 0:
            self.log_test("Buyer Information Population", False, "No overview data available")
            return False
        
        # Check tenders in the first listing
        first_listing = overview_data[0]
        tenders = first_listing.get('tenders', [])
        
        if len(tenders) == 0:
            self.log_test("Buyer Information Population", False, "No tenders found in overview")
            return False
        
        # Check buyer information in each tender
        for i, tender in enumerate(tenders):
            buyer_info = tender.get('buyer', {})
            
            # Verify buyer object is not empty
            if not buyer_info or buyer_info == {}:
                self.log_test("Buyer Information Population", False, f"Tender {i+1}: Buyer field is empty object {{}}")
                return False
            
            # Verify required buyer fields
            required_fields = ['id', 'username', 'full_name']
            missing_fields = []
            
            for field in required_fields:
                if field not in buyer_info or not buyer_info[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_test("Buyer Information Population", False, f"Tender {i+1}: Missing buyer fields: {missing_fields}")
                return False
        
        self.log_test("Buyer Information Population", True, f"All {len(tenders)} tenders have complete buyer information")
        
        # Print sample buyer info
        sample_buyer = tenders[0].get('buyer', {})
        print(f"   📋 Sample Buyer Info: {json.dumps(sample_buyer, indent=2)}")
        return True

    def test_tender_listing_association(self, overview_data):
        """Test 4: Verify tenders are properly associated with listings"""
        print("\n🔍 Test 4: Tender-Listing Association")
        
        if not overview_data or len(overview_data) == 0:
            self.log_test("Tender-Listing Association", False, "No overview data available")
            return False
        
        # Check that we have the expected listing
        found_test_listing = False
        for listing_data in overview_data:
            listing = listing_data.get('listing', {})
            if listing.get('id') == self.test_listing_id:
                found_test_listing = True
                
                # Verify listing has complete information
                required_listing_fields = ['id', 'title', 'price', 'seller_id']
                missing_fields = []
                
                for field in required_listing_fields:
                    if field not in listing or not listing[field]:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_test("Tender-Listing Association", False, f"Missing listing fields: {missing_fields}")
                    return False
                
                # Verify tender count matches expected
                expected_tender_count = len(self.test_tender_ids)
                actual_tender_count = listing_data.get('tender_count', 0)
                
                if actual_tender_count != expected_tender_count:
                    self.log_test("Tender-Listing Association", False, f"Expected {expected_tender_count} tenders, got {actual_tender_count}")
                    return False
                
                # Verify highest offer is correct
                tenders = listing_data.get('tenders', [])
                if tenders:
                    expected_highest = max([1500.00, 1600.00, 1750.00])  # Our test tender amounts
                    actual_highest = listing_data.get('highest_offer', 0)
                    
                    if actual_highest != expected_highest:
                        self.log_test("Tender-Listing Association", False, f"Expected highest offer €{expected_highest}, got €{actual_highest}")
                        return False
                
                break
        
        if not found_test_listing:
            self.log_test("Tender-Listing Association", False, "Test listing not found in overview")
            return False
        
        self.log_test("Tender-Listing Association", True, "Tenders properly associated with listings")
        return True

    def test_complete_data_structure(self, overview_data):
        """Test 5: Verify complete data structure for frontend display"""
        print("\n🔍 Test 5: Complete Data Structure Verification")
        
        if not overview_data or len(overview_data) == 0:
            self.log_test("Complete Data Structure", False, "No overview data available")
            return False
        
        # Verify overall structure
        first_listing = overview_data[0]
        required_top_level_fields = ['listing', 'seller', 'tender_count', 'highest_offer', 'tenders']
        
        missing_top_level = []
        for field in required_top_level_fields:
            if field not in first_listing:
                missing_top_level.append(field)
        
        if missing_top_level:
            self.log_test("Complete Data Structure", False, f"Missing top-level fields: {missing_top_level}")
            return False
        
        # Verify frontend can display "by [buyer name]" information
        tenders = first_listing.get('tenders', [])
        if tenders:
            for tender in tenders:
                buyer = tender.get('buyer', {})
                buyer_name = buyer.get('full_name') or buyer.get('username')
                
                if not buyer_name:
                    self.log_test("Complete Data Structure", False, "Cannot determine buyer name for 'by [buyer name]' display")
                    return False
        
        # Verify seller business information for display
        seller = first_listing.get('seller', {})
        if seller.get('is_business'):
            business_name = seller.get('business_name')
            if not business_name:
                self.log_test("Complete Data Structure", False, "Business seller missing business_name for display")
                return False
        
        self.log_test("Complete Data Structure", True, "All data structure requirements met for frontend display")
        return True

    def test_user_profile_endpoint_comparison(self):
        """Test 6: Compare with profile endpoint to verify consistency"""
        print("\n🔍 Test 6: Profile Endpoint Comparison")
        
        # Test seller profile endpoint
        response = self.make_request('GET', f'api/auth/profile/{self.test_seller_id}')
        
        if not response or response.status_code != 200:
            self.log_test("Profile Endpoint Comparison", False, f"Profile endpoint failed: {response.status_code if response else 'No response'}")
            return False
        
        profile_data = response.json()
        
        # Verify profile contains expected business information
        if not profile_data.get('is_business'):
            self.log_test("Profile Endpoint Comparison", False, "Profile endpoint missing business information")
            return False
        
        if not profile_data.get('business_name'):
            self.log_test("Profile Endpoint Comparison", False, "Profile endpoint missing business_name")
            return False
        
        self.log_test("Profile Endpoint Comparison", True, "Profile endpoint returns complete business information")
        print(f"   📋 Profile Data: {json.dumps(profile_data, indent=2)}")
        return True

    def run_comprehensive_test(self):
        """Run all tender visibility tests"""
        print("🎯 TENDER OFFERER VISIBILITY FIX COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Setup test data
        if not self.setup_test_data():
            print("\n❌ CRITICAL: Failed to setup test data. Cannot proceed with testing.")
            return False
        
        # Test 1: Endpoint accessibility
        overview_data = self.test_seller_overview_endpoint_accessibility()
        if not overview_data:
            print("\n❌ CRITICAL: Cannot access seller overview endpoint. Stopping tests.")
            return False
        
        # Test 2: Seller information population
        seller_test_passed = self.test_seller_information_population(overview_data)
        
        # Test 3: Buyer information population
        buyer_test_passed = self.test_buyer_information_population(overview_data)
        
        # Test 4: Tender-listing association
        association_test_passed = self.test_tender_listing_association(overview_data)
        
        # Test 5: Complete data structure
        structure_test_passed = self.test_complete_data_structure(overview_data)
        
        # Test 6: Profile endpoint comparison
        profile_test_passed = self.test_user_profile_endpoint_comparison()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 TENDER OFFERER VISIBILITY TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Determine overall status
        critical_tests_passed = seller_test_passed and buyer_test_passed and association_test_passed
        
        if critical_tests_passed:
            print("\n✅ TENDER OFFERER VISIBILITY FIX: WORKING")
            print("   - Seller information properly populated")
            print("   - Buyer information properly populated")
            print("   - Tenders properly associated with listings")
            print("   - Frontend can display complete offerer information")
        else:
            print("\n❌ TENDER OFFERER VISIBILITY FIX: NOT WORKING")
            if not seller_test_passed:
                print("   - Seller information population FAILED")
            if not buyer_test_passed:
                print("   - Buyer information population FAILED")
            if not association_test_passed:
                print("   - Tender-listing association FAILED")
        
        return critical_tests_passed

if __name__ == "__main__":
    tester = TenderVisibilityTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)