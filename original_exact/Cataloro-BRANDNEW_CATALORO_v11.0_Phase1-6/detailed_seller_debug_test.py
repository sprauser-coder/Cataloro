#!/usr/bin/env python3
"""
Detailed Seller Debug Test - Deep dive into the seller lookup issue
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://listing-repair-4.preview.emergentagent.com/api"

class DetailedSellerDebugTester:
    def __init__(self):
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

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
                return data.get('user', {})
            return None
        except Exception as e:
            print(f"Error getting demo user: {e}")
            return None

    def deep_dive_seller_lookup_issue(self):
        """Deep dive into the seller lookup issue"""
        print("🔍 DEEP DIVE: SELLER LOOKUP ISSUE ANALYSIS")
        print("=" * 60)
        
        # Get demo user
        demo_user = self.get_demo_user()
        if not demo_user:
            print("❌ Could not get demo user")
            return
        
        user_id = demo_user.get('id')
        print(f"Demo User ID: {user_id}")
        print()
        
        # Get bought items
        try:
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            if response.status_code != 200:
                print(f"❌ Could not get bought items: HTTP {response.status_code}")
                return
            
            bought_items = response.json()
            print(f"Found {len(bought_items)} bought items")
            print()
            
            # Analyze each bought item in detail
            for i, item in enumerate(bought_items[:2]):  # Check first 2 items
                print(f"🔍 ANALYZING ITEM {i+1}")
                print("-" * 40)
                
                listing_id = item.get('listing_id')
                seller_id_from_item = item.get('seller_id')
                seller_name_from_item = item.get('seller_name')
                
                print(f"Item Data:")
                print(f"  - Title: {item.get('title')}")
                print(f"  - Listing ID: {listing_id}")
                print(f"  - Seller ID (from item): {seller_id_from_item}")
                print(f"  - Seller Name (from item): {seller_name_from_item}")
                print()
                
                # Step 1: Check the listing data
                print("Step 1: Checking listing data...")
                try:
                    # We need to check the listings collection directly
                    # Since there's no direct endpoint, let's check via browse
                    browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
                    if browse_response.status_code == 200:
                        all_listings = browse_response.json()
                        
                        # Find our specific listing
                        target_listing = None
                        for listing in all_listings:
                            if listing.get('id') == listing_id:
                                target_listing = listing
                                break
                        
                        if target_listing:
                            listing_seller_id = target_listing.get('seller_id')
                            listing_seller_info = target_listing.get('seller', {})
                            
                            print(f"  ✅ Found listing in browse results")
                            print(f"  - Listing seller_id: {listing_seller_id}")
                            print(f"  - Listing seller info: {listing_seller_info}")
                            print()
                            
                            # Step 2: Check if seller_id matches
                            print("Step 2: Checking seller_id consistency...")
                            if listing_seller_id == seller_id_from_item:
                                print(f"  ✅ Seller IDs match: {listing_seller_id}")
                            else:
                                print(f"  ❌ Seller ID mismatch!")
                                print(f"    - From listing: {listing_seller_id}")
                                print(f"    - From bought item: {seller_id_from_item}")
                            print()
                            
                            # Step 3: Check seller user record
                            print("Step 3: Checking seller user record...")
                            try:
                                seller_response = requests.get(f"{BACKEND_URL}/auth/profile/{listing_seller_id}", timeout=10)
                                if seller_response.status_code == 200:
                                    seller_data = seller_response.json()
                                    print(f"  ✅ Seller user found:")
                                    print(f"    - ID: {seller_data.get('id')}")
                                    print(f"    - Username: {seller_data.get('username')}")
                                    print(f"    - Email: {seller_data.get('email')}")
                                    print(f"    - Full Name: {seller_data.get('full_name')}")
                                    
                                    # Step 4: Compare with what should be returned
                                    expected_seller_name = seller_data.get('username', 'Unknown')
                                    print()
                                    print("Step 4: Expected vs Actual comparison...")
                                    print(f"  - Expected seller_name: '{expected_seller_name}'")
                                    print(f"  - Actual seller_name: '{seller_name_from_item}'")
                                    
                                    if expected_seller_name == seller_name_from_item:
                                        print(f"  ✅ Seller names match!")
                                    else:
                                        print(f"  ❌ SELLER NAME MISMATCH - THIS IS THE BUG!")
                                        print(f"    The backend should return '{expected_seller_name}' but returns '{seller_name_from_item}'")
                                else:
                                    print(f"  ❌ Seller user not found: HTTP {seller_response.status_code}")
                            except Exception as e:
                                print(f"  ❌ Error checking seller: {e}")
                        else:
                            print(f"  ❌ Listing {listing_id} not found in browse results")
                    else:
                        print(f"  ❌ Could not get browse results: HTTP {browse_response.status_code}")
                except Exception as e:
                    print(f"  ❌ Error checking listing: {e}")
                
                print()
                print("=" * 60)
                print()
                
        except Exception as e:
            print(f"❌ Error in deep dive analysis: {e}")

    def test_backend_seller_lookup_logic(self):
        """Test the backend seller lookup logic step by step"""
        print("🧪 TESTING BACKEND SELLER LOOKUP LOGIC")
        print("=" * 60)
        
        # Simulate the backend logic
        demo_user = self.get_demo_user()
        if not demo_user:
            return
        
        user_id = demo_user.get('id')
        
        print("Simulating backend logic for bought items...")
        print()
        
        # Step 1: Get accepted tenders (simulating backend logic)
        print("Step 1: Checking for accepted tenders...")
        # We can't directly access tenders, but we can infer from bought items
        
        # Step 2: For each tender, get listing and seller
        print("Step 2: For each bought item, trace the seller lookup...")
        
        try:
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            if response.status_code == 200:
                bought_items = response.json()
                
                for i, item in enumerate(bought_items[:1]):  # Check first item
                    print(f"\nTracing item {i+1}: {item.get('title')}")
                    listing_id = item.get('listing_id')
                    seller_id = item.get('seller_id')
                    
                    # Check if we can find this listing in browse
                    browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
                    if browse_response.status_code == 200:
                        listings = browse_response.json()
                        listing = None
                        for l in listings:
                            if l.get('id') == listing_id:
                                listing = l
                                break
                        
                        if listing:
                            print(f"  ✅ Found listing: {listing.get('title')}")
                            print(f"  - Listing seller_id: {listing.get('seller_id')}")
                            
                            # Now check the seller
                            listing_seller_id = listing.get('seller_id')
                            if listing_seller_id:
                                seller_response = requests.get(f"{BACKEND_URL}/auth/profile/{listing_seller_id}", timeout=10)
                                if seller_response.status_code == 200:
                                    seller = seller_response.json()
                                    expected_name = seller.get("username", "Unknown") if seller else "Unknown"
                                    actual_name = item.get('seller_name')
                                    
                                    print(f"  ✅ Found seller: {seller.get('username')} ({seller.get('email')})")
                                    print(f"  - Backend should set seller_name = seller.get('username', 'Unknown')")
                                    print(f"  - Expected: '{expected_name}'")
                                    print(f"  - Actual: '{actual_name}'")
                                    
                                    if expected_name != actual_name:
                                        print(f"  ❌ BUG CONFIRMED: Backend is not properly setting seller_name")
                                        print(f"      The seller exists and has username '{expected_name}'")
                                        print(f"      But bought item shows '{actual_name}'")
                                        
                                        # Check if it's a timing issue or data consistency issue
                                        print(f"\n  🔍 INVESTIGATING FURTHER:")
                                        print(f"    - Seller ID from listing: {listing_seller_id}")
                                        print(f"    - Seller ID from bought item: {seller_id}")
                                        
                                        if listing_seller_id != seller_id:
                                            print(f"    ❌ SELLER ID MISMATCH between listing and bought item!")
                                        else:
                                            print(f"    ✅ Seller IDs match - issue is in the lookup logic")
                                else:
                                    print(f"  ❌ Could not fetch seller profile: HTTP {seller_response.status_code}")
                            else:
                                print(f"  ❌ Listing has no seller_id")
                        else:
                            print(f"  ❌ Could not find listing {listing_id} in browse results")
                    else:
                        print(f"  ❌ Could not get browse results")
        except Exception as e:
            print(f"❌ Error in backend logic test: {e}")

if __name__ == "__main__":
    tester = DetailedSellerDebugTester()
    
    print("🎯 DETAILED SELLER NAME DEBUG ANALYSIS")
    print("Investigating the exact cause of 'Unknown' seller names...")
    print()
    
    tester.deep_dive_seller_lookup_issue()
    tester.test_backend_seller_lookup_logic()
    
    print("\n🎯 ANALYSIS COMPLETE")
    print("This detailed analysis should reveal the exact cause of the seller name issue.")