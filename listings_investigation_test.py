#!/usr/bin/env python3
"""
CRITICAL: Listings Management Data Source Investigation
Investigating why listings management shows 4 listings when there should be 0 active listings
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

def test_listings_endpoint():
    """Test /api/listings endpoint - check what data it returns"""
    print("=" * 80)
    print("1. TESTING /api/listings ENDPOINT")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BACKEND_URL}/listings")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict) and 'listings' in data:
                listings = data['listings']
                total_count = data.get('total', len(listings))
            else:
                listings = data if isinstance(data, list) else []
                total_count = len(listings)
            
            print(f"✅ Total listings returned: {len(listings)}")
            print(f"📊 Total count from API: {total_count}")
            
            # Analyze listing statuses
            status_counts = {}
            for listing in listings:
                status = listing.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"📈 Listings by status: {json.dumps(status_counts, indent=2)}")
            
            # Show first few listings for analysis
            print(f"\n📋 First 3 listings details:")
            for i, listing in enumerate(listings[:3]):
                print(f"  Listing {i+1}:")
                print(f"    ID: {listing.get('id', 'N/A')}")
                print(f"    Title: {listing.get('title', 'N/A')}")
                print(f"    Status: {listing.get('status', 'N/A')}")
                print(f"    Price: €{listing.get('price', 0)}")
                print(f"    Created: {listing.get('created_at', 'N/A')}")
            
            return listings, total_count
        else:
            print(f"❌ Failed to get listings: {response.text}")
            return [], 0
            
    except Exception as e:
        print(f"❌ Error testing /api/listings: {e}")
        return [], 0

def test_browse_endpoint():
    """Test /api/marketplace/browse endpoint - compare with listings"""
    print("\n" + "=" * 80)
    print("2. TESTING /api/marketplace/browse ENDPOINT")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BACKEND_URL}/marketplace/browse")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            listings = response.json()
            
            print(f"✅ Browse listings returned: {len(listings)}")
            
            # Analyze listing statuses
            status_counts = {}
            for listing in listings:
                status = listing.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"📈 Browse listings by status: {json.dumps(status_counts, indent=2)}")
            
            # Show first few listings for analysis
            print(f"\n📋 First 3 browse listings details:")
            for i, listing in enumerate(listings[:3]):
                print(f"  Listing {i+1}:")
                print(f"    ID: {listing.get('id', 'N/A')}")
                print(f"    Title: {listing.get('title', 'N/A')}")
                print(f"    Status: {listing.get('status', 'N/A')}")
                print(f"    Price: €{listing.get('price', 0)}")
                print(f"    Created: {listing.get('created_at', 'N/A')}")
            
            return listings
        else:
            print(f"❌ Failed to get browse listings: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error testing /api/marketplace/browse: {e}")
        return []

def test_admin_listings_endpoint():
    """Test if there's an /api/admin/listings endpoint"""
    print("\n" + "=" * 80)
    print("3. TESTING /api/admin/listings ENDPOINT")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/listings")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict) and 'listings' in data:
                listings = data['listings']
                total_count = data.get('total', len(listings))
            else:
                listings = data if isinstance(data, list) else []
                total_count = len(listings)
            
            print(f"✅ Admin listings endpoint exists!")
            print(f"📊 Admin listings returned: {len(listings)}")
            print(f"📊 Total count from admin API: {total_count}")
            
            # Analyze listing statuses
            status_counts = {}
            for listing in listings:
                status = listing.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"📈 Admin listings by status: {json.dumps(status_counts, indent=2)}")
            
            return listings, True
        elif response.status_code == 404:
            print(f"❌ Admin listings endpoint does not exist (404)")
            return [], False
        else:
            print(f"❌ Admin listings endpoint error: {response.status_code} - {response.text}")
            return [], False
            
    except Exception as e:
        print(f"❌ Error testing /api/admin/listings: {e}")
        return [], False

def test_listings_with_filters():
    """Test /api/listings with different query parameters"""
    print("\n" + "=" * 80)
    print("4. TESTING /api/listings WITH FILTERS")
    print("=" * 80)
    
    filters_to_test = [
        {"status": "active"},
        {"status": "inactive"},
        {"status": "expired"},
        {"active_only": "true"},
        {"category": "all"},
    ]
    
    results = {}
    
    for filter_params in filters_to_test:
        try:
            # Build query string
            query_string = "&".join([f"{k}={v}" for k, v in filter_params.items()])
            url = f"{BACKEND_URL}/listings?{query_string}"
            
            print(f"\n🔍 Testing filter: {filter_params}")
            print(f"URL: {url}")
            
            response = requests.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'listings' in data:
                    listings = data['listings']
                    total_count = data.get('total', len(listings))
                else:
                    listings = data if isinstance(data, list) else []
                    total_count = len(listings)
                
                print(f"✅ Filtered listings returned: {len(listings)}")
                print(f"📊 Total count: {total_count}")
                
                # Store results
                filter_key = str(filter_params)
                results[filter_key] = {
                    'count': len(listings),
                    'total': total_count,
                    'listings': listings
                }
            else:
                print(f"❌ Filter failed: {response.text}")
                results[str(filter_params)] = {'count': 0, 'total': 0, 'listings': []}
                
        except Exception as e:
            print(f"❌ Error testing filter {filter_params}: {e}")
            results[str(filter_params)] = {'count': 0, 'total': 0, 'listings': []}
    
    return results

