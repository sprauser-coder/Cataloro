#!/usr/bin/env python3
"""
DATABASE DEEP DIVE - Investigate the missing listings issue
Focus: Direct database inspection to understand why listings are missing
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://cataloro-market.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class DatabaseInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                print("✅ Admin authenticated successfully")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def investigate_listings_discrepancy(self):
        """Investigate why public and admin endpoints show different counts"""
        print("\n🔍 INVESTIGATING LISTINGS DISCREPANCY")
        print("=" * 60)
        
        # Get public listings with detailed info
        try:
            response = self.session.get(f"{BACKEND_URL}/listings?limit=100")
            if response.status_code == 200:
                public_listings = response.json()
                print(f"📊 Public listings endpoint: {len(public_listings)} listings")
                
                for i, listing in enumerate(public_listings):
                    print(f"   {i+1}. '{listing.get('title', 'Unknown')}' - Status: {listing.get('status', 'Unknown')}")
                    print(f"      ID: {listing.get('id', 'Unknown')}")
                    print(f"      Seller: {listing.get('seller_name', 'Unknown')}")
                    print(f"      Created: {listing.get('created_at', 'Unknown')}")
                    print()
            else:
                print(f"❌ Failed to get public listings: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting public listings: {str(e)}")
        
        # Get admin listings with detailed info
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/listings")
            if response.status_code == 200:
                admin_listings = response.json()
                print(f"📊 Admin listings endpoint: {len(admin_listings)} listings")
                
                for i, listing in enumerate(admin_listings):
                    print(f"   {i+1}. '{listing.get('title', 'Unknown')}' - Status: {listing.get('status', 'Unknown')}")
                    print(f"      ID: {listing.get('id', 'Unknown')}")
                    print(f"      Seller: {listing.get('seller_name', 'Unknown')}")
                    print(f"      Views: {listing.get('views', 0)}")
                    print(f"      Created: {listing.get('created_at', 'Unknown')}")
                    print()
            else:
                print(f"❌ Failed to get admin listings: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting admin listings: {str(e)}")

    def test_different_listing_filters(self):
        """Test different filters to see if listings are being filtered out"""
        print("\n🔍 TESTING DIFFERENT LISTING FILTERS")
        print("=" * 60)
        
        filters_to_test = [
            ({}, "No filters"),
            ({"status": "active"}, "Active only"),
            ({"status": "sold"}, "Sold only"),
            ({"status": "expired"}, "Expired only"),
            ({"limit": 1000}, "High limit"),
            ({"skip": 0, "limit": 1000}, "With pagination"),
        ]
        
        for filter_params, description in filters_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}/listings", params=filter_params)
                
                if response.status_code == 200:
                    listings = response.json()
                    print(f"📊 {description}: {len(listings)} listings")
                    
                    # Show status breakdown
                    status_counts = {}
                    for listing in listings:
                        status = listing.get('status', 'unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    if status_counts:
                        status_str = ", ".join([f"{k}: {v}" for k, v in status_counts.items()])
                        print(f"   Status breakdown: {status_str}")
                    
                else:
                    print(f"❌ {description}: Failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")

    def check_user_listings(self):
        """Check if there are user-specific listings that might not be showing"""
        print("\n🔍 CHECKING USER-SPECIFIC LISTINGS")
        print("=" * 60)
        
        # Get all users first
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            if response.status_code == 200:
                users = response.json()
                print(f"📊 Total users in system: {len(users)}")
                
                # Check each user's listing count
                for user in users:
                    user_id = user.get('id', '')
                    username = user.get('username', 'Unknown')
                    total_listings = user.get('total_listings', 0)
                    
                    print(f"   User: {username} - {total_listings} listings")
                    
            else:
                print(f"❌ Failed to get users: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting users: {str(e)}")

    def check_my_listings_endpoint(self):
        """Check the my-listings endpoint for current user"""
        print("\n🔍 CHECKING MY-LISTINGS ENDPOINT")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/listings/my-listings")
            
            if response.status_code == 200:
                my_listings = response.json()
                print(f"📊 Current user's listings: {len(my_listings)} listings")
                
                for i, listing in enumerate(my_listings):
                    print(f"   {i+1}. '{listing.get('title', 'Unknown')}' - Status: {listing.get('status', 'Unknown')}")
                    print(f"      ID: {listing.get('id', 'Unknown')}")
                    print(f"      Created: {listing.get('created_at', 'Unknown')}")
                    
            else:
                print(f"❌ Failed to get my listings: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting my listings: {str(e)}")

    def test_create_new_listing(self):
        """Test creating a new listing to see if the system is working"""
        print("\n🔍 TESTING NEW LISTING CREATION")
        print("=" * 60)
        
        test_listing = {
            "title": "Database Investigation Test Listing",
            "description": "This is a test listing created during database investigation",
            "category": "Electronics",
            "listing_type": "fixed_price",
            "price": 99.99,
            "condition": "New",
            "quantity": 1,
            "location": "Test Location"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/listings", json=test_listing)
            
            if response.status_code == 200:
                new_listing = response.json()
                listing_id = new_listing.get('id', 'Unknown')
                print(f"✅ Successfully created test listing: {listing_id}")
                
                # Now check if it appears in listings
                response = self.session.get(f"{BACKEND_URL}/listings")
                if response.status_code == 200:
                    listings = response.json()
                    print(f"📊 After creation, public listings count: {len(listings)}")
                    
                    # Check if our new listing is there
                    found = any(l.get('id') == listing_id for l in listings)
                    if found:
                        print("✅ New listing appears in public listings")
                    else:
                        print("❌ New listing NOT appearing in public listings")
                
                return listing_id
            else:
                print(f"❌ Failed to create test listing: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating test listing: {str(e)}")
            return None

    def check_database_statistics(self):
        """Check database statistics from admin panel"""
        print("\n🔍 CHECKING DATABASE STATISTICS")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/stats")
            
            if response.status_code == 200:
                stats = response.json()
                print("📊 Database Statistics:")
                print(f"   Total users: {stats.get('total_users', 'Unknown')}")
                print(f"   Active users: {stats.get('active_users', 'Unknown')}")
                print(f"   Total listings: {stats.get('total_listings', 'Unknown')}")
                print(f"   Active listings: {stats.get('active_listings', 'Unknown')}")
                print(f"   Total orders: {stats.get('total_orders', 'Unknown')}")
                print(f"   Total revenue: ${stats.get('total_revenue', 'Unknown')}")
                
                # This should help us understand the true state of the database
                return stats
            else:
                print(f"❌ Failed to get database stats: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting database stats: {str(e)}")
            return None

    def run_deep_investigation(self):
        """Run complete database investigation"""
        print("🔍 DATABASE DEEP DIVE INVESTIGATION")
        print("=" * 80)
        print("Investigating the root cause of missing listings issue")
        print("=" * 80)
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Check database statistics first
        stats = self.check_database_statistics()
        
        # Investigate the discrepancy between endpoints
        self.investigate_listings_discrepancy()
        
        # Test different filters
        self.test_different_listing_filters()
        
        # Check user listings
        self.check_user_listings()
        
        # Check my-listings endpoint
        self.check_my_listings_endpoint()
        
        # Test creating a new listing
        new_listing_id = self.test_create_new_listing()
        
        # Final analysis
        print("\n" + "=" * 80)
        print("DEEP DIVE ANALYSIS RESULTS")
        print("=" * 80)
        
        if stats:
            total_listings = stats.get('total_listings', 0)
            active_listings = stats.get('active_listings', 0)
            
            print(f"🔍 Database reports: {total_listings} total listings, {active_listings} active")
            
            if total_listings <= 2:
                print("🚨 CONFIRMED: Database has very few listings")
                print("🔍 POSSIBLE CAUSES:")
                print("   • Listings were accidentally deleted")
                print("   • Database was reset or corrupted")
                print("   • Migration issue lost data")
                print("   • Bulk delete operation was performed")
            elif active_listings <= 2 and total_listings > active_listings:
                print("🚨 CONFIRMED: Most listings are inactive/sold/expired")
                print("🔍 POSSIBLE CAUSES:")
                print("   • Listings expired or were marked as sold")
                print("   • Status update issue changed listings to inactive")
            else:
                print("🤔 Database stats don't match endpoint results")
                print("🔍 POSSIBLE CAUSES:")
                print("   • Filtering issue in API endpoints")
                print("   • Database query problems")
                print("   • Caching issues")
        
        if new_listing_id:
            print("✅ New listing creation works - system is functional")
        else:
            print("❌ Cannot create new listings - system has issues")
        
        return True

if __name__ == "__main__":
    investigator = DatabaseInvestigator()
    investigator.run_deep_investigation()