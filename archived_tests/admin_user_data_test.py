#!/usr/bin/env python3
"""
ADMIN PANEL USER STATUS COUNTING INVESTIGATION - URGENT
Investigating the user data structure to fix the Admin Panel user status counting issue:

PROBLEM REPORTED:
- Admin Panel shows "20 total, 20 active and 20 pending" - all the same number
- Users are being double-counted between active and pending categories
- Current filtering logic is not working correctly

INVESTIGATION NEEDED:
1. Test GET `/api/admin/users` endpoint to see actual user data structure
2. Examine what fields determine user status (active vs pending)
3. Check fields like: status, registration_status, is_active, is_verified, user_role
4. Identify the correct logic to separate active from pending users
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://vps-sync.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"

class AdminUserDataInvestigator:
    """
    ADMIN PANEL USER DATA STRUCTURE INVESTIGATION
    Investigating the user data structure to understand why user counts are incorrect
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = {}
        
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
    
    async def authenticate_admin(self) -> bool:
        """Authenticate admin user"""
        print("🔐 Authenticating admin user for user data investigation...")
        
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login_data)
        
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            print(f"  ✅ Admin authentication successful")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {admin_result.get('error', 'Unknown error')}")
            return False
    
    async def test_admin_users_endpoint(self) -> Dict:
        """
        Test 1: User Data Structure Analysis
        Test GET `/api/admin/users` endpoint to see actual user data structure
        """
        print("👥 Testing GET /api/admin/users endpoint...")
        
        test_results = {
            "endpoint": "/admin/users",
            "expected_status": 200,
            "actual_status": 0,
            "response_time_ms": 0,
            "total_users": 0,
            "user_data_structure": {},
            "status_fields_found": [],
            "sample_users": [],
            "error_messages": [],
            "success": False
        }
        
        # Test admin users endpoint with authentication
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/users", headers=headers)
        
        test_results["actual_status"] = result["status"]
        test_results["response_time_ms"] = result["response_time_ms"]
        
        if result["success"]:
            users_data = result.get("data", [])
            test_results["total_users"] = len(users_data) if isinstance(users_data, list) else 0
            test_results["success"] = True
            
            print(f"    ✅ Admin users endpoint successful")
            print(f"    📊 Total users found: {test_results['total_users']}")
            print(f"    ⏱️ Response time: {test_results['response_time_ms']:.1f}ms")
            
            # Analyze user data structure
            if users_data and isinstance(users_data, list) and len(users_data) > 0:
                # Get first few users as samples
                sample_count = min(5, len(users_data))
                test_results["sample_users"] = users_data[:sample_count]
                
                # Analyze fields in first user
                first_user = users_data[0]
                if isinstance(first_user, dict):
                    test_results["user_data_structure"] = {
                        "all_fields": list(first_user.keys()),
                        "status_related_fields": []
                    }
                    
                    # Look for status-related fields
                    status_fields = [
                        "status", "registration_status", "is_active", "is_verified", 
                        "user_role", "role", "badge", "account_status", "approved"
                    ]
                    
                    for field in status_fields:
                        if field in first_user:
                            test_results["status_fields_found"].append(field)
                            test_results["user_data_structure"]["status_related_fields"].append({
                                "field": field,
                                "value": first_user[field],
                                "type": type(first_user[field]).__name__
                            })
                    
                    print(f"    🔍 Status-related fields found: {test_results['status_fields_found']}")
                    
                    # Print sample user data structure
                    print(f"    📋 Sample user fields: {list(first_user.keys())}")
                    for status_field in test_results["user_data_structure"]["status_related_fields"]:
                        print(f"      - {status_field['field']}: {status_field['value']} ({status_field['type']})")
            else:
                test_results["error_messages"].append("No user data returned or invalid format")
                print(f"    ⚠️ No user data returned or invalid format")
        else:
            test_results["error_messages"].append(f"Admin users endpoint failed: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Admin users endpoint failed: Status {result['status']}")
            if result.get("error"):
                print(f"    ❌ Error: {result['error']}")
        
        return {
            "test_name": "User Data Structure Analysis",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def test_user_status_field_mapping(self) -> Dict:
        """
        Test 2: User Status Field Mapping
        Determine what makes a user "active" vs "pending"
        """
        print("🔍 Analyzing user status field mapping...")
        
        test_results = {
            "status_field_analysis": {},
            "active_users_count": 0,
            "pending_users_count": 0,
            "rejected_users_count": 0,
            "inactive_users_count": 0,
            "status_distribution": {},
            "registration_status_distribution": {},
            "is_active_distribution": {},
            "user_role_distribution": {},
            "filtering_logic_recommendations": [],
            "error_messages": [],
            "success": False
        }
        
        # Get user data from previous test
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/users", headers=headers)
        
        if result["success"]:
            users_data = result.get("data", [])
            test_results["success"] = True
            
            print(f"    📊 Analyzing {len(users_data)} users for status patterns...")
            
            # Initialize counters
            registration_status_counts = {}
            is_active_counts = {}
            user_role_counts = {}
            status_counts = {}
            
            active_users = []
            pending_users = []
            rejected_users = []
            inactive_users = []
            
            # Analyze each user
            for user in users_data:
                if isinstance(user, dict):
                    # Count registration_status values
                    reg_status = user.get("registration_status", "Unknown")
                    registration_status_counts[reg_status] = registration_status_counts.get(reg_status, 0) + 1
                    
                    # Count is_active values
                    is_active = user.get("is_active", "Unknown")
                    is_active_counts[is_active] = is_active_counts.get(is_active, 0) + 1
                    
                    # Count user_role values
                    user_role = user.get("user_role", "Unknown")
                    user_role_counts[user_role] = user_role_counts.get(user_role, 0) + 1
                    
                    # Count status values (if exists)
                    status = user.get("status", "Unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    # Categorize users based on different logic
                    # Logic 1: Based on registration_status
                    if reg_status == "Approved":
                        active_users.append(user)
                    elif reg_status == "Pending":
                        pending_users.append(user)
                    elif reg_status == "Rejected":
                        rejected_users.append(user)
                    
                    # Logic 2: Based on is_active
                    if not user.get("is_active", True):
                        inactive_users.append(user)
            
            test_results["active_users_count"] = len(active_users)
            test_results["pending_users_count"] = len(pending_users)
            test_results["rejected_users_count"] = len(rejected_users)
            test_results["inactive_users_count"] = len(inactive_users)
            
            test_results["registration_status_distribution"] = registration_status_counts
            test_results["is_active_distribution"] = is_active_counts
            test_results["user_role_distribution"] = user_role_counts
            test_results["status_distribution"] = status_counts
            
            print(f"    📈 Registration Status Distribution: {registration_status_counts}")
            print(f"    📈 Is Active Distribution: {is_active_counts}")
            print(f"    📈 User Role Distribution: {user_role_counts}")
            print(f"    📈 Status Distribution: {status_counts}")
            
            print(f"    ✅ Active users (registration_status='Approved'): {test_results['active_users_count']}")
            print(f"    ⏳ Pending users (registration_status='Pending'): {test_results['pending_users_count']}")
            print(f"    ❌ Rejected users (registration_status='Rejected'): {test_results['rejected_users_count']}")
            print(f"    🚫 Inactive users (is_active=false): {test_results['inactive_users_count']}")
            
            # Generate filtering logic recommendations
            recommendations = []
            
            if "Approved" in registration_status_counts and "Pending" in registration_status_counts:
                recommendations.append("Use registration_status field: 'Approved' for active, 'Pending' for pending")
            
            if True in is_active_counts and False in is_active_counts:
                recommendations.append("Use is_active field: true for active, false for suspended/inactive")
            
            recommendations.append("Combine both: registration_status='Approved' AND is_active=true for truly active users")
            recommendations.append("Pending users: registration_status='Pending' (regardless of is_active)")
            
            test_results["filtering_logic_recommendations"] = recommendations
            
            print(f"    💡 Filtering Logic Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"      {i}. {rec}")
                
        else:
            test_results["error_messages"].append(f"Failed to get user data: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Failed to get user data: {result.get('error', 'Unknown error')}")
        
        return {
            "test_name": "User Status Field Mapping",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def test_sample_user_records(self) -> Dict:
        """
        Test 3: Sample User Records
        Get sample user records to understand the data structure
        """
        print("📝 Analyzing sample user records...")
        
        test_results = {
            "sample_approved_users": [],
            "sample_pending_users": [],
            "sample_rejected_users": [],
            "sample_inactive_users": [],
            "field_comparison": {},
            "correct_filtering_criteria": {},
            "error_messages": [],
            "success": False
        }
        
        # Get user data
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/users", headers=headers)
        
        if result["success"]:
            users_data = result.get("data", [])
            test_results["success"] = True
            
            print(f"    🔍 Analyzing sample records from {len(users_data)} users...")
            
            # Categorize users and collect samples
            for user in users_data:
                if isinstance(user, dict):
                    reg_status = user.get("registration_status", "Unknown")
                    is_active = user.get("is_active", True)
                    
                    # Collect samples of different user types
                    if reg_status == "Approved" and len(test_results["sample_approved_users"]) < 3:
                        test_results["sample_approved_users"].append({
                            "id": user.get("id", "N/A"),
                            "email": user.get("email", "N/A"),
                            "registration_status": reg_status,
                            "is_active": is_active,
                            "user_role": user.get("user_role", "N/A"),
                            "badge": user.get("badge", "N/A"),
                            "created_at": user.get("created_at", "N/A")
                        })
                    
                    elif reg_status == "Pending" and len(test_results["sample_pending_users"]) < 3:
                        test_results["sample_pending_users"].append({
                            "id": user.get("id", "N/A"),
                            "email": user.get("email", "N/A"),
                            "registration_status": reg_status,
                            "is_active": is_active,
                            "user_role": user.get("user_role", "N/A"),
                            "badge": user.get("badge", "N/A"),
                            "created_at": user.get("created_at", "N/A")
                        })
                    
                    elif reg_status == "Rejected" and len(test_results["sample_rejected_users"]) < 3:
                        test_results["sample_rejected_users"].append({
                            "id": user.get("id", "N/A"),
                            "email": user.get("email", "N/A"),
                            "registration_status": reg_status,
                            "is_active": is_active,
                            "user_role": user.get("user_role", "N/A"),
                            "badge": user.get("badge", "N/A"),
                            "created_at": user.get("created_at", "N/A")
                        })
                    
                    elif not is_active and len(test_results["sample_inactive_users"]) < 3:
                        test_results["sample_inactive_users"].append({
                            "id": user.get("id", "N/A"),
                            "email": user.get("email", "N/A"),
                            "registration_status": reg_status,
                            "is_active": is_active,
                            "user_role": user.get("user_role", "N/A"),
                            "badge": user.get("badge", "N/A"),
                            "created_at": user.get("created_at", "N/A")
                        })
            
            # Print sample records
            print(f"    ✅ Sample Approved Users ({len(test_results['sample_approved_users'])}):")
            for user in test_results["sample_approved_users"]:
                print(f"      - {user['email']}: reg_status={user['registration_status']}, is_active={user['is_active']}, role={user['user_role']}")
            
            print(f"    ⏳ Sample Pending Users ({len(test_results['sample_pending_users'])}):")
            for user in test_results["sample_pending_users"]:
                print(f"      - {user['email']}: reg_status={user['registration_status']}, is_active={user['is_active']}, role={user['user_role']}")
            
            print(f"    ❌ Sample Rejected Users ({len(test_results['sample_rejected_users'])}):")
            for user in test_results["sample_rejected_users"]:
                print(f"      - {user['email']}: reg_status={user['registration_status']}, is_active={user['is_active']}, role={user['user_role']}")
            
            print(f"    🚫 Sample Inactive Users ({len(test_results['sample_inactive_users'])}):")
            for user in test_results["sample_inactive_users"]:
                print(f"      - {user['email']}: reg_status={user['registration_status']}, is_active={user['is_active']}, role={user['user_role']}")
            
            # Determine correct filtering criteria
            test_results["correct_filtering_criteria"] = {
                "active_users": "registration_status == 'Approved' AND is_active == true",
                "pending_users": "registration_status == 'Pending'",
                "rejected_users": "registration_status == 'Rejected'",
                "inactive_users": "is_active == false",
                "total_users": "COUNT(*) - all users regardless of status"
            }
            
            print(f"    💡 Correct Filtering Criteria:")
            for category, criteria in test_results["correct_filtering_criteria"].items():
                print(f"      - {category}: {criteria}")
                
        else:
            test_results["error_messages"].append(f"Failed to get user data: {result.get('error', 'Unknown error')}")
            print(f"    ❌ Failed to get user data: {result.get('error', 'Unknown error')}")
        
        return {
            "test_name": "Sample User Records",
            "success": test_results["success"],
            "test_results": test_results,
            "critical_issue": not test_results["success"]
        }
    
    async def run_admin_user_data_investigation(self) -> Dict:
        """
        Run complete admin user data structure investigation
        """
        print("🚨 STARTING ADMIN PANEL USER DATA STRUCTURE INVESTIGATION")
        print("=" * 80)
        print("PROBLEM: Admin Panel shows same count for total, active, and pending users")
        print("GOAL: Understand user data structure and identify correct filtering logic")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_admin()
            if not auth_success:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Admin authentication failed - cannot proceed with investigation"
                }
            
            # Run all investigation tests
            data_structure_test = await self.test_admin_users_endpoint()
            status_mapping_test = await self.test_user_status_field_mapping()
            sample_records_test = await self.test_sample_user_records()
            
            # Compile comprehensive investigation results
            investigation_results = {
                "test_timestamp": datetime.now().isoformat(),
                "investigation_focus": "Admin Panel user data structure and counting logic",
                "user_data_structure_test": data_structure_test,
                "user_status_mapping_test": status_mapping_test,
                "sample_user_records_test": sample_records_test
            }
            
            # Determine critical findings
            critical_issues = []
            working_features = []
            
            tests = [data_structure_test, status_mapping_test, sample_records_test]
            
            for test in tests:
                if test.get("critical_issue", False):
                    error_msg = "Unknown error"
                    if test.get("test_results", {}).get("error_messages"):
                        error_msg = test["test_results"]["error_messages"][0]
                    elif test.get("error"):
                        error_msg = test["error"]
                    critical_issues.append(f"{test['test_name']}: {error_msg}")
                
                if test.get("success", False):
                    working_features.append(f"{test['test_name']}: Investigation completed successfully")
            
            # Calculate success metrics
            total_tests = len(tests)
            successful_tests = sum(1 for test in tests if test.get("success", False))
            success_rate = (successful_tests / total_tests) * 100
            
            # Extract key findings
            key_findings = {}
            if status_mapping_test.get("success"):
                status_results = status_mapping_test["test_results"]
                key_findings = {
                    "total_users": status_results.get("active_users_count", 0) + status_results.get("pending_users_count", 0) + status_results.get("rejected_users_count", 0),
                    "active_users": status_results.get("active_users_count", 0),
                    "pending_users": status_results.get("pending_users_count", 0),
                    "rejected_users": status_results.get("rejected_users_count", 0),
                    "inactive_users": status_results.get("inactive_users_count", 0),
                    "registration_status_distribution": status_results.get("registration_status_distribution", {}),
                    "is_active_distribution": status_results.get("is_active_distribution", {}),
                    "filtering_recommendations": status_results.get("filtering_logic_recommendations", [])
                }
            
            investigation_results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": success_rate,
                "critical_issues": critical_issues,
                "working_features": working_features,
                "investigation_complete": len(critical_issues) == 0,
                "key_findings": key_findings
            }
            
            return investigation_results
            
        finally:
            await self.cleanup()


async def main():
    """Run the admin user data investigation"""
    investigator = AdminUserDataInvestigator()
    results = await investigator.run_admin_user_data_investigation()
    
    print("\n" + "=" * 80)
    print("🔍 ADMIN USER DATA STRUCTURE INVESTIGATION RESULTS")
    print("=" * 80)
    
    summary = results.get("summary", {})
    key_findings = summary.get("key_findings", {})
    
    if key_findings:
        print(f"📊 USER COUNT ANALYSIS:")
        print(f"   Total Users: {key_findings.get('total_users', 'N/A')}")
        print(f"   Active Users: {key_findings.get('active_users', 'N/A')} (registration_status='Approved')")
        print(f"   Pending Users: {key_findings.get('pending_users', 'N/A')} (registration_status='Pending')")
        print(f"   Rejected Users: {key_findings.get('rejected_users', 'N/A')} (registration_status='Rejected')")
        print(f"   Inactive Users: {key_findings.get('inactive_users', 'N/A')} (is_active=false)")
        
        print(f"\n📈 FIELD DISTRIBUTIONS:")
        print(f"   Registration Status: {key_findings.get('registration_status_distribution', {})}")
        print(f"   Is Active: {key_findings.get('is_active_distribution', {})}")
        
        print(f"\n💡 FILTERING RECOMMENDATIONS:")
        for i, rec in enumerate(key_findings.get('filtering_recommendations', []), 1):
            print(f"   {i}. {rec}")
    
    print(f"\n✅ Investigation Success Rate: {summary.get('success_rate', 0):.1f}%")
    print(f"📋 Tests Completed: {summary.get('successful_tests', 0)}/{summary.get('total_tests', 0)}")
    
    if summary.get("critical_issues"):
        print(f"\n❌ CRITICAL ISSUES:")
        for issue in summary["critical_issues"]:
            print(f"   - {issue}")
    
    if summary.get("working_features"):
        print(f"\n✅ WORKING FEATURES:")
        for feature in summary["working_features"]:
            print(f"   - {feature}")
    
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())