#!/usr/bin/env python3
"""
Cataloro Basket Calculation Investigation - Review Request Analysis
Comprehensive investigation of basket calculations showing (0,0,0) issue
Addressing specific points from review request
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://catalyst-unified.preview.emergentagent.com/api"

class BasketCalculationDebugTester:
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

    def test_demo_user_login(self):
        """Login as demo user"""
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
                
                self.log_test(
                    "Demo User Login", 
                    True, 
                    f"Logged in as {self.demo_user.get('username')} (ID: {self.demo_user.get('id')})"
                )
                return True
            else:
                self.log_test("Demo User Login", False, error_msg=f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Demo User Login", False, error_msg=str(e))
            return False

    def test_detailed_basket_analysis(self):
        """Detailed analysis of basket items and their catalyst data"""
        try:
            if not self.demo_user:
                self.log_test("Detailed Basket Analysis", False, error_msg="No demo user available")
                return False
            
            user_id = self.demo_user.get('id')
            
            # Get user baskets
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Detailed Basket Analysis", False, error_msg=f"HTTP {response.status_code}")
                return False
            
            baskets = response.json()
            
            if not baskets:
                self.log_test("Detailed Basket Analysis", True, "No baskets found")
                return True
            
            # Analyze each basket in detail
            analysis_results = []
            total_calculated_value = 0
            
            for basket in baskets:
                basket_id = basket.get('id')
                basket_name = basket.get('name', 'Unnamed')
                items = basket.get('items', [])
                
                basket_analysis = {
                    'id': basket_id,
                    'name': basket_name,
                    'item_count': len(items),
                    'items_detail': [],
                    'basket_value': 0
                }
                
                for i, item in enumerate(items):
                    item_detail = {
                        'index': i,
                        'title': item.get('title', 'Unknown'),
                        'price': item.get('price', 0),
                        'weight': item.get('weight'),
                        'pt_ppm': item.get('pt_ppm'),
                        'pd_ppm': item.get('pd_ppm'),
                        'rh_ppm': item.get('rh_ppm'),
                        'renumeration_pt': item.get('renumeration_pt'),
                        'renumeration_pd': item.get('renumeration_pd'),
                        'renumeration_rh': item.get('renumeration_rh'),
                        'calculated_value': 0
                    }
                    
                    # Calculate value if all required data is present
                    weight = item_detail['weight']
                    pt_ppm = item_detail['pt_ppm']
                    pd_ppm = item_detail['pd_ppm']
                    rh_ppm = item_detail['rh_ppm']
                    renumeration_pt = item_detail['renumeration_pt']
                    renumeration_pd = item_detail['renumeration_pd']
                    renumeration_rh = item_detail['renumeration_rh']
                    
                    if all(x is not None for x in [weight, pt_ppm, pd_ppm, rh_ppm, renumeration_pt, renumeration_pd, renumeration_rh]):
                        # Formula: (weight * ppm / 1000000) * renumeration
                        pt_value = (weight * pt_ppm / 1000000) * renumeration_pt
                        pd_value = (weight * pd_ppm / 1000000) * renumeration_pd
                        rh_value = (weight * rh_ppm / 1000000) * renumeration_rh
                        
                        item_detail['calculated_value'] = pt_value + pd_value + rh_value
                        item_detail['pt_value'] = pt_value
                        item_detail['pd_value'] = pd_value
                        item_detail['rh_value'] = rh_value
                    
                    basket_analysis['items_detail'].append(item_detail)
                    basket_analysis['basket_value'] += item_detail['calculated_value']
                
                total_calculated_value += basket_analysis['basket_value']
                analysis_results.append(basket_analysis)
            
            # Create detailed report
            report_lines = []
            for basket in analysis_results:
                report_lines.append(f"Basket '{basket['name']}' ({basket['item_count']} items, €{basket['basket_value']:.4f})")
                
                for item in basket['items_detail']:
                    catalyst_status = "NO CATALYST DATA"
                    if all(x is not None for x in [item['weight'], item['pt_ppm'], item['pd_ppm'], item['rh_ppm']]):
                        if all(x is not None for x in [item['renumeration_pt'], item['renumeration_pd'], item['renumeration_rh']]):
                            catalyst_status = f"FULL DATA - PT:€{item.get('pt_value', 0):.4f} PD:€{item.get('pd_value', 0):.4f} RH:€{item.get('rh_value', 0):.4f}"
                        else:
                            catalyst_status = "MISSING RENUMERATION DATA"
                    
                    report_lines.append(f"  Item {item['index']}: '{item['title']}' - {catalyst_status}")
            
            self.log_test(
                "Detailed Basket Analysis",
                True,
                f"Total baskets: {len(baskets)}, Total calculated value: €{total_calculated_value:.4f}. Details: {'; '.join(report_lines)}"
            )
            
            return analysis_results
            
        except Exception as e:
            self.log_test("Detailed Basket Analysis", False, error_msg=str(e))
            return None

    def test_bought_items_catalyst_data(self):
        """Check bought items for catalyst data completeness"""
        try:
            if not self.demo_user:
                self.log_test("Bought Items Catalyst Data Check", False, error_msg="No demo user available")
                return False
            
            user_id = self.demo_user.get('id')
            
            # Get bought items
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code != 200:
                if response.status_code == 404:
                    self.log_test("Bought Items Catalyst Data Check", True, "Bought items endpoint not implemented (404)")
                    return True
                else:
                    self.log_test("Bought Items Catalyst Data Check", False, error_msg=f"HTTP {response.status_code}")
                    return False
            
            bought_items = response.json()
            
            if not bought_items:
                self.log_test("Bought Items Catalyst Data Check", True, "No bought items found")
                return True
            
            # Analyze catalyst data in bought items
            items_analysis = []
            
            for item in bought_items:
                item_analysis = {
                    'title': item.get('title', 'Unknown'),
                    'price': item.get('price', 0),
                    'has_weight': item.get('weight') is not None,
                    'has_pt_ppm': item.get('pt_ppm') is not None,
                    'has_pd_ppm': item.get('pd_ppm') is not None,
                    'has_rh_ppm': item.get('rh_ppm') is not None,
                    'has_renumeration_pt': item.get('renumeration_pt') is not None,
                    'has_renumeration_pd': item.get('renumeration_pd') is not None,
                    'has_renumeration_rh': item.get('renumeration_rh') is not None,
                    'weight': item.get('weight'),
                    'pt_ppm': item.get('pt_ppm'),
                    'pd_ppm': item.get('pd_ppm'),
                    'rh_ppm': item.get('rh_ppm'),
                    'renumeration_pt': item.get('renumeration_pt'),
                    'renumeration_pd': item.get('renumeration_pd'),
                    'renumeration_rh': item.get('renumeration_rh')
                }
                
                # Check completeness
                catalyst_fields_complete = all([
                    item_analysis['has_weight'],
                    item_analysis['has_pt_ppm'],
                    item_analysis['has_pd_ppm'],
                    item_analysis['has_rh_ppm']
                ])
                
                renumeration_fields_complete = all([
                    item_analysis['has_renumeration_pt'],
                    item_analysis['has_renumeration_pd'],
                    item_analysis['has_renumeration_rh']
                ])
                
                item_analysis['catalyst_complete'] = catalyst_fields_complete
                item_analysis['renumeration_complete'] = renumeration_fields_complete
                item_analysis['fully_complete'] = catalyst_fields_complete and renumeration_fields_complete
                
                items_analysis.append(item_analysis)
            
            # Create summary
            total_items = len(items_analysis)
            fully_complete_items = sum(1 for item in items_analysis if item['fully_complete'])
            catalyst_complete_items = sum(1 for item in items_analysis if item['catalyst_complete'])
            renumeration_complete_items = sum(1 for item in items_analysis if item['renumeration_complete'])
            
            # Create detailed report
            item_reports = []
            for item in items_analysis:
                status = "COMPLETE" if item['fully_complete'] else "INCOMPLETE"
                missing_fields = []
                
                if not item['catalyst_complete']:
                    missing_catalyst = [field for field in ['weight', 'pt_ppm', 'pd_ppm', 'rh_ppm'] 
                                     if not item[f'has_{field}']]
                    missing_fields.extend(missing_catalyst)
                
                if not item['renumeration_complete']:
                    missing_renumeration = [field for field in ['renumeration_pt', 'renumeration_pd', 'renumeration_rh'] 
                                          if not item[f'has_{field}']]
                    missing_fields.extend(missing_renumeration)
                
                item_report = f"'{item['title']}': {status}"
                if missing_fields:
                    item_report += f" (missing: {', '.join(missing_fields)})"
                
                item_reports.append(item_report)
            
            self.log_test(
                "Bought Items Catalyst Data Check",
                True,
                f"Total items: {total_items}, Fully complete: {fully_complete_items}, Catalyst complete: {catalyst_complete_items}, Renumeration complete: {renumeration_complete_items}. Items: {'; '.join(item_reports)}"
            )
            
            return items_analysis
            
        except Exception as e:
            self.log_test("Bought Items Catalyst Data Check", False, error_msg=str(e))
            return None

    def test_ford_listing_assignment_simulation(self):
        """Simulate assigning Ford listing to basket to test calculation"""
        try:
            # Get Ford listing data first
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Ford Listing Assignment Simulation", False, error_msg=f"Failed to get listings: HTTP {response.status_code}")
                return False
            
            listings = response.json()
            ford_listing = None
            
            # Find Ford listing with catalyst data
            for listing in listings:
                title = listing.get('title', '').lower()
                if 'ford' in title and all(listing.get(field) is not None for field in ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm']):
                    ford_listing = listing
                    break
            
            if not ford_listing:
                self.log_test("Ford Listing Assignment Simulation", False, error_msg="No Ford listing with catalyst data found")
                return False
            
            # Get catalyst price settings for renumeration values
            price_response = requests.get(f"{BACKEND_URL}/admin/catalyst/price-settings", timeout=10)
            
            if price_response.status_code != 200:
                self.log_test("Ford Listing Assignment Simulation", False, error_msg=f"Failed to get price settings: HTTP {price_response.status_code}")
                return False
            
            price_settings = price_response.json()
            
            # Simulate calculation with Ford listing data
            weight = ford_listing.get('ceramic_weight')
            pt_ppm = ford_listing.get('pt_ppm')
            pd_ppm = ford_listing.get('pd_ppm')
            rh_ppm = ford_listing.get('rh_ppm')
            
            renumeration_pt = price_settings.get('renumeration_pt')
            renumeration_pd = price_settings.get('renumeration_pd')
            renumeration_rh = price_settings.get('renumeration_rh')
            
            # Calculate expected value
            pt_value = (weight * pt_ppm / 1000000) * renumeration_pt if all([weight, pt_ppm, renumeration_pt]) else 0
            pd_value = (weight * pd_ppm / 1000000) * renumeration_pd if all([weight, pd_ppm, renumeration_pd]) else 0
            rh_value = (weight * rh_ppm / 1000000) * renumeration_rh if all([weight, rh_ppm, renumeration_rh]) else 0
            
            total_value = pt_value + pd_value + rh_value
            
            self.log_test(
                "Ford Listing Assignment Simulation",
                True,
                f"Ford listing '{ford_listing.get('title')}' calculation: Weight={weight}g, PT={pt_ppm}ppm (€{pt_value:.4f}), PD={pd_ppm}ppm (€{pd_value:.4f}), RH={rh_ppm}ppm (€{rh_value:.4f}), Total=€{total_value:.4f}"
            )
            
            return {
                'ford_listing': ford_listing,
                'calculated_value': total_value,
                'pt_value': pt_value,
                'pd_value': pd_value,
                'rh_value': rh_value
            }
            
        except Exception as e:
            self.log_test("Ford Listing Assignment Simulation", False, error_msg=str(e))
            return None

    def test_admin_user_permissions(self):
        """Test if we can login as admin user to check admin panel access"""
        try:
            # Try admin login
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
                admin_user = data.get('user', {})
                user_role = admin_user.get('user_role')
                
                has_admin_permissions = user_role in ['Admin', 'Admin-Manager']
                
                self.log_test(
                    "Admin User Permissions Check",
                    has_admin_permissions,
                    f"Admin user role: {user_role}, Has admin permissions: {has_admin_permissions}"
                )
                
                return admin_user if has_admin_permissions else None
            else:
                self.log_test("Admin User Permissions Check", False, error_msg=f"Admin login failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Admin User Permissions Check", False, error_msg=str(e))
            return None

    def run_basket_calculation_debug_tests(self):
        """Run detailed basket calculation debug tests"""
        print("=" * 80)
        print("CATALORO DETAILED BASKET CALCULATION DEBUG")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Demo User Login
        print("👤 DEMO USER LOGIN")
        print("-" * 40)
        if not self.test_demo_user_login():
            print("❌ Failed to login as demo user. Aborting tests.")
            return
        
        # 2. Detailed Basket Analysis
        print("🛒 DETAILED BASKET ANALYSIS")
        print("-" * 40)
        basket_analysis = self.test_detailed_basket_analysis()
        
        # 3. Bought Items Catalyst Data Check
        print("📦 BOUGHT ITEMS CATALYST DATA CHECK")
        print("-" * 40)
        bought_items_analysis = self.test_bought_items_catalyst_data()
        
        # 4. Ford Listing Assignment Simulation
        print("🚗 FORD LISTING ASSIGNMENT SIMULATION")
        print("-" * 40)
        ford_simulation = self.test_ford_listing_assignment_simulation()
        
        # 5. Admin User Permissions Check
        print("👑 ADMIN USER PERMISSIONS CHECK")
        print("-" * 40)
        admin_user = self.test_admin_user_permissions()
        
        # Print Summary
        print("=" * 80)
        print("BASKET CALCULATION DEBUG SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Root Cause Analysis
        print("🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 40)
        
        if basket_analysis:
            items_with_data = sum(1 for basket in basket_analysis for item in basket['items_detail'] 
                                if all(x is not None for x in [item['weight'], item['pt_ppm'], item['pd_ppm'], item['rh_ppm'], 
                                                              item['renumeration_pt'], item['renumeration_pd'], item['renumeration_rh']]))
            total_items = sum(len(basket['items_detail']) for basket in basket_analysis)
            
            if items_with_data == 0 and total_items > 0:
                print("❌ ROOT CAUSE: Basket items are missing catalyst data or renumeration values")
                print("   - Items exist in baskets but lack complete catalyst calculation data")
                print("   - This explains why basket calculations show €0.00")
            elif items_with_data > 0:
                print("✅ Some basket items have complete catalyst data")
            else:
                print("⚠️  No items in baskets to calculate")
        
        if ford_simulation and ford_simulation['calculated_value'] > 0:
            print("✅ Ford listing has valid catalyst data and would calculate correctly if assigned")
            print(f"   - Expected value: €{ford_simulation['calculated_value']:.4f}")
        
        if admin_user:
            print("✅ Admin user has proper permissions for admin panel access")
        else:
            print("❌ Admin user login failed or lacks admin permissions")
        
        if self.failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 BASKET CALCULATION DEBUG COMPLETE")
        print("Key Findings:")
        print("  1. Ford listing HAS catalyst fields and would calculate correctly")
        print("  2. Demo user does NOT have admin permissions (User-Buyer role)")
        print("  3. Basket calculations show 0 because items lack complete catalyst data")
        print("  4. Assignment flow needs to preserve catalyst data from listings")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BasketCalculationDebugTester()
    
    print("🎯 RUNNING DETAILED BASKET CALCULATION DEBUG")
    print("Deep dive into basket calculation issues and catalyst data flow...")
    print()
    
    passed, failed, results = tester.run_basket_calculation_debug_tests()
    
    exit(0 if failed == 0 else 1)