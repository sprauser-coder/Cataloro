#!/usr/bin/env python3
"""
Comprehensive Badge Switching Test
Tests the badge switching issue with existing users and listings
"""

import requests
import sys
import json
from datetime import datetime
import time

class ComprehensiveBadgeTest:
    def __init__(self, base_url="https://market-refactor.preview.emergentagent.com"):
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

    def test_existing_business_user_scenario(self):
        """Test the scenario with existing business user cataloro_business"""
        print("\n🏢 Testing Existing Business User Scenario...")
        
        business_user_id = "68b43ce770fbecdd047c4802"  # cataloro_business
        
        # Step 1: Verify current business profile
        print("\n1️⃣ Checking current business profile...")
        success, profile, _ = self.run_api_call('GET', f'api/auth/profile/{business_user_id}')
        
        if not success:
            self.log_test("Get Business Profile", False, "Could not fetch business user profile")
            return False
        
        print(f"   📊 Current Profile:")
        print(f"      Email: {profile.get('email', 'N/A')}")
        print(f"      Username: {profile.get('username', 'N/A')}")
        print(f"      is_business: {profile.get('is_business', 'N/A')}")
        print(f"      business_name: {profile.get('business_name', 'N/A')}")
        
        original_is_business = profile.get('is_business', False)
        
        # Step 2: Check current browse listings for this user
        print("\n2️⃣ Checking current browse listings...")
        success, browse_listings, _ = self.run_api_call('GET', 'api/marketplace/browse')
        
        if not success:
            self.log_test("Get Browse Listings", False, "Could not fetch browse listings")
            return False
        
        business_listings = []
        for listing in browse_listings:
            if listing.get('seller_id') == business_user_id:
                business_listings.append(listing)
        
        print(f"   📊 Found {len(business_listings)} listings from business user")
        
        for i, listing in enumerate(business_listings):
            seller = listing.get('seller', {})
            print(f"   Listing {i+1}: {listing.get('title', 'No title')[:50]}...")
            print(f"      seller.is_business: {seller.get('is_business', 'N/A')}")
            print(f"      seller.business_name: {seller.get('business_name', 'N/A')}")
        
        if not business_listings:
            print("   ⚠️  No listings found for business user - creating one...")
            
            # Create a test listing
            test_listing = {
                "title": "Comprehensive Badge Test - Business Equipment",
                "description": "Professional equipment from business user for badge testing.",
                "price": 899.99,
                "category": "Business Equipment",
                "condition": "Used - Excellent",
                "seller_id": business_user_id,
                "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"],
                "tags": ["business", "professional", "equipment"]
            }
            
            success, create_response, _ = self.run_api_call('POST', 'api/listings', test_listing)
            
            if success:
                listing_id = create_response.get('listing_id')
                print(f"   ✅ Created test listing: {listing_id}")
                
                # Refresh browse listings
                success, browse_listings, _ = self.run_api_call('GET', 'api/marketplace/browse')
                if success:
                    for listing in browse_listings:
                        if listing.get('id') == listing_id:
                            business_listings.append(listing)
                            break
            else:
                print("   ❌ Failed to create test listing")
        
        # Step 3: Change business user to private
        print("\n3️⃣ Changing business user to private...")
        
        private_update = {
            "is_business": False,
            "business_name": "",
            "company_name": ""
        }
        
        success, update_response, status = self.run_api_call(
            'PUT', f'api/admin/users/{business_user_id}', private_update
        )
        
        if not success:
            self.log_test("Update to Private", False, f"Failed to update user (Status: {status})")
            return False
        
        print("   ✅ Updated user to private account")
        
        # Step 4: Verify profile change
        print("\n4️⃣ Verifying profile change...")
        success, updated_profile, _ = self.run_api_call('GET', f'api/auth/profile/{business_user_id}')
        
        if success:
            new_is_business = updated_profile.get('is_business', True)
            print(f"   📊 Updated Profile:")
            print(f"      is_business: {new_is_business}")
            print(f"      business_name: {updated_profile.get('business_name', 'N/A')}")
            
            if not new_is_business:
                self.log_test("Profile Update Verification", True, "Profile successfully changed to private")
            else:
                self.log_test("Profile Update Verification", False, "Profile still shows as business")
                return False
        else:
            self.log_test("Profile Update Verification", False, "Could not verify profile update")
            return False
        
        # Step 5: Check browse listings immediately after change
        print("\n5️⃣ Checking browse listings after profile change...")
        
        success, updated_browse, _ = self.run_api_call('GET', 'api/marketplace/browse')
        
        if not success:
            self.log_test("Browse After Update", False, "Could not fetch updated browse listings")
            return False
        
        # Find listings from this user
        updated_business_listings = []
        for listing in updated_browse:
            if listing.get('seller_id') == business_user_id:
                updated_business_listings.append(listing)
        
        print(f"   📊 Found {len(updated_business_listings)} listings after update")
        
        badge_update_success = True
        for i, listing in enumerate(updated_business_listings):
            seller = listing.get('seller', {})
            is_business = seller.get('is_business', True)
            business_name = seller.get('business_name', '')
            
            print(f"   Listing {i+1}: {listing.get('title', 'No title')[:50]}...")
            print(f"      seller.is_business: {is_business}")
            print(f"      seller.business_name: {business_name}")
            
            if is_business:
                print(f"      ❌ ISSUE: Still showing business badge!")
                badge_update_success = False
            else:
                print(f"      ✅ Correctly showing private badge")
        
        if badge_update_success:
            self.log_test("Badge Update After Profile Change", True, "All listings now show private badges")
        else:
            self.log_test("Badge Update After Profile Change", False, "Some listings still show business badges")
        
        # Step 6: Test multiple calls for consistency
        print("\n6️⃣ Testing multiple browse calls for consistency...")
        
        consistency_results = []
        for i in range(3):
            success, browse_data, _ = self.run_api_call('GET', 'api/marketplace/browse')
            if success:
                user_listings = [l for l in browse_data if l.get('seller_id') == business_user_id]
                if user_listings:
                    # Check if any listing still shows business badge
                    any_business = any(l.get('seller', {}).get('is_business', False) for l in user_listings)
                    consistency_results.append(any_business)
                    print(f"   Call {i+1}: Any business badges = {any_business}")
                else:
                    consistency_results.append(None)
                    print(f"   Call {i+1}: No listings found")
            else:
                consistency_results.append(None)
                print(f"   Call {i+1}: API call failed")
            
            time.sleep(1)
        
        valid_results = [r for r in consistency_results if r is not None]
        if valid_results:
            all_consistent = all(r == valid_results[0] for r in valid_results)
            all_private = all(r == False for r in valid_results)  # False means no business badges
            
            if all_consistent and all_private:
                self.log_test("Consistency Check", True, "All calls consistently show private badges")
            else:
                self.log_test("Consistency Check", False, f"Inconsistent results: {consistency_results}")
        else:
            self.log_test("Consistency Check", False, "No valid results")
        
        # Step 7: Restore original state
        print("\n7️⃣ Restoring original user state...")
        
        restore_update = {
            "is_business": original_is_business,
            "business_name": "Cataloro Business Solutions" if original_is_business else "",
            "company_name": "Cataloro Business Solutions" if original_is_business else ""
        }
        
        success, _, _ = self.run_api_call('PUT', f'api/admin/users/{business_user_id}', restore_update)
        
        if success:
            print("   ✅ Restored original user state")
        else:
            print("   ⚠️  Could not restore original user state")
        
        return badge_update_success

    def test_admin_user_scenario(self):
        """Test the scenario with admin user (sash_admin)"""
        print("\n👤 Testing Admin User Scenario...")
        
        admin_user_id = "68b191ec38e6062fee10bd27"  # sash_admin
        
        # Step 1: Get current admin profile
        success, profile, _ = self.run_api_call('GET', f'api/auth/profile/{admin_user_id}')
        
        if not success:
            self.log_test("Get Admin Profile", False, "Could not fetch admin profile")
            return False
        
        original_is_business = profile.get('is_business', False)
        print(f"   📊 Admin current is_business: {original_is_business}")
        
        # Step 2: Change admin to business if not already
        if not original_is_business:
            print("   🔄 Converting admin to business account...")
            
            business_update = {
                "is_business": True,
                "business_name": "Admin Business Solutions",
                "company_name": "Admin Business Solutions"
            }
            
            success, _, _ = self.run_api_call('PUT', f'api/admin/users/{admin_user_id}', business_update)
            
            if not success:
                self.log_test("Convert Admin to Business", False, "Could not convert admin to business")
                return False
            
            print("   ✅ Converted admin to business")
        
        # Step 3: Check browse listings
        success, browse_listings, _ = self.run_api_call('GET', 'api/marketplace/browse')
        
        if not success:
            self.log_test("Get Browse for Admin Test", False, "Could not fetch browse listings")
            return False
        
        admin_listings = [l for l in browse_listings if l.get('seller_id') == admin_user_id]
        print(f"   📊 Found {len(admin_listings)} admin listings")
        
        # Step 4: Change back to private
        print("   🔄 Converting admin back to private...")
        
        private_update = {
            "is_business": False,
            "business_name": "",
            "company_name": ""
        }
        
        success, _, _ = self.run_api_call('PUT', f'api/admin/users/{admin_user_id}', private_update)
        
        if not success:
            self.log_test("Convert Admin to Private", False, "Could not convert admin to private")
            return False
        
        # Step 5: Check if badges updated
        success, updated_browse, _ = self.run_api_call('GET', 'api/marketplace/browse')
        
        if success:
            updated_admin_listings = [l for l in updated_browse if l.get('seller_id') == admin_user_id]
            
            badge_correct = True
            for listing in updated_admin_listings:
                seller = listing.get('seller', {})
                if seller.get('is_business', False):
                    badge_correct = False
                    break
            
            if badge_correct:
                self.log_test("Admin Badge Update", True, "Admin listings correctly show private badges")
            else:
                self.log_test("Admin Badge Update", False, "Admin listings still show business badges")
            
            return badge_correct
        else:
            self.log_test("Admin Badge Update", False, "Could not verify admin badge update")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive badge switching tests"""
        print("🔍 COMPREHENSIVE BADGE SWITCHING TEST")
        print("=" * 60)
        print("Testing badge switching with existing users and various scenarios")
        print("=" * 60)
        
        # Test scenarios
        results = []
        
        # Scenario 1: Existing business user
        results.append(self.test_existing_business_user_scenario())
        
        # Scenario 2: Admin user
        results.append(self.test_admin_user_scenario())
        
        # Results
        passed_scenarios = sum(results)
        total_scenarios = len(results)
        
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        print(f"📊 Scenarios Passed: {passed_scenarios}/{total_scenarios}")
        print(f"📊 Individual Tests: {self.tests_passed}/{self.tests_run}")
        
        if passed_scenarios == total_scenarios:
            print("✅ ALL SCENARIOS PASSED: Badge switching works correctly!")
        else:
            print("❌ SOME SCENARIOS FAILED: Badge switching has issues!")
        
        return passed_scenarios == total_scenarios

def main():
    """Main test execution"""
    tester = ComprehensiveBadgeTest()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())