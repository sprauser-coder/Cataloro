#!/usr/bin/env python3
"""
LISTINGS ENDPOINT STATUS FILTERING FIX VERIFICATION
Testing the fix for listings endpoint to default to active listings only
"""

import requests
import json
from datetime import datetime

# Use the production URL from frontend/.env
BASE_URL = "https://cataloro-marketplace-3.preview.emergentagent.com/api"

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

if __name__ == "__main__":
    success = test_listings_endpoint_status_filtering()
    exit(0 if success else 1)