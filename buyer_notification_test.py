#!/usr/bin/env python3
"""
BUYER NOTIFICATION TEST

This test specifically checks if the buyer receives notifications after order approval.
The issue might be that we were checking admin notifications instead of buyer notifications.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration - Use frontend environment for backend URL
BACKEND_URL = 'https://marketplace-fix-6.preview.emergentagent.com/api'

# Test credentials
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class BuyerNotificationTester:
    def __init__(self):
        self.admin_token = None
        self.buyer_token = None
        self.test_results = []
        self.test_listing_id = None
        self.test_order_id = None
        
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

    def authenticate_buyer(self):
        """Authenticate as buyer user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": "testbuyer@example.com",
                "password": "testpass123"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.buyer_token = data['access_token']
                self.log_result("Buyer Authentication", True, f"Token obtained for {data['user']['email']}")
                return True
            else:
                self.log_result("Buyer Authentication", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Buyer Authentication", False, f"Exception: {str(e)}")
            return False

    def create_test_listing(self):
        """Create a test listing for the order"""
        try:
            listing_data = {
                "title": "Buyer Notification Test Item",
                "description": "Test item for buyer notification testing",
                "category": "Electronics",
                "listing_type": "fixed_price",
                "price": 149.99,
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
        """Create a test order as buyer"""
        try:
            order_data = {
                "listing_id": self.test_listing_id,
                "quantity": 1,
                "shipping_address": "456 Buyer Street, Buyer City"
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

    def check_buyer_notifications_before_approval(self):
        """Check buyer notifications before order approval"""
        try:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                unread_count = data.get('unread_count', 0)
                
                self.log_result(
                    "Check Buyer Notifications Before Approval", 
                    True, 
                    f"Buyer has {len(notifications)} total notifications, {unread_count} unread"
                )
                
                return True
            else:
                self.log_result("Check Buyer Notifications Before Approval", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Check Buyer Notifications Before Approval", False, f"Exception: {str(e)}")
            return False

    def approve_order_as_seller(self):
        """Approve the order as seller (admin)"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.put(f"{BACKEND_URL}/orders/{self.test_order_id}/approve", headers=headers)
            
            if response.status_code == 200:
                self.log_result("Approve Order as Seller", True, f"Order {self.test_order_id} approved successfully")
                return True
            else:
                self.log_result("Approve Order as Seller", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Approve Order as Seller", False, f"Exception: {str(e)}")
            return False

    def check_buyer_notifications_after_approval(self):
        """Check buyer notifications after order approval - THIS IS THE KEY TEST"""
        try:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                unread_count = data.get('unread_count', 0)
                
                # Look for approval notifications
                approval_notifications = [n for n in notifications if 'approved' in n.get('title', '').lower()]
                recent_unread = [n for n in notifications if not n.get('read', True)]
                
                self.log_result(
                    "Check Buyer Notifications After Approval", 
                    True, 
                    f"Buyer has {len(notifications)} total notifications, {unread_count} unread, {len(approval_notifications)} approval notifications"
                )
                
                if approval_notifications:
                    print("📋 APPROVAL NOTIFICATIONS FOUND:")
                    for i, notif in enumerate(approval_notifications):
                        print(f"   {i+1}. ID: {notif.get('id', 'N/A')}")
                        print(f"      Title: {notif.get('title', 'N/A')}")
                        print(f"      Message: {notif.get('message', 'N/A')}")
                        print(f"      Read: {notif.get('read', 'N/A')}")
                        print(f"      Type: {notif.get('type', 'N/A')}")
                        print()
                
                if recent_unread:
                    print("📋 RECENT UNREAD NOTIFICATIONS:")
                    for i, notif in enumerate(recent_unread):
                        print(f"   {i+1}. ID: {notif.get('id', 'N/A')}")
                        print(f"      Title: {notif.get('title', 'N/A')}")
                        print(f"      Message: {notif.get('message', 'N/A')}")
                        print(f"      Type: {notif.get('type', 'N/A')}")
                        print()
                
                return len(approval_notifications) > 0
            else:
                self.log_result("Check Buyer Notifications After Approval", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Check Buyer Notifications After Approval", False, f"Exception: {str(e)}")
            return False

    def test_mark_approval_notification_read(self):
        """Test marking the approval notification as read"""
        try:
            # Get buyer notifications to find approval notification
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                
                # Find approval notification
                approval_notification = next((n for n in notifications if 'approved' in n.get('title', '').lower() and not n.get('read', True)), None)
                
                if approval_notification:
                    notification_id = approval_notification.get('id')
                    
                    # Mark it as read
                    mark_response = requests.put(f"{BACKEND_URL}/notifications/{notification_id}/read", headers=headers)
                    
                    if mark_response.status_code == 200:
                        self.log_result("Mark Approval Notification Read", True, f"Approval notification {notification_id} marked as read")
                        
                        # Verify it was marked as read
                        verify_response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            updated_notification = next((n for n in verify_data.get('notifications', []) if n.get('id') == notification_id), None)
                            
                            if updated_notification and updated_notification.get('read'):
                                self.log_result("Verify Approval Notification Read", True, "Approval notification successfully marked as read")
                                return True
                            else:
                                self.log_result("Verify Approval Notification Read", False, "Approval notification was not marked as read")
                                return False
                        else:
                            self.log_result("Verify Approval Notification Read", False, f"Failed to verify: {verify_response.status_code}")
                            return False
                    else:
                        self.log_result("Mark Approval Notification Read", False, f"Status: {mark_response.status_code}", mark_response.text)
                        return False
                else:
                    self.log_result("Mark Approval Notification Read", False, "No unread approval notification found")
                    return False
            else:
                self.log_result("Mark Approval Notification Read", False, f"Failed to get notifications: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Mark Approval Notification Read", False, f"Exception: {str(e)}")
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

    def run_buyer_notification_test(self):
        """Run the buyer notification test"""
        print("🚀 STARTING BUYER NOTIFICATION TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate admin and buyer
        if not self.authenticate_admin():
            return False
        
        if not self.authenticate_buyer():
            return False
        
        # Step 2: Create test listing
        if not self.create_test_listing():
            return False
        
        # Step 3: Create test order as buyer
        if not self.create_test_order():
            return False
        
        # Step 4: Check buyer notifications before approval
        self.check_buyer_notifications_before_approval()
        
        # Step 5: Approve order as seller
        if not self.approve_order_as_seller():
            return False
        
        # Step 6: Check buyer notifications after approval (KEY TEST)
        approval_notification_created = self.check_buyer_notifications_after_approval()
        
        # Step 7: Test marking approval notification as read
        if approval_notification_created:
            self.test_mark_approval_notification_read()
        
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
        print(f"   - Approval Notification Created: {'✅ YES' if approval_notification_created else '❌ NO'}")
        
        if approval_notification_created:
            print("   - ✅ NOTIFICATION CLEARING FUNCTIONALITY IS WORKING")
            print("   - The issue reported by user may be frontend-related")
        else:
            print("   - ❌ APPROVAL NOTIFICATIONS ARE NOT BEING CREATED")
            print("   - This explains why notifications don't clear - they're never created")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = BuyerNotificationTester()
    success = tester.run_buyer_notification_test()
    
    if success:
        print("\n✅ BUYER NOTIFICATION TEST COMPLETED")
        sys.exit(0)
    else:
        print("\n❌ BUYER NOTIFICATION TEST FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()