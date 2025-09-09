#!/usr/bin/env python3
"""
Debug script to investigate basket data and catalyst persistence issues
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://cataloro-speedup.preview.emergentagent.com/api"

def get_demo_user():
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
            return None
    except Exception as e:
        return None

def debug_baskets():
    """Debug basket data"""
    print("=" * 60)
    print("DEBUGGING BASKET DATA")
    print("=" * 60)
    
    user = get_demo_user()
    if not user:
        print("❌ Could not get demo user")
        return
    
    user_id = user.get('id')
    print(f"Demo User ID: {user_id}")
    
    # Get baskets
    response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
    
    if response.status_code == 200:
        baskets = response.json()
        print(f"\n📊 Found {len(baskets)} baskets")
        
        for i, basket in enumerate(baskets):
            print(f"\n--- Basket {i+1}: {basket.get('name', 'Unknown')} ---")
            print(f"ID: {basket.get('id')}")
            print(f"Items count: {len(basket.get('items', []))}")
            
            items = basket.get('items', [])
            for j, item in enumerate(items):
                print(f"\n  Item {j+1}:")
                print(f"    Title: {item.get('title', 'Unknown')}")
                print(f"    Weight: {item.get('weight', 'N/A')}")
                print(f"    Ceramic Weight: {item.get('ceramic_weight', 'N/A')}")
                print(f"    PT PPM: {item.get('pt_ppm', 'N/A')}")
                print(f"    PD PPM: {item.get('pd_ppm', 'N/A')}")
                print(f"    RH PPM: {item.get('rh_ppm', 'N/A')}")
                print(f"    Renumeration PT: {item.get('renumeration_pt', 'N/A')}")
                print(f"    Renumeration PD: {item.get('renumeration_pd', 'N/A')}")
                print(f"    Renumeration RH: {item.get('renumeration_rh', 'N/A')}")
                print(f"    Listing ID: {item.get('listing_id', 'N/A')}")
                print(f"    All keys: {list(item.keys())}")
    else:
        print(f"❌ Failed to get baskets: HTTP {response.status_code}")

def debug_bought_items():
    """Debug bought items data"""
    print("\n" + "=" * 60)
    print("DEBUGGING BOUGHT ITEMS DATA")
    print("=" * 60)
    
    user = get_demo_user()
    if not user:
        print("❌ Could not get demo user")
        return
    
    user_id = user.get('id')
    
    # Get bought items
    response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
    
    if response.status_code == 200:
        bought_items = response.json()
        print(f"\n📦 Found {len(bought_items)} bought items")
        
        for i, item in enumerate(bought_items):
            print(f"\n--- Bought Item {i+1}: {item.get('title', 'Unknown')} ---")
            print(f"ID: {item.get('id')}")
            print(f"Listing ID: {item.get('listing_id')}")
            print(f"Seller Name: {item.get('seller_name')}")
            print(f"Weight: {item.get('weight', 'N/A')}")
            print(f"PT PPM: {item.get('pt_ppm', 'N/A')}")
            print(f"PD PPM: {item.get('pd_ppm', 'N/A')}")
            print(f"RH PPM: {item.get('rh_ppm', 'N/A')}")
            print(f"Renumeration PT: {item.get('renumeration_pt', 'N/A')}")
            print(f"Renumeration PD: {item.get('renumeration_pd', 'N/A')}")
            print(f"Renumeration RH: {item.get('renumeration_rh', 'N/A')}")
            print(f"All keys: {list(item.keys())}")
    else:
        print(f"❌ Failed to get bought items: HTTP {response.status_code}")

def debug_listings():
    """Debug listings with catalyst data"""
    print("\n" + "=" * 60)
    print("DEBUGGING LISTINGS WITH CATALYST DATA")
    print("=" * 60)
    
    # Get listings
    response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
    
    if response.status_code == 200:
        listings = response.json()
        print(f"\n📋 Found {len(listings)} total listings")
        
        listings_with_catalyst = []
        for listing in listings:
            weight = listing.get('ceramic_weight', 0)
            pt_ppm = listing.get('pt_ppm', 0)
            pd_ppm = listing.get('pd_ppm', 0)
            rh_ppm = listing.get('rh_ppm', 0)
            
            if any([weight, pt_ppm, pd_ppm, rh_ppm]):
                listings_with_catalyst.append(listing)
        
        print(f"📊 Found {len(listings_with_catalyst)} listings with catalyst data")
        
        for i, listing in enumerate(listings_with_catalyst[:5]):  # Show first 5
            print(f"\n--- Listing {i+1}: {listing.get('title', 'Unknown')} ---")
            print(f"ID: {listing.get('id')}")
            print(f"Ceramic Weight: {listing.get('ceramic_weight', 'N/A')}")
            print(f"PT PPM: {listing.get('pt_ppm', 'N/A')}")
            print(f"PD PPM: {listing.get('pd_ppm', 'N/A')}")
            print(f"RH PPM: {listing.get('rh_ppm', 'N/A')}")
    else:
        print(f"❌ Failed to get listings: HTTP {response.status_code}")

if __name__ == "__main__":
    debug_baskets()
    debug_bought_items()
    debug_listings()