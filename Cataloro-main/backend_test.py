#!/usr/bin/env python3
"""
Cataloro Backend API Testing Suite
Tests core functionality after version update to 1.6.5
"""

import requests
import json
import sys
import time
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://dependency-fixer.preview.emergentagent.com/api"
TIMEOUT = 30

class CataloroAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.test_results = []
        self.auth_token = None
        self.test_user_data = {
            "email": f"testuser{uuid.uuid4().hex[:8]}@example.com",
            "username": f"testuser{uuid.uuid4().hex[:8]}",
            "password": "TestPassword123!",
            "full_name": "Test User",
            "role": "both"
        }
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_version_endpoint(self):
        """Test version endpoint returns 1.6.5"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if data.get("version") == "v1.6.5":
                    self.log_result("Version Endpoint", True, f"Version correctly shows v1.6.5", data)
                    return True
                else:
                    self.log_result("Version Endpoint", False, f"Expected v1.6.5, got {data.get('version')}", data)
                    return False
            else:
                self.log_result("Version Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Version Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_categories_endpoint(self):
        """Test categories endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/categories")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    expected_categories = ["Electronics", "Fashion", "Home & Garden", "Sports", "Books"]
                    found_categories = [cat for cat in expected_categories if cat in data]
                    if len(found_categories) >= 3:
                        self.log_result("Categories Endpoint", True, f"Categories loaded successfully: {len(data)} categories", data[:5])
                        return True
                    else:
                        self.log_result("Categories Endpoint", False, f"Expected categories missing. Found: {data}")
                        return False
                else:
                    self.log_result("Categories Endpoint", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("Categories Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Categories Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=self.test_user_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("User Registration", True, f"User registered successfully: {data['user']['username']}")
                    return True
                else:
                    self.log_result("User Registration", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("User Registration", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("User Registration", False, f"Request failed: {str(e)}")
            return False
    
    def test_user_login(self):
        """Test user login endpoint"""
        try:
            login_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("User Login", True, f"User logged in successfully: {data['user']['username']}")
                    return True
                else:
                    self.log_result("User Login", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("User Login", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("User Login", False, f"Request failed: {str(e)}")
            return False
    
    def test_protected_endpoint(self):
        """Test a protected endpoint with authentication"""
        if not self.auth_token:
            self.log_result("Protected Endpoint", False, "No auth token available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            response = self.session.get(f"{self.base_url}/listings/my-listings", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Protected Endpoint", True, f"Protected endpoint accessible, returned {len(data)} listings")
                return True
            else:
                self.log_result("Protected Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Protected Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_listings_endpoint(self):
        """Test listings endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/listings")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Listings Endpoint", True, f"Listings endpoint working, returned {len(data)} listings")
                    return True
                else:
                    self.log_result("Listings Endpoint", False, f"Invalid response format: {type(data)}")
                    return False
            else:
                self.log_result("Listings Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Listings Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_listings_count_endpoint(self):
        """Test listings count endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/listings/count")
            if response.status_code == 200:
                data = response.json()
                if "total_count" in data and isinstance(data["total_count"], int):
                    self.log_result("Listings Count Endpoint", True, f"Count endpoint working, total: {data['total_count']}")
                    return True
                else:
                    self.log_result("Listings Count Endpoint", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("Listings Count Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Listings Count Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity by checking if endpoints return data"""
        try:
            # Test multiple endpoints that require database access
            endpoints_to_test = [
                ("/listings", "listings data"),
                ("/categories", "categories data"),
                ("/listings/count", "count data")
            ]
            
            db_tests_passed = 0
            for endpoint, description in endpoints_to_test:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    if response.status_code == 200:
                        db_tests_passed += 1
                except:
                    pass
            
            if db_tests_passed >= 2:
                self.log_result("Database Connectivity", True, f"Database accessible - {db_tests_passed}/{len(endpoints_to_test)} endpoints working")
                return True
            else:
                self.log_result("Database Connectivity", False, f"Database issues - only {db_tests_passed}/{len(endpoints_to_test)} endpoints working")
                return False
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Database test failed: {str(e)}")
            return False
    
    def test_service_health(self):
        """Test overall service health and responsiveness"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/")
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 5.0:
                self.log_result("Service Health", True, f"Service responsive in {response_time:.2f}s")
                return True
            elif response.status_code == 200:
                self.log_result("Service Health", False, f"Service slow: {response_time:.2f}s response time")
                return False
            else:
                self.log_result("Service Health", False, f"Service unhealthy: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Service Health", False, f"Service unreachable: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting Cataloro Backend API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print(f"⏰ Started at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Core service tests
        tests = [
            ("Service Health Check", self.test_service_health),
            ("Version Endpoint", self.test_version_endpoint),
            ("Database Connectivity", self.test_database_connectivity),
            ("Categories Endpoint", self.test_categories_endpoint),
            ("Listings Endpoint", self.test_listings_endpoint),
            ("Listings Count Endpoint", self.test_listings_count_endpoint),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Protected Endpoint Access", self.test_protected_endpoint),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
            
            # Small delay between tests
            time.sleep(0.5)
        
        print("=" * 60)
        print(f"📊 Test Results Summary:")
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed_tests, total_tests, self.test_results

def main():
    """Main test execution"""
    tester = CataloroAPITester()
    passed, total, results = tester.run_all_tests()
    
    # Write results to file
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "total": total,
                "success_rate": (passed/total)*100,
                "timestamp": datetime.now().isoformat()
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: /app/backend_test_results.json")
    
    # Exit with appropriate code
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"⚠️  {total - passed} tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()