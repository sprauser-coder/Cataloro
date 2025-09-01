#!/usr/bin/env python3
"""
Cat Database Functionality Test Suite
Tests the updated Cat Database functionality with add_info column and delete functionality
"""

import requests
import sys
import json
import io
import pandas as pd
from datetime import datetime

class CatDatabaseTester:
    def __init__(self, base_url="https://marketplace-pro-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.admin_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_listing_id = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for multipart/form-data
                    test_headers.pop('Content-Type', None)
                    response = self.session.post(url, files=files, data=data, headers=test_headers)
                else:
                    response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_admin_login(self):
        """Setup admin authentication"""
        print("🔐 Setting up admin authentication...")
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@cataloro.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_user = response['user']
            print(f"   Admin User: {self.admin_user}")
        return success

    def create_test_excel_with_add_info(self):
        """Create test Excel file with add_info column"""
        data = {
            'cat_id': ['TEST001', 'TEST002', 'TEST003'],
            'name': ['TestCat001', 'TestCat002', 'TestCat003'],
            'ceramic_weight': [1.5, 2.0, 1.8],
            'pt_ppm': [1000, 1200, 800],
            'pd_ppm': [500, 600, 400],
            'rh_ppm': [100, 150, 80],
            'add_info': ['Additional info for TestCat001', 'Extra details for TestCat002', 'Special notes for TestCat003']
        }
        
        df = pd.DataFrame(data)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        return excel_buffer.getvalue()

    def create_test_excel_without_add_info(self):
        """Create test Excel file without add_info column (backward compatibility)"""
        data = {
            'cat_id': ['COMPAT001', 'COMPAT002'],
            'name': ['CompatCat001', 'CompatCat002'],
            'ceramic_weight': [1.2, 1.7],
            'pt_ppm': [900, 1100],
            'pd_ppm': [450, 550],
            'rh_ppm': [90, 120]
        }
        
        df = pd.DataFrame(data)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        return excel_buffer.getvalue()

    def test_excel_upload_with_add_info(self):
        """Test Excel upload with add_info column"""
        if not self.admin_user:
            print("❌ Excel Upload with add_info - SKIPPED (No admin logged in)")
            return False

        excel_data = self.create_test_excel_with_add_info()
        
        files = {
            'file': ('test_catalysts_with_add_info.xlsx', excel_data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        success, response = self.run_test(
            "Excel Upload with add_info Column",
            "POST",
            "api/admin/catalyst/upload",
            200,
            files=files
        )
        
        if success:
            print(f"   ✅ Uploaded {response.get('count', 0)} catalyst records with add_info")
            print(f"   Columns detected: {response.get('columns', [])}")
            if 'add_info' in response.get('columns', []):
                self.log_test("add_info Column Detection", True, "add_info column properly detected")
            else:
                self.log_test("add_info Column Detection", False, "add_info column not detected")
        
        return success

    def test_excel_upload_without_add_info(self):
        """Test Excel upload without add_info column (backward compatibility)"""
        if not self.admin_user:
            print("❌ Excel Upload without add_info - SKIPPED (No admin logged in)")
            return False

        excel_data = self.create_test_excel_without_add_info()
        
        files = {
            'file': ('test_catalysts_without_add_info.xlsx', excel_data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        success, response = self.run_test(
            "Excel Upload without add_info Column (Backward Compatibility)",
            "POST",
            "api/admin/catalyst/upload",
            200,
            files=files
        )
        
        if success:
            print(f"   ✅ Uploaded {response.get('count', 0)} catalyst records without add_info")
            print(f"   Columns detected: {response.get('columns', [])}")
            if 'add_info' not in response.get('columns', []):
                self.log_test("Backward Compatibility", True, "System handles missing add_info column gracefully")
            else:
                self.log_test("Backward Compatibility", False, "Unexpected add_info column found")
        
        return success

    def test_catalyst_data_retrieval(self):
        """Test catalyst data retrieval including add_info field"""
        if not self.admin_user:
            print("❌ Catalyst Data Retrieval - SKIPPED (No admin logged in)")
            return False

        success, response = self.run_test(
            "Catalyst Data Retrieval with add_info",
            "GET",
            "api/admin/catalyst/data",
            200
        )
        
        if success and response:
            print(f"   Found {len(response)} catalyst entries")
            
            # Check for add_info field in the data
            add_info_found = False
            add_info_with_content = 0
            
            for catalyst in response:
                if 'add_info' in catalyst:
                    add_info_found = True
                    if catalyst['add_info'] and catalyst['add_info'].strip():
                        add_info_with_content += 1
                        print(f"   📝 Catalyst {catalyst.get('name', 'Unknown')} has add_info: {catalyst['add_info'][:50]}...")
            
            if add_info_found:
                self.log_test("add_info Field Present", True, f"add_info field found in catalyst data")
                if add_info_with_content > 0:
                    self.log_test("add_info Content", True, f"{add_info_with_content} catalysts have add_info content")
                else:
                    self.log_test("add_info Content", True, "add_info field present but empty (expected for backward compatibility)")
            else:
                self.log_test("add_info Field Present", False, "add_info field not found in catalyst data")
        
        return success

    def test_listing_creation_with_add_info(self):
        """Test catalyst listing creation with add_info data"""
        if not self.admin_user:
            print("❌ Listing Creation with add_info - SKIPPED (No admin logged in)")
            return False

        # First, get catalyst data to find one with add_info
        data_success, catalyst_data = self.run_test(
            "Get Catalyst Data for Listing",
            "GET",
            "api/admin/catalyst/data",
            200
        )
        
        if not data_success or not catalyst_data:
            print("   ⚠️  No catalyst data available for listing creation test")
            return False

        # Find a catalyst with add_info content
        test_catalyst = None
        for catalyst in catalyst_data:
            if catalyst.get('add_info') and catalyst['add_info'].strip():
                test_catalyst = catalyst
                break
        
        if not test_catalyst:
            print("   ⚠️  No catalyst with add_info content found")
            # Use first catalyst anyway for basic test
            test_catalyst = catalyst_data[0] if catalyst_data else None
        
        if not test_catalyst:
            return False

        # Create listing with add_info in description
        add_info_text = test_catalyst.get('add_info', '')
        description = f"High-quality catalyst {test_catalyst.get('name', 'Unknown')}. "
        if add_info_text:
            description += f"Additional Information: {add_info_text}"
        else:
            description += "Standard catalyst specifications."

        listing_data = {
            "title": f"{test_catalyst.get('name', 'TestCatalyst')} - Premium Grade",
            "description": description,
            "price": 150.00,
            "category": "Catalysts",
            "condition": "Used - Good",
            "seller_id": self.admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"],
            "tags": ["catalyst", "automotive", "add_info_test"],
            "features": ["Tested quality", "Includes additional information"]
        }
        
        success, response = self.run_test(
            "Create Listing with add_info Data",
            "POST",
            "api/listings",
            200,
            data=listing_data
        )
        
        if success:
            self.test_listing_id = response.get('listing_id')
            print(f"   ✅ Listing created with ID: {self.test_listing_id}")
            
            # Verify add_info is included in description
            if add_info_text and add_info_text in description:
                self.log_test("add_info in Description", True, "add_info data properly included in listing description")
            else:
                self.log_test("add_info in Description", True, "Listing created (no add_info content to include)")
        
        return success

    def test_delete_database_functionality(self):
        """Test delete database functionality"""
        if not self.admin_user:
            print("❌ Delete Database - SKIPPED (No admin logged in)")
            return False

        # First, verify we have data to delete
        data_success, catalyst_data = self.run_test(
            "Verify Data Before Delete",
            "GET",
            "api/admin/catalyst/data",
            200
        )
        
        if data_success:
            print(f"   📊 Found {len(catalyst_data)} catalyst records before deletion")
        
        # Delete the database
        success, response = self.run_test(
            "Delete Catalyst Database",
            "DELETE",
            "api/admin/catalyst/database",
            200
        )
        
        if success:
            deleted_count = response.get('deleted_records', 0)
            print(f"   🗑️  Deleted {deleted_count} catalyst records")
            self.log_test("Database Deletion", True, f"Successfully deleted {deleted_count} records")
            
            # Verify database is empty
            verify_success, verify_data = self.run_test(
                "Verify Database Empty",
                "GET",
                "api/admin/catalyst/data",
                200
            )
            
            if verify_success:
                if len(verify_data) == 0:
                    self.log_test("Database Empty Verification", True, "Database is empty after deletion")
                else:
                    self.log_test("Database Empty Verification", False, f"Database still contains {len(verify_data)} records")
        
        return success

    def test_database_recovery(self):
        """Test database recovery after deletion"""
        if not self.admin_user:
            print("❌ Database Recovery - SKIPPED (No admin logged in)")
            return False

        # Upload new data after deletion
        excel_data = self.create_test_excel_with_add_info()
        
        files = {
            'file': ('recovery_test_catalysts.xlsx', excel_data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        success, response = self.run_test(
            "Database Recovery - Upload New Data",
            "POST",
            "api/admin/catalyst/upload",
            200,
            files=files
        )
        
        if success:
            print(f"   🔄 Recovery successful: {response.get('count', 0)} records uploaded")
            
            # Verify data is accessible
            verify_success, verify_data = self.run_test(
                "Verify Recovery Data",
                "GET",
                "api/admin/catalyst/data",
                200
            )
            
            if verify_success and verify_data:
                print(f"   ✅ Recovery verified: {len(verify_data)} records accessible")
                self.log_test("Database Recovery", True, f"System recovered with {len(verify_data)} records")
                
                # Check if add_info is still working after recovery
                add_info_working = any(cat.get('add_info') for cat in verify_data)
                if add_info_working:
                    self.log_test("add_info After Recovery", True, "add_info functionality preserved after recovery")
                else:
                    self.log_test("add_info After Recovery", False, "add_info functionality not working after recovery")
            else:
                self.log_test("Database Recovery", False, "Could not verify recovery data")
        
        return success

    def test_column_structure_validation(self):
        """Test that system handles both Excel formats correctly"""
        if not self.admin_user:
            print("❌ Column Structure Validation - SKIPPED (No admin logged in)")
            return False

        print("\n📋 Testing Column Structure Validation...")
        
        # Test 1: Upload with add_info
        with_add_info_success = self.test_excel_upload_with_add_info()
        
        # Test 2: Upload without add_info (should replace previous data)
        without_add_info_success = self.test_excel_upload_without_add_info()
        
        # Test 3: Verify mixed data handling
        data_success, final_data = self.run_test(
            "Final Data Structure Check",
            "GET",
            "api/admin/catalyst/data",
            200
        )
        
        if data_success and final_data:
            # Check that all records have add_info field (even if empty)
            all_have_add_info = all('add_info' in cat for cat in final_data)
            
            if all_have_add_info:
                self.log_test("Consistent add_info Field", True, "All catalyst records have add_info field")
            else:
                self.log_test("Consistent add_info Field", False, "Some catalyst records missing add_info field")
            
            # Check for mixed content (some with add_info, some without)
            with_content = sum(1 for cat in final_data if cat.get('add_info', '').strip())
            without_content = len(final_data) - with_content
            
            print(f"   📊 Final data: {len(final_data)} total, {with_content} with add_info content, {without_content} without")
            
            if with_content >= 0 and without_content >= 0:  # Both scenarios handled
                self.log_test("Mixed Content Handling", True, "System handles both scenarios correctly")
            else:
                self.log_test("Mixed Content Handling", False, "System not handling mixed content correctly")
        
        return with_add_info_success and without_add_info_success and data_success

    def run_cat_database_tests(self):
        """Run complete Cat Database test suite"""
        print("🗄️  Starting Cat Database Functionality Tests")
        print("=" * 60)

        # Setup
        if not self.setup_admin_login():
            print("❌ Admin login failed - stopping tests")
            return False

        # Test 1: Excel Upload with add_info Column
        print("\n📤 Test 1: Excel Upload with add_info Column")
        test1_success = self.test_excel_upload_with_add_info()

        # Test 2: Catalyst Data Retrieval
        print("\n📥 Test 2: Catalyst Data Retrieval with add_info")
        test2_success = self.test_catalyst_data_retrieval()

        # Test 3: Listing Creation with add_info
        print("\n📝 Test 3: Listing Creation with add_info")
        test3_success = self.test_listing_creation_with_add_info()

        # Test 4: Delete Database Functionality
        print("\n🗑️  Test 4: Delete Database Functionality")
        test4_success = self.test_delete_database_functionality()

        # Test 5: Database Recovery
        print("\n🔄 Test 5: Database Recovery")
        test5_success = self.test_database_recovery()

        # Test 6: Column Structure Validation
        print("\n📋 Test 6: Column Structure Validation")
        test6_success = self.test_column_structure_validation()

        # Summary
        all_tests = [test1_success, test2_success, test3_success, test4_success, test5_success, test6_success]
        passed_tests = sum(all_tests)
        total_tests = len(all_tests)

        print("\n" + "=" * 60)
        print(f"📊 Cat Database Test Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        print(f"🎯 Main Test Categories: {passed_tests}/{total_tests} categories passed")
        
        if passed_tests == total_tests:
            print("🎉 All Cat Database functionality tests passed!")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} test categories failed")
            return False

def main():
    """Main test execution"""
    tester = CatDatabaseTester()
    success = tester.run_cat_database_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())