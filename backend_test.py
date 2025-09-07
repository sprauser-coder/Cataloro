#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - MazdaRF4SOK14 Listing and Admin Authentication Testing
Testing the specific individual listing endpoint for MazdaRF4SOK14 listing and admin login functionality
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://catalyst-unified.preview.emergentagent.com/api"

# Specific listing ID to test as requested in review
MAZDA_LISTING_ID = "6b7961e7-3191-4a3b-84cb-cdcbe74a6ea3"

class BackendTester:
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

    def test_admin_authentication(self):
        """Test admin login functionality to ensure it works properly"""
        try:
            # Test admin login with correct credentials
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
                username = user.get('username')
                
                # Verify admin user details
                is_admin = user_role in ['Admin', 'Admin-Manager']
                has_token = 'token' in data
                
                self.log_test(
                    "Admin Authentication", 
                    is_admin and has_token, 
                    f"Admin login successful. Username: {username}, Role: {user_role}, User ID: {user_id}, Token provided: {has_token}"
                )
                return user if is_admin else None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Admin Authentication", False, error_msg=f"Login failed: {error_detail}")
                return None
        except Exception as e:
            self.log_test("Admin Authentication", False, error_msg=str(e))
            return None

    def test_mazda_listing_endpoint(self):
        """Test the specific MazdaRF4SOK14 listing endpoint to verify it returns listing data with catalyst content fields"""
        try:
            # First, check if the listing exists in browse endpoint
            browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            mazda_listing_found = False
            mazda_listing_data = None
            
            if browse_response.status_code == 200:
                listings = browse_response.json()
                for listing in listings:
                    if listing.get('id') == MAZDA_LISTING_ID:
                        mazda_listing_found = True
                        mazda_listing_data = listing
                        break
            
            if not mazda_listing_found:
                self.log_test(
                    "MazdaRF4SOK14 Listing Endpoint", 
                    False, 
                    error_msg=f"MazdaRF4SOK14 listing with ID {MAZDA_LISTING_ID} not found in browse endpoint"
                )
                return None
            
            # Test the individual listing endpoint
            response = requests.get(f"{BACKEND_URL}/listings/{MAZDA_LISTING_ID}", timeout=10)
            
            if response.status_code == 200:
                listing_data = response.json()
                
                # Check for catalyst content fields
                catalyst_fields = {
                    'ceramic_weight': listing_data.get('ceramic_weight'),
                    'pt_ppm': listing_data.get('pt_ppm'),
                    'pd_ppm': listing_data.get('pd_ppm'),
                    'rh_ppm': listing_data.get('rh_ppm'),
                    'pt_g': listing_data.get('pt_g'),
                    'pd_g': listing_data.get('pd_g'),
                    'rh_g': listing_data.get('rh_g')
                }
                
                # Count available catalyst fields
                available_fields = {k: v for k, v in catalyst_fields.items() if v is not None}
                has_catalyst_data = len(available_fields) > 0
                
                # Get basic listing info
                title = listing_data.get('title', 'Unknown')
                price = listing_data.get('price', 0)
                
                self.log_test(
                    "MazdaRF4SOK14 Listing Endpoint", 
                    has_catalyst_data, 
                    f"Listing found: {title} (€{price}). Catalyst fields available: {len(available_fields)}/7. Fields: {list(available_fields.keys())}"
                )
                
                # Print detailed catalyst data for verification
                if available_fields:
                    print("   Catalyst Content Fields:")
                    for field, value in available_fields.items():
                        print(f"     - {field}: {value}")
                
                return listing_data if has_catalyst_data else None
            else:
                self.log_test(
                    "MazdaRF4SOK14 Listing Endpoint", 
                    False, 
                    error_msg=f"Individual listing endpoint failed: HTTP {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_test("MazdaRF4SOK14 Listing Endpoint", False, error_msg=str(e))
            return None

    def test_catalyst_data_structure_compatibility(self, listing_data):
        """Test that the listing data structure is compatible with frontend expectations"""
        if not listing_data:
            self.log_test("Catalyst Data Structure Compatibility", False, error_msg="No listing data provided")
            return False
            
        try:
            # Check required fields for frontend compatibility
            required_fields = ['id', 'title', 'description', 'price', 'seller_id']
            catalyst_fields = ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm', 'pt_g', 'pd_g', 'rh_g']
            
            # Check required fields
            missing_required = [field for field in required_fields if field not in listing_data]
            
            # Check catalyst fields availability
            available_catalyst_fields = [field for field in catalyst_fields if listing_data.get(field) is not None]
            
            # Check seller information (should be enriched by browse endpoint)
            has_seller_info = 'seller' in listing_data or 'seller_id' in listing_data
            
            success = len(missing_required) == 0 and len(available_catalyst_fields) > 0
            
            self.log_test(
                "Catalyst Data Structure Compatibility", 
                success, 
                f"Required fields present: {len(required_fields) - len(missing_required)}/{len(required_fields)}, "
                f"Catalyst fields available: {len(available_catalyst_fields)}/{len(catalyst_fields)}, "
                f"Seller info present: {has_seller_info}"
            )
            
            if missing_required:
                print(f"   Missing required fields: {missing_required}")
            
            return success
            
        except Exception as e:
            self.log_test("Catalyst Data Structure Compatibility", False, error_msg=str(e))
            return False

    def test_admin_permissions_for_catalyst_content(self, admin_user):
        """Test that admin user has proper permissions to view catalyst content"""
        if not admin_user:
            self.log_test("Admin Permissions for Catalyst Content", False, error_msg="No admin user provided")
            return False
            
        try:
            user_role = admin_user.get('user_role')
            
            # Test permission logic that would be used in frontend
            has_admin_permissions = user_role in ['Admin', 'Admin-Manager']
            
            # Test alternative permission check (Admin-Manager mapped to Manager)
            mapped_role = 'Manager' if user_role == 'Admin-Manager' else user_role
            alternative_permission = mapped_role in ['Admin', 'Manager']
            
            success = has_admin_permissions or alternative_permission
            
            self.log_test(
                "Admin Permissions for Catalyst Content", 
                success, 
                f"User role: {user_role}, Has admin permissions: {has_admin_permissions}, Alternative check: {alternative_permission}"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Admin Permissions for Catalyst Content", False, error_msg=str(e))
            return False

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}, Version: {data.get('version')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def test_admin_login_and_permissions(self):
        """Test admin login and verify permissions for catalyst content visibility"""
        try:
            # Login as admin
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

    def test_listings_with_catalyst_data(self):
        """Test that backend provides listings with complete catalyst field data"""
        try:
            # Get all listings from browse endpoint
            response = requests.get(f"{BACKEND_URL}/marketplace/browse", timeout=10)
            
            if response.status_code == 200:
                listings = response.json()
                
                if isinstance(listings, list):
                    # Find listings with catalyst data
                    catalyst_listings = []
                    for listing in listings:
                        has_catalyst_fields = any([
                            listing.get('ceramic_weight'),
                            listing.get('pt_ppm'),
                            listing.get('pd_ppm'), 
                            listing.get('rh_ppm'),
                            listing.get('pt_g'),
                            listing.get('pd_g'),
                            listing.get('rh_g')
                        ])
                        
                        if has_catalyst_fields:
                            catalyst_listings.append({
                                'id': listing.get('id'),
                                'title': listing.get('title'),
                                'ceramic_weight': listing.get('ceramic_weight'),
                                'pt_ppm': listing.get('pt_ppm'),
                                'pd_ppm': listing.get('pd_ppm'),
                                'rh_ppm': listing.get('rh_ppm'),
                                'pt_g': listing.get('pt_g'),
                                'pd_g': listing.get('pd_g'),
                                'rh_g': listing.get('rh_g')
                            })
                    
                    success = len(catalyst_listings) > 0
                    
                    self.log_test(
                        "Listings with Catalyst Data", 
                        success, 
                        f"Found {len(catalyst_listings)} listings with catalyst data out of {len(listings)} total listings"
                    )
                    
                    return catalyst_listings if success else []
                else:
                    self.log_test("Listings with Catalyst Data", False, error_msg="Browse endpoint returned invalid format")
                    return []
            else:
                self.log_test("Listings with Catalyst Data", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Listings with Catalyst Data", False, error_msg=str(e))
            return []

    def test_individual_listing_catalyst_display(self, catalyst_listings):
        """Test individual listing pages display catalyst content properly"""
        if not catalyst_listings:
            self.log_test("Individual Listing Catalyst Display", False, error_msg="No catalyst listings provided for testing")
            return False
            
        try:
            # Test first few catalyst listings
            tested_listings = 0
            successful_displays = 0
            
            for listing in catalyst_listings[:3]:  # Test first 3 catalyst listings
                listing_id = listing.get('id')
                if not listing_id:
                    continue
                    
                # Get individual listing details
                response = requests.get(f"{BACKEND_URL}/listings/{listing_id}", timeout=10)
                
                if response.status_code == 200:
                    listing_detail = response.json()
                    tested_listings += 1
                    
                    # Check if catalyst fields are present for admin display
                    catalyst_fields_present = {
                        'ceramic_weight': listing_detail.get('ceramic_weight'),
                        'pt_ppm': listing_detail.get('pt_ppm'),
                        'pd_ppm': listing_detail.get('pd_ppm'),
                        'rh_ppm': listing_detail.get('rh_ppm'),
                        'pt_g': listing_detail.get('pt_g'),
                        'pd_g': listing_detail.get('pd_g'),
                        'rh_g': listing_detail.get('rh_g')
                    }
                    
                    # Count non-null catalyst fields
                    available_fields = {k: v for k, v in catalyst_fields_present.items() if v is not None}
                    
                    if len(available_fields) > 0:
                        successful_displays += 1
                        print(f"   Listing {listing_id}: {len(available_fields)} catalyst fields available")
                        for field, value in available_fields.items():
                            print(f"     - {field}: {value}")
                    else:
                        print(f"   Listing {listing_id}: No catalyst fields available")
                else:
                    print(f"   Failed to get listing {listing_id}: HTTP {response.status_code}")
            
            success = successful_displays > 0 and tested_listings > 0
            
            self.log_test(
                "Individual Listing Catalyst Display", 
                success, 
                f"Tested {tested_listings} listings, {successful_displays} have catalyst data for admin display"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Individual Listing Catalyst Display", False, error_msg=str(e))
            return False

    def test_catalyst_calculations_section_data(self, catalyst_listings):
        """Test that catalyst calculations section has proper data (Pt g, Pd g, Rh g)"""
        if not catalyst_listings:
            self.log_test("Catalyst Calculations Section Data", False, error_msg="No catalyst listings provided for testing")
            return False
            
        try:
            # Check if we have listings with calculated values or raw data for calculations
            listings_with_calculations = 0
            listings_with_raw_data = 0
            
            for listing in catalyst_listings[:5]:  # Test first 5 catalyst listings
                # Check for pre-calculated values (pt_g, pd_g, rh_g)
                has_calculated_values = any([
                    listing.get('pt_g') is not None,
                    listing.get('pd_g') is not None,
                    listing.get('rh_g') is not None
                ])
                
                # Check for raw data that can be used for calculations
                has_raw_data = all([
                    listing.get('ceramic_weight') is not None,
                    any([
                        listing.get('pt_ppm') is not None,
                        listing.get('pd_ppm') is not None,
                        listing.get('rh_ppm') is not None
                    ])
                ])
                
                if has_calculated_values:
                    listings_with_calculations += 1
                    print(f"   Listing {listing.get('id')}: Has calculated values - Pt: {listing.get('pt_g')}, Pd: {listing.get('pd_g')}, Rh: {listing.get('rh_g')}")
                
                if has_raw_data:
                    listings_with_raw_data += 1
                    print(f"   Listing {listing.get('id')}: Has raw data - Weight: {listing.get('ceramic_weight')}g, Pt ppm: {listing.get('pt_ppm')}, Pd ppm: {listing.get('pd_ppm')}, Rh ppm: {listing.get('rh_ppm')}")
            
            # Success if we have either calculated values or raw data for calculations
            success = listings_with_calculations > 0 or listings_with_raw_data > 0
            
            self.log_test(
                "Catalyst Calculations Section Data", 
                success, 
                f"Found {listings_with_calculations} listings with calculated values, {listings_with_raw_data} listings with raw calculation data"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Catalyst Calculations Section Data", False, error_msg=str(e))
            return False

    def test_permission_logic_verification(self, admin_user):
        """Test that permission checks work correctly for catalyst content visibility"""
        if not admin_user:
            self.log_test("Permission Logic Verification", False, error_msg="No admin user provided for testing")
            return False
            
        try:
            # Test admin user permissions
            user_role = admin_user.get('user_role')
            user_id = admin_user.get('id')
            
            # Verify the role matches expected admin/manager roles
            expected_roles = ['Admin', 'Admin-Manager']
            has_correct_role = user_role in expected_roles
            
            # Test that the permission logic would work
            # This simulates the frontend logic: (permissions?.userRole === 'Admin' || permissions?.userRole === 'Manager')
            frontend_permission_check = user_role == 'Admin' or user_role == 'Manager'
            
            # Also test the alternative role mapping (Admin-Manager -> Manager)
            mapped_role = 'Manager' if user_role == 'Admin-Manager' else user_role
            alternative_check = mapped_role == 'Admin' or mapped_role == 'Manager'
            
            success = has_correct_role and (frontend_permission_check or alternative_check)
            
            self.log_test(
                "Permission Logic Verification", 
                success, 
                f"User role: {user_role}, Expected roles: {expected_roles}, Frontend check: {frontend_permission_check}, Alternative check: {alternative_check}"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Permission Logic Verification", False, error_msg=str(e))
            return False

    def test_create_catalyst_listing_for_testing(self, admin_user):
        """Create a test listing with catalyst data to verify individual page display"""
        if not admin_user:
            self.log_test("Create Catalyst Listing for Testing", False, error_msg="No admin user provided")
            return None
            
        try:
            # Create a test listing with comprehensive catalyst data
            test_listing_data = {
                "title": "Test Catalyst Converter - Individual Page Display Test",
                "description": "Professional grade catalyst converter for testing individual listing page catalyst content display functionality. This listing contains comprehensive catalyst data for Admin/Manager visibility testing.",
                "price": 299.99,
                "category": "Catalysts",
                "condition": "New",
                "seller_id": admin_user.get('id'),
                "images": [],
                "tags": ["catalyst", "test", "admin-display"],
                "features": ["Professional Grade", "Admin Testing"],
                # Catalyst database fields (raw values)
                "ceramic_weight": 145.8,
                "pt_ppm": 1250.0,
                "pd_ppm": 890.0,
                "rh_ppm": 125.0,
                # Pre-calculated content values (if supported)
                "pt_g": 0.7854,
                "pd_g": 0.5592,
                "rh_g": 0.0785
            }
            
            response = requests.post(
                f"{BACKEND_URL}/listings",
                json=test_listing_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                listing_id = result.get('listing_id')
                
                # Verify the listing was created with catalyst data
                verify_response = requests.get(f"{BACKEND_URL}/listings/{listing_id}")
                if verify_response.status_code == 200:
                    created_listing = verify_response.json()
                    
                    # Check that all catalyst fields are present
                    catalyst_fields = ['ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm']
                    content_fields = ['pt_g', 'pd_g', 'rh_g']
                    
                    catalyst_fields_present = all(field in created_listing for field in catalyst_fields)
                    content_fields_present = any(field in created_listing for field in content_fields)
                    
                    success = catalyst_fields_present
                    
                    self.log_test(
                        "Create Catalyst Listing for Testing", 
                        success, 
                        f"Created test listing {listing_id} with catalyst fields: {catalyst_fields_present}, content fields: {content_fields_present}"
                    )
                    
                    return {
                        'listing_id': listing_id,
                        'listing_data': created_listing,
                        'has_catalyst_fields': catalyst_fields_present,
                        'has_content_fields': content_fields_present
                    }
                else:
                    self.log_test("Create Catalyst Listing for Testing", False, error_msg="Failed to verify created listing")
                    return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Catalyst Listing for Testing", False, error_msg=error_detail)
                return None
                
        except Exception as e:
            self.log_test("Create Catalyst Listing for Testing", False, error_msg=str(e))
            return None

    def cleanup_test_listing(self, test_listing):
        """Clean up test listing after testing"""
        if test_listing and test_listing.get('listing_id'):
            try:
                requests.delete(f"{BACKEND_URL}/listings/{test_listing['listing_id']}")
                print(f"   Cleaned up test listing {test_listing['listing_id']}")
            except:
                pass

    def run_mazda_listing_and_admin_testing(self):
        """Run MazdaRF4SOK14 listing and admin authentication testing as requested in review"""
        print("=" * 80)
        print("CATALORO MAZDA RF4SOK14 LISTING AND ADMIN AUTHENTICATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Target Listing ID: {MAZDA_LISTING_ID}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting testing.")
            return
        
        # 2. Test Admin Authentication
        print("👤 ADMIN AUTHENTICATION TESTING")
        print("-" * 40)
        admin_user = self.test_admin_authentication()
        
        # 3. Test MazdaRF4SOK14 Listing Endpoint
        print("🚗 MAZDA RF4SOK14 LISTING ENDPOINT TESTING")
        print("-" * 40)
        mazda_listing = self.test_mazda_listing_endpoint()
        
        # 4. Test Catalyst Data Structure Compatibility
        print("📊 CATALYST DATA STRUCTURE COMPATIBILITY TESTING")
        print("-" * 40)
        self.test_catalyst_data_structure_compatibility(mazda_listing)
        
        # 5. Test Admin Permissions for Catalyst Content
        print("🔐 ADMIN PERMISSIONS FOR CATALYST CONTENT TESTING")
        print("-" * 40)
        self.test_admin_permissions_for_catalyst_content(admin_user)
        
        # Print Summary
        print("=" * 80)
        print("MAZDA RF4SOK14 LISTING AND ADMIN AUTHENTICATION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 MAZDA RF4SOK14 LISTING AND ADMIN AUTHENTICATION TESTING COMPLETE")
        print("Expected Results:")
        print("  ✅ Admin login works properly with correct credentials")
        print("  ✅ MazdaRF4SOK14 listing endpoint returns listing data")
        print("  ✅ Listing contains catalyst content fields for admin users")
        print("  ✅ Data structure is compatible with frontend expectations")
        print("  ✅ Admin user has proper permissions for catalyst content")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    
    # Run MazdaRF4SOK14 listing and admin authentication testing as requested in the review
    print("🎯 RUNNING MAZDA RF4SOK14 LISTING AND ADMIN AUTHENTICATION TESTING AS REQUESTED")
    print("Testing the specific individual listing endpoint for MazdaRF4SOK14 listing and admin login functionality...")
    print()
    
    passed, failed, results = tester.run_mazda_listing_and_admin_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)