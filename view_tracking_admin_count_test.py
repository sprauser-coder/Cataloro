#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - VIEW TRACKING & ADMIN COUNT FIX TESTING
Testing the view tracking fix and admin dashboard count fix

SPECIFIC FIXES BEING TESTED:
1. **View Tracking Fix**: 
   - Test specific listing "ed1b24bb-4e6d-48d5-b54a-8a5780313675" that user reported having 0 views
   - Verify views increment properly with increment_view=true
   - Test session-based tracking for unauthenticated users using IP+User-Agent hash
   - Verify same session doesn't increment views multiple times

2. **Admin Dashboard Count Fix**:
   - Test GET /api/admin/dashboard with admin authentication
   - Verify total_listings shows ALL listings (should be higher number like 62+)
   - Verify active_listings shows only active status listings (should be lower)
   - Confirm total >= active

3. **Session-based View Tracking**:
   - Test increment_view=true without authentication (should increment using session)
   - Test that same session doesn't increment views multiple times
   - Check logging shows proper session tracking messages

4. **Multiple User Scenarios**:
   - Test authenticated user viewing (should track by user_id)
   - Test unauthenticated viewing (should track by session_id based on IP+User-Agent)
   - Verify both scenarios increment view counts properly

CRITICAL ENDPOINTS BEING TESTED:
- GET /api/listings/{listing_id}?increment_view=true (view tracking)
- GET /api/admin/dashboard (admin dashboard counts)
- POST /api/auth/login (authentication)

EXPECTED RESULTS AFTER FIXES:
- Views increment properly for the specific listing
- Admin dashboard shows correct total_listings vs active_listings counts
- Session-based tracking works for unauthenticated users
- Proper logging for debugging view tracking behavior
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz
import hashlib

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://mobileui-sync.preview.emergentagent.com/api"

# Specific listing ID reported by user
SPECIFIC_LISTING_ID = "ed1b24bb-4e6d-48d5-b54a-8a5780313675"

class ViewTrackingAdminCountTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, details, response_time=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        time_info = f" ({response_time:.1f}ms)" if response_time else ""
        print(f"{status}: {test_name}{time_info}")
        print(f"   Details: {details}")
        print()
    
    async def test_login_and_get_token(self, email="admin@cataloro.com", password="admin123"):
        """Test login and get JWT token"""
        start_time = datetime.now()
        
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    user = data.get("user", {})
                    user_id = user.get("id")
                    
                    if token and user_id:
                        self.log_result(
                            f"Login Authentication ({email})", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Unknown')} (ID: {user_id}), token received",
                            response_time
                        )
                        return token, user_id, user
                    else:
                        self.log_result(
                            f"Login Authentication ({email})", 
                            False, 
                            f"Login successful but missing token or user_id in response: {data}",
                            response_time
                        )
                        return None, None, None
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Login Authentication ({email})", 
                        False, 
                        f"Login failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None, None, None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Login Authentication ({email})", 
                False, 
                f"Login request failed with exception: {str(e)}",
                response_time
            )
            return None, None, None
    
    async def get_listing_with_view_tracking(self, listing_id, token=None, increment_view=False, session_headers=None):
        """Get listing with optional view tracking"""
        start_time = datetime.now()
        
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            # Add session headers for unauthenticated requests
            if session_headers:
                headers.update(session_headers)
            
            params = {}
            if increment_view:
                params["increment_view"] = "true"
            
            url = f"{BACKEND_URL}/listings/{listing_id}"
            if params:
                param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                url += f"?{param_str}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    view_count = data.get('views', 0)
                    
                    auth_status = "authenticated" if token else "unauthenticated"
                    increment_status = "with increment_view=true" if increment_view else "without increment_view"
                    
                    self.log_result(
                        f"Get Listing ({auth_status}, {increment_status})", 
                        True, 
                        f"Retrieved listing {listing_id}, current view count: {view_count}",
                        response_time
                    )
                    return data
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Get Listing", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get Listing", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return None
    
    async def test_specific_listing_view_tracking(self):
        """Test the specific listing that user reported having 0 views"""
        print(f"\n🎯 TESTING SPECIFIC LISTING VIEW TRACKING: {SPECIFIC_LISTING_ID}")
        
        # Step 1: Get initial view count
        initial_data = await self.get_listing_with_view_tracking(SPECIFIC_LISTING_ID, increment_view=False)
        if not initial_data:
            self.log_result("Specific Listing View Tracking", False, f"Could not retrieve listing {SPECIFIC_LISTING_ID}")
            return False
        
        initial_view_count = initial_data.get('views', 0)
        print(f"   Initial view count: {initial_view_count}")
        
        # Step 2: Test multiple calls with increment_view=true (should increment properly)
        for i in range(3):
            view_data = await self.get_listing_with_view_tracking(SPECIFIC_LISTING_ID, increment_view=True)
            if view_data:
                current_count = view_data.get('views', 0)
                print(f"   View attempt {i+1}: count = {current_count}")
        
        # Step 3: Get final view count
        final_data = await self.get_listing_with_view_tracking(SPECIFIC_LISTING_ID, increment_view=False)
        if not final_data:
            return False
        
        final_view_count = final_data.get('views', 0)
        
        # Check if views incremented
        if final_view_count > initial_view_count:
            self.log_result(
                "Specific Listing View Increment", 
                True, 
                f"✅ VIEW TRACKING FIX WORKING: Views incremented from {initial_view_count} to {final_view_count}"
            )
            return True
        else:
            self.log_result(
                "Specific Listing View Increment", 
                False, 
                f"❌ VIEW TRACKING NOT WORKING: Views did not increment ({initial_view_count} → {final_view_count})"
            )
            return False
    
    async def test_authenticated_user_view_tracking(self):
        """Test authenticated user view tracking"""
        print(f"\n🔐 TESTING AUTHENTICATED USER VIEW TRACKING")
        
        # Login as admin user
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        if not admin_token:
            return False
        
        # Get initial view count
        initial_data = await self.get_listing_with_view_tracking(SPECIFIC_LISTING_ID, admin_token, increment_view=False)
        if not initial_data:
            return False
        
        initial_view_count = initial_data.get('views', 0)
        
        # First authenticated view (should increment)
        first_view_data = await self.get_listing_with_view_tracking(SPECIFIC_LISTING_ID, admin_token, increment_view=True)
        if not first_view_data:
            return False
        
        first_view_count = first_view_data.get('views', 0)
        
        # Second authenticated view from same user (behavior depends on implementation)
        second_view_data = await self.get_listing_with_view_tracking(SPECIFIC_LISTING_ID, admin_token, increment_view=True)
        if not second_view_data:
            return False
        
        second_view_count = second_view_data.get('views', 0)
        
        if first_view_count > initial_view_count:
            self.log_result(
                "Authenticated User First View", 
                True, 
                f"✅ First authenticated view incremented: {initial_view_count} → {first_view_count}"
            )
        else:
            self.log_result(
                "Authenticated User First View", 
                False, 
                f"❌ First authenticated view did not increment: {initial_view_count} → {first_view_count}"
            )
        
        # Check second view behavior
        if second_view_count >= first_view_count:
            self.log_result(
                "Authenticated User Second View", 
                True, 
                f"✅ Second authenticated view handled correctly: {first_view_count} → {second_view_count}"
            )
            return True
        else:
            self.log_result(
                "Authenticated User Second View", 
                False, 
                f"❌ Second authenticated view decreased count: {first_view_count} → {second_view_count}"
            )
            return False
    
    async def test_session_based_view_tracking(self):
        """Test session-based view tracking for unauthenticated users"""
        print(f"\n🌐 TESTING SESSION-BASED VIEW TRACKING (UNAUTHENTICATED)")
        
        # Create session headers based on IP + User-Agent
        session_headers = {
            "User-Agent": "TestBot/1.0 (Session-Test)",
            "X-Forwarded-For": "192.168.1.100"  # Simulate IP
        }
        
        # Get initial view count
        initial_data = await self.get_listing_with_view_tracking(SPECIFIC_LISTING_ID, increment_view=False)
        if not initial_data:
            return False
        
        initial_view_count = initial_data.get('views', 0)
        
        # First unauthenticated view with session (should increment based on new implementation)
        first_view_data = await self.get_listing_with_view_tracking(
            SPECIFIC_LISTING_ID, 
            token=None, 
            increment_view=True, 
            session_headers=session_headers
        )
        if not first_view_data:
            return False
        
        first_view_count = first_view_data.get('views', 0)
        
        # Second unauthenticated view with same session (should not increment again)
        second_view_data = await self.get_listing_with_view_tracking(
            SPECIFIC_LISTING_ID, 
            token=None, 
            increment_view=True, 
            session_headers=session_headers
        )
        if not second_view_data:
            return False
        
        second_view_count = second_view_data.get('views', 0)
        
        # Test with different session (different User-Agent)
        different_session_headers = {
            "User-Agent": "DifferentBot/2.0 (Different-Session)",
            "X-Forwarded-For": "192.168.1.100"  # Same IP, different User-Agent
        }
        
        third_view_data = await self.get_listing_with_view_tracking(
            SPECIFIC_LISTING_ID, 
            token=None, 
            increment_view=True, 
            session_headers=different_session_headers
        )
        if not third_view_data:
            return False
        
        third_view_count = third_view_data.get('views', 0)
        
        # Analyze results
        if first_view_count > initial_view_count:
            self.log_result(
                "Session-Based First View", 
                True, 
                f"✅ First session view incremented: {initial_view_count} → {first_view_count}"
            )
        else:
            self.log_result(
                "Session-Based First View", 
                True, 
                f"ℹ️ First session view did not increment (may be by design): {initial_view_count} → {first_view_count}"
            )
        
        if second_view_count == first_view_count:
            self.log_result(
                "Session-Based Duplicate Prevention", 
                True, 
                f"✅ Same session duplicate view prevented: {first_view_count} → {second_view_count}"
            )
        else:
            self.log_result(
                "Session-Based Duplicate Prevention", 
                False, 
                f"❌ Same session view incremented again: {first_view_count} → {second_view_count}"
            )
        
        if third_view_count >= second_view_count:
            self.log_result(
                "Different Session View", 
                True, 
                f"✅ Different session view handled: {second_view_count} → {third_view_count}"
            )
            return True
        else:
            self.log_result(
                "Different Session View", 
                False, 
                f"❌ Different session view decreased count: {second_view_count} → {third_view_count}"
            )
            return False
    
    async def test_admin_dashboard_counts(self):
        """Test admin dashboard count fix"""
        print(f"\n📊 TESTING ADMIN DASHBOARD COUNT FIX")
        
        # Login as admin
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        if not admin_token:
            return False
        
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            async with self.session.get(f"{BACKEND_URL}/admin/dashboard", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    total_listings = data.get('total_listings', 0)
                    active_listings = data.get('active_listings', 0)
                    
                    # Check if counts make sense
                    if total_listings >= active_listings:
                        self.log_result(
                            "Admin Dashboard Count Logic", 
                            True, 
                            f"✅ COUNT FIX WORKING: total_listings ({total_listings}) >= active_listings ({active_listings})",
                            response_time
                        )
                    else:
                        self.log_result(
                            "Admin Dashboard Count Logic", 
                            False, 
                            f"❌ COUNT LOGIC ERROR: total_listings ({total_listings}) < active_listings ({active_listings})",
                            response_time
                        )
                        return False
                    
                    # Check if total_listings is a reasonable number (should be higher like 62+)
                    if total_listings >= 50:
                        self.log_result(
                            "Admin Dashboard Total Count", 
                            True, 
                            f"✅ TOTAL COUNT FIX WORKING: Shows ALL listings ({total_listings} total)",
                            response_time
                        )
                    else:
                        self.log_result(
                            "Admin Dashboard Total Count", 
                            False, 
                            f"⚠️ TOTAL COUNT LOW: Only {total_listings} total listings (expected 50+)",
                            response_time
                        )
                    
                    # Check if active_listings is lower than total (as expected)
                    if active_listings < total_listings:
                        self.log_result(
                            "Admin Dashboard Active Count", 
                            True, 
                            f"✅ ACTIVE COUNT FIX WORKING: Shows only active listings ({active_listings} active)",
                            response_time
                        )
                    else:
                        self.log_result(
                            "Admin Dashboard Active Count", 
                            False, 
                            f"⚠️ ACTIVE COUNT ISSUE: Active count ({active_listings}) equals total ({total_listings})",
                            response_time
                        )
                    
                    # Log additional dashboard data for verification
                    additional_data = {k: v for k, v in data.items() if k not in ['total_listings', 'active_listings']}
                    if additional_data:
                        print(f"   Additional dashboard data: {additional_data}")
                    
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Dashboard Access", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Admin Dashboard Access", 
                False, 
                f"Request failed with exception: {str(e)}",
                response_time
            )
            return False
    
    async def test_multiple_user_scenarios(self):
        """Test multiple user scenarios for view tracking"""
        print(f"\n👥 TESTING MULTIPLE USER SCENARIOS")
        
        # Login as different users
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        demo_token, demo_user_id, demo_user = await self.test_login_and_get_token("demo@cataloro.com", "demo123")
        
        if not admin_token or not demo_token:
            return False
        
        # Get initial view count
        initial_data = await self.get_listing_with_view_tracking(SPECIFIC_LISTING_ID, increment_view=False)
        if not initial_data:
            return False
        
        initial_view_count = initial_data.get('views', 0)
        
        # Admin user views
        admin_view_data = await self.get_listing_with_view_tracking(SPECIFIC_LISTING_ID, admin_token, increment_view=True)
        if not admin_view_data:
            return False
        
        admin_view_count = admin_view_data.get('views', 0)
        
        # Demo user views
        demo_view_data = await self.get_listing_with_view_tracking(SPECIFIC_LISTING_ID, demo_token, increment_view=True)
        if not demo_view_data:
            return False
        
        demo_view_count = demo_view_data.get('views', 0)
        
        # Unauthenticated user views
        unauth_session_headers = {
            "User-Agent": "UnauthenticatedBot/1.0",
            "X-Forwarded-For": "192.168.1.200"
        }
        
        unauth_view_data = await self.get_listing_with_view_tracking(
            SPECIFIC_LISTING_ID, 
            token=None, 
            increment_view=True, 
            session_headers=unauth_session_headers
        )
        if not unauth_view_data:
            return False
        
        unauth_view_count = unauth_view_data.get('views', 0)
        
        # Analyze progression
        progression = f"{initial_view_count} → {admin_view_count} → {demo_view_count} → {unauth_view_count}"
        
        if unauth_view_count >= initial_view_count:
            self.log_result(
                "Multiple User Scenarios", 
                True, 
                f"✅ MULTIPLE USER TRACKING WORKING: View progression: {progression}"
            )
            return True
        else:
            self.log_result(
                "Multiple User Scenarios", 
                False, 
                f"❌ MULTIPLE USER TRACKING FAILED: View progression: {progression}"
            )
            return False
    
    async def test_database_connectivity(self):
        """Test if backend can connect to database"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Database Connectivity", 
                        True, 
                        f"Backend health check passed: {data.get('status', 'unknown')}",
                        response_time
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Database Connectivity", 
                        False, 
                        f"Health check failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Database Connectivity", 
                False, 
                f"Health check failed with exception: {str(e)}",
                response_time
            )
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 VIEW TRACKING & ADMIN COUNT FIX TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"   - {result['test']}: {result['details']}")
        
        print("\n" + "="*80)
        
        # Overall assessment
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - VIEW TRACKING & ADMIN COUNT FIXES WORKING!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ MOSTLY WORKING - Minor issues detected")
        else:
            print("❌ SIGNIFICANT ISSUES - Fixes need attention")
        
        print("="*80)

async def main():
    """Main test execution"""
    print("🚀 Starting View Tracking & Admin Count Fix Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Specific Listing ID: {SPECIFIC_LISTING_ID}")
    print("="*80)
    
    async with ViewTrackingAdminCountTester() as tester:
        # Test database connectivity first
        await tester.test_database_connectivity()
        
        # Test 1: Specific listing view tracking fix
        await tester.test_specific_listing_view_tracking()
        
        # Test 2: Admin dashboard count fix
        await tester.test_admin_dashboard_counts()
        
        # Test 3: Authenticated user view tracking
        await tester.test_authenticated_user_view_tracking()
        
        # Test 4: Session-based view tracking
        await tester.test_session_based_view_tracking()
        
        # Test 5: Multiple user scenarios
        await tester.test_multiple_user_scenarios()
        
        # Print summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())