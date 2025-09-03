#!/usr/bin/env python3
"""
Seller Status Fix Test Suite
Tests the business badge functionality and seller enrichment logic
"""

import requests
import sys
import json
from datetime import datetime

class SellerStatusTester:
    def __init__(self, base_url="https://tender-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.admin_user = None
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
                    details += f", Response: {json.dumps(response_data, indent=2)[:300]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login to get admin user info"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_user = response['user']
            print(f"   Admin User ID: {self.admin_user.get('id', 'N/A')}")
            print(f"   Admin Username: {self.admin_user.get('username', 'N/A')}")
            print(f"   Admin Email: {self.admin_user.get('email', 'N/A')}")
        return success

    def test_admin_user_profile(self):
        """Test admin user profile to verify business status"""
        if not self.admin_user:
            print("❌ Admin Profile Test - SKIPPED (No admin logged in)")
            return False
            
        admin_id = self.admin_user.get('id')
        if not admin_id:
            print("❌ Admin Profile Test - SKIPPED (No admin ID)")
            return False
            
        success, response = self.run_test(
            "Admin User Profile",
            "GET",
            f"api/auth/profile/{admin_id}",
            200
        )
        
        if success:
            print(f"\n📋 Admin Profile Details:")
            print(f"   ID: {response.get('id', 'N/A')}")
            print(f"   Username: {response.get('username', 'N/A')}")
            print(f"   Email: {response.get('email', 'N/A')}")
            print(f"   Full Name: {response.get('full_name', 'N/A')}")
            print(f"   Is Business: {response.get('is_business', 'N/A')}")
            print(f"   Business Name: {response.get('business_name', 'N/A')}")
            print(f"   Company Name: {response.get('company_name', 'N/A')}")
            
            # Check if admin has business status
            is_business = response.get('is_business', False)
            business_name = response.get('business_name', '') or response.get('company_name', '')
            
            self.log_test("Admin Business Status", is_business, 
                         f"is_business: {is_business}, business_name: '{business_name}'")
            
            # Check if this is the specific admin mentioned in the review
            expected_admin_id = "68b191ec38e6062fee10bd27"
            if admin_id == expected_admin_id:
                self.log_test("Correct Admin User ID", True, f"Admin ID matches expected: {expected_admin_id}")
            else:
                print(f"   ⚠️  Admin ID {admin_id} doesn't match expected {expected_admin_id}")
                self.log_test("Correct Admin User ID", False, f"Expected: {expected_admin_id}, Got: {admin_id}")
            
            return is_business and business_name
        
        return False

    def test_browse_listings_seller_info(self):
        """Test browse listings API for correct seller information"""
        success, response = self.run_test(
            "Browse Listings Seller Information",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            print(f"\n📊 Browse Listings Analysis:")
            print(f"   Total listings found: {len(response)}")
            
            admin_listings = []
            business_listings = []
            private_listings = []
            
            for listing in response:
                seller = listing.get('seller', {})
                seller_name = seller.get('name', 'Unknown')
                seller_username = seller.get('username', 'Unknown')
                is_business = seller.get('is_business', False)
                business_name = seller.get('business_name', '')
                
                print(f"\n   📝 Listing: {listing.get('title', 'No Title')[:50]}...")
                print(f"      Seller Name: {seller_name}")
                print(f"      Seller Username: {seller_username}")
                print(f"      Is Business: {is_business}")
                print(f"      Business Name: {business_name}")
                print(f"      Seller ID: {listing.get('seller_id', 'N/A')}")
                
                # Check if this is an admin listing
                if (seller_username == 'sash_admin' or 
                    seller_name == 'sash_admin' or 
                    'admin' in seller_name.lower() or
                    listing.get('seller_id') == self.admin_user.get('id') if self.admin_user else False):
                    admin_listings.append(listing)
                
                if is_business:
                    business_listings.append(listing)
                else:
                    private_listings.append(listing)
            
            print(f"\n📈 Seller Analysis Summary:")
            print(f"   Admin listings: {len(admin_listings)}")
            print(f"   Business listings: {len(business_listings)}")
            print(f"   Private listings: {len(private_listings)}")
            
            # Test 1: Check if admin listings show business status
            admin_business_correct = True
            for listing in admin_listings:
                seller = listing.get('seller', {})
                if not seller.get('is_business', False):
                    admin_business_correct = False
                    print(f"   ❌ Admin listing '{listing.get('title', 'Unknown')}' shows is_business: False")
                else:
                    print(f"   ✅ Admin listing '{listing.get('title', 'Unknown')}' shows is_business: True")
            
            self.log_test("Admin Listings Business Status", admin_business_correct,
                         f"{len(admin_listings)} admin listings, all show business status: {admin_business_correct}")
            
            # Test 2: Check seller enrichment completeness
            enrichment_complete = True
            missing_fields = []
            
            for listing in response[:5]:  # Check first 5 listings
                seller = listing.get('seller', {})
                required_fields = ['name', 'username', 'email', 'is_business', 'business_name', 'verified', 'location']
                
                for field in required_fields:
                    if field not in seller:
                        enrichment_complete = False
                        missing_fields.append(f"{listing.get('title', 'Unknown')[:20]}... missing {field}")
            
            self.log_test("Seller Enrichment Completeness", enrichment_complete,
                         f"All required seller fields present: {enrichment_complete}")
            
            if missing_fields:
                print(f"   Missing fields: {missing_fields[:3]}")  # Show first 3 missing fields
            
            # Test 3: Verify business name is set for business accounts
            business_names_set = True
            for listing in business_listings:
                seller = listing.get('seller', {})
                business_name = seller.get('business_name', '')
                if not business_name:
                    business_names_set = False
                    print(f"   ❌ Business listing '{listing.get('title', 'Unknown')}' has empty business_name")
            
            self.log_test("Business Names Set", business_names_set,
                         f"{len(business_listings)} business listings, all have business names: {business_names_set}")
            
            return admin_business_correct and enrichment_complete
        
        return False

    def test_create_admin_listing(self):
        """Create a test listing as admin to verify business badge"""
        if not self.admin_user:
            print("❌ Create Admin Listing - SKIPPED (No admin logged in)")
            return False
            
        admin_listing = {
            "title": "Admin Test Listing - Business Badge Verification",
            "description": "This listing is created by admin (sash_admin) to test business badge functionality. Should show 'Business' badge, not 'Private'.",
            "price": 199.99,
            "category": "Test Category",
            "condition": "New",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"],
            "tags": ["admin", "test", "business-badge"],
            "features": ["Business verification test", "Admin created", "Badge testing"]
        }
        
        success, response = self.run_test(
            "Create Admin Test Listing",
            "POST",
            "api/listings",
            200,
            data=admin_listing
        )
        
        if success:
            listing_id = response.get('listing_id')
            print(f"   ✅ Created admin test listing with ID: {listing_id}")
            
            # Verify the listing appears in browse with correct seller info
            browse_success, browse_response = self.run_test(
                "Verify Admin Listing in Browse",
                "GET",
                "api/marketplace/browse",
                200
            )
            
            if browse_success:
                # Find our test listing
                test_listing = None
                for listing in browse_response:
                    if listing.get('id') == listing_id:
                        test_listing = listing
                        break
                
                if test_listing:
                    seller = test_listing.get('seller', {})
                    is_business = seller.get('is_business', False)
                    business_name = seller.get('business_name', '')
                    seller_username = seller.get('username', '')
                    
                    print(f"\n📋 Admin Test Listing Verification:")
                    print(f"   Listing ID: {listing_id}")
                    print(f"   Seller Username: {seller_username}")
                    print(f"   Is Business: {is_business}")
                    print(f"   Business Name: {business_name}")
                    
                    # This should show business badge
                    business_badge_correct = is_business and business_name
                    self.log_test("Admin Listing Business Badge", business_badge_correct,
                                 f"Admin listing shows business badge: {business_badge_correct}")
                    
                    # Cleanup: Delete test listing
                    self.run_test(
                        "Cleanup Admin Test Listing",
                        "DELETE",
                        f"api/listings/{listing_id}",
                        200
                    )
                    
                    return business_badge_correct
                else:
                    self.log_test("Admin Listing Business Badge", False, "Test listing not found in browse")
            
        return False

    def test_seller_enrichment_logic(self):
        """Test the seller enrichment logic comprehensively"""
        print("\n🔍 Testing Seller Enrichment Logic...")
        
        # Get all users to understand the data structure
        if not self.admin_user:
            print("❌ Seller Enrichment Test - SKIPPED (No admin logged in)")
            return False
            
        # Test admin users endpoint to see user data structure
        success, users_response = self.run_test(
            "Get All Users for Enrichment Analysis",
            "GET",
            "api/admin/users",
            200
        )
        
        if success:
            print(f"\n👥 User Database Analysis:")
            print(f"   Total users: {len(users_response)}")
            
            admin_users = []
            business_users = []
            
            for user in users_response:
                print(f"\n   👤 User: {user.get('username', 'N/A')}")
                print(f"      ID: {user.get('id', 'N/A')}")
                print(f"      Email: {user.get('email', 'N/A')}")
                print(f"      Role: {user.get('role', 'N/A')}")
                print(f"      Is Business: {user.get('is_business', 'N/A')}")
                print(f"      Business Name: {user.get('business_name', 'N/A')}")
                print(f"      Company Name: {user.get('company_name', 'N/A')}")
                
                if user.get('role') == 'admin':
                    admin_users.append(user)
                
                if user.get('is_business', False):
                    business_users.append(user)
            
            print(f"\n📊 User Analysis Summary:")
            print(f"   Admin users: {len(admin_users)}")
            print(f"   Business users: {len(business_users)}")
            
            # Check if the specific admin user has correct business status
            target_admin_id = "68b191ec38e6062fee10bd27"
            target_admin = None
            
            for user in users_response:
                if user.get('id') == target_admin_id:
                    target_admin = user
                    break
            
            if target_admin:
                is_business = target_admin.get('is_business', False)
                business_name = target_admin.get('business_name', '') or target_admin.get('company_name', '')
                
                print(f"\n🎯 Target Admin User (ID: {target_admin_id}):")
                print(f"   Username: {target_admin.get('username', 'N/A')}")
                print(f"   Is Business: {is_business}")
                print(f"   Business Name: {business_name}")
                
                target_admin_correct = is_business and business_name
                self.log_test("Target Admin Business Status", target_admin_correct,
                             f"Admin {target_admin_id} has correct business status: {target_admin_correct}")
                
                return target_admin_correct
            else:
                self.log_test("Target Admin Business Status", False, f"Admin {target_admin_id} not found in users")
                return False
        
        return False

    def test_business_vs_private_badges(self):
        """Test that business and private badges are correctly assigned"""
        success, response = self.run_test(
            "Browse Listings for Badge Analysis",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success:
            print(f"\n🏷️ Business vs Private Badge Analysis:")
            
            business_badge_listings = []
            private_badge_listings = []
            incorrect_badges = []
            
            for listing in response:
                seller = listing.get('seller', {})
                is_business = seller.get('is_business', False)
                business_name = seller.get('business_name', '')
                seller_username = seller.get('username', 'Unknown')
                listing_title = listing.get('title', 'Unknown')[:30]
                
                # Determine what badge should be shown
                should_show_business = is_business and business_name
                
                if should_show_business:
                    business_badge_listings.append({
                        'title': listing_title,
                        'seller': seller_username,
                        'business_name': business_name
                    })
                else:
                    private_badge_listings.append({
                        'title': listing_title,
                        'seller': seller_username
                    })
                
                # Check for admin listings specifically
                if (seller_username == 'sash_admin' or 
                    'admin' in seller_username.lower() or
                    listing.get('seller_id') == self.admin_user.get('id') if self.admin_user else False):
                    
                    if not should_show_business:
                        incorrect_badges.append({
                            'title': listing_title,
                            'seller': seller_username,
                            'issue': 'Admin listing showing Private badge instead of Business'
                        })
            
            print(f"   Business badge listings: {len(business_badge_listings)}")
            print(f"   Private badge listings: {len(private_badge_listings)}")
            print(f"   Incorrect badge assignments: {len(incorrect_badges)}")
            
            # Show some examples
            if business_badge_listings:
                print(f"\n   ✅ Business Badge Examples:")
                for listing in business_badge_listings[:3]:
                    print(f"      '{listing['title']}' by {listing['seller']} ({listing['business_name']})")
            
            if private_badge_listings:
                print(f"\n   🏠 Private Badge Examples:")
                for listing in private_badge_listings[:3]:
                    print(f"      '{listing['title']}' by {listing['seller']}")
            
            if incorrect_badges:
                print(f"\n   ❌ Incorrect Badge Assignments:")
                for listing in incorrect_badges:
                    print(f"      '{listing['title']}' by {listing['seller']}: {listing['issue']}")
            
            badges_correct = len(incorrect_badges) == 0
            self.log_test("Business vs Private Badge Correctness", badges_correct,
                         f"All badges correctly assigned: {badges_correct}, {len(incorrect_badges)} incorrect")
            
            return badges_correct
        
        return False

    def run_seller_status_tests(self):
        """Run all seller status fix tests"""
        print("🚀 Starting Seller Status Fix Tests")
        print("=" * 60)
        print("Testing business badge functionality and seller enrichment logic")
        print("=" * 60)

        # Test 1: Admin login
        if not self.test_admin_login():
            print("❌ Admin login failed - stopping tests")
            return False

        # Test 2: Admin user profile verification
        print(f"\n1️⃣ Testing Admin User Profile (ID: {self.admin_user.get('id', 'N/A')})...")
        admin_profile_success = self.test_admin_user_profile()

        # Test 3: Browse listings seller information
        print(f"\n2️⃣ Testing Browse Listings Seller Information...")
        browse_seller_success = self.test_browse_listings_seller_info()

        # Test 4: Create admin listing to test business badge
        print(f"\n3️⃣ Testing Admin Listing Business Badge...")
        admin_listing_success = self.test_create_admin_listing()

        # Test 5: Seller enrichment logic
        print(f"\n4️⃣ Testing Seller Enrichment Logic...")
        enrichment_success = self.test_seller_enrichment_logic()

        # Test 6: Business vs Private badge correctness
        print(f"\n5️⃣ Testing Business vs Private Badge Assignment...")
        badge_success = self.test_business_vs_private_badges()

        # Summary
        tests = [
            ("Admin Profile Business Status", admin_profile_success),
            ("Browse Seller Information", browse_seller_success),
            ("Admin Listing Business Badge", admin_listing_success),
            ("Seller Enrichment Logic", enrichment_success),
            ("Badge Assignment Correctness", badge_success)
        ]
        
        passed_tests = sum(1 for _, success in tests if success)
        total_tests = len(tests)
        
        print("\n" + "=" * 60)
        print(f"📊 Seller Status Fix Test Results: {passed_tests}/{total_tests} tests passed")
        print("=" * 60)
        
        for test_name, success in tests:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n📊 Overall Test Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All seller status fix tests passed!")
            print("✅ Business badges are working correctly")
            print("✅ Admin listings show business badges instead of private badges")
            print("✅ Seller enrichment logic is functioning properly")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} test categories failed")
            print("❌ Seller status fix may have issues - see details above")
            return False

def main():
    """Main test execution"""
    tester = SellerStatusTester()
    success = tester.run_seller_status_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())