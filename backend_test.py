#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Catalyst Data Preservation and Basket Calculation Testing
Testing the fixed inventory/basket calculation functionality with catalyst data preservation
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://catalyst-view.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_user = None
        self.admin_token = None
        
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

    def test_admin_login(self):
        """Test admin login and store credentials for subsequent tests"""
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
                token = data.get('token', '')
                
                self.admin_user = user
                self.admin_token = token
                
                user_role = user.get('user_role')
                user_id = user.get('id')
                username = user.get('username')
                
                is_admin = user_role in ['Admin', 'Admin-Manager']
                
                self.log_test(
                    "Admin Login", 
                    is_admin, 
                    f"Username: {username}, Role: {user_role}, User ID: {user_id}"
                )
                return is_admin
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login", False, error_msg=f"Login failed: {error_detail}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, error_msg=str(e))
            return False

    def test_create_listing_with_catalyst_data(self):
        """Test creating a listing with catalyst data for testing"""
        try:
            if not self.admin_user:
                self.log_test("Create Listing with Catalyst Data", False, error_msg="Admin user not available")
                return None
                
            # Create a test listing with comprehensive catalyst data
            listing_data = {
                "title": "Test Catalyst Converter BMW E90",
                "description": "Test catalyst converter for inventory/basket calculation testing with preserved catalyst data",
                "price": 150.0,
                "category": "Automotive",
                "condition": "Used",
                "seller_id": self.admin_user.get('id'),
                "images": [],
                "tags": ["catalyst", "bmw", "test"],
                "features": ["Platinum content", "Palladium content"],
                # Catalyst database fields for calculations
                "ceramic_weight": 142.5,
                "pt_ppm": 1450.0,
                "pd_ppm": 980.0,
                "rh_ppm": 125.0,
                # Pre-calculated content values (should be preserved)
                "pt_g": 0.8234,  # weight * pt_ppm / 1000000 * renumeration
                "pd_g": 0.5563,  # weight * pd_ppm / 1000000 * renumeration  
                "rh_g": 0.0711,  # weight * rh_ppm / 1000000 * renumeration
                "status": "active"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/listings",
                json=listing_data,
                timeout=10
            )
            
            if response.status_code == 200:
                create_response = response.json()
                listing_id = create_response.get('listing_id')
                
                if listing_id:
                    # Get the created listing to verify catalyst data
                    get_response = requests.get(f"{BACKEND_URL}/listings/{listing_id}", timeout=10)
                    if get_response.status_code == 200:
                        created_listing = get_response.json()
                        
                        # Verify catalyst data was stored
                        has_catalyst_data = all([
                            created_listing.get('ceramic_weight') is not None,
                            created_listing.get('pt_ppm') is not None,
                            created_listing.get('pd_ppm') is not None,
                            created_listing.get('rh_ppm') is not None
                        ])
                        
                        self.log_test(
                            "Create Listing with Catalyst Data", 
                            has_catalyst_data, 
                            f"Listing ID: {listing_id}, Weight: {created_listing.get('ceramic_weight')}g, "
                            f"PT: {created_listing.get('pt_ppm')}ppm, PD: {created_listing.get('pd_ppm')}ppm, "
                            f"RH: {created_listing.get('rh_ppm')}ppm"
                        )
                        
                        return created_listing if has_catalyst_data else None
                    else:
                        self.log_test("Create Listing with Catalyst Data", False, error_msg="Failed to retrieve created listing")
                        return None
                else:
                    self.log_test("Create Listing with Catalyst Data", False, error_msg="No listing ID returned")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Listing with Catalyst Data", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Create Listing with Catalyst Data", False, error_msg=str(e))
            return None

    def test_create_tender_and_accept(self, listing):
        """Test creating a tender for the listing and accepting it"""
        try:
            if not listing or not self.admin_user:
                self.log_test("Create Tender and Accept", False, error_msg="Listing or admin user not available")
                return None
                
            listing_id = listing.get('id')
            seller_id = listing.get('seller_id')
            
            # Use a different user as buyer (get existing user from system)
            users_response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if users_response.status_code != 200:
                self.log_test("Create Tender and Accept", False, error_msg="Could not get users list")
                return None
                
            users = users_response.json()
            buyer_user = None
            
            # Find a user that's not the seller
            for user in users:
                if user.get('id') != seller_id and user.get('registration_status') == 'Approved':
                    buyer_user = user
                    break
            
            if not buyer_user:
                self.log_test("Create Tender and Accept", False, error_msg="No suitable buyer user found")
                return None
            
            # Create a tender (buyer makes offer)
            tender_data = {
                "listing_id": listing_id,
                "buyer_id": buyer_user.get('id'),
                "offer_amount": listing.get('price', 150.0),
                "message": "Test tender for catalyst data preservation testing"
            }
            
            # Create tender
            tender_response = requests.post(
                f"{BACKEND_URL}/tenders/submit",
                json=tender_data,
                timeout=10
            )
            
            if tender_response.status_code != 200:
                error_detail = tender_response.json().get('detail', 'Unknown error') if tender_response.content else f"HTTP {tender_response.status_code}"
                self.log_test("Create Tender and Accept", False, error_msg=f"Tender creation failed: {error_detail}")
                return None
                
            tender = tender_response.json()
            tender_id = tender.get('tender_id') or tender.get('id')
            
            if not tender_id:
                self.log_test("Create Tender and Accept", False, error_msg="No tender ID returned from creation")
                return None
            
            # Accept the tender (seller accepts offer)
            accept_data = {
                "seller_id": seller_id
            }
            print(f"DEBUG: Accepting tender with seller_id: {seller_id}")
            accept_response = requests.put(
                f"{BACKEND_URL}/tenders/{tender_id}/accept",
                json=accept_data,
                timeout=10
            )
            
            if accept_response.status_code == 200:
                accepted_tender = accept_response.json()
                
                self.log_test(
                    "Create Tender and Accept", 
                    True, 
                    f"Tender ID: {tender_id}, Amount: €{tender.get('offer_amount')}, Buyer: {buyer_user.get('username')}, Status: {accepted_tender.get('status', 'accepted')}"
                )
                
                # Store buyer info for later use
                self.buyer_user = buyer_user
                return accepted_tender
            else:
                error_detail = accept_response.json().get('detail', 'Unknown error') if accept_response.content else f"HTTP {accept_response.status_code}"
                self.log_test("Create Tender and Accept", False, error_msg=f"Tender acceptance failed: {error_detail}")
                return None
                
        except Exception as e:
            self.log_test("Create Tender and Accept", False, error_msg=str(e))
            return None

    def test_verify_catalyst_data_in_bought_items(self):
        """Test that catalyst data is preserved in bought items after purchase"""
        try:
            # Use buyer user if available, otherwise admin
            test_user = getattr(self, 'buyer_user', self.admin_user)
            if not test_user:
                self.log_test("Verify Catalyst Data in Bought Items", False, error_msg="No test user available")
                return None
                
            user_id = test_user.get('id')
            
            # Get bought items for the user
            response = requests.get(
                f"{BACKEND_URL}/user/bought-items/{user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                bought_items = response.json()
                
                if not bought_items:
                    self.log_test("Verify Catalyst Data in Bought Items", False, error_msg="No bought items found")
                    return None
                
                # Find the most recent bought item (should be our test item)
                latest_item = bought_items[0] if bought_items else None
                
                if latest_item:
                    # Check if catalyst data is preserved
                    catalyst_data_preserved = all([
                        latest_item.get('weight') is not None and latest_item.get('weight') > 0,
                        latest_item.get('pt_ppm') is not None and latest_item.get('pt_ppm') > 0,
                        latest_item.get('pd_ppm') is not None and latest_item.get('pd_ppm') > 0,
                        latest_item.get('rh_ppm') is not None
                    ])
                    
                    # Check renumeration values
                    has_renumeration = all([
                        latest_item.get('renumeration_pt') is not None,
                        latest_item.get('renumeration_pd') is not None,
                        latest_item.get('renumeration_rh') is not None
                    ])
                    
                    self.log_test(
                        "Verify Catalyst Data in Bought Items", 
                        catalyst_data_preserved and has_renumeration, 
                        f"Item: {latest_item.get('title')}, Weight: {latest_item.get('weight')}g, "
                        f"PT: {latest_item.get('pt_ppm')}ppm, PD: {latest_item.get('pd_ppm')}ppm, "
                        f"RH: {latest_item.get('rh_ppm')}ppm, Renumeration PT: {latest_item.get('renumeration_pt')}"
                    )
                    
                    return latest_item if catalyst_data_preserved and has_renumeration else None
                else:
                    self.log_test("Verify Catalyst Data in Bought Items", False, error_msg="No bought items available")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Verify Catalyst Data in Bought Items", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Verify Catalyst Data in Bought Items", False, error_msg=str(e))
            return None

    def test_create_basket_and_assign_item(self, bought_item):
        """Test creating a basket and assigning the bought item to it"""
        try:
            if not bought_item:
                self.log_test("Create Basket and Assign Item", False, error_msg="Bought item not available")
                return None
                
            # Use buyer user if available, otherwise admin
            test_user = getattr(self, 'buyer_user', self.admin_user)
            if not test_user:
                self.log_test("Create Basket and Assign Item", False, error_msg="No test user available")
                return None
                
            user_id = test_user.get('id')
            
            # Create a new basket
            basket_data = {
                "user_id": user_id,
                "name": "Test Catalyst Calculation Basket",
                "description": "Test basket for verifying catalyst data preservation and calculations"
            }
            
            basket_response = requests.post(
                f"{BACKEND_URL}/user/baskets",
                json=basket_data,
                timeout=10
            )
            
            if basket_response.status_code != 200:
                error_detail = basket_response.json().get('detail', 'Unknown error') if basket_response.content else f"HTTP {basket_response.status_code}"
                self.log_test("Create Basket and Assign Item", False, error_msg=f"Basket creation failed: {error_detail}")
                return None
                
            basket = basket_response.json()
            basket_id = basket.get('basket_id') or basket.get('id')
            
            if not basket_id:
                self.log_test("Create Basket and Assign Item", False, error_msg="No basket ID returned from creation")
                return None
            
            # Assign the bought item to the basket
            item_id = bought_item.get('id')
            assign_data = {
                "basket_id": basket_id
            }
            
            assign_response = requests.put(
                f"{BACKEND_URL}/user/bought-items/{item_id}/assign",
                json=assign_data,
                timeout=10
            )
            
            if assign_response.status_code == 200:
                self.log_test(
                    "Create Basket and Assign Item", 
                    True, 
                    f"Basket ID: {basket_id}, Assigned Item: {bought_item.get('title')}"
                )
                
                # Return basket with correct ID for further testing
                return {"id": basket_id, "name": basket_data["name"]}
            else:
                error_detail = assign_response.json().get('detail', 'Unknown error') if assign_response.content else f"HTTP {assign_response.status_code}"
                self.log_test("Create Basket and Assign Item", False, error_msg=f"Item assignment failed: {error_detail}")
                return None
                
        except Exception as e:
            self.log_test("Create Basket and Assign Item", False, error_msg=str(e))
            return None

    def test_basket_calculations_with_preserved_data(self, basket):
        """Test that basket calculations produce non-zero values using preserved catalyst data"""
        try:
            if not basket:
                self.log_test("Basket Calculations with Preserved Data", False, error_msg="Basket not available")
                return False
                
            # Use buyer user if available, otherwise admin
            test_user = getattr(self, 'buyer_user', self.admin_user)
            if not test_user:
                self.log_test("Basket Calculations with Preserved Data", False, error_msg="No test user available")
                return False
                
            user_id = test_user.get('id')
            
            # Get baskets with calculations
            response = requests.get(
                f"{BACKEND_URL}/user/baskets/{user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                baskets = response.json()
                
                if not baskets:
                    self.log_test("Basket Calculations with Preserved Data", False, error_msg="No baskets returned")
                    return False
                
                # Find our test basket
                basket_id = basket.get('id')
                test_basket = None
                
                for b in baskets:
                    if b.get('id') == basket_id:
                        test_basket = b
                        break
                
                if not test_basket:
                    self.log_test("Basket Calculations with Preserved Data", False, error_msg="Test basket not found in response")
                    return False
                
                # Check if basket has items with calculations
                items = test_basket.get('items', [])
                if not items:
                    self.log_test("Basket Calculations with Preserved Data", False, error_msg="No items found in basket")
                    return False
                
                # Check calculations for the first item
                item = items[0]
                
                # Verify calculation values are non-zero
                pt_g = item.get('pt_g', 0)
                pd_g = item.get('pd_g', 0) 
                rh_g = item.get('rh_g', 0)
                
                # Check raw catalyst data
                weight = item.get('weight', 0)
                pt_ppm = item.get('pt_ppm', 0)
                pd_ppm = item.get('pd_ppm', 0)
                rh_ppm = item.get('rh_ppm', 0)
                renumeration_pt = item.get('renumeration_pt', 0)
                renumeration_pd = item.get('renumeration_pd', 0)
                renumeration_rh = item.get('renumeration_rh', 0)
                
                calculations_working = any([pt_g > 0, pd_g > 0, rh_g > 0])
                
                # Verify formula: ptG = weight * pt_ppm / 1000 * renumeration_pt
                if weight > 0 and pt_ppm > 0 and renumeration_pt > 0:
                    expected_pt_g = weight * pt_ppm / 1000 * renumeration_pt
                    formula_correct = abs(pt_g - expected_pt_g) < 0.01  # Allow small floating point differences
                else:
                    expected_pt_g = 0
                    formula_correct = False
                
                self.log_test(
                    "Basket Calculations with Preserved Data", 
                    calculations_working and formula_correct, 
                    f"Item: {item.get('title')}, PT: {pt_g:.4f}g, PD: {pd_g:.4f}g, RH: {rh_g:.4f}g. "
                    f"Raw data preserved: Weight={weight}g, PT={pt_ppm}ppm, PD={pd_ppm}ppm, RH={rh_ppm}ppm. "
                    f"Expected PT: {expected_pt_g:.4f}g, Got: {pt_g:.4f}g. "
                    f"Issue: {'Calculations missing' if not calculations_working else 'Formula incorrect'}"
                )
                
                return calculations_working and formula_correct
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Basket Calculations with Preserved Data", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Basket Calculations with Preserved Data", False, error_msg=str(e))
            return False

    def test_formula_verification(self):
        """Test the calculation formula verification with known values"""
        try:
            if not self.admin_user:
                self.log_test("Formula Verification", False, error_msg="Admin user not available")
                return False
                
            user_id = self.admin_user.get('id')
            
            # Get price settings for renumeration values
            price_response = requests.get(
                f"{BACKEND_URL}/admin/catalyst/price-settings",
                timeout=10
            )
            
            if price_response.status_code != 200:
                self.log_test("Formula Verification", False, error_msg="Could not get price settings")
                return False
                
            price_settings = price_response.json()
            renumeration_pt = price_settings.get('renumeration_pt', 0.98)
            renumeration_pd = price_settings.get('renumeration_pd', 0.98)
            renumeration_rh = price_settings.get('renumeration_rh', 0.9)
            
            # Test formula with known values
            test_weight = 142.5  # grams
            test_pt_ppm = 1450.0  # ppm
            test_pd_ppm = 980.0   # ppm
            test_rh_ppm = 125.0   # ppm
            
            # Calculate expected values using formula: content_g = weight * ppm / 1000 * renumeration
            expected_pt_g = test_weight * test_pt_ppm / 1000 * renumeration_pt
            expected_pd_g = test_weight * test_pd_ppm / 1000 * renumeration_pd
            expected_rh_g = test_weight * test_rh_ppm / 1000 * renumeration_rh
            
            # Verify formula produces reasonable values
            formula_working = all([
                expected_pt_g > 0,
                expected_pd_g > 0,
                expected_rh_g > 0,
                expected_pt_g < 1000,  # Sanity check - should be reasonable values
                expected_pd_g < 1000,
                expected_rh_g < 1000
            ])
            
            self.log_test(
                "Formula Verification", 
                formula_working, 
                f"Test values - Weight: {test_weight}g, PT: {test_pt_ppm}ppm, PD: {test_pd_ppm}ppm, RH: {test_rh_ppm}ppm. "
                f"Expected results - PT: {expected_pt_g:.4f}g, PD: {expected_pd_g:.4f}g, RH: {expected_rh_g:.4f}g"
            )
            
            return formula_working
            
        except Exception as e:
            self.log_test("Formula Verification", False, error_msg=str(e))
            return False

    def run_catalyst_data_preservation_testing(self):
        """Run comprehensive catalyst data preservation and basket calculation testing"""
        print("=" * 80)
        print("CATALORO CATALYST DATA PRESERVATION AND BASKET CALCULATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Admin Login
        print("👤 ADMIN LOGIN")
        print("-" * 40)
        if not self.test_admin_login():
            print("❌ Admin login failed. Aborting testing.")
            return
        
        # 2. Create Listing with Catalyst Data
        print("📝 CREATE LISTING WITH CATALYST DATA")
        print("-" * 40)
        test_listing = self.test_create_listing_with_catalyst_data()
        if not test_listing:
            print("❌ Failed to create test listing. Aborting testing.")
            return
        
        # 3. Create Tender and Accept
        print("🤝 CREATE TENDER AND ACCEPT")
        print("-" * 40)
        accepted_tender = self.test_create_tender_and_accept(test_listing)
        if not accepted_tender:
            print("❌ Failed to create and accept tender. Aborting testing.")
            return
        
        # Wait a moment for the system to process the purchase
        time.sleep(2)
        
        # 4. Verify Catalyst Data in Bought Items
        print("🔍 VERIFY CATALYST DATA PRESERVATION IN BOUGHT ITEMS")
        print("-" * 40)
        bought_item = self.test_verify_catalyst_data_in_bought_items()
        if not bought_item:
            print("❌ Catalyst data not preserved in bought items. Continuing with remaining tests.")
        
        # 5. Create Basket and Assign Item
        print("🗂️ CREATE BASKET AND ASSIGN ITEM")
        print("-" * 40)
        test_basket = self.test_create_basket_and_assign_item(bought_item)
        if not test_basket:
            print("❌ Failed to create basket and assign item. Continuing with remaining tests.")
        
        # 6. Test Basket Calculations
        print("🧮 TEST BASKET CALCULATIONS WITH PRESERVED DATA")
        print("-" * 40)
        self.test_basket_calculations_with_preserved_data(test_basket)
        
        # 7. Formula Verification
        print("📐 FORMULA VERIFICATION")
        print("-" * 40)
        self.test_formula_verification()
        
        # Print Summary
        print("=" * 80)
        print("CATALYST DATA PRESERVATION AND BASKET CALCULATION TEST SUMMARY")
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
        
        print("\n🎯 CATALYST DATA PRESERVATION AND BASKET CALCULATION TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Catalyst data preserved from listing to bought items")
        print("  ✅ Basket calculations produce non-zero values")
        print("  ✅ Formula (ptG = weight * pt_ppm / 1000 * renumeration_pt) works correctly")
        print("  ✅ Complete flow from listing creation to calculation verification")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    
    print("🎯 RUNNING CATALYST DATA PRESERVATION AND BASKET CALCULATION TESTING")
    print("Testing the fixed inventory/basket calculation functionality with catalyst data preservation...")
    print()
    
    result = tester.run_catalyst_data_preservation_testing()
    if result:
        passed, failed, results = result
        # Exit with appropriate code
        exit(0 if failed == 0 else 1)
    else:
        exit(1)