def analyze_data_discrepancy(listings_data, browse_data, admin_data, filter_results):
    """Analyze the discrepancy between different endpoints"""
    print("\n" + "=" * 80)
    print("5. DATA DISCREPANCY ANALYSIS")
    print("=" * 80)
    
    print(f"📊 ENDPOINT COMPARISON:")
    print(f"  /api/listings: {len(listings_data)} listings")
    print(f"  /api/marketplace/browse: {len(browse_data)} listings")
    print(f"  /api/admin/listings: {len(admin_data[0]) if admin_data[1] else 'N/A'} listings")
    
    print(f"\n🔍 FILTER RESULTS:")
    for filter_name, result in filter_results.items():
        print(f"  {filter_name}: {result['count']} listings")
    
    # Check if /api/listings returns all listings including expired
    if len(listings_data) > len(browse_data):
        print(f"\n⚠️  POTENTIAL ISSUE IDENTIFIED:")
        print(f"  /api/listings returns {len(listings_data)} listings")
        print(f"  /api/marketplace/browse returns {len(browse_data)} listings")
        print(f"  This suggests /api/listings includes inactive/expired listings")
        print(f"  Admin listings management may be using /api/listings instead of filtering for active only")
    
    # Analyze status distribution
    all_statuses = set()
    for listing in listings_data:
        all_statuses.add(listing.get('status', 'unknown'))
    
    print(f"\n📈 ALL LISTING STATUSES FOUND: {list(all_statuses)}")
    
    # Check if there are expired listings
    expired_count = len([l for l in listings_data if l.get('status') == 'expired' or l.get('is_expired', False)])
    inactive_count = len([l for l in listings_data if l.get('status') == 'inactive'])
    active_count = len([l for l in listings_data if l.get('status') == 'active'])
    
    print(f"\n📊 LISTING STATUS BREAKDOWN:")
    print(f"  Active: {active_count}")
    print(f"  Inactive: {inactive_count}")
    print(f"  Expired: {expired_count}")
    print(f"  Total: {len(listings_data)}")
    
    # Root cause analysis
    print(f"\n🔍 ROOT CAUSE ANALYSIS:")
    if len(listings_data) == 4 and len(browse_data) == 0:
        print(f"  ✅ CONFIRMED: /api/listings returns 4 listings (likely expired/inactive)")
        print(f"  ✅ CONFIRMED: /api/marketplace/browse returns 0 listings (only active)")
        print(f"  🎯 ROOT CAUSE: Admin listings management is using /api/listings")
        print(f"  🎯 SOLUTION: Admin should filter for active listings only or use browse endpoint")
    elif len(listings_data) > 0 and active_count == 0:
        print(f"  ✅ CONFIRMED: All {len(listings_data)} listings are expired/inactive")
        print(f"  🎯 ROOT CAUSE: Admin shows all listings, should show only active for management")
    else:
        print(f"  ❓ UNEXPECTED: Need further investigation")

def main():
    """Main test execution"""
    print("🔍 LISTINGS MANAGEMENT DATA SOURCE INVESTIGATION")
    print("=" * 80)
    print("Investigating why listings management shows 4 when there should be 0")
    print("=" * 80)
    
    # Test all endpoints
    listings_data, listings_total = test_listings_endpoint()
    browse_data = test_browse_endpoint()
    admin_data = test_admin_listings_endpoint()
    filter_results = test_listings_with_filters()
    
    # Analyze discrepancy
    analyze_data_discrepancy(listings_data, browse_data, admin_data, filter_results)
    
    # Final summary
    print("\n" + "=" * 80)
    print("📋 INVESTIGATION SUMMARY")
    print("=" * 80)
    print(f"✅ /api/listings endpoint tested: {len(listings_data)} listings found")
    print(f"✅ /api/marketplace/browse endpoint tested: {len(browse_data)} listings found")
    print(f"✅ /api/admin/listings endpoint: {'EXISTS' if admin_data[1] else 'DOES NOT EXIST'}")
    print(f"✅ Filter testing completed: {len(filter_results)} filters tested")
    
    if len(listings_data) > len(browse_data):
        print(f"\n🎯 CONCLUSION:")
        print(f"  The listings management is likely using /api/listings which returns ALL listings")
        print(f"  including expired/inactive ones ({len(listings_data)} total).")
        print(f"  Browse page uses /api/marketplace/browse which only shows active listings ({len(browse_data)}).")
        print(f"  Admin interface should filter for active listings only.")
    
    print(f"\n✅ INVESTIGATION COMPLETED")

if __name__ == "__main__":
    main()