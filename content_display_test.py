#!/usr/bin/env python3
"""
Cataloro Content Display Functionality Testing Suite
Testing content display functionality end-to-end as requested in review
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://enterprise-market.preview.emergentagent.com/api"

class ContentDisplayTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.found_catalysts = []
        self.admin_user = None
        
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

    def test_admin_login(self):
        """Test admin login for permissions"""
        try:
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
                    "Admin Login", 
                    has_admin_permissions, 
                    f"Admin logged in successfully. Role: {user_role}, User ID: {user_id}, Has admin permissions: {has_admin_permissions}"
                )
                
                if has_admin_permissions:
                    self.admin_user = user
                    return user
                return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Admin Login", False, error_msg=str(e))
            return None

    def test_find_catalysts_with_significant_content(self):
        """Find catalysts with significant content values (Pt g > 0.1, Pd g > 0.1, Rh g > 0.1)"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations", timeout=15)
            
            if response.status_code == 200:
                unified_data = response.json()
                
                if isinstance(unified_data, list) and len(unified_data) > 0:
                    # Find catalysts with significant content values
                    significant_catalysts = []
                    
                    for catalyst in unified_data:
                        pt_g = catalyst.get('pt_g', 0)
                        pd_g = catalyst.get('pd_g', 0) 
                        rh_g = catalyst.get('rh_g', 0)
                        weight = catalyst.get('weight', 0)
                        
                        # Check criteria: significant precious metal content AND reasonable weight
                        has_significant_content = (pt_g > 0.1 or pd_g > 0.1 or rh_g > 0.1) and weight > 0.5
                        
                        if has_significant_content:
                            catalyst_details = {
                                "cat_id": catalyst.get('cat_id'),
                                "name": catalyst.get('name'),
                                "weight": weight,
                                "total_price": catalyst.get('total_price'),
                                "pt_g": pt_g,
                                "pd_g": pd_g,
                                "rh_g": rh_g,
                                "add_info": catalyst.get('add_info', ''),
                                "catalyst_id": catalyst.get('catalyst_id')
                            }
                            significant_catalysts.append(catalyst_details)
                    
                    # Sort by total precious metal content (highest first)
                    significant_catalysts.sort(key=lambda x: x['pt_g'] + x['pd_g'] + x['rh_g'], reverse=True)
                    
                    # Keep top 10 for testing
                    self.found_catalysts = significant_catalysts[:10]
                    
                    self.log_test(
                        "Find Catalysts with Significant Content", 
                        len(significant_catalysts) > 0, 
                        f"Found {len(significant_catalysts)} catalysts with significant content values. Top catalyst: {significant_catalysts[0]['name'] if significant_catalysts else 'None'} (Pt: {significant_catalysts[0]['pt_g']:.3f}g, Pd: {significant_catalysts[0]['pd_g']:.3f}g, Rh: {significant_catalysts[0]['rh_g']:.3f}g)" if significant_catalysts else "No catalysts found with significant content"
                    )
                    
                    return significant_catalysts
                else:
                    self.log_test("Find Catalysts with Significant Content", False, "No unified data available")
                    return []
            else:
                self.log_test("Find Catalysts with Significant Content", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Find Catalysts with Significant Content", False, error_msg=str(e))
            return []

    def test_unified_calculations_access(self):
        """Test access to unified calculations endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations", timeout=15)
            
            if response.status_code == 200:
                unified_data = response.json()
                
                if isinstance(unified_data, list):
                    total_entries = len(unified_data)
                    
                    # Check data completeness
                    complete_entries = 0
                    for item in unified_data:
                        required_fields = ['catalyst_id', 'cat_id', 'name', 'weight', 'total_price', 'pt_g', 'pd_g', 'rh_g']
                        if all(field in item for field in required_fields):
                            complete_entries += 1
                    
                    completeness_rate = (complete_entries / total_entries * 100) if total_entries > 0 else 0
                    
                    self.log_test(
                        "Unified Calculations Access", 
                        True, 
                        f"Successfully accessed unified calculations. Total entries: {total_entries}, Complete entries: {complete_entries}, Completeness: {completeness_rate:.1f}%"
                    )
                    return unified_data
                else:
                    self.log_test("Unified Calculations Access", False, "Invalid data format returned")
                    return None
            else:
                self.log_test("Unified Calculations Access", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Unified Calculations Access", False, error_msg=str(e))
            return None

    def test_admin_content_visibility(self, catalyst):
        """Test that Admin users can see content values"""
        if not self.admin_user or not catalyst:
            self.log_test("Admin Content Visibility", False, error_msg="No admin user or catalyst provided")
            return False
            
        try:
            # Admin should be able to see content values in unified calculations
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations", timeout=10)
            
            if response.status_code == 200:
                unified_data = response.json()
                
                # Find our test catalyst
                test_catalyst = None
                for item in unified_data:
                    if item.get('catalyst_id') == catalyst.get('catalyst_id'):
                        test_catalyst = item
                        break
                
                if test_catalyst:
                    # Check that admin can see content values
                    has_content_values = all(field in test_catalyst for field in ['pt_g', 'pd_g', 'rh_g'])
                    content_values_visible = any(test_catalyst.get(field, 0) > 0 for field in ['pt_g', 'pd_g', 'rh_g'])
                    
                    self.log_test(
                        "Admin Content Visibility", 
                        has_content_values and content_values_visible, 
                        f"Admin can see content values: {has_content_values}, Content values present: {content_values_visible}. Pt: {test_catalyst.get('pt_g', 0):.3f}g, Pd: {test_catalyst.get('pd_g', 0):.3f}g, Rh: {test_catalyst.get('rh_g', 0):.3f}g"
                    )
                    return has_content_values and content_values_visible
                else:
                    self.log_test("Admin Content Visibility", False, error_msg="Test catalyst not found in unified data")
                    return False
            else:
                self.log_test("Admin Content Visibility", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Content Visibility", False, error_msg=str(e))
            return False

    def test_create_listing_with_catalyst(self, catalyst):
        """Create a test listing with comprehensive catalyst data"""
        if not self.admin_user or not catalyst:
            self.log_test("Create Listing with Catalyst", False, error_msg="No admin user or catalyst provided")
            return None
            
        try:
            # Calculate PPM values from grams
            weight = catalyst.get('weight', 1)
            pt_ppm = (catalyst.get('pt_g', 0) * 1000000) / weight if weight > 0 else 0
            pd_ppm = (catalyst.get('pd_g', 0) * 1000000) / weight if weight > 0 else 0
            rh_ppm = (catalyst.get('rh_g', 0) * 1000000) / weight if weight > 0 else 0
            
            # Create comprehensive listing data
            listing_data = {
                "title": f"Premium Catalyst - {catalyst.get('name', 'Professional Grade')}",
                "description": f"Professional grade automotive catalyst converter.\n\nCatalyst Details:\n• Name: {catalyst.get('name', 'N/A')}\n• Cat ID: {catalyst.get('cat_id', 'N/A')}\n• Weight: {weight}g\n\nThis catalyst is suitable for automotive and industrial applications.\n\nAdditional Information:\n{catalyst.get('add_info', 'Professional grade catalyst with verified specifications.')}",
                "price": catalyst.get('total_price', 150.0),
                "category": "Catalysts",
                "condition": "Used - Good",
                "seller_id": self.admin_user.get('id'),
                "images": [],
                "tags": ["catalyst", "automotive", "converter"],
                "features": ["Professional Grade", "Verified Content"],
                # Comprehensive catalyst data for calculations
                "ceramic_weight": weight,
                "pt_ppm": pt_ppm,
                "pd_ppm": pd_ppm,
                "rh_ppm": rh_ppm,
                # Additional catalyst specifications for inventory management
                "catalyst_specs": {
                    "cat_id": catalyst.get('cat_id'),
                    "name": catalyst.get('name'),
                    "pt_g": catalyst.get('pt_g'),
                    "pd_g": catalyst.get('pd_g'),
                    "rh_g": catalyst.get('rh_g'),
                    "total_price": catalyst.get('total_price'),
                    "add_info": catalyst.get('add_info'),
                    "catalyst_id": catalyst.get('catalyst_id')
                }
            }
            
            response = requests.post(
                f"{BACKEND_URL}/listings",
                json=listing_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                listing_id = result.get('listing_id')
                
                # Verify the listing was created with all data
                listing_response = requests.get(f"{BACKEND_URL}/listings/{listing_id}")
                if listing_response.status_code == 200:
                    created_listing = listing_response.json()
                    
                    # Check comprehensive data saving
                    has_catalyst_fields = all(field in created_listing for field in ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm'])
                    has_catalyst_specs = 'catalyst_specs' in created_listing
                    description_uses_add_info = catalyst.get('add_info', '') in created_listing.get('description', '') if catalyst.get('add_info') else True
                    
                    # Check that content values are NOT in description (proper separation)
                    description = created_listing.get('description', '')
                    content_values_in_desc = any(f"{catalyst.get(field, 0):.3f}" in description for field in ['pt_g', 'pd_g', 'rh_g'])
                    
                    success = has_catalyst_fields and has_catalyst_specs and description_uses_add_info and not content_values_in_desc
                    
                    self.log_test(
                        "Create Listing with Catalyst", 
                        success, 
                        f"Listing created with ID: {listing_id}. Catalyst fields: {has_catalyst_fields}, Catalyst specs: {has_catalyst_specs}, Description uses add_info: {description_uses_add_info}, Content values NOT in description: {not content_values_in_desc}"
                    )
                    
                    return {
                        "listing_id": listing_id,
                        "listing": created_listing,
                        "catalyst": catalyst,
                        "success": success
                    }
                else:
                    self.log_test("Create Listing with Catalyst", False, error_msg="Failed to retrieve created listing")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Listing with Catalyst", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Create Listing with Catalyst", False, error_msg=str(e))
            return None

    def test_listing_browse_verification(self, listing_result):
        """Verify listing appears in browse with catalyst data intact"""
        if not listing_result:
            self.log_test("Listing Browse Verification", False, error_msg="No listing result provided")
            return False
            
        try:
            listing_id = listing_result.get('listing_id')
            
            # Check browse endpoint
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                browse_listings = response.json()
                
                # Find our listing in browse results
                found_listing = None
                for listing in browse_listings:
                    if listing.get('id') == listing_id:
                        found_listing = listing
                        break
                
                if found_listing:
                    # Check that catalyst data is preserved
                    has_catalyst_data = all(field in found_listing for field in ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm'])
                    has_seller_info = 'seller' in found_listing
                    has_bid_info = 'bid_info' in found_listing
                    
                    self.log_test(
                        "Listing Browse Verification", 
                        has_catalyst_data and has_seller_info and has_bid_info, 
                        f"Listing found in browse. Catalyst data: {has_catalyst_data}, Seller info: {has_seller_info}, Bid info: {has_bid_info}"
                    )
                    return has_catalyst_data and has_seller_info and has_bid_info
                else:
                    self.log_test("Listing Browse Verification", False, error_msg="Listing not found in browse results")
                    return False
            else:
                self.log_test("Listing Browse Verification", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Listing Browse Verification", False, error_msg=str(e))
            return False

    def cleanup_test_listing(self, listing_id):
        """Clean up test listing"""
        try:
            if listing_id:
                requests.delete(f"{BACKEND_URL}/listings/{listing_id}")
                print(f"🧹 Cleaned up test listing: {listing_id}")
        except:
            pass

    def run_content_display_testing(self):
        """Run comprehensive content display functionality testing"""
        print("=" * 80)
        print("CATALORO CONTENT DISPLAY FUNCTIONALITY TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting testing.")
            return
        
        # 2. Admin Login
        print("👤 ADMIN LOGIN")
        print("-" * 40)
        admin_user = self.test_admin_login()
        if not admin_user:
            print("❌ Admin login failed. Aborting testing.")
            return
        
        # 3. Access Unified Calculations
        print("🧮 UNIFIED CALCULATIONS ACCESS")
        print("-" * 40)
        unified_data = self.test_unified_calculations_access()
        
        # 4. Find Catalysts with Significant Content
        print("🔍 FIND CATALYSTS WITH SIGNIFICANT CONTENT")
        print("-" * 40)
        significant_catalysts = self.test_find_catalysts_with_significant_content()
        
        if not significant_catalysts:
            print("❌ No catalysts with significant content found. Cannot continue testing.")
            return
        
        # Use the best catalyst for testing
        test_catalyst = significant_catalysts[0]
        print(f"🎯 Using test catalyst: {test_catalyst['name']} (Cat ID: {test_catalyst['cat_id']})")
        print(f"   Content: Pt={test_catalyst['pt_g']:.3f}g, Pd={test_catalyst['pd_g']:.3f}g, Rh={test_catalyst['rh_g']:.3f}g")
        print(f"   Weight: {test_catalyst['weight']}g, Price: €{test_catalyst['total_price']}")
        print()
        
        # 5. Test Admin Content Visibility
        print("👁️ ADMIN CONTENT VISIBILITY")
        print("-" * 40)
        self.test_admin_content_visibility(test_catalyst)
        
        # 6. Create Test Listing
        print("📝 CREATE TEST LISTING WITH CATALYST")
        print("-" * 40)
        listing_result = self.test_create_listing_with_catalyst(test_catalyst)
        
        # 7. Verify Listing in Browse
        print("🌐 LISTING BROWSE VERIFICATION")
        print("-" * 40)
        self.test_listing_browse_verification(listing_result)
        
        # Clean up
        if listing_result:
            self.cleanup_test_listing(listing_result.get('listing_id'))
        
        # Print Summary
        print("=" * 80)
        print("CONTENT DISPLAY FUNCTIONALITY TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Return catalyst details for frontend testing
        if significant_catalysts:
            print("🎯 CATALYST DETAILS FOR FRONTEND TESTING:")
            print("-" * 50)
            for i, catalyst in enumerate(significant_catalysts[:3], 1):
                print(f"{i}. {catalyst['name']} (Cat ID: {catalyst['cat_id']})")
                print(f"   Weight: {catalyst['weight']}g")
                print(f"   Content: Pt={catalyst['pt_g']:.3f}g, Pd={catalyst['pd_g']:.3f}g, Rh={catalyst['rh_g']:.3f}g")
                print(f"   Price: €{catalyst['total_price']}")
                print(f"   Catalyst ID: {catalyst['catalyst_id']}")
                print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 CONTENT DISPLAY FUNCTIONALITY TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results, significant_catalysts

if __name__ == "__main__":
    tester = ContentDisplayTester()
    
    print("🎯 RUNNING CONTENT DISPLAY FUNCTIONALITY TESTING AS REQUESTED")
    print("Testing content display functionality end-to-end...")
    print()
    
    passed, failed, results, catalysts = tester.run_content_display_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)