#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - ADMIN PANEL COMPLETED TRANSACTIONS TAB TESTING
Testing the "Completed Transactions" tab accessibility issue in the Admin Panel

SPECIFIC TESTS REQUESTED (Review Request):
I need to investigate why the "Completed Transactions" tab is not accessible in the Admin Panel.

**CONTEXT**: The testing agent couldn't locate the "Completed Transactions" tab in the Admin Panel. 
According to the permissions system, both Admin and Admin-Manager roles should have this permission.

**TEST REQUIREMENTS**:
1. **Test Admin Login**: Login with admin credentials and verify admin panel access
2. **Test Admin Permissions**: Verify that admin users have the correct permissions (specifically `canAccessUserManagement`)
3. **Test Backend API**: Check if the backend API endpoint `/api/admin/completed-transactions` exists and works
4. **Test Tab Filtering Logic**: Verify the tab filtering logic in AdminPanel.js to see why the "Completed" tab might not be visible

**ADMIN CREDENTIALS TO USE**:
- admin@cataloro.com / password123 or admin@cataloro.com / admin123
- sash_admin / standard admin password

**EXPECTED RESULTS**:
- Admin login should work and return proper admin role
- Admin users should have `canAccessUserManagement` permission
- Backend API endpoint `/api/admin/completed-transactions` should be accessible to admin users
- The "Completed Transactions" tab should be visible in the Admin Panel

**FOCUS**: This is critical as it's preventing one of the 5 implemented fixes from being verified as working.

