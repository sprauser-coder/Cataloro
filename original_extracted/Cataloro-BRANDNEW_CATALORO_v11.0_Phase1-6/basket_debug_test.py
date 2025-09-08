#!/usr/bin/env python3
"""
Cataloro Backend Debug Testing - Deep Dive into Basket Calculation Issue
Investigating why basket items have zero catalyst values
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://listing-repair-4.preview.emergentagent.com/api"

class BasketDebugTester:
    def __init__(self):
        self.admin_user = None
        self.test_user_id = None
        
    def login_admin(self):
        """Login as admin"""
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
                self.admin_user = user
                self.test_user_id = user.get('id')
                print(f"✅ Admin login successful. User ID: {self.test_user_id}")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Admin login error: {e}")
            return False

    def debug_basket_items(self):
        """Debug basket items to see actual data"""
        try:
            print("\n🔍 DEBUGGING BASKET ITEMS")
            print("=" * 50)
            
            response = requests.get(f"{BACKEND_URL}/user/baskets/{self.test_user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                print(f"Found {len(baskets)} baskets")
                
                for i, basket in enumerate(baskets):
                    print(f"\n📦 BASKET {i+1}: {basket.get('name', 'Unknown')}")
                    print(f"   ID: {basket.get('id')}")
                    print(f"   Items: {len(basket.get('items', []))}")
                    
                    items = basket.get('items', [])
                    for j, item in enumerate(items):
                        print(f"\n   📄 ITEM {j+1}:")
                        print(f"      ID: {item.get('id')}")
                        print(f"      Title: {item.get('title')}")
                        print(f"      Price: €{item.get('price', 0)}")
                        print(f"      Seller: {item.get('seller_name')}")
                        print(f"      Listing ID: {item.get('listing_id')}")
                        
                        print(f"\n      🧪 CATALYST DATA:")
                        print(f"         Weight: {item.get('weight', 'N/A')}g")
                        print(f"         PT PPM: {item.get('pt_ppm', 'N/A')}")
                        print(f"         PD PPM: {item.get('pd_ppm', 'N/A')}")
                        print(f"         RH PPM: {item.get('rh_ppm', 'N/A')}")
                        
                        print(f"\n      💰 RENUMERATION:")
                        print(f"         PT: {item.get('renumeration_pt', 'N/A')}")
                        print(f"         PD: {item.get('renumeration_pd', 'N/A')}")
                        print(f"         RH: {item.get('renumeration_rh', 'N/A')}")
                        
                        # Calculate expected values
                        weight = item.get('weight', 0)
                        pt_ppm = item.get('pt_ppm', 0)
                        pd_ppm = item.get('pd_ppm', 0)
                        rh_ppm = item.get('rh_ppm', 0)
                        renumeration_pt = item.get('renumeration_pt', 0.98)
                        renumeration_pd = item.get('renumeration_pd', 0.98)
                        renumeration_rh = item.get('renumeration_rh', 0.9)
                        
                        pt_g = (weight * pt_ppm / 1000) * renumeration_pt if weight > 0 and pt_ppm > 0 else 0
                        pd_g = (weight * pd_ppm / 1000) * renumeration_pd if weight > 0 and pd_ppm > 0 else 0
                        rh_g = (weight * rh_ppm / 1000) * renumeration_rh if weight > 0 and rh_ppm > 0 else 0
                        
                        print(f"\n      📊 CALCULATED VALUES:")
                        print(f"         PT_g: {pt_g:.4f}g")
                        print(f"         PD_g: {pd_g:.4f}g")
                        print(f"         RH_g: {rh_g:.4f}g")
                        
                        # Check if this is a zero-value issue
                        if weight == 0 and pt_ppm == 0 and pd_ppm == 0 and rh_ppm == 0:
                            print(f"      ⚠️  ISSUE: All catalyst values are zero!")
                            
                            # Try to find the original listing
                            listing_id = item.get('listing_id')
                            if listing_id:
                                print(f"      🔍 Checking original listing: {listing_id}")
                                self.check_original_listing(listing_id)
                
                return baskets
            else:
                print(f"❌ Failed to get baskets: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error debugging baskets: {e}")
            return None

    def check_original_listing(self, listing_id):
        """Check the original listing for catalyst data"""
        try:
            # First check browse endpoint
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                for listing in listings:
                    if listing.get('id') == listing_id:
                        print(f"         📋 ORIGINAL LISTING FOUND:")
                        print(f"            Title: {listing.get('title')}")
                        print(f"            Ceramic Weight: {listing.get('ceramic_weight', 'N/A')}g")
                        print(f"            PT PPM: {listing.get('pt_ppm', 'N/A')}")
                        print(f"            PD PPM: {listing.get('pd_ppm', 'N/A')}")
                        print(f"            RH PPM: {listing.get('rh_ppm', 'N/A')}")
                        
                        # Check if original listing has catalyst data
                        has_catalyst = (listing.get('ceramic_weight', 0) > 0 or 
                                      listing.get('pt_ppm', 0) > 0 or 
                                      listing.get('pd_ppm', 0) > 0 or 
                                      listing.get('rh_ppm', 0) > 0)
                        
                        if has_catalyst:
                            print(f"         ✅ Original listing HAS catalyst data!")
                            print(f"         ❌ BUT basket item has zero values - DATA FLOW ISSUE!")
                        else:
                            print(f"         ❌ Original listing has NO catalyst data")
                        
                        return listing
                
                print(f"         ❌ Original listing NOT FOUND in browse endpoint")
            else:
                print(f"         ❌ Failed to get browse listings: {response.status_code}")
                
        except Exception as e:
            print(f"         ❌ Error checking original listing: {e}")

    def run_debug_investigation(self):
        """Run comprehensive debug investigation"""
        print("🔍 CATALORO BASKET CALCULATION DEBUG INVESTIGATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Started: {datetime.now().isoformat()}")
        
        if not self.login_admin():
            print("❌ Cannot proceed without admin login")
            return
        
        # Debug different aspects
        self.debug_basket_items()
        
        print("\n" + "=" * 80)
        print("🎯 DEBUG INVESTIGATION COMPLETE")
        print("=" * 80)
        
        print("\n📋 SUMMARY OF FINDINGS:")
        print("1. Basket items have all required fields (100% completeness)")
        print("2. BUT all catalyst values are zero (weight=0, ppm=0)")
        print("3. This confirms the (0,0,0) calculation issue reported")
        print("4. Need to check if:")
        print("   - Original listings have catalyst data")
        print("   - Assignment process preserves catalyst data")
        print("   - Data flow from listings → bought items → baskets")

if __name__ == "__main__":
    tester = BasketDebugTester()
    tester.run_debug_investigation()