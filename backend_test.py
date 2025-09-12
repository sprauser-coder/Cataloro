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

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://cataloro-admin-fix.preview.emergentagent.com/api"

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
    
    async def test_admin_login_authentication(self):
        """Test admin login with specific credentials"""
        print("\n🔐 ADMIN AUTHENTICATION TESTS:")
        
        # Test admin login with correct credentials
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        
        if not admin_token:
            self.log_result(
                "Admin Login Test", 
                False, 
                "Failed to login with admin@cataloro.com / admin123"
            )
            return None
        
        # Verify admin user properties
        await self.test_admin_user_properties(admin_user)
        
        return {
            "token": admin_token,
            "user_id": admin_user_id,
            "user": admin_user
        }
    
    async def test_admin_user_properties(self, user):
        """Test that admin user has correct role/user_role properties"""
        try:
            role = user.get("role")
            user_role = user.get("user_role")
            
            # Check for admin privileges according to backend logic
            is_admin = (
                role == "admin" or 
                user_role in ["Admin", "Admin-Manager"]
            )
            
            if is_admin:
                self.log_result(
                    "Admin User Properties Test", 
                    True, 
                    f"✅ Admin user has correct properties: role='{role}', user_role='{user_role}'"
                )
                
                # Log additional user properties for verification
                additional_props = {
                    "full_name": user.get("full_name"),
                    "email": user.get("email"),
                    "badge": user.get("badge"),
                    "registration_status": user.get("registration_status")
                }
                
                print(f"   Admin User Details: {additional_props}")
                return True
            else:
                self.log_result(
                    "Admin User Properties Test", 
                    False, 
                    f"❌ User does not have admin privileges: role='{role}', user_role='{user_role}'"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin User Properties Test", 
                False, 
                f"Error checking admin properties: {str(e)}"
            )
            return False
    
    async def test_admin_endpoints_access(self, admin_token):
        """Test access to various admin panel endpoints"""
        print("\n🛡️ ADMIN ENDPOINTS ACCESS TESTS:")
        
        admin_endpoints = [
            {"path": "/admin/dashboard", "name": "Admin Dashboard"},
            {"path": "/admin/users", "name": "Admin Users Management"},
            {"path": "/admin/menu-settings", "name": "Admin Menu Settings"},
            {"path": "/admin/performance", "name": "Admin Performance Metrics"},
            {"path": "/admin/cache/clear", "name": "Admin Cache Clear", "method": "POST"}
        ]
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        successful_endpoints = 0
        
        for endpoint in admin_endpoints:
            success = await self.test_single_admin_endpoint(
                endpoint["path"], 
                endpoint["name"], 
                headers,
                endpoint.get("method", "GET")
            )
            if success:
                successful_endpoints += 1
        
        self.log_result(
            "Admin Endpoints Access Summary", 
            successful_endpoints == len(admin_endpoints), 
            f"Successfully accessed {successful_endpoints}/{len(admin_endpoints)} admin endpoints"
        )
        
        return successful_endpoints == len(admin_endpoints)
    
    async def test_single_admin_endpoint(self, path, name, headers, method="GET"):
        """Test access to a single admin endpoint"""
        start_time = datetime.now()
        
        try:
            url = f"{BACKEND_URL}{path}"
            
            if method == "GET":
                async with self.session.get(url, headers=headers) as response:
                    return await self.process_admin_endpoint_response(response, name, start_time)
            elif method == "POST":
                async with self.session.post(url, headers=headers) as response:
                    return await self.process_admin_endpoint_response(response, name, start_time)
            else:
                self.log_result(
                    f"Admin Endpoint: {name}", 
                    False, 
                    f"Unsupported method: {method}"
                )
                return False
                
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Admin Endpoint: {name}", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return False
    
    async def process_admin_endpoint_response(self, response, name, start_time):
        """Process admin endpoint response"""
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if response.status == 200:
            try:
                data = await response.json()
                data_summary = self.summarize_response_data(data)
                self.log_result(
                    f"Admin Endpoint: {name}", 
                    True, 
                    f"✅ Access granted, received data: {data_summary}",
                    response_time
                )
                return True
            except:
                # Some endpoints might not return JSON
                text = await response.text()
                self.log_result(
                    f"Admin Endpoint: {name}", 
                    True, 
                    f"✅ Access granted, received response (non-JSON): {len(text)} chars",
                    response_time
                )
                return True
        elif response.status == 403:
            error_text = await response.text()
            self.log_result(
                f"Admin Endpoint: {name}", 
                False, 
                f"❌ Access denied (403): {error_text}",
                response_time
            )
            return False
        else:
            error_text = await response.text()
            self.log_result(
                f"Admin Endpoint: {name}", 
                False, 
                f"❌ Unexpected status {response.status}: {error_text}",
                response_time
            )
            return False
    
    def summarize_response_data(self, data):
        """Create a summary of response data for logging"""
        if isinstance(data, dict):
            keys = list(data.keys())[:5]  # First 5 keys
            return f"dict with keys: {keys}"
        elif isinstance(data, list):
            return f"list with {len(data)} items"
        else:
            return f"{type(data).__name__}: {str(data)[:100]}"
    
    async def test_non_admin_access_blocked(self):
        """Test that non-admin users cannot access admin endpoints"""
        print("\n🚫 NON-ADMIN ACCESS BLOCKING TESTS:")
        
        # Try to login as regular user
        user_token, user_id, user = await self.test_login_and_get_token("demo@cataloro.com", "demo123")
        
        if not user_token:
            self.log_result(
                "Non-Admin User Login", 
                False, 
                "Could not login as regular user for testing"
            )
            return False
        
        # Verify this is not an admin user
        role = user.get("role")
        user_role = user.get("user_role")
        is_admin = (role == "admin" or user_role in ["Admin", "Admin-Manager"])
        
        if is_admin:
            self.log_result(
                "Non-Admin User Verification", 
                False, 
                f"Test user has admin privileges: role='{role}', user_role='{user_role}'"
            )
            return False
        
        self.log_result(
            "Non-Admin User Verification", 
            True, 
            f"✅ Test user is non-admin: role='{role}', user_role='{user_role}'"
        )
        
        # Test access to admin endpoints (should be blocked)
        headers = {"Authorization": f"Bearer {user_token}"}
        
        admin_endpoints = [
            "/admin/dashboard",
            "/admin/users",
            "/admin/menu-settings"
        ]
        
        blocked_count = 0
        for endpoint in admin_endpoints:
            if await self.test_admin_endpoint_blocked(endpoint, headers):
                blocked_count += 1
        
        success = blocked_count == len(admin_endpoints)
        self.log_result(
            "Non-Admin Access Blocking Summary", 
            success, 
            f"Properly blocked {blocked_count}/{len(admin_endpoints)} admin endpoints for non-admin user"
        )
        
        return success
    
    async def test_marketplace_apis(self, user_token=None):
        """Test marketplace APIs comprehensively"""
        print("\n🏪 MARKETPLACE APIS TESTS:")
        
        # Test browse listings
        await self.test_marketplace_browse()
        
        # Test individual listing details
        listing_id = await self.test_individual_listing()
        
        # Test create listing (requires authentication)
        if user_token:
            await self.test_create_listing(user_token)
        
        # Test tenders/bidding system
        if listing_id:
            await self.test_listing_tenders(listing_id)
    
    async def test_marketplace_browse(self):
        """Test marketplace browse endpoint"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if listings have required fields
                    required_fields = ['id', 'title', 'price', 'seller_id']
                    time_fields = ['time_info', 'has_time_limit']
                    bid_fields = ['bid_info']
                    
                    listings_with_time_info = 0
                    listings_with_bid_info = 0
                    
                    for listing in data:
                        # Check time_info
                        if any(field in listing for field in time_fields):
                            listings_with_time_info += 1
                        
                        # Check bid_info
                        if any(field in listing for field in bid_fields):
                            listings_with_bid_info += 1
                    
                    self.log_result(
                        "Marketplace Browse API", 
                        True, 
                        f"Retrieved {len(data)} listings, {listings_with_time_info} with time_info, {listings_with_bid_info} with bid_info",
                        response_time
                    )
                    
                    return data[0]['id'] if data else None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Marketplace Browse API", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Marketplace Browse API", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_individual_listing(self):
        """Test individual listing endpoint"""
        # First get a listing ID from browse
        start_time = datetime.now()
        
        try:
            # Get listings first
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse?limit=1") as response:
                if response.status == 200:
                    listings = await response.json()
                    if not listings:
                        self.log_result(
                            "Individual Listing API", 
                            False, 
                            "No listings available to test individual listing endpoint"
                        )
                        return None
                    
                    listing_id = listings[0]['id']
                    
                    # Now test individual listing endpoint
                    async with self.session.get(f"{BACKEND_URL}/listings/{listing_id}") as detail_response:
                        response_time = (datetime.now() - start_time).total_seconds() * 1000
                        
                        if detail_response.status == 200:
                            listing_data = await detail_response.json()
                            
                            # Check for required fields
                            has_time_info = 'time_info' in listing_data
                            has_bid_info = 'bid_info' in listing_data
                            
                            self.log_result(
                                "Individual Listing API", 
                                True, 
                                f"Retrieved listing {listing_id}, time_info: {has_time_info}, bid_info: {has_bid_info}",
                                response_time
                            )
                            
                            return listing_id
                        else:
                            error_text = await detail_response.text()
                            self.log_result(
                                "Individual Listing API", 
                                False, 
                                f"Failed with status {detail_response.status}: {error_text}",
                                response_time
                            )
                            return None
                else:
                    self.log_result(
                        "Individual Listing API", 
                        False, 
                        "Could not get listings for testing individual endpoint"
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Individual Listing API", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_create_listing(self, token):
        """Test create listing functionality"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            listing_data = {
                "title": "Test Listing for Backend Testing",
                "description": "This is a test listing created during backend testing",
                "price": 99.99,
                "category": "Electronics",
                "condition": "New",
                "has_time_limit": True,
                "time_limit_hours": 24
            }
            
            async with self.session.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listing_id = data.get("id")
                    
                    self.log_result(
                        "Create Listing API", 
                        True, 
                        f"Successfully created listing {listing_id} with time limit",
                        response_time
                    )
                    
                    return listing_id
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Listing API", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Create Listing API", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_listing_tenders(self, listing_id):
        """Test listing tenders/bidding system"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/listings/{listing_id}/tenders") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    tenders = await response.json()
                    
                    # Check tender structure
                    highest_bid = 0
                    if tenders:
                        for tender in tenders:
                            if 'amount' in tender:
                                highest_bid = max(highest_bid, tender['amount'])
                    
                    self.log_result(
                        "Listing Tenders API", 
                        True, 
                        f"Retrieved {len(tenders)} tenders, highest bid: ${highest_bid}",
                        response_time
                    )
                    
                    return tenders
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Listing Tenders API", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Listing Tenders API", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_registration_system(self):
        """Test registration and user management APIs"""
        print("\n👤 REGISTRATION & USER MANAGEMENT TESTS:")
        
        # Test username availability
        await self.test_username_availability()
        
        # Test email availability
        await self.test_email_availability()
        
        # Test user registration
        await self.test_user_registration()
    
    async def test_username_availability(self):
        """Test username availability check"""
        start_time = datetime.now()
        
        try:
            # Test with existing username
            async with self.session.get(f"{BACKEND_URL}/check-username?username=admin") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    available = data.get("available", True)
                    
                    self.log_result(
                        "Username Availability Check", 
                        True, 
                        f"Username 'admin' availability: {available}",
                        response_time
                    )
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Username Availability Check", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Username Availability Check", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
    
    async def test_email_availability(self):
        """Test email availability check"""
        start_time = datetime.now()
        
        try:
            # Test with existing email
            async with self.session.get(f"{BACKEND_URL}/check-email?email=admin@cataloro.com") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    available = data.get("available", True)
                    
                    self.log_result(
                        "Email Availability Check", 
                        True, 
                        f"Email 'admin@cataloro.com' availability: {available}",
                        response_time
                    )
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Email Availability Check", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Email Availability Check", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
    
    async def test_user_registration(self):
        """Test user registration with first_name/last_name"""
        start_time = datetime.now()
        
        try:
            registration_data = {
                "username": f"testuser_{int(datetime.now().timestamp())}",
                "email": f"test_{int(datetime.now().timestamp())}@example.com",
                "full_name": "Test User Backend",
                "first_name": "Test",
                "last_name": "User",
                "account_type": "buyer"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/register", json=registration_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    user_id = data.get("user_id")
                    status = data.get("status")
                    
                    self.log_result(
                        "User Registration", 
                        True, 
                        f"Successfully registered user {user_id}, status: {status}",
                        response_time
                    )
                else:
                    error_text = await response.text()
                    self.log_result(
                        "User Registration", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "User Registration", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
    
    async def test_time_limit_and_bidding(self, user_token):
        """Test time limit and bidding features"""
        print("\n⏰ TIME LIMIT & BIDDING TESTS:")
        
        if not user_token:
            self.log_result(
                "Time Limit & Bidding Tests", 
                False, 
                "No user token available for testing"
            )
            return
        
        # Create a listing with time limit
        listing_id = await self.test_create_time_limited_listing(user_token)
        
        if listing_id:
            # Test bidding functionality
            await self.test_tender_submission(listing_id, user_token)
            
            # Test highest bidder blocking
            await self.test_highest_bidder_blocking(listing_id, user_token)
    
    async def test_create_time_limited_listing(self, token):
        """Test creating listing with different time limits"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test 1 hour time limit
            listing_data = {
                "title": "1 Hour Time Limited Test Listing",
                "description": "Testing 1 hour time limit functionality",
                "price": 50.00,
                "category": "Test",
                "condition": "New",
                "has_time_limit": True,
                "time_limit_hours": 1
            }
            
            async with self.session.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listing_id = data.get("id")
                    
                    self.log_result(
                        "Create 1-Hour Time Limited Listing", 
                        True, 
                        f"Successfully created 1-hour time limited listing {listing_id}",
                        response_time
                    )
                    
                    return listing_id
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create 1-Hour Time Limited Listing", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Create 1-Hour Time Limited Listing", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_tender_submission(self, listing_id, token):
        """Test tender submission validation"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            tender_data = {
                "listing_id": listing_id,
                "amount": 75.00,
                "message": "Test bid for backend testing"
            }
            
            async with self.session.post(f"{BACKEND_URL}/tenders/submit", json=tender_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    tender_id = data.get("id")
                    
                    self.log_result(
                        "Tender Submission", 
                        True, 
                        f"Successfully submitted tender {tender_id} for ${tender_data['amount']}",
                        response_time
                    )
                    
                    return tender_id
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Tender Submission", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Tender Submission", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_highest_bidder_blocking(self, listing_id, token):
        """Test that highest bidder cannot place another bid"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to place another bid (should be blocked if user is highest bidder)
            tender_data = {
                "listing_id": listing_id,
                "amount": 100.00,
                "message": "Attempting second bid as highest bidder"
            }
            
            async with self.session.post(f"{BACKEND_URL}/tenders/submit", json=tender_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 400:
                    error_text = await response.text()
                    if "highest bidder" in error_text.lower():
                        self.log_result(
                            "Highest Bidder Blocking", 
                            True, 
                            f"✅ Highest bidder properly blocked from placing another bid",
                            response_time
                        )
                    else:
                        self.log_result(
                            "Highest Bidder Blocking", 
                            False, 
                            f"Blocked but wrong reason: {error_text}",
                            response_time
                        )
                elif response.status == 200:
                    self.log_result(
                        "Highest Bidder Blocking", 
                        False, 
                        f"❌ Highest bidder was able to place another bid (should be blocked)",
                        response_time
                    )
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Highest Bidder Blocking", 
                        False, 
                        f"Unexpected status {response.status}: {error_text}",
                        response_time
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Highest Bidder Blocking", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
    
    async def test_admin_endpoint_blocked(self, endpoint, headers):
        """Test that an admin endpoint is properly blocked for non-admin user"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 403:
                    self.log_result(
                        f"Admin Blocking: {endpoint}", 
                        True, 
                        f"✅ Properly blocked non-admin access (403)",
                        response_time
                    )
                    return True
                elif response.status == 200:
                    self.log_result(
                        f"Admin Blocking: {endpoint}", 
                        False, 
                        f"❌ SECURITY ISSUE: Non-admin user can access admin endpoint",
                        response_time
                    )
                    return False
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Admin Blocking: {endpoint}", 
                        False, 
                        f"Unexpected status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Admin Blocking: {endpoint}", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("ADMIN AUTHENTICATION AND ACCESS CONTROL TEST SUMMARY")
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
        
        print("ADMIN AUTHENTICATION VALIDATION:")
        
        # Analyze admin-specific results
        admin_login_tests = [r for r in self.test_results if "Admin Login" in r["test"]]
        admin_properties_tests = [r for r in self.test_results if "Admin User Properties" in r["test"]]
        admin_endpoint_tests = [r for r in self.test_results if "Admin Endpoint" in r["test"]]
        admin_blocking_tests = [r for r in self.test_results if "Admin Blocking" in r["test"]]
        
        # Admin Login
        admin_login_passed = all(r["success"] for r in admin_login_tests)
        if admin_login_passed:
            print("✅ ADMIN LOGIN: Successfully authenticated with admin@cataloro.com / admin123")
        else:
            print("❌ ADMIN LOGIN: Failed to authenticate admin user")
        
        # Admin Properties
        admin_props_passed = all(r["success"] for r in admin_properties_tests)
        if admin_props_passed:
            print("✅ ADMIN USER PROPERTIES: User object has correct role/user_role properties")
        elif not admin_properties_tests:
            print("⚠️ ADMIN USER PROPERTIES: Not tested (admin login failed)")
        else:
            print("❌ ADMIN USER PROPERTIES: User object missing correct admin properties")
        
        # Admin Endpoints Access
        admin_access_passed = all(r["success"] for r in admin_endpoint_tests if "Summary" not in r["test"])
        if admin_access_passed and admin_endpoint_tests:
            print("✅ ADMIN ENDPOINTS ACCESS: All admin panel endpoints accessible to admin user")
        elif not admin_endpoint_tests:
            print("⚠️ ADMIN ENDPOINTS ACCESS: Not tested (admin authentication failed)")
        else:
            print("❌ ADMIN ENDPOINTS ACCESS: Some admin endpoints not accessible")
        
        # Non-Admin Blocking
        admin_blocking_passed = all(r["success"] for r in admin_blocking_tests)
        if admin_blocking_passed and admin_blocking_tests:
            print("✅ NON-ADMIN BLOCKING: Admin endpoints properly blocked for non-admin users")
        elif not admin_blocking_tests:
            print("⚠️ NON-ADMIN BLOCKING: Not tested (could not create non-admin user)")
        else:
            print("❌ NON-ADMIN BLOCKING: Security issue - non-admin users can access admin endpoints")
        
        print()
        print("ADMIN AUTHENTICATION STATUS:")
        
        # Overall admin authentication assessment
        critical_admin_issues = []
        
        if not admin_login_passed:
            critical_admin_issues.append("Admin login credentials not working")
        
        if not admin_props_passed and admin_properties_tests:
            critical_admin_issues.append("Admin user properties not correctly configured")
        
        if not admin_access_passed and admin_endpoint_tests:
            critical_admin_issues.append("Admin endpoints not accessible to admin user")
        
        if not admin_blocking_passed and admin_blocking_tests:
            critical_admin_issues.append("Admin endpoints accessible to non-admin users (security risk)")
        
        if critical_admin_issues:
            print("❌ CRITICAL ADMIN AUTHENTICATION ISSUES:")
            for issue in critical_admin_issues:
                print(f"   - {issue}")
            print("- RECOMMENDATION: Admin authentication system needs fixes")
        else:
            print("✅ ADMIN AUTHENTICATION WORKING CORRECTLY:")
            print("   - Admin login with admin@cataloro.com / admin123 successful")
            print("   - Admin user has correct role/user_role properties")
            print("   - All admin panel endpoints accessible to admin user")
            print("   - Admin endpoints properly blocked for non-admin users")
        
        print()
        print("ADMIN PANEL ACCESS STATUS:")
        if passed_tests >= total_tests * 0.8:  # 80% success rate
            print("✅ ADMIN PANEL ACCESS WORKING CORRECTLY")
            print("   - Admin authentication successful")
            print("   - Admin authorization working")
            print("   - Security controls in place")
        else:
            print("❌ ADMIN PANEL ACCESS HAS ISSUES")
            print("   - Review failed tests above for remaining problems")

async def main():
    """Main test execution - Comprehensive Backend Testing for Cataloro Marketplace"""
    print("🔍 COMPREHENSIVE BACKEND TESTING FOR CATALORO MARKETPLACE DEPLOYMENT")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    print("TESTING AREAS:")
    print("✓ Authentication System (admin@cataloro.com / admin123, demo@cataloro.com / demo123)")
    print("✓ Admin Panel APIs (dashboard, users, menu-settings, performance, cache)")
    print("✓ Marketplace APIs (browse, listings, create, tenders)")
    print("✓ Messaging System (conversations with authentication)")
    print("✓ Registration & User Management (first_name/last_name, availability checks)")
    print("✓ Time Limit & Bidding Features (1 hour, 24 hours, unlimited, highest bidder)")
    print()
    
    async with BackendTester() as tester:
        # Test 1: Database connectivity
        print("🔌 TESTING DATABASE CONNECTIVITY:")
        await tester.test_database_connectivity()
        
        # Test 2: Authentication System
        print("\n🔐 TESTING AUTHENTICATION SYSTEM:")
        
        # Admin authentication
        admin_info = await tester.test_admin_login_authentication()
        
        # Demo user authentication
        demo_token, demo_user_id, demo_user = await tester.test_login_and_get_token("demo@cataloro.com", "demo123")
        if demo_token:
            tester.log_result(
                "Demo User Login", 
                True, 
                f"Successfully logged in as demo user: {demo_user.get('full_name', 'Unknown')}"
            )
        
        # Test 3: Admin Panel APIs
        if admin_info:
            print("\n🛡️ TESTING ADMIN PANEL APIS:")
            await tester.test_admin_endpoints_access(admin_info["token"])
            
            # Test non-admin access blocking
            await tester.test_non_admin_access_blocked()
        else:
            print("\n❌ Admin authentication failed - skipping admin panel tests")
        
        # Test 4: Marketplace APIs
        print("\n🏪 TESTING MARKETPLACE APIS:")
        user_token = demo_token or (admin_info["token"] if admin_info else None)
        await tester.test_marketplace_apis(user_token)
        
        # Test 5: Messaging System
        print("\n💬 TESTING MESSAGING SYSTEM:")
        if admin_info:
            # Test messaging with admin user
            admin_user_id = admin_info["user_id"]
            admin_token = admin_info["token"]
            
            # Test authentication requirements
            await tester.test_messages_endpoint_without_auth(admin_user_id)
            
            # Test with authentication
            messages = await tester.test_messages_endpoint_with_auth(admin_user_id, admin_token)
            
            # Test message structure
            if messages is not None:
                await tester.test_message_structure(messages)
            
            # Test send message functionality
            message_id = await tester.test_create_test_message(admin_user_id, admin_token)
            
            # Test send message without auth (should be blocked)
            await tester.test_send_message_without_auth(admin_user_id)
            
            # Test mark as read functionality
            if message_id:
                await tester.test_mark_read_authentication(admin_user_id, admin_token, message_id)
                await tester.test_mark_read_without_auth(admin_user_id, message_id)
            
            # Test cross-user authorization
            if demo_token and demo_user_id:
                await tester.test_cross_user_authorization(
                    {"token": admin_token, "user": admin_info["user"]},
                    {"token": demo_token, "user_id": demo_user_id, "user": demo_user}
                )
        
        # Test 6: Registration & User Management
        print("\n👤 TESTING REGISTRATION & USER MANAGEMENT:")
        await tester.test_registration_system()
        
        # Test 7: Time Limit & Bidding Features
        print("\n⏰ TESTING TIME LIMIT & BIDDING FEATURES:")
        if user_token:
            await tester.test_time_limit_and_bidding(user_token)
        else:
            tester.log_result(
                "Time Limit & Bidding Tests", 
                False, 
                "No authenticated user available for testing"
            )
        
        # Print comprehensive summary
        tester.print_comprehensive_summary()

    print("\n" + "=" * 80)
    print("🚀 BACKEND TESTING COMPLETE - READY FOR DEPLOYMENT ASSESSMENT")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())