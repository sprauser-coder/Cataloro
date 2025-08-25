#!/usr/bin/env python3
"""
Profile Endpoints Testing Script
Tests GET /api/profile and PUT /api/profile endpoints specifically for:
1. user_id field presence and correctness
2. Profile update functionality and data persistence
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://cataloro-market.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class ProfileTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_data = None
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print("🔐 Authenticating with admin credentials...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user_data = data["user"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print(f"✅ Authentication successful for user: {self.user_data.get('email')}")
                print(f"   User ID: {self.user_data.get('user_id', 'NOT_SET')}")
                print(f"   Role: {self.user_data.get('role')}")
                return True
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_get_profile(self):
        """Test GET /api/profile endpoint"""
        print("\n📋 Testing GET /api/profile endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/profile")
            print(f"GET /profile response status: {response.status_code}")
            
            if response.status_code == 200:
                profile_data = response.json()
                print("✅ GET /profile successful")
                
                # Check for user_id field
                user_id = profile_data.get('user_id')
                if user_id:
                    print(f"✅ user_id field present: {user_id}")
                    if user_id.startswith('U') and len(user_id) == 6:
                        print("✅ user_id format is correct (U00001 format)")
                    else:
                        print(f"⚠️  user_id format may be incorrect: {user_id}")
                else:
                    print("❌ user_id field missing or empty")
                
                # Display all profile fields
                print("\n📊 Current Profile Data:")
                for key, value in profile_data.items():
                    print(f"   {key}: {value}")
                
                return profile_data
            else:
                print(f"❌ GET /profile failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ GET /profile error: {str(e)}")
            return None
    
    def test_put_profile_updates(self):
        """Test PUT /api/profile endpoint with various updates"""
        print("\n✏️  Testing PUT /api/profile endpoint...")
        
        # Test data for profile updates
        test_updates = [
            {
                "name": "Phone Update",
                "data": {"phone": "+1-555-0123"},
                "expected_field": "phone"
            },
            {
                "name": "Bio Update", 
                "data": {"bio": "Updated bio for testing profile persistence"},
                "expected_field": "bio"
            },
            {
                "name": "Location Update",
                "data": {"location": "Test City, Test State"},
                "expected_field": "location"
            },
            {
                "name": "Full Name Update",
                "data": {"full_name": "Updated Admin Name"},
                "expected_field": "full_name"
            },
            {
                "name": "Multiple Fields Update",
                "data": {
                    "phone": "+1-555-9999",
                    "bio": "Multi-field update test bio",
                    "location": "Multi-Update City"
                },
                "expected_field": "multiple"
            }
        ]
        
        results = []
        
        for test_case in test_updates:
            print(f"\n🧪 Testing {test_case['name']}...")
            
            try:
                # Make the update request
                response = self.session.put(f"{BACKEND_URL}/profile", json=test_case['data'])
                print(f"PUT /profile response status: {response.status_code}")
                
                if response.status_code == 200:
                    updated_profile = response.json()
                    print(f"✅ {test_case['name']} successful")
                    
                    # Verify the update was applied
                    success = True
                    for field, expected_value in test_case['data'].items():
                        actual_value = updated_profile.get(field)
                        if actual_value == expected_value:
                            print(f"   ✅ {field}: {actual_value}")
                        else:
                            print(f"   ❌ {field}: expected '{expected_value}', got '{actual_value}'")
                            success = False
                    
                    # Check if user_id is still present after update
                    user_id = updated_profile.get('user_id')
                    if user_id:
                        print(f"   ✅ user_id preserved: {user_id}")
                    else:
                        print("   ❌ user_id missing after update")
                        success = False
                    
                    results.append({
                        "test": test_case['name'],
                        "success": success,
                        "profile_data": updated_profile
                    })
                    
                else:
                    print(f"❌ {test_case['name']} failed: {response.text}")
                    results.append({
                        "test": test_case['name'],
                        "success": False,
                        "error": response.text
                    })
                    
            except Exception as e:
                print(f"❌ {test_case['name']} error: {str(e)}")
                results.append({
                    "test": test_case['name'],
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def test_profile_persistence(self):
        """Test if profile changes persist by getting profile after updates"""
        print("\n🔄 Testing Profile Data Persistence...")
        
        # Get current profile to verify persistence
        current_profile = self.test_get_profile()
        
        if current_profile:
            print("\n📊 Final Profile State After All Updates:")
            for key, value in current_profile.items():
                print(f"   {key}: {value}")
            
            # Check if updated_at field is recent
            updated_at = current_profile.get('updated_at')
            if updated_at:
                print(f"✅ Profile has updated_at timestamp: {updated_at}")
            else:
                print("⚠️  No updated_at timestamp found")
            
            return current_profile
        else:
            print("❌ Could not retrieve profile for persistence check")
            return None
    
    def run_comprehensive_test(self):
        """Run all profile endpoint tests"""
        print("🚀 Starting Comprehensive Profile Endpoints Testing")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test GET /profile
        initial_profile = self.test_get_profile()
        if not initial_profile:
            print("❌ GET /profile failed. Cannot proceed with update tests.")
            return False
        
        # Step 3: Test PUT /profile updates
        update_results = self.test_put_profile_updates()
        
        # Step 4: Test persistence
        final_profile = self.test_profile_persistence()
        
        # Step 5: Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        successful_tests = sum(1 for result in update_results if result['success'])
        total_tests = len(update_results)
        
        print(f"Profile Update Tests: {successful_tests}/{total_tests} passed")
        
        # Check critical issues
        critical_issues = []
        
        if not initial_profile.get('user_id'):
            critical_issues.append("user_id field missing in GET /profile")
        
        if final_profile and not final_profile.get('user_id'):
            critical_issues.append("user_id field missing after updates")
        
        failed_updates = [result for result in update_results if not result['success']]
        if failed_updates:
            critical_issues.append(f"{len(failed_updates)} profile update(s) failed")
        
        if critical_issues:
            print("\n❌ CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   • {issue}")
            return False
        else:
            print("\n✅ ALL TESTS PASSED - Profile endpoints working correctly")
            return True

def main():
    """Main test execution"""
    tester = ProfileTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 Profile endpoints testing completed successfully!")
        exit(0)
    else:
        print("\n💥 Profile endpoints testing found issues!")
        exit(1)

if __name__ == "__main__":
    main()