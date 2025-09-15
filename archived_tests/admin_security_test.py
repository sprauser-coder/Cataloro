#!/usr/bin/env python3
"""
CRITICAL ADMIN SECURITY TESTING
Testing admin endpoints authentication and JWT token security fixes
"""

import asyncio
import aiohttp
import time
import json
import jwt
import base64
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://nginx-config-fix.preview.emergentagent.com/api"

# Admin credentials for testing
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

# Regular user credentials for role testing
DEMO_EMAIL = "demo@cataloro.com"
DEMO_PASSWORD = "demo_password"

class AdminSecurityTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.test_results = []
        
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
    
    async def test_jwt_token_generation(self) -> Dict:
        """Test that login generates real JWT tokens, not mock tokens"""
        print("🔐 Testing JWT Token Generation...")
        
        # Test admin login
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if not result["success"]:
            return {
                "test_name": "JWT Token Generation",
                "success": False,
                "error": f"Admin login failed: {result.get('error', 'Unknown error')}",
                "status": result["status"]
            }
        
        user_data = result["data"].get("user", {})
        token = result["data"].get("token", "")
        
        # Store admin token for subsequent tests
        self.admin_token = token
        
        # Analyze token structure
        token_analysis = self.analyze_jwt_token(token)
        
        print(f"  ✅ Admin login successful")
        print(f"  🎫 Token received: {'✅' if token else '❌'}")
        print(f"  🔍 Token type: {token_analysis['token_type']}")
        print(f"  📝 Token structure: {token_analysis['structure_valid']}")
        
        if token_analysis['is_jwt']:
            print(f"  📋 JWT payload fields: {list(token_analysis['payload'].keys())}")
            print(f"  👤 User ID in token: {token_analysis['payload'].get('user_id', 'Missing')}")
            print(f"  📧 Email in token: {token_analysis['payload'].get('email', 'Missing')}")
            print(f"  🔑 Role in token: {token_analysis['payload'].get('role', 'Missing')}")
        
        return {
            "test_name": "JWT Token Generation",
            "success": True,
            "token_received": bool(token),
            "token_analysis": token_analysis,
            "user_data": user_data,
            "is_real_jwt": token_analysis['is_jwt'],
            "has_required_fields": token_analysis['has_required_fields'],
            "token_not_mock": not token.startswith("mock_token") if token else False
        }
    
    def analyze_jwt_token(self, token: str) -> Dict:
        """Analyze JWT token structure and content"""
        if not token:
            return {
                "token_type": "empty",
                "is_jwt": False,
                "structure_valid": False,
                "has_required_fields": False
            }
        
        # Check if it's a mock token
        if token.startswith("mock_token"):
            return {
                "token_type": "mock_token",
                "is_jwt": False,
                "structure_valid": False,
                "has_required_fields": False,
                "mock_token": True
            }
        
        # Try to decode JWT token
        try:
            # Split token into parts
            parts = token.split('.')
            if len(parts) != 3:
                return {
                    "token_type": "invalid_jwt_structure",
                    "is_jwt": False,
                    "structure_valid": False,
                    "has_required_fields": False
                }
            
            # Decode header and payload (without verification for analysis)
            header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
            
            # Check required fields
            required_fields = ['user_id', 'email', 'role']
            has_required_fields = all(field in payload for field in required_fields)
            
            return {
                "token_type": "jwt",
                "is_jwt": True,
                "structure_valid": True,
                "header": header,
                "payload": payload,
                "has_required_fields": has_required_fields,
                "required_fields_present": [field for field in required_fields if field in payload],
                "missing_fields": [field for field in required_fields if field not in payload]
            }
            
        except Exception as e:
            return {
                "token_type": "invalid_jwt",
                "is_jwt": False,
                "structure_valid": False,
                "has_required_fields": False,
                "decode_error": str(e)
            }
    
    async def test_admin_endpoints_with_auth(self) -> Dict:
        """Test admin endpoints WITH valid authentication"""
        print("🔒 Testing Admin Endpoints WITH Authentication...")
        
        if not self.admin_token:
            return {
                "test_name": "Admin Endpoints With Auth",
                "success": False,
                "error": "No admin token available"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test all admin endpoints
        admin_endpoints = [
            {"endpoint": "/admin/menu-settings", "method": "GET", "name": "Menu Settings GET"},
            {"endpoint": "/admin/menu-settings", "method": "POST", "name": "Menu Settings POST", 
             "data": {"desktop_menu": {"test": "data"}, "mobile_menu": {"test": "data"}}},
            {"endpoint": "/admin/dashboard", "method": "GET", "name": "Admin Dashboard"},
            {"endpoint": "/admin/users", "method": "GET", "name": "Admin Users"},
            {"endpoint": "/admin/performance", "method": "GET", "name": "Admin Performance"}
        ]
        
        endpoint_results = []
        
        for endpoint_test in admin_endpoints:
            print(f"  Testing {endpoint_test['name']}...")
            
            result = await self.make_request(
                endpoint_test["endpoint"], 
                endpoint_test["method"], 
                data=endpoint_test.get("data"),
                headers=headers
            )
            
            endpoint_result = {
                "endpoint": endpoint_test["endpoint"],
                "method": endpoint_test["method"],
                "name": endpoint_test["name"],
                "success": result["success"],
                "status": result["status"],
                "response_time_ms": result["response_time_ms"],
                "authenticated_access": result["success"]
            }
            
            if result["success"]:
                print(f"    ✅ {endpoint_test['name']}: {result['status']} ({result['response_time_ms']:.0f}ms)")
            else:
                print(f"    ❌ {endpoint_test['name']}: {result['status']} - {result.get('error', 'Failed')}")
                endpoint_result["error"] = result.get("error", "Request failed")
            
            endpoint_results.append(endpoint_result)
        
        successful_endpoints = [r for r in endpoint_results if r["success"]]
        
        return {
            "test_name": "Admin Endpoints With Auth",
            "success": True,
            "total_endpoints": len(admin_endpoints),
            "successful_endpoints": len(successful_endpoints),
            "success_rate": len(successful_endpoints) / len(admin_endpoints) * 100,
            "all_endpoints_accessible": len(successful_endpoints) == len(admin_endpoints),
            "endpoint_results": endpoint_results
        }
    
    async def test_admin_endpoints_without_auth(self) -> Dict:
        """Test admin endpoints WITHOUT authentication (should return 401)"""
        print("🚫 Testing Admin Endpoints WITHOUT Authentication...")
        
        # Test all admin endpoints without auth headers
        admin_endpoints = [
            {"endpoint": "/admin/menu-settings", "method": "GET", "name": "Menu Settings GET"},
            {"endpoint": "/admin/menu-settings", "method": "POST", "name": "Menu Settings POST", 
             "data": {"desktop_menu": {"test": "data"}, "mobile_menu": {"test": "data"}}},
            {"endpoint": "/admin/dashboard", "method": "GET", "name": "Admin Dashboard"},
            {"endpoint": "/admin/users", "method": "GET", "name": "Admin Users"},
            {"endpoint": "/admin/performance", "method": "GET", "name": "Admin Performance"}
        ]
        
        endpoint_results = []
        
        for endpoint_test in admin_endpoints:
            print(f"  Testing {endpoint_test['name']} without auth...")
            
            result = await self.make_request(
                endpoint_test["endpoint"], 
                endpoint_test["method"], 
                data=endpoint_test.get("data")
                # No headers = no authentication
            )
            
            # Should return 401 Unauthorized or 403 Forbidden
            properly_blocked = result["status"] in [401, 403]
            
            endpoint_result = {
                "endpoint": endpoint_test["endpoint"],
                "method": endpoint_test["method"],
                "name": endpoint_test["name"],
                "status": result["status"],
                "response_time_ms": result["response_time_ms"],
                "properly_blocked": properly_blocked,
                "security_vulnerability": result["success"]  # If success=True, it's a vulnerability
            }
            
            if properly_blocked:
                print(f"    ✅ {endpoint_test['name']}: Properly blocked ({result['status']})")
            elif result["success"]:
                print(f"    🚨 {endpoint_test['name']}: SECURITY VULNERABILITY - Accessible without auth!")
                endpoint_result["vulnerability_details"] = "Endpoint accessible without authentication"
            else:
                print(f"    ⚠️ {endpoint_test['name']}: {result['status']} - {result.get('error', 'Unknown error')}")
                endpoint_result["error"] = result.get("error", "Request failed")
            
            endpoint_results.append(endpoint_result)
        
        properly_blocked_count = len([r for r in endpoint_results if r["properly_blocked"]])
        vulnerable_endpoints = [r for r in endpoint_results if r.get("security_vulnerability", False)]
        
        return {
            "test_name": "Admin Endpoints Without Auth",
            "success": True,
            "total_endpoints": len(admin_endpoints),
            "properly_blocked_endpoints": properly_blocked_count,
            "vulnerable_endpoints": len(vulnerable_endpoints),
            "security_score": properly_blocked_count / len(admin_endpoints) * 100,
            "all_endpoints_secured": len(vulnerable_endpoints) == 0,
            "endpoint_results": endpoint_results,
            "vulnerable_endpoint_details": vulnerable_endpoints
        }
    
    async def test_admin_endpoints_with_invalid_token(self) -> Dict:
        """Test admin endpoints with invalid/fake tokens (should return 401)"""
        print("🔓 Testing Admin Endpoints WITH Invalid Tokens...")
        
        # Test with various invalid tokens
        invalid_tokens = [
            "invalid_token_123",
            "Bearer fake_jwt_token",
            "mock_token_admin_user_1",  # Old mock token format
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # Sample JWT
            ""  # Empty token
        ]
        
        test_endpoint = "/admin/menu-settings"
        token_results = []
        
        for i, invalid_token in enumerate(invalid_tokens):
            token_name = f"Invalid Token {i+1}"
            if invalid_token == "":
                token_name = "Empty Token"
            elif invalid_token.startswith("mock_token"):
                token_name = "Mock Token"
            elif invalid_token.startswith("eyJ"):
                token_name = "Sample JWT"
            
            print(f"  Testing with {token_name}...")
            
            headers = {"Authorization": f"Bearer {invalid_token}"} if invalid_token else {"Authorization": "Bearer "}
            
            result = await self.make_request(test_endpoint, "GET", headers=headers)
            
            # Should return 401 Unauthorized
            properly_rejected = result["status"] == 401
            
            token_result = {
                "token_name": token_name,
                "token_value": invalid_token[:20] + "..." if len(invalid_token) > 20 else invalid_token,
                "status": result["status"],
                "properly_rejected": properly_rejected,
                "security_vulnerability": result["success"]  # If success=True, it's a vulnerability
            }
            
            if properly_rejected:
                print(f"    ✅ {token_name}: Properly rejected (401)")
            elif result["success"]:
                print(f"    🚨 {token_name}: SECURITY VULNERABILITY - Invalid token accepted!")
                token_result["vulnerability_details"] = "Invalid token was accepted"
            else:
                print(f"    ⚠️ {token_name}: {result['status']} - {result.get('error', 'Unknown error')}")
            
            token_results.append(token_result)
        
        properly_rejected_count = len([r for r in token_results if r["properly_rejected"]])
        vulnerable_tokens = [r for r in token_results if r.get("security_vulnerability", False)]
        
        return {
            "test_name": "Admin Endpoints With Invalid Tokens",
            "success": True,
            "total_tokens_tested": len(invalid_tokens),
            "properly_rejected_tokens": properly_rejected_count,
            "vulnerable_tokens": len(vulnerable_tokens),
            "token_security_score": properly_rejected_count / len(invalid_tokens) * 100,
            "all_invalid_tokens_rejected": len(vulnerable_tokens) == 0,
            "token_results": token_results,
            "vulnerable_token_details": vulnerable_tokens
        }
    
    async def test_role_based_access_control(self) -> Dict:
        """Test role-based access control - regular users should not access admin endpoints"""
        print("👥 Testing Role-Based Access Control...")
        
        # First, get a regular user token
        demo_login_data = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login_data)
        
        if not demo_result["success"]:
            return {
                "test_name": "Role-Based Access Control",
                "success": False,
                "error": f"Failed to login demo user: {demo_result.get('error', 'Unknown error')}"
            }
        
        demo_user = demo_result["data"].get("user", {})
        demo_token = demo_result["data"].get("token", "")
        self.demo_token = demo_token
        
        print(f"  Demo user logged in: {demo_user.get('email')} (Role: {demo_user.get('role', demo_user.get('user_role'))})")
        
        # Test admin endpoints with regular user token
        headers = {"Authorization": f"Bearer {demo_token}"}
        
        admin_endpoints = [
            {"endpoint": "/admin/menu-settings", "method": "GET", "name": "Menu Settings"},
            {"endpoint": "/admin/dashboard", "method": "GET", "name": "Admin Dashboard"},
            {"endpoint": "/admin/users", "method": "GET", "name": "Admin Users"},
            {"endpoint": "/admin/performance", "method": "GET", "name": "Admin Performance"}
        ]
        
        rbac_results = []
        
        for endpoint_test in admin_endpoints:
            print(f"  Testing {endpoint_test['name']} with regular user token...")
            
            result = await self.make_request(
                endpoint_test["endpoint"], 
                endpoint_test["method"], 
                headers=headers
            )
            
            # Should return 403 Forbidden (not authorized for admin role)
            properly_blocked = result["status"] == 403
            
            rbac_result = {
                "endpoint": endpoint_test["endpoint"],
                "name": endpoint_test["name"],
                "status": result["status"],
                "properly_blocked": properly_blocked,
                "rbac_vulnerability": result["success"]  # If success=True, it's a vulnerability
            }
            
            if properly_blocked:
                print(f"    ✅ {endpoint_test['name']}: Properly blocked (403 Forbidden)")
            elif result["success"]:
                print(f"    🚨 {endpoint_test['name']}: RBAC VULNERABILITY - Regular user can access admin endpoint!")
                rbac_result["vulnerability_details"] = "Regular user can access admin endpoint"
            else:
                print(f"    ⚠️ {endpoint_test['name']}: {result['status']} - {result.get('error', 'Unknown error')}")
            
            rbac_results.append(rbac_result)
        
        properly_blocked_count = len([r for r in rbac_results if r["properly_blocked"]])
        vulnerable_endpoints = [r for r in rbac_results if r.get("rbac_vulnerability", False)]
        
        return {
            "test_name": "Role-Based Access Control",
            "success": True,
            "demo_user_role": demo_user.get("role", demo_user.get("user_role")),
            "total_endpoints": len(admin_endpoints),
            "properly_blocked_endpoints": properly_blocked_count,
            "vulnerable_endpoints": len(vulnerable_endpoints),
            "rbac_security_score": properly_blocked_count / len(admin_endpoints) * 100,
            "rbac_working_correctly": len(vulnerable_endpoints) == 0,
            "endpoint_results": rbac_results,
            "vulnerable_endpoint_details": vulnerable_endpoints
        }
    
    async def test_security_bypass_prevention(self) -> Dict:
        """Test various security bypass attempts"""
        print("🛡️ Testing Security Bypass Prevention...")
        
        bypass_tests = []
        
        # Test 1: Header manipulation
        print("  Testing header manipulation...")
        headers_tests = [
            {"X-Admin-Override": "true"},
            {"X-User-Role": "admin"},
            {"X-Bypass-Auth": "true"},
            {"Authorization": ""},
            {"Authorization": "Basic YWRtaW46YWRtaW4="},  # Basic auth
        ]
        
        for i, test_headers in enumerate(headers_tests):
            result = await self.make_request("/admin/dashboard", "GET", headers=test_headers)
            
            bypass_test = {
                "test_type": "Header Manipulation",
                "test_name": f"Header Test {i+1}",
                "headers": test_headers,
                "status": result["status"],
                "bypassed": result["success"],
                "properly_blocked": not result["success"]
            }
            
            if result["success"]:
                print(f"    🚨 Header Test {i+1}: BYPASS VULNERABILITY - {test_headers}")
            else:
                print(f"    ✅ Header Test {i+1}: Properly blocked")
            
            bypass_tests.append(bypass_test)
        
        # Test 2: URL manipulation
        print("  Testing URL manipulation...")
        url_tests = [
            "/admin/../admin/dashboard",
            "/admin/dashboard?admin=true",
            "/admin/dashboard#bypass",
            "/admin/dashboard/",
            "/ADMIN/DASHBOARD",  # Case sensitivity
        ]
        
        for i, test_url in enumerate(url_tests):
            result = await self.make_request(test_url, "GET")
            
            bypass_test = {
                "test_type": "URL Manipulation",
                "test_name": f"URL Test {i+1}",
                "url": test_url,
                "status": result["status"],
                "bypassed": result["success"],
                "properly_blocked": not result["success"]
            }
            
            if result["success"]:
                print(f"    🚨 URL Test {i+1}: BYPASS VULNERABILITY - {test_url}")
            else:
                print(f"    ✅ URL Test {i+1}: Properly blocked")
            
            bypass_tests.append(bypass_test)
        
        # Test 3: Method manipulation
        print("  Testing HTTP method manipulation...")
        method_tests = ["PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
        
        for method in method_tests:
            result = await self.make_request("/admin/dashboard", method)
            
            bypass_test = {
                "test_type": "Method Manipulation",
                "test_name": f"Method {method}",
                "method": method,
                "status": result["status"],
                "bypassed": result["success"],
                "properly_blocked": not result["success"]
            }
            
            if result["success"]:
                print(f"    🚨 Method {method}: BYPASS VULNERABILITY")
            else:
                print(f"    ✅ Method {method}: Properly blocked")
            
            bypass_tests.append(bypass_test)
        
        # Calculate security metrics
        total_tests = len(bypass_tests)
        properly_blocked = len([t for t in bypass_tests if t["properly_blocked"]])
        bypass_vulnerabilities = [t for t in bypass_tests if t["bypassed"]]
        
        return {
            "test_name": "Security Bypass Prevention",
            "success": True,
            "total_bypass_tests": total_tests,
            "properly_blocked_attempts": properly_blocked,
            "bypass_vulnerabilities": len(bypass_vulnerabilities),
            "bypass_prevention_score": properly_blocked / total_tests * 100,
            "no_bypass_vulnerabilities": len(bypass_vulnerabilities) == 0,
            "bypass_test_results": bypass_tests,
            "vulnerability_details": bypass_vulnerabilities
        }
    
    async def run_comprehensive_security_test(self) -> Dict:
        """Run all security tests"""
        print("🔒 Starting Comprehensive Admin Security Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all security test suites
            jwt_test = await self.test_jwt_token_generation()
            auth_test = await self.test_admin_endpoints_with_auth()
            no_auth_test = await self.test_admin_endpoints_without_auth()
            invalid_token_test = await self.test_admin_endpoints_with_invalid_token()
            rbac_test = await self.test_role_based_access_control()
            bypass_test = await self.test_security_bypass_prevention()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "jwt_token_generation": jwt_test,
                "admin_endpoints_with_auth": auth_test,
                "admin_endpoints_without_auth": no_auth_test,
                "admin_endpoints_invalid_tokens": invalid_token_test,
                "role_based_access_control": rbac_test,
                "security_bypass_prevention": bypass_test
            }
            
            # Calculate overall security metrics
            security_scores = [
                no_auth_test.get("security_score", 0),
                invalid_token_test.get("token_security_score", 0),
                rbac_test.get("rbac_security_score", 0),
                bypass_test.get("bypass_prevention_score", 0)
            ]
            
            overall_security_score = sum(security_scores) / len(security_scores)
            
            # Critical security checks
            critical_checks = {
                "jwt_tokens_working": jwt_test.get("is_real_jwt", False),
                "admin_endpoints_accessible_with_auth": auth_test.get("all_endpoints_accessible", False),
                "admin_endpoints_blocked_without_auth": no_auth_test.get("all_endpoints_secured", False),
                "invalid_tokens_rejected": invalid_token_test.get("all_invalid_tokens_rejected", False),
                "rbac_working": rbac_test.get("rbac_working_correctly", False),
                "no_bypass_vulnerabilities": bypass_test.get("no_bypass_vulnerabilities", False)
            }
            
            all_critical_passed = all(critical_checks.values())
            
            # Count vulnerabilities
            total_vulnerabilities = (
                no_auth_test.get("vulnerable_endpoints", 0) +
                invalid_token_test.get("vulnerable_tokens", 0) +
                rbac_test.get("vulnerable_endpoints", 0) +
                bypass_test.get("bypass_vulnerabilities", 0)
            )
            
            all_results["security_summary"] = {
                "overall_security_score": overall_security_score,
                "all_critical_checks_passed": all_critical_passed,
                "total_vulnerabilities_found": total_vulnerabilities,
                "security_level": "SECURE" if all_critical_passed and total_vulnerabilities == 0 else "VULNERABLE",
                "critical_security_checks": critical_checks,
                "individual_scores": {
                    "authentication_required_score": no_auth_test.get("security_score", 0),
                    "token_validation_score": invalid_token_test.get("token_security_score", 0),
                    "role_based_access_score": rbac_test.get("rbac_security_score", 0),
                    "bypass_prevention_score": bypass_test.get("bypass_prevention_score", 0)
                }
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Run the comprehensive admin security test"""
    tester = AdminSecurityTester()
    results = await tester.run_comprehensive_security_test()
    
    # Print summary
    print("\n" + "="*70)
    print("🔒 ADMIN SECURITY TEST SUMMARY")
    print("="*70)
    
    summary = results["security_summary"]
    print(f"Overall Security Score: {summary['overall_security_score']:.1f}%")
    print(f"Security Level: {summary['security_level']}")
    print(f"Total Vulnerabilities: {summary['total_vulnerabilities_found']}")
    print(f"All Critical Checks Passed: {'✅' if summary['all_critical_checks_passed'] else '❌'}")
    
    print("\nCritical Security Checks:")
    for check, passed in summary["critical_security_checks"].items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check.replace('_', ' ').title()}")
    
    print("\nIndividual Scores:")
    for score_name, score in summary["individual_scores"].items():
        print(f"  {score_name.replace('_', ' ').title()}: {score:.1f}%")
    
    # Save detailed results
    with open("/app/admin_security_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: /app/admin_security_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())