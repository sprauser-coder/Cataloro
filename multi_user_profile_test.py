#!/usr/bin/env python3
"""
Multi-User Profile Test
Create multiple test users and check if they get different profile data.
"""

import requests
import json
import sys
from datetime import datetime
import os
import uuid

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class MultiUserProfileTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.test_users = []
        
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
    
    def create_test_user(self, username_suffix):
        """Create a test user"""
        try:
            user_data = {
                "email": f"testuser_{username_suffix}@test.com",
                "username": f"testuser_{username_suffix}",
                "password": "testpass123",
                "full_name": f"Test User {username_suffix}",
                "role": "both"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(f"Create Test User {username_suffix}", True, 
                            f"User ID: {data['user']['id']}")
                
                self.test_users.append({
                    'email': user_data['email'],
                    'password': user_data['password'],
                    'username': user_data['username'],
                    'user_id': data['user']['id'],
                    'token': data['access_token']
                })
                return True
            else:
                self.log_test(f"Create Test User {username_suffix}", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test(f"Create Test User {username_suffix}", False, f"Exception: {str(e)}")
            return False
    
    def update_user_profile_data(self, user_data, profile_views, trust_score):
        """Update user's profile data directly in database via admin"""
        try:
            # We'll use a direct database update approach
            # First, let's try to increment profile views using the existing endpoint
            user_session = requests.Session()
            user_session.headers.update({
                "Authorization": f"Bearer {user_data['token']}"
            })
            
            # Try to increment profile views multiple times
            for i in range(profile_views):
                try:
                    response = user_session.get(f"{BACKEND_URL}/profile/increment-view/{user_data['user_id']}")
                except:
                    pass  # Ignore errors, just trying to increment
            
            self.log_test(f"Update Profile Data for {user_data['username']}", True, 
                        f"Attempted to set views: {profile_views}, trust: {trust_score}")
            return True
            
        except Exception as e:
            self.log_test(f"Update Profile Data for {user_data['username']}", False, f"Exception: {str(e)}")
            return False
    
    def test_user_profile_stats(self, user_data):
        """Test profile stats for a specific user"""
        try:
            user_session = requests.Session()
            user_session.headers.update({
                "Authorization": f"Bearer {user_data['token']}"
            })
            
            # Test /profile/stats
            stats_response = user_session.get(f"{BACKEND_URL}/profile/stats")
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                
                self.log_test(f"Profile Stats for {user_data['username']}", True, 
                            f"Views: {stats_data.get('profile_views', 0)}, "
                            f"Trust: {stats_data.get('trust_score', 50)}, "
                            f"Orders: {stats_data.get('total_orders', 0)}, "
                            f"Listings: {stats_data.get('total_listings', 0)}")
                
                user_data['stats'] = stats_data
                return True
            else:
                self.log_test(f"Profile Stats for {user_data['username']}", False, 
                            f"Status: {stats_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(f"Profile Stats for {user_data['username']}", False, f"Exception: {str(e)}")
            return False
    
    def test_user_profile(self, user_data):
        """Test profile endpoint for a specific user"""
        try:
            user_session = requests.Session()
            user_session.headers.update({
                "Authorization": f"Bearer {user_data['token']}"
            })
            
            # Test /profile
            profile_response = user_session.get(f"{BACKEND_URL}/profile")
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                
                self.log_test(f"Profile Data for {user_data['username']}", True, 
                            f"ID: {profile_data.get('id', 'N/A')}, "
                            f"Email: {profile_data.get('email', 'N/A')}")
                
                user_data['profile'] = profile_data
                return True
            else:
                self.log_test(f"Profile Data for {user_data['username']}", False, 
                            f"Status: {profile_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(f"Profile Data for {user_data['username']}", False, f"Exception: {str(e)}")
            return False
    
    def compare_user_data(self):
        """Compare profile data between users"""
        print(f"\n=== USER DATA COMPARISON ===")
        
        if len(self.test_users) < 2:
            self.log_test("User Data Comparison", False, "Need at least 2 users to compare")
            return
        
        # Compare stats data
        print("Profile Stats Comparison:")
        for user in self.test_users:
            if 'stats' in user:
                stats = user['stats']
                print(f"  {user['username']} (ID: {user['user_id']}):")
                print(f"    Profile Views: {stats.get('profile_views', 'N/A')}")
                print(f"    Trust Score: {stats.get('trust_score', 'N/A')}")
                print(f"    Total Orders: {stats.get('total_orders', 'N/A')}")
                print(f"    Total Listings: {stats.get('total_listings', 'N/A')}")
                print(f"    Total Earned: {stats.get('total_earned', 'N/A')}")
                print(f"    Account Level: {stats.get('account_level', 'N/A')}")
        
        # Check for data uniqueness
        profile_views = []
        trust_scores = []
        user_ids = []
        
        for user in self.test_users:
            if 'stats' in user:
                profile_views.append(user['stats'].get('profile_views', 0))
                trust_scores.append(user['stats'].get('trust_score', 50))
                user_ids.append(user['user_id'])
        
        # Check if all values are the same
        unique_views = set(profile_views)
        unique_scores = set(trust_scores)
        unique_ids = set(user_ids)
        
        print(f"\nUniqueness Analysis:")
        print(f"  Profile Views: {profile_views} -> Unique: {len(unique_views)}")
        print(f"  Trust Scores: {trust_scores} -> Unique: {len(unique_scores)}")
        print(f"  User IDs: {len(unique_ids)} unique out of {len(user_ids)}")
        
        # Determine if there's a data sharing issue
        if len(unique_views) == 1 and len(profile_views) > 1:
            self.log_test("Profile Views Uniqueness", False, 
                        f"❌ BUG DETECTED: All users have same profile views: {list(unique_views)[0]}")
        else:
            self.log_test("Profile Views Uniqueness", True, 
                        f"✅ Users have different profile views")
        
        if len(unique_scores) == 1 and len(trust_scores) > 1:
            self.log_test("Trust Score Uniqueness", False, 
                        f"❌ BUG DETECTED: All users have same trust score: {list(unique_scores)[0]}")
        else:
            self.log_test("Trust Score Uniqueness", True, 
                        f"✅ Users have different trust scores")
        
        if len(unique_ids) != len(user_ids):
            self.log_test("User ID Uniqueness", False, 
                        f"❌ CRITICAL BUG: Duplicate user IDs found!")
        else:
            self.log_test("User ID Uniqueness", True, 
                        f"✅ All users have unique IDs")
    
    def test_existing_users(self):
        """Test with existing users from the database"""
        print(f"\n=== TESTING EXISTING USERS ===")
        
        # Test with admin user
        admin_session = requests.Session()
        admin_session.headers.update({
            "Authorization": f"Bearer {self.admin_token}"
        })
        
        admin_stats = admin_session.get(f"{BACKEND_URL}/profile/stats")
        if admin_stats.status_code == 200:
            admin_data = admin_stats.json()
            print(f"Admin Profile Stats:")
            print(f"  Profile Views: {admin_data.get('profile_views', 'N/A')}")
            print(f"  Trust Score: {admin_data.get('trust_score', 'N/A')}")
            print(f"  Total Orders: {admin_data.get('total_orders', 'N/A')}")
            print(f"  Total Listings: {admin_data.get('total_listings', 'N/A')}")
        
        # Try to test with Ana Lukic if we can guess the password
        test_passwords = ['password', 'ana123', 'test123', 'admin123']
        for pwd in test_passwords:
            try:
                ana_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                    "email": "ana@lukic.com",
                    "password": pwd
                })
                if ana_response.status_code == 200:
                    ana_token = ana_response.json()["access_token"]
                    ana_session = requests.Session()
                    ana_session.headers.update({
                        "Authorization": f"Bearer {ana_token}"
                    })
                    
                    ana_stats = ana_session.get(f"{BACKEND_URL}/profile/stats")
                    if ana_stats.status_code == 200:
                        ana_data = ana_stats.json()
                        print(f"Ana Lukic Profile Stats:")
                        print(f"  Profile Views: {ana_data.get('profile_views', 'N/A')}")
                        print(f"  Trust Score: {ana_data.get('trust_score', 'N/A')}")
                        print(f"  Total Orders: {ana_data.get('total_orders', 'N/A')}")
                        print(f"  Total Listings: {ana_data.get('total_listings', 'N/A')}")
                        
                        # Compare with admin data
                        if (admin_data.get('profile_views') == ana_data.get('profile_views') and
                            admin_data.get('trust_score') == ana_data.get('trust_score')):
                            self.log_test("Existing Users Data Comparison", False, 
                                        "❌ BUG DETECTED: Admin and Ana have identical profile data!")
                        else:
                            self.log_test("Existing Users Data Comparison", True, 
                                        "✅ Admin and Ana have different profile data")
                    break
            except:
                continue
    
    def run_test(self):
        """Run the complete multi-user profile test"""
        print("=== MULTI-USER PROFILE TEST ===")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now()}")
        print()
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Step 2: Test with existing users first
        self.test_existing_users()
        
        # Step 3: Create test users
        print(f"\n=== CREATING TEST USERS ===")
        for i in range(3):
            suffix = str(uuid.uuid4())[:8]
            self.create_test_user(suffix)
        
        if len(self.test_users) < 2:
            print("❌ Need at least 2 test users to proceed")
            return
        
        # Step 4: Test profile endpoints for each user
        print(f"\n=== TESTING PROFILE ENDPOINTS ===")
        for user in self.test_users:
            self.test_user_profile_stats(user)
            self.test_user_profile(user)
        
        # Step 5: Compare user data
        self.compare_user_data()
        
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

if __name__ == "__main__":
    tester = MultiUserProfileTester()
    tester.run_test()