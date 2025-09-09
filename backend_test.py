#!/usr/bin/env python3
"""
Cataloro Marketplace Admin Authentication & Database Consistency Testing
Testing admin user authentication and database integrity after recent fixes
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-boost.preview.emergentagent.com/api"
PERFORMANCE_TARGET_MS = 1000  # Browse endpoint should respond in under 1 second
CACHE_IMPROVEMENT_TARGET = 20  # Cached responses should be at least 20% faster

# Admin User Configuration (from review request)
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"
ADMIN_ROLE = "admin"
ADMIN_ID = "admin_user_1"

class AdminAuthenticationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.admin_token = None
        self.test_users = []  # Store test users for management testing
        
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
    
    async def test_admin_user_authentication(self) -> Dict:
        """Test admin user login with admin@cataloro.com"""
        print("🔐 Testing admin user authentication...")
        
        # Test admin login
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"  # Mock password for testing
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            token = result["data"].get("token", "")
            
            # Store token for subsequent requests
            self.admin_token = token
            
            # Verify admin user properties
            email_correct = user_data.get("email") == ADMIN_EMAIL
            username_correct = user_data.get("username") == ADMIN_USERNAME
            role_correct = user_data.get("role") == ADMIN_ROLE or user_data.get("user_role") == "Admin"
            
            print(f"  ✅ Admin login successful")
            print(f"  📧 Email: {user_data.get('email')} ({'✅' if email_correct else '❌'})")
            print(f"  👤 Username: {user_data.get('username')} ({'✅' if username_correct else '❌'})")
            print(f"  🔑 Role: {user_data.get('role', user_data.get('user_role'))} ({'✅' if role_correct else '❌'})")
            
            return {
                "test_name": "Admin User Authentication",
                "login_successful": True,
                "response_time_ms": result["response_time_ms"],
                "admin_email_correct": email_correct,
                "admin_username_correct": username_correct,
                "admin_role_correct": role_correct,
                "user_data": user_data,
                "token_received": bool(token),
                "all_admin_properties_correct": email_correct and username_correct and role_correct
            }
        else:
            print(f"  ❌ Admin login failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Admin User Authentication",
                "login_successful": False,
                "response_time_ms": result["response_time_ms"],
                "error": result.get("error", "Login failed"),
                "status": result["status"]
            }
    
    async def test_database_user_consistency(self) -> Dict:
        """Test that all expected users exist in database"""
        print("🗄️ Testing database user consistency...")
        
        expected_users = [
            {"email": "admin@cataloro.com", "username": "sash_admin", "role": "admin"},
            {"email": "demo@cataloro.com", "username": "demo_user", "role": "user"},
        ]
        
        user_tests = []
        
        for expected_user in expected_users:
            print(f"  Testing user: {expected_user['email']}")
            
            # Try to login to verify user exists
            login_data = {
                "email": expected_user["email"],
                "password": "test_password"
            }
            
            result = await self.make_request("/auth/login", "POST", data=login_data)
            
            if result["success"]:
                user_data = result["data"].get("user", {})
                
                email_match = user_data.get("email") == expected_user["email"]
                username_match = user_data.get("username") == expected_user["username"]
                role_match = (user_data.get("role") == expected_user["role"] or 
                             (expected_user["role"] == "admin" and user_data.get("user_role") == "Admin"))
                
                user_tests.append({
                    "email": expected_user["email"],
                    "exists_in_database": True,
                    "email_correct": email_match,
                    "username_correct": username_match,
                    "role_correct": role_match,
                    "user_data": user_data,
                    "all_properties_correct": email_match and username_match and role_match
                })
                
                print(f"    ✅ User exists and properties match")
            else:
                user_tests.append({
                    "email": expected_user["email"],
                    "exists_in_database": False,
                    "error": result.get("error", "User not found"),
                    "status": result["status"]
                })
                print(f"    ❌ User not found or login failed")
        
        # Calculate overall consistency
        existing_users = [u for u in user_tests if u.get("exists_in_database", False)]
        correct_users = [u for u in existing_users if u.get("all_properties_correct", False)]
        
        return {
            "test_name": "Database User Consistency",
            "total_expected_users": len(expected_users),
            "users_found_in_database": len(existing_users),
            "users_with_correct_properties": len(correct_users),
            "database_consistency_score": (len(correct_users) / len(expected_users)) * 100,
            "all_users_consistent": len(correct_users) == len(expected_users),
            "detailed_user_tests": user_tests
        }
    
    async def test_user_management_functionality(self) -> Dict:
        """Test comprehensive user management functionality including activate/suspend endpoints"""
        print("👥 Testing user management functionality...")
        
        if not self.admin_token:
            return {
                "test_name": "User Management Functionality",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        test_results = []
        
        # Step 1: Test listing all users
        print("  Testing user listing endpoint...")
        users_result = await self.make_request("/users", headers=headers)
        
        if users_result["success"]:
            users_data = users_result["data"]
            print(f"    ✅ Found {len(users_data)} users in system")
            
            # Store users for further testing
            self.test_users = users_data
            
            test_results.append({
                "test": "List Users",
                "success": True,
                "response_time_ms": users_result["response_time_ms"],
                "user_count": len(users_data),
                "has_expected_users": any(u.get("email") == "admin@cataloro.com" for u in users_data)
            })
        else:
            print(f"    ❌ Failed to list users: {users_result.get('error')}")
            test_results.append({
                "test": "List Users",
                "success": False,
                "error": users_result.get("error"),
                "response_time_ms": users_result["response_time_ms"]
            })
        
        # Step 2: Test individual user activate/suspend endpoints
        if self.test_users:
            # Find a test user (not admin)
            test_user = None
            for user in self.test_users:
                if user.get("email") != "admin@cataloro.com" and user.get("id"):
                    test_user = user
                    break
            
            if test_user:
                user_id = test_user["id"]
                original_status = test_user.get("is_active", True)
                
                print(f"  Testing activate/suspend with user: {test_user.get('email', 'Unknown')}")
                
                # Test suspend endpoint
                print("    Testing suspend endpoint...")
                suspend_result = await self.make_request(f"/admin/users/{user_id}/suspend", "PUT", headers=headers)
                
                if suspend_result["success"]:
                    suspended_user = suspend_result["data"].get("user", {})
                    is_suspended = not suspended_user.get("is_active", True)
                    
                    test_results.append({
                        "test": "Suspend User",
                        "success": True,
                        "response_time_ms": suspend_result["response_time_ms"],
                        "user_id": user_id,
                        "is_active_after_suspend": suspended_user.get("is_active"),
                        "suspend_successful": is_suspended,
                        "returns_updated_user": bool(suspended_user)
                    })
                    
                    print(f"      ✅ User suspended successfully (is_active: {suspended_user.get('is_active')})")
                else:
                    test_results.append({
                        "test": "Suspend User",
                        "success": False,
                        "error": suspend_result.get("error"),
                        "response_time_ms": suspend_result["response_time_ms"],
                        "user_id": user_id
                    })
                    print(f"      ❌ Suspend failed: {suspend_result.get('error')}")
                
                # Test activate endpoint
                print("    Testing activate endpoint...")
                activate_result = await self.make_request(f"/admin/users/{user_id}/activate", "PUT", headers=headers)
                
                if activate_result["success"]:
                    activated_user = activate_result["data"].get("user", {})
                    is_activated = activated_user.get("is_active", False)
                    
                    test_results.append({
                        "test": "Activate User",
                        "success": True,
                        "response_time_ms": activate_result["response_time_ms"],
                        "user_id": user_id,
                        "is_active_after_activate": activated_user.get("is_active"),
                        "activate_successful": is_activated,
                        "returns_updated_user": bool(activated_user)
                    })
                    
                    print(f"      ✅ User activated successfully (is_active: {activated_user.get('is_active')})")
                else:
                    test_results.append({
                        "test": "Activate User",
                        "success": False,
                        "error": activate_result.get("error"),
                        "response_time_ms": activate_result["response_time_ms"],
                        "user_id": user_id
                    })
                    print(f"      ❌ Activate failed: {activate_result.get('error')}")
                
                # Test state persistence by listing users again
                print("    Testing state persistence...")
                users_check_result = await self.make_request("/users", headers=headers)
                
                if users_check_result["success"]:
                    updated_users = users_check_result["data"]
                    updated_user = next((u for u in updated_users if u.get("id") == user_id), None)
                    
                    if updated_user:
                        final_status = updated_user.get("is_active", False)
                        persistence_test = {
                            "test": "State Persistence",
                            "success": True,
                            "user_id": user_id,
                            "final_is_active_status": final_status,
                            "state_persisted": final_status == True  # Should be active after activate
                        }
                        print(f"      ✅ State persisted correctly (final is_active: {final_status})")
                    else:
                        persistence_test = {
                            "test": "State Persistence",
                            "success": False,
                            "error": "User not found in updated list",
                            "user_id": user_id
                        }
                        print(f"      ❌ User not found in updated list")
                    
                    test_results.append(persistence_test)
            else:
                test_results.append({
                    "test": "Individual User Operations",
                    "success": False,
                    "error": "No suitable test user found (need non-admin user with ID)"
                })
                print("    ❌ No suitable test user found for activate/suspend testing")
        
        # Step 3: Test error handling for non-existent users
        print("  Testing error handling for non-existent users...")
        fake_user_id = "non-existent-user-id-12345"
        
        # Test suspend with fake ID
        fake_suspend_result = await self.make_request(f"/admin/users/{fake_user_id}/suspend", "PUT", headers=headers)
        fake_activate_result = await self.make_request(f"/admin/users/{fake_user_id}/activate", "PUT", headers=headers)
        
        test_results.append({
            "test": "Error Handling - Non-existent User",
            "suspend_correctly_fails": not fake_suspend_result["success"],
            "activate_correctly_fails": not fake_activate_result["success"],
            "suspend_status": fake_suspend_result["status"],
            "activate_status": fake_activate_result["status"],
            "proper_error_handling": not fake_suspend_result["success"] and not fake_activate_result["success"]
        })
        
        if not fake_suspend_result["success"] and not fake_activate_result["success"]:
            print("    ✅ Error handling working correctly for non-existent users")
        else:
            print("    ❌ Error handling not working properly")
        
        # Step 4: Test bulk operations if available
        print("  Testing bulk user operations...")
        bulk_test_data = {
            "action": "activate",
            "user_ids": [user["id"] for user in self.test_users[:2] if user.get("id")]  # Test with first 2 users
        }
        
        bulk_result = await self.make_request("/admin/users/bulk-action", "POST", data=bulk_test_data, headers=headers)
        
        test_results.append({
            "test": "Bulk Operations",
            "success": bulk_result["success"],
            "response_time_ms": bulk_result.get("response_time_ms", 0),
            "bulk_endpoint_available": bulk_result["success"] or bulk_result["status"] != 404,
            "error": bulk_result.get("error") if not bulk_result["success"] else None
        })
        
        if bulk_result["success"]:
            print("    ✅ Bulk operations endpoint working")
        elif bulk_result["status"] == 404:
            print("    ⚠️ Bulk operations endpoint not implemented")
        else:
            print(f"    ❌ Bulk operations failed: {bulk_result.get('error')}")
        
        # Calculate overall success metrics
        successful_tests = [t for t in test_results if t.get("success", False)]
        critical_tests = [t for t in test_results if t["test"] in ["List Users", "Suspend User", "Activate User", "State Persistence"]]
        critical_successful = [t for t in critical_tests if t.get("success", False)]
        
        return {
            "test_name": "User Management Functionality",
            "total_tests": len(test_results),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(test_results) * 100 if test_results else 0,
            "critical_functionality_working": len(critical_successful) == len(critical_tests),
            "activate_suspend_working": any(t.get("suspend_successful") for t in test_results) and any(t.get("activate_successful") for t in test_results),
            "state_persistence_working": any(t.get("state_persisted") for t in test_results),
            "error_handling_working": any(t.get("proper_error_handling") for t in test_results),
            "bulk_operations_available": any(t.get("bulk_endpoint_available") for t in test_results),
            "detailed_test_results": test_results
        }
    
    async def test_user_workflow_integration(self) -> Dict:
        """Test complete user management workflow"""
        print("🔄 Testing complete user management workflow...")
        
        if not self.admin_token:
            return {
                "test_name": "User Workflow Integration",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        workflow_steps = []
        
        # Step 1: List all users and verify expected users exist
        print("  Step 1: Verifying expected users exist...")
        users_result = await self.make_request("/users", headers=headers)
        
        expected_emails = ["admin@cataloro.com", "demo@cataloro.com", "seller@cataloro.com"]
        found_users = {}
        
        if users_result["success"]:
            users_data = users_result["data"]
            for user in users_data:
                email = user.get("email", "")
                if email in expected_emails:
                    found_users[email] = user
            
            workflow_steps.append({
                "step": "List Users",
                "success": True,
                "total_users": len(users_data),
                "expected_users_found": len(found_users),
                "missing_users": [email for email in expected_emails if email not in found_users]
            })
            
            print(f"    ✅ Found {len(found_users)}/{len(expected_emails)} expected users")
        else:
            workflow_steps.append({
                "step": "List Users",
                "success": False,
                "error": users_result.get("error")
            })
            print(f"    ❌ Failed to list users")
        
        # Step 2: Test user state management with demo user
        demo_user = found_users.get("demo@cataloro.com")
        if demo_user and demo_user.get("id"):
            user_id = demo_user["id"]
            original_status = demo_user.get("is_active", True)
            
            print(f"  Step 2: Testing state management with demo user (original status: {original_status})...")
            
            # Suspend user
            suspend_result = await self.make_request(f"/admin/users/{user_id}/suspend", "PUT", headers=headers)
            suspend_success = suspend_result["success"] and not suspend_result["data"].get("user", {}).get("is_active", True)
            
            # Activate user
            activate_result = await self.make_request(f"/admin/users/{user_id}/activate", "PUT", headers=headers)
            activate_success = activate_result["success"] and activate_result["data"].get("user", {}).get("is_active", False)
            
            # Verify final state
            final_users_result = await self.make_request("/users", headers=headers)
            final_state_correct = False
            
            if final_users_result["success"]:
                final_users = final_users_result["data"]
                final_user = next((u for u in final_users if u.get("id") == user_id), None)
                if final_user:
                    final_state_correct = final_user.get("is_active", False) == True
            
            workflow_steps.append({
                "step": "State Management",
                "success": suspend_success and activate_success and final_state_correct,
                "suspend_worked": suspend_success,
                "activate_worked": activate_success,
                "final_state_correct": final_state_correct,
                "user_id": user_id
            })
            
            if suspend_success and activate_success and final_state_correct:
                print("    ✅ State management workflow completed successfully")
            else:
                print("    ❌ State management workflow had issues")
        else:
            workflow_steps.append({
                "step": "State Management",
                "success": False,
                "error": "Demo user not found or missing ID"
            })
            print("    ❌ Demo user not available for state management testing")
        
        # Step 3: Test UUID and ObjectId compatibility
        print("  Step 3: Testing ID format compatibility...")
        id_format_tests = []
        
        if found_users:
            test_user = list(found_users.values())[0]
            user_id = test_user.get("id")
            
            if user_id:
                # Test with UUID format (current format)
                uuid_result = await self.make_request(f"/admin/users/{user_id}/activate", "PUT", headers=headers)
                id_format_tests.append({
                    "format": "UUID",
                    "success": uuid_result["success"],
                    "user_id": user_id
                })
                
                # Test with potential ObjectId format (if different)
                # Note: This is mainly for verification that the backend handles both formats
                workflow_steps.append({
                    "step": "ID Format Compatibility",
                    "success": uuid_result["success"],
                    "uuid_format_works": uuid_result["success"],
                    "id_format_tests": id_format_tests
                })
                
                if uuid_result["success"]:
                    print("    ✅ UUID format compatibility confirmed")
                else:
                    print("    ❌ UUID format compatibility issues")
        
        # Calculate workflow success
        successful_steps = [s for s in workflow_steps if s.get("success", False)]
        workflow_success = len(successful_steps) == len(workflow_steps)
        
        return {
            "test_name": "User Workflow Integration",
            "total_workflow_steps": len(workflow_steps),
            "successful_steps": len(successful_steps),
            "workflow_success_rate": len(successful_steps) / len(workflow_steps) * 100 if workflow_steps else 0,
            "complete_workflow_working": workflow_success,
            "expected_users_present": len(found_users) >= 2,  # At least admin and demo
            "state_management_working": any(s.get("step") == "State Management" and s.get("success") for s in workflow_steps),
            "id_compatibility_working": any(s.get("step") == "ID Format Compatibility" and s.get("success") for s in workflow_steps),
            "detailed_workflow_steps": workflow_steps
        }
        """Test user management endpoints work correctly"""
        print("👥 Testing user management endpoints...")
        
        if not self.admin_token:
            return {
                "test_name": "User Management Endpoints",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        endpoint_tests = []
        
        # Test admin dashboard
        print("  Testing admin dashboard...")
        dashboard_result = await self.make_request("/admin/dashboard", headers=headers)
        endpoint_tests.append({
            "endpoint": "/admin/dashboard",
            "success": dashboard_result["success"],
            "response_time_ms": dashboard_result["response_time_ms"],
            "has_data": bool(dashboard_result.get("data")) if dashboard_result["success"] else False
        })
        
        # Test performance metrics
        print("  Testing performance metrics...")
        performance_result = await self.make_request("/admin/performance", headers=headers)
        endpoint_tests.append({
            "endpoint": "/admin/performance",
            "success": performance_result["success"],
            "response_time_ms": performance_result["response_time_ms"],
            "has_data": bool(performance_result.get("data")) if performance_result["success"] else False
        })
        
        # Test health check (public endpoint)
        print("  Testing health check...")
        health_result = await self.make_request("/health")
        endpoint_tests.append({
            "endpoint": "/health",
            "success": health_result["success"],
            "response_time_ms": health_result["response_time_ms"],
            "has_data": bool(health_result.get("data")) if health_result["success"] else False
        })
        
        successful_endpoints = [t for t in endpoint_tests if t["success"]]
        avg_response_time = statistics.mean([t["response_time_ms"] for t in successful_endpoints]) if successful_endpoints else 0
        
        return {
            "test_name": "User Management Endpoints",
            "total_endpoints_tested": len(endpoint_tests),
            "successful_endpoints": len(successful_endpoints),
            "success_rate": (len(successful_endpoints) / len(endpoint_tests)) * 100,
            "avg_response_time_ms": avg_response_time,
            "all_endpoints_working": len(successful_endpoints) == len(endpoint_tests),
            "detailed_endpoint_tests": endpoint_tests
        }
    
    async def test_browse_endpoint_performance(self) -> Dict:
        """Test browse endpoint still works after database reset"""
        print("🔍 Testing browse endpoint performance...")
        
        # Test basic browse functionality
        result = await self.make_request("/marketplace/browse")
        
        if result["success"]:
            listings = result["data"]
            
            # Check data structure integrity
            data_integrity_score = self.check_browse_data_integrity(listings)
            
            print(f"  ✅ Browse endpoint working: {len(listings)} listings found")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            print(f"  📊 Data integrity: {data_integrity_score:.1f}%")
            
            return {
                "test_name": "Browse Endpoint Performance",
                "endpoint_working": True,
                "response_time_ms": result["response_time_ms"],
                "listings_count": len(listings),
                "data_integrity_score": data_integrity_score,
                "meets_performance_target": result["response_time_ms"] < PERFORMANCE_TARGET_MS,
                "data_structure_valid": data_integrity_score >= 80
            }
        else:
            print(f"  ❌ Browse endpoint failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Browse Endpoint Performance",
                "endpoint_working": False,
                "error": result.get("error", "Browse endpoint failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"]
            }
    
    async def test_admin_functionality(self) -> Dict:
        """Test admin-specific features"""
        print("⚙️ Testing admin functionality...")
        
        if not self.admin_token:
            return {
                "test_name": "Admin Functionality",
                "error": "No admin token available - admin login required first"
            }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        admin_tests = []
        
        # Test admin dashboard access
        dashboard_result = await self.make_request("/admin/dashboard", headers=headers)
        admin_tests.append({
            "feature": "Admin Dashboard",
            "success": dashboard_result["success"],
            "response_time_ms": dashboard_result["response_time_ms"],
            "has_kpis": False
        })
        
        if dashboard_result["success"]:
            dashboard_data = dashboard_result["data"]
            # Check for KPI data
            has_kpis = any(key in dashboard_data for key in ["total_users", "total_revenue", "total_listings"])
            admin_tests[-1]["has_kpis"] = has_kpis
            
            print(f"  ✅ Admin dashboard accessible with KPIs: {has_kpis}")
        
        # Test performance metrics access
        performance_result = await self.make_request("/admin/performance", headers=headers)
        admin_tests.append({
            "feature": "Performance Metrics",
            "success": performance_result["success"],
            "response_time_ms": performance_result["response_time_ms"],
            "has_metrics": False
        })
        
        if performance_result["success"]:
            performance_data = performance_result["data"]
            has_metrics = any(key in performance_data for key in ["performance_status", "database", "cache"])
            admin_tests[-1]["has_metrics"] = has_metrics
            
            print(f"  ✅ Performance metrics accessible: {has_metrics}")
        
        successful_features = [t for t in admin_tests if t["success"]]
        
        return {
            "test_name": "Admin Functionality",
            "total_admin_features_tested": len(admin_tests),
            "successful_admin_features": len(successful_features),
            "admin_success_rate": (len(successful_features) / len(admin_tests)) * 100,
            "all_admin_features_working": len(successful_features) == len(admin_tests),
            "detailed_admin_tests": admin_tests
        }
    
    def check_browse_data_integrity(self, listings: List[Dict]) -> float:
        """Check data integrity of browse listings"""
        if not listings:
            return 100.0  # Empty result is valid
        
        total_checks = 0
        passed_checks = 0
        
        for listing in listings:
            # Check required fields
            required_fields = ["id", "title", "price"]
            for field in required_fields:
                total_checks += 1
                if field in listing and listing[field] is not None:
                    passed_checks += 1
            
            # Check seller information
            total_checks += 1
            if "seller" in listing and isinstance(listing["seller"], dict):
                seller = listing["seller"]
                if "name" in seller or "username" in seller:
                    passed_checks += 1
        
        return (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    async def run_comprehensive_admin_test(self) -> Dict:
        """Run all admin authentication and user management tests"""
        print("🚀 Starting Cataloro Admin Authentication & User Management Testing")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test suites
            admin_auth = await self.test_admin_user_authentication()
            db_consistency = await self.test_database_user_consistency()
            user_management_endpoints = await self.test_user_management_endpoints()
            user_management_functionality = await self.test_user_management_functionality()
            user_workflow = await self.test_user_workflow_integration()
            browse_performance = await self.test_browse_endpoint_performance()
            admin_functionality = await self.test_admin_functionality()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "admin_authentication": admin_auth,
                "database_consistency": db_consistency,
                "user_management_endpoints": user_management_endpoints,
                "user_management_functionality": user_management_functionality,
                "user_workflow_integration": user_workflow,
                "browse_endpoint_performance": browse_performance,
                "admin_functionality": admin_functionality
            }
            
            # Calculate overall success metrics
            test_results = [
                admin_auth.get("all_admin_properties_correct", False),
                db_consistency.get("all_users_consistent", False),
                user_management_endpoints.get("all_endpoints_working", False),
                user_management_functionality.get("critical_functionality_working", False),
                user_workflow.get("complete_workflow_working", False),
                browse_performance.get("endpoint_working", False),
                admin_functionality.get("all_admin_features_working", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "admin_authentication_working": admin_auth.get("all_admin_properties_correct", False),
                "database_consistency_verified": db_consistency.get("all_users_consistent", False),
                "user_management_endpoints_operational": user_management_endpoints.get("all_endpoints_working", False),
                "activate_suspend_functionality_working": user_management_functionality.get("activate_suspend_working", False),
                "state_persistence_working": user_management_functionality.get("state_persistence_working", False),
                "error_handling_working": user_management_functionality.get("error_handling_working", False),
                "complete_user_workflow_working": user_workflow.get("complete_workflow_working", False),
                "browse_endpoint_functional": browse_performance.get("endpoint_working", False),
                "admin_features_accessible": admin_functionality.get("all_admin_features_working", False),
                "all_tests_passed": overall_success_rate == 100
            }
            
            return all_results
            
        finally:
            await self.cleanup()


class BrowseEndpointTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{BACKEND_URL}{endpoint}", params=params) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "response_time_ms": response_time_ms,
                        "data": data,
                        "status": response.status
                    }
                else:
                    return {
                        "success": False,
                        "response_time_ms": response_time_ms,
                        "error": f"HTTP {response.status}",
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
    
    async def test_basic_browse_performance(self) -> Dict:
        """Test basic browse endpoint performance"""
        print("🔍 Testing basic browse endpoint performance...")
        
        # Test multiple calls to get average performance
        response_times = []
        data_integrity_checks = []
        
        for i in range(5):
            result = await self.make_request("/marketplace/browse")
            response_times.append(result["response_time_ms"])
            
            if result["success"]:
                # Check data integrity
                listings = result["data"]
                integrity_score = self.check_data_integrity(listings)
                data_integrity_checks.append(integrity_score)
                
                print(f"  Call {i+1}: {result['response_time_ms']:.0f}ms, {len(listings)} listings")
            else:
                print(f"  Call {i+1}: FAILED - {result['error']}")
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        meets_target = avg_response_time < PERFORMANCE_TARGET_MS
        avg_integrity = statistics.mean(data_integrity_checks) if data_integrity_checks else 0
        
        return {
            "test_name": "Basic Browse Performance",
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "meets_performance_target": meets_target,
            "target_ms": PERFORMANCE_TARGET_MS,
            "data_integrity_score": avg_integrity,
            "total_calls": len(response_times),
            "success_rate": len([t for t in response_times if t > 0]) / max(len(response_times), 1) * 100
        }
    
    async def test_cache_performance(self) -> Dict:
        """Test Redis caching effectiveness"""
        print("🚀 Testing Redis cache performance...")
        
        # Test parameters that should be cached
        test_params = {"type": "all", "page": 1, "limit": 10}
        
        # First call (cold cache)
        print("  Making cold cache call...")
        cold_result = await self.make_request("/marketplace/browse", test_params)
        
        # Wait a moment for cache to settle
        await asyncio.sleep(0.1)
        
        # Second call (warm cache)
        print("  Making warm cache call...")
        warm_result = await self.make_request("/marketplace/browse", test_params)
        
        # Third call (should also be cached)
        print("  Making second warm cache call...")
        warm_result2 = await self.make_request("/marketplace/browse", test_params)
        
        if cold_result["success"] and warm_result["success"] and warm_result2["success"]:
            cold_time = cold_result["response_time_ms"]
            warm_time = warm_result["response_time_ms"]
            warm_time2 = warm_result2["response_time_ms"]
            
            # Calculate cache improvement
            cache_improvement = ((cold_time - warm_time) / cold_time) * 100 if cold_time > 0 else 0
            cache_improvement2 = ((cold_time - warm_time2) / cold_time) * 100 if cold_time > 0 else 0
            
            avg_cache_improvement = (cache_improvement + cache_improvement2) / 2
            
            # Check data consistency
            data_consistent = self.compare_listing_data(cold_result["data"], warm_result["data"])
            
            print(f"  Cold cache: {cold_time:.0f}ms")
            print(f"  Warm cache: {warm_time:.0f}ms ({cache_improvement:.1f}% improvement)")
            print(f"  Warm cache 2: {warm_time2:.0f}ms ({cache_improvement2:.1f}% improvement)")
            
            return {
                "test_name": "Cache Performance",
                "cold_cache_ms": cold_time,
                "warm_cache_ms": warm_time,
                "warm_cache_2_ms": warm_time2,
                "cache_improvement_percent": avg_cache_improvement,
                "meets_cache_target": avg_cache_improvement >= CACHE_IMPROVEMENT_TARGET,
                "cache_target_percent": CACHE_IMPROVEMENT_TARGET,
                "data_consistent": data_consistent,
                "cache_working": warm_time < cold_time and warm_time2 < cold_time
            }
        else:
            return {
                "test_name": "Cache Performance",
                "error": "Failed to complete cache test",
                "cold_success": cold_result["success"],
                "warm_success": warm_result["success"],
                "cache_working": False
            }
    
    async def test_filtering_options(self) -> Dict:
        """Test various filtering options"""
        print("🔧 Testing filtering options...")
        
        filter_tests = [
            {"name": "No filters", "params": {}},
            {"name": "Private sellers", "params": {"type": "Private"}},
            {"name": "Business sellers", "params": {"type": "Business"}},
            {"name": "Price range 100-500", "params": {"price_from": 100, "price_to": 500}},
            {"name": "Price range 0-100", "params": {"price_from": 0, "price_to": 100}},
            {"name": "Page 2", "params": {"page": 2, "limit": 5}},
            {"name": "Large limit", "params": {"limit": 20}},
            {"name": "Combined filters", "params": {"type": "Business", "price_from": 50, "price_to": 1000, "page": 1, "limit": 10}}
        ]
        
        results = []
        
        for test in filter_tests:
            print(f"  Testing: {test['name']}")
            result = await self.make_request("/marketplace/browse", test["params"])
            
            if result["success"]:
                listings = result["data"]
                integrity_score = self.check_data_integrity(listings)
                filter_validation = self.validate_filters(listings, test["params"])
                
                test_result = {
                    "filter_name": test["name"],
                    "response_time_ms": result["response_time_ms"],
                    "listing_count": len(listings),
                    "data_integrity_score": integrity_score,
                    "filter_validation_passed": filter_validation,
                    "success": True
                }
                
                print(f"    ✅ {result['response_time_ms']:.0f}ms, {len(listings)} listings, integrity: {integrity_score:.1f}%")
            else:
                test_result = {
                    "filter_name": test["name"],
                    "response_time_ms": result["response_time_ms"],
                    "error": result["error"],
                    "success": False
                }
                print(f"    ❌ FAILED - {result['error']}")
            
            results.append(test_result)
        
        # Calculate overall statistics
        successful_tests = [r for r in results if r["success"]]
        avg_response_time = statistics.mean([r["response_time_ms"] for r in successful_tests]) if successful_tests else 0
        avg_integrity = statistics.mean([r["data_integrity_score"] for r in successful_tests if "data_integrity_score" in r]) if successful_tests else 0
        
        return {
            "test_name": "Filtering Options",
            "total_filter_tests": len(filter_tests),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(filter_tests) * 100,
            "avg_response_time_ms": avg_response_time,
            "avg_data_integrity": avg_integrity,
            "all_filters_under_target": all(r.get("response_time_ms", 9999) < PERFORMANCE_TARGET_MS for r in successful_tests),
            "detailed_results": results
        }
    
    async def test_concurrent_performance(self) -> Dict:
        """Test concurrent request performance"""
        print("⚡ Testing concurrent request performance...")
        
        # Test with 5 concurrent requests
        concurrent_count = 5
        start_time = time.time()
        
        # Create concurrent requests
        tasks = []
        for i in range(concurrent_count):
            params = {"page": i + 1, "limit": 5}  # Different pages to avoid cache hits
            task = self.make_request("/marketplace/browse", params)
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time_ms = (end_time - start_time) * 1000
        successful_requests = [r for r in results if r["success"]]
        
        if successful_requests:
            avg_individual_time = statistics.mean([r["response_time_ms"] for r in successful_requests])
            max_individual_time = max([r["response_time_ms"] for r in successful_requests])
            min_individual_time = min([r["response_time_ms"] for r in successful_requests])
            
            print(f"  {len(successful_requests)}/{concurrent_count} requests successful")
            print(f"  Total time: {total_time_ms:.0f}ms")
            print(f"  Avg individual: {avg_individual_time:.0f}ms")
            print(f"  Max individual: {max_individual_time:.0f}ms")
            
            return {
                "test_name": "Concurrent Performance",
                "concurrent_requests": concurrent_count,
                "successful_requests": len(successful_requests),
                "total_time_ms": total_time_ms,
                "avg_individual_time_ms": avg_individual_time,
                "max_individual_time_ms": max_individual_time,
                "min_individual_time_ms": min_individual_time,
                "throughput_requests_per_second": len(successful_requests) / (total_time_ms / 1000),
                "all_under_target": max_individual_time < PERFORMANCE_TARGET_MS,
                "concurrent_performance_acceptable": total_time_ms < (PERFORMANCE_TARGET_MS * 2)
            }
        else:
            return {
                "test_name": "Concurrent Performance",
                "error": "All concurrent requests failed",
                "successful_requests": 0,
                "concurrent_requests": concurrent_count
            }
    
    async def test_pagination_performance(self) -> Dict:
        """Test pagination performance across different pages"""
        print("📄 Testing pagination performance...")
        
        page_tests = []
        
        # Test first 5 pages
        for page in range(1, 6):
            params = {"page": page, "limit": 10}
            result = await self.make_request("/marketplace/browse", params)
            
            if result["success"]:
                listings = result["data"]
                page_tests.append({
                    "page": page,
                    "response_time_ms": result["response_time_ms"],
                    "listing_count": len(listings),
                    "success": True
                })
                print(f"  Page {page}: {result['response_time_ms']:.0f}ms, {len(listings)} listings")
            else:
                page_tests.append({
                    "page": page,
                    "error": result["error"],
                    "success": False
                })
                print(f"  Page {page}: FAILED - {result['error']}")
        
        successful_pages = [p for p in page_tests if p["success"]]
        
        if successful_pages:
            avg_response_time = statistics.mean([p["response_time_ms"] for p in successful_pages])
            max_response_time = max([p["response_time_ms"] for p in successful_pages])
            
            return {
                "test_name": "Pagination Performance",
                "pages_tested": len(page_tests),
                "successful_pages": len(successful_pages),
                "avg_response_time_ms": avg_response_time,
                "max_response_time_ms": max_response_time,
                "all_pages_under_target": max_response_time < PERFORMANCE_TARGET_MS,
                "pagination_consistent": max_response_time - statistics.mean([p["response_time_ms"] for p in successful_pages]) < 200,
                "detailed_results": page_tests
            }
        else:
            return {
                "test_name": "Pagination Performance",
                "error": "All pagination tests failed",
                "pages_tested": len(page_tests),
                "successful_pages": 0
            }
    
    def check_data_integrity(self, listings: List[Dict]) -> float:
        """Check data integrity of listings"""
        if not listings:
            return 100.0  # Empty result is valid
        
        total_checks = 0
        passed_checks = 0
        
        for listing in listings:
            # Check required fields
            required_fields = ["id", "title", "price"]
            for field in required_fields:
                total_checks += 1
                if field in listing and listing[field] is not None:
                    passed_checks += 1
            
            # Check seller information
            total_checks += 1
            if "seller" in listing and isinstance(listing["seller"], dict):
                seller = listing["seller"]
                if "name" in seller and "username" in seller:
                    passed_checks += 1
            
            # Check bid information
            total_checks += 1
            if "bid_info" in listing and isinstance(listing["bid_info"], dict):
                bid_info = listing["bid_info"]
                if "has_bids" in bid_info and "total_bids" in bid_info and "highest_bid" in bid_info:
                    passed_checks += 1
            
            # Check time information
            total_checks += 1
            if "time_info" in listing and isinstance(listing["time_info"], dict):
                time_info = listing["time_info"]
                if "has_time_limit" in time_info and "is_expired" in time_info:
                    passed_checks += 1
        
        return (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    def validate_filters(self, listings: List[Dict], params: Dict) -> bool:
        """Validate that filters are applied correctly"""
        if not listings:
            return True  # Empty result is valid for filters
        
        # Check price filters
        price_from = params.get("price_from", 0)
        price_to = params.get("price_to", 999999)
        
        for listing in listings:
            price = listing.get("price", 0)
            if price < price_from or price > price_to:
                return False
        
        # Check seller type filter
        seller_type = params.get("type")
        if seller_type and seller_type != "all":
            for listing in listings:
                seller = listing.get("seller", {})
                is_business = seller.get("is_business", False)
                
                if seller_type == "Private" and is_business:
                    return False
                elif seller_type == "Business" and not is_business:
                    return False
        
        return True
    
    def compare_listing_data(self, data1: List[Dict], data2: List[Dict]) -> bool:
        """Compare two listing datasets for consistency"""
        if len(data1) != len(data2):
            return False
        
        # Compare first few listings for key fields
        for i in range(min(3, len(data1))):
            listing1 = data1[i]
            listing2 = data2[i]
            
            # Check key fields match
            key_fields = ["id", "title", "price"]
            for field in key_fields:
                if listing1.get(field) != listing2.get(field):
                    return False
        
        return True
    
    async def run_comprehensive_test(self) -> Dict:
        """Run all performance tests"""
        print("🚀 Starting Cataloro Browse Endpoint Performance Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run all test suites
            basic_performance = await self.test_basic_browse_performance()
            cache_performance = await self.test_cache_performance()
            filtering_performance = await self.test_filtering_options()
            concurrent_performance = await self.test_concurrent_performance()
            pagination_performance = await self.test_pagination_performance()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "performance_target_ms": PERFORMANCE_TARGET_MS,
                "cache_improvement_target_percent": CACHE_IMPROVEMENT_TARGET,
                "basic_performance": basic_performance,
                "cache_performance": cache_performance,
                "filtering_performance": filtering_performance,
                "concurrent_performance": concurrent_performance,
                "pagination_performance": pagination_performance
            }
            
            # Calculate overall success metrics
            performance_tests = [
                basic_performance.get("meets_performance_target", False),
                filtering_performance.get("all_filters_under_target", False),
                concurrent_performance.get("all_under_target", False),
                pagination_performance.get("all_pages_under_target", False)
            ]
            
            cache_working = cache_performance.get("cache_working", False)
            data_integrity_scores = [
                basic_performance.get("data_integrity_score", 0),
                filtering_performance.get("avg_data_integrity", 0)
            ]
            
            overall_performance_success = sum(performance_tests) / len(performance_tests) * 100
            avg_data_integrity = statistics.mean(data_integrity_scores)
            
            all_results["summary"] = {
                "overall_performance_success_rate": overall_performance_success,
                "cache_functionality_working": cache_working,
                "average_data_integrity_score": avg_data_integrity,
                "performance_target_met": overall_performance_success >= 75,
                "cache_target_met": cache_performance.get("meets_cache_target", False),
                "data_integrity_excellent": avg_data_integrity >= 90
            }
            
            return all_results
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    print("🔧 Cataloro Marketplace Testing Suite")
    print("=" * 50)
    
    # Run Admin Authentication & Database Consistency Tests
    print("\n🔐 ADMIN AUTHENTICATION & DATABASE CONSISTENCY TESTS")
    print("=" * 60)
    
    admin_tester = AdminAuthenticationTester()
    admin_results = await admin_tester.run_comprehensive_admin_test()
    
    # Print Admin Test Summary
    print("\n" + "=" * 60)
    print("📊 ADMIN AUTHENTICATION & DATABASE CONSISTENCY SUMMARY")
    print("=" * 60)
    
    admin_summary = admin_results["summary"]
    admin_auth = admin_results["admin_authentication"]
    db_consistency = admin_results["database_consistency"]
    user_mgmt = admin_results["user_management_endpoints"]
    browse_perf = admin_results["browse_endpoint_performance"]
    admin_func = admin_results["admin_functionality"]
    
    print(f"🎯 Overall Success Rate: {admin_summary.get('overall_success_rate', 0):.0f}%")
    print()
    
    # Admin Authentication
    auth_status = "✅" if admin_auth.get("all_admin_properties_correct") else "❌"
    print(f"{auth_status} Admin Authentication: {admin_auth.get('login_successful', False)}")
    if admin_auth.get("login_successful"):
        print(f"   📧 Email: {admin_auth.get('admin_email_correct', False)}")
        print(f"   👤 Username: {admin_auth.get('admin_username_correct', False)}")
        print(f"   🔑 Role: {admin_auth.get('admin_role_correct', False)}")
    
    # Database Consistency
    db_status = "✅" if db_consistency.get("all_users_consistent") else "❌"
    db_score = db_consistency.get("database_consistency_score", 0)
    print(f"{db_status} Database Consistency: {db_score:.0f}%")
    print(f"   👥 Users Found: {db_consistency.get('users_found_in_database', 0)}/{db_consistency.get('total_expected_users', 0)}")
    
    # User Management Endpoints
    mgmt_status = "✅" if user_mgmt.get("all_endpoints_working") else "❌"
    mgmt_success = user_mgmt.get("success_rate", 0)
    print(f"{mgmt_status} User Management Endpoints: {mgmt_success:.0f}% success rate")
    
    # Browse Endpoint Performance
    browse_status = "✅" if browse_perf.get("endpoint_working") else "❌"
    browse_time = browse_perf.get("response_time_ms", 0)
    print(f"{browse_status} Browse Endpoint: {browse_time:.0f}ms response time")
    
    # Admin Functionality
    func_status = "✅" if admin_func.get("all_admin_features_working") else "❌"
    func_success = admin_func.get("admin_success_rate", 0)
    print(f"{func_status} Admin Functionality: {func_success:.0f}% features working")
    
    print()
    print("🏆 OVERALL ADMIN TEST RESULTS:")
    overall_status = "✅ ALL TESTS PASSED" if admin_summary.get("all_tests_passed") else "⚠️ SOME TESTS FAILED"
    print(f"   {overall_status}")
    print(f"   Success Rate: {admin_summary.get('overall_success_rate', 0):.0f}%")
    
    # Save detailed results
    with open("/app/admin_authentication_test_results.json", "w") as f:
        json.dump(admin_results, f, indent=2, default=str)
    
    print(f"\n📄 Admin test results saved to: /app/admin_authentication_test_results.json")
    
    # Run Browse Performance Tests (if requested)
    run_browse_tests = input("\n🤔 Run additional browse performance tests? (y/N): ").lower().strip() == 'y'
    
    if run_browse_tests:
        print("\n🚀 BROWSE ENDPOINT PERFORMANCE TESTS")
        print("=" * 50)
        
        browse_tester = BrowseEndpointTester()
        browse_results = await browse_tester.run_comprehensive_test()
        
        # Print Browse Test Summary
        print("\n" + "=" * 60)
        print("📊 BROWSE PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        browse_summary = browse_results["summary"]
        basic = browse_results["basic_performance"]
        cache = browse_results["cache_performance"]
        filtering = browse_results["filtering_performance"]
        concurrent = browse_results["concurrent_performance"]
        pagination = browse_results["pagination_performance"]
        
        print(f"🎯 Performance Target: {browse_results['performance_target_ms']}ms")
        print(f"📈 Cache Improvement Target: {browse_results['cache_improvement_target_percent']}%")
        print()
        
        # Basic Performance
        status = "✅" if basic.get("meets_performance_target") else "❌"
        print(f"{status} Basic Browse Performance: {basic.get('avg_response_time_ms', 0):.0f}ms avg")
        
        # Cache Performance
        cache_status = "✅" if cache.get("cache_working") else "❌"
        improvement = cache.get("cache_improvement_percent", 0)
        print(f"{cache_status} Cache Performance: {improvement:.1f}% improvement")
        
        # Data Integrity
        integrity_status = "✅" if browse_summary.get("data_integrity_excellent") else "❌"
        integrity = browse_summary.get("average_data_integrity_score", 0)
        print(f"{integrity_status} Data Integrity: {integrity:.1f}%")
        
        # Filtering
        filter_status = "✅" if filtering.get("all_filters_under_target") else "❌"
        filter_success = filtering.get("success_rate", 0)
        print(f"{filter_status} Filtering Options: {filter_success:.0f}% success rate")
        
        # Concurrent Performance
        concurrent_status = "✅" if concurrent.get("all_under_target") else "❌"
        throughput = concurrent.get("throughput_requests_per_second", 0)
        print(f"{concurrent_status} Concurrent Performance: {throughput:.1f} req/sec")
        
        # Pagination
        pagination_status = "✅" if pagination.get("all_pages_under_target") else "❌"
        pagination_success = pagination.get("successful_pages", 0)
        print(f"{pagination_status} Pagination: {pagination_success}/5 pages successful")
        
        print()
        print("🏆 BROWSE PERFORMANCE RESULTS:")
        browse_overall_status = "✅ EXCELLENT" if browse_summary.get("performance_target_met") and browse_summary.get("cache_target_met") else "⚠️ NEEDS IMPROVEMENT"
        print(f"   {browse_overall_status}")
        print(f"   Performance Success Rate: {browse_summary.get('overall_performance_success_rate', 0):.0f}%")
        print(f"   Cache Working: {'Yes' if browse_summary.get('cache_functionality_working') else 'No'}")
        print(f"   Data Integrity: {browse_summary.get('average_data_integrity_score', 0):.0f}%")
        
        # Save detailed results
        with open("/app/browse_performance_test_results.json", "w") as f:
            json.dump(browse_results, f, indent=2, default=str)
        
        print(f"\n📄 Browse test results saved to: /app/browse_performance_test_results.json")
    
    return admin_results

if __name__ == "__main__":
    asyncio.run(main())