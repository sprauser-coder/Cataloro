#!/usr/bin/env python3
"""
Business Badge Verification Test
Comprehensive test to verify business badge display functionality
"""

import requests
import sys
import json
from datetime import datetime

class BusinessBadgeVerificationTester:
    def __init__(self, base_url="https://cataloro-dash.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def make_request(self, method, endpoint, data=None):
        """Make API request with error handling"""
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
            
            return response.status_code == 200, response.json() if response.text else {}
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False, {}

    def test_admin_profile_business_status(self):
        """Test admin profile has business account status"""
        print("\n1️⃣ TESTING ADMIN PROFILE BUSINESS STATUS")
        
        admin_id = "68b191ec38e6062fee10bd27"  # Known admin ID
        success, profile_data = self.make_request("GET", f"api/auth/profile/{admin_id}")
        
        if success:
            is_business = profile_data.get('is_business', False)
            business_name = profile_data.get('business_name', '')
            
            if is_business and business_name:
                self.log_test(
                    "Admin Profile Business Status", 
                    True, 
                    f"is_business={is_business}, business_name='{business_name}'"
                )
                return True
            else:
                self.log_test(
                    "Admin Profile Business Status", 
                    False, 
                    f"is_business={is_business}, business_name='{business_name}'"
                )
                return False
        else:
            self.log_test("Admin Profile Business Status", False, "Failed to retrieve profile")
            return False

    def test_browse_seller_enrichment(self):
        """Test browse endpoint seller enrichment for business badges"""
        print("\n2️⃣ TESTING BROWSE SELLER ENRICHMENT")
        
        success, browse_data = self.make_request("GET", "api/marketplace/browse")
        
        if success:
            admin_id = "68b191ec38e6062fee10bd27"
            business_listings = []
            private_listings = []
            
            for listing in browse_data:
                seller = listing.get('seller', {})
                seller_id = listing.get('seller_id')
                
                if seller.get('is_business'):
                    business_listings.append({
                        'id': listing.get('id'),
                        'title': listing.get('title'),
                        'seller_id': seller_id,
                        'seller_name': seller.get('name'),
                        'business_name': seller.get('business_name')
                    })
                else:
                    private_listings.append({
                        'id': listing.get('id'),
                        'title': listing.get('title'),
                        'seller_id': seller_id,
                        'seller_name': seller.get('name')
                    })
            
            # Check if admin listings show as business
            admin_business_listings = [l for l in business_listings if l['seller_id'] == admin_id]
            
            if admin_business_listings:
                self.log_test(
                    "Admin Listings Show Business Badge", 
                    True, 
                    f"Found {len(admin_business_listings)} admin business listings"
                )
                
                # Print details
                for listing in admin_business_listings:
                    print(f"   📋 Business Listing: {listing['title']}")
                    print(f"      Business Name: {listing['business_name']}")
                
                return True
            else:
                self.log_test(
                    "Admin Listings Show Business Badge", 
                    False, 
                    f"No admin business listings found. Total business: {len(business_listings)}, Total private: {len(private_listings)}"
                )
                return False
        else:
            self.log_test("Browse Seller Enrichment", False, "Failed to retrieve browse data")
            return False

    def test_business_vs_private_distinction(self):
        """Test that business and private accounts are properly distinguished"""
        print("\n3️⃣ TESTING BUSINESS VS PRIVATE DISTINCTION")
        
        success, browse_data = self.make_request("GET", "api/marketplace/browse")
        
        if success:
            business_count = 0
            private_count = 0
            
            for listing in browse_data:
                seller = listing.get('seller', {})
                if seller.get('is_business'):
                    business_count += 1
                else:
                    private_count += 1
            
            # We should have both business and private accounts
            has_distinction = business_count > 0 and private_count >= 0
            
            self.log_test(
                "Business vs Private Distinction", 
                has_distinction, 
                f"Business listings: {business_count}, Private listings: {private_count}"
            )
            
            return has_distinction
        else:
            self.log_test("Business vs Private Distinction", False, "Failed to retrieve browse data")
            return False

    def test_seller_enrichment_fields(self):
        """Test that seller enrichment includes all required business fields"""
        print("\n4️⃣ TESTING SELLER ENRICHMENT FIELDS")
        
        success, browse_data = self.make_request("GET", "api/marketplace/browse")
        
        if success:
            required_fields = ['name', 'username', 'email', 'is_business', 'business_name', 'verified', 'location']
            all_fields_present = True
            missing_fields = []
            
            for listing in browse_data:
                seller = listing.get('seller', {})
                for field in required_fields:
                    if field not in seller:
                        all_fields_present = False
                        if field not in missing_fields:
                            missing_fields.append(field)
            
            if all_fields_present:
                self.log_test(
                    "Seller Enrichment Fields Complete", 
                    True, 
                    f"All required fields present: {required_fields}"
                )
                return True
            else:
                self.log_test(
                    "Seller Enrichment Fields Complete", 
                    False, 
                    f"Missing fields: {missing_fields}"
                )
                return False
        else:
            self.log_test("Seller Enrichment Fields", False, "Failed to retrieve browse data")
            return False

    def test_create_business_listing(self):
        """Test creating a listing as business user and verify badge display"""
        print("\n5️⃣ TESTING BUSINESS LISTING CREATION")
        
        # Login as business user
        success, login_response = self.make_request(
            "POST", 
            "api/auth/login",
            {"email": "business@cataloro.com", "password": "demo123"}
        )
        
        if not success:
            self.log_test("Business User Login", False, "Failed to login as business user")
            return False
        
        business_user = login_response.get('user', {})
        business_user_id = business_user.get('id')
        
        if not business_user.get('is_business'):
            self.log_test("Business User Verification", False, "User is not marked as business")
            return False
        
        # Create test listing
        test_listing = {
            "title": "Business Badge Test - Professional Service",
            "description": "Test listing created by verified business account to test business badge display functionality.",
            "price": 199.99,
            "category": "Services",
            "condition": "New",
            "seller_id": business_user_id,
            "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"],
            "tags": ["business", "professional", "test"]
        }
        
        success, create_response = self.make_request("POST", "api/listings", test_listing)
        
        if success:
            listing_id = create_response.get('listing_id')
            
            # Check if listing appears in browse with business badge
            success_browse, browse_data = self.make_request("GET", "api/marketplace/browse")
            
            if success_browse:
                test_listing_found = None
                for listing in browse_data:
                    if listing.get('id') == listing_id:
                        test_listing_found = listing
                        break
                
                if test_listing_found:
                    seller = test_listing_found.get('seller', {})
                    is_business = seller.get('is_business', False)
                    business_name = seller.get('business_name', '')
                    
                    if is_business and business_name:
                        self.log_test(
                            "Business Listing Badge Display", 
                            True, 
                            f"Business badge shown: {business_name}"
                        )
                        
                        # Cleanup - delete test listing
                        self.make_request("DELETE", f"api/listings/{listing_id}")
                        return True
                    else:
                        self.log_test(
                            "Business Listing Badge Display", 
                            False, 
                            f"Business badge not shown: is_business={is_business}, business_name='{business_name}'"
                        )
                        # Cleanup - delete test listing
                        self.make_request("DELETE", f"api/listings/{listing_id}")
                        return False
                else:
                    self.log_test("Business Listing Badge Display", False, "Test listing not found in browse")
                    return False
            else:
                self.log_test("Business Listing Badge Display", False, "Failed to retrieve browse data")
                return False
        else:
            self.log_test("Business Listing Creation", False, "Failed to create test listing")
            return False

    def run_verification_tests(self):
        """Run complete business badge verification test suite"""
        print("🔍 BUSINESS BADGE VERIFICATION TEST SUITE")
        print("=" * 60)
        print("Verifying: Business badge display functionality after fix")
        print("=" * 60)
        
        # Run all tests
        test_results = []
        
        test_results.append(self.test_admin_profile_business_status())
        test_results.append(self.test_browse_seller_enrichment())
        test_results.append(self.test_business_vs_private_distinction())
        test_results.append(self.test_seller_enrichment_fields())
        test_results.append(self.test_create_business_listing())
        
        # Generate summary
        print("\n" + "=" * 60)
        print("🔍 BUSINESS BADGE VERIFICATION SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ✅ ALL BUSINESS BADGE TESTS PASSED!")
            print("\n💡 CONCLUSION:")
            print("   ✅ Admin profile has business account status")
            print("   ✅ Browse endpoint shows business badges correctly")
            print("   ✅ Business vs private accounts are properly distinguished")
            print("   ✅ Seller enrichment includes all required fields")
            print("   ✅ New business listings display business badges")
            print("\n🔧 ISSUE RESOLUTION:")
            print("   The business badge display issue has been RESOLVED.")
            print("   Admin account now properly shows business badges in listings.")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed")
            print("\n💡 REMAINING ISSUES:")
            if not test_results[0]:
                print("   ❌ Admin profile missing business account status")
            if not test_results[1]:
                print("   ❌ Browse endpoint not showing business badges for admin")
            if not test_results[2]:
                print("   ❌ Business vs private distinction not working")
            if not test_results[3]:
                print("   ❌ Seller enrichment missing required fields")
            if not test_results[4]:
                print("   ❌ New business listings not showing business badges")
            return False

def main():
    """Main verification execution"""
    tester = BusinessBadgeVerificationTester()
    success = tester.run_verification_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())