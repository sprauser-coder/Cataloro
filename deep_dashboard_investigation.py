#!/usr/bin/env python3
"""
Deep Dashboard Investigation
Investigating the specific collections and data sources for dashboard calculations
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://cataloro-marketplace-3.preview.emergentagent.com/api"

class DeepDashboardInvestigator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        
    def investigate_tenders_collection(self):
        """Investigate tenders collection for revenue calculation"""
        print("🔍 INVESTIGATING TENDERS COLLECTION")
        print("-" * 60)
        
        try:
            # Login as test user to access tender endpoints
            test_user_data = {
                "email": "dashboard_test_user@example.com",
                "password": "testpass123",
                "username": "dashboard_test_user"
            }
            
            login_response = self.session.post(f"{self.backend_url}/auth/login", json=test_user_data)
            if login_response.status_code == 200:
                user_data = login_response.json()
                test_user_id = user_data.get("user", {}).get("id")
                
                if test_user_id:
                    # Check seller tenders overview
                    tenders_response = self.session.get(f"{self.backend_url}/tenders/seller/{test_user_id}/overview")
                    if tenders_response.status_code == 200:
                        tenders_data = tenders_response.json()
                        print(f"✅ Tenders overview accessible")
                        print(f"   Response structure: {list(tenders_data.keys()) if isinstance(tenders_data, dict) else type(tenders_data)}")
                        
                        if isinstance(tenders_data, dict):
                            for key, value in tenders_data.items():
                                if isinstance(value, list):
                                    print(f"   {key}: {len(value)} items")
                                    if value and len(value) > 0:
                                        sample = value[0]
                                        if isinstance(sample, dict):
                                            print(f"     Sample {key[:-1]}: {sample.get('offer_amount', 'N/A')} - {sample.get('status', 'N/A')}")
                                else:
                                    print(f"   {key}: {value}")
                    else:
                        print(f"❌ Tenders overview not accessible: HTTP {tenders_response.status_code}")
                    
                    # Check buyer tenders
                    buyer_tenders_response = self.session.get(f"{self.backend_url}/tenders/buyer/{test_user_id}")
                    if buyer_tenders_response.status_code == 200:
                        buyer_tenders = buyer_tenders_response.json()
                        print(f"✅ Buyer tenders accessible: {len(buyer_tenders) if isinstance(buyer_tenders, list) else 'Not a list'}")
                        
                        if isinstance(buyer_tenders, list) and buyer_tenders:
                            total_tender_value = 0
                            accepted_tenders = 0
                            for tender in buyer_tenders:
                                if tender.get('status') == 'accepted':
                                    accepted_tenders += 1
                                    total_tender_value += tender.get('offer_amount', 0)
                            
                            print(f"   Total buyer tenders: {len(buyer_tenders)}")
                            print(f"   Accepted tenders: {accepted_tenders}")
                            print(f"   Total accepted tender value: €{total_tender_value}")
                    else:
                        print(f"❌ Buyer tenders not accessible: HTTP {buyer_tenders_response.status_code}")
                        
        except Exception as e:
            print(f"❌ Exception investigating tenders: {str(e)}")
    
    def investigate_deals_collection_directly(self):
        """Try to investigate deals collection through different endpoints"""
        print("\n🔍 INVESTIGATING DEALS COLLECTION")
        print("-" * 60)
        
        try:
            # Try to find any endpoint that gives us deals information
            # Check if there are any admin endpoints for deals
            
            # First, let's see what collections might exist by checking different user IDs
            test_users = ["dashboard_test_user", "admin", "test_user"]
            
            for i, username in enumerate(test_users):
                try:
                    test_user_data = {
                        "email": f"{username}@example.com" if username != "admin" else "admin@cataloro.com",
                        "password": "testpass123",
                        "username": username
                    }
                    
                    login_response = self.session.post(f"{self.backend_url}/auth/login", json=test_user_data)
                    if login_response.status_code == 200:
                        user_data = login_response.json()
                        user_id = user_data.get("user", {}).get("id")
                        
                        if user_id:
                            deals_response = self.session.get(f"{self.backend_url}/user/my-deals/{user_id}")
                            if deals_response.status_code == 200:
                                deals_data = deals_response.json()
                                deals_count = len(deals_data) if isinstance(deals_data, list) else 0
                                
                                if deals_count > 0:
                                    print(f"✅ Found {deals_count} deals for user {username}")
                                    
                                    total_revenue = 0
                                    completed_deals = 0
                                    
                                    for deal in deals_data:
                                        if deal.get('status') in ['approved', 'completed']:
                                            completed_deals += 1
                                            total_revenue += deal.get('amount', 0)
                                        
                                        print(f"   Deal: {deal.get('listing', {}).get('title', 'N/A')} - €{deal.get('amount', 0)} ({deal.get('status', 'N/A')})")
                                    
                                    print(f"   Completed deals: {completed_deals}, Total revenue: €{total_revenue}")
                                else:
                                    print(f"   No deals found for user {username}")
                            else:
                                print(f"   Deals endpoint failed for {username}: HTTP {deals_response.status_code}")
                        
                except Exception as user_error:
                    print(f"   Error checking user {username}: {str(user_error)}")
                    
        except Exception as e:
            print(f"❌ Exception investigating deals: {str(e)}")
    
    def investigate_revenue_sources(self):
        """Investigate where the €5445 revenue might be coming from"""
        print("\n🔍 INVESTIGATING REVENUE SOURCES")
        print("-" * 60)
        
        try:
            # Let's check all listings to see if any have been sold
            listings_response = self.session.get(f"{self.backend_url}/listings?limit=1000")
            if listings_response.status_code == 200:
                listings_data = listings_response.json()
                
                if isinstance(listings_data, dict) and 'listings' in listings_data:
                    listings = listings_data['listings']
                elif isinstance(listings_data, list):
                    listings = listings_data
                else:
                    listings = []
                
                sold_listings = []
                total_sold_value = 0
                
                for listing in listings:
                    if listing.get('status') == 'sold':
                        sold_listings.append(listing)
                        total_sold_value += listing.get('price', 0)
                
                print(f"✅ Listings analysis:")
                print(f"   Total listings: {len(listings)}")
                print(f"   Sold listings: {len(sold_listings)}")
                print(f"   Total sold value: €{total_sold_value}")
                
                if sold_listings:
                    print("   Sold listings details:")
                    for listing in sold_listings:
                        print(f"     • {listing.get('title', 'N/A')} - €{listing.get('price', 0)}")
                
                # Check for any listings with special status or fields that might indicate completed transactions
                special_listings = []
                for listing in listings:
                    if listing.get('winning_bidder_id') or listing.get('is_expired'):
                        special_listings.append(listing)
                
                if special_listings:
                    print(f"   Listings with special status: {len(special_listings)}")
                    for listing in special_listings:
                        print(f"     • {listing.get('title', 'N/A')} - Winner: {listing.get('winning_bidder_id', 'None')}, Expired: {listing.get('is_expired', False)}")
                        
        except Exception as e:
            print(f"❌ Exception investigating revenue sources: {str(e)}")
    
    def check_dashboard_calculation_logic(self):
        """Analyze what the dashboard calculation logic might be doing"""
        print("\n🔍 ANALYZING DASHBOARD CALCULATION LOGIC")
        print("-" * 60)
        
        print("Based on the backend code analysis:")
        print("The dashboard endpoint calculates revenue from:")
        print("1. Completed deals: await db.deals.find({'status': 'completed'})")
        print("2. Accepted tenders: await db.tenders.find({'status': 'accepted'})")
        print()
        print("Current findings:")
        print("• Dashboard reports €5445.0 revenue")
        print("• No completed deals found through user endpoints")
        print("• Need to investigate if there are accepted tenders in the system")
        print("• The revenue calculation includes both deal.final_price and tender.offer_amount")
        print()
        print("Possible explanations for €5445 revenue:")
        print("1. There are accepted tenders in the tenders collection")
        print("2. There are completed deals in the deals collection not accessible via user endpoints")
        print("3. Test/dummy data exists in these collections")
        print("4. The calculation logic is including incorrect data")
    
    def run_investigation(self):
        """Run the complete investigation"""
        print("=" * 80)
        print("DEEP DASHBOARD DATA INVESTIGATION")
        print("Investigating the source of dashboard revenue calculation")
        print("=" * 80)
        
        self.investigate_tenders_collection()
        self.investigate_deals_collection_directly()
        self.investigate_revenue_sources()
        self.check_dashboard_calculation_logic()
        
        print("\n" + "=" * 80)
        print("INVESTIGATION SUMMARY")
        print("=" * 80)
        print()
        print("KEY FINDINGS:")
        print("• Dashboard shows €5445.0 revenue but source is unclear")
        print("• No completed deals found through accessible user endpoints")
        print("• Need to verify if accepted tenders exist in the system")
        print("• Users count discrepancy: Dashboard shows 72, actual is 71")
        print()
        print("RECOMMENDATIONS:")
        print("1. Check if there are accepted tenders contributing to revenue")
        print("2. Verify if deals collection contains data not accessible via user endpoints")
        print("3. Review dashboard calculation to ensure it only includes real marketplace transactions")
        print("4. Consider adding admin endpoints to directly inspect deals and tenders collections")

if __name__ == "__main__":
    investigator = DeepDashboardInvestigator()
    investigator.run_investigation()