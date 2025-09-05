#!/usr/bin/env python3
"""
Final Comprehensive Username Availability Test
Testing all scenarios from the review request with proper handling of edge cases
"""

import requests
import json
import uuid
import urllib.parse
from datetime import datetime

BACKEND_URL = "https://cataloro-marketplace-3.preview.emergentagent.com/api"

class FinalUsernameTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.created_users = []
        
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

    def test_available_username_scenarios(self):
        """Test various available username scenarios"""
        test_cases = [
            f"available_{str(uuid.uuid4())[:8]}",
            f"new_user_{str(uuid.uuid4())[:8]}",
            f"test.user.{str(uuid.uuid4())[:6]}",
            f"test-user-{str(uuid.uuid4())[:6]}",
            f"test_user_{str(uuid.uuid4())[:6]}"
        ]
        
        passed = 0
        for username in test_cases:
            try:
                response = requests.get(f"{BACKEND_URL}/auth/check-username/{username}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('available', False):
                        passed += 1
                        print(f"   ✅ '{username}': Available")
                    else:
                        print(f"   ❌ '{username}': {data.get('reason', 'Unavailable')}")
                else:
                    print(f"   ❌ '{username}': HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ '{username}': Error - {str(e)}")
        
        success = passed == len(test_cases)
        self.log_test(
            "Available Username Scenarios", 
            success, 
            f"Passed {passed}/{len(test_cases)} available username tests"
        )
        return success

    def test_existing_username_scenarios(self):
        """Test existing username detection"""
        # Create a test user first
        test_username = f"existing_{str(uuid.uuid4())[:8]}"
        test_email = f"{test_username}@example.com"
        
        created, result = self.create_test_user(test_username, test_email)
        if not created:
            self.log_test("Existing Username Test - Setup", False, f"Failed to create test user: {result}")
            return False
        
        # Test the created username
        try:
            response = requests.get(f"{BACKEND_URL}/auth/check-username/{test_username}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                available = data.get('available', True)
                reason = data.get('reason', '')
                
                if not available and "already taken" in reason.lower():
                    self.log_test(
                        "Existing Username Detection", 
                        True, 
                        f"Username '{test_username}' correctly reported as unavailable: {reason}"
                    )
                    return True
                else:
                    self.log_test(
                        "Existing Username Detection", 
                        False, 
                        f"Username '{test_username}' should be unavailable but got: available={available}, reason='{reason}'"
                    )
                    return False
            else:
                self.log_test("Existing Username Detection", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Existing Username Detection", False, error_msg=str(e))
            return False

    def test_invalid_username_validation(self):
        """Test invalid username validation with proper handling"""
        invalid_cases = [
            ("ab", "Too short (2 characters)", True),  # Should be rejected
            ("a" * 51, "Too long (51 characters)", True),  # Should be rejected
            ("user@name", "Contains @ symbol", True),  # Should be rejected
            ("user name", "Contains space", True),  # Should be rejected
            ("user$name", "Contains $ symbol", True),  # Should be rejected
            ("user%name", "Contains % symbol", True),  # Should be rejected
        ]
        
        # Special cases that need URL encoding
        special_cases = [
            ("user#name", "Contains # symbol", True),  # Should be rejected, needs encoding
        ]
        
        passed = 0
        total = len(invalid_cases) + len(special_cases)
        
        # Test regular invalid cases
        for username, description, should_reject in invalid_cases:
            try:
                response = requests.get(f"{BACKEND_URL}/auth/check-username/{username}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    available = data.get('available', True)
                    reason = data.get('reason', '')
                    
                    if should_reject and not available and reason:
                        passed += 1
                        print(f"   ✅ {description}: Correctly rejected - {reason}")
                    elif not should_reject and available:
                        passed += 1
                        print(f"   ✅ {description}: Correctly accepted")
                    else:
                        print(f"   ❌ {description}: Expected rejection={should_reject}, got available={available}")
                else:
                    print(f"   ❌ {description}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {description}: Error - {str(e)}")
        
        # Test special cases with URL encoding
        for username, description, should_reject in special_cases:
            try:
                encoded_username = urllib.parse.quote(username, safe='')
                response = requests.get(f"{BACKEND_URL}/auth/check-username/{encoded_username}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    available = data.get('available', True)
                    reason = data.get('reason', '')
                    
                    if should_reject and not available and reason:
                        passed += 1
                        print(f"   ✅ {description}: Correctly rejected - {reason}")
                    else:
                        print(f"   ❌ {description}: Expected rejection, got available={available}")
                else:
                    print(f"   ❌ {description}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {description}: Error - {str(e)}")
        
        # Test empty username (should return 404 due to invalid URL path)
        try:
            response = requests.get(f"{BACKEND_URL}/auth/check-username/", timeout=10)
            if response.status_code == 404:
                passed += 1
                print(f"   ✅ Empty username: Correctly returns 404 (invalid URL path)")
            else:
                print(f"   ❌ Empty username: Expected 404, got HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Empty username: Error - {str(e)}")
        
        total += 1  # Add empty username test to total
        
        success = passed == total
        self.log_test(
            "Invalid Username Validation", 
            success, 
            f"Passed {passed}/{total} validation tests"
        )
        return success

    def test_case_sensitivity(self):
        """Test case-insensitive username matching"""
        # Create user with lowercase username
        base_username = f"casetest_{str(uuid.uuid4())[:8]}".lower()
        test_email = f"{base_username}@example.com"
        
        created, result = self.create_test_user(base_username, test_email)
        if not created:
            self.log_test("Case Sensitivity Test - Setup", False, f"Failed to create test user: {result}")
            return False
        
        # Test variations
        test_variations = [
            base_username.upper(),
            base_username.capitalize(),
            base_username.title()
        ]
        
        passed = 0
        for variation in test_variations:
            try:
                response = requests.get(f"{BACKEND_URL}/auth/check-username/{variation}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    available = data.get('available', True)
                    
                    if not available:
                        passed += 1
                        print(f"   ✅ '{variation}': Correctly detected as unavailable (case-insensitive)")
                    else:
                        print(f"   ❌ '{variation}': Should be unavailable but reported as available")
                else:
                    print(f"   ❌ '{variation}': HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ '{variation}': Error - {str(e)}")
        
        success = passed == len(test_variations)
        self.log_test(
            "Case Sensitivity Test", 
            success, 
            f"Case-insensitive matching works for {passed}/{len(test_variations)} variations"
        )
        return success

    def test_integration_with_user_creation(self):
        """Test complete integration flow"""
        test_username = f"integration_{str(uuid.uuid4())[:8]}"
        test_email = f"{test_username}@example.com"
        
        try:
            # Step 1: Check availability (should be available)
            response1 = requests.get(f"{BACKEND_URL}/auth/check-username/{test_username}", timeout=10)
            if response1.status_code != 200 or not response1.json().get('available', False):
                self.log_test("Integration Test", False, "Step 1 failed: Username should be available")
                return False
            
            # Step 2: Create user
            created, result = self.create_test_user(test_username, test_email)
            if not created:
                self.log_test("Integration Test", False, f"Step 2 failed: User creation failed - {result}")
                return False
            
            # Step 3: Check availability again (should be unavailable)
            response2 = requests.get(f"{BACKEND_URL}/auth/check-username/{test_username}", timeout=10)
            if response2.status_code != 200:
                self.log_test("Integration Test", False, f"Step 3 failed: HTTP {response2.status_code}")
                return False
            
            data2 = response2.json()
            if data2.get('available', True):
                self.log_test("Integration Test", False, "Step 3 failed: Username should now be unavailable")
                return False
            
            self.log_test(
                "Integration with User Creation", 
                True, 
                "Complete flow successful: available → create user → unavailable"
            )
            return True
            
        except Exception as e:
            self.log_test("Integration with User Creation", False, error_msg=str(e))
            return False

    def test_edge_cases(self):
        """Test edge cases and special usernames"""
        edge_cases = [
            ("admin", "Reserved admin username"),
            ("root", "Reserved root username"),
            ("test", "Common test username"),
            ("user", "Generic user username"),
            ("123", "Numeric username"),
            ("a.b.c", "Multiple dots"),
            ("a-b-c", "Multiple hyphens"),
            ("a_b_c", "Multiple underscores"),
            ("MixedCase123", "Mixed case with numbers")
        ]
        
        passed = 0
        for username, description in edge_cases:
            try:
                response = requests.get(f"{BACKEND_URL}/auth/check-username/{username}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    available = data.get('available', False)
                    reason = data.get('reason', 'Available')
                    passed += 1
                    print(f"   ✅ {description} ('{username}'): {reason}")
                else:
                    print(f"   ❌ {description} ('{username}'): HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {description} ('{username}'): Error - {str(e)}")
        
        success = passed == len(edge_cases)
        self.log_test(
            "Edge Cases Test", 
            success, 
            f"Successfully handled {passed}/{len(edge_cases)} edge cases"
        )
        return success

    def cleanup_test_users(self):
        """Clean up test users"""
        cleaned_count = 0
        for user_id in self.created_users:
            try:
                response = requests.delete(f"{BACKEND_URL}/admin/users/{user_id}", timeout=10)
                if response.status_code == 200:
                    cleaned_count += 1
            except:
                pass
        
        if cleaned_count > 0:
            self.log_test(
                "Test Cleanup", 
                True, 
                f"Successfully cleaned up {cleaned_count} test users"
            )

    def run_all_tests(self):
        """Run all username availability tests"""
        print("=" * 80)
        print("FINAL USERNAME AVAILABILITY CHECK TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        print("🔍 1. AVAILABLE USERNAME SCENARIOS")
        print("-" * 50)
        self.test_available_username_scenarios()
        
        print("❌ 2. EXISTING USERNAME DETECTION")
        print("-" * 50)
        self.test_existing_username_scenarios()
        
        print("🚫 3. INVALID USERNAME VALIDATION")
        print("-" * 50)
        self.test_invalid_username_validation()
        
        print("🔤 4. CASE SENSITIVITY TESTING")
        print("-" * 50)
        self.test_case_sensitivity()
        
        print("🔗 5. INTEGRATION WITH USER CREATION")
        print("-" * 50)
        self.test_integration_with_user_creation()
        
        print("🎯 6. EDGE CASES")
        print("-" * 50)
        self.test_edge_cases()
        
        print("🧹 7. CLEANUP")
        print("-" * 50)
        self.cleanup_test_users()
        
        # Summary
        print("=" * 80)
        print("FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result.get('error', 'See details above')}")
        
        print("\n" + "=" * 80)
        return self.passed_tests, self.failed_tests

if __name__ == "__main__":
    tester = FinalUsernameTester()
    passed, failed = tester.run_all_tests()
    exit(0 if failed == 0 else 1)