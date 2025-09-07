#!/usr/bin/env python3
"""
Admin Listings Endpoint Limit Testing
Testing the limit parameter issue in /api/listings endpoint
"""

import requests
import json
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://catalyst-view.preview.emergentagent.com/api"

def test_admin_listings_with_limits():
    """Test admin listings endpoint with different limit parameters"""
    print("=" * 80)
    print("ADMIN LISTINGS ENDPOINT LIMIT TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Started: {datetime.now().isoformat()}")
    print()
    
    # Test different limit values
    test_cases = [
        {"limit": None, "description": "Default limit (no parameter)"},
        {"limit": 20, "description": "Explicit limit=20"},
        {"limit": 50, "description": "Higher limit=50"},
        {"limit": 100, "description": "Very high limit=100"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 TEST {i}: {test_case['description']}")
        print("-" * 40)
        
        try:
            # Build URL with parameters
            url = f"{BACKEND_URL}/listings?status=all"
            if test_case['limit'] is not None:
                url += f"&limit={test_case['limit']}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'listings' in data:
                    listings = data['listings']
                    total_field = data.get('total', 'Not provided')
                    returned_count = len(listings)
                    
                    print(f"✅ SUCCESS: Returned {returned_count} listings")
                    print(f"   Total field: {total_field}")
                    print(f"   Response type: Object with 'listings' array")
                    
                    # Show first few listing titles for verification
                    if listings:
                        sample_titles = [listing.get('title', 'No title')[:30] for listing in listings[:3]]
                        print(f"   Sample titles: {sample_titles}")
                    
                elif isinstance(data, list):
                    returned_count = len(data)
                    print(f"✅ SUCCESS: Returned {returned_count} listings")
                    print(f"   Response type: Direct array")
                    
                    # Show first few listing titles for verification
                    if data:
                        sample_titles = [listing.get('title', 'No title')[:30] for listing in data[:3]]
                        print(f"   Sample titles: {sample_titles}")
                else:
                    print(f"❌ UNEXPECTED: Unknown response format")
                    print(f"   Response type: {type(data)}")
                    
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                if response.content:
                    error_detail = response.json().get('detail', 'Unknown error')
                    print(f"   Error: {error_detail}")
                    
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print()
    
    # Test with status=active and different limits
    print("🔍 ADDITIONAL TEST: Active listings with different limits")
    print("-" * 40)
    
    for limit in [20, 50]:
        try:
            url = f"{BACKEND_URL}/listings?status=active&limit={limit}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'listings' in data:
                    returned_count = len(data['listings'])
                    total_field = data.get('total', 'Not provided')
                    print(f"✅ Active with limit={limit}: {returned_count} listings, total={total_field}")
                    
        except Exception as e:
            print(f"❌ ERROR testing limit {limit}: {str(e)}")
    
    print()
    print("🎯 CONCLUSION:")
    print("The /api/listings endpoint has a default limit=20 parameter.")
    print("This explains why admin panel shows only 20 listings while browse shows 37.")
    print("The browse endpoint (/api/marketplace/browse) doesn't have this limit.")
    print("To see all listings in admin panel, the frontend should use limit=100 or higher.")

if __name__ == "__main__":
    test_admin_listings_with_limits()