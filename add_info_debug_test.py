#!/usr/bin/env python3
"""
Cataloro Marketplace - Add_Info Debug Test Suite
Comprehensive testing of add_info field functionality in catalyst data and listing creation
"""

import requests
import sys
import json
import io
import pandas as pd
from datetime import datetime

class AddInfoDebugTester:
    def __init__(self, base_url="https://seller-status-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.test_catalyst_id = None
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
        test_headers = {}
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                if files:
                    response = self.session.post(url, files=files, headers=test_headers)
                else:
                    test_headers['Content-Type'] = 'application/json'
                    response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                test_headers['Content-Type'] = 'application/json'
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True, f"Status: {response.status_code}")
                return response.json() if response.content else {}
            else:
                self.log_test(name, False, f"Expected: {expected_status}, Got: {response.status_code}, Response: {response.text[:200]}")
                return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def setup_authentication(self):
        """Setup admin and user authentication"""
        print("\n🔐 Setting up authentication...")
        
        # Admin login
        admin_data = {"email": "admin@cataloro.com", "password": "admin123"}
        admin_response = self.run_test("Admin Login", "POST", "api/auth/login", 200, admin_data)
        if admin_response:
            self.admin_user = admin_response.get('user')
            self.admin_token = admin_response.get('token')
            print(f"   Admin User ID: {self.admin_user.get('id')}")

        # Regular user login
        user_data = {"email": "user@cataloro.com", "password": "user123"}
        user_response = self.run_test("User Login", "POST", "api/auth/login", 200, user_data)
        if user_response:
            self.regular_user = user_response.get('user')
            self.user_token = user_response.get('token')
            print(f"   Regular User ID: {self.regular_user.get('id')}")

    def test_1_catalyst_data_structure(self):
        """Test 1: Check /api/admin/catalyst/data endpoint for add_info field"""
        print("\n" + "="*60)
        print("TEST 1: CATALYST DATA STRUCTURE")
        print("="*60)
        
        # Get current catalyst data
        catalyst_data = self.run_test("Get Catalyst Data", "GET", "api/admin/catalyst/data", 200)
        
        if catalyst_data is not None:
            print(f"\n📊 Found {len(catalyst_data)} catalyst entries")
            
            # Check if any entries have add_info field
            entries_with_add_info = 0
            entries_with_content = 0
            
            for i, catalyst in enumerate(catalyst_data[:5]):  # Check first 5 entries
                print(f"\n   Catalyst {i+1}:")
                print(f"   - ID: {catalyst.get('cat_id', 'N/A')}")
                print(f"   - Name: {catalyst.get('name', 'N/A')}")
                print(f"   - Has add_info field: {'add_info' in catalyst}")
                
                if 'add_info' in catalyst:
                    entries_with_add_info += 1
                    add_info_content = catalyst.get('add_info', '')
                    print(f"   - add_info content: '{add_info_content}'")
                    if add_info_content and add_info_content.strip():
                        entries_with_content += 1
                        print(f"   - add_info has content: YES")
                    else:
                        print(f"   - add_info has content: NO (empty/null)")
            
            print(f"\n📈 Summary:")
            print(f"   - Entries with add_info field: {entries_with_add_info}/5")
            print(f"   - Entries with add_info content: {entries_with_content}/5")
            
            return catalyst_data
        
        return None

    def test_2_upload_test_data_with_add_info(self):
        """Test 2: Create and upload Excel file with add_info content"""
        print("\n" + "="*60)
        print("TEST 2: UPLOAD TEST DATA WITH ADD_INFO")
        print("="*60)
        
        # Create test Excel data with add_info
        test_data = {
            'cat_id': ['TEST001', 'TEST002', 'TEST003'],
            'name': ['TestCatalyst001', 'TestCatalyst002', 'TestCatalyst003'],
            'ceramic_weight': [1.5, 2.0, 1.8],
            'pt_ppm': [1500, 2000, 1800],
            'pd_ppm': [500, 600, 550],
            'rh_ppm': [100, 150, 120],
            'add_info': [
                'High performance catalyst with excellent durability. Suitable for automotive applications.',
                'Premium grade catalyst with enhanced efficiency. Recommended for industrial use.',
                'Standard catalyst with good performance characteristics. General purpose applications.'
            ]
        }
        
        # Create DataFrame and Excel file
        df = pd.DataFrame(test_data)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        print(f"\n📄 Created test Excel file with {len(test_data['cat_id'])} catalyst entries")
        print("   Each entry has detailed add_info content")
        
        # Upload the Excel file
        files = {
            'file': ('test_catalysts_with_add_info.xlsx', excel_buffer.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        upload_response = self.run_test("Upload Excel with add_info", "POST", "api/admin/catalyst/upload", 200, files=files)
        
        if upload_response:
            print(f"\n📊 Upload Results:")
            print(f"   - Message: {upload_response.get('message', 'N/A')}")
            print(f"   - Count: {upload_response.get('count', 'N/A')}")
            print(f"   - Valid rows: {upload_response.get('valid_rows', 'N/A')}")
            print(f"   - Errors: {upload_response.get('errors_count', 'N/A')}")
            
            return upload_response
        
        return None

    def test_3_verify_data_retrieval(self):
        """Test 3: Verify catalyst data endpoint returns entries with populated add_info"""
        print("\n" + "="*60)
        print("TEST 3: VERIFY DATA RETRIEVAL")
        print("="*60)
        
        # Get catalyst data after upload
        catalyst_data = self.run_test("Get Updated Catalyst Data", "GET", "api/admin/catalyst/data", 200)
        
        if catalyst_data is not None:
            print(f"\n📊 Retrieved {len(catalyst_data)} catalyst entries")
            
            # Look for our test entries
            test_entries_found = 0
            entries_with_add_info_content = 0
            
            for catalyst in catalyst_data:
                cat_id = catalyst.get('cat_id', '')
                if cat_id.startswith('TEST'):
                    test_entries_found += 1
                    print(f"\n   Found Test Entry:")
                    print(f"   - ID: {cat_id}")
                    print(f"   - Name: {catalyst.get('name', 'N/A')}")
                    
                    add_info = catalyst.get('add_info', '')
                    print(f"   - add_info present: {'add_info' in catalyst}")
                    print(f"   - add_info content: '{add_info}'")
                    
                    if add_info and add_info.strip():
                        entries_with_add_info_content += 1
                        print(f"   - add_info has content: YES ✅")
                        
                        # Store one for listing test
                        if not self.test_catalyst_id:
                            self.test_catalyst_id = catalyst.get('id')
                            print(f"   - Selected for listing test: {self.test_catalyst_id}")
                    else:
                        print(f"   - add_info has content: NO ❌")
            
            print(f"\n📈 Verification Summary:")
            print(f"   - Test entries found: {test_entries_found}")
            print(f"   - Entries with add_info content: {entries_with_add_info_content}")
            
            success = test_entries_found > 0 and entries_with_add_info_content > 0
            self.log_test("Data Retrieval Verification", success, 
                         f"Found {test_entries_found} test entries, {entries_with_add_info_content} with add_info")
            
            return catalyst_data
        
        return None

    def test_4_listing_creation_with_add_info(self):
        """Test 4: Create test listing using catalyst with add_info and verify description"""
        print("\n" + "="*60)
        print("TEST 4: LISTING CREATION WITH ADD_INFO")
        print("="*60)
        
        if not self.test_catalyst_id:
            print("❌ No test catalyst ID available for listing creation")
            return None
        
        # Get the specific catalyst data
        catalyst_data = self.run_test("Get All Catalyst Data", "GET", "api/admin/catalyst/data", 200)
        
        test_catalyst = None
        if catalyst_data:
            for catalyst in catalyst_data:
                if catalyst.get('id') == self.test_catalyst_id:
                    test_catalyst = catalyst
                    break
        
        if not test_catalyst:
            print(f"❌ Could not find test catalyst with ID: {self.test_catalyst_id}")
            return None
        
        print(f"\n🧪 Using Test Catalyst:")
        print(f"   - ID: {test_catalyst.get('cat_id')}")
        print(f"   - Name: {test_catalyst.get('name')}")
        print(f"   - add_info: '{test_catalyst.get('add_info', '')}'")
        
        # Create listing with catalyst information
        add_info_content = test_catalyst.get('add_info', '')
        base_description = f"Catalyst listing for {test_catalyst.get('name')}. Weight: {test_catalyst.get('ceramic_weight')}g."
        
        # Include add_info in description if present
        if add_info_content and add_info_content.strip():
            full_description = f"{base_description}\n\nAdditional Information: {add_info_content}"
        else:
            full_description = base_description
        
        listing_data = {
            "title": f"Catalyst: {test_catalyst.get('name')}",
            "description": full_description,
            "price": 250.00,
            "category": "Catalysts",
            "condition": "Used",
            "seller_id": self.admin_user.get('id') if self.admin_user else "test_seller",
            "images": [],
            "catalyst_id": test_catalyst.get('id'),
            "catalyst_data": test_catalyst
        }
        
        print(f"\n📝 Creating listing with description:")
        print(f"   '{full_description}'")
        
        # Create the listing
        listing_response = self.run_test("Create Catalyst Listing", "POST", "api/listings", 200, listing_data)
        
        if listing_response:
            self.test_listing_id = listing_response.get('listing_id')
            print(f"\n✅ Listing created successfully:")
            print(f"   - Listing ID: {self.test_listing_id}")
            print(f"   - Status: {listing_response.get('status')}")
            
            # Verify the listing was created with add_info in description
            created_listing = self.run_test("Get Created Listing", "GET", f"api/listings/{self.test_listing_id}", 200)
            
            if created_listing:
                stored_description = created_listing.get('description', '')
                print(f"\n📄 Stored listing description:")
                print(f"   '{stored_description}'")
                
                # Check if add_info content is in the description
                add_info_in_description = add_info_content in stored_description if add_info_content else True
                
                self.log_test("Add_info in Listing Description", add_info_in_description,
                             f"add_info content {'found' if add_info_in_description else 'NOT found'} in description")
                
                return created_listing
        
        return None

    def test_5_check_data_format(self):
        """Test 5: Examine exact structure of catalyst data returned by API"""
        print("\n" + "="*60)
        print("TEST 5: CHECK DATA FORMAT")
        print("="*60)
        
        # Get catalyst data
        catalyst_data = self.run_test("Get Catalyst Data for Format Check", "GET", "api/admin/catalyst/data", 200)
        
        if catalyst_data and len(catalyst_data) > 0:
            print(f"\n🔍 Examining data structure of {len(catalyst_data)} entries...")
            
            # Analyze first few entries
            for i, catalyst in enumerate(catalyst_data[:3]):
                print(f"\n   Entry {i+1} Structure:")
                print(f"   - Keys: {list(catalyst.keys())}")
                
                # Check each field
                for key, value in catalyst.items():
                    value_type = type(value).__name__
                    value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"     {key}: {value_type} = '{value_preview}'")
            
            # Check add_info field specifically
            add_info_analysis = {
                'present': 0,
                'with_content': 0,
                'empty': 0,
                'null': 0
            }
            
            for catalyst in catalyst_data:
                if 'add_info' in catalyst:
                    add_info_analysis['present'] += 1
                    add_info_value = catalyst.get('add_info')
                    
                    if add_info_value is None:
                        add_info_analysis['null'] += 1
                    elif isinstance(add_info_value, str) and add_info_value.strip():
                        add_info_analysis['with_content'] += 1
                    else:
                        add_info_analysis['empty'] += 1
            
            print(f"\n📊 add_info Field Analysis:")
            print(f"   - Total entries: {len(catalyst_data)}")
            print(f"   - Entries with add_info field: {add_info_analysis['present']}")
            print(f"   - Entries with add_info content: {add_info_analysis['with_content']}")
            print(f"   - Entries with empty add_info: {add_info_analysis['empty']}")
            print(f"   - Entries with null add_info: {add_info_analysis['null']}")
            
            # Test calculations endpoint as well
            calculations_data = self.run_test("Get Catalyst Calculations", "GET", "api/admin/catalyst/calculations", 200)
            
            if calculations_data:
                print(f"\n🧮 Calculations endpoint returned {len(calculations_data)} entries")
                if len(calculations_data) > 0:
                    calc_sample = calculations_data[0]
                    print(f"   Sample calculation structure: {list(calc_sample.keys())}")
            
            return catalyst_data
        
        return None

    def run_comprehensive_add_info_test(self):
        """Run all add_info related tests"""
        print("🚀 Starting Comprehensive Add_Info Debug Test Suite")
        print("="*80)
        
        # Setup
        self.setup_authentication()
        
        if not self.admin_user:
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Run all tests
        test_results = {}
        
        test_results['catalyst_data_structure'] = self.test_1_catalyst_data_structure()
        test_results['upload_with_add_info'] = self.test_2_upload_test_data_with_add_info()
        test_results['verify_data_retrieval'] = self.test_3_verify_data_retrieval()
        test_results['listing_creation'] = self.test_4_listing_creation_with_add_info()
        test_results['data_format_check'] = self.test_5_check_data_format()
        
        # Summary
        print("\n" + "="*80)
        print("🏁 ADD_INFO DEBUG TEST SUMMARY")
        print("="*80)
        
        print(f"\n📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        # Analyze results
        issues_found = []
        
        if not test_results['catalyst_data_structure']:
            issues_found.append("❌ Catalyst data endpoint not accessible")
        
        if not test_results['upload_with_add_info']:
            issues_found.append("❌ Excel upload with add_info failed")
        
        if not test_results['verify_data_retrieval']:
            issues_found.append("❌ Data retrieval after upload failed")
        
        if not test_results['listing_creation']:
            issues_found.append("❌ Listing creation with add_info failed")
        
        if issues_found:
            print(f"\n🚨 Issues Found:")
            for issue in issues_found:
                print(f"   {issue}")
        else:
            print(f"\n✅ All major functionality working correctly")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if test_results['catalyst_data_structure'] and test_results['upload_with_add_info']:
            print("   ✅ Backend add_info functionality appears to be working")
            print("   ✅ Excel upload with add_info is functional")
            print("   ✅ Data retrieval includes add_info field")
            
            if test_results['listing_creation']:
                print("   ✅ Listing creation can include add_info in descriptions")
                print("   📝 If frontend is not showing add_info, check frontend code for:")
                print("      - Proper API integration with /api/admin/catalyst/data")
                print("      - Description generation logic in listing creation")
                print("      - Catalyst selection and auto-fill functionality")
            else:
                print("   ⚠️  Listing creation needs investigation")
        else:
            print("   🔧 Backend add_info functionality needs attention")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = AddInfoDebugTester()
    success = tester.run_comprehensive_add_info_test()
    sys.exit(0 if success else 1)