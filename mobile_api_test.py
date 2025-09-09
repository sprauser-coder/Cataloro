#!/usr/bin/env python3
"""
Mobile Functionality API Testing
Testing Messages API, Ads Management API, and Browse Listings API for mobile functionality
"""

import asyncio
import aiohttp
import time
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://mobi-market.preview.emergentagent.com/api"

# Demo User Configuration
DEMO_USER_EMAIL = "demo@cataloro.com"
DEMO_USER_ID = None  # Will be set after login

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_TOKEN = None  # Will be set after login

class MobileAPITester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.demo_user_id = None
        self.admin_token = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
            if headers:
                request_kwargs['headers'] = headers
            
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **request_kwargs) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "response_time_ms": response_time_ms,
                    "data": response_data,
                    "status": response.status
                }
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time_ms,
                "error": str(e),
                "status": 0
            }
    
    async def authenticate_demo_user(self) -> Dict:
        """Authenticate demo user and get user ID"""
        print("🔐 Authenticating demo user...")
        
        login_data = {
            "email": DEMO_USER_EMAIL,
            "password": "demo_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            self.demo_user_id = user_data.get("id")
            
            print(f"  ✅ Demo user authenticated successfully")
            print(f"  👤 User ID: {self.demo_user_id}")
            print(f"  📧 Email: {user_data.get('email')}")
            
            return {
                "test_name": "Demo User Authentication",
                "success": True,
                "user_id": self.demo_user_id,
                "user_data": user_data,
                "response_time_ms": result["response_time_ms"]
            }
        else:
            print(f"  ❌ Demo user authentication failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Demo User Authentication",
                "success": False,
                "error": result.get("error", "Authentication failed"),
                "response_time_ms": result["response_time_ms"]
            }
    
    async def authenticate_admin_user(self) -> Dict:
        """Authenticate admin user and get token"""
        print("🔐 Authenticating admin user...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            self.admin_token = result["data"].get("token", "")
            
            print(f"  ✅ Admin user authenticated successfully")
            print(f"  👤 User ID: {user_data.get('id')}")
            print(f"  🔑 Token received: {bool(self.admin_token)}")
            
            return {
                "test_name": "Admin User Authentication",
                "success": True,
                "user_data": user_data,
                "token_received": bool(self.admin_token),
                "response_time_ms": result["response_time_ms"]
            }
        else:
            print(f"  ❌ Admin user authentication failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Admin User Authentication",
                "success": False,
                "error": result.get("error", "Authentication failed"),
                "response_time_ms": result["response_time_ms"]
            }
    
    async def test_messages_api(self) -> Dict:
        """Test Messages API for mobile functionality"""
        print("💬 Testing Messages API for mobile functionality...")
        
        if not self.demo_user_id:
            return {
                "test_name": "Messages API Testing",
                "error": "Demo user not authenticated - cannot test messages API"
            }
        
        message_tests = []
        
        # Test 1: GET /api/user/{user_id}/messages endpoint for demo user
        print("  Testing GET messages endpoint...")
        get_messages_result = await self.make_request(f"/user/{self.demo_user_id}/messages")
        
        if get_messages_result["success"]:
            messages_data = get_messages_result["data"]
            message_count = len(messages_data) if isinstance(messages_data, list) else 0
            
            message_tests.append({
                "test": "GET Messages",
                "success": True,
                "response_time_ms": get_messages_result["response_time_ms"],
                "message_count": message_count,
                "data_structure_valid": isinstance(messages_data, list),
                "endpoint": f"/user/{self.demo_user_id}/messages"
            })
            
            print(f"    ✅ GET messages successful: {message_count} messages found")
        else:
            message_tests.append({
                "test": "GET Messages",
                "success": False,
                "error": get_messages_result.get("error", "GET messages failed"),
                "status": get_messages_result["status"],
                "response_time_ms": get_messages_result["response_time_ms"],
                "endpoint": f"/user/{self.demo_user_id}/messages"
            })
            print(f"    ❌ GET messages failed: {get_messages_result.get('error', 'Unknown error')}")
        
        # Test 2: POST /api/user/{user_id}/messages endpoint to send messages
        print("  Testing POST messages endpoint...")
        test_message_data = {
            "recipient_id": "test-recipient-123",
            "subject": "Mobile Test Message",
            "content": "This is a test message sent from mobile API testing",
            "message_type": "general",
            "priority": "normal"
        }
        
        post_messages_result = await self.make_request(
            f"/user/{self.demo_user_id}/messages", 
            "POST", 
            data=test_message_data
        )
        
        if post_messages_result["success"]:
            response_data = post_messages_result["data"]
            message_id = response_data.get("message_id") or response_data.get("id")
            
            message_tests.append({
                "test": "POST Messages",
                "success": True,
                "response_time_ms": post_messages_result["response_time_ms"],
                "message_sent": True,
                "message_id": message_id,
                "response_data": response_data,
                "endpoint": f"/user/{self.demo_user_id}/messages"
            })
            
            print(f"    ✅ POST message successful: Message ID {message_id}")
        else:
            message_tests.append({
                "test": "POST Messages",
                "success": False,
                "error": post_messages_result.get("error", "POST message failed"),
                "status": post_messages_result["status"],
                "response_time_ms": post_messages_result["response_time_ms"],
                "endpoint": f"/user/{self.demo_user_id}/messages"
            })
            print(f"    ❌ POST message failed: {post_messages_result.get('error', 'Unknown error')}")
        
        # Test 3: Verify message data structure and error handling
        print("  Testing message data structure and error handling...")
        
        # Test with invalid user ID
        invalid_user_result = await self.make_request("/user/invalid-user-id/messages")
        
        # Test with malformed POST data
        malformed_data = {"invalid": "data"}
        malformed_post_result = await self.make_request(
            f"/user/{self.demo_user_id}/messages", 
            "POST", 
            data=malformed_data
        )
        
        error_handling_working = (
            not invalid_user_result["success"] and 
            invalid_user_result["status"] in [400, 404, 403]
        )
        
        message_tests.append({
            "test": "Error Handling",
            "success": error_handling_working,
            "invalid_user_handled": not invalid_user_result["success"],
            "invalid_user_status": invalid_user_result["status"],
            "malformed_data_handled": not malformed_post_result["success"],
            "malformed_data_status": malformed_post_result["status"],
            "proper_error_responses": error_handling_working
        })
        
        if error_handling_working:
            print("    ✅ Error handling working correctly")
        else:
            print("    ⚠️ Error handling may need improvement")
        
        # Calculate overall success
        successful_tests = [t for t in message_tests if t.get("success", False)]
        
        return {
            "test_name": "Messages API Testing",
            "total_tests": len(message_tests),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(message_tests) * 100 if message_tests else 0,
            "get_messages_working": any(t.get("test") == "GET Messages" and t.get("success") for t in message_tests),
            "post_messages_working": any(t.get("test") == "POST Messages" and t.get("success") for t in message_tests),
            "error_handling_working": any(t.get("test") == "Error Handling" and t.get("success") for t in message_tests),
            "messages_api_functional": len(successful_tests) >= 2,  # At least GET and POST working
            "detailed_test_results": message_tests
        }
    
    async def test_ads_management_api(self) -> Dict:
        """Test Ads Management API for mobile functionality"""
        print("📢 Testing Ads Management API for mobile functionality...")
        
        if not self.admin_token:
            return {
                "test_name": "Ads Management API Testing",
                "error": "Admin user not authenticated - cannot test ads management API"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        ads_tests = []
        created_ad_id = None
        
        # Test 1: GET /api/admin/ads (should return empty array initially)
        print("  Testing GET admin ads endpoint...")
        get_ads_result = await self.make_request("/admin/ads", headers=headers)
        
        if get_ads_result["success"]:
            ads_data = get_ads_result["data"]
            is_array = isinstance(ads_data, list)
            initial_count = len(ads_data) if is_array else 0
            
            ads_tests.append({
                "test": "GET Admin Ads",
                "success": True,
                "response_time_ms": get_ads_result["response_time_ms"],
                "is_array": is_array,
                "initial_ad_count": initial_count,
                "data_structure_valid": is_array,
                "endpoint": "/admin/ads"
            })
            
            print(f"    ✅ GET admin ads successful: {initial_count} ads found (array: {is_array})")
        else:
            ads_tests.append({
                "test": "GET Admin Ads",
                "success": False,
                "error": get_ads_result.get("error", "GET admin ads failed"),
                "status": get_ads_result["status"],
                "response_time_ms": get_ads_result["response_time_ms"],
                "endpoint": "/admin/ads"
            })
            print(f"    ❌ GET admin ads failed: {get_ads_result.get('error', 'Unknown error')}")
        
        # Test 2: POST /api/admin/ads to create a new ad
        print("  Testing POST admin ads endpoint...")
        test_ad_data = {
            "title": "Mobile Test Advertisement",
            "description": "This is a test advertisement created for mobile API testing",
            "content": "Test ad content for mobile functionality verification",
            "ad_type": "banner",
            "target_audience": "mobile_users",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now().replace(month=12, day=31)).isoformat(),
            "budget": 500.00,
            "status": "draft"
        }
        
        post_ads_result = await self.make_request("/admin/ads", "POST", data=test_ad_data, headers=headers)
        
        if post_ads_result["success"]:
            response_data = post_ads_result["data"]
            created_ad_id = response_data.get("ad_id") or response_data.get("id")
            is_inactive_by_default = not response_data.get("is_active", True)
            
            ads_tests.append({
                "test": "POST Admin Ads",
                "success": True,
                "response_time_ms": post_ads_result["response_time_ms"],
                "ad_created": True,
                "ad_id": created_ad_id,
                "is_inactive_by_default": is_inactive_by_default,
                "response_data": response_data,
                "endpoint": "/admin/ads"
            })
            
            print(f"    ✅ POST admin ads successful: Ad ID {created_ad_id}, inactive by default: {is_inactive_by_default}")
        else:
            ads_tests.append({
                "test": "POST Admin Ads",
                "success": False,
                "error": post_ads_result.get("error", "POST admin ads failed"),
                "status": post_ads_result["status"],
                "response_time_ms": post_ads_result["response_time_ms"],
                "endpoint": "/admin/ads"
            })
            print(f"    ❌ POST admin ads failed: {post_ads_result.get('error', 'Unknown error')}")
        
        # Test 3: PUT /api/admin/ads/{ad_id}/activate to activate an ad
        if created_ad_id:
            print("  Testing PUT activate ad endpoint...")
            activate_result = await self.make_request(f"/admin/ads/{created_ad_id}/activate", "PUT", headers=headers)
            
            if activate_result["success"]:
                response_data = activate_result["data"]
                is_now_active = response_data.get("is_active", False)
                
                ads_tests.append({
                    "test": "PUT Activate Ad",
                    "success": True,
                    "response_time_ms": activate_result["response_time_ms"],
                    "ad_activated": is_now_active,
                    "ad_id": created_ad_id,
                    "response_data": response_data,
                    "endpoint": f"/admin/ads/{created_ad_id}/activate"
                })
                
                print(f"    ✅ PUT activate ad successful: Ad is now active: {is_now_active}")
            else:
                ads_tests.append({
                    "test": "PUT Activate Ad",
                    "success": False,
                    "error": activate_result.get("error", "PUT activate ad failed"),
                    "status": activate_result["status"],
                    "response_time_ms": activate_result["response_time_ms"],
                    "ad_id": created_ad_id,
                    "endpoint": f"/admin/ads/{created_ad_id}/activate"
                })
                print(f"    ❌ PUT activate ad failed: {activate_result.get('error', 'Unknown error')}")
        else:
            ads_tests.append({
                "test": "PUT Activate Ad",
                "success": False,
                "error": "No ad ID available - ad creation failed",
                "skipped": True
            })
            print("    ⚠️ Skipping activate test - no ad created")
        
        # Test 4: GET /api/ads/active to verify only active ads are returned
        print("  Testing GET active ads endpoint...")
        get_active_ads_result = await self.make_request("/ads/active")
        
        if get_active_ads_result["success"]:
            active_ads_data = get_active_ads_result["data"]
            is_array = isinstance(active_ads_data, list)
            active_count = len(active_ads_data) if is_array else 0
            
            # Check if our created ad is in the active ads (if it was activated)
            our_ad_in_active = False
            if created_ad_id and is_array:
                our_ad_in_active = any(ad.get("id") == created_ad_id for ad in active_ads_data)
            
            ads_tests.append({
                "test": "GET Active Ads",
                "success": True,
                "response_time_ms": get_active_ads_result["response_time_ms"],
                "is_array": is_array,
                "active_ad_count": active_count,
                "our_ad_in_active": our_ad_in_active,
                "data_structure_valid": is_array,
                "endpoint": "/ads/active"
            })
            
            print(f"    ✅ GET active ads successful: {active_count} active ads found, our ad included: {our_ad_in_active}")
        else:
            ads_tests.append({
                "test": "GET Active Ads",
                "success": False,
                "error": get_active_ads_result.get("error", "GET active ads failed"),
                "status": get_active_ads_result["status"],
                "response_time_ms": get_active_ads_result["response_time_ms"],
                "endpoint": "/ads/active"
            })
            print(f"    ❌ GET active ads failed: {get_active_ads_result.get('error', 'Unknown error')}")
        
        # Calculate overall success
        successful_tests = [t for t in ads_tests if t.get("success", False) and not t.get("skipped", False)]
        
        return {
            "test_name": "Ads Management API Testing",
            "total_tests": len([t for t in ads_tests if not t.get("skipped", False)]),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len([t for t in ads_tests if not t.get("skipped", False)]) * 100 if ads_tests else 0,
            "get_admin_ads_working": any(t.get("test") == "GET Admin Ads" and t.get("success") for t in ads_tests),
            "post_admin_ads_working": any(t.get("test") == "POST Admin Ads" and t.get("success") for t in ads_tests),
            "activate_ad_working": any(t.get("test") == "PUT Activate Ad" and t.get("success") for t in ads_tests),
            "get_active_ads_working": any(t.get("test") == "GET Active Ads" and t.get("success") for t in ads_tests),
            "inactive_by_default_verified": any(t.get("is_inactive_by_default") for t in ads_tests),
            "ads_management_functional": len(successful_tests) >= 3,  # At least 3 core functions working
            "created_ad_id": created_ad_id,
            "detailed_test_results": ads_tests
        }
    
    async def test_browse_listings_api(self) -> Dict:
        """Test Browse Listings API for mobile functionality"""
        print("🔍 Testing Browse Listings API for mobile functionality...")
        
        browse_tests = []
        
        # Test 1: GET /api/marketplace/browse to ensure listings are still working
        print("  Testing GET marketplace browse endpoint...")
        browse_result = await self.make_request("/marketplace/browse")
        
        if browse_result["success"]:
            listings_data = browse_result["data"]
            is_array = isinstance(listings_data, list)
            listing_count = len(listings_data) if is_array else 0
            
            # Check data structure for mobile compatibility
            mobile_data_structure_valid = self.validate_mobile_data_structure(listings_data)
            
            browse_tests.append({
                "test": "GET Browse Listings",
                "success": True,
                "response_time_ms": browse_result["response_time_ms"],
                "is_array": is_array,
                "listing_count": listing_count,
                "mobile_data_structure_valid": mobile_data_structure_valid,
                "data_structure_score": mobile_data_structure_valid["score"],
                "endpoint": "/marketplace/browse"
            })
            
            print(f"    ✅ GET browse listings successful: {listing_count} listings found")
            print(f"    📱 Mobile data structure score: {mobile_data_structure_valid['score']:.1f}%")
        else:
            browse_tests.append({
                "test": "GET Browse Listings",
                "success": False,
                "error": browse_result.get("error", "GET browse listings failed"),
                "status": browse_result["status"],
                "response_time_ms": browse_result["response_time_ms"],
                "endpoint": "/marketplace/browse"
            })
            print(f"    ❌ GET browse listings failed: {browse_result.get('error', 'Unknown error')}")
        
        # Test 2: Test with mobile-specific parameters
        print("  Testing browse with mobile-specific parameters...")
        mobile_params = {
            "limit": 10,  # Mobile-friendly page size
            "page": 1,
            "type": "all"
        }
        
        mobile_browse_result = await self.make_request("/marketplace/browse", params=mobile_params)
        
        if mobile_browse_result["success"]:
            mobile_listings = mobile_browse_result["data"]
            mobile_count = len(mobile_listings) if isinstance(mobile_listings, list) else 0
            mobile_structure = self.validate_mobile_data_structure(mobile_listings)
            
            browse_tests.append({
                "test": "Mobile Browse Parameters",
                "success": True,
                "response_time_ms": mobile_browse_result["response_time_ms"],
                "mobile_listing_count": mobile_count,
                "mobile_structure_valid": mobile_structure["score"] >= 80,
                "mobile_structure_score": mobile_structure["score"],
                "respects_limit": mobile_count <= 10,
                "endpoint": "/marketplace/browse with mobile params"
            })
            
            print(f"    ✅ Mobile browse successful: {mobile_count} listings (limit respected: {mobile_count <= 10})")
        else:
            browse_tests.append({
                "test": "Mobile Browse Parameters",
                "success": False,
                "error": mobile_browse_result.get("error", "Mobile browse failed"),
                "status": mobile_browse_result["status"],
                "response_time_ms": mobile_browse_result["response_time_ms"],
                "endpoint": "/marketplace/browse with mobile params"
            })
            print(f"    ❌ Mobile browse failed: {mobile_browse_result.get('error', 'Unknown error')}")
        
        # Test 3: Test performance for mobile (should be under 800ms for mobile)
        print("  Testing mobile performance requirements...")
        mobile_performance_times = []
        
        for i in range(3):
            perf_result = await self.make_request("/marketplace/browse", params={"limit": 5})
            if perf_result["success"]:
                mobile_performance_times.append(perf_result["response_time_ms"])
        
        if mobile_performance_times:
            avg_mobile_time = sum(mobile_performance_times) / len(mobile_performance_times)
            mobile_performance_acceptable = avg_mobile_time < 800  # Mobile target
            
            browse_tests.append({
                "test": "Mobile Performance",
                "success": mobile_performance_acceptable,
                "avg_response_time_ms": avg_mobile_time,
                "mobile_performance_target_ms": 800,
                "meets_mobile_target": mobile_performance_acceptable,
                "performance_times": mobile_performance_times
            })
            
            print(f"    {'✅' if mobile_performance_acceptable else '⚠️'} Mobile performance: {avg_mobile_time:.0f}ms (target: <800ms)")
        else:
            browse_tests.append({
                "test": "Mobile Performance",
                "success": False,
                "error": "Could not measure mobile performance",
                "performance_times": []
            })
            print("    ❌ Could not measure mobile performance")
        
        # Calculate overall success
        successful_tests = [t for t in browse_tests if t.get("success", False)]
        
        return {
            "test_name": "Browse Listings API Testing",
            "total_tests": len(browse_tests),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(browse_tests) * 100 if browse_tests else 0,
            "browse_listings_working": any(t.get("test") == "GET Browse Listings" and t.get("success") for t in browse_tests),
            "mobile_parameters_working": any(t.get("test") == "Mobile Browse Parameters" and t.get("success") for t in browse_tests),
            "mobile_performance_acceptable": any(t.get("test") == "Mobile Performance" and t.get("success") for t in browse_tests),
            "mobile_data_structure_valid": any(t.get("mobile_data_structure_valid", {}).get("score", 0) >= 80 for t in browse_tests),
            "browse_api_mobile_ready": len(successful_tests) == len(browse_tests),
            "detailed_test_results": browse_tests
        }
    
    def validate_mobile_data_structure(self, listings: List[Dict]) -> Dict:
        """Validate data structure for mobile compatibility"""
        if not listings or not isinstance(listings, list):
            return {"score": 0, "issues": ["Not a valid array"]}
        
        total_checks = 0
        passed_checks = 0
        issues = []
        
        for listing in listings[:5]:  # Check first 5 listings
            # Check required fields for mobile
            required_fields = ["id", "title", "price", "seller"]
            for field in required_fields:
                total_checks += 1
                if field in listing and listing[field] is not None:
                    passed_checks += 1
                else:
                    issues.append(f"Missing {field}")
            
            # Check seller information structure
            if "seller" in listing and isinstance(listing["seller"], dict):
                seller = listing["seller"]
                seller_fields = ["name", "username"]
                for field in seller_fields:
                    total_checks += 1
                    if field in seller:
                        passed_checks += 1
                    else:
                        issues.append(f"Missing seller.{field}")
            
            # Check bid information (important for mobile)
            if "bid_info" in listing and isinstance(listing["bid_info"], dict):
                bid_info = listing["bid_info"]
                bid_fields = ["has_bids", "total_bids", "highest_bid"]
                for field in bid_fields:
                    total_checks += 1
                    if field in bid_info:
                        passed_checks += 1
                    else:
                        issues.append(f"Missing bid_info.{field}")
        
        score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        return {
            "score": score,
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "issues": list(set(issues))  # Remove duplicates
        }
    
    async def run_comprehensive_mobile_api_test(self) -> Dict:
        """Run all mobile API tests"""
        print("🚀 Starting Mobile Functionality API Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Step 1: Authenticate users
            demo_auth = await self.authenticate_demo_user()
            admin_auth = await self.authenticate_admin_user()
            
            # Step 2: Run API tests
            messages_test = await self.test_messages_api()
            ads_test = await self.test_ads_management_api()
            browse_test = await self.test_browse_listings_api()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "authentication": {
                    "demo_user": demo_auth,
                    "admin_user": admin_auth
                },
                "messages_api": messages_test,
                "ads_management_api": ads_test,
                "browse_listings_api": browse_test
            }
            
            # Calculate overall success metrics
            api_test_results = [
                messages_test.get("messages_api_functional", False),
                ads_test.get("ads_management_functional", False),
                browse_test.get("browse_api_mobile_ready", False)
            ]
            
            auth_success = demo_auth.get("success", False) and admin_auth.get("success", False)
            overall_success_rate = sum(api_test_results) / len(api_test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "authentication_successful": auth_success,
                "messages_api_working": messages_test.get("messages_api_functional", False),
                "ads_management_working": ads_test.get("ads_management_functional", False),
                "browse_listings_mobile_ready": browse_test.get("browse_api_mobile_ready", False),
                "mobile_apis_functional": overall_success_rate >= 75,
                "all_tests_passed": overall_success_rate == 100 and auth_success,
                "critical_issues": self.identify_critical_issues(messages_test, ads_test, browse_test)
            }
            
            return all_results
            
        finally:
            await self.cleanup()
    
    def identify_critical_issues(self, messages_test: Dict, ads_test: Dict, browse_test: Dict) -> List[str]:
        """Identify critical issues that could cause mobile messages to get stuck on loading"""
        issues = []
        
        # Check messages API issues
        if not messages_test.get("get_messages_working", False):
            issues.append("GET messages endpoint not working - mobile messages will fail to load")
        
        if not messages_test.get("post_messages_working", False):
            issues.append("POST messages endpoint not working - mobile users cannot send messages")
        
        # Check ads management issues
        if not ads_test.get("get_active_ads_working", False):
            issues.append("Active ads endpoint not working - mobile ads will not display")
        
        if not ads_test.get("inactive_by_default_verified", False):
            issues.append("Ads not created as inactive by default - may show unapproved ads")
        
        # Check browse listings issues
        if not browse_test.get("browse_listings_working", False):
            issues.append("Browse listings endpoint not working - mobile marketplace will fail")
        
        if not browse_test.get("mobile_performance_acceptable", False):
            issues.append("Browse listings too slow for mobile - may cause loading timeouts")
        
        return issues


async def main():
    """Main test execution"""
    tester = MobileAPITester()
    results = await tester.run_comprehensive_mobile_api_test()
    
    print("\n" + "=" * 60)
    print("📊 MOBILE FUNCTIONALITY API TEST RESULTS")
    print("=" * 60)
    
    summary = results.get("summary", {})
    
    print(f"🎯 Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"🔐 Authentication: {'✅' if summary.get('authentication_successful') else '❌'}")
    print(f"💬 Messages API: {'✅' if summary.get('messages_api_working') else '❌'}")
    print(f"📢 Ads Management API: {'✅' if summary.get('ads_management_working') else '❌'}")
    print(f"🔍 Browse Listings API: {'✅' if summary.get('browse_listings_mobile_ready') else '❌'}")
    
    critical_issues = summary.get("critical_issues", [])
    if critical_issues:
        print(f"\n🚨 CRITICAL ISSUES FOUND ({len(critical_issues)}):")
        for issue in critical_issues:
            print(f"  ❌ {issue}")
    else:
        print(f"\n✅ NO CRITICAL ISSUES FOUND")
    
    print(f"\n🏁 Mobile APIs Functional: {'✅ YES' if summary.get('mobile_apis_functional') else '❌ NO'}")
    
    # Save detailed results
    with open('/app/mobile_api_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/mobile_api_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())