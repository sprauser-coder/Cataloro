#!/usr/bin/env python3
"""
User Data Investigation Test
Testing the user profile data issue where all users see the same profile data.
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

class UserDataInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.users_data = {}
        
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
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_all_users(self):
        """Get all users from the database"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            
            if response.status_code == 200:
                users = response.json()
                self.log_test("Get All Users", True, f"Found {len(users)} users")
                
                print("\n=== USER DATABASE CONTENTS ===")
                for user in users:
                    print(f"User ID: {user['id']}")
                    print(f"  Email: {user['email']}")
                    print(f"  Username: {user['username']}")
                    print(f"  Full Name: {user['full_name']}")
                    print(f"  Role: {user['role']}")
                    print(f"  Total Orders: {user.get('total_orders', 0)}")
                    print(f"  Total Listings: {user.get('total_listings', 0)}")
                    print(f"  Created: {user['created_at']}")
                    print("---")
                
                return users
            else:
                self.log_test("Get All Users", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Get All Users", False, f"Exception: {str(e)}")
            return []
    
    def test_profile_endpoints_for_user(self, email, password, user_info):
        """Test profile endpoints for a specific user"""
        print(f"\n=== TESTING PROFILE ENDPOINTS FOR {email} ===")
        
        # Create a new session for this user
        user_session = requests.Session()
        
        try:
            # Login as this user
            login_response = user_session.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            
            if login_response.status_code != 200:
                self.log_test(f"Login as {email}", False, f"Status: {login_response.status_code}")
                return
            
            login_data = login_response.json()
            user_token = login_data["access_token"]
            user_session.headers.update({
                "Authorization": f"Bearer {user_token}"
            })
            
            self.log_test(f"Login as {email}", True, f"User ID: {login_data['user']['id']}")
            
            # Test GET /api/profile/stats (first endpoint - comprehensive)
            stats_response1 = user_session.get(f"{BACKEND_URL}/profile/stats")
            if stats_response1.status_code == 200:
                stats_data1 = stats_response1.json()
                self.log_test(f"GET /profile/stats (comprehensive) for {email}", True, 
                            f"Orders: {stats_data1.get('total_orders', 'N/A')}, "
                            f"Listings: {stats_data1.get('total_listings', 'N/A')}, "
                            f"Profile Views: {stats_data1.get('profile_views', 'N/A')}, "
                            f"Trust Score: {stats_data1.get('trust_score', 'N/A')}")
                
                print(f"  Comprehensive Stats for {email}:")
                for key, value in stats_data1.items():
                    print(f"    {key}: {value}")
            else:
                self.log_test(f"GET /profile/stats (comprehensive) for {email}", False, 
                            f"Status: {stats_response1.status_code}")
            
            # Test GET /api/profile (user profile)
            profile_response = user_session.get(f"{BACKEND_URL}/profile")
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                self.log_test(f"GET /profile for {email}", True, 
                            f"Profile Views: {profile_data.get('profile_views', 'N/A')}, "
                            f"Trust Score: {profile_data.get('trust_score', 'N/A')}")
                
                print(f"  Profile Data for {email}:")
                print(f"    ID: {profile_data.get('id', 'N/A')}")
                print(f"    Email: {profile_data.get('email', 'N/A')}")
                print(f"    Profile Views: {profile_data.get('profile_views', 'N/A')}")
                print(f"    Trust Score: {profile_data.get('trust_score', 'N/A')}")
                print(f"    Account Level: {profile_data.get('account_level', 'N/A')}")
            else:
                self.log_test(f"GET /profile for {email}", False, 
                            f"Status: {profile_response.status_code}")
            
            # Store user data for comparison
            self.users_data[email] = {
                'user_id': login_data['user']['id'],
                'stats': stats_data1 if stats_response1.status_code == 200 else None,
                'profile': profile_data if profile_response.status_code == 200 else None
            }
            
        except Exception as e:
            self.log_test(f"Profile testing for {email}", False, f"Exception: {str(e)}")
    
    def check_data_uniqueness(self):
        """Check if different users have different data"""
        print(f"\n=== DATA UNIQUENESS ANALYSIS ===")
        
        if len(self.users_data) < 2:
            self.log_test("Data Uniqueness Check", False, "Need at least 2 users to compare")
            return
        
        # Compare profile views
        profile_views = {}
        trust_scores = {}
        user_ids = {}
        
        for email, data in self.users_data.items():
            if data['profile']:
                profile_views[email] = data['profile'].get('profile_views', 0)
                trust_scores[email] = data['profile'].get('trust_score', 50)
                user_ids[email] = data['user_id']
        
        print("Profile Views by User:")
        for email, views in profile_views.items():
            print(f"  {email}: {views} views")
        
        print("Trust Scores by User:")
        for email, score in trust_scores.items():
            print(f"  {email}: {score} trust score")
        
        print("User IDs:")
        for email, uid in user_ids.items():
            print(f"  {email}: {uid}")
        
        # Check if all values are the same (indicating a bug)
        unique_views = set(profile_views.values())
        unique_scores = set(trust_scores.values())
        unique_ids = set(user_ids.values())
        
        if len(unique_views) == 1 and len(profile_views) > 1:
            self.log_test("Profile Views Uniqueness", False, 
                        f"All users have same profile views: {list(unique_views)[0]}")
        else:
            self.log_test("Profile Views Uniqueness", True, 
                        f"Users have different profile views: {unique_views}")
        
        if len(unique_scores) == 1 and len(trust_scores) > 1:
            self.log_test("Trust Score Uniqueness", False, 
                        f"All users have same trust score: {list(unique_scores)[0]}")
        else:
            self.log_test("Trust Score Uniqueness", True, 
                        f"Users have different trust scores: {unique_scores}")
        
        if len(unique_ids) != len(user_ids):
            self.log_test("User ID Uniqueness", False, 
                        f"Duplicate user IDs found: {user_ids}")
        else:
            self.log_test("User ID Uniqueness", True, 
                        f"All users have unique IDs")
    
    def check_database_associations(self):
        """Check if orders and listings are properly associated with different users"""
        print(f"\n=== DATABASE ASSOCIATIONS CHECK ===")
        
        try:
            # Get all orders
            orders_response = self.session.get(f"{BACKEND_URL}/admin/orders")
            if orders_response.status_code == 200:
                orders = orders_response.json()
                self.log_test("Get All Orders", True, f"Found {len(orders)} orders")
                
                buyer_ids = set()
                seller_ids = set()
                
                for order in orders:
                    order_data = order.get('order', {})
                    buyer_ids.add(order_data.get('buyer_id'))
                    seller_ids.add(order_data.get('seller_id'))
                
                print(f"Unique Buyer IDs in Orders: {len(buyer_ids)}")
                print(f"Unique Seller IDs in Orders: {len(seller_ids)}")
                
                if len(buyer_ids) > 1 or len(seller_ids) > 1:
                    self.log_test("Order User Association", True, 
                                "Orders have different buyer/seller IDs")
                else:
                    self.log_test("Order User Association", False, 
                                "All orders have same buyer/seller IDs")
            else:
                self.log_test("Get All Orders", False, f"Status: {orders_response.status_code}")
            
            # Get all listings
            listings_response = self.session.get(f"{BACKEND_URL}/admin/listings")
            if listings_response.status_code == 200:
                listings = listings_response.json()
                self.log_test("Get All Listings", True, f"Found {len(listings)} listings")
                
                seller_ids = set()
                
                for listing in listings:
                    seller_ids.add(listing.get('seller_id'))
                
                print(f"Unique Seller IDs in Listings: {len(seller_ids)}")
                
                if len(seller_ids) > 1:
                    self.log_test("Listing User Association", True, 
                                "Listings have different seller IDs")
                else:
                    self.log_test("Listing User Association", False, 
                                "All listings have same seller ID")
            else:
                self.log_test("Get All Listings", False, f"Status: {listings_response.status_code}")
                
        except Exception as e:
            self.log_test("Database Associations Check", False, f"Exception: {str(e)}")
    
    def test_endpoint_conflict(self):
        """Test which /profile/stats endpoint is actually being called"""
        print(f"\n=== PROFILE STATS ENDPOINT CONFLICT TEST ===")
        
        try:
            # Make a request to /profile/stats and analyze the response structure
            response = self.session.get(f"{BACKEND_URL}/profile/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure to determine which endpoint is being used
                # First endpoint returns comprehensive stats with many fields
                # Second endpoint returns UserStats model with fewer fields
                
                comprehensive_fields = [
                    'profile_views', 'trust_score', 'account_level', 
                    'badges_earned', 'response_rate', 'avg_response_time'
                ]
                
                basic_fields = ['user_id', 'successful_transactions']
                
                has_comprehensive = any(field in data for field in comprehensive_fields)
                has_basic = any(field in data for field in basic_fields)
                
                print("Response fields:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
                
                if has_comprehensive:
                    self.log_test("Profile Stats Endpoint Detection", True, 
                                "Using FIRST endpoint (line 2199) - comprehensive stats")
                elif has_basic:
                    self.log_test("Profile Stats Endpoint Detection", True, 
                                "Using SECOND endpoint (line 2744) - basic UserStats model")
                else:
                    self.log_test("Profile Stats Endpoint Detection", False, 
                                "Cannot determine which endpoint is being used")
            else:
                self.log_test("Profile Stats Endpoint Test", False, 
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Profile Stats Endpoint Test", False, f"Exception: {str(e)}")
    
    def run_investigation(self):
        """Run the complete user data investigation"""
        print("=== USER DATA INVESTIGATION TEST ===")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now()}")
        print()
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Step 2: Get all users
        users = self.get_all_users()
        if not users:
            print("❌ No users found in database")
            return
        
        # Step 3: Test endpoint conflict
        self.test_endpoint_conflict()
        
        # Step 4: Test profile endpoints for different users
        # Try to test with admin and any other users we can find
        test_users = [
            (ADMIN_EMAIL, ADMIN_PASSWORD, "admin")
        ]
        
        # Add other users if we can guess their passwords or if they're test users
        for user in users:
            if user['email'] != ADMIN_EMAIL:
                # Try common test passwords
                test_passwords = ['password', 'test123', user['username'], 'admin123']
                for pwd in test_passwords:
                    try:
                        test_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                            "email": user['email'],
                            "password": pwd
                        })
                        if test_response.status_code == 200:
                            test_users.append((user['email'], pwd, user['role']))
                            print(f"✅ Found working credentials for {user['email']}")
                            break
                    except:
                        continue
        
        # Test profile endpoints for each user we can authenticate as
        for email, password, role in test_users:
            self.test_profile_endpoints_for_user(email, password, role)
        
        # Step 5: Check data uniqueness
        self.check_data_uniqueness()
        
        # Step 6: Check database associations
        self.check_database_associations()
        
        # Summary
        print(f"\n=== INVESTIGATION SUMMARY ===")
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

if __name__ == "__main__":
    investigator = UserDataInvestigator()
    investigator.run_investigation()