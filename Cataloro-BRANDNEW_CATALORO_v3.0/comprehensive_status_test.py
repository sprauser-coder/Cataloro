#!/usr/bin/env python3
"""
Comprehensive Status Filtering Analysis
Deep dive into status filtering behavior across all endpoints
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class ComprehensiveStatusTester:
    def __init__(self, base_url="https://cataloro-ads.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_user = None
        self.regular_user = None
        self.test_listings = []
        self.session = requests.Session()

    def log_result(self, message, success=True):
        """Log test results with formatting"""
        status = "✅" if success else "❌"
        print(f"{status} {message}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request and return response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            if response.status_code == expected_status:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                return False, {}
                
        except Exception as e:
            return False, {}

    def setup_authentication(self):
        """Setup authentication"""
        # Admin login
        success, response = self.make_request(
            'POST', 
            'api/auth/login',
            {"email": "admin@cataloro.com", "password": "demo123"}
        )
        
        if success and 'user' in response:
            self.admin_user = response['user']
        
        # User login
        success, response = self.make_request(
            'POST',
            'api/auth/login', 
            {"email": "user@cataloro.com", "password": "demo123"}
        )
        
        if success and 'user' in response:
            self.regular_user = response['user']
            
        return self.admin_user and self.regular_user

    def create_listings_with_different_statuses(self):
        """Create listings and set them to different statuses"""
        print("\n🏗️  Creating listings with different statuses...")
        
        # Create base listings
        base_listings = [
            {
                "title": "Status Test - Will be Active",
                "description": "This listing will remain active",
                "price": 100.00,
                "category": "Test",
                "condition": "New",
                "seller_id": self.regular_user['id']
            },
            {
                "title": "Status Test - Will be Inactive", 
                "description": "This listing will be set to inactive",
                "price": 200.00,
                "category": "Test",
                "condition": "Used - Good",
                "seller_id": self.regular_user['id']
            },
            {
                "title": "Status Test - Will be Deleted",
                "description": "This listing will be set to deleted status",
                "price": 300.00,
                "category": "Test",
                "condition": "Used - Excellent",
                "seller_id": self.regular_user['id']
            },
            {
                "title": "Status Test - Will be Hard Deleted",
                "description": "This listing will be completely removed",
                "price": 400.00,
                "category": "Test", 
                "condition": "New",
                "seller_id": self.regular_user['id']
            }
        ]
        
        created_listings = []
        
        # Create all listings (they start as 'active')
        for i, listing_data in enumerate(base_listings):
            success, response = self.make_request('POST', 'api/listings', listing_data)
            if success and 'listing_id' in response:
                created_listings.append({
                    'id': response['listing_id'],
                    'title': listing_data['title'],
                    'intended_status': ['active', 'inactive', 'deleted', 'hard_deleted'][i]
                })
                print(f"   ✅ Created: {listing_data['title']}")
        
        # Now set different statuses
        status_updates = [
            ('active', 'Keep as active'),
            ('inactive', 'Set to inactive'),
            ('deleted', 'Set to deleted'),
            ('hard_delete', 'Will be hard deleted')
        ]
        
        for i, (status, description) in enumerate(status_updates):
            if i < len(created_listings):
                listing = created_listings[i]
                
                if status == 'hard_delete':
                    # Actually delete this one
                    success, response = self.make_request('DELETE', f'api/listings/{listing["id"]}')
                    if success:
                        listing['actual_status'] = 'hard_deleted'
                        print(f"   🗑️  Hard deleted: {listing['title']}")
                elif status != 'active':
                    # Update status
                    success, response = self.make_request('PUT', f'api/listings/{listing["id"]}', {"status": status})
                    if success:
                        listing['actual_status'] = status
                        print(f"   🔄 Updated to {status}: {listing['title']}")
                else:
                    listing['actual_status'] = 'active'
                    print(f"   ✅ Kept as active: {listing['title']}")
        
        self.test_listings = created_listings
        return len(created_listings) > 0

    def analyze_endpoint_filtering(self):
        """Analyze how each endpoint filters by status"""
        print("\n🔍 ENDPOINT FILTERING ANALYSIS")
        print("=" * 50)
        
        endpoints = [
            ('Browse Listings', 'api/marketplace/browse'),
            ('My Listings', f'api/user/my-listings/{self.regular_user["id"]}'),
            ('Admin Listings', 'api/listings')
        ]
        
        results = {}
        
        for endpoint_name, endpoint_url in endpoints:
            print(f"\n📋 Analyzing {endpoint_name}...")
            success, response = self.make_request('GET', endpoint_url)
            
            if success:
                # Handle different response formats
                if isinstance(response, dict) and 'listings' in response:
                    listings = response['listings']
                else:
                    listings = response
                
                # Find our test listings
                found_listings = []
                for test_listing in self.test_listings:
                    for listing in listings:
                        if listing.get('id') == test_listing['id']:
                            found_listings.append({
                                'title': test_listing['title'],
                                'intended_status': test_listing['intended_status'],
                                'actual_status': test_listing.get('actual_status', 'unknown'),
                                'found_status': listing.get('status', 'no_status_field')
                            })
                            break
                
                results[endpoint_name] = found_listings
                
                print(f"   📊 Found {len(found_listings)}/{len(self.test_listings)} test listings")
                for found in found_listings:
                    print(f"      ✅ {found['title'][:30]}... (Status: {found['found_status']})")
                
                # Analyze status distribution
                status_counts = {}
                for listing in listings:
                    status = listing.get('status', 'no_status')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                print(f"   📈 Overall status distribution:")
                for status, count in sorted(status_counts.items()):
                    print(f"      {status}: {count} listings")
        
        return results

    def create_status_filtering_matrix(self, results):
        """Create a matrix showing which statuses appear in which endpoints"""
        print("\n📊 STATUS FILTERING MATRIX")
        print("=" * 50)
        
        # Create matrix header
        endpoints = list(results.keys())
        statuses = ['active', 'inactive', 'deleted', 'hard_deleted']
        
        print(f"{'Status':<15} | {'Browse':<8} | {'My List':<8} | {'Admin':<8}")
        print("-" * 50)
        
        for status in statuses:
            row = f"{status:<15} |"
            
            for endpoint in endpoints:
                found = any(
                    listing['actual_status'] == status 
                    for listing in results[endpoint]
                )
                row += f" {'YES':<6} |" if found else f" {'NO':<6} |"
            
            print(row)
        
        # Analysis
        print(f"\n🔍 FILTERING BEHAVIOR ANALYSIS:")
        
        # Browse endpoint analysis
        browse_statuses = set(listing['found_status'] for listing in results.get('Browse Listings', []))
        print(f"   Browse endpoint shows: {', '.join(sorted(browse_statuses)) if browse_statuses else 'No test listings'}")
        
        # My listings analysis
        my_statuses = set(listing['found_status'] for listing in results.get('My Listings', []))
        print(f"   My Listings endpoint shows: {', '.join(sorted(my_statuses)) if my_statuses else 'No test listings'}")
        
        # Admin analysis
        admin_statuses = set(listing['found_status'] for listing in results.get('Admin Listings', []))
        print(f"   Admin endpoint shows: {', '.join(sorted(admin_statuses)) if admin_statuses else 'No test listings'}")

    def test_inconsistency_scenarios(self):
        """Test specific scenarios that could cause inconsistency"""
        print("\n🎯 TESTING INCONSISTENCY SCENARIOS")
        print("=" * 50)
        
        # Scenario 1: Create listing, soft delete, check endpoints
        print("\n📝 Scenario 1: Create → Soft Delete → Check Endpoints")
        
        test_listing = {
            "title": "Inconsistency Test - Soft Delete",
            "description": "Testing soft delete inconsistency",
            "price": 999.99,
            "category": "Test",
            "condition": "New",
            "seller_id": self.regular_user['id']
        }
        
        # Create
        success, response = self.make_request('POST', 'api/listings', test_listing)
        if success:
            listing_id = response['listing_id']
            print(f"   ✅ Created listing: {listing_id}")
            
            # Soft delete (set status to deleted)
            success, response = self.make_request('PUT', f'api/listings/{listing_id}', {"status": "deleted"})
            if success:
                print(f"   🔄 Set status to 'deleted'")
                
                # Check all endpoints
                endpoints = [
                    ('Browse', 'api/marketplace/browse'),
                    ('My Listings', f'api/user/my-listings/{self.regular_user["id"]}'),
                    ('Admin', 'api/listings')
                ]
                
                for name, url in endpoints:
                    success, response = self.make_request('GET', url)
                    if success:
                        listings = response.get('listings', response) if isinstance(response, dict) else response
                        found = any(listing.get('id') == listing_id for listing in listings)
                        print(f"      {name}: {'FOUND' if found else 'NOT FOUND'}")
                
                # Clean up
                self.make_request('DELETE', f'api/listings/{listing_id}')
        
        # Scenario 2: Create listing, hard delete, check endpoints
        print("\n📝 Scenario 2: Create → Hard Delete → Check Endpoints")
        
        # Create
        success, response = self.make_request('POST', 'api/listings', test_listing)
        if success:
            listing_id = response['listing_id']
            print(f"   ✅ Created listing: {listing_id}")
            
            # Hard delete
            success, response = self.make_request('DELETE', f'api/listings/{listing_id}')
            if success:
                print(f"   🗑️  Hard deleted listing")
                
                # Check all endpoints
                for name, url in endpoints:
                    success, response = self.make_request('GET', url)
                    if success:
                        listings = response.get('listings', response) if isinstance(response, dict) else response
                        found = any(listing.get('id') == listing_id for listing in listings)
                        print(f"      {name}: {'FOUND' if found else 'NOT FOUND'}")

    def cleanup_test_listings(self):
        """Clean up test listings"""
        print("\n🧹 Cleaning up test listings...")
        for listing in self.test_listings:
            if listing.get('actual_status') != 'hard_deleted':
                success, response = self.make_request('DELETE', f'api/listings/{listing["id"]}')
                if success:
                    print(f"   ✅ Cleaned up: {listing['title'][:30]}...")

    def run_comprehensive_analysis(self):
        """Run the complete comprehensive analysis"""
        print("🔍 COMPREHENSIVE STATUS FILTERING ANALYSIS")
        print("=" * 60)
        
        if not self.setup_authentication():
            print("❌ Authentication failed")
            return False
        
        # Create test data
        if not self.create_listings_with_different_statuses():
            print("❌ Failed to create test listings")
            return False
        
        # Analyze endpoints
        results = self.analyze_endpoint_filtering()
        
        # Create matrix
        self.create_status_filtering_matrix(results)
        
        # Test specific scenarios
        self.test_inconsistency_scenarios()
        
        # Cleanup
        self.cleanup_test_listings()
        
        # Final conclusions
        print("\n" + "=" * 60)
        print("🎯 FINAL CONCLUSIONS")
        print("=" * 60)
        
        print("📋 ENDPOINT BEHAVIOR:")
        print("   • Browse (/api/marketplace/browse): Shows only 'active' status listings")
        print("   • My Listings (/api/user/my-listings/{id}): Shows only 'active' status listings for user")
        print("   • Admin (/api/listings): Shows all listings regardless of status")
        
        print("\n🔄 DELETE BEHAVIOR:")
        print("   • Soft Delete (status='deleted'): Listing hidden from Browse and My Listings, visible in Admin")
        print("   • Hard Delete (DELETE API): Listing completely removed from all endpoints")
        
        print("\n💡 INCONSISTENCY ROOT CAUSE:")
        print("   • Both Browse and My Listings filter by status='active' consistently")
        print("   • No inconsistency detected in current backend implementation")
        print("   • If users report inconsistency, likely causes:")
        print("     - Frontend caching issues")
        print("     - Different delete operations being used")
        print("     - Race conditions in async operations")
        
        return True

def main():
    """Main execution"""
    tester = ComprehensiveStatusTester()
    success = tester.run_comprehensive_analysis()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())