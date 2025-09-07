#!/usr/bin/env python3
"""
Catalyst Content Debug Test - Specific Investigation for MazdaRF4SOK14 Listing
Debug why catalyst content sections are not showing up on individual listing pages for Admin users
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://inventory-fix-1.preview.emergentagent.com/api"

class CatalystDebugTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def test_admin_login(self):
        """Test admin login for catalyst access"""
        try:
            admin_credentials = {
                "email": "admin@cataloro.com",
                "password": "admin123"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login", 
                json=admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                user_role = user.get('user_role')
                user_id = user.get('id')
                
                self.log_test(
                    "Admin Login for Catalyst Access", 
                    True, 
                    f"Admin logged in successfully. Role: {user_role}, User ID: {user_id}"
                )
                return user
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login for Catalyst Access", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Admin Login for Catalyst Access", False, error_msg=str(e))
            return None

    def test_search_mazda_listing(self):
        """Search for MazdaRF4SOK14 listing specifically"""
        try:
            # Get all listings and search for MazdaRF4SOK14
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                # Search for MazdaRF4SOK14 in titles, descriptions, or IDs
                mazda_listings = []
                for listing in listings:
                    title = listing.get('title', '').lower()
                    description = listing.get('description', '').lower()
                    listing_id = listing.get('id', '').lower()
                    
                    if 'mazdarf4sok14' in title or 'mazdarf4sok14' in description or 'mazdarf4sok14' in listing_id:
                        mazda_listings.append(listing)
                    elif 'mazda' in title and ('rf4' in title or 'sok14' in title):
                        mazda_listings.append(listing)
                
                if mazda_listings:
                    self.log_test(
                        "Search MazdaRF4SOK14 Listing", 
                        True, 
                        f"Found {len(mazda_listings)} Mazda listings that might match MazdaRF4SOK14"
                    )
                    
                    # Print details of found listings
                    for i, listing in enumerate(mazda_listings):
                        print(f"   Mazda Listing {i+1}:")
                        print(f"     ID: {listing.get('id')}")
                        print(f"     Title: {listing.get('title')}")
                        print(f"     Has catalyst data: {self._has_catalyst_data(listing)}")
                        if self._has_catalyst_data(listing):
                            print(f"     Catalyst fields: {self._get_catalyst_summary(listing)}")
                    
                    return mazda_listings
                else:
                    # Search more broadly for any Mazda listings
                    broad_mazda = [l for l in listings if 'mazda' in l.get('title', '').lower()]
                    
                    self.log_test(
                        "Search MazdaRF4SOK14 Listing", 
                        False, 
                        f"MazdaRF4SOK14 not found. Found {len(broad_mazda)} general Mazda listings",
                        "Specific MazdaRF4SOK14 listing not found in current listings"
                    )
                    
                    if broad_mazda:
                        print("   General Mazda listings found:")
                        for listing in broad_mazda[:3]:
                            print(f"     - {listing.get('title')} (ID: {listing.get('id')})")
                    
                    return []
            else:
                self.log_test("Search MazdaRF4SOK14 Listing", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Search MazdaRF4SOK14 Listing", False, error_msg=str(e))
            return []

    def test_catalyst_database_search(self):
        """Search catalyst database for MazdaRF4SOK14"""
        try:
            # Try to access unified calculations endpoint to search for MazdaRF4SOK14
            response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations", timeout=10)
            
            if response.status_code == 200:
                catalysts = response.json()
                
                # Search for MazdaRF4SOK14 in catalyst database
                mazda_catalysts = []
                for catalyst in catalysts:
                    cat_id = catalyst.get('cat_id', '').lower()
                    name = catalyst.get('name', '').lower()
                    
                    if 'mazdarf4sok14' in cat_id or 'mazdarf4sok14' in name:
                        mazda_catalysts.append(catalyst)
                    elif 'mazda' in name and ('rf4' in name or 'sok14' in name):
                        mazda_catalysts.append(catalyst)
                
                if mazda_catalysts:
                    self.log_test(
                        "Catalyst Database Search for MazdaRF4SOK14", 
                        True, 
                        f"Found {len(mazda_catalysts)} matching catalysts in database"
                    )
                    
                    # Print details of found catalysts
                    for i, catalyst in enumerate(mazda_catalysts):
                        print(f"   Catalyst {i+1}:")
                        print(f"     Cat ID: {catalyst.get('cat_id')}")
                        print(f"     Name: {catalyst.get('name')}")
                        print(f"     Weight: {catalyst.get('weight')}g")
                        print(f"     Content values: Pt={catalyst.get('pt_g')}g, Pd={catalyst.get('pd_g')}g, Rh={catalyst.get('rh_g')}g")
                    
                    return mazda_catalysts
                else:
                    # Search more broadly
                    broad_mazda = [c for c in catalysts if 'mazda' in c.get('name', '').lower()]
                    
                    self.log_test(
                        "Catalyst Database Search for MazdaRF4SOK14", 
                        False, 
                        f"MazdaRF4SOK14 not found in catalyst database. Found {len(broad_mazda)} general Mazda catalysts",
                        "Specific MazdaRF4SOK14 catalyst not found in database"
                    )
                    
                    if broad_mazda:
                        print("   General Mazda catalysts found:")
                        for catalyst in broad_mazda[:5]:
                            print(f"     - {catalyst.get('name')} (Cat ID: {catalyst.get('cat_id')})")
                    
                    return []
            else:
                self.log_test("Catalyst Database Search for MazdaRF4SOK14", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Catalyst Database Search for MazdaRF4SOK14", False, error_msg=str(e))
            return []

    def test_individual_listing_endpoint(self, listing_id):
        """Test individual listing endpoint for specific listing"""
        try:
            response = requests.get(f"{BACKEND_URL}/listings/{listing_id}", timeout=10)
            
            if response.status_code == 200:
                listing = response.json()
                
                # Check catalyst data availability
                has_catalyst = self._has_catalyst_data(listing)
                catalyst_summary = self._get_catalyst_summary(listing) if has_catalyst else "No catalyst data"
                
                self.log_test(
                    f"Individual Listing Endpoint ({listing_id})", 
                    True, 
                    f"Listing retrieved successfully. Has catalyst data: {has_catalyst}. {catalyst_summary}"
                )
                
                return listing
            else:
                self.log_test(f"Individual Listing Endpoint ({listing_id})", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test(f"Individual Listing Endpoint ({listing_id})", False, error_msg=str(e))
            return None

    def test_listings_with_catalyst_data(self):
        """Find listings that DO have catalyst data for testing"""
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                # Find listings with significant catalyst data
                good_catalyst_listings = []
                for listing in listings:
                    if self._has_significant_catalyst_data(listing):
                        good_catalyst_listings.append({
                            'id': listing.get('id'),
                            'title': listing.get('title'),
                            'catalyst_summary': self._get_catalyst_summary(listing)
                        })
                
                if good_catalyst_listings:
                    self.log_test(
                        "Find Listings with Good Catalyst Data", 
                        True, 
                        f"Found {len(good_catalyst_listings)} listings with significant catalyst data"
                    )
                    
                    # Print top 5 listings with best catalyst data
                    print("   Top listings with catalyst data:")
                    for i, listing in enumerate(good_catalyst_listings[:5]):
                        print(f"     {i+1}. {listing['title']} (ID: {listing['id']})")
                        print(f"        {listing['catalyst_summary']}")
                    
                    return good_catalyst_listings
                else:
                    self.log_test("Find Listings with Good Catalyst Data", False, error_msg="No listings with significant catalyst data found")
                    return []
            else:
                self.log_test("Find Listings with Good Catalyst Data", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Find Listings with Good Catalyst Data", False, error_msg=str(e))
            return []

    def test_permission_system(self, admin_user):
        """Test permission system for Admin users"""
        try:
            if not admin_user:
                self.log_test("Permission System Test", False, error_msg="No admin user provided")
                return False
            
            user_role = admin_user.get('user_role')
            
            # Test the exact permission logic from frontend
            # (permissions?.userRole === 'Admin' || permissions?.userRole === 'Manager')
            is_admin = user_role == 'Admin'
            is_manager = user_role == 'Manager' or user_role == 'Admin-Manager'
            has_catalyst_permissions = is_admin or is_manager
            
            self.log_test(
                "Permission System Test", 
                has_catalyst_permissions, 
                f"User role: {user_role}, Is Admin: {is_admin}, Is Manager: {is_manager}, Has catalyst permissions: {has_catalyst_permissions}"
            )
            
            return has_catalyst_permissions
        except Exception as e:
            self.log_test("Permission System Test", False, error_msg=str(e))
            return False

    def _has_catalyst_data(self, listing):
        """Check if listing has any catalyst data"""
        catalyst_fields = ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm', 'pt_g', 'pd_g', 'rh_g']
        return any(listing.get(field) is not None for field in catalyst_fields)

    def _has_significant_catalyst_data(self, listing):
        """Check if listing has significant catalyst data (non-zero values)"""
        # Check for calculated values (pt_g, pd_g, rh_g) with meaningful amounts
        pt_g = listing.get('pt_g', 0) or 0
        pd_g = listing.get('pd_g', 0) or 0
        rh_g = listing.get('rh_g', 0) or 0
        
        # Consider significant if any content value > 0.01g
        has_significant_content = pt_g > 0.01 or pd_g > 0.01 or rh_g > 0.01
        
        # Or if has raw data with meaningful ppm values
        ceramic_weight = listing.get('ceramic_weight', 0) or 0
        pt_ppm = listing.get('pt_ppm', 0) or 0
        pd_ppm = listing.get('pd_ppm', 0) or 0
        rh_ppm = listing.get('rh_ppm', 0) or 0
        
        has_significant_raw = ceramic_weight > 0 and (pt_ppm > 0 or pd_ppm > 0 or rh_ppm > 0)
        
        return has_significant_content or has_significant_raw

    def _get_catalyst_summary(self, listing):
        """Get summary of catalyst data in listing"""
        summary_parts = []
        
        # Content values
        pt_g = listing.get('pt_g')
        pd_g = listing.get('pd_g')
        rh_g = listing.get('rh_g')
        
        if pt_g is not None or pd_g is not None or rh_g is not None:
            summary_parts.append(f"Content: Pt={pt_g}g, Pd={pd_g}g, Rh={rh_g}g")
        
        # Raw values
        ceramic_weight = listing.get('ceramic_weight')
        pt_ppm = listing.get('pt_ppm')
        pd_ppm = listing.get('pd_ppm')
        rh_ppm = listing.get('rh_ppm')
        
        if ceramic_weight is not None:
            summary_parts.append(f"Weight: {ceramic_weight}g")
        
        if pt_ppm is not None or pd_ppm is not None or rh_ppm is not None:
            summary_parts.append(f"PPM: Pt={pt_ppm}, Pd={pd_ppm}, Rh={rh_ppm}")
        
        return "; ".join(summary_parts) if summary_parts else "No catalyst data"

    def run_catalyst_debug_testing(self):
        """Run catalyst content debug testing"""
        print("=" * 80)
        print("CATALYST CONTENT DEBUG TESTING - MazdaRF4SOK14 INVESTIGATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Admin Login
        print("👤 ADMIN LOGIN FOR CATALYST ACCESS")
        print("-" * 40)
        admin_user = self.test_admin_login()
        
        # 2. Search for MazdaRF4SOK14 listing
        print("🔍 SEARCH FOR MazdaRF4SOK14 LISTING")
        print("-" * 40)
        mazda_listings = self.test_search_mazda_listing()
        
        # 3. Search catalyst database for MazdaRF4SOK14
        print("📊 CATALYST DATABASE SEARCH FOR MazdaRF4SOK14")
        print("-" * 40)
        mazda_catalysts = self.test_catalyst_database_search()
        
        # 4. Test individual listing endpoints for found listings
        if mazda_listings:
            print("🔍 INDIVIDUAL LISTING ENDPOINT TESTING")
            print("-" * 40)
            for listing in mazda_listings[:3]:
                self.test_individual_listing_endpoint(listing.get('id'))
        
        # 5. Find listings that DO have catalyst data
        print("✅ FIND LISTINGS WITH GOOD CATALYST DATA")
        print("-" * 40)
        good_catalyst_listings = self.test_listings_with_catalyst_data()
        
        # 6. Test permission system
        print("🔐 PERMISSION SYSTEM TESTING")
        print("-" * 40)
        self.test_permission_system(admin_user)
        
        # Print Summary
        print("=" * 80)
        print("CATALYST CONTENT DEBUG TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Analysis and Recommendations
        print("🔍 ANALYSIS AND RECOMMENDATIONS:")
        print("-" * 40)
        
        if not mazda_listings and not mazda_catalysts:
            print("❌ ISSUE IDENTIFIED: MazdaRF4SOK14 listing/catalyst not found")
            print("   - The specific listing 'MazdaRF4SOK14' does not exist in the current system")
            print("   - This explains why catalyst content sections are not showing up")
            print("   - RECOMMENDATION: Use one of the existing catalyst listings for testing")
        
        if good_catalyst_listings:
            print("✅ ALTERNATIVE LISTINGS AVAILABLE:")
            print("   - Found listings with proper catalyst data that can be used for testing")
            print("   - These listings should display catalyst content sections for Admin users")
            print(f"   - RECOMMENDED TEST LISTING: {good_catalyst_listings[0]['title']} (ID: {good_catalyst_listings[0]['id']})")
        
        if admin_user and admin_user.get('user_role') == 'Admin':
            print("✅ ADMIN PERMISSIONS WORKING:")
            print("   - Admin user login successful")
            print("   - Permission system correctly identifies Admin users")
            print("   - Frontend should show catalyst content sections for this user")
        
        print("\n🎯 CATALYST CONTENT DEBUG TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results, {
            'mazda_listings': mazda_listings,
            'mazda_catalysts': mazda_catalysts,
            'good_catalyst_listings': good_catalyst_listings,
            'admin_user': admin_user
        }

if __name__ == "__main__":
    tester = CatalystDebugTester()
    
    print("🎯 RUNNING CATALYST CONTENT DEBUG TESTING")
    print("Investigating why catalyst content sections are not showing up for MazdaRF4SOK14...")
    print()
    
    passed, failed, results, data = tester.run_catalyst_debug_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)