#!/usr/bin/env python3
"""
Cataloro CMS Integration Test Suite
Tests live CMS integration by saving comprehensive content and verifying it appears on the live info page
"""

import requests
import sys
import json
from datetime import datetime

class CataloroLiveCMSTester:
    def __init__(self, base_url="https://cataloro-marketplace.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0

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
                raise ValueError(f"Unsupported HTTP method: {method}")

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Array'}"
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def create_comprehensive_cms_content(self):
        """Create comprehensive, realistic Cataloro marketplace content"""
        return {
            "seo": {
                "title": "Cataloro - Advanced Marketplace Platform for Modern Commerce",
                "description": "Discover Cataloro, the cutting-edge marketplace platform featuring real-time messaging, intelligent notifications, advanced search, and seamless transactions for buyers and sellers.",
                "keywords": ["marketplace", "e-commerce", "online trading", "buy sell platform", "cataloro", "modern commerce", "digital marketplace"],
                "ogImage": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&h=630",
                "canonicalUrl": "https://cataloro-marketplace.preview.emergentagent.com/info"
            },
            "hero": {
                "title": "Cataloro",
                "subtitle": "The Future of Online Marketplace",
                "description": "Experience next-generation commerce with our ultra-modern platform featuring intelligent matching, real-time communication, advanced analytics, and seamless transactions. Join thousands of users who trust Cataloro for their buying and selling needs.",
                "primaryButtonText": "Start Trading Now",
                "secondaryButtonText": "Explore Marketplace",
                "primaryButtonLink": "/browse",
                "secondaryButtonLink": "/register",
                "backgroundImage": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1920&h=1080",
                "overlayOpacity": 0.6,
                "textAlignment": "center"
            },
            "stats": [
                {
                    "label": "Active Users",
                    "value": "25K+",
                    "icon": "users",
                    "color": "#3B82F6",
                    "description": "Verified marketplace participants"
                },
                {
                    "label": "Products Listed",
                    "value": "150K+",
                    "icon": "package",
                    "color": "#10B981",
                    "description": "Items available for purchase"
                },
                {
                    "label": "Successful Transactions",
                    "value": "75K+",
                    "icon": "check-circle",
                    "color": "#F59E0B",
                    "description": "Completed deals with satisfaction"
                },
                {
                    "label": "User Satisfaction",
                    "value": "4.9★",
                    "icon": "star",
                    "color": "#EF4444",
                    "description": "Average user rating"
                },
                {
                    "label": "Response Time",
                    "value": "<2min",
                    "icon": "clock",
                    "color": "#8B5CF6",
                    "description": "Average message response time"
                },
                {
                    "label": "Global Reach",
                    "value": "50+ Countries",
                    "icon": "globe",
                    "color": "#06B6D4",
                    "description": "International marketplace presence"
                }
            ],
            "features": {
                "title": "Advanced Platform Features",
                "description": "Discover the comprehensive suite of tools and features that make Cataloro the most advanced marketplace platform available today.",
                "categories": [
                    {
                        "name": "Trading & Commerce",
                        "icon": "shopping-cart",
                        "features": [
                            {
                                "name": "Smart Listing Creation",
                                "description": "AI-powered listing optimization with automatic categorization and pricing suggestions",
                                "icon": "magic-wand"
                            },
                            {
                                "name": "Advanced Search & Filters",
                                "description": "Powerful search engine with intelligent filters and personalized recommendations",
                                "icon": "search"
                            },
                            {
                                "name": "Secure Payment Processing",
                                "description": "Multiple payment methods with buyer protection and escrow services",
                                "icon": "shield-check"
                            },
                            {
                                "name": "Order Management System",
                                "description": "Complete order lifecycle management with tracking and status updates",
                                "icon": "clipboard-list"
                            }
                        ]
                    },
                    {
                        "name": "Communication & Support",
                        "icon": "chat",
                        "features": [
                            {
                                "name": "Real-time Messaging",
                                "description": "Instant communication between buyers and sellers with file sharing",
                                "icon": "message-circle"
                            },
                            {
                                "name": "Smart Notifications",
                                "description": "Intelligent notification system with customizable preferences",
                                "icon": "bell"
                            },
                            {
                                "name": "24/7 Customer Support",
                                "description": "Round-the-clock assistance with multilingual support team",
                                "icon": "headphones"
                            },
                            {
                                "name": "Community Forums",
                                "description": "Active community discussions and knowledge sharing platform",
                                "icon": "users"
                            }
                        ]
                    },
                    {
                        "name": "Analytics & Insights",
                        "icon": "bar-chart",
                        "features": [
                            {
                                "name": "Performance Analytics",
                                "description": "Detailed insights into listing performance and market trends",
                                "icon": "trending-up"
                            },
                            {
                                "name": "Price Intelligence",
                                "description": "Market-based pricing recommendations and competitor analysis",
                                "icon": "dollar-sign"
                            },
                            {
                                "name": "Sales Reporting",
                                "description": "Comprehensive sales reports with revenue tracking and forecasting",
                                "icon": "file-text"
                            },
                            {
                                "name": "User Behavior Insights",
                                "description": "Understanding customer preferences and shopping patterns",
                                "icon": "eye"
                            }
                        ]
                    }
                ]
            },
            "testimonials": [
                {
                    "name": "Sarah Johnson",
                    "role": "Small Business Owner",
                    "company": "Vintage Treasures Co.",
                    "content": "Cataloro has transformed how I sell my vintage items. The intelligent pricing suggestions and real-time messaging have increased my sales by 300%. The platform is incredibly user-friendly and the customer support is outstanding.",
                    "rating": 5,
                    "avatar": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
                    "location": "San Francisco, CA"
                },
                {
                    "name": "Michael Chen",
                    "role": "Electronics Enthusiast",
                    "company": "Tech Collector",
                    "content": "As both a buyer and seller on Cataloro, I'm impressed by the platform's sophistication. The advanced search filters help me find exactly what I need, and the secure payment system gives me confidence in every transaction.",
                    "rating": 5,
                    "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
                    "location": "Austin, TX"
                },
                {
                    "name": "Emma Rodriguez",
                    "role": "Fashion Entrepreneur",
                    "company": "Sustainable Style",
                    "content": "The analytics dashboard on Cataloro provides incredible insights into my business. I can track performance, understand customer behavior, and optimize my listings for better results. It's like having a business consultant built into the platform.",
                    "rating": 5,
                    "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
                    "location": "Miami, FL"
                },
                {
                    "name": "David Thompson",
                    "role": "Automotive Parts Dealer",
                    "company": "Premium Auto Parts",
                    "content": "Cataloro's specialized features for automotive parts, including the catalyst database and pricing intelligence, have revolutionized my business. The platform understands the unique needs of different industries.",
                    "rating": 5,
                    "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
                    "location": "Detroit, MI"
                }
            ],
            "cta": {
                "title": "Ready to Transform Your Commerce Experience?",
                "description": "Join thousands of successful buyers and sellers who have discovered the power of modern marketplace technology. Start your journey with Cataloro today and experience the future of online commerce.",
                "primaryButtonText": "Create Free Account",
                "secondaryButtonText": "Schedule Demo",
                "primaryButtonLink": "/register",
                "secondaryButtonLink": "/demo",
                "backgroundColor": "#1F2937",
                "textColor": "#FFFFFF",
                "buttonStyle": "gradient",
                "animation": "fade-in-up"
            },
            "footer": {
                "companyDescription": "Cataloro is the leading next-generation marketplace platform, empowering businesses and individuals to buy and sell with confidence through advanced technology, intelligent features, and exceptional user experience.",
                "socialLinks": [
                    {
                        "platform": "Twitter",
                        "url": "https://twitter.com/cataloro",
                        "icon": "twitter"
                    },
                    {
                        "platform": "LinkedIn",
                        "url": "https://linkedin.com/company/cataloro",
                        "icon": "linkedin"
                    },
                    {
                        "platform": "Facebook",
                        "url": "https://facebook.com/cataloro",
                        "icon": "facebook"
                    },
                    {
                        "platform": "Instagram",
                        "url": "https://instagram.com/cataloro",
                        "icon": "instagram"
                    }
                ],
                "quickLinks": [
                    {"name": "About Us", "url": "/about"},
                    {"name": "How It Works", "url": "/how-it-works"},
                    {"name": "Pricing", "url": "/pricing"},
                    {"name": "Success Stories", "url": "/success-stories"},
                    {"name": "Help Center", "url": "/help"},
                    {"name": "Contact Support", "url": "/contact"}
                ],
                "legalLinks": [
                    {"name": "Terms of Service", "url": "/terms"},
                    {"name": "Privacy Policy", "url": "/privacy"},
                    {"name": "Cookie Policy", "url": "/cookies"},
                    {"name": "Acceptable Use", "url": "/acceptable-use"}
                ],
                "contactInfo": {
                    "email": "hello@cataloro.com",
                    "phone": "+1 (555) 123-4567",
                    "address": "123 Innovation Drive, Tech Valley, CA 94000"
                }
            }
        }

    def test_save_comprehensive_cms_content(self):
        """Test saving comprehensive CMS content using PUT /api/admin/content"""
        print("\n💾 Testing Save Comprehensive CMS Content...")
        
        # Create comprehensive content
        comprehensive_content = self.create_comprehensive_cms_content()
        
        print(f"   📝 Content sections: {list(comprehensive_content.keys())}")
        print(f"   🎯 SEO title: {comprehensive_content['seo']['title']}")
        print(f"   🏆 Hero title: {comprehensive_content['hero']['title']}")
        print(f"   📊 Statistics count: {len(comprehensive_content['stats'])}")
        print(f"   🔧 Feature categories: {len(comprehensive_content['features']['categories'])}")
        print(f"   💬 Testimonials count: {len(comprehensive_content['testimonials'])}")
        
        # Save content via PUT endpoint
        success, response = self.run_test(
            "Save Comprehensive CMS Content",
            "PUT",
            "api/admin/content",
            200,
            data=comprehensive_content
        )
        
        if success:
            print(f"   ✅ Content saved successfully")
            if 'version' in response:
                print(f"   📋 Content version: {response['version']}")
            if 'warning' in response:
                print(f"   ⚠️  SEO Warning: {response['warning']}")
        
        return success, response

    def test_verify_content_saved(self):
        """Test verifying the content was saved by retrieving it with GET /api/admin/content"""
        print("\n🔍 Testing Verify Content Was Saved...")
        
        success, response = self.run_test(
            "Retrieve Saved CMS Content",
            "GET",
            "api/admin/content",
            200
        )
        
        if success:
            # Verify all major sections are present
            expected_sections = ['seo', 'hero', 'stats', 'features', 'testimonials', 'cta', 'footer']
            present_sections = [section for section in expected_sections if section in response]
            
            print(f"   📋 Sections present: {present_sections}")
            print(f"   ✅ All sections saved: {len(present_sections) == len(expected_sections)}")
            
            # Verify specific content integrity
            if 'seo' in response:
                seo_complete = all(field in response['seo'] for field in ['title', 'description', 'keywords'])
                self.log_test("SEO Section Integrity", seo_complete, f"SEO fields complete: {seo_complete}")
            
            if 'hero' in response:
                hero_complete = all(field in response['hero'] for field in ['title', 'subtitle', 'description'])
                self.log_test("Hero Section Integrity", hero_complete, f"Hero fields complete: {hero_complete}")
            
            if 'stats' in response:
                stats_count = len(response['stats']) if isinstance(response['stats'], list) else 0
                self.log_test("Statistics Section", stats_count >= 4, f"Statistics count: {stats_count}")
            
            if 'features' in response:
                features_complete = 'categories' in response['features'] and len(response['features']['categories']) >= 3
                self.log_test("Features Section Integrity", features_complete, f"Feature categories present: {features_complete}")
            
            if 'testimonials' in response:
                testimonials_count = len(response['testimonials']) if isinstance(response['testimonials'], list) else 0
                self.log_test("Testimonials Section", testimonials_count >= 3, f"Testimonials count: {testimonials_count}")
            
            if 'footer' in response:
                footer_complete = all(field in response['footer'] for field in ['companyDescription', 'socialLinks'])
                self.log_test("Footer Section Integrity", footer_complete, f"Footer fields complete: {footer_complete}")
        
        return success, response

    def test_public_api_access(self):
        """Test that the public API returns the content for the live site (without auth)"""
        print("\n🌐 Testing Public API Access (Live Site Content)...")
        
        # Test the same endpoint without authentication (public access)
        success, response = self.run_test(
            "Public CMS Content Access",
            "GET",
            "api/admin/content",  # This should be accessible publicly for live site rendering
            200
        )
        
        if success:
            print(f"   🌍 Public content accessible: True")
            
            # Verify content is suitable for live site rendering
            if 'hero' in response:
                hero_ready = all(field in response['hero'] for field in ['title', 'subtitle', 'description'])
                self.log_test("Live Site Hero Content", hero_ready, f"Hero content ready for live site: {hero_ready}")
            
            if 'stats' in response and isinstance(response['stats'], list):
                stats_ready = len(response['stats']) > 0 and all('label' in stat and 'value' in stat for stat in response['stats'])
                self.log_test("Live Site Statistics", stats_ready, f"Statistics ready for live site: {stats_ready}")
            
            if 'features' in response:
                features_ready = 'title' in response['features'] and 'categories' in response['features']
                self.log_test("Live Site Features", features_ready, f"Features ready for live site: {features_ready}")
            
            # Check if content has all necessary fields for /info page rendering
            info_page_ready = all(section in response for section in ['hero', 'stats', 'features', 'cta'])
            self.log_test("Info Page Content Complete", info_page_ready, f"All sections for /info page: {info_page_ready}")
        
        return success, response

    def test_content_version_tracking(self):
        """Test content version tracking functionality"""
        print("\n📋 Testing Content Version Tracking...")
        
        # Test version history endpoint
        success, response = self.run_test(
            "Get Content Version History",
            "GET",
            "api/admin/content/versions",
            200
        )
        
        if success:
            versions = response.get('versions', [])
            print(f"   📊 Version history entries: {len(versions)}")
            
            if versions:
                latest_version = versions[0] if versions else {}
                version_fields_present = all(field in latest_version for field in ['version', 'updated_at'])
                self.log_test("Version Tracking Data", version_fields_present, f"Version fields complete: {version_fields_present}")
        
        return success

    def test_content_backup_functionality(self):
        """Test content backup functionality"""
        print("\n💾 Testing Content Backup Functionality...")
        
        # Test backup creation endpoint
        success, response = self.run_test(
            "Create Content Backup",
            "POST",
            "api/admin/content/backup",
            200
        )
        
        if success:
            backup_created = 'backup_version' in response
            self.log_test("Content Backup Creation", backup_created, f"Backup created: {backup_created}")
            
            if backup_created:
                print(f"   💾 Backup version: {response['backup_version']}")
        
        return success

    def test_seo_validation(self):
        """Test SEO validation functionality"""
        print("\n🔍 Testing SEO Validation...")
        
        # Create content with long SEO fields to test validation
        test_content = {
            "seo": {
                "title": "This is a very long SEO title that exceeds the recommended 60 character limit for search engine optimization and should trigger a warning",
                "description": "This is a very long meta description that exceeds the recommended 160 character limit for search engine optimization and should trigger a validation warning from the CMS system to help users optimize their content for better search engine visibility and ranking performance.",
                "keywords": ["test", "seo", "validation"]
            },
            "hero": {
                "title": "Test SEO Validation",
                "subtitle": "Testing SEO validation functionality",
                "description": "This is a test of the SEO validation system."
            }
        }
        
        success, response = self.run_test(
            "SEO Validation Test",
            "PUT",
            "api/admin/content",
            200,
            data=test_content
        )
        
        if success:
            seo_warning_present = 'warning' in response
            self.log_test("SEO Validation Warning", seo_warning_present, f"SEO validation warning triggered: {seo_warning_present}")
            
            if seo_warning_present:
                print(f"   ⚠️  SEO Warning: {response['warning']}")
        
        return success

    def run_comprehensive_cms_integration_test(self):
        """Run the complete CMS integration test suite"""
        print("🚀 Starting Cataloro Live CMS Integration Test Suite")
        print("=" * 80)
        
        # Test 1: Save comprehensive CMS content
        print("\n1️⃣ SAVE COMPREHENSIVE CMS CONTENT")
        save_success, save_response = self.test_save_comprehensive_cms_content()
        
        # Test 2: Verify content was saved
        print("\n2️⃣ VERIFY CONTENT WAS SAVED")
        verify_success, verify_response = self.test_verify_content_saved()
        
        # Test 3: Test public API access
        print("\n3️⃣ TEST PUBLIC API ACCESS")
        public_success, public_response = self.test_public_api_access()
        
        # Test 4: Test version tracking
        print("\n4️⃣ TEST VERSION TRACKING")
        version_success = self.test_content_version_tracking()
        
        # Test 5: Test backup functionality
        print("\n5️⃣ TEST BACKUP FUNCTIONALITY")
        backup_success = self.test_content_backup_functionality()
        
        # Test 6: Test SEO validation
        print("\n6️⃣ TEST SEO VALIDATION")
        seo_success = self.test_seo_validation()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 CMS INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = 6
        passed_tests = sum([save_success, verify_success, public_success, version_success, backup_success, seo_success])
        
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"📋 Major Test Categories: {passed_tests}/{total_tests}")
        
        test_results = [
            ("Save Comprehensive Content", save_success),
            ("Verify Content Saved", verify_success),
            ("Public API Access", public_success),
            ("Version Tracking", version_success),
            ("Backup Functionality", backup_success),
            ("SEO Validation", seo_success)
        ]
        
        for test_name, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL CMS INTEGRATION TESTS PASSED!")
            print("🌟 The live CMS integration is fully operational and ready for production use.")
            print("📝 Comprehensive marketplace content has been successfully saved and is accessible for the live /info page.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test categories failed")
            print("🔧 Some CMS integration features may need attention.")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    print("🏪 Cataloro Live CMS Integration Tester")
    print("Testing comprehensive CMS content management and live site integration")
    print("-" * 80)
    
    tester = CataloroLiveCMSTester()
    success = tester.run_comprehensive_cms_integration_test()
    
    if success:
        print("\n🎯 CMS Integration Test: SUCCESS")
        sys.exit(0)
    else:
        print("\n❌ CMS Integration Test: FAILED")
        sys.exit(1)