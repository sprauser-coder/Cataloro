#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Ford Listing Catalyst Fields and Basket Calculation Debug
Testing Ford listing catalyst fields, demo user permissions, and basket calculation issues
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://marketplace-repair-1.preview.emergentagent.com/api"

class FordListingDebugTester:
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

    def test_demo_user_login_and_permissions(self):
        """Test demo user login and check their permissions for admin features"""
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
                user_role = user.get('user_role')
                user_id = user.get('id')
                registration_status = user.get('registration_status')
                
                # Check if user has admin permissions
                has_admin_permissions = user_role in ['Admin', 'Admin-Manager']
                
                # Store demo user for later tests
                self.demo_user = user
                
                self.log_test(
                    "Demo User Login and Permissions Check", 
                    True, 
                    f"Demo user logged in. Role: {user_role}, Status: {registration_status}, Has Admin Permissions: {has_admin_permissions}, User ID: {user_id}"
                )
                return user, has_admin_permissions
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Demo User Login and Permissions Check", False, error_msg=error_detail)
                return None, False
        except Exception as e:
            self.log_test("Demo User Login and Permissions Check", False, error_msg=str(e))
            return None, False

    def test_ford_listing_catalyst_fields(self):
        """Check Ford listing directly to verify catalyst fields are present"""
        try:
            # First, get all listings to find Ford listing
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Ford Listing Catalyst Fields Check", False, error_msg=f"Failed to get listings: HTTP {response.status_code}")
                return False
            
            listings = response.json()
            ford_listing = None
            
            # Look for Ford listing
            for listing in listings:
                title = listing.get('title', '').lower()
                if 'ford' in title or 'f150' in title or 'f-150' in title:
                    ford_listing = listing
                    break
            
            if not ford_listing:
                self.log_test("Ford Listing Catalyst Fields Check", False, error_msg="No Ford listing found in browse results")
                return False
            
            # Check catalyst fields
            catalyst_fields = {
                'ceramic_weight': ford_listing.get('ceramic_weight'),
                'pt_ppm': ford_listing.get('pt_ppm'),
                'pd_ppm': ford_listing.get('pd_ppm'),
                'rh_ppm': ford_listing.get('rh_ppm')
            }
            
            # Check if all catalyst fields are present and not None
            fields_present = all(field is not None for field in catalyst_fields.values())
            
            # Get specific values for reporting
            field_details = []
            for field_name, field_value in catalyst_fields.items():
                if field_value is not None:
                    field_details.append(f"{field_name}: {field_value}")
                else:
                    field_details.append(f"{field_name}: MISSING")
            
            self.log_test(
                "Ford Listing Catalyst Fields Check",
                fields_present,
                f"Ford listing ID: {ford_listing.get('id')}, Title: {ford_listing.get('title')}, Catalyst fields: {', '.join(field_details)}"
            )
            
            return ford_listing if fields_present else None
            
        except Exception as e:
            self.log_test("Ford Listing Catalyst Fields Check", False, error_msg=str(e))
            return None

    def test_current_basket_state(self):
        """GET current basket data to see why calculations are showing 0"""
        try:
            if not self.demo_user:
                self.log_test("Current Basket State Check", False, error_msg="No demo user available")
                return False
            
            user_id = self.demo_user.get('id')
            
            # Get user baskets
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                if not baskets:
                    self.log_test(
                        "Current Basket State Check",
                        True,
                        "No baskets found for demo user (this explains why calculations show 0)"
                    )
                    return True
                
                # Analyze basket contents
                basket_details = []
                total_items = 0
                total_value = 0
                
                for basket in baskets:
                    basket_id = basket.get('id')
                    basket_name = basket.get('name')
                    items = basket.get('items', [])
                    item_count = len(items)
                    total_items += item_count
                    
                    # Calculate basket value if items have catalyst data
                    basket_value = 0
                    for item in items:
                        # Check if item has catalyst calculation data
                        weight = item.get('weight', 0)
                        pt_ppm = item.get('pt_ppm', 0)
                        pd_ppm = item.get('pd_ppm', 0)
                        rh_ppm = item.get('rh_ppm', 0)
                        renumeration_pt = item.get('renumeration_pt', 0)
                        renumeration_pd = item.get('renumeration_pd', 0)
                        renumeration_rh = item.get('renumeration_rh', 0)
                        
                        # Calculate value using formula: (weight * ppm / 1000000) * renumeration
                        pt_value = (weight * pt_ppm / 1000000) * renumeration_pt if all([weight, pt_ppm, renumeration_pt]) else 0
                        pd_value = (weight * pd_ppm / 1000000) * renumeration_pd if all([weight, pd_ppm, renumeration_pd]) else 0
                        rh_value = (weight * rh_ppm / 1000000) * renumeration_rh if all([weight, rh_ppm, renumeration_rh]) else 0
                        
                        item_value = pt_value + pd_value + rh_value
                        basket_value += item_value
                    
                    total_value += basket_value
                    basket_details.append(f"Basket '{basket_name}' (ID: {basket_id}): {item_count} items, Value: €{basket_value:.2f}")
                
                self.log_test(
                    "Current Basket State Check",
                    True,
                    f"Found {len(baskets)} baskets with {total_items} total items. Total calculated value: €{total_value:.2f}. Details: {'; '.join(basket_details)}"
                )
                
                return baskets
                
            elif response.status_code == 404:
                self.log_test(
                    "Current Basket State Check",
                    True,
                    "Baskets endpoint returned 404 - endpoint may not be implemented yet"
                )
                return None
            else:
                self.log_test("Current Basket State Check", False, error_msg=f"HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Current Basket State Check", False, error_msg=str(e))
            return None

    def test_assignment_flow(self):
        """Test complete assignment flow to verify basket calculations"""
        try:
            if not self.demo_user:
                self.log_test("Assignment Flow Test", False, error_msg="No demo user available")
                return False
            
            user_id = self.demo_user.get('id')
            
            # Test bought items endpoint (this is where assignments would show up)
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                if not bought_items:
                    self.log_test(
                        "Assignment Flow Test",
                        True,
                        "No bought items found for demo user (no assignments have been made)"
                    )
                    return True
                
                # Analyze bought items for Ford items
                ford_items = []
                total_items = len(bought_items)
                
                for item in bought_items:
                    title = item.get('title', '').lower()
                    if 'ford' in title or 'f150' in title or 'f-150' in title:
                        ford_items.append(item)
                
                # Check catalyst data in bought items
                items_with_catalyst = 0
                items_without_catalyst = 0
                
                for item in bought_items:
                    has_catalyst_data = all([
                        item.get('weight') is not None,
                        item.get('pt_ppm') is not None,
                        item.get('pd_ppm') is not None,
                        item.get('rh_ppm') is not None
                    ])
                    
                    if has_catalyst_data:
                        items_with_catalyst += 1
                    else:
                        items_without_catalyst += 1
                
                self.log_test(
                    "Assignment Flow Test",
                    True,
                    f"Found {total_items} bought items, {len(ford_items)} Ford items. Items with catalyst data: {items_with_catalyst}, without: {items_without_catalyst}"
                )
                
                return bought_items
                
            elif response.status_code == 404:
                self.log_test(
                    "Assignment Flow Test",
                    True,
                    "Bought items endpoint returned 404 - endpoint may not be implemented yet"
                )
                return None
            else:
                self.log_test("Assignment Flow Test", False, error_msg=f"HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Assignment Flow Test", False, error_msg=str(e))
            return None

    def test_catalyst_price_settings(self):
        """Check catalyst price settings that affect basket calculations"""
        try:
            # Get catalyst price settings
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/price-settings", timeout=10)
            
            if response.status_code == 200:
                settings = response.json()
                
                # Check if all required price settings are present
                required_fields = ['pt_price', 'pd_price', 'rh_price', 'renumeration_pt', 'renumeration_pd', 'renumeration_rh']
                missing_fields = []
                present_fields = []
                
                for field in required_fields:
                    if field in settings and settings[field] is not None:
                        present_fields.append(f"{field}: {settings[field]}")
                    else:
                        missing_fields.append(field)
                
                all_fields_present = len(missing_fields) == 0
                
                self.log_test(
                    "Catalyst Price Settings Check",
                    all_fields_present,
                    f"Price settings present: {', '.join(present_fields)}" + (f". Missing: {', '.join(missing_fields)}" if missing_fields else "")
                )
                
                return settings if all_fields_present else None
                
            elif response.status_code == 404:
                self.log_test(
                    "Catalyst Price Settings Check",
                    False,
                    "Catalyst price settings endpoint returned 404 - may not be implemented"
                )
                return None
            else:
                self.log_test("Catalyst Price Settings Check", False, error_msg=f"HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Catalyst Price Settings Check", False, error_msg=str(e))
            return None

    def test_marketplace_browse_with_catalyst_data(self):
        """Test marketplace browse to see if listings have catalyst data"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Marketplace Browse Catalyst Data Check", False, error_msg=f"HTTP {response.status_code}")
                return False
            
            listings = response.json()
            
            if not listings:
                self.log_test("Marketplace Browse Catalyst Data Check", False, error_msg="No listings found")
                return False
            
            # Analyze catalyst data in listings
            total_listings = len(listings)
            listings_with_catalyst = 0
            ford_listings = []
            
            for listing in listings:
                title = listing.get('title', '')
                
                # Check if listing has catalyst fields
                has_catalyst_data = all([
                    listing.get('ceramic_weight') is not None,
                    listing.get('pt_ppm') is not None,
                    listing.get('pd_ppm') is not None,
                    listing.get('rh_ppm') is not None
                ])
                
                if has_catalyst_data:
                    listings_with_catalyst += 1
                
                # Check for Ford listings
                if 'ford' in title.lower() or 'f150' in title.lower() or 'f-150' in title.lower():
                    ford_listings.append({
                        'id': listing.get('id'),
                        'title': title,
                        'has_catalyst': has_catalyst_data,
                        'ceramic_weight': listing.get('ceramic_weight'),
                        'pt_ppm': listing.get('pt_ppm'),
                        'pd_ppm': listing.get('pd_ppm'),
                        'rh_ppm': listing.get('rh_ppm')
                    })
            
            ford_details = []
            for ford in ford_listings:
                catalyst_info = f"Catalyst: {ford['has_catalyst']}"
                if ford['has_catalyst']:
                    catalyst_info += f" (weight: {ford['ceramic_weight']}, PT: {ford['pt_ppm']}, PD: {ford['pd_ppm']}, RH: {ford['rh_ppm']})"
                ford_details.append(f"'{ford['title']}' - {catalyst_info}")
            
            self.log_test(
                "Marketplace Browse Catalyst Data Check",
                True,
                f"Found {total_listings} listings, {listings_with_catalyst} with catalyst data, {len(ford_listings)} Ford listings. Ford details: {'; '.join(ford_details) if ford_details else 'None'}"
            )
            
            return ford_listings
            
        except Exception as e:
            self.log_test("Marketplace Browse Catalyst Data Check", False, error_msg=str(e))
            return None

    def run_ford_listing_debug_tests(self):
        """Run Ford Listing Debug testing as requested in review"""
        print("=" * 80)
        print("CATALORO FORD LISTING CATALYST FIELDS & BASKET CALCULATION DEBUG")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting Ford Listing debug tests.")
            return
        
        # 2. Demo User Login and Permissions Check
        print("👤 DEMO USER LOGIN AND PERMISSIONS CHECK")
        print("-" * 40)
        demo_user, has_admin_permissions = self.test_demo_user_login_and_permissions()
        
        if not demo_user:
            print("❌ Failed to login as demo user. Aborting tests.")
            return
        
        # 3. Check Ford Listing Catalyst Fields
        print("🚗 FORD LISTING CATALYST FIELDS CHECK")
        print("-" * 40)
        ford_listing = self.test_ford_listing_catalyst_fields()
        
        # 4. Check Current Basket State
        print("🛒 CURRENT BASKET STATE CHECK")
        print("-" * 40)
        baskets = self.test_current_basket_state()
        
        # 5. Test Assignment Flow
        print("🔄 ASSIGNMENT FLOW TEST")
        print("-" * 40)
        bought_items = self.test_assignment_flow()
        
        # 6. Check Catalyst Price Settings
        print("💰 CATALYST PRICE SETTINGS CHECK")
        print("-" * 40)
        price_settings = self.test_catalyst_price_settings()
        
        # 7. Marketplace Browse with Catalyst Data
        print("📋 MARKETPLACE BROWSE CATALYST DATA CHECK")
        print("-" * 40)
        ford_listings_data = self.test_marketplace_browse_with_catalyst_data()
        
        # Print Summary
        print("=" * 80)
        print("FORD LISTING DEBUG TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Analysis and Recommendations
        print("🔍 ANALYSIS AND FINDINGS:")
        print("-" * 40)
        
        if ford_listing:
            print("✅ Ford listing found with catalyst fields")
        else:
            print("❌ Ford listing missing catalyst fields or not found")
        
        if has_admin_permissions:
            print("✅ Demo user has admin permissions")
        else:
            print("⚠️  Demo user does not have admin permissions")
        
        if baskets and any(basket.get('items') for basket in baskets):
            print("✅ User has baskets with items")
        else:
            print("⚠️  User has no basket items (explains 0 calculations)")
        
        if price_settings:
            print("✅ Catalyst price settings are configured")
        else:
            print("❌ Catalyst price settings missing or incomplete")
        
        if self.failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 FORD LISTING DEBUG TESTING COMPLETE")
        print("Key Issues to Address:")
        print("  1. Verify Ford listing has catalyst fields (ceramic_weight, pt_ppm, pd_ppm, rh_ppm)")
        print("  2. Check if demo user has Admin/Admin-Manager role for admin panel access")
        print("  3. Investigate why basket calculations show 0 (likely no assigned items)")
        print("  4. Ensure assignment/unassignment flow is working correctly")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = FordListingDebugTester()
    
    # Run Ford Listing Debug testing as requested in the review
    print("🎯 RUNNING FORD LISTING CATALYST FIELDS & BASKET CALCULATION DEBUG")
    print("Investigating Ford listing catalyst fields and basket calculation issues...")
    print()
    
    passed, failed, results = tester.run_ford_listing_debug_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)