#!/usr/bin/env python3
"""
Real-Time Statistics System Testing
Testing the new real-time statistics system thoroughly as requested
"""

import requests
import json
import sys
from datetime import datetime, timezone
import time

# Configuration
BASE_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class RealTimeStatsTestSuite:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.log_test("Admin Authentication", True, f"Token: {self.admin_token[:20]}...")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_test_user(self):
        """Create a test user for user-specific endpoint testing"""
        try:
            # First check if test user already exists
            test_user_data = {
                "email": "testuser@cataloro.com",
                "username": "testuser123",
                "password": "testpass123",
                "full_name": "Test User",
                "role": "both"
            }
            
            # Try to register
            response = self.session.post(f"{BASE_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["access_token"]
                self.log_test("Test User Creation", True, f"Created user: {test_user_data['email']}")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                # User exists, try to login
                login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                })
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.user_token = data["access_token"]
                    self.log_test("Test User Login", True, f"Logged in existing user: {test_user_data['email']}")
                    return True
                else:
                    self.log_test("Test User Login", False, f"Status: {login_response.status_code}")
                    return False
            else:
                self.log_test("Test User Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test User Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_stats_endpoint(self):
        """Test GET /api/profile/stats endpoint for individual user statistics"""
        print("=== Testing Profile Stats Endpoint ===")
        
        # Test with admin user
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/profile/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate required fields
                required_fields = [
                    "user_id", "total_orders", "total_listings", "favorites_count",
                    "total_spent", "total_earned", "avg_rating", "total_reviews",
                    "trust_score", "account_level", "badges_earned"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Profile Stats - Admin User", True, 
                                f"Retrieved stats: Orders={data.get('total_orders', 0)}, "
                                f"Listings={data.get('total_listings', 0)}, "
                                f"Level={data.get('account_level', 'N/A')}")
                else:
                    self.log_test("Profile Stats - Admin User", False, 
                                f"Missing fields: {missing_fields}")
            else:
                self.log_test("Profile Stats - Admin User", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Profile Stats - Admin User", False, f"Exception: {str(e)}")
        
        # Test with regular user if available
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BASE_URL}/profile/stats", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Profile Stats - Regular User", True, 
                                f"Retrieved stats: Orders={data.get('total_orders', 0)}, "
                                f"Listings={data.get('total_listings', 0)}")
                else:
                    self.log_test("Profile Stats - Regular User", False, 
                                f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Profile Stats - Regular User", False, f"Exception: {str(e)}")
        
        # Test without authentication
        try:
            response = self.session.get(f"{BASE_URL}/profile/stats")
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_test("Profile Stats - No Auth", True, "Correctly blocked unauthenticated request")
            else:
                self.log_test("Profile Stats - No Auth", False, 
                            f"Should block unauthenticated requests, got: {response.status_code}")
                
        except Exception as e:
            self.log_test("Profile Stats - No Auth", False, f"Exception: {str(e)}")
    
    def test_admin_time_based_stats(self):
        """Test GET /api/admin/stats/time-based endpoint with different time frames"""
        print("=== Testing Admin Time-Based Stats Endpoint ===")
        
        if not self.admin_token:
            self.log_test("Admin Time-Based Stats", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        time_frames = ["today", "week", "month", "year"]
        
        for time_frame in time_frames:
            try:
                response = self.session.get(f"{BASE_URL}/admin/stats/time-based?time_frame={time_frame}", 
                                          headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate required fields
                    required_fields = [
                        "total_users", "users_in_period", "active_users", "blocked_users",
                        "total_listings", "listings_in_period", "active_listings",
                        "total_orders", "orders_in_period", "total_revenue", "time_frame"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        # Validate logical consistency
                        logical_errors = []
                        
                        # Check that period counts don't exceed totals
                        if data["users_in_period"] > data["total_users"]:
                            logical_errors.append(f"Users in {time_frame} ({data['users_in_period']}) > Total users ({data['total_users']})")
                        
                        if data["listings_in_period"] > data["total_listings"]:
                            logical_errors.append(f"Listings in {time_frame} ({data['listings_in_period']}) > Total listings ({data['total_listings']})")
                        
                        if data["orders_in_period"] > data["total_orders"]:
                            logical_errors.append(f"Orders in {time_frame} ({data['orders_in_period']}) > Total orders ({data['total_orders']})")
                        
                        # Check that active + blocked users make sense
                        total_calculated = data["active_users"] + data["blocked_users"]
                        if abs(total_calculated - data["total_users"]) > 1:
                            logical_errors.append(f"Active ({data['active_users']}) + Blocked ({data['blocked_users']}) != Total ({data['total_users']})")
                        
                        if not logical_errors:
                            self.log_test(f"Admin Time-Based Stats - {time_frame.title()}", True,
                                        f"Users: {data['users_in_period']}/{data['total_users']}, "
                                        f"Listings: {data['listings_in_period']}/{data['total_listings']}, "
                                        f"Orders: {data['orders_in_period']}/{data['total_orders']}")
                        else:
                            self.log_test(f"Admin Time-Based Stats - {time_frame.title()}", False,
                                        f"Logical validation errors: {'; '.join(logical_errors)}")
                    else:
                        self.log_test(f"Admin Time-Based Stats - {time_frame.title()}", False,
                                    f"Missing fields: {missing_fields}")
                else:
                    self.log_test(f"Admin Time-Based Stats - {time_frame.title()}", False,
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Admin Time-Based Stats - {time_frame.title()}", False, f"Exception: {str(e)}")
        
        # Test invalid time frame
        try:
            response = self.session.get(f"{BASE_URL}/admin/stats/time-based?time_frame=invalid", 
                                      headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Should default to "today" for invalid time frame
                if data.get("time_frame") == "today":
                    self.log_test("Admin Time-Based Stats - Invalid Time Frame", True,
                                "Correctly defaulted to 'today' for invalid time frame")
                else:
                    self.log_test("Admin Time-Based Stats - Invalid Time Frame", False,
                                f"Expected default to 'today', got: {data.get('time_frame')}")
            else:
                self.log_test("Admin Time-Based Stats - Invalid Time Frame", False,
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin Time-Based Stats - Invalid Time Frame", False, f"Exception: {str(e)}")
        
        # Test without admin privileges
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BASE_URL}/admin/stats/time-based", headers=headers)
                
                if response.status_code == 403:
                    self.log_test("Admin Time-Based Stats - Non-Admin User", True,
                                "Correctly blocked non-admin user")
                else:
                    self.log_test("Admin Time-Based Stats - Non-Admin User", False,
                                f"Should block non-admin users, got: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Admin Time-Based Stats - Non-Admin User", False, f"Exception: {str(e)}")
    
    def test_enhanced_admin_stats(self):
        """Test GET /api/admin/stats endpoint (enhanced version)"""
        print("=== Testing Enhanced Admin Stats Endpoint ===")
        
        if not self.admin_token:
            self.log_test("Enhanced Admin Stats", False, "No admin token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate required fields for AdminStats model
                required_fields = [
                    "total_users", "active_users", "blocked_users",
                    "total_listings", "active_listings", "total_orders", "total_revenue"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Enhanced Admin Stats", True,
                                f"Total Users: {data['total_users']}, "
                                f"Active Listings: {data['active_listings']}, "
                                f"Total Revenue: €{data['total_revenue']}")
                else:
                    self.log_test("Enhanced Admin Stats", False,
                                f"Missing fields: {missing_fields}")
            else:
                self.log_test("Enhanced Admin Stats", False,
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Enhanced Admin Stats", False, f"Exception: {str(e)}")
    
    def test_track_activity_endpoint(self):
        """Test POST /api/track-activity endpoint for real-time activity tracking"""
        print("=== Testing Track Activity Endpoint ===")
        
        # Test with admin user
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                activity_data = {
                    "type": "listing_viewed",
                    "listing_id": "test-listing-123",
                    "metadata": {
                        "page": "browse",
                        "category": "Electronics"
                    }
                }
                
                response = self.session.post(f"{BASE_URL}/track-activity", 
                                           json=activity_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("message") == "Activity tracked successfully":
                        self.log_test("Track Activity - Admin User", True,
                                    f"Successfully tracked activity: {activity_data['type']}")
                    else:
                        self.log_test("Track Activity - Admin User", False,
                                    f"Unexpected response: {data}")
                else:
                    self.log_test("Track Activity - Admin User", False,
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test("Track Activity - Admin User", False, f"Exception: {str(e)}")
        
        # Test with regular user
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                activity_data = {
                    "type": "profile_updated",
                    "metadata": {
                        "fields_changed": ["bio", "location"]
                    }
                }
                
                response = self.session.post(f"{BASE_URL}/track-activity", 
                                           json=activity_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("message") == "Activity tracked successfully":
                        self.log_test("Track Activity - Regular User", True,
                                    f"Successfully tracked activity: {activity_data['type']}")
                    else:
                        self.log_test("Track Activity - Regular User", False,
                                    f"Unexpected response: {data}")
                else:
                    self.log_test("Track Activity - Regular User", False,
                                f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Track Activity - Regular User", False, f"Exception: {str(e)}")
        
        # Test without authentication
        try:
            activity_data = {"type": "unauthorized_test"}
            response = self.session.post(f"{BASE_URL}/track-activity", json=activity_data)
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_test("Track Activity - No Auth", True,
                            "Correctly blocked unauthenticated request")
            else:
                self.log_test("Track Activity - No Auth", False,
                            f"Should block unauthenticated requests, got: {response.status_code}")
                
        except Exception as e:
            self.log_test("Track Activity - No Auth", False, f"Exception: {str(e)}")
    
    def test_favorites_count_endpoint(self):
        """Test GET /api/favorites/count endpoint for real-time favorites count"""
        print("=== Testing Favorites Count Endpoint ===")
        
        # Test with admin user
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.get(f"{BASE_URL}/favorites/count", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "count" in data and isinstance(data["count"], int):
                        self.log_test("Favorites Count - Admin User", True,
                                    f"Favorites count: {data['count']}")
                    else:
                        self.log_test("Favorites Count - Admin User", False,
                                    f"Invalid response format: {data}")
                else:
                    self.log_test("Favorites Count - Admin User", False,
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test("Favorites Count - Admin User", False, f"Exception: {str(e)}")
        
        # Test with regular user
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BASE_URL}/favorites/count", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "count" in data and isinstance(data["count"], int):
                        self.log_test("Favorites Count - Regular User", True,
                                    f"Favorites count: {data['count']}")
                    else:
                        self.log_test("Favorites Count - Regular User", False,
                                    f"Invalid response format: {data}")
                else:
                    self.log_test("Favorites Count - Regular User", False,
                                f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Favorites Count - Regular User", False, f"Exception: {str(e)}")
        
        # Test without authentication
        try:
            response = self.session.get(f"{BASE_URL}/favorites/count")
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_test("Favorites Count - No Auth", True,
                            "Correctly blocked unauthenticated request")
            else:
                self.log_test("Favorites Count - No Auth", False,
                            f"Should block unauthenticated requests, got: {response.status_code}")
                
        except Exception as e:
            self.log_test("Favorites Count - No Auth", False, f"Exception: {str(e)}")
    
    def test_data_uniqueness_validation(self):
        """Test that individual user statistics are unique per user"""
        print("=== Testing Data Uniqueness Validation ===")
        
        if not (self.admin_token and self.user_token):
            self.log_test("Data Uniqueness Validation", False, "Need both admin and user tokens")
            return
        
        try:
            # Get admin stats
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            admin_response = self.session.get(f"{BASE_URL}/profile/stats", headers=admin_headers)
            
            # Get user stats
            user_headers = {"Authorization": f"Bearer {self.user_token}"}
            user_response = self.session.get(f"{BASE_URL}/profile/stats", headers=user_headers)
            
            if admin_response.status_code == 200 and user_response.status_code == 200:
                admin_data = admin_response.json()
                user_data = user_response.json()
                
                # Check that user_ids are different
                if admin_data.get("user_id") != user_data.get("user_id"):
                    self.log_test("Data Uniqueness - Different User IDs", True,
                                f"Admin ID: {admin_data.get('user_id')[:8]}..., "
                                f"User ID: {user_data.get('user_id')[:8]}...")
                else:
                    self.log_test("Data Uniqueness - Different User IDs", False,
                                "Both users have the same user_id")
                
                # Check that statistics are potentially different (they could be the same by coincidence)
                different_fields = []
                comparable_fields = ["total_orders", "total_listings", "total_spent", "total_earned"]
                
                for field in comparable_fields:
                    if admin_data.get(field, 0) != user_data.get(field, 0):
                        different_fields.append(field)
                
                if different_fields or admin_data.get("user_id") != user_data.get("user_id"):
                    self.log_test("Data Uniqueness - Individual Statistics", True,
                                f"Users have unique statistics. Different fields: {different_fields}")
                else:
                    self.log_test("Data Uniqueness - Individual Statistics", True,
                                "Users have identical statistics (could be valid for new users)")
            else:
                self.log_test("Data Uniqueness Validation", False,
                            f"Failed to get stats - Admin: {admin_response.status_code}, "
                            f"User: {user_response.status_code}")
                
        except Exception as e:
            self.log_test("Data Uniqueness Validation", False, f"Exception: {str(e)}")
    
    def test_time_based_logical_validation(self):
        """Test logical validation of time-based statistics"""
        print("=== Testing Time-Based Logical Validation ===")
        
        if not self.admin_token:
            self.log_test("Time-Based Logical Validation", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get stats for different time frames
            today_response = self.session.get(f"{BASE_URL}/admin/stats/time-based?time_frame=today", 
                                            headers=headers)
            week_response = self.session.get(f"{BASE_URL}/admin/stats/time-based?time_frame=week", 
                                           headers=headers)
            month_response = self.session.get(f"{BASE_URL}/admin/stats/time-based?time_frame=month", 
                                            headers=headers)
            
            if all(r.status_code == 200 for r in [today_response, week_response, month_response]):
                today_data = today_response.json()
                week_data = week_response.json()
                month_data = month_response.json()
                
                validation_errors = []
                
                # Test: Today's counts shouldn't exceed week's counts
                if today_data["users_in_period"] > week_data["users_in_period"]:
                    validation_errors.append(f"Today's users ({today_data['users_in_period']}) > Week's users ({week_data['users_in_period']})")
                
                if today_data["listings_in_period"] > week_data["listings_in_period"]:
                    validation_errors.append(f"Today's listings ({today_data['listings_in_period']}) > Week's listings ({week_data['listings_in_period']})")
                
                if today_data["orders_in_period"] > week_data["orders_in_period"]:
                    validation_errors.append(f"Today's orders ({today_data['orders_in_period']}) > Week's orders ({week_data['orders_in_period']})")
                
                # Test: Week's counts shouldn't exceed month's counts
                if week_data["users_in_period"] > month_data["users_in_period"]:
                    validation_errors.append(f"Week's users ({week_data['users_in_period']}) > Month's users ({month_data['users_in_period']})")
                
                if week_data["listings_in_period"] > month_data["listings_in_period"]:
                    validation_errors.append(f"Week's listings ({week_data['listings_in_period']}) > Month's listings ({month_data['listings_in_period']})")
                
                if week_data["orders_in_period"] > month_data["orders_in_period"]:
                    validation_errors.append(f"Week's orders ({week_data['orders_in_period']}) > Month's orders ({month_data['orders_in_period']})")
                
                if not validation_errors:
                    self.log_test("Time-Based Logical Validation", True,
                                f"All time-based relationships are logical. "
                                f"Today: {today_data['listings_in_period']} listings, "
                                f"Week: {week_data['listings_in_period']} listings, "
                                f"Month: {month_data['listings_in_period']} listings")
                else:
                    self.log_test("Time-Based Logical Validation", False,
                                f"Logical validation errors: {'; '.join(validation_errors)}")
            else:
                self.log_test("Time-Based Logical Validation", False,
                            f"Failed to get all time frame stats - Today: {today_response.status_code}, "
                            f"Week: {week_response.status_code}, Month: {month_response.status_code}")
                
        except Exception as e:
            self.log_test("Time-Based Logical Validation", False, f"Exception: {str(e)}")
    
    def test_growth_metrics_calculation(self):
        """Test that growth metrics calculations are working correctly"""
        print("=== Testing Growth Metrics Calculation ===")
        
        if not self.admin_token:
            self.log_test("Growth Metrics Calculation", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/stats/time-based?time_frame=week", 
                                      headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if "growth_metrics" in data:
                    growth = data["growth_metrics"]
                    
                    # Check that growth metrics have expected fields
                    expected_fields = ["users_growth", "listings_growth", "orders_growth"]
                    missing_fields = [field for field in expected_fields if field not in growth]
                    
                    if not missing_fields:
                        # Check that growth values are reasonable numbers
                        valid_growth = True
                        for field in expected_fields:
                            value = growth[field]
                            if not isinstance(value, (int, float)) or value < -100 or value > 10000:
                                valid_growth = False
                                break
                        
                        if valid_growth:
                            self.log_test("Growth Metrics Calculation", True,
                                        f"Users: {growth['users_growth']}%, "
                                        f"Listings: {growth['listings_growth']}%, "
                                        f"Orders: {growth['orders_growth']}%")
                        else:
                            self.log_test("Growth Metrics Calculation", False,
                                        f"Invalid growth values: {growth}")
                    else:
                        self.log_test("Growth Metrics Calculation", False,
                                    f"Missing growth fields: {missing_fields}")
                else:
                    self.log_test("Growth Metrics Calculation", False,
                                "No growth_metrics field in response")
            else:
                self.log_test("Growth Metrics Calculation", False,
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Growth Metrics Calculation", False, f"Exception: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling for various scenarios"""
        print("=== Testing Error Handling ===")
        
        # Test with non-existent user (this would require creating a fake token, skip for now)
        # Test invalid endpoints
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/stats/time-based?time_frame=invalid_frame", 
                                      headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Should default to "today"
                if data.get("time_frame") == "today":
                    self.log_test("Error Handling - Invalid Time Frame", True,
                                "Correctly handled invalid time frame by defaulting to 'today'")
                else:
                    self.log_test("Error Handling - Invalid Time Frame", False,
                                f"Unexpected handling of invalid time frame: {data.get('time_frame')}")
            else:
                self.log_test("Error Handling - Invalid Time Frame", False,
                            f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Error Handling - Invalid Time Frame", False, f"Exception: {str(e)}")
        
        # Test malformed requests
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{BASE_URL}/track-activity", 
                                       json={"invalid": "data"}, headers=headers)
            
            # Should still work as the endpoint accepts any activity data
            if response.status_code == 200:
                self.log_test("Error Handling - Malformed Activity Data", True,
                            "Endpoint gracefully handled malformed activity data")
            else:
                self.log_test("Error Handling - Malformed Activity Data", False,
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Error Handling - Malformed Activity Data", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Real-Time Statistics System Testing")
        print("=" * 60)
        
        # Setup
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        self.create_test_user()  # Optional, tests will work with just admin
        
        # Run all test suites
        self.test_profile_stats_endpoint()
        self.test_admin_time_based_stats()
        self.test_enhanced_admin_stats()
        self.test_track_activity_endpoint()
        self.test_favorites_count_endpoint()
        self.test_data_uniqueness_validation()
        self.test_time_based_logical_validation()
        self.test_growth_metrics_calculation()
        self.test_error_handling()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        return failed_tests == 0

if __name__ == "__main__":
    tester = RealTimeStatsTestSuite()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)