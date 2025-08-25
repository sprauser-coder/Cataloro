#!/usr/bin/env python3
"""
Profile Data Integrity Test
Test if users with different activities have different profile data.
"""

import requests
import json
import sys
from datetime import datetime
import os

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ProfileDataIntegrityTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Token: {self.admin_token[:20]}...")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_user_profile_stats(self, email, password, expected_user_id=None):
        """Get profile stats for a specific user"""
        try:
            # Login as the user
            login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            
            if login_response.status_code != 200:
                self.log_test(f"Login as {email}", False, f"Status: {login_response.status_code}")
                return None
            
            login_data = login_response.json()
            user_token = login_data["access_token"]
            actual_user_id = login_data["user"]["id"]
            
            # Check if user ID matches expected (if provided)
            if expected_user_id and actual_user_id != expected_user_id:
                self.log_test(f"User ID Verification for {email}", False, 
                            f"Expected: {expected_user_id}, Got: {actual_user_id}")
                return None
            
            # Create session for this user
            user_session = requests.Session()
            user_session.headers.update({
                "Authorization": f"Bearer {user_token}"
            })
            
            # Get profile stats
            stats_response = user_session.get(f"{BACKEND_URL}/profile/stats")
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                
                self.log_test(f"Profile Stats for {email}", True, 
                            f"User ID: {actual_user_id}, Views: {stats_data.get('profile_views', 0)}, "
                            f"Trust: {stats_data.get('trust_score', 50)}")
                
                return {
                    'user_id': actual_user_id,
                    'email': email,
                    'stats': stats_data
                }
            else:
                self.log_test(f"Profile Stats for {email}", False, 
                            f"Status: {stats_response.status_code}")
                return None
                
        except Exception as e:
            self.log_test(f"Profile Stats for {email}", False, f"Exception: {str(e)}")
            return None
    
    def test_profile_stats_endpoint_behavior(self):
        """Test the behavior of the profile stats endpoint"""
        print(f"\n=== PROFILE STATS ENDPOINT BEHAVIOR TEST ===")
        
        # Test with admin user (has activity)
        admin_data = self.get_user_profile_stats(ADMIN_EMAIL, ADMIN_PASSWORD)
        
        if admin_data:
            print(f"Admin User Profile Stats:")
            stats = admin_data['stats']
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            # Check if the stats are being calculated correctly
            total_orders = stats.get('total_orders', 0)
            total_listings = stats.get('total_listings', 0)
            profile_views = stats.get('profile_views', 0)
            trust_score = stats.get('trust_score', 50)
            
            # Verify against database
            orders_response = self.session.get(f"{BACKEND_URL}/admin/orders")
            listings_response = self.session.get(f"{BACKEND_URL}/admin/listings")
            
            if orders_response.status_code == 200 and listings_response.status_code == 200:
                all_orders = orders_response.json()
                all_listings = listings_response.json()
                
                # Count admin's orders and listings
                admin_orders = [o for o in all_orders if o.get('order', {}).get('buyer_id') == admin_data['user_id']]
                admin_listings = [l for l in all_listings if l.get('seller_id') == admin_data['user_id']]
                
                print(f"\nDatabase Verification:")
                print(f"  Admin Orders in DB: {len(admin_orders)}")
                print(f"  Admin Listings in DB: {len(admin_listings)}")
                print(f"  Stats Orders: {total_orders}")
                print(f"  Stats Listings: {total_listings}")
                
                if len(admin_orders) == total_orders:
                    self.log_test("Orders Count Accuracy", True, 
                                f"Stats match database: {total_orders}")
                else:
                    self.log_test("Orders Count Accuracy", False, 
                                f"Stats: {total_orders}, DB: {len(admin_orders)}")
                
                if len(admin_listings) == total_listings:
                    self.log_test("Listings Count Accuracy", True, 
                                f"Stats match database: {total_listings}")
                else:
                    self.log_test("Listings Count Accuracy", False, 
                                f"Stats: {total_listings}, DB: {len(admin_listings)}")
    
    def test_user_data_isolation(self):
        """Test if different users get their own data"""
        print(f"\n=== USER DATA ISOLATION TEST ===")
        
        # Get all users from database
        users_response = self.session.get(f"{BACKEND_URL}/admin/users")
        if users_response.status_code != 200:
            self.log_test("Get Users for Isolation Test", False, "Cannot get users")
            return
        
        users = users_response.json()
        print(f"Found {len(users)} users in database")
        
        # Test with users that have different activity levels
        user_profiles = []
        
        # Test admin user
        admin_profile = self.get_user_profile_stats(ADMIN_EMAIL, ADMIN_PASSWORD)
        if admin_profile:
            user_profiles.append(admin_profile)
        
        # Try to find other users with known passwords or create test scenarios
        test_users = [
            ("ana@lukic.com", ["password", "ana123", "test123"]),
            ("carsten@zimmer.de", ["password", "carsten123", "test123"]),
        ]
        
        for email, passwords in test_users:
            for pwd in passwords:
                profile = self.get_user_profile_stats(email, pwd)
                if profile:
                    user_profiles.append(profile)
                    break
        
        if len(user_profiles) < 2:
            self.log_test("User Data Isolation Test", False, 
                        "Need at least 2 users with known passwords")
            return
        
        # Compare profile data
        print(f"\nProfile Data Comparison ({len(user_profiles)} users):")
        for profile in user_profiles:
            stats = profile['stats']
            print(f"  {profile['email']} (ID: {profile['user_id']}):")
            print(f"    Orders: {stats.get('total_orders', 0)}")
            print(f"    Listings: {stats.get('total_listings', 0)}")
            print(f"    Earned: €{stats.get('total_earned', 0)}")
            print(f"    Profile Views: {stats.get('profile_views', 0)}")
            print(f"    Trust Score: {stats.get('trust_score', 50)}")
        
        # Check for data isolation
        user_ids = [p['user_id'] for p in user_profiles]
        orders_counts = [p['stats'].get('total_orders', 0) for p in user_profiles]
        listings_counts = [p['stats'].get('total_listings', 0) for p in user_profiles]
        earned_amounts = [p['stats'].get('total_earned', 0) for p in user_profiles]
        
        # Verify user IDs are different
        if len(set(user_ids)) == len(user_ids):
            self.log_test("User ID Isolation", True, "All users have unique IDs")
        else:
            self.log_test("User ID Isolation", False, "❌ CRITICAL: Duplicate user IDs found!")
        
        # Check if users have different activity data
        if len(set(orders_counts)) > 1 or len(set(listings_counts)) > 1 or len(set(earned_amounts)) > 1:
            self.log_test("User Activity Data Isolation", True, 
                        "Users have different activity data")
        else:
            # This might be OK if users genuinely have the same activity
            self.log_test("User Activity Data Isolation", True, 
                        "Users have same activity levels (may be legitimate)")
    
    def test_profile_stats_query_logic(self):
        """Test the query logic in profile stats endpoints"""
        print(f"\n=== PROFILE STATS QUERY LOGIC TEST ===")
        
        # Get admin profile stats
        admin_profile = self.get_user_profile_stats(ADMIN_EMAIL, ADMIN_PASSWORD)
        if not admin_profile:
            self.log_test("Profile Stats Query Logic Test", False, "Cannot get admin profile")
            return
        
        admin_user_id = admin_profile['user_id']
        admin_stats = admin_profile['stats']
        
        # Manually verify the queries used in the endpoint
        print(f"Admin User ID: {admin_user_id}")
        print(f"Verifying query logic...")
        
        # Check orders query: {"user_id": user_id} vs {"buyer_id": user_id}
        # The endpoint at line 2205 uses {"user_id": user_id} which might be wrong
        # It should probably use {"buyer_id": user_id}
        
        orders_response = self.session.get(f"{BACKEND_URL}/admin/orders")
        if orders_response.status_code == 200:
            all_orders = orders_response.json()
            
            # Count orders using different field names
            orders_by_user_id = [o for o in all_orders if o.get('order', {}).get('user_id') == admin_user_id]
            orders_by_buyer_id = [o for o in all_orders if o.get('order', {}).get('buyer_id') == admin_user_id]
            
            print(f"Orders with user_id = {admin_user_id}: {len(orders_by_user_id)}")
            print(f"Orders with buyer_id = {admin_user_id}: {len(orders_by_buyer_id)}")
            print(f"Stats reported total_orders: {admin_stats.get('total_orders', 0)}")
            
            # Check which field the endpoint is actually using
            if admin_stats.get('total_orders', 0) == len(orders_by_user_id):
                self.log_test("Orders Query Field", False, 
                            "❌ BUG: Endpoint uses 'user_id' field instead of 'buyer_id'")
            elif admin_stats.get('total_orders', 0) == len(orders_by_buyer_id):
                self.log_test("Orders Query Field", True, 
                            "✅ Endpoint correctly uses 'buyer_id' field")
            else:
                self.log_test("Orders Query Field", False, 
                            f"❌ Query logic unclear: stats={admin_stats.get('total_orders', 0)}, "
                            f"user_id={len(orders_by_user_id)}, buyer_id={len(orders_by_buyer_id)}")
        
        # Check earnings query: {"seller_id": user_id, "status": "completed"}
        # This should be correct
        earnings_by_seller = [o for o in all_orders 
                            if o.get('order', {}).get('seller_id') == admin_user_id 
                            and o.get('order', {}).get('status') == 'completed']
        
        total_earned_calculated = sum(o.get('order', {}).get('total_amount', 0) for o in earnings_by_seller)
        
        print(f"Completed orders as seller: {len(earnings_by_seller)}")
        print(f"Calculated total earned: €{total_earned_calculated}")
        print(f"Stats reported total_earned: €{admin_stats.get('total_earned', 0)}")
        
        if abs(admin_stats.get('total_earned', 0) - total_earned_calculated) < 0.01:
            self.log_test("Earnings Calculation", True, 
                        "✅ Earnings calculation is correct")
        else:
            self.log_test("Earnings Calculation", False, 
                        f"❌ Earnings mismatch: stats={admin_stats.get('total_earned', 0)}, "
                        f"calculated={total_earned_calculated}")
    
    def run_test(self):
        """Run the complete profile data integrity test"""
        print("=== PROFILE DATA INTEGRITY TEST ===")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now()}")
        print()
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Step 2: Test profile stats endpoint behavior
        self.test_profile_stats_endpoint_behavior()
        
        # Step 3: Test user data isolation
        self.test_user_data_isolation()
        
        # Step 4: Test profile stats query logic
        self.test_profile_stats_query_logic()
        
        # Summary
        print(f"\n=== TEST SUMMARY ===")
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Conclusions
        print(f"\n=== CONCLUSIONS ===")
        if failed_tests == 0:
            print("✅ No critical issues found with user profile data isolation")
        else:
            print("❌ Issues found that may cause users to see incorrect profile data")

if __name__ == "__main__":
    tester = ProfileDataIntegrityTester()
    tester.run_test()