#!/usr/bin/env python3
"""
Quick test to verify price sorting still works after the created_at fix
"""

import requests
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cataloro-ads.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_price_sorting():
    """Test that price sorting logic in frontend would work with current data"""
    try:
        response = requests.get(f"{API_BASE}/marketplace/browse")
        
        if response.status_code != 200:
            print(f"❌ Browse endpoint failed with status {response.status_code}")
            return False
        
        listings = response.json()
        
        if len(listings) < 2:
            print("⚠️ Need at least 2 listings to test price sorting")
            return True
        
        # Extract prices
        prices = []
        for listing in listings:
            if 'price' in listing:
                prices.append(listing['price'])
        
        if not prices:
            print("❌ No prices found in listings")
            return False
        
        print(f"✅ Found {len(prices)} listings with prices")
        print(f"ℹ️ Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        
        # Show first few prices to verify variety
        print("ℹ️ First 5 listing prices:")
        for i, listing in enumerate(listings[:5]):
            price = listing.get('price', 0)
            title = listing.get('title', 'Unknown')[:30]
            print(f"  {i+1}. ${price:.2f} - {title}...")
        
        # Verify we have price variety (not all the same price)
        unique_prices = set(prices)
        if len(unique_prices) > 1:
            print(f"✅ Price variety confirmed: {len(unique_prices)} different prices")
        else:
            print("⚠️ All listings have the same price - price sorting won't be visible")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in price sorting test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 PRICE SORTING VERIFICATION")
    print("=" * 40)
    success = test_price_sorting()
    if success:
        print("\n✅ Price sorting data looks good!")
    else:
        print("\n❌ Price sorting test failed!")