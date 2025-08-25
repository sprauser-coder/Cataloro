#!/usr/bin/env python3
"""
NOTIFICATION CLEARING FUNCTIONALITY DEBUG TEST

This test specifically addresses the critical issue:
"The notification center is not clearing notifications after approve/reject actions are taken"

Test Scenarios:
1. Get all notifications for admin user
2. Test notification mark-as-read endpoint directly
3. Test order approval workflow and notification clearing
4. Check database state of notifications
5. Simulate complete flow: get notifications → approve order → mark notification as read
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration - Use frontend environment for backend URL
BACKEND_URL = 'https://cataloro-revival.preview.emergentagent.com/api'

# Test credentials
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class NotificationDebugTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.notifications = []
        self.orders = []
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access_token']
                self.log_result("Admin Authentication", True, f"Token obtained for {data['user']['email']}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}

    def test_get_notifications(self):
        """Test getting all notifications"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/notifications",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.notifications = data.get('notifications', [])
                unread_count = data.get('unread_count', 0)
                
                self.log_result(
                    "Get Notifications", 
                    True, 
                    f"Retrieved {len(self.notifications)} notifications, {unread_count} unread",
                    {"notification_count": len(self.notifications), "unread_count": unread_count, "first_few_notifications": self.notifications[:3] if len(self.notifications) > 3 else self.notifications}
                )
                
                # Log notification details
                if self.notifications:
                    print("📋 NOTIFICATION DETAILS:")
                    for i, notif in enumerate(self.notifications[:5]):  # Show first 5
                        print(f"   {i+1}. ID: {notif.get('id', 'N/A')}")
                        print(f"      Type: {notif.get('type', 'N/A')}")
                        print(f"      Title: {notif.get('title', 'N/A')}")
                        print(f"      Read: {notif.get('read', 'N/A')}")  # Note: backend uses 'read', not 'is_read'
                        print(f"      Created: {notif.get('created_at', 'N/A')}")
                        print()
                
                return True
            else:
                self.log_result("Get Notifications", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Get Notifications", False, f"Exception: {str(e)}")
            return False

    def test_mark_notification_read(self, notification_id):
        """Test marking a specific notification as read"""
        try:
            response = requests.put(
                f"{BACKEND_URL}/notifications/{notification_id}/read",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                self.log_result(
                    f"Mark Notification Read (ID: {notification_id})", 
                    True, 
                    "Notification marked as read successfully"
                )
                return True
            else:
                self.log_result(
                    f"Mark Notification Read (ID: {notification_id})", 
                    False, 
                    f"Status: {response.status_code}", 
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(
                f"Mark Notification Read (ID: {notification_id})", 
                False, 
                f"Exception: {str(e)}"
            )
            return False

    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        try:
            response = requests.put(
                f"{BACKEND_URL}/notifications/mark-all-read",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Mark All Notifications Read", 
                    True, 
                    "All notifications marked as read successfully"
                )
                return True
            else:
                self.log_result(
                    "Mark All Notifications Read", 
                    False, 
                    f"Status: {response.status_code}", 
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Mark All Notifications Read", False, f"Exception: {str(e)}")
            return False

    def test_get_orders(self):
        """Test getting orders to find pending orders for approval testing"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/orders",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                self.orders = response.json()
                pending_orders = [order for order in self.orders if order.get('order', {}).get('status') == 'pending']
                
                self.log_result(
                    "Get Orders", 
                    True, 
                    f"Retrieved {len(self.orders)} orders, {len(pending_orders)} pending",
                    {"total_orders": len(self.orders), "pending_orders": len(pending_orders)}
                )
                
                # Log order details
                if pending_orders:
                    print("📦 PENDING ORDERS:")
                    for i, order_data in enumerate(pending_orders[:3]):  # Show first 3
                        order = order_data.get('order', {})
                        listing = order_data.get('listing', {})
                        print(f"   {i+1}. Order ID: {order.get('id', 'N/A')}")
                        print(f"      Status: {order.get('status', 'N/A')}")
                        print(f"      Listing: {listing.get('title', 'N/A')}")
                        print(f"      Amount: €{order.get('total_amount', 0):.2f}")
                        print()
                
                return True
            else:
                self.log_result("Get Orders", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Get Orders", False, f"Exception: {str(e)}")
            return False

    def test_approve_order(self, order_id):
        """Test approving an order"""
        try:
            response = requests.put(
                f"{BACKEND_URL}/orders/{order_id}/approve",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                self.log_result(
                    f"Approve Order (ID: {order_id})", 
                    True, 
                    "Order approved successfully"
                )
                return True
            else:
                self.log_result(
                    f"Approve Order (ID: {order_id})", 
                    False, 
                    f"Status: {response.status_code}", 
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(f"Approve Order (ID: {order_id})", False, f"Exception: {str(e)}")
            return False

    def test_notification_workflow(self):
        """Test the complete notification workflow"""
        print("🔄 TESTING COMPLETE NOTIFICATION WORKFLOW")
        print("=" * 60)
        
        # Step 1: Get initial notifications
        print("Step 1: Getting initial notifications...")
        if not self.test_get_notifications():
            return False
        
        initial_unread_count = 0
        if isinstance(self.notifications, list):
            initial_unread_count = len([n for n in self.notifications if isinstance(n, dict) and not n.get('read', True)])
        print(f"Initial unread notifications: {initial_unread_count}")
        
        # Step 2: Test mark single notification as read (if any exist)
        if isinstance(self.notifications, list) and self.notifications:
            first_unread = None
            if isinstance(self.notifications, list):
                first_unread = next((n for n in self.notifications if isinstance(n, dict) and not n.get('read', True)), None)
            if first_unread:
                print(f"\nStep 2: Testing mark single notification as read...")
                notification_id = first_unread.get('id')
                if notification_id:
                    self.test_mark_notification_read(notification_id)
                    
                    # Verify it was marked as read
                    print("Verifying notification was marked as read...")
                    self.test_get_notifications()
                    updated_notification = None
                    if isinstance(self.notifications, list):
                        updated_notification = next((n for n in self.notifications if isinstance(n, dict) and n.get('id') == notification_id), None)
                    if updated_notification and updated_notification.get('read'):
                        self.log_result("Notification Read Status Update", True, "Notification successfully marked as read")
                    else:
                        self.log_result("Notification Read Status Update", False, "Notification was not marked as read")
        
        # Step 3: Test order approval workflow
        print(f"\nStep 3: Testing order approval workflow...")
        if not self.test_get_orders():
            return False
        
        # Find a pending order to approve
        pending_orders = [order for order in self.orders if order.get('order', {}).get('status') == 'pending']
        if pending_orders:
            order_to_approve = pending_orders[0]
            order_id = order_to_approve.get('order', {}).get('id')
            
            if order_id:
                print(f"Attempting to approve order: {order_id}")
                
                # Get notifications before approval
                self.test_get_notifications()
                notifications_before = len(self.notifications)
                
                # Approve the order
                if self.test_approve_order(order_id):
                    # Get notifications after approval
                    print("Checking notifications after order approval...")
                    self.test_get_notifications()
                    notifications_after = len(self.notifications)
                    
                    # Check if new notification was created for buyer
                    new_notifications = []
                    if isinstance(self.notifications, list):
                        new_notifications = [n for n in self.notifications if isinstance(n, dict) and n.get('type') == 'order_approved']
                    if new_notifications:
                        self.log_result(
                            "Order Approval Notification Creation", 
                            True, 
                            f"New approval notification created: {len(new_notifications)} notifications"
                        )
                    else:
                        self.log_result(
                            "Order Approval Notification Creation", 
                            False, 
                            "No approval notification found after order approval"
                        )
        else:
            print("No pending orders found to test approval workflow")
        
        # Step 4: Test mark all notifications as read
        print(f"\nStep 4: Testing mark all notifications as read...")
        if self.test_mark_all_notifications_read():
            # Verify all notifications are marked as read
            print("Verifying all notifications were marked as read...")
            self.test_get_notifications()
            unread_notifications = []
            if isinstance(self.notifications, list):
                unread_notifications = [n for n in self.notifications if isinstance(n, dict) and not n.get('read', True)]
            if not unread_notifications:
                self.log_result("Mark All Notifications Read Verification", True, "All notifications successfully marked as read")
            else:
                self.log_result(
                    "Mark All Notifications Read Verification", 
                    False, 
                    f"{len(unread_notifications)} notifications still unread"
                )
        
        return True

    def run_debug_tests(self):
        """Run all notification debug tests"""
        print("🚀 STARTING NOTIFICATION CLEARING FUNCTIONALITY DEBUG")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Run the complete workflow test
        self.test_notification_workflow()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r['status']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result['status']:
                    print(f"   - {result['test']}: {result['details']}")
        
        print("\n🔍 KEY FINDINGS:")
        
        # Check if notifications exist
        if hasattr(self, 'notifications') and self.notifications:
            # Handle case where notifications might be a string (error response)
            if isinstance(self.notifications, list):
                unread_count = len([n for n in self.notifications if isinstance(n, dict) and not n.get('read', True)])
                print(f"   - Found {len(self.notifications)} total notifications")
                print(f"   - {unread_count} notifications are unread")
                
                # Check notification types
                notification_types = {}
                for notif in self.notifications:
                    if isinstance(notif, dict):
                        notif_type = notif.get('type', 'unknown')
                        notification_types[notif_type] = notification_types.get(notif_type, 0) + 1
                
                print(f"   - Notification types: {notification_types}")
            else:
                print(f"   - Notifications response was not a list: {type(self.notifications)}")
        else:
            print("   - No notifications found in the system")
        
        # Check if orders exist
        if hasattr(self, 'orders') and self.orders:
            pending_count = len([o for o in self.orders if o.get('order', {}).get('status') == 'pending'])
            print(f"   - Found {len(self.orders)} total orders")
            print(f"   - {pending_count} orders are pending approval")
        else:
            print("   - No orders found in the system")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = NotificationDebugTester()
    success = tester.run_debug_tests()
    
    if success:
        print("\n✅ ALL NOTIFICATION DEBUG TESTS PASSED")
        sys.exit(0)
    else:
        print("\n❌ SOME NOTIFICATION DEBUG TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()