#!/usr/bin/env python3
"""
SECURITY TESTING - Verify authentication is working properly
Testing that admin endpoints properly reject unauthorized access
"""

import asyncio
import aiohttp
import time
from datetime import datetime

BACKEND_URL = "https://mobileui-sync.preview.emergentagent.com/api"

async def test_admin_endpoints_security():
    """Test that admin endpoints properly reject unauthorized access"""
    print("🔒 Testing Admin Endpoints Security...")
    
    async with aiohttp.ClientSession() as session:
        # Test admin endpoints without authentication
        admin_endpoints = [
            {"method": "POST", "endpoint": "/admin/users", "name": "Create User"},
            {"method": "PUT", "endpoint": "/admin/users/test-id", "name": "Update User"},
            {"method": "PUT", "endpoint": "/admin/users/test-id/approve", "name": "Approve User"},
            {"method": "PUT", "endpoint": "/admin/users/test-id/reject", "name": "Reject User"},
            {"method": "PUT", "endpoint": "/admin/users/test-id/suspend", "name": "Suspend User"},
            {"method": "PUT", "endpoint": "/admin/users/test-id/activate", "name": "Activate User"},
            {"method": "DELETE", "endpoint": "/admin/users/test-id", "name": "Delete User"},
            {"method": "GET", "endpoint": "/admin/performance", "name": "Performance Metrics"}
        ]
        
        security_results = []
        
        for endpoint_test in admin_endpoints:
            try:
                async with session.request(
                    endpoint_test["method"], 
                    f"{BACKEND_URL}{endpoint_test['endpoint']}"
                ) as response:
                    status = response.status
                    
                    # Admin endpoints should return 401 (Unauthorized) or 403 (Forbidden) without auth
                    is_secure = status in [401, 403]
                    
                    result = {
                        "name": endpoint_test["name"],
                        "endpoint": endpoint_test["endpoint"],
                        "method": endpoint_test["method"],
                        "status": status,
                        "secure": is_secure
                    }
                    
                    security_results.append(result)
                    
                    if is_secure:
                        print(f"  ✅ {endpoint_test['name']}: Properly secured (Status {status})")
                    else:
                        print(f"  ❌ {endpoint_test['name']}: Security issue (Status {status})")
                        
            except Exception as e:
                print(f"  ❌ {endpoint_test['name']}: Error testing - {str(e)}")
        
        # Summary
        secure_endpoints = sum(1 for r in security_results if r["secure"])
        total_endpoints = len(security_results)
        security_rate = (secure_endpoints / total_endpoints) * 100 if total_endpoints > 0 else 0
        
        print(f"\n🔒 Security Summary:")
        print(f"  Secure Endpoints: {secure_endpoints}/{total_endpoints}")
        print(f"  Security Rate: {security_rate:.1f}%")
        
        return security_rate >= 100  # All endpoints should be secure

if __name__ == "__main__":
    result = asyncio.run(test_admin_endpoints_security())
    print(f"\n🏁 Security Test {'PASSED' if result else 'FAILED'}")