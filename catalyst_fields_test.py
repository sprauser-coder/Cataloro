#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Catalyst Fields Approach Testing
Testing the improved catalyst fields approach for accurate basket calculations
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-admin-5.preview.emergentagent.com/api"

class CatalystFieldsTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_user_id = None
        self.test_listing_id = None
        self.test_basket_id = None
        self.ford_listing_id = None
        
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

    def setup_test_user(self):
        """Setup a test user for testing"""
        try:
            # Login as demo user
            demo_credentials = {
                "email": "demo@cataloro.com",
                "password": "demo123"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login", 
                json=demo_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                self.test_user_id = user.get('id')
                
                self.log_test(
                    "Setup Test User", 
                    True, 
                    f"Demo user logged in successfully. User ID: {self.test_user_id}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Setup Test User", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Setup Test User", False, error_msg=str(e))
            return False

    def test_create_listing_with_catalyst_fields(self):
        """Test creating a listing with catalyst fields (ceramic_weight, pt_ppm, pd_ppm, rh_ppm)"""
        try:
            if not self.test_user_id:
                self.log_test("Create Listing with Catalyst Fields", False, error_msg="No test user available")
                return False

            # Create a test listing with catalyst fields
            listing_data = {
                "title": "Test Catalyst Converter with Direct Fields",
                "description": "Test listing with catalyst fields stored directly",
                "price": 250.0,
                "category": "Automotive",
                "condition": "Used",
                "seller_id": self.test_user_id,
                "images": ["test_image.jpg"],
                "tags": ["catalyst", "converter", "test"],
                "features": ["Direct catalyst fields", "Test item"],
                # Direct catalyst fields (the new approach)
                "ceramic_weight": 139.7,
                "pt_ppm": 1394.0,
                "pd_ppm": 959.0,
                "rh_ppm": 0.0
            }
            
            response = requests.post(
                f"{BACKEND_URL}/listings", 
                json=listing_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_listing_id = data.get('listing_id')
                
                # Verify the listing was created with catalyst fields
                listing_response = requests.get(f"{BACKEND_URL}/listings/{self.test_listing_id}", timeout=10)
                if listing_response.status_code == 200:
                    listing = listing_response.json()
                    
                    # Check if catalyst fields are stored correctly
                    ceramic_weight = listing.get('ceramic_weight')
                    pt_ppm = listing.get('pt_ppm')
                    pd_ppm = listing.get('pd_ppm')
                    rh_ppm = listing.get('rh_ppm')
                    
                    fields_correct = (
                        ceramic_weight == 139.7 and
                        pt_ppm == 1394.0 and
                        pd_ppm == 959.0 and
                        rh_ppm == 0.0
                    )
                    
                    if fields_correct:
                        self.log_test(
                            "Create Listing with Catalyst Fields", 
                            True, 
                            f"Listing created with catalyst fields: weight={ceramic_weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Create Listing with Catalyst Fields", 
                            False, 
                            f"Catalyst fields not stored correctly: weight={ceramic_weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}"
                        )
                        return False
                else:
                    self.log_test("Create Listing with Catalyst Fields", False, error_msg="Failed to retrieve created listing")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Listing with Catalyst Fields", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Create Listing with Catalyst Fields", False, error_msg=str(e))
            return False

    def test_create_basket_and_assign_item(self):
        """Test creating a basket and assigning the test listing to it"""
        try:
            if not self.test_user_id or not self.test_listing_id:
                self.log_test("Create Basket and Assign Item", False, error_msg="Missing test user or listing")
                return False

            # First, create a tender for the listing to simulate a bought item
            tender_data = {
                "listing_id": self.test_listing_id,
                "buyer_id": self.test_user_id,
                "offer_amount": 200.0,
                "message": "Test tender for catalyst fields testing"
            }
            
            tender_response = requests.post(
                f"{BACKEND_URL}/tenders", 
                json=tender_data,
                timeout=10
            )
            
            if tender_response.status_code != 200:
                self.log_test("Create Basket and Assign Item", False, error_msg="Failed to create test tender")
                return False
            
            tender_id = tender_response.json().get('tender_id')
            
            # Accept the tender to create a bought item
            accept_response = requests.put(
                f"{BACKEND_URL}/tenders/{tender_id}/accept",
                timeout=10
            )
            
            if accept_response.status_code != 200:
                self.log_test("Create Basket and Assign Item", False, error_msg="Failed to accept test tender")
                return False

            # Create a test basket
            basket_data = {
                "user_id": self.test_user_id,
                "name": "Test Catalyst Basket",
                "description": "Test basket for catalyst fields approach"
            }
            
            basket_response = requests.post(
                f"{BACKEND_URL}/user/baskets", 
                json=basket_data,
                timeout=10
            )
            
            if basket_response.status_code == 200:
                self.test_basket_id = basket_response.json().get('basket_id')
                
                # Get bought items to find the item ID
                bought_items_response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.test_user_id}", timeout=10)
                if bought_items_response.status_code == 200:
                    bought_items = bought_items_response.json()
                    
                    # Find the item from our test listing
                    test_item = None
                    for item in bought_items:
                        if item.get('listing_id') == self.test_listing_id:
                            test_item = item
                            break
                    
                    if test_item:
                        # Assign the item to the basket
                        assignment_data = {"basket_id": self.test_basket_id}
                        assign_response = requests.put(
                            f"{BACKEND_URL}/user/bought-items/{test_item['id']}/assign",
                            json=assignment_data,
                            timeout=10
                        )
                        
                        if assign_response.status_code == 200:
                            self.log_test(
                                "Create Basket and Assign Item", 
                                True, 
                                f"Created basket {self.test_basket_id} and assigned item {test_item['id']}"
                            )
                            return True
                        else:
                            self.log_test("Create Basket and Assign Item", False, error_msg="Failed to assign item to basket")
                            return False
                    else:
                        self.log_test("Create Basket and Assign Item", False, error_msg="Test item not found in bought items")
                        return False
                else:
                    self.log_test("Create Basket and Assign Item", False, error_msg="Failed to get bought items")
                    return False
            else:
                error_detail = basket_response.json().get('detail', 'Unknown error') if basket_response.content else f"HTTP {basket_response.status_code}"
                self.log_test("Create Basket and Assign Item", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Create Basket and Assign Item", False, error_msg=str(e))
            return False

    def test_basket_calculation_with_direct_fields(self):
        """Test that basket calculations use direct listing fields"""
        try:
            if not self.test_user_id or not self.test_basket_id:
                self.log_test("Basket Calculation with Direct Fields", False, error_msg="Missing test user or basket")
                return False

            # Get the basket with items
            baskets_response = requests.get(f"{BACKEND_URL}/user/baskets/{self.test_user_id}", timeout=10)
            
            if baskets_response.status_code == 200:
                baskets = baskets_response.json()
                
                # Find our test basket
                test_basket = None
                for basket in baskets:
                    if basket.get('id') == self.test_basket_id:
                        test_basket = basket
                        break
                
                if test_basket and test_basket.get('items'):
                    item = test_basket['items'][0]  # Get the first (and only) item
                    
                    # Check if the item has the correct catalyst fields from the listing
                    weight = item.get('weight')
                    pt_ppm = item.get('pt_ppm')
                    pd_ppm = item.get('pd_ppm')
                    rh_ppm = item.get('rh_ppm')
                    
                    # Expected values from our test listing
                    expected_weight = 139.7
                    expected_pt = 1394.0
                    expected_pd = 959.0
                    expected_rh = 0.0
                    
                    fields_match = (
                        weight == expected_weight and
                        pt_ppm == expected_pt and
                        pd_ppm == expected_pd and
                        rh_ppm == expected_rh
                    )
                    
                    if fields_match:
                        # Calculate expected values using renumeration
                        renumeration_pt = item.get('renumeration_pt', 0.98)
                        renumeration_pd = item.get('renumeration_pd', 0.98)
                        renumeration_rh = item.get('renumeration_rh', 0.9)
                        
                        # Expected calculations: (weight * ppm / 1000000) * renumeration
                        expected_pt_calc = (expected_weight * expected_pt / 1000000) * renumeration_pt
                        expected_pd_calc = (expected_weight * expected_pd / 1000000) * renumeration_pd
                        expected_rh_calc = (expected_weight * expected_rh / 1000000) * renumeration_rh
                        
                        self.log_test(
                            "Basket Calculation with Direct Fields", 
                            True, 
                            f"Basket uses direct listing fields: weight={weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}. Expected calculations: PT={expected_pt_calc:.4f}, PD={expected_pd_calc:.4f}, RH={expected_rh_calc:.4f}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Basket Calculation with Direct Fields", 
                            False, 
                            f"Catalyst fields don't match: got weight={weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}, expected weight={expected_weight}, pt={expected_pt}, pd={expected_pd}, rh={expected_rh}"
                        )
                        return False
                else:
                    self.log_test("Basket Calculation with Direct Fields", False, error_msg="Test basket not found or has no items")
                    return False
            else:
                error_detail = baskets_response.json().get('detail', 'Unknown error') if baskets_response.content else f"HTTP {baskets_response.status_code}"
                self.log_test("Basket Calculation with Direct Fields", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Basket Calculation with Direct Fields", False, error_msg=str(e))
            return False

    def test_find_and_update_ford_listing(self):
        """Find the existing Ford listing and update it with correct catalyst values"""
        try:
            # Get all listings to find the Ford one
            browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if browse_response.status_code == 200:
                listings = browse_response.json()
                
                # Find Ford listing
                ford_listing = None
                for listing in listings:
                    title = listing.get('title', '').lower()
                    if 'ford' in title:
                        ford_listing = listing
                        self.ford_listing_id = listing.get('id')
                        break
                
                if ford_listing:
                    # Update Ford listing with correct catalyst values from cat database
                    # (weight: 139.7, pt_ppm: 1394, pd_ppm: 959, rh_ppm: 0)
                    update_data = {
                        "ceramic_weight": 139.7,
                        "pt_ppm": 1394,
                        "pd_ppm": 959,
                        "rh_ppm": 0
                    }
                    
                    update_response = requests.put(
                        f"{BACKEND_URL}/listings/{self.ford_listing_id}",
                        json=update_data,
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        # Verify the update
                        verify_response = requests.get(f"{BACKEND_URL}/listings/{self.ford_listing_id}", timeout=10)
                        if verify_response.status_code == 200:
                            updated_listing = verify_response.json()
                            
                            ceramic_weight = updated_listing.get('ceramic_weight')
                            pt_ppm = updated_listing.get('pt_ppm')
                            pd_ppm = updated_listing.get('pd_ppm')
                            rh_ppm = updated_listing.get('rh_ppm')
                            
                            values_correct = (
                                ceramic_weight == 139.7 and
                                pt_ppm == 1394 and
                                pd_ppm == 959 and
                                rh_ppm == 0
                            )
                            
                            if values_correct:
                                self.log_test(
                                    "Find and Update Ford Listing", 
                                    True, 
                                    f"Ford listing '{ford_listing.get('title')}' updated with catalyst values: weight={ceramic_weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}"
                                )
                                return True
                            else:
                                self.log_test(
                                    "Find and Update Ford Listing", 
                                    False, 
                                    f"Ford listing values not updated correctly: weight={ceramic_weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}"
                                )
                                return False
                        else:
                            self.log_test("Find and Update Ford Listing", False, error_msg="Failed to verify Ford listing update")
                            return False
                    else:
                        error_detail = update_response.json().get('detail', 'Unknown error') if update_response.content else f"HTTP {update_response.status_code}"
                        self.log_test("Find and Update Ford Listing", False, error_msg=f"Failed to update Ford listing: {error_detail}")
                        return False
                else:
                    self.log_test("Find and Update Ford Listing", False, error_msg="Ford listing not found")
                    return False
            else:
                error_detail = browse_response.json().get('detail', 'Unknown error') if browse_response.content else f"HTTP {browse_response.status_code}"
                self.log_test("Find and Update Ford Listing", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Find and Update Ford Listing", False, error_msg=str(e))
            return False

    def test_end_to_end_workflow(self):
        """Test the complete end-to-end workflow: Ford listing → picki basket → calculations"""
        try:
            if not self.test_user_id or not self.ford_listing_id:
                self.log_test("End-to-End Workflow", False, error_msg="Missing test user or Ford listing")
                return False

            # Create picki basket
            picki_basket_data = {
                "user_id": self.test_user_id,
                "name": "picki",
                "description": "Test basket for Ford listing end-to-end workflow"
            }
            
            picki_response = requests.post(
                f"{BACKEND_URL}/user/baskets", 
                json=picki_basket_data,
                timeout=10
            )
            
            if picki_response.status_code != 200:
                self.log_test("End-to-End Workflow", False, error_msg="Failed to create picki basket")
                return False
            
            picki_basket_id = picki_response.json().get('basket_id')
            
            # Create a tender for Ford listing
            ford_tender_data = {
                "listing_id": self.ford_listing_id,
                "buyer_id": self.test_user_id,
                "offer_amount": 200.0,
                "message": "Test tender for Ford listing end-to-end workflow"
            }
            
            ford_tender_response = requests.post(
                f"{BACKEND_URL}/tenders", 
                json=ford_tender_data,
                timeout=10
            )
            
            if ford_tender_response.status_code != 200:
                self.log_test("End-to-End Workflow", False, error_msg="Failed to create Ford tender")
                return False
            
            ford_tender_id = ford_tender_response.json().get('tender_id')
            
            # Accept the Ford tender
            accept_ford_response = requests.put(
                f"{BACKEND_URL}/tenders/{ford_tender_id}/accept",
                timeout=10
            )
            
            if accept_ford_response.status_code != 200:
                self.log_test("End-to-End Workflow", False, error_msg="Failed to accept Ford tender")
                return False

            # Get bought items to find the Ford item
            bought_items_response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.test_user_id}", timeout=10)
            if bought_items_response.status_code != 200:
                self.log_test("End-to-End Workflow", False, error_msg="Failed to get bought items")
                return False
            
            bought_items = bought_items_response.json()
            ford_item = None
            for item in bought_items:
                if item.get('listing_id') == self.ford_listing_id:
                    ford_item = item
                    break
            
            if not ford_item:
                self.log_test("End-to-End Workflow", False, error_msg="Ford item not found in bought items")
                return False

            # Assign Ford item to picki basket
            assignment_data = {"basket_id": picki_basket_id}
            assign_response = requests.put(
                f"{BACKEND_URL}/user/bought-items/{ford_item['id']}/assign",
                json=assignment_data,
                timeout=10
            )
            
            if assign_response.status_code != 200:
                self.log_test("End-to-End Workflow", False, error_msg="Failed to assign Ford item to picki basket")
                return False

            # Get picki basket with calculations
            baskets_response = requests.get(f"{BACKEND_URL}/user/baskets/{self.test_user_id}", timeout=10)
            
            if baskets_response.status_code == 200:
                baskets = baskets_response.json()
                
                # Find picki basket
                picki_basket = None
                for basket in baskets:
                    if basket.get('id') == picki_basket_id:
                        picki_basket = basket
                        break
                
                if picki_basket and picki_basket.get('items'):
                    item = picki_basket['items'][0]
                    
                    # Check calculations with Ford catalyst values
                    weight = item.get('weight', 0)
                    pt_ppm = item.get('pt_ppm', 0)
                    pd_ppm = item.get('pd_ppm', 0)
                    rh_ppm = item.get('rh_ppm', 0)
                    
                    renumeration_pt = item.get('renumeration_pt', 0.98)
                    renumeration_pd = item.get('renumeration_pd', 0.98)
                    renumeration_rh = item.get('renumeration_rh', 0.9)
                    
                    # Calculate expected results based on Ford values (139.7g, 1394ppm PT, 959ppm PD, 0ppm RH)
                    expected_pt = (139.7 * 1394 / 1000000) * renumeration_pt
                    expected_pd = (139.7 * 959 / 1000000) * renumeration_pd
                    expected_rh = (139.7 * 0 / 1000000) * renumeration_rh
                    
                    # Actual calculations from the item
                    actual_pt = (weight * pt_ppm / 1000000) * renumeration_pt
                    actual_pd = (weight * pd_ppm / 1000000) * renumeration_pd
                    actual_rh = (weight * rh_ppm / 1000000) * renumeration_rh
                    
                    calculations_correct = (
                        abs(actual_pt - expected_pt) < 0.001 and
                        abs(actual_pd - expected_pd) < 0.001 and
                        abs(actual_rh - expected_rh) < 0.001
                    )
                    
                    if calculations_correct:
                        self.log_test(
                            "End-to-End Workflow", 
                            True, 
                            f"End-to-end workflow successful. Ford listing assigned to picki basket with correct calculations: PT={actual_pt:.4f}, PD={actual_pd:.4f}, RH={actual_rh:.4f} (expected: PT={expected_pt:.4f}, PD={expected_pd:.4f}, RH={expected_rh:.4f})"
                        )
                        return True
                    else:
                        self.log_test(
                            "End-to-End Workflow", 
                            False, 
                            f"Calculations incorrect: got PT={actual_pt:.4f}, PD={actual_pd:.4f}, RH={actual_rh:.4f}, expected PT={expected_pt:.4f}, PD={expected_pd:.4f}, RH={expected_rh:.4f}"
                        )
                        return False
                else:
                    self.log_test("End-to-End Workflow", False, error_msg="Picki basket not found or has no items")
                    return False
            else:
                error_detail = baskets_response.json().get('detail', 'Unknown error') if baskets_response.content else f"HTTP {baskets_response.status_code}"
                self.log_test("End-to-End Workflow", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("End-to-End Workflow", False, error_msg=str(e))
            return False

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        try:
            cleanup_results = []
            
            # Delete test listing
            if self.test_listing_id:
                try:
                    delete_response = requests.delete(f"{BACKEND_URL}/listings/{self.test_listing_id}", timeout=10)
                    if delete_response.status_code == 200:
                        cleanup_results.append("Test listing deleted")
                    else:
                        cleanup_results.append(f"Failed to delete test listing: HTTP {delete_response.status_code}")
                except Exception as e:
                    cleanup_results.append(f"Error deleting test listing: {str(e)}")
            
            # Delete test basket
            if self.test_basket_id:
                try:
                    delete_response = requests.delete(f"{BACKEND_URL}/user/baskets/{self.test_basket_id}", timeout=10)
                    if delete_response.status_code == 200:
                        cleanup_results.append("Test basket deleted")
                    else:
                        cleanup_results.append(f"Failed to delete test basket: HTTP {delete_response.status_code}")
                except Exception as e:
                    cleanup_results.append(f"Error deleting test basket: {str(e)}")
            
            self.log_test(
                "Cleanup Test Data", 
                True, 
                f"Cleanup completed: {'; '.join(cleanup_results)}"
            )
            return True
        except Exception as e:
            self.log_test("Cleanup Test Data", False, error_msg=str(e))
            return False

    def run_catalyst_fields_testing(self):
        """Run comprehensive catalyst fields approach testing"""
        print("=" * 80)
        print("CATALORO CATALYST FIELDS APPROACH TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting catalyst fields testing.")
            return
        
        # 2. Setup Test User
        print("👤 SETUP TEST USER")
        print("-" * 40)
        if not self.setup_test_user():
            print("❌ Failed to setup test user. Aborting tests.")
            return
        
        # 3. Test Updated Listing Model with Catalyst Fields
        print("📝 TEST UPDATED LISTING MODEL WITH CATALYST FIELDS")
        print("-" * 40)
        self.test_create_listing_with_catalyst_fields()
        
        # 4. Test Basket Calculation with Direct Fields
        print("🧮 TEST BASKET CALCULATION WITH DIRECT FIELDS")
        print("-" * 40)
        self.test_create_basket_and_assign_item()
        self.test_basket_calculation_with_direct_fields()
        
        # 5. Update Existing Ford Listing
        print("🚗 UPDATE EXISTING FORD LISTING")
        print("-" * 40)
        self.test_find_and_update_ford_listing()
        
        # 6. Verify End-to-End Workflow
        print("🔄 VERIFY END-TO-END WORKFLOW")
        print("-" * 40)
        self.test_end_to_end_workflow()
        
        # 7. Cleanup Test Data
        print("🧹 CLEANUP TEST DATA")
        print("-" * 40)
        self.cleanup_test_data()
        
        # Print Summary
        print("=" * 80)
        print("CATALYST FIELDS APPROACH TEST SUMMARY")
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
        
        print("\n🎯 CATALYST FIELDS APPROACH TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Listings should store catalyst fields directly (ceramic_weight, pt_ppm, pd_ppm, rh_ppm)")
        print("  ✅ Basket calculations should use direct listing fields instead of separate catalyst database")
        print("  ✅ Ford listing should be updated with correct catalyst values")
        print("  ✅ End-to-end workflow should show accurate calculations")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = CatalystFieldsTester()
    
    # Run Catalyst Fields Approach testing as requested in the review
    print("🎯 RUNNING CATALYST FIELDS APPROACH TESTING AS REQUESTED")
    print("Testing improved catalyst fields approach for accurate basket calculations...")
    print()
    
    passed, failed, results = tester.run_catalyst_fields_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)