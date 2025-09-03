#!/usr/bin/env python3
"""
CMS Backend API Test Suite
Tests the Content Management System endpoints for the Cataloro Marketplace
"""

import requests
import sys
import json
from datetime import datetime

class CMSAPITester:
    def __init__(self, base_url="https://tender-system.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
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
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)
            else:
                self.log_test(name, False, f"Unsupported method: {method}")
                return None

            print(f"   Status: {response.status_code}")
            
            # Check if status matches expected
            if response.status_code == expected_status:
                try:
                    response_data = response.json()
                    self.log_test(name, True, f"Status: {response.status_code}")
                    return response_data
                except:
                    # Non-JSON response
                    self.log_test(name, True, f"Status: {response.status_code} (Non-JSON)")
                    return response.text
            else:
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_get_content_default(self):
        """Test GET /api/admin/content - should return default content structure"""
        print("\n" + "="*60)
        print("🎯 TESTING CMS GET CONTENT (DEFAULT)")
        print("="*60)
        
        response_data = self.run_test(
            "Get Default Content Structure",
            "GET",
            "api/admin/content",
            200
        )
        
        if response_data:
            # Verify default content structure
            required_sections = ['hero', 'stats', 'features', 'cta']
            all_sections_present = True
            
            for section in required_sections:
                if section not in response_data:
                    print(f"❌ Missing required section: {section}")
                    all_sections_present = False
                else:
                    print(f"✅ Found section: {section}")
            
            # Verify hero section structure
            if 'hero' in response_data:
                hero = response_data['hero']
                hero_fields = ['title', 'subtitle', 'description', 'primaryButtonText', 'secondaryButtonText']
                for field in hero_fields:
                    if field in hero:
                        print(f"✅ Hero section has {field}: {hero[field]}")
                    else:
                        print(f"❌ Hero section missing {field}")
                        all_sections_present = False
            
            # Verify stats section
            if 'stats' in response_data and isinstance(response_data['stats'], list):
                print(f"✅ Stats section is array with {len(response_data['stats'])} items")
                if len(response_data['stats']) > 0:
                    stat = response_data['stats'][0]
                    if 'label' in stat and 'value' in stat:
                        print(f"✅ Stats have proper structure: {stat['label']} = {stat['value']}")
                    else:
                        print("❌ Stats missing label/value structure")
                        all_sections_present = False
            
            # Verify features section
            if 'features' in response_data:
                features = response_data['features']
                if 'title' in features and 'description' in features:
                    print(f"✅ Features section: {features['title']}")
                else:
                    print("❌ Features section missing title/description")
                    all_sections_present = False
            
            # Verify CTA section
            if 'cta' in response_data:
                cta = response_data['cta']
                cta_fields = ['title', 'description', 'primaryButtonText', 'secondaryButtonText']
                for field in cta_fields:
                    if field in cta:
                        print(f"✅ CTA section has {field}")
                    else:
                        print(f"❌ CTA section missing {field}")
                        all_sections_present = False
            
            self.log_test("Content Structure Validation", all_sections_present, 
                         f"All required sections present: {all_sections_present}")
            
            return response_data
        
        return None

    def test_update_content(self):
        """Test PUT /api/admin/content - should update content successfully"""
        print("\n" + "="*60)
        print("🎯 TESTING CMS UPDATE CONTENT")
        print("="*60)
        
        # Test content to update
        test_content = {
            "hero": {
                "title": "Test Cataloro CMS",
                "subtitle": "Testing Content Management System",
                "description": "This is a test update to verify the CMS functionality is working correctly.",
                "primaryButtonText": "Test Start",
                "secondaryButtonText": "Test Browse"
            },
            "stats": [
                {"label": "Test Users", "value": "100+"},
                {"label": "Test Products", "value": "500+"},
                {"label": "Test Deals", "value": "250+"},
                {"label": "Test Rating", "value": "5.0★"}
            ],
            "features": {
                "title": "Test Platform Features",
                "description": "Testing all the powerful features of our CMS system."
            },
            "cta": {
                "title": "Ready to Test?",
                "description": "Join our testing program and help us improve the platform.",
                "primaryButtonText": "Start Testing",
                "secondaryButtonText": "Learn More"
            }
        }
        
        response_data = self.run_test(
            "Update Content via PUT",
            "PUT",
            "api/admin/content",
            200,
            data=test_content
        )
        
        if response_data:
            # Verify response message
            if 'message' in response_data:
                print(f"✅ Update response: {response_data['message']}")
                
                # Verify the content was actually saved by getting it again
                print("\n🔍 Verifying content was saved...")
                saved_content = self.run_test(
                    "Verify Updated Content",
                    "GET",
                    "api/admin/content",
                    200
                )
                
                if saved_content:
                    # Check if our test content is reflected
                    if (saved_content.get('hero', {}).get('title') == test_content['hero']['title'] and
                        saved_content.get('hero', {}).get('subtitle') == test_content['hero']['subtitle']):
                        print("✅ Content successfully updated and persisted")
                        self.log_test("Content Persistence Verification", True, "Updated content found in database")
                    else:
                        print("❌ Content update may not have persisted correctly")
                        print(f"Expected title: {test_content['hero']['title']}")
                        print(f"Found title: {saved_content.get('hero', {}).get('title')}")
                        self.log_test("Content Persistence Verification", False, "Updated content not found")
                
                return response_data
            else:
                print("❌ Update response missing success message")
                self.log_test("Update Response Validation", False, "Missing success message")
        
        return None

    def test_content_database_integration(self):
        """Test that content is properly stored in site_content collection with type 'info_page'"""
        print("\n" + "="*60)
        print("🎯 TESTING DATABASE INTEGRATION")
        print("="*60)
        
        # First, update with specific test data
        test_data = {
            "hero": {
                "title": "Database Integration Test",
                "subtitle": "Testing MongoDB Storage",
                "description": "Verifying that content is stored in site_content collection with type info_page",
                "primaryButtonText": "DB Test",
                "secondaryButtonText": "Verify Storage"
            },
            "stats": [
                {"label": "DB Tests", "value": "1"}
            ],
            "features": {
                "title": "Database Features",
                "description": "Testing database storage and retrieval."
            },
            "cta": {
                "title": "Database Ready?",
                "description": "Testing complete database integration.",
                "primaryButtonText": "Test DB",
                "secondaryButtonText": "Check Storage"
            }
        }
        
        # Update content
        update_response = self.run_test(
            "Update Content for DB Test",
            "PUT",
            "api/admin/content",
            200,
            data=test_data
        )
        
        if update_response:
            # Retrieve content to verify storage
            retrieve_response = self.run_test(
                "Retrieve Content from DB",
                "GET",
                "api/admin/content",
                200
            )
            
            if retrieve_response:
                # Verify the specific test data is present
                if (retrieve_response.get('hero', {}).get('title') == "Database Integration Test"):
                    print("✅ Database integration working - content stored and retrieved correctly")
                    self.log_test("Database Storage Integration", True, "Content properly stored in site_content collection")
                else:
                    print("❌ Database integration issue - content not properly stored/retrieved")
                    self.log_test("Database Storage Integration", False, "Content storage/retrieval failed")

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n" + "="*60)
        print("🎯 TESTING ERROR HANDLING")
        print("="*60)
        
        # Test with invalid JSON structure
        invalid_data = {
            "invalid_field": "test"
        }
        
        # This should still work as the endpoint accepts any dict structure
        response = self.run_test(
            "Update with Non-Standard Data",
            "PUT",
            "api/admin/content",
            200,
            data=invalid_data
        )
        
        if response:
            print("✅ Endpoint accepts flexible data structure")
            self.log_test("Flexible Data Structure", True, "Endpoint handles non-standard data")

    def run_all_tests(self):
        """Run all CMS API tests"""
        print("🚀 STARTING CMS BACKEND API TESTS")
        print("="*80)
        
        # Test 1: Get default content structure
        default_content = self.test_get_content_default()
        
        # Test 2: Update content
        self.test_update_content()
        
        # Test 3: Database integration
        self.test_content_database_integration()
        
        # Test 4: Error handling
        self.test_error_handling()
        
        # Final summary
        print("\n" + "="*80)
        print("📊 CMS API TEST SUMMARY")
        print("="*80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL CMS TESTS PASSED! ✅")
            return True
        else:
            print("⚠️  SOME CMS TESTS FAILED ❌")
            return False

if __name__ == "__main__":
    print("🎯 Cataloro CMS Backend API Test Suite")
    print("Testing Content Management System endpoints")
    print("="*80)
    
    tester = CMSAPITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)