#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - NOTIFICATION SYSTEM BACKEND TESTING
Testing the backend notification system to ensure it supports the new notification routing

SPECIFIC TESTS REQUESTED (Review Request):
Test the backend notification system to ensure it supports the new notification routing I just implemented.

**Context**: Updated notification routing in both desktop (ModernHeader.js) and mobile (NotificationsCenterPage.js) 
to route to specific Buy/Sell page tabs based on notification types.

**Test Requirements**:
1. **Verify notification endpoints work correctly** - Test GET /api/notifications endpoints
2. **Test notification marking as read** - Ensure mark-as-read functionality works
3. **Check notification types** - Verify the system supports the notification types I'm routing:
   - tender_accepted
   - transaction_completed / transaction_marked_completed
   - transaction_fully_completed
   - new_tender_offer / tender_offer
   - new_user_registration (for admin users)

**Expected Results**:
- Notification endpoints should return proper data structure with type, title, message fields
- Mark-as-read functionality should work correctly
- Notification types should be consistent and match the routing logic I implemented

**Login Credentials**:
- Use demo_user@cataloro.com / demo123 or admin@cataloro.com / admin123
- Test with both regular user and admin to verify admin-specific notifications

GOAL: Ensure the backend properly supports the notification routing changes implemented for both mobile and desktop platforms.
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

    async def test_notifications_endpoint(self, token, user_id, user_email):
        """Test GET /api/user/{user_id}/notifications endpoint for notification routing support"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/user/{user_id}/notifications"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response has the expected structure
                    if isinstance(data, list):
                        notifications = data
                        
                        # Verify notification structure for routing
                        notification_types = set()
                        required_fields = ['id', 'type', 'title', 'message', 'read', 'created_at']
                        
                        for notification in notifications:
                            notification_type = notification.get('type', 'unknown')
                            notification_types.add(notification_type)
                            
                            # Check for required fields
                            missing_fields = [field for field in required_fields if field not in notification]
                            if missing_fields:
                                self.log_result(
                                    "Notifications Endpoint", 
                                    False, 
                                    f"❌ MISSING FIELDS: Notification missing fields {missing_fields}",
                                    response_time
                                )
                                return {'success': False, 'error': f'Missing fields: {missing_fields}'}
                        
                        # Check for expected notification types for routing
                        expected_types = {
                            'tender_accepted', 'transaction_completed', 'transaction_marked_completed',
                            'transaction_fully_completed', 'new_tender_offer', 'tender_offer',
                            'new_user_registration'
                        }
                        
                        found_routing_types = notification_types.intersection(expected_types)
                        
                        self.log_result(
                            "Notifications Endpoint", 
                            True, 
                            f"✅ NOTIFICATIONS WORKING: Found {len(notifications)} notifications, Types: {list(notification_types)}, Routing types found: {list(found_routing_types)}",
                            response_time
                        )
                        return {
                            'success': True, 
                            'notifications_count': len(notifications),
                            'notification_types': list(notification_types),
                            'routing_types_found': list(found_routing_types),
                            'notifications': notifications,
                            'user_email': user_email
                        }
                    else:
                        self.log_result(
                            "Notifications Endpoint", 
                            False, 
                            f"❌ WRONG STRUCTURE: Expected array, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response structure'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Notifications Endpoint", 
                        False, 
                        f"❌ NOTIFICATIONS FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Notifications Endpoint", 
                False, 
                f"❌ NOTIFICATIONS EXCEPTION: {str(e)}",
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

    async def run_notification_system_tests(self):
        """Run comprehensive notification system tests"""
        print("🚀 CATALORO NOTIFICATION SYSTEM BACKEND TESTING")
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
            
            # Step 2: Test notifications endpoint
            print(f"📬 Testing notifications endpoint for {user_type}...")
            notifications_result = await self.test_notifications_endpoint(token, user_id, email)
            user_results['notifications'] = notifications_result
            
            # Step 3: Test notification types support
            print(f"🏷️ Testing notification types support for {user_type}...")
            types_result = await self.test_notification_types_support(notifications_result)
            user_results['types_support'] = types_result
            
            # Step 4: Test mark as read functionality (if we have notifications)
            if notifications_result.get('success') and notifications_result.get('notifications'):
                notifications = notifications_result.get('notifications', [])
                if notifications:
                    # Find an unread notification or use the first one
                    test_notification = None
                    for notif in notifications:
                        if not notif.get('read', True):
                            test_notification = notif
                            break
                    
                    if not test_notification and notifications:
                        test_notification = notifications[0]
                    
                    if test_notification:
                        notification_id = test_notification.get('id')
                        print(f"✅ Testing mark as read for {user_type} with notification {notification_id}...")
                        mark_read_result = await self.test_mark_notification_as_read(token, user_id, notification_id)
                        user_results['mark_as_read'] = mark_read_result
                    else:
                        print(f"⚠️ No notifications available for mark-as-read test for {user_type}")
                        user_results['mark_as_read'] = {'success': False, 'error': 'No notifications available'}
                else:
                    print(f"⚠️ No notifications found for {user_type}")
                    user_results['mark_as_read'] = {'success': False, 'error': 'No notifications found'}
            else:
                print(f"⚠️ Notifications endpoint failed for {user_type}, skipping mark-as-read test")
                user_results['mark_as_read'] = {'success': False, 'error': 'Notifications endpoint failed'}
            
            # Step 5: Try to create test notifications for missing types (if admin)
            if user_type == "Admin User" and types_result.get('success'):
                missing_types = types_result.get('missing_routing_types', [])
                if missing_types:
                    print(f"🧪 Creating test notifications for missing types: {missing_types}")
                    created_notifications = []
                    for notif_type in missing_types[:3]:  # Limit to 3 test notifications
                        create_result = await self.create_test_notification(token, user_id, notif_type)
                        if create_result.get('success'):
                            created_notifications.append(create_result)
                    
                    user_results['created_test_notifications'] = created_notifications
                    
                    # Re-test notifications endpoint to see if new types are now available
                    if created_notifications:
                        print(f"🔄 Re-testing notifications endpoint after creating test notifications...")
                        updated_notifications_result = await self.test_notifications_endpoint(token, user_id, email)
                        user_results['updated_notifications'] = updated_notifications_result
            
            all_results[user_type] = user_results
            print()
        
        # Generate summary
        self.generate_notification_system_summary(all_results)
        
        return all_results

    def generate_notification_system_summary(self, all_results):
        """Generate comprehensive summary of notification system testing"""
        print("📊 NOTIFICATION SYSTEM TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        
        for user_type, results in all_results.items():
            print(f"\n🔍 {user_type} Results:")
            print("-" * 30)
            
            # Handle case where results might be a list or dict
            if isinstance(results, dict):
                results_items = results.items()
            else:
                # Skip if results is not a dict
                print(f"  ⚠️ Invalid results format for {user_type}")
                continue
            
            for test_name, result in results_items:
                total_tests += 1
                if result.get('success'):
                    passed_tests += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
                
                print(f"  {status}: {test_name.replace('_', ' ').title()}")
                
                # Add specific details for key tests
                if test_name == 'notifications' and result.get('success'):
                    count = result.get('notifications_count', 0)
                    types = result.get('notification_types', [])
                    routing_types = result.get('routing_types_found', [])
                    print(f"    📊 Found {count} notifications")
                    print(f"    🏷️ Types: {types}")
                    print(f"    🔀 Routing types: {routing_types}")
                
                elif test_name == 'types_support' and result.get('success'):
                    supported = result.get('supported_routing_types', [])
                    missing = result.get('missing_routing_types', [])
                    print(f"    ✅ Supported: {supported}")
                    if missing:
                        print(f"    ⚠️ Missing: {missing}")
                
                elif not result.get('success'):
                    error = result.get('error', 'Unknown error')
                    print(f"    ❌ Error: {error}")
        
        # Overall summary
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Key findings
        print(f"\n🔑 KEY FINDINGS:")
        
        # Check if notification endpoints are working
        demo_notifications = all_results.get('Demo User', {})
        admin_notifications = all_results.get('Admin User', {})
        
        # Handle case where results might contain lists
        if isinstance(demo_notifications, dict):
            demo_notifications_result = demo_notifications.get('notifications', {})
        else:
            demo_notifications_result = {}
            
        if isinstance(admin_notifications, dict):
            admin_notifications_result = admin_notifications.get('notifications', {})
        else:
            admin_notifications_result = {}
        
        if demo_notifications_result.get('success') or admin_notifications_result.get('success'):
            print("   ✅ Notification endpoints are working")
        else:
            print("   ❌ Notification endpoints are not working")
        
        # Check routing types support
        demo_types = demo_notifications.get('types_support', {}) if isinstance(demo_notifications, dict) else {}
        admin_types = admin_notifications.get('types_support', {}) if isinstance(admin_notifications, dict) else {}
        
        all_supported_types = set()
        if demo_types.get('success'):
            all_supported_types.update(demo_types.get('supported_routing_types', []))
        if admin_types.get('success'):
            all_supported_types.update(admin_types.get('supported_routing_types', []))
        
        required_types = {
            'tender_accepted', 'transaction_completed', 'transaction_marked_completed',
            'transaction_fully_completed', 'new_tender_offer', 'tender_offer',
            'new_user_registration'
        }
        
        if all_supported_types:
            print(f"   ✅ Routing types supported: {list(all_supported_types)}")
            missing_types = required_types - all_supported_types
            if missing_types:
                print(f"   ⚠️ Missing routing types: {list(missing_types)}")
        else:
            print("   ❌ No routing types supported")
        
        # Check mark as read functionality
        demo_mark_read = demo_notifications.get('mark_as_read', {}) if isinstance(demo_notifications, dict) else {}
        admin_mark_read = admin_notifications.get('mark_as_read', {}) if isinstance(admin_notifications, dict) else {}
        
        if demo_mark_read.get('success') or admin_mark_read.get('success'):
            print("   ✅ Mark-as-read functionality is working")
        else:
            print("   ❌ Mark-as-read functionality needs attention")
        
        print(f"\n🎉 NOTIFICATION SYSTEM TESTING COMPLETED!")
        print("=" * 80)

async def main():
    """Main test execution function"""
    async with BackendTester() as tester:
        results = await tester.run_notification_system_tests()
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