#!/usr/bin/env python3
"""
ADMIN DASHBOARD LISTINGS COUNT FIX VERIFICATION
Testing the fix for the discrepancy where dashboard showed 4 total listings vs management showing 0
Expected: Dashboard total_listings should now show 0 (matching active listings count)
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-upgrade.preview.emergentagent.com/api"

def test_dashboard_kpi_after_fix():
    """Test /api/admin/dashboard endpoint to verify the listings count fix"""
    print("=" * 80)
    print("1. TESTING ADMIN DASHBOARD KPI AFTER FIX")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/dashboard")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            kpis = data.get('kpis', {})
            total_listings = kpis.get('total_listings', 0)
            active_listings = kpis.get('active_listings', 0)
            
            print(f"✅ Dashboard KPI - Total Listings: {total_listings}")
            print(f"✅ Dashboard KPI - Active Listings: {active_listings}")
            print(f"📊 All KPIs: {json.dumps(kpis, indent=2)}")
            
            # Check if the fix worked
            if total_listings == active_listings:
                print(f"✅ SUCCESS: total_listings ({total_listings}) matches active_listings ({active_listings})")
                consistency_check = "PASSED"
            else:
                print(f"❌ ISSUE: total_listings ({total_listings}) != active_listings ({active_listings})")
                consistency_check = "FAILED"
            
            return total_listings, active_listings, consistency_check, data
        else:
            print(f"❌ Failed to get dashboard data: {response.text}")
            return 0, 0, "ERROR", None
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return 0, 0, "ERROR", None

def verify_listings_database_state():
    """Verify the current state of listings in the database"""
    print("\n" + "=" * 80)
    print("2. VERIFYING CURRENT LISTINGS DATABASE STATE")
    print("=" * 80)
    
    try:
        # Get all listings to see total count
        response = requests.get(f"{BACKEND_URL}/listings?limit=100")
        print(f"All Listings Endpoint Status: {response.status_code}")
        
        total_in_db = 0
        active_in_db = 0
        status_breakdown = {}
        
        if response.status_code == 200:
            data = response.json()
            all_listings = data.get('listings', [])
            total_in_db = len(all_listings)
            
            # Count by status
            for listing in all_listings:
                status = listing.get('status', 'unknown')
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
                if status == 'active':
                    active_in_db += 1
            
            print(f"📊 Total listings in database: {total_in_db}")
            print(f"📊 Active listings in database: {active_in_db}")
            print(f"📊 Status breakdown: {json.dumps(status_breakdown, indent=2)}")
        
        # Also check browse endpoint (what users see)
        browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse")
        browse_count = 0
        if browse_response.status_code == 200:
            browse_listings = browse_response.json()
            browse_count = len(browse_listings)
            print(f"📊 Browse endpoint shows: {browse_count} listings")
        
        return {
            'total_in_db': total_in_db,
            'active_in_db': active_in_db,
            'browse_count': browse_count,
            'status_breakdown': status_breakdown
        }
        
    except Exception as e:
        print(f"❌ Error verifying database state: {e}")
        return {'error': str(e)}

def test_data_consistency():
    """Test that the fix resolves the previous discrepancy"""
    print("\n" + "=" * 80)
    print("3. TESTING DATA CONSISTENCY AFTER FIX")
    print("=" * 80)
    
    # Get dashboard data
    dashboard_total, dashboard_active, consistency, _ = test_dashboard_kpi_after_fix()
    
    # Get database state
    db_state = verify_listings_database_state()
    
    print(f"\n🔍 CONSISTENCY ANALYSIS:")
    print(f"  Dashboard total_listings: {dashboard_total}")
    print(f"  Dashboard active_listings: {dashboard_active}")
    print(f"  Database active listings: {db_state.get('active_in_db', 'ERROR')}")
    print(f"  Browse endpoint count: {db_state.get('browse_count', 'ERROR')}")
    
    # Check if all sources are consistent
    expected_active = db_state.get('active_in_db', 0)
    browse_count = db_state.get('browse_count', 0)
    
    consistency_results = []
    
    if dashboard_total == expected_active:
        print(f"  ✅ Dashboard total_listings matches database active count")
        consistency_results.append("dashboard_total_correct")
    else:
        print(f"  ❌ Dashboard total_listings ({dashboard_total}) != database active ({expected_active})")
        consistency_results.append("dashboard_total_incorrect")
    
    if dashboard_active == expected_active:
        print(f"  ✅ Dashboard active_listings matches database active count")
        consistency_results.append("dashboard_active_correct")
    else:
        print(f"  ❌ Dashboard active_listings ({dashboard_active}) != database active ({expected_active})")
        consistency_results.append("dashboard_active_incorrect")
    
    if browse_count == expected_active:
        print(f"  ✅ Browse endpoint matches database active count")
        consistency_results.append("browse_correct")
    else:
        print(f"  ❌ Browse endpoint ({browse_count}) != database active ({expected_active})")
        consistency_results.append("browse_incorrect")
    
    # Overall consistency check
    all_consistent = (dashboard_total == dashboard_active == expected_active == browse_count)
    
    if all_consistent:
        print(f"\n✅ PERFECT CONSISTENCY: All sources show {expected_active} active listings")
        return "CONSISTENT"
    else:
        print(f"\n❌ INCONSISTENCY DETECTED: Sources show different counts")
        return "INCONSISTENT"

def test_edge_cases():
    """Test edge cases to ensure the fix works correctly"""
    print("\n" + "=" * 80)
    print("4. TESTING EDGE CASES")
    print("=" * 80)
    
    # Check what happens when there are no active listings
    db_state = verify_listings_database_state()
    active_count = db_state.get('active_in_db', 0)
    total_count = db_state.get('total_in_db', 0)
    
    print(f"📊 Current state: {active_count} active out of {total_count} total listings")
    
    if active_count == 0:
        print(f"✅ EDGE CASE: Zero active listings - Perfect test scenario")
        print(f"   Dashboard should show 0 for both total_listings and active_listings")
    elif active_count > 0:
        print(f"✅ NORMAL CASE: {active_count} active listings found")
        print(f"   Dashboard should show {active_count} for both total_listings and active_listings")
    
    # Check if there are expired/inactive listings
    status_breakdown = db_state.get('status_breakdown', {})
    inactive_statuses = {k: v for k, v in status_breakdown.items() if k != 'active'}
    
    if inactive_statuses:
        print(f"📊 Inactive/expired listings found: {json.dumps(inactive_statuses, indent=2)}")
        print(f"   These should be excluded from dashboard total_listings count")
    else:
        print(f"📊 No inactive listings found - all listings are active")
    
    return {
        'active_count': active_count,
        'total_count': total_count,
        'inactive_statuses': inactive_statuses
    }

def verify_frontend_impact():
    """Verify that the fix will resolve the frontend discrepancy"""
    print("\n" + "=" * 80)
    print("5. VERIFYING FRONTEND IMPACT")
    print("=" * 80)
    
    # Get the current dashboard data that frontend would receive
    dashboard_total, dashboard_active, consistency, dashboard_data = test_dashboard_kpi_after_fix()
    
    # Get the browse data that listings management would show
    try:
        browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse")
        if browse_response.status_code == 200:
            browse_listings = browse_response.json()
            browse_count = len(browse_listings)
            
            print(f"📱 Frontend Dashboard KPI will show: {dashboard_total} total listings")
            print(f"📱 Frontend Listings Management will show: {browse_count} results")
            
            if dashboard_total == browse_count:
                print(f"✅ SUCCESS: Frontend will show consistent numbers ({dashboard_total})")
                print(f"   No more confusing discrepancy for users!")
                return "CONSISTENT"
            else:
                print(f"❌ ISSUE: Frontend will still show discrepancy!")
                print(f"   Dashboard: {dashboard_total}, Management: {browse_count}")
                return "INCONSISTENT"
        else:
            print(f"❌ Failed to get browse data: {browse_response.text}")
            return "ERROR"
            
    except Exception as e:
        print(f"❌ Error verifying frontend impact: {e}")
        return "ERROR"

def main():
    """Main verification function"""
    print("🔍 ADMIN DASHBOARD LISTINGS COUNT FIX VERIFICATION")
    print("=" * 80)
    print("Expected: Dashboard total_listings should now show 0 (matching active listings)")
    print("Previous Issue: Dashboard showed 4 total listings, management showed 0")
    print("=" * 80)
    
    # Run all verification tests
    dashboard_total, dashboard_active, consistency_check, dashboard_data = test_dashboard_kpi_after_fix()
    db_state = verify_listings_database_state()
    consistency_result = test_data_consistency()
    edge_case_result = test_edge_cases()
    frontend_impact = verify_frontend_impact()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 FIX VERIFICATION SUMMARY")
    print("=" * 80)
    
    print(f"✅ Dashboard total_listings: {dashboard_total}")
    print(f"✅ Dashboard active_listings: {dashboard_active}")
    print(f"✅ Database active listings: {db_state.get('active_in_db', 'ERROR')}")
    print(f"✅ Browse endpoint count: {db_state.get('browse_count', 'ERROR')}")
    
    # Determine if fix is working
    fix_working = (
        consistency_check == "PASSED" and
        consistency_result == "CONSISTENT" and
        frontend_impact == "CONSISTENT"
    )
    
    if fix_working:
        print(f"\n🎉 FIX VERIFICATION: SUCCESS!")
        print(f"   ✅ Dashboard total_listings now matches active_listings")
        print(f"   ✅ All data sources are consistent")
        print(f"   ✅ Frontend will show consistent numbers")
        print(f"   ✅ Listings count discrepancy bug is RESOLVED")
    else:
        print(f"\n❌ FIX VERIFICATION: ISSUES FOUND!")
        if consistency_check != "PASSED":
            print(f"   ❌ Dashboard total_listings != active_listings")
        if consistency_result != "CONSISTENT":
            print(f"   ❌ Data sources are inconsistent")
        if frontend_impact != "CONSISTENT":
            print(f"   ❌ Frontend will still show discrepancy")
    
    # Show the expected vs actual results
    expected_total = db_state.get('active_in_db', 0)
    print(f"\n📊 EXPECTED RESULTS:")
    print(f"   Dashboard total_listings: {expected_total} (matches active listings)")
    print(f"   Dashboard active_listings: {expected_total}")
    print(f"   Listings management display: {expected_total} results")
    print(f"   Consistency: ACHIEVED")
    
    print(f"\n📊 ACTUAL RESULTS:")
    print(f"   Dashboard total_listings: {dashboard_total}")
    print(f"   Dashboard active_listings: {dashboard_active}")
    print(f"   Listings management display: {db_state.get('browse_count', 'ERROR')} results")
    print(f"   Consistency: {'ACHIEVED' if fix_working else 'NOT ACHIEVED'}")
    
    return {
        'fix_working': fix_working,
        'dashboard_total': dashboard_total,
        'dashboard_active': dashboard_active,
        'database_active': db_state.get('active_in_db', 0),
        'browse_count': db_state.get('browse_count', 0),
        'consistency_check': consistency_check,
        'consistency_result': consistency_result,
        'frontend_impact': frontend_impact
    }

if __name__ == "__main__":
    results = main()
    
    # Exit with appropriate code
    if results['fix_working']:
        print(f"\n✅ ADMIN DASHBOARD LISTINGS COUNT FIX VERIFICATION: PASSED")
        sys.exit(0)
    else:
        print(f"\n❌ ADMIN DASHBOARD LISTINGS COUNT FIX VERIFICATION: FAILED")
        sys.exit(1)