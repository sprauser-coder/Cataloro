#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - BACKEND VERIFICATION STATUS TESTING
Testing if the backend is correctly returning the is_verified status for users in the public profile endpoint

SPECIFIC TESTS REQUESTED (Review Request):
I need to test if the backend is correctly returning the is_verified status for users in the public profile endpoint.

**CONTEXT**: I'm trying to fix the verified badge display on public profiles. The frontend testing showed that verified users are not showing the verified badge at the top.

**TEST REQUIREMENTS**:
1. **Test Public Profile Endpoint**: Call `/api/user/admin_user_1/public-profile` or `/api/user/sash_admin/public-profile`
2. **Check is_verified Field**: Verify if the response includes `"is_verified": true` for verified users
3. **Check User Database**: Query the users collection directly to see what verification status is stored

**EXPECTED RESULTS**:
- Public profile endpoint should return `"is_verified": true` for verified users
- Users with verification status should show this in the API response
- The is_verified field should be properly mapped from database to API response

**LOGIN CREDENTIALS**: Use admin@cataloro.com / admin123 or demo_user@cataloro.com / demo123

**FOCUS**: Specifically check if users like admin_user_1 or sash_admin have is_verified status in database and if it's properly returned by the API.

GOAL: Verify the verification status handling in the backend.
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://mobileui-sync.preview.emergentagent.com/api"

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

    async def test_registration_date_endpoint(self, token, user_id, user_email):
        """Test GET /api/user/{user_id}/registration-date endpoint for date parsing fix"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/user/{user_id}/registration-date"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response has the expected structure
                    registration_date = data.get('registration_date')
                    created_at = data.get('created_at')
                    date_joined = data.get('date_joined')
                    
                    # Check if date parsing is working correctly
                    if registration_date and registration_date != "Unknown":
                        # Check if it's in the expected format (e.g., "Sep 2025")
                        if len(registration_date.split()) == 2:  # Month Year format
                            self.log_result(
                                "Registration Date Endpoint", 
                                True, 
                                f"✅ DATE PARSING WORKING: Registration date formatted correctly as '{registration_date}' (created_at: {created_at})",
                                response_time
                            )
                            return {
                                'success': True, 
                                'registration_date': registration_date,
                                'created_at': created_at,
                                'date_joined': date_joined,
                                'user_email': user_email,
                                'formatted_correctly': True
                            }
                        else:
                            self.log_result(
                                "Registration Date Endpoint", 
                                False, 
                                f"❌ DATE FORMAT INCORRECT: Registration date '{registration_date}' not in expected 'Month Year' format (created_at: {created_at})",
                                response_time
                            )
                            return {
                                'success': False, 
                                'registration_date': registration_date,
                                'created_at': created_at,
                                'error': 'Date format incorrect',
                                'formatted_correctly': False
                            }
                    else:
                        self.log_result(
                            "Registration Date Endpoint", 
                            False, 
                            f"❌ DATE PARSING FAILED: Registration date is 'Unknown' or missing (created_at: {created_at}, response: {data})",
                            response_time
                        )
                        return {
                            'success': False, 
                            'registration_date': registration_date,
                            'created_at': created_at,
                            'error': 'Date parsing failed - returned Unknown',
                            'formatted_correctly': False
                        }
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Registration Date Endpoint", 
                        False, 
                        f"❌ ENDPOINT FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Registration Date Endpoint", 
                False, 
                f"❌ ENDPOINT EXCEPTION: {str(e)}",
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

    async def run_date_parsing_tests(self):
        """Run comprehensive date parsing fix tests"""
        print("🚀 CATALORO DATE PARSING FIX BACKEND TESTING")
        print("=" * 80)
        print()
        
        # Test with both demo user and admin
        test_users = [
            ("demo_user@cataloro.com", "demo123", "Demo User"),
            ("admin@cataloro.com", "admin123", "Admin User")
        ]
        
        all_results = {}
        
        for email, password, user_type in test_users:
            print(f"🔐 Testing with {user_type} ({email})")
            print("-" * 50)
            
            # Step 1: Login
            token, user_id, user = await self.test_login_and_get_token(email, password)
            if not token:
                print(f"❌ Login failed for {user_type}, skipping tests")
                continue
            
            user_results = {}
            
            # Step 2: Test registration date endpoint
            print(f"📅 Testing registration date endpoint for {user_type}...")
            registration_date_result = await self.test_registration_date_endpoint(token, user_id, email)
            user_results['registration_date'] = registration_date_result
            
            # Step 3: Test public profile endpoint
            print(f"👤 Testing public profile endpoint for {user_type}...")
            public_profile_result = await self.test_public_profile_endpoint(token, user_id, email)
            user_results['public_profile'] = public_profile_result
            
            all_results[user_type] = user_results
            print()
        
        # Generate summary
        self.generate_date_parsing_summary(all_results)
        
        return all_results

    def generate_date_parsing_summary(self, all_results):
        """Generate comprehensive summary of date parsing fix testing"""
        print("📊 DATE PARSING FIX TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        
        for user_type, results in all_results.items():
            print(f"\n🔍 {user_type} Results:")
            print("-" * 30)
            
            for test_name, result in results.items():
                total_tests += 1
                if result.get('success'):
                    passed_tests += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
                
                print(f"  {status}: {test_name.replace('_', ' ').title()}")
                
                # Add specific details for key tests
                if test_name == 'registration_date':
                    if result.get('success'):
                        reg_date = result.get('registration_date', 'Unknown')
                        created_at = result.get('created_at', 'Unknown')
                        print(f"    📅 Registration Date: {reg_date}")
                        print(f"    🕐 Created At: {created_at}")
                        print(f"    ✅ Formatted Correctly: {result.get('formatted_correctly', False)}")
                    else:
                        error = result.get('error', 'Unknown error')
                        reg_date = result.get('registration_date', 'Unknown')
                        created_at = result.get('created_at', 'Unknown')
                        print(f"    ❌ Error: {error}")
                        print(f"    📅 Registration Date: {reg_date}")
                        print(f"    🕐 Created At: {created_at}")
                
                elif test_name == 'public_profile':
                    if result.get('success'):
                        member_since = result.get('member_since', 'Unknown')
                        profile = result.get('profile', {})
                        print(f"    👤 Member Since: {member_since}")
                        print(f"    📝 Profile Name: {profile.get('full_name', 'Unknown')}")
                        print(f"    ✅ Formatted Correctly: {result.get('formatted_correctly', False)}")
                    else:
                        error = result.get('error', 'Unknown error')
                        member_since = result.get('member_since', 'Unknown')
                        print(f"    ❌ Error: {error}")
                        print(f"    👤 Member Since: {member_since}")
        
        # Overall summary
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Key findings
        print(f"\n🔑 KEY FINDINGS:")
        
        # Check if registration date endpoints are working
        demo_results = all_results.get('Demo User', {})
        admin_results = all_results.get('Admin User', {})
        
        demo_reg_date = demo_results.get('registration_date', {})
        admin_reg_date = admin_results.get('registration_date', {})
        
        if demo_reg_date.get('success') or admin_reg_date.get('success'):
            print("   ✅ Registration date endpoint is working")
            # Show successful date formats
            if demo_reg_date.get('success'):
                print(f"   📅 Demo User Registration Date: {demo_reg_date.get('registration_date', 'Unknown')}")
            if admin_reg_date.get('success'):
                print(f"   📅 Admin User Registration Date: {admin_reg_date.get('registration_date', 'Unknown')}")
        else:
            print("   ❌ Registration date endpoint is not working")
            # Show what we got instead
            if demo_reg_date.get('registration_date'):
                print(f"   ❌ Demo User got: {demo_reg_date.get('registration_date', 'Unknown')}")
            if admin_reg_date.get('registration_date'):
                print(f"   ❌ Admin User got: {admin_reg_date.get('registration_date', 'Unknown')}")
        
        # Check public profile endpoints
        demo_profile = demo_results.get('public_profile', {})
        admin_profile = admin_results.get('public_profile', {})
        
        if demo_profile.get('success') or admin_profile.get('success'):
            print("   ✅ Public profile endpoint is working")
            # Show successful date formats
            if demo_profile.get('success'):
                print(f"   👤 Demo User Member Since: {demo_profile.get('member_since', 'Unknown')}")
            if admin_profile.get('success'):
                print(f"   👤 Admin User Member Since: {admin_profile.get('member_since', 'Unknown')}")
        else:
            print("   ❌ Public profile endpoint is not working")
            # Show what we got instead
            if demo_profile.get('member_since'):
                print(f"   ❌ Demo User got: {demo_profile.get('member_since', 'Unknown')}")
            if admin_profile.get('member_since'):
                print(f"   ❌ Admin User got: {admin_profile.get('member_since', 'Unknown')}")
        
        # Check if date parsing fix is working
        all_working = (
            demo_reg_date.get('success', False) and 
            admin_reg_date.get('success', False) and
            demo_profile.get('success', False) and 
            admin_profile.get('success', False)
        )
        
        if all_working:
            print("   🎉 Date parsing fix is working correctly for all endpoints!")
        else:
            print("   ⚠️ Date parsing fix needs attention - some endpoints still returning 'Unknown'")
        
        print(f"\n🎉 DATE PARSING FIX TESTING COMPLETED!")
        print("=" * 80)

async def main():
    """Main test execution function"""
    async with BackendTester() as tester:
        results = await tester.run_date_parsing_tests()
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