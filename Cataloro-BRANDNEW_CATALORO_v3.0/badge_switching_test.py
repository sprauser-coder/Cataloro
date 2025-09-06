#!/usr/bin/env python3
"""
Badge Switching Issue Debug Test
Tests the specific issue where users change account type from business to private 
but browse listings still show old "Business" badges instead of updating to "Private" badges.
"""

import requests
import sys
import json
from datetime import datetime
import time

class BadgeSwitchingTester:
    def __init__(self, base_url="https://cataloro-ads.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.business_user = None
        self.business_user_token = None
        self.test_listing_id = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_api_call(self, method, endpoint, data=None, expected_status=200):
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
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            success = response.status_code == expected_status
            return success, response.json() if response.text else {}, response.status_code
        except Exception as e:
            print(f"API Error: {str(e)}")
            return False, {}, 0

    def test_1_create_business_user(self):
        """Step 1: Create a business user account"""
        print("\n🏢 Step 1: Creating Business User Account...")
        
        # First login as admin to get admin user
        success, admin_response, _ = self.run_api_call(
            'POST', 'api/auth/login',
            {"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if not success:
            self.log_test("Admin Login for Business User Creation", False, "Could not login as admin")
            return False
        
        admin_user = admin_response.get('user')
        if not admin_user:
            self.log_test("Admin Login for Business User Creation", False, "No admin user data")
            return False
        
        # Update admin user to be a business account
        business_update_data = {
            "is_business": True,
            "business_name": "Cataloro Business Solutions",
            "company_name": "Cataloro Business Solutions"
        }
        
        success, update_response, status = self.run_api_call(
            'PUT', f'api/admin/users/{admin_user["id"]}',
            business_update_data
        )
        
        if success:
            print(f"   ✅ Updated admin user to business account")
            self.business_user = admin_user
            self.business_user_token = admin_response.get('token')
            self.log_test("Create Business User", True, f"Admin user converted to business: {admin_user['email']}")
            return True
        else:
            self.log_test("Create Business User", False, f"Failed to update user to business (Status: {status})")
            return False

    def test_2_verify_business_profile(self):
        """Step 2: Verify the business profile data in database"""
        print("\n🔍 Step 2: Verifying Business Profile in Database...")
        
        if not self.business_user:
            self.log_test("Verify Business Profile", False, "No business user available")
            return False
        
        success, profile_response, status = self.run_api_call(
            'GET', f'api/auth/profile/{self.business_user["id"]}'
        )
        
        if success:
            is_business = profile_response.get('is_business', False)
            business_name = profile_response.get('business_name', '')
            company_name = profile_response.get('company_name', '')
            
            print(f"   📊 Profile Data:")
            print(f"      is_business: {is_business}")
            print(f"      business_name: {business_name}")
            print(f"      company_name: {company_name}")
            
            if is_business:
                self.log_test("Verify Business Profile", True, f"Business profile confirmed: {business_name}")
                return True
            else:
                self.log_test("Verify Business Profile", False, "is_business flag is False")
                return False
        else:
            self.log_test("Verify Business Profile", False, f"Could not fetch profile (Status: {status})")
            return False

    def test_3_create_business_listing(self):
        """Step 3: Create a listing from the business user"""
        print("\n📝 Step 3: Creating Listing from Business User...")
        
        if not self.business_user:
            self.log_test("Create Business Listing", False, "No business user available")
            return False
        
        business_listing = {
            "title": "Badge Test Listing - Professional Camera Equipment",
            "description": "Professional camera equipment from Cataloro Business Solutions. High-quality gear for professionals.",
            "price": 1299.99,
            "category": "Photography",
            "condition": "Used - Excellent",
            "seller_id": self.business_user['id'],
            "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"],
            "tags": ["professional", "camera", "business"],
            "features": ["Professional grade", "Business seller", "Warranty included"]
        }
        
        success, create_response, status = self.run_api_call(
            'POST', 'api/listings',
            business_listing
        )
        
        if success and 'listing_id' in create_response:
            self.test_listing_id = create_response['listing_id']
            print(f"   ✅ Created business listing with ID: {self.test_listing_id}")
            self.log_test("Create Business Listing", True, f"Listing created: {self.test_listing_id}")
            return True
        else:
            self.log_test("Create Business Listing", False, f"Failed to create listing (Status: {status})")
            return False

    def test_4_verify_business_badge_in_browse(self):
        """Step 4: Verify business badge appears in browse listings"""
        print("\n🏷️ Step 4: Verifying Business Badge in Browse Listings...")
        
        if not self.test_listing_id:
            self.log_test("Verify Business Badge", False, "No test listing available")
            return False
        
        success, browse_response, status = self.run_api_call(
            'GET', 'api/marketplace/browse'
        )
        
        if not success:
            self.log_test("Verify Business Badge", False, f"Could not fetch browse listings (Status: {status})")
            return False
        
        # Find our test listing
        test_listing = None
        for listing in browse_response:
            if listing.get('id') == self.test_listing_id:
                test_listing = listing
                break
        
        if not test_listing:
            self.log_test("Verify Business Badge", False, "Test listing not found in browse results")
            return False
        
        # Check seller information
        seller = test_listing.get('seller', {})
        is_business = seller.get('is_business', False)
        business_name = seller.get('business_name', '')
        
        print(f"   📊 Seller Data in Browse:")
        print(f"      seller.name: {seller.get('name', 'N/A')}")
        print(f"      seller.username: {seller.get('username', 'N/A')}")
        print(f"      seller.is_business: {is_business}")
        print(f"      seller.business_name: {business_name}")
        
        if is_business:
            self.log_test("Verify Business Badge", True, f"Business badge correctly shown: {business_name}")
            return True
        else:
            self.log_test("Verify Business Badge", False, "Business badge NOT shown (is_business=False)")
            return False

    def test_5_change_to_private_account(self):
        """Step 5: Change account type from Business to Private"""
        print("\n🔄 Step 5: Changing Account from Business to Private...")
        
        if not self.business_user:
            self.log_test("Change to Private Account", False, "No business user available")
            return False
        
        # Update user to private account
        private_update_data = {
            "is_business": False,
            "business_name": "",
            "company_name": ""
        }
        
        success, update_response, status = self.run_api_call(
            'PUT', f'api/admin/users/{self.business_user["id"]}',
            private_update_data
        )
        
        if success:
            print(f"   ✅ Updated user to private account")
            self.log_test("Change to Private Account", True, "User converted to private account")
            return True
        else:
            self.log_test("Change to Private Account", False, f"Failed to update user to private (Status: {status})")
            return False

    def test_6_verify_private_profile(self):
        """Step 6: Verify the profile change persisted in database"""
        print("\n🔍 Step 6: Verifying Private Profile in Database...")
        
        if not self.business_user:
            self.log_test("Verify Private Profile", False, "No user available")
            return False
        
        success, profile_response, status = self.run_api_call(
            'GET', f'api/auth/profile/{self.business_user["id"]}'
        )
        
        if success:
            is_business = profile_response.get('is_business', True)  # Default True to catch the issue
            business_name = profile_response.get('business_name', '')
            company_name = profile_response.get('company_name', '')
            
            print(f"   📊 Updated Profile Data:")
            print(f"      is_business: {is_business}")
            print(f"      business_name: {business_name}")
            print(f"      company_name: {company_name}")
            
            if not is_business:
                self.log_test("Verify Private Profile", True, "Profile successfully changed to private")
                return True
            else:
                self.log_test("Verify Private Profile", False, "Profile still shows as business account")
                return False
        else:
            self.log_test("Verify Private Profile", False, f"Could not fetch updated profile (Status: {status})")
            return False

    def test_7_check_browse_badge_update(self):
        """Step 7: Check if browse endpoint shows updated badge (CRITICAL TEST)"""
        print("\n🎯 Step 7: CRITICAL TEST - Checking Browse Badge Update...")
        
        if not self.test_listing_id:
            self.log_test("Check Browse Badge Update", False, "No test listing available")
            return False
        
        # Add small delay to ensure any caching is cleared
        print("   ⏳ Waiting 2 seconds for any caching to clear...")
        time.sleep(2)
        
        success, browse_response, status = self.run_api_call(
            'GET', 'api/marketplace/browse'
        )
        
        if not success:
            self.log_test("Check Browse Badge Update", False, f"Could not fetch browse listings (Status: {status})")
            return False
        
        # Find our test listing
        test_listing = None
        for listing in browse_response:
            if listing.get('id') == self.test_listing_id:
                test_listing = listing
                break
        
        if not test_listing:
            self.log_test("Check Browse Badge Update", False, "Test listing not found in browse results")
            return False
        
        # Check seller information after profile change
        seller = test_listing.get('seller', {})
        is_business = seller.get('is_business', True)  # Default True to catch the issue
        business_name = seller.get('business_name', '')
        
        print(f"   📊 Seller Data After Profile Change:")
        print(f"      seller.name: {seller.get('name', 'N/A')}")
        print(f"      seller.username: {seller.get('username', 'N/A')}")
        print(f"      seller.is_business: {is_business}")
        print(f"      seller.business_name: {business_name}")
        
        if not is_business:
            self.log_test("Check Browse Badge Update", True, "✅ BADGE CORRECTLY UPDATED - Now shows Private badge")
            return True
        else:
            self.log_test("Check Browse Badge Update", False, "❌ BADGE NOT UPDATED - Still shows Business badge (THIS IS THE BUG)")
            return False

    def test_8_multiple_browse_calls(self):
        """Step 8: Test multiple browse calls to check for caching issues"""
        print("\n🔄 Step 8: Testing Multiple Browse Calls for Caching Issues...")
        
        if not self.test_listing_id:
            self.log_test("Multiple Browse Calls", False, "No test listing available")
            return False
        
        results = []
        for i in range(3):
            print(f"   📞 Browse call #{i+1}...")
            success, browse_response, status = self.run_api_call(
                'GET', 'api/marketplace/browse'
            )
            
            if success:
                # Find our test listing
                test_listing = None
                for listing in browse_response:
                    if listing.get('id') == self.test_listing_id:
                        test_listing = listing
                        break
                
                if test_listing:
                    seller = test_listing.get('seller', {})
                    is_business = seller.get('is_business', True)
                    results.append(is_business)
                    print(f"      Result: is_business = {is_business}")
                else:
                    results.append(None)
                    print(f"      Result: Listing not found")
            else:
                results.append(None)
                print(f"      Result: API call failed")
            
            # Small delay between calls
            time.sleep(1)
        
        # Check consistency
        valid_results = [r for r in results if r is not None]
        if valid_results:
            all_same = all(r == valid_results[0] for r in valid_results)
            all_private = all(r == False for r in valid_results)  # False means private
            
            print(f"   📊 Results: {results}")
            print(f"   📊 All consistent: {all_same}")
            print(f"   📊 All showing private: {all_private}")
            
            if all_same and all_private:
                self.log_test("Multiple Browse Calls", True, "All calls consistently show private badge")
                return True
            elif all_same and not all_private:
                self.log_test("Multiple Browse Calls", False, "All calls consistently show business badge (caching issue)")
                return False
            else:
                self.log_test("Multiple Browse Calls", False, "Inconsistent results across calls")
                return False
        else:
            self.log_test("Multiple Browse Calls", False, "No valid results obtained")
            return False

    def test_9_seller_enrichment_debug(self):
        """Step 9: Debug seller enrichment process"""
        print("\n🔧 Step 9: Debugging Seller Enrichment Process...")
        
        if not self.business_user:
            self.log_test("Seller Enrichment Debug", False, "No user available")
            return False
        
        # Get fresh profile data
        success, profile_response, status = self.run_api_call(
            'GET', f'api/auth/profile/{self.business_user["id"]}'
        )
        
        if not success:
            self.log_test("Seller Enrichment Debug", False, "Could not fetch profile for debug")
            return False
        
        print(f"   🔍 Fresh Profile Data:")
        print(f"      User ID: {self.business_user['id']}")
        print(f"      Email: {profile_response.get('email', 'N/A')}")
        print(f"      Username: {profile_response.get('username', 'N/A')}")
        print(f"      is_business: {profile_response.get('is_business', 'N/A')}")
        print(f"      business_name: {profile_response.get('business_name', 'N/A')}")
        
        # Get browse data
        success, browse_response, status = self.run_api_call(
            'GET', 'api/marketplace/browse'
        )
        
        if success and self.test_listing_id:
            test_listing = None
            for listing in browse_response:
                if listing.get('id') == self.test_listing_id:
                    test_listing = listing
                    break
            
            if test_listing:
                seller = test_listing.get('seller', {})
                print(f"   🔍 Browse Seller Data:")
                print(f"      seller.name: {seller.get('name', 'N/A')}")
                print(f"      seller.username: {seller.get('username', 'N/A')}")
                print(f"      seller.email: {seller.get('email', 'N/A')}")
                print(f"      seller.is_business: {seller.get('is_business', 'N/A')}")
                print(f"      seller.business_name: {seller.get('business_name', 'N/A')}")
                
                # Compare profile vs browse data
                profile_is_business = profile_response.get('is_business', None)
                browse_is_business = seller.get('is_business', None)
                
                if profile_is_business == browse_is_business:
                    self.log_test("Seller Enrichment Debug", True, f"Profile and browse data match: is_business={profile_is_business}")
                    return True
                else:
                    self.log_test("Seller Enrichment Debug", False, f"MISMATCH - Profile: {profile_is_business}, Browse: {browse_is_business}")
                    return False
            else:
                self.log_test("Seller Enrichment Debug", False, "Test listing not found in browse")
                return False
        else:
            self.log_test("Seller Enrichment Debug", False, "Could not fetch browse data")
            return False

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test listing
        if self.test_listing_id:
            success, _, _ = self.run_api_call(
                'DELETE', f'api/listings/{self.test_listing_id}'
            )
            if success:
                print(f"   ✅ Deleted test listing: {self.test_listing_id}")
            else:
                print(f"   ⚠️  Could not delete test listing: {self.test_listing_id}")
        
        # Reset user to original state (admin, not business)
        if self.business_user:
            reset_data = {
                "is_business": False,
                "business_name": "",
                "company_name": ""
            }
            success, _, _ = self.run_api_call(
                'PUT', f'api/admin/users/{self.business_user["id"]}',
                reset_data
            )
            if success:
                print(f"   ✅ Reset user to original state")
            else:
                print(f"   ⚠️  Could not reset user state")

    def run_badge_switching_test(self):
        """Run the complete badge switching test"""
        print("🔍 BADGE SWITCHING ISSUE DEBUG TEST")
        print("=" * 60)
        print("Testing: User changes profile from Business to Private,")
        print("but browse listings still show old 'Business' badges")
        print("=" * 60)
        
        # Run all test steps
        test_results = []
        
        test_results.append(self.test_1_create_business_user())
        test_results.append(self.test_2_verify_business_profile())
        test_results.append(self.test_3_create_business_listing())
        test_results.append(self.test_4_verify_business_badge_in_browse())
        test_results.append(self.test_5_change_to_private_account())
        test_results.append(self.test_6_verify_private_profile())
        test_results.append(self.test_7_check_browse_badge_update())  # CRITICAL TEST
        test_results.append(self.test_8_multiple_browse_calls())
        test_results.append(self.test_9_seller_enrichment_debug())
        
        # Clean up
        self.cleanup_test_data()
        
        # Results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print("\n" + "=" * 60)
        print("🎯 BADGE SWITCHING TEST RESULTS")
        print("=" * 60)
        print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
        print(f"📊 Overall Tests: {self.tests_passed}/{self.tests_run}")
        
        # Critical analysis
        if test_results[6]:  # test_7_check_browse_badge_update
            print("✅ CRITICAL: Badge switching works correctly!")
            print("   The browse endpoint correctly updates badges when user profile changes.")
        else:
            print("❌ CRITICAL: Badge switching issue confirmed!")
            print("   The browse endpoint does NOT update badges when user profile changes.")
            print("   This is the bug described in the review request.")
        
        # Detailed analysis
        print("\n🔍 DETAILED ANALYSIS:")
        
        if test_results[4] and test_results[5]:  # Profile change successful
            print("✅ Profile Update: User profile successfully changed from Business to Private")
        else:
            print("❌ Profile Update: Failed to change user profile")
        
        if test_results[6]:  # Browse badge update
            print("✅ Browse Update: Browse endpoint reflects profile changes immediately")
        else:
            print("❌ Browse Update: Browse endpoint shows stale badge data")
        
        if test_results[7]:  # Multiple calls consistency
            print("✅ Consistency: Multiple browse calls return consistent results")
        else:
            print("❌ Consistency: Browse calls return inconsistent results (possible caching)")
        
        if test_results[8]:  # Seller enrichment debug
            print("✅ Data Flow: Profile data matches browse seller data")
        else:
            print("❌ Data Flow: Mismatch between profile data and browse seller data")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = BadgeSwitchingTester()
    success = tester.run_badge_switching_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())