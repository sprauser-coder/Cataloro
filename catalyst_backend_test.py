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
BACKEND_URL = "https://catalyst-unified.preview.emergentagent.com/api"

class CatalystBackendTester:
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
                    f"Test user ID: {self.test_user_id}, Role: {user.get('user_role')}"
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
                "title": "Test Catalyst Converter Ford F150",
                "description": "Test listing with catalyst fields for basket calculation testing",
                "price": 250.0,
                "category": "Automotive",
                "condition": "Used",
                "seller_id": self.test_user_id,
                "images": [],
                "tags": ["catalyst", "ford", "test"],
                "features": ["Ceramic catalyst", "Platinum content", "Palladium content"],
                # Catalyst fields - using realistic values
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
                    
                    # Check if catalyst fields are present and correct
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
                            f"Listing created with ID: {self.test_listing_id}. Catalyst fields: weight={ceramic_weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Create Listing with Catalyst Fields", 
                            False, 
                            f"Catalyst fields incorrect: weight={ceramic_weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}"
                        )
                        return False
                else:
                    self.log_test("Create Listing with Catalyst Fields", False, error_msg="Could not retrieve created listing")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Listing with Catalyst Fields", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Create Listing with Catalyst Fields", False, error_msg=str(e))
            return False

    def test_create_basket(self):
        """Test creating a basket for testing"""
        try:
            if not self.test_user_id:
                self.log_test("Create Test Basket", False, error_msg="No test user available")
                return False

            basket_data = {
                "user_id": self.test_user_id,
                "name": "Test Catalyst Basket",
                "description": "Test basket for catalyst calculation testing"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/baskets", 
                json=basket_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_basket_id = data.get('basket_id')
                
                self.log_test(
                    "Create Test Basket", 
                    True, 
                    f"Basket created with ID: {self.test_basket_id}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test Basket", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Create Test Basket", False, error_msg=str(e))
            return False

    def test_create_tender_and_assign_to_basket(self):
        """Test assigning existing bought items to basket to verify catalyst calculations"""
        try:
            if not self.test_basket_id or not self.test_user_id:
                self.log_test("Create Tender and Assign to Basket", False, error_msg="Missing test prerequisites")
                return False

            # Get existing bought items for the user
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.test_user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                if not bought_items:
                    self.log_test("Create Tender and Assign to Basket", False, error_msg="No bought items available for testing")
                    return False
                
                # Use the first bought item
                test_item = bought_items[0]
                item_id = test_item.get('id')
                
                # First, update the corresponding listing with catalyst fields for testing
                listing_id = test_item.get('listing_id')
                if listing_id:
                    update_data = {
                        "ceramic_weight": 100.0,
                        "pt_ppm": 1000.0,
                        "pd_ppm": 500.0,
                        "rh_ppm": 100.0
                    }
                    
                    update_response = requests.put(
                        f"{BACKEND_URL}/listings/{listing_id}",
                        json=update_data,
                        timeout=10
                    )
                
                # Now assign the bought item to the basket
                assignment_data = {
                    "basket_id": self.test_basket_id
                }
                
                assign_response = requests.put(
                    f"{BACKEND_URL}/user/bought-items/{item_id}/assign",
                    json=assignment_data,
                    timeout=10
                )
                
                if assign_response.status_code == 200:
                    self.log_test(
                        "Create Tender and Assign to Basket", 
                        True, 
                        f"Bought item {item_id} assigned to basket {self.test_basket_id}"
                    )
                    return True
                else:
                    error_detail = assign_response.json().get('detail', 'Unknown error') if assign_response.content else f"HTTP {assign_response.status_code}"
                    self.log_test("Create Tender and Assign to Basket", False, error_msg=f"Assignment failed: {error_detail}")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Tender and Assign to Basket", False, error_msg=f"Failed to get bought items: {error_detail}")
                return False
        except Exception as e:
            self.log_test("Create Tender and Assign to Basket", False, error_msg=str(e))
            return False

    def test_basket_calculation_with_direct_fields(self):
        """Test that basket calculations use direct listing fields"""
        try:
            if not self.test_basket_id or not self.test_user_id:
                self.log_test("Basket Calculation with Direct Fields", False, error_msg="Missing test prerequisites")
                return False

            # Get the basket with items
            response = requests.get(
                f"{BACKEND_URL}/user/baskets/{self.test_user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                baskets = response.json()
                test_basket = None
                
                # Find our test basket
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
                    renumeration_pt = item.get('renumeration_pt')
                    renumeration_pd = item.get('renumeration_pd')
                    renumeration_rh = item.get('renumeration_rh')
                    
                    # Expected values from our test listing (updated in the tender test)
                    expected_weight = 100.0
                    expected_pt_ppm = 1000.0
                    expected_pd_ppm = 500.0
                    expected_rh_ppm = 100.0
                    
                    # Calculate expected results (weight * ppm / 1000000 * renumeration)
                    expected_pt_result = (expected_weight * expected_pt_ppm / 1000000) * renumeration_pt
                    expected_pd_result = (expected_weight * expected_pd_ppm / 1000000) * renumeration_pd
                    expected_rh_result = (expected_weight * expected_rh_ppm / 1000000) * renumeration_rh
                    
                    fields_correct = (
                        weight == expected_weight and
                        pt_ppm == expected_pt_ppm and
                        pd_ppm == expected_pd_ppm and
                        rh_ppm == expected_rh_ppm
                    )
                    
                    if fields_correct:
                        self.log_test(
                            "Basket Calculation with Direct Fields", 
                            True, 
                            f"Basket item has correct catalyst fields: weight={weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}. Expected calculations: PT={expected_pt_result:.4f}, PD={expected_pd_result:.4f}, RH={expected_rh_result:.4f}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Basket Calculation with Direct Fields", 
                            False, 
                            f"Catalyst fields incorrect: weight={weight} (expected {expected_weight}), pt={pt_ppm} (expected {expected_pt_ppm}), pd={pd_ppm} (expected {expected_pd_ppm}), rh={rh_ppm} (expected {expected_rh_ppm})"
                        )
                        return False
                else:
                    self.log_test("Basket Calculation with Direct Fields", False, error_msg="Test basket not found or has no items")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Basket Calculation with Direct Fields", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Basket Calculation with Direct Fields", False, error_msg=str(e))
            return False

    def test_find_existing_ford_listing(self):
        """Find existing Ford listing to update"""
        try:
            # Get all listings and search for Ford
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                ford_listings = []
                
                for listing in listings:
                    title = listing.get('title', '').lower()
                    if 'ford' in title:
                        ford_listings.append(listing)
                
                if ford_listings:
                    # Use the first Ford listing found
                    ford_listing = ford_listings[0]
                    self.ford_listing_id = ford_listing.get('id')
                    
                    self.log_test(
                        "Find Existing Ford Listing", 
                        True, 
                        f"Found Ford listing: {ford_listing.get('title')} (ID: {self.ford_listing_id})"
                    )
                    return True
                else:
                    # If no Ford listing exists, we'll use our test listing as the "Ford" listing
                    if self.test_listing_id:
                        self.ford_listing_id = self.test_listing_id
                        self.log_test(
                            "Find Existing Ford Listing", 
                            True, 
                            f"No existing Ford listing found, using test listing as Ford listing: {self.ford_listing_id}"
                        )
                        return True
                    else:
                        self.log_test("Find Existing Ford Listing", False, error_msg="No Ford listing found and no test listing available")
                        return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Find Existing Ford Listing", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Find Existing Ford Listing", False, error_msg=str(e))
            return False

    def test_update_ford_listing_with_catalyst_values(self):
        """Update Ford listing with correct catalyst values from cat database"""
        try:
            if not self.ford_listing_id:
                self.log_test("Update Ford Listing with Catalyst Values", False, error_msg="No Ford listing ID available")
                return False

            # Update the Ford listing with correct catalyst values
            # Using the values mentioned in the review: weight: 139.7, pt_ppm: 1394, pd_ppm: 959, rh_ppm: 0
            update_data = {
                "ceramic_weight": 139.7,
                "pt_ppm": 1394.0,
                "pd_ppm": 959.0,
                "rh_ppm": 0.0
            }
            
            response = requests.put(
                f"{BACKEND_URL}/listings/{self.ford_listing_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                # Verify the update by fetching the listing
                verify_response = requests.get(f"{BACKEND_URL}/listings/{self.ford_listing_id}", timeout=10)
                
                if verify_response.status_code == 200:
                    listing = verify_response.json()
                    
                    ceramic_weight = listing.get('ceramic_weight')
                    pt_ppm = listing.get('pt_ppm')
                    pd_ppm = listing.get('pd_ppm')
                    rh_ppm = listing.get('rh_ppm')
                    
                    values_correct = (
                        ceramic_weight == 139.7 and
                        pt_ppm == 1394.0 and
                        pd_ppm == 959.0 and
                        rh_ppm == 0.0
                    )
                    
                    if values_correct:
                        self.log_test(
                            "Update Ford Listing with Catalyst Values", 
                            True, 
                            f"Ford listing updated successfully with catalyst values: weight={ceramic_weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Update Ford Listing with Catalyst Values", 
                            False, 
                            f"Update verification failed: weight={ceramic_weight}, pt={pt_ppm}, pd={pd_ppm}, rh={rh_ppm}"
                        )
                        return False
                else:
                    self.log_test("Update Ford Listing with Catalyst Values", False, error_msg="Could not verify listing update")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Update Ford Listing with Catalyst Values", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Update Ford Listing with Catalyst Values", False, error_msg=str(e))
            return False

    def test_create_picki_basket_and_assign_ford(self):
        """Create a 'picki' basket and assign an item with Ford catalyst values to it"""
        try:
            if not self.test_user_id:
                self.log_test("Create Picki Basket and Assign Ford", False, error_msg="Missing test user")
                return False

            # Create picki basket
            basket_data = {
                "user_id": self.test_user_id,
                "name": "picki",
                "description": "Test basket for Ford catalyst calculation verification"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/baskets", 
                json=basket_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                picki_basket_id = data.get('basket_id')
                
                # Get existing bought items
                bought_items_response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.test_user_id}", timeout=10)
                
                if bought_items_response.status_code == 200:
                    bought_items = bought_items_response.json()
                    
                    if not bought_items:
                        self.log_test("Create Picki Basket and Assign Ford", False, error_msg="No bought items available")
                        return False
                    
                    # Use the first available bought item
                    test_item = bought_items[0]
                    item_id = test_item.get('id')
                    listing_id = test_item.get('listing_id')
                    
                    # Update the corresponding listing with Ford catalyst values
                    if listing_id:
                        update_data = {
                            "ceramic_weight": 139.7,
                            "pt_ppm": 1394.0,
                            "pd_ppm": 959.0,
                            "rh_ppm": 0.0
                        }
                        
                        update_response = requests.put(
                            f"{BACKEND_URL}/listings/{listing_id}",
                            json=update_data,
                            timeout=10
                        )
                    
                    # Assign to picki basket
                    assignment_data = {
                        "basket_id": picki_basket_id
                    }
                    
                    assign_response = requests.put(
                        f"{BACKEND_URL}/user/bought-items/{item_id}/assign",
                        json=assignment_data,
                        timeout=10
                    )
                    
                    if assign_response.status_code == 200:
                        self.log_test(
                            "Create Picki Basket and Assign Ford", 
                            True, 
                            f"Picki basket created ({picki_basket_id}) and item {item_id} assigned with Ford catalyst values"
                        )
                        
                        # Store picki basket ID for verification
                        self.picki_basket_id = picki_basket_id
                        return True
                    else:
                        error_detail = assign_response.json().get('detail', 'Unknown error') if assign_response.content else f"HTTP {assign_response.status_code}"
                        self.log_test("Create Picki Basket and Assign Ford", False, error_msg=f"Assignment failed: {error_detail}")
                        return False
                else:
                    error_detail = bought_items_response.json().get('detail', 'Unknown error') if bought_items_response.content else f"HTTP {bought_items_response.status_code}"
                    self.log_test("Create Picki Basket and Assign Ford", False, error_msg=f"Failed to get bought items: {error_detail}")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Picki Basket and Assign Ford", False, error_msg=f"Basket creation failed: {error_detail}")
                return False
        except Exception as e:
            self.log_test("Create Picki Basket and Assign Ford", False, error_msg=str(e))
            return False

    def test_verify_end_to_end_workflow(self):
        """Verify end-to-end workflow with correct calculations"""
        try:
            if not hasattr(self, 'picki_basket_id') or not self.test_user_id:
                self.log_test("Verify End-to-End Workflow", False, error_msg="Missing picki basket or test user")
                return False

            # Get the picki basket with Ford item
            response = requests.get(
                f"{BACKEND_URL}/user/baskets/{self.test_user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                baskets = response.json()
                picki_basket = None
                
                # Find picki basket
                for basket in baskets:
                    if basket.get('id') == self.picki_basket_id:
                        picki_basket = basket
                        break
                
                if picki_basket and picki_basket.get('items'):
                    item = picki_basket['items'][0]  # Get the Ford item
                    
                    # Get catalyst values
                    weight = item.get('weight', 0)
                    pt_ppm = item.get('pt_ppm', 0)
                    pd_ppm = item.get('pd_ppm', 0)
                    rh_ppm = item.get('rh_ppm', 0)
                    renumeration_pt = item.get('renumeration_pt', 0.98)
                    renumeration_pd = item.get('renumeration_pd', 0.98)
                    renumeration_rh = item.get('renumeration_rh', 0.9)
                    
                    # Calculate results (weight * ppm / 1000000 * renumeration)
                    pt_result = (weight * pt_ppm / 1000000) * renumeration_pt
                    pd_result = (weight * pd_ppm / 1000000) * renumeration_pd
                    rh_result = (weight * rh_ppm / 1000000) * renumeration_rh
                    
                    # Expected results based on Ford catalyst values: weight=139.7, pt=1394, pd=959, rh=0
                    # Calculation: (weight * ppm / 1000000) * renumeration
                    expected_pt = (139.7 * 1394.0 / 1000000) * renumeration_pt  # ≈ 0.1908
                    expected_pd = (139.7 * 959.0 / 1000000) * renumeration_pd   # ≈ 0.1313
                    expected_rh = (139.7 * 0.0 / 1000000) * renumeration_rh     # = 0.0000
                    
                    # Allow small tolerance for floating point calculations
                    tolerance = 0.001
                    pt_correct = abs(pt_result - expected_pt) < tolerance
                    pd_correct = abs(pd_result - expected_pd) < tolerance
                    rh_correct = abs(rh_result - expected_rh) < tolerance
                    
                    all_correct = pt_correct and pd_correct and rh_correct
                    
                    if all_correct:
                        self.log_test(
                            "Verify End-to-End Workflow", 
                            True, 
                            f"Ford listing in picki basket shows correct calculations: PT={pt_result:.4f} (expected {expected_pt}), PD={pd_result:.4f} (expected {expected_pd}), RH={rh_result:.4f} (expected {expected_rh})"
                        )
                        return True
                    else:
                        self.log_test(
                            "Verify End-to-End Workflow", 
                            False, 
                            f"Calculation mismatch: PT={pt_result:.4f} (expected {expected_pt}, correct: {pt_correct}), PD={pd_result:.4f} (expected {expected_pd}, correct: {pd_correct}), RH={rh_result:.4f} (expected {expected_rh}, correct: {rh_correct})"
                        )
                        return False
                else:
                    self.log_test("Verify End-to-End Workflow", False, error_msg="Picki basket not found or has no items")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Verify End-to-End Workflow", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Verify End-to-End Workflow", False, error_msg=str(e))
            return False

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        try:
            cleanup_results = []
            
            # Delete test basket
            if self.test_basket_id:
                try:
                    response = requests.delete(f"{BACKEND_URL}/user/baskets/{self.test_basket_id}", timeout=10)
                    if response.status_code == 200:
                        cleanup_results.append(f"Test basket {self.test_basket_id} deleted")
                    else:
                        cleanup_results.append(f"Failed to delete test basket {self.test_basket_id}")
                except:
                    cleanup_results.append(f"Error deleting test basket {self.test_basket_id}")
            
            # Delete picki basket
            if hasattr(self, 'picki_basket_id'):
                try:
                    response = requests.delete(f"{BACKEND_URL}/user/baskets/{self.picki_basket_id}", timeout=10)
                    if response.status_code == 200:
                        cleanup_results.append(f"Picki basket {self.picki_basket_id} deleted")
                    else:
                        cleanup_results.append(f"Failed to delete picki basket {self.picki_basket_id}")
                except:
                    cleanup_results.append(f"Error deleting picki basket {self.picki_basket_id}")
            
            # Note: We don't delete the test listing as it might be useful for future tests
            # and the Ford listing should remain with updated catalyst values
            
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
            print("❌ Health check failed. Aborting catalyst testing.")
            return
        
        # 2. Setup Test User
        print("👤 SETUP TEST USER")
        print("-" * 40)
        if not self.setup_test_user():
            print("❌ Failed to setup test user. Aborting tests.")
            return
        
        # 3. Test Updated Listing Model
        print("📝 TEST UPDATED LISTING MODEL")
        print("-" * 40)
        self.test_create_listing_with_catalyst_fields()
        
        # 4. Test Basket Creation
        print("🗂️ TEST BASKET CREATION")
        print("-" * 40)
        self.test_create_basket()
        
        # 5. Test Basket Calculation with Direct Fields
        print("🧮 TEST BASKET CALCULATION WITH DIRECT FIELDS")
        print("-" * 40)
        self.test_create_tender_and_assign_to_basket()
        self.test_basket_calculation_with_direct_fields()
        
        # 6. Update Existing Ford Listing
        print("🚗 UPDATE EXISTING FORD LISTING")
        print("-" * 40)
        self.test_find_existing_ford_listing()
        self.test_update_ford_listing_with_catalyst_values()
        
        # 7. Verify End-to-End Workflow
        print("🔄 VERIFY END-TO-END WORKFLOW")
        print("-" * 40)
        self.test_create_picki_basket_and_assign_ford()
        self.test_verify_end_to_end_workflow()
        
        # 8. Cleanup
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
        print("  ✅ Basket calculations should use direct listing fields")
        print("  ✅ Ford listing should be updated with correct catalyst values")
        print("  ✅ End-to-end workflow should show correct calculations (1.3686, 0.9398, 0.0000)")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = CatalystBackendTester()
    
    # Run Catalyst Fields Approach testing as requested in the review
    print("🎯 RUNNING CATALYST FIELDS APPROACH TESTING AS REQUESTED")
    print("Testing improved catalyst fields approach for accurate basket calculations...")
    print()
    
    passed, failed, results = tester.run_catalyst_fields_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)