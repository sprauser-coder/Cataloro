#!/usr/bin/env python3
"""
Additional Authentication Tests
Testing edge cases and security scenarios
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://market-refactor-1.preview.emergentagent.com/api"

class AdditionalAuthTester:
    def __init__(self):
        self.session = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params=None, data=None, headers=None):
        """Make HTTP request"""
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
            if headers:
                request_kwargs['headers'] = headers
            
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **request_kwargs) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "status": response.status,
                    "data": response_data,
                    "headers": dict(response.headers)
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": 0
            }
    
    async def test_invalid_credentials(self):
        """Test login with invalid credentials"""
        print("🔒 Testing invalid credentials...")
        
        invalid_tests = [
            {"email": "admin@cataloro.com", "password": "wrong_password"},
            {"email": "nonexistent@cataloro.com", "password": "any_password"},
            {"email": "", "password": ""},
            {"email": "admin@cataloro.com", "password": ""},
        ]
        
        results = []
        for test in invalid_tests:
            result = await self.make_request("/auth/login", "POST", data=test)
            results.append({
                "credentials": test,
                "blocked": not result["success"],
                "status": result["status"],
                "error": result.get("error") if not result["success"] else None
            })
            
            status_emoji = "✅" if not result["success"] else "❌"
            print(f"  {status_emoji} {test['email'][:20]}... - Status: {result['status']}")
        
        return {
            "test_name": "Invalid Credentials Test",
            "results": results,
            "all_blocked": all(r["blocked"] for r in results)
        }
    
    async def test_token_validation(self):
        """Test token validation scenarios"""
        print("🎫 Testing token validation...")
        
        # First get a valid token
        login_result = await self.make_request("/auth/login", "POST", data={
            "email": "admin@cataloro.com",
            "password": "admin_password"
        })
        
        if not login_result["success"]:
            return {"test_name": "Token Validation", "error": "Could not get valid token"}
        
        valid_token = login_result["data"]["token"]
        
        # Test various token scenarios
        token_tests = [
            {"name": "Valid Token", "token": valid_token, "should_work": True},
            {"name": "Invalid Token", "token": "invalid_token_12345", "should_work": False},
            {"name": "Empty Token", "token": "", "should_work": False},
            {"name": "Malformed Token", "token": "Bearer invalid", "should_work": False},
            {"name": "Expired-like Token", "token": "mock_token_expired_user", "should_work": False},
        ]
        
        results = []
        for test in token_tests:
            headers = {"Authorization": f"Bearer {test['token']}"} if test['token'] else {}
            result = await self.make_request("/auth/profile/admin_user_1", headers=headers)
            
            works_as_expected = (result["success"] == test["should_work"])
            
            results.append({
                "test_name": test["name"],
                "token_works": result["success"],
                "should_work": test["should_work"],
                "works_as_expected": works_as_expected,
                "status": result["status"]
            })
            
            emoji = "✅" if works_as_expected else "❌"
            print(f"  {emoji} {test['name']}: {result['status']}")
        
        return {
            "test_name": "Token Validation",
            "results": results,
            "all_working_as_expected": all(r["works_as_expected"] for r in results)
        }
    
    async def test_admin_endpoints_security(self):
        """Test admin endpoints without proper authentication"""
        print("🛡️ Testing admin endpoints security...")
        
        admin_endpoints = [
            "/admin/dashboard",
            "/admin/users", 
            "/admin/menu-settings",
            "/admin/performance",
            "/admin/cache/clear"
        ]
        
        results = []
        for endpoint in admin_endpoints:
            # Test without any authentication
            no_auth_result = await self.make_request(endpoint)
            
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token"}
            invalid_auth_result = await self.make_request(endpoint, headers=invalid_headers)
            
            # Determine if endpoint is properly secured
            properly_secured = (not no_auth_result["success"] and 
                              not invalid_auth_result["success"] and
                              no_auth_result["status"] in [401, 403] and
                              invalid_auth_result["status"] in [401, 403])
            
            results.append({
                "endpoint": endpoint,
                "no_auth_status": no_auth_result["status"],
                "invalid_auth_status": invalid_auth_result["status"],
                "properly_secured": properly_secured,
                "accessible_without_auth": no_auth_result["success"],
                "accessible_with_invalid_auth": invalid_auth_result["success"]
            })
            
            emoji = "✅" if properly_secured else "❌"
            print(f"  {emoji} {endpoint}: No auth={no_auth_result['status']}, Invalid auth={invalid_auth_result['status']}")
        
        return {
            "test_name": "Admin Endpoints Security",
            "results": results,
            "all_properly_secured": all(r["properly_secured"] for r in results),
            "security_issues": [r["endpoint"] for r in results if not r["properly_secured"]]
        }
    
    async def test_user_profile_access(self):
        """Test user profile access with different user IDs"""
        print("👤 Testing user profile access...")
        
        # Get admin token first
        login_result = await self.make_request("/auth/login", "POST", data={
            "email": "admin@cataloro.com",
            "password": "admin_password"
        })
        
        if not login_result["success"]:
            return {"test_name": "User Profile Access", "error": "Could not get admin token"}
        
        admin_token = login_result["data"]["token"]
        admin_user_id = login_result["data"]["user"]["id"]
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test profile access scenarios
        profile_tests = [
            {"name": "Own Profile", "user_id": admin_user_id, "should_work": True},
            {"name": "Demo User Profile", "user_id": "68bfff790e4e46bc28d43631", "should_work": True},
            {"name": "Non-existent User", "user_id": "non_existent_user_123", "should_work": False},
            {"name": "Invalid User ID", "user_id": "invalid_id", "should_work": False},
        ]
        
        results = []
        for test in profile_tests:
            result = await self.make_request(f"/auth/profile/{test['user_id']}", headers=headers)
            
            works_as_expected = (result["success"] == test["should_work"])
            
            results.append({
                "test_name": test["name"],
                "user_id": test["user_id"],
                "accessible": result["success"],
                "should_work": test["should_work"],
                "works_as_expected": works_as_expected,
                "status": result["status"]
            })
            
            emoji = "✅" if works_as_expected else "❌"
            print(f"  {emoji} {test['name']}: {result['status']}")
        
        return {
            "test_name": "User Profile Access",
            "results": results,
            "all_working_as_expected": all(r["works_as_expected"] for r in results)
        }
    
    async def run_additional_tests(self):
        """Run all additional authentication tests"""
        print("🔍 Starting Additional Authentication Tests")
        print("=" * 50)
        
        await self.setup()
        
        try:
            invalid_creds = await self.test_invalid_credentials()
            token_validation = await self.test_token_validation()
            admin_security = await self.test_admin_endpoints_security()
            profile_access = await self.test_user_profile_access()
            
            results = {
                "test_timestamp": datetime.now().isoformat(),
                "tests": {
                    "invalid_credentials": invalid_creds,
                    "token_validation": token_validation,
                    "admin_endpoints_security": admin_security,
                    "user_profile_access": profile_access
                }
            }
            
            # Calculate summary
            security_issues = admin_security.get("security_issues", [])
            
            results["summary"] = {
                "invalid_credentials_blocked": invalid_creds.get("all_blocked", False),
                "token_validation_working": token_validation.get("all_working_as_expected", False),
                "admin_endpoints_secured": admin_security.get("all_properly_secured", False),
                "profile_access_working": profile_access.get("all_working_as_expected", False),
                "security_issues_found": len(security_issues),
                "security_issues": security_issues,
                "overall_security_score": 0
            }
            
            # Calculate overall security score
            security_checks = [
                invalid_creds.get("all_blocked", False),
                token_validation.get("all_working_as_expected", False),
                admin_security.get("all_properly_secured", False),
                profile_access.get("all_working_as_expected", False)
            ]
            
            results["summary"]["overall_security_score"] = sum(security_checks) / len(security_checks) * 100
            
            return results
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = AdditionalAuthTester()
    results = await tester.run_additional_tests()
    
    # Print summary
    print("\n" + "=" * 50)
    print("🏁 ADDITIONAL AUTHENTICATION TESTS SUMMARY")
    print("=" * 50)
    
    summary = results.get("summary", {})
    
    print(f"🔒 Invalid Credentials Blocked: {'✅' if summary.get('invalid_credentials_blocked') else '❌'}")
    print(f"🎫 Token Validation Working: {'✅' if summary.get('token_validation_working') else '❌'}")
    print(f"🛡️ Admin Endpoints Secured: {'✅' if summary.get('admin_endpoints_secured') else '❌'}")
    print(f"👤 Profile Access Working: {'✅' if summary.get('profile_access_working') else '❌'}")
    print(f"📊 Overall Security Score: {summary.get('overall_security_score', 0):.1f}%")
    
    security_issues = summary.get("security_issues", [])
    if security_issues:
        print(f"\n🚨 Security Issues Found:")
        for issue in security_issues:
            print(f"  ❌ {issue} - Not properly secured")
    else:
        print(f"\n✅ No Security Issues Found")
    
    # Save results
    with open("/app/additional_auth_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: /app/additional_auth_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())