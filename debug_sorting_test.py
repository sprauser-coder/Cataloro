#!/usr/bin/env python3
"""
Debug sorting issues in Phase 3D listings API
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def authenticate():
    """Authenticate as admin"""
    session = requests.Session()
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    return None

def debug_sorting():
    """Debug sorting functionality"""
    session = authenticate()
    if not session:
        print("Authentication failed")
        return
    
    # Test default sorting
    print("=== DEFAULT SORTING (no sort_by parameter) ===")
    response = session.get(f"{BACKEND_URL}/listings")
    if response.status_code == 200:
        listings = response.json()
        print(f"Found {len(listings)} listings")
        
        # Show first 5 listings with key fields
        for i, listing in enumerate(listings[:5]):
            print(f"{i+1}. Title: {listing.get('title', 'N/A')}")
            print(f"   Created: {listing.get('created_at', 'N/A')}")
            print(f"   Price: {listing.get('price', 'N/A')}")
            print(f"   Current Bid: {listing.get('current_bid', 'N/A')}")
            print(f"   Views: {listing.get('views', 'N/A')}")
            print()
    
    # Test created_desc sorting explicitly
    print("=== EXPLICIT created_desc SORTING ===")
    response = session.get(f"{BACKEND_URL}/listings", params={"sort_by": "created_desc"})
    if response.status_code == 200:
        listings = response.json()
        print(f"Found {len(listings)} listings")
        
        # Show first 5 listings with creation dates
        for i, listing in enumerate(listings[:5]):
            print(f"{i+1}. Title: {listing.get('title', 'N/A')}")
            print(f"   Created: {listing.get('created_at', 'N/A')}")
            print()
    
    # Test price_high sorting
    print("=== PRICE HIGH TO LOW SORTING ===")
    response = session.get(f"{BACKEND_URL}/listings", params={"sort_by": "price_high"})
    if response.status_code == 200:
        listings = response.json()
        print(f"Found {len(listings)} listings")
        
        # Show first 5 listings with prices
        for i, listing in enumerate(listings[:5]):
            price = listing.get('price') or listing.get('current_bid', 0)
            print(f"{i+1}. Title: {listing.get('title', 'N/A')}")
            print(f"   Price: {listing.get('price', 'N/A')}")
            print(f"   Current Bid: {listing.get('current_bid', 'N/A')}")
            print(f"   Effective Price: {price}")
            print(f"   Listing Type: {listing.get('listing_type', 'N/A')}")
            print()

if __name__ == "__main__":
    debug_sorting()