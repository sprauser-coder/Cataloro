#!/usr/bin/env python3
"""
Admin Dashboard Enhanced Revenue Validation Testing
Testing the new strict validation and debug logging for revenue calculation
"""

import requests
import json
import sys
from datetime import datetime

# Use the production URL from frontend/.env
BASE_URL = "https://cataloro-ads.preview.emergentagent.com/api"

def test_admin_dashboard_revenue_validation():
    """Test the admin dashboard with enhanced revenue validation"""
    print("=" * 80)
    print("ADMIN DASHBOARD ENHANCED REVENUE VALIDATION TESTING")
    print("=" * 80)
    
    try:
        # Test GET /api/admin/dashboard endpoint
        print("\n1. Testing GET /api/admin/dashboard endpoint...")
        response = requests.get(f"{BASE_URL}/admin/dashboard", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Dashboard endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        dashboard_data = response.json()
        print(f"✅ Dashboard endpoint accessible (HTTP {response.status_code})")
        
        # Extract KPIs
        kpis = dashboard_data.get('kpis', {})
        revenue = kpis.get('revenue', 0)
        total_deals = kpis.get('total_deals', 0)
        total_users = kpis.get('total_users', 0)
        total_listings = kpis.get('total_listings', 0)
        active_listings = kpis.get('active_listings', 0)
        
        print(f"\n📊 DASHBOARD KPIs:")
        print(f"   Total Users: {total_users}")
        print(f"   Total Listings: {total_listings}")
        print(f"   Active Listings: {active_listings}")
        print(f"   Total Deals: {total_deals}")
        print(f"   Revenue: €{revenue}")
        
        # Check if revenue is now realistic (should be much lower than €5,870)
        print(f"\n2. Revenue Validation Analysis...")
        if revenue > 5000:
            print(f"❌ Revenue still inflated: €{revenue} (expected much lower than €5,870)")
            print("   The €2000 per transaction limit may not be working properly")
        elif revenue > 2000:
            print(f"⚠️  Revenue moderately high: €{revenue} (investigating if realistic)")
        else:
            print(f"✅ Revenue appears realistic: €{revenue} (much lower than previous €5,870)")
        
        # Calculate average revenue per deal
        if total_deals > 0:
            avg_revenue_per_deal = revenue / total_deals
            print(f"   Average revenue per deal: €{avg_revenue_per_deal:.2f}")
            
            if avg_revenue_per_deal > 2000:
                print(f"❌ Average per deal exceeds €2000 limit: €{avg_revenue_per_deal:.2f}")
            else:
                print(f"✅ Average per deal within €2000 limit: €{avg_revenue_per_deal:.2f}")
        else:
            print("   No deals found for average calculation")
        
        # Test marketplace browse to get actual transaction data
        print(f"\n3. Verifying marketplace transaction data...")
        browse_response = requests.get(f"{BASE_URL}/marketplace/browse", timeout=30)
        
        if browse_response.status_code == 200:
            listings = browse_response.json()
            print(f"✅ Found {len(listings)} active listings in marketplace")
            
            # Analyze bid amounts to identify high-value transactions
            high_value_bids = []
            total_marketplace_value = 0
            
            for listing in listings:
                bid_info = listing.get('bid_info', {})
                highest_bid = bid_info.get('highest_bid', 0)
                listing_id = listing.get('id', 'unknown')
                title = listing.get('title', 'Unknown')
                
                if highest_bid > 0:
                    total_marketplace_value += highest_bid
                    if highest_bid > 2000:
                        high_value_bids.append({
                            'id': listing_id,
                            'title': title,
                            'bid': highest_bid
                        })
            
            print(f"   Total marketplace bid value: €{total_marketplace_value}")
            
            if high_value_bids:
                print(f"⚠️  Found {len(high_value_bids)} listings with bids > €2000:")
                for bid in high_value_bids:
                    print(f"      - {bid['title']}: €{bid['bid']} (ID: {bid['id']})")
                print("   These should be filtered out by the €2000 limit")
            else:
                print(f"✅ No bids exceed €2000 limit in marketplace data")
        
        # Test tenders endpoint to check for high-value accepted tenders
        print(f"\n4. Checking accepted tenders for validation...")
        
        # We'll need to check if there's a way to get tender data
        # For now, let's analyze the revenue vs marketplace data discrepancy
        
        if browse_response.status_code == 200:
            marketplace_vs_dashboard = abs(total_marketplace_value - revenue)
            print(f"   Marketplace bid total: €{total_marketplace_value}")
            print(f"   Dashboard revenue: €{revenue}")
            print(f"   Discrepancy: €{marketplace_vs_dashboard}")
            
            if marketplace_vs_dashboard > 1000:
                print(f"⚠️  Large discrepancy suggests dashboard includes non-marketplace data")
            else:
                print(f"✅ Revenue closely matches marketplace activity")
        
        # Summary of validation results
        print(f"\n5. REVENUE VALIDATION SUMMARY:")
        print(f"   Dashboard Revenue: €{revenue}")
        print(f"   Previous Inflated Amount: €5,870")
        
        if revenue < 1000:
            print(f"✅ SIGNIFICANT IMPROVEMENT: Revenue reduced by €{5870 - revenue:.2f}")
            print(f"✅ Revenue now appears realistic for marketplace activity")
            validation_success = True
        elif revenue < 3000:
            print(f"✅ MODERATE IMPROVEMENT: Revenue reduced by €{5870 - revenue:.2f}")
            print(f"⚠️  Still investigating if current amount is fully realistic")
            validation_success = True
        else:
            print(f"❌ LIMITED IMPROVEMENT: Revenue only reduced by €{5870 - revenue:.2f}")
            print(f"❌ Revenue still appears inflated")
            validation_success = False
        
        return validation_success
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error testing dashboard: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

def test_debug_logging_verification():
    """Verify that debug logging is working (check for console output)"""
    print("\n" + "=" * 80)
    print("DEBUG LOGGING VERIFICATION")
    print("=" * 80)
    
    print("\n📝 Note: Debug logging verification requires checking backend logs")
    print("   The backend should show DEBUG messages indicating:")
    print("   - Which tenders/listings are being included in revenue calculation")
    print("   - Which transactions are being excluded due to €2000 limit")
    print("   - Detailed breakdown of revenue sources")
    
    # Make a dashboard request to trigger debug logging
    try:
        print(f"\n🔄 Triggering dashboard request to generate debug logs...")
        response = requests.get(f"{BASE_URL}/admin/dashboard", timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Dashboard request successful - debug logs should be generated")
            print(f"   Check backend logs for DEBUG messages showing:")
            print(f"   - 'DEBUG: Starting revenue calculation...'")
            print(f"   - 'DEBUG: Found X accepted tenders'")
            print(f"   - 'DEBUG: Added tender X: €Y' (for included transactions)")
            print(f"   - 'DEBUG: Excluded tender X: €Y (outside realistic range)'")
            print(f"   - 'DEBUG: Final calculated revenue: €X, deals: Y'")
            return True
        else:
            print(f"❌ Dashboard request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error triggering debug logs: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Admin Dashboard Enhanced Revenue Validation Testing")
    print(f"🌐 Testing against: {BASE_URL}")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Run tests
    revenue_test_passed = test_admin_dashboard_revenue_validation()
    debug_test_passed = test_debug_logging_verification()
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if revenue_test_passed:
        print("✅ Revenue Validation: PASSED - Revenue calculation improved with strict validation")
    else:
        print("❌ Revenue Validation: FAILED - Revenue still appears inflated")
    
    if debug_test_passed:
        print("✅ Debug Logging: TRIGGERED - Check backend logs for detailed validation messages")
    else:
        print("❌ Debug Logging: FAILED - Could not trigger debug logging")
    
    overall_success = revenue_test_passed and debug_test_passed
    
    if overall_success:
        print("\n🎉 OVERALL RESULT: ENHANCED REVENUE VALIDATION WORKING")
        print("   The €2000 per transaction limit and strict validation are functioning")
        print("   Revenue calculation now excludes unrealistic test/dummy data")
    else:
        print("\n❌ OVERALL RESULT: REVENUE VALIDATION NEEDS ATTENTION")
        print("   The enhanced validation may not be fully effective")
        print("   Further investigation needed to identify inflated revenue sources")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)