#!/usr/bin/env python3
"""
CATALORO - Unified Calculations Endpoint Testing
Testing the updated listing creation process with unified calculations
"""

import requests
import json
import uuid
import time
from datetime import datetime
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://marketplace-central.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class UnifiedCalculationsTest:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.demo_user = None
        self.created_listing_id = None
        
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

    def get_demo_user(self):
        """Get demo user for testing"""
        try:
            # Login as demo user to get user ID
            login_data = {
                "email": "demo@cataloro.com",
                "password": "demo123"
            }
            
            response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=30)
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                self.demo_user = user
                self.log_test(
                    "Demo User Login", 
                    True, 
                    f"Successfully logged in demo user: {user.get('username', 'Unknown')}"
                )
                return user
            else:
                self.log_test("Demo User Login", False, f"Login failed with status {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Demo User Login", False, error_msg=f"Login error: {str(e)}")
            return None

    def test_unified_calculations_endpoint_access(self):
        """Test 1: Unified endpoint integration - Access unified calculations endpoint"""
        try:
            response = requests.get(f"{API_BASE}/admin/catalyst/unified-calculations", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    sample_item = data[0]
                    self.log_test(
                        "Unified Calculations Endpoint Access",
                        True,
                        f"Successfully accessed endpoint, found {len(data)} catalyst entries. Sample structure: {list(sample_item.keys()) if sample_item else []}"
                    )
                    return data
                else:
                    self.log_test(
                        "Unified Calculations Endpoint Access",
                        False,
                        f"Endpoint returned empty or invalid data. Type: {type(data).__name__}, Length: {len(data) if isinstance(data, list) else 'N/A'}"
                    )
                    return []
            else:
                self.log_test(
                    "Unified Calculations Endpoint Access",
                    False,
                    f"Endpoint returned status {response.status_code}"
                )
                return []
                
        except Exception as e:
            self.log_test(
                "Unified Calculations Endpoint Access",
                False,
                error_msg=f"Failed to access endpoint: {str(e)}"
            )
            return []

    def test_catalyst_search_functionality(self, unified_data):
        """Test 2: Catalyst search - Verify catalysts can be found from unified calculations"""
        try:
            if not unified_data:
                self.log_test(
                    "Catalyst Search Functionality",
                    False,
                    "No unified data available for search testing"
                )
                return None
                
            # Test search functionality by looking for catalysts with different criteria
            search_results = {
                "by_name": 0,
                "by_cat_id": 0,
                "with_content": 0,
                "sample_names": [],
                "sample_cat_ids": []
            }
            
            # Analyze search capabilities
            for catalyst in unified_data[:20]:  # Test first 20 items
                name = catalyst.get('name', '')
                cat_id = catalyst.get('cat_id', '')
                
                if name and len(name) > 3:
                    search_results["by_name"] += 1
                    if len(search_results["sample_names"]) < 3:
                        search_results["sample_names"].append(name)
                        
                if cat_id:
                    search_results["by_cat_id"] += 1
                    if len(search_results["sample_cat_ids"]) < 3:
                        search_results["sample_cat_ids"].append(cat_id)
                        
                # Check for content data
                if (catalyst.get('pt_g') is not None and catalyst.get('pt_g') > 0) or \
                   (catalyst.get('pd_g') is not None and catalyst.get('pd_g') > 0):
                    search_results["with_content"] += 1
                    
            success = (search_results["by_name"] > 0 and 
                      search_results["by_cat_id"] > 0 and 
                      search_results["with_content"] > 0)
                      
            self.log_test(
                "Catalyst Search Functionality",
                success,
                f"Search analysis: {search_results['by_name']} searchable names, {search_results['by_cat_id']} cat IDs, {search_results['with_content']} with content data. Samples: {search_results['sample_names'][:2]}"
            )
            
            # Return a sample catalyst for further testing
            return unified_data[0] if unified_data else None
            
        except Exception as e:
            self.log_test(
                "Catalyst Search Functionality",
                False,
                error_msg=f"Search functionality test failed: {str(e)}"
            )
            return None

    def test_data_structure_completeness(self, unified_data):
        """Test 3: Data structure - Verify comprehensive data includes all required fields"""
        try:
            if not unified_data:
                self.log_test(
                    "Data Structure Completeness",
                    False,
                    "No unified data available for structure testing"
                )
                return False
                
            required_fields = ['cat_id', 'name', 'weight', 'total_price', 'pt_g', 'pd_g', 'rh_g']
            field_analysis = {}
            
            for field in required_fields:
                present_count = sum(1 for item in unified_data if field in item and item[field] is not None)
                field_analysis[field] = {
                    "present": present_count,
                    "percentage": (present_count / len(unified_data) * 100) if unified_data else 0
                }
                
            # Check completeness - require at least 80% presence for each field
            all_fields_good = all(analysis["percentage"] >= 80 for analysis in field_analysis.values())
            
            details = f"Field completeness analysis for {len(unified_data)} items: " + \
                     ", ".join([f"{field}: {analysis['percentage']:.1f}%" for field, analysis in field_analysis.items()])
                     
            self.log_test(
                "Data Structure Completeness",
                all_fields_good,
                details
            )
            
            return all_fields_good
            
        except Exception as e:
            self.log_test(
                "Data Structure Completeness",
                False,
                error_msg=f"Data structure test failed: {str(e)}"
            )
            return False

    def test_listing_creation_with_catalyst(self, sample_catalyst):
        """Test 4: Listing creation - Test creating listing with catalyst selection"""
        try:
            if not sample_catalyst or not self.demo_user:
                self.log_test(
                    "Listing Creation with Catalyst",
                    False,
                    "Missing sample catalyst or user data for listing creation test"
                )
                return None
                
            # Create comprehensive listing data with catalyst information
            listing_data = {
                "title": f"Test Unified Catalyst - {sample_catalyst.get('name', 'Unknown')}",
                "description": f"Professional grade catalyst: {sample_catalyst.get('name', 'Unknown')}\n\nSpecifications:\n• Weight: {sample_catalyst.get('weight', 'N/A')}g\n• Pt content: {sample_catalyst.get('pt_g', 'N/A')}g\n• Pd content: {sample_catalyst.get('pd_g', 'N/A')}g\n• Rh content: {sample_catalyst.get('rh_g', 'N/A')}g",
                "price": float(sample_catalyst.get('total_price', 100.0)),
                "category": "Catalysts",
                "condition": "New",
                "seller_id": self.demo_user.get('id'),
                "tags": ["catalyst", "automotive", "professional"],
                "features": ["high-grade", "certified"],
                "street": "Test Street 123",
                "post_code": "12345",
                "city": "Test City",
                "country": "Germany",
                "shipping": "pickup",
                "shipping_cost": 0,
                "has_time_limit": False,
                # Comprehensive catalyst data from unified calculations
                "catalyst_id": sample_catalyst.get('cat_id'),
                "catalyst_name": sample_catalyst.get('name'),
                "is_catalyst_listing": True,
                "calculated_price": sample_catalyst.get('total_price'),
                # Weight data
                "ceramic_weight": sample_catalyst.get('weight'),
                # Content calculations (Pt g, Pd g, Rh g)
                "pt_g": sample_catalyst.get('pt_g'),
                "pd_g": sample_catalyst.get('pd_g'),
                "rh_g": sample_catalyst.get('rh_g'),
                # Store comprehensive catalyst specs for inventory management
                "catalyst_specs": {
                    "weight": sample_catalyst.get('weight'),
                    "total_price": sample_catalyst.get('total_price'),
                    "pt_g": sample_catalyst.get('pt_g'),
                    "pd_g": sample_catalyst.get('pd_g'),
                    "rh_g": sample_catalyst.get('rh_g'),
                    "is_override": sample_catalyst.get('is_override', False)
                }
            }
            
            response = requests.post(f"{API_BASE}/listings", json=listing_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self.created_listing_id = result.get('listing_id')
                
                catalyst_fields_included = {
                    "catalyst_id": listing_data.get('catalyst_id'),
                    "weight": listing_data.get('ceramic_weight'),
                    "pt_g": listing_data.get('pt_g'),
                    "pd_g": listing_data.get('pd_g'),
                    "rh_g": listing_data.get('rh_g'),
                    "total_price": listing_data.get('calculated_price')
                }
                
                self.log_test(
                    "Listing Creation with Catalyst",
                    True,
                    f"Successfully created listing with comprehensive catalyst data. Listing ID: {self.created_listing_id}. Catalyst fields: {catalyst_fields_included}"
                )
                return result
            else:
                self.log_test(
                    "Listing Creation with Catalyst",
                    False,
                    f"Failed to create listing. Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Listing Creation with Catalyst",
                False,
                error_msg=f"Listing creation test failed: {str(e)}"
            )
            return None

    def test_inventory_readiness(self):
        """Test 5: Inventory readiness - Verify saved listing has all fields for inventory management"""
        try:
            if not self.created_listing_id:
                self.log_test(
                    "Inventory Readiness Verification",
                    False,
                    "No created listing available for inventory readiness testing"
                )
                return False
                
            # Retrieve the created listing to verify data persistence
            response = requests.get(f"{API_BASE}/listings/{self.created_listing_id}", timeout=30)
            
            if response.status_code == 200:
                listing = response.json()
                
                # Check for inventory management fields
                inventory_fields = {
                    "catalyst_id": listing.get('catalyst_id'),
                    "catalyst_name": listing.get('catalyst_name'),
                    "ceramic_weight": listing.get('ceramic_weight'),
                    "pt_g": listing.get('pt_g'),
                    "pd_g": listing.get('pd_g'),
                    "rh_g": listing.get('rh_g'),
                    "calculated_price": listing.get('calculated_price'),
                    "catalyst_specs": listing.get('catalyst_specs'),
                    "is_catalyst_listing": listing.get('is_catalyst_listing')
                }
                
                # Analyze field completeness
                present_fields = {k: v for k, v in inventory_fields.items() if v is not None}
                missing_fields = [k for k, v in inventory_fields.items() if v is None]
                
                completeness_percentage = (len(present_fields) / len(inventory_fields)) * 100
                is_ready = completeness_percentage >= 80  # 80% threshold for readiness
                
                self.log_test(
                    "Inventory Readiness Verification",
                    is_ready,
                    f"Inventory readiness: {len(present_fields)}/{len(inventory_fields)} fields present ({completeness_percentage:.1f}%). Present: {list(present_fields.keys())}. Missing: {missing_fields}"
                )
                
                return is_ready
            else:
                self.log_test(
                    "Inventory Readiness Verification",
                    False,
                    f"Failed to retrieve created listing. Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Inventory Readiness Verification",
                False,
                error_msg=f"Inventory readiness test failed: {str(e)}"
            )
            return False

    def run_unified_calculations_tests(self):
        """Run all unified calculations tests"""
        print("🧪 CATALORO - Unified Calculations Endpoint Testing")
        print("=" * 80)
        print("Testing the updated listing creation process with unified calculations")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Get demo user
        user = self.get_demo_user()
        
        # Test 1: Access unified calculations endpoint
        unified_data = self.test_unified_calculations_endpoint_access()
        
        # Test 2: Verify catalyst search functionality
        sample_catalyst = self.test_catalyst_search_functionality(unified_data)
        
        # Test 3: Verify data structure completeness
        self.test_data_structure_completeness(unified_data)
        
        # Test 4: Test listing creation with catalyst selection
        self.test_listing_creation_with_catalyst(sample_catalyst)
        
        # Test 5: Verify inventory readiness
        self.test_inventory_readiness()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test in [r for r in self.test_results if "❌ FAIL" in r["status"]]:
                print(f"  • {test['test']}: {test.get('error', test.get('details', 'Unknown error'))}")
                
        print("\n✅ PASSED TESTS:")
        for test in [r for r in self.test_results if "✅ PASS" in r["status"]]:
            print(f"  • {test['test']}")
            
        return self.failed_tests == 0

if __name__ == "__main__":
    """Main test execution"""
    tester = UnifiedCalculationsTest()
    success = tester.run_unified_calculations_tests()
    
    if success:
        print("\n🎉 All tests passed! Unified calculations endpoint is working correctly.")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the results above.")
        exit(1)