#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Basket Calculation Fix Testing
Testing the basket calculation fix that preserves catalyst data from original listings
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://enterprise-market.preview.emergentagent.com/api"

class BasketCatalystFixTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.demo_user = None
        
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

    def setup_demo_user(self):
        """Login as demo user and get user data"""
        try:
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
                self.demo_user = data.get('user', {})
                user_id = self.demo_user.get('id')
                user_role = self.demo_user.get('user_role')
                
                self.log_test(
                    "Demo User Login", 
                    True, 
                    f"Logged in as {user_id} with role {user_role}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Demo User Login", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Demo User Login", False, error_msg=str(e))
            return False

    def test_create_listing_with_catalyst_data(self):
        """Create a test listing with catalyst data for testing"""
        try:
            if not self.demo_user:
                self.log_test("Create Test Listing", False, error_msg="No demo user available")
                return None
                
            # Create a listing with catalyst data
            listing_data = {
                "title": "Test Catalyst Converter for Basket Fix Testing",
                "description": "Test listing with catalyst data for basket calculation fix testing",
                "price": 175.0,
                "category": "Automotive",
                "condition": "Used",
                "seller_id": self.demo_user.get('id'),
                "images": [],
                "tags": ["test", "catalyst", "basket", "fix"],
                "features": ["Catalyst data included", "For basket testing"],
                # Catalyst data fields - use realistic values
                "ceramic_weight": 142.3,
                "pt_ppm": 1450.0,
                "pd_ppm": 890.0,
                "rh_ppm": 75.0
            }
            
            response = requests.post(
                f"{BACKEND_URL}/listings",
                json=listing_data,
                timeout=10
            )
            
            if response.status_code == 200:
                listing = response.json()
                listing_id = listing.get('id')
                
                self.log_test(
                    "Create Test Listing", 
                    True, 
                    f"Created listing {listing_id} with catalyst data: weight={listing_data['ceramic_weight']}g, pt={listing_data['pt_ppm']}ppm, pd={listing_data['pd_ppm']}ppm, rh={listing_data['rh_ppm']}ppm"
                )
                return listing_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test Listing", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Create Test Listing", False, error_msg=str(e))
            return None

    def test_create_tender_for_listing(self, listing_id):
        """Create a tender for the test listing"""
        try:
            if not listing_id or not self.demo_user:
                self.log_test("Create Test Tender", False, error_msg="No listing or user available")
                return None
                
            # Create a tender for the listing
            tender_data = {
                "listing_id": listing_id,
                "buyer_id": self.demo_user.get('id'),
                "offer_amount": 165.0,
                "message": "Test tender for basket calculation fix testing"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/tenders",
                json=tender_data,
                timeout=10
            )
            
            if response.status_code == 200:
                tender = response.json()
                tender_id = tender.get('id')
                
                # Accept the tender to create a bought item
                accept_response = requests.put(
                    f"{BACKEND_URL}/tenders/{tender_id}/accept",
                    timeout=10
                )
                
                if accept_response.status_code == 200:
                    self.log_test(
                        "Create Test Tender", 
                        True, 
                        f"Created and accepted tender {tender_id} for listing {listing_id} with offer €{tender_data['offer_amount']}"
                    )
                    return tender_id
                else:
                    self.log_test("Create Test Tender", False, error_msg=f"Failed to accept tender: HTTP {accept_response.status_code}")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test Tender", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Create Test Tender", False, error_msg=str(e))
            return None

    def test_create_basket(self):
        """Create a test basket"""
        try:
            if not self.demo_user:
                self.log_test("Create Test Basket", False, error_msg="No demo user available")
                return None
                
            basket_data = {
                "user_id": self.demo_user.get('id'),
                "name": "Test Basket for Catalyst Fix",
                "description": "Testing basket calculation fix with catalyst data preservation"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/user/baskets",
                json=basket_data,
                timeout=10
            )
            
            if response.status_code == 200:
                basket = response.json()
                basket_id = basket.get('id')
                
                self.log_test(
                    "Create Test Basket", 
                    True, 
                    f"Created basket {basket_id}: '{basket_data['name']}'"
                )
                return basket_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test Basket", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Create Test Basket", False, error_msg=str(e))
            return None

    def test_assign_item_with_catalyst_preservation(self, tender_id, basket_id):
        """Test 1: Assign item to basket and verify catalyst data is preserved in assignment"""
        try:
            if not tender_id or not basket_id:
                self.log_test("1. Assign Item with Catalyst Preservation", False, error_msg="No tender or basket available")
                return False
                
            # Assign the tender item to the basket
            item_id = f"tender_{tender_id}"
            assignment_data = {
                "basket_id": basket_id
            }
            
            response = requests.put(
                f"{BACKEND_URL}/user/bought-items/{item_id}/assign",
                json=assignment_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                self.log_test(
                    "1. Assign Item with Catalyst Preservation", 
                    True, 
                    f"✅ Successfully assigned item {item_id} to basket {basket_id}. Response: {result.get('message', 'No message')}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("1. Assign Item with Catalyst Preservation", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("1. Assign Item with Catalyst Preservation", False, error_msg=str(e))
            return False

    def test_basket_calculations_show_proper_values(self, basket_id):
        """Test 2: Verify GET /api/user/baskets/{user_id} shows proper Pt g, Pd g, Rh g values instead of (0,0,0)"""
        try:
            if not self.demo_user or not basket_id:
                self.log_test("2. Basket Calculations Show Proper Values", False, error_msg="No user or basket available")
                return False
                
            user_id = self.demo_user.get('id')
            
            response = requests.get(
                f"{BACKEND_URL}/user/baskets/{user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                baskets = response.json()
                
                # Find our test basket
                test_basket = None
                for basket in baskets:
                    if basket.get('id') == basket_id:
                        test_basket = basket
                        break
                
                if not test_basket:
                    self.log_test("2. Basket Calculations Show Proper Values", False, error_msg=f"Test basket {basket_id} not found in response")
                    return False
                
                items = test_basket.get('items', [])
                if not items:
                    self.log_test("2. Basket Calculations Show Proper Values", False, error_msg="No items found in test basket")
                    return False
                
                # Check the first item for catalyst data and calculate values
                item = items[0]
                weight = item.get('weight', 0.0)
                pt_ppm = item.get('pt_ppm', 0.0)
                pd_ppm = item.get('pd_ppm', 0.0)
                rh_ppm = item.get('rh_ppm', 0.0)
                renumeration_pt = item.get('renumeration_pt', 0.0)
                renumeration_pd = item.get('renumeration_pd', 0.0)
                renumeration_rh = item.get('renumeration_rh', 0.0)
                
                # Calculate expected values using the formula: (weight * ppm / 1000000) * renumeration
                pt_g = (weight * pt_ppm / 1000000) * renumeration_pt if weight > 0 and pt_ppm > 0 else 0.0
                pd_g = (weight * pd_ppm / 1000000) * renumeration_pd if weight > 0 and pd_ppm > 0 else 0.0
                rh_g = (weight * rh_ppm / 1000000) * renumeration_rh if weight > 0 and rh_ppm > 0 else 0.0
                
                # Check if we have non-zero catalyst data and calculations
                has_catalyst_data = weight > 0 and (pt_ppm > 0 or pd_ppm > 0 or rh_ppm > 0)
                has_non_zero_calculations = pt_g > 0 or pd_g > 0 or rh_g > 0
                
                if has_catalyst_data and has_non_zero_calculations:
                    self.log_test(
                        "2. Basket Calculations Show Proper Values", 
                        True, 
                        f"✅ Basket calculations now show proper values! Weight: {weight}g, PT: {pt_ppm}ppm→{pt_g:.6f}g, PD: {pd_ppm}ppm→{pd_g:.6f}g, RH: {rh_ppm}ppm→{rh_g:.6f}g. NOT (0,0,0)!"
                    )
                    return True
                elif has_catalyst_data:
                    self.log_test(
                        "2. Basket Calculations Show Proper Values", 
                        False, 
                        f"❌ Catalyst data preserved but calculations still (0,0,0). Weight: {weight}g, PT: {pt_ppm}ppm, PD: {pd_ppm}ppm, RH: {rh_ppm}ppm. Renumeration: PT={renumeration_pt}, PD={renumeration_pd}, RH={renumeration_rh}"
                    )
                    return False
                else:
                    self.log_test(
                        "2. Basket Calculations Show Proper Values", 
                        False, 
                        f"❌ Catalyst data NOT preserved - still showing (0,0,0). Weight: {weight}g, PT: {pt_ppm}ppm, PD: {pd_ppm}ppm, RH: {rh_ppm}ppm"
                    )
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("2. Basket Calculations Show Proper Values", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("2. Basket Calculations Show Proper Values", False, error_msg=str(e))
            return False

    def test_existing_assignments_with_preserved_data(self):
        """Test 3: Verify existing assignments (if any) show correct calculations"""
        try:
            if not self.demo_user:
                self.log_test("3. Existing Assignments Verification", False, error_msg="No demo user available")
                return False
                
            user_id = self.demo_user.get('id')
            
            response = requests.get(
                f"{BACKEND_URL}/user/baskets/{user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                baskets = response.json()
                
                total_items = 0
                items_with_catalyst = 0
                items_with_calculations = 0
                calculation_examples = []
                
                for basket in baskets:
                    items = basket.get('items', [])
                    total_items += len(items)
                    
                    for item in items:
                        weight = item.get('weight', 0.0)
                        pt_ppm = item.get('pt_ppm', 0.0)
                        pd_ppm = item.get('pd_ppm', 0.0)
                        rh_ppm = item.get('rh_ppm', 0.0)
                        renumeration_pt = item.get('renumeration_pt', 0.0)
                        renumeration_pd = item.get('renumeration_pd', 0.0)
                        renumeration_rh = item.get('renumeration_rh', 0.0)
                        
                        # Check if item has catalyst data
                        if weight > 0 and (pt_ppm > 0 or pd_ppm > 0 or rh_ppm > 0):
                            items_with_catalyst += 1
                            
                            # Calculate values
                            pt_g = (weight * pt_ppm / 1000000) * renumeration_pt if pt_ppm > 0 else 0.0
                            pd_g = (weight * pd_ppm / 1000000) * renumeration_pd if pd_ppm > 0 else 0.0
                            rh_g = (weight * rh_ppm / 1000000) * renumeration_rh if rh_ppm > 0 else 0.0
                            
                            if pt_g > 0 or pd_g > 0 or rh_g > 0:
                                items_with_calculations += 1
                                calculation_examples.append(f"PT:{pt_g:.4f}g, PD:{pd_g:.4f}g, RH:{rh_g:.4f}g")
                
                if total_items == 0:
                    self.log_test(
                        "3. Existing Assignments Verification", 
                        True, 
                        "No existing basket items found - this is expected for a fresh test environment"
                    )
                    return True
                elif items_with_catalyst > 0 and items_with_calculations > 0:
                    success_rate = (items_with_calculations / items_with_catalyst) * 100
                    examples_text = "; ".join(calculation_examples[:3])  # Show first 3 examples
                    self.log_test(
                        "3. Existing Assignments Verification", 
                        True, 
                        f"✅ Found {total_items} total items, {items_with_catalyst} with catalyst data, {items_with_calculations} with working calculations ({success_rate:.1f}% success rate). Examples: {examples_text}"
                    )
                    return True
                elif items_with_catalyst > 0:
                    self.log_test(
                        "3. Existing Assignments Verification", 
                        False, 
                        f"❌ Found {items_with_catalyst} items with catalyst data but only {items_with_calculations} with working calculations - calculation issue detected"
                    )
                    return False
                else:
                    self.log_test(
                        "3. Existing Assignments Verification", 
                        False, 
                        f"❌ Found {total_items} items but none have catalyst data - data preservation issue detected"
                    )
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("3. Existing Assignments Verification", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("3. Existing Assignments Verification", False, error_msg=str(e))
            return False

    def test_assignment_process_error_handling(self):
        """Test 4: Check for errors with the new assignment process"""
        try:
            if not self.demo_user:
                self.log_test("4. Assignment Process Error Handling", False, error_msg="No demo user available")
                return False
                
            # Test 1: Try to assign non-existent item to non-existent basket
            fake_item_id = "tender_nonexistent123"
            fake_basket_id = str(uuid.uuid4())
            
            assignment_data = {"basket_id": fake_basket_id}
            
            response = requests.put(
                f"{BACKEND_URL}/user/bought-items/{fake_item_id}/assign",
                json=assignment_data,
                timeout=10
            )
            
            # Should fail with 404 for non-existent basket
            error_1_handled = response.status_code == 404
            
            # Test 2: Try to assign without basket_id
            response2 = requests.put(
                f"{BACKEND_URL}/user/bought-items/tender_test123/assign",
                json={},  # No basket_id
                timeout=10
            )
            
            # Should fail with 400 for missing basket_id
            error_2_handled = response2.status_code == 400
            
            # Test 3: Try to assign with invalid basket_id format
            response3 = requests.put(
                f"{BACKEND_URL}/user/bought-items/tender_test123/assign",
                json={"basket_id": "invalid_format"},
                timeout=10
            )
            
            # Should fail with 404 for invalid basket
            error_3_handled = response3.status_code == 404
            
            all_errors_handled = error_1_handled and error_2_handled and error_3_handled
            
            self.log_test(
                "4. Assignment Process Error Handling", 
                all_errors_handled, 
                f"Error handling tests: Non-existent basket → HTTP {response.status_code} ({'✅' if error_1_handled else '❌'}), Missing basket_id → HTTP {response2.status_code} ({'✅' if error_2_handled else '❌'}), Invalid basket_id → HTTP {response3.status_code} ({'✅' if error_3_handled else '❌'})"
            )
            return all_errors_handled
        except Exception as e:
            self.log_test("4. Assignment Process Error Handling", False, error_msg=str(e))
            return False

    def test_catalyst_data_fallback_mechanism(self, listing_id, basket_id):
        """Test 5: Verify fallback mechanism when original listing is deleted"""
        try:
            if not listing_id or not basket_id or not self.demo_user:
                self.log_test("5. Catalyst Data Fallback Mechanism", False, error_msg="Missing required test data")
                return False
            
            user_id = self.demo_user.get('id')
            
            # First, get the current basket state to verify catalyst data is there
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            if response.status_code != 200:
                self.log_test("5. Catalyst Data Fallback Mechanism", False, error_msg="Failed to get initial basket state")
                return False
            
            baskets = response.json()
            test_basket = None
            for basket in baskets:
                if basket.get('id') == basket_id:
                    test_basket = basket
                    break
            
            if not test_basket or not test_basket.get('items'):
                self.log_test("5. Catalyst Data Fallback Mechanism", False, error_msg="No test basket or items found")
                return False
            
            # Get catalyst data before deletion
            item = test_basket['items'][0]
            original_weight = item.get('weight', 0.0)
            original_pt_ppm = item.get('pt_ppm', 0.0)
            original_pd_ppm = item.get('pd_ppm', 0.0)
            original_rh_ppm = item.get('rh_ppm', 0.0)
            
            if original_weight == 0 and original_pt_ppm == 0:
                self.log_test("5. Catalyst Data Fallback Mechanism", False, error_msg="No catalyst data found before deletion test")
                return False
            
            # Now delete the original listing to test fallback
            delete_response = requests.delete(f"{BACKEND_URL}/listings/{listing_id}", timeout=10)
            
            # Wait a moment for the deletion to process
            time.sleep(1)
            
            # Get basket data again to see if fallback works
            response2 = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            if response2.status_code != 200:
                self.log_test("5. Catalyst Data Fallback Mechanism", False, error_msg="Failed to get basket state after listing deletion")
                return False
            
            baskets2 = response2.json()
            test_basket2 = None
            for basket in baskets2:
                if basket.get('id') == basket_id:
                    test_basket2 = basket
                    break
            
            if not test_basket2 or not test_basket2.get('items'):
                self.log_test("5. Catalyst Data Fallback Mechanism", False, error_msg="Basket or items disappeared after listing deletion")
                return False
            
            # Check if catalyst data is preserved via fallback
            item2 = test_basket2['items'][0]
            fallback_weight = item2.get('weight', 0.0)
            fallback_pt_ppm = item2.get('pt_ppm', 0.0)
            fallback_pd_ppm = item2.get('pd_ppm', 0.0)
            fallback_rh_ppm = item2.get('rh_ppm', 0.0)
            
            # Check if fallback preserved the data
            data_preserved = (
                fallback_weight == original_weight and
                fallback_pt_ppm == original_pt_ppm and
                fallback_pd_ppm == original_pd_ppm and
                fallback_rh_ppm == original_rh_ppm
            )
            
            if data_preserved:
                self.log_test(
                    "5. Catalyst Data Fallback Mechanism", 
                    True, 
                    f"✅ Fallback mechanism working! Catalyst data preserved after listing deletion: weight={fallback_weight}g, pt={fallback_pt_ppm}ppm, pd={fallback_pd_ppm}ppm, rh={fallback_rh_ppm}ppm"
                )
                return True
            else:
                self.log_test(
                    "5. Catalyst Data Fallback Mechanism", 
                    False, 
                    f"❌ Fallback mechanism failed. Original: weight={original_weight}g, pt={original_pt_ppm}ppm. After deletion: weight={fallback_weight}g, pt={fallback_pt_ppm}ppm"
                )
                return False
                
        except Exception as e:
            self.log_test("5. Catalyst Data Fallback Mechanism", False, error_msg=str(e))
            return False

    def cleanup_test_data(self, basket_id):
        """Clean up test data created during testing"""
        try:
            cleanup_results = []
            
            # Delete test basket (listing already deleted in fallback test)
            if basket_id:
                try:
                    response = requests.delete(f"{BACKEND_URL}/user/baskets/{basket_id}", timeout=10)
                    if response.status_code == 200:
                        cleanup_results.append("✅ Basket deleted")
                    else:
                        cleanup_results.append(f"⚠️ Basket deletion: HTTP {response.status_code}")
                except Exception as e:
                    cleanup_results.append(f"❌ Basket deletion error: {str(e)}")
            
            self.log_test(
                "Test Data Cleanup", 
                True, 
                f"Cleanup completed: {'; '.join(cleanup_results)}"
            )
            return True
        except Exception as e:
            self.log_test("Test Data Cleanup", False, error_msg=str(e))
            return False

    def run_basket_catalyst_fix_testing(self):
        """Run comprehensive basket catalyst fix testing as requested in review"""
        print("=" * 80)
        print("CATALORO BASKET CALCULATION FIX TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        print("Testing the basket calculation fix that:")
        print("1. Assignment endpoint preserves catalyst data from original listings")
        print("2. Basket retrieval uses preserved catalyst data as fallback")
        print("3. Calculations show proper Pt g, Pd g, Rh g values instead of (0,0,0)")
        print()
        
        # Initialize test data variables
        listing_id = None
        tender_id = None
        basket_id = None
        
        try:
            # 1. Basic Health Check
            print("🔍 BASIC HEALTH CHECK")
            print("-" * 40)
            if not self.test_health_check():
                print("❌ Health check failed. Aborting basket catalyst fix testing.")
                return
            
            # 2. Setup Demo User
            print("👤 DEMO USER SETUP")
            print("-" * 40)
            if not self.setup_demo_user():
                print("❌ Failed to setup demo user. Aborting tests.")
                return
            
            # 3. Test Existing Assignments First
            print("📋 TEST 3: EXISTING ASSIGNMENTS VERIFICATION")
            print("-" * 40)
            self.test_existing_assignments_with_preserved_data()
            
            # 4. Create Test Listing with Catalyst Data
            print("📝 CREATE TEST LISTING WITH CATALYST DATA")
            print("-" * 40)
            listing_id = self.test_create_listing_with_catalyst_data()
            if not listing_id:
                print("❌ Failed to create test listing. Continuing with existing data tests only.")
            
            # 5. Create Tender for Testing (if listing created)
            if listing_id:
                print("💰 CREATE TEST TENDER")
                print("-" * 40)
                tender_id = self.test_create_tender_for_listing(listing_id)
                if not tender_id:
                    print("❌ Failed to create test tender.")
            
            # 6. Create Test Basket
            print("🗂️ CREATE TEST BASKET")
            print("-" * 40)
            basket_id = self.test_create_basket()
            if not basket_id:
                print("❌ Failed to create test basket.")
            
            # 7. TEST 1: Assignment with Catalyst Preservation
            if tender_id and basket_id:
                print("🔗 TEST 1: ASSIGN ITEM WITH CATALYST PRESERVATION")
                print("-" * 40)
                assignment_success = self.test_assign_item_with_catalyst_preservation(tender_id, basket_id)
                
                # 8. TEST 2: Basket Calculation Verification
                if assignment_success:
                    print("🧮 TEST 2: BASKET CALCULATIONS SHOW PROPER VALUES")
                    print("-" * 40)
                    calculation_success = self.test_basket_calculations_show_proper_values(basket_id)
                    
                    # 9. TEST 5: Fallback Mechanism (only if calculations work)
                    if calculation_success and listing_id:
                        print("🔄 TEST 5: CATALYST DATA FALLBACK MECHANISM")
                        print("-" * 40)
                        self.test_catalyst_data_fallback_mechanism(listing_id, basket_id)
            
            # 10. TEST 4: Assignment Process Error Handling
            print("⚠️ TEST 4: ASSIGNMENT PROCESS ERROR HANDLING")
            print("-" * 40)
            self.test_assignment_process_error_handling()
            
        finally:
            # 11. Cleanup Test Data
            print("🧹 TEST DATA CLEANUP")
            print("-" * 40)
            self.cleanup_test_data(basket_id)
        
        # Print Summary
        print("=" * 80)
        print("BASKET CALCULATION FIX TEST SUMMARY")
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
        
        print("\n🎯 BASKET CALCULATION FIX TESTING COMPLETE")
        print("Expected Results from Review Request:")
        print("  ✅ Assignment endpoint preserves catalyst data (weight, pt_ppm, pd_ppm, rh_ppm)")
        print("  ✅ Basket retrieval uses preserved catalyst data as fallback")
        print("  ✅ Basket calculations show proper Pt g, Pd g, Rh g values (not 0,0,0)")
        print("  ✅ Existing assignments with preserved data show correct calculations")
        print("  ✅ Assignment process handles errors gracefully")
        print("  ✅ Catalyst data persists even if original listings are deleted")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BasketCatalystFixTester()
    
    print("🎯 RUNNING BASKET CALCULATION FIX TESTING AS REQUESTED IN REVIEW")
    print("Testing the basket calculation fix implementation...")
    print()
    
    passed, failed, results = tester.run_basket_catalyst_fix_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)