#!/usr/bin/env python3
"""
Detailed Data Analysis for Data Source Discrepancy
Analyzes the specific differences between /api/listings and /api/marketplace/browse
"""

import requests
import sys
import json
from datetime import datetime

class DetailedDataAnalyzer:
    def __init__(self, base_url="https://cataloro-dash.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()

    def get_endpoint_data(self, endpoint_name, endpoint_path):
        """Get data from an endpoint and analyze its structure"""
        url = f"{self.base_url}/{endpoint_path}"
        print(f"\n🔍 Analyzing {endpoint_name}")
        print(f"   URL: {url}")
        
        try:
            response = self.session.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                print(f"   Error: {response.text[:200]}")
                return False, None
                
        except Exception as e:
            print(f"   Exception: {str(e)}")
            return False, None

    def analyze_data_structure(self, data, endpoint_name):
        """Analyze the structure of data from an endpoint"""
        print(f"\n📊 {endpoint_name} Data Structure Analysis:")
        
        if isinstance(data, list):
            print(f"   Format: ARRAY")
            print(f"   Count: {len(data)}")
            
            if len(data) > 0:
                first_item = data[0]
                print(f"   Sample item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                
                # Analyze ID field
                if isinstance(first_item, dict):
                    id_field = first_item.get('id', 'NO_ID')
                    _id_field = first_item.get('_id', 'NO_MONGODB_ID')
                    print(f"   Sample ID: {id_field}")
                    print(f"   Sample _id: {_id_field}")
                    
                    # Check if it's a MongoDB ObjectId or UUID
                    if len(str(id_field)) == 24 and isinstance(id_field, str):
                        print(f"   ID Type: Likely MongoDB ObjectId")
                    elif len(str(id_field)) == 36 and '-' in str(id_field):
                        print(f"   ID Type: Likely UUID")
                    else:
                        print(f"   ID Type: Unknown format")
            
            return data
            
        elif isinstance(data, dict):
            print(f"   Format: OBJECT")
            print(f"   Keys: {list(data.keys())}")
            
            if 'listings' in data:
                listings = data['listings']
                print(f"   Listings count: {len(listings)}")
                
                if len(listings) > 0:
                    first_item = listings[0]
                    print(f"   Sample item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                    
                    # Analyze ID field
                    if isinstance(first_item, dict):
                        id_field = first_item.get('id', 'NO_ID')
                        _id_field = first_item.get('_id', 'NO_MONGODB_ID')
                        print(f"   Sample ID: {id_field}")
                        print(f"   Sample _id: {_id_field}")
                        
                        # Check if it's a MongoDB ObjectId or UUID
                        if len(str(id_field)) == 24 and isinstance(id_field, str):
                            print(f"   ID Type: Likely MongoDB ObjectId")
                        elif len(str(id_field)) == 36 and '-' in str(id_field):
                            print(f"   ID Type: Likely UUID")
                        else:
                            print(f"   ID Type: Unknown format")
                
                return listings
            else:
                return []
        else:
            print(f"   Format: UNKNOWN ({type(data)})")
            return []

    def compare_id_formats(self, listings_data, browse_data):
        """Compare ID formats between the two endpoints"""
        print(f"\n🔍 ID Format Comparison:")
        
        # Analyze listings IDs
        listings_ids = []
        listings_mongodb_ids = []
        for item in listings_data[:5]:  # First 5 items
            if isinstance(item, dict):
                id_val = item.get('id')
                _id_val = item.get('_id')
                if id_val:
                    listings_ids.append(str(id_val))
                if _id_val:
                    listings_mongodb_ids.append(str(_id_val))
        
        # Analyze browse IDs
        browse_ids = []
        browse_mongodb_ids = []
        for item in browse_data[:5]:  # First 5 items
            if isinstance(item, dict):
                id_val = item.get('id')
                _id_val = item.get('_id')
                if id_val:
                    browse_ids.append(str(id_val))
                if _id_val:
                    browse_mongodb_ids.append(str(_id_val))
        
        print(f"   /api/listings IDs: {listings_ids}")
        print(f"   /api/listings _ids: {listings_mongodb_ids}")
        print(f"   /api/marketplace/browse IDs: {browse_ids}")
        print(f"   /api/marketplace/browse _ids: {browse_mongodb_ids}")
        
        # Check for matches
        id_matches = set(listings_ids).intersection(set(browse_ids))
        mongodb_id_matches = set(listings_mongodb_ids).intersection(set(browse_mongodb_ids))
        
        print(f"\n📊 ID Match Analysis:")
        print(f"   ID field matches: {len(id_matches)} - {list(id_matches)}")
        print(f"   _id field matches: {len(mongodb_id_matches)} - {list(mongodb_id_matches)}")
        
        # Cross-check: Do listings IDs match browse _ids?
        cross_matches_1 = set(listings_ids).intersection(set(browse_mongodb_ids))
        cross_matches_2 = set(listings_mongodb_ids).intersection(set(browse_ids))
        
        print(f"   Cross-matches (listings.id vs browse._id): {len(cross_matches_1)} - {list(cross_matches_1)}")
        print(f"   Cross-matches (listings._id vs browse.id): {len(cross_matches_2)} - {list(cross_matches_2)}")
        
        return {
            'id_matches': len(id_matches),
            'mongodb_id_matches': len(mongodb_id_matches),
            'cross_matches_1': len(cross_matches_1),
            'cross_matches_2': len(cross_matches_2)
        }

    def analyze_content_differences(self, listings_data, browse_data):
        """Analyze content differences between the endpoints"""
        print(f"\n📋 Content Analysis:")
        
        # Sample titles from each endpoint
        listings_titles = [item.get('title', 'NO_TITLE') for item in listings_data[:10] if isinstance(item, dict)]
        browse_titles = [item.get('title', 'NO_TITLE') for item in browse_data[:10] if isinstance(item, dict)]
        
        print(f"   Sample /api/listings titles:")
        for i, title in enumerate(listings_titles[:5]):
            print(f"     {i+1}. {title}")
        
        print(f"   Sample /api/marketplace/browse titles:")
        for i, title in enumerate(browse_titles[:5]):
            print(f"     {i+1}. {title}")
        
        # Check for title matches
        title_matches = set(listings_titles).intersection(set(browse_titles))
        print(f"\n   Title matches: {len(title_matches)}")
        if title_matches:
            print(f"   Matching titles: {list(title_matches)[:3]}")
        
        # Analyze status fields
        listings_statuses = [item.get('status', 'NO_STATUS') for item in listings_data if isinstance(item, dict)]
        browse_statuses = [item.get('status', 'NO_STATUS') for item in browse_data if isinstance(item, dict)]
        
        print(f"\n   /api/listings status values: {set(listings_statuses)}")
        print(f"   /api/marketplace/browse status values: {set(browse_statuses)}")

    def test_create_and_track_listing(self):
        """Create a listing and track it through both endpoints"""
        print(f"\n🧪 Create and Track Test:")
        
        # First, login to get user ID
        login_data = {"email": "user@cataloro.com", "password": "demo123"}
        login_response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print("   ❌ Failed to login")
            return False
        
        user_data = login_response.json()
        user_id = user_data['user']['id']
        print(f"   ✅ Logged in as user: {user_id}")
        
        # Create a test listing
        test_listing = {
            "title": "TRACKING TEST - Smartphone Analysis",
            "description": "Test listing to track data flow between endpoints",
            "price": 599.99,
            "category": "Electronics",
            "condition": "Used - Good",
            "seller_id": user_id,
            "images": ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400"]
        }
        
        create_response = self.session.post(f"{self.base_url}/api/listings", json=test_listing)
        
        if create_response.status_code != 200:
            print(f"   ❌ Failed to create listing: {create_response.text}")
            return False
        
        create_data = create_response.json()
        listing_id = create_data.get('listing_id')
        print(f"   ✅ Created listing with ID: {listing_id}")
        
        # Check if it appears in /api/listings
        listings_success, listings_data = self.get_endpoint_data("/api/listings", "api/listings")
        if listings_success:
            listings_items = listings_data.get('listings', listings_data) if isinstance(listings_data, dict) else listings_data
            found_in_listings = any(item.get('id') == listing_id for item in listings_items if isinstance(item, dict))
            print(f"   📋 Found in /api/listings: {found_in_listings}")
            
            if found_in_listings:
                # Find the actual item
                for item in listings_items:
                    if isinstance(item, dict) and item.get('id') == listing_id:
                        print(f"      ID: {item.get('id')}")
                        print(f"      _id: {item.get('_id')}")
                        print(f"      Title: {item.get('title')}")
                        print(f"      Status: {item.get('status')}")
                        break
        
        # Check if it appears in /api/marketplace/browse
        browse_success, browse_data = self.get_endpoint_data("/api/marketplace/browse", "api/marketplace/browse")
        if browse_success:
            found_in_browse = any(item.get('id') == listing_id for item in browse_data if isinstance(item, dict))
            print(f"   🌐 Found in /api/marketplace/browse: {found_in_browse}")
            
            if found_in_browse:
                # Find the actual item
                for item in browse_data:
                    if isinstance(item, dict) and item.get('id') == listing_id:
                        print(f"      ID: {item.get('id')}")
                        print(f"      _id: {item.get('_id')}")
                        print(f"      Title: {item.get('title')}")
                        print(f"      Status: {item.get('status')}")
                        break
        
        # Clean up - delete the test listing
        delete_response = self.session.delete(f"{self.base_url}/api/listings/{listing_id}")
        if delete_response.status_code == 200:
            print(f"   🗑️  Test listing deleted successfully")
        
        return True

    def run_detailed_analysis(self):
        """Run complete detailed analysis"""
        print("🔍 Starting Detailed Data Source Analysis")
        print("=" * 60)
        
        # Get data from both endpoints
        listings_success, listings_raw_data = self.get_endpoint_data("/api/listings", "api/listings")
        browse_success, browse_raw_data = self.get_endpoint_data("/api/marketplace/browse", "api/marketplace/browse")
        
        if not listings_success or not browse_success:
            print("❌ Failed to get data from one or both endpoints")
            return False
        
        # Analyze data structures
        listings_data = self.analyze_data_structure(listings_raw_data, "/api/listings")
        browse_data = self.analyze_data_structure(browse_raw_data, "/api/marketplace/browse")
        
        # Compare ID formats
        id_analysis = self.compare_id_formats(listings_data, browse_data)
        
        # Analyze content differences
        self.analyze_content_differences(listings_data, browse_data)
        
        # Test create and track
        self.test_create_and_track_listing()
        
        # Final conclusions
        print(f"\n" + "=" * 60)
        print("🔍 DETAILED ANALYSIS CONCLUSIONS")
        print("=" * 60)
        
        if id_analysis['mongodb_id_matches'] > 0:
            print("✅ FINDING: Endpoints share data via MongoDB _id field")
            print("   - Both endpoints access the same database collection")
            print("   - The 'id' field format differs between endpoints")
        elif id_analysis['cross_matches_2'] > 0:
            print("✅ FINDING: Data correlation found via cross-matching")
            print("   - /api/listings uses MongoDB _id as 'id' field")
            print("   - /api/marketplace/browse uses UUID as 'id' field")
        elif id_analysis['id_matches'] > 0:
            print("✅ FINDING: Direct ID matches found")
            print("   - Both endpoints use the same ID format")
        else:
            print("⚠️  FINDING: No clear data correlation found")
            print("   - Endpoints may be using different data sources")
            print("   - Or different ID generation strategies")
        
        print(f"\n📊 Summary:")
        print(f"   - /api/listings returned {len(listings_data)} items")
        print(f"   - /api/marketplace/browse returned {len(browse_data)} items")
        print(f"   - ID matches: {id_analysis['id_matches']}")
        print(f"   - MongoDB ID matches: {id_analysis['mongodb_id_matches']}")
        print(f"   - Cross matches: {id_analysis['cross_matches_1']} + {id_analysis['cross_matches_2']}")
        
        return True

def main():
    """Main analysis execution"""
    analyzer = DetailedDataAnalyzer()
    success = analyzer.run_detailed_analysis()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())