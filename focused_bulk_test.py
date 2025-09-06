#!/usr/bin/env python3
"""
Focused Bulk User Management Test
Testing the bulk user operations with proper user creation and verification
"""

import requests
import json
import uuid
import time
from datetime import datetime

BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

def log_test(test_name, success, details="", error_msg=""):
    """Log test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    if error_msg:
        print(f"   Error: {error_msg}")
    print()

def create_test_user():
    """Create a single test user and return the ID"""
    try:
        test_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"bulktest_{test_id}",
            "email": f"bulktest_{test_id}@example.com",
            "full_name": f"Bulk Test User {test_id}",
            "password": "TestPassword123!"
        }
        
        response = requests.post(f"{BACKEND_URL}/admin/users", json=user_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            user_id = user.get('id')
            print(f"Created test user: {user_id} ({user_data['username']})")
            return user_id
        else:
            print(f"Failed to create user: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error creating test user: {e}")
        return None

def test_bulk_delete():
    """Test bulk delete operation with real users"""
    print("🗑️ TESTING BULK DELETE OPERATION")
    print("-" * 40)
    
    # Create 3 test users
    user_ids = []
    for i in range(3):
        user_id = create_test_user()
        if user_id:
            user_ids.append(user_id)
    
    if len(user_ids) < 2:
        log_test("Bulk Delete Operation", False, error_msg="Could not create enough test users")
        return False
    
    # Test bulk delete with first 2 users
    delete_user_ids = user_ids[:2]
    
    try:
        bulk_data = {
            "action": "delete",
            "user_ids": delete_user_ids
        }
        
        print(f"Attempting to delete users: {delete_user_ids}")
        response = requests.post(f"{BACKEND_URL}/admin/users/bulk-action", json=bulk_data, timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            success_count = results.get('success_count', 0)
            failed_count = results.get('failed_count', 0)
            errors = results.get('errors', [])
            
            # Verify users are actually deleted by checking if they still exist
            deleted_count = 0
            all_users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=5)
            if all_users_response.status_code == 200:
                all_users = all_users_response.json()
                for user_id in delete_user_ids:
                    user_exists = any(user.get('id') == user_id for user in all_users)
                    if not user_exists:
                        deleted_count += 1
            
            log_test(
                "Bulk Delete Operation", 
                success_count == len(delete_user_ids),
                f"API reported: {success_count} success, {failed_count} failed. Verified: {deleted_count} users actually deleted. Errors: {errors}"
            )
            
            # Clean up remaining user
            if len(user_ids) > 2:
                requests.delete(f"{BACKEND_URL}/admin/users/{user_ids[2]}", timeout=5)
            
            return success_count == len(delete_user_ids)
        else:
            log_test("Bulk Delete Operation", False, error_msg=f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Bulk Delete Operation", False, error_msg=str(e))
        return False

def test_bulk_activate():
    """Test bulk activate operation"""
    print("✅ TESTING BULK ACTIVATE OPERATION")
    print("-" * 40)
    
    # Create 2 test users
    user_ids = []
    for i in range(2):
        user_id = create_test_user()
        if user_id:
            user_ids.append(user_id)
    
    if len(user_ids) < 2:
        log_test("Bulk Activate Operation", False, error_msg="Could not create enough test users")
        return False
    
    try:
        # First deactivate them
        for user_id in user_ids:
            requests.put(f"{BACKEND_URL}/admin/users/{user_id}", json={"is_active": False}, timeout=5)
        
        # Now test bulk activate
        bulk_data = {
            "action": "activate",
            "user_ids": user_ids
        }
        
        print(f"Attempting to activate users: {user_ids}")
        response = requests.post(f"{BACKEND_URL}/admin/users/bulk-action", json=bulk_data, timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            success_count = results.get('success_count', 0)
            failed_count = results.get('failed_count', 0)
            errors = results.get('errors', [])
            
            # Verify users are actually activated
            activated_count = 0
            all_users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=5)
            if all_users_response.status_code == 200:
                all_users = all_users_response.json()
                for user_id in user_ids:
                    user = next((u for u in all_users if u.get('id') == user_id), None)
                    if user and user.get('is_active', False):
                        activated_count += 1
            
            log_test(
                "Bulk Activate Operation", 
                success_count == len(user_ids),
                f"API reported: {success_count} success, {failed_count} failed. Verified: {activated_count} users actually activated. Errors: {errors}"
            )
            
            # Clean up
            for user_id in user_ids:
                requests.delete(f"{BACKEND_URL}/admin/users/{user_id}", timeout=5)
            
            return success_count == len(user_ids)
        else:
            log_test("Bulk Activate Operation", False, error_msg=f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Bulk Activate Operation", False, error_msg=str(e))
        return False

def test_bulk_approve():
    """Test bulk approve operation"""
    print("👍 TESTING BULK APPROVE OPERATION")
    print("-" * 40)
    
    # Create 2 test users
    user_ids = []
    for i in range(2):
        user_id = create_test_user()
        if user_id:
            user_ids.append(user_id)
    
    if len(user_ids) < 2:
        log_test("Bulk Approve Operation", False, error_msg="Could not create enough test users")
        return False
    
    try:
        # First set them to pending status
        for user_id in user_ids:
            requests.put(f"{BACKEND_URL}/admin/users/{user_id}", json={"registration_status": "Pending"}, timeout=5)
        
        # Now test bulk approve
        bulk_data = {
            "action": "approve",
            "user_ids": user_ids
        }
        
        print(f"Attempting to approve users: {user_ids}")
        response = requests.post(f"{BACKEND_URL}/admin/users/bulk-action", json=bulk_data, timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            success_count = results.get('success_count', 0)
            failed_count = results.get('failed_count', 0)
            errors = results.get('errors', [])
            
            # Verify users are actually approved
            approved_count = 0
            all_users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=5)
            if all_users_response.status_code == 200:
                all_users = all_users_response.json()
                for user_id in user_ids:
                    user = next((u for u in all_users if u.get('id') == user_id), None)
                    if user and user.get('registration_status') == 'Approved':
                        approved_count += 1
            
            log_test(
                "Bulk Approve Operation", 
                success_count == len(user_ids),
                f"API reported: {success_count} success, {failed_count} failed. Verified: {approved_count} users actually approved. Errors: {errors}"
            )
            
            # Clean up
            for user_id in user_ids:
                requests.delete(f"{BACKEND_URL}/admin/users/{user_id}", timeout=5)
            
            return success_count == len(user_ids)
        else:
            log_test("Bulk Approve Operation", False, error_msg=f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Bulk Approve Operation", False, error_msg=str(e))
        return False

def test_error_handling():
    """Test error handling scenarios"""
    print("⚠️ TESTING ERROR HANDLING")
    print("-" * 40)
    
    try:
        # Test 1: Invalid action
        response1 = requests.post(
            f"{BACKEND_URL}/admin/users/bulk-action",
            json={"action": "invalid_action", "user_ids": ["test1", "test2"]},
            timeout=10
        )
        
        print(f"Invalid action test - Status: {response1.status_code}, Response: {response1.text}")
        
        # Test 2: Missing parameters
        response2 = requests.post(
            f"{BACKEND_URL}/admin/users/bulk-action",
            json={"action": "delete"},  # Missing user_ids
            timeout=10
        )
        
        print(f"Missing params test - Status: {response2.status_code}, Response: {response2.text}")
        
        # Test 3: Non-existent users
        response3 = requests.post(
            f"{BACKEND_URL}/admin/users/bulk-action",
            json={"action": "delete", "user_ids": ["nonexistent1", "nonexistent2"]},
            timeout=10
        )
        
        print(f"Non-existent users test - Status: {response3.status_code}, Response: {response3.text}")
        
        # Evaluate results
        invalid_action_handled = response1.status_code == 200  # Should return success with errors
        missing_params_handled = response2.status_code == 400  # Should return bad request
        nonexistent_handled = response3.status_code == 200  # Should return success with failed_count
        
        if response3.status_code == 200:
            data3 = response3.json()
            results3 = data3.get('results', {})
            failed_count = results3.get('failed_count', 0)
            nonexistent_handled = failed_count > 0
        
        log_test(
            "Error Handling", 
            invalid_action_handled and missing_params_handled and nonexistent_handled,
            f"Invalid action: {invalid_action_handled}, Missing params: {missing_params_handled}, Non-existent users: {nonexistent_handled}"
        )
        
        return invalid_action_handled and missing_params_handled and nonexistent_handled
        
    except Exception as e:
        log_test("Error Handling", False, error_msg=str(e))
        return False

def main():
    """Run focused bulk user management tests"""
    print("=" * 80)
    print("FOCUSED BULK USER MANAGEMENT TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Started: {datetime.now().isoformat()}")
    print()
    
    # Health check
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            log_test("Health Check", True, "Backend is healthy")
        else:
            log_test("Health Check", False, f"HTTP {response.status_code}")
            return
    except Exception as e:
        log_test("Health Check", False, error_msg=str(e))
        return
    
    # Run tests
    results = []
    results.append(test_bulk_delete())
    results.append(test_bulk_activate())
    results.append(test_bulk_approve())
    results.append(test_error_handling())
    
    # Summary
    passed = sum(results)
    total = len(results)
    failed = total - passed
    
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total + 1}")  # +1 for health check
    print(f"Passed: {passed + 1} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {((passed + 1)/(total + 1)*100):.1f}%")
    print()
    
    if failed > 0:
        print("Some tests failed. Check the details above.")
    else:
        print("🎉 All bulk user management tests passed!")

if __name__ == "__main__":
    main()