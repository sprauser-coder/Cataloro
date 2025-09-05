#!/usr/bin/env python3
"""
LISTINGS ENDPOINT STATUS FILTERING FIX VERIFICATION
Testing the fix for listings endpoint to default to active listings only
"""

import requests
import json
from datetime import datetime

# Use the production URL from frontend/.env
BASE_URL = "https://cataloro-upgrade.preview.emergentagent.com/api"

def test_admin_dashboard_kpi():
    """Test /api/admin/dashboard endpoint and examine how total_listings is calculated"""
    print("=" * 80)
    print("1. TESTING ADMIN DASHBOARD KPI CALCULATION")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/dashboard")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            kpis = data.get('kpis', {})
            total_listings = kpis.get('total_listings', 0)
            
            print(f"✅ Dashboard KPI - Total Listings: {total_listings}")
            print(f"📊 All KPIs: {json.dumps(kpis, indent=2)}")
            
            return total_listings, data
        else:
            print(f"❌ Failed to get dashboard data: {response.text}")
            return 0, None
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return 0, None

def test_listings_endpoint():
    """Test /api/listings endpoint to see what listings actually exist"""
    print("\n" + "=" * 80)
    print("2. TESTING LISTINGS ENDPOINT - ACTUAL LISTINGS DATA")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BACKEND_URL}/listings")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            listings = data.get('listings', [])
            total = data.get('total', 0)
            
            print(f"✅ Listings Endpoint - Total Count: {total}")
            print(f"📋 Actual Listings Returned: {len(listings)}")
            
            # Analyze listing statuses
            status_counts = {}
            for listing in listings:
                status = listing.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"📊 Listings by Status: {json.dumps(status_counts, indent=2)}")
            
            # Show first few listings for analysis
            print(f"\n📝 Sample Listings (first 3):")
            for i, listing in enumerate(listings[:3]):
                print(f"  {i+1}. ID: {listing.get('id', 'N/A')}")
                print(f"     Title: {listing.get('title', 'N/A')}")
                print(f"     Status: {listing.get('status', 'N/A')}")
                print(f"     Created: {listing.get('created_at', 'N/A')}")
                print()
            
            return total, listings, status_counts
        else:
            print(f"❌ Failed to get listings: {response.text}")
            return 0, [], {}
            
    except Exception as e:
        print(f"❌ Error testing listings: {e}")
        return 0, [], {}

def test_browse_endpoint():
    """Test /api/marketplace/browse endpoint used by frontend"""
    print("\n" + "=" * 80)
    print("3. TESTING BROWSE ENDPOINT - FRONTEND LISTINGS DATA")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BACKEND_URL}/marketplace/browse")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            listings = response.json()
            
            print(f"✅ Browse Endpoint - Listings Count: {len(listings)}")
            
            # Analyze listing statuses
            status_counts = {}
            for listing in listings:
                status = listing.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"📊 Browse Listings by Status: {json.dumps(status_counts, indent=2)}")
            
            return len(listings), listings, status_counts
        else:
            print(f"❌ Failed to get browse listings: {response.text}")
            return 0, [], {}
            
    except Exception as e:
        print(f"❌ Error testing browse: {e}")
        return 0, [], {}

