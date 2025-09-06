#!/usr/bin/env python3
"""
Tender Revenue Investigation
Investigating accepted tenders that might be contributing to the €5445 revenue
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

class TenderRevenueInvestigator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        
    def investigate_all_user_tenders(self):
        """Check tenders for multiple users to find accepted tenders"""
        print("🔍 INVESTIGATING TENDERS ACROSS ALL USERS")
        print("-" * 60)
        
        total_accepted_tenders = 0
        total_accepted_revenue = 0
        
        try:
            # Get all users first
            users_response = self.session.get(f"{self.backend_url}/admin/users")
            if users_response.status_code == 200:
                users_data = users_response.json()
                print(f"✅ Found {len(users_data)} users to check")
                
                # Check tenders for each user (both as buyer and seller)
                for i, user in enumerate(users_data[:10]):  # Check first 10 users to avoid too many requests
                    user_id = user.get('id')
                    username = user.get('username', 'Unknown')
                    
                    if user_id:
                        try:
                            # Check as buyer
                            buyer_response = self.session.get(f"{self.backend_url}/tenders/buyer/{user_id}")
                            if buyer_response.status_code == 200:
                                buyer_tenders = buyer_response.json()
                                if isinstance(buyer_tenders, list) and buyer_tenders:
                                    accepted_as_buyer = [t for t in buyer_tenders if t.get('status') == 'accepted']
                                    if accepted_as_buyer:
                                        print(f"   User {username} (buyer): {len(accepted_as_buyer)} accepted tenders")
                                        for tender in accepted_as_buyer:
                                            amount = tender.get('offer_amount', 0)
                                            total_accepted_tenders += 1
                                            total_accepted_revenue += amount
                                            print(f"     • Accepted tender: €{amount} for listing {tender.get('listing_id', 'N/A')}")
                            
                            # Check as seller
                            seller_response = self.session.get(f"{self.backend_url}/tenders/seller/{user_id}/overview")
                            if seller_response.status_code == 200:
                                seller_data = seller_response.json()
                                if isinstance(seller_data, list):
                                    # This might be a list of listings with tenders
                                    for listing_tenders in seller_data:
                                        if isinstance(listing_tenders, dict) and 'tenders' in listing_tenders:
                                            tenders = listing_tenders['tenders']
                                            accepted_tenders = [t for t in tenders if t.get('status') == 'accepted']
                                            if accepted_tenders:
                                                print(f"   User {username} (seller): {len(accepted_tenders)} accepted tenders")
                                                for tender in accepted_tenders:
                                                    amount = tender.get('offer_amount', 0)
                                                    print(f"     • Accepted tender: €{amount} for listing {tender.get('listing_id', 'N/A')}")
                                
                        except Exception as user_error:
                            # Skip users that cause errors
                            continue
                
                print(f"\n📊 TENDER REVENUE SUMMARY:")
                print(f"   Total accepted tenders found: {total_accepted_tenders}")
                print(f"   Total accepted tender revenue: €{total_accepted_revenue}")
                
                return total_accepted_revenue
                
        except Exception as e:
            print(f"❌ Exception investigating tenders: {str(e)}")
            return 0
    
    def check_specific_listings_for_tenders(self):
        """Check specific listings that might have accepted tenders"""
        print("\n🔍 CHECKING SPECIFIC LISTINGS FOR TENDERS")
        print("-" * 60)
        
        try:
            # Get all listings
            listings_response = self.session.get(f"{self.backend_url}/listings?limit=1000")
            if listings_response.status_code == 200:
                listings_data = listings_response.json()
                
                if isinstance(listings_data, dict) and 'listings' in listings_data:
                    listings = listings_data['listings']
                elif isinstance(listings_data, list):
                    listings = listings_data
                else:
                    listings = []
                
                print(f"✅ Checking {len(listings)} listings for tenders")
                
                total_tender_revenue = 0
                listings_with_tenders = 0
                
                for listing in listings:
                    listing_id = listing.get('id')
                    title = listing.get('title', 'N/A')
                    
                    if listing_id:
                        try:
                            # Check tenders for this listing
                            tenders_response = self.session.get(f"{self.backend_url}/tenders/listing/{listing_id}")
                            if tenders_response.status_code == 200:
                                tenders_data = tenders_response.json()
                                if isinstance(tenders_data, list) and tenders_data:
                                    listings_with_tenders += 1
                                    accepted_tenders = [t for t in tenders_data if t.get('status') == 'accepted']
                                    
                                    if accepted_tenders:
                                        print(f"   Listing '{title}': {len(accepted_tenders)} accepted tenders")
                                        for tender in accepted_tenders:
                                            amount = tender.get('offer_amount', 0)
                                            total_tender_revenue += amount
                                            buyer_id = tender.get('buyer_id', 'N/A')
                                            print(f"     • €{amount} from buyer {buyer_id}")
                                    elif tenders_data:
                                        print(f"   Listing '{title}': {len(tenders_data)} tenders (none accepted)")
                        except Exception:
                            continue
                
                print(f"\n📊 LISTING TENDER SUMMARY:")
                print(f"   Listings with tenders: {listings_with_tenders}")
                print(f"   Total revenue from accepted tenders: €{total_tender_revenue}")
                
                return total_tender_revenue
                
        except Exception as e:
            print(f"❌ Exception checking listing tenders: {str(e)}")
            return 0
    
    def verify_dashboard_revenue_calculation(self):
        """Verify the dashboard revenue calculation matches our findings"""
        print("\n🔍 VERIFYING DASHBOARD REVENUE CALCULATION")
        print("-" * 60)
        
        try:
            # Get dashboard data
            dashboard_response = self.session.get(f"{self.backend_url}/admin/dashboard")
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                kpis = dashboard_data.get('kpis', {})
                dashboard_revenue = kpis.get('revenue', 0)
                
                print(f"✅ Dashboard revenue: €{dashboard_revenue}")
                
                # Compare with our findings
                print("\n📊 REVENUE SOURCE BREAKDOWN:")
                print(f"   Sold listings value: €425.0 (3 sold listings)")
                print(f"   Completed deals revenue: €0 (24 deals with €0 amounts)")
                print(f"   Dashboard reported revenue: €{dashboard_revenue}")
                print(f"   Unexplained revenue: €{dashboard_revenue - 425.0}")
                
                if dashboard_revenue > 425.0:
                    print(f"\n⚠️  REVENUE DISCREPANCY IDENTIFIED:")
                    print(f"   The dashboard shows €{dashboard_revenue - 425.0} more than the sold listings")
                    print(f"   This suggests there are accepted tenders or other revenue sources")
                    print(f"   that are not visible through the standard marketplace endpoints")
                
                return dashboard_revenue
                
        except Exception as e:
            print(f"❌ Exception verifying dashboard revenue: {str(e)}")
            return 0
    
    def run_investigation(self):
        """Run the complete tender revenue investigation"""
        print("=" * 80)
        print("TENDER REVENUE INVESTIGATION")
        print("Investigating the source of €5445 dashboard revenue")
        print("=" * 80)
        
        # Check tenders across users
        tender_revenue_from_users = self.investigate_all_user_tenders()
        
        # Check tenders for specific listings
        tender_revenue_from_listings = self.check_specific_listings_for_tenders()
        
        # Verify dashboard calculation
        dashboard_revenue = self.verify_dashboard_revenue_calculation()
        
        print("\n" + "=" * 80)
        print("FINAL INVESTIGATION RESULTS")
        print("=" * 80)
        print()
        print("REVENUE SOURCES IDENTIFIED:")
        print(f"• Sold listings: €425.0 (3 listings)")
        print(f"• Accepted tenders (user check): €{tender_revenue_from_users}")
        print(f"• Accepted tenders (listing check): €{tender_revenue_from_listings}")
        print(f"• Dashboard reported total: €{dashboard_revenue}")
        print()
        
        total_identified = 425.0 + max(tender_revenue_from_users, tender_revenue_from_listings)
        unexplained = dashboard_revenue - total_identified
        
        if abs(unexplained) < 1.0:  # Within €1 tolerance
            print("✅ REVENUE CALCULATION VERIFIED:")
            print(f"   All dashboard revenue (€{dashboard_revenue}) is accounted for")
        else:
            print("❌ REVENUE DISCREPANCY CONFIRMED:")
            print(f"   Dashboard shows €{dashboard_revenue}")
            print(f"   Identified sources total €{total_identified}")
            print(f"   Unexplained amount: €{unexplained}")
            print()
            print("POSSIBLE CAUSES:")
            print("• Test/dummy data in deals or tenders collections")
            print("• Accepted tenders not accessible via API endpoints")
            print("• Dashboard calculation including incorrect data")
            print("• Revenue from sources not checked (e.g., direct database entries)")
        
        print()
        print("RECOMMENDATIONS FOR MAIN AGENT:")
        print("1. Review dashboard revenue calculation logic in backend/server.py")
        print("2. Ensure only real marketplace transactions are included")
        print("3. Add logging to dashboard calculation to trace revenue sources")
        print("4. Consider adding admin endpoints to inspect deals/tenders collections directly")

if __name__ == "__main__":
    investigator = TenderRevenueInvestigator()
    investigator.run_investigation()