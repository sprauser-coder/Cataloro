#!/usr/bin/env python3
"""
Business Badge Debug Test Suite
Debug the specific business badge data for the current 4 listings visible in the browse page.
"""

import requests
import sys
import json
from datetime import datetime

class BusinessBadgeDebugger:
    def __init__(self, base_url="https://cataloro-ads.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.findings = []

    def log_finding(self, category, message, data=None):
        """Log debug findings"""
        finding = {
            "category": category,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.findings.append(finding)
        print(f"🔍 {category}: {message}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)[:300]}...")

    def make_request(self, method, endpoint, data=None):
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": f"Status {response.status_code}: {response.text}"}
        except Exception as e:
            return False, {"error": str(e)}

    def test_current_browse_response(self):
        """Check Current Browse Response - examine all 4 listings' seller objects"""
        print("\n1️⃣ CHECKING CURRENT BROWSE RESPONSE")
        print("=" * 50)
        
        success, response = self.make_request('GET', 'api/marketplace/browse')
        
        if not success:
            self.log_finding("BROWSE_ERROR", "Failed to get browse response", response)
            return False
        
        listings = response if isinstance(response, list) else []
        self.log_finding("BROWSE_COUNT", f"Found {len(listings)} listings in browse", {"count": len(listings)})
        
        if len(listings) == 0:
            self.log_finding("BROWSE_EMPTY", "No listings found - cannot debug business badges", {})
            return False
        
        # Examine each listing's seller object in detail
        for i, listing in enumerate(listings):
            listing_id = listing.get('id', 'unknown')
            title = listing.get('title', 'No title')
            seller = listing.get('seller', {})
            
            print(f"\n📋 LISTING {i+1}: {title[:50]}...")
            print(f"   ID: {listing_id}")
            print(f"   Seller Object: {json.dumps(seller, indent=4)}")
            
            # Check seller object structure
            seller_analysis = {
                "has_name": "name" in seller,
                "has_username": "username" in seller,
                "has_email": "email" in seller,
                "has_is_business": "is_business" in seller,
                "has_business_name": "business_name" in seller,
                "has_verified": "verified" in seller,
                "name_value": seller.get('name', 'MISSING'),
                "username_value": seller.get('username', 'MISSING'),
                "email_value": seller.get('email', 'MISSING'),
                "is_business_value": seller.get('is_business', 'MISSING'),
                "business_name_value": seller.get('business_name', 'MISSING'),
                "verified_value": seller.get('verified', 'MISSING'),
                "seller_id_in_listing": listing.get('seller_id', 'MISSING')
            }
            
            self.log_finding(f"LISTING_{i+1}_SELLER", f"Seller analysis for listing {i+1}", seller_analysis)
            
            # Flag potential issues
            if seller.get('is_business') is True:
                self.log_finding(f"BUSINESS_FOUND", f"Found business account in listing {i+1}", {
                    "listing_id": listing_id,
                    "business_name": seller.get('business_name', 'No business name'),
                    "seller_name": seller.get('name', 'No name')
                })
            elif seller.get('is_business') is False:
                self.log_finding(f"PRIVATE_ACCOUNT", f"Found private account in listing {i+1}", {
                    "listing_id": listing_id,
                    "seller_name": seller.get('name', 'No name')
                })
            else:
                self.log_finding(f"MISSING_BUSINESS_FLAG", f"Missing is_business flag in listing {i+1}", {
                    "listing_id": listing_id,
                    "seller_object": seller
                })
        
        return True

    def test_business_account_users(self):
        """Verify Business Account Users - check if any users have is_business=true"""
        print("\n2️⃣ CHECKING BUSINESS ACCOUNT USERS IN DATABASE")
        print("=" * 50)
        
        # Get all users via admin endpoint
        success, response = self.make_request('GET', 'api/admin/users')
        
        if not success:
            self.log_finding("USERS_ERROR", "Failed to get users list", response)
            return False
        
        users = response if isinstance(response, list) else []
        self.log_finding("USERS_COUNT", f"Found {len(users)} users in database", {"count": len(users)})
        
        business_users = []
        private_users = []
        missing_flag_users = []
        
        for user in users:
            user_id = user.get('id', 'unknown')
            username = user.get('username', 'No username')
            email = user.get('email', 'No email')
            is_business = user.get('is_business')
            
            print(f"\n👤 USER: {username} ({email})")
            print(f"   ID: {user_id}")
            print(f"   is_business: {is_business}")
            print(f"   Full user data: {json.dumps(user, indent=4)}")
            
            if is_business is True:
                business_users.append({
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "business_name": user.get('business_name', user.get('company_name', 'No business name')),
                    "full_name": user.get('full_name', 'No full name')
                })
                self.log_finding("BUSINESS_USER_FOUND", f"Found business user: {username}", user)
            elif is_business is False:
                private_users.append({
                    "id": user_id,
                    "username": username,
                    "email": email
                })
            else:
                missing_flag_users.append({
                    "id": user_id,
                    "username": username,
                    "email": email
                })
                self.log_finding("MISSING_BUSINESS_FLAG_USER", f"User missing is_business flag: {username}", user)
        
        self.log_finding("BUSINESS_USERS_SUMMARY", f"Business users: {len(business_users)}, Private users: {len(private_users)}, Missing flag: {len(missing_flag_users)}", {
            "business_users": business_users,
            "private_users": private_users[:3],  # First 3 only
            "missing_flag_users": missing_flag_users
        })
        
        return len(business_users) > 0

    def test_seller_id_matching(self):
        """Cross-Reference Seller IDs - match seller_id in listings with user profiles"""
        print("\n3️⃣ CROSS-REFERENCING SELLER IDs WITH USER PROFILES")
        print("=" * 50)
        
        # Get browse listings
        browse_success, browse_response = self.make_request('GET', 'api/marketplace/browse')
        if not browse_success:
            self.log_finding("BROWSE_ERROR", "Failed to get browse listings", browse_response)
            return False
        
        # Get all users
        users_success, users_response = self.make_request('GET', 'api/admin/users')
        if not users_success:
            self.log_finding("USERS_ERROR", "Failed to get users", users_response)
            return False
        
        listings = browse_response if isinstance(browse_response, list) else []
        users = users_response if isinstance(users_response, list) else []
        
        # Create user lookup dictionary
        user_lookup = {}
        for user in users:
            user_id = user.get('id')
            if user_id:
                user_lookup[user_id] = user
        
        self.log_finding("USER_LOOKUP", f"Created user lookup with {len(user_lookup)} users", {
            "user_ids": list(user_lookup.keys())[:5]  # First 5 IDs
        })
        
        # Check each listing's seller_id
        for i, listing in enumerate(listings):
            listing_id = listing.get('id', 'unknown')
            title = listing.get('title', 'No title')
            seller_id = listing.get('seller_id')
            seller_object = listing.get('seller', {})
            
            print(f"\n🔗 LISTING {i+1}: {title[:50]}...")
            print(f"   Listing ID: {listing_id}")
            print(f"   Seller ID: {seller_id}")
            
            if seller_id in user_lookup:
                actual_user = user_lookup[seller_id]
                print(f"   ✅ Found matching user profile")
                print(f"   User Profile: {json.dumps(actual_user, indent=4)}")
                
                # Compare seller object with actual user profile
                comparison = {
                    "seller_id_match": True,
                    "actual_username": actual_user.get('username', 'No username'),
                    "actual_email": actual_user.get('email', 'No email'),
                    "actual_is_business": actual_user.get('is_business'),
                    "actual_business_name": actual_user.get('business_name', actual_user.get('company_name', 'No business name')),
                    "seller_object_name": seller_object.get('name', 'No name'),
                    "seller_object_username": seller_object.get('username', 'No username'),
                    "seller_object_is_business": seller_object.get('is_business'),
                    "seller_object_business_name": seller_object.get('business_name', 'No business name'),
                    "name_matches": False,
                    "business_flag_matches": False,
                    "business_name_matches": False
                }
                
                # Check if data matches
                comparison["name_matches"] = (
                    comparison["seller_object_name"] == comparison["actual_username"] or
                    comparison["seller_object_name"] == comparison["actual_email"]
                )
                comparison["business_flag_matches"] = comparison["seller_object_is_business"] == comparison["actual_is_business"]
                comparison["business_name_matches"] = comparison["seller_object_business_name"] == comparison["actual_business_name"]
                
                self.log_finding(f"SELLER_MATCH_{i+1}", f"Seller ID matching analysis for listing {i+1}", comparison)
                
                # Flag mismatches
                if not comparison["business_flag_matches"]:
                    self.log_finding("BUSINESS_FLAG_MISMATCH", f"Business flag mismatch in listing {i+1}", {
                        "listing_id": listing_id,
                        "actual_is_business": comparison["actual_is_business"],
                        "seller_object_is_business": comparison["seller_object_is_business"]
                    })
                
                if comparison["actual_is_business"] and not comparison["business_name_matches"]:
                    self.log_finding("BUSINESS_NAME_MISMATCH", f"Business name mismatch in listing {i+1}", {
                        "listing_id": listing_id,
                        "actual_business_name": comparison["actual_business_name"],
                        "seller_object_business_name": comparison["seller_object_business_name"]
                    })
            else:
                print(f"   ❌ No matching user profile found")
                self.log_finding(f"SELLER_NO_MATCH_{i+1}", f"No user profile found for seller_id in listing {i+1}", {
                    "listing_id": listing_id,
                    "seller_id": seller_id,
                    "available_user_ids": list(user_lookup.keys())[:5]
                })
        
        return True

    def test_specific_user_profiles(self):
        """Debug Specific Users - check profiles of users who should be business accounts"""
        print("\n4️⃣ DEBUGGING SPECIFIC USER PROFILES")
        print("=" * 50)
        
        # Test specific user profiles that might be business accounts
        test_emails = [
            "admin@cataloro.com",
            "business@cataloro.com", 
            "cataloro_business@example.com",
            "user@cataloro.com"
        ]
        
        for email in test_emails:
            print(f"\n🔍 Testing login and profile for: {email}")
            
            # Try to login as this user
            login_success, login_response = self.make_request('POST', 'api/auth/login', {
                "email": email,
                "password": "demo123"
            })
            
            if login_success and 'user' in login_response:
                user_data = login_response['user']
                user_id = user_data.get('id')
                
                print(f"   ✅ Login successful")
                print(f"   User Data: {json.dumps(user_data, indent=4)}")
                
                # Get full profile
                if user_id:
                    profile_success, profile_response = self.make_request('GET', f'api/auth/profile/{user_id}')
                    if profile_success:
                        print(f"   Profile Data: {json.dumps(profile_response, indent=4)}")
                        
                        self.log_finding(f"USER_PROFILE_{email}", f"Profile data for {email}", {
                            "login_data": user_data,
                            "profile_data": profile_response,
                            "is_business_in_login": user_data.get('is_business'),
                            "is_business_in_profile": profile_response.get('is_business'),
                            "business_name_in_profile": profile_response.get('business_name', profile_response.get('company_name'))
                        })
                    else:
                        self.log_finding(f"PROFILE_ERROR_{email}", f"Failed to get profile for {email}", profile_response)
            else:
                print(f"   ❌ Login failed: {login_response}")
                self.log_finding(f"LOGIN_FAILED_{email}", f"Login failed for {email}", login_response)
        
        return True

    def create_business_user_test(self):
        """Create a test business user to verify the system works"""
        print("\n5️⃣ CREATING TEST BUSINESS USER")
        print("=" * 50)
        
        # Register a new business user
        business_user_data = {
            "username": "test_business_user",
            "email": "testbusiness@cataloro.com",
            "full_name": "Test Business Account",
            "is_business": True,
            "business_name": "Test Business Solutions",
            "company_name": "Test Business Solutions"
        }
        
        register_success, register_response = self.make_request('POST', 'api/auth/register', business_user_data)
        
        if register_success:
            print(f"   ✅ Business user registered successfully")
            print(f"   Response: {json.dumps(register_response, indent=4)}")
            
            # Login as the business user
            login_success, login_response = self.make_request('POST', 'api/auth/login', {
                "email": "testbusiness@cataloro.com",
                "password": "demo123"
            })
            
            if login_success and 'user' in login_response:
                business_user = login_response['user']
                user_id = business_user.get('id')
                
                print(f"   ✅ Business user login successful")
                print(f"   Business User Data: {json.dumps(business_user, indent=4)}")
                
                # Create a test listing as this business user
                business_listing = {
                    "title": "Business Test Listing - Professional Service",
                    "description": "Test listing created by business account to verify badge system",
                    "price": 500.00,
                    "category": "Services",
                    "condition": "New",
                    "seller_id": user_id,
                    "images": ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"]
                }
                
                listing_success, listing_response = self.make_request('POST', 'api/listings', business_listing)
                
                if listing_success:
                    listing_id = listing_response.get('listing_id')
                    print(f"   ✅ Business listing created: {listing_id}")
                    
                    # Check if it appears in browse with correct business badge
                    browse_success, browse_response = self.make_request('GET', 'api/marketplace/browse')
                    
                    if browse_success:
                        listings = browse_response if isinstance(browse_response, list) else []
                        business_listing_found = None
                        
                        for listing in listings:
                            if listing.get('id') == listing_id:
                                business_listing_found = listing
                                break
                        
                        if business_listing_found:
                            seller = business_listing_found.get('seller', {})
                            print(f"   📋 Business listing found in browse")
                            print(f"   Seller Object: {json.dumps(seller, indent=4)}")
                            
                            self.log_finding("BUSINESS_LISTING_TEST", "Created business listing and checked browse", {
                                "listing_id": listing_id,
                                "seller_object": seller,
                                "is_business_flag": seller.get('is_business'),
                                "business_name": seller.get('business_name'),
                                "expected_is_business": True,
                                "expected_business_name": "Test Business Solutions"
                            })
                            
                            # Check if business badge would show correctly
                            if seller.get('is_business') is True:
                                print(f"   ✅ Business badge should show correctly")
                                self.log_finding("BUSINESS_BADGE_SUCCESS", "Business badge data is correct", seller)
                            else:
                                print(f"   ❌ Business badge would NOT show - is_business: {seller.get('is_business')}")
                                self.log_finding("BUSINESS_BADGE_FAILURE", "Business badge data is incorrect", seller)
                        else:
                            self.log_finding("BUSINESS_LISTING_NOT_FOUND", "Business listing not found in browse", {
                                "listing_id": listing_id,
                                "total_listings": len(listings)
                            })
                else:
                    self.log_finding("BUSINESS_LISTING_FAILED", "Failed to create business listing", listing_response)
            else:
                self.log_finding("BUSINESS_LOGIN_FAILED", "Failed to login as business user", login_response)
        else:
            self.log_finding("BUSINESS_REGISTER_FAILED", "Failed to register business user", register_response)
        
        return True

    def run_debug_tests(self):
        """Run all debug tests"""
        print("🔍 BUSINESS BADGE DEBUG INVESTIGATION")
        print("=" * 60)
        print("Investigating why ALL 4 listings show 'Private' badges")
        print("when some should show 'Business' badges")
        print("=" * 60)
        
        # Run all debug tests
        tests = [
            ("Current Browse Response Analysis", self.test_current_browse_response),
            ("Business Account Users Verification", self.test_business_account_users),
            ("Seller ID Cross-Reference", self.test_seller_id_matching),
            ("Specific User Profile Debug", self.test_specific_user_profiles),
            ("Business User Creation Test", self.create_business_user_test)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results.append((test_name, result))
                print(f"✅ {test_name}: {'PASSED' if result else 'COMPLETED'}")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Print summary
        print("\n" + "=" * 60)
        print("🔍 BUSINESS BADGE DEBUG SUMMARY")
        print("=" * 60)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "⚠️ COMPLETED"
            print(f"{status} {test_name}")
        
        # Print key findings
        print("\n📋 KEY FINDINGS:")
        for finding in self.findings:
            if finding['category'] in ['BUSINESS_USER_FOUND', 'BUSINESS_FLAG_MISMATCH', 'BUSINESS_BADGE_FAILURE', 'BUSINESS_BADGE_SUCCESS']:
                print(f"🔍 {finding['category']}: {finding['message']}")
        
        # Provide recommendations
        print("\n💡 RECOMMENDATIONS:")
        
        business_users_found = any(f['category'] == 'BUSINESS_USER_FOUND' for f in self.findings)
        business_flag_mismatches = any(f['category'] == 'BUSINESS_FLAG_MISMATCH' for f in self.findings)
        
        if not business_users_found:
            print("1. No business users found in database - create business accounts with is_business=true")
        
        if business_flag_mismatches:
            print("2. Business flag mismatches detected - check seller enrichment logic in /api/marketplace/browse")
        
        print("3. Check if seller enrichment query is using correct field names (is_business vs business_name vs company_name)")
        print("4. Verify that business account data is being saved properly during user registration/update")
        
        return True

def main():
    """Main debug execution"""
    debugger = BusinessBadgeDebugger()
    debugger.run_debug_tests()
    return 0

if __name__ == "__main__":
    sys.exit(main())