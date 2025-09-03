#!/usr/bin/env python3
"""
Final Data Source Investigation Test
Comprehensive test documenting the data source discrepancy findings
"""

import requests
import sys
import json
import time
from datetime import datetime

class FinalDataSourceTest:
    def __init__(self, base_url="https://tender-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.findings = []

    def add_finding(self, category, finding, severity="INFO"):
        """Add a finding to the results"""
        self.findings.append({
            "category": category,
            "finding": finding,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        severity_icon = {"CRITICAL": "🚨", "WARNING": "⚠️", "INFO": "ℹ️"}
        print(f"{severity_icon.get(severity, 'ℹ️')} {category}: {finding}")

    def test_data_source_discrepancy(self):
        """Comprehensive test of the data source discrepancy"""
        print("🔍 FINAL DATA SOURCE DISCREPANCY INVESTIGATION")
        print("=" * 60)
        
        # Test 1: Authenticate
        print("\n1️⃣ Authentication Setup")
        login_data = {"email": "user@cataloro.com", "password": "demo123"}
        login_response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            self.add_finding("Authentication", "Failed to authenticate user", "CRITICAL")
            return False
        
        user_data = login_response.json()
        user_id = user_data['user']['id']
        self.add_finding("Authentication", f"Successfully authenticated user: {user_id}", "INFO")
        
        # Test 2: Analyze endpoint response formats
        print("\n2️⃣ Endpoint Response Format Analysis")
        
        # Get /api/listings data
        listings_response = self.session.get(f"{self.base_url}/api/listings")
        if listings_response.status_code == 200:
            listings_data = listings_response.json()
            if isinstance(listings_data, dict) and 'listings' in listings_data:
                listings_count = len(listings_data['listings'])
                self.add_finding("Response Format", f"/api/listings returns OBJECT format with {listings_count} listings", "INFO")
            else:
                self.add_finding("Response Format", "/api/listings has unexpected format", "WARNING")
        
        # Get /api/marketplace/browse data
        browse_response = self.session.get(f"{self.base_url}/api/marketplace/browse")
        if browse_response.status_code == 200:
            browse_data = browse_response.json()
            if isinstance(browse_data, list):
                browse_count = len(browse_data)
                self.add_finding("Response Format", f"/api/marketplace/browse returns ARRAY format with {browse_count} listings", "INFO")
            else:
                self.add_finding("Response Format", "/api/marketplace/browse has unexpected format", "WARNING")
        
        # Test 3: ID Format Analysis
        print("\n3️⃣ ID Format Analysis")
        
        if listings_response.status_code == 200 and browse_response.status_code == 200:
            listings_items = listings_data.get('listings', [])
            browse_items = browse_data if isinstance(browse_data, list) else []
            
            # Analyze ID formats
            if listings_items:
                sample_listing = listings_items[0]
                listing_id = sample_listing.get('id', 'NO_ID')
                listing_mongodb_id = sample_listing.get('_id', 'NO_MONGODB_ID')
                
                self.add_finding("ID Format", f"/api/listings uses UUID format for 'id': {listing_id}", "INFO")
                self.add_finding("ID Format", f"/api/listings includes MongoDB '_id': {listing_mongodb_id}", "INFO")
            
            if browse_items:
                sample_browse = browse_items[0]
                browse_id = sample_browse.get('id', 'NO_ID')
                browse_mongodb_id = sample_browse.get('_id', 'NO_MONGODB_ID')
                
                self.add_finding("ID Format", f"/api/marketplace/browse uses MongoDB ObjectId format for 'id': {browse_id}", "INFO")
                self.add_finding("ID Format", f"/api/marketplace/browse '_id' field: {browse_mongodb_id}", "INFO")
        
        # Test 4: Data Correlation Analysis
        print("\n4️⃣ Data Correlation Analysis")
        
        if listings_response.status_code == 200 and browse_response.status_code == 200:
            listings_items = listings_data.get('listings', [])
            browse_items = browse_data if isinstance(browse_data, list) else []
            
            # Check for cross-correlation (listings._id vs browse.id)
            listings_mongodb_ids = [item.get('_id') for item in listings_items if item.get('_id')]
            browse_ids = [item.get('id') for item in browse_items if item.get('id')]
            
            correlation_matches = set(listings_mongodb_ids).intersection(set(browse_ids))
            correlation_count = len(correlation_matches)
            
            if correlation_count > 0:
                self.add_finding("Data Correlation", f"Found {correlation_count} correlated records between endpoints", "INFO")
                self.add_finding("Data Correlation", "Endpoints access same database but use different ID mapping", "WARNING")
            else:
                self.add_finding("Data Correlation", "No correlation found between endpoints", "CRITICAL")
        
        # Test 5: Status Filter Analysis
        print("\n5️⃣ Status Filter Analysis")
        
        if listings_response.status_code == 200 and browse_response.status_code == 200:
            listings_items = listings_data.get('listings', [])
            browse_items = browse_data if isinstance(browse_data, list) else []
            
            # Analyze status values
            listings_statuses = [item.get('status') for item in listings_items if item.get('status')]
            browse_statuses = [item.get('status') for item in browse_items if item.get('status')]
            
            unique_listings_statuses = set(listings_statuses)
            unique_browse_statuses = set(browse_statuses)
            
            self.add_finding("Status Filter", f"/api/listings status values: {unique_listings_statuses}", "INFO")
            self.add_finding("Status Filter", f"/api/marketplace/browse status values: {unique_browse_statuses}", "INFO")
            
            if unique_browse_statuses == {'active'}:
                self.add_finding("Status Filter", "/api/marketplace/browse only shows 'active' listings", "INFO")
            
            if len(unique_listings_statuses) > 1:
                self.add_finding("Status Filter", "/api/listings shows multiple status values", "INFO")
        
        # Test 6: Create, Delete, and Track Test
        print("\n6️⃣ Create, Delete, and Track Test")
        
        # Create test listing
        test_listing = {
            "title": "FINAL TEST - Data Source Investigation",
            "description": "Final test to verify data source behavior",
            "price": 999.99,
            "category": "Electronics",
            "condition": "New",
            "seller_id": user_id,
            "images": ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400"]
        }
        
        create_response = self.session.post(f"{self.base_url}/api/listings", json=test_listing)
        if create_response.status_code == 200:
            create_data = create_response.json()
            listing_id = create_data.get('listing_id')
            self.add_finding("CRUD Test", f"Successfully created test listing: {listing_id}", "INFO")
            
            # Check immediate appearance in both endpoints
            time.sleep(1)  # Brief wait for consistency
            
            # Check in /api/listings
            listings_check = self.session.get(f"{self.base_url}/api/listings")
            if listings_check.status_code == 200:
                listings_check_data = listings_check.json()
                listings_items = listings_check_data.get('listings', [])
                found_in_listings = any(item.get('id') == listing_id for item in listings_items)
                self.add_finding("CRUD Test", f"New listing found in /api/listings: {found_in_listings}", "INFO")
            
            # Check in /api/marketplace/browse
            browse_check = self.session.get(f"{self.base_url}/api/marketplace/browse")
            if browse_check.status_code == 200:
                browse_check_data = browse_check.json()
                # Need to check by MongoDB _id since browse uses different ID format
                found_in_browse = any(item.get('title') == test_listing['title'] for item in browse_check_data)
                self.add_finding("CRUD Test", f"New listing found in /api/marketplace/browse: {found_in_browse}", "INFO")
            
            # Delete the test listing
            delete_response = self.session.delete(f"{self.base_url}/api/listings/{listing_id}")
            if delete_response.status_code == 200:
                self.add_finding("CRUD Test", f"Successfully deleted test listing: {listing_id}", "INFO")
                
                # Verify deletion persistence
                time.sleep(1)
                
                # Check deletion in /api/listings
                listings_after = self.session.get(f"{self.base_url}/api/listings")
                if listings_after.status_code == 200:
                    listings_after_data = listings_after.json()
                    listings_items = listings_after_data.get('listings', [])
                    still_in_listings = any(item.get('id') == listing_id for item in listings_items)
                    self.add_finding("CRUD Test", f"Deleted listing still in /api/listings: {still_in_listings}", "WARNING" if still_in_listings else "INFO")
                
                # Check deletion in /api/marketplace/browse
                browse_after = self.session.get(f"{self.base_url}/api/marketplace/browse")
                if browse_after.status_code == 200:
                    browse_after_data = browse_after.json()
                    still_in_browse = any(item.get('title') == test_listing['title'] for item in browse_after_data)
                    self.add_finding("CRUD Test", f"Deleted listing still in /api/marketplace/browse: {still_in_browse}", "WARNING" if still_in_browse else "INFO")
            else:
                self.add_finding("CRUD Test", f"Failed to delete test listing: {delete_response.status_code}", "WARNING")
        else:
            self.add_finding("CRUD Test", f"Failed to create test listing: {create_response.status_code}", "WARNING")
        
        return True

    def generate_summary(self):
        """Generate investigation summary"""
        print("\n" + "=" * 60)
        print("📋 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        critical_findings = [f for f in self.findings if f['severity'] == 'CRITICAL']
        warning_findings = [f for f in self.findings if f['severity'] == 'WARNING']
        info_findings = [f for f in self.findings if f['severity'] == 'INFO']
        
        print(f"\n📊 Findings Summary:")
        print(f"   🚨 Critical: {len(critical_findings)}")
        print(f"   ⚠️  Warnings: {len(warning_findings)}")
        print(f"   ℹ️  Info: {len(info_findings)}")
        
        print(f"\n🔍 Key Discoveries:")
        
        # Root cause analysis
        has_format_discrepancy = any("OBJECT format" in f['finding'] and "ARRAY format" in f['finding'] for f in self.findings)
        has_id_mapping_issue = any("different ID mapping" in f['finding'] for f in self.findings)
        has_status_filtering = any("only shows 'active'" in f['finding'] for f in self.findings)
        
        if has_id_mapping_issue:
            print("   ✅ ROOT CAUSE IDENTIFIED: ID Mapping Discrepancy")
            print("      - /api/listings uses UUID for 'id' field")
            print("      - /api/marketplace/browse uses MongoDB ObjectId for 'id' field")
            print("      - Both access same database but serialize IDs differently")
        
        if has_status_filtering:
            print("   ✅ FILTERING DIFFERENCE IDENTIFIED:")
            print("      - /api/marketplace/browse only shows 'active' status listings")
            print("      - /api/listings shows all status values")
        
        if has_format_discrepancy:
            print("   ✅ RESPONSE FORMAT DIFFERENCE:")
            print("      - /api/listings returns object with 'listings' array")
            print("      - /api/marketplace/browse returns array directly")
        
        print(f"\n💡 CONCLUSION:")
        if critical_findings:
            print("   🚨 CRITICAL ISSUES FOUND - Data source discrepancy confirmed")
        elif warning_findings:
            print("   ⚠️  MINOR DISCREPANCIES - Same data source, different presentation")
        else:
            print("   ✅ NO MAJOR ISSUES - Endpoints working as designed")
        
        # Recommendations
        print(f"\n🔧 RECOMMENDATIONS:")
        if has_id_mapping_issue:
            print("   1. Standardize ID field format across all endpoints")
            print("   2. Use consistent serialization for MongoDB documents")
        
        if has_format_discrepancy:
            print("   3. Standardize response format (either all arrays or all objects)")
        
        print("   4. Add API documentation explaining endpoint differences")
        print("   5. Consider adding endpoint versioning for consistency")
        
        return len(critical_findings) == 0

    def run_final_test(self):
        """Run the complete final test"""
        success = self.test_data_source_discrepancy()
        if success:
            return self.generate_summary()
        return False

def main():
    """Main test execution"""
    tester = FinalDataSourceTest()
    success = tester.run_final_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())