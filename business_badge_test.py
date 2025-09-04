#!/usr/bin/env python3
"""
Business Badge Functionality Test
Comprehensive test to verify business badge display and seller information
"""

import requests
import json
import sys

class BusinessBadgeTest:
    def __init__(self, base_url="https://cataloro-admin-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.business_user_id = "68b43ce770fbecdd047c4802"  # Known business user
        self.admin_user_id = "68b191ec38e6062fee10bd27"     # Known admin user
        self.test_listings = []

    def log_result(self, test_name, success, details=""):
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        return success

    def make_request(self, method, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            print(f"   {method} {endpoint} -> {response.status_code}")
            
            if response.status_code in [200, 201]:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                return False, response.text
                
        except Exception as e:
            print(f"   Exception: {str(e)}")
            return False, {}

    def test_current_browse_structure(self):
        """Test current browse listings structure"""
        print("\n🔍 TEST 1: Current Browse Listings Structure")
        
        success, browse_data = self.make_request('GET', 'api/marketplace/browse')
        
        if not success:
            return self.log_result("Current Browse Structure", False, "API call failed")
        
        print(f"\n📊 Current Browse Response Analysis:")
        print(f"   Total listings: {len(browse_data)}")
        print(f"   Response type: {type(browse_data)}")
        
        # Analyze each listing
        business_listings = 0
        private_listings = 0
        
        for i, listing in enumerate(browse_data):
            print(f"\n   Listing {i+1}: {listing.get('title', 'No title')}")
            print(f"      ID: {listing.get('id')}")
            print(f"      Seller ID: {listing.get('seller_id')}")
            
            # Check seller object in listing
            if 'seller' in listing:
                seller_obj = listing['seller']
                print(f"      Seller Object: {seller_obj}")
                
                # Check if seller name is email or username
                seller_name = seller_obj.get('name', '')
                if '@' in seller_name:
                    print(f"      ⚠️  Seller showing EMAIL: {seller_name}")
                else:
                    print(f"      ✅ Seller showing USERNAME: {seller_name}")
            
            # Get full seller profile
            seller_id = listing.get('seller_id')
            if seller_id:
                profile_success, profile = self.make_request('GET', f'api/auth/profile/{seller_id}')
                if profile_success:
                    is_business = profile.get('is_business', False)
                    username = profile.get('username', '')
                    business_name = profile.get('business_name', '')
                    
                    print(f"      Profile - Username: {username}")
                    print(f"      Profile - Is Business: {is_business}")
                    print(f"      Profile - Business Name: {business_name}")
                    
                    if is_business:
                        business_listings += 1
                        print(f"      🏢 BUSINESS ACCOUNT - Should show 'Business' badge")
                    else:
                        private_listings += 1
                        print(f"      👤 PRIVATE ACCOUNT - Should show 'Private' badge")
        
        print(f"\n📋 Summary:")
        print(f"   Business listings: {business_listings}")
        print(f"   Private listings: {private_listings}")
        
        return self.log_result("Current Browse Structure", True, 
                             f"Analyzed {len(browse_data)} listings - {business_listings} business, {private_listings} private")

    def test_create_business_listing(self):
        """Create a listing from the known business user"""
        print("\n🏢 TEST 2: Create Business User Listing")
        
        # First verify the business user profile
        success, business_profile = self.make_request('GET', f'api/auth/profile/{self.business_user_id}')
        
        if not success:
            return self.log_result("Create Business Listing", False, "Could not get business user profile")
        
        print(f"\n👤 Business User Profile:")
        print(f"   ID: {business_profile.get('id')}")
        print(f"   Username: {business_profile.get('username')}")
        print(f"   Email: {business_profile.get('email')}")
        print(f"   Is Business: {business_profile.get('is_business')}")
        print(f"   Business Name: {business_profile.get('business_name')}")
        
        if not business_profile.get('is_business'):
            return self.log_result("Create Business Listing", False, "User is not marked as business account")
        
        # Create business listing
        business_listing = {
            "title": "Business Test - Professional Camera Equipment",
            "description": "Professional camera equipment from Cataloro Business Solutions. Enterprise grade with full warranty and support.",
            "price": 2499.99,
            "category": "Photography",
            "condition": "New",
            "seller_id": self.business_user_id,
            "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"],
            "tags": ["business", "professional", "camera"],
            "features": ["Enterprise warranty", "Professional support", "Business grade"]
        }
        
        success, create_response = self.make_request('POST', 'api/listings', business_listing)
        
        if success:
            listing_id = create_response.get('listing_id')
            self.test_listings.append(listing_id)
            
            return self.log_result("Create Business Listing", True, 
                                 f"Created business listing: {listing_id}")
        else:
            return self.log_result("Create Business Listing", False, "Failed to create listing")

    def test_create_private_listing(self):
        """Create a listing from a private user for comparison"""
        print("\n👤 TEST 3: Create Private User Listing")
        
        # Create private listing from admin user (who is not business)
        private_listing = {
            "title": "Private Test - Personal Laptop",
            "description": "Personal laptop for sale. Well maintained, selling due to upgrade.",
            "price": 899.99,
            "category": "Electronics",
            "condition": "Used - Excellent",
            "seller_id": self.admin_user_id,
            "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400"],
            "tags": ["personal", "laptop", "private"],
            "features": ["Personal use", "Well maintained", "Quick sale"]
        }
        
        success, create_response = self.make_request('POST', 'api/listings', private_listing)
        
        if success:
            listing_id = create_response.get('listing_id')
            self.test_listings.append(listing_id)
            
            return self.log_result("Create Private Listing", True, 
                                 f"Created private listing: {listing_id}")
        else:
            return self.log_result("Create Private Listing", False, "Failed to create listing")

    def test_browse_with_mixed_listings(self):
        """Test browse response with both business and private listings"""
        print("\n🔄 TEST 4: Browse Response with Mixed Account Types")
        
        success, browse_data = self.make_request('GET', 'api/marketplace/browse')
        
        if not success:
            return self.log_result("Mixed Listings Browse", False, "Could not get browse data")
        
        print(f"\n📊 Browse Response with Test Listings:")
        print(f"   Total listings: {len(browse_data)}")
        
        business_count = 0
        private_count = 0
        email_display_count = 0
        username_display_count = 0
        
        for i, listing in enumerate(browse_data):
            print(f"\n   Listing {i+1}: {listing.get('title', 'No title')[:50]}...")
            
            seller_id = listing.get('seller_id')
            if seller_id:
                # Get seller profile
                profile_success, profile = self.make_request('GET', f'api/auth/profile/{seller_id}')
                
                if profile_success:
                    is_business = profile.get('is_business', False)
                    username = profile.get('username', '')
                    email = profile.get('email', '')
                    business_name = profile.get('business_name', '')
                    
                    # Check seller object in listing
                    seller_obj = listing.get('seller', {})
                    seller_display_name = seller_obj.get('name', '')
                    
                    print(f"      Seller ID: {seller_id}")
                    print(f"      Profile Username: {username}")
                    print(f"      Profile Email: {email}")
                    print(f"      Is Business: {is_business}")
                    print(f"      Business Name: {business_name}")
                    print(f"      Seller Display Name: {seller_display_name}")
                    
                    # Count account types
                    if is_business:
                        business_count += 1
                        print(f"      🏢 BUSINESS ACCOUNT -> Should show 'Business' badge")
                    else:
                        private_count += 1
                        print(f"      👤 PRIVATE ACCOUNT -> Should show 'Private' badge")
                    
                    # Check display name type
                    if '@' in seller_display_name:
                        email_display_count += 1
                        print(f"      ⚠️  SHOWING EMAIL in seller name")
                    else:
                        username_display_count += 1
                        print(f"      ✅ SHOWING USERNAME in seller name")
        
        print(f"\n📋 Analysis Results:")
        print(f"   Business accounts: {business_count}")
        print(f"   Private accounts: {private_count}")
        print(f"   Showing emails: {email_display_count}")
        print(f"   Showing usernames: {username_display_count}")
        
        # Identify issues
        issues = []
        if business_count == 0:
            issues.append("No business accounts found - all will show 'Private' badges")
        if email_display_count > 0:
            issues.append(f"{email_display_count} listings showing emails instead of usernames")
        
        if issues:
            print(f"\n⚠️  Issues Found:")
            for issue in issues:
                print(f"   - {issue}")
        
        return self.log_result("Mixed Listings Browse", len(issues) == 0, 
                             f"Found {len(issues)} issues in browse response")

    def test_seller_object_structure(self):
        """Test the seller object structure in listings"""
        print("\n🔍 TEST 5: Seller Object Structure Analysis")
        
        success, browse_data = self.make_request('GET', 'api/marketplace/browse')
        
        if not success:
            return self.log_result("Seller Object Structure", False, "Could not get browse data")
        
        print(f"\n📊 Seller Object Analysis:")
        
        for i, listing in enumerate(browse_data):
            if 'seller' in listing:
                seller_obj = listing['seller']
                seller_id = listing.get('seller_id')
                
                print(f"\n   Listing {i+1}: {listing.get('title', 'No title')[:30]}...")
                print(f"      Seller Object Keys: {list(seller_obj.keys())}")
                print(f"      Seller Object: {seller_obj}")
                
                # Get actual profile
                if seller_id:
                    profile_success, profile = self.make_request('GET', f'api/auth/profile/{seller_id}')
                    if profile_success:
                        print(f"      Profile Username: {profile.get('username')}")
                        print(f"      Profile Email: {profile.get('email')}")
                        print(f"      Profile Is Business: {profile.get('is_business')}")
                        
                        # Compare seller object with profile
                        seller_name = seller_obj.get('name', '')
                        profile_username = profile.get('username', '')
                        profile_email = profile.get('email', '')
                        
                        if seller_name == profile_email:
                            print(f"      ⚠️  Seller object using EMAIL instead of USERNAME")
                        elif seller_name == profile_username:
                            print(f"      ✅ Seller object using USERNAME correctly")
                        else:
                            print(f"      ❓ Seller object using unknown value: {seller_name}")
        
        return self.log_result("Seller Object Structure", True, "Seller object analysis complete")

    def test_data_transformation_recommendations(self):
        """Provide recommendations for fixing the issues"""
        print("\n💡 TEST 6: Data Transformation Recommendations")
        
        print(f"\n🔧 Recommendations to Fix Business Badge Issues:")
        
        print(f"\n1️⃣ Backend API Response Enhancement:")
        print(f"   - The /api/marketplace/browse endpoint should include seller profile data")
        print(f"   - Add 'is_business' field to the seller object in each listing")
        print(f"   - Add 'business_name' field for business accounts")
        print(f"   - Use 'username' instead of 'email' in seller.name field")
        
        print(f"\n2️⃣ Frontend Data Processing:")
        print(f"   - Check if seller.is_business exists in listing data")
        print(f"   - If not, fetch seller profile for each listing (current approach)")
        print(f"   - Use seller.username or seller.business_name for display")
        print(f"   - Show 'Business' badge when is_business = true")
        
        print(f"\n3️⃣ Backend Modification Needed:")
        print(f"   - Modify /api/marketplace/browse to join seller profile data")
        print(f"   - Include seller.is_business, seller.username, seller.business_name")
        print(f"   - This will eliminate need for multiple API calls on frontend")
        
        return self.log_result("Data Transformation Recommendations", True, "Recommendations provided")

    def cleanup_test_listings(self):
        """Clean up test listings"""
        print(f"\n🧹 Cleaning up {len(self.test_listings)} test listings...")
        
        for listing_id in self.test_listings:
            success, _ = self.make_request('DELETE', f'api/listings/{listing_id}')
            if success:
                print(f"   ✅ Deleted: {listing_id[:8]}...")
            else:
                print(f"   ❌ Failed to delete: {listing_id[:8]}...")

    def run_all_tests(self):
        """Run all business badge tests"""
        print("🏢 BUSINESS BADGE FUNCTIONALITY DEBUG TESTS")
        print("=" * 60)
        
        test_results = []
        
        # Run tests
        test_results.append(self.test_current_browse_structure())
        test_results.append(self.test_create_business_listing())
        test_results.append(self.test_create_private_listing())
        test_results.append(self.test_browse_with_mixed_listings())
        test_results.append(self.test_seller_object_structure())
        test_results.append(self.test_data_transformation_recommendations())
        
        # Cleanup
        self.cleanup_test_listings()
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print("\n" + "=" * 60)
        print(f"🏢 BUSINESS BADGE TEST RESULTS: {passed_tests}/{total_tests} tests passed")
        
        return passed_tests == total_tests

def main():
    tester = BusinessBadgeTest()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())