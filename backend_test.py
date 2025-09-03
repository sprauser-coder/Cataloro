#!/usr/bin/env python3
"""
ADMIN PANEL & PROFILE FIXES COMPREHENSIVE TESTING
Testing critical admin panel and profile fixes as requested in review
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://cataloro-marketplace-2.preview.emergentagent.com/api"

def test_admin_panel_and_profile_fixes():
    """Test the critical admin panel and profile fixes"""
    print("🎯 ADMIN PANEL & PROFILE FIXES COMPREHENSIVE TESTING")
    print("=" * 60)
    
    results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "critical_issues": [],
        "test_details": []
    }
    
    try:
        # Test 1: Admin Login
        print("\n1. 🔐 ADMIN AUTHENTICATION")
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "email": "admin@cataloro.com",
            "password": "admin123"
        })
        
        if login_response.status_code == 200:
            admin_data = login_response.json()
            admin_id = admin_data["user"]["id"]
            print(f"   ✅ Admin login successful - Admin ID: {admin_id}")
            results["tests_passed"] += 1
            results["test_details"].append("✅ Admin authentication successful")
        else:
            print(f"   ❌ Admin login failed: {login_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("Admin authentication failed")
            return results
        
        # Test 2: Dashboard KPI Accuracy
        print("\n2. 📊 DASHBOARD KPI ACCURACY TEST")
        dashboard_response = requests.get(f"{BACKEND_URL}/admin/dashboard")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            kpis = dashboard_data.get("kpis", {})
            
            print(f"   ✅ Dashboard endpoint accessible")
            print(f"   📈 KPI Data:")
            print(f"      - Total Users: {kpis.get('total_users', 0)}")
            print(f"      - Total Listings: {kpis.get('total_listings', 0)}")
            print(f"      - Active Listings: {kpis.get('active_listings', 0)}")
            print(f"      - Total Deals: {kpis.get('total_deals', 0)}")
            print(f"      - Revenue: €{kpis.get('revenue', 0)}")
            print(f"      - Growth Rate: {kpis.get('growth_rate', 0)}%")
            
            # Verify real data (not fake 156 users)
            total_users = kpis.get('total_users', 0)
            if total_users != 156:  # Should not be the fake data
                print(f"   ✅ Real user count displayed (not fake 156)")
                results["tests_passed"] += 1
                results["test_details"].append("✅ Dashboard shows real user count")
            else:
                print(f"   ❌ Still showing fake user count (156)")
                results["tests_failed"] += 1
                results["critical_issues"].append("Dashboard showing fake user count")
            
            # Verify revenue calculation from real data
            revenue = kpis.get('revenue', 0)
            if isinstance(revenue, (int, float)) and revenue >= 0:
                print(f"   ✅ Revenue calculation working (€{revenue})")
                results["tests_passed"] += 1
                results["test_details"].append("✅ Revenue calculation from real data")
            else:
                print(f"   ❌ Revenue calculation issues")
                results["tests_failed"] += 1
                results["critical_issues"].append("Revenue calculation problems")
            
            # Verify recent activity is real
            recent_activity = dashboard_data.get("recent_activity", [])
            if recent_activity and len(recent_activity) > 0:
                print(f"   ✅ Recent activity displayed ({len(recent_activity)} items)")
                results["tests_passed"] += 1
                results["test_details"].append("✅ Real recent activity displayed")
            else:
                print(f"   ⚠️ No recent activity found")
                
        else:
            print(f"   ❌ Dashboard endpoint failed: {dashboard_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("Dashboard endpoint not accessible")
        
        # Test 3: User Management by Admin - Create User
        print("\n3. 👤 ADMIN USER CREATION TEST")
        unique_timestamp = int(time.time())
        new_user_data = {
            "username": f"admin_created_user_{unique_timestamp}",
            "email": f"admin_user_{unique_timestamp}@test.com",
            "password": "testpassword123",
            "full_name": "Admin Created User",
            "role": "user"
        }
        
        create_user_response = requests.post(f"{BACKEND_URL}/admin/users", json=new_user_data)
        
        if create_user_response.status_code == 200:
            created_user_data = create_user_response.json()
            created_user_id = created_user_data["user"]["id"]
            print(f"   ✅ Admin user creation successful - ID: {created_user_id}")
            print(f"   📋 Created user: {created_user_data['user']['username']}")
            results["tests_passed"] += 1
            results["test_details"].append("✅ Admin can create new users")
        else:
            print(f"   ❌ Admin user creation failed: {create_user_response.status_code}")
            try:
                error_detail = create_user_response.json()
                print(f"   📋 Error: {error_detail}")
            except:
                pass
            results["tests_failed"] += 1
            results["critical_issues"].append("Admin user creation failed")
            created_user_id = None
        
        # Test 4: Admin Create Another Admin
        print("\n4. 👑 ADMIN CREATE ADMIN USER TEST")
        admin_user_data = {
            "username": f"admin_created_admin_{unique_timestamp}",
            "email": f"admin_admin_{unique_timestamp}@test.com",
            "password": "adminpassword123",
            "full_name": "Admin Created Admin",
            "role": "admin"
        }
        
        create_admin_response = requests.post(f"{BACKEND_URL}/admin/users", json=admin_user_data)
        
        if create_admin_response.status_code == 200:
            created_admin_data = create_admin_response.json()
            created_admin_id = created_admin_data["user"]["id"]
            print(f"   ✅ Admin can create other admins - ID: {created_admin_id}")
            print(f"   👑 Created admin: {created_admin_data['user']['username']}")
            results["tests_passed"] += 1
            results["test_details"].append("✅ Admin can create other admins")
        else:
            print(f"   ❌ Admin admin creation failed: {create_admin_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("Admin cannot create other admins")
            created_admin_id = None
        
        # Test 5: User Deletion by Admin
        if created_user_id:
            print("\n5. 🗑️ ADMIN USER DELETION TEST")
            delete_response = requests.delete(f"{BACKEND_URL}/admin/users/{created_user_id}")
            
            if delete_response.status_code == 200:
                print(f"   ✅ Admin user deletion successful")
                results["tests_passed"] += 1
                results["test_details"].append("✅ Admin can delete users")
                
                # Verify user is actually deleted
                verify_response = requests.get(f"{BACKEND_URL}/auth/profile/{created_user_id}")
                if verify_response.status_code == 404:
                    print(f"   ✅ User properly deleted from database")
                    results["tests_passed"] += 1
                    results["test_details"].append("✅ User deletion verified")
                else:
                    print(f"   ⚠️ User may not be fully deleted")
                    
            else:
                print(f"   ❌ Admin user deletion failed: {delete_response.status_code}")
                results["tests_failed"] += 1
                results["critical_issues"].append("Admin user deletion failed")
        
        # Test 6: Profile Address Persistence
        print("\n6. 🏠 PROFILE ADDRESS PERSISTENCE TEST")
        
        # Create test user for profile testing
        profile_test_user_data = {
            "username": f"profile_test_{unique_timestamp}",
            "email": f"profile_test_{unique_timestamp}@test.com",
            "full_name": "Profile Test User"
        }
        
        profile_user_response = requests.post(f"{BACKEND_URL}/auth/register", json=profile_test_user_data)
        
        if profile_user_response.status_code == 200:
            profile_user_id = profile_user_response.json()["user_id"]
            print(f"   ✅ Profile test user created - ID: {profile_user_id}")
            
            # Test profile update with address
            profile_update_data = {
                "profile": {
                    "full_name": "Updated Profile Test User",
                    "bio": "Testing profile address persistence",
                    "location": "Test City, Test Country",
                    "phone": "+1234567890",
                    "company": "Test Company",
                    "website": "https://test.com",
                    "address": "123 Test Street, Test City, Test State, 12345"
                },
                "settings": {
                    "notifications": True,
                    "email_updates": False,
                    "public_profile": True
                }
            }
            
            update_response = requests.put(f"{BACKEND_URL}/auth/profile/{profile_user_id}", json=profile_update_data)
            
            if update_response.status_code == 200:
                print(f"   ✅ Profile update successful")
                
                # Verify address persistence
                get_profile_response = requests.get(f"{BACKEND_URL}/auth/profile/{profile_user_id}")
                
                if get_profile_response.status_code == 200:
                    profile_data = get_profile_response.json()
                    stored_address = profile_data.get("profile", {}).get("address", "")
                    
                    if stored_address == "123 Test Street, Test City, Test State, 12345":
                        print(f"   ✅ Address field persisted correctly")
                        print(f"   📍 Stored address: {stored_address}")
                        results["tests_passed"] += 1
                        results["test_details"].append("✅ Profile address persistence working")
                    else:
                        print(f"   ❌ Address field not persisted correctly")
                        print(f"   📍 Expected: 123 Test Street, Test City, Test State, 12345")
                        print(f"   📍 Got: {stored_address}")
                        results["tests_failed"] += 1
                        results["critical_issues"].append("Profile address not persisting")
                    
                    # Verify other profile fields
                    stored_bio = profile_data.get("profile", {}).get("bio", "")
                    stored_company = profile_data.get("profile", {}).get("company", "")
                    
                    if stored_bio == "Testing profile address persistence" and stored_company == "Test Company":
                        print(f"   ✅ All profile fields persisted correctly")
                        results["tests_passed"] += 1
                        results["test_details"].append("✅ All profile fields persistent")
                    else:
                        print(f"   ⚠️ Some profile fields may not be persisting")
                        
                else:
                    print(f"   ❌ Failed to retrieve updated profile")
                    results["tests_failed"] += 1
                    results["critical_issues"].append("Cannot retrieve updated profile")
                    
            else:
                print(f"   ❌ Profile update failed: {update_response.status_code}")
                try:
                    error_detail = update_response.json()
                    print(f"   📋 Error: {error_detail}")
                except:
                    pass
                results["tests_failed"] += 1
                results["critical_issues"].append("Profile update failed")
        else:
            print(f"   ❌ Profile test user creation failed")
            results["tests_failed"] += 1
            results["critical_issues"].append("Profile test user creation failed")
        
        # Test 7: Hero Display Options in Settings
        print("\n7. 🎨 HERO DISPLAY OPTIONS TEST")
        settings_response = requests.get(f"{BACKEND_URL}/admin/settings")
        
        if settings_response.status_code == 200:
            settings_data = settings_response.json()
            
            print(f"   ✅ Admin settings endpoint accessible")
            
            # Check for hero display options
            hero_display_mode = settings_data.get("hero_display_mode")
            hero_background_style = settings_data.get("hero_background_style")
            hero_text_alignment = settings_data.get("hero_text_alignment")
            
            print(f"   🎨 Hero Display Options:")
            print(f"      - Display Mode: {hero_display_mode}")
            print(f"      - Background Style: {hero_background_style}")
            print(f"      - Text Alignment: {hero_text_alignment}")
            
            # Verify all three options are present
            expected_options = ["hero_display_mode", "hero_background_style", "hero_text_alignment"]
            missing_options = []
            
            for option in expected_options:
                if option not in settings_data:
                    missing_options.append(option)
            
            if not missing_options:
                print(f"   ✅ All hero display options present")
                results["tests_passed"] += 1
                results["test_details"].append("✅ Hero display options available")
                
                # Verify valid values
                valid_display_modes = ["full_width", "boxed", "centered"]
                valid_background_styles = ["gradient", "image", "solid"]
                valid_text_alignments = ["left", "center", "right"]
                
                if (hero_display_mode in valid_display_modes and
                    hero_background_style in valid_background_styles and
                    hero_text_alignment in valid_text_alignments):
                    print(f"   ✅ Hero display option values are valid")
                    results["tests_passed"] += 1
                    results["test_details"].append("✅ Hero display option values valid")
                else:
                    print(f"   ⚠️ Some hero display option values may be invalid")
                    
            else:
                print(f"   ❌ Missing hero display options: {missing_options}")
                results["tests_failed"] += 1
                results["critical_issues"].append(f"Missing hero display options: {missing_options}")
            
            # Test updating hero display settings
            print("\n8. 🔄 HERO DISPLAY SETTINGS UPDATE TEST")
            updated_settings = {
                "hero_display_mode": "boxed",
                "hero_background_style": "image",
                "hero_text_alignment": "left",
                "site_name": "Cataloro",
                "theme_color": "#3B82F6"
            }
            
            update_settings_response = requests.put(f"{BACKEND_URL}/admin/settings", json=updated_settings)
            
            if update_settings_response.status_code == 200:
                print(f"   ✅ Hero display settings update successful")
                
                # Verify the update
                verify_settings_response = requests.get(f"{BACKEND_URL}/admin/settings")
                if verify_settings_response.status_code == 200:
                    verify_data = verify_settings_response.json()
                    
                    if (verify_data.get("hero_display_mode") == "boxed" and
                        verify_data.get("hero_background_style") == "image" and
                        verify_data.get("hero_text_alignment") == "left"):
                        print(f"   ✅ Hero display settings persisted correctly")
                        results["tests_passed"] += 1
                        results["test_details"].append("✅ Hero display settings persistence working")
                    else:
                        print(f"   ❌ Hero display settings not persisted correctly")
                        results["tests_failed"] += 1
                        results["critical_issues"].append("Hero display settings not persisting")
                        
            else:
                print(f"   ❌ Hero display settings update failed: {update_settings_response.status_code}")
                results["tests_failed"] += 1
                results["critical_issues"].append("Hero display settings update failed")
                
        else:
            print(f"   ❌ Admin settings endpoint failed: {settings_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("Admin settings endpoint not accessible")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        results["tests_failed"] += 1
        results["critical_issues"].append(f"Critical testing error: {str(e)}")
    
    return results

def main():
    """Main testing function"""
    print("🚀 STARTING ADMIN PANEL & PROFILE FIXES TESTING")
    print("Testing critical admin panel and profile fixes as requested in review")
    print("=" * 80)
    
    start_time = time.time()
    results = test_admin_panel_and_profile_fixes()
    end_time = time.time()
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Tests Passed: {results['tests_passed']}")
    print(f"   ❌ Tests Failed: {results['tests_failed']}")
    print(f"   ⏱️ Total Time: {end_time - start_time:.2f} seconds")
    
    success_rate = (results['tests_passed'] / (results['tests_passed'] + results['tests_failed']) * 100) if (results['tests_passed'] + results['tests_failed']) > 0 else 0
    print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    print(f"\n✅ SUCCESSFUL TESTS:")
    for detail in results['test_details']:
        print(f"   {detail}")
    
    if results['critical_issues']:
        print(f"\n❌ CRITICAL ISSUES FOUND:")
        for issue in results['critical_issues']:
            print(f"   ❌ {issue}")
    
    # Overall status
    if results['tests_failed'] == 0:
        print(f"\n🎉 ADMIN PANEL & PROFILE FIXES STATUS: ✅ FULLY OPERATIONAL")
        print("   All tests passed - admin panel and profile fixes working correctly")
    elif results['tests_failed'] <= 2:
        print(f"\n⚠️ ADMIN PANEL & PROFILE FIXES STATUS: ⚠️ MOSTLY WORKING")
        print("   Minor issues detected but core functionality operational")
    else:
        print(f"\n❌ ADMIN PANEL & PROFILE FIXES STATUS: ❌ CRITICAL ISSUES")
        print("   Major problems detected - requires immediate attention")
    
    return results

if __name__ == "__main__":
    main()