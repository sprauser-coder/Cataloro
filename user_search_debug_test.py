#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - User Search Debug Focus
Testing the GET /api/admin/users endpoint to debug UserNotificationSelector component issues
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

class UserSearchDebugTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
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

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}, Version: {data.get('version')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def test_get_admin_users_structure(self):
        """Test GET /api/admin/users endpoint and analyze user data structure"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if response.status_code == 200:
                users = response.json()
                
                if not isinstance(users, list):
                    self.log_test(
                        "GET /api/admin/users Structure", 
                        False, 
                        f"Expected array but got: {type(users)}"
                    )
                    return None
                
                user_count = len(users)
                
                if user_count == 0:
                    self.log_test(
                        "GET /api/admin/users Structure", 
                        True, 
                        "No users found in database - this explains the search issue"
                    )
                    return users
                
                # Analyze first user structure
                first_user = users[0]
                user_fields = list(first_user.keys())
                
                # Check for common field variations
                name_fields = []
                if 'firstName' in first_user:
                    name_fields.append('firstName')
                if 'first_name' in first_user:
                    name_fields.append('first_name')
                if 'full_name' in first_user:
                    name_fields.append('full_name')
                if 'username' in first_user:
                    name_fields.append('username')
                if 'email' in first_user:
                    name_fields.append('email')
                
                self.log_test(
                    "GET /api/admin/users Structure", 
                    True, 
                    f"Found {user_count} users. Available fields: {user_fields}. Name-related fields: {name_fields}"
                )
                
                return users
            else:
                self.log_test("GET /api/admin/users Structure", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("GET /api/admin/users Structure", False, error_msg=str(e))
            return None

    def analyze_user_field_names(self, users):
        """Analyze user field names to identify search field issues"""
        if not users or len(users) == 0:
            self.log_test(
                "User Field Names Analysis", 
                False, 
                "No users available for field analysis"
            )
            return
        
        try:
            # Analyze all users to get comprehensive field mapping
            all_fields = set()
            field_variations = {
                'name_fields': [],
                'email_fields': [],
                'id_fields': [],
                'other_fields': []
            }
            
            for user in users:
                all_fields.update(user.keys())
                
                # Categorize fields
                for field in user.keys():
                    field_lower = field.lower()
                    if any(name_part in field_lower for name_part in ['name', 'first', 'last', 'full']):
                        if field not in field_variations['name_fields']:
                            field_variations['name_fields'].append(field)
                    elif 'email' in field_lower:
                        if field not in field_variations['email_fields']:
                            field_variations['email_fields'].append(field)
                    elif 'id' in field_lower:
                        if field not in field_variations['id_fields']:
                            field_variations['id_fields'].append(field)
                    else:
                        if field not in field_variations['other_fields']:
                            field_variations['other_fields'].append(field)
            
            # Sample user data for debugging
            sample_user = users[0]
            sample_data = {
                'id': sample_user.get('id', 'NOT_FOUND'),
                'username': sample_user.get('username', 'NOT_FOUND'),
                'email': sample_user.get('email', 'NOT_FOUND'),
                'full_name': sample_user.get('full_name', 'NOT_FOUND'),
                'first_name': sample_user.get('first_name', 'NOT_FOUND'),
                'firstName': sample_user.get('firstName', 'NOT_FOUND'),
                'last_name': sample_user.get('last_name', 'NOT_FOUND'),
                'lastName': sample_user.get('lastName', 'NOT_FOUND')
            }
            
            details = f"""
Field Analysis Results:
- Total unique fields: {len(all_fields)}
- Name fields: {field_variations['name_fields']}
- Email fields: {field_variations['email_fields']}
- ID fields: {field_variations['id_fields']}
- Other fields: {field_variations['other_fields']}

Sample User Data:
{json.dumps(sample_data, indent=2)}

Full Sample User:
{json.dumps(sample_user, indent=2)}
            """
            
            self.log_test(
                "User Field Names Analysis", 
                True, 
                details.strip()
            )
            
            return field_variations
            
        except Exception as e:
            self.log_test("User Field Names Analysis", False, error_msg=str(e))
            return None

    def test_user_data_availability(self, users):
        """Check if there are actual registered users with searchable data"""
        if not users:
            self.log_test(
                "User Data Availability", 
                False, 
                "No users returned from API - UserNotificationSelector will have no data to search"
            )
            return False
        
        try:
            user_count = len(users)
            
            # Check for users with searchable content
            searchable_users = []
            for user in users:
                has_searchable_data = False
                searchable_fields = []
                
                # Check various name field possibilities
                name_fields_to_check = ['username', 'full_name', 'first_name', 'firstName', 'last_name', 'lastName', 'email']
                for field in name_fields_to_check:
                    if field in user and user[field] and str(user[field]).strip():
                        has_searchable_data = True
                        searchable_fields.append(f"{field}: '{user[field]}'")
                
                if has_searchable_data:
                    searchable_users.append({
                        'user_id': user.get('id', 'NO_ID'),
                        'searchable_fields': searchable_fields
                    })
            
            if len(searchable_users) == 0:
                self.log_test(
                    "User Data Availability", 
                    False, 
                    f"Found {user_count} users but none have searchable name/email data"
                )
                return False
            
            # Show sample of searchable users
            sample_searchable = searchable_users[:3]  # First 3 users
            sample_details = []
            for user_info in sample_searchable:
                sample_details.append(f"User {user_info['user_id']}: {', '.join(user_info['searchable_fields'])}")
            
            self.log_test(
                "User Data Availability", 
                True, 
                f"Found {len(searchable_users)} users with searchable data out of {user_count} total.\n" +
                f"Sample searchable users:\n" + "\n".join(sample_details)
            )
            
            return True
            
        except Exception as e:
            self.log_test("User Data Availability", False, error_msg=str(e))
            return False

    def test_response_format_structure(self, users):
        """Verify the response format matches what frontend expects"""
        try:
            # Check if response is direct array vs wrapped in data object
            if isinstance(users, list):
                format_type = "Direct array"
                user_count = len(users)
            elif isinstance(users, dict) and 'users' in users:
                format_type = "Wrapped in 'users' key"
                user_count = len(users['users']) if isinstance(users['users'], list) else 0
            elif isinstance(users, dict) and 'data' in users:
                format_type = "Wrapped in 'data' key"
                user_count = len(users['data']) if isinstance(users['data'], list) else 0
            else:
                format_type = f"Unknown format: {type(users)}"
                user_count = 0
            
            # Check if frontend expects data.users vs direct array
            expected_formats = [
                "Direct array (users)",
                "Wrapped object (data.users)", 
                "Wrapped object (response.users)"
            ]
            
            self.log_test(
                "Response Format Structure", 
                True, 
                f"Current format: {format_type} with {user_count} users.\n" +
                f"Frontend may expect one of: {', '.join(expected_formats)}"
            )
            
            return format_type
            
        except Exception as e:
            self.log_test("Response Format Structure", False, error_msg=str(e))
            return None

    def create_test_users_for_search(self):
        """Create a few test users to ensure there's data for search testing"""
        created_users = []
        
        test_users = [
            {
                "username": "john_doe_search_test",
                "email": "john.doe.search@example.com",
                "password": "TestPassword123!",
                "full_name": "John Doe",
                "role": "user"
            },
            {
                "username": "jane_smith_search_test", 
                "email": "jane.smith.search@example.com",
                "password": "TestPassword123!",
                "full_name": "Jane Smith",
                "role": "user"
            },
            {
                "username": "admin_search_test",
                "email": "admin.search@example.com", 
                "password": "TestPassword123!",
                "full_name": "Admin User",
                "role": "admin"
            }
        ]
        
        try:
            for i, user_data in enumerate(test_users):
                response = requests.post(
                    f"{BACKEND_URL}/admin/users",
                    json=user_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    created_user = data.get('user', {})
                    created_users.append(created_user.get('id'))
                    self.log_test(
                        f"Create Test User {i+1}",
                        True,
                        f"Created user: {user_data['username']} ({user_data['full_name']})"
                    )
                else:
                    error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                    self.log_test(f"Create Test User {i+1}", False, error_msg=error_detail)
            
            if created_users:
                self.log_test(
                    "Test Users Creation Summary",
                    True,
                    f"Successfully created {len(created_users)} test users for search testing"
                )
            
            return created_users
            
        except Exception as e:
            self.log_test("Create Test Users for Search", False, error_msg=str(e))
            return []

    def cleanup_test_users(self, user_ids):
        """Clean up test users created during testing"""
        if not user_ids:
            return
            
        cleaned_count = 0
        for user_id in user_ids:
            if user_id:
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

    def run_user_search_debug_tests(self):
        """Run comprehensive user search debugging tests"""
        print("=" * 80)
        print("CATALORO USER SEARCH DEBUG TESTING")
        print("Debugging UserNotificationSelector component search issues")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        created_user_ids = []
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting user search debug testing.")
            return
        
        # 2. Test GET /api/admin/users endpoint structure
        print("👥 GET /api/admin/users ENDPOINT ANALYSIS")
        print("-" * 40)
        users = self.test_get_admin_users_structure()
        
        # 3. Analyze user field names
        print("🔍 USER FIELD NAMES ANALYSIS")
        print("-" * 40)
        field_variations = self.analyze_user_field_names(users) if users else None
        
        # 4. Check user data availability
        print("📊 USER DATA AVAILABILITY CHECK")
        print("-" * 40)
        has_searchable_data = self.test_user_data_availability(users)
        
        # 5. Test response format structure
        print("📋 RESPONSE FORMAT STRUCTURE CHECK")
        print("-" * 40)
        response_format = self.test_response_format_structure(users)
        
        # 6. Create test users if no searchable data exists
        if not has_searchable_data or (users and len(users) < 3):
            print("➕ CREATING TEST USERS FOR SEARCH TESTING")
            print("-" * 40)
            created_user_ids = self.create_test_users_for_search()
            
            # Re-test with new users
            print("🔄 RE-TESTING WITH NEW USERS")
            print("-" * 40)
            users = self.test_get_admin_users_structure()
            self.test_user_data_availability(users)
        
        # 7. Final Analysis and Recommendations
        print("💡 FRONTEND INTEGRATION ANALYSIS")
        print("-" * 40)
        self.provide_frontend_recommendations(users, field_variations, response_format)
        
        # 8. Cleanup
        if created_user_ids:
            print("🧹 CLEANUP")
            print("-" * 40)
            self.cleanup_test_users(created_user_ids)
        
        # Print Summary
        print("=" * 80)
        print("USER SEARCH DEBUG TEST SUMMARY")
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
        
        print("\n🎯 USER SEARCH DEBUG TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results

    def provide_frontend_recommendations(self, users, field_variations, response_format):
        """Provide recommendations for fixing the frontend UserNotificationSelector"""
        try:
            recommendations = []
            
            # Check user count
            user_count = len(users) if users else 0
            if user_count == 0:
                recommendations.append("❌ NO USERS: Database has no users - UserNotificationSelector will be empty")
            else:
                recommendations.append(f"✅ USER COUNT: Found {user_count} users in database")
            
            # Check field names
            if field_variations and users:
                sample_user = users[0]
                
                # Check for common field name issues
                if 'firstName' not in sample_user and 'first_name' not in sample_user:
                    if 'full_name' in sample_user:
                        recommendations.append("⚠️ FIELD NAMES: No firstName/first_name field. Use 'full_name' instead")
                    elif 'username' in sample_user:
                        recommendations.append("⚠️ FIELD NAMES: No firstName/first_name field. Use 'username' instead")
                    else:
                        recommendations.append("❌ FIELD NAMES: No name fields found for search")
                else:
                    if 'firstName' in sample_user:
                        recommendations.append("✅ FIELD NAMES: 'firstName' field available")
                    if 'first_name' in sample_user:
                        recommendations.append("✅ FIELD NAMES: 'first_name' field available")
                
                # Check email field
                if 'email' in sample_user:
                    recommendations.append("✅ EMAIL FIELD: 'email' field available for search")
                else:
                    recommendations.append("❌ EMAIL FIELD: No 'email' field found")
            
            # Check response format
            if response_format:
                if "Direct array" in response_format:
                    recommendations.append("✅ RESPONSE FORMAT: Direct array - frontend should access users directly")
                elif "Wrapped" in response_format:
                    recommendations.append("⚠️ RESPONSE FORMAT: Wrapped response - frontend needs to access nested data")
            
            # Provide specific frontend code recommendations
            if users and len(users) > 0:
                sample_user = users[0]
                available_fields = list(sample_user.keys())
                
                code_recommendations = []
                
                # Search field recommendations
                search_fields = []
                if 'full_name' in available_fields:
                    search_fields.append('full_name')
                if 'username' in available_fields:
                    search_fields.append('username')
                if 'email' in available_fields:
                    search_fields.append('email')
                if 'firstName' in available_fields:
                    search_fields.append('firstName')
                if 'first_name' in available_fields:
                    search_fields.append('first_name')
                
                if search_fields:
                    code_recommendations.append(f"Frontend should search these fields: {', '.join(search_fields)}")
                
                recommendations.extend(code_recommendations)
            
            # Log all recommendations
            recommendation_text = "\n".join([f"  {rec}" for rec in recommendations])
            
            self.log_test(
                "Frontend Integration Recommendations",
                True,
                f"Analysis complete. Recommendations:\n{recommendation_text}"
            )
            
        except Exception as e:
            self.log_test("Frontend Integration Recommendations", False, error_msg=str(e))

if __name__ == "__main__":
    tester = UserSearchDebugTester()
    
    print("🔍 RUNNING USER SEARCH DEBUG TESTING")
    print("Investigating UserNotificationSelector component search issues...")
    print()
    
    passed, failed, results = tester.run_user_search_debug_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)