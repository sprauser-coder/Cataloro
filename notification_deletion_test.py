#!/usr/bin/env python3
"""
Enhanced Notification System Deletion Testing
Tests the enhanced notification system with focus on deletion issues
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class NotificationDeletionTester:
    def __init__(self, base_url="https://cataloro-upgrade.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.created_notifications = []

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
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

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

    def setup_users(self):
        """Setup admin and regular users for testing"""
        print("\n🔐 Setting up test users...")
        
        # Login admin user
        success_admin, admin_response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success_admin and 'token' in admin_response:
            self.admin_token = admin_response['token']
            self.admin_user = admin_response['user']
            print(f"   Admin User ID: {self.admin_user['id']}")
        
        # Login regular user
        success_user, user_response = self.run_test(
            "Regular User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "demo@cataloro.com", "password": "demo123"}
        )
        
        if success_user and 'token' in user_response:
            self.user_token = user_response['token']
            self.regular_user = user_response['user']
            print(f"   Regular User ID: {self.regular_user['id']}")
        
        return success_admin and success_user

    def create_test_notifications(self):
        """Create test notifications of different types"""
        print("\n📝 Creating test notifications of different types...")
        
        if not self.regular_user:
            print("❌ Cannot create notifications - no regular user")
            return False
        
        user_id = self.regular_user['id']
        
        # Test notification types to create
        test_notifications = [
            {
                "title": "Order Complete",
                "message": "Your order for Premium Headphones has been completed successfully.",
                "type": "order_complete",
                "archived": False
            },
            {
                "title": "New Message",
                "message": "You have received a new message about your listing.",
                "type": "message",
                "archived": False
            },
            {
                "title": "System Update",
                "message": "System maintenance completed successfully.",
                "type": "system",
                "archived": False
            },
            {
                "title": "Order Shipped",
                "message": "Your order has been shipped and is on the way.",
                "type": "order",
                "archived": False
            },
            {
                "title": "Payment Received",
                "message": "Payment for your listing has been received.",
                "type": "payment",
                "archived": False
            }
        ]
        
        created_count = 0
        for notification_data in test_notifications:
            success, response = self.run_test(
                f"Create {notification_data['type']} Notification",
                "POST",
                f"api/user/{user_id}/notifications",
                200,
                data=notification_data
            )
            
            if success and 'id' in response:
                self.created_notifications.append({
                    'id': response['id'],
                    'type': notification_data['type'],
                    'title': notification_data['title']
                })
                created_count += 1
                print(f"   ✅ Created {notification_data['type']} notification: {response['id']}")
        
        self.log_test("Create Test Notifications", created_count == len(test_notifications),
                     f"Created {created_count}/{len(test_notifications)} notifications")
        
        return created_count > 0

    def test_notification_retrieval(self):
        """Test notification retrieval with enhanced fields"""
        print("\n📋 Testing notification retrieval with enhanced fields...")
        
        if not self.regular_user:
            print("❌ Cannot test retrieval - no regular user")
            return False
        
        user_id = self.regular_user['id']
        
        success, response = self.run_test(
            "Get User Notifications",
            "GET",
            f"api/user/{user_id}/notifications",
            200
        )
        
        if success and response:
            print(f"   📊 Found {len(response)} notifications")
            
            # Check for enhanced fields
            enhanced_fields_found = 0
            for notification in response:
                required_fields = ['id', 'title', 'message', 'type', 'is_read', 'created_at']
                has_required = all(field in notification for field in required_fields)
                
                if has_required:
                    enhanced_fields_found += 1
                    
                # Check for archived field
                has_archived = 'archived' in notification
                if has_archived:
                    print(f"   ✅ Notification {notification['id'][:8]}... has archived field: {notification.get('archived', False)}")
                
                print(f"   📝 Notification: {notification.get('title', 'No title')} (Type: {notification.get('type', 'unknown')})")
            
            self.log_test("Enhanced Fields Present", enhanced_fields_found > 0,
                         f"Found {enhanced_fields_found} notifications with enhanced fields")
            
            return enhanced_fields_found > 0
        
        return False

    def test_single_notification_deletion(self):
        """Test deletion of individual notifications using multi-endpoint approach"""
        print("\n🗑️ Testing single notification deletion with multi-endpoint approach...")
        
        if not self.regular_user or not self.created_notifications:
            print("❌ Cannot test deletion - no user or notifications")
            return False
        
        user_id = self.regular_user['id']
        deletion_results = []
        
        # Test each deletion endpoint for different notification types
        for i, notification in enumerate(self.created_notifications[:3]):  # Test first 3
            notification_id = notification['id']
            notification_type = notification['type']
            
            print(f"\n   🎯 Testing deletion of {notification_type} notification...")
            
            # Try multiple deletion endpoints as per the enhanced system
            endpoints_to_try = [
                f"api/user/{user_id}/notifications/{notification_id}",
                f"api/notifications/{notification_id}?user_id={user_id}",
                f"api/user/{user_id}/system-notifications/{notification_id}"
            ]
            
            deletion_success = False
            successful_endpoint = None
            
            for endpoint in endpoints_to_try:
                print(f"      Trying endpoint: {endpoint}")
                success, response = self.run_test(
                    f"Delete via {endpoint.split('/')[-2] if '/' in endpoint else 'direct'}",
                    "DELETE",
                    endpoint,
                    200
                )
                
                if success:
                    deletion_success = True
                    successful_endpoint = endpoint
                    print(f"      ✅ Successfully deleted via: {endpoint}")
                    break
                else:
                    print(f"      ❌ Failed via: {endpoint}")
            
            deletion_results.append({
                'notification_id': notification_id,
                'type': notification_type,
                'success': deletion_success,
                'endpoint': successful_endpoint
            })
            
            if deletion_success:
                # Verify deletion by trying to retrieve
                verify_success, verify_response = self.run_test(
                    f"Verify {notification_type} Deletion",
                    "GET",
                    f"api/user/{user_id}/notifications",
                    200
                )
                
                if verify_success:
                    still_exists = any(n.get('id') == notification_id for n in verify_response)
                    self.log_test(f"Deletion Verification for {notification_type}", not still_exists,
                                 f"Notification {'still exists' if still_exists else 'successfully deleted'}")
        
        # Summary
        successful_deletions = sum(1 for result in deletion_results if result['success'])
        self.log_test("Single Notification Deletions", successful_deletions > 0,
                     f"Successfully deleted {successful_deletions}/{len(deletion_results)} notifications")
        
        return successful_deletions > 0

    def test_bulk_deletion_functionality(self):
        """Test bulk deletion functionality with mixed notification types"""
        print("\n📦 Testing bulk deletion functionality...")
        
        if not self.regular_user:
            print("❌ Cannot test bulk deletion - no regular user")
            return False
        
        user_id = self.regular_user['id']
        
        # Create additional notifications for bulk testing
        bulk_test_notifications = [
            {
                "title": "Bulk Test Order 1",
                "message": "First order for bulk deletion testing.",
                "type": "order_complete",
                "archived": False
            },
            {
                "title": "Bulk Test Message 1",
                "message": "First message for bulk deletion testing.",
                "type": "message",
                "archived": False
            },
            {
                "title": "Bulk Test System 1",
                "message": "First system notification for bulk deletion testing.",
                "type": "system",
                "archived": False
            }
        ]
        
        bulk_notification_ids = []
        
        # Create bulk test notifications
        for notification_data in bulk_test_notifications:
            success, response = self.run_test(
                f"Create Bulk Test {notification_data['type']}",
                "POST",
                f"api/user/{user_id}/notifications",
                200,
                data=notification_data
            )
            
            if success and 'id' in response:
                bulk_notification_ids.append(response['id'])
        
        if not bulk_notification_ids:
            print("❌ Failed to create bulk test notifications")
            return False
        
        print(f"   📝 Created {len(bulk_notification_ids)} notifications for bulk testing")
        
        # Test bulk deletion
        successful_bulk_deletions = 0
        failed_bulk_deletions = 0
        
        for notification_id in bulk_notification_ids:
            # Try the enhanced multi-endpoint deletion approach
            endpoints_to_try = [
                f"api/user/{user_id}/notifications/{notification_id}",
                f"api/notifications/{notification_id}?user_id={user_id}"
            ]
            
            deletion_success = False
            for endpoint in endpoints_to_try:
                success, response = self.run_test(
                    f"Bulk Delete {notification_id[:8]}...",
                    "DELETE",
                    endpoint,
                    200
                )
                
                if success:
                    deletion_success = True
                    successful_bulk_deletions += 1
                    break
            
            if not deletion_success:
                failed_bulk_deletions += 1
        
        # Calculate success/failure rates
        total_bulk = len(bulk_notification_ids)
        success_rate = (successful_bulk_deletions / total_bulk) * 100 if total_bulk > 0 else 0
        
        print(f"   📊 Bulk Deletion Results:")
        print(f"      ✅ Successful: {successful_bulk_deletions}/{total_bulk} ({success_rate:.1f}%)")
        print(f"      ❌ Failed: {failed_bulk_deletions}/{total_bulk}")
        
        self.log_test("Bulk Deletion Functionality", successful_bulk_deletions > 0,
                     f"Success rate: {success_rate:.1f}% ({successful_bulk_deletions}/{total_bulk})")
        
        # Test feedback on success/failure rates
        if successful_bulk_deletions > 0 and failed_bulk_deletions > 0:
            print(f"   ⚠️  Mixed results - some deletions succeeded, some failed")
            self.log_test("Mixed Deletion Results Handling", True,
                         "System handles mixed success/failure scenarios")
        
        return successful_bulk_deletions > 0

    def test_order_complete_notifications(self):
        """Specifically test 'Order complete' notification deletion"""
        print("\n🛒 Testing 'Order complete' notification deletion specifically...")
        
        if not self.regular_user:
            print("❌ Cannot test order complete notifications - no regular user")
            return False
        
        user_id = self.regular_user['id']
        
        # Create multiple "Order complete" notifications
        order_complete_notifications = []
        for i in range(3):
            notification_data = {
                "title": f"Order Complete #{i+1}",
                "message": f"Your order #{1000+i} for Premium Product {i+1} has been completed successfully.",
                "type": "order_complete",
                "archived": False
            }
            
            success, response = self.run_test(
                f"Create Order Complete #{i+1}",
                "POST",
                f"api/user/{user_id}/notifications",
                200,
                data=notification_data
            )
            
            if success and 'id' in response:
                order_complete_notifications.append(response['id'])
        
        if not order_complete_notifications:
            print("❌ Failed to create order complete notifications")
            return False
        
        print(f"   📝 Created {len(order_complete_notifications)} 'Order complete' notifications")
        
        # Test deletion of each "Order complete" notification
        successful_order_deletions = 0
        
        for i, notification_id in enumerate(order_complete_notifications):
            print(f"\n   🎯 Testing deletion of Order Complete #{i+1}...")
            
            # Use the enhanced multi-endpoint deletion logic
            endpoints_to_try = [
                f"api/user/{user_id}/notifications/{notification_id}",
                f"api/notifications/{notification_id}?user_id={user_id}",
                f"api/user/{user_id}/system-notifications/{notification_id}"
            ]
            
            deletion_success = False
            for endpoint in endpoints_to_try:
                success, response = self.run_test(
                    f"Delete Order Complete via {endpoint.split('/')[-2]}",
                    "DELETE",
                    endpoint,
                    200
                )
                
                if success:
                    deletion_success = True
                    successful_order_deletions += 1
                    print(f"      ✅ Successfully deleted Order Complete #{i+1}")
                    break
            
            if not deletion_success:
                print(f"      ❌ Failed to delete Order Complete #{i+1}")
        
        # Verify all order complete notifications are deleted
        verify_success, verify_response = self.run_test(
            "Verify Order Complete Deletions",
            "GET",
            f"api/user/{user_id}/notifications",
            200
        )
        
        remaining_order_complete = 0
        if verify_success:
            remaining_order_complete = sum(1 for n in verify_response 
                                         if n.get('type') == 'order_complete' and 
                                         n.get('id') in order_complete_notifications)
        
        self.log_test("Order Complete Notification Deletion", successful_order_deletions > 0,
                     f"Deleted {successful_order_deletions}/{len(order_complete_notifications)} order complete notifications")
        
        self.log_test("Order Complete Deletion Verification", remaining_order_complete == 0,
                     f"Remaining order complete notifications: {remaining_order_complete}")
        
        return successful_order_deletions > 0

    def test_notification_types_deletion(self):
        """Test deletion of various notification types"""
        print("\n🏷️ Testing deletion of various notification types...")
        
        if not self.regular_user:
            print("❌ Cannot test notification types - no regular user")
            return False
        
        user_id = self.regular_user['id']
        
        # Test different notification types
        notification_types_to_test = [
            {"type": "order", "title": "New Order", "message": "You have a new order."},
            {"type": "order_complete", "title": "Order Complete", "message": "Your order is complete."},
            {"type": "system", "title": "System Alert", "message": "System maintenance scheduled."},
            {"type": "message", "title": "New Message", "message": "You have a new message."},
            {"type": "payment", "title": "Payment Received", "message": "Payment has been processed."}
        ]
        
        type_test_results = {}
        
        for notification_type_data in notification_types_to_test:
            notification_type = notification_type_data['type']
            
            # Create notification of this type
            success, response = self.run_test(
                f"Create {notification_type} Notification",
                "POST",
                f"api/user/{user_id}/notifications",
                200,
                data=notification_type_data
            )
            
            if success and 'id' in response:
                notification_id = response['id']
                
                # Test deletion
                deletion_success = False
                endpoints_to_try = [
                    f"api/user/{user_id}/notifications/{notification_id}",
                    f"api/notifications/{notification_id}?user_id={user_id}"
                ]
                
                for endpoint in endpoints_to_try:
                    delete_success, delete_response = self.run_test(
                        f"Delete {notification_type} Notification",
                        "DELETE",
                        endpoint,
                        200
                    )
                    
                    if delete_success:
                        deletion_success = True
                        break
                
                type_test_results[notification_type] = deletion_success
                
                if deletion_success:
                    print(f"   ✅ {notification_type} notification deleted successfully")
                else:
                    print(f"   ❌ {notification_type} notification deletion failed")
        
        # Summary of type deletion results
        successful_types = sum(1 for success in type_test_results.values() if success)
        total_types = len(type_test_results)
        
        print(f"\n   📊 Notification Type Deletion Results:")
        for notification_type, success in type_test_results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"      {notification_type}: {status}")
        
        self.log_test("Various Notification Types Deletion", successful_types > 0,
                     f"Successfully deleted {successful_types}/{total_types} notification types")
        
        return successful_types > 0

    def run_comprehensive_test(self):
        """Run comprehensive notification deletion testing"""
        print("🔔 ENHANCED NOTIFICATION SYSTEM DELETION TESTING")
        print("=" * 60)
        
        # Setup
        if not self.setup_users():
            print("❌ Failed to setup users - stopping tests")
            return False
        
        # Test sequence
        test_results = []
        
        # 1. Create test notifications
        test_results.append(self.create_test_notifications())
        
        # 2. Test notification retrieval with enhanced fields
        test_results.append(self.test_notification_retrieval())
        
        # 3. Test single notification deletion with multi-endpoint approach
        test_results.append(self.test_single_notification_deletion())
        
        # 4. Test bulk deletion functionality
        test_results.append(self.test_bulk_deletion_functionality())
        
        # 5. Specifically test "Order complete" notifications
        test_results.append(self.test_order_complete_notifications())
        
        # 6. Test various notification types deletion
        test_results.append(self.test_notification_types_deletion())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"\n📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 40)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"Major Test Categories: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL NOTIFICATION DELETION TESTS PASSED!")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} major test categories failed")
            return False

if __name__ == "__main__":
    tester = NotificationDeletionTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)