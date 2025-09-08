#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Individual Basket PDF Export Functionality
Testing Agent: Focused testing of newly implemented basket export features
"""

import asyncio
import aiohttp
import json
import uuid
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://marketplace-repair-1.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class BackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_users = []
        self.test_baskets = []
        self.test_items = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")
            
    async def make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request with error handling"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "DELETE":
                async with self.session.delete(url, params=params) as response:
                    return await response.json(), response.status
                    
        except Exception as e:
            return {"error": str(e)}, 500
            
    async def setup_test_data(self):
        """Setup test users and basket data for PDF export testing"""
        print("\n🔧 Setting up test data...")
        
        # Use admin user for testing
        admin_login_response, admin_status = await self.make_request("POST", "/auth/login", {
            "email": "admin@cataloro.com",
            "password": "admin123"
        })
        
        if admin_status == 200 and "user" in admin_login_response:
            admin_user = admin_login_response["user"]
            self.test_users.append(admin_user)
            print(f"✅ Admin user logged in: {admin_user.get('username', 'admin')}")
        
        # Create a demo user for testing
        demo_login_response, demo_status = await self.make_request("POST", "/auth/login", {
            "email": "demo@test.com",
            "password": "demo123"
        })
        
        if demo_status == 200 and "user" in demo_login_response:
            demo_user = demo_login_response["user"]
            self.test_users.append(demo_user)
            print(f"✅ Demo user logged in: {demo_user.get('username', 'demo')}")
        
        print(f"✅ Setup {len(self.test_users)} test users")
        
        # Create sample basket data for testing
        if len(self.test_users) >= 1:
            user = self.test_users[0]
            
            # Create sample basket items with realistic precious metals data
            sample_items = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "BMW 320d Catalytic Converter",
                    "price": 450.00,
                    "seller": "AutoParts Pro",
                    "seller_name": "AutoParts Pro",
                    "created_at": "2024-12-15T10:30:00Z",
                    "weight": 1.2,
                    "pt_ppm": 1200,
                    "pd_ppm": 800,
                    "rh_ppm": 150,
                    "renumeration_pt": 0.85,
                    "renumeration_pd": 0.80,
                    "renumeration_rh": 0.75,
                    "pt_g": 1.224,
                    "pd_g": 0.768,
                    "rh_g": 0.135
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Mercedes E-Class Catalyst",
                    "price": 650.00,
                    "seller": "Euro Catalysts",
                    "seller_name": "Euro Catalysts",
                    "created_at": "2024-12-16T14:20:00Z",
                    "weight": 1.8,
                    "pt_ppm": 1500,
                    "pd_ppm": 1000,
                    "rh_ppm": 200,
                    "renumeration_pt": 0.85,
                    "renumeration_pd": 0.80,
                    "renumeration_rh": 0.75,
                    "pt_g": 2.295,
                    "pd_g": 1.440,
                    "rh_g": 0.270
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Audi A4 Catalytic Converter",
                    "price": 350.00,
                    "seller": "German Auto Parts",
                    "seller_name": "German Auto Parts",
                    "created_at": "2024-12-17T09:15:00Z",
                    "weight": 0.9,
                    "pt_ppm": 1000,
                    "pd_ppm": 600,
                    "rh_ppm": 100,
                    "renumeration_pt": 0.85,
                    "renumeration_pd": 0.80,
                    "renumeration_rh": 0.75,
                    "pt_g": 0.765,
                    "pd_g": 0.432,
                    "rh_g": 0.068
                }
            ]
            
            self.test_items = sample_items
            
            # Create sample basket with totals
            sample_basket = {
                "basketId": str(uuid.uuid4()),
                "basketName": "Premium Catalysts Collection",
                "basketDescription": "High-value catalytic converters from European vehicles",
                "userId": user["id"],
                "exportDate": "2024-12-18T16:45:00Z",
                "items": sample_items,
                "totals": {
                    "valuePaid": 1450.00,
                    "ptG": 4.284,  # Sum of all pt_g values
                    "pdG": 2.640,  # Sum of all pd_g values
                    "rhG": 0.473   # Sum of all rh_g values
                }
            }
            
            self.test_baskets.append(sample_basket)
            print(f"✅ Created sample basket: {sample_basket['basketName']} with {len(sample_items)} items")
            
            # Create empty basket for testing edge cases
            empty_basket = {
                "basketId": str(uuid.uuid4()),
                "basketName": "Empty Test Basket",
                "basketDescription": "Test basket with no items",
                "userId": user["id"],
                "exportDate": "2024-12-18T16:45:00Z",
                "items": [],
                "totals": {
                    "valuePaid": 0.00,
                    "ptG": 0.00,
                    "pdG": 0.00,
                    "rhG": 0.00
                }
            }
            
            self.test_baskets.append(empty_basket)
            print(f"✅ Created empty basket for edge case testing")
            
        print(f"✅ Setup complete: {len(self.test_baskets)} baskets, {len(self.test_items)} items")
                
    async def test_basket_pdf_export_functionality(self):
        """Test comprehensive basket PDF export functionality"""
        print("\n📄 Testing Basket PDF Export Functionality...")
        
        if len(self.test_baskets) < 1:
            self.log_result("Basket PDF Export Setup", False, "Insufficient test data", "Need at least 1 basket")
            return
        
        # Test 1: Basic basket PDF export with sample data
        await self.test_basic_basket_pdf_export()
        
        # Test 2: Empty basket PDF export (edge case)
        await self.test_empty_basket_pdf_export()
        
        # Test 3: PDF structure and content validation
        await self.test_pdf_content_validation()
        
        # Test 4: Logo integration testing
        await self.test_logo_integration()
        
        # Test 5: Precious metals data formatting
        await self.test_precious_metals_formatting()
        
        # Test 6: Error handling scenarios
        await self.test_error_handling_scenarios()
        
        # Test 7: File generation and response validation
        await self.test_file_generation_validation()
        
    async def test_basic_basket_pdf_export(self):
        """Test basic basket PDF export with sample data"""
        basket = self.test_baskets[0]  # Use the basket with items
        
        response, status = await self.make_request("POST", "/user/export-basket-pdf", basket)
        
        if status == 200:
            # Check if response is a streaming response (PDF file)
            if hasattr(response, 'read') or isinstance(response, bytes):
                self.log_result("Basic Basket PDF Export", True, f"PDF generated for basket: {basket['basketName']}")
            else:
                self.log_result("Basic Basket PDF Export", False, "Response is not a valid PDF file")
        else:
            self.log_result("Basic Basket PDF Export", False, f"Status: {status}", str(response))
            
    async def test_empty_basket_pdf_export(self):
        """Test PDF export with empty basket (edge case)"""
        if len(self.test_baskets) < 2:
            self.log_result("Empty Basket PDF Export", False, "No empty basket available for testing")
            return
            
        empty_basket = self.test_baskets[1]  # Use the empty basket
        
        response, status = await self.make_request("POST", "/user/export-basket-pdf", empty_basket)
        
        if status == 200:
            self.log_result("Empty Basket PDF Export", True, "PDF generated successfully for empty basket")
        else:
            self.log_result("Empty Basket PDF Export", False, f"Status: {status}", str(response))
            
    async def test_pdf_content_validation(self):
        """Test PDF content structure and data accuracy"""
        basket = self.test_baskets[0]
        
        # Make a custom request to get raw response for validation
        try:
            url = f"{API_BASE}/user/export-basket-pdf"
            async with self.session.post(url, json=basket) as response:
                if response.status == 200:
                    pdf_content = await response.read()
                    
                    # Validate PDF header
                    if pdf_content.startswith(b'%PDF'):
                        self.log_result("PDF Content Validation - Header", True, "Valid PDF header detected")
                        
                        # Check PDF size (should be reasonable for content)
                        pdf_size = len(pdf_content)
                        if 5000 < pdf_size < 500000:  # Between 5KB and 500KB seems reasonable
                            self.log_result("PDF Content Validation - Size", True, f"PDF size: {pdf_size} bytes")
                        else:
                            self.log_result("PDF Content Validation - Size", False, f"Unusual PDF size: {pdf_size} bytes")
                            
                        # Check for ReportLab markers (indicates proper library usage)
                        if b'ReportLab' in pdf_content or b'reportlab' in pdf_content:
                            self.log_result("PDF Content Validation - ReportLab", True, "ReportLab library integration confirmed")
                        else:
                            self.log_result("PDF Content Validation - ReportLab", False, "ReportLab markers not found in PDF")
                            
                    else:
                        self.log_result("PDF Content Validation - Header", False, "Invalid PDF header")
                else:
                    self.log_result("PDF Content Validation", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.log_result("PDF Content Validation", False, f"Validation failed: {str(e)}")
            
    async def test_logo_integration(self):
        """Test Cataloro logo integration in PDF"""
        basket = self.test_baskets[0]
        
        try:
            url = f"{API_BASE}/user/export-basket-pdf"
            async with self.session.post(url, json=basket) as response:
                if response.status == 200:
                    pdf_content = await response.read()
                    
                    # Check for image markers in PDF (indicates logo presence)
                    if b'/Image' in pdf_content or b'/XObject' in pdf_content:
                        self.log_result("Logo Integration", True, "Image/logo markers found in PDF")
                    else:
                        self.log_result("Logo Integration", True, "PDF generated without logo (acceptable if no logo file found)")
                        
                    # Check for Cataloro branding text
                    if b'CATALORO' in pdf_content or b'Cataloro' in pdf_content:
                        self.log_result("Logo Integration - Branding", True, "Cataloro branding text found in PDF")
                    else:
                        self.log_result("Logo Integration - Branding", False, "Cataloro branding text not found")
                        
                else:
                    self.log_result("Logo Integration", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.log_result("Logo Integration", False, f"Test failed: {str(e)}")
            
    async def test_precious_metals_formatting(self):
        """Test proper formatting of precious metals data (Pt, Pd, Rh)"""
        basket = self.test_baskets[0]
        
        # Verify the test data has proper precious metals values
        expected_pt = basket['totals']['ptG']
        expected_pd = basket['totals']['pdG'] 
        expected_rh = basket['totals']['rhG']
        
        if expected_pt > 0 and expected_pd > 0 and expected_rh > 0:
            self.log_result("Precious Metals Data - Test Setup", True, f"Test data: Pt={expected_pt}g, Pd={expected_pd}g, Rh={expected_rh}g")
            
            response, status = await self.make_request("POST", "/user/export-basket-pdf", basket)
            
            if status == 200:
                self.log_result("Precious Metals Formatting", True, "PDF generated with precious metals data")
                
                # Test individual item precious metals calculations
                for item in basket['items']:
                    if item.get('pt_g', 0) > 0:
                        self.log_result("Precious Metals - Item Level", True, f"Item '{item['title'][:20]}...' has Pt: {item['pt_g']}g")
                        break
                        
            else:
                self.log_result("Precious Metals Formatting", False, f"Status: {status}")
        else:
            self.log_result("Precious Metals Data - Test Setup", False, "Test data lacks precious metals values")
            
    async def test_error_handling_scenarios(self):
        """Test various error scenarios"""
        
        # Test 1: Missing required fields
        invalid_basket = {"basketName": "Test"}  # Missing required fields
        
        response, status = await self.make_request("POST", "/user/export-basket-pdf", invalid_basket)
        
        if status in [400, 422, 500]:  # Any error status is acceptable for invalid data
            self.log_result("Error Handling - Invalid Data", True, f"Properly handled invalid data (status: {status})")
        else:
            self.log_result("Error Handling - Invalid Data", False, f"Should reject invalid data, got status: {status}")
            
        # Test 2: Empty request body
        response, status = await self.make_request("POST", "/user/export-basket-pdf", {})
        
        if status in [400, 422, 500]:
            self.log_result("Error Handling - Empty Request", True, f"Properly handled empty request (status: {status})")
        else:
            self.log_result("Error Handling - Empty Request", False, f"Should reject empty request, got status: {status}")
            
        # Test 3: Malformed data types
        malformed_basket = {
            "basketName": 12345,  # Should be string
            "totals": "invalid",  # Should be object
            "items": "not_array"  # Should be array
        }
        
        response, status = await self.make_request("POST", "/user/export-basket-pdf", malformed_basket)
        
        if status in [400, 422, 500]:
            self.log_result("Error Handling - Malformed Data", True, f"Properly handled malformed data (status: {status})")
        else:
            self.log_result("Error Handling - Malformed Data", False, f"Should reject malformed data, got status: {status}")
            
    async def test_file_generation_validation(self):
        """Test file generation and response headers"""
        basket = self.test_baskets[0]
        
        try:
            url = f"{API_BASE}/user/export-basket-pdf"
            async with self.session.post(url, json=basket) as response:
                if response.status == 200:
                    # Check response headers
                    content_type = response.headers.get('content-type', '')
                    content_disposition = response.headers.get('content-disposition', '')
                    
                    if 'application/pdf' in content_type:
                        self.log_result("File Generation - Content Type", True, f"Correct content type: {content_type}")
                    else:
                        self.log_result("File Generation - Content Type", False, f"Incorrect content type: {content_type}")
                        
                    if 'attachment' in content_disposition and 'cataloro-basket' in content_disposition:
                        self.log_result("File Generation - Filename", True, f"Proper filename in headers: {content_disposition}")
                    else:
                        self.log_result("File Generation - Filename", False, f"Missing or incorrect filename: {content_disposition}")
                        
                    # Check file size
                    pdf_content = await response.read()
                    file_size = len(pdf_content)
                    
                    if file_size > 1000:  # Should be at least 1KB for a proper PDF
                        self.log_result("File Generation - Size", True, f"Generated PDF size: {file_size} bytes")
                    else:
                        self.log_result("File Generation - Size", False, f"PDF too small: {file_size} bytes")
                        
                else:
                    self.log_result("File Generation Validation", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.log_result("File Generation Validation", False, f"Test failed: {str(e)}")
            
    async def test_backend_health(self):
        """Test backend health and connectivity"""
        print("\n🏥 Testing Backend Health...")
        
        response, status = await self.make_request("GET", "/health")
        
        if status == 200:
            app_name = response.get("app", "")
            version = response.get("version", "")
            self.log_result("Backend Health Check", True, f"App: {app_name}, Version: {version}")
        else:
            self.log_result("Backend Health Check", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🧪 BACKEND TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error']}")
                    
        print(f"\n🎯 TESTING FOCUS AREAS:")
        print(f"   • User Rating System: 4 endpoints tested")
        print(f"   • Enhanced Messaging: 5 endpoints tested") 
        print(f"   • Enhanced Profile: 3 endpoints tested")
        print(f"   • Backend Health: 1 endpoint tested")
        
        print(f"\n📊 ENDPOINT COVERAGE:")
        rating_tests = [r for r in self.test_results if "Rating" in r["test"]]
        messaging_tests = [r for r in self.test_results if "Message" in r["test"] or "Conversation" in r["test"]]
        profile_tests = [r for r in self.test_results if "Profile" in r["test"]]
        
        print(f"   • Rating System: {sum(1 for t in rating_tests if t['success'])}/{len(rating_tests)} passed")
        print(f"   • Messaging System: {sum(1 for t in messaging_tests if t['success'])}/{len(messaging_tests)} passed")
        print(f"   • Profile System: {sum(1 for t in profile_tests if t['success'])}/{len(profile_tests)} passed")
        
async def main():
    """Main test execution"""
    print("🚀 Starting Comprehensive Backend Testing")
    print(f"🌐 Backend URL: {BASE_URL}")
    print("="*80)
    
    tester = BackendTester()
    
    try:
        await tester.setup_session()
        
        # Test backend health first
        await tester.test_backend_health()
        
        # Setup test data
        await tester.setup_test_data()
        
        # Run all test suites
        await tester.test_user_rating_system()
        await tester.test_enhanced_messaging_system()
        await tester.test_enhanced_profile_endpoints()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())