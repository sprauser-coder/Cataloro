#!/usr/bin/env python3
"""
Multi-Endpoint Deletion Testing
Tests the enhanced multi-endpoint deletion logic specifically
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class MultiEndpointDeletionTester:
    def __init__(self, base_url="https://admanager-cataloro.preview.emergentagent.com"):
        self.base_url = base_url
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:100]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_user(self):
        """Setup regular user for testing"""
        print("\n🔐 Setting up test user...")
        
        success, response = self.run_test(
            "Regular User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "demo@cataloro.com", "password": "demo123"}
        )
        
        if success and 'user' in response:
            self.regular_user = response['user']
            print(f"   User ID: {self.regular_user['id']}")
            return True
        
        return False

    def test_multi_endpoint_deletion(self):
        """Test the multi-endpoint deletion approach"""
        print("\n🎯 Testing Multi-Endpoint Deletion Logic...")
        
        if not self.regular_user:
            print("❌ Cannot test - no user")
            return False
        
        user_id = self.regular_user['id']
        
        # Create a test notification
        notification_data = {
            "title": "Multi-Endpoint Test",
            "message": "Testing multi-endpoint deletion approach.",
            "type": "order_complete",
            "archived": False
        }
        
        success, response = self.run_test(
            "Create Test Notification",
            "POST",
            f"api/user/{user_id}/notifications",
            200,
            data=notification_data
        )
        
        if not success or 'id' not in response:
            print("❌ Failed to create test notification")
            return False
        
        notification_id = response['id']
        print(f"   📝 Created notification: {notification_id}")
        
        # Test all deletion endpoints as per the enhanced system
        deletion_endpoints = [
            {
                "name": "User-Scoped Endpoint",
                "endpoint": f"api/user/{user_id}/notifications/{notification_id}",
                "description": "Standard user-scoped deletion"
            },
            {
                "name": "General Endpoint with User ID",
                "endpoint": f"api/notifications/{notification_id}?user_id={user_id}",
                "description": "General endpoint with user_id parameter"
            },
            {
                "name": "System Notifications Endpoint",
                "endpoint": f"api/user/{user_id}/system-notifications/{notification_id}",
                "description": "System notifications specific endpoint"
            }
        ]
        
        # Test each endpoint (we'll create multiple notifications to test each)
        endpoint_results = []
        
        for i, endpoint_info in enumerate(deletion_endpoints):
            # Create a new notification for each endpoint test
            test_notification_data = {
                "title": f"Endpoint Test {i+1}",
                "message": f"Testing {endpoint_info['name']} deletion.",
                "type": "order_complete",
                "archived": False
            }
            
            create_success, create_response = self.run_test(
                f"Create Notification for {endpoint_info['name']}",
                "POST",
                f"api/user/{user_id}/notifications",
                200,
                data=test_notification_data
            )
            
            if create_success and 'id' in create_response:
                test_notification_id = create_response['id']
                
                # Replace the notification_id in the endpoint with the actual test notification ID
                test_endpoint = endpoint_info['endpoint'].replace(notification_id, test_notification_id)
                
                # Test deletion
                delete_success, delete_response = self.run_test(
                    f"Delete via {endpoint_info['name']}",
                    "DELETE",
                    test_endpoint,
                    200
                )
                
                endpoint_results.append({
                    'name': endpoint_info['name'],
                    'endpoint': test_endpoint,
                    'success': delete_success,
                    'description': endpoint_info['description']
                })
                
                if delete_success:
                    print(f"   ✅ {endpoint_info['name']} deletion successful")
                    
                    # Verify deletion
                    verify_success, verify_response = self.run_test(
                        f"Verify {endpoint_info['name']} Deletion",
                        "GET",
                        f"api/user/{user_id}/notifications",
                        200
                    )
                    
                    if verify_success:
                        still_exists = any(n.get('id') == test_notification_id for n in verify_response)
                        if not still_exists:
                            print(f"   ✅ Deletion verified - notification removed")
                        else:
                            print(f"   ❌ Deletion failed - notification still exists")
                else:
                    print(f"   ❌ {endpoint_info['name']} deletion failed")
        
        # Summary
        successful_endpoints = sum(1 for result in endpoint_results if result['success'])
        total_endpoints = len(endpoint_results)
        
        print(f"\n   📊 Multi-Endpoint Deletion Results:")
        for result in endpoint_results:
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print(f"      {result['name']}: {status}")
            print(f"         Endpoint: {result['endpoint']}")
            print(f"         Description: {result['description']}")
        
        self.log_test("Multi-Endpoint Deletion Logic", successful_endpoints > 0,
                     f"Working endpoints: {successful_endpoints}/{total_endpoints}")
        
        return successful_endpoints > 0

    def test_handleSingleDelete_simulation(self):
        """Simulate the handleSingleDelete function logic"""
        print("\n🔄 Testing handleSingleDelete Function Simulation...")
        
        if not self.regular_user:
            print("❌ Cannot test - no user")
            return False
        
        user_id = self.regular_user['id']
        
        # Create test notification
        notification_data = {
            "title": "HandleSingleDelete Test",
            "message": "Testing handleSingleDelete function simulation.",
            "type": "order_complete",
            "archived": False
        }
        
        success, response = self.run_test(
            "Create Notification for handleSingleDelete",
            "POST",
            f"api/user/{user_id}/notifications",
            200,
            data=notification_data
        )
        
        if not success or 'id' not in response:
            print("❌ Failed to create test notification")
            return False
        
        notification_id = response['id']
        print(f"   📝 Created notification for handleSingleDelete test: {notification_id}")
        
        # Simulate the handleSingleDelete function logic
        # Try multiple endpoints in order until one succeeds
        deletion_endpoints = [
            f"api/user/{user_id}/notifications/{notification_id}",
            f"api/notifications/{notification_id}?user_id={user_id}",
            f"api/user/{user_id}/system-notifications/{notification_id}"
        ]
        
        deletion_success = False
        successful_endpoint = None
        
        print(f"   🔄 Simulating handleSingleDelete logic...")
        
        for i, endpoint in enumerate(deletion_endpoints):
            print(f"      Attempt {i+1}: {endpoint}")
            
            success, response = self.run_test(
                f"handleSingleDelete Attempt {i+1}",
                "DELETE",
                endpoint,
                200
            )
            
            if success:
                deletion_success = True
                successful_endpoint = endpoint
                print(f"      ✅ Success on attempt {i+1}")
                break
            else:
                print(f"      ❌ Failed on attempt {i+1}")
        
        if deletion_success:
            print(f"   ✅ handleSingleDelete simulation successful via: {successful_endpoint}")
            
            # Verify deletion
            verify_success, verify_response = self.run_test(
                "Verify handleSingleDelete Deletion",
                "GET",
                f"api/user/{user_id}/notifications",
                200
            )
            
            if verify_success:
                still_exists = any(n.get('id') == notification_id for n in verify_response)
                verification_success = not still_exists
                self.log_test("handleSingleDelete Verification", verification_success,
                             f"Notification {'still exists' if still_exists else 'successfully deleted'}")
        else:
            print(f"   ❌ handleSingleDelete simulation failed - no endpoint worked")
        
        self.log_test("handleSingleDelete Function Simulation", deletion_success,
                     f"Successful endpoint: {successful_endpoint if successful_endpoint else 'None'}")
        
        return deletion_success

    def test_enhanced_error_handling(self):
        """Test enhanced error handling and feedback"""
        print("\n⚠️ Testing Enhanced Error Handling...")
        
        if not self.regular_user:
            print("❌ Cannot test - no user")
            return False
        
        user_id = self.regular_user['id']
        
        # Test 1: Try to delete non-existent notification
        fake_notification_id = str(uuid.uuid4())
        
        endpoints_to_test = [
            f"api/user/{user_id}/notifications/{fake_notification_id}",
            f"api/notifications/{fake_notification_id}?user_id={user_id}"
        ]
        
        error_handling_results = []
        
        for endpoint in endpoints_to_test:
            success, response = self.run_test(
                f"Delete Non-Existent Notification via {endpoint.split('/')[-2]}",
                "DELETE",
                endpoint,
                404  # Expecting 404 for non-existent notification
            )
            
            error_handling_results.append(success)
            
            if success:
                print(f"   ✅ Proper 404 error handling for: {endpoint}")
            else:
                print(f"   ❌ Incorrect error handling for: {endpoint}")
        
        # Test 2: Try to delete with wrong user ID
        # First create a notification
        notification_data = {
            "title": "Error Handling Test",
            "message": "Testing error handling with wrong user ID.",
            "type": "system",
            "archived": False
        }
        
        create_success, create_response = self.run_test(
            "Create Notification for Error Test",
            "POST",
            f"api/user/{user_id}/notifications",
            200,
            data=notification_data
        )
        
        if create_success and 'id' in create_response:
            notification_id = create_response['id']
            wrong_user_id = str(uuid.uuid4())
            
            # Try to delete with wrong user ID
            wrong_user_success, wrong_user_response = self.run_test(
                "Delete with Wrong User ID",
                "DELETE",
                f"api/user/{wrong_user_id}/notifications/{notification_id}",
                404  # Expecting 404 for wrong user
            )
            
            error_handling_results.append(wrong_user_success)
            
            # Clean up - delete the test notification properly
            self.run_test(
                "Cleanup Error Test Notification",
                "DELETE",
                f"api/user/{user_id}/notifications/{notification_id}",
                200
            )
        
        successful_error_handling = sum(error_handling_results)
        total_error_tests = len(error_handling_results)
        
        self.log_test("Enhanced Error Handling", successful_error_handling > 0,
                     f"Proper error responses: {successful_error_handling}/{total_error_tests}")
        
        return successful_error_handling > 0

    def run_comprehensive_test(self):
        """Run comprehensive multi-endpoint deletion testing"""
        print("🎯 MULTI-ENDPOINT DELETION TESTING")
        print("=" * 50)
        
        # Setup
        if not self.setup_user():
            print("❌ Failed to setup user - stopping tests")
            return False
        
        # Test sequence
        test_results = []
        
        # 1. Test multi-endpoint deletion
        test_results.append(self.test_multi_endpoint_deletion())
        
        # 2. Test handleSingleDelete simulation
        test_results.append(self.test_handleSingleDelete_simulation())
        
        # 3. Test enhanced error handling
        test_results.append(self.test_enhanced_error_handling())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"\n📊 MULTI-ENDPOINT TEST SUMMARY")
        print("=" * 40)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"Major Test Categories: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL MULTI-ENDPOINT DELETION TESTS PASSED!")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} major test categories failed")
            return False

if __name__ == "__main__":
    tester = MultiEndpointDeletionTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)