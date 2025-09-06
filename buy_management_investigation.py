#!/usr/bin/env python3
"""
Buy Management Data Synchronization Investigation
Detailed investigation of the frontend-backend data mismatch for Buy Management
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class BuyManagementInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.demo_user_id = None
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def get_demo_user_id(self):
        """Get demo user ID"""
        try:
            login_data = {
                "email": "demo@cataloro.com",
                "username": "demo_user"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                user_data = response.json()
                self.demo_user_id = user_data.get('user', {}).get('id')
                self.log(f"✅ Demo user ID: {self.demo_user_id}")
                return self.demo_user_id
            else:
                self.log(f"❌ Failed to get demo user: {response.status_code}")
                return None
        except Exception as e:
            self.log(f"❌ Error getting demo user: {e}")
            return None

    def check_database_collections(self):
        """Check what data exists in database collections"""
        self.log("🔍 Investigating database collections...")
        
        # Check tenders collection
        try:
            # We can't directly access MongoDB, but we can check related endpoints
            
            # Check if there are any deals for the demo user
            deals_response = self.session.get(f"{BASE_URL}/user/my-deals/{self.demo_user_id}")
            if deals_response.status_code == 200:
                deals = deals_response.json()
                self.log(f"📊 Demo user has {len(deals)} deals")
                for i, deal in enumerate(deals[:3]):  # Show first 3
                    self.log(f"   Deal {i+1}: {deal.get('listing', {}).get('title', 'Unknown')} - €{deal.get('amount', 0)} - Status: {deal.get('status')}")
            
            # Check if there are any listings by the demo user
            listings_response = self.session.get(f"{BASE_URL}/user/my-listings/{self.demo_user_id}")
            if listings_response.status_code == 200:
                listings = listings_response.json()
                self.log(f"📊 Demo user has {len(listings)} active listings")
            
            # Check marketplace browse to see overall activity
            browse_response = self.session.get(f"{BASE_URL}/marketplace/browse")
            if browse_response.status_code == 200:
                all_listings = browse_response.json()
                self.log(f"📊 Total marketplace has {len(all_listings)} active listings")
                
                # Count listings with bids
                listings_with_bids = 0
                total_bids = 0
                for listing in all_listings:
                    bid_info = listing.get('bid_info', {})
                    if bid_info.get('has_bids', False):
                        listings_with_bids += 1
                        total_bids += bid_info.get('total_bids', 0)
                
                self.log(f"📊 {listings_with_bids} listings have bids, {total_bids} total bids in system")
                
        except Exception as e:
            self.log(f"❌ Error checking database collections: {e}")

    def create_test_tender_data(self):
        """Create test tender data to simulate bought items"""
        self.log("🧪 Creating test tender data...")
        
        try:
            # First, let's see if we can find any active listings to bid on
            browse_response = self.session.get(f"{BASE_URL}/marketplace/browse")
            if browse_response.status_code == 200:
                listings = browse_response.json()
                if listings:
                    # Take the first listing
                    test_listing = listings[0]
                    listing_id = test_listing.get('id')
                    listing_title = test_listing.get('title', 'Unknown')
                    listing_price = test_listing.get('price', 0)
                    
                    self.log(f"📝 Found test listing: {listing_title} (ID: {listing_id}) - €{listing_price}")
                    
                    # Try to create a tender for this listing
                    tender_data = {
                        "listing_id": listing_id,
                        "buyer_id": self.demo_user_id,
                        "offer_amount": listing_price + 10,  # Bid slightly higher
                        "message": "Test tender for Buy Management testing",
                        "status": "pending"
                    }
                    
                    # Note: We need to check if there's a tender creation endpoint
                    # Let's try a few possible endpoints
                    
                    # Try creating a tender (this might not exist)
                    tender_endpoints = [
                        f"{BASE_URL}/tenders",
                        f"{BASE_URL}/listings/{listing_id}/tenders",
                        f"{BASE_URL}/marketplace/tender"
                    ]
                    
                    tender_created = False
                    for endpoint in tender_endpoints:
                        try:
                            response = self.session.post(endpoint, json=tender_data)
                            if response.status_code in [200, 201]:
                                self.log(f"✅ Created test tender via {endpoint}")
                                tender_created = True
                                break
                            else:
                                self.log(f"⚠️ Tender creation failed at {endpoint}: {response.status_code}")
                        except:
                            continue
                    
                    if not tender_created:
                        self.log("❌ Could not create test tender - endpoints may not exist")
                        
                        # Let's try to manually insert data by checking if there are admin endpoints
                        # This is a workaround for testing
                        self.log("🔧 Attempting workaround to create test data...")
                        
                        # Try to create a completed order instead
                        order_data = {
                            "buyer_id": self.demo_user_id,
                            "seller_id": test_listing.get('seller_id', 'unknown'),
                            "listing_id": listing_id,
                            "status": "approved"
                        }
                        
                        try:
                            order_response = self.session.post(f"{BASE_URL}/orders", json=order_data)
                            if order_response.status_code in [200, 201]:
                                self.log("✅ Created test order as workaround")
                            else:
                                self.log(f"⚠️ Order creation failed: {order_response.status_code}")
                        except Exception as e:
                            self.log(f"❌ Order creation error: {e}")
                
                else:
                    self.log("❌ No listings found to create test tender")
            
        except Exception as e:
            self.log(f"❌ Error creating test tender data: {e}")

    def test_bought_items_detailed(self):
        """Detailed test of bought items endpoint"""
        self.log("🔍 Detailed bought items analysis...")
        
        try:
            response = self.session.get(f"{BASE_URL}/user/bought-items/{self.demo_user_id}")
            
            if response.status_code == 200:
                bought_items = response.json()
                self.log(f"📊 Bought items response: {len(bought_items)} items")
                
                if len(bought_items) == 0:
                    self.log("❌ CONFIRMED: Backend returns empty array for bought items")
                    self.log("🔍 This means either:")
                    self.log("   1. No accepted tenders exist for this user")
                    self.log("   2. No completed orders exist for this user")
                    self.log("   3. The user ID being used is incorrect")
                else:
                    self.log("✅ Found bought items:")
                    for item in bought_items:
                        self.log(f"   - {item.get('title')} - €{item.get('price')} from {item.get('seller_name')}")
                
                return bought_items
            else:
                self.log(f"❌ Bought items API failed: {response.status_code}")
                return []
                
        except Exception as e:
            self.log(f"❌ Error testing bought items: {e}")
            return []

    def test_baskets_detailed(self):
        """Detailed test of baskets endpoint"""
        self.log("🔍 Detailed baskets analysis...")
        
        try:
            response = self.session.get(f"{BASE_URL}/user/baskets/{self.demo_user_id}")
            
            if response.status_code == 200:
                baskets = response.json()
                self.log(f"📊 Baskets response: {len(baskets)} baskets")
                
                if len(baskets) > 0:
                    self.log("✅ Found baskets:")
                    for basket in baskets:
                        items_count = len(basket.get('items', []))
                        self.log(f"   - '{basket.get('name')}' with {items_count} items")
                        self.log(f"     Description: {basket.get('description', 'No description')}")
                        self.log(f"     Created: {basket.get('created_at', 'Unknown')}")
                else:
                    self.log("❌ No baskets found")
                
                return baskets
            else:
                self.log(f"❌ Baskets API failed: {response.status_code}")
                return []
                
        except Exception as e:
            self.log(f"❌ Error testing baskets: {e}")
            return []

    def check_user_id_consistency(self):
        """Check if the user ID is consistent across different endpoints"""
        self.log("🔍 Checking user ID consistency...")
        
        try:
            # Get user profile
            profile_response = self.session.get(f"{BASE_URL}/auth/profile/{self.demo_user_id}")
            if profile_response.status_code == 200:
                profile = profile_response.json()
                profile_id = profile.get('id')
                profile_email = profile.get('email')
                self.log(f"✅ Profile endpoint confirms ID: {profile_id}")
                self.log(f"   Email: {profile_email}")
                
                if profile_id == self.demo_user_id:
                    self.log("✅ User ID is consistent")
                else:
                    self.log(f"❌ User ID mismatch! Login: {self.demo_user_id}, Profile: {profile_id}")
            else:
                self.log(f"❌ Profile check failed: {profile_response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Error checking user ID consistency: {e}")

    def investigate_frontend_backend_mismatch(self):
        """Main investigation method"""
        self.log("🚀 Starting Buy Management Data Synchronization Investigation")
        self.log("=" * 80)
        self.log("PROBLEM: Frontend shows 1 bought item and 2 baskets, but backend APIs return empty arrays for bought items.")
        self.log("=" * 80)
        
        # 1. Get demo user ID
        if not self.get_demo_user_id():
            self.log("❌ Cannot proceed without demo user ID")
            return
        
        # 2. Check user ID consistency
        self.check_user_id_consistency()
        
        # 3. Check database collections
        self.check_database_collections()
        
        # 4. Test bought items in detail
        bought_items = self.test_bought_items_detailed()
        
        # 5. Test baskets in detail
        baskets = self.test_baskets_detailed()
        
        # 6. Try to create test data
        self.create_test_tender_data()
        
        # 7. Test again after creating data
        self.log("🔄 Re-testing after attempting to create test data...")
        bought_items_after = self.test_bought_items_detailed()
        
        # 8. Analysis and recommendations
        self.log("=" * 80)
        self.log("📊 INVESTIGATION RESULTS")
        self.log("=" * 80)
        
        self.log(f"Demo User ID: {self.demo_user_id}")
        self.log(f"Bought Items (initial): {len(bought_items)} items")
        self.log(f"Bought Items (after test data): {len(bought_items_after)} items")
        self.log(f"Baskets: {len(baskets)} baskets")
        
        self.log("\n🔍 ROOT CAUSE ANALYSIS:")
        
        if len(bought_items) == 0:
            self.log("❌ CONFIRMED: Backend bought-items API returns empty array")
            self.log("📝 LIKELY CAUSES:")
            self.log("   1. No accepted tenders exist for demo user in database")
            self.log("   2. No completed orders exist for demo user in database")
            self.log("   3. Frontend is using cached/mock data")
            self.log("   4. Frontend is using a different user ID")
            
        if len(baskets) >= 2:
            self.log("✅ CONFIRMED: Backend baskets API returns data (matches frontend)")
            
        self.log("\n💡 RECOMMENDATIONS:")
        self.log("   1. Create test tenders/orders for demo user")
        self.log("   2. Verify frontend user ID matches backend user ID")
        self.log("   3. Check if frontend has cached data")
        self.log("   4. Implement tender creation endpoints if missing")
        self.log("   5. Add sample data to database for testing")
        
        self.log("\n🎯 NEXT STEPS:")
        self.log("   1. Main agent should create test accepted tenders")
        self.log("   2. Main agent should create test completed orders")
        self.log("   3. Verify frontend uses correct API endpoints")
        self.log("   4. Clear any frontend caching")

if __name__ == "__main__":
    investigator = BuyManagementInvestigator()
    investigator.investigate_frontend_backend_mismatch()