GOAL: Identify why the "Completed Transactions" tab is not accessible and provide detailed diagnostics.
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://marketplace-fix-9.preview.emergentagent.com/api"

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

    async def test_admin_permissions(self, token, user_id, user_data):
        """Test admin user permissions to verify canAccessUserManagement permission"""
        start_time = datetime.now()
        
        try:
            # Check user role and permissions from login response
            user_role = user_data.get('user_role', 'Unknown')
            role = user_data.get('role', 'Unknown')
            
            # Determine if user should have canAccessUserManagement permission
            should_have_permission = (
                user_role in ['Admin', 'Admin-Manager'] or 
                role == 'admin'
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if should_have_permission:
                self.log_result(
                    "Admin Permissions Check", 
                    True, 
                    f"✅ ADMIN PERMISSIONS CONFIRMED: User has role '{user_role}' (legacy: '{role}') which should grant canAccessUserManagement permission",
                    response_time
                )
                return {
                    'success': True, 
                    'user_role': user_role,
                    'legacy_role': role,
                    'should_have_permission': True,
                    'permission_name': 'canAccessUserManagement'
                }
            else:
                self.log_result(
                    "Admin Permissions Check", 
                    False, 
                    f"❌ INSUFFICIENT PERMISSIONS: User has role '{user_role}' (legacy: '{role}') which should NOT grant canAccessUserManagement permission",
                    response_time
                )
                return {
                    'success': False, 
                    'user_role': user_role,
                    'legacy_role': role,
                    'should_have_permission': False,
                    'error': 'User does not have admin permissions'
                }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Admin Permissions Check", 
                False, 
                f"❌ PERMISSIONS CHECK EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_public_profile_verification_status(self, token, user_id, username, user_email):
        """Test GET /api/user/{user_id}/public-profile endpoint for is_verified field"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/user/{user_id}/public-profile"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response has the expected structure
                    profile_data = data.get('profile', {})
                    stats = data.get('stats', {})
                    is_verified = data.get('is_verified')
                    verified = data.get('verified')
                    
                    # Check for verification status in different possible locations
                    verification_found = False
                    verification_status = None
                    verification_location = None
                    
                    if is_verified is not None:
                        verification_found = True
                        verification_status = is_verified
                        verification_location = "root.is_verified"
                    elif verified is not None:
                        verification_found = True
                        verification_status = verified
                        verification_location = "root.verified"
                    elif profile_data.get('is_verified') is not None:
                        verification_found = True
                        verification_status = profile_data.get('is_verified')
                        verification_location = "profile.is_verified"
                    elif profile_data.get('verified') is not None:
                        verification_found = True
                        verification_status = profile_data.get('verified')
                        verification_location = "profile.verified"
                    
                    if verification_found:
                        self.log_result(
                            f"Public Profile Verification - {username}", 
                            True, 
                            f"✅ VERIFICATION STATUS FOUND: {verification_location} = {verification_status} for user {username} ({user_email})",
                            response_time
                        )
                        return {
                            'success': True, 
                            'is_verified': verification_status,
                            'verification_location': verification_location,
                            'profile': profile_data,
                            'stats': stats,
                            'user_email': user_email,
                            'username': username,
                            'full_response': data
                        }
                    else:
                        self.log_result(
                            f"Public Profile Verification - {username}", 
                            False, 
                            f"❌ VERIFICATION STATUS MISSING: No is_verified or verified field found in response for user {username} ({user_email}). Response keys: {list(data.keys())}",
                            response_time
                        )
                        return {
                            'success': False, 
                            'is_verified': None,
                            'verification_location': None,
                            'profile': profile_data,
                            'stats': stats,
                            'error': 'Verification status field not found',
                            'response_keys': list(data.keys()),
                            'full_response': data
                        }
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Public Profile Verification - {username}", 
                        False, 
                        f"❌ PUBLIC PROFILE ENDPOINT FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text, 'status_code': response.status}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Public Profile Verification - {username}", 
                False, 
                f"❌ PUBLIC PROFILE EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_user_profile_verification_status(self, token, user_id, username, user_email):
        """Test GET /api/auth/profile/{user_id} endpoint for verification status in user profile"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/auth/profile/{user_id}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for verification status in user profile
                    is_verified = data.get('is_verified')
                    verified = data.get('verified')
                    
                    verification_found = False
                    verification_status = None
                    verification_location = None
                    
                    if is_verified is not None:
                        verification_found = True
                        verification_status = is_verified
                        verification_location = "is_verified"
                    elif verified is not None:
                        verification_found = True
                        verification_status = verified
                        verification_location = "verified"
                    
                    if verification_found:
                        self.log_result(
                            f"User Profile Verification - {username}", 
                            True, 
                            f"✅ USER PROFILE VERIFICATION FOUND: {verification_location} = {verification_status} for user {username} ({user_email})",
                            response_time
                        )
                        return {
                            'success': True, 
                            'is_verified': verification_status,
                            'verification_location': verification_location,
                            'user_data': data,
                            'user_email': user_email,
                            'username': username
                        }
                    else:
                        self.log_result(
                            f"User Profile Verification - {username}", 
                            False, 
                            f"❌ USER PROFILE VERIFICATION MISSING: No verification field found for user {username} ({user_email}). Available fields: {list(data.keys())}",
                            response_time
                        )
                        return {
                            'success': False, 
                            'is_verified': None,
                            'verification_location': None,
                            'error': 'Verification status field not found in user profile',
                            'available_fields': list(data.keys()),
                            'user_data': data
                        }
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"User Profile Verification - {username}", 
                        False, 
                        f"❌ USER PROFILE ENDPOINT FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text, 'status_code': response.status}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"User Profile Verification - {username}", 
                False, 
                f"❌ USER PROFILE EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_specific_user_verification(self, username_or_id):
        """Test verification status for a specific user by username or ID"""
        start_time = datetime.now()
        
        try:
            # Try to get public profile without authentication first
            url = f"{BACKEND_URL}/user/{username_or_id}/public-profile"
            
            async with self.session.get(url) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for verification status
                    is_verified = data.get('is_verified')
                    verified = data.get('verified')
                    profile_data = data.get('profile', {})
                    
                    verification_found = False
                    verification_status = None
                    verification_location = None
                    
                    if is_verified is not None:
                        verification_found = True
                        verification_status = is_verified
                        verification_location = "root.is_verified"
                    elif verified is not None:
                        verification_found = True
                        verification_status = verified
                        verification_location = "root.verified"
                    elif profile_data.get('is_verified') is not None:
                        verification_found = True
                        verification_status = profile_data.get('is_verified')
                        verification_location = "profile.is_verified"
                    elif profile_data.get('verified') is not None:
                        verification_found = True
                        verification_status = profile_data.get('verified')
                        verification_location = "profile.verified"
                    
                    if verification_found:
                        self.log_result(
                            f"Specific User Verification - {username_or_id}", 
                            True, 
                            f"✅ VERIFICATION STATUS FOUND: {verification_location} = {verification_status} for user {username_or_id}",
                            response_time
                        )
                        return {
                            'success': True, 
                            'is_verified': verification_status,
                            'verification_location': verification_location,
                            'profile': profile_data,
                            'username_or_id': username_or_id,
                            'full_response': data
                        }
                    else:
                        self.log_result(
                            f"Specific User Verification - {username_or_id}", 
                            False, 
                            f"❌ VERIFICATION STATUS MISSING: No verification field found for user {username_or_id}. Response keys: {list(data.keys())}",
                            response_time
                        )
                        return {
                            'success': False, 
                            'is_verified': None,
                            'verification_location': None,
                            'error': 'Verification status field not found',
                            'response_keys': list(data.keys()),
                            'full_response': data
                        }
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Specific User Verification - {username_or_id}", 
                        False, 
                        f"❌ PUBLIC PROFILE FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text, 'status_code': response.status}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Specific User Verification - {username_or_id}", 
                False, 
                f"❌ SPECIFIC USER EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_mark_notification_as_read(self, token, user_id, notification_id):
        """Test PUT /api/user/{user_id}/notifications/{notification_id}/read endpoint"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/user/{user_id}/notifications/{notification_id}/read"
            
            async with self.session.put(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("message"):
                        self.log_result(
                            "Mark Notification as Read", 
                            True, 
                            f"✅ MARK AS READ WORKING: {data.get('message')}",
                            response_time
                        )
                        return {'success': True, 'marked_read': True}
                    else:
                        self.log_result(
                            "Mark Notification as Read", 
                            False, 
                            f"❌ UNEXPECTED RESPONSE: {data}",
                            response_time
                        )
                        return {'success': False, 'error': 'Unexpected response'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Mark Notification as Read", 
                        False, 
                        f"❌ MARK AS READ FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Mark Notification as Read", 
                False, 
                f"❌ MARK AS READ EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_notification_types_support(self, notifications_result):
        """Test that the notification system supports all required notification types for routing"""
        try:
            if not notifications_result.get('success'):
                self.log_result(
                    "Notification Types Support", 
                    False, 
                    "❌ PREREQUISITE FAILED: Notifications endpoint failed, cannot test types support"
                )
                return {'success': False, 'error': 'Prerequisite notifications endpoint failed'}
            
            # Extract notification types from the results
            found_types = set(notifications_result.get('notification_types', []))
            routing_types_found = set(notifications_result.get('routing_types_found', []))
            
            # Required notification types for routing
            required_routing_types = {
                'tender_accepted',
                'transaction_completed', 
                'transaction_marked_completed',
                'transaction_fully_completed',
                'new_tender_offer',
                'tender_offer',
                'new_user_registration'
            }
            
            # Check which types are supported
            supported_types = routing_types_found.intersection(required_routing_types)
            missing_types = required_routing_types - routing_types_found
            
            # Analyze type support
            type_checks = []
            
            # Check 1: Basic notification types present
            if found_types:
                type_checks.append(f"✅ Notification types found: {list(found_types)}")
            else:
                type_checks.append("❌ No notification types found")
            
            # Check 2: Routing-specific types support
            if supported_types:
                type_checks.append(f"✅ Routing types supported: {list(supported_types)}")
            else:
                type_checks.append("❌ No routing types supported")
            
            # Check 3: Missing types analysis
            if missing_types:
                type_checks.append(f"⚠️ Missing routing types: {list(missing_types)}")
            else:
                type_checks.append("✅ All routing types supported")
            
            # Check 4: Admin-specific types (new_user_registration)
            if 'new_user_registration' in supported_types:
                type_checks.append("✅ Admin notification type supported")
            else:
                type_checks.append("⚠️ Admin notification type not found (may require admin user)")
            
            # Determine overall success
            # Success if we have at least some routing types supported
            success = len(supported_types) > 0
            
            self.log_result(
                "Notification Types Support", 
                success, 
                f"{'✅ TYPES SUPPORTED' if success else '❌ TYPES NOT SUPPORTED'}: {'; '.join(type_checks)}",
            )
            
            return {
                'success': success,
                'found_types': list(found_types),
                'supported_routing_types': list(supported_types),
                'missing_routing_types': list(missing_types),
                'type_checks': type_checks,
                'routing_ready': success
            }
            
        except Exception as e:
            self.log_result(
                "Notification Types Support", 
                False, 
                f"❌ TYPES SUPPORT EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}

    async def create_test_notification(self, token, user_id, notification_type="tender_accepted"):
        """Create a test notification for testing purposes"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/user/{user_id}/notifications"
            
            notification_data = {
                "user_id": user_id,
                "title": f"Test {notification_type.replace('_', ' ').title()}",
                "message": f"This is a test notification of type {notification_type} for routing verification",
                "type": notification_type,
                "read": False
            }
            
            async with self.session.post(url, headers=headers, json=notification_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status in [200, 201]:
                    data = await response.json()
                    notification_id = data.get('notification', {}).get('id') or data.get('id')
                    
                    if notification_id:
                        self.log_result(
                            "Create Test Notification", 
                            True, 
                            f"✅ TEST NOTIFICATION CREATED: Created {notification_type} notification with ID {notification_id}",
                            response_time
                        )
                        return {'success': True, 'notification_id': notification_id, 'type': notification_type}
                    else:
                        self.log_result(
                            "Create Test Notification", 
                            False, 
                            f"❌ NO NOTIFICATION ID: Response missing notification ID: {data}",
                            response_time
                        )
                        return {'success': False, 'error': 'No notification ID in response'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Test Notification", 
                        False, 
                        f"❌ CREATION FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Create Test Notification", 
                False, 
                f"❌ CREATION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def run_verification_status_tests(self):
        """Run comprehensive verification status tests"""
        print("🚀 CATALORO VERIFICATION STATUS BACKEND TESTING")
        print("=" * 80)
        print()
        
        # Test with both demo user and admin
        test_users = [
            ("demo_user@cataloro.com", "demo123", "Demo User"),
            ("admin@cataloro.com", "admin123", "Admin User")
        ]
        
        # Also test specific users mentioned in the request
        specific_users = ["admin_user_1", "sash_admin"]
        
        all_results = {}
        
        # Test authenticated users
        for email, password, user_type in test_users:
            print(f"🔐 Testing with {user_type} ({email})")
            print("-" * 50)
            
            # Step 1: Login
            token, user_id, user = await self.test_login_and_get_token(email, password)
            if not token:
                print(f"❌ Login failed for {user_type}, skipping tests")
                continue
            
            user_results = {}
            username = user.get('username', 'unknown')
            
            # Step 2: Test public profile verification status
            print(f"🔍 Testing public profile verification status for {user_type}...")
            public_profile_result = await self.test_public_profile_verification_status(token, user_id, username, email)
            user_results['public_profile_verification'] = public_profile_result
            
            # Step 3: Test user profile verification status
            print(f"👤 Testing user profile verification status for {user_type}...")
            user_profile_result = await self.test_user_profile_verification_status(token, user_id, username, email)
            user_results['user_profile_verification'] = user_profile_result
            
            all_results[user_type] = user_results
            print()
        
        # Test specific users without authentication
        print("🎯 Testing specific users mentioned in request...")
        print("-" * 50)
        
        for username in specific_users:
            print(f"🔍 Testing verification status for {username}...")
            specific_result = await self.test_specific_user_verification(username)
            all_results[f"Specific User - {username}"] = {'public_profile_verification': specific_result}
            print()
        
        # Generate summary
        self.generate_verification_status_summary(all_results)
        
        return all_results

    def generate_verification_status_summary(self, all_results):
        """Generate comprehensive summary of verification status testing"""
        print("📊 VERIFICATION STATUS TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        verification_found_count = 0
        verified_users_count = 0
        
        for user_type, results in all_results.items():
            print(f"\n🔍 {user_type} Results:")
            print("-" * 30)
            
            for test_name, result in results.items():
                total_tests += 1
                if result.get('success'):
                    passed_tests += 1
                    status = "✅ PASS"
                    
                    # Check if verification status was found
                    if result.get('is_verified') is not None:
                        verification_found_count += 1
                        if result.get('is_verified'):
                            verified_users_count += 1
                else:
                    status = "❌ FAIL"
                
                print(f"  {status}: {test_name.replace('_', ' ').title()}")
                
                # Add specific details for verification tests
                if result.get('success'):
                    is_verified = result.get('is_verified')
                    verification_location = result.get('verification_location', 'unknown')
                    username = result.get('username', 'unknown')
                    
                    print(f"    🔍 Verification Status: {is_verified}")
                    print(f"    📍 Found in: {verification_location}")
                    print(f"    👤 Username: {username}")
                    
                    if is_verified:
                        print(f"    ✅ User is VERIFIED")
                    else:
                        print(f"    ❌ User is NOT VERIFIED")
                else:
                    error = result.get('error', 'Unknown error')
                    status_code = result.get('status_code', 'N/A')
                    print(f"    ❌ Error: {error}")
                    if status_code != 'N/A':
                        print(f"    🔢 Status Code: {status_code}")
                    
                    # Show available fields if verification field is missing
                    if 'response_keys' in result:
                        print(f"    🔑 Available fields: {result['response_keys']}")
                    elif 'available_fields' in result:
                        print(f"    🔑 Available fields: {result['available_fields']}")
        
        # Overall summary
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   Verification Field Found: {verification_found_count}/{total_tests}")
        print(f"   Verified Users Found: {verified_users_count}/{verification_found_count if verification_found_count > 0 else 1}")
        
        # Key findings
        print(f"\n🔑 KEY FINDINGS:")
        
        # Check if verification status is being returned
        if verification_found_count > 0:
            print(f"   ✅ Verification status field found in {verification_found_count} out of {total_tests} tests")
            
            if verified_users_count > 0:
                print(f"   ✅ Found {verified_users_count} verified users")
            else:
                print(f"   ⚠️ No verified users found - all users have is_verified: false")
        else:
            print(f"   ❌ Verification status field NOT FOUND in any API responses")
            print(f"   🔧 ISSUE: The is_verified field is missing from public profile endpoints")
        
        # Check specific users mentioned in request
        admin_user_1_result = all_results.get('Specific User - admin_user_1', {}).get('public_profile_verification', {})
        sash_admin_result = all_results.get('Specific User - sash_admin', {}).get('public_profile_verification', {})
        
        print(f"\n🎯 SPECIFIC USERS REQUESTED:")
        
        if admin_user_1_result.get('success'):
            is_verified = admin_user_1_result.get('is_verified')
            print(f"   👤 admin_user_1: {'✅ VERIFIED' if is_verified else '❌ NOT VERIFIED'} (is_verified: {is_verified})")
        else:
            error = admin_user_1_result.get('error', 'Unknown error')
            print(f"   👤 admin_user_1: ❌ FAILED - {error}")
        
        if sash_admin_result.get('success'):
            is_verified = sash_admin_result.get('is_verified')
            print(f"   👤 sash_admin: {'✅ VERIFIED' if is_verified else '❌ NOT VERIFIED'} (is_verified: {is_verified})")
        else:
            error = sash_admin_result.get('error', 'Unknown error')
            print(f"   👤 sash_admin: ❌ FAILED - {error}")
        
        # Root cause analysis
        print(f"\n🔧 ROOT CAUSE ANALYSIS:")
        
        if verification_found_count == 0:
            print("   ❌ CRITICAL ISSUE: is_verified field is completely missing from API responses")
            print("   🔧 SOLUTION NEEDED: Backend needs to include is_verified field in public profile endpoint")
            print("   📝 CHECK: Verify if users have 'verified' field in database and map it to 'is_verified' in API")
        elif verified_users_count == 0:
            print("   ⚠️ ISSUE: is_verified field exists but all users are marked as not verified")
            print("   🔧 SOLUTION NEEDED: Check if admin users should have verified status in database")
            print("   📝 CHECK: Verify admin users like 'admin_user_1' and 'sash_admin' have verified: true in database")
        else:
            print("   ✅ VERIFICATION SYSTEM WORKING: is_verified field found and some users are verified")
            print("   🎉 FRONTEND ISSUE: The problem might be in frontend badge display logic")
        
        print(f"\n🎉 VERIFICATION STATUS TESTING COMPLETED!")
        print("=" * 80)

async def main():
    """Main test execution function"""
    async with BackendTester() as tester:
        results = await tester.run_verification_status_tests()
        return results

if __name__ == "__main__":
    # Run the tests
    try:
        results = asyncio.run(main())
        print("\n✅ All tests completed successfully!")
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()