#!/usr/bin/env python3
"""
Clear Notifications Endpoint Testing
====================================

This script tests the new clear notifications endpoint functionality:
1. GET /api/notifications - Check existing notifications
2. DELETE /api/notifications/clear-all - Test the new clear all notifications endpoint
3. GET /api/notifications - Verify notifications are permanently cleared

Admin credentials: admin@marketplace.com / admin123
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://cataloro-profile-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class NotificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Failed to authenticate: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_notifications(self, test_name="Get Notifications"):
        """Get current notifications"""
        try:
            response = self.session.get(f"{BACKEND_URL}/notifications")
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                unread_count = data.get("unread_count", 0)
                
                self.log_test(test_name, True, 
                    f"Retrieved {len(notifications)} notifications ({unread_count} unread)",
                    {"total_notifications": len(notifications), "unread_count": unread_count})
                return notifications, unread_count
            else:
                self.log_test(test_name, False, f"Failed to get notifications: {response.status_code}", response.text)
                return None, None
                
        except Exception as e:
            self.log_test(test_name, False, f"Error getting notifications: {str(e)}")
            return None, None
    
    def clear_all_notifications(self):
        """Test the clear all notifications endpoint"""
        try:
            response = self.session.delete(f"{BACKEND_URL}/notifications/clear-all")
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get("deleted_count", 0)
                message = data.get("message", "")
                
                self.log_test("Clear All Notifications", True, 
                    f"Successfully cleared {deleted_count} notifications",
                    {"deleted_count": deleted_count, "message": message})
                return deleted_count
            else:
                self.log_test("Clear All Notifications", False, 
                    f"Failed to clear notifications: {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Clear All Notifications", False, f"Error clearing notifications: {str(e)}")
            return None
    
    def create_test_notification(self):
        """Create a test notification by placing an order (if possible)"""
        try:
            # First, get available listings
            response = self.session.get(f"{BACKEND_URL}/listings?limit=1")
            if response.status_code != 200:
                self.log_test("Create Test Notification", False, "Could not get listings to create test notification")
                return False
            
            listings = response.json()
            if not listings:
                self.log_test("Create Test Notification", False, "No listings available to create test notification")
                return False
            
            # Try to create an order to generate a notification
            listing = listings[0]
            if listing.get("listing_type") == "fixed_price" and listing.get("seller_id") != self.get_current_user_id():
                order_data = {
                    "listing_id": listing["id"],
                    "quantity": 1,
                    "shipping_address": "Test Address for Notification"
                }
                
                response = self.session.post(f"{BACKEND_URL}/orders", json=order_data)
                if response.status_code == 200:
                    self.log_test("Create Test Notification", True, "Created test order to generate notification")
                    return True
            
            self.log_test("Create Test Notification", False, "Could not create test notification - no suitable listings")
            return False
            
        except Exception as e:
            self.log_test("Create Test Notification", False, f"Error creating test notification: {str(e)}")
            return False
    
    def get_current_user_id(self):
        """Get current user ID from token"""
        try:
            # Decode the JWT token to get user info (simplified)
            import base64
            if self.admin_token:
                # This is a simplified approach - in production you'd properly decode JWT
                return "admin_user_id"
            return None
        except:
            return None
    
    def run_comprehensive_test(self):
        """Run comprehensive clear notifications test"""
        print("=" * 60)
        print("CLEAR NOTIFICATIONS ENDPOINT TESTING")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Authentication failed. Cannot proceed with testing.")
            return False
        
        print("\n" + "=" * 40)
        print("PHASE 1: Check Initial Notifications")
        print("=" * 40)
        
        # Step 2: Get initial notifications
        initial_notifications, initial_unread = self.get_notifications("Initial Notifications Check")
        if initial_notifications is None:
            print("\n❌ CRITICAL: Cannot retrieve notifications. Testing aborted.")
            return False
        
        print(f"\nFound {len(initial_notifications)} existing notifications ({initial_unread} unread)")
        
        # Step 3: If no notifications exist, try to create some
        if len(initial_notifications) == 0:
            print("\n" + "=" * 40)
            print("PHASE 2: Create Test Notifications")
            print("=" * 40)
            
            print("No existing notifications found. Attempting to create test notifications...")
            self.create_test_notification()
            
            # Check again after attempting to create notifications
            initial_notifications, initial_unread = self.get_notifications("Post-Creation Notifications Check")
        
        print("\n" + "=" * 40)
        print("PHASE 3: Clear All Notifications")
        print("=" * 40)
        
        # Step 4: Clear all notifications
        deleted_count = self.clear_all_notifications()
        if deleted_count is None:
            print("\n❌ CRITICAL: Clear notifications endpoint failed.")
            return False
        
        print("\n" + "=" * 40)
        print("PHASE 4: Verify Notifications Cleared")
        print("=" * 40)
        
        # Step 5: Verify notifications are cleared
        final_notifications, final_unread = self.get_notifications("Post-Clear Notifications Check")
        if final_notifications is None:
            print("\n❌ CRITICAL: Cannot verify notifications after clearing.")
            return False
        
        # Step 6: Validate clearing was successful
        if len(final_notifications) == 0 and final_unread == 0:
            self.log_test("Notification Clearing Verification", True, 
                "All notifications successfully cleared from database")
        else:
            self.log_test("Notification Clearing Verification", False, 
                f"Notifications not fully cleared: {len(final_notifications)} remaining ({final_unread} unread)")
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)
        
        # Return overall success
        return failed == 0

def main():
    """Main test execution"""
    tester = NotificationTester()
    
    try:
        success = tester.run_comprehensive_test()
        overall_success = tester.print_summary()
        
        if overall_success:
            print("🎉 ALL TESTS PASSED - Clear notifications functionality working correctly!")
            sys.exit(0)
        else:
            print("💥 SOME TESTS FAILED - Clear notifications functionality has issues!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()