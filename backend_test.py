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

    async def test_admin_completed_transactions_endpoint(self, token, user_role):
        """Test GET /api/admin/completed-transactions endpoint for admin access"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/admin/completed-transactions"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response has the expected structure
                    transactions = data.get('transactions', [])
                    total_count = data.get('total_count', 0)
                    
                    self.log_result(
                        "Admin Completed Transactions Endpoint", 
                        True, 
                        f"✅ ENDPOINT ACCESSIBLE: Successfully accessed admin completed transactions endpoint. Found {len(transactions)} transactions (total: {total_count})",
                        response_time
                    )
                    return {
                        'success': True, 
                        'transactions_count': len(transactions),
                        'total_count': total_count,
                        'endpoint_accessible': True,
                        'user_role': user_role,
                        'response_structure': list(data.keys())
                    }
                elif response.status == 403:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Completed Transactions Endpoint", 
                        False, 
                        f"❌ ACCESS DENIED: Status 403 - User with role '{user_role}' does not have permission to access admin completed transactions endpoint: {error_text}",
                        response_time
                    )
                    return {
                        'success': False, 
                        'error': 'Access denied - insufficient permissions',
                        'status_code': 403,
                        'user_role': user_role,
                        'endpoint_accessible': False
                    }
                elif response.status == 401:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Completed Transactions Endpoint", 
                        False, 
                        f"❌ AUTHENTICATION FAILED: Status 401 - Token may be invalid or expired: {error_text}",
                        response_time
                    )
                    return {
                        'success': False, 
                        'error': 'Authentication failed',
                        'status_code': 401,
                        'user_role': user_role,
                        'endpoint_accessible': False
                    }
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Completed Transactions Endpoint", 
                        False, 
                        f"❌ ENDPOINT FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {
                        'success': False, 
                        'error': error_text,
                        'status_code': response.status,
                        'user_role': user_role,
                        'endpoint_accessible': False
                    }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Admin Completed Transactions Endpoint", 
                False, 
                f"❌ ENDPOINT EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e), 'user_role': user_role}

    async def test_admin_panel_tab_visibility(self, user_role, permissions_result):
        """Test the tab filtering logic to determine if Completed Transactions tab should be visible"""
        start_time = datetime.now()
        
        try:
            # Simulate the frontend tab filtering logic from AdminPanel.js
            # Tab definition: { id: 'completed', label: 'Completed Transactions', shortLabel: 'Completed', icon: CheckCircle, permission: 'canAccessUserManagement' }
            
            # Check if user should have canAccessUserManagement permission
            should_have_permission = permissions_result.get('should_have_permission', False)
            
            # Simulate the frontend permission check
            # From usePermissions.js: canAccessUserManagement: userRole === 'Admin' || userRole === 'Admin-Manager'
            frontend_permission_check = user_role in ['Admin', 'Admin-Manager']
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if should_have_permission and frontend_permission_check:
                self.log_result(
                    "Admin Panel Tab Visibility", 
                    True, 
                    f"✅ TAB SHOULD BE VISIBLE: User with role '{user_role}' should have canAccessUserManagement permission and see the 'Completed Transactions' tab",
                    response_time
                )
                return {
                    'success': True, 
                    'tab_should_be_visible': True,
                    'user_role': user_role,
                    'has_permission': True,
                    'permission_name': 'canAccessUserManagement',
                    'frontend_check_passes': frontend_permission_check
                }
            else:
                self.log_result(
                    "Admin Panel Tab Visibility", 
                    False, 
                    f"❌ TAB SHOULD NOT BE VISIBLE: User with role '{user_role}' should NOT have canAccessUserManagement permission (backend: {should_have_permission}, frontend: {frontend_permission_check})",
                    response_time
                )
                return {
                    'success': False, 
                    'tab_should_be_visible': False,
                    'user_role': user_role,
                    'has_permission': False,
                    'error': 'User does not have required permission',
                    'frontend_check_passes': frontend_permission_check
                }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Admin Panel Tab Visibility", 
                False, 
                f"❌ TAB VISIBILITY CHECK EXCEPTION: {str(e)}",
                response_time
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

    async def run_admin_panel_completed_transactions_tests(self):
        """Run comprehensive admin panel completed transactions tab tests"""
        print("🚀 CATALORO ADMIN PANEL COMPLETED TRANSACTIONS TAB TESTING")
        print("=" * 80)
        print()
        
        # Test with admin credentials
        test_credentials = [
            ("admin@cataloro.com", "admin123", "Admin User"),
            ("admin@cataloro.com", "password123", "Admin User (Alt Password)"),
        ]
        
        all_results = {}
        
        # Test with admin credentials
        for email, password, user_type in test_credentials:
            print(f"🔐 Testing with {user_type} ({email})")
            print("-" * 50)
            
            # Step 1: Login
            token, user_id, user = await self.test_login_and_get_token(email, password)
            if not token:
                print(f"❌ Login failed for {user_type}, trying next credentials")
                continue
            
            user_results = {}
            user_role = user.get('user_role', 'Unknown')
            username = user.get('username', 'unknown')
            
            # Step 2: Test admin permissions
            print(f"🔍 Testing admin permissions for {user_type}...")
            permissions_result = await self.test_admin_permissions(token, user_id, user)
            user_results['admin_permissions'] = permissions_result
            
            # Step 3: Test admin completed transactions endpoint
            print(f"🔗 Testing admin completed transactions endpoint for {user_type}...")
            endpoint_result = await self.test_admin_completed_transactions_endpoint(token, user_role)
            user_results['completed_transactions_endpoint'] = endpoint_result
            
            # Step 4: Test tab visibility logic
            print(f"👁️ Testing admin panel tab visibility logic for {user_type}...")
            tab_visibility_result = await self.test_admin_panel_tab_visibility(user_role, permissions_result)
            user_results['tab_visibility'] = tab_visibility_result
            
            all_results[user_type] = user_results
            print()
            
            # If login was successful, we can break (no need to test alternative password)
            break
        
        # Generate summary
        self.generate_admin_panel_summary(all_results)
        
        return all_results

    def generate_admin_panel_summary(self, all_results):
        """Generate comprehensive summary of admin panel completed transactions tab testing"""
        print("📊 ADMIN PANEL COMPLETED TRANSACTIONS TAB TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        critical_issues = []
        
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
                    critical_issues.append(f"{user_type}: {test_name}")
                
                print(f"  {status}: {test_name.replace('_', ' ').title()}")
                
                # Add specific details for each test
                if test_name == 'admin_permissions':
                    user_role = result.get('user_role', 'Unknown')
                    should_have_permission = result.get('should_have_permission', False)
                    print(f"    👤 User Role: {user_role}")
                    print(f"    🔑 Should Have Permission: {should_have_permission}")
                    if result.get('success'):
                        print(f"    ✅ Permission Check: PASSED")
                    else:
                        print(f"    ❌ Permission Check: FAILED - {result.get('error', 'Unknown error')}")
                        
                elif test_name == 'completed_transactions_endpoint':
                    endpoint_accessible = result.get('endpoint_accessible', False)
                    status_code = result.get('status_code', 'N/A')
                    transactions_count = result.get('transactions_count', 0)
                    print(f"    🔗 Endpoint Accessible: {endpoint_accessible}")
                    print(f"    📊 Status Code: {status_code}")
                    if result.get('success'):
                        print(f"    📈 Transactions Found: {transactions_count}")
                    else:
                        print(f"    ❌ Error: {result.get('error', 'Unknown error')}")
                        
                elif test_name == 'tab_visibility':
                    tab_should_be_visible = result.get('tab_should_be_visible', False)
                    frontend_check_passes = result.get('frontend_check_passes', False)
                    print(f"    👁️ Tab Should Be Visible: {tab_should_be_visible}")
                    print(f"    🎨 Frontend Check Passes: {frontend_check_passes}")
                    if not result.get('success'):
                        print(f"    ❌ Issue: {result.get('error', 'Unknown error')}")
        
        # Overall summary
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Key findings
        print(f"\n🔑 KEY FINDINGS:")
        
        # Analyze results to determine root cause
        admin_results = all_results.get('Admin User', {}) or all_results.get('Admin User (Alt Password)', {})
        
        if admin_results:
            permissions_result = admin_results.get('admin_permissions', {})
            endpoint_result = admin_results.get('completed_transactions_endpoint', {})
            tab_result = admin_results.get('tab_visibility', {})
            
            # Check login success
            if permissions_result.get('success'):
                print(f"   ✅ Admin login successful with proper role: {permissions_result.get('user_role')}")
            else:
                print(f"   ❌ Admin login or permissions issue")
                
            # Check permissions
            if permissions_result.get('should_have_permission'):
                print(f"   ✅ Admin user should have canAccessUserManagement permission")
            else:
                print(f"   ❌ Admin user does not have required permissions")
                
            # Check endpoint access
            if endpoint_result.get('success'):
                print(f"   ✅ Admin completed transactions endpoint is accessible")
                print(f"   📊 Found {endpoint_result.get('transactions_count', 0)} transactions")
            else:
                print(f"   ❌ Admin completed transactions endpoint is NOT accessible")
                print(f"   🔍 Status Code: {endpoint_result.get('status_code', 'Unknown')}")
                print(f"   💬 Error: {endpoint_result.get('error', 'Unknown error')}")
                
            # Check tab visibility
            if tab_result.get('success'):
                print(f"   ✅ Completed Transactions tab should be visible in Admin Panel")
            else:
                print(f"   ❌ Completed Transactions tab should NOT be visible")
                print(f"   🔍 Frontend permission check: {tab_result.get('frontend_check_passes', False)}")
        
        # Root cause analysis
        print(f"\n🔧 ROOT CAUSE ANALYSIS:")
        
        if not admin_results:
            print("   ❌ CRITICAL: Could not login with admin credentials")
            print("   🔧 SOLUTION: Check admin credentials and authentication system")
        elif not permissions_result.get('success'):
            print("   ❌ CRITICAL: Admin user does not have proper role or permissions")
            print("   🔧 SOLUTION: Verify admin user has 'Admin' or 'Admin-Manager' role")
        elif not endpoint_result.get('success'):
            if endpoint_result.get('status_code') == 403:
                print("   ❌ CRITICAL: Admin user cannot access completed transactions endpoint (403 Forbidden)")
                print("   🔧 SOLUTION: Check backend require_admin_role function and user role verification")
            elif endpoint_result.get('status_code') == 401:
                print("   ❌ CRITICAL: Authentication token is invalid or expired (401 Unauthorized)")
                print("   🔧 SOLUTION: Check JWT token generation and validation")
            else:
                print("   ❌ CRITICAL: Backend endpoint /api/admin/completed-transactions is not working")
                print("   🔧 SOLUTION: Check backend server logs and endpoint implementation")
        elif not tab_result.get('success'):
            print("   ❌ ISSUE: Frontend permission logic may be incorrect")
            print("   🔧 SOLUTION: Check usePermissions.js and AdminPanel.js tab filtering logic")
        else:
            print("   ✅ ALL SYSTEMS WORKING: The Completed Transactions tab should be accessible")
            print("   🎉 RECOMMENDATION: The issue may be resolved or was a temporary problem")
        
        print(f"\n🎉 ADMIN PANEL COMPLETED TRANSACTIONS TAB TESTING COMPLETED!")
        print("=" * 80)

async def main():
    """Main test execution function"""
    async with BackendTester() as tester:
        results = await tester.run_admin_panel_completed_transactions_tests()
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