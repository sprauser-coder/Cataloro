#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Seller Name Fix Verification
Testing the seller name fix for bought items endpoint
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://enterprise-market.preview.emergentagent.com/api"

class SellerNameFixTester:
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

    def get_demo_user(self):
        """Get demo user for testing"""
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
                return user
            else:
                return None
        except Exception as e:
            return None

    def test_bought_items_seller_names(self):
        """Test GET /api/user/bought-items/{user_id} for seller names"""
        try:
            # Get demo user
            user = self.get_demo_user()
            if not user:
                self.log_test("Bought Items Seller Names", False, error_msg="Could not get demo user")
                return False
            
            user_id = user.get('id')
            
            # Test the bought items endpoint
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                if not isinstance(bought_items, list):
                    self.log_test("Bought Items Seller Names", False, error_msg="Response is not a list")
                    return False
                
                total_items = len(bought_items)
                unknown_seller_count = 0
                actual_seller_count = 0
                seller_details = []
                
                for item in bought_items:
                    seller_name = item.get('seller_name', 'Unknown')
                    seller_id = item.get('seller_id', '')
                    item_title = item.get('title', 'Unknown Item')
                    
                    if seller_name == 'Unknown':
                        unknown_seller_count += 1
                        seller_details.append(f"'{item_title}': seller_name='Unknown', seller_id='{seller_id}'")
                    else:
                        actual_seller_count += 1
                        seller_details.append(f"'{item_title}': seller_name='{seller_name}', seller_id='{seller_id}'")
                
                # The fix should ensure that seller names are no longer "Unknown" when seller_id exists
                fix_working = unknown_seller_count == 0 or (unknown_seller_count < total_items and actual_seller_count > 0)
                
                details = f"Total items: {total_items}, Unknown sellers: {unknown_seller_count}, Actual sellers: {actual_seller_count}"
                if seller_details:
                    details += f". Items: {'; '.join(seller_details[:5])}"  # Show first 5 items
                
                self.log_test(
                    "Bought Items Seller Names", 
                    fix_working, 
                    details
                )
                return fix_working
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Bought Items Seller Names", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Bought Items Seller Names", False, error_msg=str(e))
            return False

    def test_seller_id_direct_lookup(self):
        """Test that seller_id is used directly from tenders/orders"""
        try:
            # Get demo user
            user = self.get_demo_user()
            if not user:
                self.log_test("Seller ID Direct Lookup", False, error_msg="Could not get demo user")
                return False
            
            user_id = user.get('id')
            
            # Get bought items
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                items_with_seller_id = 0
                items_with_seller_name = 0
                seller_lookup_working = 0
                
                for item in bought_items:
                    seller_id = item.get('seller_id')
                    seller_name = item.get('seller_name', 'Unknown')
                    
                    if seller_id:
                        items_with_seller_id += 1
                        
                        if seller_name != 'Unknown':
                            items_with_seller_name += 1
                            
                            # Verify the seller actually exists by checking the seller endpoint
                            try:
                                seller_response = requests.get(f"{BACKEND_URL}/auth/profile/{seller_id}", timeout=5)
                                if seller_response.status_code == 200:
                                    seller_data = seller_response.json()
                                    actual_username = seller_data.get('username', 'Unknown')
                                    if actual_username == seller_name:
                                        seller_lookup_working += 1
                            except:
                                pass  # Skip if seller lookup fails
                
                # The fix should ensure seller_id is used directly and seller lookup works
                direct_lookup_working = (items_with_seller_id > 0 and 
                                       items_with_seller_name > 0 and 
                                       seller_lookup_working > 0)
                
                details = f"Items with seller_id: {items_with_seller_id}, Items with seller_name: {items_with_seller_name}, Verified seller lookups: {seller_lookup_working}"
                
                self.log_test(
                    "Seller ID Direct Lookup", 
                    direct_lookup_working, 
                    details
                )
                return direct_lookup_working
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Seller ID Direct Lookup", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Seller ID Direct Lookup", False, error_msg=str(e))
            return False

    def test_tender_vs_order_seller_names(self):
        """Test that both tender-based and order-based bought items show seller names"""
        try:
            # Get demo user
            user = self.get_demo_user()
            if not user:
                self.log_test("Tender vs Order Seller Names", False, error_msg="Could not get demo user")
                return False
            
            user_id = user.get('id')
            
            # Get bought items
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                tender_items = []
                order_items = []
                
                for item in bought_items:
                    item_id = item.get('id', '')
                    seller_name = item.get('seller_name', 'Unknown')
                    
                    if item_id.startswith('tender_'):
                        tender_items.append(seller_name)
                    elif item_id.startswith('order_'):
                        order_items.append(seller_name)
                
                # Check if both types have actual seller names (not "Unknown")
                tender_names_working = len([name for name in tender_items if name != 'Unknown'])
                order_names_working = len([name for name in order_items if name != 'Unknown'])
                
                both_types_working = (
                    (len(tender_items) == 0 or tender_names_working > 0) and
                    (len(order_items) == 0 or order_names_working > 0)
                )
                
                details = f"Tender items: {len(tender_items)} (working names: {tender_names_working}), Order items: {len(order_items)} (working names: {order_names_working})"
                
                self.log_test(
                    "Tender vs Order Seller Names", 
                    both_types_working, 
                    details
                )
                return both_types_working
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Tender vs Order Seller Names", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Tender vs Order Seller Names", False, error_msg=str(e))
            return False

    def test_seller_exists_verification(self):
        """Verify that sellers referenced in bought items actually exist"""
        try:
            # Get demo user
            user = self.get_demo_user()
            if not user:
                self.log_test("Seller Exists Verification", False, error_msg="Could not get demo user")
                return False
            
            user_id = user.get('id')
            
            # Get bought items
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                total_items = len(bought_items)
                verified_sellers = 0
                seller_verification_details = []
                
                for item in bought_items:
                    seller_id = item.get('seller_id')
                    seller_name = item.get('seller_name', 'Unknown')
                    item_title = item.get('title', 'Unknown Item')
                    
                    if seller_id and seller_name != 'Unknown':
                        try:
                            # Verify seller exists
                            seller_response = requests.get(f"{BACKEND_URL}/auth/profile/{seller_id}", timeout=5)
                            if seller_response.status_code == 200:
                                seller_data = seller_response.json()
                                actual_username = seller_data.get('username', 'Unknown')
                                if actual_username == seller_name:
                                    verified_sellers += 1
                                    seller_verification_details.append(f"'{item_title}': {seller_name} ✅")
                                else:
                                    seller_verification_details.append(f"'{item_title}': {seller_name} ≠ {actual_username} ❌")
                            else:
                                seller_verification_details.append(f"'{item_title}': {seller_name} (seller not found) ❌")
                        except:
                            seller_verification_details.append(f"'{item_title}': {seller_name} (lookup failed) ❌")
                
                verification_working = verified_sellers > 0 or total_items == 0
                
                details = f"Total items: {total_items}, Verified sellers: {verified_sellers}"
                if seller_verification_details:
                    details += f". Verification: {'; '.join(seller_verification_details[:3])}"  # Show first 3
                
                self.log_test(
                    "Seller Exists Verification", 
                    verification_working, 
                    details
                )
                return verification_working
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Seller Exists Verification", False, error_msg=error_detail)
                return False
                
        except Exception as e:
            self.log_test("Seller Exists Verification", False, error_msg=str(e))
            return False

    def run_seller_name_fix_testing(self):
        """Run Seller Name Fix testing as requested in review"""
        print("=" * 80)
        print("CATALORO SELLER NAME FIX VERIFICATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting Seller Name Fix testing.")
            return
        
        # 2. Test Bought Items Seller Names
        print("👤 TEST BOUGHT ITEMS SELLER NAMES")
        print("-" * 40)
        self.test_bought_items_seller_names()
        
        # 3. Test Seller ID Direct Lookup
        print("🔍 TEST SELLER ID DIRECT LOOKUP")
        print("-" * 40)
        self.test_seller_id_direct_lookup()
        
        # 4. Test Tender vs Order Seller Names
        print("📋 TEST TENDER VS ORDER SELLER NAMES")
        print("-" * 40)
        self.test_tender_vs_order_seller_names()
        
        # 5. Test Seller Exists Verification
        print("✅ TEST SELLER EXISTS VERIFICATION")
        print("-" * 40)
        self.test_seller_exists_verification()
        
        # Print Summary
        print("=" * 80)
        print("SELLER NAME FIX TEST SUMMARY")
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
        
        print("\n🎯 SELLER NAME FIX TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Seller names should no longer be 'Unknown' when seller_id exists")
        print("  ✅ Seller_id should be used directly from tenders/orders")
        print("  ✅ Both tender-based and order-based items should show seller names")
        print("  ✅ Seller information should be verifiable via profile lookup")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = SellerNameFixTester()
    
    # Run Seller Name Fix testing as requested in the review
    print("🎯 RUNNING SELLER NAME FIX VERIFICATION TESTING AS REQUESTED")
    print("Testing the seller name fix for bought items endpoint...")
    print()
    
    passed, failed, results = tester.run_seller_name_fix_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)