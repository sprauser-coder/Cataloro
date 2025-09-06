#!/usr/bin/env python3
"""
Cataloro Marketplace - Browse Listings Response Format Test
Tests the exact response structure of browse listings endpoints
"""

import requests
import json
import sys
from datetime import datetime

class ListingsResponseTester:
    def __init__(self, base_url="https://browse-ads.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_endpoint(self, name, endpoint):
        """Test an endpoint and show exact response structure"""
        url = f"{self.base_url}/{endpoint}"
        print(f"\n🔍 Testing {name}")
        print(f"   URL: {url}")
        print("-" * 50)
        
        try:
            response = self.session.get(url)
            print(f"   Status Code: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response Type: {type(data).__name__}")
                    
                    if isinstance(data, list):
                        print(f"   ✅ RESPONSE IS AN ARRAY")
                        print(f"   Array Length: {len(data)}")
                        if data:
                            print(f"   First Item Type: {type(data[0]).__name__}")
                            print(f"   First Item Keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                    elif isinstance(data, dict):
                        print(f"   ❌ RESPONSE IS AN OBJECT (NOT ARRAY)")
                        print(f"   Object Keys: {list(data.keys())}")
                        if 'listings' in data:
                            print(f"   Contains 'listings' key: {type(data['listings']).__name__}")
                            if isinstance(data['listings'], list):
                                print(f"   Listings Array Length: {len(data['listings'])}")
                    else:
                        print(f"   ⚠️  UNEXPECTED RESPONSE TYPE: {type(data).__name__}")
                    
                    # Show full response structure (truncated for readability)
                    response_str = json.dumps(data, indent=2, default=str)
                    if len(response_str) > 1000:
                        print(f"   Response Preview (first 1000 chars):")
                        print(response_str[:1000] + "...")
                    else:
                        print(f"   Full Response:")
                        print(response_str)
                        
                    return True, data
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON Decode Error: {e}")
                    print(f"   Raw Response: {response.text[:500]}")
                    return False, None
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Request Error: {e}")
            return False, None

    def test_marketplace_service_compatibility(self, browse_response, listings_response):
        """Test what format the frontend marketplaceService expects"""
        print(f"\n🔧 Frontend Compatibility Analysis")
        print("-" * 50)
        
        print("Frontend expects: apiListings.map() - meaning apiListings should be an array")
        
        if browse_response is not None:
            if isinstance(browse_response, list):
                print("✅ /api/marketplace/browse returns ARRAY - Compatible with .map()")
            else:
                print("❌ /api/marketplace/browse returns OBJECT - NOT compatible with .map()")
                if isinstance(browse_response, dict) and 'listings' in browse_response:
                    print("   Fix: Frontend should use response.listings.map() instead of response.map()")
        
        if listings_response is not None:
            if isinstance(listings_response, list):
                print("✅ /api/listings returns ARRAY - Compatible with .map()")
            else:
                print("❌ /api/listings returns OBJECT - NOT compatible with .map()")
                if isinstance(listings_response, dict) and 'listings' in listings_response:
                    print("   Fix: Frontend should use response.listings.map() instead of response.map()")

    def run_tests(self):
        """Run all browse listings tests"""
        print("🚀 Testing Browse Listings Response Formats")
        print("=" * 60)
        print("Purpose: Understand exact response structure to fix frontend TypeError")
        print("Error: 'TypeError: apiListings.map is not a function'")
        print("=" * 60)

        # Test both endpoints
        browse_success, browse_data = self.test_endpoint(
            "GET /api/marketplace/browse", 
            "api/marketplace/browse"
        )
        
        listings_success, listings_data = self.test_endpoint(
            "GET /api/listings", 
            "api/listings"
        )
        
        # Analyze compatibility
        self.test_marketplace_service_compatibility(browse_data, listings_data)
        
        # Summary
        print(f"\n📊 Test Summary")
        print("-" * 50)
        print(f"/api/marketplace/browse: {'✅ SUCCESS' if browse_success else '❌ FAILED'}")
        print(f"/api/listings: {'✅ SUCCESS' if listings_success else '❌ FAILED'}")
        
        if browse_success and listings_success:
            print(f"\n🎯 Root Cause Analysis:")
            if isinstance(browse_data, list) and isinstance(listings_data, dict):
                print("- /api/marketplace/browse returns ARRAY (good for .map())")
                print("- /api/listings returns OBJECT with 'listings' array inside")
                print("- Frontend is likely calling /api/listings but expecting array format")
                print("- Solution: Use response.listings.map() or switch to /api/marketplace/browse")
            elif isinstance(browse_data, dict) and isinstance(listings_data, list):
                print("- /api/marketplace/browse returns OBJECT")
                print("- /api/listings returns ARRAY (good for .map())")
                print("- Frontend should call /api/listings or use response.listings.map()")
            elif isinstance(browse_data, list) and isinstance(listings_data, list):
                print("- Both endpoints return ARRAY format (good for .map())")
                print("- Check which endpoint frontend is actually calling")
            else:
                print("- Both endpoints return OBJECT format")
                print("- Frontend needs to access nested array property")
        
        return browse_success or listings_success

def main():
    """Main test execution"""
    tester = ListingsResponseTester()
    success = tester.run_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())