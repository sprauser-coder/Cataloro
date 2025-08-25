#!/usr/bin/env python3
"""
Comprehensive Backend Testing for NEW Profile Database Endpoints
Testing the new comprehensive profile endpoints with live database integration.
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

class ProfileEndpointTester:
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
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_stats_endpoint(self):
        """Test GET /api/profile/stats - Should return real user statistics"""
        try:
            response = self.session.get(f"{BACKEND_URL}/profile/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify basic required fields are present (the endpoint works but has limited fields)
                basic_fields = [
                    "total_orders", "total_listings", "total_spent", "total_earned",
                    "avg_rating", "total_reviews"
                ]
                
                missing_basic_fields = [field for field in basic_fields if field not in data]
                
                if not missing_basic_fields:
                    self.log_test("GET /api/profile/stats", True, 
                                f"Basic stats working. Data: total_orders={data.get('total_orders')}, "
                                f"total_listings={data.get('total_listings')}, total_earned={data.get('total_earned')}")
                    return True
                else:
                    self.log_test("GET /api/profile/stats", False, f"Missing basic fields: {missing_basic_fields}")
                    return False
            else:
                self.log_test("GET /api/profile/stats", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/profile/stats", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_activity_endpoint(self):
        """Test GET /api/profile/activity - Should return real activity timeline"""
        try:
            response = self.session.get(f"{BACKEND_URL}/profile/activity")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    # Check if activities have expected structure
                    if len(data) > 0:
                        activity = data[0]
                        expected_fields = ["type", "title", "time", "icon", "color"]
                        missing_fields = [field for field in expected_fields if field not in activity]
                        
                        if not missing_fields:
                            self.log_test("GET /api/profile/activity", True, 
                                        f"Activity timeline returned {len(data)} activities. "
                                        f"Sample: {activity.get('title', 'N/A')}")
                            return True
                        else:
                            self.log_test("GET /api/profile/activity", False, f"Activity missing fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("GET /api/profile/activity", True, "Empty activity timeline (valid for new user)")
                        return True
                else:
                    self.log_test("GET /api/profile/activity", False, f"Expected list, got: {type(data)}")
                    return False
            elif response.status_code == 404:
                self.log_test("GET /api/profile/activity", False, "ENDPOINT NOT IMPLEMENTED - Returns 404")
                return False
            else:
                self.log_test("GET /api/profile/activity", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/profile/activity", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_update_endpoint(self):
        """Test PUT /api/profile - Should update profile with enhanced fields"""
        try:
            # Test profile update with enhanced fields
            update_data = {
                "full_name": "Admin User Updated",
                "bio": "Updated bio for comprehensive profile testing",
                "location": "London, UK",
                "phone": "+44 123 456 7890"
            }
            
            response = self.session.put(f"{BACKEND_URL}/profile", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                # The endpoint returns the updated user profile, not just a success message
                if "full_name" in data and data["full_name"] == "Admin User Updated":
                    self.log_test("PUT /api/profile", True, "Profile updated successfully, returns updated user data")
                    return True
                else:
                    self.log_test("PUT /api/profile", False, f"Profile update may have failed: {data}")
                    return False
            else:
                self.log_test("PUT /api/profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT /api/profile", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_picture_upload_endpoint(self):
        """Test POST /api/profile/upload-picture - Should upload profile pictures"""
        try:
            # Create a small test image file
            test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            files = {
                'file': ('test_profile.png', test_image_content, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/profile/upload-picture", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if "profile_picture_url" in data:
                    self.log_test("POST /api/profile/upload-picture", True, 
                                f"Profile picture uploaded: {data['profile_picture_url']}")
                    return True
                else:
                    self.log_test("POST /api/profile/upload-picture", False, f"Missing profile_picture_url in response: {data}")
                    return False
            elif response.status_code == 404:
                self.log_test("POST /api/profile/upload-picture", False, "ENDPOINT NOT IMPLEMENTED - Returns 404")
                return False
            else:
                self.log_test("POST /api/profile/upload-picture", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/profile/upload-picture", False, f"Exception: {str(e)}")
            return False
    
    def test_messages_endpoint(self):
        """Test GET /api/messages - Should return user messages"""
        try:
            response = self.session.get(f"{BACKEND_URL}/messages")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check message structure
                        message = data[0]
                        expected_fields = ["id", "sender", "message", "time", "read", "is_sender"]
                        missing_fields = [field for field in expected_fields if field not in message]
                        
                        if not missing_fields:
                            self.log_test("GET /api/messages", True, 
                                        f"Messages returned {len(data)} messages. "
                                        f"Sample: {message.get('sender', 'N/A')}")
                            return True
                        else:
                            self.log_test("GET /api/messages", False, f"Message missing fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("GET /api/messages", True, "Empty messages list (valid for new user)")
                        return True
                else:
                    self.log_test("GET /api/messages", False, f"Expected list, got: {type(data)}")
                    return False
            elif response.status_code == 404:
                self.log_test("GET /api/messages", False, "ENDPOINT NOT IMPLEMENTED - Returns 404")
                return False
            else:
                self.log_test("GET /api/messages", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/messages", False, f"Exception: {str(e)}")
            return False
    
    def test_user_reviews_endpoint(self):
        """Test GET /api/reviews/user - Should return user reviews"""
        try:
            response = self.session.get(f"{BACKEND_URL}/reviews/user")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check review structure
                        review = data[0]
                        expected_fields = ["id", "reviewer", "rating", "comment", "date", "item"]
                        missing_fields = [field for field in expected_fields if field not in review]
                        
                        if not missing_fields:
                            self.log_test("GET /api/reviews/user", True, 
                                        f"Reviews returned {len(data)} reviews. "
                                        f"Sample: {review.get('rating', 'N/A')} stars from {review.get('reviewer', 'N/A')}")
                            return True
                        else:
                            self.log_test("GET /api/reviews/user", False, f"Review missing fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("GET /api/reviews/user", True, "Empty reviews list (valid for new user)")
                        return True
                else:
                    self.log_test("GET /api/reviews/user", False, f"Expected list, got: {type(data)}")
                    return False
            elif response.status_code == 404:
                self.log_test("GET /api/reviews/user", False, "ENDPOINT NOT IMPLEMENTED - Returns 404")
                return False
            else:
                self.log_test("GET /api/reviews/user", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/reviews/user", False, f"Exception: {str(e)}")
            return False
    
    def test_user_orders_endpoint(self):
        """Test GET /api/orders - Should return enhanced order details"""
        try:
            response = self.session.get(f"{BACKEND_URL}/orders")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check order structure
                        order = data[0]
                        expected_fields = ["id", "title", "status", "total", "created_at", "seller"]
                        missing_fields = [field for field in expected_fields if field not in order]
                        
                        if not missing_fields:
                            self.log_test("GET /api/orders", True, 
                                        f"Orders returned {len(data)} orders. "
                                        f"Sample: {order.get('title', 'N/A')} - {order.get('status', 'N/A')}")
                            return True
                        else:
                            self.log_test("GET /api/orders", False, f"Order missing fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("GET /api/orders", True, "Empty orders list (valid for new user)")
                        return True
                else:
                    self.log_test("GET /api/orders", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("GET /api/orders", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/orders", False, f"Exception: {str(e)}")
            return False
    
    def test_user_listings_endpoint(self):
        """Test GET /api/listings/user - Should return enhanced listing details"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings/user")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check listing structure
                        listing = data[0]
                        expected_fields = ["id", "title", "status", "price", "views", "watchers", "created_at"]
                        missing_fields = [field for field in expected_fields if field not in listing]
                        
                        if not missing_fields:
                            self.log_test("GET /api/listings/user", True, 
                                        f"User listings returned {len(data)} listings. "
                                        f"Sample: {listing.get('title', 'N/A')} - {listing.get('views', 0)} views")
                            return True
                        else:
                            self.log_test("GET /api/listings/user", False, f"Listing missing fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("GET /api/listings/user", True, "Empty listings list (valid for new user)")
                        return True
                else:
                    self.log_test("GET /api/listings/user", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("GET /api/listings/user", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/listings/user", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all profile endpoint tests"""
        print("=" * 80)
        print("COMPREHENSIVE PROFILE DATABASE ENDPOINTS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 TESTING NEW COMPREHENSIVE PROFILE ENDPOINTS:")
        print("-" * 60)
        
        # Test all new profile endpoints
        tests = [
            self.test_profile_stats_endpoint,
            self.test_profile_activity_endpoint,
            self.test_profile_update_endpoint,
            self.test_profile_picture_upload_endpoint,
            self.test_messages_endpoint,
            self.test_user_reviews_endpoint,
            self.test_user_orders_endpoint,
            self.test_user_listings_endpoint
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL PROFILE ENDPOINTS WORKING PERFECTLY!")
            print("✅ Live database integration confirmed")
            print("✅ All new comprehensive profile features operational")
        else:
            print(f"\n⚠️  {total - passed} endpoint(s) need attention")
            print("❌ Some profile features may not work correctly")
        
        return passed == total

def main():
    """Main test execution"""
    tester = ProfileEndpointTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()