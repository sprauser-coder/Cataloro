#!/usr/bin/env python3
"""
Tenders Collection Investigation
Direct investigation of tenders collection to find inflated revenue data
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class TendersInvestigator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        
    def investigate_tenders_collection(self):
        """Investigate tenders collection through available endpoints"""
        print("🔍 INVESTIGATING TENDERS COLLECTION")
        print("=" * 60)
        
        # Login as admin to get access to more data
        admin_response = self.session.post(f"{self.backend_url}/auth/login", 
                                         json={"email": "admin@cataloro.com", "password": "admin"})
        
        if admin_response.status_code != 200:
            print("❌ Could not login as admin")
            return
        
        admin_user = admin_response.json().get("user", {})
        admin_user_id = admin_user.get("id")
        print(f"✅ Logged in as admin: {admin_user_id}")
        
        # Get all listings to check for tenders
        listings_response = self.session.get(f"{self.backend_url}/listings")
        if listings_response.status_code != 200:
            print("❌ Could not get listings")
            return
        
        listings_data = listings_response.json()
        all_listings = listings_data.get("listings", [])
        print(f"📋 Found {len(all_listings)} total listings")
        
        total_accepted_revenue = 0.0
        accepted_tenders_found = []
        
        # Check each listing for tenders
        for listing in all_listings:
            listing_id = listing.get("id")
            if not listing_id:
                continue
                
            # Try to get tenders for this listing (if endpoint exists)
            try:
                # Check if there's a tenders endpoint for this listing
                tenders_response = self.session.get(f"{self.backend_url}/tenders/listing/{listing_id}")
                
                if tenders_response.status_code == 200:
                    tenders = tenders_response.json()
                    
                    for tender in tenders:
                        if tender.get("status") == "accepted":
                            offer_amount = tender.get("offer_amount", 0)
                            total_accepted_revenue += offer_amount
                            accepted_tenders_found.append({
                                "listing_id": listing_id,
                                "listing_title": listing.get("title", "Unknown"),
                                "offer_amount": offer_amount,
                                "buyer_id": tender.get("buyer_id", "Unknown"),
                                "accepted_at": tender.get("accepted_at", "Unknown")
                            })
                            
                            print(f"💰 Accepted tender found:")
                            print(f"   Listing: {listing.get('title', 'Unknown')}")
                            print(f"   Amount: €{offer_amount}")
                            print(f"   Buyer: {tender.get('buyer_id', 'Unknown')}")
                            print()
                            
            except Exception as e:
                # Endpoint might not exist, continue
                pass
        
        print("=" * 60)
        print("TENDERS INVESTIGATION SUMMARY")
        print("=" * 60)
        print(f"Total accepted tenders found: {len(accepted_tenders_found)}")
        print(f"Total accepted revenue: €{total_accepted_revenue}")
        
        # Get dashboard revenue for comparison
        dashboard_response = self.session.get(f"{self.backend_url}/admin/dashboard")
        dashboard_revenue = 0
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            dashboard_revenue = dashboard_data.get("kpis", {}).get("revenue", 0)
        
        print(f"Dashboard revenue: €{dashboard_revenue}")
        print(f"Discrepancy: €{dashboard_revenue - total_accepted_revenue}")
        
        if dashboard_revenue > total_accepted_revenue + 100:
            print(f"\n🚨 CRITICAL ISSUE CONFIRMED!")
            print(f"Dashboard shows €{dashboard_revenue} but only €{total_accepted_revenue} in accepted tenders")
            print(f"There's €{dashboard_revenue - total_accepted_revenue} of unexplained revenue")
            print("\nPossible causes:")
            print("1. Test/dummy tenders with inflated amounts in database")
            print("2. Tenders collection contains non-marketplace data")
            print("3. Dashboard calculation includes wrong data sources")
            
            # Try to access tender management to see more data
            print(f"\n🔍 Checking tender management for admin user...")
            tender_mgmt_response = self.session.get(f"{self.backend_url}/tenders/seller/{admin_user_id}/overview")
            
            if tender_mgmt_response.status_code == 200:
                tender_overview = tender_mgmt_response.json()
                print(f"Tender overview response: {json.dumps(tender_overview, indent=2)}")
            else:
                print(f"Could not access tender overview: HTTP {tender_mgmt_response.status_code}")
        
        return accepted_tenders_found, total_accepted_revenue, dashboard_revenue

    def check_specific_users_tenders(self):
        """Check tenders for specific users that might have inflated data"""
        print("\n🔍 CHECKING SPECIFIC USERS FOR INFLATED TENDERS")
        print("=" * 60)
        
        # Check demo user
        demo_response = self.session.post(f"{self.backend_url}/auth/login", 
                                        json={"email": "demo@example.com", "password": "demo"})
        
        if demo_response.status_code == 200:
            demo_user = demo_response.json().get("user", {})
            demo_user_id = demo_user.get("id")
            
            print(f"📋 Checking demo user: {demo_user_id}")
            
            # Check demo user's submitted tenders
            demo_tenders_response = self.session.get(f"{self.backend_url}/tenders/buyer/{demo_user_id}")
            
            if demo_tenders_response.status_code == 200:
                demo_tenders = demo_tenders_response.json()
                print(f"Demo user has {len(demo_tenders)} tenders")
                
                for tender in demo_tenders:
                    if tender.get("status") == "accepted":
                        print(f"   Accepted tender: €{tender.get('offer_amount', 0)} for listing {tender.get('listing_id', 'Unknown')}")
            else:
                print(f"Could not get demo user tenders: HTTP {demo_tenders_response.status_code}")
        
        # Check admin user tenders
        admin_response = self.session.post(f"{self.backend_url}/auth/login", 
                                         json={"email": "admin@cataloro.com", "password": "admin"})
        
        if admin_response.status_code == 200:
            admin_user = admin_response.json().get("user", {})
            admin_user_id = admin_user.get("id")
            
            print(f"\n📋 Checking admin user: {admin_user_id}")
            
            # Check admin user's submitted tenders
            admin_tenders_response = self.session.get(f"{self.backend_url}/tenders/buyer/{admin_user_id}")
            
            if admin_tenders_response.status_code == 200:
                admin_tenders = admin_tenders_response.json()
                print(f"Admin user has {len(admin_tenders)} tenders")
                
                total_admin_accepted = 0
                for tender in admin_tenders:
                    if tender.get("status") == "accepted":
                        amount = tender.get('offer_amount', 0)
                        total_admin_accepted += amount
                        print(f"   Accepted tender: €{amount} for listing {tender.get('listing_id', 'Unknown')}")
                
                print(f"Total admin accepted tenders: €{total_admin_accepted}")
                
                if total_admin_accepted > 1000:
                    print(f"🚨 FOUND INFLATED DATA: Admin user has €{total_admin_accepted} in accepted tenders!")
                    print("This is likely test/dummy data that should not be counted in dashboard revenue")
                    
            else:
                print(f"Could not get admin user tenders: HTTP {admin_tenders_response.status_code}")

if __name__ == "__main__":
    investigator = TendersInvestigator()
    investigator.investigate_tenders_collection()
    investigator.check_specific_users_tenders()