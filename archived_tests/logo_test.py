#!/usr/bin/env python3
"""
Logo Implementation Testing
Testing logo upload, retrieval, and frontend integration
"""

import asyncio
import aiohttp
import time
import json
import base64
from datetime import datetime
from typing import Dict, List, Any
from io import BytesIO
from PIL import Image

# Test Configuration
BACKEND_URL = "https://marketplace-fix-9.preview.emergentagent.com/api"

class LogoTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None, files: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data and not files:
                request_kwargs['json'] = data
            if data and files:
                request_kwargs['data'] = data
            if headers:
                request_kwargs['headers'] = headers
            if files:
                request_kwargs['data'] = files
            
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **request_kwargs) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "response_time_ms": response_time_ms,
                    "data": response_data,
                    "status": response.status
                }
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time_ms,
                "error": str(e),
                "status": 0
            }
    
    def create_test_logo(self) -> bytes:
        """Create a small test logo image"""
        # Create a simple 100x50 test logo with text
        img = Image.new('RGB', (100, 50), color='blue')
        
        # Convert to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    async def test_logo_upload(self) -> Dict:
        """Test POST /api/admin/logo endpoint"""
        print("📤 Testing logo upload...")
        
        try:
            # Create test logo
            logo_data = self.create_test_logo()
            
            # Prepare multipart form data
            form_data = aiohttp.FormData()
            form_data.add_field('file', logo_data, filename='test_logo.png', content_type='image/png')
            form_data.add_field('mode', 'light')
            
            # Make upload request
            start_time = time.time()
            async with self.session.post(f"{BACKEND_URL}/admin/logo", data=form_data) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                success = response.status in [200, 201]
                
                if success:
                    print(f"  ✅ Logo upload successful")
                    print(f"  📁 Filename: {response_data.get('filename', 'N/A')}")
                    print(f"  📏 Size: {response_data.get('size', 'N/A')} bytes")
                    print(f"  🔗 URL: {response_data.get('url', 'N/A')[:50]}...")
                    print(f"  ⏱️ Response time: {response_time_ms:.0f}ms")
                    
                    return {
                        "test_name": "Logo Upload",
                        "success": True,
                        "response_time_ms": response_time_ms,
                        "filename": response_data.get('filename'),
                        "size": response_data.get('size'),
                        "url": response_data.get('url'),
                        "mode": response_data.get('mode'),
                        "message": response_data.get('message')
                    }
                else:
                    print(f"  ❌ Logo upload failed: {response_data}")
                    return {
                        "test_name": "Logo Upload",
                        "success": False,
                        "response_time_ms": response_time_ms,
                        "error": response_data,
                        "status": response.status
                    }
                    
        except Exception as e:
            print(f"  ❌ Logo upload error: {str(e)}")
            return {
                "test_name": "Logo Upload",
                "success": False,
                "error": str(e)
            }
    
    async def test_logo_retrieval(self) -> Dict:
        """Test GET /api/admin/logo endpoint"""
        print("📥 Testing logo retrieval...")
        
        result = await self.make_request("/admin/logo", "GET")
        
        if result["success"]:
            logo_data = result["data"]
            logo_url = logo_data.get("logo_url")
            mode = logo_data.get("mode")
            
            print(f"  ✅ Logo retrieval successful")
            print(f"  🔗 Logo URL: {logo_url[:50] if logo_url else 'None'}...")
            print(f"  🎨 Mode: {mode}")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            
            return {
                "test_name": "Logo Retrieval",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "logo_url": logo_url,
                "mode": mode,
                "has_logo": logo_url is not None
            }
        else:
            print(f"  ❌ Logo retrieval failed: {result.get('error', 'Unknown error')}")
            return {
                "test_name": "Logo Retrieval",
                "success": False,
                "response_time_ms": result["response_time_ms"],
                "error": result.get("error", "Retrieval failed"),
                "status": result["status"]
            }
    
    async def test_logo_url_accessibility(self, logo_url: str) -> Dict:
        """Test if the logo URL is accessible"""
        print("🌐 Testing logo URL accessibility...")
        
        if not logo_url:
            print("  ⚠️ No logo URL to test")
            return {
                "test_name": "Logo URL Accessibility",
                "success": False,
                "error": "No logo URL provided"
            }
        
        try:
            # For data URLs, just validate format
            if logo_url.startswith('data:'):
                print(f"  ✅ Data URL format valid")
                print(f"  📊 Data URL length: {len(logo_url)} characters")
                
                # Try to decode base64 data
                try:
                    header, data = logo_url.split(',', 1)
                    decoded_data = base64.b64decode(data)
                    print(f"  ✅ Base64 data decoded successfully ({len(decoded_data)} bytes)")
                    
                    return {
                        "test_name": "Logo URL Accessibility",
                        "success": True,
                        "url_type": "data_url",
                        "data_size": len(decoded_data),
                        "url_length": len(logo_url)
                    }
                except Exception as decode_error:
                    print(f"  ❌ Base64 decode failed: {decode_error}")
                    return {
                        "test_name": "Logo URL Accessibility",
                        "success": False,
                        "error": f"Base64 decode failed: {decode_error}"
                    }
            
            # For regular URLs, try to fetch
            else:
                start_time = time.time()
                async with self.session.get(logo_url) as response:
                    end_time = time.time()
                    response_time_ms = (end_time - start_time) * 1000
                    
                    success = response.status == 200
                    content_length = response.headers.get('content-length', 'unknown')
                    content_type = response.headers.get('content-type', 'unknown')
                    
                    if success:
                        print(f"  ✅ Logo URL accessible")
                        print(f"  📏 Content length: {content_length}")
                        print(f"  📄 Content type: {content_type}")
                        print(f"  ⏱️ Response time: {response_time_ms:.0f}ms")
                    else:
                        print(f"  ❌ Logo URL not accessible (status: {response.status})")
                    
                    return {
                        "test_name": "Logo URL Accessibility",
                        "success": success,
                        "response_time_ms": response_time_ms,
                        "url_type": "http_url",
                        "content_length": content_length,
                        "content_type": content_type,
                        "status": response.status
                    }
                    
        except Exception as e:
            print(f"  ❌ Logo URL accessibility error: {str(e)}")
            return {
                "test_name": "Logo URL Accessibility",
                "success": False,
                "error": str(e)
            }
    
    async def test_frontend_logo_integration(self) -> Dict:
        """Test frontend logo integration (corrected URL path)"""
        print("🖥️ Testing frontend logo integration...")
        
        # Test the corrected frontend URL (without double /api)
        frontend_url = "https://marketplace-fix-9.preview.emergentagent.com/api/admin/logo"
        
        try:
            start_time = time.time()
            async with self.session.get(frontend_url) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                success = response.status == 200
                
                if success:
                    print(f"  ✅ Frontend logo endpoint accessible")
                    print(f"  🔗 URL: {frontend_url}")
                    print(f"  ⏱️ Response time: {response_time_ms:.0f}ms")
                    
                    # Check if response contains logo_url
                    if isinstance(response_data, dict) and 'logo_url' in response_data:
                        print(f"  ✅ Response contains logo_url field")
                        logo_url = response_data.get('logo_url')
                        print(f"  🔗 Logo URL: {logo_url[:50] if logo_url else 'None'}...")
                    else:
                        print(f"  ⚠️ Response format: {type(response_data)}")
                    
                    return {
                        "test_name": "Frontend Logo Integration",
                        "success": True,
                        "response_time_ms": response_time_ms,
                        "frontend_url": frontend_url,
                        "response_data": response_data,
                        "has_logo_url": isinstance(response_data, dict) and 'logo_url' in response_data
                    }
                else:
                    print(f"  ❌ Frontend logo endpoint failed (status: {response.status})")
                    print(f"  📄 Response: {response_data}")
                    
                    return {
                        "test_name": "Frontend Logo Integration",
                        "success": False,
                        "response_time_ms": response_time_ms,
                        "frontend_url": frontend_url,
                        "error": response_data,
                        "status": response.status
                    }
                    
        except Exception as e:
            print(f"  ❌ Frontend logo integration error: {str(e)}")
            return {
                "test_name": "Frontend Logo Integration",
                "success": False,
                "error": str(e)
            }
    
    async def run_comprehensive_logo_tests(self) -> Dict:
        """Run all logo tests in sequence"""
        print("🚀 Starting comprehensive logo implementation testing...")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Test 1: Upload logo
            upload_result = await self.test_logo_upload()
            self.test_results.append(upload_result)
            
            print()
            
            # Test 2: Retrieve logo
            retrieval_result = await self.test_logo_retrieval()
            self.test_results.append(retrieval_result)
            
            print()
            
            # Test 3: Test logo URL accessibility (if we have a URL)
            logo_url = None
            if retrieval_result.get("success") and retrieval_result.get("logo_url"):
                logo_url = retrieval_result["logo_url"]
                accessibility_result = await self.test_logo_url_accessibility(logo_url)
                self.test_results.append(accessibility_result)
                
                print()
            
            # Test 4: Test frontend integration
            frontend_result = await self.test_frontend_logo_integration()
            self.test_results.append(frontend_result)
            
            print()
            print("=" * 60)
            print("📊 LOGO IMPLEMENTATION TEST SUMMARY")
            print("=" * 60)
            
            total_tests = len(self.test_results)
            successful_tests = sum(1 for result in self.test_results if result.get("success"))
            
            print(f"Total tests: {total_tests}")
            print(f"Successful: {successful_tests}")
            print(f"Failed: {total_tests - successful_tests}")
            print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
            
            print("\nDetailed Results:")
            for result in self.test_results:
                status = "✅" if result.get("success") else "❌"
                test_name = result.get("test_name", "Unknown Test")
                print(f"{status} {test_name}")
                
                if not result.get("success") and result.get("error"):
                    print(f"   Error: {result['error']}")
            
            # Overall assessment
            print("\n" + "=" * 60)
            if successful_tests == total_tests:
                print("🎉 ALL LOGO TESTS PASSED - Logo implementation working perfectly!")
            elif successful_tests >= total_tests * 0.75:
                print("✅ LOGO TESTS MOSTLY SUCCESSFUL - Minor issues detected")
            else:
                print("❌ LOGO TESTS FAILED - Critical issues need attention")
            
            return {
                "overall_success": successful_tests == total_tests,
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": (successful_tests/total_tests)*100,
                "test_results": self.test_results
            }
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = LogoTester()
    results = await tester.run_comprehensive_logo_tests()
    
    # Return exit code based on results
    return 0 if results["overall_success"] else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)