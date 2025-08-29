#!/usr/bin/env python3
"""
Catalyst Database System CORS Fix Verification Test
Testing backend endpoints after CORS configuration fix for frontend URL.
"""

import requests
import json
import sys
from datetime import datetime

# Use the frontend URL from .env file
BASE_URL = "https://cataloro-hub.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class CatalystDatabaseTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Basic API Connectivity", 
                    True, 
                    f"API accessible: {data.get('message', 'Unknown')}"
                )
                return True
            else:
                self.log_result(
                    "Basic API Connectivity", 
                    False, 
                    f"API not accessible: HTTP {response.status_code}",
                    {"response": response.text}
                )
                return False
        except Exception as e:
            self.log_result(
                "Basic API Connectivity", 
                False, 
                f"Connection failed: {str(e)}"
            )
            return False
    
    def test_cors_headers(self):
        """Test CORS headers for frontend URL"""
        try:
            # Test OPTIONS preflight request
            headers = {
                'Origin': 'https://cataloro-hub.preview.emergentagent.com',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            }
            
            response = self.session.options(f"{BASE_URL}/admin/catalyst-data", headers=headers)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            origin_allowed = cors_headers['Access-Control-Allow-Origin'] == 'https://cataloro-hub.preview.emergentagent.com'
            
            self.log_result(
                "CORS Headers Configuration",
                origin_allowed,
                f"Frontend URL allowed: {origin_allowed}",
                {"cors_headers": cors_headers, "status_code": response.status_code}
            )
            
            return origin_allowed
            
        except Exception as e:
            self.log_result(
                "CORS Headers Configuration",
                False,
                f"CORS test failed: {str(e)}"
            )
            return False
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                user_info = data.get("user", {})
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Login successful for {user_info.get('full_name', 'Admin')}",
                    {
                        "user_id": user_info.get("id"),
                        "role": user_info.get("role"),
                        "token_length": len(self.admin_token) if self.admin_token else 0
                    }
                )
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}",
                    "Content-Type": "application/json"
                })
                
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"Login failed: HTTP {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False
    
    def test_catalyst_basis_endpoints(self):
        """Test catalyst basis data endpoints"""
        try:
            # Test GET /admin/catalyst-basis
            response = self.session.get(f"{BASE_URL}/admin/catalyst-basis")
            
            if response.status_code == 200:
                basis_data = response.json()
                self.log_result(
                    "GET Catalyst Basis Data",
                    True,
                    "Basis data retrieved successfully",
                    {
                        "pt_price": basis_data.get("pt_price"),
                        "pd_price": basis_data.get("pd_price"),
                        "rh_price": basis_data.get("rh_price"),
                        "exchange_rate": basis_data.get("exchange_rate")
                    }
                )
                
                # Test POST /admin/catalyst-basis (update basis data)
                updated_basis = {
                    "pt_price": 1000.0,
                    "pd_price": 1300.0,
                    "rh_price": 5000.0,
                    "exchange_rate": 0.95,
                    "pt_renumeration": 85.0,
                    "pd_renumeration": 80.0,
                    "rh_renumeration": 75.0
                }
                
                post_response = self.session.post(f"{BASE_URL}/admin/catalyst-basis", json=updated_basis)
                
                if post_response.status_code in [200, 201]:
                    self.log_result(
                        "POST Catalyst Basis Data",
                        True,
                        "Basis data updated successfully",
                        {"updated_data": updated_basis}
                    )
                    return True
                else:
                    self.log_result(
                        "POST Catalyst Basis Data",
                        False,
                        f"Failed to update basis data: HTTP {post_response.status_code}",
                        {"response": post_response.text}
                    )
                    return False
            else:
                self.log_result(
                    "GET Catalyst Basis Data",
                    False,
                    f"Failed to retrieve basis data: HTTP {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Catalyst Basis Endpoints",
                False,
                f"Basis endpoints test failed: {str(e)}"
            )
            return False
    
    def test_catalyst_data_endpoints(self):
        """Test catalyst data CRUD endpoints"""
        try:
            # Test GET /admin/catalyst-data (initially empty)
            response = self.session.get(f"{BASE_URL}/admin/catalyst-data")
            
            if response.status_code == 200:
                initial_data = response.json()
                self.log_result(
                    "GET Catalyst Data",
                    True,
                    f"Retrieved {len(initial_data)} catalyst items",
                    {"item_count": len(initial_data)}
                )
                
                # Test POST /admin/catalyst-data (bulk upload)
                test_catalyst_data = [
                    {
                        "cat_id": "CAT001",
                        "pt_ppm": 1500.0,
                        "pd_ppm": 800.0,
                        "rh_ppm": 200.0,
                        "ceramic_weight": 2.5,
                        "add_info": "Test catalyst 1",
                        "name": "Test Catalyst Alpha"
                    },
                    {
                        "cat_id": "CAT002", 
                        "pt_ppm": 2000.0,
                        "pd_ppm": 1200.0,
                        "rh_ppm": 300.0,
                        "ceramic_weight": 3.0,
                        "add_info": "Test catalyst 2",
                        "name": "Test Catalyst Beta"
                    },
                    {
                        "cat_id": "CAT003",
                        "pt_ppm": 1800.0,
                        "pd_ppm": 900.0,
                        "rh_ppm": 250.0,
                        "ceramic_weight": 2.8,
                        "add_info": "Test catalyst 3", 
                        "name": "Test Catalyst Gamma"
                    }
                ]
                
                bulk_data = {"catalyst_data": test_catalyst_data}
                post_response = self.session.post(f"{BASE_URL}/admin/catalyst-data", json=bulk_data)
                
                if post_response.status_code in [200, 201]:
                    post_result = post_response.json()
                    self.log_result(
                        "POST Catalyst Data (Bulk Upload)",
                        True,
                        f"Bulk upload successful: {post_result.get('message', 'Data saved')}",
                        {"items_uploaded": len(test_catalyst_data)}
                    )
                    
                    # Verify data was saved by getting it again
                    verify_response = self.session.get(f"{BASE_URL}/admin/catalyst-data")
                    if verify_response.status_code == 200:
                        saved_data = verify_response.json()
                        if len(saved_data) >= len(test_catalyst_data):
                            self.log_result(
                                "Verify Catalyst Data Persistence",
                                True,
                                f"Data persisted correctly: {len(saved_data)} items found",
                                {"saved_items": len(saved_data)}
                            )
                            
                            # Test individual item operations if we have data
                            if saved_data:
                                return self.test_individual_catalyst_operations(saved_data[0])
                            return True
                        else:
                            self.log_result(
                                "Verify Catalyst Data Persistence",
                                False,
                                f"Data not persisted correctly: expected >= {len(test_catalyst_data)}, got {len(saved_data)}"
                            )
                            return False
                    else:
                        self.log_result(
                            "Verify Catalyst Data Persistence",
                            False,
                            f"Failed to verify data: HTTP {verify_response.status_code}"
                        )
                        return False
                else:
                    self.log_result(
                        "POST Catalyst Data (Bulk Upload)",
                        False,
                        f"Bulk upload failed: HTTP {post_response.status_code}",
                        {"response": post_response.text}
                    )
                    return False
            else:
                self.log_result(
                    "GET Catalyst Data",
                    False,
                    f"Failed to retrieve catalyst data: HTTP {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Catalyst Data Endpoints",
                False,
                f"Data endpoints test failed: {str(e)}"
            )
            return False
    
    def test_individual_catalyst_operations(self, test_item):
        """Test individual catalyst item operations (PUT/DELETE)"""
        try:
            item_id = test_item.get("id")
            if not item_id:
                self.log_result(
                    "Individual Catalyst Operations",
                    False,
                    "No item ID found for individual operations"
                )
                return False
            
            # Test PUT /admin/catalyst-data/{item_id}
            updated_item = {
                "cat_id": test_item.get("cat_id"),
                "pt_ppm": 2500.0,  # Updated value
                "pd_ppm": test_item.get("pd_ppm"),
                "rh_ppm": test_item.get("rh_ppm"),
                "ceramic_weight": test_item.get("ceramic_weight"),
                "add_info": "Updated test catalyst",
                "name": test_item.get("name") + " (Updated)"
            }
            
            put_response = self.session.put(f"{BASE_URL}/admin/catalyst-data/{item_id}", json=updated_item)
            
            if put_response.status_code in [200, 204]:
                self.log_result(
                    "PUT Catalyst Data (Update Item)",
                    True,
                    f"Item {item_id} updated successfully",
                    {"updated_pt_ppm": updated_item["pt_ppm"]}
                )
                
                # Test DELETE /admin/catalyst-data/{item_id}
                delete_response = self.session.delete(f"{BASE_URL}/admin/catalyst-data/{item_id}")
                
                if delete_response.status_code in [200, 204]:
                    self.log_result(
                        "DELETE Catalyst Data (Remove Item)",
                        True,
                        f"Item {item_id} deleted successfully"
                    )
                    return True
                else:
                    self.log_result(
                        "DELETE Catalyst Data (Remove Item)",
                        False,
                        f"Failed to delete item: HTTP {delete_response.status_code}",
                        {"response": delete_response.text}
                    )
                    return False
            else:
                self.log_result(
                    "PUT Catalyst Data (Update Item)",
                    False,
                    f"Failed to update item: HTTP {put_response.status_code}",
                    {"response": put_response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Individual Catalyst Operations",
                False,
                f"Individual operations test failed: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all catalyst database tests"""
        print("🧪 CATALYST DATABASE SYSTEM CORS FIX VERIFICATION")
        print("=" * 60)
        print(f"Testing against: {BASE_URL}")
        print(f"Frontend URL: https://cataloro-hub.preview.emergentagent.com")
        print("=" * 60)
        
        # Test sequence
        tests_passed = 0
        total_tests = 0
        
        # 1. Basic connectivity
        total_tests += 1
        if self.test_basic_connectivity():
            tests_passed += 1
        
        # 2. CORS headers
        total_tests += 1
        if self.test_cors_headers():
            tests_passed += 1
        
        # 3. Admin authentication
        total_tests += 1
        if self.authenticate_admin():
            tests_passed += 1
            
            # 4. Catalyst basis endpoints (only if authenticated)
            total_tests += 1
            if self.test_catalyst_basis_endpoints():
                tests_passed += 1
            
            # 5. Catalyst data endpoints (only if authenticated)
            total_tests += 1
            if self.test_catalyst_data_endpoints():
                tests_passed += 1
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Tests Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        
        if tests_passed == total_tests:
            print("🎉 ALL TESTS PASSED - Catalyst Database System is working correctly!")
            print("✅ CORS configuration fix successful")
            print("✅ Admin authentication working")
            print("✅ All 6 catalyst endpoints operational")
        else:
            print("⚠️  SOME TESTS FAILED - Issues detected:")
            failed_tests = [r for r in self.test_results if "❌ FAIL" in r["status"]]
            for failed in failed_tests:
                print(f"   - {failed['test']}: {failed['message']}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"   {result['status']}: {result['test']}")
        
        return tests_passed == total_tests

if __name__ == "__main__":
    tester = CatalystDatabaseTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)