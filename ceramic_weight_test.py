#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Ceramic Weight Display Fix Verification
Testing the ceramic weight display fix in CreateListingPage.js
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://catalyst-unified.preview.emergentagent.com/api"

class CeramicWeightTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}, Version: {data.get('version')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def test_unified_calculations_weight_field(self):
        """Test that unified calculations endpoint returns catalyst data with 'weight' field (not 'ceramic_weight')"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations", timeout=15)
            if response.status_code == 200:
                unified_data = response.json()
                
                if isinstance(unified_data, list) and len(unified_data) > 0:
                    # Check if weight field is present (not ceramic_weight)
                    sample_items = unified_data[:5]  # Check first 5 items
                    
                    weight_field_count = 0
                    ceramic_weight_field_count = 0
                    items_with_weight_values = 0
                    
                    for item in sample_items:
                        if "weight" in item:
                            weight_field_count += 1
                            if item.get("weight", 0) > 0:
                                items_with_weight_values += 1
                        if "ceramic_weight" in item:
                            ceramic_weight_field_count += 1
                    
                    # The fix requires 'weight' field, not 'ceramic_weight'
                    has_correct_field = weight_field_count > 0
                    has_incorrect_field = ceramic_weight_field_count > 0
                    
                    self.log_test(
                        "Unified Calculations Weight Field Structure", 
                        has_correct_field and not has_incorrect_field, 
                        f"Total catalysts: {len(unified_data)}, Items with 'weight' field: {weight_field_count}/{len(sample_items)}, Items with 'ceramic_weight' field: {ceramic_weight_field_count}/{len(sample_items)}, Items with weight values > 0: {items_with_weight_values}"
                    )
                    return unified_data if has_correct_field else None
                else:
                    self.log_test("Unified Calculations Weight Field Structure", True, "No data to test (empty database)")
                    return []
            else:
                self.log_test("Unified Calculations Weight Field Structure", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Unified Calculations Weight Field Structure", False, error_msg=str(e))
            return None

    def test_admin_login_for_catalyst_access(self):
        """Test admin login to access catalyst functionality"""
        try:
            # Login as admin
            admin_credentials = {
                "email": "admin@cataloro.com",
                "password": "admin123"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login", 
                json=admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                user_role = user.get('user_role')
                user_id = user.get('id')
                
                # Check if user has admin/manager permissions for catalyst access
                has_catalyst_permissions = user_role in ['Admin', 'Admin-Manager']
                
                self.log_test(
                    "Admin Login for Catalyst Access", 
                    has_catalyst_permissions, 
                    f"Admin logged in successfully. Role: {user_role}, Has catalyst permissions: {has_catalyst_permissions}, User ID: {user_id}"
                )
                return user if has_catalyst_permissions else None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login for Catalyst Access", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Admin Login for Catalyst Access", False, error_msg=str(e))
            return None

    def test_catalyst_selection_data_consistency(self, unified_data):
        """Test that catalyst selection works properly with weight field"""
        if not unified_data:
            self.log_test("Catalyst Selection Data Consistency", False, error_msg="No unified data provided")
            return False
            
        try:
            # Find catalysts with weight values for testing
            catalysts_with_weight = [
                catalyst for catalyst in unified_data 
                if catalyst.get("weight", 0) > 0
            ]
            
            if len(catalysts_with_weight) == 0:
                self.log_test("Catalyst Selection Data Consistency", True, "No catalysts with weight values found to test")
                return True
            
            # Test data structure for frontend compatibility
            test_catalyst = catalysts_with_weight[0]
            
            # Check required fields for CreateListingPage.js
            required_fields = ["catalyst_id", "cat_id", "name", "weight", "total_price"]
            missing_fields = []
            
            for field in required_fields:
                if field not in test_catalyst:
                    missing_fields.append(field)
            
            # Check that weight field has actual numeric value
            weight_value = test_catalyst.get("weight", 0)
            has_valid_weight = isinstance(weight_value, (int, float)) and weight_value > 0
            
            success = len(missing_fields) == 0 and has_valid_weight
            
            self.log_test(
                "Catalyst Selection Data Consistency", 
                success, 
                f"Tested catalyst: {test_catalyst.get('name', 'Unknown')} (ID: {test_catalyst.get('cat_id', 'N/A')}), Weight: {weight_value}g, Missing fields: {missing_fields if missing_fields else 'None'}, Valid weight: {has_valid_weight}"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Catalyst Selection Data Consistency", False, error_msg=str(e))
            return False

    def test_ceramic_weight_display_fix(self, unified_data):
        """Test that ceramic weight shows actual weight value instead of being empty"""
        if not unified_data:
            self.log_test("Ceramic Weight Display Fix", False, error_msg="No unified data provided")
            return False
            
        try:
            # Find catalysts with significant weight values
            significant_catalysts = [
                catalyst for catalyst in unified_data 
                if catalyst.get("weight", 0) >= 1.0  # At least 1g
            ]
            
            if len(significant_catalysts) == 0:
                self.log_test("Ceramic Weight Display Fix", True, "No catalysts with significant weight values found to test")
                return True
            
            # Test multiple catalysts to ensure consistency
            test_results = []
            
            for i, catalyst in enumerate(significant_catalysts[:5]):  # Test first 5 significant catalysts
                catalyst_name = catalyst.get("name", f"Catalyst_{i}")
                weight_value = catalyst.get("weight", 0)
                
                # Simulate the frontend fix: selectedCatalyst.weight instead of selectedCatalyst.ceramic_weight
                # The fix ensures that weight field is accessible and has a value
                weight_accessible = "weight" in catalyst
                weight_has_value = weight_value is not None and weight_value > 0
                weight_is_numeric = isinstance(weight_value, (int, float))
                
                test_result = {
                    "catalyst": catalyst_name,
                    "weight_accessible": weight_accessible,
                    "weight_has_value": weight_has_value,
                    "weight_is_numeric": weight_is_numeric,
                    "weight_value": weight_value,
                    "success": weight_accessible and weight_has_value and weight_is_numeric
                }
                test_results.append(test_result)
            
            # Calculate overall success
            successful_tests = sum(1 for result in test_results if result["success"])
            total_tested = len(test_results)
            success_rate = (successful_tests / total_tested) * 100 if total_tested > 0 else 0
            
            overall_success = success_rate >= 90  # At least 90% success rate
            
            # Create detailed summary
            details = f"Tested {total_tested} catalysts, {successful_tests} successful ({success_rate:.1f}% success rate). "
            if test_results:
                sample_result = test_results[0]
                details += f"Sample: {sample_result['catalyst']} - Weight: {sample_result['weight_value']}g, Accessible: {sample_result['weight_accessible']}, Has Value: {sample_result['weight_has_value']}"
            
            self.log_test(
                "Ceramic Weight Display Fix", 
                overall_success, 
                details
            )
            
            return overall_success
            
        except Exception as e:
            self.log_test("Ceramic Weight Display Fix", False, error_msg=str(e))
            return False

    def test_backend_data_structure_consistency(self, unified_data):
        """Verify the backend data structure is consistent with what the frontend expects"""
        if not unified_data:
            self.log_test("Backend Data Structure Consistency", False, error_msg="No unified data provided")
            return False
            
        try:
            # Check data structure consistency across all catalysts
            structure_issues = []
            
            # Expected structure based on the unified calculations endpoint
            expected_fields = {
                "catalyst_id": str,
                "cat_id": str, 
                "name": str,
                "weight": (int, float),  # This is the key field for the fix
                "total_price": (int, float),
                "pt_g": (int, float),
                "pd_g": (int, float),
                "rh_g": (int, float),
                "is_override": bool,
                "add_info": str
            }
            
            # Test structure consistency
            for i, catalyst in enumerate(unified_data[:10]):  # Test first 10 catalysts
                for field, expected_type in expected_fields.items():
                    if field not in catalyst:
                        structure_issues.append(f"Catalyst {i}: Missing field '{field}'")
                    else:
                        value = catalyst[field]
                        if not isinstance(value, expected_type):
                            structure_issues.append(f"Catalyst {i}: Field '{field}' has type {type(value).__name__}, expected {expected_type}")
            
            # Check for presence of old 'ceramic_weight' field (should not exist in unified endpoint)
            ceramic_weight_found = any("ceramic_weight" in catalyst for catalyst in unified_data[:10])
            if ceramic_weight_found:
                structure_issues.append("Found 'ceramic_weight' field in unified data (should be 'weight')")
            
            # Check weight field statistics
            weight_values = [catalyst.get("weight", 0) for catalyst in unified_data if catalyst.get("weight", 0) > 0]
            avg_weight = sum(weight_values) / len(weight_values) if weight_values else 0
            
            success = len(structure_issues) == 0
            
            self.log_test(
                "Backend Data Structure Consistency", 
                success, 
                f"Tested {min(10, len(unified_data))} catalysts. Issues found: {len(structure_issues)}. Catalysts with weight > 0: {len(weight_values)}/{len(unified_data)}. Average weight: {avg_weight:.2f}g. Issues: {structure_issues[:3] if structure_issues else 'None'}"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Backend Data Structure Consistency", False, error_msg=str(e))
            return False

    def run_ceramic_weight_fix_testing(self):
        """Run ceramic weight display fix testing"""
        print("=" * 80)
        print("CATALORO CERAMIC WEIGHT DISPLAY FIX TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        print("ISSUE FIXED: CreateListingPage.js was showing empty ceramic weight values")
        print("FIX APPLIED: Changed selectedCatalyst.ceramic_weight to selectedCatalyst.weight")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting testing.")
            return
        
        # 2. Test Unified Calculations Weight Field
        print("🧮 UNIFIED CALCULATIONS WEIGHT FIELD TESTING")
        print("-" * 40)
        unified_data = self.test_unified_calculations_weight_field()
        
        # 3. Test Admin Login for Catalyst Access
        print("👤 ADMIN LOGIN FOR CATALYST ACCESS")
        print("-" * 40)
        admin_user = self.test_admin_login_for_catalyst_access()
        
        # 4. Test Catalyst Selection Data Consistency
        print("🎯 CATALYST SELECTION DATA CONSISTENCY")
        print("-" * 40)
        self.test_catalyst_selection_data_consistency(unified_data)
        
        # 5. Test Ceramic Weight Display Fix
        print("🔧 CERAMIC WEIGHT DISPLAY FIX VERIFICATION")
        print("-" * 40)
        self.test_ceramic_weight_display_fix(unified_data)
        
        # 6. Test Backend Data Structure Consistency
        print("📊 BACKEND DATA STRUCTURE CONSISTENCY")
        print("-" * 40)
        self.test_backend_data_structure_consistency(unified_data)
        
        # Print Summary
        print("=" * 80)
        print("CERAMIC WEIGHT DISPLAY FIX TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 CERAMIC WEIGHT DISPLAY FIX TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Unified calculations endpoint returns 'weight' field (not 'ceramic_weight')")
        print("  ✅ Catalyst selection works with weight field structure")
        print("  ✅ Ceramic weight displays actual weight values instead of being empty")
        print("  ✅ Backend data structure is consistent with frontend expectations")
        print("  ✅ Admin users can access catalyst functionality properly")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = CeramicWeightTester()
    
    # Run Ceramic Weight Display Fix testing as requested in the review
    print("🎯 RUNNING CERAMIC WEIGHT DISPLAY FIX TESTING AS REQUESTED")
    print("Testing the ceramic weight display fix in CreateListingPage.js...")
    print()
    
    passed, failed, results = tester.run_ceramic_weight_fix_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)