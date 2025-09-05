#!/usr/bin/env python3
"""
Extended Cataloro Marketplace Backend API Test Suite
Tests additional CRUD operations, edge cases, and error handling
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class ExtendedCataloroAPITester:
    def __init__(self, base_url="https://cataloro-marketplace-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_id = None

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

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration with real data"""
        test_email = f"testuser_{uuid.uuid4().hex[:8]}@cataloro.com"
        success, response = self.run_test(
            "User Registration",
            "POST",
            "api/auth/register",
            200,
            data={
                "username": "sarah_johnson",
                "email": test_email,
                "full_name": "Sarah Johnson"
            }
        )
        if success and 'user_id' in response:
            self.test_user_id = response['user_id']
            print(f"   Created user ID: {self.test_user_id}")
        return success

    def test_duplicate_registration(self):
        """Test duplicate email registration (should fail)"""
        success, response = self.run_test(
            "Duplicate Registration (Should Fail)",
            "POST",
            "api/auth/register",
            400,  # Should return 400 for duplicate email
            data={
                "username": "duplicate_user",
                "email": "admin@cataloro.com",  # Already exists
                "full_name": "Duplicate User"
            }
        )
        return success

    def test_invalid_profile_lookup(self):
        """Test profile lookup with invalid user ID"""
        success, response = self.run_test(
            "Invalid Profile Lookup (Should Fail)",
            "GET",
            "api/auth/profile/invalid_user_id_12345",
            404  # Should return 404 for non-existent user
        )
        return success

    def test_marketplace_with_real_data(self):
        """Test marketplace browse with verification of real data structure"""
        success, response = self.run_test(
            "Marketplace Browse - Data Structure Validation",
            "GET",
            "api/marketplace/browse",
            200
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            # Validate data structure
            listing = response[0]
            required_fields = ['id', 'title', 'description', 'price', 'category', 'seller_id', 'status']
            missing_fields = [field for field in required_fields if field not in listing]
            
            if not missing_fields:
                print(f"   ✅ Data structure valid - all required fields present")
                print(f"   📊 Found {len(response)} listings with proper structure")
                return True
            else:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
        
        return success

    def test_admin_user_update(self):
        """Test admin user update functionality"""
        if not self.test_user_id:
            print("❌ Admin User Update - SKIPPED (No test user created)")
            return False
            
        success, response = self.run_test(
            "Admin User Update",
            "PUT",
            f"api/admin/users/{self.test_user_id}",
            200,
            data={
                "full_name": "Sarah Johnson Updated",
                "is_active": True
            }
        )
        return success

    def test_database_persistence(self):
        """Test that data persists across requests"""
        if not self.test_user_id:
            print("❌ Database Persistence - SKIPPED (No test user created)")
            return False
            
        # First, get the user profile
        success1, response1 = self.run_test(
            "Database Persistence - Profile Retrieval",
            "GET",
            f"api/auth/profile/{self.test_user_id}",
            200
        )
        
        if success1:
            # Verify the updated data is persisted
            if response1.get('full_name') == 'Sarah Johnson Updated':
                print(f"   ✅ Data persistence verified - updated name found")
                return True
            else:
                print(f"   ❌ Data persistence failed - expected 'Sarah Johnson Updated', got '{response1.get('full_name')}'")
                return False
        
        return False

    def test_cors_headers(self):
        """Test CORS configuration"""
        url = f"{self.base_url}/api/health"
        
        try:
            # Test OPTIONS request for CORS preflight
            response = self.session.options(url)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            print(f"\n🔍 Testing CORS Configuration...")
            print(f"   CORS Headers: {cors_headers}")
            
            # Check if basic CORS headers are present
            has_cors = any(header for header in cors_headers.values() if header)
            
            if has_cors:
                self.log_test("CORS Configuration", True, f"CORS headers present")
                return True
            else:
                self.log_test("CORS Configuration", False, f"No CORS headers found")
                return False
                
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Error: {str(e)}")
            return False

    def run_extended_tests(self):
        """Run extended test suite"""
        print("🚀 Starting Extended Cataloro Marketplace API Tests")
        print("=" * 70)

        # Test user registration and CRUD operations
        self.test_user_registration()
        self.test_duplicate_registration()
        
        # Test error handling
        self.test_invalid_profile_lookup()
        
        # Test data structure and persistence
        self.test_marketplace_with_real_data()
        
        # Test admin operations
        self.test_admin_user_update()
        self.test_database_persistence()
        
        # Test infrastructure
        self.test_cors_headers()

        # Print results
        print("\n" + "=" * 70)
        print(f"📊 Extended Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All extended tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} extended tests failed")
            return False

def main():
    """Main test execution"""
    tester = ExtendedCataloroAPITester()
    success = tester.run_extended_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())