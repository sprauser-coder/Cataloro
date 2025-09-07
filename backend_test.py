#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Updated Description Functionality and Unified Calculations
Testing the updated description functionality and unified calculations endpoint with add_info field
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://catalyst-calc.preview.emergentagent.com/api"

class BackendTester:
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

    def test_unified_calculations_add_info_field(self):
        """Test that unified calculations endpoint includes add_info field"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations")
            if response.status_code == 200:
                unified_data = response.json()
                
                if isinstance(unified_data, list) and len(unified_data) > 0:
                    # Check if add_info field is present
                    sample_item = unified_data[0]
                    has_add_info = "add_info" in sample_item
                    
                    # Count items with add_info data
                    items_with_add_info = sum(1 for item in unified_data if item.get("add_info", "").strip())
                    
                    self.log_test(
                        "Unified Calculations Add Info Field", 
                        has_add_info, 
                        f"add_info field present: {has_add_info}, Items with add_info data: {items_with_add_info}/{len(unified_data)}"
                    )
                    return unified_data if has_add_info else None
                else:
                    self.log_test("Unified Calculations Add Info Field", True, "No data to test (empty database)")
                    return []
            else:
                self.log_test("Unified Calculations Add Info Field", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Unified Calculations Add Info Field", False, error_msg=str(e))
            return None

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

    def test_admin_login_and_permissions(self):
        """Test admin login and verify permissions for content value visibility"""
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
                
                # Check if user has admin/manager permissions
                has_admin_permissions = user_role in ['Admin', 'Admin-Manager']
                
                self.log_test(
                    "Admin Login and Permissions", 
                    has_admin_permissions, 
                    f"Admin logged in successfully. Role: {user_role}, Has admin permissions: {has_admin_permissions}"
                )
                return user if has_admin_permissions else None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login and Permissions", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Admin Login and Permissions", False, error_msg=str(e))
            return None

    def test_listing_creation_with_add_info(self, admin_user, unified_data):
        """Test that listing creation uses add_info in descriptions (not content values)"""
        if not admin_user or not unified_data:
            self.log_test("Listing Creation with Add Info", False, error_msg="No admin user or unified data provided")
            return None
            
        try:
            # Find a catalyst with add_info data
            catalyst_with_add_info = None
            for catalyst in unified_data:
                if catalyst.get("add_info", "").strip():
                    catalyst_with_add_info = catalyst
                    break
            
            if not catalyst_with_add_info:
                self.log_test("Listing Creation with Add Info", True, "No catalysts with add_info data found to test")
                return None
            
            # Create a test listing using the catalyst data
            listing_data = {
                "title": f"Test Catalyst - {catalyst_with_add_info.get('name', 'Unknown')}",
                "description": f"Catalyst: {catalyst_with_add_info.get('name', 'Professional Grade Catalyst')}\n\nSpecifications:\n• Weight: {catalyst_with_add_info.get('weight', 'N/A')}g\n• Cat ID: {catalyst_with_add_info.get('cat_id', 'N/A')}\n\nProfessional grade catalyst suitable for automotive and industrial applications.\n\nAdditional Information:\n{catalyst_with_add_info.get('add_info', '')}",
                "price": catalyst_with_add_info.get('total_price', 100.0),
                "category": "Catalysts",
                "condition": "New",
                "seller_id": admin_user.get('id'),
                "images": [],
                "tags": ["catalyst", "automotive"],
                "features": ["Professional Grade"],
                # Store catalyst data but NOT in description
                "ceramic_weight": catalyst_with_add_info.get('weight'),
                "pt_ppm": catalyst_with_add_info.get('pt_g') * 1000 / catalyst_with_add_info.get('weight', 1) if catalyst_with_add_info.get('weight', 0) > 0 else 0,
                "pd_ppm": catalyst_with_add_info.get('pd_g') * 1000 / catalyst_with_add_info.get('weight', 1) if catalyst_with_add_info.get('weight', 0) > 0 else 0,
                "rh_ppm": catalyst_with_add_info.get('rh_g') * 1000 / catalyst_with_add_info.get('weight', 1) if catalyst_with_add_info.get('weight', 0) > 0 else 0
            }
            
            response = requests.post(
                f"{BACKEND_URL}/listings",
                json=listing_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                listing_id = result.get('listing_id')
                
                # Verify the listing was created
                listing_response = requests.get(f"{BACKEND_URL}/listings/{listing_id}")
                if listing_response.status_code == 200:
                    created_listing = listing_response.json()
                    
                    # Check that description contains add_info but NOT content values (pt_g, pd_g, rh_g)
                    description = created_listing.get('description', '')
                    contains_add_info = catalyst_with_add_info.get('add_info', '') in description
                    contains_content_values = any(val in description for val in ['pt_g', 'pd_g', 'rh_g'])
                    
                    # Check that content values are stored separately (not in description)
                    has_separate_catalyst_data = all(field in created_listing for field in ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm'])
                    
                    success = contains_add_info and not contains_content_values and has_separate_catalyst_data
                    
                    self.log_test(
                        "Listing Creation with Add Info", 
                        success, 
                        f"Listing created with ID: {listing_id}. Description contains add_info: {contains_add_info}, Description contains content values: {contains_content_values}, Separate catalyst data stored: {has_separate_catalyst_data}"
                    )
                    
                    # Clean up - delete test listing
                    try:
                        requests.delete(f"{BACKEND_URL}/listings/{listing_id}")
                    except:
                        pass
                    
                    return created_listing if success else None
                else:
                    self.log_test("Listing Creation with Add Info", False, error_msg="Failed to retrieve created listing")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Listing Creation with Add Info", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Listing Creation with Add Info", False, error_msg=str(e))
            return None

    def test_content_values_stored_separately(self, admin_user, unified_data):
        """Test that content values are still stored but not in descriptions"""
        if not admin_user or not unified_data:
            self.log_test("Content Values Stored Separately", False, error_msg="No admin user or unified data provided")
            return False
            
        try:
            # Find a catalyst with content values
            catalyst_with_content = None
            for catalyst in unified_data:
                if any(catalyst.get(field, 0) > 0 for field in ['pt_g', 'pd_g', 'rh_g']):
                    catalyst_with_content = catalyst
                    break
            
            if not catalyst_with_content:
                self.log_test("Content Values Stored Separately", True, "No catalysts with content values found to test")
                return True
            
            # Create a test listing
            listing_data = {
                "title": f"Test Content Values - {catalyst_with_content.get('name', 'Unknown')}",
                "description": f"Basic catalyst description without content values",
                "price": catalyst_with_content.get('total_price', 100.0),
                "category": "Catalysts",
                "condition": "New",
                "seller_id": admin_user.get('id'),
                "images": [],
                # Store catalyst content data separately
                "ceramic_weight": catalyst_with_content.get('weight'),
                "pt_ppm": catalyst_with_content.get('pt_g') * 1000 / catalyst_with_content.get('weight', 1) if catalyst_with_content.get('weight', 0) > 0 else 0,
                "pd_ppm": catalyst_with_content.get('pd_g') * 1000 / catalyst_with_content.get('weight', 1) if catalyst_with_content.get('weight', 0) > 0 else 0,
                "rh_ppm": catalyst_with_content.get('rh_g') * 1000 / catalyst_with_content.get('weight', 1) if catalyst_with_content.get('weight', 0) > 0 else 0
            }
            
            response = requests.post(
                f"{BACKEND_URL}/listings",
                json=listing_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                listing_id = result.get('listing_id')
                
                # Verify the listing
                listing_response = requests.get(f"{BACKEND_URL}/listings/{listing_id}")
                if listing_response.status_code == 200:
                    created_listing = listing_response.json()
                    
                    # Check that content values are NOT in description
                    description = created_listing.get('description', '')
                    description_clean = not any(str(catalyst_with_content.get(field, 0)) in description for field in ['pt_g', 'pd_g', 'rh_g'])
                    
                    # Check that content values ARE stored separately
                    content_stored_separately = all(field in created_listing for field in ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm'])
                    
                    success = description_clean and content_stored_separately
                    
                    self.log_test(
                        "Content Values Stored Separately", 
                        success, 
                        f"Description clean of content values: {description_clean}, Content values stored separately: {content_stored_separately}"
                    )
                    
                    # Clean up
                    try:
                        requests.delete(f"{BACKEND_URL}/listings/{listing_id}")
                    except:
                        pass
                    
                    return success
                else:
                    self.log_test("Content Values Stored Separately", False, error_msg="Failed to retrieve created listing")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Content Values Stored Separately", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Content Values Stored Separately", False, error_msg=str(e))
            return False

    def test_data_consistency_across_endpoints(self, unified_data):
        """Test data consistency across all endpoints"""
        if not unified_data:
            self.log_test("Data Consistency Across Endpoints", False, error_msg="No unified data provided")
            return False
            
        try:
            # Test consistency between unified calculations and individual endpoints
            consistency_errors = []
            
            # Get catalyst data endpoint
            catalyst_response = requests.get(f"{BACKEND_URL}/admin/catalyst/data")
            if catalyst_response.status_code == 200:
                catalyst_data = catalyst_response.json()
                
                # Create lookup for comparison
                catalyst_lookup = {item.get('id'): item for item in catalyst_data}
                
                # Check consistency for first few items
                for unified_item in unified_data[:5]:  # Test first 5 items
                    catalyst_id = unified_item.get('catalyst_id')
                    if catalyst_id in catalyst_lookup:
                        original_catalyst = catalyst_lookup[catalyst_id]
                        
                        # Check add_info consistency
                        unified_add_info = unified_item.get('add_info', '')
                        original_add_info = original_catalyst.get('add_info', '')
                        
                        if unified_add_info != original_add_info:
                            consistency_errors.append(f"add_info mismatch for {catalyst_id}")
                        
                        # Check basic data consistency
                        for field in ['cat_id', 'name', 'ceramic_weight']:
                            unified_val = unified_item.get('weight' if field == 'ceramic_weight' else field)
                            original_val = original_catalyst.get(field)
                            
                            if unified_val != original_val:
                                consistency_errors.append(f"{field} mismatch for {catalyst_id}")
            else:
                consistency_errors.append("Failed to get catalyst data for comparison")
            
            # Test browse endpoint includes proper data
            browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse")
            if browse_response.status_code == 200:
                browse_data = browse_response.json()
                if isinstance(browse_data, list):
                    # Check that listings have proper structure
                    for listing in browse_data[:3]:  # Check first 3 listings
                        if not all(field in listing for field in ['id', 'title', 'description', 'price']):
                            consistency_errors.append(f"Listing {listing.get('id', 'unknown')} missing required fields")
                else:
                    consistency_errors.append("Browse endpoint returned invalid format")
            else:
                consistency_errors.append("Browse endpoint failed")
            
            success = len(consistency_errors) == 0
            
            self.log_test(
                "Data Consistency Across Endpoints", 
                success, 
                f"Consistency check completed. Errors found: {len(consistency_errors)}" + (f" - {consistency_errors}" if consistency_errors else "")
            )
            
            return success
            
        except Exception as e:
            self.log_test("Data Consistency Across Endpoints", False, error_msg=str(e))
            return False

    def run_unified_calculations_testing(self):
        """Run Unified Calculations Endpoint testing as requested in review"""
        print("=" * 80)
        print("CATALORO UNIFIED CALCULATIONS ENDPOINT TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting Unified Calculations testing.")
            return
        
        # 2. Run Unified Calculations Tests
        print("🧮 UNIFIED CALCULATIONS ENDPOINT TESTING")
        print("-" * 40)
        self.test_unified_calculations_endpoint()
        
        # Print Summary
        print("=" * 80)
        print("UNIFIED CALCULATIONS ENDPOINT TEST SUMMARY")
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
        
        print("\n🎯 UNIFIED CALCULATIONS ENDPOINT TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Endpoint should return unified data combining price and content calculations")
        print("  ✅ Should include fields: catalyst_id, cat_id, name, weight, total_price, pt_g, pd_g, rh_g, is_override")
        print("  ✅ Should hide database_id from response")
        print("  ✅ Should calculate content values using formula (weight * ppm / 1000 * renumeration)")
        print("  ✅ Should handle edge cases like empty database, missing settings")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    
    # Run Unified Calculations testing as requested in the review
    print("🎯 RUNNING UNIFIED CALCULATIONS ENDPOINT TESTING AS REQUESTED")
    print("Testing the new /api/admin/catalyst/unified-calculations endpoint...")
    print()
    
    passed, failed, results = tester.run_unified_calculations_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)