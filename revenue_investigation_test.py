#!/usr/bin/env python3
"""
Revenue Investigation Test
Deep dive into revenue calculation to identify the source of inflated figures
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class RevenueInvestigator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        
    def investigate_revenue_sources(self):
        """Investigate all possible revenue sources"""
        print("🔍 INVESTIGATING REVENUE SOURCES")
        print("=" * 60)
        
        total_revenue = 0.0
        revenue_breakdown = {}
        
        # 1. Check tenders collection for accepted tenders
        print("1. Checking accepted tenders...")
        try:
            # We need to check if there's a tenders endpoint or use admin access
            # Let's try to get tender data through user endpoints
            
            # Check for demo_user tenders (known to have accepted tenders)
            demo_user_response = self.session.post(f"{self.backend_url}/auth/login", 
                                                 json={"email": "demo@example.com", "password": "demo"})
            
            if demo_user_response.status_code == 200:
                demo_user = demo_user_response.json().get("user", {})
                demo_user_id = demo_user.get("id")
                
                if demo_user_id:
                    # Try to get deals for demo user
                    deals_response = self.session.get(f"{self.backend_url}/user/my-deals/{demo_user_id}")
                    if deals_response.status_code == 200:
                        deals = deals_response.json()
                        tender_revenue = sum(deal.get("amount", 0) for deal in deals)
                        revenue_breakdown["accepted_tenders"] = tender_revenue
                        total_revenue += tender_revenue
                        print(f"   Accepted tenders revenue: €{tender_revenue}")
                        print(f"   Number of deals found: {len(deals)}")
                    else:
                        print(f"   Could not access deals: HTTP {deals_response.status_code}")
            else:
                print(f"   Could not login as demo user: HTTP {demo_user_response.status_code}")
                
        except Exception as e:
            print(f"   Error checking tenders: {e}")
        
        # 2. Check sold listings
        print("\n2. Checking sold listings...")
        try:
            listings_response = self.session.get(f"{self.backend_url}/listings")
            if listings_response.status_code == 200:
                listings_data = listings_response.json()
                all_listings = listings_data.get("listings", [])
                
                sold_revenue = 0.0
                sold_count = 0
                for listing in all_listings:
                    if listing.get("status") == "sold":
                        price = listing.get("final_price", listing.get("price", 0))
                        sold_revenue += price
                        sold_count += 1
                        print(f"   Sold listing: {listing.get('title', 'Unknown')} - €{price}")
                
                revenue_breakdown["sold_listings"] = sold_revenue
                total_revenue += sold_revenue
                print(f"   Total sold listings revenue: €{sold_revenue} ({sold_count} listings)")
            else:
                print(f"   Could not access listings: HTTP {listings_response.status_code}")
                
        except Exception as e:
            print(f"   Error checking sold listings: {e}")
        
        # 3. Check browse endpoint for any revenue indicators
        print("\n3. Checking browse endpoint for bid information...")
        try:
            browse_response = self.session.get(f"{self.backend_url}/marketplace/browse")
            if browse_response.status_code == 200:
                browse_listings = browse_response.json()
                
                bid_revenue = 0.0
                high_bids = []
                for listing in browse_listings:
                    bid_info = listing.get("bid_info", {})
                    if bid_info.get("has_bids", False):
                        highest_bid = bid_info.get("highest_bid", 0)
                        if highest_bid > listing.get("price", 0):
                            high_bids.append({
                                "title": listing.get("title", "Unknown"),
                                "starting_price": listing.get("price", 0),
                                "highest_bid": highest_bid,
                                "difference": highest_bid - listing.get("price", 0)
                            })
                            bid_revenue += highest_bid
                
                revenue_breakdown["potential_bid_revenue"] = bid_revenue
                print(f"   Potential revenue from bids: €{bid_revenue}")
                print(f"   High bid listings: {len(high_bids)}")
                for bid in high_bids[:5]:  # Show first 5
                    print(f"     {bid['title']}: €{bid['starting_price']} → €{bid['highest_bid']} (+€{bid['difference']})")
                    
        except Exception as e:
            print(f"   Error checking browse data: {e}")
        
        # 4. Try to access admin users to check for admin deals
        print("\n4. Checking admin user deals...")
        try:
            admin_response = self.session.post(f"{self.backend_url}/auth/login", 
                                             json={"email": "admin@cataloro.com", "password": "admin"})
            
            if admin_response.status_code == 200:
                admin_user = admin_response.json().get("user", {})
                admin_user_id = admin_user.get("id")
                
                if admin_user_id:
                    admin_deals_response = self.session.get(f"{self.backend_url}/user/my-deals/{admin_user_id}")
                    if admin_deals_response.status_code == 200:
                        admin_deals = admin_deals_response.json()
                        admin_revenue = sum(deal.get("amount", 0) for deal in admin_deals)
                        revenue_breakdown["admin_deals"] = admin_revenue
                        print(f"   Admin deals revenue: €{admin_revenue}")
                        print(f"   Number of admin deals: {len(admin_deals)}")
                        
                        # Show details of admin deals
                        for deal in admin_deals[:3]:  # Show first 3
                            print(f"     Deal: €{deal.get('amount', 0)} - {deal.get('listing', {}).get('title', 'Unknown')}")
                    else:
                        print(f"   Could not access admin deals: HTTP {admin_deals_response.status_code}")
            else:
                print(f"   Could not login as admin: HTTP {admin_response.status_code}")
                
        except Exception as e:
            print(f"   Error checking admin deals: {e}")
        
        print("\n" + "=" * 60)
        print("REVENUE BREAKDOWN SUMMARY")
        print("=" * 60)
        
        dashboard_response = self.session.get(f"{self.backend_url}/admin/dashboard")
        dashboard_revenue = 0
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            dashboard_revenue = dashboard_data.get("kpis", {}).get("revenue", 0)
        
        print(f"Dashboard Revenue: €{dashboard_revenue}")
        print(f"Investigated Revenue Sources:")
        
        for source, amount in revenue_breakdown.items():
            print(f"  {source}: €{amount}")
        
        total_investigated = sum(revenue_breakdown.values())
        print(f"Total Investigated: €{total_investigated}")
        
        discrepancy = dashboard_revenue - total_investigated
        print(f"Unexplained Amount: €{discrepancy}")
        
        if discrepancy > 100:
            print(f"\n🚨 MAJOR DISCREPANCY: €{discrepancy} is unaccounted for!")
            print("This suggests the dashboard is including revenue from sources not accessible via API")
            print("Possible sources:")
            print("- Test/dummy data in deals collection")
            print("- Inflated tender amounts in database")
            print("- Incorrect calculation logic in dashboard endpoint")
        elif discrepancy < -100:
            print(f"\n⚠️  NEGATIVE DISCREPANCY: Dashboard shows €{discrepancy} less than investigated")
            print("This suggests some revenue sources are not being counted by dashboard")
        else:
            print(f"\n✅ REVENUE SOURCES MATCH: Discrepancy of €{discrepancy} is within acceptable range")
        
        return revenue_breakdown, dashboard_revenue

if __name__ == "__main__":
    investigator = RevenueInvestigator()
    investigator.investigate_revenue_sources()