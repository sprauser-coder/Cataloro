#!/usr/bin/env python3
"""
Header Logo Size Field Testing
Test the new header_logo_size field in CMS settings endpoint
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-market.preview.emergentagent.com/api"

# Admin credentials
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def log_test(message, status="INFO"):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def authenticate_admin():
    """Authenticate as admin and return token"""
    log_test("Authenticating as admin...")
    
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            log_test("✅ Admin authentication successful", "SUCCESS")
            return token
        else:
            log_test(f"❌ Admin authentication failed: {response.status_code} - {response.text}", "ERROR")
            return None
    except Exception as e:
        log_test(f"❌ Admin authentication error: {str(e)}", "ERROR")
        return None

def test_header_logo_size_field():
    """Test header_logo_size field functionality"""
    log_test("=== HEADER LOGO SIZE FIELD TESTING ===")
    
    # Authenticate admin
    admin_token = authenticate_admin()
    if not admin_token:
        log_test("❌ Cannot proceed without admin authentication", "ERROR")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    test_results = []
    
    # Test 1: GET /api/cms/settings - Check default header_logo_size value
    log_test("Test 1: Checking default header_logo_size value...")
    try:
        response = requests.get(f"{BACKEND_URL}/cms/settings")
        if response.status_code == 200:
            settings = response.json()
            header_logo_size = settings.get("header_logo_size")
            
            if header_logo_size == "h-8":
                log_test("✅ Default header_logo_size value is correct: 'h-8'", "SUCCESS")
                test_results.append(True)
            else:
                log_test(f"❌ Default header_logo_size value incorrect. Expected: 'h-8', Got: '{header_logo_size}'", "ERROR")
                test_results.append(False)
        else:
            log_test(f"❌ Failed to get CMS settings: {response.status_code} - {response.text}", "ERROR")
            test_results.append(False)
    except Exception as e:
        log_test(f"❌ Error getting CMS settings: {str(e)}", "ERROR")
        test_results.append(False)
    
    # Test 2: PUT /api/admin/cms/settings - Update header_logo_size to 'h-12'
    log_test("Test 2: Updating header_logo_size to 'h-12'...")
    try:
        update_data = {
            "header_logo_size": "h-12"
        }
        
        response = requests.put(f"{BACKEND_URL}/admin/cms/settings", json=update_data, headers=headers)
        if response.status_code == 200:
            log_test("✅ Successfully updated header_logo_size to 'h-12'", "SUCCESS")
            test_results.append(True)
        else:
            log_test(f"❌ Failed to update header_logo_size: {response.status_code} - {response.text}", "ERROR")
            test_results.append(False)
    except Exception as e:
        log_test(f"❌ Error updating header_logo_size: {str(e)}", "ERROR")
        test_results.append(False)
    
    # Test 3: GET /api/cms/settings - Verify updated header_logo_size persists
    log_test("Test 3: Verifying updated header_logo_size persists...")
    try:
        response = requests.get(f"{BACKEND_URL}/cms/settings")
        if response.status_code == 200:
            settings = response.json()
            header_logo_size = settings.get("header_logo_size")
            
            if header_logo_size == "h-12":
                log_test("✅ Updated header_logo_size value persists correctly: 'h-12'", "SUCCESS")
                test_results.append(True)
            else:
                log_test(f"❌ Updated header_logo_size value not persisted. Expected: 'h-12', Got: '{header_logo_size}'", "ERROR")
                test_results.append(False)
        else:
            log_test(f"❌ Failed to get CMS settings after update: {response.status_code} - {response.text}", "ERROR")
            test_results.append(False)
    except Exception as e:
        log_test(f"❌ Error getting CMS settings after update: {str(e)}", "ERROR")
        test_results.append(False)
    
    # Test 4: PUT /api/admin/cms/settings - Test different header_logo_size values
    log_test("Test 4: Testing different header_logo_size values...")
    test_values = ["h-6", "h-10", "h-16"]
    
    for test_value in test_values:
        try:
            update_data = {
                "header_logo_size": test_value
            }
            
            response = requests.put(f"{BACKEND_URL}/admin/cms/settings", json=update_data, headers=headers)
            if response.status_code == 200:
                # Verify the value was saved
                verify_response = requests.get(f"{BACKEND_URL}/cms/settings")
                if verify_response.status_code == 200:
                    settings = verify_response.json()
                    saved_value = settings.get("header_logo_size")
                    
                    if saved_value == test_value:
                        log_test(f"✅ Successfully updated and verified header_logo_size: '{test_value}'", "SUCCESS")
                        test_results.append(True)
                    else:
                        log_test(f"❌ header_logo_size not saved correctly. Expected: '{test_value}', Got: '{saved_value}'", "ERROR")
                        test_results.append(False)
                else:
                    log_test(f"❌ Failed to verify header_logo_size after update to '{test_value}'", "ERROR")
                    test_results.append(False)
            else:
                log_test(f"❌ Failed to update header_logo_size to '{test_value}': {response.status_code}", "ERROR")
                test_results.append(False)
        except Exception as e:
            log_test(f"❌ Error testing header_logo_size value '{test_value}': {str(e)}", "ERROR")
            test_results.append(False)
    
    # Test 5: Verify admin authentication is required for updates
    log_test("Test 5: Verifying admin authentication is required...")
    try:
        update_data = {
            "header_logo_size": "h-8"
        }
        
        # Try without authentication
        response = requests.put(f"{BACKEND_URL}/admin/cms/settings", json=update_data)
        if response.status_code == 403 or response.status_code == 401:
            log_test("✅ Admin authentication properly required for CMS settings updates", "SUCCESS")
            test_results.append(True)
        else:
            log_test(f"❌ Admin authentication not properly enforced: {response.status_code}", "ERROR")
            test_results.append(False)
    except Exception as e:
        log_test(f"❌ Error testing admin authentication requirement: {str(e)}", "ERROR")
        test_results.append(False)
    
    # Test 6: Reset to default value
    log_test("Test 6: Resetting header_logo_size to default value...")
    try:
        update_data = {
            "header_logo_size": "h-8"
        }
        
        response = requests.put(f"{BACKEND_URL}/admin/cms/settings", json=update_data, headers=headers)
        if response.status_code == 200:
            log_test("✅ Successfully reset header_logo_size to default 'h-8'", "SUCCESS")
            test_results.append(True)
        else:
            log_test(f"❌ Failed to reset header_logo_size: {response.status_code}", "ERROR")
            test_results.append(False)
    except Exception as e:
        log_test(f"❌ Error resetting header_logo_size: {str(e)}", "ERROR")
        test_results.append(False)
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    log_test("=== HEADER LOGO SIZE FIELD TEST SUMMARY ===")
    log_test(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        log_test("🎉 ALL TESTS PASSED - Header logo size field is working correctly!", "SUCCESS")
        return True
    else:
        log_test("❌ SOME TESTS FAILED - Header logo size field has issues", "ERROR")
        return False

if __name__ == "__main__":
    print("Header Logo Size Field Testing")
    print("=" * 50)
    
    success = test_header_logo_size_field()
    
    if success:
        print("\n✅ Header logo size field testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Header logo size field testing failed!")
        sys.exit(1)