#!/usr/bin/env python3
"""
Admin Panel Fixes Backend Testing
Testing Agent: Focused testing of recently implemented admin panel fixes
"""

import asyncio
import aiohttp
import json
import uuid
import time
import base64
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://cataloro-menueditor.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class AdminPanelFixesTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_users = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")
            
    async def make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request with error handling"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "DELETE":
                async with self.session.delete(url, params=params) as response:
                    return await response.json(), response.status
                    
        except Exception as e:
            return {"error": str(e)}, 500
            
    async def setup_test_data(self):
        """Setup test users for admin panel testing"""
        print("\n🔧 Setting up test data...")
        
        # Login as admin user
        admin_login_response, admin_status = await self.make_request("POST", "/auth/login", {
            "email": "admin@cataloro.com",
            "password": "admin123"
        })
        
        if admin_status == 200 and "user" in admin_login_response:
            admin_user = admin_login_response["user"]
            self.test_users.append(admin_user)
            print(f"✅ Admin user logged in: {admin_user.get('username', 'admin')}")
        
        # Create a demo user for testing
        demo_login_response, demo_status = await self.make_request("POST", "/auth/login", {
            "email": "user@cataloro.com",
            "password": "demo123"
        })
        
        if demo_status == 200 and "user" in demo_login_response:
            demo_user = demo_login_response["user"]
            self.test_users.append(demo_user)
            print(f"✅ Demo user logged in: {demo_user.get('username', 'demo')}")
        
        print(f"✅ Setup {len(self.test_users)} test users")
                
    async def test_export_manager_functionality(self):
        """Test Export Manager functionality - basket PDF export"""
        print("\n📄 Testing Export Manager - Basket PDF Export...")
        
        # Test POST /api/admin/export/basket-pdf endpoint
        sample_basket_data = {
            "items": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "BMW 320d Catalytic Converter",
                    "weight": 2.5,
                    "pt_ppm": 1200,
                    "pd_ppm": 800,
                    "rh_ppm": 150,
                    "price": 450.00
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Mercedes E-Class Catalyst",
                    "weight": 3.2,
                    "pt_ppm": 1500,
                    "pd_ppm": 1000,
                    "rh_ppm": 200,
                    "price": 650.00
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Audi A4 Catalytic Converter",
                    "weight": 1.8,
                    "pt_ppm": 900,
                    "pd_ppm": 600,
                    "rh_ppm": 120,
                    "price": 350.00
                }
            ],
            "total_value": 1450.00,
            "basket_name": "Test Basket Export"
        }
        
        response, status = await self.make_request("POST", "/admin/export/basket-pdf", sample_basket_data)
        
        if status == 200:
            pdf_data = response.get("pdf_data")
            filename = response.get("filename")
            items_count = response.get("items_count")
            total_value = response.get("total_value")
            
            if pdf_data and filename:
                # Verify PDF data is base64 encoded and valid
                try:
                    decoded = base64.b64decode(pdf_data)
                    if decoded.startswith(b'%PDF'):
                        self.log_result("Export Manager - Basket PDF", True, 
                                      f"PDF generated: {filename}, Items: {items_count}, Total: €{total_value}")
                    else:
                        self.log_result("Export Manager - Basket PDF", False, "PDF data is not valid PDF format")
                except Exception as e:
                    self.log_result("Export Manager - Basket PDF", False, f"PDF validation failed: {str(e)}")
            else:
                self.log_result("Export Manager - Basket PDF", False, "Missing pdf_data or filename in response")
        else:
            self.log_result("Export Manager - Basket PDF", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
        # Test with empty basket
        empty_basket_data = {
            "items": [],
            "total_value": 0.00,
            "basket_name": "Empty Test Basket"
        }
        
        response, status = await self.make_request("POST", "/admin/export/basket-pdf", empty_basket_data)
        
        if status == 200:
            self.log_result("Export Manager - Empty Basket PDF", True, "Empty basket PDF generated successfully")
        else:
            self.log_result("Export Manager - Empty Basket PDF", False, f"Status: {status}")
            
    async def test_profile_account_actions(self):
        """Test Profile Account Actions - Export Data and Delete Account"""
        print("\n👤 Testing Profile Account Actions...")
        
        if len(self.test_users) < 1:
            self.log_result("Profile Account Actions Setup", False, "No test users available")
            return
            
        user = self.test_users[0]
        user_id = user["id"]
        
        # Test 1: POST /api/auth/profile/{user_id}/export (Export Data button)
        response, status = await self.make_request("POST", f"/auth/profile/{user_id}/export")
        
        if status == 200:
            pdf_data = response.get("pdf_data")
            filename = response.get("filename")
            
            if pdf_data and filename:
                # Verify PDF data is base64 encoded and valid
                try:
                    decoded = base64.b64decode(pdf_data)
                    if decoded.startswith(b'%PDF'):
                        self.log_result("Profile Export Data", True, f"User data export successful: {filename}")
                    else:
                        self.log_result("Profile Export Data", False, "PDF data is not valid PDF format")
                except Exception as e:
                    self.log_result("Profile Export Data", False, f"PDF validation failed: {str(e)}")
            else:
                self.log_result("Profile Export Data", False, "Missing pdf_data or filename in response")
        else:
            self.log_result("Profile Export Data", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
        # Test 2: Delete Account functionality (we'll test validation without actually deleting)
        # Test with invalid confirmation text
        invalid_delete_data = {
            "password": "test123",
            "confirmation": "wrong confirmation"
        }
        
        response, status = await self.make_request("DELETE", f"/auth/profile/{user_id}/delete-account", invalid_delete_data)
        
        if status in [400, 422]:  # Accept both 400 and 422 for validation errors
            self.log_result("Profile Delete Account - Invalid Confirmation", True, "Correctly rejected invalid confirmation text")
        else:
            self.log_result("Profile Delete Account - Invalid Confirmation", False, f"Should reject invalid confirmation, got status: {status}")
            
    async def test_username_verification(self):
        """Test Username Verification endpoint"""
        print("\n🔍 Testing Username Verification...")
        
        # Test 1: Check available username
        test_username = f"test_user_{int(time.time())}"
        response, status = await self.make_request("GET", f"/auth/check-username/{test_username}")
        
        if status == 200:
            available = response.get("available", False)
            if available:
                self.log_result("Username Verification - Available", True, f"Username '{test_username}' is available")
            else:
                reason = response.get("reason", "Unknown reason")
                self.log_result("Username Verification - Available", False, f"Username check failed: {reason}")
        else:
            self.log_result("Username Verification - Available", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
        # Test 2: Check existing username (should be unavailable)
        if len(self.test_users) > 0:
            existing_username = self.test_users[0].get("username", "admin")
            response, status = await self.make_request("GET", f"/auth/check-username/{existing_username}")
            
            if status == 200:
                available = response.get("available", True)
                if not available:
                    self.log_result("Username Verification - Existing", True, f"Correctly identified '{existing_username}' as taken")
                else:
                    self.log_result("Username Verification - Existing", False, f"Should identify existing username as taken")
            else:
                self.log_result("Username Verification - Existing", False, f"Status: {status}")
                
        # Test 3: Check invalid username format
        invalid_username = "a"  # Too short
        response, status = await self.make_request("GET", f"/auth/check-username/{invalid_username}")
        
        if status == 200:
            available = response.get("available", True)
            if not available:
                reason = response.get("reason", "")
                if "3 and 50 characters" in reason:
                    self.log_result("Username Verification - Invalid Format", True, "Correctly rejected short username")
                else:
                    self.log_result("Username Verification - Invalid Format", False, f"Wrong rejection reason: {reason}")
            else:
                self.log_result("Username Verification - Invalid Format", False, "Should reject invalid username format")
        else:
            self.log_result("Username Verification - Invalid Format", False, f"Status: {status}")
            
    async def test_public_profile_api(self):
        """Test Public Profile API endpoint"""
        print("\n🌐 Testing Public Profile API...")
        
        if len(self.test_users) < 1:
            self.log_result("Public Profile API Setup", False, "No test users available")
            return
            
        user = self.test_users[0]
        user_id = user["id"]
        
        # Test GET /api/profile/{user_id}/public endpoint
        response, status = await self.make_request("GET", f"/profile/{user_id}/public")
        
        if status == 200:
            is_public = response.get("public", False)
            
            if is_public:
                # Check required fields for public profile
                required_fields = ["user", "statistics", "ratings"]
                missing_fields = [field for field in required_fields if field not in response]
                
                if not missing_fields:
                    user_data = response["user"]
                    username = user_data.get("username", "Unknown")
                    total_listings = response["statistics"].get("total_listings", 0)
                    self.log_result("Public Profile API", True, 
                                  f"Public profile accessible for '{username}', Listings: {total_listings}")
                else:
                    self.log_result("Public Profile API", False, f"Missing required fields: {missing_fields}")
            else:
                message = response.get("message", "")
                self.log_result("Public Profile API", True, f"Profile is private: {message}")
        else:
            self.log_result("Public Profile API", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
        # Test with non-existent user ID
        fake_user_id = str(uuid.uuid4())
        response, status = await self.make_request("GET", f"/profile/{fake_user_id}/public")
        
        if status == 404:
            self.log_result("Public Profile API - Not Found", True, "Correctly handled non-existent user")
        else:
            self.log_result("Public Profile API - Not Found", False, f"Should return 404 for non-existent user, got: {status}")
            
    async def test_backend_health(self):
        """Test backend health and connectivity"""
        print("\n🏥 Testing Backend Health...")
        
        response, status = await self.make_request("GET", "/health")
        
        if status == 200:
            app_name = response.get("app", "")
            version = response.get("version", "")
            self.log_result("Backend Health Check", True, f"App: {app_name}, Version: {version}")
        else:
            self.log_result("Backend Health Check", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🧪 ADMIN PANEL FIXES TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error']}")
                    
        print(f"\n🎯 ADMIN PANEL FIXES TESTED:")
        print(f"   • Export Manager (Basket PDF): /api/admin/export/basket-pdf")
        print(f"   • Profile Export Data: /api/auth/profile/{{user_id}}/export")
        print(f"   • Username Verification: /api/auth/check-username/{{username}}")
        print(f"   • Public Profile API: /api/profile/{{user_id}}/public")
        print(f"   • Delete Account Validation: /api/auth/profile/{{user_id}}/delete-account")
        
        print(f"\n📊 FEATURE COVERAGE:")
        export_tests = [r for r in self.test_results if "Export" in r["test"]]
        profile_tests = [r for r in self.test_results if "Profile" in r["test"]]
        username_tests = [r for r in self.test_results if "Username" in r["test"]]
        
        print(f"   • Export Manager: {sum(1 for t in export_tests if t['success'])}/{len(export_tests)} passed")
        print(f"   • Profile Actions: {sum(1 for t in profile_tests if t['success'])}/{len(profile_tests)} passed")
        print(f"   • Username Verification: {sum(1 for t in username_tests if t['success'])}/{len(username_tests)} passed")
        
        # Identify critical issues
        critical_failures = []
        for result in self.test_results:
            if not result["success"] and any(keyword in result["test"] for keyword in ["Export Manager", "Profile Export", "Username Verification", "Public Profile API"]):
                critical_failures.append(result["test"])
                
        if critical_failures:
            print(f"\n⚠️ CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   • {failure}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES - All admin panel fixes working correctly")

async def main():
    """Main test execution"""
    print("🚀 Starting Admin Panel Fixes Backend Testing")
    print(f"🌐 Backend URL: {BASE_URL}")
    print("="*80)
    
    tester = AdminPanelFixesTester()
    
    try:
        await tester.setup_session()
        
        # Test backend health first
        await tester.test_backend_health()
        
        # Setup test data
        await tester.setup_test_data()
        
        # Run all admin panel fix tests
        await tester.test_export_manager_functionality()
        await tester.test_profile_account_actions()
        await tester.test_username_verification()
        await tester.test_public_profile_api()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())