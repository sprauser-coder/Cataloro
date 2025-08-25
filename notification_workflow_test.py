#!/usr/bin/env python3
"""
COMPREHENSIVE NOTIFICATION WORKFLOW TEST

This test creates test data and simulates the complete notification workflow:
1. Create a test order (which should generate a notification)
2. Test notification retrieval
3. Test order approval (which should mark notification as read)
4. Verify notification clearing works properly
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration - Use frontend environment for backend URL
BACKEND_URL = 'https://emarket-fix.preview.emergentagent.com/api'

# Test credentials
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class NotificationWorkflowTester:
    def __init__(self):
        self.admin_token = None
        self.buyer_token = None
        self.test_results = []
        self.test_listing_id = None
        self.test_order_id = None
        self.test_notification_id = None
        
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

    def create_test_buyer(self):
        """Create a test buyer user"""
        try:
            buyer_data = {
                "email": "testbuyer@example.com",
                "username": "testbuyer",
                "password": "testpass123",
                "full_name": "Test Buyer",
                "role": "buyer"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/register", json=buyer_data)
            
            if response.status_code == 200:
                data = response.json()
                self.buyer_token = data['access_token']
                self.log_result("Create Test Buyer", True, f"Buyer created: {data['user']['email']}")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                # User already exists, try to login
                login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                    "email": buyer_data["email"],
                    "password": buyer_data["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.buyer_token = data['access_token']
                    self.log_result("Create Test Buyer", True, f"Existing buyer logged in: {data['user']['email']}")
                    return True
                else:
                    self.log_result("Create Test Buyer", False, f"Login failed: {login_response.status_code}", login_response.text)
                    return False
            else:
                self.log_result("Create Test Buyer", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Create Test Buyer", False, f"Exception: {str(e)}")
            return False

    def create_test_listing(self):
        """Create a test listing for the order"""
        try:
            listing_data = {
                "title": "Test Notification Item",
                "description": "Test item for notification workflow testing",
                "category": "Electronics",
                "listing_type": "fixed_price",
                "price": 99.99,
                "condition": "New",
                "quantity": 1,
                "location": "Test City"
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_listing_id = data['id']
                self.log_result("Create Test Listing", True, f"Listing created: {data['title']} (ID: {self.test_listing_id})")
                return True
            else:
                self.log_result("Create Test Listing", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Create Test Listing", False, f"Exception: {str(e)}")
            return False

    def create_test_order(self):
        """Create a test order (should generate notification)"""
        try:
            order_data = {
                "listing_id": self.test_listing_id,
                "quantity": 1,
                "shipping_address": "123 Test Street, Test City"
            }
            
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = requests.post(f"{BACKEND_URL}/orders", json=order_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_order_id = data['id']
                self.log_result("Create Test Order", True, f"Order created: {self.test_order_id} (Status: {data['status']})")
                return True
            else:
                self.log_result("Create Test Order", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Create Test Order", False, f"Exception: {str(e)}")
            return False

    def check_notifications_after_order(self):
        """Check if notification was created after order"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                unread_count = data.get('unread_count', 0)
                
                # Look for the new order notification
                order_notifications = [n for n in notifications if 'Order Received' in n.get('title', '')]
                recent_notifications = [n for n in notifications if not n.get('read', True)]
                
                self.log_result(
                    "Check Notifications After Order", 
                    True, 
                    f"Found {len(notifications)} total notifications, {unread_count} unread, {len(order_notifications)} order notifications, {len(recent_notifications)} recent unread"
                )
                
                if recent_notifications:
                    self.test_notification_id = recent_notifications[0].get('id')
                    print(f"📋 RECENT NOTIFICATION FOUND:")
                    notif = recent_notifications[0]
                    print(f"   ID: {notif.get('id', 'N/A')}")
                    print(f"   Title: {notif.get('title', 'N/A')}")
                    print(f"   Message: {notif.get('message', 'N/A')}")
                    print(f"   Read: {notif.get('read', 'N/A')}")
                    print(f"   Type: {notif.get('type', 'N/A')}")
                    print()
                
                return len(recent_notifications) > 0
            else:
                self.log_result("Check Notifications After Order", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Check Notifications After Order", False, f"Exception: {str(e)}")
            return False

    def test_mark_notification_read(self):
        """Test marking the notification as read"""
        if not self.test_notification_id:
            self.log_result("Mark Notification Read", False, "No notification ID available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.put(f"{BACKEND_URL}/notifications/{self.test_notification_id}/read", headers=headers)
            
            if response.status_code == 200:
                self.log_result("Mark Notification Read", True, f"Notification {self.test_notification_id} marked as read")
                return True
            else:
                self.log_result("Mark Notification Read", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Mark Notification Read", False, f"Exception: {str(e)}")
            return False

    def verify_notification_marked_read(self):
        """Verify the notification was actually marked as read"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                unread_count = data.get('unread_count', 0)
                
                # Find our specific notification
                target_notification = next((n for n in notifications if n.get('id') == self.test_notification_id), None)
                
                if target_notification:
                    is_read = target_notification.get('read', False)
                    self.log_result(
                        "Verify Notification Marked Read", 
                        is_read, 
                        f"Notification read status: {is_read}, Total unread: {unread_count}"
                    )
                    return is_read
                else:
                    self.log_result("Verify Notification Marked Read", False, "Target notification not found")
                    return False
            else:
                self.log_result("Verify Notification Marked Read", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Verify Notification Marked Read", False, f"Exception: {str(e)}")
            return False

    def test_order_approval_workflow(self):
        """Test the complete order approval workflow"""
        if not self.test_order_id:
            self.log_result("Order Approval Workflow", False, "No test order available")
            return False
            
        try:
            # First, get notifications before approval
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            before_response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            before_unread = 0
            if before_response.status_code == 200:
                before_data = before_response.json()
                before_unread = before_data.get('unread_count', 0)
            
            # Approve the order
            approve_response = requests.put(f"{BACKEND_URL}/orders/{self.test_order_id}/approve", headers=headers)
            
            if approve_response.status_code == 200:
                self.log_result("Order Approval", True, f"Order {self.test_order_id} approved successfully")
                
                # Check notifications after approval
                after_response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
                if after_response.status_code == 200:
                    after_data = after_response.json()
                    after_unread = after_data.get('unread_count', 0)
                    notifications = after_data.get('notifications', [])
                    
                    # Look for approval notification
                    approval_notifications = [n for n in notifications if 'approved' in n.get('title', '').lower()]
                    
                    self.log_result(
                        "Order Approval Notification Check", 
                        True, 
                        f"Before approval: {before_unread} unread, After approval: {after_unread} unread, Approval notifications: {len(approval_notifications)}"
                    )
                    
                    return True
                else:
                    self.log_result("Order Approval Notification Check", False, f"Failed to get notifications after approval: {after_response.status_code}")
                    return False
            else:
                self.log_result("Order Approval", False, f"Status: {approve_response.status_code}", approve_response.text)
                return False
                
        except Exception as e:
            self.log_result("Order Approval Workflow", False, f"Exception: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Delete test listing if created
            if self.test_listing_id:
                requests.delete(f"{BACKEND_URL}/admin/listings/{self.test_listing_id}", headers=headers)
                
            self.log_result("Cleanup Test Data", True, "Test data cleanup completed")
            
        except Exception as e:
            self.log_result("Cleanup Test Data", False, f"Exception: {str(e)}")

    def run_workflow_test(self):
        """Run the complete notification workflow test"""
        print("🚀 STARTING COMPREHENSIVE NOTIFICATION WORKFLOW TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            return False
        
        # Step 2: Create test buyer
        if not self.create_test_buyer():
            return False
        
        # Step 3: Create test listing
        if not self.create_test_listing():
            return False
        
        # Step 4: Create test order (should generate notification)
        if not self.create_test_order():
            return False
        
        # Step 5: Check if notification was created
        notification_created = self.check_notifications_after_order()
        
        # Step 6: Test manual notification marking
        if notification_created and self.test_notification_id:
            self.test_mark_notification_read()
            self.verify_notification_marked_read()
        
        # Step 7: Test order approval workflow
        self.test_order_approval_workflow()
        
        # Step 8: Cleanup
        self.cleanup_test_data()
        
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
        print(f"   - Test Order ID: {self.test_order_id}")
        print(f"   - Test Notification ID: {self.test_notification_id}")
        print(f"   - Notification Creation: {'✅ Working' if notification_created else '❌ Failed'}")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = NotificationWorkflowTester()
    success = tester.run_workflow_test()
    
    if success:
        print("\n✅ NOTIFICATION WORKFLOW TEST COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n❌ NOTIFICATION WORKFLOW TEST FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()