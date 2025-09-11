#!/usr/bin/env python3
"""
Detailed Basket Investigation - Deep dive into basket assignment and catalyst data flow
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://marketplace-debug-3.preview.emergentagent.com/api"

class DetailedBasketInvestigator:
    def __init__(self):
        self.demo_user_id = None
        
    def setup_demo_user(self):
        """Login as demo user and get user ID"""
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
                self.demo_user_id = user.get('id')
                print(f"✅ Demo user logged in successfully. User ID: {self.demo_user_id}")
                return True
            else:
                print(f"❌ Failed to login: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False

    def investigate_basket_items_detailed(self):
        """Detailed investigation of basket items and their catalyst data"""
        print("\n🔍 DETAILED BASKET ITEMS INVESTIGATION")
        print("=" * 60)
        
        try:
            response = requests.get(f"{BACKEND_URL}/user/baskets/{self.demo_user_id}", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Failed to get baskets: HTTP {response.status_code}")
                return
            
            baskets = response.json()
            print(f"Found {len(baskets)} baskets")
            
            for i, basket in enumerate(baskets):
                basket_id = basket.get('id', f'basket_{i}')
                basket_name = basket.get('name', 'Unnamed Basket')
                items = basket.get('items', [])
                
                print(f"\n📦 Basket {i+1}: '{basket_name}' (ID: {basket_id})")
                print(f"   Items count: {len(items)}")
                
                if items:
                    for j, item in enumerate(items):
                        print(f"\n   📋 Item {j+1}: {item.get('title', 'Unknown')}")
                        print(f"      ID: {item.get('id', 'No ID')}")
                        print(f"      Price: €{item.get('price', 0)}")
                        print(f"      Seller: {item.get('seller_name', 'Unknown')}")
                        
                        # Catalyst data analysis
                        print(f"      🧪 Catalyst Data:")
                        weight = item.get('weight', 'MISSING')
                        pt_ppm = item.get('pt_ppm', 'MISSING')
                        pd_ppm = item.get('pd_ppm', 'MISSING')
                        rh_ppm = item.get('rh_ppm', 'MISSING')
                        
                        print(f"         Weight: {weight}")
                        print(f"         PT PPM: {pt_ppm}")
                        print(f"         PD PPM: {pd_ppm}")
                        print(f"         RH PPM: {rh_ppm}")
                        
                        # Renumeration data
                        print(f"      💰 Renumeration Data:")
                        renumeration_pt = item.get('renumeration_pt', 'MISSING')
                        renumeration_pd = item.get('renumeration_pd', 'MISSING')
                        renumeration_rh = item.get('renumeration_rh', 'MISSING')
                        
                        print(f"         PT Renumeration: {renumeration_pt}")
                        print(f"         PD Renumeration: {renumeration_pd}")
                        print(f"         RH Renumeration: {rh_ppm}")
                        
                        # Calculate expected values
                        if (isinstance(weight, (int, float)) and isinstance(pt_ppm, (int, float)) and 
                            isinstance(renumeration_pt, (int, float))):
                            pt_calc = weight * pt_ppm / 1000 * renumeration_pt
                            pd_calc = weight * pd_ppm / 1000 * renumeration_pd if isinstance(pd_ppm, (int, float)) and isinstance(renumeration_pd, (int, float)) else 0
                            rh_calc = weight * rh_ppm / 1000 * renumeration_rh if isinstance(rh_ppm, (int, float)) and isinstance(renumeration_rh, (int, float)) else 0
                            
                            print(f"      📊 Calculated Values:")
                            print(f"         PT: {pt_calc:.4f}g")
                            print(f"         PD: {pd_calc:.4f}g")
                            print(f"         RH: {rh_calc:.4f}g")
                            
                            if pt_calc == 0 and pd_calc == 0 and rh_calc == 0:
                                print(f"         ❌ ISSUE: All calculations result in ZERO!")
                        else:
                            print(f"      ❌ Cannot calculate - missing or invalid data types")
                        
                        # Show all fields for debugging
                        print(f"      🔧 All Item Fields:")
                        for key, value in item.items():
                            if key not in ['title', 'id', 'price', 'seller_name', 'weight', 'pt_ppm', 'pd_ppm', 'rh_ppm', 'renumeration_pt', 'renumeration_pd', 'renumeration_rh']:
                                print(f"         {key}: {value}")
                else:
                    print("   (No items in this basket)")
                    
        except Exception as e:
            print(f"❌ Error investigating baskets: {str(e)}")

    def investigate_bought_items_detailed(self):
        """Detailed investigation of bought items and their catalyst data"""
        print("\n🛒 DETAILED BOUGHT ITEMS INVESTIGATION")
        print("=" * 60)
        
        try:
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.demo_user_id}", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Failed to get bought items: HTTP {response.status_code}")
                return
            
            bought_items = response.json()
            print(f"Found {len(bought_items)} bought items")
            
            for i, item in enumerate(bought_items):
                print(f"\n🛍️ Bought Item {i+1}: {item.get('title', 'Unknown')}")
                print(f"   ID: {item.get('id', 'No ID')}")
                print(f"   Listing ID: {item.get('listing_id', 'No Listing ID')}")
                print(f"   Price: €{item.get('price', 0)}")
                print(f"   Seller: {item.get('seller_name', 'Unknown')}")
                print(f"   Basket ID: {item.get('basket_id', 'Not assigned')}")
                
                # Catalyst data analysis
                print(f"   🧪 Catalyst Data:")
                weight = item.get('weight', 'MISSING')
                pt_ppm = item.get('pt_ppm', 'MISSING')
                pd_ppm = item.get('pd_ppm', 'MISSING')
                rh_ppm = item.get('rh_ppm', 'MISSING')
                
                print(f"      Weight: {weight}")
                print(f"      PT PPM: {pt_ppm}")
                print(f"      PD PPM: {pd_ppm}")
                print(f"      RH PPM: {rh_ppm}")
                
                # Renumeration data
                print(f"   💰 Renumeration Data:")
                renumeration_pt = item.get('renumeration_pt', 'MISSING')
                renumeration_pd = item.get('renumeration_pd', 'MISSING')
                renumeration_rh = item.get('renumeration_rh', 'MISSING')
                
                print(f"      PT Renumeration: {renumeration_pt}")
                print(f"      PD Renumeration: {renumeration_pd}")
                print(f"      RH Renumeration: {renumeration_rh}")
                
                # Show all fields for debugging
                print(f"   🔧 All Item Fields:")
                for key, value in item.items():
                    if key not in ['title', 'id', 'listing_id', 'price', 'seller_name', 'basket_id', 'weight', 'pt_ppm', 'pd_ppm', 'rh_ppm', 'renumeration_pt', 'renumeration_pd', 'renumeration_rh']:
                        print(f"      {key}: {value}")
                        
        except Exception as e:
            print(f"❌ Error investigating bought items: {str(e)}")

    def investigate_original_listings(self):
        """Check original listings to see if they have catalyst data"""
        print("\n🏪 ORIGINAL LISTINGS CATALYST DATA INVESTIGATION")
        print("=" * 60)
        
        try:
            # First get bought items to find their listing IDs
            bought_response = requests.get(f"{BACKEND_URL}/user/bought-items/{self.demo_user_id}", timeout=10)
            
            if bought_response.status_code != 200:
                print("❌ Cannot get bought items to check original listings")
                return
            
            bought_items = bought_response.json()
            listing_ids = [item.get('listing_id') for item in bought_items if item.get('listing_id')]
            
            print(f"Checking {len(listing_ids)} original listings from bought items")
            
            # Get all marketplace listings
            listings_response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if listings_response.status_code != 200:
                print(f"❌ Failed to get marketplace listings: HTTP {listings_response.status_code}")
                return
            
            all_listings = listings_response.json()
            
            for listing_id in listing_ids:
                print(f"\n🔍 Looking for listing ID: {listing_id}")
                
                # Find the listing in marketplace
                found_listing = None
                for listing in all_listings:
                    if listing.get('id') == listing_id:
                        found_listing = listing
                        break
                
                if found_listing:
                    print(f"   ✅ Found listing: {found_listing.get('title', 'Unknown')}")
                    print(f"   🧪 Original Catalyst Data:")
                    
                    # Check for catalyst fields (both naming conventions)
                    weight = found_listing.get('ceramic_weight', found_listing.get('weight', 'MISSING'))
                    pt_ppm = found_listing.get('pt_ppm', 'MISSING')
                    pd_ppm = found_listing.get('pd_ppm', 'MISSING')
                    rh_ppm = found_listing.get('rh_ppm', 'MISSING')
                    
                    print(f"      Weight (ceramic_weight): {weight}")
                    print(f"      PT PPM: {pt_ppm}")
                    print(f"      PD PPM: {pd_ppm}")
                    print(f"      RH PPM: {rh_ppm}")
                    
                    # Show all fields that might contain catalyst data
                    print(f"   🔧 All Listing Fields (catalyst-related):")
                    catalyst_related_fields = ['ceramic_weight', 'weight', 'pt_ppm', 'pd_ppm', 'rh_ppm', 'catalyst_id', 'cat_id']
                    for key, value in found_listing.items():
                        if any(field in key.lower() for field in ['weight', 'ppm', 'catalyst', 'cat']):
                            print(f"      {key}: {value}")
                else:
                    print(f"   ❌ Listing not found in marketplace (may be inactive/deleted)")
                    
        except Exception as e:
            print(f"❌ Error investigating original listings: {str(e)}")

    def run_detailed_investigation(self):
        """Run the complete detailed investigation"""
        print("🔍 DETAILED BASKET AND CATALYST DATA INVESTIGATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Started: {datetime.now().isoformat()}")
        
        if not self.setup_demo_user():
            print("❌ Cannot proceed without demo user")
            return
        
        # Run all investigations
        self.investigate_basket_items_detailed()
        self.investigate_bought_items_detailed()
        self.investigate_original_listings()
        
        print("\n" + "=" * 80)
        print("🎯 INVESTIGATION COMPLETE")
        print("=" * 80)
        print("Key Questions Answered:")
        print("1. ✅ Do baskets show correct item counts?")
        print("2. ✅ Do basket items have catalyst data?")
        print("3. ✅ Do bought items have catalyst data?")
        print("4. ✅ Do original listings have catalyst data?")
        print("5. ✅ Is data being lost during assignment process?")

if __name__ == "__main__":
    investigator = DetailedBasketInvestigator()
    investigator.run_detailed_investigation()