def test_admin_listings_management():
    """Test potential admin listings management endpoints"""
    print("\n" + "=" * 80)
    print("4. TESTING ADMIN LISTINGS MANAGEMENT ENDPOINTS")
    print("=" * 80)
    
    # Try various potential admin listing endpoints
    endpoints_to_test = [
        "/admin/listings",
        "/admin/listings/active",
        "/admin/listings/pending", 
        "/admin/listings/inactive",
        "/admin/listings/sold",
        "/admin/manage/listings"
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
            print(f"Testing {endpoint}: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict) and 'listings' in data:
                    count = len(data['listings'])
                elif isinstance(data, dict) and 'total' in data:
                    count = data['total']
                else:
                    count = "Unknown format"
                
                print(f"  ✅ Success - Count: {count}")
                results[endpoint] = {'status': 200, 'count': count, 'data': data}
            else:
                print(f"  ❌ Failed - {response.status_code}")
                results[endpoint] = {'status': response.status_code, 'error': response.text}
                
        except Exception as e:
            print(f"  ❌ Error testing {endpoint}: {e}")
            results[endpoint] = {'error': str(e)}
    
    return results

def analyze_database_query_differences(dashboard_total, listings_total, browse_total):
    """Analyze the differences between the three data sources"""
    print("\n" + "=" * 80)
    print("5. ROOT CAUSE ANALYSIS - DATABASE QUERY COMPARISON")
    print("=" * 80)
    
    print(f"📊 COMPARISON RESULTS:")
    print(f"  Dashboard KPI Total Listings: {dashboard_total}")
    print(f"  /api/listings Total:          {listings_total}")
    print(f"  /api/marketplace/browse:      {browse_total}")
    
    print(f"\n🔍 DISCREPANCY ANALYSIS:")
    
    if dashboard_total == listings_total == browse_total:
        print("  ✅ All endpoints return the same count - NO DISCREPANCY")
        return "no_discrepancy"
    
    elif dashboard_total != listings_total:
        print(f"  ❌ CRITICAL: Dashboard ({dashboard_total}) vs Listings ({listings_total}) mismatch!")
        print(f"     Difference: {abs(dashboard_total - listings_total)}")
        
    elif dashboard_total != browse_total:
        print(f"  ⚠️  Dashboard ({dashboard_total}) vs Browse ({browse_total}) mismatch!")
        print(f"     Difference: {abs(dashboard_total - browse_total)}")
        
    if browse_total != listings_total:
        print(f"  ⚠️  Browse ({browse_total}) vs Listings ({listings_total}) mismatch!")
        print(f"     Difference: {abs(browse_total - listings_total)}")
    
    print(f"\n🔎 LIKELY CAUSES:")
    print(f"  1. Dashboard uses: db.listings.count_documents({{}})")
    print(f"  2. Browse uses: db.listings.find({{\"status\": \"active\"}})")
    print(f"  3. Admin listings may use different filtering")
    
    if dashboard_total > browse_total:
        print(f"  💡 Dashboard counts ALL listings, Browse only shows ACTIVE")
        print(f"     Inactive/Sold listings: {dashboard_total - browse_total}")
    
    return "discrepancy_found"

def investigate_listing_statuses():
    """Deep dive into listing statuses to understand the data"""
    print("\n" + "=" * 80)
    print("6. DEEP DIVE - LISTING STATUS INVESTIGATION")
    print("=" * 80)
    
    try:
        # Get all listings without filters
        response = requests.get(f"{BACKEND_URL}/listings?limit=100")
        
        if response.status_code == 200:
            data = response.json()
            all_listings = data.get('listings', [])
            
            print(f"📋 DETAILED LISTING ANALYSIS ({len(all_listings)} total):")
            
            # Detailed status breakdown
            status_details = {}
            for listing in all_listings:
                status = listing.get('status', 'unknown')
                if status not in status_details:
                    status_details[status] = []
                
                status_details[status].append({
                    'id': listing.get('id', 'N/A')[:8] + '...',
                    'title': listing.get('title', 'N/A')[:30] + '...',
                    'created_at': listing.get('created_at', 'N/A')
                })
            
            for status, listings in status_details.items():
                print(f"\n  📊 {status.upper()} LISTINGS: {len(listings)}")
                for i, listing in enumerate(listings[:3]):  # Show first 3
                    print(f"    {i+1}. {listing['id']} - {listing['title']}")
                if len(listings) > 3:
                    print(f"    ... and {len(listings) - 3} more")
            
            return status_details
        else:
            print(f"❌ Failed to get detailed listings: {response.text}")
            return {}
            
    except Exception as e:
        print(f"❌ Error investigating statuses: {e}")
        return {}

def main():
    """Main investigation function"""
    print("🔍 ADMIN DASHBOARD LISTINGS COUNT DISCREPANCY INVESTIGATION")
    print("=" * 80)
    print("Issue: KPI shows '4 TOTAL LISTINGS' but Listings management shows '0 results'")
    print("=" * 80)
    
    # Test all endpoints
    dashboard_total, dashboard_data = test_admin_dashboard_kpi()
    listings_total, listings_data, listings_status = test_listings_endpoint()
    browse_total, browse_data, browse_status = test_browse_endpoint()
    admin_results = test_admin_listings_management()
    
    # Analyze differences
    analysis_result = analyze_database_query_differences(dashboard_total, listings_total, browse_total)
    
    # Deep dive into statuses
    status_details = investigate_listing_statuses()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 INVESTIGATION SUMMARY")
    print("=" * 80)
    
    print(f"✅ Dashboard KPI Total Listings: {dashboard_total}")
    print(f"✅ /api/listings Total: {listings_total}")
    print(f"✅ /api/marketplace/browse: {browse_total}")
    
    if dashboard_total == 4 and browse_total == 0:
        print(f"\n❌ CONFIRMED BUG: Dashboard shows 4 but browse shows 0!")
        print(f"🔍 ROOT CAUSE: Dashboard counts ALL listings, browse only shows ACTIVE")
        print(f"💡 SOLUTION: Check if all 4 listings have status != 'active'")
    elif dashboard_total != 4:
        print(f"\n⚠️  Dashboard doesn't show 4 listings as reported (shows {dashboard_total})")
    
    # Check for admin listings endpoints
    working_admin_endpoints = [ep for ep, result in admin_results.items() if result.get('status') == 200]
    if working_admin_endpoints:
        print(f"\n✅ Found working admin endpoints: {working_admin_endpoints}")
    else:
        print(f"\n❌ No admin listings management endpoints found!")
        print(f"💡 This could be why listings management shows '0 results'")
    
    print(f"\n📊 Status Distribution:")
    for status, count in listings_status.items():
        print(f"  {status}: {count}")
    
    return {
        'dashboard_total': dashboard_total,
        'listings_total': listings_total,
        'browse_total': browse_total,
        'admin_endpoints': admin_results,
        'status_distribution': listings_status,
        'bug_confirmed': dashboard_total == 4 and browse_total == 0
    }

if __name__ == "__main__":
    results = main()
    
    # Exit with appropriate code
    if results['bug_confirmed']:
        print(f"\n🚨 BUG CONFIRMED: Dashboard/Browse discrepancy found!")
        sys.exit(1)
    else:
        print(f"\n✅ Investigation completed successfully")
        sys.exit(0)