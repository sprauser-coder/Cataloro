#!/usr/bin/env python3
"""
Catalyst Content Verification Test - Complete Flow Testing
Comprehensive verification of catalyst content display on individual listing pages for Admin users
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://inventory-fix-1.preview.emergentagent.com/api"

class CatalystContentVerificationTester:
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

    def test_admin_login_and_permissions(self):
        """Test admin login and verify permissions for catalyst content visibility"""
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
                
                # Check if user has admin/manager permissions for catalyst content
                has_catalyst_permissions = user_role in ['Admin', 'Admin-Manager']
                
                self.log_test(
                    "Admin Login and Catalyst Permissions", 
                    has_catalyst_permissions, 
                    f"Admin logged in successfully. Role: {user_role}, Has catalyst permissions: {has_catalyst_permissions}, User ID: {user_id}"
                )
                return user if has_catalyst_permissions else None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Login and Catalyst Permissions", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Admin Login and Catalyst Permissions", False, error_msg=str(e))
            return None

    def test_mazda_listing_specific_check(self):
        """Test the specific MazdaRF4SOK14 listing mentioned in the review"""
        try:
            # Get all listings and find MazdaRF4SOK14
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                # Find the exact MazdaRF4SOK14 listing
                mazda_listing = None
                for listing in listings:
                    if listing.get('title') == 'MazdaRF4SOK14':
                        mazda_listing = listing
                        break
                
                if mazda_listing:
                    # Check catalyst data
                    has_catalyst_data = any([
                        mazda_listing.get('ceramic_weight'),
                        mazda_listing.get('pt_ppm'),
                        mazda_listing.get('pd_ppm'),
                        mazda_listing.get('rh_ppm'),
                        mazda_listing.get('pt_g'),
                        mazda_listing.get('pd_g'),
                        mazda_listing.get('rh_g')
                    ])
                    
                    catalyst_summary = self._get_catalyst_summary(mazda_listing)
                    
                    self.log_test(
                        "MazdaRF4SOK14 Listing Specific Check", 
                        True, 
                        f"Found MazdaRF4SOK14 listing (ID: {mazda_listing.get('id')}). Has catalyst data: {has_catalyst_data}. {catalyst_summary}"
                    )
                    
                    return mazda_listing
                else:
                    self.log_test("MazdaRF4SOK14 Listing Specific Check", False, error_msg="MazdaRF4SOK14 listing not found")
                    return None
            else:
                self.log_test("MazdaRF4SOK14 Listing Specific Check", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("MazdaRF4SOK14 Listing Specific Check", False, error_msg=str(e))
            return None

    def test_individual_listing_endpoint_complete_data(self, listing_id):
        """Test individual listing endpoint returns complete product data including catalyst fields"""
        try:
            response = requests.get(f"{BACKEND_URL}/listings/{listing_id}", timeout=10)
            
            if response.status_code == 200:
                listing = response.json()
                
                # Check all catalyst fields
                catalyst_fields = {
                    'ceramic_weight': listing.get('ceramic_weight'),
                    'pt_ppm': listing.get('pt_ppm'),
                    'pd_ppm': listing.get('pd_ppm'),
                    'rh_ppm': listing.get('rh_ppm'),
                    'pt_g': listing.get('pt_g'),
                    'pd_g': listing.get('pd_g'),
                    'rh_g': listing.get('rh_g')
                }
                
                # Count available fields
                available_fields = {k: v for k, v in catalyst_fields.items() if v is not None}
                has_complete_data = len(available_fields) > 0
                
                self.log_test(
                    f"Individual Listing Endpoint Complete Data ({listing_id})", 
                    has_complete_data, 
                    f"Listing retrieved successfully. Available catalyst fields: {len(available_fields)}/7. Fields: {list(available_fields.keys())}"
                )
                
                # Print detailed field values
                if available_fields:
                    print("   Detailed catalyst field values:")
                    for field, value in available_fields.items():
                        print(f"     - {field}: {value}")
                
                return listing
            else:
                self.log_test(f"Individual Listing Endpoint Complete Data ({listing_id})", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test(f"Individual Listing Endpoint Complete Data ({listing_id})", False, error_msg=str(e))
            return None

    def test_backend_catalyst_data_serving(self):
        """Check if there are any backend issues preventing catalyst data from being served"""
        try:
            # Test multiple endpoints to ensure backend is serving catalyst data properly
            
            # 1. Browse endpoint
            browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            browse_success = browse_response.status_code == 200
            
            # 2. Unified calculations endpoint (admin only)
            unified_response = requests.get(f"{BACKEND_URL}/admin/catalyst/unified-calculations", timeout=10)
            unified_success = unified_response.status_code == 200
            
            # 3. Price settings endpoint
            price_response = requests.get(f"{BACKEND_URL}/admin/catalyst/price-settings", timeout=10)
            price_success = price_response.status_code == 200
            
            # Count listings with catalyst data from browse
            catalyst_listings_count = 0
            if browse_success:
                listings = browse_response.json()
                for listing in listings:
                    if self._has_catalyst_data(listing):
                        catalyst_listings_count += 1
            
            # Count catalysts from unified endpoint
            unified_catalysts_count = 0
            if unified_success:
                catalysts = unified_response.json()
                unified_catalysts_count = len(catalysts) if isinstance(catalysts, list) else 0
            
            overall_success = browse_success and unified_success and price_success and catalyst_listings_count > 0
            
            self.log_test(
                "Backend Catalyst Data Serving", 
                overall_success, 
                f"Browse endpoint: {browse_success}, Unified endpoint: {unified_success}, Price settings: {price_success}. Catalyst listings: {catalyst_listings_count}, Unified catalysts: {unified_catalysts_count}"
            )
            
            return {
                'browse_success': browse_success,
                'unified_success': unified_success,
                'price_success': price_success,
                'catalyst_listings_count': catalyst_listings_count,
                'unified_catalysts_count': unified_catalysts_count
            }
        except Exception as e:
            self.log_test("Backend Catalyst Data Serving", False, error_msg=str(e))
            return None

    def test_permission_system_admin_identification(self, admin_user):
        """Test the permission system to ensure Admin users are properly identified"""
        try:
            if not admin_user:
                self.log_test("Permission System Admin Identification", False, error_msg="No admin user provided")
                return False
            
            user_role = admin_user.get('user_role')
            user_id = admin_user.get('id')
            
            # Test the exact permission logic from frontend
            # (permissions?.userRole === 'Admin' || permissions?.userRole === 'Manager')
            is_admin = user_role == 'Admin'
            is_manager = user_role == 'Manager' or user_role == 'Admin-Manager'
            has_catalyst_permissions = is_admin or is_manager
            
            # Also test alternative permission checks
            has_permission_admin = user_role in ['Admin', 'Admin-Manager']
            
            success = has_catalyst_permissions and has_permission_admin
            
            self.log_test(
                "Permission System Admin Identification", 
                success, 
                f"User role: {user_role}, Is Admin: {is_admin}, Is Manager: {is_manager}, Has catalyst permissions: {has_catalyst_permissions}, Alternative check: {has_permission_admin}"
            )
            
            return success
        except Exception as e:
            self.log_test("Permission System Admin Identification", False, error_msg=str(e))
            return False

    def test_find_listings_with_catalyst_data(self):
        """Find listings that DO have catalyst data we can test with"""
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
                
                success = len(good_catalyst_listings) > 0
                
                self.log_test(
                    "Find Listings with Catalyst Data", 
                    success, 
                    f"Found {len(good_catalyst_listings)} listings with significant catalyst data out of {len(listings)} total listings"
                )
                
                # Print top 5 listings with best catalyst data
                if good_catalyst_listings:
                    print("   Top listings with catalyst data for testing:")
                    for i, listing in enumerate(good_catalyst_listings[:5]):
                        print(f"     {i+1}. {listing['title']} (ID: {listing['id']})")
                        print(f"        {listing['catalyst_summary']}")
                
                return good_catalyst_listings
            else:
                self.log_test("Find Listings with Catalyst Data", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Find Listings with Catalyst Data", False, error_msg=str(e))
            return []

    def test_frontend_data_structure_compatibility(self, listing):
        """Test that listing data structure is compatible with frontend expectations"""
        try:
            if not listing:
                self.log_test("Frontend Data Structure Compatibility", False, error_msg="No listing provided")
                return False
            
            # Check required fields for frontend
            required_fields = ['id', 'title', 'price', 'description', 'category']
            missing_required = [field for field in required_fields if field not in listing]
            
            # Check catalyst fields structure
            catalyst_fields = ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm', 'pt_g', 'pd_g', 'rh_g']
            available_catalyst = [field for field in catalyst_fields if listing.get(field) is not None]
            
            # Check seller information
            has_seller_info = 'seller' in listing or 'seller_id' in listing
            
            # Check bid information
            has_bid_info = 'bid_info' in listing
            
            success = len(missing_required) == 0 and len(available_catalyst) > 0
            
            self.log_test(
                "Frontend Data Structure Compatibility", 
                success, 
                f"Required fields present: {len(required_fields) - len(missing_required)}/{len(required_fields)}, Catalyst fields: {len(available_catalyst)}/{len(catalyst_fields)}, Has seller info: {has_seller_info}, Has bid info: {has_bid_info}"
            )
            
            if missing_required:
                print(f"   Missing required fields: {missing_required}")
            
            return success
        except Exception as e:
            self.log_test("Frontend Data Structure Compatibility", False, error_msg=str(e))
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

    def run_catalyst_content_verification_testing(self):
        """Run comprehensive catalyst content verification testing"""
        print("=" * 80)
        print("CATALYST CONTENT VERIFICATION TESTING - COMPLETE FLOW")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Admin Login and Permissions
        print("👤 ADMIN LOGIN AND PERMISSIONS TESTING")
        print("-" * 40)
        admin_user = self.test_admin_login_and_permissions()
        
        # 2. MazdaRF4SOK14 Specific Check
        print("🔍 MazdaRF4SOK14 SPECIFIC LISTING CHECK")
        print("-" * 40)
        mazda_listing = self.test_mazda_listing_specific_check()
        
        # 3. Individual Listing Endpoint Testing
        if mazda_listing:
            print("📊 INDIVIDUAL LISTING ENDPOINT TESTING")
            print("-" * 40)
            detailed_listing = self.test_individual_listing_endpoint_complete_data(mazda_listing.get('id'))
        else:
            detailed_listing = None
        
        # 4. Backend Catalyst Data Serving
        print("🔧 BACKEND CATALYST DATA SERVING TESTING")
        print("-" * 40)
        backend_status = self.test_backend_catalyst_data_serving()
        
        # 5. Permission System Testing
        print("🔐 PERMISSION SYSTEM TESTING")
        print("-" * 40)
        self.test_permission_system_admin_identification(admin_user)
        
        # 6. Find Alternative Listings with Catalyst Data
        print("✅ FIND ALTERNATIVE CATALYST LISTINGS")
        print("-" * 40)
        good_catalyst_listings = self.test_find_listings_with_catalyst_data()
        
        # 7. Frontend Data Structure Compatibility
        if detailed_listing:
            print("🎨 FRONTEND DATA STRUCTURE COMPATIBILITY")
            print("-" * 40)
            self.test_frontend_data_structure_compatibility(detailed_listing)
        
        # Print Summary
        print("=" * 80)
        print("CATALYST CONTENT VERIFICATION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Analysis and Recommendations
        print("🔍 ANALYSIS AND RECOMMENDATIONS:")
        print("-" * 40)
        
        if mazda_listing:
            print("✅ MazdaRF4SOK14 LISTING FOUND:")
            print(f"   - Listing ID: {mazda_listing.get('id')}")
            print(f"   - Has catalyst data: {self._has_catalyst_data(mazda_listing)}")
            print(f"   - Catalyst summary: {self._get_catalyst_summary(mazda_listing)}")
            print("   - This listing SHOULD display catalyst content sections for Admin users")
        
        if admin_user and admin_user.get('user_role') == 'Admin':
            print("✅ ADMIN PERMISSIONS WORKING:")
            print("   - Admin user login successful")
            print("   - Permission system correctly identifies Admin users")
            print("   - Frontend permission logic should work: (permissions?.userRole === 'Admin')")
        
        if backend_status and backend_status.get('catalyst_listings_count', 0) > 0:
            print("✅ BACKEND SERVING CATALYST DATA:")
            print(f"   - Found {backend_status['catalyst_listings_count']} listings with catalyst data")
            print(f"   - Unified calculations endpoint has {backend_status['unified_catalysts_count']} catalysts")
            print("   - Backend is properly serving catalyst data to frontend")
        
        if good_catalyst_listings:
            print("✅ ALTERNATIVE TEST LISTINGS AVAILABLE:")
            print(f"   - Found {len(good_catalyst_listings)} listings with good catalyst data")
            print(f"   - RECOMMENDED TEST LISTING: {good_catalyst_listings[0]['title']} (ID: {good_catalyst_listings[0]['id']})")
            print("   - These listings should display catalyst content sections for Admin users")
        
        # Final Conclusion
        print("\n🎯 FINAL CONCLUSION:")
        print("-" * 40)
        if self.failed_tests == 0:
            print("✅ ALL TESTS PASSED - CATALYST CONTENT DISPLAY SHOULD BE WORKING")
            print("   - Backend is serving catalyst data correctly")
            print("   - Admin permissions are working properly")
            print("   - Individual listing endpoints return complete data")
            print("   - If catalyst sections are not showing, it may be a frontend rendering issue")
        else:
            print("❌ SOME TESTS FAILED - ISSUES IDENTIFIED")
            print("   - Check failed tests above for specific issues")
        
        print("\n🎯 CATALYST CONTENT VERIFICATION TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results, {
            'admin_user': admin_user,
            'mazda_listing': mazda_listing,
            'backend_status': backend_status,
            'good_catalyst_listings': good_catalyst_listings
        }

if __name__ == "__main__":
    tester = CatalystContentVerificationTester()
    
    print("🎯 RUNNING CATALYST CONTENT VERIFICATION TESTING")
    print("Comprehensive verification of catalyst content display on individual listing pages...")
    print()
    
    passed, failed, results, data = tester.run_catalyst_content_verification_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)