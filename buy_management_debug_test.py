#!/usr/bin/env python3
"""
Cataloro Buy Management Calculation Debug Test
Investigating the specific issue where basket calculations show (0,0,0) for Pt, Pd, and Rh values
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://mega-dashboard.preview.emergentagent.com/api"

class BuyManagementDebugger:
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
                print(f"Failed to login demo user: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting demo user: {e}")
            return None

    def test_listings_catalyst_data(self):
        """Check if there are any listings with catalyst fields (ceramic_weight, pt_ppm, pd_ppm, rh_ppm) with non-zero values"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                catalyst_listings = []
                non_zero_catalyst_listings = []
                
                for listing in listings:
                    # Check if listing has catalyst fields
                    ceramic_weight = listing.get('ceramic_weight')
                    pt_ppm = listing.get('pt_ppm')
                    pd_ppm = listing.get('pd_ppm')
                    rh_ppm = listing.get('rh_ppm')
                    
                    has_catalyst_fields = any([
                        ceramic_weight is not None,
                        pt_ppm is not None,
                        pd_ppm is not None,
                        rh_ppm is not None
                    ])
                    
                    if has_catalyst_fields:
                        listing_data = {
                            'id': listing.get('id'),
                            'title': listing.get('title'),
                            'ceramic_weight': ceramic_weight,
                            'pt_ppm': pt_ppm,
                            'pd_ppm': pd_ppm,
                            'rh_ppm': rh_ppm
                        }
                        catalyst_listings.append(listing_data)
                        
                        # Check if any values are non-zero
                        has_non_zero_values = any([
                            (ceramic_weight or 0) > 0,
                            (pt_ppm or 0) > 0,
                            (pd_ppm or 0) > 0,
                            (rh_ppm or 0) > 0
                        ])
                        
                        if has_non_zero_values:
                            non_zero_catalyst_listings.append(listing_data)
                
                success = len(non_zero_catalyst_listings) > 0
                details = f"Total listings: {len(listings)}, With catalyst fields: {len(catalyst_listings)}, With non-zero catalyst values: {len(non_zero_catalyst_listings)}"
                
                if non_zero_catalyst_listings:
                    details += f"\n\nListings with non-zero catalyst data:"
                    for listing in non_zero_catalyst_listings[:5]:  # Show first 5
                        details += f"\n  - {listing['title']}: weight={listing['ceramic_weight']}, pt={listing['pt_ppm']}, pd={listing['pd_ppm']}, rh={listing['rh_ppm']}"
                
                self.log_test(
                    "1. Listings Catalyst Data Check",
                    success,
                    details,
                    "❌ ISSUE: No listings found with non-zero catalyst values" if not success else ""
                )
                
                return non_zero_catalyst_listings
            else:
                self.log_test("1. Listings Catalyst Data Check", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("1. Listings Catalyst Data Check", False, error_msg=str(e))
            return []

    def test_baskets_with_items(self, user_id):
        """Check if there are any baskets with items assigned to them"""
        try:
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                baskets_with_items = []
                total_items = 0
                
                for basket in baskets:
                    items = basket.get('items', [])
                    if items:
                        basket_data = {
                            'id': basket.get('id'),
                            'name': basket.get('name'),
                            'item_count': len(items),
                            'items': []
                        }
                        
                        for item in items:
                            item_data = {
                                'id': item.get('id'),
                                'title': item.get('title'),
                                'weight': item.get('weight'),
                                'pt_ppm': item.get('pt_ppm'),
                                'pd_ppm': item.get('pd_ppm'),
                                'rh_ppm': item.get('rh_ppm'),
                                'renumeration_pt': item.get('renumeration_pt'),
                                'renumeration_pd': item.get('renumeration_pd'),
                                'renumeration_rh': item.get('renumeration_rh')
                            }
                            basket_data['items'].append(item_data)
                        
                        baskets_with_items.append(basket_data)
                        total_items += len(items)
                
                success = len(baskets_with_items) > 0
                details = f"Total baskets: {len(baskets)}, Baskets with items: {len(baskets_with_items)}, Total items: {total_items}"
                
                if baskets_with_items:
                    details += f"\n\nBaskets with items:"
                    for basket in baskets_with_items[:3]:  # Show first 3
                        details += f"\n  - Basket '{basket['name']}': {basket['item_count']} items"
                        for item in basket['items'][:2]:  # Show first 2 items per basket
                            details += f"\n    * {item['title']}: weight={item['weight']}, pt_ppm={item['pt_ppm']}, renumeration_pt={item['renumeration_pt']}"
                
                self.log_test(
                    "2. Baskets with Items Check",
                    success,
                    details,
                    "❌ ISSUE: No baskets found with items assigned" if not success else ""
                )
                
                return baskets_with_items
            else:
                self.log_test("2. Baskets with Items Check", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("2. Baskets with Items Check", False, error_msg=str(e))
            return []

    def test_basket_api_endpoint(self, user_id):
        """Test the GET /api/user/baskets/{user_id} endpoint to see what data is being returned"""
        try:
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                # Calculate totals using frontend logic
                total_ptG = 0
                total_pdG = 0
                total_rhG = 0
                calculation_details = []
                
                for basket in baskets:
                    items = basket.get('items', [])
                    for item in items:
                        weight = item.get('weight', 0) or 0
                        pt_ppm = item.get('pt_ppm', 0) or 0
                        pd_ppm = item.get('pd_ppm', 0) or 0
                        rh_ppm = item.get('rh_ppm', 0) or 0
                        renumeration_pt = item.get('renumeration_pt', 0) or 0
                        renumeration_pd = item.get('renumeration_pd', 0) or 0
                        renumeration_rh = item.get('renumeration_rh', 0) or 0
                        
                        # Frontend calculation logic:
                        # ptG = weight * pt_ppm / 1000 * renumeration_pt
                        ptG = weight * pt_ppm / 1000 * renumeration_pt
                        pdG = weight * pd_ppm / 1000 * renumeration_pd
                        rhG = weight * rh_ppm / 1000 * renumeration_rh
                        
                        total_ptG += ptG
                        total_pdG += pdG
                        total_rhG += rhG
                        
                        calculation_details.append({
                            'item': item.get('title', 'Unknown'),
                            'weight': weight,
                            'pt_ppm': pt_ppm,
                            'pd_ppm': pd_ppm,
                            'rh_ppm': rh_ppm,
                            'renumeration_pt': renumeration_pt,
                            'renumeration_pd': renumeration_pd,
                            'renumeration_rh': renumeration_rh,
                            'calculated_ptG': ptG,
                            'calculated_pdG': pdG,
                            'calculated_rhG': rhG
                        })
                
                is_zero_result = total_ptG == 0 and total_pdG == 0 and total_rhG == 0
                success = True  # API call succeeded
                
                details = f"API Response: {len(baskets)} baskets returned"
                details += f"\nCalculated totals: Pt={total_ptG:.4f}, Pd={total_pdG:.4f}, Rh={total_rhG:.4f}"
                details += f"\nResult is (0,0,0): {is_zero_result}"
                
                if calculation_details:
                    details += f"\n\nCalculation breakdown:"
                    for calc in calculation_details[:3]:  # Show first 3 calculations
                        details += f"\n  - {calc['item']}: weight={calc['weight']} * pt_ppm={calc['pt_ppm']} / 1000 * renumeration_pt={calc['renumeration_pt']} = {calc['calculated_ptG']:.4f}"
                
                if is_zero_result:
                    details += f"\n\n❌ CONFIRMED: Basket calculations are showing (0,0,0) as reported"
                
                self.log_test(
                    "3. Basket API Endpoint Test",
                    success,
                    details
                )
                
                return {
                    'total_ptG': total_ptG,
                    'total_pdG': total_pdG,
                    'total_rhG': total_rhG,
                    'is_zero_result': is_zero_result,
                    'calculation_details': calculation_details
                }
            else:
                self.log_test("3. Basket API Endpoint Test", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("3. Basket API Endpoint Test", False, error_msg=str(e))
            return None

    def test_catalyst_calculation_backend(self, user_id):
        """Verify if the catalyst calculation is working correctly in the backend"""
        try:
            # Get baskets data
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code != 200:
                self.log_test("4. Catalyst Calculation Backend Verification", False, f"Failed to get baskets: HTTP {response.status_code}")
                return False
            
            baskets = response.json()
            
            issues_identified = []
            items_analyzed = 0
            
            for basket in baskets:
                items = basket.get('items', [])
                for item in items:
                    items_analyzed += 1
                    
                    # Check each required field
                    weight = item.get('weight')
                    pt_ppm = item.get('pt_ppm')
                    pd_ppm = item.get('pd_ppm')
                    rh_ppm = item.get('rh_ppm')
                    renumeration_pt = item.get('renumeration_pt')
                    renumeration_pd = item.get('renumeration_pd')
                    renumeration_rh = item.get('renumeration_rh')
                    
                    item_name = item.get('title', 'Unknown Item')
                    
                    # Identify specific issues
                    if weight is None or weight == 0:
                        issues_identified.append(f"Item '{item_name}': weight is missing or 0 (weight={weight})")
                    
                    if pt_ppm is None or pt_ppm == 0:
                        issues_identified.append(f"Item '{item_name}': pt_ppm is missing or 0 (pt_ppm={pt_ppm})")
                    
                    if pd_ppm is None or pd_ppm == 0:
                        issues_identified.append(f"Item '{item_name}': pd_ppm is missing or 0 (pd_ppm={pd_ppm})")
                    
                    if rh_ppm is None or rh_ppm == 0:
                        issues_identified.append(f"Item '{item_name}': rh_ppm is missing or 0 (rh_ppm={rh_ppm})")
                    
                    if renumeration_pt is None or renumeration_pt == 0:
                        issues_identified.append(f"Item '{item_name}': renumeration_pt is missing or 0 (renumeration_pt={renumeration_pt})")
                    
                    if renumeration_pd is None or renumeration_pd == 0:
                        issues_identified.append(f"Item '{item_name}': renumeration_pd is missing or 0 (renumeration_pd={renumeration_pd})")
                    
                    if renumeration_rh is None or renumeration_rh == 0:
                        issues_identified.append(f"Item '{item_name}': renumeration_rh is missing or 0 (renumeration_rh={renumeration_rh})")
            
            success = items_analyzed > 0
            details = f"Items analyzed: {items_analyzed}, Issues found: {len(issues_identified)}"
            
            if issues_identified:
                details += f"\n\nIssues causing (0,0,0) calculations:"
                for issue in issues_identified[:10]:  # Show first 10 issues
                    details += f"\n  - {issue}"
                
                if len(issues_identified) > 10:
                    details += f"\n  ... and {len(issues_identified) - 10} more issues"
            
            self.log_test(
                "4. Catalyst Calculation Backend Verification",
                success,
                details,
                "No items found to analyze" if not success else ""
            )
            
            return issues_identified
        except Exception as e:
            self.log_test("4. Catalyst Calculation Backend Verification", False, error_msg=str(e))
            return []

    def run_buy_management_debug(self):
        """Run comprehensive Buy Management calculation debugging"""
        print("=" * 80)
        print("CATALORO BUY MANAGEMENT CALCULATION DEBUG")
        print("=" * 80)
        print("Investigating why basket calculations show (0,0,0) for Pt, Pd, and Rh values")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting Buy Management debug.")
            return
        
        # 2. Get Demo User
        print("👤 GET DEMO USER")
        print("-" * 40)
        demo_user = self.get_demo_user()
        if not demo_user:
            print("❌ Failed to get demo user. Aborting tests.")
            return
        
        user_id = demo_user.get('id')
        print(f"✅ Demo user ID: {user_id}")
        print()
        
        # 3. Check Listings with Catalyst Fields
        print("🧪 CHECK LISTINGS WITH CATALYST FIELDS")
        print("-" * 40)
        catalyst_listings = self.test_listings_catalyst_data()
        
        # 4. Check Baskets with Items
        print("🗂️ CHECK BASKETS WITH ITEMS")
        print("-" * 40)
        baskets_with_items = self.test_baskets_with_items(user_id)
        
        # 5. Test Basket API Endpoint
        print("📊 TEST BASKET API ENDPOINT")
        print("-" * 40)
        basket_calculation = self.test_basket_api_endpoint(user_id)
        
        # 6. Verify Catalyst Calculation Backend
        print("🧮 VERIFY CATALYST CALCULATION BACKEND")
        print("-" * 40)
        calculation_issues = self.test_catalyst_calculation_backend(user_id)
        
        # Print Summary
        print("=" * 80)
        print("BUY MANAGEMENT CALCULATION DEBUG SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Root Cause Analysis
        print("🔍 ROOT CAUSE ANALYSIS")
        print("-" * 40)
        
        root_causes = []
        
        if not catalyst_listings:
            root_causes.append("❌ ISSUE 1: No listings found with non-zero catalyst values")
            root_causes.append("   → The listings don't have catalyst data stored properly")
        else:
            print(f"✅ Found {len(catalyst_listings)} listings with catalyst data")
        
        if not baskets_with_items:
            root_causes.append("❌ ISSUE 2: No baskets found with items assigned")
            root_causes.append("   → No items in baskets to calculate")
        else:
            print(f"✅ Found baskets with items")
        
        if basket_calculation and basket_calculation.get('is_zero_result'):
            root_causes.append("❌ ISSUE 3: Basket calculations are indeed showing (0,0,0)")
            root_causes.append("   → Confirmed the reported problem")
        
        if calculation_issues:
            root_causes.append(f"❌ ISSUE 4: Found {len(calculation_issues)} calculation issues")
            root_causes.append("   → Items in baskets missing required catalyst or renumeration data")
        
        if root_causes:
            print("\nROOT CAUSES IDENTIFIED:")
            for cause in root_causes:
                print(cause)
        else:
            print("✅ No major issues identified")
        
        print()
        print("🎯 BUY MANAGEMENT CALCULATION DEBUG COMPLETE")
        print()
        print("SUSPECTED CAUSES (as mentioned in review request):")
        print("1. ❓ The listings don't have catalyst data stored")
        print("2. ❓ The basket items don't have the catalyst fields populated correctly") 
        print("3. ❓ The calculation is failing somewhere")
        print()
        print("FRONTEND CALCULATION LOGIC:")
        print("- ptG = weight * pt_ppm / 1000 * renumeration_pt")
        print("- pdG = weight * pd_ppm / 1000 * renumeration_pd")
        print("- rhG = weight * rh_ppm / 1000 * renumeration_rh")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    debugger = BuyManagementDebugger()
    
    print("🎯 RUNNING BUY MANAGEMENT CALCULATION DEBUG")
    print("Investigating why basket calculations show (0,0,0) for Pt, Pd, and Rh values...")
    print()
    
    passed, failed, results = debugger.run_buy_management_debug()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)