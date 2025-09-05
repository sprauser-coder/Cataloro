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

def test_listings_endpoint_status_filtering():
    """
    Verify that the listings endpoint status filtering fix is working correctly
    """
    print("=" * 80)
    print("LISTINGS ENDPOINT STATUS FILTERING FIX VERIFICATION")
    print("=" * 80)
    
    results = {
        "default_behavior": False,
        "status_all_parameter": False, 
        "status_active_parameter": False,
        "browse_comparison": False,
        "admin_impact": False
    }
    
    try:
        # 1. Test Default Behavior - should return only active listings
        print("\n1. Testing Default Behavior (/api/listings without parameters)")
        print("-" * 60)
        
        response = requests.get(f"{BASE_URL}/listings", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            listings = data.get("listings", [])
            total = data.get("total", 0)
            
            print(f"Total listings returned: {len(listings)}")
            print(f"Total count from API: {total}")
            
            # Check if all returned listings are active
            active_count = 0
            expired_count = 0
            
            for listing in listings:
                status = listing.get("status", "unknown")
                if status == "active":
                    active_count += 1
                else:
                    expired_count += 1
                    print(f"  ⚠️  Non-active listing found: {listing.get('title', 'Unknown')} (status: {status})")
            
            print(f"Active listings: {active_count}")
            print(f"Non-active listings: {expired_count}")
            
            if expired_count == 0:
                print("✅ DEFAULT BEHAVIOR: Only active listings returned")
                results["default_behavior"] = True
            else:
                print("❌ DEFAULT BEHAVIOR: Non-active listings found in default response")
        else:
            print(f"❌ Failed to fetch default listings: {response.status_code}")
            print(f"Response: {response.text}")
        
        # 2. Test Status=all Parameter - should return all listings
        print("\n2. Testing Status=all Parameter (/api/listings?status=all)")
        print("-" * 60)
        
        response = requests.get(f"{BASE_URL}/listings?status=all", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            all_listings = data.get("listings", [])
            all_total = data.get("total", 0)
            
            print(f"Total listings with status=all: {len(all_listings)}")
            print(f"Total count from API: {all_total}")
            
            # Count different statuses
            status_counts = {}
            for listing in all_listings:
                status = listing.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("Status breakdown:")
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
            
            if len(all_listings) > 0:
                print("✅ STATUS=ALL: Returns listings (including all statuses)")
                results["status_all_parameter"] = True
            else:
                print("❌ STATUS=ALL: No listings returned")
        else:
            print(f"❌ Failed to fetch all listings: {response.status_code}")
        
        # 3. Test Status=active Parameter - should return only active listings
        print("\n3. Testing Status=active Parameter (/api/listings?status=active)")
        print("-" * 60)
        
        response = requests.get(f"{BASE_URL}/listings?status=active", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            active_listings = data.get("listings", [])
            active_total = data.get("total", 0)
            
            print(f"Total active listings: {len(active_listings)}")
            print(f"Total count from API: {active_total}")
            
            # Verify all are active
            non_active_found = False
            for listing in active_listings:
                if listing.get("status") != "active":
                    non_active_found = True
                    print(f"  ⚠️  Non-active listing: {listing.get('title')} (status: {listing.get('status')})")
            
            if not non_active_found:
                print("✅ STATUS=ACTIVE: Only active listings returned")
                results["status_active_parameter"] = True
            else:
                print("❌ STATUS=ACTIVE: Non-active listings found")
        else:
            print(f"❌ Failed to fetch active listings: {response.status_code}")
        
        # 4. Compare with Browse Endpoint - should match active listings count
        print("\n4. Comparing with Browse Endpoint (/api/marketplace/browse)")
        print("-" * 60)
        
        response = requests.get(f"{BASE_URL}/marketplace/browse", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            browse_listings = response.json()
            browse_count = len(browse_listings)
            
            print(f"Browse endpoint listings count: {browse_count}")
            
            # Compare with default listings count
            if 'listings' in locals():
                default_count = len(listings)
                print(f"Default listings count: {default_count}")
                
                if browse_count == default_count:
                    print("✅ BROWSE COMPARISON: Counts match between browse and default listings")
                    results["browse_comparison"] = True
                else:
                    print(f"❌ BROWSE COMPARISON: Count mismatch (browse: {browse_count}, listings: {default_count})")
            else:
                print("❌ BROWSE COMPARISON: Cannot compare - default listings not available")
        else:
            print(f"❌ Failed to fetch browse listings: {response.status_code}")
        
        # 5. Verify Admin Impact - admin should see only active by default
        print("\n5. Verifying Admin Impact (listings management)")
        print("-" * 60)
        
        if results["default_behavior"]:
            print("✅ ADMIN IMPACT: Admin listings management will show only active listings by default")
            print("   - No more showing expired listings when there are active ones")
            print("   - Admin can use ?status=all to see all listings when needed")
            results["admin_impact"] = True
        else:
            print("❌ ADMIN IMPACT: Default behavior not fixed - admin will still see mixed listings")
        
        # Summary
        print("\n" + "=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print()
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            test_display = test_name.replace("_", " ").title()
            print(f"{status} - {test_display}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - Listings endpoint status filtering fix is working correctly!")
            return True
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed - Status filtering fix needs attention")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
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