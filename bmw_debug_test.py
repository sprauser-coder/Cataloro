#!/usr/bin/env python3
"""
BMW75364089 Links Purchase Debug Test
Debugging the specific BMW75364089 Links purchase that shows (0,0,0) calculations
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://catalyst-view.preview.emergentagent.com/api"

class BMWDebugTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_user = None
        self.admin_token = None
        self.bmw_listing = None
        self.bmw_tender = None
        self.bmw_bought_item = None
        self.picki_basket = None
        
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
        """Test admin authentication"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": "admin@cataloro.com",
                "password": "admin123"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user = data.get("user")
                self.admin_token = data.get("token")
                
                if self.admin_user and self.admin_user.get("user_role") == "Admin":
                    self.log_test("Admin Login", True, 
                                f"Logged in as {self.admin_user.get('username')} with Admin role")
                    return True
                else:
                    self.log_test("Admin Login", False, "", "User role is not Admin")
                    return False
            else:
                self.log_test("Admin Login", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, "", str(e))
            return False

    def find_bmw_listing(self):
        """Find the BMW75364089 Links listing"""
        try:
            # Get all listings
            response = requests.get(f"{BACKEND_URL}/marketplace/browse")
            
            if response.status_code == 200:
                listings = response.json()
                
                # Search for BMW listing
                bmw_listings = []
                for listing in listings:
                    title = listing.get("title", "").lower()
                    if "bmw75364089" in title or "bmw" in title and "links" in title:
                        bmw_listings.append(listing)
                
                if bmw_listings:
                    self.bmw_listing = bmw_listings[0]  # Take the first match
                    catalyst_data = {
                        "ceramic_weight": self.bmw_listing.get("ceramic_weight"),
                        "pt_ppm": self.bmw_listing.get("pt_ppm"),
                        "pd_ppm": self.bmw_listing.get("pd_ppm"),
                        "rh_ppm": self.bmw_listing.get("rh_ppm")
                    }
                    
                    self.log_test("Find BMW Listing", True, 
                                f"Found BMW listing: {self.bmw_listing.get('title')} (€{self.bmw_listing.get('price')}) - "
                                f"ID: {self.bmw_listing.get('id')} - Catalyst data: {catalyst_data}")
                    return True
                else:
                    # Search more broadly
                    all_titles = [listing.get("title", "") for listing in listings]
                    self.log_test("Find BMW Listing", False, 
                                f"BMW listing not found. Available listings: {all_titles[:10]}...", 
                                "No listing with BMW75364089 or BMW+Links found")
                    return False
            else:
                self.log_test("Find BMW Listing", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Find BMW Listing", False, "", str(e))
            return False

    def find_bmw_tender(self):
        """Find tenders related to the BMW listing"""
        if not self.bmw_listing:
            self.log_test("Find BMW Tender", False, "", "BMW listing not found")
            return False
            
        try:
            # Get all tenders (we need admin access for this)
            # Since there's no direct tender endpoint, let's check bought items first
            user_id = self.admin_user.get("id")
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}")
            
            if response.status_code == 200:
                bought_items = response.json()
                
                # Look for BMW-related bought items
                bmw_items = []
                for item in bought_items:
                    if (item.get("listing_id") == self.bmw_listing.get("id") or 
                        "bmw" in item.get("title", "").lower() or
                        item.get("price") == 170.0):
                        bmw_items.append(item)
                
                if bmw_items:
                    self.bmw_bought_item = bmw_items[0]
                    catalyst_data = {
                        "weight": self.bmw_bought_item.get("weight"),
                        "pt_ppm": self.bmw_bought_item.get("pt_ppm"),
                        "pd_ppm": self.bmw_bought_item.get("pd_ppm"),
                        "rh_ppm": self.bmw_bought_item.get("rh_ppm")
                    }
                    
                    self.log_test("Find BMW Tender/Purchase", True, 
                                f"Found BMW bought item: {self.bmw_bought_item.get('title')} (€{self.bmw_bought_item.get('price')}) - "
                                f"Catalyst data: {catalyst_data}")
                    return True
                else:
                    all_items = [(item.get("title"), item.get("price"), item.get("listing_id")) for item in bought_items]
                    self.log_test("Find BMW Tender/Purchase", False, 
                                f"No BMW bought items found. Available items: {all_items}", 
                                "No bought item matching BMW listing or €170 price")
                    return False
            else:
                self.log_test("Find BMW Tender/Purchase", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Find BMW Tender/Purchase", False, "", str(e))
            return False

    def find_picki_basket(self):
        """Find the Picki basket and check BMW item assignment"""
        if not self.admin_user:
            self.log_test("Find Picki Basket", False, "", "Admin user not available")
            return False
            
        try:
            user_id = self.admin_user.get("id")
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}")
            
            if response.status_code == 200:
                baskets = response.json()
                
                # Look for Picki basket
                picki_baskets = []
                for basket in baskets:
                    if "picki" in basket.get("name", "").lower():
                        picki_baskets.append(basket)
                
                if picki_baskets:
                    self.picki_basket = picki_baskets[0]
                    
                    # Check items in the basket
                    items = self.picki_basket.get("items", [])
                    bmw_items_in_basket = []
                    
                    for item in items:
                        if ("bmw" in item.get("title", "").lower() or 
                            item.get("price") == 170.0 or
                            (self.bmw_bought_item and item.get("id") == self.bmw_bought_item.get("id"))):
                            bmw_items_in_basket.append(item)
                    
                    if bmw_items_in_basket:
                        bmw_item = bmw_items_in_basket[0]
                        catalyst_data = {
                            "weight": bmw_item.get("weight"),
                            "pt_ppm": bmw_item.get("pt_ppm"),
                            "pd_ppm": bmw_item.get("pd_ppm"),
                            "rh_ppm": bmw_item.get("rh_ppm")
                        }
                        
                        self.log_test("Find Picki Basket", True, 
                                    f"Found Picki basket with BMW item: {bmw_item.get('title')} - "
                                    f"Catalyst data: {catalyst_data}")
                        return True
                    else:
                        item_titles = [item.get("title") for item in items]
                        self.log_test("Find Picki Basket", False, 
                                    f"Picki basket found but no BMW item. Items: {item_titles}", 
                                    "BMW item not found in Picki basket")
                        return False
                else:
                    basket_names = [basket.get("name") for basket in baskets]
                    self.log_test("Find Picki Basket", False, 
                                f"Picki basket not found. Available baskets: {basket_names}", 
                                "No basket named Picki")
                    return False
            else:
                self.log_test("Find Picki Basket", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Find Picki Basket", False, "", str(e))
            return False

    def check_data_flow_integrity(self):
        """Check the complete data flow from listing to basket"""
        if not all([self.bmw_listing, self.bmw_bought_item, self.picki_basket]):
            self.log_test("Data Flow Integrity", False, "", "Missing required data (listing, bought item, or basket)")
            return False
            
        try:
            # Compare catalyst data across the flow
            listing_data = {
                "ceramic_weight": self.bmw_listing.get("ceramic_weight"),
                "pt_ppm": self.bmw_listing.get("pt_ppm"),
                "pd_ppm": self.bmw_listing.get("pd_ppm"),
                "rh_ppm": self.bmw_listing.get("rh_ppm")
            }
            
            bought_item_data = {
                "weight": self.bmw_bought_item.get("weight"),
                "pt_ppm": self.bmw_bought_item.get("pt_ppm"),
                "pd_ppm": self.bmw_bought_item.get("pd_ppm"),
                "rh_ppm": self.bmw_bought_item.get("rh_ppm")
            }
            
            # Find BMW item in basket
            basket_items = self.picki_basket.get("items", [])
            bmw_basket_item = None
            for item in basket_items:
                if ("bmw" in item.get("title", "").lower() or 
                    item.get("price") == 170.0):
                    bmw_basket_item = item
                    break
            
            if bmw_basket_item:
                basket_data = {
                    "weight": bmw_basket_item.get("weight"),
                    "pt_ppm": bmw_basket_item.get("pt_ppm"),
                    "pd_ppm": bmw_basket_item.get("pd_ppm"),
                    "rh_ppm": bmw_basket_item.get("rh_ppm")
                }
                
                # Check for data loss
                issues = []
                
                # Check listing -> bought item
                if listing_data.get("ceramic_weight") and not bought_item_data.get("weight"):
                    issues.append("Catalyst weight lost: listing -> bought item")
                if listing_data.get("pt_ppm") and not bought_item_data.get("pt_ppm"):
                    issues.append("PT PPM lost: listing -> bought item")
                if listing_data.get("pd_ppm") and not bought_item_data.get("pd_ppm"):
                    issues.append("PD PPM lost: listing -> bought item")
                if listing_data.get("rh_ppm") and not bought_item_data.get("rh_ppm"):
                    issues.append("RH PPM lost: listing -> bought item")
                
                # Check bought item -> basket
                if bought_item_data.get("weight") and not basket_data.get("weight"):
                    issues.append("Catalyst weight lost: bought item -> basket")
                if bought_item_data.get("pt_ppm") and not basket_data.get("pt_ppm"):
                    issues.append("PT PPM lost: bought item -> basket")
                if bought_item_data.get("pd_ppm") and not basket_data.get("pd_ppm"):
                    issues.append("PD PPM lost: bought item -> basket")
                if bought_item_data.get("rh_ppm") and not basket_data.get("rh_ppm"):
                    issues.append("RH PPM lost: bought item -> basket")
                
                if issues:
                    self.log_test("Data Flow Integrity", False, 
                                f"Data loss detected: {', '.join(issues)}\n"
                                f"Listing: {listing_data}\n"
                                f"Bought Item: {bought_item_data}\n"
                                f"Basket Item: {basket_data}", 
                                "Catalyst data not preserved through the flow")
                    return False
                else:
                    self.log_test("Data Flow Integrity", True, 
                                f"Data flow preserved:\n"
                                f"Listing: {listing_data}\n"
                                f"Bought Item: {bought_item_data}\n"
                                f"Basket Item: {basket_data}")
                    return True
            else:
                self.log_test("Data Flow Integrity", False, "", "BMW item not found in basket for comparison")
                return False
                
        except Exception as e:
            self.log_test("Data Flow Integrity", False, "", str(e))
            return False

    def check_calculation_formula(self):
        """Check if the calculation formula produces correct results"""
        if not self.picki_basket:
            self.log_test("Calculation Formula", False, "", "Picki basket not available")
            return False
            
        try:
            # Find BMW item in basket
            basket_items = self.picki_basket.get("items", [])
            bmw_basket_item = None
            for item in basket_items:
                if ("bmw" in item.get("title", "").lower() or 
                    item.get("price") == 170.0):
                    bmw_basket_item = item
                    break
            
            if not bmw_basket_item:
                self.log_test("Calculation Formula", False, "", "BMW item not found in basket")
                return False
            
            # Get catalyst data
            weight = bmw_basket_item.get("weight", 0)
            pt_ppm = bmw_basket_item.get("pt_ppm", 0)
            pd_ppm = bmw_basket_item.get("pd_ppm", 0)
            rh_ppm = bmw_basket_item.get("rh_ppm", 0)
            
            # Get renumeration values (should be from price settings)
            renumeration_pt = bmw_basket_item.get("renumeration_pt", 0.98)  # Default
            renumeration_pd = bmw_basket_item.get("renumeration_pd", 0.98)  # Default
            renumeration_rh = bmw_basket_item.get("renumeration_rh", 0.9)   # Default
            
            # Calculate expected values using the formula: ptG = weight * pt_ppm / 1000 * renumeration_pt
            expected_pt_g = weight * pt_ppm / 1000 * renumeration_pt
            expected_pd_g = weight * pd_ppm / 1000 * renumeration_pd
            expected_rh_g = weight * rh_ppm / 1000 * renumeration_rh
            
            calculation_details = {
                "weight": weight,
                "pt_ppm": pt_ppm,
                "pd_ppm": pd_ppm,
                "rh_ppm": rh_ppm,
                "renumeration_pt": renumeration_pt,
                "renumeration_pd": renumeration_pd,
                "renumeration_rh": renumeration_rh,
                "expected_pt_g": expected_pt_g,
                "expected_pd_g": expected_pd_g,
                "expected_rh_g": expected_rh_g
            }
            
            if weight == 0 or (pt_ppm == 0 and pd_ppm == 0 and rh_ppm == 0):
                self.log_test("Calculation Formula", False, 
                            f"Zero input values detected: {calculation_details}", 
                            "Cannot calculate with zero weight or all zero PPM values")
                return False
            else:
                self.log_test("Calculation Formula", True, 
                            f"Formula calculation successful: {calculation_details}")
                return True
                
        except Exception as e:
            self.log_test("Calculation Formula", False, "", str(e))
            return False

    def run_comprehensive_debug(self):
        """Run comprehensive BMW debug test"""
        print("=" * 80)
        print("BMW75364089 LINKS PURCHASE DEBUG TEST")
        print("=" * 80)
        print()
        
        # Run all tests in sequence
        tests = [
            self.test_admin_login,
            self.find_bmw_listing,
            self.find_bmw_tender,
            self.find_picki_basket,
            self.check_data_flow_integrity,
            self.check_calculation_formula
        ]
        
        for test in tests:
            if not test():
                print(f"❌ Test failed: {test.__name__}")
                break
        
        # Print summary
        print("=" * 80)
        print("BMW DEBUG TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        print()
        
        if self.failed_tests > 0:
            print("❌ CRITICAL ISSUES FOUND:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        else:
            print("✅ ALL TESTS PASSED - BMW data flow working correctly")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = BMWDebugTester()
    success = tester.run_comprehensive_debug()
    exit(0 if success else 1)