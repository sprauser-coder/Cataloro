#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Username Availability Check Focus
Comprehensive testing of the /api/auth/check-username/{username} endpoint
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class UsernameAvailabilityTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.created_users = []  # Track users created for testing
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def create_test_user(self, username, email):
        """Create a test user for availability testing"""
        try:
            user_data = {
                "username": username,
                "email": email,
                "password": "TestPassword123!",
                "role": "user",
                "full_name": f"Test User {username}"
            }
            
            response = requests.post(f"{BACKEND_URL}/admin/users", json=user_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('user', {}).get('id')
                if user_id:
                    self.created_users.append(user_id)
                return True, user_id
            else:
                return False, response.json().get('detail', 'Unknown error')
        except Exception as e:
            return False, str(e)

    def test_available_username(self):
        """Test username availability check with available username"""
        try:
            # Generate a unique username that should be available
            test_username = f"available_user_{str(uuid.uuid4())[:8]}"
            
            response = requests.get(f"{BACKEND_URL}/auth/check-username/{test_username}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                available = data.get('available', False)
                
                if available:
                    self.log_test(
                        "Available Username Check", 
                        True, 
                        f"Username '{test_username}' correctly reported as available"
                    )
                    return True
                else:
                    reason = data.get('reason', 'No reason provided')
                    self.log_test(
                        "Available Username Check", 
                        False, 
                        f"Username '{test_username}' incorrectly reported as unavailable: {reason}"
                    )
                    return False
            else:
                self.log_test("Available Username Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Available Username Check", False, error_msg=str(e))
            return False

    def test_existing_username(self):
        """Test username availability check with existing username"""
        try:
            # First create a test user
            test_username = f"existing_user_{str(uuid.uuid4())[:8]}"
            test_email = f"{test_username}@example.com"
            
            created, result = self.create_test_user(test_username, test_email)
            if not created:
                self.log_test("Existing Username Check - Setup", False, f"Failed to create test user: {result}")
                return False
            
            # Now check if the username is reported as unavailable
            response = requests.get(f"{BACKEND_URL}/auth/check-username/{test_username}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                available = data.get('available', True)
                reason = data.get('reason', '')
                
                if not available and "already taken" in reason.lower():
                    self.log_test(
                        "Existing Username Check", 
                        True, 
                        f"Username '{test_username}' correctly reported as unavailable: {reason}"
                    )
                    return True
                else:
                    self.log_test(
                        "Existing Username Check", 
                        False, 
                        f"Username '{test_username}' incorrectly reported as available: {available}"
                    )
                    return False
            else:
                self.log_test("Existing Username Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Existing Username Check", False, error_msg=str(e))
            return False

    def test_case_sensitivity(self):
        """Test case-insensitive username checking"""
        try:
            # Create a user with lowercase username
            test_username_lower = f"casetest_{str(uuid.uuid4())[:8]}".lower()
            test_email = f"{test_username_lower}@example.com"
            
            created, result = self.create_test_user(test_username_lower, test_email)
            if not created:
                self.log_test("Case Sensitivity Test - Setup", False, f"Failed to create test user: {result}")
                return False
            
            # Test with uppercase version
            test_username_upper = test_username_lower.upper()
            response = requests.get(f"{BACKEND_URL}/auth/check-username/{test_username_upper}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                available = data.get('available', True)
                
                if not available:
                    self.log_test(
                        "Case Sensitivity Test", 
                        True, 
                        f"Case-insensitive matching works: '{test_username_upper}' correctly reported as unavailable"
                    )
                    return True
                else:
                    self.log_test(
                        "Case Sensitivity Test", 
                        False, 
                        f"Case-insensitive matching failed: '{test_username_upper}' reported as available when '{test_username_lower}' exists"
                    )
                    return False
            else:
                self.log_test("Case Sensitivity Test", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Case Sensitivity Test", False, error_msg=str(e))
            return False

    def test_invalid_usernames(self):
        """Test validation of invalid usernames"""
        invalid_cases = [
            ("", "Empty username"),
            ("ab", "Too short (2 characters)"),
            ("a" * 51, "Too long (51 characters)"),
            ("user@name", "Contains @ symbol"),
            ("user name", "Contains space"),
            ("user#name", "Contains # symbol"),
            ("user$name", "Contains $ symbol"),
            ("user%name", "Contains % symbol")
        ]
        
        passed_validations = 0
        total_validations = len(invalid_cases)
        
        for username, description in invalid_cases:
            try:
                response = requests.get(f"{BACKEND_URL}/auth/check-username/{username}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    available = data.get('available', True)
                    reason = data.get('reason', '')
                    
                    if not available and reason:
                        passed_validations += 1
                        print(f"   ✅ {description}: Correctly rejected - {reason}")
                    else:
                        print(f"   ❌ {description}: Incorrectly accepted")
                else:
                    print(f"   ❌ {description}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {description}: Error - {str(e)}")
        
        success = passed_validations == total_validations
        self.log_test(
            "Invalid Username Validation", 
            success, 
            f"Passed {passed_validations}/{total_validations} validation tests"
        )
        return success

    def test_valid_username_formats(self):
        """Test valid username formats are accepted"""
        valid_cases = [
            f"user_{str(uuid.uuid4())[:8]}",  # With underscore
            f"user.{str(uuid.uuid4())[:8]}",  # With dot
            f"user-{str(uuid.uuid4())[:8]}",  # With hyphen
            f"User{str(uuid.uuid4())[:8]}",   # Mixed case
            f"123user{str(uuid.uuid4())[:8]}", # Starting with number
            "abc",  # Minimum length (3 characters)
            "a" * 50  # Maximum length (50 characters)
        ]
        
        passed_validations = 0
        total_validations = len(valid_cases)
        
        for username in valid_cases:
            try:
                response = requests.get(f"{BACKEND_URL}/auth/check-username/{username}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    available = data.get('available', False)
                    
                    if available:
                        passed_validations += 1
                        print(f"   ✅ '{username}': Correctly accepted as valid format")
                    else:
                        reason = data.get('reason', '')
                        if "already taken" in reason.lower():
                            # This is fine - username format is valid but already exists
                            passed_validations += 1
                            print(f"   ✅ '{username}': Valid format (already taken)")
                        else:
                            print(f"   ❌ '{username}': Incorrectly rejected - {reason}")
                else:
                    print(f"   ❌ '{username}': HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ '{username}': Error - {str(e)}")
        
        success = passed_validations == total_validations
        self.log_test(
            "Valid Username Format Test", 
            success, 
            f"Passed {passed_validations}/{total_validations} format tests"
        )
        return success

    def test_integration_with_user_creation(self):
        """Test integration between username check and user creation"""
        try:
            # Step 1: Check availability of a new username
            test_username = f"integration_test_{str(uuid.uuid4())[:8]}"
            
            response1 = requests.get(f"{BACKEND_URL}/auth/check-username/{test_username}", timeout=10)
            if response1.status_code != 200:
                self.log_test("Integration Test - Step 1", False, f"Username check failed: HTTP {response1.status_code}")
                return False
            
            data1 = response1.json()
            if not data1.get('available', False):
                self.log_test("Integration Test - Step 1", False, f"Username should be available but reported as: {data1}")
                return False
            
            # Step 2: Create user with that username
            test_email = f"{test_username}@example.com"
            created, result = self.create_test_user(test_username, test_email)
            if not created:
                self.log_test("Integration Test - Step 2", False, f"User creation failed: {result}")
                return False
            
            # Step 3: Check that username is now unavailable
            response2 = requests.get(f"{BACKEND_URL}/auth/check-username/{test_username}", timeout=10)
            if response2.status_code != 200:
                self.log_test("Integration Test - Step 3", False, f"Username check failed: HTTP {response2.status_code}")
                return False
            
            data2 = response2.json()
            if data2.get('available', True):
                self.log_test("Integration Test - Step 3", False, f"Username should be unavailable but reported as: {data2}")
                return False
            
            self.log_test(
                "Integration with User Creation", 
                True, 
                f"Complete flow works: available → create user → unavailable"
            )
            return True
            
        except Exception as e:
            self.log_test("Integration with User Creation", False, error_msg=str(e))
            return False

    def test_edge_cases(self):
        """Test edge cases and special scenarios"""
        edge_cases = [
            ("admin", "Reserved admin username"),
            ("root", "Reserved root username"),
            ("test", "Common test username"),
            ("user", "Generic user username"),
            ("null", "Null string"),
            ("undefined", "Undefined string"),
            ("true", "Boolean string"),
            ("false", "Boolean string")
        ]
        
        passed_tests = 0
        total_tests = len(edge_cases)
        
        for username, description in edge_cases:
            try:
                response = requests.get(f"{BACKEND_URL}/auth/check-username/{username}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # For edge cases, we just want to ensure the endpoint responds properly
                    # The actual availability depends on whether these usernames exist
                    passed_tests += 1
                    available = data.get('available', False)
                    reason = data.get('reason', 'Available')
                    print(f"   ✅ {description} ('{username}'): {reason}")
                else:
                    print(f"   ❌ {description} ('{username}'): HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {description} ('{username}'): Error - {str(e)}")
        
        success = passed_tests == total_tests
        self.log_test(
            "Edge Cases Test", 
            success, 
            f"Handled {passed_tests}/{total_tests} edge cases properly"
        )
        return success

    def cleanup_test_users(self):
        """Clean up test users created during testing"""
        cleaned_count = 0
        for user_id in self.created_users:
            try:
                response = requests.delete(f"{BACKEND_URL}/admin/users/{user_id}", timeout=10)
                if response.status_code == 200:
                    cleaned_count += 1
            except:
                pass  # Ignore cleanup errors
        
        if cleaned_count > 0:
            self.log_test(
                "Test Cleanup", 
                True, 
                f"Successfully cleaned up {cleaned_count} test users"
            )

    def run_comprehensive_username_tests(self):
        """Run all username availability tests"""
        print("=" * 80)
        print("CATALORO USERNAME AVAILABILITY CHECK - COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Availability Tests
        print("🔍 BASIC AVAILABILITY TESTS")
        print("-" * 40)
        self.test_available_username()
        self.test_existing_username()
        
        # 2. Case Sensitivity Tests
        print("🔤 CASE SENSITIVITY TESTS")
        print("-" * 40)
        self.test_case_sensitivity()
        
        # 3. Validation Tests
        print("✅ USERNAME VALIDATION TESTS")
        print("-" * 40)
        self.test_invalid_usernames()
        self.test_valid_username_formats()
        
        # 4. Integration Tests
        print("🔗 INTEGRATION TESTS")
        print("-" * 40)
        self.test_integration_with_user_creation()
        
        # 5. Edge Cases
        print("🎯 EDGE CASES TESTS")
        print("-" * 40)
        self.test_edge_cases()
        
        # 6. Cleanup
        print("🧹 CLEANUP")
        print("-" * 40)
        self.cleanup_test_users()
        
        # Print Summary
        print("=" * 80)
        print("USERNAME AVAILABILITY TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = UsernameAvailabilityTester()
    passed, failed, results = tester.run_comprehensive_username_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)