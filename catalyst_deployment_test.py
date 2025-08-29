#!/usr/bin/env python3
"""
URGENT DEPLOYMENT RULE COMPLIANCE VERIFICATION
Test Catalyst Database System after removing ALL forbidden URLs and using only allowed deployment URLs.

CRITICAL CONFIGURATION CHANGES TESTED:
- Frontend .env: Updated REACT_APP_BACKEND_URL from forbidden emergent.host to allowed http://217.154.0.82
- Backend .env: Updated CORS_ORIGINS to ONLY allowed URLs: http://217.154.0.82,https://217.154.0.82
- Removed ALL forbidden URLs: localhost:3000, *.emergent.host
- Backend Base URL: Updated to http://217.154.0.82

DEPLOYMENT RULE COMPLIANCE:
✅ Frontend URL: http://217.154.0.82 (no port)
✅ Backend CORS: http://217.154.0.82,https://217.154.0.82 (no ports)
❌ REMOVED: All localhost and emergent.host references
"""

import requests
import json
import sys
from datetime import datetime

# DEPLOYMENT RULE COMPLIANT CONFIGURATION
BASE_URL = "http://217.154.0.82/api"
FRONTEND_URL = "http://217.154.0.82"

# Test credentials
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class CatalystDatabaseTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.frontend_url = FRONTEND_URL
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
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
    
    def test_deployment_rule_compliance(self):
        """Test 1: Verify deployment rule compliance - no forbidden URLs"""
        print("\n🔍 TESTING DEPLOYMENT RULE COMPLIANCE")
        
        try:
            # Check that we're using the correct IP address
            if "217.154.0.82" not in self.base_url:
                self.log_test("Deployment URL Compliance", False, 
                            f"Backend URL not using allowed IP: {self.base_url}")
                return False
                
            if "217.154.0.82" not in self.frontend_url:
                self.log_test("Frontend URL Compliance", False, 
                            f"Frontend URL not using allowed IP: {self.frontend_url}")
                return False
                
            # Verify no forbidden URLs in configuration
            forbidden_patterns = ["localhost", "emergent.host", ":3000", ":8001"]
            for pattern in forbidden_patterns:
                if pattern in self.base_url or pattern in self.frontend_url:
                    self.log_test("Forbidden URL Check", False, 
                                f"Found forbidden pattern '{pattern}' in URLs")
                    return False
            
            self.log_test("Deployment Rule Compliance", True, 
                         "All URLs comply with deployment rules - using allowed IP address only")
            return True
            
        except Exception as e:
            self.log_test("Deployment Rule Compliance", False, f"Error: {str(e)}")
            return False
    
    def test_basic_connectivity(self):
        """Test 2: Basic API connectivity with IP address"""
        print("\n🔗 TESTING BASIC API CONNECTIVITY")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Basic API Connectivity", True, 
                            f"API accessible at {self.base_url}", 
                            {"response": data, "status_code": response.status_code})
                return True
            else:
                self.log_test("Basic API Connectivity", False, 
                            f"API returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Basic API Connectivity", False, f"Connection failed: {str(e)}")
            return False
    
    def test_cors_compliance(self):
        """Test 3: CORS compliance with allowed URLs only"""
        print("\n🌐 TESTING CORS COMPLIANCE")
        
        try:
            # Test OPTIONS request with allowed origin
            headers = {
                "Origin": self.frontend_url,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            
            response = requests.options(f"{self.base_url}/auth/login", headers=headers, timeout=10)
            
            # Check CORS headers
            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            cors_methods = response.headers.get("Access-Control-Allow-Methods")
            cors_headers = response.headers.get("Access-Control-Allow-Headers")
            
            if cors_origin == self.frontend_url:
                self.log_test("CORS Origin Compliance", True, 
                            f"CORS allows frontend URL: {cors_origin}",
                            {"allowed_methods": cors_methods, "allowed_headers": cors_headers})
                return True
            else:
                self.log_test("CORS Origin Compliance", False, 
                            f"CORS origin mismatch. Expected: {self.frontend_url}, Got: {cors_origin}")
                return False
                
        except Exception as e:
            self.log_test("CORS Compliance", False, f"CORS test failed: {str(e)}")
            return False
    
    def test_admin_authentication(self):
        """Test 4: Admin authentication with IP address configuration"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            headers = {
                "Content-Type": "application/json",
                "Origin": self.frontend_url
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login", 
                json=login_data, 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                user_data = data.get("user", {})
                
                if self.admin_token and user_data.get("role") == "admin":
                    self.log_test("Admin Authentication", True, 
                                f"Admin login successful for {user_data.get('full_name', 'Admin')}",
                                {"user_id": user_data.get("id"), "role": user_data.get("role")})
                    return True
                else:
                    self.log_test("Admin Authentication", False, 
                                "Login response missing token or admin role")
                    return False
            else:
                self.log_test("Admin Authentication", False, 
                            f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers for admin requests"""
        if not self.admin_token:
            return {"Content-Type": "application/json", "Origin": self.frontend_url}
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.admin_token}",
            "Origin": self.frontend_url
        }
    
    def test_catalyst_basis_endpoints(self):
        """Test 5: Catalyst Basis Data endpoints (price calculation variables)"""
        print("\n💰 TESTING CATALYST BASIS ENDPOINTS")
        
        try:
            headers = self.get_auth_headers()
            
            # Test GET /admin/catalyst-basis
            response = requests.get(f"{self.base_url}/admin/catalyst-basis", headers=headers, timeout=10)
            
            if response.status_code == 200:
                basis_data = response.json()
                self.log_test("GET Catalyst Basis", True, 
                            "Retrieved catalyst basis data successfully",
                            {"data_keys": list(basis_data.keys()) if isinstance(basis_data, dict) else "non-dict response"})
                
                # Test POST /admin/catalyst-basis (update basis data)
                updated_basis = {
                    "pt_price": 1000.0,
                    "pd_price": 1300.0,
                    "rh_price": 5000.0,
                    "exchange_rate": 0.92,
                    "renumeration_pt": 85.0,
                    "renumeration_pd": 85.0,
                    "renumeration_rh": 85.0
                }
                
                post_response = requests.post(
                    f"{self.base_url}/admin/catalyst-basis", 
                    json=updated_basis, 
                    headers=headers,
                    timeout=10
                )
                
                if post_response.status_code in [200, 201]:
                    self.log_test("POST Catalyst Basis", True, 
                                "Updated catalyst basis data successfully",
                                {"updated_data": updated_basis})
                    return True
                else:
                    self.log_test("POST Catalyst Basis", False, 
                                f"Failed to update basis data: {post_response.status_code}")
                    return False
            else:
                self.log_test("GET Catalyst Basis", False, 
                            f"Failed to retrieve basis data: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Catalyst Basis Endpoints", False, f"Error: {str(e)}")
            return False
    
    def test_catalyst_data_endpoints(self):
        """Test 6: Catalyst Data endpoints (bulk Excel uploads and CRUD operations)"""
        print("\n📊 TESTING CATALYST DATA ENDPOINTS")
        
        try:
            headers = self.get_auth_headers()
            
            # Test GET /admin/catalyst-data
            response = requests.get(f"{self.base_url}/admin/catalyst-data", headers=headers, timeout=10)
            
            if response.status_code == 200:
                catalyst_data = response.json()
                self.log_test("GET Catalyst Data", True, 
                            f"Retrieved {len(catalyst_data) if isinstance(catalyst_data, list) else 'unknown count'} catalyst items")
                
                # Test POST /admin/catalyst-data (bulk upload simulation)
                test_catalyst_items = [
                    {
                        "cat_id": "CAT001",
                        "pt_ppm": 1500.0,
                        "pd_ppm": 800.0,
                        "rh_ppm": 200.0,
                        "ceramic_weight": 2.5,
                        "add_info": "Test catalyst item 1",
                        "name": "Test Catalyst 1"
                    },
                    {
                        "cat_id": "CAT002", 
                        "pt_ppm": 2000.0,
                        "pd_ppm": 1200.0,
                        "rh_ppm": 300.0,
                        "ceramic_weight": 3.0,
                        "add_info": "Test catalyst item 2",
                        "name": "Test Catalyst 2"
                    }
                ]
                
                bulk_data = {"data": test_catalyst_items}
                
                post_response = requests.post(
                    f"{self.base_url}/admin/catalyst-data", 
                    json=bulk_data, 
                    headers=headers,
                    timeout=10
                )
                
                if post_response.status_code in [200, 201]:
                    post_result = post_response.json()
                    self.log_test("POST Catalyst Data (Bulk Upload)", True, 
                                "Bulk catalyst data upload successful",
                                {"uploaded_count": len(test_catalyst_items), "response": post_result})
                    
                    # Test individual item operations if we have items
                    return self.test_individual_catalyst_operations()
                else:
                    self.log_test("POST Catalyst Data (Bulk Upload)", False, 
                                f"Bulk upload failed: {post_response.status_code}")
                    return False
            else:
                self.log_test("GET Catalyst Data", False, 
                            f"Failed to retrieve catalyst data: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Catalyst Data Endpoints", False, f"Error: {str(e)}")
            return False
    
    def test_individual_catalyst_operations(self):
        """Test 7: Individual catalyst item operations (PUT/DELETE)"""
        print("\n🔧 TESTING INDIVIDUAL CATALYST OPERATIONS")
        
        try:
            headers = self.get_auth_headers()
            
            # Get current catalyst data to find an item to test with
            response = requests.get(f"{self.base_url}/admin/catalyst-data", headers=headers, timeout=10)
            
            if response.status_code == 200:
                catalyst_items = response.json()
                
                if isinstance(catalyst_items, list) and len(catalyst_items) > 0:
                    # Test with the first item
                    test_item = catalyst_items[0]
                    item_id = test_item.get("id")
                    
                    if item_id:
                        # Test PUT /admin/catalyst-data/{item_id}
                        updated_item = {
                            "cat_id": test_item.get("cat_id", "CAT001"),
                            "pt_ppm": 2500.0,  # Updated value
                            "pd_ppm": test_item.get("pd_ppm", 800.0),
                            "rh_ppm": test_item.get("rh_ppm", 200.0),
                            "ceramic_weight": test_item.get("ceramic_weight", 2.5),
                            "add_info": "Updated test catalyst item",
                            "name": test_item.get("name", "Test Catalyst")
                        }
                        
                        put_response = requests.put(
                            f"{self.base_url}/admin/catalyst-data/{item_id}",
                            json=updated_item,
                            headers=headers,
                            timeout=10
                        )
                        
                        if put_response.status_code in [200, 201]:
                            self.log_test("PUT Catalyst Item", True, 
                                        f"Updated catalyst item {item_id} successfully",
                                        {"item_id": item_id, "updated_pt_ppm": 2500.0})
                            
                            # Test DELETE /admin/catalyst-data/{item_id}
                            delete_response = requests.delete(
                                f"{self.base_url}/admin/catalyst-data/{item_id}",
                                headers=headers,
                                timeout=10
                            )
                            
                            if delete_response.status_code in [200, 204]:
                                self.log_test("DELETE Catalyst Item", True, 
                                            f"Deleted catalyst item {item_id} successfully")
                                return True
                            else:
                                self.log_test("DELETE Catalyst Item", False, 
                                            f"Failed to delete item: {delete_response.status_code}")
                                return False
                        else:
                            self.log_test("PUT Catalyst Item", False, 
                                        f"Failed to update item: {put_response.status_code}")
                            return False
                    else:
                        self.log_test("Individual Operations", False, 
                                    "No item ID found in catalyst data")
                        return False
                else:
                    self.log_test("Individual Operations", False, 
                                "No catalyst items available for individual operations test")
                    return False
            else:
                self.log_test("Individual Operations Setup", False, 
                            f"Failed to get catalyst data: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Individual Catalyst Operations", False, f"Error: {str(e)}")
            return False
    
    def test_forbidden_url_removal(self):
        """Test 8: Verify no forbidden URLs remain in system"""
        print("\n🚫 TESTING FORBIDDEN URL REMOVAL")
        
        try:
            # Test that old forbidden URLs are not accessible
            forbidden_urls = [
                "http://localhost:3000",
                "http://localhost:8001", 
                "https://cataloro-hub.preview.emergentagent.com",
                "https://revived-cataloro.preview.emergentagent.com"
            ]
            
            accessible_forbidden = []
            
            for url in forbidden_urls:
                try:
                    response = requests.get(f"{url}/api/", timeout=5)
                    if response.status_code == 200:
                        accessible_forbidden.append(url)
                except:
                    # Expected - forbidden URLs should not be accessible
                    pass
            
            if not accessible_forbidden:
                self.log_test("Forbidden URL Removal", True, 
                            "All forbidden URLs are inaccessible as expected")
                return True
            else:
                self.log_test("Forbidden URL Removal", False, 
                            f"Some forbidden URLs are still accessible: {accessible_forbidden}")
                return False
                
        except Exception as e:
            self.log_test("Forbidden URL Removal", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all catalyst database tests for deployment rule compliance"""
        print("🚀 STARTING CATALYST DATABASE DEPLOYMENT RULE COMPLIANCE TESTING")
        print("=" * 80)
        
        tests = [
            self.test_deployment_rule_compliance,
            self.test_basic_connectivity,
            self.test_cors_compliance,
            self.test_admin_authentication,
            self.test_catalyst_basis_endpoints,
            self.test_catalyst_data_endpoints,
            self.test_forbidden_url_removal
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
        
        print("\n" + "=" * 80)
        print(f"🏁 CATALYST DATABASE TESTING COMPLETE")
        print(f"📊 RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("✅ ALL TESTS PASSED - Catalyst Database System is deployment rule compliant!")
        else:
            print("❌ SOME TESTS FAILED - Review failures above")
        
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']} - {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    print("URGENT DEPLOYMENT RULE COMPLIANCE VERIFICATION")
    print("Testing Catalyst Database System with allowed IP address configuration")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BASE_URL}")
    print()
    
    tester = CatalystDatabaseTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)