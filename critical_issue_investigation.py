#!/usr/bin/env python3
"""
CRITICAL ISSUE INVESTIGATION - Backend Testing Script
Focus: Investigate user-reported critical issues:
1. MISSING LISTINGS: Only 1 listing shows on browse page and 2 in admin panel
2. IMAGE UPLOAD BROKEN: Picture upload not possible with "serious connection error"
"""

import requests
import json
import sys
import os
import tempfile
from datetime import datetime
from PIL import Image
import io

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://emarket-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class CriticalIssueTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Connectivity", True, f"Backend responding: {data.get('message', 'Unknown')}")
                return True
            else:
                self.log_test("Backend Connectivity", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Backend Connectivity", False, error=f"Connection error: {str(e)}")
            return False

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                user_info = data.get("user", {})
                self.log_test("Admin Authentication", True, 
                            f"Authenticated as {user_info.get('full_name', 'Unknown')} ({user_info.get('role', 'Unknown')})")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                            error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, error=f"Auth error: {str(e)}")
            return False

    def investigate_missing_listings_issue(self):
        """CRITICAL ISSUE 1: Investigate missing listings"""
        print("🔍 INVESTIGATING MISSING LISTINGS ISSUE")
        print("=" * 60)
        
        # Test 1: Check total listings count
        try:
            response = self.session.get(f"{BACKEND_URL}/listings")
            
            if response.status_code == 200:
                listings = response.json()
                total_listings = len(listings)
                self.log_test("GET /api/listings", True, 
                            f"Retrieved {total_listings} listings from database")
                
                # Show sample listing details
                if listings:
                    sample = listings[0]
                    print(f"   Sample listing: '{sample.get('title', 'Unknown')}' by {sample.get('seller_name', 'Unknown')}")
                    print(f"   Status: {sample.get('status', 'Unknown')}, Category: {sample.get('category', 'Unknown')}")
                
                return total_listings
            else:
                self.log_test("GET /api/listings", False, 
                            error=f"Status: {response.status_code}, Response: {response.text}")
                return 0
                
        except Exception as e:
            self.log_test("GET /api/listings", False, error=f"Request error: {str(e)}")
            return 0

    def check_admin_listings_view(self):
        """Check admin panel listings view"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/listings")
            
            if response.status_code == 200:
                admin_listings = response.json()
                admin_count = len(admin_listings)
                self.log_test("GET /api/admin/listings", True, 
                            f"Admin panel shows {admin_count} listings")
                
                # Show sample admin listing details
                if admin_listings:
                    sample = admin_listings[0]
                    print(f"   Sample admin listing: '{sample.get('title', 'Unknown')}' by {sample.get('seller_name', 'Unknown')}")
                    print(f"   Status: {sample.get('status', 'Unknown')}, Views: {sample.get('views', 0)}")
                
                return admin_count
            else:
                self.log_test("GET /api/admin/listings", False, 
                            error=f"Status: {response.status_code}, Response: {response.text}")
                return 0
                
        except Exception as e:
            self.log_test("GET /api/admin/listings", False, error=f"Request error: {str(e)}")
            return 0

    def check_listings_count_endpoint(self):
        """Check listings count endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/listings/count")
            
            if response.status_code == 200:
                data = response.json()
                count = data.get("total_count", 0)
                self.log_test("GET /api/listings/count", True, 
                            f"Count endpoint reports {count} active listings")
                return count
            else:
                self.log_test("GET /api/listings/count", False, 
                            error=f"Status: {response.status_code}, Response: {response.text}")
                return 0
                
        except Exception as e:
            self.log_test("GET /api/listings/count", False, error=f"Request error: {str(e)}")
            return 0

    def create_test_png_image(self):
        """Create a test PNG image for upload testing"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes.getvalue()
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None

    def investigate_image_upload_issue(self):
        """CRITICAL ISSUE 2: Investigate image upload problems"""
        print("🔍 INVESTIGATING IMAGE UPLOAD ISSUE")
        print("=" * 60)
        
        # Test 1: Listing image upload
        self.test_listing_image_upload()
        
        # Test 2: Logo upload
        self.test_logo_upload()

    def test_listing_image_upload(self):
        """Test POST /api/listings/upload-image"""
        try:
            # Create test PNG image
            test_image_data = self.create_test_png_image()
            if not test_image_data:
                self.log_test("POST /api/listings/upload-image", False, 
                            error="Failed to create test image")
                return False
            
            # Prepare file upload
            files = {
                'file': ('test_image.png', test_image_data, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/listings/upload-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("image_url", "")
                self.log_test("POST /api/listings/upload-image", True, 
                            f"Image uploaded successfully: {image_url}")
                
                # Test if uploaded image is accessible
                if image_url:
                    self.test_image_accessibility(image_url)
                
                return True
            else:
                self.log_test("POST /api/listings/upload-image", False, 
                            error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/listings/upload-image", False, 
                        error=f"Upload error: {str(e)}")
            return False

    def test_logo_upload(self):
        """Test POST /api/admin/cms/upload-logo"""
        try:
            # Create test PNG image
            test_image_data = self.create_test_png_image()
            if not test_image_data:
                self.log_test("POST /api/admin/cms/upload-logo", False, 
                            error="Failed to create test image")
                return False
            
            # Prepare file upload
            files = {
                'file': ('test_logo.png', test_image_data, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-logo", files=files)
            
            if response.status_code == 200:
                data = response.json()
                logo_url = data.get("logo_url", "")
                self.log_test("POST /api/admin/cms/upload-logo", True, 
                            f"Logo uploaded successfully: {logo_url}")
                
                # Test if uploaded logo is accessible
                if logo_url:
                    self.test_image_accessibility(logo_url)
                
                return True
            else:
                self.log_test("POST /api/admin/cms/upload-logo", False, 
                            error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/admin/cms/upload-logo", False, 
                        error=f"Upload error: {str(e)}")
            return False

    def test_image_accessibility(self, image_url):
        """Test if uploaded image is accessible via HTTP"""
        try:
            # Convert relative URL to full URL if needed
            if image_url.startswith('/'):
                full_url = f"https://emarket-fix.preview.emergentagent.com{image_url}"
            else:
                full_url = image_url
            
            response = self.session.get(full_url)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                self.log_test("Image Accessibility", True, 
                            f"Image accessible: {content_type}, {content_length} bytes")
                return True
            else:
                self.log_test("Image Accessibility", False, 
                            error=f"Image not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Image Accessibility", False, 
                        error=f"Accessibility test error: {str(e)}")
            return False

    def check_database_connectivity(self):
        """Check if there are database connectivity issues"""
        print("🔍 CHECKING DATABASE CONNECTIVITY")
        print("=" * 60)
        
        # Test various endpoints that require database access
        endpoints_to_test = [
            ("/admin/stats", "Admin Statistics"),
            ("/admin/users", "User Management"),
            ("/categories", "Categories List"),
            ("/cms/settings", "CMS Settings")
        ]
        
        db_issues = 0
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Database Access - {description}", True, 
                                f"Endpoint responding with data")
                else:
                    self.log_test(f"Database Access - {description}", False, 
                                error=f"Status: {response.status_code}")
                    db_issues += 1
                    
            except Exception as e:
                self.log_test(f"Database Access - {description}", False, 
                            error=f"Request error: {str(e)}")
                db_issues += 1
        
        return db_issues == 0

    def run_critical_investigation(self):
        """Run complete critical issue investigation"""
        print("🚨 CRITICAL ISSUE INVESTIGATION")
        print("=" * 80)
        print("Investigating user-reported critical issues:")
        print("1. MISSING LISTINGS: Only 1 listing shows on browse page and 2 in admin panel")
        print("2. IMAGE UPLOAD BROKEN: Picture upload not possible with 'serious connection error'")
        print("=" * 80)
        print()
        
        # Step 1: Test basic connectivity
        if not self.test_backend_connectivity():
            print("❌ Backend connectivity failed. Cannot proceed with investigation.")
            return False
        
        # Step 2: Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with investigation.")
            return False
        
        # Step 3: Investigate missing listings issue
        public_listings_count = self.investigate_missing_listings_issue()
        admin_listings_count = self.check_admin_listings_view()
        count_endpoint_result = self.check_listings_count_endpoint()
        
        # Step 4: Investigate image upload issue
        self.investigate_image_upload_issue()
        
        # Step 5: Check database connectivity
        db_healthy = self.check_database_connectivity()
        
        # Step 6: Analysis and Summary
        print("🔍 CRITICAL ISSUE ANALYSIS")
        print("=" * 80)
        
        # Analyze listings issue
        print("LISTINGS ISSUE ANALYSIS:")
        print(f"   Public listings endpoint: {public_listings_count} listings")
        print(f"   Admin listings endpoint: {admin_listings_count} listings")
        print(f"   Count endpoint result: {count_endpoint_result} listings")
        
        if public_listings_count == admin_listings_count == count_endpoint_result:
            if public_listings_count <= 2:
                print("   🚨 CONFIRMED: Very few listings in database - this explains user's issue")
                print("   🔍 ROOT CAUSE: Database may have lost listings or listings were deleted")
            else:
                print("   ✅ All endpoints show consistent listing counts")
        else:
            print("   🚨 INCONSISTENCY: Different endpoints showing different counts")
            print("   🔍 ROOT CAUSE: Possible data synchronization or filtering issues")
        
        print()
        
        # Database health
        if not db_healthy:
            print("🚨 DATABASE CONNECTIVITY ISSUES DETECTED")
            print("   This could explain both missing listings and upload failures")
        else:
            print("✅ Database connectivity appears healthy")
        
        print()
        
        # Summary
        print("=" * 80)
        print("INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Critical findings
        critical_issues = []
        
        if public_listings_count <= 2:
            critical_issues.append("MISSING LISTINGS: Very few listings in database")
        
        if failed_tests > 0:
            failed_tests_list = [result['test'] for result in self.test_results if not result['success']]
            if any('upload' in test.lower() for test in failed_tests_list):
                critical_issues.append("IMAGE UPLOAD: Upload functionality failing")
        
        if not db_healthy:
            critical_issues.append("DATABASE: Connectivity issues detected")
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES CONFIRMED:")
            for issue in critical_issues:
                print(f"   • {issue}")
        else:
            print("✅ No critical issues detected in backend")
        
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['error']}")
            print()
        
        return len(critical_issues) == 0

if __name__ == "__main__":
    tester = CriticalIssueTester()
    success = tester.run_critical_investigation()
    
    if success:
        print("✅ Investigation complete - no critical backend issues found")
        sys.exit(0)
    else:
        print("🚨 Investigation complete - critical issues confirmed")
        sys.exit(1)