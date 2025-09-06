#!/usr/bin/env python3
"""
Cataloro Marketplace Backend API Testing Suite
Comprehensive testing of all backend endpoints for functionality verification
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://cataloro-ads.preview.emergentagent.com/api"
TEST_USER_EMAIL = "test_user@cataloro.com"
TEST_ADMIN_EMAIL = "admin@cataloro.com"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_user_id = None
        self.admin_user_id = None
        self.test_listing_id = None
        self.test_tender_id = None
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }

    def log_test(self, test_name, status, details=""):
        """Log test results"""
        self.results["total_tests"] += 1
        if status == "PASS":
            self.results["passed_tests"] += 1
            print(f"✅ {test_name}: PASSED")
        else:
            self.results["failed_tests"] += 1
            print(f"❌ {test_name}: FAILED - {details}")
        
        self.results["test_details"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_health_check(self):
        """Test basic API health check"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", "PASS")
                    return True
                else:
                    self.log_test("Health Check", "FAIL", f"Unexpected response: {data}")
            else:
                self.log_test("Health Check", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", "FAIL", str(e))
        return False

    def test_authentication_endpoints(self):
        """Test authentication system"""
        # Test user login/registration
        try:
            # Test login (creates user if not exists)
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": "test123"
            }
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.test_user_id = data["user"]["id"]
                    self.log_test("User Authentication", "PASS")
                else:
                    self.log_test("User Authentication", "FAIL", "Missing user or token in response")
                    return False
            else:
                self.log_test("User Authentication", "FAIL", f"Status code: {response.status_code}")
                return False

            # Test admin login
            admin_login_data = {
                "email": TEST_ADMIN_EMAIL,
                "password": "admin123"
            }
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=admin_login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and data["user"]["role"] == "admin":
                    self.admin_user_id = data["user"]["id"]
                    self.log_test("Admin Authentication", "PASS")
                else:
                    self.log_test("Admin Authentication", "FAIL", "User is not admin")
                    return False
            else:
                self.log_test("Admin Authentication", "FAIL", f"Status code: {response.status_code}")
                return False

            # Test profile retrieval
            if self.test_user_id:
                response = self.session.get(f"{BACKEND_URL}/auth/profile/{self.test_user_id}")
                if response.status_code == 200:
                    self.log_test("Profile Retrieval", "PASS")
                else:
                    self.log_test("Profile Retrieval", "FAIL", f"Status code: {response.status_code}")

            return True

        except Exception as e:
            self.log_test("Authentication Endpoints", "FAIL", str(e))
            return False

    def test_marketplace_endpoints(self):
        """Test marketplace browsing and listing endpoints"""
        try:
            # Test browse listings
            response = self.session.get(f"{BACKEND_URL}/marketplace/browse")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Browse Listings", "PASS", f"Found {len(data)} listings")
                else:
                    self.log_test("Browse Listings", "FAIL", "Response is not a list")
            else:
                self.log_test("Browse Listings", "FAIL", f"Status code: {response.status_code}")

            # Test browse with filters
            response = self.session.get(f"{BACKEND_URL}/marketplace/browse?type=all&price_from=0&price_to=1000")
            if response.status_code == 200:
                self.log_test("Browse with Filters", "PASS")
            else:
                self.log_test("Browse with Filters", "FAIL", f"Status code: {response.status_code}")

            # Test price range settings
            response = self.session.get(f"{BACKEND_URL}/marketplace/price-range-settings")
            if response.status_code == 200:
                data = response.json()
                if "price_range_min_percent" in data and "price_range_max_percent" in data:
                    self.log_test("Price Range Settings", "PASS")
                else:
                    self.log_test("Price Range Settings", "FAIL", "Missing price range fields")
            else:
                self.log_test("Price Range Settings", "FAIL", f"Status code: {response.status_code}")

            return True

        except Exception as e:
            self.log_test("Marketplace Endpoints", "FAIL", str(e))
            return False

    def test_listing_management(self):
        """Test listing creation, retrieval, and management"""
        if not self.test_user_id:
            self.log_test("Listing Management", "FAIL", "No test user ID available")
            return False

        try:
            # Create a test listing
            listing_data = {
                "title": f"Test Listing {int(time.time())}",
                "description": "Test listing for API verification",
                "price": 100.0,
                "category": "Electronics",
                "condition": "New",
                "seller_id": self.test_user_id,
                "images": [],
                "tags": ["test"],
                "features": ["API Test"],
                "has_time_limit": True,
                "time_limit_hours": 24
            }

            response = self.session.post(f"{BACKEND_URL}/listings", json=listing_data)
            if response.status_code == 200:
                data = response.json()
                if "listing_id" in data:
                    self.test_listing_id = data["listing_id"]
                    self.log_test("Create Listing", "PASS")
                else:
                    self.log_test("Create Listing", "FAIL", "No listing_id in response")
                    return False
            else:
                self.log_test("Create Listing", "FAIL", f"Status code: {response.status_code}")
                return False

            # Test retrieve listing
            if self.test_listing_id:
                response = self.session.get(f"{BACKEND_URL}/listings/{self.test_listing_id}")
                if response.status_code == 200:
                    self.log_test("Retrieve Listing", "PASS")
                else:
                    self.log_test("Retrieve Listing", "FAIL", f"Status code: {response.status_code}")

            # Test my listings
            response = self.session.get(f"{BACKEND_URL}/user/my-listings/{self.test_user_id}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("My Listings", "PASS", f"Found {len(data)} user listings")
                else:
                    self.log_test("My Listings", "FAIL", "Response is not a list")
            else:
                self.log_test("My Listings", "FAIL", f"Status code: {response.status_code}")

            # Test time limit functionality
            if self.test_listing_id:
                extension_data = {"additional_hours": 6}
                response = self.session.post(f"{BACKEND_URL}/listings/{self.test_listing_id}/extend-time", json=extension_data)
                if response.status_code == 200:
                    self.log_test("Time Extension", "PASS")
                else:
                    self.log_test("Time Extension", "FAIL", f"Status code: {response.status_code}")

                # Test expiration check
                response = self.session.post(f"{BACKEND_URL}/listings/{self.test_listing_id}/check-expiration")
                if response.status_code == 200:
                    self.log_test("Expiration Check", "PASS")
                else:
                    self.log_test("Expiration Check", "FAIL", f"Status code: {response.status_code}")

            return True

        except Exception as e:
            self.log_test("Listing Management", "FAIL", str(e))
            return False

    def test_tender_system(self):
        """Test tender/bidding system"""
        if not self.test_user_id or not self.test_listing_id:
            self.log_test("Tender System", "FAIL", "Missing test user ID or listing ID")
            return False

        try:
            # Create a second user for bidding
            bidder_login_data = {
                "email": "bidder@cataloro.com",
                "password": "bidder123"
            }
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=bidder_login_data)
            
            if response.status_code == 200:
                bidder_data = response.json()
                bidder_id = bidder_data["user"]["id"]
                
                # Submit a tender
                tender_data = {
                    "listing_id": self.test_listing_id,
                    "buyer_id": bidder_id,
                    "offer_amount": 120.0,
                    "message": "Test tender offer"
                }
                
                response = self.session.post(f"{BACKEND_URL}/tenders/submit", json=tender_data)
                if response.status_code == 200:
                    data = response.json()
                    if "tender_id" in data:
                        self.test_tender_id = data["tender_id"]
                        self.log_test("Submit Tender", "PASS")
                    else:
                        self.log_test("Submit Tender", "FAIL", "No tender_id in response")
                        return False
                else:
                    self.log_test("Submit Tender", "FAIL", f"Status code: {response.status_code}")
                    return False

                # Test seller tender overview
                response = self.session.get(f"{BACKEND_URL}/tenders/seller/{self.test_user_id}/overview")
                if response.status_code == 200:
                    self.log_test("Seller Tender Overview", "PASS")
                else:
                    self.log_test("Seller Tender Overview", "FAIL", f"Status code: {response.status_code}")

                # Test buyer tenders
                response = self.session.get(f"{BACKEND_URL}/tenders/buyer/{bidder_id}")
                if response.status_code == 200:
                    self.log_test("Buyer Tenders", "PASS")
                else:
                    self.log_test("Buyer Tenders", "FAIL", f"Status code: {response.status_code}")

                # Test listing tenders
                response = self.session.get(f"{BACKEND_URL}/tenders/listing/{self.test_listing_id}")
                if response.status_code == 200:
                    self.log_test("Listing Tenders", "PASS")
                else:
                    self.log_test("Listing Tenders", "FAIL", f"Status code: {response.status_code}")

            return True

        except Exception as e:
            self.log_test("Tender System", "FAIL", str(e))
            return False

    def test_messaging_endpoints(self):
        """Test messaging system"""
        if not self.test_user_id:
            self.log_test("Messaging System", "FAIL", "No test user ID available")
            return False

        try:
            # Test get messages
            response = self.session.get(f"{BACKEND_URL}/user/{self.test_user_id}/messages")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Messages", "PASS", f"Found {len(data)} messages")
                else:
                    self.log_test("Get Messages", "FAIL", "Response is not a list")
            else:
                self.log_test("Get Messages", "FAIL", f"Status code: {response.status_code}")

            # Test notifications
            response = self.session.get(f"{BACKEND_URL}/user/notifications/{self.test_user_id}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Notifications", "PASS", f"Found {len(data)} notifications")
                else:
                    self.log_test("Get Notifications", "FAIL", "Response is not a list")
            else:
                self.log_test("Get Notifications", "FAIL", f"Status code: {response.status_code}")

            return True

        except Exception as e:
            self.log_test("Messaging Endpoints", "FAIL", str(e))
            return False

    def test_admin_endpoints(self):
        """Test admin panel endpoints"""
        if not self.admin_user_id:
            self.log_test("Admin Endpoints", "FAIL", "No admin user ID available")
            return False

        try:
            # Test admin dashboard
            response = self.session.get(f"{BACKEND_URL}/admin/dashboard")
            if response.status_code == 200:
                data = response.json()
                if "kpis" in data:
                    self.log_test("Admin Dashboard", "PASS")
                else:
                    self.log_test("Admin Dashboard", "FAIL", "Missing KPIs in response")
            else:
                self.log_test("Admin Dashboard", "FAIL", f"Status code: {response.status_code}")

            # Test admin users
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Admin Users", "PASS", f"Found {len(data)} users")
                else:
                    self.log_test("Admin Users", "FAIL", "Response is not a list")
            else:
                self.log_test("Admin Users", "FAIL", f"Status code: {response.status_code}")

            # Test admin settings
            response = self.session.get(f"{BACKEND_URL}/admin/settings")
            if response.status_code == 200:
                data = response.json()
                if "site_name" in data:
                    self.log_test("Admin Settings", "PASS")
                else:
                    self.log_test("Admin Settings", "FAIL", "Missing site_name in response")
            else:
                self.log_test("Admin Settings", "FAIL", f"Status code: {response.status_code}")

            # Test catalyst price settings
            response = self.session.get(f"{BACKEND_URL}/admin/catalyst/price-settings")
            if response.status_code == 200:
                data = response.json()
                if "pt_price" in data and "pd_price" in data and "rh_price" in data:
                    self.log_test("Catalyst Price Settings", "PASS")
                else:
                    self.log_test("Catalyst Price Settings", "FAIL", "Missing price fields")
            else:
                self.log_test("Catalyst Price Settings", "FAIL", f"Status code: {response.status_code}")

            # Test content management
            response = self.session.get(f"{BACKEND_URL}/admin/content")
            if response.status_code == 200:
                data = response.json()
                if "hero" in data:
                    self.log_test("Admin Content", "PASS")
                else:
                    self.log_test("Admin Content", "FAIL", "Missing hero section")
            else:
                self.log_test("Admin Content", "FAIL", f"Status code: {response.status_code}")

            return True

        except Exception as e:
            self.log_test("Admin Endpoints", "FAIL", str(e))
            return False

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        try:
            # Delete test listing if created
            if self.test_listing_id:
                response = self.session.delete(f"{BACKEND_URL}/listings/{self.test_listing_id}")
                if response.status_code == 200:
                    self.log_test("Cleanup Test Listing", "PASS")
                else:
                    self.log_test("Cleanup Test Listing", "FAIL", f"Status code: {response.status_code}")

        except Exception as e:
            self.log_test("Cleanup", "FAIL", str(e))

    def run_all_tests(self):
        """Run comprehensive backend API tests"""
        print("🚀 Starting Cataloro Marketplace Backend API Testing Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        test_categories = [
            ("Basic Connectivity", self.test_health_check),
            ("Authentication System", self.test_authentication_endpoints),
            ("Marketplace Endpoints", self.test_marketplace_endpoints),
            ("Listing Management", self.test_listing_management),
            ("Tender System", self.test_tender_system),
            ("Messaging System", self.test_messaging_endpoints),
            ("Admin Panel", self.test_admin_endpoints)
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n📋 Testing {category_name}...")
            test_function()
        
        # Cleanup
        print(f"\n🧹 Cleaning up test data...")
        self.cleanup_test_data()
        
        # Generate summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']} ✅")
        print(f"Failed: {self.results['failed_tests']} ❌")
        print(f"Success Rate: {(self.results['passed_tests']/self.results['total_tests']*100):.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if self.results['failed_tests'] > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.results['test_details']:
                if test['status'] == 'FAIL':
                    print(f"  - {test['test']}: {test['details']}")
        
        # Overall status
        if self.results['failed_tests'] == 0:
            print("\n🎉 ALL TESTS PASSED - Backend is fully operational!")
            return True
        else:
            print(f"\n⚠️  {self.results['failed_tests']} tests failed - Backend needs attention")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(tester.results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
    
    # Exit with appropriate code
    exit(0 if success else 1)