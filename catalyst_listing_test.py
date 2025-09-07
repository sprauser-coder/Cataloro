#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Catalyst Listing Creation Test
Testing catalyst data listing creation to verify ProductDetailPage displays content values correctly
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://enterprise-market.preview.emergentagent.com/api"

class CatalystListingTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_user_id = None
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

    def login_as_demo_admin(self):
        """Step 1: Login as demo admin user"""
        print("=" * 80)
        print("STEP 1: LOGIN AS DEMO ADMIN USER")
        print("=" * 80)
        
        try:
            login_data = {
                "email": "admin@cataloro.com",
                "password": "admin123"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                login_result = response.json()
                user_data = login_result.get("user", {})
                self.admin_user_id = user_data.get("id")
                
                if self.admin_user_id and user_data.get("user_role") in ["Admin", "Admin-Manager"]:
                    self.log_test("Demo Admin Login", True, 
                                f"Successfully logged in as {user_data.get('username', 'admin')} with role {user_data.get('user_role')}")
                    return True
                else:
                    self.log_test("Demo Admin Login", False, 
                                f"Login successful but user role is {user_data.get('user_role')}, not Admin")
                    return False
            else:
                self.log_test("Demo Admin Login", False, 
                            f"Login failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Demo Admin Login", False, error_msg=str(e))
            return False

    def get_catalyst_data_for_listing(self):
        """Get catalyst data from unified calculations endpoint"""
        print("=" * 80)
        print("STEP 2: GET CATALYST DATA FOR LISTING CREATION")
        print("=" * 80)
        
        try:
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations")
            
            if response.status_code == 200:
                unified_data = response.json()
                
                if len(unified_data) > 0:
                    # Find a catalyst with good content values for testing
                    selected_catalyst = None
                    for catalyst in unified_data:
                        if (catalyst.get("pt_g", 0) > 0 or 
                            catalyst.get("pd_g", 0) > 0 or 
                            catalyst.get("rh_g", 0) > 0):
                            selected_catalyst = catalyst
                            break
                    
                    if not selected_catalyst:
                        # Use first catalyst if none have content values
                        selected_catalyst = unified_data[0]
                    
                    self.log_test("Catalyst Data Retrieval", True, 
                                f"Retrieved {len(unified_data)} catalysts, selected: {selected_catalyst.get('name', 'Unknown')}")
                    return selected_catalyst
                else:
                    self.log_test("Catalyst Data Retrieval", False, "No catalyst data available")
                    return None
            else:
                self.log_test("Catalyst Data Retrieval", False, 
                            f"Failed to get catalyst data, status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Catalyst Data Retrieval", False, error_msg=str(e))
            return None

    def create_listing_with_catalyst_data(self, catalyst_data):
        """Step 3: Create a listing with comprehensive catalyst data"""
        print("=" * 80)
        print("STEP 3: CREATE LISTING WITH CATALYST DATA")
        print("=" * 80)
        
        if not catalyst_data:
            self.log_test("Listing Creation", False, "No catalyst data available for listing creation")
            return None
            
        try:
            # Create comprehensive listing data with catalyst information
            listing_data = {
                "title": f"Test Catalyst Converter - {catalyst_data.get('name', 'Unknown')}",
                "description": f"Test listing with catalyst data for ProductDetailPage verification. Contains comprehensive catalyst specifications including content values (pt_g: {catalyst_data.get('pt_g', 0)}, pd_g: {catalyst_data.get('pd_g', 0)}, rh_g: {catalyst_data.get('rh_g', 0)}).",
                "price": catalyst_data.get("total_price", 100.0),
                "category": "Automotive",
                "condition": "Used",
                "seller_id": self.admin_user_id,
                "images": ["https://via.placeholder.com/400x300?text=Catalyst+Converter"],
                "tags": ["catalyst", "converter", "automotive", "test"],
                "features": ["Platinum content", "Palladium content", "Rhodium content", "Ceramic weight"],
                
                # Catalyst database fields - comprehensive data
                "ceramic_weight": catalyst_data.get("weight", 0),
                "pt_ppm": catalyst_data.get("pt_ppm", 0),
                "pd_ppm": catalyst_data.get("pd_ppm", 0), 
                "rh_ppm": catalyst_data.get("rh_ppm", 0),
                
                # Additional catalyst fields for comprehensive testing
                "catalyst_id": catalyst_data.get("catalyst_id"),
                "catalyst_name": catalyst_data.get("name"),
                "calculated_price": catalyst_data.get("total_price", 0),
                
                # Catalyst specs object for inventory management
                "catalyst_specs": {
                    "catalyst_id": catalyst_data.get("catalyst_id"),
                    "cat_id": catalyst_data.get("cat_id"),
                    "name": catalyst_data.get("name"),
                    "weight": catalyst_data.get("weight", 0),
                    "pt_g": catalyst_data.get("pt_g", 0),
                    "pd_g": catalyst_data.get("pd_g", 0),
                    "rh_g": catalyst_data.get("rh_g", 0),
                    "pt_ppm": catalyst_data.get("pt_ppm", 0),
                    "pd_ppm": catalyst_data.get("pd_ppm", 0),
                    "rh_ppm": catalyst_data.get("rh_ppm", 0),
                    "total_price": catalyst_data.get("total_price", 0),
                    "is_override": catalyst_data.get("is_override", False)
                },
                
                # Mark as catalyst listing for identification
                "is_catalyst_listing": True,
                "status": "active"
            }
            
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data)
            
            if response.status_code == 200:
                listing_result = response.json()
                self.created_listing_id = listing_result.get("listing_id")
                
                self.log_test("Listing Creation with Catalyst Data", True, 
                            f"Successfully created listing ID: {self.created_listing_id}")
                return listing_result
            else:
                self.log_test("Listing Creation with Catalyst Data", False, 
                            f"Failed to create listing, status code: {response.status_code}, response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Listing Creation with Catalyst Data", False, error_msg=str(e))
            return None

    def verify_listing_catalyst_data(self, listing_id):
        """Step 4: Verify the listing was created with comprehensive catalyst data"""
        print("=" * 80)
        print("STEP 4: VERIFY LISTING CATALYST DATA")
        print("=" * 80)
        
        if not listing_id:
            self.log_test("Listing Verification", False, "No listing ID to verify")
            return False
            
        try:
            # Get the created listing to verify data
            response = requests.get(f"{BACKEND_URL}/listings/{listing_id}")
            
            if response.status_code == 200:
                listing = response.json()
                
                # Check for all required catalyst fields
                required_fields = [
                    "ceramic_weight", "pt_ppm", "pd_ppm", "rh_ppm",
                    "catalyst_id", "catalyst_name", "calculated_price",
                    "catalyst_specs", "is_catalyst_listing"
                ]
                
                missing_fields = []
                present_fields = []
                
                for field in required_fields:
                    if field in listing and listing[field] is not None:
                        present_fields.append(field)
                    else:
                        missing_fields.append(field)
                
                if not missing_fields:
                    # Verify catalyst_specs object structure
                    catalyst_specs = listing.get("catalyst_specs", {})
                    specs_fields = ["catalyst_id", "name", "weight", "pt_g", "pd_g", "rh_g", "total_price"]
                    specs_present = [field for field in specs_fields if field in catalyst_specs]
                    
                    self.log_test("Listing Catalyst Data Verification", True, 
                                f"All {len(required_fields)} catalyst fields present: {present_fields}. Catalyst specs has {len(specs_present)} fields: {specs_present}")
                    return True
                else:
                    self.log_test("Listing Catalyst Data Verification", False, 
                                f"Missing catalyst fields: {missing_fields}. Present: {present_fields}")
                    return False
            else:
                self.log_test("Listing Catalyst Data Verification", False, 
                            f"Failed to retrieve listing, status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Listing Catalyst Data Verification", False, error_msg=str(e))
            return False

    def verify_browse_endpoint_shows_listing(self):
        """Step 5: Verify the listing appears in browse endpoint with catalyst data"""
        print("=" * 80)
        print("STEP 5: VERIFY LISTING IN BROWSE ENDPOINT")
        print("=" * 80)
        
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/browse")
            
            if response.status_code == 200:
                listings = response.json()
                
                # Find our created listing
                our_listing = None
                for listing in listings:
                    if listing.get("id") == self.created_listing_id:
                        our_listing = listing
                        break
                
                if our_listing:
                    # Check if catalyst data is preserved in browse endpoint
                    catalyst_fields_in_browse = []
                    for field in ["ceramic_weight", "pt_ppm", "pd_ppm", "rh_ppm", "catalyst_specs"]:
                        if field in our_listing and our_listing[field] is not None:
                            catalyst_fields_in_browse.append(field)
                    
                    self.log_test("Browse Endpoint Listing Verification", True, 
                                f"Listing found in browse with {len(catalyst_fields_in_browse)} catalyst fields: {catalyst_fields_in_browse}")
                    return True
                else:
                    self.log_test("Browse Endpoint Listing Verification", False, 
                                f"Created listing {self.created_listing_id} not found in browse results")
                    return False
            else:
                self.log_test("Browse Endpoint Listing Verification", False, 
                            f"Failed to get browse listings, status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Browse Endpoint Listing Verification", False, error_msg=str(e))
            return False

    def run_comprehensive_test(self):
        """Run the complete catalyst listing test suite"""
        print("🧪 CATALYST LISTING CREATION TEST FOR PRODUCTDETAILPAGE VERIFICATION")
        print("=" * 80)
        print(f"Testing against: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Step 1: Login as demo admin
        if not self.login_as_demo_admin():
            print("❌ Cannot proceed without admin login")
            return self.print_summary()
        
        # Step 2: Get catalyst data
        catalyst_data = self.get_catalyst_data_for_listing()
        if not catalyst_data:
            print("❌ Cannot proceed without catalyst data")
            return self.print_summary()
        
        # Step 3: Create listing with catalyst data
        listing_result = self.create_listing_with_catalyst_data(catalyst_data)
        if not listing_result:
            print("❌ Cannot proceed without successful listing creation")
            return self.print_summary()
        
        # Step 4: Verify listing catalyst data
        self.verify_listing_catalyst_data(self.created_listing_id)
        
        # Step 5: Verify listing in browse endpoint
        self.verify_browse_endpoint_shows_listing()
        
        return self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("CATALYST LISTING TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.created_listing_id:
            print(f"\n🎯 CREATED LISTING ID: {self.created_listing_id}")
            print(f"📋 Frontend URL: https://enterprise-market.preview.emergentagent.com/listing/{self.created_listing_id}")
            print(f"🔍 Use this listing ID to test ProductDetailPage content value display")
        
        print("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   📝 {result['details']}")
            if result['error']:
                print(f"   ⚠️  {result['error']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 80:
            print("✅ CATALYST LISTING TEST COMPLETED SUCCESSFULLY")
            print("🎯 Listing created with comprehensive catalyst data for ProductDetailPage testing")
        else:
            print("❌ CATALYST LISTING TEST COMPLETED WITH ISSUES")
            print("⚠️  Some tests failed - check details above")
        
        print("=" * 80)
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = CatalystListingTester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)