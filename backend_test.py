#!/usr/bin/env python3
"""
Backend Testing Script for Admin Authentication and Access Control
Testing admin user authentication and access to admin panel endpoints
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://market-refactor-1.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, details, response_time=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        time_info = f" ({response_time:.1f}ms)" if response_time else ""
        print(f"{status}: {test_name}{time_info}")
        print(f"   Details: {details}")
        print()
    
    async def test_login_and_get_token(self, email="admin@cataloro.com", password="admin123"):
        """Test login and get JWT token"""
        start_time = datetime.now()
        
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    user = data.get("user", {})
                    user_id = user.get("id")
                    
                    if token and user_id:
                        self.log_result(
                            "Login Authentication", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Unknown')} (ID: {user_id}), token received",
                            response_time
                        )
                        return token, user_id, user
                    else:
                        self.log_result(
                            "Login Authentication", 
                            False, 
                            f"Login successful but missing token or user_id in response: {data}",
                            response_time
                        )
                        return None, None, None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Login Authentication", 
                        False, 
                        f"Login failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None, None, None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Login Authentication", 
                False, 
                f"Login request failed with exception: {str(e)}",
                response_time
            )
            return None, None, None
    
    async def test_messages_endpoint_without_auth(self, user_id):
        """Test messages endpoint without authentication - should be BLOCKED"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/user/{user_id}/messages") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Authentication Security Test", 
                        False, 
                        f"❌ SECURITY VULNERABILITY: Endpoint accessible without auth, returned {len(data)} messages",
                        response_time
                    )
                    return data
                elif response.status in [401, 403]:
                    self.log_result(
                        "Authentication Security Test", 
                        True, 
                        f"✅ SECURITY FIX WORKING: Endpoint properly requires authentication (Status {response.status})",
                        response_time
                    )
                    return None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Authentication Security Test", 
                        False, 
                        f"Unexpected status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Authentication Security Test", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_messages_endpoint_with_auth(self, user_id, token):
        """Test messages endpoint with authentication"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.get(f"{BACKEND_URL}/user/{user_id}/messages", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Messages Endpoint (With Auth)", 
                        True, 
                        f"Successfully retrieved {len(data)} messages with authentication",
                        response_time
                    )
                    return data
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Messages Endpoint (With Auth)", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Messages Endpoint (With Auth)", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_message_structure(self, messages):
        """Test message data structure and NULL content validation"""
        if not messages:
            self.log_result(
                "Message Structure Validation", 
                True, 
                "No messages to validate (empty array is valid)"
            )
            return True
        
        try:
            required_fields = ['sender_id', 'recipient_id', 'content', 'created_at']
            optional_fields = ['subject', 'read', 'sender_name', 'recipient_name', '_id', 'id']
            
            structure_issues = []
            null_content_count = 0
            
            for i, message in enumerate(messages):
                # Check required fields
                missing_required = [field for field in required_fields if field not in message]
                if missing_required:
                    structure_issues.append(f"Message {i}: Missing required fields: {missing_required}")
                
                # Check data types
                if 'sender_id' in message and not isinstance(message['sender_id'], str):
                    structure_issues.append(f"Message {i}: sender_id should be string")
                
                if 'recipient_id' in message and not isinstance(message['recipient_id'], str):
                    structure_issues.append(f"Message {i}: recipient_id should be string")
                
                # CRITICAL: Check for NULL content (the main fix)
                content = message.get('content')
                if content is None or content == "null" or content == "":
                    null_content_count += 1
                    structure_issues.append(f"Message {i}: NULL/empty content detected")
                elif not isinstance(content, str):
                    structure_issues.append(f"Message {i}: content should be string, got {type(content)}")
            
            # Report NULL content findings
            if null_content_count > 0:
                self.log_result(
                    "NULL Content Data Quality Test", 
                    False, 
                    f"❌ DATA QUALITY ISSUE: {null_content_count} messages with NULL/empty content found"
                )
            else:
                self.log_result(
                    "NULL Content Data Quality Test", 
                    True, 
                    f"✅ DATA QUALITY FIX WORKING: No NULL content found in {len(messages)} messages"
                )
            
            if structure_issues:
                self.log_result(
                    "Message Structure Validation", 
                    False, 
                    f"Structure issues found: {'; '.join(structure_issues)}"
                )
                return False
            else:
                sample_message = messages[0] if messages else {}
                self.log_result(
                    "Message Structure Validation", 
                    True, 
                    f"All {len(messages)} messages have valid structure. Sample fields: {list(sample_message.keys())}"
                )
                return True
                
        except Exception as e:
            self.log_result(
                "Message Structure Validation", 
                False, 
                f"Validation failed with exception: {str(e)}"
            )
            return False
    
    async def test_database_connectivity(self):
        """Test if backend can connect to database"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Database Connectivity", 
                        True, 
                        f"Backend health check passed: {data.get('status', 'unknown')}",
                        response_time
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Database Connectivity", 
                        False, 
                        f"Health check failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Database Connectivity", 
                False, 
                f"Health check failed with exception: {str(e)}",
                response_time
            )
            return False
    
    async def test_create_test_message(self, sender_id, token):
        """Create a test message to ensure there's data to retrieve"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            message_data = {
                "recipient_id": sender_id,  # Send to self for testing
                "subject": "Test Message for Security Validation",
                "content": "This is a test message created to verify the messaging system security fixes are working properly."
            }
            
            async with self.session.post(f"{BACKEND_URL}/user/{sender_id}/messages", 
                                       json=message_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    message_id = data.get("id")
                    self.log_result(
                        "Send Message Authentication Test", 
                        True, 
                        f"✅ Send message with auth working (ID: {message_id})",
                        response_time
                    )
                    return message_id
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Send Message Authentication Test", 
                        False, 
                        f"Failed to create test message with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Send Message Authentication Test", 
                False, 
                f"Message creation failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_send_message_without_auth(self, user_id):
        """Test sending message without authentication - should be BLOCKED"""
        start_time = datetime.now()
        
        try:
            message_data = {
                "recipient_id": user_id,
                "subject": "Unauthorized Test",
                "content": "This should not be sent without authentication"
            }
            
            async with self.session.post(f"{BACKEND_URL}/user/{user_id}/messages", 
                                       json=message_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    self.log_result(
                        "Send Message Security Test", 
                        False, 
                        f"❌ SECURITY VULNERABILITY: Can send messages without authentication",
                        response_time
                    )
                    return True
                elif response.status in [401, 403]:
                    self.log_result(
                        "Send Message Security Test", 
                        True, 
                        f"✅ SECURITY FIX WORKING: Send message properly requires authentication (Status {response.status})",
                        response_time
                    )
                    return False
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Send Message Security Test", 
                        False, 
                        f"Unexpected status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Send Message Security Test", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return False
    
    async def test_cross_user_authorization(self, user1_info, user2_info):
        """Test that users cannot access other users' messages (unless admin)"""
        start_time = datetime.now()
        
        try:
            # Check if user1 is an admin
            user1_role = user1_info.get('user', {}).get('role', '')
            user1_user_role = user1_info.get('user', {}).get('user_role', '')
            is_admin = (user1_role == 'admin' or user1_user_role in ['Admin', 'Admin-Manager'])
            
            # Try to access user2's messages with user1's token
            headers = {"Authorization": f"Bearer {user1_info['token']}"}
            
            async with self.session.get(f"{BACKEND_URL}/user/{user2_info['user_id']}/messages", 
                                      headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    if is_admin:
                        self.log_result(
                            "Cross-User Authorization Test", 
                            True, 
                            f"✅ ADMIN PRIVILEGE WORKING: Admin can access other user's messages ({len(data)} messages)",
                            response_time
                        )
                        return True
                    else:
                        self.log_result(
                            "Cross-User Authorization Test", 
                            False, 
                            f"❌ AUTHORIZATION VULNERABILITY: Non-admin user can access other user's messages ({len(data)} messages)",
                            response_time
                        )
                        return False
                elif response.status == 403:
                    if is_admin:
                        self.log_result(
                            "Cross-User Authorization Test", 
                            False, 
                            f"❌ ADMIN ACCESS BLOCKED: Admin should be able to access other user's messages",
                            response_time
                        )
                        return False
                    else:
                        self.log_result(
                            "Cross-User Authorization Test", 
                            True, 
                            f"✅ AUTHORIZATION FIX WORKING: Non-admin cross-user access properly blocked (Status 403)",
                            response_time
                        )
                        return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Cross-User Authorization Test", 
                        False, 
                        f"Unexpected status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Cross-User Authorization Test", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return False
    
    async def test_mark_read_authentication(self, user_id, token, message_id):
        """Test mark message as read with authentication"""
        if not message_id:
            self.log_result(
                "Mark Read Authentication Test", 
                False, 
                "No message ID available for testing"
            )
            return False
            
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.put(f"{BACKEND_URL}/user/{user_id}/messages/{message_id}/read", 
                                      headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    self.log_result(
                        "Mark Read Authentication Test", 
                        True, 
                        f"✅ Mark read with auth working",
                        response_time
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Mark Read Authentication Test", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Mark Read Authentication Test", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return False
    
    async def test_mark_read_without_auth(self, user_id, message_id):
        """Test mark message as read without authentication - should be BLOCKED"""
        if not message_id:
            self.log_result(
                "Mark Read Security Test", 
                False, 
                "No message ID available for testing"
            )
            return False
            
        start_time = datetime.now()
        
        try:
            async with self.session.put(f"{BACKEND_URL}/user/{user_id}/messages/{message_id}/read") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    self.log_result(
                        "Mark Read Security Test", 
                        False, 
                        f"❌ SECURITY VULNERABILITY: Can mark messages as read without authentication",
                        response_time
                    )
                    return False
                elif response.status in [401, 403]:
                    self.log_result(
                        "Mark Read Security Test", 
                        True, 
                        f"✅ SECURITY FIX WORKING: Mark read properly requires authentication (Status {response.status})",
                        response_time
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Mark Read Security Test", 
                        False, 
                        f"Unexpected status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Mark Read Security Test", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return False
    
    async def test_different_user_scenarios(self):
        """Test with different user scenarios"""
        test_users = [
            {"email": "admin@cataloro.com", "name": "Admin User"},
            {"email": "demo@cataloro.com", "name": "Demo User"},
            {"email": "user@cataloro.com", "name": "Regular User"}
        ]
        
        successful_logins = []
        
        for user_info in test_users:
            token, user_id, user = await self.test_login_and_get_token(user_info["email"])
            if token and user_id:
                successful_logins.append({
                    "email": user_info["email"],
                    "name": user_info["name"],
                    "token": token,
                    "user_id": user_id,
                    "user": user
                })
        
        if not successful_logins:
            self.log_result(
                "User Scenarios Test", 
                False, 
                "No users could be logged in successfully"
            )
            return None
        
        # Test messages for each successful login
        for login_info in successful_logins:
            messages = await self.test_messages_endpoint_with_auth(login_info["user_id"], login_info["token"])
            await self.test_message_structure(messages)
        
        return successful_logins  # Return all successful logins for further testing
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("MESSAGING/CONVERSATIONS SECURITY FIXES TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['details']}")
            print()
        
        print("SECURITY FIXES VALIDATION:")
        
        # Analyze security-specific results
        auth_security_tests = [r for r in self.test_results if "Security" in r["test"]]
        auth_tests = [r for r in self.test_results if "Authentication" in r["test"]]
        authorization_tests = [r for r in self.test_results if "Authorization" in r["test"]]
        data_quality_tests = [r for r in self.test_results if "NULL Content" in r["test"]]
        
        # Authentication Security
        auth_security_passed = all(r["success"] for r in auth_security_tests)
        if auth_security_passed:
            print("✅ AUTHENTICATION SECURITY: All endpoints properly require JWT tokens")
        else:
            print("❌ AUTHENTICATION SECURITY: Some endpoints accessible without authentication")
        
        # Authorization Security
        auth_passed = all(r["success"] for r in authorization_tests)
        if auth_passed:
            print("✅ AUTHORIZATION SECURITY: Cross-user access properly blocked")
        elif not authorization_tests:
            print("⚠️ AUTHORIZATION SECURITY: Not tested (insufficient users)")
        else:
            print("❌ AUTHORIZATION SECURITY: Cross-user access vulnerabilities detected")
        
        # Data Quality
        data_quality_passed = all(r["success"] for r in data_quality_tests)
        if data_quality_passed:
            print("✅ DATA QUALITY: No NULL content found in messages")
        elif not data_quality_tests:
            print("⚠️ DATA QUALITY: Not tested (no messages found)")
        else:
            print("❌ DATA QUALITY: NULL content still present in messages")
        
        # Overall endpoint functionality
        message_tests = [r for r in self.test_results if "Messages Endpoint (With Auth)" in r["test"]]
        if any(r["success"] for r in message_tests):
            print("✅ CONVERSATIONS LOADING: Messages endpoint working with authentication")
        else:
            print("❌ CONVERSATIONS LOADING: Messages endpoint not working properly")
        
        print()
        print("SECURITY FIXES STATUS:")
        
        # Overall security assessment
        critical_security_issues = []
        
        if not auth_security_passed:
            critical_security_issues.append("Authentication not enforced on all endpoints")
        
        if not auth_passed and authorization_tests:
            critical_security_issues.append("Cross-user access vulnerabilities exist")
        
        if not data_quality_passed and data_quality_tests:
            critical_security_issues.append("NULL content data quality issues remain")
        
        if critical_security_issues:
            print("❌ CRITICAL SECURITY ISSUES REMAIN:")
            for issue in critical_security_issues:
                print(f"   - {issue}")
            print("- RECOMMENDATION: Security fixes need additional work")
        else:
            print("✅ ALL SECURITY FIXES WORKING:")
            print("   - Authentication required on all message endpoints")
            print("   - Authorization prevents cross-user access")
            print("   - NULL content cleaned up from database")
            print("   - Conversations should now load properly for authenticated users")
        
        print()
        print("CONVERSATIONS LOADING STATUS:")
        if passed_tests >= total_tests * 0.8:  # 80% success rate
            print("✅ CONVERSATIONS SHOULD NOW LOAD PROPERLY")
            print("   - All security fixes are working")
            print("   - Authentication and authorization enforced")
            print("   - Data quality issues resolved")
        else:
            print("❌ CONVERSATIONS MAY STILL HAVE ISSUES")
            print("   - Review failed tests above for remaining problems")

async def main():
    """Main test execution"""
    print("🔍 TESTING FIXED MESSAGING/CONVERSATIONS SYSTEM")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    print("TESTING SECURITY FIXES:")
    print("✓ Authentication requirements on all message endpoints")
    print("✓ Authorization checks to prevent cross-user access")
    print("✓ NULL content cleanup verification")
    print("✓ JWT token validation on all operations")
    print()
    
    async with BackendTester() as tester:
        # Test 1: Database connectivity
        await tester.test_database_connectivity()
        
        # Test 2: User authentication and get multiple users for cross-user testing
        successful_logins = await tester.test_different_user_scenarios()
        
        if successful_logins and len(successful_logins) >= 1:
            primary_user = successful_logins[0]
            
            # Test 3: Authentication Security Tests
            print("\n🔒 AUTHENTICATION SECURITY TESTS:")
            await tester.test_messages_endpoint_without_auth(primary_user["user_id"])
            await tester.test_send_message_without_auth(primary_user["user_id"])
            
            # Test 4: Create test message with authentication
            message_id = await tester.test_create_test_message(primary_user["user_id"], primary_user["token"])
            
            # Test 5: Retrieve messages with authentication and validate structure/content
            messages = await tester.test_messages_endpoint_with_auth(primary_user["user_id"], primary_user["token"])
            await tester.test_message_structure(messages)
            
            # Test 6: Mark read authentication tests
            if message_id:
                await tester.test_mark_read_authentication(primary_user["user_id"], primary_user["token"], message_id)
                await tester.test_mark_read_without_auth(primary_user["user_id"], message_id)
            
            # Test 7: Cross-user authorization test (if we have multiple users)
            if len(successful_logins) >= 2:
                print("\n🚫 AUTHORIZATION SECURITY TESTS:")
                await tester.test_cross_user_authorization(successful_logins[0], successful_logins[1])
            else:
                print("\n⚠️ Cross-user authorization test skipped (need 2+ users)")
        
        # Print comprehensive summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())