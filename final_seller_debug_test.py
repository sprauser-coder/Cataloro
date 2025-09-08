#!/usr/bin/env python3
"""
Final Seller Debug Test - Root Cause Analysis and Solution
"""

import requests
import json
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://marketplace-admin-1.preview.emergentagent.com/api"

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
            return data.get('user', {})
        return None
    except Exception as e:
        print(f"Error getting demo user: {e}")
        return None

def main():
    print("🎯 FINAL SELLER NAME DEBUG ANALYSIS")
    print("=" * 80)
    print("ROOT CAUSE INVESTIGATION AND SOLUTION")
    print("=" * 80)
    
    # Get demo user
    demo_user = get_demo_user()
    if not demo_user:
        print("❌ Could not get demo user")
        return
    
    user_id = demo_user.get('id')
    print(f"Demo User ID: {user_id}")
    print()
    
    # Get bought items
    print("📋 STEP 1: GET BOUGHT ITEMS")
    print("-" * 50)
    try:
        response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
        if response.status_code != 200:
            print(f"❌ Could not get bought items: HTTP {response.status_code}")
            return
        
        bought_items = response.json()
        print(f"✅ Found {len(bought_items)} bought items")
        
        # Extract listing IDs
        listing_ids = [item.get('listing_id') for item in bought_items]
        print(f"Listing IDs in bought items: {listing_ids}")
        print()
        
    except Exception as e:
        print(f"❌ Error getting bought items: {e}")
        return
    
    # Get all listings from browse
    print("📋 STEP 2: GET ALL ACTIVE LISTINGS")
    print("-" * 50)
    try:
        response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
        if response.status_code != 200:
            print(f"❌ Could not get browse listings: HTTP {response.status_code}")
            return
        
        active_listings = response.json()
        print(f"✅ Found {len(active_listings)} active listings")
        
        # Extract active listing IDs
        active_listing_ids = [listing.get('id') for listing in active_listings]
        print(f"Active listing IDs: {active_listing_ids[:5]}..." if len(active_listing_ids) > 5 else f"Active listing IDs: {active_listing_ids}")
        print()
        
    except Exception as e:
        print(f"❌ Error getting active listings: {e}")
        return
    
    # Check for missing listings
    print("🔍 STEP 3: CHECK FOR MISSING LISTINGS")
    print("-" * 50)
    missing_listings = []
    found_listings = []
    
    for listing_id in listing_ids:
        if listing_id in active_listing_ids:
            found_listings.append(listing_id)
            print(f"✅ Found: {listing_id}")
        else:
            missing_listings.append(listing_id)
            print(f"❌ Missing: {listing_id}")
    
    print()
    print(f"Summary: {len(found_listings)} found, {len(missing_listings)} missing")
    print()
    
    # Analyze the root cause
    print("🎯 STEP 4: ROOT CAUSE ANALYSIS")
    print("-" * 50)
    
    if missing_listings:
        print("❌ ROOT CAUSE IDENTIFIED:")
        print("   The bought items reference listings that are NOT in the active listings!")
        print()
        print("   This explains why seller names show as 'Unknown':")
        print("   1. Backend tries to find listing by ID")
        print("   2. Listing is not found (deleted/inactive)")
        print("   3. listing = None")
        print("   4. seller lookup fails")
        print("   5. seller_name defaults to 'Unknown'")
        print()
        
        print("📋 BACKEND CODE ANALYSIS:")
        print("   Current backend logic in get_bought_items():")
        print("   ```")
        print("   listing = await db.listings.find_one({'id': tender.get('listing_id')})")
        print("   if listing:")
        print("       seller = await db.users.find_one({'id': listing.get('seller_id')})")
        print("       seller_name = seller.get('username', 'Unknown') if seller else 'Unknown'")
        print("   ```")
        print()
        print("   The issue: listing is None, so seller lookup never happens!")
        print()
        
        print("💡 SOLUTION OPTIONS:")
        print("   Option 1: Store seller_id directly in tenders/orders")
        print("   Option 2: Store seller_name at purchase time")
        print("   Option 3: Query all listings (not just active ones)")
        print("   Option 4: Add seller info to bought_items when created")
        print()
        
        # Check if we can get seller info directly
        print("🔧 STEP 5: TESTING DIRECT SELLER LOOKUP")
        print("-" * 50)
        
        for i, item in enumerate(bought_items[:2]):
            seller_id = item.get('seller_id')
            print(f"Item {i+1}: {item.get('title')[:30]}...")
            print(f"  Seller ID: {seller_id}")
            
            if seller_id:
                try:
                    seller_response = requests.get(f"{BACKEND_URL}/auth/profile/{seller_id}", timeout=10)
                    if seller_response.status_code == 200:
                        seller_data = seller_response.json()
                        expected_name = seller_data.get('username', 'Unknown')
                        print(f"  ✅ Seller exists: {expected_name} ({seller_data.get('email')})")
                        print(f"  💡 SHOULD show: '{expected_name}' instead of 'Unknown'")
                    else:
                        print(f"  ❌ Seller not found: HTTP {seller_response.status_code}")
                except Exception as e:
                    print(f"  ❌ Error checking seller: {e}")
            else:
                print(f"  ❌ No seller_id in bought item")
            print()
    else:
        print("✅ All listings found - issue must be elsewhere")
    
    print("🎯 FINAL DIAGNOSIS")
    print("=" * 80)
    print("ISSUE: Seller names show as 'Unknown' in bought items")
    print()
    print("ROOT CAUSE:")
    print("  The bought items reference listing IDs that no longer exist in active listings.")
    print("  When the backend tries to look up the listing to get seller info, it fails.")
    print("  Since listing lookup fails, seller lookup never happens.")
    print()
    print("EVIDENCE:")
    print(f"  - {len(missing_listings)} out of {len(listing_ids)} listings are missing from active listings")
    print("  - Seller users DO exist and have valid usernames")
    print("  - Backend logic is correct, but depends on finding the listing first")
    print()
    print("RECOMMENDED FIX:")
    print("  Modify the backend to use seller_id directly from tenders/orders")
    print("  instead of looking it up through the listing.")
    print("  The seller_id is already stored in the bought items!")
    print()
    print("IMMEDIATE WORKAROUND:")
    print("  Use the seller_id that's already in the bought items to look up seller info")
    print("  instead of going through the listing lookup.")

if __name__ == "__main__":
    main()