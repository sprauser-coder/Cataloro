#!/usr/bin/env python3
"""
Final Comprehensive Profile Endpoints Test
Tests all aspects of profile functionality as requested in the review
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "https://marketplace-fix-4.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def run_final_profile_test():
    """Run comprehensive profile endpoint tests"""
    print("🎯 FINAL COMPREHENSIVE PROFILE ENDPOINTS TEST")
    print("=" * 60)
    print("Testing as requested in review:")
    print("1. GET /api/profile - Verify user_id field returns correctly")
    print("2. PUT /api/profile - Test profile updates persist correctly")
    print("=" * 60)
    
    # Authenticate
    print("\n🔐 Step 1: Authentication")
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.text}")
        return False
    
    token_data = response.json()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    print(f"✅ Authenticated as: {token_data['user']['email']}")
    
    # Test 1: GET /api/profile - user_id field verification
    print("\n📋 Step 2: Testing GET /api/profile - user_id field verification")
    profile_response = requests.get(f"{BACKEND_URL}/profile", headers=headers)
    
    if profile_response.status_code != 200:
        print(f"❌ GET /profile failed: {profile_response.text}")
        return False
    
    profile_data = profile_response.json()
    user_id = profile_data.get('user_id')
    
    if not user_id:
        print("❌ CRITICAL: user_id field is missing from GET /profile response")
        return False
    
    print(f"✅ user_id field present: {user_id}")
    print(f"✅ GET /profile working correctly")
    
    # Store original values for comparison
    original_phone = profile_data.get('phone')
    original_bio = profile_data.get('bio')
    original_location = profile_data.get('location')
    
    print(f"\n📊 Current Profile State:")
    print(f"   user_id: {user_id}")
    print(f"   phone: {original_phone}")
    print(f"   bio: {original_bio}")
    print(f"   location: {original_location}")
    
    # Test 2: PUT /api/profile - Profile update persistence
    print("\n✏️  Step 3: Testing PUT /api/profile - Profile update persistence")
    
    # Test data with timestamp to ensure uniqueness
    timestamp = int(time.time())
    test_updates = {
        "phone": f"+1-555-{timestamp % 10000:04d}",
        "bio": f"Profile test bio updated at {timestamp}",
        "location": f"Test Location {timestamp}"
    }
    
    print(f"Updating profile with test data:")
    for field, value in test_updates.items():
        print(f"   {field}: {value}")
    
    # Make the update
    update_response = requests.put(f"{BACKEND_URL}/profile", json=test_updates, headers=headers)
    
    if update_response.status_code != 200:
        print(f"❌ PUT /profile failed: {update_response.text}")
        return False
    
    updated_profile = update_response.json()
    print("✅ PUT /profile request successful")
    
    # Verify updates were applied in the response
    update_success = True
    for field, expected_value in test_updates.items():
        actual_value = updated_profile.get(field)
        if actual_value == expected_value:
            print(f"   ✅ {field} updated correctly: {actual_value}")
        else:
            print(f"   ❌ {field} update failed: expected '{expected_value}', got '{actual_value}'")
            update_success = False
    
    # Verify user_id is still present
    updated_user_id = updated_profile.get('user_id')
    if updated_user_id == user_id:
        print(f"   ✅ user_id preserved: {updated_user_id}")
    else:
        print(f"   ❌ user_id changed or missing: expected '{user_id}', got '{updated_user_id}'")
        update_success = False
    
    if not update_success:
        print("❌ Profile update verification failed")
        return False
    
    # Test 3: Persistence verification - Get profile again
    print("\n🔄 Step 4: Testing data persistence - GET /profile again")
    
    # Small delay to ensure database consistency
    time.sleep(1)
    
    persistence_response = requests.get(f"{BACKEND_URL}/profile", headers=headers)
    
    if persistence_response.status_code != 200:
        print(f"❌ Persistence check failed: {persistence_response.text}")
        return False
    
    persisted_profile = persistence_response.json()
    
    # Verify all updates persisted
    persistence_success = True
    for field, expected_value in test_updates.items():
        actual_value = persisted_profile.get(field)
        if actual_value == expected_value:
            print(f"   ✅ {field} persisted correctly: {actual_value}")
        else:
            print(f"   ❌ {field} persistence failed: expected '{expected_value}', got '{actual_value}'")
            persistence_success = False
    
    # Verify user_id persisted
    persisted_user_id = persisted_profile.get('user_id')
    if persisted_user_id == user_id:
        print(f"   ✅ user_id persisted correctly: {persisted_user_id}")
    else:
        print(f"   ❌ user_id persistence failed: expected '{user_id}', got '{persisted_user_id}'")
        persistence_success = False
    
    # Check updated_at timestamp
    updated_at = persisted_profile.get('updated_at')
    if updated_at:
        print(f"   ✅ updated_at timestamp present: {updated_at}")
    else:
        print("   ⚠️  updated_at timestamp missing")
    
    if not persistence_success:
        print("❌ Data persistence verification failed")
        return False
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 FINAL TEST RESULTS")
    print("=" * 60)
    print("✅ GET /api/profile - user_id field returns correctly")
    print("✅ PUT /api/profile - Profile updates work correctly")
    print("✅ Data persistence - All changes persist correctly")
    print("✅ user_id field - Preserved through all operations")
    print("\n🏆 ALL PROFILE ENDPOINT TESTS PASSED")
    print("📝 The reported bug 'profile changes not saved and missing user number display' appears to be RESOLVED")
    
    return True

if __name__ == "__main__":
    success = run_final_profile_test()
    if success:
        print("\n✅ Profile endpoints are working correctly!")
        exit(0)
    else:
        print("\n❌ Profile endpoints have issues!")
        exit(1)