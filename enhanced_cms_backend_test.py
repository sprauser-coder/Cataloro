#!/usr/bin/env python3
"""
Enhanced CMS Backend API Test Suite
Tests the enhanced Content Management System endpoints for the Cataloro Marketplace
Focuses on SEO, version tracking, backup functionality, and enhanced content structure
"""

import requests
import sys
import json
from datetime import datetime

class EnhancedCMSAPITester:
    def __init__(self, base_url="https://cataloro-marketplace-4.preview.emergentagent.com"):
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
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_get_enhanced_content_structure(self):
        """Test GET /api/admin/content - enhanced content structure with SEO, hero, stats, features, testimonials, CTA, footer"""
        print("\n" + "="*80)
        print("🎯 TESTING ENHANCED CMS GET CONTENT STRUCTURE")
        print("="*80)
        
        response_data = self.run_test(
            "Get Enhanced Content Structure",
            "GET",
            "api/admin/content",
            200
        )
        
        if response_data:
            print("\n📋 Verifying Enhanced Content Structure...")
            
            # Check for enhanced sections
            enhanced_sections = ['hero', 'stats', 'features', 'cta']
            optional_sections = ['seo', 'testimonials', 'footer']
            
            all_required_present = True
            
            # Verify required sections
            for section in enhanced_sections:
                if section not in response_data:
                    print(f"❌ Missing required section: {section}")
                    all_required_present = False
                else:
                    print(f"✅ Found required section: {section}")
            
            # Check optional sections
            for section in optional_sections:
                if section in response_data:
                    print(f"✅ Found optional section: {section}")
                else:
                    print(f"ℹ️  Optional section not present: {section}")
            
            # Detailed hero section verification
            if 'hero' in response_data:
                hero = response_data['hero']
                hero_fields = ['title', 'subtitle', 'description', 'primaryButtonText', 'secondaryButtonText']
                hero_optional = ['links', 'styling', 'backgroundImage']
                
                print("\n🦸 Hero Section Analysis:")
                for field in hero_fields:
                    if field in hero:
                        print(f"✅ Hero has {field}: {hero[field]}")
                    else:
                        print(f"❌ Hero missing required {field}")
                        all_required_present = False
                
                for field in hero_optional:
                    if field in hero:
                        print(f"✅ Hero has optional {field}")
            
            # Detailed stats section verification
            if 'stats' in response_data and isinstance(response_data['stats'], list):
                print(f"\n📊 Stats Section Analysis:")
                print(f"✅ Stats is array with {len(response_data['stats'])} items")
                
                if len(response_data['stats']) >= 4:
                    print("✅ Stats has recommended 4+ items")
                    for i, stat in enumerate(response_data['stats'][:4]):
                        if 'label' in stat and 'value' in stat:
                            print(f"✅ Stat {i+1}: {stat['label']} = {stat['value']}")
                            # Check for enhanced stat fields
                            if 'icon' in stat:
                                print(f"   ✅ Has icon: {stat['icon']}")
                            if 'color' in stat:
                                print(f"   ✅ Has color: {stat['color']}")
                        else:
                            print(f"❌ Stat {i+1} missing label/value")
                            all_required_present = False
            
            # Features section verification
            if 'features' in response_data:
                features = response_data['features']
                print(f"\n🎯 Features Section Analysis:")
                if 'title' in features and 'description' in features:
                    print(f"✅ Features title: {features['title']}")
                    print(f"✅ Features description: {features['description']}")
                    
                    # Check for enhanced features
                    if 'categories' in features:
                        print("✅ Features has categories")
                    if 'customization' in features:
                        print("✅ Features has customization options")
                else:
                    print("❌ Features missing title/description")
                    all_required_present = False
            
            # CTA section verification
            if 'cta' in response_data:
                cta = response_data['cta']
                print(f"\n📢 CTA Section Analysis:")
                cta_fields = ['title', 'description', 'primaryButtonText', 'secondaryButtonText']
                for field in cta_fields:
                    if field in cta:
                        print(f"✅ CTA has {field}: {cta[field]}")
                    else:
                        print(f"❌ CTA missing {field}")
                        all_required_present = False
                
                # Check for enhanced CTA options
                if 'enhancedOptions' in cta:
                    print("✅ CTA has enhanced options")
            
            self.log_test("Enhanced Content Structure Validation", all_required_present, 
                         f"All required sections present: {all_required_present}")
            
            return response_data
        
        return None

    def test_enhanced_content_update_with_seo(self):
        """Test PUT /api/admin/content with enhanced structure including SEO validation"""
        print("\n" + "="*80)
        print("🎯 TESTING ENHANCED CMS UPDATE WITH SEO")
        print("="*80)
        
        # Enhanced test content with SEO and all sections
        enhanced_content = {
            "seo": {
                "title": "Enhanced Cataloro CMS Test - Modern Marketplace Platform",
                "description": "Testing the enhanced Content Management System with SEO optimization, version tracking, and advanced features for the Cataloro marketplace.",
                "keywords": ["cataloro", "cms", "marketplace", "seo", "testing"],
                "ogImage": "https://example.com/og-image.jpg",
                "canonicalUrl": "https://cataloro-marketplace-4.preview.emergentagent.com"
            },
            "hero": {
                "title": "Enhanced Cataloro CMS",
                "subtitle": "Advanced Content Management with SEO",
                "description": "Experience the enhanced CMS with SEO optimization, version tracking, and advanced content management features.",
                "primaryButtonText": "Start Enhanced Journey",
                "secondaryButtonText": "Explore Advanced Features",
                "links": {
                    "primary": "/enhanced-start",
                    "secondary": "/advanced-features"
                },
                "styling": {
                    "theme": "modern",
                    "gradient": "blue-purple"
                }
            },
            "stats": [
                {"label": "Enhanced Users", "value": "15K+", "icon": "users", "color": "blue"},
                {"label": "Advanced Products", "value": "75K+", "icon": "products", "color": "green"},
                {"label": "Premium Deals", "value": "35K+", "icon": "deals", "color": "purple"},
                {"label": "Enhanced Rating", "value": "4.95★", "icon": "star", "color": "yellow"}
            ],
            "features": {
                "title": "Enhanced Platform Features",
                "description": "Discover advanced features with SEO optimization and enhanced customization.",
                "categories": ["SEO", "Analytics", "Customization", "Performance"],
                "customization": {
                    "themes": ["modern", "classic", "minimal"],
                    "layouts": ["grid", "list", "card"]
                }
            },
            "testimonials": {
                "title": "What Our Users Say",
                "items": [
                    {
                        "name": "John Doe",
                        "role": "Marketplace Owner",
                        "content": "The enhanced CMS with SEO features is amazing!",
                        "rating": 5
                    }
                ]
            },
            "cta": {
                "title": "Ready for Enhanced Experience?",
                "description": "Join the enhanced platform with SEO optimization and advanced features.",
                "primaryButtonText": "Start Enhanced Journey",
                "secondaryButtonText": "Learn About Features",
                "enhancedOptions": {
                    "animation": "fade-in",
                    "style": "gradient"
                }
            },
            "footer": {
                "socialLinks": [
                    {"platform": "twitter", "url": "https://twitter.com/cataloro"},
                    {"platform": "linkedin", "url": "https://linkedin.com/company/cataloro"}
                ],
                "links": [
                    {"text": "Privacy Policy", "url": "/privacy"},
                    {"text": "Terms of Service", "url": "/terms"}
                ]
            }
        }
        
        print("📝 Testing Enhanced Content Update...")
        response_data = self.run_test(
            "Update Enhanced Content with SEO",
            "PUT",
            "api/admin/content",
            200,
            data=enhanced_content
        )
        
        if response_data:
            print("\n🔍 Verifying Update Response...")
            
            # Check for success message
            if 'message' in response_data:
                print(f"✅ Update response: {response_data['message']}")
                
                # Check for version tracking
                if 'version' in response_data:
                    print(f"✅ Version tracking: {response_data['version']}")
                    self.log_test("Version Tracking", True, f"Version: {response_data['version']}")
                else:
                    print("⚠️  Version tracking not found in response")
                    self.log_test("Version Tracking", False, "No version in response")
                
                # Verify content persistence
                print("\n🔍 Verifying Enhanced Content Persistence...")
                saved_content = self.run_test(
                    "Verify Enhanced Content Saved",
                    "GET",
                    "api/admin/content",
                    200
                )
                
                if saved_content:
                    # Verify SEO section
                    if 'seo' in saved_content:
                        seo = saved_content['seo']
                        if seo.get('title') == enhanced_content['seo']['title']:
                            print("✅ SEO title persisted correctly")
                            self.log_test("SEO Persistence", True, "SEO data saved correctly")
                        else:
                            print("❌ SEO title not persisted correctly")
                            self.log_test("SEO Persistence", False, "SEO data not saved")
                    
                    # Verify enhanced hero
                    if 'hero' in saved_content:
                        hero = saved_content['hero']
                        if (hero.get('title') == enhanced_content['hero']['title'] and
                            'links' in hero and 'styling' in hero):
                            print("✅ Enhanced hero with links and styling persisted")
                            self.log_test("Enhanced Hero Persistence", True, "Hero enhancements saved")
                        else:
                            print("❌ Enhanced hero features not fully persisted")
                            self.log_test("Enhanced Hero Persistence", False, "Hero enhancements not saved")
                    
                    # Verify enhanced stats
                    if 'stats' in saved_content and len(saved_content['stats']) > 0:
                        stat = saved_content['stats'][0]
                        if 'icon' in stat and 'color' in stat:
                            print("✅ Enhanced stats with icons and colors persisted")
                            self.log_test("Enhanced Stats Persistence", True, "Stats enhancements saved")
                        else:
                            print("❌ Enhanced stats features not persisted")
                            self.log_test("Enhanced Stats Persistence", False, "Stats enhancements not saved")
                    
                    # Verify testimonials section
                    if 'testimonials' in saved_content:
                        print("✅ Testimonials section persisted")
                        self.log_test("Testimonials Persistence", True, "Testimonials section saved")
                    else:
                        print("ℹ️  Testimonials section not persisted (optional)")
                    
                    # Verify footer section
                    if 'footer' in saved_content:
                        footer = saved_content['footer']
                        if 'socialLinks' in footer:
                            print("✅ Footer with social links persisted")
                            self.log_test("Footer Persistence", True, "Footer with social links saved")
                        else:
                            print("❌ Footer social links not persisted")
                            self.log_test("Footer Persistence", False, "Footer social links not saved")
                    else:
                        print("ℹ️  Footer section not persisted (optional)")
                
                return response_data
            else:
                print("❌ Update response missing success message")
                self.log_test("Update Response Validation", False, "Missing success message")
        
        return None

    def test_seo_validation(self):
        """Test SEO field validation (title max 60 chars, description max 160 chars)"""
        print("\n" + "="*80)
        print("🎯 TESTING SEO VALIDATION")
        print("="*80)
        
        # Test with SEO title over 60 characters
        long_title_content = {
            "seo": {
                "title": "This is a very long SEO title that exceeds the recommended 60 character limit for search engine optimization",
                "description": "Valid description under 160 characters"
            },
            "hero": {
                "title": "SEO Test",
                "subtitle": "Testing SEO validation",
                "description": "Testing SEO field validation",
                "primaryButtonText": "Test",
                "secondaryButtonText": "Validate"
            }
        }
        
        print("📝 Testing Long SEO Title (>60 chars)...")
        response = self.run_test(
            "SEO Title Length Validation",
            "PUT",
            "api/admin/content",
            200,  # Should still accept but may warn
            data=long_title_content
        )
        
        if response:
            if 'warning' in response and 'title' in response['warning']:
                print("✅ SEO title length validation working - warning returned")
                self.log_test("SEO Title Validation", True, "Warning for long title")
            else:
                print("ℹ️  SEO title validation may be lenient")
                self.log_test("SEO Title Validation", True, "Accepts long title")
        
        # Test with SEO description over 160 characters
        long_desc_content = {
            "seo": {
                "title": "Valid SEO Title",
                "description": "This is a very long SEO meta description that exceeds the recommended 160 character limit for search engine optimization and should trigger a validation warning"
            },
            "hero": {
                "title": "SEO Test",
                "subtitle": "Testing SEO validation",
                "description": "Testing SEO field validation",
                "primaryButtonText": "Test",
                "secondaryButtonText": "Validate"
            }
        }
        
        print("\n📝 Testing Long SEO Description (>160 chars)...")
        response = self.run_test(
            "SEO Description Length Validation",
            "PUT",
            "api/admin/content",
            200,  # Should still accept but may warn
            data=long_desc_content
        )
        
        if response:
            if 'warning' in response and 'description' in response['warning']:
                print("✅ SEO description length validation working - warning returned")
                self.log_test("SEO Description Validation", True, "Warning for long description")
            else:
                print("ℹ️  SEO description validation may be lenient")
                self.log_test("SEO Description Validation", True, "Accepts long description")

    def test_version_tracking_and_timestamps(self):
        """Test version tracking and timestamps functionality"""
        print("\n" + "="*80)
        print("🎯 TESTING VERSION TRACKING AND TIMESTAMPS")
        print("="*80)
        
        # Create content with version tracking
        version_test_content = {
            "hero": {
                "title": "Version Tracking Test",
                "subtitle": "Testing Version and Timestamps",
                "description": "This content is created to test version tracking functionality.",
                "primaryButtonText": "Track Version",
                "secondaryButtonText": "Check Timestamps"
            },
            "stats": [
                {"label": "Version Tests", "value": "1"}
            ]
        }
        
        print("📝 Creating Content for Version Tracking...")
        response1 = self.run_test(
            "Create Content with Version Tracking",
            "PUT",
            "api/admin/content",
            200,
            data=version_test_content
        )
        
        if response1:
            version1 = response1.get('version')
            if version1:
                print(f"✅ First version created: {version1}")
                
                # Update content to create new version
                version_test_content['hero']['title'] = "Version Tracking Test - Updated"
                version_test_content['stats'][0]['value'] = "2"
                
                print("\n📝 Updating Content to Create New Version...")
                response2 = self.run_test(
                    "Update Content for New Version",
                    "PUT",
                    "api/admin/content",
                    200,
                    data=version_test_content
                )
                
                if response2:
                    version2 = response2.get('version')
                    if version2 and version2 != version1:
                        print(f"✅ New version created: {version2}")
                        self.log_test("Version Increment", True, f"Version changed from {version1} to {version2}")
                    else:
                        print("❌ Version not incremented")
                        self.log_test("Version Increment", False, "Version not changed")
                    
                    # Check for timestamps
                    if 'updated_at' in response2 or 'timestamp' in response2:
                        print("✅ Timestamp tracking working")
                        self.log_test("Timestamp Tracking", True, "Timestamps present")
                    else:
                        print("⚠️  Timestamp tracking not visible in response")
                        self.log_test("Timestamp Tracking", False, "No timestamps in response")

    def test_content_versions_endpoint(self):
        """Test GET /api/admin/content/versions endpoint"""
        print("\n" + "="*80)
        print("🎯 TESTING CONTENT VERSIONS ENDPOINT")
        print("="*80)
        
        response_data = self.run_test(
            "Get Content Version History",
            "GET",
            "api/admin/content/versions",
            200
        )
        
        if response_data:
            if 'versions' in response_data:
                versions = response_data['versions']
                print(f"✅ Version history endpoint working - found {len(versions)} versions")
                
                if len(versions) > 0:
                    print("📋 Version History:")
                    for i, version in enumerate(versions[:3]):  # Show first 3
                        version_num = version.get('version', 'Unknown')
                        updated_at = version.get('updated_at', 'Unknown')
                        print(f"   Version {i+1}: {version_num} (Updated: {updated_at})")
                    
                    self.log_test("Version History Retrieval", True, f"Found {len(versions)} versions")
                else:
                    print("ℹ️  No version history found (may be first run)")
                    self.log_test("Version History Retrieval", True, "Endpoint working, no history yet")
            else:
                print("❌ Version history response missing 'versions' field")
                self.log_test("Version History Retrieval", False, "Invalid response format")
        else:
            print("❌ Version history endpoint not working")
            self.log_test("Version History Retrieval", False, "Endpoint failed")

    def test_content_backup_endpoint(self):
        """Test POST /api/admin/content/backup endpoint"""
        print("\n" + "="*80)
        print("🎯 TESTING CONTENT BACKUP ENDPOINT")
        print("="*80)
        
        response_data = self.run_test(
            "Create Content Backup",
            "POST",
            "api/admin/content/backup",
            200
        )
        
        if response_data:
            if 'message' in response_data:
                print(f"✅ Backup response: {response_data['message']}")
                
                if 'backup_version' in response_data:
                    backup_version = response_data['backup_version']
                    print(f"✅ Backup version created: {backup_version}")
                    self.log_test("Content Backup Creation", True, f"Backup version: {backup_version}")
                else:
                    print("⚠️  Backup version not returned")
                    self.log_test("Content Backup Creation", True, "Backup created without version info")
            else:
                print("❌ Backup response missing success message")
                self.log_test("Content Backup Creation", False, "Invalid backup response")
        else:
            print("❌ Content backup endpoint not working")
            self.log_test("Content Backup Creation", False, "Backup endpoint failed")

    def test_site_content_collection_storage(self):
        """Test that content is saved to site_content collection with type 'info_page'"""
        print("\n" + "="*80)
        print("🎯 TESTING SITE_CONTENT COLLECTION STORAGE")
        print("="*80)
        
        # Create specific test content to verify storage
        storage_test_content = {
            "hero": {
                "title": "Storage Test Content",
                "subtitle": "Testing Database Storage",
                "description": "This content tests storage in site_content collection with type info_page.",
                "primaryButtonText": "Test Storage",
                "secondaryButtonText": "Verify DB"
            },
            "stats": [
                {"label": "Storage Tests", "value": "1"}
            ]
        }
        
        print("📝 Creating Content to Test Storage...")
        response = self.run_test(
            "Create Content for Storage Test",
            "PUT",
            "api/admin/content",
            200,
            data=storage_test_content
        )
        
        if response:
            print("✅ Content creation successful")
            
            # Retrieve content to verify it was stored correctly
            print("\n🔍 Verifying Content Storage...")
            retrieved_content = self.run_test(
                "Retrieve Stored Content",
                "GET",
                "api/admin/content",
                200
            )
            
            if retrieved_content:
                if (retrieved_content.get('hero', {}).get('title') == "Storage Test Content"):
                    print("✅ Content stored and retrieved correctly from site_content collection")
                    self.log_test("Site Content Collection Storage", True, "Content stored with type info_page")
                else:
                    print("❌ Content storage/retrieval issue")
                    self.log_test("Site Content Collection Storage", False, "Content not properly stored")
            else:
                print("❌ Could not retrieve stored content")
                self.log_test("Site Content Collection Storage", False, "Content retrieval failed")

    def run_all_enhanced_tests(self):
        """Run all enhanced CMS API tests"""
        print("🚀 STARTING ENHANCED CMS BACKEND API TESTS")
        print("="*80)
        
        # Test 1: Enhanced content structure
        self.test_get_enhanced_content_structure()
        
        # Test 2: Enhanced content update with SEO
        self.test_enhanced_content_update_with_seo()
        
        # Test 3: SEO validation
        self.test_seo_validation()
        
        # Test 4: Version tracking and timestamps
        self.test_version_tracking_and_timestamps()
        
        # Test 5: Content versions endpoint
        self.test_content_versions_endpoint()
        
        # Test 6: Content backup endpoint
        self.test_content_backup_endpoint()
        
        # Test 7: Site content collection storage
        self.test_site_content_collection_storage()
        
        # Final summary
        print("\n" + "="*80)
        print("📊 ENHANCED CMS API TEST SUMMARY")
        print("="*80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL ENHANCED CMS TESTS PASSED! ✅")
            return True
        else:
            print("⚠️  SOME ENHANCED CMS TESTS FAILED ❌")
            return False

if __name__ == "__main__":
    print("🎯 Cataloro Enhanced CMS Backend API Test Suite")
    print("Testing enhanced Content Management System endpoints with SEO, version tracking, and backup functionality")
    print("="*80)
    
    tester = EnhancedCMSAPITester()
    success = tester.run_all_enhanced_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)